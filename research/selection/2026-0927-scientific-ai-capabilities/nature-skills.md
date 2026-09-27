---
title: Nature Skills 代码级深读
subtitle: 科研 AI 能力选型 · 文献、假设、写作三阶段的候选 · 19 个 skill 加一个共享包，逐个对到代码
kind: 开源项目选型深读（只读代码，不跑、不装依赖）
date: 2026-09-27
scope: 仓库 https://github.com/Yuan1z0825/nature-skills，浅克隆到外层 vendor/nature-skills，提交 9e2d90e（2026-09-25）；不带前缀的 文件:行 相对该仓库根，带 platform/ 前缀的相对外层仓（内仓提交 de3d948，v1.0.1）；issue、PR、CI、提交历史用 gh api 于 2026-09-27 查；网页版 natureskills.cn 于同日用 curl 取页面；不读 README_EN、各 skill 的 README_EN、nature-figure 里的 figures4papers 第三方示例；对应 issue #187（母 issue #186）
status: 第一版
---

> **结论先行**：它是 20 个按 agentskills.io 格式写的 skill 目录（19 个可触发，加一个共享包 `nature-shared`），主体是提示词：写作、润色两个目录零代码，连同共享包合计约 7800 行 Markdown（不含 README），共享包里只有一个 273 行的检查脚本。仓库里**没有任何调文本模型的代码**（按 SDK 导入与外部主机名全仓 grep 过），起草、润色、读论文、做 PPT 都由宿主 agent（Codex、Claude Code 等）自己完成；脚本做的事有：确定性检查（图的碰撞与对齐、PPTX 版式、公式定界符、术语与数值精度、返修包一致性）、格式转换与文档组装（RIS / BibTeX / ENW / DOCX，image2ppt 与 patent 还组装 PPTX、DOCX）、调公开检索与出版商接口（CrossRef、OpenAlex、PubMed、arXiv、Unpaywall、Europe PMC，Elsevier / Springer Nature / IEEE 要各自的 key）、驱动用户已登录的 Chrome 下全文与用 Playwright 爬国知局公布站，以及三个要单独凭据的图像 / OCR 服务（OpenRouter 图像接口、OpenAI 兼容图像接口或读 `~/.codex/auth.json` 走 ChatGPT 后端、百度 PaddleOCR）。
>
> 放到平台要找的三个阶段上：**写作**最厚，但 `nature-writing` 与 `nature-polishing` 的默认产出是对话里的回复（writing 的投稿材料任务在用户要 `.tex` 时才填仓库的 LaTeX 模板，polishing 的排版请求直接改用户的 LaTeX 并编译）；写作侧代码量最大的是 `nature-figure`（约 3900 行），出图方式是 agent 自己写 matplotlib 或 ggplot2 并运行，仓库给 5 个 CSV 模板和约 2850 行 QA 脚本（含一个 R 文件），AI 示意图走 OpenRouter Images API；其余写作侧的代码只有 proposal-writer 的 md 转 DOCX（231 行）与 response 的返修包一致性检查（310 行）。**文献**有检索（一个 MCP server 加一个无 MCP 的 OpenAlex 脚本）、Nature/CNS 限定的引文检索导出、双语全文 reader、论文精读卡；**假设**没有专门的 skill，最接近的是精读卡第 16 节的六道门、文献管线里的 gap 分析、开题报告写作状态机。
>
> README 与代码对不上的主要几处：`nature-literature-pipeline` 自称 "production-tested" 并标 Stable，目录里零代码，靠宿主的 cron；`nature-ref-verifier` 标 Stable，零代码；`nature-academic-search` 的工具清单列了 11 个仓库里不存在的 MCP 工具（其中 6 个标注来自外部的 "paper-search MCP"），说"两个纯标准库脚本"其中一个要 `requests` 与 `defusedxml`；它的 MCP server 在当前 HEAD 上用 Python 3.13 及以下导入即失败（CI 用 3.11），CI 里的 skill 工具测试从 2026-09-16 起在 main 上一直失败，而且同一个 job 里排在它后面的 9 个 skill 的测试步骤从那时起都被跳过、没有跑。网页版 natureskills.cn 是另一个闭源的收费站点（Skills 交易市场加按积分计费的"科研 Agent"），仓库里没有它的代码。
>
> 和平台对照只列事实：原样放进平台的 `skills/`，20 个目录里 14 个会被 `platform/framework/skills/library.py` 拒掉（脚本缺 PEP 723 头与锁、metadata 嵌套、名字与目录不一致；已用平台的 `load_skill` 对 20 个目录逐个跑过确认），且库里有一个坏的就整库报错；它的 router 写法要 agent 按相对路径读 `manifest.yaml`、`static/`、`../nature-shared/`，而平台的 `ai4sci skill show` 只给正文、`references/` 文件名与目录路径；它让 agent 直接跑 `python` / `Rscript` / `node`，平台的 Claude Code 适配器给执行层的 Bash 白名单只有 `ai4sci skill`，Codex 适配器没有按命令的白名单，别的命令留在断网的沙箱里跑。怎么读：第 1 节对账，第 2 节流程，第 5 节平台对照，第 7 节没弄清的。横向对比见同目录的 [README.md](README.md)。

## 1. 是不是：README 说的能力在代码里对应哪段

### 1.1 二十个目录逐个对账

README 的技能索引列 19 个可触发 skill，`nature-shared` 不计入（`README.md:482-506`），与 `skills/` 下 20 个目录一致。20 个目录每个都有 `manifest.yaml`，但只有 8 个声明了轴（writing 5 个、polishing 4 个、patent 3 个，figure、reader、paper-card、paper2ppt、academic-search 各 1 个；figure 另有两条路由），其余 12 个的 manifest 没有 `axes`，只列总要加载的文件与按需读取的条件表（用 PyYAML 逐个读 `axes` 键统计）。"形态"一列：**router** 指 SKILL.md 只是路由，按 `manifest.yaml` 的轴把 `static/` 里的片段读进来；**无轴**指有 manifest 但没有轴；**纯提示词**指目录里没有任何可执行文件（测试除外）。

| 目录 | README 状态 | 形态 | 代码做什么 | 证据 |
|---|---|---|---|---|
| `nature-writing` | Draft | router，5 轴（task、paper_type、section、language、journal），纯提示词 | 无脚本；`templates/submission/` 四个初投稿 LaTeX 模板 | `skills/nature-writing/SKILL.md:12-38`、`skills/nature-writing/manifest.yaml:8-92` |
| `nature-polishing` | Stable | router，4 轴，纯提示词 | 无脚本；全文一致性扫描借用 `nature-shared` 的脚本 | `skills/nature-polishing/SKILL.md:12-36`、`skills/nature-polishing/manifest.yaml:7-72` |
| `nature-shared` | 不计入索引 | 共享参考包：11 个 `core/` 文件、3 个期刊格式文件 | `check_consistency.py` 273 行，纯标准库：术语变体、同值不同精度、等值长度单位混用三项 | `skills/nature-shared/manifest.yaml:12-52`、`skills/nature-shared/scripts/check_consistency.py:15-26,215-223` |
| `nature-figure` | Stable | router，1 轴（backend：python / r）加两条路由 | 5 个 CSV 驱动的 matplotlib 模板；源码静态预检、PDF 字号审计、渲染后碰撞审计、多面板对齐审计；OpenRouter 出示意图；Python/R 偏好读写 | `skills/nature-figure/manifest.yaml:16-63`、`skills/nature-figure/scripts/plot_templates.py:1-11` |
| `nature-reader` | Beta | router，1 轴（source_format） | 只有 `validate_reader_math.py`（458 行，标准库）查公式定界符、裸 LaTeX、公式锚点；PDF 抽取交给仓库外一个叫 `pdf` 的 skill | `skills/nature-reader/static/fragments/source/pdf-text.md:3`、`skills/nature-reader/static/core/output-contract.md:28-34` |
| `nature-paper-card` | Beta | router，1 轴（paper_type） | `prepare_paper.py` 从 PDF 或 reader 的 source map 出 `source_bundle.json`；`audit_paper_card.py` 查 16 节结构与页码定位 | `skills/nature-paper-card/SKILL.md:35-50,106-125` |
| `nature-paper2ppt` | Beta | router，1 轴（paper_type，6 条叙事弧） | 没有生成 PPTX 的脚本，agent 自己写 python-pptx；只有 `audit_pptx_quality.py`（370 行，标准库）读 PPTX XML 查越界、字数、模板腔 | `skills/nature-paper2ppt/static/core/toolchain.md:5-10,20-28`、`skills/nature-paper2ppt/scripts/audit_pptx_quality.py:2-19` |
| `nature-image2ppt` | Beta | 自带 CLI 包，非 router | 约 1.05 万行 Python（其中 CLI 包 8300 行）：页面状态机、PPTX 组装、渲染 QA；图像生成与 OCR 走外部接口 | `skills/nature-image2ppt/SKILL.md:9-18,79-92` |
| `nature-academic-search` | Beta | router，1 轴（workflow，6 条） | MCP server（CrossRef、PubMed、arXiv、Scopus、ScienceDirect）约 2500 行；无 MCP 时的 OpenAlex 检索脚本；RIS/BibTeX 转换 | `skills/nature-academic-search/mcp-server/academic_search_server.py:1-35` |
| `nature-citation` | Beta | 无轴 | `nature_citation.py` 2356 行：切段、查 CrossRef、按 Nature/CNS 期刊族过滤、导出 RIS/ENW/Zotero RDF | `skills/nature-citation/scripts/nature_citation.py:1-30,2239-2269` |
| `nature-ref-verifier` | Stable | 纯提示词 | 无脚本；要求 agent 用 CrossRef、WebSearch、`kimi-datasource`、`zotero-mcp` 等环境里现成的工具，超过 20 条拆给并行子代理 | `skills/nature-ref-verifier/SKILL.md:43-59` |
| `nature-literature-pipeline` | Stable | 纯提示词 | 无脚本；每日检索、六维打分、推送、归档全靠宿主 agent 与宿主的定时任务（文中写 Hermes cron） | `skills/nature-literature-pipeline/SKILL.md:16-40,112` |
| `nature-downloader` | Beta | 大 SKILL.md（345 行正文），非 router | Node.js 22 编排：OA、出版商 API、CNKI 与机构访问走用户已登录的 Chrome（CDP 远程调试）；Python 做学校配置与 PDF 校验 | `skills/nature-downloader/SKILL.md:4-5,31` |
| `nature-proposal-writer` | Beta | 状态机提示词，frontmatter 名字是 `researchwrite` | `build_proposal_docx.py`（python-docx）把 md 转 DOCX | `skills/nature-proposal-writer/SKILL.md:2,41-60` |
| `nature-reviewer` | Draft | 纯提示词 | 无脚本；要求三份互盲审稿报告各在独立上下文生成 | `skills/nature-reviewer/SKILL.md:19-23` |
| `nature-response` | Beta | 无轴：manifest 只有 2 个 `always_load` 与按需 references | `check_package_consistency.py`（310 行，标准库）查返修包内部一致；另有 3 个返修 LaTeX 模板 | `skills/nature-response/scripts/check_package_consistency.py:1-12`、`skills/nature-response/manifest.yaml` |
| `nature-statistics` | Draft | 纯提示词 | 无脚本 | `skills/nature-statistics/SKILL.md:1-4` |
| `nature-data` | Draft | 无轴，纯提示词：manifest 自己写"there is therefore no content axis"，只有 2 个 core 文件加按需 references | 无脚本 | `skills/nature-data/manifest.yaml:7-18` |
| `nature-paper-to-patent` | Beta | router | 约 4600 行：DOCX / OMML / Mermaid 渲染、权利要求审计、国知局检索（Playwright） | `skills/nature-paper-to-patent/requirements.txt:1-7`、`skills/nature-paper-to-patent/scripts/disclosure/requirements-cnipa.txt:1-2` |
| `nature-experiment-log` | Draft | 纯提示词 | 无脚本；可选接飞书 CLI 与 Obsidian | `skills/nature-experiment-log/SKILL.md:1-9` |

规模上（不含测试与 figures4papers）：全仓 skill 代码约 3.35 万行，其中 `nature-image2ppt` 1.05 万、`nature-downloader` 5300、`nature-paper-to-patent` 4600、`nature-academic-search` 4400、`nature-figure` 3900、`nature-citation` 2400；写作、润色、统计、数据、审稿、文献管线、文献核验、实验日志八个目录零代码。

**仓库里调模型的只有图像与 OCR**，没有一处调文本模型：`skills/nature-figure/scripts/generate_openrouter_schematic.py:19-20`（`https://openrouter.ai/api/v1/images`，默认 `openai/gpt-image-2`）、`skills/nature-image2ppt/cli/image2ppt/runtime/image_gen.py:39-52`（`codex-oauth` 与 `openai-compatible-api` 两个后端）、`skills/nature-image2ppt/cli/image2ppt/runtime/paddle_text_hints.py:11,32`（PaddleOCR）。

### 1.2 README 说了、代码里没有或只接了一半的

| README 或 SKILL 里的说法 | 代码里 | 证据 |
|---|---|---|
| `nature-literature-pipeline`："A complete, production-tested automated literature pipeline"，状态 Stable（定义是"已在真实学术内容上验证"） | 目录里只有 SKILL.md、6 个 references、1 个模板，零代码；定时、检索、推送全靠宿主 agent，文末自己写了"Hermes cron is local" | `skills/nature-literature-pipeline/SKILL.md:16,112`、`README.md:504,660` |
| `nature-ref-verifier` 状态 Stable、"多源交叉验证" | 零代码；来源表里的 IEEE Xplore、CNKI/万方（`kimi-datasource / webbridge`）、`zotero-mcp` 都是环境里有才用 | `skills/nature-ref-verifier/SKILL.md:47-59`、`README.md:501` |
| `nature-academic-search` 工具清单：扩展检索 6 个（Google Scholar、Semantic Scholar、bioRxiv、medRxiv、WoS、Scopus）与 PubMed 工具 6 个 | 本仓的 MCP server 实现 16 个工具：`search_papers`、`get_paper_by_id`、`get_citation`、`lookup_mesh` 与 12 个 Scopus/ScienceDirect 工具；清单上另外 11 个名字（扩展检索里除 `search_scopus` 外的 5 个、PubMed 工具 6 个）在全仓 `.py` / `.json` / `.toml` / `.sh` 里零命中；扩展检索一栏标注来源是"paper-search MCP"，PubMed 一栏没写来源，`config/` 与 `install.sh` 里也没有配置这两个外部 server。同目录调研的 openags/paper-search-mcp（[paper-search-mcp.md](paper-search-mcp.md)，本地克隆提交 808e462）里有同名的 `search_google_scholar`、`search_biorxiv`、`search_medrxiv`，Semantic Scholar 在那边叫 `search_semantic`，没有 `search_webofscience` 与 `search_scopus`；清单指的是不是这个项目、哪个版本，未核实 | `skills/nature-academic-search/static/core/tools.md:30-50`、`skills/nature-academic-search/mcp-server/academic_search_server.py:163-613`；paper-search-mcp 的 `paper_search_mcp/server.py:687-723,920` |
| 无 MCP 时"two stdlib-only scripts"；同一文件前面还写 format converter "uses Python stdlib only — no extra dependencies" | `academic_search.py` 是纯标准库；`format-converter.py` 导入 `requests` 与 `defusedxml`（`defusedxml` 是 PR #225 于 09-22 换进来的） | `skills/nature-academic-search/static/core/routing-and-ops.md:47,51-54`、`skills/nature-academic-search/scripts/format-converter.py:31-32` |
| MCP server 可用（README 让用户 `pip install -r mcp-server/requirements.txt`） | HEAD 上 `sources/arxiv.py` 用 `defusedxml.ElementTree as ET` 并在方法与函数的类型注解里写 `ET.Element`，该文件没有 `from __future__ import annotations`，Python 3.13 及以下在导入时就求值注解，报 `AttributeError`；server 经 `sources/__init__.py` 导入它，所以整个 server 起不来；CI（Python 3.11）日志里正是这个错误[^ci]。同样换成 `defusedxml` 的 `pubmed.py`、`nature_citation.py` 有 `from __future__ import annotations`，不受影响。Python 3.14 起注解默认延迟求值，在 3.14 上能否导入未实测 | `skills/nature-academic-search/mcp-server/sources/arxiv.py:1-8,243,329`、`skills/nature-academic-search/mcp-server/sources/pubmed.py:3`、`skills/nature-academic-search/mcp-server/sources/__init__.py:5`、`skills/nature-academic-search/mcp-server/academic_search_server.py:16-22`、`.github/workflows/test-skill-tooling.yml:54-57` |
| MCP 启动命令（`uv run --with …`） | 片段里的 `--with` 列表没有 `defusedxml`，而 `requirements.txt` 里有 | `skills/nature-academic-search/config/mcp-snippet.json:5-20`、`skills/nature-academic-search/mcp-server/requirements.txt:6` |
| `nature-polishing`："扫描全文术语、单位、数值精度和声称漂移" | 机器能查的只有术语组、同值不同精度、长度单位（μm/mm/cm/m）三项；"声称漂移"只在提示词里 | `skills/nature-shared/scripts/check_consistency.py:15-26,112,158-163`、`skills/nature-shared/core/consistency-sweep.md:1-25` |
| `nature-reader`："公式渲染、图文对应" | 抽取、裁图、OCR 都写成对 agent 的要求，第一步是"Load the `pdf` skill"，这个 skill 不在本仓；本仓代码只有公式校验器 | `skills/nature-reader/static/fragments/source/pdf-text.md:3`、`skills/nature-reader/static/fragments/source/scanned-pdf.md:3` |
| `nature-paper2ppt`："从科研论文生成中文 PPTX" | 没有生成 PPTX 的代码，SKILL 要求 agent 用 PyMuPDF、Pillow、python-pptx 自己写；目录里没有这几个依赖的声明 | `skills/nature-paper2ppt/static/core/toolchain.md:5-12` |
| `nature-proposal-writer` 的专家审查与去 AI 腔 | 依赖 `professor`、`avoid-ai-writing`、`brainstorming`、`docx` 四个 skill，都不在本仓 | `skills/nature-proposal-writer/SKILL.md:5-8,13,25,117` |
| `nature-citation` 脚本"prefer when internet access is available"；academic-search 的脚本注释与 routing 文档都拿它当"无第三方依赖的单文件"样板 | 从 PR #231（09-24 合并）起导入 `defusedxml`，但 `nature-citation` 目录下没有任何依赖声明。CI 里 citation 的测试步骤排在 academic-search 之后，09-16 起前一步失败、它被跳过，所以 #231 合并时 citation 的测试没有跑[^ci]；即便跑，能导入 `defusedxml` 也只是因为同一个 job 装了 academic-search 的 requirements | `skills/nature-citation/scripts/nature_citation.py:24`、`skills/nature-academic-search/scripts/academic_search.py:8-10`、`skills/nature-academic-search/static/core/routing-and-ops.md:51`、`.github/workflows/test-skill-tooling.yml:70-86` |
| README 装机说明：单装 reader、paper2ppt、polishing、writing 时要连 `nature-shared` 一起装；示例命令单装 `nature-figure` 不带它 | 实际有 10 个 manifest 引 `../nature-shared/`：上面 4 个之外还有 figure、paper-card、response、reviewer、statistics、data（多数是按需引 NMI 格式或一致性扫描）；writing 与 polishing 是在 `always_load` 里引 | `README.md:158,161-166`、`skills/nature-figure/manifest.yaml:84`、`skills/nature-writing/manifest.yaml:8-13` |
| 多份 `evals/evals.json` | 是提示词加期望输出的声明，没有任何代码执行它们；`scripts/tests/` 只读 figure 的那份检查字段；reader 那份的输入文件是作者本机路径 | `skills/nature-reader/evals/evals.json:8`、`scripts/tests/test_nature_figure_collision_audit.py:200` |
| nature-figure 与 figures4papers 说明里写"本仓库 MIT License" | 根 LICENSE 是 Apache-2.0（2026-06-18 由 MIT 改过来[^license]），这两处文字没跟着改 | `skills/nature-figure/README.md:78`、`skills/nature-figure/assets/figures4papers/THIRD_PARTY_NOTICES.md:10-12` |

### 1.3 网页版 natureskills.cn 与仓库的关系

README 顶部写"Nature Skills 网页版：内置 Nature Polishing（论文润色）与 Nature Figure（科研绘图）核心功能"（`README.md:21-25`）。仓库里与网页相关的只有 `index.html`（2827 行），它是 GitHub Pages 的静态介绍页（`yuan1z0825.github.io/nature-skills`），只有多语言切换脚本，全文不含 `natureskills.cn`。

2026-09-27 取页面的结果[^nscn]：根路径 307 跳到 `/agent`，页面标题"科研 Agent · NatureSkills"，站点自述"科研 Skills 发布与交易平台 — 发现、购买和发布科研 Skills、代码与在线工具"；sitemap 里有 `/marketplace`、`/legal/refunds` 与一批作品页（如 `drawio-skill`、`scipilot-figure-skill`、`paper-novelty-design`，也有 `nature-skills` 本身，以及与本组调研同名的 `academic-research-skills`、`ai-research-skills`，见 [academic-research-skills.md](academic-research-skills.md)、[ai-research-skills.md](ai-research-skills.md)；是不是同一项目、由谁上架，未核实）；隐私政策写明"科研 Agent 积分"计费，用户点击发送后"本轮原始对话文本和当轮所选原始附件"会提供给"平台配置的 AI 模型服务商"。页面是客户端渲染，润色与绘图功能本身没取到，也看不到它用的是不是本仓的 SKILL.md。能确定的只有：这是一个闭源、要注册、按积分收费、自己调模型的站点，仓库里没有它的代码。

## 2. 怎么做：主流程

### 2.1 一个 skill 被调起之后

没有入口程序。宿主 agent 按 frontmatter 的 `description` 决定用哪个 skill，读 SKILL.md 后照做。router 型的 SKILL.md 都是同一套四步，以 `nature-writing` 为例：

1. 读 `manifest.yaml` 与 `always_load` 下的全部文件（写作是 4 个共享文件加 3 个本地 core 文件）（`skills/nature-writing/SKILL.md:12-16`、`skills/nature-writing/manifest.yaml:8-17`）。
2. 对每个轴按 `detect:` 提示判值，用一句话告诉用户，"This is a progress update, not an approval gate"（`skills/nature-writing/SKILL.md:18-32`）。
3. 只读选中值映射的片段，"Do **not** read every fragment"（`skills/nature-writing/SKILL.md:34-38`）。
4. 起草；`references/` 按 `on_demand` 条件表再读（`skills/nature-writing/SKILL.md:87-119`、`skills/nature-writing/manifest.yaml:94-139`）。

**manifest 不被任何运行时代码解析**：全仓提到 `manifest.yaml` 的代码只有三个校验脚本（`scripts/validate-*.py`）、`scripts/tests/` 与 image2ppt 的测试、`nature-academic-search/install.sh` 的拷贝清单和 `init_patent_project.py` 的拷贝清单。路由是 agent 读 YAML 后自己判断的，路径也由 agent 自己解析：同一个共享文件，manifest 里写 `../nature-shared/core/reader-workflow.md`（相对 skill 根），`static/core/stance.md` 里写 `../../../nature-shared/core/reader-workflow.md`（相对该文件）（`skills/nature-writing/manifest.yaml:10`、`skills/nature-writing/static/core/stance.md:11`）。

### 2.2 模型怎么调

全部文本由宿主 agent 在它自己的会话里生成，skill 不指定模型、不带 key。脚本调外部模型的三处都是非文本：

| 调用 | 端点与凭据 | 何时走 | 证据 |
|---|---|---|---|
| figure 的 AI 示意图 | `POST https://openrouter.ai/api/v1/images`，`OPENROUTER_API_KEY`；`--api-url` 或 `SCHEMATIC_IMAGE_API_URL` 可换成任何 OpenAI 兼容图像端点；`--dry-run` 只打印请求 | 用户明说要 OpenRouter / GPT Image 2 / 图像生成 API 时，跳过 Python/R 选择 | `skills/nature-figure/scripts/generate_openrouter_schematic.py:137-140,230-242`、`skills/nature-figure/SKILL.md:29-39` |
| image2ppt 的图像编辑 | 优先宿主 agent 暴露的 `image_gen.imagegen` 工具（仓库只称它为 agent tool，没写是哪家宿主；与 `codex-oauth` 并列，是不是 Codex 的内置工具未核实）；其次 `codex-oauth` 读 `~/.codex/auth.json` 调 `https://chatgpt.com/backend-api/codex`；或 `OPENAI_API_KEY` + `OPENAI_BASE_URL` | 重建幻灯片里的复杂位图素材 | `skills/nature-image2ppt/SKILL.md:79-92`、`skills/nature-image2ppt/cli/image2ppt/runtime/image_gen.py:39-52,68-74` |
| image2ppt 的 OCR | `https://paddleocr.aistudio-app.com/api/v2/ocr/jobs`，`PADDLE_OCR_TOKEN`（百度 AI Studio）；没有 token 退到本地只测几何不识字 | 每页文字提示 | `skills/nature-image2ppt/cli/image2ppt/runtime/paddle_text_hints.py:11,32`、`skills/nature-image2ppt/SKILL.md:95-104` |

需要"另一个模型会话"的地方靠宿主的子代理或多次调用，不靠代码：`nature-reviewer` 要求三位审稿人"in a genuinely separate context, subagent, process, or invocation"，做不到就明说不能保证互盲（`skills/nature-reviewer/SKILL.md:19-23`）；`nature-ref-verifier` 超过 20 条拆给并行子代理（`skills/nature-ref-verifier/SKILL.md:59`）；`nature-image2ppt` 的 `run dispatch` 只在 `page_jobs.json` 里记一笔派给谁（agent id、prompt 的 sha256、时间），不起任何进程，起 worker 是宿主的事（`skills/nature-image2ppt/SKILL.md:127-137`、`skills/nature-image2ppt/cli/image2ppt/runtime/record_page_dispatch.py:34-75`）。

### 2.3 数据怎么进出

| skill | 进 | 出 | 写到哪 | 证据 |
|---|---|---|---|---|
| `nature-writing` | 作者给的笔记、结果、图（对话里） | 对话回复：`Draft:`、`Section outline:`、`Assumptions or missing inputs:`、`Claim-evidence map:`、`Why this structure:`、`To redirect me:` 六段；缺证据写 `[Evidence needed: …]` 占位；`task=submission-package` 时换成六段投稿准备格式，用户要 `.tex` 时填 `templates/submission/` 的四个 LaTeX 模板 | 默认不写文件；没有规定 `.tex` 写到哪 | `skills/nature-writing/static/core/output-format.md:3-11,26-35`、`skills/nature-writing/static/fragments/task/submission-package.md:38` |
| `nature-polishing` | 已有文本；排版请求是用户的 LaTeX 工程 | 润色后正文 + `Revision notes:` 3 到 5 条 | 润色不写文件；排版请求直接改用户的 `.tex`，要求编译并看渲染页 | `skills/nature-polishing/static/core/output-format.md:3-7`、`skills/nature-polishing/SKILL.md:90-98` |
| `nature-figure` | 数据文件或绘图脚本 | `figure.svg/.pdf/.tiff`、`.alignment.json`、`.collision-audit.json`；AI 路线出图片 + `*_request_metadata.json` | 绘图路线的文件名由 agent 写的代码定；AI 路线缺省写 `./openrouter_schematic/`，可用 `--outdir` 改 | `skills/nature-figure/static/fragments/backend/python.md:26-39`、`skills/nature-figure/scripts/generate_openrouter_schematic.py:169-199,221` |
| `nature-reader` | PDF、HTML、DOI/arXiv、粘贴文本 | `paper.md`（逐段 Original / 中文 对照）、`source_map.json`（S/C/F/T/E 编号块）、`translation_notes.md`、`assets/` | 用户指定目录 | `skills/nature-reader/static/core/output-contract.md:3-9`、`skills/nature-reader/static/core/workflow.md:19-25` |
| `nature-paper-card` | PDF 或 reader 的 `source_map.json` | `source_bundle.json`、`paper-card.md`（固定 16 节）、`audit-report.json` | `WORKDIR` | `skills/nature-paper-card/SKILL.md:41-44,100,109-114` |
| `nature-paper2ppt` | 论文 PDF 或读书笔记 | `.pptx`、`output/qa_report.md` | 项目本地 `output/` | `skills/nature-paper2ppt/SKILL.md:53,63` |
| `nature-citation` | 稿件文本、单条 claim、DOI、PMID | 一个 `.ris`（或 `.enw` / Zotero RDF），可选 JSON/TSV/HTML | `--output-file` / `--outdir` | `skills/nature-citation/scripts/nature_citation.py:1-6,2248-2251` |
| `nature-academic-search` | 查询词、作者、ORCID、DOI | MCP 工具返回 JSON 字符串；脚本 stdout 一段 JSON，单源失败退非零 | stdout | `skills/nature-academic-search/scripts/academic_search.py:1-40` |
| `nature-proposal-writer` | 题目、方向或已有稿 | `00_scope.md` 到 `05_style_guide.md`、`state.json`、`drafts/`、`exports/`（md + docx） | `<outputs>/researchwrite/<project-slug>/` | `skills/nature-proposal-writer/SKILL.md:41-60` |
| `nature-shared` 一致性脚本 | 若干文本文件 | 发现项到 stdout（文本或 `--json`），`--fail-on-findings` 时有发现退 1 | stdout | `skills/nature-shared/scripts/check_consistency.py:226-269` |

### 2.4 写作侧三个重点 skill

**`nature-writing`**：先写一句话论证"In [system/problem], we show [advance] using [approach], supported by [evidence], with [boundary]"，写不出就告诉用户"论文还没有论证"；建术语表；每段只做一件事（context、gap、approach、result、comparison、mechanism、implication、limitation 之一）；Results 类任务先把每条结果分成 core / support / qualification / robustness 等并分配到正文、图注、SI；动词强度按证据校准；返修只改被点名的段落（`skills/nature-writing/static/core/workflow.md:5-81`）。期刊轴区分旗舰 Nature、Nat Commun、NMI、其他 Nature 子刊与通用，子刊规则不从旗舰推（`skills/nature-writing/manifest.yaml:77-92`）。它引的"Nature 风格"写作规则有两类来源：期刊官方要求（`journal-formats/`）和从已发表论文语料归纳的默认写法，后者在文件里反复声明"not official policy"（`skills/nature-writing/SKILL.md:60-74`）；共享包摘要指南里的同类声明"corpus-derived writing guidance, not official journal requirements"有字符串测试守着（`skills/nature-shared/core/nature-abstract.md:7`、`scripts/tests/test_nature_abstract_guidance.py:8,20-27`）。

**`nature-polishing`**：轴比 writing 少一个 `task`（剩 paper_type、section、language、journal 四个），section 的取值不同，期刊轴没有 `nature-family`（其他 Nature 子刊归 `generic`）；`always_load` 用 `failure-modes.md` 代替 writing 的 `workflow.md`（`skills/nature-polishing/manifest.yaml:7-70`）。改写顺序是"paper type → section job → paragraph logic → claim/evidence/boundary → sentence polish"，结构问题不补内容就修不好时要标出来而不是糊过去（`skills/nature-polishing/SKILL.md:38-48`）。LaTeX 排版请求绕开四个轴直接读 `references/latex-layout.md`（`skills/nature-polishing/SKILL.md:90-98`）。

**`nature-figure` 怎么出图**：

1. 先判是不是 AI 示意图路线（用户明说 OpenRouter / GPT Image 2 / 图像生成 API）；是就读政策与出处要求后调 `generate_openrouter_schematic.py`，产出只算"draft schematic"（`skills/nature-figure/SKILL.md:16-39`）。脚本缺省在用户内容前拼两段：Nature 风格扁平矢量的样式要求，和"不要编数值、p 值、显微结果、机构标志"的约束；`--style` 可替换样式段，`--raw` 加自定义提示时两段都不拼（`skills/nature-figure/scripts/generate_openrouter_schematic.py:32-35,57-72,218-219`）。
2. 否则定 backend：当前请求明说 → 输入文件的语言 → 本任务已定 → `nature_figure_backend.py get` 读 `~/.config/nature-skills/nature-figure.json`；都没有就问一次"Python or R?"并存下来（`skills/nature-figure/SKILL.md:51-56`、`skills/nature-figure/scripts/nature_figure_backend.py:16-20`）。定了之后排他，缺运行时也不许换另一种语言出替代图（`skills/nature-figure/static/core/contract.md:17-31`）。
3. 写图前先填五点契约：核心结论、证据链（每个面板一个推理角色）、版式原型、backend、期刊导出参数；数据不许为了好画而删行（`skills/nature-figure/static/core/contract.md:33-49`）。
4. **图由 agent 写 matplotlib/seaborn 或 ggplot2/patchwork 代码并自己运行**；仓库给一段 rcParams 与导出函数（SVG + PDF + 600 dpi TIFF，`pdf.fonttype 42` 保证文字可编辑）（`skills/nature-figure/static/fragments/backend/python.md:5-39`），另有 `plot_templates.py` 的 volcano、roc、dotplot、marginal、paired 五个 CSV 模板，只有显式 `--demo` 才用模拟数据，否则缺 `--input` 就报错（`skills/nature-figure/scripts/plot_templates.py:1-11,206-210,526,538-585`）。这段 quick-start 要 `from audit_panel_alignment import …`，注释让用户把脚本拷到绘图源码旁边或把 skill 的 `scripts/` 加进 `PYTHONPATH`（`skills/nature-figure/static/fragments/backend/python.md:10-12`）。
5. 导出后必须跑的机器检查：`validate_figure.py` 对源码做 21 项静态检查（字体、字号、色图、矢量导出、分辨率、对数保护、演示数据等，零依赖）；多面板图在最终布局后测每个绘图区矩形，容差 1.5 pt，超差退 1 阻止交付；`audit_pdf_text.py` 读 PDF 内容流查最小字号；`audit_figure_collisions.py` 用 PyMuPDF 读最终 PDF 的几何查文字重叠与裁切（`skills/nature-figure/SKILL.md:76-118`、`skills/nature-figure/scripts/validate_figure.py:1-10,653-679`、`skills/nature-figure/scripts/audit_figure_collisions.py:1-13`）。

### 2.5 文献与假设阶段相关的几个

- **检索**：`nature-academic-search` 首选 MCP 的 `search_papers`（CrossRef、PubMed、arXiv 并发，Scopus 与 ScienceDirect 要 `~/.config/pybliometrics.cfg` 并耗 Elsevier 配额）；无 MCP 时用 OpenAlex 脚本，带作者消歧（`--affiliation`、`--orcid`、`--list-authors`）（`skills/nature-academic-search/static/core/routing-and-ops.md:51-72`）。
- **引文**：`nature-citation` 把稿件切段，每段查 CrossRef，按 Nature/CNS 期刊族过滤，缺名字的作者再按 PMID 回查，导出一个参考文献管理器文件（`skills/nature-citation/SKILL.md:31-35`）。
- **读论文**：`nature-reader` 先建全文 source map 再逐段翻译，长文分页增量写、不许退化成摘要（`skills/nature-reader/static/core/workflow.md:15-43`）；`nature-paper-card` 强制用自带脚本准备材料，明文禁止 agent 临时写抽取脚本（`skills/nature-paper-card/SKILL.md:50,141-148`），并按能否拿到可靠页码分三种定位模式，拿不到就不许写页码（`skills/nature-paper-card/SKILL.md:52-58`）。
- **假设**：没有专门 skill。最接近的三处都是提示词：精读卡第 16 节"Research Ideas"必须过六道门（可追溯到论文的具体局限、可证伪、写明改了什么、写明验证用的对照与变量与证伪结果、至少两条会失败的理由、不许用 novel / first 等词除非做过查新）（`skills/nature-paper-card/references/research-idea-gates.md:1-50`）；文献管线的 gap 分析是四步：至少 3 个来源精确检索并记命中数 → 直接命中为 0 时拆成子体系、命中按直接相关 / 边缘相关 / 无关分三档 → 摘出边缘相关论文的方法与发现 → 写 `outputs/literature/<topic>_gap_report.md`，例子是一个熔盐四元体系，回答的是"这个方向有没有人做过"，不生成假设（`skills/nature-literature-pipeline/references/gap-analysis.md:3-50`）；开题写作状态机的 compose 模式要先建 `02_evidence_table.md` 与 `03_argument_map.md`，章节契约里有"科学问题与研究目标""创新点"（`skills/nature-proposal-writer/references/compose-mode.md:53-160`）。`nature-writing` 的 `paper_type: hypothesis` 片段讲的是怎么写一篇假设驱动的论文，不是生成假设（`skills/nature-writing/static/fragments/paper_type/hypothesis.md:1-14`）。

## 3. 为什么这么设计

### 3.1 router 加静态片段：为了少进上下文

2026-05-26 到 05-30 的一批 PR 把 SKILL.md 从一整篇改成"薄路由 + 按轴加载片段"：`nature-paper2ppt` 从 696 行的单文件变成 71 行路由（PR #45），写作与润色拆成 `static/core/`（总加载）和 `static/fragments/<轴>/`（按值加载），为之后把共用内容提成共享层做准备（PR #37）[^prs]。SKILL.md 里反复出现的"Do **not** read every fragment"就是这个目的（`skills/nature-writing/SKILL.md:38`）。PR 正文写的理由只有两条：按轴只读匹配的片段、给之后提共享层留出平行结构；没有写 token 数或上下文长度。把它对到 agentskills.io 规范"激活时整篇 SKILL.md 进上下文、正文建议 500 行以内、其余文件按需加载"[^spec]，是本文的推断。

### 3.2 共享包：为了让按需安装不断引用

`nature-shared` 原来是仓库级的 `_shared/` 目录，`npx skills add` 只装选中的 skill 时共享文件会丢；PR #121 把它改成可安装的包，并要求单装 reader、paper2ppt、polishing、writing 时连它一起装[^prs]（`README.md:161-166`）。它的 `agents/openai.yaml` 设 `allow_implicit_invocation: false`，只给别的 skill 读（`skills/nature-shared/agents/openai.yaml:5-6`），仓库自己的校验器强制这一条（`scripts/validate-skill-metadata.py:141-144`）。只有两个以上 skill 用到的内容才进共享包（`skills/nature-shared/README.md:33-35`）。

### 3.3 确认门：加上又收回

PR #76（2026-06-18）因为"起草结果不是我想要的"这类反馈，把写作默认流程从"先写再列缺口"翻成"先确认再写"，在 workflow 里加了 3b 确认门。PR #213（09-06）与 #215（09-14）又把它收窄：短请求与追问沿用已定上下文，确认改成"progress update, not an approval gate"，只在会实质改变论证的未决选择上停；同时缩短 15 个 skill 的 description，19 个可触发 skill 的 description 合计从 11835 字符降到 4311 字符（减 63.6%）[^prs]。现状见 `skills/nature-writing/static/core/workflow.md:35-43`。作者自己留了一份小样本观察记录：6 个短请求在隔离上下文里跑，明说"不是基准、不是跨模型评测"（`docs/skill-scope-smoke-evaluation.md:3-14`）。

### 3.4 安装形态反复

- Claude Code 插件：2026-05-06 加 `.claude-plugin/`，06-15 整目录删除；前一天的 issue #72 报的是 `.mcp.json` 里用了 Claude Code 专有的 `${CLAUDE_PLUGIN_ROOT}`，Codex 不展开导致 MCP 起不来，维护者回复"推荐使用mac"，提问者回"和是不是mac无关"[^i72][^plugins]。两个给 Claude Code 加插件的 PR（#70、#83）都没合[^prs]。现在 README 让 Claude Code 用户自己写 subagent 或 slash command 包一层，或用脚本把目录拷进 `~/.claude/skills/`（`README.md:196-268`）。
- Codex：市场元数据 05-26 加、06-15 删、08-31 由 PR #210 以 `.codex-plugin/plugin.json` 加 `.agents/plugins/marketplace.json` 重新加上，PR 里写了用 `codex plugin marketplace add` 走过完整流程[^plugins]。

### 3.5 issue 与 PR 里记下的坑

仓库没有 CHANGELOG 文件，下面取自 issue 与 PR 正文。

| 编号 | 坑 | 怎么处理的 | 证据 |
|---|---|---|---|
| #62（06-06，提交者是 devin-ai-integration 机器人） | `nature_citation.py` 末尾引用两个未定义的变量，最终导出永远跑不到；另外没挂 MCP 的环境里检索不能用 | #64 修 NameError；#65 加无 MCP 的 OpenAlex 检索（两个 PR 正文都引 #62） | [^i62] |
| #74（06-16） | academic-search 改成 router 后，`install.sh` 没拷 `manifest.yaml` 与 `static/`，装出来的 skill 看着在、路由文件缺 | #75 补拷贝；现在 `install.sh` 逐项拷 | [^i74]、`skills/nature-academic-search/install.sh:60-71` |
| #60（06-02） | figure 画出的柱线图有偏移、箭头落在框中间 | 仓库作者回复把 SVG 导入 Illustrator 手调，另一位用户补"还可以导入 ppt"，当天关闭；8 月底加了碰撞审计（#206，08-24）与对齐门（#208，08-27），两个 PR 正文都没引 #60，是不是针对它不能确定 | [^i60][^prs] |
| #97（07-06） | paper2ppt 可用度低：图裁不全、对齐不稳、"AI 味"重 | 核心开发者 Travisma2233 回复"确实做的还有不足"；同日的 #99（"Improve paper2ppt QA"）加了 PPTX 审计脚本，PR 正文没引 #97 | [^i97][^prs] |
| #181（07-31） | reader 生成的 md 里公式是 LaTeX 源码，要回 PDF 看 | e7a9bc0：公式单独成 E 编号块、低置信度显示原图、新增 `validate_reader_math.py` | [^i181] |
| #183（08-01） | `prepare_paper.py` 把缺页码或页码非法的块记成第 1 页，和真第 1 页分不开 | 4312c49：只收正整数页码，其余进 `unlocated_blocks` 并标状态 | [^i183] |
| #66（06-07） | 中文特色强的稿子译出来"中文直译"感重，编辑原话"a direct translation from Chinese" | 仓库作者回复认为编辑的评价"比较片面"、用国外模型翻译应当没问题，06-09 关闭；`zh-to-en` 片段存在，是否针对此改动没查到对应提交 | [^i66] |
| #222、#224、#225、#231（09-15 到 09-23 提，09-16 到 09-24 合并） | 外部贡献者 anupamme 按 bandit 扫描把 arxiv、pubmed、format-converter、nature_citation 的 XML 解析换成 `defusedxml` | #222 合并后 `arxiv.py` 导入失败，main 上 skill 工具测试从 09-16 起持续红；#224、#225、#231 合并时 main 上这个 workflow 已经是红的；#231 合并后那次 main 运行里，citation 的测试步骤因前一步失败被跳过；同一人 09-24 又提了两个安全加固 PR（#233、#234），仍开着 | [^ci][^issues] |

## 4. 跑起来要什么

### 4.1 按 skill 的依赖

| skill | 语言与包 | 系统程序 | 声明在哪 | 证据 |
|---|---|---|---|---|
| writing、polishing、statistics、data、reviewer、ref-verifier、literature-pipeline、experiment-log | 无 | 无 | — | 目录里无 `.py` / `.mjs` / `.R` / `.sh`（reviewer 只有 `tests/` 下的字符串断言测试），见第 1.1 节 |
| `nature-shared` | Python 标准库 | — | 无需声明 | `skills/nature-shared/scripts/check_consistency.py:1-12` |
| `nature-figure` | Python：matplotlib、numpy（模板与 helper）、PyMuPDF（碰撞审计）；或 R：ggplot2、patchwork、svglite、ragg | R 路线要 `Rscript` | `requirements.txt` 只写 PyMuPDF；matplotlib、numpy、R 包都没有声明 | `skills/nature-figure/requirements.txt:1`、`skills/nature-figure/scripts/figure_safety.py:8`、`skills/nature-figure/scripts/plot_templates.py:31-37` |
| `nature-reader` | 标准库（校验器）；抽取依赖宿主的 `pdf` skill | 扫描件要 OCR | 无 | `skills/nature-reader/static/fragments/source/scanned-pdf.md:3` |
| `nature-paper2ppt` | PyMuPDF、Pillow、python-pptx（agent 自己写代码用） | LibreOffice 可选 | 无 | `skills/nature-paper2ppt/static/core/toolchain.md:5-14` |
| `nature-paper-card` | 标准库 + PyMuPDF（懒加载） | — | 无 | `skills/nature-paper-card/scripts/prepare_paper.py:152` |
| `nature-academic-search` | MCP server：mcp、requests、toml、lxml、pybliometrics、defusedxml；无 MCP 脚本：`academic_search.py` 标准库，`format-converter.py` 要 requests、defusedxml | `uv`（MCP 启动片段） | `mcp-server/requirements.txt`；`scripts/` 的依赖没有声明；`install.sh` 用全局 `pip install`，失败只打印 WARNING 继续装 | `skills/nature-academic-search/mcp-server/requirements.txt:1-6`、`skills/nature-academic-search/scripts/format-converter.py:31-32`、`skills/nature-academic-search/install.sh:47-55` |
| `nature-citation` | defusedxml（09-24 起） | — | 无 | `skills/nature-citation/scripts/nature_citation.py:24` |
| `nature-proposal-writer` | python-docx（`build_proposal_docx.py`） | — | 无 | `skills/nature-proposal-writer/scripts/build_proposal_docx.py:14-17` |
| `nature-response` | Python 标准库 | — | 无需声明 | `skills/nature-response/scripts/check_package_consistency.py:4-12` |
| `nature-image2ppt` | pypdfium2、Pillow、numpy、requests、PyYAML、openai（Python 3.10+） | Linux/macOS 要 LibreOffice（Office 输入转换与渲染 QA），Windows 首选 PowerPoint 自动化；公式页要 TeX 引擎加 dvisvgm / pdf2svg / ImageMagick 之一，缺了公式页硬失败；中文页要 CJK 字体 | `requirements.txt` 与 `cli/pyproject.toml` | `skills/nature-image2ppt/requirements.txt:1-7`、`skills/nature-image2ppt/references/runtime-dependencies.md:36-48`、`.github/workflows/test-skill-tooling.yml:65-68` |
| `nature-downloader` | Node.js 22+；Python：pdfplumber、pypdf、PyYAML、jsonschema | Chrome 开远程调试 | `requirements.txt`；Node 与 Chrome 的要求只写在 SKILL frontmatter 的 `metadata.compatibility` 里 | `skills/nature-downloader/requirements.txt:1-4`、`skills/nature-downloader/SKILL.md:4-5` |
| `nature-paper-to-patent` | python-docx、matplotlib、Pillow、pypdf、mammoth、latex2mathml、python-pptx；可选 Playwright | Node + `@mermaid-js/mermaid-cli`（可 npx 临时拉） | 两份 requirements、一份 package.json | `skills/nature-paper-to-patent/scripts/disclosure/mermaid_render.py:8-15` |

仓库自己的安装脚本不装 Python 依赖，README 让用户按需 `python -m pip install -r …`（`README.md:368-378`）。全仓只有 `academic_search.py` 一个脚本带 PEP 723 块，且块里没有依赖、没有锁文件（`skills/nature-academic-search/scripts/academic_search.py:1-4`）。

### 4.2 模型、key 与外部服务

- **文本模型**：宿主 agent 自己的登录，skill 不管。
- **要单独凭据的**：`OPENROUTER_API_KEY`（figure 示意图）；`OPENAI_API_KEY` + `OPENAI_BASE_URL` 或 `~/.codex/auth.json`（image2ppt 图像）；`PADDLE_OCR_TOKEN`（image2ppt OCR）；`PUBMED_EMAIL` 与可选 PubMed key、`~/.config/pybliometrics.cfg` 的 Elsevier key（academic-search）；Elsevier / Springer Nature / IEEE 出版商 key 与学校图书馆入口（downloader）。image2ppt 的 `config.yaml`（含 key）默认写在 skill 目录自己下面，`.gitignore` 挡住（`skills/nature-image2ppt/cli/image2ppt/runtime/runtime_env.py:40-62`、`skills/nature-image2ppt/config.example.yaml:1-4`）。
- **免 key 的公开接口**：CrossRef、OpenAlex、PubMed E-utilities、arXiv、DOI 解析、Europe PMC、Unpaywall（要填邮箱，没填就不查）、国知局公布公告站（Playwright 爬）（`skills/nature-downloader/scripts/lib/open-access-provider.mjs:48,77-79`）。
- **会把稿件内容发出去的**：OpenRouter 路线，参考文档自己写了"Do not send confidential manuscript content to OpenRouter without user permission"（`skills/nature-figure/references/openrouter-image-generation.md:34-41`）。

### 4.3 算力与操作系统

没有 GPU 需求；最重的是 image2ppt 的 LibreOffice 渲染与 LaTeX 公式。操作系统：README 装机步骤以 macOS/Linux shell 为主；issue #26 问 Windows 教程、#72 维护者回复"推荐使用mac"；代码层面 image2ppt 在 CI 里跑了 ubuntu、macOS、Windows 三平台矩阵（只跑 9 个不需要 Office 渲染的可移植测试文件，完整测试只在 ubuntu 上跑），paper2ppt 的工具链要求"must work on macOS, Linux, and Windows"，patent 修过 Windows 下带空格路径的 Mermaid 渲染（PR #212）（`.github/workflows/test-skill-tooling.yml:96-98,120-161`、`skills/nature-paper2ppt/static/core/toolchain.md:12`）。figure 的两处命令写的是相对仓库根的路径（`python skills/nature-figure/scripts/…`、`source("skills/nature-figure/scripts/panel_alignment.R")`），用户当前目录不是本仓库根时这两处解析不到（按路径写法推断，未实测）；共享包的清单则明写"resolve relative to the nature-shared package directory, never the user working directory"（`skills/nature-figure/SKILL.md:103`、`skills/nature-figure/static/fragments/backend/r.md:10`、`skills/nature-shared/manifest.yaml:52`）。

### 4.4 与 Codex、Claude Code 的兼容点

| 项 | Codex | Claude Code | 证据 |
|---|---|---|---|
| 安装 | 仓库是一个 Codex 插件市场（`.codex-plugin/plugin.json` + `.agents/plugins/marketplace.json`）；或 `update-codex-skills.sh` 用 rsync 拷到 `~/.codex/skills/` 并逐目录 diff 校验 | 无插件；自己写 subagent / slash command 指向 SKILL.md，或用 `autoupdate-skills.sh` 拷进 `~/.claude/skills/` | `.codex-plugin/plugin.json:1-38`、`scripts/update-codex-skills.sh:5-16,129,279-280`、`README.md:196-268` |
| 每个 skill 的 UI 元数据 | 每个目录一份 `agents/openai.yaml`（display_name、short_description、`$skill` 形式的 default_prompt），仓库校验器强制 | 不读这个文件 | `scripts/validate-skill-metadata.py:88-145` |
| 自动更新 | Codex `SessionStart` hook，同步执行，靠 1 小时节流与断网跳过 | `SessionStart` hook，`async: true` | `README.md:283-313,394-429` |
| 只在一家有的能力 | image2ppt 的 `codex-oauth` 直接读 `~/.codex/auth.json`；首选的 `image_gen.imagegen` 仓库称为 agent tool，属于哪家宿主未写明 | — | `skills/nature-image2ppt/SKILL.md:79-92`、`skills/nature-image2ppt/references/manifest-schema.md:68-70` |
| MCP | academic-search 的 `mcp-snippet.json` 用 `uv run --no-project` | `install.sh` 写 `~/.claude/.mcp.json`（`python3 …/academic_search_server.py`）与 `settings.json`，skill 装成 `~/.claude/skills/academic-search`，目录名与 frontmatter 名 `nature-academic-search` 不同 | `skills/nature-academic-search/config/mcp-snippet.json:1-24`、`skills/nature-academic-search/install.sh:7-10,76-110` |
| 两家都依赖宿主的 | 子代理（reviewer、ref-verifier、image2ppt）；在宿主 shell 里跑 python / Rscript / node；`../nature-shared/` 要求共享包与 skill 装在同一级目录 | 同左 | `skills/nature-reviewer/SKILL.md:21`、`README.md:442` |

## 5. 和平台对照

### 5.1 平台这三个阶段现在有什么

- 七个阶段里只有设计、实验、分析、验证有"步骤"能力；文献、假设、写作没有。研究助理的指南原话："文献、假设、写作三个阶段还没有步骤……你自己写：`ai4sci output new <stage> --title <一句>`"（`platform/coordinator/README.md:64`）。
- 阶段主文件只定了文献的 `sources.md`（助理手写），假设与写作待第一个能力定名（`platform/framework/capabilities/__init__.py:45-52`、纲领 P-20）。
- 文献阶段的做法是助理用 CLI 自带的 WebSearch / WebFetch 找材料、手写 `sources.md`、用 `download` skill 拉材料（`platform/coordinator/README.md:120-130`、`platform/backends/claude_code.py:42`）。
- 通用 skill 只有两个：`pdf`（论文 PDF → `paper.md` + `images/` + `structured.json`，pymupdf4llm，不做 OCR）与 `download`（git、单文件、HF 拉进 `materials/`）；领域包里另有一个只有说明、没有脚本的 `petab`（`platform/docs/add-a-skill.md:87-90`、`platform/skills/pdf/SKILL.md:4`）。平台里没有文献检索、引文核对、参考文献导出、绘图、写作、润色相关的任何代码（内仓 `git grep -i` crossref、openalex、pubmed、bibtex，唯一命中是 `projects/boehm-nll` 示例数据里的一条 PubMed 链接）。

### 5.2 它多了什么、和平台重叠什么

| 方面 | 平台现有 | nature-skills 有 | 关系 | 证据 |
|---|---|---|---|---|
| 论文 PDF 解析 | `pdf` skill，出 `paper.md` / `structured.json` / `images/`，无 OCR | reader 三处写"先 load `pdf` skill"（包括扫描件的 OCR 指导），这个 `pdf` 不在本仓；downloader 在抽取失败时提"local `pdf` skill"；paper2ppt 不引它，要 agent 直接用 PyMuPDF；reader 自己的产出也叫 `paper.md`（双语对照，内容不同）；paper-card 自带 `prepare_paper.py`（PyMuPDF） | 重叠，且同名；reader 期望的 `pdf` skill 要能做 OCR，平台的不做 | `skills/nature-reader/static/fragments/source/pdf-text.md:3`、`skills/nature-reader/static/fragments/source/scanned-pdf.md:3`、`skills/nature-reader/static/core/output-contract.md:38`、`skills/nature-downloader/references/delivery-verification-and-failures.md:66`、`skills/nature-paper2ppt/static/core/toolchain.md:7`、`platform/skills/pdf/SKILL.md:4` |
| 拉材料 | `download`（git / 文件 / HF） | `nature-downloader`（OA、出版商 API、CNKI 与机构登录态） | 覆盖对象不同：平台拉代码与数据，它拉论文全文 | `platform/docs/add-a-skill.md:89`、`skills/nature-downloader/SKILL.md:10-16` |
| 文献检索 | 靠 CLI 自带联网工具，无脚本 | academic-search 的 MCP 与 OpenAlex 脚本；citation 的 CrossRef 脚本；ref-verifier 提示词 | 平台没有，它多出来 | `platform/coordinator/README.md:120`、第 1.1 节 |
| 文献阶段主文件 | `sources.md` | 无对应命名；产出是 RIS、JSON、reader 包、精读卡 | 不对应 | `platform/framework/capabilities/__init__.py:47`、第 2.3 节 |
| 假设 | 无 | 精读卡第 16 节六道门、gap 分析、开题状态机（都是提示词） | 平台没有 | 第 2.5 节 |
| 写作与润色 | 无 | writing、polishing、shared 约 7800 行 Markdown 提示词；统计、数据可用性、审稿、返修 | 平台没有 | 第 1.1 节 |
| 绘图 | 无 | figure 的模板与四个 QA 脚本；OpenRouter 示意图 | 平台没有 | 第 2.4 节 |
| 数字核对 | `verify` 能力做数字回溯（零模型） | `check_consistency.py` 只查术语变体、同值不同精度、长度单位写法，不回溯来源 | 对象不同 | `platform/coordinator/README.md:60`、`skills/nature-shared/scripts/check_consistency.py:215-223` |
| 模型评审 | P-2：派隔离新会话，尚未实现 | reviewer 用提示词要求宿主开独立上下文 | 平台没有 | 纲领 P-2、`skills/nature-reviewer/SKILL.md:21` |

### 5.3 格式：规范、它自己的校验器、平台三方对照

| 规则 | agentskills.io 规范[^spec] | 它自己的校验器 | 平台 `library.py` | nature-skills 现状 |
|---|---|---|---|---|
| frontmatter 字段 | name、description、license、compatibility、metadata、allowed-tools（实验性） | 允许 name、description、license、metadata、allowed-tools；**不允许 compatibility** | 允许 name、description、license、compatibility、metadata；**不允许 allowed-tools** | 没有人用 compatibility 与 allowed-tools；downloader 把 compatibility 塞进 metadata（`skills/nature-downloader/SKILL.md:4-5`、`scripts/validate-skill-metadata.py:31-38`、`platform/framework/skills/library.py:26`） |
| name 等于目录名 | 必须 | 有一条豁免：`nature-proposal-writer` → `researchwrite` | 必须 | 1 个不符（`skills/nature-proposal-writer/SKILL.md:2`、`scripts/validate-skill-metadata.py:30`、`platform/framework/skills/library.py:190-191`） |
| metadata 是字符串到字符串 | 必须 | 不查 | 查 | 3 个嵌套了 `hermes` 字典：experiment-log、literature-pipeline、proposal-writer（`skills/nature-literature-pipeline/SKILL.md:6-11`、`platform/framework/skills/library.py:205-209`） |
| 正文 500 行以内 | 建议 | 不查 | 强制 | 全部符合，最长 downloader 345 行 |
| 目录外引用 | 建议从 skill 根写相对路径、只引一层 | 只允许 `../nature-shared/` 一种出目录 | 不查引用；`show` 只给目录路径、正文与 `references/` 顶层文件名 | 10 个 skill 的 manifest 引 `../nature-shared/`（`scripts/validate-skill-metadata.py:181-195`、`platform/framework/cli/skill.py:41-57`） |
| 脚本 | 自包含或写清依赖；语言随宿主 | 不查 | 只认 `scripts/*.py`，每个要 PEP 723 块与 `.lock`，`uv run --locked --offline` 起 | 12 个目录的 `scripts/*.py` 全无锁；另有 `cli/`、`mcp-server/`、`src/`、`.mjs`、`.R` 不在平台的识别范围（`platform/framework/skills/library.py:147-150,218-228`、`platform/framework/skills/run.py:21`） |
| 额外文件 | 允许任意 | 要求 README.md、README_EN.md、manifest.yaml、agents/openai.yaml | 不管 | 每个目录都有这四样 |
| 坏一个的后果 | — | 校验失败 | 整库报错，清单一个都不给 | —（`platform/framework/skills/library.py:110-132`） |

照这张表逐个算（只看 frontmatter 与 `scripts/*.py` 两条门），原样放进平台 `skills/` 时能过 `load_skill` 的是 6 个没有脚本、metadata 平铺的目录：writing、polishing、statistics、data、reviewer、ref-verifier。不过的 14 个：12 个因为 `scripts/*.py` 没有 PEP 723 块或锁（academic-search、citation、downloader、figure、image2ppt、paper-card、paper-to-patent、paper2ppt、proposal-writer、reader、response、shared），3 个因为 metadata 嵌套（experiment-log、literature-pipeline、proposal-writer），1 个因为名字（proposal-writer），有重叠。能过的 6 个里，writing 与 polishing 在 `always_load` 里引 `../nature-shared/` 的 4 个 core 文件，statistics、data、reviewer 按需引它的 NMI 格式或一致性扫描，只有 ref-verifier 不引；而 `nature-shared` 自带脚本、自己过不了 `load_skill`，放进同一个 `skills/` 会让整库报错，不放则这 5 个的共享引用落空。另外平台测试要求有脚本的 skill 正文里出现 `ai4sci skill run`，全仓零处（`platform/tests/test_skills.py:95-100`）。上面 6 过 14 不过的结果，是用内仓 venv 的 Python 对 `vendor/nature-skills/skills/` 下 20 个目录逐个调 `framework.skills.library.load_skill` 得到的（只读，没有复制进 `skills/`，没有跑 `make skills` 与 nature-skills 的代码）。

### 5.4 接进来会碰到的平台规则

只列碰到的事实，不下结论。

| 平台规则 | 碰到的事实 | 证据 |
|---|---|---|
| P-1 执行层是唯一写代码的；框架不调模型 | 它的文本全由宿主 agent 写，框架侧不需要调模型；但 figure、image2ppt 的脚本自己调外部图像与 OCR 接口，这些脚本若进平台是 skill 脚本，不在 `framework/` 下 | 第 2.2 节表；纲领 P-1 的判据是 `framework/` 下 grep 不到模型 API 名 |
| P-25 底座归人（模型与登录在 `~/.config/ai4sci/agents.yaml`） | 图像接口要 `OPENROUTER_API_KEY` / `OPENAI_API_KEY` / `PADDLE_OCR_TOKEN`，不经 agent 登录；image2ppt 的 `codex-oauth` 直接读 `~/.codex/auth.json` 调 ChatGPT 后端 | `skills/nature-image2ppt/cli/image2ppt/runtime/image_gen.py:51-52,68-74` |
| P-22 加载不靠 agent 原生机制；框架把清单拼进 prompt，全文用 `ai4sci skill show` | router 型 skill 要 agent 自己读 `manifest.yaml`、`static/…`、`../nature-shared/…`；`show` 打印 skill 目录的绝对路径、SKILL.md 正文与 `references/` 顶层文件名，不打印 `manifest.yaml` 与 `static/`。执行层的 Claude Code 适配器给 allowed_paths 的 Edit / Write 规则和会话工作目录（多数能力就是产出目录）的 Read 规则，研究助理可写整个项目、额外可读的只有流程库两层与需求模板库，skill 目录都不在里面；Codex 适配器每次起会话都把 Codex 原生 skill 关掉 | `platform/framework/cli/skill.py:41-57`、`platform/backends/claude_code.py:151-155`、`platform/framework/capabilities/analysis/analyze.py:54`、`platform/framework/chat/scope.py:39-43`、`platform/backends/codex.py:25-29` |
| P-22 脚本 PEP 723 + 锁 + `uv run --locked --offline` | 见 5.3；Node、R、CLI 包形态的脚本不在这套机制里 | `platform/framework/skills/run.py:1-23` |
| P-14 CLI 主导：不裸跑 python；执行层命令前缀只有 `ai4sci skill`，研究助理只有 `ai4sci` | 它的 SKILL.md 让 agent 直接跑 `python <skill>/scripts/…`、`Rscript`、`node`、`uv run`、`npx`；figure 的出图本身就是 agent 运行自己写的绘图代码；paper2ppt 是 agent 运行自己写的 python-pptx。两家适配器落实这条前缀的方式不同：Claude Code 在 dontAsk 下按 `Bash(ai4sci skill *)` 白名单放行，别的写命令被拒（注释说只读的 grep / ls / wc 本就自动放行）；Codex 没有按命令的白名单，`ai4sci` 在沙箱外跑，别的命令留在沙箱里，只能写工作区、不能联网 | `platform/framework/skills/__init__.py:37`、`platform/framework/chat/guide.py:28`、`platform/backends/claude_code.py:149-150`、`platform/backends/codex.py:16-22,33`、`skills/nature-figure/SKILL.md:102-106` |
| P-20 阶段主文件；假设、写作待第一个能力定名；skill 不开产出目录 | writing、polishing 默认产出是对话回复（例外见第 2.3 节）；reader 的 `paper.md` 与平台 `pdf` skill 的 `paper.md` 同名、内容不同；proposal-writer 自定 `<outputs>/researchwrite/<slug>/` 的目录结构与 `state.json` | 第 2.3 节表 |
| P-13 文档即接口：名字是角色名词、版本在文件里、一个名字一个生产者 | 同上 `paper.md` 两个生产者；paper-card 缺省写 `paper-card.md`；proposal 的 `00_scope.md` 到 `05_style_guide.md` 带两位序号前缀（纲领列的禁项是模型名、日期、轮次，没提序号） | `skills/nature-paper-card/SKILL.md:100`、`skills/nature-proposal-writer/SKILL.md:48-53` |
| P-2 评审上下文隔离（模型评审未实现） | reviewer 把"独立上下文"写成对宿主的要求，做不到就在报告里声明 | `skills/nature-reviewer/SKILL.md:21` |
| P-11 领域 skill 只进执行层、通用 skill 两层都有 | 它的 skill 按任务分（写作、绘图、检索），没有按学科分；学科差异放在各 skill 的 `paper_type` 片段里 | `skills/nature-paper2ppt/manifest.yaml:19-41` |
| P-15 项目边界；P-23、P-25 配置归人的一份文件 | figure 把 backend 偏好写到 `~/.config/nature-skills/nature-figure.json`；image2ppt 把含 key 的 `config.yaml` 默认写在 skill 目录里；downloader 把出版商凭据与学校配置写到用户目录 | `skills/nature-figure/manifest.yaml:35-43`、`skills/nature-image2ppt/cli/image2ppt/runtime/runtime_env.py:40-62`、`skills/nature-downloader/scripts/lib/credentials.mjs:8-14` |
| P-7 fail-closed | academic-search 规定脚本失败两次后"fall back to manual generation from MCP-fetched metadata"；patent 的 Mermaid 渲染失败"不中断"、保留原代码块继续导出；figure 的对齐与碰撞审计失败是阻断交付的 | `skills/nature-academic-search/static/core/routing-and-ops.md:76-78`、`skills/nature-paper-to-patent/scripts/disclosure/mermaid_render.py:15`、`skills/nature-figure/SKILL.md:108-113` |
| P-14 联网只用 CLI 自带工具 | 检索类脚本自己发 HTTP（CrossRef、OpenAlex、PubMed、arXiv）；平台现有 `pdf`、`download` 脚本也自己联网，`--offline` 只管依赖解析。Codex 下只有经 `ai4sci skill run` 起的脚本在沙箱外、能联网，agent 直接敲的 `python …` 在沙箱里断网 | `platform/framework/skills/run.py:6-8`、`platform/backends/codex.py:16-22,33` |

## 6. 成熟度

### 6.1 测试

| 位置 | 数量 | 测的是什么 | 证据 |
|---|---|---|---|
| `scripts/tests/`（CI 的 content contracts） | 109 个 | 约一半（9 个文件 55 个）是对 md 文件做"某句话在不在"的字符串断言，如摘要指南必须含 "corpus-derived writing guidance, not official journal requirements"；另一半是 figure 对齐（24）与碰撞审计（8）的几何测试、star 曲线脚本（10）、元数据与 workflow 校验器自测（12） | `scripts/tests/test_nature_abstract_guidance.py:20-27`、`scripts/tests/test_nature_figure_panel_alignment.py:113-140` |
| `nature-image2ppt/tests` | 168 个 | 状态机、路径约束、渲染、并发派发；三平台矩阵只跑其中 9 个文件 | `.github/workflows/test-skill-tooling.yml:96-98,120-161` |
| `nature-downloader/tests` | 108 个 JS（bun test）+ 10 个 Python | 路由、元数据、PDF 原子写入、凭据 | `.github/workflows/test-skill-tooling.yml:88-91,163-175` |
| `nature-academic-search/mcp-server/tests` | 43 个 | 各数据源解析与 MCP 工具；另有 `test_elsevier_live.py` | `.github/workflows/test-skill-tooling.yml:80-83` |
| figure / citation / paper-card / patent / shared | 13 / 9 / 7 / 10 / 5 个 | 各自脚本 | `.github/workflows/test-skill-tooling.yml:84-119` |
| reviewer、response | 4 / 11 个 Python | reviewer 的 4 个与 response 的 4 个是对 SKILL.md 的字符串断言（如必须含 "genuinely separate context"）；response 另 7 个测 `check_package_consistency.py` | `skills/nature-reviewer/tests/test_reviewer_instruction_contracts.py:21-27`、`skills/nature-response/tests/test_package_consistency.py:10-15` |
| reviewer、response、writing 的 `tests/*.md` | 4 / 11 / 1 份 | 人工对照的场景与评分表，文件自己写"not an executed model benchmark" | `skills/nature-writing/tests/scoped-drafting.md:3-4`、`skills/nature-response/tests/rubric.md:1-3` |
| writing、polishing、reader、paper2ppt、statistics、data 的行为 | 0 | 没有任何会执行提示词、比较输出的测试；`evals.json` 不被执行 | 第 1.2 节 |
| 上面 `test-skill-tooling.yml` 里 python-tests job 的部分（academic-search、citation、downloader Python、figure、image2ppt 完整、paper-card、patent、response、reviewer、shared） | — | 09-16 起在 main 上：academic-search 这一步收集阶段就报错中断（43 个一个没跑），后面 9 步全部 skipped；downloader 的 bun、image2ppt 三平台可移植部分、安装同步测试这几个独立 job 仍是绿的 | [^ci]、`.github/workflows/test-skill-tooling.yml:80-118` |

### 6.2 CI

8 个 workflow：content contracts、skill tooling（Python 多目录、image2ppt 三平台矩阵、downloader 的 bun、安装脚本同步测试）、元数据、README 中英镜像、技能索引、workflow 路径过滤、仓库校验，以及每三天更新 star 曲线的机器人（`.github/workflows/` 下 8 个 yml）。测试依赖以 `-c .github/requirements-ci.txt` 约束安装，这个文件钉了 48 个包的版本，但 numpy、matplotlib、openai、PyMuPDF、defusedxml 不在里面、不钉（`.github/requirements-ci.txt:1-3`、`.github/workflows/test-skill-tooling.yml:70-78`）；设了 Python 版本的 workflow 都用 3.11，只有 image2ppt 的矩阵另跑 3.10 与 3.12；actions 按 commit SHA 钉（`.github/workflows/test-skill-tooling.yml:52`）。当前状态：main 上 "Test skill tooling" 从 2026-09-16（c17a4c9，合并 #222）起连续 6 次失败，最近一次 2026-09-24（351f619）失败在 "Test nature-academic-search"，错误是 `module 'defusedxml.ElementTree' has no attribute 'Element'`，同 job 后面 9 个测试步骤 skipped[^ci]；其余 workflow（content contracts、元数据、索引、仓库校验等）在 main 上最近几次都是 success；HEAD 9e2d90e 只改了 README 图片，没触发 skill tooling 这个 workflow。

### 6.3 发版与维护节奏

- 0 个 release、0 个 tag、没有 CHANGELOG；版本号只写在各 `manifest.yaml`（如 polishing 6.6.0、writing 1.5.0、figure 2.8.0）和 `.codex-plugin/plugin.json` 的 0.1.0[^repo]。
- 2026-04-24 建仓，到 09-25 共 858 个提交，其中 312 个是 star 曲线机器人；人工提交 546 个、37 个作者，按月 4 月 19、5 月 119、6 月 95、7 月 205、8 月 72、9 月 36；前两位是创建者（220）与核心开发者 Travisma2233（195）[^commits]。
- 31 个 issue 全部关闭；198 个 PR 中 164 个合并、32 个未合、2 个开着（均为 09-24 的安全加固）[^issues]。
- 44,699 star、2,346 fork（2026-09-27）[^repo]。README 前部有代充值与成品号服务、知识星球、商务合作等运营内容（`README.md:53-88`）。

### 6.4 许可证

- 根目录 Apache-2.0（2026-06-18 提交 54eadc6 由 MIT 改为 Apache-2.0[^license]），`.codex-plugin/plugin.json:11` 同。要点：可商用、修改、再分发；附带专利授权；再分发要保留许可证文本与版权声明，改过的文件要标明改动；没有 NOTICE 文件。
- 目录内另有 MIT：`skills/nature-downloader/LICENSE`（baihe26）、`skills/nature-image2ppt/LICENSE`（版权人 Image2PPT contributors 与 ningzimu；README 与 manifest 说实现同步自 Paul-Jeo/Image2PPT，`skills/nature-image2ppt/manifest.yaml:8`）、`skills/nature-paper-to-patent/references/disclosure/patent-disclosure-skill-MIT-LICENSE.txt`；三个 SKILL frontmatter 写 `license: MIT`（experiment-log、literature-pipeline、proposal-writer）。
- `skills/nature-figure/assets/figures4papers/`（约 28 MB，占仓库体积大头）来自无许可证的上游，仓库自己的说明写明"does not grant permission to copy, modify, redistribute"（`skills/nature-figure/assets/figures4papers/THIRD_PARTY_NOTICES.md:8-17`）。
- `validate_figure.py` 与 `plot_templates.py` 注明规则与模板思路来自 Apache-2.0 的 academic-figure-skill（`skills/nature-figure/scripts/validate_figure.py:8-9`、`skills/nature-figure/scripts/plot_templates.py:8-10`）。

## 7. 还没弄清的问题

1. **写作类提示词的实际效果**：仓库里没有任何执行过的对比评测，只有 6 条短请求的观察记录。它在我们的真稿子上能省多少改稿量，只能靠 #188 实测回答。
2. **natureskills.cn 用的是不是本仓的 SKILL.md**，用哪家模型，收费多少：页面客户端渲染，未登录取不到。
3. **执行层能不能读到 skill 目录下的其他文件**：Claude Code 适配器只给会话工作目录的 Read 规则（`ai4sci skill show` 会把 skill 目录的绝对路径打出来），但 `platform/backends/claude_code.py:149-150` 的注释说 dontAsk 下只读的 Bash（grep、ls、wc）自动放行；router 型 skill 在执行层里能否读到 `manifest.yaml` 与 `static/`，Codex 沙箱对工作区外的读是否放行，都未实测。
4. **`defusedxml` 能否被 MCP 启动片段的传递依赖带进来**：片段的 `--with` 列表没有它，mcp / pybliometrics 等是否间接依赖它未查；CI 的约束文件里没有 `defusedxml`，但那个文件连 numpy、openai 也没列，不是完整的解析结果，推不出结论。即便带进来了，`arxiv.py` 在 Python 3.13 及以下的导入错误仍在；Python 3.14 注解延迟求值后能否正常导入、运行时有没有别处用到 `ET.Element`，未实测。
5. **"Nature 风格"规则的出处有多扎实**：共享包里的摘要、引言、Results/Discussion 指南自称从 NMI 与旗舰 Nature 已发表论文归纳、Nat Commun 2025 语料有词频统计；语料规模、抽样方式、统计脚本仓库里都没有，只有结论文本。
6. **figure 出图在无显示器环境、中文字体下的表现**：`plot_templates.py` 设了 `mpl.use("Agg")`，但 agent 自己写的绘图代码没有这层保证；字体回退到 DejaVu Sans 时 5 pt 字号门会不会误报，未跑。
7. **中文直译问题（#66）是否改过**：issue 已关，`zh-to-en` 片段里有没有针对它的改动，没有逐提交追。
8. **README 里"Stable / Beta / Draft"的判定依据**：定义是"已在真实学术内容上验证"，但文献管线与文献核验两个零代码目录标 Stable，验证记录在哪没找到。
9. **子代理依赖在平台里怎么落**：reviewer 的互盲、ref-verifier 的并行、image2ppt 的多页 worker 都靠宿主开子代理。已查到的：Claude Code 适配器给执行层的 `--allowedTools` 只有 Edit / Write / Read / `Bash(ai4sci skill *)` / WebSearch / WebFetch，没有子代理工具，dontAsk 下不在白名单的工具被拒（`platform/backends/claude_code.py:40-42,151-159`）；Codex 适配器的事件表里有 `collab_tool_call`，没看到关掉它的配置（`platform/backends/codex.py:38-40,116-117`）。两家实际能不能开子代理，未实测。
10. **`install.sh` 写的 MCP 配置 Claude Code 读不读**：它把 server 写进 `~/.claude/.mcp.json` 并往 `~/.claude/settings.json` 的 `enabledMcpjsonServers` 加名字（`skills/nature-academic-search/install.sh:10,73-133`）；Claude Code 的 `.mcp.json` 是否会从 `~/.claude/` 这个位置读，没有查官方文档、未实测。
11. **academic-search 清单里 11 个外部工具名从哪来**：扩展检索标"paper-search MCP"、PubMed 工具没标来源，仓库没有配置这两个 server，issue 与 PR 里也没找到讨论；和同目录调研的 paper-search-mcp 只对上 3 个名字。

## 8. 调研方法

- 浅克隆到外层 `vendor/nature-skills`（gitignore 挡住），提交 9e2d90e，工作树 78 MB，其中 figure 目录 34 MB。
- 逐个读了 20 个 SKILL.md、全部 `manifest.yaml`、写作 / 润色 / 共享包的 core 文件、figure 与 reader 与 paper2ppt 与 paper-card 的 core 与主要 references；脚本读了头部、导入、参数表与关键函数，按导入与 URL grep 了全部外部依赖与外部主机；统计了每个目录的 md 行数、代码行数、测试数。
- 用仓库自带校验器的规则、agentskills.io 规范、平台 `library.py` 的规则对 20 个 frontmatter 逐个做了比对（Python 读 YAML，不跑项目代码）。
- 用 gh api 取了仓库元数据、全部提交、全部 issue 与 PR、关键 PR 正文、插件目录与 LICENSE 的文件历史、CI 最近的运行与一次失败日志。
- 用 curl 取了 natureskills.cn 的首页、sitemap、manifest、关于页与两份法律文本。
- 没有找到与本仓对应的论文。没有安装任何依赖、没有运行任何 nature-skills 代码。
- 复查（同日，另一人）：逐条打开文中的 `文件:行` 核对；独立重搜了"零调用文本模型""零代码""工具名零命中""MCP 导入失败""平台命令白名单"几条否定判断；用内仓 venv 的 Python 对 20 个目录调平台的 `load_skill`（只读平台代码，不跑 nature-skills 代码）；用 gh api 重取了 CI 运行的 job 与 step 结论、失败日志、issue 评论与 PR 正文；用 curl 复核了 natureskills.cn 的跳转、标题、sitemap 与隐私政策原文；对照了同目录调研克隆的 paper-search-mcp（808e462）的工具名。

[^ci]: GitHub Actions run 35950391382（main，351f619，2026-09-24）"Test skill tooling" 的失败日志：`tests/test_sources.py` 与 `tests/test_elsevier_live.py` 收集阶段 `AttributeError: module 'defusedxml.ElementTree' has no attribute 'Element'`；同一次运行的 python-tests job 里，"Test nature-academic-search" 之后的 9 个步骤（citation、downloader Python、figure、image2ppt 完整、paper-card、patent、response、reviewer、shared）结论都是 skipped，另外 6 个 job（bun、image2ppt 四个可移植矩阵、安装同步）success。同 workflow 在 main 上 c17a4c9（2026-09-16，合并 #222）起连续 6 次 failure（c17a4c9、2375e0a、ed94f39、f4f828a、9c9953a、351f619），之前 54b7e03 为 success。gh api `actions/runs/35950391382/jobs`、`actions/jobs/<id>/logs`、`actions/workflows/test-skill-tooling.yml/runs?branch=main` 于 2026-09-27 查。
[^license]: 提交 54eadc6（2026-06-18，"Update LICENSE"）：LICENSE 由 "MIT License, Copyright (c) 2026 Yuan Yizhe" 换成 Apache License 2.0 全文。gh api `repos/Yuan1z0825/nature-skills/commits/54eadc6`。
[^nscn]: 2026-09-27 curl https://natureskills.cn（307 → /agent）、/sitemap.xml、/manifest.webmanifest、/about、/legal/terms、/legal/privacy；隐私政策第 3、4 节讲积分与"平台配置的 AI 模型服务商"。
[^prs]: PR #37、#45（router 拆分，2026-05-28 / 05-30 合并）、#76（确认门，06-18）、#121（npx skills 与 nature-shared 包，07-15）、#213、#215（收窄确认与缩短 description，09-06 / 09-14）、#206、#208（碰撞审计与对齐门，08-24 / 08-27）、#70、#83（Claude Code 插件，未合并）、#64、#65（修 #62，06-07）、#99（paper2ppt QA，07-07）、#210（Codex 插件，08-31）、#212（Windows Mermaid 路径，09-03）、#222、#224、#225、#231（defusedxml，09-16 至 09-24 合并）、#233、#234（09-24 提，仍开着）的正文与合并状态，gh api 于 2026-09-27 查。
[^spec]: agentskills.io Specification，https://agentskills.io/specification，2026-09-27 取：字段表、name 须等于父目录名、metadata 为字符串到字符串映射、allowed-tools 实验性、SKILL.md 建议 500 行以内、引用只引一层。
[^i72]: issue #72「codex中无法打开nature-academic-search MCP」（2026-06-14，2 条评论）。
[^plugins]: 文件历史：`.claude-plugin/plugin.json` 由 cf4387d（05-06）加入、574e167（06-15 "Delete .claude-plugin directory"）删除；`.agents/plugins/marketplace.json` 由 77dc9be（05-26）加入、f6c791d（06-15）删除、2fc270f（08-31，PR #210）重新加入。
[^i62]: issue #62（2026-06-06），报告 `nature_citation.py` 的 NameError 与无 MCP 环境的可移植性问题。
[^i74]: issue #74（2026-06-16），academic-search 安装脚本漏拷 `manifest.yaml` 与 `static/`。
[^i60]: issue #60（2026-06-02 提、当天关闭）及两条评论：仓库作者 Yuan1z0825 与另一用户 YUAN-0014。
[^i97]: issue #97（2026-07-06）及两条评论。
[^i181]: issue #181（2026-07-31）及维护者评论，指向修复提交 e7a9bc0。
[^i183]: issue #183（2026-08-01）及维护者评论，指向修复提交 4312c49。
[^i66]: issue #66（2026-06-07 提、06-09 关闭）及仓库作者的一条评论（06-08）。
[^repo]: gh api `repos/Yuan1z0825/nature-skills`、`/releases`、`/tags`，2026-09-27：44,699 star、2,346 fork、license Apache-2.0、release 与 tag 均为 0。
[^commits]: gh api 提交列表全量（858 条），2026-09-27 取；机器人指 github-actions[bot]；作者按 login 或提交署名计。
[^issues]: gh api issues（state=all）与 pulls（state=all）全量，2026-09-27 取：issue 31 条全关；PR 198 条，164 合并、32 关闭未合、2 开着（#233、#234）。
