# platform 0.2.0 初级版 · 诚实的实验内环

- 状态：**draft**（等主人审阅后转 aligned）
- 目标日期：2026-09-28
- 版本：产品版本 = 内仓 `platform/` 的 tag `v0.2.0`（0.1.0 是骨架）；外仓有自己的版本线，CHANGELOG 里只记一句交叉引用。spec 文件按产品版本号命名
- 纲领：[architecture/](../architecture/README.md)；未决项：[open-questions.md](../architecture/open-questions.md)
- 目标合约：[#2](https://github.com/zephyr4123/TJU-AI4Science/issues/2)；母 issue [#3](https://github.com/zephyr4123/TJU-AI4Science/issues/3) 到 [#7](https://github.com/zephyr4123/TJU-AI4Science/issues/7)，milestone `platform 0.2.0 · 初级版`；架构调整 [#18](https://github.com/zephyr4123/TJU-AI4Science/issues/18)

## 目标

在一个玩具任务上跑通"协调层 + 框架 + 执行层 + 工具"四层的最小闭环。协调层就是人加一个交互态的 Claude Code，用四条命令把四个能力手工串起来；框架不连跑、不等人。能当众演示三件事：

1. **上下文清空后循环还能接着爬**：中途杀掉执行层会话，重启后从 git 与账本续跑，进度不掉。
2. **账本与 git 对得上**：账本每一行的 commit 在 git 里找得到，每一行的耗时与 harness hash 证明预算和评测没被改。
3. **假成功被机器拦住**：注入一个"直接 print 一个好看的分数"的假实验，runner 判 crash 并回滚。

这三件事是三个开源仓都没做到的，也是我们相对它们的差异化叙事。

## 范围（R-n）

| 编号 | 需求 | 纲领依据 |
|---|---|---|
| R-1 | `Runner` 协议 + Claude Code 适配器：`claude -p --output-format stream-json`，权限只放行 `allowed_paths`，超时杀进程组，产出结构化事件流 | workflow §5 |
| R-2 | 任务包契约：`manifest.yaml` schema、`harness/` 约束与 hash 校验、`code/` `data/` `run_0/` 布局；`ai4sci task validate` | packs §2 |
| R-3 | 玩具任务一个：30 秒内跑完、单标量、方向 minimize；候选 MLP 回归或悬臂梁有限元 | Q-5 |
| R-4 | 实验内环 runner：拷快照、独立进程跑 launcher、读 `results.json`、按 direction 比较、统计门、git 留或回滚、账本、失败六分类、停止条件；内环之外用一个无模型的剧本后端把 A-4 到 A-9 在 CI 里测全 | workflow §2 |
| R-5 | 能力最小版：设计、实验、分析、验证四个能力各自一条 `ai4sci` 子命令，契约校验，内环 checkpoint 续跑；框架不连跑，顺序由协调层定 | workflow §1，P-10 |
| R-6 | 验证最小版：`analysis.md` 里出现的每个数字能回溯到 `results.json`，不过就 FAILED | workflow §3 |
| R-7 | CLI：`ai4sci task validate` / `run new` / `cap` / `loop run` / `loop resume` / `status`，命令名拟定；没有 `--mode`，没有等人 | workflow §5 |
| R-8 | 框架自己的测试：契约、账本对账、续跑、假成功拦截；`make check` 门禁 | P-4 P-8 |
| R-9 | 文档：内仓 README 承接步骤，CHANGELOG | ADR-0002 |
| R-10 | 协调层最小 skill 包：内仓 `coordinator/` 一份入口指南，让 Claude Code 当科研助理驱动框架：读 `runs/` 与账本、调 `ai4sci`、什么该问人 | README §2，Q-10 |

## 非目标（N-n）

- N-1 文献、假设、写作三个能力
- N-2 人在环的异步通道（无人值守过夜）、WebSocket、任何 UI；人在协调层对话里，不是框架功能
- N-3 领域包（只有 `generic`）
- N-4 Codex 适配器（时间富余再做，不算验收）
- N-5 docker、集群、多 agent 并行
- N-6 跨 run 记忆、skills 注入
- N-7 真实工科任务（学院定了另开 spec）

## 约束（C-n）

- C-1 Python，venv，依赖钉版本；`framework/` 下 grep 不到模型 API（P-1）
- C-2 不吞异常、不模板兜底、验证不过就停（P-7）
- C-3 执行层只改 `code/`；harness 与 data 只读且校验 hash（P-6）
- C-4 每个配置项有读取点与断言，每个抽象带调用点（P-8）
- C-5 遵守外层 `CLAUDE.md` 红线：内仓不依赖外层路径、大文件不进 git、发版走 `make release`
- C-6 每个工作单元一条外层仓 issue，commit 引用 issue（spec coding + issue driven）
- C-7 框架不连跑、不等人：每条子命令一个能力，跑完退出（P-10）；协调层与执行层的 skill 搜索路径不相交（P-11）

## 验收（A-n）

尽量一条命令能查。

| 编号 | 验收标准 | 怎么查 |
|---|---|---|
| A-1 | 门禁绿 | `make check` 含框架测试全过 |
| A-2 | 框架零模型调用 | `grep -rE "anthropic\|openai\|claude_sdk" framework/` 为空 |
| A-3 | 框架不随任务改 | 临时删掉 `tasks/` `domains/`，框架测试照过 |
| A-4 | 账本与 git 对账 | 跑玩具任务 ≥ 20 轮，账本每行 `commit` 在 git 里能找到，keep 行在分支上、discard 行在 `refs/attempts/` 下 |
| A-5 | 续跑 | 第 10 轮时 kill 执行层进程，`ai4sci loop resume` 后从第 11 轮继续，best 不变 |
| A-6 | 假成功拦截 | 注入直接 print 分数不产 `results.json` 的假实验，runner 判 crash 并回滚，账本记 crash |
| A-7 | 只读被改拦截 | 执行层改动 `harness/`，runner 判 crash 并回滚 |
| A-8 | 统计门 | 账本每个 keep 行的差值 > `accept_sigma × sigma`，σ 来自 `run_0/` 的重复 |
| A-9 | 预算 | 每行 `elapsed_s` 在预算的 0.8 到 1.5 倍之间，超出的行 status 为 timeout |
| A-10 | 数字回溯 | `analysis.md` 里的每个数值在 `results.json` 里能匹配（1% 容差），构造一个编造数字的分析 → 验证能力 FAILED |
| A-11 | 框架不连跑 | 四个能力用四条命令手工串起来才能走完；`framework/` 里 grep 不到能力顺序表，没有子命令跑完一个能力再起另一个 |

## 里程碑

| 日期 | 交付 |
|---|---|
| 09-13 | R-1 R-2 R-3：适配器能跑一条 prompt，玩具任务 `run_0` 出来 |
| 09-18 | R-4：内环跑 20 轮，A-4 A-6 A-7 A-8 过 |
| 09-22 | R-5 R-6 R-7：四个能力 + 续跑 + 数字回溯，A-5 A-10 A-11 过；内测 tag `v0.2.0-rc.1` |
| 09-28 | R-8 R-9 R-10：门禁、文档、协调层入口指南、初级版 tag `v0.2.0` |

## 未决（挂 issue）

- Q-5 玩具任务选哪个（MLP 回归开箱即有；有限元更贴工科但要先写基线）→ [#12](https://github.com/zephyr4123/TJU-AI4Science/issues/12)；真实案例采集 → [#1](https://github.com/zephyr4123/TJU-AI4Science/issues/1)
- Q-8 Codex 适配器是否纳入 → [#15](https://github.com/zephyr4123/TJU-AI4Science/issues/15)
- Q-10 协调层 skill 包放哪、怎么注入 → [#19](https://github.com/zephyr4123/TJU-AI4Science/issues/19)

## 变更记录

| 日期 | 改了什么 | 为什么 | 认可 |
|---|---|---|---|
| 2026-09-10 | 建档 | 纲领 aligned 后的第一份版本 spec | 待主人审 |
| 2026-09-10 | 改名 v0.1 → platform 0.2.0 | 外仓已发到 0.2.0，两条版本线撞号；产品版本一律带 platform 前缀 | 主人 + Claude |
| 2026-09-10 | 按纲领四层改写：目标段、R-5 R-7 N-2 改写，R-4 加剧本后端，新增 R-10 C-7 A-11，"底座"改"执行层"，未决加 Q-10（[#18](https://github.com/zephyr4123/TJU-AI4Science/issues/18)） | 加了协调层，框架不连跑不等人；三件演示不变 | 主人 + Claude |
