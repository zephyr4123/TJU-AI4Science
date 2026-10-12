---
name: architecture-model
description: 平台的架构心智模型：四层、项目/工作区/阶段/产出、能力两种 tag、流程与断点、冻结、端口与适配器
metadata:
  node_type: memory
  type: project
  originSessionId: ecc4450e-06d2-447c-a0b1-2ca7efce5ea9
  modified: 2026-10-12T02:59:29.784Z
---

**四层**：协调层（人 + 助理，科研判断）→ 框架（零模型的诚实执行基底：开门、开产出目录、封评分脚本、跑内环、记账、判冻结与签字）→ 执行层（每次新开的 coding agent 会话，唯一写代码的，面前只有 `ai4sci skill`）→ skill 脚本（确定性工具）。框架没有「下一步」：每条 `ai4sci` 子命令只跑一个能力就退出，串起来的是助理。

**盘上的形状**（平台的家 `~/.ai4sci/projects/<p>/`）：项目 = 一位助理 = 一个课题；工作区 = 一份需求（`requirement.md` + 人确认的 `requirement.lock`，唯一内置的门）；七个阶段各一个目录，每次产出一个 `<stage>/<n>/`，`meta.yaml` 用 `from`（带 tree hash）记读了谁。被引用或被签（`signed.json`）就冻结。进度从 meta 现算，没有进度文件。

**能力两种 tag**：步骤（`ai4sci cap`，框架起执行层、开产出、能签；现有 8 个：literature-search/read、design、reproduction、auto-research、analysis、reproducibility、verify）与 skill（`ai4sci skill run`，不开产出）。skill 三处库：`skills/` 平台自带常驻、`skills-curated/` 收录的社区 skill、`domains/*/skills/`；按项目装载（只装流程实例上挂的 + 常驻）。

**流程**：阶段序列 + 每格挂的能力 + 断点（人签字下游才能读）。出厂流程只读（research、reproduce、literature-survey）；编辑台流程助理存到 `studio/workflows/`；项目里研究助理 `flow take` 取实例。两位助理分权靠可写目录与命令前缀，不靠 prompt 里的「请不要」。

**可替换**：`backends/`（`Runner` 执行层一次会话、`Chat` 协调层多轮）与 `compute/`（local、ssh）是端口，各家一个适配器文件、显式字典选；页面是 `ai4sci serve` 端点的客户端，桌面 App 是给页面套的窗口。

**Why:** 架构细节散在纲领 P-1~P-27、workflow.md 与 framework/README，开工前需要一张总图判断改动落在哪层、碰哪条原则。
**How to apply:** 改动前先定位层；凡是「让框架判断科研」「让模型给自己打分」「加注册表」「默认读最新」都是越界信号。细则：`docs/architecture/README.md`（P-n 带机器判据）、`docs/architecture/workflow.md`（词表 §5）、`platform/framework/README.md`（分层与依赖方向）。相关：[[product-thesis]] [[tech-stack]]
