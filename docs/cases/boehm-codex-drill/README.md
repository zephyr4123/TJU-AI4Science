# boehm-codex-drill · 参数拟合（两层都换成 Codex 的演练）

平台第一次两层（研究助理 + 执行层）都换成 Codex 跑通研究流全链：研究者 9 句话、两次签字；助理自己写需求、起设计、修执行层的脚本错、跑三轮自动搜索、写分析、核数字、给交付摘要。2026-09-22，外层 [#135](https://github.com/zephyr4123/TJU-AI4Science/issues/135)（伞 [#130](https://github.com/zephyr4123/TJU-AI4Science/issues/130) 底座归人，纲领 P-25）。

- 任务类型：**连续参数优化**——9 个参数在 log10 尺度、边界 1e-5 到 1e5，目标函数是 PEtab 的负对数似然（NLL），方向 minimize
- 应用领域：系统生物学
- 案例类型：平台演练（Claude 扮水平一般、只会说「你看着办」的研究者；主人当维护者，只修平台不喂答案；**两层底座都是 Codex**：codex-cli 0.147.0、gpt-5.6-terra、medium，ChatGPT Plus 订阅）
- 来源：PEtab benchmark 的 Boehm 2014 STAT5 模型，与材料卡 [boehm-stat5-petab](../boehm-stat5-petab/) 同一份材料
- 状态：**验收已签**（`verification/1`，2026-09-22 13:16）
- 喂给哪一层：研究流全链（需求 → `design` → 断点 → `auto-research` → `analysis` → `verify` → 验收）+ Codex 适配器（[#131](https://github.com/zephyr4123/TJU-AI4Science/issues/131)）+ 设置与自检（[#132](https://github.com/zephyr4123/TJU-AI4Science/issues/132) [#133](https://github.com/zephyr4123/TJU-AI4Science/issues/133) [#134](https://github.com/zephyr4123/TJU-AI4Science/issues/134)）

## 结论一句话

PEtab 包自带的标称参数就在这份数据的最优点旁边：基线从 138.222035 降到 138.221929（三个种子一个数，σ = 0），三轮自动搜索（拉长截止、放大差分步长、换 Powell）没有一轮过 0.1 的门，最终交付的就是基线参数。执行层没记优化器的停止原因，助理在交付摘要里写「收敛状态未记录、无法审计」，没有编一个「已收敛」。

## 数字

基线（`baseline/`，种子 42 / 43 / 44 三个数完全一样）与三轮搜索（`ledger.tsv`、`notebook.md`）：

| 轮 | 改了什么 | NLL | 相对基线 | 用时 | 裁决 |
|---|---|---|---|---|---|
| 基线 | L-BFGS-B，从标称值起，60 秒预算 | 138.221929 | — | 45.9 s | — |
| 1 | 优化截止从预算的 80% 放到 95% | 138.221929 | 0 | 46.8 s | discard：分数一模一样，改动多半没生效 |
| 2 | L-BFGS-B 的 `eps` 放大到 1e-3 | 138.222012 | 变差 8.3e-5 | 3.5 s | discard |
| 3 | 换成有边界的 Powell | 138.221918 | 好 1.1e-5 | 3.8 s | discard：没过 0.1 的门 |

交付的 9 个参数（`baseline/diagnostics.json`）：动力学 6 个 + 噪声 3 个，全在边界内，PEtab `estimate=1` 的名单与优化问题里的名单一致（执行层按助理的要求留了这份对照）。

## 时间线（本机时间，2026-09-22）

| 时刻 | 谁 | 发生了什么 |
|---|---|---|
| 12:15 | 研究者 | 「有一个细胞信号的模型，想把参数拟合出来，文件都放 materials 里了」 |
| 12:16 | 研究者 | 「同事给的标准格式，好像叫 PEtab，Boehm 2014 那个 STAT5」→ 助理写需求初稿 |
| 12:22 | 平台 | **坑 1**：Codex 助理照指南「只能运行 ai4sci」办，连 `materials/` 都不敢 `cat`，需求写成「后续再读」。修：端口加 `tool_guide`，指南变了塞进下一轮；助理这才读完 PEtab 文件补全需求（47 条测量、9 个参数、边界、固定参数） |
| 12:24 | 研究者 | 「我确认了」→ **坑 2**：确认被模板引言里的「待填」两个字拦下。修：只查格子 |
| 12:26 | 研究者 | 「我在页面上确认了」→ 助理 `cap design --flow research --detach` |
| 12:27 | 平台 | **坑 3**：作业里嵌套的执行层 codex 401「Missing bearer」。根因：作业继承了协调层的 `CODEX_HOME`（私有 home），auth.json 软链指到了自己。修：算「真」home 时忽略私有根下的候选 |
| 12:35 | 研究者 | 「好像失败了？页面上那个设计写着失败」；12:36「管理员说修好了，你再试一次」 |
| 12:39 | 平台 | **坑 4**：执行层什么都没写：`apply_patch` 被沙箱拒（Operation not permitted）。根因：作业在协调层的 `workspace-write` 沙箱里起，里面的执行层 codex 再开一层沙箱，嵌套走不通。修：`ai4sci` 靠 execpolicy 规则在沙箱外跑，其余命令留在沙箱里 |
| 12:51 | 平台 | **坑 5**：改了 home 布局，老对话 `resume` 报 no rollout found。修：协调层 home 留在根 |
| 12:52 | 研究者 | 「又失败了，说什么写权限被拒。管理员说这次真修好了」→ 助理重起 design |
| 12:56 | 平台 | **坑 6**：清单里的缺省算力是关了机的 AutoDL，SSH 超时被报成「平台内部错误…这是平台的 bug」。助理自己看懂了，换 `--compute local` 重跑，没来问人。修：`ComputeError` 报「算力不可用，换 `--compute <名字>`」 |
| 12:58 | 执行层 | 壳写成了（scoring.yaml + harness 封好，lint / validate 0），基线脚本自己 `raise`：把 PEtab 返回的参数顺序当契约核对 |
| 12:58–13:07 | 助理 | 三次 `--continue --feedback`（`feedback/`）：顺序断言改集合断言 → 导入路径与参数名对照、留诊断 → ruff B009 的 `getattr` 改直接属性；第 7 次 design 成了，基线三个种子 45.9 s |
| 13:08 | 助理 | 报评分与基线：9 个参数、边界、预算、σ = 0、门槛 0.1，请签 |
| 13:09 | 研究者 | 签 `design/1`；「初值本来就是论文里的最优值吧，再搜还能有多大改善？先跑跑看」 |
| 13:10–13:13 | 助理 | `cap auto-research --max-iters 3 --compute local`，三轮无一保留（batch_exhausted） |
| 13:13–13:14 | 助理 | `cap analysis`（12 个数）→ `cap verify` PASS（4 项）→ 报参数表，请签验收 |
| 13:15 | 研究者 | 「分析里写着收敛状态账本没记、验收项未决，那到底收敛了没？参数表加拟合优度摘要一起给我」 |
| 13:16 | 助理 | 交付摘要一张表：NLL、相对下降、用时、边界、模拟有限值、搜索结果，**收敛状态「未记录，无法审计」**；研究者签 `verification/1` |

从第一句话到验收 61 分钟，其中 12:27–12:56 约半小时是维护者在修坑（研究者两次被告知「管理员修好了」）；去掉修坑，链路本身约半小时。

## 撞了什么坑、平台怎么修（都在内仓 `codex` 分支，CHANGELOG 有条目）

| 坑 | 是谁的 | 修法 | issue |
|---|---|---|---|
| 助理不敢看 `materials/`（Codex 只有 shell，指南写的是 Claude 的 Read / Grep） | 适配器 | 端口 `Chat.tool_guide()` 各家自己说「工具怎么用」；指南只在开线程时送到的 CLI，指南变了框架把全文塞进那一轮 | #131 |
| 需求确认被模板引言的「待填」拦 | 平台 | 只查二级标题下的格子 | #135 |
| 作业里嵌套的执行层 codex 401 | 适配器 | `CODEX_HOME` 落在私有根下的不当「真」home，auth.json 软链不再指向自己 | #131 |
| 嵌套沙箱里执行层写不进自己的可写根 | 适配器 | `ai4sci` 靠 execpolicy `prefix_rule(decision="allow")` 在沙箱外跑，其余命令留在 `workspace-write` 里；端口删 `runtime_paths`，不再 `--ignore-rules`、不再开网络 | #131 |
| 改 home 布局后老对话 no rollout found | 适配器 | 协调层 home 就是根、执行层 `executor/` | #131 |
| 缺省算力关了机，SSH 超时报成「平台内部错误」 | 平台 | `cap` 里 `ComputeError` 单独一条：算力不可用、换 `--compute` 或先 `compute check`，退出码 1 | #135 |
| `--continue` 续跑时 meta 还挂着上一次的错、结论、机器（本机跑着，看板写 autodl） | 平台 | `outputs.reopen_output` 一次清干净，机器按这次的记 | #135 |

执行层自己的三次脚本错（顺序断言、导入核对、lint）不算平台的坑：助理三次 `--feedback` 都诊断对了，这是链路该有的样子。

## 这次演练说了 Codex 什么

- 协调层 21 轮全在一条线程上 `resume`，没丢过一次记忆；线程累计输入 3.66M token（95.6% 命中缓存）、输出 16.6k；每轮 12–46 秒。
- 执行层 9 次会话（design 5、实验 3、分析 1）：输入 2.27M（约 2.0M 缓存）、输出 38.5k。订阅账号没有美元数，全程 `cost_usd=nan`。
- 助理每一轮都先 `show job` / `show output` 再开口，回话比 Claude 的短、像汇报；研究者两次追问（初值是不是最优、收敛了没）都答得实在。
- 执行层第一版壳写了五个文件自述「未运行验证」，跟 Claude 执行层一个毛病；`getattr(obj, "常量")` 被 ruff B009 拦是 Codex 的手笔。三轮改法都是 `fit_boehm.py` 里三行以内，第 1 轮改了等于没改，账本把它标了出来。
- 第 2、3 轮 3 秒就跑完，60 秒预算没用上；不是坑，但「把预算用满」得执行层自己盯。

## 成本

- 模型：ChatGPT Plus 订阅，不按 token 计费；上面的 token 数是 Codex 事件里的 `usage` 原样。
- 算力：本机 CPU，基线 46 秒 × 3 个种子，三轮搜索 54 秒。
- 人：研究者 9 句话、两次签字；维护者修了 7 个坑、没碰工作区。

## 保留意见

- 基线就是最优点：这道题验的是链路和适配器，不是搜索能力（之前的任务包 `boehm-nll` 从随机起点出发才有 keep）。
- 需求「交付」要的「收敛状态」到验收时仍是「未记录」：平台 `results.json` 的契约只有指标、用时、种子、状态，优化器的停止原因这类领域诊断靠执行层自觉。要不要进契约，下一轮再定。
- 7 个坑里 5 个是 Codex 适配器第一次接才撞的（认证、沙箱、线程、指南通道），2 个是平台通用的（确认、续跑 meta）加 1 个报错措辞；冷启动自检（`ai4sci check`、设置板）在演练前跑过都过，演练里没撞「没装 / 没登录」。
- 研究者由 Claude 扮，问题比真人问得准（「收敛了没」）；真人未必会追这一句。

## 目录

| 文件 | 是什么 |
|---|---|
| `requirement.md` | 研究者确认的需求 v1（助理起草） |
| `flow.yaml` | 取到工作区的研究流程实例 |
| `scoring.yaml`、`harness/` | 执行层写的壳：评分契约（门 0.1、三个种子、60 秒）、`launcher.sh`、`make_run0.sh`、`evaluate.md`（evaluate.py 原文放代码块里：外层仓不放 .py）、`SHA256SUMS` |
| `code/fit_boehm.md` | 拟合脚本原文（pyPESTO + libRoadRunner，L-BFGS-B，参数名对照诊断） |
| `baseline/` | 三个种子的结果、σ、9 个参数与名单对照 |
| `feedback/` | 助理三次喂回执行层的意见原文 |
| `ledger.tsv`、`notebook.md` | 三轮搜索的账本与执行层的笔记（假设 / 改动 / 预期 / 裁决） |
| `analysis.md` | 分析初稿（12 个数全部回溯到结果） |
| `report.json` | 数字核对报告（PASS，4 项） |
| `transcript.md` | 整段对话：研究者每句话、助理每轮回话、框架的叫醒；两次塞进来的指南全文略去 |

主机、端口、本机路径按红线抹成 `<autodl-host>`、`<port>`、`<workspace>`、`<repo>`。原件不进 git：PEtab 包九个文件与 sha256 见 [boehm-stat5-petab](../boehm-stat5-petab/README.md) 的原件索引；工作区全貌（七次 design 作业、执行层每次会话的事件流与 stderr）在本机 `materials/home/workspaces/boehm-codex/`。
