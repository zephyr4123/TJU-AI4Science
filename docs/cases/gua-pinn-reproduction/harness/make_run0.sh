#!/usr/bin/env bash
# 复现结果：基线一次 + repeat_k 次重复 + σ。
set -euo pipefail
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$TASK_DIR"
export AI4SCI_PYTHON="${AI4SCI_PYTHON:-$TASK_DIR/.venv/bin/python}"
: "${AI4SCI_BUDGET_S:?未设 AI4SCI_BUDGET_S：经 ai4sci cap reproduction 起}"
: "${AI4SCI_INNER_K:?未设 AI4SCI_INNER_K：经 ai4sci cap reproduction 起}"
if [ ! -x "$AI4SCI_PYTHON" ]; then
  echo "make_run0: 任务环境不存在：$AI4SCI_PYTHON" >&2
  exit 1
fi
SEEDS=(1 2 3 4)   # 与 scoring.budget.repeat_k=4 对应；基线 0 + 这 4 个 = 论文的种子 {0,1,2,3,4}
rm -rf baseline
mkdir -p baseline/repeats
AI4SCI_SEED=0 harness/launcher.sh
cp results.json baseline/results.json
for seed in "${SEEDS[@]}"; do
  AI4SCI_SEED="$seed" harness/launcher.sh
  cp results.json "baseline/repeats/results-${seed}.json"
done
"$AI4SCI_PYTHON" - <<'PY'
import json
import statistics
from pathlib import Path

run0 = Path("baseline")
docs = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(run0.glob("repeats/results-*.json"))]
docs.sort(key=lambda d: d["seed"])
seeds = [d["seed"] for d in docs]
sigma = {}
for name in docs[0]["metrics"]:
    values = [d["metrics"][name] for d in docs]
    sigma[name] = {"sigma": statistics.stdev(values) if len(values) > 1 else 0.0,
                   "seeds": seeds, "values": values}
(run0 / "sigma.json").write_text(json.dumps(sigma), encoding="utf-8")
print("sigma.json:", {k: round(v["sigma"], 6) for k, v in sigma.items()})
PY
rm -rf outputs results.json
echo "baseline 就绪"
