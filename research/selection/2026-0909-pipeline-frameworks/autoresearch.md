---
title: autoresearch 代码级深读
subtitle: 流水线层选型 · Karpathy 的棘轮循环到底跟"结果塞 prompt"差在哪
kind: 开源项目选型深读（只读代码，不跑、不装依赖）
date: 2026-09-09
scope: 仓库 https://github.com/karpathy/autoresearch，克隆到 vendor/autoresearch，master 提交 228791f（2026-03-25）；连同远端分支 origin/exp/H100/mar8（一次真实跑档）与 origin/agenthub（未合并的多 agent 版协议）；文中 文件:行 均相对该仓库根
status: 第一版
---

> **结论先行**：它跟 InternAgent"结果塞 prompt"的循环有本质区别，但区别**不在循环里传什么**（它每轮进上下文的信息比 InternAgent 还少，成功时只有两个数字），而在**循环外用什么承载状态、用什么规则收敛**。三件东西：git 工作树是状态载体（改进就推进分支，退步就 `git reset` 物理销毁）；一个外部的单标量硬闸（固定 5 分钟预算下的 `val_bpb`，低了才算数）；一份被 gitignore 的 append-only 账本（正因为不进 git，才能活过 `git reset`）。所以 agent 的上下文可以随时压缩、清空、换会话，棘轮不掉。代价是整套东西是荣誉制：跑实验、比大小、执行回滚、写账本全是 agent 自己做，仓库里没有一行代码去校验；而且接受阈值低于噪声，125 次实验里多次被 keep 的改进只有换个随机种子造成波动的十分之一。
>
> 怎么读：第 1 节是结论，第 4 节是与 InternAgent 内环的逐项对照，第 6 节是那次真实跑档的数据，第 7 节是协议的洞。它不是 InternAgent 的替代品，是补 InternAgent 短板的那一半：InternAgent 有流水线没有严格的实验床契约，autoresearch 有实验床契约没有流水线。横向对比见同目录的 [README.md](README.md)。

## 1. 结论

**一句话**：抄形态不抄代码。整个仓库 1200 行里跟我们任务相关的代码是零（GPT + Muon + flash-attn3 + 单卡 NVIDIA），但它的循环形态是目前读到的最值得照搬的"实验床契约"。

**它相对"结果塞 prompt"多出来的三件东西**（详见[第 4 节](#4-棘轮机制与-internagent-内环的对照)）：

1. **状态在文件系统里单调前进**，不在上下文里。`train.py` 的当前工作树就是"已积累的知识"，`git commit` / `git reset --hard` 就是 accept / revert 算子。
2. **接受与拒绝是外部标量硬闸**，不是让模型看着结果自己决定要不要继续。这是把验证层从"建议"升格成"闸门"。
3. **失败记忆外部化**成一份活过 revert 的账本 `results.tsv`，不靠 prompt 堆历史。

再加一条纪律：`run.log` 不许进上下文，只 `grep` 两行。每轮进上下文的信息量是常数，这才是它能在一台 H100 上连跑 12 小时、125 次实验不塌的原因。

**能借的五条骨架**（约 150 到 250 行就能重写一遍）：固定墙钟预算而非固定步数、单标量且实现无关的指标、保留集在只读文件里物理钉死、`stdout` 摘要 + exit code + fast-fail、git 作为状态载体 + 账本 + 显式 accept/revert。

**照抄会踩的四个洞**（都能用一条命令查，符合"机器判不了的规矩不是规矩"）：

1. **裁判员就是运动员**。跑实验、解析指标、比大小、执行 `git reset`、写账本五件事全是 agent 自己做。要写一个 runner 当裁判，agent 只负责改代码和提交。
2. **只读保护是字面的不是结构的**。`TIME_BUDGET`、`evaluate_bpb`、`make_dataloader` 全部 import 进了 agent 全权拥有的 `train.py`（`train.py:26`）。改时间预算、包一层假评测、把训练 split 改成 `"val"`，三件事都不违反"不许改 `prepare.py`"。
3. **账本不与 git 对账**。`results.tsv` 由被考核者手写、被 gitignore、commit 哈希从不校验；唯一能戳穿改预算的字段 `training_seconds` 恰好是协议不 grep 也不记的那个。
4. **没有统计门**。没有重复种子、没有显著性阈值，单次跑分变好就 keep。

**对 demo 的定位**：这套东西落在我们五层的"验证层 + 评测层"，给的是实验床契约；流水线层和 skills 层它基本没有，整个"流水线"就是 `program.md` 里 13 行伪代码。移植前提比以上都重要：**它成立的唯一原因是有一个 5 分钟、必然跑完、单标量、改什么都可比的评测。** 选型时先问的不是"用不用这套循环"，而是"我们的验证层能不能压缩成一个 5 分钟的标量"。

## 2. 仓库画像

| 项 | 实况 |
|---|---|
| 仓库 | <https://github.com/karpathy/autoresearch>，MIT，95k star |
| 时间线 | 36 个提交全在 2026-03（03-06 初始提交，03-25 最后一次合并）；karpathy 本人 28 个，外部贡献 8 条 |
| 规模 | git 追踪的文件只有 10 个：`README.md` 92 行、`program.md` 114 行、`train.py` 630 行、`prepare.py` 389 行、`analysis.ipynb`、`pyproject.toml`、`uv.lock`、`.gitignore`、`.python-version`、`progress.png` |
| 远端分支 | `exp/H100/mar8`：一次真实跑档，25 个提交 + agent 提交的 `results.tsv`；`agenthub`：未合并，多了一份 191 行的 `program_agenthub.md` |
| 测试与 CI | 零测试、零 CI、零 hook；`train.py` 零 `try/except`，靠 7 条 `assert` + 一条 NaN fast-fail |
| 依赖 | 9 个直接依赖，`torch==2.9.1` 钉在 cu128 索引；`uv.lock` 里 torch 只有 manylinux 与 win_amd64 wheel |
| 平台 | 单卡 NVIDIA 硬绑定：`train.py:21` 在模块导入期就调 `torch.cuda.get_device_capability()`；无 CPU / MPS 回退；README 列了 macOS / MLX / Windows / AMD 四个第三方 fork |
| 分工 | README 明说：`train.py` 由 agent 迭代，`program.md` 由人迭代，`prepare.py` 谁都不改 |

## 3. 协议：`program.md` 逐条

`program.md` 是写给 agent 的唯一指令文件，114 行纯 Markdown，无代码无 schema，README 称它"本质上是一个超轻量 skill"。启动就是一句自然语言 prompt 加"disable all permissions"。

**Setup**（`program.md:5-19`）：约定 run tag → 开分支 `autoresearch/<tag>` → 读三个文件 → 确认 `~/.cache/autoresearch/` 有数据 → 建只有表头的 `results.tsv` → 人确认后开跑。人介入点只有四个：setup 确认、数据缺失时替 agent 跑 `prepare.py`、手动打断、第二天看结果。

**边界**（`:25-37`）：只改 `train.py`，文件内"everything is fair game"；不改 `prepare.py`；不装包；不改评测（`evaluate_bpb` 是 ground truth）；VRAM 软约束；简洁性判据带数值门槛（0.001 提升加 20 行 hacky 代码不要，0.001 提升来自删代码一定留，提升约 0 但更简单也留）；第一次 run 必须原样跑 baseline。

**循环**（`:94-106`），每步的动作与状态载体：

| 步 | 动作 | 状态落在哪 |
|---|---|---|
| 1 | 看 git state（当前分支 / commit） | git |
| 2 | 改 `train.py` | 工作树 |
| 3 | `git commit` | git |
| 4 | `uv run train.py > run.log 2>&1`，不许 `tee`、不许让输出淹没上下文 | 磁盘 |
| 5 | `grep "^val_bpb:\|^peak_vram_mb:" run.log` | 上下文（两行） |
| 6 | grep 为空即崩溃 → `tail -n 50 run.log` 读 traceback → 修几次不行就放弃 | 上下文（50 行，仅崩溃时） |
| 7 | 写 `results.tsv`（不 commit，保持 untracked） | 磁盘，gitignore |
| 8 | `val_bpb` 变低 → 推进分支、保留 commit | git |
| 9 | 持平或变差 → `git reset` 回起点 | git（失败代码被销毁） |

**其它条款**：10 分钟超时必杀（`:108`）；崩溃分"笨错误就修"与"想法本身坏了就记 crash 跳过"（`:110`）；**NEVER STOP**（`:112`），人可能在睡觉，跑到被手动打断为止，没想法就"think harder"。

**账本格式**（`:64-88`）：5 列 TSV，`commit / val_bpb / memory_gb / status∈{keep,discard,crash} / description`，崩溃写 `0.000000 / 0.0`。

## 4. 棘轮机制，与 InternAgent 内环的对照

| 维度 | InternAgent 实验内环 | autoresearch |
|---|---|---|
| 迭代间传递什么 | 全部 run 的 `final_info.json` 原样 json.load 塞进下一轮 prompt，加 traceback | 磁盘上 `train.py` 的实际内容 + 分支 tip；上下文只进两个数字 |
| 谁判断"改进" | 没有判断。每个 run 的编辑都留下，agent 说 `ALL_COMPLETED` 或到 `max_runs` 就停 | 外部标量 `val_bpb`，低了才 advance |
| 失败怎么处理 | traceback 回喂，最多 5 次修错；失败的代码留在目录里 | `git reset --hard`，失败代码物理销毁；`results.tsv` 记一行 discard |
| 记忆载体 | prompt 里的历史 + 三层 memory（默认配置下断的） | git + 一份 untracked 的 TSV |
| 上下文被截断会怎样 | 进度退回 | 进度不掉，换个 agent 接手也行 |
| 每轮进上下文的量 | 整个 JSON + 整段 stderr（上限 3 万字符） | 常数：两行，崩溃时 50 行 |
| 可比性 | 无固定预算，`max_runs=2` | 固定 5 分钟墙钟，任何改动同一成本下可比 |
| 谁执行判定 | 代码（但不看指标方向） | agent 自己心算 |

两点要说清楚。第一，从信息通道看 autoresearch 反而更薄，它的优势全在"循环外"。第二，`results.tsv` 被 gitignore 不是疏忽，是设计：`.gitignore:22-23` 与 `program.md:102` 双重要求它 untracked，正是为了在 `git reset --hard` 摧毁失败代码后这条失败记录还活着。

但这份账本**只写不读**：循环里没有任何一步要求回读 `results.tsv`，"不要重复已失败方向"完全靠 agent 上下文。真实跑档里能看到重复描述（"matrix LR 0.04 to 0.045" 两次、"embedding WD 0.001 to 0.002" 三次），分不清是 baseline 前移后的合理复测还是遗忘。`agenthub` 分支把"读回前沿、查 current best 的 children"补成了循环第一步（`program_agenthub.md:137`），可见作者自己认这是个洞。

## 5. harness：`train.py` 与 `prepare.py`

### 5.1 分区

`train.py` 用注释横幅切成五段：模型 `28-291`、优化器 `293-427`、超参常量区 `428-451`（14 个全大写常量，"edit these directly, no CLI flags needed"）、setup `453-532`、训练循环 `534-604`、终局评测与打印 `606-631`。这些横幅只是分节，**没有把可变区与评测区分开**，评测区在另一个文件里。分界完全靠文件边界 + `prepare.py:26-28`、`:339-341` 两条"do not modify"横幅，没有任何机器校验。

### 5.2 指标

`val_bpb` = 总 nats / (ln2 × 总 UTF-8 字节数)，逐 token cross-entropy 按 token 字节长度加权，special token 记 0 字节被 mask（`prepare.py:343-365`）。对词表大小不变，所以架构改动可公平比。整个 5 分钟只在训练结束后算一次（`train.py:610-613`），没有中途验证曲线、没有 early stopping。一次实验的全部反馈信号就是一个标量加几个辅助数。

评测虽在只读文件里，但由 agent 的代码调用、吃 agent 的 model 对象、传 agent 的 `DEVICE_BATCH_SIZE`，打印 `val_bpb` 的那行 `print` 也在 `train.py:622`。"评测不可改"只挡住了 bpb 的算术公式，没挡住喂进公式的数。另一个可比性漏洞：评测步数是 `EVAL_TOKENS // (batch_size × MAX_SEQ_LEN)` 的整除，改 `DEVICE_BATCH_SIZE` 会同时改变评测 token 总量（`prepare.py:350-354`）。真实跑档里这个常量没被动过，洞没触发，但它敞着。

### 5.3 固定墙钟预算

`TIME_BUDGET = 300` 定义在 `prepare.py:31`，`train.py:26` import 进来，退出条件 `step > 10 and total_training_time >= TIME_BUDGET`（`train.py:603`），前 10 步吃掉 `torch.compile` 与 CUDA warmup 不计时。真正的杠杆在调度：LR 乘子、Muon weight decay 都以 `progress = total_training_time / TIME_BUDGET` 为自变量（`train.py:516-532`），所以"跑得更快"自动换成"同样调度形状下更多步"，吞吐优化和算法优化统一成同一个可比目标。代价是跨机器不可比，README 自己承认。

### 5.4 数据隔离

做得比协议宣称的还严：`VAL_SHARD` 钉死在 `shard_06542`，训练分片 `range(0, min(num_shards, 6542))` 永不含它（`prepare.py:42-44`、`:94-97`）；训练 dataloader 显式剔除 val 路径（`:258-263`）；**连 BPE tokenizer 的训练语料也剔除了 val 分片**（`:126-127`）。提交 `032d203` 显示这是后来修的，早期用"排序后最后一个分片"当 val，不同人下载不同分片数就在不同数据上评测。

### 5.5 输出契约与 fast-fail

`train.py` 全程不写任何文件，无 `open()`、无 `torch.save`、无 checkpoint。唯一产物是 stdout：`---` 分隔符后 9 行 `key: value` 定宽文本（`train.py:621-631`）。agent 用 `grep` 取两行。跟 InternAgent 的 `final_info.json` 比是"更弱的机器可读性 + 更强的上下文节流"。

退出码是唯一的机器信号：loss 为 NaN 或 > 100 时打印 `FAIL` 并 `exit(1)`（`train.py:569-572`），让发散的实验几秒内失败而不是烧掉 5 分钟。这条有段演化史：初版 `> 100` 漏掉 NaN（IEEE 754 下 NaN 任何比较都 False），社区 PR 改成 `not x <= 100`，再改成显式 `math.isnan`。

### 5.6 硬件耦合

`train.py:21` 模块顶层调 `torch.cuda.get_device_capability()`，无 GPU 机器 import 即崩；device / autocast 写死 cuda（`:461-462`）；MFU 分母写死 H100 峰值 `989.5e12`（`:463`），非 H100 上打印的 `mfu_percent` 是错的但仍进 stdout 给 agent 看；`prepare.py:298-299`、`:352` 直接建 pinned CPU buffer 与 cuda buffer。全仓 grep 不到 `mps` / `is_available` / cpu fallback。

## 6. 真实跑档：`origin/exp/H100/mar8`

这条分支是一次完整的过夜实验留档，是评估这套协议最硬的证据。

| 项 | 数据 |
|---|---|
| 时长 | 首个实验 commit 2026-03-08 03:38Z 到末次 15:50Z，12 小时 11 分 |
| 实验数 | 125 次（账本 126 行 = baseline + 125） |
| 结果 | keep 23（含 baseline 行）/ discard 102 / crash 1 |
| 收益 | `val_bpb` 0.997900 → 0.969686，降 2.83% |
| 收益分布 | 头两次（batch 524K 减半到 262K、depth 8 → 9）贡献 0.016127，占 57%；其余 123 次合计 43% |
| 改动形态 | 绝大多数 commit 的 diffstat 是 `1 file changed, 1 insertion(+), 1 deletion(-)`；整条分支相对 master 的 `train.py` 净差异 18 插入 19 删除 |
| 结构性改动 | parallel attn+MLP、weight tying、multi-query attention 都显著变差被丢弃 |

**噪声证据**：账本第 16 行是一次"只把随机种子 42 改成 137"的实验，`val_bpb` 从 0.973104 变到 0.973799，差 6.95e-4，被判 discard。而后续多次被 keep 的改进 delta 是 7.0e-5、8.5e-5、1.30e-4、3.1e-5、8.8e-5，全部比这个噪声样本小一个量级。棘轮把噪声也棘进去了；再加上验证集是一个钉死的分片被同一条链选择 125 次、没有 holdout，最终 2.83% 里有多少是真提升，这套协议无法回答。这不是 agent 作弊，是协议缺一个统计门。

实际形态是"一次改一个数字"的坐标下降，擅长在给定架构里刮超参，不擅长产生结构性创新。向课题组展示时要预设这个期望。

分支最后两条 commit 是收尾动作：把本该 untracked 的 `results.tsv` 提交进去做公开留档（即公开留档必须破一次自己的规矩），以及用一个新 commit 把被中断的实验改回去。这两条带 `Co-Authored-By: Claude Opus 4.6` 尾注，22 条实验 commit 都不带。

## 7. 协议的洞

| # | 洞 | 证据 | 性质 |
|---|---|---|---|
| 1 | 裁判员就是运动员：跑、比、reset、记账全由 agent 做，无 runner 无校验 | `program.md:94-106` | 结构性 |
| 2 | `TIME_BUDGET` 经 import 进入可改文件，改预算不违反字面规定；破绽字段 `training_seconds` 协议不 grep 不记 | `train.py:26`、`:603`、`program.md:100`、`:71` | 作弊面 |
| 3 | 评测调用点、model 对象、batch size、打印行都在可改文件；训练 split 是 `train.py:510` 的字符串字面量，改成 `"val"` 是一个单词 | `train.py:510`、`:613`、`:622` | 作弊面 |
| 4 | 账本由被考核者手写、不进 git、commit 哈希不校验；102 条 discard 的哈希在 reset 后本来就是悬空对象 | `program.md:102`、`analysis.ipynb:24-26` | 作弊面 |
| 5 | 接受阈值低于噪声，无重复种子、无显著性、无 holdout | 第 6 节 | 方法学 |
| 6 | 记忆只写不读，避免重复靠上下文 | `program.md:96-105` | 设计 |
| 7 | 证据保留极差：`run.log` 每轮覆盖不归档，9 个字段只有 2 个进账本，commit message 不带数字 | `program.md:71`、`:99` | 设计 |
| 8 | 自主性靠指令扛不住：`NEVER STOP` 写了一整段，作者自己仍在 `spawn.sh` 里写了每 120 秒检测空提示符并 `send-keys` "Keep going" 的 watcher | `spawn.sh:165-181`（见第 8 节） | 实证 |
| 9 | 跨机器不可比是设计内在的；`agenthub` 版的做法是强制每条结果标 `platform` 字段 | `README.md:64`、`program_agenthub.md:102` | 设计 |
| 10 | `prepare.py` 下载失败静默降级：部分分片失败只打印计数不退出，tokenizer 凑到 2 个文件就继续训 | `prepare.py:108-113` | 违反不吞失败 |

公平地说，协议确实防住了几类常见跑偏：改动范围锁死单文件（diff 可审）、依赖冻结、评测文件只读、显存不许爆、复杂度不许无限膨胀、跑飞 10 分钟必杀、崩溃必须读 traceback、上下文不许被日志淹没。但全部是散文约束，靠 agent 自觉。

## 8. 被删的 `spawn.sh` 与未合并的 `agenthub`

**`spawn.sh`**：初始提交里有一个 248 行的多 agent 编排脚本，第二天被作者删除（`1e207aa`，"erase experimental file from before that snuck through in my purge"），README 与 `program.md` 里的引用一并清掉，但 `.gitignore:9-17` 至今留着 `worktrees/`、`results/`、`queue/` 和"Agent prompt files (generated per-session by launchers)"的化石。用 `git show 1e207aa^:spawn.sh` 可取回。形状：

```
bash spawn.sh launch mar5 opus:0 sonnet:1 codex:2 codex:3
```

每个 worker 一条分支 `autoresearch/<tag>-gpu<N>` + 一个 `git worktree` + 软链共享 `.venv` + `CUDA_VISIBLE_DEVICES` 绑卡，全部塞进 tmux tiled session。启动命令是 `claude --dangerously-skip-permissions --model <m> "Read program.md and follow the instructions."` 或 `codex --dangerously-bypass-approvals-and-sandbox`（`spawn.sh:70-73`）。末尾的 watcher 每 120 秒 `capture-pane` 做 md5，内容没变且匹配到空提示符就判定 agent 卡住，`send-keys` 发一句 "Keep going. Do not stop — continue your research loop."（`:165-181`）。

这才是真正的"底座 coding agent 编排层"：worktree 隔离 + 绑卡 + tmux + 空闲催促。对我们的意义是两条实证：长跑必须配外部哨兵，不能只靠 prompt；多 agent 并行的隔离单位是 git worktree 而不是目录拷贝。

**`agenthub`**：未合并分支上有一份 191 行的 `program_agenthub.md`（作者提交，message 只有一个字 "hmmm"）。把单机协议改成中心 hub 版：`git bundle` 通过 HTTP 推拉 commit；`/api/git/leaves` 取探索前沿的叶子 commit，`/api/git/commits/<hash>/children` 查"这个 commit 上别人已经试过什么"；`#results` / `#discussion` 两个消息板。三处关键差异：循环第一步从"看 git state"升级成"读 hub、看 leaves、看 current best 的 children 避免重复劳动"；结果强制加 `platform` 字段；只推 improvement，discard 和 crash 只发帖不推 commit，让 hub 上的 git 树天然是一棵纯改进树。hub 服务端不在这个仓里也没开源，跑没跑通无从判断。

## 9. 对 demo 的意义

### 9.1 借什么

| 借的东西 | 从哪儿 | 大约行数 | 抄进内仓时要改 |
|---|---|---|---|
| 固定墙钟预算，调度按 progress 走 | `train.py:516-532`、`:555-563`、`:578-579`、`:603-604` | 40 | 连调度一起抄，不只抄退出条件，否则拿不到"跑得快 = 做得多"的性质 |
| 单标量、实现无关的指标 | `prepare.py:343-365` | 25 | 换成对网格分辨率 / 离散格式 / 单位制不变的误差度量（相对 L2、守恒量偏差），否则 agent 会改离散化刷指标 |
| 保留集物理钉死 | `prepare.py:42-44`、`:126-127`、`:258-263` | 15 | 验证算例有明确 ID、准备阶段就分开、分离逻辑写在 agent 不改的文件里 |
| stdout 摘要 + exit code + fast-fail | `train.py:569-572`、`:621-631` | 20 | 同时写一份 JSON 产物给自动汇总用，stdout 摘要给 agent grep，两个都要 |
| git 状态载体 + 账本 + 显式 accept/revert | `program.md:94-106` | 协议 | 不写 checkpoint、不留隐藏状态、每次实验对应一个 commit |
| 简洁性判据的数值门槛措辞 | `program.md:37` | 协议 | 直接抄 |
| 上下文卫生条款 | `program.md:99-101` | 协议 | 直接抄 |
| 多 agent 编排形态 | `git show 1e207aa^:spawn.sh` | 248 | worktree 隔离 + 绑卡 + 外部哨兵；权限标志按我们的红线来 |

### 9.2 必须补的

1. **裁判外置**：runner 负责跑实验、解析指标、比较、执行 `git reset`；agent 只改代码和提交。
2. **只读文件校验和**：`prepare.py` 类文件的 hash 进 CI；禁止在可改文件里重绑 import 进来的常量（一条 grep 能查）。
3. **账本机器可对账**：`training_seconds` 等破绽字段必须进账本，commit 哈希与 git 对账，每轮 `run.log` 归档不覆盖。
4. **统计门**：同配置重复 k 次估 σ，接受阈值 > 2σ 或对候选做二次确认跑；一个从不参与选择的 holdout。
5. **评测进程隔离**：评测跑成独立子进程，只吃 agent 的产物文件不吃 agent 的对象，这样"评测不可改"才是真的。
6. **记忆读回**：循环第一步读账本，按 `agenthub` 版的做法。

补齐大约再多 60 到 100 行。

### 9.3 移植前提

这套协议成立的唯一原因是有一个 5 分钟、必然跑完、输出单标量、改什么都可比的评测。换一个没有这种评测的领域（跑一次几小时、指标多维、或需要人判），闸门失效，棘轮立刻退化成"结果塞 prompt"。对新工科任务，网格加密、时间步长、求解器选择本来就是精度换时间的权衡，固定预算是合适的；但仿真往往要看收敛曲线、残差、守恒量违反度才能判断结果可信，照抄"只留一个数"会失去判断实验是否有效的能力。

### 9.4 跟 InternAgent 各取一半

InternAgent 给任务目录契约、实验执行循环、经验记忆闭环；autoresearch 给实验床契约、棘轮、账本、编排形态。demo 建议先照 autoresearch 的形状搭一个最小闭环（单文件可改 + 固定预算 + 单标量 + git 棘轮 + 外部账本），把 runner 做成裁判，然后拿 InternAgent 的内环做对照，展示"上下文被清空后谁还能接着爬"。这个对比就是我们相对两者的差异化叙事。

## 10. 可运行性

- `requires-python >= 3.10`，9 个直接依赖，`uv.lock` 锁 74 个包。
- **macOS 上 `uv sync` 这一步就过不去**：`torch` 被 `[tool.uv.sources]` 强制走 cu128 索引，lock 里没有任何 macosx wheel；即便绕过，`train.py:21` 导入期就崩。缩小版只能走 README 列的四个 fork。
- README 自己给了 7 条往小机器缩的旋钮，其中两条要动 `prepare.py` 里的"不可改"常量（`MAX_SEQ_LEN`、`EVAL_TOKENS`），等于承认那两条横幅是给"同一台机器上的同一轮实验"用的，不是给移植用的。
- 数据：HF 的 `karpathy/climbmix-400b-shuffle`，6543 个 parquet 分片，默认下载 10 个训练分片 + 1 个 val 分片，缓存在 `~/.cache/autoresearch/`。单分片体积仓库里没写。

## 11. 未验证与待办

- 125 次实验的 `run.log` 全部丢失，无法核查 `training_seconds` 是否始终约 300 秒，只能说协议留了口子，不能说被用过。
- 换种子那次只做了一次，7e-4 是噪声的一个样本不是标准差估计。
- 22 条实验 commit 不带 AI 尾注、2 条收尾 commit 带，跑实验的 agent 到底是不是 Claude Code、什么模型，仓库里无法确认。
- `agenthub` 的 hub 服务端不开源，那套"commit 树即前沿"的协调跑没跑通无从判断。
- 四个 fork 是否同时改了 `program.md` 的禁止清单、改完还能不能跨机器比，要单独读 fork。
- 改 `DEVICE_BATCH_SIZE` 会让 `val_bpb` 漂多少，只能推出"会漂"，量级要实跑。

## 12. 调研方法

- 克隆到外层仓 `vendor/autoresearch`（gitignore 挡住），连同两条远端分支。
- 两个读者：一个读协议（`README.md`、`program.md`、`analysis.ipynb`、36 个提交的历史、两条远端分支），一个逐行读 harness（`train.py`、`prepare.py`、依赖锁）。每条结论带 `文件:行`，不跑代码、不装依赖。
- 两份结果合计 42 条发现，本文由此汇总并另抽查 5 条（`train.py:26` 的 import、`:603` 的退出条件、跑档账本的状态计数与换种子行、`spawn.sh` 的历史与 watcher、`agenthub` 协议的三处差异），全部属实。
- 读者顺带发现 `vendor/autoresearch/vendor/` 下有一个套错层级的残留克隆（是我们自己 clone 时 cwd 没回到外层仓根造成的），已删除。
