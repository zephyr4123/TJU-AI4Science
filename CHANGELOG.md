# 变更日志

本仓库所有值得注意的变更都记录在这里。格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本 2.0.0](https://semver.org/lang/zh-CN/)。

- 每个改动合并时，把条目写进 **Unreleased**；发布时 `make release VERSION=x.y.z` 把它轮转成版本小节并打 tag，推送 tag 即触发 GitHub Release。
- 1.0.0 之前是开发期：0.x 不承诺兼容性，正式发布才进入 1.0.0。
- 条目分类用：新增 / 变更 / 修复 / 移除 / 安全。

## [Unreleased]

### 新增
- 第一篇调研《新工科自动化科研智能体：2026 年工业界现状与架构设计》：`research/landscape/2026-0908-auto-research-agents/`，正文里项目名链接到条目、数字挂脚注，附 `references.md` 台账
- 调研阅读版工具链 `md2html`：README.md → index.html，锚点按 GitHub 规则生成，文内链接与脚注不能落地直接报错；`make html` 构建，`make check` 新增 html 与 md 同步检查
- `research/README.md` 写明一篇调研的目录形态与引用规则
- `md2html` 改为渲染 `research/` 下全部 .md（索引页、台账一并出 html），站内 .md 链接改写为 .html
- GitHub Pages 管线 `pages.yml`：仓库转为公开，`research/` 定为公开区，main 更新即重新渲染并整体发布到 <https://zephyr4123.github.io/TJU-AI4Science/>；新调研进 main 自动上线

### 变更
- 内仓远端尚未创建，`repos.json` 的 url 改为 `TBD` 占位，不再写编造的地址；`./repos` 对占位仓只报告状态，clone / fetch / sync / pull / push 明确拒绝并退非 0
- `changelog.sh` 的链接引用允许 `TBD` 占位，但在占位上 `release` 会被拒绝

## [0.1.1] - 2026-09-08

### 修复
- `./repos remotes --fix` 对刚 `git init`、尚无 origin 的内仓会报错退出；现在 origin 不存在就 add，存在才 set-url

## [0.1.0] - 2026-09-08

### 新增
- 项目之家骨架：`repos.json` 内仓 manifest、`./repos` 跨仓 CLI（doctor / clone / status / sync / pull / push / remotes）、`.gitignore` 挡位
- 目录约定：`docs/`（项目级文档与 ADR）、`research/`（调研）、`scripts/`（外部脚本，生产代码不得依赖）、`assets/`
- 变更日志与发布流水线：CHANGELOG 机器校验、`make release` 轮转、tag 触发 GitHub Release
- ADR-0001 内外仓拓扑、ADR-0002 版本与发布策略

[Unreleased]: https://github.com/zephyr4123/TJU-AI4Science/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/zephyr4123/TJU-AI4Science/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/zephyr4123/TJU-AI4Science/releases/tag/v0.1.0
