---
name: project-history
description: 项目从 2026-09-08 到现在的演进脉络与几次关键转向，读懂「为什么现在长这样」
metadata:
  node_type: memory
  type: project
  originSessionId: ecc4450e-06d2-447c-a0b1-2ca7efce5ea9
  modified: 2026-10-12T07:02:05.333Z
---

一个月从零到 1.9.0（内仓 472 个提交、外层 249 个，2026-09-08 → 10-11）。节奏是每天几十个提交、一天发好几版。

1. **调研与定调（09-08 ~ 09-10）**：nested-git 拓扑落地；深读 InternAgent、autoresearch、AutoResearchClaw 三个开源项目后定下两条：底座用现成 coding agent、评审上下文隔离。纲领从「三箱」改成「四层」，加了协调层（人 + 助理），框架不做编排。内仓定栈 Python，第一个端口 `Runner` + Claude Code 适配器靠 spike 实测定隔离位。实验内环（棘轮、账本、六类失败、笔记）先做出来。
2. **真任务与页面（09-15 ~ 09-17）**：能力描述符、分析、验证；第一个真任务 boehm-nll（学长案例）跑出第一个 keep；协调 agent 服务化（`Chat` 端口、SSE），页面第一版。v0.2.0。
3. **原则密集期（09-17 ~ 09-23）**：P-13 到 P-25 几乎一天一条，大多由演练撞出来——工作区即边界、造流程与用流程分权、阶段/能力/实现三层、需求是根、skill 系统、算力归人（SSH、AutoDL）、论文复现另一条流程、底座归人（Codex 适配器）、项目层。三轮真任务演练。用词清洗（「房间」「裁判」「按钮」「便条」全部换成直白工程词）。09-23 文档全面对齐代码（#140），发 1.0.0，立分支模型与冻结契约。
4. **能力扩张（10-01 ~ 10-05）**：能力按项目装载（P-26），从三个整合包收录 200 个社区 skill；10-01 定「内测期例外」，内测期不兼容也走 MINOR。文献检索（OpenAlex + Crossref + arXiv + Europe PMC 多跳）与精读，配套一套评测；出厂流程加 literature-survey；进度面板。
5. **装得上（10-06 ~ 10-08）**：前端改名 AAAI4S；平台的家收进 `~/.ai4sci`；供应商切换（DeepSeek、Kimi……），key 进 `keys.yaml`；一行命令全程国内源（1.8.0）；Windows 原生（一下午经 SSH 操作真机做完）；Tauri 桌面 App（1.9.0）；本机服务查请求来源（安全）、进程树不留孤儿；助理指南做减法（#287：能力自带 `assistant.md`、流程自带 `guide`、`show cap` 按需读），用 `guide_replay.py` 回放验收。
6. **对外（10-10 ~）**：官网 aaai4s.zephyrxiang.com 单独开仓 `site/`；10-11 接入 skills-scaffolding 3.0（红线 + `.memory/`）。

反复出现的模式：真任务演练撞坑 → 修根因并补机器判据 → 回写纲领 → 文档对齐代码。

**Why:** 很多现状只有放回历史里才说得通（例如为什么有项目层、为什么 key 不走环境变量、为什么指南这么短）。
**How to apply:** 想动某个设计前，先 `git log --grep '#<issue>'` 或看纲领变更记录找当时的理由；演练类工作照上面的循环收尾。相关：[[project-status]] [[drill-lessons]]
