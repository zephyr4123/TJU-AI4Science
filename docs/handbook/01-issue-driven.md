# 01 issue driven：每个工作单元一条 issue

## 场景

你要做一件事：修个 bug、加个能力、整理一片文档、做一次演练。做之前、做的过程中、做完之后，这件事的信息该放在哪，别人（包括三个月后的自己、下一个会话的 agent）怎么找到它。

## 做法

1. **先有 issue，再动手。** 开在外层仓（跨仓的改动也只开一条，两边 commit 都引它）。标题一句人话，写清「什么坏了 / 要什么」，不写「优化」「完善」这种没信息量的词。
2. **正文写四段**：现象或目标、边界（改哪不改哪）、入口（从哪个文件读起）、验收（怎么算做完，最好是一条能跑的命令）。写不出验收，说明还没想清，先别派活。写法见 [02](02-brief-an-agent.md)。
3. **标签三根轴**：`kind:*`（bug / feat / fix / decision / research / infra / umbrella …，可多选）、`area:*`（哪一层）、`P0 / P1 / P2`。大活开一条 `kind:umbrella`，叶子用 GitHub 的 sub-issue 挂在它下面；milestone 只挂母 issue，不把几十条平铺上去。
4. **过程写进评论，随做随写。** 发现了什么、试了什么、看到什么、决定了什么，当场贴：commit 哈希、命令与输出、数字、`文件:行`。不攒到最后写总结——会话会压缩、聊天记录会丢，评论不会。
5. **commit 末尾 `（#n）`**，message 说改了什么和为什么。
6. **做完必关。** merge + push 之后，关 issue 时评论写做了什么、在哪个 commit（两个仓都写）；关之前核对代码里真有。做完不关的 issue 等于没做完的 issue。决策类的题（`kind:decision`）定了也要关，评论写定了什么。
7. 要人拍板的加 `needs-decision`，不要在评论里反复问；拍板的人看这个标签。

## 反例

- 「口头说一下就改」：改完谁也不知道为什么改，下次 agent 读代码只看到结果，把它当成有意为之。
- 一条 issue 装十件事：关不掉，也说不清做到哪了。
- 攒总结：做了三天最后写一段「本次完成了……」，中间的坑、试错、否掉的方案全没了，而那些才是下次最值钱的。
- 开了不关：追踪列表里真开着的和早做完的混在一起，没人再看它。本仓 2026-09-23 一次清理关了 42 条，剩 11 条是真开着的——清之前列表已经没法用了。

## 本仓真实例子

- 母 issue 与 sub-issue：[#130](https://github.com/zephyr4123/TJU-AI4Science/issues/130)「底座归人」是 umbrella，下面挂 [#131](https://github.com/zephyr4123/TJU-AI4Science/issues/131)–[#135](https://github.com/zephyr4123/TJU-AI4Science/issues/135) 五条叶子（Codex 适配器、agents.yaml、设置页、删除、演练）；用 `gh api repos/zephyr4123/TJU-AI4Science/issues/130/sub_issues` 能列出来。
- 一条 bug 从发现到关：[#144](https://github.com/zephyr4123/TJU-AI4Science/issues/144)。写手册这天发现内仓 CI 从 `7a4638b` 起三次全红，本地却是绿的。先开 issue 写清现象、根因（uv 建的 venv 没有 pip，`python -m pip freeze` 直接失败）、修法、怎么验；再改代码，commit 引 `（#144）`，CHANGELOG 加一行，PR 上 CI 绿了才关。
- 跨仓一条锚：[#142](https://github.com/zephyr4123/TJU-AI4Science/issues/142) 发 1.0.0 的流程改动同时改了两个仓（CONTRIBUTING、脚本、CI），两边的 commit 都引 #142；问「这件事改了哪些仓」查 issue，不翻 git log。
- 规矩本身：[`CLAUDE.md`「协作方式」](../../CLAUDE.md#协作方式issue-drivenspec-coding)。
