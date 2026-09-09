# 变更日志

本仓库所有值得注意的变更都记录在这里。格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本 2.0.0](https://semver.org/lang/zh-CN/)。

- 每个改动合并时，把条目写进 **Unreleased**；发布时 `make release VERSION=x.y.z` 把它轮转成版本小节并打 tag，推送 tag 即触发 GitHub Release。
- 1.0.0 之前是开发期：0.x 不承诺兼容性，正式发布才进入 1.0.0。
- 条目分类用：新增 / 变更 / 修复 / 移除 / 安全。

## [Unreleased]

### 新增
- 流水线层选型调研 `research/selection/2026-0909-pipeline-frameworks/`：InternAgent-1.5 代码级深读（四个读者分片读 `vendor/` 克隆，138 条带 `文件:行` 的发现，抽查 8 条属实），结论是抄任务契约与三块零件、不当流水线层底座；`README.md` 放候选清单与横向对比表，后续候选逐个补入
- 选型深读第二、三篇：autoresearch（两个读者，42 条发现，抽查 5 条；含 H100 真实跑档 125 次实验的数据与被删的 `spawn.sh`、未合并的 `agenthub` 协议）与 AutoResearchClaw v0.5.0（六个读者，177 条发现，抽查 13 条；四个总问题逐条对账 README 与代码）。对比表补齐三行，"目前能定下来的"从 4 条扩到 8 条：编排自己写、任务契约两层、内环用棘轮且裁判外置、评测由框架注入、验证层三条零 LLM 判据、底座 Runner 协议、人在环文件通道、四条机器可查的规矩
- `research/README.md` 新增 `selection/` 目录形态说明；行业调研的 InternAgent 条目与台账链接到深读
- `.gitignore` 新增 `/vendor/`：选型阶段拉来研究的第三方开源项目放这里，物理在树里、git 看不见

### 修复
- `make check` 的 html 同步检查只看未暂存改动与未追踪文件，md 改完 `make html` 并 `git add` 后本地门禁也能过；此前在提交前必报不同步

### 变更
- 调研第 10 节路线图改为按决策点排期：2026-09-28 发初级版，之后每月一个正式版、内测版随时发；原按传统工期的阶段表相应重排

## [0.2.0] - 2026-09-08

### 新增
- 第一篇调研《新工科自动化科研智能体：2026 年工业界现状与架构设计》：`research/landscape/2026-0908-auto-research-agents/`，正文里项目名链接到条目、数字挂脚注，附 `references.md` 台账
- 调研阅读版工具链 `md2html`：渲染 `research/` 下全部 .md（README.md → index.html，索引页与台账一并出 html），锚点按 GitHub 规则生成，站内 .md 链接改写为 .html，文内链接与脚注不能落地直接报错；`make html` 构建，`make check` 新增 html 与 md 同步检查
- `research/README.md` 写明一篇调研的目录形态与引用规则
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

[Unreleased]: https://github.com/zephyr4123/TJU-AI4Science/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/zephyr4123/TJU-AI4Science/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/zephyr4123/TJU-AI4Science/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/zephyr4123/TJU-AI4Science/releases/tag/v0.1.0
