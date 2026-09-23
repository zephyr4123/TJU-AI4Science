# 05 先搜再答：AI 的知识有截止日期

## 场景

你问 agent「Codex CLI 怎么配自定义 provider」「uv 怎么建 venv」「这个库最新版怎么用」「DeepSeek 现在什么价」。它答得很流利。问题是它的知识停在训练截止的那一天，而这些东西一年里能变好几次。答得流利和答得对是两回事。

## 做法

1. **默认它的记忆是旧的。** 凡是 CLI 的 flag、库的版本与 API、模型名与价格、平台的政策、最近一年冒出来的工具，都当作「需要查」。
2. **让它用自带的联网搜索，不是让它凭记忆答。** 成熟的 coding agent 都带联网工具：Claude Code 有 WebSearch / WebFetch，Codex 有 web_search，桌面端的 Claude 与 ChatGPT 有「搜索网页」。派活时明说：「先用你的联网搜索查官方文档 / release notes，再给方案，附来源链接」。
3. **要来源。** 答案里没有链接的，问它从哪来的。有链接的，点开看一眼是不是它说的那样（[04](04-evidence-not-claims.md)）。
4. **用新东西。** 知识截止日期意味着它默认推荐旧方案：旧的打包工具、旧的 API 写法、已经被替代的库。选型时让它查「现在大家用什么」，选型四看（维护活跃度、社区、许可证、安全记录）都要查得到当下的数据。
5. **给它工具，不然它会硬凑。** 联网工具没放行，它不会老实说「我查不了」，会在 Bash 里拿 curl 抓网页、拿 grep 解析 HTML，效果差还费 token。放行自带工具，并在 prompt 里写清什么时候查。
6. **写进产品的 prompt。** 平台自己的两层 agent 也一样：研究助理与执行层的提示词里写了什么时候查（研究者给了链接、论文有没有公开代码与数据、API 或报错拿不准、近期事实）、只用自带工具、查到的带来源链接。

## 反例

- 「我记得这个 flag 是 `--model-provider`」——记得的是半年前的版本，现在早改名了。照着写，CLI 报「unknown flag」，agent 再猜三次。
- 让它从记忆里写一份依赖版本清单：版本号是旧的，有的包早改名。
- 「这个库最好用」——最好用是它训练那年的判断。
- 联网工具被拒，agent 在 Bash 里 `curl | grep` 搜索引擎结果页，抓回来一堆 HTML。

## 本仓真实例子

- 硬凑的根因与修法：[#114](https://github.com/zephyr4123/TJU-AI4Science/issues/114)。实测 `--permission-mode dontAsk` 下 WebSearch / WebFetch 不在白名单里就被拒，拒绝信息还说「你可以用别的工具试试」，agent 于是在 Bash 里拿 curl 硬搜。修法：端口（内仓 `backends/__init__.py`）写成要求——适配器必须放行这家 CLI 自带的联网搜索与网页读取工具；Claude Code 适配器两层白名单都加上；prompt 写清什么时候查。机器判据：`tests/test_backend_claude_code.py::test_argv_grants_the_clis_own_web_tools_on_both_layers`。放开之后一轮里搜索 + 读 GitHub releases 页都通。
- 按官方文档对账：[#131](https://github.com/zephyr4123/TJU-AI4Science/issues/131) 写 Codex 适配器时，每个 flag 都对着当时的官方文档核，再用真 CLI 冒烟测试；不信记忆里的用法。
- 按开放规范写：[#113](https://github.com/zephyr4123/TJU-AI4Science/issues/113) skill 系统照 agentskills.io 的 SKILL.md 格式，而不是自己发明一个——查到有现成规范就用现成的。
- 平台里的写法：内仓 `framework/chat/guide.py`（研究助理前言）、`framework/executor/prompting.py` 的 `WEB_RULE`、内仓根目录 `coordinator/README.md`「工具包与联网」。
