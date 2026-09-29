# AI4Science：可编排、可追溯的自动化科研

**作者**：黄素翔、李瑞彬\
**实验室**：天津大学记忆与推理实验室\
**指导老师**：王征\
**日期**：2026 年 9 月 29 日

![](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/diagrams/logo.fc39622e.png)

&emsp;&emsp;2026 年 9 月 21 日 12 时 18 分，**一位刚刚进组、连代码都还不会运行的“科研小白”**，在对话框中输入了一句话：

> “我有一篇论文……你帮我复现一下。”

&emsp;&emsp;随后附上了论文链接。被问及复现到什么程度、以什么标准判定对上时，他答道：“**都听你的。**”他也坦言：“**命令行那些我搞不来。**”对于时间与经费，他给出的约束是：“时间就今天下午吧，钱别超过一百块。”

![演练的原始对话：一句话与一个链接之后，助理自行解析论文、联网查阅代码仓库、撰写需求](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/screenshots/chat-open.047da6a8.png)

&emsp;&emsp;当天 15 时 43 分，他完成了验收签字。**论文报告的新方法使误差降低 62.6%，平台的复现结果为 62.2%**；五个随机种子的结果均落在论文给出的误差范围之内，**论文作者的官方代码未作任何改动**。

&emsp;&emsp;**在这三个半小时里，他仅签字两次。**

&emsp;&emsp;这是 AI4Science 的一次演练。AI4Science 是我们在天津大学新工科背景下搭建的 **AI 驱动的自动化科研平台**：一项研究经过哪些步骤、在哪里停下来由人把关，**可以自由编排**；从提出问题到得出结论，**每一步都有据可查**。9 月 23 日，平台发布 1.0 版本。

## 01 为什么要做这个平台

&emsp;&emsp;新工科是交叉学科。研究者来自化学、化工、材料、物理、生物等不同领域，各自带着具体的科学问题，但其中多数人并非工程师。

&emsp;&emsp;在 AI 一侧，过去一年发生了显著的变化。以 Claude Code、Codex 为代表的 coding agent，已经能够读懂陌生的代码仓库，编写代码、运行程序、分析日志并自行修复错误。**仅就编写代码而言，模型的能力已经相当成熟。**

&emsp;&emsp;**真正欠缺的，是将科研活动组织起来的那一层。**

&emsp;&emsp;目前借助 AI 开展科研，**常见的做法处于两个极端**：其一是在对话框中逐问逐答，每一步都需要人工跟进、搬运结果并决定下一步；其二是端到端的自动化流水线（pipeline），从选题直至成文一次运行到底，过程中无法介入，流程也难以调整，一旦偏离方向只能从头再来。

| | 对话框逐问逐答 | 端到端流水线 | AI4Science |
|---|---|---|---|
| 人的参与 | 每一步都要人跟进 | 过程中无法介入 | 只在自己设置的断点处确认 |
| 流程调整 | 随时可调，全靠人推进 | 固定，难以调整 | workflow 自由编排 |
| 结论追溯 | 依赖人工整理 | 视具体实现而定 | 每一步有记录，每个数可回溯 |

&emsp;&emsp;项目启动的第一天，我们完成了第一篇调研《新工科自动化科研智能体：2026 年工业界现状与架构设计》。次日，我们克隆了几个具有代表性的开源项目，逐行阅读其代码。

![站在前人的肩膀上：所读项目各自的长处，以及它们在本平台中的落点](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/diagrams/borrow.2404c8d6.png)

&emsp;&emsp;通读之后，我们得出一个结论：这些项目的编排形态大同小异，都是“外层一个 for 循环，加上硬编码的状态判断”；**真正的差别在循环之外**，即以什么承载状态、以什么规则判断收敛、以什么机器判据防止模型造假。

&emsp;&emsp;这一结论成为整个平台的出发点。我们的回答是：

> 首先，把科研的边界划分清楚。

&emsp;&emsp;**平台将科研划分为七个阶段**：文献、假设、设计、实验、分析、写作、验证。每个阶段包含若干能力，每个能力都必须写明五项内容：职责、边界、输入、产出与终止条件，**缺少任何一项，平台在加载时即报错**。每个阶段只向下游交付一个主文件。

![七个阶段，以及一个能力必须写明的五项内容](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/diagrams/stages.7bc42016.png)

&emsp;&emsp;边界清晰之后，**AI 在每一个环节面对的都是确定的问题**：输入是什么，应当交付什么，做到何处为止。它不会在模糊的大目标中反复试探，给出的也是确定的解；而在边界之内，**如何完成则由它自主决定**。后文将会看到，那位科研小白的复现之所以能够全自动完成，正是得益于此。

&emsp;&emsp;边界之外，还需要一条贯穿始终的线索。研究问题写进经人确认的需求，实验依照锁定的评测运行，数据由平台逐轮记账，分析中的每一个数都能回溯到产生它的结果文件。**问题、实验、数据与结论前后对得上，结论才站得住**。在我们看来，自动化科研的价值不在于更快地写出一篇论文，**而在于让每一个结论都经得起追问**。

## 02 平台是什么

&emsp;&emsp;概括而言：研究者在网页上向 AI 助理说明研究意图，助理依照一条 workflow 推进研究，**人只在自己希望暂停的环节审阅并签字**。

&emsp;&emsp;平台面向各学科的研究者，不要求使用者具备编程能力。其中的分工十分清晰：**人确定方向，AI 执行工作，平台负责组织科研过程并记录每一个步骤**。

![平台的构成](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/diagrams/product.f0d2db0b.png)

&emsp;&emsp;平台中的几个核心概念如下：

| 概念 | 对应什么 | 说明 |
|---|---|---|
| **项目** | 一个课题 | 配备一位研究助理，掌握课题的来龙去脉 |
| **工作区** | 一项具体需求 | 从一条 workflow 开始，产出按阶段存档，来源全程记录 |
| **workflow** | 一条研究路线 | 规定经过哪些阶段、调用哪些能力、在何处设断点 |
| **能力** | 一个研究动作 | 分“步骤”与“skill”两类，存放在能力库中 |
| **编辑台** | 流程库与能力库 | 流程助理通过对话组合出新的 workflow |
| **设置** | AI 与计算资源 | 选用哪家 AI、在哪台机器上运行 |

&emsp;&emsp;打开平台，首页是项目墙。

![首页：项目墙](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/screenshots/home.9a879c58.png)

&emsp;&emsp;进入一个项目，正中是与研究助理对话的入口。助理**掌握课题的来龙去脉**：已经完成了什么、目前停在何处、下一步应当做什么。

![项目页：中央是与研究助理对话的入口，下方列出该课题的各个工作区](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/screenshots/project.6c2b594b.png)

&emsp;&emsp;编辑台存放流程库与能力库。平台内置若干条 workflow，用户也可以与流程助理对话，**由它将能力组合成新的 workflow**，保存到个人的流程库中。

![编辑台的流程库：两条内置流程与一条用户自存的流程](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/screenshots/studio-library.8e08817c.png)

&emsp;&emsp;**其中最关键的是 workflow**。科研首先需要方向。一条 workflow 规定了本次研究经过哪些阶段、以何种顺序、每个阶段调用哪些能力、在何处暂停等待人工确认。**方向确定之后，AI 才知道应当朝哪里推进。**

&emsp;&emsp;流程库目前内置两条 workflow：论文复现（reproduce）与从设计到验证（research）。

![两条内置 workflow：各自经过的阶段、调用的能力与需要人工签字的断点](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/diagrams/workflows.49c2af11.png)

&emsp;&emsp;在编辑台的画布上，“论文复现”的形态如下：

![编辑台中的“论文复现”：文献阶段挂载两个 skill，设计阶段调用原码复现基线，两个橙色断点等待人工签字](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/screenshots/studio-reproduce.3dfa46a2.png)

&emsp;&emsp;workflow 由能力组合而成，能力存放在能力库中。以两个能力为例：pdf 这一 skill 可以将论文解析为正文、图片、公式以及结构化的表格与参考文献，**一篇二十页的论文仅用 CPU 约两秒即可完成解析**；PEtab 参数估计领域包则集成了系统生物学中常用的参数估计工具链（pyPESTO、petab、libroadrunner），能够载入 PEtab 问题、计算负对数似然并执行多起点优化。

![能力库：按阶段排列，skill 单独成栏](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/screenshots/studio-caps.95f56281.png)

## 03 设计原则

### CLI 是第一性原则

&emsp;&emsp;如果说大模型是 AI 的大脑，那么 **CLI 就是 AI 接触真实世界的钥匙，相当于为 AI 装上了双手**。

&emsp;&emsp;**平台只有一个入口：`ai4sci`**。每一项操作都是它的一条子命令，参数一律通过 flag 传递。例如，运行一个能力使用 `ai4sci cap`，查询项目状态使用 `ai4sci show`，接入一台机器使用 `ai4sci compute add`。开篇那段对话中，助理逐条调用的正是这些命令。

![CLI：三种角色对应三组命令前缀；每个能力是一个 Python 函数；具体使用什么资源由配置决定](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/diagrams/cli.f43f4a4f.png)

&emsp;&emsp;这一设计带来两方面的好处。**其一，AI 可以直接操作**。命令的输入与输出都十分明确，AI 能够准确理解和调用；每个能力本质上是一个 Python 函数加一层很薄的 CLI 封装，助理通过命令行调用，网页后端与测试直接调用同一个函数，**三者的行为完全一致**。**其二，封装之后，底层转为配置驱动**。使用哪个模型、在哪台机器上运行，记录在每位用户自己的 `agents.yaml` 与 `computes.yaml` 中；命令只描述“做什么”，配置只描述“用什么做”，二者互不干扰。

&emsp;&emsp;**命令同时也是权限的边界**：

| 角色 | 可用命令 | 职责 |
|---|---|---|
| 研究助理 | `ai4sci` 全部命令 | 在项目中推进研究 |
| 流程助理 | `ai4sci show`、`ai4sci workflow` | 在编辑台组合 workflow |
| 执行层 agent | `ai4sci skill` | 编写代码、调用工具包 |

&emsp;&emsp;缺少某项操作时，我们的做法是新增一条命令，**而不是向 AI 开放任意命令的执行权限**。

&emsp;&emsp;算力正是通过这套命令接入的。助理执行 `ai4sci compute add`，**用户只需提供 ssh 连接信息与密钥路径**，平台即当场完成探测：能否连通、是否具备 Python、GPU 型号以及剩余磁盘空间。此后，代码上传、远程任务启动与结果回传，均由这套命令完成。

### 站在巨人的肩膀上

&emsp;&emsp;平台支持主流的 coding agent，目前已接入 Claude Code 与 Codex；**我们不自行开发 agent**。

![设置页：Claude Code 与 Codex 均已接入并通过自检；研究助理与执行层可以分别选用，模型与推理深度各自可调](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/screenshots/settings-agents.f44af33f.png)

&emsp;&emsp;**理由在于专业分工**。一个成熟的 coding agent 凝聚了大量的工程积累，工具调用、上下文管理、沙箱与权限控制，每一项都颇具难度，而最成熟的团队已经将其做到了很高的水准。**我们专注于其上的那一层。**

![三层架构：模型、agent harness 与科研层](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/diagrams/layers.cdee11d1.png)

&emsp;&emsp;DeepSeek 于 8 月开源的 DeepSeek Harness 提出了一个出色的思想：一切能力皆为插件，模型适配、工具注册、会话日志乃至 agent 循环本身都可以替换。我们借鉴了这一思想，并将其上移一层：在本平台中，**整个 coding agent 本身就是一个插件**。平台为执行与对话分别定义了端口（`Runner` 与 `Chat`），每接入一家 agent，只需编写一个适配器；助理与执行层可以选用不同的 agent，**切换只需修改一行配置**。

&emsp;&emsp;在 coding agent 之上，能力、算力与界面同样以插件形式存在。此外还有一条约定：**平台框架本身不调用任何模型**。编写代码、阅读文献、起草分析交由 agent 完成；组织流程、记录过程、判定结果，则由不调用模型的确定性代码完成。

### 像搭积木一样组织科研

&emsp;&emsp;平台采用三层结构：研究阶段、能力、实现。能力分为“步骤”与“skill”两类。流程运行到某个步骤时，平台为其建立一个编号的产出目录，需要编写代码时启动一个执行层会话，产出可以由人签字确认；skill 则是即取即用的工具，可以挂载在任意阶段。skill 遵循 agentskills.io 开放规范编写，由框架自行将清单注入 agent，因此**同一个 skill 可以在不同的 agent 上直接使用**。

&emsp;&emsp;下面以 Karpathy 的 autoresearch 为例，说明“积木”的含义。

&emsp;&emsp;autoresearch 的核心是一个 ratchet（棘轮）循环：agent 修改代码，进行一次固定时长 5 分钟的训练，观察验证集指标 `val_bpb` 是否改善；若改善则保留本次提交，否则通过 `git reset` 回退。由于状态保存在 git 中，agent 的上下文可以随时清空、更换会话，已经取得的进展不会丢失。这一机制之所以成立，**依赖于一个 5 分钟内必然结束、只输出单一标量的固定评测**；运行实验、比较优劣、执行回退与记录账本，均由 agent 自己完成。

&emsp;&emsp;在本平台中，这套机制被拆分为两部分。

![把 autoresearch 拆成两块积木](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/diagrams/autoresearch.68b8fb4e.png)

&emsp;&emsp;固定评测部分移至设计阶段：执行层编写启动脚本与评测脚本，平台以 SHA256 将其封装为只读的 harness，研究者签字确认评分标准之后，**agent 便无法再作修改**。ratchet 循环部分移至实验阶段，成为名为 AutoResearch 的能力：agent 只负责修改代码，运行实验、与当前最优结果比较、判断改进是否超过统计门限、保留或回退以及记录账本，**全部由平台完成**。

&emsp;&emsp;拆分之后，**它成为一块积木**，既可以与文献、分析、验证等阶段组合为完整的研究流程，也可以替换为其他实验能力。

![编辑台中的“从设计到验证”：AutoResearch 是画布上的一个模块](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/screenshots/studio-research.145b6f9d.png)

> 它由更小的部件构成，自身又可以作为部件参与更大的组合：下限由平台的规则保障，上限取决于如何组合。

### 可编排：高度自由

&emsp;&emsp;**自由度由 workflow 的编排决定。**

![同一组阶段，断点的数量与位置由用户决定](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/diagrams/freedom.01bc0827.png)

&emsp;&emsp;在编辑台上，用户可以决定经过哪些阶段、以何种顺序、每个阶段调用哪些能力，以及在何处设置断点。**若希望全自动运行，可以不设任何断点；若希望逐步审阅，可以在每一步之后设置断点**。取入工作区的 workflow 还可以继续调整参数、增删步骤。开工之前，**人只需确认一次需求以明确方向**；此后如何推进，由 workflow 决定。

&emsp;&emsp;**流程也可以随时暂停**。平台的全部状态都保存在磁盘上，而非会话之中：代码由 git 管理，每一轮尝试记入账本，每一次产出保存在独立的目录中。即使会话关闭或进程中断，**重启之后也能从磁盘上的状态继续运行**。

### 可追溯：每一个数都有来处

&emsp;&emsp;自动化程度越高，越需要回答一个朴素的问题：这个结论从何而来。**平台对此的回答写在机制里，而不是写在提示词里**。

&emsp;&emsp;每一次产出都在自己的目录中留下一份记录：

| 记录项 | 内容 |
|---|---|
| 上游产出 | 读取了哪些产出，连同其哈希值 |
| 需求版本 | 依据的是哪一版经人确认的需求 |
| 运行位置 | 在哪台机器上运行 |
| 执行者 | 由哪家 AI 完成 |
| 确认状态 | 是否经人签字 |

&emsp;&emsp;**产出一旦被下游引用或经人签字，便即冻结**，不再改动；此后任何人都可以沿着这条记录，**从结论一路回到最初的问题**。

&emsp;&emsp;**判定则交给不调用模型的代码**。评测脚本由平台封装、agent 无法改动；验证阶段的“数字核对”将分析中数据表的每一行回溯到对应那一轮的结果文件，正文中出现的每一个带小数的数字都必须在表中有据，实验账本也要与 git 历史逐条对账，**任何一项对不上即判为不通过**。开篇那位科研小白的分析被拦下两次，拦下它的正是这道检查。

&emsp;&emsp;问题、实验、数据与结论由此首尾相接。写作只是最后一环；**前面每一环都站得住，最后写出的论文才站得住**。

### 全学科适配

&emsp;&emsp;平台没有针对任何学科作特殊处理，**框架不随课题而改变**。

![全学科适配：新增一个领域包，无需修改框架](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/diagrams/domains.46a408a9.png)

&emsp;&emsp;接入一个新学科，**只需向平台添加一个领域包**：一个目录，包含一份描述文件以及该领域的约定与 skill，**无需改动框架的任何代码**。领域包按工具链与任务类型命名，而不按学科命名，因为平台关注的是问题的形态，例如“九个参数，最小化一个标量”；学科信息则写在需求之中。平台也按领域准备了相应的需求模板。

&emsp;&emsp;化学、化工、材料、物理、生物等学科，**使用的是同一个平台**。GUA 的复现，正是在物理方向上已经跑通的一条路径。

## 04 实战：科研小白全自动复现 GUA

&emsp;&emsp;回到开篇的那位科研小白。

&emsp;&emsp;他要复现的论文是 9 月 1 日刚刚发布于 arXiv 的《Gradient–Update Mismatch: Rethinking Conflict-Free Training of Physics-Informed Neural Networks》，研究的是用物理信息神经网络（PINN）求解偏微分方程时的训练问题。论文提出的 GUA 方法，在 Burgers 方程上**将 ConFIG 方法的误差进一步降低了六成以上**。

&emsp;&emsp;**他只发送了一句话和一个链接，此后的工作全部由助理自主完成。**

![3 小时 25 分：左侧为人的操作，右侧为 AI 的操作](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/charts/gua-timeline.47a9dfdd.png)

&emsp;&emsp;**12:19**，助理在需求模板中找到“论文复现”，调用 pdf skill 将论文解析为文本与结构化表格，定位到需要复现的表格与训练设置；随后根据摘要中的链接，**联网查阅了代码仓库**。接着，它撰写了需求初稿，建议优先复现论文附录表 8 中 Burgers 方程的两行结果，并**向小白确认四个问题**：复现的目的、复现的级别、判定对上的标准，以及是否有可用的 GPU 机器。

&emsp;&emsp;**12:25**，小白回复“级别和对上的标准都听你的”，并提供了一台租用的 AutoDL 服务器的 ssh 地址。**助理通过 `compute add` 接入这台 RTX 4090**，决定直接使用镜像自带的环境，并补全了需求。小白确认需求。

&emsp;&emsp;**12:26**，助理从流程库中取出“论文复现”这条 workflow，通过 download 拉取官方代码并记录 commit，撰写材料清单，随后将复现任务提交到这台 4090 上后台运行。

&emsp;&emsp;执行层的 coding agent 阅读了仓库中的 79 个文件，编写了启动脚本、评测脚本与评分契约。助理在检查时发现，**草稿中的随机种子被写成 42 至 46，而论文使用的是 0 至 4**，于是将修改意见反馈给执行层，由其修订出第二版。

&emsp;&emsp;**12:35**，任务在 4090 上启动后随即报错：服务器环境缺少 scipy 等九个依赖包。**助理在算力服务器上一次性补齐了全部依赖**，任务随之继续运行。

&emsp;&emsp;**12:46 至 15:25**，五个随机种子、两种方法，**在 4090 上连续运行了 2 小时 40 分钟**。

&emsp;&emsp;**15:25**，助理将论文值与复现值并列呈现，逐一列出每个种子的结果以及**对原作者代码的改动（0 处）**，并在断点处请小白核对。小白签字确认。

![运行结束后，助理将论文值与复现值并列呈现，并在断点处请人签字](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/screenshots/chat-result.133de065.png)

&emsp;&emsp;随后，助理开始撰写复现性分析。第一版通过了数字核对，但助理在通读时发现，**文中出现了一个论文中并不存在的方程名称**，于是将问题连同两个选项交给小白：按此版本验收，或重写一版后再次核对。小白回复：“**重写一份吧，交给老师的东西别有错。**”重写的第二版与第三版先后被数字核对拦下：一次是正文中直接写出的超参数在结果文件中找不到出处，一次是“1.84 倍”的表述无法回溯。**第四版三项检查全部通过**。

![分析的重写：未通过数字核对的版本，在对话中标记为“出错”](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/screenshots/chat-rewrite.385f4c12.png)

&emsp;&emsp;**15:43**，**小白签字验收**。助理最后提醒：AutoDL 上的机器仍在按小时计费，请及时在控制台关机。

![工作区看板：论文复现流程的每个环节与每次产出，已签字的与未通过的均完整保留](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/screenshots/workspace-board.1b351e34.png)

&emsp;&emsp;最终结果如下：

![复现结果：两行结果均落在论文的误差范围之内](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/charts/gua-results.8604c2ab.png)

| 方法 | 论文（均值 ± 标准差） | 复现（均值 ± 标准差） | 落在论文 ± 2σ 内 |
|---|---|---|---|
| ConFIG | 1.74e-3 ± 3.38e-4 | 1.94e-3 ± 3.3e-4 | 是 |
| ConFIG + GUA | 6.50e-4 ± 1.27e-4 | 7.33e-4 ± 1.8e-4 | 是 |
| 误差降幅 | 62.6% | **62.2%** | 方向一致 |

&emsp;&emsp;在每一个随机种子上，**引入 GUA 后误差均有所下降，没有出现反例**。两组均值都比论文略高约一成，助理在分析中给出了最可能的原因：服务器镜像中的 torch 版本为 2.8，而论文使用的是 2.12，下一步可以仅替换这一项进行验证。

&emsp;&emsp;另有一处细节值得一提。在选定这篇论文之前，我们另外安排了三个 AI 读者对材料进行事先核实，整理成一份“答案卷”，**且未向助理提供**。事后比对的结果如下：

![助理独立得出的结论与答案卷逐项一致](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/diagrams/answer.659849f8.png)

&emsp;&emsp;**平台提供给助理的，是方向与工具**。workflow 规定了本次任务是复现，需要经过文献、设计、分析、验证等阶段，并在何处暂停等待签字；平台的命令则提供了每一步可用的工具。然而，**并没有任何脚本规定它先做什么、后做什么、遇到问题如何处理**。从摘要中的链接追溯到代码仓库，从论文的众多表格中选出应当复现的一行，发现执行层写错的随机种子，在服务器上自行补齐环境，通读分析时识别出凭空出现的方程名称，验收之后提醒关机以节省费用：这些都是它在既定边界之内、针对具体情境作出的自主决策。

> 这正是我们所说的涌现：方向由人通过 workflow 给定，路径由 AI 自主走出。

![验收之后，助理说明了各项交付物的位置，并提醒及时关机](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/screenshots/chat-end.ad66e8f3.png)

&emsp;&emsp;完整的对话记录、每一次产出与签字均已公开，见 [GUA 论文复现的公开记录](https://zephyr4123.github.io/TJU-AI4Science/evals/2026-0921-gua-reproduction/)。

## 05 十六天，从 0.1 到 1.0

![十六天：每日提交数与关键节点](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/charts/sixteen-days.c1b74e77.png)

&emsp;&emsp;9 月 8 日，第一篇调研完成；**9 月 23 日，1.0.0 版本发布**。各版本如下：

| 版本 | 日期 | 要点 |
|---|---|---|
| v0.1.0 | 9 月 8 日 | 项目骨架与发布流水线 |
| v0.2.0 | 9 月 17 日 | 工作区与两位助理分权 |
| v1.0.0 | 9 月 23 日 | 首个正式版本：项目层、Codex 全面适配、自检与设置 |
| v1.0.1 | 9 月 23 日 | 流程库分为内置与用户自存两层，自行编排的 workflow 升级后不丢失 |


&emsp;&emsp;**这个平台本身，也是人与 AI 协作完成的**。十六天里，**两个仓库共计 320 次提交、146 条 issue**。每一项工作都先建立 issue，先对齐需求与边界，再动手实施，过程中的发现、证据与决策随时记录在 issue 中。设计原则从最初的九条增加到二十五条，每一条都写明了检验其是否被遵守的方法，凡能交由机器检查的，均已纳入自动检查。每次合并之前，同一套检查都会在本地与 CI 上各执行一遍。

&emsp;&emsp;自 1.0.0 起，**平台承诺向后兼容**。**平台完全开源**：

- [平台代码仓库：TJU-AI4Science-Platform](https://github.com/zephyr4123/TJU-AI4Science-Platform)
- [项目文档、调研与案例：TJU-AI4Science](https://github.com/zephyr4123/TJU-AI4Science)

&emsp;&emsp;如仅需使用，准备好 uv 以及一家已登录的 coding agent（Claude Code 或 Codex），执行以下两行命令即可：

```bash
uv tool install https://github.com/zephyr4123/TJU-AI4Science-Platform/releases/download/v1.0.1/ai4sci-1.0.1-py3-none-any.whl
ai4sci serve
```

&emsp;&emsp;随后在浏览器中打开 `http://127.0.0.1:8765`。如需参与开发，克隆仓库后执行 `make up`，即可一键启动完整环境。

## 06 下一步

| 方向 | 内容 |
|---|---|
| **接入更多 coding agent** | 成熟的商用产品与可搭配第三方模型 API 的开源 agent 都将陆续接入；端口已经预留，每接入一家只需新增一个适配器 |
| **补齐三个阶段的能力** | 文献、假设、写作；已调研 18 个开源科研 AI 项目，对其中 13 个进行了代码级深读，将择优接入 |
| **Windows 支持与评测体系** | 让更多用户能够顺利安装，也使平台的能力可以被量化比较 |

![七个阶段的能力覆盖情况，以及已调研能力对应的补充方向](https://media.zephyrxiang.com/ai4science/articles/2026-0929-first-release/diagrams/coverage.234eddda.png)

&emsp;&emsp;最后，欢迎各学科的同学与老师试用。**只要有一个科研问题，就可以从这里开始。**

&emsp;&emsp;那位科研小白在 15 时 43 分签字之后，平台留下了一条完整、可追溯的记录：他说过的每一句话，助理作出的每一个决定，服务器上计算出的每一个数字。下一次，他可以换一篇论文，也可以调整这条 workflow，开展自己的课题。

&emsp;&emsp;**让自动化的科研依然实事求是，这是 AI4Science 想做的事。**

## 相关链接

- [平台代码仓库：TJU-AI4Science-Platform](https://github.com/zephyr4123/TJU-AI4Science-Platform)
- [1.0.1 版本发布页与安装包](https://github.com/zephyr4123/TJU-AI4Science-Platform/releases/tag/v1.0.1)
- [项目文档、调研与案例：TJU-AI4Science](https://github.com/zephyr4123/TJU-AI4Science)
- [GUA 论文复现的公开记录](https://zephyr4123.github.io/TJU-AI4Science/evals/2026-0921-gua-reproduction/)
- [第一篇调研：新工科自动化科研智能体](https://zephyr4123.github.io/TJU-AI4Science/landscape/2026-0908-auto-research-agents/)
- [论文：Gradient–Update Mismatch（arXiv 2609.01558）](https://arxiv.org/abs/2609.01558)
- [karpathy/autoresearch](https://github.com/karpathy/autoresearch)
- [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)
