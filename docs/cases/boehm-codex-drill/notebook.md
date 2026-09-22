### 第 1 轮 · discard · 138.222

假设：80% 的提前截止使优化过早结束，未充分利用一分钟预算。  
改动：将优化截止从总预算的 80% 调整为 95%，并在代码中注明假设。  
预期：在仍能写出参数产物的前提下，更多迭代可将 negative_log_likelihood 降低超过 0.1。

改动：
```
code/fit_boehm.py | 4 +++-
 1 file changed, 3 insertions(+), 1 deletion(-)
```
裁决：持平 delta=0：分数与 best 完全相同，改动很可能没有生效

### 第 2 轮 · discard · 138.222

假设：默认数值差分步长过小，导致优化器无法辨识 RoadRunner 目标函数梯度。  
改动：将 L-BFGS-B 的 `eps` 设为 log10 参数空间中的 `1e-3`，并写入假设注释。  
预期：优化能离开 nominal 点，使 negative_log_likelihood 下降超过 0.1。

改动：
```
code/fit_boehm.py | 4 +++-
 1 file changed, 3 insertions(+), 1 deletion(-)
```
裁决：变差 delta=-8.29655e-05

### 第 3 轮 · discard · 138.222

假设：RoadRunner 目标的数值梯度在标称点近乎为零，方向集搜索可仅凭函数值离开该点。  
改动：将 `code/fit_boehm.py` 的优化器从 L-BFGS-B 改为有边界的 Powell。  
预期：在相同迭代与时间预算内，negative_log_likelihood 可下降超过 0.1。

改动：
```
code/fit_boehm.py | 3 ++-
 1 file changed, 2 insertions(+), 1 deletion(-)
```
裁决：within noise: delta=1.12893e-05 <= gate=0.1

