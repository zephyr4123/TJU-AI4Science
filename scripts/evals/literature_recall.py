"""文献检索步骤的评测，第一步：照一道题跑一次检索（外层 #212 #215 #217，报告 §6）。

一道题 = 一个用户需求 + 这个需求下什么算对（literature_questions/<题>.md，literature_question.py
读）。照题里的需求跑一次文献检索，记下看过、收录的每篇（candidates.jsonl）与一行汇总（eval.json）。
打分是第二步 literature_judge.py：评分模型照题里的判对标准判，算收得准不准、看得准不准、找得全不全。

题里给了圈定范围的综述时：综述本身的任何版本都挡在外面（预印本、会议版的 W 号各不相同，按题目认），
否则向后一跳就把它的参考文献全抄回来；默认只认综述发表日（含）以前的论文（#215），综述之后发表的
论文不进候选池，等于在综述发表那天跑这个工具，`--no-cutoff` 关掉。eval.json 里另按第一版的旧口径
（收录了几成综述参考文献）量一遍，只作对照。

依赖内仓的代码（`framework.capabilities.literature_search`），用内仓的 venv 跑；内仓的生产代码
不依赖这里。OpenAlex 的回答按 URL 存在 --cache 目录里复用：同一道题换参数重跑不重复扣额度。

用法（在外层仓根；一次只跑一个检索，几个同时跑会撞 arXiv 的限速）：
    . ~/.secrets/loader.sh
    withkey openalex platform/.venv/bin/python scripts/evals/literature_recall.py \
        <工作区目录> <题目文件> <claude_code|codex> <最多跳数> <每跳筛选数> <停止下限> \
        [--seeds <seeds.md>] [--no-cutoff]

工作区要先建好：requirement.md 是题里「需求」一节的原文、确认过，流程实例上挂了 literature-search
（报告 §12）；AI4SCI_HOME 指到评测用的数据根，别拿正式数据根跑。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
from pathlib import Path

import literature_question
from backends import get_backend
from framework.capabilities.literature_search import loop
from framework.capabilities.literature_search.exchange import parse_seeds
from framework.capabilities.literature_search.openalex import BASE_URL, OpenAlex, api_key
from framework.capabilities.literature_search.papers import from_openalex, work_key
from framework.capabilities.literature_search.web import Web, http_get
from framework.contracts import requirement
from framework.contracts.capability import Inputs
from framework.workspace import outputs
from framework.workspace.root import load


def cached(cache: Path):
    """按 URL 存盘的 GET：命中就读盘，不连网也不扣额度。只存正文，响应头不存。"""
    cache.mkdir(parents=True, exist_ok=True)

    def get(url: str, headers: dict[str, str]):
        path = cache / hashlib.sha256(url.encode()).hexdigest()
        if path.is_file():
            return path.read_bytes(), {}
        body, got = http_get(url, headers)
        path.write_bytes(body)
        return body, got
    return get


CORE_RE = re.compile(r"physics[- ](informed|guided|constrained)|\bPINNs?\b", re.IGNORECASE)


def same_title(a: str, b: str) -> bool:
    return re.sub(r"\W+", "", a.lower()) == re.sub(r"\W+", "", b.lower())


class Blind(OpenAlex):
    """评测用的 OpenAlex：综述本身的任何版本（预印本、会议版，W 号各不相同，按题目认）都取不到；
    给了 until 时只取那天（含）以前发表的，每个请求的 filter 加一条 to_publication_date。检索命中、
    种子、参考文献、谁引用了它，元数据都从这里取，取不到的就进不了候选池。"""

    def __init__(self, web: Web, key: str | None, title: str | None, until: str | None) -> None:
        super().__init__(web, key=key)
        self.title, self.until = title, until

    def _page(self, params: dict[str, str]) -> dict:
        if self.until is not None:
            cut = f"to_publication_date:{self.until}"
            params = {**params, "filter": f"{params['filter']},{cut}" if "filter" in params
                      else cut}
        doc = super()._page(params)
        if self.title is not None:
            doc["results"] = [w for w in doc["results"]
                              if not same_title(w.get("display_name") or "", self.title)]
        return doc


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("workspace", type=Path,
                    help="这道题的工作区：requirement.md 要和题里的需求一字不差")
    ap.add_argument("question", type=Path, help="题目文件 literature_questions/<题>.md")
    ap.add_argument("backend", choices=("claude_code", "codex"))
    ap.add_argument("max_hops", type=int)
    ap.add_argument("per_hop", type=int)
    ap.add_argument("min_new", type=int)
    ap.add_argument("--seeds", type=Path,
                    help="固定的 seeds.md：不起种子会话，比较参数时少一处随机")
    ap.add_argument("--cache", type=Path, default=Path.home() / ".cache" / "ai4sci-literature-eval")
    ap.add_argument("--no-cutoff", action="store_true", help="不按综述发表日截断（截断以前的口径）")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")

    question = literature_question.load(args.question)
    ws = load(args.workspace)
    assert requirement.read(ws.root).strip() == question.requirement.strip(), (
        f"{args.workspace} 的 requirement.md 和题 {question.name} 的需求对不上")
    web = Web(get=cached(args.cache))
    plain = OpenAlex(web, key=api_key())
    gold: set[str] = set()
    resolvable: dict = {}
    core: set[str] = set()
    until = title = None
    if question.review:
        [doc] = plain.by_keys([question.review])
        title = doc["display_name"]
        gold = {work_key(r) for r in doc["referenced_works"]}
        resolvable = {p.key: p for p in map(from_openalex, plain.by_keys(sorted(gold)))}
        core = {k for k, p in resolvable.items() if CORE_RE.search(f"{p.title} {p.abstract}")}
        # 单篇取不扣积分；SELECT 里没有发表日，单独取一次
        until = None if args.no_cutoff else json.loads(
            web.get(f"{BASE_URL}/{question.review}?select=publication_date")[0])["publication_date"]
    client = Blind(web, api_key(), title, until)
    out, _ = outputs.open_output(ws, "literature", title=f"评测 {question.name}",
                                 by="literature-search", inputs=[], params={}, flow=None,
                                 step=None, requirement=1, chat_id=None)
    if args.seeds:
        text = args.seeds.read_text(encoding="utf-8")
        (out / "seeds.md").write_text(text, encoding="utf-8")
        fixed, problems = parse_seeds(text)
        assert fixed is not None, problems
        loop._seed_session = lambda *a, **k: fixed
    pools = []
    expand = loop._expand

    def spy(pool, *a, **k):  # 记下池子：「线索里出现过」要算没轮到筛的
        expand(pool, *a, **k)
        pools.append(pool)
    loop._expand = spy

    excluded = frozenset({question.review}) if question.review else frozenset()
    line = loop.search(out, Inputs(ws.root), get_backend(args.backend),
                       loop.Limits(args.max_hops, args.per_hop, args.min_new), fulltext=False,
                       client=client, excluded=excluded)
    rows = [json.loads(x) for x in (out / "candidates.jsonl").read_text().splitlines()]
    screened = {r["paper"]["key"] for r in rows}
    included = {r["paper"]["key"] for r in rows if r["verdict"] == "收"}
    reached = screened | (set(pools[-1].leads) if pools else set())
    by_hop: dict[int, dict[str, int]] = {}
    for r in rows:
        h = by_hop.setdefault(r["hop"], {"screened": 0, "gold": 0, "included": 0, "gold_in": 0,
                                         "core_in": 0})
        key, took = r["paper"]["key"], r["verdict"] == "收"
        h["screened"] += 1
        h["gold"] += key in gold
        h["included"] += took
        h["gold_in"] += took and key in gold
        h["core_in"] += took and key in core
    result = {"question": question.name, "kind": question.kind, "review": question.review,
              "until": until, "abstract_max": loop.ABSTRACT_MAX,
              "gold": len(gold), "gold_resolvable": len(resolvable), "gold_core": len(core),
              "backend": args.backend,
              "limits": [args.max_hops, args.per_hop, args.min_new], "line": line,
              "screened": len(screened), "included": len(included),
              "gold_screened": len(gold & screened), "gold_included": len(gold & included),
              "core_included": len(core & included),
              "gold_reached": len(gold & reached), "by_hop": by_hop,
              # 防泄漏的事后核对：候选里不该有题目和综述相同的（Blind 已挡，这里再数一遍）
              "leaked": [r["paper"]["key"] for r in rows
                         if title and same_title(r["paper"]["title"], title)],
              "gold_keys_reached": sorted(gold & reached),
              "openalex_requests": client.requests, "openalex_remaining": client.remaining}
    (out / "eval.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != "gold_keys_reached"},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
