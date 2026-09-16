# 案例一问卷原文

- 填写人：博士学长（GitHub `nqdcxy`）
- 来源：`案例1.docx`，随 [#1](https://github.com/zephyr4123/TJU-AI4Science/issues/1) 的 zip 于 2026-09-15 交付；sha256 见 [案例卡](README.md)
- 转换：docx 逐段转 md，文字一字未改；问题标签改成小节标题，三条核心数字加了列表符，其余原样

## 论文

Witten J, Raji I, Manan RS, et al. Artificial intelligence-guided design of lipid nanoparticles for pulmonary gene therapy. Nature Biotechnology, 2025. DOI: 10.1038/s41587-024-02490-y。

## 代码在哪，怎么启动

GitHub：`https://github.com/jswitten/LNP_ML`

环境：
```bash
conda create -n lnp_ml python=3.8
conda activate lnp_ml
pip install chemprop==1.7.0
```

进入 `scripts` 文件夹后运行：
```bash
python main_script.py split all_amine_split_for_paper.csv -1
python main_script.py train all_amine_split_for_paper
python main_script.py analyze all_amine_split_for_paper
```

README 明确说明这些命令应从 `/scripts` 目录运行。

## 数据在哪，怎么获取

数据已经包含在 GitHub 仓库中，不需要额外下载训练数据。
`data/all_data.csv` 包含仓库中的全部 LNP 数据，`data/all_data_for_paper.csv` 是论文分析使用的数据子集。

## 论文里哪几个数字是核心结论（表几、指标名、数值）

- Figure 2H：RJ-A30-T01 的 Epo mRNA delivery 约为 RM-133-3 的 9 倍。
- Table 1：ferret bronchial epithelial GFP+ cells 平均值：FO-35 14.13%，FO-32 60.66%，IR-117-17 1.41%。
- 计算复现时，可用 Figure 1F/G 的预测值与实验值相关性结果作为主要对账指标。

## 复现一遍要多久，在什么机器上

作者报告，基于仓库全部数据训练模型约需 CUDA GPU 3 小时；仅使用 CPU 约需 24 小时以上。建议内存 >8 GB。
