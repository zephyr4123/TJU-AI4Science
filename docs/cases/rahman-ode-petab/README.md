# rahman-ode-petab · ODE 模型参数估计（平台自测材料）

- 任务类型：**连续参数优化**。7 个状态量的 ODE 模型、9 个待估参数（log10 尺度）、1 个观测量、23 个测量点，最小化负对数似然（NLL）；名义参数处 NLL 21.15，谷底约 21.18
- 应用领域：流行病学。这是第三方 benchmark 的背景，不是我们的研究内容
- 案例类型：**平台自测**。不是学长的案例：2026-09-16 为验收「接任务的对话入口」（[#41](https://github.com/zephyr4123/TJU-AI4Science/issues/41)）从同一个 benchmark 集里挑的第二道题，研究者由 Claude 扮演，协调层由一个只读 `coordinator/README.md` 的新会话扮演
- 状态：**已成任务包** `platform/tasks/rahman-nll`，只经 `ai4sci task design` 接入，协调层没手改 `harness/`；run_0 均值 21.5958、σ 0.056；内环第一批 5 轮无 keep（1 超时、1 改动无效、3 次执行层连不上模型）
- 喂给哪一层：实验内环；接任务入口的真人测试

## 这道题问的是什么

不是"把 NLL 压更低"：谷底就在 21.2 附近，研究者的朴素跑法（5 个均匀随机起点 + scipy 默认优化器）已有约七成次数摸到它，可拿的改进只有 0.34。协调 agent 先撒 300 个起点探出这一点，回头把题改成**紧预算下的稳定性**：每次优化 2 秒，评分脚本内部跑 25 次取均值当主指标，另记最差一次、最好一次、失手次数（超过 21.5 算失手）；改进要稳定超过 0.15 才算数（研究者最初说 0.3，agent 用基线值本身的抽样抖动说服他松到 0.15）。

## 接入过程记了什么

协调 agent 走 README 固定流之二，撞到的 12 个卡点并成五条 issue：[#42](https://github.com/zephyr4123/TJU-AI4Science/issues/42) 预检要问值不值得跑、[#43](https://github.com/zephyr4123/TJU-AI4Science/issues/43) 内部重复次数与预算的契约、[#44](https://github.com/zephyr4123/TJU-AI4Science/issues/44) harness 静默兜底的机器检查、[#45](https://github.com/zephyr4123/TJU-AI4Science/issues/45) delta=0 提示改动没生效、[#46](https://github.com/zephyr4123/TJU-AI4Science/issues/46) 文档缺口。评分脚本第一版的静默默认值（缺参数时按 5 份算）是协调 agent 逐行审出来、用 `--feedback` 打回改掉的，三个设计会话共 1.00 美元。

## 原件索引

八个 PEtab 文件由"研究者"提供，原样进了任务包 `platform/tasks/rahman-nll/data/`（内仓 git 跟踪）；来源 [Benchmark-Models-PEtab](https://github.com/Benchmarking-Initiative/Benchmark-Models-PEtab) 的 `Benchmark-Models/Rahman_MBS2016/`（BSD-3-Clause，Zenodo <https://doi.org/10.5281/zenodo.8155057>）。上游引用表给的原论文 DOI：<https://doi.org/10.1016/j.mbs.2016.07.009>（Math Biosci 2016，题名未核）。

| 文件 | sha256 |
|---|---|
| `Rahman_MBS2016.yaml` | `12176b76b1a092fdd98f4e1710fb5cd1ac977e195239d98d8904670d8db037d7` |
| `model_Rahman_MBS2016.xml` | `00632eaa0aaf371b07b56dea05f12005997809c685953d4960a84cd700100394` |
| `experimentalCondition_Rahman_MBS2016.tsv` | `e3a240d5109ad6cad550b940d327f6388d227f0fd4e473fc2a7357caeaf95cc4` |
| `measurementData_Rahman_MBS2016.tsv` | `77ea7059f814d706a2b1c12a1acf7617bdf9dec2fe8f684b559a5ed01b0261f9` |
| `observables_Rahman_MBS2016.tsv` | `dff3482246b6e8525d3526fbca16637e683343db7e5a0dd921c36072da01a25c` |
| `parameters_Rahman_MBS2016.tsv` | `78a8fd99e76fb5a524eb6c7275bf3ea7bf4e8f18a6c1ce5466aa6eae4e9f1569` |
| `simulatedData_Rahman_MBS2016.tsv` | `555288ccb26aaa10c207e8a158dbfeaa3f20b5cf0797be4771485334f4d4f6bf` |
| `visualizationSpecification_Rahman_MBS2016.tsv` | `b647de9ddfa3c7e785753836a9b61baf55fe892841031e806e67c2e8081dfcf1` |

重取方式：上游仓库 `git clone` 后取同名目录。备选题 Crauste_CellSystems2017 在 petab 0.9.0 下装不了（时间点相关的参数覆盖不支持），记在这里免得下次再试。
