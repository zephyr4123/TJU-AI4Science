---
title: AI Scientist（一代与二代）方法深读
subtitle: 研究创意选型 · 出想法与查新：提示词、反思轮数、打分字段、Semantic Scholar 判定，论文与代码逐条对账
kind: 开源项目方法借鉴（只读论文与代码，不跑、不装依赖、不评估整体接入）
date: 2026-09-27
scope: 一代仓库 https://github.com/SakanaAI/AI-Scientist 提交 1de1dbc（2025-12-19），二代仓库 https://github.com/SakanaAI/AI-Scientist-v2 提交 96bd516（2025-12-19），均浅克隆到外层 vendor/；论文一代 arXiv 2408.06292（下载时最新是 v3，2024-09-01）、二代 arXiv 2504.08066（只有 v1，2025-04-10），均 2026-09-27 下载。只深读出想法与查新，实验与写作一两句带过。文中 文件:行 相对各自仓库根；两代同名的文件（llm.py、README.md、LICENSE、perform_writeup.py）前面标「一代」「二代」，平台一侧的路径标「外层」「内仓」
status: 第一版
---

> **结论先行**：两代「出想法」是同一个形状：把研究方向描述（一代还有整份基线代码）和已经出过的全部想法原文一起放进 prompt，让模型出一条「和前面不一样」的结构化想法，再在同一段对话里自我反思几轮。差别在查新。**一代**出完一批想法后，每条单独开一段对话，让模型扮「苛刻的查新者」：每轮给一个检索词、看 Semantic Scholar 前 10 条的摘要，最多 10 轮，靠回复里的字符串 `Decision made: novel / not novel` 判定（代码不数检索次数，第 1 轮一次没检索就写判定串也算数；10 轮用完没判定算不新），只存一个布尔值 `novel`，主流程只跑判新的想法。**二代**去掉了单独的查新和这个布尔值，检索变成出想法循环里模型可选的一次工具调用，最终只多一个模型自己写的「Related Work」字段；没有判定、没有过滤，挑哪条去跑实验由人用 `--idea_idx` 指定。二代的树搜索只用在实验的四个阶段，出想法里没有树。
>
> 证据：两篇论文都没有消融出想法的反思轮数（一代唯一的反思消融做在自动审稿人上），也没有拿标准答案测过查新准不准。一代表 3 到表 5 的「Novel Ideas」就是查新自己的输出，论文自己说这是各模型给自己的想法判的、彼此不可比；附录 C 的 50 条想法里，自评有趣度 48 条是 9 分，自评新颖度 49 条在 8 到 9 分，46 条判新，其中有两对同名重复想法。代码里三个自评分数没有任何读取点。独立评测（Beel 等）用 gpt-4o 在推荐系统任务上跑，10 条生成想法加 2 条种子全部判新，包括 SGD 的 micro-batching 这种已知做法。一代论文与 2026 年的 Nature 版都写查新「接 Semantic Scholar 与网页访问」，Nature 版还写「与已有工作语义相似度高的丢弃」；代码里没有网页访问工具，也没有任何相似度计算，判定全靠模型写的那个字符串。
>
> 这次摘出的方法件五样：带存档的出想法加早停串、二代的七字段想法表（下游实验硬读其中五个）、有轮数上限的检索判定循环、检索进出想法循环、写作时 bibtex 从检索 API 取而不让模型写（取的是 S2 返回的 `citationStyles` 字段，一代的 OpenAlex 分支没有这个字段）。它们在平台上对应假设阶段（主文件未定名）与文献、写作阶段，对照在[第 4 节](#4-平台哪里能用)。许可证 2025-12-19 从 Apache 2.0 改成 AI Scientist Source Code License，带五类使用限制，其中一条要求用它产出的论文显著声明机器生成，条款要点在[第 5.1 节](#51-许可证条款要点)。横向对比见同目录的 [README.md](README.md)。

## 1. 结论

| 问题 | 论文 / README 说 | 代码里 | 证据 |
|---|---|---|---|
| 一代出想法的提示词 | 以代码模板为起点，借鉴进化计算与开放式研究，用 LLM 做变异算子不断扩充想法存档（一代论文 §3） | 首轮 prompt = 模板的 `task_description` + 整份 `experiment.py` + 存档里全部想法的 JSON 原文，要求出「下一个有影响、有创意、用给定代码可行」的想法，并告知拿不到额外资源或数据集、想法不要过拟合特定数据集或模型；系统提示取模板里 `prompt.json` 的 `system` | `ai_scientist/generate_ideas.py:14-52`、`:98-110` |
| 反思轮数 | 附录 B 表 6：3 轮 | 主流程 `NUM_REFLECTIONS = 3`（首轮算第 1 轮，再反思 2 轮），同一段对话里做，模型写「I am done」就提前停；单独跑 `generate_ideas.py` 时是 5 | `launch_scientist.py:22`、`ai_scientist/generate_ideas.py:54-72`、`:138-159`、`:497` |
| 打分字段 | 每条想法带自评的有趣度、新颖度、可行性（§3）；§5 承认 LLM 自评会高估 | `Interestingness` / `Feasibility` / `Novelty` 各 1 到 10，只出现在 prompt 里，全仓 grep 没有读取点；查新另写一个布尔 `novel` | `ai_scientist/generate_ideas.py:45-49` |
| 一代查新的判定 | 接 Semantic Scholar API 与网页访问当工具，丢掉与已有文献太像的想法（§3）；附录 B：10 轮 | 每条想法一段新对话；每轮模型给一个 `Query`，框架调 S2 `/graph/v1/paper/search` 取前 10 条（含摘要）喂回；回复里出现判定串就停，判定检查排在抽 JSON 与检索之前，第 1 轮不检索也能判；10 轮用完没判就是「不新」；只存 `novel`；主流程只跑 `novel` 为真的。没有通用网页访问，另一个检索源是 OpenAlex | `ai_scientist/generate_ideas.py:285-352`、`:356-492`（判定 `:448-454` 早于检索 `:457-462`）、`launch_scientist.py:351-363` |
| 二代与一代的差别 | 从更高抽象层出发、像写基金申请；检索进循环，出想法时就查新（二代论文 §3.1） | 输入换成一份主题 Markdown，不要代码；每轮模型二选一：`SearchSemanticScholar` 或 `FinalizeIdea`；字段换成七个文本字段，三个分数与 `novel` 都去掉；「至少检索一次」只写在 prompt 里；没有查新判定、没有过滤。S2 key 现在可选，但仓库初版没有 `S2_API_KEY` 时检索工具直接抛错，2025-04-17 才改 | `ai_scientist/perform_ideation_temp_free.py:24-39`、`:61-96`、`:158-250`；提交 39ee150 [^v2-commits] |
| 树搜索用在哪 | 四个实验阶段都用 agentic tree search（二代论文 §3.2.2） | 只在实验：启动器从想法 JSON 里按下标取一条，之后才进树搜索；四个阶段是初步实现、调参、创造性研究、消融 | `launch_scientist_bfts.py:191-256`、`ai_scientist/treesearch/agent_manager.py:143-167` |
| 想法质量与查新准确度的评估 | 一代：表 3–5 报判新条数，§6 说是自评、不可比；二代：没有；Nature 版正文：没看到 | 两篇都没有对出想法的消融、没有标准答案对照；独立评测给出反例 | 一代论文 §4 §5 §6 §8、附录 C；二代论文 §4；Beel 等 [^beel]；Nature 版 [^nature] |
| 许可证 | README：用它产出的论文必须显著声明使用了 AI | 两仓同一份 LICENSE（2025 年 12 月版 1.0），2025-12-19 从 Apache 2.0 改来 | 一代 `LICENSE:1-53`；提交 2906fcb、c204ee8 [^lic] |

## 2. 方法是什么

### 2.1 一代：出想法

输入是模板目录里的三个文件（`ai_scientist/generate_ideas.py:98-110`）：`seed_ideas.json`（人写的种子想法，格式与输出相同；仓里 11 套模板各一到三条，论文用的 2d_diffusion、nanoGPT、grokking 是一到两条）、`experiment.py`（基线实验代码全文）、`prompt.json`（`system` 与 `task_description` 两句话，比如 nanoGPT 模板是「雄心勃勃的 AI 研究者」与「给你的文件在多个字符级数据集上训练多个小语言模型」，`templates/nanoGPT/prompt.json`）。

流程（`ai_scientist/generate_ideas.py:112-172`）：

1. 存档先放种子想法的 JSON 字符串，每出一条就追加一条（`:98-102`、`:161`）。
2. 每条想法开一段新对话。首轮 prompt 拼上任务描述、整份代码、存档里全部想法原文，要求先写 THOUGHT 再写 JSON，THOUGHT 里要「说明这个想法和已有的有何不同」（`:14-52`）。这是它唯一的去重手段：靠 prompt 里的存档原文，没有任何相似度计算。
3. 之后在同一段对话里反思 `num_reflections - 1` 轮。反思提示要求考虑质量、新颖度、可行性，「除非有明显问题，否则保持原想法的方向」；没什么可改就原样重复 JSON 并写「I am done」，框架看到这个串就停（`:54-72`、`:138-159`）。
4. JSON 从标了 json 的代码围栏里抽，抽不到退到正则找花括号（一代 `ai_scientist/llm.py:289-314`）；还抽不到就 `assert` 失败，整条想法被外层 `except` 打印一行后跳过（`:132-134`、`:162-164`）。
5. 全部写进 `ideas.json`，种子也在里面、排在最前（`:166-172`），所以种子同样会被查新、判新后同样会被执行。例外：社区加的 earthquake-prediction、sketch_rnn 两套模板，种子里预置了 `"novel": true`，查新时按「已查过」跳过（`:420-422`），直接进执行（`templates/earthquake-prediction/seed_ideas.json`、`templates/sketch_rnn/seed_ideas.json`）。

想法 JSON 六个字段（`:41-47`）：`Name`、`Title`、`Experiment`（实现提纲：改哪些函数、结果怎么拿）、`Interestingness`、`Feasibility`、`Novelty`，后三个是 1 到 10 的自评分，prompt 另加一句「评分要谨慎务实」（`:49`）。

参数：主流程出 50 条（`launch_scientist.py:79-84`）、3 轮（`:22`），查新默认开；单独跑 `generate_ideas.py` 是 32 条、5 轮，查新要加 `--check-novelty` 才跑（`:496-497`、`:520-546`）；温度用默认 0.75（一代 `ai_scientist/llm.py:150`），论文附录 B 表 6 只列了审稿温度 0.1。

开放式变体 `generate_next_idea`（`:178-272`）每次只出一条（存档为空的第一次调用只放入第一条种子、不生成，`:191-197`），prompt 追加一句「已完成的想法带 Score 字段，是专家 ML 审稿人按 1 到 10 打的分，0 分表示实验、写作或审稿失败」（`:221-225`），分数由 `experimental/launch_oe_scientist.py:133`、`:390` 写回存档。论文 §3 说的「存档里可以带已完成想法的审稿分」只在 `experimental/` 下这个启动器里有；论文 §6 也说正式实验没等审稿分回来，一次性出完所有想法。

### 2.2 一代：查新

`check_idea_novelty`（`ai_scientist/generate_ideas.py:405-492`），每条想法一段新对话（`:427` 清空对话历史）：

| 环节 | 做法 | 证据 |
|---|---|---|
| 身份 | 系统提示：雄心勃勃的 AI 博士生，要判断想法是否与已有文献明显重叠，「做苛刻的查新者」，确保够一篇会议或 workshop 论文；附上任务描述与整份 `experiment.py` | `:356-371` |
| 每轮输入 | 轮次号、想法本身（Python dict 直接格式化，含三个自评分）、上一轮检索结果（首轮为空） | `:373-383`、`:432-447` |
| 每轮输出 | THOUGHT + 只有 `Query` 一个字段的 JSON；判定了就在 THOUGHT 里写 `Decision made: novel.` 或 `Decision made: not novel.`。提示说「能想起确切论文名或作者时检索效果最好」 | `:385-402` |
| 检索 | S2 `/graph/v1/paper/search`，`limit=10`，字段 title / authors / venue / year / abstract / citationStyles / citationCount；设了 `S2_API_KEY` 就带上；成功返回后睡 1 秒（出错走退避，不睡）。或 OpenAlex（`--engine openalex`，要装 `pyalex`，摘要截到 1000 字符，返回的字段里没有 `citationStyles`） | `:285-352`（睡眠 `:305`，OpenAlex 字段 `:338-345`） |
| 判定 | 回复转小写后找子串：先找 `decision made: novel`，再找 `decision made: not novel`（两者不会互相命中，中间隔着 `not `）。判定检查在抽 JSON 与检索之前，模型第 1 轮一次都没检索就写判定串也会被接受；系统提示里「充分检索后没找到重叠才判新」只是文字要求，代码不数检索次数 | `:448-454`、`:457-462`、`:364` |
| 默认值 | 10 轮用完没判定：`novel = False` | `:410`、`:426`、`:485` |
| 出错 | 任何异常（JSON 抽不到、`ConnectionError` 这类不在退避范围里的网络错）打印后 `continue`，这一轮算用掉；对话历史保留，下一轮模型看到的检索结果还是上一次成功的那份 | `:481-483` |
| 检索为空 | `papers is None` 时先把结果设成「No papers found.」，紧接着对 `None` 做 `enumerate` 抛 TypeError，被上面的 `except` 接住；下一轮模型看到的仍是「No papers found.」——结果对，但走的是异常路径 | `:463-467` |
| 留痕 | 只写回 `idea["novel"]` 一个布尔；检索词、返回的论文、判定理由只打到 stdout | `:485-490` |
| 续跑 | 已经有 `novel` 键的想法跳过 | `:420-422` |
| 用在哪 | 主流程 `novel_ideas = [idea for idea in ideas if idea["novel"]]`，只跑判新的 | `launch_scientist.py:363` |

退避装饰器 `@backoff.on_exception(backoff.expo, requests.exceptions.HTTPError)` 既没设 `max_tries` 也没设 `max_time`（`:282-284`）。`rsp.raise_for_status()`（`:302`）把所有 4xx、5xx 都抛成 HTTPError，所以不只 429，其他 4xx（请求本身有错这类重试也不会好的）与 5xx 也会无上限重试。issue #78「always backing off」与 #133 贴出的日志就是 429 加退避；#116「检索阶段卡了一小时」贴出的日志里都是 200，维护者只是猜没 key 或超时，原因没有定论。维护者在 #78 的回复是没 key 时限速每秒 1 次、可以先把查新注释掉让它跑全部想法 [^v1-hang]；社区为此加了 OpenAlex（PR #135，2025-01-14 合入）[^v1-openalex]。

### 2.3 二代：出想法与检索合在一个循环里

`ai_scientist/perform_ideation_temp_free.py`，319 行，文件名的 temp_free 指不依赖代码模板。

- **输入**：一份主题 Markdown，README 要求写 Title、Keywords、TL;DR、Abstract（二代 `README.md:101`，样例 `ai_scientist/ideas/i_cant_believe_its_not_better.md`），不需要代码。输出写到同名 `.json`（`:309`），文件已存在就先读进来当存档（`:137-146`）。
- **系统提示**（`:61-96`）：有经验的 AI 研究者，提「像激动人心的基金申请」那样的高影响想法、「确保新颖」；每个提案源自一个简单优雅的问题、观察或假设，说清与现有文献的区别；资源不超过学术实验室负担得起的；要能发在顶级 ML 会议；「定稿前至少做一次文献检索」。
- **每一轮**：模型回复 `ACTION:` + `ARGUMENTS:`，ACTION 二选一：`SearchSemanticScholar`（参数 `{"query": ...}`）或 `FinalizeIdea`（参数 `{"idea": {...}}`）（`:24-39`、`:69-92`）。框架用正则抽出两段（`:184-206`）；检索就调工具，结果放进下一轮的反思提示（`:209-224`、`:111-125`）；定稿就追加到存档，开始下一条（`:225-237`）。
- **提示词**：首轮 = 主题描述 + 已出过的全部提案原文 +「出一个与以前不同的新提案」（`:99-108`）；后续轮的反思提示与一代几乎同文，多一句「有工具返回的新信息就据此改进」（`:111-125`）。没有「I am done」，定稿就是停止条件。
- **检索工具**：同一个 S2 端点，前 10 条，字段里没有 `citationStyles`，**按引用数降序重排**后才给模型（`ai_scientist/tools/semantic_scholar.py:57-85`）；这个方法里没有一代那样的 1 秒间隔；退避同时接 HTTPError 与 ConnectionError，同样不设上限（`:52-56`），断网时一旦模型选了检索就会一直等。仓库初版（f85bb03）没有 `S2_API_KEY` 时这个工具构造时就抛 `ValueError`，2025-04-17 的 39ee150 才改成只警告 [^v2-commits]。没有 OpenAlex，社区的两个 OpenAlex PR 一个关闭未合、一个未合 [^v2-openalex]。
- **七个字段**（`:30-37`）：`Name`、`Title`、`Short Hypothesis`（要说清为什么非这个方向不可、有没有更简单的回答办法）、`Related Work`（最相关的工作与区别，「不是平凡扩展」）、`Abstract`（约 250 词）、`Experiments`（简单可行、写清怎么检验假设、精确的算法改动、评价指标）、`Risk Factors and Limitations`。
- **失败**：解析失败 `break`，这条想法作废（`:245-250`）；ACTION 不认识只打印、不告诉模型（`:240-244`）；`num_reflections` 轮内没定稿，这条也作废（`:158-253`）。全都只打到 stdout。
- **参数**：`--num-reflections` 默认 5（`:292-297`），`--max-num-generations` 默认 1（`:280-285`），模型默认 gpt-4o-2024-05-13（`:276`），温度默认 0.7（二代 `ai_scientist/llm.py:274`）。
- **下游怎么读**：启动器按 `--idea_idx` 取一条（`launch_scientist_bfts.py:63-67`、`:195`）；实验侧 `AgentManager` 要求 Title、Abstract、Short Hypothesis、Experiments、Risk Factors and Limitations 五个键都在，缺一个就抛错（`ai_scientist/treesearch/agent_manager.py:124-134`）；每个阶段都拼进 Title、Abstract、Short Hypothesis，启动时加了 `--load_code` 或 `--add_dataset_ref` 还有 Code（`:179-198`；`launch_scientist_bfts.py:205-242`），Experiments 只在第 3 阶段、Risk Factors 只在第 4 阶段拼进任务描述（`:216-247`），第 1、2 阶段看不到实验计划。各阶段目标里另写死了数据集要求：第 2 阶段「再引入两个 HuggingFace 数据集」、第 3 阶段「总共用三个 HuggingFace 数据集」（`:155-163`）。Related Work 不进实验，只经 `idea.md` 进写作（`ai_scientist/treesearch/bfts_utils.py:7-41`、`ai_scientist/perform_icbinb_writeup.py:648-662`）。

### 2.4 两代差别

| | 一代 | 二代 | 证据 |
|---|---|---|---|
| 输入 | 模板目录：基线代码 + 两句描述 + 种子想法 | 一份主题 Markdown | 一代 `ai_scientist/generate_ideas.py:98-110`；二代 `perform_ideation_temp_free.py:303-316` |
| 对想法的约束 | 整份代码进 prompt，「用给定代码可行、不用额外资源或数据集」 | 不看代码，「学术实验室负担得起」 | 一代 `:25-27`；二代 `:63` |
| 字段 | 3 个文本 + 3 个自评分 + 查新布尔 | 7 个文本，没有分数也没有布尔 | 一代 `:41-47`；二代 `:30-37` |
| 反思 | 主流程 3 轮，「I am done」早停 | 最多 5 轮，定稿即停 | `launch_scientist.py:22`；二代 `:292-297` |
| 检索时机 | 出完一批后，每条单开一段对话查新 | 出想法过程中，模型自己决定查不查 | 一代 `:405-492`；二代 `:209-224` |
| 查新判定 | 字符串判新 / 不新，默认不新 | 没有 | 一代 `:448-454`、`:485` |
| 过滤 | 只跑判新的 | 没有，人挑 `--idea_idx` | `launch_scientist.py:363`；`launch_scientist_bfts.py:195` |
| 检索源 | S2 或 OpenAlex | 只有 S2，结果按引用数重排 | 一代 `:285-352`；二代 `tools/semantic_scholar.py:83-84` |
| 留下什么 | `ideas.json` 里的想法与布尔 | 只有定稿的想法 JSON | 一代 `:487-490`；二代 `:260-265` |

### 2.5 树搜索用在哪

实验，不在出想法。二代启动器先读想法 JSON、按下标取一条（`launch_scientist_bfts.py:191-195`），转成 `idea.md` 与 `idea.json`（`:217`、`:245-247`），然后才调 `perform_experiments_bfts`（`:249-256`）。树搜索的四个阶段写死在 `AgentManager`：初步实现、调参、创造性研究、消融（`ai_scientist/treesearch/agent_manager.py:143-167`）；选下一个扩展的节点时，先按 `debug_prob` 的概率挑一个可修的 buggy 叶子去修（`ai_scientist/treesearch/parallel_agent.py:1963-2004`）；否则第 2、4 阶段固定扩展上一阶段的最优节点（`:2006-2015`），第 1、3 阶段让 LLM 在非 buggy 节点里挑最好的（`:2016-2036`、`ai_scientist/treesearch/journal.py:420-447`）。论文 §3.2.2 写「四个实验阶段都用」树搜索，图 2 也写第 2、4 阶段从上一阶段选出的根节点生出调参、消融节点，与代码一致。

#175 表里「原稿的匹配点」一行说二代「通过 Agentic Tree Search 扩展、搜索并迭代研究方向与方案」。代码里研究方向在进树之前就由那条想法定死了；树在第 3 阶段的目标里有「探索新的改进、设计揭示新见解的实验」（`agent_manager.py:159-163`），是在这条想法之内找实现与实验方案，不在不同研究方向之间搜索。

### 2.6 实验与写作两句话

一代：Aider 在模板代码上按想法改，最多 5 次实验、每次失败最多重试 4 次（一代论文附录 B 表 6）；写作按节填 LaTeX，再用 S2 检索 20 轮补引用，bibtex 直接取 S2 返回的 `citationStyles`，不让模型写，框架把它插进 `references.bib`（一代论文 §3(b)；一代 `ai_scientist/perform_writeup.py:318` 检索、`:369-370` 取 bibtex、`:401-402` 默认 20 轮、`:474-478` 插入）。OpenAlex 分支返回的论文没有 `citationStyles`（`ai_scientist/generate_ideas.py:338-345`），`--engine openalex` 时 `:369` 会抛 KeyError、被 `:374` 接住，这一轮不加引用；按代码推断整篇论文都加不上引用，未运行验证。一代 issue #179（2025-01-19 开，至今未关）报的就是这个缺字段，OpenAlex PR 的作者回复「我认为这是 bug」[^v1-i179]。二代：实验是基于 AIDE 的并行树搜索（二代 `README.md:196`，README 自述，本篇没有对照 AIDE 代码）；写作改成一次生成加反思，引用同样从 S2 取 bibtex，每轮取 5 条（`ai_scientist/perform_icbinb_writeup.py:450`、`:507`）。另外二代论文附录 A 表 2、表 3 的超参与仓里 `bfts_config.yaml` 有五处对不上：debug 概率 1.0 对 0.5、第 1 阶段 21 对 20 个节点、第 4 阶段 12 对 18 个节点、代码生成温度 0.5 对 1.0、代码生成 max tokens 8192 对 12000（`bfts_config.yaml:40`、`:43`、`:58-59`、`:75`；阶段上限按 `len(journal.nodes)` 计，确实是节点数，`ai_scientist/treesearch/agent_manager.py:398`、`:414`），属实验侧，本篇不展开。

## 3. 为什么有效：证据与对账

### 3.1 论文给了哪些证据

**一代** [^v1paper]：

- 表 3 到表 5 报三个模板、四个模型的判新条数：

  | 模板 | Sonnet 3.5 | GPT-4o | DeepSeek Coder | Llama-3.1 405b |
  |---|---|---|---|---|
  | 2D Diffusion（表 3） | 49 / 51 | 41 / 51 | 42 / 51 | 31 / 51 |
  | NanoGPT（表 4） | 50 / 52 | 44 / 52 | 37 / 52 | 41 / 52 |
  | Grokking（表 5） | 47 / 51 | 51 / 51 | 46 / 51 | 36 / 51 |

  §6 原话的意思是：查新与检索都是各模型给自己的想法做的，模型之间的「新颖」不好比。这一列是查新的输出，不是对查新的评估。
- 附录 C 列了 Grokking 模板、Sonnet 3.5 一次运行的 50 条生成想法加 1 条种子。按附录原文逐条数（数法见[第 7 节](#7-调研方法)）：自评有趣度 48 条 9 分、2 条 8 分；自评新颖度 30 条 9 分、19 条 8 分、1 条 7 分；可行性 6 到 9 分；46 条生成想法判新，加上判新的种子共 47，和表 5 Sonnet 那一行对得上。名字完全相同的想法有两对：`mutual_information_grokking`（第 15、46 条，都判新，内容都是跟踪训练中互信息与 grokking 的关系，一个用分箱估计、一个用 MINE）与 `lottery_tickets_grokking`（第 20、47 条，都判不新）；另有 `critical_periods_grokking`（19）与 `critical_learning_periods_grokking`（32）两条都判新。存档原文在 prompt 里并没有挡住重复，查新也不和存档里的其他想法比。
- §5 案例说，LLM 判断有偏，在想法有趣度、可行性、新颖度的高估上看得到；§8 说出想法常在不同运行、甚至不同模型之间给出很相似的想法。
- §4 验证的是自动审稿人（ICLR 2022 数据上与人类 65% 对 66% 的平衡准确率），评的是成稿论文，不是想法。全文唯一的反思消融也在这里：审稿人加 Reflexion 平衡准确率 +2%。
- 出想法没有反思轮数的消融，没有「有查新 / 没查新」的对比，没有用已知工作做标准答案测查新的准确度。

**二代** [^v2paper]：

- §4.2：以 ICBINB workshop 主题出了约 20 条想法，改系统提示偏向应用领域后又出约 20 条，人从中挑 3 条，每条用不同随机种子跑多遍完整流程，人再挑最好的一篇投稿；3 篇里 1 篇过了 workshop 评审（6、7、6 分）。挑想法与挑成稿都是人做的。
- 被接收那篇的初始想法里，实验计划写的是 SCAN、COGS、IWSLT、GeoQuery（§4.2 与附录 C.1「Initial Idea」），成稿只用了合成的算术表达式数据（§1、§4.2）。这一例里想法的 Experiments 字段没有约束住实验；代码上 Experiments 也只在第 3 阶段进任务描述（见 [2.3 节](#23-二代出想法与检索合在一个循环里)），第 1、2 阶段看不到。
- §4.1 提到成稿里有引用不准确；§5 说「提出真正新颖、高影响的假设」仍是难点。
- 对出想法、对检索都没有任何定量评估；§6 引了 Si 等（人评下 LLM 想法更新颖、可行性更差）和 Beel 等的独立评测，没有针对它们做实验。

两篇论文的证据能支持的是「这套流程能产出结构化想法，并在一代里筛掉一小部分」；「反思让想法更好」「查新能挡住已有工作」两件事，两篇都没有测量。

### 3.2 独立评测

Beel、Kan、Baumgart 用一代跑了一个推荐系统课题：FunkSVD 在 MovieLens-100k 上，目标是找提升能效的新办法，模型 gpt-4o-2024-05-13，两条种子想法 [^beel]。

- 10 条生成想法加 2 条种子**全部判新**，其中 SGD 的 micro-batching、自适应学习率、混合矩阵分解、e-fold 交叉验证都是已有工作（§2.3）。作者把原因归到关键词检索而非对文献的综合；脚注说此前的测试里它偶尔也会判不新，不是永远判新。
- 三个自评分「看起来是随意给的，后续处理不用」（§2.3），与本篇 grep 的结果一致。
- 12 个想法里 5 个（42%）因为代码错误没跑成；成稿的参考文献中位数 5 条，34 条里只有 5 条是 2020 年以后的。
- 作者自己说明只用了一个数据集、一个领域、一组种子和一个模板（§2.8）。
- 他们对机制的描述有一处与代码不符：§2.3 说「没找到明显匹配就判 novel=True」；代码的默认值是 `False`，只有模型写出 `Decision made: novel` 才为真（`ai_scientist/generate_ideas.py:426`、`:448-451`）。这不影响他们观察到的结果（12 条全判新）。

一代仓 issue 里还有一条旁证：S2 对查新词返回 0 条结果，回复的是一位非维护者，说是关键词检索本身的问题 [^v1-empty]。该 issue 贴出的返回格式（`totalHits` / `results`、`limit 5`）与当前代码请求的端点返回格式（`total` / `data`、`limit 10`）不同，报告者跑的可能不是原版代码。

### 3.3 代码是否按论文做

| 论文或 README 说 | 代码 | 证据 | 对得上吗 |
|---|---|---|---|
| 一代：3 轮反思、10 轮查新（附录 B 表 6） | 主流程 3、查新默认 10 且主流程不覆盖 | `launch_scientist.py:22`、`ai_scientist/generate_ideas.py:410` | 对上 |
| 一代：查新接「Semantic Scholar API 与网页访问」（§3）；Nature 版同样写网页访问，并写「与已有工作语义相似度高的想法被丢弃」[^nature] | 只有 S2 检索端点与 OpenAlex，没有通用网页访问；判新靠模型回复里的字符串，没有任何相似度计算（grep `cosine` `embedding` `similarit` 在出想法与查新代码里零命中） | `ai_scientist/generate_ideas.py:285-352`、`:448-454` | 网页访问没有；「语义相似度」没有 |
| 一代：存档可以带已完成想法的审稿分（§3） | 只在 `experimental/launch_oe_scientist.py`；主启动器不回写分数 | `ai_scientist/generate_ideas.py:221-225`、`experimental/launch_oe_scientist.py:133` | 只接了一半，论文 §6 自己说明了 |
| 一代：丢掉与文献太像的想法（§3） | 主启动器按 `novel` 过滤；开放式启动器查完新后不看 `novel`，照样跑 | `launch_scientist.py:363`；`experimental/launch_oe_scientist.py:109-118`、`:368-377` | 主流程对上，开放式没有 |
| 一代 README：没有 S2 key 可以跳过查新与引用阶段（一代 `README.md:137`、`:368`） | `--skip-novelty-check` 存在，但跳过后主流程仍读 `idea["novel"]`；新出的想法没有这个键。论文用的三套模板种子也没有这个键、且排在列表第一个，所以 `:363` 读第一个元素就会 KeyError。这是读代码的推断，未运行；#116 的评论里有人说「注释掉查新后报一堆错」，与此相符但没贴错误 [^v1-hang] | `launch_scientist.py:36-40`、`:351-363`；`templates/grokking/seed_ideas.json` | 新出想法时跳不过去（未运行验证） |
| 一代：每条想法带自评分（§3） | 只在 prompt 里，没有读取点 | `ai_scientist/generate_ideas.py:45-49` | 论文没说拿来用，代码也没用 |
| 二代：出想法时查文献评估新颖度（§3.1）；README 说用 S2「评估想法新颖度」（二代 `README.md:99`、`:188`） | 检索是可选工具；没有新颖度判定；「至少检索一次」只在 prompt | `ai_scientist/perform_ideation_temp_free.py:96`、`:209-237` | 有检索，没有评估 |
| 二代附录 B 系统提示：「确保提案能从给定代码库出发做」 | 代码里的系统提示没有这半句；是论文挂出（2025-04-10）两天后的提交 364aa55 删的，提交说明是「删掉对不存在的代码库的引用」 | `ai_scientist/perform_ideation_temp_free.py:63`；[^v2-commits] | 文与码不一致，原因可查 |
| 二代附录 B 的 IDEA JSON 示例没有外层 `"idea"` 键 | 代码要求 `{"idea": {...}}`，缺了抛 `ValueError`、被外层接住后这条想法作废；2025-05-05 的 c31970c 才把示例改成带 `"idea"` | `ai_scientist/perform_ideation_temp_free.py:79-92`、`:229-231`、`:245-250`；[^v2-commits] | 仓里现在的示例与代码一致，论文里的是旧版 |
| 二代 README：S2 有问题时可以跳过引用阶段（`README.md:83`），FAQ 说可以跳过查新与引用（`:188`） | 出想法脚本没有跳过检索的参数；查不查由模型每轮决定；一旦调用，S2 返回 4xx / 5xx 或连不上就无上限退避 | `ai_scientist/perform_ideation_temp_free.py:269-297`、`ai_scientist/tools/semantic_scholar.py:52-56` | 出想法阶段没有跳过的开关 |
| 二代：每批约 20 条想法（§4.2） | 命令行默认 1 条，要自己传 `--max-num-generations` | `ai_scientist/perform_ideation_temp_free.py:280-285` | 默认值不同，参数可调 |
| 二代：树搜索用于四个实验阶段（§3.2.2） | 同 | `ai_scientist/treesearch/agent_manager.py:143-167` | 对上 |

## 4. 平台哪里能用

只列落点与事实，不写接不接。

### 4.1 方法件与阶段

| 方法件 | 落在哪个阶段 | 需要什么输入 | 产出什么 | AI Scientist 里的出处 |
|---|---|---|---|---|
| 带存档的出想法：已出过的想法原文进 prompt、要求「不同」，同一段对话里反思 N 轮，约定一个早停串 | 假设 | 研究方向描述（对应平台已确认的需求）；可选的基线代码（一代的 `experiment.py`，对应 `materials/` 里的代码）；本项目已出过的想法 | 一组结构化想法 | 一代 `ai_scientist/generate_ideas.py:14-72`、二代 `ai_scientist/perform_ideation_temp_free.py:99-125` |
| 想法字段表：二代七个字段，下游实验硬读其中五个 | 假设（主文件的内容） | — | 每条想法一份结构化记录；实验侧拿它拼任务描述 | 二代 `ai_scientist/perform_ideation_temp_free.py:30-37`、`ai_scientist/treesearch/agent_manager.py:124-134` |
| 有上限的检索判定循环：新对话、苛刻查新者口吻、每轮一个检索词、看前 10 条摘要、字符串判定、用完轮数默认不新 | 假设（也可看成文献阶段的一种检查） | 一条想法 + 一个返回摘要的检索通道 | 新 / 不新；AI Scientist 没存、但检索时手上有的：检索词、命中论文、判定理由 | 一代 `ai_scientist/generate_ideas.py:356-492` |
| 检索进出想法循环：检索是模型可选的一个动作，结果进下一轮 | 假设 + 文献 | 同上 | 想法与 Related Work 字段；检索命中本可以落成一份材料清单，AI Scientist 没落 | 二代 `ai_scientist/perform_ideation_temp_free.py:209-237` |
| bibtex 从检索 API 取，不让模型写 | 写作 | 检索通道返回的 bibtex（两代都用 S2 的 `citationStyles` 字段；一代的 OpenAlex 分支不返回它） | 引用条目 | 一代论文 §3(b)、一代 `ai_scientist/perform_writeup.py:369-370`、二代 `ai_scientist/perform_icbinb_writeup.py:507` |

### 4.2 跟平台现有规矩的对照

- **谁调模型**：AI Scientist 两代都是 Python 程序直接调模型 API，按模型名分派：Anthropic（含 Bedrock、Vertex）走 `anthropic` SDK，OpenAI 走 `openai` SDK，DeepSeek、OpenRouter、Gemini 也走 `openai` SDK、换 `base_url`（一代 `ai_scientist/llm.py:317-351`、二代 `ai_scientist/llm.py:480-544`）；凭据来自环境变量（各家 key，Bedrock 用 AWS 凭据）。二代 2025-09-30 起还能接本机 Ollama（`http://localhost:11434/v1`，`OLLAMA_API_KEY` 可空；列表里有 qwen3、deepseek-r1、gpt-oss，二代 `ai_scientist/llm.py:54-72`、`:492-497`），这条路不需要付费 key [^v2-commits]。平台 P-1：框架不调模型写文本，执行层是唯一写代码的（外层 `docs/architecture/README.md:151`）；执行层用哪家 CLI、什么模型由按人的 `agents.yaml` 定（P-25，`:175`）。方法件里的「轮数、早停串、判定串」在平台上写进执行层会话的说明还是写进 skill 脚本，目前没有定。
- **检索通道**：AI Scientist 用 S2 的 HTTP API（key 可选）。平台 P-14：联网只用 CLI 自带的搜索与网页读取工具，查到的带来源（外层 `docs/architecture/README.md:164`）；skill 脚本运行时联网有先例，`download` 拉 git 仓库与 Hugging Face，私有仓读环境变量 `HF_TOKEN`（内仓 `skills/download/SKILL.md:4`），依赖用 `uv run --locked --offline` 起（内仓 `docs/add-a-skill.md:65`）。CLI 自带搜索返回的是网页，S2 返回的是结构化元数据与摘要，两者给查新的输入不同。
- **评审隔离**：一代查新是新开的一段对话，但与出想法同一个模型、同一个进程，还能看到想法自带的三个自评分。平台 P-2 要求需要模型判断的评审由隔离的新会话做、只给产物不给轨迹，这一段注明「尚未实现」（外层 `docs/architecture/README.md:152`）。
- **阶段主文件**：假设、写作两个阶段还没有主文件，由第一个进来的能力定名（内仓 `framework/capabilities/__init__.py:42-51`、`docs/add-a-capability.md`「文件名按阶段定」一节）；文献阶段主文件是 `sources.md`（P-20，外层 `docs/architecture/README.md:170`），由助理手写（P-1，`:151`；内仓 `framework/capabilities/__init__.py:46`）。AI Scientist 两代都不保存检索命中的论文列表。
- **阶段之间**：平台 P-18 阶段之间不做数据流校验、进下一阶段时助理自己看盘（外层 `docs/architecture/README.md:168`）；二代的想法 JSON 与实验之间是硬校验，五个键缺一个就抛错。
- **人确认**：二代挑想法由人做（`--idea_idx`，二代论文 §4.2）；一代由 `novel` 过滤、不经人。平台上步骤能力的产出「能签」（P-22，外层 `docs/architecture/README.md:172`），要不要签由流程在哪放断点定（P-19，`:169`）。

## 5. 局限与前提

| 方面 | 事实 | 证据 |
|---|---|---|
| 输入 | 一代出想法离不开代码模板：基线代码、`prompt.json`、`seed_ideas.json`，想法被限定在「给定代码可行、不用额外数据集」；二代只要一份主题 Markdown | 一代 `ai_scientist/generate_ideas.py:25-27`、`:98-110`；二代 `README.md:101` |
| 领域 | 提示词写死了 ML：「顶级 ML 会议」「AI 研究者 / 博士生」；二代 issue #32 报告生成的想法与主题 Markdown 无关，回复的是一位非维护者，归因到 ML 取向的提示词（未核实）。二代实验阶段的目标里写死了要用 HuggingFace 数据集 | 二代 `ai_scientist/perform_ideation_temp_free.py:61-63`、一代 `ai_scientist/generate_ideas.py:356-358` [^v2-i32]；二代 `ai_scientist/treesearch/agent_manager.py:155-163` |
| 模型 | 出想法与查新用同一个模型；判新条数随模型在 31/51 到 51/51 之间变，论文说不可比；一代 README 说不建议用明显弱于 GPT-4 的模型；二代论文附录 A 没列出想法用的模型，代码默认 gpt-4o-2024-05-13；二代可接本机 Ollama，本地模型能不能稳定按 `ACTION:` / `ARGUMENTS:` 格式回复没有数据 | `launch_scientist.py:339-358`；一代论文表 3–5、§6；一代 `README.md:360`；二代 `perform_ideation_temp_free.py:276`、二代 `ai_scientist/llm.py:492-497` |
| 算力与成本 | 出想法本身不用 GPU。一代单独跑 `generate_ideas.py` 要装模型 SDK（`llm.py` 顶部 import 了 anthropic、openai、google.generativeai）；走主启动器则还要 torch 与 aider，并且在出想法之前先查 `pdflatex` 与 `chktex`，缺一个就退出。二代出想法脚本只依赖 anthropic、openai、backoff、requests、tiktoken，不碰 torch。二代 README 说出想法花费「一般几美元」 | 一代 `ai_scientist/generate_ideas.py:1-10`、一代 `ai_scientist/llm.py:5-9`、`launch_scientist.py:10-13`、`:334-336`；二代 `ai_scientist/perform_ideation_temp_free.py:1-18`、二代 `ai_scientist/llm.py:1-9`、二代 `README.md:180` |
| 依赖 | 两仓都只有不带版本号的 `requirements.txt`，没有锁文件 | 一代与二代 `requirements.txt`（`grep -c '=='` 均为 0） |
| 外部服务 | 没有 key 时 S2 限速；两代的退避都不设上限，429 及其他 4xx / 5xx 都会让进程一直重试；一代有 OpenAlex 备选（只在查新里可用，写作取 bibtex 用不了），二代没有 | 一代 `ai_scientist/generate_ideas.py:282-284`、`:302`；二代 `ai_scientist/tools/semantic_scholar.py:52-56`、`:101-103` [^v1-hang] [^v2-openalex] |
| 失败处理 | 一代：异常打印后跳过，一次失败吃掉一轮查新；二代：解析失败、没定稿的想法直接作废，只有 stdout 记录 | 一代 `:162-164`、`:481-483`；二代 `:240-253` |
| 留痕 | 一代只存 `novel` 布尔；二代只存定稿的想法。检索词、命中论文、判定理由都不落盘 | 一代 `:485-490`；二代 `:260-265` |
| 自评分 | 集中在 8 到 9 分，没有读取点；独立评测说它们看起来是随意给的 | 一代论文附录 C；[^beel] |

### 5.1 许可证条款要点

两仓 LICENSE 逐字相同（`diff` 无输出），名为 The AI Scientist Source Code License，Version 1.0，December 2025，基于 Responsible AI Source Code License v1.1（一代 `LICENSE:1-4`）。GitHub API 报的许可证类型是「Other / NOASSERTION」。

- **授权**（§2）：非独占、全球、免版税的著作权许可，可复制、可做衍生作品、可分发（`LICENSE:18-19`）。
- **分发**（§3.1）：分发任何部分都要附上完整的许可证文本（`:22`）。
- **使用限制**（§3.2）：本体及衍生作品不得由你或你控制的第三方用于（`:23-40`）：
  - a. 监控：检测或推断受美国联邦法保护的身份类别，或人的姓名、住址、性别、宗教、健康等身份特征；
  - b. 计算机生成媒体：合成逼真的人物或事件音视频而不加说明、水印或元数据；
  - c. 医疗：预测某人是否会提保险理赔；无人监督地诊断疾病；
  - d. 犯罪：根据面部或个人数据预测犯罪；
  - e. 科研稿件与学术诚信（「AI Scientist 条款」）：生成或传播科学稿件、论文、技术报告时，必须在显著位置（如摘要、专门的 Disclosure 或 Methods 节）明确说明内容是机器生成的或用 The AI Scientist 产出的。
- **传递**（§3.3）：上述限制必须作为可执行条款写进任何约束本作品或衍生作品使用、分发的法律协议（`:42`）。
- **终止**（§4）：出现受限用途时，许可方有权终止许可并要求归还或销毁全部副本（`:44-45`）。
- §5、§6：按现状提供、不担保、不担责（`:47-51`）。

历史：两仓最初都是 Apache 2.0，2025-12-19 同日改成上面这份（一代提交 2906fcb「Update license from Apache 2.0 to AI Scientist License 1.0」，二代提交 c204ee8），随后 README 加了「Mandatory Disclosure」一节（一代 `README.md:391-395`、二代 `README.md:203-209`）[^lic]。本篇读的两个提交都在改许可证之后。二代 README 说树搜索基于 AIDE（二代 `README.md:196`），AIDE 仓库是 MIT [^aide]。

## 6. 还没弄清的问题

1. **查新到底准不准**：两篇论文都没有标准答案对照；Beel 等是一个领域、一个模型、12 条想法的单次观察。Nature 版（2026-03-25）[^nature] 这次只扫了网页正文：出想法用 o3，查新写成「语义相似度高的丢弃」、仍写「网页访问」，正文没看到对想法或查新的定量评估；补充材料没读，不知道那里有没有。
2. **错判的来源分不开**：误判新是 S2 关键词检索召回不到、模型没想到对的检索词（提示里说「能想起确切论文名时最好」）、还是模型读到了也判新，现有材料分不开。
3. **反思轮数有没有用**：没有消融；一代「I am done」在实际运行里第几轮出现、一代查新平均检索几轮才判定、二代有多少比例的想法定稿前真的检索过，都没有统计。二代论文说公开的 workshop 实验数据在 SakanaAI/AI-Scientist-ICLR2025-Workshop-Experiment [^workshop-data]：用 `gh api` 列了文件树，只有三篇论文的标注版、AI 审稿结果与审稿代码，没有出想法的记录（约 40 条想法、检索词、反思轮次都不在里面）。
4. **同模型自查**：一代查新与出想法是同一个模型，且查新能看到想法的自评分；换模型或换一个看不到自评分的会话，判定会不会变，没有数据。
5. **检索通道的差别**：S2 现在没有 key 时的限速、key 的申请周期（2026-09 的情况）没查（#179 里 2025-01 有人说 S2 的 key 申请在排队等候，是旧情况 [^v1-i179]）；OpenAlex 用来查新效果如何没有数据；CLI 自带网页搜索与 S2 结构化检索用于查新孰优孰劣，没有数据。
6. **领域迁移**：提示词是 ML 取向，在课题组的工程学科题目上表现如何没有证据。二代 issue #133 是一次生物医学主题的独立评测（10 个题目、24 次写作）报的两个 bug，都在写作与 VLM 看图环节，不在出想法；报告者用的主模型 DeepSeek-Chat 不在二代 `AVAILABLE_LLMS` 里（二代 `ai_scientist/llm.py:13-73`），说明他改过代码；他们的出想法记录说是随论文发布，还没看到 [^v2-i133]。
7. **OpenAlex 与写作**：一代 `--engine openalex` 时写作阶段会不会一条引用都加不上（见 [2.6 节](#26-实验与写作两句话)），是读代码推断，未运行验证；issue #179 确认了缺字段，没人贴出实际运行结果 [^v1-i179]。
8. **许可证怎么适用**：照着方法重新实现、抄提示词原文、用改许可证之前的 Apache 2.0 提交，分别算不算这份许可证意义上的「衍生作品」，§3.3 对再分发的要求落到平台上意味着什么，这些是法律问题，本篇不下判断。
9. **README 的「可以跳过查新」**：`--skip-novelty-check` 配合新出的想法会不会真的 KeyError，是读代码推断，未运行验证。
10. **本地模型**：二代接 Ollama 后，出想法这段能不能不花钱跑通（本地模型守不守 `ACTION:` / `ARGUMENTS:` 格式、会不会调检索），没有数据。

## 7. 调研方法

- 两个仓库浅克隆到外层 `vendor/`（gitignore 挡住），只读代码、不装依赖、不跑。重点逐行读了一代 `ai_scientist/generate_ideas.py`（546 行全读）、`launch_scientist.py`、`experimental/launch_oe_scientist.py` 的出想法部分，二代 `ai_scientist/perform_ideation_temp_free.py`（319 行全读）、`ai_scientist/tools/semantic_scholar.py`、`launch_scientist_bfts.py`，以及 `agent_manager.py` 里读想法的部分；分数字段、`novel`、检索函数的调用点都用 grep 全仓确认。
- 论文用平台的 `pdf` skill 解析，原件与解析结果放在外层 `materials/research/2026-0927-scientific-ai-capabilities/papers/`（gitignore）。附录 C 的分数分布与判新条数，是对解析出的 `paper.md` 附录 C 一节按「Idea n/50」切段、用正则取 `"Interestingness"` `"Feasibility"` `"Novelty"` `"novel"` 数出来的；判新 46 条加种子共 47，与表 5 对上作为自检。
- 许可证历史、issue 与 PR、出想法相关文件的提交历史用 `gh api` 只读查询；独立评测 Beel 等的论文下载后解析核对了数字；Nature 版只抓了网页正文扫读。
- 2026-09-27 另一个会话照出处独立复核了一轮：逐个打开文中的 `文件:行`、重数附录 C 的分数与判新条数（结果与第一版一致）、重查 issue 与提交历史、对「没有网页访问 / 没有相似度计算 / 没有查新判定 / 分数没有读取点」几条否定说法重新 grep；改正的行号、补上的事实已并入正文。

[^v1paper]: Chris Lu 等，The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery，arXiv 2408.06292，<https://arxiv.org/abs/2408.06292>。章节、表号按 2026-09-27 下载的版本（186 页；下载时 arXiv 最新是 v3，2024-09-01）。
[^v2paper]: Yutaro Yamada 等，The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search，arXiv 2504.08066，<https://arxiv.org/abs/2504.08066>。章节、表号按 2026-09-27 下载的版本（69 页；arXiv 只有 v1，2025-04-10）。
[^beel]: Joeran Beel、Min-Yen Kan、Moritz Baumgart，Evaluating Sakana's AI Scientist: Bold Claims, Mixed Results, and a Promising Future?，arXiv 2502.14297，<https://arxiv.org/abs/2502.14297>（v1 2025-02-20，v3 2025-10-15；v3 PDF 内的 ACM 引用格式题名是「Evaluating Sakana's AI Scientist for Autonomous Research: Wishful Thinking or an Emerging Reality Towards 'Artificial Research Intelligence' (ARI)?」）。本篇核对的是 2026-09-27 下载的 v3（16 页），章节号按 v3：§2.3 Idea Generation、§2.4、§2.5、§2.8。
[^lic]: 一代 LICENSE 提交历史 <https://github.com/SakanaAI/AI-Scientist/commits/main/LICENSE>（d6576a3 初版 Apache 2.0，2906fcb 2025-12-19 改许可证）；二代 <https://github.com/SakanaAI/AI-Scientist-v2/commits/main/LICENSE>（f85bb03 初版 Apache 2.0，c204ee8 2025-12-19）。2026-09-27 用 `gh api` 查。
[^v1-hang]: 一代 issue #78「always backing off」<https://github.com/SakanaAI/AI-Scientist/issues/78>、#116「stuck at the retrieval phase for about an hour」<https://github.com/SakanaAI/AI-Scientist/issues/116>、#133「429 - Too many requests」<https://github.com/SakanaAI/AI-Scientist/issues/133>，均未关闭。
[^v1-openalex]: 一代 PR #135「OpenAlex API support」，2025-01-14 合入，<https://github.com/SakanaAI/AI-Scientist/pull/135>；对应代码 `ai_scientist/generate_ideas.py:311-350` 与一代 `README.md:146-158`。
[^v1-empty]: 一代 issue #113，S2 对查新词返回 `totalHits: 0`，<https://github.com/SakanaAI/AI-Scientist/issues/113>。
[^v2-openalex]: 二代 PR #59「Integrating OpenAlex」2025-07-27 关闭未合，<https://github.com/SakanaAI/AI-Scientist-v2/pull/59>；PR #56「Add OpenAlex search tool support」未合，<https://github.com/SakanaAI/AI-Scientist-v2/pull/56>。
[^v2-i32]: 二代 issue #32「JSON Output Unrelated to Original Markdown Content」，<https://github.com/SakanaAI/AI-Scientist-v2/issues/32>。
[^aide]: WecoAI/aideml，GitHub API 报许可证 MIT，<https://github.com/WecoAI/aideml>，2026-09-27 查。
[^nature]: Chris Lu、Cong Lu 等，Towards end-to-end automation of AI research，Nature，2026-03-25 在线发表，<https://www.nature.com/articles/s41586-026-10265-5>；Sakana AI 博客「The AI Scientist: Towards Fully Automated AI Research, Now Published in Nature」，2026-03-26，<https://sakana.ai/ai-scientist-nature/>。2026-09-27 抓网页正文扫读（查新、出想法、模型选择几段），补充材料未读。
[^v1-i179]: 一代 issue #179「`citationStyles` key for OpenAlex API」，2025-01-19 开，未关闭，<https://github.com/SakanaAI/AI-Scientist/issues/179>。
[^v2-commits]: 二代出想法相关提交，2026-09-27 用 `gh api` 查：f85bb03（2025-04-08，初版；`ai_scientist/tools/semantic_scholar.py` 没有 `S2_API_KEY` 就抛错，出想法脚本调 `get_response_from_llm` 的参数名也写错了）；364aa55（2025-04-12，系统提示删掉「从给定代码库出发」）；39ee150（2025-04-17，S2 key 改成可选，修参数名）；c31970c（2025-05-05，IDEA JSON 示例加外层 `"idea"`）；9cda77f（2025-09-30，`ai_scientist/llm.py` 加 Ollama）。<https://github.com/SakanaAI/AI-Scientist-v2/commits/main/ai_scientist>。
[^v2-i133]: 二代 issue #133「Two v2 bugs (F11 VLM whitelist rejection, F13 UnboundLocalError on pdf_path) reproduce in 24/24 biomedical-prompt runs at SHA 96bd51617」，2026-08-16 开，未关闭，无回复，<https://github.com/SakanaAI/AI-Scientist-v2/issues/133>。
[^workshop-data]: SakanaAI/AI-Scientist-ICLR2025-Workshop-Experiment，<https://github.com/SakanaAI/AI-Scientist-ICLR2025-Workshop-Experiment>，最后推送 2025-04-18，GitHub API 报无许可证；2026-09-27 用 `gh api .../git/trees/HEAD?recursive=1` 列了 37 项。
