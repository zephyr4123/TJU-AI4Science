---
name: team-roles
description: 谁在做这个项目、各自什么角色与约束，派活与写文档时怎么对待他们
metadata:
  node_type: memory
  type: project
  originSessionId: ecc4450e-06d2-447c-a0b1-2ca7efce5ea9
  modified: 2026-10-12T02:59:51.842Z
---

- **黄素翔（主人，GitHub zephyr4123）**：唯一维护者与发版人，拍板纲领与决策；兜底一切要机器、账号、secrets 的活。文档里「主人」就是指这位。
- **桓梓峻**：同届工程师，分工草案里排在主线（内测、扩能力与流程、onboarding）。
- **李瑞彬**：博士、理论方向；顾问与真实用户，只做调研与提案、不派工程活。2026-09-27 交回科研 AI 能力调研（#151），促成收录社区 skill 的决定。
- **田建隆**：本科生，不设 DDL、不要求产出，给开放的探索题（评测 benchmark、开源 agent 适配器 spike），产出是调研或 spike 记录而非合进 main 的代码。
- 案例来源的「学长」是提供真实课题与访谈的外部研究者。

实际节奏仍是主人 + Claude 单线高频推进（一天能发好几个版本）。分工草案里打算移交的活，最后多半是主人 + Claude 自己做完的，例如 Windows 适配（原定移交，2026-10-07 一个下午经 SSH 操作真机做完，随 1.8.0 发布）。GitHub ruleset 的一人 review 由管理员绕过。

**Why:** 分工草案（`docs/meetings/2026-0923-division-of-labor.md`）写着约束；派活、写 issue、估工期时要按人的身份收放。
**How to apply:** 给非主人的人开 issue 要写清边界、入口文件、验收；涉及 secrets、发版、服务器的活默认归主人；不要把探索题写成有 DDL 的工程任务。相关：[[project-status]]
