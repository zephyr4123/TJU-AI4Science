---
title: 流水线层选型
subtitle: 逐个深读调研清单上的 workflow / pipeline 框架，决定 demo 的流水线层借谁、抄谁、不碰谁
kind: 开源项目选型（代码级，只读不跑）
date: 2026-09-09
scope: 候选来自 landscape/2026-0908-auto-research-agents/references.md 的"流水线层"表，外加用户点名的底座层项目 autoresearch；每个项目克隆到 vendor/ 下读源码，一个项目一篇深读；本页只放横向对比与当前结论
status: 进行中，已评 3 / 11
---

> **当前结论**（2026-09-09，已评 InternAgent、autoresearch、AutoResearchClaw）：流水线层不直接采用现成框架当底座，自己写一个薄的编排层；三个候选各出一半零件：InternAgent 的任务目录形态与执行循环、autoresearch 的棘轮与实验床契约、AutoResearchClaw 的 manifest / rubric / requirements 契约与验证层部件。三个仓共同证实了一件事：编排形态都是"外层 for + 硬编码状态判断"，差别全在循环之外用什么承载状态、用什么规则收敛、用什么机器判据卡住模型造假。这个结论会随着后续深读修正。

## 为什么先做这一层

五层框架（底座 coding agent → 流水线 → skills + 工具 → 验证 → 评测）里，流水线层决定了其余四层怎么接：底座以什么协议被调用、任务以什么形态输入、结果以什么格式出来给验证层。先把这一层的契约定下来，demo 的其他部分才有地方落。

## 候选清单

来自[行业调研的流水线层台账](../../landscape/2026-0908-auto-research-agents/references.md#流水线层)，外加 autoresearch（台账里在底座与循环层，用户点名一起评，因为它的循环形态正是流水线层要回答的问题）。

| 项目 | 机构 | 深读 | 状态 |
|---|---|---|---|
| InternAgent | 上海 AI Lab · InternScience | [internagent.md](internagent.md) | 已评 |
| autoresearch | Karpathy | [autoresearch.md](autoresearch.md) | 已评 |
| AutoResearchClaw | UNC aiming-lab | [autoresearchclaw.md](autoresearchclaw.md) | 已评 |
| AI Scientist v2 | Sakana AI | — | 待评（下一个） |
| Denario + cmbagent | AstroPilot-AI / CMBAgents | — | 待评 |
| OpenEvolve | algorithmicsuperintelligence | — | 待评 |
| MLEvolve | InternScience | — | 待评（InternAgent 的算法优化子系统，可能合并评） |
| DrClaw | InternScience | — | 待评 |
| Agent Laboratory | JHU | — | 待评（2025 年前整体式，低优先） |
| AI-Researcher | 港大 HKUDS | — | 待评（同上） |

## 横向对比

维度说明：**底座对接**看它怎么调 coding agent（SDK / CLI / 自带 agent），有没有抽象层，加一个新底座要多少行；**编排抽象**看阶段顺序是配置还是代码；**内环**看迭代 N 到 N+1 之间传什么、靠什么收敛；**任务契约**看接一个新任务要几个文件、契约是否机器可查；**验证**看有没有零 LLM 的机器判据卡造假；**可运行**看依赖是否干净、macOS 能否装、默认配置是否开箱即坏；**代码健康**看测试、CI、死代码、异常处理。

| 项目 | 底座对接 | 编排抽象 | 内环 | 任务契约 | 验证 | 可运行 | 代码健康 | 结论 |
|---|---|---|---|---|---|---|---|---|
| InternAgent | 弱：三个后端只有 claudecode 真能跑，`subprocess.run` 一层，无 `-p`、无超时、无抽象基类 | 无：外层 for + 内层硬编码状态机 | 结果塞 prompt：全部 `final_info.json` 原样回喂，无 accept/reject | 好：`prompt.json` + `code/` + `launcher.sh` + `run_0/final_info.json` | 无 | 差：pip freeze 依赖、macOS 装不下、六处开箱即坏 | 差：零测试零 CI，24 条已确认缺陷 | 抄任务目录形态与执行循环，不当底座 |
| autoresearch | 无：一份 Markdown + 一个 shell，任何能开 shell 的 agent 都能跑；需关权限 | 无：`program.md` 里 13 行伪代码循环 | **棘轮**：git 工作树承载状态，外部单标量硬闸 accept/reject，gitignore 的账本外化失败记忆，上下文每轮只进两行 | 极简：单可变文件 + 只读评测文件 + 固定 5 分钟预算 | 无：荣誉制，裁判员就是运动员，接受阈值低于噪声 | 差：单卡 NVIDIA 硬绑定，macOS `uv sync` 过不去 | 零测试，但只有 1200 行 | 抄形态不抄代码：棘轮四件套 + 实验床契约，落在验证层与评测层 |
| AutoResearchClaw | 中：LLM 客户端厚（重试分级、fallback 链、双 wire），沙盒层有 `SandboxProtocol`；但 CLI 后端靠外部 `acpx` 透传零分支，`CodeAgentProvider` 整块零调用 | 弱：产物契约表 + 原子 checkpoint + HITL 钩子是真的；编排仍是外层 for + 7 处特判，状态机写了测了没接线 | 比结果塞 prompt 多 revert-to-best 一件事；第 N 轮看不到前 N-1 轮指标；旁边有 14 类确定性失败分类 + 3 轮修复 | 最好：ARC-Bench manifest（conditions / metrics 带 direction / requirements 带 must_pass）+ 加权 rubric 树，55 题五领域同一模板 | **有**：数字白名单对账 + 五源引用校验，零 LLM 有真测试；但硬闸包在 `except: pass` 里，REJECT 只涂黑不终止 | 中：核心依赖 4 个 macOS 装得上；默认 sandbox 无隔离；幽灵打包 | 差：8 万行，死代码过万，主循环 import 四个不存在的模块，3.9 万行测试无 CI，作者自审 7 条 P0 剩 4 | 零件按模块摘（契约、harness、验证层部件、HITL 通道），骨架不要 |
| AI Scientist v2 | | | | | | | | |
| Denario + cmbagent | | | | | | | | |
| OpenEvolve | | | | | | | | |

## 目前能定下来的

评完一个就能定的事，先定；后续深读如果推翻，改这里并记 CHANGELOG。

1. **编排层自己写，且不用状态机装饰**。三个仓的编排都是过程式 for，ARC 还多养了一套没接线的状态机误导读者。我们要么真的用状态机驱动，要么老实写 for，阶段用注册式（装饰器或 entry_points）而不是硬编码枚举。产物契约表（ARC `contracts.py` 的形状）+ 磁盘状态 + 原子 checkpoint 三件确定性设施第一批就做。
2. **任务契约两层**：声明层采用 ARC-Bench 的 manifest 形态（`research_question` / `conditions` / `metrics` 带 `direction` / `datasets` / `requirements` 带 `must_pass`）+ 加权 rubric 树；执行层采用 InternAgent 的目录形态（`code/` + `launcher.sh` + `run_0/` + `run_N/` 快照）。两处必须补：`final_info.json` 强 schema 校验，指标方向在主路径上真正被读。
3. **实验内环采用 autoresearch 的棘轮，把裁判外置**：git 工作树承载状态、runner 负责跑实验、解析指标、比较、执行 `git reset`，agent 只改代码和提交；失败记忆外化成机器可对账的账本；固定墙钟预算；统计门（重复种子 + 显著性阈值 + holdout）。ARC 的 revert-to-best 和 14 类失败分类器作为补充。
4. **评测由框架注入、模型改不了**：ARC 的 `harness_template.py` 形态（`report_metric` / `check_value` / `should_stop` / `finalize`），评测跑成独立子进程只吃产物文件；只读文件挂校验和门禁。
5. **验证层从三条零 LLM 的机器判据起步**：论文里每个数字回溯到实验产物（ARC `VerifiedRegistry` + `paper_verifier`）、每条引用在真实学术 API 里存在（ARC `literature/verify.py`）、每张图的数值来自数据（ARC `visualize.py` 思路）。fail-open 全部改成 fail-closed。
6. **底座对接层自己写**：一个 `Runner` 协议（`run(prompt, cwd, timeout) → {events, exit_code, cost}`），用各 CLI 的非交互 + 结构化输出模式取证，每个 CLI 一个适配器。ARC 的 `CodeAgentProvider` 是这层该有的形状（在它仓里是死代码，对我们反而省事）。
7. **人在环用 stage 边界暂停 + 文件通道回传**：ARC 的 `intervention.py` + `file_wait.py` + pre/post hook 签名。实验内环里的打断粒度我们自己往下切。
8. **立四条机器可查的规矩**（从 ARC 的反面清单来）：每个抽象合入时必须带真实调用点；每加一个配置项同时加一条断言证明它被读到；集成点必须有测试；不许裸 `except`。
9. **底座 coding agent 是唯一执行者**（2026-09-10 拍板）：写代码、修 bug、文献检索、假设、分析、写论文，凡是产出文件的活都交给它，一个阶段一次新会话，上下文从磁盘来（`runs/`、账本、git log）。框架不单独调 LLM 写文本，`framework/` 目录里 grep 不到模型 API。联网检索做成框架提供的确定性脚本，换底座能力不变；用户自带的调研直接当阶段输入。
10. **裁判是上下文隔离的 agent**（2026-09-10 拍板）：accept / reject、验证、评审绝不由干活的那个会话做。确定性能判的用 runner 与零 LLM 判据；需要模型判断的，由框架派一个新会话（subagent / workflow，可指定不同模型），只给产物不给轨迹。执行与决策的分界：产出文件的是执行，改变流程走向的是决策。

## 目录

```
selection/2026-0909-pipeline-frameworks/
├── README.md              本页：候选清单、横向对比、当前结论
├── internagent.md         InternAgent-1.5 代码级深读
├── autoresearch.md        autoresearch 代码级深读（含一次 H100 真实跑档与两条远端分支）
├── autoresearchclaw.md    AutoResearchClaw v0.5.0 代码级深读
├── <下一个>.md
└── assets/
```

每篇深读的纪律：克隆到外层仓 `vendor/`（gitignore 挡住，不进版本库）；只读代码不跑、不装依赖；每条结论带 `文件:行`；"跑不起来"的判断标明是静态推断还是实测；读者结论由主线程抽查后才写进正文。
