---
name: drill-lessons
description: 真任务演练怎么做、到目前为止反复撞到的几类坑，以及从中得出的可复用判断
metadata:
  node_type: memory
  type: project
  originSessionId: ecc4450e-06d2-447c-a0b1-2ca7efce5ea9
  modified: 2026-10-12T03:04:20.131Z
---

**演练是产品需求的主要来源，不是测试。** 一共做过这些：第零轮 PINNs（Claude 扮研究者）、#120 GUA 论文复现（Claude Code 两层，已验收，约 $10.4，研究者 8 句话两次签字）、#135 boehm 研究流（Codex 两层，已验收，7 个坑里 5 个出在 Codex 适配器）、#137 GUA 再复现（Codex + 项目层页面，没跑到底）、#210 Windows 真机端到端（经 SSH，加隧道跑 Playwright）、#287 指南减法的冻结决策点回放。
固定做法：写清扮谁、验收是什么 → agent 干、人只签字 → 每个坑先取证再修根因 → 当天写进 issue 与案例卡（时间线、坑与修法、留着的债、复跑怎么接）→ 下一轮从上一张卡接着跑。

反复出现的几类坑与对应判断：
- **执行层会编，只信框架算的。** 执行层自报「已验证」、自己写 σ、编论文里的方程名。改法都是把这件事从执行层手里拿走，交给零模型代码（σ 由框架算、改了什么只信前后快照 diff），而不是在 prompt 里多叮嘱一句。
- **隔离要实测，看参数不算数。** Claude Code 的自动记忆不归设置源管，执行层会话一直带着开发者的 MEMORY.md（#222，一次会话多花三成）；Codex 的个人 skill 在私有 home 下照样被扫进来。接任何 CLI 都要拿探针真跑一次。
- **租来的 GPU 用镜像自带的环境。** 在 AutoDL 这类机器上隔离新建环境，两小时都装不完；`env use` 用现成的，缺包再 `env add`。瓶颈在 Python 循环的代码，租更贵的卡也没用。
- **单测全绿之后，端到端还会撞出 Mac 上本来就有的 bug。** Windows 那次单测全绿后，端到端又撞出 6 个问题，其中 2 个 Mac 上也有、早已在发布的包里。页面与安装改动一定要在真服务、真装出来的包上走一遍。
- **预筛过的好材料掩盖了复现里最常见的坑。** 数据链接失效、README 里的命令跑不起来、权重与测试集重叠，这几类还没真正考过。

**Why:** 这几条决定了下一轮演练怎么设计、坑该修在哪一层；不知道的话容易又在 prompt 里打补丁。
**How to apply:** 新演练照固定做法走，案例卡写进 `docs/cases/`（索引在 `docs/cases/README.md`，原件放 `materials/`）；评估「怎么修」时优先把判断挪进框架或补机器判据。做法的展开在 `docs/handbook/10-worked-examples.md`。相关：[[project-history]] [[agent-cli-integration]]
