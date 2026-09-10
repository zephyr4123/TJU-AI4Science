# 流水线：阶段骨架与实验内环

- 状态：**aligned**（形状）；阶段切几段拟定为 7，见 Q-1
- 最近变更：2026-09-10
- 依据：[InternAgent 深读](../../research/selection/2026-0909-pipeline-frameworks/internagent.md)、[autoresearch 深读](../../research/selection/2026-0909-pipeline-frameworks/autoresearch.md)、[AutoResearchClaw 深读](../../research/selection/2026-0909-pipeline-frameworks/autoresearchclaw.md)

三个仓的编排形态都是"外层 for + 硬编码状态判断"，差别全在循环之外：用什么承载状态、用什么规则收敛、用什么机器判据卡住造假。我们的流水线层只有两样东西：**阶段骨架**和住在其中一个阶段里的**实验内环**。

## 1. 阶段骨架

框架只认"阶段"。每个阶段同一个形状：输入契约 → 干活 → 输出契约 → 机器校验。阶段之间不传内存对象，只传磁盘文件。

```
 任务包 (manifest)
      │
      ▼
 ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
 │ 1 文献  │──▶│ 2 假设  │──▶│ 3 设计  │──▶│ 4 实验  │──▶│ 5 分析  │──▶│ 6 写作  │──▶│ 7 验证  │
 └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
      │             │             │             │             │             │             │
  lit.jsonl     hypo.md      plan.yaml     runs/ +       analysis.md    paper.md     report.json
                                           ledger.tsv                                （门）

 每个阶段：
 ┌─────────────────────────────────────────────────────────────────┐
 │  读 stage-N-1/ 的产物 ──▶ [干活] ──▶ 写 stage-N/ 的产物 ──▶ 校验  │
 │                             │                               │    │
 │                       一次底座调用                   schema 对不上│
 │                  （阶段指令 + 任务包 + 领域包            就 FAILED │
 │                    + 「去读 runs/ ledger git log」）              │
 └─────────────────────────────────────────────────────────────────┘
```

- **7 段是拟定值**。阶段 1 可跳过：用户自带调研包就当阶段 1 的产物。v0.1 只做 3 → 4 → 5 → 7 四段。
- **每个阶段一次底座调用，新会话。** 上下文从磁盘来，不靠上一阶段的会话。这是 P-1 与 P-3 的直接推论。
- **失败处理**：FAILED 就停，不模板兜底、不静默跳过（P-7）。重试是显式配置，默认 0。
- **回退**：只有一个回退点，阶段 5 分析可以判定"回到阶段 3 重设计"，上限 2 次，每次把 `stage-3..5` 目录改名成 `_v{n}` 留档，不覆盖。
- **并行**：v0.x 不做。

### 磁盘布局

```
runs/<run_id>/
├── manifest.yaml           任务包 manifest 的快照，跑起来后不再读任务包
├── checkpoint.json         {last_completed_stage, run_id, ts}；原子写；续跑只看它
├── stage-01/ lit.jsonl
├── stage-02/ hypo.md
├── stage-03/ plan.yaml
├── stage-04/               实验内环整个住在这里，见第 2 节
│   ├── runs/               每轮一个 run_N/ 快照
│   └── ledger.tsv
├── stage-05/ analysis.md
├── stage-06/ paper.md
└── stage-07/ report.json
```

跨阶段读取按**契约声明的生产者**找文件，不按目录名 glob 倒序（AutoResearchClaw 在这一点上打了四层补丁）。

### 契约

每个阶段声明 `inputs`、`outputs`、每个产物的 schema（JSON Schema 或一个 `validate()` 函数）。契约是机器可查的（P-4），契约测试属于框架自己的测试，删掉全部任务包也要过（P-5）。

## 2. 实验内环（阶段 4）

唯一有循环的地方。核心是**四个角色分开**：三个仓都把它们混在一起了。

```
                 ┌──────────────────────────────────────────┐
                 │  底座 coding agent                        │   只干一件事：改代码、git commit
                 │  只能碰 code/ 目录                          │   不跑、不比、不记账
                 └───────────────┬──────────────────────────┘
                                 │ commit
                                 ▼
   ┌─────────────────────────────────────────────────────────────────────────┐
   │  runner（框架，确定性代码，零模型）                                         │
   │                                                                          │
   │   ① 拷快照 run_N/   ② 起独立进程跑 launcher   ③ 读 harness 吐出的产物      │
   │   ④ 跟 best 比：看 manifest 的 direction，过统计门                         │
   │   ⑤ 好 → 分支前进 / 差 → git reset 回 best     ⑥ ledger 记一行             │
   │   ⑦ 把「分数、好坏、失败分类」压成一小段文本给底座，回到顶上                  │
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
 底座改 code/ ──commit──▶ runner 跑（固定预算）──▶ harness: metric=0.9712, elapsed=298s
 ──▶ 比 best 0.9731，方向 minimize，差值超过统计门 ──▶ 留，best=0.9712
 ──▶ ledger +1 行 ──▶ 给底座：「留了。metric 0.9712 (best)。继续。」
```

**规则**

- 底座只改 `code/`，`harness` 与 `data/` 只读；runner 每轮校验它们的 hash，变了判 crash 并回滚。
- runner 是裁判：比较、留或回滚、记账全由 runner 做，底座不参与（P-2）。
- **统计门**：同配置重复 k 次估 σ（k 与阈值来自 manifest，默认 k=3、阈值 2σ）；差值不过门的判"持平"不留。这是 autoresearch 跑档里"被 keep 的改进比换种子的波动还小一个量级"的直接教训。
- **固定预算**：墙钟预算写在 manifest，harness 到时自停；超时 1.5 倍必杀，记 timeout。
- **失败分类**：确定性规则，不调模型。首批六类：缺依赖、超时、崩溃、结果文件缺失或不合 schema、指标为 NaN、只读文件被改。分类结果与修复建议一起给底座；同类失败连续 3 次判不可修复，停。
- **停止条件**：轮数上限、总预算、连续 N 轮不改进；任一触发即停并写原因。
- **上下文卫生**（P-9）：给底座的是摘要，不是 stdout；日志落盘。
- **revert-to-best**：下一轮的起点永远是分支 tip，不是上一轮的失败候选。

**账本 `ledger.tsv`**

```
iter  commit   parent   metric   direction  elapsed_s  seed  status   sigma   harness_sha  note
1     a1b2c3d  base     0.9979   minimize   300.1      42    keep     -       9f3e…        baseline
2     b2c3d4e  a1b2c3d  0.9860   minimize   299.7      42    keep     0.0007  9f3e…        halve batch
3     c3d4e5f  b2c3d4e  0.9863   minimize   300.4      42    discard  0.0007  9f3e…        lr 0.04→0.045 (within noise)
4     -        b2c3d4e  -        minimize   12.0       42    crash    -       9f3e…        OOM
```

- 每行的 `commit` 必须能在 git 里找到（keep 的在分支上，discard 的在 reflog 或 `refs/attempts/` 下保留），这是 P-3 的对账测试。
- `sigma` 来自统计门，`harness_sha` 证明评测没被改，`elapsed_s` 证明预算没被改。

## 3. 裁判与验证

- **确定性优先**：能用规则判的不用模型。阶段 4 的 accept / reject 完全确定性；阶段 7 的验证首批三条零 LLM 判据：报告里的每个数字能回溯到 `results.json`，每条引用在真实学术 API 里存在，每张图由数据文件生成。
- **模型裁判**：需要模型判断的（假设质量、写作质量、manifest 里 `requirements` 的 discussion 类验收），由框架派**一个新会话**，可指定与执行者不同的模型，只给产物不给轨迹，输出结构化 verdict（P-2）。
- **fail-closed**：门不过就停在门口，不涂黑、不降级（P-7）。

## 4. 人在环

- 暂停点在阶段边界：pre-stage 与 post-stage 两个钩子，阶段实现本身不感知人在环。
- 通道是文件：`runs/<id>/hitl/waiting.json` 写出等待，轮询 `response.json` 回传；任何能写 JSON 的东西都能当审批人，天然支持挂机过夜。
- 模式：`full-auto`、`gate-only`（只在阶段 3 设计后与阶段 7 验证后停）；v0.1 只做这两种，co-pilot 之后再说（Q-7）。
- 超时不自动放行，默认 ABORT；显式配置才 APPROVE。

## 5. 底座适配

一个 `Runner` 协议，每个 CLI 一个适配器：

```
run(prompt, cwd, timeout_s, allowed_paths) -> {exit_code, events[], changed_files[], cost}
```

- 非交互 + 结构化输出：Claude Code 走 `claude -p ... --output-format stream-json`（本机 `claude --help` 已确认这两个 flag 存在），Codex 走 `codex exec --json`（落地前对账）。
- 权限：只放行 `allowed_paths` 内的编辑；不用 `--dangerously-skip-permissions` 这类全放行标志。
- 超时由适配器执行，进程组一起杀。
- `events[]` 是取证用的结构化事件流（工具调用、文件改动、token），验证层与评测层都靠它。
- 任何适配器合入必须带一个真实调用点和一个真 CLI 的冒烟测试（P-8）。

## 变更记录

| 日期 | 改了什么 | 为什么 | 认可 |
|---|---|---|---|
| 2026-09-10 | 建档。阶段骨架、实验内环四角色、账本、裁判、人在环、Runner 协议 | 三个仓深读的收敛结论；棘轮来自 autoresearch，harness 注入来自 AutoResearchClaw，目录形态来自 InternAgent | 主人 + Claude |
