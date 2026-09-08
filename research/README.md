# research/ 调研

课题组的知识资产。结论进 git；原始产物（PDF、数据集、原始导出）不进 git，放 LFS 或 NAS，这里只放索引与来源链接。

**这个目录是公开区。** main 上的每次变动都会把这里全部 `.md` 渲染成 html 并整体发布到 <https://zephyr4123.github.io/TJU-AI4Science/>，新加一篇调研不用碰任何配置；不想公开的材料不要放进来。

## 目录

| 目录 | 放什么 |
|---|---|
| `landscape/` | 同类系统、开源项目与行业现状调研 |
| `selection/` | 开源项目选型深读：一轮选型一目录，`README.md` 做横向对比，每个候选项目一个 md |
| `literature/` | 文献综述，按主题一目录，附 `refs.bib` |
| `domain/` | 课题组学科的领域知识 |
| `evals/` | 方案评测、benchmark 结论 |

## 一篇调研长什么样

一篇调研一个目录，目录名 `YYYY-MMDD-slug`，天然按时间排：

```
landscape/2026-0908-auto-research-agents/
├── README.md        正文，唯一原始稿。开头是 YAML 元数据（title / subtitle / kind / date / scope / status）
├── references.md    文献与项目台账：类型、机构、链接、一句话、正文位置
├── index.html       由 README.md 生成的阅读版，随 md 一起提交
└── assets/          图
```

选型类目录（`selection/`）允许一个目录里多个 md：`README.md` 放候选清单、横向对比与当前结论，每个候选项目一个 `<slug>.md` 深读，都会各自渲染成 html。

写法上的两条规则，让文献和内容真正连起来：

1. 项目、论文、基准的名字在**每一节首次出现处**链接到正文里它自己的条目（`#锚点`），条目里放全部外链，并写一行"被引用：§x、§y"作为回跳。
2. 具体数字与判断用脚注 `[^id]` 挂到来源；脚注在文末自动汇成参考列表，阅读版里可回跳正文。

## 生成阅读版

```bash
make html          # research/*/*/README.md → 同目录 index.html；文内链接与脚注不能落地会直接报错
make check         # 含 html-check：index.html 落后于 README.md 时门禁不过
```

md 是原始稿，html 是构建产物；本地 `make html` 生成并随 md 提交（离线可读），`.github/workflows/pages.yml` 在 main 更新时重新渲染并发布到 GitHub Pages。视觉层遵守 `artifact-design` 的规范（阅读列宽、层级、明暗主题、表格可横向滚动、脚注回跳），模板在 `.github/scripts/md2html/template.html`。

`.venv/bin/python .github/scripts/md2html/md2html.py backrefs <README.md>` 能打印每个标题被哪些章节链接到，写"被引用"行时用。

## 调研索引

| 日期 | 标题 | 状态 | 原稿 | 公网阅读版 |
|---|---|---|---|---|
| 2026-09-08 | 新工科自动化科研智能体：2026 年工业界现状与架构设计 | 第一版 | [README](landscape/2026-0908-auto-research-agents/README.md) | <https://zephyr4123.github.io/TJU-AI4Science/landscape/2026-0908-auto-research-agents/> |
| 2026-09-09 | 流水线层选型（已评 InternAgent，代码级深读） | 进行中 | [README](selection/2026-0909-pipeline-frameworks/README.md) · [InternAgent](selection/2026-0909-pipeline-frameworks/internagent.md) | <https://zephyr4123.github.io/TJU-AI4Science/selection/2026-0909-pipeline-frameworks/> |
