#!/usr/bin/env bash
# hygiene.sh —— 外层仓角色边界的机器判据（「机器判不了的规矩不是规矩」）：
#   1) git ls-files 里不许出现业务代码 —— 只放行 ./repos、.github/scripts/ 下的仓库工具、scripts/ 下的外部脚本
#   2) 大文件不进 git —— PDF / 数据集 / 模型权重走 LFS 或 NAS，仓里只放索引与结论
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

MAX_KB="${MAX_KB:-2048}"
rc=0

code=$(git ls-files | grep -E '\.(py|js|mjs|cjs|ts|tsx|jsx|go|rs|java|kt|swift|rb|c|cc|cpp|h|hpp|cs|php|scala)$' \
       | grep -vE '^(scripts/|\.github/scripts/)' || true)
if [ -n "$code" ]; then
  echo "✗ 外层仓追踪到了代码文件。业务代码放内仓（platform/），仓库工具放 .github/scripts/，外部脚本放 scripts/："
  printf '%s\n' "$code" | sed 's/^/    /'
  rc=1
fi

big=""
while IFS= read -r f; do
  [ -f "$f" ] || continue
  kb=$(( $(wc -c < "$f") / 1024 ))
  if [ "$kb" -gt "$MAX_KB" ]; then big="$big    $f (${kb} KB)"$'\n'; fi
done < <(git ls-files)
if [ -n "$big" ]; then
  echo "✗ 有超过 ${MAX_KB} KB 的文件进了 git。大文件走 LFS / NAS，仓里只放索引："
  printf '%s' "$big"
  rc=1
fi

if [ "$rc" -eq 0 ]; then echo "✓ 外层零业务代码、无大文件"; fi
exit "$rc"
