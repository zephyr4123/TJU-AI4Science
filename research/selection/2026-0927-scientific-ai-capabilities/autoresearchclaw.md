---
title: AutoResearchClaw 假设阶段深读
subtitle: 研究创意 · Idea Workshop、多角色生成、查新、方向收敛逐条对账
kind: 开源项目方法借鉴（只读论文与代码，不跑、不装依赖，不评估整体接入）
date: 2026-09-27
scope: 仓库 https://github.com/aiming-lab/AutoResearchClaw，克隆到 vendor/AutoResearchClaw（浅克隆），提交 be4ba47（2026-08-19）；论文 arXiv 2605.20025 v2（2026-05-23）。只看与假设相关的部分：Stage 1/2/7/8/15、HITL 在这几个阶段的通路、Idea Workshop、查新、分支、想法池、ARC-Bench 里测假设的那部分。流水线、沙盒、验证层已在 research/selection/2026-0909-pipeline-frameworks/autoresearchclaw.md 读过，本篇不重复。文中 文件:行 相对该仓库根；平台一侧的路径以 platform/ 开头
status: 第一版
---

> **结论先行**：AutoResearchClaw（下称 ARC）在假设这一段真正接上线的有四样：Stage 8 的「三个角色各写一份、再合成一份」（默认路径是同一个模型客户端分别调三次）；co-pilot 模式下 Stage 7 / 8 跑完后的通用协作对话（在终端里和模型一起改 `synthesis.md` / `hypotheses.md`）；人用 `researchclaw guide --stage 8` 在 Stage 8 执行前写好的意见文件（Stage 8 末尾多调一次模型按它改写）；以及通用的 `--to-stage` / `--from-stage`：停在 Stage 8 之后手改 `hypotheses.md` 再续跑，ARC-Bench 自己就是这样把假设放进去的。查新也真的去 OpenAlex / Semantic Scholar / arXiv 搜，但结果只写进一个没有下游读取的 JSON。
>
> README 与论文里其余说法多数只接了一半或零调用：Idea Workshop 的出想法、打分、细化三个方法从不被调用，Stage 8 只往它的存档里塞一个占位对象（真调的话返回类型也对不上）；「并行探索多个方向」的 `BranchManager` 只拷目录、不执行、生产零调用；想法池、ideation 记忆零调用；终端里暂停时可选的动作只有批准、拒绝、编辑、协作、跳过、中止，「注入意见」和「回滚」两个键输入后被拒。论文说的「角色互相质疑」「跨 run 的教训进入辩论」「Pivot 把失败当新证据带回假设生成」「SmartPause 学习阈值」，在假设这一段的代码里都不成立；有反驳轮的多模型 debate 与 best-of-N tournament 是 2026-08-18 才加的、默认关、晚于论文，打分与合成拆成两次调用还要另配 `reviewer_model`。「角色之间互相看不见」只对 API 类 provider 成立：provider 选 acp（把 Claude Code、Codex 这类命令行 agent 当后端）时，三个角色与合成发进同一个具名会话（按代码推断，未实跑）。
>
> 论文里能归到假设生成的证据只有三处：组件消融的「w/o Debate」（同时去掉 Stage 8 与 Stage 14 的多角色，−1.37 分）、附录 F 的角色数消融、T10 一个案例。主表 Table 2 的实验阶段评测从 Stage 10 开跑、假设直接取自 manifest，不测假设生成；HITL 消融与组件消融的脚本和数据在 `.gitignore` 里。能摘出来的形状：按领域替换的角色提示词（生成 / 可行性 / 反驳三分）、一条假设的字段、打分与合成分开的两次调用、查新产出的近邻论文清单。反面事实两条：co-pilot 下人的意见在 Stage 8 跑完之后才到，改不到这一次的 `hypotheses.md`；PIVOT 后按主指标跨版本挑实验结果，挑中的结果与当前 `hypotheses.md` 可能不是同一版假设。

## 1. 方法是什么

### 1.1 假设这一段的链路

代码里实际的数据流（默认配置，ML 领域）：

```
Stage 6  cards/*.md（知识卡片，最多取 24 张）
   │
Stage 7  一次模型调用 → synthesis.md（聚类、Gap 1..N、优先机会）
   │        Stage 8 提示词里的变量只有 {topic, synthesis}
   │        （goal.md、problem_tree.md、hardware_profile.json、进化教训、skill 都不进提示词；
   │          provider=acp 时会话本身可能带着之前的往来，见下表第一行）
Stage 8  默认：innovator / pragmatist / contrarian 各调一次（同一个客户端）
   │           → hypothesis_synthesize 再调一次，合成 2–4 条
   │     debate_enabled=true：面板开场 → 反驳轮 → 配了 reviewer_model 时 judge 先打分、主模型再合成；
   │                          没配时主模型一次调用里打分加合成
   │     tournament_enabled=true：N 份候选 → judge 挑一份，原样胜出（不合成）
   │     若 stage-08/hitl_guidance.md 已存在：再调一次「按人的意见改写」
   │     → hypotheses.md（自由格式 markdown；执行器只查文件非空，内容不解析）
   │     → check_novelty() → novelty_report.json（无下游读取）
Stage 9  读 hypotheses.md 写实验计划
   ⋮
Stage 15 模型判 PROCEED / REFINE / PIVOT；PIVOT 把 stage-08..15 改名为 _vN，从 Stage 8 重跑
```

| 方法 | 论文怎么讲 | 代码里 | 接线 | 证据 |
|---|---|---|---|---|
| 多角色生成 + 合成 | §3.2：K=3 个认知角色 Innovator / Pragmatist / Contrarian，§1 说它们互相质疑，再由 synthesizer 合成 2–4 条可证伪假设，附可检验标准与所需基线 | 默认走 `_multi_perspective_generate`：三个角色各自一次 `llm.chat`，提示词只含 `topic` 与 `synthesis`；再用 `hypothesis_synthesize` 合成一次。API 类 provider 每次调用无状态，角色彼此看不见。provider=acp 时四次调用用同一个 `ACPClient`、发进同一个具名会话（默认名 `researchclaw`），该文件的 docstring 写明会话在各次调用之间保留上下文，因此后发的角色发出时会话里已有先发角色的往来（按代码推断，acpx 在仓库外，未实跑） | 真接线，默认开 | `researchclaw/pipeline/stage_impls/_synthesis.py:103-113,177-193`、`researchclaw/pipeline/_helpers.py:1689-1749`、`researchclaw/pipeline/executor.py:639-649`、`researchclaw/llm/acp_client.py:1-7,43,102-135,474-480` |
| 角色提示词 | 附录 B.1：ML 用 Innovator / Pragmatist / Contrarian，HEP 用 Theorist / Phenomenologist / Experimentalist | 按 prompt bank 取。`PromptManager` 支持 `ml`、`hep_ph`、`biology_metabolic` 三套，但执行器选 bank 的函数只返回 `ml` 或 `hep_ph`，`biology_metabolic` 那套在流水线里不可达 | 真接线 | `researchclaw/prompts/ml.py:21-81`、`researchclaw/prompts/hep.py:34-118`、`researchclaw/prompts/manager.py:31,85-94,285-287`、`researchclaw/pipeline/_domain.py:140-190`、`researchclaw/pipeline/executor.py:654-661` |
| 多模型辩论 | 未单独描述（论文只有 §3.2 的多角色） | `run_debate`：角色按轮转绑到面板里的模型（只配了 `primary_model` 时面板只有一个模型），开场一轮、反驳 `debate_rounds` 轮（默认 1）。配了 `reviewer_model` 时 judge 单独打分排序、主模型照排序合成；没配时 judge 就是主模型客户端，打分与合成在一次调用里 | 可选，`debate_enabled` 默认 False；2026-08-18 加入 | `researchclaw/pipeline/debate.py:80-292`、`researchclaw/llm/__init__.py:105-145`、`researchclaw/config.py:218-222`、`researchclaw/pipeline/stage_impls/_synthesis.py:151-176` |
| best-of-N | 未描述 | `run_tournament`：按角色提示词轮转生成 N 份（默认 3），judge 以 JSON 选一份，选不出就取分最高的、再不行取第 0 份。开了 debate 时候选由面板模型轮流生成。全部候选失败时抛异常，这段调用没有 `try`，Stage 8 记 FAILED | 可选，`tournament_enabled` 默认 False；与 debate 互斥（if / else） | `researchclaw/pipeline/tournament.py:53-88,91-238`、`researchclaw/pipeline/stage_impls/_synthesis.py:114-150`、`researchclaw/config.py:223-229` |
| 人的意见改写 | §3.5 CoPilot 的「Idea Workshop 假设共创」 | Stage 8 生成完，若本阶段目录下已有 `hitl_guidance.md` 且有模型，多调一次模型「按人的意见改写」，失败只记 debug | 真接线，但要求意见在 Stage 8 执行前就写好（见 [1.2](#12-人怎么参与假设共创)） | `researchclaw/pipeline/stage_impls/_synthesis.py:196-214` |
| Idea Workshop | §3.5；README 称「协作式出想法、评估、细化假设（Stage 7-8）」 | `IdeaWorkshop` 有 `brainstorm` / `evaluate` / `refine` / `select`，生产代码只 `save()` 一个用 `type(...)` 临时造的占位对象（标题恒为 "Generated Hypothesis"，描述是假设文本前 500 字），外面裹 `except: pass` | 只接了存档；三个方法零调用 | `researchclaw/pipeline/stage_impls/_synthesis.py:216-230`、`researchclaw/hitl/workshops/idea.py:104-256`、`README.md:416` |
| 查新 | 论文没有描述查新 | `check_novelty`：搜三个库、关键词 Jaccard、给 novelty_score 与 proceed / differentiate / abort 建议，写 `novelty_report.json` | 调用是真的，结果无人读（见 [1.5](#15-查新怎么做)） | `researchclaw/pipeline/stage_impls/_synthesis.py:234-259`、`researchclaw/literature/novelty.py:185-335` |
| 失败兜底 | 未描述 | 没有模型（非 acp 时 `base_url` 或 `api_key` 为空就视为没有）、全部角色失败、debate 抛异常时，写死三条模板假设（"Increasing protocol control for {topic} improves metric stability…"），Stage 8 仍记 DONE；tournament 失败不在此列。`researchclaw run` 默认先做一次模型预检、不过就退出，所以「没有模型」这一支只在带 `--skip-preflight`（ARC-Bench 的跑法就带）时走到；预检过了、之后调用失败则走「全部角色失败」那一支 | 真接线 | `researchclaw/cli.py:228-239`、`experiments/arc_bench/scripts/run_bench.py:198-206`、`researchclaw/pipeline/executor.py:639-649`、`researchclaw/pipeline/_helpers.py:1591-1605`、`researchclaw/pipeline/stage_impls/_synthesis.py:171-176,184-188,194-195` |

在论文发表时的代码（v0.5.0，提交 12d3fd8，2026-05-20）里，Stage 8 只有上表第一行那条路径：`run_debate` 与 `run_tournament` 都是 2026-08-18 的提交 1d7e46f 加进来的[^gh-commits]，用 GitHub 取回 v0.5.0 的 `_synthesis.py` 与 HEAD 对比，差异正好是这两段分支及其 import[^v050-diff]。

### 1.2 人怎么参与：假设共创

ARC 里人能碰到假设的通道，按「改没改到 `hypotheses.md`」排。先说一个贯穿全表的事实：暂停时的可选动作由 `WaitingState.available_actions` 决定，默认值是 approve / reject / edit / collaborate / skip / abort 六个，`session.pause()` 从不改它；终端适配器只接受这张表里的动作（`researchclaw/hitl/intervention.py:194-201`、`researchclaw/hitl/session.py:140-167`、`researchclaw/hitl/adapters/cli_adapter.py:136-141`）。

| 通道 | 什么时候 | 改到什么 | 状态 | 证据 |
|---|---|---|---|---|
| `researchclaw guide <run> --stage 8 --message …` | 任意时刻写文件；要在 Stage 8 执行之前写才有效。PIVOT 会把 `stage-08/` 连同这个文件改名成 `stage-08_vN/`，重跑的 Stage 8 读不到 | Stage 8 末尾多一次改写调用，改到 `hypotheses.md` | 真接线；前提是人知道要提前写 | `researchclaw/cli.py:2304-2321`、`researchclaw/pipeline/stage_impls/_synthesis.py:196-214`、`researchclaw/pipeline/runner.py:1302-1320`、`docs/HITL_GUIDE.md:204-212` |
| `--to-stage HYPOTHESIS_GEN` 停下，手改 `stage-08/hypotheses.md`（或写意见后 `--from-stage HYPOTHESIS_GEN` 重跑 Stage 8），再 `--from-stage EXPERIMENT_DESIGN` 续跑 | 流水线停下之后 | 直接改文件，或让重跑的 Stage 8 读到意见 | `--from-stage` 只是从指定阶段开始循环，不清理已有目录；ARC-Bench 正是先写好 `stage-07/08/09` 的文件再 `--from-stage CODE_GENERATION`。这条通路按代码推断可行，未实跑 | `researchclaw/cli.py:1208-1213,248-282,330-341`、`researchclaw/pipeline/runner.py:35-38,482-486,663-664`、`experiments/arc_bench/scripts/prepare_run.py:62-70`、`experiments/arc_bench/scripts/run_bench.py:198-206` |
| Stage 8 执行前暂停收意见 | 六个模式与 `--mode` 的 express / thorough / learning 三个预设都没有设 `pause_before`；任何模式下在配置里给 8 号写 `stage_policies` 都能开（逐阶段配置优先于模式默认）。暂停时终端里选不了「注入意见」，只能在另一个终端先 `researchclaw guide --stage 8` 再批准；脚本化适配器可以直接送 inject | 意见写进 `stage-08/hitl_guidance.md`，Stage 8 末尾的改写调用读到 | 预设下不发生 | `researchclaw/hitl/config.py:112-116,200-243`、`researchclaw/hitl/presets.py:12-127`、`researchclaw/pipeline/executor.py:200-254` |
| co-pilot 下 Stage 8 跑完后的协作对话（`c`） | Stage 8 在 co-pilot 的「要批准」与「可协作」两组里 | 流水线进程的 stdin 里和模型对话；模型用 `<<<FILE: hypotheses.md>>> … <<<END_FILE>>>` 包住全文即覆盖文件，人也可以 `edit hypotheses.md` 粘贴；两种改写都立即写盘，`done` 时再存对话记录与修订记录 | 真接线；要求流水线在前台终端：暂停时读到 EOF，终端适配器返回中止，这一阶段记 FAILED | `researchclaw/hitl/config.py:193-197`、`researchclaw/pipeline/executor.py:409-428,440-564`、`researchclaw/hitl/collaboration.py:83-190`、`researchclaw/hitl/chat.py:178-235`、`researchclaw/hitl/adapters/cli_adapter.py:111-118` |
| co-pilot 下 Stage 8 跑完后的「注入意见」（INJECT） | 同上 | 终端适配器有 `i` 键，但 inject 不在可选动作里，输入后被拒；能送来 INJECT 的只有脚本化适配器（它对没写动作的条目默认就是 inject）和读 `hitl/response.json` 的文件轮询。送到后写 `stage-08/hitl_guidance.md`，Stage 8 已经跑完，`hypotheses.md` 不变；这段文字进入之后所有用 `_build_context_preamble` 的阶段（每份截前 1000 字），Stage 9 起才看得到 | 终端里用不了；脚本化干预能送到，但改不到本阶段产物 | `researchclaw/hitl/adapters/cli_adapter.py:77-96,136-141`、`researchclaw/hitl/adapters/scripted_adapter.py:138-139`、`researchclaw/pipeline/executor.py:430-435`、`researchclaw/pipeline/_helpers.py:1112-1122` |
| 编辑（EDIT） | 同上 | 终端适配器用 `$EDITOR` 打开 `hypotheses.md`，存盘后执行器原样返回 StageResult；脚本化 JSON 里的 `edited_files` 全仓没有代码写盘 | 终端里真接线；脚本化编辑不落盘 | `researchclaw/hitl/adapters/cli_adapter.py:290-369`、`researchclaw/pipeline/executor.py:396-398`、`researchclaw/hitl/adapters/scripted_adapter.py:147` |
| 拒绝（REJECT） | 同上 | 返回 REJECTED，runner 直接停掉整条流水线，不会重新生成。`stages.py` 里有一张「Stage 9 被拒 → 回 Stage 8」的 `GATE_ROLLBACK` 表，但只有 `advance()` 用它，生产代码只以 START 事件调一次 `advance()` | 真接线，拒绝即停 | `researchclaw/pipeline/executor.py:386-394,652`、`researchclaw/pipeline/runner.py:837-843`、`researchclaw/pipeline/stages.py:117-123,247-312` |
| 回滚（ROLLBACK） | 同上 | 终端适配器的 `b` 键同样不在可选动作里；脚本化适配器能送来 ROLLBACK，执行器的暂停处理没有这一分支，等于放行 | 终端按不出，处理也不在 | `researchclaw/hitl/adapters/cli_adapter.py:84,136-141`、`researchclaw/hitl/adapters/scripted_adapter.py:44`、`researchclaw/pipeline/executor.py:383-437`（无 ROLLBACK 分支）、全仓只有 `researchclaw/hitl/session.py:480` 把它映射成日志类型 |
| Stage 7 跑完后协作改 `synthesis.md` | co-pilot 下 Stage 7 也在「可协作」组 | Stage 8 的唯一文献输入就是 `synthesis.md`，改它等于改假设的来源 | 真接线 | `researchclaw/hitl/config.py:194`、`researchclaw/pipeline/stage_impls/_synthesis.py:103,113` |
| Stage 7 跑完后注入意见 | 同上（终端选不了，脚本化可以） | 写 `stage-07/hitl_guidance.md`，进 preamble；Stage 8 不用 preamble，只用 `{topic, synthesis}`，所以影响不到假设 | 改不到假设 | `researchclaw/pipeline/stage_impls/_synthesis.py:113` |
| Stage 15 上人要求换方向（PIVOT） | HITL 指南写「Choose PROCEED, PIVOT, or REFINE」 | 决定在暂停前已由模型文本解析出来；EDIT 改 `decision.md` 不改已解析的 `decision`；SKIP 把 decision 改成 proceed，所以人能把 PIVOT / REFINE 压成 PROCEED，反过来不行；REJECT 停流水线。HITL 里人没有让流水线回到 Stage 8 的通路；HITL 之外只能停下后 `--from-stage HYPOTHESIS_GEN` 手动重跑（按代码推断，未实跑） | 文档有、通路无 | `docs/HITL_GUIDE.md:197`、`researchclaw/pipeline/stage_impls/_analysis.py:1269-1335`、`researchclaw/pipeline/executor.py:400-407,818-821` |
| SmartPause 在 Stage 8 自动叫人 | §3.5：不确定性高于「学习到的阈值」就暂停，阈值按历史批准率自适应 | 阈值写死 0.7；置信度 = 5 项固定权重，Stage 8 的关键度 0.9。PRM 默认只评 5 / 9 / 15 / 20，Stage 8 通常没有 PRM 分数，这时 quality 与 confidence 取 1.0，novelty_risk 从不赋值取 0，总分 = 0.72 + 0.10 ×（1 − 本 run 的拒绝率），最低 0.72，高于 0.7 | 默认配置下 Stage 8 上不触发；co-pilot 下 Stage 8 本来就暂停 | `researchclaw/pipeline/executor.py:299-323,716-717`、`researchclaw/hitl/smart_pause.py:34-51,66-91,110-180` |
| 实验用的脚本化干预 | 附录 E、J：HITL 实验用预先写好的干预，不是真人 | `ScriptedHITLAdapter` 在流水线暂停时按阶段号返回 JSON 里写好的动作，没有的阶段自动批准；环境变量 `HITL_INTERVENTIONS_FILE` 或 `--interventions` 挂上（环境变量优先） | 真接线 | `researchclaw/hitl/adapters/scripted_adapter.py:122-168`、`researchclaw/cli.py:377-388` |
| `researchclaw attach` / `approve` / `reject` | 另开一个终端 | 只写 `hitl/response.json`。读它的文件轮询只在会话没有输入回调、或回调抛异常时走；`researchclaw run` 开了 HITL 时总会挂上终端或脚本化适配器，终端适配器读到 EOF 返回中止而不是抛异常 | `researchclaw run` 路径下读不到（按代码推断，未实跑） | `researchclaw/cli.py:377-394,2186-2301`、`researchclaw/hitl/session.py:181-237`、`researchclaw/hitl/file_wait.py:53-80` |

`docs/HITL_GUIDE.md:220-253` 演示的 Idea Workshop 对话（「我生成了 3 个候选，Novelty 8/10、Feasibility 6/10……」）在代码里没有对应：co-pilot 在 Stage 8 进的是上表的通用协作对话，系统提示只有主题、当前 `hypotheses.md`（截 3000 字）与意见文件，不带合成稿、各角色稿与查新报告（`researchclaw/hitl/chat.py:190-233`），也不产生分项分数。

`IdeaWorkshop.brainstorm` 与 `evaluate` 把 `self.llm.chat(...)` 的返回值当字符串直接 `json.loads`（`researchclaw/hitl/workshops/idea.py:136-143,286,336`），而 `LLMClient.chat` 返回的是 `LLMResponse` 数据类（`researchclaw/llm/client.py:55-66,239-249`）。按代码推断，真接上时 `json.loads` 抛 `TypeError`，解析函数只接 `JSONDecodeError` / `ValueError`，于是 `brainstorm` 走到外层 `except` 返回空列表，`evaluate` 保留默认的 5.0 分；它的单测把 `chat` mock 成返回 JSON 字符串，所以是绿的（`tests/test_hitl_collaboration.py:383-392`）。这与 2026-09-09 那篇记的 memory 构造签名问题同一类：测试用的契约与生产不同。

### 1.3 假设评估与细化的判据

代码里出现过的「好假设」判据，以及它们有没有改变任何东西：

| 位置 | 判据 | 谁判 | 结果去哪 | 是否影响流程 | 证据 |
|---|---|---|---|---|---|
| innovator 提示词 | NOVELTY 超出已有方法的增量组合；FEASIBILITY 单卡 30 分钟内可测；FALSIFIABILITY 给出拒绝它的指标阈值；每条带风险等级 | 模型自述 | 角色稿 | 只作为生成要求 | `researchclaw/prompts/ml.py:28-42` |
| pragmatist 提示词 | 可测的具体主张、为何有限算力可行、资源估计、可测预测与失败条件 | 模型自述 | 角色稿 | 同上 | `researchclaw/prompts/ml.py:50-60` |
| contrarian 提示词 | 挑战一个主流假定、主流看法为何可能错、替代假设、会有信息量的负结果 | 模型自述 | 角色稿 | 同上 | `researchclaw/prompts/ml.py:69-79` |
| `hypothesis_synthesize` | 取最强、最新颖的想法；回应 contrarian 的顾虑；保证可行性；标出未解决的分歧；每条写依据、可测预测、失败条件；2–4 条 | 同一模型 | `hypotheses.md` | 是（它就是产物） | `researchclaw/prompts/shared.py:750-768` |
| debate judge | 对每个角色稿按严谨、证据、可证伪性打 1–10 分并排序。配了 `reviewer_model` 时是单独一次打分调用，写 `debate_scores.md`，排序原文交给合成；没配时 judge 与合成是同一个主模型客户端，一次调用里先打分再合成，分数不单独落盘 | `reviewer_model`；没配就是主模型 | 见左 | 是，但只在 `debate_enabled` 下 | `researchclaw/pipeline/debate.py:202-276` |
| `tournament_rank` | 要求按新颖、可行、严谨打 1–10 分并挑唯一胜者；输出的 JSON 里每份候选只有一个 `score` | 同上 | `tournament_record.json`，胜者原文成为 `hypotheses.md` | 是，但只在 `tournament_enabled` 下；解析失败先取分最高、再默认第 0 份 | `researchclaw/prompts/shared.py:793-808`、`researchclaw/pipeline/tournament.py:53-88,195-219` |
| `hypothesis_gen` 阶段提示词 | NOVEL、GAP-FILLING、FEASIBLE、FALSIFIABLE、SURPRISING；每条写新颖性论证、依据、可测预测、失败条件、所需基线（论文 Table 8 列的就是这些） | — | — | 从不被渲染：Stage 8 不调 `for_stage("hypothesis_gen")` | `researchclaw/prompts/ml.py:330-362`；`for_stage` 全部调用点里没有它 |
| 契约 `dod` | 「≥2 条可证伪假设」，错误码 `E08_HYP_INVALID` | — | — | 字符串，全仓无读取点；契约里被执行的只有「输入文件存在」「输出文件非空」两项 | `researchclaw/pipeline/contracts.py:85-91`、`researchclaw/pipeline/executor.py:615-627,680-705` |
| Stage 2 选题自评 | 按顶会标准给新颖、具体、可行 1–10 分，总分 < 5 时给改题建议 | 同一模型 | `topic_evaluation.json` + 一行 warning 日志 | 否，文件无读取点 | `researchclaw/pipeline/stage_impls/_topic.py:178-216` |
| 查新报告 | 相似度 → novelty_score → high / moderate / low / critical → proceed / differentiate / abort | 确定性代码 | `novelty_report.json` | 否（见 [1.5](#15-查新怎么做)） | `researchclaw/literature/novelty.py:292-314,359-398` |
| `IdeaWorkshop.evaluate` | 新颖、可行、影响、总分 0–10，优缺点与建议 | — | — | 零调用 | `researchclaw/hitl/workshops/idea.py:150-199` |
| `IdeaPool.score` | 0.4 × 可行 + 0.6 × 新颖 | 人手填 | — | 零调用 | `researchclaw/project/models.py:70-72`、`researchclaw/project/idea_pool.py:75-91` |
| Stage 15 研究决策 | PIVOT = 假设根本上有缺陷；REFINE = 假设成立但实验要重调；PROCEED 需同时满足 5 条（≥2 基线、主指标有定义、每条件 ≥3 种子、条件间无逐种子相同值、分析质量 ≥4/10） | 模型；提示词后面追加确定性提示（退化循环、诊断、消融无效比例） | `decision.md` → runner 回退 | 是 | `researchclaw/prompts/ml.py:923-948`、`researchclaw/pipeline/stage_impls/_analysis.py:1188-1253` |

细化（从一版假设到下一版）实际发生在六处：合成调用、debate 的反驳轮（可选）、意见改写调用、协作对话里的文件覆盖、人停下后手改文件或 `--from-stage` 重跑、PIVOT 后的整段重跑。上表里所有打分类判据（选题自评、查新、Workshop 打分）都没有回流到任何一处细化。

还有两处论文说有、提示词里没有：论文 §3.2 说合成结果「附可检验标准与所需基线」，`hypothesis_synthesize` 没要求基线；Table 8 说 Stage 14 要「逐条假设给结论」，Stage 14 的提示词前段带着假设原文（preamble 截 2200 字），但三个分析角色与 `analysis_synthesize` 提示词都没有逐条给结论的要求（`researchclaw/pipeline/stage_impls/_analysis.py:561-562,598-616`、`researchclaw/prompts/ml.py:83-136`、`researchclaw/prompts/shared.py:769-791`），写着 sanity check 清单的 `result_analysis` 阶段提示词同样不被渲染（`researchclaw/prompts/ml.py:863` 起）。

### 1.4 并行方向：怎么探索、怎么收敛

| 机制 | 并行在哪 | 收敛规则 | 状态 | 证据 |
|---|---|---|---|---|
| 三角色 | 每个角色至少 2 条，共 ≥6 条候选 | 一次合成调用挑成 2–4 条，要求「保留真实分歧、不折中」 | 默认开 | `researchclaw/prompts/ml.py:29,51,70`、`researchclaw/prompts/shared.py:750-768` |
| 多模型 debate | 角色按轮转绑到面板模型：`primary_model` + `reviewer_model` + `fallback_models` 去重，全部共用主配置的 endpoint 与 key，只换模型名 | 反驳轮里每个角色看其余角色上一轮的稿；配了 `reviewer_model` 时 judge 排序、主模型照排序合成，没配时主模型一次调用里打分加合成；记 `debate_record.json`（含 judge 是否独立于作者模型） | 可选，默认关；provider=acp 时面板为空 | `researchclaw/pipeline/debate.py:136-196,202-291`、`researchclaw/llm/__init__.py:105-145` |
| tournament | N 份候选按角色提示词轮转（候选 0 是 innovator 的稿，1 是 pragmatist，2 是 contrarian）；开了 debate 时由面板模型轮流生成 | judge 挑一份，胜者原文就是最终假设，不再合成 | 可选，默认关；开了就不走 debate 那条分支 | `researchclaw/pipeline/stage_impls/_synthesis.py:114-150`、`researchclaw/pipeline/tournament.py:144-238` |
| PIVOT | 串行，不并行：Stage 15 判 PIVOT 就把 `stage-08..15` 改名为 `_vN`，从 Stage 8 递归重跑 | PIVOT 与 REFINE 共用一个计数，合计最多 2 次（论文算法 1 写的是 pivot ≤2、refine ≤10 两层嵌套）；用完后强制 PROCEED | 真接线 | `researchclaw/pipeline/stages.py:129-134`、`researchclaw/pipeline/runner.py:699-778,1278-1320,1557-1568` |
| PIVOT 后的结果选择 | 全部 `stage-14*` 版本 | `_promote_best_stage14` 按主指标在所有版本里挑最好的一份实验摘要与分析稿，拷回 `stage-14/` 与 `experiment_summary_best.json`；按代码推断，挑中的可能是 PIVOT 之前、针对旧假设的那一版，而 `hypotheses.md` 已是新的一版（未实跑） | 真接线 | `researchclaw/pipeline/runner.py:777,1357-1460` |
| `BranchManager` | README 称「流水线分支，并行探索假设」 | `create_branch` 拷贝前 N 个阶段目录；`compare_branches` 列每个分支的文件名、前 200 字与 PRM 分；`merge_branch` 把分支目录拷回主目录。没有执行分支的代码 | 生产零调用；另有一个 `copilot/branching.py` 同名类，整个 `copilot/` 包也零调用 | `researchclaw/hitl/branching.py:84-268`、`README.md:72` |
| `IdeaPool` | 想法的增删查、打分、排序、转项目 | 按 0.4 / 0.6 加权分排序 | 生产零调用（只在 `project/__init__.py` 导出） | `researchclaw/project/idea_pool.py:16-112` |
| `IdeationMemory` | 记选题结果、假设可行性、反模式 | 失败的置信度更高（0.7 对 0.6） | 生产零调用 | `researchclaw/memory/ideation_memory.py:16-158` |
| `trends --suggest-topics` | CLI 旁路命令，从近期论文的关键词趋势出候选选题 | 新颖度 = max(0.3, 1 − 0.15 × 与上升关键词重叠数)，总分 0.4 新颖 + 0.3 可行 + 0.3 影响；CLI 里不传模型，走启发式 | 真接线，但不在流水线里 | `researchclaw/trends/auto_topic.py:76-110`、`researchclaw/cli.py:1050-1059` |

PIVOT 重跑 Stage 8 时，提示词的变量仍然只有 `topic` 与 `stage-07/synthesis.md`：上一版假设在 `stage-08_v1/`，决策理由在 `stage-15_v1/decision.md`，都不进 Stage 8 的提示词；人事先写在 `stage-08/` 的意见文件也随目录改名，重跑读不到（`researchclaw/pipeline/stage_impls/_synthesis.py:103,113,197`、`researchclaw/pipeline/runner.py:1302-1320`）。论文 §3.3 说的「带着失败作为新证据回到假设生成」，对 API 类 provider 在代码里是同样输入的一次重新采样。provider=acp 时每个阶段新建一个客户端，旧客户端回收时会关闭会话（`researchclaw/llm/acp_client.py:155-179`），重跑的 Stage 8 会话里还剩不剩之前的往来，取决于仓库外 acpx 的 `sessions ensure` 语义，仓库内看不出。

### 1.5 查新怎么做

ARC 里叫得上「查新」的有三处，只有第三处真去搜论文：

1. Stage 1 提示词要求「Novel Angle，带趋势验证，不许编论文标题」，没有检索；产物前面自动加一段「未验证草稿」声明（`researchclaw/prompts/ml.py:167-182`、`researchclaw/pipeline/stage_impls/_topic.py:44-65`）。
2. Stage 2 的选题自评（上一节表中），纯模型打分，结果不被读取。
3. Stage 8 末尾的 `check_novelty`，步骤如下：

| 步骤 | 做法 | 证据 |
|---|---|---|
| 抽关键词 | 主题 + 全部假设文本，正则 `[a-zA-Z][a-zA-Z0-9_-]+`，小写，去英文停用词，≥3 字符，去重 | `researchclaw/literature/novelty.py:133-142,217-219` |
| 组检索式 | 主题一条；`## H1` 这类标题行（>10 字符）各一条；前 5 个关键词拼一条；最多 5 条 | `researchclaw/literature/novelty.py:338-356` |
| 检索 | `search_papers_multi_query`，默认 OpenAlex、Semantic Scholar、arXiv 三源，每条检索式每个源最多 15 篇，检索式之间隔 1.5 秒；某个源失败时退到本地检索缓存（同一检索式以前查过才有）；全局去重后按引用数降序；取前 30 篇比较 | `researchclaw/literature/novelty.py:229-262`、`researchclaw/literature/search.py:36,104-124,201-223,246-281` |
| 也比已收集的论文 | Stage 4 的 `candidates.jsonl` 全部参与比较 | `researchclaw/pipeline/stage_impls/_synthesis.py:239-240`、`researchclaw/literature/novelty.py:264-287` |
| 相似度 | 假设关键词集合与论文「标题 + 摘要」关键词集合的 Jaccard；标题序列相似度那一支要传 `hypothesis_title` 才启用，两处调用都没传 | `researchclaw/literature/novelty.py:164-177,239,271` |
| 判定 | ≥0.25 记为相似；novelty_score = 1 − 相似论文里的最大相似度；相似度最高的前 5 篇里有 ≥2 篇相似度 ≥0.4 且引用 ≥50，再乘 0.7；≥0.7 high、≥0.45 moderate、≥0.25 low、其余 critical；对应 proceed / proceed / differentiate / abort；API 一篇没返回且没有已收集论文时记 `insufficient_data` / `proceed_with_caution` | `researchclaw/literature/novelty.py:292-314,359-398` |
| 结果去向 | 写 `novelty_report.json`、打一行 info 日志；外面裹 `except` 只记 warning。唯一读它的是 `hitl/summarizer.py`，该模块在生产代码里没有被 import | `researchclaw/pipeline/stage_impls/_synthesis.py:234-259`、`researchclaw/hitl/summarizer.py:142-147` |

Jaccard 的分母是两边关键词的并集，假设文本越长，分母越大。量级估计（没有真实的 `hypotheses.md` 产物，用论文自己的文本代替，照同一正则与停用词自己写几行 Python 算，没跑 ARC 代码）：论文摘要 179 词抽出 109 个关键词，同一篇论文 §3.2–3.3 正文 518 词抽出 271 个，两者 Jaccard 为 0.092；要到 0.25，摘要里约 70% 的关键词（76 / 109）都得出现在正文里。一份 2–4 条、带依据与预测的 `hypotheses.md` 与这段正文长度相当，所以同题论文多半也到不了 0.25，这个检查在多数情况下会给 `high`（按公式推算，未用真实产物验证）。假设用中文写时，正则只能抽到主题与夹带的英文词。论文正文与附录都没有描述这一步。

## 2. 为什么有效：论文证据与代码对账

### 2.1 论文给了哪些证据

论文[^arc-paper]里和假设有关的证据：

| 证据 | 内容 | 设置 | 出处 |
|---|---|---|---|
| 组件消融 | 去掉 Debate：质量 5.62 → 4.25（−1.37，p=0.003），接受 3/10 → 1/10；同时去掉 Debate 与自愈：完成 4/10、质量 3.47、接受 0 | Full-Auto，10 个 topic，每组合跑 3 次取最好；p 值未写检验方法 | §4.5、Table 5 |
| 角色数 | K=2 使「假设多样性」−23%；K=5 多花 67% token 只多 8% 多样性 | 每档 10 个 run；「多样性」怎么量没有写 | 附录 F |
| 案例 T10 | Full-Auto 的 8 种交叉验证策略全部输出相同的零偏差；CoPilot 里 Pragmatist 指出 LOOCV 可能超时、Contrarian 质疑消融能否分辨差异，synthesizer 收窄假设集 | 单个 topic；CoPilot 一侧同时有文献、假设、设计、写作、质量 5 个阶段的人工意见 | §4.6、图 2、Table 11 |
| HITL 消融 | CoPilot 平均 7.27、接受 87.5%；只在 5 / 8 / 9 介入的 Pre-Experiment 为 4.28、37.5%；Full-Auto 4.03、25% | 10 个 topic × 7 种模式，单次运行（§4.5 称其为 single-run）；干预是预先写好的脚本，不是真人；接受率的分母是有效 run 数（例如 CoPilot 7/8） | §4.4、Table 3、附录 E、附录 J |
| 失败分析 | 13 个无效 run 里 11 个死在 Stage 17，四类原因之一是「设计对预算太大」 | HITL 消融的 run | 附录 H |

### 2.2 这些证据测没测到假设这一段

| 证据 | 测到了什么 | 依据 |
|---|---|---|
| Table 2 主表（0.648 对 AI Scientist v2 的 0.419） | 没测假设生成。ARC-Bench 的实验阶段评测从 Stage 10 开跑、到 Stage 14 停，`stage-08/hypotheses.md` 由 `prepare_run.py` 直接从 manifest 的 `hypotheses` 写出；设计文档也写明 ARC 额外拿到注入的合成稿、假设与实验计划 | `experiments/arc_bench/scripts/prepare_run.py:62-70`、`experiments/arc_bench/scripts/run_bench.py:198-206`、`experiments/arc_bench/EXPERIMENT_DESIGN.md:42-48,79-83` |
| Table 2 的 CoPilot 一行 | 仓库里唯一一批 rc_copilot 干预（25 个 JSON）只有 Stage 10 与 13 两个键、动作全是 inject，由 `hitl_suggestor.py` 把 Full-Auto 那次的本地判分结果（哪些评分叶子没拿分）、manifest、提交物喂给一次模型调用生成，默认模型 gpt-5.3-codex；脚本的提示词写明 bench 的 co-pilot 只在 Stage 10 与 13 之后暂停，而 `EXPERIMENT_DESIGN.md` 仍写键是 5 / 8 / 9 / 14。论文没写 Table 2 的 CoPilot 用的是不是这批，仓库里没有别的 | `experiments/arc_bench/scripts/hitl_suggestor.py:1-16,40-73,151-167,203-219`、`experiments/arc_bench/EXPERIMENT_DESIGN.md:66-71`、`experiments/arc_bench/baseline/README.md:15-17` |
| Table 5 的 w/o Debate | 同时去掉 Stage 8 与 Stage 14 两处多角色，分不开假设端与分析端各占多少。仓库里的消融开关 `ARC_ABL_DISABLE_DEBATE=1` 会把角色表截成第一个角色：Stage 8 只剩 innovator，Stage 14 只剩 optimist，合成调用照跑；如果消融用的是这个开关，对照组是「只留最激进与最乐观的角色」，不是「单个中性生成器」。开关注释写「只给 experiments/component_ablation 用」，该目录在 `.gitignore` 里 | `researchclaw/pipeline/_helpers.py:1703-1709`、`researchclaw/pipeline/debate.py:130-134`、`researchclaw/prompts/ml.py:21-22,83-84`、`.gitignore:128` |
| 附录 F 的 K 消融 | 代码里没有角色数参数：每个 bank 的角色表写死 3 个，只有「截成 1 个」的开关 | `researchclaw/prompts/ml.py:21-81`；全仓 `ARC_*` 环境变量只有 5 个（`ARC_ABL_DISABLE_DEBATE`、`ARC_ABL_DISABLE_REGISTRY`、`ARC_ABL_DISABLE_TOURNAMENT`、`ARC_DEBATE_ROUNDS`、`ARC_TOURNAMENT_CANDIDATES`） |
| Table 3 的 Pre-Experiment（5 / 8 / 9） | 按代码推断，如果用的是 co-pilot 那种跑后暂停，Stage 8 的脚本化 inject 改不到 `hypotheses.md`，只进入 Stage 9 以后的 preamble（见 [1.2](#12-人怎么参与假设共创)），这一格测到的「假设共创」更接近「给设计阶段递一段意见」；如果作者用 `stage_policies` 给 8 号配了 `pause_before`，inject 会在 Stage 8 执行前落盘并被改写调用读到。代码里没有 Pre-Experiment 这个模式或预设。HITL 消融的脚本与数据在 `experiments/hitl_ablation/`，同样被 `.gitignore` 挡住，Stage 8 的干预内容与投递方式无从核对 | `researchclaw/pipeline/executor.py:200-254,430-435`、`researchclaw/hitl/presets.py:117-127`、`.gitignore:130` |

### 2.3 代码是否按论文做

| 论文说 | 代码里 | 证据 |
|---|---|---|
| 角色在生成假设时互相质疑（§1、§3.2） | 默认路径三个角色各自一次调用，提示词里没有别的角色的稿，唯一「看到全部」的是合成调用；有反驳轮的 `run_debate` 在 2026-08-18 加入、默认关，论文 v2 发于 2026-05-23。provider=acp 时各角色进同一个会话，彼此能看到，但那是会话上下文，不是提示词里设计的质疑轮 | `researchclaw/pipeline/_helpers.py:1713-1725`、`researchclaw/pipeline/debate.py:167-196`、`researchclaw/llm/acp_client.py:1-7`[^gh-commits] |
| 单个模型既提又评，难以证伪自己的假设（§3.2 动机） | 默认路径里三个角色与合成用的是同一个模型客户端；独立 judge 只在 debate / tournament 下、且配了 `reviewer_model` 才有。`reviewer_model` 可以只换模型名，也可以配独立的 `reviewer_provider` / `reviewer_base_url` / `reviewer_api_key` | `researchclaw/pipeline/stage_impls/_synthesis.py:179-193`、`researchclaw/llm/__init__.py:88-103`、`researchclaw/llm/client.py:180-229`、`researchclaw/config.py:206-217` |
| Pragmatist 按硬件与时间预算评估可行性（§3.2） | Stage 8 的变量只有 `topic` 与 `synthesis`；Stage 1 探测的 `hardware_profile.json` 不进来；pragmatist 提示词只写「有限算力」，单卡 30 分钟的约束写死在 innovator 提示词里 | `researchclaw/pipeline/stage_impls/_synthesis.py:113`、`researchclaw/pipeline/stage_impls/_topic.py:96-102`、`researchclaw/prompts/ml.py:32,54` |
| 合成出的每条假设带可检验标准与所需基线（§3.2）；Stage 8 要求新颖性论证与所需基线（Table 8） | 合成提示词要依据、可测预测、失败条件，不要基线；Table 8 那套要求所在的 `hypothesis_gen` 提示词从不被渲染；输出只查非空，不解析 | `researchclaw/prompts/shared.py:758-766`、`researchclaw/prompts/ml.py:330-362`、`researchclaw/pipeline/executor.py:680-705` |
| 跨 run 教训注入所有阶段、教训影响辩论（图 1、§1、§3.6） | Stage 8 不调 `_get_evolution_overlay`，所以进化教训、MetaClaw 技能与 SkillRegistry 匹配到的 skill 都进不来；也不走 `for_stage`，配置里的 `extra_prompts.hypothesis_gen` 同样到不了 Stage 8；Stage 7 调了 overlay | `researchclaw/pipeline/stage_impls/_synthesis.py:50,94-195`、`researchclaw/pipeline/_helpers.py:816-860`、`researchclaw/prompts/manager.py:214-244` |
| Pivot 带着失败回到假设生成（§3.3） | 重跑 Stage 8 的提示词输入不变（见 [1.4](#14-并行方向怎么探索怎么收敛)） | `researchclaw/pipeline/stage_impls/_synthesis.py:103,113` |
| pivot ≤2、refine ≤10，两层循环（算法 1） | 两者共用一个计数，合计 ≤2 | `researchclaw/pipeline/stages.py:134`、`researchclaw/pipeline/runner.py:1557-1568` |
| 每个阶段有 JSON schema 契约与验收条件，如「至少 2 条假设标为可证伪」、错误码 `E-HYPO-*`（附录 A） | 契约是 dataclass，不是 JSON schema；执行器只查输入文件存在、输出文件非空；`dod` 与 `error_code` 是字符串，全仓无读取点，错误码实际写作 `E08_HYP_INVALID` | `researchclaw/pipeline/contracts.py:85-91`、`researchclaw/pipeline/executor.py:615-627,680-705` |
| CoPilot 的 Idea Workshop 做假设共创（§3.5） | 通用协作对话；`IdeaWorkshop` 只存占位对象 | 见 [1.2](#12-人怎么参与假设共创) |
| SmartPause 阈值随历史批准率自适应（§3.5） | 阈值写死 0.7；历史项权重 0.10，只读本 run 的干预记录；Stage 8 没有 PRM 分数时算不出低于 0.72 的分 | `researchclaw/pipeline/executor.py:305`、`researchclaw/hitl/smart_pause.py:154-180` |
| 七种干预模式，CoPilot 在 5 / 8 / 9 / 14 / 17 / 20 接收干预，Thorough 在 8 个阶段边界（§3.5、Table 10） | 模式枚举 6 个；`--mode` 另有 express / thorough / learning 三个预设，thorough 就是 checkpoint 模式，阶段边界 2 / 6 / 8 / 11 / 13 / 15 / 19 / 23 共 8 个，与 Table 10 一致。co-pilot 预设在 Stage 14 不暂停（不在批准、协作、跑后暂停任一组，SmartPause 在 14 上最低 0.80 也不触发），脚本化干预投递不到 14；Pre-Experiment / Post-Experiment 在代码里没有，只能用 `stage_policies` 拼 | `researchclaw/hitl/config.py:10-18,180-243`、`researchclaw/hitl/presets.py:37-86,117-127`、`researchclaw/cli.py:1229-1234` |
| HEP 用 Theorist / Phenomenologist / Experimentalist（附录 B.1） | 属实 | `researchclaw/prompts/hep.py:34-118` |

## 3. 平台哪里能用

平台现状（以文件为准）：假设阶段没有步骤能力，主文件未定名（`platform/framework/capabilities/__init__.py:42-52`）；助理可以 `ai4sci output new` 手写（`platform/framework/cli/output.py:1-6`）；设计阶段的 `design` 会把 `--from hypothesis/N` 目录里的全部文本文件拼进执行层提示词（`platform/framework/capabilities/design/__init__.py:102-108`）；分析阶段的提示词已有「证伪与未决」一节（`platform/framework/capabilities/analysis/prompt.md:22`）。框架不调模型（P-1），模型评审要派隔离的新会话、尚未实现（P-2），决策在协调层（P-10），每次产出一个 `<stage>/<n>/`、`meta.yaml` 的 `from` 带 hash（P-19）。

### 3.1 可摘出的方法与落点

| 可摘出的方法 | ARC 出处 | 落在平台哪里 | 需要的输入 | 产出 | 与平台现状的关系（事实） |
|---|---|---|---|---|---|
| 生成 / 可行性 / 反驳三个角色分开写，再合成，合成时保留分歧 | `researchclaw/prompts/ml.py:21-81`、`researchclaw/prompts/shared.py:750-768` | 假设阶段的一个步骤（要起执行层） | 已确认的 `requirement.md`；文献阶段的 `sources.md` 与解析过的论文（`pdf` skill 的 `paper.md`）；可选的上一轮分析产出 | 假设阶段主文件（名字由第一个能力定）；三份角色稿作私有文件 | 平台的执行层是 Claude Code / Codex 会话，三个角色可以是三次隔离的会话，也可以是一次会话写三节，两种做法角色之间可见性不同；ARC 默认是同一个客户端调三次，API 类 provider 下彼此不可见，acp（同样把 CLI agent 当后端）下进同一个会话（按代码推断） |
| 角色提示词按领域换一套（ML 与 HEP 两套，职责对位：提出 / 落地 / 挑刺） | `researchclaw/prompts/hep.py:34-118`、`researchclaw/prompts/manager.py:85-94` | 领域包 | 领域包给这一族的提示词补充 | 同上 | 平台已有「领域包给一族能力补提示词」的机制（`platform/docs/add-a-capability.md`「写代码」一节，`domains/<包>/prompts/<族>.md`） |
| 一条假设的字段：陈述、依据、可测预测（带阈值）、证伪条件、所需基线、风险等级；机器可读部分对照 ARC-Bench manifest 的 `hypotheses[{id, statement, measurable}]` | `researchclaw/prompts/ml.py:344-354`、2026-09-09 那篇 §7.2 | 假设阶段主文件的格式 | — | 带编号的假设条目 | `design` 已把假设产出拼进提示词；分析阶段的「证伪与未决」目前按自由文本写，没有假设编号可对 |
| 打分与合成分成两次调用：打分的一方只看各份稿件、不改写，合成的一方照排序写（anti self-preference） | `researchclaw/pipeline/debate.py:231-276` | P-2 所说的「隔离的新会话、只给产物不给轨迹」 | 各份候选假设 | 排序与理由 | P-2 这一段未实现。ARC 里只有配了 `reviewer_model` 才拆成两次调用；judge 可以只换模型名，也可以配独立的 provider / base_url / key（`researchclaw/llm/client.py:180-229`）；provider 是 acp 时面板与独立 judge 都为空（`researchclaw/llm/__init__.py:95-96,116-117`） |
| N 份候选、挑一份 | `researchclaw/pipeline/tournament.py:91-238` | 协调层多次跑同一个假设能力，得到 `hypothesis/1`、`hypothesis/2`… | 同上 | 多个并列产出 | 平台里同一阶段的多次产出本来就并列存放，下游读哪一份由 `--from` 点名、由人在断点签字（P-19），选哪一份是协调层的决定（P-10）；ARC 的做法是框架内一次 judge 调用选定 |
| 查新：用假设文本检索三库、列出最相近的论文与相似度 | `researchclaw/literature/novelty.py:185-356` | 一个 skill 脚本（零模型、联网），结果写进调用方给的目录，给人和助理看 | 假设文本、主题 | 近邻论文清单（标题、年份、链接、相似度、检索式） | ARC 的结果没有下游读取；平台已有联网的 skill 先例（`download`）；算法本身的问题见 [3.2](#32-反面arc-在这一段踩过的坑) |
| 上一轮分析结论作为重新出假设的输入 | ARC 没做（[1.4](#14-并行方向怎么探索怎么收敛)） | 假设步骤的可选输入 | `--from analysis/N` 的 `analysis.md` | 新一版假设 | 平台分析阶段的 `analysis.md` 固定有「证伪与未决」一节，写被证伪的假设与没试的方向（`platform/framework/capabilities/analysis/prompt.md:22`） |
| 在 Gap 列表上改，而不是在假设上改 | co-pilot 下 Stage 7 可协作、Stage 8 只吃 `synthesis.md` | 文献阶段或假设步骤的输入 | 人确认过的 Gap / 机会列表 | — | 平台里人的意见走对话与 `requirement.md`，由助理在开跑前带进输入 |

### 3.2 反面：ARC 在这一段踩过的坑

每条都有代码出处，也都能对应到平台已有或待写的规矩：

1. **人的意见在阶段跑完之后才到，改不到这个阶段的产物。** co-pilot 在 Stage 8 只在跑完后暂停，INJECT 写的意见文件要等下一次重跑才被读（`researchclaw/pipeline/executor.py:430-435`），而且终端里这个动作选不了（`researchclaw/hitl/intervention.py:194-201`）。平台里能力是纯函数（P-19），输入只有需求、材料与 `--from` 点名的产出，开跑之后给的意见进不了这一次产出。
2. **拒绝等于停机。** REJECT 让整条流水线停下，不会带着拒绝理由重新生成（`researchclaw/pipeline/runner.py:837-843`）；「Stage 9 被拒回 Stage 8」的回退表写了但没接（`researchclaw/pipeline/stages.py:117-123`）；ROLLBACK 选项没有处理分支。
3. **重跑拿到的是同样的输入。** PIVOT 后 Stage 8 的提示词里没有上一版假设和失败理由，人事先写的意见文件也随目录改名丢掉。
4. **假设版本和实验结果没绑在一起。** `_promote_best_stage14` 跨 PIVOT 版本按主指标挑结果（`researchclaw/pipeline/runner.py:1357-1460`）。平台的 `meta.yaml` `from` 带 hash（P-19），记录每份产出读的是哪一版输入。
5. **写了判据、没人读。** 查新报告、选题自评、契约 `dod`、`IdeaWorkshop.evaluate` 都算了或写了，都不改变任何走向。对应纲领 P-8「每个配置项必须有读取点与断言」。
6. **失败时写模板假设继续跑。** 角色调用全部失败、debate 抛异常，或带 `--skip-preflight` 跑而没有模型时，写死三条通用假设，Stage 8 记 DONE（`researchclaw/pipeline/executor.py:639-649`、`researchclaw/pipeline/_helpers.py:1591-1605`）。对应 P-7 fail-closed。
7. **查新算法本身。** 整段文本的关键词集合对单篇摘要做 Jaccard，分母被假设文本撑大（同一篇论文的摘要对它自己的方法节也只有 0.09，见 [1.5](#15-查新怎么做)）；只认 ASCII；先按引用数排序再截前 30 篇，新而低引的相近工作可能被截掉（`researchclaw/literature/search.py:279-280`、`researchclaw/literature/novelty.py:238`）。
8. **测试契约与生产不一致。** `IdeaWorkshop` 的单测把 `chat` mock 成返回字符串，生产返回数据类（[1.2](#12-人怎么参与假设共创)）。对应 P-8「集成点必须有测试」。
9. **论文与 README 超前于代码。** Idea Workshop、分支并行、SmartPause 自适应、pivot 带证据回流、README 列的 WebSocket / MCP 两个 HITL 适配器（`researchclaw/hitl/adapters/ws_adapter.py` 与 `mcp_adapter.py` 在 `researchclaw/` 其余代码里没有 import）都是这一类；2026-09-09 那篇 §10.2 第 6 条已记过同一现象。

## 4. 局限与前提

| 类别 | 事实 | 证据 |
|---|---|---|
| 数据 | 假设的全部文献依据是 Stage 6 抽出的知识卡片（最多 24 张）经 Stage 7 一次合成；卡片由模型一次调用从 `shortlist.jsonl`（检索返回的题录与摘要）加 Stage 4 的网页检索摘录（截 10000 字）抽取，没有全文 | `researchclaw/pipeline/stage_impls/_synthesis.py:40-46`、`researchclaw/pipeline/stage_impls/_literature.py:919-940` |
| 数据 | 查新要在线访问 OpenAlex、Semantic Scholar、arXiv；S2 key 可选，读的是 `llm.s2_api_key` 而不是文献检索段的同名字段（Stage 4 两处都读、还读环境变量 `S2_API_KEY`）；某个源失败时先退到本地检索缓存，再不行只剩与已收集论文的比较 | `researchclaw/pipeline/stage_impls/_synthesis.py:245`、`researchclaw/pipeline/stage_impls/_literature.py:414-418`、`researchclaw/config.py:203,243-244`、`researchclaw/literature/search.py:201-223`、`researchclaw/literature/novelty.py:259-262` |
| 数据 | 关键词正则只认 ASCII，停用词表是英文 ML 语境；中文假设只能抽到主题与夹带的英文词 | `researchclaw/literature/novelty.py:35-142` |
| 模型 | 非 acp provider 走 HTTP 接口（OpenAI 兼容、Anthropic 等），要 `base_url` 与 key；`researchclaw run` 默认先预检，缺了就退出，带 `--skip-preflight` 时 Stage 8 退回模板假设。debate 面板里的每个模型共用主配置的 endpoint 与 key，只换模型名，要跨厂商得靠 OpenRouter 这类聚合 endpoint；judge 可以单独配 provider / base_url / key | `researchclaw/cli.py:228-239`、`researchclaw/pipeline/executor.py:639-649`、`researchclaw/llm/__init__.py:60-85,122-144`、`researchclaw/llm/client.py:180-229` |
| 模型 | provider 选 acp（把 Claude Code、Codex 等 CLI agent 当后端，经仓库外的 `acpx`）时，debate 面板与独立 judge 都不构建，退回单模型；Stage 8 的各次调用进同一个具名会话 | `researchclaw/llm/__init__.py:78-80,95-96,116-117`、`researchclaw/llm/acp_client.py:1-7,474-480` |
| 模型 | 论文所有对比实验用同一骨干 GPT-5.3-codex；提示词英文、ML 口吻；领域角色只有 ml 与 hep_ph 两套可达 | 论文 §4.1；`researchclaw/pipeline/_domain.py:140-190` |
| 算力与成本 | Stage 8 默认 4 次调用（3 角色 + 1 合成），有意见文件再加 1 次；debate 一轮反驳：开场 3 + 反驳 3 + 打分 1 + 合成 1 = 8 次，没配 `reviewer_model` 时打分与合成是一次，共 7 次，每次失败或空输出再试一次；tournament 是 N + 1 次；PIVOT 与 REFINE 合计最多 2 次回退。论文报一次完整 run 花 3–15 美元 | `researchclaw/pipeline/debate.py:37-66,143-276`、`researchclaw/pipeline/tournament.py:144-219`；论文附录 J |
| 算力 | 「单卡 30 分钟」写死在 innovator 提示词里，不随 Stage 1 探测的硬件变 | `researchclaw/prompts/ml.py:32` |
| 人 | 暂停与协作对话都读流水线进程的 stdin：后台运行时暂停读到 EOF，终端适配器返回中止，该阶段记 FAILED；`attach` / `approve` / `reject` 只写 `hitl/response.json`，`researchclaw run` 开了 HITL 时总挂着输入回调，文件轮询只在回调抛异常时才走 | `researchclaw/hitl/adapters/cli_adapter.py:111-118`、`researchclaw/pipeline/executor.py:409-417,486-491`、`researchclaw/cli.py:377-394,2186-2301`、`researchclaw/hitl/session.py:181-237` |
| 许可证 | 代码 MIT，提示词文本在代码里，同样 MIT；论文是 arXiv 非独占分发许可[^arxiv-license] | `LICENSE` |
| 测试与 CI | debate、tournament、查新、分支各有单测（12、14、37、16 条），都用假客户端或 mock 检索；有测试直接调 Stage 8，但没有测试走 Stage 8 的 debate / tournament 分支；仓库无 CI（2026-09-09 那篇 §2） | `tests/test_debate_engine.py`、`tests/test_tournament_engine.py`、`tests/test_rc_novelty.py:365-460`、`tests/test_hitl_branching.py`、`tests/test_rc_executor.py:1490-1515` |

## 5. 还没弄清的问题

1. **HITL 消融里 Stage 8 的干预写了什么、怎么投递。** `experiments/hitl_ablation/` 在 `.gitignore:130`；`EXPERIMENT_DESIGN.md:66-71` 说那批干预文件按阶段 5 / 8 / 9 / 14 分键。按仓库里的 co-pilot 预设，Stage 8 的 inject 在跑完后才到、Stage 14 根本不暂停，与 Table 10 对不上。作者是否另配了 `stage_policies`，看不到；脚本化干预里如果用了 edit，`edited_files` 不会被写盘，这类干预是否出现过也看不到。
2. **Table 3 的数字口径。** 表里 CoPilot 干预 6 次、Step-by-Step 23 次，正文写 19 次与 29 次；1–10 的论文质量分由谁打没有写（Table 11 的案例用的是流水线自己的 Stage 20 分）。Table 3 的 Thorough 是否就是 `--mode thorough` 预设（checkpoint 模式），论文没写。
3. **Table 5 的 w/o Debate 用的是不是 `ARC_ABL_DISABLE_DEBATE`。** 如果是，对照组只剩 innovator 与 optimist；p=0.003 用的什么检验没有写。
4. **附录 F 的「假设多样性」怎么量，K=2 / K=5 怎么配出来的。** 代码里没有角色数参数。
5. **debate 的反驳轮与 tournament 对假设质量有没有用。** 两者晚于论文加入，仓库里没有对应实验。
6. **查新在真实产物上是否几乎总报 high。** 本文用论文自己的文本估了量级（Jaccard 0.09），没有拿真实的 `hypotheses.md` 与检索结果算。
7. **provider=acp 时角色之间到底能不能看到彼此。** 同一个 `ACPClient` 在 Stage 8 内复用、会话名固定，按 `acp_client.py` 的 docstring 会话保留上下文；但会话怎么存历史、`sessions close` 之后 `sessions ensure` 是否恢复历史，都在仓库外的 acpx 里，本次没查也没跑。
8. **`IdeaWorkshop.brainstorm` 接真客户端是否必然返回空列表、`_promote_best_stage14` 是否真会取到 PIVOT 前的结果、人在 Stage 15 是否确实无法经 HITL 触发 PIVOT、`--to-stage` / `--from-stage` 手改假设再续跑是否顺畅。** 都是读代码的推断，未执行。
9. **平台一侧要定的事**（本文不下结论，归 #155 比较）：假设阶段主文件叫什么、字段要不要机器可读；查新做 skill 还是步骤、联网走 skill 脚本还是 agent 自带的搜索；三个角色用三次隔离会话还是一次会话写三节；P-2 的「隔离新会话」用同一家 CLI、同一模型时算不算独立评审，要不要为打分单独配模型。

## 6. 调研方法

- 读 2026-09-09 那篇，确定本篇只看假设相关部分；从 `_synthesis.py` 的 Stage 8 入口出发，顺着调用读到提示词、debate、tournament、HITL 执行器与适配器、查新、runner 的 PIVOT 处理、ACP 客户端，再反查 README、`docs/HITL_GUIDE.md` 与 `experiments/arc_bench/` 里的说法。
- 「零调用」的判断都用 grep 查过生产代码（`researchclaw/` 下除自身与 `__init__` 导出外无引用），测试里的引用单列。
- 本地是浅克隆，文件提交历史用 GitHub API 查[^gh-commits]；论文发表时的 Stage 8 用 v0.5.0 提交的文件对比[^v050-diff]。
- 论文 PDF 下到外层 `materials/research/2026-0927-scientific-ai-capabilities/papers/`（gitignore），用平台的 `pdf` skill 解析；引用按章节与表号。版本与许可证在 arXiv 页面上核过[^arc-paper][^arxiv-license]。
- 查新 Jaccard 的量级用论文自己的摘要与 §3.2–3.3 正文，按 `novelty.py` 同样的正则与停用词自己写几行 Python 算，没有 import 或运行 ARC 的代码。
- 第一版写完后另一个会话照出处逐条复查过一遍：行号偏的改了，终端可选动作、`--mode thorough` 预设、`stage_policies` 的适用范围、debate 在没配 `reviewer_model` 时的形态、acp 会话复用、`--from-stage` 通路、查新的量级估计这几处按代码改了说法。
- 没有安装依赖、没有运行 ARC 的任何代码；标「按代码推断」「按公式推算」的条目未经执行验证。

[^arc-paper]: Jiaqi Liu、Shi Qiu 等，AutoResearchClaw: Self-Reinforcing Autonomous Research with Human-AI Collaboration，arXiv 2605.20025；v1 2026-05-19，v2 2026-05-23，<https://arxiv.org/abs/2605.20025>。
[^gh-commits]: GitHub commits API 按文件查提交记录，2026-09-27 查：`debate.py` 与 `tournament.py` 只有 1d7e46f（2026-08-18，feat(review): independent reviewer, multi-model debate, best-of-N tournament）；`hitl/workshops/idea.py`、`hitl/branching.py`、`hitl/smart_pause.py` 只有 40836b2（2026-04-01，v0.4.0）；`literature/novelty.py` 最后一次改在 2026-03-16（5e308d6）。<https://api.github.com/repos/aiming-lab/AutoResearchClaw/commits>。
[^v050-diff]: v0.5.0 发布提交 12d3fd8（2026-05-20）的 `researchclaw/pipeline/stage_impls/_synthesis.py`，<https://github.com/aiming-lab/AutoResearchClaw/blob/12d3fd8/researchclaw/pipeline/stage_impls/_synthesis.py>；与 be4ba47 对比，差异只有 tournament 与 debate 两段分支及其 import。
[^arxiv-license]: arXiv 页面标注的许可为 arXiv.org perpetual, non-exclusive license 1.0，<http://arxiv.org/licenses/nonexclusive-distrib/1.0/>，2026-09-27 查。
