# 平台的家 `~/.ai4sci` 与供应商切换

- 状态：实现中（platform 1.7.0）
- 锚：母 issue [#263](https://github.com/zephyr4123/TJU-AI4Science/issues/263)；叶子 [#264](https://github.com/zephyr4123/TJU-AI4Science/issues/264)（家）、[#265](https://github.com/zephyr4123/TJU-AI4Science/issues/265)（key）、[#266](https://github.com/zephyr4123/TJU-AI4Science/issues/266)（供应商）、[#267](https://github.com/zephyr4123/TJU-AI4Science/issues/267)（设置页）
- 日期：2026-10-06（主人与 Claude 对齐）
- 相关纲领：P-23（算力归人）、P-25（底座归人）、P-27（不要 key 也能用）；内仓红线 4（密钥）、16（可选 key）

## 0. 一页看完

**为什么做**：平台要照顾想花 10 块钱跑通端到端、没有订阅的人。今天只能用 Claude / ChatGPT 的订阅登录；平台的私有东西还散在用户的五个目录里，清不干净。

**做什么**：

1. **一个家**。平台的一切私有东西收进 `~/.ai4sci`，像 Claude Code 的 `~/.claude`：设置、key、项目与产出、两家 CLI 的会话记录与登录、依赖缓存。用户带着干净的环境进来，想清除时一把删干净。平台不再写用户自己的 `~/.claude`、`~/.codex`、`~/.config`。
2. **供应商切换**。Claude Code、Codex 各自选用谁的模型：官方登录、官方 API key、DeepSeek、Kimi、自定义。key 在设置页粘贴、存在家里；模型清单跟着供应商走；成本按供应商的价目表算。

**和 cc-switch 的区别**：cc-switch 改用户本机 CLI 的全局配置，切了用户自己的终端也跟着变。平台不碰任何全局文件，只在起 agent 时把地址、key、模型交给那一个进程；平台用 DeepSeek 的同时，用户本机照样走订阅（2026-10-06 冒烟实测）。

## 1. 家

```
~/.ai4sci/                  AI4SCI_HOME 可指向别处（开发、测试）
  agents.yaml               用哪家、每家的供应商 / 模型 / 思考深度、上次检查
  computes.yaml             算力
  keys.yaml                 key：只有本人能读（0600）
  projects/<项目>/           项目、工作区、产出、项目里的对话
  studio/                   编辑台的流程与对话
  claude_code/              Claude Code 的配置目录（CLAUDE_CONFIG_DIR）：会话记录、平台自己的登录
  codex/                    Codex 的 CODEX_HOME：会话记录、登录、放行规则；执行层在 codex/executor/
  cache/uv/                 skill 与实验环境的依赖缓存（UV_CACHE_DIR）
```

- **一个读取点**：家在哪只在 `framework/paths.py`；下面每样东西的路径也由它给。源码跑与装包跑都是 `~/.ai4sci`，不再有「源码跑时数据根是仓库」。仓库根下的样例项目随之删掉。
- **两家 CLI 的私有目录在家里**：适配器不再自己定路径（删 `AI4SCI_CODEX_HOME`、`~/.config/ai4sci/codex-home`），由框架交给它。
- **官方订阅在平台里单独登录**（主人 2026-10-06 又定：平台上开发与测试一律 Claude Code + DeepSeek，官方登录只留终端命令 `ai4sci agent login <家>`，页面不做浏览器授权——服务端起 `claude auth login` 会直接弹 Safari、还要把页面给的码贴回 CLI）：`CLAUDE_CONFIG_DIR` 指到私有目录后，CLI 不认用户本机的登录（2026-10-06 实测 `loggedIn:false`）。这正是隔离要的：平台的登录归平台，清除时一起清掉。Codex 同理，不再软链用户的 `~/.codex/auth.json`。登录走 CLI 自己的流程（浏览器授权），只在终端里：`ai4sci agent login <家>`（要终端，agent 起不了）。
- **清除**：`ai4sci reset` 与设置页「清除全部数据」做同一件事：先让两家 CLI 在平台的目录里登出（Claude 的登录在系统钥匙串里，不登出会留下），再清空整个家、留一个只有标记的空家（回到刚装好的样子）。家里有一个标记文件，没有标记的目录不删（防 `AI4SCI_HOME` 指错删了别的）；有作业在跑时拒绝。命令只给人：要终端、要敲「清除」两个字；页面按住确认。
- **删掉的**：`~/.config/ai4sci/`、`AI4SCI_AGENTS`、`AI4SCI_COMPUTES`、`AI4SCI_CODEX_HOME`、源码模式的数据根缺省、Codex 的凭据软链、仓库根的 `projects/` 样例。

## 2. key

- `~/.ai4sci/keys.yaml`，权限 0600，读写点只在 `framework/keys.py`。键是供应商的名字（`deepseek`、`kimi`、`anthropic`、`openai`），外加 `openalex`；自定义供应商的 key 记在 `custom.<家>` 下。
- 页面上只显示末四位，接口从不把 key 整个吐回页面。
- 平台起子进程时把 key 交给那一个进程（Claude Code 是 `ANTHROPIC_AUTH_TOKEN` / `ANTHROPIC_API_KEY`，Codex 是供应商配置里点名的变量）；不读用户 shell 里的环境变量。
- OpenAlex 的 key 同样从这里读，不再读 `OPENALEX_API_KEY`。
- 纲领改写：红线 4「密钥只进环境变量」改成「密钥只在家里的 `keys.yaml`，不进代码、不进 argv、不进 git」；P-27「只走环境变量」同步改。

## 3. 供应商

| 供应商 | Claude Code | Codex | 要什么 |
|---|---|---|---|
| 官方登录 | Claude 订阅 | ChatGPT 登录 | 在平台里登录一次 |
| 官方 API | Anthropic API key | OpenAI API key | key |
| DeepSeek | `api.deepseek.com/anthropic` | `api.deepseek.com`（Responses） | key |
| Kimi | `api.moonshot.cn/anthropic` | `api.moonshot.cn/v1`（Responses） | key |
| 自定义 | 兼容 Anthropic 的地址 | 兼容 OpenAI Responses 的地址 | 地址、模型名、key |

- **对照表**：每家适配器一份供应商目录（地址、怎么交 key、模型清单、思考档、起点、价目），数据从 cc-switch（MIT）搬：供应商预设（`src/config/*ProviderPresets.ts`）、价目种子（`src-tauri/src/database/schema.rs` 的 `seed_model_pricing`）、Codex 的 DeepSeek 模型说明（`codex_deepseek_catalog_template.json`）。文件头记从 cc-switch 哪次提交搬的；更新价目跑外层 `scripts/sync-provider-prices.py`。**思考深度不从 cc-switch 搬**，照各家官方文档（主人 2026-10-06 定，#266）：旋钮上只给那家分得出来的档，一档对一档、不出现多对一，起点照官方缺省——DeepSeek 与 Kimi K3 都只分 low / high / max（DeepSeek 缺省 high、Kimi 缺省 max，DeepSeek 把 medium、xhigh 当 high），Kimi K2.7 Code 不认思考深度所以不进清单；官方两家用 CLI 自己的档（Claude Code 五档、Codex 四档）。两家 CLI 都把选的档原样发出去（本机抓包）。每家的档写明官方出处与查证日期；Codex 随包的模型说明与档位表对账，测试守着。**上下文开满**（主人 2026-10-06：必须配）：Claude Code 接 DeepSeek、Kimi 时模型名带 `[1m]`（不带按 200k 算），自动压缩窗口照两家官方给 Claude Code 的配置；Codex 的模型说明里本来就是 1M。**能不能联网也照官方文档登记**（主人 2026-10-06，P-14 的例外）：搜索在供应商的服务端跑——Claude Code 的 WebSearch 是向同一个地址另发一个只带服务端工具 `web_search_20250305` 的请求（本机转发抓包，DeepSeek 回了搜索结果），Codex 的 `web_search` 是 Responses API 的内置工具——所以看的是那家在这个 CLI 用的那套接口里实没实现，同一家在两个 CLI 上可以相反，按 CLI × 供应商一格一格登记、写出处，没有缺省值（#271）。现在：Claude Code 接 DeepSeek 能（兼容表标 Supported，实测通），接 Kimi 不能（Messages 接口只认 custom 工具，未实测）；Codex 接 DeepSeek 不能（Responses API 忽略内置工具，实测模型说没有搜索工具），照实关掉，接 Kimi 能（Responses 文档写「由服务端执行」，未实测）；官方两家都能。设置里标「不能联网」，选它的那一层琥珀色一行提醒，只提醒不拦。
- **模型跟着供应商走**：选了 DeepSeek，模型下拉只有 DeepSeek 的模型；对话 meta 与运行留档记下供应商，旧记录没有就当官方。
- **Claude Code 怎么接**：`ANTHROPIC_BASE_URL` + key + `--model <那家的模型名>`；后台的小活（标题、摘要）用的 haiku 映射到那家最便宜的模型（`ANTHROPIC_DEFAULT_HAIKU_MODEL`）。
- **Codex 怎么接**：`-c` 写一个 `model_providers.<名>`（`base_url`、`wire_api="responses"`、`env_key`），key 放进那个变量；不是 OpenAI 的模型要给 `model_catalog_json`（模型说明，cc-switch 有 DeepSeek 那份），不然 Codex 不知道这些模型怎么调工具。
- **成本**：官方的（订阅、官方 API）照旧用 CLI 报的数；第三方按目录里的价目算；价目里没有的写「未知」，不当 0。

## 4. 设置页

- 「AI」每家一格多一枚「供应商」下拉；选了要 key 的，旁边一格粘贴（显示末四位，「换」「删」）；选了官方登录，写一句「在终端里跑 `ai4sci agent login <家>`」（主人 2026-10-06：页面不做浏览器授权）。
- 模型、思考深度的下拉跟着供应商换。
- 「存放」那格写家在哪、各部分占多大，最底下「清除全部数据」，按住确认。

## 5. 迁移（内测期不兼容走 MINOR）

`scripts/oneoff/migrate-to-home-263.py`（外层）一次搬：旧数据根的 `projects/` `studio/`、`~/.config/ai4sci/` 的两份清单、Codex 私有 home 里的会话记录（不搬凭据软链）、`~/.claude/projects/` 里平台对话的会话记录（按新路径改目录名，续聊才找得到）。先 `--dry-run` 列清单，再搬；不删旧的，人确认后自己删。

## 6. 验收

- 新装：没有 `~/.ai4sci` → 起服务 → 设置里选 DeepSeek、粘 key、检查通过 → 建项目、对话、跑一步，成本按 DeepSeek 价算。
- 本机隔离：跑完以上，`~/.claude`、`~/.codex`、`~/.config/ai4sci` 的修改时间不变。
- 清除：一键清除后 `~/.ai4sci` 不在，钥匙串里平台那条登录不在；用户自己的 Claude 仍登录着。
- 四种组合（Claude Code / Codex × DeepSeek / Kimi）各一次探针；没 key 实测的标「未实测」写进目录。
- 两仓 `make check` 绿；设置页过浏览器（浅深、手机）。

## 7. 未验证（动手时逐条取证）

- Claude 的 `auth login` 被服务端起（没有终端）时怎么走：自动开浏览器，还是要贴码。
- Codex 接 DeepSeek / Kimi 的 Responses：工具调用、续接、联网搜索是否都通。
- `--effort` 对第三方模型有没有效果（DeepSeek 接受这个参数、不报错，2026-10-06）。
