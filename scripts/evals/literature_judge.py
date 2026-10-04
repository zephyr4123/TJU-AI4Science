"""给文献检索步骤打分：评分模型判切不切题，按 pooling 算准不准、全不全（外层 #215，报告 §6）。

只拿一篇综述的参考文献当答案，分数不可信：综述之后发表的论文工具找到了不得分（这一半由
literature_recall.py 的发表日截断解决）；综述只引了相关论文的一部分，工具找到的另一部分不得分；
综述的参考文献里又有方法论、背景这类和需求无关的，摊进分母。这里改成 TREC 的 pooling 做法：

- 待判的池子 = 综述取得到的参考文献 + 这道题所有运行里执行层看过摘要的论文；
- 评分模型对池子里每一篇只看需求原文与题目、摘要判「切题 / 不切题」，一个标准判到底；
- 切题全集 R = 池子里判切题的。一次运行打三个分：
  - 准不准 = 收录 ∩ R ÷ 收录：收进清单的是不是研究者要的；
  - 名额用得准不准 = 看过 ∩ R ÷ 看过：每次只看约 125 篇（第 0 跳 60 加种子、之后每跳 30），这些名额
    有几成花在切题的论文上，衡量检索与排序，名额相同的版本直接比；
  - 全不全 = 收录 ∩ R ÷ R，旁边给上限 min(看过, |R|) ÷ |R|：R 比名额大时一次运行不可能收全，
    分数到了上限附近说明卡在名额，离上限远说明卡在检索、排序或筛选。
  旧口径（收录了几成综述参考文献）一并给出，对照用。R 随加进来的运行变大，比较版本时把各版本的
  运行一起交给这个脚本，在同一个 R 上算分。

评分模型先过关才采信：综述里的核心答案（题目或摘要提到 PINN 类方法）应几乎全判切题；池子里另混进
一篇无关综述的参考文献，应几乎全判不切题；两家评分模型（缺省 Claude Code 的 Opus、思考深度高；
`--backend codex` 再判一遍）判同一池子的一致率要高。打乱顺序，不告诉它哪篇是哪类，不给执行层写的
纳入标准。每批一个隔离会话，不联网、不放行任何命令。

用法（在外层仓根，召回实测 literature_recall.py 跑完以后）：
    . ~/.secrets/loader.sh
    withkey openalex platform/.venv/bin/python scripts/evals/literature_judge.py \
        <工作区 requirement.md> <综述 W 号> <评分目录> <产出目录…> \
        [--backend claude_code --model opus --effort high] [--against <另一家的 judge.json>]

产出目录是 literature_recall.py 跑出来的（里面有 candidates.jsonl 与 eval.json），同一道题几次运行
一起给，池子才全。判过的论文按 W 号复用（评分目录里所有 judgments.md），加运行时只判新进池子的；
结果写在评分目录的 judge.json。
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import random
import re
import string
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from backends import Tuning, get_backend
from framework.capabilities.literature_search.openalex import OpenAlex, api_key
from framework.capabilities.literature_search.papers import Paper, from_openalex, work_key
from framework.capabilities.literature_search.web import Web
from framework.executor import session
from literature_recall import CORE_RE, cached

LOGGER = logging.getLogger("literature_judge")
RELEVANT, IRRELEVANT = "切题", "不切题"
LINE_RE = re.compile(rf"^\s*(W\d+)\s*\|\s*({IRRELEVANT}|{RELEVANT})\s*\|\s*(.+?)\s*$")
ABSTRACT_MAX = 1500
BATCH = 40
PARALLEL = 4
SEED = 215
OUT_NAME = "judgments.md"
REST_DIRNAME = "rest"

PROMPT = string.Template("""# 任务：判断一批论文切不切研究需求的题（$count 篇）

你在给一个文献检索工具的结果打分。下面是研究者写的需求，和一批论文的题目、年份、出处与摘要。逐篇判断这篇论文是不是研究者要找的：
在需求说的范围里、放进他的文献清单有用，就是切题；只是同一个大领域、但不是需求要的问题或方法，
或者完全无关，就是不切题。结论写进 `$out`。

## 研究需求

$requirement

## 论文（$count 篇）

$listing

## $out 的写法

每篇一行，三段用 `|` 隔开：W 号 | 切题 或 不切题 | 一句理由（二十到六十字，照需求说）。
上面每个 W 号都要有一行，不多不少，不要别的内容：

```
W2963431257 | 切题 | 研究的正是需求里的问题，用的也是需求要的那类方法
W1234567890 | 不切题 | 同一个大领域，但问题与方法都不是需求要的
```

## 规矩

- 只写 `$out`，别的文件都不要建、不要改。
- 只按上面给的题目与摘要判，不联网，不运行代码。
- 没有摘要的按题目与出处判；两头都说得通的，按「研究者会不会想看到它」定。
""")


def listing(paper: Paper) -> str:
    facts = " · ".join(x for x in (str(paper.year or "年份不详"), paper.venue) if x)
    abstract = paper.abstract[:ABSTRACT_MAX] + ("…" if len(paper.abstract) > ABSTRACT_MAX else "")
    return "\n".join([f"### {paper.key}", f"- 题目：{paper.title or '（没有题目）'}",
                      f"- 年份 · 出处：{facts}", f"- 摘要：{abstract or '（没有摘要）'}"])


def parse(text: str, keys: list[str]) -> tuple[dict[str, tuple[str, str]], list[str]]:
    got: dict[str, tuple[str, str]] = {}
    for line in text.splitlines():
        m = LINE_RE.match(line)
        if m and m.group(1) in keys:
            got[m.group(1)] = (m.group(2), m.group(3))
    missing = [k for k in keys if k not in got]
    return got, ([f"缺 {len(missing)} 篇：{', '.join(missing[:5])}"] if missing else [])


def judge_batch(runner, tuning: Tuning, requirement: str, batch_dir: Path, papers: list[Paper]
                ) -> dict[str, tuple[str, str]]:
    """一批一个会话、一个目录（会话的事件流写在 cwd 下，并行的不能共用）。判过的不重判；四十篇偶尔
    漏写一两行（实测 Opus 漏过一篇），只把漏的再起一个会话判，在这批的 rest/ 里。"""
    keys = [p.key for p in papers]
    out = batch_dir / OUT_NAME
    if not out.is_file():
        batch_dir.mkdir(parents=True, exist_ok=True)
        prompt = PROMPT.substitute(count=len(papers), out=OUT_NAME, requirement=requirement,
                                   listing="\n\n".join(map(listing, papers)))
        # 不走 session.run_session：那里的模型与深度取按人的设置（执行层的），评分要另指好模型
        result = runner.run(prompt=f"{prompt.rstrip()}\n\n{runner.tool_guide(())}",
                            cwd=batch_dir, timeout_s=session.executor_timeout_s(),
                            allowed_paths=[batch_dir], tuning=tuning)
        session.stash_executor_logs(batch_dir, batch_dir / "executor")
        (batch_dir / "usage.json").write_text(json.dumps(usage(result), ensure_ascii=False))
        outside = [f for f in result.changed_files
                   if f != OUT_NAME and not f.startswith("executor/")]
        if outside or result.timed_out or result.exit_code != 0 or not out.is_file():
            raise RuntimeError(f"{batch_dir} 评分会话没走完：exit={result.exit_code} "
                               f"timed_out={result.timed_out} 越界={outside} "
                               f"有结论={out.is_file()}")
    got, problems = parse(out.read_text(encoding="utf-8"), keys)
    if problems:
        if batch_dir.name == REST_DIRNAME:
            raise RuntimeError(f"{out} 补判了还缺：{'；'.join(problems)}")
        LOGGER.info("judge_rest batch=%s %s", batch_dir.name, problems[0])
        got |= judge_batch(runner, tuning, requirement, batch_dir / REST_DIRNAME,
                           [p for p in papers if p.key not in got])
    return got


def usage(result) -> dict:
    """一次会话的花费：Claude Code 有美元；Codex 订阅报不出美元（NaN），token 从事件里加。"""
    tokens: dict[str, int] = {}
    for event in result.events:
        for k, v in (event.get("usage") or {}).items():
            if isinstance(v, int):
                tokens[k] = tokens.get(k, 0) + v
    cost = None if math.isnan(result.cost_usd) else result.cost_usd
    return {"cost_usd": cost, "duration_s": result.duration_s, "tokens": tokens}


def prior_verdicts(out: Path) -> dict[str, tuple[str, str]]:
    """评分目录里已经判过的（所有批次、补判的也算）：按 W 号复用，加运行、加题时不重判。"""
    known: dict[str, tuple[str, str]] = {}
    for path in sorted(out.glob(f"batch-*/**/{OUT_NAME}")):
        for line in path.read_text(encoding="utf-8").splitlines():
            m = LINE_RE.match(line)
            if m:
                known.setdefault(m.group(1), (m.group(2), m.group(3)))
    return known


def agreement(verdicts: dict[str, tuple[str, str]], other_json: Path) -> dict:
    """两家评分模型判同一批论文的一致率与 Cohen's kappa（扣掉碰巧一致的部分）。"""
    other = {k: v["verdict"] for k, v in json.loads(other_json.read_text())["verdicts"].items()}
    keys = sorted(set(verdicts) & set(other))
    mine = [verdicts[k][0] == RELEVANT for k in keys]
    theirs = [other[k] == RELEVANT for k in keys]
    n = len(keys)
    observed = sum(a == b for a, b in zip(mine, theirs, strict=True)) / n
    p_mine, p_theirs = sum(mine) / n, sum(theirs) / n
    chance = p_mine * p_theirs + (1 - p_mine) * (1 - p_theirs)
    return {"against": str(other_json), "n": n, "agree": round(observed, 3),
            "kappa": round((observed - chance) / (1 - chance), 3) if chance < 1 else None}


def refs_of(client: OpenAlex, review: str) -> dict[str, Paper]:
    [doc] = client.by_keys([review])
    keys = sorted({work_key(r) for r in doc["referenced_works"]})
    return {p.key: p for p in map(from_openalex, client.by_keys(keys))}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("requirement", type=Path, help="工作区的 requirement.md（需求原文）")
    ap.add_argument("review", help="当标准答案的综述的 OpenAlex W 号")
    ap.add_argument("out", type=Path, help="评分目录：每批一个子目录，结果 judge.json")
    ap.add_argument("runs", type=Path, nargs="+", help="literature_recall.py 跑出来的产出目录")
    ap.add_argument("--backend", default="claude_code", choices=("claude_code", "codex"))
    ap.add_argument("--model", default="opus", help="评分模型（这家 CLI 认的名字）")
    ap.add_argument("--effort", default="high", help="思考深度")
    ap.add_argument("--negatives", default="W4415344803",
                    help="无关综述的 W 号：它的参考文献应判不切题（缺省：大模型做组合优化）")
    ap.add_argument("--neg-sample", type=int, default=40, help="混进去验评分模型的无关论文篇数")
    ap.add_argument("--against", type=Path, help="另一家评分模型的 judge.json：算两家的一致率")
    ap.add_argument("--cache", type=Path, default=Path.home() / ".cache" / "ai4sci-literature-eval")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")

    client = OpenAlex(Web(get=cached(args.cache)), key=api_key())
    gold = refs_of(client, args.review)
    core = {k for k, p in gold.items() if CORE_RE.search(f"{p.title} {p.abstract}")}
    runs = []
    for run in args.runs:
        rows = [json.loads(x) for x in (run / "candidates.jsonl").read_text().splitlines()]
        runs.append((run, json.loads((run / "eval.json").read_text()), rows))
    found = {r["paper"]["key"]: Paper.from_dict(r["paper"]) for _, _, rows in runs for r in rows
             if r["paper"]["key"] not in gold}
    negatives = {k: p for k, p in refs_of(client, args.negatives).items()
                 if k not in gold and k not in found}
    neg_probe = random.Random(SEED).sample(sorted(negatives), min(args.neg_sample, len(negatives)))
    papers = {**gold, **found, **{k: negatives[k] for k in neg_probe}}

    known = prior_verdicts(args.out)
    todo = [papers[k] for k in sorted(papers) if k not in known]
    random.Random(SEED + 1).shuffle(todo)
    start = len(list(args.out.glob("batch-*")))
    batches = [todo[i:i + BATCH] for i in range(0, len(todo), BATCH)]
    LOGGER.info("judge pool=%d gold=%d found=%d negatives=%d known=%d todo=%d batches=%d "
                "backend=%s model=%s", len(papers), len(gold), len(found), len(neg_probe),
                len(known), len(todo), len(batches), args.backend, args.model)
    requirement = args.requirement.read_text(encoding="utf-8")
    runner, tuning = get_backend(args.backend), Tuning(args.model, args.effort)
    with ThreadPoolExecutor(PARALLEL) as pool:
        parts = list(pool.map(lambda ib: judge_batch(runner, tuning, requirement,
                                                     args.out / f"batch-{start + ib[0]:02d}",
                                                     ib[1]),
                              enumerate(batches)))
    verdicts = {k: v for k, v in known.items() if k in papers}
    for part in parts:
        verdicts |= part

    def rate(keys, want: str) -> dict:
        hit = sum(verdicts[k][0] == want for k in keys)
        return {"n": len(keys), "hit": hit, "rate": round(hit / len(keys), 3) if keys else None}

    relevant = {k for k in (*gold, *found) if verdicts[k][0] == RELEVANT}
    scores = []
    for run, ev, rows in runs:
        included = {r["paper"]["key"] for r in rows if r["verdict"] == "收"}
        screened = {r["paper"]["key"] for r in rows}
        scores.append({
            "run": str(run), "until": ev.get("until"), "line": ev["line"],
            "screened": len(screened), "included": len(included),
            "relevant_included": len(included & relevant),
            "precision": round(len(included & relevant) / len(included), 3) if included else None,
            "yield": round(len(screened & relevant) / len(screened), 3),
            "recall": round(len(included & relevant) / len(relevant), 3),
            "recall_ceiling": round(min(len(screened), len(relevant)) / len(relevant), 3),
            # 旧口径：收录了几成综述的参考文献
            "gold_included": len(included & set(gold)),
            "gold_recall": round(len(included & set(gold)) / len(gold), 3),
            # 漏在哪：看过没收的是筛选漏的，没看过的是检索与排序没送到
            "screen_missed": len((screened - included) & relevant),
            "never_screened": len(relevant - screened),
            "by_hop": {h: {"screened": sum(r["hop"] == h for r in rows),
                           "included": sum(r["hop"] == h and r["verdict"] == "收" for r in rows),
                           "relevant_included": sum(r["hop"] == h and r["verdict"] == "收"
                                                    and r["paper"]["key"] in relevant
                                                    for r in rows)}
                       for h in sorted({r["hop"] for r in rows})},
        })
    spent = [json.loads(p.read_text()) for p in sorted(args.out.glob("batch-*/**/usage.json"))]
    result = {
        "review": args.review, "judge": {"backend": args.backend, "model": args.model,
                                         "effort": args.effort},
        "gold": len(gold), "core": len(core), "found_outside_gold": len(found),
        "relevant": len(relevant), "relevant_from_gold": len(relevant & set(gold)),
        "relevant_outside_gold": len(relevant - set(gold)),
        "judge_check": {"core_relevant": rate(sorted(core), RELEVANT),
                        "background_relevant": rate(sorted(set(gold) - core), RELEVANT),
                        "negatives_irrelevant": rate(neg_probe, IRRELEVANT)},
        "agreement": agreement(verdicts, args.against) if args.against else None,
        "runs": scores,
        "judge_sessions": spent,
        "verdicts": {k: {"verdict": v[0], "reason": v[1],
                         "kind": "gold" if k in gold else "negative" if k in negatives else "found"}
                     for k, v in sorted(verdicts.items())},
    }
    (args.out / "judge.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k not in ("verdicts", "judge_sessions")},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
