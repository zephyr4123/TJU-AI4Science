---
name: literature-search
description: 文献阶段（检索 + 精读）的现状、评测方法与已经验证过的规律，改文献相关能力前必读
metadata:
  node_type: memory
  type: project
  originSessionId: ecc4450e-06d2-447c-a0b1-2ca7efce5ea9
  modified: 2026-10-12T03:04:30.439Z
---

文献阶段目前有两个步骤，分开做、各自优化：`literature-search`（种子会话 → OpenAlex、Crossref、arXiv、Europe PMC 四家检索 → 每跳筛选 → 顺着引用扩 2 跳 → 并行下原文 → 写 `sources.md`）与 `literature-read`（逐篇读原文，每篇一份带原句的笔记）。出厂流程 `literature-survey` 把两步放在一格里，止于 `sources.md`，不写综述（助理在对话里照笔记回答）。综述能力还是缺口（#154）。OpenAlex 的 key 可选，不带 key 每 IP 每天 1000 积分，一次检索约 80。

**评测**（SOP 在 `docs/specs/literature-search.md` §6，脚本在外层 `scripts/evals/literature_*.py`）：专、广、平行、串行四类共八道题，每题自带判对标准；Opus 主评、Codex 对照；打三个分：收得准不准、看得准不准、找得全不全。基线（Claude Code · Sonnet · medium，1.3.1）：87% / 61% / 47%（上限 81%），一次 0.60 美元（从 0.78 降下来）。

已验证的规律（换哪家执行层都成立）：
- 每跳筛决定往外扩的方向，不能砍；降本只能让筛选变便宜（砍输入有效；换 Haiku 收进来的错论文翻倍；调低思考深度几乎省不了钱）
- 写理由会让模型判得更严，理由也是交给用户的东西，保留
- 续接会话不省钱：省下的固定写入被每轮重读前文抵掉
- 一次运行分不清改动和波动：同一设置的两次运行，单题分数能差近 10 个点。比较要多跑几次、先量噪声、按题看
- 只改筛选时用 `literature_rescreen.py` 重放，不用从头跑

下一步候选：写种子的会话占一半花费（#223）、平行题的冷门类（#220）、串行题第二步（#221）、arXiv 限速丢检索词（#224）、Claude Code + DeepSeek 上的评测（#273，悬着）。

**Why:** 这块是 10 月投入最大的研发线，结论靠一整套评测得来；不知道这些规律，很容易重做已经否掉的实验，或拿一次运行就下结论。
**How to apply:** 改检索、筛选、提示词前先读 spec §0、§8、§11；任何「变好了」都要在八道题上多跑几次、和噪声比；评测材料放 `materials/evals/literature/`。相关：[[project-status]] [[drill-lessons]]
