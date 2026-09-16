# 案例二问卷原文

- 填写人：博士学长（GitHub `nqdcxy`）
- 来源：`案例2.docx`，随 [#1](https://github.com/zephyr4123/TJU-AI4Science/issues/1) 的 zip 于 2026-09-15 交付；sha256 见 [案例卡](README.md)
- 转换：docx 逐段转 md，文字一字未改；问题标签改成小节标题，启动代码加了 python 围栏，其余原样

## 案例名

Boehm_JProteomeRes2014——Epo/STAT5A/STAT5B 动力学参数优化

## 一句话研究问题

根据 Epo 刺激后的实验数据，优化 STAT5A/STAT5B 动力学模型参数，使模型预测结果拟合实验观测。

## 输入是什么（数据、参数及范围）

输入包括 48 个实验测量值、3 个观测指标和 9 个待优化参数。参数范围为 1e-5～1e5，采用 log10 参数尺度。

## 输出是什么（主指标是哪个）

主指标为 Negative Log-Likelihood（NLL），越小越好。

## 基线数字是多少，怎么得到的

使用 pyPESTO 默认优化流程进行 multi-start 参数优化，得到初始优化结果作为 baseline。

## 跑一次多久，在什么机器上

模型规模较小，普通 CPU 即可运行；单次优化通常为秒级到分钟级，不需要 GPU。

## 代码在哪，怎么启动

代码和数据：
https://github.com/Benchmarking-Initiative/Benchmark-Models-PEtab
案例目录：
https://github.com/Benchmarking-Initiative/Benchmark-Models-PEtab/tree/master/Benchmark-Models/Boehm_JProteomeRes2014
pyPESTO：
https://pypesto.readthedocs.io/

原论文：
https://pubmed.ncbi.nlm.nih.gov/25333863/

启动方式：
```python
import pypesto.optimize as optimize
import pypesto.petab

yaml = "Benchmark-Models-PEtab/Benchmark-Models/Boehm_JProteomeRes2014/Boehm_JProteomeRes2014.yaml"

importer = pypesto.petab.PetabImporter.from_yaml(yaml)

problem = importer.create_problem()

result = optimize.minimize(
    problem,
    optimizer=optimize.ScipyOptimizer(),
    n_starts=5
)
```

## 好多少才算真的好，而不是噪声

重复运行多次，如果 NLL 稳定下降，并且下降幅度超过不同随机初始点造成的波动，则认为优化有效。
