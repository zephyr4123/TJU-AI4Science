#!/usr/bin/env python3
"""把 2026-09-18 之前平铺在 platform/runs/ 里的东西按归属搬进 workspaces/<id>/（外层 #72）。

一次性工具：只搬不删，搬过的逐条打印，回滚就是按打印的行搬回去。规则只有三条：

  runs/<run>/            有 checkpoint.json 且 manifest.yaml 的 id 对得上某个工作区 → workspaces/<id>/runs/<run>/
  runs/design-<id>/      cap design 的执行层日志                                       → workspaces/<id>/runs/design/
  其余（chats/ jobs/ 对不上工作区的 run）                                                留在原地，列出来由人处置

用法：python3 scripts/oneoff/migrate-runs-to-workspaces.py [platform 目录，缺省 ./platform]
零依赖：manifest 只取 `id:` 一行，不引 yaml。
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

ID_RE = re.compile(r"^id:\s*['\"]?([A-Za-z0-9_-]+)", re.M)


def manifest_id(run_dir: Path) -> str | None:
    manifest = run_dir / "manifest.yaml"
    if not manifest.is_file():
        return None
    found = ID_RE.search(manifest.read_text(encoding="utf-8"))
    return found.group(1) if found else None


def main(platform: Path) -> int:
    runs, workspaces = platform / "runs", platform / "workspaces"
    if not runs.is_dir():
        print(f"没有 {runs}，不用搬")
        return 0
    known = {p.name for p in workspaces.iterdir() if (p / "workspace.yaml").is_file()} \
        if workspaces.is_dir() else set()
    left: list[str] = []
    for entry in sorted(runs.iterdir()):
        if entry.name.startswith("design-") and entry.is_dir():
            owner = entry.name[len("design-"):]
            dest = workspaces / owner / "runs" / "design"
        elif entry.is_dir() and (entry / "checkpoint.json").is_file():
            owner = manifest_id(entry)
            dest = workspaces / (owner or "?") / "runs" / entry.name
        else:
            left.append(f"{entry}\t没有归属（对话或作业记录），留在原地")
            continue
        if owner not in known:
            left.append(f"{entry}\t对不上任何工作区（id={owner!r}），留在原地")
            continue
        if dest.exists():
            left.append(f"{entry}\t目标已存在，留在原地：{dest}")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(entry), str(dest))
        print(f"搬了\t{entry}\t→ {dest}")
    for line in left:
        print(f"留下\t{line}")
    print(f"剩下的 {runs} 看过没用就删掉；搬错了按上面的行搬回去。")
    return 0


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "platform").resolve()))
