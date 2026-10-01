---
title: GPT Researcher 代码级深读
subtitle: 文献阶段选型 · 拆子查询、并行检索抓取、BM25 挑段落、一次写成；三种外壳都自己调模型
kind: 开源项目选型深读（只读代码，不跑、不装依赖）
date: 2026-09-27
scope: 仓库 https://github.com/assafelovic/gpt-researcher，浅克隆到外层 vendor/gpt-researcher，提交 0957c30（2026-09-26）；PyPI 0.16.1 的 gpt_researcher/ 与该提交逐文件一致。另读 assafelovic/gptr-mcp 提交 6388477 的 server.py、utils.py（文中写作 gptr-mcp/…）与 vercel-labs/skills 提交 f00c1a1 的 src/skills.ts（写作 vercel-labs/skills:…）。不读 frontend、docs 站点源码、terraform、各语言 README。文中不带前缀的 文件:行 相对 gpt-researcher 仓库根（其中 docs/docs/…、docs/blog/… 是 gpt-researcher 自己的文档）；平台一侧写作 platform/… 或 docs/architecture/…，相对外层仓根
status: 第一版
---

> **结论先行**：核心包 `gpt_researcher/`（约 1.6 万行）是一条形状固定的流水线：一次模型调用给任务挑一个「角色提示词」，一次模型调用把问题拆成 3 条子查询，加上原问题共 4 条并行去搜、去抓页面、用 BM25 从页面里挑段落，最后一次模型调用写成一篇带 URL 超链接引用的 markdown 报告。README 里的 planner / execution agents / publisher 在代码里就是这两次提示词调用加一组 asyncio 协程，没有独立的 agent；README 写的「逐个来源做摘要」在现行代码里不存在（`summarize_url` 零调用），换成了不调模型的段落筛选。deep research 是递归树，默认宽 3 深 2，一次跑下来约 9 个嵌套研究、33 次模型调用，它自己的成本计数器漏算了这部分。
>
> 学术源四个检索器都有（arXiv、Semantic Scholar、OpenAlex、PubMed Central），都薄：只回标题、链接、摘要，作者、年份、DOI 全部丢掉；arXiv 的 PDF 链接被路由到只取摘要的抓取器，拿不到正文；Semantic Scholar 只留开放获取的论文，代码不带 API key，本机三次无 key 请求全部 429；OpenAlex 的 API 摘要在进上下文之前被丢掉，只抓链接，付费墙论文的链接是出版社落地页。引用只靠提示词要求模型写 `([in-text citation](url))`，运行路径上没有代码核对引用的 URL 抓没抓过、原文支不支持；作者自己在 DeepResearch Bench 10 道题上测得引用精确率 56%。能追到的是 URL 级，段落级要拿 `get_research_sources()` 里存的原文自己去对（检索器直接给全文的来源在那里只存了 URL）。
>
> README 说的 Claude skill 装下去的是一份「教你开发、集成 GPT Researcher」的说明书（`.claude/SKILL.md`，没有脚本）；Codex 插件的 `.mcp.json` 起 `uvx gpt-researcher`，而发布的 wheel 里没有这个可执行入口；独立仓库 gptr-mcp 启动时没有 `OPENAI_API_KEY` 就退出，它的 `deep_research` 工具跑的是标准研究而不是 deep 模式，修这几处的 PR 开着没合，仓库最后一次提交在 2025-11-07。三种外壳里的研究都由 GPT Researcher 自己经 LangChain 调模型、用自己的 key，没有一种把推理交给宿主 agent。能绕开模型的是它的检索器、抓取器、BM25 筛选这几块，以及 `quick_search()`（首个检索器不是 MCP 时零次模型调用）。维护活跃（近 12 个月 468 个提交、93 位作者），但测试 2026-08 才进 CI，PyPI 0.16.0 在 Python 3.12/3.13 上一 import 就报错、挂了 70 天，默认的 BM25 段落筛选 2026-09-26 才进代码，2026-07-14 一天按「积压清理」关掉 110 个 issue；LICENSE 是 Apache-2.0，包元数据与维护者在 issue 里的说法是 MIT，硬依赖里有 AGPL 的 PyMuPDF。
>
> 怎么读：第 1 节逐条对账 README 与代码；第 2 节是主流程，2.4 检索器、2.5 引用、2.6 模型、2.7 三种外壳是这次重点；第 5 节列与平台文献阶段的对照和会碰到的规则，只写事实。横向对比见同目录 [README.md](README.md)。

## 1. 是不是

README 的每条能力说法回到代码里对账。「判断」一栏只描述代码现状。

| README 的说法 | 代码里 | 判断 | 证据 |
|---|---|---|---|
| planner 生成问题、execution agents 并行收集、publisher 汇总成报告（`README.md:56,62-67`） | 一次 STRATEGIC 模型调用出 3 条子查询（`MAX_ITERATIONS`），加原问题共 4 条，`asyncio.gather` 并行处理；一次 SMART 模型调用流式写报告。没有独立 agent 进程，也没有循环 | 有；实质是两次提示词调用加一组协程 | `gpt_researcher/actions/query_processing.py:109-156`、`gpt_researcher/skills/researcher.py:365-405`、`gpt_researcher/actions/report_generation.py:291-306` |
| 按任务创建专门 agent（`README.md:63`） | `choose_agent` 一次 SMART 调用，返回 emoji 名字与一段角色提示词，作为写报告时的 system prompt；解析不出退到固定的 "Default Agent" | 有 | `gpt_researcher/actions/agent_creator.py:41-71,115-119` |
| 逐个来源摘要并追踪来源（`README.md:66`） | 默认路径不逐来源调模型：页面切块后按 BM25（或 Jev、embeddings）挑块，原文块前挂 `Source: <url>` 进上下文。`summarize_url` 在 `actions/__init__.py` 导出但全仓零调用，`generate_summary_prompt` 零调用（grep 全仓，含 tests） | 摘要这一步不存在；来源追踪是每块前面的字符串。2023 年的设计博客写的是「用模型对事实做摘要」（`docs/blog/2023-09-22-gpt-researcher/index.md:35-37`），现行代码已换掉 | `gpt_researcher/context/select.py:53-101`、`gpt_researcher/prompts.py:518,555-561`、`gpt_researcher/actions/report_generation.py:115-157`、`gpt_researcher/actions/__init__.py:5,17` |
| 聚合 20 个以上来源（`README.md:80`） | 每条查询默认 5 条结果，初搜 1 次加子查询 4 次，按 URL 去重，单检索器时最多约 25 页 | 数量级对得上 | `gpt_researcher/config/variables/default.py:22,26`、`gpt_researcher/skills/researcher.py:851-934` |
| Deep Research：树状、并发、约 5 分钟、约 $0.4（o3-mini high）（`README.md:214-224`） | 树与并发都在（[2.3 节](#23-deep-research)）。成本数字无法用它自己的计数器得出：deep 模式三处模型调用不传 `cost_callback`，嵌套研究器的花费留在各自对象里、不回加父对象；默认 STRATEGIC 模型已是 gpt-5.4 | 结构有；成本口径没有代码支撑 | `gpt_researcher/skills/deep_research.py:287-294,341-348,373-382,442-457,610` |
| Deep Research 先生成追问澄清方向 | 追问生成了，答案写死成 "Automatically proceeding with research" | 只有形式 | `gpt_researcher/skills/deep_research.py:594-600` |
| Jev 段落筛选，默认（`README.md:226-248`） | `CONTEXT_FILTER=auto`：有 `TYPESAFE_API_KEY` 用 Jev，否则 BM25；两者都不需要 embeddings。这两个文件 2026-09-26 才进代码，此前默认是 embeddings（要 OpenAI 的 embedding key）[^jevcommit] | 有，README 自己也写了回落；代码只有一天历史 | `gpt_researcher/context/select.py:38-46`、`gpt_researcher/context/jev_filter.py:1-15` |
| 学术检索 | arXiv、Semantic Scholar、OpenAlex、PubMed Central 四个实现在，都只回 title / href / body，见 [2.4 节](#24-检索器与学术源) | 有，薄 | `gpt_researcher/retrievers/` |
| 本地文档研究（`README.md:274-286`） | `DOC_PATH` 下 pdf、docx、pptx、csv、xlsx、md、txt 等由 LangChain loader 读入；但本地模式仍先用第一个检索器联网搜一次原问题来拆子查询 | 有；「只用本地」不成立 | `gpt_researcher/document/document.py:69-82`、`gpt_researcher/skills/researcher.py:166-173,365-366` |
| 研究过程保持记忆（`README.md:84`） | `Memory` 只是 embedding 模型工厂；同一次运行内靠 `visited_urls` 与 `context` 串起来，跨运行不存任何东西 | 仅限单次运行 | `gpt_researcher/memory/embeddings.py:57-74`、`gpt_researcher/skills/researcher.py:108-111` |
| 行内配图 `IMAGE_GENERATION_ENABLED=true`（`README.md:194-212`） | `ImageGenerator` 用大写名 `getattr(self.cfg, 'IMAGE_GENERATION_ENABLED', False)` 读配置，而 `Config` 只设小写属性、没有 `__getattr__`；全仓只有 `llm_provider/image/image_generator.py` 用小写名读 | 读代码看恒为 False，走不通（未实测） | `gpt_researcher/skills/image_generator.py:53`、`gpt_researcher/config/config.py:72-76`、`gpt_researcher/llm_provider/image/image_generator.py:435` |
| MCP client：接 GitHub 等 MCP 数据源（`README.md:159-190`） | `MCPRetriever`：一次 STRATEGIC 模型调用从全部工具里选 ≤3 个，再让 STRATEGIC 模型 `bind_tools` 去调；依赖 `langchain-mcp-adapters` 只在 requirements.txt，不在 PyPI 硬依赖。缺这个包时 `retrievers/mcp/__init__.py` 把 `MCPRetriever` 设成 `None`、打一行 warning，`get_retrievers` 再把 `mcp` 这个名字换成默认的 Tavily 检索器 | 有；pip 安装后缺包，传了 `mcp_configs` 也不走 MCP，静默多出一个 Tavily 检索器（读代码推断，未实测） | `gpt_researcher/retrievers/mcp/retriever.py:116-199`、`gpt_researcher/mcp/tool_selector.py:145-155`、`gpt_researcher/mcp/research.py:50-80`、`gpt_researcher/retrievers/mcp/__init__.py:11-27`、`gpt_researcher/actions/retriever.py:191`、`requirements.txt:62` |
| 配置项 `MCP_SERVERS`、`MCP_ALLOWED_ROOT_PATHS` | `Config.__init__` 读完配置后把两者重置成 `[]` | 配了不生效 | `gpt_researcher/config/config.py:53-61` |
| 作为 Claude Skill 安装扩展深度研究能力（`README.md:44-52`） | 装下去的是开发说明书，见 [2.7 节](#27-三种外壳) | 与说法不符 | `.claude/SKILL.md:1-4` |
| MCP Server 已迁到 gptr-mcp（`README.md:289-301`） | 在另一仓库；主仓 `.mcp.json` 另写了一个起不来的入口，见 2.7 节 | 两处不一致 | `.mcp.json:1-10`、`mcp-server/README.md:1-3` |
| 导出 PDF、Word（`README.md:85`） | 在 `backend/utils.py`，不在 PyPI 包内 | 核心包没有 | `backend/utils.py:97-98`、PyPI wheel 目录[^wheel] |
| 可执行 JavaScript 的抓取（`README.md:83`） | 默认抓取器 `bs` 不执行 JS；`SCRAPER=browser`（selenium，只在 extra `requirements-txt`）或 `SCRAPER=nodriver`（要 `zendriver`，哪份依赖清单里都没有）才执行 | 有，默认关，依赖要自己装 | `gpt_researcher/config/variables/default.py:28`、`gpt_researcher/scraper/scraper.py:324-333`、`gpt_researcher/scraper/browser/nodriver_scraper.py:140-145`、`pyproject.toml:203` |
| 多智能体助手（LangGraph / AG2，参考 STORM，`README.md:304-311`） | `multi_agents/` 在仓库、不在 wheel；其中 fact checker 是一次模型调用审稿，不去抓引用页 | 有，属示例 | `multi_agents/agents/fact_checker.py:10-32` |

代码里有、README 没说清的几样：检索器用 `requires_scraping` 声明「返回的是要抓的链接还是已取好的全文」（`gpt_researcher/retrievers/base.py:1-61`）；第三方包可以用 entry point `gpt_researcher.retrievers` 注册检索器（`gpt_researcher/actions/retriever.py:139-147`）；`source_urls` 加 `complement_source_urls` 可以只研究给定链接或给定链接加网搜（`gpt_researcher/skills/researcher.py:145-162`）；`write_report(custom_prompt=…)` 整段替换报告提示词（`gpt_researcher/actions/report_generation.py:255-256`）。

## 2. 怎么做

### 2.1 入口与数据进出

| 入口 | 做什么 | 模型调用次数（默认配置） | 证据 |
|---|---|---|---|
| `GPTResearcher(query, report_type, report_source, source_urls, …)` | 读配置、按名字选检索器类，不发请求 | 0 | `gpt_researcher/agent.py:53-201` |
| `quick_search(query)` | 用第一个检索器搜一次，原样返回 `[{title, href, body}]`；`aggregated_summary=True` 才多一次 SMART 调用；`all_retrievers=True` 并发搜全部检索器按 URL 去重。第一个检索器是 MCP 时，MCP 检索器自己会调模型选工具、调工具 | 0（或 1；MCP 另计） | `gpt_researcher/agent.py:531-618` |
| `conduct_research()`，标准 | 选角色 1 次 SMART、拆子查询 1 次 STRATEGIC；检索、抓取、挑段落不调模型 | 2 | `gpt_researcher/agent.py:367-392`、`gpt_researcher/actions/query_processing.py:117-127` |
| `conduct_research()`，传了 `agent`、`role` 与 `source_urls` | 跳过选角色与拆子查询，只抓给定 URL、BM25 挑段落 | 0 | `gpt_researcher/agent.py:367`、`gpt_researcher/skills/researcher.py:145-147,245-261` |
| `conduct_research()`，`report_type="deep"` | 递归树，见 2.3 | 约 32 | `gpt_researcher/agent.py:363-365` |
| `write_report()` | 一次 SMART 流式调用 | 1 | `gpt_researcher/actions/report_generation.py:291-306` |

数据进：一句问题；配置来自环境变量或 JSON 文件（`CONFIG_PATH`），环境变量优先（`gpt_researcher/config/config.py:72-76,157-178`）；可选 `source_urls`、`document_urls`、`DOC_PATH`、LangChain 文档或向量库、`mcp_configs`。

数据出：`write_report()` 返回 markdown 字符串；`get_research_context()` 返回进提示词的上下文；`get_source_urls()` 返回 `visited_urls`，即准备去抓的全部 URL（抓之前就加进去，抓失败的也在，`gpt_researcher/skills/researcher.py:813-834`），不是被引用的那些；`get_research_sources()` 返回抓取成功的页面 `{url, raw_content, image_urls, title}`（抓取失败的在 `Scraper.run` 里被滤掉，`gpt_researcher/skills/browser.py:55-58`、`gpt_researcher/scraper/scraper.py:153-158`），但 PubMed Central 这类「检索器已给全文」的来源在这里只记 `{url}`、不带正文（`gpt_researcher/skills/researcher.py:910,922`），本地文档不进这个列表；`get_costs()` / `get_step_costs()` 是美元（`gpt_researcher/agent.py:761-775`）。默认路径（web 来源、`bs` 抓取器、不配图）不留文件：落盘日志的 `setup_research_logging` 全仓零调用（`gpt_researcher/utils/logging_config.py:38-76`），PyMuPDF 的临时文件用完即删（`gpt_researcher/scraper/pymupdf/pymupdf.py:56-70`）；配置文件里 `REPORT_SOURCE` 不是 web 时会 `os.makedirs(DOC_PATH)`（`gpt_researcher/config/config.py:50-51,253-255`，读的是配置字典，不是环境变量）。非默认路径会写：`document_urls` 下载的临时文件不删（`gpt_researcher/document/online_document.py:57-59`）、selenium 抓取器存 cookie（`gpt_researcher/scraper/browser/browser.py:198`）、nodriver 调试截图写 `logs/screenshots`（`gpt_researcher/scraper/browser/nodriver_scraper.py:234-240`）、配图写图片文件（`gpt_researcher/llm_provider/image/image_generator.py:321-322`）。stdout 上不干净：核心包 32 个文件里有 89 处 `print(`；写报告的流式正文在没有 websocket 时逐段 print 到 stdout，这由 `GenericLLMProvider.verbose` 决定，它默认 True 且 `create_chat_completion` 从不传这个参数，所以 `GPTResearcher(verbose=False)` 也关不掉（`gpt_researcher/llm_provider/generic/base.py:118-121,400-404`、`gpt_researcher/utils/llm.py:117`）。

### 2.2 标准研究的一次运行

`report_type="research_report"`、`report_source="web"`、默认配置下，一次 `conduct_research()` + `write_report()`：

1. **选角色**：SMART，temperature 0.15，返回 `{server, agent_role_prompt}`，先 `json_repair` 再正则兜底，都不行用默认角色（`gpt_researcher/actions/agent_creator.py:41-130`）。
2. **初搜**：第一个检索器搜原问题，取 5 条（`gpt_researcher/skills/researcher.py:50-66`）。
3. **拆子查询**：初搜结果（含片段或摘要）整段塞进提示词，要 3 条纯自然语言查询、禁止 `site:` 这类操作符（`gpt_researcher/prompts.py:212-259`）。STRATEGIC、`reasoning_effort=medium`；失败先带 `max_tokens` 重试，再退到 SMART；`json_repair` 解析，解析不出就用原问题（`gpt_researcher/actions/query_processing.py:117-156`）。自定义 `PromptFamily` 不进这一步：调用链上没传 `prompt_family`（`gpt_researcher/skills/researcher.py:83-93`）。
4. **加原问题**，共 4 条（`gpt_researcher/skills/researcher.py:370-371`）；初搜结果的页面先抓一遍，作为单独一段上下文（`gpt_researcher/skills/researcher.py:387-391,836-849`）。
5. **4 条并行**：每条对每个非 MCP 检索器搜 5 条（`asyncio.to_thread`）；按 `requires_scraping` 分成「要抓的 URL」与「检索器已给全文」；新 URL 进 `visited_urls` 去重后打乱顺序（`gpt_researcher/skills/researcher.py:851-934`）。
6. **抓取**：默认 BeautifulSoup，15 个 worker；路径以 `.pdf` 结尾走 PyMuPDF，链接含 `arxiv.org` 走 ArxivScraper；先过 SSRF 校验；丢弃不足 100 字符、反爬挑战页、无标点的大词表页；HTML 抓取器拿到 PDF 原始字节时改用 PyMuPDF 重试（`gpt_researcher/scraper/scraper.py:194-274,307-352`）。
7. **挑段落**：每页先截到前 5 万字符（`gpt_researcher/context/retriever.py:9-13,29`），切 1000 字符的块。`keyword`：BM25，保留得分不低于最高分一半的块，最多 25 块（`gpt_researcher/context/select.py:34-35,99-101`、`gpt_researcher/context/lexical.py:95-104`）；`jev`：每块调一次 TypeSafe API 打 0 到 3 分，取 ≥1.5 的（`gpt_researcher/context/jev_filter.py:84-119,167-184`）；`embeddings`：余弦相似度 >0.42（`gpt_researcher/config/variables/default.py:6`）。总量不到 8000 字符且不超过 10 页时不筛，整页进（`gpt_researcher/context/select.py:74-77`、`gpt_researcher/skills/context_manager.py:56-64`）。BM25 与 embeddings 都在本机算，Jev 每块一次 HTTP 请求。
8. **拼上下文**：每块以 `Source: url / Title: / Content:` 开头，各段用空格拼成一个字符串；整段出异常返回 `[]`（`gpt_researcher/skills/researcher.py:399-408`、`gpt_researcher/prompts.py:555-561`）。
9. **可选策展**：`CURATE_SOURCES` 默认关，开了多一次 SMART 调用挑来源（`gpt_researcher/config/variables/default.py:18`、`gpt_researcher/skills/researcher.py:211-229`）。
10. **写报告**：上下文为空直接返回一段「没找到材料」的固定文本，不调模型（`gpt_researcher/skills/writer.py:79-88`）。否则 system 是角色提示词，user 是报告提示词：至少 `TOTAL_WORDS`（1200）词、APA 格式、每个实质性结论带内联超链接引用、末尾参考列表（`gpt_researcher/prompts.py:262-316`）。SMART 流式；失败改成单条 user 消息再试一次，再失败 print 一行错误、返回空字符串（`gpt_researcher/actions/report_generation.py:291-326`）。写报告这一步同样不用自定义 `PromptFamily`：`ReportGenerator` 传参里没有它（`gpt_researcher/skills/writer.py:38-47,107-124`）。

`detailed_report` 模式的编排在 `backend/`（不在 PyPI 包内）：先做一次标准研究，一次 SMART 调用拆子主题，每个子主题新建一个研究器写一节，再写导言、结论，末尾把 `visited_urls` 全部列成 References（`backend/report_type/detailed_report/detailed_report.py:84-205`）。

### 2.3 deep research

入口：`report_type="deep"`（`gpt_researcher/agent.py:192-193,363-365`）。默认宽 `DEEP_RESEARCH_BREADTH=3`、深 `DEEP_RESEARCH_DEPTH=2`、并发 4（`gpt_researcher/config/variables/default.py:40-42`；文档写的默认宽度是 4，`docs/docs/gpt-researcher/gptr/deep_research.md:52`）。

1. **研究计划**：每个检索器搜一次原问题；STRATEGIC、high，生成 3 条追问；答案写死，拼成一段「原问题 + 追问与答案」（`gpt_researcher/skills/deep_research.py:298-350,594-600`）。
2. **一层**：STRATEGIC 生成 `breadth` 条 `{query, researchGoal}`（`gpt_researcher/skills/deep_research.py:265-296`）；每条在信号量内新建一个 `GPTResearcher(report_type="research_report", report_source="web")`，共享父对象的 `visited_urls`，只跑 `conduct_research()`（即 2.2 的 1 到 8 步）（`gpt_researcher/skills/deep_research.py:432-457`）；再用 STRATEGIC、high 从这段上下文里抽 `learnings`（每条带 `sourceUrl`）与后续问题（`gpt_researcher/skills/deep_research.py:352-384`）。
3. **往下**：对本层每个结果，按顺序递归一次，宽度 `max(2, breadth // 2)`、深度减 1，查询是「上一层的 researchGoal + 后续问题」（`gpt_researcher/skills/deep_research.py:523-560`）。
4. **收尾**：`learnings`（有 URL 的后面挂 `[Source: url]`）加各层原始上下文，从尾部往前保留到 2.5 万词（`gpt_researcher/skills/deep_research.py:18,219-237,619-641`）；`write_report()` 用 deep 专用提示词（`gpt_researcher/prompts.py:418-487`）。

按默认参数数调用（读代码推算，未实跑）：研究计划 1 + 第一层（1 + 3 个研究 × 3 次）+ 第二层 3 个分支 ×（1 + 2 个研究 × 3 次）= 32 次研究期模型调用，加写报告 1 次共 33 次；嵌套研究器 9 个，单检索器时约 46 次检索。deep 自己的三处模型调用都不传 `cost_callback`（`gpt_researcher/skills/deep_research.py:287-294,341-348,373-382`），嵌套研究器的花费不回加，所以一次 deep 运行结束后 `get_costs()` 只剩写报告那一次（推断，未实测）。

两条停止保护：生成 0 条查询就停（#2110[^i2110]），一层全部失败就停（#1579[^i1579]）（`gpt_researcher/skills/deep_research.py:421-429,505-520`）。

### 2.4 检索器与学术源

内置 21 个名字（`gpt_researcher/actions/retriever.py:49-136`），`RETRIEVER=arxiv,openalex` 逗号分隔可多选：初搜只用第一个，子查询打全部非 MCP 检索器（`gpt_researcher/skills/researcher.py:58-64,861-865`）。名字写错时 `Config` 打一行警告后整体回落 Tavily（`gpt_researcher/config/config.py:78-84,189-202`）。

| 检索器 | 要 key 吗 | 返回什么 | 之后怎么处理 | 证据 |
|---|---|---|---|---|
| `tavily`（默认） | `TAVILY_API_KEY`；没有时 print 一行，请求失败被吞，返回空列表 | href + 片段 | 声明要抓，抓页面 | `gpt_researcher/retrievers/tavily/tavily_search.py:25,52-61,108-156`、`gpt_researcher/actions/retriever.py:196-204` |
| `arxiv` | 不要 | title、href = `pdf_url`、body = 摘要；作者、日期、arXiv 号不带 | arXiv 的 `pdf_url` 形如 `https://arxiv.org/pdf/<id>v1`，没有 `.pdf` 后缀[^arxivapi]，被路由到 ArxivScraper，它按 ID 再查一次 API，只拼「发表日期 + 作者 + 摘要」，不下载 PDF；body 里的摘要本身被丢掉（未声明 `requires_scraping`、没有 `raw_content`） | `gpt_researcher/retrievers/arxiv/arxiv.py:15-50`、`gpt_researcher/scraper/scraper.py:340-346`、`gpt_researcher/scraper/arxiv/arxiv.py:35-68`、`gpt_researcher/skills/researcher.py:887-926` |
| `semantic_scholar` | 代码不带 key 头；本机无 key 连调三次都是 429[^s2]，此时检索器 print 后返回空 | 只保留 `isOpenAccess` 且有 `openAccessPdf` 的；请求了 authors、year、venue 但不用；代码给 `/paper/search` 传 `sort`，而官方 API 规范里这个端点没有 `sort` 参数（只有 `/paper/search/bulk` 有）[^s2spec] | 抓 PDF；PDF 在 arxiv.org 上时同上只得摘要 | `gpt_researcher/retrievers/semantic_scholar/semantic_scholar.py:11,36-73` |
| `openalex` | 可选 `OPENALEX_EMAIL`、`OPENALEX_API_KEY` | href 依次取开放 PDF、落地页、OpenAlex ID；body 是由倒排索引拼回的摘要 | 摘要同样被丢，只抓 href。实看一个 PINN 查询前 5 条，3 条没有开放 PDF，href 是 doi.org 落地页[^openalex] | `gpt_researcher/retrievers/openalex/openalex.py:44-114` |
| `pubmed_central` | 可选 `NCBI_API_KEY`，没有时限流 | 从 XML 抽标题、摘要、正文拼成全文 | 声明 `requires_scraping = False`，直接进上下文 | `gpt_researcher/retrievers/pubmed_central/pubmed_central.py:12-23,86-172` |
| `duckduckgo` | 不要 key，要 `ddgs` 包；PyPI 硬依赖里写的是 `duckduckgo-search` | href + 片段（截到 100 字符） | 抓页面；缺 `ddgs` 时构造即 `ImportError` | `gpt_researcher/retrievers/duckduckgo/duckduckgo.py:19,29-35`、`pyproject.toml:55`、`requirements.txt:28` |
| `mcp` | 看所接的 MCP server | 模型调工具得到的文本 | 走 MCP 专用分支；同步 `search()` 在异步流程里起新线程新事件循环，最长等 5 分钟 | `gpt_researcher/retrievers/mcp/retriever.py:201-298`、`gpt_researcher/skills/researcher.py:665-737` |
| 其余 | google、bing、brave、serper、serpapi、searchapi、searx、exa、crw、bocha（博查中文网页搜索，要 `BOCHA_API_KEY`）、groundroute、xquik、getxapi、custom | | | `gpt_researcher/actions/retriever.py:49-136`、`gpt_researcher/retrievers/bocha/bocha.py:23,31` |

学术相关的共同事实：

- 检索器接口只有 `{title, href, body}`（外加可选 `raw_content`），书目元数据没有字段可放，报告里的「引用」最多是标题加 URL；只有 arXiv 条目因为 ArxivScraper 把作者和日期写进正文，模型才可能写出作者-年份格式（`gpt_researcher/scraper/arxiv/arxiv.py:59-66`）。
- 抓到的 PDF 由 PyMuPDFLoader 逐页取纯文本拼接（`gpt_researcher/scraper/pymupdf/pymupdf.py:64-80`），再截到前 5 万字符；下载时 SSL 校验失败会以 `verify=False` 重试（`gpt_researcher/scraper/pymupdf/pymupdf.py:44-53`）。
- 没有 GitHub、Hugging Face、Zenodo、Papers with Code 这类找代码与数据的检索器，也没有知网、万方等中文学术源；中文只有 bocha 这一个通用网页搜索。README 的 MCP 例子用的是 GitHub MCP server（`README.md:175-184`）。
- BM25 分词用 `\w+`，不切中文：两个标点或空格之间的一串汉字是一个 token；和查询一个词都交不上时回落到 `chunks[:25]`，即按页面顺序排在最前的 25 块，页面长时这 25 块全来自第一页（`gpt_researcher/context/lexical.py:19,44-45,95-101`）。中文题目下段落筛选大概率退化成取第一页开头（推断，未实测）。

### 2.5 引用怎么进报告

1. 每个段落块前挂 `Source: <url>` 与 `Title:`（`gpt_researcher/prompts.py:555-561`、`gpt_researcher/context/retriever.py:24-36`）。
2. 写报告提示词要求：每个实质性结论、数字、引语带 `([in-text citation](url))`；不许引用上下文里没有的来源；末尾写 APA 参考列表（`gpt_researcher/prompts.py:277-289,309-312`）。
3. 运行路径上不核对。`gpt_researcher/` 里搜 citation，命中的只有提示词、deep 模式的解析、MCP 结果的格式化；没有任何代码检查报告里的 URL 是否在 `visited_urls` 里，更没有检查原文是否支持那句话。#1572 的讨论里有人提议「生成后把不在上下文里的 URL 删掉」，维护者关 issue 时只加了空上下文判空，没做这一步[^i1572]。
4. deep 模式里 `learnings` 的 `sourceUrl` 由模型填，原样挂进上下文，不校验（`gpt_researcher/skills/deep_research.py:361-371,158-170,621-626`）。#1572 的讨论里有人报告 deep 模式的 learnings 会编来源[^i1572]。
5. 参考列表：`research_report` 靠模型自己写；`detailed_report` 把 `visited_urls` 排序全列，里面有没被引用的、也有抓取失败的（`gpt_researcher/actions/markdown_processing.py:101-126`、`gpt_researcher/skills/researcher.py:821-823`）。
6. 粒度：URL 级。PDF 引到 PDF 链接；本地文档引到文件名（`gpt_researcher/document/document.py:54-61`）；没有页码、段落号、DOI、BibTeX。
7. 能事后核：`get_research_sources()` 留着抓取成功的页面全文（检索器直接给全文的来源只留 URL，见 2.1），`get_research_context()` 留着真正进提示词的块（`gpt_researcher/agent.py:684-698,753-759`），调用方可以拿报告里的 URL 回去对原文。
8. 作者的量化：`deep_agents/` 例子里，用 LangChain deepagents 作宿主、gpt-5.4 作模型，在 DeepResearch Bench 抽的 10 道英文题上，GPT Researcher 工具组的引用精确率 56.0%（原生 Tavily 搜索组 53.9%），每篇被评测模型核实为支持的引用 35.2 条（`deep_agents/BENCHMARK.md:8,17,27-28,35-38`）。仓库里另有两个离线评测，都不在运行路径上：`evals/quality_eval` 的 `citation_faithfulness` 只比对域名（`evals/quality_eval/metrics.py:68-131`）；同文件的 `unsupported_claim` 让评测模型逐条判断结论是否被上下文支持，但每条只给上下文的前 4000 字符（`evals/quality_eval/metrics.py:451-467`）。

### 2.6 怎么调模型

- **三档模型**：FAST 只在配图里用；SMART 管选角色、写报告、导言与结论、拆子主题、策展；STRATEGIC 管拆子查询、deep research、MCP 选工具与调用（按 `grep` 调用点：`gpt_researcher/skills/image_generator.py:236`、`gpt_researcher/actions/report_generation.py:39-310`、`gpt_researcher/actions/query_processing.py:119`、`gpt_researcher/skills/deep_research.py:290`、`gpt_researcher/mcp/tool_selector.py:149`、`gpt_researcher/mcp/research.py:56`）。
- **默认值**：`FAST_LLM=openai:gpt-5.4-mini`、`SMART_LLM` 与 `STRATEGIC_LLM=openai:gpt-5.4`、`EMBEDDING=openai:text-embedding-3-small`、`RETRIEVER=tavily`（`gpt_researcher/config/variables/default.py:4-10`）。默认 BM25 筛选下 embedding 模型不会被构造（`gpt_researcher/agent.py:177-179`、`gpt_researcher/context/select.py:63-66`）。
- **接法**：`provider:model` 字符串，27 个 provider 全走 LangChain 的 chat 类（`gpt_researcher/llm_provider/generic/base.py:13-41,146-358`、`gpt_researcher/config/config.py:204-222`）。`create_chat_completion` 按模型名单决定传不传 temperature 与 `reasoning_effort`，`LLM_KWARGS` 可覆盖；失败最多重试 10 次、指数退避封顶 8 秒（流式且有 websocket 时只试 1 次）；每次成功按返回的 usage 算美元（`gpt_researcher/utils/llm.py:41-162`）。拆子查询那一步自己还有三级回落（STRATEGIC、带 `max_tokens` 的 STRATEGIC、SMART），每级各自重试，最坏 30 次请求（`gpt_researcher/actions/query_processing.py:117-154`）。
- **成本口径**：价格表只有 OpenAI 与 Anthropic 的型号；不在表里的模型（DeepSeek、Ollama 本地模型等）按固定的每百万 token 输入 $5、输出 $15 算，没有返回 usage 时用 tiktoken 的 `o200k_base` 估 token 数（`gpt_researcher/utils/costs.py:13-14,31-62,71-98,306-314`）。所以本地模型也会报出一个非零美元数，不会是空值；tiktoken 第一次用要联网下载编码表，CI 为此专门在断网测试前预热（`.github/workflows/tests.yml:110-123`）。
- **换 Anthropic**：设 `ANTHROPIC_API_KEY`，把三档改成 `anthropic:<model>`。`langchain-anthropic` 不在 PyPI 硬依赖（只在 extra `requirements-txt`，`pyproject.toml:182-204`），仓库的 `requirements.txt` 也没有；第一次构造时 `_check_pkg` 用 `sys.executable -m pip install -U langchain-anthropic` 当场安装（`gpt_researcher/llm_provider/generic/base.py:160-164,407-425`）。名单里的 Claude 4.x 型号不传 temperature（`gpt_researcher/llm_provider/generic/base.py:66-74`、`gpt_researcher/utils/llm.py:89-96`）。官方文档的 Anthropic 例子还是 claude-2.1 / claude-3-opus（`docs/docs/gpt-researcher/llms/llms.md:170-178`）；`.env.example` 写的 token 上限默认值（3000/6000/4000）与代码（6000/12000/8000）不一致（`.env.example:71`、`gpt_researcher/config/variables/default.py:14-16`）。Claude Haiku 4.5 下 deep 模式曾解析出 0 条查询（#1772[^i1772]），现在先要 JSON、`json_repair` 解析，解析不出再按行正则回落（`gpt_researcher/skills/deep_research.py:62-122`）。
- **只认各家 API 的凭据**：全部经 LangChain / SDK 走 HTTP API（API key，Bedrock、Vertex 走各自云账号的凭据链）；`gpt_researcher/`、`backend/`、`multi_agents/`、`deep_agents/` 里搜不到 Claude Code、Codex、claude_agent_sdk 的任何引用，没有对接命令行登录；本地模型可以用 `ollama`、`vllm_openai` 或 `OPENAI_BASE_URL` 指向兼容接口（`gpt_researcher/llm_provider/generic/base.py:151-153,194-204,299-306`）。

### 2.7 三种外壳

| 形态 | 在哪 | 实际执行什么 | 谁调模型、要谁的 key | 证据 |
|---|---|---|---|---|
| Claude skill（skills.sh） | `.claude/SKILL.md` 226 行 + `references/` 12 份，共 2276 行，没有 scripts | 一份开发说明：Python 快速上手、文件地图、加检索器与加功能的步骤、配置、易错点。description 原话是「帮开发者理解、扩展、调试、集成 GPT Researcher 时用」 | 宿主只按说明写、跑 Python；研究本身由 `GPTResearcher` 调它配置的模型（默认 OpenAI）与 Tavily，key 从环境变量读 | `.claude/SKILL.md:1-4,10-29`、skills.sh 条目页[^skillssh] |
| 为什么装的是上面这份 | | skills CLI 先在仓库根下走一层子目录，`.claude/` 目录里的 `SKILL.md` 先命中；`skills/gpt-researcher/SKILL.md` 与它同名，按名字去重被跳过 | | `vercel-labs/skills:src/skills.ts:253-308`[^skillsts]（读代码推断，没跑 `npx`） |
| Codex 插件 | `.codex-plugin/plugin.json` + `skills/gpt-researcher/SKILL.md`（12 行）+ `.mcp.json` | SKILL.md 只有一句「Use GPT Researcher from Codex via MCP」；`.mcp.json` 起 `uvx gpt-researcher` | PyPI 0.16.1 的 wheel 没有 `entry_points.txt`，`pyproject.toml` 也没有 `[project.scripts]`，不存在名为 `gpt-researcher` 的可执行文件，uvx 起不来（读 wheel 推断，未跑）。这组文件是外部贡献者 2026-04-05 提交的[^plugincommit] | `.codex-plugin/plugin.json:15,23`、`.mcp.json:1-10`、`skills/gpt-researcher/SKILL.md:1-12`、wheel[^wheel] |
| gptr-mcp（独立仓库） | assafelovic/gptr-mcp，MIT，最后提交 2025-11-07 | FastMCP：工具 `deep_research`、`quick_search`、`write_report`、`get_research_sources`、`get_research_context`，资源 `research://{topic}`，prompt `research_query`；stdio / SSE / streamable-http；会话对象存在进程内存里 | `deep_research` 工具就是 `GPTResearcher(query)` 默认 `research_report` 加 `conduct_research()`，不是 deep 模式，返回上下文与来源，报告另调 `write_report`；启动时没有 `OPENAI_API_KEY` 直接退出（配了别家模型也一样）；来源列表里的 `content_length` 读的键名是 `content`，而来源字典用的是 `raw_content`，恒为 0；`mcp.run()` 返回后落进 `while True: pass` 空转。这几处都有人提了 issue 或 PR（#25、#30、#31、#33），都开着没合[^gptrmcpissues]。stdio 模式下 stdout 就是协议通道，而核心包会往 stdout print（见 2.1），`write_report` 的流式正文也会 print 出来；这对 stdio 客户端有什么影响没实测 | `gptr-mcp/server.py:45-46,93-137,177-209,277-312`、`gptr-mcp/utils.py:61-67`[^gptrmcp] |
| 核心包（PyPI） | wheel 只有 `gpt_researcher/` | `backend/`、`multi_agents/`、`deep_agents/`、`cli.py`、PDF / Word 导出都不在包内 | 见 2.1 表：`quick_search` 0 次；给 URL 并预设角色 0 次；标准研究 2 + 1 次 | wheel[^wheel] |
| deep_agents 例子（仓库内） | LangChain deepagents 作宿主，把 `quick_search` 与「`conduct_research` + `write_report`」包成两个工具 | 宿主负责规划、分派子 agent、审稿、拼终稿；GPT Researcher 在工具里跑自己的完整流水线，工具返回的报告末尾附全部 `visited_urls` | 两层都调模型：宿主的模型写在 `task.json`，GPT Researcher 用自己的环境变量 | `deep_agents/tools.py:9-78`、`deep_agents/task.json:3` |

三种外壳里，「选角色」「拆子查询」「写报告」这几次模型调用都在 GPT Researcher 进程里、用它自己的配置和 key；宿主 agent 最多拿到上下文后自己再写一遍（gptr-mcp 的 `deep_research` 只返回上下文就是这种用法，但选角色与拆子查询仍由它的模型完成）。完全不碰模型的用法：直接调它的检索器类、抓取器、`select_context` 的 keyword 模式；`quick_search()`（首个检索器不是 MCP）；或者 `GPTResearcher(agent=…, role=…, source_urls=[…])` 再 `conduct_research()`，只抓给定链接、BM25 挑段落（见 2.1 表）。

## 3. 为什么

### 3.1 设计理由

| 设计 | 解决什么 | 证据 |
|---|---|---|
| 先列出一组子问题、再逐条确定执行，不用 AutoGPT 式的自主循环 | 保证在固定时间内结束，作者称任务完成率由此到 100% | `docs/blog/2023-09-22-gpt-researcher/index.md:18-27` |
| 多抓站点，让模型只改写给定内容 | 作者的假设：来源越多偏差越小；模型只做改写可以少编造 | `docs/blog/2023-09-22-gpt-researcher/index.md:29-39`、`README.md:357` |
| asyncio 并行抓取 | 速度，博客称约 3 分钟一篇、比 AutoGPT 快 85% | `docs/blog/2023-09-22-gpt-researcher/index.md:43-56` |
| 参照 Plan-and-Solve 与 RAG；详细报告与多智能体参照 STORM | 先规划再检索增强生成；长报告按子主题分节写。STORM 另见同目录 [storm.md](storm.md) | `README.md:27,307`、`backend/report_type/detailed_report/README.md:3` |
| 段落筛选从 embeddings 改成 Jev，没有 key 时用 BM25（2026-09-26 进代码[^jevcommit]） | 不再需要 embedding 的 key；作者在 28 题回放上测得相关段落占比 Jev 73%、BM25（放出的 `keyword` 配置）51%、embeddings 46%，每篇成本 $0.115 / $0.116 / $0.117。「相关」由 gpt-5.4-mini 评判，写报告的是 gpt-5.4 | `README.md:226-248`、`evals/context_filter/README.md:17-23,45-47,58-59,76-77,104-110`、`gpt_researcher/context/select.py:1-14` |
| 检索器显式声明 `requires_scraping` | 取代「内容超过 100 字符就当全文」的猜测，那个猜测让页面不被抓、引用无从核 | `gpt_researcher/retrievers/base.py:1-30`、#1846[^i1846] |
| deep 宽度逐层减半、并发信号量、上下文截到 2.5 万词 | 控制调用次数与上下文长度 | `gpt_researcher/skills/deep_research.py:18,432,540-543` |
| MCP 的 fast / deep / disabled 三档与 Tavily MCP 去重 | 每条子查询都跑一次 MCP 太贵；直连 Tavily 与 Tavily MCP 同时开等于付两次钱（#1875[^i1875]） | `gpt_researcher/agent.py:133-136`、`gpt_researcher/skills/researcher.py:311-362,492-517` |
| MCP 配置只改本次的 `cfg`，不写 `os.environ` | 后端并发请求之间互相污染（#1676[^i1676]） | `gpt_researcher/agent.py:295-321` |
| `visited_urls` 在父子研究器间共享 | 子主题、deep 分支不重复抓同一页 | `gpt_researcher/skills/researcher.py:108-111`、`gpt_researcher/skills/deep_research.py:450` |
| 各处模型输出一律 `json_repair` 解析，失败有回落 | 各家模型 JSON 格式不稳（#1772[^i1772]） | `gpt_researcher/actions/query_processing.py:12-40,156`、`gpt_researcher/skills/deep_research.py:48-122` |
| 后端不带鉴权 | 定位为运营者部署在自己可信网络里的软件，鉴权由运营者在外层做 | `SECURITY.md:20-41`、#1694[^i1694] |

### 3.2 踩过的坑

仓库没有 CHANGELOG 文件，下面来自 issue、发布说明与 CI 注释。

| issue | 现象 | 处理 | 时间 |
|---|---|---|---|
| #1893[^i1893] | 小结果集的快速路径把 URL 丢成 `Source: None`，模型被要求引用，于是报告里几十次引 `https://example.com` | 修了元数据映射；现行 Jev 与 keyword 路径都显式取 `url` | 2026-07-13 报，次日关 |
| #1572[^i1572] | 检索什么都没拿到时，报告照样写得像模像样、来源是编的；报告人还指出 `writer.py` 不用自定义 `PromptFamily`、deep 模式抽 learnings 时也会编来源 | 写报告前判空，空就返回固定的弃权文本（`gpt_researcher/skills/writer.py:79-88`）；`PromptFamily` 没传进写报告这一步至今未改（`gpt_researcher/skills/writer.py:38-47`） | 2025-12 报，2026-08 关 |
| #1892、#1846[^i1846] | 检索片段超过 100 字符就被当成全文，页面一个都不抓，报告只靠片段写 | 先在检索器里截短片段，再引入 `requires_scraping` | 2026-07 报，2026-08 关 |
| #2100[^i2100] | 检索器直接给全文的来源不进 `visited_urls`，从 References 里消失 | 补记 `visited_urls` | 2026-09 |
| #1894[^i1894] | arxiv 库 2.2 起删了 `Search.results()`，ArxivScraper 100% 失败，而检索器照样返回标题摘要，外表看不出 | 改用 `arxiv.Client`；抓取器仍只取摘要 | 2026-07 |
| #1772[^i1772] | deep 模式按 `Query:` 前缀解析，Claude Haiku 4.5 等模型下解析出 0 条，报告在空上下文上照写 | 改成要 JSON 并 `json_repair`，按行正则留作回落 | 2026-05 |
| #1945、PR #1943[^i1945] | 没有任何 CI 跑 pytest；0.16.0 把 typing 导入放在使用之后，3.14 以下一 import 就 `NameError`，而这个版本已经发到 PyPI | 加 `tests.yml`（import 矩阵、收集检查、断网单测）；PyPI 到 0.16.1 才换掉[^wheel0160] | 2026-07-18 报，main 上 08-23 修 |
| CI 注释 | 测试之间泄漏全局状态，单独跑过、合起来跑失败 | 暂用 `--forked` 每个测试一个进程；三个依赖真实网络与 key 的测试文件从 CI 里排除 | `.github/workflows/tests.yml:125-138` |
| #1986[^i1986] | Anthropic 的 prompt cache token 按 $0 计价 | 修了成本计算 | 2026-07 报，08 关 |
| #1694[^i1694] | 未鉴权的 WebSocket 能提交 `mcp_configs` 里的任意 `command` / `args`，在服务器上起进程 | 维护者按威胁模型关为不在范围，写进 `SECURITY.md:39-41` | 2026-03 报，06 关 |

## 4. 跑起来要什么

| 项 | 要求 | 证据 |
|---|---|---|
| Python | ≥3.12；CI 测 3.12、3.13、3.14 | `pyproject.toml:30`、`.github/workflows/tests.yml:28` |
| 依赖 | PyPI 0.16.1 硬依赖 140 个，含 LangChain 全家、LangGraph、litellm、unstructured、pymupdf、weasyprint、fastapi、uvicorn、nltk 等 | wheel METADATA[^wheel] |
| 依赖清单不一致 | `tavily-python`、`ddgs`、`google-genai`、`python-pptx`、`pandas`、`langchain-mcp-adapters` 只在 `requirements.txt`；PyPI 硬依赖里是 `duckduckgo-search`，而检索器要的是 `ddgs`；`langchain-anthropic` 两边的硬依赖都没有，只在 extra `requirements-txt`。wheel 的 140 条硬依赖与仓库 `pyproject.toml` 逐条一致 | `requirements.txt:24,27-28,36,39,62`、`pyproject.toml:31-173,182-204`、wheel METADATA[^wheel] |
| 运行时自己装包 | 缺 LLM provider 包、或选了 `tavily_extract` / `firecrawl` 抓取器时，用 `sys.executable -m pip install` 当场安装 | `gpt_researcher/llm_provider/generic/base.py:407-425`、`gpt_researcher/scraper/scraper.py:160-192` |
| 模型 key | 默认 `OPENAI_API_KEY`；可换其余 26 家 provider（含本地 Ollama、vLLM）；只认各家 API 的凭据，不认 Claude Code / Codex 的登录 | `.env.example:1`、`gpt_researcher/llm_provider/generic/base.py:13-41` |
| 搜索 key | 默认 `TAVILY_API_KEY`（商业 API；维护者是 Tavily 联合创始人[^crunchbase]，README 里 PIP 包文档的链接指向 docs.tavily.com）；不要 key 的组合：arxiv、openalex、pubmed_central、duckduckgo（要装 `ddgs`）、semantic_scholar（无 key 易 429） | `.env.example:2`、`README.md:286`、2.4 节 |
| 可选 key | `TYPESAFE_API_KEY`（Jev，外部报道称 2026-09-15 开放[^jev]，代码 2026-09-26 才接入[^jevcommit]）、`NCBI_API_KEY`、`OPENALEX_EMAIL` / `OPENALEX_API_KEY`、`GOOGLE_API_KEY`（配图，见第 1 节走不通） | `.env.example:7,15-17`、`README.md:199-203` |
| 外部服务 | 模型 API、搜索 API、被抓取的网站（默认 15 并发；默认 User-Agent 是 Edge 119 的字符串，可用环境变量 `USER_AGENT` 覆盖）；tiktoken 首次用要联网下编码表（见 2.6） | `gpt_researcher/config/variables/default.py:21,29`、`gpt_researcher/config/config.py:72-76` |
| 算力 | 纯 CPU：硬依赖里没有 torch 这类 GPU 框架；BM25 是纯 Python 实现（README 报 0.02 秒） | wheel METADATA[^wheel]、`gpt_researcher/context/lexical.py:1-7`、`README.md:235` |
| 时间与花费（作者报的） | 写报告这一步约 45 秒（整次运行的时间 README 没给），每篇约 $0.115 到 $0.192（gpt-5.4，28 题回放）；deep 约 5 分钟、约 $0.4（o3-mini high，旧口径，且见 2.3 节成本漏算） | `README.md:222,232-239` |
| 操作系统 | CI 只跑 ubuntu；weasyprint 是硬依赖但在 Windows 上不装（只在 `backend/` 导出 PDF 时用，Linux 上要 pango 等系统库）；Docker 镜像是 python:3.14 + chromium / firefox（浏览器抓取器用）；macOS 没有专门说明 | `.github/workflows/tests.yml:23,100-105`、`pyproject.toml:164`、`Dockerfile:3-14` |
| 写盘 | 默认路径不留文件，PyMuPDF 的临时文件用完即删；非默认路径（`document_urls`、浏览器抓取器、配图）会写；stdout 有 print，写报告的流式正文关不掉 | 2.1 节 |

## 5. 和平台对照

### 5.1 平台文献阶段现在有什么

| 项 | 现状 | 证据 |
|---|---|---|
| 步骤能力 | 没有。文献、假设、写作三个阶段都没有步骤；研究助理用 `ai4sci output new literature` 开产出目录，手写 `sources.md` | `platform/framework/capabilities/__init__.py:42-52`、`platform/coordinator/README.md:64,120` |
| 主文件 | `sources.md`（页面名「材料来源」），写法不限；复现流程的两个步骤把文献产出目录里的文本文件原样拼进 prompt，`sources.md` 排在最前 | `platform/framework/capabilities/__init__.py:47,55`、`platform/framework/capabilities/reproduction/__init__.py:282-285` |
| 助理该找什么 | 论文本身、官方代码、数据与权重、别人的复现与已知坑、跑起来要什么；每样写链接、commit 或版本、许可证、拿没拿到 | `platform/coordinator/README.md:120-128` |
| 联网 | 两层都只用 CLI 自带的搜索与网页读取（Claude Code 的 WebSearch / WebFetch、Codex 的 `web_search`），查到的带来源 | `docs/architecture/workflow.md:240`、`platform/coordinator/README.md:168` |
| skill | `pdf`：论文 PDF 出 `paper.md`、`images/`、`structured.json`（分节、表格、图注、参考文献、题目作者年份 DOI、arXiv 号）；`download`：git / 文件 / Hugging Face 拉进 `materials/` 并留收据 | `platform/skills/pdf/SKILL.md:3,44`、`platform/skills/download/SKILL.md:3` |
| 流程 | `reproduce` 的文献格挂 `[pdf, download]` 两个 skill | `platform/workflows/reproduce.yaml:4,10` |
| 对缺口的口径 | 流程助理被要求：要文献检索、写综述这类还没有的能力时，直说平台还没有 | `platform/coordinator/studio.md:42` |

### 5.2 多了什么重叠什么

| 能力 | 平台现在 | GPT Researcher | 证据 |
|---|---|---|---|
| 拆检索式 | 助理在对话里自己想 | 一次模型调用出 3 条，deep 模式递归展开 | 2.2、2.3 节 |
| 学术 API 检索 | 没有，只有助理的通用网页搜索 | arXiv、S2、OpenAlex、PMC 四个客户端，均只回标题、链接、摘要 | 2.4 节 |
| 批量抓页面 | 助理 WebFetch 逐页读 | 并行抓约 25 页，过滤反爬页与词表页 | `gpt_researcher/scraper/scraper.py:40-106,194-274` |
| 段落筛选 | 没有，助理读全文 | BM25 / Jev / embeddings | 2.2 节第 7 步 |
| 成文 | 助理手写 `sources.md`：材料清单，含 commit、许可证、拿没拿到 | 一次模型调用写综述式报告，≥1200 词，URL 级内联引用 | `gpt_researcher/prompts.py:262-316` |
| PDF 解析 | `pdf` skill：版面模式，分节、表格、参考文献进 `structured.json` | PyMuPDFLoader 逐页纯文本拼接，截前 5 万字符，无结构 | `gpt_researcher/scraper/pymupdf/pymupdf.py:64-80` |
| 书目元数据 | `pdf` skill 从单篇 PDF 抽题目、作者、年份、DOI | 检索器把作者、年份、DOI 丢掉 | 2.4 节 |
| 找代码、数据、权重 | 助理搜，`download` 拉并留收据 | 没有对应检索器；要靠接 MCP server | 2.4 节 |
| 本地文献库 | 没有 | `DOC_PATH` 本地模式（仍会联网初搜一次） | `gpt_researcher/skills/researcher.py:166-173,365-366` |
| 引用可核 | `sources.md` 要求带链接 | URL 级超链接，不校验；原文留在内存供事后核对 | 2.5 节 |
| 作者自测的增益 | — | 同一宿主 agent、同一模型下，换成它的工具后每篇被核实为支持的引用从 18.6 条到 35.2 条，精确率 53.9% 到 56.0%（10 题） | `deep_agents/BENCHMARK.md:35-38` |

### 5.3 会碰到的现有规则

只列规则原文要点与 GPT Researcher 的对应事实，不下结论。

| 规则 | 规则要点 | GPT Researcher 的事实 | 证据 |
|---|---|---|---|
| P-1 | 代码、分析稿、论文正文只由执行层产出；框架不调模型写文本；总纲第 1 节与四层图把 skill 脚本定为「确定性工具」 | 研究与成文都在它自己的进程里经 LangChain 调模型；若包成 skill 脚本，就是 skill 进程调模型写综述。只用检索器、抓取器、BM25、`quick_search()`，或预设 `agent` / `role` 并给定 `source_urls` 的 `conduct_research()` 时不调模型 | `docs/architecture/README.md:7,28,151`、2.1 节 |
| P-20 | 文献阶段主文件 `sources.md`，进这个阶段的步骤必须留下它；skill 不开产出目录，写哪里由调用者定 | 默认路径不写文件，产出是内存里的报告字符串、URL 列表、来源全文；形状是叙述报告，不是材料清单 | `docs/architecture/README.md:170`、2.1 节 |
| P-22 | agentskills.io 格式；脚本 PEP 723 自带依赖、锁进仓、`uv run --locked --offline` 起；`make skills` 预热是唯一联网的一步；脚本结果一行 JSON 到 stdout，诊断到 stderr | 硬依赖 140 个；缺 provider 包时运行中 `pip install`，uv 建的环境默认不带 pip（这一步在平台里的实际表现未实测）；`ddgs`、`langchain-mcp-adapters`、`langchain-anthropic` 不在 PyPI 硬依赖里；运行时必须联网（检索、抓取、模型 API，tiktoken 首次用还要下编码表），平台现有的 `download` skill 与 `pdf` 的链接输入也在运行时联网；核心包有 89 处 print 到 stdout，写报告的流式正文用 `verbose=False` 也关不掉 | `docs/architecture/README.md:172`、`platform/docs/add-a-skill.md:55,65,71`、2.1、2.6、4 节 |
| P-25 | 两层 agent 用哪家、什么模型、思考深度按人写在 `~/.config/ai4sci/agents.yaml`，走研究者自己的 agent 登录；订阅账号报不出美元时成本填 NaN | 读自己的 `FAST_LLM` / `SMART_LLM` / `STRATEGIC_LLM` 环境变量；只认各家 API 的凭据，不能用 Claude Code / Codex 的登录；成本一律报美元，价格表外的模型按固定单价估、不会出空值，deep 模式漏算 | `docs/architecture/README.md:175`、2.3、2.6 节 |
| P-14 | agent 联网只用 CLI 自带的搜索与网页读取；配置归按人的设置与起服务的环境变量，不挂在命令前 | 自带一条搜索通道（Tavily 等 API 加自己抓页面）；配置全在环境变量或 JSON。平台起 skill 脚本时把整份 `os.environ` 传下去，`download` 读 `HF_TOKEN` 是已有先例 | `docs/architecture/README.md:164`、`platform/framework/skills/run.py:37-42`、`platform/skills/download/SKILL.md:4,31` |
| P-2 | 需要模型判断的评审由隔离的新会话做，只给产物不给轨迹（尚未实现） | 核心包没有评审步骤；`multi_agents/` 的 reviewer 与 fact checker 是同一流水线里的模型调用 | `docs/architecture/README.md:152`、`multi_agents/agents/reviewer.py:15-47`、`multi_agents/agents/fact_checker.py:10-32` |
| 许可证 | — | 硬依赖 PyMuPDF 是 AGPL-3.0 或商业双许可；平台 `pdf` skill 用的 pymupdf4llm 同样是这两种许可[^pymupdf] | `pyproject.toml:128`、`platform/skills/pdf/scripts/extract.py:1-6` |

## 6. 成熟度

| 项 | 实况 | 证据 |
|---|---|---|
| 规模与热度 | 29.6k star、4.1k fork，2023-05-12 建库，默认分支 main；核心包约 1.6 万行 | GitHub API[^ghmeta] |
| 维护节奏 | 近 12 个月 468 个提交、93 位作者，维护者本人 242 个（52%）；按月 9 到 92 个（2025-09 只算 27 日以后），2026-09 最密（92），其次 2026-03（52）、2026-07（51）；近 3 个月合并 62 个 PR | GitHub API[^ghmeta] |
| issue | 开着 5 个、关了 742 个；PR 开着 9 个、合并 618 个。「开着 5 个」要连着这件事看：2026-07-14 一天关了 110 个 issue（其中 94 个在关闭时已开了一年以上），抽看 #510 的关闭评论是「开了一年以上、无近期动静的积压清理，不代表问题无效」，关闭状态记为 completed[^bulkclose]。开着的 5 个里与本题相关的两个：#1764「研究时常卡住且日志看不出在干什么」，#1582 PyMuPDF 的 AGPL 许可问题（见下面许可证一行） | GitHub search API[^ghmeta] |
| 发版 | 两条版本号并行：GitHub tag v3.x（2026 年 11 次，最近 v3.7.0，2026-09-26）与 PyPI 0.x（2026 年 7 次，最近 0.16.1，同日）。0.16.0（2026-07-18）在 3.12 / 3.13 上 import 即报错，修复 08-23 进 main、GitHub 发了 v3.6.1（08-24），PyPI 直到 09-26 才发 0.16.1。仓库 0957c30 的 `pyproject.toml` 版本号仍写 0.16.0 | 发布列表[^releases]、[^wheel0160]、`pyproject.toml:3,25` |
| 测试 | 135 个测试文件、528 个测试函数、约 1.1 万行；从文件名看以各检索器、抓取器「坏输入不崩」的守卫测试为主（`test_*_malformed*`、`test_*_none*` 之类），没有端到端质量测试；新进的 BM25 与 Jev 筛选各有 8、13 个单测；`evals/` 下的评测是手动跑的离线脚本 | `tests/`、`tests/test_lexical_context_filter.py`、`tests/test_jev_context_filter.py`、`evals/README.md` |
| CI | `tests.yml` 从 2026-08-23 起跑：import 矩阵、收集检查、断网单测（`GPTR_BLOCK_NETWORK=1`、`--forked`、排除三个联网文件）；另有 PR 成本评论、插件清单扫描、Docker 构建、部署到维护者自己的 AWS | `.github/workflows/tests.yml:14,125-138`、`.github/workflows/` |
| 已知小缺陷 | `ResearchConductor` 的 `_search`、`_extract_content`、`_summarize_content`、`_update_search_progress` 零调用；`add_costs` 里调异步的 `_log_event` 没有 await；配图开关读错属性名；`MCP_SERVERS` 被覆盖；缺 `langchain-mcp-adapters` 时 `mcp` 被静默换成 Tavily；写报告与拆子查询不用自定义 `PromptFamily`；流式正文的 print 不受 `verbose` 控制；deep 成本漏算；gptr-mcp 的 `content_length` 恒 0 | `gpt_researcher/agent.py:801-806`、第 1、2 节 |
| 安全 | 后端无鉴权是设计选择；MCP 配置能起任意命令（#1694 按威胁模型不修）；抓取前有 SSRF 校验；PDF 下载 SSL 失败降级 `verify=False` | `SECURITY.md:20-41`、`gpt_researcher/scraper/scraper.py:200-211`、`gpt_researcher/scraper/pymupdf/pymupdf.py:48-53` |
| 许可证 | `LICENSE` 是 Apache-2.0（GitHub 也识别为 Apache-2.0），README 写 Apache 2；wheel 里附带的也是这份 Apache-2.0 全文；但 `pyproject.toml`、`setup.py` 与 PyPI 元数据写 MIT，维护者账号在 #1582 的回复里也说「this project is MIT」[^i1582]；没有 NOTICE 文件。Apache-2.0 要点：可商用、修改、再分发；分发时附许可证全文、标明改动、保留 NOTICE；含专利授权，对使用者提起专利诉讼则授权终止；不授商标权。gptr-mcp 是 MIT | `LICENSE:1-2`、`README.md:354`、`pyproject.toml:6,28`、`setup.py:33,35`、wheel[^wheel] |
| 作者自己的免责声明 | 「实验性软件，按现状提供……不建议用于学术或研究论文」 | `README.md:352-354` |
| 依赖的许可证与商业服务 | PyMuPDF AGPL-3.0 或商业双许可[^pymupdf]，是硬依赖、抓 PDF 与读本地 PDF 都用它。#1582 里有人给出 MIT 的 pdfminer.six 替代实现，维护者账号下的回复确认「许可问题真实存在、未解决，对把 GPT Researcher 当托管服务跑的人有影响，要维护者决定」，issue 仍开着[^i1582]。Tavily、TypeSafe 是商业 API | `pyproject.toml:128`、`gpt_researcher/scraper/pymupdf/pymupdf.py:5`、`gpt_researcher/document/document.py:73` |

## 7. 还没弄清的问题

1. 科研题目上的实际内容质量：按代码，arXiv 只进摘要、S2 无 key 易被限流、OpenAlex 付费墙论文只剩落地页。一个 PINN 或参数估计类题目跑下来，上下文里多少是论文正文、多少是博客与新闻，要 #172 实测。
2. 学术题上的引用精确率。作者的 56% 来自 DeepResearch Bench 10 道通用英文题、gpt-5.4、deepagents 宿主，换成学术题与 Claude 系模型是多少不知道。
3. Claude 系模型走标准与 deep 两条路径时的 JSON 解析成功率与成本（#1772 修过，没实测）。
4. 放进 `uv run --locked --offline` 的脚本环境后，`_check_pkg` 的 `pip install` 是报错、静默失败还是被 offline 拦住；PEP 723 下 140 个硬依赖的锁与环境体积多大。
5. `npx skills add assafelovic/gpt-researcher` 装的是哪一份、`uvx gpt-researcher` 是否确实起不来，都只是读 CLI 源码与 wheel 推断，没跑。
6. deep 模式成本漏算的实际数额，以及 README「约 5 分钟、约 $0.4」在 gpt-5.4 或 Claude 下是多少。
7. 中文查询：BM25 不切中文会不会让段落筛选退化成取第一页开头；有没有可接的中文学术源（现有的 bocha 是通用网页搜索）。
8. 本地模式能否完全离线：代码显示仍用第一个检索器联网初搜，把检索器设成不可用时拆子查询会怎样。
9. 每页截前 5 万字符对长论文（正文加附录）的影响。
10. Semantic Scholar：官方 API 规范里 `/paper/search` 没有 `sort` 参数，代码照传；API 是忽略还是报错，本机请求全被 429 挡住，没测到。
11. 默认值与维护者商业利益的关系：维护者是 Tavily 联合创始人（二手来源[^crunchbase]；README 的 PIP 文档链接指向 docs.tavily.com），有二手来源称 Tavily 2026-02 被 Nebius 收购[^tavilywiki]，API 条款是否变过没查；与 TypeSafe 的关系没查到，而把 Jev 设为默认的依据是作者自己的评测（`evals/context_filter/`）。
12. PyMuPDF 的 AGPL 对平台分发的影响。上游 #1582 还没定；平台 `pdf` skill 已依赖同许可的 pymupdf4llm，这不是 GPT Researcher 新带来的问题，但结论要另行确认。另外 `LICENSE`（Apache-2.0，wheel 里附带的也是它）与包元数据、维护者说法（MIT）哪个算数，上游没有说明。
13. 仓库里没有一个真正「让宿主 agent 执行研究」的 skill，作者是否有这个计划，issue 里没找到。
14. gptr-mcp 在 stdio 模式下，核心包往 stdout 的 print（含写报告的流式正文）会不会打乱协议消息；gptr-mcp #2「parsing errors」是否就是这个，issue 里只有截图，没查清。
15. 默认的 BM25 段落筛选与 Jev 都是 2026-09-26 才进代码，此前的默认是 embeddings；换了筛选之后，作者在 `deep_agents/BENCHMARK.md` 报的引用数字（该文件最后改于 2026-07-05，用的是当时的 embeddings 筛选）是否还成立，不知道。
16. 缺 `langchain-mcp-adapters` 时 `mcp` 被换成 Tavily：没有 `TAVILY_API_KEY` 时这个替身会报错还是返回空、会不会让整次研究失败，没实测。

## 8. 调研方法

- 浅克隆到外层 `vendor/gpt-researcher`（gitignore 挡住），提交 0957c30。核心包逐文件读完主路径（`agent.py`、`skills/`、`actions/`、`context/`、`retrievers/` 四个学术源、`scraper/`、`llm_provider/`、`config/`、`mcp/`），`backend/`、`multi_agents/`、`deep_agents/` 只读与本题相关的部分。
- 没装依赖、没跑项目代码。另外做了四件只读的事：下载 PyPI 0.16.0 与 0.16.1 的 wheel 看元数据与文件（0.16.1 的 `gpt_researcher/` 与 0957c30 `diff -rq` 无差异）；用 `gh api` 读 gptr-mcp、vercel-labs/skills 的源码与 issue、release、提交统计；用 curl 直接请求 arXiv、Semantic Scholar、OpenAlex 的公开 API 看返回格式；两次网页搜索确认维护者背景与 Jev 的发布时间。
- 所有「零调用」「恒为 False」「推算 33 次」都来自读代码与 grep，标了「推断」「未实测」的留给 #172 实测验证。
- 第一版写完后另做了一轮独立复查：逐条打开文中的 `文件:行` 核对；重新下载 0.16.0 / 0.16.1 wheel 核对元数据；用 `gh api` 重数提交、issue、release，读 gptr-mcp 的 issue 与 PR、关键文件的提交历史；下载 Semantic Scholar 官方 API 规范（`/graph/v1/swagger.json`）核对 `sort` 参数。改动集中在：MCP 缺包时的回落、`get_research_sources()` 的内容、stdout 与写盘、成本口径、BM25 中文回落、筛选代码的上线日期、issue 批量关闭、发版次数与月度提交数。

[^wheel]: PyPI gpt-researcher 0.16.1 的 wheel（2026-09-26 上传，poetry-core 2.5.0 构建）：`dist-info` 里没有 `entry_points.txt`；`Requires-Dist` 166 条，其中不带 extra 的 140 条，与仓库 `pyproject.toml` 的 `dependencies` 逐条一致，没有 torch 等 GPU 框架；`License: MIT`，而 `dist-info/licenses/LICENSE` 是 Apache-2.0 全文；包内只有 `gpt_researcher/`。<https://pypi.org/project/gpt-researcher/0.16.1/>
[^wheel0160]: PyPI gpt-researcher 0.16.0 的 wheel（2026-07-18 上传）中 `gpt_researcher/actions/query_processing.py`：第 6 行的函数签名已用到 `Any`、`List`，`from typing import Any, List, Dict` 却在第 37 行，文件也没有 `from __future__ import annotations`。<https://pypi.org/project/gpt-researcher/0.16.0/>
[^arxivapi]: 2026-09-27 请求 `https://export.arxiv.org/api/query?search_query=all:electron&max_results=1`，返回条目里 `title="pdf"` 的链接是 `https://arxiv.org/pdf/cond-mat/0011267v1`，没有 `.pdf` 后缀。
[^s2]: 2026-09-27 从本机不带 key 请求 `https://api.semanticscholar.org/graph/v1/paper/search` 三次（不带 sort、`sort=citationCount`、`sort=relevance` 各一次），都返回 429「Too Many Requests … apply for a key」。
[^openalex]: 2026-09-27 请求 `https://api.openalex.org/works?search=physics informed neural network&per_page=5&sort=relevance_score:desc`：5 条里 3 条 `best_oa_location` 没有 `pdf_url`，落地页是 doi.org 链接（如 10.1016/j.jcp.2018.10.045）。
[^skillssh]: skills.sh 条目页 <https://skills.sh/assafelovic/gpt-researcher/gpt-researcher>，2026-09-27 查：安装命令 `npx skills add https://github.com/assafelovic/gpt-researcher --skill gpt-researcher`，展示的 SKILL.md 标题是「GPT Researcher Development Skill」，安装数 1.9K。
[^skillsts]: vercel-labs/skills 提交 f00c1a1（2026-09-08）的 `src/skills.ts`，函数 `discoverSkills()`：先对仓库根做深度 1 的子目录扫描，再扫 `skills/` 等容器目录，按 `name` 去重。<https://github.com/vercel-labs/skills/blob/f00c1a1/src/skills.ts>
[^plugincommit]: gpt-researcher 提交 ec126e0（2026-04-05，作者 internet-dot），一次加入 `.codex-plugin/plugin.json`、`.mcp.json`、`skills/gpt-researcher/SKILL.md` 与 `plugin-quality-gate.yml`。<https://github.com/assafelovic/gpt-researcher/commit/ec126e0>
[^gptrmcp]: assafelovic/gptr-mcp 提交 6388477（2025-11-07，也是最后一次提交）的 `server.py`、`utils.py`、`requirements.txt`、`.env.example`；仓库 MIT，371 star，2026-09-27 查。<https://github.com/assafelovic/gptr-mcp>
[^gptrmcpissues]: gptr-mcp 2026-09-27 仍开着的：#25「只认 OPENAI_API_KEY，配了别家模型也起不来」（2026-04-26）、#30「`content_length` 恒为 0」等三项修复（2026-07-18）、#31「`deep_research` 只构造 `GPTResearcher(query)`，deep 模式经 MCP 用不到」（2026-09-05）、#33「`run_server()` 的 `while True: pass` 空转占满 CPU」（2026-09-15）、#2「parsing errors」（2025-04-06，只有截图）。<https://github.com/assafelovic/gptr-mcp/issues>
[^ghmeta]: GitHub API，2026-09-27 查：仓库元数据；search API 的 issue / PR 计数；`commits?since=2025-09-27` 全量翻页按月、按作者统计。<https://github.com/assafelovic/gpt-researcher>
[^releases]: GitHub releases 列表与 v3.7.0 发布说明 <https://github.com/assafelovic/gpt-researcher/releases/tag/v3.7.0>；PyPI 各版本上传时间来自 <https://pypi.org/pypi/gpt-researcher/json>。
[^i1572]: Report Generator Halluzinates Sources，2025-12-08 报，2026-08-23 关。<https://github.com/assafelovic/gpt-researcher/issues/1572>
[^i1846]: Snippet retrievers (searx): search snippets >100 chars are treated as prefetched full content，2026-07-02 报；同类 #1892。<https://github.com/assafelovic/gpt-researcher/issues/1846> <https://github.com/assafelovic/gpt-researcher/issues/1892>
[^i1893]: ContextCompressor fast path loses source URLs → reports cite "https://example.com"，2026-07-13 报。<https://github.com/assafelovic/gpt-researcher/issues/1893>
[^i1894]: Arxiv scraper broken with arxiv>=2.2，2026-07-13 报。<https://github.com/assafelovic/gpt-researcher/issues/1894>
[^i1945]: No CI workflow actually runs the test suite，2026-07-18 报，08-23 关；同日的 PR #1943「fix: NameError on import in query_processing.py (package currently unusable as published)」，08-23 关。<https://github.com/assafelovic/gpt-researcher/issues/1945> <https://github.com/assafelovic/gpt-researcher/pull/1943>
[^i1772]: Deep Research: "Generated 0 queries: []" with Claude Haiku 4.5，2026-05-15 报。<https://github.com/assafelovic/gpt-researcher/issues/1772>
[^i1694]: Unauthenticated Remote Code Execution via MCP Command Injection，2026-03-23 报，维护者按威胁模型关闭。<https://github.com/assafelovic/gpt-researcher/issues/1694>
[^i2100]: Prefetched sources never enter visited_urls, so they drop out of References，2026-09-02 报。<https://github.com/assafelovic/gpt-researcher/issues/2100>
[^i2110]: Deep research zero-query path raises NameError before fallback state is initialized，2026-09-08 报。<https://github.com/assafelovic/gpt-researcher/issues/2110>
[^i1579]: DEEP mode does not stop when retrievers can not obtain context，2025-12-16 报。<https://github.com/assafelovic/gpt-researcher/issues/1579>
[^i1676]: Env pollution，2026-03-14 报。<https://github.com/assafelovic/gpt-researcher/issues/1676>
[^i1875]: Two Tavily paths run simultaneously，2026-07-10 报。<https://github.com/assafelovic/gpt-researcher/issues/1875>
[^i1582]: GPL License Alternative PDF Scraper Implementation，2026-01-05 报，2026-09-27 仍开着；引用了更早的 #1571。<https://github.com/assafelovic/gpt-researcher/issues/1582>
[^i1986]: Anthropic prompt-cache tokens are silently priced at $0，2026-07-24 报。<https://github.com/assafelovic/gpt-researcher/issues/1986>
[^crunchbase]: Crunchbase「Assaf Elovic - Co-Founder @ Tavily」，二手来源，未与本人声明核对。<https://www.crunchbase.com/person/assaf-elovic>
[^tavilywiki]: AI Wiki「Tavily」条目，称 2026-02 Nebius 宣布收购 Tavily，二手来源，未核实。<https://aiwiki.ai/wiki/tavily>
[^jev]: TypeSafe 博客「Introducing System One Models & Jev」<https://typesafe.ai/blog/introducing-system-one-models-and-jev>；MarkTechPost 2026-09-19 的报道称 2026-09-15 开放早期访问（二手）<https://www.marktechpost.com/2026/09/19/typesafe-ai-releases-jev/>。
[^pymupdf]: PyPI 上 pymupdf 1.28.2 与 pymupdf4llm 1.28.2 的 license 字段均为「Dual Licensed - GNU AFFERO GPL 3.0 or Artifex Commercial License」，2026-09-27 查。
[^jevcommit]: `gpt_researcher/context/jev_filter.py` 与 `select.py` 的提交历史只有两条，都是 2026-09-26、维护者本人：a0a7449「feat(context): filter scraped content with Jev; embeddings become optional」与 2906e63「feat(context): keyword fallback so no filter needs a key or embeddings」。GitHub API `commits?path=…`，2026-09-27 查。
[^s2spec]: Semantic Scholar Graph API 官方规范 <https://api.semanticscholar.org/graph/v1/swagger.json>（2026-09-27 下载）：`/paper/search` 的参数是 query、fields、publicationTypes、openAccessPdf、minCitationCount、publicationDateOrYear、year、venue、fieldsOfStudy、offset、limit，没有 sort；`/paper/search/bulk` 有 sort，格式 `field:order`，可排 paperId、publicationDate、citationCount。
[^bulkclose]: GitHub search API `is:issue closed:2026-07-14` 共 110 条，state_reason 全是 completed；#510 的关闭评论（维护者，2026-07-14）：「Closing as part of a long-tail backlog cleanup — this issue has been open for over a year with no recent activity. This is not a judgment on its validity」。<https://github.com/assafelovic/gpt-researcher/issues/510>
