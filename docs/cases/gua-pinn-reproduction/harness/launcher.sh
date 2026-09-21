#!/usr/bin/env bash
# 唯一执行入口：清上一轮的产物 → 用官方 trainer.py 原样跑 ConFIG 与 ConFIG+GUA
# 两个变体（论文表 8 · Burgers · 2-loss 列的两行）→ 评分。
set -euo pipefail
: "${AI4SCI_PYTHON:?未设 AI4SCI_PYTHON}"
: "${AI4SCI_BUDGET_S:?未设 AI4SCI_BUDGET_S}"
: "${AI4SCI_INNER_K:?未设 AI4SCI_INNER_K}"
TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$TASK_DIR"
SEED="${AI4SCI_SEED:-0}"
OUTPUT_DIR="$TASK_DIR/outputs"
rm -rf "$OUTPUT_DIR" results.json
AI4SCI_START_EPOCH="$("$AI4SCI_PYTHON" -c 'import time; print(time.time())')"
export AI4SCI_START_EPOCH

# 每个变体各分一半预算：两次调用都跑完这一轮才算数，一次超时就整轮失败。
BUDGET_INT="${AI4SCI_BUDGET_S%.*}"
HALF_BUDGET=$((BUDGET_INT / 2))

COMMON_ARGS=(
  --equation burgers
  --method config
  --n-losses 2
  --device cuda:0
  --random-seed "$SEED"
  --save-path "$OUTPUT_DIR"
  --run-folder-name run
)

(
  cd code
  timeout "$HALF_BUDGET" "$AI4SCI_PYTHON" experiments/PINN/trainer.py \
    "${COMMON_ARGS[@]}" --name none --optimizer-correction none
  timeout "$HALF_BUDGET" "$AI4SCI_PYTHON" experiments/PINN/trainer.py \
    "${COMMON_ARGS[@]}" --name gua --optimizer-correction gua
)

"$AI4SCI_PYTHON" harness/evaluate.py
