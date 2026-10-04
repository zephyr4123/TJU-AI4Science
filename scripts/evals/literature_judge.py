"""给文献检索步骤打分：评分模型照题里的判对标准判对不对，打三个分（外层 #215 #217，报告 §6）。

一道题（literature_questions/<题>.md）自带判对标准：专的题只算方法和领域都对上的，广的题沾边的都算，
平行、串行的题还要给对的论文标分支（并列的子方向、有先后的步骤）。评分模型只看需求原文、判对标准和
每篇的题目、年份、出处、摘要，逐篇判「切题 / 不切题」：

- 待判的论文 = 这道题所有运行里执行层看过摘要的论文 + 题里综述的参考文献（有综述时）
  + 40 篇无关论文；
- 这道题全部对的论文 = 待判论文里判切题的（无关论文不进）；
- 一次运行打三个分：
  - 收得准不准 = 收录的里对的 ÷ 收录的；
  - 看得准不准 = 看过的里对的 ÷ 看过的（每次只看约 125 篇：第 0 跳 60 加种子、之后每跳 30）；
  - 找得全不全 = 收录的里对的 ÷ 全部对的，旁边给上限 min(看过, 全部对的) ÷ 全部对的；
    平行、串行的题另给每个分支各自的找得全不全，最差的那个分支单列。
  另给两项找原因：看过没收、其实对的（筛选漏的）；对的里没看过的（检索与排序没送到）。
  有综述时按第一版的旧口径（收录了几成综述参考文献）量一遍，只作对照。
- 「全部对的论文」随加进来的运行变全，比较版本时把各版本的运行一起交给这个脚本，在同一份上算分。

评分模型先过关才采信：40 篇无关论文（一篇讲大模型做组合优化的综述的参考文献）应几乎全判不切题；
题里有综述、且综述是 PINN 方向的，它的参考文献里提到 PINN 类方法的应几乎全判切题；两家评分模型
（缺省 Claude Code 的 Opus、思考深度高；`--backend codex` 再判一遍）判同一批论文要一致
（Cohen's κ）。
打乱顺序，不告诉它哪篇是哪类，不给执行层写的纳入标准。每批一个隔离会话，不联网、不放行任何命令。

用法（在外层仓根，literature_recall.py 跑完以后）：
    . ~/.secrets/loader.sh
    withkey openalex platform/.venv/bin/python scripts/evals/literature_judge.py \
        <题目文件> <评分目录> <产出目录…> \
        [--backend claude_code --model opus --effort high] [--against <另一家的 judge.json>]

判过的论文按编号复用（评分目录里所有 judgments.md），加运行时只判新的；结果写在评分目录的
judge.json。判对标准改了要换一个新的评分目录，旧判定不能复用。
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
from literature_question import Question
from literature_question import load as load_question
from literature_recall import CORE_RE, cached

LOGGER = logging.getLogger("literature_judge")
RELEVANT, IRRELEVANT = "切题", "不切题"
OTHER_BRANCH, NO_BRANCH = "其他", "-"
REFUSED = "拒判"  # 评分会话正常结束却没写结论，拆到一篇还这样（不计分，单列）
_CELL = r"\s*\|\s*"
LINE_RE = re.compile(rf"^\s*(W\d+){_CELL}({IRRELEVANT}|{RELEVANT}){_CELL}(.+?)\s*$")
BRANCH_LINE_RE = re.compile(
    rf"^\s*(W\d+){_CELL}({IRRELEVANT}|{RELEVANT}){_CELL}([^|]+?){_CELL}(.+?)\s*$")
ABSTRACT_MAX = 1500
BATCH = 40
PARALLEL = 4
SEED = 215
OUT_NAME = "judgments.md"
REST_DIRNAME = "rest"

PROMPT = string.Template("""# 任务：照判对标准判断一批论文对不对（$count 篇）

你在给一个文献检索工具的结果打分。下面是研究者写的需求、这个需求下什么算对（判对标准），和一批
论文的题目、年份、出处与摘要。逐篇照判对标准判「切题」或「不切题」，结论写进 `$out`。

## 研究需求

$requirement

## 判对标准

$rubric
$branch_rule
## 论文（$count 篇）

$listing

## $out 的写法

$format
上面每个 W 号都要有一行，不多不少，不要别的内容。

## 规矩

- 只写 `$out`，别的文件都不要建、不要改。
- 只按上面给的题目与摘要判，不联网，不运行代码。
- 没有摘要的按题目与出处判；两头都说得通的，按「照判对标准，研究者会不会想看到它」定。
""")
PLAIN_FORMAT = """每篇一行，三段用 `|` 隔开：W 号 | 切题 或 不切题 | 一句理由
（二十到六十字，照判对标准说）：

```
W2963431257 | 切题 | 研究的正是需求里的问题，用的也是需求要的那类方法
W1234567890 | 不切题 | 同一个大领域，但问题与方法都不是需求要的
```
"""
BRANCH_FORMAT = """每篇一行，四段用 `|` 隔开：W 号 | 切题 或 不切题 | 分支 | 一句理由
（二十到六十字）。
切题的写它属于哪个分支（只写分支名：$names；都不属于写「其他」），不切题的分支写 `-`：

```
W2963431257 | 切题 | $first | 属于这个分支，问题与方法都对上
W1234567890 | 不切题 | - | 不满足判对标准
```
"""


def listing(paper: Paper) -> str:
    facts = " · ".join(x for x in (str(paper.year or "年份不详"), paper.venue) if x)
    abstract = paper.abstract[:ABSTRACT_MAX] + ("…" if len(paper.abstract) > ABSTRACT_MAX else "")
    return "\n".join([f"### {paper.key}", f"- 题目：{paper.title or '（没有题目）'}",
                      f"- 年份 · 出处：{facts}", f"- 摘要：{abstract or '（没有摘要）'}"])


Verdict = tuple[str, str, str]  # （切题 / 不切题, 分支或 "-", 理由）


def parse_line(line: str, branches: dict[str, str]) -> tuple[str, Verdict] | None:
    """一行判定；有分支的题要四段，切题的分支要是题里的分支名或「其他」，不认的当没判。"""
    if branches:
        m = BRANCH_LINE_RE.match(line)
        if not m:
            return None
        branch = m.group(3).strip()
        ok = (branch in branches or branch == OTHER_BRANCH) if m.group(2) == RELEVANT else True
        return (m.group(1), (m.group(2), branch if m.group(2) == RELEVANT else NO_BRANCH,
                             m.group(4))) if ok else None
    m = LINE_RE.match(line)
    return (m.group(1), (m.group(2), NO_BRANCH, m.group(3))) if m else None


def parse(text: str, keys: list[str], branches: dict[str, str]
          ) -> tuple[dict[str, Verdict], list[str]]:
    got: dict[str, Verdict] = {}
    for line in text.splitlines():
        hit = parse_line(line, branches)
        if hit and hit[0] in keys:
            got[hit[0]] = hit[1]
    missing = [k for k in keys if k not in got]
    return got, ([f"缺 {len(missing)} 篇：{', '.join(missing[:5])}"] if missing else [])


def prompt_for(question: Question, papers: list[Paper]) -> str:
    names = "、".join(question.branches)
    rules = (f"- {k}：{v}\n" for k, v in question.branches.items())
    branch_rule = "".join(["\n分支：\n\n", *rules]) if question.branches else ""
    fmt = (string.Template(BRANCH_FORMAT).substitute(
        names=names, first=next(iter(question.branches))) if question.branches else PLAIN_FORMAT)
    return PROMPT.substitute(count=len(papers), out=OUT_NAME, requirement=question.requirement,
                             rubric=question.rubric, branch_rule=branch_rule, format=fmt,
                             listing="\n\n".join(map(listing, papers)))


def judge_batch(runner, tuning: Tuning, question: Question, batch_dir: Path, papers: list[Paper]
                ) -> dict[str, Verdict]:
    """一批一个会话、一个目录（会话的事件流写在 cwd 下，并行的不能共用）。判过的不重判；四十篇偶尔
    漏写一两行（实测 Opus 漏过一篇），只把漏的再起一个会话判，在这批的 rest/ 里。"""
    keys = [p.key for p in papers]
    out = batch_dir / OUT_NAME
    if (batch_dir / "part-1").is_dir():
        return _split(runner, tuning, question, batch_dir, papers)
    if not out.is_file():
        batch_dir.mkdir(parents=True, exist_ok=True)
        prompt = prompt_for(question, papers)
        # 不走 session.run_session：那里的模型与深度取按人的设置（执行层的），评分要另指好模型
        result = runner.run(prompt=f"{prompt.rstrip()}\n\n{runner.tool_guide(())}",
                            cwd=batch_dir, timeout_s=session.executor_timeout_s(),
                            allowed_paths=[batch_dir], tuning=tuning)
        session.stash_executor_logs(batch_dir, batch_dir / "executor")
        (batch_dir / "usage.json").write_text(json.dumps(usage(result), ensure_ascii=False))
        outside = [f for f in result.changed_files
                   if f != OUT_NAME and not f.startswith("executor/")]
        if not (outside or result.timed_out or result.exit_code != 0 or out.is_file()):
            # 会话正常结束却没写结论：实测是 Claude 的安全分类器拦了写入（扩散模型那道题，一批里有
            # 蛋白质设计的论文，会话自述「写这个文件的那次回复被安全分类器拦下了」）。拦不拦不固定：
            # 九批里两批第一次被拦，整批再判就过了。所以对半拆开重判（等于重试），
            # 拆到一篇还拦就记拒判
            LOGGER.warning("judge_blocked batch=%s papers=%d report=%s", batch_dir, len(papers),
                           result.report[:200])
            if len(papers) == 1:
                return {papers[0].key: (REFUSED, NO_BRANCH, result.report[:200])}
            return _split(runner, tuning, question, batch_dir, papers)
        if outside or result.timed_out or result.exit_code != 0 or not out.is_file():
            raise RuntimeError(f"{batch_dir} 评分会话没走完：exit={result.exit_code} "
                               f"timed_out={result.timed_out} 越界={outside} "
                               f"有结论={out.is_file()}")
    got, problems = parse(out.read_text(encoding="utf-8"), keys, question.branches)
    if problems:
        if batch_dir.name == REST_DIRNAME:
            raise RuntimeError(f"{out} 补判了还缺：{'；'.join(problems)}")
        LOGGER.info("judge_rest batch=%s %s", batch_dir.name, problems[0])
        got |= judge_batch(runner, tuning, question, batch_dir / REST_DIRNAME,
                           [p for p in papers if p.key not in got])
    return got


def _split(runner, tuning: Tuning, question: Question, batch_dir: Path, papers: list[Paper]
           ) -> dict[str, Verdict]:
    mid = len(papers) // 2
    return (judge_batch(runner, tuning, question, batch_dir / "part-1", papers[:mid])
            | judge_batch(runner, tuning, question, batch_dir / "part-2", papers[mid:]))


def usage(result) -> dict:
    """一次会话的花费：Claude Code 有美元；Codex 订阅报不出美元（NaN），token 从事件里加。"""
    tokens: dict[str, int] = {}
    for event in result.events:
        for k, v in (event.get("usage") or {}).items():
            if isinstance(v, int):
                tokens[k] = tokens.get(k, 0) + v
    cost = None if math.isnan(result.cost_usd) else result.cost_usd
    return {"cost_usd": cost, "duration_s": result.duration_s, "tokens": tokens}


def prior_verdicts(out: Path, branches: dict[str, str]) -> dict[str, Verdict]:
    """评分目录里已经判过的（所有批次、补判的也算）：按 W 号复用，加运行、加题时不重判。"""
    known: dict[str, Verdict] = {}
    for path in sorted(out.glob(f"batch-*/**/{OUT_NAME}")):
        for line in path.read_text(encoding="utf-8").splitlines():
            hit = parse_line(line, branches)
            if hit:
                known.setdefault(*hit)
    return known


def agreement(verdicts: dict[str, Verdict], other_json: Path) -> dict:
    """两家评分模型判同一批论文的一致率与 Cohen's kappa（扣掉碰巧一致的部分）。"""
    other = {k: v["verdict"] for k, v in json.loads(other_json.read_text())["verdicts"].items()}
    keys = sorted(k for k in set(verdicts) & set(other)
                  if verdicts[k][0] != REFUSED and other[k] != REFUSED)
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
    ap.add_argument("question", type=Path, help="题目文件 literature_questions/<题>.md")
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

    question = load_question(args.question)
    client = OpenAlex(Web(get=cached(args.cache)), key=api_key())
    gold = refs_of(client, question.review) if question.review else {}
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

    known = prior_verdicts(args.out, question.branches)
    todo = [papers[k] for k in sorted(papers) if k not in known]
    random.Random(SEED + 1).shuffle(todo)
    start = len(list(args.out.glob("batch-*")))
    batches = [todo[i:i + BATCH] for i in range(0, len(todo), BATCH)]
    LOGGER.info("judge question=%s pool=%d gold=%d found=%d negatives=%d known=%d todo=%d "
                "batches=%d backend=%s model=%s", question.name, len(papers), len(gold),
                len(found), len(neg_probe), len(known), len(todo), len(batches), args.backend,
                args.model)
    runner, tuning = get_backend(args.backend), Tuning(args.model, args.effort)
    with ThreadPoolExecutor(PARALLEL) as pool:
        parts = list(pool.map(lambda ib: judge_batch(runner, tuning, question,
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
    by_branch = {b: {k for k in relevant if verdicts[k][1] == b}
                 for b in (*question.branches, OTHER_BRANCH)} if question.branches else {}
    scores = [score(run, ev, rows, relevant, set(gold), by_branch) for run, ev, rows in runs]
    spent = [json.loads(p.read_text()) for p in sorted(args.out.glob("batch-*/**/usage.json"))]
    result = {
        "question": question.name, "kind": question.kind, "review": question.review,
        "judge": {"backend": args.backend, "model": args.model, "effort": args.effort},
        "gold": len(gold), "core": len(core), "found_outside_gold": len(found),
        "relevant": len(relevant), "relevant_from_gold": len(relevant & set(gold)),
        "relevant_outside_gold": len(relevant - set(gold)),
        "relevant_by_branch": {b: len(ks) for b, ks in by_branch.items()},
        "judge_check": {"core_relevant": rate(sorted(core), RELEVANT) if core else None,
                        "background_relevant": rate(sorted(set(gold) - core), RELEVANT)
                        if gold else None,
                        "negatives_irrelevant": rate(neg_probe, IRRELEVANT)},
        "refused": sorted(k for k, v in verdicts.items() if v[0] == REFUSED),
        "agreement": agreement(verdicts, args.against) if args.against else None,
        "runs": scores,
        "judge_sessions": spent,
        "verdicts": {k: {"verdict": v[0], "branch": v[1], "reason": v[2],
                         "kind": "gold" if k in gold else "negative" if k in negatives else "found"}
                     for k, v in sorted(verdicts.items())},
    }
    (args.out / "judge.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k not in ("verdicts", "judge_sessions")},
                     ensure_ascii=False))


def score(run: Path, ev: dict, rows: list[dict], relevant: set[str], gold: set[str],
          by_branch: dict[str, set[str]]) -> dict:
    included = {r["paper"]["key"] for r in rows if r["verdict"] == "收"}
    screened = {r["paper"]["key"] for r in rows}
    branch_recall = {b: round(len(included & ks) / len(ks), 3) for b, ks in by_branch.items()
                     if ks and b != OTHER_BRANCH}
    return {
        "run": str(run), "screen": ev.get("screen"),
        "crossref_results": ev.get("crossref_results"), "line": ev["line"],
        "screened": len(screened), "included": len(included),
        "relevant_included": len(included & relevant),
        "precision": round(len(included & relevant) / len(included), 3) if included else None,
        "yield": round(len(screened & relevant) / len(screened), 3),
        "recall": round(len(included & relevant) / len(relevant), 3),
        "recall_ceiling": round(min(len(screened), len(relevant)) / len(relevant), 3),
        # 平行、串行的题：每个分支各自找回几成，最差的那个单列（不能只顾一头）
        "branch_recall": branch_recall,
        "worst_branch_recall": min(branch_recall.values()) if branch_recall else None,
        # 旧口径：收录了几成综述的参考文献（有综述时）
        "gold_included": len(included & gold),
        "gold_recall": round(len(included & gold) / len(gold), 3) if gold else None,
        # 漏在哪：看过没收的是筛选漏的，没看过的是检索与排序没送到
        "screen_missed": len((screened - included) & relevant),
        "never_screened": len(relevant - screened),
        "by_hop": {h: {"screened": sum(r["hop"] == h for r in rows),
                       "included": sum(r["hop"] == h and r["verdict"] == "收" for r in rows),
                       "relevant_screened": sum(r["hop"] == h and r["paper"]["key"] in relevant
                                                for r in rows),
                       "relevant_included": sum(r["hop"] == h and r["verdict"] == "收"
                                                and r["paper"]["key"] in relevant for r in rows)}
                   for h in sorted({r["hop"] for r in rows})},
    }


if __name__ == "__main__":
    main()
