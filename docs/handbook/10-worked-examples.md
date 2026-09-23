# 10 三轮演练与一次文档盘点

前九章的做法不是先想好再执行的，是这几件真事里踩出来的。每件事按「目的 / 怎么派 / 撞到什么 / 沉淀在哪 / 用了哪几章」写。案例卡里有全部细节（时间线、对话、账本），这里只讲做法。

## 第零轮：Claude 扮小白跑 PINNs（[#115](https://github.com/zephyr4123/TJU-AI4Science/issues/115) [#116](https://github.com/zephyr4123/TJU-AI4Science/issues/116) [#117](https://github.com/zephyr4123/TJU-AI4Science/issues/117)）

- **目的**：平台第一次让「不是作者的人」用。没有外人，就让 agent 扮一个不会命令行的研究者，在外层 `materials/` 下的工作区里从需求走到设计基线。
- **怎么派**：派活里写明扮谁（「你是一个只会说『听你的』的研究者」）、走哪条流程、撞到坑先记不绕。
- **撞到什么**：没有「停作业」的命令；设计阶段 ruff 能自动修的格式问题让执行层白跑一轮；研究者没有 Python 环境时清单不完整。纯 CPU 太慢，停下等 GPU。
- **沉淀**：三条 issue 各修根因（`ai4sci job stop`、先 `--fix` 再判、校验 `requirements.lock` 完整并给「按包名算完整清单」的命令）；纲领 P-23「算力归人」由此立项（[#119](https://github.com/zephyr4123/TJU-AI4Science/issues/119)）。
- **用了**：[02](02-brief-an-agent.md)（用户是谁写进派活）、[04](04-evidence-not-claims.md)（每个坑修根因）、[01](01-issue-driven.md)（一坑一条 issue）。

## 第一轮：复现 GUA 论文（[#120](https://github.com/zephyr4123/TJU-AI4Science/issues/120)，2026-09-21）

- **目的**：论文复现流全链跑通——复现 ≠ 改进，两条流程。研究者只丢一个链接、说「听你的」「我不会命令行」。
- **怎么派**：研究助理与执行层都是 Claude Code；GPU 是租的机器（P-23，按人的 `computes.yaml`）；验收是研究者签两次字（需求、验收），复现性分析与论文值并排。
- **撞到什么**：租来的机器上装隔离环境两小时没完——改为用镜像自带的环境（`env use`）；`env add` 往现成环境补包由此而来（[#118](https://github.com/zephyr4123/TJU-AI4Science/issues/118)）。
- **沉淀**：案例卡 [`docs/cases/gua-pinn-reproduction/`](../cases/gua-pinn-reproduction/README.md)；公开记录页 `research/evals/2026-0921-gua-reproduction/`；纲领 P-24 论文复现。
- **用了**：[05](05-search-before-answer.md)（助理自己找公开代码与数据，用自带的联网工具）、[07](07-docs-are-context.md)（案例卡记「复跑怎么接」）。

## 第二轮：两层都换成 Codex（[#135](https://github.com/zephyr4123/TJU-AI4Science/issues/135)，2026-09-22）

- **目的**：验证「涉及 agent 的一律可替换」不是口号：研究助理与执行层都换成 Codex，跑参数拟合课题的研究流全链。
- **怎么派**：Claude 扮水平一般的研究者，9 句话、两次签字；Codex 适配器（[#131](https://github.com/zephyr4123/TJU-AI4Science/issues/131)）flag 按官方文档对账、真 CLI 冒烟测试。
- **撞到什么**：七个坑（案例卡里逐条），都是适配器与提示词在另一家 CLI 上的差异；每个修根因，不在 prompt 里打补丁。
- **沉淀**：案例卡 [`docs/cases/boehm-codex-drill/`](../cases/boehm-codex-drill/README.md)（含 token 数与花费）；纲领 P-25 底座归人，母 issue [#130](https://github.com/zephyr4123/TJU-AI4Science/issues/130)。
- **用了**：[05](05-search-before-answer.md)（按官方文档对账）、[08](08-refactor-clean.md)（环境变量退役，只从 `agents.yaml` 读）、[01](01-issue-driven.md)（umbrella + sub-issue）。

## 第三轮：Codex 在项目层与新页面上复现 GUA（[#137](https://github.com/zephyr4123/TJU-AI4Science/issues/137)，2026-09-22 夜）

- **目的**：项目层（[#136](https://github.com/zephyr4123/TJU-AI4Science/issues/136)）落地后，在网页那只对话框里把 #120 那篇论文再复现一遍，换新机器。
- **怎么派**：同上，但入口是页面而不是 CLI；派活里写「每个坑当真用户会撞的修根因」。
- **撞到什么**：四个坑——σ 算错（执行层自己写 `sigma.json`）、复现的种子不照论文、探测缺解释器路径、页面四处不对。凌晨四点没跑到底，决定「结果就这样」收口。
- **沉淀**：案例卡 [`docs/cases/gua-codex-drill/`](../cases/gua-codex-drill/README.md)：时间线、与 #120 那轮并排、四个坑与修法、留着的债（写清楚没做的）、复跑怎么接。
- **用了**：[04](04-evidence-not-claims.md)（先找到出错的那一行再改）、[08](08-refactor-clean.md)（σ 改由框架算而不是叮嘱执行层）、[07](07-docs-are-context.md)（债写进案例卡而不是留在口头）。

## 文档盘点到 1.0.0（[#140](https://github.com/zephyr4123/TJU-AI4Science/issues/140) → [#141](https://github.com/zephyr4123/TJU-AI4Science/issues/141) → [#142](https://github.com/zephyr4123/TJU-AI4Science/issues/142)，2026-09-23）

- **目的**：三轮演练之后原则冻结，要让别人来接手；文档必须和代码一致。
- **怎么派**：先派读者盘全部文档（[06](06-survey-before-acting.md)），回来逐条核；派活明说「不要为了改而改，结构好就只改内容；规矩分层放；主要做减法；这一轮探出来的全在这一轮修干净」。
- **撞到什么**：文档说有的功能没了、路径变了；顺带盘出真 bug（助理会话里能替人确认、助理的本子算进产出 hash）；草稿里一句「删掉 `domains/` 测试照过」是错的，核对时抓回来。
- **沉淀**：两仓 `CLAUDE.md` 装下纲领、各层 README 装细则（#140）；两仓 README 做成地图（#141）；`CONTRIBUTING.md`、分支模型、ruleset、`-rc.N`、内仓转公开（#142）；本手册（[#145](https://github.com/zephyr4123/TJU-AI4Science/issues/145)）。写手册当天又从 PR 门禁上抓到 CI 已经红了三次没人看见（[#144](https://github.com/zephyr4123/TJU-AI4Science/issues/144)）。
- **用了**：全部九章。

## 共同的形状

四件事的做法是一样的：**先写清用户是谁与验收是什么 → 让 agent 干、人只签字 → 撞到的每个坑先取证再修根因 → 坑、债、决定当天写进 issue 与案例卡 → 下一轮从上一轮的案例卡接。** 演练不是测试，是产品需求的来源；文档盘点不是打扫，是让下一个人（与下一个 agent）能接手的前提。
