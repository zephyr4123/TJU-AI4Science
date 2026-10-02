---
title: BootLoops 调研：工具包、工作协议与公开说法
subtitle: Matthew D. Schwartz 2026-10-01 开源的大模型定量科学工具包与 12 个工作协议 skill；读三个仓库的文档、本机实跑自检，对照平台收录门槛逐条核对
kind: 开源项目调研（代码级，本机实跑自检）
date: 2026-10-02
scope: 仓库 BootLoops-ai/bootloops 提交 66b680c（读 README、INSTALL 与 49 份 GUIDE）、BootLoops-ai/skills 提交 ca89227（12 个 SKILL.md 读全文）、BootLoops-ai/jackandjill 提交 e0ccb07（读契约文档）；原文 Claude-shaped science、前作 Vibe Physics、总论文 BootLoops.pdf 读全文，bootloops.ai 读首页与 harness、papers、summaries、amplitudes、contact 各页；Kira、Blade、AMFlow.cpp 三个引擎分叉没有克隆，只看了 bootloops README 里的介绍。文中 bootloops/、skills/、jackandjill/ 开头的路径相对各自仓库根，platform/ 与 docs/ 开头的相对本外层仓根
status: 已结论（2026-10-02）：不收录任何代码或 skill，调研存档备查
---

> **结论（2026-10-02）**：不收录 BootLoops 的任何代码或 skill，调研存档备查。
>
> BootLoops 由两部分组成：一个以费曼积分、散射振幅为主的计算工具包（49 个包里 34 个服务理论物理与数学物理），和 12 个纯文字的工作协议 skill；另有单独发布的系统发育证据包 JaCKandJill。工具包每个包有写给 agent 的说明页、验证等级和一条固定的自检命令，本机 macOS 92.7 s 跑完全部 49 个包的自检，42 个通过、3 个按设计拒跑、4 个失败；协议 skill 把盲分析、预注册、交叉验证、变异测试这些既有做法写成步骤、按机制命名的失败模式与复选清单；JaCKandJill 给每个数标明声明强度并附可机器核对的证书。局限：工具包的学科集中在理论物理；部分包依赖的十余种外部程序多为 GPL，三个引擎分叉要从源码编译，官方只在 Linux 上做发布测试；自检汇总不区分跳过，42 个通过里至少 23 个含跳过的子项；研究 skill 对效果的说法没有附运行记录，三个仓里也没有它们的产出样例；JaCKandJill 的精确值只覆盖四类群的短比对，默认验证模式不重算 40 列以上的精确值；查询时距博客发布约 15 小时，没有外部 issue 或复现。
>
> 公开说法方面，博客里的手稿数、合著者数、积分数与经济学、语言学两项的数字都能在网站或 NBER 页面上对上，领域数在三处材料里不一致；原文披露了利益关系，也写明了多条局限（多数科学问题做不了、概念工作要人做、手稿多由模型起草且部分未经人完整核对）。口径上的出入：36 条手稿里 7 条还没有稿，有稿的除 1 篇 NBER 工作论文外页面上没有期刊、arXiv 或 DOI 链接；「与模型无关」是设计主张，没有其他模型驱动的实测。一篇中文转载把手稿称作「成果」、把 30 个积分说成都是椭圆积分、点名千问和 DeepSeek 可以直接适配，这几处与原文不符；它称「凌晨 Anthropic 分享」，原文是发在 Anthropic 网站上的客座文章，发布于北京时间 22:02，并写明 BootLoops 不是 Anthropic 的项目。
>
> 不收录的原因：skill 正文是 CC BY 4.0，不在平台的收录许可证白名单里；工具包与 JaCKandJill 服务的课题在平台现有案例里没有，工具包的外部程序要装系统软件，与收录规则「核心做法离不开装系统软件的不收」冲突；研究 skill 的一部分功能（书目元数据核对、主张支持度、夸大词检查、检索台账）在已收录的 skill 里已有对应。对照时看到的平台自身问题（挑选与认证用同一次测量、评测脚本没被证明会报错、检查结果只有两态等）记在 [8.3](#83-对照中看到的平台自身问题)。

## 1. 来源与范围

BootLoops 由哈佛大学物理系教授 Matthew D. Schwartz 主持，2026-10-01 随 Anthropic Science 博客上的客座文章《Claude-shaped science》公开[^rp-essay]。GitHub 组织 [BootLoops-ai](https://github.com/BootLoops-ai) 下有七个仓库：bootloops README 列的六个（`bootloops/README.md:128-156`），加收工具请求与报错的 feedback 仓[^rp-org]。本次读了其中三个：

| 仓库 | 提交（作者日期） | 规模 | 许可证 | 本次做了什么 |
|---|---|---|---|---|
| [bootloops](https://github.com/BootLoops-ai/bootloops/tree/66b680ce742e654cfe86da4f072a69061fe182b1) | 66b680c（2026-09-30） | 2061 个受版本管理的文件，克隆目录 42 MB（含 `.git` 8.9 MB） | 代码 MIT，文字与图 CC BY 4.0，3 个文件 GPL | 读 README、INSTALL、各包 GUIDE；本机跑全量自检 |
| [skills](https://github.com/BootLoops-ai/skills) | ca89227（2026-09-30） | 47 个文件，12 个 skill | 脚本 MIT，正文 CC BY 4.0 | 12 个 SKILL.md 逐个读全文；用平台的解析器与零 key 扫描实测 |
| [jackandjill](https://github.com/BootLoops-ai/jackandjill) | e0ccb07（2026-09-30） | 466 个文件 | 代码 MIT，文字 CC BY 4.0，一个数据文件 GPL-3.0 | 读契约文档；本机安装并跑自检 |
| kira、blade、amflow-cpp | — | — | Kira 分叉 GPL-3.0-or-later，另两个 MIT | 没有克隆，只看了 bootloops README 里的介绍 |
| feedback | — | — | — | 查公开 issue：2026-10-02 为 0 条 |

另读了 [bootloops.ai](https://www.bootloops.ai) 的首页、harness、papers、summaries、amplitudes、contact 各页，总论文 BootLoops.pdf（27 页），NBER 工作论文 w35782 的摘要页，以及同一作者的前作《Vibe Physics》，用来核对公开说法。

## 2. BootLoops 是什么

BootLoops 自称「给大模型做精密定量科学用的 harness」：一套写给 agent 驱动的科学计算软件，加上一套让结果可核验的工作协议；它不绑定驱动它的模型，克隆下来、让任意 agent 读索引即可使用[^rp-readme]。实际由两部分组成：

- **计算工具包**（`bootloops` 仓）：`tools/` 下 49 个包（另有共享夹具 `fixtures/` 与 26 个顶层兼容 shim 与成员文件）；`upgrades/` 放三个随仓发布的 Julia 引擎（Eichler.jl、SOFIA.jl、leviathan，README 称为 engines of our own，其中 SOFIA.jl 是 SOFIA 的 Julia 翻译）；`ops/` 放共享机器上的作业准入控制。每个包附一份写给 agent 的 GUIDE.md（做什么、什么时候用、输出什么意思、答案要过什么检查）和一条钉死的自检命令。主体服务费曼积分与散射振幅计算，见[第 6 节](#6-计算工具包)。
- **工作协议**（`skills` 仓）：12 个 agentskills.io 格式的纯 markdown skill，分「协议层」7 个和「研究」5 个，见[第 4 节](#4-协议层-skill7-个)与[第 5 节](#5-研究-skill5-个)。
- **JaCKandJill**（`jackandjill` 仓）：贝叶斯系统发育模型的精确与认证 evidence 计算，是工具包之外单独发布的一个领域包，见[第 7 节](#7-jackandjill系统发育证据)。

README 写明：代码由 Claude 在作者指导下写成，作者定题、批准每个计划、用独立路线核对结果；这些是研究工具，使用前要自行验证，不适用于临床、精算、支付、监管或公共安全决策[^rp-readme-status]。

[^rp-essay]: Matthew Schwartz, *Claude-shaped science*, Anthropic Science 博客客座文章，2026-10-01，<https://www.anthropic.com/research/claude-shaped-science>；作者单位见同一博客 2026-03-23 的前作 *Vibe Physics*，<https://www.anthropic.com/research/vibe-physics>。
[^rp-org]: 2026-10-02 查询 GitHub REST API `GET /orgs/BootLoops-ai/repos`，返回 7 个仓：feedback、skills、kira、jackandjill、amflow-cpp、blade、bootloops。`bootloops/README.md:128` 原句 "BootLoops is six repositories published side by side"，不计 feedback。
[^rp-readme]: `bootloops/README.md:3-11`；upgrades 下三个引擎的来源见 `bootloops/upgrades/README.md:1-14`。
[^rp-readme-status]: `bootloops/README.md:204-213`（Status, provenance and responsible use 一节）。

## 3. 原文与公开说法

本节依据的公开材料有四类：Anthropic Science 博客上的一篇客座文章、bootloops.ai 网站、一篇 27 页的总论文、GitHub 组织 BootLoops-ai 下的 bootloops、skills、jackandjill 三个仓库。一篇中文转载文章里的数字都能在这些材料里找到出处，偏差在措辞与口径上：发布方与文章类型、手稿被称作「成果」、30 个积分被说成都是椭圆积分、点名千问和 DeepSeek 可以直接适配。原文写明了多条局限，例如多数科学问题做不了、概念工作仍要人做、论文多由模型起草且部分未经人完整核对；没有交代的是落选候选、成本数字和其他模型的实测记录。

### 3.1 原文、发布与归属

原文是 Matthew Schwartz 的《Claude-shaped science》，发在 anthropic.com 的 Science 栏目，页首注明是客座文章（"In this guest post"）[^cl-guest]。页面元数据的发布时间是 2026-10-01 14:02 UTC，即北京时间 22:02；修改时间是北京时间 10-02 02:50[^cl-time]。同一作者此前在同一栏目发过客座文章《Vibe Physics》，本文开头回顾了那次项目[^cl-vibe]。

| 时间 | 事件 | 出处 |
|---|---|---|
| 2025-12 | 作者用 Claude Opus 4.5 做 Vibe Physics 项目，原文写 "Last December" | [^cl-vibe] |
| 2026-03-23 | 《Vibe Physics》发布 | [^cl-vibe] |
| 2026-07 至 09 | Manuscripts 页写所列项目都在这段时间完成 | [^cl-papers] |
| 2026-09-27 | feedback 仓创建，官网指定它为工具请求与报错入口 | [^cl-gh] [^cl-contact] |
| 2026-09-30 | 三个仓最后一次提交；Contact 页贡献表记 "BootLoops 1.0: 49 toolkit packages" | [^cl-commits] [^cl-contact] |
| 2026-10-01 | 三个仓在 GitHub 上创建（UTC 01:21 skills、10:58 jackandjill、15:29 bootloops） | [^cl-gh] |
| 2026-10-01 | 博客文章发布（UTC 14:02）；总论文落款同日 | [^cl-time] |

归属有两组说法，下表照录原句，不做概括。

| 出处 | 原文 |
|---|---|
| 博客文末 Disclosure | "During this project, Schwartz has been working as a visiting researcher at Anthropic. BootLoops is not an Anthropic project; it is owned and maintained by Matthew Schwartz."[^cl-own] |
| 官网首页末段 | "Funding for BootLoops was provided by Anthropic. BootLoops is not an Anthropic project. It is owned and maintained by Matthew Schwartz."[^cl-own] |
| 总论文 p.21 | "Funding for this project was provided by Anthropic. This is not an official Anthropic project and results and views are not endorsed by Anthropic."[^cl-own] |
| 三个仓的 NOTICE | "Copyright (c) 2026 Anthropic, PBC"；"Created by Matthew D. Schwartz. Code written by Claude (Anthropic) under his supervision. This is not an officially supported Anthropic product; it is maintained by Matthew D. Schwartz"[^cl-notice] |
| 三个仓的 LICENSE（MIT） | "Copyright (c) 2026 Anthropic, PBC"[^cl-notice] |
| bootloops、skills 的 LICENSE-CONTENT（CC BY 4.0 署名串） | "BootLoops 1.0, Anthropic, PBC and Matthew D. Schwartz (2026), https://www.bootloops.ai"[^cl-notice] |
| bootloops、skills 的 NOTICE 引用格式 | "M. D. Schwartz, BootLoops 1.0 (2026), https://www.bootloops.ai"[^cl-notice] |

博客和网站写 BootLoops 归 Schwartz 所有并由他维护；仓库的版权行写 Anthropic, PBC，同时写明不是 Anthropic 官方支持的产品、由 Schwartz 维护。两组说法字面不同，本报告不对所有权做法律判断，转述时照各自原句。三处原文都写了 "not an Anthropic project" 或 "not an official Anthropic project"，把 BootLoops 当作 Anthropic 的产品与这些声明不符。

利益关系原文都有披露：作者在项目期间是 Anthropic 的访问研究员，项目由 Anthropic 资助，文章发在 Anthropic 网站，报告的计算由 Anthropic 的 Claude 运行[^cl-own] [^cl-pdf]；NBER 工作论文的披露写 "For this project, Schwartz worked as a contractor for Anthropic; the results and views are not endorsed by Anthropic."[^cl-nber] 代码的作者也写明了：总论文 p.21 写 "The BootLoops package was written by AI, except for forks of public packages which are their authors' work"，NOTICE 写 "Code written by Claude (Anthropic) under his supervision"[^cl-notice]。

### 3.2 手稿清单与状态

博客给的总数是 "36 manuscripts in 18 fields with 19 coauthors over three months, out of some 400 candidate problems"[^cl-36]。逐项对照网站：

| 项目 | 数字 | 说明 | 出处 |
|---|---|---|---|
| 手稿条目 | 36 | Manuscripts 页 36 条：总论文 1 条，另 35 条分在 9 个学科分组下 | [^cl-papers] |
| 尚无稿 | 7 | 标 `[in preparation]`，有标题、作者与简介，没有 PDF | [^cl-papers] |
| 站内 PDF | 28 | 托管在 bootloops.ai，含总论文 | [^cl-papers] |
| 外链 | 1 | 链到 NBER 工作论文 | [^cl-papers] |
| 标 preliminary | 未验证 | 页首说部分手稿带 preliminary 水印；本次只下载了总论文，带水印的条数没有逐篇核对 | [^cl-papers] |
| 候选问题 | 约 400 | 只在博客出现一次，没有列表 | [^cl-36] |
| 领域 | 18 / 22 / 9 | 博客 18 个；官网首页 "twenty-two fields of science"；Manuscripts 页 9 个分组；三处都没有定义「领域」 | [^cl-fields] |
| 合著者 | 19 | Manuscripts 页作者去重后，Schwartz 之外 19 人，与博客一致；博客致谢 22 人，总论文致谢 23 人 | [^cl-coauth] |
| 时间 | 3 个月 | 2026 年 7 月至 9 月 | [^cl-papers] |
| 站外发行 | 1 | NBER 工作论文 w35782（2026-09，DOI 10.3386/w35782）；其余条目页面上没有期刊、arXiv 或 DOI 链接 | [^cl-nber] [^cl-papers] |

Manuscripts 页对手稿状态的原话是："All of these manuscripts have been read by humans for accuracy. Many were drafted first by LLMs and some have not been fully checked yet by humans; those are watermarked as preliminary."[^cl-papers] 博客介绍七个 additional highlights 时写明 "each of which is undergoing further exploration and verification"；其中有的在 Manuscripts 页还没有稿，例如博客写 "We solved Watson's 'final problem'"，对应条目 "The anisotropic Watson integral" 标 `[in preparation]`[^cl-watson]。

外部反馈与复现：2026-10-02 05:04 UTC 查询，feedback 仓与 bootloops、skills、jackandjill 三个仓的 issue 与 PR 都是 0 条[^cl-gh]；Contact 页的贡献记录表只有作者本人 2026-09-30 的一行[^cl-contact]。查询时距博客发布约 15 小时。没有外部记录这一点，既不说明结果有误，也不说明结果经过了独立检验。

### 3.3 中文转载说法逐条核对

下表的说法摘自一篇中文转载文章，逐条回到英文原文、网站与仓库核对。判断分四档：属实、部分属实、夸大、查不到。

| 说法 | 原文怎么说 | 判断 | 出处 |
|---|---|---|---|
| 「凌晨 Anthropic 分享」 | 文章发在 anthropic.com，页首写 "In this guest post"；发布于北京时间 10-01 22:02，修改于 10-02 02:50；文末写 "BootLoops is not an Anthropic project" | 部分属实：发布渠道属实；文章是客座文章；「凌晨」只对得上修改时间；Anthropic 社交媒体账号的推送时间本次未查 | [^cl-guest] [^cl-time] [^cl-own] |
| 「3 个月 36 个成果、18 个学科、19 位专家」 | "36 manuscripts in 18 fields with 19 coauthors over three months, out of some 400 candidate problems"；36 条里 7 条尚无稿；官网写 22 个领域 | 夸大：数字与博客一致；原文的计数单位是手稿，其中 7 条还没有稿；所引转述里没有约 400 个候选这个分母 | [^cl-36] [^cl-papers] [^cl-fields] |
| 「不绑定任何大模型，Claude、千问、DeepSeek 都能直接适配」 | 博客："it can be used with whatever model you like"；README："The harness is independent of the model driving it"；官网："it can be called with Claude, or Gemini or ChatGPT, any version"；总论文："The computations reported here were run by a large language model, Claude (Anthropic)" | 部分属实：「不绑定模型」是原文的设计主张，材料里没有其他模型驱动的实测；千问、DeepSeek 查不到 | [^cl-agnostic] |
| 「AI 20 分钟复现教授几周的代码」 | "it reproduced the results from my paper in around 20 minutes, while the code I wrote to do it took me weeks"；任务是把已有方法移植到统一框架、复现作者本人论文的结果，模型为 Claude Fable 5 | 属实 | [^cl-20min] |
| 「30 个椭圆积分一半是新结果」 | "30 integrals … 15 reproductions of known results … and 15 that had never before been computed"；amplitudes 页按函数类：椭圆 17、多重对数 8、K3 2、Calabi–Yau 2、多重对数加 K3 1；15 个新结果中椭圆 10 个 | 部分属实：「一半是新的」与原文一致；30 个里椭圆积分 17 个 | [^cl-amp] |
| 「巴拿马森林树种变化是中性理论上限的 4.5 倍」 | 博客："the mix of tree species changes 4.5 times faster than neutral theory allows"；下一段写专家的评价 "be met with a shrug by many ecologists"；网站摘要的口径是多数物种 "two to six times"、整体相当于更替快 "four times"，并写明 "It was already known" | 属实：数字出自博客；网站摘要的倍数口径与博客不同；博客下一段写了专家的保留意见 | [^cl-bci] |
| 「经济学 4452 篇顶刊论文代码复刻和数据核验」 | NBER 摘要："Across 4,452 published replication packages for five economics journals, the workflow flags discrepancies in 3,460 articles"；12.4% 的包声明依赖未公开数据，只能记录表面差异；最早一处差异是数值不符的 3,166 篇中，35.6% 的差异在末位一个单位以内；作者写明 "the workflow does not aim to evaluate research" | 属实：数字准确；所引转述里没有这几条口径 | [^cl-nber] |
| 「语言学 6072 种语言重音数据库、16 万篇参考文献」 | 6,072 条中 77 条不在 Glottolog 的口语语言名单内（人造语言 27、皮钦语 26、手语 15、语域 8、无记录语言 1）；739 条未定类型；595 条 "should be treated as provisional"；书目 160,654 篇；站点 closed beta；"not every entry has been checked by hand" | 属实：数字准确；所引转述里没有这几条口径 | [^cl-acc] |

八条说法里出现的数字，在原文里都有对应原句。偏差有三类：发布方与文章类型（第 1 条）；计数单位与分母（第 2、5 条）；模型适配范围（第 3 条，千问和 DeepSeek 在原文、网站和三个仓库里都没有出现）。第 6 至 8 条数字属实，博客相邻段落或网站对应的摘要页给了限定条件，所引转述里没有这些条件。

### 3.4 原文的方法论

方法论分散在博客的 "The technical details" 一节、官网首页的四条原则（Checkability、Breadth、Porting and improving、Rigorous vetting）、总论文 §1 至 §2 与 harness 页。下面按四个问题整理，引文保留英文原句。这些是作者对自己做法的陈述，工具包与 skill 落实到什么程度在本报告的其他各节。

**怎么挑适合模型的题。** 作者的出发点是按模型实际擅长的事挑题："instead of treating Claude like the collaborator I wanted it to be, I started to treat it like the collaborator it actually is. This required looking for problems suited to its strengths."[^cl-36] 他列的擅长项是跨领域知识、写代码、数学与统计、高速读论文和数据，并写明 "Claude is just not able to help me with deep conceptual questions"。挑题的三个条件以 semi-numerical bootstrap 为例："It draws on mathematics, physics, and computer science that no one person has mastered; it needs a great deal of coding and algorithm development; and it is checkable"。官网的 Breadth 原则要求每个项目说清 AI hook："Every project should have an AI hook: why should BootLoops solve this when humans couldn't."[^cl-vetting] harness 页写模型可以判定问题不适合："Or maybe your problem is just not BootLoops-shaped and it will tell you that."[^cl-playbook] 题目有没有科学价值由人判断："you still can't trust its judgment of whether something is interesting."[^cl-blogfail] 约 400 个候选最后对应 36 条手稿条目，其中 7 条尚无稿[^cl-36] [^cl-papers]。

**人和模型怎么分工。** 总论文 §2.1 写明人、模型与程序各做什么："The computations reported here were run by a large language model, Claude (Anthropic), with a human setting the targets and the standards."，"The programs compute every number and symbol. At no step is the model asked for a digit, and no result rests on the model's judgment."[^cl-pdf] 同一篇论文把 BootLoops 与 FunSearch、AI Scientist、Robin 等面向自主科研的系统对照，定位是 "a language model working under human supervision"[^cl-pdf]。博客描述了与领域专家合作时的角色："I became a sort of Claude handler, translating Claude-speak to James and keeping the model on track, while James pushed the model to produce something ecologists might value."[^cl-expert] 会话的组织方式是每个项目一个会话，另有一个主会话 "coordinates the others, allocates compute, and validates results"，写作和 "checking and rechecking results as an adversarial referee" 各开独立会话，中间结果写进各自目录的 markdown 文件[^cl-36]。积累放在工具里："Each problem leaves behind the tools it forged, so the next problem starts from a stronger harness."[^cl-vetting]

**怎么检查模型报告的结果。** 博客列了一组失败模式与对策[^cl-blogfail]：

- "Claude loves to declare victory. 'Done, with one asterisk' is often 'not done at all.'" 对策是事先给出 "clear and rigid standards for what success looks like"。原文的例子是证明只差 "one unproven lemma"，而 "That lemma was the whole proof!"
- "I always ask to see plots. Even with all the monitors I set up, I've found the automated checks still can't be trusted. Beware of qualitative claims like 'good agreement.'"
- "Question the conclusions. Claude is good at performing calculations, but the conclusions it draws can be wrong."

官网的两条原则把核验写成规则[^cl-vetting]：结果要能被独立脚本复现，"so nothing is hidden deep inside the LLM's knowledge base or in some secret file"；预测事先封存，"Predictions are sealed beforehand with a SHA code"，目的是 "to avoid reward hacking"；定期派怀疑型 agent 做对抗审查，强制下载并阅读原文而不凭记忆，并且 "It's important not to ask for a list of corrections but rather to iterate until no corrections remain."。散射振幅的数值标准是 "thirty digits or more of agreement, often a hundred, at points that entered no fit"。前作《Vibe Physics》记录过更早的问题："It faked results, hoping I wouldn't notice."，"It says 'verified' when it hasn't actually checked."；当时的做法之一是 "I had GPT check Claude's work and vice versa."[^cl-vibe]

**怎么找专家核验。** 作者说明了为什么需要外部专家："When Claude claims something it did in my field is fantastic, I can judge whether that's true or not (it often isn't). But when it claims something it did in another field is fantastic, I find myself agreeing."，以及专家介入前的状况："in almost all cases, Claude was technically correct, but the result was not all that interesting until the expert helped steer us."[^cl-expert] 两个实例：生态学专家认为中性理论的结果会 "be met with a shrug by many ecologists"，随后提出减去中性预测、研究剩余部分；群体遗传学专家 "was impressed by the technical result but not compelled by the science"，随后建议改看同一染色体上的突变对[^cl-expert]。找专家本身有成本："I had to write to three different biologists for validation before one responded"[^cl-expert]。

如果以后要用这些做法，能对上平台现有规定的地方如下，只列对应关系：

| 原文做法 | 平台相近的规定 | 出处 |
|---|---|---|
| 数由程序算，模型不出数 | P-24「数由框架跑不由 agent 自报」；P-2 确定性能判的用零模型代码 | `docs/architecture/README.md:174`、`docs/architecture/README.md:152` |
| 对抗审稿开独立会话 | P-2 需要模型判断的由隔离的新会话做，正文标明这一段尚未实现 | `docs/architecture/README.md:152` |
| 目标与标准由人定 | P-19 `requirement.lock` 是人的确认，「唯一内置的门」；P-24「对没对上由研究者按需求里的标准判」 | `docs/architecture/README.md:169`、`docs/architecture/README.md:174` |
| 领域专家判断结果有没有科学价值 | 纲领里没有对应条款 | `docs/architecture/*.md` 检索「专家」0 命中 |

### 3.5 原文承认的局限与没说的

原文自己写明的局限：

| 局限 | 原句 | 出处 |
|---|---|---|
| 多数科学问题做不了 | "The current generation of AI tools is not capable of solving most problems in science." | [^cl-guest] |
| 概念工作仍要人做 | "humans are still needed for the conceptual part." | [^cl-guest] |
| 技术上对，科学上未必有价值 | "in almost all cases, Claude was technically correct, but the result was not all that interesting until the expert helped steer us."；两位专家的评价见 [3.4](#34-原文的方法论)「怎么找专家核验」一段 | [^cl-expert] |
| 手稿由模型起草，写得不好，部分未经人完整核对 | "the papers here were almost entirely written by Claude, and they are not written well."；"some have not been fully checked yet by humans" | [^cl-playbook] [^cl-papers] |
| 亮点仍在核验中 | "each of which is undergoing further exploration and verification" | [^cl-watson] |
| 自动检查不可全信 | "the automated checks still can't be trusted" | [^cl-blogfail] |
| 估时不准，倾向于长时间计算而不先造工具 | "I never succeeded in getting Claude to estimate time well."；"The model will grind forever if you let it." | [^cl-blogfail] |
| 上下文压缩丢信息 | "compaction would often kick in, causing Claude to lose important context" | [^cl-36] |
| 证明代码有 bug 时会误称穷尽 | "when AI is doing the proving, there is another failure mode: bugs in the code."（总论文 p.17） | [^cl-pdf] |
| 静默失败的实例 | AMFlow "returned zero correct digits at exactly the limit the calculation needed, with no error message"；参考值本身只准到 18 位。同一节写了处理结果：容差判断改为随工作精度缩放后，同一次运行给出 160 位；换用新参考值后，终值与完全独立的计算一致到 41 位 | [^cl-playbook] |
| 方法单项不新 | "No single ingredient of the methods in BootLoops is new."；"Our contribution is to pool these methods as working programs in a single toolkit"（总论文 p.3） | [^cl-pdf] |
| 算力与 token 开销大 | "these projects were compute- and token-intensive" | [^cl-cost] |
| 使用范围 | "These are research instruments. Validate outputs before relying on them; nothing here is intended or fit for clinical, actuarial, payment, regulatory or public-safety decisions." | [^cl-notice] |
| 没有答案的问题 | "I still don't know how to train graduate students."；谈到功劳分配时写 "I don't know how this resolves" | [^cl-guest] |
| 对过高预期的态度 | "AI can sit inside that loop … but it does not collapse the loop to a point."；"I don't see any evidence or need to revisit the scientific method." | [^cl-guest] |

原文没有交代或本次无法核实的：

- **模型无关是设计主张，未见实测。** 博客、README、官网、harness 页和总论文都说可以接任何模型，所报告的计算都由 Claude 运行；本次查到的材料里没有其他模型驱动工具包的实测记录[^cl-agnostic]。
- **落选与失败的题。** 约 400 个候选中没成稿的题、做到一半放弃的项目，原文没有列表，也没有失败原因的统计[^cl-36]。
- **成本数字。** 原文只说开销大，没有给出 token 数、算力时长、金额或人工时；harness 页说工具建成后运行便宜，同样没有给数字[^cl-cost]。前作《Vibe Physics》给过这类数字（"36M tokens, and 40+ hours of local CPU compute"）[^cl-vibe]。
- **同行评审。** 有稿的 29 条里，28 条是 bootloops.ai 站内 PDF，页面上没有期刊、arXiv 或 DOI 链接；另 1 条是 NBER 工作论文[^cl-papers] [^cl-nber]。Manuscripts 页没有标出任何一篇已在期刊发表。「新结果」由作者一方判定；博客在「椭圆 Feynman 积分此前没人完整用 bootstrap 算过」一句上加了 "at least to my or Claude's knowledge" 的限定[^cl-amp]。
- **外部复现。** 截至 2026-10-02 05:04 UTC 没有外部 issue、PR 或贡献记录[^cl-gh]。
- **预告的一节没有单独成节。** harness 页开头说页尾有 "the human-intervention playbook: practical tips on succeeding at LLM-assisted science"，取证时页面最后一节是 "How to use it"，内容是安装方法和几条使用提示，没有以 playbook 为题的一节；这一节是否就是预告的 playbook，页面没有说明[^cl-playbook]。
- **口径不一致。** 领域数在博客、官网首页与 Manuscripts 页分别是 18、22、9 组[^cl-fields]；工具数在网站导航是 59 个工具页，Contact 页写 49 个工具包，差别来自哪里没有说明[^cl-tools]。

[^cl-guest]: 《Claude-shaped science》，<https://www.anthropic.com/research/claude-shaped-science>（2026-10-02 取证）。页首摘要："In this guest post, Prof. Matthew Schwartz returns to describe a new approach to AI-accelerated science." 本节引用的 "not capable of solving most problems in science" 在开篇，"humans are still needed for the conceptual part"、"train graduate students"、"collapse the loop to a point"、"revisit the scientific method" 在 Outlook 一节。

[^cl-time]: 同页 HTML 的 `article:published_time` 为 `2026-10-01T14:02:00.000Z`，`article:modified_time` 为 `2026-10-01T18:50:14.000Z`。总论文首页落款 "October 1, 2026"，<https://www.bootloops.ai/BootLoops.pdf> p.1。

[^cl-vibe]: 《Vibe physics: The AI grad student》，<https://www.anthropic.com/research/vibe-physics>，`article:published_time` 为 `2026-03-23T23:00:00.000Z`，页首写 "In this guest post"。该文写项目时间是 "I conducted this project in the last two weeks of December 2025."；摘要列了开销 "Over 110 separate drafts, 36M tokens, and 40+ hours of local CPU compute"。引文 "It faked results"、"Honest verification"、"Cross-verification" 三处都在该文。《Claude-shaped science》的对应原句："Last December, I tried using Claude as a research assistant, and found that Claude Opus 4.5 performed like a strong graduate student at 20 times the speed."

[^cl-own]: 博客文末 Disclosure 段，<https://www.anthropic.com/research/claude-shaped-science>；官网首页末段，<https://www.bootloops.ai>；总论文 Acknowledgments，<https://www.bootloops.ai/BootLoops.pdf> p.21。

[^cl-notice]: `bootloops/NOTICE:1-10`、`skills/NOTICE:1-6`、`jackandjill/NOTICE:1-7`（skills 仓的措辞是 "Written by Claude (Anthropic) under his supervision"）；`bootloops/LICENSE:3`、`skills/LICENSE:3`、`jackandjill/LICENSE:3`；署名串 `bootloops/LICENSE-CONTENT:5-6`、`skills/LICENSE-CONTENT:5-6`；JaCKandJill 的署名串不同，为 "JaCKandJill 1.0, Anthropic, PBC and Matthew D. Schwartz (2026), https://www.bootloops.ai/diagrams/jackjill.html"，见 `jackandjill/LICENSE-CONTENT:6-8`；引用格式 `bootloops/NOTICE:62-64`、`skills/NOTICE:27-29`；使用范围的原句在 `bootloops/NOTICE:8-10`；总论文 p.21 Acknowledgments。三个仓的提交分别为 66b680c、ca89227、e0ccb07。

[^cl-commits]: 三个仓 `git log -1` 的提交时间都是 2026-09-30 21:02（UTC-4），作者 Matthew D. Schwartz。博客末尾的 GitHub 链接钉在 bootloops 的 66b680c。

[^cl-contact]: <https://www.bootloops.ai/contact.html> 的 "Record of contributions" 表，取证时只有一行："Sep 30, 2026 · M. Schwartz · BootLoops 1.0: 49 toolkit packages"。同页把提工具请求、报 bug、改页面都指向 <https://github.com/BootLoops-ai/feedback>。

[^cl-papers]: <https://www.bootloops.ai/papers.html>（2026-10-02 取证）。页首原文："These projects were all done during the period July - September 2026. All of these manuscripts have been read by humans for accuracy. Many were drafted first by LLMs and some have not been fully checked yet by humans; those are watermarked as preliminary. For some projects the draft is not ready yet; those are marked as `[in preparation]`. As manuscripts get finalized and published, published versions or links to them will appear here." 条数按页面 HTML 的列表项逐条统计：36 条，其中总论文 1 条、站内 PDF 27 条、NBER 外链 1 条、`[in preparation]` 7 条；页首说明里的同一字样不计入。

[^cl-36]: 博客 "The technical details" 一节："Running many projects at once (36 manuscripts in 18 fields with 19 coauthors over three months, out of some 400 candidate problems) takes a lot of coordination"，会话组织与 compaction 的原句在同一节；挑题的原句在 "Claude, take the wheel!" 一节。<https://www.anthropic.com/research/claude-shaped-science>

[^cl-fields]: 博客："36 manuscripts in 18 fields"；官网首页 HTML："In BootLoops 1.0 applications spanned twenty-two fields of science"；Manuscripts 页的 9 个分组：Ecology and evolutionary biology、Genetics、Earth and planetary science、Collider physics、Mathematical physics and string theory、Economics and statistics、Astrophysics and cosmology、Language and textual analysis、Health policy and medicine。

[^cl-coauth]: 对 Manuscripts 页每条的作者行按逗号与 and 拆分并去重，Schwartz 之外 19 人。博客 Acknowledgements 列 22 人；总论文 p.21 致谢列 23 人，比博客多 Ethan Dyer。

[^cl-gh]: 2026-10-02 05:04 UTC 查询 GitHub REST API：`GET /repos/BootLoops-ai/{feedback,bootloops,skills,jackandjill}/issues?state=all`，四个仓都返回空列表（该接口同时列出 PR）；`GET /repos/BootLoops-ai/{仓名}` 的 `created_at`：feedback `2026-09-27T16:48:14Z`、skills `2026-10-01T01:21:34Z`、jackandjill `2026-10-01T10:58:19Z`、bootloops `2026-10-01T15:29:28Z`。同一时刻的星标数：bootloops 34、skills 6、jackandjill 1、feedback 2。

[^cl-watson]: 博客 "I know Kung Fu" 一节：七个 additional highlights 前写 "each of which was done in collaboration with experts, and each of which is undergoing further exploration and verification"；其中一条为 "We solved Watson's 'final problem': the exact return probability of a 3D random walk with three unequal hopping rates"。Manuscripts 页对应条目："The anisotropic Watson integral · `[in preparation]`"。

[^cl-agnostic]: 博客开篇："It is also open-source, so it can be used with whatever model you like."；`bootloops/README.md:6-8`："The harness is independent of the model driving it: clone it, point whatever agent you use at it"；官网首页 Introduction："it can be called with Claude, or Gemini or ChatGPT, any version"；harness 页："can be cloned and used by anyone with any LLM"，<https://www.bootloops.ai/harness.html>；总论文 p.3："BootLoops can be used with any underlying language model, or inside a commercial harness such as Claude Science or Codex (OpenAI)"，同页 §2.1："The computations reported here were run by a large language model, Claude (Anthropic)"。安装说明点名的 agent 是 Claude Code、Codex、Cursor、Copilot（`skills/README.md:127-129`、`bootloops/README.md:153-156`）。对三个仓全文做不分大小写的 `qwen|deepseek` 检索，0 命中；取证的博客、网站各页与总论文文本同样 0 命中。

[^cl-20min]: 博客 "Claude, take the wheel!" 一节："So my first assignment for Fable 5 was to port all of it to a common framework, and to write the code the papers never provided. Claude did this effortlessly. I was surprised when it reproduced the results from my paper in around 20 minutes, while the code I wrote to do it took me weeks."

[^cl-amp]: 博客："Soon we had 30 integrals BootLooped from end to end, comprising 15 reproductions of known results by this new method and 15 that had never before been computed."；同一段开头："Only a handful of elliptic Feynman integrals have ever been computed, and none completely by the bootstrap, at least to my or Claude's knowledge."。<https://www.bootloops.ai/amplitudes.html>："Fifteen of these were already known … Fifteen are new." 按该页 "The results" 表的 function class 列逐行数：elliptic 17、polylog 8、K3 2、Calabi–Yau 2、polylog + K3 1；status 为 new 的 15 行中 elliptic 10 行。

[^cl-bci]: 博客 "I know Kung Fu" 一节的生态学段落；<https://www.bootloops.ai/summaries/biodiversity.html>："by two to six times for most species … Overall, the mix of species changes about as fast as drift would change it if trees were replaced four times as often as they are. It was already known that abundances at Barro Colorado change faster than drift allows"，"already known" 链接的是 Chisholm 等 2014 年发表于 Ecology Letters 的论文。

[^cl-nber]: <https://www.nber.org/papers/w35782>，NBER Working Paper 35782，DOI 10.3386/w35782，Issue Date September 2026，作者 Schwartz、Andrews、Shapiro；页面 Acknowledgements and Disclosures："For this project, Schwartz worked as a contractor for Anthropic; the results and views are not endorsed by Anthropic."；摘要："Across 4,452 published replication packages for five economics journals, the workflow flags discrepancies in 3,460 articles or their appendices."。<https://www.bootloops.ai/summaries/metaeconomics.html>：五刊为 AER、Econometrica、JPE、QJE、ReStud，范围是 2000 至 2026 年发表的文章；"The other 12.4% declared every calculation dependent on omitted data"；"This bin holds 35.6% of the 3,166 articles"（差异在末位一档）；"The authors state that the workflow does not aim to evaluate research."

[^cl-acc]: 博客："a database of word stress covering 6,072 languages … plus a bibliography of 160,000 phonology works"；<https://www.bootloops.ai/summaries/linguistics.html>："has 6,072 entries … 77 entries outside that list (27 artificial languages, 26 pidgins, 15 sign languages, 8 speech registers and one unattested language)"，"739 are assigned no type"，"the 595 entries rated not confident … should be treated as provisional"，"A companion bibliography lists 160,654 works"，"The site is in a closed beta"；Manuscripts 页 ACCSTACK 条目："not every entry has been checked by hand"，同条简介写的是 "5,561 languages"，与 v1.0 的 6,072 条口径不同。

[^cl-pdf]: <https://www.bootloops.ai/BootLoops.pdf>：p.3（§1 后半，含与 FunSearch 等系统的对照和 "No single ingredient … is new"；§2.1）、p.4（§2.1 续）、p.17（穷举证明中的代码 bug）。

[^cl-vetting]: 官网首页 "The principles" 一节，<https://www.bootloops.ai>：AI hook 出自 Breadth，"Each problem leaves behind the tools it forged" 出自 Porting and improving，独立脚本、SHA 封存与 thirty digits 出自 Checkability，对抗审查与迭代到无可改出自 Rigorous vetting。散射振幅标准的完整表述见 <https://www.bootloops.ai/amplitudes.html> 的 "The BootLoops standard"。

[^cl-blogfail]: 博客 "The technical details" 一节的失败模式清单，条目标题依次为 "Claude loves to declare victory"、"Look at everything yourself"、"Question the conclusions"、"Supply the taste"、"Follow up"、"Watch out for the grind"。<https://www.anthropic.com/research/claude-shaped-science>

[^cl-expert]: 博客 "I know Kung Fu" 一节，<https://www.anthropic.com/research/claude-shaped-science>。

[^cl-playbook]: <https://www.bootloops.ai/harness.html>（2026-10-02 取证）。开头："the page ends with the human-intervention playbook: practical tips on succeeding at LLM-assisted science"；页面最后一节标题为 "How to use it"。"not BootLoops-shaped" 在开头的用法说明段；"not written well" 在 "How to use it" 一节；AMFlow 与 18 位参考值在 "How the toolkit grows" 一节，同节原句 "The same run then gave 160 digits"、"Against a fresh reference, the final value agreed with a fully independent computation to 41 digits."。

[^cl-cost]: 博客："these projects were compute- and token-intensive"；harness 页 "How to use it" 一节："a lot of compute and billions of tokens went into constructing the initial tool library, the tools are cheap to run"，"A laptop and whatever LLM access you already have are enough to drive the code"。博客、harness 页与总论文文本里没有 token 数、算力时长或金额。

[^cl-tools]: 官网各页左侧导航列出 59 个工具页（不计 Toolkit index 页），其中 AMFlow、Blade、FORM、GiNaC 4 个标 external；Contact 页贡献表写 "49 toolkit packages"。两处计数的差别本次没有逐项核对。

## 4. 协议层 skill（7 个）

七个协议层 skill 都是单个 `SKILL.md`（95 到 209 行），没有脚本、不调用工具包、不需要任何 key，内容是把盲分析、预注册、交叉验证、变异测试、模拟校准这些既有做法整理成面向 agent 的步骤、失败模式与复选清单[^sk-gate][^sk-sources]。acceptance-gate、independence-bookkeeping、planted-truth 讲的「先定判据再看结果」「检查要先被看到失败一次」「参与过挑选的数据不能再拿来认证」能对上平台验证与 AutoResearch 的几处现状，但 acceptance-gate 与 independence-bookkeeping 按确定性高精度数值计算来写，精度翻倍重跑、留一法、数位数这些条款在随机训练上没有直接对应；constant-recognition 与 tool-stewardship 的适用对象和平台用户对不上。正文许可证是 CC BY 4.0，不在平台收录白名单里[^sk-platform-license]。

下文单写 `:行号` 时，指同一句里前面最近写出的文件；同一句里前面没有文件时，指该小节所讲 skill 的 `skills/skills/<name>/SKILL.md`。

### 4.1 共同点

**格式与体量。** 12 个 skill 都按 Agent Skills 格式写（`skills/README.md:13-17`），一个目录只有一个 `SKILL.md`，frontmatter 只有 `name` 与 `description` 两个字段，没有 `license`、`compatibility`、`metadata`。协议层七个的体量与结构（行数为 `wc -l`）：

| skill | 行数 | 步骤 | 失败模式 | 出处 |
|---|---|---|---|---|
| acceptance-gate | 209 | 9 步（0–8） | 11 | 有出处节 |
| independence-bookkeeping | 192 | 1 条规则 + 账本 6 项 | 10 | 末尾一句，无标题 |
| planted-truth | 205 | 8 步（0–7） | 10 | 有出处节 |
| timing-discipline | 184 | 8 步 | 10 | 无 |
| reading-contract | 206 | 9 步 | 12 | 无 |
| constant-recognition | 205 | 位数预算 + 7 步 | 7 | 有出处节 |
| tool-stewardship | 95 | 3 组步骤 + 四问页 + 去重 | 10 | 无 |

**无脚本、无 key、不依赖工具包。** 本机用平台自己的门禁函数逐个加载：协议层七个全部通过格式检查，零 key 扫描命中 0 处，与平台三处库没有重名[^sk-gate]。正文里没有工具包的路径、包名或安装命令，仓库 README 写明这些 skill 离开工具包也能用（`skills/README.md:166-174`）；tool-stewardship 只说「the toolkit」，不写路径、包名或命令，NOTICE 说明它指同组织发布的 bootloops 仓（`skills/NOTICE:23-25`）[^sk-toolkit]。

**写法。** 主体结构相同：讲为什么需要这条纪律，然后是编号步骤、失败模式目录、一两个小例子、退出前的复选清单。acceptance-gate、independence-bookkeeping、planted-truth、reading-contract 开头是一句加粗的总规则；timing-discipline 的加粗规则放在一段说明之后（`skills/skills/timing-discipline/SKILL.md:16-20`）；constant-recognition 与 tool-stewardship 开头是说明段，没有加粗总规则。失败模式按机制写，acceptance-gate 写明「The vignette states the mechanism; learn the shape, not the example」（`skills/skills/acceptance-gate/SKILL.md:101-103`）。timing-discipline、reading-contract、tool-stewardship 三个没有引用任何文献，与 README「每个 skill 末尾都有出处说明」（`skills/README.md:215-219`）不符[^sk-sources]。

**许可证。** `skills/NOTICE:10-14` 写明：`SKILL.md`、README 及其在 `plugins/` 下的生成副本按 CC BY 4.0，`tools/` 与 `*.json` 按 MIT。仓库根的 `LICENSE` 是 MIT，只覆盖脚本与插件清单，单看它会误判正文许可证；生成脚本里的 `LICENSE_ID = "CC-BY-4.0 AND MIT"`（`skills/tools/make_plugins.py:52`）也印证这一点。署名串是「BootLoops 1.0, Anthropic, PBC and Matthew D. Schwartz (2026), https://www.bootloops.ai」（`skills/LICENSE-CONTENT:5-6`），版权行是「Copyright (c) 2026 Anthropic, PBC」（`skills/NOTICE:2`），NOTICE 同时写明由 Matthew D. Schwartz 创建和维护、不是 Anthropic 官方支持的产品（`skills/NOTICE:4-6`）。CC BY 4.0 允许改编与再分发，条件是署名、保留版权声明、给出许可证链接、写明是否改过[^sk-license]。收不进平台是平台自己的规则：收录白名单只有 MIT、Apache-2.0、BSD、ISC，CC-BY 系列 2026-10-01 定为不收（[#198](https://github.com/zephyr4123/TJU-AI4Science/issues/198)）[^sk-platform-license]。台账每个上游只有一个 `license` 字段（`platform/framework/skills/provenance.py:100`），同一个仓「文字 CC BY、代码 MIT」的双许可目前表达不了。

**打包层与安装器。** `plugins/` 下两个插件 bootloops-protocols（协议层 7 个）与 bootloops-research（研究 skill 5 个），连同给 Claude Code、Codex 的 marketplace 清单，都由 `skills/tools/make_plugins.py` 从 `skills/` 生成，不手改（`skills/README.md:59-63`、`skills/plugins/README.md:1-12`）。本机实测 `--check` 报告生成树是最新的，12 份插件副本与原件逐字节相同[^sk-plugins]。`skills/.claude/skills/bootloops-setup/` 是只在克隆目录里打开 Claude Code 时才生效的安装器：先列清单，问装哪些、装在项目级 `.claude/skills/` 还是用户级 `~/.claude/skills/`，缺省项目级，并写明「Never activate anything without an explicit choice」（`skills/.claude/skills/bootloops-setup/SKILL.md:10-11`、`:35-48`）。平台不走 agent 的原生 skill 加载，由框架把装载的 skill 拼成清单注入会话（P-22），所以打包层与安装器在平台里没有对应位置[^sk-setup]。

**作用范围。** 仓库 README 写明这些协议让 agent 的结果可以被检查，不替代合格人员的审阅；CLOSED、VERIFIED-CLOSED 是内部等级，所有 BootLoops 结果发布前都经作者审阅（`skills/README.md:45-48`）。

### 4.2 acceptance-gate

**管什么。** 计算结果什么时候可以叫「做完」：必须通过一道本来可能失败、由不知道答案的路线来跑的检查；算完不等于做完（:8-10）。

**核心规则。** 九步按顺序执行（:31-97）：

- 第 0 步，拟合前写下门：保留哪些评估点、独立路线是什么、多少位算通过、对照怎么做。
- 第 1 步，保留点不参与任何拟合、调参和基的选择，包括塑造了方法的探索性运行。
- 第 2 步，审独立路线：不共享代码、级数表示和拟合输入；做不到完全不相交时写明共享了什么，检查的分量按共享程度打折。
- 第 3 步，数一致的位数，报数字，不写「吻合很好」。
- 第 4 步，工作精度翻倍重跑，一致位数必须加深；位数钉住不动判失败。
- 第 5 步，正负对照：负对照扰动候选（翻一个符号、把最后一个拟合系数的末位改掉），门要在预期的那一位上报错。
- 第 6 步，答案由拟合决定时做留一法。
- 第 7 步，附一个陌生人能重跑的独立求值脚本，能在任意精度下重测这道门。
- 第 8 步，判决只有 CLOSED 与 OPEN 两种，OPEN 写明已确立什么、还差什么。

BootLoops 对自己的圈积分结果用的门槛是至少 30 位保留数字、两档精度稳定、对照的 oracle 从未参与拟合（:26-29）。

**长处。** 11 条失败模式各写一个机制，其中几条在数值计算以外同样成立：门槛漂移（:142-146，门槛在第 0 步定下后不许动，需要挪门槛的候选就是没过）、不会失败的门（:135-140，容差宽到什么都能过、变量别名导致自己和自己比）、无条件的 PASS 行（:164-169，PASS 打印在比较分支之外）、自评信心（:154-157）。负对照一句「A gate that has never failed anything certifies nothing」（:75-77）给出了判断一个检查是否有效的可执行标准。出处列了粒子物理的盲分析、预注册、Stone 的交叉验证和 Knight 与 Leveson 1986 年的多版本软件实验（:200-209）。

**局限与适用前提。** 证据单位是「一致的位数」，第 4 步「精度翻倍后位数加深」与第 6 步留一法针对确定性的数值拟合；放到神经网络训练这类带随机性的实验上，这两步没有直接对应，原文只写了「Scale the digit count to the problem; never scale away the structure」（:28-29），没有说明哪些条款在随机设定下不适用[^sk-ag-stochastic]。用到这类实验上，「位数」对应以 σ 计的差距，「加深」对应「加种子后效应仍在、区间收窄」，「保留点」对应留出的种子与留出的数据；这些对应是阅读时的推断，原文没有写。

**与平台已有能力的重叠。**

- 「门在拟合前声明」平台在结构上已有：`scoring.yaml` 在设计阶段写定，harness 由 `SHA256SUMS` 封存（`platform/framework/experiment/pack.py:218-286`），人在「评分指标核对」断点签字后才进实验（`platform/coordinator/README.md:95`）。
- 「报数字」「不许无条件 PASS」对应步骤 `verify`：数据表每个值回溯到 `results.json`，相对容差 1%（`platform/framework/capabilities/verify/__init__.py:27`），总状态由各项检查合成（`:76`），数据表为空判失败（`platform/framework/capabilities/verify/checks.py:53`）。
- 「保留点」平台没有。AutoResearch 内环每一轮都用基线那一个种子打分，keep / discard 与最后报告的 best 是同一次测量；`verify` 声明不重跑任何实验；`platform/framework/` 里没有留出数据的概念[^sk-holdout]。
- 已收录的 `platform/skills-curated/verification/rigor/scientific-critical-thinking`（预注册、盲法，`references/common_biases.md:15-17`）与 `ara-rigor-reviewer` 的对象是研究证据的评审（偏倚、可证伪性等维度）。

**对上平台的位置。** 开放问题 Q-3「验收怎么定义」中单次运行验收的那一半（`docs/architecture/open-questions.md:23-28`，[#10](https://github.com/zephyr4123/TJU-AI4Science/issues/10)）；Q-3 的另一半「版本验收」它不涉及。还有 [#125](https://github.com/zephyr4123/TJU-AI4Science/issues/125)「棘轮扔掉方向对但没过门的改动」。issue 列的三种解法里，「连续 k 轮同向的小改进合起来过门」如果用在已经出现的这几轮上，按这套规则属于候选出现后改动判据（门槛漂移，:142-146），而且那几轮是因为在同一份评分上方向对才被挑出来的（independence-bookkeeping 的泄漏 oracle，`skills/skills/independence-bookkeeping/SKILL.md:113-115`）；「允许一轮试叠加前几轮」按这套规则要求叠加后的候选在不变的门下重新测量。这两条是把原文规则套到 #125 上的推断，原文没有讨论这类设计[^sk-125]。

### 4.3 independence-bookkeeping

**管什么。** 让「第二条路线」的独立性有记录可查：两条路线各自依赖的代码、输入、调参历史要拿得出来，并且在可能藏错的那一层上不相交；拿不出记录就不算独立（:8-13）。

**核心规则。**

- 单向污染：喂过拟合的参考值永远不能用来认证这个结果。「喂过」包括调试时对照着它改代码、靠它决定取几项、因为和它不一致而丢掉某次运行。判据是反事实的：这个参考值如果不同，结果有没有可能不同（:30-42）。
- 账本六项（:51-98）：每个参考值有出生记录（生成器与版本、输入、工作精度、精度估计及其依据、日期）；每个 oracle 有只增不删的接触日志；声称两条独立路线时写明最深的共享层，并书面论证要防的错不在那一层；保留一个刻意不同的求值引擎；比较器先喂一对错配、看它失败，失败标准在比较之前写下；认证后在接触日志记下这次认证，该参考值从此不能认证建立在这个结论上的东西。
- 10 条失败模式（:104-133），包括泄漏的 oracle（:113-115，用参考值挑模型，再用同一批参考值认证被挑中的模型）与隔了一层的污染（:119-121，原始值留出了，但比较的是用拟合参数算出的残差）。

**长处。** 给了一个五行的出生记录样例（:152-158），最后一行 `contacts:` 直接写明这个值已不能认证哪次拟合，查记录就能知道一个参考值还能不能用。反事实判据可以逐项回答是或否。出处是 Knight 与 Leveson 的多版本实验，以及统计学习里训练集与测试集的分离（:189-192）。

**局限与适用前提。** 样例里的参考值是高精度数值，精度以位数计。放到带噪实验上，被反复用来打分的评估数据本身就是 oracle。按 :41-42 的反事实判据推一步：平台内环每一轮 keep 都在同一份评分数据上判，这份数据已经影响了挑选；换新种子只能去掉「挑中噪声」，去不掉对评分数据的适应性过拟合，按这个 skill 认证还需要一份设计阶段封存、循环从没见过的留出数据[^sk-holdout]。这一步是推断，原文没有写到 ML 场景。账本六项要人或 agent 手写，原文没有配套工具。

**与平台已有能力的重叠。** 出处记账平台已有一部分：每轮账本 `ledger.tsv` 记 commit、parent、seed、sigma、harness_sha 等（`docs/architecture/workflow.md:173`），被弃的尝试留在 `refs/attempts/`（`docs/architecture/workflow.md:164`），`verify` 拿账本与 git 对账，harness 由 SHA256 封存。平台没有的是单向污染这条规则：没有字段记录评分数据参与过哪些挑选，也没有记录 `evaluate.py` 与 `code/` 出自同一个设计会话这一最深共享层。已收录 skill 里没有管同一件事的。

**对上平台的位置。** 与 [4.2](#42-acceptance-gate) 相同，对应 #125 与 Q-3：认证用的测量与挑选用的测量不相交。框架已有的 `AI4SCI_INNER_K`（评分内部重复取均值，`platform/framework/experiment/harness_contract.md:10`）降低的是单次评分的噪声，评分数据仍是同一份。

### 4.4 planted-truth

**管什么。** 分析流程在碰真数据之前，先在按已知答案构造的合成数据上证明自己能找回答案、能抓住故意弄坏的输入（:8-11）。

**核心规则。** 八步（:32-93）：

- 第 0 步，打开真数据之前冻结对照：植入值、篡改方式、零输入及各自的通过标准。
- 第 1 步，植入数据走与真数据完全相同的生产入口、配置和文件格式，找回精度达到真分析要声称的精度，参数范围的边角也要植入。
- 第 2 步，一次一种篡改（符号反转、两行对调、两列标签对调、一块按常数缩放、网格平移、重复记录、截断文件），每种都要在声称能抓到它的那一步报出来，同时跑一份未篡改的副本必须通过。
- 第 3 步，把零表推过汇总流程，必须精确回到基线。
- 第 4 步，期望答案按构造得到或来自独立实现，不能由被测代码生成。
- 第 5 步，每个检查故意弄坏一次、亲眼看它报错。
- 第 6 步，对照随结果一起交付。
- 第 7 步，对照在真数据上报错就停下查根因，不许找一个看似合理的解释后放行。

**长处。** 七个里只有它的小例子是统计分析流程（一条回归流程，:171-177）。10 条失败模式中，静默通过的分支（:122-127）要求每份汇总写明分母，分母小于声明值就判失败；按字符串比较的校验（:107-113）指出两边经同一个格式化器打印后再比，实际比的位数比以为的少。第 4 步（:68-74）允许同一作者「先写答案再从答案造数据」的构造式夹具，只禁止用被测代码生成期望值[^sk-pt-harness]。出处是模拟校准（Cook、Gelman、Rubin 2006；Talts 等 arXiv:1804.06788）、实验物理的注入测试与变异测试（:198-205）。工具包的测试也按这个做法写，例如 `bootloops/tools/qinvert/README.md:172`、`bootloops/tools/popcorn/planted.py:1`，skill 正文不引用这些代码。

**局限与适用前提。** 植入已知答案要有能生成数据的模型。复现别人代码时上游产物格式各异，第 1、2 步的植入与篡改不一定写得出来，这是取舍时的判断，没有在平台上实测。第 0 步要求对照在第一次真实运行前封存，看过真输出再设计的对照按原文只算弱证据（:32-35、:135-139）。

**与平台已有能力的重叠。** 框架自己的 `verify` 做到了「检查要先被看到失败」：测试里有编造表值、编造正文数字、篡改账本三类负对照（`platform/tests/test_capability_verify.py:60`、`:77`、`:132`），通过时写明「核对 N 个值」（`platform/framework/capabilities/verify/checks.py:56`）。harness 契约规定 `evaluate.py` 遇到缺产物、形状错、NaN 分别退 2、3、4（`platform/framework/experiment/harness_contract.md:12`），设计提示要求它拒收坏产物（`platform/framework/capabilities/design/prompt.md:17`）。但框架对每个任务的 `evaluate.py` 只做结构检查与 SHA256 核对（`platform/framework/experiment/pack.py:218-286`），从没喂过坏产物看它是否真的退非零；「评分指标核对」断点是协调层 agent 读 `evaluate.py` 后转述给人（`platform/coordinator/README.md:95`）[^sk-pt-harness]。已收录的 `platform/skills-curated/design/planning/analytical-method-validation`（回收率检查，`SKILL.md:89`）是同一思路在分析化学里的版本。

**对上平台的位置。** 设计阶段收尾、人签字之前的 `evaluate.py`：第 2 步的篡改对照落到这里，就是喂空产物、形状错、含 NaN 的产物，核对退出码是否是契约规定的 2、3、4，同时跑一份干净副本。`evaluate.py` 要在跑实验的那台机器上用任务自己的解释器起（`platform/framework/capabilities/auto_research/judge.py:66-68` 的 `compute.submit`），所以每做一次是一次 `compute.submit` 往返，算力在远端时成本不为零。第 0 步要求对照在第一次真实运行前封存，对应的时间点在基线 `make_run0` 之前。

### 4.5 timing-discipline

**管什么。** 算力规划：不是从「这个计算、这个配置、这台机器」上测出来的预估都算猜（:16-20）；预估超过「a couple of hours」就改结构，不换更大的机器（:22-26、:48-56）。

**核心规则。** 八步（:30-80）：同代码、同机器、同设置、同用例分布的缩小版试跑并记时间戳；去掉启动段，只用稳态窗口拟合速率，单项成本随序号增长时用两档规模拟合指数；启动前写下带来源的预估；超阈值先列出改结构的候选；长跑前让一个没有利害关系的人或单独提示的 agent 判断有没有更好的路线，结论记录在案；启动前定义真进度单位（例如结果文件的行数），日志滚动和进程存活不算进度；速率骤降旧的预计完成时间立即作废；换机器、换输入、换精度都重测。

**长处。** 合法预估只有三种来源：本作业的时间戳日志拟合、同配置同硬件的已测运行、「未知，正在测」（:17-20），可以直接拿来检查一个 ETA 有没有出处。10 条失败模式里，日志行当进度（:132-136）、沉没成本（:138-142）、不忠实的试跑（:144-149，例如难度随序号增长时只试跑了列表前段）都写明了机制。

**局限与适用前提。** 没有出处，也没有说明两小时阈值的依据。改结构的候选（更好的表示或基、先做精确约化、用对称性减少用例、拆成独立的几块、大部分用例用廉价方法而昂贵方法只留给剩余部分、用极限或特例直接回答问题，:48-56）偏向数学计算，神经网络训练常用的手段（缩小模型、减少轮数、先用数据子集）原文没有列。原文谈估时不准用的是泛指的「language models」（:11-14），skill 里没有点名 Claude；点名 Claude 估时不准、默认硬磨长计算的话出自 Anthropic 网站的客座文章[^sk-td-claude]。

**与平台已有能力的重叠。** 设计阶段 `make_run0` 跑出的基线是同一任务的一次完整运行，经算力端口跑（`platform/framework/capabilities/design/__init__.py:101`），`results.json` 带 `elapsed_s`（`platform/framework/experiment/harness_contract.md:4`）；实验与基线用同一台机器时，按原文它属于「同配置同硬件的已测运行」这类合法来源。框架对 `elapsed_s` 只做两件事：核对是否超出 `wall_clock_s` 的 1.5 倍（`platform/framework/experiment/pack.py:347-354`）和记进账本；预检念给人听的 `headroom.summary()` 只拼基线、σ、门和尽头，没有用它估整轮实验时长（`platform/framework/experiment/headroom.py:74-79`）。复现路径的 `wall_clock_s` 按 README 或论文写的时间「给足，宁多勿少」（`platform/framework/capabilities/reproduction/prompt.md:38`），是未经测量的上限。三处库的 `SKILL.md` 里搜 ETA、pilot run、runtime estimate 等词，只命中参数名 eta（PyMC 先验、偏 eta 方、pymoo 算子），没有管运行时长预估的 skill。

**对上平台的位置。** [#127](https://github.com/zephyr4123/TJU-AI4Science/issues/127) 记录远端装环境几十分钟没有进度输出。第 6 步「先定义真进度单位」能对上这件事：装环境的产出单位是包，锁文件里的包数可以做分母，进度写成「已装 n/N」。`uv pip sync` 在非 TTY 下的输出能否逐包解析，未验证。拉回远端 stderr 这件工程活它不涉及。

### 4.6 reading-contract

**管什么。** 读文档并据此下断言的工具或 agent，只能断言眼前记录支持的内容，并附页、表、式、行级的定位；其余标明是记忆、推断还是没找到（:8-13）。

**核心规则。** 九步（:28-94）：本会话里真打开原文，打不开就写「未查」；每条事实带定位并写明版本（预印本还是正式发表）；承重的结论先放逐字引文，引号意味着原文逐字有这串字；保留原文的语气强度，转述只对照引文核对，不对照上一次转述；核对已发表数值只有四种结论：复现、只在原文未写明的约定下成立、原文信息不足以确定、无法核对；归属限定到实际作者，否定性结论限定到实际搜过的范围；检索到的标为检索，不说成自己推导；书目信息查规范数据库；报告分「读到 / 推断 / 背景记忆」三栏。

**长处。** 四种核对结论与 BootLoops 总论文 §6.3 审计已发表数字时的四类一致，作者在自己的工作里用过这套分类[^sk-rc-63]。转述漂移链的例子（:137-151）展示三次转述如何把「consistent with a vanishing correction」变成「it is known that the correction vanishes」；抽取记录样例（:153-175）给出可照抄的格式。失败模式 12 条。

**局限与适用前提。** 没有出处。它只管「读」这一步，不管检索、组织和成文；第 8 步说查规范数据库，没有点名是哪些。

**与平台已有能力的重叠。** 定位与「不编页码」已有：`platform/skills-curated/literature/reading/nature-paper-card` 有页码定位状态机（`SKILL.md:50-54`），准备失败时不编页码（`:145`）；`nature-reader` 要求引页码与块号，原文不支持就说「原文未明确说明」（`references/grounding-rules.md:9-11`）。平台文献阶段没有步骤，`sources.md` 由协调层 agent 自己写、写法不限（`platform/coordinator/README.md:120`）。reading-contract 独有的是三栏分隔、四种核对结论和语气强度保留。平台的一个案例里出现过它要防的问题：GUA 复现的 `verify` 判 PASS，通读时发现分析稿编了论文里没有的 Allen-Cahn（`docs/cases/gua-pinn-reproduction/README.md:52`）。

**对上平台的位置。** 文献阶段 `sources.md` 的写法；复现性分析里核对论文数值的措辞。平台现有的复现分级（`platform/framework/capabilities/reproducibility/prompt.md:45`）分的是「复现到哪一级」，与这四种结论是两个维度。

### 4.7 constant-recognition

**管什么。** 用 PSLQ、LLL 这类整数关系算法把高精度数字认成闭式常数时的纪律（:8-15）。

**核心规则。** 先算位数预算：n 个常数、系数上界 H 的关系大约消耗 n·log₁₀H 位精度，剩下的才是证据，盈余不够就多算位数或缩小常数环（:24-37）。搜索前写下常数环（每个常数为什么在里面）与系数上界并注明日期；正对照（已知闭式必须找回）和负对照（随机实数必须返回空）走同一条代码路径；在明显更高的精度下重跑，整数系数必须不变；用独立求值、在搜索没用过的位数上认证；找不到就报「在声明的环、上界、精度下无关系」，交付数值和任意精度求值器，不编名字（:41-89）。

**长处。** 「命中便宜，空结果只有对照声明的环才有信息量」（:17-22）把找到和找不到两种结果都定义成可报告的结论。7 条失败模式里的事后扩环、上界蠕变（:96-111）与 acceptance-gate 的门槛漂移属于同一类问题：看到结果后改判据。出处是 Ferguson 与 Bailey 的 PSLQ、Lenstra–Lenstra–Lovász 的 LLL，以及 Bailey、Borwein、Broadhurst 的实验数学实践（:196-205）。

**局限与适用前提。** 适用对象是用整数关系算法把高精度数值认成闭式常数，原文的例子与出处来自实验数学和量子场论（:196-205）。平台三处库里搜 PSLQ、integer relation 零命中，领域包只有 `generic` 与 `petab` 两个[^sk-cr-none]。工具包里有 `bootloops/tools/pslq_gate.py` 与 `bootloops/tools/lockpick/`，skill 正文不调用。它的两条通用做法（先声明再搜索、负对照必须返回空）在 acceptance-gate 第 0、5 步和「识别常数」的小例子（`skills/skills/acceptance-gate/SKILL.md:183-187`）里已经有。

**与平台已有能力的重叠。** 无。

### 4.8 tool-stewardship

**管什么。** 工具包怎么查、怎么扩、怎么写文档（:3、:8-10）。

**核心规则。** 写代码前按能力搜索引、读完候选工具的整页、先在已知答案上试跑；按「直接用、打补丁或扩展、包一层、新写」的顺序往上走，新写要用一句话写明查过哪些工具、为什么都不行（:16-19）；补丁打在上游原件上，接口不变或同一次改动迁移全部调用方，当天记录变更（:23-26）；新工具当天进工具树并写「四问页」：做什么、什么时候用、输出含义与失败长什么样、信它之前要过什么测试（:34-43）；重复工具合并到强的那个，删掉弱的并在旧名处留指针（:63）。失败模式 10 条。

**长处。** 四问页第 3 问要求写明失败输出与成功输出的区别，第 4 问要求写明信它之前要过什么测试（:40-41），与 planted-truth、acceptance-gate 的「检查要能失败」是同一要求，落在工具文档上。

**局限与适用前提。** 读者是维护工具包的开发者。没有出处。四问页样例写的是一个叫 `ratefit` 的运行时长预估工具（:46-57），工具包里搜不到这个名字，只有做有理函数重建的 `ratfit`，样例应是示意[^sk-ts-ratefit]。「补丁打在上游原件上」（:23）与平台分工冲突：执行层的可写范围锁在产出目录（`docs/architecture/open-questions.md:21`，Q-15），skill 库对它只读。

**与平台已有能力的重叠。** 外层仓规矩已有「有真实的第二个用例才抽象」「重构要彻底，旧入口逐个删干净」「一个事实只有一个家」（`CLAUDE.md:44`、`:45`、`:48`）。`platform/docs/add-a-skill.md:63` 要求 skill 正文写四件事：什么时候用、命令怎么敲、留下哪几个文件、常见失败怎么办。步骤描述符有 `does`、`does_not`、`brings`、`leaves`、`stops` 几栏（`platform/framework/capabilities/verify/__init__.py:29-60`），大致对应四问页的前三问；「信它之前要过什么测试」没有对应字段。

## 5. 研究 skill（5 个）

五个研究 skill 同样是纯文本、没有脚本（123 到 332 行）。lit-review、ref-check、referee-sim、prove-protocol 四个规定了可检查的产物（逐条主张的裁定、逐条目与逐主张的判定、判定表文件、带执行记录的工作文件），prose-lint 附了可直接运行的 grep 正则，五个的失败模式都按机制列出；原文对效果的说法（lit-review 的「highest-yield」、referee-sim 首轮「reliably surface findings」、prove-protocol 的 X0）都没有附运行次数或记录，三个仓里也没有找到这几个 skill 的产出样例，效果未验证。原样放进平台各有对不上的地方：lit-review 与 ref-check 点名的 NASA ADS 要 token、MathSciNet 要机构订阅，Semantic Scholar 匿名接口本机连试 3 次都是 429[^sk-measure]；referee-sim 与 prove-protocol 的核心保证来自隔离上下文，平台会话里没有子代理，P-2 隔离评审也未实现[^sk-fresh]；prose-lint 的 frontmatter 在平台解析器上报错[^sk-gate]。内容上，书目元数据核对、按主张分级的支持度、夸大词检查、检索边界台账在平台已收录的 skill 里已有；平台没有对应物的是 lit-review 的 P0–P5 分级与 FULL-TEXT-UNREAD 标记、ref-check 的五类主张判定、prose-lint 的英文套话词表与句式条目、referee-sim 的按读者群审摘要。

### 5.1 lit-review

**管什么。** 新颖性主张背后的文献审计（:3）。产物是逐条主张的裁定，原文写明只交阅读清单等于没做完（:162-169）。

**核心规则。**

- P0–P5 接近度分级（:31-44），义务随等级加码；按下面三条规则，P3 以上读全文、把相关的定理或构造逐字引用并给页码或节号、双向追引文链。
- 三条规则（:46-97）：读原文、不凭记忆，拿不到全文标 FULL-TEXT-UNREAD、等级只当上限；彻底性要有凭据：检索台账（写明年份范围，没涵盖当年的查询算缺陷）、精读台账、缺口声明（没搜的领域、语种、年份、中途断掉的通道）、迭代到新一轮在 P3 以上没有新增为止并报告轮数；引文链双向追，P3 以上作者的近作扫到当月。
- 流程 0–4（:144-171）：先把主张钉成 C1..Cn 和标题句；按学术脉络分 6–12 个方向检索；对 P3 以上跑引文链与近作；汇总成去重的最近作品表、P2–P3 致谢清单（与论文实际参考文献表对比）和逐条裁定；迭代到无新增。
- 「结果写进论文」一节（:173-188）规定先致谢最近的前人工作再陈述差异，引用只从已核实条目抄。它不写综述正文。
- 11 条失败模式（:190-240），其中「静默断掉的通道」（:220-226）要求因预算或访问受限断掉的检索通道写进缺口声明并算作欠账。

**检索靠什么。** skill 不带程序，工具包里也没有检索接口的代码[^sk-toolkit]。检索靠 agent 自己的联网搜索、网页读取和手动调用公开接口：原文首选有文档的接口（Semantic Scholar、OpenAlex、Crossref、arXiv、INSPIRE、PubMed、ADS），Google Scholar 只许人手按人的速度查，自动请求间隔约 2 秒，查不了的服务写进缺口声明（:101-106）；领域数据库另列 zbMATH、MathSciNet、INSPIRE、PubMed（:135-136）。本机 macOS（Apple Silicon）2026-10-02 用 curl 不带凭据实测[^sk-measure]：

| 服务 | 匿名访问结果 |
|---|---|
| NASA ADS | 401，`Missing "Authorization" in headers.` |
| MathSciNet | 跳转到 connect.liblynx.com 的机构登录页 |
| Semantic Scholar | 连试 3 次，均为 429 |
| OpenAlex | 200，按日计额度（见下） |
| Crossref、INSPIRE、zbMATH、DBLP、PubMed、arXiv | 200 |

OpenAlex 的额度按响应头读：`search=` 与 `title.search` 这类全文检索一次记 10 credit，按 DOI 或 `cites:` 的精确过滤一次记 1，单条 ID 查询记 0；每日上限 1000 credit，另有每日 0.1 美元的额度，一次关键词检索记 0.001 美元。两种额度都折合约每天 100 次关键词检索，引文链查询与之共用同一份 1000 credit[^sk-openalex]。原文要求每找到一个新同义词就在所有用过的引擎上重查，并迭代到新一轮无新增（:80-82、:137-142），每天约 100 次关键词检索会限制能跑的轮数。第一次请求后剩余 918，即测试前当天这个出口 IP 已用掉 72 credit；实验室多人共用出口 IP 时额度是否共享，未验证。原文致谢把 NASA ADS 与其他几家一起称为「open APIs」（:264-266）；实测 ADS 接口不带 token 返回 401，要注册账号取 token。平台的零 key 门禁扫 lit-review 命中 0 处，因为原文只点名 ADS、MathSciNet，没有写凭据字样；这类「点名需要账号的服务」门禁查不出[^sk-gate]。

拿全文的正当途径原文列了开放获取版本、作者自贴副本、机构订阅、馆际互借、向作者索取，并禁止绕过访问控制（:61-67）；机构订阅依赖研究者自己的校园网或登录。并行子代理可选，原文写了「parallel subagents if your framework supports them; sequential passes otherwise」（:152-154）。

**保密稿件。** 原文开头规定：审稿时按期刊对 AI 辅助和稿件保密的规定办，很多期刊禁止把在审稿件交给 AI 工具；这种情况下只对公开文献跑这套流程，不碰保密稿件本身，期刊要求时向编辑披露（:23-29）。平台已收录 `nature-reviewer`、`peer-review` 这类审稿 skill，研究者用它们审别人的稿件时同样涉及这条。

**局限与适用前提。** 定位是给已有主张做审计：第 0 步要求先写出编号的新颖性主张和标题句（:146-150），研究者刚进课题、还没有主张时怎么用，原文没写。只列英文渠道，没有 CNKI、万方。原文称「取最强的已知前人工作的前向引文、按新到旧细读近两年标题」是「the highest-yield single move」（:253-258），没有附运行记录；三个仓里没有找到 lit-review 的产出样例，实际效果未验证。

**与平台已有能力的重叠。** 平台文献阶段没有步骤，[#154](https://github.com/zephyr4123/TJU-AI4Science/issues/154) 列了五段缺口：检索、逐篇取证、组织结构、带引用成文、引用核对[^sk-154]。lit-review 覆盖逐篇取证与检索纪律，组织结构只到最近作品表与逐条裁定，不写综述正文，引用核对交给 ref-check（:180-182）。已收录的 `platform/skills-curated/hypothesis/reasoning/hypothesis-generation` 第 4 步要求写带日期的检索边界（检索日期、数据库、检索式、纳排、语言与时间限制），只许说「在记录的检索范围内没找到」（`SKILL.md:97-109`），并有 `scripts/audit_evidence_ledger.py` 机器核对台账；它的 `references/literature_search_strategies.md` 还写了前后向引文追踪（:96-100）和写明的停止规则，其中包括「saturation documented」（:170-178）。这部分与 lit-review 的检索台账、缺口声明、双向引文链和迭代到无新增重叠。lit-review 独有的是 P0–P5 分级与对应义务、FULL-TEXT-UNREAD 标记、P3 以上作者的近作扫到当月、把断掉的通道算作欠账、先钉主张再逐条给出逆着利益的裁定。`platform/skills-curated/literature/search/paper-lookup` 给出 18 个免注册学术接口的用法与辅助脚本，包括引文图查询（`SKILL.md:3`、`:56-57`），是 lit-review 没有的工具一侧。同类的 K-Dense literature-review 因检索要 Parallel 账号、配图要 OpenRouter key 被拒收（`platform/skills-curated/provenance.yaml:2055-2058`）。

paper-lookup 对 OpenAlex 的说明是「Filters and ID lookups work; anonymous `search=` is rate-limited under load」（`platform/skills-curated/literature/search/paper-lookup/SKILL.md:129`，`:152` 有同样的说法），没有写按日计的 credit 额度；按上面的实测，`title.search` 这类全文检索 filter 与 `search=` 一样每次记 10 credit。

### 5.2 ref-check

**管什么。** 参考文献的核对与新增：作者、标题、期刊、卷、页、年、arXiv 号、DOI 一律拿抓取到的权威记录逐字段比对，不凭记忆（:10-15）。原文给的理由是书目多从别的书目抄来，模型记住的是多数写法，流传开的错误恰好就是多数写法；模型凭记忆写出的条目是「a fabrication with correct formatting」（:17-32）。

**核心规则。**

- 按学科列权威来源（:34-53）：CrossRef 与出版方 DOI 页为主干，物理用 INSPIRE（:41 给了直接出 BibTeX 的 URL 模板）与 arXiv abs 页，数学用 zbMATH、MathSciNet，天文用 ADS，生命科学用 PubMed，计算机用 DBLP，软件用 Zenodo 或 CITATION 文件。Google Scholar、Semantic Scholar 只用来找，不用来核（:55-58）。
- 逐字段语义比对，条目判 OK、MINOR、FIX、UNVERIFIABLE、INTERNAL 五类；DOI 必须实际解析并比对着陆页标题（:66-94）。
- 13 条实测出现过的流传性错误（:96-149），例如截断的作者列表、同姓作者合并成一人、正确的预印本号挂着另一篇论文的期刊信息、凭记忆写的描述性标题。
- 主张核对层（:151-184）：被引作品是否真说了句子里的话。打开全文，记录定理、公式或页码定位，判 SUPPORTED、DRIFTED（主张成立但出自另一篇）、INFLATED（原文只证明了特例或更弱的形式）、ABSENT、CONTRADICTED 五类；只报告，不替作者改意思（:172-174）。
- 流程（:186-219）：新增条目小批量做，每条打 `% VERIFIED <日期> <URL>`，查重 key 也查重作品；全文件审计分块并行、只报告，修复串行做；改 key 要 grep 全部 `\cite`；最后完整重编译（例如 pdflatex 加 bibtex），零错误、零未定义引用才算过，并确认渲染结果带上了修复。

**依赖。** 联网抓取；`grep`；重编译需要系统里装 LaTeX；并行子代理可选（:201-203）。本机实测 INSPIRE 的 BibTeX 接口、Crossref、zbMATH、DBLP 均返回 200；点名的 MathSciNet（:48）与 ADS（:49）分别要机构订阅和 token[^sk-measure]。致谢要求用过 ADS 的工作附 ADS 的致谢语（:240-242）。

**长处。** 陷阱一节写明全部来自实际审计（:96-100），其中几条带了计数或具体情形，例如同一次审计里描述性标题出现 5 次（:132-135）、一次审计里 3 条给名写错、1 条多出合作者（:136-139）。「只报告、不改正文」把核对者与作者的职责分开。作者在 JaCKandJill 的模型说明里用「ref-checked」标注出处（`jackandjill/MODELS.md:31`、`:293`、`:499`），说明这套流程在作者自己的项目里用过；没有公开的审计日志。

**局限与适用前提。** 只列英文来源，没有中文 DOI 与 CNKI、万方。重编译一步假定稿件是 LaTeX；平台收录规则把核心离不开装系统软件的 skill 排除在外（`platform/docs/add-a-skill.md:111`），已收录的 nature-polishing 收录时删掉了要编译 LaTeX 的排版那一支（`platform/skills-curated/provenance.yaml:1567`）。

**与平台已有能力的重叠。**

- 元数据层：`platform/skills-curated/verification/references/nature-ref-verifier` 先查 DOI 能否在 Crossref 解析（`SKILL.md:45`），列了「DOI 张冠李戴」这类错误（`:72`），中文文献经网页搜索查 CNKI、万方（`:54`、`:171-173`）。两者在这一层大部分重叠，中文覆盖只有 nature-ref-verifier 有。
- 主张层：已收录 skill 里有三个做了一部分。`literature/search/nature-citation` 按主张给支持度分级 strong、partial、background、contradictory/limiting、metadata-only，失败模式里写了「把关联写成因果」，与 INFLATED 相近，但它的用途是为 Nature 系期刊稿件找支撑文献；`writing/manuscript/scientific-writing` 要求每个来源记确切的支持位置，并确认来源在方向、人群、结局、不确定性上支持主张；`verification/rigor/ara-rigor-reviewer` 的 D1 Evidence Relevance、D3 Scope Calibration 查引文是否实质支持主张[^sk-rf-overlap]。
- ref-check 独有的是 DRIFTED、ABSENT 两类及整套五分类，强制记定位且摘要只能核摘要级主张（:159-164），只报告不改写，以及它审计的是已有的 `.bib`。
- 平台验证阶段的「引用真伪」判据未实现（`docs/architecture/workflow.md:177`）。

### 5.3 prose-lint

**管什么。** 科研文字的清晰度与诚信 linter（:3）。总测试是：这句话会不会有一位具体的科学家当面对同事说出来（:8-15）。原文写明它不用于掩盖 AI 参与，按期刊要求披露（:17-19）。

**核心规则。** 298 行，按类编号：A 节禁用或可疑词汇（hype 词、营销形容词、套话、weasel 开头、总结式开头，:29-39）；A2 比喻与语域（:41-55）；A3 无主体文字，含一张流水线词汇对照表（:57-98）；B1–B17 句式（:102-144）；C 节奏，其中 C4 规定全文至多一个破折号（:153）；D 格式（:157-159）；E1–E6 诚信，包括编造的具体数字、抬高重要性、出处错误、过度宣称、自信的含糊、区间与引号（:163-170）；N1–N13 数字纪律（:172-188）；F 先于找毛病的语法与成文检查（:192-208）；G 清扫流程（:210-224）；一组 grep 正则（:228-251）；编辑时注释吞掉后一句的检查（:254-288）。原文把诚信与数字两类定为最先查的两类（:25、:218）。

**长处。** 多数条目给了改法与例句。N 节针对正文、表格、图注之间的数字不一致给了可以机械检查的规则，例如 N4 指出 141/400 = 0.3525 在浮点格式化与四舍五入显示下会打印成不同的数（:179）。G 节第 8 条要求外部发现的漏网句子既修句子、又把句式补进目录（:219）；第 9 条写明「lint 到不动点」只说明这一遍扫不出更多，不能当质量宣称（:222）。出处写明 A 节词表与 Kobak 等（Sci. Adv. 2025）、Liang 等（arXiv:2403.07183）和维基百科「Signs of AI writing」大量重叠，B 节多源自 Orwell 与 Gopen、Swan（:290-298）。

**局限与适用前提。**

- frontmatter 在平台解析器上报错：`description`（:3）没加引号，内容里有 `linter: hype` 这样「冒号加空格」的写法；平台用 `yaml.safe_load` 解析（`platform/framework/skills/library.py:300`），本机实测报 `mapping values are not allowed here`，位置在第 3 行第 112 列，原样放进库会被隔离。其余 11 个都能通过[^sk-gate]。
- 词表与句式只适用于英文。
- N1（实测的位数只许往弱的方向舍入，:176）针对「已验证位数」这类计数，属于高精度数学语境；E6（认证区间往外舍入，:170）要求先知道哪些数是区间。平台 `verify` 用 1% 相对容差、不看舍入方向，也没有「区间」这种结构，这两条用到平台上需要另加结构[^sk-pl-verify]。
- F 节第 9 条（:204）与 :254-281 的注释吞句检查要求读渲染后的文档，前提是稿件经过 LaTeX 这类渲染。工具包的 `bootloops/tools/emitall/paper_seams.py`（MIT）对 LaTeX 稿件做同类的注释吞句检查（`bootloops/tools/emitall/paper_seams.py:2`、`:10-12`），skill 正文不引用它。

**与平台已有能力的重叠。** 已收录的 `platform/skills-curated/writing/manuscript/scientific-writing` 带确定性脚本 `scripts/lint_manuscript.py`，查夸大词（`OVERSTATEMENT_RE`，`:50-54`）、因果措辞（`CAUSAL_RE`，`:55-57`）和占位符，同目录还有 `check_consistency.py`、`audit_claims.py`；`nature-polishing` 禁破折号（`static/fragments/language/en.md:12`），`nature-writing` 禁无依据的「the first」「unprecedented」（`references/submission-package.md:81`）。平台三处库里搜 delve、tapestry、「signs of ai writing」零命中；`lint_manuscript.py` 的规则只有占位符、敏感信息、伦理与资助等声明、夸大词、因果措辞与主张标记几类，没有句式规则[^sk-pl-overlap]。A 节那类词表与 B 节句式在平台没有对应。

### 5.4 referee-sim

**管什么。** 文档对外发出前的框架审计：事实核查确认每句是真的，这一遍查读者会得出什么结论（:8-10）。

**核心规则。** 七步（:14-68）：

- 书面列出所有可能写审稿意见的读者群：引言点名的、借用了其方法或结果的、现有做法的一方（incumbent）、拿结果去用的实践者、期刊的一般读者；借用了谁的方法、数据或基准，谁就必须有一行（:25）。
- 每个读者群分别写一条正确性质疑、一条新颖性质疑，并按群体类型校准：工程应用、实验、数值、形式理论、incumbent 各有第一个会问的问题（:27-42）。
- 用 sting、knowledge、lead 三个测试把质疑做到最强（:44-50）。
- 检查答案是否落在质疑者的阅读路径上（标题、摘要、图、结论），按 HIGH、MEDIUM、LOW 定严重度（:52-56）。
- 最后单独冷读审摘要（:58-60）。
- 只做最小的防御性修改：一句范围句、把限定挪到显眼处，不许到处加限定把主张弱化（:62-64）。
- 在文档旁写 `referee_sim_<doc>.md` 判定表，没改任何东西也要写（:66-68）。

另有 9 条失败模式（:70-80）和 6 项每次都做的交叉检查（:95-102），其中一项是对照项目自己的结果文件找矛盾（:98）。

**依赖。** 一个新的 agent 上下文，原文写明不能是写文档的那个上下文（:106），否则落入「作者上下文污染」（:80）；能重新编译或渲染文档（:64）；能读项目自己的结果文件。原文没有要求联网，也不要 key。

**长处。** 它查的问题与逐句核查不重叠：每句都真但拼起来误导，限定只写在正文、摘要里没有（原文称 abstract firewall，:77）。按读者群列质疑，并规定借用了谁的方法谁就必须有一行，把审稿视角落成一张可以逐行检查的表；附了一张四行的示例读者表（:82-93）。

**局限与适用前提。** 核心保证来自隔离上下文。平台会话里没有子代理或单独起的上下文；纲领 P-2「框架派隔离会话、只给产物不给轨迹」这一段尚未实现；收录规则把核心离不开子代理的 skill 排除在外[^sk-fresh]。在写稿的同一个会话里照步骤跑，就是原文自己点名的作者上下文污染。「Expected yield」一节说首次运行「reliably surface findings, often HIGH-severity ones」（:110-112），列了四类典型发现，没有给运行次数或运行记录；三个仓里没有找到 referee-sim 的判定表，效果未验证。

**与平台已有能力的重叠。** `platform/skills-curated/writing/review/nature-reviewer` 的 originality 轴与 readability for nonspecialists 轴（`references/review-axes.md:5-7`、`:17-19`）以及「谁会对结果感兴趣」（`SKILL.md:26`）与它部分重叠；nature-reviewer 另有三份互盲报告加综合，并在 `SKILL.md:23` 写明在这个环境里互盲无法保证。`writing/review/peer-review` 的主张与证据对照（`SKILL.md:128` 起）有少量重叠。referee-sim 独有的是按学术群体列读者（含借用方法的群体与 incumbent）、每群两轴、阅读路径、冷读摘要、禁止到处加限定和判定表文件。

**对上平台的位置。** P-2 的隔离模型评审：只给稿子，不给轨迹；「对照项目自己的结果文件」对应 `results.json` 与 `analysis.md`。

### 5.5 prove-protocol

**管什么。** 用多个 agent 证明或证伪数学命题（:3）。命题评为 VERIFIED-CLOSED 的条件：指定的反驳者带着执行过的精确算术没能驳倒，并且一个没参与写作的 agent 只照规格从头重建、用新代码复现了全部预先登记的数值（:10-14）。原文写明这是给 agent 产出的工作标准，不替代审稿或形式化证明（:14-16）。

**核心规则。**

- 情形 1，命题已知（:48-126）：对抗者先上（X0），在退化与边界实例上找精确反例；把目标钉成共享规格：命题原文、MAY-ASSUME 与 MUST-NOT-ASSUME 清单、带验收标准的备选形式、精确测试实例 T1 与判死条件、勘误通道；证明者与怀疑者循环，怀疑者的报告必须是 `{步号, 实例, 两边的值, 残差}` 这种机器可读格式，纯文字批评不算；在副本上埋一个已知错误的步骤，审核抓不到就判这一路无效；至少两个走不同路线、互不看对方的证明者；新上下文交叉验证，并追查交付物在下游的每个使用点。
- 10 条失败模式（:128-182）；基础设施规则（:184-211），例如先写工作文件骨架、运行中不插话、日志随做随落盘、长时计算脱离会话。
- 情形 2，命题本身未知（:213-250）：先建精确评估器与已认证对象语料，开强制分路线的理论锦标赛，做不变量合成，记录每个被驳倒的表述和杀死它的反例。
- 前置条件（:252-275）：可精确计算、几秒内枚举完的 T1，预先登记的备选形式，已有明确假设的下游使用方。原文引用的无前置条件基线：LemmaBench 冷启动成功率 10–15%，Proof or Bluff 中多数模型在 USAMO 2025 的平均证明分低于 5%。

**长处。** 主要规则都标了来源方法：埋错审计对应变异测试，强制多样性对应 Knight 与 Leveson 的多版本实验，「纯文字批评无效」引用 Huang 等关于内在自我纠错的结果（arXiv:2310.01798），对抗者与证明者交替对应反例引导的归纳综合（:30-35、:292-307）。「哪些做法有效、哪些无效」单列一节（:277-290），列了无效的：没有机械认证器的端到端自动证明、自报信心、只看最终答案的基准、纯文字批评。

**局限与适用前提。** 适用范围是数学命题，评级、T1 与基准成功率都按证明写（:3、:252-275）。核心依赖多个新上下文、并行证明者、CAS 或精确算术脚本、能脱离会话的长时计算（:102-126、:206-208），平台会话里没有子代理[^sk-fresh]。原文对效果的说法，例如 X0 是「reliably the highest-value step per token」、「One agent-run; it often saves ten」（:50、:65），没有附运行次数，未验证。平台 `docs/cases/` 下七个案例里没有数学证明类课题。

**与平台已有能力的重叠。** `platform/skills-curated/hypothesis/reasoning/hypothesis-generation` 有竞争假设（`SKILL.md:111-127`）、可区分的预测（`:150-163`）和防事后假设（`:202-213`）；`hypothesis/ideation/scientific-brainstorming` 第 7 步有对抗评审，但只是文字提问，不要求跑出反例（`SKILL.md:139-152`）。平台没有「埋一个错看审核能不能抓到」的做法[^sk-pp-overlap]。

**对上平台的位置。** 「对抗者先上」「批评要带实例和数值」对应假设阶段；埋错审计对应设计阶段给 `evaluate.py` 跑负对照（与 [4.4](#44-planted-truth) 是同一件事）；驳倒表述清单对应 AutoResearch 的失败记录。

### 5.6 横向对照

| skill | 管什么 | 依赖 | 已有重叠 | 收录门槛 |
|---|---|---|---|---|
| lit-review | 新颖性主张的文献审计 | agent 联网与公开接口；子代理可选 | hypothesis-generation 的检索边界、台账脚本、引文追踪与停止规则；paper-lookup 的检索脚本 | CC BY 4.0；点名 ADS（要 token）、MathSciNet（订阅），零 key 扫描查不出 |
| ref-check | 书目逐字段核对与主张核对 | 联网；grep；LaTeX 重编译；子代理可选 | nature-ref-verifier 元数据层（含中文）；nature-citation、scientific-writing、ara-rigor-reviewer 的主张支持度 | CC BY 4.0；点名 ADS、MathSciNet；重编译一步要系统 LaTeX |
| prose-lint | 英文科研文字 linter | grep；渲染后的稿件 | scientific-writing 的 lint 脚本；nature-polishing、nature-writing 的禁用规则 | CC BY 4.0；frontmatter 解析失败被隔离 |
| referee-sim | 对外发出前的框架审计 | 新的隔离上下文；可渲染文档；项目结果文件 | nature-reviewer 部分；peer-review 少量 | CC BY 4.0；核心离不开隔离上下文 |
| prove-protocol | 多 agent 证明数学命题 | 多个新上下文；CAS 或精确算术；脱离会话的长计算 | hypothesis-generation、scientific-brainstorming 部分 | CC BY 4.0；核心离不开子代理 |

[^sk-gate]: 本机 macOS（Apple Silicon）实测，2026-10-02。在内仓目录下用平台自己的门禁函数逐个加载 BootLoops skills 仓 `skills/` 下的 12 个目录：`framework.skills.library.load_skill(<目录>)` 后跑 `library.key_mentions(skill)`（`platform/framework/skills/library.py:258`、`:366`），并与平台三处库的名字比对。结果：11 个加载成功、`key_mentions` 均为 0、无 `scripts/`、无重名、frontmatter 无 `license` 字段；prose-lint 报「frontmatter 不是合法 YAML：mapping values are not allowed here」，位置 `line 3, column 112`。各文件行数：`wc -l skills/skills/*/SKILL.md`，协议层 95–209 行，研究 skill 123–332 行（referee-sim 123、ref-check 242、lit-review 285、prose-lint 298、prove-protocol 332）。门禁只认凭据字样，不认「需要账号的服务」，后者按 `platform/docs/add-a-skill.md:110` 与纲领 P-27（`docs/architecture/README.md:177`）由收录的人判断。

[^sk-sources]: 「None of the ideas here is new; what is ours is their assembly into one gate」见 `skills/skills/acceptance-gate/SKILL.md:200-201`；planted-truth 末尾「We claim only the checklist」（`skills/skills/planted-truth/SKILL.md:204-205`）。带出处节的：acceptance-gate、constant-recognition、planted-truth、lit-review、prose-lint、prove-protocol 六个有「Sources and acknowledgments」，ref-check 有致谢基础设施的「Acknowledgment」（`skills/skills/ref-check/SKILL.md:237-242`）；independence-bookkeeping 末尾一句引 Knight 与 Leveson（`skills/skills/independence-bookkeeping/SKILL.md:189-192`）；referee-sim 只在操作说明里引 Klein 的 pre-mortem（`skills/skills/referee-sim/SKILL.md:108`）；timing-discipline、reading-contract、tool-stewardship 用 `grep` 查年份、arXiv、et al.、期刊缩写均无命中。README 的说法见 `skills/README.md:215-219`。

[^sk-platform-license]: 收录白名单 `LICENSES = ("MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "ISC")`，注释写明 CC-BY 系列不收（`platform/framework/skills/provenance.py:53-55`）；收录规则第 1 条（`platform/docs/add-a-skill.md:109`）；决定记录在 [#198](https://github.com/zephyr4123/TJU-AI4Science/issues/198)。

[^sk-toolkit]: `grep -niE 'toolkit|tools/|lockpick|nestor|emitall|gatekeeper|pip install|\bmcp\b|api key|\.py\b|python'` 扫 12 个 `SKILL.md`，只命中 tool-stewardship 的「toolkit」泛指（`:3`、`:8`、`:31`）。工具包仓（`bootloops/`，提交 66b680c）里 `grep -rIl -iE 'semanticscholar|api\.openalex|api\.crossref|inspirehep|export\.arxiv'` 无输出，没有支撑 lit-review、ref-check 的检索代码。

[^sk-license]: 许可证原文 <https://creativecommons.org/licenses/by/4.0/legalcode>，§3(a)(1) 列出署名、保留版权声明、注明许可证并给出链接、写明是否修改。`skills/LICENSE-CONTENT:5-8` 给出署名串与许可证链接。以上为对许可证文本的阅读，未经法律人士确认。

[^sk-plugins]: 本机实测：在 skills 仓根目录跑 `python3 tools/make_plugins.py --check`，输出 `up to date: 2 plugins, 12 skills`，退出码 0；对 12 个 skill 逐个 `cmp skills/<name>/SKILL.md plugins/*/skills/<name>/SKILL.md`，全部相同。插件分组见 `skills/tools/make_plugins.py:60-82`。

[^sk-setup]: 安装器原文 `skills/.claude/skills/bootloops-setup/SKILL.md:10-11`（不经明确选择不激活任何东西）、`:42-48`（问范围、缺省项目级、只拷贝选中的目录）。平台的加载方式见纲领 P-22（`docs/architecture/README.md:172`）：「加载不靠任何 agent 的原生机制：框架起会话时把本项目装载的那套拼成清单进 prompt」。

[^sk-ag-stochastic]: 第 4 步原文 `skills/skills/acceptance-gate/SKILL.md:65-69`，第 6 步原文 `:79-84`，两步都以「工作精度」「锚点重拟合」为前提；全文没有说明哪些条款在带随机性的设定下不适用。

[^sk-holdout]: 内环种子取自基线 `results.json`（`platform/framework/experiment/context.py:88`），每轮 `compute.submit` 传的都是这个种子（`platform/framework/capabilities/auto_research/judge.py:66-68`）；`verify` 的 `does_not` 写明「不重跑任何实验」（`platform/framework/capabilities/verify/__init__.py:43`）。`grep -rniE 'holdout|held.out|留出|验证集|测试集' platform/framework` 无输出；各任务的 `evaluate.py` 内部是否自行切分数据，未逐个检查。单向污染与反事实判据见 `skills/skills/independence-bookkeeping/SKILL.md:30-42`，「隔了一层的污染」见 `:119-121`。

[^sk-125]: [#125](https://github.com/zephyr4123/TJU-AI4Science/issues/125) 正文：PINNs 演练里三轮改动各好 0.6e-3 到 0.9e-3，统计门 1.77e-3，三轮全部 discard；issue 列了三种解法。门的算法见 `platform/framework/capabilities/auto_research/gate.py:17-40`。门槛漂移原文 `skills/skills/acceptance-gate/SKILL.md:142-146`。

[^sk-pt-harness]: 构造式夹具原文 `skills/skills/planted-truth/SKILL.md:68-74`。框架对 harness 的检查见 `platform/framework/experiment/pack.py:218-286`（三件套齐全、脚本不裸调 python、环境变量不写默认值、`SHA256SUMS` 与磁盘一致），没有运行 `evaluate.py` 的步骤；`make_run0` 结尾会删掉产物（`platform/framework/capabilities/design/prompt.md:104`）。

[^sk-td-claude]: `grep -i claude skills/skills/*/SKILL.md` 无命中。客座文章 <https://www.anthropic.com/research/claude-shaped-science> 原话：「I never succeeded in getting Claude to estimate time well.」「Claude's default approach seemed to be to try to grind through a long, multiday calculation rather than build a new tool」。

[^sk-rc-63]: 总论文 <https://www.bootloops.ai/BootLoops.pdf> §6.3「Audits of published numbers」（p.20）：「the number in question can be reproduced from the published inputs; it is determined only under unstated conventions; it is undetermined by what was published; or it cannot be examined at all」。与 `skills/skills/reading-contract/SKILL.md:59-65` 的四种结论逐项对应。页码按 PDF 页序，2026-10-02 对照下载的 PDF 文本核对。

[^sk-cr-none]: `grep -rniE 'pslq|integer.relation' platform/skills platform/skills-curated platform/domains` 无输出；`grep -rnw LLL platform/skills-curated` 只命中 `platform/skills-curated/experiment/physics/pymatgen/references/core_classes.md:127` 的晶胞 Niggli/LLL 约化。`platform/domains/` 下只有 `generic`、`petab`。

[^sk-ts-ratefit]: `ls bootloops/tools`（提交 66b680c）有 `ratfit`，无 `ratefit`；`grep -rn ratefit` 在工具包仓内无输出；`bootloops/tools/ratfit/GUIDE.md:5`、`:16` 写明它是基于 python-flint 与 fractions 的有理函数精确重建与门控套件。四问页样例原文见 `skills/skills/tool-stewardship/SKILL.md:46`（「ratefit — runtime projection from a partial log」）。

[^sk-measure]: 本机 macOS（Apple Silicon）实测，2026-10-02 约 04:52 UTC 与 05:16 UTC 各一次，curl 不带任何凭据，两次结果相同。`curl -s -w '%{http_code}' 'https://api.adsabs.harvard.edu/v1/search/query?q=star'` 返回 401，响应体 `{"message": "Missing \"Authorization\" in headers."}`；`curl -s -L -o /dev/null -w '%{http_code} %{url_effective}' 'https://mathscinet.ams.org/mathscinet/api/publications/search?query=pslq'` 最终落在 `https://connect.liblynx.com/wayf/…`；`https://api.semanticscholar.org/graph/v1/paper/search?query=physics+informed+neural+network&limit=1` 间隔 2 秒连试 3 次，均为 429；INSPIRE `https://inspirehep.net/api/literature?sort=mostrecent&size=1&q=arxiv%3A1711.10561&format=bibtex`（返回 BibTeX）、`https://api.crossref.org/works/10.1016/j.jcp.2018.10.045`、`https://api.zbmath.org/v1/document/_search?search_string=pslq`、`https://dblp.org/search/publ/api?q=physics%20informed&format=json`、PubMed `esearch.fcgi`、`https://arxiv.org/abs/1711.10561` 均为 200。

[^sk-openalex]: `curl -s -D - -o /dev/null '<URL>'` 读响应头，2026-10-02：`/works?search=physics%20informed%20neural%20network` 与 `/works?filter=title.search:pinn` 都是 `x-ratelimit-credits-used: 10`、`x-ratelimit-cost-usd: 0.001`；`/works?filter=doi:10.1016/j.jcp.2018.10.045` 与 `/works?filter=cites:W2741809807` 都是 `credits-used: 1`；`/works/W2741809807` 是 `credits-used: 0`。共同的头：`x-ratelimit-limit: 1000`、`x-ratelimit-limit-usd: 0.1`、`x-ratelimit-reset: 68853`（约 19 小时），第一次请求后 `x-ratelimit-remaining: 918`。05:16 UTC 复测，五个请求的扣费与上面相同，另有 `x-ratelimit-cost-usd: 0.0001`（doi、cites 两种 filter）与 `0`（单条 ID）。filter 按种类计费：`title.search` 这类全文检索 filter 记 10，`doi`、`cites` 这类精确 filter 记 1。

[^sk-154]: [#154](https://github.com/zephyr4123/TJU-AI4Science/issues/154) 的评论（2026-09-27 列出五段缺口与 14 个问题，2026-10-01 评论仍是缺口），2026-10-02 用 `gh issue view` 核对，issue 仍为 OPEN。

[^sk-rf-overlap]: nature-citation 的支持度分级与失败模式：`platform/skills-curated/literature/search/nature-citation/references/search-strategy.md:22-48`，用途见同目录 `SKILL.md:3`。scientific-writing 的核对步骤：`platform/skills-curated/writing/manuscript/scientific-writing/references/evidence_workflow.md:46-58`（第 3 条记确切支持位置，第 4 条确认方向、人群、干预或暴露、结局、时间点、不确定性）。ara-rigor-reviewer 的 D1、D3：`platform/skills-curated/verification/rigor/ara-rigor-reviewer/SKILL.md:40`、`:42`。

[^sk-pl-verify]: `DEFAULT_TOLERANCE = 0.01`（`platform/framework/capabilities/verify/__init__.py:27`）；`verify` 的模块说明写明「整数与百分比不查」（`platform/framework/capabilities/verify/checks.py:7`）。N1、E6 原文见 `skills/skills/prose-lint/SKILL.md:176`、`:170`：N1 的例子是「已验证位数」这类计数，E6 的对象是认证区间的端点。

[^sk-pl-overlap]: `grep -rniE 'delve|tapestry|signs of ai' platform/skills platform/skills-curated platform/domains` 无输出。scientific-writing 的脚本目录 `platform/skills-curated/writing/manuscript/scientific-writing/scripts/` 下有 `lint_manuscript.py`、`check_consistency.py`、`audit_claims.py` 等 8 个工具；`lint_manuscript.py` 的规则集中在 `:24-59`（`PLACEHOLDER_PATTERNS`、`SENSITIVE_PATTERNS`、`DECLARATION_RE`、`OVERSTATEMENT_RE`、`CAUSAL_RE` 与主张、证据标记）。

[^sk-fresh]: `platform/skills-curated/writing/review/nature-reviewer/SKILL.md:23`：「This environment has no subagents or separately launched contexts」；平台收录 nature-reviewer 时的改动记录写明「平台没有子代理」，把互盲审稿改成三份报告依次写（`platform/skills-curated/provenance.yaml:1608`）；纲领 P-2「这一段尚未实现」（`docs/architecture/README.md:152`）；收录规则第 3 条「核心做法离不开 MCP 服务、子代理……的不收」（`platform/docs/add-a-skill.md:111`）。referee-sim 的要求见 `skills/skills/referee-sim/SKILL.md:80`、`:106`。

[^sk-pp-overlap]: `grep -rIl -iE 'planted|sneaky|mutation test' platform/tests platform/framework platform/coordinator platform/docs` 无输出。埋错审计原文 `skills/skills/prove-protocol/SKILL.md:94-96`，失败模式「The harness that cannot fail」见 `:155-159`。

## 6. 计算工具包

BootLoops 工具包（`bootloops` 仓，提交 66b680c）由 49 个包（以 Python 为主，少数带 Julia 组件）、3 个 Julia 引擎和一套自检脚本组成，每个包配一份写给 agent 的 GUIDE.md 和一条固定的自检命令；按各包自述的用途数，34 个服务费曼积分、散射振幅等理论物理计算与数学物理，其余 15 个里 14 个是学科无关的认证数值、整数关系识别、统计证据与结果核对工具，1 个（popcorn）服务群体遗传[^tk-count]。本机 macOS（Apple Silicon）按 INSTALL.md 的步骤跑全量自检（并行数取 6），92.7 s 跑完，42 PASS、3 按设计拒跑、4 FAIL；4 个 FAIL 里 2 个缺 Julia，2 个是读 Linux `/proc` 的代码；42 个 PASS 里至少 23 个的输出含跳过或未验证的子项，汇总表不区分[^tk-full]。平台现有 7 个案例的课题与 34 个理论物理、数学物理包服务的对象不重合，其余 15 个包解决的问题在现有课题的流程里也没有对应步骤，本轮不收录；工具包的说明写法与失败处理方式和平台的 skill 规范有可对照之处，见 [6.8](#68-和平台的关系)。

### 6.1 组成

| 部分 | 内容 | 规模 |
|---|---|---|
| `tools/` | 49 个包，一包一目录，各带 GUIDE.md；另有共享夹具 `fixtures/` 与 26 个顶层兼容 shim 与成员文件（提供扁平导入名） | 28 MB；49 份 GUIDE 共 8723 行 |
| `upgrades/` | 3 个随仓发布的 Julia 引擎：Eichler.jl（Eichler 积分与 sunrise 周期）、SOFIA.jl（SOFIA 的 Julia 移植，去掉 Wolfram 依赖）、leviathan（Landau 奇点的 Euler 示性数下降法） | 4.8 MB，全部 MIT |
| `ops/` | turnstile：共享 Linux 机器上长作业的准入控制 | 1 个包，自检 runner 不覆盖 |
| `toolkit/` | `ours/README.md` 按主题列包；`ours/RECIPES.md` 8 条带必查项的配方；`external/TOOLS.md` 外部引擎清单 | 3 个文件 |
| 根目录 | `run_selftests.py`、`INSTALL.md`、`THIRD_PARTY.md`、`REFERENCES.md`；自检命令清单在 `tools/BATTERIES.json` | |

出处：`bootloops/README.md:104-124`、`bootloops/upgrades/README.md:10-14`、`bootloops/ops/README.md:13-15`、`bootloops/toolkit/ours/RECIPES.md:1-9`。全仓 2061 个受版本管理的文件，其中 Python 949 个约 24.3 万行，Julia 160 个约 4.3 万行[^tk-scale]。`ls tools/` 列出 78 个条目，包是其中 49 个，其余是 `fixtures/`、26 个兼容 shim 与成员文件（含 1 个 `.sh`、1 个 `.jl`）和 `README.md`、`BATTERIES.json` 两个索引文件（`bootloops/tools/README.md:24-31`、`:101-103`）；统计包数以 49 为准。

- **兄弟仓库**。README 写明 BootLoops 由 6 个仓组成（`bootloops/README.md:128-156`；GitHub 组织下另有收反馈的 feedback 仓，见[第 1 节](#1-来源与范围)）：本仓；`skills`（工作协议）；`jackandjill`（系统发育模型的贝叶斯证据包 phyloexact）；三个打过补丁的第三方引擎分叉 `kira`（Kira 3.1，GPL-3.0-or-later）、`blade`（MIT）、`amflow-cpp`（MIT），各带 `PATCHES.md` 记录相对上游的改动（`bootloops/upgrades/README.md:16-25`）。代码默认兄弟仓检出在本仓旁边的 `../<name>`。skills 与 JaCKandJill 在本报告其他章节讨论。
- **安装方式**。1.0 只能克隆安装，没有 pip 发行（`bootloops/toolkit/ours/README.md:91`）；包之间靠把 `tools/` 放进 `PYTHONPATH` 互相导入（`bootloops/INSTALL.md:30-37`）；49 个包里只有 seedling、winnow 带 `pyproject.toml`。
- **不在本仓的**。各问题专用的求值脚本、结果表脚本随官网结果页发布；官网介绍过的 Recount、Actuary、Trireme 三个包没有随 1.0 发布（`bootloops/tools/README.md:12-15`、`:111-119`）。
- **作者与维护**。代码由 Claude 在 Matthew D. Schwartz 指导下写成，版权归 Anthropic, PBC，由 Schwartz 维护，不是 Anthropic 官方支持的产品（`bootloops/README.md:206-209`、`:229-231`、`:247-251`）。

### 6.2 学科分布

上游 `bootloops/toolkit/ours/README.md:12-43` 按主题把包分成七组（ops 另算），blade、kira-stack、holonomic、qinvert、tropical-sampler 5 个包没有列入任何一组，下表按它们在 `bootloops/tools/README.md` 索引行的描述归入[^tk-roster]。

| 组 | 数 | 包 | 服务的领域 |
|---|---|---|---|
| 约化与 IBP | 9 | seedling、dogtag、winnow、maxcut、trust、formglue、ffcapital；blade、kira-stack（未列组） | 费曼积分的 IBP 约化：围绕 Kira、FireFly、Blade、FORM 的预检、对账与中断恢复 |
| 奇点与几何 | 6 | landau-alphabet、dipstick、geotriage、coalescer、subtropica、surd | 费曼积分的 Landau 奇点、符号字母表、最大割几何 |
| 微分方程与输运 | 9 | counterweight、wayfinder、famhar、ratfit、vopclose、numkin、pmflow、cosmoflow、membound | 积分族的 ε 形式微分方程与数值输运；cosmoflow 算宇宙学波函数，membound 算后闵可夫斯基引力展开的边界常数 |
| 周期与算术几何 | 6 | eichler、ellipticus、gpl-eval、frobenius-boundary、abacus、terrier | 数学物理：椭圆多重对数、Calabi–Yau 周期、弦景观通量真空、阿贝尔四维簇点计数 |
| 数值真值与认证算术 | 8 | longhand、amflow-kit；nestor、baller、eras、clinch、gatekeeper、emitall | 前 2 个只服务费曼积分，后 6 个学科无关 |
| 数的识别与闭合 | 5 | ansatzer、galois；lockpick、annihilator、rankscreen | 前 2 个服务振幅符号与多重 zeta 值，后 3 个学科无关 |
| 精确统计与证据 | 3 | mixalot、popcorn、posq | 贝叶斯证据、群体遗传 |
| 未列组 | 3 | holonomic、qinvert、tropical-sampler | 学科无关 |

合计：理论物理积分 28 个（前三组 24 个，加 longhand、amflow-kit、ansatzer、galois），数学物理 6 个，两者共 34 个，占 69%；其余 15 个占 31%，其中 popcorn 服务群体遗传，另 14 个学科无关。这 34 个包的输入是积分族、IBP 方程组、微分算子、周期格这类理论物理与数学物理对象，其中至少 5 个包直接读写或驱动 Kira、FireFly、AMFlow、FORM（例如 amflow-kit、ffcapital、formglue、kira-stack、pmflow，`bootloops/tools/README.md:52`、`:68-69`、`:76`、`:85`）。coalescer 另有通用入口，`--op FILE.json` 接任意 Fuchs 型算子（`bootloops/tools/coalescer/GUIDE.md:5-7`、`:22-26`）。

理论物理、数学物理之外的 15 个包：

| 包 | 做什么 | 出处 |
|---|---|---|
| nestor | 认证求积：嵌套 tanh-sinh 加逐层精度阶梯；端点奇点须先声明，算不准就带名拒绝 | `bootloops/tools/nestor/GUIDE.md:7-9`、`:16-18` |
| baller | 球算术的统一入口：认证求积、ODE 端点输运、Krawczyk 证书、mpmath 精度静态检查 | `bootloops/tools/baller/GUIDE.md:8-13` |
| eras | 共享参数造成的区间依赖使包络爆炸时，用中心形式与 order-K Taylor 包络收窄 | `bootloops/tools/eras/GUIDE.md:10-21` |
| clinch | 层级或混合模型 MAP 最优点的区间 Newton 证书（存在、唯一、Hessian 正定），只给局部结论 | `bootloops/tools/clinch/GUIDE.md:8-15`、`:26-28` |
| holonomic | holonomic ODE 的认证解析延拓，引擎是 SageMath 上的 ore_algebra | `bootloops/tools/holonomic/GUIDE.md:5-20` |
| lockpick | 整数关系与格约化拟合：PSLQ 闭合协议 pslq_gate、多点 LLL/BKZ 拟合 mplll | `bootloops/tools/lockpick/GUIDE.md:7-11` |
| annihilator | 只凭精确级数求最小 P-finite 递推与 θ 形 ODE | `bootloops/tools/annihilator/GUIDE.md:10-14` |
| rankscreen | 精确有理消元之前的多素数并行秩与不一致性筛查 | `bootloops/tools/rankscreen/GUIDE.md:11-15` |
| tropical-sampler | Euler 型积分的热带重要性采样，用例含系统发育证据积分 | `bootloops/tools/tropical-sampler/GUIDE.md:16-29` |
| mixalot | 混合模型的精确贝叶斯证据与组分数后验；成员覆盖生态中性理论、单细胞 telegraph 模型、文本突发性模型 | `bootloops/tools/mixalot/GUIDE.md:12-31`、`bootloops/THIRD_PARTY.md:78` |
| popcorn | 群体遗传的认证似然：选择 SFS / DFE、Λ-coalescent、两位点频谱、EPO 祖先态极化 | `bootloops/tools/README.md:86` |
| posq | 贝叶斯证据的双侧认证求积；生产算例是四类群系统发育模型 | `bootloops/tools/posq/GUIDE.md:12-19`、`:43-55` |
| qinvert | 已公布的分位数、均值等汇总统计能否由部分公开数据精确重算；验证案例是 CMS Star Ratings | `bootloops/tools/qinvert/GUIDE.md:9-23` |
| emitall | 报告里引用的数字与回执文件对账；附生成脚本检查 lint.py（手打的数字、哈希序输出、未设种子的抽样）与 LaTeX 注释吞句检查 paper_seams.py | `bootloops/tools/emitall/GUIDE.md:10-26` |
| gatekeeper | 结果文件哈希去重与留出交叉验证；输入格式按 AMFlow 的 JSON 输出写 | `bootloops/tools/gatekeeper/GUIDE.md:7-15` |

另有几个通用包带着应用学科的成员，对应 README 所列的「population-genetics, ecology, seismology, phylogenetics and public-records tools」（`bootloops/README.md:223`）：clinch 的适配器认证 ETAS 地震模型与 Etienne 生态模型的拟合最优点，模型代码与参考拟合不随仓（`bootloops/tools/clinch/GUIDE.md:42-52`、`:94-100`）；baller 的 vendor 成员重写了 INGV 海啸概率预警代码 matPTF 的告警计算，用于研究数值认证，GUIDE 写明不得用于实际预警（`bootloops/tools/baller/GUIDE.md:30-33`），另一个成员复现 pyCSEP 地震预报一致性检验的抽样（`bootloops/THIRD_PARTY.md:83`）；eras 的参考数据由 DravLex 语言学数据库派生（`bootloops/tools/eras/GUIDE.md:53-59`）。

### 6.3 给 agent 的说明怎么写

**四问页规范**。skills 仓的 tool-stewardship 规定每个工具的说明页回答四个问题：做什么；什么时候用，并点名覆盖相邻场景的工具；输出什么意思，失败输出与成功输出相像时要加粗写明；答案要过什么检验才可信（`skills/skills/tool-stewardship/SKILL.md:34-43`），工具包 README 开头对每件工具的说明也是这四项（`bootloops/README.md:8-10`）。GUIDE 的常见栏目是 KIND、REQUIREMENTS、PURPOSE、USE-WHEN、NOT-FOR、INVOKE、INPUTS、OUTPUTS、ENV、GATES、FOOTGUNS、CREDIT（例如 `bootloops/tools/nestor/GUIDE.md:5-63`），5 个包另有 MANUAL.md 放细节。49 个包都有 GUIDE.md 且都有 PURPOSE 段，46 份有 NOT-FOR 段[^tk-guide]。

**验证等级**。索引给每个包标一个等级（`bootloops/tools/README.md:33-45`）：

| 等级 | 定义 | 包数 |
|---|---|---|
| selftest | 克隆下来原样就能跑绿 | 23 |
| partial | 公开部分能跑绿；要内部参考数据或先编译外部引擎的子项，跳过或带名报错 | 20 |
| smoke | 没有正式 battery，只验证示例、拒绝路径与正负对照 | 3 |
| data-gated | 处理用户自带的数据，没有数据就按设计拒跑 | 3 |

**固定的自检命令**。每个包的 battery 命令与工作目录写在 `bootloops/tools/BATTERIES.json`（49 条），`run_selftests.py` 只执行这一条，不做发现、不猜，清单里没有的包报 `no-manifest-entry`（`bootloops/run_selftests.py:19-23`、`:55-58`）。时间标准是单包默认 battery 在笔记本上约 20 s，重的子项放到开关后面（`bootloops/tools/README.md:17`、`bootloops/run_selftests.py:31-32`）。

**长处**：

- 失败与成功相像的情形在 FOOTGUNS 里点名。emitall：没写 quoted 的 claim 只记 EMITTED，不算 finding，不能当成通过（`bootloops/tools/emitall/GUIDE.md:96-98`）；eras：调用方拿到 `BatteryResult` 不检查 `ok` 就退 0，算调用方的 bug（`bootloops/tools/eras/GUIDE.md:46-49`）。
- 拒绝带名字，退出码分类型。nestor 返回数值或 EvalRefusal、SpecRefusal、CertFail、AbortRefusal 之一，退出码 0/2/3/4（`bootloops/tools/nestor/GUIDE.md:20-21`、`:33-35`）；lockpick 的 pslq_gate 退 2 表示对照失败，退 3 表示退化基（`bootloops/tools/lockpick/GUIDE.md:57-59`）。
- NOT-FOR 指向相邻工具：eras 指向 baller（`bootloops/tools/eras/GUIDE.md:35-36`），lockpick 指向 gatekeeper 的留出认证（`bootloops/tools/lockpick/GUIDE.md:30`）。
- 用途段写实测规模与代价：clinch 约 90 s 出 5592 维证书（`bootloops/tools/clinch/GUIDE.md:14-15`）；annihilator 从 550 项求出 24 阶递推用 204 s（`bootloops/tools/annihilator/GUIDE.md:22-24`）；popcorn 在 n=8、rho>0 时每次求值约 13 s、0.8 GB（`bootloops/tools/popcorn/GUIDE.md:212`）。
- battery 里放必须失败的对照。本机输出里能看到 mixalot 的比较器变异对照全部按要求 FAIL，rankscreen 的 4 个变异全部被抓到，maxcut 的扰动负对照让门槛按要求失败，nestor 的符号变异对照把一致位数从 46 位降到 0 位[^tk-mutation]。
- 校验链防改。部分包把源文件与参考值的 sha256 写进代码，被改过就拒跑（`bootloops/tools/README.md:133-135`、`bootloops/tools/popcorn/certsfs.py:46-83`）；baller、clinch 的 battery 拒绝在包目录里运行，避免产物写进源码树（`bootloops/tools/baller/GUIDE.md:38-40`、`bootloops/tools/clinch/GUIDE.md:38-40`）。
- 术语统一：banked 指已过验收、只读存放的参考值，value of record 指多个候选中被认定的那一个（`bootloops/tools/README.md:19-22`）。RECIPES.md 的 8 条配方都写用途、适用场景、必查项与实现位置，多数另写范围限制与坑；没有随仓实现的配方，正文即参考（`bootloops/toolkit/ours/RECIPES.md:3-9`）。

**不一致处**：

- 格式两种：36 份用行首 `PURPOSE:` 式关键字，10 份用 `## PURPOSE` 小节，3 份混用；长度从 75 行（vopclose）到 876 行（popcorn）[^tk-guide]。runner 读验证等级只靠正则解析 `tools/README.md` 的表格行（`bootloops/run_selftests.py:36-42`），GUIDE 里写的等级不被读取。
- 等级标注与实际要求不一致：qinvert 在索引里是 selftest（`bootloops/tools/README.md:88`），它自己的 GUIDE 写 PARTIAL（`bootloops/tools/qinvert/GUIDE.md:76`）；abacus、counterweight 标 selftest（`bootloops/tools/README.md:51`、`:60`），abacus 要 cypari2 与 Julia（`bootloops/tools/abacus/GUIDE.md:47-62`），counterweight 要 Julia 1.11（`bootloops/tools/counterweight/GUIDE.md:10-12`）。
- 依赖说明缺项：baller 的 GUIDE 只写依赖 python-flint（`bootloops/tools/baller/GUIDE.md:42`），它的 vendor 成员导入 scipy（`bootloops/tools/baller/vendor/geo/mc.py:8`），只装核心依赖时 battery 失败，见 [6.5](#65-本机-macos-实测)。
- 默认读者熟悉本领域：MUM point、Frobenius landing、eps-graded DE transport 这类术语直接使用，不加解释（例如 `bootloops/tools/README.md:63`、`:98`）。

### 6.4 依赖与许可证

| 层 | 内容 | 获取 | 许可证 |
|---|---|---|---|
| Python 核心 | Python 3.12；mpmath、sympy、numpy、python-flint；battery 要 pytest | PyPI | BSD / MIT；python-flint 底层的 FLINT 是 LGPL-3.0+ |
| Python 可选 | scipy、pyyaml、gmpy2、networkx、dynesty、cypari2、msprime、tskit | PyPI | 多数宽松；msprime 是 GPL-3.0+，cypari2 绑定的 PARI/GP 是 GPL-2.0+ |
| Julia | Julia ≥1.11，各组件经 `Project.toml` 装 Nemo、Arblib、OSCAR 等；仓内 7 个 `Project.toml`（upgrades 3 个、tools 4 个），10 个包含 Julia 源文件 | juliaup、Homebrew 或发行版 | Julia 是 MIT；OSCAR 是 GPL-3.0+ |
| 引擎分叉 | Kira 3.1（另需 FireFly 与 Fermat）、Blade（链接 FiniteFlow）、AMFlow.cpp | 从兄弟仓编译；Fermat 只能从作者网站下载 | Kira GPL-3.0+；Blade、AMFlow.cpp MIT；Fermat 是专有免费软件 |
| 其他外部程序 | FORM、HyperFORM、FIRE、FIESTA、pySecDec、GiNaC、PentagonFunctions-cpp、Singular、msolve、PARI/GP、SageMath 与 ore_algebra、fplll | 用户自行安装上游版本 | 多数 GPL |
| 本地编译 | posq 的 C 内核要 C 编译器与 FLINT、MPFR、GMP 开发头文件；gpl-eval 与 Eichler.jl 链接 GiNaC 的桥接程序只发源码 | 首次使用时编译 | 链接 GiNaC 的产物受 GPL 约束 |

出处：`bootloops/README.md:160-163`、`bootloops/INSTALL.md:38-47`、`:62-87`、`:117-133`、`bootloops/toolkit/external/TOOLS.md:17-45`、`bootloops/THIRD_PARTY.md:89-104`、`bootloops/tools/posq/GUIDE.md:117-131`[^tk-julia]。Blade 分叉的源码安装脚本在 arm64 上会停在 MPFR 自带的测试里，完整构建只在 x86_64 上验证过（`bootloops/README.md:168-170`）。

许可证：

- 代码是 MIT（Copyright (c) 2026 Anthropic, PBC）；为本仓写的说明文字与图是 CC BY 4.0，署名串固定为「BootLoops 1.0, Anthropic, PBC and Matthew D. Schwartz (2026), https://www.bootloops.ai」（`bootloops/README.md:247-252`、`bootloops/LICENSE-CONTENT:1-6`）。GUIDE.md 属于说明文字，按 CC BY 4.0 许可（`bootloops/LICENSE-CONTENT:1-3`）。
- 仓内有 3 个 GPL 文件：`tools/subtropica/src/lr_refine.jl`（GPL-3.0-or-later，源自 HyperInt）、`tools/eichler/genus2/mestre_port.py`（GPL-2.0-or-later，源自 SageMath）、`tools/formglue/form_hyper.py`（GPL-3.0-only，源自 HyperFORM 示例）（`bootloops/README.md:256-264`）。
- 第三方数据：surd 的物理数据、terrier 的一张通量真空卡片、eras 与 baller 共用的 DravLex 派生计数是 CC BY 4.0；terrier 另有 3 份按 arXiv 非独占许可从论文转录的数值，从 LMFDB 转录的 Hecke 特征值按 CC BY-SA 4.0 标注（`bootloops/THIRD_PARTY.md:59-70`）。eras 缺这份数据在 import 时就报错（`bootloops/tools/eras/GUIDE.md:53-55`），baller 的 vendor 文件有 sha 钉住、`verify()` 遇不符即拒（`bootloops/tools/baller/GUIDE.md:42-44`，DravLex 文件在钉住清单里：`bootloops/tools/baller/baller/_pins.py:22`），所以 CC BY 数据不能单独剔除而让包照常运行。
- 运行时导入的 GPL 库：pySecDec（longhand）、SageMath 与 ore_algebra（holonomic）、OSCAR（subtropica 等），运行时的组合受 GPL 约束（`bootloops/toolkit/external/TOOLS.md:12-15`）。

**凭据与联网**。全仓查 API key、access token、`load_dotenv`、huggingface、openai 等写法零命中，`.py` 文件里没有 requests 或 urllib 导入；工具包自己的代码里，联网只有 `bootloops/upgrades/Eichler.jl/vendor/zenodo-2502.00118/fetch.sh:16-19` 用 curl 下载 Zenodo 公开记录，不需要账号。随仓保留的上游参考源 SubTropica.wl（SubTropica 原件，Wolfram 语言，按原许可证保留，`bootloops/README.md:252-256`；工具包的 Julia 移植引用它的行号作对照，`bootloops/tools/subtropica/CONTRACTS.md:3-4`）里有联网代码：用 curl 拉 SubTropica 中央库清单、向其提交结果，内嵌的 Python 服务按 arXiv 号下载 PDF（`bootloops/tools/subtropica/reference/SubTropica.wl:30815-30818`、`:33933`、`:34181`），请求里不带凭据[^tk-keys]。

**输入文件的安全性**。README 说明许多工具会执行输入文件（JSON、YAML、`.m`、`.jl`、pickle 等）的内容，别人给的输入文件要按代码对待；仓内的完整性检查与证书只防意外，不构成安全边界（`bootloops/README.md:236-243`）。

### 6.5 本机 macOS 实测

官方测试平台是 Linux x86_64（开发平台）和 x86_64、arm64 两种架构的 Debian 12 容器；README 写明 macOS 不在发布测试范围，在 macOS 上使用前要先跑验证命令（`bootloops/README.md:158-174`）。

**环境与命令**。本机 macOS（Apple Silicon）实测，2026-10-02：macOS 26.5.2，15 核，48 GB 内存；uv 建的 Python 3.12.14 隔离环境，装 `bootloops/INSTALL.md:120-121` 列出的核心与可选依赖，全量运行时漏装了其中的 cypari2，事后补装并单独重跑了 abacus；本机没有 Julia、PARI/GP、SageMath、FORM、msolve、Singular。自检在克隆的副本里运行，原克隆 `git status` 无改动。命令如下，并行数取 6（README 与 INSTALL.md 的示例是 `--par 8`），单包限时取默认的 300 s：

```
python3 run_selftests.py --par 6
```

**结果**。总墙钟 92.7 s（user 378.1 s）[^tk-full]。

| 等级 | 包数 | PASS | REFUSED | FAIL |
|---|---|---|---|---|
| selftest | 23 | 21 | 0 | 2 |
| partial | 20 | 18 | 0 | 2 |
| smoke | 3 | 3 | 0 | 0 |
| data-gated | 3 | 0 | 3 | 0 |
| 合计 | 49 | 42 | 3 | 4 |

6 路并行下，最慢的单包是 dogtag 56.0 s、amflow-kit 46.8 s、wayfinder 39.2 s、seedling 38.0 s、annihilator 37.4 s；9 个包超过 20 s 的时间标准，没有包超过 runner 的 60 s 提示线（`bootloops/run_selftests.py:127-132`）。6.2 第二张表的 15 个包里，emitall 1.1 s（69 个测试通过），nestor 1.5 s（13/13），lockpick 0.1 s（16/16），qinvert 0.5 s（50 个通过、2 个跳过），popcorn 22.6 s（43 项全过），mixalot 28.5 s（24 项）。

**4 个 FAIL**：

| 包 | 等级 | 现象 | 原因 |
|---|---|---|---|
| abacus | selftest | `ABACUS-REFUSAL`，缺 cypari2；补装后单独重跑，报找不到 julia | 要 cypari2 与 Julia（`bootloops/tools/abacus/GUIDE.md:47-62`） |
| counterweight | selftest | 退出码 127，`julia: command not found` | 固定命令就是 `julia --project=. test/runtests.jl`（`bootloops/tools/BATTERIES.json:38-41`） |
| amflow-kit | partial | 7 个测试失败、42 个通过、4 个跳过，`FileNotFoundError: '/proc'` | `bootloops/tools/amflow-kit/amflow_kit/memfence.py:569` 遍历 `/proc`，macOS 没有这个目录 |
| seedling | partial | `bootloops/tools/seedling/tests/test_cgroup_law.py:227` 断言失败，得到 0、期望 99；pytest 带 `-x`，停在第 1 个失败（11 个通过） | 测试用 mock 代替 cgroup 操作，但父进程查询仍读 `/proc/<pid>/stat`（`bootloops/tools/seedling/runner.py:157-164`），macOS 上读不到，外来进程被判为已退出（`:241-243`），没有触发中止 |

amflow-kit 与 seedling 都是 Python 代码。ops/turnstile 的文档写明只支持 Linux、在 macOS 上按名跳过（`bootloops/ops/README.md:15`、`bootloops/INSTALL.md:143-146`），runner 不跑它，本机未实测。

**3 个 REFUSED**。runner 把 data-gated 包除用法报错外的任何非零退出都记为 `REFUSED (by design)`（`bootloops/run_selftests.py:113-123`）。ffcapital 输出 `DATA GATE: no ff_save/ state supplied`，galois 报 `GALOIS_CAMPAIGN_BANK is not set`，这两个是按设计的缺数据拒跑。frobenius-boundary 停在固定命令的第一步 `asdminer/run_control.py`，Python traceback 显示找不到 PARI/GP 的 `gp`，没有走到数据检查；它的 GUIDE 写明这一步要 gp（`bootloops/tools/frobenius-boundary/GUIDE.md:50`、`:146`）。

**PASS 与验证覆盖**。runner 只看退出码，0 就记 PASS（`bootloops/run_selftests.py:115-117`），每包只保留输出的最后 1200 个字符（`bootloops/run_selftests.py:106`）。在这段输出里，42 个 PASS 中至少 23 个出现了跳过、未构建或未验证的子项[^tk-skip]，例如：

- gpl-eval：没有 julia 时打印 `Nothing was verified` 并返回 0（`bootloops/tools/gpl-eval/selftest.py:77-82`；缺依赖设置时同样处理，`:69-71`）。
- posq：自动编译 C 内核时找不到 FLINT 头文件 `flint/flint.h`，内核子项按名跳过（`POSQ-KERNEL-UNAVAILABLE`），随后打印 `posq selftest: PASS`。
- clinch：battery 先打印 `OVERALL FAIL`，列出 L3、L4、L6 三个子项；包装脚本随后说明 L3、L6 与 L4 中依赖回执的子项要用不随仓的参考结果、按跳过处理，最后输出 `clinch selftest PASS`。
- holonomic 输出 `smoke: SKIP (SageMath not on PATH ...)`；terrier 34 项中 18 项通过、16 项按名跳过；dipstick 8 个子项中 5 个因缺 julia 或 msolve 跳过。

partial 等级的定义允许这类跳过（`bootloops/tools/README.md:39-41`）；selftest 等级定义为克隆后原样跑绿（`:38`），其中也有 6 个包带跳过的子项（ansatzer、cosmoflow、dipstick、landau-alphabet、longhand、qinvert），cosmoflow 的那一项是按设计放在 `--deep` 之后的重子项。汇总表只给 PASS 一个状态，不给跳过数。BootLoops 自己的 planted-truth 协议要求每份汇总写明分母、分母比声明的小就判失败（`skills/skills/planted-truth/SKILL.md:122-127`）；runner 的汇总以包为单位计数，不汇总包内子项的分母，gpl-eval 这种一项都没验证的包也记 PASS。

**只装核心依赖**。另在只装 `bootloops/INSTALL.md:120` 核心依赖（mpmath、sympy、numpy、python-flint、pytest）的隔离环境里，用同一个 runner 跑了 6.2 第二张表里的 7 个包[^tk-core]：popcorn、emitall、nestor、lockpick、qinvert 通过，其中 popcorn 32 项通过、11 项按名跳过（7 项缺 scipy、3 项缺 msprime、1 项缺 gmpy2）；mixalot 失败于 `ModuleNotFoundError: No module named 'scipy'`（`bootloops/tools/mixalot/mixalot/vendor/jeff/estimators.py:64`），它的 GUIDE 已在 REQUIREMENTS 写明要 scipy（`bootloops/tools/mixalot/GUIDE.md:8-10`）；baller 的 L7、L14 报缺 scipy，L20 是 vendor 成员 certlane 的测试失败，该测试导入 scipy（`bootloops/tools/baller/vendor/certlane/test_primitives.py:132`），而 baller 的 GUIDE 没写这项依赖。

**小结**。6.2 第二张表的 15 个包在全量环境下都记 PASS，其中 holonomic（缺 SageMath）的主子项被跳过，posq 的 C 内核没有编译成；只装核心依赖时 mixalot、baller 因缺 scipy 失败；依赖 Julia、PARI/GP、SageMath 等外部程序的子项被跳过或失败；amflow-kit、seedling 含读 Linux `/proc` 的代码。

### 6.6 优势

- 说明文档逐包覆盖：49 个包都有 GUIDE，按用途、适用与不适用、调用方式、验收条件、已知的坑等栏目写，栏目齐全程度不一；索引给每个包标验证等级（[6.3](#63-给-agent-的说明怎么写)）。
- 自检一条命令可复跑：每包一条固定命令，runner 不猜；本机 6 路并行 92.7 s 跑完 49 个包，6.2 第二张表的 15 个包除主子项被跳过的 holonomic 外，单包自检在 0.1 s 到 37.4 s 之间，最慢的是 annihilator（[6.5](#65-本机-macos-实测)）。
- 测试数量：wayfinder 132 个测试，emitall 69 个，ratfit 53 个，dogtag 的自检注册了 203 个子项（本机全量自检输出）。
- 失败处理显式：缺数据按名拒跑，拒绝分类型、退出码分档；battery 内含必须失败的变异对照；关键文件 sha 钉住，改过即拒跑。
- 零凭据：代码不调用任何模型或付费服务；工具包自己的联网只有下载 Zenodo 公开数据，随仓的上游参考源里另有不带凭据的联网代码（[6.4](#64-依赖与许可证)）。
- 核心依赖少：核心只有 4 个 PyPI 包加 pytest，可选依赖也都在 PyPI 上，本机都能直接装上。
- 来源记录细：`bootloops/THIRD_PARTY.md` 逐文件列来源、上游提交、许可证、是否修改；外部引擎清单给获取地址与应引文献（`bootloops/toolkit/external/TOOLS.md:17-45`）；`upgrades/` 下三个引擎各带 `PATCHES.md`，三个引擎分叉按 README 所述也各带一份（分叉仓本次未克隆，未验证）。
- 自述边界：README 写明 macOS 不在发布测试范围、输入文件要按代码对待、结果不适用于临床、精算、支付、监管与公共安全决策（`bootloops/README.md:172-174`、`:211-213`、`:236-243`）。

### 6.7 局限

- 学科集中：49 个包里 34 个服务理论物理与数学物理；其他学科的逐题代码不在本仓（[6.2](#62-学科分布)）。
- 外部依赖重：部分包要 Julia 与十余种外部程序，其中多数是 GPL；Kira、Blade、AMFlow.cpp 要从源码编译，Fermat 只能从作者网站下载；没有 pip 发行，安装靠克隆加 `PYTHONPATH`（[6.4](#64-依赖与许可证)）。
- 平台覆盖：发布测试只覆盖 Linux；本机 macOS 上 4 个包失败，其中 2 个是读 Linux `/proc` 的代码；Blade 分叉在 arm64 上从源码安装会停在 MPFR 测试（`bootloops/README.md:168-170`）。
- 汇总口径宽：PASS 不区分跳过，至少 23 个 PASS 含跳过的子项；data-gated 包除用法报错外的任何非零退出都记为按设计拒跑；gpl-eval 什么都没验证也记 PASS（[6.5](#65-本机-macos-实测)）。
- 文档与实现有出入：验证等级标注、依赖说明、「缺引擎就跳过并说明要装什么」的承诺，各有不一致的实例（[6.3](#63-给-agent-的说明怎么写)、[6.9](#69-公开说法核对)）。
- 读者门槛：GUIDE 默认读者熟悉本领域，术语不加解释，长度 75 到 876 行，格式两种。
- 许可证混合：MIT 代码、CC BY 4.0 文字、3 个 GPL 文件、CC BY 与 CC BY-SA 数据在同一个仓里，部分数据被 sha 钉住，不能单独剔除。
- 输入安全：工具会执行输入文件的内容，完整性检查不防恶意输入（`bootloops/README.md:236-243`）。

### 6.8 和平台的关系

**平台现有用户的课题**。平台面向课题组的研究者：研究者在页面上跟助理说清课题，助理调用平台能力，人只在断点上确认（外层仓 `README.md:14`）。案例库现有 7 个案例，任务类型是回归、连续参数优化、表示学习、论文复现，应用领域是药剂学、系统生物学、流行病学、多模态 ML、计算物理（`docs/cases/README.md:7-15`）；出厂领域包只有 generic 与 petab（`platform/docs/add-a-domain.md:22`）。这些课题与工具包 34 个理论物理、数学物理包服务的对象没有交集。其余 15 个包解决的是带误差证书的高精度数值、精确关系识别、精确贝叶斯证据与群体遗传似然；平台现在的验收按重复运行的 σ 设统计门（`platform/framework/experiment/headroom.py:31-38`），`docs/cases/` 下搜「证书」「certif」「PSLQ」「高精度」等字样零命中，现有案例里没有要求证书级数值的步骤。

**有对应工具的研究方向**。按包的用途：理论物理中的散射振幅、费曼积分、宇宙学关联函数、后闵可夫斯基引力；数学物理与数论中的周期、模形式、算术几何；群体遗传（popcorn）；生态、单细胞、文本数据的混合模型选择（mixalot）；系统发育模型的贝叶斯证据（posq、tropical-sampler，以及另一仓的 JaCKandJill）；公开汇总统计的复核（qinvert）；需要认证数值或整数关系识别的计算（nestor、baller、lockpick、annihilator）。

**用法上的差别**。BootLoops 的用法是让 agent 读索引与 GUIDE，再自己写 Python 调用这些包（`bootloops/README.md:70-80`、`bootloops/INSTALL.md:33-37`）。平台的助理面前只有 `ai4sci`，执行层只有 `ai4sci skill`，不裸跑 python（P-14，`docs/architecture/README.md:164`）；skill 脚本要带 PEP 723 头与锁，用 `uv run --locked` 起（P-22，`docs/architecture/README.md:172`）。

**如果以后出现对应课题**，工具包各部分在平台里能对上的位置：

| 工具包部分 | 平台对应处 | 接入时要处理的事 |
|---|---|---|
| lockpick、nestor、annihilator、baller 的 dps_lint（认证数值） | 按任务类型命名的领域包（`platform/docs/add-a-domain.md:9-11`），skill 放 `experiment/computing`（`platform/framework/skills/shelves.py:35`） | 没有 pip 发行，包目录要随 skill 带上，另写带 PEP 723 头的入口脚本，平台只认 `scripts/` 顶层的 `.py`（`platform/framework/skills/library.py:268-272`）；nestor 依赖 gatekeeper 的 `quad_probe.py`（`bootloops/tools/nestor/GUIDE.md:26-27`）；baller 整包带 CC BY 数据 |
| popcorn、mixalot（群体遗传、混合模型证据） | 领域包，skill 放 `experiment/biology` 或 `analysis/statistics`（`platform/framework/skills/shelves.py:33`、`:41`） | 引擎文件 sha 钉住，CLI 先校验再导入（`bootloops/tools/popcorn/certsfs.py:46-83`），源文件不能改；msprime 是 GPL-3.0+ 可选依赖；mixalot 要 scipy、dynesty |
| emitall 的比对规则：按引文印出的精度比、计数核对、区间端点向外取整、回执过期 | 验证步骤 `verify` 的数字回溯，现在整数与百分比不查（`platform/framework/capabilities/verify/checks.py:6-7`） | emitall 按文件 mtime 先后判回执过期，没有比对内容哈希（`bootloops/tools/emitall/GUIDE.md:28-30`） |
| GUIDE 的四问、验证等级、固定自检命令 | SKILL.md 正文的「四件事」（`platform/docs/add-a-skill.md:63`）；门禁拦格式与锁（`platform/docs/add-a-skill.md:65`） | GUIDE 正文是 CC BY 4.0，不能照抄 |
| ops/turnstile | 算力按人配置（P-23，`docs/architecture/README.md:173`） | 只支持 Linux 共享机器 |

**平台收录规则下的情况**：

- 零 key（P-27，`docs/architecture/README.md:177`）：工具包满足，见 [6.4](#64-依赖与许可证)。
- 许可证：可收的只有 MIT、Apache-2.0、BSD、ISC，CC BY 系列不收（`platform/framework/skills/provenance.py:54-55`、`platform/docs/add-a-skill.md:109`）。工具包的 Python 代码是 MIT；GUIDE 正文是 CC BY 4.0，不能照抄进 SKILL.md；带 GPL 文件或 CC BY、CC BY-SA 数据的包（subtropica、eichler、formglue、surd、terrier、eras、baller）不满足这一条。
- 台账检查只读收录库 `skills-curated` 的台账（`platform/framework/skills/provenance.py:87-90`），领域包里放第三方代码没有许可证的机器检查。
- 系统软件：核心做法要装系统软件的不收（`platform/docs/add-a-skill.md:111`），要 Julia、Kira、FORM、PARI/GP、SageMath 等外部程序的包属于这一类。

本轮结论是不收录任何代码或 skill，上面只记录对应关系。

### 6.9 公开说法核对

| 说法 | 出处 | 核对 |
|---|---|---|
| The package itself is general purpose | `bootloops/README.md:40-45` | 方法层面成立：球算术、PSLQ、认证求积不限学科，14 个包学科无关。按包的用途数，49 个里 34 个服务理论物理与数学物理，另有 popcorn 服务群体遗传，见 [6.2](#62-学科分布) |
| applications spanned twenty-two fields of science | [bootloops.ai 首页](https://www.bootloops.ai) | 本仓只有通用包，各领域的逐题代码在官网结果页（`bootloops/tools/README.md:12-15`）。仓内能看到的应用学科成员是群体遗传、生态、地震、海啸预警计算的研究性重写、语言学数据、公开统计、系统发育、单细胞转录动力学与文本建模（`bootloops/tools/mixalot/GUIDE.md:23-31`、`bootloops/THIRD_PARTY.md:78`）；单凭本仓核实不了 22 个领域 |
| 全量自检在笔记本上几分钟跑完，3 个包因缺数据带名报错，缺外部引擎的 battery 会跳过并说明要装什么 | `bootloops/README.md:90-95`、`:184-186` | 时间成立，本机 6 路并行 92.7 s。macOS 上另有 4 个 FAIL；counterweight 缺 Julia 时 shell 退 127，没有按名跳过；frobenius-boundary 记为拒跑，实际原因是缺 gp。README 已说明 macOS 不在测试范围 |
| The pure-Python packages have no platform-specific code | `bootloops/README.md:172-173` | 与本机实测不符：amflow-kit 遍历 `/proc`，seedling 查父进程读 `/proc/<pid>/stat`，两者的测试在 macOS 上失败（[6.5](#65-本机-macos-实测)） |
| A laptop and whatever LLM access you already have are enough to drive the code | [harness 页](https://www.bootloops.ai/harness.html)、`bootloops/README.md:79-80` | 自检与小算例成立。GUIDE 记载的生产规模计算可到数十 CPU 小时，例如 posq 的 15 个拓扑共 93.25 CPU-h（`bootloops/tools/posq/GUIDE.md:47-50`）；harness 页同时写明构建初始工具库用了大量算力和数十亿 token |
| The harness is independent of the model driving it | `bootloops/README.md:6-8` | 工具包代码不调用任何模型，这一点上与模型无关（[6.4](#64-依赖与许可证)）。总论文写明文中的计算由 Claude 运行，同页称可接任何语言模型，也可在 Codex 等商用 harness 里用（[总论文 p.3](https://www.bootloops.ai/BootLoops.pdf)）；本次查阅的官网页面、总论文与三个仓里没有找到用其他模型驱动的实测 |

[^tk-count]: 分类方法：以 `bootloops/toolkit/ours/README.md:12-43` 的主题分组为准，未列组的 5 个包按 `bootloops/tools/README.md` 的索引行归入；「学科无关」指包的 PURPOSE 不以某一学科的对象为输入。逐包归属见 6.2 的两张表。popcorn 的输入是群体遗传模型（选择 SFS、DFE、coalescent），按这个定义不算学科无关，单列；mixalot、posq 的成员与生产算例分别来自生态、单细胞、系统发育，方法本身是通用的贝叶斯证据计算，计入学科无关。gatekeeper 的方法学科无关、输入格式按 AMFlow 输出写，计入学科无关；coalescer 有通用算子入口，按上游分组计入理论物理。

[^tk-full]: 本机 macOS（Apple Silicon）实测，2026-10-02，在克隆副本里运行 `python3 run_selftests.py --par 6`。runner 汇总输出 `{"data-gated/REFUSED (by design)": 3, "partial/FAIL": 2, "partial/PASS": 18, "selftest/FAIL": 2, "selftest/PASS": 21, "smoke/PASS": 3}`，`failures: ['abacus', 'amflow-kit', 'counterweight', 'seedling']`，计时 `real 92.74 user 378.07 sys 18.49`。各包的命令、退出码、耗时与输出尾部在 runner 写出的 `selftest_results.json` 里。补装 cypari2 后用 `python3 run_selftests.py abacus` 单独重跑，输出 `ABACUS-REFUSAL: julia executable 'julia' does not resolve`，退出码 1。

[^tk-scale]: 在提交 66b680c 上统计：`git ls-files` 共 2061 个文件；`*.py` 949 个、243475 行；`*.jl` 160 个、43016 行；`du -sh` 得克隆目录 42 MB（含 `.git` 8.9 MB），`tools/` 28 MB，`upgrades/` 4.8 MB。

[^tk-roster]: blade、kira-stack 的索引行分别写「Wolfram-free Blade block-triangular IBP pipeline」「IBP reduction to masters + raw DE」（`bootloops/tools/README.md:56`、`:76`），归入约化与 IBP；holonomic、qinvert、tropical-sampler 的索引行在 `bootloops/tools/README.md:75`、`:88`、`:95`。cosmoflow、membound 的领域见 `bootloops/tools/README.md:59`、`:81`。

[^tk-guide]: 在提交 66b680c 上统计：49 个包目录（不含 `fixtures/`）都有 GUIDE.md，`wc -l` 合计 8723 行，最短 vopclose 75 行，最长 popcorn 876 行。行首 `PURPOSE:` 39 份，`## PURPOSE` 或 `## Purpose` 13 份，其中 dogtag、ratfit、tropical-sampler 3 份两种都有。NOT-FOR 段 46 份，amflow-kit、mixalot、posq 没有。

[^tk-mutation]: 均取自本机全量自检输出：mixalot `PASS M10 comparator mutation controls all FAIL as required`；rankscreen 4 行 `MUTATION ...: CAUGHT`；maxcut `T4-negative-control PASS perturbed min_digits=6.0 (need 10) -> gate FAILS as required`；nestor `D4 PASS add-back sign mutation control`（`46 d -> 0 d`）；trust `mutation_test: ALL MUTANTS CAUGHT`。

[^tk-julia]: Julia 统计：`find . -name Project.toml` 得 `upgrades/` 下 Eichler.jl、SOFIA.jl、leviathan 3 个，`tools/` 下 counterweight、subtropica、landau-alphabet/LandauAlphabet.jl、gpl-eval/GPLEval.jl 4 个；含 `.jl` 源文件的包是 abacus、coalescer、counterweight、dipstick、dogtag、eichler、gpl-eval、landau-alphabet、subtropica、terrier。Julia 版本要求见 `bootloops/INSTALL.md:127-131`。

[^tk-keys]: 在提交 66b680c 上运行 `git grep -nIiE "api[_-]?key|access[_-]?token|load_dotenv|huggingface|openai"` 无输出；对 `*.py` 查行首的 `import requests`、`from requests`、`import urllib`、`from urllib` 无输出。不限文件类型查 `git grep -nIw -e curl -e wget` 与 `git grep -nI urlopen`，命中只有 `upgrades/Eichler.jl/vendor/zenodo-2502.00118/fetch.sh:16`、`:19` 和 `tools/subtropica/reference/SubTropica.wl`（`:30818` 的 urlopen，`:33933`、`:34181`、`:34261` 的 curl）；`tools/maxcut/de_transport.py` 里的 curl 是数学上的旋度，不是命令。

[^tk-skip]: 判据：输出尾部出现 SKIP、skipped、`not built`、`Nothing was verified` 等字样，排除「0 skipped」这类计数。逐个列出 23 个：selftest 等级 ansatzer（`[SKIP] no alphabet.json supplied`）、cosmoflow（重子项按设计放在 `--deep` 后）、dipstick、landau-alphabet、longhand、qinvert；partial 等级 blade、clinch、eichler、formglue、gpl-eval、holonomic、maxcut、posq、ratfit、subtropica、surd、terrier、trust、wayfinder、winnow；smoke 等级 kira-stack、pmflow。输出尾部只有 1200 个字符，实际数目可能更多。

[^tk-core]: 本机 macOS（Apple Silicon）实测，2026-10-02：`uv venv -p 3.12` 后只装 `mpmath sympy numpy python-flint pytest`，在克隆副本里运行 `python3 run_selftests.py mixalot baller popcorn emitall nestor lockpick qinvert`。复查时用同一环境在新导出的副本里复跑，结果：mixalot FAIL（0.4 s），baller FAIL（1.8 s，`OVERALL FAIL: ['L7 ...', 'L14 ...', 'L20 ...']`），popcorn PASS（13.5 s，`32 pass, 11 skip, 0 fail`），emitall PASS（0.6 s），nestor PASS（1.5 s），lockpick PASS（0.1 s），qinvert PASS（0.2 s），总计 `real 18.18`。初次运行的状态相同，耗时没有存档。单独运行 `python3 tools/popcorn/selftest.py` 列出 11 项跳过的原因：7 项提示 numpy、scipy（其中 2 项连带 sympy）缺失，本环境实际只缺 scipy；3 项 `msprime absent`；1 项 `gmpy2 absent`。另在临时目录单独跑 `tools/baller/battery/battery.py`，L7、L14 输出 `ModuleNotFoundError: No module named 'scipy'`，L20 输出 `certlane pytest rc=1`。

## 7. JaCKandJill（系统发育证据）

JaCKandJill（Python 包 `phyloexact` 1.0.0）计算系统发育替换模型的边际似然与贝叶斯因子，每个数都标明声明强度（对称性定理、精确有理数、严格区间、校准过的估计），并附一份可以机器核对的证书；自检电池与证书验证器两个文件占包内 Python 行数的 57%，本机 38 道自检门中 37 道通过，1 道超时没跑完[^jj-codesize]。适用规模有限：精确值只覆盖四类群、JC69 在 CPU 上最多 150 列、K2P 最多 35 列的比对，带误差数的估计只覆盖四类群、JC69 32 列（K2P 35 列）以内；包只能从源码树运行，默认自检在本机合计至少 26 分钟。平台现有七个案例里没有系统发育课题，两者的交集在验收与契约的写法上，见 [7.7](#77-和平台的关系)。

### 7.1 解决什么问题

系统发育学比较候选树或替换模型时，看每个假设下数据的边际似然（evidence）Z，两个 Z 之比是贝叶斯因子。常用的估计方法有热力学积分、stepping-stone 与 nested sampling，单次运行不认证自身的误差[^jj-r4]。JaCKandJill 按能给出的保证分四档：数据的置换对称能推出平局时给定理（R0），能精确计算时给有理数（R1），能严格界定时给区间（R2），其余给浮点估计并说明误差数从哪里来（R3）。这四档在文档里叫 register，下文称「档」[^jj-ladder]。

| 项 | 内容 |
|---|---|
| 输入 | FASTA（UTF-8，全包只有一个读取器，重名、长度不齐等情况按名拒绝）、`{taxon: 序列}` 映射，或位点模式计数；拓扑写成分割键（如 12\|34）或 Newick，带枝长的 Newick 按名拒绝 |
| 主要入口 | `px.evidence`（单个拓扑）、`px.compare`（两个拓扑）、`px.compare_models`（两个模型）、`px.decidability`（R0）、`px.grade_model`、`px.check_adequacy`、`px.quintet.adjudicate`（五类群）、`px.hill.*`（基因组尺度） |
| 输出 | `Report`：`.value`（R1 为 `Fraction`，其余为 float 的 logZ）、`.register`（实际给到的档）、`.certificate`（可 JSON 化的 dict） |
| 核对 | `px.verify_certificate(cert, dataset=...)` 返回逐行检查表，含 `ok`、`n_performed`、`n_skipped`、`checks` |
| 自检 | `python -m phyloexact.validate`，写出 `VALIDATION_REPORT.json` |

上表出自 `jackandjill/GUIDE.md:41-229`（quickstart 代码块）。各档覆盖的规模如下：

| 档 | 声明 | 类群数 | 规模上限 | 模型 |
|---|---|---|---|---|
| R0 | 数据的置换对称强制两个拓扑平局，对所声明类别里的一切方法与先验成立 | 4–32 | 对称群搜索超过 400,000 个节点时按名拒绝 | 叶可交换的模型（GM 除外） |
| R1 | 精确有理数，零误差 | 4 | JC69 在 CPU 上 N ≤ 150 列，`auto` 只在实测包络内走精确路线（N = 68 时混合位点 m ≤ 25，N = 150 时 m ≤ 10）；K2P 实际 N ≤ 35；K3ST N ≤ 5；N > 150 且 m 在 100–250 的 JC69 要 GPU | JC69、JC-SR4、K2P、K3ST、JC+R |
| R2 | 严格区间（Arb 球算术），下端点没闭合时标 R2-one-sided | 4 | JC69 N ≤ 150；JC+R 在 r = 2 时 N ≤ 75；HKY85、GTR+G、GTR+Γ4 在拟合点或调用方指定的点上算；HKY85 可以在 π 固定时对 κ 积分（free-κ 路线，要 fork），κ 与 π 同时自由、GTR+Γ4 自由参数的积分按名拒绝 | JC69、JC-SR4、JC+R、HKY85、GTR+G、GTR+Γ4；需要 python-flint |
| R3 | 浮点蒙特卡洛估计 | JC69 任意 n ≥ 4，其余为 4 | 任意长度都能算；带误差数只限校准范围：四类群、默认先验，JC69 N ≤ 32 且 m ≤ 9，K2P N ≤ 35 且 m ≤ 11，范围外标 UNGRADED、不给误差数；HKY85 与 GTR 路线不在校准记录里 | JC69、K2P、HKY85、GTR+Γ4 等；GM 在本版停用 |

出处：R0 见 `jackandjill/SPEC.md:3886-3894` 与 `jackandjill/MODELS.md:55-61`；R1 见 `jackandjill/SPEC.md:121-142` 与 `jackandjill/AMBIGUITIES.md:28-58`[^jj-r1env]；R2 见 `jackandjill/MODELS.md:63-80` 与 `jackandjill/AMBIGUITIES.md:60-70`；R3 见下文[^jj-r3regime]。

四类群之外有两条路线。`px.quintet` 对五类群在 JC69 下做认证的最大似然排序，文档把它定为单独声明、弱于 R1 的一档，五类群的精确证据只到窗口尺度；`px.hill` 面向基因组尺度，按窗口扫描，每个窗口给 R0 判定、精确上界（sup ceiling）与 R3 后验估计，另有对任意比对的精确上界和给 wASTRAL、wQFM 用的认证权重文件[^jj-quartet]。包只给指定的拓扑打分，不搜索树，不认证树，也不做多物种溯祖（MSC）的认证声明[^jj-notfor]。随包的真实序列多为 tRNA 长度（PAIL 演示用的 18 个线粒体 tRNA 四类群为 66–75 nt），最长的一组是 4 条 390 nt 的溶菌酶编码序列，这组在 V26 里本包按名拒绝精确计算；网站自己写明，两条约 900 列、含几百个混合位点的经典比对，精确算法仍然算不到[^jj-900]。

### 7.2 怎么自证

自证分四层。

1. **档位规则。** R3 的结果永远不进入 R0–R2 的声明；由几个单项结果合成的量（贝叶斯因子、拓扑后验），文档把每个单项叫一条腿（leg），合成量取各腿中最弱的档，与腿的顺序无关；强制要求某一档而做不到时，抛出 `RegisterUnavailable`，写明撞上的边界（定理、包络或实测成本墙）以及最小的解锁条件 `unlock`，不悄悄降档[^jj-law]。
2. **独立验证器。** `verify_certificate` 用数据集和随包引擎重算，不依据证书对自身的描述下结论。「某条腿不分级」「有效样本量不够」「哪个复合量没有误差界」这类披露，由验证器从自己手里的数据算出，作为它自己的行列出；证书的自述与之矛盾就按名失败，证书没写不算失败[^jj-disclose]。
3. **R3 误差数的来源。** 在校准类上拿精确锚点实测：容差取最大偏差的 3 倍，向上取两位有效数字；容差大于 0.25 nats 的预算档整档不分级。默认校准记录用 JC69 下的合成四类群数据，文档写明这个数是校准类上实测的指示性精度，不构成误差界。单个点的误差数取类容差与 3 倍重复分歧中的较大者，4 个内部重复的分歧超过类容差就标 UNGRADED[^jj-r3regime]。
4. **自检电池。** 38 道门，每道是代码检查：精确算术恒等式、必须触发的篡改检查、必须说明原因的拒绝、缺引擎时按名跳过。每道门由若干条子检查（同样叫腿）组成，没在本机跑的腿记为 skipped（ok 为 null），按腿计数，汇总行带跳过数；文档写明，缺少可选能力的主机上得到的 PASS 不能读成被跳过的腿也通过了[^jj-battery]。几道门针对自身：V15 要求损坏一个字节必须让自检失败；V25 用 AST 把 SPEC 里列出的证书种类与 `verify.py` 的分派双向对账；V27 把 `GATES.md` 与 `validate.py` 的门清单双向对账；V37 要求每个值检查都有一个植入缺陷的对照，对照必须按名失败，正向对照必须通过[^jj-gates]。

验证器有三种用法，差别在超出重算范围的值怎么处理：

| 模式 | 参数 | 超出重算范围的值 | `ok` |
|---|---|---|---|
| 默认 | `recompute='auto'`，`strict=False` | 记一条按名跳过（UNVERIFIED beyond the recompute envelope） | 可以为 True，此时值没有核过 |
| strict | `strict=True` | 任何一条跳过都让结果按名失败 | False |
| strict 加重算 | `strict=True, recompute=True` | 重跑到验证器自己的上限，逐字节比对 | 值对不上为 False |

JC69 精确值的默认重算上限是 40 列（`RECOMPUTE_N_MAX = 40`），GUIDE 写明「绝不能接受未核值」的使用方要传 `strict=True` 并给出数据集，成本可以接受时再加 `recompute=True`[^jj-verify-modes]。7.5 的篡改实验显示了三种模式的差别。

验证器的威胁模型限定为善意使用（honest use）：它抓无心之失和意外损坏，不防能改写证书、记录、仓库或解释器环境的人故意伪造[^jj-threat]。

### 7.3 契约文档的写法

仓库根目录的文档分工如下：

| 文件 | 行数 | 管什么 |
|---|---|---|
| `SPEC.md` | 3950 | 规范：入口、档位与档位规则、路由规则、证书 schema、浮点规则、验证器披露、git 隔离、硬件适配、自检电池、Not built（不做什么）、实验特性 |
| `GUIDE.md` | 1771 | 使用：安装、quickstart、每个入口、怎么读和核证书、怎么跑自检 |
| `MODELS.md` | 967 | 模型 × 档位矩阵，以及每个做不到的格子的数学原因 |
| `GATES.md` | 56 | 38 道门的清单，由代码生成 |
| `AMBIGUITIES.md` | 711 | 规范没说死的地方采用了哪种读法，共 33 条 |
| `GM_CORRECTION_CONTRACT.md` | 56 | GM 证据路线的有效范围 |
| `ROADMAP.md` | 70 | 编号的已知限制与后续工作 |

这套文档的几个做法：

- **AMBIGUITIES 把判断写在前面。** 开头声明：凡影响证书声明的判断都写在这里，能写成自检的就写成自检；SPEC 声明这些读法有约束力[^jj-amb]。每条写歧义、采用的读法、理由。例如 A2 在 SPEC 的「K2P N ≲ 40」之外加上实测包络 m ≤ 11、N_B ≤ 24，推出实际上限 N ≤ 35，写明 SPEC 的 40 永远不起作用，也写明包络角上的耗时是小时级；A3 把 K2P gate-projection 的「any-N」收窄到 JC 的 CPU 上限 N ≤ 150，理由是字面上的 any-N 会承诺 N = 10^4 这类规模，而验证只做到 N = 68；A26 写明默认校准数据是合成的[^jj-amb-a2]。
- **清单由代码生成并双向对账。** `GATES.md` 由 `validate.py --write-gates-md` 生成，V27 核对数目、标题、档位和顺序；V25 核对 SPEC 中的证书种类列表与验证器的分派[^jj-gates]。
- **有效范围由记录划定。** GM_CORRECTION_CONTRACT 规定 GM 的证据值只在有精确参照或校准记录覆盖的格子里许可，范围外只给拟合，不给证据值。文档给的理由是：范围外的运行不会崩溃，会返回一个数，诊断指标看起来仍然正常，而算出的下界可以证明这个数偏了几千 nats。消费者规则要求每个证据格说明是哪一档记录覆盖了它。本版停用了 GM 的 R3 路线[^jj-gm]。
- **限制单独列出。** SPEC 的 Not built 一节列出不做什么，包括不上 PyPI[^jj-notbuilt]；ROADMAP 把 9 条已知限制编号，其中一条是随附的 MSC 示例插件在部分历史上把末端枝长配错，300 位点比对上最多差约 24 nats，并写明自检的恒等式查不出它[^jj-roadmap]；MODELS 对 R1 做不到的格子给出原因（HKY85、GTR 的转移概率含无理的特征结构，证据不是有理数）[^jj-models]。
- **拒绝文案带下一步。** SPEC 要求每个 `RegisterUnavailable` 写明缺的能力和能解锁请求的最小能力（`jackandjill/SPEC.md:2089-2092`）。本机实测：`--report` 指向不存在的目录，任何门开跑之前就返回 `REFUSED: ... pass --report PATH (a writable location) ... No gates run.`，退出码 2。

阅读上的成本：根目录 9 份 md 合计约 600 KB、7,751 行；quickstart 代码块 187 行（`jackandjill/GUIDE.md:43-229`），接受与拒绝的规则写在行尾注释里，其中 `px.verify_certificate` 一个调用后面跟了约 100 行注释（`jackandjill/GUIDE.md:104-207`）。自检电池的耗时不写进文档，原文是「walls are printed at run time, never documented」，各门耗时在运行时打印并写进报告[^jj-walls]；路线层面的成本文档里有写，例如 JC69 在 `auto` 下每次调用 480 s 的预算、K2P 在 20–30 列上可能跑几分钟到几小时[^jj-k2pauto]。

### 7.4 依赖、许可证与安装

| 项 | 情况 | 出处 |
|---|---|---|
| Python | ≥ 3.10 | `jackandjill/pyproject.toml:19` |
| 必需依赖 | numpy、scipy、mpmath、sympy，只设下限 | `jackandjill/pyproject.toml:22-29` |
| 可选依赖 | python-flint（R2，缺了按名拒绝）、numba（GM 路线与 kit CPU 引擎，缺了按名跳过）、torch 加 CUDA（大 m 的 R1 GPU 后端） | `jackandjill/pyproject.toml:30-40`、`jackandjill/GUIDE.md:1419-1427` |
| 联网与凭据 | 运行时不联网，参考数据都在 `pins/`；不需要任何 key | 全仓 `*.py` 搜索网络库与 key 相关写法，只命中 `urllib.parse` 的导入 |
| 发布形式 | 不上 PyPI，不出 wheel 或 sdist，只能从源码树运行 | `jackandjill/SPEC.md:3919-3926` |
| 启动方式 | zoo v3 与 free-κ 的 R2 路线要求 fork；macOS、Windows 与 Python 3.14 起的 Linux 默认不是 fork，这些路线按名拒绝 | `jackandjill/SPEC.md:2076-2085` |
| 预编译件 | `phyloexact/quintet/_vendor/fastbnb.so` 是 x86-64 ELF，arm64 机器上回退到 numpy 路径 | 本机 `file` 实测 |
| 规模 | 466 个受跟踪文件，文件字节合计约 9.4 MB，其中 `pins/` 约 3.8 MB、`phyloexact/` 约 4.6 MB | 本机 `git ls-files` 统计 |

**安装限制的原因。** 包运行时要按内容哈希核对旁边的 `pins/`，单独的 wheel 只会把包目录拷进 site-packages，带不走 `pins/`。所以仓内的 PEP 517 后端对 `pip install .`、`pip wheel`、`python -m build` 按名抛 `NonEditableBuildRefused`，支持的方式只有 `pip install -e .` 或把目录加进 `PYTHONPATH`；包目录被单独拷走时，`import` 阶段就按名拒绝[^jj-build]。

**许可证。** 代码 MIT，版权归 Anthropic, PBC；`*.md` 文档与图为 CC BY 4.0，要求的署名串是「JaCKandJill 1.0, Anthropic, PBC and Matthew D. Schwartz (2026), https://www.bootloops.ai/diagrams/jackjill.html」，与 BootLoops 主仓的署名串不同。仓里唯一的 GPL-3.0 文件是数据 `pins/parity/datasets/banked-lysozyme1997.fasta`（1,618 字节，取自 PAML 的示例），NOTICE 声明它是代码读取的数据，所有源文件仍为 MIT。其余序列来自 NCBI（无使用限制）与 Rfam（CC0）。仓里没有第三方代码；可选的 python-flint 包装的 FLINT、Arb 是 LGPL-3.0，不随包分发[^jj-license]。

**耗时。** 安装本身耗时短：本机 `uv pip install -e .` 用 0.85 s（依赖走缓存）。耗时集中在自检电池和部分路线：K2P 在 `auto` 下没有秒级预算，20–30 列、混合位点不多的四类群就可能跑几分钟到几小时[^jj-k2pauto]；默认自检电池在本机合计至少 26 分钟（见 7.5）。

**维护与安全。** README 写明代码由 Claude 在作者指导下写成，仓库由 Matthew D. Schwartz 个人维护，不是 Anthropic 官方支持的产品；公开仓 2026-10-01 创建，只有一个提交，2026-10-02 查询时公开 issue 为 0 条[^jj-maint]。README 的安全条款（输入文件里的 JSON、YAML、pickle 可能执行代码）与 BootLoops 主仓、skills 仓 README 的同名条款逐字相同；包内唯一的 `exec` 用于加载按 sha 钉住的自家引擎模块，没有发现对输入文件做 eval、pickle 或 yaml.load。用户插件模型 `px.PlugIn` 与 `--pin-root` 本身是执行代码的入口，本次没做完整安全审计，标未验证[^jj-security]。

### 7.5 本机实测

环境：本机 macOS（Apple Silicon，15 核），uv 0.12.18 建隔离的 Python 3.12.14 环境，装 numpy 2.5.3、scipy 1.18.1、mpmath 1.3.0、sympy 1.14.0、python-flint 0.9.0；没装 numba，没有 GPU；没有往系统 Python 装任何包。时间为 2026-10-02。数据文件路径相对 JaCKandJill 仓根。

**安装与调用**

下表耗时为单独运行时的数，同日另跑一次，差别在 0.1 s 以内（PEP 723 一行除外）；与全量自检同时运行时更慢，例如 R3 一行当时用了 20.2 s。

| 操作 | 结果 | 耗时 |
|---|---|---|
| `uv pip install -e .` | 成功；之后源码树 `git status --porcelain --ignored` 为空 | 0.85 s |
| `uv pip install .`（非可编辑） | 构建后端抛 `NonEditableBuildRefused` | 未计时 |
| `python -m phyloexact.validate --tree-sha` | `2a6c806bd0e97a90b8a56c73102451a1edbcfe78`，与 `git rev-parse 'HEAD^{tree}'` 相同 | 未计时 |
| `px.evidence`，JC69，强制 R1，`pins/pail_demo/ala.quartet.fasta`（4 类群 × 69 列） | 精确 `Fraction` | 4.05 s |
| 同上，强制 R3 | logZ = −134.9227，标签 `UNGRADED (regime)`：69 列超过校准记录最大的 32 列；4 个内部重复分歧 0.000902 nats；不给误差数 | 1.86 s |
| `px.compare`，GTR+G，拓扑 13\|24 对 14\|23 | `forced-tie`，R0，附置换见证 σ = [1, 0, 2, 3]，没做数值计算 | < 0.01 s |
| `px.compare_models`，K2P 对 JC69 | R3，log BF = −9.36，`UNGRADED`，没有误差界 | 2.76 s |
| `px.quintet.adjudicate`，`pins/hoatzin_quintet/fuzz02.fasta`（5 类群 × 6 列） | `CERTIFIED_ML_WINNER`，T14；预编译件加载失败，引擎回退为 python-numpy | 5.5 s |
| PEP 723 脚本用 `uv run --no-project --script` 起，运行时把源码树加进 `sys.path`，`pins/pail_demo/gln.quartet.fasta` | `compare_models`（R3）返回 UNGRADED；`check_adequacy` 跑完 | `compare_models` 三次分别为 41 s、3.7 s、25.2 s；`check_adequacy` 94.5–95.9 s |

同一个 `compare_models` 调用（gln 四类群，R3）在已装好的环境里直接调用为 2.9–3.8 s。PEP 723 方式下慢的两次是否由 uv 新建环境后的首次运行引起，没有拆分，未验证。

**证书篡改**

取上表 R1 的证书（69 列，超过默认重算上限 40 列），把分子加 1，用三种模式核对：

| 证书 | 模式 | `ok` | 说明 |
|---|---|---|---|
| 原样 | 默认 | True | 执行 18 项、跳过 1 项（UNVERIFIED beyond the recompute envelope） |
| 原样 | strict | False | 失败行为「value not verified」，列出跳过的那一项 |
| 原样 | strict 加重算 | True | 执行 20 项、跳过 0 项，3.9 s |
| 分子加 1 | 默认 | True | 执行 18 项、跳过 1 项，与原样证书相同 |
| 分子加 1 | strict | False | 「value not verified」 |
| 分子加 1 | strict 加重算 | False | 「full exact recomputation byte-identical」失败 |

结果与 GUIDE 的说明一致：默认模式会把跳过写明，但值是否被改过要在 strict 加重算下才能发现[^jj-verify-modes]。

**自检电池**

全量一次跑设了 300 s 上限，跑完 V19 后在 V20 处被杀（退出码 124），其余分批跑：

| 批次 | 结果 | 耗时 |
|---|---|---|
| V1、V2、V3、V25、V27 | PASS，0 条跳过 | 7.7 s |
| V1–V19 | PASS；26 条腿按名跳过（V8 9 条、V9 3 条、V10 1 条、V11 2 条、V16 1 条、V17 10 条），原因是缺 numba 或本机启动方式不是 fork | 各门合计 270 s |
| V20–V24、V26 | PASS | 53.8 s |
| V28–V33 | PASS | 各门合计 243.5 s |
| V34、V35 | PASS | 225.3 s |
| V36 | PASS，56 条腿按名跳过 | 248.2 s |
| V38 | PASS，7 条腿按名跳过 | 255.1 s |
| V37 | 290 s 时被 timeout 杀掉，结果未验证 | > 290 s |

合计 37 道门 PASS、1 道未跑完；已跑完的各门耗时相加约 1,303 s，加上 V37，默认电池在本机至少 26 分钟。最后四批（V34–V35、V36、V37、V38）是同时跑的，单门耗时可能偏高，这组数只说明量级。

跑的过程中看到三件事：

- **公开仓不带开发历史。** GUIDE 写交付的提交历史是开发历史、保留不改写，V36 会把随包记录的 head 逐条解析到历史里的提交；公开仓 `git rev-list --count HEAD` 为 1。V36 跳过的 56 条腿中，49 条的原因是包所在仓库不带包自己的历史，其余 7 条是 fork 3 条、缺 numba 2 条、缺 GPU 1 条、GM 路线停用 1 条。GUIDE 把外部读者拿到的正本定为不带历史的 git-archive tarball，并写明这种情况下这些行按名跳过、不算失败，所以 V36 照样 PASS；依赖历史的出处检查在公开仓上没有执行，外部读者用 pin 的 sha 与 `--tree-sha` 核对身份[^jj-history]。
- **fork 限制在 macOS 上生效。** V9、V10、V11、V36 中依赖 fork 的腿都按名跳过，理由写明本机的启动方式是 spawn，对应 R2 的 zoo v3 与 free-κ 路线在本机不可用。
- **误导性警告。** arm64 上 quintet 加载 x86-64 的预编译件失败时，警告写「$PHYLOEXACT_FASTBNB_SO is set but did not load」，用户并没有设这个变量：包内部在加载前临时设了它，失败后套用了「用户覆盖」的文案。结论不受影响，只是走更慢的 numpy 路径[^jj-warn]。

### 7.6 优势与局限

下面三块分开写：项目本身的优势、项目本身的局限、公开说法与仓库的对照。是否适合平台放在 7.7。

**优势**

- 每个数都带档位和证书；复合量按最弱的一腿标档；做不到时返回说明边界与解锁条件的拒绝，不降档[^jj-law]。实测 69 列的 R3 结果写明 UNGRADED 及原因，不给误差数。
- 验证器独立于产出方，披露由验证器自算；「没查」与「通过」分开计数，汇总行带跳过数[^jj-disclose]。本机篡改实验中，strict 加重算抓到了分子加 1 的改动。
- 文档与代码之间有机器对账（V25、V27），每个值检查都要求植入缺陷的对照（V37）[^jj-gates]。
- 限制公开：Not built、33 条口径取舍、9 条编号的已知限制，包括影响示例最多约 24 nats 的缺陷[^jj-roadmap]。
- 出处钉扎：参考件读取时按 sha256 核对（`jackandjill/SPEC.md:2112-2114`），`--tree-sha` 给整份交付一个身份，本机实测与 git 一致；可编辑安装之后源码树保持干净。
- 不需要任何 key，运行时不联网，必需依赖只有四个 BSD-3-Clause 许可的科学计算库[^jj-license]。

**局限**

- **适用范围限于小规模。** 精确值只到四类群短比对，带误差数的估计只覆盖四类群、JC69 32 列与 K2P 35 列以内；更大的规模只能得到 R0 平局判定、不带误差数的估计、五类群认证排序或基因组尺度的窗口扫描与上界；不搜索树[^jj-r3regime]。
- **默认核对不重算大比对。** 超过 40 列的 JC69 精确值默认不重算，篡改过的证书在默认模式下仍得到 `ok=True`。文档写明了这一点，但要拿到严格的核对，调用方得主动打开 strict 与重算[^jj-verify-modes]。
- **自检耗时长。** 本机默认电池至少 26 分钟，V37 单门超过 290 s；SPEC 称每道门是「fast code-check」，耗时不进文档[^jj-walls]。BootLoops 工具包给 `tools/` 下各包定的时间标准是默认电池在笔记本上约 20 s，JaCKandJill 单独发布、有自己的自检，这条标准是否适用于它，文档没有写[^jj-timestd]。
- **安装受限。** 不上 PyPI，不出 wheel；macOS 与 Windows 上依赖 fork 的 R2 路线不可用；quintet 的预编译件只有 x86-64[^jj-build]。
- **文档篇幅大。** 根目录 md 合计约 600 KB、7,751 行，SPEC 3950 行，quickstart 一个调用的注释约 100 行。
- **开发历史没有公开。** GUIDE 称交付的历史保留开发历史；公开仓只有一个提交，依赖历史的出处检查在公开仓上不执行。GUIDE 预先写明这种情况记为跳过、不算失败[^jj-history]。
- **验证器只防善意使用中的错误**[^jj-threat]；**有一处误导性警告**[^jj-warn]。
- **维护与外部检验。** 个人维护，代码由 Claude 写成；公开仓 2026-10-01 创建，到 2026-10-02 查询时不到一天，暂无外部 issue、复现或纠错记录[^jj-maint]。两篇伴随论文的署名作者另有 Scott V. Edwards 与 Paul O. Lewis[^jj-papers]。

**公开说法核对**

| 说法 | 出处 | 与仓库和实测对照 |
|---|---|---|
| 让系统发育证据「算得快、可以精确核对」 | 博客[^jj-blog] | R1 精确值只覆盖四类群短比对，五类群精确值只到窗口尺度；网站写 tRNA-Gln（68 列、25 个混合位点）三棵树的精确值在 72 核上用时约为单核 MrBayes 的 3 倍，R3 估计在网站基准里每个问题约 4 s；本机 69 列四类群 JC69 精确值 4.05 s。验证器默认对 40 列以上的 JC69 精确值不重算，要 strict 加重算才逐字节核对。小规模四类群上与仓库和实测相符；博客这一句没写规模条件，同一段开头写明这些项目都与领域专家合作、仍在进一步探索与核查 |
| 「单个基因常常在竞争的树之间平局，差距小于常用采样程序的误差」 | 博客 | 网站给的依据：tRNA-Phe 四类群两棵树的证据是同一个分数，同一比对上 stepping-stone 运行间相差 0.017 到 0.067 log units；按蚊 5,375 个窗口与四类群组合中 2,997 个精确平局。本机在随包的 tRNA-Ala 四类群上得到一例 R0 平局（7.5），只是单个例子。「常常」属研究结论，本次没有复核，未验证 |
| 「一条命令跑 38 项验证」 | 网站摘要[^jj-phyloweb] | 属实，`python -m phyloexact.validate`，38 道门；网站与文档都没写耗时，本机至少 26 分钟 |
| JC69 小四类群（约 32 列以内）的估计值带 0.014 log units 的指示性误差 | 网站摘要 | 与 AMBIGUITIES A26 一致（JC69 v1 模式、预算 100,000 档为 0.014），文档写明它是校准类上的实测值，不构成误差界 |
| 四个模型下都给「带实测误差的估计」，等时间下比 MrBayes、RevBayes、LoRaD 准 20 到 200 倍 | JaCK & Jill 论文摘要[^jj-papers] | 网站摘要给出倍数的来源：九个 tRNA 问题（JC69 下有精确值），等时间约 7 s 时误差比 LoRaD 低 20–44 倍、比两个 stepping-stone 程序低 67–213 倍[^jj-phyloweb]；基准本次没有复跑，未验证。随包版本里四个模型的 R3 估计都带内部重复分歧，带误差数的只有校准范围内的 JC69 与 K2P，HKY85、GTR 路线的点不带误差数[^jj-r3regime]；摘要的「measured error」指哪一种，本次没读论文 PDF，未验证 |
| 两篇伴随论文 | papers 页、网页摘要 | 两篇都标 preliminary version，尚未正式发表；papers 页写明所有稿件都经人读过，许多先由大模型起草，标 preliminary 的是还没被人完整核对的稿件 |

### 7.7 和平台的关系

平台 `docs/cases/` 的七个案例涉及药剂学、系统生物学、多模态机器学习、流行病学、计算物理，没有系统发育课题[^jj-cases]。项目负责人已定不收录。平台已收录的 skill 里，biopython 的 Bio.Phylo 只管树的读写、绘制与构建（`platform/skills-curated/experiment/biology/biopython/SKILL.md:35,193`），在 `platform/skills-curated/` 搜 marginal likelihood、Bayes factor、MrBayes、phylogen，没有能算系统发育边际似然的 skill。JaCKandJill 是计算包，与平台文献阶段的缺口无关。下面只陈述对应关系。

**如果以后有系统发育课题，它能对上平台的哪里**

| 平台位置 | 对应 | 约束 |
|---|---|---|
| 领域包 `domains/<id>/`，按工具链命名，skill 与 `skills/` 同格式 | phyloexact 作为领域工具，skill 摆在实验阶段的生物架下 | skill 脚本要有 PEP 723 块和锁文件；phyloexact 不能写成 PEP 723 依赖（不上 PyPI，非可编辑构建被拒），只能在运行时把源码树放进 `sys.path`，本机实测可行（7.5）[^jj-domain] |
| 收录台账与许可证白名单 | 代码 MIT 在白名单内 | 台账核对只覆盖 `skills-curated/`，领域包没有台账；文档的 CC BY 4.0 与一个 GPL-3.0 数据文件不在白名单里[^jj-ledger] |
| P-27「一个 key 都不要」 | 满足 | 运行时不联网[^jj-p27] |
| 复现流的评分脚本 evaluate | 精确 logZ 或贝叶斯因子可以作为评分指标 | 规模受 7.1 的范围限制 |
| 评测 | `pins/parity` 的 66 行清单、57 个精确值（V26）可以当作「能否算对一个精确证据值」的标准答案 | 57 个值里 18 个本包引擎自己也按名拒绝；这一用途未验证[^jj-parity] |

**契约写法与平台复现流的对应**

平台的论文复现流（P-24）涉及需求文档 `requirement.md`、评分契约 `scoring.yaml`、复现性分析 `analysis.md` 与零模型的验证步骤 `verify`，对没对上由研究者按需求里的标准签字判定[^jj-p24]。逐项对应如下：

| JaCKandJill | 平台复现流 | 两边的做法 |
|---|---|---|
| SPEC 的 Not built | `requirement.md` 的「不复现的」 | 两边都事先写明不做什么[^jj-req] |
| 档位与验证器规则，强度由机器判定 | `requirement.md` 的「怎么算对上」与 `scoring.yaml` 的 `requirements` | 平台的判定由研究者签字；`requirements` 有 schema，唯一的读取点只查 id 重复，GUA 的两条 numeric 条件写在 description 文字里[^jj-requirements] |
| AMBIGUITIES：口径取舍事先写下、有约束力、能写成自检的就写成自检 | 复现需求模板没有专门记口径的一节，GUA 的「跑几次、与论文同口径」写在「怎么算对上」里 | σ 的算法由框架固定（只用 repeat_1~4），写在代码里，分析稿里加以说明；gua-codex-drill 的基线曾因种子列表被拒，之后改为由框架统一算 σ[^jj-sigma] |
| GATES 与自检电池，跳过单独计数 | `verify` 的检查项与 `report.json` | 平台的 `Check` 只有 `passed` 布尔值，`report.json` 的 status 只有 PASS、FAIL；复现路径不跑账本项，GUA 的报告只有三项[^jj-check] |
| 验证器自算披露 | `verify` 把数据表里的数回溯到 results.json，容差 1%；整数与百分比不查 | GUA 分析里五个种子的均值与「高约 13%」由正文自算[^jj-tol] |
| GM_CORRECTION_CONTRACT：范围外只给拟合，不给证据 | 分析稿必有「证伪与未决」一节 | 平台用文字说明范围，JaCKandJill 用校准记录划界、由代码拒绝[^jj-analysis] |
| ROADMAP 的编号已知限制 | 案例卡的「留着的债」 | 都公开记录（`docs/cases/README.md:21`） |
| pins 的 sha256、`--tree-sha` | 原件索引带 sha256；`upstream.diff` 由框架逐字节比出 | download 的收据记 commit，不记 tree 哈希[^jj-pins] |

[^jj-codesize]: 本机统计：`phyloexact/validate.py`（自检电池）28,927 行、`phyloexact/verify.py`（证书验证器）11,465 行，合计 40,392 行，占 `phyloexact/` 下 55 个 `.py` 文件共 71,237 行的 57%；全仓 122 个 `.py` 文件共 87,560 行。门数见 `jackandjill/GATES.md:19-56`，实测见 7.5。
[^jj-r4]: `jackandjill/GUIDE.md:32-39`（R4：现有估计方法单次运行不认证自身误差）。
[^jj-ladder]: `jackandjill/SPEC.md:85-104`；`jackandjill/GUIDE.md:11-30`。仓库 <https://github.com/BootLoops-ai/jackandjill>，提交 e0ccb07；`jackandjill/pyproject.toml:13-14`（版本 1.0.0）。
[^jj-r1env]: `jackandjill/phyloexact/router.py:82`（`JC_CPU_N_MAX = 150`）、`:148`（`JC_AUTO_ENVELOPE`）、`:100`（`R0_N_TAXA_MAX = 32`）；`jackandjill/GUIDE.md:894-916`（auto 下的成本）。
[^jj-r3regime]: `jackandjill/AMBIGUITIES.md:368-392`（A26：容差规则、合成校准、范围 JC N ≤ 32、m ≤ 9，K2P N ≤ 35、m ≤ 11）；`jackandjill/phyloexact/lanes/r3.py:458-468`（类群数不在记录内即出范围，记录只扫 n_taxa = 4）；`jackandjill/pins/r3_calibration_sweep/R3_SEED_SWEEP.json:20`（「the plug-in / zoo / GTR lanes are not swept: their points carry no tolerance from this record」）；`jackandjill/SPEC.md:94-104`（每个 R3 结果都带重复分歧）。
[^jj-quartet]: `jackandjill/SPEC.md:3895-3899`；`jackandjill/GUIDE.md:86-90`、`:937-941`、`:1106-1110`（`px.hill` 的 H1 窗口扫描、H2 精确上界、H3 认证权重文件）。
[^jj-notfor]: `jackandjill/GUIDE.md:926-941`；`jackandjill/SPEC.md:3908-3913`；网页摘要 <https://www.bootloops.ai/summaries/phylo.html>「JaCK & Jill: the method as software」一段（「does not search over trees」）。
[^jj-900]: `jackandjill/THIRD_PARTY.md:23-27`（随包序列：tRNA-Phe 五类群约 71 nt、PAIL 演示的 18 个 tRNA 四类群 66–75 nt、溶菌酶 4 × 390 nt 等）；本机 V26 日志中 `lysozyme:consA` 三行为 REFUSED-BY-NAME；<https://www.bootloops.ai/summaries/phylo.html>「The integral is a fraction」一段（tRNA-Gln 68 列、25 个混合位点；两条约 900 列的比对 remain out of reach）。
[^jj-law]: `jackandjill/SPEC.md:94-104`（Register law）。
[^jj-disclose]: `jackandjill/SPEC.md:1658-1700`（Verifier-stated disclosures）；`jackandjill/GUIDE.md:188-194`。
[^jj-battery]: `jackandjill/SPEC.md:2116-2139`。
[^jj-gates]: `jackandjill/GATES.md:3-7`（由代码生成、V27 双向对账）、`:33`（V15）、`:43`（V25）、`:45`（V27）、`:55`（V37）。
[^jj-verify-modes]: `jackandjill/GUIDE.md:125-145`、`:195-203`；`jackandjill/phyloexact/verify.py:469`（`RECOMPUTE_N_MAX = 40`）。
[^jj-threat]: `jackandjill/SPEC.md:639-651`；`jackandjill/GUIDE.md:231-244`。
[^jj-amb]: `jackandjill/AMBIGUITIES.md:1-7`；`jackandjill/SPEC.md:9-14`。引用的文档文字为 CC BY 4.0，署名见 `jackandjill/LICENSE-CONTENT:6-8`。
[^jj-amb-a2]: `jackandjill/AMBIGUITIES.md:28-48`（A2）、`:50-58`（A3）、`:368-392`（A26）。
[^jj-gm]: `jackandjill/GM_CORRECTION_CONTRACT.md:9-27`（范围规则）、`:29-36`（为什么按记录划界，原句「an out-of-envelope run does not crash, it returns a number」）、`:38-41`（消费者规则）、`:45-49`（本版停用 GM R3）。
[^jj-notbuilt]: `jackandjill/SPEC.md:3884-3926`。
[^jj-roadmap]: `jackandjill/ROADMAP.md:7-53`，示例缺陷在 `:38-46`。
[^jj-models]: `jackandjill/MODELS.md:75-80`。
[^jj-walls]: `jackandjill/SPEC.md:2118`（「Every gate is a fast code-check」）、`:2164-2166`；`jackandjill/GUIDE.md:1641-1642`（耗时运行时打印并记入报告，不写进指南）。
[^jj-build]: `jackandjill/_build_backend.py:14-19`、`:34-52`；`jackandjill/SPEC.md:3919-3926`；`jackandjill/GUIDE.md:1429-1448`；`jackandjill/SPEC.md:2076-2085`（fork）。
[^jj-license]: `jackandjill/LICENSE:1-3`；`jackandjill/LICENSE-CONTENT:1-14`；`jackandjill/NOTICE:21-44`；`jackandjill/THIRD_PARTY.md:9-17`（无第三方代码）、`:23-27`（数据来源与条款）、`:42-43`（依赖库许可证）。
[^jj-k2pauto]: `jackandjill/ROADMAP.md:9-14`；`jackandjill/GUIDE.md:894-916`（JC69 `auto` 每次调用 480 s 的预算，K2P 在 `auto` 下没有秒级预算）。
[^jj-maint]: `jackandjill/README.md:3-5`、`:39-44`；`jackandjill/NOTICE:4-7`；`git rev-list --count HEAD` 输出 1（提交 e0ccb07「JaCKandJill 1.0」）；2026-10-02 查询 GitHub API，<https://github.com/BootLoops-ai/jackandjill> 的创建时间为 2026-10-01，issues（含已关闭）为 0 条。
[^jj-security]: `jackandjill/README.md:46-53`，与 `bootloops/README.md:236-243`、`skills/README.md:185-192` 逐字相同；`jackandjill/phyloexact/lanes/_pins.py:1481`（全包唯一的 `exec`）。
[^jj-history]: `jackandjill/GUIDE.md:1490-1501`（外部读者的正本是 git-archive tarball，不带历史时 V36 的 head 行记为跳过）、`:1592-1599`（「the history is kept as delivered rather than rewritten」）；V36 跳过原因按本机 `VALIDATION_REPORT.json` 的 `skipped_legs` 统计。
[^jj-warn]: `jackandjill/phyloexact/quintet/__init__.py:319-323`（内部临时设置环境变量后调用加载）；`jackandjill/phyloexact/quintet/_vendor/ml_rank.py:176-183`（按「用户覆盖」的文案报警）。
[^jj-timestd]: `bootloops/tools/README.md:17`（Time standard）、`:126-129`（JaCK & Jill 单独成仓，with its own self-certification suite）。
[^jj-blog]: Matthew Schwartz, *Claude-shaped science*，<https://www.anthropic.com/research/claude-shaped-science>，Phylogenetics 一条及其所在段的开头一句（「each of which was done in collaboration with experts, and each of which is undergoing further exploration and verification」）。
[^jj-phyloweb]: <https://www.bootloops.ai/summaries/phylo.html>，「JaCK & Jill: the method as software」与「Testing the estimators against the answer」两段（含九个问题的基准与 20–44 倍、67–213 倍）；72 核用时在「The integral is a fraction」一段，平局数字与 stepping-stone 运行间差异在「An exact tie among the great apes」与「Beyond one gene」两段。
[^jj-papers]: <https://www.bootloops.ai/papers.html>（页首说明与 JaCK & Jill 条目，含署名）；网页摘要页对两篇论文都写「A preliminary version of the paper」。
[^jj-cases]: `docs/cases/README.md:9-15`。
[^jj-domain]: `platform/docs/add-a-domain.md:9-11`、`:43`；`platform/framework/skills/shelves.py:32-34`（实验阶段的「生物」子类）；`platform/framework/skills/library.py:353-363`（脚本的 PEP 723 块与锁文件检查）；`docs/architecture/README.md:172`（P-22）。
[^jj-ledger]: `platform/framework/skills/provenance.py:55`（许可证白名单 MIT、Apache-2.0、BSD-2-Clause、BSD-3-Clause、ISC）、`:87-90`（台账核对只读 `skills-curated/`）。
[^jj-p27]: `docs/architecture/README.md:177`。
[^jj-parity]: `jackandjill/GATES.md:44`（V26：66 行、57 个精确值的清单）；本机 V26 日志「57 distinct values (39 runnable, 18 scope-certified)」。这一用途是上一轮调研提出的设想，没有实际试过。
[^jj-p24]: `docs/architecture/README.md:174`；`platform/framework/capabilities/reproducibility/__init__.py:48-50`（复现性分析不替人判算不算复现成功）。
[^jj-req]: `docs/cases/gua-pinn-reproduction/requirement.md:24-29`（不复现的）、`:45-51`（怎么算对上）。
[^jj-requirements]: `platform/framework/experiment/schemas/scoring.schema.json:104-137`；`platform/framework/experiment/pack.py:153-158`；`docs/architecture/open-questions.md:23-28`（Q-3）；`docs/cases/gua-pinn-reproduction/scoring.yaml:16-24`。
[^jj-sigma]: `platform/templates/reproduce.md:1-29`（章节为论文、要复现的数、复现到第几级、材料、怎么算对上、算力环境与预算、交付）；`docs/cases/gua-pinn-reproduction/requirement.md:49`；`platform/framework/experiment/baseline.py:15-16`；`docs/cases/gua-pinn-reproduction/analysis.md:24`；`docs/cases/README.md:15`。
[^jj-check]: `platform/framework/capabilities/verify/checks.py:22-29`；`platform/framework/experiment/schemas/report.schema.json:10`；`platform/framework/capabilities/verify/__init__.py:97-99`（账本项只对实验产出跑）；`docs/cases/gua-pinn-reproduction/report.json`（analysis_present、numbers_traceable、prose_numbers_in_table 三项）。
[^jj-tol]: `platform/framework/capabilities/verify/__init__.py:27`（容差 1%）；`platform/framework/capabilities/verify/checks.py:6-7`（整数与百分比不查）；`docs/cases/gua-pinn-reproduction/analysis.md:3`、`:24`。
[^jj-analysis]: `platform/framework/experiment/analysis.py:24`（结论、数据、证伪与未决三节必有）；对照 `jackandjill/GM_CORRECTION_CONTRACT.md:38-49`。
[^jj-pins]: `docs/cases/README.md:22`；`platform/framework/experiment/pack.py:561-580`（`write_upstream_diff` 逐字节比对）；`platform/skills/general/materials/download/scripts/fetch.py:96-99`（收据字段）；JaCKandJill 侧见 `jackandjill/SPEC.md:2112-2114` 与 `jackandjill/GUIDE.md:1501-1507`。

## 8. 与本平台的对照

平台收录外部 skill 有几道硬门槛：许可证只收 MIT、Apache-2.0、BSD、ISC，CC-BY 系列不收[^rp-lic]；默认用法要 key 的不收（P-27）；两层 agent 面前只有 `ai4sci` 命令，核心做法离不开 MCP、子代理、装系统软件的不收[^rp-gates]；脚本要 PEP 723 自带依赖并锁版本；名字在三处库里唯一。BootLoops 各部分逐项过一遍：12 个 skill 的正文都是 CC BY 4.0，不在白名单里；工具包与 JaCKandJill 的代码是 MIT，服务的课题在平台现有案例里没有，外部程序与安装方式也与收录规则有冲突。负责人据此定为不收录。下面把逐项结果、与平台已有能力的重叠、以及对照中看到的平台自身问题分别记下。

### 8.1 逐项对照收录门槛

| 部分 | 许可证 | 零 key | 在平台里能不能用 | 其他 |
|---|---|---|---|---|
| 协议层 7 个 skill | 正文 CC BY 4.0，不在可收范围 | 平台扫描 0 处；无脚本、无外部调用 | 纯文字，没有脚本；acceptance-gate、independence-bookkeeping、constant-recognition 以高精度数值为语境，用到带噪实验要换说法；tool-stewardship 的读者是工具包维护者 | frontmatter 过平台解析器；无重名 |
| lit-review、ref-check | 同上 | 扫描 0 处；但点名 NASA ADS（要 token）与 MathSciNet（订阅库），门禁的正则查不出，按收录规则由收录的人判断 | 两个都写了子代理可选；lit-review 原文给出了不支持子代理时的顺序做法 | ref-check 的重编译检查要系统装 LaTeX |
| prose-lint | 同上 | 扫描 0 处 | 可读 | frontmatter 第 3 行 description 未加引号且含冒号，平台解析器报 YAML 错误，整个 skill 被隔离[^rp-prose] |
| referee-sim | 同上 | 扫描 0 处 | 要求在新的隔离上下文里跑；平台的隔离模型评审（P-2）尚未实现 | — |
| prove-protocol | 同上 | 扫描 0 处 | 面向数学证明；核心依赖多个新上下文与并行证明者，平台会话里没有子代理 | — |
| bootloops-setup、plugins/ | — | — | setup 先问用户、把选中的 skill 拷进 agent 自带的 skill 目录；平台按 P-22 由框架拼清单注入，不走 agent 的原生加载 | plugins/ 是 skills/ 的生成副本，内容逐字相同 |
| 工具包主体 | 代码 MIT；3 个 GPL 文件；GUIDE 等说明文字 CC BY 4.0；部分随仓数据是 CC BY 或 CC BY-SA | 无 key | 部分包要 Julia 与十余种外部程序（多为 GPL），三个引擎分叉要从源码编译，收录规则把核心离不开装系统软件的排除在外；amflow-kit、seedling 含只在 Linux 上成立的代码；不在 PyPI，接入要另写 PEP 723 入口 | 49 个包里 34 个服务理论物理与数学物理，见[第 6 节](#6-计算工具包) |
| emitall 的 `paper_seams.py`（工具包中的一个文件） | MIT，单文件，只用标准库 | 无 key | 本机自检通过（emitall 的 69 个测试含它的测试）；只查 LaTeX 稿的注释吞句，S2 一项要 pdftotext，没有时跳过并写明 | 许可证与零 key 两条都满足；收录要补 PEP 723 头，SKILL.md 正文要另写（GUIDE 是 CC BY 4.0） |
| JaCKandJill | 代码 MIT；文档 CC BY 4.0；一个数据文件 GPL-3.0 | 无 key | 不在 PyPI，构建方式与 PEP 723 依赖写法冲突；默认自检耗时长 | 现有案例里没有系统发育课题，见[第 7 节](#7-jackandjill系统发育证据) |

### 8.2 与平台已有能力的重叠

BootLoops 的协议与平台已有的步骤、已收录的 skill 有不同程度的重叠。下表左列是 BootLoops 的条目，右两列分别是已经覆盖的部分与它多出来的部分。路径相对 `platform/`。

| BootLoops | 平台已有 | 已覆盖 | BootLoops 多出来的 |
|---|---|---|---|
| acceptance-gate | 步骤 `verify`（`framework/capabilities/verify/`）；AutoResearch 统计门（`framework/capabilities/auto_research/gate.py`）；`scoring.yaml` 设计阶段封存并签字 | 门在实验前写定；报数字不写形容词 | 留出点、负对照、门槛定下后不许动、提精度后一致位数要加深 |
| planted-truth | `verify` 自身的负对照测试（`tests/test_capability_verify.py`）；已收录 analytical-method-validation（加标回收） | 框架自己的检查有负对照 | 对每个任务的评测脚本喂坏产物与植入已知答案的产物 |
| independence-bookkeeping | 实验账本、`upstream.diff`、签字记 hash | 出处记账 | 「参与过拟合或挑选的参考值不能用来认证」的反事实判据与接触日志 |
| timing-discipline | 实验前的 headroom 预检 | — | 先小规模实测再预估总时长；定义真实的进度单位 |
| reading-contract | 已收录 nature-paper-card、nature-reader、ara-compiler | 逐篇精读；页码定位；原文不支持时如实说明 | 「读到 / 推断 / 背景记忆」三栏；已发表数值的四种核对结论；保留原文的语气强度 |
| lit-review | 已收录 paper-lookup、citation-management、nature-ref-verifier、hypothesis-generation；平台自带 pdf | 检索与元数据核对；带日期的检索边界台账、前后向引文追踪、写明的停止规则（hypothesis-generation） | P0–P5 接近度分级与对应义务、FULL-TEXT-UNREAD 标记、P3 以上作者的近作扫到当月、断掉的检索通道算作欠账、先钉主张再逐条裁定 |
| ref-check | 已收录 nature-ref-verifier（覆盖中文 DOI 与 CNKI）、nature-citation（按主张分级的支持度）、scientific-writing 的 evidence_workflow | 元数据核对；主张是否被支持 | DRIFTED、ABSENT 等五分类；强制记定位；只报告不改写 |
| prose-lint | 已收录 scientific-writing 的 `lint_manuscript.py`（夸大词、因果措辞）、nature-polishing 与 nature-writing 的用词规则 | 夸大词与因果措辞；禁破折号；禁无依据的「the first」 | 英文套话词表、B 节句式条目、N 节数字舍入纪律 |
| referee-sim | 已收录 nature-reviewer、peer-review | 模拟审稿；原创性与非专业读者可读性两轴 | 按学术群体列读者（含借用方法的群体与 incumbent）、每群两条质疑、阅读路径、冷读摘要、判定表文件；查「每句都真、合起来误导」 |
| prove-protocol | 已收录 hypothesis-generation（竞争假设、可区分的预测）、scientific-brainstorming（文字形式的对抗评审） | 竞争假设与对抗提问 | 带实例与数值的反驳、埋错审计、VERIFIED-CLOSED 评级 |
| constant-recognition | 无 | — | PSLQ 常数识别的位数预算与正负对照 |
| tool-stewardship | 外层仓规矩；`docs/add-a-skill.md` 的四件事；步骤描述符的几栏 | 说明页写做什么、什么时候用、留下什么 | 「信它之前要过什么测试」 |

### 8.3 对照中看到的平台自身问题

下面这些是拿 BootLoops 的协议对照平台时看到的平台现状，和收不收录无关，记在这里备查，本轮不处理。

| 问题 | 现状（出处） | BootLoops 里相关的条款 | 相关 issue |
|---|---|---|---|
| AutoResearch 挑选与认证用的是同一次测量 | 内环每轮沿用基线那一个种子（`platform/framework/experiment/context.py:88`），keep 判决与最终报告的最好结果是同一次测量；`verify` 不重跑实验（`platform/framework/capabilities/verify/__init__.py:42-45`）；框架里没有「留出数据」这个概念。按 independence-bookkeeping 的反事实判据推一步（原文没有写到 ML 场景）：只换种子去不掉对评分数据本身的挑选，认证需要一份设计阶段封存、循环从没见过的数据 | acceptance-gate 的留出点与门槛漂移；independence-bookkeeping 的反事实判据 | [#125](https://github.com/zephyr4123/TJU-AI4Science/issues/125)、[#10](https://github.com/zephyr4123/TJU-AI4Science/issues/10) |
| 每个任务的评测脚本没被证明会报错 | 框架只查 harness 文件齐全与 SHA256（`platform/framework/experiment/pack.py:218` 起），harness 契约规定的拒收退出码从没被喂坏产物验证过 | planted-truth：每个检查都要故意弄坏一次看它报错 | [#10](https://github.com/zephyr4123/TJU-AI4Science/issues/10) |
| `verify` 不查百分比，复现分析的提示要求相对差异写百分比 | `verify` 的说明写明「整数与百分比不查」（`platform/framework/capabilities/verify/checks.py:7`）；复现分析的提示要求结论写「差多少（写百分比或倍数）」、相对差异一律写百分比（`platform/framework/capabilities/reproducibility/prompt.md:45`、`:53`） | emitall 的比对规则：按引文印出的精度比、计数也核对 | — |
| 检查结果只有通过与不通过两态 | `Check` 只有 `passed: bool`（`platform/framework/capabilities/verify/checks.py:23-26`）；复现路径不跑账本项，`report.json` 只列跑过的检查项，不记录哪些项没跑（`platform/framework/capabilities/verify/__init__.py:97-99`） | planted-truth：汇总必须写分母；JaCKandJill 的检查三态 | [#10](https://github.com/zephyr4123/TJU-AI4Science/issues/10) |
| 评分契约里的验收条件没有判定 | `requirements` 唯一的读取点是检查 id 重复（`platform/framework/experiment/pack.py:153-158`） | acceptance-gate：门在实验前写定、判决只有过与没过 | [#10](https://github.com/zephyr4123/TJU-AI4Science/issues/10) |
| 文献综述缺口 | 文献阶段没有步骤，#154 列了检索、逐篇取证、组织结构、带引用成文、引用核对五段缺口 | lit-review 能覆盖逐篇取证与检索纪律，不覆盖组织结构与成文，见[第 5 节](#5-研究-skill5-个) | [#154](https://github.com/zephyr4123/TJU-AI4Science/issues/154) |
| 已收录 paper-lookup 对 OpenAlex 限额的说明不全 | `platform/skills-curated/literature/search/paper-lookup/SKILL.md:129`、`:152` 只写匿名 `search=` 在高负载时会 429；2026-10-02 实测：匿名每天 1000 credit，`search=` 与 `title.search` 这类全文检索每次 10，`doi`、`cites` 这类精确过滤每次 1，单条 ID 查询 0，另有每天 0.1 美元的额度，折合约每天 100 次关键词检索（见 [5.1](#51-lit-review)）[^rp-openalex] | lit-review 要求迭代检索到没有新结果为止，每天约 100 次关键词检索会限制能跑的轮数 | [#154](https://github.com/zephyr4123/TJU-AI4Science/issues/154) |
| 远端装环境看不到进度 | GUA 演练的对话记录写「隔离新建要在 AutoDL 上下 CUDA 版 torch，之前实测两个多小时都装不完」（`docs/cases/gua-pinn-reproduction/transcript.md:117`）；#127 记的是远端 `uv pip sync` 装几十分钟、作业日志里一行输出都没有 | timing-discipline：日志与进程存活不算进度，要定义真实的进度单位 | [#127](https://github.com/zephyr4123/TJU-AI4Science/issues/127) |

## 9. 总体评价

三件事分开看：项目本身做得怎么样，公开说法准不准，对本平台适不适配。

### 9.1 项目本身

| 部分 | 优势 | 局限 |
|---|---|---|
| 计算工具包 | 49 个包都有说明页，按用途、适用与不适用、调用方式、验收条件与已知的坑等栏目写，栏目齐全程度不一（46 份有 NOT-FOR 段），索引逐包标验证等级；每包一条固定自检命令，本机 92.7 s 跑完；拒绝带名字、退出码分类型，自检里放了必须失败的变异对照；不需要任何凭据；`THIRD_PARTY.md` 逐文件记来源与许可证 | 34 个包服务理论物理与数学物理；部分包要 Julia 与十余种外部程序，多为 GPL、要编译；只在 Linux 上做发布测试，本机 4 个失败；PASS 不区分跳过，至少 23 个 PASS 含跳过的子项，什么都没验证的包也记 PASS；验证等级、依赖说明与实际有出入；说明页默认读者熟悉本领域 |
| 协议层 skill | 规则写成可检查的条件：门在拟合前写定、检查要先看到它失败、参与过挑选的数据不能用来认证；失败模式按机制写；7 个里 4 个列了方法的学术出处 | acceptance-gate、independence-bookkeeping 以确定性高精度数值为语境，精度翻倍重跑、留一法等条款在随机训练上没有直接对应；3 个没有出处；没有配套工具，账本要手写 |
| 研究 skill | 规定了可检查的产物（逐条裁定、判定表文件）；ref-check 写明陷阱来自实际审计；prose-lint 附了可运行的检查正则 | 效果说法没有运行次数或记录，三个仓里没有产出样例；referee-sim、prove-protocol 的核心保证来自隔离上下文；检索渠道与词表只覆盖英文；lit-review、ref-check 点名了需要账号的服务 |
| JaCKandJill | 每个数带声明强度与证书，复合量取最弱一档；验证器独立于产出方，「没查」与「通过」分开计数；文档与代码有机器对账；口径取舍与已知限制公开列出 | 精确值只覆盖四类群的短比对；默认验证模式不重算大比对，本机实测篡改过的证书在默认模式下仍得 `ok=True`；本机自检至少 26 分钟；只能从源码树运行 |

几部分共同的情况：代码以 MIT 为主（工具包另有 3 个 GPL 文件），skill 正文与说明文字是 CC BY 4.0；运行不需要 key；由 Schwartz 一人维护，代码由 Claude 在他指导下写成；截至 2026-10-02 05:04 UTC 没有外部 issue、贡献或复现记录，查询时距博客发布约 15 小时，这一点不能用来判断结果对错。

### 9.2 公开说法

- **原文**：手稿数、合著者数、积分数与经济学、语言学两项的数字能在网站或 NBER 页面上对上；披露了利益关系（作者是 Anthropic 访问研究员、项目由 Anthropic 资助、代码由 Claude 写成）；写明了多条局限，包括「多数科学问题做不了」「技术上对、科学上未必有价值」「论文写得不好、部分未经人完整核对」（[3.5](#35-原文承认的局限与没说的)）。
- **口径**：领域数在博客、官网、手稿页分别是 18、22、9 组；工具数是网站 59 个页面、贡献表 49 个包；36 条手稿中 7 条尚无稿，有稿的除 1 篇 NBER 工作论文外页面上没有期刊、arXiv 或 DOI 链接；「与模型无关」没有其他模型驱动的实测；没有给出成本数字和落选候选（[3.2](#32-手稿清单与状态)、[3.5](#35-原文承认的局限与没说的)）。
- **仓库自述与本机实测不符的几处**：README 说纯 Python 包没有平台相关代码，amflow-kit、seedling 读 Linux 的 `/proc`；README 说缺外部引擎的自检会跳过并说明要装什么，counterweight 缺 Julia 时直接退出码 127（[6.9](#69-公开说法核对)）。
- **中文转载**：八条说法里的数字在原文都有对应原句，偏差在发布方与文章类型、计数单位与分母、模型适配范围三处（[3.3](#33-中文转载说法逐条核对)）。

### 9.3 对本平台

不收录的原因有三类：许可证（skill 正文与工具包说明页是 CC BY 4.0，部分包含 GPL 文件或 CC BY、CC BY-SA 数据）；学科（工具包与 JaCKandJill 服务的课题，平台现有 7 个案例里没有）；平台约束（外部程序要装系统软件、referee-sim 与 prove-protocol 依赖平台没有的隔离上下文或子代理、工具包与 JaCKandJill 都不能写成 PEP 723 依赖）。此外，研究 skill 的书目元数据核对、主张支持度、夸大词检查、检索台账，在已收录的 skill 里已有对应（[8.2](#82-与平台已有能力的重叠)）。

与平台现状能对上的部分：协议层 skill 对验收的几条规则，对应 #10、#125 记录的现状（[8.3](#83-对照中看到的平台自身问题)）；工具包说明页的四问与验证等级；JaCKandJill 把口径取舍、不做什么、已知限制分文件写明，并把「没查」与「通过」分开计数。

## 10. 结论依赖的现状

不收录的结论建立在 2026-10-02 的下列现状上：

- 平台现有 7 个案例的课题是回归、连续参数优化、表示学习与论文复现，没有高精度数值、整数关系识别、费曼积分、群体遗传或系统发育课题（[6.8](#68-和平台的关系)、[7.7](#77-和平台的关系)）；JaCKandJill 的精确值只覆盖四类群的短比对（[7.1](#71-解决什么问题)）。
- 收录许可证白名单只有 MIT、Apache-2.0、BSD、ISC，CC-BY 系列 2026-10-01 定为不收（#198）。CC BY 4.0 的再分发条件是署名、保留版权声明、给出许可证链接、写明是否修改；台账每个上游只有一个 `license` 字段，记不下 skills 仓「脚本 MIT、正文 CC BY 4.0」的双许可（[4.1](#41-共同点)）。
- 平台会话里没有子代理，P-2 的隔离模型评审尚未实现（[5.4](#54-referee-sim)）。
- 评估对象是 BootLoops 1.0（提交 66b680c、ca89227、e0ccb07）；查询时没有外部复现或同行评审记录（[3.2](#32-手稿清单与状态)）。

## 11. 怎么做的

1. 三个仓库克隆到本地，固定在上面列的提交上，只读不改。
2. 分六块独立阅读：协议层 skill、研究 skill、工具包、JaCKandJill、原文与公开说法、平台自己的收录门槛与开着的 issue。工具包与 JaCKandJill 在本机 macOS（Apple Silicon）用 uv 建的隔离环境里实跑自检，不往全局装任何东西。
3. 一个会话汇总六块的结果，逐项对照平台门槛。
4. 两个没参与前面工作的会话回源复查：一个打开 BootLoops 原文核对事实，一个用平台真实的解析器、零 key 扫描与重名规则实测。共核 53 条说法，判错 1 条、部分不准 21 条，本文按更正后的说法写。
5. 报告分节起草，每节由另一个会话回源核对事实、检查褒贬是否有证据支撑。
6. 负责人看完结论，定为不收录、存档备查（[#208](https://github.com/zephyr4123/TJU-AI4Science/issues/208)）。

[^rp-lic]: `platform/framework/skills/provenance.py:53-55`；`platform/docs/add-a-skill.md:109`。
[^rp-gates]: `platform/docs/add-a-skill.md:110-111`；纲领 P-14、P-22、P-27 见 `docs/architecture/README.md`。
[^rp-prose]: 用平台的 `framework.skills.library.load_skill` 加载 `skills/skills/prose-lint/` 实测，`yaml.safe_load` 报 mapping values are not allowed；其余 11 个 SKILL.md 加载通过，零 key 扫描均为 0 处，与三处库无重名。
[^rp-openalex]: 2026-10-02 不带 key 请求 `api.openalex.org`，读响应头 `x-ratelimit-limit`、`x-ratelimit-credits-used`、`x-ratelimit-limit-usd`。
