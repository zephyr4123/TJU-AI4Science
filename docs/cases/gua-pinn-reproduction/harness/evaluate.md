# harness/evaluate.py（原文照抄；外层仓不放 .py，所以放在代码块里）

```python
"""评分脚本：从 ConFIG、ConFIG+GUA 两个变体各自的 formal_metrics.json 里，
读取上游代码按论文定义（run_test 对参考解的相对 L2 范数）算好的误差，写 results.json。
这是上游训练代码自己保存的表，不是 stdout 打印的一行字；任何一个变体的产物缺失、
字段不对、非有限数都视为这一轮不合格，不写 results.json。
"""

import json
import math
import os
import sys
import time
from pathlib import Path

import yaml

TASK_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SEED = 0
EQUATION = "burgers"
# (指标名, outputs/ 下的子目录名, --optimizer-correction 的取值)
VARIANTS = (
    ("config_relative_l2", "none", "none"),
    ("config_gua_relative_l2", "gua", "gua"),
)


def _fail(code: int, message: str) -> None:
    print(f"evaluate: {message}", file=sys.stderr)
    raise SystemExit(code)


def _elapsed_s() -> float:
    start = os.environ.get("AI4SCI_START_EPOCH")
    if start is None:
        _fail(5, "拿不到 AI4SCI_START_EPOCH，不填 0 假装量过")
    return time.time() - float(start)


def _load_json(path: Path) -> dict:
    if not path.exists():
        _fail(2, f"缺产物：{path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _fail(2, f"读不出 {path}：{exc}")
    return {}


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        _fail(2, f"缺产物：{path}")
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        _fail(2, f"读不出 {path}：{exc}")
    return {}


def _read_variant(subdir: str, expected_correction: str, seed: int) -> float:
    run_dir = TASK_DIR / "outputs" / subdir / "run"
    configs = _load_yaml(run_dir / "configs.yaml")
    if configs.get("optimizer_correction") != expected_correction or configs.get("n_losses") != 2:
        _fail(3, f"{run_dir} 的 configs.yaml 不是预期的 optimizer_correction/n_losses 组合")
    metrics = _load_json(run_dir / "formal_metrics.json")
    for key in ("equation", "seed", "relative_l2"):
        if key not in metrics:
            _fail(3, f"{run_dir}/formal_metrics.json 缺字段 {key}")
    if metrics["equation"] != EQUATION or int(metrics["seed"]) != seed:
        _fail(3, f"{run_dir}/formal_metrics.json 的 equation/seed 和本轮对不上")
    relative_l2 = metrics["relative_l2"]
    is_number = isinstance(relative_l2, (int, float))
    if not is_number or not math.isfinite(relative_l2) or relative_l2 <= 0:
        _fail(4, f"{run_dir}/formal_metrics.json 的 relative_l2 不是有限正数：{relative_l2!r}")
    return float(relative_l2)


def main() -> None:
    seed = int(os.environ.get("AI4SCI_SEED", DEFAULT_SEED))
    metrics = {
        name: _read_variant(subdir, correction, seed) for name, subdir, correction in VARIANTS
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
