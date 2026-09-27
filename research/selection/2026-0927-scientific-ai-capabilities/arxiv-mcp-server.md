---
title: arxiv-mcp-server 代码级深读
subtitle: 文献阶段候选 · 19 个 MCP 工具、零模型调用；按节读 LaTeX、BibTeX、主题订阅逐条对账
kind: 开源项目选型深读（只读代码，不跑、不装依赖）
date: 2026-09-27
scope: 仓库 https://github.com/blazickjp/arxiv-mcp-server，浅克隆到 vendor/arxiv-mcp-server，提交 42419c1（2026-08-26，v0.7.2 之后两天）；读了 src/ 全部 8016 行、tests/ 与 .github/ 的结构、CLAUDE.md、SKILL.md 与各份打包清单；issue、release、提交节奏、CI 结果用 gh api 查（2026-09-27）；文中 文件:行 均相对该仓库根；平台一侧的路径相对外层仓根，内仓 platform/ 在提交 de3d948；复查时另只读了 pymupdf4llm 0.2.9、pymupdf-layout 1.27.1 的 wheel 与 MCP Python SDK v1.27.0、PyMuPDF 1.27.1 的相关源码
status: 第一版
---

> **结论先行**：它是一个只管 arXiv 的本地 MCP 服务：19 个工具、7 个 MCP prompt，全仓零模型调用（`src/` 里 grep 不到任何模型 API），所有能力都是确定性代码——arXiv Atom API 检索、HTML 优先 PDF 兜底的全文抽取、e-print 源码包的安全解包与按节切分、从 arXiv 元数据拼 BibTeX、Semantic Scholar 引用图、存在一个 JSON 文件里的主题订阅。README 的主张在代码里大体有对应。**厚**的是三块：源码包的防御性解包（每条上限都在流式读取时卡）、所有正文输出默认有界（12,000 字符一页、带续读游标）、arXiv 限流与版本号边界。**薄或与说法不符**的有八处：HTML 路径产的是按行拼的纯文本而不是 markdown；LaTeX 分节只认 `\section` 三级，LaTeX 工具失败时不会自动退回 PDF；「主题订阅」是存下来的查询加游标，代码里没有任何定时或推送；BibTeX 一律 `@misc`，不带 arXiv 元数据里现成的 DOI 与期刊信息；语义检索只嵌摘要、按带版本号的 ID 存，建索引在事件循环上同步联网（违反仓库自己 `CLAUDE.md` 的规矩）；搜索与语义检索结果里的 `arxiv://` 资源 URI 服务端没有注册；限流软返回只做了三个工具，其余联网工具（`get_abstract`、`export_citations`、`download_paper`、三个 LaTeX 工具）遇到限流仍报错；两个配置项（`BATCH_SIZE`、低于 120 的 `REQUEST_TIMEOUT`）不起作用。
>
> 和平台对照：文献阶段平台现在只有助理手写 `sources.md` 加 `pdf`、`download` 两个 skill。它多出来的是 LaTeX 分节读、BibTeX、引用图、订阅、本地论文缓存五样；重叠的是检索（助理自带的网页搜索）与 PDF 转文本（同一个库 pymupdf4llm，但版本与模式不同：本仓锁 0.2.9，按代码看不会进版面模式；`pdf` skill 锁 1.28.2、走版面模式）。它现在只有 MCP 服务一种形态，没有命令行（`arxiv-mcp-server` 只会起服务等 stdin），自带的 SKILL.md 是 26 行「怎么调这些 MCP 工具」的说明。平台两家适配器目前都把 MCP 清空了，P-14 只放行 `ai4sci`，P-22 要求 PEP 723 脚本，P-15 / P-20 要求产物落在工作区里：这些是接进来会碰到的现有规则，本文只列事实，不下接不接的结论（[第 5 节](#5-和平台对照)）。
>
> 成熟度：389 个测试函数、三个操作系统乘三个 Python 版本的 CI 矩阵、发版前跑测试加 wheel 冒烟并同步发到 PyPI 与官方 MCP Registry；但所有网络行为只在 mock 里测，CI 不装 `[pdf]` `[pro]` 两个 extra（只检查它们能从二进制 wheel 解析）。单人维护（217 个提交里 193 个出自作者），2026-03 曾有用户开 issue 说「没人维护」，4 月恢复，2026-08-21 到 23 日（UTC）作者一人开了 51 条 issue、62 个 PR 集中修，最后一次提交 2026-08-26，之后的外部 PR 在等批。`[pdf]` 锁定的 pymupdf-layout 1.27.1 在 PyPI 上标的是「PolyForm Noncommercial 或 Artifex 商业许可」，不是 AGPL（见[第 4 节](#4-跑起来要什么)）。横向对比见同目录的 [README.md](README.md)。

## 1. 是不是：README 的主张在代码里对应哪段

### 1.1 暴露了什么

`server.py` 注册 19 个工具，一条 `if/elif` 链分发（`src/arxiv_mcp_server/server.py:85-108,127-177`）；README 说 19 个（`README.md:182`），但仓库自己的 `CLAUDE.md` 还写「registers 16 tools」、漏了三个大纲工具（`CLAUDE.md:53-60`），是没跟上的文档。成功结果是一段 JSON 文本，部分错误路径返回以 `Error:` 开头的纯文本（如 `src/arxiv_mcp_server/tools/alerts.py:311`、`src/arxiv_mcp_server/tools/citation_graph.py:397-401`）；顶层 `status == "error"` 的 JSON 或以 `Error:` 开头的文本被 `call_tool` 改抛 `RuntimeError`（`src/arxiv_mcp_server/server.py:111-124,175-176`），MCP SDK 再把异常包成 `isError=true` 的结果[^mcpsdk]。限流只有三个工具软返回 `status: rate_limited`、不算错误：`search_papers`、`check_alerts`、`citation_graph`（`src/arxiv_mcp_server/tools/search.py:784-790`、`src/arxiv_mcp_server/tools/alerts.py:419-426`、`src/arxiv_mcp_server/tools/citation_graph.py:478-491`）；`get_abstract`、`export_citations`、`download_paper` 遇到限流仍报 `status: error`（`src/arxiv_mcp_server/tools/get_abstract.py:142-148`、`src/arxiv_mcp_server/tools/export_citations.py:326-327`、`src/arxiv_mcp_server/tools/download.py:1160-1175`）；三个 LaTeX 工具下载 e-print 不做退避，429 直接报 `HTTP 429`（`src/arxiv_mcp_server/tools/latex_archive.py:55-56`、`src/arxiv_mcp_server/tools/latex.py:366-373`）。

| 组 | 工具 | 主要参数 | 返回 | 证据 |
|---|---|---|---|---|
| 检索 | `search_papers` | `query`（必填）、`max_results`（缺省 5，服务端上限 50）、`start`、`abstract_mode`（none / snippet / full，缺省 snippet 截 280 字）、`date_from` / `date_to`、`categories`、`sort_by`（relevance / date） | `papers[]`（id、versioned_id、title、authors、abstract、categories、published、url、resource_uri）、`total_results`、`returned`、`has_more`、`next_start`、`content_warning` | `src/arxiv_mcp_server/tools/search.py:589-663,459-496,568-580` |
| 检索 | `get_abstract` | `paper_id` | title、authors、abstract、categories、published、pdf_url | `src/arxiv_mcp_server/tools/get_abstract.py:18-38,122-140` |
| 全文 | `download_paper` | `paper_id`、`start`、`max_chars`、`return_full_text`、`force` | `source`（cache / html / pdf）、`arxiv_version`、分页正文（`content`、`content_length`、`next_start`、`is_truncated`） | `src/arxiv_mcp_server/tools/download.py:688-744,934-1131` |
| 全文 | `list_papers` | `compact` | 本地 sidecar 里的 id、title、authors、published、版本；不联网 | `src/arxiv_mcp_server/tools/list_papers.py:28-53,315-346` |
| 全文 | `read_paper` | `paper_id`、`start`、`max_chars`、`return_full_text` | 本地缓存正文，分页 | `src/arxiv_mcp_server/tools/read_paper.py:25-71,97-154` |
| 全文大纲 | `get_paper_outline` / `read_paper_section` / `search_paper_text` | `paper_id`；分节用 `section_id`（大纲 ID 或唯一标题）；检索用 `query`（子串，≤ 200 字）、`max_passages`（≤ 25）、`passage_chars`（≤ 2000） | 标题层级与字符偏移；一节正文；带偏移与所在节的片段 | `src/arxiv_mcp_server/tools/paper_outline.py:738-822,825-953` |
| LaTeX | `get_paper_latex` | `paper_id`、`start`、`max_chars`（显式给时 ≤ 50,000）、`return_full_text`（为真时不设上限） | 主文件名、源文件数、展平后的 LaTeX 分页 | `src/arxiv_mcp_server/tools/latex.py:146-157,273-286,345-378`、`src/arxiv_mcp_server/tools/content.py:59-62` |
| LaTeX | `list_paper_latex_sections` | `paper_id`、`start`、`max_sections`（≤ 200） | `sections[]`（id、level、title）分页 | `src/arxiv_mcp_server/tools/latex.py:288-311,381-429` |
| LaTeX | `get_paper_latex_section` | `paper_id`、`section_id`（ID 或标题） | 一节的 LaTeX 原文，分页 | `src/arxiv_mcp_server/tools/latex.py:313-331,432-479` |
| 引用 | `citation_graph` | `paper_id`、`max_citations`（缺省 50，≤ 200） | 本文元数据、`citations[]`、`references[]`（各带 `arxiv_id`）、总数 | `src/arxiv_mcp_server/tools/citation_graph.py:59-91,377-476` |
| 引用 | `export_citations` | `paper_ids`（1 到 50 个） | 拼好的 `bibtex`、逐条 `results[]`、计数；整体 success / partial / error | `src/arxiv_mcp_server/tools/export_citations.py:189-216,219-330` |
| 订阅 | `watch_topic` / `list_watches` / `check_alerts` / `unwatch_topic` | `topic`（arXiv 查询串）、`categories`、`max_results`（缺省 10） | 订阅记录；`check_alerts` 返回每个主题的新论文与 `has_more` | `src/arxiv_mcp_server/tools/alerts.py:28-152,248-496` |
| 语义（`[pro]`） | `semantic_search` / `reindex` | `query` 或 `paper_id`、`max_results`；`clear_existing` | 按余弦相似度排的本地论文 | `src/arxiv_mcp_server/tools/semantic_search.py:46-98,341-453` |

另有 7 个 MCP prompt（research-discovery、deep-paper-analysis、summarize_paper、compare_papers、literature_review、literature-synthesis、research-question），`get_prompt` 只把参数拼进一段固定文字返回，不调模型、不存状态（`src/arxiv_mcp_server/prompts/prompts.py:9-117`、`src/arxiv_mcp_server/prompts/handlers.py:55-127`）。

### 1.2 README 与代码逐条对账

| README 的说法 | 代码里 | 判断 | 证据 |
|---|---|---|---|
| 「original-LaTeX section reads」是主要卖点（`README.md:19`） | 下载 e-print、流式解包、展平 `\input` 系列、按 `\section` / `\subsection` / `\subsubsection` 切分，全链路有上限与测试 | 有，且厚；但只认三级标题，`\chapter`、`\paragraph`、附录编号、摘要环境都不认（详见 [2.5](#25-按节读-latex-原文)） | `src/arxiv_mcp_server/tools/latex_flatten.py:26,373-408` |
| `get_paper_latex_section`「macros expanded」（`src/arxiv_mcp_server/tools/latex.py:316`） | 返回的正文是展平后源文的切片，其中只展开了定义体里含 include / section 命令的宏（展平需要）；记号、公式缩写这类一般的宏原样保留；另外在列大纲与按标题匹配时展开标题里的简单宏（优先零参数的） | 半对：一般的宏不展开 | `src/arxiv_mcp_server/tools/latex.py:453`、`src/arxiv_mcp_server/tools/latex_flatten.py:137-149,195-216` |
| 「LaTeX archives are validated, size-limited, and cached locally」（`README.md:363`） | 缓存的是展平后的 `.tex` 文本（一个 JSON），原始压缩包不落盘 | 说法不准 | `src/arxiv_mcp_server/tools/latex.py:160-164,203-239`、`src/arxiv_mcp_server/tools/latex_archive.py:122-123` |
| `download_paper`「convert a paper to local Markdown」（`README.md:188`） | HTML 路径用标准库 `HTMLParser` 抽文本块、按 `\n` 拼接，不产生 `#` 标题；只有 PDF 路径是 pymupdf4llm 出的真 markdown | HTML 路径名不副实；大纲工具为此另写了一套标题启发式（编号行、罗马数字、34 个常见节名） | `src/arxiv_mcp_server/tools/download.py:449-464`、`src/arxiv_mcp_server/tools/paper_outline.py:1-8,44-139` |
| BibTeX「from authoritative arXiv metadata」（`README.md:198`） | 一次 Atom 请求取元数据，渲染 `@misc`，字段只有 title、author、year、eprint、archivePrefix、primaryClass、url | 有；但 Atom 里现成的 `<arxiv:doi>`、`<arxiv:journal_ref>` 没解析[^manual]，已正式发表的论文也只出 `@misc` | `src/arxiv_mcp_server/tools/export_citations.py:125-146`、`src/arxiv_mcp_server/tools/search.py:499-586` |
| 「topic watches」、「standing alert」（`README.md:19`、`src/arxiv_mcp_server/tools/alerts.py:34-36`） | 订阅是 `watched_topics.json` 里的一条记录；只有客户端调 `check_alerts` 才去查；`src/` 里没有定时器、后台循环或推送 | 有，但是拉取式的 | `src/arxiv_mcp_server/tools/alerts.py:155-175,314-418` |
| `semantic_search`「Search downloaded papers by semantic similarity」（`README.md:203`） | 嵌的是从 arXiv API 取回的**摘要**，不是下载下来的全文；索引键取自 `get_short_id()`，即带版本号的 ID | 半对（见 [2.8](#28-引用图与语义检索)） | `src/arxiv_mcp_server/tools/semantic_search.py:183,237-262` |
| 搜索与语义检索结果带 `resource_uri: arxiv://<id>` | 服务端没有注册 `list_resources` / `read_resource`；`resources/papers.py` 的 `PaperManager` 全仓（含测试）无调用，`CLAUDE.md` 自称「legacy … retained for compatibility」。初始化时传了 `NotificationOptions(resources_changed=True)`，但 MCP SDK 只在注册了 `list_resources` 处理函数时才声明 resources 能力[^mcpsdk]，所以这个开关不起作用，客户端看到的能力里没有 resources | URI 指向不存在的资源 | `src/arxiv_mcp_server/tools/search.py:578`、`src/arxiv_mcp_server/tools/semantic_search.py:444`、`src/arxiv_mcp_server/resources/papers.py:18-112`、`src/arxiv_mcp_server/server.py:85-108,183-192`、`CLAUDE.md:46` |
| `REQUEST_TIMEOUT` 缺省 60，「PDF fallback download timeout」（`README.md:461`） | 读超时取 `max(120.0, request_timeout)`，低于 120 的值不起作用 | 配置项部分失效 | `src/arxiv_mcp_server/arxiv_api.py:89-94`、`src/arxiv_mcp_server/tools/download.py:795` |
| `Settings.BATCH_SIZE = 20`（README 与 `CLAUDE.md` 的配置表都没列它） | 全仓无读取点 | 死配置 | `src/arxiv_mcp_server/config.py:97`、`README.md:457-467` |
| `CLAUDE.md`：「Use the shared arXiv request gate rather than creating an independent request path」（`CLAUDE.md:69`） | HTML 正文（`arxiv.org/html/`）与 PDF 流式下载都绕过限流闸；HTML 请求也不带本仓统一的 User-Agent | 自己定的规矩没全守 | `src/arxiv_mcp_server/tools/download.py:752-770,790-800,823-830` |
| 依赖清单 | `aiohttp`、`sse-starlette`、`python-dotenv`、`anyio` 声明了但 `src/` 里没有直接 import；`aiofiles` 只被未接线的 `PaperManager` 用；`requests` 被 `config.py` 直接 import 却没声明（靠 `arxiv` 4.0.0 传递进来，`uv.lock` 里 arxiv 的依赖是 lxml 与 requests） | 依赖清单与代码不一致 | `pyproject.toml:30-44`、`src/arxiv_mcp_server/config.py:9`、`src/arxiv_mcp_server/resources/papers.py:7` |
| `get_abstract` 报「not found」 | 任何上游 HTTP 错误都报成 `Paper <id> not found on arXiv` | 错报；外部用户 2026-09-20 开了 #278，到 2026-09-27 未修[^i278] | `src/arxiv_mcp_server/tools/get_abstract.py:149-161` |

另外两处小毛病：`_optimize_query` 名为「优化」，实际原样返回、只打日志（`src/arxiv_mcp_server/tools/search.py:679-703`）；Atom 解析取短 ID 用 `paper_id.split("v")[0]`，旧式 ID 里带字母 v 的学科（`solv-int/…`）会被切坏（`src/arxiv_mcp_server/tools/search.py:513-515`，读代码推断，未跑）。

## 2. 怎么做：主流程

### 2.1 入口与分发

```
uvx arxiv-mcp-server [--storage-path DIR]
  └─ arxiv_mcp_server:main → asyncio.run(server.main())        pyproject.toml:77-78、src/arxiv_mcp_server/__init__.py:9-11
       ├─ TRANSPORT=stdio（缺省）：stdio_server → server.run      src/arxiv_mcp_server/server.py:231-234
       └─ TRANSPORT=http：Starlette 挂 /mcp 与 /healthz，uvicorn    src/arxiv_mcp_server/server.py:237-272
  tools/call → call_tool 的 if/elif 链 → tools/<x>.py 的 handle_<x>(arguments: dict)
             → 返回 [TextContent(JSON)]；status=error 改抛 RuntimeError      src/arxiv_mcp_server/server.py:127-180
```

`--storage-path` 不走 argparse，而是每次访问 `Settings.STORAGE_PATH` 时从 `sys.argv` 里找（`src/arxiv_mcp_server/config.py:107-156`）；每个工具模块在 import 时各建一个 `Settings()`（例如 `src/arxiv_mcp_server/tools/search.py:20`）。HTTP 模式缺省绑 `127.0.0.1`，开了 DNS rebinding 防护（`src/arxiv_mcp_server/server.py:200-228`）。

### 2.2 外部接口与限流闸

全进程一个 `ArxivRateLimiter`（`threading.Lock` + 两次请求间至少 3 秒），同步与异步调用者共用；异步一侧每 10 毫秒轮询一次锁（`src/arxiv_mcp_server/arxiv_api.py:16-62`）。这对应 arXiv API 使用条款的「每三秒至多一次、单连接」[^tou]。闸是进程内单例，几个进程各起一个服务就各有一把闸（读代码推断）。

| 外部端点 | 谁用 | 过不过闸 | 证据 |
|---|---|---|---|
| `https://export.arxiv.org/api/query`（Atom，httpx 直接拼 URL） | `search_papers`、`get_abstract`、`export_citations`、`check_alerts`、下载前的存在性检查 | 过；只对 429 / 503 指数退避，最多重试 5 次，超时另重试 1 次，**退避与重试的 sleep 都在闸里**，期间别的 arXiv 请求全排队；其他状态码直接抛（外部用户 2026-09-19 开的 #277 报的就是 406 被当成硬错误，未修） | `src/arxiv_mcp_server/tools/search.py:117-174,177-179`、`src/arxiv_mcp_server/tools/download.py:777-787`[^repo] |
| 同一 API，经 `arxiv` 包的 `arxiv.Client` | 下载后补元数据、PDF 路径取元数据、语义索引取摘要 | 过；进程里第一次用到 client 时给包里的 `requests.Session` 注入 (5, 30) 秒超时并关掉 keep-alive，防止一次挂死的连接永久卡住闸 | `src/arxiv_mcp_server/config.py:32-76`、`src/arxiv_mcp_server/tools/download.py:878-888`、`src/arxiv_mcp_server/tools/semantic_search.py:220-234` |
| `https://arxiv.org/html/<id>` | `download_paper` 首选 | 不过；也不带本仓的 User-Agent（`httpx.get` 缺省头） | `src/arxiv_mcp_server/tools/download.py:752-770` |
| `https://arxiv.org/pdf/<id>.pdf` | `download_paper` 兜底 | 不过（只有取元数据那一步过） | `src/arxiv_mcp_server/arxiv_api.py:71-117`、`src/arxiv_mcp_server/tools/download.py:821-830` |
| `https://arxiv.org/e-print/<id>` | 三个 LaTeX 工具 | 过，**整个下载（读超时 120 秒、上限 50 MB）都持有闸** | `src/arxiv_mcp_server/tools/latex_archive.py:40-77` |
| `https://api.semanticscholar.org/graph/v1/paper/ARXIV:<id>` | `citation_graph` | 另一套：429 退避重试 5 次，可带 `x-api-key` | `src/arxiv_mcp_server/tools/citation_graph.py:122-133,308-322` |
| Hugging Face（`sentence-transformers/all-MiniLM-L6-v2`） | `[pro]` 首次加载模型 | 与 arXiv 无关；下载由 sentence-transformers 库按缺省行为完成，本仓没设缓存目录 | `src/arxiv_mcp_server/tools/semantic_search.py:27,154-160` |

### 2.3 搜索

`search_papers` 不用 `arxiv` 包，自己拼 URL 走 raw httpx，原因写在注释里：包会把日期区间里的 `+` 编成 `%2B`，`submittedDate:[… TO …]` 就坏了；同时要拿 OpenSearch 的 `totalResults`（`src/arxiv_mcp_server/tools/search.py:333-370,706-713`）。查询串的改写只有一处：用户没写任何字段前缀时，整串改成 `(ti:(q) OR abs:(q))`，不让裸词匹配到作者名（`src/arxiv_mcp_server/tools/search.py:231-244`）；分类过滤拼成 `(cat:a OR cat:b)`（`src/arxiv_mcp_server/tools/search.py:283-285`），只校验前缀在 20 个已知大类里，子类名不校验（`src/arxiv_mcp_server/tools/search.py:189-210,666-676`）；日期按天粒度（`src/arxiv_mcp_server/tools/search.py:247-268`）。只搜 arXiv，没有别的来源。

### 2.4 全文：HTML 优先、PDF 兜底

`download_paper` 的顺序（`src/arxiv_mcp_server/tools/download.py:934-1131`）：

1. 校验 ID（新旧两种格式，允许 `arxiv:` 前缀与 abs / pdf 链接，`src/arxiv_mcp_server/tools/arxiv_ids.py:15-61`）。不合法直接报错，这是修 #118 路径穿越之后加的[^i118]。
2. 缓存命中就直接返回：存盘一律用不带版本号的 ID，sidecar 里记版本与抽取器版本；抽取器版本升了（现在是 7）缓存自动作废；请求旧版本时拒绝覆盖更新的缓存，除非 `force`（`src/arxiv_mcp_server/tools/download.py:133-137,959-1026`）。
3. 取 `arxiv.org/html/<id>`，200 就用 `_ArticleTextExtractor` 抽文本：只取 `<article>`，跳过脚本、导航、作者注、ACM/IEEE 前言、脚注标记、许可声明、ICML 版式警告，公式优先留 `alttext`（没有 `alttext` 时留 MathML 的文本、去掉 TeX annotation），把被 HTML 拆开的引用号与「Fig. 2」拼回一行，最后按 `\n` 把文本块拼起来（`src/arxiv_mcp_server/tools/download.py:145-533`）。这 389 行代码本身不带 issue 号；每条规则对应的 issue 写在按 issue 分开的回归测试里（#158 #175 #177 #190 #239 #258 #260，见 `tests/tools/test_download_html.py:1`、`tests/tools/test_download_footnotemark.py:1`、`tests/tools/test_download_icml_style.py:1`、`tests/tools/test_download_html_frontmatter.py:1`、`tests/tools/test_download_html_title.py:1`、`tests/tools/test_download_html_switch_noise.py:1`）。
4. HTML 请求返回任何非 200（不只 404）或网络出错，都静默转 PDF 路径（`src/arxiv_mcp_server/tools/download.py:760-770`）：先查 arXiv 上有没有这篇（区分「论文不存在」与「没装 `[pdf]`」），没装 `[pdf]` 就报错；装了就下 PDF 到存储目录、`pymupdf4llm.to_markdown(pdf_path, show_progress=False)` 转（不带任何版面参数，锁定的 0.2.9 版下走非版面模式，见 [2.10](#210-有没有模型调用除了-mcp-还有什么形态)）、转完无论成败都删掉 PDF（`src/arxiv_mcp_server/tools/download.py:1066-1091,803-843`）。同一篇论文的 PDF 转换用 64 路锁条带串行（`src/arxiv_mcp_server/tools/download.py:63-64,846-850`）。
5. 写 `<id>.md` 与 `<id>.meta.json`；装了 `[pro]` 就在后台起一个索引任务（信号量 1，`src/arxiv_mcp_server/tools/download.py:58-117`）。
6. 返回第一页（缺省 12,000 字符），`content_warning` 只在第一页出现一次（`src/arxiv_mcp_server/tools/content.py:8-16,99-129`）。调用方显式给的 `max_chars` 没有硬上限（`src/arxiv_mcp_server/tools/content.py:65`）。

大纲三件套在本地 `.md` 上做：认 ATX 标题、阿拉伯数字编号行、IEEE 罗马数字、34 个常见节名的独占行，遇到 References 就停，什么都认不出时整篇算一个合成节「1」（`src/arxiv_mcp_server/tools/paper_outline.py:44-139,430-518`）。`search_paper_text` 是大小写不敏感的子串查找，去掉重叠过半的片段、优先每节一条（`src/arxiv_mcp_server/tools/paper_outline.py:607-735`）。

### 2.5 按节读 LaTeX 原文

三个 LaTeX 工具共用一个 `_load_source`：先看 `<storage>/.latex/<id>.json` 缓存，没有就下载、解包、展平、原子写缓存；同一篇用 64 路锁条带串行；缓存键就是调用方给的 ID，带版本号与不带版本号各存一份（`src/arxiv_mcp_server/tools/latex.py:71,160-239`）。

| 步骤 | 做法 | 上限 / 规则 | 证据 |
|---|---|---|---|
| 下载 | `GET https://arxiv.org/e-print/<id>` 流式读，声明长度与实收长度都卡 | 压缩后 50 MB | `src/arxiv_mcp_server/tools/latex_archive.py:18,40-77` |
| 解包 | `tarfile` 流模式 `r|*`（自动识别 gz / bz2 / xz），逐个成员检查，**只把 `.tex` 读进内存，从不写盘**；不是 tar 就当单文件 gzip，要求里面有 `\documentclass` 或 `\documentstyle` | 成员 ≤ 2000、路径 ≤ 512 字节且深度 ≤ 20、拒绝软硬链接与特殊文件与重名、单个 `.tex` ≤ 10 MB、`.tex` ≤ 500 个、展开总量 ≤ 100 MB、`.tex` 总量 ≤ 50 MB；按 UTF-8 解码，坏字节替换 | `src/arxiv_mcp_server/tools/latex_archive.py:18-25,80-205` |
| 选主文件 | 打分：有 `\documentclass` +100、有 `\begin{document}` +50、文件名是 main / paper / article / manuscript +20，平手比长度 | — | `src/arxiv_mcp_server/tools/latex_archive.py:208-216` |
| 展平 | 递归内联 `\input` `\include` `\import` `\subimport` 等 8 种写法；先遮掉注释与宏定义体；只展开「定义体里有 include 或 section 命令」的宏；环引用与越界路径不跟；没解析上的命令记进 `unmatched_includes` | 深度 ≤ 20、展平后 ≤ 50 MB、宏展开 ≤ 8 轮 | `src/arxiv_mcp_server/tools/latex_flatten.py:15-25,195-216,315-370` |
| 切节 | 正则找 `\section` `\subsection` `\subsubsection`（带星号的也算），花括号配平取标题，`\texorpdfstring` 取第二参数，标题里的简单宏展开（优先零参数的）、样式命令剥掉；ID 是层级计数 `1`、`1.2`、`1.2.3`；一节到下一个同级或更高级标题为止，最后一节到文件末尾 | 节数 ≤ 10,000、标题 ≤ 200 字 | `src/arxiv_mcp_server/tools/latex_flatten.py:17-18,26-30,152-169,373-408` |
| 定位 | 按 ID，或按大小写与空白归一后的标题（原样与宏展开后两种都试） | `section_id` ≤ 200 字 | `src/arxiv_mcp_server/tools/latex_flatten.py:411-433`、`src/arxiv_mcp_server/tools/latex.py:66,441-442` |
| 返回 | 展平源文的切片，分页 | 缺省 12,000；显式 `max_chars` 最多 50,000；`return_full_text=true` 时不设上限 | `src/arxiv_mcp_server/tools/latex.py:62-69,146-157,453`、`src/arxiv_mcp_server/tools/content.py:59-62` |

**失败时怎么办——不会自动退回 PDF。** `get_paper_latex` 遇到 403 / 404 报「LaTeX source is unavailable for this paper」，另外两个 LaTeX 工具报「arXiv source request failed with HTTP 404」这类原始状态；解包或上限失败报对应的 `LatexSourceError` 文本（`src/arxiv_mcp_server/tools/latex.py:366-378,420-426,470-476`）；`list_paper_latex_sections` 大纲为空时报「Use read_paper or HTML instead」并列出没解析上的 include 命令（`src/arxiv_mcp_server/tools/latex.py:334-342,389-391`）。退回 HTML / PDF 是调用方 agent 自己换工具（`download_paper`）的事，代码里两条链路互不调用。只提交了 PDF 的论文，e-print 端点返回的不是 tar 也不是 gzip，会落到「arXiv response is not a supported source archive」（`src/arxiv_mcp_server/tools/latex_archive.py:104-111`；arXiv 对这类论文返回什么，未实测）。

从代码能看出的边界：只认三级标题，`\chapter`、`\paragraph` 不进大纲；`\appendix` 之后的节接着前面的编号数，带星号的节也占编号，所以 ID 可能对不上论文印出来的节号（`src/arxiv_mcp_server/tools/latex_flatten.py:26,393-397`，读代码推断）；`\begin{abstract}` 不是节，标题与摘要只能从 `get_paper_latex` 的第一页读；只收 `.tex` 成员，`.bbl` 不进来，参考文献条目多半读不到（`src/arxiv_mcp_server/tools/latex_archive.py:171-172`）。

### 2.6 BibTeX

`export_citations`（`src/arxiv_mcp_server/tools/export_citations.py:219-330`）：

- 逐个规范化 ID，非法的记一条错误；合法的**一次** Atom 请求取回（`id_list=a,b,c`），按带版本号的 ID 建表，裸 ID 映射到返回里最新的那个版本（`:149-178`）。
- 同一篇的裸 ID 与带版本 ID 同时出现只留带版本的；完全相同的 ID 去重；请求的版本与返回的不一致就判「not found」，不拿别的版本顶（`:238-288`）。
- 键 = 第一作者姓（按空格切的最后一段）+ 年 + 标题第一个词，全部折成小写 ASCII，撞了按 a、b、…、aa 追加后缀（`:84-122`）。
- 条目一律 `@misc`，字段 title、author（`and` 连接）、year、eprint（保留调用方给的版本号）、archivePrefix、primaryClass（第一个分类）、url（`:125-146`）；`& % $ # _ { } ~ ^ \` 全部转义（`:38-58`）。
- year 取 Atom 的 `<published>`，按 arXiv 的定义是 **v1 的提交日期**[^manual]，请求 v7 也是 v1 那年（`:79-81`）。
- 不取 `<arxiv:doi>`、`<arxiv:journal_ref>`（`src/arxiv_mcp_server/tools/search.py:499-586` 里没有这两个字段）；标题只用单层花括号，没有大小写保护；标题里的 `$…$` 数学被转义成字面的 `\$`。
- 只支持 BibTeX，RIS / CSL-JSON 的 PR #142 自 2026-07-26 开着未合。

### 2.7 主题订阅

存储：`<storage>/watched_topics.json`，一个 `{"topics": [...]}`，每条记 topic（原样的 arXiv 查询串）、categories、max_results、last_checked、created_at、updated_at，翻页时多两个游标字段 drain_from、check_start（`src/arxiv_mcp_server/tools/alerts.py:26,155-175,276-291,384-387`）。

触发：只有调用 `check_alerts` 才查，代码里没有定时、没有后台任务、没有推送（`src/` 里唯一的 `create_task` 是语义索引，`src/arxiv_mcp_server/tools/download.py:111`）。每次查询：对每个主题发一次 `sort_by=date`、**升序**、`date_from = drain_from 或 last_checked` 的搜索，`start = check_start`；按 `published > last_checked` 过滤出新论文；页满了就推进游标、`last_checked` 记到本页最新一篇，页没满就把 `last_checked` 设成现在、清游标（`src/arxiv_mcp_server/tools/alerts.py:339-411`）。新建订阅时 `last_checked` 预设为当前时刻，第一次查不会倒出历史论文（`src/arxiv_mcp_server/tools/alerts.py:272-289`，#227）。

由此可知的事实：比的是 `<published>`（v1 日期），所以只抓新投稿，老论文发新版本不算新；日期过滤按天，所以要靠游标翻页；文件是直接 `write_text` 覆盖，没有原子写也没有文件锁，JSON 坏了读成空列表、下次保存会把它覆盖掉（`src/arxiv_mcp_server/tools/alerts.py:160-175`）；多主题时中途任何一个主题抛异常（限流也算），整轮的游标都不保存、已查到的结果也不返回，因为保存在循环之后、异常在循环外接（`src/arxiv_mcp_server/tools/alerts.py:339-411,419-429`）。

### 2.8 引用图与语义检索

`citation_graph`：把 vN 去掉，对 S2 发**一次** `paper/ARXIV:<id>?fields=…,citations.…,references.…`（嵌套字段不能分页，注释说 S2「通常」每项最多给 1000 条，本仓再切到 `max_citations`）；成功结果缓存 7 天、被限流的结果缓存 5 分钟，文件名 `<id>__limit_<n>.json`，取缓存时找 limit ≥ 请求值里最小的那份（`src/arxiv_mcp_server/tools/citation_graph.py:29-57,175-292,377-476`）。邻居带 `arxiv_id`，能直接接下一跳（`:98-119`）。被限流时返回 `status: rate_limited` 加一句醒目的「This is NOT an empty graph」（`:40-50,148-172`）。

`semantic_search`（`[pro]`）：模型写死 `all-MiniLM-L6-v2`（可配置的 issue #147 与 PR #150 都开着[^i147]），向量存 `<storage>/semantic_index.db` 的一张 SQLite 表，排序是全表载入后矩阵乘（`src/arxiv_mcp_server/tools/semantic_search.py:27-28,133-151,268-324`）。嵌入对象是摘要（`:183`），摘要从 arXiv API 重新取（`:220-234`）。索引键来自 `arxiv.Result.get_short_id()`（`:240`），这个方法返回带版本号的 ID（如 `2107.05580v1`）[^shortid]；而按 `paper_id` 找相似论文时拿用户给的原串去查（`:406-421`），给裸 ID 时会查不到、补索引后仍查不到，这时 `query_vector` 是 `None`，接下来的矩阵乘会抛异常，结果是一条 `Error:`（`:419,430,451-453`）；排除「自己」也按原串比（`:421`）。测试里是直接用裸 ID 插记录、mock 的 `get_short_id` 也返回裸 ID（`tests/tools/test_semantic_search.py:77-125`、`tests/conftest.py:25`），所以测试覆盖不到这条路径。这一条是读代码推断，未跑。

`reindex` 与 `semantic_search` 都在事件循环线程上同步干活：`reindex` 对每篇本地论文同步调 `index_paper_by_id`，每篇都要过一次 arXiv 闸（`run_sync` 里是阻塞的 `time.sleep`）再算嵌入；`semantic_search` 补索引与算查询向量也是同步的（`:341-381,412,425`，`src/arxiv_mcp_server/arxiv_api.py:39-46`）。这与 `CLAUDE.md:73`「Avoid blocking network or filesystem work on the event loop」不一致。进一步从代码推断（未跑）：MCP SDK 对每个请求起一个并发任务[^mcpsdk]，若此时另一个请求正通过 `run_async` 持有闸（`threading.Lock`，在事件循环线程上 `await` HTTP），`reindex` 在同一线程上阻塞地抢这把锁，持锁的协程再也得不到调度，进程会卡死。

### 2.9 存盘目录

```
<storage>/                       缺省 ~/.arxiv-mcp-server/papers，--storage-path 改（进程级，不能按调用改）
├── <id>.md                      download_paper 的正文；旧式 ID 的 / 换成 __（hep-th__9901001.md）
├── <id>.meta.json               sidecar：id、title、authors、published、extractor_version、arxiv_version
├── <id>.pdf                     只在 PDF 转换期间存在，转完即删
├── .latex/<id>.json             LaTeX 展平结果：cache_format、content、main_file、source_files、unmatched_includes
├── citation_graphs/<id>__limit_<n>.json    S2 结果 + cached_at；这里的 / 不换，旧式 ID 写缓存会失败、只记 warning
├── watched_topics.json          主题订阅
└── semantic_index.db            [pro] 向量索引
```

证据：`src/arxiv_mcp_server/config.py:107-120`、`src/arxiv_mcp_server/tools/download.py:541-552,829-843`、`src/arxiv_mcp_server/tools/arxiv_ids.py:85-93`、`src/arxiv_mcp_server/tools/list_papers.py:215-242`、`src/arxiv_mcp_server/tools/latex.py:160-164,203-226`、`src/arxiv_mcp_server/tools/citation_graph.py:175-186,279-292`、`src/arxiv_mcp_server/tools/alerts.py:155-157`、`src/arxiv_mcp_server/tools/semantic_search.py:128-130`。目录是扁平的，按论文 ID 当文件名，没有按项目或课题分；一个服务进程只服务一个目录。

### 2.10 有没有模型调用；除了 MCP 还有什么形态

- **模型调用：没有。** `src/` 里 grep 不到 openai、anthropic、completion 这类名字；唯一的「模型」是 `[pro]` 的本地句向量模型；`[pdf]` 还装进来 pymupdf-layout 自带的 ONNX 版面模型（连带 onnxruntime、numpy、networkx），但按代码看本仓用不上它：锁定的 pymupdf4llm 0.2.9 只在 `pymupdf._get_layout` 非空时走版面分析，这个钩子只有 `import pymupdf.layout` 才会装上[^p4l]，本仓 `src/` 里只 `import fitz` 与 `import pymupdf4llm`（`src/arxiv_mcp_server/tools/download.py:37-53`），没有任何地方 import `pymupdf.layout`（读代码推断，未跑）。两者都不是生成式调用。MCP 的 sampling（让客户端代调模型）也没用。7 个 MCP prompt 只返回文字，由客户端的 agent 自己去执行（`README.md:408` 也这么写）。
- **命令行：没有。** 入口 `main` 直接起服务（`src/arxiv_mcp_server/__init__.py:9-11`），`CLAUDE.md:37` 明说「It is not an interactive CLI」；除了 `--storage-path` 不解析任何参数，`--help` 也会起服务等 stdin（读代码推断）。
- **skill：有一份，但依赖 MCP。** `skills/arxiv-mcp-server/SKILL.md` 共 26 行，frontmatter 只有 name、description，正文是「先搜、再看摘要、LaTeX 先列节再取节」的调用顺序，没有 `scripts/`；它随 Claude Code 插件（`.claude-plugin/`）与 Codex 插件（`.codex-plugin/plugin.json:13-14`）一起装，前提是 MCP 服务已接上。Kiro 用 `POWER.md` 装同一套。
- **当库用：代码形状上可以，但没有为此设计。** 每个工具是 `async def handle_x(arguments: dict) -> list[TextContent]`，测试就是直接 import 这些函数调的（如 `tests/tools/test_semantic_search.py:92`）；但存储目录只能从 `sys.argv` 读，测试靠 monkeypatch `_get_storage_path_from_args`（`tests/tools/test_semantic_search.py:63-67`）；返回值是 MCP 的 `TextContent`，要自己拆 JSON。
- **其他打包**：PyPI wheel、官方 MCP Registry 条目（`server.json`）、Claude Desktop 的 `.mcpb` 包（只出 macOS 两个架构、要 CPython 3.11，`manifest.json:44-49`）、Dockerfile（不装任何 extra，`Dockerfile:14,20`）。

## 3. 为什么：设计动机与踩过的坑

仓库没有 CHANGELOG 文件，变更说明在 GitHub Release 与 issue 里。下表是代码里能对上动机的设计。

| 设计 | 解决什么 | 出处 | 代码 |
|---|---|---|---|
| 做成 MCP 服务，stdio 缺省、`uvx` 一行装、同时出 Claude Code / Codex / Kiro 插件与 `.mcpb` | 一份代码给所有 MCP 客户端用；README 前 180 行几乎都是各家客户端的安装法 | `README.md:21-178` | `.claude-plugin/`、`.codex-plugin/`、`manifest.json`、`server.json` |
| 所有正文默认 12,000 字符一页、搜索缺省 5 条加摘要截断、大纲 + 分节 + 片段检索、工具描述瘦身 | 作者实测一次不带参数的 `read_paper` 回了 111,305 字符（约 27,800 token）[^i127]；工具 schema 本身常驻上下文，瘦身前约 2,500 token[^i131]；测试把 `tools/list` 整体钉在 18,000 字符以内 | #127 #128 #129 #131 | `src/arxiv_mcp_server/tools/content.py:47-96`、`tests/test_tool_schemas.py:128-157` |
| 下载改成同步返回、不再有「converting」状态 | 早期异步转换让 agent 说「等的时候我还能做什么」然后忘了回来读，工作流断掉[^i19] | #19 #54 | `src/arxiv_mcp_server/tools/download.py:934-935` |
| HTML 优先、PDF 兜底，另加抽取器版本号让旧缓存自动作废 | arXiv 的 HTML（LaTeXML 生成）比 PDF 转出来干净；但页面杂质多，8 月连修十几条（站点横幅、重复公式、作者脚注、ICML 版式警告、装饰性标题拆字……），每改一次规则就得让旧缓存失效 | #158 #175 #177 #190 #239 #258 #260 | `src/arxiv_mcp_server/tools/download.py:133-137,145-533` |
| 按节读 LaTeX 原文 | 用户指出另一个项目（arxiv-latex-mcp）只给 LaTeX 源码，认为这样比下载再转 markdown 更快、更轻，数学也准得多（原文「way more accurate with respect to math」）[^i88] | #23 #88 → PR #132 | `src/arxiv_mcp_server/tools/latex.py` 全文 |
| 源码包按敌意输入处理，上限在流式读取中途就卡 | 解压炸弹、路径穿越、链接逃逸；v0.6.0 连着三个 PR（#132 加工具、#133 加固清单、#134 限处理量） | `SECURITY.md:33-35` | `src/arxiv_mcp_server/tools/latex_archive.py:80-205` |
| ID 严格校验，存盘用扁平文件名 | 曾经可以用 `../outside-secret` 读到存储目录外的 `.md`[^i118]；旧式 ID 带 `/` 会建不存在的子目录崩掉（#254） | #118 #254 | `src/arxiv_mcp_server/tools/arxiv_ids.py:15-61,85-93` |
| 全进程一把 3 秒的闸 + raw httpx + 超时 + 429 退避 | arXiv 条款要求[^tou]；`arxiv` 包把日期区间编坏[^i53]；一条对端不再响应的连接曾在锁里永久挂住所有搜索[^i155]；8 月补上 429 退避与 `rate_limited` 软返回 | #53 #125 #155 #238 | `src/arxiv_mcp_server/arxiv_api.py:16-62`、`src/arxiv_mcp_server/config.py:45-73`、`src/arxiv_mcp_server/tools/search.py:117-174` |
| 裸词只搜标题与摘要 | 按日期排序加 `OR` 时，短词（如 MoE）匹配到作者名碎片，结果退化成「这几个分类里最新的论文」 | #159 | `src/arxiv_mcp_server/tools/search.py:231-244` |
| BibTeX 只从 arXiv 元数据生成 | 提需求的人原话是让 agent 导出引用「while ensuring the agent does not make up on its own」[^i41] | #41 → PR #135 | `src/arxiv_mcp_server/tools/export_citations.py:1-9` |
| 引用图一次调用 + 磁盘缓存 + 醒目的限流提示 | 不带 key 的 S2 共享配额很快 429：#160 报工具直接吐原始 429 错误，#226 报加了退避后仍然硬失败；#274 从三次请求减到一次、加缓存，并写明目标是「Clients cannot mistake rate limits for empty success graphs」（这个 PR 的正文带 Cursor agent 的标记） | #160 #169 #226 #274[^i274] | `src/arxiv_mcp_server/tools/citation_graph.py:40-57,417-434` |
| 存盘用裸 ID、sidecar 记版本、拒绝静默降级 | 带版本号下载后按裸 ID 读不到；下载旧版本会悄悄覆盖新版本 | #202 #206 | `src/arxiv_mcp_server/tools/download.py:636-659,995-1026` |
| 订阅新建时 `last_checked = now`、翻页用游标 | 第一次查把历史论文全当新的倒出来；按天粒度的日期过滤在页满时会卡在边界上 | #217 #219 #227 | `src/arxiv_mcp_server/tools/alerts.py:272-289,346-396` |
| 语义索引串行（信号量 1） | 用户报告并行调用把 GPU 压到关机[^i68] | #68 | `src/arxiv_mcp_server/tools/download.py:58-72` |
| 未信任内容标记改成每次响应一次、不插进正文 | 外部用户在 #70 提出论文内容有提示注入风险，于是加了横幅；之后每段都插长横幅既费 token 又让分页拼不回原文，#215 #230 #244 改成首页一个短字段 | #70 #215 #230 #244 | `src/arxiv_mcp_server/tools/content.py:10-16,99-129` |
| `mcp` 依赖钉在 `<2.0.0` | mcp 2.0.0 改了模块名，导入直接坏[^i144] | #144 | `pyproject.toml:35` |

维护史上的一个坑：2026-03-04 有用户开 issue 标题就是「NOT WORKING AND NOT MAINTAINED ANYMORE, SKIP」[^i65]，当时 2025-08 到 2026-03 只有十几个提交；作者 4 月回来连发 0.4.x（4 月 3 日一天 10 个版本号）[^pypi]，之后的大修集中在 7、8 月。8 月那一轮是作者自己试用发现、自己开 issue、自己修（2026-08-21 到 23 日 UTC 开的 51 条 issue、62 个 PR 全出自作者[^aug]），Release 说明写的就是「Patch release after dogfood」[^rel072]；提交里能看到 Cursor 分支名（`cursor/citation-graph-cache-5e91`）与署名 Claude 的提交，作者在用 coding agent 维护。

## 4. 跑起来要什么

| 项 | 基础安装 | `[pdf]` | `[pro]` | 证据 |
|---|---|---|---|---|
| Python | ≥ 3.11 | 同 | 同 | `pyproject.toml:10` |
| 直接依赖 | 13 个（arxiv、httpx、mcp < 2、pydantic、uvicorn、starlette 等） | + pymupdf4llm、pymupdf-layout | + sentence-transformers、numpy | `pyproject.toml:30-69` |
| 锁文件里的传递闭包 | 43 个包 | 56 个（多出的 13 个里有 pymupdf-layout 带进来的 onnxruntime、numpy、networkx、sympy、protobuf） | 93 个（含 torch 2.10.0） | `uv.lock`，用 tomllib 静态算的闭包（含只在某些平台装的包） |
| 模型与 key | 不要任何 key；不调模型 | 同 | 首次运行从 Hugging Face 拉 MiniLM | `src/arxiv_mcp_server/tools/semantic_search.py:27,154-160`、`SECURITY.md:43` |
| 可选 key | `SEMANTIC_SCHOLAR_API_KEY`：代码里只是有值就加 `x-api-key` 头；「免费申请、不填也能用到共享配额耗尽」是 README 自述 | | | `src/arxiv_mcp_server/tools/citation_graph.py:122-133`、`README.md:467` |
| 外部服务 | export.arxiv.org、arxiv.org（html / pdf / e-print）、api.semanticscholar.org；不联网的只有本地读、三个大纲工具、`list_papers`、订阅的增删查，以及 `download_paper`、三个 LaTeX 工具、`citation_graph` 命中缓存时 | 同 | + huggingface.co | 第 [2.2](#22-外部接口与限流闸) 节 |
| 算力 | 纯 CPU、I/O 为主 | PDF 转换在 CPU 上 | 句向量模型，CPU / GPU 都行 | #68[^i68] |
| 操作系统 | CI 覆盖 Linux / Windows / macOS × 3.11 / 3.12 / 3.13，每个组合都检查 `[pdf]` `[pro]` 能从二进制 wheel 解析（不安装、不测）；`.mcpb` 只有 macOS；Docker 镜像不含 extra | | | `.github/workflows/tests.yml:15-19,35-42`、`manifest.json:44-49`、`Dockerfile:14,20` |
| 客户端 | 一个能说 MCP 的客户端（stdio JSON-RPC，或 Streamable HTTP） | | | `src/arxiv_mcp_server/server.py:275-289` |
| 磁盘 | 存储目录（缺省在用户家目录） | 转换期间临时存 PDF | 一个 SQLite 文件 | 第 [2.9](#29-存盘目录) 节 |

许可证方面要注意 `[pdf]` 的依赖，而且要按版本看。本仓 `uv.lock` 锁的是 pymupdf 1.27.1、pymupdf4llm 0.2.9、pymupdf-layout 1.27.1：前两个在 PyPI 上标「AGPL-3.0 或 Artifex 商业许可」；pymupdf-layout 1.27.1 标的是「PolyForm Noncommercial 或 Artifex 商业许可」，wheel 里的 COPYING 也是这句。pymupdf-layout 的许可随版本变过：1.26.6 标「Commercial license」，1.27.1、1.27.2、1.28.0 是 PolyForm Noncommercial 或商业，1.28.2 改成 AGPL-3.0 或商业[^plic]。`pyproject.toml` 只写了下限（`pymupdf-layout>=1.26.6`、`pymupdf4llm>=0.0.17`，`pyproject.toml:52-55`），用 README 的 `uvx --from 'arxiv-mcp-server[pdf]'` 装时拿到哪一版、按哪份许可，取决于装的那天 PyPI 上的版本（未实测）。其余：`arxiv`、`mcp` 是 MIT，sentence-transformers 是 Apache-2.0[^deplic]。平台的 `pdf` skill 锁的是 pymupdf4llm、pymupdf、pymupdf-layout 都为 1.28.2（`platform/skills/pdf/scripts/extract.py:1-6`、`platform/skills/pdf/scripts/extract.py.lock:183-222`）。

## 5. 和平台对照

只列事实，不下接不接的结论。

### 5.1 平台这个阶段现在有什么

| 平台现状 | 证据 |
|---|---|
| 文献阶段没有「步骤」能力；主文件 `sources.md` 由助理手写（`ai4sci output new literature`），框架只认文件名、写法不限 | `platform/framework/capabilities/__init__.py:45-52`、`platform/coordinator/README.md:120`、`docs/architecture/README.md:170` |
| 找材料靠两层 CLI 自带的联网搜索与网页读取（Claude Code 的 WebSearch / WebFetch、Codex 的 web_search），适配器必须放行 | `platform/backends/claude_code.py:40-42`、`platform/backends/codex.py:114`、`docs/architecture/README.md:164` |
| `pdf` skill：PDF（本地或链接）→ `paper.md` + `images/` + `structured.json`（分节、表格、图注、参考文献、题目作者年份 DOI），后端 pymupdf4llm 版面模式，锁 1.28.2 | `platform/skills/pdf/SKILL.md:1-7,38-44`、`platform/skills/pdf/scripts/extract.py:1-6` |
| `download` skill：git 仓库、单个文件、Hugging Face 仓库拉进工作区 `materials/`，留收据 | `platform/skills/download/SKILL.md:1-6` |
| 假设、写作两个阶段也没有步骤能力，主文件待第一个能力定名 | `docs/architecture/README.md:170`、`platform/coordinator/README.md:64` |

### 5.2 多了什么、重叠什么

| 功能 | 平台现在 | arxiv-mcp-server | 关系 |
|---|---|---|---|
| 检索论文 | 助理用 CLI 自带网页搜索，来源不限 | 只搜 arXiv；Atom API、分类与日期过滤、分页、总数、限流 | 重叠（范围更窄、结构化更强） |
| 读 PDF | `pdf` skill，pymupdf4llm 1.28.2 版面模式，出 `structured.json`（表格、参考文献、图） | 只在 HTML 拿不到时走 PDF；用锁定的 pymupdf4llm 0.2.9 的 `to_markdown`，按代码看是非版面模式；只出一个 `.md`，不出结构化字段、不存图 | 重叠（同一个库，版本与模式不同） |
| 读 arXiv HTML | 助理可以 WebFetch 网页 | 专门的 HTML 抽取器 + 标题启发式 + 分页 | 部分重叠 |
| 按节读 LaTeX 原文 | 没有 | 有 | 多出 |
| BibTeX | 没有 | `@misc`，只来自 arXiv 元数据 | 多出（与写作阶段相关） |
| 引用图 | 没有 | S2 一跳，带 `arxiv_id` 可继续跳 | 多出（需要 S2 联网） |
| 主题订阅 | 没有 | 拉取式，存一个 JSON | 多出 |
| 本地论文缓存与语义检索 | 原件放工作区 `materials/` | 放自己的存储目录；`[pro]` 只嵌摘要 | 多出，但存放位置不同 |
| 材料清单 `sources.md` | 助理手写 | 不产 | 无对应 |
| 拉代码、数据、权重 | `download` skill | 不做 | 无对应 |
| 假设、写作 | 无能力 | 只有 `research-question`、`literature_review`、`literature-synthesis` 几段 prompt 文字，没有代码 | 仅文字层面 |

### 5.3 接进来会碰到的现有规则

| 规则 | 平台怎么定的 | arxiv-mcp-server 的相关事实 | 证据 |
|---|---|---|---|
| P-1 执行层是唯一写代码的，框架不调模型 | 框架零模型调用；skill 脚本是确定性工具 | 本身零模型调用 | `docs/architecture/README.md:151`；本文 [2.10](#210-有没有模型调用除了-mcp-还有什么形态) |
| P-11 两层 agent 不继承本机的插件与配置 | Claude Code 适配器 `--setting-sources ""` + `--strict-mcp-config` + `--disable-slash-commands`；Codex 用私有 `CODEX_HOME`、`mcp_servers={}` | README 给的装法都是往客户端的 MCP 配置里登记：缺省是一段 `mcpServers` JSON（`uvx arxiv-mcp-server`），Claude Code / Codex 另给 `mcp add` 一行命令与插件（插件同时装 MCP 连接与自带 SKILL.md） | `platform/backends/claude_code.py:3-11,39`、`platform/backends/codex.py:7-13,118`、`README.md:21-43,58-90` |
| P-14 助理面前只有 `ai4sci`；联网只用 CLI 自带工具 | Claude Code 的 `--allowedTools` 白名单只放 `Bash(ai4sci …)`、读写指定路径与两件联网工具 | 它的能力只以 MCP 工具的形式暴露，自己发 HTTP；没有命令行 | `docs/architecture/README.md:164`、`platform/backends/claude_code.py:146-166` |
| P-15 需求与产出只在 `projects/<p>/workspaces/<id>/` 里 | 项目整个打包能交给同事 | 缺省存储在 `~/.arxiv-mcp-server/papers`，按论文 ID 扁平存放，一个进程一个目录 | `docs/architecture/README.md:165`、`src/arxiv_mcp_server/config.py:107-120` |
| P-20 文献主文件是 `sources.md`；skill 不开产出目录，写哪里由调用者定 | 下游只认阶段主文件 | 不产 `sources.md`；写到哪里由服务启动参数定，不由每次调用定 | `docs/architecture/README.md:170`、`platform/docs/add-a-skill.md:17,56` |
| P-22 skill 按 agentskills.io 写，脚本 PEP 723 自带依赖、`uv run --locked --offline` 起，框架自己把清单拼进 prompt、不靠 agent 的原生加载 | `make skills` 预热依赖是唯一联网的一步 | 自带 SKILL.md 格式上是 agentskills.io 形状，但没有脚本、内容依赖 MCP 工具；本体是带 13 个直接依赖的 Python 包；运行时每次调用都联网（平台 `download` skill 也是运行时联网） | `docs/architecture/README.md:172`、`platform/docs/add-a-skill.md:57-65`、`skills/arxiv-mcp-server/SKILL.md:1-26` |
| P-7 / P-8 fail-closed、不许吞异常 | 验证不过就停，不静默降级 | 几处软失败：元数据写失败只记 warning（`src/arxiv_mcp_server/tools/download.py:925-926`）；后台索引失败在 `semantic_search.py` 里记 error 后返回 `False`，调用方不看返回值，逃出来的异常在 `download.py:98-102` 被取走、不记日志（`src/arxiv_mcp_server/tools/semantic_search.py:227-232,263-265`）；HTML 请求非 200 静默转 PDF（`src/arxiv_mcp_server/tools/download.py:760-770`）；订阅文件坏了重置为空（`src/arxiv_mcp_server/tools/alerts.py:166-170`）；`get_abstract` 把任何 HTTP 错误报成「不存在」（`src/arxiv_mcp_server/tools/get_abstract.py:149-161`）；三个工具的限流以 `rate_limited` 正常返回 | `docs/architecture/README.md:157-158` |
| P-9 上下文有界 | 进执行层的是有界的账本与笔记 | 所有正文默认有界、带续读游标 | `docs/architecture/README.md:159`、`src/arxiv_mcp_server/tools/content.py:47-96` |
| P-10 框架没有「下一步」，每条命令跑完即退 | 串起来的是协调层 | 订阅不会自己跑，要有人或 agent 调 `check_alerts` | `docs/architecture/README.md:160`、`src/arxiv_mcp_server/tools/alerts.py:314-418` |

## 6. 成熟度

| 项 | 实况 | 证据 |
|---|---|---|
| 规模 | `src/` 31 个文件 8016 行 Python；`tests/` 40 个文件 10,422 行、389 个测试函数；受版本管理的文件合计约 1.27 MB（`git ls-files` 字节数），浅克隆目录连 `.git` 1.9 MB | 本地 `wc` / `du` 统计 |
| 测试写法 | 全部单元测试加协议层测试，网络一律 mock（`mocker` / `aioresponses`），没有打真 arXiv 的测试；源码包的敌意输入（穿越、链接、重名、超限、环引用）有专门用例；CI 环境只装 `test` extra，锁文件闭包里没有 numpy / pymupdf / torch，依赖 numpy 的语义检索用例会 `importorskip` 跳过、PDF 转换用 mock | `tests/tools/test_latex.py:36-323,410-430`、`.github/workflows/tests.yml:35-45`、`tests/tools/test_semantic_search.py:44,62` |
| CI | Lint（black）；测试矩阵 3 OS × 3 Python，跑完构建 wheel 并在隔离 venv 里经 MCP 冒烟（只调 `list_tools`、`list_prompts`、`get_prompt`、`list_papers`，不联网）；Docker 构建冒烟 | `.github/workflows/tests.yml:1-64`、`.github/workflows/lint.yml`、`scripts/smoke_installed_wheel.py` |
| 最近 CI | main 在 42419c1 上 Lint 与测试都绿；2026-09-05、09-09 两个外部 PR 的运行状态是 action_required（等维护者批准才跑） | [^ci] |
| 发版 | 发 GitHub Release 触发：校验 tag 等于版本号 → black + pytest → 构建 → twine check → wheel 冒烟 → PyPI + 官方 MCP Registry；另一条流水线出 macOS 两个架构的 `.mcpb` | `.github/workflows/publish.yml:1-80`、`.github/workflows/build-mcpb.yml` |
| 版本线 | PyPI 37 个版本，0.1.0（2024-12-03）到 0.7.2（2026-08-24）；0.7.0 / 0.7.1 / 0.7.2 连续三天；没有 CHANGELOG 文件，GitHub Release 只从 v0.4.12 开始有 | [^pypi] |
| 提交节奏 | 217 个提交：2024-11 到 2025-04 共 68；2025-06 到 2026-02 共 20；2026-04 37；2026-05 8；2026-07 18；2026-08 66；最后一次 2026-08-26，到 2026-09-27 一个月没有提交 | [^commits] |
| 人 | 作者 193 个提交，其余 17 个身份合计 24 个（含 github-actions 3 个、署名 claude 1 个、未关联 GitHub 账号的 2 个）；2026-08-21 到 23 日（UTC）的 51 条 issue、62 个 PR（#158–#270）全出自作者 | [^commits] [^aug] |
| 社区 | 3175 star、258 fork；开着的 issue 5 条（#147 #149 #276 #277 #278，均为外部用户所开），开着的 PR 6 个（最早 2026-07-22） | [^repo] |
| 依赖风险 | `mcp` 钉在 `< 2.0.0`，PyPI 上 mcp 已到 2.2.0[^deplic]；外部用户 2026-08-07 开的 #149 报它与 MCP 2026-07-28 版规范有三处不符（`tools/list` 顺序不定、没有 `server/discover`、缺缓存提示），未处理 | `pyproject.toml:35`、[^repo] |
| 许可证 | Apache-2.0（Copyright 2024 Joseph Blazick）：允许商用、修改、再分发，含专利授权；再分发要附许可证文本、改过的文件要标明；仓库没有 NOTICE 文件。可选依赖 `[pdf]` 锁定的版本里，pymupdf 与 pymupdf4llm 是 AGPL-3.0 或商业，pymupdf-layout 1.27.1 是 PolyForm Noncommercial 或商业（见第 4 节） | `LICENSE:1-3,189`、`pyproject.toml:11-12` |
| 安全 | `SECURITY.md` 写了威胁模型（论文内容当不可信输入、源码包当敌意输入、HTTP 只绑回环）；报告走邮件、无 SLA | `SECURITY.md:1-43` |

## 7. 还没弄清的问题

1. **真实论文上的抽取质量。** HTML 抽取器的规则是对着 ML 论文（Transformer、Switch Transformers、ICML 模板）调出来的；课题组领域的论文 HTML 覆盖率、抽出来的文本与平台 `pdf` skill 的 `paper.md` 谁更好，要在本平台仓的 #166 拿真材料比。
2. **LaTeX 分节在真源码上的成功率**：多文件工程、自定义分节命令、`\chapter` 体例的学位论文，大纲为空或 ID 对不上印刷节号的比例；只交 PDF 的论文走 e-print 端点到底返回什么（第 [2.5](#25-按节读-latex-原文) 节的推断未实测）。
3. **语义检索的 `paper_id` 模式**是否真如第 [2.8](#28-引用图与语义检索) 节推断那样查不到（索引键带版本号）、最后报矩阵乘的错，要装 `[pro]` 跑一次。
4. **能不能不经 MCP 用它**：handler 在代码形状上可 import，但存储目录只从 `sys.argv` 读、每个模块 import 时各建一个 `Settings()`；在 PEP 723 脚本里 `uv run --locked --offline` 调这些函数行不行、要绕几道，没有试。
5. **多进程时的限流**：闸是进程内的；平台每个执行层会话是新进程，若各自起一个服务，彼此之间没有协调。实验室出口 IP 上几个会话并发时 arXiv 会不会 429，未测。
6. **网络可达性**：实验室与平台所在机器到 arxiv.org、export.arxiv.org、api.semanticscholar.org、huggingface.co 的连通性与速度，未测。
7. **S2 返回哪些引用**：嵌套字段不分页，本仓只取前 `max_citations` 条；S2 返回的顺序是什么（按时间、按影响力还是无序），代码注释里的「通常最多 1000 条」是否属实，未查 S2 文档。S2 API 许可对本地缓存 7 天有没有限制，也没读。
8. **PDF 兜底实际走不走版面模式**：读了 pymupdf4llm 0.2.9 与 pymupdf-layout 1.27.1 的 wheel 源码，推断不走（见 [2.10](#210-有没有模型调用除了-mcp-还有什么形态)），也就是 `[pdf]` 装进来的 onnxruntime 与版面模型用不上；没有装包实跑确认。若不走，PDF 路径出来的 markdown 与平台 `pdf` skill（版面模式）差多少，要拿同一篇论文比。
9. **维护会不会继续**：2026-08-26 之后没有提交、外部 PR 等批；`mcp` 2.x 的迁移计划没见到。
10. **BibTeX 的 year 取 v1 日期、只出 `@misc`**：这是事实，平台写作阶段对引用条目有什么要求还没定，本文不评。
11. **事件循环上的同步调用会不会卡死进程**：第 [2.8](#28-引用图与语义检索) 节从代码推断，`reindex` 或补索引时恰逢另一个请求持有 arXiv 闸，进程会卡住；需要并发发两个请求实测。
12. **`[pdf]` 实际装到哪一版、按哪份许可**：锁文件是 pymupdf-layout 1.27.1（PolyForm Noncommercial 或商业），不经锁文件装时按 PyPI 当天版本（2026-09-27 是 1.28.2，AGPL 或商业）；README 推荐的 `uvx --from 'arxiv-mcp-server[pdf]'` 会不会读仓库的 `uv.lock`，未实测。

## 8. 调研方法

- 浅克隆到外层仓 `vendor/arxiv-mcp-server`（gitignore 挡住），提交 42419c1。逐文件读完 `src/` 全部 31 个 Python 文件；`tests/` 看结构、mock 方式、覆盖到的边界，用 grep 核对具体断言；没有装依赖、没有跑任何代码。
- 依赖闭包用 Python 标准库 `tomllib` 读 `uv.lock` 静态计算；依赖许可证查 PyPI JSON，按锁定版本与最新版分别查。
- 复查时另外只读了三处外部源码：pymupdf4llm 0.2.9 与 pymupdf-layout 1.27.1 的 wheel（下载到临时目录解包，不安装），MCP Python SDK v1.27.0 的 `src/mcp/server/lowlevel/server.py`（`get_capabilities` 与请求分发），PyMuPDF 1.27.1 的 `src/__init__.py`（`_get_layout` 钩子）。
- issue、PR、release、提交按月计数、CI 结果用 `gh api` / `gh issue` / `gh run list` 查，2026-09-27。
- 标了「读代码推断」「未实测」的条目，留给本平台仓 #166 实测时验证。

[^tou]: arXiv, Terms of Use for arXiv APIs, <https://info.arxiv.org/help/api/tou.html>（2026-09-27 读）：legacy API（含 arXiv API、OAI-PMH、RSS）每三秒至多一次请求、单连接；描述性元数据按 CC0；e-print 内容可为个人或研究目的存储使用。
[^manual]: arXiv, arXiv API User's Manual §3.3.2, <https://info.arxiv.org/help/api/user-manual.html>：`<published>` 是 v1 的提交日期，`<updated>` 是所取版本的提交日期；作者提供过的话，条目里有 `<arxiv:journal_ref>` 与 `<arxiv:doi>`。
[^shortid]: `arxiv` 包 `Result.get_short_id()` 的文档字符串：URL 为 `https://arxiv.org/abs/2107.05580v1` 时返回 `2107.05580v1`，<https://github.com/lukasschwab/arxiv.py/blob/master/arxiv/__init__.py>（2026-09-27 读）。本仓 `src/arxiv_mcp_server/tools/download.py:598-606` 也依赖这一点从中取版本号。
[^repo]: GitHub API `repos/blazickjp/arxiv-mcp-server` 与 `gh issue list` / `gh pr list`（2026-09-27 查）：创建于 2024-11-29，3175 star、258 fork，未归档；开着的 issue 为 #147（2026-08-03）、#149「MCP 2026-07-28: non-deterministic tools/list order, no server/discover, missing cache hints」（2026-08-07）、#276（2026-09-13）、#277「search_papers: arXiv HTTP 406 is surfaced as a hard error instead of being handled as throttling (429/503 parity)」（2026-09-19）、#278（2026-09-20），全部由外部用户开；开着的 PR 为 #136 #142 #146 #148 #150 #275。
[^pypi]: PyPI `arxiv-mcp-server` 的发版记录，<https://pypi.org/project/arxiv-mcp-server/#history>（2026-09-27 查）。
[^commits]: GitHub commits API 全量分页按月计数（2026-09-27 查）：2024-11 5、2024-12 21、2025-01 15、2025-03 6、2025-04 21、2025-06 3、2025-08 6、2025-12 2、2026-01 5、2026-02 4、2026-04 37、2026-05 8、2026-07 18、2026-08 66，合计 217；按提交作者分：blazickjp 193，其余 17 个身份 24 个（calclavia 4、github-actions[bot] 3、未关联账号 2、gldanoob 2、其余 13 个各 1，含 claude 1）。
[^ci]: `gh run list -R blazickjp/arxiv-mcp-server`（2026-09-27 查）。
[^rel072]: Release v0.7.2，<https://github.com/blazickjp/arxiv-mcp-server/releases/tag/v0.7.2>：「Patch release after dogfood #238–#245 and #254–#260」。
[^deplic]: PyPI JSON 元数据（2026-09-27 查）：最新版 pymupdf、pymupdf4llm、pymupdf-layout 1.28.2 均为「Dual Licensed - GNU AFFERO GPL 3.0 or Artifex Commercial License」；arxiv 4.0.1 MIT；mcp 2.2.0 MIT；sentence-transformers 6.1.0 Apache-2.0。本仓锁定的是 arxiv 4.0.0、mcp 1.27.0、pymupdf 1.27.1（AGPL 或商业）、pymupdf4llm 0.2.9（AGPL 或商业）、pymupdf-layout 1.27.1（PolyForm Noncommercial 或商业）、sentence-transformers 5.2.2（`uv.lock`）。
[^plic]: PyPI JSON 按版本查 pymupdf-layout 的 `license` 字段（2026-09-27）：1.26.6「Commercial license. See artifex.com for details.」；1.27.1、1.27.2、1.28.0「Dual Licensed - Polyform Noncommercial or Artifex Commercial License」；1.28.2「Dual Licensed - GNU AFFERO GPL 3.0 or Artifex Commercial License」。1.27.1 的 wheel 里 `METADATA` 与 `COPYING` 也写「Polyform Noncommercial or Artifex Commercial License」。1.27.2.2、1.27.2.3 没查。
[^p4l]: pymupdf4llm 0.2.9 wheel 的 `pymupdf4llm/__init__.py:14-26`：`pymupdf._get_layout is None` 时用 `helpers/pymupdf_rag.py` 的 `to_markdown`（非版面，`write_images` 缺省为假），否则走 `helpers/document_layout.py`；PyMuPDF 1.27.1 `src/__init__.py:336` 把 `_get_layout` 初值设为 `None`；pymupdf-layout 1.27.1 wheel 的 `pymupdf/layout/__init__.py:10-25` 在被 import 时才给 `pymupdf._get_layout` 赋值，wheel 里没有自动加载的 `.pth` 文件。
[^mcpsdk]: MCP Python SDK v1.27.0（本仓锁定版本）`src/mcp/server/lowlevel/server.py`：`get_capabilities` 在第 209-213 行只有注册了 `ListResourcesRequest` 处理函数时才生成 resources 能力、才用到 `resources_changed`；`call_tool` 处理函数抛出的异常在第 583-584 行被包成 `isError=True` 的结果；`run` 在第 673-679 行对每条消息 `tg.start_soon(self._handle_message, …)`，请求并发处理。<https://github.com/modelcontextprotocol/python-sdk/blob/v1.27.0/src/mcp/server/lowlevel/server.py>（2026-09-27 读）。
[^aug]: GitHub issues API，`state=all&since=2026-08-01`，按 `created_at` 取 2026-08-20 到 2026-08-24（UTC）：共 113 条，最早 #158（2026-08-21 00:32Z）、最晚 #270（2026-08-23 23:58Z），51 条 issue、62 个 PR，作者全是 blazickjp（2026-09-27 查）。
[^i274]: PR #274「feat: citation_graph fewer S2 calls, disk cache, unmistakable 429」，2026-08-26，<https://github.com/blazickjp/arxiv-mcp-server/pull/274>；正文以 `CURSOR_AGENT_PR_BODY_BEGIN` 开头。#160（2026-08-21）正文贴的是原始「Client error '429 '」，#226（2026-08-22）写的是「hard-fails under Semantic Scholar rate limits」。
[^i19]: Issue #19「Remove "converting" status from download_paper to avoid workflow disruption」，2025-03-26，<https://github.com/blazickjp/arxiv-mcp-server/issues/19>；同类 #54（2025-12-15）。
[^i41]: Issue #41「Export citations」，2025-08-05，<https://github.com/blazickjp/arxiv-mcp-server/issues/41>。
[^i53]: Issue #53「Date filtering broken in paper search - URL encoding issue with submittedDate syntax」，2025-12-14，<https://github.com/blazickjp/arxiv-mcp-server/issues/53>。
[^i65]: Issue #65「NOT WORKING AND NOT MAINTAINED ANYMORE, SKIP」，2026-03-04 开、2026-04-02 关，<https://github.com/blazickjp/arxiv-mcp-server/issues/65>。
[^i68]: Issue #68「Parallel tool invocations can DDoS the GPU, causing it to shut off」，2026-03-12，<https://github.com/blazickjp/arxiv-mcp-server/issues/68>。
[^i88]: Issue #88「Add tools to load LaTeX source only」，2026-04-24，<https://github.com/blazickjp/arxiv-mcp-server/issues/88>；更早的 #23（2025-04-05）要的是同一件事。
[^i118]: Issue #118「Path traversal in `download_paper` allows arbitrary out-of-bounds Markdown file read」，2026-06-29，<https://github.com/blazickjp/arxiv-mcp-server/issues/118>。
[^i127]: Issue #127「Bound paper content responses by default」，2026-07-21，<https://github.com/blazickjp/arxiv-mcp-server/issues/127>：「A live MCP stdio benchmark returned 111,305 response characters—approximately 27,800 tokens」。
[^i131]: Issue #131「Reduce MCP tool-schema token overhead」，2026-07-21，<https://github.com/blazickjp/arxiv-mcp-server/issues/131>：「approximately 10,000 characters / 2,500 tokens before any research begins」。
[^i144]: Issue #144「mcp 2.0.0 breaks imports: FastMCP renamed to MCPServer, module moved」，2026-07-28，<https://github.com/blazickjp/arxiv-mcp-server/issues/144>。
[^i147]: Issue #147「make the semantic_search embedding model configurable」，2026-08-03，<https://github.com/blazickjp/arxiv-mcp-server/issues/147>；对应 PR #150 未合。
[^i155]: Issue #155「search_papers permanently hangs after a hanging connection」，2026-08-17，<https://github.com/blazickjp/arxiv-mcp-server/issues/155>；由 PR #156 修。
[^i278]: Issue #278「get_abstract: any upstream HTTP error is reported as "Paper <id> not found on arXiv"」，2026-09-20，外部用户 jackiectl2 开，<https://github.com/blazickjp/arxiv-mcp-server/issues/278>。
