# 桌面 App：Tauri 薄包

- 状态：实现中（platform 1.9.0）
- 锚：母 issue [#276](https://github.com/zephyr4123/TJU-AI4Science/issues/276)；叶子 [#282](https://github.com/zephyr4123/TJU-AI4Science/issues/282)（这一份）；摸底时实测出的后端 bug [#283](https://github.com/zephyr4123/TJU-AI4Science/issues/283)（服务不查请求来源）、[#284](https://github.com/zephyr4123/TJU-AI4Science/issues/284)（Windows 后台作业跳不出 Job）、[#285](https://github.com/zephyr4123/TJU-AI4Science/issues/285)（服务退出留孤儿）、[#286](https://github.com/zephyr4123/TJU-AI4Science/issues/286)（家外面的 `~/.codex/tmp`）
- 日期：2026-10-07（主人与 Claude 对齐；动手前四路对抗审查过一遍，改动见 §11）
- 相关：[onboarding.md](onboarding.md)（一行命令安装，桌面第一次打开做的是同一件事）、[windows-adaptation.md](windows-adaptation.md)、[ADR-0005](../adr/0005-desktop-release.md)（桌面包的版本与发版产物）；纲领「界面也是适配器」、P-17

## 0. 一页看完

**为什么做**：一行命令已经能装好平台，但要开终端、要记得下次 `ai4sci serve`。研究者要的是双击一个图标就进页面。

**硬要求**（主人 2026-10-07）：

1. 框架用 **Tauri**（v2）。
2. **薄包**：包里只有外壳和 uv；第一次打开做一行命令安装同样的事，装好 Python 与平台进 `~/.ai4sci`、跑 setup；问 key 挪到页面里的弹窗。后端随 wheel 升级，不重发 App；外壳走 Tauri 自带的更新器。不做把 Python 打进去的胖包。
3. **四种装法都开放、共用一份后端**：源码跑网页版、一行命令装网页版、源码跑桌面 App、安装包装桌面 App。桌面只是在外面套一个窗口，不另起后端。
4. **退出 App**：停服务和正在回复的那一轮，不留孤儿进程；后台实验照跑，跑完自己叫醒助理，下次打开看结果。与网页版关掉终端一致，Mac 与 Windows 一样。
5. **版本**：同一个 tag 出桌面包，版本号与平台一致；只有外壳改过才往已装的人推外壳更新（ADR-0005）。
6. **Mac 出一个通用包**（Apple 芯片与 Intel 共用）；Windows 出按用户安装的 NSIS 安装包。
7. Apple 证书正式对外发布时再配，之前出 ad-hoc 签名的包；Windows 暂无代码签名证书。

**顺序**：后端配合与页面先行（它们让四种装法都受益），外壳与发版流水线并行，最后 Mac 本机、Windows 测试机端到端。

## 1. 用户看到的

```
双击 AAAI4S
┌──────────────────────────────────────────────┐
│                  [三色的 A]                    │
│                    AAAI4S                     │
│        第一次打开：装平台 · 已用 0:41            │
│                                               │
│   ✓ uv            已装，跳过                   │
│   ✓ Python        3.12，下载完成                │
│   ✓ ai4sci        1.9.0，安装完成               │
│   ✓ git           已装，跳过                   │
│   ↓ Claude Code   已下 120 MB / 共 224 MB      │
└──────────────────────────────────────────────┘
装好以后窗口换成平台的页面；助理那家缺 key，就弹：

  ┌ 助理还不能说话 ────────────────────────┐
  │ 填 DeepSeek 的 key（platform.deepseek.com 申请）│
  │ [••••••••••••••••••••]                      │
  │                           [跳过] [试通] │
  └──────────────────────────────────────┘
```

- 以后每次打开：直接起服务进页面，一两秒。平台有新版本就先升级，进度同样画在这一屏。
- 只有「没有能跑的平台」时才停在这一屏：说一句为什么、给「重试」和「打开日志」。git、CLI 没装上照样进页面，设置里的红点说缺什么，下次打开再补装。
- 关窗口：Mac 上只是收起（App 还在 Dock 里，服务照开，点 Dock 图标回来），Cmd+Q 才退出；Windows 上关窗口就是退出。助理这一轮还没回完时，退出前先问一句「退出会打断它」。

## 2. 分层

```
┌──────── 外壳 ui/desktop/（Rust + Tauri）────────┐
│  启动页（本地静态页，只有它能调外壳的命令）          │
│  守进程：首次安装 / 升级 → setup → serve → 退出收拾 │
│  外链交给系统浏览器、下载落「下载」目录、单实例、更新器 │
└──────────────┬────────────────────────────────┘
               │ 起子进程、读输出、读两个 JSON（只认 §3 的约定）
┌──────────────▼──── 后端（同一份 wheel）──────────┐
│  install.sh / install.ps1 → ai4sci setup → ai4sci serve │
│  页面（ui/web 构建，随 wheel 走）从 serve 的地址加载      │
└─────────────────────────────────────────────────┘
```

- 页面不打进外壳：窗口导航到 `http://127.0.0.1:<端口>/`，页面和接口同源，升级 wheel 就连页面一起升了。
- **页面对外壳零权限**：页面是远程来源，Tauri 2.11.1 起远程来源的 IPC 一律过 ACL，我们不给它开任何 capability；只有本地的启动页能调外壳的命令，而且这些命令不收 JS 传来的路径、URL。窗口回到启动页只认外壳自己发起的那一次导航。页面里的 markdown 来自模型输出，不能让它够到外壳。
- 外壳只依赖 §3 列的后端约定，不认识框架内部；这些约定在外壳里集中写在 `src-tauri/src/contract.rs` 一个文件，`make check` 里有一条测试把它与 Python 常量、两份安装脚本、`cdn.py` 对账。

## 3. 外壳与后端的约定

这一张表进外层 CONTRIBUTING 冻结清单的单独一栏「外壳与后端的约定」：**只加不改**，不适用内测期例外（已装的外壳跟不上 wheel）；要改走弃用周期，并抬 `min_desktop`。

| 约定 | 内容 |
|---|---|
| 用哪个 `ai4sci` | 设了 `AI4SCI_DESKTOP_CLI` 就用它（源码桌面：仓里 `.venv` 的 `ai4sci`），不装不升级；否则用家里的 `bin/ai4sci`（Windows `bin\ai4sci.exe`）。家 = `AI4SCI_HOME`，缺省 `~/.ai4sci` |
| 版本写法 | `ai4sci --version` 输出 `ai4sci <版本>`，版本是 PEP 440（rc 写成 `1.9.0rc1`）；tag 与外壳用 SemVer（`1.9.0-rc.1`）。外壳只有一个版本解析函数，两种写法都认；同号的 rc 算满足这个号的下限 |
| 最新是哪一版 | `<DIST>/platform.json` 与 `platform.json.sig`（用更新器那把 key 签，外壳用内置公钥验，验不过当作取不到）：`{"version", "min_desktop", "sha256": {"install.sh", "install.ps1", "wheel"}}`。只在正式版发布时改写。`DIST` = `AI4SCI_DIST`，缺省 `https://media.zephyrxiang.com/ai4science/dist`，release 构建只认 https |
| 装与升级 | 下载带版本号的 `<DIST>/<ver>/install.sh`（Windows `install.ps1`），按签名清单核 sha256 后照跑，环境带 `AI4SCI_NO_SETUP=1` 与 `AI4SCI_WHEEL_SHA256`（脚本用它核 wheel，不再信 CDN 上的 `.sha256`）。Windows：外壳把脚本存成带 UTF-8 BOM 的文件，用 `%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File <路径>` 起；脚本在这种模式下第一句把输出设成 UTF-8。退出码：`0` 装好；`75` 平台还开着（有进程在用家里的平台：网页版服务、后台实验），没动；其余是失败。升级先装进暂存目录（下载都在这一步，旧的那份不动），成了再离线换进去；中途失败或被打断，原来那份照样能用。uv 的 sidecar 所在目录放在 PATH 最前；PATH 上的 uv 低于脚本钉的版本就当没有 |
| setup | `ai4sci setup --no-serve --no-input`：不问 key、不探模型、不开浏览器、不起服务；不认 PATH 上的 Claude Code / Codex，一律装进家里（外壳拿到的 PATH 不稳定）；Mac 没装命令行工具时弹一次苹果的安装框、打 `!`、不算失败（git 只在跑实验时要）。输出一行一项 `  ✓ / ✗ / ! 标签 说明`；不接终端时下载先打 `  … 标签 下载中`、之后每 5 秒 `  ↓ 标签 已下 N MB / 共 M MB`。退出码 `0` 全过，其余是没装好 |
| serve | `ai4sci serve --host 127.0.0.1 --port <N> --until-stdin-closes`；listen 之后 stdout 打且只打一行，以 `ok http://127.0.0.1:<N>` 开头、Tab 分隔的字段只加不改；日志全走 stderr。端口用不了（被占、Windows 的保留端口段）一句话退出，退出码 `3`。标准输入关了、Ctrl-C、SIGTERM 走同一条退出：先停掉在跑的那几轮（`procs` 登记的不脱离的进程树，逐个 `kill_tree`），再退出；后台作业不碰 |
| 在跑什么 | `GET /health` 加 `turns`：此刻在跑的对话轮数（外壳退出前要不要问一句） |
| 版本互相要求 | 外壳写死 `MIN_PLATFORM`，装着的低于它就必须升级；`platform.json` 的 `min_desktop` 是后端要求的最低外壳版本（值在内仓一处常量），外壳低于它就先更新外壳、不升后端 |
| 也冻结 | `bundle.identifier` = `com.zephyrxiang.aaai4s`、更新器公钥、`dist/platform.json`、`dist/<ver>/install.*`、`dist/desktop/latest.json` 这几个路径 |

**外壳给子进程的环境**：在继承的环境上叠加，不清空（Windows 要 `SystemRoot`、`ComSpec`）。

- PATH：外壳实际起的那个 `ai4sci` 所在目录在最前（装好的是家里的 `bin/`，源码桌面是仓里 `.venv` 的 bin）；Mac 上再接用户登录 shell 的 PATH：`$SHELL -ilc` 只打印两个标记之间的 `$PATH`，3 秒超时，取到就记在外壳的配置目录，超时用上次记下的、都没有用系统缺省；原始输出永远不写日志（用户 rc 里常 export 各种 key）。安装时 uv 的 sidecar 目录放最前。
- 设 `PYTHONUTF8=1`、`PYTHONUNBUFFERED=1`、`NO_COLOR=1`、`UV_NO_PROGRESS=1`；Mac 上没有 `LANG` 就设 `en_US.UTF-8`。
- 去掉 `AI4SCI_JOB_ID`、`AI4SCI_CHAT_ID`、`AI4SCI_PROJECT`、`PYTHONHOME`、`PYTHONPATH`、`VIRTUAL_ENV`、`CONDA_PREFIX`。`AI4SCI_HOME`、`AI4SCI_DIST` 原样传下去（测试靠它们隔离）。外壳不记录传给子进程的环境。
- 工作目录用外壳的临时目录（`uv python find` 会读当前目录的 `.venv`）；标准输入一律接管道（Windows 上接 NUL 时 `isatty()` 是真，`getpass` 会卡死）。

## 4. 外壳怎么守进程

**启动**（每次打开）：

1. 单实例：第二次打开只把已有窗口拉到前面。Mac 上 App 从 DMG 里或隔离的只读路径（`/Volumes/`、`AppTranslocation`）跑，就停在启动页：「先把 AAAI4S 拖进『应用程序』再打开」。Windows 上 WebView2 低于 111（页面要的下限）也停在这里，给微软的安装地址。
2. 窗口先显示启动页，显示已用时间。
3. 取签名的 `platform.json`（4 秒超时）。外壳低于 `min_desktop`：先更新外壳，后端不动。
4. 源码桌面直接到第 7 步。
5. 没有能跑的平台（`--version` 跑不通）或低于 `MIN_PLATFORM`：必须装（目标版本：外壳自己是预发布就用自己的版本，否则用 `platform.json` 的；都取不到就停在启动页）。脚本退 75：停在启动页「平台在后台还开着（网页版服务或实验）：关掉网页版服务的窗口，或等实验跑完再点重试」。低于 `platform.json`：照样升级，退 75 或失败就这次不升，照用旧版。
6. 这一版平台还没成功跑过 setup（外壳在配置目录记着哪一版跑通过），就跑一次；没跑通照样往下走，下次打开再跑。
7. 起 serve：端口优先用上次记下的（页面的主题等存在 localStorage，按端口分）；serve 退 3 就让系统给一个空闲端口只用这一次，记下的不改。读到 `ok http://` 那一行（60 秒超时）就把窗口导航过去。
8. serve 起来以后再查外壳更新（签名的 `latest.json`），有就弹系统对话框「桌面 App 有新版本 X：现在更新？」。装、升级的过程中不弹。
9. serve 中途退出：窗口回到启动页显示出错，给「重试」。重试前先收掉上一个 serve 留下的一切（Windows 结束整个 Job 再新建；Mac 由下一个 serve 启动时按 #285 记在盘上的登记清掉死掉的 serve 留下的轮次）。
10. Mac 上收起再点 Dock 回来（`RunEvent::Reopen`），距上次查版本超过一天、又没有在跑的轮次，走一遍第 3–7 步。

**守进程树**：

- 外壳起的每个子进程（安装脚本、setup、`--version`、serve）：Windows 上都放进外壳握着的一个 Job（只设 `KILL_ON_JOB_CLOSE`，不许 breakaway；用 process-wrap 的「挂起、放进 Job、再恢复」，不留竞态），外壳怎么死内核都会关掉句柄、杀掉 Job 里的一切；外壳自己不进这个 Job（更新器拉起的安装器、重启出的新实例会被连带杀掉）。Mac 上各自一个进程组。
- 后台作业怎么活过 App（#284，两个系统都改）：
  - Windows：Git for Windows 的 bash 只要所在 Job 允许 breakaway，就给它起的**每个**子进程都带 `CREATE_BREAKAWAY_FROM_JOB`，所以不能靠 breakaway 区分「后台作业」与「一轮里的普通命令」——打开 breakaway，一轮里的命令、harness 起的 python 都会跳出所有 Job 成孤儿。改成：每棵树的 Job 照旧不许 breakaway；`--detach` 起作业时用 `PROC_THREAD_ATTRIBUTE_PARENT_PROCESS` 把父进程指定成当前会话的 explorer（`GetShellWindow`），作业生来就不在任何 Job 里、不是任何人的后代；作业的日志由作业自己按路径打开（指定父进程后句柄从 explorer 继承，传不过去）。没有 explorer（SSH 会话、服务）就照旧起、打 WARNING。
  - Mac：`--detach` 经一个中间进程起作业、中间进程马上退出，作业生来就归 launchd，不再是那条 `ai4sci cap` 的后代（不然那 20 秒里退出 App，顺后代往下杀会杀到它）。
- 子进程的 stdout、stderr 一直读（不读会把 serve 顶住），写进外壳的日志文件。

**退出**（Mac 的 Cmd+Q 与「退出」菜单、Windows 关窗口、更新器装新版前都走这里；Mac 的「退出」换成自定义菜单项、保留 Cmd+Q，挂在 `RunEvent::Exit` 与更新器的 `on_before_exit` 上）：

1. `GET /health` 的 `turns` 不为 0：先问「助理这一轮还没回完，退出会打断它」，按钮「等它回完」「仍然退出」（只防误触，不改退出语义）。
2. 关掉 serve 的标准输入，serve 自己停掉在跑的轮次后退出；同时收掉还在跑的安装脚本、setup。
3. 5 秒还没退：Windows 结束整个 Job；Mac 趁 serve 还活着先找出它的后代逐个 SIGKILL，再 SIGKILL 整个进程组。
4. 后台作业不受影响。

**外壳替页面做的事**：

- 导航只放行后端来源；`target=_blank`、`window.open` 与导航到别处：只有 `http`、`https`、`mailto` 交给系统浏览器，`file:`、`data:`、`blob:`、`javascript:` 与一切自定义协议直接拒（日志只记协议名）。所以 Windows 上把文件拖进窗口（WebView2 缺省会导航到 `file:`）什么都不会运行。
- 下载落到「下载」目录、下完在访达 / 资源管理器里显示。
- Windows 上关掉 Tauri 自己的拖放处理（不然编辑台的 HTML5 拖放失效）。
- Mac 保留系统菜单的「编辑」（不然 Cmd+V 粘贴不了 key）；`Info.plist` 写桌面、文稿、下载、本地网络四条中文用途说明。
- 正式包不开 devtools、配置里不许出现 `remote-debugging`（门禁查）。

## 5. 后端与页面要配合的

| 改什么 | 为什么 | issue |
|---|---|---|
| 所有请求查 `Host`（主机名只认 `127.0.0.1`、`localhost`，端口不限）；带 `Origin` 就必须等于 `http://` + 这次的 `Host`，`Origin: null` 拒；POST 只收 `application/json`；所有响应 `X-Frame-Options: DENY` 与 `frame-ancestors 'none'`；`/raw` 加 `nosniff` 与 `sandbox` | 任何网页都能对本机服务发简单请求（存 key、清空家、让助理动手），DNS rebinding 能读走对话与文件，页面能被别的网站嵌进去诱导点击。Vite 开发代理、SSH 隧道照常能用 | #283 |
| `procs` 登记不脱离的进程树并记到盘上；serve 退出时逐个收拾，启动时清掉死掉的 serve 留下的；`--until-stdin-closes` | 退出服务会把对话里 CLI 的子孙留成孤儿继续花 token；外壳崩溃、serve 自己崩溃也要能收尾 | #285 |
| Windows：`--detach` 以 explorer 为父进程起作业；Mac：经中间进程起作业 | 后台作业跳不出那一轮的 Job（一轮超时就被连带杀掉）；Mac 上起作业后 20 秒内退出会杀到它 | #284 |
| 凡跑 codex 都带平台的 `CODEX_HOME` | setup 在家外面建了 `~/.codex/tmp` | #286 |
| `setup --no-input`、下载进度行、setup 交给 serve 时用 serve 的 parser | 外壳不能接终端；`make up` 与一行命令最后一步不能因 serve 加参数而断 | #282 |
| 安装脚本：`AI4SCI_NO_SETUP`、`AI4SCI_WHEEL_SHA256`、退出码 75、升级先暂存、uv 版本下限；install.sh 补「平台还开着」；rc 的版本从 wheel 文件名取 | 外壳自己起服务、要分清「被拒」与「失败」；升级中途断网不能把能用的平台弄没；rc 从没走通过 | #282 |
| `dist/platform.json(.sig)`、`dist/<ver>/install.ps1`；`.dmg` `.exe` `.json` 的 Content-Type | 外壳查后端新版本、核安装脚本；下载页不能把安装包当文本发 | #282 |
| 适配器起 CLI 前先查它在不在，不在说一句人话（不再是 500 加英文 errno） | 外壳拿到的 PATH 与终端不一样 | #282 |
| `/settings` 给出助理那家的状态 `ready / needs_key / cannot_talk / unchecked` 与一句原因；页面只在 `needs_key` 时弹「填 DeepSeek 的 key」（`cannot_talk` 只显示原因：余额不足去充值、连不上就是网络），`unchecked` 时页面后台探一次；「跳过」记在页面本地、下一次自检结果出来才再弹；`POST /settings/quickstart {key}` 与 setup 问 key 共用一段代码：存 key、两家都切到 DeepSeek、问一句 | 问 key 从终端挪到页面；不能把算力自检失败、余额不足当成缺 key；一行命令装、回车跳过 key 的人也受益 | #282 |
| 页面：玻璃组件不靠 UA 里的 `Safari` 判断 WebKit；中文输入法用回车选词时不发出 | WKWebView 的 UA 没有 `Safari`；WebKit 选词那次 keydown 的 `isComposing` 是假 | #282 |

## 6. 目录与命令

```
platform/ui/desktop/
  README.md            这一层的规矩
  package.json         @tauri-apps/cli（钉在 package-lock.json）与 dev / check / build 三条脚本（跨平台的真入口）
  scripts/             准备构建输入：从品牌标 SVG 生成图标、放 uv sidecar
  splash/              启动页：index.html + 一个 css + 一个 js，不打包
  src-tauri/
    Cargo.toml  Cargo.lock  build.rs  tauri.conf.json  Info.plist
    capabilities/      只给启动页
    src/               contract.rs（§3 的常量，唯一一处）与守进程、安装、环境、导航各一个模块
    icons/  binaries/  构建时生成，不进 git（P-17）
```

| 命令 | 做什么 |
|---|---|
| `make desktop`（Windows：`npm --prefix ui/desktop run dev`） | 源码跑桌面 App：先 `venv ui-auto`（同 `make up`），后端用仓里 `.venv` 的 `ai4sci`，`identifier` 换成 `….dev`（不与装好的 App 抢单实例与配置目录） |
| `make desktop-check`（`npm --prefix ui/desktop run check`） | 外壳的门禁：准备图标与 sidecar、`cargo fmt --check`、`cargo clippy -D warnings`、`cargo test`（含真起 serve 的集成测试）、查配置里没有 `remote-debugging`；CI 在 Mac 与 Windows 两边跑 |
| `make desktop-build`（`npm --prefix ui/desktop run build`） | 本机出安装包（Mac 上设 `CI=true`，不然打 DMG 时会卡在 Finder 的自动化授权） |

源码桌面在 Windows 上要 Rust（MSVC）与 VS 的 C++ 生成工具，只承诺 dev，不承诺本机打 NSIS（打包工具要从 GitHub 下载）。国内的 Rust 与 crates 镜像写在 `ui/desktop/README.md`，不进仓库配置（CI 在国外）。

## 7. 发版与 CDN

推 `vX.Y.Z` 之后：wheel 那条照旧；并行在 `macos-latest` 出通用包（`--target universal-apple-darwin`，uv 按 `uv.lock` 的版本取两个架构、核 sha256、`lipo` 合成）、在 `windows-latest` 出 NSIS；版本号由 tag 经 `--config` 注入，`tauri.conf.json` 与 `Cargo.toml` 里的只是占位。都好了再统一传 GitHub Release 与 CDN。桌面构建失败不挡 wheel 的发布。

```
ai4science/dist/
  platform.json  platform.json.sig            最新平台版本与安装件的 sha256（签名，短缓存，只在正式版改）
  <ver>/install.ps1                           带版本号的一份（新增，与 install.sh 对齐）
  desktop/
    <ver>/AAAI4S_<ver>_universal.dmg            给人下载
    <ver>/AAAI4S.app.tar.gz(.sig)               Mac 外壳更新
    <ver>/AAAI4S_<ver>_x64-setup.exe(.sig)      给人下载，也是 Windows 外壳更新
    latest.json                               更新器读的清单（短缓存）：只有外壳改过才改写
    AAAI4S.dmg  AAAI4S-setup.exe              固定的下载地址（短缓存、按附件下载，正式版每次都换成最新）
```

- **外壳改没改**：基准是 CDN 上当前 `desktop/latest.json` 的版本（404 才算第一次，别的错误让作业失败），`git diff v<基准> <tag> -- ui/desktop ui/web/public/favicon.svg ':!ui/desktop/README.md'`，路径清单只写在这一处；判定与理由写进作业摘要。
- **重跑不出错**：`desktop/<ver>/` 只写一次；已经在桶里就不再传，`latest.json` 用桶里那份的 `.sig` 生成。不可变对象按 sha256 判断是否已在，同名不同内容让作业失败。`latest.json` 最后传，传之前校验：键齐、每个地址 HEAD 是 200 且长度对、用公钥验签、签名里的版本等于清单的版本（更新器开了 `requireSignedVersion`）。
- rc 只传带版本号的那些，不碰 `platform.json`、`latest.json` 与固定下载地址。
- 发布作业第一步查 CDN 证书剩余天数，少于 30 天就失败（证书 2026-11-22 到期，过期了安装与更新都会断）。
- 更新器的签名密钥：私钥在内仓 secrets（`TAURI_SIGNING_PRIVATE_KEY`、`…_PASSWORD`）并在本机备份；丢了已装的外壳就再也收不到更新。同一把也签 `platform.json`。
- 以后加 Apple 签名与公证只加 secrets（`APPLE_CERTIFICATE` 等），配置结构不动；没有这些 secrets 时照样出 ad-hoc 签名的包。

## 8. 装到哪、卸载

- 平台照旧全在 `~/.ai4sci`，四种装法共用。
- 外壳：Mac 在「应用程序」里；Windows 在 `%LOCALAPPDATA%\AAAI4S`（按用户装，不要管理员）。外壳自己的配置、日志、WebView 缓存在系统给 App 的目录里（标识 `com.zephyrxiang.aaai4s`）。
- 卸载 App 不碰 `~/.ai4sci`（别的装法还在用）；要连平台一起删，照 onboarding 的卸载段。

**没签名时的放行**：Mac 15 起 ad-hoc 签名的 App 第一次打开会被拦，要去「系统设置 → 隐私与安全性」点「仍要打开」（一小时内有效）并输入密码；一定要先拖进「应用程序」。Windows 弹 SmartScreen 时点「更多信息 → 仍要运行」；Win11 开着「智能应用控制」时没有这个选项（平台的 python 也没签名，一行命令同样受影响）。正式对外前先配 Apple 证书与公证。

## 9. 验收

Mac 本机与 Windows 测试机各走一遍，启动都要像用户一样（Mac 从访达或 `open`，环境与 Dock 一致；Windows 从桌面会话），不能从开发的终端里直接起：

1. 干净的家（`AI4SCI_HOME` 指到一个空目录）装包、第一次打开：启动页逐行出进度、有已用时间，装完进页面。
2. 页面弹窗：空 key、错 key 报错；真 key 试通后不再弹；跳过后重开不再弹；算力自检失败不弹；key 不出现在任何日志里（只数出现次数）。
3. 跑一个流程，确认页面渲染（Windows 上就是 WebView2）与中文输入正常；外链在系统浏览器打开；Windows 上把一个 `.bat` 拖进窗口什么都不运行。
4. 起一个后台作业、发一轮对话后退出 App（先确认问了一句）：家目录下除了作业不剩任何进程，端口没人监听；作业跑完记录正确，再打开能续上。Windows 上用 `IsProcessInJob` 看：一轮里经 Git Bash 跑的命令在 Job 里、退出后不在了；后台作业不在任何 Job 里。助理起后台作业后 5 秒内退出，作业照跑。
5. 用过页面后退出，10 秒内重开：一两秒进页面，端口不变，主题还在。
6. 单实例：连开两次只有一个窗口、一个服务；Mac 上关窗口后点 Dock、在「应用程序」里双击，都回到窗口。
7. 后端升级：CDN 测试目录放一个更高版本的 wheel 与签名的 `platform.json`，打开 App 自动升级；升级途中断网，旧平台照样能用。
8. 外壳更新：用测试密钥签两个版本，从旧版更新到新版；改一个字节的包与换一把公钥都被拒。
9. 门禁：`make desktop-check` 在 CI 的 Mac 与 Windows 上都过。

Windows 上只在计划任务那一次启动的环境里设 `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port=…`（不写注册表、只开在回环地址上），用 SSH 隧道接到 Mac，Playwright 直接驱动 App 里的页面（Windows 复盘「SSH 隧道 + Playwright」的延伸），补上 Windows 复盘留下的「浏览器渲染没验」；测完删掉计划任务。

## 10. 这一轮不做

- Apple 证书、公证与 Windows 代码签名（发布时再配）。
- 胖包、App Store、Linux 桌面包。
- 托盘、开机自启、阻止睡眠。
- 代理设置（GUI 拿不到终端里设的 `HTTPS_PROXY`，只影响官方订阅与海外供应商，DeepSeek 不受影响）。
- 本机别的账户也能连 serve（要 token，`ok` 那一行的字段只加不改，留了位置）。
- 卸载 App 时连平台一起删：家是四种装法共用的，删不删要主人定。

## 11. 动手前的对抗审查改了什么

四路（进程与平台机制、安全、研究者的上手路、约定与发版）各自挑错，约 40 条，采纳的都已写进上面各节。改动最大的几条：

- #284 原来的修法（给每棵树的 Job 开 breakaway）是错的：Git for Windows 的 bash 在允许 breakaway 的 Job 里会让每个子进程都跳出去，一轮里的命令、harness 的 python 都会成杀不掉的孤儿。改成以 explorer 为父进程起后台作业（§4）。
- 后端的安装与升级原来没有签名，外壳每次打开都会无人值守地跑 CDN 上可变的脚本，外壳更新的签名形同虚设。改成签名的 `platform.json` 加带版本号的脚本与 sha256（§3）。
- setup 不再探模型、退出码只分「装好 / 没装好」；页面按助理那家的状态弹窗，余额不足、算力自检失败不再被当成缺 key（§3、§5）。
- 「平台还开着」单独一个退出码 75；升级先暂存再换，中途断网不把能用的平台弄没（§3、§4）。
- Mac 关窗口后点 Dock 要处理 `Reopen`；退出前有在跑的轮次先问一句（§4）。
- rc 的版本有 PEP 440 与 SemVer 两种写法，cdn.py 与安装脚本的 rc 一直是坏的，一并修（§3、§5）。
- 外链只放行 `http`、`https`、`mailto`；Windows 拖进窗口的文件不会被运行（§4）。

## 参考

- Tauri v2：[sidecar](https://v2.tauri.app/develop/sidecar/)、[updater](https://v2.tauri.app/plugin/updater/)、[single-instance](https://v2.tauri.app/plugin/single-instance/)、[Windows 安装包](https://v2.tauri.app/distribute/windows-installer/)、[macOS 签名](https://v2.tauri.app/distribute/sign/macos/)、[capabilities](https://v2.tauri.app/security/capabilities/)
- Windows：[Nested Jobs](https://learn.microsoft.com/en-us/windows/win32/procthread/nested-jobs)、[UpdateProcThreadAttribute](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-updateprocthreadattribute)、[Process creation flags](https://learn.microsoft.com/en-us/windows/win32/procthread/process-creation-flags)、[Playwright + WebView2](https://playwright.dev/docs/webview2)
- Git for Windows：[msys2-runtime spawn.cc](https://github.com/git-for-windows/msys2-runtime/blob/main/winsup/cygwin/spawn.cc)（Job 允许 breakaway 时给子进程带 `CREATE_BREAKAWAY_FROM_JOB`）
- Apple：[打开未知开发者的 App](https://support.apple.com/guide/mac-help/open-a-mac-app-from-an-unknown-developer-mh40616/mac)
