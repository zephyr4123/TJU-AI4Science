---
title: InternAgent-1.5 代码级深读
subtitle: 流水线层选型 · 上海 AI Lab InternScience
kind: 开源项目选型深读（只读代码，不跑、不装依赖）
date: 2026-09-09
scope: 仓库 https://github.com/InternScience/InternAgent，克隆到 vendor/InternAgent，提交 fa8c3ee（v1.5.0 之后 4 个提交，2026-07-29）；tasks/*/code/ 下的第三方基线代码不深读；文中 文件:行 均相对该仓库根
status: 第一版
---

> **结论先行**：InternAgent 不适合直接当我们五层框架里的"流水线层"底座，适合当**契约来源和零件供应商**。它最值钱的是一套很轻的任务目录契约（`prompt.json` + `code/` + `launcher.sh` + `run_0/final_info.json`）和"跑失败把报错回喂给 coding agent、最多重试五次"的自修复循环骨架；最不值钱的恰恰是我们最看重的"对接 coding agent"这一层——三个后端里只有 `claudecode` 真能跑，`openhands` 从未有过实现，`iflow` 是半成品，而且调用深度只有一层 `subprocess.run`，没有流式、没有超时、没有重试、没有结构化输出。
>
> 怎么读：第 1 节是结论与建议，第 7 节是带 `文件:行` 的缺陷清单，其余各节按"流水线骨架 → 后端层 → 任务契约与可运行性 → mas 子系统"逐层讲解。横向对比与其他候选见同目录的 [README.md](README.md)。

## 1. 结论

**一句话**：科研流程设计想得清楚，工程实现相当粗糙；读它的设计，抄它的契约，不背它的代码。

**能直接借的三块**（按价值排序）：

1. **任务目录契约**。`prompt.json`（任务描述）+ `code/`（基线）+ `launcher.sh`（唯一执行入口）+ `run_0/final_info.json`（基线指标）+ `run_N/`（每轮完整快照）。语言无关、四五个文件就能接一个新任务，和我们"底座 coding agent → 流水线"的分层天然对齐：流水线只管拷目录、起进程、读一个 json。
2. **实验执行循环**。`experiments_utils_claude.py` 里 `run_experiment` + `perform_experiments` 约 350 行：拷快照 → 让 agent 改代码 → `bash launcher.sh` → 失败读 `traceback.log` 截断回喂 → 最多 `MAX_ITERS=5` 次 → 成功进下一个 run。逻辑清晰，可以整段吸收后重写，不必从零设计。
3. **经验记忆闭环**。`TaskMemoryLayer` + `HybridRetriever`（`mas/memory/task_memory.py`、`retriever.py`，约 1400 行）：实验结果打正负标签 → BM25 + faiss 混合检索 → 生成 guidance 塞回下一轮 prompt。只依赖 faiss-cpu、rank_bm25、sentence-transformers，落盘就是 JSON + npy，是这个仓里工程完成度最高的部分，正好对应我们"验证 → 反哺流水线"那一环。

**不该借的**：流水线编排本身（外层 round 循环是 `main()` 里 200 行过程式代码，内层是状态跳转写死在每个 phase 函数末尾的隐式状态机，改顺序等于改源码）；后端层代码（无抽象基类、两份互不相干的 Runner、四套互不一致的指标解析）；`requirements.txt`（是 pip freeze 倒出来的整机环境，装不干净、装上也缺关键包）。

**开箱即坏的六处**（默认配置、照 README 装完就会踩到，详见[第 7 节](#7-缺陷清单)）：`openhands` 后端方法不存在；MCTS 模式入口 `TypeError`；记忆模块因 `chromadb`/`pyclustering` 不在依赖里静默降级；`embedding.model_name` 为空导致 online memory 初始化失败；改进率不分指标方向；README 钦点的首跑任务 `AutoDebug` 没有 `launcher.sh`。六处全是半小时能修的，但仓库里没有任何测试或 CI 会告诉你它们坏了。

**对 demo 的建议**：流水线层自己写（我们的五层划分比它的 `WorkflowState` 清楚），把 InternAgent 当零件供应商——抄任务契约、抄执行循环、抄记忆闭环，Deep Research 需要时当独立进程外挂。底座对接层按我们自己的需要做成 `Runner` 协议（`run(prompt, cwd, timeout) → {events, exit_code, cost}`），用 `claude -p --output-format stream-json` 这类结构化能力取证，每个 CLI 一个 60 到 80 行的适配器。这比在它的 `if/elif` 上打补丁省事，也能把超时、重试、流式取证一次做对。

## 2. 仓库画像

| 项 | 实况 |
|---|---|
| 仓库 | <https://github.com/InternScience/InternAgent>，Apache-2.0，版权归上海人工智能实验室 |
| 版本线 | v0.0.1（2025-10-11，1.0 开源）→ v1.0.1（2026-03-17）→ v1.5.0（2026-05-07）；本次读的是 v1.5.0 之后 4 个提交的 `fa8c3ee`（2026-07-29） |
| 活跃度 | 49 个提交；2026-02 集中提交 24 个，之后每月 1 到 6 个；主力作者一人占 28 个提交 |
| 规模 | 185 MB 克隆；1295 个 py 文件，其中 `internagent/mas/agents/dr_agents/camel/` 是原样 vendor 的 CAMEL 0.2.47（372 个文件、3.4 MB），`tasks/*/code/` 是各任务的第三方基线（含整套 verl） |
| 顶层结构 | `launch_discovery.py`（1105 行，主入口）、`internagent/stage.py`（1356 行，三个阶段类）、`internagent/experiments_utils_{claude,iflow}.py`（后端）、`internagent/mcts_experiments_utils_{claude,iflow}.py`（MCTS 后端）、`internagent/mas/`（多智能体子系统，约 2 万行）、`tasks/`（13 个算法发现任务）、`sci_tasks/`（论文复现，子模块，当前为空） |
| 测试与 CI | 框架代码零测试、零 CI、无 `pyproject.toml`/`setup.py`；`find` 到的 124 个 `test_*.py` 全在 `tasks/AutoTTRL/code/verl/` 下，属于第三方 |
| 依赖声明 | `requirements.txt` 376 行，373 行精确钉死，按字典序排列，含 jupyterlab、Sphinx、paddleocr 整套，是 pip freeze 产物；代码硬 import 的 `chromadb`、`pyclustering` 反而不在里面 |
| 文档 | README 之外有 `docs/{deep_research,memory_module,openrouter,sci_tasks}.md`；`tasks/README.md` 路径全是旧的（指向不存在的 `scripts/run_sci_debug.sh`、`config/debug_config.yaml`） |
| 大文件 | `dr_agents/tools/tool_test_files/` 下 mp4 2.9 MB、mp3 1.6 MB、xlsx 141 KB，与运行无关；抄部件进内仓时只抄源码 |

## 3. 流水线骨架

### 3.1 两层循环

一次 discovery 运行是两层循环，都没有独立的 pipeline 或 DAG 抽象：

```
launch_discovery.py main()                       ← 外层：for round in 1..loop_rounds（默认 10）
  ├─ IdeaGenerator.generate_ideas()              ←   内层：mas 状态机，产出 ideas.json
  │    └─ OrchestrationAgent.run_session()
  │         GENERATING → REFLECTING → EXTERNAL_DATA → EVOLVING → RANKING
  │         → (达到 max_iterations 后) METHOD_DEVELOPMENT → REFLECTING → EXTERNAL_DATA
  │         → REFINING → COMPLETED
  ├─ ExperimentRunner.run_experiments()          ←   每个 top idea 一个实验目录，线程池并行
  │    └─ 后端 perform_experiments()             ←     run_1..run_N，每 run 内最多 5 次自修复
  ├─ _generate_experiences_for_round()           ←   每轮末：ExperienceGenerator 写 experience_library.json
  └─ (incremental 模式) _update_baseline_for_incremental()  ← 本轮最优覆盖成下一轮基线
```

外层循环在 `launch_discovery.py:798-1000`，是 `main()` 里的一段过程式代码。内层状态跳转写死在各 phase 函数末尾：`orchestration_agent.py:499`（GENERATING→REFLECTING）、`:568`、`:614-624`、`:700`、`:748-758`（RANKING 收尾三分支）、`:856`、`:965`。没有配置化的图，想在阶段之间插我们自己的验证层或评测层，只能改代码。

`loop_mode` 两种：`fresh` 每轮都从 `args.task_dir` 起步；`incremental`（默认）第二轮起 `base_code_dir` 指向上一轮最优实验目录，且只在本轮最优 `overall_improvement_rate` 超过历史最优时才更新基线（`launch_discovery.py:977-998`）。更新时会**就地覆盖** results 下那个实验目录的 `code/` 与 `run_0/`（`launch_discovery.py:157-246`），历史产物因此被污染，多轮之后复现不了某一轮的原始状态。

### 3.2 内层状态机的实际语义

- `top_ideas` 是 ranking agent 返回的 `top_hypotheses` id 列表（`orchestration_agent.py:748-749`）；配置里的 `workflow.top_ideas_count=5` 只是传给 agent 的提示，代码没有二次截断，实际数量由 LLM 输出决定。
- `top_ideas_evo=true` 时 `iteration>0` 只演化 top ideas（`:1020-1025`）；EVOLVING 每个 idea 生成 `evolution_count=2` 个子 idea，带 `parent_id`，形成树。
- "人在环"的 `AWAITING_FEEDBACK` 状态默认被 `--offline_feedback=config/feedback_global.json` 顶掉，即一段固定的批评话术（`config/feedback_global.json:1-4`）；不是真的人工反馈。
- `_extract_feedback_content` 号称取最近一条反馈，实现是 `sorted(..., reverse=True)[-1]`，取的是最旧一条（`orchestration_agent.py:1040-1049`）。多轮反馈场景下永远拿第一轮的。

### 3.3 数据契约

这是全仓最值得抄的部分。

**任务目录**（输入）：

```
tasks/<Name>/
├── prompt.json            代码真正读的只有 5 个字段，见 5.1
├── code/                  基线代码；可预置 code_summary.json 省一次 LLM 全仓扫描
│   └── experiment.py
├── launcher.sh            唯一执行入口；claudecode 后端以 cwd=run_N 无参执行 bash launcher.sh
└── run_0/
    ├── code/              基线代码快照（setup 时由 code/ 拷入）
    └── final_info.json    基线指标，改进率的分母
```

**结果目录**（输出，`launch_discovery.py:642-673`、`stage.py:350-382`）：

```
results/<task>/<YYYYmmdd_HHMMSS>_launch/
├── prompt.json                    每轮可能被 PromptEvolver 就地覆盖
├── prompt_backup_round<N>.json    覆盖前的备份
├── prompt_candidates.json
├── discovery_summary.json         跨轮汇总，也是 --resume 的唯一状态源
└── session_<epoch>/
    ├── ideas.json                 只落 refined_method_details 五字段
    ├── traj.json                  mas 轨迹（落盘路径与 --output_dir 不一致，见 7）
    └── <ts>_<idea_name>/          每个 idea 一个实验目录 = 任务目录整份 copytree
        ├── notes.txt              Name/Title/Description/Method 四行 + 各 run 摘要
        ├── log.txt
        ├── run_0/                 基线
        └── run_1..run_N/          每 run 是主目录的完整快照，内含 final_info.json / traceback.log
results/<task>/experience_library.json   跨 launch 共享的经验库
```

**`ideas.json`**：落盘的不是完整 idea，只有 `refined_method_details` 的 `{name, title, description, statement, method}` 五字段（`launch_discovery.py:867-869`，schema 在 `refinement_agent.py:92-123`）；内存里传给 `ExperimentRunner` 的却是含 `id/score/rationale/critiques/evidence/references/parent_id` 的完整 dict（`data_type.py:52-73`）。所以用 `--skip_idea_generation --idea_path` 回喂时信息会降级。

**`final_info.json`**：规范格式是两层嵌套、叶子必须是标量：

```json
{"cifar100": {"means": {"best_acc": 0.812, "epoch": 1}}}
```

`stage.py:629-643` 的解析只取第一个值为 dict 的顶层键，有 `means` 取 `means`，否则整个值当指标；整块 `except Exception: pass`。sci 任务写成 `{"sci_task": {"means": {"total_score": ..., "item_i_score": ...}}}`。

**`discovery_summary.json`**（`launch_discovery.py:1048-1085`）：`timestamp/launch_id/task/task_dir/task_type/mode/output_dir/loop_rounds/loop_mode/sessions/total_ideas/total_successful/total_failed/rounds[]`，每轮 `{round, session_id, results[], successful, failed}`，每条结果 `{idea_name, success, gpu_ids, folder_name, code_path, performance}`；incremental 额外 `incremental_mode.{final_best_code_path, final_best_performance}`。`--resume` 优先读它，读不到才 glob `session_*` 数轮数；粒度是整轮，一轮中途挂只能整轮重跑。

### 3.4 记忆回流的三条链路及各自的断点

| 链路 | 写者 / 时机 | 读者 / 时机 | 默认配置下的状态 |
|---|---|---|---|
| 经验库 `experience_library.json` | `ExperienceGenerator`，每轮末（`launch_discovery.py:968-971`、`long_memory.py:1171-1306`） | 下一轮 `PromptEvolver` | 需要 `chromadb`、`pyclustering`，两者都不在 `requirements.txt`，`ImportError` 被 `try/except` 吞成一行 warning（`stage.py:23-31`、`launch_discovery.py:22-29`），**静默失效** |
| prompt 进化 | `IdeaGenerator.load_task`，`round>1`（`stage.py:190-256`） | 同上，就地覆盖 `prompt.json` | 同上 |
| IdeaGraph 聚类去重 | `_load_historical_ideas_to_graph` glob 磁盘上的 `ideas.json`（`stage.py:102-176`） | 本轮 exploration_score | 本轮 `ideas.json` 在 `generate_ideas()` 返回后才落盘，所以第 N 轮的 idea 到 N+1 轮才进图，**落后一轮**；`add_ideas_batch` 无人调用 |
| online memory（`TaskMemoryLayer`） | 实验成功后立刻写 `./config/mem_store/<task>/`（`stage.py:479-495`） | generation / evolution agent 的 `use_memory` 与 `filter_failed_ideas` | `embedding.model_name` 默认空串，`SentenceTransformer("")` 构造失败被捕获后只 log，`memory_saver` 保持 `None`，**开箱即断**（`config/default_config.yaml:43-50`、`embedding_models.py:57-59`） |

四条里三条"坏了不吭声"。拿它做"带记忆的自动科研"演示，很可能演示的是一个没有记忆的版本。

### 3.5 三个阶段类的可拆性

| 类 | 依赖 `args` 的属性 | 可拆性 |
|---|---|---|
| `ReportWriter`（`stage.py:1225-1355`） | 存了 `self.args` 但全类不读 | 完全独立，剪下来就能用 |
| `ExperimentRunner`（`stage.py:465-1223`） | `exp_backend`、`task_dir`、`task_name`、`task_type` 四个 | 依赖面窄，是三者里最现实的复用点 |
| `IdeaGenerator`（`stage.py:65-388`） | 九个属性，且在 `__init__` 里把 `exp_backend` 塞进 mas 的 config | 同时干 prompt 进化、IdeaGraph 维护、traj 拷贝、PDF 可视化四件事，最难拆 |

另外 `AgentFactory._agent_cache` 是类属性（进程级共享），缓存 key 读的是不存在的 `config['model']['provider']`，永远退化成 `"<type>_default"`（`agent_factory.py:96-121`）；同进程用不同配置创建同类型 agent 会静默拿到旧实例。`SurveyAgent.execute` 还会永久删掉自己的 `web_search` 源（`survey_agent.py:116-121`），第二轮起 web 搜索静默停掉。

## 4. coding agent 后端层

这一层是我们选它的理由，也是读完落差最大的一层。

### 4.1 三个后端实况

| `--exp_backend` | 实况 | 证据 |
|---|---|---|
| `openhands` | **从未有过实现**。argparse 允许选、`launch_discovery.py:914-923` 还专门为它读配置，但 `run_openhands_experiment` 全仓无定义。上游历史：1.0 开源版（`25fa46c`）里这个方法整段被注释掉，1.5（`e341f8f`）把注释也删了，只留调用点。选它在 `stage.py:1069` 抛 `AttributeError`，被 `:1143` 的 `except Exception` 吞成一行"实验失败" | `stage.py:1068-1075`、`git log -S` |
| `claudecode` | 唯一真跑过的路。`subprocess.run(['claude', '--permission-mode', 'acceptEdits', '--model', M, prompt], cwd=实验目录, capture_output=True)` | `experiments_utils_claude.py:121-127` |
| `iflow` | 半成品。`--model` 被注释在同一行行尾，model 参数是死的；`gpu_ids` 收了只打一行日志就丢；`proxy_settings` 为 None 时硬编码兜底 `http://127.0.0.1:7890` 写进子进程 env，而 `stage.py` 四个调用点都不传 proxy，所以每次都强制走本机 7890；`max_runs` 判定用的是模块常量 `MAX_RUNS=5` 而非传入参数；遇到扁平 `final_info.json`（如 `AutoDebug`）直接 `TypeError` | `experiments_utils_iflow.py:89-92,118-124,344-345,399-401` |

`tasks/README.md:84` 还列了第四个后端 `aider`，argparse 里没有。仓库里 80 处 "aider"、56 处 "cline"、22 处 "openhands" 字符串命中，绝大多数在 `tasks/AutoTTRL/code/verl/` 的训练数据里，不是集成代码。

### 4.2 claudecode 到底怎么调

`experiments_utils_claude.py:87-145`：

- 没有 `-p/--print`、没有 `--output-format`、没有 `--allowedTools`。本机 `claude --help` 明确写着"starts an interactive session by default, use -p/--print for non-interactive"。在 `capture_output=True` 的非 TTY 子进程里它究竟走哪种模式，本次没有实测（见[第 9 节](#9-未验证与待办)），这是复用前必须第一个验证的事。
- `capture_output=True` 意味着全缓冲、零流式：几十分钟的实验期间外部看不到任何中间输出，`stage.py:848-875` 的进度监视只能看 `log.txt` 文件大小涨没涨。
- `subprocess.run` 没有 `timeout`。coding agent 卡住就永久挂住；实验本体的超时靠 `config experiment.run_timeout`，而**两份 shipped config 里都没有这个键**，所以默认也是无超时。
- 没有重试，没有退出码语义化，拿不到工具调用轨迹和 token 成本。
- `--permission-mode acceptEdits` 只自动放行文件编辑；agent 跑脚本、装依赖会不会被拦，代码里没有任何证据。实验目录是任务目录的整份 copytree（sci 任务还 symlink 了原始 `data/`），没有容器或沙箱。

### 4.3 成功 / 失败怎么判

- claude 侧纯看 `launcher.sh` 的 returncode（`:272-298`）；iflow 侧先看 `run_N/final_info.json` 存不存在，存在就判成功、不看 returncode（`iflow.py:236-262`）。两边逻辑相反。
- agent 输出里被当判据的字符串只有两条：`"litellm.BadRequestError" in output → return False`，`"ALL_COMPLETED" in output → break`（`claude.py:399-404`）。而 `ALL_COMPLETED` 这个词本身就写在发给 agent 的 prompt 里（`prompts.py:90,149,176`），agent 复述一句指令就会误判"全部完成"并提前 `return True`，且这个 break 在第一轮、任何实验还没跑时就可能触发。这是"假成功"，会直接污染评测层的成功率统计。
- MCTS 路径一次都没检查这两个字符串。

### 4.4 契约自相矛盾处

- claude 后端在 `run_N` 目录内无参执行 `bash launcher.sh`（`claude.py:201-224`）；iflow 后端在父目录执行 `bash launcher.sh run_N`（`iflow.py:194-210`）。同一个任务目录不可能同时满足两个后端。
- 共用的 `NEXT_EXPERIMENT_PROMPT` 告诉 agent "We will run `bash launcher.sh {NEXT_RUN_NUM}`"（`prompts.py:87`），只对 iflow 成立；MCTS 的 prompt 又说 `bash launcher.sh .`（`prompts.py:13,166`），对谁都不成立。给 agent 的执行契约描述与实际命令不符。
- 普通模式的 coder prompt `CODER_PROMPT_OPENHANDS`（`prompts.py:26-47`）通篇没提 `final_info.json`；"实验要写出 `final_info.json`"这条契约完全隐含在基线代码里。只有 MCTS 的 prompt 显式约束了 schema。

### 4.5 重复度与抽象缺失

- `ClaudeCodeRunner` 与 `IFlowCodeRunner` 是两个互不相干的 plain class，没有共同父类、ABC、Protocol 或注册表；后端选择是 `stage.py:1068-1075` 的三分支 `if/elif` 字符串比较。
- `experiments_utils_claude.py`（576 行）与 `_iflow.py`（403 行）：`extract_idea_info`、`info_traceback` 逐字节相同；iflow 404 行里 277 行在 claude 文件里逐字出现。
- `mcts_experiments_utils_claude.py`（762 行）与 `_iflow.py`（731 行）：行级相同 700 行（92%），差异只有类名替换、默认模型名、工作区是否拆 `code/`。整棵 MCTS 树、UCT、reward、backprop 复制了两份。
- `extract_idea_info` 全仓四份副本（`stage.py:545-580`、`:1233-1271`、两个 utils 文件）；`_load_config` 两份逐字复制，连同错误的兜底路径 `config/default.yaml`（实际只有 `default_config.yaml`）一起复制。

### 4.6 新增一个后端要动哪里

照现有范式加 codex / opencode / gemini CLI，必改 6 处：`launch_discovery.py:414` choices；`stage.py:15-18` import；`stage.py:1068-1075` dispatch 加 `elif`；`stage.py` 新写一个 `run_<x>_experiment`（照抄 `:883-975` 的 93 行）；新建 `experiments_utils_<x>.py` 约 400 行（其中真正要写的是 `Runner.run` 45 行 + `run_experiment` 160 行 + `perform_experiments` 95 行）；`config/default_config.yaml:180-187`。要 MCTS 再复制一份 730 行。

如果先抽一层 `Runner` 接口，新后端可以压到 60 到 80 行——但那已经是在写我们自己的后端层了。

### 4.7 MCTS 模式

`experiment.use_mcts=true` 这条路当前跑不起来：`stage.py:926-932` 传了 `gpu_ids`、`log_file` 两个关键字参数，`mcts_experiments_utils_claude.py:709-714` 的签名只有 `(idea, folder_name, proxy_settings, model)`，必抛 `TypeError`，被 `stage.py:970` 吞成一行 error。默认 `false`，所以没人踩到。

机制本身：每个节点一个 `node_<uuid>` 工作区、从父节点全量复制代码；root 下最多 2 个 draft、每个非 root 节点最多 3 个 improve、总迭代 30；奖励只有三档（跑挂 −1、跑通 +1、刷新全局最优再 +1），指标提升多少不影响奖励；MCTS 下 GPU 分配完全失效（不传 `gpu_ids`）。值得借鉴的只有 `mcts_node.py:19-74` 的 `MetricValue`——按 `maximize` 翻转比较语义，约 60 行。

## 5. 任务契约与可运行性

### 5.1 `prompt.json` 真正被读的字段

用 grep 逐字段核对代码（`stage.py:257-267`）：只读 `task_description`（必填）、`domain`（必填）、`background`（可选，但默认 `agents.dr.enabled=true` 时会被 DR 生成的背景整体覆盖，`orchestration_agent.py:120-130`）、`constraints`（可选 list）、`fix_direction`（仅 prompt 进化用）。README 和样例里的 `system/goal/dataset/baseline/metrics/task_name/description` 在 `internagent/` 全仓零读取点，是装饰。`AutoDebug/prompt.json` 里那组 `metrics.primary/optimization_direction` 没人消费。

仓库自带的 `tasks/AutoDrug/prompt.json` 只有 `{system, task_description, tools}`，缺 `domain`，按现有代码 `load_task` 直接 `ValueError`。`AutoDebug/prompt_backup.json`（演化前的原始版）没有 `task_description`，也跑不了；能跑的那份是被 `PromptEvolver` 写过一遍才补上的。

### 5.2 执行与指标的隐性契约

- `launcher.sh`：唯一入口，pipeline 不关心 `experiment.py` 叫什么。
- `final_info.json`：两层 `{"<数据集>": {"means": {"<指标>": 标量}}}`，写到 `run_N/`，即实验脚本里的 `os.path.dirname(os.path.dirname(__file__))`。
- `traceback.log`：失败时 `run_experiment` 去 `run_N/traceback.log` 读回栈，正则抽 `File "...", line N` 与 `\w*Error\w*` 拼成修错 prompt（`claude.py:249-277`）；没有这个文件只能给一句 "Experiment failed with return code N"。README 没写，但直接决定 debug 循环的质量。
- `code_summary.json`：`ref_code_path` 是目录且该文件不存在时，由 codeview 自动生成（claudecode 后端调 CLI，其他后端调 LLM API，`generation_agent.py:856-903`）；`GenerationAgent` 只消费 `summary` 与 `key_files[*].path/description`。

### 5.3 仓库自带任务的一致性

| 任务 | `launcher.sh` | `final_info.json` 格式 | 写 `traceback.log` | 与 claudecode 契约 |
|---|---|---|---|---|
| `AutoDebug`（README 钦点首跑） | **没有** | 扁平 `{mse, r2, mae, training_time, config:{…}}` | 否（无 try/except） | 不符：无入口；解析会把 `config` 里的超参当指标 |
| `AutoCls2D` | 有 | 规范两层 | 是 | 符合（`--out_dir` 被硬覆盖成 `run_N`，参数是死的） |
| `AutoMem` | 有 | 三层（指标下再套 mean/std/median） | 是 | 入口符合；指标解析返回一堆 dict，`float()` 全部 `TypeError` 被吞，改进率恒 0 |
| `AutoChem` | 有，`deepspeed experiment.py --out_dir $1`（旧扁平布局遗留，根目录并没有 `experiment.py`） | 规范两层 | 是 | 不符：无参调用 `$1` 为空，`os.makedirs('')` 抛异常 |

四个里只有两个真正对得上。"开箱可跑"不可信，任何"某功能能用"的结论都得我们自己复现。

### 5.4 指标比较的三个缺陷

1. **不看优化方向**。`_calculate_experiment_performance`（`stage.py:606-628`）逐指标算 `(current − baseline) / |baseline| × 100` 再取算术平均，没有任何 maximize/minimize 判断；`_find_best_experiment_result` 直接取最大者当下一轮基线。工科仿真任务的指标绝大多数越小越好（误差、残差、能耗、时间），直接用它的 incremental 循环会把越跑越差的方向当最优往下传。方向表 `tasks/metric_config.json` 存在，但只被默认关闭的 MCTS 分支读。
2. **解析静默出错**。`_extract_metrics_from_final_info` 整块 `except: pass`，格式不符不会报错，只会安静得到 0% 改进。
3. **基线更新取"最后一个"而非"最好一个"**。`_update_baseline_for_incremental`（`launch_discovery.py:170-190`）注释直说 "assumed to be the best"，循环里每遇到一个有 `final_info.json` 的 run 就覆盖；且 `sorted(glob('run_[1-9]*'))` 是字典序，`run_10` 排在 `run_2` 前，`max_runs > 9` 时取错。

### 5.5 依赖与安装

从 `internagent.stage` 静态追 import 图（49 个模块），无条件导入的第三方包 21 个：`yaml numpy requests httpx bs4 sklearn tqdm rich networkx faiss rank_bm25 pdfplumber pypdf graphviz dataclasses_json easydict fastmcp rdkit molbloom chromadb pyclustering`，另有 `model_factory` 动态加载的 `openai`、`json_repair`。

- `torch`：**不是流水线必需**。`launch_discovery.py:13` 有一句无条件 `import torch`，全文件再无第二处引用；GPU 探测在 `stage.py:518-527` 且有 `ImportError` 保护。删掉那一行就不需要 torch。
- `transformers`：`internagent/`（除 dr_agents）零引用，只是 sentence-transformers 的传递依赖。
- `chromadb`、`pyclustering`：`long_memory.py:19-22` 模块级硬 import，`requirements.txt` 里没有。
- macOS / Apple Silicon：`requirements.txt` 含 15 个 `nvidia-*-cu12` 与 `triton==3.4.0`，只发 manylinux x86_64 wheel，整份装不下来。
- 版本冲突：根 `requirements.txt` 钉 `openai==2.5.0`、`anthropic==0.69.0`，`dr_agents/requirements.txt` 钉 `openai==1.98.0`、`anthropic==0.60.0`，还钉了早已废弃的 `asyncio==3.4.3`（装上会遮蔽标准库）。两份不可能装进同一个 venv。
- Python 版本：唯一声明是 README 的 `conda create -n InternAgent python=3.11`。
- `literature_search.py:19-31` 在 import 阶段用 `subprocess` 调 pip 装 `aiohttp`、`beautifulsoup4`，副作用式安装。

### 5.6 最小跑通 `AutoDebug` 需要什么

- 两把 key：`OPENAI_API_KEY`（+ `OPENAI_API_BASE_URL`）供 mas 全部 agent（默认 provider `openai`、模型 `gpt-4o`）；`ANTHROPIC_API_KEY` 供实验后端。后端不是 SDK，是 subprocess 调本机 `claude` 可执行文件，所以 PATH 里必须有 claude CLI。
- 关 memory 与 DR 没有 CLI 开关，只能改 yaml：`agents.dr.enabled=false`、`memory.task_memory.enabled=false`、`memory.online_memory.enabled=false`、`memory.long_memory.enabled=false`。但 `long_memory.enabled` 只有 `launch_discovery.py` 判，`stage.py` 初始化 IdeaGraph 只看 `LONG_MEMORY_AVAILABLE`，覆盖不完整。
- 建议同时 `agents.generation.do_survey=false`（默认 true，会去打 arxiv / crossref / Serper）、`workflow.loop_rounds=1`。
- 默认配置不依赖内网服务：`kg_papers` 的 `172.30.35.89` 写在 config 里但没列进 `scholar.sources`；MCP remote 全部注释。唯一硬编码的本机地址是 iflow 的 `127.0.0.1:7890`。
- 无 GPU 时并行度被静默压成 1：`GPUAllocator` 在 `total_gpus==0` 时 semaphore 置 1（`stage.py:401-412`），线程池却按配置开 4 个 worker，日志还打印 "Actual max parallel: 4"。纯 API 驱动的 demo 机上会比预期慢 4 倍且不报错。

### 5.7 给一个新工科任务要准备什么

按它的契约接一个力学 / 材料仿真任务，必备 5 项：`prompt.json`（`task_description` + `domain`，`constraints` 用 list）、`code/`（仿真基线，可选 `code_summary.json`）、`launcher.sh`（如 `python code/experiment.py`）、`run_0/final_info.json`（如 `{"beam_fem": {"means": {"rmse": 0.031, "runtime_s": 12.4}}}`）、实验脚本把 `final_info.json` 写到上两级目录并在 `except` 里写 `traceback.log`。

纯契约工作量半天到一天。真正的成本在三处：指标方向必须绕过它的 bug（改代码，或把误差取负伪装成越大越好）；仿真运行时长与资源——pipeline 只有 `run_timeout` 与 `CUDA_VISIBLE_DEVICES` 级别的粗调度，没有队列、没有 MPS/ROCm、没有显存隔离，求解器若依赖商业软件或 MPI 得自己在 `launcher.sh` 里包；基线代码要先整理成"单文件 + 明确 argparse + 快速小规模模式"，否则 agent 每轮改完跑不动，全耗在 debug 循环里。

## 6. mas 子系统

约 2 万行（不含 vendored CAMEL）。顶层 docstring 写得极详尽，底下有实打实跑不通的分支。

### 6.1 agent 层

- `AgentFactory` 注册 11 个：generation / reflection / evolution / method_development / refinement / ranking / survey / scholar / dr / prompt_evolver / experience（`agent_factory.py:41-53`）。discovery 用 9 个（dr → survey → generation → reflection → scholar → evolution → ranking → method_development → refinement）；QA 只用 `DRAgent`。
- `BaseAgent` 契约干净：`async execute(context, params) → Dict`；`_call_model` 带 `max_retries=10` 的重试；`_call_model_with_tools` 实现 OpenAI 风格多轮 tool loop（`base_agent.py:331-480`），是可以直接当"skills + 工具层"参考实现的一百多行。它自带的 `run_with_timing` 既无人调用又调不通（单参调用双参 `execute`，读从未赋值的 `agent_type`）。
- `GenerationAgent` 与 `EvolutionAgent` 之间 200 多行逐字重复（`generation_agent.py:131-355` vs `evolution_agent.py:93-325`）。
- `DRAgent.execute` 把所有异常吞成一段自然语言兜底字符串返回（`dr_agent.py:186-189`），下游分不清"DR 真产出了 background"和"DR 挂了"。
- 死代码：`codeview_agent.py` 没有 `CodeViewAgent` 类；`tools/code_search.py` 零 importer；`demo.py` 直接返回协程对象再 `len()`，官方示例跑不起来。

### 6.2 模型层

- 4 个 provider：`openai`、`openrouter`（继承 openai）、`interns1`、`dsr1`。`BaseModel` 把 `generate_with_messages` 声明为抽象方法，只有 `OpenAIModel` 实现了；`S1Model`、`R1Model` 一实例化就 `TypeError`（`base_model.py:135-162`、`s1_model.py`、`r1_model.py`）。**接国产模型走 `interns1` 这条路当前不通。**
- 好消息：`OpenAIModel` 的 `base_url` 走 config 或 `OPENAI_API_BASE_URL`（`openai_model.py:48-70`），一行配置就能指到 vLLM / DashScope / DeepSeek 这类 OpenAI 兼容端点；按 agent 单独指定模型也支持（`model_factory.py:102-139`）。
- `OpenAIModel.generate_with_json_output` 的 `json_repair` 兜底是死代码：修复成功后仍会落到同缩进的无条件 `raise ValueError`（`openai_model.py:160-174`）；对照 `s1_model.py:176-192` 缩进是对的，是复制粘贴改坏的回归。后果是任何非法 JSON 都走满 10 次重试。
- `dr_agents` 自带第二套完全独立的模型层（deepseek / openai / vllm_qwen / intern_s1 / qwen / gemini，靠模型名前缀 if-else），两套互不相通；vLLM 支持只在 DR 那侧。

### 6.3 工具层

- 两份 `mcp_manager`：老 SDK 版（494 行）已在 `tools/__init__.py:9` 注释掉，生效的是 `mcp_manager_fastmcp.py`（367 行）。
- 默认配置 `sci_tools.local=false`、`remote` 全注释，`ToolRegistry` 是空的，`GenerationAgent` 的 TF-IDF 工具筛选打印 "No related tools found" 后整段 tool loop 空转。真正发网络请求的是 `SurveyAgent` / `ScholarAgent` 直接 new 的 arXiv / CrossRef / Serper 搜索，不经过 registry。
- `sci_tools` 只有 chem 一个子域两个工具（PubChem 查 SMILES、rdkit 改分子）；`search_tools` 三个（`calculate` 用 `eval` 实现、`patent_check` 查 SureChEMBL、`academic_search`）。合计 5 个函数工具。

### 6.4 记忆层

三套互不相干的实现、三套存储、两套 embedding：

| 子系统 | 存储 | embedding | 状态 |
|---|---|---|---|
| `task_memory` + `online_memory` | JSON + npy + faiss 索引，`./config/mem_store/`（运行时状态写进配置目录） | 本地 sentence-transformers，默认 `model_name` 空串 | 开箱即断 |
| `long_memory`（IdeaGraph / PromptEvolver / ExperienceGenerator） | chromadb `PersistentClient` + networkx pickle | 硬编码 OpenAI `text-embedding-3-small` | 依赖缺失，静默降级 |
| `context_memory`（session 轨迹） | 文件系统 `results/<task>/traj_<session>.json` | 无 | 落盘路径与 `--output_dir` 不一致，传了 `--output_dir` 就找不到 |

`docs/memory_module.md` 示例把 `task_memory` 与 `online_memory` 都写成 `enabled=false`，`default_config.yaml` 却都是 `true`——文档和发行配置互相矛盾。

### 6.5 Deep Research

- `dr_agents/camel/` 原样 vendor 了 CAMEL 0.2.47，靠 `sys.path` 注入接入（`dr_agent.py:23-56`），把 `agents / models / tools / utils / workflow` 这些极通用的顶层模块名塞进解释器，与我们自己的包重名时会出难查的导入冲突。
- 耦合面窄且单向，`dr_agents` 内部没有回头 import `internagent.mas` 的地方；QA 模式（`launch_qa.py`）确实能脱离 discovery 独立跑，但 `workflow/main.py:11` 无条件 `import redis`。
- 三段式设计（planner / executor / synthesizer）值得读；整目录 9.4 MB 里 5 MB 是与运行无关的 mp4 / mp3 / xlsx。
- `docs/deep_research.md` 示例写 `DRAgent(model=..., config_path=...)`，实际签名没有 `config_path`，照文档写 `TypeError`。

## 7. 缺陷清单

全部是亲自读到代码证实的；本次没有执行任何 InternAgent 代码。

| # | 位置 | 现象 | 后果 |
|---|---|---|---|
| 1 | `stage.py:1069` | `run_openhands_experiment` 无定义（1.0 里就是注释掉的，1.5 连注释都删了） | 选 `openhands` 必崩，被吞成"实验失败" |
| 2 | `stage.py:926-932` vs `mcts_experiments_utils_claude.py:709-714` | 调用多传 `gpu_ids`、`log_file` | `use_mcts=true` 必 `TypeError`，被吞 |
| 3 | `stage.py:606-628` | 改进率不看 maximize/minimize | loss 类指标越差越"优"，污染 incremental 基线选择 |
| 4 | `stage.py:629-643` | `final_info.json` 解析 `except: pass` | 格式错不报错，静默 0% 改进；`AutoDebug` 会把超参当指标 |
| 5 | `launch_discovery.py:170-190`、`stage.py:594-600` | run 目录字典序排序、取最后而非最优 | `max_runs > 9` 取错 run |
| 6 | `long_memory.py:19-22` vs `requirements.txt` | `chromadb`、`pyclustering` 硬 import 但未声明 | 长期记忆整体静默降级 |
| 7 | `default_config.yaml:43-50`、`embedding_models.py:57-59` | `embedding.model_name` 默认空串 | online memory 初始化失败，只 log |
| 8 | `orchestration_agent.py:1040-1049` | 取"最新反馈"实现为 `sorted(reverse=True)[-1]` | 永远拿最旧一条 |
| 9 | `openai_model.py:160-174` | `json_repair` 成功后仍无条件 `raise` | 非法 JSON 走满 10 次重试 |
| 10 | `base_model.py:135-162`、`s1_model.py`、`r1_model.py` | `interns1`、`dsr1` 未实现抽象方法 | 实例化即 `TypeError`，国产模型 provider 不可用 |
| 11 | `experiments_utils_claude.py:121-127` | `claude` 调用无 `-p`、无 `timeout`、`capture_output` | 可能挂死；无流式；无超时 |
| 12 | `prompts.py:90` + `claude.py:402` | `ALL_COMPLETED` 既在 prompt 里又当完成判据 | agent 复述指令即"假成功" |
| 13 | `experiments_utils_iflow.py:89-92,119,344,399` | 硬编码 7890 代理；`--model` 注释掉；`gpu_ids` 丢弃；`max_runs` 用错常量 | iflow 后端不可信 |
| 14 | `stage.py:401-412` + `:529-543` | 无 GPU 时 semaphore=1 而线程池开 4 | 并行度静默为 1，日志误报 |
| 15 | `memory_manager.py:391-407` vs `launch_discovery.py:645-648` | traj 落盘路径不跟随 `--output_dir` | 轨迹与记忆回流断链，只 warning |
| 16 | `interface.py:421-434`、`long_memory.py:1094-1107` | 兜底配置路径 `config/default.yaml` 不存在 | 兜底形同虚设（两处逐字复制） |
| 17 | `agent_factory.py:96-121` | 缓存 key 读不存在的 `config['model']['provider']` | 同类型 agent 永远拿第一个实例 |
| 18 | `survey_agent.py:116-121` | 缓存单例就地删 `web_search` 源 | 第二轮起 web 搜索静默停 |
| 19 | `launch_discovery.py:841-845` | `--skip_idea_generation` 的 `session_id` 少 `session_` 前缀 | 产出目录与正常路径不同构，resume 与经验生成 glob 对不上 |
| 20 | `data_type.py:128-144`、`memory_manager.py:358-378` | `WorkflowSession` 序列化丢 `method_phase` | 跨进程恢复 session 会走错状态 |
| 21 | `tasks/AutoDebug/` | 无 `launcher.sh`；`AutoDrug/prompt.json` 缺 `domain` | 仓库自带样例并非都验证过 |
| 22 | `stage.py:292-320` | `while self.status != "completed"` 比较的是 dict | 循环只靠 break 退出；无反馈时可能死循环 |
| 23 | `dr_agent.py:186-189`、mas 8 处裸 `except`、7 处 `except: pass` | 异常吞成兜底字符串或 pass | 成功与失败不可区分 |
| 24 | `requirements.txt` | pip freeze 产物；含 15 个 `nvidia-*` 与 `triton` | macOS 装不下；装上也缺关键包 |

## 8. 对 demo 的意义

### 8.1 借什么、怎么借

| 借的东西 | 从哪儿 | 怎么用 | 抄进内仓时要改 |
|---|---|---|---|
| 任务目录契约 | `tasks/AutoCls2D/`、`stage.py:784-832` | 原样采用，写进我们的任务规范 | 补上 `optimization_direction` 字段并真正读它；`final_info.json` 强 schema 校验 |
| 实验执行循环 | `experiments_utils_claude.py:147-433` | 读懂后重写，不复制 | 加 `timeout`、结构化事件流、去掉字符串判据 |
| coder prompt 的硬约束 | `prompts.py:26-47` | 措辞直接抄（不许改 `launcher.sh`、argparse 改动必须设成 default、不许自建 run 目录） | 补 `final_info.json` 的 schema 要求 |
| 经验记忆闭环 | `task_memory.py`、`retriever.py`、`memory_retrieval.py` | 约 1400 行可整段吸收 | 所有 `except` 兜底改成向上抛 |
| agent 契约 | `base_agent.py:110-152,259-480` | 当"skills + 工具层"参考实现 | 删掉坏死的 `run_with_timing` |
| `MetricValue` | `mcts_node.py:19-74` | 按 maximize 翻转比较，约 60 行 | 无 |
| sci 任务的 checklist + LLM-judge | `sci_eval.py`、`docs/sci_tasks.md` | 思路搬到评测层，自己实现 | 依赖的 ResearchClawBench 子模块要另拉 |
| Deep Research | `dr_agents/` 整目录 | 需要时当独立进程外挂，独立 venv | 不塞进主 `sys.path`；不带 `tool_test_files` |

### 8.2 不借什么

- 流水线编排（外层 for + 内层隐式状态机）。
- 后端层代码（无抽象、双份 Runner、四套指标解析）。
- MCTS 模式（入口就坏、奖励三档、每节点全量复制目录、GPU 失效）。
- `requirements.txt`。
- 三套记忆存储里的 chromadb 那套（硬编码 OpenAI embedding、依赖未声明）。

### 8.3 若仍要直接跑它做成本对比

调研路线图里初级版要"同一个小任务分别跑 AutoResearchClaw 和 InternAgent-1.5"，那就得让它跑起来。最短路径：

1. 用我们自己的 venv，按 5.5 节的 21 个硬依赖 + `openai` + `json_repair` 写精简 requirements，删掉 `launch_discovery.py:13` 的 `import torch`。
2. 先实测 `claude` 无 `-p` 在非 TTY 下的行为；不行就给 `experiments_utils_claude.py:121` 加 `-p`（顺手加 `timeout`）。
3. 关 DR、关三层 memory、关 survey、`loop_rounds=1`、`max_runs=2`。
4. 不用 `AutoDebug`，用 `AutoCls2D` 或自建一个契约完整的小任务（给 `AutoDebug` 补一个 `launcher.sh` 和两层 `final_info.json` 也行）。
5. 改 `stage.py:606-628` 读方向，否则改进率没有意义。

以上五步做完，才能得到一个"InternAgent 到底花多少 token、多少时间跑通一轮"的可信数字。

## 9. 未验证与待办

- **`claude` 无 `-p` 在 `capture_output` 子进程里的行为**：只读到命令行拼装，没有执行。本机 `claude --help` 写默认是交互模式。这条决定 claudecode 后端在当前 CLI 版本上还能不能跑，复用前第一件事实测。
- **`acceptEdits` 权限档下 agent 跑 bash 会不会被拦**：代码里没有 `--allowedTools` 或 `--dangerously-skip-permissions`，若被拦整个自修复循环会静默空转。
- **`AutoDebug` 到底怎么跑通**：是上游忘了提交 `launcher.sh`，还是设计上指望 agent 自己造一个。需要实跑一次。
- **精简依赖在 Apple Silicon 上能否一把装上**：`faiss-cpu==1.12.0`、`rdkit==2025.9.1`、`graphviz==0.21`、`fastmcp==2.12.4`、`molbloom==3.0.0` 的 arm64 wheel 需要在隔离 venv 里 `pip download --no-deps` 验证。
- **sci 模式**：`sci_tasks/` 子模块空、`internagent/rcb_evaluation` 符号链接悬空，`structai`（`requirements.txt:304`）来路不明。这是 1.5 相对 1.0 的主要卖点，也是最接近"科研全自动化"叙事的部分，要另拉 ResearchClawBench 才能评估。
- **单轮 token 成本**：默认 `generation_count=15`、`max_iterations=4`、`loop_rounds=10`、`top_ideas_count=5`，量级不小，本次没有读各 agent 的 prompt，无法估算。
- **`interns1`/`dsr1` 不可实例化**是靠"抽象方法未实现"推出来的，没起解释器验证，高置信但落地前用一行 `python -c` 实测。

## 10. 调研方法

- 克隆到外层仓 `vendor/InternAgent`（被 `.gitignore` 挡住，只读参考），不进版本库。
- 四个读者并行，范围互不重叠：流水线骨架与数据契约；后端层；任务契约与可运行性；mas 子系统。每条结论必须带 `文件:行`，亲自读到才标"已验证"；不跑代码、不装依赖、不深读 `tasks/*/code/`。
- 四份结果合计 138 条发现，本文由此汇总并另抽查了 8 条最重的结论（MCTS 签名、改进率方向、反馈取最旧、`json_repair` 死代码、`ALL_COMPLETED` 双重角色、依赖缺失、`AutoDebug` 无入口、`openhands` 的上游历史），全部属实。
- 所有"跑不起来"的判断都是静态的；第 9 节列了需要动态验证的项。
