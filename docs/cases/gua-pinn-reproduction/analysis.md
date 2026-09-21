## 结论

这次复现是**一级**：用官方代码、官方附带的 Burgers 数据、论文给定的五个种子 `{0,1,2,3,4}` 原样重跑，检验的是「结果可重跑」，没有换实现，只换了机器（同型号 GPU、不同软件版本）。主指标 `config_gua_relative_l2` 论文值 0.00065、我们五个种子均值比论文值高约 13%；基线 `config_relative_l2` 论文值 0.00174、我们均值比论文值高约 11%；两者都落在需求给定的 ±2 倍论文标准差（折成相对值约 ±39%）容差内，而且五个种子里每一个加 GUA 后误差都下降——按需求的标准，两个指标都对上了，方向一致。最可能的原因是环境版本差异（`Python 3.12.3` / `torch 2.8.0+cu128`，仓库声明的是 `Python 3.10.12` / `torch 2.12.0+cu130`）与硬件之间的正常波动，量级与论文给出的样本标准差相当。

## 数据

| 来源 | 指标 | 值 |
|---|---|---|
| design/1/scoring | config_relative_l2 | 0.00174 |
| design/1/scoring | config_gua_relative_l2 | 0.00065 |
| design/1/baseline | config_relative_l2 | 0.002332588890567422 |
| design/1/baseline | config_gua_relative_l2 | 0.0007692898507229984 |
| design/1/repeat_1 | config_relative_l2 | 0.002162467921152711 |
| design/1/repeat_1 | config_gua_relative_l2 | 0.0006698203505948186 |
| design/1/repeat_2 | config_relative_l2 | 0.0019970054272562265 |
| design/1/repeat_2 | config_gua_relative_l2 | 0.0006293538026511669 |
| design/1/repeat_3 | config_relative_l2 | 0.0016592246247455478 |
| design/1/repeat_3 | config_gua_relative_l2 | 0.000574023462831974 |
| design/1/repeat_4 | config_relative_l2 | 0.0015395124210044742 |
| design/1/repeat_4 | config_gua_relative_l2 | 0.0010216208174824715 |
| design/1/sigma | config_relative_l2 | 0.00028960201721050166 |
| design/1/sigma | config_gua_relative_l2 | 0.0002024550162030212 |

`design/1/scoring` 是论文值；`design/1/baseline` 与 `design/1/repeat_1`~`repeat_4` 是我们五个种子各自跑的一次；`design/1/sigma` 是平台按 `repeat_1`~`repeat_4` 这 4 次重复算的样本标准差（不含 baseline，是平台的固定算法）。均值（baseline + repeat_1~4 五个值的算术平均）不在结果清单里单列，是本文自己算的：`config_relative_l2` 均值约 0.00194，`config_gua_relative_l2` 均值约 0.00073（用于上面结论一节的百分比对比）。

## 方法与环境

- 代码：官方仓库 `GUA`（https://github.com/JingXiao10/GUA），commit `8bbbcd545436493602bb82a91d08afb449b5b750`，MIT 许可。
- 数据：仓库自带的 Burgers（Cole–Hopf 解析解）数据，未另外下载或生成。
- 机器：`autodl`（租的 AutoDL），GPU `NVIDIA GeForce RTX 4090`（24564 MiB），与论文使用的显卡型号相同。
- 解释器与关键库：机器上现成的 `/root/miniconda3/bin/python`，`Python 3.12.3`、`torch 2.8.0+cu128`；仓库声明的环境是 `Python 3.10.12`、`torch 2.12.0` + `torchvision 0.27.0`（`cu130`）——版本不同。仓库 `requirements.txt` 里缺的包（`numpy==2.2.6`、`scipy==1.15.3`、`PyYAML==6.0.3`、`tqdm==4.68.1`、`tensorboard==2.20.0`、`torchjd==0.13.0`、`qpsolvers==4.12.0`、`quadprog==0.1.13`、`Pillow==12.2.0`）已用 `env add` 补装到这个现成环境上，没有隔离新建。
- 跑的次数：两个方法（ConFIG、ConFIG+GUA）各五个种子（`baseline` + `repeat_1`~`repeat_4`，对应论文的种子 `{0,1,2,3,4}`），共 5 次训练，每次训练两个变体一起跑。
- 单次时长：约半小时；五个种子合计不到三小时。
- 论文使用的硬件与设置：单张 RTX 4090；其余训练细节（学习率调度、采点方式等）按论文附录 B 的设置原样跑，具体数值见材料来源 `sources.md`，本文不重复列出。

## 偏离与改动

- `code/` 相对上游 `GUA` 的改动：`upstream.diff` 为空，一字未改。
- 与论文设置的不同：解释器与关键库版本（`Python 3.12.3` / `torch 2.8.0+cu128`，对比仓库声明的 `Python 3.10.12` / `torch 2.12.0+cu130`）；机器是租用的 AutoDL 而非论文所用的本地机器（GPU 型号相同）；环境是现成 conda base 补装出来的，没有按仓库声明的版本隔离新建。
- 种子数：五个种子全部跑齐，与论文口径一致，未按预算缩减。
- 缺的材料：无——数据随仓库自带，不需要预训练权重或 API key，材料齐全。

## 容易与困难

- 容易：数据随仓库自带（Burgers 的 Cole–Hopf 解析解），不用额外下载或生成；`trainer.py` 提供了现成的命令行参数（如 `--num-run 5 --seed-offset 0`）可以直接连跑五个种子，不用自己写多种子循环；每个基准的训练配置封装在 `training_configs/burgers.yaml` 里，参数不用逐个翻代码找。
- 费时：环境版本差异——仓库声明 `Python 3.10.12` + `torch 2.12.0`，现成环境是 `Python 3.12.3` + `torch 2.8.0+cu128`，`requirements.txt` 里的几个依赖（`torchjd`、`qpsolvers`、`quadprog` 等）缺省环境里没有，要用 `env add` 逐个补装。

## 证伪与未决

- 这次检验了：GUA 相对 ConFIG 能否在重新跑的实验里稳定降低误差（论文核心主张之一）——检验了，五个种子里每一个都是 ConFIG+GUA 比 ConFIG 更低，方向与论文一致。
- 没检验的：论文其余五个 PDE 基准（Schrödinger、Kovasznay、Poisson-5D、Heat-MS、Beltrami）、其余五种梯度手术方法、3-loss 拆分组合，以及诊断性的冲突率结果（表 1、表 7、表 9）和 CelebA 多任务实验（Q6）——本次范围内未跑。
- 没搞清楚的：环境版本差异（`Python`、`torch` 版本与仓库声明不同）对结果偏差的具体贡献有多大，没有做消融，无法区分这部分偏差是版本差异还是种子/硬件本身的正常波动。
- 下一步如果要缩小差距：先把 `torch` 换成仓库声明的 `2.12.0`（其余设置不变）在同一台机器上单独跑一次，看均值是否更贴近论文值——一次只换这一个设置。
