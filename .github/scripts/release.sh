#!/usr/bin/env bash
# release.sh X.Y.Z —— 本地发版三步：轮转 CHANGELOG → 提交「发布 vX.Y.Z」→ 打 annotated tag。
# 不 push：推送是出分支的动作，由人执行；tag 一推上去 GitHub Actions 就会出包并建 Release。
set -euo pipefail

die() { echo "release: $*" >&2; exit 1; }

VER="${1:-}"
[ -n "$VER" ] || die "用法：make release VERSION=X.Y.Z"
VER="${VER#v}"

cd "$(git rev-parse --show-toplevel)"
[ -z "$(git status --porcelain)" ] || die "工作区不干净，先提交或 stash 再发版"
git rev-parse -q --verify "refs/tags/v$VER" >/dev/null && die "tag v$VER 已存在"

BRANCH=$(git branch --show-current)
[ -n "$BRANCH" ] || die "当前是 detached HEAD，先 checkout 到分支"
[ "$BRANCH" = "main" ] || echo "release: 注意，当前在分支 $BRANCH 而不是 main" >&2

.github/scripts/changelog.sh release "$VER"
git add CHANGELOG.md
git commit -q -m "发布 v$VER"
git tag -a "v$VER" -m "v$VER"

echo "✓ 已提交并打 tag v${VER}（尚未推送）"
echo "  推送并触发发布流水线：git push origin $BRANCH --follow-tags"
