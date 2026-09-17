# platform 0.2.0 初级版 · 诚实的实验内环

- 状态：**滚动**。spec 只对下一步负责：第 n 步的 spec 只驱动第 n+1 步的执行，做完一步回来改；不设 aligned 门槛，变化是常态
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
| R-5 | 能力最小版：设计、实验、分析、验证四个能力各自一条 `ai4sci` 子命令，契约校验，内环 checkpoint 续跑；框架不连跑，顺序由协调层定；第二个能力落地时从两个真实例抽出能力描述符，CLI 只是薄壳。**2026-09-15**：实验 / 分析 / 验证与描述符落地（[#35](https://github.com/zephyr4123/TJU-AI4Science/issues/35) [#36](https://github.com/zephyr4123/TJU-AI4Science/issues/36) [#37](https://github.com/zephyr4123/TJU-AI4Science/issues/37)），设计 = `run new` 吃现成任务包 | workflow §1，P-10 P-12 |
| R-6 | 验证最小版：`analysis.md` 里出现的每个数字能回溯到 `results.json`，不过就 FAILED。**2026-09-15 完成**：`ai4sci cap verify`，A-10 在 CI 与真跑各过一次（[#37](https://github.com/zephyr4123/TJU-AI4Science/issues/37)） | workflow §3 |
| R-7 | CLI：`ai4sci task validate` / `run new` / `cap` / `loop run` / `loop resume` / `status`，命令名拟定；没有 `--mode`，没有等人。**2026-09-15 完成**：`cap list` / `cap <name>` 从描述符生成（[#35](https://github.com/zephyr4123/TJU-AI4Science/issues/35)） | workflow §5 |
| R-8 | 框架自己的测试：契约、账本对账、续跑、假成功拦截；`make check` 门禁 | P-4 P-8 |
| R-9 | 文档：内仓 README 承接步骤，CHANGELOG | ADR-0002 |
| R-10 | 协调层最小 skill 包：内仓 `coordinator/` 一份入口指南，让 Claude Code 当科研助理驱动框架：读 `runs/` 与账本、调 `ai4sci`、什么该问人。**2026-09-15 首版**：`coordinator/README.md`，auto-research 流四条命令与每步看什么（[#38](https://github.com/zephyr4123/TJU-AI4Science/issues/38)） | README §2，Q-10 |
| R-11 | 任务包自带环境：`env/`（python-version + requirements.lock），uv 建任务级 venv（`tasks/<id>/.venv` 与 `runs/<id>/.venv`），launcher 只经 `$AI4SCI_PYTHON` 起 Python、裸 python 判不合法；manifest 加 `format_version` 必填与 `source` 可选；`ai4sci task env build`；`mlp-regression` 迁到新契约。**2026-09-16 完成**（[#39](https://github.com/zephyr4123/TJU-AI4Science/issues/39)） | packs §2，Q-6 |
| R-12 | 第一个真领域包 `domains/petab/`：profile、`prompts/experiment.md`、`skills/petab/SKILL.md`；skill 注入走 prompt 快照，实验与分析都吃；内仓 `docs/add-a-task.md`「十分钟接一个任务」。**2026-09-16 完成**（[#39](https://github.com/zephyr4123/TJU-AI4Science/issues/39)） | packs §3，Q-2 |
| R-14 | 接任务的按钮 `ai4sci task design <dir>`：读 manifest、协调层写的 `design.md`、领域 skill，起执行层（只放行 `harness/` `code/`）写草稿，框架封 harness（执行位、SHA256SUMS）、ruff、validate（不查 run_0），停；`--feedback` 喂回改第二版；不抽描述符、不进 `cap`。协调层 README 固定流之二改为三问 + 按钮。验收方式是**模仿一个研究者**只经对话把第二道基准题接进来，卡点逐条成 issue。**2026-09-16 完成**：`task design` 落地（11 个剧本测试）；rahman-nll 只经按钮接入，协调 agent 用 `--feedback` 打回一次静默兜底，8 轮出 1 个 keep、验证 PASS；12 个卡点并成 [#42](https://github.com/zephyr4123/TJU-AI4Science/issues/42)–[#46](https://github.com/zephyr4123/TJU-AI4Science/issues/46)，顺带修了 `run extend` 对不可修复无效（[#41](https://github.com/zephyr4123/TJU-AI4Science/issues/41)） | vision「给谁用、凭什么」，packs §2 |
| R-15 | 发布做成钥匙：`ai4sci task publish <dir> --by <谁>` 写 `publish.json`（签 manifest.yaml 与 design.md 的 sha256）；`cap design` `cap baseline` `run new` 没它或签的文件改过都不开。接任务预检：门高的算式只此一处（内环 gate 同用），manifest 主指标可写 `attainable`，基线到尽头不到一个门或门是 0 就停；「看基线」停点取消。**2026-09-16 完成**（[#48](https://github.com/zephyr4123/TJU-AI4Science/issues/48)） | vision「产品形态」，packs §2，#42 |
| R-16 | 接任务与跑基线升格成 task 级能力：描述符 `level: task`，`ai4sci cap design|baseline <task_dir>` 从描述符生成，`cap list` 列全；`task design` / `task baseline` 删除。**2026-09-16 完成**（[#49](https://github.com/zephyr4123/TJU-AI4Science/issues/49)） | P-12，Q-13 |
| R-17 | 流通不通检查 `ai4sci flow check <能力>...`：按描述符对吃吐文件，任务段→桥（run new）→run 段，同一 run 不重复，`--json` 给编排看板；不跑。**2026-09-16 完成**（[#50](https://github.com/zephyr4123/TJU-AI4Science/issues/50)） | P-12，Q-13 |
| R-18 | 协调 agent 服务化第一版：`backends` 第二个端口 `Chat`（多轮、session id 续接、事件流）与 Claude Code 适配器；`framework/chat/` 指南注入、对话落盘 `runs/chats/<id>/`、标准库 HTTP + SSE；`ai4sci chat new|send|list`、`ai4sci serve`。涉及 agent 的一律走端口可替换。**2026-09-16 完成**（[#51](https://github.com/zephyr4123/TJU-AI4Science/issues/51)） | vision「产品形态」，workflow §5 |
| R-19 | 页面第一版：`ui/web/` React 19 + Tailwind v4 + shadcn，`ai4sci serve` 端出静态文件；对话（SSE 事件流、工具行翻成人话）、需求页（想解决什么、怎么算好、花多少、**发布键**）、工作流页（几条工作流、几颗能力，从 `workflows/*.yaml` 与 `/cap` 读）、结果页（比原来好了多少、可信吗、助理的结论、每轮一句、**验收键**），每页是一页纸、术语全翻译；`run new` 升成能力 `start`，能力清单六颗；后端加 tasks / runs / flow/check 端点与验收记录 `accept.json`（`ai4sci run accept`）；`ui/` 是界面适配器层，TUI 留位置；`make ui-check` 进 `make check` 与 CI。**2026-09-16 完成**（[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)） | vision「产品形态」，workflow §5 界面适配 |
| R-20 | 命令行收成四类：`cap` 能力（六颗，续跑与续命是 `experiment` 的参数）、`sign task|run` 两颗键、`show` 查询、`chat` / `serve` 入口；`task` `run` `loop` `status` `flow` `cap list` 全部并掉，环境由 `cap baseline` 自建。R-7 R-15 R-17 A-5 A-14 里的旧命令名是历史记录，以本行为准。**2026-09-16 完成**（[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)） | 主人：每样东西要么是模块要么不是；workflow §5 |
| R-21 | 能力归到七个科研阶段下：描述符加 `stage`（只认 `STAGES`）与人话 `title` / `what`；`show caps` / `GET /cap` 按阶段列、空阶段标空、带反查的 `used_by`；工作流与 `show flow` 带算出来的 `covers` 与「有实验没验证」的 `remarks`；`GET /stages`；页面能力清单按阶段分组。阶段是标签不定先后，能力上不写属于哪条流。**2026-09-17 完成**（[#53](https://github.com/zephyr4123/TJU-AI4Science/issues/53)） | 主人：能力归科研模块、模块拼工作流；workflow §1 |
| R-13 | 第一个真任务包 `tasks/boehm-nll/`（学长案例二）：按 packs §2 的分工手工走一遍设计流程——协调层填 manifest、执行层写 harness / code / env、人签 evaluate.py——跑出 run_0 与 σ；这是设计能力的第二个实例，描述符之后从两个实例抽。**2026-09-16 完成**：run_0 200.33、σ 28.98，真跑 3 轮 + 分析 + 验证 PASS，手工流沉淀为 `coordinator/README.md` 固定流之二（[#40](https://github.com/zephyr4123/TJU-AI4Science/issues/40)） | packs §2，Q-5，#1 |

## 非目标（N-n）

- N-1 文献、假设、写作三个能力
- N-2 人在环的异步通道（无人值守过夜）、WebSocket、任何 UI；人在协调层对话里，不是框架功能
- N-3 ~~领域包（只有 `generic`）~~ **2026-09-16 纳入**：R-12 加 `petab`
- N-4 Codex 适配器（时间富余再做，不算验收）
- N-5 docker、集群、多 agent 并行
- N-6 跨 run 记忆、skills 注入
- N-7 ~~真实工科任务（学院定了另开 spec）~~ **2026-09-16 纳入**：学院方向是交叉领域，案例二作为 R-13 进本版；案例一仍不跑

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
| A-9 | 预算 | 每行 `elapsed_s` 不超过预算 1.5 倍，超出的行 status 为 timeout；0.8 倍下限只对填满预算的 harness 成立，玩具任务 0.3 秒跑完不适用 |
| A-10 | 数字回溯 | `analysis.md` 里的每个数值在 `results.json` 里能匹配（1% 容差），构造一个编造数字的分析 → 验证能力 FAILED |
| A-11 | 框架不连跑 | 四个能力用四条命令手工串起来才能走完；`framework/` 里 grep 不到能力顺序表，没有子命令跑完一个能力再起另一个 |
| A-12 | 环境隔离 | 夹具任务经框架跑 harness，`sys.executable` 落在 `runs/<id>/.venv/` 下（CI 测试）；`make check` 前后平台 venv 的 `pip list` 不变 |
| A-13 | 环境契约机器可查 | `harness/*.sh` 里的裸 `python3` 被 `task validate` 判不合法；`format_version` 缺失或不受支持判不合法 |
| A-15 | 接任务是按钮 | 剧本执行层下 `task design`：合约草稿被封且 validate 空、越界 / 会话死 / 什么都没写判 `DesignFailed`、裸 python 与 lint 问题作为清单回传、第二版提示带现状与反馈（CI）；第二道基准题只经 `task design` 接入、协调层没手改 `harness/`、`task validate` 退 0（[#41](https://github.com/zephyr4123/TJU-AI4Science/issues/41)） |
| A-16 | 没发布不开 | 夹具包不发布时 `run new` `cap design` `cap baseline` 都退 1 并指向 `task publish`；发布后改 manifest 或 design.md 再按退 1 说「改过了」（CI）；仓内三个任务包都带 `publish.json` 且 validate 退 0（[#48](https://github.com/zephyr4123/TJU-AI4Science/issues/48)） |
| A-17 | 预检停得住 | 夹具 σ=0 无 min_delta → `run new` 退 1；`attainable` 离基线不到一个门 → `cap baseline` 退 1 说「无解」；rahman-nll 真包预检：baseline 21.5958、gate 0.15、room 0.4158（2.8 个门）（[#48](https://github.com/zephyr4123/TJU-AI4Science/issues/48)） |
| A-18 | 节点清单完整、流查得出 | `cap list` 列出 design baseline experiment analysis verify 五个；`flow check design baseline experiment analysis verify` 退 0，跳过 baseline 报桥缺 run_0/，只有 verify 报缺 analysis.md（CI，[#49](https://github.com/zephyr4123/TJU-AI4Science/issues/49) [#50](https://github.com/zephyr4123/TJU-AI4Science/issues/50)） |
| A-19 | 网页能起协调 agent、发话、收话、让它按按钮 | 剧本适配器下：两轮续接带同一个 session id、事件流与 transcript 落盘、忙锁 409、错误码（CI）；真跑：sonnet 经 `ai4sci chat` 两轮，第一轮 `ls tasks/` + 读三个 manifest 用人话复述，第二轮续接答 rahman 预算，共 $0.12；`ai4sci serve` 起来 `/health` `/cap` `/chats` 都通（[#51](https://github.com/zephyr4123/TJU-AI4Science/issues/51)） |
| A-20 | 人在页面上按两颗键，机器认账 | HTTP 层（CI）：`POST /tasks/<id>/publish` 不署名 400、design.md 为空 422、成功 201 且 `publish.json` 落盘；`POST /runs/<id>/accept` 内环在跑 422、成功后 `accept` 带 stale=false；静态页与单页应用回退、接口前缀下怪路径仍 404。浏览器闭环（playwright，本机）：需求看板按「发布需求」→ `publish.json` 由张三签、阶段跳到可开跑；结果看板按「验收结果」→ `accept.json` 签第 6 轮 21.3392、验证 PASS；编排看板 design → baseline → experiment → design 报不通；对话两轮 haiku 共 $0.03，第二轮工具行 `ls -1 tasks/` 可展开（[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)） |
| A-14 | 真任务跑通 | `ai4sci task validate tasks/boehm-nll` 退 0；run_0 与 σ 出来；`loop run` 至少 3 轮不炸 |

## 里程碑

| 日期 | 交付 |
|---|---|
| 09-13 | R-1 R-2 R-3：适配器能跑一条 prompt，玩具任务 `run_0` 出来。**2026-09-10 完成**：内仓分支 `feat/runner-spike`，[#20](https://github.com/zephyr4123/TJU-AI4Science/issues/20) [#21](https://github.com/zephyr4123/TJU-AI4Science/issues/21) |
| 09-18 | R-4：内环跑 20 轮，A-4 A-6 A-7 A-8 过。**2026-09-10 完成**：内仓分支 `feat/inner-loop`，真跑 21 轮证据在 [#25](https://github.com/zephyr4123/TJU-AI4Science/issues/25)；A-7 真跑未触发，由 CI 验 |
| 09-22 | R-5 R-6 R-7：四个能力 + 续跑 + 数字回溯，A-5 A-10 A-11 过；内测 tag `v0.2.0-rc.1`。**2026-09-15 主体完成**：内仓分支 `feat/analysis-verify`，[#35](https://github.com/zephyr4123/TJU-AI4Science/issues/35) [#36](https://github.com/zephyr4123/TJU-AI4Science/issues/36) [#37](https://github.com/zephyr4123/TJU-AI4Science/issues/37) [#38](https://github.com/zephyr4123/TJU-AI4Science/issues/38)；A-10 CI + 真跑，A-11 真跑证据在 [#38](https://github.com/zephyr4123/TJU-AI4Science/issues/38)；rc.1 tag 等 [#17](https://github.com/zephyr4123/TJU-AI4Science/issues/17) 的 rc 后缀 |
| 09-2x | R-11 R-12 R-13：任务自带环境、领域包 petab、真任务 boehm-nll 的 run_0 与 σ；A-12 A-13 A-14 过。**2026-09-16 完成**：内仓分支 `feat/task-env`，A-12 A-13 在 CI，A-14 真跑证据在 [#40](https://github.com/zephyr4123/TJU-AI4Science/issues/40)（[#39](https://github.com/zephyr4123/TJU-AI4Science/issues/39)） |
| 09-2x | R-14：接任务的按钮 + 模仿研究者走一遍；A-15。**2026-09-16 完成**（[#41](https://github.com/zephyr4123/TJU-AI4Science/issues/41)） |
| 09-2x | R-15 R-16 R-17：发布钥匙 + 预检、两个按钮进能力清单、flow check；A-16 A-17 A-18。**2026-09-16 完成**：内仓分支 `feat/mvp-batch-1`（[#47](https://github.com/zephyr4123/TJU-AI4Science/issues/47)） |
| 09-2x | R-19：页面第一版；A-20。**2026-09-16 完成**：内仓分支 `feat/web-ui`（[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)） |
| 09-2x | R-18：协调 agent 服务化第一版；A-19。**2026-09-16 完成**：内仓分支 `feat/coordinator-service`（[#51](https://github.com/zephyr4123/TJU-AI4Science/issues/51)） |
| 09-28 | R-8 R-9 R-10：门禁、文档、协调层入口指南、初级版 tag `v0.2.0` |

## 未决（挂 issue）

- Q-5 玩具任务选哪个（MLP 回归开箱即有；有限元更贴工科但要先写基线）→ [#12](https://github.com/zephyr4123/TJU-AI4Science/issues/12)；真实案例采集 → [#1](https://github.com/zephyr4123/TJU-AI4Science/issues/1)。**2026-09-16**：案例到，案例二 boehm-nll 选为第一个真任务（R-13）
- Q-8 Codex 适配器是否纳入 → [#15](https://github.com/zephyr4123/TJU-AI4Science/issues/15)
- Q-10 协调层 skill 包放哪、怎么注入 → [#19](https://github.com/zephyr4123/TJU-AI4Science/issues/19)

## 变更记录

| 日期 | 改了什么 | 为什么 | 认可 |
|---|---|---|---|
| 2026-09-10 | 建档 | 纲领 aligned 后的第一份版本 spec | 主人 + Claude |
| 2026-09-10 | 改名 v0.1 → platform 0.2.0 | 外仓已发到 0.2.0，两条版本线撞号；产品版本一律带 platform 前缀 | 主人 + Claude |
| 2026-09-10 | 按纲领四层改写：目标段、R-5 R-7 N-2 改写，R-4 加剧本后端，新增 R-10 C-7 A-11，"底座"改"执行层"，未决加 Q-10（[#18](https://github.com/zephyr4123/TJU-AI4Science/issues/18)） | 加了协调层，框架不连跑不等人；三件演示不变 | 主人 + Claude |
| 2026-09-10 | 09-13 一格标完成；R-1 实测出的约束回写纲领 workflow §5 | 第一单元做完 | 主人 + Claude |
| 2026-09-10 | 09-18 一格标完成；R-4 加实验笔记与 executor_failed | 真跑暴露执行层失忆与被杀炸循环两个问题，当天修掉 | 主人 + Claude |
| 2026-09-10 | A-9 去掉 0.8 倍下限的硬要求 | 玩具任务不填满预算，下限只对长跑 harness 有意义 | 主人 + Claude |
| 2026-09-15 | R-5 加能力描述符与 CLI 薄壳（[#33](https://github.com/zephyr4123/TJU-AI4Science/issues/33)） | 主人对齐高度模块化；描述符从两个真实例抽，不先设计 | 主人 + Claude |
| 2026-09-15 | R-5 R-6 R-7 R-10 标完成或首版，09-22 一格标主体完成（[#35](https://github.com/zephyr4123/TJU-AI4Science/issues/35) [#36](https://github.com/zephyr4123/TJU-AI4Science/issues/36) [#37](https://github.com/zephyr4123/TJU-AI4Science/issues/37) [#38](https://github.com/zephyr4123/TJU-AI4Science/issues/38)） | 分析、验证、描述符、cap CLI、协调层指南一次做完，真跑 live-20 与 flow-1 | 主人 + Claude |
| 2026-09-10 | 状态从"draft 待审"改为"滚动" | 主人：spec 随时会变，第 n 步只驱动第 n+1 步，没有更硬的理由驱动更后面的执行 | 主人 + Claude |
| 2026-09-16 | 加 R-11 R-12 R-13 与 A-12 A-13 A-14，N-3 N-7 纳入，里程碑加 09-2x 一格（[#39](https://github.com/zephyr4123/TJU-AI4Science/issues/39) [#40](https://github.com/zephyr4123/TJU-AI4Science/issues/40)） | 学长案例到了（#1），主人定调按工业级开源项目完善：任务自带环境、领域包、接任务流程三处缺口用真任务补 | 主人 + Claude |
| 2026-09-16 | 加 R-14 A-15 与 09-2x 第二格（[#41](https://github.com/zephyr4123/TJU-AI4Science/issues/41)） | 主人定调平台给非工程师用，入口必须是对话；接任务七步里唯一不是按钮的一步做成按钮，用模仿研究者的真人测试验收 | 主人 + Claude |
| 2026-09-16 | R-11 R-12 R-13 与 09-2x 一格标完成（[#39](https://github.com/zephyr4123/TJU-AI4Science/issues/39) [#40](https://github.com/zephyr4123/TJU-AI4Science/issues/40)） | 第一个真任务端到端闭环跑通：三轮全 discard、分析证伪两条假设、验证 PASS；门是否太严带回人拍板 | 主人 + Claude |
| 2026-09-16 | 加 R-15 R-16 R-17 与 A-16 A-17 A-18，09-2x 第三格（[#47](https://github.com/zephyr4123/TJU-AI4Science/issues/47) [#48](https://github.com/zephyr4123/TJU-AI4Science/issues/48) [#49](https://github.com/zephyr4123/TJU-AI4Science/issues/49) [#50](https://github.com/zephyr4123/TJU-AI4Science/issues/50)） | 产品形态定为两个发布键一次验收：发布做成钥匙、签字挪到脚本前、看基线交给机器预检；编排看板要节点清单完整、要能查流通不通 | 主人 + Claude |
| 2026-09-16 | 加 R-18 A-19 与 09-2x 第四格（[#51](https://github.com/zephyr4123/TJU-AI4Science/issues/51)） | MVP 第 4 件：网页要能起协调 agent；主人拍板走 CLI 子进程 + 续接，端口可替换 | 主人 + Claude |
| 2026-09-16 | 加 R-19 A-20 与 09-2x 第五格（[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)） | MVP 第 5 件：页面。主人定 React + Tailwind v4，UI 作适配器留 TUI 位置，浏览器闭环验证 | 主人 + Claude |
| 2026-09-16 | 加 R-20：命令行收成四类（[#52](https://github.com/zephyr4123/TJU-AI4Science/issues/52)） | 主人指出 CLI 上一堆没归类的动作，要求按纲领每样要么是能力要么是键要么是查询 | 主人 + Claude |
| 2026-09-17 | 加 R-21：能力归到科研阶段下（[#53](https://github.com/zephyr4123/TJU-AI4Science/issues/53)） | 主人提出「模块 → 能力包 → workflow」三层；对齐后模块定名为阶段，反向归属不存只算 | 主人 + Claude |
