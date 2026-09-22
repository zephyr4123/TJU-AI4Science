# code/fit_boehm.py（原文照抄；外层仓不放 .py，所以放在代码块里）

```python
"""以 RoadRunner PEtab 目标函数拟合 Boehm 模型，并只交付最终参数。"""

import json
import math
import os
import random
import time
from pathlib import Path

import petab
import pypesto.petab
from scipy.optimize import minimize

TASK_DIR = Path(__file__).resolve().parent.parent
YAML_PATH = TASK_DIR / "data" / "Boehm_JProteomeRes2014.yaml"
EXPECTED_IDS = (
    "Epo_degradation_BaF3",
    "k_exp_hetero",
    "k_exp_homo",
    "k_imp_hetero",
    "k_imp_homo",
    "k_phos",
    "sd_pSTAT5A_rel",
    "sd_pSTAT5B_rel",
    "sd_rSTAT5A_rel",
)
MAXITER = 200  # 单起点上限；墙钟截止仍优先，避免小模型在异常数值处拖延。
N_STARTS = 4  # 少量随机起点在一分钟预算内兼顾局部最优与可重复性。


class _TimeLimitReached(Exception):
    """用受控异常离开 SciPy 回调，确保仍可交付当前最优参数。"""


def _deadline() -> float:
    run_budget = float(os.environ["AI4SCI_RUN_BUDGET_S"])
    if not math.isfinite(run_budget) or run_budget <= 0:
        raise ValueError("AI4SCI_RUN_BUDGET_S 必须为正有限数")
    return time.monotonic() + 0.8 * run_budget


def _as_linear(parameter_id: str, scaled: float) -> float:
    if parameter_id not in EXPECTED_IDS:
        raise ValueError(f"未知待估计参数：{parameter_id}")
    return 10.0**scaled


def _nominal_in_problem_order(
    petab_problem: petab.Problem, x_names: tuple[str, ...]
) -> list[float]:
    """按名称重排 nominal 值，避免 PEtab 表与优化问题恰巧同序成为隐含前提。"""
    values = []
    for parameter_id in x_names:
        nominal = float(petab_problem.parameter_df.loc[parameter_id, "nominalValue"])
        if not math.isfinite(nominal) or nominal <= 0:
            raise ValueError(f"PEtab nominal 值无效：{parameter_id}")
        values.append(math.log10(nominal))
    return values


def _estimated_ids(petab_problem: petab.Problem) -> tuple[str, ...]:
    """以 PEtab 表为准，避免导入器的完整向量把固定参数混入待估计集合。"""
    parameter_df = petab_problem.parameter_df
    if "estimate" not in parameter_df:
        raise ValueError("PEtab 参数表缺少 estimate 列")
    estimated = tuple(
        str(parameter_id)
        for parameter_id in parameter_df.index[parameter_df["estimate"] == 1]
    )
    if len(estimated) != len(EXPECTED_IDS) or set(estimated) != set(EXPECTED_IDS):
        raise ValueError("PEtab estimate=1 参数集合不符合九参数契约")
    return estimated


def _free_problem_names(problem: object) -> tuple[str, ...]:
    """pyPESTO 保留完整名称；优化器只能接收移除固定参数后的同序向量。"""
    x_names = getattr(problem, "x_names")
    free_indices = getattr(problem, "x_free_indices")
    free_names = tuple(str(x_names[index]) for index in free_indices)
    if len(free_names) != len(EXPECTED_IDS) or set(free_names) != set(EXPECTED_IDS):
        raise ValueError("导入后的自由参数集合不符合九参数契约")
    return free_names


def main() -> None:
    seed = int(os.environ.get("AI4SCI_SEED", "42"))
    run_index = int(os.environ["AI4SCI_RUN_INDEX"])
    deadline = _deadline()
    petab_problem = petab.Problem.from_yaml(YAML_PATH)
    estimated_ids = _estimated_ids(petab_problem)
    importer = pypesto.petab.PetabImporter(
        petab_problem, simulator_type="roadrunner"
    )
    problem = importer.create_problem()
    x_names = _free_problem_names(problem)
    if problem.dim != len(x_names) or len(problem.lb) != len(x_names):
        raise ValueError("导入后的优化向量与边界长度不一致")

    bounds = list(zip(problem.lb, problem.ub, strict=True))
    best_x = _nominal_in_problem_order(petab_problem, x_names)
    best_fval = float(problem.objective(best_x))
    rng = random.Random(seed + run_index * 100003)
    starts = [best_x]
    starts.extend([[rng.uniform(lower, upper) for lower, upper in bounds]
                   for _ in range(N_STARTS - 1)])

    for start in starts:
        if time.monotonic() >= deadline:
            break

        def objective(x: object) -> float:
            if time.monotonic() >= deadline:
                raise _TimeLimitReached
            return float(problem.objective(x))

        try:
            result = minimize(objective, start, method="L-BFGS-B", bounds=bounds,
                              options={"maxiter": MAXITER})
        except _TimeLimitReached:
            break
        if math.isfinite(float(result.fun)) and float(result.fun) < best_fval:
            best_fval = float(result.fun)
            best_x = [float(value) for value in result.x]

    artifact = {
        "parameters": {
            parameter_id: _as_linear(parameter_id, scaled)
            for parameter_id, scaled in zip(x_names, best_x, strict=True)
        },
        "diagnostics": {
            "petab_estimate_1_parameters": estimated_ids,
            "optimization_free_parameters": x_names,
        },
    }
    (TASK_DIR / f"fit-{run_index}.json").write_text(
        json.dumps(artifact), encoding="utf-8"
    )


if __name__ == "__main__":
    main()

```
