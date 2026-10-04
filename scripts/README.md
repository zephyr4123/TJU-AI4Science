# scripts/ 外部脚本与一次性工具

**防火墙：内仓的生产代码禁止依赖这里的任何文件。** 脚本一旦被生产用到，就迁进内仓正式维护。

| 目录 | 放什么 |
|---|---|
| `external/` | 第三方拿来的脚本，每个带 `SOURCE.md` 记来源、版本与许可 |
| `oneoff/` | 一次性的数据处理、爬取、转换 |
| `articles/` | 对外文章的出图脚本，一篇一个目录，与 `docs/articles/` 同名；图的出处写在那篇的 `sources.md` |
| `evals/` | 给平台的步骤做实测的脚本（依赖内仓代码、用内仓 venv 跑，内仓不依赖它们）。文献检索的评测分两步：`literature_recall.py` 照一道题跑一次检索，`literature_judge.py` 用评分模型判对不对、打三个分；三道题的需求原文在 `literature_questions/`（[#212](https://github.com/zephyr4123/TJU-AI4Science/issues/212) [#215](https://github.com/zephyr4123/TJU-AI4Science/issues/215)，流程与基线见 `docs/specs/literature-search.md` §6 §7） |

仓库自身的工具脚本（changelog、release、hygiene、md2html）在 `.github/scripts/`，不在这里。
