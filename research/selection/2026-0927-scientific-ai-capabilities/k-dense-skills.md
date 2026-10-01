---
title: K-Dense Scientific Agent Skills 代码级深读
subtitle: 科研 AI 能力选型 · 文献检索 · 166 个 skill 的格式、文献相关 skill 实际调了什么、和平台 P-22 差在哪
kind: 开源项目选型深读（只读代码，不跑、不装依赖）
date: 2026-09-27
scope: 仓库 https://github.com/K-Dense-AI/scientific-agent-skills，浅克隆到外层 vendor/scientific-agent-skills，提交 49c6e97（2026-09-21，比 v2.69.0 标签多 9 个提交）。深读 paper-lookup、research-lookup、literature-review、database-lookup、scientific-writing，citation-management 读到接口与 key 一层；其余 skill 只统计。论文 arXiv 2609.00065 读摘要、第 1、2、6、7 节与附录 D、E。文中 文件:行 均相对该仓库根；平台一侧的路径以 platform/ 或 docs/ 开头，相对外层仓库根
status: 第一版
---

> **结论先行**：它是 166 个按 agentskills.io 格式写的**说明文档包**，其中 106 个带脚本；仓库本身不调模型，干活的是装了它的宿主 agent（Claude Code、Codex 等）：读 `SKILL.md`，自己在 shell 里 `curl`、跑脚本。按它自己的分组，生物与组学 35 个、机器学习 18 个、临床与医学 12 个，文献检索与写作相关的十来个。
>
> **文献相关的四个，做法各不相同**。`paper-lookup` 是「18 个学术接口的调用手册 + 4 个只用标准库的解析与翻页脚本」：脚本只直连 bioRxiv/medRxiv、Europe PMC、OpenAlex、Crossref 这 5 个接口（4 个主机）的翻页，其余 13 家靠 agent 照 `references/*.md` 自己 `curl`；它比别处多出来的是：18 份手册里 12 份写了「HTTP 200 里藏着的失败」，翻页脚本按接口报的总数对账。李瑞彬原稿提到的 Research Lookup **存在**，名字就是 `research-lookup`，但它的脚本**不直连学术库**：缺省走 Parallel（parallel.ai 的检索服务，要装 `parallel-cli` 并登录），先把搜索限定在 25 个学术域名里，不够 60 条再补一次不限域名的；产出的证据矩阵、论断—来源映射、共识与冲突全是关键词与正则启发式，「60 篇已核实」里的「核实」包括「标题或摘录里正则到一个 DOI/PMID」。`literature-review` 的检索也是 `parallel-cli`，自带的 `search_databases.py` 不联网、只做去重排序，`verify_citations.py` 只查 DOI 能否解析；它的 `SKILL.md` 还要求每篇综述至少一张经 OpenRouter 生成的配图。`scientific-writing` 是另一种东西：纯本地、断网、零 key 的证据台账校验器，论断必须挂证据号，证据的 `status` 为 `verified` 且 `source_opened` 为 `true` 才算核实；这些字段是人填的还是 agent 填的，脚本分不出来。
>
> **和平台**：用平台自己的 `load_skill()` 逐个读，166 个里 22 个能过；文献相关的五个与 `scientific-writing` 全都不过（`allowed-tools` 字段、嵌套的 `metadata`、脚本没有 PEP 723 块和锁文件），能过的 22 个里与文献有关的只有 `paperzilla`、`bgpt-paper-search` 两个没有脚本的。平台的 `scan()` 遇到一个不过就整库报错，所以原样整包放进 `platform/skills/`，清单与 `ai4sci skill` 全都起不来。`paper-lookup` 的主流程是 agent 在 shell 里 `curl` 再管道给脚本：Claude Code 适配器的命令白名单里只有 `ai4sci` 前缀，Codex 适配器把 `ai4sci` 以外的命令留在断网的沙箱里。`research-lookup` 缺省路径就要 Parallel 账号（`parallel-cli` 登录或 `PARALLEL_API_KEY`），`literature-review` 的检索也走 `parallel-cli`、强制配图要 `OPENROUTER_API_KEY`；这些是研究者 agent 登录之外另一家服务的凭据，平台目前唯一读独立凭据的先例是 `download` 的 `HF_TOKEN`。
>
> **成熟度**：MIT，但 `pdf`、`docx`、`pptx`、`xlsx` 四个是 Anthropic 的专有条款，另有非商用许可的 skill。106 个带脚本的 skill 都有测试目录，CI 只跑其中 20 个纯标准库的（`paper-lookup`、`scientific-writing` 在内，`research-lookup`、`literature-review`、`citation-management` 不在）；规范校验与测试这两道 CI 是 2026-07 下旬才加的。11 个月 106 个自动 release，主力作者一人占 44% 提交。作者的论文明写「没有任务级评测」。
>
> 怎么读：七个问题各一节；第 1 节第 3 小节是 README 与代码的逐条对账，第 5 节是碰到平台哪些规则，第 7 节是还没弄清的。横向对比见同目录的 [README.md](README.md)，同类候选见 [arxiv-mcp-server.md](arxiv-mcp-server.md)、[paper-search-mcp.md](paper-search-mcp.md)。

## 0. 仓库画像

| 项 | 实况 | 证据 |
|---|---|---|
| 是什么 | 一个 Agent Plugins 包：根目录 `plugin.json` + `skills/` 下 166 个目录，每个目录一个 skill | `AGENTS.md:26-41`、`plugin.json:1-4` |
| 规模 | `skills/` 下 548 个 `.py` 共 17.1 万行、`.md` 共 34.6 万行；`tests/` 下 `.py` 5.2 万行 | 见第 8 节的统计命令 |
| 版本 | `pyproject.toml` 与 `plugin.json` 都是 2.69.0；README 徽章还是 2.68.0；HEAD 比 v2.69.0 标签多 9 个提交（多了 `alphagenome`），版本号没动所以没发版 | `pyproject.toml:3`、`README.md:5`、`.github/workflows/release.yml:3-9` |
| 作者 | K-Dense, Inc.；GitHub 贡献者 56 个账号，第一作者 Timothy Kassis 323 个提交，主干共 732 个 | [^gh-meta] |
| 热度 | 46,743 star、4,227 fork（2026-09-27 查）；仓库 2025-10-19 建 | [^gh-meta] |
| 论文 | Kassis 等，arXiv 2609.00065，描述 v2.65.0（163 个 skill）；自称资源论文，摘要与第 6 节写明没有任务级评测、没有宿主选中率；五位作者都是 K-Dense 现任或前任员工（第 7 节利益声明） | [^paper] |
| 前身 | 原名 Claude Scientific Skills，目录原叫 `scientific-skills/`；按路径查提交，`skills/` 下最早的是 2026-05-27 的 0936740「Update directory」 | `README.md:18`、[^i159] |

## 1. 是不是：README 说的能力在代码里对应哪段

### 1.1 一个 skill 在代码里是什么

| 层 | 仓库的规矩 | 实况（HEAD） | 证据 |
|---|---|---|---|
| 目录 | `SKILL.md` 必有，`references/` `scripts/` `assets/` 可选；测试不许放在 skill 目录里，放 `tests/<name>/` | 166 个都有 `SKILL.md`；157 个有 `references/`，106 个有 `scripts/`，34 个有 `assets/`；106 个 `tests/<name>/` 与 106 个带脚本的 skill 一一对应 | `AGENTS.md:34-53`、`tests/_meta/test_repo_contract.py:72-110` |
| frontmatter | 只许规范的六个顶层字段；`metadata.version` 必填且带引号；`metadata.openclaw` / `metadata.hermes` 必须是嵌套映射（为了 OpenClaw 读它做凭据注入） | 顶层字段合计：`name` `description` `metadata` 166、`license` 162、`compatibility` 119、`allowed-tools` 102；26 个带嵌套的 `openclaw` 块 | `AGENTS.md:113-177`、`.github/workflows/skill-spec-validation.yml:76-131` |
| 脚本依赖 | 仓库不要求脚本自带依赖声明；依赖写在 `SKILL.md` 正文（多数是 `uv pip install`）和测试用的 `tests/skill-requirements.toml` 里 | 548 个 `.py` 里只有 18 个（5 个 skill）带 PEP 723 块，**0 个锁文件**；107 个 `SKILL.md` 写了 `pip install` | `tests/skill-requirements.toml:1-19`、`AGENTS.md:286-311` |
| 正文长度 | `SKILL.md` 500 行以内，超了 CI 只报警告 | 文献相关的五个与 scientific-writing 在 280–405 行 | `.github/workflows/skill-spec-validation.yml:139-141` |
| 联网与 key | 规范不管；仓库要求在 `compatibility` 与 `metadata.openclaw.envVars` 里写明 | 40 个 `SKILL.md` 提到 `*_API_KEY` / `*_TOKEN` / `*_KEY` 形式的环境变量；8 个 skill 的脚本里出现 OpenRouter / OpenAI / Anthropic / Gemini 的接口地址或 SDK（autoskill、generate-image、infographics、latex-posters、literature-review、research-lookup、scientific-schematics、scientific-slides）；另有 research-lookup 调 Parallel、exa-search 调 Exa | `AGENTS.md:127-131`；计数用 `grep -rlE` 扫 `skills/*/SKILL.md` 与 `skills/*/scripts` |
| 自引用 | 136 个 `SKILL.md` 末尾有一节「Citing Scientific Agent Skills」，让 agent 在用了这个 skill 的稿子、报告、代码里**加上 K-Dense 的论文引用**并先联网取 arXiv 记录 | 它自己的安全扫描在 60 个 skill 上把这一节标了出来，全是低级别：`LLM_POLICY_VIOLATION` 29 条、`LLM_SOCIAL_ENGINEERING` 28 条、`LLM_PROMPT_INJECTION` 3 条（按发现标题含 citation / self-promot 计） | `skills/paper-lookup/SKILL.md:288-303`、`docs/security-report.json`（如 `citation-management`、`scientific-writing`） |

agentskills.io 规范本身只定 frontmatter 六个字段（`allowed-tools` 标「实验性」，`metadata` 是字符串到字符串），对脚本只要求「自包含或写清依赖」，不要求 PEP 723[^spec]。所以 K-Dense 与规范的偏差只有一处：嵌套的 `openclaw` 块，它自己在 CI 里特意放行（`.github/workflows/skill-spec-validation.yml:76-80`）。平台 P-22 比规范严，差异见第 5 节。

### 1.2 166 个 skill 按领域

按 `docs/skills.md` 自己的分组（每个 skill 恰好出现一次，2026-09-13 审过，`docs/skills.md:3-7`）归并，个数与带脚本数是复查时逐组重算的：

| 组 | 个数 | 带脚本 | 例子 |
|---|---|---|---|
| 生物与组学（生信、系统发育、蛋白组、蛋白工程） | 35 | 21 | scanpy、biopython、bulk-rnaseq、esm |
| 机器学习、量子计算 | 18 | 11 | scikit-learn、pytorch-lightning、qiskit |
| 临床、医学影像、神经、临床前 | 12 | 9 | pydicom、neurokit2、clinical-reports |
| 实验室与平台集成（LIMS、ELN、云实验室、工作流平台） | 12 | 9 | benchling-integration、opentrons-integration、nextflow |
| 科研思维与方法 | 12 | 11 | **literature-review**、**scientific-writing**、hypothesis-generation、peer-review、statistical-analysis |
| 科研写作、出版与展示 | 11 | 9 | **citation-management**、venue-templates、scientific-schematics、pyzotero |
| 化学、药物、药理 | 10 | 6 | rdkit、deepchem、pkpd-modeling |
| 数据库与数据接入 | 10 | 6 | **database-lookup**、depmap、ontology-term-resolution |
| 材料、物理、工程仿真 | 9 | 6 | pymatgen、fluidsim、openpiv、sympy |
| 数据分析与可视化 | 9 | 3 | matplotlib、polars、networkx |
| 基础设施、agent 框架、工具发现 | 8 | 3 | modal、pi-agent、get-available-resources |
| 文档处理 | 7 | 6 | pdf、docx、markitdown、liteparse |
| 研究方法与文献 | 6 | 3 | **paper-lookup**、**research-lookup**、paperclip、paperzilla、research-grants |
| 决策与情景分析 | 3 | 0 | what-if-oracle、consciousness-council |
| 网页检索 | 2 | 1 | parallel-web、exa-search |
| 法规与标准 | 2 | 2 | iso-standards-readiness |
| 合计 | 166 | 106 | |

README 的分类（`README.md:477-633`）有一个 skill 挂多类的情况，加起来是 184，不能直接当分布用。

和平台缺步骤的三个阶段对得上的（只统计，没深读的只看了 frontmatter 与脚本清单）：

| 阶段 | skill | 做法 | 要 key | 证据 |
|---|---|---|---|---|
| 文献 | paper-lookup、research-lookup、literature-review、citation-management、database-lookup | 见第 2 节 | 见第 2.7 节 | 第 2 节 |
| 文献 | paperclip、bgpt-paper-search、paperzilla、exa-search、parallel-web、pyzotero | 第三方服务的调用说明（Paperclip CLI、BGPT MCP、Exa SDK、Parallel CLI、Zotero API），只有 exa-search 带脚本 | 各自的服务 key；bgpt-paper-search 要宿主里配好 BGPT 的 MCP 服务器 | 各 `SKILL.md` 的 `compatibility` 行，如 `skills/bgpt-paper-search/SKILL.md:5` |
| 假设 | hypothesis-generation（8 个脚本，含 `_common.py`）、scientific-brainstorming（4 个）、scientific-critical-thinking、hypogenic | 前两个自称纯标准库、断网、零 key 的本地校验器（证据台账、可证伪检查、预注册模板） | 前两个不要；hypogenic 真跑时要另配 LLM provider 与凭据；scientific-critical-thinking 的可选配图要 OpenRouter | `skills/hypothesis-generation/SKILL.md:5`、`skills/scientific-brainstorming/SKILL.md:5`、`skills/hypogenic/SKILL.md:5`、`skills/scientific-critical-thinking/SKILL.md:6` |
| 写作 | scientific-writing（9 个脚本，含 `_common.py`）、peer-review（8 个）、scholar-evaluation（8 个）、venue-templates（3 个）、research-grants | 前三个同样自称本地、断网的校验器 | 前三个不要；research-grants 的可选配图经 scientific-schematics 要 OpenRouter | `skills/scientific-writing/SKILL.md:5`、`skills/peer-review/SKILL.md:5`、`skills/scholar-evaluation/SKILL.md:5`、`skills/research-grants/SKILL.md:6` |

### 1.3 文献相关 skill 逐条对账

| 说法 | 出处 | 代码里 | 证据 |
|---|---|---|---|
| Paper Lookup 覆盖 10 个学术库 | `README.md:579,630` | `SKILL.md` 已是 18 个（2026-09-11 PR #263 加了 7 个）；README 没跟上 | `skills/paper-lookup/SKILL.md:3`、[^pr263] |
| paper-lookup「查 18 个学术 API」 | `skills/paper-lookup/SKILL.md:3,14` | 18 个 `references/*.md` 是给 agent 的接口手册；**脚本直连的只有 5 个接口**（bioRxiv、medRxiv、Europe PMC、OpenAlex、Crossref 的翻页），另外 3 个脚本只解析 agent 用 `curl` 拿回来的 XML/JSON，不 import 任何网络库 | `skills/paper-lookup/scripts/paginate.py:260-304`、`skills/paper-lookup/scripts/arxiv_atom.py:1-31`、`skills/paper-lookup/scripts/jats_to_text.py:1-34`、`skills/paper-lookup/scripts/openalex_abstract.py:1-27` |
| 每个库的 reference 文件都写了「悄悄失败的方式」 | `skills/paper-lookup/SKILL.md:26` | 18 份里 9 份有单列的 Failure Modes / Hazard 一节（arXiv、PMC、BioStudies、DOAJ、Figshare、OpenCitations、PubTator3、ROR、Zenodo），bioRxiv、medRxiv、Europe PMC 的 200 陷阱写在分页与响应格式节里；PubMed、OpenAlex、Crossref、CORE、Semantic Scholar、Unpaywall 六份没写 200 陷阱，只有错误码格式、限流或零星警告（如 CORE 的分片失败要重试、Unpaywall 的搜索端点 2026-03 起常报 500） | `skills/paper-lookup/references/arxiv.md:206`、`references/pmc.md:46`、`references/biorxiv.md:77,149`、`references/europepmc.md:81-87`、`references/core.md:148-150`、`references/unpaywall.md:34-40`、`references/openalex.md:172-174`、`references/pubmed.md:118-125` |
| paginate 的注释说「这里十个库里六个翻页方式各不相同」 | `skills/paper-lookup/scripts/paginate.py:4` | 注释停在 10 个库的时候；`APIS` 实际覆盖 5 个 | `skills/paper-lookup/scripts/paginate.py:260-304` |
| 可以用 NCBI / S2 key 提速 | `skills/paper-lookup/scripts/paginate.py:25` | 脚本读的只有 `OPENALEX_API_KEY`、`OPENALEX_EMAIL`、`CROSSREF_MAILTO`；NCBI、S2、CORE 的 key 只在 agent 自己拼 `curl` 时用 | `skills/paper-lookup/scripts/paginate.py:203-208,236` |
| Paper Lookup / Research Lookup「可连接多类学术数据库并整理检索证据」（李瑞彬原稿） | 外层 #161 正文「李瑞彬原稿的匹配点」一行[^i161] | research-lookup 的脚本不连。它调 `parallel-cli search/extract`，用 `--include-domains` 把结果限定在 PubMed、arXiv、nature.com 等 25 个域名；学术库只是被搜索的网站。直连学术库的只有 paper-lookup 的 `paginate.py`（5 个接口）与 citation-management 的几个脚本（第 2.5 节） | `skills/research-lookup/scripts/research_lookup.py:39-65,319-341` |
| research-lookup「60 篇已核实、不重复的参考文献」 | `skills/research-lookup/SKILL.md:23,176` | 「已核实」= 被 Parallel Extract 抓到过，**或者**在 URL、标题、摘录里正则匹配到 DOI/PMID（`identifier-verified`）；没有拿 DOI 去 Crossref 核对。DOI 正则的前缀是可选的，任何 `10.xxxx/…` 形状的串都算 | `skills/research-lookup/scripts/manuscript_packet.py:13-17,298-299,345-351,515-520` |
| 证据矩阵、论断—来源映射、共识与冲突、研究空白 | `skills/research-lookup/SKILL.md:147-156` | 全是关键词启发式：研究类型按子串分类；「主要发现」= 含 found/showed/effect 等词的句子；「冲突」= 含 did not/failed to 等词的发现；「研究空白」是三条固定句；每条发现都是 single-source 论断 | `skills/research-lookup/scripts/manuscript_packet.py:177-183,311-339,416-472` |
| 撤稿的排除出去 | `skills/research-lookup/SKILL.md:179` | 标题或摘录里出现 retracted / retraction notice / withdrawn 子串就标 `exclude`：不进论断映射、不进 BibTeX、排到最后，但仍留在 `references.json` 里（读代码推断：讨论撤稿的论文也会被排除，未用样例验证） | `skills/research-lookup/scripts/manuscript_packet.py:302-305,408-413,419-420,692-693` |
| 只在显式选择或允许回退时才发给 OpenRouter | `skills/research-lookup/SKILL.md:38-39,243` | 没装 `parallel-cli` 而环境里有 `OPENROUTER_API_KEY` 时，普通查询会被**自动**路由到 Perplexity（读代码推断；所有测试都把 `parallel-cli` 模拟成已安装，这条路径没测） | `skills/research-lookup/scripts/research_lookup.py:238-247`、`tests/research-lookup/test_research_lookup.py:55,139,234` |
| literature-review「用 PubMed、arXiv、bioRxiv、Semantic Scholar 等多个学术库做系统综述」 | `skills/literature-review/SKILL.md:3` | 检索的主工具是 `parallel-cli search`；自带脚本里没有任何学术库检索 | `skills/literature-review/SKILL.md:23,96` |
| `search_databases.py`「检索多个文献库并汇总」 | `skills/literature-review/scripts/search_databases.py:2-4` | 不联网：读一个已有的 JSON，去重、按年份过滤、排序、输出 markdown / BibTeX | `skills/literature-review/scripts/search_databases.py:209-300` |
| 「经过核实的引用」 | `skills/literature-review/SKILL.md:3,124` | `verify_citations.py` 只查稿子里能正则出来的 DOI（没有 DOI 的引用不查），查它在 doi.org 能否解析、再取 Crossref 元数据；不比对稿子里写的标题作者与记录是否一致；DOI 解析失败也以退出码 0 结束；这个脚本没有测试 | `skills/literature-review/scripts/verify_citations.py:21-42,108-137,182-219`、`tests/literature-review/test_scripts.py:1-36` |
| 配合 gget、bioservices、datacommons-client、brand-guidelines、internal-comms 使用 | `skills/literature-review/SKILL.md:157-159,172-173` | 后三个 skill 在本仓不存在 | `ls skills/` |
| database-lookup 覆盖 78 个库 | `README.md:79,594` | `SKILL.md` 说 80 个，`references/` 下 82 份文件、去掉选库指南与检索契约两份正好 80 个库；没有脚本，全靠 agent 用 WebFetch 或 `curl` | `skills/database-lookup/SKILL.md:13,23,162-176` |
| scientific-writing「证据可追溯、本地一致性检查」 | `skills/scientific-writing/SKILL.md:3,5` | 「本地」对得上：9 个脚本纯标准库、不联网、不读环境变量，测试里用 AST 查禁了 `requests` `urllib` `socket` `subprocess` 等导入。「可追溯」靠的是台账字段，字段由谁填脚本查不了（第 2.6 节） | `tests/scientific-writing/test_static.py:45-87` |
| 论断文本存哈希 | `skills/scientific-writing/SKILL.md:133` | `audit_claims.py` 只检查哈希是 64 位十六进制，不拿稿子里那句话去算、去比；改了句子哈希对不上也查不出 | `skills/scientific-writing/scripts/audit_claims.py:99` |
| 带脚本的 skill 都有测试、CI 挡着；结构契约（含 `--help` 行为）每个 PR 都跑 | `README.md:91,135` | 106 个都有测试目录；CI 只跑 20 个纯标准库的（第 6.1 节）。`--help` 检查不在 `tests/_meta` 的结构契约里，在各 skill 自己的测试套件里（`skill_contract.cli.help_test_case`），所以 PR 上只对那 20 个跑 | `.github/workflows/skill-tests.yml:72-103`、`tests/_contract/structure.py:457-468`、`AGENTS.md:266-281` |
| BYOK 能用全部 166 个 skill | `README.md:20` | BYOK 自己的 README 写 149 个 | [^byok] |

### 1.4 只在 README 里、或代码很薄的

1. **「100+ 数据库」**是 database-lookup 的 80 个接口手册，加上 BioServices、BioPython、gget 这些库自己能访问的库数（`README.md:79`）。手册没有脚本、没有对账代码，靠 agent 照着写。
2. **research-lookup 的「manuscript research packet」**十个文件是真写出来的（`skills/research-lookup/scripts/manuscript_packet.py:719-754`），但内容的结构化程度取决于 Parallel 返回的摘录里有没有 `Authors:` `Journal:` 这类标签行（`skills/research-lookup/scripts/manuscript_packet.py:157-165,341-344`）；没有标签的网页，作者、期刊、方法字段就是空的。十个文件里 `evidence-matrix.json` 与 `references.json` 是同一份列表（`skills/research-lookup/scripts/manuscript_packet.py:603-604,737-738`）。
3. **literature-review 的七阶段方法论**（筛选、质量评估、PRISMA）在 `references/core_workflow.md` 里是文字，代码只有去重排序、DOI 解析、pandoc 出 PDF、AI 配图四样。
4. **「多 agent / 宿主可移植」**：论文自己写「可移植是意图，没测过」，没有宿主 × skill 的兼容矩阵[^paper]。
5. **效果**：论文第 6 节明写不证明装了这些 skill 能让 agent 的科研做得更好；K-Dense 在 k-dense.ai/benchmarks 发过部分 skill 的自测，论文说那些不代表整库[^paper]。

### 1.5 K-Dense BYOK 与本仓的关系

- BYOK 是另一个仓库（`K-Dense-AI/k-dense-byok`，MIT，TypeScript，1,262 star，2026-03-19 建）：一个本机跑的网页应用，内核是 Pi coding-agent SDK 起的单个 agent（叫 Kady），模型走 OpenRouter、各家 API key、ChatGPT/Claude 订阅的 OAuth 或 Ollama[^byok][^byok-arch]。
- 关系是**单向消费**：BYOK 启动时和每天一次，从本仓 `main` 分支拉 skill 放进每个项目的 `sandbox/.pi/skills/`（仓库与分支可用 `KADY_SKILLS_REPO` / `KADY_SKILLS_BRANCH` 改），用户改过的保留、上游删掉的归档[^byok-skills]。本仓代码里没有任何对 BYOK 的依赖，只有 README 的推广段落（`README.md:20-23`）。
- 本仓测试里出现的 `is_byok`（`tests/generate-image/test_scripts.py:383-390`）指的是 OpenRouter 的「自带 key」计费标志，与 K-Dense BYOK 无关。
- BYOK 在 skill 之外还有自己的东西：326 个工作流模板、21 个子 agent、实验记录本、Modal 算力、MCP 接入；再往上是托管平台 K-Dense Web（README 自述，收费方式没查）[^byok]。本文只读 skill 仓库，这些没读。

## 2. 怎么做：主流程

### 2.1 通用做法：说明文档 + agent 自己动手

1. 宿主把 166 个 skill 的 `name` + `description` 常驻上下文，任务看起来对得上时读全文 `SKILL.md`，需要时再读 `references/`（论文第 2.1 节的三层加载）[^paper]。
2. 文档告诉 agent 选哪个接口、怎么拼 URL、哪些失败会伪装成成功；agent 用自己的 shell 跑 `curl`、跑 `python3 scripts/x.py`，结果写回对话。
3. 模型调用只在宿主那边。仓库里直连生成服务的只有 8 个 skill 的脚本（配图、海报、幻灯片、综述配图、research-lookup 的 Chat 与 Perplexity 后端、autoskill）。

### 2.2 paper-lookup

主流程写在 `SKILL.md` 的七步（`skills/paper-lookup/SKILL.md:20-34`）：定检索契约（要什么、时间范围、要不要穷尽）→ 按用途表选库（`:36-91`）→ **先读那个库的 reference 文件**，特别是「静默失败」一节（`:26`）→ 能用脚本就不手写解析（`:28`）→ 有界调用：超过约 1,000 条或 50 次调用要先问人（`:30,157`）→ 返回内容一律当不可信的第三方数据（`:32`）→ 按固定格式交结果：检索摘要、分库结果、出处（端点与参数、ID 转换、条数对账、警告）（`:211-238`）。

脚本做的事：

| 脚本 | 输入 → 输出 | 挡住的失败 | 证据 |
|---|---|---|---|
| `paginate.py` | `--api` + `--query` → 一个 JSON：`provenance.urls`（key 已打码）、`reconciliation`（期望总数、实得、页数、是否完整）、`records` | 按响应报告的页大小步进（bioRxiv 详情页 30 条而非文档写的 100）；认各家真正的结束信号；走完自然结束却少于总数时退出码 4；触到调用方给的上限只算「部分结果」，退出码 0 但要写明 | `skills/paper-lookup/scripts/paginate.py:1-26,98-146,307-373,470-485` |
| `jats_to_text.py` | PMC / Europe PMC 的 JATS XML → 分节正文 | 没有 `<body>`（出版方不许转载时 PMC 照样返回 200）退出码 2，元数据照样输出并标明只是元数据 | `skills/paper-lookup/scripts/jats_to_text.py:1-14,278-285` |
| `arxiv_atom.py` | arXiv Atom XML → JSON | 参数错时 arXiv 返回 200、`totalResults` 为 1、唯一条目标题叫 Error：退出码 3；限流返回纯文本 `Rate exceeded.`：退出码 5 | `skills/paper-lookup/scripts/arxiv_atom.py:1-18` |
| `openalex_abstract.py` | OpenAlex 的倒排索引 → 摘要原文 | 同一位置多个词时，朴素的 `{位置: 词}` 反转会丢词 | `skills/paper-lookup/scripts/openalex_abstract.py:1-12` |
| `_common.py` | 共用：限 64 MB 输入、去控制字符、对账类、URL 里的 `api_key` `apikey` `key` `email` `mailto` `tool` 打码 | | `skills/paper-lookup/scripts/_common.py:32-34,99-113,116-186,197-216` |

四个脚本都不调模型、只用标准库；`paginate.py` 用 `urllib` 直连，其余三个从 stdin 或文件读 agent 抓回来的原始字节（`skills/paper-lookup/SKILL.md:196-204` 的例子全是 `curl … | python3 scripts/x.py -`）。

### 2.3 research-lookup

一个 1,204 行的 CLI 加一个 754 行的纯函数模块。四个后端（`--force-backend parallel` 是 `research` 的别名，`research_lookup.py:168-180`）：

| 后端 | 什么时候选 | 调什么 | 证据 |
|---|---|---|---|
| search（缺省） | 装了 `parallel-cli` 的普通查询 | `parallel-cli search` | `skills/research-lookup/scripts/research_lookup.py:238-247,308-368` |
| research | `--force-backend research`（`parallel` 是别名） | `parallel-cli research run`，默认超时 3,600 秒，返回服务端生成的长报告 | `skills/research-lookup/scripts/research_lookup.py:651-703` |
| chat | 只有显式指定 | 直接 POST `https://api.parallel.ai/chat/completions`，要 `PARALLEL_API_KEY` | `skills/research-lookup/scripts/research_lookup.py:705-759` |
| perplexity | 显式指定，或 `--fallback-perplexity`，或没装 `parallel-cli` 但有 OpenRouter key（见 1.3） | POST `https://openrouter.ai/api/v1/chat/completions`，模型 `perplexity/sonar-pro-search` | `skills/research-lookup/scripts/research_lookup.py:761-829` |

学术模式（查询里有 cite、pubmed、literature review 等 28 个关键词之一，或 `--academic`）的主流程（`skills/research-lookup/scripts/research_lookup.py:449-600`）：

1. 五个方面各跑一次 `advanced` 模式的 Parallel 搜索：近期原始研究、综述与荟萃分析、奠基文献、方法与机制、相反与阴性证据；每次带三到四个关键词变体、限定 25 个学术域名、每次最多 20 条（`:98-130,459-490`）。
2. 去重后不够 60 条，再跑一次不限域名的补充搜索（`:492-522`）。
3. 按「是否撤稿 → 核实程度 → 证据等级 → 年份」排序，取前 60 条，每 10 条一批交给 `parallel-cli extract` 抓页面、抽作者年份期刊 DOI 设计样本量等字段（`:370-447`）。某一批失败只记进台账、不停（`:414-426`）。
4. `build_manuscript_packet` 用正则与关键词把每条来源变成证据矩阵的一行，再拼出论断映射、综合、分节提要、覆盖率（`skills/research-lookup/scripts/manuscript_packet.py:564-611`）。进 packet 的是去重后的**全部**来源（五个方面各最多 20 条，加补充搜索最多 20 条），不截到 60；60 只用在抽取上限和覆盖率的缺口计算上，没被抽取的标 `search-only` 留在列表里（`manuscript_packet.py:573-582,512-538`）。
5. `--packet-dir` 写十个文件：`packet.json/md`、`references.json/bib`、`evidence-matrix.json`、`claim-source-map.json`、`synthesis.json`、`section-briefs.json`、`coverage.json`、`search-ledger.json`（`skills/research-lookup/scripts/manuscript_packet.py:719-754`）。Parallel 的原始响应整包留在 `packet.json` 里（`skills/research-lookup/scripts/research_lookup.py:554-557`）。

默认路径里脚本本身不生成文本；research、chat、perplexity 三个后端返回的是服务端生成的综合文本。search 与 extract 都带一段自然语言的 `objective` 交给 Parallel，由服务端挑摘录（`research_lookup.py:319-341,392-412`）；服务端是否用模型、怎么计费，代码里看不出。

### 2.4 literature-review

`SKILL.md` 定七个阶段（规划、检索、筛选、抽取与质量评估、综合、引用核对、出文档，`skills/literature-review/SKILL.md:73-91`），细节在 `references/core_workflow.md`。agent 实际要做的：用 `parallel-cli search` 带学术域名做第一轮，再用 gget、bioservices 补（`:96,151-159`）；把检索结果存成 JSON 交给 `search_databases.py` 去重排序；写综述正文；跑 `verify_citations.py`；用 `generate_pdf.py`（pandoc + xelatex）出 PDF（`skills/literature-review/scripts/generate_pdf.py:44-57`）。

`SKILL.md:38` 写着「**强制**：每篇综述必须包含至少 1–2 张 AI 生成的图」，给的命令是 `python scripts/generate_schematic.py …`（`SKILL.md:51`）：这个外壳先找 `OPENROUTER_API_KEY`（命令行参数 → 环境变量 → 从当前目录一路往上每一层的 `.env`），再起子进程跑 `generate_schematic_ai.py`，只把这把 key 和网络、证书相关的少数环境变量传过去（`skills/literature-review/scripts/generate_schematic.py:32-85,168-190`）。后者在 OpenRouter 上用 `google/gemini-3.1-flash-image` 出图、`google/gemini-3.7-flash` 看图打分，不够分就改提示重画，最多 2 轮（`skills/literature-review/scripts/generate_schematic_ai.py:113-145,240-247,682-767`、`generate_schematic.py:142-154`）。`generate_schematic.py` 与 `generate_schematic_ai.py` 在 `scientific-schematics`、`scientific-slides`、`latex-posters` 里有逐字节相同的副本，`tests/_meta` 守着不许漂移（`tests/_contract/office.py:35-54`、`tests/_meta/test_repo_contract.py:141-151`）；`SKILL.md` 末尾的脚本清单只列了另外三个脚本，没列这两个（`SKILL.md:190-193`）。

### 2.5 database-lookup 与 citation-management

- **database-lookup**：没有脚本。`SKILL.md` 是选库指南、ID 换算、POST-only 接口清单、key 加载规矩；80 个 `references/*.md` 各写一家的端点与坑（`skills/database-lookup/SKILL.md:17-38,89-99,101-158`）。按平台列了取数工具：Claude Code 用 WebFetch、Codex 和 Cursor 用 `curl`（`:162-176`）；「POST-only」表里 5 个接口（Open Targets、gnomAD、RummaGEO、GDC/TCGA 四个要 POST，SEC EDGAR 要自定义 User-Agent）写明 WebFetch 用不了、要 `curl`（`:89-99`）。上限比 paper-lookup 宽：1 万条或 100 次调用（`:27`）。覆盖物理天文、地球环境、化学药物、材料、生物基因、疾病临床、专利法规、经济金融、社会人口（`:42-45`），**不含文献库**。
- **citation-management**：8 个脚本，是这一组里唯一把学术库检索写成代码的：`search_pubmed.py`（NCBI E-utilities）、`search_openalex.py`（OpenAlex）、`search_google_scholar.py`（`scholarly` 库抓 Google Scholar，可选用免费公共代理）、`extract_metadata.py`（Crossref、PubMed efetch、arXiv）、`validate_citations.py`（Crossref，失败再查 DataCite）、`doi_to_bibtex.py`（doi.org 内容协商取 BibTeX）（`skills/citation-management/scripts/search_pubmed.py:38-40`、`search_openalex.py:37,61`、`search_google_scholar.py:26,48-49,82`、`extract_metadata.py:119,169,255`、`validate_citations.py:209,227`、`doi_to_bibtex.py:43-47`）。`validate_citations.py` 查 DOI 能否解析和 BibTeX 格式，不比对标题作者（`skills/citation-management/scripts/validate_citations.py:88-192,400-415`）。

### 2.6 scientific-writing

不是写稿工具，是写稿时的**台账与校验**（`skills/scientific-writing/SKILL.md:90-276`）：

1. `scaffold_manuscript.py` 生成 7 个文件：`manuscript.md`、`claims.csv`、`source_manifest.json`、`consistency_manifest.json`、`authorship.json`、`manuscript_manifest.json`、`reporting_coverage.json`，里面是 `[[TODO:…]]` 占位，linter 会拒（`skills/scientific-writing/scripts/scaffold_manuscript.py:26-30,80-85`、`skills/scientific-writing/scripts/lint_manuscript.py:20-22,101-104`、`SKILL.md:94-105`）。
2. 来源编 `E` 号进 `source_manifest.json`，论断编 `C` 号进 `claims.csv`，数值、方法、结局、结果编 `N` `M` `O` `R` 号进 `consistency_manifest.json`；稿子里写 `[claim:C001] [evidence:E001,E002]`（`:124-140`）。
3. `audit_claims.py`：每条论断要有已核实的证据号；证据「已核实」= `status: verified` **且** `source_opened: true`；没挂论断号的数字直接报错（`skills/scientific-writing/scripts/audit_claims.py:52-69,194-200`）。`validate_manifest.py` 另要求 `verified` 的来源填了 `verified_by` 与日期（`skills/scientific-writing/scripts/validate_manifest.py:370-400`）。这些都只查字段的值；`SKILL.md` 说「由负责的人打开来源后才标 verified」（`:139-140`），但字段是人填还是 agent 填，脚本分不出来。
4. `check_consistency.py` 对数字与方法—结果映射；`check_references.py` 查 DOI / PMID / ISBN 格式与重复，**不联网解析**（`skills/scientific-writing/SKILL.md:183-195`）。
5. `lint_manuscript.py` 查占位符、夸大与因果措辞、敏感信息，报行号不回显原文。`SKILL.md` 规定 `submission_ready` 只能由人改（`:269-276`）；代码里能做的只是 `submission_ready` 为真时要求各人工核对项 `completed` 并填了核对人与日期（`validate_manifest.py:98-118`）。

### 2.7 各 skill 调了哪些接口、要哪些 key、证据怎么整理

| skill | 脚本直连的接口 | 脚本读的 key / 环境变量 | 只在文档里、由 agent 自己调的 | 检索证据怎么整理 |
|---|---|---|---|---|
| paper-lookup | api.biorxiv.org、ebi.ac.uk/europepmc、api.openalex.org、api.crossref.org（`paginate.py:102,164,201,239`） | `OPENALEX_API_KEY`、`OPENALEX_EMAIL`、`CROSSREF_MAILTO`（`paginate.py:203-208,236`） | PubMed、PMC、arXiv 检索、Semantic Scholar、CORE、Unpaywall、OpenCitations、PubTator3、Zenodo、Figshare、ROR、BioStudies、DOAJ；key：`NCBI_API_KEY`、`S2_API_KEY`、`CORE_API_KEY`（CORE 全文必需）；Unpaywall 要真实邮箱（`SKILL.md:120-135`） | 对话里的固定格式：检索摘要、分库结果、出处与条数对账、警告（`SKILL.md:211-238`）；翻页结果是一个带对账的 JSON；不落固定文件名 |
| research-lookup | `parallel-cli`（search / extract / research）、api.parallel.ai、openrouter.ai（`research_lookup.py:271-278,728-736,800-810`） | `PARALLEL_API_KEY`（chat 必需；search/extract 可用 CLI 登录代替）、`OPENROUTER_API_KEY`（`research_lookup.py:210-212`） | 无 | 十个文件的 packet（2.3 节第 5 步）；证据等级、发现、冲突为启发式 |
| literature-review | doi.org handle API、api.crossref.org（`verify_citations.py:32,47`）；openrouter.ai（`generate_schematic_ai.py:240`） | `OPENROUTER_API_KEY`（配图；环境变量没有就从当前目录往上逐层找 `.env`，`generate_schematic.py:43-77`） | `parallel-cli search/extract`（要 Parallel 账号）；gget、bioservices | agent 按 `assets/review_template.md` 写综述；`search_databases.py` 出 markdown / BibTeX 列表；`verify_citations.py` 出 `<稿>_citation_report.json` |
| database-lookup | 无脚本 | 无 | 80 个库；18 个库的 key 表（FRED、BEA、NCBI、OpenFDA、Materials Project 等，都免费注册）；DrugBank、COSMIC、BRENDA 要付费或注册（`SKILL.md:111-142`） | 对话里：结果表 + 库、端点、参数、访问日期、条数对账、警告（`SKILL.md:31-37`） |
| citation-management | NCBI E-utilities、OpenAlex、Crossref、DataCite、doi.org、export.arxiv.org、Google Scholar（经 `scholarly`） | `NCBI_API_KEY`、`NCBI_EMAIL`、`OPENALEX_EMAIL`（`extract_metadata.py:41,180`、`search_pubmed.py:38-39`、`search_openalex.py:61`） | WebSearch / WebFetch（`SKILL.md:4`） | BibTeX 文件与校验报告 |
| scientific-writing | 无（测试禁网） | 无（测试禁读环境变量） | 无 | 本地台账：`source_manifest.json`、`claims.csv`、`consistency_manifest.json`，校验报告只报代码与行号 |

## 3. 为什么：设计理由与踩过的坑

### 3.1 仓级规则背后的理由

| 规则 | 作者给的理由 | 证据 |
|---|---|---|
| 只收窄 skill：拒收通用工程类、带个科学例子的基础设施、在 skill 之间路由的总控类、同一服务的第二家 | 每个装上的 skill 在每个任务上都争 agent 的注意力；总控类按构造就和所有专科重叠 | `AGENTS.md:10-24`、[^paper] 附录 D |
| `SKILL.md` 500 行上限 | 长内容挤进 `references/`，只有 agent 顺着指针读时才占上下文 | [^paper] 附录 D |
| 测试放 `tests/<name>/`，不进 skill 目录 | skill 目录只装 agent 要读的东西，测试增长不增加宿主要扫的文件 | `AGENTS.md:46-63`、[^paper] 附录 D |
| 一个 skill 一个测试环境、一个 pytest 进程 | 科学包的版本钉互相冲突（opentrons 要 numpy<2、若干包要比 3.13 老的解释器）；多个 skill 各带一个同名的 `scripts/_common.py`，同进程会互相顶掉（文档写 32 个，HEAD 实有 41 个） | `AGENTS.md:240-311`、`tests/conftest.py:1-18` |
| 嵌套的 `metadata.openclaw` | OpenClaw 读这个块做依赖检查和凭据注入，写成 JSON 字符串会让它静默失效 | `AGENTS.md:154-177` |

论文把问题定成「程序性知识」：agent 写出能跑的代码，但分析站不住，比如多重检验没校正、把 3 只鼠 × 100 个细胞当 300 个独立样本；skill 就是把这些领域惯例写下来一次（第 1 节）[^paper]。写法上，论文第 2 节说他们自己写的 skill 通常先让语言模型起草，再人工审读、在环境可用时测一下文档里的流程能不能跑，并明说「这是编写与维护，不是领域验证」；第 6 节说 v2.65.0 的 163 个里有 32 个作者不是 K-Dense，社区贡献的审读可能更少[^paper]。

### 3.2 paper-lookup 2.0：HTTP 200 里的失败

2026-07-28 的提交 061882b 把 paper-lookup 升到 2.0，提交说明写了动机：逐个端点对着真接口核过一遍，发现多数错答案来自「失败时返回 200」——PMC eFetch 对非开放获取文章返回没有正文的完整 XML（这是常态：eFetch 全文只覆盖约 1,000 万篇里的约 300 万篇开放子集）；arXiv 参数错返回一条标题为 Error 的结果；bioRxiv 详情页每页 30 条而不是文档写的 100，按 100 步进会静默跳过 30–99 条；Europe PMC 把 `errCode` 放在 200 的响应体里[^c061882b]。同一个提交把原来按宿主列取网页工具的表换成了「用 `curl`」一节，理由是要和 `allowed-tools` 实际授权的一致[^c061882b]（现在的 `SKILL.md:139-144`）。脚本就是为这几种各做一个退出码，测试用 2026-07-27 抓的真实响应当夹具，其中 `arxiv_error.xml` 是按一次核实过的真实响应重建的，因为 arXiv 限流没能再抓一次（`tests/paper-lookup/test_scripts.py:1-22`）。9 月 11 日的 PR #263 又加了 7 个接口，同样逐个写了实测的 200 陷阱（Figshare GET 忽略查询词、OpenCitations 查不到的 DOI 返回 count 0 等）[^pr263]。

### 3.3 research-lookup 的后端：脚本换过两次，说明与脚本错开过三个月

| 时间 | 变化 | 证据 |
|---|---|---|
| 2025-12-12 到 2026-03 | 随「deep research and writing skills」一批加入，经 OpenRouter 调 Perplexity 的 Sonar Pro Search / Sonar Reasoning Pro，按查询复杂度自动选；2026-02-05 的 PR #41 又从 K-Dense 另一个仓库 claude-scientific-writer 同步过一次 `SKILL.md`（Perplexity 请求头里至今写着 `Scientific Writer Research Tool`，`skills/research-lookup/scripts/research_lookup.py:805-806`） | [^rl-old]、[^pr41] |
| 2026-03-03 | 脚本第一次换后端。PR #66：Parallel Chat 作主、查询里有学术关键词就走 Perplexity，同时加了 `parallel-web` skill | [^pr66] |
| 2026-04-13 | 提交 e5cb785 只改 `SKILL.md`（+213 −76），把说明写成「`parallel-cli search` 是主后端、Chat 管深度研究、Perplexity 管学术检索」；脚本没动，仍是 Chat 作主、学术关键词走 Perplexity。说明与脚本从这天起不一致，到 7 月 14 日才对上 | [^ce5cb785] |
| 2026-04-30 | PR #149：在 description 里补一句「查询文本会发给 api.parallel.ai 与 openrouter.ai」；这句里的 `Note:` 没加引号，把整个 YAML frontmatter 弄坏，Codex 因此跳过加载这个 skill；5 月 18 日 PR #164 加引号修好 | [^i159] |
| 2026-07-14 | 脚本第二次换后端。提交 fc0b9f6：缺省改成 Parallel Search + Extract，目标 60 篇、产出 packet；Chat 降为只能显式选；新增 `manuscript_packet.py` | [^cfc0b9f6] |

#159 的报告人建议在 CI 里加 YAML 检查；现在的 CI 用 `skills-ref validate`（strictyaml）逐个解析，flow 风格的映射会让整份 frontmatter 解析失败，`AGENTS.md` 专门写了一节提醒（`.github/workflows/skill-spec-validation.yml:44-61`、`AGENTS.md:133-147`）。这个 workflow 是 2026-07-26 的提交 b085e11 才加进仓的，比 #159 晚两个多月[^ci-history]；两者之间有没有因果，提交记录里没写。同一类的还有 2026-04 的 PR #135：Codex 对 description 有 1,024 字符上限，超了静默不加载；database-lookup 的描述 1,929 字符超限被砍到 884，paper-lookup 的 1,010 字符没超也一并砍到 495[^pr135]。

### 3.4 scientific-writing 重做：删模板、断网

2026-07-24 的提交 3441b92「Redesign scientific writing safeguards」增 5,295 行、删 7,822 行，删了 LaTeX 报告模板，加了全套台账模板与校验脚本[^c3441b92]。`SKILL.md` 给的理由：一个通用、好看的模板会让看起来合理的占位内容混进投稿（`skills/scientific-writing/SKILL.md:304-306`）。测试把这件事钉死：删掉的 `generate_image.py`、`generate_schematic*.py`、LaTeX 模板不许回来，脚本不许导入网络库、不许读环境变量（`tests/scientific-writing/test_static.py:29-87`）。这与同仓 literature-review「强制 AI 配图」的方向相反，两者并存。

### 3.5 issue 里的其他坑

- **安全**：2026-04 有人用 Claude Code 审计全仓，列了 `curl | sh` 安装、从 GitHub dev 分支装包、docker-compose 默认密码等（#128）；维护者的回应是接入 Cisco 的 skill 扫描器并公开报告[^i128]。literature-review 至今仍写着 `curl -fsSL https://parallel.ai/install.sh | bash`（`skills/literature-review/SKILL.md:224`），它自己的扫描器也把这条标了出来。
- **接口过期**：USPTO 的 PatentsView 迁移后旧域名 NXDOMAIN（#243）、AlphaFold v4 链接失效（#204）——手册型 skill 的内容会随外部接口过期[^i243]。
- **数字对不上**：README 里 skill 总数 161 与 163 混用（#240）；现在 README 说 166、`CITATION.cff:10` 说 163、BYOK README 说 149[^i240]。
- **仓库没有 CHANGELOG**；release 说明由 `release.yml` 把上个 tag 以来的提交标题拼起来（`.github/workflows/release.yml:56-80`）。

## 4. 跑起来要什么

| skill | Python 依赖 | 外部命令 / 服务 | key | 算力与系统 |
|---|---|---|---|---|
| paper-lookup | 无（标准库，Python ≥ 3.11） | `curl`；18 个公开接口 | 全部可选；CORE 全文、Unpaywall 邮箱例外 | 纯 CPU；只要能访问这些接口 |
| research-lookup | `requests`（只有 chat / perplexity 后端要，脚本里懒加载；`SKILL.md` 没写，测试清单写了） | `parallel-cli` 0.7.1（`uv tool install "parallel-web-tools[cli]==0.7.1"`，装在用户级的 uv tool 目录，脚本按 PATH 找它）与 Parallel 账号；可选 OpenRouter | Parallel 登录或 `PARALLEL_API_KEY`；可选 `OPENROUTER_API_KEY` | 纯 CPU；deep research 默认最长等 1 小时 |
| literature-review | `requests`（`verify_citations.py`、`generate_schematic_ai.py`）；测试清单另列 `python-dotenv`，但脚本没 import 它 | `parallel-cli`（`SKILL.md:224` 给的装法之一是把 parallel.ai 的安装脚本直接管道给 bash）；pandoc + xelatex（出 PDF，要装 TeX）；OpenRouter（配图） | `OPENROUTER_API_KEY`；Parallel 账号 | 纯 CPU |
| database-lookup | 无 | 80 个公开接口；`curl` 或宿主的取网页工具 | 视库而定，18 个免费注册 | 纯 CPU |
| citation-management | `requests`；`scholarly`（只有 Google Scholar 要） | 学术接口；可选免费公共代理 | 可选 `NCBI_API_KEY` 等 | 纯 CPU |
| scientific-writing | 无 | 无，断网可跑 | 无 | 纯 CPU |

依据：各 `SKILL.md` 的 `compatibility` 行（literature-review 与 database-lookup 没有这一行，看正文的 Dependencies 与 API Keys 节）、`tests/skill-requirements.toml:73-122`、`skills/research-lookup/SKILL.md:295-299`、`skills/research-lookup/scripts/research_lookup.py:210,271`、`skills/literature-review/SKILL.md:219-243`。

- **操作系统**：5 个 workflow 全在 `ubuntu-latest` 上跑；Windows 上契约测试的 shell 检查会失败，修复 PR #269 还开着[^open-prs]；论文说宿主可移植性没测[^paper]。
- **仓库自己的工具**：`pyproject.toml` 要 Python ≥ 3.13、`cisco-ai-skill-scanner>=2.0.12`；`AGENTS.md` 说扫描器「在 `pyproject.toml` 里钉了版本」，实际只写了下限（`AGENTS.md:208-210`、`pyproject.toml:8`）；`uv.lock` 被 `.gitignore` 挡掉没进仓（`.gitignore:23`），CI 每次重新解析依赖，几个 workflow 的触发路径里却还写着 `uv.lock`（`.github/workflows/skill-spec-validation.yml:8`）；`skills-ref` 从 GitHub 按分支装，没钉版本（`pyproject.toml:13-16`）。
- **安全扫描**要一把 LLM key（`SKILL_SCANNER_LLM_API_KEY`，默认模型 `claude-opus-5`），这是维护方的成本，用 skill 的人不需要（`.github/workflows/security-scan.yml:37-46`）。

## 5. 和平台对照

### 5.1 平台文献阶段现在有什么

- 文献阶段没有步骤能力。主文件是 `sources.md`，由助理用 `ai4sci output new literature` 手写，材料来自助理 CLI 自带的搜索与读网页（`platform/framework/capabilities/__init__.py:45-47`、`platform/docs/add-a-capability.md:42`、`docs/architecture/README.md:174`）。
- 两个通用 skill：`pdf`（论文 PDF → `paper.md` + `images/` + `structured.json`）、`download`（git 仓库、单文件、Hugging Face 拉进 `materials/` 并留收据）；领域包 `domains/petab` 另有一个只有说明的 skill（`platform/docs/add-a-skill.md` 末表）。
- skill 的约定：`stdout` 一行 JSON、诊断进 `stderr`、有 `--help`、输出目录由调用方 `--out` 给（`platform/docs/add-a-skill.md:55-56`，文档约定，不是代码门禁）。
- 没有接任何学术数据库接口；写作阶段的主文件还没定名（P-20）。

### 5.2 它多了什么、重叠什么

| 平台没有的 | 在 K-Dense 哪 |
|---|---|
| 18 个学术接口的调用手册（端点、参数、限流；12 份写了 HTTP 200 里的失败，见第 1.3 节） | `skills/paper-lookup/references/*.md` |
| 翻页与条数对账（走完少了就退出码 4） | `skills/paper-lookup/scripts/paginate.py` |
| JATS 全文分节、arXiv Atom 解析、OpenAlex 摘要重建 | `skills/paper-lookup/scripts/` |
| 一次检索出 60 条带摘录、分等级、带台账的来源包 | `skills/research-lookup/` |
| DOI → BibTeX、BibTeX 校验、PubMed / OpenAlex / Google Scholar 检索脚本 | `skills/citation-management/scripts/` |
| 写作阶段的论断—证据台账与离线校验 | `skills/scientific-writing/` |

| 重叠 | 平台 | K-Dense | 证据 |
|---|---|---|---|
| 读论文 PDF | `pdf` skill（pymupdf4llm） | 同名 `pdf` skill（Anthropic 的，专有许可）、`liteparse`、`markitdown`；名字与平台的 `pdf` 撞车 | `platform/docs/add-a-skill.md` 末表、`skills/pdf/SKILL.md:4` |
| 拿开放获取全文 | `download file` 按链接下 | paper-lookup 用 Unpaywall / CORE 找链接，找到后仍要下载 | `platform/skills/download/SKILL.md:24,30`、`skills/paper-lookup/SKILL.md:53,58` |
| 联网找材料 | 助理与执行层都放行 CLI 自带的联网工具：Claude Code 是 WebSearch / WebFetch，Codex 是服务端的 web_search | research-lookup 与 literature-review 另走 Parallel | `platform/backends/claude_code.py:40-42`、`platform/backends/codex.py:52-53`、第 2.3、2.4 节 |

### 5.3 接进来会碰到平台哪些现有规则

| 规则 | 平台怎么规定 | K-Dense 的实况 | 证据 |
|---|---|---|---|
| P-22 frontmatter | loader 只认 `name` `description` `license` `compatibility` `metadata` 五个字段；`metadata` 必须字符串到字符串 | 102 个用了 `allowed-tools`（规范里的实验性字段），26 个有嵌套的 `openclaw` 块；paper-lookup、literature-review、database-lookup、citation-management 用了前者，research-lookup、literature-review、citation-management 有后者 | `platform/framework/skills/library.py:26,180-215` |
| P-22 脚本 | `scripts/*.py` 每个都要 PEP 723 块和同名 `.lock`，`uv run --locked --offline` 起 | 文献相关带脚本的四个（paper-lookup、research-lookup、literature-review、citation-management）与 scientific-writing 的脚本全部没有 PEP 723 与锁（database-lookup 没有脚本）；平台按 `scripts/*.py` 收，`_common.py` 这类被导入的模块也会被当成脚本要求这两样 | `platform/framework/skills/library.py:147-150,218-228`、`platform/framework/skills/run.py:21,61-66` |
| P-22 合计 | 逐个 skill 过 `load_skill()` 的结果；库级的 `scan()` 只要有一个不过就整库抛错（「agent 拿到一份缺项的清单比拿不到更糟」） | 逐个读：**22 / 166** 能过。文献相关五个与 scientific-writing 全不过：paper-lookup（`allowed-tools`、无 PEP 723、无锁），research-lookup（嵌套 metadata、无 PEP 723、无锁），literature-review 与 citation-management（三样都有），database-lookup（`allowed-tools`），scientific-writing（无 PEP 723、无锁）。能过的 22 个里与文献有关的只有 paperzilla、bgpt-paper-search，都没有脚本。整包原样放进 `platform/skills/`，`scan()` 抛错，清单、`ai4sci skill list / show / run` 与会话注入都起不来 | `platform/framework/skills/library.py:5,110-132`；逐个读的命令见第 8 节 |
| P-22 名字唯一 | 通用库与领域包合起来不许重名 | K-Dense 的 `pdf` 与平台的 `pdf` 重名 | `platform/framework/skills/library.py:124-127` |
| P-22 加载方式 | 不靠任何 agent 的原生 skill 机制：两家适配器都把宿主自己的 skill 关掉（Claude Code `--disable-slash-commands`，Codex 按路径逐个 `enabled=false`），框架把清单拼进 prompt，agent 用 `ai4sci skill list / show / run` | K-Dense 的三层加载（`name` + `description` 常驻、按需读全文与 `references/`）按论文第 2.1 节是交给宿主原生机制做的；`SKILL.md` 里的调用写法是 `python3 scripts/x.py`，不是 `ai4sci skill run` | `docs/architecture/README.md:172`、`platform/backends/claude_code.py:8,39`、`platform/backends/codex.py:25-29`、`skills/paper-lookup/SKILL.md:192-205`、[^paper] 第 2.1 节 |
| P-14 命令入口 | 助理只能跑 `ai4sci`，执行层只能跑 `ai4sci skill`；不接管道、不裸跑 python；联网只用 CLI 自带的搜索与读网页。Claude Code 适配器用 `--permission-mode dontAsk` + `--allowedTools`，Bash 白名单只有 `ai4sci` 前缀（适配器注释说 `dontAsk` 下 grep、ls 这类只读命令本就自动放行，`curl` 算不算没测）；Codex 没有按命令的白名单，`ai4sci` 前缀的命令在沙箱外跑、能联网，其余命令留在沙箱里、没网 | paper-lookup 的主流程就是 agent 在 shell 里 `curl`、再把输出管道给脚本（`SKILL.md:139-150,192-205`），并且写明「总结型取网页工具拿不到状态码与原始 XML、做不了 POST 与自定义头」；database-lookup 允许用 WebFetch，但表里 5 个接口要 `curl`。paper-lookup 里自己联网的脚本只有 `paginate.py`；research-lookup、citation-management、literature-review 的脚本也自己联网。这些脚本经 `ai4sci skill run` 起时，两家适配器下都走放行的那条路 | `platform/framework/chat/guide.py:28`、`platform/framework/skills/__init__.py:35-37`、`platform/backends/__init__.py:77-79`、`platform/backends/claude_code.py:86-89,149-159`、`platform/backends/codex.py:16-22,33`、`skills/paper-lookup/SKILL.md:139-144`、`skills/database-lookup/SKILL.md:89-99` |
| MCP | 两家适配器都不带本机的 MCP：Claude Code `--strict-mcp-config`，Codex 用私有 `CODEX_HOME`、本机 MCP 配置不进 | 12 个 `SKILL.md` 提到 MCP；文献相关的 bgpt-paper-search 的 `compatibility` 写明要在宿主里配 BGPT 的 MCP 服务器，paperclip 在 Windows 上指向托管的 MCP 服务器 | `platform/backends/claude_code.py:8,39`、`platform/backends/codex.py:6-11`、`skills/bgpt-paper-search/SKILL.md:5`、`skills/paperclip/SKILL.md:6` |
| P-1 与 P-25 | 框架不调模型；执行层是唯一写正文的；底座是研究者自己的 agent 登录，按人一份 `agents.yaml` | skill 脚本不在 `framework/`，P-1 的 grep 查不到它们；research-lookup 的 chat / research / perplexity 后端与 literature-review 的配图脚本用独立 key 直接调生成服务，是研究者 agent 登录之外的另一条模型调用路径；research-lookup 缺省的 search / extract 也要 Parallel 账号。平台现有 skill 里读独立凭据的只有 `download`（私有 HF 仓库读 `HF_TOKEN`），那是取数据的凭据，不是调模型 | `docs/architecture/README.md:151,175`、`platform/skills/download/SKILL.md:4,31`、第 2.7 节 |
| P-20 主文件 | 进文献阶段的能力必须留下 `sources.md`；写作主文件待第一个能力定名；skill 不开产出目录，写哪里由调用方定 | paper-lookup 结果在对话里、没有固定文件；research-lookup 写 packet 十个文件，没有 `sources.md`；scientific-writing 的脚手架是 `manuscript.md`、`claims.csv` 与五份 JSON；research-lookup 的 `--packet-dir`、paginate 的 `-o` 都由调用方给路径，与「写哪里由调用者定」一致 | `platform/framework/capabilities/__init__.py:45-52`、`skills/research-lookup/scripts/manuscript_packet.py:719-754`、`skills/scientific-writing/scripts/scaffold_manuscript.py:26-30,80-85` |
| P-7 / P-8 不吞异常 | `make lint` 跑 `ruff check .`，含 `skills/`；选了 E F W B I BLE UP，BLE 是「不吞异常」的机器判据 | 按平台这组规则跑 ruff：BLE001（`except Exception`）paper-lookup 0、scientific-writing 0、research-lookup 3、literature-review 9、citation-management 13；全部规则合计 paper-lookup 11、scientific-writing 0、research-lookup 10、literature-review 206、citation-management 463 条。`verify_citations.py` 失败也退出码 0 | `platform/Makefile:33-34`、`platform/pyproject.toml:44-52`、`skills/literature-review/scripts/verify_citations.py:41-42,182-219`；命令见第 8 节 |
| P-11 两层隔离 | 通用 skill 两层都有，领域 skill 只进执行层；哪层看得到由放在哪个库决定 | K-Dense 没有这种分层。另外 136 个 `SKILL.md` 末尾都有「Citing Scientific Agent Skills」一节，指示 agent 往用它产出的稿子、报告里加一条 K-Dense 论文的引用；放进哪一层，哪一层的 agent 就会读到这一节（会不会照做没测） | `platform/framework/skills/library.py:79-91`、`skills/scientific-writing/SKILL.md:358-373` |
| 脚本约定 | stdout 一行 JSON、`--help`、`--out` 由调用方给（`add-a-skill.md` 的约定，非代码门禁） | paper-lookup 与 scientific-writing 的脚本有 `--help` 和明确退出码，但 JSON 是缩进多行输出；literature-review 的 `search_databases.py` 手写 `sys.argv` 解析，没有 `--help` | `skills/paper-lookup/scripts/_common.py:90-96`、`skills/scientific-writing/scripts/_common.py:165`、`skills/literature-review/scripts/search_databases.py:209-267` |

## 6. 成熟度

### 6.1 测试与 CI 实际测什么

| workflow | 触发 | 测什么 | 不测什么 | 证据 |
|---|---|---|---|---|
| Skill Spec Validation（2026-07-26 加入） | PR、推主干 | 166 个全部过 `skills-ref validate`（字段集合、名字规则、长度、strictyaml 解析）；再加仓库规则：`metadata.version` 必有、`metadata` 值是字符串（`openclaw` `hermes` 例外）、`allowed-tools` 是空格分隔 | skill 内容对不对 | `.github/workflows/skill-spec-validation.yml:48-149` |
| Skill Tests · contract（2026-07-28 加入） | PR、推主干 | `tests/_meta`：带脚本的有测试目录和依赖条目；文档规则（frontmatter、长度、本地链接、不含个人路径、不含测试）对全部 166 个；脚本规则（能编译、不带字节码、禁 `eval`/`exec`/`os.system`、不遮蔽标准库、shell 脚本）对 106 个带脚本的；docx / pptx / xlsx 的 office 目录树，和 `generate_schematic.py`、`generate_schematic_ai.py` 在四个 skill 里的副本不许漂移；`plugin.json` 合规 | 不导入 skill 代码 | `tests/_meta/test_repo_contract.py:67-189`、`tests/_contract/structure.py:457-481`、`tests/_contract/office.py:35-54` |
| Skill Tests · suites | 同上 | 每个 skill 一个临时 uv 环境跑自己的测试；**只跑依赖为空的 20 个**：含 paper-lookup、scientific-writing、hypothesis-generation、peer-review、scholar-evaluation | research-lookup、literature-review、citation-management 等 86 个要装科学包或第三方包的，只在本地 `run_all.py --isolated` 跑，是否在发版前跑过没有记录 | `.github/workflows/skill-tests.yml:72-103`、[^paper] 附录 E |
| PR Skill Scan（2026-04-17 起） | PR 改了 `skills/**` | 改动的 skill 过 Cisco 扫描器，HIGH 及以上判失败；fork 来的 PR 拿不到 key 就只留说明、退出 0 | | `.github/workflows/pr-skill-scan.yml:76-88` |
| Weekly Security Scan（2026-04-10 起） | 每周一 | 全库增量扫描，没变的 skill 沿用上次结果，30 天或换模型时全扫；报告由机器人直接提交到 `main` | | `.github/workflows/security-scan.yml:3-6,37-71` |

文献相关 skill 的测试内容：paper-lookup 的测试全离线，用真实响应夹具测解析、退出码、对账算术、URL 打码，网络翻页本身写明「靠人工核」（`tests/paper-lookup/test_scripts.py:382-384`）；research-lookup 的测试模拟掉 `parallel-cli` 和 `requests.post`，测路由、分面、批量抽取、packet 形状（`tests/research-lookup/test_research_lookup.py:54-387`）；literature-review 只测 `search_databases.py`、`generate_pdf.check_dependencies()` 与配图脚本的共享契约，`verify_citations.py` 没有测试（`tests/literature-review/test_scripts.py:28-37,265-269`）；research-lookup、literature-review、citation-management 的测试都要装 `requests`，不在 CI 那 20 个里。各 workflow 的加入日期按文件的提交历史查[^ci-history]：仓库 2025-10 建，扫描 2026-04 起，规范校验与测试 2026-07 下旬起。

论文附录 E 在 v2.65.0 时指出结构契约只盖 105 个带脚本的 skill，另 58 个不查；HEAD 已把文档类规则扩到全部 skill（`tests/_contract/structure.py:101-112,473-481`）。论文同一节也写明：这些门禁都不判断 skill 写的科学方法对不对[^paper]。

### 6.2 安全扫描实际测什么

- 扫描器组合三类分析：行为（静态看脚本读了什么、发到哪）、触发条件、LLM 审读（`scan_skills.py:95-110`）。
- 2026-09-21 的报告：166 个 skill，674 条发现（28 严重、4 高），155 个标为安全；本次 0 个重扫，最近一次全扫是 9 月 7 日（`docs/security-report.md:3-9`、`docs/security-report.json` 的 `run`）。
- 28 条严重全部来自「读环境变量 + 发网络请求」这一组三条规则（`BEHAVIOR_ENV_VAR_EXFILTRATION` 12、两条跨文件规则各 8），落在 8 个 skill 上，research-lookup、literature-review、citation-management 都在里面（按 `docs/security-report.json` 逐条计数）。`AGENTS.md` 把这类规则列为「skill 读自己服务的 key 调自己服务」的已知系统性误报（`AGENTS.md:224-229`）；分诊文档对这 8 个的结论是「重复前面记录过的服务鉴权模式」，同时写明 autoskill 那种目的地可配的仍要人判断是否可信（`docs/security-triage.md:22-26`）。分诊文档写的是 2026-09-13 那一版报告（165 个 skill、661 条），不是现在这版（`docs/security-triage.md:7-10`）。
- 文献相关几个的低级别发现对得上代码与文档：literature-review 的 `curl | bash` 安装（`skills/literature-review/SKILL.md:224`）、paper-lookup 与 database-lookup 让 agent 读 `.env`（`skills/paper-lookup/SKILL.md:133`、`skills/database-lookup/SKILL.md:107,156`）、citation-management 与 scientific-writing 的自引用指令；database-lookup 另有一条「用 `curl` 拼用户给的标识符」。

### 6.3 发版与维护节奏

- 106 个 release，v1.50.0（2025-10-22）到 v2.69.0（2026-09-11）；改了 `pyproject.toml` 的版本号并推主干就自动打 tag 建 release（`.github/workflows/release.yml:3-9,24-95`）[^releases]。每个 skill 另有自己的 `metadata.version`，与仓库版本分开维护（`AGENTS.md:103-112`）。
- 近 52 周（2025-09-28 到 2026-09-26）653 个提交，按月 18–115 个，2025-10（建仓当月）与 2026-07 最多，各 115 个；9 月 13 日之后主干只有机器人提交的扫描报告[^activity]。
- 732 个提交里第一作者 323 个；56 个贡献者账号。开着的 2 个 issue、15 个 PR，其中改 literature-review 标题重复（#273）、Windows 兼容（#269）、根目录文档同步到 v2.69.0（#268）、新增 verify-citations skill（#254，撤稿与幻觉引用检查）都还没合[^open-prs]。
- 有 PR 模板、三种 issue 模板、`CONTRIBUTING.md`、`SECURITY.md`（私下报告漏洞、只支持 `main` 与最新 tag）。

### 6.4 许可证条款要点

| 范围 | 许可 | 要点 | 证据 |
|---|---|---|---|
| 仓库整体 | MIT，© 2025 K-Dense Inc. | 可改、可再分发、须保留版权声明 | `LICENSE.md:1-20` |
| `pdf` `docx` `pptx` `xlsx` 四个 skill | Anthropic 专有条款（四份 `LICENSE.txt` 逐字节相同） | 不许在服务之外保留副本、复制、做衍生、再分发；使用受与 Anthropic 的协议约束。论文致谢里也写「按其条款使用」 | `skills/pdf/LICENSE.txt:1-30`、`skills/pdf/SKILL.md:4,322`、[^paper] 第 7 节 |
| `deepspot-m` | PolyForm-Noncommercial-1.0.0 | 非商用 | `skills/deepspot-m/SKILL.md:4` |
| `what-if-oracle` | CC BY-NC-SA 4.0 | 非商用、相同方式共享 | `skills/what-if-oracle/SKILL.md:4` |
| 包装类 skill | 字段多写被包装库的许可：BSD 三条款（scanpy 等，写法不一，共 18 个）、Apache-2.0（共 20 个）、GPL（bioservices、etetoolkit、cobrapy）、`Unknown`（3 个）、`Proprietary (API key required)`（rowan）、没写（4 个） | 这个字段说的是 skill 文本的许可还是被包装库的，仓库没写清 | `license:` 字段统计，见第 8 节 |
| 文献相关五个 | MIT | | 各 `SKILL.md` 第 4–5 行 |

## 7. 还没弄清的问题

1. **Parallel 的费用与可达性**：research-lookup 默认一次学术查询是 5–6 次 advanced 搜索加最多 6 批抽取，Parallel 怎么计费、有没有免费额度、国内网络能否访问 api.parallel.ai 与 openrouter.ai，都没查也没测。
2. **OpenAlex 是否已按量收费**：`paginate.py` 会把 OpenAlex 返回的 `meta.cost_usd` 记进备注，`SKILL.md` 把 `OPENALEX_API_KEY` 标为「推荐」（`skills/paper-lookup/scripts/paginate.py:218-219`、`skills/paper-lookup/SKILL.md:129`）；不带 key 的额度是多少没查。
3. **宿主自带的取网页工具够不够**：paper-lookup 认为总结型工具拿不到状态码和原始 XML。Claude Code 的 WebFetch、Codex 的 web_search 实际能不能拿到 JATS / Atom 原文与 200 响应体里的错误，要实测（#163）。
4. **放进平台时 `_common.py` 怎么处理**：平台按 `scripts/*.py` 一律要求 PEP 723 与锁，`ai4sci skill run` 也会把 `_common.py` 列成可起的脚本（`platform/framework/skills/run.py:45-58`）；被导入的共享模块算不算脚本，平台没有先例。K-Dense 的脚本靠把自己所在目录插进 `sys.path` 来 import 它（`skills/paper-lookup/scripts/paginate.py:42-44`）。
5. **启发式在我们课题上的表现**：research-lookup 的研究类型词表和效应量正则以临床研究为主（`skills/research-lookup/scripts/manuscript_packet.py:23-32,68-96`），对 PINN、参数估计这类工程与物理论文会分成什么样，没测。
6. **自引用指令会不会真的被执行**：136 个 `SKILL.md` 让 agent 往用户的稿子里加 K-Dense 论文的引用；平台的执行层或助理读到这一节时会不会照做，没测。
7. **撤稿判定与自动路由到 Perplexity** 两条（第 1.3 节）是读代码推断，没有用样例或真跑验证。
8. **BYOK 的 149 与本仓的 166** 差在哪：BYOK 的 `server/src/agent/skills-fetch.ts` 用 `skills` CLI 拉整个目录，粗看没有按名单过滤的代码，149 可能只是 README 徽章没更新；没有逐行读，未验证[^byok-skills]。
9. **86 个不在 CI 的测试**有没有在发版前跑过：论文说 pinned tree 不记录这件事，现在也没有记录。
10. **论文外的效果数据**：K-Dense 在 k-dense.ai/benchmarks 和博客里的 skill 自测没读；论文本身不提供任务级评测。
11. **包装类 skill 的 `license` 字段含义**（第 6.4 节）。
12. **平台里三个解析脚本的输入从哪来**：`jats_to_text.py`、`arxiv_atom.py`、`openalex_abstract.py` 只读 stdin 或本地文件里的原始响应（第 2.2 节）。平台里 agent 不能自己 `curl`（第 5.3 节 P-14 一行）；Claude Code 的 WebFetch、Codex 的 web_search 能不能把原始 XML / JSON 原样落成文件，没测；`download file` 能不能拿来取这类接口的响应，也没试。
13. **Parallel 服务端做了什么、数据去哪**：search / extract 都把一段自然语言 `objective` 和查询文本发给 Parallel（第 2.3 节）；服务端是否用模型、查询文本与摘录如何留存、按什么计费，没查。
14. **scientific-writing 的人工核对字段在平台里由谁填**：它的 `verified_by`、`source_opened`、`submission_ready` 只是 JSON 字段（第 2.6 节）；平台里「只有人能确认」靠的是 `signed.json` 与拒绝助理调用的判据（`docs/architecture/README.md:169`），两者之间没有对过。

## 8. 调研方法

- 克隆：外层仓 `vendor/scientific-agent-skills`（`.gitignore` 挡住），浅克隆，只有提交 49c6e97 一个；历史、issue、PR、release、贡献者、提交频率都用 `gh api` 与 `gh issue/pr view` 只读查询，2026-09-27 取数。
- 统计用的都是只读命令：`ls -d skills/*/scripts | wc -l`；`grep -rl '^# /// script' --include='*.py' skills`；`find skills -name '*.lock'`；逐个 `SKILL.md` 取 frontmatter 顶层键与 `license:` 值做计数；按 `docs/skills.md` 的标题与链接归组；从 `tests/skill-requirements.toml` 挑 `packages = []` 且无 `python` 的条目复算 CI 实际跑的 20 个。
- 「22 / 166 过平台 loader」：用平台自己的 `platform/framework/skills/library.py` 的 `load_skill()` 逐个读 `vendor/scientific-agent-skills/skills/*`，按报错归因（复查时重跑一遍，结果相同：缺锁 106、`allowed-tools` 102、缺 PEP 723 102、嵌套 metadata 26）。这一步只运行了平台代码读文件，没有运行 K-Dense 的任何代码。
- 平台 ruff 规则的统计：用平台 venv 里的 ruff 按平台选的规则（`--isolated --select E,F,W,B,I,BLE,UP --line-length 100 --target-version py312`）静态检查五个文献 skill 的 `scripts/`，只读不改、不执行被检查的代码。
- 论文：`arxiv.org/pdf/2609.00065` 下载到外层 `materials/research/2026-0927-scientific-ai-capabilities/papers/`，用平台的 `pdf` skill 解析；读了摘要、第 1、2、6、7 节与附录 D、E。
- BYOK：只读了它的 README、`docs/architecture.md`、`docs/skill-management.md`、`server/src/config.ts` 的 skill 仓库配置，并在 `server/src/agent/skills-fetch.ts` 里 grep 过有没有过滤名单。
- 没做的：没装依赖、没跑 K-Dense 的脚本和测试、没调任何外部接口。实测留给 #163。

[^paper]: Kassis T., Agarwal V., He Y., Patel D., Brueckner A. M. *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*. arXiv:2609.00065，描述 v2.65.0（2026-08-29，提交 f6fcafe）。摘要与第 6 节写明没有任务级评测、宿主可移植性没测、163 个里 32 个作者不是 K-Dense；第 2 节写编写流程（语言模型起草、人工审读）与三层加载；附录 D 设计规则；附录 E 门禁范围与安全扫描。<https://arxiv.org/abs/2609.00065>
[^spec]: Agent Skills Specification，frontmatter 字段表（`allowed-tools` 标 Experimental，`metadata` 为字符串到字符串）与 `scripts/` 一节。<https://agentskills.io/specification>，2026-09-27 取。
[^gh-meta]: GitHub API `repos/K-Dense-AI/scientific-agent-skills` 与 `contributors`、`commits`，2026-09-27 取：46,743 star、4,227 fork、2025-10-19 建、732 个主干提交、56 个贡献者账号、timothykassis 323 个。
[^releases]: GitHub API `releases`，共 106 个，最早 v1.50.0（2025-10-22），最新 v2.69.0（2026-09-11）。<https://github.com/K-Dense-AI/scientific-agent-skills/releases>
[^activity]: GitHub API `stats/commit_activity`，2026-09-27 取，52 周从 2025-09-28 起；把每周的逐日计数按日期归到月份：2025-10 起依次 115、43、18、36、76、48、57、51、32、115、33、29，合计 653。
[^open-prs]: 2026-09-27 开着的 issue #197、#277，PR #252、#254、#260、#265–#276。<https://github.com/K-Dense-AI/scientific-agent-skills/pulls>
[^byok]: K-Dense BYOK README（v0.7.3 徽章、149 个 skill、326 个工作流、模型来源、K-Dense Web）。<https://github.com/K-Dense-AI/k-dense-byok>
[^byok-arch]: K-Dense BYOK `docs/architecture.md`：后端是 Pi SDK 起的单个 agent，首次启动把 skill 目录下载到每个项目的 `sandbox/.pi/skills/`。<https://github.com/K-Dense-AI/k-dense-byok/blob/main/docs/architecture.md>
[^byok-skills]: K-Dense BYOK `docs/skill-management.md`（启动与每日同步、改过的保留、上游删除的归档）与 `server/src/config.ts` 第 41–43 行（`KADY_SKILLS_REPO` 缺省 `K-Dense-AI/scientific-agent-skills`，分支缺省 `main`）；拉取在 `server/src/agent/skills-fetch.ts`（经 `skills` CLI，失败退回浅克隆）。2026-09-27 用 `gh api` 取。<https://github.com/K-Dense-AI/k-dense-byok/blob/main/docs/skill-management.md>
[^i159]: Issue #159：PR #149 在 research-lookup 的 description 里加的 `Note:` 使 YAML 失效、Codex 跳过加载；报告里的路径还是旧目录 `scientific-skills/`；PR #164 修复。<https://github.com/K-Dense-AI/scientific-agent-skills/issues/159>
[^rl-old]: `scientific-skills/research-lookup/SKILL.md` 在提交 f6f3023（2026-02-23，2026-03-01 之前对该文件的最后一次改动）时的 description：经 OpenRouter 用 Perplexity 的 Sonar Pro Search 或 Sonar Reasoning Pro；该文件最早出现在 2025-12-12 的提交 ae60fcf「Added all updated deep research and writing skills」。用 `gh api repos/K-Dense-AI/scientific-agent-skills/contents/…?ref=f6f3023` 取。
[^pr41]: PR #41「Sync writing skills from claude-scientific-writer」，2026-02-05 合并。<https://github.com/K-Dense-AI/scientific-agent-skills/pull/41>
[^pr66]: PR #66「Add parallel-web skill and update research-lookup」，2026-03-03 合并：Parallel Chat 为主、Perplexity 管学术检索。<https://github.com/K-Dense-AI/scientific-agent-skills/pull/66>
[^cfc0b9f6]: 提交 fc0b9f6（2026-07-14）：research-lookup 改为 60 篇目标与 packet，新增 `manuscript_packet.py`。<https://github.com/K-Dense-AI/scientific-agent-skills/commit/fc0b9f6>
[^pr135]: PR #135「trim skill descriptions for Codex 1024-char limit」，2026-04-13 合并：database-lookup 描述 1,929 → 884 字符，paper-lookup 1,010 → 495（后者原本没超 1,024）。<https://github.com/K-Dense-AI/scientific-agent-skills/pull/135>
[^c061882b]: 提交 061882b「Update paper-lookup to 2.0」（2026-07-28），提交说明列出 PMC、arXiv、bioRxiv、Europe PMC 的 200 陷阱；24 个文件、+3,377 行。<https://github.com/K-Dense-AI/scientific-agent-skills/commit/061882b>
[^pr263]: PR #263「Add companion literature APIs to paper-lookup」，2026-09-11 合并：11 → 18 个接口，不加脚本，逐个写了实测的 200 陷阱。<https://github.com/K-Dense-AI/scientific-agent-skills/pull/263>
[^c3441b92]: 提交 3441b92「Redesign scientific writing safeguards」（2026-07-24）：39 个文件、+5,295 / −7,822 行，删除 LaTeX 模板。<https://github.com/K-Dense-AI/scientific-agent-skills/commit/3441b92>
[^i128]: Issue #128「Security review: credential exposure, unsafe install patterns, insecure defaults」，2026-04-11 关闭，维护者回复改用 Cisco Skill Scanner。<https://github.com/K-Dense-AI/scientific-agent-skills/issues/128>
[^i243]: Issue #243：PatentsView 迁到 USPTO ODP 后旧 API 域名 NXDOMAIN；另见 #204 AlphaFold v4 链接失效。<https://github.com/K-Dense-AI/scientific-agent-skills/issues/243>
[^i240]: Issue #240：README 的 skill 总数 161 与 163 混用。<https://github.com/K-Dense-AI/scientific-agent-skills/issues/240>
[^i161]: 本仓 issue #161「项目 · K-Dense Scientific Agent Skills（文献检索）」正文表格「李瑞彬原稿的匹配点」一行：「含 Paper Lookup / Research Lookup，可连接多类学术数据库并整理检索证据」。<https://github.com/zephyr4123/TJU-AI4Science/issues/161>
[^ce5cb785]: 提交 e5cb785「enhance: integrate parallel-web skill for literature reviews and research lookups」（2026-04-13），research-lookup 只改了 `SKILL.md`；同一提交下 `scientific-skills/research-lookup/scripts/research_lookup.py` 的模块说明与 `_select_backend` 仍是「Parallel Chat 为缺省、学术关键词走 Perplexity」。用 `gh api repos/K-Dense-AI/scientific-agent-skills/commits/e5cb785` 与 `contents/…?ref=e5cb785` 取。<https://github.com/K-Dense-AI/scientific-agent-skills/commit/e5cb785>
[^ci-history]: 按路径查提交历史（`gh api repos/K-Dense-AI/scientific-agent-skills/commits?path=<文件>`），取最早一条：`security-scan.yml` 0303a33（2026-04-10），`pr-skill-scan.yml` aaf95ee（2026-04-17），`skill-spec-validation.yml` b085e11（2026-07-26），`skill-tests.yml` 与 `tests/_meta/test_repo_contract.py` 4fb7e0b（2026-07-28）。2026-09-27 取。
