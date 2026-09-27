---
title: Academic Research Skills 代码级深读
subtitle: 科研 AI 能力选型 · 文献、假设、写作三阶段候选 · 4.4 万行提示词的 Claude Code 插件，和围着它的 27 万行确定性脚本
kind: 开源项目选型深读（只读代码，不跑、不装依赖）
date: 2026-09-27
scope: 仓库 https://github.com/Imbad0202/academic-research-skills，浅克隆到 vendor/academic-research-skills，提交 e79085d（2026-09-25，v3.22.2 发版后一次文档提交）；读了插件清单、hooks、commands、agents、四个 skill 的 SKILL.md 与主要 agents / references、shared 的协议与契约、scripts 里运行时会被调起的脚本与几支关键 lint、docs 下的 ARCHITECTURE / CONTROL_AVAILABILITY / DATA_FLOWS / STAGE_CAPABILITY_MATRIX / SETUP / PERFORMANCE、POSITIONING、GOVERNANCE、LICENSE、evals 与 plugin-evals 的说明、CI 配置；GitHub 上的 release、issue、提交统计用 gh api 查（2026-09-27）；docs/design 下 100 多份设计稿与 2500 行 CHANGELOG 只按关键词抽读，不读各语言 README 翻译；Codex 版是另一个仓，只用 gh api 读了它的元数据、VERSION 与 CHANGELOG 开头，没读代码；平台一侧对照内仓提交 de3d948；文中 文件:行 不带前缀的均相对该仓库根，带 platform/ 的相对内仓根，标「外层」的相对外层仓根；2026-09-27 经过一轮独立复查，改动见第 8 节末
status: 第一版
---

> **结论先行**：ARS 是一个 Claude Code 插件：4 个 skill（deep-research、academic-paper、academic-paper-reviewer、academic-pipeline）、16 条 `/ars-*` 命令、2 个 hook、3 个插件子 agent。干活的主体是约 4.4 万行 markdown 提示词，39 个角色里除 3 个插件子 agent 外，默认都由当前会话的模型在同一个会话里按角色提示词依次执行（`docs/PERFORMANCE.md:55`）。仓库另有 27 万行 Python：一半是测试，五分之一是 `check_*` 脚本（多数是把提示词文本钉住的 CI lint，含整文件 sha256 锁）；三十多支脚本在提示词里给了运行方式，不都在默认流程里（运行账本、修订补丁的确定性应用、PDF 页数预检、审稿面板算术复核、缩写检查、投稿包校验等）。
>
> **是不是**：README 上最显眼的几项，代码里的实现与 README 的说法有落差。「每个阶段停下等人确认」「7 模式诚信闸门」「让步门槛」「防泄漏」「Style Calibration」「Writing Quality Check」都是提示词，作者自己在 `docs/CONTROL_AVAILABILITY.md:96-103` 写明是「prompt-level, trust-based controls」；Writing Quality Check 里只有缩写检查是脚本。`ARS_CLAIM_AUDIT=1` 没有任何代码读它：打开后是一个提示词 agent 让模型逐条引用当 judge；同名的 Python 流水线是依赖注入的参考实现，仓库里没有生产调用方，自带的校准测试用的是「原样返回金标」的桩 judge。v3.11 的四索引引用存在性闸门是真的确定性代码（Semantic Scholar、OpenAlex、Crossref、arXiv，免 key，SQLite 缓存），但诚信 agent 的提示词里没有给出在 Stage 2.5 / 4.5 调它的命令，写的是让模型按协议自己查 S2、逐条 WebSearch；它唯一的命令行入口 `verify_passport.py` 默认拒绝输出，文件头说真正的数据对应由「Stage 4→5 流水线或 formatter 批处理」接，而那条 Python 流水线在仓库里没有生产调用方。编排提示词里还有一道 v3.6.7 的交叉模型审计闸门：synthesis 等三个角色交付之后，要一份由会话外手动运行的 Codex 审计脚本产出的审计记录，提示词写明不可跳过；SETUP 的最小配置与 CONTROL_AVAILABILITY 都没提它。作者的能力矩阵 16 行里 10 行行为证据是 NOT_RUN，外部或人类结果证据 16 行都是 none。这些上限作者自己多半写在文档里，大量段落注明「不是运行时保证」。
>
> **和平台对照**（只列事实）：平台文献阶段只有助理手写的 `sources.md` 与 pdf、download 两个 skill，假设、写作两个阶段没有能力也没有主文件；ARS 在这三个阶段都有相近的模式（假设阶段对应的是研究问题与方法蓝图；苏格拉底模式下不替研究者生成候选问题，full 等模式里 `research_question_agent` 会从研究者给的题目生成 3–5 个候选研究问题）。它的格式接近 agentskills.io；拿平台自己的校验函数跑四个 SKILL.md，每个报两处（metadata 里有列表值、正文 524 至 761 行超过 500）；脚本一项不报，是因为四个 skill 目录里都没有 `scripts/`，运行时要叫的脚本全在仓库根 `scripts/`，没有一个带 PEP 723 头。它还依赖 Claude Code 的 Skill / Agent 工具、hook、`${CLAUDE_PLUGIN_ROOT}` 与交互式的用户回合；平台执行层是带隔离参数的一次性 `claude -p` / `codex exec`，Bash 白名单只有 `ai4sci skill`。许可证 CC BY-NC 4.0，覆盖代码。
>
> 怎么读：第 1 节逐条对账 README 与代码，第 2 节是一次运行怎么走，第 3 节是设计理由与作者踩过的坑，第 5 节和平台规则逐条对照，第 7 节是没弄清、要靠外层仓 #185 实测回答的问题（文中其余 `#n` 不加说明的都是 ARS 仓的 issue）。横向对比见同目录的 [README.md](README.md)。

## 1. 是不是

### 1.1 仓库里放了什么

| 目录 | 放什么 | 规模 | 证据 |
|---|---|---|---|
| `.claude-plugin/` | 插件清单与 marketplace 清单，列 4 个 skill，版本 3.22.2，许可证写 CC-BY-NC-4.0 | 2 个 JSON | `.claude-plugin/plugin.json:3,11`、`.claude-plugin/marketplace.json:13-20` |
| `skills/` | 4 个符号链接，指向仓库根的四个 skill 目录，插件从这里发现 skill | 4 个链接 | `git ls-files -s skills`（模式 120000） |
| `deep-research/` `academic-paper/` `academic-paper-reviewer/` `academic-pipeline/` | 每个 skill：`SKILL.md` + `agents/`（角色提示词）+ `references/`（协议）+ `templates/` + `examples/` | SKILL.md 536–775 行（去掉 frontmatter、按平台校验的算法是正文 524–761 行）；agents 38 个文件 1.65 万行；references 86 个 md 1.75 万行；四个 skill 目录都没有 `scripts/` | `wc -l */SKILL.md`、`ls <skill>/` |
| `agents/` | 3 个插件子 agent（synthesis、research_architect、report_compiler），与 skill 内同名文件逐字节相同；frontmatter 带 `model: inherit` 与工具白名单 `Read, Write, Edit, Grep, Glob` | 3 个文件 1025 行 | `agents/synthesis_agent.md:1-6` |
| `commands/` | 16 条命令。13 条模式命令只做一件事：调 Skill 工具加载对应 skill 并带上模式名；3 条工具命令（mark-read、unmark-read、cache-invalidate）直接跑 Python | 250 行 | `commands/ars-full.md:1-14`、`commands/ars-mark-read.md:13-16` |
| `hooks/` | `SessionStart` 跑 `scripts/announce-ars-loaded.sh`（注入命令清单、路由规则、更新提醒）；`PreToolUse` 对 Write / Edit / MultiEdit / Bash 跑写入范围守卫 | 2 个文件 | `hooks/hooks.json:3-24` |
| `shared/` | 跨 skill 的协议（交接 schema、交叉模型核对、风格校准、诚信边界、路由规则）、107 个 JSON 契约文件（多数是 JSON Schema）、审稿标准来源快照；`shared/agents/compliance_agent.md` 是第 39 个角色 | md 约 8000 行，JSON 116 个 | `shared/handoff_schemas.md:676`、`shared/contracts/`、`shared/model_tiering.md:62,74` |
| `scripts/` | 全部 Python / shell：顶层 `test_*` 217 个文件 13.5 万行，`check_*` 114 个 5.5 万行，其余 106 个 7.4 万行；5 个子目录共 186 个文件：`adapters/`（Zotero、Obsidian、文件夹三个文献导入器）、`verification_gate/`（1 个文件）、`cross_model_verification/`（jq 过滤器）、`fixtures/`、`legacy/` | 623 个文件 27.7 万行 | 按文件名前缀统计 |
| `tools/` | 从另一个项目整份拷来的发版纪律脚本 | 6 个文件 | `tools/release-discipline/README.md:1-5` |
| `evals/` `plugin-evals*/` | 金标集、留出集测量记录、`claude plugin eval` 用例 | 见[第 6 节](#6-成熟度) | `evals/README.md` |
| `docs/` `audits/` | 架构、能力矩阵、数据流、风险登记、100 多份设计稿；每月一次的「提示词债」清理审计 | docs 125 个文件 5 万行 | `docs/ARCHITECTURE.md` |
| `pi/` | 社区维护的 Pi 编码 agent 包装层 | 4 个文件 | `pi/README.md:1-12` |
| `.claude/CLAUDE.md` | 仓库自己的开发说明与路由规则，只在仓库目录里启动的会话加载 | 405 行 | `docs/CONTROL_AVAILABILITY.md:110-123` |

`check_*` 前缀不等于 CI lint：其中一部分（`check_acronyms.py`、`check_phase_conformance.py`、`check_panel_synthesis.py`、`check_re_review_synthesis.py`、`check_revision_token_conservation.py`，以及 `check_committee_correspondence.py`、`check_review_pathway_output.py`、`check_literature_corpus_schema.py` 等）是提示词在运行中或用户手动叫起来的检查器，其余是 CI 里查提示词文本的 lint（`academic-paper/references/committee_correspondence_protocol.md:159`、`shared/references/review_pathway_rule_trace_protocol.md:126`、`academic-pipeline/references/adapters/overview.md:143`）。

### 1.2 README 说的能力，代码里是什么

形态一栏主要是四种：**提示词**（模型照着做，没有代码约束）、**运行时脚本**（提示词给了命令、会话去跑）、**库未接线**（有确定性代码，但提示词里找不到调用它的命令）、**CI lint**（只在仓库 CI 里查文本，从不在用户机器上跑）。

| README 说的 | 代码里 | 形态 | 证据 |
|---|---|---|---|
| 13 / 12 / 7 个 agent 组成的团队 | skill 内 38 个角色文件（deep-research 实有 14 个）加 `shared/agents/compliance_agent.md`，共 39 个角色；只有 3 个注册成插件子 agent，其余是 skill 内模板，主会话 inline 执行。作者 2026-08 把分发文案里的「39-agent ensemble」删掉，理由是默认 inline 路径不提供执行上的独立性 | 提示词 | `README.md:100-102`、`docs/PERFORMANCE.md:45-55`、`CHANGELOG.md:199` |
| 每个阶段停下等人确认 | `IRON RULE` 一段文字；流水线状态记在对话里，压缩会改写它；v3.22.2 加了运行账本兜底，但账本条目由编排提示词自己写 | 提示词 + 可选账本脚本 | `README.md:21`、`academic-pipeline/SKILL.md:183`、`academic-pipeline/agents/state_tracker_agent.md:146`、`academic-pipeline/agents/pipeline_orchestrator_agent.md:807` |
| Stage 2.5 / 4.5 跑 7 模式阻断清单 | `integrity_verification_agent.md` 886 行提示词，要求每条参考文献都走 WebSearch 并留审计记录（同一文件的 A0 路由表又写 S2_VERIFIED 可跳过 A1，两处并存）；判定由模型做，确定性部分是论断登记覆盖差与证据行两支脚本，修订轮另加数字 / 引用守恒检查与论断强度漂移处置两支 | 提示词为主 | `README.md:29`、`academic-pipeline/agents/integrity_verification_agent.md:18-19,110-115,159-165,492,539,605-611`、`docs/STAGE_CAPABILITY_MATRIX.md:131-133` |
| Semantic Scholar API 核对，标题 Levenshtein ≥ 0.70（ARCHITECTURE 标为机器闸门） | 协议文档告诉模型 GET 哪个 URL、按什么阈值算相似度；诚信 agent 的 A0 就是让模型照它做 | 提示词 | `docs/ARCHITECTURE.md:257`、`deep-research/references/semantic_scholar_api_protocol.md:21-37`、`academic-pipeline/agents/integrity_verification_agent.md:104-115` |
| v3.11 确定性四索引引用存在性闸门 | `verification_gate/__init__.py` 345 行 + 四个 urllib 客户端（`scripts/semantic_scholar_client.py` 等）+ SQLite 缓存 + `verify_passport.py` 命令行；命令行默认拒绝输出（汇总要求每条引用有 `ref_slug`，只读 Passport 拿不到），加 `--synthetic-ref-slug` 才出诊断用结果，文件头说真正的对应由「Stage 4→5 流水线或 formatter 批处理」接；非测试代码里直接 import 它的只有这个命令行，另有评测脚本 `run_evals.py` 按金标集清单里的入口名调它，其余出现处是注释与 lint；CI 只用夹具测；诚信 agent 说「可执行层就是这个闸门」，但没有写调用命令 | 库未接线（运行时由谁调，未弄清） | `scripts/verification_gate/__init__.py:1-22`、`scripts/verify_passport.py:1-18`、`academic-pipeline/agents/integrity_verification_agent.md:119`、`docs/STAGE_CAPABILITY_MATRIX.md:61-71` |
| v3.6.7 交叉模型审计闸门（marketplace 描述写「Includes v3.6.7 cross-model audit gate」） | 编排提示词 §3.5：`synthesis_agent`、`research_architect_agent`（survey-designer 模式）、`report_compiler_agent`（abstract-only 模式）交付后的每个阶段转换，要一条审计记录才放行，没有记录就 BLOCK，「不可跳过」；记录由 `scripts/run_codex_audit.sh`（1205 行，调 `codex exec`，默认 `gpt-6-astra` xhigh）产出，脚本头规定不许由产出交付物的同一会话调用，只能人在别的终端、CI 或 SubagentStop hook 跑；SubagentStop hook 在 v3.7.0 被砍掉，插件的 `hooks.json` 里没有；设计稿自己写「没装 codex CLI 的新用户会在第一个 synthesis 阶段被硬拦」 | 提示词 + 会话外手动跑的 Codex 脚本 | `.claude-plugin/marketplace.json:12`、`academic-pipeline/agents/pipeline_orchestrator_agent.md:531-560`、`scripts/run_codex_audit.sh:4-8,802-810`、`CHANGELOG.md:1412`、`docs/design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md:2197-2201` |
| `ARS_CLAIM_AUDIT=1` 逐条核对论断是否被引文支持 | 见 1.4 | 提示词 + 未接线的参考实现 | `academic-pipeline/SKILL.md:44` |
| Style Calibration 学习作者文风 | 让模型读 3 篇以上样文，按 6 个维度自己估算后写成 Style Profile；没有任何脚本算句长均值、标准差 | 提示词 | `shared/style_calibration_protocol.md:34-75`、`academic-paper/agents/intake_agent.md:240-262` |
| Writing Quality Check 抓 AI 腔 | 一份词表与检查清单，明确「不是禁词、不阻断」；v3.22.2 起多了一支缩写检查脚本 | 提示词 + 一支运行时脚本 | `academic-paper/references/writing_quality_check.md:11,15-47,151-183` |
| 防泄漏（缺材料标 `[MATERIAL GAP]`，ARCHITECTURE 标为机器闸门） | 写作 agent 的规则文字，没有脚本 | 提示词 | `docs/ARCHITECTURE.md:259`、`academic-paper/references/anti_leakage_protocol.md:48-49` |
| VLM 图表核对（ARCHITECTURE 标为机器闸门） | 可选步骤：渲染图、交给多模态模型按 10 点清单查、最多改 2 轮；不可用就跳过 | 提示词 | `docs/ARCHITECTURE.md:260`、`academic-paper/agents/visualization_agent.md:403-411` |
| 魔鬼代言人让步门槛（反驳 1–5 分，≥4 才让步，ARCHITECTURE 标为机器闸门） | 提示词规则；对应 lint 的文件头写明「只钉文本，不测运行时审稿行为」 | 提示词 + CI lint | `README.md:296-305`、`docs/ARCHITECTURE.md:263`、`scripts/check_reviewer_finding_contract.py:23-26,362-366` |
| `data_access_level` 由 `check_data_access_level.py` 强制 | lint 只核对每个 SKILL.md frontmatter 里的值等于钉死的值；四个 skill 现在都是 `raw` | CI lint | `README.md:104`、`scripts/check_data_access_level.py:1-12`、`docs/ARCHITECTURE.md:140` |
| 写入范围守卫（单阶段 agent 不能写别的阶段目录） | 真的确定性 hook，但阶段范围只在 hook payload 的 `agent_type` 命中清单里 23 个名字时生效；主会话 inline 执行时没有 `agent_type`，除了不许写 ARS 插件自己的 hook / 守卫文件外一律放行 | 运行时 hook，覆盖面窄 | `scripts/ars_write_scope_guard.py:8-24,63-80,264-274,326-328,377-382`、`scripts/ars_phase_scope_manifest.json:5-6` |
| 审稿校准模式（量 FNR / FPR） | 协议、语料清单与维护者脚本在；从来没跑过，首次测量卡在 OpenReview 账号审批，另有相机版替换会泄露录用标签的问题 | 提示词 + 维护者脚本，未运行过 | `docs/STAGE_CAPABILITY_MATRIX.md:171-180`、[^i828] |
| 交叉模型核对 | 提示词里写好的 curl（OpenAI、Gemini、OpenAI 兼容端点），由会话执行；从回复里抽来源与「是否有检索依据」的判断写成 jq 过滤器、CI 有行为测试 | 提示词驱动的 HTTP + 确定性过滤 | `shared/cross_model_verification.md:444-500` |

### 1.3 诚信闸门与引用核对：哪些是脚本，哪些是提示词

| 环节 | 确定性脚本 | 只靠提示词（模型判断） | 证据 |
|---|---|---|---|
| 参考文献是否存在（Phase A） | 四索引闸门库与 `verify_passport.py`（运行时接线未弄清；命令行默认拒绝输出，见 1.2） | A0 按协议查 S2，S2_VERIFIED 的按路由表跳过 A1；A1 WebSearch，三次查不到判 NOT_FOUND；A2 核对作者、年份、刊名，并要求每条都有 WebSearch 审计记录 | `academic-pipeline/agents/integrity_verification_agent.md:104-165` |
| 撤稿 | `retraction_status.py` 把 OpenAlex `is_retracted` 与 Crossref 撤稿信号归一化 | 取数据由会话做 | `deep-research/agents/bibliography_agent.md:387-389` |
| 引用锚点格式（`<!--ref:slug-->` 后必须跟 `<!--anchor:kind:value-->`） | `check_v3_7_3_three_layer_citation.py` 能查草稿文件的格式 | 锚点指的页、句是否真支持论断，仍由模型判 | `scripts/check_v3_7_3_three_layer_citation.py:1-25`、`docs/STAGE_CAPABILITY_MATRIX.md:114-120` |
| PDF 页码可不可信 | `pdf_read_preflight.py`：页树声明、递归枚举、pypdf 三路页数一致才 PASS，只有 PASS 允许用页码当锚点 | — | `scripts/pdf_read_preflight.py:1-25` |
| 论断与引文是否一致（Phase E） | `claim_registry_coverage.py`（只查两类机械可检的漏登）、`evidence_rows.py`（证据行构建与校验） | 抽取论断、找原文、判支持与否 | `academic-pipeline/agents/integrity_verification_agent.md:478-575`、`docs/STAGE_CAPABILITY_MATRIX.md:125-134` |
| 数据核对（Phase C） | — | WebSearch 原始来源、查内部一致性 | `academic-pipeline/agents/integrity_verification_agent.md:202-225` |
| 原创性（Phase D） | — | WebSearch 8–12 词片段；报告里自己声明不是专业查重 | `academic-pipeline/agents/integrity_verification_agent.md:428-447,808` |
| 折磨短语（论文工厂痕迹） | `tortured_phrase_screening.py` 3502 行，确定性匹配；只在合成语料上 190/190；仓库不带短语表，要用户自己提供短语快照与带 sha256 的清单文件 | — | `docs/STAGE_CAPABILITY_MATRIX.md:136-145`、`deep-research/agents/bibliography_agent.md:411-415` |
| 7 模式 AI 研究失败清单 | — | 全部 | `academic-pipeline/references/ai_research_failure_modes.md` |
| 修订轮数字与引用漂移 | `check_revision_token_conservation.py`，只出提示不阻断；E6 论断强度漂移的处置记录由 `claim_strength_drift_disposition.py` 做字节绑定与重放 | E6 的漂移检测本身由模型做 | `academic-pipeline/agents/integrity_verification_agent.md:605-611,784` |
| 出稿前拒绝（formatter 规则 6–12） | — | formatter 提示词看到 HIGH-WARN 标记就拒绝输出；能力矩阵把它记为「prompt-contract refusal layer」 | `docs/ARCHITECTURE.md:111`、`docs/STAGE_CAPABILITY_MATRIX.md:198-207` |

诚信 agent 的判决是 PASS / FAIL，FAIL 进修订轮（2.5 失败回 Stage 2、4.5 失败走修订模式）后复查，最多 3 轮；仍不过就列出核实不了的条目，由用户选择手工处理、删掉这些引用或带「部分未核实」警告继续，决定要记录，重复放行时理由要求逐级提高（`academic-pipeline/SKILL.md:168,173,409`、`academic-pipeline/references/pipeline_state_machine.md:338-345`、`academic-pipeline/agents/pipeline_orchestrator_agent.md:1290`）。

### 1.4 ARS_CLAIM_AUDIT 实际做什么

- **没有代码读这个变量。** 全仓 `.py` / `.sh` / `.js` / `.json` / `.yml` 里 grep 不到 `ARS_CLAIM_AUDIT`，它只出现在 20 个 markdown 文件的 49 行里；`docs/SETUP.md:129-139` 的环境开关表也没有列它。提示词里也没有写「用什么命令读环境变量」，模型怎么知道它开了，未弄清。同样没有运行时代码读取的还有 `ARS_MODEL_TIERING`（全仓代码零命中）与 `ARS_PASSPORT_RESET`（只出现在一支 CI lint `scripts/check_passport_reset_contract.py:32` 与它的测试里）；有代码读取的是 `ARS_CROSS_MODEL*`、`ARS_VERIFICATION_CACHE_PATH`、`ARS_CACHE_REVALIDATE`、`ARS_CACHE_STALE_ADVISORY_DAYS`、`ARS_UPDATE_CHECK*` 等（对 `scripts/`、`hooks/` 下 `.py` / `.sh` grep `ARS_[A-Z_]*`）。审计 agent 说它的配置在「`academic-pipeline/SKILL.md` mode flags 里的 `claim_audit_config` 块」，SKILL.md 里没有这个块，全仓只有这个 agent 与两份设计稿提到它（`academic-pipeline/agents/claim_ref_alignment_audit_agent.md:79`）。
- **打开后的行为全在提示词里。** Stage 4 → 5 之间，编排提示词派 `claim_ref_alignment_audit_agent`（415 行）：锚点是 `none` 的引用直接记 RETRIEVAL_FAILED；其余按 `literature_corpus[]` 条目取原文（API、用户给的 PDF），取不到分三类：付费墙（`failed`，低级提示）、检索接口说查无此文（`not_found`，判为编造、HIGH-WARN）、临时故障（`audit_tool_failure`，中级提示）；取到了就让模型当 judge，一次调用同时问「是否支持」与「是否违反作者声明的约束」，judge 输出 SUPPORTED / UNSUPPORTED / AMBIGUOUS / PARTIAL / VIOLATED，再归到结果行，UNSUPPORTED 还要标出错在哪一环；另外对没有引用的句子查作者预先声明的否定约束（例如「不许用因果措辞」）有没有被违反，查论断强度漂移；引用超过 100 条按桶抽样（`academic-pipeline/SKILL.md:44`、`academic-pipeline/agents/pipeline_orchestrator_agent.md:562-618`、`academic-pipeline/agents/claim_ref_alignment_audit_agent.md:1-12,83-110,118-144,193-197`）。
- **结果怎么用。** 写进 `claim_audit_results[]` 等五个聚合，按 8 行矩阵分级；5 类 HIGH-WARN 让 formatter 的拒绝规则 6–10 不出稿（`docs/ARCHITECTURE.md:110-111`）。judge 是谁由调用方填 `judge_model`，填不出就记 `unknown`，缓存不跨运行复用（`academic-pipeline/agents/claim_ref_alignment_audit_agent.md:84-94`）。
- **那 1609 行 Python 是什么。** `scripts/claim_audit_pipeline.py` 文件头写明「在测试下跑」，检索与 judge 都是注入的函数，「生产调用方在自己的调度层接真客户端」（`scripts/claim_audit_pipeline.py:1-16`）；除测试外没有 `run_audit_pipeline`（`:989`）的调用方（非测试文件里提到它的只有 lint 与注释），也没有 `__main__`。`claim_audit_finalizer.py` 同样没有命令行入口；编排提示词把两者列为「实现」，另在 Stage 6 一处点名函数 `claim_audit_finalizer.py:render_stage6_histogram`，没给调用方式（`academic-pipeline/agents/pipeline_orchestrator_agent.md:592,617-618`）。
- **校准。** 25 条合成金标，门槛 FNR < 0.15、FPR < 0.10；测试里的 judge 是「原样返回金标」的桩（`scripts/test_claim_audit_calibration.py:75`），README 自己写了「checks the tooling, not a live judge」，默认关，上线要等真 judge 的校准结果（`README.md:33`）。

一句话：这个开关让编排提示词多走一段「逐条引用让模型当 judge、按矩阵分级、formatter 按标记拒绝」的流程；分级规则有一份被测试钉住的 Python 参考实现，运行时调不调它、judge 用哪个模型，由会话自己决定。

### 1.5 Style Calibration 与 Writing Quality Check

**Style Calibration**：入口是 academic-paper 配置访谈的第 10 步，可选。模型读用户给的样文（建议 3 篇以上），自己估 6 个维度：句长分布（均值、标准差、节奏）、段长、用词偏好（缓和词、连接词、引述动词、正式程度）、引用融入方式（叙述式占比、密度、位置）、修饰密度、各节语域变化，写成 Style Profile（Schema 10）挂在配置记录上，由 `draft_writer_agent` 与 `report_compiler_agent` 消费。使用时有优先级：学科惯例 > 目标期刊 > 个人风格，冲突时用惯例并记日志、提醒用户一次（`shared/style_calibration_protocol.md:21-133`、`academic-paper/agents/intake_agent.md:240-262`、`academic-paper/agents/draft_writer_agent.md:62`）。仓库里没有任何脚本计算这些统计量，数字是模型估的。

**Writing Quality Check**：`academic-paper/references/writing_quality_check.md` 195 行，A–E 五节是给模型的自查清单：25 个高频词（delve、tapestry、leverage 等，学科术语例外）、破折号与分号、「It is important to note」这类开场白、凑三条、同义词轮换、句长；文件开头写明这些「是判断提示，不是禁词表、不设标点配额」，不阻断交付（`:11`、`:15-147`、`:194-195`）。F 节是唯一的脚本：`scripts/check_acronyms.py`（1023 行，不调模型、不改文件）查缩写是否首次出现时定义、是否重复定义，由派发写作 agent 的会话在起草、摘要、审稿决定之后跑，结果只做提示（`:151-183`）。写作 agent 本身跑不了脚本（`:162`）。

两者都在 README 里被放在「帮你写得更好，不是帮你藏 AI」的定位下（`README.md:23`、`POSITIONING.md:75-81`）。

### 1.6 对 Claude Code 专有能力的依赖

| 机制 | 依赖的 Claude Code 能力 | 缺了会怎样 | 证据 |
|---|---|---|---|
| 模式命令与 skill 加载 | 插件 commands、Skill 工具、`${CLAUDE_PLUGIN_ROOT}`、frontmatter `disable-model-invocation` / `model` | 拷贝安装、仓库克隆、Cowork 等渠道没有 `/ars-*`（Pi 包装层为 Conditional）；claude.ai Project 只能读、Claude Science 只剩「方法论层」 | `commands/ars-citation-check.md:1-15`、`docs/CONTROL_AVAILABILITY.md:22-24,35-47` |
| 多角色分派 | Agent（Task）工具；3 个插件子 agent 由插件清单注册 | Cowork 等渠道「每个 skill 单独跑」，流水线的分阶段检查点不按设计运行 | `docs/CONTROL_AVAILABILITY.md:22,44` |
| 写入范围守卫 | PreToolUse hook 与 payload 里的 `agent_type` | 只在插件渠道生效（用户手动把 hook 配进自己的设置也行）；Windows 没有 Git Bash 时守卫不工作、每次调用记一条错误 | `scripts/ars_write_scope_guard.py:30-34`、`docs/CONTROL_AVAILABILITY.md:42,69-74,148-152` |
| 会话开头注入命令清单与路由规则 | SessionStart hook 的 `additionalContext` | 路由规则退回到「skill 加载之后才生效」 | `scripts/announce-ars-loaded.sh:77-152`、`docs/CONTROL_AVAILABILITY.md:110-129` |
| 子 agent 的工具白名单 | 插件 agent frontmatter 的 `tools:` | 拷贝安装时白名单不生效 | `docs/CONTROL_AVAILABILITY.md:43,69-74` |
| 按角色换模型档位 | Agent 工具的 `model` 参数 | 派不出子 agent 时 inline 跑并声明「不适用」 | `shared/model_tiering.md:50-54` |
| 等人确认 | 交互式会话：模型停下，等用户下一回合 | 无人回答时流程停在检查点 | `academic-pipeline/SKILL.md:183-191` |
| 查文献 | 会话自带的 WebSearch / WebFetch | Pi 等环境要自己装等价工具 | `docs/DATA_FLOWS.md:75-80`、`pi/README.md:18-25` |

作者给了 7 种安装渠道的可用性矩阵：「插件」渠道是唯一没有 Absent 项的，但它也有 5 项是 Conditional（路由规则、SessionStart 注入、写入守卫、靠 Python 的功能、交叉模型核对，各有前提条件）；拷贝 skill 目录时 hook、插件 agent 与白名单都不生效，靠仓库根 `scripts/` 的功能还要求保留完整克隆；claude.ai Project 只能读、什么都不执行（`docs/CONTROL_AVAILABILITY.md:15-47,78-87`）。

**Codex 版**：本仓 README 说 Codex CLI 用户装另一个仓 `Imbad0202/academic-research-skills-codex`，「同样的流程内容，按 Codex 原生方式打包成一个 `$academic-research-suite` skill，带 `ars-*` 别名」（`README.md:81`、`POSITIONING.md:5`、`docs/SETUP.md:295`）。那个仓的代码没读；它的 `VERSION` 是 3.22.0，CHANGELOG 说 3.22.0（2026-09-16）同步的是上游 v3.22.0 的提交 3c546bc，另外单独钉了一个 experiment-agent v1.1.0，比本仓 v3.22.2 落后两个补丁版本[^codexrepo]。本仓自己在三处用 Codex CLI：订阅通道的单条引用核对（`scripts/cross_model_codex_transport.py:1-8,507`，只接受 `Logged in using ChatGPT` 的登录态）；v3.6.7 审计闸门要的审计记录由 `scripts/run_codex_audit.sh` 调 `codex exec` 产出（见 1.2）；维护者自己的测量与发版前审查（例如 `scripts/run_review_criteria_constructive_value.py`，`docs/DATA_FLOWS.md:23-32`）。另有社区的 Pi 包装层，自己声明不提供 agent 隔离、没有 hook（`pi/README.md:7-12`）。

### 1.7 作者自己标的证据上限

`docs/STAGE_CAPABILITY_MATRIX.md` 由 `shared/contracts/capability/stage_capability_matrix.json` 生成，逐项写机制状态、行为证据和「最多能说到哪」：

| 行为证据 | 行数 | 例子 | 证据 |
|---|---|---|---|
| MEASURED | 3 | RQ 措辞提示在 48 条留出集上漏报 0.094、误报 0/16（单一 judge 模型、英文、一次测量）；修订漂移防护提示词 1/16 对 7/16（测的是浓缩版提示词，不是上线的流程）；折磨短语筛查合成语料 190/190 | `docs/STAGE_CAPABILITY_MATRIX.md:14-23,136-145,184-194` |
| MIXED | 1 | 审稿面板在 2 篇种子缺陷稿上召回 1.00，但严重度一致性 0.607 低于基线 0.672，是回退 | `docs/STAGE_CAPABILITY_MATRIX.md:160-169` |
| DESIGNED | 2 | 构思多样性测量、论断立场探针 | `docs/STAGE_CAPABILITY_MATRIX.md:26-35,73-82` |
| NOT_RUN | 10 | 引用存在性闸门、方法蓝图、综合、起草、论断核对、审稿校准、出稿拒绝等 | 同文件各节 |

16 行的「外部 / 人类结果证据」全部是 none。README 的样例论文是 2026-03 用 v2.3 跑的，作者注明「不代表当前性能」（`README.md:120`）。

## 2. 怎么做

### 2.1 入口

- **命令**：`/ars-full` 让模型调 Skill 工具加载 `academic-research-skills:academic-pipeline`，再按它的 SKILL.md 走；其它 12 条模式命令同理，带上模式名（`commands/ars-full.md:7-14`）。
- **自然语言**：SessionStart 注入的文字要求模型遇到匹配的请求先调核心 skill，再附上路由规则：显式意图直接进；给了横跨两个以上阶段的材料却没点名技能时，用 a–d 选项问用户要哪条流程；什么都没给也问（`scripts/announce-ars-loaded.sh:111`、`academic-pipeline/SKILL.md:23-40`）。
- **中途进入**：已有论文从 Stage 2.5 进，拿到审稿意见从 Stage 4 进（`academic-pipeline/SKILL.md:62-72`）；`resume_from_passport=<hash>` 在新会话里从 Material Passport 的重置点接着跑，前提是上一个会话开了 `ARS_PASSPORT_RESET=1`（`:74-83`）。
- 编排 skill 自己声明「不做实质工作，只识别阶段、推荐模式、派发 skill、管转换、记状态」（`academic-pipeline/SKILL.md:19`）。

### 2.2 主流程与人确认点

10 个阶段（含 2.5、3'、4'、4.5）加一个可选的 4→5 核对，每个阶段结束都有检查点；FULL 列出全部产物，连续两次「继续」后降为 SLIM 一行，诚信失败、审稿决定、定稿入口是 MANDATORY 不能跳（`academic-pipeline/SKILL.md:140-153,164-191`、`docs/ARCHITECTURE.md:17-41`）。

| 阶段 | 谁做 | 人确认什么 | 这一步里的确定性部分 | 证据 |
|---|---|---|---|---|
| 1 RESEARCH | deep-research（socratic / full / quick 等）：内部 6 个 phase，研究问题与方法蓝图、检索与来源核验、综合、成稿、主编 + 伦理 + 魔鬼代言人三方审、修订，三处魔鬼代言人检查点；synthesis 交付后按编排提示词要过 v3.6.7 审计闸门（见 1.2） | RQ Brief 与方法蓝图 | 本地 PDF 页数预检；文献导入器（会话外跑） | `deep-research/SKILL.md:189-304`、`academic-pipeline/agents/pipeline_orchestrator_agent.md:531-550,575` |
| 2 WRITE | academic-paper（plan / full）：Phase 0 配置访谈 → 1 文献策略 → 2 大纲 → 3 论证 → 4 起草 → 5a 引用合规 + 5b 双语摘要 → 6 内部审稿 → 7 排版 | 配置记录、大纲 | 缩写检查 | `academic-paper/SKILL.md:158-170` |
| 2.5 INTEGRITY | `integrity_verification_agent` | 确认诚信报告；失败回 2 修订后复查，最多 3 轮 | 论断登记覆盖差、证据行 | 1.3 节 |
| 3 REVIEW | academic-paper-reviewer full：领域分析定 3 个审稿席位 + 期刊契合席 + 魔鬼代言人，两段式（先只看契约、再看论文），合成者给 Accept / Minor / Major / Reject | 编辑决定 | Phase 1 泄漏检查（12 词片段比对）、合成算术复核 | `docs/ARCHITECTURE.md:103`、`academic-paper-reviewer/references/sprint_contract_protocol.md:34,68,231` |
| 3→4 | 修订辅导，最多 8 轮苏格拉底对话，可说「直接改」跳过 | 修订策略 | — | `docs/ARCHITECTURE.md:104` |
| 4 REVISE | academic-paper revision：写作 agent 交的是补丁文档，不是整篇重写 | 修订内容 | 草稿分块锚定 + 补丁确定性应用 | `academic-pipeline/agents/pipeline_orchestrator_agent.md:1290-1297` |
| 3' RE-REVIEW | 三次按契约的调用 + 追溯矩阵 | 复审决定 | `check_re_review_synthesis.py`（写明是 MANDATORY 运行时步骤） | `academic-pipeline/agents/pipeline_orchestrator_agent.md:1385-1392` |
| 4' RE-REVISE | 最多再修一轮，之后内容冻结；剩余问题写进「已知局限」 | 冻结 | — | `docs/ARCHITECTURE.md:108` |
| 4.5 FINAL INTEGRITY | 诚信 agent 深检一遍 | 确认报告 | 同 2.5 | `docs/ARCHITECTURE.md:109` |
| 4→5 CLAIM-AUDIT | 可选，见 1.4 | — | — | 1.4 节 |
| 5 FINALIZE | formatter：MD → DOCX（Pandoc）→ 问要不要 LaTeX → PDF（tectonic）；AI 使用声明按 15 个期刊或政策目标出 | 输出格式 | 投稿包校验 `verify_submission_package.py` | `academic-pipeline/SKILL.md:152`、`docs/ARCHITECTURE.md:111`、`academic-pipeline/agents/pipeline_orchestrator_agent.md:1409` |
| 6 PROCESS SUMMARY | 过程记录 MD + PDF，含协作深度章节与 AI 自评（让步率、谄媚风险） | 语言、最终确认 | — | `docs/ARCHITECTURE.md:112` |

### 2.3 怎么调模型

- **默认**：所有角色都由当前 Claude Code 会话的模型执行。3 个插件子 agent `model: inherit`，工具白名单里没有 Bash、没有联网；其余 36 个角色是 skill 内模板，主会话 inline 执行（`docs/PERFORMANCE.md:43-55`）。
- **命令钉模型**：16 条命令里 13 条 frontmatter 写 `model: sonnet`，`/ars-full`、`/ars-reviewer`、`/ars-revision-coach` 继承会话模型（`grep '^model:' commands/*.md`）。作者推荐的会话模型是 Fable 5.1 或 Opus 5.5 配 Max 套餐，Opus 5.5 要把 effort 调到 high 以上（`docs/PERFORMANCE.md:3-5`）。
- **换档**：`ARS_MODEL_TIERING=economy|quality-boost` 把 39 个角色分成判断型 26、执行型 13，用 Agent 工具的 `model` 参数派子 agent 升一档或降一档；派不出时 inline 并声明（`shared/model_tiering.md:50-54,62-83`、`docs/ARCHITECTURE.md:280`）。这个开关同样没有代码读取，靠会话自己知道它开了（见 1.4）。
- **第二模型**：`ARS_CROSS_MODEL` 只是配置，每个会话还要用户显式同意才发数据；调用方式是提示词里写好的 curl（OpenAI Responses、Gemini generateContent、OpenAI 兼容端点），或者 Codex CLI 订阅通道（只限引用核对）。用在诚信抽样复核、魔鬼代言人盲评、方法冻结与最终编辑决定两处「盲分歧检查」；分歧交给人，不取平均（`docs/SETUP.md:188-227`、`shared/cross_model_verification.md:199-372,444-500`）。
- **Python 基本不调模型**：会在用户一侧调模型的脚本只有 Codex 那几支：`cross_model_codex_transport.py`（经 `cross_model_codex_verify.sh`，起 Codex app-server 做单条引用核对）与 `run_codex_audit.sh`（v3.6.7 审计，`codex exec`），外加用户手动跑的 `cross_model_smoke_test*.sh`；OpenAI / Gemini 的交叉核对是提示词里的 curl，由会话执行。其余运行时脚本不调模型接口。会调 `claude -p` 的只有维护者自己做测量的脚本，例如审稿面板逐席隔离派发用 `claude -p --bare --no-session-persistence --strict-mcp-config --tools ""`（`docs/DATA_FLOWS.md:23-32,68-71`、`scripts/dispatch_e4_panel.py:530-560`）。
- **没有 MCP**：仓库不带 MCP 配置；代码里出现 MCP 的地方只是在隔离参数或禁止事件清单里把它关掉（`scripts/cross_model_codex_transport.py:593`、`scripts/dispatch_e4_panel.py:551`、`scripts/run_review_criteria_constructive_value.py:137`），提示词里没有 MCP 工具；文献索引走协议文档（会话自己发 HTTP）或 Python urllib 客户端。

### 2.4 数据怎么进出

**进**：用户消息（其中别人写的粘贴文本与运行中读到的网页、文档当数据、不当指令，`academic-pipeline/SKILL.md:94-108`）；用户给的 PDF、DOCX、Markdown；会话自己的 WebSearch / WebFetch 与四个索引 API；可选的 `literature_corpus[]`，由用户在会话外用导入器生成 `passport.yaml` + `rejection_log.yaml`，自带三个导入器（Zotero Better BibTeX 导出的 JSON、Obsidian、PDF 文件夹，都只读本地文件）（`docs/ARCHITECTURE.md:165-201`、`scripts/adapters/zotero.py:1-13`）；外部实验结果由研究者在 Stage 1 登记成 `experiment_provenance[]`，ARS 自己不跑实验（`README.md:110`）。

**出**：

| 产物 | 位置 | 证据 |
|---|---|---|
| 各阶段文件 | 当前工作目录下的 `phaseN_*/`，按 agent 约定（编号是各 skill 内部的 phase 号，三个 skill 都用 `phase1_*/`）；排版阶段固定名 `phase7_*/paper.md`、`paper.tex`、`references.bib`、`cover_letter.md`、`provenance_summary.md`；写作 agent 的草稿是 `phase4_*/draft.md` | `scripts/ars_phase_scope_manifest.json:9-31`（formatter 在第 25 行）、`scripts/check_pipeline_integrity.py:16-19`、`academic-paper/references/writing_quality_check.md:162` |
| v3.6.7 审计记录 | 会话外跑 `run_codex_audit.sh` 写到 `audit_artifacts/`，编排合并后进 Passport 的 `audit_artifact[]` | `scripts/run_codex_audit.sh:26`、`shared/handoff_schemas.md:895-899` |
| 阶段间交接物 | 12 种 schema（RQ Brief、书目、综合、草稿、诚信报告、审稿报告、修订路线图、回复信、Material Passport、风格档案、追溯矩阵、合规报告），多数以 markdown 段落在对话里传 | `shared/handoff_schemas.md:25-1133` |
| Material Passport | 用户自己命名的路径；不命名就没有这个文件 | `docs/DATA_FLOWS.md:94` |
| 运行账本 | Passport 旁边的 `<stem>_run_ledger.yaml`，哈希链，存用户原话 | `docs/DATA_FLOWS.md:95`、`scripts/run_ledger.py:1-25` |
| 引用核验缓存 | `~/.cache/ars/verification.db`（SQLite，条目 90 天过期） | `docs/DATA_FLOWS.md:91` |
| 终稿与过程记录 | MD / DOCX / LaTeX / PDF | `academic-pipeline/SKILL.md:152-153` |

**状态**：流水线状态记在对话里，压缩会改写（`academic-pipeline/agents/state_tracker_agent.md:146`）；v3.22.2 的运行账本就是为了压缩、续接、子 agent 返回后能对账（`academic-pipeline/agents/pipeline_orchestrator_agent.md:797-807`）。

### 2.5 运行时真正会被叫起来的脚本

提示词里以 `python scripts/...` 写法给出命令的有 27 支（grep 统计，方法见[第 8 节](#8-调研方法)），另有十来支以「Run `scripts/...`」「pipe to `scripts/...`」写法出现，两者去重约 37 支，其中一部分只在可选流程或手动步骤里。提示词规定这些脚本由派发方（主会话）跑，单阶段 agent 不跑；这些 agent 作为插件子 agent 派出时，守卫会拒它们的全部 Bash（`scripts/ars_write_scope_guard.py:13-22`、`academic-paper/references/writing_quality_check.md:162`）。主要的几支：

| 脚本 | 什么时候跑 | 做什么 | 证据 |
|---|---|---|---|
| `run_ledger.py` | 每个检查点开与关、压缩或续接后 | 追加哈希链条目；`report` 对照摘要里声称的决定与账本 | `academic-pipeline/agents/pipeline_orchestrator_agent.md:801-804` |
| `pdf_read_preflight.py` | Stage 1 导入每个本地 PDF | 三路页数一致才允许页码锚点 | 同上 `:575` |
| `ars_anchorize_draft.py` + `ars_apply_revision_patch.py` | 每个修订轮 | 草稿分块打锚；写作 agent 交补丁 JSON，脚本确定性应用 | 同上 `:1290-1297` |
| `check_phase_conformance.py`、`check_panel_synthesis.py` | reviewer full | 审稿第一段是否偷看了正文；合成算术复核 | `academic-paper-reviewer/references/sprint_contract_protocol.md:34,231` |
| `check_re_review_synthesis.py` | Stage 3' | 复审追溯矩阵校验 | `academic-pipeline/agents/pipeline_orchestrator_agent.md:1389` |
| `claim_registry_coverage.py`、`evidence_rows.py` | Stage 2.5 / 4.5 Phase E | 论断登记漏登、证据行 | `academic-pipeline/agents/integrity_verification_agent.md:492,539` |
| `check_acronyms.py` | 起草、摘要、审稿决定后 | 缩写定义检查 | `academic-paper/references/writing_quality_check.md:160-176` |
| `verify_submission_package.py` | Stage 5 formatter 之后 | 投稿包对照期刊限制 | `academic-pipeline/agents/pipeline_orchestrator_agent.md:1409` |
| `retraction_status.py`、`tortured_phrase_screening.py` | 文献导入 | 撤稿归一化、折磨短语（短语快照要用户自备） | `deep-research/agents/bibliography_agent.md:387-415` |
| `ars_mark_read.py`、`ars_cache_invalidate.py` | 用户命令 | 记「已读」声明、清缓存 | `commands/ars-mark-read.md:15`、`commands/ars-cache-invalidate.md:17` |

这些脚本的依赖写在两份清单里：`requirements-dev.txt`（pyyaml、ruamel.yaml、jsonschema[format]、pypdf、defusedxml，另两行 markdown-it-py、linkify-it-py 是给测试的）与只含 `pdf-inspector==0.2.6` 的 `requirements-pdf-content-classifier.txt`；`pyproject.toml` 只有 pytest 配置；没有锁文件，也没有一支脚本带 PEP 723 头（`grep -rl '^# /// script' scripts` 零命中）；脚本之间互相 import（例如 `scripts/verification_gate/__init__.py:29-40`）。

## 3. 为什么

### 3.1 设计取舍

| 取舍 | 解决什么 | 证据 |
|---|---|---|
| 人在环，不做全自动 | 引 AI Scientist 论文列的失败模式（实现 bug、幻觉结果、捷径、把 bug 当发现、编造方法、框架锁定、幻觉引用）与一篇综述转引的 PNAS 复现实验（人工 94%、AI 辅助 91%、AI 主导 37%，AI 辅助组发现的重大编码错误还少于纯人工组）作设计依据，README 注明这是设计理由、不是 ARS 自身有效的证据；明确拒绝「自主生成研究假设」「自主跑实验」「批量出稿」等机制 | `README.md:25-29,39`、`POSITIONING.md:13-37` |
| 提示词为主，Python 可选 | 核心 skill 不需要 Python，方法论层在 claude.ai、Claude Science、Cowork 等渠道也能读 | `docs/SETUP.md:17`、`docs/CONTROL_AVAILABILITY.md:37` |
| 模型靠不住的环节换确定性脚本 | 引用存在性（v2.7 的事后审计）；修订时让模型整篇重写会悄悄改坏文档（改成补丁 + 哈希前置条件 + 脚本应用，设计稿自己注明这是未验证的假设）；压缩丢决定（运行账本）；PDF 截断导致页码锚点错（页数预检） | `CHANGELOG.md:2433-2440`、`docs/design/2026-06-10-390-diff-patch-revision-mode-spec.md:52-95`、`scripts/run_ledger.py:1-10`、`scripts/pdf_read_preflight.py:1-9` |
| 把提示词当产品管 | 提示词就是交付物，编辑会悄悄改坏它；逐句钉「12 轮交叉审查都收敛不了」，于是对 5 个编排文件上整文件 sha256 锁，改一个字节 CI 就不过 | `scripts/check_pipeline_boundary_semantics.py:54-78` |
| 反谄媚、防框架锁定 | 魔鬼代言人对用户的反驳打 1–5 分，≥4 才让步、不许连续让步；苏格拉底导师每 3 轮判一次用户是在探索还是要结论 | `README.md:284-321` |
| 能力声明不超过证据 | 能力矩阵加分发文案 lint；2026-08 删掉「Production-grade」「39-agent ensemble」 | `CHANGELOG.md:199`、`docs/STAGE_CAPABILITY_MATRIX.md:1-10` |
| 引用存在性默认只提示 | 人文、非英文、区域期刊没有 DOI 多是覆盖缺口不是造假；只有 DOI / arXiv ID 被索引明确否认才判 false，拦截要用户自己选 strict | `academic-pipeline/agents/pipeline_orchestrator_agent.md:1246,1250-1258` |
| 第三方文字是数据不是指令 | 作者引 Opus 5.5 系统卡：它比旧模型更容易执行用户粘贴文本里藏的指令，同样文字经工具读入则在卡里的测试中 0/105 被执行 | `docs/PERFORMANCE.md:7`、`academic-pipeline/SKILL.md:94-108` |
| 交叉模型审计做成硬闸门 | v3.6.7 把「审计建议做」改成「没有审计记录就不放行」，并规定审计脚本不许由产出交付物的同一会话调用，理由是防止产出交付物的会话在没做审计时自称审计已通过（作者叫 Pattern C3）；设计稿承认这会让没装 Codex 的新用户在第一个 synthesis 阶段被拦，明确不提供跳过命令 | `scripts/run_codex_audit.sh:4-8`、`docs/design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md:2197-2209` |
| 定期清理「提示词债」 | 为某代模型写的补丁性提示会堆积（注释里写「5 天 9 个 tag 攒了一堆」），每月开 issue 审一遍 | `.github/workflows/harness-retirement-monthly.yml:3-14`、`audits/harness-retirement-*.md` |

### 3.2 作者踩过的坑

| 时间 / 编号 | 发生了什么 | 怎么改的 | 证据 |
|---|---|---|---|
| 2026-03，v2.7 | 样例论文过了 3 轮诚信检查，事后用 WebSearch 全量核对 68 条参考文献，21 条仍有问题（31%），含 4 条编造 | 诚信 agent 改成每条必须 WebSearch、取消「难以核实」这一档；后来 v3.3 加 S2、v3.11 加四索引闸门 | `CHANGELOG.md:2433-2440`、`README.md:134` |
| 2026-04，v3.0 | 作者自己用时发现三件事：魔鬼代言人只攻论点不攻前提；用户一反驳就让步；导师总想收尾出产物 | 让步门槛、意图识别、对话健康度 | `README.md:286-321` |
| #133，2026-05 | 按阶段派 agent 时，文献 agent 自己一路跑完 Phase 3–6，三个独立检查点全被跳过 | v3.9.2 路由澄清 + 提示词围栏 + 事后目录扫描；v3.10 上 PreToolUse 写入守卫 | [^i133]、`scripts/check_pipeline_integrity.py:1-20` |
| #454，2026-06 | Windows 上 `python3` 是应用商店占位；与另一个 hook 工具冲突，守卫以退出码 49 崩溃刷日志 | 改成 shell 启动器找真 Python，找不到就放行、不报错 | [^i454]、`hooks/run_guard.sh:3-21` |
| #857，2026-09 | 16 条命令里 13 条用相对路径引用插件文件、也不调 Skill 工具；工作目录不是插件根时，模式提示词根本没加载，模型只凭命令摘要作答。是用 `claude plugin eval` 对照实验发现的 | v3.22.1 改成先调 Skill、路径带 `${CLAUDE_PLUGIN_ROOT}` | [^i857]、`commands/ars-citation-check.md:8-14` |
| #892，2026-09 | 路由规则只写在 `.claude/CLAUDE.md`，插件与拷贝安装都不加载；修复前用 #133 夹具测，插件安装的会话在 Opus 5.5 上 12 个失败 6 个 | v3.22.2 复制进每个 SKILL.md 与 SessionStart 注入，lint 钉住副本一致；issue 仍开 | [^i892]、`CHANGELOG.md:41`、`academic-pipeline/SKILL.md:21-40` |
| #887，2026-09 | 上下文压缩与子 agent 返回会丢掉待决的决定与用户原话；依据是 Opus 5.5 系统卡，不是 ARS 自己复现的 | 运行账本 | [^i887] |
| #753，2026-08 | 分发文案里的说法超出证据 | 能力矩阵 + 文案 lint | `CHANGELOG.md:199` |
| #475 | 子 agent 派发继承 1M 上下文档导致报错，上游问题，仍开 | 记录追踪条件 | [^i475] |
| #828 | OpenReview 相机版替换会泄露录用标签，挡住审稿校准的第一次测量，仍开 | — | [^i828] |
| #595，2026-07 | 中文 DOI 多注册在 ISTIC / CNKI，Crossref 查不到，四索引闸门把中文引用几乎都判成 unresolvable，与编造分不开 | 写了独立的中文文献客户端（doi.org、Handle、NCBI，不爬 CNKI），没接进闸门，也没有命令行入口 | [^i595]、`scripts/chinese_literature_client.py:7-14,50-56`、`docs/DATA_FLOWS.md:64` |
| v3.7.0，2026-05 | 想用 SubagentStop hook 自动跑 v3.6.7 的 Codex 审计，hook 的 payload 里没有阶段与交付物信息，而且审计脚本不许由产出会话调用 | 砍掉，推迟到有阶段 / 交付物传递约定的版本；审计闸门仍在 | `CHANGELOG.md:1401,1412` |
| 审稿测量 | 种子缺陷召回 1.00，严重度一致性回退到 0.607 | 仍开 #648 | `docs/STAGE_CAPABILITY_MATRIX.md:160-169` |

## 4. 跑起来要什么

| 项 | 必需还是可选 | 实况 | 证据 |
|---|---|---|---|
| Claude Code | 必需 | 最新版；插件安装要求较新版本，完整机制只在插件渠道 | `README.md:55`、`docs/CONTROL_AVAILABILITY.md:19` |
| 模型与登录 | 必需 | `ANTHROPIC_API_KEY` 或 `claude` 首次登录；作者推荐 Fable 5.1 / Opus 5.5 + Max 套餐 | `README.md:56`、`docs/PERFORMANCE.md:3-5` |
| 会话的搜索与读网页工具 | 实际必需 | 查文献、核引用都靠它 | `academic-pipeline/agents/integrity_verification_agent.md:18` |
| 真 Python 3 | 作者标可选 | SETUP 说核心 skill 不要 Python，只有守卫与几项可选功能要；但提示词里有三十多支脚本给了运行方式，其中复审校验写明是 MANDATORY 运行时步骤、运行账本与 PDF 页数预检在默认流程里；依赖列在 `requirements-dev.txt`（pyyaml、ruamel.yaml、jsonschema、pypdf、defusedxml 等），无锁；`pdf-inspector==0.2.6` 单独可选；`bootstrap_timeline_yaml.py` 另要 requests | `docs/SETUP.md:17`、`academic-pipeline/agents/pipeline_orchestrator_agent.md:575,801,1389`、`requirements-dev.txt`、`requirements-pdf-content-classifier.txt`、`docs/DATA_FLOWS.md:66` |
| bash、curl、jq | 可选 | hook 启动器要 bash（Windows 要 Git Bash）；更新检查与交叉模型要 curl；交叉模型的来源过滤要 jq | `docs/CONTROL_AVAILABILITY.md:88-95,104-109`、`shared/cross_model_verification.md:456-460` |
| Pandoc、tectonic + 思源宋体繁中 | 可选 | 分别用于 DOCX 与 APA 7 PDF；没有就只出 Markdown | `README.md:57`、`docs/SETUP.md:65-97` |
| 文献索引 | 免 key | Semantic Scholar、OpenAlex、Crossref、arXiv；`S2_API_KEY`、`OPENALEX_API_KEY` 可选，只提速 | `docs/DATA_FLOWS.md:42-58` |
| 第二模型 | 可选 | `OPENAI_API_KEY` 或 `GOOGLE_AI_API_KEY`，或 `ARS_OPENAI_COMPAT_API_KEY` + `ARS_OPENAI_COMPAT_BASE_URL`（兼容端点没有联网检索）；或 Codex CLI ≥ 0.147 以 ChatGPT 登录（只限引用核对）；估算每次全流程多花约 0.6–1.1 美元 | `docs/SETUP.md:188-246`、`shared/cross_model_verification.md:95-130` |
| Codex CLI（v3.6.7 审计闸门） | 编排提示词写为不可跳过，用户文档没列 | `run_codex_audit.sh` 要 Bash 4+（macOS 自带的 3.2 不够）、`codex` 与能跑 `gpt-6-astra` xhigh 的凭据，由人在会话外跑；SETUP 的最小配置、CONTROL_AVAILABILITY、PERFORMANCE 都没提；实跑时缺它是否真被拦，未验证 | `academic-pipeline/agents/pipeline_orchestrator_agent.md:531-560`、`scripts/run_codex_audit.sh:4-8,41-46,802-810`、`docs/SETUP.md:7-13` |
| 其它网络 | — | 每天至多一次到 raw.githubusercontent.com 查版本，`ARS_UPDATE_CHECK=0` 关 | `docs/DATA_FLOWS.md:70` |
| 算力 | 无 GPU 要求 | 全流程约 20 万+ 输入、10 万+ 输出 token；README 估 3–7 美元，按 2026-09 价格 Opus 5.5 约 2.8 美元、Fable 5.1 约 7 美元 | `README.md:89`、`docs/PERFORMANCE.md:24,29` |
| 本地存储 | — | `~/.cache/ars/` 下 SQLite 缓存与更新状态；账本在 Passport 旁 | `docs/DATA_FLOWS.md:87-96` |
| 操作系统 | — | macOS、Linux 测过；CI 只有 Ubuntu；Windows 尽力而为，文件锁有 msvcrt 后备，分支账本在 Windows 上拒绝运行 | `docs/SETUP.md:35` |
| 语言 | — | 双语摘要的语言对注册表只有 `zh-tw-en` 一条，用户用中文写时默认繁体；README 说触发词只列英文与繁中，四个 SKILL.md 的 description 里实际还有韩文、西班牙文触发词 | `shared/output_language_pair.md:20-24`、`README.md:235-241`、各 SKILL.md 第 3 行 |
| MCP | 不用 | 仓库不带 MCP 配置，提示词不用 MCP 工具 | 2.3 节 |

## 5. 和平台对照

只列事实。平台一侧的依据：外层 `docs/architecture/README.md` 的 P-1、P-2、P-11、P-14、P-19、P-20、P-22、P-25，`platform/docs/add-a-skill.md`、`platform/docs/add-a-capability.md` 与对应代码。

### 5.1 三个阶段：平台现在有什么，ARS 对应什么

| 阶段 | 平台现在 | ARS 对应的 | 证据 |
|---|---|---|---|
| 文献 | 主文件 `sources.md` 由助理手写（`ai4sci output new literature`），不是能力产的；skill 有 pdf（论文 PDF → `paper.md` + `images/` + `structured.json`）与 download（git 仓库、单文件、HF 仓库，留收据）；两层 agent 用 CLI 自带的 WebSearch / WebFetch | deep-research 的 lit-review、three-way-scan、systematic-review（PRISMA，含偏倚风险与荟萃分析）、fact-check；检索策略与两轮筛选、证据分级、注释书目、综合与缺口分析（提示词）；四索引存在性库 + SQLite 缓存、撤稿与折磨短语脚本、Zotero / Obsidian / 文件夹导入器；中文文献客户端（未接线） | `platform/framework/capabilities/__init__.py:46-47`、`platform/docs/add-a-skill.md`「现在有的」表、`platform/backends/claude_code.py:40-42`、`deep-research/SKILL.md:142-160,363-367` |
| 假设 | 没有能力，`MAIN_FILES` 没有这一行；`add-a-capability.md` 定名举例用 `hypothesis.md`，未落地 | 没有单独的「假设」产物；RQ Brief 里有一个可选字段 `hypothesis`（初步假设，适用时填）。最近的是 RQ Brief（FINER 打分、范围、子问题；schema 写 1–10 分，`research_question_agent` 提示词写 1–5 分，两处不一致）与方法蓝图（范式、方法、数据策略、效度），苏格拉底导师五层追问与魔鬼代言人检查点。苏格拉底模式默认不替研究者生成候选问题，研究者明确要求才退出该模式并标明 AI 生成；full 等模式里 `research_question_agent` 会从研究者给的题目生成 3–5 个候选研究问题 | `platform/framework/capabilities/__init__.py:45-52`、`platform/docs/add-a-capability.md:36-52`、`shared/handoff_schemas.md:25-51`、`deep-research/agents/research_question_agent.md:31,55-59`、`POSITIONING.md:18-31` |
| 写作 | 没有能力、没有主文件；`add-a-capability.md` 用「论文初稿」`draft.md` 做例子，未落地 | academic-paper 11 个模式（full、plan、outline-only、revision、revision-coach、abstract-only、lit-review、format-convert、citation-check、disclosure、rebuttal-audit），reviewer 6 个模式，pipeline 全流程；出 MD / DOCX / LaTeX / PDF、双语摘要、AI 使用声明、模拟审稿与回复信；写作 agent 的草稿文件也叫 `draft.md` | `platform/docs/add-a-capability.md:142-151`、`docs/ARCHITECTURE.md:436-443`、`academic-paper/references/writing_quality_check.md:162` |
| 验证（参照） | `verify` 零模型核对分析稿里的数字与账本，写 `report.json` | 不跑实验、不核对实验真伪；只核对论文论断与研究者声明的外部实验是否一致，且由模型判 | `platform/framework/capabilities/verify/__init__.py:1-7`、`POSITIONING.md:47-51`、`README.md:110` |

### 5.2 重叠的部分

| 事项 | 平台 | ARS | 证据 |
|---|---|---|---|
| 找文献 | 助理用 WebSearch / WebFetch 找、手写 `sources.md` | 同样靠会话的搜索工具，另给四个索引的 HTTP 协议文档与 Python 客户端 | `docs/DATA_FLOWS.md:75-80` |
| 读 PDF | pdf skill 解析正文、表、图、参考文献 | 不解析正文（会话自己读）；只做页数一致性预检，可选 `--classify-content` 交给 pdf-inspector 出内容分类提示 | `platform/skills/pdf/SKILL.md:1-6`、`scripts/pdf_read_preflight.py:1-40` |
| 人确认 | `requirement.lock` 与产出目录里的 `signed.json`，助理会话里调签字一律被拒 | 提示词检查点 +「只有用户回合算决定」+ 运行账本；作者注明是纪律不是运行时保证 | 外层 `docs/architecture/README.md:169`、`academic-pipeline/agents/pipeline_orchestrator_agent.md:784-793` |
| 判定 | 能确定性判的用零模型代码 | 大部分由模型判；确定性部分是存在性、格式、算术、补丁应用、账本 | 外层 `docs/architecture/README.md:152`、1.3 节 |
| 模型评审隔离 | P-2：要模型判断的由框架另起隔离会话、只给产物，「尚未实现」 | 审稿面板默认同一会话 inline；逐席隔离派发只在维护者测量脚本里 | 外层 `docs/architecture/README.md:152`、`docs/PERFORMANCE.md:55`、`scripts/dispatch_e4_panel.py:530-560` |
| 产出与来源 | `<stage>/<n>/` + `meta.yaml` 记谁产的、读了谁 | `phaseN_*/` 目录 + Material Passport（`origin_skill`、`upstream_dependencies`、`content_hash`） | 外层 `docs/architecture/README.md:169-170`、`shared/handoff_schemas.md:710-730` |

### 5.3 接进来会碰到的平台规则

| 规则 | 平台怎么定 | ARS 的实况 | 证据 |
|---|---|---|---|
| P-1 执行层是唯一写代码与论文正文的 | 框架不调模型；助理只可手写材料清单这类东西 | ARS 的 Python 除 Codex 两支（引用核对通道、v3.6.7 审计脚本）外不调模型，写正文的是会话模型；ARS 设计成在同一个交互会话里既问人、又派角色、又写正文 | 外层 `docs/architecture/README.md:151`、2.3 节 |
| P-2 评审上下文隔离 | 见上表 | 见上表 | 同上 |
| P-11 指南只进协调层，领域 skill 只进执行层 | 两层清单分开 | ARS 的 SKILL.md 同时是流程指南（何时停、问什么）和执行内容（怎么写） | 外层 `docs/architecture/README.md:161`、`academic-pipeline/SKILL.md:181-191` |
| P-14 CLI 主导 | 助理只有 `ai4sci`；执行层 Bash 白名单只有 `ai4sci skill`；不裸跑 python | 提示词直接写 `python3 scripts/...`、`curl`、`jq`；3 条工具命令直接跑 python | 外层 `docs/architecture/README.md:164`、`platform/framework/skills/__init__.py:35-37`、`commands/ars-mark-read.md:15`、`shared/cross_model_verification.md:444` |
| P-19 只有人能确认，断点是产出要人签 | 签字是 `signed.json`；执行层是一次性会话：`claude -p ... --output-format stream-json`、`codex exec --json` | 检查点靠会话停下等用户下一回合；一次性执行层会话里没有用户回合 | `platform/backends/claude_code.py:157`、`platform/backends/codex.py:1` |
| P-20 主文件归阶段、能力只写自己的 `<stage>/<n>/`、skill 不开产出目录 | 假设、写作的主文件待第一个能力定名，定名照 P-13（角色名词） | ARS 在工作目录下自建 `phaseN_*/`，还写 Passport、账本、`audit_artifacts/`、`~/.cache/ars/`；文件名按它自己的约定（`draft.md`、`paper.md` 等） | 外层 `docs/architecture/README.md:170`、`platform/docs/add-a-capability.md:36-52`、2.4 节 |
| P-22 skill 按开放规范写、框架注入、脚本自带依赖 | frontmatter 只认 `name`、`description`、`license`、`compatibility`、`metadata`，metadata 必须字符串到字符串；正文不超过 500 行；`scripts/*.py` 要 PEP 723 头 + 锁文件；加载不靠 agent 的原生机制 | 用平台的 `load_skill` 直接校验四个目录，每个报两条：`metadata 要是字符串到字符串的映射`（`related_skills` 是列表）与正文超 500 行（627 / 583 / 524 / 761）；字段名都在范围内。脚本一项不报：四个 skill 目录里没有 `scripts/`，而平台的校验与 `ai4sci skill run` 都只看 skill 自己的 `scripts/*.py`；ARS 运行时要叫的脚本在仓库根 `scripts/`，没有一支带 PEP 723 头，且互相 import。每个 SKILL.md 还引用 16–29 个不重复的仓库内路径（`shared/`、`scripts/`、`docs/` 与其它 skill 的文件）；加载与分派靠 Claude Code 的 Skill、Agent 工具与插件机制 | `platform/framework/skills/library.py:26,32,144-150,205-209,218-229`、`platform/framework/skills/run.py:45-58`、各 SKILL.md frontmatter、[^agentskills] |
| P-25 底座归人，模型与思考深度按人的设置、只有具体值 | 执行层用哪家、什么模型由设置定 | 13 条命令在 frontmatter 钉 `model: sonnet`；`ARS_MODEL_TIERING` 自己按角色换档；3 个插件子 agent `model: inherit` | 外层 `docs/architecture/README.md:175`、2.3 节 |
| 执行层隔离参数 | Claude Code 带 `--setting-sources ""`、`--strict-mcp-config`、`--disable-slash-commands`、`--no-session-persistence`，注释写明因此不继承本机的 CLAUDE.md、hook、plugin、自定义 agent；本机 Claude Code 2.1.283 的 `claude --help` 对 `--disable-slash-commands` 的说明是「Disable all skills」；Codex 用私有 `CODEX_HOME`，本机的 plugins、hooks、用户 skills 都不进 | ARS 的 hook、`/ars-*` 命令、插件子 agent 都靠插件机制加载，skill 靠 Skill 工具加载 | `platform/backends/claude_code.py:36-39,46`、`platform/backends/codex.py:6-11` |
| 执行层默认预算 | `--max-turns 30`、`--max-budget-usd 2.0`，可用环境变量改 | 全流程估算 20 万+ 输入、10 万+ 输出 token，2.8–7 美元 | `platform/backends/claude_code.py:159-163`、`docs/PERFORMANCE.md:24,29` |
| 单独的模型 key | 底座走研究者自己的 agent 登录 | 交叉模型核对要另一家的 API key，或 Codex 订阅登录（只限引用）；v3.6.7 审计闸门要 Codex CLI 与能跑 `gpt-6-astra` 的凭据，由人在会话外跑 | 外层 `docs/architecture/README.md:175`、4 节 |

## 6. 成熟度

### 6.1 发版与维护节奏

| 项 | 实况 | 证据 |
|---|---|---|
| 年龄与提交 | 2026-02-26 建仓，798 个提交 | [^ghstats] |
| 发版 | 45 个 GitHub release（47 个 tag），v2.8（2026-03-22）到 v3.22.2（2026-09-25）；最近三版间隔 2–7 天；SETUP 自述「大约 1–2 周一版」；发版前有版本一致性、CHANGELOG 覆盖合并等门禁，tag 后再复查 | [^releases]、`docs/SETUP.md:288`、`GOVERNANCE.md:52-56` |
| 活跃度 | 近 26 周每周 3–168 次提交，最近 8 周每周 7–43 次；main 上最近的 CI 运行全绿（2026-09-24、09-25） | [^ghstats] |
| 人 | 维护者 763 / 798 个提交（约 96%），其余约 19 人各 1–8 个；单人维护，没有共同维护者、没有 SLA，停更即视为终止 | [^ghstats]、`GOVERNANCE.md:15-27,59-66` |
| issue 与 PR | 358 个 issue（87 个非维护者提）、508 个 PR、33 个 open | [^ghstats] |
| 开发方式 | 近期提交带 Claude Opus 5.5 的共同作者尾注；发版前做「dual-track」审查，CHANGELOG 里多写成一路 Claude Opus 子 agent 做安全审查、一路 Codex（GPT）审查；作者声明第二个模型不等于组织上的独立审查 | [^ghstats]、`GOVERNANCE.md:29-48`、CHANGELOG 中 `Dual-track pre-ship review (security opus subagent + codex …)` 各条 |
| 关注度 | 4.96 万 star、3835 fork；Codex 版 1.17 万 star，最后推送 2026-09-16 | [^ghstats]、[^codexrepo] |
| 文档体量 | CHANGELOG 2513 行（77 万字节），README 381 行，docs 5 万行 | `wc -l` |

### 6.2 测试、CI 与评测

- **CI**：14 个 workflow，全部 `ubuntu-latest`；作者自己分类为 8 个至少在一种事件上阻断、2 个只告警、1 个只开 issue、3 个 tag 推送后才检测；有 `test-count-monotonic`（测试数不许下降）、`pr-closes-issue`（PR 必须引 issue）（`docs/ARCHITECTURE.md:284-322`）。没有 macOS、Windows 的 CI。
- **测试**：`scripts/test_*` 217 个文件 + `tests/` 4 个顶层文件（另有 `tests/fixtures/`），约 7066 个 test 函数、13.5 万行。三类：运行时脚本的逻辑（夹具驱动，例如引用闸门的传输夹具、补丁应用、账本链）；104 个 `test_check_*` 对提示词文本 lint 做变异测试；整文件内容锁。全部离线：CI 不做任何真实索引或模型调用，workflow 里用到的 secret 只有 `GITHUB_TOKEN`，没有模型 key（`docs/DATA_FLOWS.md:83-85`、`.github/workflows/eval-harness.yml:131`）。
- **evals**：`evals/gold/` 4 个金标集在 CI 里跑，入口都是确定性函数；引用抽取那一套测的是 reducer 自己的分类，能力矩阵说它不是幻觉捕获率的独立真值（`evals/gold/*/manifest.yaml`、`docs/STAGE_CAPABILITY_MATRIX.md:67`）。`evals/heldout/suite_registry.json` 注册了 12 个套件（目录下另有 3 个未注册的套件目录），只有 3 个有已提交的测量 JSON（revision_claim_drift 2 次、rq_framing_offlist 2 次、tortured_phrase_conformance 1 次），reviewer_seeded_defects 有原始运行记录；这些由维护者用指定模型离线跑（`evals/heldout/suite_registry.json`）。
- **plugin-evals**：`claude plugin eval` 做有 / 无插件对照，三套合成用例共 18 个，本地跑、结果不入库；README 记录其中两例两组得分相同，说明基础模型本身就能处理（`plugin-evals/README.md:17-22,58,132`）。
- 小结见 1.7 节：能力矩阵 16 行，行为证据 MEASURED 3、MIXED 1、DESIGNED 2、NOT_RUN 10，外部结果证据全无。

### 6.3 许可证条款要点

- **授权范围**：CC BY-NC 4.0 全文在 `LICENSE`，版权人 Cheng-I Wu（`LICENSE:1-4`）。授权只限「为非商业目的」复制、分享，以及制作、分享改编作品（`LICENSE:156-165`）。NonCommercial 的定义是「主要目的不是商业利益或金钱报酬」（`LICENSE:126-132`）；Share 指向公众提供（`LICENSE:134-140`）。
- **覆盖代码**：许可证覆盖整个仓库，包括 27 万行 Python；`plugin.json`、`package.json` 都写 CC-BY-NC-4.0，GitHub 识别为 NOASSERTION[^ghstats]。作者自称「source-available，不是开源许可」（`POSITIONING.md:7`）。CC 官方 FAQ 不建议把 CC 许可用于软件，理由之一是它不含源码分发条款、与主流软件许可不兼容[^ccfaq]。
- **对「随平台分发」**：平台仓或安装包里带上 ARS 文件或改过的版本，属于分享（改编）作品，要保留作者署名、版权声明、许可声明、免责声明与原链接，注明是否修改并保留修改记录，附许可正文或链接（`LICENSE:237-266`）；分享改编作品时所用许可不得妨碍接收者遵守 BY-NC（`LICENSE:279-281`），下游接收者对 ARS 原有内容直接从许可人处按 BY-NC 获得授权、不能被加限制（`LICENSE:187-200`），即 ARS 这部分对下游仍然只能非商业使用。作者列的禁止用途包括基于 ARS 的商业托管服务、打包收费、机构付费部署，并注明这是「policy intent」，法律以许可正文为准（`POSITIONING.md:66-73`）。平台自身的许可证与 ARS 部分怎么并存，未弄清。
- **对「课题组内部用」**：作者把研究组、实验室、院系的非商业学术协作列为允许用途（`POSITIONING.md:53-58`）。CC 的解释是非商业看用途不看使用者身份，教育机构没有自动豁免[^ccnc]。组内使用不向公众提供时不构成 Share，但复制仍须出于非商业目的。有外部资助或企业委托的课题算不算非商业，未弄清。
- **仓库里的第三方内容**：审稿标准来源快照里有一条记录「出版方页面没有再分发许可」，因此只存哈希、不镜像页面（`shared/review_criteria_sources/msr-2027-technical-papers.2026-08-24.json:43`）。

## 7. 还没弄清的问题

1. **四索引闸门在运行时由谁调。** 文档说它在 Stage 2.5 / 4.5 触发（`docs/DATA_FLOWS.md:44-45`），诚信 agent 的提示词只说「从 summary 上读这些字段」（`academic-pipeline/agents/integrity_verification_agent.md:119`），A0 仍让模型按协议自己查 S2；全部提示词里没有调用 `verify_passport.py` 的命令，而这个命令行默认拒绝输出、文件头把真正的对应推给「Stage 4→5 流水线或 formatter 批处理」（`scripts/verify_passport.py:11-18`），那条 Python 流水线没有生产调用方。实跑时 `citation_verification_summary[]` 到底由谁生成、是不是模型照 schema 手写，要看外层仓 #185 的运行记录。
2. **模型怎么知道 `ARS_*` 开关开了。** `ARS_CLAIM_AUDIT`、`ARS_MODEL_TIERING` 没有代码读，`ARS_PASSPORT_RESET` 只在 lint 里出现；提示词也没写读环境变量的命令；开关是被会话 `echo` 出来、还是靠用户在对话里说，未弄清。审计 agent 指向的 `claim_audit_config` 配置块在 SKILL.md 里不存在，`max_claims_per_paper`、`judge_model` 这些配置实际从哪来，也未弄清。
3. **插件渠道下相对路径的脚本命令怎么找到插件根。** 编排提示词写 `python scripts/...`，三条工具命令写 `python3 scripts/ars_mark_read.py`（`commands/ars-mark-read.md:15`），都没带 `${CLAUDE_PLUGIN_ROOT}`，而用户会话的工作目录是自己的项目。#857 修的是 13 条模式命令。是否依赖 Claude Code 给 skill 注入的基目录，未验证。
4. **写入守卫实际覆盖多少。** 清单里 23 个名字，其中只有 synthesis_agent、research_architect_agent 同时是插件注册的子 agent（report_compiler 属 Bucket B，不在清单）；其余 21 个默认 inline，没有 `agent_type`，守卫除了保护 ARS 自己的 hook / 守卫文件外一律放行。开 `ARS_MODEL_TIERING` 派子 agent 时 `agent_type` 是什么，未查。
5. **审稿第一段「不看正文」在 inline 执行下成不成立。** 协议把第一段、第二段写成两次独立调用（`academic-paper-reviewer/references/sprint_contract_protocol.md:30-34`）；同一会话已经读过论文时，第一段的盲性从何而来；`check_phase_conformance.py` 只查 12 词片段是否被抄进第一段输出。
6. **放进平台执行层会怎样。** 本机 Claude Code 2.1.283 的 `claude --help` 把 `--disable-slash-commands` 说成「Disable all skills」，另有 `--plugin-dir` 可以只为本次会话加载一个插件目录；这两条和平台的 `--setting-sources ""` 叠在一起时 ARS 能不能加载、Skill 工具还在不在，没跑过。`--allowedTools` 白名单里没有 Agent 工具时 dontAsk 模式下派子 agent 是否被拒；一次性会话遇到检查点是停下还是自己往下走；30 轮与 2 美元的默认上限能走到哪一步。这些都没跑过。
7. **Codex 版与主仓的差距。** Codex 版 `VERSION` 是 3.22.0，CHANGELOG 说它同步的是上游 v3.22.0，比本仓 v3.22.2 落后两个补丁版本（运行账本、缩写检查、#892 路由修复都在 v3.22.2 里）；它另钉了一个 experiment-agent v1.1.0，而本仓 POSITIONING 拒绝自主跑实验，两者关系没读；它的单 skill 结构、`CODEX_FULL_RUNTIME_ADAPTER.md`、脚本与 hook 的处理方式都没读[^codexrepo]。
8. **许可证的两个边界。** 平台以什么形式、在什么许可下带 ARS 内容；有外部资助的课题组使用是否算非商业。需要看法律意见，不是读代码能回答的。
9. **真实效果。** 作者自己的矩阵里没有外部结果证据，样例论文是 3 月的 v2.3。当前版本在真实稿件上的引用问题检出率、误报率、成本与耗时都没有数，留给外层仓 #185。
10. **中文与简体。** 语言对只注册了繁中—英文；中文文献客户端没接进闸门。对以简体中文和中文期刊为主的稿件会怎样，未测。
11. **v3.6.7 审计闸门在默认运行里会不会拦。** 编排提示词写 synthesis 等三个角色交付后没有 Codex 审计记录就 BLOCK、不可跳过，设计稿也写新用户会在第一个 synthesis 阶段被拦；但用户文档的最小配置只要 Claude Code，CONTROL_AVAILABILITY 的渠道矩阵也没有这一行。实跑时模型是否真的停在这里、是否只在插件子 agent 派发时才触发、没有 Codex 的用户怎么过这一关，未验证。
12. **「Python 可选」与提示词里的必跑脚本怎么对上。** SETUP 说核心 skill 不要 Python，编排提示词却把复审校验写成 MANDATORY 运行时步骤、把运行账本与 PDF 预检写进默认流程；没有 Python 时各步骤是跳过并声明、还是停下：缩写检查写了「跑不了就说没跑」（`academic-paper/references/writing_quality_check.md:182`），运行账本写了条件不满足时声明不记账本（`docs/CONTROL_AVAILABILITY.md:86-87`），其余未弄清。

## 8. 调研方法

- 浅克隆到外层 `vendor/academic-research-skills`（提交 e79085d，只有一个提交，历史统计用 `gh api`：release 列表、tag、`stats/participation`、contributors、search issues、main 上最近 30 次 workflow 运行，2026-09-27 查）。不装依赖、不跑项目代码；只用本机 Python 读了四个 SKILL.md 的 frontmatter、金标集条数、能力矩阵 JSON 与 heldout 套件注册表；用内仓 venv 调了平台自己的 `framework.skills.library.load_skill` 校验四个 ARS skill 目录（只读，不写任何文件）；看了本机 `claude --help`（2.1.283）里几个隔离参数的说明。
- 读的顺序：插件清单与 hooks → 四个 SKILL.md → 编排、诚信、论断核对三个 agent → 作者自己的 CONTROL_AVAILABILITY、DATA_FLOWS、STAGE_CAPABILITY_MATRIX（先看作者承认了什么）→ 对 README 每项能力 grep 代码，区分提示词、运行时脚本、库、lint。
- 几个关键 grep：`ARS_CLAIM_AUDIT` 在 `*.py *.sh *.js *.json *.yml` 里零命中；`scripts/`、`hooks/` 下 `.py` / `.sh` 里出现的全部 `ARS_*` 变量名；`run_audit_pipeline`、`verify_passport`、`verification_gate` 的非测试调用方；`^# /// script` 在 `scripts/` 里零命中；提示词里 `python3? (-m )?scripts[/.]名字` 的写法去重得 27 支，加上「Run / pipe to / invoke `scripts/…`」写法去重约 37 支；`^model:` 在 `commands/*.md` 里 13 条 sonnet；`mcp` 在代码与提示词里的出现处。
- Codex 版只用 `gh api` 读了仓库元数据、根目录列表、`VERSION` 与 `CHANGELOG.md` 开头。
- 平台一侧读了外层纲领的 P-1、P-2、P-11、P-14、P-19、P-20、P-22、P-25，`platform/docs/add-a-skill.md`、`add-a-capability.md`，`platform/framework/skills/library.py`、`framework/capabilities/__init__.py`、`backends/claude_code.py`、`backends/codex.py`，平台提交 de3d948。
- 外部来源只查了三处：CC 官方 FAQ 与 NonCommercial 解释页、agentskills.io 规范页，都用于第 5、6 节的条款对照。
- 2026-09-27 独立复查（另一个会话照 `文件:行` 逐条核对）：改掉「平台校验三处不过」（实为两处，脚本一项因 skill 目录里没有 `scripts/` 而不报）、「ARS 刻意不替研究者生成假设」（只在苏格拉底模式成立）、「运行时脚本全部不调模型」（Codex 两支例外）、「只有插件渠道各项都是 Active」（插件渠道有 5 项 Conditional）、「`run_codex_audit.sh` 是维护者脚本」（它是编排提示词里不可跳过的审计闸门的输入）、heldout 套件数（12 不是 13）、守卫放行的角色数（21 不是 20）、SKILL.md 行数与 scripts 分项统计、若干行号；补上 v3.6.7 审计闸门、`verify_passport.py` 默认拒绝输出、折磨短语表要用户自备、其它无代码读取的 `ARS_*` 开关、`claim_audit_config` 不存在、Codex 版的版本号。

[^i133]: Imbad0202/academic-research-skills #133「Phase 2+ agents can silently inflate scope and skip independent Phase 3/5 checkpoints」，2026-05-17，已关。<https://github.com/Imbad0202/academic-research-skills/issues/133>
[^i454]: #454「ars_write_scope_guard.py crashes silently with exitCode: 49 when used alongside RTK proxy」，2026-06-16，已关。<https://github.com/Imbad0202/academic-research-skills/issues/454>
[^i857]: #857「Command stubs reference plugin files by relative path and never invoke the skill」，2026-09-13，已关。<https://github.com/Imbad0202/academic-research-skills/issues/857>
[^i892]: #892「Routing discipline lives only in .claude/CLAUDE.md, which plugin and skills-copy installs do not load (static finding)」，2026-09-23，仍开（修复已随 v3.22.2 发出）。<https://github.com/Imbad0202/academic-research-skills/issues/892>
[^i887]: #887「Handoff integrity: keep pending decisions, unfinished work, and actual tool outcomes across context compaction and subagent returns」，2026-09-23，已关。<https://github.com/Imbad0202/academic-research-skills/issues/887>
[^i475]: #475「Upstream: Claude Code skill/subagent dispatch incorrectly inherits the 1M context tier」，仍开。<https://github.com/Imbad0202/academic-research-skills/issues/475>
[^i828]: #828「Reviewer calibration corpus: OpenReview camera-ready replacement leaks the accept label (blocks #653 first scored run)」，仍开。<https://github.com/Imbad0202/academic-research-skills/issues/828>
[^i595]: #595「Chinese-literature citation resolver: standalone client + API protocol doc (gate untouched)」，2026-07-26，已关。<https://github.com/Imbad0202/academic-research-skills/issues/595>
[^releases]: Release 列表，<https://github.com/Imbad0202/academic-research-skills/releases>，2026-09-27 用 `gh api repos/Imbad0202/academic-research-skills/releases` 查得 45 个。
[^ghstats]: 2026-09-27 用 `gh api` 查 <https://github.com/Imbad0202/academic-research-skills>：仓库元数据（star、fork、license 字段为 NOASSERTION）、`commits` 分页总数 798、`contributors`、`stats/participation`、`search/issues`（issue 358、PR 508）、`actions/runs?branch=main`；共同作者尾注取自最近 5 个提交的提交信息。
[^codexrepo]: <https://github.com/Imbad0202/academic-research-skills-codex>，2026-09-27 用 `gh api` 查了元数据（1.17 万 star，最后推送 2026-09-16，license 字段 NOASSERTION，描述「Codex-native Academic Research Skills suite for human-in-the-loop academic research workflows」）、根目录列表、`VERSION`（3.22.0）与 `CHANGELOG.md` 的 3.22.0 条目（2026-09-16，同步上游 v3.22.0 提交 3c546bc，另钉 experiment-agent v1.1.0），未读代码。
[^agentskills]: Agent Skills 规范，<https://agentskills.io/specification>：`metadata` 是「a map from string keys to string values」，建议 SKILL.md 不超过 500 行，文件引用用相对 skill 根的路径、只深一层。
[^ccfaq]: Creative Commons FAQ，「Can I apply a Creative Commons license to software?」：「We recommend against using Creative Commons licenses for software.」<https://creativecommons.org/faq/>
[^ccnc]: Creative Commons wiki，NonCommercial interpretation：「NonCommercial turns on the use, not the identity of the reuser.」<https://wiki.creativecommons.org/wiki/NonCommercial_interpretation>
