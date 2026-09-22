上一版已改为集合比较，但在实际执行中仍于此处失败：

```python
x_names = tuple(problem.x_names)
if len(x_names) != len(set(x_names)) or set(x_names) != set(EXPECTED_IDS):
    raise ValueError("PEtab 的待估计参数集合不符合任务契约")
```

这表明当前 `pypesto.petab.PetabImporter(..., simulator_type="roadrunner")` 的 `problem.x_names` 并未返回需求中 9 个 `estimate=1` 参数。不要删除检查、不要静默丢弃参数，也不要把参数数目改成少于 9 个。

请按已锁定的 PEtab/pyPESTO 版本实际 API 修正：

1. 从 `petab_problem.parameter_df` 的 `estimate == 1` 推导权威的待估计参数集合，并核对其恰好为需求中所列 9 个（6 个动力学、3 个 noise）。
2. 查明并修正导入/目标函数配置，使优化问题确实包含这些参数，特别是 3 个 noise 参数 `sd_pSTAT5A_rel`、`sd_pSTAT5B_rel`、`sd_rSTAT5A_rel`。若 RoadRunner 导入器不能正确承担该 PEtab 版本的噪声模型，改用该锁定环境中能完整实现 PEtab 目标函数的受支持路径；不得自行改变观测式、噪声模型或参数定义。
3. 优化向量、边界和 nominal 值必须以最终导入器的名称顺序一致地映射；写出的线性尺度参数表必须包含全部 9 个参数。
4. 在基线产物中留下可读诊断，列出 PEtab `estimate=1` 参数名与最终优化问题参数名，便于人工核对；然后在本机 60 秒预算内重跑基线。
