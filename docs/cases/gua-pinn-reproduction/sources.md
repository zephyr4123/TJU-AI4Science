# 材料来源：复现 GUA（arXiv 2609.01558）

## 论文

- Gradient–Update Mismatch: Rethinking Conflict-Free Training of Physics-Informed Neural Networks. Jing Xiao, Xinhai Chen 等，国防科技大学，2026。
- https://arxiv.org/abs/2609.01558 ；PDF 直链 https://arxiv.org/pdf/2609.01558
- 已解析：`materials/paper/`（`source.pdf`、`paper.md`、`structured.json`、`images/`），36 页、11 张表。
- 要复现的数（论文附录 C.4.1 表 8，五个种子的均值 ± 样本标准差，Burgers · 2-loss 列；从 `structured.json` 的表里抄）：

| 方法 | 相对 L2 误差 |
|---|---|
| ConFIG | 1.74e-3 ± 3.38e-4 |
| ConFIG + GUA | 6.50e-4 ± 1.27e-4 |

- 训练设置（附录 B.3 表 3、表 4）：Burgers 30,000 轮，Nf=10,000、Nb=250、Ni=250；Adam(0.9, 0.999, 1e-8)，100 轮线性预热后余弦从 1e-3 衰到 1e-4；全批；每轮重采样（LHS）；每 100 轮验证一次，取验证最好的 checkpoint 测试；种子 {0,1,2,3,4}；单张 RTX 4090。

## 官方代码（选定）

- https://github.com/JingXiao10/GUA ，MIT 许可，论文摘要里给的链接，README 自称 official implementation。
- 拉到 `materials/GUA/`，commit `8bbbcd545436493602bb82a91d08afb449b5b750`（默认分支最新，2026-09-21 拉的），80 个文件、5.4 MB，收据在 `materials/GUA/.ai4sci-download.json`。
- 结构：`conflictfree/` 核心算子（grad_operator / weight_model / length_model）；`experiments/PINN/trainer.py` 训练入口；`experiments/PINN/training_configs/burgers.yaml` 每个基准的配置；`experiments/PINN/lib_pinns/` 六个 PDE 的实现；`experiments/MTL/` CelebA 多任务（不用）。
- 入口参数（`trainer.py`）：`--equation burgers --method config --n-losses 2 --optimizer-correction none|gua --random-seed <n>`；`--num-run 5 --seed-offset 0` 可连跑五个种子；`--save-path` 指定输出目录；`--device cuda:0`。
- README 声明的环境：Python 3.10.12、torch 2.12.0 + torchvision 0.27.0（cu130）；`requirements.txt`：numpy 2.2.6、scipy 1.15.3、PyYAML 6.0.3、tqdm 4.68.1、tensorboard 2.20.0、torchjd 0.13.0、qpsolvers 4.12.0、quadprog 0.1.13、Pillow 12.2.0。
- 没有 Docker、没有预训练权重、不要 API key。

## 数据

- Burgers：随仓库附带，`materials/GUA/experiments/PINN/data/burgers/simulation_data_cole_hopf.npy`（Cole–Hopf 解析解），不用另外下载。
- Schrödinger：同样附带（`data/schrodinger/NLS.mat`），本次不用。
- 其余四个基准由代码按协议生成，本次不用。

## 别人的复现

- 没找到：论文 2026 年新出，Papers with Code / GitHub 上暂无第三方复现或活跃 fork；仓库 issue 里也没有「跑不出论文的数」的记录（2026-09-21 查）。

## 我们的环境（与论文的差异，复现性分析里要写）

- 机器：`autodl`（租的 AutoDL），RTX 4090 24 GB——与论文同型号显卡。
- 环境：镜像自带的 conda base，`/root/miniconda3/bin/python`，Python 3.12.3、torch 2.8.0+cu128；清单冻在 `materials/env/`（126 个包）。比 README 声明的 torch 2.12 旧、Python 比 3.10 新；`requirements.txt` 里的 torchjd / qpsolvers / quadprog 等要装到这个环境上。
- 没有隔离新建：租来的机器，装 CUDA 版 torch 要两个多小时，关机即失。

## 还缺什么

- 单次训练时长：没实测。先跑一个种子看时间，再定五个种子全跑还是减到三个（需求里写了退路）。
