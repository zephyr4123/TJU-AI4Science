---
title: POPPER 方法深读
subtitle: 假设阶段候选 · 自由文本假设拆成子假设逐个证伪，p 值转 e 值连乘控一类错误；只摘方法，逐条对论文与代码
kind: 开源项目方法深读（只读论文与代码，不跑、不装依赖）
date: 2026-09-27
scope: 仓库 https://github.com/snap-stanford/POPPER，浅克隆到 vendor/POPPER，提交 5961186（2025-05-14，main 最新一次提交）；论文 arXiv 2502.09858 v1（PDF 元数据标 ICML 2025，65 页含附录），原件与解析稿在外层 materials/research/2026-0927-scientific-ai-capabilities/papers/；读了 popper/ 全部、benchmark_scripts/ 全部、baseline_agents/ 入口、demo.ipynb 的输出、GitHub issue、PyPI 与 Harvard Dataverse 元数据；没下载 2.27 GB 的数据存档。同日复查逐条核对了 文件:行，补读 demo cells[4] 里 22 张表的列、论文附录 I 的轨迹（图 9–11）与 PyPI 0.0.5 sdist 同 HEAD 的差异。POPPER 的 文件:行 相对该仓库根，平台的 文件:行 相对内仓 platform/（提交 de3d948）。对应外层 issue #181（项目）、#182（本篇）
status: 第一版
---

> **结论先行**：POPPER 不生成假设，只验证一个给定的自由文本假设。它的方法拆开是四件：（1）一段设计 prompt，每轮把主假设翻成一条带 h0 / h1 的子假设，并要求模型自问「主假设为空时子假设是否也为空」；（2）一次只看提案与主假设的 LLM 相关性打分，低于 0.8 丢弃重设计；（3）一个 ReAct + Python REPL 的执行 agent，在预载的 DataFrame 上跑检验，最后由另一次 LLM 调用从自由文本里读出 p 值；（4）p 值按 e = 0.5·p^(−0.5) 转成 e 值连乘，超过 1/α 就停并判「通过」，否则到预算为止。第（4）件是十行 numpy、零模型（`popper/agent.py:131-139`），demo 输出里的累计值 9.41 → 345.07 用这条式子能逐位复算。
>
> 证据：论文表 3 在三个基准上报一类错误 0.103 / 0.082 / 0.085（α = 0.1），功效 0.638 / 0.580 / 0.591；换成 Fisher 合并后一类错误升到 0.311 / 0.264 / 0.173，去掉相关性检查升到 0.134 / 0.340 / 0.300。理论依据是定理 4（非负超鞅 + 可选停止 + Markov 不等式），前提是三条假设。
>
> 与论文对不上或论文没讲的：公共 API `Popper.validate` 返回的 True / False 是总结 LLM 写出来再被解析的，把 e 值判定写回结果的那行被注释掉了（`popper/agent.py:1051`），只有基准脚本读的是 e 值判定；设计 agent 看得到每张表一行真实数据；执行 agent 先看数据再选检验，同一张表可以在多轮里反复用，这与假设 2 的关系论文没讨论。一类错误的负例全部靠置换造，五次重复用的是同一份置换数据；DiscoveryBench 是逐列独立置换，TargetVal 的置换代码（`popper/utils.py:160-167`）每列换一个种子、种子按 42·2^k mod 2^31 递推，从第 31 列起全是 0，按 demo 输出的列数，22 张表里至少 19 张表各自的所有列共用同一个排列，只打乱了行序、行内关联原样保留，这与论文「ensuring the null hypothesis holds」（§4）对不上（读代码推算，未运行，见 [1.7](#17-数据要长什么样基准数据集)）。消融「去掉相关性检查」走的代码分支在 HEAD 与 PyPI 0.0.5 里调设计 agent 时没传日志字典，读代码会抛 TypeError（见 [4.6](#46-实现层面的问题读代码得出未运行)），表 3 这一行没法用仓库代码复现。
>
> 平台一侧：它落在假设阶段（主文件还没定）；e 值累计与停止规则是确定性算术，形状对应框架的判定层；相关性检查的输入形状与 P-2 的隔离评审一致；执行 agent 要交互式跑 Python，而平台执行层的 Bash 只放行 `ai4sci skill`，两边形状不同。许可证：仓库没有 LICENSE 文件，只有 setup.py 与 PyPI 元数据写着 MIT，包里没有许可证正文。
>
> 怎么读：第 0 节是画像，第 1 到 5 节依次回答 #181 的五个问题。本文不下「接 / 不接」的结论；横向对比见同目录的 [README.md](README.md)。

## 0. 仓库与论文画像

| 项 | 实况 | 证据 |
|---|---|---|
| 论文 | Huang、Jin、Li、Li、Candès、Leskovec（斯坦福 CS / 统计、哈佛），arXiv 只有 v1（2025-02-14），PDF 元数据标 ICML 2025 | 论文首页[^paper] |
| 仓库 | 289 star、32 fork、6 个未关 issue（含 1 个 PR）、33 个提交；2025-01-28 从私有仓迁出，最后一次提交 2025-05-14，之后没有动静；没有 release | GitHub API[^repo] |
| 规模 | 38 个文件，Python 5187 行：核心 `popper/agent.py` 1052 行，其余是提示词、数据加载、ReAct 执行器、本机模型的 OpenAI 兼容封装（`popper/llm/`）、基准与基线脚本；没有测试、没有 CI | `git ls-files`、`wc -l` |
| 依赖 | langchain 0.3.7、langchain_core 0.3.22、langchain_experimental 0.3.3（ReAct 执行器的 Python REPL 工具出自这里）、langgraph 0.2.39、langchain_anthropic 0.2.3、langchain_openai 0.2.11、openai 1.61.0、pydantic 2.9.2、numpy 1.26.4、scipy 1.13.1；pandas、scikit-learn、gradio、tqdm、ipython 不钉版本 | `requirements.txt:1-15`、`popper/react_utils.py:6` |
| 分发 | PyPI `popper_agent` 0.0.5（2025-04-26，只有 sdist），比 main 少最后一次提交（还会调 mermaid.ink 画图） | PyPI[^pypi]、sdist 与 HEAD 的 diff |
| 数据 | Harvard Dataverse 一个 2.27 GB 的 tar.gz，首次 `register_data` 自动下载 | `popper/popper.py:44-46`、`popper/popper.py:250-253`、Dataverse[^dataverse] |
| 许可证 | 仓库无 LICENSE；`setup.py` 写 `license='MIT'`；`version.py` 文件头写着「Based on NiLearn package / License: simplified BSD」 | `setup.py:28`、`popper/version.py:2-3`，详见 [4.4](#44-许可证) |

一次验证的流程（`popper/agent.py:1015-1027` 建的 LangGraph 图，加上 `go()` 里的预算检查）：

```
自由文本假设 H
   │
   ▼
设计 agent ── 一次模型调用：prompt 让它在一段输出里自己写「提案—批评—反思」几轮，
   ▲          再用第二次调用抽出结构化字段：名称 / 描述 / h0 / h1
   │                │
   │                ▼
   │        相关性检查 ── LLM 按 0.1–1.0 打分，只看子假设与主假设；< 0.8 进失败清单、重设计
   │                │ 通过
   │                ▼
   │        执行 agent ── ReAct + Python REPL，全部数据表预载成 DataFrame，最多 25 步，
   │                │     输出一段自由文本 Final Answer
   │                ▼
   │        p 值读取 ── 另一次 LLM 调用从文本里读 p；缺失、NaN、恰为 0 → 重试，重试用完进失败清单
   │                │ p_i
   │                ▼
   │        序贯判定 ── e_i = 0.5 · p_i^(−0.5)，E_i = e_1 · … · e_i
   │                │
   └── E_i ≤ 10 且没超预算 ◄──┤
  （上几轮的检验与 p 值、失败清单喂回设计）
                    │ E_i > 1/α（α = 0.1 时即 10），或预算用完
                    ▼
            总结 LLM 写五栏结论 → 再解析成结构化字段（含 True / False）
```

## 1. 方法是什么

### 1.1 问题的形式化

论文把假设 H 定义为「变量集合 V 在情境 c 下的关系 r」，配一个零假设 H0；验证任务是一个映射 f: H → {0, 1}，0 是「未验证」，1 是「验证（拒绝 H0）」。评价标准是一类错误 sup P(ŷ = 1)（H0 为真时误判为 1 的概率）控制在 α 以内，在此前提下比较功效 P(ŷ = 1)（§2.1[^paper]）。

这里有一个容易读错的地方：输出只有「验证 / 未验证」两态，没有「证伪」这一态。POPPER 名字里的「证伪」指的是每一轮去拒绝子假设的零假设 h0，拒绝得够多就拒绝主假设的 H0（§2.2）。代码与之一致：图里只有「判定通过 → 总结」和「没通过 → 回设计」两条边（`popper/agent.py:994-1002`），总结 prompt 要求「没拒绝零假设就输出 False」（`popper/prompt_utils.py:193`），这个 False 的含义是「未验证」，不是「假设为假」。

### 1.2 把自由文本假设拆成可证伪的子假设

| 要点 | 论文 | 代码 | 证据 |
|---|---|---|---|
| 每轮产一条子假设 | 设计 agent 拿到主假设、前几轮的子假设与 p 值、数据库元数据，产出一条子假设及其 h0、h1、做法（§2.4、§3） | 结构化输出四个字段：`test_name`、`test_description`、`null_hypothesis`、`alternate_hypothesis` | `popper/agent.py:78-84`、`popper/agent.py:796-803` |
| 蕴含约束 | 假设 1：H0 为真则每个 h0 都为真（§2.3） | 写成 prompt 里的硬性要求与自检问题：「if the main hypotheiss is null, then the falsification sub-hypothesis should also be null」，批评环节第一问就是它 | `popper/prompt_utils.py:135`、`popper/prompt_utils.py:168` |
| 自我精炼 | 按新颖、可实现、蕴含三条迭代改进（§3，引 Self-Refine） | 一次 `create_react_agent(llm, [])` 调用（没有工具，模型回一次就结束），prompt 让模型在同一段输出里自己写几轮「批评—反思」；随后第二次调用把最后一段解析成结构化字段，失败最多重试 10 次 | `popper/agent.py:785-800`、`popper/prompt_utils.py:164-172` |
| 历史回喂 | 设计时可以用 D_{i−1}（假设 2） | 已通过的检验连同 p 值、失败清单（相关性不过的与执行失败的）原样拼进 prompt，要求不重复 | `popper/agent.py:922`、`popper/agent.py:782`、`popper/prompt_utils.py:147-159` |
| 设计时看得到什么 | 「只看 schema，不看原始数据或汇总统计」（§3） | 拿到的 `data_desc` 是每张表的列名加**第一行的真实值**；论文附录 I 的 prompt 原文也写着「columns and example rows」 | `popper/utils.py:119`、`popper/utils.py:212-215`、`popper/utils.py:323`、`popper/prompt_utils.py:137` |
| 目标措辞 | — | 「A good falsification test should serve as a strong evidence for the main hypothesis … maximize the implication strength」 | `popper/prompt_utils.py:161-162` |

最后一行措辞被外部审计（[2.6](#26-外部审计-issue-10-的核对)）读成「在找支持而不是找反驳」。按论文的形式化，一轮子检验拒绝 h0 本来就是给主假设的备择加证据，这句话与 §2.2 的定义不矛盾；它要求的是「蕴含强」，不是「结果显著」。两种读法都记在这里，不裁决。

### 1.3 相关性检查

| 要点 | 内容 | 证据 |
|---|---|---|
| 作用 | 用 LLM 近似执行假设 1：估计子假设的 h0 被主假设 H0 蕴含的程度 R(h)，R(h) < r0 就丢弃（§3） | 论文 §3 |
| 输入 | 只有两段文字：「Subhypothesis: {提案}; Main hypothesis: {主假设}」。设计 agent 的推理过程不给它 | `popper/agent.py:926` |
| 打分 | 六档 rubric：1.0 / 0.8 / 0.6 / 0.4 / 0.2 / 0.1，附理由 | `popper/prompt_utils.py:200-218`、`popper/agent.py:105-111` |
| 阈值 | `< 0.8` 丢弃，写死；论文正文只写 r0「预先设定」，没给数 | `popper/agent.py:927` |
| 丢弃之后 | 提案进失败清单，下一次设计 prompt 里会看到它；同一次设计最多重来 `max_failed_tests` 次 | `popper/agent.py:924-930` |
| 随机性 | 检查器用 `get_llm` 的默认温度 0.7，同一提案两次打分可能不同 | `popper/utils.py:17`、`popper/agent.py:818`、`popper/agent.py:829` |

### 1.4 在数据上执行检验

仓库有两种执行器，论文主结果用 ReAct，CodeGen 是消融（表 3 的「POPPER-CodeGen」）。

| 要点 | ReAct 执行器（默认） | CodeGen 执行器（消融） | 证据 |
|---|---|---|---|
| 形态 | LangChain `AgentExecutor`，一个自定义 Python REPL 工具，命名空间在一次执行里跨步保留；每次执行前把全部 DataFrame 放进命名空间 | 结构化输出一段完整代码（前言、imports、正文），LangGraph 里「生成 → 检查 → 反思」循环 | `popper/react_utils.py:205-254`、`popper/react_agent.py:154-181`；`popper/agent.py:190-607` |
| 步数与时间 | 最多 25 步；**没有超时** | 最多 `max_retry` 轮；代码在子进程跑，超时 `time_limit` 分钟 | `popper/react_agent.py:76`；`popper/agent.py:374-394` |
| 输出约定 | 必须给一个 p 值、科学计数；多个 p 值要自己合并；找不到有效 p 值就报 1.00e+00；p 值与结论方向要一致（拒绝了 h0 但效应方向不对时不许报 < 0.05）；「avoid p-hacking」 | 必须输出一个 p 值；不许占位符 | `popper/react_utils.py:32-36`、`popper/react_utils.py:136-143`；`popper/prompt_utils.py:51-54` |
| p 值怎么读出来 | 另一次 LLM 调用（温度 0）读 Final Answer，返回「有没有 p 值」和 p 值字符串 | 同样由 LLM 读子进程的 stdout | `popper/agent.py:623-633`、`popper/agent.py:687-698`；`popper/agent.py:457-464` |
| 什么算失败 | 没输出、读不出 p、p 为 NaN、p 恰为 0，重试 `max_retry` 次后记失败；不检查 p 是否落在 (0, 1] | 同上（p 恰为 0 的报错写「supposedly wrong」），另加 import 失败、超时、LLM 判定「编造数据」 | `popper/agent.py:677-738`；`popper/agent.py:323-349`、`popper/agent.py:481-505` |
| 在哪跑 | 宿主进程里 `exec` | imports 在主进程 `exec`，正文在子进程 | `popper/react_utils.py:242`；`popper/agent.py:325`、`popper/agent.py:365` |

执行 agent 选什么统计检验、用哪几列当代理变量，都是它在 REPL 里看过数据之后自己定的；论文把这写成能力：「Without explicit prompting, it selects suitable tests based on the data distribution」（§3），附录 E 表 6 把轨迹归成 Inspect Dataset、Visualize Data、Implement Test、Inspect Test 等 11 类动作。

### 1.5 e 值序贯检验与一类错误控制

**式子**。论文用 Vovk & Wang 的 p-to-e 校准器[^vovk]：e_i = κ · p_i^(κ−1)，κ ∈ (0, 1)（§2.4 式 1）；累计 E_i = e_1 · … · e_i；E_i ≥ 1/α 就拒绝 H0（§2.4、定理 4）。只要每个 p_i 在给定前几轮数据时仍然有效，即 P(p_i ≤ t | D_{i−1}) ≤ t，就有 E[e_i | D_{i−1}] ≤ 1。

**代码**。`e_value_kappa_calibrator` 就是这条式子，κ 写死 0.5，`configure` 不暴露；判定用 `cum_e > 1/alpha`（`popper/agent.py:131-139`、`popper/agent.py:972`）。每成功一轮就对全部历史 p 值重算一次连乘（`popper/agent.py:964-983`）。论文正文没写 κ 取多少，但 demo、附录 I 轨迹与表 1 的数都与 κ = 0.5 对得上：

| 核对对象 | 原始 p 值 | 按 κ = 0.5 复算 | 原文 | 证据 |
|---|---|---|---|---|
| demo 第 1 轮 | 0.002822 | 9.412 | 9.412207643723193 | `demo.ipynb` 的 cells[10] 输出 |
| demo 第 2 轮累计 | 0.000186 | 9.412 × 36.66 = 345.07 | 345.06827423348386 | 同上 |
| 附录 I 图 9（o1）第 1 轮 | 0.031 | 2.8398 | 2.8398091712353244 | 论文附录 I 图 9 |
| 附录 I 图 10 第 1 轮 | 1.0（执行 agent 说找不到数据，按约定报 1.00e+00） | 0.5 | 0.5 | 论文附录 I 图 10 |
| 表 1 第 1、2 轮 | 1.0、8.8e-3 | 0.5、0.5 × 5.33 = 2.67 | 0.5、2.67 | 论文表 1 |
| 表 1 第 4 轮 | 第 3 轮为「-」，第 4 轮 4.7e-4 | 不计第 3 轮：61.46；把第 3 轮按 p = 1（e = 0.5）计入：30.73 | 30.78 | 论文表 1 |

表 1 最后一行只有把第 3 轮当 e = 0.5 乘进去才对得上（30.73 与 30.78 的差在表中 p 值两位有效数字的舍入范围内）。代码里有两种轮：执行失败的轮进失败清单、不进连乘（`popper/agent.py:942-945`）；执行 agent 按 prompt「找不到有效 p 值就报 1.00e+00」（`popper/react_utils.py:142`）报了 1 的轮算成功轮，e = 0.5 进连乘，图 10 第 1 轮就是这种。表 1 的「-」是哪一种，论文没说；若是后一种，表与代码一致，若是前一种则不一致。见 [第 5 节](#5-还没弄清的问题)。

**κ = 0.5 时这条式子的性质**（按式子算出，不是论文陈述）：

| 单轮 p 值 | e 值 | 对累计值的作用 |
|---|---|---|
| 1.0（执行 agent「找不到有效 p 值」时报的值） | 0.5 | 累计值减半 |
| 0.25 | 1.0 | 不变 |
| 0.05 | 2.24 | |
| 0.01 | 5.0 | |
| 0.0025 | 10.0 | 恰好等于 1/α；判定是严格大于（`popper/agent.py:136`），α = 0.1 时一轮通过要 p < 0.0025 |

要在 n 轮里靠相同的 p 值攒过 10：n = 1 需要 p < 0.0025，n = 2 需要 p < 0.025，n = 3 需要 p < 0.054，n = 5 需要 p < 约 0.0995。p > 0.25 的轮会把累计值往下拉，所以「没找到证据」的轮不是零成本的。

**同一处代码里的另外三种合并方式**（都能用 `aggregate_test` 切换）：

| 方式 | 实现 | 论文里的角色 | 证据 |
|---|---|---|---|
| Fisher 合并 | −2 Σ ln p 对 χ²(2n) 求合并 p 值，< α 就停 | 消融「Fisher Combined Test」；脚注 1 说它要求独立且不能可选停止 | `popper/agent.py:151-163` |
| LLM 估似然比 | 另起一个 agent 估 P(data given h1) 与 P(data given h0)，连乘比值 | 消融「LLM-Likelihood ratio」 | `popper/agent.py:123-129`、`popper/agent.py:741-764`、`popper/prompt_utils.py:82-122` |
| 积分校准器 | e = (1 − p + p ln p) / (p (−ln p)²) | 论文没用 | `popper/agent.py:141-149` |
| 序贯概率比检验 | 注释掉的旧代码 | 论文没提 | `popper/agent.py:172-187` |

### 1.6 什么时候停

| 条件 | 触发后 | 证据 |
|---|---|---|
| 累计 e 值 > 1/α | 判「通过」，转总结 | `popper/agent.py:136-137`、`popper/agent.py:994-1000` |
| 成功完成的检验数达到 `max_num_of_tests`（`Popper.configure` 默认 5；底层类默认 10） | `go()` 打断图的流、直接总结 | `popper/agent.py:1043-1048`、`popper/popper.py:75`、`popper/agent.py:884` |
| 失败提案累计达到 `max_failed_tests`（相关性不过的 + 执行失败的；底层类默认 10；`Popper.configure` 的参数表里没有，但 `Popper(**kwargs)` 会原样转给底层 `configure`；DiscoveryBench 脚本把它设成与轮数上限相同） | 同上 | `popper/agent.py:885`、`popper/agent.py:928`、`popper/agent.py:944`、`popper/agent.py:1043`、`popper/popper.py:16`、`popper/popper.py:104`、`benchmark_scripts/run_discovery_bench.py:90` |
| 单个检验执行重试 `max_retry` 次仍失败（`Popper.configure` 默认 5） | 进失败清单，回设计 | `popper/agent.py:677`、`popper/agent.py:730-738`、`popper/popper.py:76` |
| 单次 ReAct 执行满 25 步 | 结束这次执行 | `popper/react_agent.py:76`、`popper/react_utils.py:289-296` |

与论文算法 1 的差别：算法 1 的外层循环 i = 1..N_max 数的是**所有轮**（含相关性不过和执行失败的轮），代码把成功轮与失败轮分开计数、各有上限（附录 A.1、`popper/agent.py:1043`）。停止规则只依赖累计 e 值与计数，符合假设 3「停止时刻是关于已用数据的停时」的形状（§2.3）。

### 1.7 数据要长什么样（基准数据集）

方法对数据的要求（代码层面）：若干张能读成 pandas DataFrame 的表，全部读进内存；列名要能让模型看懂，因为设计 agent 只拿到列名与一行样例；数据是「与假设无关」的大库，事先没为某个假设准备（§3）。

| 数据 | 形状 | 证据 |
|---|---|---|
| TargetVal 数据库 | 22 张 pkl 表，变量名 `df_<表名>`：GTEx 组织表达、GWAS Catalog、基因注释、BioGRID 各类互作（亲和捕获、双杂交、合成致死等）、GeneBASS 三类变异负担、UK Biobank eQTL / pQTL / sQTL、变异表、性状表；论文说合计约 8500 万条记录 | `popper/utils.py:46-69`、§3 |
| TargetVal 假设 | 模板「Gene {gene} regulates the production of Interleukin-2 (IL-2).」与 IFN-γ 版；真值表 `benchmark/targetval/ground_truth_{IL2,IFNG}.csv`，以基因为索引、带 `Score` 列（来自 Schmidt 等 2022 的 CRISPR 筛选，§3） | `popper/benchmark.py:17-30` |
| TargetVal 正例与负例 | 正例 = 按 \|Score\| 排序取最大的 N 个基因（跑分用 20 个）；负例 = 随机抽 N 个基因（跑分用 50 个，`random_state=42`）配**置换过的数据**，标签恒为 False | `popper/benchmark.py:28-37`、`benchmark_scripts/run_targetval.sh:8-9` |
| 置换怎么做（TargetVal） | 只载 3 张默认表时（基线脚本走这条）：只打乱 GTEx 与 GWAS 表里的基因列。全部 22 张表时（POPPER 的基准脚本带 `--use_full_data` 走这条）：逐列 `sample(frac=1, random_state=种子)`，种子从 42 起每列乘 2 再模 2^31，跨表累计不重置；42·2^k 在 k ≥ 30 时模 2^31 为 0，所以第 31 列起每一列的种子都是 0。同一张表行数相同，种子相同就得到同一个排列，这些列一起换行、行内关联不变。demo 输出里表的顺序与代码一致，列数是 GTEx 4 列、GWAS Catalog 超过 20 列（显示被截断）、gene_info 13 列，之后 19 张表 2–9 列不等。种子不同的只有累计前 30 列，即 GTEx 4 列加 GWAS 表开头的 26 列（GWAS 不足 26 列时再加上 gene_info 开头几列）；从 BioGRID genetic_interaction 起的 19 张表（BioGRID 各类、GeneBASS、UKBB QTL、变异表、性状表）全部列、gene_info 的大部分列只是行序被打乱，基因与表型、p 值的对应原样保留。另外赋值时 pandas 按索引对齐，而 demo 里 BioGRID 各表与 sQTL 表第一行的索引是 96170、1935001 这类大数，若这些表的索引不是 0 到 n−1，索引落在范围外的行会整行变成 NaN，剩下的行行内关联照样保留（读代码与 demo 输出推算，未运行，没下载数据核实索引） | `popper/utils.py:136-167`、`benchmark_scripts/run_targetval.sh:9`、`benchmark_scripts/run_targetval_benchmark.py:38-45`、`demo.ipynb` 的 cells[4] 输出 |
| DiscoveryBench | allenai 的数据集[^discoverybench]：每个任务一个目录，`metadata_<id>.json` 带领域、数据集（文件名、描述、每列名称与描述）、问题；CSV 数据文件；答案表每行（数据集、metadataid、query_id、gold_hypo）。论文用去重后 86 条非空假设（§3） | `popper/utils.py:188-222`、`popper/benchmark.py:100-161` |
| DiscoveryBench 的正负例 | 每条假设出两次：原数据标 True，逐列置换过的数据标 False；读的是 `answer_key/answer_key_real_cleaned_1.csv`，并跳过 `non-trivially falsifiable == 0` 的行。上游仓库真实数据的答案表是 `eval/answer_key_real.csv`（列只有 dataset、metadataid、query_id、gold_hypo），没有 `answer_key/` 目录、`answer_key_real_cleaned_1.csv` 文件与这一列，这三样是 POPPER 自己的 | `popper/benchmark.py:102`、`popper/benchmark.py:133-161`、`popper/utils.py:234-239` |
| 自己的数据 | 一个目录里的 `*.pkl`（必须是 DataFrame）与 `*.csv`，变量名 `df_<文件名>`，描述只有列名与第一行 | `popper/utils.py:275-324` |
| 存档 | 2,271,481,285 字节的 `popper_data_processed.tar.gz`，解到 `data_path` 下有 `bio_database/`（及 `benchmark/`）；demo 用同一个路径去读 DiscoveryBench，推断存档里也有它与答案表，**没下载核实** | `popper/popper.py:44-47`、`popper/popper.py:250-271`、`demo.ipynb` 的 cells[12]、Dataverse[^dataverse] |

## 2. 为什么有效

### 2.1 理论：定理 4 与三条假设

| 假设 | 内容（§2.3） | 实现里靠什么近似 |
|---|---|---|
| 1 蕴含 | H0 为真则每一轮的 h0 都为真 | 设计 prompt 里的自检问题（`popper/prompt_utils.py:168`）+ LLM 相关性检查（`popper/agent.py:927`） |
| 2 序贯信息 | agent 的训练与 D 无关；E[e_i given D_{i−1}] ≤ 1 在 h0_i 下成立。充分条件是：选 h0_i 与检验函数 f_i 时只用 D_{i−1} 与元数据，不碰还没用的数据；f_i 在固定的 h 下期望 ≤ 1 | 论文说靠「设计 agent 只看元数据」满足（§3）；p 值本身有效靠执行 agent 选对检验 |
| 3 可选停止 | 停止时刻 τ 是关于 F_i = σ(D_i) 的停时 | 只按累计 e 值和计数停（`popper/agent.py:994-1002`、`popper/agent.py:1043`） |

定理 4：三条都成立时，停止时的累计值 E 是有效 e 值，P(E ≥ 1/α) ≤ α。证明在附录 A.2：E_i 是非负超鞅，用 Doob 可选停止定理得 E[E] ≤ 1，再用 Markov 不等式。这是 e 值文献里的标准结果，论文注明「standard result」。

### 2.2 一类错误与功效的实证

设置：Claude 3.5 Sonnet；α = 0.1；DiscoveryBench 最多 3 轮、TargetVal 最多 5 轮；负例按论文说用逐列置换造出（DiscoveryBench 正负一样多，TargetVal 20 正 50 负；TargetVal 那条置换代码实际做了什么见 [1.7](#17-数据要长什么样基准数据集)）；一类错误 = 负例上判「验证」的比例，功效 = 正例上判「验证」的比例；5 次运行取均值与标准差（§4、表 3）。

| 实证 | 数 | 出处 |
|---|---|---|
| POPPER 一类错误 | DiscoveryBench 0.103 ± 0.020、TargetVal-IL2 0.082 ± 0.046、TargetVal-IFNG 0.085 ± 0.028 | 表 3 |
| POPPER 功效 | 0.638 ± 0.066、0.580 ± 0.125、0.591 ± 0.069 | 表 3 |
| 论文拿来比的基线 | DiscoveryBench 上是 ReAct 0.383（这一列唯一控住的基线），论文说 POPPER「高 66.5%」；TargetVal-IL2 上是 Self-Refine 0.183，论文说「3.17 倍」。同一列里 CodeGen (o1) 也控住了、功效 0.250 更高，论文没拿它比 | 表 3、§4.1 |
| 换骨干模型 | 一类错误（DiscoveryBench / IL2）：Haiku 3.5 0.230 / 0.780，Llama 3.3 70B 0.147 / 0.116，GPT-4o 0.143 / 0.096，Sonnet 3.5 0.103 / 0.082，o1 0.091 / 0.031 | 表 4 |
| α 扫描 | α = 0.10 / 0.15 / 0.20 时经验一类错误约 0.10 / 0.14 / 0.22（读图） | 图 4(1) |
| 预算扫描 | 最多 1 / 3 / 5 / 7 轮时功效约 0.20 / 0.55 / 0.60 / 0.65，一类错误约 0.02 / 0.10 / 0.02 / 0.16（读图） | 图 4(2) |
| 与人对照 | 9 位计算生物背景的参与者，TargetVal-IL2 抽 18 个任务（9 负 9 正）；一类错误 POPPER 1/9 = 11.1%、人 2/9 = 22.2%；功效都是 6/9 = 66.7%；耗时 POPPER 快 9.7 倍 | 图 2、附录 F |
| 相关性检查与人一致性 | 90 条提案，三位作者校准后 Kendall W = 0.91；检查器与人 Spearman 0.55、Kendall τ 0.43；检查器判「强相关」84%–85%，人 77% | §4.2、附录 G |
| 失败归因 | 128 条失败日志，o1 自动归类、人抽查 30 条一致率 93.3%：误读 p 值 35.9%、设计无效 28.1%、检验破坏蕴含 17.2%、实现错误 8.6%、找不到数据 7.0%、幻觉 1 例、未见 p-hacking | 附录 D、图 5、表 5 |

### 2.3 消融说明了什么

| 变体 | 一类错误（DB / IL2 / IFNG） | 功效 | 论文的解读 | 代码开关 |
|---|---|---|---|---|
| Fisher 合并 | 0.311 / 0.264 / 0.173 | 0.741 / 0.800 / 0.650（作废） | 逐轮看合并 p 值、达标就停，Fisher 不支持这种可选停止 | `popper/agent.py:151-163`、`popper/agent.py:967-968` |
| LLM 估似然比 | 0.152 / 0.016 / 0.180 | 0.428 / 0.185 / 0.357 | 没校准，时松时紧 | `popper/agent.py:900-902`、`popper/agent.py:951-959` |
| 去掉相关性检查 | 0.134 / 0.340 / 0.300 | 0.610 / 0.897 / 0.717 | 不相关的 h0 被拒会抬高一类错误，这是假设 1 在实证上的体现 | `popper/agent.py:923`、`popper/agent.py:935-937`；这条分支调设计 agent 时没传 `log`，读代码会在 `popper/agent.py:794` 抛 TypeError（见 [4.6](#46-实现层面的问题读代码得出未运行)） |
| CodeGen 执行器 | 0.140 / 0.105 / 0.090 | 0.544 / 0.526 / 0.450 | 论文推测是 ReAct 的推理让检验设计得更有效；与 POPPER（ReAct）比，POPPER 功效更高，一类错误也更低 | `popper/agent.py:907-910` |

四个开关都在代码里，与论文的消融一一对应；其中「去掉相关性检查」按 HEAD 与 PyPI 0.0.5 的代码跑不通（读代码，未运行），表 3 这一行出自哪一版代码不清楚。

### 2.4 证据本身的边界

下面每条都是可查的事实，影响的是「这些数能说明到什么程度」。

| 事实 | 影响什么 | 证据 |
|---|---|---|
| 「5 次独立运行」：脚本的 `--seed` 只拼进结果文件名，不设任何随机种子；置换种子固定 42，负例基因抽样 `random_state=42`，DiscoveryBench 抽样种子默认 1234 | 五次跑的是同一份置换数据、同一批负例，标准差只反映模型采样的波动 | `benchmark_scripts/run_targetval_benchmark.py:22`、`benchmark_scripts/run_targetval_benchmark.py:70-71`、`popper/utils.py:136`、`popper/utils.py:234-236`、`popper/benchmark.py:36`、`popper/benchmark.py:86` |
| 负例只有一种构造：置换。DiscoveryBench 是逐列独立置换，表内关联都被打掉；TargetVal 按 HEAD 代码，至少 19 / 22 张表只被打乱了行序，行内关联原样保留（见 [1.7](#17-数据要长什么样基准数据集)） | DiscoveryBench 上覆盖的是「数据里什么关系都没有」，「H 为假但数据里有混杂相关」这类零假设没被测到（推断）。TargetVal 的负例不满足论文说的「ensuring the null hypothesis holds」：随机抽到的负例基因在 GeneBASS、QTL、BioGRID 等表里的真实关联还在，表 3 TargetVal 两列的一类错误测的不是论文描述的那个量；数值因此偏高还是偏低，从代码判断不了（读代码推算，未运行） | `popper/utils.py:160-167`、`popper/utils.py:234-239`、`popper/benchmark.py:36`、§4 |
| 判「控住」的规则是「α 落在均值 ± 1 个标准差内」 | 均值 0.103 也算控住；Self-Refine 在 DiscoveryBench 上 0.117 ± 0.028 按这条规则应判控住，表里标了 ✗；POPPER-NoReleCheck 在 DiscoveryBench 上标 ✗ 但功效 0.610 没有置灰 | 表 3 表注与标记 |
| 图 4(2) 最多 7 轮时一类错误约 0.16，在 0.1 虚线之上；正文写「Type-I error remained well-controlled」 | 预算放大时的控制情况，正文与图不一致；图注没说是哪个基准、几次运行 | 图 4、§4.2 |
| 附录 I 图 9 注：o1 因速率限制，执行层只能用 CodeGen，图 9 的轨迹里也是 CodeGen 的输出格式；`run_targetval.sh` 给 o1 传的是 `--react`，但 HEAD 的 ReAct 执行器只把 `claude-` 与 `gpt-` 开头的名字当云端模型，`o1-2024-12-17` 会走本机分支、没传端口就断言失败 | 按 HEAD 代码，脚本里 o1 + ReAct 那两行跑不起来（读代码，未运行）；图 9 注与代码都指向 CodeGen，但表 4 的 o1 一行用哪种执行器，论文没写，这一行可能混进了执行器差异 | 附录 I 图 9、`benchmark_scripts/run_targetval.sh:36-37`、`popper/react_agent.py:83-88`、`popper/react_agent.py:142-144` |
| DiscoveryBench 最多轮数：论文写 3，`run_discoverybench.sh` 与 `run_discoverybench_docker.sh` 都传 5（脚本默认 3）；这个脚本还把失败提案上限设成与轮数相同 | 复现时轮数要自己定 | §4、`benchmark_scripts/run_discoverybench.sh:2`、`benchmark_scripts/run_discoverybench_docker.sh:11`、`benchmark_scripts/run_discovery_bench.py:22`、`benchmark_scripts/run_discovery_bench.py:90` |
| DiscoveryBench 脚本里抛异常的样例只记错误，不进 `predictions` / `targets`；指标按跑完的样例算 | 出错的样例从一类错误与功效的分母里消失，出错率论文没报 | `benchmark_scripts/run_discovery_bench.py:95-96`、`benchmark_scripts/run_discovery_bench.py:109-120`、`benchmark_scripts/run_discovery_bench.py:139` |
| TargetVal 正例是 CRISPR 筛选里 \|Score\| 最大的 20 个基因 | 功效是在最强的信号上测的 | `popper/benchmark.py:28-34` |
| 样本量小：TargetVal 每次 50 个负例，一个负例 = 2 个百分点；与人对照每项 9 个任务 | 与人「没有显著差异」是在 9 个任务上说的，论文自己也写了样本小 | `benchmark_scripts/run_targetval.sh:9`、附录 F、§4.1 |
| 基线可复现性：coder / react 基线读 `baseline_agents/config/*.json`，仓库里没有这个目录；react 基线命令带了脚本不认的 `--use_other_claude_api`；TargetVal 上 coder / react 基线没加 `--use_full_data`，只载 3 张表、只置换基因列，POPPER 载 22 张表、走全量表那条置换（它实际打散了哪些列见 [1.7](#17-数据要长什么样基准数据集)） | 按脚本，表 3 的部分基线与 POPPER 不在同一份数据与同一种零假设上 | `baseline_agents/coder_agent.py:49-69`、`benchmark_scripts/run_targetval_baseline.py:82`、`benchmark_scripts/run_targetval.sh:49-62`、`popper/utils.py:77-84`、`popper/utils.py:137-159` |
| TargetVal 的指标怎么算不在仓库里：主脚本只存 pkl，出错的样例存成 `('Error', 堆栈)`；`gene_perturb_hypothesis.evaluate` 在不传 answers 时引用不存在的 `self.examples`，传了 answers（基线脚本传的是列表）又不转成数组，`answers == True` 成了列表与布尔的比较；指标名「false discovery rate」算的其实是负例上的拒绝率（即一类错误率） | 表 3 里 TargetVal 的数没法从仓库复核（读代码得出，未运行） | `benchmark_scripts/run_targetval_benchmark.py:116-127`、`benchmark_scripts/run_targetval_baseline.py:131`、`popper/benchmark.py:71-83`、`popper/benchmark.py:81`、`popper/benchmark.py:207` |

### 2.5 代码是否真按论文做

| 论文说 | 代码里 | 对得上吗 | 证据 |
|---|---|---|---|
| e_i = κ p_i^(κ−1)（式 1） | κ 写死 0.5，不暴露 | 对得上；κ 值论文正文没写 | `popper/agent.py:131-139`、`popper/agent.py:972` |
| E ≥ 1/α 拒绝（定理 4） | `cum_e > 1/alpha` | 对得上（等号差别可忽略） | `popper/agent.py:136` |
| 设计 agent 只看 schema（§3） | 每张表带一行真实值；论文自己的 prompt 也写 example rows | 部分 | `popper/utils.py:119`、`popper/prompt_utils.py:137` |
| 自我精炼迭代改进（§3） | 一次调用里自写几轮批评反思 | 对得上「chain-of-thought」的说法；不是多次调用的循环 | `popper/agent.py:785-800` |
| R(h) < r0 丢弃（§3） | 阈值 0.8，温度 0.7 | 对得上；r0 数值论文正文没给 | `popper/agent.py:927` |
| 执行 agent 用 ReAct（§3） | LangChain AgentExecutor + 自定义 REPL | 对得上 | `popper/react_utils.py:257-296` |
| 执行 agent 输出 p 值（§2.4） | 输出自由文本，p 值由另一次 LLM 调用读出 | 论文没写这一步是 LLM 读的 | `popper/agent.py:687-698` |
| 失败的实验记为失败、继续（§2.4） | 进失败清单，不进连乘；报了 p = 1 的轮不算失败，e = 0.5 进连乘 | 对得上；表 1 第 3 轮若是失败轮则与表中累计值不一致，见 [1.5](#15-e-值序贯检验与一类错误控制) | `popper/agent.py:942-945`、`popper/react_utils.py:142` |
| 算法 1：N_max 数所有轮（附录 A.1） | 成功轮、失败轮分开计数 | 对不上 | `popper/agent.py:1043` |
| 输出 ŷ = 1{E ≥ 1/α}（定理 4） | 基准脚本读 `agent.res`；公共 API 返回的 `conclusion` 是总结 LLM 的文字再结构化解析，`result.conclusion = self.res` 被注释 | 基准对得上；API 对不上 | `benchmark_scripts/run_discovery_bench.py:95`、`popper/agent.py:1050-1052`、`popper/popper.py:119-125` |
| 负例靠「random column-wise permutations」造、零假设成立（§4） | DiscoveryBench 逐列独立置换；TargetVal 全量表的置换因种子递推到 0，多数表只打乱行序 | DiscoveryBench 对得上；TargetVal 对不上 | `popper/utils.py:234-239`、`popper/utils.py:160-167`，见 [1.7](#17-数据要长什么样基准数据集) |
| 四个消融 | 开关都在；「去掉相关性检查」那条分支读代码会抛 TypeError | 部分 | 见 [2.3](#23-消融说明了什么)、[4.6](#46-实现层面的问题读代码得出未运行) |

### 2.6 外部审计 issue #10 的核对

2026-08-02 一位外部用户在仓库提了题为「Audit」的 issue[^issue10]，针对 demo 的一次运行，维护者没有回复。能用代码或论文核对的几条：

| 审计的说法 | 核对结果 | 证据 |
|---|---|---|
| 设计 prompt 要求找「对主假设的强证据」 | 原文属实 | `popper/prompt_utils.py:161-162` |
| 停止规则只在「通过」时停，累计无效结果不会得出「被证伪」 | 属实，且与论文的定义一致：输出只有验证 / 未验证两态（§2.1）；另外 p > 0.25 的轮会拉低累计值（见 [1.5](#15-e-值序贯检验与一类错误控制)） | `popper/agent.py:994-1002` |
| demo 两轮的累计 e 值 9.41 → 345.07 | 属实，按 κ = 0.5 可复算 | `demo.ipynb` 的 cells[10] |
| 执行 agent 看过 1418 行表型后才挑了代理变量，没有多重比较校正 | 代码不限制执行 agent 在一次执行里看多少数据、跑多少检验，只有 prompt 里的「avoid p-hacking」；论文附录 D 在 128 条失败日志里「未见 p-hacking」 | `popper/react_utils.py:36`、`popper/react_utils.py:143`、附录 D |
| 第 2 轮的蕴含自检自相矛盾却通过了 | 蕴含自检只存在于设计 agent 的自述文字里，没有机器检查；相关性检查按 rubric 给了 0.8 就放行 | `popper/prompt_utils.py:168`、`popper/agent.py:927` |
| 两轮共用同一个混杂信号，连乘把它放大 | 论文的假设 2 要求每轮 e 值在给定前几轮数据时有效；两轮用同一批数据时是否成立，论文没讨论（见 [4.5](#45-方法本身的前提)） | §2.3 |
| demo 里 `os.setenv` 不存在 | 属实，在 demo 的 markdown 格里 | `demo.ipynb` 的 cells[2] |
| 结果里 `check_output_error: 'Yes'` 与「implementation successful? True」并存，没解释 | 这个字段是 p 值读取器的输出，问的是「文本里有没有 p 值」，Yes 表示读到了；字段名容易读反，不是执行出错 | `popper/agent.py:90-96`、`popper/agent.py:693` |
| 相关性检查按「对主假设的支持强度」打分，是确认式的标准 | 放行的两档（1.0、0.8）写的是「supports or refutes」「supporting or refuting」，措辞是双向的，0.6 档只写了 supporting；rubric 评的是相关性，没有「假设为真时这条检验回来为空的可能性」这类严苛度的维度 | `popper/prompt_utils.py:207-212` |

审计里关于生物学解读的部分（组织组成导致的共表达、效应方向）不是代码或论文能核对的，这里不收。

## 3. 平台哪里能用

### 3.1 落在哪个阶段

| 阶段 | POPPER 有没有东西 | 依据 |
|---|---|---|
| 假设 | 有：它做的是「验证一个给定的假设」。不生成假设，论文自述与生成类工作互补（§5、附录 B）。平台假设阶段目前没有步骤，也没有主文件 | `framework/capabilities/__init__.py:45-52`（`MAIN_FILES` 没有假设这一行） |
| 文献 | 没有：设计与执行都只用数据，人类对照的任务说明写明「purely data-driven, not literature-driven」 | `popper/prompt_utils.py:137-139`、附录 I 图 7（人类对照的任务界面） |
| 写作 | 没有：只有一个五栏总结 prompt，不产论文正文 | `popper/prompt_utils.py:182-194` |
| 验证 / 框架判定层 | e 值连乘与阈值是零模型的确定性算术，形状上对应纲领 P-2「确定性能判的用零模型代码」 | `popper/agent.py:131-139`；纲领 P-2 |

### 3.2 部件对照

平台约定：框架不调模型，执行层是研究者自己登录的 Claude Code / Codex 会话（P-1、P-25）；步骤读已确认的需求、`materials/` 原件与点名的上游产出，写自己的产出目录（P-20）。

| POPPER 部件 | 平台里对应的位置 | 需要的输入 | 产出 | 与平台现有约定的差异 | 证据 |
|---|---|---|---|---|---|
| 设计 agent（拆子假设） | 假设阶段一次执行层会话 | 需求里的假设陈述；`materials/` 数据表的列名与说明；上几轮的子假设、p 值、失败清单 | 每轮一条子假设：名称、描述、h0、h1 | POPPER 自己用 langchain 调 API；平台由执行层会话产出 | `popper/agent.py:767-809`；纲领 P-1 |
| 相关性检查 | 纲领 P-2 的「需要模型判断的由框架派一个隔离的新会话、只给产物不给轨迹」，这一段平台**尚未实现** | 子假设文本、主假设文本 | 0.1–1.0 分与理由 | 输入形状本身就是隔离的（看不到设计过程）；但在 POPPER 里它只是同一进程里的一次调用 | `popper/agent.py:926`；纲领 P-2 |
| 执行 agent | 执行层会话写检验代码 | 全部数据表、一条子假设 | 自由文本结论与 p 值 | POPPER 靠 REPL 边跑边看；平台执行层会话的 Bash 只放行 `ai4sci skill` 前缀 | `popper/react_utils.py:205-254`；`framework/skills/__init__.py:37`、`framework/executor/session.py:41-43` |
| p 值读取 | 纲领 P-24 在复现流程里的「数由框架跑不由 agent 自报」；假设阶段还没有对应约定 | 执行输出 | 一个浮点数 | POPPER 用 LLM 从文本里读，只拦 NaN 与 0，不查范围；论文失败归因第一类是误读 p 值（35.9%，指执行 agent 对 p 值语境的误读，不专指读取这一步） | `popper/agent.py:687-710`、附录 D 表 5；纲领 P-24 |
| e 值累计与停止 | 框架判定层（零模型） | 各轮 p 值、α、预算 | 累计 E、通过 / 继续 | 纯算术，与模型无关 | `popper/agent.py:131-139`、`popper/agent.py:964-1002` |
| 置换零假设评测 | 评测（外层 `research/evals/`） | 一组带表格数据的正例假设 | 一类错误率、功效 | 是评测方法，不是运行时部件；逐列独立置换的实现是 DiscoveryBench 那条，TargetVal 那条有种子问题（见 [1.7](#17-数据要长什么样基准数据集)） | `popper/utils.py:234-239`、§4 |

### 3.3 可以单独摘出的方法点

「论文里有没有」一栏区分两类来源：论文正文与附录 I 的 prompt 清单（清单 2 是 CodeGen 执行器、清单 3 是设计 agent、清单 4 是相关性检查、清单 5 是总结、清单 6 是似然比估计）里能找到的，和只在仓库代码里的。许可证上这两类有没有区别，见 [4.4](#44-许可证)。

| 方法点 | 内容 | 论文里有没有 | 代码出处 |
|---|---|---|---|
| p 转 e 再连乘 | e = κ p^(κ−1)，累计值过 1/α 停；κ = 0.5 时 p > 0.25 会拉低累计值；允许按累计值随时停、按上一轮结果设计下一轮 | 式 1、定理 4、Vovk & Wang 2021[^vovk]；κ 的取值正文没写，附录 I 轨迹里的数与 κ = 0.5 一致 | `popper/agent.py:131-139` |
| 子假设三件套 | 每轮一条：描述、统计意义上的 h0、h1 | 附录 I 清单 3 | `popper/prompt_utils.py:141-145` |
| 蕴含自检 | 「主假设为空时，这条子假设是否也为空」作为设计时必答的第一问 | 附录 I 清单 3 | `popper/prompt_utils.py:135`、`popper/prompt_utils.py:168` |
| 只给产物的相关性打分 | 六档 rubric，输入只有提案与主假设 | rubric 在附录 I 清单 4；阈值 0.8 正文没给，只在代码里 | `popper/prompt_utils.py:200-218`、`popper/agent.py:926-927` |
| 执行输出约定 | 恰好一个 p 值；多个要合并；找不到有效 p 值报 1；p 值方向要与结论一致；p 恰为 0 视为错误重试 | 「恰好一个 p 值、多个要合并」在附录 I 清单 2（CodeGen）；「找不到报 1」「方向一致」只在仓库的 ReAct 模板里，附录 I 没收这个模板；「p 为 0 重试」是代码逻辑 | `popper/react_utils.py:136-143`、`popper/agent.py:706-710` |
| 失败清单回喂 | 相关性不过的与执行失败的提案都写进下一次设计 prompt，要求不重复 | 附录 I 清单 3 | `popper/prompt_utils.py:155-159` |
| 置换造零假设 | 逐列独立打乱，让任一假设的零假设成立，用来测任何 agent 流程的一类错误 | §4 | 逐列独立的实现是 DiscoveryBench 那条 `popper/utils.py:234-239`；TargetVal 那条有种子递推到 0 的问题，见 [1.7](#17-数据要长什么样基准数据集) |
| 先控一类错误再比功效 | 一类错误没控住的方法，功效置灰不参与比较 | 表 3 表注 | — |

## 4. 局限与前提

### 4.1 数据

- 只支持表格：全部读成 DataFrame 放进内存（`popper/utils.py:98-104`、`popper/utils.py:289-304`）。TargetVal 压缩后 2.27 GB、约 8500 万条记录（§3）。
- 模型看到的只有列名与一行样例；DiscoveryBench 的描述另带数据集说明与每列说明（`popper/utils.py:203-222`），自己的数据只有列名与一行样例、没有任何说明（`popper/utils.py:317-324`），列名起得差，设计质量会受影响（推断）。
- 用自己的数据时，`register_data` 会先检查并下载 2.27 GB 的生物数据存档，不看 `loader_type`（`popper/popper.py:44-46`）；issue #6、#8 报了这个问题，至今没关[^issue6]。README「Run on your own hypothesis and database」一节的示例先调 `configure` 再调 `register_data`，而 `configure` 在没注册数据时直接抛 ValueError（`README.md:140-143`、`popper/popper.py:91-92`），照抄跑不通。
- 论文说框架能扩到实验室测量或模拟（§2.4），实现只有静态数据库这一种（§3）。

### 4.2 模型

- POPPER 自己调模型 API，有两套路由。`get_llm`（设计、相关性、p 值读取、总结、CodeGen 用）：`claude-*` 走 Anthropic（`langchain_anthropic`，读 `ANTHROPIC_API_KEY`），`gpt-*` 与 `o1*` 走 OpenAI（`OPENAI_API_KEY`），其它名字一律当本机 `127.0.0.1:<port>` 上的 OpenAI 兼容服务，以 o3、o4 开头的名字也算本机（`popper/utils.py:17-41`）。ReAct 执行器自己的 `get_model` 只认 `claude-` 与 `gpt-`，`o1*` 也走本机分支，没有端口就断言失败；云端两家直接取 `os.environ["ANTHROPIC_API_KEY"]` / `os.environ["OPENAI_API_KEY"]`（`popper/react_agent.py:83-88`、`popper/react_agent.py:123-151`）。本机服务的地址写死是 `127.0.0.1`，只有端口可配（`popper/utils.py:40`、`popper/react_agent.py:151`）。
- 一次验证里的模型调用：每轮设计 2 次（生成 + 结构化解析）、相关性 1 次、执行最多 25 步、p 值读取至少 1 次，最后总结与解析各 1 次（`popper/agent.py:785-800`、`popper/agent.py:926`、`popper/react_agent.py:76`、`popper/agent.py:687`、`popper/agent.py:865-880`、`popper/agent.py:1050`）。
- 默认模型名是 `claude-3-5-sonnet-20240620` / `20241022`（`popper/popper.py:16`、`popper/agent.py:812`）。这些名字今天还能不能调用，没查。
- 表 4：模型弱了一类错误控不住（Haiku 3.5 在 TargetVal-IL2 上 0.780）。论文结论是「需要强推理与写码能力」（§4.1）。
- 温度：设计、相关性、总结用 0.7，CodeGen 与 p 值读取用 0，ReAct 执行用服务端默认（`popper/utils.py:17`、`popper/agent.py:194`、`popper/agent.py:612`、`popper/react_agent.py:124-128`）。

### 4.3 算力与运行环境

- 模型生成的代码在宿主机上 `exec`：ReAct 路径在主进程里、没有超时（`popper/react_utils.py:242`）；CodeGen 路径 imports 在主进程、正文在子进程（`popper/agent.py:325`、`popper/agent.py:374-382`）。README 说 agent 能读写文件系统、建议在容器里跑基准，并给了 Dockerfile（`README.md:195`、`Dockerfile:1-21`，python 3.9-slim、非 root 用户）。
- CodeGen 路径的子进程以函数内定义的 `run_code` 为目标，DataFrame 靠 `configure` 塞进模块全局变量再由子进程继承（`popper/agent.py:356`、`popper/agent.py:374-376`、`popper/agent.py:888-889`）。这依赖 fork 启动方式（Python 3.13 及以前 Linux 的默认）；macOS 与 Windows 的 Python 默认用 spawn，函数内定义的目标没法被 pickle，模块全局里的表也不会带过去（推断，未运行）。ReAct 路径不起子进程，不受影响。
- 本机模型要自己起 OpenAI 兼容服务，README 的示例是 4 卡跑 Mistral Large（README 自述，`README.md:98-130`）；只用云端 API 时本机不需要 GPU，但 22 张表要全部读进内存（`popper/utils.py:98-104`），解压后多大没查。
- `launch_UI` 用 `demo.launch(share=True)`，会生成公网可访问的 gradio 分享链接（`popper/popper.py:247`）。
- `time_limit` 的文档写「小时」，代码当分钟用，ReAct 路径不读它（`popper/popper.py:87`、`popper/agent.py:377`、`popper/agent.py:610`）。
- 依赖钉在 2024 年的 langchain 0.3.x 一代，用到 `langchain.agents.AgentExecutor`、`langchain_experimental` 的 `PythonAstREPLTool` 与 `langchain_core.pydantic_v1`（`popper/react_utils.py:2`、`popper/react_utils.py:6`、`popper/benchmark.py:61`）；没有测试、没有 CI；PyPI 上的 0.0.5 在建图时默认去 mermaid.ink 画图，issue #4 里维护者认为那次连接错误就来自这一步[^issue4]。能不能在今天的环境里装起来，没试。
- 耗时：与人对照时 POPPER 平均快 9.7 倍（图 2）；论文没报 API 成本。

### 4.4 许可证

| 项 | 事实 | 证据 |
|---|---|---|
| 仓库 LICENSE 文件 | 没有；GitHub API 的 license 字段为 null | 仓库根目录、GitHub API[^repo] |
| `setup.py` | `license='MIT'` | `setup.py:28` |
| PyPI 包 | 元数据 `License: MIT`；sdist 里没有许可证正文、没有版权声明 | PyPI[^pypi] |
| `popper/version.py` 文件头 | 「Based on NiLearn package / License: simplified BSD」，注释写的是另一个项目（NiLearn）的来源与许可证 | `popper/version.py:2-3` |
| 数据存档 | Harvard Dataverse 上标 CC0 1.0；存档汇集了 GTEx、GWAS Catalog、BioGRID、UK Biobank 衍生统计等上游来源，上游各自的条款没查 | Dataverse[^dataverse]、§3 |
| DiscoveryBench | ODC-By（署名） | 上游 `discoverybench/license.md`[^discoverybench] |
| 核心算式 | e = κ p^(κ−1) 出自 Vovk & Wang 2021，是已发表的数学结果 | 论文式 1、[^vovk] |

这对复用意味着什么：GitHub 的文档写明，没有许可证时默认著作权规则适用，作者保留全部权利，别人不得复制、分发或基于它做衍生作品；GitHub 服务条款只给了在 GitHub 上查看与 fork 的权利[^ghlicense]。这个仓库多了一层不确定：打包元数据里写着 MIT，但仓库与包里都没有 MIT 要求随附的许可证正文与版权声明，这行元数据算不算授权，本文不判断，列进 [第 5 节](#5-还没弄清的问题)。论文正文与附录 I 公开了公式、算法 1 与五份 prompt（[3.3](#33-可以单独摘出的方法点) 标了哪些方法点在论文里有、哪些只在代码里）；只照论文文字实现与复制仓库代码在授权上是否有区别，本文不判断。

### 4.5 方法本身的前提

- **假设 1 靠 LLM 近似**：相关性检查与人的 Spearman 只有 0.55，且比人宽（84%–85% 对 77%）（附录 G）；失败归因里「检验破坏蕴含」占 17.2%（附录 D）。论文报告去掉它一类错误明显上升（表 3；这一行用 HEAD 代码复现不了，见 [4.6](#46-实现层面的问题读代码得出未运行)），说明一类错误的控制依赖这一步，而这一步本身是一个随机的模型判断（温度 0.7）。
- **假设 2 在实现里的几处空隙**（事实 + 论文未讨论）：设计 agent 看得到每张表一行真实值（`popper/utils.py:119`）；执行 agent 在同一次会话里先看数据、再定检验与代理变量（§3、附录 E 表 6）；各轮拿到的都是全部表，同一张表可以在多轮里反复用（`popper/agent.py:782`）。执行 agent 拿到的是原 DataFrame 对象本身、不是副本，一轮里原地改了表，后面各轮看到的是改过的表（`popper/react_utils.py:213-218`、`popper/react_agent.py:156`）。论文对静态数据库只写了「选用 D_i 的决定不依赖 D_i 里的数据」（§2.3），表被多轮复用、检验在看过数据后才定时条件是否成立，没有逐条论证；置换负例上的实证数在名义水平附近（表 3），但 DiscoveryBench 那边是在所有关联都被打掉的数据上测的，TargetVal 那边按代码负例本身就不满足零假设（见 [1.7](#17-数据要长什么样基准数据集)），两边都没测到「H 为假但有混杂相关」的情形。
- **一类错误不等于错误发现率**：同时验证多个假设时，一类错误控制不保证「通过的假设大多为真」；论文附录 C 提到可以用 Bonferroni 控 FWER、用 e-BH 控 FDR，没有评测。
- **只有两态输出**：「未验证」不等于「假设为假」（§2.1）；没有「证伪」这一态。
- **p 值的方向与含义**：「效应方向要与结论一致」只写在 prompt 里（`popper/react_utils.py:141`），没有机器检查；论文附录 H 的假阳性案例：子假设问的是 RAB39A 附近变异与 IL-2 相关免疫表型的关联，执行 agent 只看了 RAB39A 在中性粒细胞（未必产 IL-2）里的 eQTL，就把它的显著性当成了证据。

### 4.6 实现层面的问题（读代码得出，未运行）

| 问题 | 后果 | 证据 |
|---|---|---|
| 连续调用 `validate` 不清状态：`num_of_tests`、`res` 在 `__init__` 里初始化，`tracked_tests`、`tracked_stat` 与设计 agent 的已通过 / 失败清单在 `configure` 里初始化，`go()` 只清日志 | 同一个 agent 验第二个假设时，e 值连乘带着上一个假设的 p 值，成功计数与失败计数也接着走，上一个假设的检验会出现在新假设的设计 prompt 里；`launch_UI` 就是对同一个 agent 反复调 `go()` | `popper/agent.py:772-773`、`popper/agent.py:820-822`、`popper/agent.py:912-915`、`popper/agent.py:1030-1038`、`popper/popper.py:160` |
| 公共 API 的结论字段来自总结 LLM | `parsed_result['conclusion']` 可能与 e 值判定不一致；e 值判定只在 `agent.agent.res` 上 | `popper/agent.py:1050-1052`、`popper/popper.py:119-125` |
| 关掉相关性检查的分支调 `test_proposal_agent.go(main_hypothesis, test_results)`，没传 `log`，而 `go` 在流式循环第一步就写 `log['designer']` | 抛 TypeError，整次验证失败。底层类 `SequentialFalsificationTest.configure` 的 `relevance_checker` 默认就是 False，只用底层类默认值会走到这里；`Popper` 包装类默认 True，不受影响；基准脚本的 NoReleCheck 两行（不带 `--relevance_checker`）会逐条记成 Error。PyPI 0.0.5 里同样如此 | `popper/agent.py:885`、`popper/agent.py:935-937`、`popper/agent.py:779`、`popper/agent.py:794`、`popper/popper.py:78`、`benchmark_scripts/run_targetval.sh:19-20`、`benchmark_scripts/run_targetval_benchmark.py:117-121` |
| 相关性分数用 `float()` 直接转字符串，没有捕获 | 模型回了「0.8 - Strongly Relevant」这类非纯数字时，异常穿出设计节点，整次 `validate` 失败 | `popper/agent.py:111`、`popper/agent.py:927` |
| ReAct 执行器按模型名前缀选接口，只认 `claude-` 与 `gpt-` | `o1-*` 走本机分支，没端口就断言失败；与 `get_llm` 的路由不一致 | `popper/react_agent.py:83-88`、`popper/react_agent.py:142-144`、`popper/utils.py:21` |
| p 值只拦 NaN 与恰为 0，不查范围 | 读出负数时 p^(−0.5) 为 NaN，累计值成 NaN，`NaN > 10` 永远为假，只能等预算用完；读出大于 1 的数时 e < 0.5，照样进连乘 | `popper/agent.py:698-710`、`popper/agent.py:479-505`、`popper/agent.py:131-139` |
| ReAct 的 Python 工具先 `exec` 除最后一行外的代码，再对最后一行单独 `eval`，`eval` 失败直接吞掉 | 最后一行是赋值等语句时静默不执行；最后一行本在循环体里时，它被拿到循环外只执行一次（`eval` 会去掉行首空格），结果静默改变，块体只剩它一行时则前面编译报错。按同样的拆法用本机 Python 试过：循环里 `xs.append(j)` 放在最后一行，跑完 `xs` 只有最后一个元素 | `popper/react_utils.py:234-250` |
| 执行 agent 的命名空间里放的是原 DataFrame 对象 | 原地修改会带到后续各轮；基准脚本一批样例共用一个 `data_loader`，也会带到后面的假设 | `popper/react_utils.py:213-218`、`popper/react_agent.py:156`、`benchmark_scripts/run_targetval_benchmark.py:36-45`、`benchmark_scripts/run_targetval_benchmark.py:94-115` |
| `prompt_revision` 路径用 `.format(domain)` 位置参数去填 `{domain}` 命名占位符 | 打开就抛 KeyError；目前没有调用方传 True，这段提示（不许直接用数据集里现成的 p 值）在 ReAct 路径上从未生效 | `popper/prompt_utils.py:75-79`、`popper/agent.py:908` |
| 相关性检查一直不过时，设计节点返回 None | 后续行为取决于 LangGraph 对空返回的处理，没验证 | `popper/agent.py:924-934` |
| p 值字符串解析失败时的 `float()` 在 ReAct 路径上没有单独捕获 | 会落进外层 `except`，算一次重试 | `popper/agent.py:698`、`popper/agent.py:724-728` |

## 5. 还没弄清的问题

| 问题 | 为什么要紧 | 怎么查 |
|---|---|---|
| 表 1 第 3 轮的「-」是执行失败（代码里不进连乘）还是报了 p = 1 的成功轮（进连乘，e = 0.5） | 只有后一种与累计值 30.78 对得上；决定表 1 与 HEAD 代码是否一致 | 问作者；或看 2.27 GB 存档里是否附带运行日志 |
| 论文表 3 的 TargetVal 负例是不是用 HEAD 这段置换代码造的；若是，至少 19 张表只打乱了行序，这两列一类错误各有多少来自表内保留的真实关联 | 决定 TargetVal 两列一类错误能说明什么 | 下载存档，按 `popper/utils.py:160-167` 在本机置换后逐表比对行内关联；或问作者 |
| 表 3 的 NoReleCheck 一行出自哪一版代码 | HEAD 与 PyPI 0.0.5 里这条分支读代码会抛 TypeError | 问作者；在隔离环境里补传 `log` 后重跑 |
| 执行 agent 看过数据再选检验、表被多轮复用时，假设 2 还成立吗；在「H 为假但有混杂相关」的零假设上一类错误是多少 | 定理 4 的保证是否覆盖真实用法 | 论文没做；需要构造非全置换的零假设（例如只打乱假设涉及的那一列）重测 |
| 图 4 是哪个基准、几次运行；最多 7 轮时约 0.16 的一类错误是噪声还是趋势 | 预算放大后还控不控得住 | 图注没写；问作者或重跑 |
| 表 4 的 o1 用的是 ReAct 还是 CodeGen | 骨干对比是否公平 | 图 9 注与 HEAD 代码都指向 CodeGen，`run_targetval.sh` 写的是 `--react`；问作者 |
| κ = 0.5 与相关性阈值 0.8 是怎么定的，结果对它们敏感吗 | 两个旋钮直接决定功效与一类错误 | 论文没报敏感性；需要重跑扫描 |
| `answer_key_real_cleaned_1.csv` 与「non-trivially falsifiable」这一列怎么来的，是否在 Dataverse 存档里 | DiscoveryBench 的 86 条假设怎么筛的 | 下载存档查看，或问作者 |
| TargetVal 真值表的 `Score` 怎么从 Schmidt 2022 的 CRISPR 筛选算出来 | 正例定义决定功效的含义 | 存档里的 csv 与论文引文对照 |
| 打包元数据里的「MIT」能否视为授权；数据存档标 CC0 是否覆盖上游条款；只照论文文字与附录 I 的 prompt 实现，与复制仓库代码在授权上有没有区别 | 决定代码、prompt 与数据能不能复用、怎么署名 | 向作者确认并请其补 LICENSE 文件；上游数据逐个查条款；法务判断 |
| 默认模型 `claude-3-5-sonnet-2024xxxx` 今天是否仍可调用、依赖能否装起来 | 决定「原样重跑论文」有没有可能 | 在隔离环境里试装、试调（本篇只读，没做） |
| 平台侧：假设阶段主文件叫什么、长什么样；p 值由框架跑出来还是由 agent 报；需要交互式看数据的执行者怎么放进「执行层只放行 `ai4sci skill`」的约定 | 这三处是 POPPER 的形状与平台约定的差异点 | 属于平台设计问题，本文只列出差异，见 [3.2](#32-部件对照) |
| 要不要为这类能力单独配模型 key、要不要走 MCP | POPPER 本身是直接调模型 API 的 Python 包，这是事实；平台怎么用它的方法是另一件事 | 研究之后再议，本文不下结论 |

[^paper]: Kexin Huang, Ying Jin, Ryan Li, Michael Y. Li, Emmanuel Candès, Jure Leskovec. *Automated Hypothesis Validation with Agentic Sequential Falsifications*. arXiv 2502.09858 v1，2025-02-14；PDF 元数据标 Proceedings of ICML 2025。<https://arxiv.org/abs/2502.09858>。本文的章节、表、图、附录编号都指这份 PDF；原件存在外层 `materials/research/2026-0927-scientific-ai-capabilities/papers/popper-2502.09858.pdf`，平台 `pdf` skill 的解析稿在同名目录。
[^repo]: GitHub API `repos/snap-stanford/POPPER` 与其 commits、issues、pulls、releases 接口，2026-09-27 查：289 star、32 fork、6 个未关 issue（其中 #7 是 PR）、33 个提交、没有 release、license 字段为 null、最近推送 2025-05-14。<https://github.com/snap-stanford/POPPER>
[^pypi]: PyPI `popper-agent`：版本 0.0.1、0.0.2、0.0.3、0.0.5；0.0.5 于 2025-04-26 上传，只有 sdist，`PKG-INFO` 写 `License: MIT`，包内无许可证文件；其 `popper/agent.py` 比仓库 HEAD 多一段 `plot_agent_architecture` 画图代码。<https://pypi.org/project/popper-agent/>
[^dataverse]: Harvard Dataverse，数据集 doi:10.7910/DVN/XNNHVE「Data repository of "Automated Agentic Hypothesis Testing with Sequential Falsifications"」，唯一文件 `popper_data_processed.tar.gz`，2,271,481,285 字节，MD5 175d0278e4293c67b41ab989f26c61b7，2025-02-16 发布，数据集许可证 CC0 1.0。<https://doi.org/10.7910/DVN/XNNHVE>
[^discoverybench]: allenai/discoverybench：数据许可证是 ODC-By（`discoverybench/license.md`），答案表在 `eval/answer_key_real.csv`，列为 dataset、metadataid、query_id、gold_hypo。<https://github.com/allenai/discoverybench>
[^vovk]: Vladimir Vovk, Ruodu Wang. E-values: Calibration, combination and applications. *The Annals of Statistics* 49(3):1736–1754, 2021（论文参考文献）。
[^ghlicense]: GitHub Docs「Licensing a repository」：「without a license, the default copyright laws apply, meaning that you retain all rights to your source code and no one may reproduce, distribute, or create derivative works from your work」；公开仓库按服务条款，其他用户有查看与 fork 的权利。<https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository>
[^issue10]: snap-stanford/POPPER#10「Audit」，2026-08-02 由外部用户提交，截至 2026-09-27 没有评论。<https://github.com/snap-stanford/POPPER/issues/10>
[^issue6]: snap-stanford/POPPER#6（2025-05-02，自定义数据也触发下载）与 #8（2025-08-03，同一问题的用户提问），均未关；修复它的 PR #7 未合并。<https://github.com/snap-stanford/POPPER/issues/6>、<https://github.com/snap-stanford/POPPER/issues/8>
[^issue4]: snap-stanford/POPPER#4（2025-04-21，本机 vLLM 报错），维护者回复错误可能来自 LangChain 请求 mermaid.ink 画图；HEAD 的最后一次提交删掉了画图代码，PyPI 0.0.5 里还在。<https://github.com/snap-stanford/POPPER/issues/4>
