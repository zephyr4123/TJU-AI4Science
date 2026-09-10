# 变更日志

本仓库所有值得注意的变更都记录在这里。格式遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本 2.0.0](https://semver.org/lang/zh-CN/)。

- 每个改动合并时，把条目写进 **Unreleased**；发布时 `make release VERSION=x.y.z` 把它轮转成版本小节并打 tag，推送 tag 即触发 GitHub Release。
- 1.0.0 之前是开发期：0.x 不承诺兼容性，正式发布才进入 1.0.0。
- 条目分类用：新增 / 变更 / 修复 / 移除 / 安全。

## [Unreleased]

### 变更
- 架构纲领三箱改四层：加协调层（人 + 协调 agent），科研判断归它，框架降为诚实执行基底，不连跑、不等人；"阶段"改"能力"、"底座"改"执行层"，人在环模式与文件通道移除；加 P-10 P-11 与 `coordinator/` 目录。spec 的 R-5 R-7 N-2 改写，新增 R-10 C-7 A-11；未决项加 Q-10；决策 issue #18，Q-10 是 #19；纪要 `docs/meetings/2026-0910-coordinator-layer.md`。spec 状态改为滚动：只驱动下一步，不设 aligned 门槛。纲领 workflow §5 加算力端口 `Compute`（put / submit / wait / cancel / get，句柄落盘，靠名字选择、不静默回退），目录加 `compute/`
- 内仓远端就位：`repos.json` 的 url 由 `TBD` 改为 <https://github.com/zephyr4123/TJU-AI4Science-Platform>（私有），`./repos remotes --fix` 接好 origin，骨架与 v0.1.0 首次推送；根 README、spec、纪要同步

## [0.3.0] - 2026-09-10

### 新增
- 流水线层选型调研 `research/selection/2026-0909-pipeline-frameworks/`：InternAgent-1.5 代码级深读（四个读者分片读 `vendor/` 克隆，138 条带 `文件:行` 的发现，抽查 8 条属实），结论是抄任务契约与三块零件、不当流水线层底座；`README.md` 放候选清单与横向对比表，后续候选逐个补入
- 选型深读第二、三篇：autoresearch（两个读者，42 条发现，抽查 5 条；含 H100 真实跑档 125 次实验的数据与被删的 `spawn.sh`、未合并的 `agenthub` 协议）与 AutoResearchClaw v0.5.0（六个读者，177 条发现，抽查 13 条；四个总问题逐条对账 README 与代码）。对比表补齐三行，"目前能定下来的"从 4 条扩到 8 条：编排自己写、任务契约两层、内环用棘轮且裁判外置、评测由框架注入、验证层三条零 LLM 判据、底座 Runner 协议、人在环文件通道、四条机器可查的规矩
- `research/README.md` 新增 `selection/` 目录形态说明；行业调研的 InternAgent 条目与台账链接到深读
- `.gitignore` 新增 `/vendor/`：选型阶段拉来研究的第三方开源项目放这里，物理在树里、git 看不见
- 架构总纲领 `docs/architecture/`（README 三箱结构与九条原则、workflow 阶段骨架与实验内环、packs 任务包与领域包、open-questions 九项未决）；`docs/specs/platform-0.2.0.md` 初级版 PRD 草稿（R / N / C / A 编号，目标 2026-09-28）；`docs/meetings/2026-0910-workflow-alignment.md`；`docs/adr/README.md` 划定 adr 只放仓库基础设施决定。vision 与根 README 同步

### 变更
- 文档体系分四类：`architecture/` 可改的总纲领（改要双方认可 + 变更记录）、`specs/` 每版一份 PRD、`adr/` 只追加、`meetings/` 只记结论；协作方式定为 spec coding + issue driven
- 两条版本线分开命名：外仓版本只管项目之家，产品版本一律带 `platform` 前缀（初级版 = platform 0.2.0，0.1.0 是骨架）；milestone 与 spec 文件名只用产品版本。issue 面板建立：目标合约、五条母 issue 挂 milestone、Q-1 到 Q-9 各一条决策 issue、科研案例采集 issue
- 调研第 10 节路线图改为按决策点排期：2026-09-28 发初级版，之后每月一个正式版、内测版随时发；原按传统工期的阶段表相应重排

### 修复
- `make check` 的 html 同步检查只看未暂存改动与未追踪文件，md 改完 `make html` 并 `git add` 后本地门禁也能过；此前在提交前必报不同步

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

[Unreleased]: https://github.com/zephyr4123/TJU-AI4Science/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/zephyr4123/TJU-AI4Science/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/zephyr4123/TJU-AI4Science/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/zephyr4123/TJU-AI4Science/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/zephyr4123/TJU-AI4Science/releases/tag/v0.1.0
