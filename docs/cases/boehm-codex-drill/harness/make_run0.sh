#!/usr/bin/env bash
# 基线重复保留相同流程，才能让 sigma 反映优化器随机起点的波动。
set -euo pipefail

TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$TASK_DIR"
export AI4SCI_PYTHON="${AI4SCI_PYTHON:-$TASK_DIR/.venv/bin/python}"
: "${AI4SCI_BUDGET_S:?未设 AI4SCI_BUDGET_S：经 ai4sci cap design 起}"
: "${AI4SCI_INNER_K:?未设 AI4SCI_INNER_K：经 ai4sci cap design 起}"
if [ ! -x "$AI4SCI_PYTHON" ]; then
  echo "make_run0: 任务环境不存在：$AI4SCI_PYTHON（由 ai4sci cap design 建）" >&2
  exit 1
fi

SEEDS=(42 43 44)
rm -rf baseline
mkdir -p baseline/repeats
AI4SCI_SEED=42 harness/launcher.sh
cp results.json baseline/results.json
# 诊断与基线同源，方便人工确认固定参数没有被误当成优化维度。
cp fit-0.json baseline/diagnostics.json
for seed in "${SEEDS[@]}"; do
  AI4SCI_SEED="$seed" harness/launcher.sh
  cp results.json "baseline/repeats/results-${seed}.json"
done
"$AI4SCI_PYTHON" - <<'PY'
import json
import statistics
from pathlib import Path

run0 = Path("baseline")
docs = [
    json.loads(path.read_text(encoding="utf-8"))
    for path in sorted(run0.glob("repeats/results-*.json"))
]
docs.sort(key=lambda doc: doc["seed"])
seeds = [doc["seed"] for doc in docs]
sigma = {}
for name in docs[0]["metrics"]:
    values = [doc["metrics"][name] for doc in docs]
    sigma[name] = {
        "sigma": statistics.stdev(values) if len(values) > 1 else 0.0,
        "seeds": seeds,
        "values": values,
    }
(run0 / "sigma.json").write_text(json.dumps(sigma), encoding="utf-8")
print("sigma.json:", {key: round(value["sigma"], 6) for key, value in sigma.items()})
PY
rm -f fit-*.json results.json
echo "baseline 就绪"
