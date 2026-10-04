"""文献检索步骤的召回实测（外层 #212，报告见 docs/specs/literature-search.md §7）。

拿一篇综述的参考文献当标准答案，跑一次文献检索（把这篇综述挡在池外，否则向后一跳就把答案全抄
回来），量答案有几篇被看过摘要、被收录、在线索里出现过，按跳拆开。结果写在产出目录的 eval.json，
并打一行汇总。

依赖内仓的代码（`framework.capabilities.literature_search`），用内仓的 venv 跑；内仓的生产代码
不依赖这里。OpenAlex 的回答按 URL 存在 --cache 目录里复用：同一道题换参数重跑不重复扣额度。

用法（在外层仓根）：
    . ~/.secrets/loader.sh
    withkey openalex platform/.venv/bin/python scripts/evals/literature_recall.py \
        <工作区目录> <综述 W 号> <claude_code|codex> <最多跳数> <每跳筛选数> <停止下限> \
        [--seeds <固定的 seeds.md>] [--cache <目录>]

工作区要先建好、需求确认过、流程实例上挂了 literature-search（报告 §7.1 有一份示例需求）；
AI4SCI_HOME 指到实测用的数据根，别拿正式数据根跑。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
from pathlib import Path

from backends import get_backend
from framework.capabilities.literature_search import loop
from framework.capabilities.literature_search.exchange import parse_seeds
from framework.capabilities.literature_search.openalex import OpenAlex, api_key
from framework.capabilities.literature_search.papers import work_key
from framework.capabilities.literature_search.web import Web, http_get
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


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("workspace", type=Path)
    ap.add_argument("review", help="当标准答案的综述的 OpenAlex W 号")
    ap.add_argument("backend", choices=("claude_code", "codex"))
    ap.add_argument("max_hops", type=int)
    ap.add_argument("per_hop", type=int)
    ap.add_argument("min_new", type=int)
    ap.add_argument("--seeds", type=Path, help="固定的 seeds.md：不起种子会话，比较参数时少一处随机")
    ap.add_argument("--cache", type=Path, default=Path.home() / ".cache" / "ai4sci-literature-eval")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(name)s %(message)s")

    client = OpenAlex(Web(get=cached(args.cache)), key=api_key())
    [doc] = client.by_keys([args.review])
    gold = {work_key(r) for r in doc["referenced_works"]}
    ws = load(args.workspace)
    out, _ = outputs.open_output(ws, "literature", title=f"召回实测 {args.review}",
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

    line = loop.search(out, Inputs(ws.root), get_backend(args.backend),
                       loop.Limits(args.max_hops, args.per_hop, args.min_new), fulltext=False,
                       client=client, excluded=frozenset({args.review}))
    rows = [json.loads(x) for x in (out / "candidates.jsonl").read_text().splitlines()]
    screened = {r["paper"]["key"] for r in rows}
    included = {r["paper"]["key"] for r in rows if r["verdict"] == "收"}
    reached = screened | (set(pools[-1].leads) if pools else set())
    by_hop: dict[int, dict[str, int]] = {}
    for r in rows:
        h = by_hop.setdefault(r["hop"], {"screened": 0, "gold": 0, "included": 0, "gold_in": 0})
        h["screened"] += 1
        h["gold"] += r["paper"]["key"] in gold
        h["included"] += r["verdict"] == "收"
        h["gold_in"] += r["verdict"] == "收" and r["paper"]["key"] in gold
    result = {"review": args.review, "gold": len(gold), "backend": args.backend,
              "limits": [args.max_hops, args.per_hop, args.min_new], "line": line,
              "screened": len(screened), "included": len(included),
              "gold_screened": len(gold & screened), "gold_included": len(gold & included),
              "gold_reached": len(gold & reached), "by_hop": by_hop,
              "gold_keys_reached": sorted(gold & reached),
              "openalex_requests": client.requests, "openalex_remaining": client.remaining}
    (out / "eval.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k != "gold_keys_reached"},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
