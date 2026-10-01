---
title: PaperQA2 代码级深读
subtitle: 科研 AI 能力选型 · 文献阶段候选 · 带引用的文献问答：README、论文与代码逐条对账
kind: 开源项目选型深读（只读代码，不跑、不装依赖）
date: 2026-09-27
scope: 仓库 https://github.com/Future-House/paper-qa，浅克隆到 vendor/paper-qa，提交 57e89f7（即 tag v2026.08.12，2026-08-12，也是 main 当前最新提交）；读了 src/paperqa 全部、packages/ 四个 PDF 读取器的入口与许可证、tests/、CI；依赖 fhlmi 按 uv.lock 锁定的 v0.45.0 读了 llms.py、embeddings.py、rate_limiter.py；论文 arXiv 2409.13740（PDF 存外层 materials/，不进 git）。文中不带前缀的 `文件:行` 相对 paper-qa 仓库根；平台一侧的路径相对外层仓根，以 docs/ 或 platform/ 开头
status: 第一版
---

> **结论先行**：代码里的 PaperQA2 是一个 Python 库加 `pqa` 命令行：先把**本机一个目录**里的论文建成 tantivy 全文索引（每篇解析、定长切块、算好嵌入后整篇 pickle 存盘），然后一个工具调用循环的智能体在五个默认工具间来回：本地关键词搜论文、对搜进来的论文块做向量召回再逐块让模型「摘要加打分」（RCS）、按分数取前几条生成答案、清空已收证据、结束。答案里的引用是模型抄的 `pqac-xxxxxxxx` 短键，事后被换成「作者年份 pages 页码」并生成参考列表，本次收集的证据里没有的键直接删掉。`src/` 约 1.2 万行 Python，Apache-2.0。
>
> **README 与论文说的，代码里真有的**：RCS、引用键绑定、按设置哈希命名的增量索引、Crossref 加 Semantic Scholar 加期刊分级的元数据补全、图表多模态、四个 LLM 槽经 litellm 可换、嵌入槽另可用本地 sentence-transformers 或纯稀疏。**只在 README 或论文里、代码里没有或只接了一半的**：论文里「超人表现」用的是作者机构内部的服务，论文 §8.1 自己写明开源仓不含 Grobid 解析、非本地全文检索和引用遍历工具，仓里也没有可跑的 LitQA2 评测；README 说的「元数据进嵌入」实际是进 RCS 的 prompt；Quickstart 说的撤稿检查不在默认路径上；搜索工具收年份参数但不过滤；post prompt 看不到答案还会把答案覆盖掉；README 示例里的 `Settings(paper_directory=...)` 被静默忽略；`tier*_limits` 的限速表对默认模型名不生效，而且这几份文件还顺带改了证据条数、块大小等参数，README 没说。
>
> **怎么调模型**：框架自己调模型接口，LLM 调用全部经 litellm（嵌入另有不经 litellm 的本地选项），要环境变量里的 API key 或本地端点。五个槽位（llm、summary_llm、agent_llm、enrichment_llm、embedding）默认全是 OpenAI（`gpt-4o-2024-11-20` 与 `text-embedding-3-small`）。换 Anthropic 要改四个模型槽，嵌入另找一家或用本地；它用不了 Claude Code / Codex 的命令行登录。
>
> **成熟度**：有 CI（CI 里带真 key 调 OpenAI、Anthropic、Gemini 等），237 个测试函数，CalVer 发版；2026-04 以后 main 只有 4 个提交，之后的推送只有依赖机器人在分支上的锁文件更新。与平台的对照只列事实，见[第 5 节](#5-和平台对照)；还没弄清的见[第 7 节](#7-还没弄清的问题)。横向对比见同目录的 [README.md](README.md)。

## 1. 是不是

### 1.1 README 能力逐条对账

| README 说 | 代码里 | 对得上吗 | 证据 |
|---|---|---|---|
| 回答带文内引用（`README.md:110`） | qa prompt 要求句末用 `pqac-xxxxxxxx` 键并给正反例；后处理把键换成块名、生成参考列表、删掉 `session.contexts` 里没有的键（对照的是本次收集到的全部证据，不只是进了回答 prompt 的那几条） | 对得上。只校验「键存在」，不校验句子是否被那条证据支持 | `src/paperqa/prompts.py:38-69`、`src/paperqa/types.py:474-526`、`src/paperqa/utils.py:191-194` |
| 「嵌入感知文档元数据」（`README.md:111`） | 嵌入的文本只有块正文加可选的图片描述；引用数、期刊分级、撤稿标记进的是 RCS 的 prompt 和回答上下文里的 citation 字符串 | 部分：元数据在 prompt 里，不在嵌入里 | `src/paperqa/types.py:208-235`、`src/paperqa/docs.py:371-386`、`src/paperqa/docs.py:560-563`、`src/paperqa/types.py:1216-1239`、`src/paperqa/prompts.py:164-167` |
| LLM 重排与上下文摘要 RCS；算法表第 2 步「用 LLM 重打分并挑选」（`README.md:111-112`、`README.md:234-236`） | 每个候选块一次 summary_llm 调用，返回 JSON 摘要和 0–10 分；「重排」就是按这个分排序截断，没有第二次调用 | 对得上，打分与摘要是同一次调用 | `src/paperqa/core.py:178-400`、`src/paperqa/docs.py:551-585`、`src/paperqa/settings.py:1214-1224` |
| 智能体可反复改写检索（`README.md:113`） | aviary `ToolSelector` 循环，默认工具 paper_search、gather_evidence、gen_answer、reset、complete | 对得上 | `src/paperqa/agents/main.py:259-323`、`src/paperqa/agents/tools.py:702-712` |
| 多个来源冗余抓元数据，含引用数与期刊质量（`README.md:114-115`） | 默认客户端 Crossref、Semantic Scholar、期刊分级表；OpenAlex、Unpaywall、撤稿只在 `ALL_CLIENTS` | 对得上（默认三个） | `src/paperqa/clients/__init__.py:26-36` |
| Quickstart：拿元数据「含撤稿检查」（`README.md:71-74`） | 撤稿处理器不在默认客户端里；建索引调 `aadd` 时没传 `clients`，走默认 | 默认路径不查撤稿 | `src/paperqa/clients/__init__.py:26-30`、`src/paperqa/docs.py:267-273`、`src/paperqa/agents/search.py:522-530` |
| 本地论文库的全文检索引擎（`README.md:116`） | tantivy 索引，字段 file_location、body、title、year；每篇的解析结果（含嵌入）以 zlib 压缩的 pickle 存盘 | 对得上 | `src/paperqa/agents/search.py:113-434`、`src/paperqa/agents/search.py:622-718` |
| 支持所有 LiteLLM 模型（`README.md:117`） | 所有调用经 `lmi.LiteLLMModel` 进 `litellm.Router` | 对得上；但 README 的本地示例漏设槽位（见 [2.7](#27-怎么调模型)） | `src/paperqa/settings.py:925-960` |
| Paper Search：「用 LLM 生成的关键词找候选论文」（`README.md:231-232`） | 只查本机索引；工具接收 `min_year`、`max_year`，拼成字符串后只用作续查的键，查询时把 year 字段排除，不做年份过滤 | 部分：年份过滤没接上（代码里有 TODO） | `src/paperqa/agents/tools.py:155-182`、`src/paperqa/agents/main.py:235` |
| `k` 个「最相关且多样」的段落（`README.md:757-758`） | MMR 的 λ 默认 1.0，λ≥1 时直接返回相似度排序 | 默认不做多样化 | `src/paperqa/settings.py:804-806`、`src/paperqa/llms.py:144-145` |
| post prompt 可用来批评答案；速查表说它能访问 PQASession 字段（`README.md:1119-1123`、`README.md:1030`） | 校验时允许任何 PQASession 字段名，执行时只填 `question`；执行后把原答案丢掉，并把 post 的输出拼了两遍 | 没接对。测试只断言输出里有 "up"，覆盖不到这两点 | `src/paperqa/settings.py:488-498`、`src/paperqa/docs.py:694-711`、`tests/test_paperqa.py:2650-2659` |
| `prompts.select` 选论文模板（`README.md:1028`） | 定义并校验了变量，全仓没有读取点 | 死设置 | `src/paperqa/settings.py:423`、`src/paperqa/settings.py:476-486` |
| 库用法示例 `Settings(temperature=0.5, paper_directory="my_papers")`（`README.md:410-413`） | `Settings` 是 `extra="ignore"`，这个字段实际在 `agent.index.paper_directory`；顶层写法被静默丢弃，退回当前目录。出厂的 `openreview.json` 也是这个写法 | 示例不生效 | `src/paperqa/settings.py:750-751`、`src/paperqa/settings.py:530-535`、`src/paperqa/configs/openreview.json:19` |
| 出厂设置 high_quality「evidence_k = 15」（`README.md:362`） | 文件里是 20；`pqa` 不带 `-s` 时默认就用 high_quality | 数字不符 | `src/paperqa/configs/high_quality.json:3`、`src/paperqa/agents/__init__.py:176-183` |
| `tier1_limits`…`tier5_limits` 按 OpenAI 档位限速（`README.md:367-379`） | 限速表的键是 `gpt-4o`、`gpt-4o-2024-08-06` 等；默认模型 `gpt-4o-2024-11-20` 不在表里。lmi 按模型名取限速，取不到时落到每分钟 3 万 token 的兜底值。另外这几份文件不只是限速：tier1 把 `evidence_k` 改成 5、`answer_max_sources` 3、关掉元数据补全；tier2–5 把块大小改成 7000、`evidence_k` 改成 8–15。测试 `test_settings_model_config` 只断言配置里有 `gpt-4o` 这个键 | 静态推断：对默认模型，这几个档位都等于 3 万 token/分钟，未跑；README 没说这些文件会改检索参数 | `src/paperqa/configs/tier1_limits.json:1-32`、`src/paperqa/configs/tier2_limits.json`…`tier5_limits.json`、`tests/test_agents.py:819-845`；lmi `packages/lmi/src/lmi/llms.py:864-870`、`packages/lmi/src/lmi/rate_limiter.py:38,66`[^lmi] |
| 多模态：图表随页解析，生成描述只改嵌入不进引文正文（`README.md:801-845`） | 解析时每张图调 enrichment_llm 写描述，判为 IRRELEVANT 的图丢掉；描述只拼进嵌入文本；RCS 时图片作为多模态输入 | 对得上 | `src/paperqa/settings.py:1051-1193`、`src/paperqa/types.py:208-235`、`src/paperqa/core.py:233-269` |
| 可换外部向量库 Qdrant（`README.md:698-699`） | `QdrantVectorStore` 存在，默认 `NumpyVectorStore` | 对得上 | `src/paperqa/llms.py:173-523` |
| 「超人表现」（`README.md:13-15`、`README.md:145`） | 见 [1.2](#12-论文里的系统与仓里的系统) 与 [1.3](#13-超人表现的评测能否在仓里复现) | 仓里复现不了 | — |

### 1.2 论文里的系统与仓里的系统

论文 §8.1 原话：开源仓「提供基本算法，但不包括 Grobid 解析代码、非本地全文文献检索、引用遍历工具」，论文实验跑在作者机构的 HTTP 服务上（MongoDB、Redis、PostgreSQL、Dagster、Kubernetes）[^paper]。逐项对照：

| 论文里的 PaperQA2 | 仓里（57e89f7） | 证据 |
|---|---|---|
| Paper Search：智能体生成关键词，调 Semantic Scholar 等服务拿候选（默认 12 篇），再去自家库匹配或按开放获取链接现取（§2、§8.1.1） | 只查本地目录建的 tantivy 索引，一次 8 篇；唯一联网检索的工具是可选的 clinicaltrials.gov 检索 | `src/paperqa/agents/tools.py:109-210`、`src/paperqa/settings.py:655`、`src/paperqa/agents/tools.py:443-688` |
| 解析：PyMuPDF 为默认，WikiCrow 用 Grobid；可按章节切块（§8.1 参数表） | 没有 Grobid（全仓 grep 不到）；读取器有 pypdf（核心依赖）、PyMuPDF、Docling、nemotron；没有按章节切：PDF 与 Office 是按页拼接的定长字符滑窗，txt、html 是按 cl100k token 的定长滑窗，其余后缀按行；`ChunkingOptions` 只有 `SIMPLE_OVERLAP` | `pyproject.toml:38,89,101,108`、`src/paperqa/readers.py:105-143,258-358,506-551`、`src/paperqa/settings.py:176-195` |
| Citation Traversal 工具：从高分证据所在论文沿引用图前后各走一层，Semantic Scholar 加 Crossref，按重叠度过滤，上限 12 篇（§8.1.1，Algorithm 1）；消融显示它提高 DOI 召回（§3，图 2D） | 没有这个工具。`AgentSettings.tool_names` 的说明和 wikicrow、contracrow 两份设置的 agent prompt 仍在让智能体「收集证据引用的论文」；Semantic Scholar 客户端留着 citations、references、recommendations 的 URL 构造，只有 MATCH 被调用 | `src/paperqa/agents/tools.py:702-712`、`src/paperqa/settings.py:671-679`、`src/paperqa/configs/wikicrow.json:47`、`src/paperqa/clients/semantic_scholar.py:61-114`、`src/paperqa/clients/semantic_scholar.py:248` |
| RCS：LitQA 实验 top-k 30、进答案 15 条；改成 5 条时准确率最高、15 条时精度最高；GPT-4-Turbo 做 RCS 的准确率显著最好（§3、§8.1） | 默认 `evidence_k` 10、`answer_max_sources` 5；CLI 默认的 high_quality 是 20 与 5 | `src/paperqa/settings.py:109-111`、`src/paperqa/settings.py:138-140`、`src/paperqa/configs/high_quality.json:1-14` |
| 嵌入：`text-embedding-3-large` 拼 256 维 token 取模稀疏向量（§8.1.1） | 默认 `text-embedding-3-small` 纯稠密；`hybrid-` 前缀可选；wikicrow 用 hybrid-3-small，contracrow 用 hybrid-3-large | `src/paperqa/settings.py:794-797`、`src/paperqa/configs/wikicrow.json:6`、`src/paperqa/configs/contracrow.json:6` |
| agent_llm 固定 `gpt-4-turbo-2024-04-09`（§8.1） | 默认 `gpt-4o-2024-11-20` | `src/paperqa/settings.py:619-622`；lmi `packages/lmi/src/lmi/llms.py:145`[^lmi] |
| 论文说开源版用 LangChain 做智能体与状态更新（§8.1） | 已没有 LangChain 依赖；智能体是 aviary 的 `ToolSelector` 或可选的 ldp 智能体，模型走 lmi 加 litellm | `pyproject.toml:30-47`、`src/paperqa/settings.py:962-1049` |
| WikiCrow：每个基因 4 次 PaperQA2 调用加 1 次 GPT-4-Turbo 总览调用，Python 脚本拼成文章（§4，图 3A，§8.3） | 只有一份 `wikicrow.json` 单次问答设置，没有拼接脚本 | `src/paperqa/configs/wikicrow.json` |
| ContraCrow：先用多次 LLM 调用从论文里抽 claim，再逐条问矛盾（§5，图 4A） | 只有 `contracrow.json`：矛盾判断的 qa prompt 加 11 级标签；没有抽 claim 的代码 | `src/paperqa/configs/contracrow.json:34` |

### 1.3 超人表现的评测能否在仓里复现

| 论文结果 | 仓里有什么 | 缺什么 | 证据 |
|---|---|---|---|
| LitQA2：精度 85.2%、准确率 66.0%；9 名博士或在读博士 73.8% 与 67.7%；精度显著高于人，准确率无显著差异（§2，图 2B） | `docs/2024-10-16_litqa2-splits.json5`：train、eval、test 三份题号与建索引用的 DOI；README 指向外部 LAB-Bench 题目和 aviary 的 litqa 评测包；`agent_query` 与环境接受 aviary 的 `MultipleChoiceQuestion` 作输入，评分逻辑在 aviary 里 | 题目文本、评分代码、论文全文（版权）、论文用的检索服务、Grobid、引用遍历 | `README.md:1172-1191`、`docs/2024-10-16_litqa2-splits.json5:1-4`、`src/paperqa/agents/main.py:54-60`、`src/paperqa/agents/env.py:17,213` |
| 评分：GPT-4-0613 从输出里抽选项字母，3 次全量取均值（§8.2.2） | `prompts.py` 里有 `QA_PROMPT_TEMPLATE`、`EVAL_PROMPT_TEMPLATE`，全仓没有调用 | 评分流程在仓外 | `src/paperqa/prompts.py:152-162` |
| WikiCrow 与 Wikipedia 对比（§4，图 3C） | 生成的文章在论文给的公开 GCS 桶里（§4 脚注、§7） | 生成流水线、人工评分数据 | — |
| ContraCrow 在 ContraDetect 上 AUC 0.842（§5，图 4C） | `contracrow.json` | claim 抽取、ContraDetect 数据 | `src/paperqa/configs/contracrow.json` |
| LFRQA 基准（不在该论文里） | 教程 `docs/tutorials/running_on_lfrqa.md`，评测用外部的 `ldp` 与 `fhaviary[lfrqa]` 的 Evaluator，数据要另下 | 在仓外 | `docs/tutorials/running_on_lfrqa.md:226-245` |
| README FAQ 自己的说法 | 内部工具不同、有不能公开的论文访问许可，论文实验不是从已知 PDF 出发，所以结果会不同 | — | `README.md:1127-1136` |

论文里还有两处与复现相关的事实：LitQA2 前 147 题中放在 GitHub 上的一部分被搜索引擎收录，第三轮人工答题被污染，作者剔除了第三轮里这 147 题的人类答案（§8.2.1）；PaperQA2 单次查询成本 1–3 美元（§6），WikiCrow 每篇 4.48 美元（§4）[^paper]。

### 1.4 文档与代码不一致的小处

| 位置 | 现象 | 后果 |
|---|---|---|
| `src/paperqa/agents/__init__.py:61-66`、`src/paperqa/agents/__init__.py:251-253` 对 `pyproject.toml:125-126` | 「是否从命令行启动」的标志只在 `agents/__init__.py` 自己作为 `__main__` 执行时置真，而包里没有 `agents/__main__.py`；`pqa` 入口直接调 `main()`，标志一直是 False | 建索引的进度条在 `pqa` 下默认不显示，只能设 `PQA_INDEX_ENABLE_PROGRESS_BAR` 打开（`src/paperqa/agents/search.py:590-603`） |
| `src/paperqa/settings.py:580-591` 对 `src/paperqa/readers.py:477-480,540-551` | `.md` 在允许索引的后缀里，读取时落进「代码」分支 | Markdown 按行切块，块名是 `lines x-y` 而不是页码 |
| `src/paperqa/docs.py:143` | `aadd_url` 在 async 函数里用同步 `urllib` | 下载时阻塞事件循环 |
| `src/paperqa/llms.py:526-585` 对 `src/paperqa/settings.py:32,950-951` | 仓里有一份 `embedding_model_factory`，实际用的是 lmi 的同名函数 | 仓内这份只被自己递归调用 |
| `src/paperqa/clients/retractions.py:24-30` | 撤稿数据整份下载后写进已安装包的 `client_data/` 目录 | 只读安装位置下会失败（未验证） |
| `src/paperqa/agents/search.py:92-93,249-251` | 索引目录里的文件直接 `pickle.loads` | 能写索引目录的人能让读取方执行任意代码 |

## 2. 怎么做

### 2.1 入口

| 入口 | 做什么 | 证据 |
|---|---|---|
| `pqa ask "<问题>"` | 默认设置 high_quality；建或同步索引，跑智能体，答案存进 answers 索引 | `src/paperqa/agents/__init__.py:105-112,173-248` |
| `pqa index <目录>`、`pqa -i <名> search <词>` | 只建索引；在论文索引或历史答案索引里做关键词检索 | `src/paperqa/agents/__init__.py:115-149` |
| `pqa view`、`pqa save <名>`、`pqa -s <名>` | 看、存、选设置；设置文件先找 `~/.pqa/settings/`，再找包内 `configs/` | `src/paperqa/settings.py:876-923` |
| `ask()`、`agent_query()` | Python 入口，同 `pqa ask` | `src/paperqa/agents/__init__.py:105-112`、`src/paperqa/agents/main.py:54-85` |
| `Docs().aadd()` / `aget_evidence()` / `aquery()` | 不用智能体，手动加文档、收证据、出答案；没有 tantivy 这一级 | `src/paperqa/docs.py:156-721` |

命令行参数由 pydantic-settings 从 `Settings` 字段自动生成，如 `--parsing.chunk_size`、`--llm`（`src/paperqa/agents/__init__.py:219-229`）。

### 2.2 建索引

1. **定索引名与位置**：索引名是 `pqa_index_` 加哈希，哈希的输入是论文目录、是否用绝对路径、嵌入模型名、PDF 解析函数、块大小、重叠、是否整页截图、多模态开关；默认放在 `~/.pqa/indexes/<名>/`（`src/paperqa/settings.py:853-874`、`src/paperqa/settings.py:545-551`、`src/paperqa/utils.py:523-530`）。换其中任一项就是一个新索引。
2. **扫目录**：默认递归，按后缀取 `.txt .pdf .html .md .xlsx .docx .pptx`；目录里已删掉的文件从索引里删（`src/paperqa/agents/search.py:652-686`、`src/paperqa/settings.py:580-591`）。
3. **逐篇 `process_file`**，并发默认 5（注释说是照顾没有 S2、Crossref key 的人）（`src/paperqa/agents/search.py:490-580`、`src/paperqa/settings.py:563-566`）。
4. **`Docs.aadd` 一篇的流程**（`src/paperqa/docs.py:156-338`）：文件 md5 当 dockey；没给 citation 就读前 3 页的第一块，让 llm 写 MLA 引文（`docs.py:180-213`）；没给 title 和 DOI 就再让 llm 把引文抽成 JSON（`docs.py:225-261`）；有 title 或 DOI 就调元数据客户端升级成 `DocDetails`（`docs.py:266-295`）；全文解析，多模态默认开、每张图调一次 enrichment_llm（`docs.py:297-311`）；PDF 按页拼接后定长切块，库默认 5000 字符、重叠 250，`pqa` 默认的 high_quality 设置是 7000 字符，块名 `<docname> pages a-b`（`src/paperqa/readers.py:92-143`、`src/paperqa/settings.py:249-251`、`src/paperqa/configs/high_quality.json:9-12`）；粗查是不是正常文本（`docs.py:312-335`）；算嵌入（`docs.py:360-386`）。
5. **写盘**：tantivy 里存 title、year、file_location、body（全文）；整篇 `Docs`（含块和嵌入）pickle 压缩存成 `docs/<正文哈希>.zip`；处理失败的文件一律记 `ERROR` 并先存索引，之后不再重试；其中 `ValueError` 与解析失败跳过这一篇继续，其他异常记完后照样抛出、中断这次建索引（`src/paperqa/agents/search.py:297-316,531-566,271-273`）。

PDF 解析函数的默认值：装了 `paper-qa-pymupdf` 就用 PyMuPDF，否则用核心依赖里的 pypdf（`src/paperqa/settings.py:180-195`）。

### 2.3 智能体循环与工具

`agent_query` → `run_agent`：先建或同步索引（`agent.rebuild_index` 默认真），再按 `agent_type` 选三种跑法之一：`fake`（写死的顺序）、aviary `ToolSelector`（默认）、ldp 智能体（可选依赖）（`src/paperqa/agents/main.py:91-148`）。

- **环境**：每次 reset 清空 `Docs`，第一条消息是「用工具回答问题……状态：{status}」（`src/paperqa/agents/env.py:243-290`、`src/paperqa/prompts.py:142-150`）。状态行是论文数、相关论文数、证据数、已花美元（`src/paperqa/agents/tools.py:27-44`）。
- **循环**：agent_llm 通过工具调用选工具，格式错了重试 5 次；环境执行工具（允许并发的工具并发跑）；调了 complete 就结束；另有 `max_timesteps`、`max_answer_attempts`、500 秒超时（`src/paperqa/agents/main.py:274-323`、`src/paperqa/agents/env.py:295-346`、`src/paperqa/settings.py:663-669`）。
- **失败回退**：超时（状态 truncated）与轨迹里的其他异常（状态 fail）都被捕获；truncated（含步数用完）一律再强制调一次 gen_answer，fail 时只在还没调过 gen_answer 时强制调（`src/paperqa/agents/main.py:151-179,298-303`）。
- **fake 跑法**：llm 生成 3 条关键词各搜一次 → gather_evidence → gen_answer → 让 llm 选 complete；`fast.json` 用它（`src/paperqa/agents/main.py:182-256`、`src/paperqa/configs/fast.json:17`）。和论文 §3 的 No Agent 消融是同一种固定顺序，论文那组跑在作者内部服务上。
- **默认工具可用环境变量换**：`PAPERQA_DEFAULT_TOOL_NAMES`（逗号分隔）非空时替代下表的默认五个（`src/paperqa/agents/tools.py:702-712`）。

| 工具 | 做什么 | 证据 |
|---|---|---|
| `paper_search` | 在 tantivy 里查 `search_count`（默认 8）篇，同一查询再调就翻页；把命中论文的块（已带嵌入）加进当前 `Docs` | `src/paperqa/agents/tools.py:109-210` |
| `gather_evidence` | 对当前 `Docs` 做 RCS（见 2.4），返回新增证据数、最好的 `agent_evidence_n` 条摘要、状态行；没论文时报错 | `src/paperqa/agents/tools.py:217-311` |
| `gen_answer` | 调 `Docs.aquery` 出答案（见 2.5），返回「答案 + 状态行」 | `src/paperqa/agents/tools.py:314-386` |
| `reset` | 清空已收集的证据 | `src/paperqa/agents/tools.py:389-402` |
| `complete` | 结束，参数 `has_successful_answer` 表示确定或不确定 | `src/paperqa/agents/tools.py:405-440` |
| `clinical_trials_search`（可选） | 查 clinicaltrials.gov，把试验加进 `Docs` | `src/paperqa/agents/tools.py:443-688` |

### 2.4 证据收集

1. **召回范围是当前 `Docs`**，即智能体搜进来的那些论文的块，不是整个库（`src/paperqa/docs.py:437-490`）。
2. **向量召回**：查询嵌入后与块做余弦相似度取前 `evidence_k`；MMR 默认关（`src/paperqa/llms.py:111-170,241-274`）。
3. **逐块调 summary_llm**，并发数 `max_concurrent_requests`：system 是 JSON 摘要说明；user 是「Excerpt from {块名}: {带引用数与期刊级别的引文} --- {块正文，表格另附 markdown} --- Question」；块关联的图片作为多模态输入一起发（`src/paperqa/core.py:227-269`、`src/paperqa/prompts.py:3-23,108-119`、`src/paperqa/docs.py:551-571`）。
4. **解析**：去掉 `<think>`、取 ```` ```json ```` 块、把 `8/10` 换算成整数、补逗号等容错；坏 JSON 重试一次并把上次的错误告诉模型；超时、请求被拒（含安全拒答）直接丢弃这一块（`src/paperqa/core.py:19-124,214-225,289-303,383-400`）。
5. **清洗**：摘要里「作者 年份」式的括号引用被正则剥掉，避免和 pqac 键混淆（`src/paperqa/core.py:357-359`、`src/paperqa/utils.py:127-131`）。
6. **入库**：分数为 0 或失败的丢掉，其余去重后进 `session.contexts`；每条 Context 的 id 是 `pqac-` 加「问题 + 摘要前 500 字符」的 8 位哈希（`src/paperqa/docs.py:577-585`、`src/paperqa/types.py:279-316`）。

### 2.5 回答与引用绑定

1. **拼上下文**：按分数降序取前 `answer_max_sources`（默认 5），再去掉低于 `evidence_relevance_score_cutoff`（默认 1）的；每条写成「pqac-xxxx: 摘要 + From {引文}」，末尾列出合法键（`src/paperqa/settings.py:1202-1273`、`src/paperqa/prompts.py:164-167`）。
2. **没有上下文**就不调模型，直接回「I cannot answer…」（`src/paperqa/docs.py:649-654`）。
3. **qa prompt** 要求句末用键、列了合法与不合法的写法，可带上一轮答案迭代（`src/paperqa/prompts.py:30-69`、`src/paperqa/docs.py:655-682`）。
4. **后处理**：找出括号里的 pqac 键，换成块名（如 `Qian2011Neural pages 1-2`）并去重；按首次出现顺序生成「1. (块名): 引文」参考列表；答案里有、但 `session.contexts`（本次收集到的全部证据，不限于进了 prompt 的那几条）里没有的键直接从文本里删掉（`src/paperqa/types.py:474-526`）。
5. **输出字段**：`answer`（换过键）、`raw_answer`（原文）、`formatted_answer`（带问题与参考列表）、`references`、`contexts`、`cost`、`token_counts`、`tool_history`、`has_successful_answer`（`src/paperqa/types.py:319-386`）。

绑定粒度是「块」，即页码区间；机器校验只到「键在上下文里存在」，句子和证据是否一致没有检查。

### 2.6 元数据来源

| 来源 | 默认开 | 给什么 | 环境变量 | 证据 |
|---|---|---|---|---|
| Crossref | 是 | 标题、DOI、作者、日期、卷期页、期刊、出版方、被引数、bibtex | `CROSSREF_API_KEY`（可选）、`CROSSREF_MAILTO`（不设用 example@papercrow.ai） | `src/paperqa/clients/crossref.py:40-107` |
| Semantic Scholar | 是 | 同上，另有开放获取 PDF 链接、有影响力的被引数；按标题匹配时：给了作者，标题相似度不到 1 就要作者对上且不低于 0.75，没给作者就要求标题完全一致 | `SEMANTIC_SCHOLAR_API_KEY`（可选） | `src/paperqa/clients/semantic_scholar.py:40-58,224-294` |
| 期刊分级 | 是 | 包内 4 万行 CSV（芬兰 JUFO 分级 0–3，0 表示差或掠夺性期刊）加手工增删（如 PNAS 定为 3 级、去掉 Scientific Reports 的 0 级记录） | 无 | `src/paperqa/clients/journal_quality.py:30-32,92-198`、`src/paperqa/types.py:787-792` |
| OpenAlex | 否 | 同类书目数据 | `OPENALEX_MAILTO`、`OPENALEX_API_KEY` | `src/paperqa/clients/openalex.py:46-64` |
| Unpaywall | 否 | 开放获取状态、PDF 链接 | `UNPAYWALL_EMAIL` | `src/paperqa/clients/unpaywall.py:18-19,92` |
| 撤稿 | 否 | 下载 Crossref Labs 的 Retraction Watch 数据集，按 DOI 比对 | `CROSSREF_MAILTO` | `src/paperqa/clients/retractions.py:18-83`、`src/paperqa/clients/crossref.py:352-380` |

合并规则：多个来源的结果相加，出版日期新的优先、作者取总长更长的、被引数与年份取大、key 冲突就清空重生（`src/paperqa/types.py:1267-1371`）。某个来源遇到「DOI 未找到、请求错误、重试用尽、超时」四类失败时只打 warning 返回空，其他异常照常抛出（`src/paperqa/clients/client_models.py:111-143`）。用途：`formatted_citation` 在引文后加「This article has N citations and is from a domain leading peer-reviewed journal.」，撤稿的标 `**RETRACTED ARTICLE**`，这串文字进 RCS prompt 和回答上下文（`src/paperqa/types.py:1216-1249`）。`parsing.use_doc_details=False` 关掉整个元数据步骤，连同「把引文抽成 JSON」那次 llm 调用（`src/paperqa/settings.py:246-248`、`src/paperqa/docs.py:225,266`）。

### 2.7 怎么调模型

| 槽位 | 用在哪 | 默认 | 证据 |
|---|---|---|---|
| `llm` | 建索引时写引文、抽 JSON；pre、post；生成答案；fake 跑法生成关键词、最后选 complete | `gpt-4o-2024-11-20` | `src/paperqa/settings.py:753-766` |
| `summary_llm` | RCS，每个候选块一次 | 同上 | `src/paperqa/settings.py:777-783` |
| `agent.agent_llm` | 选工具，要支持工具调用 | 同上 | `src/paperqa/settings.py:619-622,962-981` |
| `parsing.enrichment_llm` | 建索引时每张图表一次（多模态默认开） | 同上 | `src/paperqa/settings.py:254-263,349-356` |
| `embedding` | 块与查询的嵌入 | `text-embedding-3-small` | `src/paperqa/settings.py:794-797` |

默认名来自 lmi 的 `CommonLLMNames.GPT_4O`（lmi `packages/lmi/src/lmi/llms.py:145`）[^lmi]。

**调用链**：`Settings.get_llm()` 等返回 `lmi.LiteLLMModel`，配置用 `*_config`（litellm Router 的 `model_list`），不给就生成一份：模型名、温度、系统消息打缓存标记（Anthropic 提示缓存）；调用进 `litellm.Router.acompletion`（`src/paperqa/settings.py:728-747,925-960`；lmi `packages/lmi/src/lmi/llms.py:818-852,922-951`[^lmi]）。给了 `*_config` 却不带 `model_list` 时（`tier*_limits` 就是这样），lmi 自己补一份，温度取 config 里的值、没有就是 1.0，不用 `Settings.temperature`，也没有缓存标记（lmi `packages/lmi/src/lmi/llms.py:729-774`[^lmi]）。`llm` 槽名字以 o1 或 gpt-5 开头时，全局 `temperature`（五个槽共用）被强制改成 1；只看 `llm` 这一个槽的名字（`src/paperqa/settings.py:823-841`）。每次调用的美元成本由 litellm 的 `completion_cost` 算、累加进 `PQASession.cost`；算不出来（例如价格表里没有的本地模型）时记 0.0 并打一条 warning（`src/paperqa/types.py:414-433`；lmi `packages/lmi/src/lmi/llms.py:988-992`[^lmi]）。

**嵌入的前缀**（lmi `embedding_model_factory`）：`st-` 本地 sentence-transformers（要 `paper-qa[local]`）；`hybrid-` 稠密拼 256 维 token 取模稀疏；`sparse` 只用稀疏，不调任何模型接口（tiktoken 编码文件首次加载见 [第 7 节](#7-还没弄清的问题)）；`litellm-` 前缀与不带前缀的都交给 litellm（lmi `packages/lmi/src/lmi/embeddings.py:201-219,311-370`[^lmi]；仓内同逻辑副本 `src/paperqa/llms.py:526-585`）。

**换成 Anthropic 要改的**：

- 环境里放 `ANTHROPIC_API_KEY`；`llm`、`summary_llm`、`agent.agent_llm`、`parsing.enrichment_llm` 四个都改成 `claude-*`。README 的 Claude 示例只改了前三个（`README.md:546-563`），多模态默认开时图片描述仍走 gpt-4o。
- 嵌入：Anthropic 不提供自己的嵌入模型[^anthropic-embed]。要么另一家的 key（OpenAI、Gemini 或其他 litellm 支持的），要么 `st-` 本地，要么 `sparse`。改嵌入就是换一个新索引。
- 仓里的测试覆盖：`test_model_chain` 用 `anthropic/claude-sonnet-4-6` 做 llm 与 summary_llm，嵌入仍用 OpenAI（`tests/test_paperqa.py:488-515`）；Claude 3.7 Sonnet 做 ldp MemoryAgent 的 agent_llm（`tests/test_agents.py:447`）。代码注释写着 claude-haiku-4-5 描述图片「反复失败」（`src/paperqa/settings.py:350-353`）。

**换成本地模型（Ollama、llama.cpp）要改的**：五个槽都要配（`*_config` 里写 `api_base`）；嵌入用 `ollama/...` 配 `embedding_config`，或用 `st-`。README 的两个本地示例都没设 `agent_llm` 和 `enrichment_llm`，llama.cpp 那个连嵌入也没设（`README.md:594-652`）。issue #1321 的报告人设了 llm、summary_llm、agent_llm 和嵌入，建索引仍调到 OpenAI，关掉多模态（不再调 enrichment_llm）后才停；之后又撞上嵌入模型上下文比默认块短[^i1321]。agent_llm 必须能做工具调用，选不出工具重试 5 次后抛错（`src/paperqa/agents/main.py:305-312`）；README 说 7B 模型不行（`README.md:586-588`）。

**不能用的**：Claude Code、Codex 这类命令行 agent 的登录。PaperQA 只认 litellm 能用的凭据：环境变量里的 key，或 `api_base` 指向的端点。

### 2.8 数据进出与落盘

| 路径或对象 | 内容 | 证据 |
|---|---|---|
| 论文目录 | 输入，只读 | `src/paperqa/agents/search.py:622-664` |
| manifest CSV（可选） | `file_location`、`doi`、`title` 等，减少建索引时的猜测 | `src/paperqa/settings.py:536-544`、`src/paperqa/agents/search.py:437-484` |
| `~/.pqa/indexes/<索引名>/index/` | tantivy 文件 | `src/paperqa/agents/search.py:155-209` |
| `~/.pqa/indexes/<索引名>/docs/*.zip` | 每篇一个 zlib 压缩的 pickle（块与嵌入） | `src/paperqa/agents/search.py:307-314,558-566` |
| `~/.pqa/indexes/<索引名>/files.zip` | 文件名到正文哈希或 `ERROR` | `src/paperqa/agents/search.py:171-174,367-379` |
| `~/.pqa/indexes/answers/` | 每次回答的 `AnswerResponse` JSON；证据的块原文、图片、嵌入在构造 `AnswerResponse` 时就被清掉（所以 `ask()`、`agent_query()` 返回的对象里也没有），摘要与块名保留；只有不经智能体、直接调 `Docs.aquery` 拿到的 `PQASession` 还带原文 | `src/paperqa/agents/main.py:64-84,148`、`src/paperqa/agents/models.py:59-67`、`src/paperqa/types.py:442-472` |
| `~/.pqa/settings/<名>.json` | `pqa save` 存的设置 | `src/paperqa/agents/__init__.py:152-170` |
| 返回值 | `AnswerResponse`：`session` 加状态 success、unsure、truncated、fail | `src/paperqa/agents/models.py:29-57` |
| 命令行输出 | 日志里一行 `Answer: ...`，只有换过键的答案，不含参考列表 | `src/paperqa/agents/main.py:74` |

`PQA_HOME` 改的是父目录，实际路径是 `$PQA_HOME/.pqa/...`（`src/paperqa/utils.py:523-530`）；索引位置也可以用 `agent.index.index_directory` 指定。

## 3. 为什么

### 3.1 设计理由

| 设计 | 解决什么 | 依据 |
|---|---|---|
| RCS：每块先摘要加打分再进答案 | 不让无关块进答案上下文；摘要约 200–400 token，原块约 2250 token，同样的上下文窗口能容纳更多论文 | 论文 §2、§8.1.1；No RCS Model 消融显著下降，GPT-3.5 与 Llama3 70B 做 RCS 反而比不做差（§3，图 2C）[^paper] |
| 智能体而不是固定顺序 | 看到相关论文数后可以换关键词再搜，召回更高 | No Agent 消融准确率显著更低（§3，t(3.7)=3.41，p=0.015）[^paper]；代码保留 fake 跑法（`src/paperqa/agents/main.py:182-256`） |
| 两级检索：tantivy 挑论文，块级向量召回，再 RCS | 每次只需比对不到 1k 个块，所以内存里的 numpy 向量库就够 | `README.md:694-697`、`src/paperqa/agents/tools.py:176-199` |
| 开源版只搜本地目录 | 全文受许可证限制，作者的检索服务与论文库不能公开 | 论文 §8.1[^paper]、`README.md:1129-1136` |
| 短哈希键加事后换名 | 模型只需照抄短键；不存在的键可以机器删掉；剥掉摘要里原有的「作者 年份」防混淆 | `src/paperqa/types.py:279-316,474-526`、`src/paperqa/core.py:357-359`；v2025.12.17 发版说明里的 #1089 Context id updates[^rel-2512] |
| 元数据写进 RCS prompt | 让模型看到被引数、期刊级别来权衡来源 | 论文 §2「RCS 步骤也注入来源论文的元数据」[^paper]、`src/paperqa/types.py:1216-1239` |
| 图片描述只进嵌入 | 让图表能被检索到，又不让模型写的描述变成可引用的正文 | `README.md:819-831`、`src/paperqa/types.py:208-235` |
| JSON 容错加重试一次 | 各家模型的 JSON 输出不稳 | `src/paperqa/core.py:19-124,383-400`；发版说明 #1082、#1083[^rel-2512] |
| 索引名是设置的哈希 | 换嵌入、解析器、块大小自动建新索引，不混用 | `src/paperqa/settings.py:853-874`；#1125 修过「不同解析器同名」[^rel-2512] |
| 不依赖 LangChain、LlamaIndex，只用 litellm 与 pydantic | 换模型厂商，集中限流与记账 | `README.md:180-192`、`README.md:1138-1153` |
| 环境注册进 aviary，每步奖励恒为 0 | 同一套工具也用于训练语言智能体，奖励在外面按答案评 | `src/paperqa/agents/env.py:307,387`、`src/paperqa/settings.py:983-1049`、`README.md:1186-1216`（由命名与 README 引用推断） |
| 2025-12 起改 CalVer | 不再承诺版本间兼容，版本号与论文里的 PaperQA2 名字脱钩 | `README.md:151-178` |

### 3.2 踩过的坑

| 来源 | 现象 | 代码现状 |
|---|---|---|
| issue #1321（开，2026-03）[^i1321] | 用 Ollama 配了 llm、summary_llm、agent_llm 与嵌入，建索引仍去调 OpenAI，关掉多模态后才停；随后嵌入模型（mxbai-embed-large）上下文比默认 5000 字符的块短而报错，换大上下文嵌入模型后跑通；帖里答疑的是 dosu 机器人，没有维护者回复；报告人最后说只读 README、不借助机器人或不读包代码不容易用起来，issue 留着等他提 README 的 PR | `enrichment_llm` 默认 gpt-4o、多模态默认开（`src/paperqa/settings.py:254-263,349-356`）；README 本地示例没设这个槽（`README.md:594-652`） |
| issue #1261（开，2026-01）[^i1261] | 自定义 `rate_limit` 后限流器等满 60 秒超时，帖里没定根因；同帖里换了 GPT-5.1，加论文时图片描述仍走 gpt-4o，维护者回复要单独配 `parsing.enrichment_llm` 或关多模态 | 限流器等待上限默认 60 秒（环境变量 `RATE_LIMITER_TIMEOUT`，lmi `packages/lmi/src/lmi/rate_limiter.py:31`）；限速表按模型名取，取不到落兜底（lmi `packages/lmi/src/lmi/llms.py:864-870`[^lmi]）；enrichment 同上 |
| issue #861（开，2025-02）[^i861] | 用 manifest 建索引仍在调 LLM | 现行代码里 manifest 行经 `DocDetails` 合成 citation 后传给 `aadd`，跳过引文调用（`src/paperqa/agents/search.py:437-445,516-530`、`src/paperqa/docs.py:180`）；图片描述仍默认调用。未实测 |
| issue #633（开，2024-10）[^i633] | 命令行与 Python 里给 `*_config` 只写 `rate_limit`、不写 `model_list`，报 `KeyError: 'model_list'` | 现行 lmi 在缺 `model_list` 时自己补一份（lmi `packages/lmi/src/lmi/llms.py:729-774`[^lmi]），`tests/test_agents.py:819-845` 用正是这种写法的 `tier1_limits` 构造模型；读代码看这个报错已不出现，未实测，issue 没关 |
| issue #381（开，2024-09）[^i381] | 标题：索引 50 篇撞 Semantic Scholar 限流 | 建索引并发默认压到 5（`src/paperqa/settings.py:563-566`）；README 建议 100 篇以上申请 key（`README.md:263-268`） |
| issue #390（开，2024-09）[^i390] | 标题：v5 怎么配 LiteLLM 加 Ollama | 同 #1321 |
| 发版说明 v2025.12.17[^rel-2512] | 下调 litellm 版本修挂起的测试（#1192）；CI 里 Python≤3.11 加 LiteLLM≥1.76 不兼容（#1195）；捕获安全拒答（#1114）；404 页面被当成论文解析（#1126） | CI 的包测试跳过 3.11（`.github/workflows/tests.yml:137`）；拒答丢弃该块（`src/paperqa/core.py:294-303`）；文本粗检（`src/paperqa/docs.py:312-335`） |
| 代码注释 | claude-haiku-4-5 描述图片不行；Claude Sonnet 4.5 把年份传成字符串 "None"；2024-10 索引 1.9 万篇 PDF 时某个来源返回空作者；JUFO 在 2025-08 到 2026-01 间改用 4 级表示未定级；Semantic Scholar 的引用遍历偶发 403；OpenAlex 连接超时 | `src/paperqa/settings.py:350-353`、`src/paperqa/agents/tools.py:151`、`src/paperqa/types.py:1012-1013`、`src/paperqa/clients/journal_quality.py:101-103`、`src/paperqa/clients/semantic_scholar.py:128-130`、`src/paperqa/clients/openalex.py:110-111` |
| 代码注释 | 建索引没有文件锁，并发 reset 会有竞争；单篇解析导致崩溃时要先存索引以便续建 | `src/paperqa/agents/env.py:275-277`、`src/paperqa/agents/search.py:531-548` |

## 4. 跑起来要什么

| 项 | 要求 | 证据 |
|---|---|---|
| Python | ≥3.11；CI 测 3.11 与 3.13，读取器子包测 3.12 与 3.13 | `pyproject.toml:59`、`.github/workflows/tests.yml:103,137` |
| 操作系统 | 声明与系统无关；CI 只在 ubuntu-latest 上跑 | `pyproject.toml:22`、`.github/workflows/tests.yml:99` |
| 核心依赖 | fhaviary[llm]、fhlmi（带 litellm、coredis、limits[async-redis]、tiktoken）、tantivy、pybtex、numpy、pydantic-settings、httpx-aiohttp、html2text、paper-qa-pypdf 等；锁定 litellm 1.82.4、fhlmi 0.45.0、fhaviary 0.34.0 | `pyproject.toml:30-47`、`uv.lock:1131-1170,2018-2019` |
| 可选依赖 | `pymupdf`、`pypdf-media`、`pypdf-enhanced`、`image`、`docling`、`nemotron`、`office`（unstructured）、`local`（sentence-transformers）、`qdrant`、`ldp`、`memory`、`zotero`（会连带装上 `paper-qa-pymupdf`）、`openreview` | `pyproject.toml:61-123` |
| 模型凭据（默认） | `OPENAI_API_KEY`：四个 LLM 槽与嵌入默认都是 OpenAI | 见 [2.7](#27-怎么调模型) |
| 模型凭据（换厂商） | 对应厂商的 key，或本地端点；Anthropic 只能覆盖四个 LLM 槽 | 见 [2.7](#27-怎么调模型) |
| 元数据服务 | 默认会访问 api.crossref.org 与 api.semanticscholar.org；key 可选，不设会限流；`use_doc_details=False` 可关 | `src/paperqa/clients/crossref.py:40-107`、`src/paperqa/clients/semantic_scholar.py:224-232`、`src/paperqa/settings.py:246-248` |
| 其他外部服务 | OpenAlex、Unpaywall、Crossref Labs（撤稿）只在 `ALL_CLIENTS`；clinicaltrials.gov 只在对应工具；NVIDIA 接口只在 nemotron 读取器（`NVIDIA_API_KEY`） | `src/paperqa/clients/__init__.py:31-36`、`packages/paper-qa-nemotron/README.md:49` |
| 算力 | 默认路径纯 CPU：numpy 余弦、tantivy、pypdf 或 PyMuPDF；Docling 要下版面与表格模型，本地嵌入要 sentence-transformers；没有必须 GPU 的步骤 | `src/paperqa/llms.py:241-274`、`.github/workflows/tests.yml:111-122` |
| 磁盘状态 | `~/.pqa/` 下的索引、答案库、设置（见 [2.8](#28-数据进出与落盘)） | `src/paperqa/utils.py:523-530` |
| 每次调用量 | 建索引：每篇 0–2 次 llm（引文与抽取）加每张图 1 次 enrichment_llm 加嵌入；每次 gather_evidence：`evidence_k` 次 summary_llm（默认 10，CLI 默认 20；JSON 坏了的块再多 1 次）；每次答案 1 次 llm（设了 pre、post 各加 1 次）；智能体每步 1 次 agent_llm | `src/paperqa/docs.py:180-311`、`src/paperqa/docs.py:521-571,626-710`、`src/paperqa/core.py:383-400`、`src/paperqa/configs/high_quality.json:3` |
| 费用 | 论文报每次查询 1–3 美元（§6），论文配置与仓里默认值不同，仓里默认配置的费用没测 | 论文[^paper] |

## 5. 和平台对照

只列事实，不下接不接的结论。

### 5.1 平台文献阶段现在有什么

| 项 | 现状 | 证据 |
|---|---|---|
| 步骤能力 | 文献阶段没有；流程里排了这个阶段时助理自己开产出目录写 | `docs/architecture/workflow.md:28` |
| 主文件 | `sources.md`，由助理手写（`ai4sci output new literature`），框架只认文件名、写法不限 | `platform/framework/capabilities/__init__.py:45-47`、`docs/architecture/README.md:170`、`platform/coordinator/README.md:120` |
| 助理怎么找材料 | 用它所在命令行自带的搜索与网页读取，找论文、官方代码、数据、别人的复现、要的 key | `platform/coordinator/README.md:120-128`、`docs/architecture/README.md:164` |
| skill | `pdf`：一篇 PDF 到 `paper.md`、`images/`、`structured.json`（后端 pymupdf4llm）；`download`：git、单文件、Hugging Face 到 `materials/` 加收据；两者都不调语言模型接口 | `platform/skills/pdf/SKILL.md:1-6`、`platform/skills/download/SKILL.md:1-6` |
| 下游谁读文献产出 | 复现流程的 `reproduction`、`reproducibility` 把 `sources.md` 当可选输入 | `platform/framework/capabilities/reproduction/__init__.py:65,282-285` |
| 流程 | `reproduce` 的文献格挂 `[pdf, download]`；`research` 流程从设计开始，不含文献 | `docs/architecture/workflow.md:47`、`platform/workflows/research.yaml:8-14` |

### 5.2 多了什么、重叠什么

| 功能 | PaperQA2 | 平台现有 | 关系 |
|---|---|---|---|
| PDF 转文本 | 四种读取器，输出按页拼接的定长块，给检索用 | `pdf` skill，输出整篇 markdown、图片目录与结构化 JSON（分节、表格、图注、参考文献、题目作者年份 DOI），给人和 agent 读、抄表格里的数 | 重叠：都做解析；产物形状与用途不同 |
| 多篇论文检索 | tantivy 挑论文加块级向量召回加 RCS | 没有专门的；助理或执行层自己读 | PaperQA2 多出 |
| 带出处的回答 | 句末键换成「作者年份 pages 页码」，自动生成参考列表 | `sources.md` 写法不限，没有页码级引用机制 | PaperQA2 多出 |
| 元数据补全 | Crossref、Semantic Scholar、期刊分级，可选撤稿、OpenAlex、Unpaywall | 助理手查；`download` 收据记 commit 与 sha256 | PaperQA2 多出一部分 |
| 联网找论文 | 智能体主流程不做（只搜本地目录）；contrib 里的 OpenReview 辅助类拉某个会议的全部投稿列表、让 llm 挑相关的再下 PDF，Zotero 辅助类从研究者自己的 Zotero 库取 PDF；两者都不在 `pqa` 命令里 | 助理用命令行自带的搜索 | 平台的通用搜索 PaperQA2 没有；PaperQA2 多出限于 OpenReview 单个会议与个人 Zotero 库的两个辅助类 |
| 拉取材料 | 智能体主流程没有；OpenReview、Zotero 辅助类能把 PDF 下到论文目录 | `download` skill（git、单文件、Hugging Face，留收据） | 平台有通用的；PaperQA2 只有两个来源专用的 |
| 智能体循环 | 自带工具调用循环，自己调模型 | 助理与执行层本身就是 Claude Code 或 Codex 会话 | 重叠：两边各有一个选工具的循环；由平台的会话去调 `pqa ask`，就是一个循环里再跑另一个、各用各的模型凭据 |
| 矛盾检测 | 只有 `contracrow.json` 的 prompt 与标签 | 没有 | PaperQA2 多出一份设置 |
| 历史问答检索 | `~/.pqa/indexes/answers` 加 `pqa -i answers search` | 产出目录加 `meta.yaml` | 各有一套存放方式 |

### 5.3 会碰到的平台规则

| 规则 | 平台怎么定 | PaperQA2 的对应事实 | 证据 |
|---|---|---|---|
| P-1 | 执行层是唯一写代码的；框架不调模型写文本；判据是 `framework/` 下没有模型接口名 | PaperQA2 的引文、RCS 摘要、答案、图片描述、选工具都由它自己调模型接口写出；平台现有的两个 skill 都不调语言模型接口；P-1 的判据只覆盖 `framework/` | `docs/architecture/README.md:151`；见 [2.7](#27-怎么调模型) |
| P-25 | 两层 agent 用研究者自己的命令行登录，按人一份 `agents.yaml`；订阅账号报不出美元的成本填 NaN | PaperQA2 要 litellm 能用的 API key 或本地端点，用不了命令行登录；它自己按美元记成本，算不出的记 0.0 | `docs/architecture/README.md:175`、`src/paperqa/types.py:414-433`；lmi `packages/lmi/src/lmi/llms.py:988-992`[^lmi] |
| P-20 | 进文献阶段的能力必须留下 `sources.md`；skill 不开产出目录，写哪由调用者定 | 产物是 `AnswerResponse` JSON 与 `formatted_answer` 文本，不是 `sources.md` 的形状 | `docs/architecture/README.md:170`；见 [2.8](#28-数据进出与落盘) |
| P-22 | agentskills.io 格式；脚本 PEP 723 自带依赖并锁定，`uv run --locked --offline` 起；输出目录由 `--out` 给，不写别处 | 依赖链含 litellm、fhlmi、fhaviary、tantivy 等；默认把索引、答案库、设置写在 `~/.pqa`，索引位置可配；撤稿数据写进包目录（只在 `ALL_CLIENTS`） | `docs/architecture/README.md:172`、`platform/docs/add-a-skill.md:56`、`src/paperqa/utils.py:523-530`、`src/paperqa/clients/retractions.py:24-30` |
| skill 运行时联网 | skill 运行器注释写「运行时不联网，沙箱断网照跑」，指的是 `--offline` 不再下依赖；现有的 `download` skill 运行时本来就要联网（git、Hugging Face）；运行器把服务进程的全部环境变量（去掉 `VIRTUAL_ENV`）传给脚本 | PaperQA2 运行时要连模型接口与 Crossref、Semantic Scholar（全本地且关元数据除外） | `platform/framework/skills/run.py:6-7,37-42,61-66`、`platform/skills/download/SKILL.md:4` |
| P-14 | 助理面前只有 `ai4sci`；联网只用命令行自带的搜索与网页读取 | `pqa` 是另一个命令行；PaperQA2 自己发 HTTP 请求 | `docs/architecture/README.md:164` |
| P-11 与会话隔离 | Claude Code 会话带 `--strict-mcp-config`，执行层命令前缀只有 `ai4sci skill` | 仓里没有 MCP 服务端（`src/` 与 `packages/*/src` 里 grep `mcp` 为 0 处） | `docs/architecture/workflow.md:238-239` |
| P-7 | 验证不过就停，不静默降级 | 多处失败后继续：元数据来源的四类失败只打 warning、证据生成失败丢弃该块、轨迹异常后仍强制出答案、单篇 `ValueError` 或解析失败标 `ERROR` 跳过、图片描述被拒跳过、成本算不出记 0.0 | `docs/architecture/README.md:157`、`src/paperqa/clients/client_models.py:111-143`、`src/paperqa/core.py:383-400`、`src/paperqa/agents/main.py:151-179`、`src/paperqa/agents/search.py:531-548`、`src/paperqa/settings.py:1144-1169`；lmi `packages/lmi/src/lmi/llms.py:988-992`[^lmi] |
| 密钥 | 密钥名写进需求，值放起服务的环境里 | 读 `OPENAI_API_KEY` 等模型 key 与 `CROSSREF_API_KEY`、`SEMANTIC_SCHOLAR_API_KEY`、`CROSSREF_MAILTO` 等 | `platform/coordinator/README.md:126`；见 [2.6](#26-元数据来源) |
| 许可证 | — | 主包 Apache-2.0；可选的 `paper-qa-pymupdf` 是 AGPL-3.0，装了它就成为默认 PDF 解析器；`pymupdf` 与 `zotero` 两个 extra 都会装上它 | `LICENSE:1-3`、`packages/paper-qa-pymupdf/LICENSE:1-2`、`src/paperqa/settings.py:180-195`、`pyproject.toml:108,120-123` |

## 6. 成熟度

| 项 | 实况 | 证据 |
|---|---|---|
| 仓库 | FutureHouse，9,251 star，922 fork，2023-02 创建 | GitHub API[^gh] |
| 规模 | `src/` 1.18 万行 Python；四个读取器子包 2,210 行 | `find src -name '*.py'` 与 `packages/*/src` 计数 |
| 测试 | `tests/` 6,921 行、166 个测试函数、47 份 VCR 录制、28 个用例标了 vcr；子包测试 2,293 行、71 个测试函数、6 份录制、3 个用例标了 vcr；录制在 CI 里只回放不新录，其余要调外部接口的用例在 CI 里用真 key 调 OpenAI、Anthropic、Gemini、Semantic Scholar、Crossref、NVIDIA；两边合计 8 处用例标了失败重跑 | `tests/conftest.py:108-123`、`.github/workflows/tests.yml:123-131,157-165`、`tests/test_paperqa.py:2380` |
| CI | pylint、refurb、构建检查；PR 上跑 pre-commit（ruff、mypy、codespell 等）；src 测试 3.11 与 3.13，子包测试 3.12 与 3.13；建 release 时发 PyPI | `.github/workflows/tests.yml`、`.github/workflows/build.yml:3-6`、`.pre-commit-config.yaml:31,96` |
| 发版 | 2025-12-17 起 CalVer，至今 10 个版本，最近 v2026.08.12；之前 v5.x 到 5.29.1（2025-08） | GitHub releases[^gh] |
| 维护节奏 | main 提交数：2025 年每月 7–51 个，2026-01 14、2026-02 22、2026-03 10，4 月到 9 月合计 4 个（6 月 3 个、8 月 1 个）；GitHub 显示 2026-09-25 有推送，是 renovate 机器人推到 `renovate/lock-file-maintenance` 分支的锁文件更新 | GitHub API[^gh] |
| 贡献者 | James Braza 476 个提交、Andrew White 232、renovate 机器人 78、Michael Skarlinski 54，其余每人不到 20 | GitHub API[^gh] |
| issue | 开 133、关 251，开着的 PR 17 | GitHub 搜索 API[^gh] |
| 兼容承诺 | CalVer 明说去掉版本间兼容保证 | `README.md:165-169` |
| 许可证 | 主包 Apache-2.0（Copyright 2024 FutureHouse）；docling、nemotron、pypdf 子包 Apache-2.0；pymupdf 子包 AGPL-3.0 | `LICENSE:1-3,189`、`packages/*/LICENSE` |

## 7. 还没弄清的问题

1. 开源版在真实论文集上的效果离论文数字差多少：仓里没有可跑的 LitQA2 评测，论文的检索服务、Grobid、引用遍历都不在，仓里看不出来；外层 #160（实测）还开着。
2. 中文论文：切块按字符、分词用 cl100k、稀疏嵌入按 token 取模；有一次多语言文本判定的改动（#1179），没看到中文测试，效果未知。
3. 对默认模型 `tier*_limits` 落到每分钟 3 万 token，以及给了 `llm_config` 却不带 `model_list` 时温度取 1.0、`Settings.temperature` 不生效（lmi `packages/lmi/src/lmi/llms.py:729-774`，温度在第 750 行[^lmi]）：都是读代码的推断，没跑。
4. `Settings` 继承 pydantic-settings 的 `BaseSettings`（`src/paperqa/settings.py:750-751`），同名环境变量（如 `LLM`、`EMBEDDING`、`VERBOSITY`）是否会覆盖字段：这是 pydantic-settings 的默认行为，本仓里没验证。平台的 skill 运行器会把服务进程的全部环境变量传给脚本（`platform/framework/skills/run.py:36-42`）。
5. 除模型与元数据接口外，运行时还有哪些联网：tiktoken 首次加载编码文件、litellm 导入时取价格表，是这两个库常见的行为，没在本机验证。
6. 用 manifest 建索引时还剩哪些模型调用（#861 仍开着）：读代码是只剩图片描述，没实测。
7. 多个工作区或多个进程共用 `~/.pqa`：注释说建索引没有文件锁（`src/paperqa/agents/env.py:275-277`），tantivy 写锁有重试（`src/paperqa/agents/search.py:292-329`），实际并发会怎样没验证。
8. 维护走向：2026-04 以后 main 基本停了，仓里看不出是转去别处还是在准备大版本。
9. 传递依赖的许可证（litellm、tantivy、pybtex、fhlmi、fhaviary 等）没逐个核；装完的体积与冷启动时间没测。
10. 经智能体拿到的答案（返回值与存盘的 JSON）都清掉了证据的原文（`src/paperqa/agents/models.py:59-67`、`src/paperqa/types.py:442-472`），只留摘要与块名；要回到原文得再打开索引里的 pickle，这对「证据可追溯」够不够，要看具体用法。
11. 只装核心依赖（读取器是 pypdf、不带 `pypdf-media`，也就没有 Pillow）而多模态默认开时，带图的 PDF 在 pypdf 读取器里走「逐张取图」分支，注释说没装 Pillow 时 pypdf 会报错（`packages/paper-qa-pypdf/src/paperqa_pypdf/reader.py:309-313`）；这时建索引是跳过这一篇还是整体中断（取决于抛出的异常类型，见 [2.2](#22-建索引) 第 5 步），没实测。

## 8. 调研方法

- 浅克隆到外层 `vendor/paper-qa`（gitignore 挡住），提交 57e89f7。只读代码，没装依赖、没跑项目代码。
- 主线程逐文件读了 `src/paperqa` 全部模块、四个读取器子包的 `pyproject.toml` 与 LICENSE、`tests/` 里与结论相关的用例、CI 配置；lmi 的三个文件按 v0.45.0 从 GitHub 取来读；issue、发版说明、提交统计用 `gh api` 查（2026-09-27）。
- 论文 arXiv 2409.13740 下载后用平台的 `pdf` skill 解析，引用的节号与图表号以该 PDF 为准。
- 「对不上」的每一条都回到代码行确认过；标了「推断」或「未验证」的没有运行证据。
- 第一版写完后另做了一遍独立复查：逐条打开文中的 `文件:行` 与论文章节核对，重新从 GitHub 取 lmi v0.45.0 三个文件比对，重查了 issue 帖子与提交统计；行号偏了的、说法过头的已按代码改正。

[^paper]: Skarlinski et al., *Language agents achieve superhuman synthesis of scientific knowledge*, arXiv 2409.13740，<https://arxiv.org/abs/2409.13740>。2026-09-27 下载的 PDF，存外层 `materials/research/2026-0927-scientific-ai-capabilities/papers/paperqa2-2409.13740.pdf`（不进 git）。
[^lmi]: fhlmi（lmi）v0.45.0 源码，<https://github.com/Future-House/ldp/tree/v0.45.0/packages/lmi>；paper-qa 的 `uv.lock:1156-1157` 锁定此版本。文中 lmi 的 `文件:行` 相对 ldp 仓库根。
[^anthropic-embed]: Anthropic 文档 Embeddings 页：「Anthropic does not offer its own embedding model」，<https://platform.claude.com/docs/en/build-with-claude/embeddings>，2026-09-27 查。
[^rel-2512]: paper-qa v2025.12.17 发版说明，<https://github.com/Future-House/paper-qa/releases/tag/v2025.12.17>。
[^i1321]: <https://github.com/Future-House/paper-qa/issues/1321>
[^i1261]: <https://github.com/Future-House/paper-qa/issues/1261>
[^i861]: <https://github.com/Future-House/paper-qa/issues/861>
[^i633]: <https://github.com/Future-House/paper-qa/issues/633>
[^i381]: <https://github.com/Future-House/paper-qa/issues/381>
[^i390]: <https://github.com/Future-House/paper-qa/issues/390>
[^gh]: GitHub API，2026-09-27 查：`repos/Future-House/paper-qa`（star、fork、创建与推送时间）、`releases`、`commits?sha=main&since=2025-01-01`（按月计数）、`contributors?anon=1`、`events`（最近一次推送是谁、推到哪个分支）、`search/issues`（issue 与 PR 计数）。
