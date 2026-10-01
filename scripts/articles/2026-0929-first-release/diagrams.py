"""公众号稿（#193）的示意图：把 diagrams.html 里的 {{i:图标名}} 换成 Phosphor（regular）内联 SVG、
{{logo}} 换成平台的标，写到 materials/ 下（gitignore），再由 capture-diagrams.js 逐张截图。

跑法（外层仓根，只用标准库）：
  python3 scripts/articles/2026-0929-first-release/diagrams.py
  cd materials/articles/2026-0929-first-release && python3 -m http.server 8770   # 用 localhost 访问，CDN 的 referer 白名单认它
图标取自内仓页面的依赖（platform/ui/web/node_modules/@phosphor-icons/react），与页面同一套（纲领 P-17）。
"""

from __future__ import annotations

import re
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
DEFS = ROOT / "platform/ui/web/node_modules/@phosphor-icons/react/dist/defs"
LOGO = ROOT / "platform/ui/web/public/favicon.svg"
OUT = ROOT / "materials/articles/2026-0929-first-release/diagrams.html"


def icon(name: str) -> str:
    src = (DEFS / f"{name}.es.js").read_text(encoding="utf-8")
    block = src.split('"regular",', 1)[1].split('\n  ],', 1)[0]
    paths = re.findall(r'd: "([^"]+)"', block)
    if not paths:
        raise SystemExit(f"图标 {name} 的 regular 里没找到 path")
    body = "".join(f'<path d="{d}"/>' for d in paths)
    return f'<svg class="ic" viewBox="0 0 256 256" fill="currentColor">{body}</svg>'


def logo() -> str:
    d = re.search(r' d="([^"]+)"', LOGO.read_text(encoding="utf-8")).group(1)
    return f'<svg class="logo" viewBox="0 0 64 64" fill="currentColor"><path fill-rule="evenodd" d="{d}"/></svg>'


def main() -> None:
    html = (HERE / "diagrams.html").read_text(encoding="utf-8")
    html = html.replace("{{logo}}", logo())
    html = re.sub(r"\{\{i:(\w+)\}\}", lambda m: icon(m.group(1)), html)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
