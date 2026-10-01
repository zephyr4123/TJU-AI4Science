#!/usr/bin/env python3
"""一次性迁移：1.0.x 的数据根迁成 1.1 的样子（外层 #195 #199 #200）。重构了不留历史遗留，旧数据在这里一次搬完。

跑法（在 platform 的 venv 里，cwd 是 platform/，要 import 平台的代码）：

    .venv/bin/python ../scripts/oneoff/migrate-to-1.1.py <数据根> [--dry-run]

做四件事，每件都幂等（迁过的再跑什么都不做），先全部算好再写盘，对不上的整段跳过、打原因、退 1：

1. **对话里塞进人话的旧指南挪出来**（`<数据根>/projects/*/.ai4sci/chats/*/`、`<数据根>/studio/chats/*/`）。
   旧版指南中途变了时，把平台提示（Codex 续接时还有整份 `<guide>…</guide>`，两万多字）拼在人那句话前面，
   `turn-N/message.md` 与 `transcript.md` 里存的都是拼好的那句，页面上研究者的气泡里就是整份指南。新版只塞
   变了的几节、人的原话照原样存、塞进去的另存 `turn-N/guide-update.md`。这里照新版的样子挪：message.md 与
   transcript 那一轮只留原话，去掉的那段原样写进 guide-update.md（已经有的不动）。只认代码里出现过的两种写法
   （conversation.py 的 git 历史里没变过）：整份重塞「（平台提示：这段对话开始后指南更新了；新指南全文在下面的
   <guide> 里，之后照它办。）\\n\\n<guide>\\n…\\n</guide>\\n\\n」，一句提醒「（平台提示：你的指南自上一轮起更新了
   ——…重看一遍。）\\n\\n」，可能两段挨着。transcript 那一轮找不到同一段就整段对话跳过、不半改。
2. **meta.json 去掉 `guide_sha`**：1.1 只认对话目录里的 guide.md（上一轮送到 CLI 的那份）。没有 guide.md 的
   老对话续接时整份指南算变了、塞一次，这是对的——不知道 CLI 手里是哪份。
3. **续不上的会话改成下次开新会话**：清掉 meta 的 `session_id`（页面上的历史都在，CLI 那边的记忆不带过来）。
   两种：编辑台的对话工作目录不是 `<数据根>/studio`（#149 之前开的，续接会站在代码仓里），顺手把 cwd 改对；
   CLI 那边找不到这条会话了（#136 搬家把项目的 cwd 改了、会话文件还在旧目录下）。会话文件的位置照两家
   适配器 `forget()` 里写的布局查：Claude Code `~/.claude/projects/<cwd 的 / 换成 ->/<id>.jsonl`，Codex
   私有 home 下 `sessions/*/*/*/rollout-*-<id>.jsonl`。
4. **工作区的流程实例补 `from`**（#199 之前 `flow take` 取的没记）：名字与库里一条流程相同的，记那条和它现在的
   结构 hash（出厂的流程自 2026-09-23 起没改过结构，现在的 hash 就是取的时候的）；名字对不上库里任何一条的
   打一行、不动——不知道取自哪条，不猜。写回走 `save_workflow`，格式与 `flow take` 一样，形状检查照过。

回滚：先自己备份（`tar czf chats.tgz $(find <数据根> -type d -name chats)` 与 flows/），脚本不删任何文件。
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

import yaml

from backends import codex
from framework import paths
from framework.capabilities import abilities
from framework.contracts import workflows
from framework.contracts.workflow_library import Library

REINJECT = re.compile(r"\A（平台提示：这段对话开始后指南更新了；新指南全文在下面的 <guide> 里，之后照它办。）"
                      r"\n\n<guide>\n.*?\n</guide>\n\n", re.S)
NOTICE = re.compile(r"\A（平台提示：你的指南自上一轮起更新了——能运行的命令可能多了或变了，"
                    r"拿不准就 ai4sci --help 重看一遍。）\n\n")
HEADING = "## 第 {n} 轮\n\n"
UPDATE_NAME = "guide-update.md"


def split_prefix(message: str) -> tuple[str, str]:
    """(塞进去的那段, 人的原话)；没塞过就是 ("", 原文)。两段可能都有，重塞的在前。"""
    prefix = ""
    for pattern in (REINJECT, NOTICE):
        found = pattern.match(message)
        if found:
            prefix += found.group()
            message = message[found.end():]
    return prefix, message


def session_exists(backend: str, session_id: str, cwd: str) -> bool:
    if backend == "claude_code":
        home = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")
        return (home / "projects" / str(Path(cwd).resolve()).replace("/", "-")
                / f"{session_id}.jsonl").is_file()
    if backend == "codex":
        root = Path(os.environ.get(codex.HOME_ENV) or codex.DEFAULT_ROOT).expanduser()
        return any((root / "sessions").glob(f"*/*/*/rollout-*-{session_id}.jsonl"))
    return True  # 不认识的后端不猜，当它在


def migrate_chat(chat: Path, studio_cwd: Path | None, *, dry_run: bool) -> list[str]:
    """一段对话：先全部算好、transcript 里每一处都对得上才写盘；返回要打的几行。"""
    transcript = chat / "transcript.md"
    text = transcript.read_text(encoding="utf-8") if transcript.is_file() else ""
    edits: list[tuple[Path, str, str]] = []
    lines: list[str] = []
    for turn in sorted(chat.glob("turn-*"), key=lambda p: int(p.name.split("-", 1)[1])):
        message_path = turn / "message.md"
        if not message_path.is_file():
            continue
        message = message_path.read_text(encoding="utf-8")
        prefix, rest = split_prefix(message)
        if not prefix:
            if message.startswith("（平台提示"):
                lines.append(f"不认得、没动 {message_path}：{message[:60]!r}")
            continue
        n = turn.name.split("-", 1)[1]
        start = text.find(HEADING.format(n=n))
        at = text.find(f"：{prefix}", start) if start != -1 else -1
        if at == -1:
            return [f"跳过 {chat}：transcript.md 第 {n} 轮找不到塞进去的那段，整段对话没动"]
        text = text[:at + 1] + text[at + 1 + len(prefix):]
        edits.append((turn, prefix, rest))

    meta_path = chat / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta_notes: list[str] = []
    if "guide_sha" in meta:
        del meta["guide_sha"]
        meta_notes.append("去掉 guide_sha")
    if studio_cwd is not None and Path(meta["cwd"]).resolve() != studio_cwd.resolve():
        meta_notes.append(f"cwd {meta['cwd']} → {studio_cwd}")
        meta["cwd"] = str(studio_cwd.resolve())
        if meta.get("session_id"):
            meta_notes.append("会话站错了地方，下次开新会话")
            meta["session_id"], meta["session_cost_usd"] = None, 0.0
    elif meta.get("session_id") and not session_exists(meta["backend"], meta["session_id"],
                                                      meta["cwd"]):
        meta_notes.append(f"{meta['backend']} 那边找不到会话 {meta['session_id']}，下次开新会话")
        meta["session_id"], meta["session_cost_usd"] = None, 0.0

    if not edits and not meta_notes:
        return lines
    if not dry_run:
        for turn, prefix, rest in edits:
            (turn / "message.md").write_text(rest, encoding="utf-8")
            update = turn / UPDATE_NAME
            if not update.exists():
                update.write_text(prefix, encoding="utf-8")
        if edits:
            transcript.write_text(text, encoding="utf-8")
        if meta_notes:
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                                 encoding="utf-8")
    verb = "会迁" if dry_run else "迁了"
    what = [f"{len(edits)} 轮挪出 {sum(len(p) for _, p, _ in edits)} 字"] if edits else []
    return [*lines, f"{verb} 对话 {chat.name}：{'；'.join(what + meta_notes)}（{chat}）"]


def migrate_flow(path: Path, library: Library, *, dry_run: bool) -> str | None:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or raw.get("from"):
        return None
    parent = library.load(str(raw.get("name")))
    if parent is None:
        return f"没动 {path}：名字 {raw.get('name')!r} 对不上库里的流程，不知道取自哪条"
    origin = workflows.Origin(parent.name, parent.content_hash())
    if not dry_run:
        doc = {"name": raw["name"], "from": origin.to_dict(),
               **{k: v for k, v in raw.items() if k != "name"}}
        workflows.save_workflow(path.parent, doc, abilities.steps(),
                                skills=abilities.skill_names(), overwrite=True)
    return f"{'会补' if dry_run else '补了'} {path} 的 from：{origin.name} {origin.hash}"


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    dry_run = "--dry-run" in argv
    if len(args) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    home = Path(args[0]).resolve()
    studio = home / "studio"
    chats = [(c, None) for c in sorted(home.glob("projects/*/.ai4sci/chats/chat-*")) if c.is_dir()]
    chats += [(c, studio) for c in sorted((studio / "chats").glob("chat-*")) if c.is_dir()]
    library = Library(paths.workflows_root(), studio / "workflows")
    flows = sorted(home.glob("projects/*/workspaces/*/flows/*.yaml"))
    skipped = 0
    for chat, studio_cwd in chats:
        for line in migrate_chat(chat, studio_cwd, dry_run=dry_run):
            print(line)
            skipped += line.startswith("跳过")
    for flow in flows:
        line = migrate_flow(flow, library, dry_run=dry_run)
        if line:
            print(line)
            skipped += line.startswith("没动")
    print(f"共 {len(chats)} 段对话、{len(flows)} 个流程实例{'（只看不改）' if dry_run else ''}")
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
