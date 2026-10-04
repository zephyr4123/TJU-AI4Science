"""读一道文献检索评测题（外层 #217）：literature_questions/<题>.md。

一道题 = 一个用户需求 + 这个需求下什么算对。题的类型不同（专、广、平行、串行），判对的标准不同：
需求原样作工作区的 requirement.md，交给执行层；判对标准只给评分模型；平行、串行的题另有分支
（并列的子方向、有先后的步骤），评分模型给对的论文标分支，算分时每个分支各算找得全不全。

文件的样子（标题之外三节；需求那一节里可以有自己的二级标题，按这三个节名切）：

    # 专 1：……
    - 类型：专
    - 综述：W4412520891        （可选：有就截断到它的发表日、把它挡在池外，参考文献进待判池）

    ## 需求
    ……
    ## 判对标准
    ……
    ## 分支                     （平行、串行才有：每行「- 标签：说明」）
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

KINDS = ("专", "广", "平行", "串行")
SECTIONS = ("需求", "判对标准", "分支")


@dataclass(frozen=True)
class Question:
    name: str                       # 文件名去掉 .md
    title: str
    kind: str
    review: str | None              # 圈定范围的综述的 W 号
    requirement: str
    rubric: str
    branches: dict[str, str]        # 标签 → 说明；专、广的题是空的


def load(path: Path) -> Question:
    text = path.read_text(encoding="utf-8")
    title = text.splitlines()[0].removeprefix("# ").strip()
    head = text.split("\n## ", 1)[0]
    kind = _field(head, "类型")
    assert kind in KINDS, f"{path}: 类型只认 {KINDS}，得到 {kind!r}"
    parts = re.split(rf"^## ({'|'.join(SECTIONS)})\s*$", text, flags=re.M)
    sections = {parts[i]: parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}
    assert sections.get("需求") and sections.get("判对标准"), (
        f"{path}: 要有「需求」「判对标准」两节")
    branches = dict(re.findall(r"^- ([^：\n]+)：(.+)$", sections.get("分支", ""), re.M))
    assert bool(branches) == (kind in ("平行", "串行")), f"{path}: 平行、串行的题要有分支，别的不要"
    return Question(path.stem, title, kind, _field(head, "综述") or None,
                    sections["需求"] + "\n", sections["判对标准"], branches)


def _field(head: str, name: str) -> str:
    m = re.search(rf"^- {name}：\s*(\S+)", head, re.M)
    return m.group(1) if m else ""
