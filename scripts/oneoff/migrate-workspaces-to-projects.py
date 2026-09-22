#!/usr/bin/env python3
"""一次性迁移：把「散装工作区」搬成「项目里的工作区」（纲领 P-15 改，外层 #136）。

跑法（在 platform 的 venv 里，数据根是 AI4SCI_HOME 或仓根）：

    .venv/bin/python ../scripts/oneoff/migrate-workspaces-to-projects.py <数据根> [--dry-run]

每个 `<数据根>/workspaces/<id>/` 搬成一个同名的单工作区项目：

    workspaces/<id>/                     →  projects/<id>/workspaces/<id>/
    workspaces/<id>/.ai4sci/chats/       →  projects/<id>/.ai4sci/chats/     （对话归项目）
    （新写）                              →  projects/<id>/project.md          （一级标题抄需求的标题）
    （新建）                              →  projects/<id>/materials/          （共用原件，空）

搬过的对话能看不能续：会话在 CLI 那边按工作目录存，工作目录变了续不上（框架的 ConversationStale 会说清）；
这里只把每段对话 meta 里的 cwd 改成新项目的根，让「能看」这半边成立。
已经是新布局的（`workspaces/` 不在或空）什么都不做；`workspaces/<id>/` 里没有 requirement.md 的打一行原因、
跳过、不吞；同名项目已在也拒。搬完 `workspaces/` 空了就删掉它。
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

MARKER = "requirement.md"
PROJECT_MARKER = "project.md"


def title_of(requirement: Path, fallback: str) -> str:
    for line in requirement.read_text(encoding="utf-8").splitlines():
        if line.startswith("# ") and line[2:].strip():
            return line[2:].strip()
    return fallback


def migrate_one(home: Path, old: Path, *, dry_run: bool) -> str:
    ws_id = old.name
    if not (old / MARKER).is_file():
        return f"跳过 {old}：没有 {MARKER}，不是工作区"
    project_dir = home / "projects" / ws_id
    if project_dir.exists():
        return f"跳过 {old}：已经有项目 {project_dir}"
    new_ws = project_dir / "workspaces" / ws_id
    old_chats = old / ".ai4sci" / "chats"
    new_chats = project_dir / ".ai4sci" / "chats"
    title = title_of(old / MARKER, ws_id)
    if dry_run:
        return f"会搬 {old} → {new_ws}（对话 {len(list(old_chats.glob('chat-*'))) if old_chats.is_dir() else 0} 段，项目标题「{title}」）"
    new_ws.parent.mkdir(parents=True)
    (project_dir / "materials").mkdir()
    (project_dir / ".ai4sci").mkdir()
    (project_dir / PROJECT_MARKER).write_text(f"# {title}\n", encoding="utf-8")
    shutil.move(str(old), str(new_ws))
    moved = 0
    if (new_ws / ".ai4sci" / "chats").is_dir():
        shutil.move(str(new_ws / ".ai4sci" / "chats"), str(new_chats))
        for meta in new_chats.glob("chat-*/meta.json"):
            doc = json.loads(meta.read_text(encoding="utf-8"))
            doc["cwd"] = str(project_dir.resolve())
            meta.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            moved += 1
    return f"ok {ws_id} → {new_ws}（对话 {moved} 段搬进项目；搬过的对话能看不能续）"


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    dry_run = "--dry-run" in argv
    if len(args) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    home = Path(args[0]).resolve()
    old_root = home / "workspaces"
    if not old_root.is_dir():
        print(f"{home} 下没有 workspaces/：已经是新布局，什么都不做")
        return 0
    failed = 0
    for old in sorted(p for p in old_root.iterdir() if p.is_dir()):
        line = migrate_one(home, old, dry_run=dry_run)
        print(line)
        if line.startswith("跳过"):
            failed += 1
    if not dry_run and not any(old_root.iterdir()):
        old_root.rmdir()
        print(f"删了空的 {old_root}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
