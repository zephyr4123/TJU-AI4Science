# 03 小步快跑与门禁

## 场景

改代码。怎么让改动随时可以停、可以回退、可以让别人看；怎么让「能不能合」由机器说了算而不是由写的人自证。

## 做法

1. **开分支。** 从当前的 `release/X.Y` 切 `feat/<issue 号>-<slug>`（只改文档 `docs/…`）。有分支才敢大刀阔斧：错了扔掉分支就行。
2. **分支内随做随提，一个逻辑单元一个 commit。** 改一处、验一处、提一处；message 中文、技术名词保留英文、说改了什么和为什么、末尾 `（#n）`。不堆成一个胖 commit——review 时看不出哪一行是为什么改的。
3. **门禁是同一条命令。** 两仓都有 `make check`，与 CI 完全相同；提交前跑它。**别接 `| tail`**——管道会吞掉退出码，红的看成绿的。
4. **改行为先写一条会失败的测试**，再改代码让它绿。机器能查的进门禁（分层检查、文案禁词、CHANGELOG 格式都是这么进去的），人只看机器查不了的：意图对不对、抽象合不合理。
5. **出分支走 PR。** PR 进 `release/X.Y`，门禁绿 + 一人 review 才合；只用 merge commit。`main` 与 `release/**` 有 GitHub ruleset 守着：不许直接 push、不许 force、要求 `check` 通过。agent 不直接 push 受保护分支；合并、push 远端、改写历史之前要人点头。
6. **本地绿不等于 CI 绿。** 环境不一样（下面的例子）。开了 PR 看 `gh pr checks`，红了 `gh run view <id> --log-failed` 看原因，别猜。
7. **合并即收尾**：CHANGELOG 的 Unreleased 一行、关 issue、删分支。流程细节在 [`CONTRIBUTING.md`](../../CONTRIBUTING.md)。

## 反例

- 在 `main` 上直接改：没有回退，没有 review 入口，agent 一次误操作就进了主干。
- 「我本地跑过了」：跑的是哪条命令、输出是什么、退出码多少，都没有。
- `make check | tail -3` 看着清爽，退出码永远是 `tail` 的 0。
- 门禁在后台跑着，没等结果就 commit + push。本手册作者写手册这天就犯了：`make check` 起在后台，看到相关测试过了就提交推送，结果门禁报三条 ruff E501，只好再补一个 commit（内仓 `18e7f32`）。等结果，或者把门禁放在同一条命令里用 `&&` 串起来。

## 本仓真实例子

- CI 红了三次没人看见：[#144](https://github.com/zephyr4123/TJU-AI4Science/issues/144)。内仓 `main` 上从 `7a4638b` 起 CI 连续三次失败，本地 `make check` 一直绿——本机 `.venv` 恰好有 pip，CI runner 上 uv 建的 venv 没有。那时 CI 只在 push 后跑、不拦任何东西，红了也没有后果。1.0.0 起 ruleset 要求 PR 上的 `check` 通过才能合（[ADR-0004](../adr/0004-branching-versioning-1.0.md)），这条路被焊死了。
- 机器判据怎么进门禁：内仓 `tests/` 里有分层检查（依赖只指向一个方向）、页面文案禁词（`ui/web/src/copy.test.ts`）、CHANGELOG 格式（`.github/scripts/changelog.sh check`）；每条都是先有人犯过一次，然后变成测试。见内仓 `tests/README.md`。
- 一条改动的 commit 切法：外层 [#141](https://github.com/zephyr4123/TJU-AI4Science/issues/141) README 做地图，Mermaid 图每张单独验证（浏览器渲染截图）再提交，图排版不对就只改那一个 commit。
