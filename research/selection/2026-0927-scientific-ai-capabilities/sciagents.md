---
title: SciAgents 方法深读
subtitle: 科研 AI 能力选型 · 概念图上取路径、多角色写结构化假设、Semantic Scholar 查新，论文与代码逐条对账
kind: 开源项目方法借鉴深读（只读论文、代码与公开数据，不跑项目代码、不装依赖；不评估整体接入）
date: 2026-09-27
scope: 仓库 https://github.com/lamm-mit/SciAgentsDiscovery 浅克隆到 vendor/SciAgentsDiscovery，提交 c5c3045（2025-05-10 UTC）；它依赖的 https://github.com/lamm-mit/GraphReasoning 浅克隆只读，提交 f1d6d44（2024-07-19）；图谱数据 Hugging Face lamm-mit/bio-graph-1K 修订 888b9c7，只下了 graphml 做统计，没下 138 MB 的 embedding pickle；论文 arXiv 2409.05556v1、期刊版 Adv. Mater. 2413523（Europe PMC 全文）、GraphReasoning 论文 arXiv 2403.11996。文中以 ScienceDiscovery/、Notebooks/、setup.py、README.md 开头的 文件:行 在 SciAgentsDiscovery 仓，以 GraphReasoning/ 开头的在 GraphReasoning 仓；notebook 的格号从 1 数，含 markdown 格
status: 第一版
---

> **结论先行**：SciAgents 的方法是四段串起来的。一，用 LLM 从约一千篇生物材料论文里抽三元组，拼成一张无向概念图（这一步在 GraphReasoning 包和它的论文里，SciAgents 仓不建图，只下载现成的图）。二，在图上取两个概念之间的一条路径，写成「节点 -- 关系 -- 节点」的一行字。三，几个角色依次写：本体学家解释路径上的词和关系，科学家写七个字段的 JSON 假设，七个字段各扩写一遍，批评者给总结、优缺点和两个「最值得用分子建模 / 合成生物学去做的问题」。四，自动版里再让一个查新 agent 用 Semantic Scholar 搜几次、读摘要，给 1 到 10 分的新颖性与可行性。
>
> 各角色的系统提示词和七个字段，论文与代码几乎逐字对得上。对不上的有五处：论文 §4.2 说路径代价里有 embedding 启发式，按论文参数（随机因子 0.2、4 个路标）走到的那个函数里 `heuristic` 定义了没被调用，实际是「边权 + 随机噪声」的 Dijkstra 再绕四个随机路标（embedding 启发式只用在两个参数都为 0 时走到的另一个函数里）；论文说取完路径带二跳邻居，SciAgents 调用处把 `second_hop` 写死成 False，交给模型的只有路径那一行字；论文 Figure 1 的 Scientist 2 在代码里是七个按字段分开的 agent；论文说用的图来自前作 [6]，但尺寸是前作报告的约 2.7 倍，怎么建的没写（论文印出的三条路径倒是逐边都能在公开图里找到）；论文称第二种编排是「全自动」，附录六份自动对话（S2–S7）里有三份是人打字催了才调查新工具，六份对话开场打出的 agent 简介与 `agents.py` 三个公开版本都对不上，其中两份还有一个公开代码里没有的 `caller` agent。
>
> 证据上没有消融、没有基线、没有人工评审：7 个案例，新颖性分数由 LLM 读 Semantic Scholar 摘要后自己给；「随机路径比最短路径好」只有一张示意图（Figure 4）。期刊版结论自己写了缺人类专家评估与指标。附录里能看到查新环节的两个具体毛病：一条 16 个词的长查询返回 0 篇，被当成「文献里没有直接匹配」打了 8 分；两份对话里 agent 未检索时自评 9 分，检索后分别降到 7 分和 6 分。
>
> 按本轮分组只摘方法。能摘的方法落在文献（建图）与假设（取路径、多角色写、查新）两个阶段；写作阶段能对上的只有它成稿的章节结构，那是一份开题式长文，没有引用。怎么读：[第 1 节](#1-方法是什么)逐段讲方法和代码位置，[第 2 节](#2-为什么有效论文证据与代码对账)是论文证据与代码对账，[第 3 节](#3-平台哪里能用)是平台上落在哪、要什么输入、出什么，[第 4 节](#4-局限与前提)是限制，[第 5 节](#5-还没弄清的问题)是没弄清的问题。横向对比见同目录的 [README.md](README.md)。

## 1. 方法是什么

### 1.1 仓库画像

| 项 | 实况 | 证据 |
|---|---|---|
| 仓库 | MIT LAMM（Buehler 组），638 star、108 fork；60 个提交，2024-08-21 建仓（空的初始提交），2024-09-09 起改 README、09-10 起上传代码，最后一个提交 2025-05-10；零 release；11 个未关 issue 与 PR | GitHub API（2026-09-27 查）[^gh] |
| 代码量 | `ScienceDiscovery/` 5 个 .py 共 977 行（`agents.py` 406、`utils.py` 517，其余三个合计几十行），另提交了两个 `__pycache__/*.pyc`；两个 notebook，没有保存输出 | `wc -l`、`git ls-files`；`Notebooks/*.ipynb` |
| 依赖 | `setup.py` 列 35 个包，只有 `transformers>=4.39`、`pyautogen>=0.2.28` 带下限，无上限、无锁文件；含 torch 三件套、bitsandbytes、peft、llama-index、langchain、guidance、weasyprint、pdfkit（要系统装 wkhtmltopdf，README 让 `apt-get install`）。GraphReasoning 不在 `install_requires` 里，README 要求另装；notebook 第 2 格只跑 `pip install -e .`，issue #4 就是这个 `ModuleNotFoundError` | `setup.py:13-49`；`README.md:44-59`；[^gh] |
| 核心依赖 | GraphReasoning 包：7 个文件 4954 行，最后提交 2024-07-19；SciAgents 调到它的读图（graphml 加载、取最大连通分量）、embedding、取路径、OpenAI 调用四块，不调它的建图函数 | GraphReasoning 仓 `wc -l` [^gr-repo]；`ScienceDiscovery/graph.py:13-20`、`ScienceDiscovery/utils.py:61` |
| 编排框架 | 自动版用 AutoGen 0.2 的 API（`pyautogen`：`config_list_from_models`、`register_for_llm`、`GroupChat`）。README 写「用 AG2（原 AutoGen）实现」，那是 PR #13、#14 只改 README 的结果；把代码迁到 autogen 0.4 与 ag2 的两个外部 PR（#12、#18）没合。PyPI 上 `pyautogen` 现在的最新版 0.10.0 是 `autogen-agentchat>=0.6.4` 的代理包，`setup.py` 没有上限，今天新装拿到的不是 0.2 的 API（按 PyPI 元数据推断，未安装验证） | `ScienceDiscovery/agents.py:1-14`、`ScienceDiscovery/llm_config.py:3`；`README.md:31`；[^gh]；[^pypi] |
| 模型 | 自动版写死 `gpt-4o`，两个配置名叫 `4turbo` 的也是 `gpt-4o`（外部 PR #9 指出这点，没合）；非自动版的模型在 notebook 里用 `partial(generate_OpenAIGPT, gpt_model='gpt-4o')` 指定 | `ScienceDiscovery/llm_config.py:3-5`；`Notebooks/SciAgents_ScienceDiscovery_GraphReasoning_non-automated.ipynb` 第 6 格；[^gh] |
| 测试与 CI | 没有 | 仓库根 |
| 许可证 | `LICENSE.txt` 是 Apache-2.0；两个仓的 `setup.py` classifier 都写 MIT；图谱数据 apache-2.0；期刊论文 CC BY-NC 4.0 | `setup.py:55`、GraphReasoning `setup.py:51`；[^hf]；[^advmat] |

### 1.2 知识图谱怎么建

SciAgents 论文只有两句：用前作 [6] 生成的大图，33,159 个节点、48,753 条边，是约 1,000 篇论文生成图的最大连通分量，92 个社区，embedding 用 `BAAI/bge-large-en-v1.5`（§4.1）。建图的方法在前作 GraphReasoning 论文 §4.2 与 GraphReasoning 仓里。

**GraphReasoning 论文里的流程**（arXiv 2403.11996 §4.2）[^gr-paper]：

| 步 | 做法 | 出处 |
|---|---|---|
| 语料 | 沿用 BioinspiredLLM 的论文集，1,000 多篇生物启发材料与力学论文 | §4.2.1，引 [^luu] |
| 转文本 | Nougat 把 PDF 转成标记文本，切块，平均 772 词 | §4.2.1 |
| 提炼 | Mistral-7B-OpenOrca 对每块写摘要、要点列表、一句标题（要求去掉人名与引用），得 8,663 份「原始上下文」 | §4.2.1 |
| 抽三元组 | Zephyr-7B-β：提示词「用范畴论抽术语和关系的网络本体构图者」，每块约 10 个 `{node_1, node_2, edge}`；再喂原文和初稿，要求「按材料科学通用叫法重命名节点」；再修 JSON 格式；失败的块第二遍重试 | §4.2.2 |
| 合图 | 随机取约 1,600 份上下文的小图，`networkx.compose` 拼起来；bge-large-en-v1.5 算节点 embedding，余弦相似度 > 0.95 的节点合并，保留度数最高的名字 | §4.2.3 |
| 规模 | 全图 12,319 节点 / 15,752 边；最大连通分量 11,878 / 15,396，80 个社区；最大度数 171 | §2.1、Table 1 |

**GraphReasoning 代码里的对应**（提交 f1d6d44）：

| 环节 | 代码 | 证据 |
|---|---|---|
| 抽三元组 | `graphPrompt` 每块至少 4 次模型调用：初抽、按材料科学重命名、修格式、再修格式；`repeat_refine>0` 时每轮再加 3 次 | `GraphReasoning/graph_generation.py:220,235,241,274`、`:246-270` |
| 领域写死 | 重命名提示词写的是「widely used in the field of materials science」；few-shot 两个例子，一个家庭关系（Alice / Marc），一个蜘蛛丝 | `GraphReasoning/graph_generation.py:231-234`、`:186-213` |
| 解析 | 取第一个 `[` 到最后一个 `]` 之间的串 `json.loads`，失败打印后返回 `None`，这块就丢了 | `GraphReasoning/graph_generation.py:105-109,277-290` |
| 切块 | 直接对原文 `RecursiveCharacterTextSplitter`，默认 2,500 字符；论文里的 Nougat 转换与「摘要 / 要点 / 标题」提炼这一步，仓里没有代码（全仓与两个 notebook grep 不到 Nougat 与那几条提示词；`GraphReasoning/agents.py` 里的 summary / bullet 是总结对话用的，不是切块提炼） | `GraphReasoning/graph_generation.py:337,351-359` |
| 成图 | `nx.Graph()`，**无向**；每条三元组先记 `count=4`，按 (node_1, node_2) 分组后把关系用逗号拼成一个标签、count 求和，边权 = 求和 ÷ 4，也就是这对节点在三元组里出现的次数（公开图里边权恰好等于每条边的 `chunk_id` 个数，见下表） | `GraphReasoning/graph_generation.py:386,400-404,410,428-433` |
| 反向重复的节点对 | 分组键是有序的 (node_1, node_2)，(A, B) 与 (B, A) 是两行；无向图上第二次 `add_edge` 落在同一条边上，按 networkx 的语义会覆盖前一次的标签与边权，不拼接（按代码与库的行为推断，未执行） | `GraphReasoning/graph_generation.py:400-404,426-433` |
| 加进大图 | `add_new_subgraph_from_text`：compose、补 embedding、按 0.95 合并相近节点、删小于 10 个节点的碎片、Louvain 分社区 | `GraphReasoning/graph_generation.py:515-650` |
| 加进大图的缺陷 | 第 538 行引用未定义的 `G_newlymade`（全仓只出现这一次），只给文本时 `NameError` 被第 561 行的裸 `except` 吞成「Graph generation failed」，随后读 `None` 路径再被第 646 行吞掉。按代码读，「从文本新建再并入」这条路在这个提交上走不通；调用方直接给 `G_to_add` 或 `graph_GraphML_to_add` 时这一段能绕过去（未执行验证） | `GraphReasoning/graph_generation.py:538,557-577,561,646` |
| 合并相近节点 | 对全部节点算完整的 N×N 余弦相似度矩阵；33,159 个节点时约 11 亿个元素，embedding 是 float32 时约 4.4 GB（sklearn 对两个 float32 输入保留 float32），是 float64 时约 8.8 GB，另有一个同尺寸的布尔矩阵约 1.1 GB；公开 pickle 的 dtype 本次没核对 | `GraphReasoning/graph_tools.py:811-815` |
| 节点 embedding | 取 `last_hidden_state` 的均值、不归一化；bge-large-en-v1.5 模型卡用的是 [CLS] 向量并做 L2 归一化。后面都用余弦比较，归一化与否不影响结果，真正不同的是均值池化与 CLS 池化 | `GraphReasoning/graph_tools.py:116-122,152-155`；[^bge] |

**公开的图长什么样**（本次用 Python 标准库解析 `large_graph_simple_giant.graphml`，sha256 `78b7c24e…`）：

| 指标 | 值 | 说明 |
|---|---|---|
| 节点 / 边 | 33,159 / 48,753 | 与 SciAgents §4.1 一致；是 GraphReasoning Table 1 全图的约 2.7 倍 |
| 方向 | `edgedefault="undirected"` | 关系标签带方向（「A is B」），图不记方向 |
| 社区 | 节点属性 `group` 有 85 个不同值 | 论文写 92 |
| 边权 | 47,876 条（98.2%）是 1.0，其余 2 到 6 | 取路径时的随机噪声与这个量级比较，见 1.3 |
| 合并过的边标签 | 边权 > 1 的 877 条，标签是几条关系用逗号拼起来的；另有 697 条边权为 1 的边，标签本身是带逗号的长句 | 1,574 条标签含逗号，只有 877 条是合并出来的 |
| 标签质量 | 有的标签是整句（「Elastic Spheres can exhibit Adhesion, which is …」），个别是列表的字符串（`[{'source': 'geometry', …}]`），6 条边的 `title` 被存成了布尔值；自环 190 条 | 抽取与修格式没把住的输出进了图 |
| 度数 | 中位数 1；59% 的节点度数为 1；最大 461 | 中位数与 GraphReasoning Table 1 一致；最大度数是它的 171 的 2.7 倍 |
| 枢纽 | mechanical properties 461、biological materials 363、collagen 345、hydrogels 308 | 路径常经过这些点，见 1.3 |
| 出处 | 每条边带一个或几个 uuid 形式的 `chunk_id`（逗号拼接，个数等于边权；98.2% 的边只有一个）；节点没有原文，HF 仓里只有 graphml 与 embedding pickle，没有「块 → 论文」的对照表 | 从一条边追不回是哪篇论文 |
| 近义残留 | 含「self-cleaning」的节点有 9 个，其中 self-cleaning、self-cleaning properties、self-cleaning effects、self-cleaning behavior 是同一概念的不同说法 | 0.95 阈值之下没合并的近义词 |

### 1.3 图上怎么取路径

论文的说法：路径是 SciAgents 的核心输入；前作用最短路径，这里改成随机路径，因为能带进更多概念（§2.1 第 1 点、Figure 4）。算法（§4.2）：用 embedding 把两个关键词对到最近的节点；在 Dijkstra 的优先队列里加随机项，代价 = h(v, target) + α·random()，h 是 embedding 距离，α 取 0.2；再从路径节点的邻居里随机选路标，逐段求最短路；正文说最后取路径节点加二跳邻居的子图作为上下文，同一节的算法第 7 步写的却只是「路径上的全部节点与边」。

代码里的实际做法：

| 步 | 代码 | 证据 |
|---|---|---|
| 选端点 | 用户给两个关键词；不给就从全部节点里均匀随机取两个；全程没有设随机种子 | `ScienceDiscovery/utils.py:163-173`、`:247-257`；两个仓 grep 不到 `random.seed` |
| 关键词对到节点 | 对 embedding 字典里的每个节点逐个算余弦，取前 5 再用第一名（公开图 33,159 个节点；pickle 没下，字典实际大小没核对）。用户在 issue #5 里问「怎么不让它改我的关键词」，就是这一步 | `GraphReasoning/graph_analysis.py:1694-1702`、`GraphReasoning/graph_tools.py:152-179`；[^gh] |
| 两种编排用的参数 | `randomness_factor=0.2`、`num_random_waypoints=4`、`shortest_path=False`、`second_hop=False`；非自动版 notebook 同样的参数，关键词写的是 energy-intensive 与 protein | `ScienceDiscovery/agents.py:365-369`；`Notebooks/SciAgents_ScienceDiscovery_GraphReasoning_non-automated.ipynb` 第 8 格 |
| 走哪个函数 | 这组参数走 `heuristic_path_with_embeddings_with_randomization_waypoints`。embedding 启发式只用在另一个函数 `heuristic_path_with_embeddings` 里（每步在按 embedding 欧氏距离排序的前 `top_k` 个邻居里随机挑一个），SciAgents 只在随机因子与路标数都为 0 时才走到它 | `ScienceDiscovery/utils.py:195-219`；`GraphReasoning/graph_analysis.py:129-172` |
| 随机 Dijkstra | 优先级 = 累计边权 + 0.2 × random()；弹出的优先级带着噪声作为下一步的累计值，所以每跳各加一个 [0, 0.2) 的噪声。这个函数里的 `heuristic`（embedding 欧氏距离）在第 1707 行定义，函数体里零调用。98% 的边权是 1：边权都为 1 时，k 跳路径的优先级落在 [k, 1.2k)，k ≤ 5 时它一定小于任何 k+1 跳路径，所以挑出的是最短跳数的一条（多条等长时随机），更长时也只是接近最短 | `GraphReasoning/graph_analysis.py:1707-1728` |
| 随机路标 | 把路径上各节点不在路径里的邻居全部收进一个池子（挨着路径上几个节点就重复出现几次），打乱取 4 个；新路径**只保留起点**，然后按边权最短路走 起点 → 路标 1 → … → 路标 4 → 终点。随机 Dijkstra 那条路径只用来提供邻居池；路径经过枢纽时，池子里大部分候选是枢纽的邻居 | `GraphReasoning/graph_analysis.py:1730-1744` |
| 子图 | 建了一个 `DiGraph` 子图，`second_hop=True` 时加二跳邻居；SciAgents 的两处调用把 `second_hop=False` 写死在调用参数里，调用方传什么都不生效，返回的子图也被丢掉 | `GraphReasoning/graph_analysis.py:1770-1786`；`ScienceDiscovery/utils.py:196-211,205,280-295,289` |
| 交给模型的 | 只有 `print_path_with_edges_as_list(G, path)` 拼出的一行「节点 -- 关系 -- 节点 -- …」 | `ScienceDiscovery/utils.py:226,310`；`GraphReasoning/graph_analysis.py:677-702` |
| 没用上的参数 | `create_path` 与 `develop_qa_over_path` 给随机路标函数传了 `top_k=5`，函数里不读 | `ScienceDiscovery/utils.py:203,287`；`GraphReasoning/graph_analysis.py:1597-1813` |

这个机制在论文自己的案例里留下了可见的形状。附录 S1（silk 到 energy-intensive）那条路径里「biological materials」出现 5 次：四个路标 novel functionalities、low-temperature processing、multi-scale organization、dandelion 都是这个枢纽（度数 363）的邻居，其中 multi-scale organization 与 dandelion 在公开图里度数是 1、只连着这个枢纽，每段最短路都从枢纽进出，路径实际是以枢纽为中心的星形。同一条边正反两个方向都出现（「biological materials -- provide functionalities -- dandelion -- provide functionalities -- biological materials」），因为图是无向的；§2.1 里本体学家把「membranes – can be spun into – silk」解释成「这表示反过来的过程」，是模型在给一条被反着读的边找说法。

随机端点也有偏向：59% 的节点度数是 1，均匀随机抽两个节点，约 83%（1 − 0.41²）的对里至少有一个度数为 1 的节点，本次在公开图上抽 1 万对得到 82.9%。论文 Figure 8 a–d 的 8 个随机端点里，rhamphotheca、heat transfer performance、theoretically reversible or partially reversible、tunable processability 四个在公开图里度数是 1；S1 由人指定的端点 energy-intensive 度数也是 1。Figure 8 标题说五组端点都是随机选的，但 S7（Figure 8e）的任务是人写的「using graphene and proteins」。

### 1.4 各个 agent 的分工与提示词

两种编排用的是同一套角色。非自动版是 `research_generation` 里一串顺序调用；自动版是 AutoGen 的 GroupChat，由一个 LLM 挑下一个发言者。

| 角色 | 做什么（提示词原意） | 非自动版 | 自动版 | 模型参数 |
|---|---|---|---|---|
| 本体学家 | 给路径上每个词下定义，再逐条讨论每条关系；「每个概念都要用上」；先定义、后关系 | `ScienceDiscovery/utils.py:315-333` | `ScienceDiscovery/agents.py:52-78` | 非自动 temperature 0.1、1024 token；自动 temperature 0 |
| 科学家（Scientist 1） | 据路径与定义写一份新研究假设，七个字段的 JSON；「尽量定量，给数字、序列、化学式」；「每个概念都要用上」；鼓励不寻常的组合 | `ScienceDiscovery/utils.py:340-393` | `ScienceDiscovery/agents.py:81-134`（字段名带序号「1- hypothesis」） | 非自动 temperature 0.2、2048 token；自动 temperature 0.2 |
| 扩写（Scientist 2） | 以同行评审的视角批判地扩写某一个字段，补化学式、数字、序列、工艺条件、微结构，给逐步推理，点名建模与实验方法；开头写「### Expanded …」 | 对前 7 个字段各调一次，`ScienceDiscovery/utils.py:443-471` | 七个 agent：`hypothesis_agent` 到 `novelty_agent`，`ScienceDiscovery/agents.py:137-269` | 非自动 temperature 0.2、2048 token；自动 temperature 0.1、2048 token |
| 批评者 | 一段总结；优点、缺点、改进建议；再从文中挑出「最值得用分子建模解决的一个问题」和「最值得用合成生物学解决的一个问题」，各写步骤；自动版不许打新颖性与可行性分 | 拆成三次调用：总结与评审、建模优先、合成生物学优先，`ScienceDiscovery/utils.py:479-500` | `ScienceDiscovery/agents.py:271-295`（不打分那句在 `:290-291`） | temperature 0.1 |
| 规划者 | 给分步计划，写明哪一步由哪个 agent 调哪个工具，自己不调工具 | 无 | `ScienceDiscovery/agents.py:25-37`；但两个工具都用 `@planner.register_for_llm()` 注册给了它（`:357,374`） | temperature 0 |
| 助手 | 按计划调 `generate_path` 与 `rate_novelty_feasibility`，结束时说 TERMINATE | 无 | `ScienceDiscovery/agents.py:39-49,356-388` | temperature 0 |
| 查新 | 见 1.6 | 无 | `ScienceDiscovery/agents.py:298-322,373-388` | temperature 0 |
| 发言调度 | LLM 按上下文和各 agent 的 description 选下一个发言者，最多 50 轮，允许同一人连说；`send_introductions=True`，开场把各 agent 的 description 念一遍 | 无 | `ScienceDiscovery/agents.py:398-407` | temperature 0 |
| 人 | `human_input_mode="ALWAYS"`：每次轮到 `user` 都等人输入；两个工具的执行也注册在 `user` 上，按 AutoGen 0.2 的行为，人直接回车才让它自动执行工具（按 AutoGen 文档推断，未执行） | 无 | `ScienceDiscovery/agents.py:16-23,356,373` | — |

几个细节：

- **上下文怎么传。** 非自动版每次调用都是单轮、只拿需要的部分：科学家拿路径与本体学家的输出（`ScienceDiscovery/utils.py:351`）；七次扩写各拿七字段全文、路径和本字段（`:444-460`），看不到本体学家的输出；批评者只拿拼好的成稿（`:474-483`，成稿里有路径、本体学家输出、七字段与七段扩写），不拿前面的提示词与过程；两个优先问题拿成稿加批评（`:493-500`）。自动版所有 agent 共享整段群聊历史（论文 §2.2；`ScienceDiscovery/agents.py:398-403`）。
- **七个扩写 agent 的系统提示词里写的是字面的 `{hypothesis}`、`{outcome}`……** 这些字符串不是 f-string，占位符不会被替换，扩写 agent 拿到的内容全靠共享的对话历史（`ScienceDiscovery/agents.py:139,159,178`）。
- **批评没有回流。** 非自动版把批评追加到文档末尾就结束，假设本身不改（`ScienceDiscovery/utils.py:485-508`）。自动版要不要回到科学家改稿取决于发言调度；附录 S3 到 S7 的节标题顺序都是「批评 → 优先问题 → 新颖性评分」，没有改稿。论文 §2.1 结尾称之为「假设生成与批判评估之间的迭代反馈循环」，期刊版结论也写「agent 通过迭代反馈循环改进提案」。
- **非自动版一次要 12 次串行调用**：本体学家 1、科学家 1、扩写 7、批评 1、优先问题 2（`ScienceDiscovery/utils.py:332,392,464,482,495,499`）。自动版的次数不固定：每轮先有一次发言调度的模型调用，选中的是 agent 再加一次发言调用，选中 `user` 时是人输入、不调模型；另加查新里最多 10 轮的嵌套对话和一次总结。
- **磁盘缓存只在自动版。** 自动版的四份模型配置都带 `cache_seed: 42`，AutoGen 会把同样的请求缓存在本地，同一输入重跑得到同一输出；文件里的注释写「换 trial 就改 cache_seed」（`ScienceDiscovery/llm_config.py:8`）。非自动版走 notebook 里包好的 `generate_OpenAIGPT`，直接用 `openai` 客户端调接口、不经 AutoGen，没有这层缓存（`GraphReasoning/openai_tools.py:12-42`；非自动版 notebook 第 6 格）。

### 1.5 输出的结构化假设字段

七个字段来自科学家的提示词（`ScienceDiscovery/utils.py:353-367`，自动版 `ScienceDiscovery/agents.py:95-109` 措辞相同）：

| 字段 | 提示词里的定义 | 措辞绑定的领域 |
|---|---|---|
| `hypothesis` | 研究问题背后的假设；自动版加「明确、新颖、可行、目的清楚、组成清楚，越详细越好」 | 通用 |
| `outcome` | 预期发现或影响，「要定量，给数字、材料性能、序列或化学式」 | 材料 |
| `mechanisms` | 预期的化学、生物或物理行为，「从分子到宏观各尺度」 | 材料 / 多尺度力学 |
| `design_principles` | 详细的设计原则，列表，侧重新概念 | 材料设计 |
| `unexpected_properties` | 「新材料或新体系」的意外性质，给具体预测与理由 | 材料 |
| `comparison` | 与其他材料、技术或概念的详细定量比较 | 材料 |
| `novelty` | 相对现有知识与技术的新意 | 通用 |

非自动版最后落一个 CSV，在七个字段外再加 `path_string`、`expanded`（本体学家输出）、`res_data_expanded`（七段扩写）、`critiques`、`modeling_priority`、`synbio_priority`（`ScienceDiscovery/utils.py:403-404,485-486,507-508,513-516`），同时出 markdown 与 PDF（`:70-104,510-511`）。自动版不落字段，notebook 把整段对话历史拼成 markdown 再转 PDF（`Notebooks/SciAgents_ScienceDiscovery_GraphReasoning_automated.ipynb` 第 8 格）。

字段本身的几个事实：

- **解析是正则加 `json.loads`，没有 schema。** 取第一个 `{` 到最后一个 `}`（`ScienceDiscovery/utils.py:107-122`）；提示词里给的 JSON 示例在 `"novelty": "...",` 后面多一个逗号（`:380`），模型照抄就是非法 JSON。非法 JSON 在 `convert_response_to_JSON` 里的 `json.loads`（`:113`）就抛 `JSONDecodeError`，那里没有 `try`，直接从 `:395` 抛出去；只有回复里完全没有花括号时才走到 `:401-407` 的裸 `except`，打印「Dict generation failed...」，下一行 `json_to_formatted_text(None)` 必抛 `TypeError`（`:409`）。少任何一个键在 `json_to_formatted_text` 里抛 `KeyError`（`:128-146`）。三种情况都让整次生成中断。自动版的「JSON」只是对话里的一段文字，从不解析。
- **扩写只取前 7 个键。** 靠字典插入顺序，默认模型严格按七个键、按顺序返回（`ScienceDiscovery/utils.py:443`）；模型少给一个键时，第 7 个会取到代码追加的 `path_string`（`:403`）。
- **字段里没有出处与检验。** 七个字段都没有「这条依据来自哪篇文献 / 图上哪条边」，也没有「用什么实验或指标判定假设不成立」。提示词要求给数字，但不要求数字的来源：论文 Table 1 的「抗拉强度 1.5 GPa」「能耗降约 30%」是模型预测，论文自己标了「as predicted by our model」。
- **「每个概念都要用上」会把不相干的节点写进假设。** 附录 S5 的假设把胶原支架的力学性能与「蜘蛛丝和 vanadium(V)」相比；vanadium(V) 是五价钒这个氧化态，在公开图里度数 4，它与 mechanical properties 之间的边标签只有一个词「similar」。查新环节反而把这个比较记为「独特的角度」（S5 Novelty 一段）。

### 1.6 用 Semantic Scholar 查新

论文 §4.6 与 Figure 12：一个「novelty assistant」按假设挑关键词组合，调 Semantic Scholar 三次，每次拿最相关的 10 篇的标题和摘要，读完给 1 到 10 分的新颖性与可行性，要求「严格，尤其是新颖性，只有够发一篇新论文的想法才能过」。

| 环节 | 代码 | 证据 |
|---|---|---|
| 调用形态 | 工具 `rate_novelty_feasibility` 里再开一段嵌套对话：`novelty_admin` 与 `novelty_assistant`，清空历史，最多 10 轮，消息里写「最多调三次、不要并行」；结果用 `reflection_with_llm` 再让模型总结一次 | `ScienceDiscovery/agents.py:373-388` |
| 检索 | `GET https://api.semanticscholar.org/graph/v1/paper/search`，字段 `title,abstract,openAccessPdf,url`，不传 `limit`。本次实测不传 `limit` 时接口返回 10 条（响应里 `next: 10`），与论文的「10 篇」一致 | `ScienceDiscovery/agents.py:324-345`；[^s2] |
| 查询参数 | `'query': {query}` 写成了 Python 集合；按 requests 对可迭代参数值逐个展开的处理，结果仍是一个 `query` 参数（按库行为推断，未执行） | `ScienceDiscovery/agents.py:333` |
| key | 读环境变量 `SEMANTIC_SCHOLAR_API_KEY`。环境变量没设时 header 值是 `None`，requests 会丢掉这个 header，请求走无 key 的公共额度；两个 notebook 的第 3 格把它设成空串，这时发出去的是一个值为空的 `x-api-key` 头。README 写 Semantic Scholar API 是「运行代码所必需」。本次无 key 连发 8 次（4 次带空 key 头、4 次不带），7 次 429，只有 1 次不带头的返回 200；空 key 头会不会被区别对待没能确认 | `ScienceDiscovery/agents.py:341-342`；两个 notebook 第 3 格；`README.md:44`；[^s2] |
| 失败处理 | 非 200 不抛错，把「Request failed with status code …」字符串交给模型；系统提示词要求「调用不成功就一直重调」，而嵌套对话最多 10 轮 | `ScienceDiscovery/agents.py:348-354,308,382` |
| 结果 | 原始 JSON 整段进模型上下文；分数是模型写的自由文本，代码不解析、不落字段 | `ScienceDiscovery/agents.py:349,388` |
| 非自动版 | 没有查新 | `ScienceDiscovery/utils.py:411-518` |

附录对话里查新的实际表现：

| 案例 | 发生了什么 | 出处 |
|---|---|---|
| S3（微流控芯片） | 调工具之前对话里先有一段「新颖性高、可行性中」的定性自评，随后一行「call the rate_novelty_feasibility tool」才触发工具。工具只查了两次：查询 1 有 36 篇结果；查询 2 是 16 个词的长串，0 篇结果。评分 8/10，理由是「文献里没有找到直接匹配」 | 附录 S3 查新段；正文 Figure 10 |
| S2（silk 与 energy-intensive，路径由人给定） | 调工具之前对话里已有一段 9/10 的新颖性自评；工具查完给 7/10 | 附录 S2 |
| S5（胶原支架） | 调工具之前有 9/10 的自评；人打字「assistant, call the tool」，助手回「请说清要调哪个工具」，人再打「rate the novelty using the tool」；工具查完给 6/10，理由是电纺胶原纤维增强「已被大量研究」 | 附录 S5 |
| S4（胶原多孔结构） | 人打字要求调工具，agent 回「我没有叫 rate_novelty_feasibility 的工具」，先给了一段定性评估；人再打「Assistant, please call the tool」才出 8/10，这段评分里没有列检索结果 | 附录 S4（第 59 页） |

附录对话没有标发言者，上表里「人打字」的几行（S3、S4、S5 各一到两行短指令）是按上下文判断的：它们紧跟在 agent 的完整回复之后、是祈使句、并且引出了 agent「请说清要调哪个工具」这类回应。

同一轮调研里的 AI-Scientist 也有一条 Semantic Scholar 查新（AI-Scientist 仓 `ai_scientist/generate_ideas.py:405` 的 `check_idea_novelty`），见 [ai-scientist.md](ai-scientist.md)。

### 1.7 两种编排的差别

| | 非自动（论文 Figure 1b） | 自动（论文 Figure 1c） | 证据 |
|---|---|---|---|
| 谁定顺序 | Python 函数里写死的顺序 | LLM 发言调度，按 agent 的 description 挑人 | `ScienceDiscovery/utils.py:411-518`；`ScienceDiscovery/agents.py:398-407` |
| 上下文 | 每次只给筛过的部分 | 全员共享整段历史 | 论文 §2.2；1.4 节 |
| 查新 | 无 | 有 | 1.6 节 |
| 人 | 在 notebook 里写好参数后不参与 | `user` 每次被选中都等人输入，工具执行挂在 `user` 上 | `ScienceDiscovery/agents.py:16-23,356,373` |
| 模型调用 | 固定 12 次，直连 OpenAI | 不固定，最多 50 轮，每轮至少一次发言调度调用，经 AutoGen、带本地缓存 | 1.4 节 |
| 产出 | md + PDF + CSV | notebook 把对话历史拼成 md + PDF；拼接时每个工具调用的参数都取自下标为 1 的那条消息（`res.chat_history[1]`，应为 `[i]`） | `Notebooks/SciAgents_ScienceDiscovery_GraphReasoning_automated.ipynb` 第 8 格 |

论文对两者的比较（§2.2）：同一条路径下，两种编排的假设「概念与方法大体相同，细节不同」，差别来自上下文传递方式；自动版多了查新工具。

### 1.8 换一个领域要重建什么

| 部件 | 现在写死的是什么 | 位置 | 换领域要做的 |
|---|---|---|---|
| 图谱数据 | bio-graph-1K 的 graphml 与 embedding pickle，路径写死 `./graph_giant_component/`（相对当前目录），import 包时就加载（`__init__` → `agents` → `graph`） | `ScienceDiscovery/graph.py:4-20`、`ScienceDiscovery/agents.py:3`、`ScienceDiscovery/__init__.py:1-2` | 整张图重建：选论文集、转文本、切块、抽三元组、合并、取最大连通分量 |
| 建图提示词 | 「材料科学通用叫法」、蜘蛛丝 few-shot | `GraphReasoning/graph_generation.py:186-213,231-234` | 改领域词与例子 |
| 建图前处理 | Nougat 转换与「摘要 / 要点 / 标题」提炼 | 只在 GraphReasoning 论文 §4.2.1，仓里没有 | 自己实现 |
| embedding | bge-large-en-v1.5，英文模型；关键词和节点都靠它对齐 | `ScienceDiscovery/graph.py:8-11`；`GraphReasoning/graph_tools.py:116-122` | 中文或别的语言要换模型并重算全部节点 embedding |
| 假设字段措辞 | 化学式、序列、材料性能、「新材料或新体系」 | `ScienceDiscovery/utils.py:353-367`；`ScienceDiscovery/agents.py:93-109` | 改字段定义 |
| 扩写措辞 | 化学式、蛋白序列、工艺条件、微结构 | `ScienceDiscovery/utils.py:455-456`；`ScienceDiscovery/agents.py:141-143` 等七处 | 改 |
| 批评者的两个方向 | 分子建模、合成生物学 | `ScienceDiscovery/utils.py:493-499`；`ScienceDiscovery/agents.py:284-288` | 换成该领域的计算与实验手段 |
| 模型 | `gpt-4o` | `ScienceDiscovery/llm_config.py:3-5`；非自动版 notebook 第 6 格 | 改配置 |
| 查新 | 领域无关；覆盖面取决于 Semantic Scholar 在该领域的收录 | `ScienceDiscovery/agents.py:324-354` | 不用改 |

外部用户的反馈：issue #15「怎么用自己的数据」、#10「怎么评估、怎么和你们的方法比」都没有回复；#6 医学领域两个关键词「找不到路径」，另一位用户答「图里没有这两个词」[^gh]。这个回答与代码对不上：关键词总会被映射到 embedding 最近的节点（1.3），而图已经取了最大连通分量（`ScienceDiscovery/graph.py:14`），任意两个节点都连通，报错的真正原因见[第 5 节](#5-还没弄清的问题)。期刊版结论写「接入相应的领域图谱后有可能用到化学、合金、半导体、物理」，没有给出实际迁移的例子 [^advmat]。

## 2. 为什么有效：论文证据与代码对账

### 2.1 论文拿什么证明

| 论文的主张 | 证据形式 | 出处 | 性质 |
|---|---|---|---|
| 随机路径比最短路径带进更多概念，产出更有新意的假设 | 一对关键词的两张子图对比 | §2.1、Figure 4 | 示意，没有度量 |
| 多 agent 比零样本回答推理更细 | 一张概念图 | §3、Figure 11 | 没有零样本基线 |
| 生成的假设新颖且可行 | 5 个自动版案例，新颖性 6–8 分、可行性 7–8 分 | Table 4、附录 S3–S7 | 分数由 LLM 读检索摘要后给出；没有人工评审 |
| 两种编排各有长处 | 同一路径的两份产出并列 | §2.2、附录 S1 与 S2 | 定性描述 |
| 可扩展到几天产出成千上万个结果 | 一句话 | §3 | 没有给耗时与花费 |
| 换更强的模型效果更好（期刊版） | o1-preview 生成的一个案例 | 期刊版结论、附录 S8 | 定性，本次未读 S8 |

期刊版结论自己写了：部分提案的可行性存疑；要「建立效率、准确率这类明确指标，配合人类专家参与的评估框架」才能更全面评估 SciAgents，并把这些列为未来工作 [^advmat]。一稿与本次复查各做了两次网页搜索，都没有找到把 SciAgents 当基线做量化对比的第三方评测（未穷尽）。

### 2.2 代码是否按论文做

| # | 论文说 | 代码里 | 证据 |
|---|---|---|---|
| 1 | 路径代价 = embedding 启发式距离 + α·random（§4.2 伪代码里代价不累加） | 论文参数走到的函数里启发式零调用，代价是累计边权 + 每跳 0.2·random；启发式只在随机因子与路标数都为 0 时走到的另一个函数里用 | `GraphReasoning/graph_analysis.py:1707-1728`、`:141-148`；`ScienceDiscovery/utils.py:195-219` |
| 2 | 取完路径再带上二跳邻居作为上下文（§4.2 正文；同节算法第 7 步没写二跳） | `second_hop=False` 写死在两处调用参数里；子图建了不用，模型只看到路径一行字 | `ScienceDiscovery/utils.py:205,226,289,310`；`ScienceDiscovery/agents.py:368` |
| 3 | 图来自前作 [6]，33,159 节点，92 个社区 | 前作 Table 1 是 12,319 节点、80 个社区、最大度数 171；公开的图 33,159 节点，`group` 85 个值，最大度数 461；多出来的节点从哪来没有文档 | GraphReasoning 论文 §2.1、Table 1；本次解析 |
| 4 | Scientist 2 是一个 agent（Figure 1、§4.4、Figure S6） | 七个按字段分开的 agent；论文 Figure 9 的计划里倒是列了这七个名字 | `ScienceDiscovery/agents.py:137-269` |
| 5 | 查新调三次 API | 消息写「最多三次」；S3 实际两次 | `ScienceDiscovery/agents.py:383`；附录 S3 |
| 6 | 第二种编排「全自动」，人可以在各阶段介入 | `user` 是 `ALWAYS`；S3、S4、S5 三份对话里人打字催调查新工具 | `ScienceDiscovery/agents.py:19`；附录 S3–S5 |
| 7 | 附录 S2–S7 的对话 | 开场介绍（`send_introductions` 念出的各 agent description）与 `agents.py` 三个公开版本（1bf657d、ee2ee17、e821ee5）都对不上：S2–S5 是一套措辞（「planner: A planner who can suggest a plan…」「assistant: An assistant who calls the appropriate tools and functions and returns the results.」），代码里是「Who can suggest a step-by-step plan…」「…Tools include "rate_novelty_feasibility" and "generate_path".」；S6、S7 的开场都多一个 `caller`（S6「I am responsible to pick the next agent to speak」，S7「I am responsible for selecting the next role to speak」），对话里反复出现「Agent caller, please proceed…」「Caller, please select …」，三个公开版本都没有这个 agent；S7 的 planner、ontologist 简介与公开代码一致，assistant 简介不一致。产生这六份对话的代码都没有公开 | 附录 S2–S7 开场（S3、S7 的开场在 PDF 第 45、74 页的图片里）；GitHub 历史 [^gh] |
| 8 | 假设与批评之间有迭代反馈 | 非自动版批评不回流；自动版的附录对话里没有改稿 | `ScienceDiscovery/utils.py:485-508`；1.4 节 |
| 9 | GraphReasoning 论文：建图用 Zephyr-7B（llama.cpp、多卡）并先做摘要提炼 | 代码接受任意 `generate` 函数；提炼步骤不在仓里 | `GraphReasoning/graph_generation.py:167-290`；1.2 节 |
| 10 | 各 agent 的提示词（Figure 5、Figure S2–S7、Figure 12） | Figure 5（非自动版科学家）、Figure S2（planner）、Figure S4（ontologist）、Figure 12（查新）与代码几乎逐字一致；Figure S3（assistant）措辞不同，代码多了「结束时说 TERMINATE」；Figure S5 名字写 scientist1、Figure S7 不打分那句措辞不同；Figure S6 的单个 scientist2 提示词在代码里没有对应，代码是七个按字段分开、带字面占位符的提示词 | `ScienceDiscovery/agents.py:25-134,271-322`；`ScienceDiscovery/utils.py:315-386` |
| 11 | §4.3.2 各步的提示词 | 论文给的是缩写版，意思与代码一致 | `ScienceDiscovery/utils.py:444-499` |

### 2.3 案例自身的一致性

- **同一个例子用了不同的路径。** §2.1 印出的 silk 到 energy-intensive 路径（经 biocompatibility、self-cleaning、structural coloration）与附录 S1 的路径（经 biological materials、dandelion、pigments）不是同一条；Figure 3 的假设（蒲公英色素加蚕丝）对应的是 S1 那条。§2.1 的本体学家摘录里有 silk–membranes、high adhesion–multifunctionality 两条边，这两条都在公开图里，但不在 §2.1 印出的路径上。
- **印出的路径与公开图对得上。** §2.1、S1、S3 三条路径的每一条边（连同关系标签）本次都在公开图里逐边找到了，这说明论文用的就是（或包含）这张公开图，尽管它的尺寸与前作 Table 1 对不上（2.2 第 3 行）。Figure 8d 的端点「self-cleaning coating」在公开图里没有这个节点（有 self-cleaning coatings）。
- **「随机端点」与任务原文不一致。** §2.2 与 Figure 8 标题说五个案例的端点都是随机选的；S7 的任务原文是「Develop a research proposal using graphene and proteins」，端点是人给的。
- **Table 4 的五个想法有两对共用枢纽概念**：想法 2 与 3 都是胶原基材料，想法 4 与 5 都用 amyloid fibrils。公开图里 collagen 度数 345、排第 3，amyloid fibrils 度数 97、排第 33，这与 1.3 节「路径常经过度数高的枢纽」一致，但论文没有统计多样性。
- **未检索的自评高于检索后的评分**：S2 是 9 → 7，S5 是 9 → 6（1.6 节）。样本只有两份。

## 3. 平台哪里能用

先把平台这边的事实摆出来：七个阶段里文献、假设、写作还没有「步骤」；文献阶段的主文件是助理手写的 `sources.md`，假设与写作的主文件「待第一个能力定名」（纲领 P-20，内仓 `docs/add-a-capability.md`）。框架不调模型，写文本的只有执行层（P-1）；执行层会话放行的命令前缀只有 `ai4sci skill`（内仓 `framework/skills/__init__.py:37` 的 `EXECUTOR_BASH_RULES`、`framework/executor/session.py:42`），联网用 agent 自带的搜索与网页读取（P-14，内仓 `framework/executor/prompting.py:21-25`）。skill 是 `SKILL.md` 加 PEP 723 脚本，`uv run --locked --offline` 起，写哪里由调用方定（P-22）；`--offline` 管的是 uv 装依赖，现有 `download` skill 的脚本本身就联网拉 git 仓库与 Hugging Face 文件（内仓 `skills/download/SKILL.md`）。现有 skill 还有 `pdf`（论文转 `paper.md` 与 `structured.json`）。需要模型判断的评审要由隔离的新会话、只给产物不给轨迹，这一段尚未实现（P-2）。

SciAgents 这边的模型调用方式：每次调用都是 Python 代码直连 OpenAI API（非自动版 `generate_OpenAIGPT`，自动版 AutoGen），要 `OPENAI_API_KEY`，每个角色的 temperature（0 到 0.2）、token 上限、缓存都写在代码里（1.4 节）。平台里写文本的是执行层的 CLI 会话，走研究者自己的 agent 登录。

SciAgents 的方法按片段拆开，和上面这些事实的对应如下。表里只列事实与接触点，不下接不接的结论。

| 方法片段 | 阶段 | 需要的输入 | 产出 | 要不要模型 | 与平台规矩的接触点 |
|---|---|---|---|---|---|
| 建概念图：论文 → 文本块 → 三元组 → 合并 → 最大连通分量 | 文献 | 一批论文（`sources.md` 列的 PDF，经 `pdf` skill 出 `paper.md`）；embedding 模型 | graphml（节点、带标签的边、边的来源块）+ 节点 embedding | 抽三元组要模型，每块至少 4 次调用；合并与连通分量零模型 | P-1 下抽三元组只能在执行层会话里做；前作用了约 1,600 块、公开图更大，用 CLI 会话逐块抽的耗时与花费本次没有数据；公开图只有块 id、没有「块 → 论文」对照，要能引用就得在建图时留来源 |
| 取路径：关键词对到节点、随机 Dijkstra、随机路标、拼成一行字 | 假设 | 图文件、节点 embedding、两个关键词或「随机」、随机种子 | 一行路径字符串（可另存子图） | 零模型（embedding 前向除外） | 形状是确定性脚本，与 skill 的写法相近；依赖 torch 与 transformers；原实现没有种子参数、也不设种子，同样输入每次路径不同 |
| 本体学家 → 科学家 → 按字段扩写 | 假设 | 路径字符串（或任何一串概念与关系） | 七字段假设 + 七段扩写 | 要模型 | 写文本归执行层；七字段是材料领域措辞，字段里没有出处与检验判据；提示词要求的数字没有来源，平台纲领 §1 要求论文里每个数字都能被机器核对 |
| 批评者：总结、优缺点、两个优先问题 | 假设（其输出可作为设计阶段的输入） | 成稿 | 评审文字 + 两个「最值得做的建模 / 实验问题」 | 要模型 | 非自动版的批评调用只吃成稿、不吃过程（`ScienceDiscovery/utils.py:479-483`），形状接近 P-2 的「只给产物」，但与写稿是同一模型、同一脚本里的下一次调用；两个方向写死为分子建模与合成生物学 |
| 查新打分：挑关键词、检索、读摘要、打分 | 假设（也可以放在文献阶段） | 假设全文 | 检索结果 + 1–10 分与理由 | 检索零模型，挑词与打分要模型 | 平台两层 agent 联网用自带工具；走 Semantic Scholar API 是另一条通道，skill 脚本联网在平台上有 `download` 这个先例，这里不下结论；无 key 公共额度本次 8 次请求 7 次 429；已暴露的毛病见 1.6 |
| 成稿：图 → 扩展图 → 提案 → 扩写 → 评审 → 优先项 | 写作 | 上面各段的输出 | markdown / PDF 长文（S1 约 8,100 词） | 拼接零模型 | 这是开题式长文，不是论文，没有引用；workflow.md 提到「假设完直接写作是开题报告」这种组合 |

几条输入前提：研究者要给两个概念，或者接受随机；要有一张覆盖他那个领域的图，平台现在没有任何领域图，公开的 bio-graph-1K 只覆盖生物启发材料；查新用 Semantic Scholar 在代码上可以不带 key、走公共额度，README 写的是必需。

## 4. 局限与前提

### 4.1 数据

- **只有一张生物启发材料的图。** 论文集来自 BioinspiredLLM 的语料 [^luu]；其他领域要从零建（1.8 节）。
- **图上的边追不回论文。** 公开图每条边只有一个或几个不透明的 `chunk_id`，没有块原文、没有论文标识（1.2 节）。基于这张图写出的假设无法给出「这条关系出自哪篇文献」。
- **图是无向的**，关系标签的方向在取路径时可能被反着读（1.3 节）；建图时同一对节点反方向的关系按代码会互相覆盖（1.2 节）。
- **稀疏且有枢纽**：59% 的节点度数为 1，少数枢纽度数几百；路径常绕回枢纽。
- **标签质量不齐**：有整句、列表字符串、布尔值，190 条自环（1.2 节）。
- **近义节点残留**：0.95 的合并阈值下，同一概念有多个节点（「self-cleaning」一词就有 4 个同义节点）。
- **英文**：embedding 用英文模型；数据卡写的是用 `BAAI/bge-large-en` 生成的 embedding，文件名与论文写的是 v1.5，两者是否一致本次没法核对（没下 pickle）[^hf]。
- **建图过程没有完整文档**：公开图的节点数是前作报告的约 2.7 倍，用了哪些块、哪个模型、什么阈值都没写。

### 4.2 模型

- 自动版写死 OpenAI `gpt-4o`，key 走环境变量 `OPENAI_API_KEY`，由 AutoGen 0.2 的 `config_list_from_models` 去读（按 AutoGen 文档的行为推断，未执行）；两个 notebook 第 3 格把 `'sk-'` 写进这个环境变量。非自动版在 notebook 第 6 格把 key 与模型名显式传给 `generate_OpenAIGPT`。换模型要改 `ScienceDiscovery/llm_config.py` 与 notebook。
- 自动版的 `cache_seed: 42` 让同样的请求直接读本地缓存（1.4 节）；各角色温度只有 0 到 0.2，论文 §2.2 自己把假设的多样性归因于随机端点与端点间的路径。
- 建图在前作里用的是本地 7B 模型；前作 §3.2 自己写「受吞吐所限没用 GPT-4 这类更强的模型抽三元组」[^gr-paper]。

### 4.3 算力

- 运行时：import 包就加载 bge-large（约 3.35 亿参数）和整张图；每个关键词对全部节点做一次线性扫描；非自动版 12 次串行调用。论文没给单次耗时与花费。
- 建图时：每块至少 4 次模型调用；合并近义节点要算完整相似度矩阵，33k 节点在 float32 下约 4.4 GB、float64 下约 8.8 GB（1.2 节）；embedding 加载失败会退回对 33k 节点逐个重算（`ScienceDiscovery/graph.py:16-20`）。

### 4.4 许可证与数据使用

- 代码 Apache-2.0（`LICENSE.txt`），但两个 `setup.py` 的 classifier 写 MIT，打包元数据与许可证文件不一致。
- 图谱数据 apache-2.0；期刊论文 CC BY-NC 4.0（含论文里印出的提示词图）[^advmat]；代码里的同一批提示词随代码是 Apache-2.0。
- 源论文本身的版权：公开图只含三元组与块 id，不含原文。
- Semantic Scholar 数据的使用受它的 API License Agreement 约束；无 key 的请求共享每秒 1,000 次的公共额度，申请到的 key 起步是每秒 1 次 [^s2]。
- embedding 以 pickle 分发，`pickle.load` 读取（`GraphReasoning/graph_tools.py:129-132`）：读一个 pickle 会执行里面携带的代码，来源要可信。

### 4.5 工程形态

- **import 即副作用**：`from ScienceDiscovery import *` 经 `agents.py` 第 3 行导入 `graph.py`，会加载图、下 embedding 模型、建全部 agent（`ScienceDiscovery/__init__.py:1-2`、`ScienceDiscovery/agents.py:3`、`ScienceDiscovery/graph.py:10-20`、`ScienceDiscovery/agents.py:16-407`）；缺图文件就 import 失败。`utils.py` 还在 import 时拉起 GraphReasoning 的全部模块（含 guidance、llama-index）。
- **按 notebook 写的**：`display(Markdown(...))`、`tqdm.notebook` 散在函数里（`ScienceDiscovery/utils.py:21-26,37,467,501-502`）。
- **裸 `except` 吞错**：`ScienceDiscovery/graph.py:18`、`ScienceDiscovery/utils.py:406`、`GraphReasoning/graph_generation.py:280,287,452,561,594,646`。
- **依赖不锁**：见 1.1，`pyautogen` 无上限而 PyPI 上的新版已换成另一套 API [^pypi]；`weasyprint` 在 `utils.py` 顶部被 import 但没用到（`ScienceDiscovery/utils.py:7`），系统缺它要的库时整个包 import 失败，issue #8 报的「cannot load library 'gobject-2.0-0'」就是 weasyprint 找不到系统库时的报错（按报错文本推断）。
- **维护**：最后一次提交 2025-05-10，只改 README；评估与自定义数据两个 issue 无人回复 [^gh]。

## 5. 还没弄清的问题

1. **附录 S2–S7 是哪份代码跑出来的。** 六份自动对话开场念出的 agent 简介与公开的三个版本都对不上；S6、S7 还有 `caller` agent。论文 Table 4 的 5 个案例全部来自这些没公开的配置，其中 2 个（S6、S7）连 agent 组成都不同。
2. **公开图怎么建的。** 33,159 个节点比前作报告的全图大 2.7 倍，用了哪些块、哪个模型、什么合并阈值、为什么是 85 个社区值而论文写 92，都没有文档。论文印出的路径都在公开图里（2.3 节），Figure 8d 的端点「self-cleaning coating」却不在，是图注笔误还是图不同，没法判断。
3. **随机路标到底有没有带来更好的假设。** 论文只有 Figure 4 一张图；按论文参数走的函数里 embedding 启发式没被用上，路径实际由边权最短路与随机路标决定。要回答，得在同一批端点上对比最短路径、有无路标、有无二跳邻居，并有人或别的判据来评。
4. **查新分数有多可信。** 长查询 0 结果被当成新颖、未检索自评比检索后高，这两个现象在两三份对话里出现；缺更多样本，也缺与人工判断的对照。
5. **embedding 是否错配。** 数据卡说 embedding 用 bge-large-en 生成，代码用 bge-large-en-v1.5 算关键词向量；两者若不同，关键词对节点的匹配会偏。要下 138 MB 的 pickle 并抽样比对才能确认，同时能核对字典大小与 dtype。
6. **在平台上建一张领域图要多少时间和花费。** 平台里模型调用只能经执行层的 CLI 会话，逐块抽三元组在上千块的规模上走不走得通，本次没有数据。
7. **平台研究者的领域有没有现成语料或图。** 这决定取路径这一段有没有输入；中文材料还涉及换 embedding 模型。
8. **SciAgents 写在 API 参数里的东西在 CLI 会话里怎么对应。** 各角色 0 到 0.2 的 temperature、token 上限、自动版的本地缓存都是直连 API 时的参数；平台执行层是 CLI 会话，这些参数能不能设、不设对产出有什么影响，本次没有查。
9. **Semantic Scholar 无 key 能不能撑住。** 本次 8 次无 key 请求 7 次 429；代码把失败字符串交给模型、提示词让它一直重调、嵌套对话最多 10 轮。notebook 默认发出的空 `x-api-key` 头会不会被当成无效 key 拒掉，也没能确认。
10. **issue #6「No path found」的真实原因。** 图是连通的最大分量、关键词总会映射到某个节点，按代码只有「映射到的节点不在图里」（embedding 字典的键多于图的节点）这类情况才会找不到路径；这要下 pickle 比对键集合才能确认。
11. **今天按 `setup.py` 装得起来吗。** `pyautogen>=0.2.28` 无上限，PyPI 最新版是 autogen-agentchat 的代理包；GraphReasoning 要另装。本次不装依赖，没有验证。
12. **期刊版附录 S8（o1-preview 案例）** 本次没有取到，没读。
13. **第三方评测。** 前后四次网页搜索没找到把 SciAgents 当基线的量化对比，没有穷尽。
14. **`add_new_subgraph_from_text` 的 `G_newlymade` 问题** 是按代码读出来的，没有执行确认；作者自己建公开图时走的是不是这条路径也不清楚。

## 6. 调研方法

- 读 SciAgentsDiscovery 全部 Python、README 与两个 notebook（提交 c5c3045）；GraphReasoning 浅克隆到本会话的临时目录，读了被 SciAgents 调到的读图、embedding、取路径、OpenAI 调用四块，以及没被 SciAgents 调用的建图代码 `graph_generation.py`（提交 f1d6d44）；用 GitHub API 查了 `agents.py` 的三个历史版本、提交记录、issue 与 PR；查了 PyPI 上 `pyautogen` 的元数据。
- 论文 PDF 下到外层 `materials/research/2026-0927-scientific-ai-capabilities/papers/`，用平台的 `pdf` skill 解析：SciAgents arXiv v1（79 页，含附录 S1–S7 全部对话）、GraphReasoning arXiv 2403.11996（85 页）；期刊版从 Europe PMC 取全文 XML（PMC12138853），与 arXiv 版对照了节目录、表格、图注与 §4.1、§4.2、§4.6 的正文：新增的是「Audio Representation」一节与结论里的局限段，五张表与对照过的方法节文字没有变。
- 下载公开图 `large_graph_simple_giant.graphml`（14.5 MB）到临时目录，用 Python 标准库解析做统计：节点、边、方向、社区值、边权分布、`chunk_id` 个数、标签含逗号的分布、自环、度数、枢纽、端点度数、随机抽 1 万对端点的度数分布，以及 §2.1、S1、S3 三条路径的逐边核对。没有下 embedding pickle，没有 import 或执行 SciAgents 与 GraphReasoning 的任何代码。
- 对 Semantic Scholar 检索接口发了无 key 请求：一稿一次，确认不传 `limit` 时的默认条数；复查 8 次，确认空 key 头与不带头两种情形，结果见 1.6。
- 附录对话里的人工干预、自评与工具评分，是在解析出的正文里按关键词定位后逐段读原文确认的；S3 开场、S4 的评分段、S7 开场在 PDF 第 45、59、74 页的图片里，看图确认。
- 复查（同日，另一人）：逐条打开文中的 `文件:行` 核对，重算公开图统计，独立搜了「启发式零调用」「二跳写死」「非自动版无查新」「提炼步骤不在仓里」「caller 不在公开版本」「key 非必需」几条否定说法；改动集中在边权公式、`chunk_id`、逗号标签、相似度矩阵内存、JSON 失败路径、空 key 头、附录开场与公开代码的对照、notebook 格号。

[^gh]: GitHub 仓库 <https://github.com/lamm-mit/SciAgentsDiscovery>，2026-09-27 经 GitHub API 查：star、fork、提交列表（60 个，最早 77fee49 2024-08-21，最晚 c5c3045 2025-05-10）、`ScienceDiscovery/agents.py` 的三个历史版本（1bf657d、ee2ee17、e821ee5，e821ee5 与 c5c3045 上的文件相同）、issue #4 #5 #6 #8 #10 #15 与 PR #9 #12 #13 #14 #18（#13、#14 已合，只改 README；#9、#12、#18 未合）。
[^gr-repo]: GraphReasoning 仓库 <https://github.com/lamm-mit/GraphReasoning>，提交 f1d6d44（2024-07-19），Apache-2.0，301 star。
[^gr-paper]: M. J. Buehler, Accelerating Scientific Discovery with Generative Knowledge Extraction, Graph-Based Representation, and Multimodal Intelligent Graph Reasoning, arXiv:2403.11996（v3，2024-06-10）；期刊版 Machine Learning: Science and Technology (2024)，<https://doi.org/10.1088/2632-2153/ad7228>。引用的是 §2.1 Table 1、§3.2、§4.2.1–4.2.3。
[^advmat]: A. Ghafarollahi, M. J. Buehler, SciAgents: Automating Scientific Discovery Through Bioinspired Multi-Agent Intelligent Graph Reasoning, Advanced Materials 37(22), 2413523，<https://doi.org/10.1002/adma.202413523>，CC BY-NC 4.0；全文取自 Europe PMC <https://europepmc.org/article/PMC/PMC12138853>。arXiv 版 <https://arxiv.org/abs/2409.05556>（v1，2024-09-09）。
[^hf]: Hugging Face 仓库 <https://huggingface.co/lamm-mit/bio-graph-1K>（model 类型仓库），修订 888b9c7（2024-09-10），apache-2.0；文件 `large_graph_simple_giant.graphml` 14,513,359 字节，`embeddings_simple_giant_ge-large-en-v1.5.pkl` 137,838,158 字节；数据卡写「embeddings generated using BAAI/bge-large-en」。
[^luu]: R. K. Luu, M. J. Buehler, BioinspiredLLM, Advanced Science (2023)，<https://doi.org/10.1002/advs.202306724>。GraphReasoning 论文 §4.2.1 称沿用这批 1,000 多篇论文。
[^bge]: BAAI/bge-large-en-v1.5 模型卡 <https://huggingface.co/BAAI/bge-large-en-v1.5>：用 transformers 时取第一个 token（[CLS]）的最后一层隐状态并做 L2 归一化；仓里 `1_Pooling/config.json` 为 `pooling_mode_cls_token: true`；参数量 335,142,400。
[^s2]: Semantic Scholar API 页面 <https://www.semanticscholar.org/product/api>（2026-09-27 读）：多数接口无需认证，无 key 请求共享每秒 1,000 次的额度；key 的起步额度是每秒 1 次；使用受 API License Agreement 约束。本次对 `/graph/v1/paper/search` 发不带 `limit` 的请求，成功的一次返回 10 条、`next` 为 10；复查时连发 8 次（4 次带空 `x-api-key` 头、4 次不带），7 次返回 429「Too Many Requests」。
[^pypi]: PyPI `pyautogen` <https://pypi.org/project/pyautogen/>（2026-09-27 经 JSON API 查）：最新版 0.10.0，摘要「Proxy package for autogen-agentchat」，依赖 `autogen-agentchat>=0.6.4`；0.2 系列最后一版是 0.2.35。
