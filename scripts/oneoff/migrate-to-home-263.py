#!/usr/bin/env python3
"""一次性搬家：把旧版平台散在各处的东西收进平台的家 `~/.ai4sci`（外层 #263 / #264）。

跑法（不 import 平台代码，任何 python3 都行）：

    python3 scripts/oneoff/migrate-to-home-263.py <旧数据根> [<新家>] [--apply]

- `<旧数据根>`：以前项目所在的目录（下面有 `projects/`）。装包跑的是 `~/ai4sci`；设过 `AI4SCI_HOME`
  的就是它指的目录。
- `<新家>`：缺省 `~/.ai4sci`。和旧数据根是同一个目录就是就地升级（开发时 `AI4SCI_HOME` 指着的那个）。
- 不带 `--apply` 只列要做的事，不动任何文件。

搬什么（都是复制，旧的一样不删，确认新家能用后自己删）：
1. 旧数据根的 `projects/` `studio/` → 新家（就地升级跳过）。
2. `~/.config/ai4sci/agents.yaml` `computes.yaml` → 新家（新家里已有的不覆盖）。
3. 旧 Codex 私有目录 `~/.config/ai4sci/codex-home/` → 新家 `codex/`：会话 rollout 在里面，续得上；
   不搬凭据软链（`auth.json` 指着你自己的 `~/.codex`）——新版平台自己登录。
4. `~/.claude/projects/` 里平台对话的会话记录（目录名以旧数据根编过的路径开头）→ 新家
   `claude_code/projects/`，目录名换成新路径编的：Claude 续聊按 cwd 编的目录找会话。
5. 数据根挪了位置时，把记录里旧数据根的绝对路径换成新的（对话与作业的 meta、两家的会话记录）。
6. 新家放标记 `.ai4sci-home`：清除只认有标记的家。

之后：Codex 要在平台里登录一次（`ai4sci agent login codex`）；Claude Code 换 DeepSeek 等供应商在
设置页填 key（#266），用订阅的同样 `ai4sci agent login claude_code`。
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

MARKER = ".ai4sci-home"
OLD_CONFIG = Path.home() / ".config" / "ai4sci"
CLAUDE_PROJECTS = Path.home() / ".claude" / "projects"
# 改绝对路径时只碰这几种文本文件
TEXT_SUFFIXES = {".json", ".jsonl", ".yaml", ".yml"}


def claude_dirname(path: Path) -> str:
    """Claude Code 按 cwd 给会话起的目录名：不是字母数字的都换成 -（与 backends/claude_code.py 同）。"""
    return re.sub(r"[^A-Za-z0-9]", "-", str(path))


def plan(old_root: Path, home: Path) -> list[tuple[str, Path, Path]]:
    """要做的事：(说明, 从, 到)。"""
    moved = old_root != home
    steps: list[tuple[str, Path, Path]] = []
    if moved:
        for name in ("projects", "studio"):
            if (old_root / name).is_dir():
                steps.append((f"复制 {name}/", old_root / name, home / name))
    for name in ("agents.yaml", "computes.yaml"):
        if (OLD_CONFIG / name).is_file() and not (home / name).exists():
            steps.append((f"复制 {name}", OLD_CONFIG / name, home / name))
    codex_old = OLD_CONFIG / "codex-home"
    if codex_old.is_dir() and not (home / "codex").exists():
        steps.append(("复制 Codex 私有目录（不含凭据软链）", codex_old, home / "codex"))
    prefix = claude_dirname(old_root)
    if CLAUDE_PROJECTS.is_dir():
        for entry in sorted(CLAUDE_PROJECTS.iterdir()):
            if entry.is_dir() and entry.name.startswith(prefix):
                target = home / "claude_code" / "projects" / (claude_dirname(home) + entry.name[len(prefix):])
                if not target.exists():
                    steps.append(("复制 Claude 会话记录", entry, target))
    return steps


def copy(source: Path, target: Path) -> None:
    if source.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        return
    # 凭据软链不搬：auth.json 指着用户自己的 ~/.codex，新版平台自己登录
    shutil.copytree(source, target, symlinks=True,
                    ignore=lambda d, names: [n for n in names
                                             if n == "auth.json" and (Path(d) / n).is_symlink()])


def rewrite_paths(root: Path, old: str, new: str) -> int:
    """root 下文本记录里的旧绝对路径换成新的；返回改了几个文件。"""
    changed = 0
    for path in root.rglob("*"):
        if path.is_symlink() or not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="strict")
        if old in text:
            path.write_text(text.replace(old, new), encoding="utf-8")
            changed += 1
    return changed


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args or len(args) > 2:
        print(__doc__)
        return 2
    apply = "--apply" in argv
    old_root = Path(args[0]).expanduser().resolve()
    home = Path(args[1]).expanduser().resolve() if len(args) == 2 else Path.home() / ".ai4sci"
    if not (old_root / "projects").is_dir():
        print(f"{old_root} 下面没有 projects/，不像旧数据根", file=sys.stderr)
        return 2
    steps = plan(old_root, home)
    print(f"旧数据根 {old_root}\n新家     {home}" + ("（就地升级）" if old_root == home else ""))
    for what, source, target in steps:
        print(f"  {what}\n    {source}\n    → {target}")
    if not steps:
        print("  没有要搬的")
    if not apply:
        print("\n只列了清单，没动任何文件；确认后加 --apply")
        return 0
    home.mkdir(parents=True, exist_ok=True)
    for _, source, target in steps:
        copy(source, target)
    if old_root != home:
        targets = [home / "projects", home / "studio", home / "codex", home / "claude_code"]
        count = sum(rewrite_paths(t, str(old_root), str(home)) for t in targets if t.is_dir())
        print(f"  旧路径换成新路径：{count} 个文件")
    (home / MARKER).write_text("ai4sci 的家（外层 #263）：清除只删有这个文件的目录。\n", encoding="utf-8")
    print("\n搬完了。旧的一样没删：新家能用后自己删 ~/.config/ai4sci、旧数据根、"
          "~/.claude/projects 下复制过的那几个目录。")
    print("Codex：ai4sci agent login codex；Claude Code 用 DeepSeek 等在设置页填 key。")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
