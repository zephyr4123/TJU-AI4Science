#!/usr/bin/env bash
# changelog.sh —— CHANGELOG.md 的机器判据。零依赖：bash 3.2+ / grep / sed / awk，本机与 CI runner 都能跑。
#
#   changelog.sh check [--tag vX.Y.Z] [FILE]   校验格式；带 --tag 时还要求最新发布版本 == tag
#   changelog.sh notes X.Y.Z [FILE]            打印某个版本的条目正文（发 GitHub Release 用）
#   changelog.sh release X.Y.Z [FILE]          把 Unreleased 轮转成「[X.Y.Z] - 今天」，并维护底部链接
#
# 格式遵循 Keep a Changelog：`## [Unreleased]` 在最前，其后是 `## [X.Y.Z] - YYYY-MM-DD` 按版本降序，
# 文件末尾是 `[Unreleased]: <url>` 与 `[X.Y.Z]: <url>` 链接引用。
set -euo pipefail

SEMVER='[0-9]+\.[0-9]+\.[0-9]+'
DATE='[0-9]{4}-[0-9]{2}-[0-9]{2}'

die() { echo "changelog: $*" >&2; exit 1; }

# 已发布版本号，按文件顺序
released_versions() {
  # 没有任何已发布版本时 grep 退 1，这里要吞掉：首次发版就是这种状态，不是错误
  grep -E "^## \[$SEMVER\] - $DATE\$" "$1" | sed -E 's/^## \[([^]]+)\].*/\1/' || true
}

# semver 比较：a > b 返回 0（不依赖 sort -V，BSD / GNU 行为不一致）
semver_gt() {
  awk -v a="$1" -v b="$2" 'BEGIN {
    split(a, x, "."); split(b, y, ".")
    for (i = 1; i <= 3; i++) { if (x[i]+0 > y[i]+0) exit 0; if (x[i]+0 < y[i]+0) exit 1 }
    exit 1
  }'
}

# 某个小节（Unreleased 或 X.Y.Z）的正文：去掉链接引用行、首尾空行
section_body() {
  local file="$1" ver="$2"
  # 标题匹配用字符串前缀而不是正则：-v 传进 awk 的值会再过一遍转义，带反斜杠的正则在 BSD / GNU awk 下行为不一致
  awk -v ver="$ver" '
    function is_head(line) {
      if (ver == "Unreleased") return line == "## [Unreleased]"
      return index(line, "## [" ver "] - ") == 1
    }
    /^## \[/ { if (inside) exit; if (is_head($0)) { inside = 1; next } }
    inside && /^\[[^]]+\]: / { next }
    inside { buf[n++] = $0 }
    END {
      s = 0; e = n - 1
      while (s <= e && buf[s] ~ /^[[:space:]]*$/) s++
      while (e >= s && buf[e] ~ /^[[:space:]]*$/) e--
      for (i = s; i <= e; i++) print buf[i]
    }' "$file"
}

cmd_check() {
  local tag="" file="CHANGELOG.md"
  while [ $# -gt 0 ]; do
    case "$1" in
      --tag) [ $# -ge 2 ] || die "--tag 后面要跟 vX.Y.Z"; tag="$2"; shift 2 ;;
      *) file="$1"; shift ;;
    esac
  done
  [ -f "$file" ] || die "缺 $file"
  grep -qE '^## \[Unreleased\]$' "$file" || die "$file 缺「## [Unreleased]」小节"
  [ "$(grep -m1 -E '^## \[' "$file")" = "## [Unreleased]" ] || die "「## [Unreleased]」必须是第一个版本小节"
  grep -qE '^\[Unreleased\]: https?://' "$file" || die "缺「[Unreleased]: <url>」链接引用行（release 轮转要用它推导仓库地址）"

  local bad
  bad=$(grep -E '^## \[' "$file" | grep -vE '^## \[Unreleased\]$' | grep -vE "^## \[$SEMVER\] - $DATE\$" || true)
  [ -z "$bad" ] || die "版本标题格式不对，应为「## [X.Y.Z] - YYYY-MM-DD」：
$bad"

  local prev="" v
  for v in $(released_versions "$file"); do
    if [ -n "$prev" ]; then
      semver_gt "$prev" "$v" || die "版本顺序不对：$prev 应严格大于其后的 ${v}（最新版本在最上面，不允许重复）"
    fi
    grep -qE "^\[$(printf '%s' "$v" | sed 's/\./\\./g')\]: https?://" "$file" || die "版本 $v 缺底部链接引用行「[$v]: <url>」"
    [ -n "$(section_body "$file" "$v")" ] || die "版本 $v 的小节是空的"
    prev="$v"
  done

  if [ -n "$tag" ]; then
    local want="${tag#v}" top
    printf '%s' "$want" | grep -qE "^$SEMVER\$" || die "tag 必须形如 vX.Y.Z，收到：$tag"
    top=$(released_versions "$file" | head -n1)
    [ -n "$top" ] || die "$file 里没有任何已发布版本，不能给 $tag 发版"
    [ "$top" = "$want" ] || die "tag $tag 与 $file 最新版本 [$top] 不一致 —— 先 make release VERSION=$want"
  fi
  echo "✓ $file 格式合规$( [ -n "$tag" ] && printf '，最新版本 %s 与 tag 一致' "$tag" )"
}

cmd_notes() {
  local ver="${1:-}" file="${2:-CHANGELOG.md}" body
  [ -n "$ver" ] || die "用法：changelog.sh notes X.Y.Z [FILE]"
  ver="${ver#v}"
  [ -f "$file" ] || die "缺 $file"
  body=$(section_body "$file" "$ver")
  [ -n "$body" ] || die "$file 里没有版本 $ver 的小节，或小节为空"
  printf '%s\n' "$body"
}

cmd_release() {
  local ver="${1:-}" file="${2:-CHANGELOG.md}" top base prev today tmp
  [ -n "$ver" ] || die "用法：changelog.sh release X.Y.Z [FILE]"
  ver="${ver#v}"
  printf '%s' "$ver" | grep -qE "^$SEMVER\$" || die "版本号必须形如 X.Y.Z，收到：$ver"
  cmd_check "$file" >/dev/null
  top=$(released_versions "$file" | head -n1)
  if [ -n "$top" ]; then
    semver_gt "$ver" "$top" || die "新版本 $ver 必须大于当前最新版本 $top"
  fi
  [ -n "$(section_body "$file" Unreleased)" ] || die "Unreleased 小节是空的，没有可发布的内容"
  # 仓库地址从现有的 [Unreleased] 链接推导：去掉 /compare/... 或 /commits/... 这类尾巴
  base=$(grep -m1 -E '^\[Unreleased\]: ' "$file" | sed -E 's/^\[Unreleased\]: //; s#/(compare|commits|releases|tree)/.*$##')
  [ -n "$base" ] || die "无法从 [Unreleased] 链接推导仓库地址"
  prev="$top"
  today=$(date +%F)
  tmp="$file.tmp.$$"
  awk -v ver="$ver" -v today="$today" -v base="$base" -v prev="$prev" '
    /^## \[Unreleased\]$/ && !h { print; print ""; print "## [" ver "] - " today; h = 1; next }
    /^\[Unreleased\]: / && !l {
      print "[Unreleased]: " base "/compare/v" ver "...HEAD"
      if (prev != "") print "[" ver "]: " base "/compare/v" prev "...v" ver
      else            print "[" ver "]: " base "/releases/tag/v" ver
      l = 1; next
    }
    { print }' "$file" > "$tmp"
  mv "$tmp" "$file"
  cmd_check --tag "v$ver" "$file" >/dev/null
  echo "✓ ${file}：Unreleased 已轮转为 [$ver] - $today"
}

case "${1:-}" in
  check)   shift; cmd_check "$@" ;;
  notes)   shift; cmd_notes "$@" ;;
  release) shift; cmd_release "$@" ;;
  *) sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'; exit 2 ;;
esac
