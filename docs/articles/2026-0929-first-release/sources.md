# 事实出处

正文 [`README.md`](README.md) 里每个数字、时间、说法的来源。改正文里的事实先改这里；来源变了（比如纲领改了原则），回来对一遍。issue [#193](https://github.com/zephyr4123/TJU-AI4Science/issues/193)。

## 发布信息（公众号后台填）

- 产品名（只用于本文，平台、仓库与命令 `ai4sci` 不改）：**AAAI4S**（Automated Alignment AI4S），导师王征 2026-09-29 定，有意蹭 AAAI 会议的热度；首次出现、摘要、横幅处括号注全称，其余只写 AAAI4S。讨论过的 Align4S、OpenAI4S、RecursiveAI4S 未采用
- 标题：AAAI4S：可编排、可追溯的自动化科研（主人 2026-09-29 定；导师王征的要求：体现平台特色与天大特色，实事求是，数据、问题、实验、论文能对齐，不是单纯为了写作）
- 摘要（120 字以内）：AAAI4S（Automated Alignment AI4S）1.0 发布。研究者说清问题，AI 沿着可自由编排的 workflow 完成调研、实验与分析；平台记下每一步，让问题、实验、数据与结论前后对得上，每个数都能追溯到来处。
- 封面：待定（底图用平台现成的风景）
- 正文不带标题：公众号的标题单独一栏，`README.md` 从署名开始，整篇全选粘进 md.doocs.org 即可
- 外链：公众号正文不认外部链接，主人定直接贴网址：文末「相关链接」写「名称：网址」（纯文本，可复制），正文不挂链接；doocs 的「格式 → 外链转引用」保持关闭。发布时「原文链接」（阅读原文）可填平台代码仓库，这是公众号里唯一能点的外链
- 排版：md.doocs.org，「样式 → 自定义 CSS」先粘一次外层 `scripts/articles/2026-0929-first-release/doocs-custom.css`（行高带单位、表格可换行、去掉表格外层的滚动容器），否则公众号后台的内容结构检测报行高、溢出（2026-09-29 实测：粘前 7 张表在 343 px 宽下被撑出屏幕，粘后都正好 343 px）
- 日期：署名行里的日期写的是发稿日（现为 2026-09-29），实际发布日变了要改

## 口径（2026-09-29 与主人对齐）

- 读者：本科生、研究生；专业名词照讲
- 主题：天大新工科 AI 驱动的自动化科研；主打高度自由（workflow 编排决定全自动还是在哪停）与全学科适配（说能适配，不说都做过）
- 演练角色写「刚进组、连代码都不会跑的科研小白」（演练里研究者由 AI 扮演，维护者只修平台不喂答案）
- 装环境那段只写「缺包自己装好」
- 署名：黄素翔、李瑞彬；天津大学记忆与推理实验室；指导老师王征；只挂名，不写分工
- 不用 emoji；层次靠编号小标题、金句引用、每 500 字左右一张图或表
- 书面语，不用口语与口头禅（主人 2026-09-29）；小白的原话照录不改
- 重点尽量加粗：每段的关键句、关键数字、小白的原话；署名一行一项（行尾反斜杠硬换行），作者 / 实验室 / 指导老师 / 日期四个标签加粗
- 加粗照 CommonMark 写（主人用 md.doocs.org，底下是 markdown-it）：收尾的 `**` 前是标点、后面紧跟文字就不闭合，所以句末标点放在 `**` 外面、引号包在 `**` 外面（`“**原话。**”`）；`preview.py` 用同一套规则渲染，漏网的 `**` 直接报错
- 正文段落首行缩进两字（源文件里每段开头 `&emsp;&emsp;`，行首直接打全角空格会被 Markdown 吞掉）；标题、引用、列表、图、署名不缩进
- 公众号封面（订阅列表与分享卡片那张）待主人拍板，底图用平台现成的风景

## 开篇与第四节：GUA 复现

| 正文说法 | 出处 |
|---|---|
| 9 月 21 日 12:18 开口、15:43 签验收、只签两次字；原话「都听你的」（全句「级别和对上的标准都听你的」）、「命令行那些我搞不来」「时间就今天下午吧，钱别超过一百块」「重写一份吧，交给老师的东西别有错」 | [`docs/cases/gua-pinn-reproduction/README.md`](../../cases/gua-pinn-reproduction/README.md) 时间线；原话在同目录 `transcript.md` |
| 62.6% vs 62.2%、两行均值 ± 标准差、± 2σ 范围、每个种子 GUA 都更低 | 同上「论文值 vs 我们的值」两张表 |
| 官方代码一字未改（改动 0 处） | 同上时间线 15:25；`upstream.json` |
| 论文题目、2026-09-01、arXiv 2609.01558、Burgers 2-loss 表 8 | 同上「来源」行 |
| 建议先复现表 8 两行、问的四件事（为什么、第几级、怎么算对上、算力）、pdf 解析、摘要链接读仓库、compute add、镜像环境、download、79 个文件、种子 42–46 改 0–4、缺九个包、2 小时 40 分、第一版编了方程名、第二第三版被数字核对拦、第四版三关全过、提醒关 AutoDL | 同上时间线 |
| 答案卷：三个 AI 读者预筛、不喂给助理、逐项对上、19% 波动、跑满五个种子与三个种子的退路 | 同上「助理自己找到的 vs 预筛的答案卷」 |
| 均值高一成、torch 2.8 vs 2.12 | 同上「结论一句话」 |
| 四个问题来自需求模板、误差棒按论文的来自指南 | 内仓 `templates/reproduce.md`、`coordinator/README.md`「复现一篇论文」一节（所以正文「涌现」一段只列这两样之外的行为） |
| 公开记录页 | <https://zephyr4123.github.io/TJU-AI4Science/evals/2026-0921-gua-reproduction/>（2026-09-29 取到 200） |

## 第一节：为什么做

| 正文说法 | 出处 |
|---|---|
| 第一天的调研标题 | [`research/landscape/2026-0908-auto-research-agents/`](../../../research/landscape/2026-0908-auto-research-agents/README.md)；外层首个 commit 2026-09-08 |
| 三个项目读代码、「外层 for + 硬编码状态判断，差别在循环之外」 | [`research/selection/2026-0909-pipeline-frameworks/README.md`](../../../research/selection/2026-0909-pipeline-frameworks/README.md)「当前结论」 |
| 七个阶段、能力五栏、缺栏报错 | [`docs/architecture/README.md`](../../architecture/README.md) P-18 |
| 每个阶段一个主文件（`scoring.yaml`、`ledger.tsv` + `results.json`、`analysis.md`） | 同上 P-20 |

## 第二节：它是什么

| 正文说法 | 出处 |
|---|---|
| 项目、工作区、编辑台、设置；项目一位研究助理、编辑台一位流程助理 | 纲领 P-15、P-16、P-25；外层 README「产品一眼看」 |
| 产出记录读了谁、在哪台机器、哪家 agent | 纲领 P-19（`meta.yaml` 的 `from`、`compute`、`agent`） |
| 两条出厂 workflow 的阶段、能力、断点 | 内仓 `workflows/reproduce.yaml`、`workflows/research.yaml`；能力标题取自 `framework/capabilities/*/__init__.py` 的 `title` / `brief` |
| pdf skill：正文、图、公式、结构化表格与参考文献，二十页两秒、纯 CPU | 内仓 `skills/pdf/SKILL.md` |
| PEtab 领域包：pyPESTO、petab、libroadrunner，装载问题、算 NLL、多起点优化 | 内仓 `domains/petab/skills/petab/SKILL.md`、`docs/add-a-domain.md` |

## 第三节：设计原则

| 正文说法 | 出处 |
|---|---|
| 只有 `ai4sci` 一个入口、参数走 flag、配置归两份清单与环境变量、缺动作就加命令、三组前缀 | 纲领 P-14、P-23、P-25 |
| 能力 = Python 函数 + 薄 CLI，助理、页面后端、测试调同一个函数 | 纲领 P-12 |
| `compute add` 只要 ssh 一行与密钥路径、当场探测 Python / GPU / 磁盘 | [`docs/architecture/workflow.md`](../../architecture/workflow.md) §5「算力适配」 |
| 不手搓 agent、`Runner` / `Chat` 两个端口一家一个适配器、两层可分开选 | 纲领 P-11、P-25；workflow.md §5「执行层适配」「协调层适配」 |
| DeepSeek Harness 2026-08-13 开源、一切皆插件（模型适配、工具注册、会话日志、agent 循环） | [The New Stack](https://thenewstack.io/deepseek-harness-open-source-plugins/)、[orcarouter](https://www.orcarouter.ai/blog/dsh-deepseek-harness-release-date)（2026-09-29 查）；「借鉴了这个思想」是主人口述，仓库文档里没有引用记录 |
| 框架不调用模型 | 纲领 P-1 |
| 步骤与 skill 两个 tag、agentskills.io、框架注入清单 | 纲领 P-22 |
| autoresearch：git 状态、5 分钟、`val_bpb`、`git reset`、比大小与回滚与记账全由 agent 做 | [`research/selection/2026-0909-pipeline-frameworks/autoresearch.md`](../../../research/selection/2026-0909-pipeline-frameworks/autoresearch.md)「结论先行」 |
| 平台的拆法：harness 由框架注入、SHA256 锁死；AutoResearch 里比较、统计门、回滚、记账归框架 | 纲领 P-6；workflow.md §2 |
| 断点可有可无、一个不放就是端到端、实例可改参数增删步骤、需求确认是唯一内置的门 | 纲领 P-15、P-19；内仓 `workflows/research.yaml` 文件头 |
| 状态在磁盘、被杀后从磁盘续 | 纲领 P-3 |
| 可追溯一节：产出记录读了谁（带 hash）、哪版需求、哪台机器、哪家 agent；被引用或签字即冻结 | 纲领 P-19（`meta.yaml` 的 `from`、`compute`、`agent`） |
| 可追溯一节：数字核对不经模型，数据表每行回溯到结果文件、正文里带小数点或指数的数必须在表里、账本与 git 对账 | 内仓 `framework/capabilities/verify/__init__.py` 的 `does` |
| 框架不随课题改、领域包按目录发现、按工具链命名、「九个参数最小化一个标量」 | 纲领 P-5；内仓 `docs/add-a-domain.md` |
| 需求模板：通用、AI、计算机、材料、复现 | 内仓 `templates/` 目录 |

## 第五节：十六天

| 正文说法 | 出处 |
|---|---|
| 各版本日期与要点 | 各 tag 所在提交的日期（`git log -1 <tag>`）：两仓 v0.1.0 09-08（内仓的 GitHub 发布页 09-10 才建）、内仓 v0.2.0 09-17、两仓 v1.0.0 与 v1.0.1 09-23；要点取自内仓 `CHANGELOG.md` 各版本小节 |
| 09-10 九条原则、原则到 P-25 | 纲领「变更记录」 |
| 09-20 第一轮真任务、09-22 Codex 全面适配 | 纲领「变更记录」；`docs/cases/` |
| 1.0.1 流程库分两层 | 两仓 `CHANGELOG.md` [1.0.1]（#149） |
| 1.0.0 起承诺兼容 | `CONTRIBUTING.md`「版本与发布」、ADR-0004 |
| 两个仓库 320 次提交、146 条 issue | `git log origin/main --no-merges`（两仓，2026-09-08 至 09-23，按作者日期）；`gh issue list --search "created:<2026-09-24"`（外层，2026-09-29 取） |
| 安装命令、`http://127.0.0.1:8765`、`make up` | 内仓 `README.md`「怎么跑」；v1.0.1 Release 资产里有 `ai4sci-1.0.1-py3-none-any.whl`（2026-09-29 查） |

## 第六节：下一步

| 正文说法 | 出处 |
|---|---|
| 接更多 coding agent | 主人 2026-09-29 口述；分工纪要 [`docs/meetings/2026-0923-division-of-labor.md`](../../meetings/2026-0923-division-of-labor.md) 方向 5 |
| 18 个项目、13 个代码级深读、六类能力 | [`research/selection/2026-0927-scientific-ai-capabilities/`](../../../research/selection/2026-0927-scientific-ai-capabilities/README.md)（#151，PR #192 未合并时这个链接在 release/1.1 上还不存在） |
| Windows、评测 | 分工纪要方向 2、方向 4 |

## 配图

图不进仓库：出图落本机 `materials/articles/2026-0929-first-release/figures/`（gitignore），`upload.py` 传到腾讯云 COS，经 CDN `media.zephyrxiang.com` 分发，正文直接引 URL。桶里按类型分目录：`ai4science/articles/2026-0929-first-release/{screenshots,charts,diagrams}/<名>.<内容哈希前 8 位>.png`，内容变了 URL 跟着变（CDN 缓存 immutable）；本机文件名与 URL 的对照在 `figures.json`。出图脚本在外层 `scripts/articles/2026-0929-first-release/`，改图改脚本再重出、再跑 `upload.py`（会删掉桶里本篇前缀下的旧版本、换正文里的链接），不手改 PNG。示意图与数据图用白底（公众号正文是白底；不做透明，深色模式下透明底上的深色字看不清）。看手机上的实际比例：`preview.py` 把正文排成公众号那一栏的宽度（375 px，`?w=580` 看电脑版），写到 `materials/`，不进 git。尺寸约定：手机上一张图不超过大半屏（约 550 px 高），横幅是一行横排。

| 文件（本机名，URL 见 figures.json） | 是什么 | 怎么出 |
|---|---|---|
| `ui-*.png` | 真实界面：首页、项目页、工作区看板、演练原始对话四段（开头、结果、重写、收尾）、编辑台流程库、两条出厂流程的画布、能力库、设置页的 AI 一栏（两家 agent 与 9/23 那次自检的状态；算力一栏有主机地址，不截） | `capture-ui.js`：数据根只放 GUA 项目的副本，起 `ai4sci serve --port 8766`，playwright 2 倍清晰度截图；对话取自 GUA 演练的原始会话（`我有一篇论文 … 9/21 12:18 · 15 轮`） |
| `chart-gua-timeline.png` | GUA 三小时二十五分的时间轴，人一侧、AI 一侧 | `charts.py`；时刻取自案例卡时间线，需求确认 12:25 取自工作区 `requirement.lock` |
| `chart-gua-results.png` | 论文值、论文 ± 2σ、五个种子、复现均值 | `charts.py`；数取自案例卡两张表 |
| `chart-sixteen-days.png` | 十六天每天的提交数与关键节点 | `charts.py`；数取自上表 git log |
| `fig-*.png` | 示意图：横幅、借鉴表、七阶段与五栏、产品结构、两条 workflow、CLI、三层、拆 autoresearch、自由度、领域包、答案卷、能力覆盖 | `diagrams.html` 经 `diagrams.py` 换进 Phosphor 图标与平台的标，本地起 http 服务，`capture-diagrams.js` 3 倍清晰度逐张截；配色照内仓 `docs/DESIGN.md`；横幅底图是平台 CDN 上的 `studio-dawn-2000.jpg` |
| `fig-stages.png` 里的五栏 | 能力「原码复现基线」的描述符 | 内仓 `framework/capabilities/reproduction/__init__.py` 的 `does` / `does_not` / `brings` / `leaves` / `stops`，压缩改写 |
| `fig-cli.png` 里的终端 | `ai4sci --help` 的子命令说明，逐字摘 7 条 | 内仓 v1.0.1 的 `.venv/bin/ai4sci --help` |

