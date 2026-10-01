#!/usr/bin/env python3
"""一次性迁移：把旧版框架塞进人话里的指南挪出来（外层 #200）。

跑法（在 platform 的 venv 里）：

    .venv/bin/python ../scripts/oneoff/migrate-chats-guide-out-of-messages.py <数据根> [--dry-run]

旧版在指南中途变了时，把一段平台提示（Codex 续接时还有整份 `<guide>…</guide>`，两万多字）拼在人那句话
前面，`turn-N/message.md` 与 `transcript.md` 里存的都是拼好的那句，页面重开时研究者的气泡里就是整份指南。
新版只塞变了的几节，人的原话照原样存，塞进去的另存 `turn-N/guide-update.md`（framework/chat/conversation.py）。

这里把旧对话迁成新版的样子，`<数据根>/projects/*/.ai4sci/chats/*/` 与 `<数据根>/studio/chats/*/` 下每一轮：

    turn-N/message.md      去掉开头的平台提示，只剩人的原话
    turn-N/guide-update.md 新写：去掉的那段原样存着（证据不丢）；已经有的不动
    transcript.md          那一轮「**人**：」后面同一段去掉

旧版的两种写法（代码里从来只有这两种，见 conversation.py 的 git 历史）：整份重塞「（平台提示：这段对话开始后
指南更新了；新指南全文在下面的 <guide> 里，之后照它办。）\\n\\n<guide>\\n…\\n</guide>\\n\\n」，以及一句提醒「（平台提示：
你的指南自上一轮起更新了——…重看一遍。）\\n\\n」，可能两段都有、前后挨着。别的「（平台提示」开头的话不认、不动、
打一行出来人看。transcript.md 里那一轮找不到同一段就整段对话跳过、打原因，不半改。幂等：迁过的再跑什么都不做。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

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


def migrate_chat(chat: Path, *, dry_run: bool) -> list[str]:
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
    if not edits:
        return lines
    if not dry_run:
        for turn, prefix, rest in edits:
            (turn / "message.md").write_text(rest, encoding="utf-8")
            update = turn / UPDATE_NAME
            if not update.exists():
                update.write_text(prefix, encoding="utf-8")
        transcript.write_text(text, encoding="utf-8")
    verb = "会迁" if dry_run else "迁了"
    chars = sum(len(prefix) for _, prefix, _ in edits)
    return [*lines, f"{verb} {chat.name}：{len(edits)} 轮、挪出 {chars} 字（{chat}）"]


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    dry_run = "--dry-run" in argv
    if len(args) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    home = Path(args[0]).resolve()
    chats = sorted({*home.glob("projects/*/.ai4sci/chats/chat-*"), *home.glob("studio/chats/chat-*")})
    chats = [c for c in chats if c.is_dir()]
    if not chats:
        print(f"{home} 下没有对话：什么都不做")
        return 0
    skipped = 0
    for chat in chats:
        for line in migrate_chat(chat, dry_run=dry_run):
            print(line)
            skipped += line.startswith("跳过")
    print(f"共 {len(chats)} 段对话{'（只看不改）' if dry_run else ''}")
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
