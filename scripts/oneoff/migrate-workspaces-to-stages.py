#!/usr/bin/env python3
"""一次性迁移：把「任务包 + run」形状的工作区改成「需求 + 七个阶段目录」（内仓 P-19，外层 #104 #108）。

跑法（在 platform 的 venv 里）：

    .venv/bin/python ../scripts/oneoff/migrate-workspaces-to-stages.py <workspaces 根>

一个工作区改成：

    task/manifest.yaml + task/design.md   →  requirement.md（人话）+ design/1/scoring.yaml（机器读的那半）
    task/publish.json                     →  requirement.lock v1 + .ai4sci/requirement/v1.md
    task/data/                            →  materials/（原件）与 design/1/data/（设计那包的拷贝）
    task/env/                             →  materials/env/ 与 design/1/env/
    task/harness/ code/ run_0/            →  design/1/harness/ code/ baseline/
    runs/<id>/                            →  experiment/<n>/（work、账本、笔记、iters/、checkpoint、快照）
    runs/<id>/analysis/ verify/           →  analysis/<n>/ verification/<n>/
    chats/ jobs/                          →  .ai4sci/chats/ .ai4sci/jobs/
    workspace.yaml、task/、runs/          →  删

已经是新形状的工作区（有 requirement.md）原样跳过；坏掉的打一行原因、跳过，不吞。每次产出的 meta.yaml
由本脚本按框架的形状写；产出之间的 from 按旧的从属关系推（实验读 design/1，分析读它所在的实验，验证读分析）。
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

PROSE_KEYS = ("id", "title", "question", "source")
IGNORED = {".git", ".venv", "__pycache__", ".ai4sci"}


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def tree_hash(directory: Path) -> str:
    """与 framework/contracts/output.py 的 tree_hash 同一算法：本脚本不 import 框架，免得两边版本不一。"""
    digest = hashlib.sha256()
    for path in sorted(p for p in directory.rglob("*") if p.is_file()):
        rel = path.relative_to(directory)
        if any(part in IGNORED | {"meta.yaml", "signed.json"} for part in rel.parts):
            continue
        digest.update(rel.as_posix().encode("utf-8") + b"\0")
        digest.update(path.read_bytes() + b"\0")
    return digest.hexdigest()


def write_meta(directory: Path, doc: dict[str, Any]) -> None:
    (directory / "meta.yaml").write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False),
                                         encoding="utf-8")


def meta(oid: str, stage: str, title: str, by: str, inputs: list[tuple[str, Path]], *,
         params: dict[str, Any] | None = None, requirement: int | None = 1,
         result: str = "迁移自旧布局") -> dict[str, Any]:
    stamp = now()
    return {"id": oid, "stage": stage, "title": title, "by": by, "created_at": stamp,
            "status": "ok", "from": [{"id": i, "sha256": tree_hash(p)} for i, p in inputs],
            "params": params or {}, "flow": None, "step": None, "requirement": requirement,
            "chat_id": None, "finished_at": stamp, "result": result, "error": ""}


def demote(text: str) -> str:
    """嵌进一格里的旧 design.md：去掉它的一级标题，二级降成三级，别把需求的格切碎。"""
    lines = [line for line in text.strip().splitlines() if not line.startswith("# ")]
    return "\n".join("#" + line if line.startswith("## ") else line for line in lines).strip()


def requirement_text(manifest: dict[str, Any], brief: str, data_readme: str) -> str:
    """manifest 里人话的那半 + design.md → requirement.md：模板那几格，能填的填，填不了的写清来源。"""
    metrics = manifest.get("metrics") or []
    primary = next((m for m in metrics if m.get("primary")), metrics[0] if metrics else {})
    budget = manifest.get("budget") or {}
    goal = (f"主指标 `{primary.get('name')}`，{'越小越好' if primary.get('direction') == 'minimize' else '越大越好'}"
            + (f"；已知可达 {primary['attainable']}" if primary.get("attainable") is not None else "")
            + "。")
    others = [m["name"] for m in metrics if m is not primary]
    if others:
        goal += f" 另记 {', '.join(others)}。"
    budget_text = (f"一次跑 {budget.get('wall_clock_s')} 秒墙钟，最多改 {budget.get('max_iterations')} 轮；"
                   f"基线重复 {budget.get('repeat_k')} 次算 σ，差值超过 {budget.get('accept_sigma')} 倍 σ"
                   + (f"（至少 {budget['min_delta']}）" if budget.get("min_delta") is not None else "")
                   + " 才算改进。")
    requirements = manifest.get("requirements") or []
    accept = "\n".join(f"- {r.get('id')}：{r.get('description')}" for r in requirements) or "见「怎么算好」。"
    parts = [
        f"# {manifest.get('title') or manifest.get('id')}",
        "",
        "## 问题",
        "",
        " ".join(str(manifest.get("question", "")).split()),
        "",
        "## 目标",
        "",
        goal,
        "",
        "## 材料",
        "",
        (f"来源：{manifest['source']}\n\n" if manifest.get("source") else "") + (data_readme.strip() or "见 materials/。"),
        "",
        "## 怎么算好",
        "",
        demote(brief),
        "",
        "## 验收",
        "",
        accept,
        "",
        "## 预算",
        "",
        budget_text,
        "",
    ]
    return "\n".join(parts)


def scoring_doc(manifest: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in manifest.items() if k not in PROSE_KEYS}


def copy_tree(src: Path, dst: Path, *extra_ignored: str) -> None:
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*IGNORED, *extra_ignored),
                    dirs_exist_ok=True)


def migrate_workspace(root: Path) -> None:
    if (root / "requirement.md").is_file():
        print(f"跳过 {root.name}：已经是新布局")
        return
    task = root / "task"
    if not (task / "manifest.yaml").is_file():
        print(f"跳过 {root.name}：没有 task/manifest.yaml，不知道怎么搬")
        return
    manifest = yaml.safe_load((task / "manifest.yaml").read_text(encoding="utf-8"))
    brief = (task / "design.md").read_text(encoding="utf-8") if (task / "design.md").is_file() else ""
    readme = task / "data" / "README.md"
    data_readme = readme.read_text(encoding="utf-8") if readme.is_file() else ""

    # 需求 + 确认
    text = requirement_text(manifest, brief, data_readme)
    (root / "requirement.md").write_text(text, encoding="utf-8")
    platform = root / ".ai4sci"
    (platform / "requirement").mkdir(parents=True, exist_ok=True)
    publish = task / "publish.json"
    if publish.is_file():
        record = json.loads(publish.read_text(encoding="utf-8"))
        (platform / "requirement" / "v1.md").write_text(text, encoding="utf-8")
        (root / "requirement.lock").write_text(json.dumps({
            "version": 1, "by": record.get("by", "migrated"),
            "confirmed_at": record.get("published_at", now()),
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}, ensure_ascii=False,
            indent=2) + "\n", encoding="utf-8")
    confirmed = publish.is_file()

    # 原件
    materials = root / "materials"
    materials.mkdir(exist_ok=True)
    if (task / "data").is_dir():
        copy_tree(task / "data", materials)
    if (task / "env").is_dir():
        copy_tree(task / "env", materials / "env")

    # 设计那包
    design = root / "design" / "1"
    design.mkdir(parents=True)
    (design / "scoring.yaml").write_text(
        yaml.safe_dump(scoring_doc(manifest), allow_unicode=True, sort_keys=False), encoding="utf-8")
    for name in ("harness", "code", "data", "env"):
        if (task / name).is_dir():
            copy_tree(task / name, design / name)
    if (task / "run_0").is_dir():
        copy_tree(task / "run_0", design / "baseline")
    write_meta(design, meta("design/1", "design", "评分脚本与基线", "design", [],
                            params={"domain": manifest.get("domain", "generic")},
                            requirement=1 if confirmed else None))

    # 旧 run → 实验 / 分析 / 验证
    runs = root / "runs"
    n_exp = n_ana = n_ver = 0
    if runs.is_dir():
        for run in sorted(p for p in runs.iterdir() if (p / "checkpoint.json").is_file()):
            n_exp += 1
            exp = root / "experiment" / str(n_exp)
            exp.mkdir(parents=True)
            for name in ("work", "prompts", "journal.md", "checkpoint.json"):
                src = run / name
                if src.is_dir():
                    copy_tree(src, exp / name)
                elif src.is_file():
                    shutil.copy2(src, exp / name)
            if (run / "manifest.yaml").is_file():
                (exp / "scoring.yaml").write_text(yaml.safe_dump(scoring_doc(
                    yaml.safe_load((run / "manifest.yaml").read_text(encoding="utf-8"))),
                    allow_unicode=True, sort_keys=False), encoding="utf-8")
            (exp / "prompts").mkdir(exist_ok=True)
            (exp / "prompts" / "requirement.md").write_text(text, encoding="utf-8")
            old = run / "experiment"
            for name in ("ledger.tsv", "notebook.md", "stop.json"):
                if (old / name).is_file():
                    shutil.copy2(old / name, exp / name)
            if (old / "runs").is_dir():
                for child in sorted((old / "runs").iterdir()):
                    if child.name.startswith("run_") and child.name[4:].isdigit():
                        copy_tree(child, exp / "iters" / f"iter_{child.name[4:]}")
            if (old / "executor").is_dir():
                copy_tree(old / "executor", exp / "executor")
            if (exp / "work" / "run_0").is_dir():
                (exp / "work" / "run_0").rename(exp / "work" / "baseline")
            if (exp / "work" / "manifest.yaml").is_file():
                (exp / "work" / "manifest.yaml").unlink()
            for stale in ("design.md", "publish.json"):
                (exp / "work" / stale).unlink(missing_ok=True)
            state = json.loads((run / "checkpoint.json").read_text(encoding="utf-8"))
            state.pop("run_id", None)
            state["output"] = f"experiment/{n_exp}"
            (exp / "checkpoint.json").write_text(json.dumps(state, ensure_ascii=False, indent=2),
                                                 encoding="utf-8")
            write_meta(exp, meta(f"experiment/{n_exp}", "experiment", "auto-research",
                                 "auto-research", [("design/1", design)],
                                 requirement=1 if confirmed else None))
            if (run / "analysis" / "analysis.md").is_file():
                n_ana += 1
                ana = root / "analysis" / str(n_ana)
                copy_tree(run / "analysis", ana)
                write_meta(ana, meta(f"analysis/{n_ana}", "analysis", "分析初稿", "analysis",
                                     [(f"experiment/{n_exp}", exp)],
                                     requirement=1 if confirmed else None))
                if (run / "verify" / "report.json").is_file():
                    n_ver += 1
                    ver = root / "verification" / str(n_ver)
                    copy_tree(run / "verify", ver)
                    write_meta(ver, meta(f"verification/{n_ver}", "verification", "数字核对",
                                         "verify", [(f"analysis/{n_ana}", ana),
                                                    (f"experiment/{n_exp}", exp)],
                                         requirement=1 if confirmed else None))
    for name in ("chats", "jobs"):
        if (root / name).is_dir():
            shutil.move(str(root / name), str(platform / name))

    for stale in ("task", "runs"):
        if (root / stale).exists():
            shutil.rmtree(root / stale)
    (root / "workspace.yaml").unlink(missing_ok=True)
    print(f"迁移 {root.name}：design/1"
          + (f"，experiment×{n_exp}，analysis×{n_ana}，verification×{n_ver}" if n_exp else "")
          + ("，需求 v1 已确认" if confirmed else "，需求未确认"))


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    root = Path(argv[1]).resolve()
    if not root.is_dir():
        print(f"不是目录：{root}", file=sys.stderr)
        return 2
    for ws in sorted(p for p in root.iterdir() if p.is_dir()):
        migrate_workspace(ws)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
