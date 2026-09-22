## 结论

基线是本次可用的最好结果：`experiment/1/baseline` 的最终目标函数低于其初始目标函数，且其相对下降量见数据表。该结果是当前最好记录，但下降幅度很小；账本没有记录收敛状态或运行时间，因此不能据此确认是否满足完整拟合的全部验收条件。

延长提前截止比例的改法无效。`experiment/1/iter_1` 的最终目标函数与 `experiment/1/baseline` 完全相同；账本据此裁决为 discard，并指出改动很可能没有生效。

增大数值差分步长的改法无效且使结果变差。`experiment/1/iter_2` 的最终目标函数高于 `experiment/1/baseline`，账本裁决为 discard；这不支持“默认数值差分步长过小导致无法辨识梯度”的假设。

改用有边界的 Powell 搜索未被证明有效。`experiment/1/iter_3` 的最终目标函数低于 `experiment/1/baseline`，但账本将该差异裁决为 within noise，未通过统计门，因此仍为 discard，不能作为有效改法。

## 数据

| 来源 | 指标 | 值 |
| --- | --- | --- |
| experiment/1/baseline | negative_log_likelihood | 138.22192933164877 |
| experiment/1/baseline | initial_negative_log_likelihood | 138.22203512435325 |
| experiment/1/baseline | relative_nll_decrease | 7.653823385910698e-07 |
| experiment/1/iter_1 | negative_log_likelihood | 138.22192933164877 |
| experiment/1/iter_1 | initial_negative_log_likelihood | 138.22203512435325 |
| experiment/1/iter_1 | relative_nll_decrease | 7.653823385910698e-07 |
| experiment/1/iter_2 | negative_log_likelihood | 138.22201229712294 |
| experiment/1/iter_2 | initial_negative_log_likelihood | 138.22203512435325 |
| experiment/1/iter_2 | relative_nll_decrease | 1.6514899588841686e-07 |
| experiment/1/iter_3 | negative_log_likelihood | 138.22191804232813 |
| experiment/1/iter_3 | initial_negative_log_likelihood | 138.22203512435325 |
| experiment/1/iter_3 | relative_nll_decrease | 8.470575984658843e-07 |

## 证伪与未决

被证伪的假设包括：延长提前截止会带来足以超过门槛的改善；以及增大数值差分步长会让优化离开标称点并取得足以超过门槛的改善。前者在第 1 轮未产生分数变化，后者在第 2 轮变差。

尚未尝试的方向包括：在既定一分钟预算内改变多起点配置，或改变每个起点的迭代与函数评估预算。账本也没有提供参数表、模拟成功情况、运行时间和收敛状态，因此这些验收项仍未决。

最值得复查的是第 1 轮：账本明确指出分数与最好结果完全相同，改动可能没有生效。其次可复查第 3 轮，以确认其微小改善在重复计算下是否仍然未通过统计门；在当前账本裁决下，该轮不得视为有效。
