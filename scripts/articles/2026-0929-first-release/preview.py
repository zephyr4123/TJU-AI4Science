# /// script
# requires-python = ">=3.12"
# dependencies = ["markdown-it-py==3.0.*"]
# ///
"""公众号稿（#193）的手机宽度预览：把 docs/articles/2026-0929-first-release/README.md 排成公众号正文那一栏的宽度
（手机 375 px，?w=580 看电脑版），图片按栏宽缩放、图注取 alt、表格与链接照公众号常见样式。只看效果，不是导入公众号的格式。

跑法（外层仓根）：uv run scripts/articles/2026-0929-first-release/preview.py
然后在 materials/articles/2026-0929-first-release/ 起 python3 -m http.server 8770，打开 http://localhost:8770/preview.html
"""

from __future__ import annotations

import re
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).parents[3]
SRC = ROOT / "docs/articles/2026-0929-first-release/README.md"
OUT_DIR = ROOT / "materials/articles/2026-0929-first-release"

CSS = """
:root { --w: 375px; --primary: #2F4BC9; }
* { box-sizing: border-box; }
body { margin: 0; background: #EDEDED; font-family: -apple-system, "PingFang SC", "Hiragino Sans GB", sans-serif; }
.phone { width: var(--w); margin: 24px auto; background: #fff; padding: 22px 16px 40px; color: #333; font-size: 17px; line-height: 1.75; letter-spacing: .3px; }
h1 { font-size: 22px; line-height: 1.4; color: #111; margin: 0 0 12px; }
h2 { font-size: 19px; color: var(--primary); margin: 36px 0 12px; }
h3 { font-size: 17px; color: #111; margin: 28px 0 8px; padding-left: 10px; border-left: 3px solid var(--primary); line-height: 1.4; }
p { margin: 0 0 8px; text-align: justify; }  /* 段落靠首行缩进区分（正文里的 &emsp;&emsp;），段间距收小 */
blockquote { margin: 20px 0; padding: 12px 14px; background: #F4F6FD; border-left: 3px solid var(--primary); color: #1C2230; font-weight: 600; }
blockquote p { margin: 0; }
figure { margin: 18px 0 22px; }
figure img { display: block; width: 100%; height: auto; border-radius: 4px; }
figcaption { margin-top: 6px; font-size: 13px; line-height: 1.5; color: #888; text-align: center; }
code { font-family: Menlo, monospace; font-size: 14px; background: #F4F5F7; padding: 1px 4px; border-radius: 3px; }
pre { background: #F4F5F7; padding: 10px 12px; overflow-x: auto; border-radius: 4px; }
pre code { background: none; padding: 0; font-size: 12.5px; line-height: 1.6; }
ul { padding-left: 20px; }
a { color: var(--primary); text-decoration: none; border-bottom: 1px solid #C9D2F3; overflow-wrap: break-word; }
table { width: 100%; border-collapse: collapse; margin: 14px 0 20px; font-size: 13.5px; line-height: 1.55; }
th, td { border: 1px solid #E3E6EC; padding: 6px 8px; text-align: left; vertical-align: top; }
th { background: #F4F6FD; color: #1C2230; font-weight: 600; }
td code, th code { font-size: 12px; }
h2 + ul { padding-left: 18px; }
.byline p { margin: 0 0 14px; font-size: 13.5px; line-height: 1.7; color: #888; }
.byline strong { color: #555; }
strong { color: #1C2230; }
"""


def main() -> None:
    md = SRC.read_text(encoding="utf-8")
    # doocs/md 用 markdown-it（严格的 CommonMark）；这里用同一套规则渲染，预览里看到的就是 doocs 里看到的
    html = MarkdownIt("commonmark", {"html": True}).enable("table").render(md)
    text_only = re.sub(r"<code>.*?</code>|<pre>.*?</pre>", "", html, flags=re.S)
    if "**" in text_only:
        spots = [text_only[max(0, i - 20) : i + 22].replace("\n", " ") for i in [m.start() for m in re.finditer(r"\*\*", text_only)]]
        raise SystemExit("有加粗没渲染出来（CommonMark 的定界规则：收尾的 ** 前是标点、后面紧跟文字就不算闭合）：\n" + "\n".join(spots))
    # 独占一段的图 → figure + 图注（公众号常见的排法）
    html = re.sub(
        r'<p><img src="([^"]+)" alt="([^"]*)" ?/?></p>',
        lambda m: f'<figure><img src="{m.group(1)}" alt="{m.group(2)}">'
        + (f"<figcaption>{m.group(2)}</figcaption>" if m.group(2) else "") + "</figure>",
        html,
    )
    # 标题下面一行署名（作者、实验室、指导老师、日期）排成小字
    html = re.sub(r"(</h1>\s*)<p>(<strong>作者</strong>.*?)</p>", r'\1<div class="byline"><p>\2</p></div>', html, count=1, flags=re.S)
    page = f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>公众号稿预览</title>
<style>{CSS}</style>
<script>const w = new URLSearchParams(location.search).get('w'); if (w) document.documentElement.style.setProperty('--w', w + 'px');</script>
</head><body><article class="phone">{html}</article></body></html>"""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "preview.html").write_text(page, encoding="utf-8")
    print((OUT_DIR / "preview.html").relative_to(ROOT))


if __name__ == "__main__":
    main()
