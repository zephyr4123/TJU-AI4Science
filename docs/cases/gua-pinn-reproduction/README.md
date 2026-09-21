# gua-pinn-reproduction · 论文复现（一级）

平台第一次完整跑通的复现：一个只丢了链接、说「听你的」「我不会命令行」的研究者，研究助理自己找代码、拉、写壳、在 4090 上跑、与论文值并排、写复现性分析、核对数字，研究者签了两次字。2026-09-21，外层 [#120](https://github.com/zephyr4123/TJU-AI4Science/issues/120)。

- 任务类型：**论文复现，一级**——官方代码 + 官方附带的数据 + 论文的种子 {0,1,2,3,4} 原样重跑，检验「结果可重跑」
- 应用领域：计算物理（PDE 求解 / 物理信息神经网络）
- 案例类型：平台演练（Claude 扮水平一般、问题模糊的研究者；主人当维护者，只修平台不喂答案）
- 来源：第三方论文 arXiv [2609.01558](https://arxiv.org/abs/2609.01558)「Gradient–Update Mismatch: Rethinking Conflict-Free Training of Physics-Informed Neural Networks」（2026-09-01），代码 <https://github.com/JingXiao10/GUA>（MIT）
- 状态：**已复现，验收已签**（`verification/4`，2026-09-21 15:43）
- 喂给哪一层：复现那条流程（纲领 P-24）全链——文献 → `reproduction` → 断点 → `reproducibility` → `verify` → 验收

## 结论一句话

用官方代码（一字未改）、官方数据、论文种子，在同款 RTX 4090 上原样重跑，Burgers · 2-loss 下 ConFIG 与 ConFIG+GUA 两行都落在论文均值 ± 2σ 内，加 GUA 误差降 62.2%（论文 62.6%），五个种子无一反例。两个均值都比论文高一成左右，最可能是 torch 2.8 对论文的 2.12；下一步只换这一项验。

## 论文值 vs 我们的值

表 8（附录 C.4.1）Burgers · 2-loss 列，相对 L2 误差，五个种子的均值 ± 样本标准差：

| 方法 | 论文 | 我们 | 论文 ± 2σ | 落在范围内 |
|---|---|---|---|---|
| ConFIG | 1.74e-3 ± 3.38e-4 | 1.94e-3 ± 3.3e-4 | 1.06e-3 ~ 2.42e-3 | 是 |
| ConFIG + GUA | 6.50e-4 ± 1.27e-4 | 7.33e-4 ± 1.8e-4 | 3.96e-4 ~ 9.04e-4 | 是 |
| 加 GUA 的改进 | 62.6% | 62.2% | — | 方向一致 |

每个种子（`baseline/`，每份 `results.json` 一行；一个种子两个变体约 32 分钟）：

| 种子 | ConFIG | ConFIG + GUA |
|---|---|---|
| 0 | 2.33e-3 | 7.69e-4 |
| 1 | 2.16e-3 | 6.70e-4 |
| 2 | 2.00e-3 | 6.29e-4 |
| 3 | 1.66e-3 | 5.74e-4 |
| 4 | 1.54e-3 | 1.02e-3 |

平台自己的 σ（`baseline/sigma.json`）按重复的四个种子 1–4 算：ConFIG 2.9e-4、GUA 2.0e-4；上表的 ± 是五个种子一起算的，两种口径都对，分析里写明了。

## 时间线（本机时间，2026-09-21）

| 时刻 | 谁 | 发生了什么 |
|---|---|---|
| 12:18 | 研究者 | 「我有一篇论文 … 你帮我复现一下」 |
| 12:20 | 助理 | `show templates` 找到复现模板 → pdf skill 解析论文 → 在论文里 grep 表与训练设置 → 从摘要的链接读仓库 README → 写需求初稿，问四件事（为什么、哪几行、几级、对上的标准）+ 有没有机器 |
| 12:25 | 研究者 | 「听你的」+ 新 AutoDL 的 ssh 一行 + 「今天下午、一百块」；助理 `compute add` 接机器、`env use` 用镜像自带的 conda base、补完需求；研究者确认 v1 |
| 12:26 | 助理 | `flow take reproduce` → `download git` 拉到 commit `8bbbcd5` → 手写 `literature/1/sources.md` → `cap reproduction --code GUA --compute autodl --detach` |
| 12:33 | 平台 | 执行层 30 轮用完（读完 79 个文件、写完四个文件、没来得及自述）→ 助理看日志、发现草稿种子 42–46 应为 0–4，`--continue --feedback` 改第二版 |
| 12:35 | 平台 | 第二版过合规、连上 4090，`import scipy` 炸：镜像环境缺仓库要的九个包。助理让研究者登录机器 pip、又教他去网页终端粘命令 |
| 12:43 | 研究者 | 「我不会命令行」「再看看平台上有没有别的办法」→ 助理重翻 `ai4sci --help`，发现刚加的 `env add`，一次装好、`--continue design/1` 接着跑 |
| 12:46–15:25 | 4090 | 五个种子 × 两个变体，2 小时 40 分 |
| 15:25 | 助理 | 论文值 vs 我们的值并排、每个种子的数、改动 = 0，停在断点请签 |
| 15:26 | 研究者 | 签 `design/1` → 助理 `cap reproducibility` |
| 15:29 | 助理 | `verify` PASS；通读发现两处文字错（编了论文里没有的 Allen-Cahn；「单 loss」应为 3-loss），问要不要重写 |
| 15:31–15:41 | 助理 | 第二版超参裸写被数字核对拦、第三版「1.84 倍」被拦；发现 `--feedback`，把三版问题一次喂回，第四版三关全过 |
| 15:43 | 研究者 | 签 `verification/4`。助理提醒去关 AutoDL |

## 助理自己找到的 vs 预筛的答案卷

选论文之前，维护者派了三个读者核实过材料（不喂给助理）。对照：

| 项 | 答案卷 | 助理自己得出的 |
|---|---|---|
| 代码仓库 | JingXiao10/GUA，MIT，数据随仓库 | 同，从摘要链接读到；拉到 commit `8bbbcd5`，收据留档 |
| 要复现的数 | 表 8 Burgers 2-loss：1.74e-3 / 6.50e-4，5 种子均值±σ | 同，从 `structured.json` 抄，并说了理由（只训 3 万轮、ConFIG 是主基线） |
| 运行命令 | `trainer.py --equation burgers --method config --n-losses 2 --optimizer-correction none\|gua` | 同，launcher 原样起两个变体 |
| 产物 | `formal_metrics.json` 有 `relative_l2` | 同，evaluate 读它，不信 stdout |
| 坑：单种子波动 19% | 写「落进误差带」或跑满 5 种子 | 自己提了 ±2σ、跑满 5 种子、时间不够减 3 种子的退路 |
| 坑：README 钉 torch 2.12，镜像是 2.8 | torchjd 只要 ≥2.3，用镜像的 | 用了镜像的，把版本差写进需求、分析归因到它 |
| 坑：镜像缺 scipy / torchjd | — | 撞上了；平台补了 `env add` 才过 |

## 撞了什么坑、平台怎么修（都进了内仓 `reproduce` 分支）

| 坑 | 修法 | issue |
|---|---|---|
| 执行层缺省 30 轮不够读别人的仓库；`cd &&`、`mkdir`、`awk` 三条 Bash 被拒白耗 | 会话额度按能力给（`reproduction` 80 轮 / 6 美元）；执行层提示加「读文件用 Read / Grep，Bash 只放行 ai4sci skill」 | #122 |
| 镜像环境缺包，助理只能让研究者登录机器 | `ai4sci env add --compute <名字> --from <requirements.txt>`；`--continue` 刷新快照不重写壳 | #128 |
| 人打断留下对话死锁 | 锁记 pid，进程没了自己收 | #129 |
| 平台中途加了命令，助理照上一轮记忆答「做不了」 | 指南指纹记进对话，变了在下一轮话前提醒 | #129 |
| 分析把超参、「1.84 倍」写在正文被数字核对拦；第一版编了个方程名；重写不知道上一版错在哪 | 提示：凡不是从结果清单抄的数写反引号、倍数只许整数、文字事实照材料抄；`reproducibility --feedback` | #123 |
| 助理把意见文件写进了 `analysis/3/executor/`（冻住的产出） | 指南：意见放 `materials/` 或 `.ai4sci/` | #123 |

## 成本

- 对话 15 轮（含 6 轮框架叫醒）：$7.41；执行层 6 次会话：$3.02（其中一次撞轮数上限 $1.44）。合计约 **$10.4**。
- GPU：AutoDL RTX 4090，基线 2 小时 40 分，加两次没跑成的几分钟；按小时计费，研究者自己在控制台核。
- 人：研究者 8 句话、两次签字；维护者中途修平台，没碰工作区。

## 保留意见

- 这篇是预筛过的「好材料」：数据在仓库里、一条命令、MIT、单卡半小时。被预筛掉的三篇（数据链接死、README 命令跑不起来、权重与测试集重叠）才是复现里更常见的坑，还没考。
- 执行层写分析会编文字事实（方程名），数字核得住、文字核不住，靠助理通读兜底；四版才过。
- 「对上」是研究者按需求里的标准判的，平台只把两列数摆出来（主人：前期别把机器校验卡太死）。

## 目录

| 文件 | 是什么 |
|---|---|
| `requirement.md` | 研究者确认的需求 v1（助理起草） |
| `sources.md` | 文献阶段主文件：材料来源（助理手写） |
| `flow.yaml` | 取到工作区的流程实例 |
| `scoring.yaml`、`harness/` | 执行层写的壳：评分契约（`attainable` = 论文值）、`launcher.sh`、`make_run0.sh`、`evaluate.md`（evaluate.py 原文放代码块里：外层仓不放 .py） |
| `upstream.json` | 上游代码的出处与 commit；`upstream.diff` 为空（一字未改），没抄 |
| `baseline/` | 五个种子的结果与 σ |
| `analysis.md` | 复现性分析（第四版，过核对与通读的那份） |
| `report.json` | 数字核对报告（PASS，14 个值） |
| `transcript.md` | 整段对话：研究者的每句话、助理的每轮回话（工具调用在工作区的 `trace.jsonl` 里，没抄） |

主机名、端口、本机路径按红线抹成 `<autodl-host>`、`<port>`、`<workspace>`。原件不进 git：

- 论文 PDF：`materials/paper/source.pdf`，sha256 `a94ba00cfee6adb284419cf4cd76bc692ec5372ff29a8416b3e1054cab1975e9`，1,015,750 字节；重取 <https://arxiv.org/pdf/2609.01558>
- 代码：`materials/GUA/`，`git clone https://github.com/JingXiao10/GUA && git checkout 8bbbcd545436493602bb82a91d08afb449b5b750`
- 工作区全貌（含四版分析、三次失败的作业、执行层日志）在本机 `materials/home/workspaces/gua/`
