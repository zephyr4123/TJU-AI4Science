---
title: Windows 适配复盘：一个下午，从开 SSH 到真机端到端
subtitle: Mac 上的 agent 经 SSH 远程操作一台 Windows 11，把平台从「只在 macOS / Linux 上跑」做到原生支持 Windows；用 SSH 隧道加 Playwright 在 Mac 的浏览器里替 Windows 用户点完一整条研究流
kind: 工程复盘
date: 2026-10-07
scope: 平台 1.8.0 的 Windows 适配（issue #210）与 Windows 上的一行命令安装（#277）。真机是一台 Windows 11 专业版 26200（AMD64、PowerShell 5.1、系统代码页 936、执行策略 Restricted、长路径没开）；agent 是 Mac 上的 Claude Code。文中的 IP、账号、机器名都换成了占位符
status: 已完成，随 1.8.0 发布
---

> **结果**：一个下午（约 13:20 开始开 SSH，16:40 端到端走完），平台从「只在 macOS / Linux 上跑」做到在 Windows 上原生能用。
>
> - 内仓全量 pytest 在真机上从 **546 过 / 152 失败 / 24 报错**做到 **747 过 / 0 失败**，和 Mac 上的数一样。
> - 一行命令 `irm …/install.ps1 | iex` 33 秒装好平台、问 DeepSeek 的 key、当场试通、起服务。
> - 在页面上走完出厂的 `research` 流：设计 → 签核对 → 3 轮实验 → 分析 → 数字核对 PASS → 签验收。
> - 停作业时整棵进程树清干净；重启服务后状态都显示对。
>
> 单元测试全绿之后，端到端又撞出 6 个问题，其中 2 个 Mac 上也有、已经在发布的包里存在了很久。GitHub 的 Windows runner 第一次跑全量，又撞出 2 个，其中一个是 key 文件管理员也能读。
>
> 做法上有三件事值得带走：
> 1. agent 经 SSH 直接操作真机，一个下午做完原本打算交给另一位工程师的活。
> 2. 先拿真机全量基线、按根因归类，再按类修。
> 3. 用 SSH 隧道把 Windows 上的服务接到 Mac 的浏览器，agent 用 Playwright 替用户点页面，请求全部落在 Windows 上。

## 1. 在 Windows 上开 SSH

目标是让 Mac 上的 agent 用密钥免密登录 Windows，跑任意 PowerShell 命令、传文件。人在 Windows 上要做的只有前四步，其余都在 Mac 上。

### 1.1 装 OpenSSH 服务端

Windows 10 / 11 自带 OpenSSH 服务端，只是默认没装。管理员 PowerShell 里：

```powershell
# 走 Windows 更新下载，等几分钟，显示 Online : True 就是装好了
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
# 起服务、开机自启
Start-Service sshd; Set-Service sshd -StartupType Automatic
# 确认 Running，记下用户名与 IP
Get-Service sshd; whoami; ipconfig | findstr IPv4
```

- 第一条要从微软的服务器下载，网络连不上时会卡住或报错。这次是先开 VPN 再装的。
- 命令装不上时走图形界面：设置 → 系统 → 可选功能 → 添加功能 → 搜「OpenSSH 服务器」。
- 账号没设密码的，Windows 不许空密码远程登录，先 `net user <用户名> <新密码>` 设一个，放公钥那一步要用一次。

### 1.2 放公钥：管理员账号放的地方不一样

Mac 上给这台机器单独生成一把钥匙（`ssh-keygen -t ed25519 -f ~/.ssh/<钥匙名>`），把公钥放到 Windows 上。**第一个坑**：账号在管理员组里时，sshd 只认 `C:\ProgramData\ssh\administrators_authorized_keys`，放在用户目录的 `~\.ssh\authorized_keys` 不生效，会一直要密码。这个文件还必须只有管理员组和 SYSTEM 能写，权限宽了 sshd 也不认。

我们写了一个小脚本，从 Mac 上一次做完：用密码登录一次、判断账号是不是管理员、把公钥写到对的地方并收紧权限、再用钥匙登录验一次。全文见[附录 A](#a-放公钥-push-keysh)。人在 Mac 的终端里跑 `sh push-key.sh <用户名>@<Windows 的 IP>`，输一次 Windows 的登录密码（微软账户就是微软账户的密码，不是 PIN）。

### 1.3 防火墙：网络被标成「公用」

钥匙放好以后连接超时。ping 两边都通，22 端口不通：Windows 把这根网线所在的网络标成了「公用」，装 OpenSSH 时自带的放行规则只在「专用」网络下生效。不改网络类型，单加一条只放行 Mac 所在网段的规则：

```powershell
New-NetFirewallRule -Name ai4sci-ssh -DisplayName "SSH from Mac" -Direction Inbound -Protocol TCP `
  -LocalPort 22 -Action Allow -Profile Any -RemoteAddress <Mac 所在网段，如 192.168.1.0/24>
```

用完删掉：`Remove-NetFirewallRule -Name ai4sci-ssh`。

### 1.4 Mac 开着 VPN 时：指定从哪块网卡出去

Mac 开着 VPN 时，默认路由走 VPN 的 utun 接口，发往 Windows 的包被 VPN 吞掉。两台机器在同一个局域网里（一台网线、一台 Wi-Fi，两个网段互通），所以让 ssh 绑定 Wi-Fi 网卡直接出去，VPN 不用关：

```sh
ssh -o BindInterface=en0 -i ~/.ssh/<钥匙名> -o IdentitiesOnly=yes <用户名>@<Windows 的 IP>
```

`en0` 是 Mac 的 Wi-Fi 网卡名（`networksetup -listallhardwareports` 查）。之后每一条 ssh、scp 都带上 `BindInterface`。

### 1.5 远端命令：cmd、GBK 与 `-EncodedCommand`

登进去的默认 shell 是 cmd，控制台代码页是 936（GBK）。直接把 PowerShell 命令拼进 ssh，会撞上三个问题：

- 引号要过三层：Mac 的 shell、cmd、PowerShell，哪层吃掉一个都会出错。
- 中文输出按 GBK 编码，Mac 上按 UTF-8 读是乱码。
- PowerShell 的错误流在输出被重定向时会序列化成 CLIXML（一大段 XML）。

解法是把整段 PowerShell 编成 UTF-16LE 的 base64，用 `powershell -EncodedCommand` 交过去：一个字符都不用转义。开头把输出编码设成 UTF-8，错误记录转成纯文本。这就是[附录 B](#b-远端跑一段-powershell-winsh) 的 `win.sh`，之后所有远端操作都经过它：

```sh
sh win.sh 'Get-Process | Where-Object Path -like "$HOME\.ai4sci\*"'
sh win.sh - < script.ps1
```

执行策略是 Restricted，`.ps1` 文件不能直接跑。要跑放在远端的脚本，就读成字符串再建脚本块：`& ([scriptblock]::Create((Get-Content -Raw -Encoding UTF8 <文件>)))`。

### 1.6 用完收尾

- 删防火墙规则：`Remove-NetFirewallRule -Name ai4sci-ssh`。
- 删公钥：编辑 `administrators_authorized_keys`。
- 不再用 SSH 就停服务：`Stop-Service sshd; Set-Service sshd -StartupType Disabled`。

这次的选择是：SSH 与防火墙规则留着（以后还要连），测试用的东西全部清掉，见 [3.5](#35-收尾)。

## 2. 端口通了以后：怎么做适配

### 2.1 先拿真机全量基线，按根因归类

第一件事不是改代码，是把内仓原样同步过去、在真机上跑全量 pytest，拿到一份失败清单：**546 过、152 失败、24 报错、7 跳**（227 秒）。按失败的原因归类：

| 原因 | 条数 | 对应改动 |
|---|---|---|
| 实验环境的解释器写死成 `bin/python`，Windows 上是 `Scripts\python.exe` | 约 110 | 解释器路径 |
| 子进程输出按 GBK 解码（`UnicodeDecodeError: 'gbk'`） | 约 25 | 编码 |
| `os.getpgid` 在 Windows 上不存在 | 6 | 进程树 |
| 测试里的假 CLI 是 shell 脚本（`%1 不是有效的 Win32 应用程序`）、权限位、`os.uname` 等 | 余下 | 测试夹具与权限 |

还有一条清单里看不出来、但最要紧的：杀进程树的测试在 Windows 上留下了孤儿进程 `sleep 300`。也就是说，「停止作业」在 Windows 上停不干净。

152 条失败看着多，归完类只有四五种根因，修一种就绿一大片。照着这张表定顺序：编码 → 解释器路径 → 进程（存活、杀树、脱离）→ 命令行长度 → 两家 agent CLI → bash、换行、rsync 等其余 → 一行命令安装 → CI 加 Windows 作业 → 真机端到端。

### 2.2 每条差异：先写会失败的测试，两边都跑

规矩只有一条：每个改动先写一条会失败的测试，在 Windows 上亲眼看它红，再改到绿；**同一份测试在 Mac 上也要绿**，不许为 Windows 另起一套。做法上分三类：

- **能在 Mac 上复现的**，在 Mac 上先红。比如换行符：测试里开着 `core.autocrlf` 的全局配置，Mac 上就能复现。
- **只有 Windows 才有的**，在真机上先红。比如进程树、ACL、PowerShell。
- **机器能查的规矩进门禁**，每个检查器带一条反例，证明它抓得到：
  - 用 ast 扫全仓所有文本模式的子进程调用和文件读写，没写 `encoding` 的就不过；
  - 扫框架里所有 `python -m <模块>`，每个模块都必须在运行时依赖里；
  - 扫 `install.ps1` 里只差大小写的变量名。

### 2.3 一个循环：同步、跑、拉日志

三个小脚本组成一次循环，全文见[附录 B–D](#b-远端跑一段-powershell-winsh)：

| 脚本 | 做什么 |
|---|---|
| `win.sh` | 在 Windows 上跑一段 PowerShell，输出按 UTF-8 拿回来 |
| `wsync.sh` | 把内仓工作区（含没提交的改动）打成 tar，经 ssh 解到 Windows 的开发副本里，保留那边的 `.venv` |
| `wtest.sh <标签> [pytest 参数]` | 同步，跑 pytest，把日志拉回 Mac，按文件统计失败条数 |

一次「改一行 → 真机上跑那个测试文件」大约 20 秒，全量约 6 分钟。真机上的开发副本、venv、日志都放在一个单独的目录里，收尾时一次删掉。

### 2.4 测试夹具也要跨平台

测试里的「假 CLI」原来是 shell 脚本（`#!/bin/sh`），Windows 不能直接执行。用 `.cmd` 包一层也不行：cmd 会改写参数里的引号和特殊字符，测不出真实情况。最后的做法是在 Windows 上用系统自带的 `csc.exe` 编一个几行的 C# 小程序：它把原始命令行原样转给同目录的 `python <名字>.py`。假 CLI 的逻辑仍然只写一份 Python。

## 3. SSH 隧道加 Playwright：在 Mac 上替 Windows 用户点页面

单元测试证明的是「每个零件在 Windows 上对」，证明不了「一个研究者在 Windows 上装好、打开页面、走完一条流程」。要验这件事，得有人在 Windows 上点页面。agent 在 Mac 上，它能驱动的是 Mac 上的浏览器（Playwright MCP）。

### 3.1 拓扑

```
Mac                                         Windows 11
Claude Code                                 ai4sci serve（只听 127.0.0.1:8765）
 └─ Playwright MCP                           ├─ 研究助理：claude.exe
     └─ Chromium                             └─ 后台作业（Job Object 管着整棵树）
          │                                      ├─ python → claude.exe（执行层）
          ▼                                      └─ Git Bash → 评分脚本 → python
 http://127.0.0.1:18765 ──── ssh -L ───────▶ 127.0.0.1:8765
                          （SSH 加密隧道）
```

一条命令把 Mac 的 18765 端口接到 Windows 的 8765：

```sh
ssh -f -N -o BindInterface=en0 -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 \
  -i ~/.ssh/<钥匙名> -o IdentitiesOnly=yes -L 18765:127.0.0.1:8765 <用户名>@<Windows 的 IP>
```

然后 Playwright 打开 `http://127.0.0.1:18765`，就是 Windows 上那个平台的页面。

### 3.2 为什么这么接

- **请求全部落在 Windows 上**。页面上的每次点击（确认需求、签断点、给助理发消息）都变成一个 HTTP 请求，经隧道打到 Windows 的服务上。服务收到的请求，和用户坐在 Windows 前面点出来的一样。起作业、管进程树、调 claude.exe、在 Git Bash 里跑评分脚本、读写 `C:\` 路径，全在真机上发生。
- **服务不用改配置**。平台的服务只听 127.0.0.1，局域网里连不上；隧道从 Windows 本机这一端连进去，不用为了测试把服务开放到网络上，防火墙也只开着 22。
- **浏览器由 agent 驱动**。Playwright 读页面的无障碍树，按按钮的名字点，长按确认这类交互用鼠标按下 / 松开模拟。一整条流程不需要人碰键盘。
- **页面本身的逻辑也在测试路径上**。比直接调接口多测了一层：页面什么时候显示「停止」、签字键在哪、流程题头写什么，都是页面读服务的数据决定的。下面 [4.4](#44-端到端才撞出来的) 第 6 条「实验在跑，页面却说轮到助理」就是从页面上看出来的，光看接口不容易发现。

**没测到的**：浏览器自己的渲染。Playwright 开的是 Mac 上的 Chromium，Windows 上 Edge / Chrome 的中文字体回退、滚动条样式、`ai4sci setup` 装完自动弹出的浏览器窗口都没看过。页面是同一份静态文件，出问题的可能小，但这一块要人在 Windows 上打开看一眼才算数。

### 3.3 几个让它跑得起来的细节

- **服务要起在桌面会话里**。在 ssh 会话里起的服务，ssh 一断就跟着结束；Windows 的 OpenSSH 会把会话里的进程一起收掉。做法是在 Windows 上建一个计划任务：登录方式选「交互式」，动作是 `ai4sci.exe setup`（setup 查完一圈就起服务）。用 `Start-ScheduledTask` 起，服务就跑在桌面会话里，和用户双击打开的一样。
- **交互提问用伪终端喂**。`ai4sci setup` 会在终端里问 DeepSeek 的 key，读 key 用的是 `getpass`，要有终端。做法是在 Mac 上写一个小驱动：用 `ssh -tt` 起一个伪终端跑那行安装命令；输出里出现「粘贴 … key」时，把 key 从 Mac 上平台的家里读出来写进去。屏幕输出里万一出现 key 就遮掉，key 不进命令行、不上屏、不进日志。
- **作业状态用后台监视，不手动轮询**。Mac 上起一个后台循环，每 20 秒经 ssh 读一次作业记录，状态有变化才通知 agent。设计、实验、分析一跑完，agent 就被叫醒去看页面、签字、发下一句话。
- **停作业前后各拍一张进程树**。一个 PowerShell 小脚本按父进程号从作业的根往下找，列出整棵树。停之前：venv 的启动器 python → 真 python → claude.exe，各带一个 conhost；停之后：整棵树都不在了，只剩服务自己的两个 python。

### 3.4 这条流程跑出来的样子

| 步骤 | 结果 |
|---|---|
| 一行命令安装（CDN 测试目录） | 33 秒，git、两家 CLI 已装跳过，问 key、问一句通了（1.6 秒），起服务 |
| 需求 | 助理建工作区、写需求，人在页面上确认 |
| 设计 | 评分脚本与基线：val_mse 0.0125723，σ=0，统计门 0.0005 |
| 签「评分指标核对」 | 助理逐条对了评分脚本与需求，还指出一个需求里没写到的口子 |
| 实验（AutoResearch，3 轮） | 第 1 轮 0.0086745 留下；第 2 轮在噪声门内被弃；第 3 轮被人停掉，续跑时对账回到最好那版 |
| 分析、数字核对 | 分析 23 秒出稿，verify PASS（4 项） |
| 签「验收」 | 流程 `done` |

全程助理的裸命令（`grep`、`ls`）都被拦下，只能用 `ai4sci`；在 Windows 上用 Git Bash 跑 `ai4sci`、读写 `C:\` 路径都放行。

### 3.5 收尾

清掉的：
- 测试项目，用平台自己的删除，顺带验了带 git 只读对象的目录在 Windows 上删得干净；
- 计划任务、开发副本与日志、开发时留在 `%LOCALAPPDATA%\uv` 的缓存；
- Mac 上的隧道；
- CDN 上的测试目录。

留着的：
- 平台本身，发版后用正式地址的一行命令升到 1.8.0；
- 用户 Path 里那一项；
- SSH 与防火墙规则。

平台在家目录（`~\.ai4sci`）之外只写用户 Path 这一处，`%APPDATA%` 下没有留东西。

## 4. 撞到的问题，与 Mac 的差异

每条写成：现象 → 根因 → 怎么修。「Mac」一栏说 Mac 上有没有这个问题。

### 4.1 连接与环境

| 现象 | 根因 | 怎么修 |
|---|---|---|
| 公钥放了还要密码 | 管理员账号的公钥要放 `C:\ProgramData\ssh\administrators_authorized_keys`，权限要收紧 | 见 [1.2](#12-放公钥管理员账号放的地方不一样) |
| ping 通、22 不通 | 网络被标成「公用」，自带规则只管「专用」 | 单加一条限源网段的规则 |
| Mac 连不上同一局域网的机器 | VPN 接管了默认路由 | `ssh -o BindInterface=en0` |
| 远端命令引号错乱、中文乱码、错误输出是 XML | 默认 shell 是 cmd、代码页 936；PowerShell 重定向时把错误流序列化成 CLIXML | `-EncodedCommand` + 输出设 UTF-8 + 错误转纯文本 |
| `.ps1` 文件不能跑 | 执行策略 Restricted（研究者的电脑缺省就是） | 读成字符串建脚本块；安装走 `irm \| iex`，iex 跑的是字符串 |
| ssh 里起的服务一断就没了 | 会话结束时 OpenSSH 收掉会话里的进程 | 计划任务（交互式登录）起在桌面会话里 |
| `python3` 退出码 9009 | 没装 Python 的 Windows 上，`python` / `python3` 是微软商店的占位程序 | 测试与脚本里一律用当前解释器的绝对路径；uv 不认这个占位 |

### 4.2 平台代码：Windows 与 Mac 的差异

| 差异 | Mac / Linux | Windows | 怎么修 |
|---|---|---|---|
| 查进程活没活 | `os.kill(pid, 0)` 只查不发信号 | `signal.CTRL_C_EVENT` 的值就是 0，`os.kill(pid, 0)` 会给对方发 Ctrl+C | 用 `OpenProcess` + `GetExitCodeProcess` 查 |
| 杀整棵进程树 | 起进程时开新进程组，`killpg` 一下全杀 | 没有进程组，`os.getpgid` 不存在；只杀根会留下孤儿 | 起进程时先挂起，放进按根 pid 命名的 Job Object，再放行；杀就是结束整个 Job。两个坑：命名对象在最后一个句柄关掉时名字就没了，所以把 Job 句柄复制一份给根进程自己握着（真机实测）；venv 的 `python.exe` 是个启动器，会再起一个真解释器，每起一个 Python 都是两层进程，要整棵树都在 Job 里 |
| 文本编码 | 缺省 UTF-8 | 中文系统缺省 GBK：子进程输出、`read_text()`、`open()` 不写 `encoding` 都按 GBK 来 | 所有文本读写显式写 `encoding="utf-8"`；入口把标准输入输出换成 UTF-8，给子进程设 `PYTHONUTF8=1`；ast 检查器进门禁 |
| 命令行长度 | 很长（几 MB） | 一条命令行最多 32767 个字符；平台给助理的指南有 4 万字 | 正文一律走 stdin；Claude Code 的指南走 `--append-system-prompt-file`；Codex 的写进私有目录里的 profile。坑：Codex 的 `--ignore-user-config` 连 profile 也不读，改成平台自己把私有 `config.toml` 写成空的 |
| venv 里的解释器 | `bin/python` | `Scripts\python.exe` | 按环境建在哪台机器上选路径；交给 bash 和 JSON 的路径一律写正斜杠 |
| 绝对路径 | `/` 开头 | `C:\…`，`PurePosixPath` 认不出它是绝对路径 | 判断时 POSIX 与 Windows 两种都认 |
| bash | 系统自带 | 没有；评分脚本是 bash 写的，Claude Code 的 Bash 工具也要它 | 从 PATH 上的 git 推出 Git Bash（`<Git>\bin\bash.exe`），找不到再看注册表里登记的安装位置；缺 Git 时 `ai4sci setup` 从国内镜像装便携版 |
| 换行符 | LF | git 的 `core.autocrlf` 会把 `.sh` 检出成 CRLF，bash 跑不了 | 实验仓的每条 git 命令带 `-c core.autocrlf=false -c core.eol=lf`；`.gitattributes` 加 `*.sh text eol=lf` |
| 同步到远端算力 | rsync | 没有 rsync | 本机没有 rsync 就打 tar 走 ssh：推过去先删远端多出来的文件，拉回来不删本地的 |
| 文件被占用 | 可以替换别人正在读的文件 | 别的进程正读着时 `os.replace` 被拒，替换的那一刻去读也被拒（`PermissionError`） | 写与读都有限次重试，试够了照样抛 |
| 删目录 | `rmtree` 就行 | git 的对象文件是只读的，`rmtree` 删到它就失败 | 碰到只读先去掉只读属性再删 |
| key 文件只有本人能读 | `chmod 600` | 权限位没有意义 | 按 SID 设 ACL（账户名会本地化，所以按 SID）：先 `/reset`，再去掉继承、只给本人（见 [4.5](#45-ci-才撞出来的)） |
| 路径长度 | 无实际限制 | 缺省一条路径最多 260 个字符 | 不替人改系统设置，`ai4sci setup` 发现没开长路径就给一行管理员命令 |
| Claude Code 的 `apiKeyHelper` | 用 sh 跑，`cat <文件>` | 用 cmd.exe 跑，没有 `cat` | 写成 `type "<文件>"`（真机自检才发现） |
| Claude Code 的权限规则 | 绝对路径照写 | 规则里的路径要写成 `//c/Users/...`（官方：先换成 POSIX 形式再匹配） | 生成规则时按这个形式写；另关掉 PowerShell 工具，显式给 Git Bash 的位置 |
| Codex 的登录凭据 | 执行层的 `auth.json` 是根上那份的软链 | 建软链要管理员或开发者模式 | 用硬链接；Codex 刷新 token 是原地截断重写，硬链接两边始终一致，每次核对是不是同一个文件 |
| npm 装的 CLI | 可执行的脚本 | `.cmd` 壳，参数要过一遍 cmd 的改写 | 认作不够用，`ai4sci setup` 装原生 exe |
| uv 放进 bin 的入口 | 软链 | 一份逐字节相同的复制 | 判断「是不是同一份安装」时，内容一样也算 |
| uv 装 Python | 只在 uv 自己的目录里 | 还会往注册表登记（PEP 514），之后别处的 uv 会找到它 | 平台起 uv 时设 `UV_PYTHON_INSTALL_REGISTRY=0` |
| 照抄的命令 | shell 加引号 | PowerShell 里带空格的路径要写成 `& "…"` | 生成给人照抄的命令时按系统写 |

### 4.3 PowerShell 自己的坑

都是写一行命令安装的 `install.ps1` 时撞上的。

| 现象 | 根因 | 怎么修 |
|---|---|---|
| 安装脚本出错把用户的窗口关了 | `irm \| iex` 跑在人自己的会话里，`exit` 关的是他的窗口 | 整段包进脚本块，出错抛一个约定好的值、外层只补一句怎么办，不 `exit` |
| 下载慢几十倍 | 5.1 的 `Invoke-WebRequest` 画进度条极慢 | `$ProgressPreference = 'SilentlyContinue'` |
| 解压时画出一大片进度条 | `Expand-Archive` 是模块里的函数，不认脚本块里设的 `$ProgressPreference` | 用 .NET 的 `ZipFile` 解压 |
| 改了用户 Path，别处的 `%USERPROFILE%` 被写死 | 读 Path 时缺省会展开变量，写回去就变成了绝对路径 | 按原样读写（`REG_EXPAND_SZ`、不展开）；借设一个环境变量让系统广播一次「环境变了」，新开的终端才认 |
| 检查「有没有进程在用」不生效 | 变量名不分大小写：`$tools = uv tool list` 把 `$TOOLS`（家里的 tools 目录）盖掉了 | 改名；门禁查只差大小写的变量名 |
| 装坏了的那份重跑修不好 | `$ErrorActionPreference = 'Stop'` 下，5.1 把原生程序写到 stderr 的第一行当成异常抛出 | 问版本时临时放宽，坏了当没装 |
| 在 ISE 或 `\| Tee-Object` 里装，装完报「没装完」、服务被掐断 | 同上：setup 起的服务往 stderr 写日志 | 交给 setup 之前放宽；ps1 的测试一律在 `2>&1` 下跑，按最严的宿主测 |
| `Get-FileHash` 找不到 | 5.1 里它是模块的脚本函数；从 PowerShell 7 里再开 5.1 会继承 7 的 `PSModulePath`，加载不到（GitHub 的 Windows runner 就是这样，人在 pwsh 窗口里敲 `powershell` 也一样） | 用 .NET 的 `SHA256` 自己算；门禁查这类命令 |

### 4.4 端到端才撞出来的

单元测试全绿以后，真机端到端又撞出 6 个问题。其中 2 个和 Windows 无关，Mac 上一样有，只是一直用源码跑、没人用装出来的包跑过整条流程。

| # | 现象 | 根因 | 怎么修 | Mac |
|---|---|---|---|---|
| 1 | 设计作业失败：`No module named ruff` | 框架用 `python -m ruff` 检查草稿，但 ruff 只在开发依赖里，装出来的包里没有；报错还指向一个早就不存在的文件，把助理带去建议 `pip install ruff` | ruff 进运行时依赖；门禁扫框架里所有 `python -m <模块>`，要求都在依赖里 | 有，1.7.x 发布的包都缺 |
| 2 | 服务开着时重跑一行命令升级，平台起不来了 | Windows 上在跑的 exe 换不掉；uv 先删了 `site-packages`，删到 `Scripts\` 被拒才停，删掉的回不来 | 动文件之前查有没有进程在用这份安装，有就停下，说先关服务 | 无（Mac 上能删正在跑的文件） |
| 3 | 上一条的检查一开始不生效 | `$tools` / `$TOOLS` 是同一个变量 | 见 [4.3](#43-powershell-自己的坑) | 无 |
| 4 | 装坏了重跑修不好 | 坏掉的那份问版本时 stderr 有 traceback | 见 4.3 | 无 |
| 5 | 装完报「没装完」、服务被掐断 | setup 的日志走 stderr | 见 4.3 | 无 |
| 6 | 实验在跑，页面却说「轮到助理」，没有停止 | 工作区只有一条流程时 `--flow` 可省，产出会推断流程，但作业记录只认命令行上显式给的 `--flow` | 作业的流程改为开产出时照产出记 | 有 |

另有一个和 Windows 无关的发现，要先定语义才能修，单开了 issue：流程实例里写的能力参数（这次是 `patience: 1`）校验能过、页面上也显示，跑能力时却没用上。

### 4.5 CI 才撞出来的

内仓 CI 加了 `windows-latest` 作业。真机上全绿之后，GitHub 的 runner 第一次跑全量又挂了 5 条，归成 2 个原因，都是真问题：

| 现象 | 根因 | 怎么修 |
|---|---|---|
| 安装脚本的 4 条测试挂了，报 `Get-FileHash` 找不到 | runner 的步骤跑在 PowerShell 7 里，测试再起 5.1，继承了 7 的 `PSModulePath`，见 4.3 | 用 .NET 算 sha256 |
| key 文件「只有本人能读」不成立 | runner 上新建的文件带着显式的 SYSTEM、Administrators、OWNER RIGHTS 三条权限；原来的做法只去掉继承来的权限，显式的去不掉，等于管理员都能读。为什么 runner 上的新文件会带显式条目，真机上复现不出来，没查实 | 先 `icacls /reset` 把文件换回全部继承，再去掉继承、只给本人；补一条直接测这个函数的测试：先给文件加一条显式的 SYSTEM，调用后只剩本人（真机上先红后绿） |

第一次 CI 只给了「assert False」，看不出 ACL 长什么样。先把断言改成失败时带上 icacls 的原文，再跑一轮才看清。检查器失败时要说清看到了什么，不然多花一轮。

## 5. 带得走的经验

1. **agent 直接操作真机，比写移交文档快**。这件事原本写好了移交说明，打算交给另一位工程师做。开 SSH 花了半小时，其中大半卡在防火墙和 VPN 上；之后基线、修复、端到端在一个下午里做完。人在 Windows 上只做了几件事：开着 VPN 装 OpenSSH、输一次密码、加一条防火墙规则；之后的活都是 agent 经 SSH 做的。
2. **先拿真机全量基线，再按根因归类**。152 条失败归完是四五种原因，修一种绿一大片。照着失败清单排顺序，比照着设计文档排靠谱。
3. **单元测试全绿不等于能用**。端到端又撞出 6 个，其中 2 个已经在发布的包里存在了很久：开发时一直用源码跑，装出来的包从没有人走完过一整条流程。真机端到端要从一行命令安装开始，用的是装出来的包，不是源码。
4. **按最严的宿主测**。PowerShell 在 stderr 被重定向时最挑剔，就让所有 ps1 测试都在 `2>&1` 下跑；runner 的步骤跑在 PowerShell 7 里，测出了从 7 里开 5.1 的问题。真机、CI、用户的终端是三种宿主，每多一种就多撞出几个。
5. **机器能查的规矩进门禁，每个检查器带一条反例**：编码扫描、`python -m` 依赖扫描、ps1 变量撞名、5.1 的模块函数。人记不住的东西，靠门禁不靠记性。
6. **SSH 隧道加浏览器自动化，能在一台机器上测另一台机器上的服务**。服务只听本机也能测，不用改配置、不用暴露端口；页面的逻辑也在测试路径上。代价是浏览器本身的表现测不到，要另外补。
7. **没做的写清楚**：
   - 远端 Linux 算力的真机验收：手上没有开着的机器；
   - 在页面上实际点一次「停止」：作业都在半分钟内跑完，没赶上；页面与命令行调的是同一个函数，命令行那条验过了；
   - 用 Codex 当执行层跑一条流：真机自检通过；
   - Windows 上浏览器的渲染。

## 附录

脚本都放在会话的临时目录里，用完即删，不进仓库；这里留档，照着能重建。`<钥匙名>`、`<用户名>`、`<Windows 的 IP>` 换成自己的。

### A. 放公钥 push-key.sh

```sh
#!/bin/sh
# 把这台 Mac 的公钥放到 Windows 上：sh push-key.sh <用户名>@<Windows 的 IP>
# 只输一次 Windows 的登录密码；之后 ssh 用这把钥匙，不再要密码。连接从 Wi-Fi 网卡（en0）出去，绕开 VPN。
# 远端走 powershell -EncodedCommand：Windows 默认 shell 是 cmd 还是 PowerShell 都行，引号也不会被吃。
set -eu
target="$1"
via="-o BindInterface=en0 -o ConnectTimeout=10"
key_file="${HOME}/.ssh/<钥匙名>"
pub=$(cat "${key_file}.pub")
ps=$(cat <<'EOF'
$k = '__KEY__'
if (whoami /groups | Select-String 'S-1-5-32-544') {   # 管理员组：sshd 只认 ProgramData 里那份
  $f = Join-Path $env:ProgramData 'ssh\administrators_authorized_keys'
  Add-Content -Encoding ascii -Path $f -Value $k
  icacls $f /inheritance:r /grant '*S-1-5-32-544:F' /grant '*S-1-5-18:F' | Out-Null
} else {
  $d = Join-Path $HOME '.ssh'
  New-Item -ItemType Directory -Force -Path $d | Out-Null
  $f = Join-Path $d 'authorized_keys'
  Add-Content -Encoding ascii -Path $f -Value $k
}
"key added to $f"
EOF
)
encoded=$(printf '%s\n' "${ps}" | sed "s|__KEY__|${pub}|" | iconv -f UTF-8 -t UTF-16LE | base64)
echo "下面要输 Windows 的登录密码（微软账户就是微软账户密码，不是 PIN）"
ssh ${via} -o PubkeyAuthentication=no "${target}" "powershell -NoProfile -EncodedCommand ${encoded}"
ssh ${via} -i "${key_file}" -o IdentitiesOnly=yes -o BatchMode=yes "${target}" whoami
echo "钥匙能用了"
```

### B. 远端跑一段 PowerShell win.sh

```sh
#!/bin/sh
# 在 Windows 上跑一段 PowerShell：sh win.sh 'Get-Date'，或 sh win.sh - < script.ps1
# 走 -EncodedCommand 不怕引号；输出统一 UTF-8；连接从 Wi-Fi 网卡出去绕开 VPN。
set -eu
if [ "$1" = "-" ]; then body=$(cat); else body="$1"; fi
# 错误流转成纯文本：不然 PowerShell 在重定向时把它序列化成 CLIXML
script=$(printf '[Console]::OutputEncoding = [Text.Encoding]::UTF8\n$OutputEncoding = [Text.Encoding]::UTF8\n$ProgressPreference = "SilentlyContinue"\n& {\n%s\n} 2>&1 | ForEach-Object { if ($_ -is [System.Management.Automation.ErrorRecord]) { "$_" } else { $_ } }\n' "${body}")
encoded=$(printf '%s' "${script}" | iconv -f UTF-8 -t UTF-16LE | base64)
exec ssh -o BindInterface=en0 -o ConnectTimeout=10 -o ServerAliveInterval=30 -i "${HOME}/.ssh/<钥匙名>" \
  -o IdentitiesOnly=yes -o BatchMode=yes <用户名>@<Windows 的 IP> \
  "powershell -NoProfile -NonInteractive -EncodedCommand ${encoded}"
```

### C. 同步代码 wsync.sh

```sh
#!/bin/sh
# 把内仓工作区（含没提交的改动）同步到 Windows 的 ~\ai4sci-dev\platform，保留那边的 .venv
set -eu
here=$(dirname "$0")
repo=<内仓在 Mac 上的路径>
sh "${here}/win.sh" '$d = "$HOME\ai4sci-dev\platform"; New-Item -ItemType Directory -Force $d | Out-Null; Get-ChildItem -Force $d | Where-Object Name -ne ".venv" | Remove-Item -Recurse -Force'
cd "${repo}"
git ls-files -co --exclude-standard -z | COPYFILE_DISABLE=1 tar --null -T - -czf - | \
  ssh -o BindInterface=en0 -o ConnectTimeout=10 -i "${HOME}/.ssh/<钥匙名>" -o IdentitiesOnly=yes \
    -o BatchMode=yes <用户名>@<Windows 的 IP> "tar -xzf - -C %USERPROFILE%\\ai4sci-dev\\platform"
echo synced
```

Windows 10 1803 起自带 `tar.exe`，所以不用装别的。`git ls-files -co --exclude-standard` 列出受版本管理的与没被忽略的新文件，正好是「工作区现在的样子」。

### D. 同步加跑测试 wtest.sh

```sh
#!/bin/sh
# 同步内仓到 Windows 并跑 pytest，日志拉回本机：sh wtest.sh <标签> [pytest 参数…]
set -eu
here=$(dirname "$0")
tag="$1"; shift
sh "${here}/wsync.sh" >/dev/null
args="${*:-}"
sh "${here}/win.sh" "Set-Location \"\$HOME\\ai4sci-dev\\platform\"; \$env:UV_CACHE_DIR = \"\$HOME\\ai4sci-dev\\cache\"; \$env:PYTHONIOENCODING = 'utf-8'; \$t = Measure-Command { & .venv\\Scripts\\python.exe -m pytest -p no:cacheprovider --continue-on-collection-errors -rfE ${args} > \"\$HOME\\ai4sci-dev\\pytest-${tag}.log\" 2>&1 }; \"took \$([int]\$t.TotalSeconds) s\""
sh "${here}/win.sh" "Get-Content \"\$HOME\\ai4sci-dev\\pytest-${tag}.log\" -Encoding UTF8" > "${here}/pytest-${tag}.log"
tail -1 "${here}/pytest-${tag}.log"
grep -E '^(FAILED|ERROR)' "${here}/pytest-${tag}.log" | sed 's/ - .*//' | awk -F'::' '{print $1}' | sort | uniq -c | sort -rn || true
```

开发副本第一次要在 Windows 上建 venv：`uv sync --locked`，`UV_CACHE_DIR` 指到开发目录里，收尾时整个目录一起删掉。
