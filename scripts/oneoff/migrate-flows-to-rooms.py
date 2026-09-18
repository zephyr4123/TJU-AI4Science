#!/usr/bin/env python3
"""一次性迁移：把「步骤」形状的工作流文件改成「房间 + 断点」（内仓 P-18，外层 #99）。

跑法（在 platform 的 venv 里，数据根同起服务时的那几个环境变量）：

    .venv/bin/python ../scripts/oneoff/migrate-flows-to-rooms.py <workflows 库> <workspaces 根>

改三处：库 `workflows/*.yaml`、工作区 `flows/*.yaml`、run 里的快照 `runs/<id>/workflow/*.yaml`
（连同 `flow.json` 的 step 按新项数重算）。已经是新形状的文件（有 `rooms`）原样跳过；读不出来的文件
打一行原因、跳过，不吞。原文件不删：旧版留成 `<name>.yaml.steps.bak`。

对照表（能力 → 房间）：init → 假设；design / baseline → 设计[design]；start / experiment →
实验[auto-research，带 experiment 那步的 with]；analysis → 分析[analysis]；verify → 验证[verify]。
键：publish → 「断点: 发布」，accept → 「断点: 验收」；纯人的步 → 「断点: <does>」；助理的非能力步
（填模板那种）并进它前面那一间。挨着的同一间合并、挨着的断点只留第一个。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOM_OF = {"init": "假设", "design": "设计", "baseline": "设计", "start": "实验",
           "experiment": "实验", "analysis": "分析", "verify": "验证"}
CAP_OF = {"design": "design", "baseline": "design", "start": "auto-research",
          "experiment": "auto-research", "analysis": "analysis", "verify": "verify"}
KEY_NOTE = {"publish": "发布", "accept": "验收"}


def convert(doc: dict[str, Any]) -> tuple[dict[str, Any], list[int]]:
    """旧文档 → 新文档，外加「旧 step k → 新 step」的对照（下标 0..n）。"""
    rooms: list[Any] = []
    at: list[int] = [0]  # at[k] = 走完前 k 个旧步骤时新清单有几项
    for step in doc.get("steps") or []:
        cap, key = step.get("cap"), step.get("key")
        if cap:
            stage = ROOM_OF.get(cap)
            if stage is None:
                raise ValueError(f"不认识的能力 {cap!r}")
            new_cap = CAP_OF.get(cap)
            params = dict(step.get("with") or {})
            last = rooms[-1] if rooms else None
            if isinstance(last, dict) and next(iter(last)) == stage:
                # 同一间挨着：合并，点名与参数并进去
                picks = last[stage]
                if new_cap and new_cap not in picks:
                    picks[new_cap] = params or None
                elif new_cap and params:
                    picks[new_cap] = {**(picks[new_cap] or {}), **params}
            elif new_cap:
                rooms.append({stage: {new_cap: params or None}})
            else:
                rooms.append(stage)
        elif key:
            if not (rooms and _is_stop(rooms[-1])):
                rooms.append({"断点": KEY_NOTE[key]})
        elif step.get("by") == "人":
            if not (rooms and _is_stop(rooms[-1])):
                rooms.append({"断点": " ".join(str(step.get("does", "")).split()) or "看一眼"})
        # 助理的非能力步：并进前面那一间，不占项
        at.append(len(rooms))
    if rooms and _is_stop(rooms[0]):
        rooms.pop(0)
        at = [max(0, n - 1) for n in at]
    # 「设计 → ◆核对 → 设计」：旧的 design 与 baseline 被人的核对隔开，合并后是同一间；
    # 后一间不添东西就删掉，断点留在合并后的那一间之后
    i = 1
    while i + 1 < len(rooms):
        if _is_stop(rooms[i]) and rooms[i - 1] == rooms[i + 1]:
            del rooms[i + 1]
            at = [n - 1 if n > i + 1 else n for n in at]
        else:
            i += 1
    out = {"name": doc["name"], "title": doc["title"], "summary": doc["summary"],
           "rooms": [_tidy(item) for item in rooms]}
    return out, at


def _is_stop(item: Any) -> bool:
    return isinstance(item, dict) and "断点" in item


def _tidy(item: Any) -> Any:
    """点名但都没参数的房间写成列表；别的原样。"""
    if isinstance(item, dict) and "断点" not in item:
        [(stage, picks)] = item.items()
        if all(v is None for v in picks.values()):
            return {stage: list(picks)}
    return item


def migrate_file(path: Path) -> list[int] | None:
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        print(f"跳过 {path}：顶层不是映射")
        return None
    if "rooms" in doc:
        return None  # 已经是新形状
    if "steps" not in doc:
        print(f"跳过 {path}：既没有 steps 也没有 rooms")
        return None
    try:
        new, at = convert(doc)
    except (KeyError, ValueError) as exc:
        print(f"跳过 {path}：{exc}")
        return None
    backup = path.with_suffix(".yaml.steps.bak")
    backup.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    path.write_text(yaml.safe_dump(new, allow_unicode=True, sort_keys=False, width=100),
                    encoding="utf-8")
    print(f"改了 {path}：{len(doc['steps'])} 步 → {len(new['rooms'])} 项")
    return at


def migrate_run(run_dir: Path) -> None:
    note = run_dir / "flow.json"
    snapshots = list((run_dir / "workflow").glob("*.yaml"))
    for snapshot in snapshots:
        at = migrate_file(snapshot)
        if at is None or not note.is_file():
            continue
        state = json.loads(note.read_text(encoding="utf-8"))
        if state.get("workflow") != snapshot.stem:
            continue
        old = int(state.get("step", 0))
        state["step"] = at[min(old, len(at) - 1)]
        note.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"改了 {note}：step {old} → {state['step']}")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    library, workspaces = Path(argv[1]), Path(argv[2])
    for path in sorted(library.glob("*.yaml")):
        migrate_file(path)
    for ws in sorted(p for p in workspaces.iterdir() if p.is_dir()) if workspaces.is_dir() else []:
        for path in sorted((ws / "flows").glob("*.yaml")):
            migrate_file(path)
        for run_dir in sorted(p for p in (ws / "runs").glob("*") if p.is_dir()):
            migrate_run(run_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
