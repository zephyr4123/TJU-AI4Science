# ADR-0005：桌面包的版本线与发版产物

- 状态：已采纳
- 日期：2026-10-07（主人定）
- 补充 [ADR-0004](0004-branching-versioning-1.0.md)；spec 在 [`../specs/desktop.md`](../specs/desktop.md)，锚 [#282](https://github.com/zephyr4123/TJU-AI4Science/issues/282)

## 背景

桌面 App 是 Tauri 薄包：包里只有外壳和 uv，平台本体照旧是 wheel，装进 `~/.ai4sci`。于是一次发版有两样东西要发、两条升级路：后端随 wheel 升级（外壳每次打开查 `platform.json`），外壳走 Tauri 的更新器（读 `desktop/latest.json`）。现在一天能发好几个版本（10-06 到 10-07 发了 1.6.1 到 1.8.0 五版），外壳的代码却很少动。

## 选项

- A. 每个 tag 都出外壳、都推更新：最简单，已装的人一天被提示好几次内容一样的更新，Windows 上每次还要重跑安装器。
- B. 外壳单独一条版本线（`desktop-vX.Y.Z`）：要改 `release.sh` 与 `changelog.sh`、多一套 CHANGELOG，碰外层红线 5「发版只走 `make release`」。
- C. 同一条版本线、同一个 tag，外壳只在改过时才推给已装的人。

## 决定

选 C。

- **每个 tag 都出桌面包**，版本号就是 tag（`tauri.conf.json`、`Cargo.toml` 里的版本只是占位，构建时注入），附到 GitHub Release、传到 CDN 的 `desktop/<ver>/`，新下载的人拿到的就是这个号。
- **只有外壳改过才改写 `desktop/latest.json`**：和 CDN 上当前 `latest.json` 的版本比，`ui/desktop`（不含 README）与品牌标 SVG 有改动才改写。判定写在发版脚本的一处，结果进作业摘要。已装的外壳版本比 `latest.json` 高时更新器不会降级。
- **后端照旧随 wheel 升级**：`platform.json`（签名）只在正式版改写。
- **两边互相声明最低版本**：外壳写死它要求的最低平台版本；`platform.json` 带后端要求的最低外壳版本 `min_desktop`，外壳低于它就先更新外壳、不升后端。
- **外壳与后端之间的约定单独冻结**（`CONTRIBUTING.md`「版本与发布」）：只加不改，不适用内测期例外——已装的外壳跟不上 wheel，改了就是让一批人打不开 App。要改走弃用周期并抬 `min_desktop`。
- rc 只传带版本号的产物，不碰 `platform.json`、`latest.json` 与固定下载地址。
- 桌面构建失败不挡 wheel 的发布。

## 后果

- 不加新 tag、不加新 CHANGELOG，ADR-0004 的结构不变；外壳的改动与平台的改动写在同一份 CHANGELOG 里。
- 已装的人看到的外壳版本号会落后于平台版本号，页面与「关于」里两个版本都显示。
- 更新器的签名私钥（也签 `platform.json`）一旦丢失，已装的外壳再也收不到更新；它在内仓 secrets 里，并在主人本机备份。`bundle.identifier`、更新器公钥、CDN 上这几个路径一经发出也就冻结了。
