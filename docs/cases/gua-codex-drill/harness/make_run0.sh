#!/usr/bin/env bash
# 五次独立运行用于样本标准差；42 是平台规定的基线种子。
set -euo pipefail

: "${AI4SCI_PYTHON:?未设 AI4SCI_PYTHON}"
: "${AI4SCI_BUDGET_S:?未设 AI4SCI_BUDGET_S：经 ai4sci cap reproduction 起}"
: "${AI4SCI_INNER_K:?未设 AI4SCI_INNER_K：经 ai4sci cap reproduction 起}"

TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$TASK_DIR"
SEEDS=(43 44 45 46)  # repeat_k=4；连同基线共五次，供样本标准差使用。

rm -rf baseline
mkdir -p baseline/repeats
AI4SCI_SEED=42 harness/launcher.sh
cp results.json baseline/results.json
for seed in "${SEEDS[@]}"; do
  AI4SCI_SEED="$seed" harness/launcher.sh
  cp results.json "baseline/repeats/results-${seed}.json"
done

"$AI4SCI_PYTHON" - <<'PY'
import json
import statistics
from pathlib import Path

root = Path("baseline")
# σ 只由真正的重复运行组成，不能把单独保存的基线结果混进来。
paths = sorted((root / "repeats").glob("results-*.json"))
docs = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
docs.sort(key=lambda doc: doc["seed"])
seeds = [doc["seed"] for doc in docs]
sigma = {}
for name in docs[0]["metrics"]:
    values = [doc["metrics"][name] for doc in docs]
    sigma[name] = {
        "sigma": statistics.stdev(values),
        "seeds": seeds,
        "values": values,
    }
(root / "sigma.json").write_text(json.dumps(sigma), encoding="utf-8")
print("sigma.json:", {name: round(item["sigma"], 6) for name, item in sigma.items()})
PY

rm -rf outputs results.json
echo "baseline 就绪"
