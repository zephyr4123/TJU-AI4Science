---
title: 科研 AI 能力选型：文献、假设、写作三个阶段
subtitle: 李瑞彬调研的 18 个开源项目，13 个做代码级深读并经独立复查，按 6 类能力横向比较
kind: 开源项目选型（代码级，只读不跑）
date: 2026-09-27
scope: 候选来自李瑞彬 2026-09 交回的调研原稿（6 类能力，每类 3 个项目）；选 13 个，克隆到外层 vendor/ 读源码，一个项目一篇深读，每篇由另一个会话照 文件:行 复查；本页放原稿、取舍、深读索引、横向比较与讨论前要弄清的问题
status: 第一版（2026-09-27）：代码读完，接不接、怎么接待讨论；实测未做
---

> **现状（2026-09-27）**：13 个项目的代码读完，每篇经过一轮独立复查；接不接、怎么接还没讨论，实测一条没做。
>
> 候选分两种做法。一种是写给宿主 agent 的说明加确定性脚本，自己不调模型：K-Dense、Academic Research Skills、Nature Skills、AI Research SKILLs 四个 skill 库，以及 arxiv-mcp-server、Paper Search MCP 两个检索服务。另一种自己调模型接口、要单独的 key：PaperQA2、GPT Researcher、STORM、AI Scientist、AutoResearchClaw、SciAgentsDiscovery、POPPER。平台现在是第一种：框架不调模型，读懂与写作由研究者登录的 Claude Code / Codex 会话做。
>
> README 与代码的差距普遍存在，各篇深读的第 1 节逐条列了。影响判断的几个例子：Academic Research Skills 的引用闸门库写好了，提示词里没有调用它的命令；AutoResearchClaw 的 Idea Workshop、分支、想法池零调用；Paper Search MCP 有 18 个源把请求失败吞成空结果；AI Scientist 一代的查新判定只看模型回复里的一句固定字符串。
>
> 研究组的 8 个都不能原样在平台现在的会话里用：skill 库原样放进来过不了平台的 skill 校验（Nature Skills 20 个里 14 个过不了 `load_skill`，已实测）；平台起会话时清空 MCP，两个检索服务加载不进来；PaperQA2 与 GPT Researcher 要平台现在没有的单独模型 key。这是现状，不是结论。三个阶段各缺什么、候选补哪一块，见[横向比较](#横向比较)；讨论前要先回答的共性问题见[下一节](#讨论前要弄清的问题)。

## 来源

李瑞彬（[分工方向 3](https://github.com/zephyr4123/TJU-AI4Science/blob/main/docs/meetings/2026-0923-division-of-labor.md#3-调研成熟的科研-ai-能力)）交回的调研：6 类能力、每类 3 个开源项目，共 18 个。6 类正好落在平台还没有步骤的三个阶段：论文阅读、文献检索、文献综述属于**文献**；研究创意、假设生成与评估属于**假设**；论文写作属于**写作**。

- 原稿：外层 `materials/research/2026-0927-scientific-ai-capabilities/AI4Science_科研AI能力调研.docx`（gitignore），sha256 `d39f82cf41418faab2038d224188836a10ab74134e3b08aa5c3f8ac142350479`
- 跟踪：主线 [#151](https://github.com/zephyr4123/TJU-AI4Science/issues/151)，下面一类能力一条 issue（#152–#157），一个项目一条 issue，再下面是分析、实测叶子

## 原稿

照录原稿的 6 张表，星数是原稿写的数。

**1. 论文阅读 / 论文理解**

| 顺序 | 项目 | GitHub 热度 | 与该能力的匹配点 | GitHub 地址 |
|---|---|---|---|---|
| 1 | GPT Academic | ≈71.4k | PDF/LaTeX 论文解读、总结、翻译、润色；科研场景插件丰富 | <https://github.com/binary-husky/gpt_academic> |
| 2 | ChatPaper | ≈19.8k | arXiv/本地论文总结、翻译、润色与审稿辅助 | <https://github.com/kaixindelele/ChatPaper> |
| 3 | PaperQA2 | ≈9.2k | 面向科学文献的高精度 RAG/问答，回答可绑定引用证据 | <https://github.com/Future-House/paper-qa> |

**2. 文献检索 / 资料搜索**

| 顺序 | 项目 | GitHub 热度 | 与该能力的匹配点 | GitHub 地址 |
|---|---|---|---|---|
| 1 | K-Dense Scientific Agent Skills | ≈46.6k | 含 Paper Lookup / Research Lookup，可连接多类学术数据库并整理检索证据 | <https://github.com/K-Dense-AI/scientific-agent-skills> |
| 2 | arxiv-mcp-server | ≈3.2k | 面向 arXiv 的论文搜索与本地管理；支持原始 LaTeX 分节读取、BibTeX 与主题监控 | <https://github.com/blazickjp/arxiv-mcp-server> |
| 3 | Paper Search MCP | ≈2.7k | 面向 arXiv、PubMed、bioRxiv、Semantic Scholar、OpenAlex 等多源论文搜索/下载/读取 | <https://github.com/openags/paper-search-mcp> |

**3. 文献综述 / 多论文综合**

| 顺序 | 项目 | GitHub 热度 | 与该能力的匹配点 | GitHub 地址 |
|---|---|---|---|---|
| 1 | STORM | ≈31.5k | 自动调研主题并生成带引用的长篇结构化报告/知识综述 | <https://github.com/stanford-oval/storm> |
| 2 | GPT Researcher | ≈29.6k | 多源深度检索、信息综合，并生成带引用的研究报告 | <https://github.com/assafelovic/gpt-researcher> |
| 3 | Local Deep Research | ≈9.1k | 本地/云模型深度调研；支持 arXiv、PubMed 等学术来源并生成引用报告 | <https://github.com/LearningCircuit/local-deep-research> |

**4. 研究创意 / 研究方向生成**

| 顺序 | 项目 | GitHub 热度 | 与该能力的匹配点 | GitHub 地址 |
|---|---|---|---|---|
| 1 | AI Scientist | ≈14.6k | 显式 research idea generation，并可结合 Semantic Scholar 做 novelty check | <https://github.com/SakanaAI/AI-Scientist> |
| 2 | AutoResearchClaw | ≈14.5k | Idea Workshop 支持假设共创、评估与细化，并支持并行研究方向探索 | <https://github.com/aiming-lab/AutoResearchClaw> |
| 3 | AI Scientist-v2 | ≈7.2k | 通过 Agentic Tree Search 扩展、搜索并迭代研究方向与方案 | <https://github.com/SakanaAI/AI-Scientist-v2> |

**5. 科学假设生成 / 假设评估**

| 顺序 | 项目 | GitHub 热度 | 与该能力的匹配点 | GitHub 地址 |
|---|---|---|---|---|
| 1 | SciAgentsDiscovery | ≈639 | 知识图谱 + 多 Agent 推理，输出 hypothesis、mechanism、novelty 等结构化科学假设 | <https://github.com/lamm-mit/SciAgentsDiscovery> |
| 2 | POPPER | ≈289 | 面向科学假设的自动验证/检验，使用 Agentic Sequential Falsifications 逐步证伪 | <https://github.com/snap-stanford/POPPER> |
| 3 | HypoGeniC / HypoRefine | ≈131 | 开放域科学假设生成；支持数据驱动以及“文献 + 数据”联合生成 | <https://github.com/ChicagoHAI/hypothesis-generation> |

**6. 科学论文写作**

| 顺序 | 项目 | GitHub 热度 | 与该能力的匹配点 | GitHub 地址 |
|---|---|---|---|---|
| 1 | Academic Research Skills | ≈49.4k | academic-paper 写作/审阅/修改工作流，覆盖 research → write → review → revise | <https://github.com/Imbad0202/academic-research-skills> |
| 2 | Nature Skills | ≈44.5k | nature-writing / nature-polishing：面向 Nature 风格稿件起草、重构与润色 | <https://github.com/Yuan1z0825/nature-skills> |
| 3 | AI Research SKILLs | ≈13.0k | 包含 ML Paper Writing 技能，覆盖论文起草、LaTeX 模板与研究写作流程 | <https://github.com/Orchestra-Research/AI-Research-SKILLs> |

## 取舍

18 个仓库先按 README、许可证与最近提交分三组（2026-09-27 查）。「研究」读代码回答是什么、怎么做、为什么，之后还要拿课题组的真材料实测；「只借鉴」只摘方法，不评估整体接入；「不研究」不开 issue。AI Scientist 两代合成一篇。

| 阶段 · 能力 | 研究 | 只借鉴 |
|---|---|---|
| 文献 · 论文阅读 | [PaperQA2](paperqa2.md) | |
| 文献 · 文献检索 | [K-Dense Scientific Agent Skills](k-dense-skills.md)、[arxiv-mcp-server](arxiv-mcp-server.md)、[Paper Search MCP](paper-search-mcp.md) | |
| 文献 · 文献综述 | [GPT Researcher](gpt-researcher.md) | [STORM](storm.md) |
| 假设 · 研究创意 | | [AI Scientist（一代与二代）](ai-scientist.md)、[AutoResearchClaw](autoresearchclaw.md) |
| 假设 · 假设生成与评估 | | [SciAgentsDiscovery](sciagents.md)、[POPPER](popper.md) |
| 写作 · 论文写作 | [Academic Research Skills](academic-research-skills.md)、[Nature Skills](nature-skills.md)、[AI Research SKILLs](ai-research-skills.md) | |

不研究的 4 个：

| 项目 | 原因 |
|---|---|
| GPT Academic | 给人用的网页工具，靠插件做 PDF / LaTeX 解读与翻译；GPL-3.0；平台的助理已能用 `pdf` skill 读论文 |
| ChatPaper | 2023 年风格的脚本集；许可证 CC BY-NC-ND 4.0，不允许修改 |
| Local Deep Research | 全本地部署（Docker、Ollama、SearXNG），本地模型要 GPU，和平台用云端 agent 的路线不合 |
| HypoGeniC / HypoRefine | 从带标签的文本数据集归纳假设，课题组的课题类型（PINN、参数估计这类）用不上 |

## 深读索引

每篇的提交号、读了什么、没读什么写在文首的 scope 里。一句话是复查之后的说法。

| 项目 | 深读 | 它实际是什么 | 项目 issue |
|---|---|---|---|
| PaperQA2 | [paperqa2.md](paperqa2.md) | Python 库加 `pqa` 命令行：给本机论文目录建索引，由自带的工具调用循环检索、逐块摘要打分（RCS），出带页码引用的答案；模型调用经 litellm，要 API key 或本地端点 | [#158](https://github.com/zephyr4123/TJU-AI4Science/issues/158) |
| K-Dense Scientific Agent Skills | [k-dense-skills.md](k-dense-skills.md) | 166 个 agentskills.io 格式的说明文档包（106 个带脚本）；仓库本身不调模型，由宿主 agent 读 SKILL.md、自己调接口与脚本；文献相关的四个 skill 做法各不相同 | [#161](https://github.com/zephyr4123/TJU-AI4Science/issues/161) |
| arxiv-mcp-server | [arxiv-mcp-server.md](arxiv-mcp-server.md) | 只做 arXiv 的本地 MCP 服务，19 个工具，全是确定性代码、不调模型；没有命令行形态，自带的 SKILL.md 离了 MCP 用不了 | [#164](https://github.com/zephyr4123/TJU-AI4Science/issues/164) |
| Paper Search MCP | [paper-search-mcp.md](paper-search-mcp.md) | 不调模型的 21 源学术检索、开放获取 PDF 兜底下载与 pypdf 抽文本，外面包 MCP、命令行、纯说明 skill 三层；18 个源出错时返回空结果 | [#167](https://github.com/zephyr4123/TJU-AI4Science/issues/167) |
| GPT Researcher | [gpt-researcher.md](gpt-researcher.md) | 自己调模型的固定研究流水线：拆子查询、并行检索抓取、BM25 挑段落、一次成文；三种外壳都不把推理交给宿主 agent，引用不校验 | [#170](https://github.com/zephyr4123/TJU-AI4Science/issues/170) |
| STORM | [storm.md](storm.md) | 多视角检索对话，先大纲、后逐节带引用写作；Co-STORM 加主持人、思维导图与人插话；经 dspy 自己调模型，论文里的几处设置与 main 上的代码对不上 | [#173](https://github.com/zephyr4123/TJU-AI4Science/issues/173) |
| AI Scientist（一代与二代） | [ai-scientist.md](ai-scientist.md) | 两代出想法都是带存档的 prompt 加同一段对话里的自我反思；一代查新的判定只看模型回复里的一句固定字符串，二代只剩一个可选的 Semantic Scholar 检索工具 | [#175](https://github.com/zephyr4123/TJU-AI4Science/issues/175) |
| AutoResearchClaw | [autoresearchclaw.md](autoresearchclaw.md) | 假设这一段真正接上的是三个角色各调一次再合成、跑完后的协作对话、执行前的意见文件与手动跳阶段；Idea Workshop、分支、想法池零调用 | [#177](https://github.com/zephyr4123/TJU-AI4Science/issues/177) |
| SciAgentsDiscovery | [sciagents.md](sciagents.md) | 在概念图上取一条带随机性的路径，只把路径字符串交给几个直连 gpt-4o 的角色写七字段假设，再用 Semantic Scholar 让模型自评新颖性 | [#179](https://github.com/zephyr4123/TJU-AI4Science/issues/179) |
| POPPER | [popper.md](popper.md) | 只验证、不生成假设：模型把假设拆成子假设并过滤相关性，ReAct agent 在数据表上跑检验，p 值转 e 值连乘，超过 1/α 判通过 | [#181](https://github.com/zephyr4123/TJU-AI4Science/issues/181) |
| Academic Research Skills | [academic-research-skills.md](academic-research-skills.md) | Claude Code 插件，主体是约 4.4 万行提示词、由会话模型执行；27 万行 Python 多是测试与钉住提示词的 lint；引用闸门与论断核对的库写好了，提示词里没有调用它们的命令 | [#183](https://github.com/zephyr4123/TJU-AI4Science/issues/183) |
| Nature Skills | [nature-skills.md](nature-skills.md) | agentskills.io 格式的 20 目录提示词库，自己不调文本模型；代码集中在绘图、转 PPT、下载、检索等六个目录；原样放进平台，20 个里有 14 个过不了 `load_skill`（已实测） | [#186](https://github.com/zephyr4123/TJU-AI4Science/issues/186) |
| AI Research SKILLs | [ai-research-skills.md](ai-research-skills.md) | Markdown skill 库，深读的四个 skill（写作两个、出想法两个）都没有脚本；按平台现有规则原样放进来，会在 frontmatter、正文行数、执行层白名单、读文件范围与单独模型 key 几处出问题 | [#189](https://github.com/zephyr4123/TJU-AI4Science/issues/189) |

## 横向比较

一类能力一节。每节读的是已复查的深读，有的候选主体挂在别的能力下，只比和这一类相关的部分。每节末尾的问题是这一类特有的，几类共有的问题收在下一节。

### 论文阅读（文献阶段）

范围：本类的主体候选是 PaperQA2（#158）；arxiv-mcp-server（#164）、Paper Search MCP（#167）、Nature Skills（#186）的主体挂在别的能力下，这里只比和读论文相关的部分。Nature Skills 里和本类相关的是 `nature-reader` 与 `nature-paper-card` 两个 skill，分两行列。深读之外，另回 `vendor/nature-skills`（提交 9e2d90e）核对了这两个 skill 的脚本；平台一侧对照的是内仓 de3d948。

| 候选 | 实际做到什么 | 做法 | 调模型与 key | 外部服务 | 成熟度 | 许可证 | 出处 |
|---|---|---|---|---|---|---|---|
| PaperQA2（#158） | 对本机一个目录里的一批论文做带引用的问答：建 tantivy 索引并给每块算嵌入，在工具调用循环里搜论文、逐块让模型写摘要并打分（RCS），再取高分证据生成答案；句末的 `pqac-` 键事后换成「作者年份 pages a-b」，并生成参考列表，本次证据里没有的键直接删掉。机器只查键存在，不查句子是否被那条证据支持；存盘与返回的答案里证据原文已被清掉，只留摘要与块名。不产单篇笔记。论文里用的检索服务、Grobid、引用遍历和 LitQA2 评测都不在仓里 | Python 库加 `pqa` 命令行，自带智能体循环；PDF 按页拼接后切成定长块（默认 pypdf，装了 `paper-qa-pymupdf` 就改用 PyMuPDF），引用粒度是块，也就是页码区间 | 自己经 litellm 调模型：llm、summary_llm、agent_llm、enrichment_llm、embedding 五个槽默认都是 OpenAI（gpt-4o-2024-11-20、text-embedding-3-small），要 `OPENAI_API_KEY`；换 Anthropic 要改四个 LLM 槽，嵌入另找一家，或用本地 `st-` / `sparse`；用不了 Claude Code / Codex 的命令行登录 | 模型接口；默认调 Crossref、Semantic Scholar 补元数据（key 可选，`use_doc_details=False` 可关）；索引与答案写在 `~/.pqa` | 9,251 star；237 个测试函数，CI 带真 key 调接口；CalVer 版本号，最近 v2026.08.12，README 明说不保证版本间兼容；main 在 2026-04 到 09 月只有 4 个提交 | Apache-2.0；可选的 `paper-qa-pymupdf` 是 AGPL-3.0，装上就成为默认解析器 | [paperqa2.md](paperqa2.md)、[回答与引用绑定](paperqa2.md#25-回答与引用绑定)、[怎么调模型](paperqa2.md#27-怎么调模型)、[数据进出](paperqa2.md#28-数据进出与落盘)、[论文与仓的差别](paperqa2.md#12-论文里的系统与仓里的系统)、[成熟度](paperqa2.md#6-成熟度) |
| arxiv-mcp-server（#164，只比读论文部分） | 只处理 arXiv 论文：`download_paper` 先取 HTML（抽出的是按行拼接的纯文本，不是 markdown），取不到再走 PDF（pymupdf4llm 0.2.9，按代码推断不走版面模式），结果缓存到本地；`read_paper` 默认每页 12,000 字符，带续读游标；另有取大纲、按节读，以及返回字符偏移与所在节的子串检索；三个 LaTeX 工具把 e-print 源码按 `\section` 三级切开、按节返回原文，失败时不会自动退回 PDF。它不产笔记、问答或摘要，7 个 MCP prompt 只是固定文字，读懂由客户端 agent 做 | 本地 MCP 服务，19 个工具，没有命令行；自带的 SKILL.md 共 26 行，前提是 MCP 已接上 | 不调模型，不要 key；`[pro]` 只带一个本地句向量模型，给摘要做语义检索 | arxiv.org（html / pdf / e-print）、export.arxiv.org；缓存默认在 `~/.arxiv-mcp-server/papers`，一个服务进程只用一个目录 | 3,175 star；389 个测试，网络一律 mock；CI 覆盖 3 个操作系统 × 3 个 Python 版本；PyPI 最新 0.7.2（2026-08-24）；单人维护（217 个提交里作者占 193 个），2026-08-26 之后没有提交 | Apache-2.0；`[pdf]` 锁定的版本里，pymupdf、pymupdf4llm 是 AGPL-3.0 或商业许可，pymupdf-layout 1.27.1 是 PolyForm Noncommercial 或商业许可 | [arxiv-mcp-server.md](arxiv-mcp-server.md)、[按节读 LaTeX](arxiv-mcp-server.md#25-按节读-latex-原文)、[模型与形态](arxiv-mcp-server.md#210-有没有模型调用除了-mcp-还有什么形态)、[存盘目录](arxiv-mcp-server.md#29-存盘目录)、[跑起来要什么](arxiv-mcp-server.md#4-跑起来要什么)、[和平台对照](arxiv-mcp-server.md#5-和平台对照) |
| Paper Search MCP（#167，只比读论文部分） | 读论文只有各源的 `read_*` 工具（命令行是 `paper-search read`）：下载 PDF 后用 pypdf 的 `extract_text()` 逐页拼接，没有 OCR，也不处理版面、公式和表格；CORE 先返回接口给的全文，CiteSeerX 有摘要就只返回摘要；多数源每次读都重新下载；没有锚点、笔记或问答。它的主体是 21 个源的检索加下载兜底链，归别的能力比 | MCP 服务（57 个工具）、`paper-search` 命令行（4 个子命令），外加一份没有脚本的 SKILL.md | 不调模型；只有数据源的可选 key，没有模型 key | 各数据源站点（读的时候重新下 PDF）；PDF 写到 `save_path`，MCP 下缺省是 `./downloads` | 2,706 star；219 个测试，多数直接打真接口，离线时被跳过；CI 只在打 tag 时跑 7 个测试文件；PyPI 上的 0.1.4 比 main 落后 39 个提交，且对 `mcp` 不设上限，按 #107 推断这样装出的 MCP 服务一导入就崩（命令行不受影响，未实跑） | MIT | [paper-search-mcp.md](paper-search-mcp.md)、[README 说了、代码里薄的](paper-search-mcp.md#15-readme-说了代码里没有或很薄)、[下载与读](paper-search-mcp.md#23-下载与读)、[怎么调模型](paper-search-mcp.md#24-怎么调模型)、[成熟度](paper-search-mcp.md#6-成熟度) |
| Nature Skills · `nature-reader`（#186） | 一套写给宿主 agent 的提示词规程：把一篇论文做成中英逐段对照的 `paper.md`，另写 `source_map.json`，正文、图注、图、表、公式分别编 S / C / F / T / E 块 ID，每块记页码；追问时要求注明「页码 + 块 ID」，原文不支持的就答「原文未明确说明」。抽取、翻译、建 source map 都由 agent 做，第一步写的是「先 load `pdf` skill」，这个 skill 不在仓里，按原文要能给 OCR 指导。仓里的代码只有 `validate_reader_math.py`（458 行），只核对公式定界符和公式块（E）的锚点与页码，不查正文块；没有会执行提示词、比较输出的测试 | agentskills.io 格式的 router：SKILL.md 加 `manifest.yaml` 加 `static/` 片段，要 agent 按相对路径去读，还引用 `../nature-shared/` | 仓里不调文本模型；文本由宿主 agent 在自己的会话里写，不带 key | 脚本不联网；输入是 DOI 或 arXiv 时由 agent 自己取原文 | README 标 Beta；仓库级情况见下一行 | Apache-2.0（仓库根） | [nature-skills.md](nature-skills.md)、[文献与假设相关的几个](nature-skills.md#25-文献与假设阶段相关的几个)、[数据怎么进出](nature-skills.md#23-数据怎么进出)、`vendor/nature-skills/skills/nature-reader/static/core/workflow.md:19-29`、`vendor/nature-skills/skills/nature-reader/references/grounding-rules.md:5-11`、`vendor/nature-skills/skills/nature-reader/scripts/validate_reader_math.py:269-338` |
| Nature Skills · `nature-paper-card`（#186） | 一篇论文出一张固定 16 节的精读卡 `paper-card.md`（方法、主张与证据矩阵、局限；第 16 节的研究想法要过六道门）。`prepare_paper.py`（490 行）用 PyMuPDF 逐页取纯文本，写出 `source_bundle.json`（PDF 页号、印刷页码、页文本、按常见节名认出的标题、图表公式清单、sha256），也能直接读 nature-reader 的 source map。按能不能拿到可靠页码分 page-grounded / structure-grounded / source-limited 三种定位模式，拿不到就不许写页码。`audit_paper_card.py`（415 行）查的是：16 节齐全且有序、有 `[Paper: …]` 指针、page-grounded 模式下页码写成「PDF p.」、清单里每个图表公式都在卡里被提到；不查所指页码是否存在，也不查内容是否支持那句话。卡的正文由宿主 agent 写，SKILL 禁止 agent 临时写抽取脚本 | router 加两个随包脚本；agent 按 `SKILL_DIR` 解析脚本路径，直接用 `python` 跑 | 同上：不调模型，不带 key | 脚本不联网；第 04、15 节和查新由 agent 自己做外部检索 | README 标 Beta；paper-card 有 7 个测试，但 main 上的 skill 工具 CI 从 2026-09-16 起一直红，这一步被跳过没跑；仓库 44,699 star，0 个 release、0 个 tag；reader 与 paper-card 的脚本都缺 PEP 723 块和锁，原样放进平台 `skills/` 过不了 `load_skill` | Apache-2.0（仓库根）；`prepare_paper.py` 要 PyMuPDF（PyPI 上标 AGPL-3.0 或商业许可），目录里没有声明这个依赖 | [nature-skills.md](nature-skills.md)、[接进来会碰到的平台规则](nature-skills.md#54-接进来会碰到的平台规则)、[成熟度](nature-skills.md#6-成熟度)、[许可证](nature-skills.md#64-许可证)、`vendor/nature-skills/skills/nature-paper-card/SKILL.md:35-58`、`vendor/nature-skills/skills/nature-paper-card/scripts/prepare_paper.py:150-201`、`vendor/nature-skills/skills/nature-paper-card/scripts/audit_paper_card.py:164-259` |

**平台缺的与候选补的**

平台现状：文献阶段没有步骤能力，主文件 `sources.md` 由助理手写，写法不限（`docs/architecture/README.md:151`、`docs/architecture/README.md:170`）。`pdf` skill 只做解析：`structured.json` 里的节、表、图、公式带页码，`paper.md` 的正文段落既没有页码也没有段落编号（`platform/skills/pdf/SKILL.md:42-44`、`platform/skills/pdf/scripts/extract.py:110`；另抽查了外层 `materials/` 里的一份产物，正文里没有分页标记）。对照 #152 的目标「笔记与问答，结论能追到原文的段落」，平台缺四样：正文段落级的锚点、带指针的笔记或问答格式、对指针的机器核对、对一批论文的检索问答。

各候选补的是哪一块：多篇问答，以及页码区间级的引用绑定，只有 PaperQA2 有；代价是它自己调模型、要单独的模型 key，自带一套解析与存放（`~/.pqa`），而且它自己有一个选工具的循环，平台两层 agent 也各有一个（[paperqa2.md](paperqa2.md#5-和平台对照)）。笔记格式和块级锚点由 nature-reader（页码 + 块 ID，只靠提示词约束）与 nature-paper-card（16 节卡 + 页级指针，审计脚本查格式与覆盖）给出，它们的分工和平台现在一样，都是由宿主 agent 读懂。arxiv-mcp-server 补的是 arXiv 论文的分页读、按节读和 LaTeX 原文，不产笔记。Paper Search MCP 的读只是 pypdf 纯文本，比平台的 `pdf` 粗，不补这一块。四个候选都不产 `sources.md`；也都不核对「所引原文是否支持这句话」：PaperQA2 只查键存在，paper-card 只查指针格式与图表覆盖，nature-reader 的脚本只查公式。

和平台现有东西的重叠：PDF 解析五个项目各有一套。平台 `pdf` 用 pymupdf4llm 1.28.2 版面模式；PaperQA2 默认 pypdf，可选 PyMuPDF 或 Docling；arxiv-mcp-server 抽 arXiv HTML，PDF 兜底用 pymupdf4llm 0.2.9；paper-card 的 `prepare_paper.py` 用 PyMuPDF 逐页取纯文本；Paper Search MCP 用 pypdf。nature-reader 自己不解析，要一个外部的 `pdf` skill，名字和平台的相同，但它要的 OCR 指导平台的 `pdf` 没有；它产出的 `paper.md` 也和平台 `pdf` 的 `paper.md` 同名、内容不同（P-13 要求一个名字只有一个生产者，`docs/architecture/README.md:163`）。形态上：arxiv-mcp-server 只有 MCP；PaperQA2 与 Paper Search MCP 有命令行，但不是 PEP 723 脚本；nature-skills 的脚本缺 PEP 723 块与锁。平台两家适配器起会话时都清空 MCP，执行层只放行 `ai4sci skill`（`docs/architecture/README.md:164`、`docs/architecture/README.md:172`；[arxiv-mcp-server.md](arxiv-mcp-server.md#5-和平台对照)、[paper-search-mcp.md](paper-search-mcp.md#5-和平台对照)）。

**讨论前要弄清的问题**

1. 这一类的产物到底是哪一种：单篇精读卡、中英对照全文，还是对一批论文的问答？三者对应的候选不同：PaperQA2 只做问答，nature-reader 做对照全文，nature-paper-card 做单篇卡。
2. 「追到原文的段落」要到什么粒度：页码区间（PaperQA2 的块）、页码加块 ID（nature-reader）、节加字符偏移（arxiv-mcp-server 的大纲工具），还是平台 `pdf` 现在的节与页？
3. 平台 `pdf` 的 `paper.md` 要不要给正文加页码或段落锚点？现在只有 `structured.json` 的节、表、图、公式带页码，而 nature-reader 与 paper-card 的指针都要页码。
4. 要不要机器核对引用指针、卡到哪一步？四个候选都不查「这句话是否被所指原文支持」；P-7 fail-closed（`docs/architecture/README.md:157`）落到读论文的笔记上意味着什么？
5. 笔记和问答写进哪个文件？文献阶段主文件是 `sources.md`（P-20），四个候选都不产它。笔记是 `sources.md` 的一部分、能力的私有文件，还是另定名字？nature-reader 的 `paper.md` 与平台 `pdf` 的 `paper.md` 同名，这个冲突怎么处理？
6. 「宿主 agent 读」和「工具自己调模型读」两种做法，在 P-1、P-25 下分别意味着什么？PaperQA2 要 litellm 能用的 API key 或本地端点，用不了 Claude Code / Codex 登录，默认全走 OpenAI，而 Anthropic 没有嵌入模型；P-1 的判据只覆盖 `framework/`，纲领没写 skill 脚本能不能自己调模型；要不要引入单独的模型 key，目前待定。
7. 一次读多少篇、读什么语言？批量问答需要索引（PaperQA2 的 tantivy 加嵌入，存在 `~/.pqa`，在项目目录之外），单篇读不需要；PaperQA2 没有中文论文的测试，nature-reader 的输出面向中文读者。课题组的实际需要是什么？
8. 解析层在真论文上差多少？平台 `pdf`、paper-card 的 PyMuPDF 逐页文本、arxiv-mcp-server 的 HTML 抽取、PaperQA2 与 Paper Search MCP 的 pypdf，还没有在同一批课题组论文上比过（外层 #160、#166 的实测还开着）。
9. MCP 形态怎么对待？arxiv-mcp-server 只有 MCP，在平台现有会话里加载不进来（两家适配器清空 MCP，P-14 只放行 `ai4sci`）；这一类要不要接 MCP 是待定的问题，还是只看能改写成 PEP 723 skill 脚本的部分？
10. nature-reader 与 nature-paper-card 放进平台要改多少？脚本缺 PEP 723 块与锁，PyMuPDF 没声明；router 要 agent 读 `manifest.yaml`、`static/` 和 `../nature-shared/`，而 `ai4sci skill show` 不给这些文件；执行层能不能读到 skill 目录，还没实测。
11. 各候选失败后继续跑的地方（PaperQA2 的元数据失败只打 warning、单篇解析失败就跳过；arxiv-mcp-server 的 HTML 非 200 静默转 PDF）和 P-7 冲突多少，要不要逐条对？
12. 许可证立场：平台 `pdf` 已经锁了 AGPL-3.0 或商业许可的 PyMuPDF 系列，paper-card 也用 PyMuPDF，PaperQA2 可选的 `paper-qa-pymupdf` 是 AGPL，arxiv-mcp-server `[pdf]` 锁定的 pymupdf-layout 1.27.1 是 PolyForm Noncommercial。平台对这几类许可证怎么看，还没写。
13. 维护风险：PaperQA2 的 main 在 2026-04 之后只有 4 个提交；arxiv-mcp-server 单人维护，08-26 之后没有提交；nature-skills 没有发过版，skill 工具测试从 09-16 起在 main 上一直红；Paper Search MCP 的 PyPI 版落后 main 39 个提交。用哪一个的代码，是不是就意味着要自己维护一份？
14. 成本：PaperQA2 论文报每次查询 1–3 美元，仓里默认配置的费用没测；宿主 agent 读的做法走研究者的订阅，成本记 NaN（P-25）。两种做法的实际花费没有比过。

### 文献检索（文献阶段）

对应 issue #153。比较范围是 #153 列的三个候选（K-Dense #161、arxiv-mcp-server #164、Paper Search MCP #167），另加 PaperQA2（#158）与 GPT Researcher（#170）里和「按题目找论文、拿元数据、全文与 BibTeX」有关的部分，这两个的主体挂在别的能力下。K-Dense 的几个文献 skill 做法差别很大，拆成两行。「实际做到什么」一列以深读为准，按检索、元数据、全文、BibTeX 四步写。K-Dense 的 literature-review 也和文献综述（#154）有关。

| 候选 | 实际做到什么 | 做法 | 调模型与 key | 外部服务 | 成熟度 | 许可证 | 出处 |
|---|---|---|---|---|---|---|---|
| arxiv-mcp-server | 只管 arXiv，四步都做了。检索：Atom API，支持分类与日期过滤、分页、返回总数。元数据：只取 arXiv 自己的字段，Atom 里现成的 DOI、journal_ref 没解析。全文：优先取 HTML，产出按行拼的纯文本，不是 markdown；没装 `[pdf]` 时 HTML 拿不到就报错；另可按 `\section` 三级读 LaTeX 原文，LaTeX 读不到时不会自动退回 PDF。BibTeX：一律 `@misc`，year 取 v1 的提交日期。此外还有 S2 一跳引用图、拉取式主题订阅 | 本地 MCP 服务，19 个工具，全是确定性代码；正文默认 12,000 字符一页，带续读游标；进程内一把 3 秒一次的 arXiv 限流闸。没有命令行，入口只起服务；自带的 SKILL.md 只有 26 行，内容依赖 MCP 工具 | 不调模型（`src/` 里 grep 不到模型接口）；不要任何 key，`SEMANTIC_SCHOLAR_API_KEY` 可选；`[pro]` 第一次运行时从 Hugging Face 拉本地句向量模型 | export.arxiv.org；arxiv.org（html、pdf、e-print）；api.semanticscholar.org；`[pro]` 另加 huggingface.co | 389 个测试函数；CI 是 3 个操作系统 × 3 个 Python 版本，网络只在 mock 里测，`[pdf]` `[pro]` 不装也不测；同时发 PyPI 和官方 MCP Registry；217 个提交里作者占 193 个，最后一次提交 2026-08-26；`mcp` 钉在 `<2`；3175 star | Apache-2.0。`[pdf]` 锁定的 pymupdf、pymupdf4llm 是 AGPL-3.0 或商业许可，pymupdf-layout 1.27.1 是 PolyForm Noncommercial 或商业许可 | [arxiv-mcp-server.md](arxiv-mcp-server.md)、[§1.2](arxiv-mcp-server.md#12-readme-与代码逐条对账)、[§2.5](arxiv-mcp-server.md#25-按节读-latex-原文)、[§2.6](arxiv-mcp-server.md#26-bibtex)、[§4](arxiv-mcp-server.md#4-跑起来要什么)、[§6](arxiv-mcp-server.md#6-成熟度) |
| Paper Search MCP | 检索与元数据：21 个源都有连接器，统一检索缺省把 21 个源全打一遍，按小写 DOI 去重（先到先得，不合并字段）。其中 bioRxiv、medRxiv 把关键词当分类名，Unpaywall 只认 DOI，BASE 是收割后在本地过滤，真正由服务端按关键词检索的是 17 个。21 个源里有 18 个把请求失败吞掉，返回「0 条」。全文：按源下载 PDF，用 pypdf `extract_text()` 抽纯文本。按 DOI 找开放获取 PDF 有一条兜底链（OpenAIRE / CORE / Europe PMC / PMC → Unpaywall → 可选 Sci-Hub），第 2、3 环查 `%PDF-` 文件头并核对前三页的身份，只在 MCP 形态里有；第 1 环（源自带下载）什么都不查。BibTeX：没有 | 不调模型的工具库，外面包了三层：MCP 服务（57 个工具）；`paper-search` 命令行（4 个子命令，没有兜底链和 Sci-Hub）；一份只有说明、没有脚本的 Claude Code skill，教 agent 直接运行全局安装的 `paper-search` | 不调模型；没有必须配的 key；可选的都是数据源 key（S2、OpenAlex、CORE、DOAJ、Zenodo、OpenAIRE、CiteSeerX）；Unpaywall 要配 email；Google Scholar 可配代理 | 21 个源的站点，其中 Google Scholar、IACR、SSRN 靠抓 HTML；可选 Sci-Hub 镜像（`download_scihub` 在 MCP 里无条件注册，没有开关） | 219 个测试函数，多数直接打真接口，离线时跳过；CI 只在推 tag 时跑 7 个测试文件，不跑 lint；main 比 PyPI 0.1.4 多 39 个提交（0.1.4 没有身份校验、Sci-Hub 缺省开、`mcp` 没有版本上限）；87 个提交里一人占 51 个；CiteSeerX 的下载缺 `import os`，一走到就抛错；2706 star | MIT。Sci-Hub 的风险 README 自己标了「用户自负」；Google Scholar、SSRN 的抓取是否符合站点条款，深读没有评估 | [paper-search-mcp.md](paper-search-mcp.md)、[§1.1](paper-search-mcp.md#11-源清单)、[§1.2](paper-search-mcp.md#12-统一与去重)、[§1.3](paper-search-mcp.md#13-下载兜底链与-sci-hub)、[§1.4](paper-search-mcp.md#14-三种形态)、[§6](paper-search-mcp.md#6-成熟度)；「没有 BibTeX」：`grep -rli bibtex vendor/paper-search-mcp` 无结果 |
| K-Dense · paper-lookup、citation-management | paper-lookup 是 18 个学术接口的调用手册（端点、参数、限流；其中 12 份写了「HTTP 200 里藏着的失败」），加 4 个只用标准库的脚本。自己联网的脚本只有 `paginate.py`：负责 5 个接口的翻页（bioRxiv / medRxiv、Europe PMC、OpenAlex、Crossref），按接口报的总数对账，少了退出码 4。另外 3 个脚本只解析 agent 用 `curl` 取回的原始响应：JATS 全文分节、arXiv Atom、OpenAlex 摘要重建。其余 13 家靠 agent 照手册自己 `curl`；结果写在对话里，没有固定文件。citation-management 是这一组里唯一把检索写成代码的：PubMed、OpenAlex、Google Scholar 检索，取元数据，按 doi.org 内容协商取 BibTeX；校验只查 DOI 能否解析和格式，不比对标题作者 | agentskills.io 格式的说明文档包。宿主 agent 读 `SKILL.md`，在自己的 shell 里 `curl`、跑 `python3 scripts/x.py`，主流程是 `curl … \| python3 scripts/x.py -` | 不调模型。paper-lookup 的脚本只读 `OPENALEX_API_KEY`、`OPENALEX_EMAIL`、`CROSSREF_MAILTO`，都可选；`NCBI_API_KEY`、`S2_API_KEY`、`CORE_API_KEY`（取 CORE 全文时必需）由 agent 拼 `curl` 时自己带。citation-management 读 `NCBI_API_KEY`、`NCBI_EMAIL`、`OPENALEX_EMAIL` | paper-lookup：18 个公开学术接口。citation-management 另加 doi.org、DataCite、Google Scholar（经 `scholarly` 库，可选免费公共代理） | 整个仓库有 166 个 skill。CI 只跑依赖为空的 20 个 skill 的测试，paper-lookup 在里面，citation-management 不在；规范校验和测试这两道 CI 是 2026-07 下旬才加的；11 个月出了 106 个自动 release；第一作者占 44% 的提交；K-Dense 的论文写明没有任务级评测；46,743 star | 这两个 skill 是 MIT。同一个仓里 `pdf` `docx` `pptx` `xlsx` 四个 skill 是 Anthropic 专有条款，另有非商用许可的 skill | [k-dense-skills.md](k-dense-skills.md)、[§1.3](k-dense-skills.md#13-文献相关-skill-逐条对账)、[§2.2](k-dense-skills.md#22-paper-lookup)、[§2.5](k-dense-skills.md#25-database-lookup-与-citation-management)、[§6](k-dense-skills.md#6-成熟度)、[§6.4](k-dense-skills.md#64-许可证条款要点) |
| K-Dense · research-lookup、literature-review | research-lookup 的脚本不直连学术库。缺省调 `parallel-cli search`，把结果限定在 25 个学术域名里，不够 60 条再补一次不限域名的搜索；然后用 `parallel-cli extract` 抓页面，写出十个文件的 packet（含 `references.bib`）。所谓「已核实」包括「用正则找到一个 DOI 或 PMID」；证据矩阵、冲突、研究空白都是关键词启发式。literature-review 的检索也走 `parallel-cli`；自带的 `search_databases.py` 不联网，只做去重排序、输出 markdown / BibTeX；`verify_citations.py` 只查 DOI 能否解析，失败也退出码 0；`SKILL.md` 要求每篇综述至少一张经 OpenRouter 生成的图 | 同样是 skill 包，但脚本调第三方检索服务和生成服务；research-lookup 的 research、chat、perplexity 三个后端返回的是服务端生成的综合文本 | 缺省路径就要 Parallel 账号（`parallel-cli` 登录或 `PARALLEL_API_KEY`）。`OPENROUTER_API_KEY` 可选；没装 `parallel-cli` 但环境里有这把 key 时，普通查询会被自动路由到 Perplexity（读代码推断）。literature-review 生成配图要 `OPENROUTER_API_KEY`。这些都是研究者 agent 登录之外的凭据 | api.parallel.ai（经 `parallel-cli`）、openrouter.ai；literature-review 另有 doi.org、api.crossref.org，出 PDF 要 pandoc + xelatex | 两个 skill 的测试都不在 CI 那 20 个里。research-lookup 的测试把 `parallel-cli` 和 `requests.post` 模拟掉了；`verify_citations.py` 没有测试。按平台的 ruff 规则扫，literature-review 206 条、research-lookup 10 条 | MIT（同一个仓库） | [k-dense-skills.md](k-dense-skills.md)、[§2.3](k-dense-skills.md#23-research-lookup)、[§2.4](k-dense-skills.md#24-literature-review)、[§5.3](k-dense-skills.md#53-接进来会碰到平台哪些现有规则) |
| PaperQA2（只比相关部分） | 不做联网找论文。智能体的 `paper_search` 只查本机一个目录建出来的 tantivy 索引；论文里用 Semantic Scholar 拿候选和做引用遍历的工具不在开源仓里（论文 §8.1 自己写明）。和本类相关的是元数据补全：对本地每篇论文，先让 llm 从前 3 页写引文、抽标题与 DOI，再查 Crossref、Semantic Scholar 和期刊分级表；OpenAlex、Unpaywall、撤稿检查不在默认路径上。每篇的 `DocDetails` 带一个 bibtex 字段，从 S2 或 Crossref 取，缺了自己拼。contrib 里的 OpenReview、Zotero 两个辅助类能把 PDF 下到论文目录，不在 `pqa` 命令里 | Python 库加 `pqa` 命令行；索引、答案库、设置默认写在 `~/.pqa` | 自己经 litellm 调模型。四个 LLM 槽和嵌入默认都是 OpenAI（`OPENAI_API_KEY`）；换 Anthropic 要改四个槽，嵌入得另找一家或用本地模型；用不了 Claude Code / Codex 的命令行登录。Crossref、S2 的 key 可选 | 模型接口；缺省访问 api.crossref.org、api.semanticscholar.org（`use_doc_details=False` 可以关掉）；可选 OpenAlex、Unpaywall、Crossref Labs、clinicaltrials.gov | 237 个测试函数，CI 里带真 key 调多家模型；用 CalVer，明说不承诺版本间兼容；2026-04 以后 main 只有 4 个提交；9,251 star | Apache-2.0；可选的 `paper-qa-pymupdf` 是 AGPL-3.0，装上后就成为默认的 PDF 解析器 | [paperqa2.md](paperqa2.md)、[§1.2](paperqa2.md#12-论文里的系统与仓里的系统)、[§2.6](paperqa2.md#26-元数据来源)、[§2.7](paperqa2.md#27-怎么调模型)、[§6](paperqa2.md#6-成熟度)；bibtex 字段：`vendor/paper-qa/src/paperqa/types.py:815,1037-1135`、`vendor/paper-qa/src/paperqa/clients/semantic_scholar.py:162-185` |
| GPT Researcher（只比相关部分） | 有 arXiv、Semantic Scholar、OpenAlex、PubMed Central 四个学术检索器，都只返回 `{title, href, body}`，作者、年份、DOI 全部丢掉。在标准研究的路径里：arXiv 只拿到「日期 + 作者 + 摘要」，不下 PDF；S2 只留开放获取的论文，代码不带 key（深读时本机无 key 请求三次都是 429）；OpenAlex 的摘要被丢掉、只抓链接，付费墙论文抓到的是出版社落地页；PMC 直接给全文。抓到的 PDF 用 PyMuPDF 取纯文本，截到前 5 万字符。没有 BibTeX，没有 DOI。`quick_search()` 零次模型调用，原样返回检索器的结果 | Python 库。标准研究是一条固定流水线：1 次模型调用选角色，1 次拆成 3 条子查询；子查询加原问题共 4 条并行检索、抓取，用 BM25 挑段落；最后 1 次调用写报告。引用靠提示词要求模型写 URL 超链接，运行时不核对。三种外壳：Claude skill 是一份开发说明书；Codex 插件的 `uvx gpt-researcher` 入口在 wheel 里不存在；gptr-mcp 启动时要 `OPENAI_API_KEY` | 自己经 LangChain 调模型；默认要 `OPENAI_API_KEY` 加 `TAVILY_API_KEY`；四个学术检索器不要 key；只认各家 API 的凭据，不认命令行登录 | 模型 API；搜索 API（默认 Tavily，商业服务）；被抓取的网站；四个学术接口；tiktoken 第一次用时联网下载编码表 | 近 12 个月 468 个提交、93 位作者；测试 2026-08 才进 CI；PyPI 0.16.0 在 Python 3.12 / 3.13 上一 import 就报错，挂了 70 天；默认的 BM25 段落筛选 2026-09-26 才进代码；2026-07-14 一天关了 110 个 issue；29.6k star | `LICENSE` 是 Apache-2.0，但包元数据和维护者都说是 MIT；硬依赖 PyMuPDF 是 AGPL-3.0 或商业许可 | [gpt-researcher.md](gpt-researcher.md)、[§2.4](gpt-researcher.md#24-检索器与学术源)、[§2.5](gpt-researcher.md#25-引用怎么进报告)、[§2.6](gpt-researcher.md#26-怎么调模型)、[§2.7](gpt-researcher.md#27-三种外壳)、[§6](gpt-researcher.md#6-成熟度) |

**平台缺的与候选补的**
#153 给这一类定的范围是四步：按题目检索、拿元数据、拿全文、出 BibTeX。平台现在各步的情况如下：

- 文献阶段没有步骤能力，`sources.md` 由助理手写（`platform/framework/capabilities/__init__.py:45-47`）。
- 检索靠两层 CLI 自带的网页搜索：Claude Code 是 WebSearch / WebFetch，Codex 是 `web_search="live"`（`platform/backends/claude_code.py:42`、`platform/backends/codex.py:114`）。拿回来的是网页，不是带 DOI、作者、日期的结构化条目。
- 元数据只能靠 `pdf` skill 从单篇 PDF 里抽题目、作者、年份、DOI（`platform/skills/pdf/SKILL.md:3`）。
- 全文靠 `pdf` skill（输入是本地文件或链接）和 `download file`（输入是直链）。「给一个 DOI，找到开放获取 PDF」这一步没有。
- BibTeX 没有。

所以缺的是三块：结构化的学术库检索、按 DOI 找开放获取 PDF、BibTeX。各候选补到哪一块：

- **结构化检索**：Paper Search MCP 覆盖 21 个源并按 DOI 去重；arxiv-mcp-server 只覆盖 arXiv；K-Dense 的 paper-lookup 提供接口手册，并对 5 个接口做翻页和条数对账，citation-management 有 PubMed、OpenAlex、Google Scholar 三个检索脚本；GPT Researcher 有四个学术检索器，但书目字段被丢掉了；PaperQA2 不做联网检索（[paperqa2.md §1.2](paperqa2.md#12-论文里的系统与仓里的系统)）。
- **按 DOI 找开放获取 PDF**：写成代码的只有 Paper Search MCP 的兜底链，而且只在 MCP 形态里有（[paper-search-mcp.md §1.4](paper-search-mcp.md#14-三种形态)）；K-Dense paper-lookup 只有 Unpaywall、CORE 的手册，要 agent 自己 `curl`。
- **BibTeX**：arxiv-mcp-server 能出，但只有 `@misc`、只用 arXiv 元数据；K-Dense citation-management 用 doi.org 内容协商取；research-lookup 输出 `references.bib`；PaperQA2 的 bibtex 字段只针对本地已建索引的论文；Paper Search MCP 和 GPT Researcher 没有。

和平台现有东西的重叠：

- **检索**：所有候选都和 CLI 自带的网页搜索重叠，只是返回的形状不同。
- **PDF 转文本**：和 `pdf` skill 重叠。arxiv-mcp-server 的 PDF 兜底用的是同一个库 pymupdf4llm，但它锁 0.2.9，按代码看走非版面模式；平台锁 1.28.2，走版面模式（[arxiv-mcp-server.md §4](arxiv-mcp-server.md#4-跑起来要什么)）。Paper Search MCP 用 pypdf，GPT Researcher 用 PyMuPDF 纯文本。K-Dense 自带一个同名的 `pdf` skill（Anthropic 专有许可），而 P-22 不许重名。
- **下载**：和 `download` skill 重叠。Paper Search MCP 按源下载 PDF，写到 `./downloads` 或 `-o` 指定的目录；`download file` 按直链下载，带 sha256 校验和收据（[paper-search-mcp.md §5.3](paper-search-mcp.md#53-接进来会碰到的平台规则)）。
- **存放位置**：候选缺省写到 `~/.arxiv-mcp-server/papers`、`./downloads`、`~/.pqa`，平台要求需求与产出都在工作区里（P-15，`docs/architecture/README.md:165`）。
- **阶段主文件**：五个候选都不产 `sources.md`，而 P-20 要求进文献阶段的步骤能力必须留下它（`docs/architecture/README.md:170`）。

形态上会碰到的现有规则（只列事实）：

- **MCP**：两家适配器起会话时都清空了 MCP，Claude Code 用 `--strict-mcp-config`，Codex 写 `mcp_servers={}`（`platform/backends/claude_code.py:39`、`platform/backends/codex.py:118`）。这是 P-11 隔离的实现（`docs/architecture/workflow.md:238`），纲领里没有专门讲 MCP 的一条。arxiv-mcp-server 只有 MCP 这一种形态。
- **命令入口（P-14）**：助理面前只有 `ai4sci`，执行层只有 `ai4sci skill`；Codex 侧 `ai4sci` 以外的命令在没有网络的沙箱里跑（`docs/architecture/README.md:164`、`platform/backends/codex.py:127-141`）。K-Dense paper-lookup 的主流程是 agent 自己 `curl | python3`，Paper Search MCP 的 skill 教 agent 直接运行 `paper-search`，都不在放行范围内。
- **skill 格式（P-22）**：K-Dense 的 166 个 skill 按平台的 `load_skill()` 读，只有 22 个能过，文献相关的全都不过（原因是 `allowed-tools` 字段、嵌套的 metadata、脚本没有 PEP 723 块和锁文件）；而 `scan()` 只要有一个不过就整库报错（[k-dense-skills.md §5.3](k-dense-skills.md#53-接进来会碰到平台哪些现有规则)）。
- **调模型与凭据**：总纲把 skill 脚本写成「确定性工具」（`docs/architecture/README.md:7`）。arxiv-mcp-server、Paper Search MCP、K-Dense 的 paper-lookup 与 citation-management 都不调模型；PaperQA2、GPT Researcher 的研究路径自己调模型，只认 API key（[paperqa2.md §5.3](paperqa2.md#53-会碰到的平台规则)、[gpt-researcher.md §5.3](gpt-researcher.md#53-会碰到的现有规则)）；K-Dense research-lookup 的缺省路径要 Parallel 账号。平台现有 skill 里读独立凭据的只有 `download` 的 `HF_TOKEN` 一个先例，而且那是取数据的凭据，不是调模型的（`platform/skills/download/SKILL.md:4`）。

**讨论前要弄清的问题**
1. 这一格做成「步骤」还是「skill」。如果做成步骤，就得留下 `sources.md`（P-20），而五个候选都不产它；检索出来的结构化条目（DOI、作者、日期、开放获取链接）和现在手写的材料清单（链接、commit、许可证、拿没拿到）怎么对应、由谁来写，需要先定下来。
2. 课题组的论文主要在哪些库：只看 arXiv 够不够，还是以期刊为主、要 Crossref / OpenAlex / PubMed 这类多源检索。五个候选都没有中文学术库，GPT Researcher 的中文源只有通用网页搜索 bocha（[gpt-researcher.md §2.4](gpt-researcher.md#24-检索器与学术源)）。
3. BibTeX 要到什么程度。写作阶段对引用条目的要求还没定：arxiv-mcp-server 的 `@misc` 加 v1 年份够不够，要不要 DOI、期刊、卷期页（doi.org 内容协商能给的那些），要不要联网核对（[arxiv-mcp-server.md §2.6](arxiv-mcp-server.md#26-bibtex)）。
4. 平台对 MCP 是什么态度。现在清空 MCP 只是 P-11 隔离的实现，纲领里没有专门一条；arxiv-mcp-server 的全部能力和 Paper Search MCP 的兜底链只以 MCP 形态提供，这件事本身要先有结论，才能讨论这些候选。
5. 不经 MCP 能不能用，没有试过。arxiv-mcp-server 的 handler 能 import，但存储目录只从 `sys.argv` 读。Paper Search MCP 的命令行没有兜底链、`search` 输出多行 JSON、所有源都失败也退出码 0；导入它的包会读 `~/.config/paper-search-mcp/.env`；PyPI 版落后 main 39 个提交。这些放进 PEP 723 + `uv run --locked --offline` 要各自处理什么，还不知道（[arxiv-mcp-server.md §7](arxiv-mcp-server.md)、[paper-search-mcp.md §5.3](paper-search-mcp.md#53-接进来会碰到的平台规则)）。
6. 平台对「skill 脚本调模型」和「研究者 agent 登录之外的模型 key」没有明文规定。P-1 的判据只查 `framework/`，总纲把 skill 脚本写成确定性工具。PaperQA2、GPT Researcher、K-Dense research-lookup 的几个后端都落在这块空白里。
7. 数据源 key 由谁配、放在哪。S2、OpenAlex、CORE、NCBI 这类取数据的 key，加上 Unpaywall 的 email（不配的话兜底链第 3 环直接跳过），平台只有 `download` 读 `HF_TOKEN` 一个先例；P-25 的 `agents.yaml` 只管 agent。
8. 网络与限额还没实测，分别留给 #166、#169、#163、#172：校园网到 arXiv、Semantic Scholar、OpenAlex、Google Scholar、SSRN、Sci-Hub、api.parallel.ai、openrouter.ai 通不通、多快；S2 不带 key 时限额多少（深读时本机三次都是 429）；OpenAlex 是否已按量收费；多个执行层会话各起一个进程时，arXiv 的 3 秒限流闸彼此不协调。
9. 检索返回「0 条」算成功还是失败。Paper Search MCP 有 18 个源把失败吞成空列表，arxiv-mcp-server 也有几处软失败；P-7 要求 fail-closed，检索类能力的空结果和请求失败怎么区分，需要先有判据（[paper-search-mcp.md §1.5](paper-search-mcp.md#15-readme-说了代码里没有或很薄)）。
10. 全文由谁出。候选自带的几种全文（arXiv HTML 文本、LaTeX 分节、pypdf、PyMuPDF 纯文本、JATS）和平台 `pdf` skill 的 `paper.md` + `structured.json` 在同一篇论文上差多少，没有比过；这决定候选只负责「找到并拿到 PDF」，还是也负责读。
11. 存放位置能不能落到调用方给的 `materials/` 下。arxiv-mcp-server 的存储目录一个进程一个；Paper Search MCP 的命令行有 `-o`，MCP 形态缺省 `./downloads`；PaperQA2 缺省 `~/.pqa`。
12. Sci-Hub 与抓取的合规边界没有评估。Paper Search MCP 的 `download_scihub` 在 MCP 里常驻、没有开关；Google Scholar、SSRN 靠抓 HTML；K-Dense citation-management 也用 `scholarly` 抓 Google Scholar。平台对这类来源没有规定。
13. 许可证的影响取决于平台怎么分发，而分发方式还没定：arxiv-mcp-server 的 `[pdf]` 锁定 PolyForm Noncommercial 的 pymupdf-layout 1.27.1；GPT Researcher 硬依赖 AGPL 的 PyMuPDF；PaperQA2 有可选的 AGPL 子包；平台的 `pdf` skill 本身也是 AGPL 或商业许可。
14. 三种接法：依赖上游包、把脚本拷进来、只参考接口手册自己写，要处理的事各不相同，包括上游维护风险：arxiv-mcp-server 单人维护、2026-08-26 之后没有提交、`mcp` 钉在 `<2`；Paper Search MCP 发版没有固定节奏；K-Dense 的文献脚本只有 paper-lookup 在 CI 里。平台对外部代码采取哪种做法，还没有先例。
15. 范围问题：arxiv-mcp-server 的引用图和主题订阅、PaperQA2 的本地库问答、GPT Researcher 的综述报告、K-Dense 的 literature-review，算不算这一格的事，还是归到文献综述（#154）等别的能力。#153 的定义只写到「找论文、元数据、全文、BibTeX」。
16. K-Dense 有 136 个 `SKILL.md` 要求 agent 往产出的稿子里加一条 K-Dense 论文的引用。这些 skill 放进哪一层，那一层的 agent 就会读到；会不会照做，没有测过（[k-dense-skills.md §5.3](k-dense-skills.md#53-接进来会碰到平台哪些现有规则)）。

### 文献综述（文献阶段）

对应 issue #154。这一类的主候选是 GPT Researcher（#170）和 STORM（#173，只借鉴）。PaperQA2（#158）、K-Dense Scientific Agent Skills（#161）、Academic Research Skills（#183）的主体分别挂在论文阅读 #152、文献检索 #153、论文写作 #157 下，这里只比它们和「围绕一个题目检索多篇、综合成带引用的综述」有关的部分。「实际做到什么」一栏以深读对代码的核对为准，README 和论文摘要只当线索。

| 候选 | 实际做到什么 | 做法 | 调模型与 key | 外部服务 | 成熟度 | 许可证 | 出处 |
|---|---|---|---|---|---|---|---|
| GPT Researcher（研究，#170） | 输入一句问题，输出一篇 markdown 报告：1 次模型调用选角色提示词，1 次拆出 3 条子查询，加上原问题共 4 条并行检索，抓约 25 页，BM25 挑段落，再用 1 次模型调用写成不少于 1200 词的报告，带 URL 级内联引用和 APA 参考列表。deep 模式是递归树，宽 3 深 2，约 33 次模型调用，它自带的成本计数漏算这部分。引用只靠提示词约束，运行路径上没有代码核对 URL 抓没抓过、原文支不支持；作者在 10 道通用英文题上测得引用精确率 56%。四个学术检索器（arXiv、Semantic Scholar、OpenAlex、PMC）只返回标题、链接、摘要，作者、年份、DOI 都丢掉，arXiv 只拿到摘要。README 说的 Claude skill 装下去是一份开发说明书；Codex 插件的 `uvx gpt-researcher` 在 wheel 里没有对应入口；gptr-mcp 的 `deep_research` 跑的是标准研究，不是 deep 模式 | 形状固定的流水线：两次提示词调用加一组 asyncio 协程，没有 agent 循环。检索器、抓取器、BM25 筛选都不调模型，可以单独用；`quick_search()`，以及给定 `source_urls` 并预设角色时，都是零次模型调用 | 自己经 LangChain 调模型，默认 `OPENAI_API_KEY`（gpt-5.4 / gpt-5.4-mini），可换 27 家 provider（含 Anthropic、Ollama）。只认各家 API 凭据，不认 Claude Code / Codex 的登录。三种外壳（skill、Codex 插件、gptr-mcp）都由它自己调模型，gptr-mcp 没有 `OPENAI_API_KEY` 就退出。搜索默认要 `TAVILY_API_KEY`；`TYPESAFE_API_KEY`（Jev 段落筛选）可选 | 模型 API；Tavily（商业）；被抓取的网站，15 并发；arXiv、OpenAlex、PMC 免 key；Semantic Scholar 不带 key 时本机三次请求都返回 429；tiktoken 首次使用要下载编码表。硬依赖 140 个，缺 provider 包时在运行中 `pip install` | 29.6k star，近 12 个月 468 个提交；测试到 2026-08 才进 CI；PyPI 0.16.0 在 3.12 / 3.13 上一 import 就报错，挂了 70 天；默认的 BM25 筛选 2026-09-26 才进代码；2026-07-14 一天批量关掉 110 个 issue；README 自己写着不建议用于学术或研究论文 | `LICENSE` 是 Apache-2.0，包元数据和维护者的说法是 MIT；硬依赖 PyMuPDF 是 AGPL-3.0 / 商业双许可（上游 #1582 未决）；gptr-mcp 是 MIT | [gpt-researcher.md](gpt-researcher.md)：[2.2](gpt-researcher.md#22-标准研究的一次运行)、[2.3](gpt-researcher.md#23-deep-research)、[2.4](gpt-researcher.md#24-检索器与学术源)、[2.5](gpt-researcher.md#25-引用怎么进报告)、[2.6](gpt-researcher.md#26-怎么调模型)、[2.7](gpt-researcher.md#27-三种外壳)、[4](gpt-researcher.md#4-跑起来要什么)、[6](gpt-researcher.md#6-成熟度) |
| STORM / Co-STORM（只借鉴，#173） | 流程是：主题 → 视角发现（模型写出维基百科相关条目的链接，抓目录，列出 N 个角色；一个链接都抓不到时静默退化成纯靠模型列角色）→ 每个角色一条多轮对话（提问 → 拆成最多 3 条查询 → 检索 → 写带 `[n]` 的回答 → 读完再问）→ 草稿大纲按对话精修 → 逐节用本地 MiniLM 从来源表取片段，写带引用的正文，并用零模型代码清洗引用编号 → 写导语。Co-STORM 另有主持人（从检索到但没被引用的资料里生成新问题）、思维导图，人可以随时插话改方向。代码和论文对不上的地方：论文说的可靠来源过滤在 main 上零调用；main 的缺省参数和论文不同；Co-STORM 的评测脚本没公开；静态读出引用编号清洗有差一错误，大纲清洗的正则会连带删掉相邻的节 | 各步的分量看论文消融：多轮「读完回答再问」最关键，去掉后收集到的不同来源从 99.8 条降到 39.6 条；先定大纲次之，去掉后 ROUGE-1 从 45.8 降到 26.8；视角主要增加来源数（54 → 100）。引用精确率 85.18、召回率 84.83（由另一个模型判），不被支持的句子里 47% 是根本没挂引用。评测对象是维基式文章，检索是通用网页，只做英文 | 每一步经 dspy（钉 2.4.9）调模型后端，示例默认 OpenAI；有 Ollama 配 DuckDuckGo / SearXNG 的示例，静态看 STORM 可以一个云端 key 都不用（未跑）；Co-STORM 的嵌入只接 OpenAI 或 Azure；不认 CLI 登录 | 搜索 API（You.com、Serper、Brave、Tavily 等要 key；Co-STORM 缺省用 Bing，Bing Search API 已于 2025-08-11 停服）；wikipedia.org（视角发现要抓）；Hugging Face（首次下载 MiniLM） | 31.5k star；最近一次 release 是 v1.1.0（2025-01-23），之后 main 只有 5 个提交；main 没有测试，CI 只有 black 检查和手动发布；按代码数调用量，main 缺省约 50 次模型调用、最多 36 次搜索，论文设置约 105 次 | 代码 MIT；FreshWiki、WildSeek 数据集 CC BY-SA 4.0 | [storm.md](storm.md)：[1](storm.md#1-方法是什么)、[2.3](storm.md#23-哪一步最关键)、[2.4](storm.md#24-代码是否按论文做)、[4.1](storm.md#41-数据与网络)、[4.2](storm.md#42-模型与调用方式)、[4.3](storm.md#43-算力与调用量)、[4.5](storm.md#45-仓库状态) |
| PaperQA2（研究，#158；主体在论文阅读 #152） | 对本机一个论文目录做带引用的问答，输出一段答案，不输出综述：tantivy 挑论文 → 块级向量召回 → 每块一次模型调用出摘要加 0–10 分（RCS）→ 取前 5 条写答案。答案里的 `pqac-` 键事后换成「作者年份 pages 页码」并生成参考列表，本次收集的证据里没有的键直接删掉，但不查句子是否被那条证据支持。开源版不联网找论文，没有引用遍历，也没有 Grobid（论文 §8.1 自己写明）；论文里生成综述式文章的 WikiCrow，在仓里只剩一份设置文件，没有拼接脚本 | 工具调用循环的智能体（aviary `ToolSelector`，五个默认工具）；Crossref、Semantic Scholar、期刊分级补来的元数据写进 RCS 的 prompt | 自己经 litellm 调模型；`llm`、`summary_llm`、`agent_llm`、`enrichment_llm`、`embedding` 五个槽默认都是 OpenAI（gpt-4o-2024-11-20、text-embedding-3-small）。换 Anthropic 要改四个 LLM 槽，嵌入要另找一家，或用本地 `st-`，或纯稀疏；不认 CLI 登录 | 模型 API；默认连 api.crossref.org、api.semanticscholar.org（key 可选，不设会限流，这一步可关）；索引和答案库写在 `~/.pqa` | 9,251 star；CI 带真 key 调 OpenAI、Anthropic、Gemini 等，共 237 个测试函数；改用 CalVer 后明说不保证版本间兼容；main 在 2026-04 到 09 之间合计 4 个提交；论文报每次查询 1–3 美元 | Apache-2.0；可选子包 `paper-qa-pymupdf` 是 AGPL-3.0，装上后就成为默认 PDF 解析器 | [paperqa2.md](paperqa2.md)：[1.2](paperqa2.md#12-论文里的系统与仓里的系统)、[2.5](paperqa2.md#25-回答与引用绑定)、[2.7](paperqa2.md#27-怎么调模型)、[5](paperqa2.md#5-和平台对照)、[6](paperqa2.md#6-成熟度) |
| K-Dense Scientific Agent Skills（研究，#161；主体在文献检索 #153） | `literature-review`：`SKILL.md` 定了七个阶段（规划、检索、筛选、抽取与质量评估、综合、引用核对、出文档），方法论是文字，综述正文由宿主 agent 写。脚本只做四件事：离线去重排序；查 DOI 能否解析（不比对标题和作者，解析失败也以退出码 0 结束，没有测试）；pandoc 出 PDF；按「强制」要求生成 1–2 张 AI 配图。`research-lookup`：用 Parallel 检索，限定 25 个学术域名、分五个方面，最多抽取 60 条，写出十个文件的证据包；证据矩阵、论断—来源映射、共识与冲突都是关键词和正则启发式，它说的「已核实」包括正则匹配到一个 DOI / PMID | 给宿主 agent 读的说明文档加少量脚本，agent 自己在 shell 里 `curl`、跑 `python3 scripts/x.py`；仓库本身不调模型 | 正文由宿主的模型写。例外：literature-review 的配图脚本要 `OPENROUTER_API_KEY`（用 gemini 出图、打分）；research-lookup 缺省要 Parallel 登录或 `PARALLEL_API_KEY`，它的 chat / research / perplexity 后端返回的是服务端生成的文本；没装 `parallel-cli` 但有 OpenRouter key 时，普通查询会自动转到 Perplexity（读代码推断） | Parallel（parallel.ai；literature-review 给的装法之一是 `curl \| bash`）、OpenRouter、doi.org、Crossref；pandoc + xelatex | 46.7k star；11 个月 106 个自动 release，第一作者提交占 44%；CI 只跑 20 个纯标准库 skill 的测试，literature-review、research-lookup 不在其中；论文明写没有任务级评测。用平台的 `load_skill` 逐个读，文献相关的五个和 scientific-writing 都过不了；整包放进 `platform/skills/` 时 `scan()` 会让整个库报错 | 文献相关的五个是 MIT；同仓的 `pdf`、`docx`、`pptx`、`xlsx` 是 Anthropic 专有条款；136 个 `SKILL.md` 末尾有一节，让 agent 往稿子里加 K-Dense 论文的引用 | [k-dense-skills.md](k-dense-skills.md)：[1.3](k-dense-skills.md#13-文献相关-skill-逐条对账)、[2.3](k-dense-skills.md#23-research-lookup)、[2.4](k-dense-skills.md#24-literature-review)、[5.3](k-dense-skills.md#53-接进来会碰到平台哪些现有规则)、[6](k-dense-skills.md#6-成熟度)、[6.4](k-dense-skills.md#64-许可证条款要点) |
| Academic Research Skills（研究，#183；主体在论文写作 #157） | 相关的是 deep-research 的三个模式（`deep-research/SKILL.md:363-367`，ARS 仓 e79085d）：`lit-review`（书目、来源核验、综合三个角色，出注释书目加综合，1,500–4,000 词）、`systematic-review`（PRISMA 2020、偏倚风险、荟萃分析）、`three-way-scan`。检索策略、两轮筛选、证据分级、注释书目、主题综合、矛盾与缺口分析都是提示词（`deep-research/agents/bibliography_agent.md:56-158`、`deep-research/agents/synthesis_agent.md:54-204`）。确定性代码有四样：四索引引用存在性库（运行时由谁调用未弄清，它的命令行默认拒绝输出）、撤稿信号归一化、PDF 页数预检、Zotero / Obsidian / 文件夹导入器。作者自己的能力矩阵 16 行里 10 行是 NOT_RUN，外部结果证据一行都没有；v2.7 的样例论文过了三轮诚信检查，68 条参考文献里仍有 21 条有问题 | Claude Code 插件：4 个 skill、16 条命令、2 个 hook。39 个角色默认由当前会话的模型在同一个会话里依次 inline 执行，每个阶段停下等用户回合；检索用会话自带的 WebSearch / WebFetch，加上四个索引的 HTTP 协议文档 | 用当前 Claude Code 会话的模型（API key 或 `claude` 登录），13 条命令钉了 `model: sonnet`；可选的第二模型要 OpenAI / Gemini key 或 Codex 登录。经 academic-pipeline 编排时，synthesis 交付后要一份在会话外手动运行的 Codex 审计记录，提示词写明不可跳过（默认运行时会不会真拦，未验证）；单独跑 deep-research 时，它的 SKILL.md 和 synthesis 提示词里 grep 不到这道闸门 | Semantic Scholar、OpenAlex、Crossref、arXiv（免 key，有 key 只是提速）；每天查一次 GitHub 上的版本；Pandoc、tectonic 可选 | 4.96 万 star；2026-03 到 09 共 45 个 release；维护者一人约占 96% 提交；14 个 CI workflow 全部离线、只跑 Ubuntu；依赖 Claude Code 插件、Skill / Agent 工具、hook 和交互回合；平台的 `load_skill` 对每个 SKILL.md 报两处问题；Codex 版在另一个仓，没读 | CC BY-NC 4.0，覆盖整个仓库，包括代码；作者自称 source-available；改编后分发，下游仍只能非商业使用 | [academic-research-skills.md](academic-research-skills.md)：[1.6](academic-research-skills.md#16-对-claude-code-专有能力的依赖)、[1.7](academic-research-skills.md#17-作者自己标的证据上限)、[2.3](academic-research-skills.md#23-怎么调模型)、[3.2](academic-research-skills.md#32-作者踩过的坑)、[5](academic-research-skills.md#5-和平台对照)、[6](academic-research-skills.md#6-成熟度)、[6.3](academic-research-skills.md#63-许可证条款要点) |

**平台缺的与候选补的**

平台现在的做法：文献阶段没有步骤能力。主文件 `sources.md` 由助理手写，材料是它用 CLI 自带的搜索与读网页找来的，框架只认文件名。指南给出的是复现用的材料清单：论文、代码、数据、别人的复现、跑起来要什么，每样写清链接、版本、许可证、拿没拿到（`platform/coordinator/README.md:120-128`、`platform/framework/capabilities/__init__.py:45-47`）。流程助理被要求在有人要「写综述」时直接说平台还没有这个能力（`platform/coordinator/studio.md:42`）。skill 只有两个：解析单篇 PDF 的 `pdf` 和拉材料的 `download`，都不调模型。

「围绕一个题目检索多篇、综合成带引用的结构化综述」拆开是五段：检索学术源并保留书目元数据；逐篇取证（挑段落或写摘要）；组织结构（视角、大纲）；按结构带引用成文；核对引用（引文是否存在、原文是否支持）。各候选补的位置：

- GPT Researcher 在自己的进程里把前四段串成一条流水线，但学术检索薄，引用不核对（[gpt-researcher.md](gpt-researcher.md#24-检索器与学术源)）。
- STORM 补的是第三、四段的方法：多轮追问、先大纲后逐节写、引用编号清洗。它的代码面向维基式文章和通用网页（[storm.md](storm.md#3-平台哪里能用)）。
- PaperQA2 补第二段和页码级的引用绑定，但输入是本机论文目录，输出是一问一答，不产综述（[paperqa2.md](paperqa2.md#5-和平台对照)）。
- K-Dense 的 `literature-review` 和 ARS 的 `lit-review` 都把五段写成给宿主 agent 的流程说明。它们的确定性代码只覆盖机械部分：去重、DOI 能否解析或是否存在、页数预检。引用是否被原文支持，两者都交给模型或人判断（[k-dense-skills.md](k-dense-skills.md#24-literature-review)、[academic-research-skills.md](academic-research-skills.md#5-和平台对照)）。

和平台现有东西的重叠有五处：

1. 读文献、写材料：K-Dense 和 ARS 写的正是助理现在手动在做的事，多出来的是筛选、PRISMA 计数、注释书目格式、综合写法这些流程要求，加上几支小脚本。
2. 联网：GPT Researcher（Tavily 等）和 K-Dense（Parallel）各自带另一条搜索通道；ARS 用的是和平台同样的会话自带搜索。P-14 规定联网只用 CLI 自带的搜索与网页读取（`docs/architecture/README.md:164`）。
3. PDF 解析：GPT Researcher 用 PyMuPDF 出纯文本，PaperQA2 有四种读取器；平台已经有 `pdf`。
4. 模型调用：GPT Researcher、PaperQA2、STORM 的代码自己调模型。放进平台的 agent 会话，就等于在一个会话的循环里再跑一个循环，两边各用各的凭据。P-1 规定正文只由执行层产出、框架不调模型，它的判据只查 `framework/`（`docs/architecture/README.md:151`）；P-25 规定底座走研究者自己的 agent 登录（`docs/architecture/README.md:175`）。
5. 产物形状：五个候选都不产 `sources.md`，而 P-20 要求进文献阶段的能力必须留下它（`docs/architecture/README.md:170`）。

另外，判断引用是否被来源支持需要模型判断，而平台 P-2 的隔离评审还没实现（`docs/architecture/README.md:152`）。

**讨论前要弄清的问题**

1. 综述写到哪：写进文献主文件 `sources.md`（现在是复现用的材料清单形状），作为能力的私有文件，还是算写作阶段的产物？P-20 只定了文献阶段的主文件名（`docs/architecture/README.md:170`）。
2. 和论文阅读 #152、文献检索 #153 怎么分界：检索、逐篇取证、综合成文三段各归哪一类？PaperQA2、K-Dense 的主体已经挂在那两类下。
3. skill 脚本自己调模型写出综述正文（GPT Researcher、PaperQA2、STORM 的代码），和 P-1「正文只由执行层产出」怎么对上？P-1 的判据目前只查 `framework/`（`docs/architecture/README.md:151`）。
4. 候选要的单独凭据由谁提供、成本怎么记：OpenAI、Tavily、Parallel、OpenRouter，以及 Co-STORM 要的 OpenAI 或 Azure 嵌入 key。P-25 走的是研究者的 agent 登录，订阅账号报不出美元时成本记 NaN（`docs/architecture/README.md:175`）。平台现有 skill 里只有 `download` 读 `HF_TOKEN`，那是取数据的凭据，不是调模型用的（`platform/skills/download/SKILL.md:4`）。
5. Claude Code 和 Codex 自带的搜索与读网页，能不能给出这些方法需要的「URL + 原文片段 + 稳定编号」，以及学术接口的原始响应（[storm.md](storm.md#5-还没弄清的问题)，K-Dense 深读第 7 节第 3 条，#163）？
6. 候选自带的搜索通道（Tavily、Parallel 等）和 P-14「联网只用 CLI 自带工具」怎么对上？`ai4sci skill run` 起的脚本能联网，已有 `download` 这个先例（`platform/framework/skills/run.py:36-42`）。
7. 引用核对要做到哪一级：URL 抓过、键存在（PaperQA2）、DOI 能解析（K-Dense；ARS 的四索引库没接线），还是句子被原文支持？「被支持」由谁判？P-2 的隔离评审尚未实现（`docs/architecture/README.md:152`）。
8. 在平台用户的课题上（PINN、参数估计这类工程物理题），各候选检索到的内容里论文正文占多少、引用精确率多少？#172、#160、#185 的实测都还没出结果。
9. 中文文献怎么覆盖？GPT Researcher 的 BM25 不切中文，中文源只有通用网页搜索 bocha；STORM 只做英文；ARS 只注册了繁中—英文语言对，中文 DOI 在它的四索引闸门里会被判 unresolvable；PaperQA2 的中文效果未知。
10. ARS 这类依赖 Claude Code 插件、Skill / Agent 工具、hook 和交互回合的流程，在平台一次性、带 `--disable-slash-commands` 等隔离参数的执行层会话里能不能加载？每个阶段的检查点会停下还是被跳过（`platform/backends/claude_code.py:39`）？
11. 综述里哪几步要人确认（检索式、纳入与排除标准、大纲、终稿），和平台的断点、`signed.json` 怎么对应？Co-STORM 的人只能插话改方向，ARS 靠停在对话里等用户回合。
12. 调用量与成本能不能放进执行层的默认上限 `--max-turns 30`、`--max-budget-usd 2.0`（`platform/backends/claude_code.py:160-162`）？参考数字：GPT Researcher deep 模式约 33 次模型调用；STORM 约 50–105 次；PaperQA2 论文报每次查询 1–3 美元；ARS 全流程 2.8–7 美元。
13. 许可证：ARS 的 CC BY-NC 4.0 覆盖代码，GPT Researcher 硬依赖 PyMuPDF（AGPL），K-Dense 同仓有 Anthropic 专有条款的 skill。在平台的分发方式下，哪些能随平台带，哪些只能由研究者自己装？
14. 只借方法（多轮追问、先大纲后逐节写、RCS、引用键绑定、筛选与 PRISMA 计数），写成平台自己的步骤描述或 skill 说明，和接入现成实现相比，各自要先验证什么？

### 研究创意（假设阶段）

对应 #155。这类能力要做两件事：生成候选研究方向，并查新（和已有工作比有没有新意）。AI Scientist 两代在出想法和查新上做法不同，所以分成两行。SciAgents（#179）和 AI Research SKILLs（#189）的主体挂在别的能力下，这里只比和出想法、查新有关的部分。「实际做到什么」一列以深读里的代码对账为准，README 和论文的说法不算。

| 候选 | 实际做到什么 | 做法 | 调模型与 key | 外部服务 | 成熟度 | 许可证 | 出处 |
|---|---|---|---|---|---|---|---|
| AI Scientist 一代（只借鉴，#175） | 出一批想法，每条六个字段：三个文本字段，加有趣度、可行性、新颖度三个 1–10 的自评分，自评分全仓没有读取点。每条想法单独查新，只写回一个布尔 `novel`，主流程只跑判新的；检索词、命中论文、判定理由只打到 stdout。论文和 Nature 版写的「网页访问」「与已有工作语义相似度高的丢弃」，代码里都没有 | 基线代码全文、两句任务描述、已出过的全部想法原文放进 prompt，要求出一条「不同」的；同一段对话反思 3 轮，模型写 `I am done` 就提前停。查新：每条想法新开一段对话，用「苛刻查新者」口吻，每轮给一个检索词、看 S2 前 10 条摘要，最多 10 轮；靠回复里的 `Decision made: novel / not novel` 判定，代码不数检索次数，轮数用完没判定就算不新 | Python 直接用 `anthropic` / `openai` SDK 调模型 API，按模型名分派（DeepSeek、OpenRouter、Gemini 换 `base_url`），各家 key 取环境变量；出想法和查新用同一个模型；`S2_API_KEY` 可选 | 模型厂商 API；Semantic Scholar 检索（没有 key 时限速，退避不设上限）；可选 OpenAlex（查新能用，写作取 bibtex 时缺字段） | 论文 2024 年，Nature 版 2026 年；两篇都没有出想法的消融，也没测查新准不准。独立评测（Beel 等，一个课题、一个模型）12 条想法全部判新，其中有已知做法。`requirements.txt` 不带版本、没有锁文件；检索卡住的 issue #78 #116 #133 都没关 | AI Scientist Source Code License 1.0（2025-12-19 由 Apache 2.0 改来）：有五类使用限制，其中一条要求用它产出的稿件显著声明是机器生成的；这些限制必须写进衍生作品的协议 | [ai-scientist §2.1](ai-scientist.md#21-一代出想法)、[§2.2](ai-scientist.md#22-一代查新)、[§3.2](ai-scientist.md#32-独立评测)、[§5](ai-scientist.md#5-局限与前提)、[§5.1](ai-scientist.md#51-许可证条款要点) |
| AI Scientist 二代（同 #175） | 输入一份主题 Markdown，出七个文本字段的想法（`Short Hypothesis`、`Related Work`、`Experiments`、`Risk Factors and Limitations` 等），下游实验缺其中五个键之一就抛错。检索是模型可选的动作；没有查新判定、没有过滤，跑哪条由人用 `--idea_idx` 指定；只存定稿的想法。树搜索只用在实验，不用在出想法 | 每轮模型二选一：`SearchSemanticScholar`（结果按引用数重排，前 10 条进下一轮）或 `FinalizeIdea`。最多 5 轮，定稿就停，没定稿的作废；「定稿前至少检索一次」只写在 prompt 里 | 和一代一样按 SDK 分派，默认 `gpt-4o-2024-05-13`。2025-09-30 起可以接本机 Ollama，不要付费 key（本地模型守不守回复格式没有数据）。S2 key 可选（初版没有 key 就抛错，2025-04-17 改掉） | 模型厂商 API 或本机 Ollama；只有 S2（OpenAlex 的两个 PR 没合）。S2 出错或断网时无上限退避，出想法脚本没有跳过检索的开关 | 论文对出想法和检索没有定量评估。实际用法：约 40 条想法里人挑 3 条跑，人再挑成稿投稿，1 篇过了 workshop。没有锁文件；README 说能跳过查新，出想法阶段没有这个开关 | 和一代同一份 | [ai-scientist §2.3](ai-scientist.md#23-二代出想法与检索合在一个循环里)、[§2.4](ai-scientist.md#24-两代差别)、[§3.3](ai-scientist.md#33-代码是否按论文做) |
| AutoResearchClaw（只借鉴，#177） | Stage 8 三个角色（innovator / pragmatist / contrarian）各写一份，再合成 2–4 条，写进自由格式的 `hypotheses.md`（执行器只查文件非空）。查新真的去三个库检索，但结果只写进没有下游读取的 `novelty_report.json`。人能改到假设的只有三条路：Stage 8 执行前写好意见文件、co-pilot 模式下跑完后协作对话、停下来手改再续跑。Idea Workshop 的出想法 / 打分 / 细化、分支并行、想法池都零调用。论文说的角色互相质疑、PIVOT 带着失败回到假设生成，在代码里不成立。有反驳轮的 debate 和 best-of-N tournament 是 2026-08-18 才加的，默认关 | 提示词变量只有 `{topic, synthesis}`（Stage 7 从知识卡片合成的 Gap 列表）；角色提示词按领域换，能走到的只有 ML、HEP 两套。查新流程：从主题和假设抽英文关键词，组成最多 5 条检索式，查 OpenAlex / S2 / arXiv，按引用数取前 30 篇，算关键词 Jaccard，得出分数和 proceed / differentiate / abort 建议（按公式推算多半给 high，而且只认 ASCII）。模型全部失败时写三条模板假设，阶段仍记 DONE | 非 acp 的 provider 走 HTTP 接口（OpenAI 兼容、Anthropic、OpenRouter 等），要 `base_url` 和 key，三个角色与合成默认用同一个客户端。打分可以另配 `reviewer_model`（可以单独配 provider 和 key）。provider 选 acp 时，经仓库外的 `acpx` 用 Claude Code、Codex，这时多模型面板和独立打分都不构建，各次调用进同一个会话（按代码推断）。S2 key 可选 | 模型 endpoint 或 `acpx`；OpenAlex、Semantic Scholar、arXiv（某个源失败时退到本地检索缓存） | 论文里能归到假设生成的证据只有三处：同时去掉 Stage 8 和 Stage 14 多角色的消融、一个代码里没有对应参数的角色数消融、一个案例。主表不测假设生成；消融脚本和数据在 `.gitignore` 里。有单测（用假客户端或 mock），但没有测试走 Stage 8 的 debate / tournament 分支；仓库没有 CI | MIT（提示词写在代码里，同样是 MIT） | [autoresearchclaw §1.1](autoresearchclaw.md#11-假设这一段的链路)、[§1.2](autoresearchclaw.md#12-人怎么参与假设共创)、[§1.5](autoresearchclaw.md#15-查新怎么做)、[§2.2](autoresearchclaw.md#22-这些证据测没测到假设这一段)、[§4](autoresearchclaw.md#4-局限与前提) |
| SciAgentsDiscovery（只借鉴，#179；只比出想法与查新） | 在一张现成的生物启发材料概念图上（33,159 个节点，从 Hugging Face 下载，本仓不建图）取两个概念之间的一条路径，拼成一行「节点 -- 关系 -- 节点」。然后依次是：本体学家解释路径，科学家写七字段 JSON 假设（材料领域措辞，没有出处和证伪判据），七个字段各扩写一次，批评者给优缺点和两个优先问题；批评不回流改稿。查新只在自动版里有；非自动版固定 12 次调用，落 md / PDF / CSV | 关键词用 bge-large embedding 对到最近的节点。按论文参数，实际走的是「边权 + 每跳随机噪声」的 Dijkstra，再绕 4 个随机路标；论文说的 embedding 启发式和二跳邻居都没用上。自动版是 AutoGen 0.2 群聊，由模型挑下一个发言者；查新 agent 调 S2 最多三次，读前 10 条摘要，给 1–10 的新颖性和可行性分，分数是自由文本、代码不解析。附录里一条返回 0 篇的长查询被判 8 分；6 份自动对话里有 3 份是人打字催了才调查新（深读按上下文判断） | Python 直连 OpenAI，写死 `gpt-4o`，要 `OPENAI_API_KEY`；各角色 temperature 0–0.2 写在代码里，自动版带本地缓存。`SEMANTIC_SCHOLAR_API_KEY` 代码里可以不设（README 写必需）。embedding 在本机跑 bge-large（torch + transformers） | OpenAI API；Semantic Scholar（深读里无 key 连发 8 次，7 次返回 429）；Hugging Face（图文件和 138 MB 的 embedding pickle，读 pickle 会执行其中的代码） | 638 star，60 个提交，零 release，没有测试和 CI；最后一次提交在 2025-05-10，只改了 README。依赖没有锁，`pyautogen` 没有上限而新版已换了 API，GraphReasoning 要另装。论文没有消融、没有基线、没有人工评审；附录六份自动对话开场的 agent 简介和公开代码对不上 | 代码 `LICENSE.txt` 是 Apache-2.0（`setup.py` 写 MIT，两处不一致）；图数据 apache-2.0；期刊论文（含印出的提示词图）CC BY-NC 4.0；S2 数据受它的 API 协议约束 | [sciagents §1.1](sciagents.md#11-仓库画像)、[§1.3](sciagents.md#13-图上怎么取路径)、[§1.4](sciagents.md#14-各个-agent-的分工与提示词)、[§1.5](sciagents.md#15-输出的结构化假设字段)、[§1.6](sciagents.md#16-用-semantic-scholar-查新)、[§4.4](sciagents.md#44-许可证与数据使用) |
| AI Research SKILLs 出想法两个 skill（研究，#189；主体在写作下） | `brainstorming-research-ideas`（10 个思考框架）和 `creative-thinking-for-research`（8 个）是两份纯 Markdown 提示词，没有 `scripts/`，由宿主 agent 带着研究者过框架。不检索文献、不落文件，新颖性只有自检问题。同库 `autoresearch` 的模板里有整库唯一的假设条目形状（`id`、`statement`、`status`、`motivation`、`parent`、`priority`） | 先判断研究者处在什么状态，挑 2–3 个框架；攒 10–20 个候选，用 5 条淘汰标准收到 3–5 个；第一名写成两句话陈述、3 个验证实验和一个 2 周试点。creative-thinking 另给一个 90 分钟的四段流程。两份都写明领域知识来自研究者，最后选哪个由研究者定 | 自己不调模型，`dependencies: []`，不要 key；判断全靠宿主 agent | 无。文献综述指向的 `scientific-skills:literature-review` 是 K-Dense 改名前的插件名，现在对不上 | 两个 skill 在 2026-02-19 一次加入后没改过；整库零测试，CI 只核 skill 总数；2026-06-16 之后没有提交；creative-thinking 点了一串认知科学的人名，没有一条参考文献。原样放进平台 `skills/` 过不了 `make skills`：frontmatter 多出 `version` `author` `tags` `dependencies` 四个字段，而库里一个 skill 不合规，整库扫描就报错 | MIT（`LICENSE` 和 frontmatter 都写 MIT；仓库根 `package.json` 写 ISC） | [ai-research-skills §1.3](ai-research-skills.md#13-出想法两个)、[§2.5](ai-research-skills.md#25-出想法两个)、[§2.6](ai-research-skills.md#26-autoresearch-一段话)、[§5.3](ai-research-skills.md#53-会碰到的平台规则)、[§6](ai-research-skills.md#6-成熟度) |

**平台缺的与候选补的**

平台现在的情况：
- 假设阶段没有「步骤」能力，`MAIN_FILES` 里没有这一行，主文件名和字段都没定（`platform/framework/capabilities/__init__.py:43-51`、`platform/docs/add-a-capability.md:43`）。
- 助理只能用 `ai4sci output new hypothesis` 开目录手写（`platform/framework/cli/output.py:1-6`）。
- 下游 `design` 把假设产出里所有 `.md` / `.txt` 原样拼进执行层提示词，不认字段（`platform/framework/capabilities/design/__init__.py:103-108`、`:175-182`）。
- 分析稿固定有「证伪与未决」一节，是自由文本，没有假设编号可以对（`platform/framework/capabilities/analysis/prompt.md:22`）。
- 出厂的 `research` 流程从设计走到验证，不经过假设（`platform/workflows/research.yaml:1`）。
- 查新在平台上没有任何对应的东西：联网只有两层 agent 自带的搜索和读网页（`docs/architecture/README.md:164`、`platform/framework/executor/prompting.py:21-25`）。
- 需要模型判断的评审（包括假设质量）要派一个隔离的新会话，这一段尚未实现（`docs/architecture/README.md:152`）。

所以缺的是四块：
1. 一个会出假设、留下主文件的步骤；
2. 查新：检索、判定、把检索证据留下来；
3. 和写稿分开的评审或打分；
4. 把上一轮分析结论带回来，重新出假设。

候选对这四块的覆盖：
- **出想法**：四个都有，形状各不相同（见表中「做法」一列）。
- **查新**：三个做了检索（AI Scientist、ARC、SciAgents 自动版），判定方式分别是模型写的判定串、确定性的关键词 Jaccard、模型打分；二代和 AI Research SKILLs 不判定。四个都没有拿已知工作当标准答案测过查新，现有观察都是误判成「新」（[ai-scientist.md](ai-scientist.md#32-独立评测)、[autoresearchclaw.md](autoresearchclaw.md#15-查新怎么做)、[sciagents.md](sciagents.md#16-用-semantic-scholar-查新)）。
- **检索证据**：没有一个候选既把证据留下来、又有下游去读。一代只存一个布尔；二代只留模型自己写的 Related Work；SciAgents 的原始结果只进了上下文；ARC 写了近邻论文清单，但没有下游读取。
- **评审和写稿分开**：只有 ARC 配了 `reviewer_model` 时成立，走 acp 时不成立；一代的查新是新对话，但用同一个模型，而且看得到自评分；SciAgents 非自动版的批评只吃成稿，但用同一个模型，批评也不回流（[autoresearchclaw.md](autoresearchclaw.md#23-代码是否按论文做)、[ai-scientist.md](ai-scientist.md#42-跟平台现有规矩的对照)、[sciagents.md](sciagents.md#3-平台哪里能用)）。
- **分析结论回流**：四个都没做；ARC 的 PIVOT 重跑 Stage 8 时输入不变（[autoresearchclaw.md](autoresearchclaw.md#31-可摘出的方法与落点)）。
- **调模型的方式**：三个带代码的候选都在 Python 里直连模型 API；平台是 P-1（框架不调模型，执行层是唯一写代码的）加 P-25（执行层走研究者自己的 CLI 登录），调用方式不同（`docs/architecture/README.md:151`、`:175`）。ARC 的 acp 是唯一能把 Claude Code、Codex 当后端的路径，但走这条路时它的多模型面板和独立打分都不构建。

和平台已有东西重叠的地方：
- **手写与交互式出想法**：助理用 `output new hypothesis` 手写，和 AI Research SKILLs 两个出想法 skill 形状最接近，都是 agent 在对话里带着研究者走、由研究者定；区别是那两个 skill 不落文件（[ai-research-skills.md](ai-research-skills.md#25-出想法两个)）。
- **出多条再挑一条**：平台里同一阶段的多次产出并列存放（`hypothesis/1`、`hypothesis/2`），下游用 `--from` 点名，断点由人签（`docs/architecture/README.md:169`）；对应二代由人用 `--idea_idx` 挑，和 ARC tournament 在框架内打分选一份。
- **文献输入**：ARC 的 Stage 8 只读它自己文献阶段合成的 `synthesis.md`，SciAgents 读概念图；平台的文献阶段是助理手写的 `sources.md`，加 `pdf` skill 出的 `paper.md`。查新的检索结果和 `sources.md` 都是一份论文清单。
- **假设作为下游输入**：`design` 读假设产出，二代的实验侧硬读五个字段，两边都把假设当下游输入；但平台阶段之间不做数据流校验（P-18，`docs/architecture/README.md:168`）。

**讨论前要弄清的问题**

1. **方向在哪一步定。** P-19 规定 `requirement.lock` 是唯一内置的门，需求没确认任何阶段都不开工（`docs/architecture/README.md:169`）。AI Research SKILLs 的两个 skill 和二代的主题 Markdown 都是给「方向还没定」的时候用的；ARC 和 SciAgents 则是在给定主题或给定两个概念的前提下出假设。要先说清：假设阶段的能力只在已确认的需求里出具体、可检验的假设，还是也负责出候选方向（那部分算不算需求确认之前的对话）。
2. **主文件叫什么，一条假设要哪些字段。** 候选的字段各不相同：二代七个文本字段；SciAgents 七个（材料措辞，没有出处和证伪判据）；ARC 合成要求依据、可测预测、失败条件；autoresearch 是 `id` / `statement` / `status` / `parent`。平台的 `design` 现在原样拼文本，分析稿的「证伪与未决」没有编号可对。下游要不要按编号对到某一条假设，决定了字段要不要机器可读（P-13：schema 只在产物要给机器读时才补，`docs/architecture/README.md:163`）。
3. **出想法和查新拆不拆。** 候选里查新放在两种位置：步骤末尾的一段（ARC 的 Stage 8 末尾、一代的主流程），或出想法循环里的一个动作（二代）。在平台上，查新是步骤的一部分、一个 skill，还是文献阶段的事？查新命中的论文和 `sources.md` 是什么关系？
4. **查新的检索走哪条通道。** 四个候选都走 S2 / OpenAlex / arXiv 的结构化 API，返回的是摘要和元数据。平台联网只放行 CLI 自带的搜索和读网页（P-14）；skill 脚本联网有 `download` 这个先例（`platform/skills/download/SKILL.md:4`）。两种通道给查新的输入不同，在课题组的题目上哪个召回更好，没有数据。S2 无 key 的限速（SciAgents 深读 8 次请求 7 次 429）、key 的申请周期、从课题组网络能不能连上，都没查。
5. **查新由谁判、判成什么。** 候选给了四种：模型写判定串（一代）、确定性关键词 Jaccard（ARC）、模型打 1–10 分（SciAgents）、不判定只写 Related Work（二代）。四个都没拿已知工作当标准答案测过，现有观察都是误判成「新」。讨论前要不要先在课题组自己的几个题目上拿已知工作试一次，需要先定。
6. **检索证据留不留。** 没有一个候选把检索式、命中论文、判定理由留下来并且有下游去读。平台产出要不要留？留在哪个文件？谁读（助理、设计阶段、人签字时）？
7. **方法放在哪一层，模型怎么调。** 三个带代码的候选都是 Python 直连模型 API、要各家的 key（二代可以接本机 Ollama；ARC 的 acp 能用 Claude Code、Codex，但那时没有独立打分）。平台上 P-1 规定框架不调模型，P-25 规定执行层走研究者自己的 CLI 登录，`agents.yaml` 里没有第三方 key 的位置（`docs/architecture/README.md:151`、`:175`）。反思轮数、早停串、判定串、角色提示词，是写进执行层会话的说明，还是写进 skill 脚本？要不要为某一段单独配模型 key？这里不下结论。
8. **多角色和评审怎么隔离。** ARC 的三个角色在 API provider 下互相看不见，在 acp 下进同一个会话；一代的查新是新对话，但用同一个模型、看得到自评分；SciAgents 非自动版的批评只吃成稿。平台上几个角色是用几次隔离会话，还是一次会话写几节？P-2 的「隔离新会话」如果用同一家 CLI、同一个模型，算不算独立评审？P-2 这一段还没实现（`docs/architecture/README.md:152`）。
9. **人的意见什么时候进，挑选怎么落地。** ARC 的教训是人的意见在阶段跑完之后才到，改不到这一次的产物；平台能力的输入在开跑前冻结（P-19 / P-20）。研究者挑方向（二代的 `--idea_idx`、SciAgents 由人给端点），在平台上是一次产出里写多条再由人挑，还是多次产出并列，用 `--from` 点名再签字？
10. **分析结论回不回流。** 平台的分析稿固定有「证伪与未决」一节，但四个候选都没有把上一轮实验结论当作重新出假设的输入。假设能力要不要读 `--from analysis/N`？
11. **领域、语言与概念图。** 候选的提示词是 ML 取向（AI Scientist、ARC）或生物材料取向（SciAgents），全是英文，ARC 的查新只认 ASCII；在课题组的学科和中文材料上表现如何，没有证据。领域差异能不能都放进领域包的 `domains/<包>/prompts/<族>.md`（`platform/docs/add-a-capability.md:127`）？SciAgents 的取路径还要一张领域概念图：研究者的领域有没有现成的语料或图，用执行层 CLI 会话逐块抽三元组要花多少时间和钱，都没有数据。
12. **许可证边界。** 在 AI Scientist 2025-12-19 起的新许可证下，照着方法重写、引用提示词原文、用改许可证之前的 Apache 2.0 提交，分别算不算衍生作品？§3.2(e) 要求的机器生成声明，对平台产出的论文意味着什么？这些是法律问题，要定由谁来判。另外，SciAgents 期刊版里印出的提示词是 CC BY-NC 4.0，代码里同一批提示词是 Apache-2.0。
13. **AI Research SKILLs 两个出想法 skill 和助理对话的关系。** 它们是交互式问答，领域知识来自研究者，不落文件；这和助理现在在对话里带着研究者走、用 `output new hypothesis` 手写的形状重叠。原样放进 `skills/` 过不了校验；改写后放通用库还是领域库、只给助理还是也给执行层（P-11，`docs/architecture/README.md:161`），平台文档没有判据。

### 假设生成与评估（假设阶段）

本节比较四个候选中与假设阶段相关的部分，四个都只借鉴。AI Scientist 与 AutoResearchClaw（下称 ARC）的主体挂在别的能力下，这里只看出想法、查新与评估这一段。「实际做到什么」一栏以深读对代码的核对为准，README 与论文摘要只当线索。

| 候选 | 实际做到什么 | 做法 | 调模型与 key | 外部服务 | 成熟度 | 许可证 | 出处 |
|---|---|---|---|---|---|---|---|
| AI Scientist（一代与二代） | 只做「提出」和「查新」，想法不在数据上检验（二代的树搜索只用在后面的实验阶段）。一代：从模板代码和种子想法出 50 条，每条在同一段对话里反思 3 轮；三个自评分全仓没有读取点。之后每条想法单开一段对话查新，最多 10 轮 S2 检索，按回复里有没有 `Decision made: novel` 这个字符串判定，只存一个布尔值 `novel`，主流程只跑判新的。二代：从一份主题 Markdown 出七字段想法，检索是循环里模型可选的一次工具调用，没有查新判定，也不过滤，由人用 `--idea_idx` 挑。两篇论文都没评估反思轮数和查新准确度；一份独立评测里 12 条想法全被判新，其中有已知做法 | 已出过的想法原文放进 prompt，要求「不同」，没有相似度计算；同一段对话反思 N 轮，用早停字符串结束；查新时模型每轮给一个检索词，读前 10 条摘要 | Python 直接调模型 API：按模型名分派 anthropic 或 openai SDK，DeepSeek、OpenRouter、Gemini 走 openai SDK 换 `base_url`，key 读环境变量；二代 2025-09-30 起可接本机 Ollama。出想法和查新用同一个模型，查新看得到想法的自评分 | Semantic Scholar `/graph/v1/paper/search`（`S2_API_KEY` 可选，没有 key 时限速）；两代的退避都不设上限，4xx 和 5xx 都会一直重试。一代可换 OpenAlex，但写作阶段取 bibtex 用不了它；二代只有 S2 | 两仓最后提交都是 2025-12-19（改许可证）；`requirements.txt` 不带版本号，没有锁文件；`git ls-files` 里没有测试文件，也没有 `.github/`（本节核对）；S2 相关的卡死 issue #78、#116、#133 没关；二代出想法脚本只依赖 anthropic、openai、backoff、requests、tiktoken | 2025-12-19 起改用 AI Scientist Source Code License 1.0（此前是 Apache 2.0）：有五类使用限制，其中一条要求用它产出的稿件显著声明是机器生成；这些限制必须写进再分发时的协议 | [ai-scientist.md#1-结论](ai-scientist.md#1-结论)、[#22-一代查新](ai-scientist.md#22-一代查新)、[#32-独立评测](ai-scientist.md#32-独立评测)、[#42-跟平台现有规矩的对照](ai-scientist.md#42-跟平台现有规矩的对照)、[#5-局限与前提](ai-scientist.md#5-局限与前提)、[#51-许可证条款要点](ai-scientist.md#51-许可证条款要点) |
| AutoResearchClaw | 只做「提出」，外加一次不影响流程的查新。Stage 8 默认让 innovator、pragmatist、contrarian 三个角色各调一次模型，再调一次合成，写出自由格式的 `hypotheses.md`（执行器只查文件非空）。可选的 debate（反驳轮加打分）和 best-of-N tournament 是 2026-08-18 加的，默认关，晚于论文。`check_novelty` 真的去三个库检索、算关键词 Jaccard，结果写进 `novelty_report.json`，生产代码里没有地方读它。Idea Workshop 的出想法、打分、细化，以及 BranchManager、IdeaPool，生产代码里都没有调用。对假设的判断只有 Stage 15 由模型判 PROCEED / REFINE / PIVOT；PIVOT 后重跑 Stage 8，输入和上一次一样。论文主表不测假设生成：评测里的假设是从 manifest 注入的 | 三个角色的提示词按领域换（ML、HEP 两套能走到），合成时要求保留分歧；只有开 debate 且配了 `reviewer_model` 时，打分和合成才拆成两次调用；查新是把假设文本的关键词和论文摘要比 Jaccard | 默认走 HTTP 接口（OpenAI 兼容、Anthropic 等），要 `base_url` 和 key，`researchclaw run` 会先预检；打分用的模型可以单独配 provider、base_url、key。provider 选 acp 时，经仓库外的 acpx 把 Claude Code、Codex 这类 CLI agent 当后端；这时 debate 的多模型和独立打分都不构建，Stage 8 的各次调用发进同一个具名会话（按代码推断，没实跑） | 查新用 OpenAlex、Semantic Scholar、arXiv；S2 key 可选，读的是 `llm.s2_api_key`；某个源失败时退到本地检索缓存 | 论文对应 v0.5.0（2026-05-20），最后提交 2026-08-19；有单测（debate 12 条、tournament 14 条、查新 37 条，都用假客户端或 mock），仓库没有 CI；Idea Workshop 的单测是绿的，但生产代码返回的类型和测试里 mock 的不一样；好几处判据算了或写了，但没有代码读 | MIT（代码和写在代码里的提示词） | [autoresearchclaw.md#11-假设这一段的链路](autoresearchclaw.md#11-假设这一段的链路)、[#13-假设评估与细化的判据](autoresearchclaw.md#13-假设评估与细化的判据)、[#15-查新怎么做](autoresearchclaw.md#15-查新怎么做)、[#22-这些证据测没测到假设这一段](autoresearchclaw.md#22-这些证据测没测到假设这一段)、[#4-局限与前提](autoresearchclaw.md#4-局限与前提) |
| SciAgentsDiscovery | 只做「提出」，外加由模型打分的查新，不在数据上检验。在一张现成的生物启发材料概念图（33,159 个节点）上取两个概念之间的一条路径，然后依次由本体学家解释路径，科学家写七字段 JSON 假设，七个字段各扩写一遍，批评者写优缺点和两个优先问题。自动版（AutoGen GroupChat）再用 Semantic Scholar 检索，由模型给 1–10 分的新颖性和可行性（自由文本，代码不解析）。批评不回到改稿。证据是 7 个案例，没有消融、没有基线、没有人工评审；附录里一条 16 个词的长查询返回 0 篇，被当成新颖打了 8 分 | 在图上跑带随机噪声的 Dijkstra（边权加噪声），再绕 4 个随机路标。论文写的 embedding 启发式和二跳邻居，在按论文参数实际走到的代码里都没用上；模型只看到一行路径字符串。七个字段的措辞绑定材料领域，不带出处，也不写证伪判据 | Python 直接调 OpenAI，模型写死 `gpt-4o`，读 `OPENAI_API_KEY`。非自动版固定 12 次串行调用；自动版经 AutoGen 0.2，带本地缓存 `cache_seed: 42`。本机还要跑 bge-large-en-v1.5 算 embedding（torch、transformers） | Semantic Scholar，只有自动版用（`SEMANTIC_SCHOLAR_API_KEY` 可以不设；深读无 key 发 8 次请求，7 次返回 429）；图和 embedding 从 Hugging Face 下载，embedding 是 pickle 格式；出 PDF 要系统装 wkhtmltopdf | 最后提交 2025-05-10，只改了 README；没有测试，没有 CI；`setup.py` 列了 35 个包，只有两个带下限，没有锁文件；`pyautogen` 不设上限，而 PyPI 上的新版已经换成另一套 API（按元数据推断，没装）；GraphReasoning 要另装；import 时就加载图和模型；换领域要重建整张图 | 代码 Apache-2.0（`setup.py` 的 classifier 写 MIT，两处不一致）；图数据 apache-2.0；期刊论文（含印出的提示词图）CC BY-NC 4.0 | [sciagents.md#11-仓库画像](sciagents.md#11-仓库画像)、[#13-图上怎么取路径](sciagents.md#13-图上怎么取路径)、[#15-输出的结构化假设字段](sciagents.md#15-输出的结构化假设字段)、[#16-用-semantic-scholar-查新](sciagents.md#16-用-semantic-scholar-查新)、[#21-论文拿什么证明](sciagents.md#21-论文拿什么证明)、[#44-许可证与数据使用](sciagents.md#44-许可证与数据使用) |
| POPPER | 不生成假设，只验证一个给定的自由文本假设，数据只能是表格。每轮流程：设计一条带 h0 / h1 的子假设；让 LLM 打相关性分，低于 0.8 就丢弃；用 ReAct 加 Python REPL 在预先载入的 DataFrame 上跑检验；再调一次 LLM 从文本里读出 p 值；p 值换算成 e 值（κ = 0.5）连乘，超过 1/α 判「验证」，否则跑到预算为止。输出只有「验证 / 未验证」两种，没有「证伪」。公共 API 返回的 True / False 是总结用的 LLM 写的，把 e 值判定写回结果的那行被注释掉了。论文表 3：α = 0.1 时一类错误 0.082–0.103，功效 0.580–0.638。另有两处读代码发现、没运行验证的问题：TargetVal 负例的置换代码按推算多数表只打乱了行序；「去掉相关性检查」这条消融的代码分支会抛 TypeError | 序贯证伪加 e 值：p 值换 e 值用的是 Vovk & Wang 的校准器，是十行 numpy、不经模型的算术；零假设之间的蕴含约束靠 prompt 里的自检，加上 LLM 相关性检查来近似；一类错误用置换数据造负例来测 | Python 经 langchain 调 API：`claude-*` 走 Anthropic（`ANTHROPIC_API_KEY`），`gpt-*` 和 `o1*` 走 OpenAI（`OPENAI_API_KEY`），其它名字当成 `127.0.0.1:<port>` 上的 OpenAI 兼容服务；ReAct 执行器只认 `claude-` 和 `gpt-` 开头的名字。默认模型是 `claude-3-5-sonnet-2024xxxx`，今天还能不能调用没查。每轮至少 4 次模型调用，另加最多 25 步执行；模型生成的代码在宿主进程里 `exec`，ReAct 这条路没有超时 | 不查文献；第一次 `register_data` 时会从 Harvard Dataverse 下载 2.27 GB 的生物数据存档，用自己的数据也会触发（issue #6、#8 没关）；`launch_UI` 会开一个 gradio 公网分享链接；PyPI 0.0.5 画图时会连 mermaid.ink | 33 个提交，最后一次 2025-05-14，没有 release；PyPI 上有 `popper_agent` 0.0.5（只有 sdist）；没有测试，没有 CI；依赖钉在 langchain 0.3.x 一代；连续调用 `validate` 不清状态等实现问题读代码可见 | 仓库里没有 LICENSE 文件；`setup.py` 和 PyPI 元数据写 MIT，包里没有许可证正文；数据存档 CC0 1.0；DiscoveryBench 是 ODC-By | [popper.md#0-仓库与论文画像](popper.md#0-仓库与论文画像)、[#15-e-值序贯检验与一类错误控制](popper.md#15-e-值序贯检验与一类错误控制)、[#22-一类错误与功效的实证](popper.md#22-一类错误与功效的实证)、[#24-证据本身的边界](popper.md#24-证据本身的边界)、[#42-模型](popper.md#42-模型)、[#44-许可证](popper.md#44-许可证)、[#46-实现层面的问题读代码得出未运行](popper.md#46-实现层面的问题读代码得出未运行) |

**平台缺的与候选补的**
平台在这个阶段缺三样。第一是「提出」：假设阶段既没有能力，也没有主文件（`platform/framework/capabilities/__init__.py:42-52` 的 `MAIN_FILES` 里没有假设这一行；纲领 P-20 写的是「假设、写作待第一个能力定名」，`docs/architecture/README.md:170`）。设计阶段现在把 `--from hypothesis/N` 目录里的文本文件原样拼进执行层的提示词，不做解析（`platform/framework/capabilities/design/__init__.py:103-108`、`platform/framework/capabilities/design/__init__.py:176`）。第二是「用数据检验假设本身」：验证阶段只有 `verify`，它不经模型，把分析稿里的数回溯到 `results.json`，再拿账本对 git（`platform/framework/capabilities/verify/__init__.py:1-7`）；分析阶段的「证伪与未决」是执行层写的自由文本（`platform/framework/capabilities/analysis/prompt.md:22`）。第三是「由模型判断假设质量」：P-2 写了由隔离的新会话来做、只给产物不给轨迹，但标明这一段尚未实现（`docs/architecture/README.md:152`）。

候选补的情况：AI Scientist、ARC、SciAgents 补的都是第一块，另外各带一种查「新不新」的做法，分别是一代的字符串布尔判定、ARC 没人读的 Jaccard 报告、SciAgents 由模型打的 1–10 分。三种查新都没有拿标准答案测过准不准，而且查的是「新不新」，不是「对不对」。只有 POPPER 补第二块，但只能用表格数据，也只给「验证 / 未验证」两种结果（[popper.md#32-部件对照](popper.md#32-部件对照)）。第三块四家都只有近似的做法，都不是 P-2 说的「框架派一个隔离的新会话」：POPPER 的相关性检查只看子假设和主假设两段文字，输入形状最接近 P-2；ARC 要开 debate 且配了 `reviewer_model`，打分和合成才拆成两次调用；SciAgents 非自动版的批评只读成稿，但和写稿的是同一个脚本里的下一次调用；AI Scientist 一代的查新新开了一段对话，但用的是同一个模型，而且看得到想法的自评分（[autoresearchclaw.md#31-可摘出的方法与落点](autoresearchclaw.md#31-可摘出的方法与落点)、[sciagents.md#3-平台哪里能用](sciagents.md#3-平台哪里能用)、[ai-scientist.md#42-跟平台现有规矩的对照](ai-scientist.md#42-跟平台现有规矩的对照)）。

和平台现有东西的重叠：

- **POPPER 与判定层、验证阶段。** 它的 e 值连乘和停止规则是不经模型的算术，对应 P-2 说的「确定性能判的用零模型代码」，和 `verify` 同属框架的判定层，但判的东西不同：`verify` 判一个数有没有出处，POPPER 判证据够不够拒绝零假设。
- **POPPER 的 p 值来源。** 它的 p 值由执行 agent 在 REPL 里自己报出来，再由 LLM 从文本里读出，这和 P-24 的「数由框架跑，不由 agent 自报」正好相反（`docs/architecture/README.md:174`）。
- **POPPER 的一轮循环与执行形态。** 「拆子假设、写检验、跑、读结果」这一轮，覆盖的是平台设计、实验、分析三个阶段已有的链路。它要交互式跑 Python，而平台执行层的 Bash 只放行 `ai4sci skill`（`platform/framework/skills/__init__.py:37`）。
- **查新与文献阶段。** 平台文献阶段的 `sources.md` 由助理用自带的搜索手写（`docs/architecture/README.md:174`），执行层联网也只用自带的搜索与网页读取（`platform/framework/executor/prompting.py:21-25`）；三家候选的查新走的都是 S2、OpenAlex、arXiv 的结构化 API，通道不同。skill 脚本联网有 `download` 这个先例。
- **ARC Stage 15 与分析阶段。** ARC 的 PROCEED / REFINE / PIVOT 和平台分析阶段的「证伪与未决」管的是同一件事，但 ARC 没有把失败带回去重新出假设（[autoresearchclaw.md#14-并行方向怎么探索怎么收敛](autoresearchclaw.md#14-并行方向怎么探索怎么收敛)）。
- **怎么调模型。** 四家都由 Python 直接调模型 API、读各自的 key；平台框架不调模型（P-1，`docs/architecture/README.md:151`），执行层是研究者自己登录的 CLI 会话（P-25，`docs/architecture/README.md:175`）。四家里只有 ARC 的 acp provider 把 CLI agent 当后端，但走这条路时 debate 的多模型和独立打分都不构建。

**讨论前要弄清的问题**
1. **假设阶段的主文件叫什么，字段要不要机器可读。** 候选的字段各不相同：AI Scientist 二代是七个文本字段，下游实验硬读其中五个；ARC 要求依据、可测预测、失败条件，但产物只查非空；SciAgents 是七个材料措辞的字段，不带出处、不写证伪判据；POPPER 每轮是 h0 / h1。平台的 `design` 现在原样读文本，分析稿的「证伪与未决」也没有假设编号可以对上（[ai-scientist.md#23-二代出想法与检索合在一个循环里](ai-scientist.md#23-二代出想法与检索合在一个循环里)、[autoresearchclaw.md#13-假设评估与细化的判据](autoresearchclaw.md#13-假设评估与细化的判据)、[sciagents.md#15-输出的结构化假设字段](sciagents.md#15-输出的结构化假设字段)、[popper.md#12-把自由文本假设拆成可证伪的子假设](popper.md#12-把自由文本假设拆成可证伪的子假设)）。
2. **「用数据检验假设」放在哪。** 可以是假设阶段里的一个步骤，按 POPPER 的形状在阶段内自带一轮「设计、执行、判定」；也可以交给设计、实验、分析、验证已有的链路，假设阶段只负责提出。选前一种，要先说清它和 `scoring.yaml`、`ledger.tsv` 是什么关系。
3. **检验里的 p 值由谁产出。** POPPER 让执行 agent 自报、再由 LLM 读出，只拦 NaN 和 0，不查取值范围。P-24 的「数由框架跑」是否同样管到假设检验？e 值累计是否归框架的判定层（[popper.md#46-实现层面的问题读代码得出未运行](popper.md#46-实现层面的问题读代码得出未运行)）？
4. **交互式跑 Python 这种执行形态在平台上怎么放。** POPPER 的执行 agent 要先看数据、再选检验，需要交互式跑 Python；平台执行层的 Bash 只放行 `ai4sci skill`。
5. **研究者手上的数据长什么样，POPPER 的保证还成不成立。** POPPER 只支持能读成 DataFrame 的表格。它一类错误的保证（定理 4）依赖三条前提，而实现里有几处空隙：设计时看得到样例行，执行时看过数据才定检验，同一张表在多轮里反复用。论文只在全部置换的负例上测过，「假设为假但数据里有混杂相关」的情形没测（[popper.md#45-方法本身的前提](popper.md#45-方法本身的前提)、[popper.md#41-数据](popper.md#41-数据)）。
6. **查新走哪条检索通道。** 一条是 S2、OpenAlex、arXiv 的结构化 API，由 skill 脚本联网（有 `download` 的先例）；另一条是助理或执行层自带的网页搜索。还要弄清：S2 无 key 的公共额度够不够用（SciAgents 深读无 key 发 8 次、7 次返回 429；AI Scientist 两代的退避都不设上限）；检索词、命中论文、判定理由落不落盘、落在哪（三家候选要么不落盘，要么落了没人读）。
7. **查新判定准不准。** 字符串布尔、关键词 Jaccard（ARC 深读按公式推算多数情况会报 high，而且只认 ASCII）、模型打的 1–10 分，三种都没有和标准答案对照过；独立评测里 AI Scientist 的 12 条想法全被判新。讨论之前，要不要先用已知工作当正例做一份小评测（[ai-scientist.md#32-独立评测](ai-scientist.md#32-独立评测)、[autoresearchclaw.md#15-查新怎么做](autoresearchclaw.md#15-查新怎么做)）？
8. **P-2 的隔离评审落地时的几件事。** 同一家 CLI、同一个模型开一个新会话，算不算隔离？评审的输入只给候选假设，还是连材料一起给？研究者的 `agents.yaml` 能不能给评审配另一家或另一个模型？要不要单独配模型 key，这里不下结论，只列为待定。
9. **多角色生成怎么落。** 三个角色用三次隔离会话，还是一次会话写三节，两种做法下角色之间的可见性不同。ARC 在 acp 下各角色进同一个会话（没实跑），可见性对产出有什么影响没有数据；ARC 论文的角色消融只有「同时去掉 Stage 8 和 Stage 14 的多角色」这一组（[autoresearchclaw.md#22-这些证据测没测到假设这一段](autoresearchclaw.md#22-这些证据测没测到假设这一段)）。
10. **领域写死的提示词在工程学科题目上表现如何。** 三家生成类提示词都写死了领域：AI Scientist 是顶级 ML 会议，ARC 是单卡 30 分钟加 ML / HEP 两套，SciAgents 是材料字段加分子建模、合成生物学两个方向。平台的领域包能补提示词，但这些提示词在课题组工程学科题目上的表现没有证据。
11. **SciAgents 的前提是一张覆盖研究者领域的概念图，平台现在没有任何领域图。** 用执行层的 CLI 会话逐块抽三元组，耗时和花费都没有数据；公开图的边追不回论文，想要能引用，就得在建图时留下来源；中文材料还要换 embedding 模型（[sciagents.md#18-换一个领域要重建什么](sciagents.md#18-换一个领域要重建什么)）。
12. **分析稿的「证伪与未决」要不要作为重新出假设的可选输入**（`--from analysis/N`）。ARC 在 PIVOT 后重跑时输入不变，可以当反面参照。
13. **人在哪一步介入假设。** ARC 的人工意见在 Stage 8 跑完之后才到，改不到这一次的产物。平台上人要改假设，是在签字前退回去重跑，是改需求，还是用 `ai4sci output new` 手写一份假设产出（P-1 允许助理手写材料清单这类东西，假设算不算在内）？
14. **许可证。** AI Scientist 新许可证的使用限制和强制披露要写进再分发的协议：照方法重写、照抄提示词原文、用改许可证之前的 Apache 2.0 提交，分别算不算衍生作品？POPPER 仓库没有 LICENSE 文件，元数据里写的 MIT 算不算授权？SciAgents 期刊版印出的提示词图是 CC BY-NC 4.0，而同一批提示词随代码是 Apache-2.0，按哪个算（[ai-scientist.md#51-许可证条款要点](ai-scientist.md#51-许可证条款要点)、[popper.md#44-许可证](popper.md#44-许可证)、[sciagents.md#44-许可证与数据使用](sciagents.md#44-许可证与数据使用)）？
15. **「提出」和「检验」是一个能力还是两个。** 候选里没有一家两件都做：三家只提出，POPPER 只检验。P-18 允许一个阶段挂几个能力，而 P-20 规定进这个阶段的能力都要留下同一个主文件。

### 论文写作（写作阶段）

候选是 #157 列的三个：Academic Research Skills（ARS，#183）、Nature Skills（#186）、AI Research SKILLs（#189）。K-Dense 的主体挂在文献检索（#161），这里只比它和写作相关的几个 skill：`scientific-writing`、`citation-management` 深读过；`venue-templates`、`scientific-schematics`、`peer-review` 深读只做了统计，没有逐行读。四个候选有一点相同：都没有框架侧代码，也都不是「步骤」形态。正文由宿主 agent 读了提示词自己写；脚本只做检查、格式转换、检索和出图。

| 候选 | 实际做到什么 | 做法 | 调模型与 key | 外部服务 | 成熟度 | 许可证 | 出处 |
|---|---|---|---|---|---|---|---|
| ARS | academic-paper 有 11 个模式（plan、full、revision、abstract-only、citation-check、format-convert 等），流程从 Phase 0 配置访谈走到 Phase 7 排版，产出 MD、DOCX、LaTeX、PDF、双语摘要和 AI 使用声明；reviewer 做模拟审稿和回复信。确定性的只有这几支脚本：缩写检查、修订补丁应用、投稿包校验、PDF 页数预检。「诚信闸门」「Style Calibration」「Writing Quality Check」「防泄漏」「VLM 图表核对」都是提示词。四索引引用存在性闸门是真代码，但提示词里找不到调用它的命令；`ARS_CLAIM_AUDIT` 没有代码读取。作者自己的能力矩阵共 16 行，其中 10 行 NOT_RUN（起草、论断核对在内） | 是一个 Claude Code 插件：约 4.4 万行提示词、39 个角色，默认在同一个会话里 inline 依次执行。每个阶段停下来等用户下一回合。运行时脚本放在仓库根 `scripts/`，没有 PEP 723，脚本之间互相 import。Codex 版在另一个仓（3.22.0），代码没读 | 用当前会话的模型；13 条命令在 frontmatter 里写死 `model: sonnet`。第二模型可选：OpenAI 或 Gemini 的 key，或 Codex 订阅（只用于引用核对），调用方式是提示词里写好的 curl。编排提示词里还有一道标「不可跳过」的 v3.6.7 审计闸门，要人在会话外用 Codex CLI 跑；用户文档没提它，实跑时会不会拦下，未验证 | 会话自带的 WebSearch / WebFetch，实际离不开；Semantic Scholar、OpenAlex、Crossref、arXiv，不要 key；Pandoc、tectonic 可选；不用 MCP | 45 个 release；798 个提交，约 96% 出自维护者一人；约 7066 个离线测试，多数是钉住提示词文本的 lint；外部结果证据 16 行全是 none | CC BY-NC 4.0，覆盖全部代码；作者自称 source-available | [深读](academic-research-skills.md)：[1.2](academic-research-skills.md#12-readme-说的能力代码里是什么)、[2.2](academic-research-skills.md#22-主流程与人确认点)、[2.3](academic-research-skills.md#23-怎么调模型)、[4](academic-research-skills.md#4-跑起来要什么)、[6](academic-research-skills.md#6-成熟度) |
| Nature Skills | `nature-writing`（标 Draft）和 `nature-polishing`（标 Stable）是纯提示词，默认产出是对话里的回复（初稿、大纲、论断—证据表等六段，缺证据的地方写占位）。用户要 `.tex` 时，writing 填 4 个初投稿 LaTeX 模板；润色遇到排版请求，直接改用户的 `.tex`。`nature-figure` 让 agent 自己写 matplotlib 或 ggplot2 代码并运行；仓库带 5 个 CSV 模板和约 2850 行 QA 脚本，其中对齐审计、碰撞审计不过就不许交付。引用方面，`nature-citation` 按段查 CrossRef，只留 Nature/CNS 期刊族，导出 RIS；`nature-ref-verifier` 标 Stable，但零代码。`nature-shared` 里有一个脚本，查术语变体、同值不同精度和长度单位 | 20 个 agentskills.io 目录。router 型 SKILL.md 让 agent 自己读 `manifest.yaml`，按轴挑 `static/` 里的片段，还要读 `../nature-shared/`；没有任何运行时代码解析 manifest | 没有调用文本模型的代码，文本全由宿主 agent 写；figure 的 AI 示意图要 `OPENROUTER_API_KEY`（默认 `openai/gpt-image-2`，可以换成 OpenAI 兼容端点） | CrossRef（citation 用）；OpenRouter（示意图用，文档自己写了未经允许不发稿件内容）；Python（matplotlib、numpy、PyMuPDF，只声明了 PyMuPDF）或 R | 0 个 release，没有 CHANGELOG；写作、润色的行为没有一个执行过的测试，只有字符串断言；skill 工具那条 CI 从 09-16 起在 main 上连续失败，citation、figure 等 9 个测试步骤被跳过 | Apache-2.0，个别目录是 MIT；figure 下的 `figures4papers/`（约 28 MB）上游没有许可证，说明文件写明不授权复制和再分发 | [深读](nature-skills.md)：[1.1](nature-skills.md#11-二十个目录逐个对账)、[2.3](nature-skills.md#23-数据怎么进出)、[2.4](nature-skills.md#24-写作侧三个重点-skill)、[4.2](nature-skills.md#42-模型key-与外部服务)、[6](nature-skills.md#6-成熟度) |
| AI Research SKILLs | `ml-paper-writing` 带 6 个 ML 会议的 LaTeX 模板（44 个文件，是会议样式文件的拷贝；NeurIPS 那份开了 `final` 选项，还写死了作者），另有写作方法清单和 5 条工作流。README 说的 citation verification 只是 references 里一段示范 Python：取检索结果第一条、`verify` 先无条件记一个来源、三处 `except: pass`、核不上照样返回 BibTeX。`academic-plotting` 给数据图的样式模板和选图型判断表；架构图工作流写死 Gemini，出 PNG。另外两个写作 skill（系统会议模板、会议报告）没有深读 | 98 个 skill 没有一个带 `scripts/`。内容是 Markdown 正文加可复制的代码片段，agent 照着自己 `pip install`、`cp -r`、`latexmk` | 文本由宿主 agent 写；架构图要 `GEMINI_API_KEY`（`gemini-3-pro-image-preview`），把它改成走 OpenRouter 的 PR #71 没合；Semantic Scholar key 可选 | Semantic Scholar、Crossref、arXiv、doi.org；Exa MCP 可选；Google Generative Language API；TeX Live | 零测试；CI 只核 skill 总数；2026-06-16 以后没有提交；维护者说 skill 内容「只验证了一部分」 | MIT；模板目录里 `natbib.sty` 等文件是 LPPL，会议样式文件本身没有许可声明 | [深读](ai-research-skills.md)：[1.2](ai-research-skills.md#12-论文写作两个)、[2.3](ai-research-skills.md#23-引用核对的示范代码)、[2.4](ai-research-skills.md#24-academic-plotting)、[4](ai-research-skills.md#4-跑起来要什么)、[6](ai-research-skills.md#6-成熟度) |
| K-Dense（只看写作相关部分） | `scientific-writing` 不起草正文，做的是台账和校验：脚手架生成 7 个文件（`manuscript.md`、`claims.csv`、`source_manifest.json` 等），另有 9 个离线校验脚本。规则是：每条论断要挂证据号，证据要同时满足 `status: verified` 和 `source_opened: true`；没挂论断号的数字直接报错；lint 查夸大和因果措辞；`check_references.py` 只查 DOI / PMID / ISBN 的格式，不联网。这些字段是人填的还是 agent 填的，脚本分不出来；论断哈希只查格式。`citation-management` 把 DOI 转成 BibTeX，`validate_citations.py` 查 DOI 能不能解析、BibTeX 格式对不对，不比对标题和作者 | 按 agentskills.io 格式写的说明文档加脚本，agent 在 shell 里跑 `python3 scripts/x.py` | 仓库不调文本模型。scientific-writing 不要 key，测试里禁止联网；citation-management 的 `NCBI_API_KEY` 等可选；配图（`scientific-schematics`，以及 literature-review 里写成「强制」的配图）要 `OPENROUTER_API_KEY` | citation-management 连 OpenAlex、PubMed、Crossref、DataCite、doi.org、arXiv 和 Google Scholar（经 `scholarly`）；scientific-writing 不连任何服务 | 106 个 release。CI 只跑 20 个纯标准库 skill 的测试，scientific-writing 在里面，citation-management 不在；规范校验和测试 2026-07 下旬才加进 CI。论文写明没有任务级评测。136 个 SKILL.md 末尾有一节，让 agent 往稿子里加 K-Dense 论文的引用 | MIT；同仓的 `pdf` `docx` `pptx` `xlsx` 四个 skill 是 Anthropic 专有条款 | [深读](k-dense-skills.md)：[1.2](k-dense-skills.md#12-166-个-skill-按领域)、[2.5](k-dense-skills.md#25-database-lookup-与-citation-management)、[2.6](k-dense-skills.md#26-scientific-writing)、[3.4](k-dense-skills.md#34-scientific-writing-重做删模板断网)、[6.1](k-dense-skills.md#61-测试与-ci-实际测什么)、[6.4](k-dense-skills.md#64-许可证条款要点) |

**平台缺的与候选补的**

平台在写作阶段现在什么都没有。没有步骤能力，也没有主文件：`MAIN_FILES` 里没有写作这一行（`platform/framework/capabilities/__init__.py:43-52`）。接法文档用 `draft.md`、`figures/`、`refs.bib` 举过例子，但没有落地（`platform/docs/add-a-capability.md:142-151`）。助理只能用 `ai4sci output new writing` 手写（`platform/coordinator/README.md:64`）。平台代码里也没有写作、润色、绘图、引文核对或参考文献导出相关的内容（[nature-skills.md](nature-skills.md#51-平台这三个阶段现在有什么)）。#32 开着的三件事是：一次调用还是分节调用、模板用什么格式、图的生成边界在哪；#32 里的一个候选方案是写完后过三条零模型判据（数字回溯、引用真伪、图源）。下面按块对照候选：

- **起草与润色的写法**：四个候选都有，形态都是给宿主 agent 读的文字。ARS 是完整流程加角色，在一个交互会话里走完；Nature 按论文类型、章节、语言、期刊分片段；AI Research SKILLs 是一份 ML 会议写作清单；K-Dense 是论断—证据台账的规矩。平台现在同样是 agent 写稿，候选多给的是写法，谁来写没有变。四个都没法原样放进平台的 skill 库。ARS 的四个 SKILL.md 各报两处不合规（[academic-research-skills.md](academic-research-skills.md#53-接进来会碰到的平台规则)）。Nature 的 writing、polishing 能单独通过校验，但它们引用的 `nature-shared` 自己通不过，而库里只要有一个不合规，整库都报错（[nature-skills.md](nature-skills.md#53-格式规范它自己的校验器平台三方对照)）。AI Research SKILLs 多了四个规范外的字段，`ml-paper-writing` 正文 974 行，超过 500 行上限（[ai-research-skills.md](ai-research-skills.md#53-会碰到的平台规则)）。K-Dense 的脚本没有 PEP 723 和锁文件（[k-dense-skills.md](k-dense-skills.md#53-接进来会碰到平台哪些现有规则)）。
- **模板与排版**：ARS 的 formatter 用 Pandoc 出 DOCX、用 tectonic 出 PDF；Nature 带 4 个初投稿模板和 3 个返修模板；AI Research SKILLs 带 6 个 ML 会议模板和 4 个系统会议模板；K-Dense 的 `venue-templates` 没深读。四家都要 agent 自己拷模板，自己跑 `latexmk`、`pandoc` 或 `tectonic`。平台执行层在 Claude Code 上只放行 `Bash(ai4sci skill *)` 和工作目录内的 Read（`platform/backends/claude_code.py:151-155`）；在 Codex 上，`ai4sci` 以外的命令都在断网的沙箱里跑。对系统命令，平台只有一个探测键 `ai4sci-system-tools`（`platform/framework/skills/library.py:33-35`）。
- **配图**：平台的分析能力写明「不画图」，还说「作图是这个阶段里另外的能力」（`platform/framework/capabilities/analysis/__init__.py:29-32`）。#32 里的候选方案是：图由工具从 `results.json` 和账本确定性生成，执行层只引用、不画。候选里，Nature figure 是 agent 写代码出图，再加确定性 QA 卡住交付；模板缺 `--input` 就报错，只有加 `--demo` 才用模拟数据。AI Research SKILLs 只给样式模板，允许数据来自一段话或内联数组，它的演示图用的是合成数据。ARS 的 VLM 核对是可选的提示词。三家的 AI 示意图都要单独的图像 key（OpenRouter 或 Gemini）。没有一个候选把图里的数和 `results.json` 绑在一起（[nature-skills.md](nature-skills.md#24-写作侧三个重点-skill)、[ai-research-skills.md](ai-research-skills.md#24-academic-plotting)）。
- **引用核对**：`verify` 只读 `analysis.md`，不查引用（`platform/framework/capabilities/verify/__init__.py:34-44`）。候选里确定性的部分有：ARS 的四索引存在性闸门（运行时由谁调用，未弄清）、撤稿信息归一化、引用锚点格式检查；K-Dense 查 DOI 能不能解析和 BibTeX 格式；Nature 按 CrossRef 检索并导出；AI Research SKILLs 只有一段有缺陷的示范代码。「论断有没有被引文支持」这件事，四家都没有确定性判定：ARS 是让模型当 judge 的提示词流程，默认关闭；Nature 的 ref-verifier 零代码；K-Dense 靠人或 agent 填 `verified` 字段。这一块对应 P-2 里「需要模型判断的，由框架派隔离的新会话」那一段，平台还没实现（`docs/architecture/README.md:152`）。见 [academic-research-skills.md](academic-research-skills.md#13-诚信闸门与引用核对哪些是脚本哪些是提示词)、[k-dense-skills.md](k-dense-skills.md#25-database-lookup-与-citation-management)。
- **稿子里的数字**：平台的 `verify` 把 `analysis.md` 里的数回溯到 `results.json`。候选里，K-Dense 要求每个数字挂论断号，只检查台账内部是否一致；Nature 查同一个值有没有写成不同精度；ARS 在修订轮做数字守恒检查，只给提示。没有候选把稿子里的数回溯到 `results.json`，这一块候选补不上，离它最近的是平台现有的 `verify`（[k-dense-skills.md](k-dense-skills.md#26-scientific-writing)）。
- **人确认与审稿**：平台的确认靠 `signed.json`，助理会话里调签字一律被拒。ARS 的检查点靠交互会话等用户下一回合，而平台执行层是一次性的 `claude -p` / `codex exec`，会话里没有用户回合。K-Dense 的 `submission_ready`、`verified_by` 只是 JSON 字段。模拟审稿方面，ARS reviewer 默认在同一会话里 inline 执行；Nature reviewer 要求宿主另开独立上下文；K-Dense 的 `peer-review` 是离线脚本，没深读。平台的模型评审还没实现（[academic-research-skills.md](academic-research-skills.md#52-重叠的部分)、[nature-skills.md](nature-skills.md#54-接进来会碰到的平台规则)）。

**讨论前要弄清的问题**

1. 写作主文件叫什么，是一个文件还是一组。各候选现在的做法：ARS 是 `phase4_*/draft.md`，再加 `phase7_*/paper.md`、`paper.tex`、`references.bib`；Nature 默认不落文件；AI Research SKILLs 的主文件名随会议模板变；K-Dense 是 `manuscript.md` 加 `claims.csv` 和五份 JSON。平台接法文档里的例子是 `draft.md`、`figures/`、`refs.bib`。按 P-20，这个名字由第一个进来的能力定（`docs/architecture/README.md:170`）。
2. #32 选一次调用还是分节调用，先要知道一次执行层会话能写到哪一步。执行层默认上限是 `--max-turns 30`、`--max-budget-usd 2.0`（`platform/backends/claude_code.py:159-163`）；ARS 全流程估计要 20 万以上输入 token、10 万以上输出 token，花 2.8 到 7 美元。Nature 和 AI Research SKILLs 的写作提示词都假设是多轮对话（先确认再写，或先交初稿再改）。单节和全文在默认上限下各能走到哪，没测过（[academic-research-skills.md](academic-research-skills.md#4-跑起来要什么)）。
3. 执行层能不能读到 skill 目录里正文以外的文件，也就是 `manifest.yaml`、`static/`、`references/`、`templates/`、`../nature-shared/`。`ai4sci skill show` 只打印正文、目录路径和 references 的文件名；Claude Code 执行层的 Read 只放行工作目录（`platform/backends/claude_code.py:154`）。实际读不读得到，没实测（[nature-skills.md](nature-skills.md#7-还没弄清的问题) 第 3 条、[ai-research-skills.md](ai-research-skills.md#7-还没弄清的问题) 第 6 条）。
4. `latexmk`、`pandoc`、`tectonic`、`Rscript`，以及 agent 自己写的绘图脚本，在平台里从哪个入口运行。它们都不在执行层白名单里，平台对「编译」「出图」这类系统命令还没有先例；Codex 沙箱里有没有能用的 Python 和 TeX，也没实测。
5. 图的边界：数据图是否必须从 `results.json` 和账本生成（#32 的候选方案）；作图归分析阶段还是写作阶段（分析描述符说作图是分析阶段里另外的能力）；要调图像模型的示意图算不算在内。
6. 单独的模型 key 放在哪、怎么算。示意图用的 OpenRouter / Gemini key、ARS 的第二模型 key、Codex 审计凭据，都在研究者的 agent 登录之外。`agents.yaml` 没有第三方 key 的位置，而两家适配器和 skill 脚本都会继承服务进程的全部环境变量。「skill 脚本拿单独的 key 调模型」在 P-1 下怎么算，纲领没写（[ai-research-skills.md](ai-research-skills.md#53-会碰到的平台规则)）。
7. 引用核对放在哪个阶段、判到哪一层。存在性（DOI 或索引查不查得到）可以不经模型判；「论断有没有被引文支持」四家都要靠模型或人。这一层是不是等 P-2 的隔离评审建起来再做？ARS 的四索引闸门运行时由谁调用，要看 #185 的实测记录。
8. 许可证的边界。ARS 的 CC BY-NC 4.0 覆盖代码：随平台分发、有外部资助或企业委托的课题，算不算非商业使用，需要法律意见。Nature 的 `figures4papers/` 不授权再分发；AI Research SKILLs 模板里的会议样式文件没有许可声明（[academic-research-skills.md](academic-research-skills.md#63-许可证条款要点)、[nature-skills.md](nature-skills.md#64-许可证)）。
9. 「引用本库」段落放进平台后，agent 会不会照做。K-Dense 的 136 个 SKILL.md 指示 agent 往稿子里加 K-Dense 论文的引用；AI Research SKILLs 的 `ml-paper-writing` 也有同类一节，但没有直接指示 agent 去加。平台的执行层或助理读到后会不会照做，没测。
10. 课题组的目标期刊和写作语言是什么。ARS 的双语摘要只注册了繁体中文—英文；Nature 按 Nature 系列期刊分轴，其中一部分规则是从语料归纳的，不是期刊官方要求；AI Research SKILLs 按 ML 和系统会议写。这类写作 skill 按 P-11 该进通用库还是领域包，平台没有判据。
11. 写得好不好，目前没有数据。四家都没有执行过的写作质量评测：ARS 的起草一项是 NOT_RUN，Nature 只有 6 条短请求的观察记录，AI Research SKILLs 零测试，K-Dense 的论文没有任务级评测。ARS 和 Nature 的实测挂在 #185、#188。
12. 执行层用哪一家，候选的表现差多少。ARS 的完整机制只在 Claude Code 插件渠道里有，Codex 版在另一个仓，版本落后，代码没读；Nature 在 Codex 上是插件市场，在 Claude Code 上没有插件。平台两家都要能接（P-25），两个渠道之间差多少，没比过。
13. 子代理能不能开。ARS 的多角色、Nature reviewer 的互盲，都靠宿主开子代理或另开上下文。Claude Code 执行层的 `--allowedTools` 里没有子代理工具；Codex 能不能开，没实测（[nature-skills.md](nature-skills.md#7-还没弄清的问题) 第 9 条）。

## 讨论前要弄清的问题

每类能力特有的问题在[横向比较](#横向比较)各节末尾。下面是几类都会碰到的，讨论时先回答这些。

1. **三个阶段的产物落在哪。** 文献阶段的主文件是 `sources.md`，没有一个候选产它；检索结果、阅读笔记、综述和它是什么关系。假设、写作两个阶段的主文件还没定名（P-20），要不要带机器可读的字段，好让下游按编号对上。
2. **谁来调模型。** 让宿主 agent 读说明、脚本只做确定性工作，还是允许工具自己调模型接口。P-1 的判据只查 `framework/`，纲领没写 skill 脚本能不能调模型；单独的模型 key 由谁出，花费怎么和 P-25「报不出美元记 NaN」的记法并存。
3. **MCP。** 两个检索候选的主要形态是 MCP；平台两家适配器起会话时都清空 MCP（`platform/backends/claude_code.py:39`、`platform/backends/codex.py:118`），纲领里没有专门一条。先弄清这是隔离的实现细节，还是有意划的边界。
4. **执行层能做什么。** 执行层只放行 `ai4sci skill` 这一个命令前缀（`platform/framework/skills/__init__.py:37`）。候选普遍要 agent 直接跑 python、latexmk、pandoc，读 skill 目录里正文以外的文件，或者开子代理；这些在两家执行层里能不能做到，还没实测。
5. **接法。** 依赖上游包、把代码拷进来改、只照方法与接口手册自己写，三种各要处理什么。上游停更、单人维护、CI 红、PyPI 版落后 main 的情况下，用上游代码是不是等于自己维护一份。
6. **核对做到哪一级。** 没有一个候选用不经模型的方式核对「这句话是否被所引原文支持」，能做的都靠模型或人；P-2 的隔离评审还没实现。存在性检查（键存在、DOI 能解析）与支持性判断各放在哪个阶段、由谁判。
7. **失败怎么算。** 多个候选把请求失败吞成空结果或只打 warning。检索返回 0 条时怎么区分「真没有」和「请求失败」，P-7 在这里的判据是什么。
8. **网络与数据源。** 校园网到 arXiv、Semantic Scholar、OpenAlex 这些接口通不通，不带 key 的限额够不够；数据源的 key 与 email 放在哪；Sci-Hub、抓 Google Scholar 网页这类来源的合规边界。
9. **许可证。** 平台 `pdf` skill 已在用的 PyMuPDF 系列是 AGPL-3.0；候选还涉及 PolyForm Noncommercial（pymupdf-layout）、CC BY-NC 4.0（Academic Research Skills，覆盖代码）、AI Scientist 自有许可证（有使用限制与强制声明）、POPPER 没有 LICENSE 文件。平台怎么分发，决定这些各有什么影响。
10. **课题组的实际需求。** 学科、论文语言（候选大多没有中文的测试或数据源）、一次读多少篇、目标期刊。这几条要问课题组，李瑞彬作为真实用户可以先答。
11. **效果与花费。** 研究组 8 个的实测 issue（#160、#163、#166、#169、#172、#185、#188、#191）都还开着，效果与花费没有一个是测出来的。

## 怎么做的

1. 18 个仓库按 README、许可证、最近提交分三组，结果见[取舍](#取舍)。
2. 13 个仓库浅克隆到外层 `vendor/`（gitignore），提交号钉在各篇 scope 里；只读代码，不装依赖、不跑项目代码。需要的论文下载到外层 `materials/`。
3. 一个项目一个会话读代码写深读，按项目 issue 里的问题组织：研究组七问（是不是、怎么做、为什么、跑起来要什么、和平台对照、成熟度、还没弄清的），只借鉴组五问（方法、为什么有效、平台哪里能用、局限、还没弄清的）。
4. 每篇由另一个没参与写作的会话复查：逐条打开 `文件:行` 核对、对 README 说法去代码里确认、独立重搜最关键的否定判断、补没答到的问题、删掉接不接的结论。每篇的改动数见下表。
5. 一类能力一个会话读相关深读做横向比较，只摆事实与要弄清的问题，不做选择。

| 项目 | 复查改动 | 复查补答 |
|---|---|---|
| [PaperQA2](paperqa2.md) | 30 | 8 |
| [K-Dense Scientific Agent Skills](k-dense-skills.md) | 25 | 12 |
| [arxiv-mcp-server](arxiv-mcp-server.md) | 19 | 12 |
| [Paper Search MCP](paper-search-mcp.md) | 25 | 17 |
| [GPT Researcher](gpt-researcher.md) | 19 | 10 |
| [STORM](storm.md) | 26 | 14 |
| [AI Scientist（一代与二代）](ai-scientist.md) | 15 | 11 |
| [AutoResearchClaw](autoresearchclaw.md) | 22 | 9 |
| [SciAgentsDiscovery](sciagents.md) | 25 | 10 |
| [POPPER](popper.md) | 15 | 10 |
| [Academic Research Skills](academic-research-skills.md) | 23 | 12 |
| [Nature Skills](nature-skills.md) | 23 | 13 |
| [AI Research SKILLs](ai-research-skills.md) | 29 | 9 |
