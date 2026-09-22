#!/usr/bin/env bash
# 唯一入口先删旧产物，避免上一轮的参数被误当成本轮成绩。
set -euo pipefail

: "${AI4SCI_PYTHON:?未设 AI4SCI_PYTHON}"
: "${AI4SCI_BUDGET_S:?未设 AI4SCI_BUDGET_S}"
: "${AI4SCI_INNER_K:?未设 AI4SCI_INNER_K}"

TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$TASK_DIR"
rm -f fit-*.json results.json
AI4SCI_START_EPOCH="$("$AI4SCI_PYTHON" -c 'import time; print(time.time())')"
export AI4SCI_START_EPOCH
RUN_BUDGET_S="$("$AI4SCI_PYTHON" -c \
  'import os; print(float(os.environ["AI4SCI_BUDGET_S"]) / int(os.environ["AI4SCI_INNER_K"]))')"

for ((run_index = 0; run_index < AI4SCI_INNER_K; run_index++)); do
  AI4SCI_RUN_BUDGET_S="$RUN_BUDGET_S" AI4SCI_RUN_INDEX="$run_index" \
    "$AI4SCI_PYTHON" code/fit_boehm.py
done
"$AI4SCI_PYTHON" harness/evaluate.py
