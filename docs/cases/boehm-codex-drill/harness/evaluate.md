# harness/evaluate.py（原文照抄；外层仓不放 .py，所以放在代码块里）

```python
"""评测层只接受参数产物，并以 data/ 中的 PEtab 原件重新计算成绩。"""

import json
import math
import os
import sys
import time
from pathlib import Path

import petab
import pypesto.petab

TASK_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = TASK_DIR / "data"
YAML_PATH = DATA_DIR / "Boehm_JProteomeRes2014.yaml"
ARTIFACT_PREFIX = "fit-"
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
LOWER_BOUND = 1e-5
UPPER_BOUND = 1e5
DEFAULT_SEED = 42


def _fail(code: int, message: str) -> None:
    print(f"evaluate: {message}", file=sys.stderr)
    raise SystemExit(code)


def _load_artifact(path: Path) -> dict[str, object]:
    if not path.is_file():
        _fail(2, f"文件缺失：{path.name}")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        _fail(2, f"文件读不出：{path.name}")
    if not isinstance(loaded, dict):
        _fail(3, f"产物根节点不是对象：{path.name}")
    return loaded


def _scaled_vector(
    artifact: dict[str, object], x_names: tuple[str, ...]
) -> list[float]:
    parameters = artifact.get("parameters")
    if not isinstance(parameters, dict) or set(parameters) != set(EXPECTED_IDS):
        _fail(3, "parameters 必须恰好包含九个待估计参数")
    vector = []
    for parameter_id in x_names:
        value = parameters[parameter_id]
        if isinstance(value, bool) or not isinstance(value, int | float):
            _fail(3, f"参数不是数值：{parameter_id}")
        value = float(value)
        if not math.isfinite(value) or not LOWER_BOUND <= value <= UPPER_BOUND:
            _fail(4, f"参数非有限或越界：{parameter_id}")
        vector.append(math.log10(value))
    return vector


def _estimated_ids(petab_problem: petab.Problem) -> tuple[str, ...]:
    """评分按 PEtab 的 estimate 列确认契约，不能信任参赛代码的声明。"""
    parameter_df = petab_problem.parameter_df
    if "estimate" not in parameter_df:
        _fail(3, "PEtab 参数表缺少 estimate 列")
    estimated = tuple(
        str(parameter_id)
        for parameter_id in parameter_df.index[parameter_df["estimate"] == 1]
    )
    if len(estimated) != len(EXPECTED_IDS) or set(estimated) != set(EXPECTED_IDS):
        _fail(3, "PEtab estimate=1 参数集合与契约不一致")
    return estimated


def _free_problem_names(problem: object) -> tuple[str, ...]:
    """固定参数存在于完整向量中，评分目标必须接收同序的自由参数子向量。"""
    try:
        x_names = problem.x_names
        free_indices = problem.x_free_indices
        dimension = problem.dim
        lower_bounds = problem.lb
    except AttributeError:
        _fail(3, "导入后的优化问题缺少参数向量或边界")
    free_names = tuple(str(x_names[index]) for index in free_indices)
    if len(free_names) != len(EXPECTED_IDS) or set(free_names) != set(EXPECTED_IDS):
        _fail(3, "导入后的自由参数集合与契约不一致")
    if dimension != len(free_names) or len(lower_bounds) != len(free_names):
        _fail(3, "导入后的优化向量与边界长度不一致")
    return free_names


def _elapsed_s() -> float:
    try:
        start = float(os.environ["AI4SCI_START_EPOCH"])
    except (KeyError, ValueError):
        _fail(5, "拿不到有效的 AI4SCI_START_EPOCH")
    elapsed = time.time() - start
    if not math.isfinite(elapsed) or elapsed < 0:
        _fail(5, "AI4SCI_START_EPOCH 不能用于计时")
    return elapsed


def main() -> None:
    try:
        inner_k = int(os.environ["AI4SCI_INNER_K"])
    except (KeyError, ValueError):
        _fail(3, "拿不到有效的 AI4SCI_INNER_K")
    if inner_k < 1:
        _fail(3, "AI4SCI_INNER_K 必须为正整数")

    try:
        petab_problem = petab.Problem.from_yaml(YAML_PATH)
        _estimated_ids(petab_problem)
        importer = pypesto.petab.PetabImporter(
            petab_problem, simulator_type="roadrunner"
        )
        problem = importer.create_problem()
        x_names = _free_problem_names(problem)
        initial_x = []
        for parameter_id in x_names:
            nominal = float(petab_problem.parameter_df.loc[parameter_id, "nominalValue"])
            if not math.isfinite(nominal) or nominal <= 0:
                _fail(4, f"PEtab nominal 值无效：{parameter_id}")
            initial_x.append(math.log10(nominal))
        initial_nll = float(problem.objective(initial_x))
        vectors = [
            _scaled_vector(
                _load_artifact(TASK_DIR / f"{ARTIFACT_PREFIX}{i}.json"), x_names
            )
            for i in range(inner_k)
        ]
        values = [float(problem.objective(vector)) for vector in vectors]
    except (
        AttributeError,
        IndexError,
        KeyError,
        OSError,
        RuntimeError,
        TypeError,
        ValueError,
    ) as exc:
        _fail(2, f"无法用 data/ 重建 PEtab 目标函数：{exc}")
    if not all(math.isfinite(value) for value in [initial_nll, *values]):
        _fail(4, "PEtab 模拟或目标函数返回 NaN/Inf")

    nll = sum(values) / len(values)
    relative_decrease = (initial_nll - nll) / abs(initial_nll) if initial_nll else 0.0
    if not all(math.isfinite(value) for value in (nll, relative_decrease)):
        _fail(4, "汇总指标返回 NaN/Inf")
    metrics = {
        "negative_log_likelihood": nll,
        "initial_negative_log_likelihood": initial_nll,
        "relative_nll_decrease": relative_decrease,
    }
    results = {
        "metrics": metrics,
        "elapsed_s": _elapsed_s(),
        "seed": int(os.environ.get("AI4SCI_SEED", DEFAULT_SEED)),
        "status": "ok",
    }
    (TASK_DIR / "results.json").write_text(json.dumps(results), encoding="utf-8")


if __name__ == "__main__":
    main()

```
