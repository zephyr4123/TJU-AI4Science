#!/usr/bin/env bash
# 唯一入口；固定目录名使评分只会读取本轮、同一配置的原始产物。
set -euo pipefail

: "${AI4SCI_PYTHON:?未设 AI4SCI_PYTHON}"
: "${AI4SCI_BUDGET_S:?未设 AI4SCI_BUDGET_S}"
: "${AI4SCI_INNER_K:?未设 AI4SCI_INNER_K}"

TASK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$TASK_DIR"
SEED="${AI4SCI_SEED:-42}"
BUDGET_S="${AI4SCI_BUDGET_S%.*}"

if [ "$BUDGET_S" -lt 1 ]; then
  echo "launcher: AI4SCI_BUDGET_S 必须至少为 1 秒" >&2
  exit 1
fi

rm -rf outputs results.json
AI4SCI_START_EPOCH="$("$AI4SCI_PYTHON" -c 'import time; print(time.time())')"
export AI4SCI_START_EPOCH

# 表 8 同时比较 ConFIG 与 ConFIG+GUA，必须在相同种子下各跑一次。
for ((inner_idx = 1; inner_idx <= AI4SCI_INNER_K; inner_idx++)); do
  run_folder="seed-${SEED}-inner-${inner_idx}"
  (
    cd code/experiments/PINN
    timeout "$BUDGET_S" "$AI4SCI_PYTHON" trainer.py \
      --equation burgers \
      --method config \
      --name config_2loss \
      --n-losses 2 \
      --optimizer-correction none \
      --random-seed "$SEED" \
      --save-path "$TASK_DIR/outputs" \
      --run-folder-name "$run_folder"
  )
  (
    cd code/experiments/PINN
    timeout "$BUDGET_S" "$AI4SCI_PYTHON" trainer.py \
      --equation burgers \
      --method config \
      --name config_2loss_gua \
      --n-losses 2 \
      --optimizer-correction gua \
      --random-seed "$SEED" \
      --save-path "$TASK_DIR/outputs" \
      --run-folder-name "$run_folder"
  )
done

"$AI4SCI_PYTHON" harness/evaluate.py
