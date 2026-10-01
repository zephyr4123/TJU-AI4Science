---
title: Paper Search MCP 代码级深读
subtitle: 科研 AI 能力选型 · 文献检索候选 · 21 个源、一条下载兜底链、三种形态逐条对账
kind: 开源项目选型深读（只读代码，不跑、不装依赖）
date: 2026-09-27
scope: 仓库 https://github.com/openags/paper-search-mcp，浅克隆到外层 vendor/paper-search-mcp，提交 808e462（main，2026-09-22）；平台一侧对照内仓 platform/ 提交 de3d948（v1.0.1）；文中不带 platform/ 前缀的 文件:行 一律相对 paper-search-mcp 仓库根（包代码在 paper_search_mcp/ 下），带 platform/ 前缀的相对外层仓根；GitHub 与 PyPI 的数据 2026-09-27 经 API 查；对应 issue 项目 #167、叶子 #168
status: 第一版
---

> **结论先行**：它是一个**不调任何模型**的检索、下载、抽文本工具库，外面包了三层壳：MCP 服务（57 个工具）、`paper-search` 命令行（4 个子命令）、一份只有说明没有脚本的 Claude Code skill。README 列的 21 个源都有连接器：17 个调站点提供的接口（REST / Atom / XML），BASE 走 OAI-PMH 翻页再本地过滤，Google Scholar、IACR、SSRN 三个抓 HTML。统一检索 `search_papers` 的缺省 `all` 会把 21 个源全打一遍，但 bioRxiv、medRxiv 把关键词当分类名，Unpaywall 只认 DOI，BASE 是收割后本地过滤（README 另说它要机构 IP 登记，代码里没有对应处理），由服务端按关键词检索的是其余 17 个。去重只看小写 DOI，没有 DOI 再看「题目 + 作者串」是否完全相等，先到先得，不合并字段。出错时 21 个源里有 18 个把请求失败吞掉、返回空列表，调用方看到的是「0 条」，统一检索的 `errors` 里没有记录；总会把失败抛出来的只有 Semantic Scholar 与 PubMed，arXiv 只在持续限流时抛。
>
> 下载兜底链（源自带下载 → OpenAIRE / CORE / Europe PMC / PMC → Unpaywall → 可选 Sci-Hub）是全仓唯一核对 PDF 身份的一路：第 2、3 环拿到的 PDF 要过 `%PDF-` 文件头和前三页的 DOI / 题目身份校验，第 4 环要过身份校验；这是外部贡献者 2026-07 提的 PR #93、2026-09-21 合并的修复。第 1 环「源自带下载」不做任何校验，返回的路径存在就算成功。Sci-Hub 在 main 上缺省关（`use_scihub=False`），但 PyPI 上最新的 0.1.4 仍是缺省开；独立工具 `download_scihub` 无条件注册、没有开关、不做身份校验。命令行与 skill 两种形态里没有 Sci-Hub，也没有兜底链。
>
> 抽全文用 pypdf 的 `extract_text()`（例外：CORE 先返回 CORE 接口给的全文，CiteSeerX 只返回摘要）：没有 OCR，不分版面，公式和表格不单独处理。读代码找到一处走到就必抛的错：CiteSeerX 的 `download_pdf` 用了 `os` 却没有 `import os`。成熟度：87 个提交里一个人占 51 个；CI 只在打 tag 时跑 7 个确定性测试文件，不跑 lint；main 比 PyPI 最新版多 39 个提交。README 里走 PyPI 的装法（uvx、`uv tool install`、pip，以及 skill 的安装步骤）装到的都是 0.1.4，而 0.1.4 对 `mcp` 没有版本上限，PyPI 上 mcp 已到 2.2.0，按 issue #107 的复现，这样装出来的 MCP 服务导入即崩（命令行不 import mcp，不受影响；未实跑）。和平台对照的事实：平台两家适配器起会话时都清空了 MCP 与 CLI 原生 skill，所以它的 MCP 形态与自带 skill 在平台现有会话里都加载不进来；它自带的 skill 教 agent 直接敲全局安装的 `paper-search`，Claude Code 侧只放行 `ai4sci` 前缀，Codex 侧 `ai4sci` 以外的命令在无网络的沙箱里跑。它比平台现有能力多出来的是结构化的多源学术检索，以及从 DOI 找到开放获取 PDF 这一步；和平台重叠的是 `pdf`、`download` 两个 skill，以及 CLI 自带的网页搜索。
>
> 怎么读：第 1 节逐条对 README，第 2 节是主流程，第 3 节是设计原因与作者踩过的坑，第 5 节是和平台的对照（只列事实），第 7 节是还没弄清的问题。横向对比见同目录的 [README.md](README.md)。

## 1. 是不是

### 1.1 源清单

README 说支持 arXiv、PubMed、bioRxiv、medRxiv、Google Scholar、IACR、Semantic Scholar、Crossref、OpenAlex、PMC、CORE、Europe PMC、dblp、OpenAIRE、CiteSeerX、DOAJ、BASE、Zenodo、HAL、SSRN、Unpaywall 和可选的 Sci-Hub（`README.md:62`）。代码里 `ALL_SOURCES` 正好是这 21 个名字（`paper_search_mcp/server.py:145-167`），配了 IEEE / ACM 的 key 时再追加 `ieee` / `acm`（`paper_search_mcp/server.py:178-192`），每个都有连接器文件。下表「证据」列里的 `…/` 是 `paper_search_mcp/academic_platforms/` 的缩写。逐个看端点与实现：

| 源 | 端点与方式 | key | 检索能力（代码实况） | 下载 / 读 | 证据 |
|---|---|---|---|---|---|
| arXiv | `export.arxiv.org/api/query`，官方 Atom 接口；类级锁 + 时间戳，同一进程内每 3 秒最多一次请求；429 / 5xx 与 HTTP 200 的「Rate exceeded.」退避重试 | 无 | 关键词；不带引号、字段前缀和布尔词的多词查询自动改写成 `all:"..."`；排序可选 | `arxiv.org/pdf/{id}.pdf`；下载不经过限速锁，没有超时、不看状态码、不查 PDF 头，响应体原样写盘 | `…/arxiv.py:27-32,46-102,104-116,163-170` |
| PubMed | NCBI E-utilities `esearch` + `efetch`，官方；两次请求都不查状态码，直接解析 XML | 无（不带 NCBI api_key） | 关键词；`sort` 可选 relevance / pub_date | 不支持，`raise NotImplementedError` | `…/pubmed.py:12-44,103-118` |
| bioRxiv | `api.biorxiv.org/details/biorxiv`，官方 | 无 | **不按关键词检索**：只认 DOI、日期区间、分类名，空串取近 30 天；关键词会被规整成分类名（空格变下划线）传上去 | 下载固定拼 `v1.full.pdf`（检索结果里的 `pdf_url` 用真实版本号） | `…/biorxiv.py:20,32-63,114-117,130-162,178` |
| medRxiv | 同一接口的 medrxiv 分支，没随 bioRxiv 重写 | 无 | **只按分类名**过滤近 30 天；关键词同样被当成分类名；外层翻页循环在第一页之后必然 `break`，最多拿第一页 100 条 | 固定拼 `v1.full.pdf` | `…/medrxiv.py:11,19-85,101` |
| Google Scholar | **抓 `scholar.google.com` 的 HTML**（requests + BeautifulSoup）；整个进程共用一个 Session（cookie 跨查询保留），每次请求前从 3 个 UA 里随机换一个、随机等 1–2.5 秒；带 `CONSENT` cookie | 可选代理 URL | 关键词；遇到验证码页或任何异常直接退出循环，返回已拿到的部分 | 不支持；`pdf_url` 恒为空、引用数恒为 0、`paper_id` 用 `hash(url)` | `…/google_scholar.py:19-54,77-94,132,137,144,183-188,247-253,271-287` |
| IACR | **抓 `eprint.iacr.org/search` 的 HTML**；`fetch_details=True` 时每条结果再抓一次详情页 | 无 | 关键词 | 拼 `{id}.pdf`，存成 `iacr_{id}.pdf`；下载没有超时，失败返回错误字符串，不抛异常 | `…/iacr.py:19-20,142-198,200-227` |
| Semantic Scholar | Graph API v1 `/paper/search`，官方；429 按 Retry-After 退避 | 可选 `x-api-key`；key 被 403 拒时去掉 key 重试一次 | 关键词 + `year` | 取 `openAccessPdf.url`，为空时用正则从 `disclaimer` 文本里抠 URL，优先取 doi.org 链接（出版商落地页，不是 PDF）；下载不查 PDF 头 | `…/semantic.py:26-27,59-116,165-269,373-411` |
| Crossref | `api.crossref.org/works`，官方；`mailto` 写死 `paper-search@example.org`，UA 里写的是另一个仓库地址 `github.com/Dragonatorul/paper-search-mcp` | 无 | 关键词 + `filter` / `sort` / `order`；过滤掉 peer-review、figure 等 5 种非论文类型；没有日期的记录填 `1970-01-01` | 不支持（检索结果里有从 `resource` / `link` 字段取的 `pdf_url`） | `…/crossref.py:15-31,40-102,131-133,237-270` |
| OpenAlex | `api.openalex.org/works`，官方 | 可选 key（Bearer 头）与联系 email | 关键词 + `filter` | 不支持，`download_pdf` 抛 `NotImplementedError`（检索结果里有 `pdf_url`） | `…/openalex.py:16-42,63-183,185-201` |
| PMC | E-utilities `esearch` + `esummary`（`db=pmc`），email 写死；结果不带摘要（`abstract=''`），`pdf_url` 一律按 PMCID 拼 | 无 | 关键词 | 拼 `ncbi.nlm.nih.gov/pmc/articles/{id}/pdf/`，查 Content-Type | `…/pmc.py:21-25,49-101,151-163,284-337` |
| CORE | `api.core.ac.uk/v3/search/works`，官方；引用数放进 `extra`，`citations` 字段仍是 0 | 可选 Bearer；401 / 403 时去掉 key 重试 | 关键词 | 详情里拿 `downloadUrl`；拿不到就按 id 再搜一次，**退到任何一个带 `pdf_url` 的候选**（可能不是同一篇）；查 Content-Type | `…/core.py:21-40,85-126,269-274,313-326,342` |
| Europe PMC | `ebi.ac.uk/europepmc/webservices/rest/search`，官方；引用数同样放进 `extra` | 无 | 关键词 | `fullTextUrlList` 里的 pdf，或拼 PMC 的 URL；查 Content-Type | `…/europepmc.py:18,45-70,220-228,235-311` |
| dblp | `dblp.org/search/publ/api`，官方 XML；失败或空结果时退到抓 HTML 页 | 无 | 关键词 | 不支持，下载与读都抛 `NotImplementedError` | `…/dblp.py:20-21,33-127,129-206,324-363` |
| OpenAIRE | `api.openaire.eu/search/researchProducts`，三套请求头轮换、每套最多 3 次，再退到 `/search/publications` | 可选 Bearer（README 的 key 表里没列） | 关键词 | 不支持，下载与读都抛 `NotImplementedError` | `…/openaire.py:22-43,45-125,270-321,651-693` |
| CiteSeerX | `citeseerx.ist.psu.edu/api/search`；被重定向到 web.archive.org 就当不可用；SSL 失败时关掉证书校验重试 | 可选 Bearer（README 的 key 表里没列） | 关键词 | `download_pdf` 用了 `os.makedirs` / `os.path.join`，但文件没有 `import os`，一旦查到 PDF 链接就抛 `NameError`；`read_paper` 有摘要就直接返回摘要，不抽全文 | `…/citeseerx.py:1-15,23-27,36,45-64,296-342,344-382` |
| DOAJ | `doaj.org/api/search/articles/{关键词}`，官方；关键词放在 URL 路径里，另拼了一份带过滤条件的 Lucene 串放进 `query` 参数（DOAJ 认不认这个参数，没查） | 可选 `X-API-Key` | 关键词 | 拿 paper_id 当查询词搜、取第一条；没有 `pdf_url` 就用 doi.org 链接；响应不是 PDF 只打警告照样写盘 | `…/doaj.py:27-45,85-106,360-414` |
| BASE | 在 `BaseHttpSearchInterface.fcgi` 上发 OAI-PMH `ListRecords`，**本地按关键词过滤**；翻页没有上限（每页间隔 0.5 秒），直到凑够条数或没有下一页 | 无（README 说要机构 IP 登记，代码里没有相关处理） | 没有服务端检索 | 视记录 | `…/base_search.py:23-32`、`…/oaipmh.py:65-169` |
| Zenodo | `zenodo.org/api/records`，官方；排序写死 `mostrecent`，缺省 `type=publication` | 可选 token | 关键词，结果按时间不按相关度 | 视记录；失败返回错误字符串 | `…/zenodo.py:33-45,56-159` |
| HAL | `api.archives-ouvertes.fr/search/`，官方，按 `score desc` | 无 | 关键词 | 先对 `/{id}/document` 发 HEAD，状态 200 就下载（不要求 Content-Type 是 PDF）；失败返回错误字符串 | `…/hal.py:32,63-119,121-154,197-211` |
| SSRN | **抓两个 SSRN 搜索页的 HTML**（模块注释自称「SSRN 没有公开 API」）；遇到 Cloudflare 的 403 返回空 | 无 | 关键词 | 尽力而为：页面上暴露了公开 PDF 链接才下，下前查 Content-Type 或 `%PDF` 头 | `…/ssrn.py:1-17,47-49,106-154,198-233` |
| Unpaywall | `api.unpaywall.org/v2/{doi}?email=`，官方 | **必须配 email**，否则整源跳过 | 只认 DOI，最多一条 | 自己不托管 PDF，给 `url_for_pdf` | `…/unpaywall.py:16-69,148-178,194-216` |
| Sci-Hub | 抓镜像 HTML，依次找 `embed`、`iframe`、`button` 元素的 onclick、含 pdf 的链接；两次请求都 `verify=False`；标识符以 `.pdf` 结尾时直接当成 PDF 链接去下 | 无 | 不做检索 | 只查 `Content-Type == application/pdf` | `…/sci_hub.py:35-139` |
| IEEE / ACM | 骨架：配了 key 才注册 3 个工具；即便配了 key，搜索、下载、读三个方法仍然全部 `raise NotImplementedError` | 要 key 才注册 | 无 | 无 | `…/ieee.py:67-107`、`…/acm.py:73-113`、`paper_search_mcp/server.py:175-192` |
| ChemRxiv | `chemrxiv.py` 文件存在（套 Crossref 过滤），但 server 与 cli 都没有 import，没有测试，README 也没列 | — | — | — | `…/chemrxiv.py:1-60` |

归纳：17 个调站点提供的接口（arXiv、PubMed、bioRxiv、medRxiv、Semantic Scholar、Crossref、OpenAlex、PMC、CORE、Europe PMC、dblp、OpenAIRE、CiteSeerX、DOAJ、Zenodo、HAL、Unpaywall，其中 dblp 带 HTML 兜底）；BASE 用 OAI-PMH 收割加本地过滤；抓网页的是 Google Scholar、IACR、SSRN，外加 Sci-Hub。

### 1.2 统一与去重

| 环节 | 代码实况 | 证据 |
|---|---|---|
| 统一形状 | 每个连接器产出 `Paper` dataclass：9 个必填字段（id、题目、作者、摘要、DOI、发表日期、pdf_url、url、source）加 6 个可选字段 | `paper_search_mcp/paper.py:9-29` |
| 序列化 | `to_dict()` 把作者、分类、关键词、参考文献都拼成 `"; "` 分隔的**一个字符串**，日期转 ISO 串，`extra` 用 `str(dict)` 转成 Python repr 字符串（不是 JSON） | `paper_search_mcp/paper.py:44-80` |
| 缺省值 | `citations` 缺省 0，只有 Semantic Scholar、Crossref、OpenAlex、CiteSeerX 四个源往这个字段里填真值；CORE、Europe PMC 拿到了引用数却放进 `extra`；Google Scholar、IACR 恒填 0；IACR 拿不到日期时填 `1900-01-01`，Crossref 填 `1970-01-01`；`references` 字段全仓没有任何连接器填 | `paper_search_mcp/paper.py:27-28`、`paper_search_mcp/academic_platforms/google_scholar.py:144`、`paper_search_mcp/academic_platforms/iacr.py:120,135`、`paper_search_mcp/academic_platforms/crossref.py:131-133`、`paper_search_mcp/academic_platforms/core.py:272`、`paper_search_mcp/academic_platforms/europepmc.py:225` |
| DOI 抽取 | README 说的「智能 DOI 抽取」（`README.md:61`）是一条正则 `10\.\d{4,9}/...`，在摘要、URL、题目里找 | `paper_search_mcp/utils.py:3-8` |
| 去重键 | 有 DOI 用小写 DOI；没有就用小写题目 + 作者串；再没有用 paper_id。作者串在各源写法不同（PubMed 是「姓 缩写」，OpenAlex 是 display_name），跨源时题目键很难相等；按代码推断，跨源去重实际只靠 DOI，未实测 | `paper_search_mcp/server.py:212-223`、`paper_search_mcp/academic_platforms/pubmed.py:59-67`、`paper_search_mcp/academic_platforms/openalex.py:111-115` |
| 去重方式 | 先到先得：按请求的源顺序拼接，第一次出现的留下，后来的整条丢弃，不合并字段（例如先到的 arXiv 条目引用数是 0，后到的 Semantic Scholar 条目的引用数就丢了）；没有跨源排序 | `paper_search_mcp/server.py:226-237,625-640` |
| DOI 归一化 | 仓里有 `_normalize_doi`（去 `doi:` 与 `https://doi.org/` 前缀），但去重没用它，只用于兜底链的身份比对 | `paper_search_mcp/server.py:357-364` |
| 命令行 | 同一套去重逻辑复制了一份 | `paper_search_mcp/cli.py:97-116` |

### 1.3 下载兜底链与 Sci-Hub

`download_with_fallback(source, paper_id, doi="", title="", save_path="./downloads", use_scihub=False, scihub_base_url="https://sci-hub.se")`（`paper_search_mcp/server.py:1074-1083`），每一环：

| 环 | 做什么 | 校验 | 证据 |
|---|---|---|---|
| 1 源自带下载 | 16 个源映射到各自的 `download_pdf`（不含 OpenAlex、OpenAIRE、Google Scholar、dblp、Unpaywall）；返回值是存在的文件路径就算成功 | **不查 PDF 头，不查身份**。arXiv 不看状态码，404 页面也会存成 `{id}.pdf` 并算成功；Semantic Scholar 可能把 doi.org 落地页的 HTML 存成 `.pdf`；CORE 可能下到另一篇 | `paper_search_mcp/server.py:1099-1134`、`paper_search_mcp/academic_platforms/arxiv.py:163-170`、`paper_search_mcp/academic_platforms/semantic.py:397-408`、`paper_search_mcp/academic_platforms/core.py:315-326` |
| 2 开放获取仓储 | 依次在 OpenAIRE → CORE → Europe PMC → PMC 里用 DOI、题目各搜一次（每次最多 3 条）；候选题目与期望题目的词 F1 小于 0.6 就跳过（候选 DOI 与期望 DOI 相同则不比题目）；同一个 URL 只试一次。每次仓储检索直接 `to_thread`，没有超时，整条兜底链也没有总超时 | 下载后查前 1024 字节里有没有 `%PDF-`，再抽前三页文字：DOI 出现即通过，否则期望题目里长度 ≥ 4 的非停用词有 60% 出现在文中才通过；抽不出文字（扫描件）一律拒；通过后先写 `.part` 再原子改名 | `paper_search_mcp/server.py:247-321,378-526` |
| 3 Unpaywall | 给了 DOI 且配了 email，取 `best_oa_location` 的 `url_for_pdf`（没有就 `url`，再没有就扫 `oa_locations`），走同一个 `_download_from_url` | 同上 | `paper_search_mcp/server.py:1144-1158`、`paper_search_mcp/academic_platforms/unpaywall.py:35-69` |
| 4 Sci-Hub | 仅 `use_scihub=True` 时；标识符取 DOI > 题目 > paper_id；下载后 `_pdf_matches_expected` 校验，不过就删文件 | 题目和 DOI 都没给时校验函数直接返回 True（`paper_search_mcp/server.py:389-390`），这时 Sci-Hub 的结果不被校验 | `paper_search_mcp/server.py:1160-1188` |
| 失败 | 返回一个以 `Download failed after OA fallback chain` 开头的字符串，列出每一环的原因；**不抛异常**，调用方要自己分辨返回的是路径还是错误信息 | — | `paper_search_mcp/server.py:1161,1188` |

**Sci-Hub 默认开不开、怎么关**：

- main 上 `download_with_fallback` 的 `use_scihub` 缺省 `False`（`paper_search_mcp/server.py:1081`），是 2026-09-20 合并的 PR #115 翻过来的；之前缺省 `True`，issue #103 指出这与 README 的「由用户显式开启」矛盾[^i103][^pr115]。
- **PyPI 上最新发布的 0.1.4 仍是 `use_scihub: bool = True`**[^v014]。README 的 uvx、`uv tool install`、pip 三种安装方法（`README.md:262-355`）都从 PyPI 装；Docker 与 clone 源码两种（`README.md:385-488`）用本地源码构建，装到的是当前代码；Smithery 两种（`README.md:252-258,359-381`）用的是哪个版本没查。
- 独立工具 `download_scihub` 在 MCP 里无条件注册（`paper_search_mcp/server.py:1052-1071`），不经过任何身份校验。全仓没有关掉它的环境变量或配置项（`paper_search_mcp/config.py`、`.env.example` 都没有 Sci-Hub 条目）；issue #103 同时建议加一个 `PAPER_SEARCH_MCP_ENABLE_SCIHUB` 开关，PR #115 只改了缺省值，没有加[^i103]。宿主一侧能不能按工具名屏蔽它，取决于 MCP 客户端。
- `download_scihub` 的 `identifier` 以 `.pdf` 结尾时，连接器不去镜像查，直接把它当 PDF 链接下载，而且 `verify=False`（`paper_search_mcp/academic_platforms/sci_hub.py:55,81-83`）。
- 命令行与 skill 里没有 Sci-Hub：`paper_search_mcp/cli.py` 不 import `sci_hub`（`paper_search_mcp/cli.py:12-33`），`claude-code/SKILL.md` 也没提。
- Sci-Hub 的两次 HTTP 请求都 `verify=False`（`paper_search_mcp/academic_platforms/sci_hub.py:55,87`）。全仓另有两处在 SSL 失败时关掉证书校验重试：CiteSeerX、OpenAIRE（`paper_search_mcp/academic_platforms/citeseerx.py:50-54`、`paper_search_mcp/academic_platforms/openaire.py:151-159`）。

### 1.4 三种形态

| | MCP 服务 | 命令行 | skill |
|---|---|---|---|
| 入口 | `paper-search-mcp` → `server:main`；也可 `python -m paper_search_mcp.server` | `paper-search` → `cli:main` | `claude-code/SKILL.md`（59 行），README 教用户 curl 到 `~/.claude/skills/paper-search/` |
| 证据 | `pyproject.toml:54-56`、`paper_search_mcp/server.py:1863-1892` | `pyproject.toml:56`、`paper_search_mcp/cli.py:262-278` | `claude-code/SKILL.md:1-59`、`README.md:211-241` |
| 传输 | stdio（缺省）、sse、streamable-http；stdio 下起一个线程盯父进程，客户端死了就退出；两种网络传输都没有鉴权，缺省绑 `127.0.0.1:8000`（`README.md:479-481` 自己提醒：绑 `0.0.0.0` 会暴露一个没有鉴权的服务） | 进程跑完即退 | 走命令行 |
| 功能面 | 57 个工具常驻 + IEEE / ACM 各 3 个（有 key 才注册）：统一检索 1、分源检索 21、分源下载 16、分源读 16、`get_crossref_paper_by_doi` 1、`download_with_fallback` 1、`download_scihub` 1 | 4 个子命令：`search` / `download` / `read` / `sources` | 说明里只教这 4 个子命令 |
| 统一检索 | `search_papers`：每个源 45 秒超时、32 线程有界线程池、无效源名进 `errors` | `cmd_search`：`asyncio.gather` + `to_thread`，**没有超时**；不认识的源名静默丢掉；全部源失败也退 0 | 同命令行 |
| 下载 | 分源工具 + 兜底链 + Sci-Hub | 只调源自带的 `download_pdf`，**没有兜底链**；连接器返回错误字符串时照样打印 `{"status":"ok","path":"Failed to ..."}` | 同命令行 |
| 源专有参数 | arXiv 排序、PubMed 排序、Crossref filter / sort / order、OpenAlex filter、Semantic Scholar year、IACR fetch_details | 只有 `-y`（仅 Semantic Scholar） | 同命令行 |
| 输出 | 工具返回 dict / list / str | `search` 出缩进的多行 JSON，`download` 出一行 JSON，`read` 出纯文本 | 同命令行 |
| 证据 | `paper_search_mcp/server.py:529-651,656-683,1052-1188,1835-1888` | `paper_search_mcp/cli.py:82-94,123-128,135-197,200-215` | — |

少掉的 MCP 工具：PMC、CORE、Europe PMC 三个源的连接器都实现了 `download_pdf` 与 `read_paper`，但没有注册成 MCP 工具，只能经兜底链（`source="pmc"` 等）或命令行 `paper-search download pmc <id>` 用到。反过来，10 个 MCP 工具注册了但永远只报「不支持」：PubMed、Crossref、dblp、OpenAIRE、OpenAlex 各自的下载与读，其中 5 个返回一段说明文字（PubMed 两个、Crossref 两个、`read_openalex_paper`），另外 5 个直接把 `NotImplementedError` 抛给 MCP 客户端（dblp 两个、OpenAIRE 两个、`download_openalex`）（`paper_search_mcp/server.py:783-796,855-865,1032-1049,1191-1205,1408-1463,1626-1649`）。`download_citeseerx` 注册了，但只要查到 PDF 链接就撞上 1.1 节的 `NameError`。命令行与 MCP 接口不一致，issue #77 与 PR #78 还开着[^i77]。

### 1.5 README 说了、代码里没有或很薄

| README 的说法 | 代码实况 | 证据 |
|---|---|---|
| Sci-Hub 缺省不开（`README.md:197`） | main 成立；已发布的 0.1.4 缺省开；`download_scihub` 常驻无开关 | 见 [1.3](#13-下载兜底链与-sci-hub) |
| 兜底链「依赖出版商开放获取链接」（`README.md:60`） | 兜底链不用检索结果里已有的 `pdf_url`（OpenAlex、Crossref 的链接不进链），出版商链接只经 Unpaywall 间接拿到 | `paper_search_mcp/server.py:1097-1158` |
| 能力矩阵「来自功能与端到端回归测试的实测结果」（`README.md:90`） | `tests/e2e_test.py` 是手动脚本（`python tests/e2e_test.py`，零个 `def test_`），pytest 配置只收 `test_*.py`，仓里没有任何一次运行结果的记录 | `tests/e2e_test.py:1-3`、`pyproject.toml:61-62` |
| 能力矩阵里 CiteSeerX 下载 ✅（`README.md:108`） | `download_pdf` 缺 `import os`，拿到 PDF 链接后必抛 `NameError`；`tests/test_citeseerx.py` 的 4 个测试都不碰下载 | `paper_search_mcp/academic_platforms/citeseerx.py:1-15,321,327` |
| 能力矩阵里 bioRxiv、medRxiv 检索 ✅「reliable」（`README.md:96-97`） | 两者都不按关键词检索，统一检索传进去的关键词被当成分类名 | 见 [1.1](#11-源清单) |
| IEEE / ACM「search registered」（`README.md:168-169`） | 注册了，但配了 key 也一律 `NotImplementedError`；配上 key 后每次 `search_papers(all)` 都会多一条 ieee / acm 错误 | `paper_search_mcp/academic_platforms/ieee.py:67-80` |
| 没有 key 时「只在启动时打一条警告」（`README.md:180`） | server 没 key 就不 import、不实例化，不打任何日志；带警告的 `IEEESearcher.__init__` 在 server 里走不到 | `paper_search_mcp/server.py:178-192`、`paper_search_mcp/academic_platforms/ieee.py:47-53` |
| 「服务目前只跑本地 stdio」（`README.md:51`） | 代码已支持 sse 与 streamable-http，都没有鉴权 | `paper_search_mcp/server.py:1835-1888` |
| SSRN 下载尽力而为（`README.md:113`） | 代码确实实现了尽力下载；但 MCP 工具说明写「metadata-only，不支持下载」，模块注释写「PDF download is explicitly NOT implemented」，三处说法互相矛盾，而工具说明是给模型看的那一份 | `paper_search_mcp/server.py:1379,1600,1615`、`paper_search_mcp/academic_platforms/ssrn.py:12-13,106-154` |
| key 表列了 10 个变量（`README.md:127-138`） | 代码还读 `OPENAIRE_API_KEY`、`CITESEERX_API_KEY`（`.env.example` 里有、README 表里没有） | `paper_search_mcp/academic_platforms/openaire.py:36`、`paper_search_mcp/academic_platforms/citeseerx.py:36`、`.env.example:22-23` |
| BASE「要机构 IP 登记，否则优雅地返回空」（`README.md:110,156`） | 代码里没有登记相关的处理；OAI-PMH 报错或请求失败都只打日志、返回空列表 | `paper_search_mcp/academic_platforms/oaipmh.py:121-127,162-169` |
| 「LLM 友好：标准化、去重、尽量完整」（`README.md:44`） | 去重只到 DOI 级，不合并字段；`extra` 序列化成 Python repr；未知的引用数写 0 | 见 [1.2](#12-统一与去重) |
| 「抽取文本」（`README.md:38`） | 本地抽取全仓只用 pypdf `extract_text()`，没有 OCR、版面、公式、表格处理；有的 `read_*` 在文前加题目作者头、按页加分隔线，有的直接拼接；CORE 先返回 CORE 接口里超过 500 字的 `fullText`；CiteSeerX 有摘要就只返回摘要 | `paper_search_mcp/academic_platforms/arxiv.py:188-196`、`paper_search_mcp/academic_platforms/iacr.py:261-289`、`paper_search_mcp/academic_platforms/semantic.py:451-479`、`paper_search_mcp/academic_platforms/pmc.py:355-369`、`paper_search_mcp/academic_platforms/core.py:391-398`、`paper_search_mcp/academic_platforms/citeseerx.py:367-369` |
| 引文图谱（`README.md:571`，未勾选） | 与 README 一致：没有；`references` 字段没有连接器填 | `paper_search_mcp/paper.py:28` |
| 可扩展（`README.md:69`） | 有 `PaperSource` 抽象基类，但加一个源要改 `paper_search_mcp/server.py` 至少四处（实例、`ALL_SOURCES`、每源的 `@mcp.tool` 函数、`search_papers` 的 if 链；要进兜底链还得加 `primary_downloaders`），再加 `paper_search_mcp/cli.py` 两处 | `paper_search_mcp/academic_platforms/base.py:7-54`、`paper_search_mcp/server.py:90-111,145-167,566-614,1099-1116`、`paper_search_mcp/cli.py:42-87` |

**出错时三种表现，只有第一种会进 `search_papers` 的 `errors`**：

| 表现 | 连接器 | 证据 |
|---|---|---|
| 抛异常 → 进 `errors` | Semantic Scholar（2026-09-20 合并的 PR #115 改的，它取代了未合并的 #111）、PubMed（请求与 XML 解析外面没有 try）、arXiv（重试用尽仍被限流时）、bioRxiv（日期区间起止颠倒时）、IEEE / ACM；另外单源超时与线程池占满也会进 `errors` | `paper_search_mcp/academic_platforms/semantic.py:323-345`、`paper_search_mcp/academic_platforms/pubmed.py:24-44`、`paper_search_mcp/academic_platforms/arxiv.py:87-100`、`paper_search_mcp/academic_platforms/biorxiv.py:50-51`、`paper_search_mcp/server.py:69-72,128-142`[^pr115] |
| 吞掉异常、打日志、返回空列表 → 看起来是「0 条结果」 | 其余 18 个源：Crossref、OpenAlex、OpenAIRE、PMC、CORE、Europe PMC、Zenodo、IACR、bioRxiv（请求失败）、medRxiv、dblp、CiteSeerX、DOAJ、BASE、HAL、SSRN、Unpaywall、Google Scholar（验证码页、异常、20 秒超时）；arXiv 的非 200 与重试用尽的网络错误也走这一路 | `paper_search_mcp/academic_platforms/crossref.py:97-102`、`paper_search_mcp/academic_platforms/openalex.py:93-95,180-181`、`paper_search_mcp/academic_platforms/openaire.py:296-297,318-319`、`paper_search_mcp/academic_platforms/pmc.py:94-99`、`paper_search_mcp/academic_platforms/core.py:148-157`、`paper_search_mcp/academic_platforms/europepmc.py:88-91`、`paper_search_mcp/academic_platforms/zenodo.py:102-104`、`paper_search_mcp/academic_platforms/iacr.py:195-196`、`paper_search_mcp/academic_platforms/biorxiv.py:65-84`、`paper_search_mcp/academic_platforms/medrxiv.py:75-80`、`paper_search_mcp/academic_platforms/dblp.py:115-125,205-206`、`paper_search_mcp/academic_platforms/citeseerx.py:141-150`、`paper_search_mcp/academic_platforms/doaj.py:137-146`、`paper_search_mcp/academic_platforms/oaipmh.py:162-167`、`paper_search_mcp/academic_platforms/hal.py:109-111`、`paper_search_mcp/academic_platforms/ssrn.py:87-92`、`paper_search_mcp/academic_platforms/unpaywall.py:173-178,202-206`、`paper_search_mcp/academic_platforms/arxiv.py:127-128`、`paper_search_mcp/academic_platforms/google_scholar.py:247-253,271-273`、`paper_search_mcp/server.py:743-749` |
| 返回错误字符串当结果 | IACR、Semantic Scholar、HAL、SSRN、Zenodo 的下载与读；PMC、CORE 的读；`read_arxiv_paper` 等出错返回空串 | `paper_search_mcp/academic_platforms/iacr.py:223-227`、`paper_search_mcp/academic_platforms/semantic.py:395,411`、`paper_search_mcp/academic_platforms/hal.py:153-154`、`paper_search_mcp/academic_platforms/zenodo.py:128-159`、`paper_search_mcp/academic_platforms/pmc.py:371-374`、`paper_search_mcp/academic_platforms/core.py:420-423`、`paper_search_mcp/server.py:848-852` |

arXiv 的「静默返回 0 条」还有一条 2026-09-25 新开的 issue #121 没修[^i121]。另外 arXiv、bioRxiv、medRxiv 的连接器和 `paper_search_mcp/server.py` 里共有 14 处 `print()` 写到 stdout（不算 `if __name__ == "__main__"` 块，例如 `paper_search_mcp/academic_platforms/medrxiv.py:80` 在正常重试时打印 `Attempt 1 failed, retrying...`，`paper_search_mcp/academic_platforms/arxiv.py:160`、`paper_search_mcp/server.py:851`）：stdio 模式下 stdout 是 MCP 协议通道，命令行下 stdout 是要被解析的 JSON。按代码推断这两处都会混进非 JSON 行，未实测。

## 2. 怎么做

### 2.1 入口与启动

1. 导入包时先执行 `load_env_file()`：读 `PAPER_SEARCH_MCP_ENV_FILE` 指的文件，缺省 `~/.config/paper-search-mcp/.env`，用 `os.environ.setdefault` 写入，不覆盖已有环境变量（`paper_search_mcp/__init__.py:1-3`、`paper_search_mcp/config.py:14-67`）。取值时先查 `PAPER_SEARCH_MCP_<NAME>`，再查不带前缀的旧名；带前缀的变量只要存在，哪怕是空串也会遮住旧名（`paper_search_mcp/config.py:70-82`）。
2. `paper_search_mcp/server.py` 在模块导入时就实例化 22 个连接器对象（21 个源 + Unpaywall 解析器，`paper_search_mcp/server.py:90-111`）；CORE 缺 key、DOAJ 缺 key、Unpaywall 缺 email 会在这时打警告（`paper_search_mcp/academic_platforms/core.py:37-40`、`paper_search_mcp/academic_platforms/doaj.py:44-52`、`paper_search_mcp/academic_platforms/unpaywall.py:28-33`）。IEEE / ACM 视 key 有无决定是否 import 与注册（`paper_search_mcp/server.py:175-192,1655-1731`）。
3. `main()` 按 `--transport` 起 FastMCP（官方 `mcp` SDK 里的 `mcp.server.fastmcp`）；stdio 下多起一个守护线程，父进程换了就 `os._exit(0)`（`paper_search_mcp/server.py:1774-1803,1863-1888`）。
4. 命令行 `cli.main()` 在第一次执行子命令时才实例化连接器（`paper_search_mcp/cli.py:42-79`）；`paper_search_mcp/cli.py` 不 import `server` 与 `mcp`。

### 2.2 统一检索的主流程

下面右列的路径都在 `paper_search_mcp/server.py` 里：

```
search_papers(query, max_results_per_source=5, sources="all", year="")
  │
  ├─ _parse_sources / _invalid_sources：拆逗号，未知源名记进 errors          195-209,547-563
  ├─ 按源名 if 链造协程：每个源调自己的 search_* 工具函数                     565-614
  │     └─ async_search → 有界线程池（32 槽，满了抛 SearchExecutorSaturatedError）
  │                      → 连接器 .search()（同步 requests）→ Paper.to_dict()  57-87,117-125
  ├─ asyncio.gather(每源套 45 s 超时, return_exceptions=True)                 128-142,616-623
  ├─ 异常 → errors[源]；否则补 source 字段、拼进 merged                        628-638
  ├─ _dedupe_papers(merged)                                                   640
  └─ 返回 {query, sources_requested, sources_used, source_results, errors, papers, total, raw_total}
```

三个细节：

- Google Scholar 在统一检索里也走它自己的工具函数，那里另有 20 秒超时，超时返回空列表而不是异常，所以不会进 `errors`（`paper_search_mcp/server.py:722-750`）。
- IACR 在统一检索里强制 `fetch_details=False`，命令行里用缺省的 `True`，每条结果多抓一次详情页（`paper_search_mcp/server.py:577-578`、`paper_search_mcp/academic_platforms/iacr.py:142-143`）；`search_iacr` 用的是 `asyncio.to_thread`，不经过 32 槽的有界线程池（`paper_search_mcp/server.py:766`）。
- 45 秒超时只是不再等这个源，线程本身不会被打断，槽位要等它自己返回才释放（`paper_search_mcp/server.py:57-87`，这是 PR #116 有意的设计[^pr116]）。BASE 翻页没有上限，一个很少命中的关键词会让它一直翻下去，期间占着一个槽（按代码推断，未实测）。

### 2.3 下载与读

- 分源下载：各连接器自己拼 PDF URL、写 `save_path`（缺省 `./downloads`，相对服务进程的工作目录），文件名各源各样（`{id}.pdf`、`iacr_{id}.pdf`、`semantic_{id}.pdf`、`core_{id}_{题目}.pdf`，Sci-Hub 是 `{md5前8位}_{名}.pdf` 等）。
- 兜底下载：见 [1.3](#13-下载兜底链与-sci-hub)。只有兜底这一路用 httpx 异步下载，其余都是同步 requests。
- 读：arXiv、bioRxiv、medRxiv、Semantic Scholar 先看 `save_path` 下有没有同名 PDF，没有才下载；其余源每次都重新下载。然后 pypdf 逐页 `extract_text()` 拼起来返回（`paper_search_mcp/academic_platforms/arxiv.py:172-199` 是最简的一版）。

### 2.4 怎么调模型

不调。全仓 grep 不到 openai、anthropic、embedding、litellm 或 MCP sampling 的调用。「让模型用起来」的全部手段是：工具的 docstring 就是给宿主 agent 看的工具说明（例如 `paper_search_mcp/server.py:536-546`），以及 2026-09-22 合并的 PR #120 给每个工具加的 `readOnlyHint` / `destructiveHint` / `openWorldHint` 注解（`paper_search_mcp/server.py:529,770`）[^pr120]。选哪个源、要不要兜底、要不要开 Sci-Hub，都由宿主 agent（MCP 客户端，或读 SKILL.md 的 Claude Code）决定。

### 2.5 数据进出

- 进：查询串、各源的 id / DOI / 题目、`save_path`；密钥只从环境变量与 `.env` 文件读，不收参数。
- 出：检索是 dict 列表（全是字符串和整数）；下载是一个路径字符串或一段错误说明；读是一整段纯文本。唯一写盘的是 PDF，检索不落任何文件，没有缓存。

## 3. 为什么

### 3.1 设计选择与它要解决的问题

| 设计 | 要解决什么 | 代码 | 来源 |
|---|---|---|---|
| 免费源优先，key 只做增强；key 被拒就退回无 key 请求 | 没有任何 key 也能用；作者在 README 里写成四条原则 | `paper_search_mcp/academic_platforms/semantic.py:182-192`、`paper_search_mcp/academic_platforms/core.py:100-114` | `README.md:40-45` |
| 两层：一个统一检索 + 每源一套工具 | 模型大多数时候只需要一个入口；分源工具保留源的专有参数 | `paper_search_mcp/server.py:529-651` | `README.md:59-61` |
| 同步连接器放进有界线程池、每源单独超时 | 一个源卡死不拖垮整次检索，超时的线程也不会占满 asyncio 默认线程池 | `paper_search_mcp/server.py:53-87,128-142` | PR #116[^pr116] |
| 工具参数一律用空串缺省、不用可空类型 | Gemini CLI 碰到这个服务整个会话报 400（issue #26），PR #116 把它归因到可空 schema | `paper_search_mcp/server.py:534,987-989` | PR #116[^pr116] |
| 兜底 PDF 查文件头 + 前三页身份 | 兜底链曾把一篇讲太阳能电池化学的 PDF 当成一篇头痛医学论文返回，贡献者称之为「phantom paper」，模型会拿它引错。PR 原稿的阈值是题目词 40%、词长 > 4，合并版是 60%、词长 ≥ 4 | `paper_search_mcp/server.py:319-429,490-504` | PR #93[^pr93] |
| Crossref 过滤 peer-review、figure 等类型，但**保留** dataset、report、standard | PR #93 原稿的黑名单还有 review、dataset、report、standard、standard-series；合并版只剩 5 种，注释写明其余仍是可引用的研究产出 | `paper_search_mcp/academic_platforms/crossref.py:20-31` | PR #93[^pr93] |
| Sci-Hub 改成显式开启 | 代码与 README 矛盾；issue 提出者说很多校园网与公司网络监控或封锁 sci-hub，缺省开会让用户在不知情时连上去 | `paper_search_mcp/server.py:1081` | issue #103[^i103] |
| arXiv 进程内每 3 秒一次、单连接 | arXiv API 使用条款要求「不超过每三秒一次请求，同一时间只开一个连接」[^arxiv-tou] | `paper_search_mcp/academic_platforms/arxiv.py:18-102` | PR #119[^pr119] |
| stdio 守护线程盯父进程 | 客户端异常退出后服务进程被 init 收养一直活着，报告者机器上攒了 9 个、最老的跑了一天多 | `paper_search_mcp/server.py:1774-1803` | PR #114[^pr114] |
| 加 streamable-http 传输 | stdio 每个客户端一个进程，多个 agent 会话时进程成倍增加 | `paper_search_mcp/server.py:1835-1888` | PR #114[^pr114] |
| `mcp` 钉在 `<2` | mcp 2.x 把 FastMCP 改名为 MCPServer，`uvx paper-search-mcp` 导入即崩 | `pyproject.toml:38` | issue #107[^i107]、PR #115[^pr115] |
| 加命令行与 skill | 2026-04 社区贡献（提交 5e4584a、cd9e431），给不想配 MCP 的 Claude Code 用户一条路 | `paper_search_mcp/cli.py`、`claude-code/SKILL.md` | `README.md:211-241` |

### 3.2 作者踩过的坑

仓里没有 CHANGELOG，坑都在 issue 与 PR 里[^issues]：

| issue / PR | 现象 | 现状 |
|---|---|---|
| #5（2025-04） | bioRxiv 端点用错，「返回永远是空」[^i5] | 2026-09-20 PR #116 按四种查询模式重写（`paper_search_mcp/academic_platforms/biorxiv.py:36-63`）；medRxiv 没跟着改 |
| #4、#74 | Google Scholar 返回空；同一会话约 10 次查询后被限流，直到重启服务[^i4][^i74] | #4 在 #115（consent 页处理）与 #116（限时）合并后关闭；#74 开着。#74 说「会话开始时选一个 UA」，但 main 与 v0.1.4 都是每次请求换 UA[^gs014]，没变的是整个进程共用一个 Session 与出口 IP（`paper_search_mcp/academic_platforms/google_scholar.py:33-54,184`） |
| #101 | arXiv 用 HTTP 端点、多词查询不加引号时，后端会卡住 | 已修（`paper_search_mcp/academic_platforms/arxiv.py:27,104-116`） |
| #121（2026-09-25） | arXiv 偶发 HTTP 406（有时响应体里还带着正常的 Atom 结果），连接器当成 0 条，没有任何错误[^i121] | 开着 |
| #46、#64、#82 | PyPI 的包缺命令行入口，`uv tool install` / uvx 失败 | 0.1.4（2026-07-02）修复，CI 加了入口检查（`.github/workflows/publish.yml:47-49`） |
| #103 | 兜底链缺省走 Sci-Hub，与 README 矛盾 | main 已改；PyPI 未发 |
| #107 | mcp 2.x 下启动崩溃 | main 已钉版本；PyPI 0.1.4 依赖写的是 `mcp[cli]>=1.6.0`、没有上限[^pypi]，而 PyPI 上 mcp 2.0.0 已于 2026-07-28 发布、最新 2.2.0[^pypi-mcp]；issue 里给的变通是 `uvx --with "mcp<2" paper-search-mcp`[^i107] |
| #26 | Gemini CLI 下整个 agent 不可用 | 已修（不可空 schema） |
| #57、#68、#69、#109 | 兜底链遇到非字符串 paper_id 崩溃；Semantic Scholar 某些字段为 None 时报 `'NoneType' object has no attribute 'strip'`、那一条被静默丢掉；Zenodo 的字符串日期让解析崩溃；Zenodo / HAL 的作者名被逐字符拆开 | 已修 |
| #93 | 兜底链下回错误论文 | 已修（身份校验） |
| #77 | 命令行和 MCP 接口不一致，提议抽一层共用 API | 开着，PR #78 未合 |

维护方式：2026-09-20 的 PR #115、#116 把别人的 10 个和 4 个 PR（其中 6 个由 Copilot 机器人提交）合在一起重做后合并，原 PR 在 GitHub 上是关闭、未合并（原提交另经一次保留代码树的合并挂进了 main 的历史，`docs/CONTRIBUTION_PROVENANCE.md:26-29`）；作者为此单独写了 `docs/CONTRIBUTION_PROVENANCE.md` 记署名来源（`docs/CONTRIBUTION_PROVENANCE.md:1-41`、`CONTRIBUTING.md:16-45`）[^pr115][^pr116]。2026-03-16 一个提交一次加了 16 个源、58 个文件、9852 行[^mega]。

## 4. 跑起来要什么

| 项 | 实况 | 证据 |
|---|---|---|
| Python | `>=3.10`；CI 在 3.10、3.12、3.13 上测 | `pyproject.toml:11`、`.github/workflows/publish.yml:13` |
| 运行依赖 | requests、feedparser、fastmcp、pypdf、`mcp[cli]>=1.8.0,<2`、beautifulsoup4、lxml、`httpx[socks]`；其中 **fastmcp 与 lxml 在包代码里没有被 import**（MCP 用的是官方 SDK 里的 `mcp.server.fastmcp`，BeautifulSoup 全部用 `html.parser`） | `pyproject.toml:33-42`、`paper_search_mcp/server.py:19` |
| 锁定版本 | `uv.lock` 共 90 个包（含 dev）；mcp 1.26.0、fastmcp 3.1.1、pypdf 6.9.2、requests 2.32.5、httpx 0.28.1 | `uv.lock` |
| 从 PyPI 装的版本 | 0.1.4，`mcp[cli]>=1.6.0` 没有上限；按 #107 与 PyPI 元数据推断，今天解析会拿到 mcp 2.x，MCP 服务导入即崩；命令行不 import mcp，不受这一条影响。未实跑 | [^pypi][^pypi-mcp][^i107] |
| 模型与模型 key | 不需要 | 见 [2.4](#24-怎么调模型) |
| 必须的配置 | 没有；唯一「不配就少一环」的是 Unpaywall 的 email（不配则 Unpaywall 源与兜底链第 3 环跳过） | `paper_search_mcp/academic_platforms/unpaywall.py:19-33` |
| 可选的 key | 都是数据源的 key，不是模型的：Semantic Scholar、OpenAlex（key 与 email）、CORE、DOAJ、Zenodo、OpenAIRE、CiteSeerX；Google Scholar 的代理 URL；IEEE / ACM 的 key 只让工具注册、不带来功能 | `paper_search_mcp/config.py:70-82`、`.env.example:12-26` |
| 写死的联系方式 | Crossref 的 `mailto=paper-search@example.org`；PMC、arXiv、CORE、Europe PMC 的 UA 或请求参数里的 `openags@example.com`；OpenAlex 缺省 email `openags@example.com`。除 OpenAlex 外都不可配置 | `paper_search_mcp/academic_platforms/crossref.py:18,69`、`paper_search_mcp/academic_platforms/pmc.py:30,55-56`、`paper_search_mcp/academic_platforms/arxiv.py:42`、`paper_search_mcp/academic_platforms/core.py:34`、`paper_search_mcp/academic_platforms/europepmc.py:23`、`paper_search_mcp/academic_platforms/openalex.py:18,29-31` |
| 外部服务 | 上表 21 个源的站点，加可选的 Sci-Hub 镜像；README 说 BASE 要机构 IP 登记；Google Scholar、SSRN 有反爬 | 见 [1.1](#11-源清单) |
| 网络 | 运行时必须联网；Google Scholar 可单独配代理。bioRxiv、medRxiv 的 Session 把 `proxies` 设成 None，意图是不走代理，但按 requests 的合并规则（请求级代理先吸收环境变量里的代理，再与会话级合并，会话里值为 None 的键被请求级覆盖），环境变量里的 HTTP(S)_PROXY 仍会生效；这是读本机另一个 venv 里 requests 2.34.2 的 `sessions.py` 得出的推断，锁定的 2.32.5 没逐行对，未实测 | `paper_search_mcp/academic_platforms/biorxiv.py:28`、`paper_search_mcp/academic_platforms/medrxiv.py:15`、`paper_search_mcp/academic_platforms/google_scholar.py:47-51` |
| 算力 | 纯 CPU，无 GPU；最重的是 pypdf 抽文字 | — |
| 操作系统 | 纯 Python；stdio 守护线程对 Windows 单独用 `WaitForSingleObject`；README 自述 macOS 上 uvx 生成的包装脚本依赖 `realpath` | `paper_search_mcp/server.py:1734-1771,1785-1793`、`README.md:271` |
| 分发 | PyPI（`uvx` / `uv tool install` / pip，装到 0.1.4）、Smithery（版本没查）、Dockerfile 与 clone 源码（装到当前代码；Dockerfile 只拷了 `paper-search-mcp`，没拷 `paper-search` 命令行） | `README.md:252-488`、`Dockerfile:1-16`、`smithery.yaml:1-43` |

## 5. 和平台对照

只列事实，不下接不接的结论。同一轮另一个 MCP 形态的文献候选见 [arxiv-mcp-server.md](arxiv-mcp-server.md)。

### 5.1 平台的文献阶段现在有什么

| 项 | 实况 | 证据 |
|---|---|---|
| 步骤能力 | 文献、假设、写作三个阶段都还没有 | `platform/framework/capabilities/__init__.py:43` |
| 阶段主文件 | 文献是 `sources.md`，由助理手写（`ai4sci output new literature`），不是能力产的 | `platform/framework/capabilities/__init__.py:45-47`、纲领 P-1 / P-24 |
| 挂在文献格上的 skill | 复现流程挂 `pdf`、`download` 两个；研究流程不经过文献阶段 | `platform/workflows/reproduce.yaml:10`、`platform/workflows/research.yaml:8-14` |
| 检索 | 用 CLI 自带的联网工具：Claude Code 放行 WebSearch / WebFetch，Codex 开 `web_search="live"` | `platform/backends/claude_code.py:40-42`、`platform/backends/codex.py:114` |
| 读论文 | `pdf` skill：pymupdf4llm 版面模式，出 `paper.md` + `images/` + `structured.json`（分节、表格、图注、参考文献）；`--input` 也收 http(s) 链接，原件存成 `source.pdf`；同样不做 OCR | `platform/skills/pdf/SKILL.md:1-46,55` |
| 拉材料 | `download` skill：git 仓库、单个文件（可校验 sha256）、Hugging Face；留收据；不搜索、没有按 DOI 找 PDF 的子命令 | `platform/skills/download/SKILL.md:1-35` |

### 5.2 它多了什么、重叠什么

| | paper-search-mcp | 平台现有 | 关系 |
|---|---|---|---|
| 学术检索 | 21 个源的结构化结果：DOI、作者、日期、引用数（4 个源）、`pdf_url`；DOI 去重 | CLI 自带网页搜索，结果是网页，不是结构化条目 | 它多出来的 |
| DOI → 开放获取 PDF | Unpaywall 解析 + 4 个仓储兜底 + 身份校验 | 没有；`download file` 与 `pdf --input` 都要给直链 | 它多出来的 |
| 分源 PDF 下载 | arXiv、bioRxiv、PMC 等按 id 下载 | `download file <url>` 按直链下载，带 sha256 与收据 | 重叠，形状不同 |
| 抽全文 | pypdf 纯文本 | `pdf` skill：markdown + 图 + 结构化 JSON | 重叠，平台这边更细 |
| 引文图谱、全文检索、摘要 | 没有 | 没有 | 都没有 |

### 5.3 接进来会碰到的平台规则

| 规则 | 平台的写法 | paper-search-mcp 的现状 | 证据 |
|---|---|---|---|
| P-1 框架不调模型 | `framework/` 下 grep 不到模型 API 名 | 它自己也不调模型，这一条不冲突 | 见 [2.4](#24-怎么调模型) |
| P-14 命令只有 `ai4sci` | 研究助理放行前缀 `ai4sci`，执行层只放行 `ai4sci skill`；Claude Code 侧按命令文本前缀匹配，Codex 侧没有按命令的白名单，`ai4sci` 以外的命令在沙箱里跑、没有网络；联网只用 CLI 自带的搜索与网页读取工具 | 它自带的 skill 教 agent 直接敲 `paper-search ...`，不在放行前缀里，在 Codex 沙箱里也连不了网；它本身是一个自己联网的检索工具 | `platform/framework/chat/guide.py:23-28`、`platform/framework/skills/__init__.py:37`、`platform/backends/codex.py:127-141` |
| MCP 形态 | 两家适配器起会话时都清空 MCP：Claude Code 带 `--strict-mcp-config`，Codex 写 `mcp_servers={}` | MCP 形态在平台现有会话里加载不进来 | `platform/backends/claude_code.py:8,39`、`platform/backends/codex.py:118` |
| P-22 skill 格式与加载 | agentskills.io 的 `SKILL.md` + `scripts/`；脚本 PEP 723 自带依赖、锁文件进仓、`uv run --locked --offline` 起；加载不靠 agent 原生机制：Claude Code 带 `--disable-slash-commands` 清空原生 skill，Codex 逐个关掉原生 skill 目录 | 自带的 `SKILL.md` frontmatter 只有 name / description（在规范字段内），但没有 `scripts/`，靠全局 `uv tool install` 装的命令行，靠 Claude Code 原生的 `~/.claude/skills/` 目录加载 | `platform/framework/skills/run.py:21`、`platform/backends/claude_code.py:8`、`platform/backends/codex.py:27-28,123-126`、`claude-code/SKILL.md:1-17`、`README.md:217-229` |
| skill 脚本约定 | 结果 JSON 一行到 stdout，诊断到 stderr；退出码 0 成、非 0 败 | 命令行 `search` 输出缩进的多行 JSON，`read` 输出纯文本；全部源失败也退 0；下载失败时打印 `"status":"ok"`；连接器还有 14 处 `print()` 往 stdout 写 | `platform/docs/add-a-skill.md:55`、`paper_search_mcp/cli.py:135-215`、见 [1.5](#15-readme-说了代码里没有或很薄) |
| P-22 运行时联网 | `--offline` 只管 uv 不去取包；`download` skill 运行时照样联网（git clone、urllib）；Codex 下 `ai4sci` 命令在沙箱外跑、能联网 | 它运行时要连 20 多个外部站点 | `platform/framework/skills/run.py:6-7`、`platform/skills/download/scripts/fetch.py:87,112`、`platform/backends/codex.py:130,140` |
| 作为 PEP 723 依赖 | 依赖写进脚本头、锁进仓 | PyPI 上最新 0.1.4 比 main 落后 39 个提交（缺身份校验、Sci-Hub 缺省关、每源超时、mcp 版本上限）；导入 `paper_search_mcp` 包会执行 `load_env_file()` 读 `~/.config/paper-search-mcp/.env`；只用连接器也会连带装上 mcp、fastmcp 等全部依赖 | `paper_search_mcp/__init__.py:1-3`、`paper_search_mcp/config.py:14-20`、`pyproject.toml:33-42`[^gh-tags] |
| P-20 接法 | 文献主文件 `sources.md`；skill 不开产出目录，写哪里由调用方定 | `search` 只往 stdout 出 JSON、不落盘；`download` / `read` 写到 `-o`（命令行）或 `save_path`（MCP，缺省 `./downloads`）；检索结果 JSON 与 `sources.md` 之间没有现成的对应 | `paper_search_mcp/cli.py:244-254`、`paper_search_mcp/server.py:771` |
| P-7 fail-closed、未知写 NaN | 验证不过就停；未知的值写 NaN 不写 0；不许吞异常 | 21 个源里 18 个把请求失败吞掉、返回空列表；引用数缺省 0、Google Scholar 恒 0；IACR 日期缺失填 1900-01-01、Crossref 填 1970-01-01；源自带下载不查 PDF 头 | 见 [1.5](#15-readme-说了代码里没有或很薄) |
| 密钥与配置位置 | 按人的配置在 `~/.config/ai4sci/`；密钥读环境变量、不进 argv（`download` skill 的 HF_TOKEN 同理） | 密钥读 `PAPER_SEARCH_MCP_*` 环境变量或 `~/.config/paper-search-mcp/.env`，不收参数 | `paper_search_mcp/config.py:14-20,70-82`、`platform/skills/download/SKILL.md:31` |
| Sci-Hub | 平台没有相关规定 | 命令行 / skill 形态里不存在；MCP 形态里 `download_scihub` 常驻 | 见 [1.3](#13-下载兜底链与-sci-hub) |

## 6. 成熟度

| 项 | 实况 | 证据 |
|---|---|---|
| 仓库 | openags/paper-search-mcp，2025-04-06 建，2706 star、281 fork，MIT | [^gh-meta] |
| 规模 | 包代码 10,928 行，其中连接器 8,584 行；`paper_search_mcp/server.py` 1,892 行；测试 4,968 行 | `wc -l` |
| 测试 | `tests/` 下 32 个 `test_*.py` 加 2 个手动脚本，共 219 个测试函数；17 个文件用了 mock / patch；其余多数直接打真接口，接口不通就 `skipTest`，离线跑会被跳过而不是失败；PMC、CORE、Europe PMC 没有测试文件；CiteSeerX 的测试不碰下载 | `tests/test_crossref.py:6-31`、`tests/test_citeseerx.py` |
| CI | 只有一个工作流 `publish.yml`，**只在推 `v*.*.*` tag 时触发**，跑 7 个它称为 deterministic 的测试文件、`compileall`、打包、检查 wheel 入口，再发 PyPI；PR 与 push 上没有 CI；不跑 lint，`compileall` 查不出 CiteSeerX 那种未定义名字；614 行、用 mock 的 `test_fallback.py` 不在这 7 个里 | `.github/workflows/publish.yml:1-77` |
| 发版 | 5 个 tag，没有 GitHub Release；PyPI 0.1.0、0.1.2（2025-04-06）、0.1.3（2025-04-29）、0.1.4（2026-07-02）；`pyproject.toml` 仍是 0.1.4，main 比 v0.1.4 多 39 个提交、37 个文件 | `pyproject.toml:7`[^gh-tags][^pypi] |
| 维护节奏 | main 上 87 个提交：2025-04 集中 18 个，2025-09 到 2026-02 零提交，2026-03 起恢复，2026-09 一个月 28 个；作者 universea 占 51 个；截至 2026-09-27 开着 13 个 issue、18 个 PR | [^commits][^issues] |
| 变更记录 | 没有 CHANGELOG；变更只能从 PR 描述里看 | 仓库根目录 |
| 许可证 | MIT，`Copyright (c) 2025 OPENAGS`：可商用、可改、可再分发，要保留版权与许可声明，无担保。许可证只管代码本身；Sci-Hub 的法律风险 README 自己标了「用户自负」，Google Scholar、SSRN 的抓取是否合各站条款，许可证不涉及 | `LICENSE:1-21`、`README.md:193-201`、`paper_search_mcp/academic_platforms/ssrn.py:6-13` |

## 7. 还没弄清的问题

1. **在我们的网络里各源实际通不通。** 21 个源从校园网 / 家庭网络出去的可达性、延迟、Google Scholar 验证码触发频率、Sci-Hub 与 SSRN 是否被墙或被拦，都要 #169 实测。
2. **`print()` 写进 stdout 的实际后果。** stdio 模式的 MCP 客户端与命令行 JSON 输出会不会被这 14 处打印弄坏，只是读代码推断。
3. **去重在真实查询上的效果。** 各源 DOI 的覆盖率多高、跨源重复有多少条被漏掉，要拿一批查询统计。
4. **身份校验的误拒率。** 阈值 60% 的词命中、只看前三页、词长 ≥ 4：中文题目在 `[^\W_]+` 下会成为一两个长词，大概率匹配不上；图片型 PDF 一律拒。这些都没实测。
5. **bioRxiv、medRxiv 在统一检索里拿到关键词时 API 返回什么。** 关键词被当成分类名传上去，接口返回空还是返回近 30 天全部，没验证。
6. **PMC 的 PDF 直链现在还能不能直接下。** README 说部分代理环境会被拦，NCBI 那边的现状没查。
7. **BASE 的机构 IP 登记。** README 说要登记，代码里看不出来；天大的出口 IP 有没有登记、登记流程要多久，不知道。
8. **main 什么时候发到 PyPI。** 维护者没有固定发版节奏，0.1.3 到 0.1.4 隔了 14 个月。
9. **今天从 PyPI 装 0.1.4 实际解析出什么。** mcp 2.x 导入即崩是按 #107 与 PyPI 元数据推断的，没实跑。
10. **bioRxiv、medRxiv 在有 HTTP(S)_PROXY 的环境里走不走代理。** 代码意图是不走，按 requests 的合并规则推断会走，没实测。
11. **Semantic Scholar、OpenAlex、CORE 不带 key 时的限额。** README 只说「会被限流」，具体数字没查官方文档。
12. **DOAJ 认不认 `query` 参数。** 连接器把带过滤条件的 Lucene 串放在 `query` 参数里，DOAJ 接口文档里有没有这个参数，没查。
13. **Google Scholar 与 SSRN 的抓取在各站条款下是否允许**、Sci-Hub 在国内使用的合规边界，没有评估。
14. **`paper_id=f"gs_{hash(url)}"`** 用的是 Python 的 `hash()`，字符串的 hash 默认每个进程加随机盐[^py-hash]，同一个 Google Scholar 结果在两次运行里 id 不同；dblp 的 HTML 兜底同样用 `hash(title)` 生成 id（`paper_search_mcp/academic_platforms/dblp.py:177`）。这对下游用 id 回查有没有实际影响，取决于怎么用，没评估。
15. **#77 / PR #78 的走向。** 如果维护者合并「共用 API」重构，命令行可能获得兜底链；现在不知道。

## 8. 调研方法

- 浅克隆到外层 `vendor/paper-search-mcp`（gitignore 挡住），只读代码，没装依赖、没跑项目代码。执行过的只有两段用 Python `ast` 解析源码的脚本（不 import 项目）：一段统计 `if __name__ == "__main__"` 块之外的 `print()` 位置，一段找模块里没有绑定就被读取的名字（找到 `paper_search_mcp/academic_platforms/citeseerx.py` 的 `os`）。
- 提交历史、tag、issue、PR 经 `gh api` 查（本地是浅克隆，git log 只有一个提交）；v0.1.4 的 `paper_search_mcp/server.py` 与 `paper_search_mcp/academic_platforms/google_scholar.py` 经 GitHub contents API 取来比对，存在外层 `materials/research/2026-0927-scientific-ai-capabilities/psm-check/`（gitignore）；PyPI 上 paper-search-mcp、mcp、fastmcp 的版本与依赖经 `pypi.org/pypi/<包>/json` 查。
- requests 的代理合并规则读的是本机另一个项目 venv 里的 requests 2.34.2 源码，不是本仓锁定的 2.32.5。
- 平台一侧读了纲领 P-1、P-7、P-11、P-14、P-18、P-20、P-22、P-23、P-24、P-25，内仓 `docs/add-a-skill.md`、`docs/add-a-capability.md`、`skills/pdf`、`skills/download`、`framework/capabilities/__init__.py`、`framework/chat/guide.py`、`framework/skills/`、两家适配器。
- 这个项目没有论文，没有下载论文。

[^gh-meta]: GitHub API `repos/openags/paper-search-mcp`，2026-09-27 查：2706 star、281 fork、MIT、创建于 2025-04-06、最近推送 2026-09-22、未归档。<https://github.com/openags/paper-search-mcp>
[^gh-tags]: GitHub API `repos/openags/paper-search-mcp/tags`、`releases`、`compare/v0.1.4...main`，2026-09-27 查：tag v0.1.0–v0.1.4，Release 列表为空；main 比 v0.1.4 多 39 个提交、改动 37 个文件，含 `paper_search_mcp/server.py`、`paper_search_mcp/academic_platforms/arxiv.py`、`paper_search_mcp/academic_platforms/crossref.py`、`pyproject.toml`；`paper_search_mcp/cli.py` 与 `claude-code/SKILL.md` 不在改动里。
[^pypi]: <https://pypi.org/pypi/paper-search-mcp/json>，2026-09-27 查：最新 0.1.4，上传于 2026-07-02；该版本 `requires_dist` 为 `mcp[cli]>=1.6.0`，没有上限，`fastmcp` 也没有版本约束。
[^pypi-mcp]: <https://pypi.org/pypi/mcp/json> 与 <https://pypi.org/pypi/fastmcp/json>，2026-09-27 查：mcp 最新 2.2.0，2.0.0 上传于 2026-07-28；fastmcp 最新 4.0.10，`requires_dist` 里没有 mcp，不会把 mcp 压在 2 以下。
[^v014]: tag v0.1.4 的 `paper_search_mcp/server.py`（经 GitHub contents API 取得，共 1384 行）第 763 行：`use_scihub: bool = True,`；全文没有 `_pdf_matches_expected`、`_looks_like_pdf` 与每源超时。
[^gs014]: tag v0.1.4 的 `paper_search_mcp/academic_platforms/google_scholar.py`（经 GitHub contents API 取得）第 132 行已在每次请求前调用 `_rotate_user_agent()`。
[^commits]: GitHub API `repos/openags/paper-search-mcp/commits`（分页取全），2026-09-27 查：main 共 87 个提交；按月 2025-04 18、2025-06 5、2025-08 4、2026-03 3、2026-04 10、2026-05 8、2026-06 3、2026-07 5、2026-08 3、2026-09 28；universea 51 个。
[^issues]: GitHub API `repos/openags/paper-search-mcp/issues?state=all`，2026-09-27 查：issue 41 个（关 28、开 13），PR 80 个（关 62、开 18）。
[^i5]: issue #5「text search functionality of bioRxiv」，2025-04-25，由 PR #116 关闭。<https://github.com/openags/paper-search-mcp/issues/5>
[^i4]: issue #4「Google Scholar search can not work」，维护者 2026-09-20 关闭时注明 consent 页处理在 #115、限时在 #116，持续限流另见 #74。<https://github.com/openags/paper-search-mcp/issues/4>
[^i74]: issue #74「google_scholar: session-scoped rate-limit (~10 queries) blocks comprehensive surveys」，2026-05-14，开着。<https://github.com/openags/paper-search-mcp/issues/74>
[^i77]: issue #77「CLI does not provide same commands as MCP」，2026-05-19，开着；对应 PR #78。<https://github.com/openags/paper-search-mcp/issues/77>
[^i103]: issue #103「download_with_fallback defaults use_scihub=True, which contradicts the Sci-Hub Notice in the README」，2026-08-25，由 PR #115 关闭；正文另建议加 `PAPER_SEARCH_MCP_ENABLE_SCIHUB` 开关。<https://github.com/openags/paper-search-mcp/issues/103>
[^i107]: issue #107「Server crashes at startup under mcp 2.x: No module named 'mcp.server.fastmcp'」，2026-09-08，由 PR #115 关闭；正文给出 `uvx paper-search-mcp --help` 的报错与变通 `uvx --with "mcp<2" paper-search-mcp`。<https://github.com/openags/paper-search-mcp/issues/107>
[^i121]: issue #121「search_arxiv silently returns 0 results when the arXiv export API answers intermittent HTTP 406」，2026-09-25，开着，报告基于 main `808e462`。<https://github.com/openags/paper-search-mcp/issues/121>
[^pr93]: PR #93「fix: validate PDF content and filter phantom papers from fallback chain」，2026-07-07 提、2026-09-21 合并；描述里的复现：`download_with_fallback('europepmc', 'PMC10912660', ...)` 返回了一篇太阳能电池化学的 PDF；原稿阈值 40%、黑名单 10 种类型，维护者另加一个提交收紧。<https://github.com/openags/paper-search-mcp/pull/93>
[^pr114]: PR #114「Exit stdio server when its client dies; add optional streamable-http transport」，2026-09-21 合并。<https://github.com/openags/paper-search-mcp/pull/114>
[^pr115]: PR #115「fix: stabilize search, metadata, and safe fallbacks」，2026-09-20 合并，关闭 #69 #101 #103 #107 #109，取代 #50 #54 #62 #84 #104 #105 #110 #111 #112 #113（这 10 个都未合并）。<https://github.com/openags/paper-search-mcp/pull/115>
[^pr116]: PR #116「fix: improve MCP compatibility and search reliability」，2026-09-20 合并，关闭 #3 #5 #23 #26，取代 #49 #51 #53 #55；描述称安装后的 wheel 暴露 57 个 MCP 工具、0 个可空 schema，超时回归测试确认超时后槽位仍被占着、直到线程结束才释放。<https://github.com/openags/paper-search-mcp/pull/116>
[^pr119]: PR #119「fix(arxiv): serialize and surface rate-limit responses」，2026-09-22 合并。<https://github.com/openags/paper-search-mcp/pull/119>
[^pr120]: PR #120「feat(mcp): publish accurate tool annotations」，2026-09-22 合并，即本次克隆的 HEAD 808e462。<https://github.com/openags/paper-search-mcp/pull/120>
[^mega]: 提交 2a81648「update some search sources」，2026-03-16：58 个文件，+9852 / −565 行，新增 OpenAlex、PMC、CORE、Europe PMC、dblp、OpenAIRE、CiteSeerX、DOAJ、BASE、Zenodo、HAL、SSRN、Unpaywall、IEEE、ACM、ChemRxiv 连接器。<https://github.com/openags/paper-search-mcp/commit/2a81648>
[^arxiv-tou]: arXiv API Terms of Use：「make no more than one request every three seconds, and limit requests to a single connection at a time.」<https://info.arxiv.org/help/api/tou.html>
[^py-hash]: Python 文档 `object.__hash__`：str 与 bytes 的 hash 值默认加一个不可预测的随机盐，同一进程内不变，重复运行之间不可预测。<https://docs.python.org/3/reference/datamodel.html#object.__hash__>
