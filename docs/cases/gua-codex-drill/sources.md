# 材料来源

## 选定材料

| 项目 | 选定版本与位置 | 用途与依据 |
|---|---|---|
| 论文 | arXiv:2609.01558 v1（https://arxiv.org/abs/2609.01558）；本地 `materials/paper/source.pdf` | 复现目标、实验设置与表 8 的基准数值。PDF 已解析为 `materials/paper/paper.md` 与 `structured.json`。|
| 官方实现 | https://github.com/JingXiao10/GUA，commit `8bbbcd545436493602bb82a91d08afb449b5b750`；本地 `materials/gua/` | 论文明确链接的官方 GUA 实现；下载收据为 `materials/gua/.ai4sci-download.json`。|
| 许可证 | 官方仓库 `LICENSE`，MIT | 允许复现实验与保存必要的启动/评测改动。|

## 本次复现选择

使用官方仓库的 PINN 入口，目标为 Burgers、ConFIG、2-loss、启用 GUA，覆盖论文种子 0–4。论文附录表 8 的目标为相对 L2 误差 `6.50e-4 ± 1.27e-4`；对照 ConFIG 为 `1.74e-3 ± 3.38e-4`。仓库 README 说明 Burgers 参考数据已随代码提供，故本次无需另行下载数据或预训练权重。

## 环境与限制

在 `seetacloud` 的 RTX 5090（32 GB）上运行，采用已冻结的现成环境：Python 3.12.3、PyTorch 2.8.0+cu128（`materials/env/`）。这与论文的 Python 3.10.12、PyTorch 2.12.0/CUDA 13 参考环境不同，须在最终分析中作为潜在偏离报告。未使用 API key 或账号；预算为今晚完成、总费用不超过 100 元。

## 未采用材料

不运行 CelebA 多任务实验；不扩展至其余五个 PDE、3-loss 或其他梯度手术方法。未发现本最小 PINN 设置所需的额外数据、权重或第三方复现报告。
