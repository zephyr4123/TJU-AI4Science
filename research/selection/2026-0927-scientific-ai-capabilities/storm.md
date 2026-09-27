---
title: STORM 与 Co-STORM 方法深读
subtitle: 文献综述候选 · 只借鉴方法：视角发现、模拟对话提问、大纲、逐节写作与引用，Co-STORM 的人参与与思维导图
kind: 开源项目选型深读（只借鉴方法；只读论文与代码，不跑、不装依赖）
date: 2026-09-27
scope: 仓库 https://github.com/stanford-oval/storm，浅克隆到 vendor/storm，main 提交 fb951af（2025-09-30）；对照读了论文实验用的 NAACL-2024-code-backup 分支（7f6f5df）的 src/engine.py、src/modules/topic_expert.py、src/modules/wiki_writer.py、src/modules/write_page.py、src/scripts/run_prewriting.py 与该分支来源过滤读的维基百科页面快照（blob f8f94b8），文中写成 NAACL:路径:行；论文 arXiv 2402.14207（STORM）与 2408.15232（Co-STORM）读全文含附录；不读 frontend/demo_light 与 lm.py 里各家模型适配器的细节；knowledge_storm/、examples/、README.md 等开头的 文件:行 相对 STORM 仓库根，platform/ 与 docs/ 开头的相对本外层仓根
status: 第一版
---

> **结论先行**：STORM 能摘出来的方法有四件，前三件按论文消融给出的分量排：**多轮「读完回答再提下一个问题」的检索对话**（去掉它，大纲召回掉得最多，收集到的不同来源从 99.8 条降到 39.6 条）；**先定大纲再逐节写**（去掉大纲阶段，文章 ROUGE-1 从 45.8 掉到 26.8）；**视角发现**（对大纲的标题软召回只多 0.3 到 1.8 个点，但让不同来源数从 54 条涨到 100 条）；第四件论文没有单独消融：**逐节检索写作，加一段零模型的引用编号清洗**。Co-STORM 多出三件：**主持人**从「检索到了、没被引用、又跟已问的问题不像」的资料里生成新问题（消融里去掉主持人比去掉多专家掉得多）；**思维导图**把被引用的资料按「引出它的问题 + 查询」挂到一棵树上（插入时先用向量取候选再让模型挑；纯靠模型挑，放进完全正确节点的比例只有 3% 到 8%，放进正确节点或其祖先的比例是 62.5% 到 71.4%）；**混合主动的回合策略**（人随时插一句，系统把它当成新问题接着走）。
>
> 代码与论文对不上的有几处是实质性的：论文说的「按维基百科可靠来源规则过滤搜索结果」，在 main 上函数定义了、全仓零调用；论文实验用的 NAACL 分支接上了，但规则是拿维基百科页面上的条目 id 对域名做区分大小写的子串匹配，对该分支页面快照做静态计算，179 条规则里只有 5 条是全小写串，youtube.com、breitbart.com、dailymail.co.uk 都命中不了。视角发现在两个分支上都是模型自己写出维基百科链接、再用 `requests` 抓网页目录（论文写的是经维基百科 API），一个都抓不到就静默退化成只凭模型知识想角色；OONI 2019 年测得中国封锁了全部语言版本的维基百科[^ooni]。Co-STORM 主持人的重排公式与论文式 (1) 不是同一个式子；论文超参数（STORM 的 N=M=5，Co-STORM 的 L=2、N=3）与 main 的缺省值（3/3、3、2）不同；Co-STORM 的模拟用户与三个消融开关在 main 上，但驱动实验的脚本与评测代码到 2026-09-27 没有公开（README 说的分支不存在）；Co-STORM 自动评测里所有系统的报告都用 STORM 的「先大纲后逐节」写，不是 main 上 `generate_report()` 那种以思维导图为大纲的写法。论文里的数字能说明「方法」，不能当作「main 这份代码」的质量证据。另有几处静态可见的实现缺陷（引用编号清洗差一、大纲清洗正则会连带删掉后面的节），见 [2.4 节](#24-代码是否按论文做)。
>
> 对平台：这些方法是「怎么安排提问、检索、归类、写」的流程知识，加几段零模型的文本处理。STORM 的代码每一步都经 dspy 调一个模型后端（示例覆盖 OpenAI、Azure、Claude、Gemini 等云端接口，也有 Ollama 本地后端配 DuckDuckGo / SearXNG 的示例），Co-STORM 的嵌入只接 OpenAI 或 Azure；平台是「框架不调模型、执行层是研究者自己登录的 CLI 会话」（P-1、P-25），两者的调用方式不同。方法能对上的位置：文献阶段（视角、对话、来源台账、思维导图、主持人）与写作阶段（大纲、逐节写、引用编号）；两篇论文都不产「假设」。怎么落、要不要另配 key，本文不下结论，第 5 节列了要先弄清的问题。横向对比见同目录的 [README.md](README.md)。

## 1. 方法是什么

两个系统共用一个包 `knowledge_storm`（`knowledge_storm/` 下 Python 合计 10444 行）：STORM 在 `knowledge_storm/storm_wiki/`，Co-STORM 在 `knowledge_storm/collaborative_storm/`，检索器在 `knowledge_storm/rm.py`，模型适配器在 `knowledge_storm/lm.py`。每一个用到模型的步骤都是一个 dspy `Signature`（提示词写在类的 docstring 里）加一个 `dspy.Predict` 或 `dspy.ChainOfThought` 调用。

### 1.1 STORM 流水线总览

论文把「写一篇维基百科式长文」拆成写前（研究 + 大纲）与写作两段，重点在写前[^storm]（STORM §2.2、§3、图 2、附录 B 算法 1）。main 上的实现（`knowledge_storm/storm_wiki/engine.py:341-441`）：

```
主题 t
 │
 ├─ 视角发现：模型列出相关主题的维基百科链接 → 抓每页的标题目录 → 模型据此列出 N 个编辑角色
 │            再固定加一个「基础事实」角色
 │
 ├─ 模拟对话：每个角色一条线程并行，最多 M 轮
 │    写作者（带角色）看对话历史提 1 个问题
 │    → 专家把问题拆成 ≤3 条搜索查询 → 每条取 top-k 结果 → 每个结果只取第 1 个片段 → 写带 [n] 的回答
 │    → 写作者读到回答再提下一个；写作者的输出以 "Thank you so much for your help!" 开头就提前结束
 │
 ├─ 大纲：只凭主题写草稿大纲 → 把全部对话（去掉引用、≤5000 词）喂进去，改成最终大纲
 │
 ├─ 逐节写：每个一级节，用「该节 + 所有子节标题」做查询，在收集到的片段里做向量检索 → 写带 [n] 的一节
 │    → 零模型清洗：删超范围的编号、丢掉没用到的来源、局部编号换成全文统一编号、按首次出现重排
 │
 └─ 润色：写导语一节；可选一次「删重复」（缺省关）
```

落盘的文件（`examples/storm_examples/run_storm_wiki_gpt.py:10-20`）：`conversation_log.json`（每个角色每一轮的问题、查询、搜索结果、回答）、`raw_search_results.json`（按 URL 去重的来源表）、`direct_gen_outline.txt` 与 `storm_gen_outline.txt`（草稿与最终大纲）、`storm_gen_article.txt` 与 `url_to_info.json`（正文与引用表）、`storm_gen_article_polished.txt`。示例脚本最后调的 `post_run()` 还写 `run_config.json` 与 `llm_call_history.jsonl`，后者逐条记下每次模型调用的完整 prompt 与输出（`knowledge_storm/storm_wiki/engine.py:290-310`、`knowledge_storm/lm.py:100-107`）。每一段都能从上一段的文件重新起跑（`knowledge_storm/storm_wiki/engine.py:312-339`），`--do-research` 等四个开关控制跑哪几段。

### 1.2 视角发现

| 项 | 论文 | 代码 | 证据 |
|---|---|---|---|
| 找相关主题 | 提示模型列出相关主题，「如果能经维基百科 API 取到」就取对应条目的目录（§3.1、脚注 7 指向 Wikipedia-API 包、图 2 的 1）；附录 B Listing 1 的提示词本身就要求「list the urls」 | 模型直接输出一串 URL（`FindRelatedTopic`，ChainOfThought），代码逐行找 `http` 截出链接，不经维基百科 API；论文实验用的 NAACL 分支同样如此；`requirements.txt` 里有 `wikipedia==1.4.0`，全仓没有 import | `knowledge_storm/storm_wiki/modules/persona_generator.py:48-53,80-84`、`NAACL:src/modules/wiki_writer.py:14-19,32-35,71-75` |
| 取目录 | 目录拼成上下文 | `requests.get(url)`（无超时）后用 BeautifulSoup 取 h1 作标题、h2 到 h6 作目录，去掉 Contents / See also / Notes / References / External links，按层级缩进 | `knowledge_storm/storm_wiki/modules/persona_generator.py:10-45` |
| 取不到时 | 算法 1 第 6–10 行只在取到条目时才加目录；没说一个都取不到时怎么办 | 每个 URL 失败只记 error 日志；一个都没取到就把上下文写成 `"N/A"` 继续，角色完全凭模型知识生成，不报错 | `knowledge_storm/storm_wiki/modules/persona_generator.py:85-94` |
| 生成角色 | 生成 N 个视角 P，再加 p0「基础事实写作者」 | `GenPersona` 让模型输出「1. 角色简称: 关注点」格式，正则取出；取前 `max_num_persona` 个，前面固定加 `"Basic fact writer: ..."` | `knowledge_storm/storm_wiki/modules/persona_generator.py:56-65,99-103,151-154` |
| 用法 | 每个视角并行引导一条提问线 | `ThreadPoolExecutor` 一个角色一个线程 | `knowledge_storm/storm_wiki/modules/knowledge_curation.py:315-345` |

提示词原文就是「你要挑一组维基百科编辑，每人代表一个不同的视角、角色或立场……可以参考相关主题的维基页面」，输出「编辑简称: 描述」。视角的来源是**同类条目的章节结构**，不是检索到的内容本身。

### 1.3 模拟对话提问

| 项 | 论文 | 代码 | 证据 |
|---|---|---|---|
| 提问 | 第 i 轮由写作者按主题、视角、对话历史提一个问题，最多 M 轮（§3.2） | `AskQuestionWithPersona`（ChainOfThought）；角色为空时退到不带角色的 `AskQuestion`；写作者的输出以 "Thank you so much for your help!" 开头即停，输出为空也停（记 error 日志） | `knowledge_storm/storm_wiki/modules/knowledge_curation.py:60-68,116-123,128-151` |
| 历史怎么给 | 完整历史 | 只有最近 4 轮带专家回答（引用去掉），更早的回答替换成 "Omit the answer here due to space limit."，整体截到 2500 词 | `knowledge_storm/storm_wiki/modules/knowledge_curation.py:102-113` |
| 拆查询 | 把问题拆成若干搜索查询（图 2 的 4） | `QuestionToQuery` 输出「- 查询」列表，按行切开后去掉所有 `-`（查询里的连字符也会被删）与首尾引号，取前 `max_search_queries_per_turn`（缺省 3）行，`set` 去重；空行不过滤 | `knowledge_storm/storm_wiki/modules/knowledge_curation.py:154-164,207-216` |
| 过滤来源 | 按维基百科可靠来源规则过滤（图 2 的 5） | main 上没有接线，见 [2.4 节](#24-代码是否按论文做) | `knowledge_storm/storm_wiki/modules/retriever.py:225-233` |
| 回答 | 综合可信来源作答，来源并入参考集 R | 每个搜索结果只取第 1 个片段，编号 `[n]`，截到 1000 词，`AnswerQuestion` 要求「每句都有依据，没有合适答案就说答不了」；答完截掉最后一个不完整的句子；搜不到任何结果时回答写死为「找不到信息，请换个问题」，不让模型编；生成回答抛异常时回答写死为「答不了，请换个问题」，只记日志 | `knowledge_storm/storm_wiki/modules/knowledge_curation.py:167-178,217-240`、`knowledge_storm/utils.py:366-425` |
| 事后清洗 | 未提 | 去掉 "References:" "Sources:" 之后的内容与 "Answer:"；有越界编号时从第 k 个（k=本轮结果数）起删 `[k]…[max]`，所以合法的最后一个 `[k]` 也会被一起删掉（差一，静态读，未运行） | `knowledge_storm/utils.py:427-454` |
| 来源台账 | R 用于写作 | 按 URL 合并所有轮次的结果，片段去重；每条结果带 `meta["query"]` | `knowledge_storm/storm_wiki/modules/storm_dataclass.py:65-80`、`knowledge_storm/interface.py:294-309` |

检索器层还有一个细节：搜索结果片段里原有的 `[1]` 这类引用标记在入库前就删掉，避免和 STORM 自己的编号混（`knowledge_storm/interface.py:300-305`）。

### 1.4 大纲生成

| 项 | 论文 | 代码 | 证据 |
|---|---|---|---|
| 草稿 | 只给主题，让模型凭内部知识写草稿大纲 O_D（§3.3、图 2 的 7） | `WritePageOutline`：`#` / `##` 表示层级，不写别的，不写主题名本身 | `knowledge_storm/storm_wiki/modules/outline_generation.py:108-116,128-137` |
| 精修 | 给主题、O_D、全部 N+1 段对话，改出最终大纲 O（图 2 的 8） | 所有角色的对话拼起来；含 "topic you" 字样的轮次丢掉（代码没写原因）；去掉引用编号；截到 5000 词；草稿大纲作为 `old_outline` 字段传进 `WritePageOutlineFromConv` | `knowledge_storm/storm_wiki/modules/outline_generation.py:91-106,117-121,153-167` |
| 清洗 | 未提 | 零模型：`-` 列表项转成下一级标题，既不是 `#` 也不是 `-` 开头的行丢掉；用正则删 See also / Notes / References / External links / Bibliography / Further reading / Summary / Appendix 节；删方括号内容。删节的正则一直删到下一个 `##` 为止，被删节后面紧跟的一级标题会被连带删掉（同一正则在样例字符串上试过） | `knowledge_storm/utils.py:456-503` |
| 解析 | 大纲是多级标题的线性化（脚注 6） | `from_outline_str` 按 `#` 数量建树；第一行若等于主题名则整体降一级 | `knowledge_storm/storm_wiki/modules/storm_dataclass.py:437-474` |

精修用的是对话文字（问与答），不是原始搜索结果。`old_outline` 在 `WritePageOutlineFromConv` 里声明成 `OutputField` 却当输入传（`knowledge_storm/storm_wiki/modules/outline_generation.py:163`），论文附录 B 的 Listing 2 也是这么写的；dspy 2.4 怎么渲染这个字段未跑验证。

### 1.5 逐节写作与引用

| 项 | 论文 | 代码 | 证据 |
|---|---|---|---|
| 检索 | 用节标题与其所有下级小节标题，按 Sentence-BERT 相似度从 R 里取相关文档（§3.4） | 每个一级节把「本节 + 子孙节标题」列表当多条查询，每条在全部片段里用 `paraphrase-MiniLM-L6-v2` 取 top `retrieve_top_k`（runner 缺省 3），按 URL 合并 | `knowledge_storm/storm_wiki/modules/article_generation.py:104-110,33-40`、`knowledge_storm/storm_wiki/modules/storm_dataclass.py:109-145`、`knowledge_storm/storm_wiki/engine.py:158-161` |
| 写 | 模型写带引用的一节，各节并行 | `WriteSection` 只收 `info`、`topic`、`section`（一级节名）三项，片段编号 `[1]…[k]`、截到 1500 词；并行线程；名为 introduction、conclusion*、summary* 的一级节跳过不写 | `knowledge_storm/storm_wiki/modules/article_generation.py:91-123,144-176` |
| 小节结构 | 未明说 | 大纲里的子节标题只用来做检索查询，不传给写作；写出来的这节自带什么子标题，就按它重建这节的子树（`trim_children=True` 删掉大纲里有、正文里没写的子节）。论文实验用的 NAACL 分支同样不传大纲 | `knowledge_storm/storm_wiki/modules/article_generation.py:156`、`knowledge_storm/storm_wiki/modules/storm_dataclass.py:209-247`、`NAACL:src/modules/write_page.py:246-256` |
| 引用编号 | 未明说 | 零模型：本节正文里大于本节片段数的 `[n]` 删掉（与 1.3 节同样的差一：有越界编号时合法的最后一个 `[k]` 也被删，对应来源随之丢掉）；只保留被引用的片段；按 URL 把局部编号映射成全文统一编号（先换成占位符再替换，避免链式替换）；全文写完后按首次出现顺序重排 `url_to_unified_index`，没出现的从这张表删掉 | `knowledge_storm/storm_wiki/modules/storm_dataclass.py:249-299,272-280,174-207,374-412`、`knowledge_storm/utils.py:540-550` |
| 句子清洗 | 未明说 | 零模型：截掉末尾不完整的句子；`[1, 2]` 拆成 `[1] [2]`（中间带空格，注释写的是 `[1][2]`），紧挨着的一串 `[n]` 去重排序；以 "Overall" "In summary" "In conclusion" 开头的段落、"# Summary" "# Conclusion" 节整段删掉 | `knowledge_storm/utils.py:366-425,505-538` |
| 润色 | 各节并行生成后，把全文给模型删重复；再写一个导语节（§3.4） | 导语一定写（`WriteLeadSection`，存成名为 summary 的第一节）；删重复只在 `remove_duplicate=True` 时做，`run()` 缺省 False | `knowledge_storm/storm_wiki/modules/article_polish.py:41-53,56-72,87-102`、`knowledge_storm/storm_wiki/engine.py:349` |

引用表 `url_to_info.json` 的形状是 `{"url_to_unified_index": {url: 编号}, "url_to_info": {url: {url, title, description, snippets, meta, citation_uuid}}}`（`knowledge_storm/storm_wiki/modules/storm_dataclass.py:480-484`、`knowledge_storm/interface.py:125-133`）。

### 1.6 Co-STORM：回合策略与人参与

论文把 Co-STORM 定义为用户、若干带视角的专家、一个主持人三种角色的轮流对话，每句话带一个意图：新问题（Original Question）、追问（Information Request）、可能答案（Potential Answer）、补充细节（Further Details）；混合主动：用户随时可以接过话头[^costorm]（Co-STORM §3.1、§3.3、图 2）。代码（`knowledge_storm/collaborative_storm/engine.py:661-761`）每调一次 `step()` 走一回合：

```
step(user_utterance=...) 有人插话 → 记成 Guest 的 Original Question，清掉「下一轮强制主持人」，本回合结束
step()                   没人插话 → get_next_turn_policy：
  ├─ warm start 刚结束              → 主持人先开口（这条排在 disable_moderator 判断之前）
  ├─ 最近连续 ≥3 轮都不是提问类     → 主持人生成新问题，本回合结束后重组思维导图
  ├─ 上一轮是提问类（人、主持人或专家问的）
  │                                  → 固定角色「General Knowledge Provider」检索作答，
  │                                    然后以这个问题为焦点、以刚才的回答为背景，重新生成专家名单
  └─ 其它                            → 专家名单轮换出一位：先让模型选意图，答案类意图检索作答，问题类直接说
  每个专家回合（含 General Knowledge Provider，含提问类意图）都再过一次「改成口语」的润色；
  主持人的问题在它自己的生成模块里润色；本轮被引用的资料插进思维导图
```

| 项 | 论文 | 代码 | 证据 |
|---|---|---|---|
| 人插话后 | 用这句话检索，更新专家名单 P′，再回到自动模式（§3.3） | 插话本身不检索；下一回合由通用专家检索作答，之后 `GenerateExpertWithFocus` 以插话为焦点、以该回答（截 100 词）为背景生成新名单（提示词要 2 位，代码不截断），整张名单替换 | `knowledge_storm/collaborative_storm/engine.py:702-709,486-500,731-738,446-453`、`knowledge_storm/collaborative_storm/modules/expert_generation.py:24-40,58-83` |
| 专家选意图 | 模型按历史与视角选意图（§3.4 第 1 步） | 上一轮是提问类时不问模型，强制「可能答案」；否则 `GenExpertActionPlanning` 输出「意图: 一句话」，解析不出直接抛异常 | `knowledge_storm/collaborative_storm/modules/costorm_expert_utterance_generator.py:17-39,110-140` |
| 专家作答 | 生成查询、检索、写带引用的回答（第 2 步） | `AnswerQuestionModule`：拆查询（`max_search_queries` 缺省 2 条）→ 每条取 `retrieve_top_k`（缺省 10）条结果 → brief 模式每个结果取第 1 个片段、共 ≤1000 词 → 回答；只把回答里真正引用到的片段记为 `cited_info` | `knowledge_storm/collaborative_storm/modules/grounded_question_answering.py:66-163`、`knowledge_storm/collaborative_storm/modules/collaborative_storm_utils.py:36-105,243-261` |
| 润色 | 让话更口语、更有互动感（第 3 步） | `ConvertUtteranceStyle`，要求保留 `[n]`、不编；上一位说的话超过 3 段时只保留首段与末两段；`CoStormExpert` 每回合都调，`TurnPolicySpec.should_polish_utterance` 设了但没有代码读它 | `knowledge_storm/collaborative_storm/modules/costorm_expert_utterance_generator.py:73-101`、`knowledge_storm/collaborative_storm/modules/grounded_question_generation.py:33-52`、`knowledge_storm/collaborative_storm/modules/co_storm_agents.py:99-106`、`knowledge_storm/collaborative_storm/engine.py:315,501` |
| 谁来答问题 | 专家按顺序轮流（§3.1 Turn Management） | 上一轮是提问类时总是通用专家答；专家轮换只发生在「接着上一个回答往下说」的回合。论文附录 G 的对话样例里，主持人与用户提问后也是 General Knowledge Provider 作答，与代码一致，正文没写这个角色 | `knowledge_storm/collaborative_storm/engine.py:486-501`、Co-STORM 附录 G |
| 预热 | 讨论开始前 N 位专家各说一轮（§3.1） | `warm_start()` 是一个小型 STORM：背景检索 → 生成 3 位专家 → 每位 2 轮问答 → 草稿大纲 + 讨论焦点生成大纲 → 建树并插入资料 → 按树写报告 → 把报告每一节改写成「一问一答」作为给人看的开场，并用它替换对话历史 | `knowledge_storm/collaborative_storm/engine.py:582-640`、`knowledge_storm/collaborative_storm/modules/warmstart_hierarchical_chat.py:157-256,259-309,346-408` |
| 结束 | 实验里到 30 次搜索查询停（§5.1） | 由调用方决定调几次 `step()`；`total_conv_turn` 参数定义了、示例脚本也传了，库里没有代码读它 | `knowledge_storm/collaborative_storm/engine.py:206-209`、`examples/costorm_examples/run_costorm_gpt.py:109,175-196` |

人能做的只有两件：插一句话（永远被记成新问题），和决定什么时候调 `generate_report()`。代码里没有「改专家名单」「改思维导图」「否决一条资料」的入口；论文局限一节也写了用户想要更多控制（管理专家视角、定制发言长度）。仓库里没有 Co-STORM 的界面（`frontend/` 下搜不到 Co-STORM 相关代码），只有控制台示例：看 1 轮、人插 1 句、再看 1 轮、重组导图、出报告（`examples/costorm_examples/run_costorm_gpt.py:181-196`）。

### 1.7 Co-STORM：主持人

论文（§3.5）：只有专家时讨论会越来越偏向「补充细节」，重复且钻牛角尖；主持人从「上次主持人发言以来检索到、但没被引用」的资料里，按与主题相似、与原问题不相似重排（式 (1)：cos(i,t)^α · (1−cos(i,q))^(1−α)，§4 定 α=0.5），连同思维导图里已有的概念名一起给模型，生成一个新问题和新的专家名单。

代码（`knowledge_storm/collaborative_storm/modules/co_storm_agents.py:190-311`）：

1. 取最近 2 个回合（遇到 `utterance_type == "Questioning"` 停；这个类型只有 warm start 的背景检索那一轮会设，`knowledge_storm/collaborative_storm/modules/warmstart_hierarchical_chat.py:176`，而 warm start 结束后对话历史被换成报告改写出来的问答，那一轮只留在 `warmstart_conv_archive` 里，所以这个停止条件在正常流程里碰不到，`knowledge_storm/collaborative_storm/engine.py:617-620`），把每轮检索到的每个结果拆成单片段。
2. 已经进了思维导图的片段按哈希排除，剩下的算三个量：与本轮查询的最大相似度、与所有已引用片段的最大相似度、与本轮「要说的论点」（`claim_to_make`）的相似度。
3. 分数 = (1 − 查询相似度)^0.5 × (1 − 已引用相似度)^0.5 × [论点相似度 ≥ 0.25]；降序。多轮之间按轮转交错合并。
4. `GroundedQuestionGeneration` 拿「思维导图的摘要（又一次模型调用，只给节点名的层级，不给资料正文）+ 重排后的资料（≤1000 词）+ 上一句话」生成一句带 `[n]` 的问题，再做一次口语润色；润色后问题里引用到的资料记为 `cited_info`（`knowledge_storm/collaborative_storm/modules/grounded_question_generation.py:81-113`、`knowledge_storm/collaborative_storm/modules/knowledge_base_summary.py:21-32`）。

warm start 刚结束时主持人先开口，这时最近 2 个回合是报告改写出来的问答，没有 `raw_retrieved_info`，未用资料为空（`knowledge_storm/collaborative_storm/modules/warmstart_hierarchical_chat.py:99-122`、`knowledge_storm/collaborative_storm/modules/co_storm_agents.py:194-212`），第一个主持人问题只凭导图摘要与上一句话生成（静态读，未运行）。与论文式 (1) 的差别见 [2.4 节](#24-代码是否按论文做)。嵌入用的是 `text-embedding-3-small`，只支持 OpenAI 与 Azure 两家；`Encoder()` 不传参时读环境变量 `ENCODER_API_TYPE`，没设就抛错（`knowledge_storm/encoder.py:78-95`）。

### 1.8 Co-STORM：思维导图与报告

| 项 | 论文 | 代码 | 证据 |
|---|---|---|---|
| 结构 | 树 M=(C,E)，每个概念挂一组检索到的资料，每条资料带引出它的问题（§3.2） | `KnowledgeNode{name, content: 资料编号集合, children}`；资料存在 `info_uuid_to_info_dict`，编号按哈希去重、全局唯一（哈希含 URL、片段、问题、查询）；资料的 `meta` 带 `question`、`query`、`placement`（在树上的路径） | `knowledge_storm/dataclass.py:86-119,291-360,680-713`、`knowledge_storm/interface.py:87-95` |
| 什么进树 | 讨论中收集的资料 | 只有回答或问题里**被引用**的片段；检索到没被引用的不进树（留给主持人用） | `knowledge_storm/dataclass.py:784-801` |
| 插入 | 先按「问题」与各概念的语义相似度取候选，再让模型选最终位置（§3.2、附录 B） | 以（问题, 查询）为单位：把树上每个节点的完整路径编码，取与「问题, 查询」最像的 8 条路径让模型选「Best placement: 编号」；选不出就逐层导航（每层模型选 insert / step: 子节点 / create: 新子节点）；同一（问题, 查询）下的资料放一起 | `knowledge_storm/collaborative_storm/modules/information_insertion_module.py:149-211,108-147,221-313` |
| 重组 | 某概念下超过 K 条资料时，模型给出子主题名，把它的资料重新插入子树；之后自底向上删空概念、把只有一个子节点的概念并掉（§3.2） | 资料数 ≥ K 就展开；`ExpandSection` 只给模型看这些资料的「问题 + 查询」，不给资料正文；子主题少于 2 个不展开；K 缺省 10；重组只在「连续答题触发主持人」的那一回合、warm start 结束时和调用方手动调 `reorganize()` 时发生 | `knowledge_storm/collaborative_storm/modules/information_insertion_module.py:316-424,378-382`、`knowledge_storm/dataclass.py:715-771,828-846`、`knowledge_storm/collaborative_storm/engine.py:483-484,621,754-760` |
| 报告 | 以思维导图为大纲、用每个概念挂的资料逐节写（§3.3） | 每个节点一节：节点自己没挂资料就只出标题、不写正文；自己挂了资料时，用本节点**及所有子孙**挂的资料（按编号升序、截 4000 词），各节并行写；「是否重写」的标志只在本节点自己的资料变了时置位，子孙新增资料不会让上层重写（静态读）；输出只有正文，引用编号是全局资料编号，引用表在 `instance_dump.json` 的 `info_uuid_to_info_dict` 里 | `knowledge_storm/collaborative_storm/modules/article_generation.py:20-107,42-49`、`knowledge_storm/dataclass.py:206-209`、`examples/costorm_examples/run_costorm_gpt.py:198-208` |
| 存盘 | 未提 | `to_dict` / `from_dict` 把树、资料表、对话、专家名单整个序列化，能从文件接着跑；每回合的 `cited_info` 写成 None（资料已在树上）；`from_dict` 忽略存下来的模型配置，FIXME 注释在 | `knowledge_storm/dataclass.py:54-66,242-256,362-372`、`knowledge_storm/collaborative_storm/engine.py:540-580` |

## 2. 为什么有效

### 2.1 STORM 的证据与消融

评测集 FreshWiki：2022-02 到 2023-09 每月编辑最多的 100 个英文维基条目里，B 级以上、有子节、非列表的，取 100 篇 3000 词以内的（§2.1、§4.1、附录 A）。大纲用「标题软召回」与「标题实体召回」对人写的条目比；文章用 ROUGE、实体召回、Prometheus 13B 按 5 分量表打分，引用用 Mistral 7B 判蕴含（§2.2、§4.2）。实验配置：提问用 gpt-3.5-turbo，其余用 gpt-3.5-turbo-instruct，大纲另试 gpt-4，正文只报 gpt-4 的结果；检索用 You.com（§4.4）。

| 证据 | 数字 | 说明了什么 | 出处 |
|---|---|---|---|
| 大纲消融（GPT-3.5） | 软召回 / 实体召回：完整 86.26 / 40.52；去视角 84.49 / 40.12；去对话 77.97 / 31.98；直接生成 80.23 / 32.39；RAG 73.59 / 33.85 | 「读回答再追问」贡献最大；只给视角、一次性列问题，比直接生成还差 | 表 3 |
| 大纲消融（GPT-4） | 完整 92.73 / 45.91；去视角 92.39 / 42.70；去对话 88.75 / 39.30；RAG-expand 91.36 / 43.53；直接生成 87.66 / 34.78 | 强模型下直接生成已经 87.66，STORM 领先 RAG-expand 1.37 个点软召回（实体召回 45.91 未标显著）；视角主要体现在实体召回 | 表 3 |
| 收集到的不同来源数 | 完整 99.83；去视角 54.36；去对话 39.56 | 视角对「找到多少不同来源」的作用比对大纲召回大 | 表 5 |
| 大纲阶段消融 | ROUGE-1 45.82 → 26.77；实体召回 14.10 → 7.39；覆盖 4.88 → 4.37；组织 4.82 → 4.87 | 先定大纲对内容覆盖是决定性的；量表上的「组织」分反而没掉 | 表 2 |
| 对 oRAG（按节检索写） | ROUGE-1 45.82 vs 44.26（不显著）；实体召回 14.10 vs 12.57、趣味 3.99 vs 3.90、相关 4.45 vs 4.09、覆盖 4.88 vs 4.70（这四项 p<0.05） | 在同样「先大纲后逐节写」的框架里，提问机制还有增量，但幅度小 | 表 2 |
| 引用质量 | 引用召回 84.83，引用精确 85.18（Mistral 7B 判） | 约 15% 的句子不被所引来源支持 | 表 4 |
| 不被支持的句子拆开看（抽 10 篇） | 缺引用 47%、评审模型误判（作者核实其实有依据）15%、不当推断连接 14%、分句错 12%、转述不准 7%、引了无关来源 4%、其它 1% | 最大一块是「这句根本没挂引用」；真错里最多的是把不相干的事实连起来 | 图 6、表 9、附录 C.3 |
| 人评（10 位资深维基编辑，20 对文章） | 1–7 分：组织 3.25 → 4.00（p=0.005）；覆盖 3.58 → 4.00（p=0.084）；可核查 3.85 vs 3.80（p=0.843）；偏好 26 : 14；评分者一致性 α 0.22–0.39 | 只有「组织」显著；样本小、一致性低 | 表 6、脚注 11 |
| 编辑的开放意见 | 语气不中立 12 次；把无关事实扯到一起 11 次；缺重要信息 6 次；时效表述不当 5 次；小节太碎 5 次 | 检索来源的偏向会传到文章；可核查性问题不止事实幻觉 | 表 11、§6、附录 E |
| 有用性问卷 | 10 位编辑全部同意对写前阶段有帮助，80% 认为能帮他们写新条目 | 定位是「起稿」，不是成稿 | 图 3 |

### 2.2 Co-STORM 的证据与消融

评测集 WildSeek：STORM 公开网站上真实用户留下的 6608 对（主题, 目的），筛到 24 个细类、6 个大领域的 100 条（§2.2、附录 A）。自动评测用 gpt-4o 扮演用户、每个系统用满 30 次搜索查询；所有系统的最终报告都用 STORM 的「先大纲后逐节」两段法按交互历史写（不是 §3.3 说的以思维导图为大纲），报告用 Prometheus-2 7B 打分（§5.1、§5.2）。

| 证据 | 数字 | 说明了什么 | 出处 |
|---|---|---|---|
| 报告质量 | 深度 3.77 vs STORM+QA 3.43；新颖 3.05 vs 2.50（均 p<0.05）；相关、广度、信息多样性差异不显著 | 相对「先 STORM 再问答」，多角色讨论主要提升深度与新颖 | 表 3 |
| 回答回合质量 | 一致 4.40、投入 4.33（均 p<0.05）、每回合不同 URL 6.04 vs STORM+QA 2.89 / RAG 聊天 2.94 | 多角色讨论引用的来源更分散 | 表 3 |
| 消融：去主持人 | 相关 3.78 → 3.56，深度 3.77 → 3.41，新颖 3.05 → 2.89，URL 6.04 → 5.67 | 主持人比多专家更要紧 | 表 3、§5.4 |
| 消融：只留 1 个专家 + 主持人 | 深度 3.77 不变，一致 4.40 不变，新颖 2.93，URL 5.91 | §5.4 讨论图 3 时原文写「一个专家加一个主持人已能拿到大部分收益」；同一节又说消融版本「在所有指标上都更差」，与表 3 里深度、一致两项持平对不上 | 表 3、图 3、§5.4 |
| 提问回合质量（读图约数） | 新颖 约 3.9 / 3.7 / 3.0；意图一致 约 4.1 / 3.9 / 3.5；不重复 约 3.9 / 3.6 / 3.1（完整 / 单专家 / 无主持人） | 去掉主持人后提问回合掉得最多 | 图 3 |
| 思维导图插入（111 个任务，把维基条目的引用放回原来的小节） | 完全放对：一级 向量 24.24% / 纯模型 3.03% / 两者结合 39.39%；二级 35.94% / 7.81% / 51.56%；三级 35.71% / 7.14% / 35.71%。放到正确节点的祖先也算的部分正确：二级 65.62% / 62.50% / 68.75%；三级 57.14% / 71.43% / 71.43% | 纯靠模型在宽深的树上很难一次放到准确节点，但多数能放到对的分支上；向量取候选 + 模型挑在一、二级最好，三级（14 个任务）与纯向量持平 | 附录 B 表 6 |
| 人评（20 人，分两组各 10 人，一组 9 份有效） | 对搜索引擎：意外发现 2.70 → 3.90（p=0.030），深度 p=0.081，广度 p=0.096；对 RAG 聊天：广度 3.11 → 4.22（p=0.013），意外发现 2.78 → 3.78（p=0.009）；总体偏好 70% / 78% | 对搜索引擎只有「意外发现」显著；对 RAG 聊天是「广度」与「意外发现」显著 | 表 4、图 4 |
| 思维导图的人评 | 80 个快照里 71% 被认为准确跟上了讨论；评过的 32% 发言里 89% 被认为把讨论引向了新方向 | 导图能跟上讨论；「更省力」（80% / 67%）是对整个系统问的，没有单独测导图对「心智负担」的作用 | §6.2、图 4 |
| 自动评分与人评的相关 | 皮尔逊 0.32（新颖，不显著）到 0.55 | 只对对话回合的 5 个量表各抽 10 条做了（n=50），报告评分没有这项对照；自动指标只是弱代理 | 附录 D 表 7 |

### 2.3 哪一步最关键

- **STORM 里最关键的是「多轮、读完回答再问」**：去掉它，GPT-3.5 的大纲软召回掉 8.3 个点、实体召回掉 8.5 个点，来源数只剩四成（表 3、表 5）；对照组「去对话」仍然有视角、有检索，只是问题一次性列完（论文说控制了问题总数相等），说明增益来自「先读到答案再决定下一问」。
- **其次是「先定大纲」**：没有大纲直接从对话写全文，ROUGE 与实体召回近乎减半（表 2）。但这个消融是「从对话直接写全文」，不是「有大纲、但大纲不经对话精修」；大纲精修本身的贡献只能从「直接生成 vs STORM」间接看（表 3）。
- **视角的作用集中在来源数与实体召回**，对软召回的增量在 GPT-4 上只有 0.34 个点（表 3）。论文没有把「视角从相关条目目录来」与「视角由模型凭空列」分开消融。
- **Co-STORM 里最关键的是主持人**，其次才是多专家（表 3、图 3）。思维导图的贡献只有插入准确率的受控实验（附录 B），没有「去掉思维导图」的端到端消融；自动评测的报告也不是从思维导图写的（§5.1），表 3 的报告分数说明不了导图做大纲的效果。

### 2.4 代码是否按论文做

「README 或论文说了、代码里没有或只接了一半」的逐条对账。第 1 到 9 条影响方法本身，其余是实现层面的。

| # | 论文 / README 说 | main 上的代码 | 证据 |
|---|---|---|---|
| 1 | 搜索结果按维基百科可靠来源规则过滤（STORM §3.2、图 2 的 5；Co-STORM 脚注 4 与伦理声明也这么说） | `is_valid_wikipedia_source` 定义了，全仓零调用；带 `is_valid_source` 参数的检索器缺省 `lambda x: True`，`AzureAISearch` 收了参数但不用，`SerperRM`、`VectorRM`、`StanfordOvalArxivRM` 没有这个参数；没有一个示例脚本传它。论文实验用的 NAACL 分支接上了：运行时从随仓的维基百科「常见来源」页面快照里取表格行的 id（去掉 `_(…)` 后缀），对 URL 域名做**区分大小写的子串匹配**。对该快照做静态计算（同样的正则，未运行项目代码）：179 条规则里只有 5 条是全小写串（bestgore.com、starsunfolded.com 与三个带连字符的 id），breitbart.com、youtube.com、amazon.com、healthline.com、dailymail.co.uk、infowars.com 都命中不了；main 上写死的 205 条同样只有这 5 条是全小写串 | `knowledge_storm/storm_wiki/modules/retriever.py:9-11,225-233`、`knowledge_storm/rm.py:26-30,67,1178-1182`、`NAACL:src/modules/topic_expert.py:31-77,104-106` |
| 2 | 经维基百科 API 取相关条目目录（§3.1、脚注 7） | 模型写 URL、直接抓网页（NAACL 分支同样）；全部失败时静默退化成 `"N/A"` | `knowledge_storm/storm_wiki/modules/persona_generator.py:80-94`、`NAACL:src/modules/wiki_writer.py:71-85` |
| 3 | N=M=5（§4.4） | main 缺省 `max_perspective=3`、`max_conv_turn=3`；NAACL 分支的实验脚本缺省是 5 / 5，且每轮查询数写死为前 5 条 | `knowledge_storm/storm_wiki/engine.py:134-145`、`NAACL:src/scripts/run_prewriting.py:78-80`、`NAACL:src/modules/topic_expert.py:163` |
| 4 | 「去视角」「去对话」两个消融（表 3） | 模块有 `disable_perspective` 分支，但 runner 调用时写死 `disable_perspective=False`，`STORMWikiRunnerArguments.disable_perspective` 字段定义了不读；NAACL 分支接了这个开关（走一条不带角色的通用对话）。「去对话」变体在 main 与读过的 NAACL 文件里都没有 | `knowledge_storm/storm_wiki/engine.py:150-153,224`、`knowledge_storm/storm_wiki/modules/knowledge_curation.py:369-374`、`NAACL:src/engine.py:132-146`、`NAACL:src/scripts/run_prewriting.py:84-85` |
| 5 | 各节写完后把全文给模型删重复（§3.4） | 缺省不做；GPT 示例脚本解析了 `--remove-duplicate` 与 `--retrieve-top-k` 两个参数，都没传下去 | `knowledge_storm/storm_wiki/engine.py:349`、`examples/storm_examples/run_storm_wiki_gpt.py:89-95,145-151,230-240` |
| 6 | 主持人重排：cos(i,t)^α · (1−cos(i,q))^(1−α)（Co-STORM 式 (1)） | (1−max cos(i,查询))^0.5 · (1−max cos(i,已引用片段))^0.5 · [cos(i,论点) ≥ 0.25]：「与主题相似」一项换成了对论点的 0/1 门槛，多了一项「与已引用资料不相似」；主题的嵌入算了但没进分数 | `knowledge_storm/collaborative_storm/modules/co_storm_agents.py:219-246,256-268` |
| 7 | 主持人用「上次主持人发言以来」的未引用资料（§3.5） | 用最近 2 个回合；停止条件判断的 Questioning 类型只有 warm start 会产生，且不在 warm start 之后的对话历史里 | `knowledge_storm/collaborative_storm/modules/co_storm_agents.py:248-262`、`knowledge_storm/collaborative_storm/modules/warmstart_hierarchical_chat.py:176`、`knowledge_storm/collaborative_storm/engine.py:617-620` |
| 8 | L=2、N=3（§4）；L 数的是连续几轮「可能答案 / 补充细节」（§3.1）；主持人同时产出新专家名单（§3.5）；专家按顺序轮流答（§3.1） | `moderator_override_N_consecutive_answering_turn=3`、`max_num_round_table_experts=2`（warm start 专家数缺省 3）；计数的是连续几轮「不是 Original Question / Information Request」，warm start 的 Support 类型也算；主持人只产问题，名单在下一回合（任何提问类之后）重生成；问题总是由固定的通用专家答 | `knowledge_storm/collaborative_storm/engine.py:218-227,241-250,408-423,486-500,731-738` |
| 9 | 报告以思维导图为大纲逐节写（§3.3）；但自动评测里所有系统的报告用 STORM 两段法写（§5.1） | `generate_report()` 只有以思维导图为大纲这一种写法，main 上没有 §5.1 那种写法的 Co-STORM 入口 | `knowledge_storm/collaborative_storm/engine.py:642-656`、`knowledge_storm/dataclass.py:848-849` |
| 10 | 30 次搜索查询后结束（§5.1） | `total_conv_turn` 定义不读，停止完全由调用方控制 | `knowledge_storm/collaborative_storm/engine.py:206-209` |
| 11 | Co-STORM 实验代码在 `EMNLP-2024-code-backup` 分支（README「placeholder for now」） | 2026-09-27 查分支列表没有这个分支；有一个 `costorm-integration` 分支（最后提交 2024-09-25），文件结构与 main 同形，没有评测脚本。main 上有实验用的零件：模拟用户 `SimulatedUser`、RAG 基线 `PureRAGAgent`、三个开关 `disable_moderator` / `disable_multi_experts` / `rag_only_baseline_mode`；缺的是驱动循环、30 次查询停止、STORM+QA 基线与打分代码。WildSeek 数据在 Hugging Face 上[^repo] | `README.md:306-310`、`knowledge_storm/collaborative_storm/modules/co_storm_agents.py:110-156,314-375`、`knowledge_storm/collaborative_storm/engine.py:257-268,469-491` |
| 12 | 同上三个开关的语义 | `disable_moderator=True` 时 warm start 后的第一回合仍由主持人开口（强制主持人的判断排在前面）；`rag_only_baseline_mode` 分支读 `self.conversation_history`，而 `DiscourseManager` 没有这个属性，走到就抛 AttributeError；`disable_multi_experts` 的帮助文字写成了「disable moderator」（均为静态读，未运行） | `knowledge_storm/collaborative_storm/engine.py:261-264,469-484,616` |
| 13 | README：思维导图「has been proven」降低心智负担 | 论文证据是 71% 快照准确与参与者引语；「更省力」是对整个系统的两两比较，没有单独测导图 | `README.md:68`、Co-STORM §6.2、图 4 |
| 14 | STORM 附录 B：框架不依赖为单一领域做提示工程 | 提示词通篇是「维基百科编辑」「维基百科页面」 | `knowledge_storm/storm_wiki/modules/knowledge_curation.py:128-151`、`knowledge_storm/storm_wiki/modules/outline_generation.py:128-167`、`knowledge_storm/storm_wiki/modules/article_generation.py:162-176` |
| 15 | — | 静默失败：思维导图插入异常只 `print` 调用栈，该条资料不进树；warm start 某位专家出错只 `print`，这位专家的问答整段丢掉；检索异常记日志后按「没搜到」继续；STORM 专家生成回答异常时换成固定句子；`conv_turn.utterance.replace("[-1]", "")` 的结果被丢弃 | `knowledge_storm/collaborative_storm/modules/information_insertion_module.py:257-259`、`knowledge_storm/collaborative_storm/modules/warmstart_hierarchical_chat.py:196-240`、`knowledge_storm/rm.py:71-72`、`knowledge_storm/storm_wiki/modules/knowledge_curation.py:235-237`、`knowledge_storm/dataclass.py:818,822` |
| 16 | — | 静态可见的处理缺陷：引用编号清洗差一（有越界编号时连合法的最后一个 `[k]` 一起删）；大纲清洗正则删到下一个 `##` 为止，会连带删掉紧随其后的一级标题；专家名单按 `split(":")` 拆成两段，描述里再带冒号就抛 ValueError，在 `step()` 里没人接 | `knowledge_storm/storm_wiki/modules/storm_dataclass.py:272-280`、`knowledge_storm/utils.py:445-447,480-500`、`knowledge_storm/collaborative_storm/engine.py:425-444` |
| 17 | — | 抓网页的 `httpx.Client(verify=False)` 关掉了 TLS 校验；BingSearch、GoogleSearch 与开了额外片段抽取的 SerperRM 抓原网页时用它 | `knowledge_storm/utils.py:651`、`knowledge_storm/rm.py:109,167,441,537,1036,1096` |
| 18 | — | GPT 示例的 `searxng` 分支没传必填的 `searxng_api_url`；`DuckDuckGoSearchRM` 依赖的 `duckduckgo_search` 不在 `requirements.txt` | `examples/storm_examples/run_storm_wiki_gpt.py:128-131`、`knowledge_storm/rm.py:644-664,749-753`、`requirements.txt` |

## 3. 平台哪里能用

先摆平台的约定（事实，出处在纲领）：框架不调模型，执行层是唯一写代码的，助理可以不经能力手写材料清单（P-1）；阶段主文件文献是 `sources.md`、假设与写作待第一个能力定名（P-20）；能力分「步骤」与「skill」，skill 脚本 PEP 723 自带依赖、`uv run --locked --offline` 起（P-22）；助理与执行层都是研究者自己登录的 Claude Code 或 Codex 会话（P-25）；联网只用 CLI 自带的搜索与网页读取工具，查到的带来源，不在 Bash 里拿 curl 硬凑（P-14，`platform/framework/chat/guide.py:74-77`、`platform/framework/executor/prompting.py:21-24`）；执行层会话的 Bash 只放行 `ai4sci skill *`（`platform/docs/add-a-capability.md`「写代码」一节）；需要模型判断的评审要隔离会话，这一段尚未实现（P-2）。纲领见 `docs/architecture/README.md`。

| 方法 | 对应阶段 | 需要的输入 | 产出（STORM 里的形状） | 与平台现状的关系 | 证据 |
|---|---|---|---|---|---|
| 视角发现 | 文献 | 主题（需求里的一句话）；若干「同类文章的章节结构」 | 角色清单：「角色: 关注点」N 条 + 基础事实 1 条 | STORM 取的是维基百科条目目录；平台的 `pdf` skill 能把一篇论文解析出分节层级（`structured.json` 的 `sections`），同是「章节标题树」这类输入 | `knowledge_storm/storm_wiki/modules/persona_generator.py:10-45,56-65`、`platform/skills/pdf/SKILL.md` |
| 模拟对话提问 | 文献 | 角色、主题、一个能返回「标题 + URL + 正文片段」的检索手段 | 每个角色一段对话：每轮的问题、查询、搜索结果、带 `[n]` 的回答（`conversation_log.json`）；按 URL 去重的来源表（`raw_search_results.json`） | P-24 让助理手写 `sources.md`、写法不限；STORM 的日志给出了一种来源溯源形状：每条来源是哪个角色、哪个问题、哪条查询找到的 | `knowledge_storm/storm_wiki/modules/knowledge_curation.py:47-81`、`knowledge_storm/storm_wiki/modules/storm_dataclass.py:14-45,82-97`、`platform/coordinator/README.md:64` |
| 大纲生成 | 写作（或文献收尾） | 主题；对话文字（去引用） | 草稿大纲与最终大纲，markdown 标题 | 写作阶段主文件未定名；大纲本身是一个 markdown 文件 | `knowledge_storm/storm_wiki/modules/outline_generation.py:84-125` |
| 逐节写作 | 写作 | 大纲；来源表；每节的检索（STORM 用本地 MiniLM 向量） | 带 `[n]` 的正文 + `url_to_info.json` | 平台 `add-a-capability.md` 的写作阶段例子是「论文初稿」`draft.md`，是文档里的例子，未落地 | `knowledge_storm/storm_wiki/modules/article_generation.py:53-133`、`platform/docs/add-a-capability.md` |
| 引用编号清洗、句子清洗 | 写作 | 正文 + 本节的来源列表 | 统一编号的正文、只含被引用来源的引用表 | 全部是零模型的字符串处理（含 2.4 节第 16 条的差一）；平台 `verify` 现在核对的是数字回溯，不含引用 | `knowledge_storm/storm_wiki/modules/storm_dataclass.py:249-299,374-412`、`knowledge_storm/utils.py:366-550`、`platform/coordinator/README.md:60` |
| 引用是否被来源支持 | 验证 | 句子 + 所引片段 | 支持 / 不支持 | 论文用另一个模型（Mistral 7B）判蕴含，生成与评审分开；STORM 仓库 main 上没有这段代码，NAACL 分支有 `eval/citation_quality.py`；平台 P-2 的模型评审未实现 | STORM §4.2、表 4；NAACL 分支文件列表[^repo] |
| 主持人 | 文献（找盲区）；与假设的关系要另外定义 | 每轮检索到的全部片段、已引用集合、嵌入 | 一句带 `[n]` 的新问题 | 产的是「下一个该问的问题」，不是假设；要嵌入，代码里只接 OpenAI / Azure | `knowledge_storm/collaborative_storm/modules/co_storm_agents.py:190-311`、`knowledge_storm/encoder.py:78-95` |
| 思维导图 | 文献（与研究者共享的资料结构）；写作（报告大纲） | 被引用的资料，每条带（问题, 查询） | 一棵可序列化的树：节点名、挂的资料编号、资料表 | 树能整个存成 JSON（`to_dict`）；插入与重组要模型与嵌入配合，附录 B 表明只靠模型一次放准的比例 3%–8% | `knowledge_storm/dataclass.py:242-256,362-372`、`knowledge_storm/collaborative_storm/modules/information_insertion_module.py` |
| 人参与 | 文献阶段的对话 | 研究者随时插的一句话 | 插话被当成新问题，下一轮据此换专家名单 | 平台的人参与是「和助理对话 + 断点处人确认」（P-18）；Co-STORM 没有确认或否决的概念，人的作用只是转向 | `knowledge_storm/collaborative_storm/engine.py:702-709,731-738` |

两篇论文都不产假设，也不评估研究问题的新颖性；Co-STORM 的「新颖」量表评的是讨论与报告对读者是否有新信息（§5.2、附录 D 表 9–11）。

## 4. 局限与前提

### 4.1 数据与网络

- **检索源是通用网页**：评测都跑在 You.com 搜索 API 上（STORM §4.4、Co-STORM §4），评测集是维基百科条目（FreshWiki）与网站用户的话题（WildSeek），都不是学术文献检索。仓库里面向论文的检索只有两样：`StanfordOvalArxivRM` 注明「仅内部使用」、POST 到调用方给的斯坦福端点；`VectorRM` 用用户自备的 CSV（content / title / url / description）建 Qdrant 库，示例拿 Kaggle 的 arXiv 摘要集筛了 cs.CV、URL 用 `uid_N` 编号代替（`knowledge_storm/rm.py:179-341`、`knowledge_storm/utils.py:152-250`、`examples/storm_examples/helper/process_kaggle_arxiv_abstract_dataset.py:1-36`）。用 `VectorRM` 时视角发现照样去抓维基百科。
- **维基百科**：视角发现依赖抓 wikipedia.org 的页面；全部失败时不报错，退化成纯模型列角色（`knowledge_storm/storm_wiki/modules/persona_generator.py:85-94`）。OONI 2019 年测得中国封锁了全部语言版本的维基百科[^ooni]，2026 年的可达性本文没有测。
- **Hugging Face**：STORM 写作阶段的 `paraphrase-MiniLM-L6-v2` 按名字加载，首次使用从 Hugging Face 下载（`knowledge_storm/storm_wiki/modules/storm_dataclass.py:110`）；大陆网络下能否直连未验证。
- **默认搜索后端**：Co-STORM 的 `CoStormRunner` 与问答模块不给检索器时缺省 `BingSearch`（`knowledge_storm/collaborative_storm/engine.py:518-519`、`knowledge_storm/collaborative_storm/modules/collaborative_storm_utils.py:252-253`），Bing Search API 已于 2025-08-11 停止服务[^bing]。其它后端各有账号与条款：You.com、Serper、Brave、Tavily、Google CSE、Azure AI Search 要 key；SearXNG 要一个实例地址；DuckDuckGo 走第三方库、不要 key。大陆网络下哪些能用，未验证。
- **偏向传递**：编辑意见里「语气不中立」与「无关事实被扯到一起」是最多的两类（STORM 表 11），论文把它归因于网页来源本身的偏向与模型的过度推断，代码里没有针对它的处理（伦理声明一节也承认「没有后处理模块」）。
- **英文**：两篇论文都只做英文（STORM 伦理声明、Co-STORM 局限与伦理声明）；提示词全是英文、面向维基百科写作。

### 4.2 模型与调用方式

- **代码自己调模型**：每个模块用 dspy 调 `LitellmModel` 或各家适配器（`knowledge_storm/storm_wiki/engine.py:38-109`、`knowledge_storm/collaborative_storm/engine.py:40-142`、`knowledge_storm/lm.py`）。云端后端要 key；仓库也有 Ollama、vLLM、TGI 等本地后端，STORM 有 Ollama 配 DuckDuckGo 或 SearXNG 的示例（`examples/storm_examples/run_storm_wiki_ollama.py:56-60,92,107`、`knowledge_storm/lm.py:845,935-945`），按代码静态看 STORM 可以一个云端 key 都不用（未运行）。Co-STORM 的主持人重排与思维导图插入离不开 `Encoder`，它只接 OpenAI 或 Azure（`knowledge_storm/encoder.py:78-95`），不改代码就要这两家之一的 key。
- **缺省模型**：STORM 的 `init_openai_model` 用 gpt-4o-mini 提问与对话、gpt-4-0125-preview 写大纲、gpt-4o 写正文与润色；GPT 示例脚本用 gpt-3.5-turbo 提问与对话、gpt-4o 写其余（`examples/storm_examples/run_storm_wiki_gpt.py:58-81`）。Co-STORM 的 `init("openai")` 五个角色用 gpt-4o-2024-05-13、warm start 写大纲用 gpt-4-1106-preview，另有 together 选项全用 Llama-3.1-70B；Co-STORM 示例脚本六个角色全用 gpt-4o（`examples/costorm_examples/run_costorm_gpt.py:67-95`）。论文实验用的是 gpt-3.5-turbo / gpt-3.5-turbo-instruct / gpt-4（STORM §4.4）与 gpt-4o-2024-05-13（Co-STORM §4）。
- **嵌入**：STORM 写作阶段用本地 `paraphrase-MiniLM-L6-v2`；Co-STORM 的主持人重排、思维导图插入全部依赖 OpenAI 或 Azure 的 `text-embedding-3-small`，不支持别的（错误信息里提到 together，代码没有这个分支）。
- **强模型的前提**：STORM 只报 gpt-4 写正文的结果，因为 gpt-3.5 带引用写作不忠于来源（§4.4）。
- **依赖版本**：`dspy_ai==2.4.9` 钉死，代码大量用 2.4 系的 `dspy.OpenAI`、`dspy.dsp.LM`、`dspy.HFModel` 等接口（`requirements.txt`、`knowledge_storm/lm.py:276-1159`）；与新版 DSPy 的兼容性未验证。2025-09-30 的提交把 `numpy`、`litellm` 从钉死改成不限版本，没有锁文件；不限版本的 litellm 与 `knowledge_storm/lm.py` 用到的 `litellm.caching.caching` 路径是否兼容，未验证。`import knowledge_storm.lm` 或 `encoder` 会把 litellm 的全局缓存设到 `~/.storm_local_cache`，LM 调用缺省走缓存（`knowledge_storm/lm.py:42-43,64`、`knowledge_storm/encoder.py:22-23`）。

### 4.3 算力与调用量

两者都不需要 GPU（除非用本地模型）。论文都没报成本或时延数字，Co-STORM 局限一节只说「比 RAG 聊天时延高」。按代码静态数的调用次数（下限，未实测）：

| 场景 | 模型调用 | 搜索查询 | 证据 |
|---|---|---|---|
| STORM，main 缺省（3 个角色 + 基础事实，每段 3 轮，每轮 ≤3 条查询） | 视角 2 + 对话 4×3×3=36 + 大纲 2 + 每个一级节 1 + 导语 1；按人写条目的平均节数 8.4 估（生成大纲的节数未测），约 50 次 | ≤36 | `knowledge_storm/storm_wiki/modules/knowledge_curation.py:60-79,207-216`、STORM 表 7 |
| STORM，论文设置 N=M=5（每轮 ≤5 条查询） | 对话 6×5×3=90，合计约 105 次 | ≤150 | `NAACL:src/modules/topic_expert.py:163` |
| Co-STORM 一个专家回合（答案类意图） | 导图摘要 1 + 选意图 1 + 拆查询 1 + 回答 1 + 润色 1 + 每个（问题, 查询）至少 1 次放置，≥6 次，另有若干嵌入 | ≤2 | `knowledge_storm/collaborative_storm/modules/co_storm_agents.py:78-107`、`knowledge_storm/collaborative_storm/modules/information_insertion_module.py:237-259` |
| Co-STORM 通用专家答问题的回合 | 导图摘要 1 + 拆查询 1 + 回答 1 + 润色 1 + 生成新专家名单 1 + 放置若干，≥6 次 | ≤2 | `knowledge_storm/collaborative_storm/engine.py:731-738`、`knowledge_storm/collaborative_storm/modules/costorm_expert_utterance_generator.py:110-116` |
| Co-STORM 主持人回合（连续答题触发） | 导图摘要 1 + 生成问题 1 + 润色 1 + 放置若干 + 重组（每个资料数 ≥10 的节点 1 次展开，再把它的资料重新放置），另有若干嵌入 | 0 | `knowledge_storm/collaborative_storm/modules/grounded_question_generation.py:81-113`、`knowledge_storm/collaborative_storm/modules/information_insertion_module.py:391-424` |
| Co-STORM warm start（缺省 3 位专家各 2 轮） | 背景 2 + 名单 1 + 3×2×3=18 + 大纲 2 + 放置若干 + 报告每节点 1 + 报告改对话每节点 1 + 结束时重组若干 | ≤14 | `knowledge_storm/collaborative_storm/modules/warmstart_hierarchical_chat.py:157-256,346-408`、`knowledge_storm/collaborative_storm/engine.py:621` |

### 4.4 许可证

- 代码 MIT（`LICENSE`、`setup.py:26`），提示词在代码里，同一许可证。
- FreshWiki 与 WildSeek 在 Hugging Face 上标 CC BY-SA 4.0[^hf]；FreshWiki 内容来自维基百科（`README.md:322`）。
- 运行时抓取的维基百科目录会进 `GenPersona` 的提示词；`post_run()` 把每次调用的 prompt 写进 `llm_call_history.jsonl`，litellm 的磁盘缓存 `~/.storm_local_cache` 也存请求，所以这部分内容会落盘（`knowledge_storm/storm_wiki/engine.py:301-310`、`knowledge_storm/lm.py:100-107`）。各搜索 API 的服务条款未逐一查。

### 4.5 仓库状态

31.5k star、2967 fork；60 个未关 issue、50 个未合 PR（GitHub 的 `open_issues_count` 110 把两者算在一起）；最近一次 GitHub Release 是 v1.1.0（2025-01-23）；之后 main 上只有 5 个提交（含 2 个合并），内容是改拼写、改 README、放宽 `numpy` 与 `litellm` 的版本限制并把 `setup.py` 版本改成 1.1.1（2025-09-30）[^repo]。`knowledge_storm/__init__.py` 的 `__version__` 还是 1.1.0，而发布工作流第一步就比对这两个版本号，不一致即失败（`setup.py:19`、`knowledge_storm/__init__.py:10`、`.github/workflows/python-package.yml:17-27`，静态推断）。main 上没有测试；CI 只有两条：PR 上跑 black 格式检查，和手动触发的打包发布（`.github/workflows/`）。STORM 论文的评测脚本在 NAACL 分支的 `eval/` 下（大纲、文章、引用质量），main 上没有。

## 5. 还没弄清的问题

| 问题 | 为什么要紧 | 怎么查 |
|---|---|---|
| 视角的增益有多少来自「相关条目的目录」，多少来自「让模型列角色」本身 | 取不到维基百科时代码会静默退化成后者；论文没有分开消融 | 同一批主题跑「有目录 / 目录为 N/A」两组，比来源数与大纲召回（表 5 的口径） |
| 论文实验时来源过滤实际滤掉了多少 | 对 NAACL 快照的静态计算只有 5 条规则能命中小写域名，表 3、表 5 的数字多半等于「没过滤」；但没见到实验日志 | 在 NAACL 分支上拿实验日志，或重放一批 You.com 结果，数被 `is_valid_wikipedia_source` 拒的条数 |
| 「去视角」消融怎么保证问题总数相等 | 论文说控制了问题总数相等；NAACL 分支的开关是一条通用对话、轮数仍是 `max_conv_turn`，按缺省值只有完整版的六分之一问题，实验时怎么设的参数没有公开 | 看 NAACL 分支是否有实验配置或日志；或问作者 |
| 最终文章的小节结构与大纲差多少 | 写作不收小节大纲、正文子标题会覆盖大纲，论文按大纲评了召回，但文章结构没有单独评 | 对同一批输出比 `storm_gen_outline.txt` 与 `storm_gen_article.txt` 的标题树 |
| 平台的 CLI 会话自带的搜索工具，能不能给出 STORM 需要的「编号稳定的正文片段」 | STORM 的回答、编号清洗、逐节检索都建立在「每条结果有 URL + 片段」之上；自带搜索的返回形状因家而异 | 在 Claude Code 与 Codex 里各跑一次搜索，看返回里有没有片段正文、能不能拿到原文 |
| 嵌入这几步（逐节检索、导图候选、主持人重排）能不能由 agent 自己判断代替 | 附录 B 显示只靠模型一次放准的比例 3%–8%（部分正确 62.5%–71.4%）；Co-STORM 的嵌入绑定 OpenAI / Azure | 用附录 B 的 111 个任务口径，比「向量候选 + 模型挑」与「只让 agent 看全树挑」 |
| 多个角色是开几个独立会话，还是在一个会话里轮流扮演 | STORM 每个角色是独立线程、上下文互不相通；「去对话」消融说明读到答案再问是关键，但没测角色之间共享上下文的影响 | 对照实验：同一主题，独立会话 vs 单会话轮流，比问题重复率与来源数 |
| Co-STORM 主持人用论文式 (1) 还是代码里的式子，哪个产出了表 3 的数 | 评测代码没有公开，两者差一个「与主题相似」项和一个「与已引用不相似」项 | 向作者确认或等 `EMNLP-2024-code-backup` 分支；也可以两式各跑一批比新颖分 |
| 以思维导图为大纲写的报告质量如何 | 表 3 的报告是 STORM 两段法写的（§5.1），人评里的报告用哪种写法论文没说；main 上只有导图写法 | 同一批对话分别用两种写法出报告，按表 3 的量表比 |
| 在学术文献上效果如何 | 两个评测集都是通用话题 + 网页检索；学术综述要的是论文级来源、方法对比，而不是百科式覆盖 | 找有人拿 STORM 做学术综述的评测，或用 `VectorRM` 接一个论文摘要库自测 |
| 「缺引用」占不被支持句子的 47% | 写作提示只要求「带引用」，代码没有逐句检查有没有挂引用 | 在输出上数「无 `[n]` 的陈述句」比例，看零模型规则能卡住多少 |

## 6. 调研方法

- 论文用 `curl` 从 arXiv 下载到外层 `materials/research/2026-0927-scientific-ai-capabilities/papers/`，用平台的 `pdf` skill 解析成 markdown，正文、附录与 STORM 图 6、Co-STORM 图 3、图 4 逐一看过原图；Co-STORM 图 3 的柱高是读图估计。
- 代码只读不跑：`knowledge_storm/` 下 STORM 与 Co-STORM 的全部模块、`interface.py`、`dataclass.py`、`utils.py`、`encoder.py`、`rm.py` 的检索器与过滤部分逐行读；`run_storm_wiki_gpt.py`、`run_storm_wiki_ollama.py` 与 `run_costorm_gpt.py` 读了主流程与参数。NAACL 分支的 5 个源文件与维基百科页面快照经 `gh api` 取回对照。
- 过滤规则的计数：main 上把 `knowledge_storm/storm_wiki/modules/retriever.py` 里的三个集合当 Python 字面量读出来算；NAACL 分支按 `NAACL:src/modules/topic_expert.py:41-63` 的同一组正则在页面快照上取 id 再算，没有运行项目代码。大纲清洗正则的连带删除，是把 `knowledge_storm/utils.py:498` 的同一正则放在样例字符串上用 Python `re` 试出来的。
- 仓库元数据（star、分支、Release、提交、issue 与 PR 数）与数据集许可证用 `gh api` 与 Hugging Face API 在 2026-09-27 查。

[^storm]: Yijia Shao 等，Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models，NAACL 2024，<https://arxiv.org/abs/2402.14207>。
[^costorm]: Yucheng Jiang、Yijia Shao 等，Into the Unknown Unknowns: Engaged Human Learning through Participation in Language Model Agent Conversations，EMNLP 2024，<https://arxiv.org/abs/2408.15232>。
[^repo]: GitHub 仓库 <https://github.com/stanford-oval/storm>，2026-09-27 经 `gh api` 查：分支列表（NAACL-2024-code-backup 头 7f6f5df，其 `eval/` 目录有 citation_quality.py、eval_article_quality.py、eval_outline_quality.py；costorm-integration 头 efac123、最后提交 2024-09-25；无 EMNLP-2024-code-backup）、Release 列表、main 提交记录、未关 issue 60 与未合 PR 50（search API）。WildSeek 数据集：<https://huggingface.co/datasets/YuchengJiang/WildSeek>。
[^ooni]: OONI，China is now blocking all language editions of Wikipedia，2019，<https://ooni.org/post/2019-china-wikipedia-blocking/>。
[^bing]: Microsoft Learn，Bing Search APIs Retiring on August 11, 2025，<https://learn.microsoft.com/en-us/lifecycle/announcements/bing-search-api-retirement>。
[^hf]: Hugging Face 数据集页：<https://huggingface.co/datasets/EchoShao8899/FreshWiki>、<https://huggingface.co/datasets/YuchengJiang/WildSeek>，许可证字段均为 cc-by-sa-4.0（2026-09-27 经 API 查）。
