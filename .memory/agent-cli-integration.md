---
name: agent-cli-integration
description: 接 Claude Code / Codex 这类 coding agent CLI 时实测出来的硬知识：隔离、key、续接、联网、成本、Windows
metadata:
  node_type: memory
  type: project
  originSessionId: ecc4450e-06d2-447c-a0b1-2ca7efce5ea9
  modified: 2026-10-12T03:04:43.829Z
---

平台不自研 agent，两层都起现成 CLI 的子进程；可替换性靠端口 + 一家一个适配器文件。接一家新 CLI 只信官方文档，并先 spike 六件事：隔离位、权限与可写目录、命令放行、联网工具放行、事件流逐字、续接与成本上报。

最容易出错、已经实测过的几条（细节与版本号在 `platform/backends/claude_code.py`、`codex.py` 的文件头）：
- **隔离的承重位**：Claude Code 靠 `--setting-sources ""`（不带时项目 CLAUDE.md、插件、hook 全进来，一句 pong 贵 9 倍；`--bare` 会读不到钥匙串，不能用）；Codex 靠私有 `CODEX_HOME`，平台把里面的 `config.toml` 写成空文件，不用 `--ignore-user-config`（它连 `-p` profile 也一起不读）。两家的个人 skill、自动记忆都要另外显式关掉。
- **key 不进环境变量**：两家的 Bash 工具都会把环境继承给 agent 跑的命令，agent 看得见 key。Claude Code 改走私有目录里 0600 的文件 + `apiKeyHelper`（Windows 上 CLI 用 cmd.exe 跑它，命令得写成 `type`）；Codex 用 `shell_environment_policy.exclude` 把 key 挡掉。
- **续接时新指南不生效**：Claude Code 的 `--resume` 沿用开会话时那份 `--append-system-prompt`，Codex 的 resume 也不再读 `developer_instructions`。所以指南只在开会话时送，中途变了由框架把变了的几节塞进那一轮的话里。
- **联网搜索在供应商服务端跑**：按「CLI × 供应商」逐格登记，不设缺省值。Codex 接 DeepSeek 搜不了（DeepSeek 的 Responses API 忽略内置工具），照实关掉，设置里标「不能联网」，只提醒不拦。
- **成本**：订阅账号报不出美元，记 NaN（绝不写 0），读的时候按 `backends/catalog/prices.json`（从 cc-switch 同步）折算；第三方模型在 Claude Code 里报的美元是按缺省价乱算的。
- **命令行长度**：正文一律从 stdin 喂，因为 Windows 一条命令行最多 32767 个字符。Codex 的 stdin 不关会一直等下去。
- **放行**：协调层只放行 `ai4sci` 前缀，执行层只放行 `ai4sci skill`；Codex 用 execpolicy 规则让 `ai4sci` 在沙箱外跑，因为嵌套的沙箱走不通。

开发与测试一律用 Claude Code + DeepSeek（便宜，也是目标用户最可能的组合），不用订阅。

**Why:** 这些都是花钱、花时间实测出来的，而且多数和直觉相反；新会话重新探一遍代价很高。
**How to apply:** 改适配器、升级 CLI 版本、接新供应商时，先读适配器文件头，改完用 `AI4SCI_LIVE=1` 冒烟；新发现写回文件头，不写进这条记忆。相关：[[tech-stack]] [[drill-lessons]]
