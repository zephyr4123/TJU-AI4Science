---
name: project-status
description: 截至 2026-10-12 的进展：发到哪一版、总目标、能做什么不能做什么、手上悬着的活与待拍板的决策
metadata:
  node_type: memory
  type: project
  originSessionId: ecc4450e-06d2-447c-a0b1-2ca7efce5ea9
  modified: 2026-10-12T07:02:04.139Z
---

**版本**（2026-10-11）：产品 platform v1.9.0（10-08，桌面 App 首发）；外层文档 v1.9.0。三个仓当前分支：外层 `release/1.10`、内仓 `release/1.10`、官网 `main`。milestone `platform 1.10.0` 已开但还是空的。官网 10-10 上线，独立发版。

**总目标**（主人 2026-10-12 定）：端到端跑通「一句话（一个 idea）→ 一篇论文」。接下来的工作由它牵引，界面与各处细节的完善从它派生；怎么拆成具体的活主人还在想，1.10 的内容等这一步。

**能做的**：页面上一个项目一位助理；出厂流程三条（research 改进、reproduce 论文复现、literature-survey 文献调研）；八个步骤（文献检索/精读、设计、原码复现、AutoResearch、分析、复现性分析、数字核对）+ 2 个平台自带 skill + 200 个收录 skill；Claude Code / Codex × 官方登录、DeepSeek、Kimi 等供应商；本机或 SSH 算力；Mac / Linux / Windows 一行命令装，Mac / Windows 桌面 App。

**还不能做的**（`docs/vision.md`「今天离它多远」）：假设、写作两个阶段没有步骤；文献综述缺口（#154，候选都不合格，要不要自己写没定）；验证只有数字回溯与账本对账，引用真伪、图源、模型评审都没有；收的形状仍窄（几分钟到几小时跑完的代码加一个数）；除团队外没有外部真用户。

**悬着的活**：
- **CDN 证书 2026-11-22 到期，不续的话 2026-10-23 起发版流水线直接失败**（见 [[release-and-distribution]]）
- #273 文献检索在 Claude Code + DeepSeek V4.1 Flash 上的八题评测：10-07 定了 high、low 两条线各 32 次，只跑了两次冒烟（`materials/evals/literature/runs273/`）；修评测脚本的提交只在本地分支 `feat/273-lit-eval-deepseek`，还没推
- P1 bug：#290 供应商余额不足（402）时那一轮被记成完成，页面直接显示英文报错；#278 流程实例里写的能力参数 `with` 能通过校验、页面也显示，跑的时候却没用上（需拍板语义）
- 待拍板：#288 作业中断后产出一直显示「运行中」；#126 失败的下游该不该冻住上游；#125 AutoResearch 棘轮丢掉「方向对但没过门」的小改进；纲领未决 Q-3 验收（#10）、Q-4 评测（#11）、Q-7 无人值守通知、Q-12 写作形态（#32）、Q-14 声明式能力

**Why:** 新会话第一件事是知道站在哪、下一步候选是什么；issue 列表太散，这里给压缩视图。
**How to apply:** 动手前用 `gh issue list` 与 `./repos status` 核对这里是否过时，过时先改这条记忆；发版、关大 issue、开新 milestone 后更新这条。相关：[[project-history]] [[literature-search]] [[report-page-workflow]]
