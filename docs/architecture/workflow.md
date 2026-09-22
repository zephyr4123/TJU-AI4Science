# 流水线：能力与实验内环

- 状态：**aligned**（形状）；首版提供哪几个能力，见 Q-1
- 最近变更：2026-09-19（P-20 阶段主文件表；§5 界面加文件镜头）
- 依据：[InternAgent 深读](../../research/selection/2026-0909-pipeline-frameworks/internagent.md)、[autoresearch 深读](../../research/selection/2026-0909-pipeline-frameworks/autoresearch.md)、[AutoResearchClaw 深读](../../research/selection/2026-0909-pipeline-frameworks/autoresearchclaw.md)

三个仓的编排形态都是"外层 for + 硬编码状态判断"，差别全在循环之外：用什么承载状态、用什么规则收敛、用什么机器判据卡住造假。我们不写那个 for：**串联能力的是协调层（人 + agent），框架只提供能力**。流水线层因此只有两样东西：**各自可调的能力**和住在其中一个能力里的**实验内环**。

## 1. 三层：研究阶段、能力、实现

科研分七个阶段：文献、假设、设计、实验、分析、写作、验证。阶段不定先后，经过哪几个阶段、按什么顺序是**流程**说了算，流程是人定的：假设完直接写作是开题报告，实验完回设计是改评分脚本，任何组合都成立（P-18，2026-09-18 与主人对齐，[#93](https://github.com/zephyr4123/TJU-AI4Science/issues/93)）。

```
 阶段            七个固定：文献 假设 设计 实验 分析 写作 验证         不定先后，任意组合
   └ 能力        一个阶段里的一件活；对协调 agent 就是一条 ai4sci cap 命令   细颗粒度，五栏说清边界
       └ 实现    这件活怎么干：一段代码、一个 skill、领域包里的东西     一个能力可以有几种实现，也可以暂时零实现（空槽照样列出）

 一条流程 = 经过几个阶段、按什么顺序、每个阶段挂哪些能力（可以不挂：助理看着办）、哪几个阶段完了要人签

 断点 = 这个阶段的产出要人签了下游才能读。几个、放哪由流程定：端到端全自动的流程一个没有，步步确认的流程每步一个。
        签字落在产出目录里（signed.json）；「发布」「验收」只是两个常见的放法，不再是框架里的特例（2026-09-19，P-19）
```

- **能力是细颗粒度的。** 一个只干一件说得清的活：分析阶段里的「写分析初稿」只读实验留下的东西写三节初稿，不是「分析」的全部；以后的对比、作图、复盘都是这个阶段里另外的能力。写作阶段同理：写综述、写正文、画图各是一个。
- **能力的描述符五栏必填**（`framework/contracts/capability.py`）：职责、边界、输入、产出、终止条件。讲机制、带通用的专业术语（auto-research 要讲清 git 分支 tip 是 best、refs/attempts 留档、统计门棘轮），不是小学生作文，也不是路径表。研究者、协调 agent、工程师读同一份；`ai4sci show caps` 与 `GET /cap` 就是它。
- **能力是纯函数：显式输入 → 一个产出目录。** 输入用 `--from <stage>/<n>` 点名（读了哪几个产出），产出是它所属阶段下的一个新目录。能力自己没有「最新」这种状态，不默认读谁：选输入是协调层的事——agent 看盘决定，或人指定（2026-09-19 主人：能力挂在流程的某个阶段上，天然解耦，给 agent 用也给人用，不随任务变）。
- **实现是能力下面的一层。** 一段自己写的代码（auto-research）、一个 skill（nature 写作 skill 归写正文，nature image skill 归画图）、领域包里的东西都算。领域包不是一层，只是打包单位：拆开各归各的能力。代码里只在出现第二种实现时才建模（有第二个用例才抽象）。 **skill 不是一格**：它是 agent 用的工具包（见下面「skill」一节，P-22），不开产出目录、不出现在流程里，写哪里由调用它的人定；要当一格就包成能力（P-20）。
- **阶段之间没有显式的输入输出接口，机器不做数据流校验。** 能力开工时 `from` 里没有它要的文件就报错说清缺哪个阶段的哪个文件（P-7）；流程的检查只查三件事：阶段名对不对、点名的能力在不在那个阶段、参数名与类型对不对。**文件仍是产物的载体**——一个文件一个生产者、命名三规矩（P-13）保留——但不是拼流程的接口。

现在有的（2026-09-19，[#104](https://github.com/zephyr4123/TJU-AI4Science/issues/104) [#106](https://github.com/zephyr4123/TJU-AI4Science/issues/106)）：

| 阶段 | 能力（命令） | 谁跑 | 一句话 |
|---|---|---|---|
| 文献 | — | | 没有能力时助理自己开产出目录写 notes.md |
| 假设 | — | | 同上；原来的 `init` 删了：建工作区 = 写需求 + 搬原件，不是一个阶段的能力 |
| 设计 | `design` 评分脚本与基线 | 执行层 + 机器 | 读需求与假设，执行层写 harness/ 与 code/，框架封 harness，跑基线、算预检；留下 scoring.yaml（原 manifest 里机器读的那半） |
| 实验 | `auto-research` AutoResearch | 执行层 + 机器 | 读设计的产出，一轮一轮改代码：过统计门才 keep，否则回退到 best |
| 分析 | `analysis` 分析初稿 | 执行层 | 读一个或几个实验的账本与结果，写三节固定的 analysis.md |
| 写作 | — | | |
| 验证 | `verify` 数字核对 | 机器 | 分析里的数回溯到实验的 results.json，账本与 git 对账，PASS / FAIL |

- **每个能力一次执行层调用，新会话。** 上下文从磁盘来，不靠上一个能力的会话。这是 P-1 与 P-3 的直接推论。
- **失败处理**：FAILED 就停，不模板兜底、不静默跳过（P-7）。重试是显式配置，默认 0。
- **回退**：框架不判断"要不要回到设计"，协调层看了分析结论决定。重做一个阶段就是这个阶段下多一个产出目录，旧的原样留着。
- **并行**：v0.x 不做。

### 流程：经过几个阶段

一条流程一个 YAML（`workflows/*.yaml`，`framework/contracts/workflows.py`）：

```yaml
name: research
title: 从课题到验证
summary: 评分脚本与基线，人核对；AutoResearch、分析初稿、数字核对，人验收。
stages:
  - 设计                                     # 一个阶段：用什么能力由助理看着办
  - 断点: 评分指标核对     # 设计的产出要人签
  - 实验: {auto-research: {max_iters: 3}}   # 点名能力、带参数（参数名是描述符里的 Param）
  - 分析: [analysis]                         # 点名不带参数
  - 验证
  - 断点: 验收                               # 验证的产出要人签
```

- **出厂两条**：`research`（改进：设计 → 实验 → 分析 → 验证）与 `reproduce`（复现，P-24，2026-09-21）；截一段、改参数、换断点都是新的流程。`reproduce` 长这样：

  ```yaml
  name: reproduce
  title: 论文复现
  summary: 找齐材料，原样跑一遍，人核对；复现性分析、数字核对，人验收。
  stages:
    - 文献                                   # 助理自带搜索找材料，手写 sources.md（材料来源）
    - 设计: [reproduction]                   # 原码复现基线：别人的代码进 code/，跑一次
    - 断点: 复现结果核对                     # 论文值与我们的值并排，研究者签
    - 分析: [reproducibility]                # 复现性分析
    - 验证
    - 断点: 验收
  ```

  没对上再进实验做差距归因，那条分支第一次撞上再拼。
- **子集也是流程、任何顺序都是流程。** 只想根据实验结果写综述就是 `[实验, 写作: [review]]` 两行——等写作阶段有了那个能力就能挂。
- **流程分两层：库、实例**（P-15）。库在 `workflows/`，通用、不依附课题，编辑台的流程助理改它；实例在工作区 `flows/`，几条都行，研究助理 `ai4sci flow take <name>` 从库里取来，按这份需求改阶段、能力参数、断点。选流程在需求确认之后、与需求独立：一份需求会走多条流程。
- **进度不另存**（2026-09-19，删了 `flow.json`）：每个产出的 `meta.yaml` 记它是在哪条流程的第几项下产的，「这条流程走到哪」沿 `from` 链算出来；同一条流程走两遍就是两条链，看板都列。「在等谁」也现算：作业在跑 → 等作业；这一项的产出还没签而流程说要签 → 等人；下一项是阶段 → 轮到助理；走完 → done。
- **编排工作台的意义是立规矩，不是做数据流校验。** 研究者要的是三样：看得见接下来会发生什么、在关键处能拦一手、下次能照做。排阶段、挂能力、插断点正好是这三样；"能力之间的输入输出对不对得上"是工程师给自己发明的问题。

### 磁盘布局

2026-09-19 与主人从第一性原理重定（[#104](https://github.com/zephyr4123/TJU-AI4Science/issues/104)）。原来的目录以「一次 auto-research」为单位建模（`runs/<id>/work + experiment`），工作区、流程、分析、验证都是后挂上去的；任务包抄三遍以上；文献、写作没有落点。科研是频繁返修、多对多的：实验不止跑一次，数据不只一份，假设也不只一版。所以：**一个阶段一个目录，里面每次产出一个子目录，产出之间靠 `from` 引用；需求是根；平台自己的记录藏起来。**

```
<数据根>/
├── workflows/                 流程的库（编辑台改）
├── templates/                 需求模板的库：通用一份，按学科加，可扩展
├── studio/                    编辑台的对话记录
└── workspaces/<id>/
    ├── requirement.md         需求：助理和人对话攒出来的，形式开放，按模板起草不定死大纲
    ├── requirement.lock       需求确认：谁、何时、hash、版本。唯一内置的门：没确认任何阶段不开工
    ├── materials/             原件（PDF / 数据 / 代码），只增不改
    ├── flows/                 这个课题取来的流程，几条都行
    ├── literature/   1/ 2/    七个阶段各一个目录（英文 slug，阶段名 ↔ slug 一张表在 contracts）
    ├── hypothesis/   1/ 2/    流程没走的阶段没有目录：ls 一眼看出走到哪
    ├── design/       1/
    ├── experiment/   1/ 2/ 3/
    ├── analysis/     1/
    ├── writing/
    ├── verification/ 1/
    └── .ai4sci/               平台记录，不是研究产物：chats/ jobs/ logs/ requirement/v1.md …

experiment/2/                  一个产出目录
├── meta.yaml                  框架只读这一份：id、stage、title、from（读了谁，每项带 sha256）、by（能力名 / assistant / human）、
│                              params、flow、step、requirement（哪版需求）、created_at、
│                              compute（在哪台机器上跑的：名字、主机名、GPU 型号；P-23 的出处）
├── signed.json                流程里有断点才有：人签的——谁、何时、签的哪些文件的 hash、一句话
└── …                          其余全是产它的那个能力自己的文件，框架不看、不定、不校验
```

- **产出的 id 就是路径**：`experiment/2`、`analysis/1`。读出来就知道是什么，不用查表；`title` 是给人看的标签，目录名不动。
- **接口 = `from` + 文件名。** 不把上游整包抄进自己目录；执行层要的合成工作树在自己那次产出里（`experiment/<n>/work/`），是实现细节。
- **冻结**：产出和需求同一条规则——没被 `from` 引用、没被签之前随便改；一旦被引用或被签就冻住，改了框架按 hash 查得出并拒读。需求确认之后再改，页面显示 diff、人再确认成 v2，旧版存 `.ai4sci/requirement/`。
- **助理不经能力也能产出**（文献、写作现在没有能力）：`ai4sci output new <stage> --title … --from …` 建目录写 meta，然后直接写文件。文献格的主文件 `sources.md`「材料来源」就是这么写的（P-24）：它是文献阶段第一个定下的主文件（`MAIN_FILES`），形状只有文件名——助理写 markdown，下游是 agent 在读。
- **一个工作区一份需求，一对一；工作区上方不加层。** 哪天一篇论文要拆几个子课题，再加 `projects/`，现在没有第二个用例。

### 契约

**框架只认 `meta.yaml`、`signed.json`、`requirement.lock`、流程文件、能力描述符这几样的形状。** 产出目录里其它一切归产它的那个能力：设计能力留 `scoring.yaml`、实验能力就去读它，两个能力私下约好的文件名写在各自描述符的「产出 / 输入」两栏里，框架从头到尾不知道有 `scoring.yaml` 这回事。换一个学科就是换一族能力：

```
实验族   design/1   scoring.yaml · harness/ · env/ · baseline/
综述族   design/1   search-plan.md · inclusion-criteria.md
仿真族   design/1   model.cfg · sweep.yaml
```

框架看它们都一样：`design/1/meta.yaml` 加一堆文件。原来 `framework/contracts/` 里的 manifest schema、results、report、headroom 都是实验这一族的，搬进对应能力的包里（P-4 的「契约机器可校验」在能力里落，不在框架里）。

**产出目录里的文件分两层，能力不自创名字**（P-20，2026-09-19，[#110](https://github.com/zephyr4123/TJU-AI4Science/issues/110)）：**阶段主文件**按阶段定、不按能力定——进这个阶段的任何能力都必须留下它，下游只认它、不认是哪个能力产的，所以换一个同阶段的能力下游不改；**族文件**是同族能力私下的约定（上面三族各自那一堆），只在族包 `framework/<族>/` 里定，开新族是一次决策；能力另外留的文件是**私有的**，谁都不许依赖，下游要用就提成族文件。一个阶段一行、第一个进来的能力定名、之后锁死；还没有能力的阶段不预填（有第二个用例才抽象）：

| 阶段 | 主文件 | 状态 |
|---|---|---|
| 文献 | — | 待第一个能力定（助理手写时留 `notes.md`） |
| 假设 | — | 待第一个能力定 |
| 设计 | `scoring.yaml` | 已定（`design`） |
| 实验 | `ledger.tsv` + `iters/iter_N/results.json` | 已定（`auto-research`） |
| 分析 | `analysis.md` | 已定（`analysis`） |
| 写作 | — | 待第一个能力定（Q-12 的方向是 `draft.md`） |
| 验证 | `report.json` | 已定（`verify`） |

设计那一行现在是实验族定的名；第二个族（综述、仿真）进设计阶段那天，要么留同一个名、要么把主文件改成族无关的，那是一次决策不是顺手（`capabilities.MAIN_FILES`，`discover()` 守着「产出」栏里写到了它）。

**谁产的记在 meta，不记在文件名。** `writing/1/draft.md` 与 `writing/2/draft.md` 同名，`meta.yaml` 的 `by`（哪个能力）、`from`（读了谁，带 hash）、`requirement`（按哪版需求）、`result`（一句结论）不同；页面的「来源 / 输入」、`ai4sci show output`、冻结的 hash 核对都读它。扫全部 `meta.yaml` 就是一张有向无环图：节点是产出、边是 `from`、需求版本是根、签字是节点状态；一条流程是图里的一条路径，主页面的「一条流程一张表」是沿一条流程的投影。两个局限如实记：助理 `output new` 手写的产出 `from` 可能为空（是助理的纪律，框架补不了）；原件 `materials/` 不是节点（没记谁读了哪份）。

**能力描述符**（`framework/contracts/capability.py`）：每个能力子包导出 `DESCRIPTOR`（name、stage、title、brief、五栏、params，参数带 label）与统一入口 `run(output_dir, inputs, ports, **params)`；`capabilities.discover()` 扫子包并断言入口签名与描述符的参数表一致，子包名下划线对命令名连字符（`auto_research/` 就是 `ai4sci cap auto-research`）；`ai4sci cap` 的子命令从描述符生成，每个都有 `--from`，所以 CLI 参数与描述符一致是构造保证。能力上**不写**「属于哪条流程」：流程文件点名能力，反过来写是两份真相；`show caps` 与 `GET /cap` 的 `used_by` 是反查算出来的。

**能力的文案分三层**（P-21，[#112](https://github.com/zephyr4123/TJU-AI4Science/issues/112)），`discover()` 守着：`title` 是**名**——名词短语不超过八字（评分脚本与基线、分析初稿、数字核对），方法有公认名字的原样写（`auto-research` 是 AutoResearch），不用动宾；`brief` 是**一行**——三十字内一句，说拿什么做出什么，不带路径与参数名（「自动迭代代码，逐轮记账」）；五栏是**详情**——页面与文档里的栏名是 职责 / 边界 / 输入 / 产出 / 终止条件（字段名 `does` / `does_not` / `brings` / `leaves` / `stops` 不变），工程语言陈述句：文件名可以写（`scoring.yaml`、`ledger.tsv` 是工作区里真实存在的东西，文件镜头里就能看到），CLI 参数不写（`--from design/<n>` 写成「设计阶段的一次产出」），框架内部机制不写（目录 hash 校验、`refs/attempts`），口语不写（「这包」「越界」「续命」）。协调层读的是同一份详情，不另写用户版。参数的 `label` 是页面上的名字（`max_iters` → 最多轮数），`help` 是 hover 的一句。执行者的种类（`needs_executor`、能不能续跑）是机器读的，不上屏。

**接口是文件名，不是 schema**（P-13，[#54](https://github.com/zephyr4123/TJU-AI4Science/issues/54)；2026-09-18 收窄，[#93](https://github.com/zephyr4123/TJU-AI4Science/issues/93)）：一个文件只有一个生产者，格式由生产者定，谁要用就报名字、不问格式；命名三规矩见 README P-13。它管的是**产物怎么命名、谁能写**，不管**流程能不能拼**。内容契约在描述符的「产出」栏里用工程语言说（账本有哪几列、report.json 的 status 是什么）。

### skill

**skill 是给 agent 用的工具包，不是流程里的一格**（P-22，2026-09-20，[#113](https://github.com/zephyr4123/TJU-AI4Science/issues/113)）。能力是流程里的一格、开产出目录、由框架驱动；skill 是 agent 在任何时候都能拿起来用的一套东西——一份说明、几个脚本、几份参考——协调层（研究助理起草需求时读论文）与执行层（能力的会话里解析文件）都能用。它不开 `<stage>/<n>/`，写哪里由调用它的人定：助理写进 `materials/`，能力写进自己的产出目录。三样东西的关系：

| | 是什么 | 谁调 | 写到哪 | 在哪儿定义 |
|---|---|---|---|---|
| 能力 | 流程里的一格，`ai4sci cap <name>` | 协调层（照流程） | 自己的 `<stage>/<n>/` | `framework/capabilities/<name>/` |
| skill | agent 的工具包，`ai4sci skill run <name>` | 协调层或执行层，随时 | 调用方给的 `--out` | `skills/<name>/` 或 `domains/<包>/skills/<name>/` |
| 领域包 | 打包单位：提示补充 + 领域 skill + 工具 | 设计阶段按 `--domain` 选 | — | `domains/<包>/` |

**格式照 agentskills.io 开放规范**，不自造：

```
skills/<name>/                     name 等于目录名，全局唯一（与 domains/*/skills/ 合起来也唯一）
├── SKILL.md                       frontmatter + 正文；正文五百行以内，细节进 references/
├── scripts/                       可执行脚本，每个自带依赖声明与锁文件
│   ├── extract.py                 头部 # /// script 块：requires-python、dependencies
│   └── extract.py.lock            uv lock --script 生成，进仓
├── references/                    agent 按需读的长文档（格式说明、坏页处理、后端差异）
└── assets/                        模板、样例文件（可选）
```

frontmatter 只用规范里的字段，不用任何一家 agent 的专有字段（换适配器就失效，也过不了别家的校验）：

| 字段 | 必填 | 写什么 |
|---|---|---|
| `name` | 是 | 小写字母数字连字符，等于目录名 |
| `description` | 是 | 一句话：做什么、什么时候用——清单里只显示它，agent 靠它决定要不要读全文 |
| `compatibility` | 否 | 自由文本：Python 版本、系统包（poppler、tesseract 这类 uv 装不了的）、要不要 GPU |
| `metadata` | 否 | string → string；我们自己的键加 `ai4sci-` 前缀（如 `ai4sci-layer: coordinator, executor`） |

正文按 progressive disclosure：清单里只有名字与一句话（约百字），`ai4sci skill show` 才给正文，脚本与参考按需读。正文写：什么时候用、命令怎么敲、留下哪几个文件（文档即接口，P-13）、常见失败怎么办。

**脚本的规矩**（agentskills.io 的脚本指南 + 我们的 CLI 口径）：

- 非交互、有 `--help`；结果 JSON 到 stdout，诊断到 stderr；幂等；退出码 0 成、非 0 败且 stderr 说清。
- 输入用参数点名，输出目录由调用方 `--out` 给（缺省：输入文件旁同名目录）；脚本不猜路径、不写别处。
- 依赖用 PEP 723 内联元数据（`uv add --script` 写），`uv lock --script` 出锁文件进仓；`requires-python` 由脚本自己定，与框架的 3.14 解耦（pdf 后端要 3.12 就写 3.12）。
- 运行一律 `uv run --locked --offline <脚本>`：uv 按脚本在全机缓存（`~/.cache/uv/environments-v2/`）建隔离环境，所有工作区共享一份；锁漂移报错不静默；沙箱断网也照跑。
- 系统包（uv 管不了的）写进 `compatibility`，`make skills` 探测，缺了报错说装什么。
- 三套环境互不 import：平台 venv（框架）、课题 venv（`materials/env/` → 每次实验一份）、skill 环境（uv 缓存）；只用文件与 JSON 交接。

**不建工作区级 venv。** 业界（agentskills.io、Anthropic 自家 skills 仓、MCP 的 uvx 惯例）没有一家这么做；skill 的依赖是 skill 的属性，不是工作区的属性——每工作区一份意味着装 N 份、版本各自漂，而工作区打包交同事时 venv 本身搬不走，真正让它自包含的是锁文件。只在「某课题要求 skill 用别的版本」时，用 uv 的 `UV_PROJECT_ENVIRONMENT=<工作区>/.venv-skills` 把那一个工作区的 skill 环境落进去；那是例外不是缺省。

**承接与门禁**：`make skills`（承接第一步之后）对每个脚本 `uv lock --script` 核对并预热环境，这是唯一允许联网的一步；之后运行全部 `--locked --offline`。门禁：每个 `scripts/*.py` 有 PEP 723 头与锁文件、`uv run --locked` 能过；每个 skill 目录有 SKILL.md、name 等于目录名、frontmatter 只含规范字段；正文不超过五百行。

**加载：框架自己注入，不靠任何 agent 的原生机制。** 执行层的隔离参数（`--setting-sources ""`、`--disable-slash-commands`）把 Claude Code 原生的 skill 加载关掉了，协调层同样不开——原生机制各家目录不同（Claude Code 读 `.claude/skills`，Codex、Cursor、Gemini CLI 读 `.agents/skills`），靠它就绑死适配器。做法照 agentskills.io 的接入指南：起会话时扫 `skills/`（执行层再加所选领域包的 `skills/`），拼一份清单进 prompt——

```
<available_skills>
  <skill><name>pdf</name><description>解析论文 PDF 成 markdown、图片与结构化 JSON；研究者给了 PDF、要起草需求或读论文细节时用</description></skill>
</available_skills>
匹配到就 ai4sci skill show <name> 读全文，照它写的命令 ai4sci skill run <name> … 跑。
```

协调层拼进 system prompt（`chat/guide.py` 的前言之后、指南之前），执行层拼进能力组的 prompt 的通用段（`executor/prompting.build_prompt`：领域约定 → 工具包 → 联网）。没有 skill 不输出空块；名字撞了起会话就报错。P-11 的两层隔离不变：指南（`coordinator/`）只给协调层，领域 skill 只进执行层的清单，通用 skill 两层都有。领域 skill 不再全文注入执行层 prompt、不再随实验快照（2026-09-20 落地前是那样）：执行层 `ai4sci skill show` 时读库里的现版本，读了什么在那一轮的事件流里；领域包的 `prompts/experiment.md` 仍快照、仍以「领域约定」注入。

**三个子命令**（P-14：agent 面前只有裸 `ai4sci`，白名单 `ai4sci *` 已经放行）：

```
ai4sci skill list                        清单：名字 + 一句话（与注入 prompt 的同一份）
ai4sci skill show <name>                 正文 + skill 目录的绝对路径 + scripts/ references/ 清单
ai4sci skill run <name> [--script <文件>] [--out <dir>] [--<arg> …]   起脚本：uv run --locked --offline；stdout 原样透出，退出码原样透出
```

`run` 只做一件事：找到脚本、按锁起环境、把参数原样递过去；不解析脚本的输出，不替脚本猜路径。一个 skill 只有一个脚本时直接起它，几个脚本时 `--script <文件名>` 点名（SKILL.md 写清）；`--out` 与其余参数都是递给脚本的。执行层会话的 Bash 白名单只有 `ai4sci skill *`（能力与签字是协调层的），执行层子进程的环境与协调层同一份（venv 的 bin 进 PATH、关后台、Bash 超时对齐本轮）。

**第一个 skill：`pdf`。** 一篇论文 PDF → 三样东西，契约固定、后端可换：

| 文件 | 内容 |
|---|---|
| `paper.md` | 正文 markdown：标题层级、段落、公式（LaTeX）、表格、图的引用（指向 `images/`）、参考文献原文 |
| `images/` | 抽出来的图，文件名与 `paper.md` 里的引用一致 |
| `structured.json` | 分节（标题、页码）、表格（表头 + 行）、图（文件名 + 图注）、参考文献条目、元数据（题目、作者、年份、DOI 若有） |

后端（2026-09-20 同一篇论文实测，PINNs arXiv 1711.10561，22 页，Apple M5 Pro 纯 CPU；细节在内仓 `skills/pdf/references/backends.md`）：**缺省 pymupdf4llm 1.28 版面模式**——1.7 s，214 MB 脚本环境，一个脚本跑完退出；节标题、四张表的数、图与图注、24 条参考文献全对，公式不出 LaTeX、切成图。MinerU 4.0.4 `--tier basic`——同一篇 27.6 s 推理外加常驻服务约 20 s 启动，1.2 GB venv（Apple Silicon 上无条件带 torch）+ 854 MB 模型，运行形态是常驻服务（UDS socket、SQLite 文档库、解析子进程）不是脚本，不合 skill 的形状；多出来的只有公式 LaTeX。所以不当缺省：复现要抄论文公式的课题出现时先手工用 MinerU 出一份放 `materials/`，第二个这样的课题再决定要不要包成 `--script mineru`。切后端不改契约。研究助理的用法：研究者给一个链接或文件 → `ai4sci skill run pdf --input <链接或 materials/<x>.pdf> --out materials/<x>/`（链接由脚本自己下载，原件存成 `source.pdf`；`--input` 收链接就是「联网」的一种：agent 自带的网页读取工具拿不到二进制）→ 按 `paper.md` 起草需求，引用论文报的数从 `structured.json` 的 `tables` 抄；文献阶段的能力要解析论文，调同一个脚本、写进自己的产出目录。

## 2. 实验内环（实验能力）

唯一有循环的地方。这个循环是机械的，不做科研判断，所以可以留在框架里。核心是**四个角色分开**：三个仓都把它们混在一起了。

```
                 ┌──────────────────────────────────────────┐
                 │  执行层 coding agent                      │   只干一件事：改 code/
                 │  只能碰 code/ 目录                          │   不跑、不比、不记账、不碰 git
                 └───────────────┬──────────────────────────┘
                                 │ 改动（runner 事后 diff，runner 提交）
                                 ▼
   ┌─────────────────────────────────────────────────────────────────────────┐
   │  runner（框架，确定性代码，零模型）                                         │
   │                                                                          │
   │   ① 拷快照 run_N/   ② 起独立进程跑 launcher   ③ 读 harness 吐出的产物      │
   │   ④ 跟 best 比：看 scoring.yaml 的 direction，过统计门                         │
   │   ⑤ 好 → 分支前进 / 差 → git reset 回 best     ⑥ ledger 记一行             │
   │   ⑦ 把「分数、好坏、失败分类」压成一小段文本给执行层，回到顶上                 │
   └─────────────┬────────────────────────┬──────────────────────┬────────────┘
                 │                        │                      │
                 ▼                        ▼                      ▼
   ┌────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
   │ harness（设计阶段留的）│   │ git（状态载体）        │   │ ledger.tsv（账本）    │
   │ 框架注入，只读，    │   │ 分支 tip = 当前最好   │   │ 每轮一行，活过 reset  │
   │ 校验 hash；独立进程 │   │ 失败的 commit 被 reset│   │ 每行能跟 git 对账     │
   │ 只吃产物文件      │   │ 物理销毁              │   │ 不进 git             │
   │ 输出 results.json  │   │                      │   │                      │
   └────────────────────┘   └──────────────────────┘   └──────────────────────┘
```

**一轮的时间线**

```
 执行层改 code/ ──commit──▶ runner 跑（固定预算）──▶ harness: metric=0.9712, elapsed=298s
 ──▶ 比 best 0.9731，方向 minimize，差值超过统计门 ──▶ 留，best=0.9712
 ──▶ ledger +1 行 ──▶ 给执行层：「留了。metric 0.9712 (best)。继续。」
```

**规则**

- 执行层只改 `code/`，`harness` 与 `data/` 只读；runner 事后 diff 与 hash 双重校验，变了判 `readonly_violated` 并回滚。
- runner 是裁判：比较、留或回滚、记账、**git 提交**全由 runner 做，执行层不参与也不需要任何 Bash 权限（P-2）。每次实验的 `work/` 是独立 git 仓：分支 tip = 当前 best，`refs/attempts/iter-N` 留档每一个被弃或失败的尝试。
- **统计门**：σ 来自设计阶段基线的 `sigma.json`（同配置重复 k 次，k 与阈值来自 scoring.yaml，默认 k=3、阈值 2σ）；gate = max(accept_sigma × σ, `budget.min_delta`)，差值不过门的判"持平"不留。σ = 0 且没给 min_delta 时 fail-closed：确定性 harness 必须显式声明最小改进量，否则浮点噪声会被当成改进锁进棘轮。这是 autoresearch 跑档里"被 keep 的改进比换种子的波动还小一个量级"的直接教训。
- **固定预算**：墙钟预算写在 scoring.yaml，harness 到时自停；超时 1.5 倍必杀，记 timeout。
- **失败分类**：确定性规则，不调模型，按优先级判：`readonly_violated`（diff 或 hash 发现 harness / data 被改）→ `timeout` → `missing_dependency`（stderr 有 ModuleNotFoundError / ImportError）→ `crash`（stderr 有 Python traceback）→ `no_results`（results.json 缺失、不合 schema、或 harness 自报 status ≠ ok；假成功落在这里）→ `nan_metric`。执行层会话自己没走完（超时、被杀、CLI 崩）判 `executor_failed`，半截改动丢弃，同样计入连续三次。另有两个非失败状态：`noop`（执行层什么都没改，或改动全被 .gitignore 挡住）、`interrupted`（那一轮被杀）。分类结果与修复提示一起给执行层；同类失败连续 3 次判 `unrecoverable`，停。
- **停止条件**：`max_iterations`、连续 `patience` 轮不改进（缺省 5）、`max_cost_usd` 累计用尽、`unrecoverable`；任一触发写 `experiment/stop.json` 并停。已停的 run 再跑一轮都不跑：要不要加预算续命是协调层的决定（P-10）。`--max-iters N` 只是本次调用的配额，用完返回 `batch_exhausted`，不算停止。
- **续跑**：每轮开跑前写 `experiment/inflight.json`，结账后删。`loop resume` 先做 checkpoint、账本、git 三方对账，对不上就 fail-closed；有 in-flight 标记的那一轮记 `interrupted`、在飞的 job 先收尸、候选 commit 进 `refs/attempts/` 再回到 best。`loop run` 撞到 in-flight 标记直接拒绝并指引用 resume。
- **轮间记忆**：`experiment/notebook.md` 一个 run 一本，runner 每轮追加执行层的自述（假设 / 改动 / 预期）、`git diff --stat`、裁决；下一轮整本进 prompt，执行层先读前面试过什么再动手。笔记由 runner 写，活在棘轮之外，回滚不抹。
- **上下文卫生**（P-9）：给执行层的是账本与笔记（有界），不是 stdout；日志落盘。
- **续命**：已停的 run 用 `ai4sci cap auto-research --run-id <id> --patience/--max-iterations/--max-cost-usd --reason` 改预算、清停止标记，journal.md 记一行，然后接着跑；要不要续是协调层的决定（P-10）。
- **revert-to-best**：下一轮的起点永远是分支 tip，不是上一轮的失败候选。

**账本 `experiment/ledger.tsv`**

```
iter  commit   parent   metric   direction  elapsed_s  seed  status   sigma   harness_sha  note                          cost_usd  executor_s
1     b2c3d4e  a1b2c3d  0.9860   minimize   299.7      42    keep     0.0007  9f3e…        halve batch                   0.11      31.2
2     c3d4e5f  b2c3d4e  0.9863   minimize   300.4      42    discard  0.0007  9f3e…        lr 0.04→0.045 (within noise)  0.09      28.0
3     d4e5f6a  b2c3d4e  -        minimize   12.0       42    crash    0.0007  9f3e…        Traceback: ZeroDivisionError  0.10      25.5
4     -        b2c3d4e  -        minimize   nan        42    noop     0.0007  9f3e…        执行层没改任何文件              0.05      12.0
```

- 基线不占行：它活在 checkpoint 的 `best_metric` / `best_commit` 里，账本从第 1 轮开始。`parent` 是结算前的 best commit，keep 行的 parent 链就是棘轮走向。
- 每行的 `commit` 必须能在 git 里找到（keep 的在分支上，其余有 commit 的在 `refs/attempts/` 下），`ai4sci show run` 每次都跑这条对账，对不上退非 0。这是 P-3 的机器判据。
- `sigma` 来自统计门，`harness_sha` 是 `harness/SHA256SUMS` 自身的 sha256，`elapsed_s` 是 compute 测到的墙钟（不采信 harness 自报），`cost_usd` 与 `executor_s` 是执行层那次调用的花费与耗时。拿不到的值写 NaN 或 `-`，绝不写 0。

## 3. 裁判与验证

- **确定性优先**：能用规则判的不用模型。实验能力的 accept / reject 完全确定性；验证能力首批三条零 LLM 判据：报告里的每个数字能回溯到 `results.json`，每条引用在真实学术 API 里存在，每张图由数据文件生成。
- **模型裁判**：需要模型判断的（假设质量、写作质量、需求里 discussion 类的验收），由框架派**一个新会话**，可指定与执行者不同的模型，只给产物不给轨迹，输出结构化 verdict（P-2）。
- **协调层只读判决**：验证结论回到协调层，由它决定接受、重跑还是换方向；协调层不替裁判改判，也不裁自己派出去的活。

### 数字回溯（已落地：分析与验证两个能力）

- **分析的形状**（`experiment/analysis.py`）：`analysis/<n>/analysis.md` 固定三节 `## 结论` / `## 数据` / `## 证伪与未决`；`## 数据` 是表 `| 来源 | 指标 | 值 |`（来源写 `experiment/<n>/baseline` 或 `experiment/<n>/iter_N`），值从 results.json 原样抄，是数字回溯的锚。执行层的 prompt 里附每次实验每一轮的指标清单，只许从清单抄。分析能力只校验形状（三节齐全、表至少一行），不裁判自己的数字（P-2）。
- **验证的四项检查**（`capabilities/verify/checks.py`，零模型）：分析存在；数据表每行 (来源, 指标, 值) 在那个来源的 `results.json` 里能找到，相对容差 1%（`--tolerance` 可调，实际值为 0 时声称也必须为 0）；正文里带小数点或指数的数与表里某个值在容差内相等；账本 × git 对账（复用内环那把尺子）。
- **已知边界**（写在这里，不在代码里静默放宽）：整数不查（轮次、行数都是整数），百分比不查（相对变化没有绝对来源），行内代码与代码块不查。执行层被告知相对变化只写百分比、不写版本号之类带小数点的东西。
- **报告**：`verify/report.json`（schema `contracts/schemas/report.schema.json`）：`status` PASS / FAIL、每项 `passed` 与 `details` 一行一条。PASS 与 FAIL 都写报告，FAIL 再退 1——协调层看退出码，读报告看细节。
- **重跑**：分析与验证重跑时旧目录改名 `analysis_v{n}` / `verify_v{n}`，不覆盖。
- **fail-closed**：门不过就停在门口，不涂黑、不降级（P-7）。

## 4. 人在环

人在协调层的对话里，不是框架的功能。

- 框架不等人：每条子命令跑完一个能力就退出并写状态，需要人判断的事由协调 agent 在对话里问。
- 自主程度是协调 agent 的行为，不是框架的模式：可逆的自己定并记录，贵的带方案来问，拿不准的停。
- 无人值守（挂机过夜）时协调 agent 怎么把问题留给人、人怎么异步回复，是协调层自己的通道问题，platform 0.2.0 不做（Q-7）。
- **长命令不占着对话等**（2026-09-17，[#63](https://github.com/zephyr4123/TJU-AI4Science/issues/63)）：每个能力都有 `--detach`，框架把同一条命令起成独立进程当作业（`.ai4sci/jobs/<id>.json` + 日志），命令等作业过门、开了产出再返回（作业号旁带 `output=<产出 id>`；当场没开起来的——输入被改过、设计那包不合约——直接退 1 把原因带回来，不让 agent 拿着作业号说「开了」，2026-09-20 演练 [#118](https://github.com/zephyr4123/TJU-AI4Science/issues/118)），agent 这一轮就结束；作业跑完，子进程以「框架」的身份给那段对话发一轮（transcript 与 history 标 origin），agent 看结果再向人汇报。能力在哪条流程第几项下跑的记进产出的 `meta.yaml`——记录不是决策，按哪个仍是 agent 定；「在等谁」不存现算（等作业 / 等人签 / 轮到助理 / 走完）。
- **人只做两件事，都落成文件**（2026-09-19，[#104](https://github.com/zephyr4123/TJU-AI4Science/issues/104)）：确认需求（`requirement.lock`，唯一内置的门）、在流程定的断点上签产出（`signed.json`）。两件事在页面上做，或终端 `ai4sci sign`；协调 agent 不替人签。自动化程度是人定的：流程里放几个断点就确认几次，一个不放就是端到端。

## 5. 框架的驱动面与执行层适配

### 协调层怎么驱动框架

框架是一个 Python 包加一条 `ai4sci` CLI。命令行上只有六类东西，每样要么是能力、要么是人的确认、要么是查询、要么是取流程或建产出、要么是入口、要么是 skill（2026-09-19 按 P-19 重定，[#104](https://github.com/zephyr4123/TJU-AI4Science/issues/104)）：

```
ai4sci cap <name> --from <stage>/<n>... [--backend] [--compute] [--<param>] [--detach]
                                      能力：协调 agent 调用的 tool，读 --from 点名的产出，在自己阶段下开一个新产出目录；
                                      子命令从描述符生成，用法错退 2、没通过退 1；需求没确认不开工
                                      六个：design（读需求 + 假设）reproduction（读需求 + 文献的 sources.md + 原件里拉来的代码，P-24）
                                      auto-research（读设计）analysis（读一个或几个实验）reproducibility（读一次设计，P-24）verify（读分析 + 实验或设计）
ai4sci sign <stage>/<n> --by <谁> [--note]   人的确认：给一次产出签字，写它目录里的 signed.json（流程里那一项是断点才需要）
ai4sci requirement confirm --by <谁>  人的确认：确认当前工作区的需求，写 requirement.lock（页面上按同一个函数）
ai4sci show workspaces | workspace | outputs [<stage>] | output <stage>/<n> | jobs | job <id> | flows | caps | workflows | templates | template <name>
                                      查询：只读，与 serve 的 GET 端点同一批函数；workspace 是当前工作区的全貌（需求状态、每个阶段有几次产出、
                                      每条流程走到哪、在等谁）；caps 七个研究阶段各有什么、每个五栏；templates 需求模板的库
ai4sci flow take <name> [--as <新名>]  取流程：把库里的一条流程复制成当前工作区的实例（P-15）
ai4sci output new <stage> --title <一句> [--from ...]   建产出：助理不经能力也能在一个阶段下开目录写东西（文献、写作现在没有能力）
ai4sci workspace new <id> [--title]   入口：起一个工作区（写模板起的 requirement.md、建 materials/）；chat new|send|list [--studio] 终端里聊；serve 网页后端
ai4sci skill list | show <name> | run <name> [--script <文件>] [--out <dir>] [--<arg> …]
ai4sci skill run download git <url> [--commit <sha>] [--into <名字>] | file <url> [--sha256 <hash>] | hf <repo> [--type dataset|model]
                                      拉材料（P-24）：落工作区 materials/<名字>/，stdout 一行收据（来源、commit / hash、路径）；两层 agent 都能按
ai4sci job stop <作业号>                     人叫停一个后台作业：杀整棵进程树，作业记 stopped、它的产出记失败（页面同一个动作）
ai4sci env resolve [--python X.Y] [--compute <名字>] <包名>…   隔离新建：按包名算出钉死传递依赖的完整清单进 materials/env/（uv pip compile，会联网；--compute 到那台机器上算）
ai4sci env use --compute <名字> <解释器绝对路径>   用那台机器上现成的环境：探版本、pip freeze 当清单、写 materials/env/interpreter（P-23 的两问）
ai4sci env add --compute <名字> [--from <requirements.txt>] <包名>…   往那台机器现成的环境里补几个包：pip 进 env use 登记的解释器、重新 freeze、清单头部记补了什么（P-24：复现时镜像环境缺论文仓库要的包）
ai4sci compute add <名字> --ssh user@host:port --key <路径> [--root <远端目录>]   接一台机器：写进按人的 computes.yaml，就地探测并报告（P-23）
ai4sci compute check <名字> | list | remove <名字>   再探一遍 / 清单 / 删一条
ai4sci agent list | check <名字> | use <名字> --for chat|executor [--model <id>] [--effort <id>]   底座（P-25）：有哪几家 coding agent CLI、装了没 / 版本 / 登录 / 能不能说话；换助理或执行层用哪家、每家新对话用的模型与深度，写按人的 agents.yaml
ai4sci check                           冷启动自检（P-25）：底座每家 probe、算力每台 check、存放（数据根在哪、可写、余量）；一项不过退出码非零
                                      skill（P-22）：agent 的工具包，不是流程里的一格；清单、正文、起脚本（uv run --locked --offline）
```

当前工作区由 cwd 决定（往上找 `requirement.md`，`AI4SCI_WORKSPACE` 可指定），agent 的工作目录就是工作区；命令不带工作区路径；数据根 `AI4SCI_HOME` 缺省仓根。`job stop` 与 `env resolve` 是 2026-09-20 第一轮真任务（PINNs，Claude 扮小白研究者）逼出来的两条（[#115](https://github.com/zephyr4123/TJU-AI4Science/issues/115) [#117](https://github.com/zephyr4123/TJU-AI4Science/issues/117)）：研究者说「先停一下」平台没有停的动作；「我不懂环境」时助理手写的三行清单让基线一 import 就炸——非工程师没有现成环境是常态，清单要框架按包名算（`uv pip compile`），建完 venv `uv pip check` 查完整，`--continue design/<n>` 遇 `materials/env/` 变了就拒、要重开。同一轮还定了设计草稿封 harness 前先 `ruff --fix-only --select I`（[#116](https://github.com/zephyr4123/TJU-AI4Science/issues/116)：两版草稿各因一条 I001 让执行层重来 13 分钟）。

CLI 是薄壳：每个能力对外是一个 Python 函数（auto-research 是 `capabilities.auto_research.run`），子命令只做参数解析与退出码。协调 agent 走 CLI，低代码 UI 后端与测试直接调函数，三者跑的是同一段代码（P-12）。

### 算力适配

harness 在哪跑，和执行层 agent 在哪跑，是两根正交的轴，各自一个端口、各自一组适配器。算力端口是策略模式在 Python 里的形态：一个 `Protocol`，一个后端一个文件，靠名字选择。runner 对算力的全部需求只有三件事：快照放过去、跑 `launcher.sh`、产物拿回来。执行层 agent（写代码的那个）永远在本机；远端只跑 harness。

**算力归人（P-23，2026-09-20，[#119](https://github.com/zephyr4123/TJU-AI4Science/issues/119)）。** 平台开源、去中心化，算力由使用者自己配，配置按人不按仓：

```
~/.config/ai4sci/computes.yaml        AI4SCI_COMPUTES 可指向别处；读取点只在 paths.py；不进 git、不进工作区、不进数据根
computes:
  local:  {kind: local}                                          # 出厂自带，永远在
  autodl: {kind: ssh, host: connect.xxx.seetacloud.com, port: 12345,
           user: root, key: ~/.ssh/id_ed25519, root: /root/ai4sci}
default: local
```

- **只有 SSH、只认密钥**：一条记录只有 主机 / 端口 / 用户 / 密钥路径 / 远端根目录；schema 里没有 password 字段（读取点断言）。密钥本身留在 `~/.ssh`，`ssh` 自己去读，不经过对话、不经过文件。AutoDL、实验室机器、学校集群都只是「一台能 ssh 上去的 Linux」，`ssh` 一个适配器通吃；Slurm 是第二个适配器，有第二个用例再写。
- **接机器是对话里的事**：助理能跑 `ai4sci compute add <名字> --ssh user@host:port --key <路径>`，人只提供 ssh 那一行与密钥路径（主机、端口、密钥路径都不是秘密，进对话记录无妨）。`add` 写进文件并就地探测：连得上、Python 版本、uv 在不在（缺就装：`curl -LsSf https://astral.sh/uv/install.sh | sh`）、GPU（`nvidia-smi`）、磁盘；一行一项报告。探测不过也只是报告，记录照留，用的时候再拒。不设的坎（主人：不设自我感动的坎，先放开再收）：加机器不用人确认、不做主机白名单、不限助理改这份文件。唯一一次人手动作是把本机公钥贴进算力平台的控制台（AutoDL 有账号级「SSH 公钥」设置，贴一次以后开的机器都带），那是它的门不是我们的。AutoDL 关机重开端口会变：`compute check` 报连不上，`compute add` 同名覆盖。
- **agent 按名字选**：助理看到的是 `ai4sci show computes`（名字、种类、GPU、可不可用、上次探测），`--compute <名字>` 每次调用给，记进产出 `meta.yaml` 的 `compute`（名字、主机名、GPU 型号）当出处；不给就用文件里的 `default:`；流程实例里也能写。需求只写要求（要 GPU、单卡几小时），不写机器名；需求要 GPU 而清单里没有，助理该说「去接一台」，不是绕。
- **接上先盘点、再问两问**（主人 2026-09-20）：`compute add` / `check` 盘点那台机器上已有的 Python 环境（conda 各环境与系统 python：解释器、版本、torch / cuda），助理念给研究者，问「隔离新建还是用现成的」「用哪个」，两边的取舍说清（隔离：版本锁死可复现、第一次下几 GB；现成：几秒起跑、版本以那台机器为准、换机器要重选）。**租来的第三方平台（AutoDL 这类）一律用镜像自带的现成环境**，租的时候就选好带 PyTorch + CUDA 的镜像，不在上面自己装隔离环境（主人 2026-09-20 演练拍板：实测装 CUDA 版 torch 两个多小时没完，机器一关环境也没了，隔离的可复现落不到实处）；隔离新建只在实验室自己的机器上谈；「你看着办」按机器是谁的定。
- **环境按目标机器算**：隔离新建 `ai4sci env resolve --compute autodl …` 到那台机器上 `uv pip compile`（CUDA 版 torch 只在那边解析得对）；用现成的 `ai4sci env use --compute autodl /root/miniconda3/bin/python`——`materials/env/interpreter` 记 `<算力名字>:<解释器>`，那个环境的 `pip freeze` 当清单留出处，那台机器上直接用不建 venv，换机器拒。远端 uv 用那台机器 pip 配的镜像当额外索引（AutoDL 直连 pypi.org 19 KB/s）；建 venv 这类长命令也走 nohup + 轮询，不在一条 ssh 长连接里干等。基线是远端 `make_run0.sh` 从头写出的一整个 `baseline/`：跑之前本地那份先删干净，拿回来（只加不删）后按开跑那套合约查全——「design ok」就等于实验阶段会接，不留设计说过、实验说不过的缝（演练里上一版基线的 `results-<seed>.json` 留在本地 `repeats/`，人签了字实验一数文件数就拒开）。**现成环境缺包就补，不整套重建**（P-24，第二轮演练 GUA）：镜像自带的环境缺论文仓库要的几个小包（scipy、torchjd），`ai4sci env add --compute <名字> --from materials/<代码目录>/requirements.txt` 装进那个解释器、重新登记清单；`reproduction --continue` 时解释器没变只是清单多了几行就刷新快照接着跑，壳不用重写——实测助理只能让研究者登录机器 pip、教他去网页终端粘命令，非工程师做不到。**执行层会话的额度按能力给**：读懂别人整个仓库再写壳比从零写一版多得多，缺省 30 轮在读完仓库、写完四个文件、还没自述时就被掐；`reproduction` 给 80 轮 / 6 美元，执行层提示通用段加「读文件用 Read / Glob / Grep，Bash 只放行 ai4sci skill，cd / mkdir / awk 会被拒并白耗一轮」（#122）。
- 页面「设置 → 算力」：一张表（名字、种类、GPU、状态、上次探测）+ 添加表单，字段同 `compute add`——settings 系统的第一项，等 ssh 适配器跑通 PINNs 之后做。

```
class Compute(Protocol):
    def put(self, local_dir, remote_dir) -> None          # 快照过去
    def submit(self, remote_dir, cmd, timeout_s) -> Job   # 起任务，立刻返回句柄
    def wait(self, job, timeout_s) -> ExitStatus          # 等结束，超时就 cancel
    def cancel(self, job) -> None                         # 杀干净
    def get(self, remote_dir, local_dir) -> None          # 产物回来

local:  put=cp        submit=Popen 新进程组   cancel=killpg      get=cp
ssh:    put=rsync     submit=ssh nohup+pid    cancel=ssh kill    get=rsync
slurm:  put=rsync     submit=sbatch           cancel=scancel     get=rsync
```

- **submit / wait 而不是阻塞的 run**：句柄落盘到 `run_N/job.json`，`loop resume` 重启后能重新接上还在远端跑的任务或 reap 已死的任务，这是 A-5 续跑的前提。阻塞改异步是最疼的方向，反过来不疼。
- **选择靠名字**：`--compute <名字>` 或文件里的缺省，名字对不上就报错退出；要的算力不可用（连不上、venv 建不出）绝不静默退回本地（P-7，AutoResearchClaw 的 docker 反例）。
- **ssh 适配器**（[#118](https://github.com/zephyr4123/TJU-AI4Science/issues/118)）：`put` = rsync 任务目录到 `<root>/<产出 id>/`；`submit` = `ssh … nohup setsid launcher.sh` 拿远端 pid / pgid 写 `Job`（句柄落盘，续跑接得回）；`wait` 轮询；`cancel` = 远端 `kill -- -pgid`；`get` = rsync 产物回来。远端 venv 按 `env/` 用远端 uv 建，建不出就 EnvBuildError。冒烟测试 `AI4SCI_LIVE=1` 连真机器，CI 不跑。
- 0.2.0 只有 `local`；ssh 是第一轮真任务（PINNs 纯 CPU 一次训练 8.5 分钟、基线 2–3 小时）逼出来的第二个实现，主人租了 AutoDL。
- 不做：抽象基类加模板方法、装饰器注册表、工厂套工厂。一个后端一个文件，60 到 80 行，与 `backends/` 同一标准。

### 设置与自检

底座照算力办（P-25，[#130](https://github.com/zephyr4123/TJU-AI4Science/issues/130)）。按人的 `~/.config/ai4sci/` 下两个文件并列，各自一个读取点：

```
computes.yaml   我有哪几台机器          framework/computes.py（P-23）
agents.yaml     我用哪家 coding agent   framework/agents.py
  chat: claude_code        # 助理用哪家
  executor: codex          # 执行层用哪家
  agents:
    claude_code: {model: sonnet, effort: medium, last_check: {...}}
    codex:       {model: gpt-5.3-codex, effort: medium, last_check: {...}}
```

- **人的选择只有这几样**：两层各用哪家、每家新对话用的模型与思考深度。值必须在那家 `knobs()` 的清单上（`Knobs.check`），不在就报错，不静默回落；一律具体值，没有「跟缺省」。文件里没有的家（`_BACKENDS` 没这一行）读到就报错。
- **三层就近生效**：这一轮实际用什么 = 这段对话 meta 里记的（旋钮改的）← 开新对话时从 `agents.yaml` 抄进去 ← 冷启动时清单第一项。改设置只影响之后开的对话。执行层：`agents.yaml` 的缺省 ← `ai4sci cap --backend / --model` 覆盖，记进产出 `meta.yaml`。
- **`probe()`**：端口第三个方法，每家适配器实现，返回 `Probe{installed, version, min_version_ok, logged_in, spoke: {duration_s, cost_usd}, notes[]}`；`agent check` 把它写进 `last_check`，页面与 `agent list` 读文件不再连。说一句话那步走与真跑一样的隔离参数。
- **`ai4sci check`**：三项同一种形状「探测 → 报告 → 写 `last_check`」，一项不过退出码非零；`GET /health` 带一位「有没有没过的自检项」给页面亮点用。
- **端点**：`GET /settings`（三段事实 + 人的选择）、`POST /settings/agents`（改用哪家与缺省，过 `Knobs.check`）、`POST /settings/check`（全盘或单项）、算力的增删走现有 `compute` 函数。页面「设置」是这些端点的客户端。
- **环境变量**：`AI4SCI_COORDINATOR_MODEL` `_EFFORT`、`AI4SCI_EXECUTOR_MODEL` 退役；留下的只有位置（`AI4SCI_HOME`、各 `_ROOT`、`AI4SCI_COMPUTES` / `AI4SCI_AGENTS` 指向别处给测试用）与能力级的轮数 / 预算 / 超时。

### 执行层适配

一个 `Runner` 协议，每个 CLI 一个适配器。形状由 R-1 spike 实测定案（[#20](https://github.com/zephyr4123/TJU-AI4Science/issues/20)，代码 `backends/`）：

```
run(prompt, cwd, timeout_s, allowed_paths, bash_rules=())
  -> RunResult{exit_code, events[], changed_files[], cost_usd, duration_s, timed_out, stdout_tail}
```

- **非交互 + 结构化输出**：Claude Code 走 `claude -p ... --output-format stream-json --verbose`，Codex 走 `codex exec --json`（[#131](https://github.com/zephyr4123/TJU-AI4Science/issues/131)，flag 与事件按官方文档对账、本机 spike 实测后回写到这里）。
- **隔离**（P-11）：`--setting-sources ""` 是承重位，不带它项目 CLAUDE.md 会原样进上下文、plugin / hook / 自定义 agent 全加载；再加 `--strict-mcp-config`（MCP 清零）与 `--disable-slash-commands`（skill 清零）。`--bare` 看似等价但会跳过 keychain 读取导致未登录，不能用。隔离后一句 pong 从 $0.46 降到 $0.05。
- **权限**：`--permission-mode dontAsk` + `--allowedTools` 白名单，只放行 `allowed_paths` 内的 Edit / Write；绝对路径规则必须写 `//`（单个 `/` 被当作项目根相对路径，会把该放行的也拒掉）。dontAsk 下只读 Bash 自动放行、写操作 Bash 被拒；Bash 规则由框架按会话给，执行层只有 `Bash(ai4sci skill *)`（P-22）。不用 `--dangerously-skip-permissions` / `bypassPermissions`。这是第一道门，真正的门仍是 runner 事后拿 `changed_files` 判：`code/` 之外有改动就判 crash 回滚（P-7）。
- **联网只用 CLI 自带的工具**（主人 2026-09-20，[#114](https://github.com/zephyr4123/TJU-AI4Science/issues/114)）：两层适配器都必须放行这家 CLI 自带的联网搜索与网页读取工具（Claude Code 是 `WebSearch` / `WebFetch`）。实测 dontAsk 下不在白名单就被拒，拒绝信息还教 agent「用别的工具试」，它于是在 Bash 里拿 curl 硬凑，效果差；放行后一轮里搜索 + 读页都通。prompt 那一侧：研究助理的前言与指南、执行层 prompt 的通用段写了什么时候查（研究者给链接、论文有没有公开代码与数据、API / 报错拿不准、近期事实）、只用自带工具、查到的带来源链接。执行层子进程的环境与协调层同一份（`build_env`：venv 的 bin 进 PATH、关后台、Bash 超时对齐本轮）——执行层要跑 `ai4sci skill`，skill 脚本可能跑几分钟。
- **changed_files 不采信 CLI 自报**：调用前后对 cwd 做 sha256 快照 diff。事件流里的 `file_path` 实测与 diff 一致，但 Bash 改文件不产生 `file_path`，改完再改回去也看不出来。
- **超时**：`kill_tree` 逐进程组杀。CLI 的 Bash 工具把 shell 起在自己的新进程组里，只 `killpg` CLI 那一组会留下 PPID=1 的孤儿；先趟进程树再叶子组先杀。
- **成本**：只认最终 `result` 事件的 `total_cost_usd` 与 `duration_ms`；超时被杀时 result 不会发出，成本填 NaN 表示未知，绝不填 0。
- **事件流落盘**：完整 stream-json 与 stderr 写 `cwd/.ai4sci/executor-<ts>.jsonl|.stderr.log`，给执行层的只有摘要（P-9）。stdin 给 DEVNULL（否则 CLI 等 3 秒），stdout 与 stderr 各一个线程排空。
- 配置从环境变量读：`AI4SCI_EXECUTOR_MAX_TURNS`（30）、`AI4SCI_EXECUTOR_MAX_BUDGET_USD`（2.0）、模型从 `agents.yaml` 读（P-25，`AI4SCI_EXECUTOR_MODEL` 退役）、`AI4SCI_EXECUTOR_TIMEOUT_S`（内环里执行层单次调用的墙钟上限，缺省 900）、`AI4SCI_RUNS_ROOT`（runs 根目录，缺省仓根 `runs/`）。用哪家、哪个模型由 `agents.yaml` 定、调用时可覆盖、记进产出 meta（P-25）。
- 任何适配器合入必须带一个真实调用点和一个真 CLI 的冒烟测试（P-8）；冒烟测试 `AI4SCI_LIVE=1` 才跑，CI 不跑。

### 协调层适配

同一批 CLI 的第二种用法：多轮、按 session id 续接、事件边跑边出。端口 `Chat` 与 `Runner` 放同一个 `backends/__init__.py`，适配器放同一个文件（一个 CLI 一个文件）；换一家 CLI 就是加一个文件，自研 agent 就是第三个适配器（主人红线：涉及 agent 的一律可替换，[#51](https://github.com/zephyr4123/TJU-AI4Science/issues/51)）：

```
turn(message, cwd, timeout_s, *, session_id, system_prompt, allowed_paths, readable_paths, bash_rules, tuning, chat_id)
  -> Iterator[ChatEvent{kind: init|delta|text|tool_use|tool_result|denied|done|error, text, tool, tool_input, session_id, cost_usd, duration_s, raw}]
knobs() -> 这家 CLI 有哪些模型、哪几档思考深度、不选时用什么
```

- **续接**：Claude Code 走 `claude -p <message> --resume <session id> --append-system-prompt <指南>`；隔离位与执行层同一组，但**不带** `--no-session-persistence`，多轮靠的就是 CLI 自己的会话持久化。
- **指南注入**：服务会话隔离了所有设置源，两份指南（`coordinator/README.md` 研究助理、`coordinator/studio.md` 流程助理）由 `framework/chat/guide.py` 连同一段"你在服务里"的前言按域塞进 system prompt（命令写裸 `ai4sci`、一条一行、不加路径不挂前缀不接管道、没有对应命令就停下来说缺什么、需求确认与签字不由你做、先说结论用人话）。研究助理的指南分两段：需求未确认——只问、只写 `requirement.md`（先 `show templates` 看有哪些模板）、不跑任何阶段；已确认——取流程、跑阶段、断点处等人。指南本身受 lint：代码块里每条命令以 `ai4sci ` 开头（P-14）；研究助理的指南里没有 `workflows/` 的写法（P-16）。
- **权限**：Bash 白名单是 `Bash(ai4sci *)`（带 `.venv/bin/` 路径的老写法也放行，前期别设坎；裸 `ai4sci` 找得到是因为适配器把本 venv 的 bin **追加**到 PATH 末尾），配置一律走起服务的人的环境变量，命令上不带。研究助理可写当前工作区（需求、原件、流程实例、七个阶段目录），库 `workflows/` 与 `templates/` 可读不可写（端口 `readable_paths`，适配器走 `--add-dir`；前言把库的实路径写给它）；流程助理只可写 `workflows/`。两组可写目录不相交，分权靠目录不靠指南里的一句「请不要」。
- **长命令不进后台**：`claude -p` 里 Bash 超过 CLI 缺省的 2 分钟会被自动挪到后台、一轮结束就被杀。适配器起会话时设 `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` 关掉全部后台机制，并把 Bash 超时抬到与本轮超时一致；指南写明前台等、跑不完分批；真长的活走 `--detach` 作业。
- **逐字流出**：端口的 `delta` 事件（刚到的几个字，不是累计；同一段说完仍有完整 `text`），契约写明每家适配器都必须逐字吐。Claude Code 适配器开 `--include-partial-messages` 只翻 `text_delta`；对话层往外吐但 events.jsonl 只留完整事件。
- **落盘**：会话内容存在 CLI 自己的目录里，我们只记 session id；但每一轮的原生事件流自己留一份在 `.ai4sci/chats/<id>/turn-N/events.jsonl`（编辑台在 `studio/chats/`），它是"agent 那一轮到底做了什么"的唯一证据（P-3）。meta 记后端、session id、cwd、完成的轮数、累计花费、记着的旋钮；transcript 给人翻；忙锁 `inflight.json` 让同一段对话同一时刻只跑一轮；一轮有 `origin`：人，或框架来叫醒（作业跑完）。
- **两张脸同一套函数**：`ai4sci chat new|send|list [--studio]` 在终端里聊，`ai4sci serve` 起标准库 HTTP + SSE 给页面。端点按域分前缀：`GET/POST /workspaces`、`GET /workspaces/<id>`（需求状态、每个阶段的产出、每条流程走到哪、在等谁）、`GET /workspaces/<id>/requirement`、`POST …/requirement/confirm`、`GET …/outputs/<stage>/<n>`、`POST …/outputs/<stage>/<n>/sign`、`GET …/flows`、`GET …/jobs[/<jid>]`；对话四个端点在 `/workspaces/<id>/chats…` 与 `/studio/chats…` 两个前缀下共用一套实现；库：`GET /stages` `GET /cap` `GET /workflows` `POST /workflows` `POST /workflows/check` `GET /templates[/<name>]` `GET /backends`；`GET /health`。清单在 `framework/chat/server.py` 文件头，看板读盘在 `boards.py`，全是纯函数，NaN 出门前换 None。
- **产出记对话号**：能力开工时把 `AI4SCI_CHAT_ID` 记进产出的 `meta.yaml`（终端里开的是空）。对话不绑流程：流程走到哪写在盘上，谁驱动的都一样；页面只拿它判断「当前对话最近碰的是哪条」。
- **两个旋钮**：`knobs()` 由适配器自报（页面照单渲染，不写死哪家有什么），每轮的 `tuning`（模型 + 思考深度）翻成 Claude Code 的 `--model` / `--effort`。旋钮上只有具体值：开新对话时把 `agents.yaml` 里这家的缺省抄进对话 meta，之后每轮沿用、改了记进去；meta 里没有 `null`（P-25，老对话一次性填成当时的缺省）。「哪家」只在开新对话那一屏选，缺省照设置；旋钮清单拿这段对话那家的，不是缺省那家的。
- 配置：哪家、模型、深度从 `agents.yaml` 读（P-25）；环境变量只剩 `AI4SCI_COORDINATOR_MAX_TURNS`（50）、`_MAX_BUDGET_USD`（每轮 2.0）、`_TIMEOUT_S`（900：它会调用命令等基线跑完）。
- 不做：多用户、鉴权（本机单人服务）。协调 agent 从终端里技术上也能 `requirement confirm` 与 `sign`，只有页面上那两处能做到"只有人能确认"；指南写明它不替人做。

### 界面适配

界面也是适配器（主人 2026-09-16：现在是 GUI，之后有 TUI，要留位置，[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)）。一种界面一个目录 `ui/<kind>/`，全部是上面那套端点的客户端，互相不认识、也不认识框架内部；换一种界面后端一行不改。契约就是端点清单（`framework/chat/server.py` 文件头）+ 响应体（`boards.py`），网页的 `ui/web/src/api/client.ts` 是它的照抄，写 TUI 时照抄一份即可。

- **词表**（P-21，[#112](https://github.com/zephyr4123/TJU-AI4Science/issues/112)）：页面、文档、指南一个概念一个词，没进词表的词不上屏；量词用「个 / 次 / 项」。

  | 词 | 指的是 | 不这么叫 |
  |---|---|---|
  | 工作区 | 一份需求的目录 `workspaces/<id>/` | 项目、任务、房间 |
  | 需求 | `requirement.md` 与它的确认 `requirement.lock` | 提纲、任务书 |
  | 阶段 | 七个研究阶段之一：文献、假设、设计、实验、分析、写作、验证 | 步骤、环节 |
  | 能力 | 一个阶段里的一件活，`ai4sci cap <name>` 一条命令 | 按钮、键、能力单元、工具 |
  | 流程 | `workflows/<name>.yaml` 一份：经过哪些阶段、挂哪些能力、哪儿有断点 | 流、库、工作流、套餐 |
  | 流程库 | 全部流程文件 | 库 |
  | 断点 | 流程里停下来等人确认的一项 | 门、关卡、闸 |
  | 产出 | 一次能力调用留下的目录 `<stage>/<n>/`，页面写「设计 · 1」 | 结果、run、artifact |
  | 确认 | 人在需求或产出上签字（`requirement.lock` / `signed.json`） | 签、盖章、放行 |
  | 助理 | 对话里的协调 agent：研究助理（主页面）、流程助理（编辑台） | 协调层、agent、模型 |
  | 参数 | 能力描述符的 `params`，页面写它的 `label` | 选项、旋钮 |
  | 主页面 / 编辑台 | 两个看板：改工作区 / 改流程库 | 工作坊、拼流台 |
  | 看板 / 文件 | 主页面的两个镜头 | 视图、tab |
  | 流程 / 能力 | 编辑台的两个镜头 | — |
  | 职责 / 边界 / 输入 / 产出 / 终止条件 | 能力描述符的五栏 | 干什么 / 不干什么 / 要带什么进来 / 留下什么 / 什么时候停 |
  | 状态词 | 运行中、失败、待确认、已确认、完成 | 在跑、没成、签了 |
  | 按钮 | 保存、覆盖、排列、确认、打开对话、打开目录 | 整理、提交 |
  | 设置 | 按人的 `~/.config/ai4sci/` 两个文件加外观，页面上那块悬浮板 | 配置、偏好、系统 |
  | AI | 设置里「助理用哪家、执行层用哪家」那一段；每一家写产品名（Claude Code、Codex） | 底座、后端、backend、模型（那是旋钮） |

- **文案**（P-21）：标签、列名、状态、节点名是两到四字名词；动词只在按钮上；句子只进解释层（hover、空态、展开层），一句为限，工程语言不口语。机器的名字不上屏——流程文件名、能力名、产出 id、参数名、CLI 参数一律翻译，翻译在源头：后端随数据给中文（能力 `title` `brief`、参数 `label`、流程 `title`、阶段名、阶段主文件的中文名），前端不拼不猜；流程文件名照工作区 id 的规矩由标题生成、不显示不让填；唯一例外是文件镜头，路径在那里是内容。能力三层对三种动作：名直接显示、一行 hover、详情点击跳转，一个阶段挂再多能力也只是名字的清单；执行者种类不上屏。机器判据：描述符 `label` / `brief` 由 `discover()` 断言；页面一条测试扫中文串、命中禁用词即失败，`font-mono` 只在文件镜头与代码块；给页面的 JSON 里凡 id / name / slug 必伴随中文字段。
- **网页 `ui/web/`**：React 19 + Tailwind v4 + shadcn + React Bits 改装件（从 registry 捞来改，不手搓）+ React Flow，Vite 构建成静态文件，`ai4sci serve` 缺省端 `ui/web/dist`。视觉系统在内仓 `docs/DESIGN.md`：纸 / 墨 / 靛 / 铜绿 / 琥珀五色都是信息，思源宋体只给结论与标题，IBM Plex 正文；配图一律风景、走自己的 CDN（P-17，`assets.ts` 一处）；图标全站一套 Phosphor 内联；文案照上面的词表与三层规矩；输入框不画下划线。
- **地方栏**：最左一条，先选世界再选世界里的东西——底下「工作区 / 编辑台」双向开关，上面工作区世界里列封面块与「新建」，编辑台世界里工作区块收掉；页眉只属于当前地方。对话列表是抽屉，入口带字。
- **门口那一屏**：一句话起工作区——写课题、选学科（需求提纲按学科起草）、回车即建；文件夹名从标题推、是内部 id 不显示也不让人填（[#109](https://github.com/zephyr4123/TJU-AI4Science/issues/109)），封面随名字换；进主页面时需求还没确认。
- **主页面**按 `requirement.lock` 在不在分两个状态。未确认——需求文档就是页面：助理按模板起草的 `requirement.md` 渲染成看板（文档里实际有的二级标题各一格，模板留的「待填」是空格子），右边对话，一个动作「确认需求」；页面只渲染不编辑，改需求只走对话（一个文件一个生产者，diff 才有意义）。已确认——需求收成顶部一条（版本、时间、点开侧滑看全文；助理又改了就显示 diff 与「确认下一版」），下面**一条流程一张表**：横向是流程经过的阶段（有什么阶段就几列，列头阶段名 + 能力），纵向是每一列跑过的每一次产出（编号 + 一个词），断点是两列之间一道线，右上角一句话说在等谁；产出点开侧滑看记录、文件、确认（[#107](https://github.com/zephyr4123/TJU-AI4Science/issues/107)）。主页面还有第二个**镜头**——页眉「看板 / 文件」切换，对话列两边都在（[#111](https://github.com/zephyr4123/TJU-AI4Science/issues/111)，主人：每个工作区要能看见盘上实际的目录，之后单独 Git 管理）：不是地方栏上第三个地方（地方栏按数据边界分），是同一个工作区的另一个镜头——看板答「做到哪了、在等谁」，文件答「盘上到底有什么」。左边一棵带平台语义的目录树（阶段目录写阶段名 + 图标、产出那一层编号 + 状态词 + 冻结锁、`.ai4sci/` 灰显、懒加载），右边按种类渲染；只看不改，改动走对话（手改会撞冻结）；Git 状态先不画。对话：研究者的话进气泡，助理逐字流出的 Markdown，工具调用一行一条原样显示（不折叠、不翻译、刷新后不消失）；输入框上两枚下拉片换模型与思考深度。
- **编辑台**：两个镜头，页眉「流程 / 能力」切换（[#112](https://github.com/zephyr4123/TJU-AI4Science/issues/112)）。流程：React Flow 节点画布，线性链，节点 = 研究阶段（能力小片 + 参数在节点里）或断点，画布铺满、左上角阶段梯 + 玻璃题头（标题与说明；文件名由标题生成，不显示不让填）、右上角流程库与保存、选中节点配置参数（勾选、名字、参数的 `label`；`Param.in_flow` 分开每次调用才定的参数）、问题贴节点；节点可自由摆、坐标进文件的 `layout` 块、「排列」回自动排。能力：七个阶段各一列名字（空的写「暂无」），hover 一行，点了原地切详情页（一行、参数、五栏；产出栏先列本阶段主文件），节点小片与配置板里的名字跳同一页。流程助理是右下角的悬浮对话窗，默认开着。
- **门禁**：`make ui-check`（tsc + oxlint + vitest + 构建）并入 `make check` 与 CI；依赖只进 `ui/web/node_modules`；`git ls-files ui/` 里没有二进制。浏览器闭环用 playwright 取证。
- **设置**（P-25，[#134](https://github.com/zephyr4123/TJU-AI4Science/issues/134)）：入口在地方栏的脚（带字「设置」，旁一个点，有自检项没过才亮；窄屏在地方清单底部），页眉不再放主题开关。点开是压在当前地方上的一块悬浮板（底图照旧铺满、四周留边、圆角、投影），左索引右滚动四段：AI（段首「对话用 / 执行用」两个下拉；每家一块：名字 + 版本、机器说的一句话状态、模型 / 深度下拉、「检查」）、算力（一张表 + 贴一行 ssh、密钥从 `~/.ssh` 里挑、「添加」）、存放（数据根与设置目录在哪，只看）、外观（浅 / 深 / 跟随系统）。状态是一句话不是徽章；没有序号、没有全大写小标题、段与段之间不画框。Claude 与 OpenAI 用品牌图标（simple-icons，内联 SVG），其余仍是 Phosphor。开新对话那一屏加第三枚旋钮「哪家」。
- **`ui/tui/`**：留位置没建。

## 变更记录

| 日期 | 改了什么 | 为什么 | 认可 |
|---|---|---|---|
| 2026-09-22 | §5 加「设置与自检」（`agents.yaml`、三层就近生效、`probe()`、`ai4sci check`、端点、环境变量退役）；命令行加 `agent` `check`；执行层 / 协调层适配的模型配置改读文件、旋钮删「默认」；界面适配加「设置」悬浮板与词表两行（P-25，[#130](https://github.com/zephyr4123/TJU-AI4Science/issues/130)） | 全面适配 Codex 要先有「用哪家」的家；冷启动自检与设置页一并定 | 主人 + Claude |
| 2026-09-20 | §1 加「skill」一节：与能力 / 领域包的关系表、agentskills.io 格式与 frontmatter、脚本规矩（PEP 723 + uv 锁 + `--locked --offline`）、不建工作区级 venv、承接与门禁、清单注入、三个子命令、第一个 skill `pdf` 的契约；§5 命令行加 `skill`（[#113](https://github.com/zephyr4123/TJU-AI4Science/issues/113)） | 主人要通用的 skill 系统与解析论文 PDF 的第一个 skill；调研后定不做工作区级 venv、先简单后端再 MinerU 实测 | 主人 + Claude |
| 2026-09-20 | §1「skill」按落地回写：`run` 加 `--script`、执行层白名单 `ai4sci skill *`、领域 skill 不再全文注入也不随实验快照、两家 pdf 后端的实测与缺省；§5 执行层适配 `run()` 加 `bash_rules`、加「联网只用 CLI 自带的工具」一条（[#113](https://github.com/zephyr4123/TJU-AI4Science/issues/113) [#114](https://github.com/zephyr4123/TJU-AI4Science/issues/114)） | 落地时的实测与取舍 | 主人 + Claude |
| 2026-09-20 | §5 命令行加 `job stop`、`env resolve`，记第一轮真任务（PINNs）逼出的三条：停作业、按包名算环境清单 + 建完查完整 + `--continue` 遇环境变了拒、设计草稿先 `ruff --fix-only` 修 import 顺序（[#115](https://github.com/zephyr4123/TJU-AI4Science/issues/115) [#116](https://github.com/zephyr4123/TJU-AI4Science/issues/116) [#117](https://github.com/zephyr4123/TJU-AI4Science/issues/117)） | Claude 扮小白研究者跑第一轮闭环，助理与执行层行为都对，坑全在平台 | 主人 + Claude |
| 2026-09-20 | §5 算力适配按 P-23 重写：按人的 computes.yaml、只有 SSH 只认密钥、对话里接机器、按名字选记进 meta、ssh 适配器的五个动作；命令行加 `compute add / check / list / remove`、`env resolve --compute`；磁盘布局 meta 加 `compute`（[#119](https://github.com/zephyr4123/TJU-AI4Science/issues/119)） | 算力由使用者自己配，AutoDL 到位 | 主人 + Claude |
| 2026-09-20 | §5 算力适配加「接上先盘点、再问两问」与 `env use`；远端 uv 用镜像当额外索引、长命令走 nohup + 轮询（[#118](https://github.com/zephyr4123/TJU-AI4Science/issues/118)） | 演练实测：AutoDL 直连 pypi.org 19 KB/s、长连接被掐、一律隔离新建让非工程师干等 | 主人 + Claude |
| 2026-09-21 | §1 流程加出厂第二条 `reproduce`；磁盘布局记文献格主文件 `sources.md` 由助理手写；§5 命令行能力加 `reproduction` `reproducibility`、skill 加 `download`（[#120](https://github.com/zephyr4123/TJU-AI4Science/issues/120)） | P-24 论文复现另起一条流程 | 主人 + Claude |
| 2026-09-21 | §5 命令行加 `env add`；算力适配加「现成环境缺包就补」「执行层会话额度按能力给」（[#120](https://github.com/zephyr4123/TJU-AI4Science/issues/120) #122） | 第二轮演练（GUA）实测：镜像环境缺 scipy、执行层 30 轮不够读仓库 | 主人 + Claude |
| 2026-09-10 | 建档。阶段骨架、实验内环四角色、账本、裁判、人在环、Runner 协议 | 三个仓深读的收敛结论；棘轮来自 autoresearch，harness 注入来自 AutoResearchClaw，目录形态来自 InternAgent | 主人 + Claude |
| 2026-09-15 | 第 1 节标实验 / 分析 / 验证已落地，能力描述符改为已落地的形状；第 3 节加"数字回溯（已落地）"：分析三节与数据表、验证四项检查、1% 容差、已知边界、report.json、重跑轮转；第 5 节 CLI 加 `cap list` / `cap <name>`（[#35](https://github.com/zephyr4123/TJU-AI4Science/issues/35) [#36](https://github.com/zephyr4123/TJU-AI4Science/issues/36) [#37](https://github.com/zephyr4123/TJU-AI4Science/issues/37)） | 09-22 单元的分析与验证做完，纲领不能描述另一套行为 | 主人 + Claude |
| 2026-09-15 | 第 1 节加"装配与固定流程"（子集也是流程、入口契约由人填、固定流程是存好的图、产物跨流程复用），契约加"能力描述符"；第 5 节注明 CLI 是薄壳、能力对外是 Python 函数（[#33](https://github.com/zephyr4123/TJU-AI4Science/issues/33)） | 主人对齐高度模块化：不同任务用不同子集流程，低代码图是第二种协调层 | 主人 + Claude |
| 2026-09-10 | 第 1 节加七个能力的输入 / 输出 / 执行者 / 判据表，标出项目级与 run 级（[#29](https://github.com/zephyr4123/TJU-AI4Science/issues/29)） | 端到端对齐，实体分两级 | 主人 + Claude |
| 2026-09-10 | 第 2 节加轮间记忆（实验笔记）与续命，P-9 措辞随纲领 README 改；磁盘布局加 notebook.md；第 5 节加 run extend（[#28](https://github.com/zephyr4123/TJU-AI4Science/issues/28) [#26](https://github.com/zephyr4123/TJU-AI4Science/issues/26)） | 真跑暴露执行层失忆，主人拍板必须有轮间记忆 | 主人 + Claude |
| 2026-09-10 | 第 1、2 节按 R-4 内环实现回写：runner 提交、work/ 独立 git 仓、失败分类改成带优先级的六类 + noop / interrupted、账本加 cost_usd 与 executor_s 且基线不占行、统计门加 min_delta 与 σ=0 fail-closed、停止条件与续跑规则、磁盘布局加 work/ prompts/ inflight.json stop.json；第 5 节环境变量清单补两项（[#24](https://github.com/zephyr4123/TJU-AI4Science/issues/24)） | 实现与审查暴露的偏差回写，纲领不能描述另一套行为 | 主人 + Claude |
| 2026-09-10 | 第 5 节执行层适配按 R-1 spike 实测改写：隔离位、`//` 路径规则、kill_tree、快照 diff、成本 NaN、落盘（[#20](https://github.com/zephyr4123/TJU-AI4Science/issues/20)） | 四个未知全部拿到证据 | 主人 + Claude |
| 2026-09-10 | 第 5 节加算力适配：`Compute` 端口五个动作，submit / wait 句柄落盘，靠名字选择、不静默回退 | 主人问算力模块用什么模式；harness 在哪跑与 agent 在哪跑是两根正交的轴，各自端口 + 适配器 | 主人 + Claude |
| 2026-09-10 | "阶段"改"能力"，去掉框架内的顺序与回退判断，串联归协调层；磁盘布局按能力名而非序号，加 `journal.md`；第 4 节人在环改写为协调层行为，去掉 full-auto / gate-only 与文件通道；第 5 节加协调层驱动面 `ai4sci` 子命令；"底座"改称"执行层"（[#18](https://github.com/zephyr4123/TJU-AI4Science/issues/18)） | 固定顺序的阶段骨架就是"外层 for + 硬编码状态"；科研判断归协调层（人 + agent），框架不等人、不连跑 | 主人 + Claude |
| 2026-09-16 | §5 加「协调层适配」：`Chat` 端口、Claude Code 续接、指南注入、对话落盘、`ai4sci chat` / `serve`（[#51](https://github.com/zephyr4123/TJU-AI4Science/issues/51)） | 产品形态定为两个看板一次验收，网页要能起协调 agent；主人拍板走 CLI 子进程 + 续接、藏在端口后面可替换 | 主人 + Claude |
| 2026-09-16 | §5 协调层适配的端点清单补看板与两个键；加「界面适配」：`ui/<kind>/` 一种界面一个目录、全是端点的客户端，网页第一版、验收记录 `accept.json`、门禁与浏览器闭环（[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)） | MVP 第 5 件页面；主人红线：UI 也是适配器，GUI 之后有 TUI 要留位置 | 主人 + Claude |
| 2026-09-16 | 「套餐」改叫流程并落成文件 `workflows/*.yaml`（`intake` 接一个新课题、`auto-research` 自动做实验；步骤是能力、键或纯人的事，`assumes` 声明前提），`run new` 升成第 6 个能力 `start`（`contracts.flow` 的桥改认它）；页面的进度页（写死五步）换成流程页（[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)） | 主人指出页面把两条固定流程拼起来当成了平台：平台是能力清单，流程只是预装的拼法；每样东西要么是能力、要么是键、要么是查询 | 主人 + Claude |
| 2026-09-17 | §1 描述符加阶段（`stage`，七个科研阶段，能力上面的一层标签）与人话字段（`title` / `what`）；流程的覆盖范围与能力的「用在哪条流程」都是算出来的，不存（[#53](https://github.com/zephyr4123/TJU-AI4Science/issues/53)） | 主人提出能力归科研模块、模块拼流程；对齐后「模块」改叫阶段，反向归属不存 | 主人 + Claude |
| 2026-09-17 | §1 契约段加「接口是文件名不是 schema」：种子清单、`checkpoint.json` 归 run 种子、两处不齐的名字与原因、写作能力的例子（[#54](https://github.com/zephyr4123/TJU-AI4Science/issues/54)） | 文档即接口升成 P-13，落地两条加载时断言 | 主人 + Claude |
| 2026-09-17 | §5 协调层适配：可写目录加 `workflows/`，长按钮不进后台（`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` + Bash 超时对齐本轮超时）（[#56](https://github.com/zephyr4123/TJU-AI4Science/issues/56) [#57](https://github.com/zephyr4123/TJU-AI4Science/issues/57)） | 实验 #55 暴露的两处缺口：拼得出存不下、长按钮被挪到后台杀掉 | 主人 + Claude |
| 2026-09-17 | §1 拟定步骤 `with:` 参数与 run 记流程 / 步序 / 快照；§5 界面适配加下一版形态：两块看板以可写目录划界、主页面右侧随流程生成（[#58](https://github.com/zephyr4123/TJU-AI4Science/issues/58)） | 主人拍板：页面不是固定流程，装什么流程长什么样；需求对齐在主页面 | 主人 + Claude |
| 2026-09-18 | §1 装配加「流程分三层：库、实例、快照」；§5 命令行改成工作区口径（task 级不带路径、`flow take`、`workspace new`、`show workspaces` / `show flows`）、协调层适配加「两位助理、两个域」与分域端点、界面适配第四版（[#70](https://github.com/zephyr4123/TJU-AI4Science/issues/70) [#72](https://github.com/zephyr4123/TJU-AI4Science/issues/72) [#73](https://github.com/zephyr4123/TJU-AI4Science/issues/73) [#74](https://github.com/zephyr4123/TJU-AI4Science/issues/74)） | 主人拍板工作区即边界、造流程与用流程分权（P-15 P-16） | 主人 + Claude |
| 2026-09-18 | §5 界面适配加「素材」：CDN URL、本机中转、视频只做门口背景、图标一套、输入框即门（[#75](https://github.com/zephyr4123/TJU-AI4Science/issues/75) [#76](https://github.com/zephyr4123/TJU-AI4Science/issues/76)） | 主人定「除了 icon 用 SVG 内联，其他都上 CDN URL，不能放仓库」；motionsites 的 MP4 在境外源站，直接引加载不出来 | 主人 + Claude |
| 2026-09-18 | §5 界面适配加「第五版」：地方栏、页眉归属、对话入口、门口那一屏（[#79](https://github.com/zephyr4123/TJU-AI4Science/issues/79) [#81](https://github.com/zephyr4123/TJU-AI4Science/issues/81)） | 主人指出编辑台不受工作区影响却和切换混在一行、对话入口谁都看不到、新建那屏像表单；对齐后拍板方案 A | 主人 + Claude |
| 2026-09-18 | §5 协调层适配加「run 记对话号」；界面适配加「第六版」：泳道、默认收起、承接的那条展开、风景背景（[#82](https://github.com/zephyr4123/TJU-AI4Science/issues/82) [#85](https://github.com/zephyr4123/TJU-AI4Science/issues/85)） | 主人问「右边这条流程什么情况下渲染」：助理一段对话可同时开几条流程，原来只显示最近一条；对齐后定对话不绑流程、看板归工作区 | 主人 + Claude |
| 2026-09-18 | §5 协调层适配加「两个旋钮」；界面适配加「旋钮」：模型与思考深度在输入框上随时换（[#86](https://github.com/zephyr4123/TJU-AI4Science/issues/86) [#87](https://github.com/zephyr4123/TJU-AI4Science/issues/87) [#88](https://github.com/zephyr4123/TJU-AI4Science/issues/88)） | 主人要求每家底座 CLI 都能换模型、换思考深度，适配器先暴露这一层，再同步输入框 UI | 主人 + Claude |
| 2026-09-18 | §1 重写成「三层：阶段、能力、实现」：七个阶段任意组合、能力五栏必填、实现是能力下一层、阶段之间不做数据流校验、流程是 stages + 断点、出厂只留 `research`、文件退出拼流程接口；§5 命令行按五个能力改、界面适配加第七版（[#93](https://github.com/zephyr4123/TJU-AI4Science/issues/93) [#94](https://github.com/zephyr4123/TJU-AI4Science/issues/94)–[#99](https://github.com/zephyr4123/TJU-AI4Science/issues/99)） | 主人：按吃吐路径对表的检查器让七个能力只能拼成一条线，工作坊搓不出东西；第一性原理：编排工作台是立规矩不是接管子；文档用直白的工程语言 | 主人 + Claude |
| 2026-09-19 | §1 磁盘布局与契约重定：一个阶段一个目录、每次产出一个子目录、`from` 引用、需求是根且是唯一内置的门、断点开放、框架只认 meta / signed / lock；能力改成纯函数（`--from`）；`init` 删；§4 人只做两件事；§5 界面第九版（[#104](https://github.com/zephyr4123/TJU-AI4Science/issues/104)） | 主人：现有目录为 auto-research 量身定做、没法涵盖七个阶段；科研是频繁返修、多对多的；需求形式开放、断点不能卡太死；能力解耦不随最新状态变 | 主人 + Claude |
