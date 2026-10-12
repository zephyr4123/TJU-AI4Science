---
name: report-page-workflow
description: 阶段汇报页怎么做：放哪、主人对内容的口径、图与视频怎么上 CDN、怎么上 Pages，以及两个会卡住的坑
metadata:
  node_type: memory
  type: project
  originSessionId: ecc4450e-06d2-447c-a0b1-2ca7efce5ea9
  modified: 2026-10-12T07:49:02.239Z
---

阶段汇报是一份手写的单文件 HTML，放 `research/reports/<日期>-<名>.html`，发布到 Pages 后主人对着页面讲。样式沿用上一份（整块 CSS 照搬），已有两份：2026-09-23、2026-10-12。

**内容口径**（主人 2026-10-12 定）：
- 只讲做完的；没做完的统一放「下一步」，小 bug 不够格当下一步
- 不署名、不写分工、不出现人名
- 数据要细：每个版本带多少提交、带了什么，列表给出来
- 说法只按有证据的写：单价的价差不写成「实测省了多少」，验收只列有记录的项
- 视频用 mp4（静音循环），不用 GIF

**图与视频不进仓**：转成 jpg / mp4、起英文名，放 `materials/reports/<名>/out/`，跑 `scripts/reports/upload.py <名>` 传 COS，把打印出来的 CDN 地址填进 HTML。

**两个坑**：
- CDN 的防盗链白名单不含 `github.io`，但放行空来源：页面 `<head>` 里加 `<meta name="referrer" content="no-referrer">`，否则 Pages 上图和视频全 403（本地预览看不出来）
- Pages 的部署环境只放行 `main`：汇报页单独 PR 进 `main`（不打 tag、不算发版），合完把 `main` 合回当前的 `release/X.Y`；CHANGELOG 的 Unreleased 两边都加了行会冲突，两边都留

**要跑很久的界面怎么录**（进度面板这类）：拿本机留档的一次真实运行，用 Playwright 拦读接口加虚拟时钟做倍速回放，不改任何文件；服务起在不带 key 的临时家目录上。演示数据在 `materials/home/projects/progress-demo`，回放与拼页面的脚本在 `materials/reports/2026-1012-progress/tools/`（本机，不进 git）。页面里要写明是回放。

**Why:** 汇报每隔几周一次，流程里几处（Pages 只认 main、防盗链、长任务没法现场跑）每次都会重新撞一遍。
**How to apply:** 接到「写汇报」先用 git 与 GitHub 统计数据、列出要讲的再对齐，不直接动笔；统计代码行时剔除 `skills-curated/` 与锁文件（收录的 skill 原文有几十万行）。相关：[[project-status]] [[release-and-distribution]] [[feedback-memory-scope]]
