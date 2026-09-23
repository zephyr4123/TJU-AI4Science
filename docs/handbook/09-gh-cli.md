# 09 gh：GitHub CLI，agent 操作 GitHub 的手

## 场景

我们 issue driven（[01](01-issue-driven.md)）：开 issue、写评论、开 PR、看 CI、关 issue，每天几十次。这些事如果只能在浏览器里点，agent 就做不了，你就成了它和 GitHub 之间的搬运工——它写好评论你去贴，它开好分支你去点 PR。

`gh` 是 GitHub 官方的命令行工具。它对 agent 友好到不需要任何适配：命令行进文本、出文本，agent 在 Bash 里直接跑；`--json` 出结构化数据，agent 不用解析网页；一条命令干一件事，写进 prompt 就是一句话。**issue driven + coding agent，gh 不是可选的，是必备的。** 这一章主要写给 agent 用，人也要知道它是什么、agent 拿它在做什么。

## 装与登录

```bash
brew install gh            # macOS；Windows 用 winget install GitHub.cli，Linux 见 cli.github.com
gh auth login              # 浏览器里点一次授权，凭据进系统钥匙串，不落在文件里
gh auth status             # 看当前登录的是哪个账号
```

有两个 GitHub 账号（个人 / 公司）的人：`gh auth status` 会列出所有账号并标出哪个是活跃的，`gh auth switch` 切换。**agent 每次动 GitHub 之前先看一眼活跃账号**——用错账号开的 issue、PR 署的是另一个人。

## 我们流程里每一步对应的命令

流程本身在 [`CONTRIBUTING.md`](../../CONTRIBUTING.md)；下面是每一步的命令。默认在外层仓目录下操作外层仓；操作内仓加 `-R zephyr4123/TJU-AI4Science-Platform` 或直接 `cd platform`。

| 流程里的一步 | 命令 |
|---|---|
| 看真开着的 issue | `gh issue list --state open --limit 50` |
| 开 issue（标签三根轴） | `gh issue create --title "一句人话" --label kind:bug --label area:base --label P1 --body-file brief.md` |
| 读一条 issue 连评论 | `gh issue view 144 --comments` |
| 过程写进评论 | `gh issue comment 144 --body "根因：… 修在 b1501f8"` |
| 改标签、挂 milestone | `gh issue edit 144 --add-label needs-decision --milestone "platform 1.1.0"` |
| 挂 sub-issue（gh 没有子命令，走 API） | `id=$(gh api repos/zephyr4123/TJU-AI4Science/issues/145 --jq .id); gh api -X POST repos/zephyr4123/TJU-AI4Science/issues/142/sub_issues -F sub_issue_id=$id` |
| 列一条母 issue 的 sub-issue | `gh api repos/zephyr4123/TJU-AI4Science/issues/130/sub_issues --jq '.[].number'` |
| 开 PR 进 release 分支 | `gh pr create --base release/1.1 --title "commit 风格的一句话（#144）" --body-file pr.md` |
| 看 PR 的门禁 | `gh pr checks 143`（加 `--watch` 等它跑完） |
| 门禁红了看原因 | `gh run list --branch feat/144-env-use --limit 1` 拿到 run id，然后 `gh run view <id> --log-failed` |
| review 意见 | `gh pr review 143 --comment --body "…"`；认可 `--approve` |
| 合并（只用 merge commit） | `gh pr merge 143 --merge --delete-branch` |
| 关 issue 带证据 | `gh issue close 144 --comment "做了什么；外层 aec7327、内仓 b1501f8"` |
| 看发布 | `gh release list`、`gh release view v1.0.0` |
| 看某次 CI 在跑什么 | `gh run watch` |

## agent 读结果：`--json` 与 `--jq`

网页是给人看的，agent 要的是字段。几乎每条 `gh` 命令都有 `--json <字段>`，配 `--jq` 直接取值：

```bash
gh pr view 143 --json state,mergeable,statusCheckRollup --jq '{state,mergeable,checks:[.statusCheckRollup[]|{name,conclusion}]}'
gh issue list --state open --json number,title,labels --jq '.[]|"#\(.number) \(.title)"'
gh run list --branch main --workflow ci.yml --limit 3 --json conclusion,headSha --jq '.[]|"\(.conclusion) \(.headSha[0:7])"'
```

`gh` 没有子命令的事（sub-issue、ruleset、仓库设置）用 `gh api <REST 路径>`，返回 JSON；`gh api graphql -f query='…'` 走 GraphQL。

## agent 用 gh 的守则

这几条在 [`CLAUDE.md`](../../CLAUDE.md) 里是红线，这里说清楚落到 gh 上是什么：

- **动之前看账号**：`gh auth status`，活跃账号不对先 `gh auth switch`。
- **合并 PR、push 受保护分支、改写历史，每次都要人确认。** `gh pr merge` 是出分支的动作；ruleset 允许管理员绕过 review，不等于 agent 可以自己绕。
- **永不 `--force`**，不删别人的分支，不 `gh repo delete`。
- **关 issue 必带证据**：做了什么、在哪个 commit，两个仓都写；关之前核对代码里真有。
- **密钥不进命令行参数**：`gh` 自己管 token（钥匙串）；脚本里要 token 用 `gh auth token` 当场取，不写进文件，不 `echo`。
- **PR 与 issue 里不写「由 AI 生成」、不加机器人 emoji、不加 `Co-Authored-By`。** 它开的 PR 与人的一样进门禁与 review。
- **不用 gh 做 git 的事**：分支、commit、rebase 还是 `git`；`gh` 只管 GitHub 上的对象。

## 反例

- 让 agent「写一段评论，我去贴」：每次都断在你手上，过程记录一半在聊天里一半在 issue 里。
- agent 拿 `curl` 直接调 GitHub API：token 得自己管、分页得自己翻、错误得自己判，gh 全都做了。
- 用错账号开了 PR：署名是另一个人，还得关了重开。
- `gh pr merge --admin` 绕过门禁：门禁存在的理由就是不让这么干。

## 本仓真实例子

写这一章的当天，agent 用 gh 做了这些事，每一步都能在 GitHub 上核对：

- 发现内仓 CI 红：`gh pr view 1 -R zephyr4123/TJU-AI4Science-Platform --json statusCheckRollup` 看到 `check` 是 FAILURE；`gh run list --branch release-process` 拿 run id，`gh run view 35840523542 --log-failed` 读到 `No module named pip`；`gh run list --branch main --limit 3` 确认 `main` 上已经连红三次。这就是 [#144](https://github.com/zephyr4123/TJU-AI4Science/issues/144) 的全部取证过程，没开过浏览器。
- 开 issue：[#144](https://github.com/zephyr4123/TJU-AI4Science/issues/144)、[#145](https://github.com/zephyr4123/TJU-AI4Science/issues/145) 都是 `gh issue create --label … --body "$(cat <<'EOF' … EOF)"` 开的，正文是四段（[02](02-brief-an-agent.md)）。
- 列 sub-issue：`gh api repos/zephyr4123/TJU-AI4Science/issues/130/sub_issues --jq '.[].number'` 回 `131 132 133 134 135`，写 [01](01-issue-driven.md) 的例子时用来核对。
- 开 PR 与看门禁：外层 [PR #143](https://github.com/zephyr4123/TJU-AI4Science/pull/143)、内仓 [PR #1](https://github.com/zephyr4123/TJU-AI4Science-Platform/pull/1) 用 `gh pr create` 开、`gh pr checks` 看；合并等人点头。
