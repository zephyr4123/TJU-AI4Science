# ADR-0004：分支模型、1.x 版本策略与 CHANGELOG 规则

- 状态：已采纳
- 日期：2026-09-23
- 取代 [ADR-0002](0002-versioning-and-release.md) 的「版本号从 0.1.0 起步、0.x 不承诺兼容」与「变更日志」两条；补充 [ADR-0003](0003-tracking-scope-and-release-artifacts.md)

## 背景

第一版框架已经冻结（纲领 P-1 到 P-25，文档全部对齐代码，[#140](https://github.com/zephyr4123/TJU-AI4Science/issues/140)），要发正式版并开始分工让别人来做。之前是一个人加 agent 在 `main` 上直接干：分支内随做随提、合并前问一句、`make check` 绿就推。人多了这套不够：谁在哪个版本上干、什么时候合、合进去的东西谁看过、发出去的东西承不承诺兼容，都要有规矩，而且规矩要机器守（GitHub 的分支规则、CI、`changelog.sh`）。内仓同日转公开，分支保护没有计划限制了。

## 决定

- **版本从 1.0.0 起承诺兼容。** 冻结的契约清单与 MAJOR / MINOR / PATCH 的判据写在 `CONTRIBUTING.md`「版本与发布」；不兼容的改动走弃用周期（一个 MINOR 里旧路标弃用 + 迁移办法，下一个 MAJOR 才删）。两仓各自一条版本线：内仓 tag 是产品版本，外层 tag 是文档版本，大版本同日对齐。
- **分支模型**：`main` 永远可发、只接 PR；开一个版本从 `main` 切 `release/X.Y`；干活从 `release/X.Y` 切 `feat/<issue 号>-<slug>`、PR 回 `release/X.Y`；版本做完发版人把 `release/X.Y` 合进 `main` 打 tag；热修 `hotfix/X.Y.Z` 从 `main` 切、合回 `main` 再合回 release 分支。PR 只用 merge commit（保留每条 commit 与 issue 里引的哈希）。
- **机器守的**：`main` 与 `release/**` 上 GitHub ruleset——禁 force push、禁删、要求 PR、一人 review、CI `check` 通过；仓库管理员可绕过（一个人维护时不被自己卡死）。CI 在 `main`、`release/**` 与所有 PR 上跑 `make check`。
- **预发布**：`release/X.Y` 上打 `vX.Y.0-rc.N`（`make release VERSION=X.Y.0-rc.N` 只打 tag、不轮转 CHANGELOG），流水线出包并标 pre-release，Release Notes 取 Unreleased；正式版从 `main` 打。`changelog.sh` 与 `release.sh` 认 `-rc.N`（关 [#17](https://github.com/zephyr4123/TJU-AI4Science/issues/17)）。
- **CHANGELOG 规则**：Unreleased 里每条一行、≤ 200 字、带 `#issue` 或链接，只说用户看得见的变化，细节在 issue；不兼容条目必须写迁移办法；`changelog.sh check` 守着。历史小节不回改。
- **PR / issue 模板与 CODEOWNERS**进 `.github/`；`CONTRIBUTING.md` 两仓根各一份（内仓那份只有合并前清单，流程不复制）。

## 后果

- 单人开发时多一次开 PR 的动作；换来的是每个合入都有 CI 记录与可 review 的入口，agent 干的活和人的一样过门禁。
- 1.x 之后改契约要走弃用周期，快速重构的自由变小；这正是「冻结」的意思。
- 一个人维护时 review 会由管理员绕过；人手够了把绕过去掉。
