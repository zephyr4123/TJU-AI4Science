---
title: 流水线层选型
subtitle: 逐个深读调研清单上的 workflow / pipeline 框架，决定 demo 的流水线层借谁、抄谁、不碰谁
kind: 开源项目选型（代码级，只读不跑）
date: 2026-09-09
scope: 候选来自 landscape/2026-0908-auto-research-agents/references.md 的"流水线层"表；每个项目克隆到 vendor/ 下读源码，一个项目一篇深读；本页只放横向对比与当前结论
status: 进行中，已评 1 / 10
---

> **当前结论**（2026-09-09，只评了 InternAgent）：流水线层不直接采用现成框架当底座，自己写一个薄的编排层，把候选项目当契约来源与零件供应商。这个结论会随着后续深读修正。

## 为什么先做这一层

五层框架（底座 coding agent → 流水线 → skills + 工具 → 验证 → 评测）里，流水线层决定了其余四层怎么接：底座以什么协议被调用、任务以什么形态输入、结果以什么格式出来给验证层。先把这一层的契约定下来，demo 的其他部分才有地方落。

## 候选清单

来自[行业调研的流水线层台账](../../landscape/2026-0908-auto-research-agents/references.md#流水线层)。评估顺序按"对接 coding agent 的成熟度"排，先看已经在用 CLI 底座跑实验的。

| 项目 | 机构 | 深读 | 状态 |
|---|---|---|---|
| InternAgent | 上海 AI Lab · InternScience | [internagent.md](internagent.md) | 已评 |
| AutoResearchClaw | UNC aiming-lab | — | 待评（下一个） |
| AI Scientist v2 | Sakana AI | — | 待评 |
| Denario + cmbagent | AstroPilot-AI / CMBAgents | — | 待评 |
| OpenEvolve | algorithmicsuperintelligence | — | 待评 |
| MLEvolve | InternScience | — | 待评（InternAgent 的算法优化子系统，可能合并评） |
| DrClaw | InternScience | — | 待评 |
| Agent Laboratory | JHU | — | 待评（2025 年前整体式，低优先） |
| AI-Researcher | 港大 HKUDS | — | 待评（同上） |

## 横向对比

维度说明：**底座对接**看它怎么调 coding agent（SDK / CLI / 自带 agent），有没有抽象层，加一个新底座要多少行；**编排抽象**看阶段顺序是配置还是代码；**任务契约**看接一个新任务要几个文件、契约是否机器可查；**可运行**看依赖是否干净、macOS 能否装、默认配置是否开箱即坏；**代码健康**看测试、CI、死代码、异常处理。

| 项目 | 底座对接 | 编排抽象 | 任务契约 | 可运行 | 代码健康 | 结论 |
|---|---|---|---|---|---|---|
| InternAgent | 弱：三个后端只有 claudecode 真能跑，`subprocess.run` 一层，无流式、无超时、无抽象基类 | 无：外层 for 循环 + 内层硬编码状态机 | 好：`prompt.json` + `code/` + `launcher.sh` + `run_0/final_info.json`，四五个文件接一个任务 | 差：pip freeze 依赖、macOS 装不下、六处开箱即坏 | 差：零测试零 CI，24 条已确认缺陷 | 抄契约与三块零件，不当底座 |
| AutoResearchClaw | | | | | | |
| AI Scientist v2 | | | | | | |
| Denario + cmbagent | | | | | | |
| OpenEvolve | | | | | | |

## 目前能定下来的

评完一个就能定的事，先定；后续深读如果推翻，改这里并记 CHANGELOG。

1. **任务目录契约采用 InternAgent 的形态**：`prompt.json` + `code/` + `launcher.sh` + `run_0/final_info.json` + `run_N/` 快照。要补两处它没做对的：`final_info.json` 强 schema 校验、指标带 `optimization_direction` 且主路径真正读它。
2. **底座对接层自己写**：一个 `Runner` 协议（`run(prompt, cwd, timeout) → {events, exit_code, cost}`），用各 CLI 的非交互 + 结构化输出模式取证，每个 CLI 一个适配器。InternAgent 这一层没有可复用的代码。
3. **实验执行循环参考 InternAgent 重写**：拷快照 → agent 改代码 → `bash launcher.sh` → 失败截断 `traceback.log` 回喂 → 有限次重试。加超时、去掉字符串判据。
4. **经验记忆闭环候选**：InternAgent 的 `TaskMemoryLayer` + `HybridRetriever` 是目前见到工程完成度最高的实现，等验证层设计时再决定是否吸收。

## 目录

```
selection/2026-0909-pipeline-frameworks/
├── README.md          本页：候选清单、横向对比、当前结论
├── internagent.md     InternAgent-1.5 代码级深读
├── <下一个>.md
└── assets/
```

每篇深读的纪律：克隆到外层仓 `vendor/`（gitignore 挡住，不进版本库）；只读代码不跑、不装依赖；每条结论带 `文件:行`；"跑不起来"的判断标明是静态推断还是实测。
