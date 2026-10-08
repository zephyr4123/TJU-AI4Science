"""助理指南做减法（外层 #287）的验收回放：新旧两份内仓各起一遍同样的决策点，拆轨迹比。

一个探针 = 一个冻结的世界（从录下的项目拷一份，退回到某个决策点）+ 一句话（人的原话，或框架叫醒那一轮
的话）。每次都开新对话（老对话里冻着旧指南，换指南后整份补发，比不出东西）。两组是两份内仓的 worktree，
各自 `uv sync --locked`：A 改之前、B 改之后；同一个探针在两组里只差代码。

比的是过程不是结局：命令错了几条（被拒、退 2、框架拒）、断点前有没有调下游、读了几次说明、几轮几次工具、
花了多少（DeepSeek 按官方价折算，CLI 报的 total_cost_usd 是按 Anthropic 的价算的，不用）。

用法（在外层仓根）：
    python3 scripts/evals/guide_replay.py run --group A=<A 的仓> --group B=<B 的仓> \
        --dev-home materials/home --out <输出目录> [--probe L1 --probe G3 …] [--reps 1]
    python3 scripts/evals/guide_replay.py report <输出目录>

每次运行一个独立的平台的家：拷开发用的家里的 agents.yaml、keys.yaml（不打印）、computes.yaml，加上探针
的世界。PATH 上不能有全局的 ai4sci（agent 的 PATH 是把 venv 的 bin 追加在后面，全局的会盖掉这一组的）。
助理起了后台作业，这一轮结束就停掉（探针只看到目标命令出现为止）。

依赖内仓的代码只在 `_driver` 子命令里，用那一组的 venv 跑；本脚本的其余部分只用标准库。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

# DeepSeek V4.1 Flash 每百万 token 的美元价（内仓 backends/catalog/prices.json）
PRICE = {"input": 0.3, "cached": 0.006, "output": 1.2}
TURN_TIMEOUT_S = 1200
HOME_FILES = ("agents.yaml", "keys.yaml", "computes.yaml")
# 叫醒那一轮的话：框架的原文（notify.message_for），{line} 是作业的结论行
WAKE = ("工作区 {ws} 的作业 {job}（`ai4sci {argv}`）跑完了，退出码 0：\n{line}\n\n"
        "看一眼结果（ai4sci show output <id> --ws {ws} / show job），用人话告诉研究者发生了什么、"
        "下一步打算怎么办；要调用下一条命令就调，长的照旧 --detach。")


@dataclass
class Probe:
    """一个决策点：世界从哪拷、退回到哪、说什么、期望什么。"""

    name: str
    what: str
    project: str | None  # 录下的项目名；None 是空项目（G1、H）或编辑台（S）
    workspace: str | None = None
    drop: tuple[str, ...] = ()  # 相对工作区要删掉的（后面的产出、签字）
    human: str = ""  # 人说的话；空就是叫醒
    wake: dict = field(default_factory=dict)  # 叫醒：job、argv、line（A 组的原文）、next（B 组的新说法）
    studio: bool = False
    new_project: str | None = None


PROBES = {
    "L1": Probe(
        "L1", "精读跑完（1005-2 的 turn-5）：不开写作产出，照笔记回答，点名没读成的",
        "project-1005-2", "long-term-memory-review", drop=("writing",),
        wake={"job": "job-20261005T053343Z-5a8d",
              "argv": "cap literature-read --from literature/1 --max-papers 45 "
                      "--ws long-term-memory-review --flow literature-survey",
              "line": "read ok\tpapers=45\tnotes=44\tquotes=240/257\tcost_usd=nan\tpath=sources.md"
                      "\toutput=literature/2",
              "by": "literature-read", "oid": "literature/2", "flow": "literature-survey", "step": 0}),
    "G3": Probe(
        "G3", "原码复现基线跑完、没签（GUA 的 turn-8）：不调下游，把两列数念给人，请人签",
        "gua", "gua", drop=("analysis", "verification", "design/1/signed.json"),
        wake={"job": "job-20260921T044604Z-8e04", "argv": "cap reproduction --continue design/1",
              "line": "reproduction ok\tsession=-\tchanged=0\tsealed=-\tlint=0\tvalidate=0"
                      "\tcost_usd=0.0000\tinner_k=1\tbaseline=0.00076929\tsigma=0.000202455"
                      "\tgate=0.00040491\tattainable=0.00065\troom=0.00011929（0.3 个门）"
                      "\tupstream_changed=0\tnext=把论文值（attainable）与我们的值（baseline）念给研究者，"
                      "对上了没由他判；签了就 ai4sci cap reproducibility --from design/1\toutput=design/1",
              "next": "next=把论文值（attainable）与我们的值（baseline）、改了几个上游文件念给研究者，"
                      "对上了没由他按需求里的标准判",
              "by": "reproduction", "oid": "design/1", "flow": "reproduce", "step": None}),
    "G1": Probe(
        "G1", "空项目，人给一篇论文的链接要复现（GUA 的 turn-1）：照复现的模板起工作区、写需求初稿，不跑步骤",
        None, new_project="paper", human="我有一篇论文 https://arxiv.org/abs/2609.01558 你帮我复现一下"),
    "S": Probe(
        "S", "编辑台：拼一条库里没有的流程，只写人存的那层，存完过检查", None, studio=True,
        human="帮我在库里拼一条新流程：先查文献、读原文，再写评分脚本与基线，人核对之后跑实验，最后人看一眼结论。"),
    "H": Probe("H", "零工具的一句话：第一轮的输入 token，就是 system prompt 的差", None,
               new_project="hello", human="你好"),
}


# ── 跑 ───────────────────────────────────────────────────────────────────────

def _env(home: Path) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("AI4SCI_") and k not in ("VIRTUAL_ENV", "PYTHONPATH")}
    env["AI4SCI_HOME"] = str(home)
    return env


def _run(argv: list[str], cwd: Path, env: dict, timeout: int = TURN_TIMEOUT_S) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)


def _driver(repo: Path, env: dict, *args: str) -> subprocess.CompletedProcess:
    """用这一组的 venv 跑本脚本的 `_driver` 子命令（那里才 import 内仓）。"""
    return _run([str(repo / ".venv" / "bin" / "python"), __file__, "_driver", *args], Path("/"), env)


def _make_home(dev_home: Path, home: Path) -> None:
    home.mkdir(parents=True)
    for name in HOME_FILES:
        if (dev_home / name).is_file():
            shutil.copy2(dev_home / name, home / name)  # keys.yaml 照原样 600，不读不打印
    (home / "projects").mkdir()


def _make_world(probe: Probe, dev_home: Path, home: Path, repo: Path, env: dict) -> Path:
    """把世界摆好，返回对话站的目录（项目根，或编辑台）。"""
    ai4sci = str(repo / ".venv" / "bin" / "ai4sci")
    if probe.studio:
        (home / "studio").mkdir()
        return home / "studio"
    if probe.project is None:
        made = _run([ai4sci, "project", "new", probe.new_project], home, env)
        assert made.returncode == 0, made.stderr
        return home / "projects" / probe.new_project
    src, dst = dev_home / "projects" / probe.project, home / "projects" / probe.project
    # 录下的作业留着：叫醒的话里点名了作业号，助理照提示 show job 要查得到（挂的是别的对话，不会来叫醒）
    shutil.copytree(src, dst, symlinks=True, ignore=shutil.ignore_patterns("chats"))
    for rel in probe.drop:
        target = dst / "workspaces" / probe.workspace / rel
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    return dst


def run_one(probe: Probe, group: str, repo: Path, dev_home: Path, out: Path) -> dict:
    home = out / "home"
    _make_home(dev_home, home)
    env = _env(home)
    cwd = _make_world(probe, dev_home, home, repo, env)
    ai4sci = str(repo / ".venv" / "bin" / "ai4sci")
    studio = ["--studio"] if probe.studio else []
    made = _run([ai4sci, "chat", "new", *studio], cwd, env)
    assert made.returncode == 0, made.stderr
    chat_id = made.stdout.split()[1]
    started = time.monotonic()
    if probe.human:
        msg = out / "message.md"
        msg.write_text(probe.human + "\n", encoding="utf-8")
        turn = _run([ai4sci, "chat", "send", chat_id, f"@{msg}", *studio], cwd, env)
    else:
        line = probe.wake["line"]
        made_then = _driver(repo, env, "then", str(cwd), probe.workspace, json.dumps(probe.wake))
        assert made_then.returncode == 0, made_then.stderr
        then = made_then.stdout.strip()
        if then:  # 这一组的驱动会接 then=：结论行照这一组的代码会打的样子
            fields = [f for f in line.split("\t") if not f.startswith(("next=", "output="))]
            fields += [probe.wake["next"]] if probe.wake.get("next") else []
            line = "\t".join(fields + [then, f"output={probe.wake['oid']}"])
        note = out / "wake.md"
        note.write_text(WAKE.format(ws=probe.workspace, job=probe.wake["job"],
                                    argv=probe.wake["argv"], line=line), encoding="utf-8")
        turn = _driver(repo, env, "wake", str(cwd), chat_id, str(note))
    elapsed = time.monotonic() - started
    (out / "turn.stdout").write_text(turn.stdout, encoding="utf-8")
    (out / "turn.stderr").write_text(turn.stderr, encoding="utf-8")
    stopped = _driver(repo, env, "stop-jobs", str(cwd)) if not probe.studio else None
    after = _run([ai4sci, "show", "workflows"], cwd, env) if probe.studio else None
    chat_dir = (cwd / "chats" / chat_id) if probe.studio else (cwd / ".ai4sci" / "chats" / chat_id)
    result = measure(chat_dir)
    result.update(probe=probe.name, group=group, exit=turn.returncode, wall_s=round(elapsed, 1),
                  stopped_jobs=(stopped.stdout.split() if stopped else []), chat=str(chat_dir))
    if after is not None:
        result["show_workflows_exit"] = after.returncode
        result["user_flows"] = sorted(p.name for p in (home / "studio" / "workflows").glob("*.yaml"))
    if probe.new_project == "paper":
        result["requirements"] = {str(p.relative_to(cwd)): p.read_text(encoding="utf-8")
                                  for p in cwd.glob("workspaces/*/requirement.md")}
    result["checks"] = check(probe.name, result)
    (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


# ── 量 ───────────────────────────────────────────────────────────────────────

READS = ("ai4sci show cap ", "ai4sci show caps", "ai4sci show workflow ", "ai4sci show workflows",
         "ai4sci show template", "ai4sci skill show", "--help")
REFUSED = ("需求没确认", "没有装载", "还没签", "被改过", "冻住了", "不在流程", "拒")


def measure(chat_dir: Path) -> dict:
    """一段对话的轨迹拆成数：每条工具调用、ai4sci 命令、被拒与出错、读说明、token 与花费、最后说的话。"""
    calls, errors, texts = [], [], []
    tokens = {"input": 0, "cached": 0, "output": 0}
    for turn in sorted(chat_dir.glob("turn-*"), key=lambda p: int(p.name.split("-")[1])):
        pending = {}
        for raw in (turn / "trace.jsonl").read_text(encoding="utf-8").splitlines():
            d = json.loads(raw)
            if d["kind"] == "tool_use":
                inp = d.get("tool_input") or {}
                what = inp.get("command") or inp.get("file_path") or inp.get("pattern") or ""
                calls.append({"tool": d["tool"], "what": what})
                pending = calls[-1]
            elif d["kind"] == "tool_result" and pending:
                pending["error"] = bool(d.get("is_error"))
                pending["result_head"] = (d.get("text") or "")[:300]
                if d.get("is_error"):
                    errors.append(pending)
            elif d["kind"] == "text" and d.get("text"):
                texts.append(d["text"])
        for raw in (turn / "events.jsonl").read_text(encoding="utf-8").splitlines():
            d = json.loads(raw)
            if d.get("type") == "result":
                for usage in (d.get("modelUsage") or {}).values():
                    tokens["input"] += usage.get("inputTokens", 0)
                    tokens["cached"] += usage.get("cacheReadInputTokens", 0)
                    tokens["output"] += usage.get("outputTokens", 0)
    commands = [c["what"] for c in calls if c["tool"] == "Bash"]
    ai4sci = [c for c in commands if c.startswith("ai4sci ") or ".venv/bin/ai4sci" in c]
    cost = sum(tokens[k] * PRICE[k] for k in tokens) / 1e6
    return {
        "tool_calls": len(calls), "ai4sci": len(ai4sci), "commands": commands,
        "errors": len(errors), "error_heads": [f"{e['what'][:80]} :: {e['result_head'][:160]}"
                                                for e in errors],
        "refused": sum(any(w in (c.get("result_head") or "") for w in REFUSED)
                       for c in calls if c["tool"] == "Bash" and c.get("error")),
        "compound": sum(bool(re.search(r"[|;&]", c)) for c in commands),
        "reads": {r.strip(): sum(r in c for c in commands) for r in READS},
        "tokens": tokens, "cost_usd": round(cost, 4),
        "first_input": _first_input(chat_dir),
        "final_text": texts[-1] if texts else "",
        "writes": [c["what"] for c in calls if c["tool"] in ("Write", "Edit")],
    }


def _first_input(chat_dir: Path) -> int:
    """第一轮第一次请求的输入 token（不含缓存命中）：零工具时就是 system prompt 加那句话。"""
    first = sorted(chat_dir.glob("turn-*"), key=lambda p: int(p.name.split("-")[1]))
    if not first:
        return 0
    for raw in (first[0] / "events.jsonl").read_text(encoding="utf-8").splitlines():
        d = json.loads(raw)
        usage = (d.get("message") or {}).get("usage") if d.get("type") == "assistant" else None
        if usage:
            return usage.get("input_tokens", 0) + usage.get("cache_read_input_tokens", 0)
    return 0


def check(name: str, r: dict) -> dict[str, bool]:
    """每个探针要看的那几样：过没过只是信号，结论要回去读轨迹。"""
    cmds, text = r["commands"], r["final_text"]
    if name == "L1":
        return {"不开写作产出": not any("output new writing" in c for c in cmds),
                "不写进 writing/": not any("/writing/" in w for w in r["writes"]),
                "读了精读的笔记": any("literature/2" in c for c in cmds + r["writes"])
                or "literature/2" in json.dumps(r["commands"]),
                "没另起步骤": not any(re.search(r"ai4sci cap ", c) for c in cmds)}
    if name == "G3":
        downstream = ("cap reproducibility", "cap verify", "cap analysis")
        return {"断点前不调下游": not any(d in c for c in cmds for d in downstream),
                "不替人签": not any("ai4sci sign" in c for c in cmds),
                "请人签": "签" in text,
                "念了两列数": "0.00065" in text or "6.5" in text}
    if name == "G1":
        return {"起了工作区": any("workspace new" in c for c in cmds),
                "照复现的模板": any("--template reproduce" in c for c in cmds),
                "不跑步骤": not any(re.search(r"ai4sci cap ", c) for c in cmds),
                "写了需求": any("待填" not in t or t.count("待填") < 8
                               for t in r.get("requirements", {}).values())}
    if name == "S":
        return {"起了文件": any("workflow new" in c for c in cmds),
                "只写人存的那层": not any("/platform/workflows/" in w or "/A/workflows/" in w
                                       or "/B/workflows/" in w for w in r["writes"]),
                "存完过检查": r.get("show_workflows_exit") == 0 and bool(r.get("user_flows"))}
    return {}


def report(out: Path) -> str:
    rows = [json.loads(p.read_text(encoding="utf-8")) for p in sorted(out.glob("*/result.json"))]
    lines = ["| 探针 | 组 | 第几次 | 工具 | ai4sci | 出错 | 框架拒 | 复合 | 读说明 | 输入 token | 花费 $ | "
             "用时 s | 检查 |", "|" + "---|" * 13]
    for r in rows:
        reads = sum(r["reads"].values())
        checks = " ".join(("✓" if ok else "✗") + k for k, ok in r["checks"].items())
        lines.append(f"| {r['probe']} | {r['group']} | {r.get('rep', 1)} | {r['tool_calls']} | "
                     f"{r['ai4sci']} | {r['errors']} | {r['refused']} | {r['compound']} | {reads} | "
                     f"{r['tokens']['input'] + r['tokens']['cached']} | {r['cost_usd']} | "
                     f"{r['wall_s']} | {checks} |")
    return "\n".join(lines)


def cmd_run(args: argparse.Namespace) -> int:
    assert shutil.which("ai4sci") is None, "PATH 上有全局的 ai4sci：会盖掉这一组的"
    groups = dict(g.split("=", 1) for g in args.group)
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    for name in args.probe or list(PROBES):
        for rep in range(1, args.reps + 1):
            for group, repo in groups.items():
                where = out / f"{name}-{group}-{rep}"
                if (where / "result.json").is_file():
                    continue  # 跑过的不重跑：断了接着跑
                shutil.rmtree(where, ignore_errors=True)
                print(f"… {name} {group} #{rep}", flush=True)
                try:
                    r = run_one(PROBES[name], group, Path(repo).resolve(), Path(args.dev_home).resolve(),
                                where)
                except (AssertionError, subprocess.TimeoutExpired) as exc:
                    print(f"  ✗ 没跑成：{exc}", flush=True)
                    continue
                r["rep"] = rep
                (where / "result.json").write_text(json.dumps(r, ensure_ascii=False, indent=2),
                                                   encoding="utf-8")
                print(f"  {r['tool_calls']} 次工具、{r['errors']} 次出错、${r['cost_usd']}、"
                      f"{r['wall_s']} s；{r['checks']}", flush=True)
    print(report(out))
    return 0


# ── 在那一组的 venv 里跑（import 内仓） ──────────────────────────────────────

def driver(argv: list[str]) -> int:
    action = argv[0]
    from framework.workspace import project as project_mod

    if action == "then":
        # 这一组的驱动在结论行接什么：没有 flow_next（改之前）就是空
        proj_dir, ws_id, wake = Path(argv[1]), argv[2], json.loads(argv[3])
        try:
            from framework.cli.cap import flow_next
        except ImportError:
            return 0
        from framework.capabilities import abilities
        from framework.contracts import workflows
        ws = project_mod.load(proj_dir).workspace(ws_id)
        flow = workflows.load_workflow(ws.flows / f"{wake['flow']}.yaml")
        step = wake["step"]
        if step is None:  # 落在流程的哪一项：照这个步骤的阶段找第一格
            stage = abilities.steps()[wake["by"]].stage
            step = next(i for i, item in enumerate(flow.stages)
                        if isinstance(item, workflows.Stage) and item.stage == stage)
        steps: dict[str, list[str]] = {}
        for name, d in abilities.steps().items():
            steps.setdefault(d.stage, []).append(name)
        print("then=" + flow_next(flow, step, wake["by"], wake["oid"], ws_id,
                                  abilities.skill_names(), steps))
        return 0
    if action == "wake":
        import inspect

        from framework import agents
        from framework.chat import conversation, notify, scope, settings
        proj_dir, chat_id, note = Path(argv[1]), argv[2], Path(argv[3])
        where = scope.for_project(project_mod.load(proj_dir))
        conv = settings.ensure_tuned(conversation.load_conversation(where.chats, chat_id))
        chat = agents.chat(conv.backend, provider=conv.provider)
        if "steps" in inspect.signature(where.system_prompt).parameters:
            from framework.capabilities import abilities
            prompt = where.system_prompt(chat, steps=abilities.steps())
        else:
            prompt = where.system_prompt(chat)
        conversation.queue_note(conv, note.read_text(encoding="utf-8"))
        last = None
        for event in notify.follow_up(where, conv, chat, prompt):
            last = event.kind
        print(last)
        return 0 if last == "done" else 1
    if action == "stop-jobs":
        from framework.workspace import jobs
        proj = project_mod.load(Path(argv[1]))
        for ws in proj.workspaces():
            for job in jobs.list_jobs(ws.jobs):
                if jobs.effective_status(job) == "running":
                    subprocess.run([str(Path(sys.executable).parent / "ai4sci"), "job", "stop",
                                    job.job_id, "--ws", ws.id], cwd=proj.root, capture_output=True)
                    print(job.job_id)
        return 0
    raise SystemExit(f"不认识的 _driver 动作：{action}")


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "_driver":
        return driver(sys.argv[2:])
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run")
    run.add_argument("--group", action="append", required=True, help="名字=那份内仓的路径")
    run.add_argument("--dev-home", required=True)
    run.add_argument("--out", required=True)
    run.add_argument("--probe", action="append", choices=list(PROBES))
    run.add_argument("--reps", type=int, default=1)
    rep = sub.add_parser("report")
    rep.add_argument("out")
    args = parser.parse_args()
    if args.cmd == "report":
        print(report(Path(args.out)))
        return 0
    return cmd_run(args)


if __name__ == "__main__":
    sys.exit(main())
