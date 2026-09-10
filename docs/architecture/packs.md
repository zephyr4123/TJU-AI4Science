# 插件形态：任务包与领域包

- 状态：**aligned**（形态）；字段细节在代码落地时以 schema 文件为准
- 最近变更：2026-09-10
- 依据：[AutoResearchClaw 深读 §7](../../research/selection/2026-0909-pipeline-frameworks/autoresearchclaw.md#7-领域适配与-arc-bench)（manifest 与 profile 的形态，以及它在注册上栽的坑）、[InternAgent 深读 §5](../../research/selection/2026-0909-pipeline-frameworks/internagent.md#5-任务契约与可运行性)（目录形态）

流程通用，任务不通用。适配的形态是**写文件，不是改代码**：一个任务一个目录，一个领域一个目录，框架启动时扫目录发现，没有注册表（P-5）。

## 1. 全景

```
 platform/
 ├── coordinator/             协调层 skill 包，跟项目走；不进执行层的搜索路径（Q-10）
 ├── framework/               通用，一行不随任务改
 ├── backends/                执行层适配器
 ├── tools/                   确定性脚本
 │
 ├── domains/                 领域包：一个领域一个目录
 │   ├── generic/             兜底，任何任务都能用
 │   ├── ml/
 │   └── mechanics/
 │       ├── profile.yaml     必有
 │       ├── prompts/         可选：各能力的领域补充提示
 │       ├── tools/           可选：求解器封装、网格生成、单位换算
 │       └── skills/          可选：执行层用的 SKILL.md，与 Claude Code 原生同格式
 │
 └── tasks/                   任务包：一个任务一个目录
     └── beam-deflection/
         ├── manifest.yaml    必有
         ├── harness/         必有：怎么算分、跑多久；只读，框架校验 hash
         ├── code/            必有：基线，执行层唯一能改的地方
         ├── data/            可选：参考解、验证算例；执行层不能碰
         └── run_0/           必有：基线跑一次的产物
```

## 2. 任务包

### manifest.yaml

声明层。**由协调层（人 + agent）拍板后填写，框架只读**：方向、预算、统计门、验收判据都是决策，不是框架自己长出来的（纲领 §2）。形态从 AutoResearchClaw 的 ARC-Bench manifest 取（55 道题五个领域同一模板），去掉它没人读的字段。

```yaml
id: beam-deflection
domain: mechanics                 # 对应 domains/<id>/，缺省 generic
title: 悬臂梁挠度计算的网格无关性
question: >                       # 研究问题，给文献、假设、设计三个能力
  在固定计算预算下，哪种网格加密策略能以最小误差逼近解析解
conditions:                       # 实验条件，设计与实验能力用
  - name: uniform
  - name: adaptive
metrics:
  - name: rel_l2_error
    direction: minimize           # runner 比较时读这个，不读别处
    primary: true
  - name: runtime_s
    direction: minimize
budget:
  wall_clock_s: 300               # 固定预算，harness 到时自停
  max_iterations: 30
  repeat_k: 3                     # 统计门：同配置重复次数
  accept_sigma: 2.0
requirements:                     # 验收条件，验证能力与隔离裁判用
  - id: R1
    type: numeric                 # numeric | artifact | discussion
    must_pass: true
    description: 主指标优于 run_0 基线且通过统计门
  - id: R2
    type: artifact
    must_pass: true
    description: 产出收敛曲线图，数据来自 results.json
```

字段每一个都必须在框架里有读取点，否则不许进 schema（P-8 的配置规矩反过来用）。

### harness/

评测层。框架注入、模型改不了、独立进程、只吃产物文件（P-6）。

```
harness/
├── evaluate.py       输入 code/ 跑出来的产物文件，输出 results.json
├── launcher.sh       唯一执行入口；runner 在 run_N/ 里无参执行它
└── SHA256SUMS        框架每轮校验；变了判 crash 并回滚
```

`results.json` 的形状固定：

```json
{"metrics": {"rel_l2_error": 0.0312, "runtime_s": 287.4}, "elapsed_s": 298.1, "seed": 42, "status": "ok"}
```

harness 的接口约束（从 AutoResearchClaw 的 `harness_template.py` 取思路）：到预算 80% 让实验自己优雅停；NaN / Inf 计满即退出非零；指标只能经 harness 写出。

### code/ 与 data/

- `code/` 是执行层唯一能改的地方，基线要整理到"单入口、明确参数、能快速小规模跑"的状态，否则执行层每轮改完跑不动，全耗在修 bug 上。
- `data/` 放参考解与验证算例，有明确 ID，准备阶段就与调参用的算例分开，分离逻辑写在 harness 里而不是 code/ 里。
- `run_0/` 是基线跑一次的产物，改进率的分母，也是账本第一行。

### 接一个新任务的清单

1. 写 `manifest.yaml`，跑 `ai4sci task validate <dir>` 过 schema。
2. 把基线整理进 `code/`，写 `launcher.sh`。
3. 写 `harness/evaluate.py`，产出 `results.json`；跑一次得到 `run_0/`。
4. 同配置重复 k 次，把 σ 记进 `run_0/`，这是统计门的基线。

纯契约工作量半天到一天；真正的成本在把仿真整理成能在预算内跑完。

## 3. 领域包

### profile.yaml

```yaml
id: mechanics
display_name: 固体力学
condition_terminology:            # 设计能力的措辞
  baseline: 参考格式
  proposed: 候选格式
default_budget_s: 600
core_libraries: [numpy, scipy, fenics]
metric_hints:                     # 对网格分辨率、单位制不变的误差度量
  - rel_l2_error
  - conservation_violation
paper_keywords: [mesh refinement, finite element, error estimate]
```

### prompts/、tools/、skills/

- `prompts/<capability>.md`：该能力的领域补充提示，框架在组装能力指令时追加；缺了就不追加，不回退到别的领域（AutoResearchClaw 让 26 个领域静默用 ML 提示词，这是反例）。
- `tools/`：确定性脚本，执行层可以调用；求解器怎么起、结果怎么读、单位怎么换。
- `skills/<name>/SKILL.md`：**执行层**用的 skill，与 Claude Code 原生同格式，怎么注入见 Q-2。协调层的 skill 不在这里，在内仓 `coordinator/`（放哪、怎么注入见 Q-10）；两条搜索路径不相交（P-11）。

### 加一个新领域

新建 `domains/<id>/profile.yaml`，其余可选。不改 `framework/`。

## 4. 发现与校验

- 框架启动时扫 `domains/*/profile.yaml` 与 `tasks/*/manifest.yaml`，按目录名当 id；同名冲突直接报错。
- 用户自己的包可以放在包外目录，通过环境变量追加搜索路径；**所有搜索路径的包待遇相同**，不存在"包内的才有提示词"。
- CI 门禁：删掉全部 `domains/` 与 `tasks/`，`framework/` 的测试照样过（P-5）。
- `ai4sci task validate` 与 `ai4sci domain validate` 两条命令做 schema 校验，任务包与领域包各自有 schema 文件放在 `framework/schemas/`。

## 变更记录

| 日期 | 改了什么 | 为什么 | 认可 |
|---|---|---|---|
| 2026-09-10 | 建档。任务包与领域包的目录、manifest 与 profile 字段、harness 约束、发现规则 | 泛化边界的结论：流程通用、任务不通用，适配必须是写文件 | 主人 + Claude |
| 2026-09-10 | manifest 明确由协调层拍板后填写；全景加 `coordinator/`；领域包 `skills/` 限定为执行层用，与协调层 skill 隔离；"阶段"改"能力"、"底座"改"执行层"（[#18](https://github.com/zephyr4123/TJU-AI4Science/issues/18)） | 加了协调层，契约的填写权归它；两层 agent 的 skill 必须物理隔离（P-11） | 主人 + Claude |
