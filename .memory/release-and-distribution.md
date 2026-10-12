---
name: release-and-distribution
description: 两仓怎么发版、产物发到哪、发版流水线的硬约束与有时效的风险（CDN 证书到期、签名私钥）
metadata:
  node_type: memory
  type: project
  originSessionId: ecc4450e-06d2-447c-a0b1-2ca7efce5ea9
  modified: 2026-10-12T07:02:08.141Z
---

- **两条版本线**：内仓 tag 是产品版本，出 wheel 与桌面包；外层 tag 是文档版本，只出 Release Notes，大版本同日对齐。官网 `site/` 独立发版，版本号运行时从 CDN 读，产品发版不用改网站。
- **分支**：`main` ← `release/X.Y` ← `feat/<issue>-<slug>`，只用 merge commit；rc 在 `release/X.Y` 上打（`make release VERSION=X.Y.Z-rc.N`，不轮转 CHANGELOG）。`make release` 只在本地做事，不推送；推送 tag 才触发流水线。
- **内测期例外**（2026-10-01 起，主人宣布结束前有效）：冻结的契约不兼容地变了也走 MINOR、不留兼容层，但 CHANGELOG 要写迁移办法，受影响的数据要带一次性迁移脚本（`scripts/oneoff/`）。**桌面外壳与后端的约定不适用这个例外**：只加不改，要改就抬 `min_desktop`。
- **产物**：腾讯云 COS + CDN `media.zephyrxiang.com/ai4science/dist/`。wheel 与两份安装脚本、签名的 `platform.json`（只在正式版改写）、`desktop/<ver>/` 下的包；外壳改过才改写 `desktop/latest.json`（ADR-0005）。rc 只传带版本号的产物。
- **流水线的硬约束**：每个 publish 作业都能直接 Re-run（不可变对象按 sha256 判断，最新的那几份不往回换）；美国的 runner 往上海的桶传要走 COS 全球加速域名；桌面构建失败不挡 wheel 的发布。
- **有时效的风险**：CDN 证书 **2026-11-22 到期**（2026-10-11 用 openssl 查过，还没续），发布作业在证书剩余不足 30 天时直接失败（`.github/scripts/cdn.py` 的 `CERT_DAYS`），也就是 **2026-10-23 起发不了版**，要在那之前续证书（续证可以用 `zephyr-cloud-cli-ops` 那一套做）。主人 2026-10-11 定：这件事只在记忆里跟，不单开 issue；续完把这一条删掉。更新器签名私钥（`TAURI_SIGNING_*`，也签 `platform.json`）在内仓 secrets，仓外另有一份备份，丢了已装的外壳就再也收不到更新。

**Why:** 发版是一天多次的高频动作，流水线踩过的坑（分片失败、签名时间戳、rc 的 PEP 440 版本号）都已固化成规则；证书到期是唯一会突然卡死发版的已知风险。
**How to apply:** 发版前看证书剩余天数；改外壳与后端的约定前读 `docs/specs/desktop.md` §3 与 ADR-0005；推送 tag 前要问主人。细节：`CONTRIBUTING.md`「版本与发布」、`docs/specs/desktop.md` §7。相关：[[tech-stack]] [[project-status]]
