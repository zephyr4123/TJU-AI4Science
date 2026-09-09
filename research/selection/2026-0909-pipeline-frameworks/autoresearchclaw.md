---
title: AutoResearchClaw 代码级深读
subtitle: 流水线层选型 · 23 阶段、8 万行、宣传与代码的差距逐条对账
kind: 开源项目选型深读（只读代码，不跑、不装依赖）
date: 2026-09-09
scope: 仓库 https://github.com/aiming-lab/AutoResearchClaw，克隆到 vendor/AutoResearchClaw，提交 be4ba47（v0.5.0 之后，2026-08-19）；不读 docs/showcase、website、frontend-legacy、image 与各语言 README 翻译；文中 文件:行 均相对该仓库根
status: 第一版
---

> **结论先行**：它在四个总问题上都比 InternAgent 深，但深的位置跟 README 写的不是同一处。**编排**：多了产物契约表、原子 checkpoint、HITL 钩子三件确定性设施，但编排本身仍是外层 `for` 加七处硬编码特判，状态机写了、测了、没接线。**后端**：LLM 客户端厚一档，沙盒层有真抽象，但"跑在五个 CLI 上"是把 agent 名原样透传给外部 npm 包 `acpx`，本仓零分支；最像样的 `CodeAgentProvider` 协议整块零调用。**实验内环**：比 InternAgent 多的实质只有 revert-to-best 一件事，第 N 轮的 prompt 里没有前 N-1 轮的指标；真正厚的是旁边那层确定性反造假规则。**验证层**：数字对账和引用真伪两条链是纯确定性、零 LLM、有真测试的机器判据，InternAgent 完全没有；其余"多 agent 评审"是一次调用扮三个角色，评审回流只有一跳。
>
> 全仓 81.5k 行里，零生产调用的死代码保守估计过万行，`runner.py` 主循环引用了四个仓库里不存在的模块，一律被 `except` 吞成 debug 日志。101 个测试文件 3.9 万行，没有任何 CI 在跑。作者自己 2026-07-03 的代码审查列了 7 条 P0，其中 4 条到现在还在。
>
> 怎么读：第 1 节是四个总问题的答案表，第 9 节是缺陷清单，第 10 节是能借什么。它给我们最大的价值是两样：一套值得直接抄的**任务契约与验证层部件**（ARC-Bench manifest、VerifiedRegistry、引用校验、immutable harness），和一份**反面清单**（"定义了 Protocol"与"Protocol 被接上"是两件事，"配置里写了"与"代码读了"是两件事）。横向对比见同目录的 [README.md](README.md)。

## 1. 结论

**一句话**：抽象方向选对了，把"模型可能骗人"当一等公民用确定性规则去卡；但工程上是一个人五个月堆出来的 8 万行，一半没通电。零件按模块摘，骨架不要。

**四个总问题的答案**：

| 问题 | README 说 | 代码里 | 证据 |
|---|---|---|---|
| 编排有没有抽象层 | 23 阶段流水线、pipeline branching、self-evolving | 阶段顺序写死在 `IntEnum`，`_STAGE_EXECUTORS` 是字面量 dict，CLI 只能切连续区间；`stages.py` 的状态机 `advance()` 全仓一处调用且返回值被 `_ =` 丢弃，`TRANSITION_MAP` 生产零引用；branching 只拷目录不执行 | `stages.py:22-62`、`executor.py:652`、`hitl/branching.py:94-278` |
| 后端有没有抽象 | 跑在 Claude Code / Codex / Copilot / Gemini / Kimi 上，Stage 10 & 13 可委托外部 CLI agent | ACP 路径把 `config.llm.acp.agent` 字符串原样塞进 `acpx` 的 argv，零分支；`experiment/code_agent.py` 的 `CodeAgentProvider` + `ClaudeCodeAgent` + `CodexAgent` 零调用零测试；三个 domain agent sandbox 仍是宿主机 `subprocess.run(['claude','-p',...])` + `--dangerously-skip-permissions` | `acp_client.py:474-481`、`experiment/code_agent.py:732-778`、`collider_agent_sandbox.py:661-690` |
| 实验内环比"结果塞 prompt"深多少 | 迭代精修、自愈、收敛评估 | 第 N 轮 prompt = 历史最优代码 + Stage 12 基线摘要，`run_summaries` 循环内从不追加，`best_metric` 数值不进 prompt；多出来的实质是 revert-to-best（约 20 行能实现）；harness 写的 `results.json` 因路径 `_project` vs `_project_{n}` 对不上从未被读；convergence evaluator 零调用 | `_execution.py:802-826,1110`、`_execution.py:325-328` vs `sandbox.py:369-374` |
| 验证层深在哪 | 4 层引用校验、多 agent 评审、7 维评分、反造假、claim 校验 | 真硬的两条：`VerifiedRegistry` + `paper_verifier`（数字白名单）、`literature/verify.py`（五源引用校验），零 LLM、有几十条行为测试；"多 agent 评审"是一次 LLM 调用扮三个 reviewer；7 维评分只写日志；`claim_verifier` 与 `assessor/` 整包零调用；唯一会终止流水线的硬闸包在 `except: pass` 里，其测试是 `assert True  # Placeholder` | `verified_registry.py:75-117`、`prompts/ml.py:1095-1121`、`_review_publish.py:621-636`、`tests/test_fabrication_guards.py:205-211` |

**能直接借的**（按性价比，详见[第 10 节](#10-对-demo-的意义)）：ARC-Bench 的 manifest + rubric + requirements 三件套（纯数据格式）；`harness_template.py`（119 行 immutable harness）；`VerifiedRegistry` + `paper_verifier`（约 1000 行，只吃一个 JSON 契约）；`literature/verify.py`（974 行纯 stdlib）；`contracts.py` 的产物契约表形状；HITL 的 `intervention.py` + `file_wait.py` + pre/post hook 签名；`llm/client.py` 的重试与 fallback；`experiment_diagnosis.py` 的失败分类思路；`debate.py`。

**不借的**：`runner.py`（1864 行主循环）；Stage 13 那 877 行精修循环；ACP 路径；三个 domain agent sandbox；`hitl/` 里零调用的那一半；`memory/` 的接线；skills 匹配器；`assessor/`、`claim_verifier`；`requirements.txt` 式的整仓 fork。

**对 demo 的定位**：不 fork。按它的抽象自己写一遍薄的，零件按模块摘。它证明了两件事：验证层可以做成机器可判、零 LLM、跟生成路径解耦的规则；以及没有 CI 的"测试很多"不等于质量。

## 2. 仓库画像

| 项 | 实况 |
|---|---|
| 仓库 | <https://github.com/aiming-lab/AutoResearchClaw>，UNC AIMING Lab，MIT，14k star；论文 arXiv 2605.20025 |
| 版本线 | v0.1.0 到 v0.3.2 全在 2026-03-15 到 03-22 一周内；v0.4.0（04-01，HITL）；v0.5.0（05-19，多领域 agent + ARC-Bench）；之后到 08-19 最后一次提交，三个半月零发版 |
| 活跃度 | 303 个提交：2026-03 占 196（65%），04 月 39，05 月 28，06 月 7，07 月 19，08 月 14；主力作者 170 个（56%），约 25 个外部贡献者合计 100 多；社区 PR 真在被合。v0.5.0 是 squash 发布，之后两次提交专门恢复被 squash 丢掉的修复 |
| 规模 | 95 MB 克隆（工作树 52 MB，其中 33 MB 是 `docs/showcase` 的展示 PDF 和 PNG）；`researchclaw/` 81.5k 行 Python、354 个文件；`tests/` 101 个文件 3.9 万行、2630 个 `def test_` |
| 最大的文件 | `_review_publish.py` 2937、`cli.py` 2325、`_paper_writing.py` 2308、`runner.py` 1864、`_helpers.py` 1847、`config.py` 1775、`_code_generation.py` 1531、`code_agent.py` 1514、`_execution.py` 1452 |
| 依赖 | 核心只有 4 个（pyyaml、rich、arxiv、numpy），`requires-python >= 3.11`；extras 分 anthropic / web / pdf / all / dev |
| 打包 | `pyproject.toml:35` 声明打包 `sibyl`、`arc` 两个仓库里不存在的目录 |
| 测试与 CI | 没有 `.github/`、没有任何 CI 配置、`conftest.py` 只有一行注释零 fixture；README 的 "Tests 2699 passed" 是写死的静态徽章 |
| 自审 | `docs/CODE_REVIEW_2026-07-03.md`：作者自己列 7 条 P0，核心结论"多个以反造假为卖点的防线在最需要生效时自我关闭" |

## 3. 流水线骨架

### 3.1 23 个阶段

`Stage` 是 `IntEnum`（`stages.py:22-62`），顺序由枚举定义：1 TOPIC_INIT → 2 PROBLEM_DECOMPOSE → 3 SEARCH_STRATEGY → 4 LITERATURE_COLLECT → 5 LITERATURE_SCREEN（门）→ 6 KNOWLEDGE_EXTRACT → 7 SYNTHESIS → 8 HYPOTHESIS_GEN → 9 EXPERIMENT_DESIGN（门）→ 10 CODE_GENERATION → 11 RESOURCE_PLANNING → 12 EXPERIMENT_RUN → 13 ITERATIVE_REFINE → 14 RESULT_ANALYSIS → 15 RESEARCH_DECISION → 16 PAPER_OUTLINE → 17 PAPER_DRAFT → 18 PEER_REVIEW → 19 PAPER_REVISION → 20 QUALITY_GATE（门）→ 21 KNOWLEDGE_ARCHIVE → 22 EXPORT_PUBLISH → 23 CITATION_VERIFY。

确定性为主的只有 3 个（4 打真实文献 API、12 执行、23 引用校验），其余 20 个以 LLM 为主体，且几乎每个都带"LLM 失败 → 写死模板"的降级：stage 4 退到 `[Placeholder]` 假论文、stage 6 退到 "Template method summary" 假卡片、stage 1/2/7 退到硬编码 markdown（`_literature.py:404-455,940-957`、`_topic.py:66-93`）。一条"LLM 全程不可用也能跑出一篇完整论文"的路径是通的。

### 3.2 三件确定性设施，InternAgent 一样都没有

- **产物契约表** `contracts.py:29-208`：23 个 `StageContract` 逐条声明 `input_files` / `output_files`，`execute_stage` 进入前校验上游产物存在、结束后校验自己该产的产了（`executor.py:615-628,679-700`）。但只到"文件存在且非空"，没有 jsonschema，`dod` / `error_code` / `max_retries` 三个字段全仓无消费点，契约测试自己注释承认"只验声明连续性不验 runtime wiring"。
- **原子 checkpoint** `runner.py:78-108`：`tempfile.mkstemp` + `Path.replace` 写单个 JSON `{last_completed_stage, run_id, timestamp}`，每个 DONE 阶段后写一次；`--resume` 按 topic 的 sha256 前 6 位找回历史 run 目录。粒度是阶段级，阶段内的中间态（Stage 13 的迭代轮次）不进 checkpoint。
- **HITL 钩子** `executor.py:606,819`：`_run_hitl_pre_stage` 与 `_run_hitl_post_stage` 插在 `execute_stage` 头尾，SKIP / ABORT / REJECT / EDIT / INJECT 五种人类动作各有明确语义，23 个 stage 实现一行没改。这是真接线的（详见[第 6 节](#6-hitl-与自进化)）。

### 3.3 编排本身没有抽象层

`execute_pipeline` 的主体就是 `for stage in STAGE_SEQUENCE:`（`runner.py:483`），循环体内散着 7 处 `if stage == ...` 硬编码特判。失败处理：FAILED → `break`；PAUSED → `break`；BLOCKED_APPROVAL 且 `stop_on_gate` → `break`。没有重试（`StageResult.decision` 会被设成 `"retry"` 但 runner 从不读），`pipeline/` 下没有任何线程池、asyncio 或 multiprocessing，零并行。

CLI 只有 `--from-stage` / `--to-stage` 两个端点且强制 `to >= from`，不能跳中间、不能换序、不能插自定义阶段；`NONCRITICAL_STAGES` 只剩 `KNOWLEDGE_ARCHIVE` 一个成员。加一个阶段要改枚举、`contracts`、dispatch、`PHASE_MAP`、prompt bank 五处。

**状态机是装饰品**：`stages.py:189-361` 定义了 9 个 `StageStatus`、9 个 `TransitionEvent`、`TRANSITION_MAP`、110 行的 `advance()`、`GATE_ROLLBACK`，配了 35 个测试。运行时唯一调用是 `executor.py:652` 的 `_ = advance(stage, StageStatus.PENDING, TransitionEvent.START)`，`TRANSITION_MAP` 在 `researchclaw/` 下零引用。真正的门禁判定绕开它手工构造。

**四个幽灵模块**：`runner.py` 主循环号称的事件日志、成本熔断、实验 spec 校验、代码陷阱检测四项能力，分别 import `researchclaw/pipeline/event_log.py`、`researchclaw/cost_tracker.py`、`researchclaw/pipeline/experiment_spec.py`、`researchclaw/pipeline/pitfall_detector.py`（`runner.py:463,510,554,584`），四个文件在仓库里都不存在，`ImportError` 被 `except` 吞成 `logger.debug`，永久静默 no-op。用户以为 `max_budget_usd` 设了预算上限，实际跑的是无限预算。

### 3.4 唯一真活着的回退：PIVOT / REFINE

Stage 15 返回 `pivot` 或 `refine` 时（`runner.py:700-810`），runner 读 `decision_history.json` 数回退次数，上限 `MAX_DECISION_PIVOTS=2`，把 `stage-{回退点..15}` 目录 rename 成 `stage-NN_v{N}`，递归调用 `execute_pipeline(from_stage=...)`。pivot 回 8，refine 回 13。用尽次数后跑四项启发式质量检查，不通过只写 `quality_warning.txt` 然后 forced PROCEED，不阻断。另有一个 `execute_iterative_pipeline` 包在外面按质量分重跑论文段（`runner.py:1629-1748`），但 CLI 的 `run` 不调用它。

### 3.5 跨阶段状态：磁盘 + 文件名 glob

阶段之间零内存传递，每个 stage impl 签名是 `(stage_dir, run_dir, config, adapters, *, llm, prompts)`，返回 frozen 的 `StageResult`。跨阶段读取靠 `_read_prior_artifact` 对 `run_dir/stage-*` 做文件名 glob 后按目录名倒序取第一个（`_helpers.py:398-421`），即"编号最大的目录里同名文件"，不是"契约声明的生产者"。REFINE 重入产生 `stage-14_v{N}` 并存时会读错，代码里为此打了 `analysis_best.md` / `experiment_summary_best.json` / `_promote_best_stage14` 至少四层补丁，注释挂着 BUG-205/211/215/218/225/226。

### 3.6 prompt 体系

仓库根的 `prompts.default.yaml` 不是运行时读取的文件，全仓无 load，只是给用户 copy 的模板，且已过期（blocks 3/19、sub_prompts 3/11）。真正的源是 `researchclaw/prompts/{ml,hep,biology}.py` + `shared.py`，`PromptManager` 按 domain 选 bank，stages 做 `dict.update()` 浅合并，`for_stage()` 渲染时追加 evolution overlay 与 `extra_prompts`（`prompts/manager.py:74-270`）。blocks 由各 stage impl 手工 `_pm.block(name)` 拼，全仓 27 个调用点，没有声明式映射。

`_prompt_bank_domain_from_config` 只可能返回 `ml` 或 `hep_ph`（`_domain.py:139-190`），`biology.py` 597 行的完整 bank 全仓无人构造，不可达。

## 4. 实验内环

### 4.1 代码怎么生成

不是 LLM 单发。默认走 `pipeline/code_agent.py` 的 `CodeAgent`：蓝图规划 → 按依赖逐文件生成 → AST 硬校验最多 4 轮定向修 → 真沙盒 exec-fix 最多 3 轮 → reviewer/coder 对话最多 2 轮（`code_agent.py:41-77,192-279,663-711`）。上面还挂 OpenCode "Beast Mode"（详见 5.4），失败回落 CodeAgent，再回落 legacy 单发。

**全部失败时的兜底会造假数据**：`_code_generation.py:775-804` 直接写死一段 numpy 随机数脚本当 `main.py`，跑 3 个 condition × 3 seed 打印指标。这份"实验"能正常产出指标、绕过 Stage 12 的零指标硬门禁、一路进论文。validator 能识别 `np.sum(x**2)` 但只 warning。

### 4.2 immutable harness：全仓最值钱的 119 行

`experiment/harness_template.py` 执行前由沙盒复制进项目目录成 `experiment_harness.py`，LLM 代码被 prompt 强制 import。四个接口：`should_stop()`（到 80% 预算返回 True）、`check_value()`（NaN/Inf 计满 5 次 `sys.exit(1)`）、`report_metric(name, value)`（校验后按 `name: value` 打印 stdout）、`finalize()`（写 `results.json`）。注释明说灵感来自 karpathy/autoresearch 的 immutable `prepare.py`。这是"LLM 改不了的指标上报信任边界"。

但 **`finalize()` 写的 `results.json` 从未被读**：`_execution.py:327` 去 `runs_dir/sandbox/_project/results.json` 找，`sandbox.py:371` 建的目录叫 `_project_{n}`，路径永远对不上，`structured_results` 恒为 None，指标一律退化成 stdout 正则。`experiment/metrics.py`（264 行 JSON→CSV→stdout 三级解析）与 `evaluators/convergence.py`（172 行）零生产调用。

### 4.3 Stage 13：迭代 N 到 N+1 到底传了什么

主路径在 `_execution.py:576-1452` 的 `_execute_iterative_refine`（877 行）。每轮：用 `best_files` 渲染上下文 → `iterative_improve` prompt → 多文件抽取 merge 进 `best_files` → 静态校验，失败修一次 → 写 `experiment_v{N}/` → 真沙盒跑 → 模糊取指标 → 检测 NaN/stderr 告警再修一次。

传进下一轮 prompt 的（`_execution.py:1096-1134`）：历史最优代码全文；`run_summaries`（**只来自 Stage 12 的基线 run，`:826` 是循环外唯一的 append，循环内从不追加**）；`metric_key` + `metric_direction` 字面量；`exp_plan` 锚与"不得改条件名"硬规则；条件覆盖缺口、饱和、超时缩规模三条提示。**没有的**：前 1..N-1 轮的 stdout 与指标、`best_metric` / `last_metric` 数值。第 10 轮看到的"上一次跑出来什么"跟第 1 轮一模一样。

讽刺的是把 last/best metric 全塞进 prompt 的那份实现（`experiment/runner.py:239-264`）恰恰没接进流水线；`experiment/code_agent.py:135-155` 的 `format_feedback_for_agent` 同样零调用。

**改进判定**：`metric_direction` 在 `:703` 读入，`_is_better` 闭包比较；改进则 `best_metric` / `best_files` / `best_version` 一起更新，不改进只 `no_improve_streak++`，`best_files` 不动。这构成事实上的 revert-to-best，是它相对"结果塞 prompt"唯一多出来的实质机制，约 20 行能实现。三个停止条件：墙钟超 `1.5 × time_budget_sec`、连续 3 轮无指标、连续 2 轮不改进。`max_iterations` 硬夹到 10。

`git_manager.py`（每轮 commit、失败 `reset --hard`）只被未接线的 `experiment/runner.py` 用，`_execution.py:478` 实例化时没传 `git_repo_dir`。Stage 13 的版本管理靠 `experiment_v{N}/` 目录快照。

### 4.4 自愈链路：真做了，且是比 traceback 回喂深一层的东西

`experiment_diagnosis.py`（738 行）定义 14 类 `DeficiencyType`（no_conditions / few_seeds / time_guard / synthetic_data / code_crash / missing_dep / identical_conditions / gpu_oom …），12 个检查器全是确定性正则或统计规则，不调 LLM，每条带 severity + `suggested_fix`。`experiment_repair.py`（905 行）最多 3 轮：诊断 → 把结构化诊断渲染成分级章节并按类型追加"SCOPE REDUCTION REQUIRED"之类的可执行指令（砍条件数、降 epoch、换预缓存数据集）→ LLM 或 OpenCode 出码 → 真沙盒重跑 → 按质量分择优保留。同类问题在历史诊断里重复出现 ≥ 3 类判不可修复直接停手。默认开启，挂在 Stage 14 之后。

与 InternAgent 的差别三层：错误被分类成枚举而不是原文回喂；修复指令按类型查表得到可执行动作而不是让模型看报错猜；有跨轮记忆防无限重试。底座仍是"把结构化文本塞进一次 LLM 调用"。

### 4.5 simulated 模式

`ExperimentConfig.mode` 代码默认值是 `'simulated'`（`config.py:585`），按公式 `0.3 + idx*0.03` 造指标；example yaml 改成 `sandbox` 并中文注释"仅用于框架开发调试"。三道拦截：Stage 13 跳过、repair 跳过、Stage 17 扫 `stage-*/runs/*.json` 全部 `status=='simulated'` 就 PAUSED。两个开口：文献综述型 topic 豁免；只要混进一条非 simulated 记录就失效。用户自己写 config 漏写 `mode` 就会默默跑假数据。

## 5. 底座后端与沙盒

### 5.1 LLM 调用层：确实厚一档

`llm/client.py` 纯 stdlib urllib：12 个 provider preset（openai / openrouter / deepseek / anthropic / kimi / novita / minimax 四变体 / ollama / openai-compatible）；模型名 fallback 链（`:274-303`，同一 base_url 换不了厂商）；重试按状态码分级（429/5xx/529 + 关键词判定的瞬时 400 可重试，403 直接抛给模型 fallback），指数退避 base 2s、上限 300s、加 jitter（`:348-456`）；Anthropic Messages 与 OpenAI Responses 两套 wire 适配；`json_mode` 在不支持 `response_format` 的 provider 上降级成 system prompt 注入。这些是踩过坑的代码。但没有基类或 Protocol，`create_llm_client()` 返回 `LLMClient | ACPClient` 联合类型靠 duck typing。

**成本记账不存在**：`LLMResponse` 正确解析 token 数，但没有全局 ledger；`cost_tracker` 模块不存在，`cost_guard.py` 的备选路径读 `run_dir/cost_log.jsonl` 而全仓没有代码写它。

### 5.2 ACP 后端：能力全在仓库外

`acp_client.py` 全篇是对外部 npm 包 `acpx` 的 subprocess 拼装：`acpx --approve-all --max-turns N --ttl 0 --cwd <abs> <agent> -s <session> <prompt>`（`:474-481`）。`config.llm.acp.agent` 是自由字符串原样透传，本仓对 Claude Code / Codex / Copilot / Gemini / Kimi 零分支，`preflight` 只做 `shutil.which`。JSON-RPC over stdio 由 `acpx` 负责，本仓只用四条正则剥元信息行。

工程细节比 InternAgent 厚：warm-up prompt、超长 prompt 自动切 stdin（分 Linux 100KB / win32 20KB / .cmd 6KB 三档）、多语言"命令行过长"关键词表、session 死亡重连最多 2 次、Popen + 后台读线程 + 30 秒心跳。但两个语义缺陷：`max_turns` 默认 1，agent 每次只能出一轮不能自己调工具，ACP 被当成"贵一点的 chat completion"；ACP 模式下 token 恒为 0，reviewer LLM 返回 None、debate panel 返回 `[]`，即选了"用 CLI agent 当后端"会静默关掉独立评审与辩论。

### 5.3 CLI-agent code generation backend：最漂亮的抽象，整块死代码

`experiment/code_agent.py`（777 行）定义 `CodeAgentProvider` Protocol（generate / refine / repair）+ `_CliAgentBase`（共享 subprocess、进程组清理、产物收集）+ `ClaudeCodeAgent`（`claude -p <prompt> --dangerously-skip-permissions --output-format text --allowed-tools "Bash Edit Write Read" --add-dir <workdir> [--max-budget-usd X]`）+ `CodexAgent`（`codex exec ... --sandbox workspace-write --json`）+ `create_code_agent` 工厂。全仓 grep：零调用点、零测试。Stage 10 走的是同名的另一个模块 `pipeline/code_agent.py`（纯 LLM）。git log 显示 v0.3.2 一次性加入，从未接线。二进制找不到时直接 `raise`，不降级。

### 5.4 OpenCode beast mode：真接线、默认开

`opencode_bridge.py`：在 `stage_dir` 下建临时 workspace，写计划与指导文件，`git init + commit`（opencode 要求是 git 仓），跑 `opencode run -m <provider/model> --format json <mega_prompt>`，Linux 上用 `script -q -e -c` 包伪 TTY（因为 opencode 无 TTY 时"exit 0 但没输出"）。`complexity_threshold` 是六信号加权的关键词计数（组件词 18 个、领域复杂词 24 个，`:34-109`），默认阈值 0.2 配合 `enabled=true, auto=true`，等于装了 opencode 就基本 always 走。失败回退是真的。跨领域这套英文 ML 词表基本无信号。

### 5.5 沙盒

| 模式 | 实况 | 隔离 |
|---|---|---|
| `sandbox`（example 默认） | `subprocess.run([python, -u, script], env={**os.environ})`，继承全部环境变量含所有 API key | 无。config 里 `allowed_imports`、`max_memory_mb` 被解析但全仓无读取点 |
| `docker` | `--memory`、`--shm-size`、`--user UID:GID`、`--gpus`、HOME/TORCH_HOME 重定向、env 名白名单、超时 `docker kill` + `finally rm -f`；三阶段 `entrypoint.sh` | 最实的一种。但 `network_policy=setup_only` 同时加了 `--user` 非 root 和 `--cap-add=NET_ADMIN`，非 root 执行不了 iptables，`entrypoint.sh:41-51` 打一行 warning 继续联网。默认档位等价于全联网 |
| `ssh_remote` | scp 上传 → `unshare --net python3 main.py`（无 unshare 静默降级）→ stdout 正则回收 → 无条件 `rm -rf` 远端目录；`StrictHostKeyChecking=no` | `use_docker=true` 时把 `python3 -u main.py` 追加在镜像名后，与自家镜像 `ENTRYPOINT` 冲突，拼出 `python3 -u /workspace/python3 -u main.py`，必挂 |
| `colab_drive` | 文件系统当队列，轮询 `done/<task>/result.json`；notebook 模板硬编码 `DRIVE_ROOT` | 靠 Colab 是一次性 VM |
| `agentic` | 长驻容器内 `npm install claude-code` + `docker exec claude -p --allowedTools 'Bash(*)'` | 整块死代码，`factory` 对 `mode="agentic"` 直接抛不支持 |
| `collider_agent` / `biology_agent` / `stat_agent` | 876 / 710 / 603 行复制粘贴，无共同基类；宿主机 `subprocess.run(['claude','-p',...,'--max-turns',N,'--dangerously-skip-permissions'])` | 无。且默认 `install_skills=True` 把 `external/agents/*/skills` 复制到用户全局 `~/.claude/skills/`，同名先 `rmtree` 再拷 |

`factory.py:29-34`：docker daemon 连不上时只打 warning 就返回本地 `ExperimentSandbox`，用户配的是容器隔离，拿到的是宿主机裸 subprocess。

唯一生效的结构化抽象是 `SandboxProtocol`（`sandbox.py:291`，`run` / `run_project` 两方法）+ 7 实现 + factory if 链。新增一个 domain agent sandbox 约 600 到 880 行整文件复制。

### 5.6 硬编码与权限

四个默认模型名散在不同文件（`claude-sonnet-4-6`、`sonnet`、`gpt-5.4`、`gpt-4o`）；`_NEW_PARAM_MODELS` 写死 gpt-5.x 系列并强制 `max_completion_tokens >= 32768`；`json_mode` 不兼容名单是 13 条模型名前缀；固定 Chrome 131 UA 注释自称"Cloudflare bypass"；`acpx` 备用路径写死 `~/.openclaw/extensions/acpx/...`；docker 数据集挂载写死 `/opt/datasets`。权限：三处 `--dangerously-skip-permissions` 默认值 + 一处硬写进 argv + `acpx --approve-all` 无开关 + `--allowedTools 'Bash(*)'`。

## 6. HITL 与自进化

### 6.1 HITL：接口真、接线一半

六种模式（`full-auto` / `gate-only` / `checkpoint` / `step-by-step` / `co-pilot` / `custom`）是 `InterventionMode` 枚举 + 纯函数映射成 12 字段的 `StagePolicy`（`hitl/config.py:28-56,180-243`）；模式差异靠三组硬编码 stage 集合。暂停点只有两个，插在 `execute_stage` 头尾，粒度到 stage 边界，做不到实验内环第 3 轮打断。

回传通道三条：进程内 callback（阻塞 `input()`）；**文件 IPC**（`run_dir/hitl/waiting.json` 写出、2 秒轮询 `response.json`，默认超时 24h，`file_wait.py:53-120`，TOCTOU 与坏 JSON 计数都处理了）；scripted JSON（离线消融用）。CLI 的 `attach` / `approve` / `reject` 就是往 `response.json` 写 dict。`session.wait_for_human` 的降级链写得严谨：callback 异常 → 文件轮询 → 只有显式 `auto_proceed_on_timeout` 才 APPROVE，否则 ABORT，注释"不要伪造一个用户要求审查的批准"（`session.py:169-244`）。

**SmartPause 默认永不触发**：置信度是 5 项固定权重线性组合（`smart_pause.py:35-51`），阈值 0.7；调用方只传 `quality_score`，而它只在 `prm_score.json` 存在时非 1.0，该文件唯一写入方是默认关闭的 MetaClaw PRM gate。代入默认值 overall ≥ 0.82 > 0.7。

**CostGuard 有 bug**：每个 stage 都 `new` 一个，`_notified_thresholds` 随之重置，花过 50% 后每个 stage 结束都重新触发一次"阈值突破"暂停（`executor.py:277`）；它读的 `hitl.cost_budget_usd` 与 runner 的 `max_budget_usd` 是两套互不相干的预算。

**死代码一半**：`hitl/` 实际 35 个文件 7835 行，只被测试引用、生产零调用的 3855 行（49%）：hooks、notify、escalation、learning、quality_predictor、claim_verifier、branching、context_manager、diff_view、editor、checksums、summarizer、tui/monitor、ws_adapter（504）、mcp_adapter（267）。WebSocket / MCP 适配器全仓无实例化处；`HITL_GUIDE.md` 写的 `hitl.escalation` 配置不被解析、`researchclaw branch create/compare/merge` 三条命令不存在。三个 workshop 的 brainstorm / evaluate 方法从不被调用，stage 7/9/17 只调 `save()` dump JSON 且裹 `except: pass`；`PaperCoWriter` 有一处 `_re_pw.search(draft_text, _re_pw.DOTALL)` 把 pattern 丢了，必抛 `TypeError` 被吞。README 说的 Stage 10 mid-stage HITL 调 `adapters.hitl.confirm(...)`，`HITLSession` 没有 `confirm` 方法，永远走不通。

`HITLConfig.enabled` 默认 False，example yaml 里没有 `hitl:` 段。

### 6.2 "自进化"在默认配置下不存在

- **memory 接线是坏的**：`runner.py:472-479` 用 `ExperimentMemory(store_dir=...)` 构造，真实签名是 `__init__(self, store, retriever, embed_fn=None)`（`experiment_memory.py:24-32`），`TypeError` 被裸 `except` 吞成 debug；下游还 import 不存在的 `ExperimentOutcome`、调用不存在的 `record_outcome`。测试用的是正确签名所以全绿。`memory/` 自 2026-03-22 后再没动过。即使能跑也是 per-run（`store_dir = run_dir / "experiment_memory"`）。
- **lessons 写完自己读不到**：`runner.py:871-873` 写 `run_dir/evolution/lessons.jsonl`，`_helpers.py:842` 读同一个 `run_dir`，同一次顺序执行里 lessons 最后才写。"Lessons from Prior Runs" 标题在默认配置下永远是空的。
- **跨 run 的唯一通道**是外部 MetaClaw 仓的 `~/.metaclaw/skills/arc-*/SKILL.md`，要 `metaclaw_bridge.enabled=true`（默认 false）；`STAGE_SKILL_MAP` 23 个条目只用于效果反馈记录，不做注入；`skill_effectiveness.jsonl` 只写不读。
- **skills 匹配器失效**：注入 context 是 `f"{stage_name} {topic}"`，18 个调用点没一个传 topic；`_tokenize` 的正则 `[a-z0-9_]+` 把下划线算进 token，`"hypothesis_gen"` 是一个 token，跟 trigger-keywords 分出来的 `"hypothesis"` 永远交不上（`skills/matcher.py:13-15,56-92`）。真正进 prompt 的只有 `evolution.py:490-506` 对 `~/.metaclaw/skills/arc-*` 前 5 个 `SKILL.md` 的无差别全文灌入。SKILL.md 格式与 Claude Code 原生同构，`.claude/skills/` 下 9 个里 6 个与 `researchclaw/skills/builtin/` 重复。

### 6.3 debate 与 tournament：质量最高但只接了一处

`pipeline/debate.py`（292 行，2026-08-18 单次提交）是真辩论：角色 round-robin 绑不同模型 → 开场 → rebuttal 轮 → 独立 judge 打分与更强的 synthesizer 分离（反自我偏好）→ 重试与空内容护栏 → 消融开关 → 每轮落盘记 provenance。`docs/debate_engine.md` 说接入 Stage 8 / 14 / 18，代码只有 `_synthesis.py:159` 一处（Stage 8）。`tournament.py` best-of-N 同样只在 Stage 8。两者默认关闭。

## 7. 领域适配与 ARC-Bench

### 7.1 领域机制

检测是四级瀑布：强制 profile → 380 行硬编码关键词表（first-match-wins）→ LLM 单选分类（默认 `llm=None` 不走）→ generic 兜底（`domains/detector.py:490-564`）。关键词表里 4 个 domain_id（chemistry_general、biology_general、economics_general、mathematics_general）指向不存在的 profile，命中就掉回 generic。

29 个 profile YAML（共 2426 行）撑起 25 字段的 `DomainProfile`；`PromptAdapter` 是带 abstractmethod 的真 ABC，注册表四级 dispatch。adapter 在 4 个点被调用，全部包在 `try/except Exception + logger.debug` 里。真正做了 stage 级 prompt 分叉的只有 `ml` / `hep_ph` / `biology_metabolic` 三个，其余 26 个 profile 静默回退到 ML 的 prompt bank（`prompts/manager.py:31,121`）。`experiment_schema.py` 的 `UniversalExperimentPlan`（README 说的"领域无关统一实验 schema"）只有测试引用，生产零调用。

**用户自建 profile 的断层**：`deploy.py` 的搜索路径是四级（含 `~/.researchclaw/profiles/`），但 `detector.load_all_profiles()` 只 glob 包内目录（`detector.py:27`）。包外 profile 只拿到 9 个部署默认值，拿不到 5 段 prompt guidance。这个 1014 行的 `deploy.py` 零测试。

**给新工科领域接入的真实成本**：4 处改动（新 profile yaml 62 到 157 行、新 adapter 51 到 154 行、`prompt_adapter.py` 注册表 append、`detector.py` 关键词表 append），后两处必须动主代码。约 250 到 350 行，一两天；做到 hep_ph 那种深度（`prompts/hep.py` 1404 行 + `ColliderAgentSandbox` 656 行）是 2000 行以上。

### 7.2 ARC-Bench：整仓最扎实的部分

55 个 topic（ML 25、HEP 10、量子 10、生物 7、统计 3）共用同一套声明式 manifest YAML：`research_question` / `conditions[{name, description}]` / `baselines[]` / `metrics[{name, direction, description}]`（direction 支持 maximize | minimize | match_reference）/ `datasets[{name, source}]` / `hypotheses[{id, statement, measurable}]` / `compute_requirements{gpu_required, estimated_wall_clock_sec}` / `requirements[{id, type(numeric|discussion|artifact), description, must_pass}]`。一个 sklearn 分类任务和一个 MadGraph 事例生成任务塞进同一个模板（`experiments/arc_bench/config/*/manifests/`）。

rubric 是 PaperBench 式加权递归树：节点 `{id, requirements, judging_note, weight, sub_tasks[], task_category, finegrained_task_category}`，ML 三桶（CD:CE:RA = 25:25:50），其他领域四桶。另有共享的 `_meta_paper_quality.json` 专管论文质量，声明为人工评。

**manifest 与流水线的接线是一条真内环**：`prepare_run.py` 把 manifest 物化成 `stage-09/exp_plan.yaml` + `stage-09/requirements.json` 等中间产物，从 stage 10 注入；跑完由 `requirements_judge.py` 用 LLM 逐条审 `must_pass`，verdict ∈ {proceed, reject, partial}，reject 才写 `REPAIR_PROMPT.md` 触发 stage 12 重跑（`_REQUIREMENTS_MAX_RETRIES = 1`）。这是"先声明验收条件、再由裁决者判、判不过才重试"，比"把 traceback 拼进下一轮"深一层。但裁决者是 LLM、重试只有 1 次、且只在 agent 模式（collider / biology / stat）走，普通 ML topic 不走。

**判分链路公开 clone 跑不通**：`judge.py:34-36` 顶层 `from paperbench_bridge import build_submission`，该模块在 `experiments/paper_replication/`，被 `.gitignore:131` 挡住、git 历史里从未提交。`RUN_GUIDE` 让跑的 `scripts/sweep.py`、`baseline/setup.sh`、根目录 `requirements.txt` 都不存在；写死 `/playpen2/shiqiu/...` 绝对路径。LLM judge 对未评分叶子默认给 0.5 并计入分母（`judge.py:561-575`），差提交被拉向中位数。`_correctness_signal`（从 `experiment_summary.json` 算零方差、std/mean 比）是不依赖 LLM 的"实验是不是坏的"判据，值得学。

`external/agents/` 不是子模块：Biology-Agent 与 stat_research_agent 是纯 markdown 提示词资产（agents/*.md + skills/*/SKILL.md）；ColliderAgent 只留 pointer README，本体要自己 clone，依赖 FeynRules → MadGraph5 → Pythia8 → Delphes → MadAnalysis5 全套。

## 8. 验证与评测层

### 8.1 真硬的两条

**数字对账**：`VerifiedRegistry`（449 行）从 `experiment_summary.json` + `refinement_log.json` 建"允许出现在论文里的数字"白名单，自动派生 1 到 4 位四舍五入、×100 / ÷100、所有 condition 两两差值与相对提升（`:75-117,217-230`），1% 相对容差。`paper_verifier`（555 行）逐行扫 LaTeX，字符级 skip mask 跳过 cite / ref / equation / verbatim，按 section 分级：results / experiments / ablation 等 strict 区未验证数字 → REJECT，intro / related work → WARN；表格按 caption 区分超参表（豁免）与结果表；`_check_condition_names` 抓论文里出现但没跑过的方法名（`:390-481`）。Stage 17 写论文前还先用 registry 生成好 LaTeX 结果表注入 prompt "copy verbatim, do NOT modify any numbers"（`_paper_writing.py:1892-1921`），generate-then-copy 比 generate-then-check 更根本。

**引用真伪**：`literature/verify.py`（974 行纯 stdlib）五源降级链 DOI → CrossRef（→ DataCite）→ OpenAlex 标题搜 → arXiv ID → Semantic Scholar，Jaccard 三分类（≥ 0.80 VERIFIED、0.50 到 0.80 SUSPICIOUS、< 0.50 HALLUCINATED），磁盘缓存、自适应延迟、全局 300 秒超时。HALLUCINATED 的 `\cite{}` 从正文与 bib 里删。

两条都有几十条零 LLM 的行为测试（`test_rc_sanitization.py` 约 20 条、`test_verified_registry.py` 33 条、`test_rc_citation_verify.py` 49 条）。

### 8.2 但两条都 fail-open

- Stage 22 判 REJECT **不终止**，只把违规数字用词边界正则涂成 `---` 继续导出（`_review_publish.py:2226-2299`）；整段 `verify_paper` 调用包在 `try/except` 里只 `logger.debug`。
- **唯一会终止流水线的硬闸**（Stage 20 "registry 零值且实验失败 → FAILED"，注释点名 issue #165 一个 3.46 秒的"实验"产出造假论文过闸）整段包在 `try: ... except Exception: pass` 里（`_review_publish.py:621-636`）。它唯一的测试搭完 mock 后函数体是 `pass`，最后一行 `assert True  # Placeholder; see integration test below`，承诺的 integration test 不存在（`tests/test_fabrication_guards.py:205-211`）。
- 引用校验断网 / 限流 / 超时全部记 SKIPPED，SKIPPED 被保留且从 `integrity_score` 分母剔掉，分数虚高到 1.0；再叠加"剥离超 50% 就整体回退原 bib"，一次网络抖动足以让全部幻觉引用原样进最终稿（`verify.py:885-974`）。
- 反造假的关键回归证据（4 个真实造假 run）在被 `.gitignore` 挡掉的 `artifacts/` 里，干净 clone 下 4 条测试全 skip。

### 8.3 其余是表演或死代码

- "多 agent 评审"：Stage 18 一次 LLM 调用，prompt 写 "Simulate peer review from at least 3 reviewer perspectives"（`prompts/ml.py:1095-1121`）。默认 `reviewer_model` 未配，评审与判分由写论文的同一个模型完成，只有 `review_provenance.json` 事后留痕。
- 7 维评分 `_review_compiled_pdf` 对 `.tex` 前 12000 字符打分，`overall_score < 5` 的处理只有一行 `logger.warning`。
- 评审回流只有一跳：`reviews.md` 单向进 Stage 19 一次；`GATE_ROLLBACK = {QUALITY_GATE: PAPER_OUTLINE}` 声明了但 `default_rollback_stage` 生产零调用。
- `hitl/claim_verifier.py` 零调用，且数字核对是 `if num_str in data_str` 子串匹配（`'95'` 命中 `'0.9512'`）。`assessor/` 整包（5 维 LLM 打分 + VenueRecommender）零调用，v0.3.2 一次提交后没动过。
- `_generate_neurips_checklist` 把 Claims / Limitations / Ethics / Broader impacts 硬编码答 "Yes"，`has_code` 写死 True（`_helpers.py:1313-1353`）。一个花几千行防数字造假的系统自动产出一份未核实的合规声明。
- README 的 Sentinel"后台质量监控"实际是 `sentinel.sh` 纯 bash 看门狗：心跳 300 秒不更新且 PID 已死就重启。
- 质量门本身是 fail-closed 的（LLM 失败返回 `threshold-2` 分让门判 FAILED），这点做得对。
- AI-slop 检测 `_validate_draft_quality`（`_paper_writing.py:689-1047`）是成体系的纯正则：56 条套话黑名单、weasel word 计数、bullet 密度、section 字数配额、Related Work 比较句比例、Results 段统计量存在性。查出来的问题拼进 Stage 18 / 19 的 prompt 让 LLM 改，"确定性检查 + LLM 执行修复"的分工值得学。
- `figure_agent` 是全仓唯一做出真反馈内环的部件：CodeGen → Render → Critic 最多 3 轮，critic 反馈按 `figure_id` 结构化回传，只重新生成失败的图，critic 三维里两维是确定性的（`figure_agent/orchestrator.py:342-440`）。
- 默认主路径上 18 到 23 阶段的 LLM 调用约 7 到 9 次；数字对账、两遍 sanitizer、写作体检、引用校验、出图全部零 LLM。

## 9. 缺陷清单

全部亲自读到代码证实，本次未执行任何 AutoResearchClaw 代码。前 13 条另经主线程抽查。

| # | 位置 | 现象 | 后果 |
|---|---|---|---|
| 1 | `executor.py:652`、`stages.py:189-361` | 状态机 `advance()` 唯一调用返回值被丢弃，`TRANSITION_MAP` 生产零引用 | 有定义、有 35 个测试、没接线 |
| 2 | `runner.py:463,510,554,584` | import 四个不存在的模块（event_log / cost_tracker / experiment_spec / pitfall_detector），`except` 吞成 debug | 事件日志、成本熔断、spec 校验、陷阱检测永久静默 no-op |
| 3 | `_execution.py:327` vs `sandbox.py:371` | 找 `_project/results.json`，沙盒建的是 `_project_{n}` | harness 的结构化产物从未被读，指标退化成 stdout 正则 |
| 4 | `runner.py:472-479` vs `experiment_memory.py:24-32` | `ExperimentMemory(store_dir=...)` 对不上 `(store, retriever)` 签名 | `TypeError` 被吞，实验记忆永远是 None；单测用正确签名所以全绿 |
| 5 | `experiment/code_agent.py:732-778` | `create_code_agent` / `ClaudeCodeAgent` / `CodexAgent` 零调用零测试 | "委托给 CLI agent"是宣传有、代码在、主路径无 |
| 6 | `_review_publish.py:621-636` | 唯一硬终止闸门包在 `except Exception: pass` 里 | 闸门可能长期失效无人知 |
| 7 | `tests/test_fabrication_guards.py:205-211` | 该闸门的测试是 `pass` + `assert True  # Placeholder` | 无有效测试 |
| 8 | `experiments/arc_bench/scripts/judge.py:34-36`、`.gitignore:131` | 顶层 import 被 gitignore 的 `paperbench_bridge` | ARC-Bench 判分链路公开 clone 跑不通 |
| 9 | `acp_client.py:474-481` | agent 名原样透传 `acpx`，零分支 | "跑在五个 CLI 上"能力全在仓库外 |
| 10 | `_execution.py:802-826` vs `:1110` | `run_summaries` 循环内从不追加 | 第 N 轮看不到前 N-1 轮的指标与 stdout |
| 11 | `pyproject.toml:35` | 打包 `sibyl`、`arc` 两个不存在的目录 | wheel 构建风险 |
| 12 | 仓库根 | 无 `.github/`、无任何 CI；`conftest.py` 零 fixture | 3.9 万行测试没有自动化在跑；README 徽章是静态图片 |
| 13 | `hitl/` | 7835 行里 3855 行只被测试引用 | WebSocket / MCP 适配器无实例化；`branch` CLI 不存在；`escalation` 配置不解析 |
| 14 | `_code_generation.py:775-804` | codegen 全失败时写死 numpy 随机数脚本当实验 | 假数据能过 Stage 12 硬门禁进论文 |
| 15 | `config.py:585` | `ExperimentConfig.mode` 代码默认 `simulated` | 用户 config 漏写 `mode` 就默默跑假数据 |
| 16 | `docker_sandbox.py:407-415`、`entrypoint.sh:41-51` | `setup_only` 网络隔离与 `--user` 非 root 互斥 | 默认档位等价于全联网，只留一行 warning |
| 17 | `factory.py:29-34` | docker daemon 不可用静默降级成宿主机 subprocess | 隔离等级降级不报错 |
| 18 | `ssh_sandbox.py:359-362` vs `entrypoint.sh:13-17` | `use_docker` 路径与自家镜像 ENTRYPOINT 冲突 | 拼出 `python3 -u /workspace/python3 -u main.py`，必挂 |
| 19 | `collider_agent_sandbox.py:599-643` 等三处 | 默认把 skills 复制到用户全局 `~/.claude/skills/`，同名先 `rmtree` | 跑一次实验污染并可能删掉开发者自己的 skill |
| 20 | `smart_pause.py:35-51`、`executor.py:301-322` | 置信度公式代入默认值恒 > 阈值 | SmartPause 默认永不触发 |
| 21 | `executor.py:277` | `CostGuard` 每 stage 新建，阈值通知集重置 | 花过 50% 后每个 stage 都重复触发暂停 |
| 22 | `skills/matcher.py:13-15,56-92`、`_helpers.py:816-863` | 分词把 `hypothesis_gen` 当一个 token，且不传 topic | skill 匹配永远交不上集 |
| 23 | `_experiment_design.py:191-214` | `hardware_profile` 槽写死 "NVIDIA RTX 6000 Ada 49140 MB"，tier1 数据集写死 CIFAR / MNIST | Stage 1 探测的硬件在最需要的阶段被常量顶掉 |
| 24 | `_domain.py:139-190` | prompt bank 选择只返回 `ml` 或 `hep_ph` | `biology.py` 597 行 bank 不可达；26 个 profile 静默用 ML prompt |
| 25 | `detector.py:27` vs `deploy.py:49-104` | detector 只读包内 profile 目录 | 用户自建 profile 拿不到 prompt guidance；`deploy.py` 1014 行零测试 |
| 26 | `detector.py:326-376` | 关键词表 4 个 domain_id 无对应 profile | 化学 / 生物 / 经济 / 数学的通用词掉回 generic |
| 27 | `verify.py:885-974` | 引用校验 SKIPPED 保留且剔出分母；剥离超 50% 整体回退 | 断网等于全过 |
| 28 | `_review_publish.py:2226-2299` | 论文数字 REJECT 只涂黑不终止 | 造假论文带着 `---` 导出 |
| 29 | `_helpers.py:1313-1353` | NeurIPS checklist 自动填 Yes | 自造合规声明 |
| 30 | `hitl/claim_verifier.py:244-266` | 数字核对是子串匹配 | 且零调用 |
| 31 | `_code_generation.py:530-548` | 调不存在的 `adapters.hitl.confirm` | Stage 10 mid-stage HITL 永远走不通 |
| 32 | `_paper_writing.py:2282-2301` | `_re_pw.search(draft_text, _re_pw.DOTALL)` 丢了 pattern | 必抛 `TypeError` 被吞 |
| 33 | `cli.py:1315-1365` | 五处 `--config` 默认 `config.yaml`，`init` 生成的是 `config.arc.yaml` | 官方流程走完这几个命令找不到配置（作者自审 P0 未修） |
| 34 | `dashboard/collector.py:91` vs `runner.py:84` | 读 `stage`，写的是 `last_completed_stage` | 仪表盘 current_stage 恒 0（作者自审 P0 未修） |
| 35 | `docs/DOMAIN_INTEGRATION_GUIDE.md:788-836` | "你不需要改的文件"列了 6 条不存在的路径，验证步骤指向不存在的测试 | 文档描述的是比现状更规整的架构 |

零生产调用的模块（不完全）：`experiment/{metrics,git_manager,code_agent,agentic_sandbox}.py`、`evaluators/convergence.py`、`domains/experiment_schema.py`、`assessor/` 整包、`copilot/` 整包（468）、`collaboration/` 整包（487）、`project/{scheduler,idea_pool}.py`、`hitl/` 一半、`mcp/server.py`（`start()` 只是 `self._running = True`）。

## 10. 对 demo 的意义

### 10.1 借什么、怎么借

| 借的东西 | 从哪儿 | 大约行数 | 抄进内仓时要改 |
|---|---|---|---|
| ARC-Bench 任务契约：manifest + rubric + requirements | `experiments/arc_bench/config/*/manifests/*.yaml`、`rubrics/*.json` | 纯数据格式 | 直接采用为我们的任务规范，比 InternAgent 的 `prompt.json + code/` 高一个维度；判分代码不抄 |
| immutable harness | `experiment/harness_template.py` | 119 | 第一批就抄；把 `results.json` 真读回来 |
| 数字白名单 + 论文校验 | `verified_registry.py` + `paper_verifier.py` + `results_table_builder.py` | 约 1300 | `from_run_dir` 的 `except` 改显式失败；REJECT 改为终止而非涂黑 |
| 引用真伪五源链 | `literature/verify.py` | 974 | SKIPPED 显式向上暴露；去掉"回退原 bib"兜底 |
| 产物契约表 | `contracts.py` | 208 | `output_files` 升级成"文件名 + 可执行校验器"；接线或删掉 `dod` / `max_retries` |
| 磁盘状态约定 + 原子 checkpoint | `runner.py:78-151`、`stage-NN/` 目录 | 约 80 | 跨阶段读取改成显式 producer → consumer 绑定，别用 glob 倒序 |
| HITL 数据模型 + 文件 IPC + 钩子签名 | `hitl/intervention.py`、`file_wait.py`、`config.py` 的 `StagePolicy`、`session.py:169-244`、`executor.py:200-437` | 约 1100 | 三组 stage 常量换成我们的；`CostGuard` 提到 run 级单例 |
| LLM 重试与 fallback | `llm/client.py:274-303,348-456` | 约 200 | 硬编码模型名换成配置 |
| 失败分类器思路 | `experiment_diagnosis.py` | 可裁到 200 | 只保留最常见 5 到 6 类 |
| 写作体检规则 | `_paper_writing.py:689-1047` | 约 350 | 进 CI |
| 辩论引擎 | `pipeline/debate.py` | 292 | 直接用，注意它只有一次提交 |
| docker 三阶段 entrypoint 与 env 白名单 | `docker/entrypoint.sh`、`docker_sandbox.py:364-491` | 约 190 | 网络隔离改在宿主机侧 `docker network disconnect`，别指望容器内非 root 改 iptables |
| `_correctness_signal` | `judge.py:792-865` | 约 70 | LLM 判官旁边的确定性兜底 |

### 10.2 反面清单：抄它的教训

这个仓给我们最大的价值是一份负面清单，每条都能变成我们的一条机器可查的规矩：

1. **"定义了 Protocol"与"Protocol 被接上"是两件事**。`CodeAgentProvider`、`agentic` 模式、`UniversalExperimentPlan`、`ExperimentMemory` 都是前者。规矩：每个抽象合入时必须带一个真实调用点，否则不合。
2. **"配置里写了"与"代码读了"是两件事**。`allowed_imports`、`max_memory_mb`、`cost_tracker`、`inject_at_stages`、`max_parallel_tasks` 都是前者。规矩：每加一个配置项同时加一条断言证明它被读到、改变了行为。
3. **单元测试全绿不等于集成可用**。memory 接线用错签名却测试全绿，因为测试用的是正确签名。规矩：集成点必须有测试。
4. **裸 `except` 是一切静默失效的温床**。四个幽灵模块、硬闸、memory、workshops 全靠它藏了几个月。这正撞我们红线 5。
5. **没有 CI 的"2699 tests passed"是一张图片**。
6. **文档比代码超前会低估工作量**。`DOMAIN_INTEGRATION_GUIDE` 列的 6 条路径不存在，`HITL_GUIDE` 的 branch 命令不存在，`debate_engine.md` 的三处接入只有一处。规矩：调研引用能力描述必须逐条回代码验证。

### 10.3 与另两个候选的关系

- 对 InternAgent：ARC 在每一层都更深，但深在确定性护栏与契约上，不在编排形态上。用户猜的"98% 的 workflow 都是外层 for + 结果塞 prompt"在编排层成立，ARC 没有跳出这个形态，只是在同一形态里堆了十倍的护栏。
- 对 autoresearch：ARC 的 `harness_template.py` 注释直接说灵感来自 autoresearch 的 immutable `prepare.py`，但它比 autoresearch 多走了一步：harness 由框架注入、LLM 改不了。而 autoresearch 的棘轮（git 载体 + 外部硬闸 + 账本）ARC 反而没有：`git_manager` 零调用，Stage 13 靠目录快照。
- 三者各取一半：InternAgent 的任务目录形态与执行循环、autoresearch 的棘轮与实验床契约、ARC 的 manifest / rubric / requirements 契约与验证层部件。

## 11. 可运行性

- 核心依赖 4 个，macOS / Apple Silicon 装得上；`requires-python >= 3.11`。
- 最小跑通一个 ML topic：一把 OpenAI 兼容 key + 本地 venv。**不需要** Docker（另一个 mode）、LaTeX（无 `pdflatex` 只导 `.tex`）、opencode（无则走 CodeAgent）。`researchclaw setup` 只会交互式 `npm i -g opencode-ai@latest`（全局安装），Docker 与 LaTeX 只探测不装。
- 默认 `experiment.mode = "sandbox"` 是宿主机裸 subprocess 跑 LLM 生成的代码，作者自审 P0 至今未修。实验室机器上必须强制 `docker` 模式。
- `pyproject.toml:35` 的幽灵包可能让 `python -m build` 失败，`pip install -e .` 可能绕过，未实测。
- ARC-Bench manifests + rubrics 完整可用（55 + 55 全在），判分链路不可用。

## 12. 未验证与待办

- `claude --max-budget-usd` 是否是真实 flag，未查；若不是，`ClaudeCodeAgent` 一旦接线就会因未知参数失败。
- `acpx` 到底覆盖哪几个 CLI、会话语义一致到什么程度，完全取决于仓库外的项目。
- `_project` vs `_project_{n}` 路径错配是何时引入的回归，`git log -S` 只定位到 v0.3.2 的 squash；docker 分支是否另有回收路径没逐行读 volume 映射。
- SmartPause 永不触发、skills matcher 交不上集，都是代入公式的静态推演，值得各用三行脚本实证。
- hatchling 面对不存在的 package 是报错还是跳过，未跑构建。
- README 与论文报的 ARC-Bench 分数是 full 模式还是 `results_only`（后者把 Code Development 叶子整体排除出分母），两者衡量的东西不同。
- Stage 20 硬闸触发条件是 `len(values)==0 AND _exp_failed`，而 `_exp_failed` 在任何 `stage-14*` 有 `condition_summaries` 时被强制置 False，"有 condition_summaries 但全无数值 metric"能否绕过，只是读代码推断。
- `experiments/arc_bench/baseline/interventions/T01-T25.json` 与 `hitl_ablation` 说明作者真跑过 HITL 消融（H2: copilot > full-auto），结果数据没读。
- 2026-08 之后是停摆还是憋大版本，HuggingFace 的 ARC-Bench 页可能有更近更新。

## 13. 调研方法

- 克隆到外层仓 `vendor/AutoResearchClaw`（gitignore 挡住）。第一次克隆时到 GitHub 只有 12 KB/s，换网络后 240 KB/s，全量克隆约 3 分钟。
- 六个读者并行，范围互不重叠：流水线骨架与契约；实验内环；后端与沙盒；HITL 与自进化；领域适配、ARC-Bench 与可运行性；验证与评测层。每条结论带 `文件:行`，不跑代码、不装依赖，可 grep `tests/` 确认覆盖与是否 mock 了 LLM，不读展示与翻译文件。
- 六份结果合计 177 条发现，本文由此汇总并另抽查 13 条最重的结论（状态机死代码、四个幽灵模块、`results.json` 路径错配、memory 构造签名、CLI 后端零调用、硬闸的 `except: pass` 与 placeholder 测试、`judge.py` 的幽灵依赖、ACP 透传、`run_summaries` 不追加、幽灵打包、无 CI、`hitl/` 行数、harness 接口），全部属实。
- 读者之间有两处口径差异已统一：`hitl/` 顶层 5064 行是不含子目录的数字，含子目录 7835 行；"多 agent 评审"在 `hep.py` / `biology.py` bank 里是否同样是一次调用未核对。
