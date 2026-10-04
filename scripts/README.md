# scripts/ 外部脚本与一次性工具

**防火墙：内仓的生产代码禁止依赖这里的任何文件。** 脚本一旦被生产用到，就迁进内仓正式维护。

| 目录 | 放什么 |
|---|---|
| `external/` | 第三方拿来的脚本，每个带 `SOURCE.md` 记来源、版本与许可 |
| `oneoff/` | 一次性的数据处理、爬取、转换 |
| `articles/` | 对外文章的出图脚本，一篇一个目录，与 `docs/articles/` 同名；图的出处写在那篇的 `sources.md` |
| `evals/` | 给平台的步骤做实测的脚本（依赖内仓代码、用内仓 venv 跑，内仓不依赖它们）。文献检索的评测：`literature_recall.py` 照一道题跑一次检索，`literature_judge.py` 用评分模型照题里的判对标准判对不对、打三个分，`literature_rescreen.py` 只改筛选时重放每跳的筛选；八道题（专、广、平行、串行各两道）在 `literature_questions/`，`literature_question.py` 读（[#215](https://github.com/zephyr4123/TJU-AI4Science/issues/215) [#218](https://github.com/zephyr4123/TJU-AI4Science/issues/218) [#219](https://github.com/zephyr4123/TJU-AI4Science/issues/219)，流程见 `docs/specs/literature-search.md` §6、命令见 §12） |

仓库自身的工具脚本（changelog、release、hygiene、md2html）在 `.github/scripts/`，不在这里。
