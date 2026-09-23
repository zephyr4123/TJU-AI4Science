# ADR-0003：外层追踪范围修订与两仓发版差异

- 状态：已采纳
- 日期：2026-09-23
- 补充 [ADR-0001](0001-nested-git-topology.md) 与 [ADR-0002](0002-versioning-and-release.md)，不推翻

## 背景

ADR-0001 写外层只追踪 `repos.json`、`./repos` CLI、文档、调研、外部脚本；ADR-0002 写技术栈未定、推 tag 出 `tar.gz`。两周下来实际情况变了：外层还追踪了 `Makefile`、`.github/`（CI、发版、渲染脚本）、`CHANGELOG.md`、`CLAUDE.md`，以及三轮演练留下的小证据（评分契约、账本、对话记录、以 md 代码块留档的评分脚本）；内仓技术栈已定（Python 3.12+ / uv、React + Vite、node 22），发版出的是 wheel + sdist；外层的发版流水线不出包，只出 Release Notes。文档盘点（[#140](https://github.com/zephyr4123/TJU-AI4Science/issues/140)）发现这些与两条 ADR 的字面不一致。

## 决定

- **外层追踪范围**：除 ADR-0001 列的五类外，还包括仓库自身的工具与门禁（`Makefile`、`.github/`）、`CHANGELOG.md`、`CLAUDE.md`，以及 `docs/cases/` 下演练留下的**小证据**：评分契约、账本、对话记录、脚本（以 md 代码块留档），单文件 2 MB 以内。原件（PDF、数据、代码 zip、模型权重）仍不进 git。`make hygiene` 查常见代码扩展名与 2 MB 上限；shell 脚本与 md 代码块里的脚本不在它的判据内，靠 review。
- **两仓发版流水线不同**：外层推 tag → 校验 CHANGELOG → 建 GitHub Release（只有 Release Notes，没有包）；内仓推 tag → `make check` → `make package`（构建页面、拷出厂件、`uv build` 出 wheel + sdist + sha256）→ 建 Release 并附包。版本号内仓由 setuptools-scm 从 tag 读。
- **`-rc.N` 预发布号**：CHANGELOG 校验脚本还不认，[#17](https://github.com/zephyr4123/TJU-AI4Science/issues/17) 开着；在它落地前不打 rc tag。
- **技术栈已定**：内仓 `pyproject.toml` 与 `ui/web/package.json` 为准，两仓 CI 与内仓发版流水线绑 Python 3.14 / node 22 / uv；ADR-0002「流水线不绑工具链」那句只对外层仍成立。

## 后果

- 外层「零业务代码」的判据比字面松：案例卡里可以有脚本，但只作证据、不被任何东西 import。
- 只用平台的人从内仓 Release 装 wheel；外层 Release 只是文档的版本快照。
