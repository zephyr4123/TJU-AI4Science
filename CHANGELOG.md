# 变更日志

本仓库所有值得注意的变更都记录在这里。格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本 2.0.0](https://semver.org/lang/zh-CN/)。

- 每个改动合并时，把条目写进 **Unreleased**；发布时 `make release VERSION=x.y.z` 把它轮转成版本小节并打 tag，推送 tag 即触发 GitHub Release。
- 1.0.0 之前是开发期：0.x 不承诺兼容性，正式发布才进入 1.0.0。
- 条目分类用：新增 / 变更 / 修复 / 移除 / 安全。

## [Unreleased]

### 新增
- README「五分钟承接」分两种人：只用平台的装 Release 里的 wheel 一行起，共同维护的 clone 后 `cd platform && make up`（[#138](https://github.com/zephyr4123/TJU-AI4Science/issues/138)）
- 案例库加 `docs/cases/gua-codex-drill/`：第三轮演练——两层都是 Codex、在项目层与新页面上复现 arXiv 2609.01558，没跑到底（基线被 sigma.json 的 seeds 拒、重跑到一半机器定时关机）；案例卡（时间线、与 #120 Claude Code 那轮并排、主人要验的三件事、四个坑与修法、留着的债、复跑怎么接）、需求、材料来源、评分契约与壳、执行层会话、整段对话（主机端口路径已抹）；案例库索引加一行（[#137](https://github.com/zephyr4123/TJU-AI4Science/issues/137)）
- workflow §5 界面适配「项目」改成已落地（地方栏三键、首页项目墙、门口一句话起项目、项目页正中间的对话入口 + 工作区清单、工作区页页眉「‹ 项目名  工作区 ▾」），词表「主页面 / 编辑台」改「首页 / 项目页 / 工作区页 / 编辑台」；变更记录（[#136](https://github.com/zephyr4123/TJU-AI4Science/issues/136)）
- 纲领加「项目」：README §2 改「项目与工作区」、P-15 改「项目即助理的边界，工作区即需求的边界」；workflow §1 磁盘布局加 `projects/<p>/`（对话与共用原件归项目、每段对话一个收件箱）、跨工作区 `from` 只限同项目、§4 叫醒改收件箱、§5 命令行加 `project` / `--ws` / `AI4SCI_PROJECT`、删除边界加项目、端点改 `/projects/<p>/…`、词表加「项目」；Q-9 记「工作区之上」已定；变更记录（[#136](https://github.com/zephyr4123/TJU-AI4Science/issues/136)）
- workflow §5 加「删除边界」：平台出厂的不能删、人产生的都能删、删就从根级联删干净（对话连 CLI 那边的会话、工作区连机器上的镜像）、没有软删除；产出只删叶子；命令行加五条 remove；变更记录（[#134](https://github.com/zephyr4123/TJU-AI4Science/issues/134)）
- 纲领 P-22 改「skill 是能力的一种」：一个词「能力」、两个 tag（步骤 / skill），两种都进能力库、都能挂到流程的格子上、都上看板；P-20 那句「skill 不是一格」改成「skill 不开产出目录」；workflow §1 skill 一节、关系表、流程示例（文献格挂 pdf 与 download）、词表（能力 / 步骤 / skill 三行）同步；变更记录（[#134](https://github.com/zephyr4123/TJU-AI4Science/issues/134)）
- 案例库加 `docs/cases/boehm-codex-drill/`：两层都换成 Codex 跑通研究流全链的演练（Boehm PEtab 参数拟合，验收已签）——案例卡（时间线、七个坑与修法、Codex 观察、token 数）、需求、流程实例、评分契约与壳、拟合脚本、三个种子的基线、助理三次喂回执行层的意见、账本与笔记、分析、核对报告、整段对话（主机端口路径已抹、指南全文略去）；案例库索引加一行（[#135](https://github.com/zephyr4123/TJU-AI4Science/issues/135)）
- workflow §5 执行层适配加 Codex 适配器的实测清单（私有 CODEX_HOME 是隔离承重位、skills 要按 SKILL.md 逐个关、`ai4sci` 靠 execpolicy 规则在沙箱外跑而其余命令留在沙箱里、嵌套沙箱走不通、无逐字事件、订阅报不出美元、嵌套会话里环境的 CODEX_HOME 会把 auth.json 软链指向自己）；协调层适配加 Codex 续接、`guide_channel` 与 `tool_guide`（[#131](https://github.com/zephyr4123/TJU-AI4Science/issues/131)）
- 纲领 §4 加 P-25 底座归人：按人的 `~/.config/ai4sci/agents.yaml` 与 `computes.yaml` 并列、助理与执行层各选一家（可不同）、四句话自检（`probe()`、`ai4sci agent list|check|use`、`ai4sci check`）、旋钮删「默认」只留具体值、接新 CLI 只信官方文档先 spike、页面「设置」悬浮板（入口在地方栏脚、主题搬进去加「跟随系统」）；workflow §5 加「设置与自检」、命令行加 `agent` `check`、词表加「设置」「AI」；Q-8 关闭（[#130](https://github.com/zephyr4123/TJU-AI4Science/issues/130)）
- research/evals 加「平台第一次完整跑通的论文复现」：README（阅读版）+ 手写的完整记录页 `report.html`（链路每一步与命令原文、论文值 vs 我们的值图表、算力与能力、涌现清单、成本、保留意见），随 Pages 公开（[#120](https://github.com/zephyr4123/TJU-AI4Science/issues/120)）
- 案例库加 `docs/cases/gua-pinn-reproduction/`：平台第一次完整跑通的论文复现（arXiv 2609.01558，一级，已验收）——案例卡、需求、材料来源、评分脚本、五个种子的结果、复现性分析、核对报告、整段对话，主机端口已抹（[#120](https://github.com/zephyr4123/TJU-AI4Science/issues/120)）
- P-24 补「现成环境缺包就补（`ai4sci env add`）」「执行层会话额度按能力给」；workflow §5 命令行加 `env add`（[#120](https://github.com/zephyr4123/TJU-AI4Science/issues/120) #122）
- 纲领 §4 加 P-24 论文复现：另一条流程 `reproduce`（文献手写 `sources.md` → `reproduction` 原码复现基线 → 人签 → `reproducibility` 复现性分析 → 验证）、复现三级、两颗新能力与现有的同阶段可替换、搜索用 agent 自带工具不做定位器、`download` skill、机器只卡三条；workflow §1 §5 同步；Q-11 关闭（[#120](https://github.com/zephyr4123/TJU-AI4Science/issues/120)）

### 变更
- P-23 两问改口（主人 2026-09-20 演练拍板）：租来的第三方平台一律用镜像自带的现成环境、租时选好带 PyTorch + CUDA 的镜像，隔离新建只在实验室自己的机器上谈；纲领与 workflow §5 同步（[#118](https://github.com/zephyr4123/TJU-AI4Science/issues/118)）
- workflow §5 按演练回写两处：`--detach` 等作业过门、开了产出再返回（带 `output=`，当场没开起来的退 1）；基线跑之前删本地 `baseline/`、拿回来按开跑的合约查全（[#118](https://github.com/zephyr4123/TJU-AI4Science/issues/118)）
- P-23 补「接上先盘点、再问两问」（盘点机器上已有的环境，问研究者隔离新建还是用现成的、用哪个；`ai4sci env use` 记 `materials/env/interpreter`）；workflow §5 算力适配加同一段与 `env use`、远端 uv 走镜像当额外索引、长命令 nohup + 轮询（[#118](https://github.com/zephyr4123/TJU-AI4Science/issues/118)）

### 新增
- 纲领 §4 加 P-23 算力归人（平台开源去中心化，算力由使用者自己配）：按人的 `~/.config/ai4sci/computes.yaml`、只有 SSH 只认密钥、agent 按名字选并记进 meta、对话里接机器（助理跑 `ai4sci compute add`，不设自我感动的坎）、远端只跑 harness；workflow §5 算力适配按它重写、命令行加 `compute` 与 `env resolve --compute`、meta 加 `compute`；P-14 补一句；open-questions Q-6 再记（[#119](https://github.com/zephyr4123/TJU-AI4Science/issues/119)）

### 变更
- workflow §5 命令行加 `job stop`、`env resolve`，记第一轮真任务（PINNs，Claude 扮小白研究者）逼出的三条改动：停作业、研究者没环境时按包名算完整清单 + 建完查完整 + `--continue` 遇环境变了拒、设计草稿先 `ruff --fix-only` 修 import 顺序（[#115](https://github.com/zephyr4123/TJU-AI4Science/issues/115) [#116](https://github.com/zephyr4123/TJU-AI4Science/issues/116) [#117](https://github.com/zephyr4123/TJU-AI4Science/issues/117)）
- 纲领 P-22 按内仓落地回写：pdf skill 的后端定为 pymupdf4llm 版面模式（PINNs 22 页 1.7 s，表里的数全对），MinerU 4.0 basic 同一篇实测 27.6 s、1.2 GB 带 torch、常驻服务，不当缺省；`ai4sci skill run` 加 `--script`；执行层 Bash 白名单只有 `ai4sci skill *`；领域 skill 不再全文注入执行层 prompt、不再随实验快照（workflow §1 §5、domains.md、README P-22）（[#113](https://github.com/zephyr4123/TJU-AI4Science/issues/113)）
- P-14 补「联网只用 CLI 自带的搜索与网页读取工具」：实测 dontAsk 下 WebSearch / WebFetch 不放行就被拒、agent 拿 curl 硬凑；两层适配器必须放行，prompt 写清什么时候查、查到的带来源（workflow §5 执行层适配）（[#114](https://github.com/zephyr4123/TJU-AI4Science/issues/114)）

### 新增
- 纲领 §4 加 P-22 skill 系统（按 agentskills.io 规范写、框架自己注入清单、`ai4sci skill list / show / run`、脚本 PEP 723 自带依赖不建工作区级 venv、第一个 skill `pdf` 的契约）；workflow §1 加「skill」一节、§5 命令行加 `skill`；P-20 的「skill 不写盘」改为「写哪里由调用者定」；domains.md `skills/` 回写；open-questions Q-2 / Q-10 关闭（[#113](https://github.com/zephyr4123/TJU-AI4Science/issues/113)）
- workflow §5 界面：编辑台按现状回写成两个镜头「流程 / 能力」（文件名由标题生成、配置板只剩名字与参数、能力陈列与详情页）；能力表与示例流程里 `auto-research` 写 AutoResearch、断点改「评分指标核对」；名的上限改为八字（[#112](https://github.com/zephyr4123/TJU-AI4Science/issues/112)）
- 纲领 §4 加 P-21 页面词表（一个概念一个词、名词做标签、内部名不上屏、能力文案三层对三种动作、编辑台加「能力」镜头）；workflow §1 契约加能力文案三层的规矩、§5 界面适配加词表与文案两条；活文档「流」「工作流」改「流程」、「颗」改「个」、五栏改名 职责 / 边界 / 输入 / 产出 / 终止条件（[#112](https://github.com/zephyr4123/TJU-AI4Science/issues/112)）
- workflow §5 界面：主页面加文件镜头（页眉「看板 / 文件」切换、带平台语义的目录树、只读）；门口与主页面两段按现状回写（学科、一条流一张表、工具调用不折叠）（[#111](https://github.com/zephyr4123/TJU-AI4Science/issues/111)）
- 纲领 §4 加 P-20 能力的接法（形状归框架、主文件归阶段、来源归 meta；skill 不是一格）；workflow §1 契约加阶段主文件表与两层文件规则、`from` 边成图的说明；open-questions 加 Q-14 声明式能力、Q-15 执行层可写范围（[#110](https://github.com/zephyr4123/TJU-AI4Science/issues/110)）
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
