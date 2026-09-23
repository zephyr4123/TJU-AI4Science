# TJU AI for Science · 外层协作仓

给 agent 与人的项目约定。仓库结构与承接步骤见 README；这里写规矩：拓扑、红线、怎么协作、写代码与验收的标准。内仓（`platform/`）有自己的 `CLAUDE.md`，改代码前读那份；产品边界与原则在 `docs/architecture/README.md`。

## 拓扑

- 本仓是**项目之家**：manifest、跨仓 CLI、文档、调研、案例卡、外部脚本。**不放业务代码。**
- 生产代码在内仓 `platform/`（独立 git，远端见 `repos.json`），外层 `.gitignore` 整目录挡住，两层互不知情。
- 内仓坐标以 `repos.json` 为唯一真相源；加仓、改地址只改它，然后 `./repos remotes --fix`。
- 承接：`git clone` 外层 → `./repos clone all` → `./repos status`；只用平台的人不 clone 这里，装内仓 Release 里的 wheel。
- 真实科研案例与演练：原件（PDF、数据、代码 zip）放 `materials/`，整目录 gitignore；仓里只放 `docs/cases/` 的案例卡、学长原文、sha256 索引与演练留下的小证据（评分契约、账本、对话记录，2 MB 以内）。案例卡按任务类型描述，应用领域只留一个名词。

## 红线（能用命令查的都进了 `make check`）

1. 外层 `git ls-files` 不出现业务代码；`platform/` 不依赖外层任何路径。（`make hygiene` 查常见代码扩展名，只放行 `.github/scripts/` 与 `scripts/`；shell 脚本与案例卡里以 md 代码块形式留档的脚本不算业务代码）
2. `scripts/` 是外部脚本与一次性工具，生产代码禁止 import；脚本一旦被生产用到就迁进内仓。
3. PDF、数据集、模型权重、实验产物不进 git，仓里只放索引与结论；单文件上限 2 MB。（`make hygiene`）
4. 跨仓变更以本仓的一条 GitHub issue 为锚，两边 commit message 都引用它；问「某功能改了哪些仓」查 issue 不查 git log。
5. 每个改动合并时写进 `CHANGELOG.md` 的 Unreleased；发版只走 `make release VERSION=x.y.z`，不手工打 tag。（`make changelog`）
6. `./repos` 的 pull 只 ff-only、push 永不 force、fetch 失败不吞，这些红线在代码里，不要删。
7. 在内仓下「某功能不存在」这类否定结论前，先看 `./repos status` 有没有 prod 分支漂移告警。
8. `research/` 是公开区：main 上的变动会把它整体渲染并发布到 <https://zephyr4123.github.io/TJU-AI4Science/>（`pages.yml`）。不想公开的材料不放这个目录。
9. `.claude/` 是本机会话产物，已 gitignore；不读取、不依赖。
10. commit、PR、文档里**不加 `Co-Authored-By`、不加「Generated with」尾注、不加机器人 emoji**。

## 协作方式：issue driven、spec coding

流程（分支模型、PR、review、发版、CHANGELOG 写法）只有一份，在 [`CONTRIBUTING.md`](CONTRIBUTING.md)；下面是纪律。

- **每个工作单元一条 issue**，开在本仓。做之前先有 issue；做的过程中发现、证据、决策随做随写进 issue 评论（贴 commit、贴数字、贴 `文件:行`），不攒总结。会话会压缩、聊天记录会丢，issue 和文档才是可靠的上下文；新会话先读 issue 与文档恢复上下文，不靠记忆。
- **先对齐再动手**：需求、边界、验收标准先写清（issue 正文或 `docs/specs/`），照它干活，做完回来改文档。纲领（`docs/architecture/`）改得慢、要双方认可；spec 与 issue 改得快，spec 是滚动的、不设 aligned 门槛。现实与文档不一致时先改文档再改代码；改了产品说法要回写纲领。
- **issue 的写法**：标题一句人话；标签三根轴——`kind:*`（什么类型，可多选）、`area:*`（哪一层）、`P0/P1/P2`；milestone 只挂 `kind:umbrella` 母 issue，叶子用 GitHub sub-issue 挂在它下面，不把几十条平铺在 milestone 上；要人拍板的加 `needs-decision`；`kind:decision` 的题定了也要关。
- **分支与 commit**：从当前的 `release/X.Y` 切 `feat/<issue 号>-<slug>`，分支内随做随提，一个逻辑单元一个 commit；message 用中文、技术名词保留英文、说改了什么和为什么、末尾 `（#n）` 引 issue。
- **回主干走 PR**：PR 进 `release/X.Y`，门禁绿 + 一人 review 才合；`main` 只接 release 分支与热修，由发版人合并打 tag。agent 不直接 push 受保护分支，改写历史要项目负责人确认。
- **做完必关**：merge+push 之后把这批 commit 引到的 issue 关掉，评论写做了什么、在哪个 commit（两个仓都写）；关之前核对代码里真有。做完不关的 issue 等于没做完的 issue。
- **过程即收益**：演练、决策、坑都沉淀成 issue 评论、案例卡（`docs/cases/`）或纲领变更记录；没人专门「补记录」。

## 写代码与验收的标准

细则按模块放在内仓（`platform/CLAUDE.md` §3 §4，以及 `framework/` `tests/` `ui/` 各自的 README）。跨仓通用的几条：

- **每一行代码都要有存在的理由**，可删的就是该删的；融入现有代码，新代码混在旧代码里看不出是后加的。
- **三个清晰**：目录清晰（打开仓库能猜到东西在哪）、结构清晰（分层明确、依赖只指向一个方向、无环）、模块清晰（单一职责、独立理解、独立测试、独立替换）。
- **有真实的第二个用例才抽象**，只有一个用例先写死；不为「以后可能」造抽象。涉及 agent、算力、界面的一律走端口 + 适配器，可替换。
- **重构要彻底**：不光加不删、不打补丁；旧入口逐个删干净并同步文档与测试；内测期没有兼容包袱。
- **错误处理显式**、不吞异常；未知的值写 NaN 不写 0；关键路径写带上下文的日志。
- **依赖**：成熟库优先，选型四看（维护活跃度、社区、许可证、安全记录），锁文件钉版本，环境隔离（Python 一律 venv，uv 管）。
- **文档随代码同步**：过期的文档比没有更糟；一个事实只有一个家，其余地方一句话加链接。
- **质量不由写的人自证**：改行为先写一条会失败的测试；机器能查的进门禁（`make check` 两仓都有，与 CI 完全相同，门禁命令别接 `| tail`）；页面改动过浏览器；agent 或工具报的 finding 是待验证输出，逐条核实才采信。
- **未取证不下结论**：查代码、查 git log、查日志再说话；提了假设就立刻验，验不了标「未验证」；「已验证」不是证据，命令与输出、数字、`文件:行` 才是。
- **写给人看的文字用直白的工程语言**：命令就是 tool，「人按」就是人确认；不写「裁判」「房间」「按钮」这类比喻，不造量词；页面文案照 `docs/architecture/workflow.md` §5 的词表。

## 版本

- 从 1.0.0 起承诺兼容：冻结的契约清单、MAJOR / MINOR / PATCH 的判据、弃用周期在 `CONTRIBUTING.md`「版本与发布」（ADR-0004）。外仓与内仓各自一条版本线，大版本同日对齐；spec 与 milestone 只用产品版本、带 `platform` 前缀。
- tag 形如 `vX.Y.Z`（预发布 `vX.Y.Z-rc.N`，在 `release/X.Y` 上打）；推送 tag 即触发 `.github/workflows/release.yml` 建 Release（外层只出 Release Notes，内仓的流水线出 wheel），rc 自动标 pre-release。
