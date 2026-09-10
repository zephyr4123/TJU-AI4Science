# 未决项

- 最近变更：2026-09-10

纲领里还没定的事，一项一个编号。每项写清问题、候选方案与依据、建议、谁拍板。定了就把结论搬进对应文件，这里改成"已定，见 xxx"。每项一条 issue，见表末列。

| 编号 | 问题 | 层 | 建议 | 拍板 | issue |
|---|---|---|---|---|---|
| Q-1 | 阶段切几段 | 流水线 | 7 段，platform 0.2.0 只做 4 段 | 主人 | [#8](https://github.com/zephyr4123/TJU-AI4Science/issues/8) |
| Q-2 | skills 怎么注入底座 | 学科适配 | 交给底座原生机制，不自研匹配器 | 主人 | [#9](https://github.com/zephyr4123/TJU-AI4Science/issues/9) |
| Q-3 | 验收怎么定义 | 验证 | manifest.requirements 的 must_pass + 零 LLM 判据；discussion 类交隔离裁判 | 主人 | [#10](https://github.com/zephyr4123/TJU-AI4Science/issues/10) |
| Q-4 | 评测怎么做 | 评测 | rubric 树 + 组件消融 + 噪声基线；首个工科 bench 3 到 5 题 | 主人 | [#11](https://github.com/zephyr4123/TJU-AI4Science/issues/11) |
| Q-5 | 第一个真任务与学院 | 任务 | 先用玩具任务把闭环跑通，不等 | 主人 | [#12](https://github.com/zephyr4123/TJU-AI4Science/issues/12) |
| Q-6 | 执行环境 | 底座 / 工具 | platform 0.2.0 本机 venv 独立进程；docker 与集群按需 | 主人 | [#13](https://github.com/zephyr4123/TJU-AI4Science/issues/13) |
| Q-7 | 人在环第一版做到哪 | 流水线 | full-auto + gate-only | 主人 | [#14](https://github.com/zephyr4123/TJU-AI4Science/issues/14) |
| Q-8 | 首批支持哪几个 CLI | 底座 | Claude Code 先行，Codex 第二 | 主人 | [#15](https://github.com/zephyr4123/TJU-AI4Science/issues/15) |
| Q-9 | 跨 run 记忆要不要做 | 学科适配 | v0.x 不做，账本与 git 就是记忆 | 主人 | [#16](https://github.com/zephyr4123/TJU-AI4Science/issues/16) |

## Q-1 阶段切几段

AutoResearchClaw 的 23 段太细（大量阶段是一次 LLM 调用），InternAgent 的 3 段太粗（想法生成一个阶段里塞了 9 个 agent）。建议 7 段：文献、假设、设计、实验、分析、写作、验证。platform 0.2.0 只做设计、实验、分析、验证四段。

## Q-2 skills 怎么注入底座

候选：
1. **交给底座原生机制**。领域包的 `skills/` 目录与 Claude Code 原生 SKILL.md 同格式，运行底座时把它挂进会话的 skill 搜索路径，由底座自己按需加载。零框架代码。
2. **框架按阶段选 skill 塞进 prompt**。AutoResearchClaw 走的是这条，它的匹配器因为分词 bug 在主路径上什么都匹配不到，真正生效的是无差别灌前 5 条。

建议 1。依据：[AutoResearchClaw 深读 §6.2](../../research/selection/2026-0909-pipeline-frameworks/autoresearchclaw.md#62-自进化在默认配置下不存在)。风险：换一个不支持 skill 的底座时这层失效，届时再做方案 2 的最简版（按 `applicable-stages` 字段整文件追加，不做关键词匹配）。

## Q-3 验收怎么定义

"验收"有两层：单次运行的验收（这次跑出来的东西能不能信）和版本的验收（这一版做完没有）。

- 单次运行：manifest 的 `requirements` 逐条判。`numeric` 与 `artifact` 类由框架确定性判；`discussion` 类由隔离裁判判并给出证据引用。三条零 LLM 判据（数字回溯、引用真伪、图源）永远在。
- 版本：spec 里的 A-n，尽量一条命令能查。

依据：AutoResearchClaw 的 `requirements_judge` 形状，但它只在 agent 模式生效、重试只有 1 次、裁决者不隔离（[§7.2](../../research/selection/2026-0909-pipeline-frameworks/autoresearchclaw.md#72-arc-bench整仓最扎实的部分)）。

## Q-4 评测怎么做

评测层评的是框架本身，不是单篇。候选形态：
- **rubric 树**：ARC-Bench 的加权递归树（叶子带 `task_category` 与 `judging_note`），LLM 判官旁边必须有确定性信号（从 `results.json` 算零方差、std/mean 比）。
- **组件消融**：开关统计门、开关 harness 校验、开关隔离裁判，看结果差多少。这是我们相对三个仓最能讲出故事的实验：它们的护栏一半没通电。
- **噪声基线**：同配置重复 k 次报 σ，任何"改进"先跟 σ 比。

建议先做噪声基线与消融，rubric 树等第一个真任务定了再写。首个工科 bench 目标 3 到 5 题。

## Q-5 第一个真任务与学院

人和领域的决定，读框架读不出来。建议不等：先用玩具任务（30 秒的 MLP 回归，或一根悬臂梁的有限元）把闭环跑通，学院定了换任务目录，循环不动。真任务要满足的条件：能在几分钟内跑完一次、能压成一个对离散化不变的标量、基线代码能整理成单入口。

## Q-6 执行环境

platform 0.2.0 本机 venv 里起独立进程，隔离只到进程级；docker 模式在 harness 需要装东西时再加；集群按 ADR-0001 的判据到时候拆仓。AutoResearchClaw 的教训：docker 不可用时静默降级成裸进程是错的，隔离降级必须显式失败。

## Q-7 人在环第一版做到哪

full-auto 与 gate-only 两种。co-pilot（协作改假设、共写论文）的价值没证据，AutoResearchClaw 的 workshops 是空壳。

## Q-8 首批支持哪几个 CLI

Claude Code 先行（本机有、flag 已对账），Codex 第二（本机有、flag 未对账）。每加一个适配器必须带真 CLI 冒烟测试。

## Q-9 跨 run 记忆

三个仓的记忆层：InternAgent 默认配置下断的，AutoResearchClaw 接线是坏的，autoresearch 只写不读。v0.x 不做专门的记忆层，账本 + git log + 上一轮的 `analysis.md` 就是记忆；`agenthub` 那种"读前沿、查 children 避免重复"的做法等多 agent 并行时再考虑。

## 变更记录

| 日期 | 改了什么 | 为什么 | 认可 |
|---|---|---|---|
| 2026-09-10 | 建档，九项 | 三层未定，先把问题与候选写下来 | 主人 + Claude |
