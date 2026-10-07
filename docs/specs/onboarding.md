# onboarding：一行命令装好平台

- 状态：实现中（platform 1.8.0）
- 锚：母 issue [#276](https://github.com/zephyr4123/TJU-AI4Science/issues/276)；叶子 [#277](https://github.com/zephyr4123/TJU-AI4Science/issues/277)（onboarding，这一份）、[#210](https://github.com/zephyr4123/TJU-AI4Science/issues/210)（Windows）
- 日期：2026-10-07（主人与 Claude 对齐）
- 相关：[platform-home-and-providers.md](platform-home-and-providers.md)（平台的家、供应商）、[windows-adaptation.md](windows-adaptation.md)

## 0. 一页看完

**为什么做**：1.7 搬家后另一位使用者登不上（#274），暴露的是整条上手路没人设计过。要接的新用户什么工具都没有：没有编译工具、没有 Claude Code 或 Codex，唯一可能会的是去 DeepSeek 后台申请一个 key；官方订阅登录对他太难。

**硬要求**（主人 2026-10-07）：

1. 全程走国内源，不访问外网就能装好、自检。
2. 每一项先查，装过就跳过，不重复装。
3. 尽量不让人在页面上点：Claude Code、Codex 也由命令装好；跑完当场提示粘贴 DeepSeek 的 key。

**做什么**：一行命令，从我们自己的腾讯云 CDN 取安装脚本，装好 uv、Python、平台、Claude Code、Codex，问 key、当场试通、起服务开浏览器。

**顺序**：先做 Mac（这一份），再做 Windows（#210，主人另一台 Windows 机开 OpenSSH 端到端验），再打桌面包（[desktop.md](desktop.md)，#282）。CDN 是三者共用的底：一行命令、DMG、Windows 安装包都从它取同一份东西，上面的装法各自定义。

## 1. 用户看到的

```
$ curl -fsSL https://media.zephyrxiang.com/ai4science/dist/install.sh | sh

AAAI4S 安装（全程国内源）
  ✓ uv            已装，跳过
  ✓ Python 3.12   下载完成
  ✓ 平台 1.8.0     安装完成
  ✓ git           已装，跳过
  ✓ Claude Code   2.1.292，下载完成
  ✓ Codex         0.160.1，下载完成

粘贴 DeepSeek 的 key（platform.deepseek.com 申请，粘贴时不显示；回车跳过）：
  ✓ Claude Code 问了一句，通了

浏览器已打开 http://127.0.0.1:8765
关掉这个窗口服务就停；下次启动：ai4sci serve
```

- key 当场用 Claude Code 问一句（就是 `ai4sci agent check` 的「说话」那一项），CLI、key、供应商三样一起验。没有 key 的直接回车，之后在页面「设置 → AI」里补。
- 已经能用的（官方登录过、或 key 已填）不再问。
- 重跑无害：装好的都跳过，所以它也是修复命令；升级也是同一行（平台换新版本，CLI 低于平台要求的版本才换）。

## 2. 装到哪

都在平台的家里，**只有两样落在外面**：

```
~/.ai4sci/
  bin/ai4sci          唯一进 PATH 的东西（uv 的 tool bin 目录）
  tools/              装出来的程序：清除时留着，卸载时一起删
    uv/               我们装的 uv（用户已有就用他的，这里空着）
    python/           uv 装的 Python（UV_PYTHON_INSTALL_DIR）
    ai4sci/           平台本体的环境（UV_TOOL_DIR）
    claude_code/      Claude Code 的原生程序
    codex/            Codex 的原生程序与它带的 rg
  agents.yaml keys.yaml computes.yaml projects/ studio/ claude_code/ codex/ cache/uv/   （已有，见家的 spec）
```

落在外面的两样：

1. **shell 配置里一行 PATH**（`~/.zshrc` 或 `~/.bashrc`，带 `# ai4sci` 注释，有了不重复加）：没有它终端里敲不到 `ai4sci`。
2. **git**：跑实验的硬依赖（`framework/experiment/gitwork.py`）。Mac 上是系统组件（Xcode 命令行工具），缺了由 `xcode-select --install` 弹苹果的安装框，从苹果的 CDN 下，国内能下；装不进我们的目录。

用户自己已经装过的 uv、Python（≥3.12）、claude / codex（版本够平台要求），直接用他的，不装第二份。平台起 CLI 时先找家里 `tools/` 下的，没有再找 PATH 上的。

**清除与卸载分开**：`ai4sci reset`（设置页「清除全部数据」）回到「刚装好的样子」，所以留 `bin/` 与 `tools/`、删别的；卸载是删整个 `~/.ai4sci` 再删那一行 PATH，README 写这一句。

以前用 `uv tool install` 装在 uv 缺省位置（`~/.local/bin/ai4sci`）的，一行命令会先把它卸掉再装进家里，不然终端里会有两份 `ai4sci`（#274 的坑）。

## 3. 从哪下

| 东西 | 源 | 装过的判据 |
|---|---|---|
| 安装脚本、平台的 wheel、uv | 我们的 CDN `media.zephyrxiang.com/ai4science/dist/` | uv：PATH 上有；平台：`ai4sci --version` 已是这一版 |
| Python | npmmirror 的 python-build-standalone（`UV_PYTHON_INSTALL_MIRROR`） | 有 ≥3.12 的解释器 |
| 平台的 Python 依赖、skill 与实验环境的依赖 | 清华 PyPI（`UV_DEFAULT_INDEX`） | uv 自己的缓存 |
| Claude Code、Codex | npmmirror 上按平台分的原生程序包，校验 npm 元数据里的 sha512 | 版本 ≥ 适配器的 `MIN_VERSION` |
| HuggingFace 上的数据与模型 | hf-mirror（`HF_ENDPOINT`） | — |
| git（Mac） | 苹果（`xcode-select --install`） | `xcode-select -p` 成功 |

2026-10-07 实测：

- npmmirror 上 Claude Code 2.1.292、Codex 0.160.1 与 npmjs 同版本。两家都是按平台分的原生程序包（Claude Code：`@anthropic-ai/claude-code-<平台>`；Codex：`@openai/codex@<版本>-<平台>`），下 tgz 解出来 `--version` 能跑，**不要 Node**。Claude Code 的 npm 安装脚本只是从平台子包里拷出程序，不出网。
- Mac M 芯片下载：Claude Code 103 MB / 28 s，Codex 134 MB / 41 s。
- Codex 的程序包里还有 `codex-path/rg` 与 `codex-resources/`，按 `codex-package.json` 的布局原样放，程序按自己的位置找它们。
- npmmirror 有 python-build-standalone（最新 20261003）；清华 PyPI 有 uv；npmmirror 没有 uv 的二进制目录，所以 uv 放我们自己的 CDN。
- Windows 的两家程序包（x64、arm64）也在 npmmirror 上：Windows 的槽位就是平台名那一段。

**Claude Code 不放我们的 CDN**：闭源许可，不能转发，只能让用户从公共镜像拿。Codex（Apache-2.0）可以放，但没必要，两家走同一条路。

## 4. 分层

```
install.sh（Mac / Linux）     install.ps1（Windows，#210 的槽位）
   只做两件事：装 uv → 装平台 → 交给 ai4sci setup
                 │
         ai4sci setup（Python，一份，能测）
   查 git → 装 Claude Code / Codex → 问 key → 试通 → 起服务开浏览器
                 ▲                    ▲
          make up（源码跑的）      桌面 App 第一次打开（desktop.md）
```

- **脚本越薄越好**：脚本要按系统写两份，只放 Python 还没有时非做不可的事；其余都在 `ai4sci setup` 里，Mac、Windows、源码、桌面 App 共用。
- **按系统分的只有一处**：CLI 的平台名（`darwin-arm64`、`win32-x64`……）与 git 怎么补。Windows 上 git 从 npmmirror 的 git-for-windows 取，那一段这一轮先明确报「Windows 还没做（#210）」，不静默。
- **CLI 的包名与布局归适配器**：`backends/claude_code.py`、`backends/codex.py` 各自声明 npm 上的包名、程序在包里的位置、要不要带上整个目录；下载、校验、解包是框架的一份通用代码。平台起 CLI 用哪一份程序（家里的或 PATH 上的）由框架定，交给适配器（`Link`）。
- **`make up`** 的最后一步从「`ai4sci check` + `ai4sci serve`」换成 `ai4sci setup`，开发者装好的东西都跳过。

## 5. CDN 上放什么

桶 `zephyr-media`、域 `media.zephyrxiang.com`（已有，素材也在这），前缀 `ai4science/dist/`：

```
ai4science/dist/
  install.sh                       永远是最新版（版本号在发版时写进去）；短缓存，发版时刷新
  install.ps1                      Windows 的槽位
  <版本>/install.sh                钉版本装
  <版本>/ai4sci-<版本>-py3-none-any.whl  + .sha256      不可变、长缓存
  uv/<uv 版本>/uv-<平台>.tar.gz     uv 官方发布包的原样副本（Windows 是 .zip）
```

- **发版流水线顺手传**：内仓 `release.yml` 出完 wheel 后跑 `.github/scripts/cdn.py` 把上面这些传上去、刷新 `install.sh` 的缓存；`--prefix` 可以先传到测试目录真验。凭据是只能写这个前缀、只能刷这个域名缓存的 CAM 子账号，密钥只在内仓 GitHub Actions secrets（主人 2026-10-07 定；建好当场正反例验过：写 `dist/` 成功、写别的前缀被拒）。
- **referer 白名单**已允许空 referer，`curl` 能下（上线前匿名 HEAD 验一次）。
- **证书 2026-11-22 到期**（免费证 90 天）：到期一行命令就断，这一轮把续期写进待办，之后再看要不要自动化。

## 6. 平台跑起来以后也走国内源

一行命令装完，平台自己起的 uv（skill 脚本、实验环境）以前直连 pypi.org（只有 ssh 远端配了镜像，`compute/ssh.py`）。这一轮统一：

- 镜像地址只在一处（`framework/mirrors.py`）；`install.sh` 里那几个地址由测试对账，不一致就红。
- 平台起 uv 时带上 `UV_DEFAULT_INDEX`、`UV_PYTHON_INSTALL_MIRROR`、`UV_PYTHON_INSTALL_DIR`、`HF_ENDPOINT`；用户 shell 里自己设了的，用他的。
- 平台起 Claude Code 一律关自动更新（`DISABLE_AUTOUPDATER=1`）：它会去国外的存储桶取新版本；版本由 `ai4sci setup` 管。
- **skill 的锁文件对着清华锁**：uv 照锁文件装依赖时用锁文件里写的地址（原来是 `files.pythonhosted.org/...`），不看 `UV_DEFAULT_INDEX`，uv 0.12.18 也没有换地址的开关（2026-10-07 查二进制与文档）。清华的路径与 pythonhosted 一一对应（`/pypi/web/packages/<同一段>`），所以 149 份锁文件只换前缀，包名、版本、哈希一字不改（主人 2026-10-07：「改，全面调整」）；门禁（`make skills`）查锁文件里不许出现官方 PyPI 的地址，新锁照 `docs/add-a-skill.md` 对着清华锁。一次性脚本 `scripts/oneoff/relock-to-tuna-277.py`。代价：国外的人（CI、海外用户）也从清华下；清华同步有延迟，刚发布的包要等一会儿才能锁。

## 7. 验收

1. **干净的 Mac**：先在本机用临时 `HOME`、只含系统目录的 `PATH` 模拟什么都没装，粘一行命令，一路只粘 key，浏览器打开，在项目里跟助理说一句话，助理回了；主人再在一个新建的 macOS 账号上验一次。全程不开代理。
2. **重跑**：同一台机器再跑一次，每一项都是「已装，跳过」，不问 key，直接起服务。
3. **已有 1.7.2 的机器**：一行命令把 `~/.local/bin/ai4sci` 换成家里那份，`which ai4sci` 只剩一份，设置与项目原样在。
4. **清除**：`ai4sci reset` 后 `ai4sci` 与两家 CLI 还在，再跑一行命令只问 key。
5. **门禁**：`make check` 绿；下载、校验、解包、跳过的判据、PATH 那一行的写法都有单测（不连网：拿本地造的 tgz 和假的元数据）。
6. **文档**：两个仓 README 的「只用」改成这一行命令，「升级」「卸载」各一句；CHANGELOG。

## 8. 这一轮不做

- Windows 的 `install.ps1` 实现与 Windows 上的 git：#210，Mac 这一轮做完接着做。
- 桌面 App：另一份 spec [desktop.md](desktop.md)（#282）。
- 发到 PyPI：主人 2026-10-07 定放自己的 CDN，PyPI 不发。
- 官方订阅登录的引导：要外网，不在默认路径上；`ai4sci agent login <家>` 照旧。
