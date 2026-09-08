#!/usr/bin/env python3
"""md2html —— 把调研目录里的 README.md 渲染成阅读版 index.html。

原则：
  - md 是唯一原始稿，html 是构建产物；只在本地生成、随 md 一起进 git，不上传到任何托管服务。
  - 输出必须确定：不写时间戳、不带随机 id。`make html` 之后 git 无 diff 才算同步，CI 有这条检查。
  - 标题锚点按 GitHub 的规则生成，md 里写的 `#锚点` 在 GitHub 页面和本地 html 里都能跳。
  - 文内链接必须能落地：指向不存在的标题或脚注直接报错退非 0，这是本工具存在的主要理由。

用法：
  md2html.py build <README.md> [...]     渲染到同目录 index.html
  md2html.py build --all                 渲染 research/*/*/README.md 全部
  md2html.py backrefs <README.md>        打印每个标题被哪些章节链接到（给「被引用」行用）
"""
import argparse
import html
import re
import sys
from pathlib import Path

import markdown
from markdown.extensions.toc import TocExtension

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TEMPLATE = HERE / "template.html"
EXTENSIONS = ["tables", "footnotes", "attr_list", "fenced_code", "sane_lists", "md_in_html"]

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
ANCHOR_LINK_RE = re.compile(r"\]\(#([^)\s]+)\)")
FOOTNOTE_REF_RE = re.compile(r"\[\^([^\]]+)\](?!:)")
FOOTNOTE_DEF_RE = re.compile(r"^\[\^([^\]]+)\]:", re.M)


def github_slug(value, separator="-"):
    """GitHub 的标题锚点规则：小写；去掉字母、数字、空格、连字符、下划线以外的字符；空格变连字符。
    中文算字母保留，中文标点（：、——（））被去掉。重复标题不做去重，靠作者用编号避免。"""
    value = value.strip().lower()
    value = "".join(ch for ch in value if ch.isalnum() or ch in " -_")
    return value.replace(" ", separator)


def split_front_matter(text):
    """开头 `---` 包起来的 key: value 块是元数据（标题、截止日期、范围……）。不引入 yaml 依赖，只认单行键值。"""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    meta = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith("#"):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, text[end + 5:]


def strip_code_blocks(body):
    """检查锚点时忽略围栏代码块里的内容（ASCII 图里可能有 `](#` 形状的字符）。"""
    return re.sub(r"```.*?```", "", body, flags=re.S)


def headings(body):
    out = []
    for line in strip_code_blocks(body).splitlines():
        m = HEADING_RE.match(line)
        if m:
            out.append((len(m.group(1)), m.group(2), github_slug(m.group(2))))
    return out


def check_links(path, body):
    """文内锚点与脚注都必须能落地。这是「文献和内容关联起来」的机器判据。"""
    slugs = {s for _, _, s in headings(body)}
    dupes = [s for s in slugs if sum(1 for _, _, x in headings(body) if x == s) > 1]
    text = strip_code_blocks(body)
    defs = set(FOOTNOTE_DEF_RE.findall(text))
    refs = set(FOOTNOTE_REF_RE.findall(text))
    problems = []
    for target in ANCHOR_LINK_RE.findall(text):
        if target.startswith("fn:") or target.startswith("fnref:"):
            continue
        if target not in slugs:
            problems.append(f"文内链接 #{target} 指向不存在的标题")
    for ref in sorted(refs - defs):
        problems.append(f"脚注 [^{ref}] 没有定义")
    for d in sorted(defs - refs):
        problems.append(f"脚注定义 [^{d}] 没有被引用")
    for s in sorted(set(dupes)):
        problems.append(f"标题锚点重复：#{s}（给标题加编号区分）")
    if problems:
        print(f"✗ {path}：", file=sys.stderr)
        for p in problems:
            print(f"    {p}", file=sys.stderr)
        return False
    return True


def render_meta(meta):
    """元数据块：只渲染认识的键，顺序固定。"""
    labels = [("kind", "类型"), ("date", "调研截止"), ("scope", "范围"), ("status", "状态")]
    rows = [f'<div class="meta-row"><dt>{html.escape(zh)}</dt><dd>{html.escape(meta[k])}</dd></div>'
            for k, zh in labels if meta.get(k)]
    return f'<dl class="meta">{"".join(rows)}</dl>' if rows else ""


def build(path):
    src = Path(path)
    text = src.read_text(encoding="utf-8")
    meta, body = split_front_matter(text)
    if not check_links(src, body):
        return False
    md = markdown.Markdown(
        extensions=EXTENSIONS + [TocExtension(slugify=github_slug, toc_depth="2-3", permalink="#",
                                              permalink_class="permalink", permalink_title="本节链接")],
        extension_configs={"footnotes": {"BACKLINK_TITLE": "回到正文第 %d 处", "BACKLINK_TEXT": "↩",
                                         "SUPERSCRIPT_TEXT": "{}"}},
        output_format="html5",
    )
    content = md.convert(body)
    # 表格和代码块要能在自己的容器里横向滚动，正文永远不横向滚
    content = re.sub(r"<table>", '<div class="table-wrap"><table>', content)
    content = re.sub(r"</table>", "</table></div>", content)
    page = TEMPLATE.read_text(encoding="utf-8")
    title = meta.get("title") or src.parent.name
    for key, val in {
        "{{title}}": html.escape(title),
        "{{subtitle}}": html.escape(meta.get("subtitle", "")),
        "{{meta}}": render_meta(meta),
        "{{toc}}": md.toc,
        "{{body}}": content,
        "{{source}}": html.escape(src.name),
    }.items():
        page = page.replace(key, val)
    out = src.parent / "index.html"
    out.write_text(page, encoding="utf-8")
    print(f"✓ {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")
    return True


def backrefs(path):
    """每个标题被哪些章节链接到。章节 = 最近的 h2 / h3 编号，用来手写「被引用」行。"""
    _, body = split_front_matter(Path(path).read_text(encoding="utf-8"))
    current = "（开头）"
    hits = {}
    for line in strip_code_blocks(body).splitlines():
        m = HEADING_RE.match(line)
        if m and len(m.group(1)) in (2, 3):
            num = m.group(2).split(" ", 1)[0].rstrip(".")
            current = f"§{num}" if num[:1].isdigit() else m.group(2)
        for target in ANCHOR_LINK_RE.findall(line):
            hits.setdefault(target, [])
            if current not in hits[target]:
                hits[target].append(current)
    for target, secs in sorted(hits.items()):
        print(f"#{target}\t{'、'.join(secs)}")
    return True


def main():
    p = argparse.ArgumentParser(prog="md2html")
    sub = p.add_subparsers(dest="cmd", required=True)
    pb = sub.add_parser("build")
    pb.add_argument("files", nargs="*")
    pb.add_argument("--all", action="store_true", help="research/*/*/README.md 全部")
    pr = sub.add_parser("backrefs")
    pr.add_argument("file")
    a = p.parse_args()
    if a.cmd == "backrefs":
        return 0 if backrefs(a.file) else 1
    files = [Path(f) for f in a.files]
    if a.all:
        files += sorted((ROOT / "research").glob("*/*/README.md"))
    if not files:
        if a.all:
            print("（research/*/*/README.md 一个都没有，无事可做）")
            return 0
        p.error("给文件，或用 --all")
    ok = all([build(f) for f in files])  # 列表推导：全部都跑，不因第一个失败短路
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
