# 流水线：能力与实验内环

- 状态：**aligned**（形状）；首版提供哪几个能力，见 Q-1
- 最近变更：2026-09-10
- 依据：[InternAgent 深读](../../research/selection/2026-0909-pipeline-frameworks/internagent.md)、[autoresearch 深读](../../research/selection/2026-0909-pipeline-frameworks/autoresearch.md)、[AutoResearchClaw 深读](../../research/selection/2026-0909-pipeline-frameworks/autoresearchclaw.md)

三个仓的编排形态都是"外层 for + 硬编码状态判断"，差别全在循环之外：用什么承载状态、用什么规则收敛、用什么机器判据卡住造假。我们不写那个 for：**串联能力的是协调层（人 + agent），框架只提供能力**。流水线层因此只有两样东西：**各自可调的能力**和住在其中一个能力里的**实验内环**。

## 1. 能力

框架只认"能力"。每个能力同一个形状：输入契约 → 干活 → 输出契约 → 机器校验。能力之间不传内存对象，只传磁盘文件。能力之间**没有顺序**：协调层决定下一个跑哪个，框架跑完一个就退出并写状态（P-10）。

```
 协调层（人 + agent）
   │ 读 runs/、账本、验证结论，定下一步
   │ 每次调一条 ai4sci 子命令，跑一个能力
   ▼
 ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
 │  文献   │   │  假设   │   │  设计   │   │  实验   │   │  分析   │   │  写作   │   │  验证   │
 └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
      │             │             │             │             │             │             │
  lit.jsonl     hypo.md      plan.yaml     runs/ +       analysis.md    paper.md     report.json
                                           ledger.tsv                                （门）

 上面这个左到右是典型顺序，不是框架里的状态机。回退、跳过、重跑都是协调层的决定。

 每个能力：
 ┌─────────────────────────────────────────────────────────────────┐
 │  读上游能力的产物 ──▶ [干活] ──▶ 写本能力的产物 ──▶ 校验 ──▶ 退出   │
 │                          │                            │          │
 │                    一次执行层调用                schema 对不上      │
 │               （指令 + 任务包 + 领域包               就 FAILED     │
 │                 + 「去读 runs/ ledger git log」）                  │
 └─────────────────────────────────────────────────────────────────┘
```

- **7 个能力是拟定值**，platform 0.2.0 只做设计、实验、分析、验证四个（Q-1）。文献能力可以不跑：用户自带调研包就当它的产物。
- **每个能力一次执行层调用，新会话。** 上下文从磁盘来，不靠上一个能力的会话。这是 P-1 与 P-3 的直接推论。
- **失败处理**：FAILED 就停，不模板兜底、不静默跳过（P-7）。重试是显式配置，默认 0。
- **回退**：框架不判断"要不要回到设计"，协调层看了分析结论决定。框架只提供留档：重跑一个能力时把旧目录改名成 `_v{n}`，不覆盖。
- **并行**：v0.x 不做。

### 磁盘布局

```
runs/<run_id>/
├── manifest.yaml           任务包 manifest 的快照，协调层拍板后写入，跑起来后不再读任务包
├── checkpoint.json         {run_id, last_iter, best_iter, best_metric, best_commit, stop_reason}；原子写；续跑只看它
├── journal.md              协调层的决定：为什么跑这个能力、看到什么、下一步；指回 issue
├── prompts/                领域包提示的快照，跑起来后不再回头读 domains/
├── work/                   任务包的拷贝，独立 git 仓：分支 tip = best，refs/attempts/* 留档被弃的尝试
├── design/    plan.yaml
├── experiment/             实验内环整个住在这里，见第 2 节
│   ├── runs/               每轮一个 run_N/ 快照 + results.json + job.json + .job/ 日志
│   ├── ledger.tsv
│   ├── inflight.json       在飞的那一轮，结账即删
│   └── stop.json           停止原因
├── analysis/  analysis.md
├── writing/   paper.md
└── verify/    report.json
```

跨能力读取按**契约声明的生产者**找文件，不按目录名 glob 倒序（AutoResearchClaw 在这一点上打了四层补丁）。

### 契约

每个能力声明 `inputs`、`outputs`、每个产物的 schema（JSON Schema 或一个 `validate()` 函数）。契约是机器可查的（P-4），契约测试属于框架自己的测试，删掉全部任务包也要过（P-5）。

契约里的值从哪来：**manifest 由协调层（人 + agent）拍板后填写**，方向、预算、统计门、验收判据都在里面；框架只读，并在每轮证明它们没被改（hash、`elapsed_s`）。

## 2. 实验内环（实验能力）

唯一有循环的地方。这个循环是机械的，不做科研判断，所以可以留在框架里。核心是**四个角色分开**：三个仓都把它们混在一起了。

```
                 ┌──────────────────────────────────────────┐
                 │  执行层 coding agent                      │   只干一件事：改 code/
                 │  只能碰 code/ 目录                          │   不跑、不比、不记账、不碰 git
                 └───────────────┬──────────────────────────┘
                                 │ 改动（runner 事后 diff，runner 提交）
                                 ▼
   ┌─────────────────────────────────────────────────────────────────────────┐
   │  runner（框架，确定性代码，零模型）                                         │
   │                                                                          │
   │   ① 拷快照 run_N/   ② 起独立进程跑 launcher   ③ 读 harness 吐出的产物      │
   │   ④ 跟 best 比：看 manifest 的 direction，过统计门                         │
   │   ⑤ 好 → 分支前进 / 差 → git reset 回 best     ⑥ ledger 记一行             │
   │   ⑦ 把「分数、好坏、失败分类」压成一小段文本给执行层，回到顶上                 │
   └─────────────┬────────────────────────┬──────────────────────┬────────────┘
                 │                        │                      │
                 ▼                        ▼                      ▼
   ┌────────────────────┐   ┌──────────────────────┐   ┌──────────────────────┐
   │ harness（任务包带的）│   │ git（状态载体）        │   │ ledger.tsv（账本）    │
   │ 框架注入，只读，    │   │ 分支 tip = 当前最好   │   │ 每轮一行，活过 reset  │
   │ 校验 hash；独立进程 │   │ 失败的 commit 被 reset│   │ 每行能跟 git 对账     │
   │ 只吃产物文件      │   │ 物理销毁              │   │ 不进 git             │
   │ 输出 results.json  │   │                      │   │                      │
   └────────────────────┘   └──────────────────────┘   └──────────────────────┘
```

**一轮的时间线**

```
 执行层改 code/ ──commit──▶ runner 跑（固定预算）──▶ harness: metric=0.9712, elapsed=298s
 ──▶ 比 best 0.9731，方向 minimize，差值超过统计门 ──▶ 留，best=0.9712
 ──▶ ledger +1 行 ──▶ 给执行层：「留了。metric 0.9712 (best)。继续。」
```

**规则**

- 执行层只改 `code/`，`harness` 与 `data/` 只读；runner 事后 diff 与 hash 双重校验，变了判 `readonly_violated` 并回滚。
- runner 是裁判：比较、留或回滚、记账、**git 提交**全由 runner 做，执行层不参与也不需要任何 Bash 权限（P-2）。每个 run 的 `work/` 是独立 git 仓：分支 tip = 当前 best，`refs/attempts/iter-N` 留档每一个被弃或失败的尝试。
- **统计门**：σ 来自 `run_0/sigma.json`（同配置重复 k 次，k 与阈值来自 manifest，默认 k=3、阈值 2σ）；gate = max(accept_sigma × σ, `budget.min_delta`)，差值不过门的判"持平"不留。σ = 0 且没给 min_delta 时 fail-closed：确定性 harness 必须显式声明最小改进量，否则浮点噪声会被当成改进锁进棘轮。这是 autoresearch 跑档里"被 keep 的改进比换种子的波动还小一个量级"的直接教训。
- **固定预算**：墙钟预算写在 manifest，harness 到时自停；超时 1.5 倍必杀，记 timeout。
- **失败分类**：确定性规则，不调模型，按优先级判：`readonly_violated`（diff 或 hash 发现 harness / data 被改）→ `timeout` → `missing_dependency`（stderr 有 ModuleNotFoundError / ImportError）→ `crash`（stderr 有 Python traceback）→ `no_results`（results.json 缺失、不合 schema、或 harness 自报 status ≠ ok；假成功落在这里）→ `nan_metric`。另有两个非失败状态：`noop`（执行层什么都没改，或改动全被 .gitignore 挡住）、`interrupted`（那一轮被杀）。分类结果与修复提示一起给执行层；同类失败连续 3 次判 `unrecoverable`，停。
- **停止条件**：`max_iterations`、连续 `patience` 轮不改进（缺省 5）、`max_cost_usd` 累计用尽、`unrecoverable`；任一触发写 `experiment/stop.json` 并停。已停的 run 再跑一轮都不跑：要不要加预算续命是协调层的决定（P-10）。`--max-iters N` 只是本次调用的配额，用完返回 `batch_exhausted`，不算停止。
- **续跑**：每轮开跑前写 `experiment/inflight.json`，结账后删。`loop resume` 先做 checkpoint、账本、git 三方对账，对不上就 fail-closed；有 in-flight 标记的那一轮记 `interrupted`、在飞的 job 先收尸、候选 commit 进 `refs/attempts/` 再回到 best。`loop run` 撞到 in-flight 标记直接拒绝并指引用 resume。
- **上下文卫生**（P-9）：给执行层的是摘要，不是 stdout；日志落盘。
- **revert-to-best**：下一轮的起点永远是分支 tip，不是上一轮的失败候选。

**账本 `experiment/ledger.tsv`**

```
iter  commit   parent   metric   direction  elapsed_s  seed  status   sigma   harness_sha  note                          cost_usd  executor_s
1     b2c3d4e  a1b2c3d  0.9860   minimize   299.7      42    keep     0.0007  9f3e…        halve batch                   0.11      31.2
2     c3d4e5f  b2c3d4e  0.9863   minimize   300.4      42    discard  0.0007  9f3e…        lr 0.04→0.045 (within noise)  0.09      28.0
3     d4e5f6a  b2c3d4e  -        minimize   12.0       42    crash    0.0007  9f3e…        Traceback: ZeroDivisionError  0.10      25.5
4     -        b2c3d4e  -        minimize   nan        42    noop     0.0007  9f3e…        执行层没改任何文件              0.05      12.0
```

- 基线不占行：它活在 checkpoint 的 `best_metric` / `best_commit` 里，账本从第 1 轮开始。`parent` 是结算前的 best commit，keep 行的 parent 链就是棘轮走向。
- 每行的 `commit` 必须能在 git 里找到（keep 的在分支上，其余有 commit 的在 `refs/attempts/` 下），`ai4sci status` 每次都跑这条对账，对不上退非 0。这是 P-3 的机器判据。
- `sigma` 来自统计门，`harness_sha` 是 `harness/SHA256SUMS` 自身的 sha256，`elapsed_s` 是 compute 测到的墙钟（不采信 harness 自报），`cost_usd` 与 `executor_s` 是执行层那次调用的花费与耗时。拿不到的值写 NaN 或 `-`，绝不写 0。

## 3. 裁判与验证

- **确定性优先**：能用规则判的不用模型。实验能力的 accept / reject 完全确定性；验证能力首批三条零 LLM 判据：报告里的每个数字能回溯到 `results.json`，每条引用在真实学术 API 里存在，每张图由数据文件生成。
- **模型裁判**：需要模型判断的（假设质量、写作质量、manifest 里 `requirements` 的 discussion 类验收），由框架派**一个新会话**，可指定与执行者不同的模型，只给产物不给轨迹，输出结构化 verdict（P-2）。
- **协调层只读判决**：验证结论回到协调层，由它决定接受、重跑还是换方向；协调层不替裁判改判，也不裁自己派出去的活。
- **fail-closed**：门不过就停在门口，不涂黑、不降级（P-7）。

## 4. 人在环

人在协调层的对话里，不是框架的功能。

- 框架不等人：每条子命令跑完一个能力就退出并写状态，需要人判断的事由协调 agent 在对话里问。
- 自主程度是协调 agent 的行为，不是框架的模式：可逆的自己定并记录，贵的带方案来问，拿不准的停。
- 无人值守（挂机过夜）时协调 agent 怎么把问题留给人、人怎么异步回复，是协调层自己的通道问题，platform 0.2.0 不做（Q-7）。

## 5. 框架的驱动面与执行层适配

### 协调层怎么驱动框架

框架是一个 Python 包加一条 `ai4sci` CLI。每条子命令只跑一个能力，跑完写状态、退非零表示 FAILED（P-10）。命令名拟定，开工时以代码为准：

```
ai4sci task validate <dir>            任务包过 schema
ai4sci run new <task> [--run-id]      建 runs/<run_id>/，写 manifest 快照
ai4sci cap <name> <run_id>            跑一个能力：design | analysis | verify …
ai4sci loop run <run_id>              跑实验内环，到停止条件即退
ai4sci loop resume <run_id>           从 checkpoint 与账本续跑
ai4sci status <run_id>                打印状态、账本摘要、验证结论；协调层读盘的入口
```

### 算力适配

harness 在哪跑，和执行层 agent 在哪跑，是两根正交的轴，各自一个端口、各自一组适配器。算力端口是策略模式在 Python 里的形态：一个 `Protocol`，一个后端一个文件，靠名字选择。runner 对算力的全部需求只有三件事：快照放过去、跑 `launcher.sh`、产物拿回来。

```
class Compute(Protocol):
    def put(self, local_dir, remote_dir) -> None          # 快照过去
    def submit(self, remote_dir, cmd, timeout_s) -> Job   # 起任务，立刻返回句柄
    def wait(self, job, timeout_s) -> ExitStatus          # 等结束，超时就 cancel
    def cancel(self, job) -> None                         # 杀干净
    def get(self, remote_dir, local_dir) -> None          # 产物回来

local:  put=cp        submit=Popen 新进程组   cancel=killpg      get=cp
ssh:    put=rsync     submit=ssh nohup+pid    cancel=ssh kill    get=rsync
slurm:  put=rsync     submit=sbatch           cancel=scancel     get=rsync
```

- **submit / wait 而不是阻塞的 run**：句柄落盘到 `run_N/job.json`，`loop resume` 重启后能重新接上还在远端跑的任务或 reap 已死的任务，这是 A-5 续跑的前提。阻塞改异步是最疼的方向，反过来不疼。
- **选择靠名字**：manifest 或命令行 `--compute local` / `ssh:<host>`，名字对不上就报错退出；要的算力不可用绝不静默退回本地（P-7，AutoResearchClaw 的 docker 反例）。
- **凭据在 git 外**：ssh 主机与密钥路径放本地配置文件；远端 venv 是否就绪由 `ai4sci doctor --compute <name>` 事先查，查不过不开跑。
- platform 0.2.0 只写 `local`（Q-6）；Protocol 现在就定，因为调用点已经存在（P-8），ssh 是第二个实现时再校验接口没漏。
- 不做：抽象基类加模板方法、装饰器注册表、工厂套工厂。一个后端一个文件，60 到 80 行，与 `backends/` 同一标准。

### 执行层适配

一个 `Runner` 协议，每个 CLI 一个适配器。形状由 R-1 spike 实测定案（[#20](https://github.com/zephyr4123/TJU-AI4Science/issues/20)，代码 `backends/`）：

```
run(prompt, cwd, timeout_s, allowed_paths)
  -> RunResult{exit_code, events[], changed_files[], cost_usd, duration_s, timed_out, stdout_tail}
```

- **非交互 + 结构化输出**：Claude Code 走 `claude -p ... --output-format stream-json --verbose`，Codex 走 `codex exec --json`（落地前对账）。
- **隔离**（P-11）：`--setting-sources ""` 是承重位，不带它项目 CLAUDE.md 会原样进上下文、plugin / hook / 自定义 agent 全加载；再加 `--strict-mcp-config`（MCP 清零）与 `--disable-slash-commands`（skill 清零）。`--bare` 看似等价但会跳过 keychain 读取导致未登录，不能用。隔离后一句 pong 从 $0.46 降到 $0.05。
- **权限**：`--permission-mode dontAsk` + `--allowedTools` 白名单，只放行 `allowed_paths` 内的 Edit / Write；绝对路径规则必须写 `//`（单个 `/` 被当作项目根相对路径，会把该放行的也拒掉）。dontAsk 下只读 Bash 自动放行、写操作 Bash 被拒；Bash 规则默认一条不给。不用 `--dangerously-skip-permissions` / `bypassPermissions`。这是第一道门，真正的门仍是 runner 事后拿 `changed_files` 判：`code/` 之外有改动就判 crash 回滚（P-7）。
- **changed_files 不采信 CLI 自报**：调用前后对 cwd 做 sha256 快照 diff。事件流里的 `file_path` 实测与 diff 一致，但 Bash 改文件不产生 `file_path`，改完再改回去也看不出来。
- **超时**：`kill_tree` 逐进程组杀。CLI 的 Bash 工具把 shell 起在自己的新进程组里，只 `killpg` CLI 那一组会留下 PPID=1 的孤儿；先趟进程树再叶子组先杀。
- **成本**：只认最终 `result` 事件的 `total_cost_usd` 与 `duration_ms`；超时被杀时 result 不会发出，成本填 NaN 表示未知，绝不填 0。
- **事件流落盘**：完整 stream-json 与 stderr 写 `cwd/.ai4sci/executor-<ts>.jsonl|.stderr.log`，给执行层的只有摘要（P-9）。stdin 给 DEVNULL（否则 CLI 等 3 秒），stdout 与 stderr 各一个线程排空。
- 配置从环境变量读：`AI4SCI_EXECUTOR_MAX_TURNS`（30）、`AI4SCI_EXECUTOR_MAX_BUDGET_USD`（2.0）、`AI4SCI_EXECUTOR_MODEL`（缺省不传）、`AI4SCI_EXECUTOR_TIMEOUT_S`（内环里执行层单次调用的墙钟上限，缺省 900）、`AI4SCI_RUNS_ROOT`（runs 根目录，缺省仓根 `runs/`）。执行层模型该由 manifest 或协调层显式指定，这是待办。
- 任何适配器合入必须带一个真实调用点和一个真 CLI 的冒烟测试（P-8）；冒烟测试 `AI4SCI_LIVE=1` 才跑，CI 不跑。

## 变更记录

| 日期 | 改了什么 | 为什么 | 认可 |
|---|---|---|---|
| 2026-09-10 | 建档。阶段骨架、实验内环四角色、账本、裁判、人在环、Runner 协议 | 三个仓深读的收敛结论；棘轮来自 autoresearch，harness 注入来自 AutoResearchClaw，目录形态来自 InternAgent | 主人 + Claude |
| 2026-09-10 | 第 1、2 节按 R-4 内环实现回写：runner 提交、work/ 独立 git 仓、失败分类改成带优先级的六类 + noop / interrupted、账本加 cost_usd 与 executor_s 且基线不占行、统计门加 min_delta 与 σ=0 fail-closed、停止条件与续跑规则、磁盘布局加 work/ prompts/ inflight.json stop.json；第 5 节环境变量清单补两项（[#24](https://github.com/zephyr4123/TJU-AI4Science/issues/24)） | 实现与审查暴露的偏差回写，纲领不能描述另一套行为 | 主人 + Claude |
| 2026-09-10 | 第 5 节执行层适配按 R-1 spike 实测改写：隔离位、`//` 路径规则、kill_tree、快照 diff、成本 NaN、落盘（[#20](https://github.com/zephyr4123/TJU-AI4Science/issues/20)） | 四个未知全部拿到证据 | 主人 + Claude |
| 2026-09-10 | 第 5 节加算力适配：`Compute` 端口五个动作，submit / wait 句柄落盘，靠名字选择、不静默回退 | 主人问算力模块用什么模式；harness 在哪跑与 agent 在哪跑是两根正交的轴，各自端口 + 适配器 | 主人 + Claude |
| 2026-09-10 | "阶段"改"能力"，去掉框架内的顺序与回退判断，串联归协调层；磁盘布局按能力名而非序号，加 `journal.md`；第 4 节人在环改写为协调层行为，去掉 full-auto / gate-only 与文件通道；第 5 节加协调层驱动面 `ai4sci` 子命令；"底座"改称"执行层"（[#18](https://github.com/zephyr4123/TJU-AI4Science/issues/18)） | 固定顺序的阶段骨架就是"外层 for + 硬编码状态"；科研判断归协调层（人 + agent），框架不等人、不连跑 | 主人 + Claude |
