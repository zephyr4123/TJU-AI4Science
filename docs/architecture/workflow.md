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

- **7 个能力各自的输入、输出、执行者、验证判据**（拟定，落地一个改一个）：

| 能力 | 级别 | 输入 | 输出 | 谁执行 | 机器判据 |
|---|---|---|---|---|---|
| 文献 | 项目 | 研究问题 | `lit.jsonl`（DOI / arXiv id、摘要、笔记） | 执行层 + `tools/` 学术 API（Q-11） | 每条引用在学术 API 里存在 |
| 假设 | 项目 | 研究问题 + 文献 + 项目记忆 | `hypotheses.md`（假设台账：编号、依据、可证伪的预测） | 执行层 | schema；每条假设引用的文献在 lit 里 |
| 设计 | 项目 → 任务包 | 一条假设 + 领域包 | 任务包（manifest、harness、code 基线、data、run_0）+ `plan.yaml` | 执行层，协调层拍 manifest | `ai4sci task validate` 通过 |
| 实验 | run | 任务包 | 账本、实验笔记、best commit | 执行层改 code/，runner 判 | 统计门、账本 × git 对账、只读 hash |
| 分析 | 项目 | 全部 run 的账本、笔记、best diff | `analysis.md`（哪条假设被证实 / 证伪、数字从哪来） | 执行层 | 每个数字回溯到账本或 results.json |
| 写作 | 项目 | 分析 + 文献 + 假设台账 + 模板 | `paper.md` / LaTeX + 图 | 执行层分节调用（Q-12），图由 tools 出 | 数字回溯、引用真伪、图源 |
| 验证 | 项目 | 论文 + 上游全部产物 | `report.json` | 框架，零模型；discussion 类交隔离裁判 | 三条判据全过才 PASS |

  platform 0.2.0 只做设计、实验、分析、验证四个（Q-1），且设计暂以现成任务包代替。文献能力可以不跑：用户自带调研包就当它的产物。**2026-09-15 起实验、分析、验证三个已落地**（`ai4sci cap list` 列出的就是全部），设计 = `ai4sci run new` 吃现成任务包。
- **每个能力一次执行层调用，新会话。** 上下文从磁盘来，不靠上一个能力的会话。这是 P-1 与 P-3 的直接推论。
- **失败处理**：FAILED 就停，不模板兜底、不静默跳过（P-7）。重试是显式配置，默认 0。
- **回退**：框架不判断"要不要回到设计"，协调层看了分析结论决定。框架只提供留档：重跑一个能力时把旧目录改名成 `_v{n}`，不覆盖。
- **并行**：v0.x 不做。

### 装配与固定流

能力没有顺序，所以流程是装配出来的，不是框架里写死的（P-12）：

- **子集也是流。** auto-research 只用实验、分析、验证三个能力，设计被现成任务包顶掉；文献综述只用文献一个；补写论文用分析加写作读已有 run。这能成立靠一条规则：契约挂在产物上，不挂在"上游是谁"。实验能力只认磁盘上一个过 schema 的任务包，不关心它是设计能力产出的还是人手写的。
- **入口契约由人填。** 端到端流的入口是研究问题，auto-research 流的入口是任务包；协调层"填契约"这步只是换了填的对象，其它规则不变。
- **固定流是存好的图，不是代码。** 平台可以预置几条常用流；用户在低代码 UI 里拖出来的也是一张图。图怎么描述、谁解释，见 Q-13；能力描述符落地之前不建图 DSL。
- **产物跨流复用。** 每个流跑完留在磁盘上的东西，别的流按契约声明的生产者去读；一个 run 的账本半年后可以喂给写作。

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
│   ├── notebook.md         实验笔记：每轮的自述、改动、裁决，下一轮整本进 prompt
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

**能力描述符**（已落地，`framework/contracts/capability.py`）：每个能力子包导出 `DESCRIPTOR`（name、level、stage、title、what、summary、inputs、outputs、params、needs_executor、needs_compute、criteria）与统一入口 `run(run_dir, ports, **params) -> str`；`capabilities.discover()` 扫子包并断言入口签名与描述符的参数表一致，`ai4sci cap` 的子命令从描述符生成，所以 CLI 参数与描述符一致是构造保证。`ai4sci cap list --json` 输出全部描述符，是低代码 UI 的节点定义、也是 UI 后端与协调 agent 的同一份真相（P-12）。它是从实验与分析两个真实例里抽出来的：只放两个都用得上的字段。

**阶段是能力上面的一层标签**（[#53](https://github.com/zephyr4123/TJU-AI4Science/issues/53)）：上图的七个格子（文献、假设、设计、实验、分析、写作、验证）不是七个能力，是七个科研阶段；落地时设计拆成了 design + baseline，实验拆成了 start + experiment，所以一个阶段下挂几颗能力。描述符的 `stage` 只认这七个（`STAGES`），`discover()` 断言。阶段没有代码、没有运行时、不定先后（P-10），目录也不按阶段套子目录——契约挂在产物上，不挂在分组上。能力上**不写**「属于哪条工作流」：工作流文件引用能力，反过来写是两份真相；`ai4sci show caps` 与 `GET /cap` 的 `used_by` 是反查算出来的。工作流「覆盖哪几个阶段」（`covers`）同样现算；有实验或分析却没有验证，机器提醒一句（`remarks`），不拦。`title` / `what` 是给研究者看的人话，页面与以后的 TUI 读同一份，不在某个界面里另抄。

**接口是文件名，不是 schema**（P-13，[#54](https://github.com/zephyr4123/TJU-AI4Science/issues/54)）：`check_flow` 比的是路径字符串——上游吐的集合包含下游要的，就通。这够用，因为每条路径只有一个生产者，形状由生产者的代码定（`validate_task`、`contracts.analysis`、`schemas/report.schema.json`、账本的写函数）。命名三规矩见 README P-13；`discover()` 加载时就断言输出唯一、输入有出处，名字写错当场被拒，不等跑到一半。种子（不需要生产者的名字）在 `contracts/flow.py`：任务段是发布那一刻包里已有的 `manifest.yaml` `design.md` `publish.json` `data/` `env/`，run 段是 `start` 建 run 时就有的 `manifest.yaml` `work/` `checkpoint.json`（checkpoint 是 run 的状态，建它的是 start、experiment 只改它，所以是种子不是 experiment 的输出）。今天 17 个名字里两处不齐、都不改：`start` 声明的输出 `runs/<run_id>/` 是过桥用的位置不是接口，没人把它当输入，桥由 `flow.py` 按名字单独查；`run_0/` 说的是位置不是角色（基线），名字已发出，按第二条不改义也不改名。

一个例子，工坊里以后拼进一颗「写作」能力：它只能往 `writing/` 里写，产物叫 `paper.md` 还是 `draft.md` 随它，撞不到别人；它声明「吃 `analysis/analysis.md` 与 `experiment/ledger.tsv`」，这两个名字上面有人吐，通；写成 `analysis/*.md` 或 `summary.md`，加载时就被拒。agent 拼流时看 `show caps` 每颗一句「吃什么、吐什么、里面有什么」，照名字接，不读 schema。

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
- **失败分类**：确定性规则，不调模型，按优先级判：`readonly_violated`（diff 或 hash 发现 harness / data 被改）→ `timeout` → `missing_dependency`（stderr 有 ModuleNotFoundError / ImportError）→ `crash`（stderr 有 Python traceback）→ `no_results`（results.json 缺失、不合 schema、或 harness 自报 status ≠ ok；假成功落在这里）→ `nan_metric`。执行层会话自己没走完（超时、被杀、CLI 崩）判 `executor_failed`，半截改动丢弃，同样计入连续三次。另有两个非失败状态：`noop`（执行层什么都没改，或改动全被 .gitignore 挡住）、`interrupted`（那一轮被杀）。分类结果与修复提示一起给执行层；同类失败连续 3 次判 `unrecoverable`，停。
- **停止条件**：`max_iterations`、连续 `patience` 轮不改进（缺省 5）、`max_cost_usd` 累计用尽、`unrecoverable`；任一触发写 `experiment/stop.json` 并停。已停的 run 再跑一轮都不跑：要不要加预算续命是协调层的决定（P-10）。`--max-iters N` 只是本次调用的配额，用完返回 `batch_exhausted`，不算停止。
- **续跑**：每轮开跑前写 `experiment/inflight.json`，结账后删。`loop resume` 先做 checkpoint、账本、git 三方对账，对不上就 fail-closed；有 in-flight 标记的那一轮记 `interrupted`、在飞的 job 先收尸、候选 commit 进 `refs/attempts/` 再回到 best。`loop run` 撞到 in-flight 标记直接拒绝并指引用 resume。
- **轮间记忆**：`experiment/notebook.md` 一个 run 一本，runner 每轮追加执行层的自述（假设 / 改动 / 预期）、`git diff --stat`、裁决；下一轮整本进 prompt，执行层先读前面试过什么再动手。笔记由 runner 写，活在棘轮之外，回滚不抹。
- **上下文卫生**（P-9）：给执行层的是账本与笔记（有界），不是 stdout；日志落盘。
- **续命**：已停的 run 用 `ai4sci cap experiment <id> --patience/--max-iterations/--max-cost-usd --reason` 改预算、清停止标记，journal.md 记一行，然后接着跑；要不要续是协调层的决定（P-10）。
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
- 每行的 `commit` 必须能在 git 里找到（keep 的在分支上，其余有 commit 的在 `refs/attempts/` 下），`ai4sci show run` 每次都跑这条对账，对不上退非 0。这是 P-3 的机器判据。
- `sigma` 来自统计门，`harness_sha` 是 `harness/SHA256SUMS` 自身的 sha256，`elapsed_s` 是 compute 测到的墙钟（不采信 harness 自报），`cost_usd` 与 `executor_s` 是执行层那次调用的花费与耗时。拿不到的值写 NaN 或 `-`，绝不写 0。

## 3. 裁判与验证

- **确定性优先**：能用规则判的不用模型。实验能力的 accept / reject 完全确定性；验证能力首批三条零 LLM 判据：报告里的每个数字能回溯到 `results.json`，每条引用在真实学术 API 里存在，每张图由数据文件生成。
- **模型裁判**：需要模型判断的（假设质量、写作质量、manifest 里 `requirements` 的 discussion 类验收），由框架派**一个新会话**，可指定与执行者不同的模型，只给产物不给轨迹，输出结构化 verdict（P-2）。
- **协调层只读判决**：验证结论回到协调层，由它决定接受、重跑还是换方向；协调层不替裁判改判，也不裁自己派出去的活。

### 数字回溯（已落地：分析与验证两个能力）

- **分析的形状**（`contracts/analysis.py`）：`analysis/analysis.md` 固定三节 `## 结论` / `## 数据` / `## 证伪与未决`；`## 数据` 是表 `| run | 指标 | 值 |`，值从 results.json 原样抄，是数字回溯的锚。执行层的 prompt 里附每个 run 的指标清单，只许从清单抄。分析能力只校验形状（三节齐全、表至少一行），不裁判自己的数字（P-2）。
- **验证的四项检查**（`capabilities/verify/checks.py`，零模型）：分析存在；数据表每行 (run, 指标, 值) 在那个 run 的 `results.json` 里能找到，相对容差 1%（`--tolerance` 可调，实际值为 0 时声称也必须为 0）；正文里带小数点或指数的数与表里某个值在容差内相等；账本 × git 对账（复用内环那把尺子）。
- **已知边界**（写在这里，不在代码里静默放宽）：整数不查（轮次、行数都是整数），百分比不查（相对变化没有绝对来源），行内代码与代码块不查。执行层被告知相对变化只写百分比、不写版本号之类带小数点的东西。
- **报告**：`verify/report.json`（schema `contracts/schemas/report.schema.json`）：`status` PASS / FAIL、每项 `passed` 与 `details` 一行一条。PASS 与 FAIL 都写报告，FAIL 再退 1——协调层看退出码，读报告看细节。
- **重跑**：分析与验证重跑时旧目录改名 `analysis_v{n}` / `verify_v{n}`，不覆盖。
- **fail-closed**：门不过就停在门口，不涂黑、不降级（P-7）。

## 4. 人在环

人在协调层的对话里，不是框架的功能。

- 框架不等人：每条子命令跑完一个能力就退出并写状态，需要人判断的事由协调 agent 在对话里问。
- 自主程度是协调 agent 的行为，不是框架的模式：可逆的自己定并记录，贵的带方案来问，拿不准的停。
- 无人值守（挂机过夜）时协调 agent 怎么把问题留给人、人怎么异步回复，是协调层自己的通道问题，platform 0.2.0 不做（Q-7）。

## 5. 框架的驱动面与执行层适配

### 协调层怎么驱动框架

框架是一个 Python 包加一条 `ai4sci` CLI。命令行上只有四类东西，每样要么是能力、要么是键、要么是查询、要么是入口（2026-09-16 收纳，[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)）：

```
ai4sci cap <name> <task_dir|run_id> [--backend] [--compute] [--<param>]
                                      能力：agent 按，产出文件；子命令从描述符生成，用法错退 2、没通过退 1
                                      六颗：design baseline start（任务包上）experiment analysis verify（run 上）
                                      续跑 = cap experiment --resume；续命 = cap experiment --patience/--max-iterations/--max-cost-usd --reason
ai4sci sign task <dir> --by <谁>      键：人按，发布需求，写 publish.json
ai4sci sign run <id> --by <谁>        键：人按，验收结果，写 accept.json
ai4sci show tasks | task <dir> | run <id> | caps | workflows | flow <能力>...
                                      查询：只读，与 serve 的 GET 端点同一批函数
ai4sci chat ... / ai4sci serve        入口：终端里聊 / 网页后端
```

并掉的旧命令：`task validate|list|env build|publish`、`run new|extend|accept`、`loop run|resume`、`status`、`cap list`、`flow list|check`。环境由 `cap baseline` 缺了就建，不再单独按。

CLI 是薄壳：每个能力对外是一个 Python 函数（实验能力是 `capabilities.experiment.run_loop`），子命令只做参数解析与退出码。协调 agent 走 CLI，低代码 UI 后端与测试直接调函数，三者跑的是同一段代码（P-12）。

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

### 协调层适配

同一批 CLI 的第二种用法：多轮、按 session id 续接、事件边跑边出。端口 `Chat` 与 `Runner` 放同一个 `backends/__init__.py`，适配器放同一个文件（一个 CLI 一个文件）；换一家 CLI 就是加一个文件，自研 agent 就是第三个适配器（主人红线：涉及 agent 的一律可替换，[#51](https://github.com/zephyr4123/TJU-AI4Science/issues/51)）：

```
turn(message, cwd, timeout_s, *, session_id, system_prompt, allowed_paths, bash_rules)
  -> Iterator[ChatEvent{kind: init|text|tool_use|tool_result|denied|done|error, text, tool, tool_input, session_id, cost_usd, duration_s, raw}]
```

- **续接**：Claude Code 走 `claude -p <message> --resume <session id> --append-system-prompt <指南>`；隔离位与执行层同一组，但**不带** `--no-session-persistence`，多轮靠的就是 CLI 自己的会话持久化。实测两轮记得住（haiku 两轮 $0.02；sonnet 列任务包并复述、续接答预算，两轮 $0.12）。
- **指南注入**：服务会话隔离了所有设置源，`coordinator/README.md` 由 `framework/chat/guide.py` 连同一段"你在服务里"的前言塞进 system prompt（命令写 `.venv/bin/ai4sci`、发布键不由你按、先说结论用人话）。
- **权限**：Bash 只放行 `ai4sci`，写只放行 `tasks/` 与 `runs/`；dontAsk 下只读 Bash 自动放行，但带 `for` / `cat` 的复合命令实测被拒，agent 会改用 Read 工具。
- **落盘**：会话内容存在 CLI 自己的目录里，我们只记 session id；但每一轮的原生事件流自己留一份在 `runs/chats/<id>/turn-N/events.jsonl`，它是"agent 那一轮到底按了什么"的唯一证据（P-3）。meta 记后端、session id、cwd、完成的轮数、累计花费；transcript 给人翻；忙锁 `inflight.json` 让同一段对话同一时刻只跑一轮；半途放弃的轮次目录留着不计数。
- **两张脸同一套函数**：`ai4sci chat new|send|list` 在终端里聊，`ai4sci serve` 起标准库 HTTP + SSE 给页面：对话（`POST /chats`、`POST /chats/<id>/messages` 逐事件推、`GET /chats[/<id>]` 带第一句话标题与一轮一条的 history）、需求看板（`GET /tasks[/<id>]`：阶段、钥匙状态、manifest、design.md、预检；`POST /tasks/<id>/publish` 发布键）、编排看板（`GET /cap` 节点清单、`GET /flow/check?steps=` 通不通）、结果看板（`GET /runs[/<id>]`：best 对基线、账本、分析、验证、验收状态；`POST /runs/<id>/accept` 验收键）、`GET /health`；不是接口前缀的路径端页面的静态文件。节点清单与流检查由 cli 以函数传入，chat 层不认识 capabilities；看板读盘在 `framework/chat/boards.py`，全是纯函数，NaN 出门前换 None。十来个端点仍是标准库，页面要更多再说。
- 配置从环境变量读：`AI4SCI_COORDINATOR_MODEL`（缺省不传）、`_MAX_TURNS`（50）、`_MAX_BUDGET_USD`（每轮 2.0）、`_TIMEOUT_S`（900：它会按按钮等基线跑完）。
- 不做：token 级流式、多用户、鉴权（本机单人服务）。协调 agent 从终端里技术上也能按两颗键（`task publish` / `run accept`），只有页面上那两颗能做到"只有人能按"；指南写明它不替人按。

### 界面适配

界面也是适配器（主人 2026-09-16：现在是 GUI，之后有 TUI，要留位置，[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)）。一种界面一个目录 `ui/<kind>/`，全部是上面那套端点的客户端，互相不认识、也不认识框架内部；换一种界面后端一行不改。契约就是端点清单（`framework/chat/server.py` 文件头）+ 响应体（`boards.py`），网页的 `ui/web/src/api/client.ts` 是它的照抄，写 TUI 时照抄一份即可。

- **网页 `ui/web/`**：React 19 + Tailwind v4 + shadcn（radix-nova 预设）+ reactbits 两个动效件，Vite 构建成静态文件，`ai4sci serve` 缺省端 `ui/web/dist`（`--ui` 可换目录，没构建只开接口）。三栏：左边对话列表，中间对话（SSE 事件流，agent 按的每个按钮以工具行显示、可展开看输入输出、denied 标红），右边一张看板三个页签，每页是助理写给研究者的一页纸（一句话结论 → 三个大数字 → 几段人话 → 细节折叠 → 键在文末；状态码、判决、命令一律翻成句子，原始值只在折叠层）——需求（想解决什么、怎么算好、花多少、**发布键**）、工作流（现在有几条工作流、几颗能力，都从后端读，页面不写死顺序）、结果（比原来好了多少、可信吗、助理的结论、每一轮一句话、**验收键**）。编排画布等自定义工坊再做。两颗键都要署名，署名记在浏览器里。设计口径在内仓 `docs/PRODUCT.md` / `docs/DESIGN.md`。
- **验收记录**：与发布记录对称。`runs/<id>/accept.json` 签 best_iter / best_metric / best_commit 与验证报告的结论（`framework/run/accept.py`，放 run 层因为它读 checkpoint）；内环在跑、只有基线、报告不合约都拒绝；验收之后 best 又变了记录标 stale，看板要人再看一遍，不让旧签名盖住新结果。
- **门禁**：`make ui-check`（tsc + oxlint + vitest + 构建）并入 `make check` 与 CI（setup-node 22）；依赖只进 `ui/web/node_modules`。浏览器闭环实测（playwright）：发布 → `publish.json`、验收 → `accept.json`、流通不通报「第 4 步 design 是 task 级能力，run 段之后不能回到任务包」、haiku 两轮对话（第二轮 `ls -1 tasks/` 的工具行）。
- **`ui/tui/`**：留位置没建。

## 变更记录

| 日期 | 改了什么 | 为什么 | 认可 |
|---|---|---|---|
| 2026-09-10 | 建档。阶段骨架、实验内环四角色、账本、裁判、人在环、Runner 协议 | 三个仓深读的收敛结论；棘轮来自 autoresearch，harness 注入来自 AutoResearchClaw，目录形态来自 InternAgent | 主人 + Claude |
| 2026-09-15 | 第 1 节标实验 / 分析 / 验证已落地，能力描述符改为已落地的形状；第 3 节加"数字回溯（已落地）"：分析三节与数据表、验证四项检查、1% 容差、已知边界、report.json、重跑轮转；第 5 节 CLI 加 `cap list` / `cap <name>`（[#35](https://github.com/zephyr4123/TJU-AI4Science/issues/35) [#36](https://github.com/zephyr4123/TJU-AI4Science/issues/36) [#37](https://github.com/zephyr4123/TJU-AI4Science/issues/37)） | 09-22 单元的分析与验证做完，纲领不能描述另一套行为 | 主人 + Claude |
| 2026-09-15 | 第 1 节加"装配与固定流"（子集也是流、入口契约由人填、固定流是存好的图、产物跨流复用），契约加"能力描述符"；第 5 节注明 CLI 是薄壳、能力对外是 Python 函数（[#33](https://github.com/zephyr4123/TJU-AI4Science/issues/33)） | 主人对齐高度模块化：不同任务用不同子集流程，低代码图是第二种协调层 | 主人 + Claude |
| 2026-09-10 | 第 1 节加七个能力的输入 / 输出 / 执行者 / 判据表，标出项目级与 run 级（[#29](https://github.com/zephyr4123/TJU-AI4Science/issues/29)） | 端到端对齐，实体分两级 | 主人 + Claude |
| 2026-09-10 | 第 2 节加轮间记忆（实验笔记）与续命，P-9 措辞随纲领 README 改；磁盘布局加 notebook.md；第 5 节加 run extend（[#28](https://github.com/zephyr4123/TJU-AI4Science/issues/28) [#26](https://github.com/zephyr4123/TJU-AI4Science/issues/26)） | 真跑暴露执行层失忆，主人拍板必须有轮间记忆 | 主人 + Claude |
| 2026-09-10 | 第 1、2 节按 R-4 内环实现回写：runner 提交、work/ 独立 git 仓、失败分类改成带优先级的六类 + noop / interrupted、账本加 cost_usd 与 executor_s 且基线不占行、统计门加 min_delta 与 σ=0 fail-closed、停止条件与续跑规则、磁盘布局加 work/ prompts/ inflight.json stop.json；第 5 节环境变量清单补两项（[#24](https://github.com/zephyr4123/TJU-AI4Science/issues/24)） | 实现与审查暴露的偏差回写，纲领不能描述另一套行为 | 主人 + Claude |
| 2026-09-10 | 第 5 节执行层适配按 R-1 spike 实测改写：隔离位、`//` 路径规则、kill_tree、快照 diff、成本 NaN、落盘（[#20](https://github.com/zephyr4123/TJU-AI4Science/issues/20)） | 四个未知全部拿到证据 | 主人 + Claude |
| 2026-09-10 | 第 5 节加算力适配：`Compute` 端口五个动作，submit / wait 句柄落盘，靠名字选择、不静默回退 | 主人问算力模块用什么模式；harness 在哪跑与 agent 在哪跑是两根正交的轴，各自端口 + 适配器 | 主人 + Claude |
| 2026-09-10 | "阶段"改"能力"，去掉框架内的顺序与回退判断，串联归协调层；磁盘布局按能力名而非序号，加 `journal.md`；第 4 节人在环改写为协调层行为，去掉 full-auto / gate-only 与文件通道；第 5 节加协调层驱动面 `ai4sci` 子命令；"底座"改称"执行层"（[#18](https://github.com/zephyr4123/TJU-AI4Science/issues/18)） | 固定顺序的阶段骨架就是"外层 for + 硬编码状态"；科研判断归协调层（人 + agent），框架不等人、不连跑 | 主人 + Claude |
| 2026-09-16 | §5 加「协调层适配」：`Chat` 端口、Claude Code 续接、指南注入、对话落盘、`ai4sci chat` / `serve`（[#51](https://github.com/zephyr4123/TJU-AI4Science/issues/51)） | 产品形态定为两个看板一次验收，网页要能起协调 agent；主人拍板走 CLI 子进程 + 续接、藏在端口后面可替换 | 主人 + Claude |
| 2026-09-16 | §5 协调层适配的端点清单补看板与两颗键；加「界面适配」：`ui/<kind>/` 一种界面一个目录、全是端点的客户端，网页第一版、验收记录 `accept.json`、门禁与浏览器闭环（[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)） | MVP 第 5 件页面；主人红线：UI 也是适配器，GUI 之后有 TUI 要留位置 | 主人 + Claude |
| 2026-09-16 | 「套餐」改叫工作流并落成文件 `workflows/*.yaml`（`intake` 接一个新课题、`auto-research` 自动做实验；步骤是能力、键或纯人的事，`assumes` 声明前提），`run new` 升成第 6 颗能力 `start`（`contracts.flow` 的桥改认它）；页面的进度页（写死五步）换成工作流页（[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)） | 主人指出页面把两条固定流拼起来当成了平台：平台是能力清单，工作流只是预装的拼法；每样东西要么是能力、要么是键、要么是查询 | 主人 + Claude |
| 2026-09-17 | §1 描述符加阶段（`stage`，七个科研阶段，能力上面的一层标签）与人话字段（`title` / `what`）；工作流的覆盖范围与能力的「用在哪条流」都是算出来的，不存（[#53](https://github.com/zephyr4123/TJU-AI4Science/issues/53)） | 主人提出能力归科研模块、模块拼工作流；对齐后「模块」改叫阶段，反向归属不存 | 主人 + Claude |
| 2026-09-17 | §1 契约段加「接口是文件名不是 schema」：种子清单、`checkpoint.json` 归 run 种子、两处不齐的名字与原因、写作能力的例子（[#54](https://github.com/zephyr4123/TJU-AI4Science/issues/54)） | 文档即接口升成 P-13，落地两条加载时断言 | 主人 + Claude |
