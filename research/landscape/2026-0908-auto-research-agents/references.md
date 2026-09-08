# 文献与项目台账

正文 `README.md` 里每个项目名链接到第 8 节条目、每个数字与判断挂脚注；这份台账是它们的平铺索引，用来快速核对"某个东西在哪、链接是什么、正文哪里用到了"。改正文时同步改这里。

类型：项目 = 能装能跑的开源仓库；论文 = 只作为证据引用；基准 = 评测任务集；制度 = 会议与出版规则。

## 底座与循环层

| 名称 | 类型 | 机构 | 链接 | 一句话 | 正文位置 |
|---|---|---|---|---|---|
| autoresearch | 项目 | Karpathy | <https://github.com/karpathy/autoresearch> | 630 行、三个文件的棘轮优化循环，模式 A 的原型 | [§8.1](README.md#karpathy-autoresearch) |
| awesome-autoresearch | 索引 | webfuse-com | <https://github.com/webfuse-com/awesome-autoresearch> | autoresearch 衍生项目汇总 | [§8.1](README.md#karpathy-autoresearch) |
| Tree-AutoResearch | 项目 | dongdongunique | <https://github.com/dongdongunique/Tree-AutoResearch> | 把线性循环改成树搜索，节点绑 git worktree | [§8.1](README.md#karpathy-autoresearch) |

## 流水线层

| 名称 | 类型 | 机构 | 链接 | 一句话 | 正文位置 |
|---|---|---|---|---|---|
| AutoResearchClaw | 项目 | UNC aiming-lab | <https://github.com/aiming-lab/AutoResearchClaw> | 23 阶段端到端流水线，底座可换、skills 可插、消息平台可接 | [§8.2](README.md#autoresearchclaw) |
| InternAgent | 项目 | 上海 AI Lab · InternScience | <https://github.com/InternScience/InternAgent> | 生成 / 验证 / 进化三子系统的统一框架，国产模型适配 | [§8.2](README.md#internagent) |
| InternAgent-1.5 技术报告 | 论文 | 上海 AI Lab | <https://arxiv.org/abs/2602.08990> | 统一框架、长程自主发现，多学科案例 | 脚注 internagent-report |
| InternScience 组织 | 索引 | 上海 AI Lab | <https://github.com/InternScience> | InternAgent、ResearchClawBench、skills 库的母组织 | [§8.2](README.md#internagent) |
| MLEvolve | 项目 | InternScience | <https://github.com/InternScience/MLEvolve> | ML 算法端到端自动设计与优化 | [§8.2](README.md#internagent) |
| DrClaw | 项目 | InternScience | <https://github.com/InternScience/DrClaw> | InternScience 的 Claw 系科研 agent | [§8.2](README.md#internagent) |
| Denario | 项目 | AstroPilot-AI | <https://github.com/AstroPilot-AI/Denario> | AG2 + LangGraph 的多学科论文生成，每节一个 agent | [§8.2](README.md#denario-与-cmbagent) |
| cmbagent | 项目 | CMBAgents | <https://github.com/CMBAgents/cmbagent> | Denario 的研究分析后端 | [§8.2](README.md#denario-与-cmbagent) |
| Denario 论文 | 论文 | 剑桥 / Flatiron / AstroPilot | <https://arxiv.org/abs/2510.26887> | 十个学科的生成论文与专家评审 | 脚注 denario-paper |
| AI Scientist v2 | 项目 | Sakana AI | <https://github.com/SakanaAI/AI-Scientist-v2> | 去模板、tree search 探索、多轮自审 | [§8.2](README.md#ai-scientist-v2) |
| AI Scientist 首篇通过评审博客 | 博客 | Sakana AI | <https://sakana.ai/ai-scientist-first-publication/> | 与 ICLR workshop 约定的评审实验经过 | 脚注 sakana-nature |
| AI Scientist Nature 论文 | 论文 | Sakana AI | DOI 10.1038/s41586-026-10265-5 | 2026-03-26 系统论文 | 脚注 sakana-nature |
| OpenEvolve | 项目 | algorithmicsuperintelligence | <https://github.com/algorithmicsuperintelligence/openevolve> | AlphaEvolve 开源复刻，模式 C | [§8.2](README.md#openevolve-与-shinkaevolve) |
| AlphaEvolve | 论文 | Google DeepMind | <https://arxiv.org/abs/2506.13131> | LLM 作变异算子的程序进化搜索 | 脚注 alphaevolve |
| Agent Laboratory | 项目 | JHU | <https://github.com/SamuelSchmidgall/AgentLaboratory> | 2025 年前的整体式系统之一 | [§1](README.md#1-2026-年发生了什么) |
| AI-Researcher | 项目 | 港大 HKUDS | <https://github.com/HKUDS/AI-Researcher> | 2025 年前的整体式系统之一 | [§1](README.md#1-2026-年发生了什么) |

## 学科适配层

| 名称 | 类型 | 机构 | 链接 | 一句话 | 正文位置 |
|---|---|---|---|---|---|
| scientific-agent-skills | 项目 | K-Dense | <https://github.com/K-Dense-AI/scientific-agent-skills> | 165 个科研 skill，偏生命科学 | [§8.3](README.md#k-dense-scientific-agent-skills) |
| science-skills | 项目 | Google DeepMind | <https://github.com/google-deepmind/science-skills> | 官方 skills 包，接 30+ 数据库，主打 grounding | [§8.3](README.md#deepmind-science-skills) |
| Awesome-Scientific-Skills | 项目 | InternScience | <https://github.com/InternScience/Awesome-Scientific-Skills> | 上海 AI Lab 策展的 skills 库 | [§8.3](README.md#awesome-scientific-skills) |
| Claw4Science | 论文 | — | <https://www.biorxiv.org/content/10.64898/2026.03.30.715118v1> | OpenClaw 科研生态的策展数据集 | [§8.3](README.md#claw4science-与-openclaw-科研生态) |
| ToolUniverse | 项目 | 哈佛 mims | <https://github.com/mims-harvard/ToolUniverse> | 600+ 科学工具统一接口 | [§8.3](README.md#工具层) |
| PaperQA2 | 项目 | FutureHouse | <https://github.com/Future-House/paper-qa> | 文献问答与合成 | [§8.3](README.md#工具层) |
| awesome-ai-for-science | 索引 | ai-boost | <https://github.com/ai-boost/awesome-ai-for-science> | AI for Science 项目索引 | 未在正文引用，备查 |

## 验证与评测层

| 名称 | 类型 | 机构 | 链接 | 一句话 | 正文位置 |
|---|---|---|---|---|---|
| ResearchClawBench | 基准 | 上海 AI Lab | <https://github.com/InternScience/ResearchClawBench> | 40 任务、10 学科、开放投任务、带稳定性统计 | [§8.4](README.md#researchclawbench) |
| ResearchClawBench 数据集 | 数据 | 上海 AI Lab | <https://huggingface.co/datasets/InternScience/ResearchClawBench> | HF 镜像，含 Self 额外 10 个任务 | [§8.4](README.md#researchclawbench) |
| ResearchClawBench 论文 | 论文 | 上海 AI Lab | <https://arxiv.org/abs/2606.07591> | 2026-06-09 | 脚注 researchclawbench-paper |
| AstaBench | 基准 | Ai2 | <https://allenai.org/asta/bench> | 2400+ 问题、四大类 | [§8.4](README.md#astabench) |
| AstaBench 论文 | 论文 | Ai2 | <https://arxiv.org/abs/2510.21652> | ICLR 2026 oral | 脚注 astabench-paper |
| AstaBench 2026 春季更新 | 博客 | Ai2 | <https://allenai.org/blog/astabench-update-spring-2026> | E2E-Bench-Hard 3% 的出处 | 脚注 astabench-update |
| PaperBench | 基准 | OpenAI | <https://arxiv.org/abs/2504.01848> | 复现 20 篇 ICML 论文，8316 个子任务 | 脚注 paperbench |
| Terminal-Bench Science | 基准 | Harbor | （原文未给链接） | 终端环境真实科研工作流 | [§8.4](README.md#其他基准) |
| NewtonBench | 基准 | HKUST | （原文未给链接） | 抗记忆的物理定律再发现 | [§8.4](README.md#其他基准) |
| Kosmos | 论文 | Edison Scientific | <https://arxiv.org/abs/2511.02824> | claim → evidence 可追溯性的参考 | 脚注 kosmos |

## 批评与综述

| 名称 | 类型 | 日期 | 链接 | 一句话 | 正文位置 |
|---|---|---|---|---|---|
| Autonomous Research Agents: A Survey of AI Scientists and the Verification Gap | 综述 | 2026-06-29 | <https://arxiv.org/abs/2608.05179> | 筛 125 纳 35，七个审计维度 | 脚注 verification-gap |
| Agentic AI Scientists Are Not Built For Autonomous Scientific Discovery | 论文 | 2026-05-09 | <https://arxiv.org/abs/2605.08956> | 四个结构性缺陷 | 脚注 not-built |
| Sibyl-AutoResearch | 论文 | 2026-05 | <https://arxiv.org/abs/2605.22343> | 要的是自进化试错 harness | 脚注 sibyl |
| AutoResearch AI | 综述 | 2026-05 | <https://arxiv.org/abs/2605.23204> | 2026 工具链综述 | 脚注 autoresearch-ai-survey |
| EvoScientist | 论文 | 2026-03 | <https://arxiv.org/abs/2603.08127> | 多智能体自进化 AI 科学家 | 脚注 evoscientist |
| ASI-Evolve | 论文 | 2026-03 | <https://arxiv.org/abs/2603.29640> | AI 加速 AI | 脚注 asi-evolve |
| ARIS | 论文 | 2026-05 | <https://arxiv.org/abs/2605.03042> | 对抗式多智能体科研 | 脚注 aris |
| Agon | 论文 | 2026-06 | <https://arxiv.org/abs/2606.24177> | 大规模全学科多智能体科研 | 脚注 agon |
| Clarus | 论文 | 2026-06 | <https://arxiv.org/abs/2606.30246> | web 级协作多智能体科研 | 脚注 clarus |

## 制度

| 名称 | 类型 | 链接 | 一句话 | 正文位置 |
|---|---|---|---|---|
| Agents4Science | 会议 | <https://agents4science.stanford.edu> | 专门接收 AI 作者论文的会议 | 脚注 agents4science |
| JAIGP | 期刊 | （原文未给链接） | 2026-02 创刊，AI 作者期刊 | [§9](README.md#9-制度约束与项目定位) |

## 原文里没有来源的说法

| 说法 | 位置 | 处理 |
|---|---|---|
| 含幻觉引用的论文比例从 2024 年的 0.3% 升到 2025 年的 2.6% | §6.2 | 原文只写"一篇 2026 年的分析"，未给链接；保留原句、不挂脚注，待补来源 |
| Google Co-Scientist 正式论文（2026-06-29） | §11 时间线 | 原文未给链接，待补 |
