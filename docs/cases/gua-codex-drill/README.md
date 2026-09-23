# gua-codex-drill · 论文复现（两层都是 Codex，在项目层与新页面上，没跑到底）

第三轮演练：项目层（[#136](https://github.com/zephyr4123/TJU-AI4Science/issues/136)）落地后，两层（研究助理 + 执行层）都换成 Codex，研究者在**网页**（项目页正中间那只对话框）上把 [#120](https://github.com/zephyr4123/TJU-AI4Science/issues/120) 那篇论文再复现一遍，机器换成新克隆的 AutoDL（RTX 5090）。2026-09-22 23:37 起、23 日 04:00 止，外层 [#137](https://github.com/zephyr4123/TJU-AI4Science/issues/137)。

- 任务类型：**论文复现，一级**——官方代码 + 官方数据 + 论文种子原样重跑
- 应用领域：计算物理（PDE 求解 / 物理信息神经网络）
- 案例类型：平台演练（Claude 扮水平一般的研究者；主人当维护者只修平台不喂答案；**两层都是 Codex**：codex-cli 0.147.0、gpt-5.6-terra、medium，ChatGPT 订阅）
- 来源：arXiv [2609.01558](https://arxiv.org/abs/2609.01558)，代码 <https://github.com/JingXiao10/GUA>（commit `8bbbcd5`，与 #120 同一个）；材料与答案卷见 [gua-pinn-reproduction](../gua-pinn-reproduction/)
- 状态：**没跑到底**——需求已签、壳写好、基线两次起跑：第一次跑完 2 h 38 min 被一个 JSON 细节拒了，第二次从头再跑到一半机器 04:00 定时关机（主人估四小时够、设了自动关机）。主人 04:20 拍板「结果就这样吧」，不再重跑
- 喂给哪一层：复现流（文献 → `reproduction` → 断点）+ 项目层的页面与 CLI（`--ws`、收件箱叫醒）+ Codex 适配器

## 结论一句话

助理这一层 Codex 比上一轮的 Claude Code 快得多、省得多（8 轮合计 7 分钟出头，执行层 4 分钟写完壳），流程走法与 #120 那轮几乎一样；输掉的不是模型，是平台的四个坑（探测结果不带解释器路径、复现种子被平台换成 42–46、σ 让执行层自己算、continue 抹掉上一版基线）加一次定时关机。四个坑修了三个根因（已合入内仓 main），`--continue` 抹掉上一版基线记债；Codex 自己的短板是撞墙不重探、凭上一轮的记忆答「做不了」，以及两次叫醒都没认出种子不对。

## 时间线（本机时间）

| 时刻 | 谁 | 发生了什么 |
|---|---|---|
| 22 日 23:37 | 研究者 | 首页「新建项目」→ 项目页正中间那只框：「我有一篇论文 … 你帮我复现一下」 |
| 23:39 | 助理 | 2 min：`show templates` → 建工作区 `pinn-reproduction`（复现模板）→ pdf skill 解析论文 → **web_search 核仓库与许可证** → rg 表 8 → 写需求初稿，问范围与预算；**没问机器** |
| 23:40 | 研究者 | 「听你的，先做最小的」+ 新 AutoDL 的 ssh 一行 + 「今晚跑完、一百块以内」 |
| 23:41 | 助理 | `compute add seetacloud` 一次接上（5090、50 GB、镜像 conda base），建议用现成环境 |
| 23:41 | 研究者 | 「行，用现成的」 |
| 23:42 | 助理 | `env use` 要解释器绝对路径，探测那一行没打出来，猜 `/opt/conda/bin/python` 猜错 → 让研究者上机器跑 `which python`（**坑 1**） |
| 23:44 | 研究者 | 「我不会命令行，平台上有没有别的办法？」→ 助理 13 s、一条命令没跑：「平台没有这个功能」 |
| 23:45 | 研究者 | 「刚才你不是说机器可用、有现成环境吗？再看看那台机器」→ 助理重跑 `compute check`（维护者已修，这回带路径）→ `env use` 成，冻结 131 个依赖 |
| 23:47 | 研究者 | 工作区页看板上署名「小黄」按「确认」→ 需求 v1；对话板里说「我确认了，开始吧」 |
| 23:48 | 助理 | `flow take reproduce` → `download git` 到 `8bbbcd5` → 手写 `literature/1/sources.md` → `cap reproduction --from literature/1 --code gua --compute seetacloud --detach` |
| 23:52 | 执行层 | 4 min、9 条命令读完仓库、写 `scoring.yaml` + 三个壳，`code/` 一字未改，lint / 校验一次过；自述里写「注意平台强制的 42–46 种子与论文 0–4 不一致」但照办（**坑 2**） |
| 23:53–02:32 | 5090 | 5 种子 × 2 变体，每个变体 15 min（GPU 利用率 6%，和 4090 一样快），2 h 38 min |
| 02:32 | 平台 | 框架校验拒了：`sigma.json` 的 seeds 写成 42–46（连基线），要的是只有重复的 43–46（**坑 3**）；design/1 failed，结果进收件箱叫醒助理 |
| 02:32 | 助理 | 35 s：`show output` + `show job` 读错误 → `cap reproduction --continue design/1 --feedback "只修汇总…"`；执行层 36 s 改好 make_run0.sh；但 continue 把本地和远端的 baseline/ 都删了从头再训（**坑 4**） |
| 04:00 | AutoDL | 定时关机；第二跑到 seed 44；作业「算力不可用」→ 叫醒 |
| 04:00 | 助理 | 24 s：`compute check` 探不到 → 「实例已关机或重启后端口变了，把新 ssh 地址发我」；又说「无需重训已有的 4 个结果」（错：已被 continue 抹掉） |
| 04:20 | 主人 | 「结果就这样吧」 |

研究者说了 7 句话、签了 1 次字（看板上）。助理 8 轮：118 / 58 / 46 / 13 / 53 / 84 / 35 / 24 秒。

## 和 #120（Claude Code）那一轮并排

| 项 | #120 Claude Code（助理 + 执行层 Sonnet · medium） | 这一轮 Codex（gpt-5.6-terra · medium） |
|---|---|---|
| 入口 | 终端 `chat send` | 网页项目页 → 整屏对话 → 工作区页看板签字，对话板接着说 |
| 第一轮 | 找论文、仓库、表 8，问四件事 + 有没有机器 | 同，多了 web_search 核仓库与许可证；没问机器 |
| 需求初稿 | 一版补完 | 一版就带「怎么算对上」（±2σ 且相对差 ≤ 20%）、材料、环境策略；多加一个指标「GUA 后冲突率为 0」（研究者没要求，论文里的主张） |
| 接机器 | `compute add` + `env use` 一次过 | `compute add` 过；`env use` 猜路径猜错，两轮才过（坑 1，平台的） |
| 执行层写壳 | 30 轮额度用完没自述、第二版才过；壳里种子 42–46，助理看日志发现后 `--continue --feedback` 改成 0–4 | 4 min、9 条命令一次过；壳里种子 42–46，自述里点了不一致，助理两次叫醒都没认出来 |
| 第一次上机器 | `import scipy` 炸，镜像缺九个包，逼出 `env add` | 克隆机上一轮装的包还在，一次跑起 |
| 基线 | 4090，2 h 40 min，过校验 | 5090，2 h 38 min，被 sigma.json 的 seeds 拒（坑 3） |
| 叫醒后 | — | 35 s 读错误、下判断、发 continue；24 s 判断机器关了 |
| 结果 | 两行都在 ±2σ 内，验收已签，3 h 25 min | 没有数 |
| 成本 | $7.41 + $3.02 | 订阅，报不出美元；执行层一次会话输入 718k token（644k 缓存命中）、输出 11k |

## 主人要验的三件事

1. **Codex 和 Claude Code 有没有差距**：每一轮都更快更省，需求初稿质量更高，执行层一次过；差在自我恢复——撞墙不重探（`env use` 失败后没再 `compute check`，研究者追问才做）、凭上一轮的记忆下「平台没这功能」的结论；两次叫醒都盯着错误信息，没把需求里的「种子 0–4」和壳里的 42–46 对起来（Claude 那轮是助理自己从日志里看出来的）。
2. **trajectory 合不合理、有什么涌现**：走法和研究助理指南一致（模板 → 工作区 → pdf → 需求 → 机器 → 环境 → 页面确认 → 流程 → download → sources → cap --detach），没有一步绕开平台；涌现三处——第一轮就用 web_search 核仓库与许可证；需求里自己加了「GUA 后冲突率为 0」这个论文主张当第三个指标；执行层把 ConFIG 对照组放进同一个 launcher 的内循环，一次种子两行数。叫醒后的反应快且准，措辞给人看得懂。
3. **项目 / 工作区重组后的边界**：都通——对话在项目层，工作区级命令全带 `--ws`，Codex 一次没漏；`flow take --ws`、`output new --ws`、`cap --ws --detach`、收件箱叫醒两次都到；页面上项目页 → 整屏对话 → 工作区页看板签字 → 右边对话板接着同一段对话，没有断层。顺手修了页面四处：Codex 的工具行只写「shell」、web_search 一直转「运行中」、签完需求页眉还写「需求未确认」、需求里网址吞了「）。」。

## 撞了什么坑、平台怎么修（都已合入内仓 main，每个有单测）

| 坑 | 根因 | 修法 |
|---|---|---|
| 1 助理拿不到现成环境的解释器路径 | 探测早就盘点到 `/root/miniconda3/bin/python` 写进了 computes.yaml，打出来的「已有环境」那一行漏了路径；`env use` 却只认路径 | 那一行带路径：`conda base /root/miniconda3/bin/python 3.12.3 torch 2.8.0+cu128 cuda` |
| 2 复现的种子被换成 42–46 | reproduction 的执行层提示词从研究流抄的「缺省 42、重复 43、44…」 | 种子照论文：`AI4SCI_SEED` 缺省论文第一个种子、`repeat_k` = 论文种子数 − 1，明说不许换成平台的 |
| 3 基线 2 h 38 min 被 sigma.json 的 seeds 拒 | σ 让执行层自己算、自己写，提示词没说 seeds 只列重复的那几个 | **σ 由框架算**：跑完 make_run0.sh 后 `pack.write_sigma` 从 repeats/ 算样本标准差写 sigma.json，脚本算的一律覆盖；两份提示词删掉那 20 行 Python |
| 4 continue 只改汇总也从头再跑，还抹掉上一版结果 | `run_baseline` 起跑前 `rm -rf baseline/`，远端脚本也 rm | 坑 3 修了这个场景不再出现；「continue 复用已有 results」记成债，没修 |
| 页面四处 | 见上 | Codex 工具行显示命令（剥 `/bin/zsh -lc` 壳）、web_search 后端配成一对、页眉状态照工作区自己那份、自动链接结尾的中文标点挪出去 |

## 留着的债

- `--continue` 只改壳不动训练时应复用已有的 `baseline/`，不该 rm 了从头跑。
- 助理撞墙后不重探：指南指纹提醒（#129）只管指南变了，管不了「命令的输出变了」。
- 老的 `autodl` 算力条目还是缺省，机器早没了；`compute add` 新名字不会自动改缺省。
- 5090 上 GPU 利用率 6%，和 4090 一样每变体 15 min：这份代码的瓶颈在 Python 循环，租更贵的卡没用——下次租机建议写进指南。

## 复跑怎么接

机器开好（端口会变）→ 研究者把新 ssh 行贴给助理 → `compute add` 同名覆盖 → `cap reproduction --continue design/1`（新提示词：种子 0–4、σ 框架算）→ 断点核对 → `reproducibility` → `verify` → 验收。项目 `pinn`、对话与 design/1（failed）都留在数据根里。

## 目录

- `requirement.md`：签了字的需求 v1（助理写的，主机端口路径已抹）
- `sources.md`：文献阶段助理手写的材料来源
- `scoring.yaml`、`harness/`：执行层写的评分契约与三个壳（`evaluate.md` 是 evaluate.py 原文的代码块，外层仓不放 .py）；`make_run0.sh` 是第一版，种子 42–46、自己算 σ——正是坑 2 与坑 3
- `executor-session-1.md`：执行层第一次会话的命令与自述、token 用量
- `transcript.md`：整段对话八轮（含框架两次叫醒的原文），主机端口路径已抹，指南全文略去
