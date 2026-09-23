# harness/evaluate.py（执行层写的；外层仓不放 .py，原文照抄成代码块）

```python
"""从官方训练保存的正式评测表读取指标，并拒收不完整或异常的产物。"""

import json
import math
import os
import sys
import time
from pathlib import Path

TASK_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SEED = 42


def _fail(code: int, message: str) -> None:
    print(f"evaluate: {message}", file=sys.stderr)
    raise SystemExit(code)


def _number(value: object, name: str, lower: float, upper: float) -> float:
    if isinstance(value, bool) or not isinstance(value, int | float):
        _fail(3, f"{name} 不是数值")
    result = float(value)
    if not math.isfinite(result) or not lower <= result <= upper:
        _fail(4, f"{name} 不是范围 [{lower}, {upper}] 内的有限数")
    return result


def _elapsed_s() -> float:
    try:
        start = float(os.environ["AI4SCI_START_EPOCH"])
    except KeyError:
        _fail(5, "拿不到 AI4SCI_START_EPOCH，不填 0 假装量过")
    except ValueError:
        _fail(5, "AI4SCI_START_EPOCH 不是时间戳")
    elapsed = time.time() - start
    if not math.isfinite(elapsed) or elapsed < 0:
        _fail(5, "AI4SCI_START_EPOCH 不能用于有效计时")
    return elapsed


def _seed() -> int:
    try:
        return int(os.environ.get("AI4SCI_SEED", DEFAULT_SEED))
    except ValueError:
        _fail(3, "AI4SCI_SEED 不是整数")


def _inner_k() -> int:
    try:
        value = int(os.environ["AI4SCI_INNER_K"])
    except KeyError:
        _fail(2, "拿不到 AI4SCI_INNER_K")
    except ValueError:
        _fail(3, "AI4SCI_INNER_K 不是整数")
    if value < 1:
        _fail(3, "AI4SCI_INNER_K 必须为正数")
    return value


def _load_formal_metrics(path: Path, seed: int, require_gua: bool) -> tuple[float, float | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        _fail(2, f"缺少官方评测表：{path.relative_to(TASK_DIR)}")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        _fail(2, f"无法读取官方评测表：{path.relative_to(TASK_DIR)}")
    if not isinstance(payload, dict):
        _fail(3, "官方评测表的顶层不是对象")
    if payload.get("equation") != "burgers" or payload.get("seed") != seed:
        _fail(3, "官方评测表不属于本次 Burgers 种子")
    if payload.get("diagnostics_enabled") is not True:
        _fail(3, "官方评测表没有更新冲突诊断")
    relative_l2 = _number(payload.get("relative_l2"), "relative_l2", 0.0, 10.0)
    if not require_gua:
        return relative_l2, None
    conflict = payload.get("conflict")
    if not isinstance(conflict, dict) or "r_p" not in conflict:
        _fail(3, "官方评测表缺少 GUA 后冲突率 r_p")
    post_conflict = _number(conflict["r_p"], "conflict.r_p", 0.0, 1.0)
    return relative_l2, post_conflict


def main() -> None:
    seed = _seed()
    base_records = []
    gua_records = []
    for inner_idx in range(1, _inner_k() + 1):
        base_path = (
            TASK_DIR
            / "outputs"
            / "config_2loss"
            / f"seed-{seed}-inner-{inner_idx}"
            / "formal_metrics.json"
        )
        gua_path = (
            TASK_DIR
            / "outputs"
            / "config_2loss_gua"
            / f"seed-{seed}-inner-{inner_idx}"
            / "formal_metrics.json"
        )
        base_records.append(_load_formal_metrics(base_path, seed, require_gua=False)[0])
        gua_records.append(_load_formal_metrics(gua_path, seed, require_gua=True))
    metrics = {
        "config_gua_relative_l2": sum(item[0] for item in gua_records) / len(gua_records),
        "config_relative_l2": sum(base_records) / len(base_records),
        "post_gua_conflict_rate": sum(item[1] for item in gua_records) / len(gua_records),
    }
    results = {
        "metrics": metrics,
        "elapsed_s": _elapsed_s(),
        "seed": seed,
        "status": "ok",
    }
    (TASK_DIR / "results.json").write_text(json.dumps(results), encoding="utf-8")


if __name__ == "__main__":
    main()
```
