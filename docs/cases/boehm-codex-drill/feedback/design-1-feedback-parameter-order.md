基线未运行的直接原因是 `code/fit_boehm.py` 第 56 行将 `tuple(problem.x_names)` 与固定的 `EXPECTED_IDS` 元组逐项比较。PEtab/pyPESTO 返回的参数顺序可以不同，因此这不是合法的契约检查。

请修改 `design/1` 的拟合与评估脚本：

- 仍严格核对待估计参数的**集合**恰好为以下 9 个：`Epo_degradation_BaF3`、`k_exp_hetero`、`k_exp_homo`、`k_imp_hetero`、`k_imp_homo`、`k_phos`、`sd_pSTAT5A_rel`、`sd_pSTAT5B_rel`、`sd_rSTAT5A_rel`。
- 不依赖 `problem.x_names` 的顺序；优化向量、边界和 nominal 值必须都遵循 `problem.x_names` 的实际顺序。
- 写出参数表时按参数名映射，并将 log10 尺度的 9 个数正确还原为线性值。
- 保持既定约束：本机 CPU、单次 60 秒、固定的 `ratio` 与 `specC17` 不估计、PEtab 目标函数对全部测量值必须为有限数。

完成后重新执行基线。
