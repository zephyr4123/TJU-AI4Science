---
title: 新工科自动化科研智能体
subtitle: 2026 年工业界现状与架构设计
kind: 行业与开源现状调研
date: 2026-09-08
scope: 只收录 2026 年发布或有实质更新、且能安装能跑的开源项目；纯论文只在验证层与批评部分点名
status: 第一版
---

> **结论先行**：2026 年自动化科研的技术栈已经收敛成一个可拼装的五层结构——**底座（coding agent）→ 流水线（workflow）→ 学科适配（skills + 工具）→ 验证（单篇把关）→ 评测（框架 ablation）**。"新工科智能体"不需要从零造任何一层，需要做的是**选型、拼装、写天大各学院的 skill pack、接真实工具，以及把验证层做扎实**。
>
> 怎么读：项目名在每一节首次出现处链接到[第 8 节](#8-开源项目现状详述)的条目，条目里有仓库、论文与数据集链接，并注明被哪些节引用；具体数字与判断的来源在脚注里，脚注可回跳正文。文献与项目的完整台账见同目录的 [references.md](references.md)。

## 1. 2026 年发生了什么

2025 年之前的"AI Scientist"基本是**单个研究组的整体系统**：Sakana 的 [AI Scientist](#ai-scientist-v2)、JHU 的 Agent Laboratory、港大的 AI-Researcher，每家都自己写 agent loop、自己写实验执行、自己写论文生成，互相不兼容。它们证明了"能跑通"，但没有一个能直接拿去给另一个学科用。

2026 年上半年三件事把格局改了：

| 时间 | 事件 | 意义 |
|---|---|---|
| 2026-02-10 | 上海 AI Lab 发布 [InternAgent-1.5](#internagent)[^internagent-report] | 第一个明确宣称"统一框架、跨计算与实验学科"的开源系统，物理/生物/地球/生命科学都跑过 |
| 2026-03-07 | Karpathy 发布 [autoresearch](#karpathy-autoresearch) | 630 行代码、三个文件，一个月 66k star。证明"coding agent + 单一指标 + git 回滚"这个最小循环就能产生真实收益 |
| 2026-03-15 | UNC 发布 [AutoResearchClaw](#autoresearchclaw) | 第一个把"底座可换（5 种 CLI agent）、skills 可插、消息平台可接"做成产品形态的端到端流水线 |

同一时期，**Agent Skills（一份 SKILL.md）成了学科适配的事实标准**：[K-Dense](#k-dense-scientific-agent-skills) 的科研 skills 库从 1 月的 143 个涨到 7 月的 165 个，Google DeepMind 6 月发了官方 [science-skills](#deepmind-science-skills)，上海 AI Lab 在做 [Awesome-Scientific-Skills](#awesome-scientific-skills)。三家不约而同地把"学科知识"编码成 markdown，而不是编码成新的 agent。

评测侧，上海 AI Lab 3 月起开放 [ResearchClawBench](#researchclawbench)（40 个真实科研任务、10 个学科），Ai2 的 [AstaBench](#astabench) 4 月更新给出了最诚实的数字：最强 agent 在"从想法到代码到报告、不做任何简化"的端到端任务上只有 3% 完美完成[^astabench-update]。

批评侧，5–6 月连续出了三篇有分量的文章：《Agentic AI Scientists Are Not Built For Autonomous Scientific Discovery》[^not-built]、《Sibyl-AutoResearch：自主科研需要的是自进化试错 harness，不是论文生成器》[^sibyl]、《Autonomous Research Agents: A Survey of AI Scientists and the Verification Gap》[^verification-gap]。共同结论是：**代码开源已经很普遍，但可复现级别和能验证结论的产物仍然很少**。

把这些拼起来看，2026 年的现状就是：**"能生成论文"已经不是问题，"生成的论文可信、可复现、可评"才是问题。** 这直接决定了"新工科智能体"应该把力气花在哪一层。

## 2. 五层架构总览

```
┌──────────────────────────────────────────────────────────────────┐
│  第五层  评测（框架 ablation）                                       │
│  ResearchClawBench · AstaBench · Terminal-Bench Science · NewtonBench │
│  换 skill / 改流水线某一步 → 固定任务集上分数怎么变                    │
├──────────────────────────────────────────────────────────────────┤
│  第四层  验证（单篇把关）                                            │
│  新颖性检查 · 引用真实性 · 复现脚本 · claim→evidence 追溯 · reviewer agent │
│  · 结果选择披露                                                     │
├──────────────────────────────────────────────────────────────────┤
│  第三层  学科适配（skills + 工具）                                    │
│  SKILL.md（怎么做）  +  MCP / API / 仿真软件 / 仪器接口（能做）          │
│  K-Dense skills · DeepMind science-skills · Awesome-Scientific-Skills │
│  → 天大各学院 skill pack                                             │
├──────────────────────────────────────────────────────────────────┤
│  第二层  流水线（workflow）                                          │
│  模式 A 棘轮优化：autoresearch                                       │
│  模式 B 假设生成 → 实验 → 论文：AutoResearchClaw · InternAgent · Denario │
│  模式 C 算法进化：OpenEvolve / ShinkaEvolve                           │
├──────────────────────────────────────────────────────────────────┤
│  第一层  底座（coding agent harness）                                │
│  Claude Code · Codex CLI · Gemini CLI · Copilot CLI · Kimi CLI       │
│  （API 可换：官方 / 第三方兼容端点 / 国产模型）                          │
└──────────────────────────────────────────────────────────────────┘
```

每一层都有现成的工业级或准工业级开源项目。下面逐层说明**为什么这么分**、**用什么**、**怎么做**；各项目的详情集中在[第 8 节](#8-开源项目现状详述)。

## 3. 第一层：底座——为什么不手搓 coding agent

### 3.1 结论

**不要自己写 agent loop。** 底座就用现成的 coding agent：Claude Code、Codex CLI、Gemini CLI、GitHub Copilot CLI、Kimi CLI，或者 OpenHands 这类开源 harness。

### 3.2 为什么

**理由一：harness 的工程量远超想象，而且没有护城河。**
一个能在真实科研环境里稳定跑几小时的 coding agent，需要处理：工具调用协议、沙盒与文件系统隔离、长上下文压缩、错误恢复与重试、并发子任务、权限控制、token 预算管理。这些东西 2024–2025 年各家 AI Scientist 都各自写了一遍，2026 年回头看，全部被商用 coding agent 覆盖，而且后者的迭代速度是按周计的。自己写等于用一个人的时间去追几家公司的团队。

**理由二：2026 年的头部项目自己都这么干了。**

- [AutoResearchClaw](#autoresearchclaw) 从 v0.3.2（2026-03-22）起，把代码生成阶段（第 10、13 阶段）**委托给外部 CLI agent**，支持 Claude Code、Codex CLI、Copilot CLI、Gemini CLI、Kimi CLI 任意一个作为后端，自己只做流水线编排和预算控制。
- Karpathy 的 [autoresearch](#karpathy-autoresearch) 根本没有 agent 代码——它只有 `program.md`（给 agent 的指令）、`train.py`（agent 可改的训练脚本）、`prepare.py`（固定的数据与评估），agent 本身就是你指向仓库的 Claude Code 或 Codex。
- 上海 AI Lab 在 [InternAgent](#internagent) 之外单独做了 `cc-mini`（超轻量 harness 脚手架），说明他们也认为 harness 应该是**薄的、可替换的**，价值在上层。
- Sibyl-AutoResearch（2026-05）的核心论点就是：自主科研系统的价值在**可自进化的试错 harness**而不在论文生成器，harness 要围绕 coding agent 搭，而不是替代它[^sibyl]。

**理由三：可替换性本身是科研价值。**
底座可换意味着你可以做"同一流水线、同一 skills，换底座模型"的对照实验。这是评测层（[第 7 节](#7-第五层评测框架本身怎么评)）能成立的前提。

### 3.3 关于 API

所有主流 CLI agent 都支持自定义端点：Claude Code 通过环境变量指向兼容端点，Codex CLI 配 OpenAI 兼容 `base_url`，[AutoResearchClaw](#autoresearchclaw) 的配置文件直接就是 `base_url` + `api_key_env` + `primary_model` + `fallback_models`。技术上第三方 API 或国产模型完全可行。

两点提醒：

1. 各家 CLI 的服务条款对非官方端点态度不同，**学校立项时优先用官方 API 或国内合规模型**。[InternAgent](#internagent) 本身就是配国产模型跑的，是一个安全的参考。
2. 流水线里**不同阶段用不同模型**：文献检索和跑实验用便宜模型，想法生成、写作、评审用强模型。AutoResearchClaw 的 `fallback_models` 和 InternAgent 的分阶段配置都支持这么做，成本能差数倍。

## 4. 第二层：流水线——为什么要固定 workflow

### 4.1 结论

**不要让 coding agent 自由发挥"去做科研"，要把专家的科研流程固化成阶段。** 流水线就是把人类科学家的隐性流程显式化，每一步有输入、输出、检查点。

### 4.2 为什么

**理由一：自由端到端的成功率极低。**
[AstaBench](#astabench)（Ai2，ICLR 2026 oral）2026-04-30 的更新给出了最直接的数据：最强 agent 综合分约 53%，文献检索和代码执行还行，但在 E2E-Bench-Hard（把一个研究想法一路做到可运行代码和书面报告，不做任何简化或脚手架）上只有 **3%** 的任务被完美完成[^astabench-update]。同一份数据说明：分解后的单步能力已经可用，端到端的"自由发挥"不可用。**流水线就是把 3% 的问题拆成一串 50%+ 的问题。**

**理由二：科研有大量隐性知识，模型不知道"下一步该做什么"。**
2026-05 的《Agentic AI Scientists Are Not Built For Autonomous Scientific Discovery》指出当前系统的四个结构性缺陷：选题有偏、缺少实验室隐性知识、偏好优化导致多样性坍缩、基准只测单轮准确率而非闭环有效性[^not-built]。前两条恰恰是 workflow 能解决的——把"先查文献再定假设""先跑 baseline 再改方法""先做消融再写结论"这些顺序写死。

**理由三：可比较。**
固定流水线后，"改第 7 步的 prompt""换第 12 步的 skill"才是可控变量，才能做[第 7 节](#7-第五层评测框架本身怎么评)的 ablation。自由发挥的 agent 每次路径都不一样，没法比。

### 4.3 三种流水线模式

2026 年的项目按"研究闭环长什么样"分成三类，**新工科智能体应该三种都支持，按学科任务选**：

| 模式 | 闭环 | 代表项目 | 适合的工科任务 |
|---|---|---|---|
| **A. 棘轮优化** | 改代码 → 跑 5 分钟 → 看单一指标 → 好则 commit 坏则回滚 → 循环 | [Karpathy autoresearch](#karpathy-autoresearch) 及衍生 | 有明确数值指标、单次实验几分钟能跑完：仿真参数优化、控制器调参、材料配方筛选、算法基准提升 |
| **B. 假设 → 实验 → 论文** | 文献 → 想法 → 实验设计 → 代码 → 执行 → 分析 → 写作 → 评审 | [AutoResearchClaw](#autoresearchclaw)、[InternAgent](#internagent)、[Denario](#denario-与-cmbagent)、[AI Scientist v2](#ai-scientist-v2) | 论文产出型任务；有数据集的学科（数据驱动发现） |
| **C. 算法进化** | LLM 做变异算子 → 评估 → 种群选择 → 循环 | [OpenEvolve、ShinkaEvolve](#openevolve-与-shinkaevolve)（AlphaEvolve 开源复刻） | 组合优化、调度、结构设计、数值算法——传统工科里"找一个更好的构造"的问题 |

模式 A 最快出真实结果，建议第一批学科先上 A；模式 B 是论文产出的主线；模式 C 是工科里最被低估的一条，因为 AlphaEvolve 一系在数学与算法上是**真的刷新过人类上限**的[^alphaevolve]。

## 5. 第三层：学科适配——为什么是 skills + 工具

### 5.1 结论

**一个 agent 适配多个学科，靠的不是多训几个模型，而是给它换 skill pack 和接工具。** 这是 2026 年三家头部（[K-Dense](#k-dense-scientific-agent-skills)、[Google DeepMind](#deepmind-science-skills)、[上海 AI Lab](#awesome-scientific-skills)）不约而同选的路线。

### 5.2 为什么

**理由一：Agent Skills 已经是开放标准。**
一个 skill 就是一份 `SKILL.md`（加可选的脚本），丢进 `.claude/skills/` 或等价目录，Claude Code、Cursor、Codex、Antigravity 都能读。这意味着**同一份学科知识可以跨底座复用**，不会绑死在某个 agent 上。

**理由二：学科差异主要在"怎么做"和"用什么工具"，不在推理能力。**
化工的 Aspen 仿真、建筑的能耗模拟、精仪的实验数据格式、智算的训练脚本——这些差异是流程和工具的差异。把它们写成 skill（流程）和接成 MCP/API（工具），比为每个学科训一个模型便宜几个数量级，而且随时能改。

**理由三：多学科的证据已经有了。**

- [InternAgent-1.5](#internagent) 用同一框架跑了物理、生物、地球、生命科学，包括算法发现和干/湿实验发现，一个案例是把气候降尺度 RMSE 压到 0.8488[^internagent-report]。
- [Denario](#denario-与-cmbagent) 用同一套模块生成过天体物理、生物、生物物理、生物医学信息、化学、材料、数学物理、医学、神经科学、行星科学的论文，还有一篇把量子物理和机器学习方法用到天体物理数据上的跨学科论文[^denario-paper]。
- [AutoResearchClaw](#autoresearchclaw) 2026-03-30 起支持加载任意学科的 skills，预置 20 个（科学写作、实验设计、化学、生物等）。

### 5.3 Skill 不等于工具（这是新工科适配真正的工作量所在）

必须分清两样东西：

| | Skill | 工具 |
|---|---|---|
| 是什么 | 一份 markdown，告诉 agent"这个学科该怎么做、注意什么、输出格式是什么" | MCP server / API / 命令行程序 / 仪器接口，agent 实际能调用的能力 |
| 写起来 | 容易，一个懂行的人一下午能写一个 | 难，要接真实的数据源、仿真软件、许可证、账号 |
| 例子 | "分析化工反应动力学数据时先做 Arrhenius 拟合、报告 R² 和残差图" | 调 Aspen Plus 跑一次流程模拟并返回结果 |

三家 skills 库的现状：

- [K-Dense scientific-agent-skills](#k-dense-scientific-agent-skills)（原 claude-scientific-skills）：165 个 skill + 100+ 科学数据库，覆盖基因组、药物发现、分子动力学、地理空间、时间序列等，号称 19 万科学家在用。**偏生命科学与数据科学，工科覆盖薄**。
- [Google DeepMind science-skills](#deepmind-science-skills)（2026-06）：官方包，接入 AlphaGenome、AFDB、UniProt 等 30+ 数据库，主打 grounding（让 agent 查真实数据库而不是靠记忆）和 token 效率。**同样偏生物**。
- [InternScience Awesome-Scientific-Skills](#awesome-scientific-skills)：上海 AI Lab 策展，遵循开放规范，强调"能组合、有人维护"，目前还在合并中。

**这意味着工科方向的 skills 是空白**。天大新工科（化工、建筑、精仪、机械、材料、智算……）每个学院一个 skill pack，本身就是可以开源、可以发出去的产出。

### 5.4 一个 skill pack 应该包含什么

以"化工反应工程"为例：

```
skills/
  chemeng-kinetics/
    SKILL.md          # 何时触发、分析流程、常见坑、输出模板
    scripts/
      fit_arrhenius.py
      plot_residuals.py
  chemeng-aspen/
    SKILL.md          # 如何构造输入、如何解析输出、单位约定
    (工具通过 MCP 接入，skill 只描述用法)
  chemeng-writing/
    SKILL.md          # 该领域论文的章节结构、期刊格式、图表规范
```

写 skill 的人必须是该学科的研究者，这是"新工科"和"上海 AI Lab 通用框架"最本质的区别：**框架是他们的，学科隐性知识是天大的**。

## 6. 第四层：验证——单篇产出怎么把关

### 6.1 结论

**这是 2026 年所有批评文章指向的同一个洞，也是新工科智能体最容易做出差异化的地方。** 验证层的目标不是"评估框架好不好"（那是[第 7 节](#7-第五层评测框架本身怎么评)），而是**对每一篇产出回答：这篇论文的结论能不能信、能不能复现、人类署名者敢不敢签字**。

### 6.2 为什么必须有

- 《Verification Gap》综述（2026-06-29）筛了 125 篇工作纳入 35 篇，按 7 个审计维度编码（生命周期阶段、自主程度、评估方法、发布产物、人在环路点、新颖性验证、结果选择披露），主要发现是：**代码发布已经很普遍，但可复现级别和能验证结论的产物仍然很少**[^verification-gap]。
- 一篇 2026 年的分析显示含幻觉引用的论文比例从 2024 年的 0.3% 升到 2025 年的 2.6%。
- Sakana 团队自己承认通过 workshop 评审的那篇论文"还行但不好"，且是 3 篇里通过 1 篇[^sakana-nature]。
- Kosmos（Edison Scientific）能收 200 美元一次的核心原因，是它的报告里**每一条结论都能追溯到对应的数据分析或文献来源**[^kosmos]。这个"claim → evidence"的可追溯性是商业价值所在，也是开源项目普遍缺的。

### 6.3 具体怎么做（六项检查，每篇必过）

| # | 检查项 | 做法 | 现成参考 |
|---|---|---|---|
| 1 | **引用真实性** | 每条引用回查 OpenAlex / Semantic Scholar / arXiv，查不到的直接删 | [AutoResearchClaw](#autoresearchclaw) 的 anti-fabrication guard；文献只从真实 API 拉 |
| 2 | **新颖性检查** | 想法确定后先做一轮文献对比，输出"最近似的 3 篇已有工作 + 差异点"，差异不成立则退回想法阶段 | [Denario](#denario-与-cmbagent) 的 idea maker / idea hater 对抗；Verification Gap 综述把"novelty verification"列为审计维度[^verification-gap] |
| 3 | **复现脚本** | 每篇论文附一键复现脚本 + 环境锁定 + 随机种子；验证层自动重跑一次，结果偏差超阈值则标红 | [PaperBench](#其他基准) 的 rubric 分解思路[^paperbench]；AutoResearchClaw 的 immutable harness |
| 4 | **claim → evidence 追溯** | 论文每个数值结论链接到产生它的实验 run ID / 日志 / 图表文件 | Kosmos 的结构化世界模型[^kosmos] |
| 5 | **结果选择披露** | 记录总共跑了多少次实验、报告了哪些、为什么没报其余的 | [autoresearch](#karpathy-autoresearch) 的 `results.tsv` 天然就是全记录；Verification Gap 的"result-selection disclosure" |
| 6 | **Reviewer agent** | 多轮、多角色自动评审（方法/实验/写作/伦理），给出分数与修改意见；低于阈值退回 | [AI Scientist v2](#ai-scientist-v2) 的多轮自审；AutoResearchClaw 的 multi-agent peer review；AAAI-26 已在试点 AI 辅助评审 |

六项都过，产出的才是"人类可以署名"的论文；任何一项不过，产出只是"实验报告"。**把这个区分做进系统，比多加十个 agent 都有价值。**

### 6.4 一个容易忽略的点

验证层的产物本身要**独立于生成层**。用同一个模型既写论文又审论文，审出来的问题会和写的时候一样。实践上：评审用不同底座模型，复现在干净沙盒里跑，引用回查走真实 API 而不是让模型"回忆"。

## 7. 第五层：评测——框架本身怎么评

### 7.1 结论

**把"换一个 skill / 改流水线一步"当作实验变量，在固定任务集上跑，看分数变化。** 这和做科研本身是一回事：控制变量、重复试验、报告方差。

### 7.2 用什么任务集

| 基准 | 机构 / 时间 | 内容 | 适用性 |
|---|---|---|---|
| [ResearchClawBench](#researchclawbench) | 上海 AI Lab，2026-03 起 | 40 个真实科研任务、10 个学科；每个任务 = 已发表论文的数据 + 专家多模态 rubric + 真值图；分"复现已有发现"和"新发现"两档 | **首选**。开放社区提交任务（走 HF Space 审核），天大可以把自己的工科任务投进去 |
| [AstaBench](#astabench) | Ai2，2025-10 首发 / 2026-04 更新 | 2400+ 问题、4 大类（文献理解、代码执行、数据分析、端到端发现） | 适合评单项能力，尤其文献层 |
| [Terminal-Bench Science](#其他基准) | Harbor，2026 | 终端环境里的真实科研工作流，覆盖生命/物理/地球/数学科学；已上 Claude Opus 4.7、GPT-5.5、Gemini 3.1 Pro 的 model card | 适合评底座 |
| [NewtonBench](#其他基准) | HKUST，ICLR 2026 | 324 个任务、12 个物理领域，通过交互实验"重新发现"物理定律，抗记忆设计 | 适合评"闭环发现"能力而不是背书 |
| [PaperBench](#其他基准) | OpenAI，2025-04 | 复现 20 篇 ICML 论文，8316 个可打分子任务[^paperbench] | 适合评复现能力（验证层第 3 项） |

### 7.3 ResearchClawBench 的评测流程（因为它最贴合）

1. **任务定义**：每个任务一个目录，含数据集（来自已发表论文）、任务描述、专家写的 rubric、真值图（多模态判分时第一张附图作为 ground truth）。
2. **接入 agent**：仓库内置了多个 agent 适配（OpenClaw、Nanobot、EvoScientist、ResearchHarness 基线），配置在 `agents.json`，接自己的框架就是加一个 entry。
3. **跑评测**：`rcb-eval` 命令行工具（2026-06-05 加入）用 YAML 配置，支持并发、重复试验、自动打分、按 run 和按 task 的统计，输出 markdown 报告。
4. **看稳定性**：2026-07-01 起榜单提供 Pass@5 和重复运行的稳定性统计——这对 ablation 特别重要，因为 agent 的方差很大，单次结果没有意义。
5. **投任务**：通过 HF Space 上传 zip，验证后开 PR 到数据集仓库，维护者审核合并。

时间线与链接见 [ResearchClawBench 条目](#researchclawbench)。

### 7.4 怎么做 ablation

```
固定：任务集（ResearchClawBench 的某个学科子集）、底座模型、评审模型
变量（每次只动一个）：
  - 流水线：去掉"新颖性检查"这一步
  - 流水线：把"先跑 baseline"移到"想法生成"之前
  - skill：换 K-Dense 的写作 skill vs 自己写的天大化工写作 skill
  - 底座：Claude Code vs Codex CLI
重复：每个配置跑 ≥5 次
报告：rubric 平均分、Pass@5、方差、token 成本、耗时
```

这样每一次改动都是一个可发表的小实验，"新工科智能体"这个项目自己就在用自己做科研。

## 8. 开源项目现状详述

按层排列。每个项目讲清楚：谁做的、什么时候出的、怎么演化的、架构是什么、怎么跑、缺点是什么、能借哪个模块。每个条目第一行是链接，最后一行是被正文哪些节引用。

### 8.1 底座与循环层

#### Karpathy autoresearch

- **链接**：<https://github.com/karpathy/autoresearch>；衍生汇总 <https://github.com/webfuse-com/awesome-autoresearch>
- **代码级深读**（2026-09-09）：[选型 / autoresearch](../../selection/2026-0909-pipeline-frameworks/autoresearch.md)。要点：棘轮的本质不在循环里传什么，而在 git 承载状态、外部单标量硬闸收敛、gitignore 的账本外化失败记忆；但整套是荣誉制且接受阈值低于噪声（一次 H100 真实跑档 125 次实验为证）。抄形态不抄代码。
- **时间**：2026-03-07 发布。几天内 21k star、Karpathy 推文 860 万浏览；一个月内 66k star、9.6k fork。
- **背景**：Karpathy 在预训练小型 transformer（nanochat）时，大量时间花在"改一个超参或结构 → 跑一会 → 看验证指标 → 决定留不留"的手动循环上。autoresearch 就是把这个循环交给 agent。
- **架构**（三个文件，约 630 行）：
    - `prepare.py`：数据准备与评估，**固定不动**；
    - `train.py`：训练脚本，**agent 唯一可改的文件**；
    - `program.md`：给 agent 的指令——搜索方向、不能动什么、什么时候停。这一个 markdown 同时承担了指令、约束、停止条件三种角色。
- **循环**：agent 读代码 → 提出改动假设 → 改 `train.py` → 跑 5 分钟训练（单 GPU）→ 看 `val_bpb` → 变好则 `git commit`，变差则回滚 → 循环。所有结果写进 `results.tsv`。崩溃自动恢复，不打断通宵运行。
- **结果**：Karpathy 两天跑了 700 次实验，agent 叠加了 20 项改进，把 "Time to GPT-2" 从 2.02 小时压到 1.80 小时（约 11%）。Shopify CEO 醒来发现模型超过了自己手调的基线；Karpathy 自己藏了几个月的 bug 被 agent 抓出来。
- **和传统调参的区别**：Optuna 搜的是你预先定义的超参网格；autoresearch 直接读改源码，可以重写 attention、换优化器、重构训练循环。
- **缺点**：只做了单指标优化，没有文献、假设、写作；只适用于"几分钟能跑完一次"的任务；不解决"该优化什么"的问题。
- **能借什么**：模式 A 的全部——`program.md` 即约束、git 即回滚、`results.tsv` 即全记录（验证层第 5 项"结果选择披露"直接得到满足）。
- **衍生生态**（均 2026-03 之后）：
    - ARK（KAUST）：6 个 agent 编排——提案分析、文献、Slurm 实验、LaTeX 起草、迭代评审；CLI / Web / Telegram 控制。
    - AutoSci：基于 Claude Code 的 20+ skills 全生命周期平台，研究状态存在结构化 wiki 里（Karpathy 的 LLM-Wiki 设想）。
    - NanoResearch：规划实验、生成代码、本地或 SLURM 执行、基于真实结果写论文。
    - Tree-AutoResearch：<https://github.com/dongdongunique/Tree-AutoResearch>，把线性循环改成树搜索，每个节点绑定 git worktree。
    - overnight-experimenter / autoloop：把循环泛化到任何"有数值分数"的问题。
- **被引用**：§1、§3.2、§4.3、§6.3、§10

### 8.2 流水线层

#### AutoResearchClaw

- **链接**：<https://github.com/aiming-lab/AutoResearchClaw>（UNC aiming-lab）
- **代码级深读**（2026-09-09）：[选型 / AutoResearchClaw](../../selection/2026-0909-pipeline-frameworks/autoresearchclaw.md)。要点："底座可换"是把 agent 名透传给外部 npm 包 `acpx`，本仓零分支；编排仍是外层 for，状态机写了没接线；真硬的是数字白名单对账与五源引用校验两条零 LLM 判据，以及 ARC-Bench 的 manifest / rubric 契约；8 万行里死代码过万，无 CI。零件按模块摘，骨架不要。
- **时间线**：
    - 2026-03-15 v0.1.0：23 阶段全自动流水线，一个想法 → 会议级论文。
    - 2026-03-22 v0.3.2：跨平台——任何 ACP 兼容后端（Claude Code、Codex CLI、Copilot CLI、Gemini CLI、Kimi CLI）；通过 OpenClaw 桥接 Discord / Telegram / 飞书 / 微信；新增"CLI-agent 代码生成后端"，把第 10、13 阶段委托给外部 CLI agent，带预算控制和超时管理。
    - 2026-03-30 灵活技能加载：可装任意学科的开源或自定义 skill，预置 20 个（科学写作、实验设计、化学、生物等，含社区贡献的 A-Evolve 进化 skill）；`researchclaw skills install` 或直接把 SKILL.md 丢进 `.claude/skills/`。
- **流水线内容**（从 README 可见的阶段组）：
    1. 文献：从 OpenAlex、Semantic Scholar、arXiv 拉真实文献；
    2. 想法与假设；
    3. 实验设计；
    4. 代码生成（第 10、13 阶段，可委托外部 CLI agent；复杂实验路由到 OpenCode 生成多文件项目、自定义架构、训练循环、消融）；
    5. 沙盒执行：自动识别 GPU / MPS / CPU；AST 校验代码；不可变 harness；NaN/Inf 快速失败；自愈修复最多 10 轮；部分结果捕获；
    6. 统计分析；
    7. 多智能体同行评审；
    8. 写作：NeurIPS / ICML / ICLR 模板（`neurips_2025`、`iclr_2026`、`icml_2026`），逐节起草 5000–6500 词，反捏造守卫、修订长度守卫、反免责声明；Markdown → LaTeX 含公式、表格、图、交叉引用、`\cite{}`。
- **两种模式**：`--auto-approve` 全自动；`--mode co-pilot` 在关键决策点等人。
- **MetaClaw**：跨运行学习——自动从失败和警告里提炼经验，转成 skill，注入后续运行的全部 23 个阶段。
- **怎么跑**：`pip install -e .` → `researchclaw setup` → `researchclaw init` → `researchclaw run --topic "..." --auto-approve`；配置文件里设 `base_url`、`api_key_env`、`primary_model`、`fallback_models`、沙盒 python 路径；输出在 `artifacts/rc-<时间戳>/deliverables/`（LaTeX、BibTeX、实验代码、图）。
- **缺点**：目标会议是 NeurIPS/ICML/ICLR，模板和评审 rubric 是 ML 视角的；工科期刊格式要自己加；仓库 fork 极多（搜索能看到十几个同名 fork），以 aiming-lab 为准。
- **能借什么**：整个"底座可换 + skills 可插 + 消息平台可接"的产品形态；沙盒执行的安全设计；反捏造守卫。
- **被引用**：§1、§3.2、§3.3、§4.3、§5.2、§6.3、§8.3、§9、§10

#### InternAgent

- **链接**：<https://github.com/InternScience/InternAgent>（上海 AI Lab · InternScience）；组织 <https://github.com/InternScience>；1.5 技术报告 <https://arxiv.org/abs/2602.08990>[^internagent-report]
- **代码级深读**（2026-09-09）：[选型 / InternAgent](../../selection/2026-0909-pipeline-frameworks/internagent.md)。要点：三个实验后端里只有 claudecode 真能跑，openhands 从未有过实现；流水线编排没有抽象层；最值得借的是任务目录契约与实验执行循环，不当底座。
- **演化过程**（这是国内跟得最久的一条线）：
    - 2025-01 Dolphin：提出"思考—实践—反馈"的闭环 auto-research；
    - 2025-05-22 NovelSeek（后改名 InternAgent）：从假设到验证的闭环系统；
    - 2025-07-17 部分开源；
    - 2025-10-13 InternAgent-1.0 完整开源，覆盖 12 类科研任务的端到端自动化与自主进化；
    - 2026-02-10 InternAgent-1.5 技术报告：统一框架、长程自主发现。
- **1.5 架构**：三个子系统构成持续循环——
    - **生成子系统**：Deep Research 模块把研究问题拆成子任务，并行从学术数据库和网络取信息，合成答案或结构化报告；产出假设与方案；
    - **验证子系统**：执行完整的计算或湿实验；
    - **进化子系统**：跨会话持久记忆记录实验结果，避免重复失败方向、在成功方向上叠加；方案精炼。
- **能力数据**：GAIA 86.06、GPQA 87.37，HLE 和 FrontierScience 领先；算法发现任务上为核心 ML 问题自主设计出有竞争力的方法；经验发现任务覆盖地球、生命、生物、物理，案例包括气候降尺度 RMSE 0.8488、复现复杂生物靶点识别。
- **怎么跑**：算法发现任务在 `tasks/`，每个含 `prompt.json`、`baseline code/`、`launcher.sh`；论文复现任务在 `sci_tasks/tasks/`（来自 [ResearchClawBench](#researchclawbench)），给一篇论文和数据，让它自主复现关键发现；`scripts/` 有现成示例；记忆模块见 `docs/memory_module.md`。
- **周边**（同组织，2026）：MLEvolve <https://github.com/InternScience/MLEvolve>（ML 算法端到端自动设计与优化，渐进搜索 + 经验记忆）、[ResearchClawBench](#researchclawbench)（评测）、[Awesome-Scientific-Skills](#awesome-scientific-skills)、DrClaw <https://github.com/InternScience/DrClaw>、AgentPanel（人机协作讨论社区）、GraphGen。
- **缺点**：三子系统耦合较紧，不像 AutoResearchClaw 那样把底座抽出来随便换；文档和示例偏他们自己的任务。
- **能借什么**：跨会话记忆的设计；"复现已发表论文"作为入门任务的做法（这对新工科各学院冷启动特别合适——先复现本院老师的论文）；国产模型适配。
- **被引用**：§1、§3.2、§3.3、§4.3、§5.2、§9、§10

#### Denario 与 cmbagent

- **链接**：Denario <https://github.com/AstroPilot-AI/Denario>；后端 cmbagent <https://github.com/CMBAgents/cmbagent>；论文 <https://arxiv.org/abs/2510.26887>[^denario-paper]（剑桥 / Flatiron / AstroPilot）
- **时间线**：2025-07 cmbagent 论文 → 2025-10-09 一篇 Denario 全生成的论文被 Agents4Science 2025 接收[^agents4science] → 2025-10-30 论文 → 2025-11-03 v1.0 发布 → 2025-12-07 cmbagent 拿 NeurIPS 2025 Fair Universe 竞赛第一 → 2026-01-20 写入 LSST DESC AI 路线图。
- **架构**：AG2 + LangGraph 实现，cmbagent 做研究分析后端。流程：用户给出问题或数据描述 → **idea maker 和 idea hater 两个 agent 对话**得到一个研究想法 → researcher agent 两轮生成方法 → cmbagent 以 Planning & Control 策略执行研究（无人在环）→ 输出 markdown 报告和图 → 另一个 LangGraph 子系统把报告转成可发表的 PDF 论文，**每个论文章节是图上一个节点/一个 agent**（例如 methods 节点的 agent 读输入文件写方法部分）。
- **模块化**：可以只跑"出想法"，也可以端到端；有 GUI（DenarioApp）和 HF Spaces 演示；`pip install "denario[app]"`。
- **多学科证据**：论文里展示了天体物理、生物、生物物理、生物医学信息、化学、材料、数学物理、医学、神经科学、行星科学的生成论文，附领域专家的打分和评审意见，还有一篇量子物理 + ML 方法用于天体物理数据的跨学科论文。
- **许可证**：Denario GPL-3、cmbagent Apache-2，要注意 GPL 对下游的传染。
- **能借什么**：论文写作的 LangGraph 图（每节一个 agent）；idea maker / hater 对抗机制（直接就是验证层的新颖性检查雏形）；GUI 形态。
- **被引用**：§4.3、§5.2、§6.3

#### AI Scientist v2

- **链接**：<https://github.com/SakanaAI/AI-Scientist-v2>；博客 <https://sakana.ai/ai-scientist-first-publication/>；Nature 论文 DOI 10.1038/s41586-026-10265-5[^sakana-nature]（Sakana AI）
- **时间线**：2024-08 v1 → 2025-03-12 v2 论文通过 ICLR 2025 ICBINB workshop 评审 → 2025-04-07 技术报告 + 开源 → 2026-03-26 系统论文登 Nature。
- **评审实验的全过程**：与 ICLR 领导层和 workshop 组织者事先约定，投 3 篇全 AI 生成的论文进双盲评审；1 篇通过，分数 6/7/6，均分 6.33，略高于 6 的门槛，超过 55% 的人类投稿；按约定评审后全部撤稿。作者自评"还行但不好"，且承认 workshop 门槛低于主会；主会明确禁止纯 AI 论文。
- **架构要点**：v1 需要人给代码模板，v2 去掉了模板；用 agentic tree search 并行探索实验分支，实验管理器决定扩展哪些节点；VLM 检查图表；多轮自评审后才输出。
- **能借什么**：tree search 的实验探索；多轮自审的 reviewer 设计；"与会议协商后做评审实验"这一透明流程本身。
- **被引用**：§1、§4.3、§6.3

#### OpenEvolve 与 ShinkaEvolve

- **链接**：OpenEvolve <https://github.com/algorithmicsuperintelligence/openevolve>；AlphaEvolve 论文 <https://arxiv.org/abs/2506.13131>[^alphaevolve]
- **背景**：DeepMind 2025-05 发布 AlphaEvolve（FunSearch 的继任），LLM 作为变异算子对程序做进化搜索，在矩阵乘法、数学构造、调度上刷新了已知最优；OpenEvolve 是发布后几天内出现的开源复刻，ShinkaEvolve 是 Sakana 的版本。2026 年 DeepMind 又在 Nature 发了"帮科学家写专家级经验软件"的系统，2026-03 有 ptychography 算法自主发现、2026-05 有 CVEvolve（非结构化科学数据处理算法发现）等应用。
- **能借什么**：工科优化问题的求解模式；MAP-Elites 式的多样性保持。
- **被引用**：§4.3、§10

### 8.3 学科适配层

#### K-Dense scientific-agent-skills

- **链接**：<https://github.com/K-Dense-AI/scientific-agent-skills>（原 claude-scientific-skills）
- **规模演化**：2026-01 索引 143 个 → 2026-07 165 个 skill + 100+ 数据库；号称 19 万科学家在用，26k+ star；MIT 许可但每个 skill 有自己的 license 字段。
- **内容**：癌症基因组、1000 Genomes 查询、调控序列预测、病原变异监测、分析方法验证、PK/PD 建模、生物医学全文检索、药物靶点结合、分子动力学、RNA velocity、微生物组基础模型、地理空间、时间序列预测……还打包成 Agent Plugin（`plugin.json` + `skills/`）可整体加载。
- **维护信号**：有 release 记录，持续更新 skill 里使用的模型版本和依赖库；有 SkillScanner 安全扫描流程。
- **评价**：目前最大、最活跃的科研 skills 库，但工科几乎空白。
- **被引用**：§1、§5.1、§5.3

#### DeepMind science-skills

- **链接**：<https://github.com/google-deepmind/science-skills>
- **时间**：2026-06 出现，7 月初有 release。
- **定位**：让 coding agent 做科研时**查真实数据库而不是靠训练记忆**——接 AlphaGenome、AlphaFold DB、UniProt 等 30+ 数据库和工具，强调 grounding 和 token 效率。安装就是把目录拷进 `~/.claude/skills/`。两种用法：探索模式（沿线索跨库浏览）和验证模式（对假设查库返回置信度和引用链）。
- **评价**：官方背书、质量高，但同样偏生物。"验证模式"的设计值得直接搬到验证层。
- **被引用**：§1、§5.1、§5.3

#### Awesome-Scientific-Skills

- **链接**：<https://github.com/InternScience/Awesome-Scientific-Skills>（上海 AI Lab · InternScience）
- **状态**：策展中，README 写着合并后 `git clone` 再拷进 `.claude/skills/` 即可；筛选标准强调能与其他 skill 组合、作者持续维护；明确警告 skill 可以执行任意代码、装前必看。
- **评价**：国内最可能长期维护的一个，值得把天大的 skill pack 投过去。
- **被引用**：§1、§5.1、§5.3、§8.2

#### Claw4Science 与 OpenClaw 科研生态

- **链接**：<https://www.biorxiv.org/content/10.64898/2026.03.30.715118v1>[^claw4science]
- **背景**：OpenClaw（2025-11 发布，几周 179k star）用 markdown skill 表达工作流，带起一批"Claw"科研项目：[AutoResearchClaw](#autoresearchclaw)、DrClaw、ResearchClaw、ScienceClaw、Prismer、CitationClaw，还有 ClawHub 和 Claw4S Conference 2026。Claw4Science（2026-03-30）是第一个把这个生态做成策展数据集的工作，动机就是**碎片化——项目散在各仓库、skill 质量参差、命名不统一、没有统一发现和比较的方式**。
- **评价**：热但新，稳定性要自己验；但它说明"skill 化 + 消息平台入口"是 2026 年公认的产品形态。
- **被引用**：仅本节

#### 工具层

skill 背后的能力：

- ToolUniverse（哈佛）：<https://github.com/mims-harvard/ToolUniverse>，600+ 科学工具统一接口，可作为"一个 agent 接多学科工具"的总线。
- PaperQA2（FutureHouse）：<https://github.com/Future-House/paper-qa>，文献问答与合成，2024-09 报告超过人类基线，是文献阶段的成熟组件。
- MCP：把院内仿真软件、数据库、仪器包成 MCP server 是接工具的标准做法。
- **被引用**：仅本节；§5.3 的「工具」一列即指这里

### 8.4 验证与评测层

#### ResearchClawBench

- **链接**：<https://github.com/InternScience/ResearchClawBench>（上海 AI Lab）；数据集 <https://huggingface.co/datasets/InternScience/ResearchClawBench>；论文 <https://arxiv.org/abs/2606.07591>[^researchclawbench-paper]
- **时间线**：
    - 2026-03-20 加入 Nanobot（超轻量 OpenClaw 替代）作为 agent，配置迁到 `agents.json`；
    - 2026-03-27 HF 数据集镜像上线（含 ResearchClawBench-Self 额外 10 个任务）；开放社区任务提交 Space；
    - 2026-03-30 内置 EvoScientist 支持[^evoscientist]；明确多模态判分时第一张附图为真值；
    - 2026-04-07 内置 ResearchHarness 轻量基线，用同一工作流测不同 LLM；
    - 2026-05-28 / 06-02 / 06-09 陆续评 Gemini-3.5-Flash、Qwen3.7、Claude-Opus-4.8、MiniMax-M3；
    - 2026-06-03 EvoScientist v0.1.1 上榜（保留 v0.0.4 作为版本化基线）；
    - 2026-06-05 `rcb-eval` YAML 配置的命令行评测（并发、重复试验、自动打分、markdown 报告）；
    - 2026-06-09 论文上 arXiv；
    - 2026-07-01 Pass@5 与稳定性统计；
    - 2026-07-08 / 15 / 28 评 Hy3-Preview、Qiushi、InnoClaw（GPT-5.5）、Open Science（Claude-Opus-4.8）。
- **任务设计**：40 个基础任务、10 个学科；数据来自已发表论文；专家策划的多模态 rubric；分"再发现"和"新发现"两档；GitHub 仓库只放基础 40 个，新任务走 HF Space 验证 → PR → 维护者审核。
- **评价**：目前唯一持续更新、开放投任务、带稳定性统计的端到端科研评测。新工科智能体应该以它为默认评测，并把天大工科任务投进去。
- **被引用**：§1、§7.2、§7.3、§8.2、§9、§10

#### AstaBench

- **链接**：<https://allenai.org/asta/bench>（Ai2）；论文 <https://arxiv.org/abs/2510.21652>[^astabench-paper]；2026-04 更新 <https://allenai.org/blog/astabench-update-spring-2026>[^astabench-update]
- **时间线**：2025-08 首发结果 → 2025-10-24 论文 → 2026-04-21 v2 / ICLR 2026 oral → 2026-04-30 更新博客。
- **内容**：2400+ 问题，4 类（文献理解、代码执行、数据分析、端到端发现）；Asta v0（路由到专用子 agent）综合约 53%；E2E-Bench-Hard 3%。Asta Paper Finder 在 PaperFindingBench 上是最接近对手（ReAct）的两倍以上。
- **评价**：数字最诚实，适合评单项能力和文献层。
- **被引用**：§1、§4.2、§7.2

#### 其他基准

- Terminal-Bench Science（Harbor，2026）：终端环境真实科研工作流，已上头部模型的 model card。
- NewtonBench（HKUST，ICLR 2026）：324 任务、12 个物理领域，抗记忆的定律再发现。
- PaperBench（OpenAI，2025-04）：<https://arxiv.org/abs/2504.01848>[^paperbench]，复现 20 篇 ICML 论文，8316 个可打分子任务，rubric 与原作者共同制定。
- **被引用**：§6.3、§7.2

### 8.5 2026 年的批评与综述

这些决定了验证层怎么设计：

| 日期 | 文章 | 核心观点 |
|---|---|---|
| 2026-05-09 | Agentic AI Scientists Are Not Built For Autonomous Scientific Discovery[^not-built] | 当前系统是称职的"副科学家"而非自主发现者：选题有偏、缺实验室隐性知识、多样性坍缩、基准测的是单轮准确率而非闭环有效性；受控研究显示人机协作质量最高、全自动反而下降 |
| 2026-05 | Sibyl-AutoResearch[^sibyl] | 自主科研需要的是自进化的试错 harness，不是论文生成器 |
| 2026-05 | AutoResearch AI[^autoresearch-ai-survey] | 对 2026 年自动化科研工具链的综述，覆盖 Claw 系列 |
| 2026-06-29 | Autonomous Research Agents: A Survey of AI Scientists and the Verification Gap[^verification-gap] | 筛 125 纳 35，按 7 个审计维度编码；代码开源普遍，可复现和可验证产物稀少 |
| 2026-03 | EvoScientist[^evoscientist] | 多智能体自进化 AI 科学家，已上 ResearchClawBench 榜 |
| 2026-03 | ASI-Evolve[^asi-evolve] | AI 加速 AI 的自改进方向 |
| 2026-05 / 06 | ARIS[^aris]、Agon[^agon]、Clarus[^clarus] | 对抗式 / 大规模全学科 / web 级协作的多智能体科研，偏论文 |

## 9. 制度约束与项目定位

1. **AI 不能署名。** 主会明确禁止纯 AI 论文投稿，五大出版社全部禁止 AI 署名；截至 2026-04 没有任何 AI 独立署名的论文发表在主流期刊。JAIGP（2026-02 创刊）和 Agents4Science（2025 首届）[^agents4science]是专门给 AI 作者的场子，但不是主流。
2. **所以"论文产出"要定义成人机协作。** 立项写法：**AI 完成 80% 的机械工作、研究者署名并把关、全程可审计**。这比"自动发论文"更能落地，也更能过学校审查。[第 6.3 节](#63-具体怎么做六项检查每篇必过)的六项检查就是"可审计"的具体内容。
3. **先窄后宽。** 第一批学科选有明确数值指标、单次实验几分钟能跑完的（仿真参数优化、控制、结构、AI4S 类），用模式 A 先出几篇有真实结果的论文，再扩到假设生成型学科。
4. **"新工科"的差异化不在框架，在学科隐性知识。** 框架（[InternAgent](#internagent) / [AutoResearchClaw](#autoresearchclaw)）是别人的，天大各学院研究者写的 skill pack、接的真实工具、投进 [ResearchClawBench](#researchclawbench) 的工科任务，才是别人没有的。

## 10. 建议路线图

排期原则先说清楚：执行环节由 AI 辅助编码承担，代码、脚本、实验的产出速度不再是瓶颈，所以不能按传统工期排；**日历上真正占位置的是人的决策点**：选哪个学院、哪个任务、哪些 skill 进正式版、哪篇结果敢署名。节奏定为：**2026-09-28 发布第一个初级版本，之后每月一个正式版；正式版之间内测版随时发**，用来试方向、收反馈，不受排期约束。

| 版本 | 时间 | 人决策什么 | 交付什么 |
|---|---|---|---|
| **初级版** | 2026-09-28 | 定底座与流水线；选第一个学院与第一个指标型任务 | 选型报告与成本对比：同一个小任务分别跑 [AutoResearchClaw](#autoresearchclaw) 和 [InternAgent-1.5](#internagent)，底座各试 Claude Code 与一个国产模型；模式 A 的 [autoresearch](#karpathy-autoresearch) 循环在第一个任务上跑通，复现本院老师一篇论文作为入门（InternAgent 的 sci_tasks 做法） |
| **10 月正式版** | 2026-10 | 定第二个学院；定第一批 skill 的范围；定"人类可署名"的最低门槛 | 模式 A 在 1–2 个学院产出真实指标提升；每学院 1 名研究者写 3–5 个 skill，院内仿真 / 数据库包成 MCP；验证层先上机器可判的三项：引用真实性、复现脚本、结果选择披露（[第 6.3 节](#63-具体怎么做六项检查每篇必过)第 1、3、5 项） |
| **11 月正式版** | 2026-11 | 定评审用的底座与退回阈值；定投进 ResearchClawBench 的工科任务 | 验证层六项全部上线，补新颖性检查、claim → evidence 追溯、reviewer agent；评审用不同底座，复现在干净沙盒；接入 [ResearchClawBench](#researchclawbench)，按[第 7.4 节](#74-怎么做-ablation)跑第一轮 ablation |
| **12 月正式版** | 2026-12 | 定第一篇人机协作论文的题目与署名者；定模式 C 的试点问题 | 有数据集的学科上假设生成流水线（模式 B）跑通，产出第一篇过六项检查的论文草稿；优化类问题上 [OpenEvolve](#openevolve-与-shinkaevolve) 试点；工科任务提交进 ResearchClawBench |
| **之后每月** | 2027-01 起 | 按 ablation 结果决定改哪一步、扩哪个学院 | 每月一个正式版：新学院的 skill pack、验证层加严、榜单结果与 ablation 小论文 |

三条排期纪律：

1. 正式版只在决策点之后发。决策是人的事，不因为代码提前写完就提前发。
2. 内测版随时发，但一个内测版只试一件事：换一个 skill、改流水线一步，对应[第 7.4 节](#74-怎么做-ablation)"每次只动一个变量"的做法。
3. 每个正式版都要有一个能对外讲的产出：报告、指标、论文草稿、榜单结果。只有代码不算。

## 11. 附录：2026 年时间线

只列 2026 年。项目链接在[第 8 节](#8-开源项目现状详述)对应条目，完整台账见 `references.md`。

| 日期 | 事件 |
|---|---|
| 2026-01 | K-Dense skills 索引 143 个；Denario/cmbagent 写入 LSST DESC AI 路线图（01-20） |
| 2026-02 | JAIGP 创刊；**InternAgent-1.5** 技术报告（02-10） |
| 2026-03-07 | **Karpathy autoresearch** 发布 |
| 2026-03-15 | **AutoResearchClaw** v0.1.0 |
| 2026-03-20 | ResearchClawBench 首条更新日志 |
| 2026-03-22 | AutoResearchClaw v0.3.2（多底座、多消息平台） |
| 2026-03-26 | Sakana AI Scientist 登 Nature |
| 2026-03-27 | ResearchClawBench HF 数据集 + 社区投任务 |
| 2026-03-30 | AutoResearchClaw 技能加载；Claw4Science 数据集；ResearchClawBench 接 EvoScientist |
| 2026-03 | EvoScientist、ASI-Evolve 论文 |
| 2026-04-07 | ResearchClawBench ResearchHarness 基线 |
| 2026-04-21 / 30 | AstaBench v2（ICLR 2026 oral）及更新：E2E-Hard 3% |
| 2026-05-09 | 《Not Built For Autonomous Discovery》 |
| 2026-05 | Sibyl-AutoResearch、AutoResearch AI 综述、ARIS |
| 2026-06-05 / 09 | ResearchClawBench `rcb-eval` 与论文 |
| 2026-06 | **DeepMind science-skills**；Agon、Clarus |
| 2026-06-29 | Google Co-Scientist 正式论文；《Verification Gap》综述 |
| 2026-07 | K-Dense 165 skills；ResearchClawBench Pass@5 与新一批 agent 上榜 |

## 参考与注

[^internagent-report]: InternAgent-1.5 技术报告，上海 AI Lab，2026-02-10，<https://arxiv.org/abs/2602.08990>。
[^astabench-update]: AstaBench 2026 春季更新博客，Ai2，2026-04-30，<https://allenai.org/blog/astabench-update-spring-2026>。E2E-Bench-Hard 3% 完美完成、综合分约 53% 均出自此处。
[^astabench-paper]: AstaBench 论文，Ai2，2025-10-24，<https://arxiv.org/abs/2510.21652>；ICLR 2026 oral。
[^not-built]: Agentic AI Scientists Are Not Built For Autonomous Scientific Discovery，2026-05-09，<https://arxiv.org/abs/2605.08956>。
[^sibyl]: Sibyl-AutoResearch，2026-05，<https://arxiv.org/abs/2605.22343>。
[^verification-gap]: Autonomous Research Agents: A Survey of AI Scientists and the Verification Gap，2026-06-29，<https://arxiv.org/abs/2608.05179>。
[^autoresearch-ai-survey]: AutoResearch AI，对 2026 年自动化科研工具链的综述，2026-05，<https://arxiv.org/abs/2605.23204>。
[^alphaevolve]: AlphaEvolve 论文，Google DeepMind，2025-05，<https://arxiv.org/abs/2506.13131>。
[^denario-paper]: Denario 论文，2025-10-30，<https://arxiv.org/abs/2510.26887>。
[^sakana-nature]: The AI Scientist 系统论文，Nature，2026-03-26，DOI 10.1038/s41586-026-10265-5；评审实验经过见 Sakana 博客 <https://sakana.ai/ai-scientist-first-publication/>。
[^kosmos]: Kosmos，Edison Scientific，<https://arxiv.org/abs/2511.02824>；"claim → evidence"可追溯性的参考。
[^paperbench]: PaperBench，OpenAI，2025-04，<https://arxiv.org/abs/2504.01848>。
[^researchclawbench-paper]: ResearchClawBench 论文，上海 AI Lab，2026-06-09，<https://arxiv.org/abs/2606.07591>。
[^claw4science]: Claw4Science，bioRxiv，2026-03-30，<https://www.biorxiv.org/content/10.64898/2026.03.30.715118v1>。
[^evoscientist]: EvoScientist，2026-03，<https://arxiv.org/abs/2603.08127>。
[^asi-evolve]: ASI-Evolve，2026-03，<https://arxiv.org/abs/2603.29640>。
[^aris]: ARIS，2026-05，<https://arxiv.org/abs/2605.03042>。
[^agon]: Agon，2026-06，<https://arxiv.org/abs/2606.24177>。
[^clarus]: Clarus，2026-06，<https://arxiv.org/abs/2606.30246>。
[^agents4science]: Agents4Science 会议，斯坦福，<https://agents4science.stanford.edu>。
