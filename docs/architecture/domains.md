# 领域包

- 状态：**aligned**（形态）
- 最近变更：2026-09-19
- 依据：[AutoResearchClaw 深读 §7](../../research/selection/2026-0909-pipeline-frameworks/autoresearchclaw.md#7-领域适配与-arc-bench)（profile 的形态，以及它在注册上栽的坑）

流程通用，任务不通用。适配的形态是**写文件，不是改代码**：一个领域一个目录，框架启动时扫目录发现，没有注册表（P-5）。工作区的目录（需求、原件、七个阶段的产出）见 workflow §1 磁盘布局；原来这里的「任务包」一节随 2026-09-19 的重定删了（[#104](https://github.com/zephyr4123/TJU-AI4Science/issues/104)）——manifest 里机器读的那半、harness、env、基线现在是设计阶段的产出，是实验这一族能力私下的约定，框架不再认它们的 schema；harness 的规矩（只读、hash、独立进程、只吃产物文件，P-6）由实验族的能力自己守。

## 1. 领域包

```
 domains/                 一个领域一个目录，按工具链或任务类型命名
 ├── generic/             兜底，任何任务都能用
 └── petab/
     ├── profile.yaml     必有
     ├── prompts/         可选：各能力的领域补充提示
     ├── tools/           可选：求解器封装、网格生成、单位换算
     └── skills/          可选：领域 skill（P-22 格式），只进执行层的清单
```

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
- `skills/<name>/SKILL.md`：领域 skill，格式与平台通用的 `skills/` 一样（agentskills.io 规范，P-22：SKILL.md + scripts/ + references/，脚本 PEP 723 自带依赖）；只进**执行层**的清单——起执行层会话时框架把所选领域包的 skill 与通用 skill 一起拼成 `<available_skills>`，agent 用 `ai4sci skill show / run` 读与跑。不走 CLI 原生机制：执行层的隔离参数（`--setting-sources ""`、`--disable-slash-commands`，见 workflow §5）把本机 CLAUDE.md、plugin、skill 一并关掉了，这正是 P-11 要的。AutoResearch 开实验时仍把领域包的提示补充（`prompts/experiment.md`）快照进产出目录；skill 不快照——清单里只有名字，执行层 `ai4sci skill show` 读的是库里的现版本，读了什么在那一轮的事件流里（2026-09-20 落地时定，[#113](https://github.com/zephyr4123/TJU-AI4Science/issues/113)）。

### 加一个新领域

新建 `domains/<id>/profile.yaml`，其余可选。不改 `framework/`。领域按**工具链或任务类型**命名（`petab`、`ml`），不按学科：平台看到的是「9 个参数最小化一个标量」这种形状，学科是需求文档指回的案例卡的事。第一个真领域包是 `domains/petab/`（[#39](https://github.com/zephyr4123/TJU-AI4Science/issues/39)）。

## 2. 发现与校验

- 框架启动时扫 `domains/*/profile.yaml`，按目录名当 id；同名冲突直接报错。
- 用户自己的包可以放在包外目录，通过环境变量追加搜索路径（`AI4SCI_DOMAINS_ROOT`）；**所有搜索路径的包待遇相同**，不存在"包内的才有提示词"。
- CI 门禁：删掉全部 `domains/` 与 `workspaces/`，`framework/` 的测试照样过（P-5）。

## 变更记录

| 日期 | 改了什么 | 为什么 | 认可 |
|---|---|---|---|
| 2026-09-10 | 建档。任务包与领域包的目录、manifest 与 profile 字段、harness 约束、发现规则 | 泛化边界的结论：流程通用、任务不通用，适配必须是写文件 | 主人 + Claude |
| 2026-09-10 | budget 加可选 patience / min_delta / max_cost_usd；harness 约束加 evaluate 退出方式与 status 字段的读取点、.gitignore 提醒（[#24](https://github.com/zephyr4123/TJU-AI4Science/issues/24)） | 内环实现的读取点反推回契约 | 主人 + Claude |
| 2026-09-10 | run_0 布局、验证集拆两份、make_run0.sh、schema 只收有读取点的字段（[#21](https://github.com/zephyr4123/TJU-AI4Science/issues/21)） | 第一个任务包落地后的实测形态 | 主人 + Claude |
| 2026-09-20 | `skills/` 改按 P-22：与平台通用 skill 同格式（agentskills.io），由框架拼清单注入、`ai4sci skill` 读与跑，不再说「与 Claude Code 原生同格式」（[#113](https://github.com/zephyr4123/TJU-AI4Science/issues/113)） | skill 系统对所有适配器通用 | 主人 + Claude |
| 2026-09-20 | 领域 skill 不再随实验快照、不再全文注入：只进执行层的清单，`ai4sci skill show` 读库里的现版本（[#113](https://github.com/zephyr4123/TJU-AI4Science/issues/113)） | 落地时定：快照与清单二选一，事件流已经记了执行层读了什么 | 主人 + Claude |
| 2026-09-10 | manifest 明确由协调层拍板后填写；全景加 `coordinator/`；领域包 `skills/` 限定为执行层用，与协调层 skill 隔离；"阶段"改"能力"、"底座"改"执行层"（[#18](https://github.com/zephyr4123/TJU-AI4Science/issues/18)） | 加了协调层，契约的填写权归它；两层 agent 的 skill 必须物理隔离（P-11） | 主人 + Claude |
| 2026-09-16 | 裁判文件的契约：`budget.inner_k`、框架保证给 harness 的三个环境变量、写默认值判不合法、`ai4sci task baseline` 按钮（[#43](https://github.com/zephyr4123/TJU-AI4Science/issues/43) [#44](https://github.com/zephyr4123/TJU-AI4Science/issues/44)） | 模仿研究者测试里评分脚本的静默默认值只被 agent 的眼睛抓到；栏杆只加在裁判文件、只加在出过事的变量上 | 主人 + Claude |
| 2026-09-16 | 接任务清单加人发布（`publish.json` 钥匙）与机器预检（`attainable` 尽头值），接任务与跑基线升格成 task 级能力 `cap design` / `cap baseline`，加 `flow check`；「人签 evaluate.py」改为协调 agent 对照 design.md 核对（[#47](https://github.com/zephyr4123/TJU-AI4Science/issues/47) [#48](https://github.com/zephyr4123/TJU-AI4Science/issues/48) [#49](https://github.com/zephyr4123/TJU-AI4Science/issues/49) [#50](https://github.com/zephyr4123/TJU-AI4Science/issues/50)） | 产品形态定为两个发布键一次验收（vision）：签字挪到脚本之前、签的是规则不是代码；「看基线」那个停点机器能算 | 主人 + Claude |
| 2026-09-16 | 接任务清单改成按钮版：协调层三问 + manifest + env + `design.md`，`ai4sci task design` 起执行层写草稿并由框架封 harness、lint、校验，人签字后跑基线（[#41](https://github.com/zephyr4123/TJU-AI4Science/issues/41)） | 平台给非工程师用（vision「给谁用、凭什么」）：接任务的七步手工里唯一不是按钮的一步做成按钮，剩下的靠对话；停点状态与面板往后 | 主人 + Claude |
| 2026-09-16 | 任务包加 `env/`（python-version + requirements.lock，uv 建任务级 venv，launcher 只经 `$AI4SCI_PYTHON` 起 Python）；manifest 加 `format_version` 必填与 `source` 可选；领域 skill 注入改走 prompt 快照；领域按工具链命名；接任务清单加分工与环境步骤（[#39](https://github.com/zephyr4123/TJU-AI4Science/issues/39) [#40](https://github.com/zephyr4123/TJU-AI4Science/issues/40)） | 第一个真实输入到了（#1）：任务跑在平台 venv 里、领域知识没家、接任务靠手攒，三处在真任务面前全露；按工业级开源项目标准补 | 主人 + Claude |
| 2026-09-19 | 「任务包」一节整节删掉，文档改名 domains.md 只讲领域包；工作区的目录归 workflow §1（[#104](https://github.com/zephyr4123/TJU-AI4Science/issues/104)） | 主人：目录为 auto-research 量身定做，该删的大胆删，文档要干净 | 主人 + Claude |
