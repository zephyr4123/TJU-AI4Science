---
title: AI Research SKILLs 代码级深读
subtitle: 科研 AI 能力选型 · 写作与出想法四个 skill：98 个 skill 没有一个脚本，能力全在 Markdown 正文里
kind: 开源项目选型深读（只读代码，不跑、不装依赖）
date: 2026-09-27
scope: 仓库 https://github.com/Orchestra-Research/AI-Research-SKILLs，浅克隆到外层 vendor/AI-Research-SKILLs，提交 773a529（release v1.7.2，2026-06-16）；深读 20-ml-paper-writing/ml-paper-writing、20-ml-paper-writing/academic-plotting 与 21-research-ideation 下两个，0-autoresearch-skill 只概述，其余 93 个只盘格式与分布；平台一侧对照内仓提交 de3d948 与外层提交 b537e64；文中不带前缀的 文件:行 相对该仓库根，带 platform/ 或 docs/ 前缀的相对外层仓根；GitHub 上的 issue、PR、release、提交数据 2026-09-27 用 gh api 查
status: 第一版
---

> **结论先行**：AI Research SKILLs 是一个**以文档为主的库**。98 个 `SKILL.md` 没有一个带 `scripts/` 目录，技能目录里的代码文件只有 `06-post-training/grpo-rl-training/` 下两个示例 `.py`（另有 NeurIPS 模板的一个 Makefile）。技能目录之外能执行的是：npm 安装器（`packages/ai-research-skills/src/`，5 个 JS 文件 2,600 行）、四条 GitHub Actions 与它们调的 `scripts/check-inventory.sh`、绘图演示的三个 Python 脚本（`demos/scientific-plotting-demo/figures/`），以及一个做宣传视频的 Remotion 工程（`video-promo/`）。README 列的能力都以「Markdown 正文 + 正文里可复制的代码片段」存在，由宿主 agent（Claude Code、Codex 等）读了照做。
>
> 这次看的四个：**`ml-paper-writing`** 真有的是 6 个会议的 LaTeX 模板目录（会议样式文件的拷贝，44 个文件）和一份写作方法清单；README 说的 citation verification 是 `references/citation-workflow.md` 里一段示范 Python（Semantic Scholar + CrossRef + arXiv + DOI 内容协商），不是脚本、没有测试，示范代码本身把检索第一条当命中、`verify` 先无条件记一个来源、网络错误 `except: pass`、核不上只打印警告仍返回 BibTeX。**`academic-plotting`** 的数据图走 matplotlib / seaborn，不要 key；架构图那条工作流写死 Gemini（`google-genai` + `GEMINI_API_KEY` + `gemini-3-pro-image-preview`），`SKILL.md` 只在「替代方案」表里点了 TikZ、draw.io、Mermaid 的名字，TikZ 与 Mermaid 的写法在 references 里各一段；把模型改成可切换的外部 PR #71 开着没合，它把 key 换成 `OPENROUTER_API_KEY`，仍是一把单独的 key。**出想法**两个（`brainstorming-research-ideas`、`creative-thinking-for-research`）是纯提示词：10 个与 8 个思考框架，`dependencies: []`，不检索文献、不落文件。
>
> 成熟度：零测试；CI 只核「文档里写的 skill 总数与分类数」与磁盘上对得上；维护者在 issue #2 里说 skill 是用带搜索 MCP 的 Claude Code 汇总写成、人再通读，「只验证了一部分」。2026-06-16 之后没有提交，6 月 25 日以来的 17 条 issue / PR 维护者只回过一条。
>
> 和平台的关系（只列事实，见[第 5 节](#5-和平台对照)）：按 `platform/framework/skills/library.py` 的校验读，这四个原样放进 `skills/` 过不了 `make skills`：frontmatter 多出 `version` `author` `tags` `dependencies` 四个字段，`ml-paper-writing` 正文按平台的算法 974 行，超过 500 行上限；而且库里有一个不合规，整库扫描就报错，`ai4sci skill list` 一个也列不出来。正文里的指令假设 agent 能 `pip install`、裸跑 `python`、`cp -r` 模板、跑 `latexmk`、装 Exa MCP、开 `/loop`；平台执行层在 Claude Code 上的 Bash 白名单只有 `ai4sci skill`、Read 只放行工作目录，在 Codex 上除 `ai4sci` 外的命令都在没网的沙箱里，MCP 在两家适配器里都被清空，两家 agent 自带的 skill 加载也都关掉。LaTeX 模板目录、`figures/` 下的文件命名约定、`research-state.yaml` 里的假设条目形状这几样本身不含要执行的东西，但在平台上要用它们，仍要经过拷贝文件、编译 LaTeX 这些白名单里没有的动作（[5.3](#53-会碰到的平台规则)）。
>
> 怎么读：第 0 节是整库格式与 98 个 skill 的分布；第 1 到 7 节按七个问题各一节；[第 7 节](#7-还没弄清的问题)是没弄清的。横向对比见同目录 [README.md](README.md)。

## 0. 仓库画像与分布

### 0.1 整体格式

| 项 | 实况 | 证据 |
|---|---|---|
| 仓库 | Orchestra-Research 维护，MIT，13,064 star、931 fork，2025-11-03 建库；没有论文，只有 `CITATION.cff` 与博客链接；组织下公开仓库共 3 个（本仓、`.github`、ARA 模板仓） | [^gh-meta]、`CITATION.cff:1-17` |
| 可执行代码 | npm 安装器 `@orchestra-research/ai-research-skills` 1.7.2：`installer.js` 1,038 行、`prompts.js` 685、`index.js` 533、`agents.js` 179、`ascii.js` 165（另有 8 行的 `bin/cli.js`）；`scripts/check-inventory.sh` 66 行；四条 workflow（`check-inventory` `claude` `publish-npm` `sync-skills`）；绘图演示三个 Python 脚本（`gen_fig_andes_architecture_gemini.py` 311 行、`gen_fig_andes_workflow.py` 280 行、`gen_fig_experiment_results.py` 347 行）；`video-promo/` 下一个 Remotion（React）宣传视频工程 | `packages/ai-research-skills/package.json:3`、`.github/workflows/`、`demos/scientific-plotting-demo/figures/`、`video-promo/ai-research-skills-promo/package.json:6-16` |
| 技能目录里的代码 | 98 个 skill 里 0 个有 `scripts/`；全部技能目录只找到两个 `.py`：`06-post-training/grpo-rl-training/examples/reward_functions_library.py`、`06-post-training/grpo-rl-training/templates/basic_grpo_training.py`；其余非 Markdown 文件是 LaTeX 模板（`.tex` `.sty` `.bst` `.bib`、样例 PDF、一个 Makefile）与 autoresearch 的两个模板（`research-state.yaml`、不含脚本的 `progress-presentation.html`） | `find` 全仓 |
| frontmatter | 98 个都有 `name` `description` `version` `author` `license` `tags`，96 个有 `dependencies`（缺的是 `systems-paper-writing` 与 `0-autoresearch-skill`）；前六个是自家 `CLAUDE.md` 定的必填字段，`dependencies` 在那里标可选 | `CLAUDE.md:62-74` |
| license 与 author 字段 | 98 个都写 `MIT`；author 96 个是 Orchestra Research，另两个是 dailycafi、A-EVO Lab | 逐个解析 frontmatter |
| name 与目录名 | 48 个不一致，例如 `0-autoresearch-skill` 的 name 是 `autoresearch`、`22-agent-native-research-artifact/compiler` 的 name 是 `ara-compiler`；这次深读的四个一致 | 同上 |
| 正文长度 | 自家规矩「200 到 500 行，超过 500 不可接受」（同一文件的目录结构图里又写 200 到 600 行，README 的结构图写 50 到 150 行）；17 个超过 500，其中 `ml-paper-writing` 正文 973 行 | `CLAUDE.md:46,86,104`、`README.md:341` |
| references/ | 91 个有，7 个没有（4 个 safety、`grpo-rl-training`、出想法两个）；README 与 `CLAUDE.md` 写「300KB+ 文档」，references 达到 300 KB 的只有 3 个（deepspeed、axolotl、unsloth） | `README.md:347,362`、`CLAUDE.md:47,118` |
| 怎么写出来的 | 工程类 skill 用 Skill Seeker 抓官方文档；维护者说 skill 是用带搜索 MCP 的 Claude Code 查仓库与帖子后汇总，再人工通读。`ml-paper-writing` 的首个提交（4643521，2026-01-22）信息里带「Generated with Claude Code」与 Claude 合著行 | `README.md:484`、`dev_data/SKILL_BUILD_PLAN.md:1-10`、[^i2]、[^gh-commits] |
| 安装方式 | ① `npx` 安装器，全局模式：`git clone --depth 1` 当前 main 到 `~/.orchestra/.temp-clone`，拷到 `~/.orchestra/skills/`，再在检测到的每家 agent 的全局 skills 目录建软链（软链失败时整目录拷贝）；项目模式：直接拷进项目下的 `.claude/skills/`、`.codex/skills/` 等，锁文件 `.orchestra-skills.json` 记在项目根；② Claude Code 插件市场（`.claude-plugin/marketplace.json` 23 个插件）；③ 让 agent 读网上的 `WELCOME.md` 自己装 | `packages/ai-research-skills/src/installer.js:62-127,132-170,668-703,708-769`、`packages/ai-research-skills/src/agents.js:14-95,127-135`、`packages/ai-research-skills/src/prompts.js:121`、`README.md:84-139` |

安装器装的是「clone 时 main 的样子」，不跟 npm 版本号走（`packages/ai-research-skills/src/installer.js:8,74`）；建软链前对同名路径 `rmSync(..., {recursive: true, force: true})`，不看它是不是自己建的（`packages/ai-research-skills/src/installer.js:150-153`），项目模式拷贝前同样整目录删（`packages/ai-research-skills/src/installer.js:692-695`）。

### 0.2 98 个 skill 的分布

磁盘上 23 个分类目录、98 个 `SKILL.md`。和平台这次要找的三个阶段（文献、假设、写作）有关的只在四个目录里，合计 10 个；其余 19 个目录 88 个是训练、推理、评测等工程工具的用法手册。

| 分类目录 | 磁盘上 | README 分类表写的 | 内容 | 与三个阶段的关系 |
|---|---|---|---|---|
| `0-autoresearch-skill` | 1 | 1 | 全流程编排提示词 + 4 个模板 | 文献、假设、写作都经过它，只概述（[2.6](#26-autoresearch-一段话)） |
| `20-ml-paper-writing` | 4 | 2 | `ml-paper-writing`、`academic-plotting`、`systems-paper-writing`、`presenting-conference-talks` | 写作；这次深读前两个 |
| `21-research-ideation` | 2 | 2 | `brainstorming-research-ideas`、`creative-thinking-for-research` | 假设；这次深读 |
| `22-agent-native-research-artifact` | 3 | 3 | `compiler`（论文、仓库转成结构化产物）、`research-manager`（会话结束时记录决策）、`rigor-reviewer`（六维评审） | 文献与验证沾边，这次没深读 |
| `01` 到 `19` 共 19 个 | 88 | 82 | 模型结构、分词、微调、可解释性、数据、后训练、安全、分布式、算力平台、量化、评测、推理、MLOps、agent 框架、RAG、提示工程、可观测、多模态、新技术 | 实验阶段的工具手册，与三个阶段无关 |

README 分类表逐行加起来是 90 而不是标题写的 98（`README.md:146-170`）：写作少列 2 个，优化、MLOps、agents 各少 1 个，多模态少 3 个。补齐列表的 PR #73 开着没合[^gh-issues]。

## 1. 是不是

### 1.1 整库层面

| README 说 | 代码里 | 证据 |
|---|---|---|
| 98 个 skill、23 个分类 | 磁盘上属实。但文档内部不一致：README 分类表合计 90，统计表写 87，`WELCOME.md` 第 3 行写 86、第 13 行写 98。CI 的 `check-inventory.sh` 对 `CLAUDE.md`、npm README、`WELCOME.md` 各用一条固定短语的正则，取第一处匹配里的数字比对（`WELCOME.md` 只认「installs N skills」，所以第 3 行的 86 查不到）；短语找不到只警告、不失败；README 不在检查范围 | `README.md:146-170,381`、`WELCOME.md:3,13`、`scripts/check-inventory.sh:21-35,45-51` |
| Research-Grade Quality：每个 skill 300KB+ 官方文档、真实 GitHub issue | 3 / 98 达到 300 KB；7 个没有 references | `README.md:78,362`，见 0.1 |
| Skill 结构里有 `scripts/`（可选） | 0 / 98 有 | `README.md:355` |
| autoresearch 自动路由到全部领域 skill，「agent 不需要知道用哪个」 | 路由是 `0-autoresearch-skill/SKILL.md` 里一张「研究活动 → 去哪个分类目录找」的表加一份 references，agent 自己去读；没有路由代码。references 里的完整路由表列了 77 个 skill 路径，其中 17 个在磁盘上不存在（如 `06-post-training/trl/`、`13-mlops/wandb/`、`11-evaluation/inspect-ai/`、`14-agents/smolagents/`） | `README.md:538`、`0-autoresearch-skill/SKILL.md:152-166`、`0-autoresearch-skill/references/skill-routing.md:9-218`（逐条对磁盘） |
| 全部 98 个自动同步到 Orchestra 平台 | `sync-skills.yml` 用 `^[0-9]{2}-` 识别改动的 skill 目录，`0-autoresearch-skill` 只有一位数字前缀，它的改动匹配不上 | `README.md:317`、`.github/workflows/sync-skills.yml:35,41` |
| v1.7.1：同步时 zip 超过 190 个文件会「fails loudly」 | 打一行错误后 `continue` 跳过这个 skill，job 不失败 | `README.md:513`、`.github/workflows/sync-skills.yml:145-150` |
| 维护者在 #56 说「文献检索已由我们的 `deep-research` 与 `autoresearch` 覆盖」 | 仓库里没有 `deep-research` skill；「deep_research」只作为 `dev_data/` 里一份建库调研稿的文件名出现（`SKILL_BUILD_PLAN.md` 第 3 行引用它）；组织下另两个公开仓库也不叫这个名字 | [^i56]、`dev_data/deep_research_report_1.md`、`dev_data/SKILL_BUILD_PLAN.md:3`、[^gh-meta] |
| 安装器可逐个选 skill | 逐个选的清单里 4 个 id 在磁盘上不存在：`03-fine-tuning/torchtune`（没有这个 skill）、`08-distributed-training/fsdp`（目录叫 `pytorch-fsdp2`）、`13-mlops/wandb`（`weights-and-biases`）、`11-evaluation/lm-eval-harness`（`lm-evaluation-harness`），下载时 `existsSync` 为假直接跳过、不报错；`wandb` 与 `lm-eval-harness` 也在 quickstart 套装里。`20-ml-paper-writing` 仍按「整个分类是一个独立 skill」处理：逐个安装时不查 `SKILL.md` 就把整个分类目录拷过去、以分类名建一个软链，而 2026-03-26 重构后分类根上已没有 `SKILL.md`，四个 skill 在下一层。分类菜单里写的各类数目加起来是 91（写作写 1 个） | `packages/ai-research-skills/src/prompts.js:8-30,49,56,62-63,67,82-98`、`packages/ai-research-skills/src/installer.js:205-223,142-148`、提交 415c770[^gh-commits] |

### 1.2 论文写作两个

| README 说 | 代码里 | 证据 |
|---|---|---|
| ML Paper Writing 分类 2 个 skill | 4 个。另两个 README 分类表没列：`systems-paper-writing`（OSDI / SOSP / NSDI / ASPLOS 的段落级写法与 4 套模板）、`presenting-conference-talks`（从论文出 Beamer PDF 与 PPTX，依赖 `python-pptx`，生成代码同样写在正文与 references 的代码块里） | `README.md:150`、`20-ml-paper-writing/systems-paper-writing/SKILL.md:1-8,267-269`、`20-ml-paper-writing/presenting-conference-talks/SKILL.md:1-8,187-215` |
| LaTeX templates for 6 major conferences | 属实：`templates/` 下 aaai2026、acl、colm2025、iclr2026、icml2026、neurips2025 六个目录 44 个文件（`.sty` 13、`.tex` 11、`.bib` 5、`.bst` 5、样例 PDF 4，另有各目录的 README、ACL 的格式说明、NeurIPS 的 Makefile 等），是会议样式文件的拷贝，不是生成的；模板总 README 第 3 行称「official LaTeX templates」。NeurIPS 那份在自家 README 里标「Community template」：`main.tex` 用 `\usepackage[nonatbib, final]{neurips}`、作者栏写死 Bojian Zheng；样式文件里 `final` 会把投稿模式关掉（不匿名、不加行号） | `20-ml-paper-writing/ml-paper-writing/templates/README.md:3,112`、`20-ml-paper-writing/ml-paper-writing/templates/neurips2025/main.tex:3,23-26`、`20-ml-paper-writing/ml-paper-writing/templates/neurips2025/neurips.sty:48,273-278,346-351` |
| citation verification | 只有文字规则和示范代码：`SKILL.md` 里 6 步清单（检索 → 两处来源确认 → DOI 取 BibTeX → 核对论点 → 入库 → 失败标占位符），references 里一个 `CitationManager` 类。没有脚本、没有测试；示范代码的问题见 [2.3](#23-引用核对的示范代码) | `20-ml-paper-writing/ml-paper-writing/SKILL.md:724-829`、`20-ml-paper-writing/ml-paper-writing/references/citation-workflow.md:218-405` |
| 「AI 生成的引用约 40% 出错」 | 出处是 `sources.md` 里一篇 Enago 博客；`citation-workflow.md` 里「NeurIPS 2025 有 100+ 条幻觉引用」出处是 ByteIota 博客。都是二手来源 | `20-ml-paper-writing/ml-paper-writing/SKILL.md:38,726`、`20-ml-paper-writing/ml-paper-writing/references/citation-workflow.md:25`、`20-ml-paper-writing/ml-paper-writing/references/sources.md:139-141` |
| frontmatter `dependencies: [semanticscholar, arxiv, habanero, requests]` | 示范代码只用到 `semanticscholar` 与 `requests`（arXiv 走 `requests` 直连 export.arxiv.org）；`arxiv`、`habanero` 两个库只出现在推荐清单里 | `20-ml-paper-writing/ml-paper-writing/SKILL.md:8`、`20-ml-paper-writing/ml-paper-writing/references/citation-workflow.md:295-304,555-558`、`20-ml-paper-writing/ml-paper-writing/references/sources.md:103-105` |
| 写作方法「来自顶尖研究者」 | 正文确有 Nanda、Farquhar、Gopen & Swan、Lipton、Steinhardt、Perez 的要点摘录与链接（Steinhardt 的链接是博客首页；来源表里的 Karpathy 一行写「Various lectures」，没有链接），另有 NeurIPS 16 项清单、ICML / ICLR / ACL 要求、审稿标准 | `20-ml-paper-writing/ml-paper-writing/SKILL.md:356-424`、`20-ml-paper-writing/ml-paper-writing/references/checklists.md:15-198` |
| Academic Plotting：架构图 via Gemini、数据图 via matplotlib / seaborn | 属实。架构图工作流写死 `gemini-3-pro-image-preview` 与 `GEMINI_API_KEY`，`SKILL.md` 里不走 Gemini 的架构图画法没有写成工作流，只在「替代方案」表里点了 TikZ、draw.io、Mermaid 三个名字；TikZ 与 Mermaid 的写法在 references 里各一段，Mermaid 那段定位成「写 Gemini 提示词之前先理结构」 | `20-ml-paper-writing/academic-plotting/SKILL.md:15-30,195,229-239,463`、`20-ml-paper-writing/academic-plotting/references/diagram-generation.md:361-394` |
| 数据图「自动选图型」 | 一张「数据形状 → 图型」的判断表，由 agent 照着选；没有选图型的代码 | `20-ml-paper-writing/academic-plotting/SKILL.md:73-79,314-324` |
| 配色「colorblind-safe」 | 自相矛盾：第 187 行写数据图「必须」用 Okabe-Ito，而第 343-347 行的样式模板用的是自家「Ocean Dusk」并称其色盲安全；`ml-paper-writing` 又说用 Okabe-Ito 或 Paul Tol | `20-ml-paper-writing/academic-plotting/SKILL.md:187,343-347`、`20-ml-paper-writing/ml-paper-writing/SKILL.md:913` |
| 海报图「用 `latex-posters` skill」 | 本仓没有这个 skill；PR #71 的说明也把它叫作悬空引用 | `20-ml-paper-writing/academic-plotting/SKILL.md:466`、[^pr71] |
| 绘图演示「真实 BurstGPT trace 上的 CDF」 | 演示的数据图用 `np.random` 按论文报的分布合成（函数注释写明 synthetic），演示 README 有三处把图说成 BurstGPT trace 上的结果（第 70、104 行明写「real-world」，第 74 行图注写「on BurstGPT Trace」），只在页尾一行注明合成数据。skill 正文没有要求数据图的数从哪个文件来，输入可以是「一段带数字的话」或内联数组 | `demos/scientific-plotting-demo/figures/gen_fig_experiment_results.py:61-83,139`、`demos/scientific-plotting-demo/README.md:70,74,104,211`、`20-ml-paper-writing/academic-plotting/SKILL.md:42,67,307` |
| 正文里的「引用本库」一节 | `ml-paper-writing` 末尾有一节「Citing AI Research Skills」，请用了本库的研究者在致谢或参考文献里引用它，给了 BibTeX 与一句致谢模板（2026-03-30 提交 4bdd8b5 加入，提交信息写「for researchers using the library」）。这一节写在 `SKILL.md` 里，读它的是 agent；正文没有指示 agent 自己把它加进论文 | `20-ml-paper-writing/ml-paper-writing/SKILL.md:920-939`、[^gh-commits] |

主线 #189 里记的学长原稿匹配点是「覆盖论文起草、LaTeX 模板与研究写作流程」：起草与写作流程是正文里的方法清单，LaTeX 模板是实打实的文件，二者都属实；「引用核对」一项只到示范代码这一层。

### 1.3 出想法两个

| README 说 | 代码里 | 证据 |
|---|---|---|
| Research Brainstorming：10 个互补视角的结构化框架 | 属实，正文 10 节，每节有说明与一段 Workflow 步骤，只有第 1、3、6 节另带自检清单（第 10 节是几条校准问题），后接 Diverge（10 到 20 个候选）→ Converge（5 条淘汰标准）→ Refine（两句话陈述、3 个验证实验、2 周试点）三段流程 | `21-research-ideation/brainstorming-research-ideas/SKILL.md:31-286,288-335`（自检清单在 54、109、189 行） |
| Creative Thinking：认知科学框架，「empirically grounded」 | 8 节框架属实；提到 Koestler、Gentner、Dunbar、Boden、Kauffman、Steven Johnson、Rothenberg 的名字，全文没有一条参考文献或链接；「Meta-research consistently shows」无出处。示例表里写神经编解码器「compress beyond information-theoretic limits」，字面上与信源编码定理（压缩率不低于信源熵）不符 | `21-research-ideation/creative-thinking-for-research/SKILL.md:13,34,36,108,142,249,282,292` |
| 找新颖方向 | 新颖性检查只有自检问题（「这个问题真的没被解决吗」），两个 skill 的流程里都没有检索文献的步骤；只有 creative-thinking 一句「5 年前能做的多半有人做过，查一下文献」 | `21-research-ideation/brainstorming-research-ideas/SKILL.md:54-57`、`21-research-ideation/creative-thinking-for-research/SKILL.md:276` |
| 文献综述请用 `scientific-skills:literature-review` | 本仓没有这个 skill，指的是 K-Dense 的。K-Dense 仓库 2026-04 之前叫 `claude-scientific-skills`，插件市场文件里的插件名就是 `scientific-skills`、清单里有 `literature-review`；2026-04-10 那个文件被删，现在插件名是 `scientific-agent-skills`。出想法两个 skill 在 2026-02-19 加入时这个名字对得上，现在对不上（见 [k-dense-skills.md](k-dense-skills.md)） | `21-research-ideation/brainstorming-research-ideas/SKILL.md:27`、`21-research-ideation/creative-thinking-for-research/SKILL.md:26`、`vendor/scientific-agent-skills/plugin.json:3`、[^kdense-old] |
| 产出 | 没有文件约定：只说「保留一份写下来的候选清单，被否的也留着」（creative-thinking 是「维护一份滚动清单」），不给文件名与格式 | `21-research-ideation/brainstorming-research-ideas/SKILL.md:383`、`21-research-ideation/creative-thinking-for-research/SKILL.md:358` |

## 2. 怎么做

### 2.1 skill 在运行时是什么

没有运行时。一个 skill = 一个目录里的 `SKILL.md`（frontmatter + 正文）加可选的 `references/` 与模板。宿主 agent 用自己的原生机制加载：安装器把目录软链进 `~/.claude/skills/`、`~/.codex/skills/`、`~/.agents/skills/` 等十个位置（`~` 下有哪家 agent 的配置目录就链进哪家，`packages/ai-research-skills/src/agents.js:14-95,101-119`），或在项目模式下拷进项目里的同名目录；agent 按 `description` 决定读不读全文，读了之后照正文做，正文里的 Python 与 shell 片段由 agent 复制出来自己执行。这次看的四个 skill **都不自己调模型**：写作、出想法的「智能」全来自宿主 agent；唯一在代码里直接调另一个模型的是 `academic-plotting` 让 agent 生成的 Gemini 出图脚本（演示目录里有一份照模板写出的 `demos/scientific-plotting-demo/figures/gen_fig_andes_architecture_gemini.py:28-38`）。

### 2.2 ml-paper-writing

入口是 `SKILL.md`，五条工作流按编号散在正文里：

| 工作流 | 做什么 | 进 | 出 | 证据 |
|---|---|---|---|---|
| 0 从研究仓库起步 | `ls`、`find`、`grep` 摸仓库结构、找结果文件与已有引用，和研究者确认一句话贡献，再检索文献 | 研究者的代码仓、结果、已有 `.bib` | 对贡献的一句话表述 | `20-ml-paper-writing/ml-paper-writing/SKILL.md:90-175` |
| 1 写一篇完整论文 | 10 步：一句话贡献（要研究者确认）→ Figure 1 → 摘要（Farquhar 五句式）→ 引言 → 方法 → 实验 → 相关工作 → 局限 → 会议清单 → 终审 | 同上 | 各节草稿 | `20-ml-paper-writing/ml-paper-writing/SKILL.md:246-346` |
| 4 从模板起一篇 | 整目录拷贝模板（`cp -r`）→ 先原样编译（`latexmk -pdf`，或 pdflatex → bibtex → pdflatex 两遍）→ 按节替换示例内容 → 最后清理 | `templates/<会议>/` | LaTeX 工程目录，主文件名随会议变（`main.tex`、`example_paper.tex`、`iclr2026_conference.tex`、`acl_latex.tex`、`aaai2026-unified-template.tex`、`colm2025_conference.tex`） | `20-ml-paper-writing/ml-paper-writing/SKILL.md:467-617` |
| 2 加引用 | 检索（Exa MCP 或 Semantic Scholar）→ 两处来源确认 → DOI 内容协商取 BibTeX → 核对论点 → 入 `.bib` → 任一步失败写 `\cite{PLACEHOLDER_...}` 并告诉研究者 | 检索词 | `.bib` 条目或占位符 | `20-ml-paper-writing/ml-paper-writing/SKILL.md:737-829` |
| 3 换会议格式 | 用目标会议新模板起工程，只搬正文，按页数增删 | 旧 LaTeX 工程 | 新 LaTeX 工程 | `20-ml-paper-writing/ml-paper-writing/SKILL.md:627-721` |

行为基调写在前面：「主动交完整初稿，不要每节都等反馈」，只有会议不明、叙事有多种同样合理的讲法、结果不完整、研究者要求先看时才停下来问（`20-ml-paper-writing/ml-paper-writing/SKILL.md:19-29,192-222`）。同一份文档里工作流 0 第 3 步写「永远不要假设叙事，一定和人核实」、工作流 1 第 1 步写「这一步要研究者明确确认」（`20-ml-paper-writing/ml-paper-writing/SKILL.md:133-141,264-273`），两处的尺度靠 agent 自己拿捏。autoresearch 调它写论文时又明写「如果 ml-paper-writing 提到要人协作的地方，自己适应、继续往下写」（`0-autoresearch-skill/SKILL.md:340`）。

### 2.3 引用核对的示范代码

`references/citation-workflow.md` 里的 `CitationManager` 是这个 skill 唯一接近「实现」的部分，agent 要么照抄运行，要么照着步骤手动做。逐段读下来：

| 位置 | 做什么 | 问题 |
|---|---|---|
| `20-ml-paper-writing/ml-paper-writing/references/citation-workflow.md:252-273` | `search()`：`SemanticScholar().search_paper(query, limit)`，转成 `Paper` | 没传 key 时走公共限流。`limit` 在库里是每页条数：按 `semanticscholar` 库默认分支的源码，`search_paper` 返回 `PaginatedResults`，它的 `__iter__` 在还有下一页时继续请求，相关性搜索上限 1,000 条[^s2lib]；所以这里的 `for r in results` 会一路翻页，`cite()` 用 `limit=5` 时最多约 200 次请求才返回。`SKILL.md` 第 1 步的示范（`20-ml-paper-writing/ml-paper-writing/SKILL.md:766-767`）同样写法。读的是库源码，没跑；示范代码没钉库版本 |
| `20-ml-paper-writing/ml-paper-writing/references/citation-workflow.md:275-306` | `verify()`：凑够两个来源算通过 | 第 280 行先无条件 `append("Semantic Scholar")`，所以只要 CrossRef 或 arXiv 任一处有就「两处确认」；CrossRef、arXiv 请求的异常都 `except: pass`（291-292、303-304） |
| `20-ml-paper-writing/ml-paper-writing/references/citation-workflow.md:308-344` | `get_bibtex()`：`doi.org` 内容协商取 BibTeX，失败退到 `_generate_bibtex()` 用 Semantic Scholar 元数据拼一条 | 异常 `except: pass`（320-321）；兜底拼出来的一律是 `@article`，会议论文也是 |
| `20-ml-paper-writing/ml-paper-writing/references/citation-workflow.md:346-368` | `cite()`：检索 → 取第一条 → verify → 取 BibTeX → 记进 `verified_papers` | 取检索第一条，不比对标题（353-354）；verify 没过只 `print` 一行警告，照样返回 BibTeX 并记为 verified（358-366） |
| `20-ml-paper-writing/ml-paper-writing/references/citation-workflow.md:167-179` | 「核对论点」：取摘要，查论点字符串在不在摘要里 | 子串匹配，只看摘要；取不到摘要时返回 `None`，下一行 `abstract.lower()` 直接抛错 |
| `20-ml-paper-writing/ml-paper-writing/references/citation-workflow.md:389-404` | `batch_cite()`：逐条 `cite()`，结果写进 `references.bib` | 没过核对的条目与兜底拼出来的 `@article` 一起写进文件，文件里分不出哪条核过 |

也就是说，文字规则（`20-ml-paper-writing/ml-paper-writing/SKILL.md:739-747` 的「每一条都要两处确认，任一步失败就标占位符」，`20-ml-paper-writing/ml-paper-writing/SKILL.md:823` 的「找到论文但取不到 BibTeX 就标占位符」）比示范代码严，代码照抄运行达不到文字规则。

### 2.4 academic-plotting

| 步骤 | 做什么 | 证据 |
|---|---|---|
| 0 从上下文抽取 | 读论文段落或结果数据，数实体、找关系、定布局（流水线左到右、分层横带、中心辐射、树），或定维度与图型；「有数值轴用 matplotlib，有框和箭头用 Gemini」 | `20-ml-paper-writing/academic-plotting/SKILL.md:30,34-89` |
| 工作流 1 架构图 | 选四种视觉风格之一（手绘、极简、图标、色条）与配色 → 写六段式提示词（框定、风格 20-30 行、配色、布局 50-150 行、连线 30-80 行、约束）→ 生成 `figures/gen_fig_<name>.py` → 连跑 3 次 → 人或 agent 按五维打分挑一张存 `figures/fig_<name>.png` | `20-ml-paper-writing/academic-plotting/SKILL.md:95-221,289-293`、`20-ml-paper-writing/academic-plotting/references/diagram-generation.md:343-359` |
| 出图脚本模板 | `google.genai.Client(api_key=os.environ["GEMINI_API_KEY"])`，`generate_content(model="gemini-3-pro-image-preview", response_modalities=["IMAGE","TEXT"])`，存第一个 `inline_data`；异常 `print` 后返回 None，三次全失败才 `exit(1)` | `20-ml-paper-writing/academic-plotting/SKILL.md:225-285` |
| 工作流 2 数据图 | 按判断表选图型 → 套一段 `rcParams` 样式 → 「我们的方法」单独配色 → 同时存 PDF 与 300 DPI PNG，脚本存 `figures/gen_fig_<name>.py` | `20-ml-paper-writing/academic-plotting/SKILL.md:299-424` |
| 文件约定 | `figures/gen_fig_<name>.py`、`fig_<name>.pdf`、`fig_<name>.png`、`fig_<name>_attempt*.png` | `20-ml-paper-writing/academic-plotting/SKILL.md:471-479` |

架构图输出是 PNG 位图（`20-ml-paper-writing/academic-plotting/SKILL.md:440`「PNG only for AI-generated diagrams」）。演示目录里还有一张纯 matplotlib 画的流程图 `gen_fig_andes_workflow.py`（280 行，不调 Gemini），这条路线 `academic-plotting` 的 `SKILL.md` 没写成工作流（`demos/scientific-plotting-demo/figures/gen_fig_andes_workflow.py:11-15`）。

### 2.5 出想法两个

两者都是「agent 带着研究者一步步过框架」的交互式提示词，不调任何工具：

- `brainstorming-research-ideas`：先判断研究者处在哪种状态（没方向、有方向没点子、有点子不确定、想换角度……），按选择表挑 2 到 3 个框架，逐步问研究者要领域内容，攒 10 到 20 个候选，用 5 条淘汰标准收到 3 到 5 个，再把第一名写成两句话陈述、3 个验证实验、一个 2 周试点（`21-research-ideation/brainstorming-research-ideas/SKILL.md:339-351,369-384`）。
- `creative-thinking-for-research`：按「卡在哪种思维障碍」挑框架，给一个 90 分钟的四段协议（映射 15、扰动 30、深化 30、评估 15），最后用 brainstorming 的两句话测试收口，再交回 brainstorming 做收敛（`21-research-ideation/creative-thinking-for-research/SKILL.md:311-335,350-366`）。
- 分工写在各自的「给 agent 的用法」里：creative-thinking 写「领域知识来自研究者，agent 只提供思考的结构」（`21-research-ideation/creative-thinking-for-research/SKILL.md:365`），brainstorming 写「最终选哪个由研究者定，agent 只做引导」（`21-research-ideation/brainstorming-research-ideas/SKILL.md:384`）。

### 2.6 autoresearch 一段话

`0-autoresearch-skill` 是一份 403 行正文的编排提示词，加 3 份 references 与 4 个模板（`research-state.yaml`、`findings.md`、`research-log.md`、`progress-presentation.html`），没有代码。它让宿主 agent 在项目根建固定目录（`literature/`、`experiments/<假设>/protocol.md`、`to_human/`、`paper/` 等，`0-autoresearch-skill/SKILL.md:38-52`），**第一件事**是开一个挂钟循环：Claude Code 上 `/loop 20m <一段续跑提示>`，OpenClaw 上 `cron.add` 每 20 分钟一次（`0-autoresearch-skill/SKILL.md:244-282`，标 MANDATORY）；然后 bootstrap（用 Exa MCP、Semantic Scholar、arXiv、CrossRef 查文献，每篇存一个摘要文件，调 `21-research-ideation` 出假设，锁定评估指标，`0-autoresearch-skill/SKILL.md:95-122`）→ 内环（每个假设先写 `protocol.md` 并 git commit 再跑，`0-autoresearch-skill/SKILL.md:131-148`）→ 外环（每 5 到 10 次实验综合一次，更新 `findings.md`，在深入、拓宽、转向、收尾四个方向里选，`0-autoresearch-skill/SKILL.md:188-228`）→ 调 `ml-paper-writing` 写论文。文首一句「不要征求用户许可或确认」（`0-autoresearch-skill/SKILL.md:16`），写论文一段又让它越过 `ml-paper-writing` 里要人协作的地方（`0-autoresearch-skill/SKILL.md:340,351`）。OpenClaw 版的循环提示还让 agent 把 PDF 报告经 Telegram、WhatsApp 或 Slack 发给用户（`0-autoresearch-skill/SKILL.md:271`）。它是整库唯一把文献、假设、实验、写作串起来的地方，也是唯一给出假设条目形状的地方：`id`、`statement`、`status`（pending / active / supported / refuted / inconclusive）、`motivation`、`parent`、`priority`（`0-autoresearch-skill/templates/research-state.yaml:22-29`）；同一模板里文献条目的形状是 `id`、`title`、`authors`、`year`、`relevance`（`0-autoresearch-skill/templates/research-state.yaml:12-20`）。

## 3. 为什么

### 3.1 文档里写明的设计理由

| 设计 | 作者写的理由 | 证据 |
|---|---|---|
| 纯 Markdown、渐进披露 | 照 Anthropic 的 skill 最佳实践：`SKILL.md` 200 到 500 行是概览，细节放一层 references；「不要解释 Claude 已经知道的基础」。为什么不带脚本没有写 | `CLAUDE.md:83-106`、`anthropic_official_docs/best_practices.md` |
| 引用必须程序化取、不许凭记忆写 BibTeX | AI 生成的引用错误率高，幻觉引用会导致拒稿或撤稿；2026-01-22 专门一次提交加上警告与 Exa MCP 推荐 | `20-ml-paper-writing/ml-paper-writing/SKILL.md:33-58`、提交 a1f5cd5[^gh-commits] |
| 先交完整初稿再问 | 「科学家很忙」，给个具体东西让人反应比逐节等反馈快 | `20-ml-paper-writing/ml-paper-writing/SKILL.md:19-29` |
| 模板整目录拷贝、先原样编译、不改 `.sty` | 列了 agent 常犯的五种模板错误（只拷 `main.tex`、改样式文件、乱加包、过早删示例、不常编译） | `20-ml-paper-writing/ml-paper-writing/SKILL.md:596-604` |
| 架构图用图像模型、每次跑 3 遍 | 框和箭头的空间布局复杂；同一提示词出图质量波动大；Gemini 会拼错或挪动文字，所以要求逐字写出每个标签。演示 README 说这一版三次全对、「上一代」三次都有拼写错误，没说上一代指模型还是提示词 | `20-ml-paper-writing/academic-plotting/SKILL.md:22,289-293`、`demos/scientific-plotting-demo/README.md:50` |
| 两个出想法 skill 分工 | brainstorming 给「发散 → 收敛 → 细化」的操作流程与过滤器，creative-thinking 给更底层的思维框架，二者配合用 | `21-research-ideation/creative-thinking-for-research/SKILL.md:28` |
| autoresearch 强制挂钟循环 | 不开循环 agent 跑完一轮就停 | `0-autoresearch-skill/SKILL.md:31,246` |

### 3.2 issue 与提交里踩过的坑

| 坑 | 经过 | 证据 |
|---|---|---|
| skill 内容没逐条验证 | 维护者答复：用 Claude Code 带搜索 MCP 汇总写，人再通读，「只验证了一部分，所以容易出错」 | [^i2] |
| 文档里的数字互相打架 | 外部审计发现 `CLAUDE.md` 等处 skill 数与分类列表过期；修法是加 `check-inventory` CI（PR #60），但它只核三个文件里固定短语处的总数与分类数，README 与各处分类明细不在内 | [^i54]、`scripts/check-inventory.sh:12-13,45-51` |
| YAML frontmatter 写坏 | ray-data、ray-train 两个 skill 的 frontmatter 不合法，PR #13 修 | [^i12] |
| Windows 上装不上 | 安装器用 shell `cp`，改成 Node `cpSync`，软链失败退到拷贝 | [^i15]、`packages/ai-research-skills/src/installer.js:155-167` |
| GitHub Action 可被任意人触发 | `claude.yml` 原先任何人评论 `@claude` 就以写权限跑；外部贡献者报告后自己提 PR #39（提交 a515c5e，2026-03-18）加了 `author_association` 限制 | [^i38]、`.github/workflows/claude.yml:17-20`、[^gh-commits] |
| 市场平台单个 zip 不超过 200 个文件 | 维护者复现不了，加了超 190 个就报错的检查（实际是跳过不失败，见 1.1）；issue 至今开着 | [^i57] |
| 全装后 skill 头太占上下文 | 用户实测 95 个 skill 的 frontmatter 约 13k token，问能否只暴露 autoresearch，未答复 | [^i65] |
| 卸载会删掉别人的软链 | `uninstallAllSkills` 只判断「是软链」不判断指向哪里，会删掉其他工具建的软链；两个修复 PR 未合 | [^i74] |
| 架构图写死 Gemini | PR #71 改成走 OpenRouter 的 OpenAI 兼容图像接口、默认 `gpt-image-2`、key 换成 `OPENROUTER_API_KEY`，未合 | [^pr71] |
| `ml-paper-writing` 982 行一整块 | PR #75 把它压成渐进披露入口、加「论点 → 证据」工作流，未合 | [^pr75] |
| 引用核对要不要换成专门工具 | bibtools 作者提议集成；维护者以「还在 alpha、没有许可证」为由不做深度集成，只同意列进推荐工具。作者次日补了 MIT，issue 仍开着，推荐工具清单里至今没有 bibtools | [^i18]、`20-ml-paper-writing/ml-paper-writing/references/citation-workflow.md:560-562` |
| 收什么、不收什么 | 拒了文献检索与翻译类（与已有能力重叠、偏医学检索、依赖外部专有 API）和机械工程领域工作流（超出 AI/ML 研究范围）；说明更倾向「本地可复现、自包含」的 skill。本仓自己的写作与 autoresearch 正文也依赖外部服务（Exa MCP、Semantic Scholar、Gemini，见第 4 节） | [^i56]、[^i58] |
| autoresearch 的循环提示反复加码 | 2026-03-15 到 03-24 的 15 次提交里 9 次在改 `/loop` 或 cron 的提示词，另一次在文首加「完全自主」指令 | 提交 8698e20、f286608、2aaeb62 等[^gh-commits] |

## 4. 跑起来要什么

| | ml-paper-writing | academic-plotting | 出想法两个 | autoresearch | 安装器 |
|---|---|---|---|---|---|
| 依赖 | 宿主 agent；示范代码要 `semanticscholar`、`requests`（frontmatter 另列 `arxiv`、`habanero` 未用到）；编译要 TeX Live（`latexmk` 或 `pdflatex` + `bibtex`），NeurIPS 的 Makefile 还要 `pdfcrop` | `matplotlib>=3.8`、`seaborn>=0.13`、`numpy`；架构图另要 `google-genai>=1.0`；样式里写 Times New Roman | 无（`dependencies: []`） | 取决于路由到的领域 skill；进度报告 HTML 打不开时退到 weasyprint / playwright / wkhtmltopdf 出 PDF | Node ≥ 18、git |
| 模型与 key | 不调模型；Semantic Scholar key 可选 | 数据图不要；架构图要 `GEMINI_API_KEY`（Google AI Studio 申请） | 不要 | 不调模型 | 不要 |
| 外部服务 | api.semanticscholar.org、doi.org 与 api.crossref.org、export.arxiv.org（示范代码用 http）；可选 Exa MCP（`npx -y mcp-remote https://mcp.exa.ai/mcp`） | Google Generative Language API | 无 | Exa MCP、Semantic Scholar、arXiv、CrossRef；Claude Code 的 `/loop` 或 OpenClaw 的 cron；OpenClaw 版要经 Telegram、WhatsApp 或 Slack 发报告 | github.com |
| 算力 | CPU | CPU；图像生成在 Google 侧 | 无 | 实验本身的 GPU | 无 |
| 操作系统 | 不限；模板 README 给了 macOS / Ubuntu / Windows 的 TeX 装法 | 不限 | 不限 | 不限 | 不限；Windows 无开发者模式时软链改拷贝 |
| 证据 | `20-ml-paper-writing/ml-paper-writing/SKILL.md:8,60-86,505-514`、`20-ml-paper-writing/ml-paper-writing/references/citation-workflow.md:248-249,298`、`20-ml-paper-writing/ml-paper-writing/templates/neurips2025/Makefile:9,19-20`、`20-ml-paper-writing/ml-paper-writing/templates/README.md:12-15` | `20-ml-paper-writing/academic-plotting/SKILL.md:8,195,229-239,333-334` | `21-research-ideation/brainstorming-research-ideas/SKILL.md:8`、`21-research-ideation/creative-thinking-for-research/SKILL.md:8` | `0-autoresearch-skill/SKILL.md:99-104,253,260-280,311` | `packages/ai-research-skills/package.json:41-48`、`packages/ai-research-skills/src/installer.js:74,155-167` |

另几件事：Exa MCP 的托管端点按 Exa 自己的 README 可以匿名用、有限流，要更高额度或它的 agent 功能才要 OAuth 或 API key[^exa]，额度多少、从课题组网络能不能连上没查；从课题组网络能不能访问 Google 的图像接口没实测（第 7 节）。安装器全局模式写用户全局目录（`~/.orchestra/`、各家 agent 的 `~/.<agent>/skills/`），项目模式写项目里的 `.<agent>/skills/`；两种模式都会把同名目录整个删掉再建（`packages/ai-research-skills/src/installer.js:150-153,692-695`）。

## 5. 和平台对照

### 5.1 平台这三个阶段现在有什么

| 阶段 | 平台现有 | 这个仓库对应的 | 证据 |
|---|---|---|---|
| 文献 | 没有步骤能力；主文件 `sources.md` 由研究助理用 CLI 自带的搜索与读网页手写；两个 skill：`pdf`（论文 → `paper.md` + `structured.json`，含本篇的题目、作者、年份、DOI、arXiv 号，以及每条参考文献一段原文，参考文献不拆字段）、`download`（拉仓库、文件、HF） | 没有专做检索或综述的 skill。沾边的：autoresearch 的 bootstrap 一段文字（查文献、每篇存摘要、写 `literature/survey.md`）；`ml-paper-writing` 的引用示范代码（检索 + 取 BibTeX）；这次没深读的 ARA `compiler`（论文、仓库转结构化产物） | `docs/architecture/README.md:151,174`、`platform/framework/capabilities/__init__.py:43-47`、`platform/skills/pdf/SKILL.md:3,44`、`platform/workflows/reproduce.yaml:10`；`0-autoresearch-skill/SKILL.md:95-106`、`README.md:308` |
| 假设 | 没有能力，主文件未定名 | 两个出想法 skill（交互式提示词，不落文件）；autoresearch 的 `research-state.yaml` 假设条目形状与每个假设一份 `protocol.md` | `docs/architecture/README.md:170`、`platform/framework/capabilities/__init__.py:43`；见 2.5、2.6 |
| 写作 | 没有能力，主文件未定名。相邻的：分析阶段 `analysis` 只写三节固定的 `analysis.md`，描述符写明「不画图」「作图是这个阶段里另外的能力」，执行层写了 `analysis.md` 以外的文件判失败；验证阶段 `verify` 零模型把 `analysis.md` 里的数回溯到 `results.json` | `ml-paper-writing`（模板 + 方法 + 引用示范代码）、`academic-plotting`（出图脚本约定）、另有 `systems-paper-writing`、`presenting-conference-talks` | `platform/framework/capabilities/analysis/__init__.py:22-32`、`platform/framework/capabilities/verify/__init__.py:29-44` |

### 5.2 多了什么、重叠什么

多出来的（平台现在没有对应物的）：

- 6 个 ML 会议加 4 个系统会议的 LaTeX 模板目录与编译步骤。
- 论文各节的写法要点、NeurIPS 16 项清单、ICML / ICLR / ACL 的会议要求、审稿标准。
- 引用核对的步骤与示范代码（Semantic Scholar、CrossRef、arXiv、DOI 内容协商）。
- 数据图的样式模板、图型判断表、`figures/` 命名约定；架构图的六段式提示词与五维挑图标准。
- 两套出想法的问答框架。

重叠的：

- 文献材料清单：平台是助理手写的 `sources.md`（`docs/architecture/README.md:174`），autoresearch 是 `literature/` 下每篇一个摘要加 `survey.md`（`0-autoresearch-skill/SKILL.md:106`）。
- 论文元数据：平台 `pdf` skill 从 PDF 里抽出本篇的 DOI、arXiv 号和每条参考文献的原文（`platform/skills/pdf/SKILL.md:44,56`）；引用核对要的是每条参考文献的标题或 DOI，与它有交集，但 `pdf` 不把参考文献拆成字段。
- 「数从哪来」：平台 `verify` 核 `analysis.md` 的数（`platform/framework/capabilities/verify/__init__.py:35-40`）；这个仓库的 `ml-paper-writing` 与 `academic-plotting` 里没有把正文或图里的数回溯到结果文件的步骤，绘图 skill 允许数据来自一段话或内联数组，绘图演示本身用了合成数据（1.2）。
- 编排：autoresearch 的「文献 → 假设 → 内环 → 外环 → 写作」与平台的流程文件是同一件事的两种做法，前者由 agent 自己决定下一步，后者由研究助理按流程文件走、断点等人签。

### 5.3 会碰到的平台规则

| 规则 | 碰到的点 | 这个仓库的证据 | 平台的证据 |
|---|---|---|---|
| P-22 frontmatter 只收规范字段 | 四个 skill 都有 `version` `author` `tags` `dependencies`（出想法两个的 `dependencies` 是空列表）；校验会报「规范之外的字段」。平台扫库时一个 skill 不合规就整库报错，`ai4sci skill list` 一个都列不出 | `20-ml-paper-writing/ml-paper-writing/SKILL.md:4-8` 等 | `platform/framework/skills/library.py:5,26,110-131,182-185`、`platform/framework/cli/skill.py:28-33` |
| P-22 正文不超过 500 行 | `ml-paper-writing` 按 `library.py` 的算法 974 行（从 frontmatter 结尾的 `---` 之后切，开头的空行也算一行）；另三个 358 到 471 行 | `20-ml-paper-writing/ml-paper-writing/SKILL.md`（982 行含 frontmatter） | `platform/framework/skills/library.py:32,144-145,164-177` |
| P-22 name 等于目录名 | 深读的四个一致；`0-autoresearch-skill` 与 `autoresearch` 不一致 | `0-autoresearch-skill/SKILL.md:2` | `platform/framework/skills/library.py:190-191` |
| P-22 脚本 PEP 723 自带依赖、锁进仓、`ai4sci skill run` 起 | 四个 skill 都没有脚本；要执行的东西写在正文代码块里，依赖靠 `pip install`（autoresearch 明写 `pip install semanticscholar`）。平台对没有 `scripts/` 的 skill，`run` 报「只能读不能跑」 | `20-ml-paper-writing/ml-paper-writing/SKILL.md:762-793`、`0-autoresearch-skill/SKILL.md:101-102` | `platform/framework/skills/library.py:218-228`、`platform/framework/skills/run.py:45-48`、`docs/architecture/README.md:172` |
| P-22 uv 装不了的系统命令 | `ml-paper-writing` 编译要 TeX Live（`latexmk` 或 `pdflatex` + `bibtex`，NeurIPS 的 Makefile 另要 `pdfcrop`）；平台为这类命令留了 metadata 键 `ai4sci-system-tools`，`make skills` 逐个 `which` | `20-ml-paper-writing/ml-paper-writing/SKILL.md:505-518`、`20-ml-paper-writing/ml-paper-writing/templates/neurips2025/Makefile:9-20` | `platform/framework/skills/library.py:33-35,62-64` |
| P-22 加载不靠 agent 原生机制 | 本仓的安装方式全是 agent 原生目录（全局或项目里的 `.<agent>/skills/`）与插件市场 | `packages/ai-research-skills/src/agents.js:14-95`、`.claude-plugin/marketplace.json` | `docs/architecture/README.md:172`；Claude Code 适配器带 `--disable-slash-commands` 清空 skill（`platform/backends/claude_code.py:8,39`）；Codex 适配器每次起会话把系统、个人、管理员三处 skill 逐个关掉（`platform/backends/codex.py:25-29,123-126`） |
| P-14 / P-22 执行层命令白名单与读文件范围 | 正文让 agent 跑 `ls` `find` `grep` `cp -r` `latexmk` `python` 与 `pip install`，并读 `references/` 与 `templates/` 下的文件。平台执行层在 Claude Code 上只放行限定目录的 Edit / Write、工作目录的 Read、`Bash(ai4sci skill *)` 与 WebSearch、WebFetch（代码注释记着只读 Bash 在 dontAsk 下自动放行、写操作被拒）；`ai4sci skill show` 只打印正文、skill 目录的绝对路径与 references 文件名，不打印 references 与模板的内容。Codex 没有按命令的白名单：`ai4sci` 在沙箱外跑，其余命令在沙箱里，只能写工作区、没有网络 | `20-ml-paper-writing/ml-paper-writing/SKILL.md:107-128,485-514`、`20-ml-paper-writing/ml-paper-writing/SKILL.md:829,881,966` | `platform/framework/skills/__init__.py:37`、`platform/backends/claude_code.py:146-160`、`platform/framework/cli/skill.py:41-57`、`platform/backends/__init__.py:66-72`、`platform/backends/codex.py:16-24,30-33,127-133` |
| P-14 联网只用 CLI 自带工具 | 两个 skill 的正文都推荐装 Exa MCP 做检索，示范代码用 `requests` 直连 Semantic Scholar、CrossRef、arXiv；平台两家适配器都清空 MCP、都放行 CLI 自带的搜索；Codex 沙箱里的命令没网，联网的动作只能走 `ai4sci` | `20-ml-paper-writing/ml-paper-writing/SKILL.md:60-86`、`0-autoresearch-skill/SKILL.md:100` | `platform/backends/claude_code.py:39-42`（`--strict-mcp-config`、WebSearch / WebFetch）、`platform/backends/codex.py:114,118`（`web_search="live"`、`mcp_servers={}`） |
| P-1 框架不调模型、执行层唯一写代码 | 架构图要一个脚本拿单独的 key 调 Gemini。P-1 的机器判据是「`framework/` 下 grep 不到模型 API 名」，skill 脚本放在 `skills/` 下，不在这条 grep 的范围里；这种脚本由执行层或助理经 `ai4sci skill run` 起，调模型的是脚本进程而不是 agent 会话本身，纲领没写这种情形怎么算。两家适配器起 agent 会话时继承服务进程的全部环境变量，skill 脚本再继承一次：起服务的人环境里有 `GEMINI_API_KEY`，agent 会话和脚本都读得到；`download` 已有读 `HF_TOKEN` 的先例 | `20-ml-paper-writing/academic-plotting/SKILL.md:229-239` | `docs/architecture/README.md:151`、`platform/backends/claude_code.py:122`、`platform/backends/codex.py:241`、`platform/framework/skills/run.py:40`、`platform/skills/download/scripts/fetch.py:15,136` |
| P-25 底座归人 | `agents.yaml` 只记助理与执行层各用哪家、每家的模型、思考深度与上次自检，没有第三方模型 key 的位置 | 同上 | `docs/architecture/README.md:175`、`platform/framework/agents.py:139-144` |
| P-20 主文件归阶段、skill 不开产出目录 | 写作与假设的主文件未定名；`ml-paper-writing` 的主文件名随会议变；`academic-plotting` 有 `figures/` 命名约定；出想法两个不落文件；autoresearch 有 `research-state.yaml`、`protocol.md` | 2.2、2.4、2.5、2.6 | `docs/architecture/README.md:170`、`platform/framework/capabilities/__init__.py:43-52` |
| P-19 只有人能确认 / P-10 框架没有下一步 | autoresearch「不要征求许可」「永不停止」、自己开循环决定方向，并让 agent 越过 `ml-paper-writing` 里要人协作的地方；`ml-paper-writing`「先交初稿、不要逐节等」与「一句话贡献要研究者确认」并存 | `0-autoresearch-skill/SKILL.md:16,150,244-282,340,351`、`20-ml-paper-writing/ml-paper-writing/SKILL.md:133-141,194-222,264-273` | `docs/architecture/README.md:160,169` |
| P-7 fail-closed / P-8 不许吞异常 | 引用示范代码三处 `except: pass`、核不上仍返回；出图脚本 `except Exception` 后 `print` | `20-ml-paper-writing/ml-paper-writing/references/citation-workflow.md:291-292,303-304,320-321,358-366`、`20-ml-paper-writing/academic-plotting/SKILL.md:266-268` | `docs/architecture/README.md:157-158` |
| P-2 评审上下文隔离 | 平台的模型评审段未实现；本仓的 `reviewer-guidelines.md` 与 ARA `rigor-reviewer` 都是评审提示词，文中没有要求换一个会话或 agent 来评（两份里搜 subagent、fresh context、separate session 都没有命中），这次没深读 | `20-ml-paper-writing/ml-paper-writing/references/reviewer-guidelines.md`、`22-agent-native-research-artifact/rigor-reviewer/SKILL.md:1-9` | `docs/architecture/README.md:152` |
| P-11 指南与领域 skill 隔离 | 平台的 skill 分两处库：`skills/`（通用，两层都拿到）与 `domains/<包>/skills/`（领域，只进执行层）。写作四个都按 ML / 系统会议写（页数、清单、模板），维护者也明确把本库限定在 AI/ML 研究；放进哪一处库，平台文档没有对应的判据 | `20-ml-paper-writing/ml-paper-writing/SKILL.md:446-461`、[^i58] | `docs/architecture/README.md:161`、`platform/framework/skills/library.py:79-91` |

## 6. 成熟度

| 项 | 实况 | 证据 |
|---|---|---|
| 测试 | 全仓没有测试文件；npm 包 `"test": "node --test"` 找不到任何测试，仓库根 `package.json` 的 test 是 npm 初始化留下的 `exit 1` 占位；`publish-npm` 发包前不跑测试；skill 内容的四项自动检查在 `CONTRIBUTING.md` 里标「when implemented」，至今没实现，外部提议帮忙（#69）未答复 | `packages/ai-research-skills/package.json:12`、`package.json:9-11`、`.github/workflows/publish-npm.yml:59-69`、`CONTRIBUTING.md:446-450`、[^gh-issues] |
| CI | `check-inventory`：只核 skill 总数与分类数；`sync-skills`：把改动的 skill 打 zip 推到 Orchestra 自家接口（要仓库 secret）；`publish-npm`：版本号变了就发 npm；`claude`：成员评论 `@claude` 时跑 Claude Code Action。没有一条校验 frontmatter、链接或代码块 | `.github/workflows/check-inventory.yml:25-31`、`.github/workflows/sync-skills.yml:65-187`、`.github/workflows/publish-npm.yml:26-69`、`.github/workflows/claude.yml:15-27` |
| 发版 | GitHub release 10 个（v0.10.0 到 v1.7.2），另有只打 tag 的 v1.0.0；README 写的 v1.6.0（4 月，ARA 分类）没有 tag 也没有 release。版本号有四套：npm 包 1.7.2、各 skill 自己的 `version`（`ml-paper-writing` 1.2.0）、`CITATION.cff` 1.4.0、仓库根 `package.json` 1.0.1。仓库没有 CHANGELOG 文件，版本说明写在 README 的「Recent Updates」里 | [^gh-rel]、`README.md:506-727`、`CITATION.cff:6`、`package.json:3` |
| 维护节奏 | 默认分支 220 个提交：2025-11 53、12 月 8、2026-01 44、02 40、03 55、04 13、05 0、06 7，之后没有。主力作者 zechenzhangAGI 136 个、AmberLJC 42 个，共 16 个作者身份（含 `claude` 8 个） | [^gh-commits] |
| issue 与 PR | 35 个 issue（12 开）、43 个 PR（11 开）；2026-06-25 以来 17 条 issue / PR 只有 #72 有一条维护者回复（07-25），PR 零 review | [^gh-issues] |
| 这四个 skill 的改动 | `ml-paper-writing` 2026-01-22 加入（当天另有三次提交补引用警告、模板用法、写作来源），03-26 挪进子目录，03-30 加「引用本库」一节，04-10 拆出 `systems-paper-writing`；`academic-plotting` 03-25 一次加入之后没动；出想法两个 02-19 一次加入之后没动 | [^gh-commits]、[^pr24]、[^pr41] |
| 许可证 | `LICENSE` 是 MIT，版权行「Claude AI Research Skills Contributors」；每个 skill 的 frontmatter 写 MIT；仓库根 `package.json` 写 ISC。模板目录里的第三方文件自带许可：`natbib.sty`、`fancyhdr.sty` 是 LPPL，会议样式文件（`icml2026.sty`、`aaai2026.sty` 等）来自各会议，文件里没有许可声明；README 只有一句「个别 skill 引用的库许可证可能不同」。`video-promo/` 依赖 Remotion，它用自己的两档许可（个人、3 人以内的营利机构、非营利机构免费，更大的营利机构要买公司许可）[^remotion]，与 skill 本身无关 | `LICENSE:1-3`、`package.json:18`、`20-ml-paper-writing/ml-paper-writing/templates/colm2025/natbib.sty:12-14`、`20-ml-paper-writing/ml-paper-writing/templates/colm2025/fancyhdr.sty:10`、`README.md:452`、`video-promo/ai-research-skills-promo/package.json:11-16` |

## 7. 还没弄清的问题

1. 引用示范代码的实际请求量：按 `semanticscholar` 库源码，`for` 迭代会一路翻页到 1,000 条上限（2.3），但没跑；在不带 key 的公共限流下一次 `cite()` 会不会被限流卡住、库遇到 429 怎么重试，没查。示范代码不钉库版本，旧版本库的迭代行为是否相同也没查。
2. Exa MCP 托管端点匿名可用的额度有多大、从课题组网络能不能连上，没查（「匿名可用、有限流」只是 Exa README 的自述）。
3. 从课题组网络能不能访问 Google Generative Language API 与 OpenRouter；`gemini-3-pro-image-preview` 这个预览模型名现在还能不能用，没查。
4. P-1 的边界：一个 skill 脚本拿单独的 key 调图像模型，算不算「框架调模型」、归不归执行层，纲领没写；P-25 的 `agents.yaml` 没有第三方 key 的位置，而两家适配器与 skill 脚本都继承起服务那个进程的全部环境变量，key 若放在环境里，agent 会话本身也读得到。这些要主人定，这里不下结论。
5. 维护者在 #56 说文献检索由 `deep-research` 覆盖：本仓没有，Orchestra-Research 组织下另两个公开仓库也没有；是在 Orchestra 平台上、在私有仓，还是记错了，不清楚。
6. 执行层能不能读到 skill 目录里的 `references/` 与 `templates/`：Claude Code 执行层的 Read 规则只放行工作目录（`platform/backends/claude_code.py:154`），skill 目录在工作目录之外，`ai4sci skill show` 也不打印这些文件的内容；平台现有的 `pdf` skill 正文同样让 agent 去看 `references/structured.md`（`platform/skills/pdf/SKILL.md:46`）。dontAsk 模式下读工作目录外的文件会不会被拒，代码里没看到放行规则，没实测。
7. NeurIPS 模板用 `final` 选项与写死作者，是有意给相机版用，还是拷贝时带进来的：加入它的提交（4643521）信息里没提。
8. 在 Codex 执行层上，正文里的 `python` 片段能不能跑：按平台 Codex 适配器文件头的实测记录，沙箱里的命令只能写工作区、没有网络（`platform/backends/codex.py:16-24,30-33`），所以要联网的示范代码在沙箱里连不上；沙箱里有没有可用的 Python 与 `semanticscholar` 包，没实测。
9. 2026-06-16 之后停更是暂停还是转移到 Orchestra 平台内部维护，GitHub 上看不出来；`sync-skills` 推送的目标接口是私有的。
10. 开着的外部 PR #71（换图像模型）与 #75（重写 `ml-paper-writing`）合不合、什么时候合，决定这两个 skill 的下一个样子；目前都零 review。
11. 这次没深读的 `systems-paper-writing`、`presenting-conference-talks` 与 ARA 三个（论文转结构化产物、会话记录、六维评审）与文献、写作、验证阶段也沾边，没有逐行读。

## 8. 调研方法

- 浅克隆到外层 `vendor/AI-Research-SKILLs`（gitignore 挡住），提交 773a529。只读：没装依赖，没跑仓库里任何代码，没在 GitHub 上留评论。
- 整库格式用 `find` 与逐个解析 frontmatter 统计（skill 数、字段、name 与目录名、正文行数、references 体积、`scripts/` 有无）；四个 skill 的 `SKILL.md` 与全部 references、NeurIPS 模板、绘图演示脚本逐行读；安装器与四条 workflow 读到函数级。
- 提交、release、issue、PR 用 `gh api` 拉全量（220 个提交、78 条 issue / PR），重点 issue 与 PR 读了正文与全部评论。
- 平台一侧读了纲领 P-1 到 P-25、`platform/framework/skills/library.py` 的校验、`ai4sci skill` 三个子命令、执行层白名单、两家适配器的隔离参数与子进程环境、`analysis` 与 `verify` 的描述符、`pdf` 与 `download` 两个 skill。
- 第一版之后做过一轮独立复查：逐条核对 `文件:行`，并对「没有脚本」「只有安装器能执行」「不调模型」「零测试」「CI 只核总数」这几条否定说法重新全仓搜了一遍；另用 `gh api` 读了 `semanticscholar` 库的分页源码、Exa MCP 的 README、K-Dense 仓库改名前的插件文件与 Remotion 的许可证，都是只读，没装、没跑。

[^gh-meta]: GitHub API `repos/Orchestra-Research/AI-Research-SKILLs` 与 `orgs/Orchestra-Research/repos`，2026-09-27 查：13,064 star、931 fork、创建于 2025-11-03、最后一次 push 2026-06-16、许可证 MIT；组织下公开仓库为 AI-Research-SKILLs、.github、Agent-Native-Research-Artifact-template 三个。<https://github.com/Orchestra-Research/AI-Research-SKILLs>
[^gh-commits]: GitHub API 默认分支提交列表（220 个），以及按路径 `20-ml-paper-writing`、`21-research-ideation`、`0-autoresearch-skill` 过滤的提交列表，2026-09-27 查。<https://github.com/Orchestra-Research/AI-Research-SKILLs/commits/main>
[^gh-rel]: GitHub API releases 与 tags，2026-09-27 查。<https://github.com/Orchestra-Research/AI-Research-SKILLs/releases>
[^gh-issues]: GitHub API issues 列表（含 PR，state=all，78 条），以及 #65 到 #82 的评论与 review，2026-09-27 查。<https://github.com/Orchestra-Research/AI-Research-SKILLs/issues>
[^i2]: issue #2「关于 skill 的验证问题」，维护者 2026-01-17 回复。<https://github.com/Orchestra-Research/AI-Research-SKILLs/issues/2>
[^i12]: issue #12「Invalid YAML frontmatter in ray-data and ray-train skills」，由 PR #13 关闭。<https://github.com/Orchestra-Research/AI-Research-SKILLs/issues/12>
[^i15]: issue #15「npx installer fails on Windows Powershell」，由 PR #16 关闭。<https://github.com/Orchestra-Research/AI-Research-SKILLs/issues/15>
[^i18]: issue #18「Open-source adoptation proposal for bibtex verify: bibtools」，维护者 2026-06-15 回复。<https://github.com/Orchestra-Research/AI-Research-SKILLs/issues/18>
[^i38]: issue #38「critical prompt injection in claude code github action」。<https://github.com/Orchestra-Research/AI-Research-SKILLs/issues/38>
[^i54]: issue #54「NLPM Audit: 7 CLAUDE.md inventory bugs + 1 security finding」，由 PR #60 关闭。<https://github.com/Orchestra-Research/AI-Research-SKILLs/issues/54>
[^i56]: issue #56「Scope question: Suppr literature-search and document-translation skills」，维护者 2026-06-15 回复。<https://github.com/Orchestra-Research/AI-Research-SKILLs/issues/56>
[^i57]: issue #57「Zip contains too many files (maximum 200)」，维护者 2026-06-15 回复。<https://github.com/Orchestra-Research/AI-Research-SKILLs/issues/57>
[^i58]: issue #58「Scope question: domain-specific engineering research workflow skill」，维护者 2026-06-15 回复。<https://github.com/Orchestra-Research/AI-Research-SKILLs/issues/58>
[^i65]: issue #65「should autoresearch be exposable as the only always-visible skill?」，无回复。<https://github.com/Orchestra-Research/AI-Research-SKILLs/issues/65>
[^i74]: issue #74「global uninstall removes unrelated symlinks from agent skill directories」，相关 PR #77、#82 未合。<https://github.com/Orchestra-Research/AI-Research-SKILLs/issues/74>
[^pr24]: PR #24「Add Research Ideation category」，2026-02-19 合并。<https://github.com/Orchestra-Research/AI-Research-SKILLs/pull/24>
[^pr41]: PR #41「add Academic Plotting skill with scientific-plotting demo」，2026-03-25 合并。<https://github.com/Orchestra-Research/AI-Research-SKILLs/pull/41>
[^pr71]: PR #71「support switchable image models, default gpt-image-2」，外部贡献者 2026-07-14 开，改 3 个文件（+72 −54），未合、零 review；说明里列的检查是 frontmatter 能解析、正文 495 行、模板能 `py_compile`、对照 OpenRouter 与 OpenAI 文档核接口形状，没有列实际调用。<https://github.com/Orchestra-Research/AI-Research-SKILLs/pull/71>
[^pr75]: PR #75「Refine ML paper writing around claims and reader-first figures」，外部贡献者 2026-08-02 开，改 2 个文件（+467 −925），未合、零 review。<https://github.com/Orchestra-Research/AI-Research-SKILLs/pull/75>
[^s2lib]: `danielnsilva/semanticscholar` 默认分支源码（最新 release v0.12.0，2026-03-29），2026-09-27 用 gh api 读：`semanticscholar/PaginatedResults.py` 的 `__iter__` 与 `_has_next_page`，`semanticscholar/AsyncSemanticScholar.py` 的 `search_paper`（相关性搜索 `max_results=1000`，`limit` 为每页条数、上限 100）。<https://github.com/danielnsilva/semanticscholar>
[^exa]: `exa-labs/exa-mcp-server` 的 README，2026-09-27 读：「The hosted MCP server works anonymously with rate limits. For higher limits and access to Exa Agent, use either OAuth or an API key.」<https://github.com/exa-labs/exa-mcp-server>
[^kdense-old]: K-Dense 仓库（现名 `K-Dense-AI/scientific-agent-skills`，旧名 `claude-scientific-skills` 会重定向）在提交 575404d（2026-04-02）时的 `.claude-plugin/marketplace.json`：插件名 `scientific-skills`，清单含 `./scientific-skills/literature-review`；该文件在提交 398fc37（2026-04-10）被删。2026-09-27 用 gh api 读。<https://github.com/K-Dense-AI/scientific-agent-skills>
[^remotion]: `remotion-dev/remotion` 的 `LICENSE.md`，2026-09-27 读。<https://github.com/remotion-dev/remotion/blob/main/LICENSE.md>
