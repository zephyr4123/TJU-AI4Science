#!/usr/bin/env bash
# release.sh X.Y.Z | X.Y.Z-rc.N —— 本地发版（CONTRIBUTING「发一个版本」，ADR-0004）：
#   正式版 X.Y.Z：轮转 CHANGELOG → 提交「发布 vX.Y.Z」→ 打 annotated tag。在 main 上做。
#   预发布 X.Y.Z-rc.N：只打 annotated tag，不动 CHANGELOG（Release Notes 取 Unreleased）。在 release/X.Y 上做。
# 不 push：推送是出分支的动作，由人执行；tag 一推上去 GitHub Actions 就会建 Release（外层只出 Release Notes，
# 内仓的流水线出 wheel；-rc.N 标 pre-release）。
set -euo pipefail

die() { echo "release: $*" >&2; exit 1; }

VER="${1:-}"
[ -n "$VER" ] || die "用法：make release VERSION=X.Y.Z 或 VERSION=X.Y.Z-rc.N"
VER="${VER#v}"

SEMVER='[0-9]+\.[0-9]+\.[0-9]+'
if printf '%s' "$VER" | grep -qE "^$SEMVER-rc\.[0-9]+\$"; then PRE=1
elif printf '%s' "$VER" | grep -qE "^$SEMVER\$"; then PRE=0
else die "版本号必须形如 X.Y.Z 或 X.Y.Z-rc.N，收到：$VER"; fi

cd "$(git rev-parse --show-toplevel)"
[ -z "$(git status --porcelain)" ] || die "工作区不干净，先提交或 stash 再发版"
git rev-parse -q --verify "refs/tags/v$VER" >/dev/null && die "tag v$VER 已存在"

BRANCH=$(git branch --show-current)
[ -n "$BRANCH" ] || die "当前是 detached HEAD，先 checkout 到分支"

if [ "$PRE" = 1 ]; then
  case "$BRANCH" in release/*) ;; *) echo "release: 注意，预发布通常在 release/X.Y 分支上打，当前在 $BRANCH" >&2 ;; esac
  .github/scripts/changelog.sh check --tag "v$VER"
  git tag -a "v$VER" -m "v${VER}（预发布）"
  echo "✓ 已打预发布 tag v${VER}（不轮转 CHANGELOG，尚未推送）"
  echo "  推送并触发发布流水线：git push origin $BRANCH --follow-tags"
  exit 0
fi

[ "$BRANCH" = "main" ] || echo "release: 注意，正式版应在 main 上发，当前在分支 $BRANCH" >&2

.github/scripts/changelog.sh release "$VER"
git add CHANGELOG.md
git commit -q -m "发布 v$VER"
git tag -a "v$VER" -m "v$VER"

echo "✓ 已提交并打 tag v${VER}（尚未推送）"
echo "  推送并触发发布流水线：git push origin $BRANCH --follow-tags"
