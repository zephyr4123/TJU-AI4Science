# 未决项

- 最近变更：2026-09-20

纲领里还没定的事，一项一个编号。每项写清问题、候选方案与依据、建议、谁拍板。定了就把结论搬进对应文件，这里改成"已定，见 xxx"。每项一条 issue，见表末列。

| 编号 | 问题 | 层 | 建议 | 拍板 | issue |
|---|---|---|---|---|---|
| Q-1 | 首版提供哪几个能力 | 流水线 | 拟定 7 个，platform 0.2.0 只做设计、实验、分析、验证 4 个；顺序不由框架定 | 主人 | [#8](https://github.com/zephyr4123/TJU-AI4Science/issues/8) |
| Q-2 | 执行层 skill 怎么注入 | 学科适配 | 2026-09-20 关闭（P-22）：框架拼清单注入 + `ai4sci skill`；此前 2026-09-16 翻案：走 prompt 整文件追加（原方案 1 被隔离参数关掉了），不做关键词匹配 | 主人 | [#9](https://github.com/zephyr4123/TJU-AI4Science/issues/9) |
| Q-3 | 验收怎么定义 | 验证 | manifest.requirements 的 must_pass + 零 LLM 判据；discussion 类交隔离裁判 | 主人 | [#10](https://github.com/zephyr4123/TJU-AI4Science/issues/10) |
| Q-4 | 评测怎么做 | 评测 | rubric 树 + 组件消融 + 噪声基线；首个工科 bench 3 到 5 题 | 主人 | [#11](https://github.com/zephyr4123/TJU-AI4Science/issues/11) |
| Q-5 | 第一个真任务与学院 | 任务 | 玩具任务已跑通；2026-09-16 案例到，案例二选为第一个真任务包，学院是交叉领域 | 主人 | [#12](https://github.com/zephyr4123/TJU-AI4Science/issues/12) [#1](https://github.com/zephyr4123/TJU-AI4Science/issues/1) |
| Q-6 | 执行环境 | 执行层 / 工具 | 任务级 venv（uv 建，任务自带 env/），独立进程；2026-09-20 加：算力按人配（P-23，`~/.config/ai4sci/computes.yaml`，只有 SSH 只认密钥），远端只跑 harness；docker 与集群按需 | 主人 | [#13](https://github.com/zephyr4123/TJU-AI4Science/issues/13) |
| Q-7 | 无人值守时协调层怎么找人 | 协调层 | 大方向已定：人在协调层对话里，框架不等人；异步通道 0.2.0 不做 | 主人 | [#14](https://github.com/zephyr4123/TJU-AI4Science/issues/14) |
| Q-8 | 协调层与执行层各用哪个 CLI | 协调层 / 执行层 | 2026-09-22 关闭（P-25）：两层各选一家、可以不同，写在按人的 `agents.yaml`；Codex 先接执行层再接协调层 | 主人 | [#15](https://github.com/zephyr4123/TJU-AI4Science/issues/15) [#130](https://github.com/zephyr4123/TJU-AI4Science/issues/130) |
| Q-9 | 项目级记忆怎么做 | 协调层 | 改写：run 级已有（账本、笔记）；项目级（文献笔记、假设台账、跨 run 结论）是写作前提，0.2.0 之后第一优先 | 主人 | [#16](https://github.com/zephyr4123/TJU-AI4Science/issues/16) |
| Q-10 | 协调层 skill 包放哪、怎么注入 | 协调层 | 2026-09-20 关闭（P-22）：指南在 `coordinator/` 由框架注入，工具型 skill 用通用 `skills/`；不走原生机制 | 主人 | [#19](https://github.com/zephyr4123/TJU-AI4Science/issues/19) |
| Q-11 | 文献检索走 tools/ 学术 API 还是执行层联网 | 学科适配 / 验证 | tools/ 学术 API，引用才可验 | 主人 | [#31](https://github.com/zephyr4123/TJU-AI4Science/issues/31) |
| Q-12 | 写作能力的形态 | 流水线 | 分节多次调用，模板放领域包，图由 tools 出，写完过三条判据 | 主人 | [#32](https://github.com/zephyr4123/TJU-AI4Science/issues/32) |
| Q-13 | 低代码协调层的形状：图怎么描述、谁解释、与人 + agent 怎么混 | 协调层 | 图 = 能力描述符引用 + 边；确定性图运行器与"交给 agent"节点并存；描述符先于图 DSL | 主人 | [#34](https://github.com/zephyr4123/TJU-AI4Science/issues/34) |
| Q-14 | 加一个能力非得写代码吗（声明式能力：描述符 + 说明书） | 能力 | 两种并存 | 主人 | [#110](https://github.com/zephyr4123/TJU-AI4Science/issues/110) |
| Q-15 | 执行层的可写范围锁不锁在产出目录 | 能力 | 一律锁 | 主人 | [#110](https://github.com/zephyr4123/TJU-AI4Science/issues/110) |

## Q-1 首版提供哪几个能力

AutoResearchClaw 的 23 段太细（大量阶段是一次 LLM 调用），InternAgent 的 3 段太粗（想法生成一个阶段里塞了 9 个 agent）。拟定 7 个能力：文献、假设、设计、实验、分析、写作、验证。platform 0.2.0 只做设计、实验、分析、验证四个。加了协调层后这个问题只剩"提供哪几个"，不再有"按什么顺序"：顺序、回退、跳过都是协调层的决定（P-10）。

> 2026-09-17 补记：这七个落地时成了七个**阶段**，不是七个能力——设计拆成 design + baseline，实验拆成 start + experiment，一个阶段下挂几个能力。阶段是描述符上的字段 `stage`，`ai4sci show caps` 按它列清单，文献、假设、写作三格标空（[#53](https://github.com/zephyr4123/TJU-AI4Science/issues/53)）。

## Q-2 执行层 skill 怎么注入

候选：
1. **交给执行层 CLI 原生机制**。领域包的 `skills/` 目录与 Claude Code 原生 SKILL.md 同格式，起执行层会话时把它挂进会话的 skill 搜索路径，由执行层自己按需加载。零框架代码。
2. **框架按能力选 skill 塞进 prompt**。AutoResearchClaw 走的是这条，它的匹配器因为分词 bug 在主路径上什么都匹配不到，真正生效的是无差别灌前 5 条。

建议 1。依据：[AutoResearchClaw 深读 §6.2](../../research/selection/2026-0909-pipeline-frameworks/autoresearchclaw.md#62-自进化在默认配置下不存在)。风险：换一个不支持 skill 的执行层时这层失效，届时再做方案 2 的最简版（按 `applicable-capabilities` 字段整文件追加，不做关键词匹配）。无论哪种，搜索路径里都不能有 `coordinator/`（P-11）。

**2026-09-16 翻案，取方案 2 的最简版**（[#39](https://github.com/zephyr4123/TJU-AI4Science/issues/39)）：R-1 spike 实测（[#20](https://github.com/zephyr4123/TJU-AI4Science/issues/20)）执行层的承重隔离位是 `--setting-sources ""` 加 `--disable-slash-commands`，这两个参数正是把本机 CLAUDE.md、plugin、skill 一并关掉的东西——P-11 的隔离与"CLI 原生加载领域 skill"是同一个开关的两面，不能只要一半。所以领域 skill 由框架在 `run new` 时快照进 run，随执行层提示的「领域约定」段整文件追加，不做关键词匹配；实验与分析两个能力都吃。这样换执行层也不失效。

> **2026-09-20 再记（[#113](https://github.com/zephyr4123/TJU-AI4Science/issues/113)，P-22）**：方案 2 收成正式规矩且不再限于执行层——框架起会话时把 `skills/`（通用）与所选领域包 `skills/`（领域）拼成 `<available_skills>` 清单进 prompt，agent 用 `ai4sci skill show / run` 读全文、起脚本；格式照 agentskills.io，脚本 PEP 723 自带依赖。快照进产出目录的做法保留。此问题关闭。

## Q-3 验收怎么定义

"验收"有两层：单次运行的验收（这次跑出来的东西能不能信）和版本的验收（这一版做完没有）。

- 单次运行：manifest 的 `requirements` 逐条判，判据由协调层拍板后写进 manifest。`numeric` 与 `artifact` 类由框架确定性判；`discussion` 类由隔离裁判判并给出证据引用。三条零 LLM 判据（数字回溯、引用真伪、图源）永远在。判决回到协调层，由它决定接受、重跑还是换方向。
- 版本：spec 里的 A-n，尽量一条命令能查。

依据：AutoResearchClaw 的 `requirements_judge` 形状，但它只在 agent 模式生效、重试只有 1 次、裁决者不隔离（[§7.2](../../research/selection/2026-0909-pipeline-frameworks/autoresearchclaw.md#72-arc-bench整仓最扎实的部分)）。

## Q-4 评测怎么做

评测层评的是框架本身，不是单篇。候选形态：
- **rubric 树**：ARC-Bench 的加权递归树（叶子带 `task_category` 与 `judging_note`），LLM 判官旁边必须有确定性信号（从 `results.json` 算零方差、std/mean 比）。
- **组件消融**：开关统计门、开关 harness 校验、开关隔离裁判，看结果差多少。这是我们相对三个仓最能讲出故事的实验：它们的护栏一半没通电。
- **噪声基线**：同配置重复 k 次报 σ，任何"改进"先跟 σ 比。

建议先做噪声基线与消融，rubric 树等第一个真任务定了再写。首个工科 bench 目标 3 到 5 题。

## Q-5 第一个真任务与学院

人和领域的决定，读框架读不出来。建议不等：先用玩具任务（30 秒的 MLP 回归，或一根悬臂梁的有限元）把闭环跑通，学院定了换任务目录，循环不动。真任务要满足的条件：能在几分钟内跑完一次、能压成一个对离散化不变的标量、基线代码能整理成单入口。

**2026-09-16**：学长案例到了（[#1](https://github.com/zephyr4123/TJU-AI4Science/issues/1)），入库在 `docs/cases/`。案例二 `boehm-stat5-petab`（9 参数最小化 NLL，秒到分钟级 CPU）三条条件全中，选为第一个真任务包；案例一登记为复现型不跑；案例三访谈是 P-10 分工的第一份研究者证据。学院方向按导师要求是交叉领域，三个案例分属三个领域是预期。

## Q-6 执行环境

platform 0.2.0 本机 venv 里起独立进程，隔离只到进程级；docker 模式在 harness 需要装东西时再加；集群按 ADR-0001 的判据到时候拆仓。AutoResearchClaw 的教训：docker 不可用时静默降级成裸进程是错的，隔离降级必须显式失败。

**2026-09-16 细化**（[#39](https://github.com/zephyr4123/TJU-AI4Science/issues/39)）：venv 是**任务级**不是平台级——任务包自带 `env/`，框架用 uv 建 `tasks/<id>/.venv` 与 `runs/<id>/.venv`，平台 venv 一个包不多装；harness 经 `$AI4SCI_PYTHON` 起 Python。第一个真任务（案例二）走纯 pip 栈就够，没触发 docker；uv 或解释器拉不下来时明确报错，不退回平台 venv。

**2026-09-20 再记**（[#119](https://github.com/zephyr4123/TJU-AI4Science/issues/119)）：环境在哪台机器上建，由 P-23 定——算力按人配在 `~/.config/ai4sci/computes.yaml`，只有 SSH 只认密钥，助理按名字选、能在对话里帮人接机器；远端只跑 harness，venv 在远端按 `env/` 建，清单按目标机器算（`env resolve --compute`）。研究者没有现成环境的情形（非工程师的常态）由 `ai4sci env resolve` 按包名算完整清单（[#117](https://github.com/zephyr4123/TJU-AI4Science/issues/117)）。docker 仍未触发。

## Q-7 无人值守时协调层怎么找人

大方向 2026-09-10 已定（[#18](https://github.com/zephyr4123/TJU-AI4Science/issues/18)）：人在协调层的对话里，框架没有人在环功能，不等人。剩下的问题只有一个：协调 agent 无人值守（挂机过夜）时把问题留给人、人异步回复，走什么通道。候选是 issue 评论、协调 CLI 自己的通知机制。platform 0.2.0 不做，先用交互态对话。co-pilot（协作改假设、共写论文）在协调层里天然就是对话，不再是单独的模式。

> Q-7 补记（2026-09-17）：实验 #55 里长按钮在一轮对话里等不到底，暂时用「关后台 + 前台等」兜住（[#57](https://github.com/zephyr4123/TJU-AI4Science/issues/57)）。无人值守的正解是长能力做成异步作业：`cap experiment` 立刻返回作业号，`show run` 报进度，页面轮询，人回来看结果。做 Q-7 时一起做。
>
> Q-7 再记（2026-09-17 晚，[#63](https://github.com/zephyr4123/TJU-AI4Science/issues/63)）：异步作业做了——`--detach` 起作业、跑完框架以「框架」身份给对话发一轮叫醒 agent，run 记流程与步序、在等谁现算。剩下的只有「人不在时怎么通知人」这一段通道（页面刷新能看到，主动推送没有），仍归 Q-7。

## Q-8 协调层与执行层各用哪个 CLI

两层各自选，可以不一样。执行层：Claude Code 先行（本机有、flag 已对账），Codex 第二（本机有、flag 未对账），每加一个适配器必须带真 CLI 冒烟测试。协调层：开工时定，0.2.0 就是主人加交互态的 Claude Code。

**2026-09-22 关闭（P-25，[#130](https://github.com/zephyr4123/TJU-AI4Science/issues/130)）**：不再是「开工时定」——两层各用哪家是使用者自己的设置（`~/.config/ai4sci/agents.yaml`），页面「设置 → AI」两个下拉；Codex 适配器 [#131](https://github.com/zephyr4123/TJU-AI4Science/issues/131) 先接执行层、再接协调层，flag 只信官方文档并本机 spike。

## Q-9 项目级记忆怎么做

2026-09-10 改写。run 级记忆已经有了：账本给机器对账，实验笔记给执行层（真跑证明没有它执行层会重复改动）。项目级记忆是另一回事：文献笔记、假设台账、跨 run 的结论，它们是分析与写作能力的输入，没有它论文写不出来。形态待定：最直接的是项目目录下几个有 schema 的文件（`lit.jsonl`、`hypotheses.md`、`conclusions.md`），由对应能力写、由协调层与后续能力读；`agenthub` 那种"读前沿、查 children 避免重复"的做法等多 agent 并行时再考虑。0.2.0 不做，之后第一优先。

**2026-09-18 再记（[#70](https://github.com/zephyr4123/TJU-AI4Science/issues/70)）**：run 之上有了工作区（一份需求的家，P-15），但工作区之上仍没有目录：项目级产物（文献、假设、论文）的家等文献 / 写作能力落地时定，多半是「几个工作区 + 项目级文件」的一层。

**2026-09-22 定（[#136](https://github.com/zephyr4123/TJU-AI4Science/issues/136)）**：工作区之上加了 `projects/<p>/`——一个项目一位助理、共用原件 `materials/`、对话归项目。项目级产物（综述、论文）不是项目自己的文件：是项目里走写作流的那个工作区的产出，`--from` 兄弟工作区；项目级记忆仍是助理看盘（`show project`）不是对话记忆。

## Q-11 文献检索走 tools/ 学术 API 还是执行层联网

**已定（2026-09-21，P-24，[#120](https://github.com/zephyr4123/TJU-AI4Science/issues/120)）：用 agent 自带的搜索与读网页，不做按站点的学术 API 脚本。** 理由：论文的产物散在作者主页、README 里的网盘链接、Zenodo、issue 里，按 GitHub / HF / Semantic Scholar API 查的脚本只覆盖规整的那部分，漏的恰恰是难找的；两层适配器已放行 WebSearch / WebFetch（P-14）。找与挑在协调层对话里做，结果手写进文献格的 `sources.md` 带来源；「引用真伪」的零 LLM 判据以后在验证阶段按 DOI / arXiv id 核，与检索怎么做无关。原先的想法留档：

> 执行层被隔离后 MCP 清零，内建 WebSearch 仍在但不受控。建议 `tools/` 里做确定性脚本走学术 API（Semantic Scholar / arXiv / OpenAlex），执行层调脚本，结果带 DOI 或 arXiv id 落 `lit.jsonl`，验证能力用同一套 API 核引用真伪。

## Q-12 写作能力的形态

论文是长文档、多节、要图、要引用，一次执行层调用写不完。建议分节多次调用，每节的输入是项目记忆 + 分析产物 + 前面已写的节；模板（Markdown 或 LaTeX）放领域包；图由 `tools/` 从 `results.json` 与账本确定性生成，执行层只引用不画；写完过数字回溯、引用真伪、图源三条判据，不过就停。

## Q-13 低代码协调层的形状

主人的预期需求：低代码平台，用户拖拽搭流程。纲领已定它是第二种协调层（P-12），框架不为它改。要定的：

- 图的描述格式：节点 = 能力描述符的引用 + 参数，边 = 产物流向；存 YAML 还是 JSON，放哪。
- 谁解释图：一个确定性的图运行器按边调能力的 Python 函数，还是协调 agent 读图照着跑。建议并存：图里放"交给 agent 决定"的节点。
- 固定流程的先例：auto-research = 实验 + 分析 + 验证；文献综述 = 文献；补写论文 = 分析 + 写作读已有 run。
- UI 后端调能力的方式：直接调 Python 函数，不解析 stdout；表单由描述符驱动。

前提：能力描述符先有（09-22 第二个能力落地时从两个真实例抽），图 DSL 在描述符之后，不先建。


**2026-09-16 主人判断（[#34](https://github.com/zephyr4123/TJU-AI4Science/issues/34)）**：协调层最终要有一个面板（先 TUI 后 GUI），人和协调 agent 的对话在面板上进行；每个能力跑完框架退出、面板停在那一格，人和 agent 看产物、拍板，再继续对话让框架走下一步。面板不是新的一层，是协调层的脸：

- 摆的东西全在磁盘上：manifest、账本、笔记、分析、验证报告、journal，各能力的退出码；UI 不发明数据，只画 `runs/<id>/`。
- 按钮就是能力函数：CLI 是薄壳，UI 后端调同一个 Python 函数（P-12）；方块由 `cap list --json` 的描述符生成。
- 停点天然存在：框架不连跑（P-10），每条命令跑完退出，UI 只是把停点变成看得见的一格——这一步吐了什么草稿、等谁拍板、拍了什么、为什么。
- 真正缺的一样东西：「等谁拍板」现在只在协调 agent 脑子里和 journal 里，不是机器可读的。做 UI 之前先给 run 加一个可读的等待状态（停在哪个能力后面、等哪个人做什么），这是 Q-13 的实质。
- 顺序：先 TUI（对话旁边一格状态面板，验证停点可视化对不对），GUI 留给拖拽搭流程，等能力多到值得拖。现在不动手，再接一两个真任务、设计能力做成命令、停点稳定了再画。
- 底线：面板不能把对话换成按钮。拍板的「为什么」是研究记录的一部分，留在对话与 journal 里，按钮只是执行。

**2026-09-16 晚补充（[#34](https://github.com/zephyr4123/TJU-AI4Science/issues/34)）**：产品形态定在 vision「产品形态：两个发布键、一次验收」。对上面几条的更正：

- ⚠️更正「先 TUI 后 GUI，现在不动手」：主人定为直接做 GUI，基于现有能力块做完整 MVP；分工由主人排。
- ⚠️更正「停点 = 签评分脚本、看基线、看报告」：合并成发布与验收两个按钮。签字挪到脚本之前，签的是看板上的「怎么算好」；「看基线」改机器预检（[#42](https://github.com/zephyr4123/TJU-AI4Science/issues/42)）。
- 「等谁拍板」机器可读仍是实质，形状定了：发布记录是按钮的钥匙，没有就不开；停点 = 断口 + 问话 + 等谁，钥匙可提前给。
- 图的描述格式（套餐文件）仍不先建：套餐先是文字，有第二个套餐再定格式。谁解释图：前期协调 agent 读着按，画布来了再由零模型的运行器按清单按到停点，框架仍不做决定。

**2026-09-17 补记（[#58](https://github.com/zephyr4123/TJU-AI4Science/issues/58)）**：真实协调 agent 拼出并跑通自定义流程之后（[#55](https://github.com/zephyr4123/TJU-AI4Science/issues/55)），几件事定了形：

- 等待状态的形状：run 记「照哪条流程、走到第几步、停在等谁」，外加开跑时那条流程的快照；页面读它高亮模块、亮钥匙。这是 Q-13 一直说的「实质」，现在有了明确的读取点。
- 两块看板：编辑台改库（对话拼流程存文件，可选），主页面改实例（接流程照跑，不立新流程）；界线是可写目录，也就是工具白名单。
- 主页面右侧随流程生成，一步一个模块，不写死流程；需求对齐是 intake 前三步，在主页面。
- 图的描述格式：还是 `workflows/*.yaml`，拟加步骤 `with:` 参数。谁解释图：主页面的协调 agent 读着按；零模型的运行器仍等画布。
- 拖拽画布仍不做；在编辑台「搓能力」是 v2，走代码的路（草稿子包 + 契约测试 + 人合并）。

**2026-09-18 补记（[#70](https://github.com/zephyr4123/TJU-AI4Science/issues/70)）**：图的实例化定了形——库里的流程 `ai4sci flow take` 到工作区成实例，改参数与步骤都在实例上，run 快照实例（P-15）；解释图的仍是主页面的研究助理；造流程归编辑台另一位助理，研究助理不造流程（P-16）。

**2026-09-18 再记（[#93](https://github.com/zephyr4123/TJU-AI4Science/issues/93)，P-18）**：图的形状定了——不是带端口的积木，是**阶段 + 断点**：`rooms` 列表里一项是一个阶段（可点名能力、带参数）或一个断点（停下来等人确认）。阶段之间不做数据流校验，机器只查阶段名、能力归属、参数、断点位置；顺序与回头由人定。编辑台就是排阶段、挂能力、插断点；解释图的仍是主页面的研究助理，走到断点停下来等人说「继续」。「等谁拍板」机器可读了：进度记录 `flow.json` 记走到第几项，下一项是断点就是等人。

## Q-14 加一个能力非得写代码吗

现在必须：能力子包导出 `run()`。另一条路是声明式能力——目录里只有描述符（YAML）与 `prompt.md`，框架用一段通用驱动起执行层、在产出目录里照说明书干、把结论写回。好处是「新 skill 想当一格」不用工程师；代价是没有代码核对产出，只能靠下游开工时报错与人签字。倾向两种并存：机器能力写代码，模型能力可以只写说明书。主人未拍板（2026-09-19，[#110](https://github.com/zephyr4123/TJU-AI4Science/issues/110)）。

## Q-15 执行层的可写范围锁不锁在产出目录

auto-research 的 `work/` 已经在产出目录里，但没有机制拦执行层写到别处。建议一律锁：cwd = 产出目录，输入目录只读挂进去——「能力是纯函数」才不靠自觉。主人未拍板（2026-09-19，[#110](https://github.com/zephyr4123/TJU-AI4Science/issues/110)）。


## Q-10 协调层 skill 包放哪、怎么注入

候选：
1. 内仓 `coordinator/`：一份 `CLAUDE.md` 级别的入口指南 + `skills/<name>/SKILL.md`。注入按 CLI 走各家原生机制（Claude Code 读项目 CLAUDE.md 与 `.claude/skills`，Codex 读 AGENTS.md 与 `.agents/skills`），用 symlink 或一条安装脚本挂进去。零框架代码。
2. 塞进 `domains/generic/skills/`。否掉：会和执行层混在一条搜索路径上，违反 P-11。

建议 1。0.2.0 只放一份入口指南（spec R-10），skill 目录等真有第二条 skill 再建。

> **2026-09-20 再记（[#113](https://github.com/zephyr4123/TJU-AI4Science/issues/113)，P-22）**：入口指南仍在 `coordinator/`、仍由框架塞进 system prompt；协调层的**工具型** skill 不另建目录，用平台通用的 `skills/`（与执行层共用同一个库、同一套 `ai4sci skill` 命令），不走各家原生机制。P-11 的隔离只剩「指南不给执行层、领域 skill 不给协调层」。此问题关闭。

## 变更记录

| 日期 | 改了什么 | 为什么 | 认可 |
|---|---|---|---|
| 2026-09-22 | Q-8 关闭：两层各用哪家是按人的设置（P-25，[#130](https://github.com/zephyr4123/TJU-AI4Science/issues/130)） | 全面适配 Codex 时一并定 | 主人 + Claude |
| 2026-09-21 | Q-11 关闭：文献检索用 agent 自带工具，不做学术 API 脚本（P-24，[#120](https://github.com/zephyr4123/TJU-AI4Science/issues/120)） | 复现流定下来时一并定 | 主人 + Claude |
| 2026-09-20 | Q-2、Q-10 关闭：skill 系统定型为 P-22（[#113](https://github.com/zephyr4123/TJU-AI4Science/issues/113)） | 三路调研后与主人定 | 主人 + Claude |
| 2026-09-10 | 建档，九项 | 三层未定，先把问题与候选写下来 | 主人 + Claude |
| 2026-09-15 | 加 Q-13 低代码协调层的形状（[#34](https://github.com/zephyr4123/TJU-AI4Science/issues/34)） | 主人对齐高度模块化，低代码图是第二种协调层 | 主人 + Claude |
| 2026-09-10 | Q-9 改写为项目级记忆；加 Q-11 文献、Q-12 写作（[#29](https://github.com/zephyr4123/TJU-AI4Science/issues/29)） | 端到端对齐 | 主人 + Claude |
| 2026-09-10 | Q-1 Q-2 Q-7 Q-8 Q-9 按四层改写，Q-7 大方向标已定；加 Q-10（[#18](https://github.com/zephyr4123/TJU-AI4Science/issues/18)） | 加了协调层：顺序、人在环、记忆都归它，skill 分两套 | 主人 + Claude |
| 2026-09-16 | Q-5 加案例到达记录：案例二选为第一个真任务包，学院方向是交叉领域（[#1](https://github.com/zephyr4123/TJU-AI4Science/issues/1)） | 学长三个案例入库 `docs/cases/` | 主人 + Claude |
| 2026-09-16 | Q-2 翻案走 prompt 追加；Q-6 细化为任务级 venv（[#39](https://github.com/zephyr4123/TJU-AI4Science/issues/39)） | 真任务落地时发现隔离参数关掉了原生 skill 加载；任务自带环境 | 主人 + Claude |
| 2026-09-16 | Q-13 加主人判断：协调层的面板（TUI → GUI）是协调层的脸，停点可视化，缺一个机器可读的等待状态（[#34](https://github.com/zephyr4123/TJU-AI4Science/issues/34)） | 真任务闭环跑通后对齐 UI 的位置 | 主人 + Claude |

> Q-13 补记（2026-09-16 深夜）：套餐文件提前落地了，改叫流程 `workflows/*.yaml`，因为页面要列出来、下一步的自定义工坊要让 agent 在对话里拼出来存进去。格式故意最小：name / title / summary / assumes / steps，见内仓 `framework/contracts/workflows.py` 文件头（[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)）。
| 2026-09-17 | Q-7 补记：长按钮暂用关后台兜住，异步作业是无人值守的正解（[#57](https://github.com/zephyr4123/TJU-AI4Science/issues/57)） | 实验 #55 第三轮长按钮被挪到后台杀掉 | 主人 + Claude |
| 2026-09-17 | Q-13 补记：等待状态的形状、两块看板、页面随流程生成、步骤参数（[#58](https://github.com/zephyr4123/TJU-AI4Science/issues/58)） | 主人拍板产品形态补记 | 主人 + Claude |
| 2026-09-19 | 加 Q-14 声明式能力、Q-15 执行层可写范围（[#110](https://github.com/zephyr4123/TJU-AI4Science/issues/110)） | P-20 探讨里主人未拍板的两条 | 主人 + Claude |
| 2026-09-20 | Q-6 加算力按人配（P-23）与「没有环境」的清单命令（[#119](https://github.com/zephyr4123/TJU-AI4Science/issues/119) [#117](https://github.com/zephyr4123/TJU-AI4Science/issues/117)） | 平台开源去中心化，算力由使用者自己配；第一轮真任务暴露小白没有环境 | 主人 + Claude |
