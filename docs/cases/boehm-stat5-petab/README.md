# boehm-stat5-petab · 常微分方程参数优化

- 任务类型：**连续参数优化**。9 个参数在 log10 尺度上搜索，边界 1e-5 到 1e5，目标函数是负对数似然（NLL），方向 minimize
- 应用领域：系统生物学。这是第三方 benchmark 的背景
- 案例类型：调参型（[#1](https://github.com/zephyr4123/TJU-AI4Science/issues/1) 的「案例二 · 日常在跑的参数实验」）
- 状态：**已接入 → `platform/projects/boehm-nll/`**（[#40](https://github.com/zephyr4123/TJU-AI4Science/issues/40)），基线与 σ 已出
- 现名对照（2026-09-23）：这张卡写于 2026-09-16，正文按当时的记录封存——「任务包 `tasks/<name>`」现在是项目里的工作区 `projects/<p>/workspaces/<p>/`，「run_0」是设计产出的 `baseline/`，「manifest」是 `scoring.yaml`，「`ai4sci task design`」是 `ai4sci cap design`，σ 由框架算
- 喂给哪一层：实验内环——决定 harness 长什么样、指标能不能压成一个数、噪声多大
- 原文：[questionnaire.md](questionnaire.md)

## 为什么选它

Q-5 对真任务提了三条要求，这道题三条全中：

1. 一次跑完是秒级到分钟级，普通 CPU 即可，不需要 GPU。
2. 主指标是单一标量 NLL，方向明确 minimize。
3. 基线是社区标准流程（pyPESTO multi-start），单入口能整理出来。

额外的好处是它用 PEtab 标准格式：参数边界、观测公式、噪声模型、测量数据全在 tsv 与 SBML 里声明好了，问题定义不用我们自己写，省掉「写 evaluate.py 时把判分标准写歪」这个最大的风险点。

## 来源与署名

不是学长自己组里的工作，是社区 benchmark 集里的一道题。

- benchmark 仓库：<https://github.com/Benchmarking-Initiative/Benchmark-Models-PEtab>
- 案例目录：`Benchmark-Models/Boehm_JProteomeRes2014/`
- 原论文：Boehm ME, Adlung L, Schilling M, et al. Journal of Proteome Research, 2014. <https://pubmed.ncbi.nlm.nih.gov/25333863/>（德国癌症研究中心 DKFZ）
- 求解工具：[pyPESTO](https://pypesto.readthedocs.io/)

## 问题规模

以下数字是读 `materials/boehm-stat5-petab/` 解压后的 tsv 核对出来的，不是转述学长的话：

| 项 | 值 | 出处 |
|---|---|---|
| 待优化参数 | 9 | `parameters_*.tsv` 里 `estimate=1` 的行 |
| 固定参数 | 2 | `ratio` = 0.693，`specC17` = 0.107，`estimate=0` |
| 观测量 | 3 | `observables_*.tsv` |
| 测量点 | 48 | `measurementData_*.tsv` 数据行 |
| 实验条件 | 1 | `experimentalCondition_*.tsv`，条件名 `model1_data1` |
| 参数尺度 | log10 | 除两个固定参数是 lin |
| 噪声模型 | normal | 三个 σ（`sd_pSTAT5A_rel` 等）本身也是待优化参数 |

benchmark 仓库 README 的表格给的是 9 个参数、48 个测量点、3 个观测量，与实际文件一致。学长问卷里说的三个数也对得上。

## 基线与最优值（2026-09-16 本机实测）

学长只说「用 pyPESTO 默认 multi-start 得到的初始优化结果作为 baseline」，没给数。实测：

| 项 | 值 | 怎么来的 |
|---|---|---|
| 名义参数处 NLL | 138.2220 | 探针直接计算，这就是文献里的公认最优值 |
| 单次优化（5 个均匀随机起点，scipy L-BFGS-B） | 147.8 ～ 249.7 | 学长的默认流程，结果全看起点运气 |
| 主指标 `nll_mean`：3 个内部 seed 各优化一次取均值 | 基线 run_0 **224.74**（seed 42） | harness 内算，code/ 只产单次的参数向量 |
| 重复（seed 42 / 43 / 44） | 224.74 / 184.76 / 168.79 | 同 seed 两次逐位相同 |
| σ | 28.8 | 三次重复的样本标准差 |
| 一次跑完 | 约 7 秒（基线用不满 60 秒预算） | 纯 CPU |

第一版指标是「单 seed 跑一次的 NLL」，基线 200.3、σ 29；真跑三轮（145.8 / 146.0 / 145.8）全被 2σ 门挡住（记在 [#40](https://github.com/zephyr4123/TJU-AI4Science/issues/40)）。复盘：单次 NLL 本身随起点运气在 148 ～ 250 之间跳，不该当指标。改成 3 个 seed 取均值后 σ 没缩多少（之前的 29 是三个样本碰巧算低了），但基线从运气值 200.3 变成期望值 224.7，keep 线 167：一个稳定到 145 的策略差 79，能过门。

## 第一次真跑的结果（2026-09-16，`runs/boehm-2`）

三轮内环（sonnet，$0.39）：第 1 轮按常数外推起点数超时；第 2 轮固定 30 起点，`nll_mean` **148.26**（三个 seed 里最好一次 139.16，离最优 0.9），差 76.5 过了 57.6 的门，**keep**；第 3 轮换拉丁超立方 147.66，门内 discard。分析 9 条数据、验证 PASS。未决：换优化器、粗搜精修、30 到超时之间的起点数。细节在 [#40](https://github.com/zephyr4123/TJU-AI4Science/issues/40)。

## 求解器

纯 pip 栈：pypesto 0.7.0 + petab 0.9.0 + libroadrunner 2.10.0，Python 3.14，全是预编译轮子，不装 AMICI、不碰 brew。PEtab 定义的 NLL 与求解器无关。roadrunner 目标函数没有解析梯度，scipy 走有限差分。

## 任务包怎么接进来的

按纲领 packs §2 的分工走了一遍：协调层填 manifest；执行层（sonnet，隔离会话，只放行 harness/ 与 code/，$0.42、170 秒）写 launcher / evaluate / make_run0 / 基线 optimize.py，一次写对；人审 evaluate.py（NLL 由 harness 重算，code/ 只产参数向量）；`task validate` 一次过。过程与洞记在 [#40](https://github.com/zephyr4123/TJU-AI4Science/issues/40)。

## 噪声怎么估

学长的判据是「重复运行多次，NLL 稳定下降，且降幅超过不同随机初始点造成的波动」。落到我们的任务包契约上就是 `run_0/sigma.json`：同配置重复 `repeat_k` 次，σ 取 NLL 的标准差。

有一个要注意的点：这道题的波动来源是 multi-start 的随机初始点，不是数据噪声。固定 seed 之后 σ 可能是 0，那就必须走 manifest 的 `min_delta` 而不是统计门（`accept_sigma`），packs §2 里已经写了「σ=0 的确定性 harness 必填 min_delta」。跑 `run_0` 时要明确 seed 策略并记进 manifest。

## 原件索引

原件不进 git（红线 3），在本机 `materials/boehm-stat5-petab/`，被 `.gitignore` 挡住。

| 文件 | 大小（字节） | sha256 |
|---|---|---|
| `Benchmark-Models-PEtab-master.zip` | 5304841 | `54c0f1435bf88b187f2987a2cadd5cf157006ef30b3bf0e3aae80c8c1889a59a` |
| `Identification_of_Isoform_Specific_Dynam.pdf` | 1182783 | `13ff38a3e3e16cd60d70b13052737364553c59b4cf50898d91456a83a86945e2` |
| `案例2.docx` | 16042 | `620a325276313f6711ded8aee6142e36844c318cced083d9945a26b4db3c9f71` |

重取方式：benchmark 仓库可直接 clone，案例目录九个文件总共不到 30 KB；PDF 是原论文；docx 只在学长的 zip 里，见 [案例库说明](../README.md)。

## 做成任务包之后

任务包落在内仓 `platform/tasks/`，`manifest.yaml` 里写 `case: docs/cases/boehm-stat5-petab` 指回这张卡，卡上回填任务包路径与 `run_0` 的实测数字。
