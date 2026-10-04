# Windows 适配 · 移交说明

- 状态：**待认领**。2026-10-03 起由另一位工程师接手；负责人：待定（认领后改这一行与 issue 的 assignee）
- 锚 issue：[#210](https://github.com/zephyr4123/TJU-AI4Science/issues/210)。两个仓的 commit 都引它
- 代码位置以内仓 `release/1.3` 的 `29dcf1d`（等于 v1.2.0）为准，行号会随代码漂移，找不到时按文件名与函数名找
- 这份是起点，不是定论：标了「需实测」的是没在 Windows 上验证过的判断，以实测为准；实测推翻了哪条，回来改这份文档
- 纲领：[architecture/](../architecture/README.md)（P-7 失败就停、P-14 agent 面前只有 `ai4sci`）；流程：[CONTRIBUTING.md](../../CONTRIBUTING.md)

## 1. 要做什么

### 1.1 目标

Windows 上的研究者能装上平台、用页面走完一条研究流，结果与 macOS 上一致。

### 1.2 范围

做：

- **使用者这条路**：装 GitHub Release 里的 wheel（`uv tool install`）→ `ai4sci check` → `ai4sci serve` → 在页面上跑完出厂流程 `research` 或 `reproduce`。
- **两家 agent**：先做 Claude Code，再做 Codex。Codex 要处理的问题更多，见 3.7。
- **两种算力**：本机；用 SSH 连远端 Linux 机器（AutoDL 这类）。

这一轮不做：

- **在 Windows 上开发平台**：`make`、用 Node 构建页面、`make check` 都不管。开发者用 macOS / Linux，或者 Windows 上的 WSL。
- **收录的第三方 skill**（`skills-curated/`）各自能不能在 Windows 上跑：撞到了再单独开 issue。
- **远端算力本身是 Windows** 的情况。

### 1.3 完成标准

1. **CI**：内仓 CI 有 `windows-latest` 作业跑全量 pytest，并且是合并门禁的必过项。起步时允许失败，见第 4 节。
2. **本机真机验收**：在一台真 Windows（Win11，或 Win10 1809 以上）上装好 Git for Windows 与 uv，然后：
   - 装 wheel，`ai4sci check` 各项通过；
   - `ai4sci serve`，浏览器能打开页面；
   - 用 Claude Code（订阅登录）跑通出厂 `research` 流程，选一个几分钟能跑完的小任务；
   - 作业跑到一半在页面上叫停：任务管理器里 claude、python 这些子进程全部结束，没有残留；
   - 关掉 `ai4sci serve` 再打开：之前在跑的作业状态显示正确（还在跑或 lost）。
3. **远端算力验收**：同样流程用 SSH 远端算力走一遍，产物传过去、跑完再传回来。
4. **不影响现有平台**：macOS / Linux 上现有测试全绿，行为不变。
5. **文档**：内仓 README「只用」那一节加上 Windows 的安装步骤；删掉代码里「本项目不跑 Windows」的说法（`framework/experiment/env.py:89`）。

## 2. 已经确定的判断

### 2.1 agent 登录不是障碍

- **Claude Code**：原生支持 Windows（Win10 1809 以上），订阅（Pro / Max）登录走浏览器。凭据存成普通文件 `%USERPROFILE%\.claude\.credentials.json`。macOS 上凭据在钥匙串里，相比之下 Windows 反而简单。
- **Codex CLI**：原生支持 Windows，有 Windows 自己的沙箱实现，用 ChatGPT 订阅登录，凭据在 `%USERPROFILE%\.codex\auth.json`。

出处见文末参考。

### 2.2 九成的工作不需要登录 agent

平台的测试不调真的 agent：执行层用的是按剧本回话的 `ScriptedRunner`（`tests/test_experiment_loop.py`）。进程、编码、路径、算力、页面这些问题，都能在 GitHub 的 Windows runner 上测出来、修掉。

只有「平台真的启动 claude / codex 跑一个任务」这一步，需要一台登录了 agent 的 Windows 机器，放到最后做（第 4 节第 5 步）。

### 2.3 路线：原生 Windows + Git for Windows，不走 WSL

- **为什么选原生**：用户是不写代码的研究者。WSL 要先在系统里开虚拟化、再装 Linux 发行版，对他们是一道门槛；原生装好就能用。
- **WSL 只当兜底**：WSL 里就是 Linux，平台基本不用改就能跑。原生路线卡住的用户可以先用 WSL，README 里写一句就够，代码里不为 WSL 写特殊分支。
- **Git for Windows 是硬依赖，不是可选**。原因有两个：
  - Claude Code 找不到 Git Bash 时会改用 PowerShell 跑命令，而我们给 agent 的放行规则只写了 `Bash(ai4sci *)`（`backends/claude_code.py:86` `bash_rule`），agent 会一条命令都跑不了；
  - 框架自己也直接 `bash xxx.sh`（见 3.8）。

  `ai4sci check` 要查它是否装了，缺的话说清楚该装什么。
- **待确认**：这条路线负责人倾向原生，接手时再确认一次。

## 3. 会遇到的问题

按严重程度排。每条写四件事：现在的代码，在 Windows 上会怎样，建议怎么改，怎么验证。

### 3.1 【严重】查进程是否还活着用的是 `os.kill(pid, 0)`

- **位置**：两处。
  - `framework/workspace/jobs.py:233` `_alive`：判断作业是不是 lost；
  - `framework/chat/conversation.py:420` `_lock_holder_alive`：判断对话锁的持有进程还在不在。
- **问题**：在 macOS / Linux 上，信号 0 只是「问一下进程还在不在」。在 Windows 上，`signal.CTRL_C_EVENT` 的值恰好是 0，Python 会把这次调用当成向那个进程组发 Ctrl+C，而不是查存活。结果要么把正在跑的作业打断，要么抛出我们没接住的 `OSError`。
- **建议**：抽一个「这个 pid 还在不在」的函数。Windows 上用 `OpenProcess` + `GetExitCodeProcess`（ctypes 就能做），或者 `psutil.pid_exists`。
- **验证**：在 Windows CI 上起一个 sleep 子进程，连调两次这个函数，子进程必须还活着；子进程结束后再调，必须返回「不在」。

### 3.2 【严重】杀进程树依赖 pgrep、ps 和进程组

- **位置**：两份。
  - `backends/_procs.py`：agent 超时时用；
  - `compute/procs.py`：本机算力与作业叫停时用，`workspace/jobs.py` 也用它。

  两份是同一套逻辑，因为规定 `backends/` 与 `compute/` 互不 import（`tests/test_layering.py`）。
- **问题**：
  - `pgrep`、`ps` 是外部命令，Windows 上没有；
  - `os.getpgid`、`os.killpg`、`signal.SIGKILL` 在 Windows 版的 Python 里根本不存在；
  - Windows 也没有「进程组」和「孤儿进程被 1 号进程收养」这一套。父进程一死，顺着父子关系就找不到孙进程了。
- **为什么不能简化成只杀顶层**：两个文件头的注释记了实测过的坑。Claude Code 的 Bash 工具会把命令起在新的进程组里；harness 的 `launcher.sh` 还会再起 python、mpirun。只杀顶层，会留下继续占着算力的孤儿进程。这件事在 Windows 上同样会发生。
- **建议**：Windows 上用 Job Object。
  - 起子进程时就把它放进一个 Job，并设上 `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`；之后它派生的所有进程都在这个 Job 里，杀掉 Job 就是杀掉整棵树，父进程先死也不影响。
  - `taskkill /T /F /PID` 只在父进程还活着时可靠，只能当兜底。
- **连带要改的**：现在作业记录里存的是进程组号 `pgid`（`compute/local.py:104`，`compute/procs.py` 的 `kill_tree(pid, pgid)` 与 `group_alive(pgid)`）。Windows 上要换成能跨进程找回来的东西，比如命名的 Job Object。作业记录是落盘的，`ai4sci serve` 重启后还要能叫停之前起的作业，这一点要设计好。
- **验证**：在 Windows CI 上起一棵「子进程再起孙进程」的树，叫停后孙进程也要没了。再做一次：先杀掉中间那一层，再叫停，孙进程同样要没了。

### 3.3 【严重】后台作业脱离不了起它的进程

- **位置**：所有写了 `start_new_session=True` 的地方：
  - `framework/workspace/jobs.py:97`：`--detach` 起作业；
  - `compute/local.py:101`；
  - `backends/claude_code.py:181`、`:359`；
  - `backends/codex.py:333`、`:516`。
- **问题**：`start_new_session` 只在 POSIX 上生效。作业的设计是「起它的命令返回之后，作业接着跑」（见 `jobs.py` 文件头）。
- **建议**：Windows 上改用 `creationflags`：`CREATE_NEW_PROCESS_GROUP`，再加 `DETACHED_PROCESS` 或 `CREATE_NO_WINDOW`。不这么做，作业会跟着控制台窗口一起结束、被 Ctrl+C 带走，还可能弹出黑窗口。
- **验证**：用 `ai4sci cap ... --detach` 起一个作业，然后关掉起它的终端；作业要能继续跑完，并把结果回写。

### 3.4 【严重】子进程的输出按系统编码解码，中文 Windows 上会解码失败

- **位置**：25 处 `subprocess.run` / `Popen` 用了 `text=True`，却没写 `encoding`，清单见附录 A。文件读写已经全部写了 `encoding="utf-8"`（用 AST 扫过，0 处遗漏），只差子进程这一块。
- **问题**：中文 Windows 的系统编码是 GBK（cp936），而 claude、codex、git 输出的是 UTF-8。不写 `encoding` 时 Python 按系统编码解码，一遇到中文就 `UnicodeDecodeError` 或者乱码。agent 的事件流里全是中文，等于平台整个跑不起来。
- **建议**：
  - 25 处统一写上 `encoding="utf-8"`；只用来记日志、不需要解析的输出，可以再加 `errors="replace"`；
  - 加一条测试扫源码，写法参考 `tests/test_layering.py`，防止以后新加的调用又漏写；
  - 不要靠 `PYTHONUTF8=1` 这个环境变量，因为用户怎么启动平台我们管不着。
- **验证**：在测试里让子进程输出含中文的 UTF-8 字节，在 Windows CI 上跑。CI 的系统编码同样不是 UTF-8，能复现这个问题；需实测确认 runner 的编码。最后在中文 Windows 真机上再验一遍。

### 3.5 【严重】系统提示放在命令行参数里，会超过 Windows 的命令行长度上限

- **位置**：
  - Claude Code 协调层用 `--append-system-prompt <全文>`（`backends/claude_code.py:341`）；
  - Claude Code 执行层的任务说明用 `-p <全文>`（`:157`）；
  - Codex 的指南用 `-c developer_instructions=<全文>`（`backends/codex.py:225`）。
- **问题**：Windows 上一条命令行最多 32767 个字符，macOS 约 1 MB。研究助理的系统提示由四部分拼成：前言、工具说明、本项目装载的 skill 清单、指南原文（`framework/chat/guide.py` 的 `system_prompt`）。2026-10-03 实测：
  - 指南 `coordinator/README.md` 有 17873 个字符；
  - skill 清单平均每个 skill 约 400 个字符，库里 202 个全装是 81832 个字符；
  - 一个项目装到 30 个左右的 skill 就会超限，进程直接起不来（WinError 206）。
- **建议**：
  - Claude Code：系统提示写进文件，改用 `--append-system-prompt-file`；`-p` 的正文改从 stdin 传，`claude -p` 支持管道输入。
  - Codex：用户消息已经走 stdin（`_write_stdin`）；指南还要找一个读文件的办法。`model_instructions_file` 是整体替换，文件头注释写了官方不建议用；有没有追加式的文件配置需实测。
  - 改法在 macOS 上一样适用。改完之后 macOS 也走同一条路，不要按平台分成两套。
- **验证**：在测试里造一份超过 32767 个字符的系统提示，在 Windows CI 上用一个假的 `claude` 可执行文件接住参数，确认进程能起来，而且收到的内容完整。

### 3.6 【严重，需实测】Claude Code 的权限规则在 Windows 上怎么写

- **PowerShell 工具**：
  - 现状：放行 agent 命令只写了 `Bash(ai4sci *)`。在 Windows 上，即使装了 Git Bash，Claude Code 的 PowerShell 工具也是默认开着的。
  - 风险：agent 可能用 PowerShell 敲 `ai4sci`，在 `dontAsk` 模式下会被拒。
  - 建议：在 `build_env`（`backends/claude_code.py:105`）里，Windows 上设置官方开关 `CLAUDE_CODE_USE_POWERSHELL_TOOL=0` 关掉它，保持「只有 Bash 一个口子」，和 macOS 一致。
- **路径规则**：
  - 现状：`_abs_glob`（`backends/claude_code.py:130`）把绝对路径写成 `//<路径>/**`，这是在 macOS 上实测出来的写法。
  - 风险：Windows 上会生成 `//C:/Users/...`，Claude Code 认不认还没验证过。认不了的话，执行层任何文件都写不进去。
  - 必须在真机上实测，需要登录。
- **找不到 Git Bash**：设置官方配置项 `CLAUDE_CODE_GIT_BASH_PATH`。`ai4sci check` 应该能把这件事告诉用户。
- **命令名**：用原生安装器装的是 `claude.exe`，没问题；用户如果是用 npm 装的，命令是 `claude.cmd`，处理同 3.7 第 3 条。

### 3.7 【严重，需实测】Codex 的三处问题

1. **登录共享靠软链**：
   - 现状：私有 `CODEX_HOME` 里的 `auth.json` 是一个软链，指向 `~/.codex/auth.json`（`backends/codex.py:177-181`）。
   - 问题：Windows 默认不允许普通用户建软链，要开开发者模式或者有管理员权限，否则会抛 `OSError`。
   - 也不能改成复制：文件头写明了「凭据不复制」，而且 token 刷新时要写回原文件。
   - 可选方向：要求用户开开发者模式，对研究者不友好；或者设 Codex 的 `cli_auth_credentials_store = "keyring"`，把凭据放进 Windows 凭据管理器，再看私有 home 下能不能读到（需实测）。
2. **命令放行规则**：
   - 现状：`ai4sci` 能在沙箱外跑，靠的是 execpolicy 的前缀规则（`backends/codex.py:185` `write_rules`）。macOS 上实测过，`/bin/zsh -lc 'ai4sci …'` 能命中。
   - 需实测：Windows 上 Codex 用 PowerShell 跑命令，沙箱也是另一套实现。前缀规则能不能命中、`writable_roots` 是否照样生效，都要实测。
3. **命令名**：
   - 问题：用 npm 装的 Codex，在 Windows 上命令是 `codex.cmd`。Python 的 `subprocess` 用列表传参时只会自动补 `.exe`，找不到 `.cmd`，报 `FileNotFoundError`。而且 `.cmd` 是交给 `cmd.exe` 执行的，参数里的引号和换行会被改写；`-c developer_instructions=...` 里全是换行。
   - 建议：先用 `shutil.which` 解析出完整路径再起进程，有 `.exe` 就用 `.exe`；长文本不放进参数，和 3.5 一起解决。

### 3.8 【中】框架直接调 `bash`

- **位置**：
  - `framework/capabilities/auto_research/judge.py:31`：`bash harness/launcher.sh`；
  - `framework/experiment/baseline.py:67`：`bash harness/make_run0.sh`。
- **问题**：Windows 起进程时，会先在 `System32` 里找可执行文件，然后才轮到 `PATH`。装过 WSL 的机器上，`C:\Windows\System32\bash.exe` 是 WSL 的入口。所以写一个光秃秃的 `bash`，脚本会跑进 WSL 的 Linux 里，找不到 Windows 这边的 Python 和任务环境。
- **建议**：本机算力在 Windows 上，显式找 Git Bash 的 `bash.exe`。它在 Git 安装目录下的 `bin\bash.exe`，可以从 `git` 所在的位置推出来；找不到就报错，说清楚原因。远端算力是 Linux，不受影响。
- **验证**：在装了 WSL 的 Windows 上跑一次基线，确认脚本是在 Git Bash 里跑的。

### 3.9 【中】任务环境的解释器路径写死成 `bin/python`

- **位置**：
  - `framework/experiment/env.py:90` `venv_python`，函数说明里写着「只做 POSIX，本项目不跑 Windows」；
  - `framework/experiment/env.py:193`。
- **问题**：Windows 的 venv 里，解释器在 `Scripts\python.exe`。
- **注意**：这个环境可能建在远端 Linux 上（SSH 算力），也可能建在本机。路径要按「环境建在哪台机器上」来选，不能按「平台跑在哪」来选。
- **验证**：在 Windows 上用本机算力建一次任务环境，并跑一次基线。

### 3.10 【中】换行符

内仓 `.gitattributes` 现在只有几行 `export-ignore`，没有换行符规则。由此有两个问题：

1. **开发者 clone 下来的脚本跑不了**：
   - 问题：Git for Windows 默认 `core.autocrlf=true`。开发者在 Windows 上 clone 后，`.sh` 会变成 CRLF，bash 报 `$'\r': command not found`。
   - 影响范围：装 wheel 的使用者不受影响，因为 wheel 是在 Linux CI 上打的。
   - 建议：加 `*.sh text eol=lf`。
2. **可能被误判成评测被篡改（需实测，可能更严重）**：
   - 背景：实验内环会在 `experiment/<n>/work/` 里自己建 git 仓，每轮都可能 reset（`framework/experiment/gitwork.py`），并用 `SHA256SUMS` 证明评测文件没被改过（`framework/capabilities/auto_research/failures.py:160`）。
   - 问题：用户全局开了 `autocrlf` 的话，reset 时 git 会把文件改成 CRLF，评测文件的哈希就对不上了，会被当成评测被篡改。
   - 建议：`gitwork.git()` 每次调用都带上 `-c core.autocrlf=false`，让平台自己的仓不受用户全局配置影响。

### 3.11 【中】SSH 远端算力靠 rsync

- **位置**：`compute/ssh.py:108` `_rsync`、`:254`；`ai4sci compute add` 的探测项里也查 rsync（`:285`、`:315`）。
- **问题**：Windows 自带 OpenSSH 客户端（`ssh`、`scp`），但没有 rsync。
- **建议**：
  - 本机是 Windows 时，传输改成 `tar` 打包后走 ssh 管道（Win10 起自带 `tar.exe`），或者用 `scp`；
  - 现在用到了 `--delete`（删掉远端多出来的文件）和 `--exclude`，换方案时这两个效果都要保住；
  - 不建议让研究者自己去装 rsync；
  - 本地路径传给 ssh / scp 之前，要处理好盘符（`C:\...`）。
- **不用改的**：远端那一侧（`nohup setsid` 起作业、杀远端进程组）跑在 Linux 上。

### 3.12 【低】路径与显示

- **配置目录**：
  - 现状：按人的配置在 `~/.config/ai4sci/`（`framework/paths.py:49`、`framework/computes.py:28`、`framework/agents.py:37`），数据根缺省在 `~/ai4sci`（`paths.py:48`）。
  - 判断：Windows 上 `Path.home()` 工作正常，这些路径都能用，只是不太合 Windows 的习惯，一般会放在 `%APPDATA%`。
  - 建议：保持不变，所有平台一个位置，文档好写，在 README 里写明即可。
- **uv 缓存显示错位置**：缺省值 `~/.cache/uv`（`paths.py:51`）只用于页面设置和 `ai4sci check` 的显示（`framework/chat/settings.py:76`、`framework/cli/check.py:51`）。但 uv 在 Windows 上实际的缺省位置是 `%LOCALAPPDATA%\uv\cache`，所以显示的会是错的位置。
- **遗留的放行前缀**：`framework/chat/guide.py:31` 的放行前缀里还有 `.venv/bin/ai4sci`，Windows 上没有这个路径。按第 50 行的注释，它是给老对话兼容用的，可以顺手确认还要不要留。

### 3.13 【低，需实测】替换文件时文件正被占用

- **原子写入**：
  - 现状：`framework/files.py` 的 `write_atomic` 用 `os.replace` 替换文件。
  - 问题：Windows 上目标文件正被别的进程打开时，`os.replace` 会报 `PermissionError`。页面服务正在读作业状态、作业刚好在写，就可能撞上。
  - 建议：先在真机上跑一个长一点的作业观察；真撞上了再加有限次数的重试，但不要把错误吞掉。
- **执行权限**：`framework/experiment/pack.py:544` 给 harness 脚本加执行权限，这在 Windows 上无效。但我们都是用 `bash xxx.sh` 显式调用的，不受影响，不用改。

## 4. 建议的做法与顺序

1. **开分支**：认领 #210，从内仓 `release/1.3` 切出 `feat/210-windows`，外仓要改文档时用同一个号。
2. **加 Windows CI**：在内仓 `.github/workflows/ci.yml` 加一个 `windows-latest` 作业，装 uv 和 Python，跑 `uv run pytest`。不跑 `make check`，因为它还要用 Node 构建页面、要用 make，不在这一轮的范围里。先设 `continue-on-error: true`，把第一份失败清单贴到 #210。
3. **按顺序修**：
   - 先修 3.4 编码：改动面大，但都是机械改动；
   - 再修 3.1 到 3.3 进程，接着 3.5 到 3.7 agent，最后是其余各条；
   - 一类问题一个 PR，每个 PR 都带能在 Windows CI 上跑的测试。
4. **Windows CI 改成必过**：全绿后去掉 `continue-on-error`，把它加进 `main` 与 `release/**` 的必过检查；ruleset 由负责人改。
5. **上真机验收**：按 1.3 的第 2、3 条做。这一步要用 Claude Code 订阅登录，接手人用自己的 Windows 机器。
6. **写文档**：
   - 内仓 README「只用」那一节加上 Windows；
   - 删掉代码里「本项目不跑 Windows」的说法；
   - 纲领 `docs/architecture/workflow.md` 里有 POSIX 假设的地方一起改；
   - 两边的 CHANGELOG 都写上。

## 5. 不要做的

- **不要用 `shell=True`**，也不要把命令拼成一个字符串来绕开问题：引号和注入都会出事。
- **不要为了让 Windows 跑起来而放宽 agent 的权限**。agent 面前只有 `ai4sci` 这一个命令（纲领 P-14）：Claude Code 不要换成 `bypassPermissions`，Codex 不要关沙箱。
- **不要复制凭据文件**。
- **不要吞异常**：Windows 上暂时不支持的功能，要明确报错并说清原因（纲领 P-7）。
- **不要改 macOS / Linux 上的行为**。进程相关代码里「为什么这么做」的注释，都是实测踩出来的坑，要保留。
- **不要到处写 `if sys.platform == "win32"`**。平台差异要收在现有的几个模块里（`backends/_procs.py`、`compute/procs.py`、`workspace/jobs.py`、各 agent 适配器），调用方感知不到。注意 `backends/` 和 `compute/` 之间不许互相 import，也不许 import `framework`，`tests/test_layering.py` 会查。
- **不要加「Windows 上改走 WSL」的代码分支**。

## 6. 需要的机器与账号

- **GitHub 的 `windows-latest` runner**：第 4 节第 1 到 4 步都在这上面做，不需要任何登录。
- **一台真 Windows**：推荐 Win11，装好 Git for Windows 与 uv。第 5 步要在上面登录 Claude Code 订阅。最好是中文系统，才能验证 3.4。
- **一台远端 Linux 算力**：用现有的 AutoDL 流程就行，用来验 SSH 那条路。

## 附录 A：用了 `text=True` 却没写 `encoding` 的子进程调用（内仓 `29dcf1d`）

用 AST 扫 `framework/`、`backends/`、`compute/` 得到。

| 文件 | 行 |
|---|---|
| `backends/_procs.py` | 20 |
| `backends/claude_code.py` | 179、357、486、498、513 |
| `backends/codex.py` | 331、514、571、585、599 |
| `compute/local.py` | 77、156、161 |
| `compute/procs.py` | 22、68 |
| `compute/ssh.py` | 99、112、257 |
| `framework/capabilities/reproduction/__init__.py` | 223、225 |
| `framework/experiment/drafting.py` | 200、224 |
| `framework/experiment/gitwork.py` | 34 |
| `framework/skills/run.py` | 77 |

## 参考

- Claude Code 安装与 Windows 设置：<https://code.claude.com/docs/en/setup>
- Claude Code 认证与凭据位置：<https://code.claude.com/docs/en/authentication>
- Claude Code 命令行参数（`--append-system-prompt-file`、`-p` 走管道）：<https://code.claude.com/docs/en/cli-reference>
- Codex 在 Windows 上的支持与沙箱：<https://learn.chatgpt.com/docs/windows/windows-sandbox>
- Codex 认证（ChatGPT 登录、`auth.json`、`cli_auth_credentials_store`）：<https://developers.openai.com/codex/auth>
- Python `os.kill` 在 Windows 上的行为：<https://docs.python.org/3/library/os.html#os.kill>
- Windows 命令行长度上限（`CreateProcessW` 的 `lpCommandLine`）与可执行文件搜索顺序：<https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-createprocessw>
