#!/usr/bin/env python3
"""一次性修数据：对话 meta 里报不出美元的花费从 0.0 改成「未知」（外层 #256）。

跑法（不 import 平台代码，任何 python3 都行）：

    python3 scripts/oneoff/fix-unknown-chat-cost-256.py <数据根> [--dry-run]

为什么：`conversation._close_turn` 以前把对话的 `cost_usd` 从 0.0 起加、NaN 跳过，Codex（订阅登录，
报不出美元）的对话因此一直记着 0.0，对话清单里一排 $0.00。#256 起一轮都没报过美元的对话记 null。
这里照每一轮框架记的 `turn-N/trace.jsonl` 末尾那条 done / error 重算：一轮都没报过美元的改成 null；
报过的不动（以前的加法对报了的那几轮是对的）。

范围：`<数据根>/projects/*/.ai4sci/chats/*/meta.json` 与 `<数据根>/studio/chats/*/meta.json`。幂等：
已经是 null 的不动。回滚：先自己备份（`tar czf chats.tgz $(find <数据根> -type d -name chats)`），
脚本只改 meta.json 的这一个字段，不删任何文件。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def reported_dollars(conv: Path) -> bool:
    """这段对话有没有哪一轮报过美元：每轮 trace.jsonl 里最后一条 done / error 的 cost_usd 不是 null。"""
    for trace in sorted(conv.glob("turn-*/trace.jsonl")):
        closing = [e for e in (json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()
                               if line.strip())
                   if e.get("kind") in ("done", "error")]
        if closing and closing[-1].get("cost_usd") is not None:
            return True
    return False


def main(argv: list[str]) -> int:
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    home, dry = Path(argv[0]).expanduser(), "--dry-run" in argv
    metas = sorted([*home.glob("projects/*/.ai4sci/chats/*/meta.json"), *home.glob("studio/chats/*/meta.json")])
    changed = 0
    for path in metas:
        meta = json.loads(path.read_text(encoding="utf-8"))
        if meta.get("cost_usd") is None or reported_dollars(path.parent):
            continue
        print(f"{'会改' if dry else '改了'}\t{path.parent.relative_to(home)}\t{meta.get('backend')}"
              f"\tcost_usd {meta['cost_usd']} → null")
        if not dry:
            meta["cost_usd"] = None
            path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        changed += 1
    print(f"共 {len(metas)} 段对话，{'会改' if dry else '改了'} {changed} 段")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
