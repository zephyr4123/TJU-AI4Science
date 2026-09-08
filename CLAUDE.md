# TJU AI for Science · 外层协作仓

给 agent 与新成员的项目约定。仓库结构与承接步骤见 README；这里只写规矩。

## 拓扑

- 本仓是**项目之家**：manifest、跨仓 CLI、文档、调研、外部脚本。**不放业务代码。**
- 生产代码在内仓 `platform/`（独立 git，远端见 `repos.json`），外层 `.gitignore` 整目录挡住，两层互不知情。
- 内仓坐标以 `repos.json` 为唯一真相源；加仓、改地址只改它，然后 `./repos remotes --fix`。
- 承接：`git clone` 外层 → `./repos clone all` → `./repos status`。

## 红线（能用命令查的都进了 `make check`）

1. 外层 `git ls-files` 不出现业务代码；`platform/` 不依赖外层任何路径。（`make hygiene`）
2. `scripts/` 是外部脚本与一次性工具，生产代码禁止 import；脚本一旦被生产用到就迁进内仓。
3. PDF、数据集、模型权重、实验产物不进 git，仓里只放索引与结论；单文件上限 2 MB。（`make hygiene`）
4. 跨仓变更以本仓的一条 GitHub issue 为锚，两边 commit message 都引用它；问"某功能改了哪些仓"查 issue 不查 git log。
5. 每个改动合并时写进 `CHANGELOG.md` 的 Unreleased；发版只走 `make release VERSION=x.y.z`，不手工打 tag。（`make changelog`）
6. `./repos` 的 pull 只 ff-only、push 永不 force、fetch 失败不吞，这些红线在代码里，不要删。
7. 在内仓下"某功能不存在"这类否定结论前，先看 `./repos status` 有没有 prod 分支漂移告警。

## 版本

- 从 0.1.0 起步，0.x 为开发期不承诺兼容；正式发布才进入 1.0.0。
- tag 形如 `vX.Y.Z`；推送 tag 即触发 `.github/workflows/release.yml` 建 Release，0.x 自动标 pre-release。

## 其它

- `.claude/` 是本机会话产物，已 gitignore；不要读取或依赖其中内容。
- commit message 用中文，技术名词保留英文；一个逻辑单元一个 commit。
- 技术栈与集群方案尚未确定，内仓目录只是位置约定，不要提前引入框架级抽象。
