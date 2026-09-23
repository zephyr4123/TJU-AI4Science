# lnp-lipid-design · 分子性质预测

- 任务类型：**回归**。输入 SMILES 字符串加配方参数，输出一个标量（数据列名 `quantified_delivery`），用图神经网络（chemprop，D-MPNN）拟合
- 应用领域：药剂学。这是第三方论文的背景，不是我们的研究内容
- 案例类型：复现型（[#1](https://github.com/zephyr4123/TJU-AI4Science/issues/1) 的「案例一 · 做完的小课题」）
- 状态：登记，没跑（理由见文末；2026-09-23 按现状重写）
- 喂给哪一层：验证层与评测层——有标准答案才能验系统对不对
- 原文：[questionnaire.md](questionnaire.md)

## 来源与署名

不是学长自己组里的工作，论文与代码都是第三方公开成果。

- 论文：Witten J, Raji I, Manan RS, et al. Nature Biotechnology, 2025. DOI 10.1038/s41587-024-02490-y
- 作者单位：MIT 化工系、Koch 研究所、University of Iowa（看署名与仓库归属判定）
- 代码：<https://github.com/jswitten/LNP_ML>，作者本人仓库，数据随仓库分发

[#1](https://github.com/zephyr4123/TJU-AI4Science/issues/1) 的案例一要的是「你自己或组里已经发表的论文」，这一条没满足。带来的后果见下面两节。

## 核心数字

学长给了三条，原文在 [questionnaire.md](questionnaire.md)。分两类：

- 前两条（Figure 2H 的倍数、Table 1 的三个百分比）是湿实验测量值，代码跑不出来，我们也拿不到原始实验数据。
- 第三条（Figure 1F/G 的预测值与实验值相关性）是唯一能用代码对账的，这是计算复现的主指标。

## 复现成本

| 项 | 值 |
|---|---|
| 作者报告训练时长，CUDA GPU | 3 小时 |
| 作者报告训练时长，纯 CPU | 24 小时以上 |
| 建议内存 | 8 GB 以上 |
| 仓库解压后体积 | 267,635,250 字节 |
| Python | 3.8，依赖 chemprop 1.7.0 |

仓库里已经带了训好的权重（`data/crossval_splits/*/cv_*/fold_0/model_0/model.pt`，每个约 6.5 MB），所以「只做推理对账」比「从头训练」便宜得多，这是以后真要复现时的切入点。

## 为什么 0.2.0 不跑

1. 三条核心数字里两条是湿实验结果，对不上账——平台能核的只有预测相关性那一条。
2. Python 3.8 加 chemprop 1.7.0：课题环境与平台 venv 已解耦（`materials/env/` 自带解释器版本与清单，或用机器上现成的环境），这条不再是障碍。
3. 纯 CPU 24 小时以上：算力可租（P-23），但 AutoResearch 一轮一天没有意义；要跑只能走复现流（一级：原样跑一遍），值不值得由研究者定。

按 [#1](https://github.com/zephyr4123/TJU-AI4Science/issues/1) 原定计划登记为复现型任务，platform 0.2.0 不跑。

## 原件索引

原件不进 git（红线 3），在本机 `materials/lnp-lipid-design/`，被 `.gitignore` 挡住。

| 文件 | 大小（字节） | sha256 |
|---|---|---|
| `LNP_ML-main.zip` | 134788854 | `77ba40b038427ddb878395aa1a5e6fd31685e4826c592bfb3648388e61e4c36c` |
| `nihms-2074395.pdf` | 2638380 | `5e8ffe6a6dc763e6f435c3982eefdda59fc2180f75246f79f3a2d471006b3eea` |
| `案例1.docx` | 15271 | `531bd0769232f949a670661995513a783632800f96d67860594e6111aa6ef8a1` |

重取方式：代码仓可直接 `git clone https://github.com/jswitten/LNP_ML`；PDF 是论文的 PMC 作者稿（`nihms-2074395`）；docx 只在学长的 zip 里，见 [案例库说明](../README.md)。
