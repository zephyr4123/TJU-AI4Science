#!/usr/bin/env bash
# changelog.sh —— CHANGELOG.md 的机器判据。零依赖：bash 3.2+ / grep / sed / awk / wc，本机与 CI runner 都能跑。
#
#   changelog.sh check [--tag vX.Y.Z | vX.Y.Z-rc.N] [FILE]
#       校验格式；带 --tag：正式版要求最新发布版本 == tag，预发布（-rc.N）要求 X.Y.Z 还没发过且 Unreleased 非空
#   changelog.sh notes X.Y.Z | X.Y.Z-rc.N [FILE]
#       打印某个版本的条目正文（发 GitHub Release 用）；预发布打印 Unreleased 的正文
#   changelog.sh release X.Y.Z [FILE]
#       把 Unreleased 轮转成「[X.Y.Z] - 今天」，并维护底部链接；预发布不轮转（只打 tag）
#
# 格式遵循 Keep a Changelog：`## [Unreleased]` 在最前，其后是 `## [X.Y.Z] - YYYY-MM-DD` 按版本降序，
# 文件末尾是 `[Unreleased]: <url>` 与 `[X.Y.Z]: <url>` 链接引用。
# Unreleased 的写法（ADR-0004）：一条一行、≤ 200 字（按 600 字节算）、带 #issue 或链接；分类只用 新增 / 变更 / 修复 / 移除 / 安全。
# 历史小节不回查：规矩从 1.0.0 起生效。
set -euo pipefail

SEMVER='[0-9]+\.[0-9]+\.[0-9]+'
PRERELEASE='-rc\.[0-9]+'
DATE='[0-9]{4}-[0-9]{2}-[0-9]{2}'
MAX_ENTRY_BYTES=600
CATEGORIES='新增|变更|修复|移除|安全'

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

# Unreleased 的写法：只许「### 分类」与「- 一行一条」；每条 ≤ MAX_ENTRY_BYTES 字节、带 #issue 或链接
check_unreleased_entries() {
  local file="$1" line n bad=""
  while IFS= read -r line; do
    [ -n "$line" ] || continue
    if printf '%s' "$line" | grep -qE '^### '; then
      printf '%s' "$line" | grep -qE "^### ($CATEGORIES)\$" || bad="$bad
    分类只用 新增 / 变更 / 修复 / 移除 / 安全：$line"
      continue
    fi
    if ! printf '%s' "$line" | grep -qE '^- '; then
      bad="$bad
    不是「- 」开头的一条（一条一行，不换行续写）：${line:0:60}"
      continue
    fi
    n=$(printf '%s' "$line" | wc -c | tr -d ' ')
    [ "$n" -le "$MAX_ENTRY_BYTES" ] || bad="$bad
    超过 200 字（细节写进 issue，这里只留一句）：${line:0:60}…"
    printf '%s' "$line" | grep -qE '#[0-9]+|https?://' || bad="$bad
    没带 #issue 或链接：${line:0:60}"
  done <<EOF
$(section_body "$file" Unreleased)
EOF
  [ -z "$bad" ] || die "Unreleased 的条目不合规矩（一条一行、≤ 200 字、带 #issue；见 CONTRIBUTING「CHANGELOG 怎么写」）：$bad"
}

cmd_check() {
  local tag="" file="CHANGELOG.md"
  while [ $# -gt 0 ]; do
    case "$1" in
      --tag) [ $# -ge 2 ] || die "--tag 后面要跟 vX.Y.Z 或 vX.Y.Z-rc.N"; tag="$2"; shift 2 ;;
      *) file="$1"; shift ;;
    esac
  done
  [ -f "$file" ] || die "缺 $file"
  grep -qE '^## \[Unreleased\]$' "$file" || die "$file 缺「## [Unreleased]」小节"
  [ "$(grep -m1 -E '^## \[' "$file")" = "## [Unreleased]" ] || die "「## [Unreleased]」必须是第一个版本小节"
  # 链接引用允许写 TBD 占位（仓库远端还没定时不编造地址），但 release 时必须已是真实地址
  grep -qE '^\[Unreleased\]: (https?://|TBD$)' "$file" || die "缺「[Unreleased]: <url>」链接引用行（远端未定可先写 TBD；release 轮转要用它推导仓库地址）"

  local bad
  bad=$(grep -E '^## \[' "$file" | grep -vE '^## \[Unreleased\]$' | grep -vE "^## \[$SEMVER\] - $DATE\$" || true)
  [ -z "$bad" ] || die "版本标题格式不对，应为「## [X.Y.Z] - YYYY-MM-DD」（预发布不占小节）：
$bad"

  local prev="" v
  for v in $(released_versions "$file"); do
    if [ -n "$prev" ]; then
      semver_gt "$prev" "$v" || die "版本顺序不对：$prev 应严格大于其后的 ${v}（最新版本在最上面，不允许重复）"
    fi
    grep -qE "^\[$(printf '%s' "$v" | sed 's/\./\\./g')\]: (https?://|TBD$)" "$file" || die "版本 $v 缺底部链接引用行「[$v]: <url>」（远端未定可先写 TBD）"
    [ -n "$(section_body "$file" "$v")" ] || die "版本 $v 的小节是空的"
    prev="$v"
  done

  check_unreleased_entries "$file"

  if [ -n "$tag" ]; then
    local want="${tag#v}" top base
    top=$(released_versions "$file" | head -n1)
    if printf '%s' "$want" | grep -qE "^$SEMVER$PRERELEASE\$"; then
      # 预发布：X.Y.Z 还没发过（要严格大于已发的最新版），Unreleased 里有东西可发
      base=$(printf '%s' "$want" | sed -E 's/-rc\.[0-9]+$//')  # bash 3.2 的 ${x%%-rc.*} 在 UTF-8 下会炸，用 sed
      if [ -n "$top" ]; then
        semver_gt "$base" "$top" || die "预发布 $tag 的版本 $base 必须大于已发布的最新版本 $top"
      fi
      [ -n "$(section_body "$file" Unreleased)" ] || die "Unreleased 小节是空的，没有可预发布的内容"
      echo "✓ $file 格式合规，预发布 $tag 对应 Unreleased（尚未发布 ${base}）"
      return 0
    fi
    printf '%s' "$want" | grep -qE "^$SEMVER\$" || die "tag 必须形如 vX.Y.Z 或 vX.Y.Z-rc.N，收到：$tag"
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
  if printf '%s' "$ver" | grep -qE "^$SEMVER$PRERELEASE\$"; then
    body=$(section_body "$file" Unreleased)
    [ -n "$body" ] || die "Unreleased 小节是空的，预发布 $ver 没有条目"
    printf '预发布 %s：下面是尚未正式发布的条目（正式版发布时轮转进 [%s]）。\n\n%s\n' "$ver" "$(printf '%s' "$ver" | sed -E 's/-rc\.[0-9]+$//')" "$body"
    return 0
  fi
  body=$(section_body "$file" "$ver")
  [ -n "$body" ] || die "$file 里没有版本 $ver 的小节，或小节为空"
  printf '%s\n' "$body"
}

cmd_release() {
  local ver="${1:-}" file="${2:-CHANGELOG.md}" top base prev today tmp
  [ -n "$ver" ] || die "用法：changelog.sh release X.Y.Z [FILE]"
  ver="${ver#v}"
  if printf '%s' "$ver" | grep -qE "^$SEMVER$PRERELEASE\$"; then
    die "预发布 $ver 不轮转 CHANGELOG：直接打 tag（make release 会跳过这一步）"
  fi
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
  [ "$base" != "TBD" ] || die "[Unreleased] 链接还是 TBD 占位：先把它填成真实仓库地址（如 https://github.com/<owner>/<repo>/commits/main）再发版"
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
  *) sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 2 ;;
esac
