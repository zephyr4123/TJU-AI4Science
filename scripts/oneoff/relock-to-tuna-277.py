# /// script
# requires-python = ">=3.12"
# ///
"""把 skill 脚本的锁文件从官方 PyPI 的地址换成清华镜像（外层 #277，一次性）。

为什么：onboarding 要全程国内源。uv 照锁文件装依赖时用锁文件里写的地址（files.pythonhosted.org），
不看 UV_DEFAULT_INDEX，uv 0.12.18 也没有把锁文件地址换成镜像的开关。清华的路径与 pythonhosted 一一
对应（/pypi/web/packages/<同一段>），所以只换前缀：包名、版本、哈希一字不改。

先核对：每个包取一次清华的索引页（PEP 503），锁文件里的每个文件都得在上面，缺一个就不改、列出来。
不加 --apply 只核对、报数；加了才写。

    uv run scripts/oneoff/relock-to-tuna-277.py platform
    uv run scripts/oneoff/relock-to-tuna-277.py platform --apply
"""

from __future__ import annotations

import argparse
import html.parser
import sys
import tomllib
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

OFFICIAL_INDEX = 'registry = "https://pypi.org/simple"'
TUNA_INDEX = 'registry = "https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple"'
OFFICIAL_FILES = "https://files.pythonhosted.org/packages/"
TUNA_FILES = "https://mirrors.tuna.tsinghua.edu.cn/pypi/web/packages/"
TUNA_SIMPLE = "https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple"
LIBRARIES = ("skills", "skills-curated", "domains")
WORKERS = 4  # 清华有限流，慢一点


class _Links(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.files: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            href = dict(attrs).get("href") or ""
            self.files.add(href.split("#", 1)[0].rsplit("/", 1)[-1])


def locks(platform: Path) -> list[Path]:
    return sorted(p for lib in LIBRARIES for p in (platform / lib).rglob("*.py.lock"))


def wanted(files: list[Path]) -> dict[str, set[str]]:
    """包名 → 锁文件里要从 pythonhosted 下的文件名。"""
    found: dict[str, set[str]] = {}
    for lock in files:
        for pkg in tomllib.loads(lock.read_text(encoding="utf-8")).get("package", []):
            urls = [w["url"] for w in pkg.get("wheels", [])]
            if "sdist" in pkg and "url" in pkg["sdist"]:
                urls.append(pkg["sdist"]["url"])
            for url in urls:
                if url.startswith(OFFICIAL_FILES):
                    found.setdefault(pkg["name"], set()).add(url.rsplit("/", 1)[-1])
    return found


def on_tuna(name: str) -> set[str]:
    req = urllib.request.Request(f"{TUNA_SIMPLE}/{name}/", headers={"User-Agent": "ai4sci-relock"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        parser = _Links()
        parser.feed(resp.read().decode("utf-8", errors="replace"))
    return parser.files


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("platform", type=Path, help="内仓目录")
    ap.add_argument("--apply", action="store_true", help="核对都在才写")
    args = ap.parse_args()
    files = locks(args.platform)
    need = wanted(files)
    total = sum(len(v) for v in need.values())
    print(f"{len(files)} 份锁文件，{len(need)} 个包，{total} 个文件要从清华取")
    with ThreadPoolExecutor(WORKERS) as pool:
        listed = dict(zip(need, pool.map(on_tuna, need), strict=True))
    missing = sorted(f"{name}: {f}" for name, fs in need.items() for f in fs - listed[name])
    if missing:
        print(f"清华上缺 {len(missing)} 个文件，不改：", *missing, sep="\n  ", file=sys.stderr)
        return 1
    print("全在清华上")
    changed = 0
    for lock in files:
        text = lock.read_text(encoding="utf-8")
        new = text.replace(OFFICIAL_INDEX, TUNA_INDEX).replace(OFFICIAL_FILES, TUNA_FILES)
        if new != text:
            changed += 1
            if args.apply:
                lock.write_text(new, encoding="utf-8")
    print(f"{'改了' if args.apply else '要改'} {changed} 份")
    return 0


if __name__ == "__main__":
    sys.exit(main())
