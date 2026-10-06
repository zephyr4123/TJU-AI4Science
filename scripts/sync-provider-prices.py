#!/usr/bin/env python3
"""从 cc-switch 同步模型价目到内仓的 `backends/catalog/prices.json`（外层 #266）。

跑法（不 import 平台代码，任何 python3 都行）：

    python3 scripts/sync-provider-prices.py <cc-switch 仓库> [--add <模型 id> ...] [--apply]

- 价目的源是 cc-switch（MIT）`src-tauri/src/database/schema.rs` 的 `seed_model_pricing`：一行一个模型，
  美元 / 百万 token 的输入、输出、命中缓存、写缓存。我们只要前三样，写缓存的加价不计（CLI 报得出成本的
  自己算，表对它只是给人看）。
- 同步哪几个模型由 prices.json 现有的键定；`--add` 加新的。cc-switch 里找不到的照实报出来，原值不动。
- 不带 `--apply` 只打差异。文件里记下这次搬自 cc-switch 哪次提交。
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

PRICES = Path(__file__).resolve().parents[1] / "platform" / "backends" / "catalog" / "prices.json"
ROW_RE = re.compile(r'\(\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)",\s*"([^"]+)",?\s*\)')


def seed(repo: Path) -> dict[str, dict]:
    text = (repo / "src-tauri" / "src" / "database" / "schema.rs").read_text(encoding="utf-8")
    start = text.index("fn seed_model_pricing")
    body = text[start:text.index("\n    fn ", start + 10)]
    return {m: {"title": title, "input": float(inp), "cached": float(cache), "output": float(out)}
            for m, title, inp, out, cache, _ in ROW_RE.findall(body)}


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    repo = Path(args[0]).expanduser()
    added = argv[argv.index("--add") + 1:] if "--add" in argv else []
    added = [a for a in added if not a.startswith("--")]
    current = json.loads(PRICES.read_text(encoding="utf-8")) if PRICES.is_file() else {"models": {}}
    wanted = sorted(set(current["models"]) | set(added))
    table = seed(repo)
    commit = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%h %ad", "--date=short"],
                            capture_output=True, text=True, check=True).stdout.strip()
    models: dict[str, dict] = {}
    for model in wanted:
        old = current["models"].get(model)
        new = table.get(model)
        if new is None:
            print(f"  cc-switch 里没有 {model}：留原值" if old else f"  cc-switch 里没有 {model}：没加")
            if old:
                models[model] = old
            continue
        if old != new:
            print(f"  {model}: {old} → {new}")
        models[model] = new
    doc = {"source": f"cc-switch {commit}（MIT，src-tauri/src/database/schema.rs 的 seed_model_pricing）"
                     "；美元 / 百万 token：input 没命中缓存的输入、cached 命中缓存的输入、output 输出",
           "models": models}
    if "--apply" not in argv:
        print(f"共 {len(models)} 个模型；没写，确认后加 --apply")
        return 0
    PRICES.parent.mkdir(parents=True, exist_ok=True)
    PRICES.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"写了 {PRICES}（{len(models)} 个模型，cc-switch {commit}）")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
