# /// script
# requires-python = ">=3.12"
# dependencies = ["matplotlib==3.10.*"]
# ///
"""公众号稿（#193）的三张数据图：GUA 时间轴、复现结果、十六天。

跑法（外层仓根）：uv run scripts/articles/2026-0929-first-release/charts.py
数据全部抄自出处，出处写在每个函数的 docstring 里；改数先改出处。
配色取平台 docs/DESIGN.md 的 tokens：靛 = AI 在动，琥珀 = 人确认，铜绿 = 通过；底色用白，不用平台的纸色。
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

OUT = Path("materials/articles/2026-0929-first-release/figures")  # 出图落本机（gitignore），upload.py 传 COS
DPI = 360  # 6 英寸宽 → 2160 px

BG = "#FFFFFF"  # 白底：公众号正文也是白底，图与正文融成一片
INK = "#1C2230"
MUTED = "#5B6270"
PRIMARY = "#2F4BC9"
PRIMARY_SOFT = "#DCE2F8"
OK = "#1F7A6D"
WAIT = "#B8741A"
LINE = "#D5D9E0"

SANS = "Hiragino Sans GB"
SERIF = "Songti SC"


def _setup() -> None:
    have = {f.name for f in font_manager.fontManager.ttflist}
    missing = {SANS, SERIF} - have
    if missing:
        raise SystemExit(f"缺字体：{sorted(missing)}（本脚本按 macOS 自带字体写）")
    plt.rcParams.update({
        "font.family": SANS,
        "font.size": 12,
        "axes.unicode_minus": False,
        "figure.facecolor": BG,
        "axes.facecolor": BG,
        "savefig.facecolor": BG,
        "text.color": INK,
        "axes.labelcolor": MUTED,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
    })


def _title(fig, title: str, sub: str) -> None:
    fig.text(0.06, 0.975, title, fontfamily=SERIF, fontweight="bold", fontsize=18, va="top")
    fig.text(0.06, 0.935, sub, fontsize=11, color=MUTED, va="top")


def _spread(ys: list[float], gap: float) -> list[float]:
    """标签按时间排好后往下推，保证相邻两条至少隔 gap，引线接回真实时刻。"""
    out: list[float] = []
    for y in ys:
        out.append(max(y, out[-1] + gap) if out else y)
    return out


def gua_timeline() -> None:
    """出处：docs/cases/gua-pinn-reproduction/README.md「时间线」；需求确认 12:25 取自工作区的 requirement.lock。"""
    def m(hhmm: str) -> float:
        h, mi = map(int, hhmm.split(":"))
        return (h - 12) * 60 + mi - 15  # 12:15 起算的分钟

    gap_from, gap_to, gap_len = m("12:48"), m("15:23"), 12.0

    def y(hhmm: str) -> float:  # 分段压缩：GPU 那 2 小时 35 分压成 12 格
        t = m(hhmm)
        if t <= gap_from:
            return t
        if t >= gap_to:
            return gap_from + gap_len + (t - gap_to)
        return gap_from + gap_len * (t - gap_from) / (gap_to - gap_from)

    human = [
        ("12:18", "发送一句话与一个链接\n“你帮我复现一下”"),
        ("12:25", "“都听你的”\n提供一台 AutoDL\n确认需求"),
        ("15:26", "签字：复现结果核对"),
        ("15:43", "签字：验收"),
    ]
    ai = [
        ("12:19", "解析论文 PDF，联网查阅代码仓库\n撰写需求初稿，列出待定的四个问题"),
        ("12:25", "接入 RTX 4090，登记镜像环境"),
        ("12:26", "取用“论文复现”workflow\n拉取官方代码，任务提交至 4090"),
        ("12:33", "发现随机种子误写为 42–46\n按论文改回 0–4"),
        ("12:35", "服务器缺少九个依赖包"),
        ("12:43", "在服务器上补齐环境，继续运行"),
        ("15:25", "论文值与复现值并列\n暂停等待人工核对"),
        ("15:33", "撰写复现性分析，自查重写\n数字核对拦下两版\n第 4 版三项检查全部通过"),
        ("15:43", "流程完成，提醒关机以节省费用"),
    ]

    fig = plt.figure(figsize=(6, 9.6), dpi=DPI)
    _title(fig, "3 小时 25 分，一次全自动复现", "2026-09-21 · 左侧为人的操作，右侧为 AI 的操作；全程人工签字两次")
    ax = fig.add_axes([0.02, 0.03, 0.96, 0.86])
    top, bottom = y("12:15"), y("15:47")
    ax.set_ylim(bottom, top)
    ax.set_xlim(-1, 1)
    ax.axis("off")
    X0 = -0.16  # 轴线偏左：AI 那侧字多

    ax.plot([X0, X0], [top, bottom], color=LINE, lw=2, zorder=1)
    # GPU 段：一整条靛色，两头画断轴记号
    g0, g1 = y("12:46"), y("15:25")
    ax.add_patch(plt.Rectangle((X0 - 0.035, g0), 0.07, g1 - g0, color=PRIMARY, zorder=2))
    for yy in (y("12:52"), y("15:18")):
        ax.plot([X0 - 0.07, X0 + 0.07], [yy - 0.6, yy + 0.6], color=BG, lw=4, zorder=3)
    ax.text(X0 + 0.1, (g0 + g1) / 2, "RTX 4090 连续训练\n2 小时 40 分\n5 个种子 × 2 种方法",
            fontsize=12.5, fontweight="bold", color=PRIMARY, va="center")

    for tick in ("12:15", "12:30", "12:45", "15:30", "15:45"):
        ax.text(X0, y(tick), f" {tick} ", fontsize=8.5, color=MUTED, ha="center", va="center",
                bbox={"boxstyle": "round,pad=0.25", "fc": BG, "ec": "none"}, zorder=4)

    def lane(events, side: int, color: str, weight: str) -> None:
        ys = [y(t) for t, _ in events]
        labels_y = _spread(ys, 4.6)
        for (t, text), y0, y1 in zip(events, ys, labels_y, strict=True):
            x_dot, x_lab = X0, X0 + 0.1 * side
            ax.plot([x_dot, x_dot + (x_lab - x_dot) * 0.8], [y0, y1], color=color, lw=0.8, alpha=0.5, zorder=2)
            ax.scatter([x_dot], [y0], s=46, color=color, zorder=5, edgecolors=BG, linewidths=1.2)
            ax.text(x_lab, y1, f"{t}  {text}", fontsize=10.5, color=INK, fontweight=weight,
                    ha="left" if side > 0 else "right", va="center", linespacing=1.35)

    lane(human, -1, WAIT, "bold")  # 人的字粗，一眼数得出几次
    lane(ai, 1, PRIMARY, "normal")
    fig.savefig(OUT / "chart-gua-timeline.png")
    plt.close(fig)


def gua_results() -> None:
    """出处：docs/cases/gua-pinn-reproduction/README.md「论文值 vs 我们的值」两张表（表 8 · Burgers · 2-loss · 相对 L2 误差）。"""
    rows = [
        # 方法, 论文均值, 论文 σ, 我们五个种子（0–4）
        ("ConFIG", 1.74e-3, 3.38e-4, [2.33e-3, 2.16e-3, 2.00e-3, 1.66e-3, 1.54e-3]),
        ("ConFIG + GUA", 6.50e-4, 1.27e-4, [7.69e-4, 6.70e-4, 6.29e-4, 5.74e-4, 1.02e-3]),
    ]
    ours_mean = [1.94e-3, 7.33e-4]

    fig = plt.figure(figsize=(6, 6.2), dpi=DPI)
    _title(fig, "复现结果：两行都落在论文的误差范围内", "Burgers 方程 · 2-loss · 相对 L2 误差（数值越低越好，对数坐标）")
    ax = fig.add_axes([0.14, 0.1, 0.82, 0.74])
    ax.set_yscale("log")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(LINE)

    offsets = [-0.14, -0.07, 0.0, 0.07, 0.14]
    for i, (name, mu, sd, seeds) in enumerate(rows):
        ax.add_patch(plt.Rectangle((i - 0.36, mu - 2 * sd), 0.72, 4 * sd, color=PRIMARY_SOFT, zorder=1))
        ax.plot([i - 0.36, i + 0.36], [mu, mu], color=MUTED, lw=1.6, ls=(0, (4, 3)), zorder=2)
        ax.scatter([i + o for o in offsets], seeds, s=42, color=PRIMARY, alpha=0.55, zorder=3,
                   edgecolors="none")
        ax.plot([i - 0.2, i + 0.2], [ours_mean[i], ours_mean[i]], color=PRIMARY, lw=3.2, zorder=4)
        ax.text(i + 0.38, mu, f"论文 {mu:.2e}", fontsize=9.5, color=MUTED, va="center")
        ax.text(i + 0.38, ours_mean[i] * 1.12, f"复现 {ours_mean[i]:.2e}", fontsize=9.5,
                color=PRIMARY, fontweight="bold", va="bottom")

    ax.set_xticks([0, 1], [r[0] for r in rows], fontsize=12, color=INK)
    ax.set_xlim(-0.6, 1.85)
    ax.set_ylim(3.2e-4, 3.3e-3)
    ax.set_ylabel("相对 L2 误差")
    ticks = [4e-4, 6e-4, 1e-3, 2e-3, 3e-3]
    ax.set_yticks(ticks, [f"{t:.0e}".replace("e-0", "e-") for t in ticks], fontsize=9)
    ax.minorticks_off()
    ax.annotate("", xy=(1.0, 7.33e-4), xytext=(0.0, 1.94e-3),
                arrowprops={"arrowstyle": "-|>", "color": OK, "lw": 1.6,
                            "connectionstyle": "arc3,rad=-0.25"})
    ax.text(1.42, 1.42e-3, "加上 GUA，误差降低\n论文 62.6% · 复现 62.2%", fontsize=11.5,
            color=OK, fontweight="bold", ha="center", va="center")
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=PRIMARY_SOFT),
        plt.Line2D([], [], color=MUTED, lw=1.6, ls=(0, (4, 3))),
        plt.Line2D([], [], color=PRIMARY, marker="o", lw=0, alpha=0.55),
        plt.Line2D([], [], color=PRIMARY, lw=3.2),
    ]
    ax.legend(handles, ["论文均值 ± 2σ", "论文均值", "复现：五个种子", "复现均值"], loc="lower left",
              fontsize=9, frameon=False)
    fig.savefig(OUT / "chart-gua-results.png")
    plt.close(fig)


def sixteen_days() -> None:
    """出处：两仓 origin/main 的 git log（--no-merges，按作者日期，2026-09-29 取）；版本日期取自各 tag 所在提交（git log -1 <tag>）；
    事件取自纲领「变更记录」与 docs/cases/。"""
    outer = {8: 15, 9: 4, 10: 16, 15: 2, 16: 19, 17: 7, 18: 10, 19: 9, 20: 7, 21: 5, 22: 9, 23: 14}
    inner = {8: 5, 10: 10, 11: 1, 15: 4, 16: 20, 17: 29, 18: 33, 19: 30, 20: 16, 21: 6, 22: 29, 23: 20}
    events = {
        8: "首篇调研 · 两个仓库 v0.1.0",
        9: "开源项目代码级深读",
        10: "纲领建档：9 条原则",
        16: "能力可自由装配、agent 可替换",
        17: "v0.2.0 · 工作区与两位助理",
        20: "首次真实课题演练",
        21: "GUA 复现验收签字",
        22: "Codex 全面适配",
        23: "v1.0.0 · v1.0.1 发布",
    }
    days = [date(2026, 9, 8) + timedelta(d) for d in range(16)]
    o = [outer.get(d.day, 0) for d in days]
    n = [inner.get(d.day, 0) for d in days]

    fig = plt.figure(figsize=(6, 8.4), dpi=DPI)
    _title(fig, "十六天，从 0.1 到 1.0", f"每日提交数 · 两个仓库共计 {sum(o) + sum(n)} 次提交、146 条 issue")
    ax = fig.add_axes([0.13, 0.04, 0.84, 0.83])
    ys = list(range(len(days)))
    ax.barh(ys, n, color=PRIMARY, height=0.62, label="平台代码仓")
    ax.barh(ys, o, left=n, color=PRIMARY_SOFT, height=0.62, label="外层文档仓")
    ax.set_yticks(ys, [d.strftime("%m-%d") for d in days], fontsize=10)
    ax.invert_yaxis()
    ax.set_xlim(0, 95)
    ax.xaxis.set_visible(False)
    for spine in ("top", "right", "bottom"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color(LINE)
    for yy, (a, b) in enumerate(zip(n, o, strict=True)):
        if a + b:
            ax.text(a + b + 1, yy, str(a + b), va="center", fontsize=9, color=MUTED)
    for yy, d in enumerate(days):
        if d.day in events:
            major = d.day in (8, 23)
            ax.text(n[yy] + o[yy] + 7, yy, events[d.day], va="center", fontsize=10.5,
                    color=OK if major else INK, fontweight="bold" if major else "normal")
    ax.legend(loc="center right", fontsize=9.5, frameon=False)
    fig.savefig(OUT / "chart-sixteen-days.png")
    plt.close(fig)


def main() -> None:
    _setup()
    OUT.mkdir(parents=True, exist_ok=True)
    gua_timeline()
    gua_results()
    sixteen_days()
    print("\n".join(sorted(p.name for p in OUT.glob("chart-*.png"))))


if __name__ == "__main__":
    main()
