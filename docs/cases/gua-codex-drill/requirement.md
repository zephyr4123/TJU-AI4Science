# PINN论文复现

> 论文复现：拿一篇已发表的论文，用它自己的代码（或别人的实现）把它报的数跑出来。复现不是改进——目标是「数对上」和「对不上时说清差在哪」，不是把数做得更好。四样说清楚：哪篇、哪几个数、复现到第几级、对上的标准。

## 论文

Gradient–Update Mismatch: Rethinking Conflict-Free Training of Physics-Informed Neural Networks（Jing Xiao 等，2026；arXiv:2609.01558，https://arxiv.org/abs/2609.01558）。

论文提出 Gradient–Update Alignment（GUA）：把优化器给出的更新方向投影回由各损失梯度定义的无冲突锥，以消除优化器转换后重新出现的梯度冲突（GUM）。目标是用作者的官方实现校验其 PINN 实验结果，作为 PINN 训练方法的可运行基线。

## 要复现的数

本次范围确定为附录表 8 的 Burgers、2-loss、ConFIG+GUA：相对 L2 误差为 6.50e-4 ± 1.27e-4（5 个随机种子）；同条件 ConFIG 基线为 1.74e-3 ± 3.38e-4，论文报告改进 62.6%。同时核对更新冲突率序列中的 GUA 后阶段是否为 0。

暂不纳入：其余五个 PDE、3-loss 设置、其他五种梯度手术方法，以及 CelebA 多任务实验；它们在最小实验跑通后可另行扩展。

## 复现到第几级

一级：用官方代码与其仓库内的 Burgers 数据原样重跑，覆盖论文使用的 5 个随机种子（0–4）。这能先检验结果是否可重跑；二级、三级不在本次范围。

## 材料

论文 PDF 已解析至 `materials/paper/`（含 `source.pdf`、`paper.md`、`structured.json`）；来源：https://arxiv.org/pdf/2609.01558。

官方代码：https://github.com/JingXiao10/GUA（MIT 许可证；待需求确认后固定 commit 并下载）。仓库说明称 Burgers 与 Schrödinger 的参考数据随仓库提供；其余 PINN 评测集按方程协议生成。未发现论文提供预训练权重的说明。暂未采用第三方复现。

## 怎么算对上

论文给出 5 个种子的均值 ± 样本标准差，本次同样报告均值与标准差；以论文均值的相对差不超过 20%，且结果落在论文均值 ± 2 个标准差内，作为「对上」标准。GPU 型号差异导致的小幅数值波动可接受；训练崩溃、缺失结果或无法达到同一数量级不可接受。

## 算力、环境与预算

论文的参考环境为 Python 3.10.12、PyTorch 2.12.0、torchvision 0.27.0、CUDA 13.0；作者报告每个实验在单张 NVIDIA RTX 4090 上运行。需要 GPU；不需要 API key。使用租用机器 `seetacloud`；目标为今晚完成，总成本上限 100 元。机器为 NVIDIA RTX 5090（32 GB），可用磁盘 50 GB，采用现成 conda base（`/root/miniconda3/bin/python`；Python 3.12.3、PyTorch 2.8.0+cu128）。该环境的 131 个依赖已冻结至 `materials/env/`；不隔离新建，避免在租用机器上重装大型 CUDA/PyTorch 依赖。环境版本差异须在复现报告中记录。

## 交付

交付一份复现性分析（论文值与实测值、环境、偏离与原因），以及可重跑的评分脚本和对官方代码所作最小启动/评测改动的 diff。
