# 插件形态：任务包与领域包

- 状态：**aligned**（形态）；字段细节在代码落地时以 schema 文件为准
- 最近变更：2026-09-16
- 依据：[AutoResearchClaw 深读 §7](../../research/selection/2026-0909-pipeline-frameworks/autoresearchclaw.md#7-领域适配与-arc-bench)（manifest 与 profile 的形态，以及它在注册上栽的坑）、[InternAgent 深读 §5](../../research/selection/2026-0909-pipeline-frameworks/internagent.md#5-任务契约与可运行性)（目录形态）

流程通用，任务不通用。适配的形态是**写文件，不是改代码**：一个任务一个目录，一个领域一个目录，框架启动时扫目录发现，没有注册表（P-5）。

## 1. 全景

```
 platform/
 ├── coordinator/             协调层 skill 包，跟项目走；不进执行层的搜索路径（Q-10）
 ├── framework/               通用，一行不随任务改
 ├── backends/                执行层适配器
 ├── compute/                 算力适配器：local / ssh / slurm
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
         ├── manifest.yaml    必有；format_version 必填
         ├── env/             必有：python-version + requirements.lock，任务自带环境，框架建成任务级 venv
         ├── harness/         必有：怎么算分、跑多久；只读，框架校验 hash
         ├── code/            必有：基线，执行层唯一能改的地方
         ├── data/            可选：参考解、验证算例；执行层不能碰（真值只给 harness，code/ 只见输入）
         ├── run_0/           必有：results.json 基线 + repeats/results-<seed>.json × repeat_k + sigma.json
         └── .venv/           不进 git：`ai4sci task env build` 按 env/ 建出来，给 make_run0.sh 用
```

## 2. 任务包

### manifest.yaml

声明层。**由协调层（人 + agent）拍板后填写，框架只读**：方向、预算、统计门、验收判据都是决策，不是框架自己长出来的（纲领 §2）。形态从 AutoResearchClaw 的 ARC-Bench manifest 取（55 道题五个领域同一模板），去掉它没人读的字段。

```yaml
format_version: 1                 # 契约版本；框架只认它支持的版本，改契约走迁移不直接 break
id: beam-deflection
domain: mechanics                 # 对应 domains/<id>/，缺省 generic
source: docs/cases/beam-bending   # 可选：这个任务从哪来（案例卡路径或 URL），ai4sci status 打印
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
  # 可选：patience 连续不改进几轮停（缺省 5）；min_delta 最小改进量，σ=0 的确定性 harness 必填；max_cost_usd 总花费上限
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

字段每一个都必须在框架里有读取点，否则不许进 schema（P-8 的配置规矩反过来用）。`format_version` 的读取点是校验（不认的版本判不合法）；`source` 的读取点是 `ai4sci status`。

### env/

任务自带环境，平台 venv 一个包不多装（红线：环境必隔离）。两个文件：

```
env/
├── python-version      一行，如 3.14；框架用 uv 找或拉这个版本的解释器
└── requirements.lock   逐行 name==version，钉死；可以为空（零依赖任务）
```

框架把它建成 venv 的地方有两处，同一份 lock、同一个函数：`tasks/<id>/.venv/`（`ai4sci task env build <dir>`，给 `make_run0.sh` 与人手工跑用）和 `runs/<id>/.venv/`（`ai4sci run new` 建 run 时顺手建，run 跑起来后不回头看任务包，环境也一样）。venv 由 `uv` 建与同步（`uv venv` + `uv pip sync`），uv 是框架的运行时依赖；uv 不在或解释器拉不下来就明确报错，不静默退回到平台 venv。

`env/` 与 `harness/` 一样是只读的：依赖是问题定义的一部分，执行层改了它判 `readonly`。docker 按 Q-6 仍不上，依赖真要系统库时再谈。

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

`launcher.sh` 只准经 `"$AI4SCI_PYTHON"` 起 Python：框架提交 harness 时把任务 venv 的解释器路径放进这个环境变量，`make_run0.sh` 缺省指到 `tasks/<id>/.venv/bin/python`。`harness/*.sh` 里出现裸 `python` / `python3` 命令，`ai4sci task validate` 判不合法——这是「任务跑在自己的环境里」的机器判据。

harness 的接口约束（从 AutoResearchClaw 的 `harness_template.py` 取思路）：到预算 80% 让实验自己优雅停；NaN / Inf 计满即退出非零；指标只能经 harness 写出。`evaluate.py` 拒收产物（预测缺失、长度不对、NaN）时用 `SystemExit` 带一句话退出非零、**不抛 traceback**，runner 据此把假成功判成 `no_results` 而不是 `crash`；`status` 字段不是 ok 也判 `no_results`。任务包别带会挡住 `code/` 产物的 `.gitignore`：被挡住的改动提交不进去，那一轮记 `noop`。

### code/ 与 data/

- `code/` 是执行层唯一能改的地方，基线要整理到"单入口、明确参数、能快速小规模跑"的状态，否则执行层每轮改完跑不动，全耗在修 bug 上。
- `data/` 放参考解与验证算例，有明确 ID，准备阶段就与调参用的算例分开，分离逻辑写在 harness 里而不是 code/ 里。
- `run_0/` 是基线跑一次的产物，改进率的分母，也是账本第一行。布局：`results.json`（基线种子）、`repeats/results-<seed>.json` 恰好 `repeat_k` 个、`sigma.json` 每个指标一条 `{sigma, seeds, values}`；`ai4sci task validate` 逐项对账。
- 验证集拆两份：`data/val_inputs.json` 只有输入给 `code/` 读，`data/val.json` 带真值只给 harness。code/ 自己算分等于自己给自己打分（P-2），当假成功处理。

### 接一个新任务的清单

谁做什么（纲领 §2 的分工，这就是设计能力手工走一遍的样子）：协调层（人 + agent）填 `manifest.yaml`；执行层在隔离会话里写 `harness/`、`code/` 基线与 `env/`，只放行这三个目录；人签 `evaluate.py` 的判分标准；框架校验、建环境、跑基线。

1. 写 `manifest.yaml`（`format_version: 1`，`source` 指回案例卡），跑 `ai4sci task validate <dir>` 过 schema。
2. 写 `env/python-version` 与 `env/requirements.lock`，`ai4sci task env build <dir>` 建出 `.venv/`。
3. 把基线整理进 `code/`，写 `launcher.sh`（Python 只经 `"$AI4SCI_PYTHON"` 起）。
4. 写 `harness/evaluate.py`，产出 `results.json`；跑一次得到 `run_0/`。
5. 同配置重复 k 次，把 σ 记进 `run_0/sigma.json`，这是统计门的基线。把这几步写成 `harness/make_run0.sh` 并登记进 SHA256SUMS，改了 code/ 或数据就重跑它。

参考实现：`tasks/mlp-regression/`（[#21](https://github.com/zephyr4123/TJU-AI4Science/issues/21)，零依赖）与 `tasks/boehm-nll/`（[#40](https://github.com/zephyr4123/TJU-AI4Science/issues/40)，第一个真任务，带依赖）；面向接任务的人的指南在内仓 `docs/add-a-task.md`。schema 只收有读取点的字段（P-8 反过来用）：`conditions` 在设计能力落地前不进 schema，写了会被判不合法。

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
- `skills/<name>/SKILL.md`：**执行层**用的 skill，与 Claude Code 原生同格式（frontmatter + 正文）。注入走 prompt 不走 CLI 原生机制：执行层的隔离参数（`--setting-sources ""`、`--disable-slash-commands`，见 workflow §5）把本机 CLAUDE.md、plugin、skill 一并关掉了，这正是 P-11 要的，所以领域 skill 只能由框架塞进 prompt——`ai4sci run new` 时把领域包的 `prompts/experiment.md` 与全部 `skills/*/SKILL.md` 快照进 `runs/<id>/prompts/`，执行层每次会话的提示末尾追加成「领域约定」一段（正文，不含 frontmatter），实验与分析两个能力都吃（Q-2 2026-09-16 翻案）。协调层的 skill 不在这里，在内仓 `coordinator/`（放哪、怎么注入见 Q-10）；两条路径不相交（P-11）。

### 加一个新领域

新建 `domains/<id>/profile.yaml`，其余可选。不改 `framework/`。领域按**工具链或任务类型**命名（`petab`、`ml`），不按学科：平台看到的是「9 个参数最小化一个标量」这种形状，学科是任务包 `source` 指回的案例卡的事。第一个真领域包是 `domains/petab/`（[#39](https://github.com/zephyr4123/TJU-AI4Science/issues/39)）。

## 4. 发现与校验

- 框架启动时扫 `domains/*/profile.yaml` 与 `tasks/*/manifest.yaml`，按目录名当 id；同名冲突直接报错。
- 用户自己的包可以放在包外目录，通过环境变量追加搜索路径；**所有搜索路径的包待遇相同**，不存在"包内的才有提示词"。
- CI 门禁：删掉全部 `domains/` 与 `tasks/`，`framework/` 的测试照样过（P-5）。
- `ai4sci task validate` 与 `ai4sci domain validate` 两条命令做 schema 校验，任务包与领域包各自有 schema 文件放在 `framework/schemas/`；`ai4sci task env build` 按 `env/` 建任务级 venv。

## 变更记录

| 日期 | 改了什么 | 为什么 | 认可 |
|---|---|---|---|
| 2026-09-10 | 建档。任务包与领域包的目录、manifest 与 profile 字段、harness 约束、发现规则 | 泛化边界的结论：流程通用、任务不通用，适配必须是写文件 | 主人 + Claude |
| 2026-09-10 | budget 加可选 patience / min_delta / max_cost_usd；harness 约束加 evaluate 退出方式与 status 字段的读取点、.gitignore 提醒（[#24](https://github.com/zephyr4123/TJU-AI4Science/issues/24)） | 内环实现的读取点反推回契约 | 主人 + Claude |
| 2026-09-10 | run_0 布局、验证集拆两份、make_run0.sh、schema 只收有读取点的字段（[#21](https://github.com/zephyr4123/TJU-AI4Science/issues/21)） | 第一个任务包落地后的实测形态 | 主人 + Claude |
| 2026-09-10 | manifest 明确由协调层拍板后填写；全景加 `coordinator/`；领域包 `skills/` 限定为执行层用，与协调层 skill 隔离；"阶段"改"能力"、"底座"改"执行层"（[#18](https://github.com/zephyr4123/TJU-AI4Science/issues/18)） | 加了协调层，契约的填写权归它；两层 agent 的 skill 必须物理隔离（P-11） | 主人 + Claude |
| 2026-09-16 | 任务包加 `env/`（python-version + requirements.lock，uv 建任务级 venv，launcher 只经 `$AI4SCI_PYTHON` 起 Python）；manifest 加 `format_version` 必填与 `source` 可选；领域 skill 注入改走 prompt 快照；领域按工具链命名；接任务清单加分工与环境步骤（[#39](https://github.com/zephyr4123/TJU-AI4Science/issues/39) [#40](https://github.com/zephyr4123/TJU-AI4Science/issues/40)） | 第一个真实输入到了（#1）：任务跑在平台 venv 里、领域知识没家、接任务靠手攒，三处在真任务面前全露；按工业级开源项目标准补 | 主人 + Claude |
