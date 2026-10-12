---
name: tech-stack
description: 三个仓各用什么技术、为什么这么选、改动时最容易踩的约束（后端、页面、桌面外壳、官网、发版与分发）
metadata:
  node_type: memory
  type: project
  originSessionId: ecc4450e-06d2-447c-a0b1-2ca7efce5ea9
  modified: 2026-10-12T03:02:47.862Z
---

**后端 `platform/`（Python 包 `ai4sci`）**：Python ≥3.12（本机与 CI 3.14），运行时依赖只有 pyyaml、jsonschema、uv、ruff。HTTP 用标准库 `ThreadingHTTPServer` + 手写 SSE，CLI 用 argparse 逐行装配，不引 web 框架、不用注册表。uv 管一切（`uv.lock`、PEP 735 dev 组、skill 脚本 PEP 723 + `uv run --locked`、课题按 `materials/env/` 每次实验自建 venv）。ruff 带 BLE 规则（不吞异常的机器判据）。pytest 用剧本后端（`tests/fixtures/scripted_backend.py`）代替 mock 模型。setuptools-scm 从 tag 取版本。
- 模型只在 `backends/` 起的 CLI 子进程里：Claude Code（≥2.1.276，`--setting-sources ""` 是隔离的承重位）、Codex（≥0.160，私有 `CODEX_HOME` 隔离）。实测坑只记在各自适配器的文件头。
- 进程树 `procs/`：POSIX 进程组，Windows Job Object；后台作业要脱离起它的那一轮（Windows 借 explorer 当父进程）。

**页面 `platform/ui/web/`**：React 19 + TypeScript strict + Vite，Tailwind v4（CSS-first，tokens 在 `src/index.css`），shadcn（radix-nova），Phosphor 图标，motion，`@xyflow/react`（只在编辑台画布），oxlint + vitest。刻意不用路由、全局状态、tanstack-query、axios。前后端契约靠 `boards.py` ↔ `api/types.ts` 注释同步（已知盲点）。

**桌面外壳 `platform/ui/desktop/`**：Tauri 2（Rust），只是给页面套的窗口，与后端之间只认 `contract.rs` 里冻结的约定（只加不改，不适用内测期例外）。Mac 通用包签名 + 公证，Windows NSIS 按用户装。

**官网 `site/`**：Next.js 16 静态导出 + Tailwind v4（写代码前先看 `node_modules/next/dist/docs/`，API 与训练数据不同），FastAPI 问答（OpenAI 兼容接口、SSE），Docker Compose 与个人网站共用一台服务器，`./ops/site` 经 SSH 推代码部署，服务器不连 GitHub。

**分发**：腾讯云 COS + CDN `media.zephyrxiang.com/ai4science/dist/`（wheel、安装脚本、桌面包、签名的 `platform.json`）；GitHub Actions 的美国 runner 往上海的桶传要走 COS 全球加速域名。全程国内源：清华 PyPI、npmmirror（两家 CLI 的原生程序、Python、Git for Windows 便携版）、hf-mirror。

**Why:** 选型都是围着「单人本机服务 + 非工程师用户 + 国内网络」定的；不知道这些约束就会顺手引一个 web 框架、一个路由库，或从国外源下东西。
**How to apply:** 加依赖先说清标准库为什么不够并过四看；页面依赖照「不引入的库」清单；碰 Next.js 16 先读本地文档；任何下载路径默认走国内镜像（`framework/mirrors.py` 是唯一出处）。细节：`platform/framework/README.md` §2、`platform/ui/README.md` §2、`platform/ui/desktop/README.md`、`site/CLAUDE.md`。相关：[[architecture-model]] [[release-and-distribution]]
