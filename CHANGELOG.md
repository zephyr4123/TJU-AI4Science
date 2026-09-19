# 变更日志

本仓库所有值得注意的变更都记录在这里。格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本 2.0.0](https://semver.org/lang/zh-CN/)。

- 每个改动合并时，把条目写进 **Unreleased**；发布时 `make release VERSION=x.y.z` 把它轮转成版本小节并打 tag，推送 tag 即触发 GitHub Release。
- 1.0.0 之前是开发期：0.x 不承诺兼容性，正式发布才进入 1.0.0。
- 条目分类用：新增 / 变更 / 修复 / 移除 / 安全。

## [Unreleased]

### 新增
- 一次性迁移脚本 `scripts/oneoff/migrate-workspaces-to-stages.py`：旧 `task/` + `runs/` 布局的工作区搬成 P-19 的阶段目录（requirement.md + lock、materials/、design/1、experiment / analysis / verification）；纲领 §5 内仓目录表与 workflow §1 §2 对齐内仓落地（`framework/experiment/` 子包、`.ai4sci/` 不含 work/、分析表列名「来源」、`docs/start-a-workspace.md`）（[#104](https://github.com/zephyr4123/TJU-AI4Science/issues/104) [#108](https://github.com/zephyr4123/TJU-AI4Science/issues/108)）
- 纲领 §4 加 P-19 工作区按阶段分目录、需求是根、产出多对多、框架只认 meta；§2 工作区那棵树重画；workflow §1 磁盘布局与契约重定、§4 人只做两件事、§5 命令行按 P-19 改、协调层与界面两节改成只写现状；vision 补记三；spec 加 R-36（[#104](https://github.com/zephyr4123/TJU-AI4Science/issues/104)）
- workflow §5 界面适配加「第八版」（编辑台节点画布：线性链、节点 = 阶段、阶段梯 + 玻璃题头、悬浮对话窗、`Param.in_flow`；全站文案清洗）；spec 加 R-35（[#100](https://github.com/zephyr4123/TJU-AI4Science/issues/100) [#101](https://github.com/zephyr4123/TJU-AI4Science/issues/101) [#102](https://github.com/zephyr4123/TJU-AI4Science/issues/102) [#103](https://github.com/zephyr4123/TJU-AI4Science/issues/103)）
- 纲领 §4 加 P-18 三层：研究阶段、能力、实现（流是按顺序经过几个阶段、断点是停下来等人确认），P-12 / P-13 收窄；workflow §1 重写成三层、§5 命令行按五颗能力改、界面适配加「第七版」；spec 加 R-34；open-questions Q-13 再记；一次性迁移脚本 `scripts/oneoff/migrate-flows-to-stages.py`（[#93](https://github.com/zephyr4123/TJU-AI4Science/issues/93) [#94](https://github.com/zephyr4123/TJU-AI4Science/issues/94) [#99](https://github.com/zephyr4123/TJU-AI4Science/issues/99)）
- workflow §5 协调层适配加「两个旋钮」、界面适配加「旋钮」（模型与思考深度：端口 `knobs()` / `tuning`、适配器 `--model` / `--effort`、对话记住、页面两枚下拉片）；spec 加 R-33（[#86](https://github.com/zephyr4123/TJU-AI4Science/issues/86)）
- workflow §5 协调层适配加「run 记对话号」、界面适配加「第六版」（泳道、默认收起、承接的那条展开、风景背景）；spec 加 R-32（[#82](https://github.com/zephyr4123/TJU-AI4Science/issues/82) [#85](https://github.com/zephyr4123/TJU-AI4Science/issues/85)）
- workflow §5 界面适配加「第五版」（地方栏、页眉归属、对话入口、门口那一屏）；spec 加 R-31（[#79](https://github.com/zephyr4123/TJU-AI4Science/issues/79) [#81](https://github.com/zephyr4123/TJU-AI4Science/issues/81)）
- 纲领 §4 加 P-17 素材上 CDN、图标内联；workflow §5 界面适配加「素材」；spec 加 R-30（[#75](https://github.com/zephyr4123/TJU-AI4Science/issues/75) [#76](https://github.com/zephyr4123/TJU-AI4Science/issues/76)）
- workflow §5 协调层适配补「库对研究助理可读不可写」：端口 `readable_paths`、`--add-dir`、前言写实路径（[#73](https://github.com/zephyr4123/TJU-AI4Science/issues/73)）
- 纲领 §2 加「工作区：一份需求的家」、§4 加 P-15 工作区即边界与 P-16 造流与用流分权、§5 目录换成 `workspaces/` `studio/`；workflow §1 流分三层、§5 命令行改成工作区口径、两位助理两个域、界面第四版；packs §1 §2 §4 任务包住进工作区；vision 产品形态补记二；spec 加 R-28 R-29；Q-9 Q-13 再记；`scripts/oneoff/migrate-runs-to-workspaces.py` 把旧 `runs/` 按 manifest 归进工作区（[#70](https://github.com/zephyr4123/TJU-AI4Science/issues/70) [#71](https://github.com/zephyr4123/TJU-AI4Science/issues/71) [#72](https://github.com/zephyr4123/TJU-AI4Science/issues/72)）
- 纲领 P-14 补「前期别设坎」「不用内部词」；workflow §5 记页面第三版（两块看板、脊柱、编辑台）与逐字流式；spec R-24 标完成、加 R-27（[#64](https://github.com/zephyr4123/TJU-AI4Science/issues/64) [#65](https://github.com/zephyr4123/TJU-AI4Science/issues/65) [#69](https://github.com/zephyr4123/TJU-AI4Science/issues/69)）
- workflow §4 人在环加「长按钮不占着对话等」、§5 协调层适配记异步作业落地；Q-7 再记；spec R-25 标完成（[#63](https://github.com/zephyr4123/TJU-AI4Science/issues/63)）
- README §4 加 P-14「CLI 主导封装」：agent 面前只有 `ai4sci`、缺按钮就加按钮不放行裸命令；workflow §1 设计阶段三颗按钮、§5 协调层适配的白名单与 PATH；spec 加 R-26；实验 #59 记录真实协调 agent 从零接 rahman（[#59](https://github.com/zephyr4123/TJU-AI4Science/issues/59) [#60](https://github.com/zephyr4123/TJU-AI4Science/issues/60)）
- vision 加「产品形态补记：两块看板，页面随工作流变」；纲领 P-12 补「页面同理」；workflow §1 拟定步骤参数与 run 记流、§5 界面适配下一版形态；Q-13 补记等待状态的形状；spec 加 R-24 R-25（拟定）与 MVP 顺序（[#58](https://github.com/zephyr4123/TJU-AI4Science/issues/58)）
- workflow §5 协调层适配加可写 `workflows/` 与「长按钮不进后台」，Q-7 补记异步作业方向，spec 加 R-23；实验 #55 记录真实协调 agent 四轮拼装并跑通（[#55](https://github.com/zephyr4123/TJU-AI4Science/issues/55) [#56](https://github.com/zephyr4123/TJU-AI4Science/issues/56) [#57](https://github.com/zephyr4123/TJU-AI4Science/issues/57)）
- README §4 加 P-13「文档即接口」：文件名就是接口、一个文件一个生产者、命名三规矩；workflow §1 契约段加种子清单与两处不齐的名字；spec 加 R-22（[#54](https://github.com/zephyr4123/TJU-AI4Science/issues/54)）
- workflow §1 与 README P-12：能力描述符加所属阶段与人话标题，七个科研阶段是能力上面的一层标签、反向归属不存只算；Q-1 补记；spec 加 R-21（[#53](https://github.com/zephyr4123/TJU-AI4Science/issues/53)）
- workflow §5 协调层驱动面改成四类命令（cap / sign / show / chat serve），packs §2 的命令名跟着改；spec 加 R-20（[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)）
- workflow §5 与 Q-13 补记：套餐改叫工作流并落成文件 `workflows/*.yaml`，`start` 成为第 6 颗能力，页面进度页换成工作流页（[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)）
- workflow §5 加「界面适配」（`ui/<kind>/` 一种界面一个目录、全是 `serve` 端点的客户端、TUI 留位置）并补看板端点与两颗键；spec 加 R-19 A-20 与 09-2x 第五格；`.playwright-mcp/` 进 gitignore（[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)）
- workflow §5 加「协调层适配」：`Chat` 端口与 Claude Code 续接、指南注入、对话落盘、`ai4sci chat` / `serve`；spec 加 R-18 A-19 与 09-2x 第四格（[#51](https://github.com/zephyr4123/TJU-AI4Science/issues/51)）
- MVP 第一批（[#47](https://github.com/zephyr4123/TJU-AI4Science/issues/47)）：packs §2 接任务清单加人发布（`publish.json` 钥匙）与机器预检（`attainable` 尽头值），接任务与跑基线升格成 task 级能力 `cap design` / `cap baseline`，加 `flow check`；spec 加 R-15 R-16 R-17 与 A-16 A-17 A-18、09-2x 第三格（[#48](https://github.com/zephyr4123/TJU-AI4Science/issues/48) [#49](https://github.com/zephyr4123/TJU-AI4Science/issues/49) [#50](https://github.com/zephyr4123/TJU-AI4Science/issues/50)）
- vision 加「产品形态：两个发布键、一次验收」：需求看板发布即签字、编排看板 agent 摆好人改、结果验收；「看基线」停点改机器预检；单点 / 套餐 / 停点 / 发布的口径。open-questions Q-13 更正「先 TUI」与三停点（[#34](https://github.com/zephyr4123/TJU-AI4Science/issues/34)）
- 裁判文件的契约进纲领 packs §2：`budget.inner_k`、框架保证给 harness 的三个环境变量、写默认值判不合法、`ai4sci task baseline`（[#43](https://github.com/zephyr4123/TJU-AI4Science/issues/43) [#44](https://github.com/zephyr4123/TJU-AI4Science/issues/44) [#45](https://github.com/zephyr4123/TJU-AI4Science/issues/45)）
- 案例卡 `docs/cases/rahman-ode-petab/`：平台自测材料（模仿研究者接入的第二道基准题），记接入过程与 12 个卡点并成的五条 issue（[#42](https://github.com/zephyr4123/TJU-AI4Science/issues/42)–[#46](https://github.com/zephyr4123/TJU-AI4Science/issues/46)）
- 接任务的按钮单元（[#41](https://github.com/zephyr4123/TJU-AI4Science/issues/41)）：spec 加 R-14 A-15 与 09-2x 第二格；packs §2 接任务清单改成「三问 + manifest + env + design.md + `ai4sci task design` + 签字 + 基线」的按钮版，分工里加框架封 harness 与 lint
- vision 加「给谁用、凭什么」：用户是非工程师研究者，产品 = 谁都能用 + 数能拿去用，命令行是 agent 的按钮不是人的界面，复用与自建的判据是「模型能干的交给模型，模型不能自证的自己做」，如实记今天的差距（[#34](https://github.com/zephyr4123/TJU-AI4Science/issues/34)）
- 任务自带环境与领域包单元的纲领与 spec（[#39](https://github.com/zephyr4123/TJU-AI4Science/issues/39) [#40](https://github.com/zephyr4123/TJU-AI4Science/issues/40)）：packs §2 加 `env/` 契约（python-version + requirements.lock，uv 建任务级 venv，launcher 只经 `$AI4SCI_PYTHON`）、manifest `format_version` 必填与 `source` 可选、接任务清单加分工；§3 领域 skill 注入改走 prompt 快照（Q-2 翻案：隔离参数关掉了原生加载），领域按工具链命名；spec 加 R-11 R-12 R-13 与 A-12 A-13 A-14，N-3 N-7 纳入；Q-6 细化为任务级 venv；vision 写工业级开源项目定位
- 案例库 `docs/cases/`（[#1](https://github.com/zephyr4123/TJU-AI4Science/issues/1)）：学长交付的三个案例入库，每个一张案例卡加一字不改的原文；按任务类型描述（回归 / 连续参数优化 / 表示学习），应用领域只留名词。案例二 `boehm-stat5-petab` 选为第一个真任务包；案例一登记为复现型 0.2.0 不跑；案例三访谈直接喂协调层的人在环停点。原件放新目录 `materials/`（gitignore），sha256 与重取方式记在案例卡；README、CLAUDE.md 同步
- 09-22 单元主体（内仓分支 `feat/analysis-verify`，#35 #36 #37 #38）：能力描述符与 `ai4sci cap`（子命令从描述符生成，`cap list --json` 是 UI 的节点定义）、分析能力（执行层写三节 `analysis.md`，数据表是数字回溯的锚）、验证能力（零模型四项检查，1% 容差，`report.json`）、协调层入口指南 `coordinator/README.md`；真跑 live-20 分析 $0.28 出 19 行数据表，验证 PASS。纲领 workflow §1 §3 §5、README §5、spec R-5 R-6 R-7 R-10 与 09-22 一格回写
- 端到端对齐（#29）：纲领加"产品是论文不是内环"与"研究项目"实体（项目 → 任务包 → run → 论文，契约与记忆各两级），workflow §1 加七个能力的输入 / 输出 / 执行者 / 判据表，Q-9 改写为项目级记忆，新增 Q-11 文献检索、Q-12 写作形态（#31 #32）；`framework/` 目录约定改为按概念分子包、依赖单向（#30）
- platform 0.2.0 第一单元完成（内仓分支 `feat/runner-spike`）：R-1 spike 用真 CLI 回答四个未知（隔离位、`//` 权限路径、逐进程组杀、成本来源），R-2 任务包契约与 `ai4sci task validate`，R-3 玩具任务 `mlp-regression` 含 run_0 与 σ。issue #20 #21 #22；纲领 workflow §5 与 packs §2 按实测回写

### 变更
- 高度模块化对齐（[#33](https://github.com/zephyr4123/TJU-AI4Science/issues/33)）：纲领加 P-12 能力可自由装配（粒度是能力、机器可读描述符、Python 函数 + 磁盘契约、契约挂产物不挂上游）与"协调层形态可换"（低代码图是第二种协调层）；workflow §1 加"装配与固定流"与"能力描述符"，§5 注明 CLI 薄壳；spec R-5 加描述符；新增 Q-13 低代码协调层的形状（[#34](https://github.com/zephyr4123/TJU-AI4Science/issues/34)）；纪要 `docs/meetings/2026-0915-modularity.md`
- 架构纲领三箱改四层：加协调层（人 + 协调 agent），科研判断归它，框架降为诚实执行基底，不连跑、不等人；"阶段"改"能力"、"底座"改"执行层"，人在环模式与文件通道移除；加 P-10 P-11 与 `coordinator/` 目录。spec 的 R-5 R-7 N-2 改写，新增 R-10 C-7 A-11；未决项加 Q-10；决策 issue #18，Q-10 是 #19；纪要 `docs/meetings/2026-0910-coordinator-layer.md`。spec 状态改为滚动：只驱动下一步，不设 aligned 门槛。纲领 workflow §5 加算力端口 `Compute`（put / submit / wait / cancel / get，句柄落盘，靠名字选择、不静默回退），目录加 `compute/`
- 内仓远端就位：`repos.json` 的 url 由 `TBD` 改为 <https://github.com/zephyr4123/TJU-AI4Science-Platform>（私有），`./repos remotes --fix` 接好 origin，骨架与 v0.1.0 首次推送；根 README、spec、纪要同步

### 移除
- `docs/architecture/packs.md` 的「任务包」一节整节删掉，文档改名 `domains.md` 只讲领域包（[#104](https://github.com/zephyr4123/TJU-AI4Science/issues/104)）

## [0.3.0] - 2026-09-10

### 新增
- 流水线层选型调研 `research/selection/2026-0909-pipeline-frameworks/`：InternAgent-1.5 代码级深读（四个读者分片读 `vendor/` 克隆，138 条带 `文件:行` 的发现，抽查 8 条属实），结论是抄任务契约与三块零件、不当流水线层底座；`README.md` 放候选清单与横向对比表，后续候选逐个补入
- 选型深读第二、三篇：autoresearch（两个读者，42 条发现，抽查 5 条；含 H100 真实跑档 125 次实验的数据与被删的 `spawn.sh`、未合并的 `agenthub` 协议）与 AutoResearchClaw v0.5.0（六个读者，177 条发现，抽查 13 条；四个总问题逐条对账 README 与代码）。对比表补齐三行，"目前能定下来的"从 4 条扩到 8 条：编排自己写、任务契约两层、内环用棘轮且裁判外置、评测由框架注入、验证层三条零 LLM 判据、底座 Runner 协议、人在环文件通道、四条机器可查的规矩
- `research/README.md` 新增 `selection/` 目录形态说明；行业调研的 InternAgent 条目与台账链接到深读
- `.gitignore` 新增 `/vendor/`：选型阶段拉来研究的第三方开源项目放这里，物理在树里、git 看不见
- 架构总纲领 `docs/architecture/`（README 三箱结构与九条原则、workflow 阶段骨架与实验内环、packs 任务包与领域包、open-questions 九项未决）；`docs/specs/platform-0.2.0.md` 初级版 PRD 草稿（R / N / C / A 编号，目标 2026-09-28）；`docs/meetings/2026-0910-workflow-alignment.md`；`docs/adr/README.md` 划定 adr 只放仓库基础设施决定。vision 与根 README 同步

### 变更
- 文档体系分四类：`architecture/` 可改的总纲领（改要双方认可 + 变更记录）、`specs/` 每版一份 PRD、`adr/` 只追加、`meetings/` 只记结论；协作方式定为 spec coding + issue driven
- 两条版本线分开命名：外仓版本只管项目之家，产品版本一律带 `platform` 前缀（初级版 = platform 0.2.0，0.1.0 是骨架）；milestone 与 spec 文件名只用产品版本。issue 面板建立：目标合约、五条母 issue 挂 milestone、Q-1 到 Q-9 各一条决策 issue、科研案例采集 issue
- 调研第 10 节路线图改为按决策点排期：2026-09-28 发初级版，之后每月一个正式版、内测版随时发；原按传统工期的阶段表相应重排

### 修复
- `make check` 的 html 同步检查只看未暂存改动与未追踪文件，md 改完 `make html` 并 `git add` 后本地门禁也能过；此前在提交前必报不同步

## [0.2.0] - 2026-09-08

### 新增
- 第一篇调研《新工科自动化科研智能体：2026 年工业界现状与架构设计》：`research/landscape/2026-0908-auto-research-agents/`，正文里项目名链接到条目、数字挂脚注，附 `references.md` 台账
- 调研阅读版工具链 `md2html`：渲染 `research/` 下全部 .md（README.md → index.html，索引页与台账一并出 html），锚点按 GitHub 规则生成，站内 .md 链接改写为 .html，文内链接与脚注不能落地直接报错；`make html` 构建，`make check` 新增 html 与 md 同步检查
- `research/README.md` 写明一篇调研的目录形态与引用规则
- GitHub Pages 管线 `pages.yml`：仓库转为公开，`research/` 定为公开区，main 更新即重新渲染并整体发布到 <https://zephyr4123.github.io/TJU-AI4Science/>；新调研进 main 自动上线

### 变更
- 内仓远端尚未创建，`repos.json` 的 url 改为 `TBD` 占位，不再写编造的地址；`./repos` 对占位仓只报告状态，clone / fetch / sync / pull / push 明确拒绝并退非 0
- `changelog.sh` 的链接引用允许 `TBD` 占位，但在占位上 `release` 会被拒绝

## [0.1.1] - 2026-09-08

### 修复
- `./repos remotes --fix` 对刚 `git init`、尚无 origin 的内仓会报错退出；现在 origin 不存在就 add，存在才 set-url

## [0.1.0] - 2026-09-08

### 新增
- 项目之家骨架：`repos.json` 内仓 manifest、`./repos` 跨仓 CLI（doctor / clone / status / sync / pull / push / remotes）、`.gitignore` 挡位
- 目录约定：`docs/`（项目级文档与 ADR）、`research/`（调研）、`scripts/`（外部脚本，生产代码不得依赖）、`assets/`
- 变更日志与发布流水线：CHANGELOG 机器校验、`make release` 轮转、tag 触发 GitHub Release
- ADR-0001 内外仓拓扑、ADR-0002 版本与发布策略

[Unreleased]: https://github.com/zephyr4123/TJU-AI4Science/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/zephyr4123/TJU-AI4Science/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/zephyr4123/TJU-AI4Science/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/zephyr4123/TJU-AI4Science/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/zephyr4123/TJU-AI4Science/releases/tag/v0.1.0
