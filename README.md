<h1 align="center">TJU AI for Science</h1>

<p align="center">科研全自动化 · 项目之家（协作仓）</p>

<p align="center">
  <a href="https://github.com/zephyr4123/TJU-AI4Science/actions/workflows/ci.yml"><img alt="ci" src="https://github.com/zephyr4123/TJU-AI4Science/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/zephyr4123/TJU-AI4Science/releases"><img alt="release" src="https://img.shields.io/github/v/release/zephyr4123/tju-ai4science?include_prereleases&label=release"></a>
  <a href="CHANGELOG.md"><img alt="changelog" src="https://img.shields.io/badge/changelog-keep%20a%20changelog-blue"></a>
</p>

## 这是什么

面向天津大学课题组的科研全自动化平台。本仓是**项目之家**：存放调研、文档、决策记录、外部脚本，以及指向生产代码仓的坐标。生产代码在独立的内仓 [`tju-ai4science-platform`](https://github.com/zephyr4123/tju-ai4science-platform)，clone 后落在本仓的 `platform/` 目录下，但对本仓的 git 完全不可见。

## 五分钟承接

```bash
git clone https://github.com/zephyr4123/TJU-AI4Science.git
cd tju-ai4science
./repos clone all      # 按 repos.json 把内仓 clone 到位（幂等）
./repos status         # 各仓分支 / 领先落后 / 脏文件 / 线上分支漂移
make check             # 本地门禁，与 CI 完全相同
```

clone 下来没有代码是预期不是故障：代码仓由 `./repos clone all` 解引用。

## 目录

```
tju-ai4science/
├── repos.json        内仓拓扑 manifest（唯一真相源）
├── repos             跨仓 CLI：doctor · clone · status · sync · fetch · pull · push · remotes
├── Makefile          check / release 入口，本地与 CI 共用
├── CHANGELOG.md      变更日志
├── docs/             项目级文档：vision、adr/（架构决策）、specs/（设计规格）、meetings/（纪要）
├── research/         调研：literature/ landscape/ domain/ evals/
├── scripts/          外部脚本与一次性工具 —— 生产代码禁止依赖这里
├── assets/           图、幻灯片；大文件只放索引
└── platform/         内仓（独立 git，被 .gitignore 挡住）
```

## 日常

| 想做什么 | 命令 |
|---|---|
| 看内仓状态 | `./repos status` |
| 拉取全部内仓（只快进） | `./repos pull all` |
| 推送某个内仓（永不 force） | `./repos push platform` |
| 提交前门禁 | `make check` |
| 发版 | `make release VERSION=0.2.0` 然后 `git push origin main --follow-tags` |

## 版本与发布

- 从 0.1.0 起步，0.x 为开发期；正式发布才进入 1.0.0。
- 改动合并时写进 `CHANGELOG.md` 的 Unreleased；`make release` 把它轮转成版本小节并打 tag。
- 推送 `vX.Y.Z` tag 即触发 GitHub Release，Release Notes 直接取自 CHANGELOG 对应小节，0.x 自动标 pre-release。

## 约定

规矩集中在 [`CLAUDE.md`](CLAUDE.md)，能用命令判定的都进了 `make check`。架构决策见 [`docs/adr/`](docs/adr/)。
