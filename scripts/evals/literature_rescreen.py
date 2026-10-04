"""把跑过的检索每一跳的筛选再做一遍，换模型、思考深度或清单写法，看便宜了还准不准（外层 #219）。

#217 说明每跳筛不能砍：它决定哪些论文当父论文往外扩。降本的几个变量（清单砍短、换便宜模型、降思考
深度）只改筛选这一步，检索和往外扩不变，所以不用从头跑：每跳交给筛选的清单（rounds/<跳>/candidates.md）
原样存着，里面每篇都已经有评分模型的判定，把清单交给改过的筛选再判一遍，拿收不收去对判定就行。
不检索、不碰 arXiv，可以多路并行；设置不改再判一遍（对照线）量同一批判两次本来差多少。

提示照检索步骤原样拼（同一个 screen.md、同一份需求与纳入标准、同一套装载）；只有结论文件写在
重放目录下的 decisions.md，不动原来的运行。漏写、抄错号的几篇照产品的做法补筛一次。
`--reasons` 试少写输出：included 只给收的写理由，none 都不写（只改提示里「写法」一节与解析）。

用法（在外层仓根）：
    AI4SCI_HOME=<评测的 home> platform/.venv/bin/python scripts/evals/literature_rescreen.py \
        <重放目录> <产出目录…> [--model sonnet --effort medium --abstract-max 1500 --short-found]
        [--reasons all|included|none]

每批的结果写在 <重放目录>/<工作区>-<次>/hop-<跳>/result.json（收不收、理由、花费、token）；
已有 result.json 的批跳过，中断了重跑接着来。
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from backends import Tuning, get_backend
from framework.capabilities.literature_search import loop
from framework.capabilities.literature_search.exchange import parse_decisions, parse_seeds
from framework.contracts import requirement
from framework.executor import prompting, session
from framework.skills import EXECUTOR_BASH_RULES
from framework.workspace import loadout

LOGGER = logging.getLogger("literature_rescreen")
PARALLEL = 6
DECISIONS = "decisions.md"
RESULT = "result.json"
HOPS = ("0", "1", "2")
ABSTRACT_PREFIX, FOUND_PREFIX = "- 摘要：", "- 怎么找到的："
# 「写法」一节的原文与两种少写的改法（screen.md 原样拼出来以后整段替换）
_EXAMPLE_IN = "W2963431257 | 收 | 用 PINN 从稀疏观测反推扩散系数，正是需求里的参数估计"
_EVERY = "上面每个 W 号都要有一行，不多不少，不要别的内容："
FORMAT_ALL = ("每篇一行，三段用 `|` 隔开：W 号 | 收 或 不收 | 一句理由（照纳入标准说，二十到"
              f"六十字）。{_EVERY}\n\n```\n{_EXAMPLE_IN}\n"
              "W1234567890 | 不收 | 只做正问题求解，不涉及参数反演\n```")
UNSURE_ALL = ("拿不准的收（这一步宁可多收，后面还有人看），"
              "理由里写明「无摘要，按题目判」或哪里拿不准。")
FORMATS = {
    "included": ("每篇一行。收的三段用 `|` 隔开：W 号 | 收 | 一句理由（照纳入标准说，二十到"
                 f"六十字）；不收的只写两段：W 号 | 不收，不写理由。{_EVERY}\n\n```\n"
                 f"{_EXAMPLE_IN}\nW1234567890 | 不收\n```", UNSURE_ALL),
    "none": (f"每篇一行，两段用 `|` 隔开：W 号 | 收 或 不收，不写理由。{_EVERY}\n\n```\n"
             "W2963431257 | 收\nW1234567890 | 不收\n```",
             "拿不准的收（这一步宁可多收，后面还有人看）。"),
}
SHORT_LINE_RE = re.compile(r"^\W*(W\d+)\s*\|\s*(收|不收)\s*(?:\|\s*(.*?))?\s*$")
# 「怎么找到的」一行的四种说法（pool.describe）：压缩时只数每种几条，不列父论文题目
FOUND_KINDS = (("种子（", "种子"), ("检索词「", "检索词 {n} 条"),
               ("被收录的《", "被 {n} 篇已收录的引用"), ("引用了收录的《", "引用了 {n} 篇已收录的"))


def blocks(listing: str) -> list[tuple[str, str]]:
    """清单 → [(W 号, 这一篇的整段)]，按原顺序。"""
    parts = re.split(r"(?m)^### ", listing.strip())
    return [(p.split("\n", 1)[0].strip(), "### " + p.rstrip()) for p in parts if p.strip()]


def rewrite(block: str, abstract_max: int, short_found: bool) -> str:
    lines = []
    for line in block.splitlines():
        if line.startswith(ABSTRACT_PREFIX):
            text = line.removeprefix(ABSTRACT_PREFIX).removesuffix("…")
            cut = len(text) > abstract_max or line.endswith("…")
            line = ABSTRACT_PREFIX + text[:abstract_max] + ("…" if cut else "")
        elif short_found and line.startswith(FOUND_PREFIX):
            line = FOUND_PREFIX + "；".join(say.format(n=line.count(mark))
                                            for mark, say in FOUND_KINDS if mark in line)
        lines.append(line)
    return "\n".join(lines)


def parse_short(text: str, expected: list[str]) -> tuple[dict, list]:
    """少写理由时的结论：`W号 | 收 或 不收 [| 理由]`；同一篇两条相反的不算有结论。"""
    decided: dict[str, tuple[str, str]] = {}
    conflicted: set[str] = set()
    for line in text.splitlines():
        m = SHORT_LINE_RE.match(line.strip())
        if not m or m.group(1) not in expected or m.group(1) in conflicted:
            continue
        key, verdict = m.group(1), m.group(2)
        if key in decided and decided[key][0] != verdict:
            del decided[key]
            conflicted.add(key)
        else:
            decided[key] = (verdict, m.group(3) or "")
    return decided, [f"{k} 没有结论" for k in expected if k not in decided]


def ask(runner, tuning: Tuning, batch_dir: Path, run_dir: Path, need: str, criteria: str,
        hop: str, entries: list[tuple[str, str]], reasons: str, suffix: str = ""
        ) -> tuple[dict, list, dict]:
    """交给筛选判一次：照检索步骤的 _ask 拼提示，只是结论写在重放目录。返回结论、问题、花费。"""
    listing = "\n\n".join(b for _, b in entries)
    decisions = DECISIONS.replace(".md", f"{suffix}.md")
    (batch_dir / f"candidates{suffix}.md").write_text(listing + "\n", encoding="utf-8")
    prompt = prompting.build_prompt(
        loop.SCREEN_PROMPT, {"batch": f"第 {hop} 跳", "count": len(entries), "requirement": need,
                             "criteria": criteria, "candidates": listing, "decisions": decisions},
        loadout=loadout.around(run_dir))
    if reasons != "all":
        fmt, unsure = FORMATS[reasons]
        assert FORMAT_ALL in prompt and UNSURE_ALL in prompt, "screen.md 的写法一节改了，重放跟着改"
        prompt = prompt.replace(FORMAT_ALL, fmt).replace(UNSURE_ALL, unsure)
    result = runner.run(prompt=session.full_prompt(runner, prompt), cwd=batch_dir,
                        timeout_s=session.executor_timeout_s(), allowed_paths=[batch_dir],
                        bash_rules=EXECUTOR_BASH_RULES, tuning=tuning)
    session.stash_executor_logs(batch_dir, batch_dir / f"executor{suffix}")
    out = batch_dir / decisions
    if result.timed_out or result.exit_code != 0 or not out.is_file():
        raise RuntimeError(f"{batch_dir} 筛选会话没走完：exit={result.exit_code} "
                           f"timed_out={result.timed_out} 有结论={out.is_file()}")
    parse = parse_decisions if reasons == "all" else parse_short
    decided, problems = parse(out.read_text(encoding="utf-8"), [k for k, _ in entries])
    tokens: dict[str, int] = {}
    for event in result.events:
        for k, v in (event.get("usage") or {}).items():
            if isinstance(v, int):
                tokens[k] = tokens.get(k, 0) + v
    return decided, problems, {"cost_usd": result.cost_usd, "duration_s": result.duration_s,
                               "tokens": tokens}


def replay(runner, tuning: Tuning, out: Path, run_dir: Path, hop: str, abstract_max: int,
           short_found: bool, reasons: str) -> None:
    batch_dir = out / f"{run_dir.parents[1].name}-{run_dir.name}" / f"hop-{hop}"
    if (batch_dir / RESULT).is_file():
        return
    batch_dir.mkdir(parents=True, exist_ok=True)
    need = requirement.read(run_dir.parents[1]).strip()
    seeds, problems = parse_seeds((run_dir / "seeds.md").read_text(encoding="utf-8"))
    assert seeds is not None, f"{run_dir}/seeds.md 不合形状：{problems}"
    listing = (run_dir / loop.ROUNDS_DIRNAME / hop / loop.LISTING_NAME).read_text(encoding="utf-8")
    entries = [(k, rewrite(b, abstract_max, short_found)) for k, b in blocks(listing)]
    decided, problems, spent = ask(runner, tuning, batch_dir, run_dir, need, seeds.criteria, hop,
                                   entries, reasons)
    sessions = [spent]
    rest = [(k, b) for k, b in entries if k not in decided]
    if rest:
        LOGGER.info("rescreen_rest batch=%s missing=%d %s", batch_dir, len(rest), problems[:3])
        got, _, spent = ask(runner, tuning, batch_dir, run_dir, need, seeds.criteria, hop, rest,
                            reasons, loop.REST_SUFFIX)
        decided |= got
        sessions.append(spent)
    result = {"run": str(run_dir), "hop": hop, "papers": len(entries),
              "listing_chars": sum(len(b) for _, b in entries),
              "missing": [k for k, _ in entries if k not in decided],
              "decisions": {k: list(v) for k, v in decided.items()}, "sessions": sessions}
    (batch_dir / RESULT).write_text(json.dumps(result, ensure_ascii=False, indent=1),
                                    encoding="utf-8")
    LOGGER.info("rescreen_done batch=%s papers=%d included=%d cost=%.3f", batch_dir, len(entries),
                sum(v[0] == "收" for v in decided.values()),
                sum(s["cost_usd"] for s in sessions))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("out", type=Path, help="重放目录（一条线一个）")
    ap.add_argument("runs", type=Path, nargs="+", help="跑过的产出目录 <工作区>/literature/<次>")
    ap.add_argument("--backend", default="claude_code")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--abstract-max", type=int, default=loop.ABSTRACT_MAX)
    ap.add_argument("--short-found", action="store_true",
                    help="「怎么找到的」只数每种几条，不列父论文题目")
    ap.add_argument("--reasons", default="all", choices=("all", "included", "none"),
                    help="理由怎么写：都写（产品现在的做法）、只给收的写、都不写")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")
    runner, tuning = get_backend(args.backend), Tuning(args.model, args.effort)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "settings.json").write_text(json.dumps(
        {"backend": args.backend, "model": args.model, "effort": args.effort,
         "abstract_max": args.abstract_max, "short_found": args.short_found,
         "reasons": args.reasons}, ensure_ascii=False))
    jobs = [(run.resolve(), hop) for run in args.runs for hop in HOPS
            if (run / loop.ROUNDS_DIRNAME / hop / loop.LISTING_NAME).is_file()]
    failed = []

    def one(job: tuple[Path, str]) -> None:
        try:
            replay(runner, tuning, args.out, *job, args.abstract_max, args.short_found,
                   args.reasons)
        except (RuntimeError, OSError) as exc:  # 一批坏了接着跑别的批，重跑只补没有结果的
            LOGGER.error("rescreen_failed run=%s hop=%s %s", *job, exc)
            failed.append(job)

    with ThreadPoolExecutor(PARALLEL) as pool:
        list(pool.map(one, jobs))
    print(f"rescreen {args.out.name}: {len(jobs) - len(failed)}/{len(jobs)} 批完成"
          + (f"，失败 {len(failed)} 批（重跑这条命令补）" if failed else ""))
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
