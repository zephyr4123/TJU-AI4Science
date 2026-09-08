# ADR-0002：版本、变更日志与发布流水线

- 状态：已采纳
- 日期：2026-09-08

## 背景

项目从第一天起就要有版本控制日志的思维，并且打 tag 就能直接出包，不靠人手工发布。技术栈尚未确定，所以流水线不能绑定任何语言工具链。

## 决定

- **版本号**：语义化版本，从 0.1.0 起步；0.x 为开发期不承诺兼容，正式发布才进入 1.0.0。tag 形如 `vX.Y.Z`。
- **变更日志**：Keep a Changelog 格式的 `CHANGELOG.md`；改动合并时写进 Unreleased。`CHANGELOG.md` 是版本的唯一真相源，没有单独的 VERSION 文件。
- **发版动作**：`make release VERSION=x.y.z` 轮转 Unreleased、提交、打 annotated tag；不自动 push。
- **流水线**：推送 tag 触发 `release.yml`：校验 tag 与 CHANGELOG 最新版本一致 → 取该版本小节做 Release Notes → 出包 → 建 GitHub Release，0.x 标 pre-release。
- **出包**：内仓 `make package` 产出 `dist/<name>-<ver>.tar.gz` 与 sha256；技术栈确定后，构建命令只需接进这一个目标。
- **门禁**：`make check` 本地与 CI 同一套；CHANGELOG 格式由脚本判定，零依赖（bash / grep / sed / awk）。

## 后果

- 忘写 CHANGELOG 不会在 PR 阶段被拦（目前只校验格式与 tag 一致性）；团队变大后可加"PR 必须触碰 CHANGELOG"门禁。
- 外仓与内仓各自独立版本，互不绑定。
