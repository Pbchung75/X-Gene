"""Figure 3 (option B): (a) rule-set reduction on a log scale (mean of 12 datasets, three selectors);
(b) test coverage and (c) test active-rule fidelity per dataset for all three selectors (k_min = 4).
Data: table4_per_dataset.csv (per-dataset values of Table 4 / Supplementary Table S1).
Run:  py fig3_reduction_quality_B.py"""
import sys
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

FONT = "Arial" if sys.platform.startswith("win") else "Liberation Sans"
mpl.rcParams.update({"font.family": FONT, "mathtext.fontset": "stixsans", "pdf.fonttype": 42, "svg.fonttype": "none",
                     "font.size": 7.5, "axes.linewidth": 0.6, "xtick.major.width": 0, "ytick.major.width": 0.6,
                     "ytick.major.size": 2.5, "ytick.minor.size": 1.5, "ytick.minor.width": 0.4})
INK, MUTED, GRID = "#1d1d1d", "#6b6b6b", "#e6e6e6"
COL = {"DT": "#3a6fb8", "RF": "#d9792b"}
MK = {"mRMR-50": "o", "mRMR-75": "s", "Boruta": "^"}
SEL = ["mRMR-50", "mRMR-75", "Boruta"]
TFS = 7.6
q = lambda v, p: Decimal(str(v)).quantize(Decimal(p), ROUND_HALF_UP)

COUNTS = {"DT": {"mRMR-50": (9.17, 5.42, 5.42), "mRMR-75": (9.00, 5.25, 5.25), "Boruta": (8.50, 4.92, 4.92)},
          "RF": {"mRMR-50": (1714.75, 805.42, 85.00), "mRMR-75": (1707.83, 827.25, 85.00), "Boruta": (1674.75, 854.67, 84.25)}}
BBAR = 85.00
D = pd.read_csv("table4_per_dataset.csv")


def style(ax):
    ax.grid(axis="y", color=GRID, lw=0.5, zorder=0); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("bottom", "left"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(labelsize=7, colors=INK)


def swarm(vals, x0, width=0.36, step=0.018, dx=0.085):
    order = np.argsort(vals); xs = np.zeros(len(vals)); placed = []
    for i in order:
        v = vals[i]; k = sum(1 for p in placed if abs(p - v) < step); placed.append(v)
        xs[i] = x0 + max(-width, min(width, ((k + 1) // 2) * dx * (1 if k % 2 else -1)))
    return xs


fig = plt.figure(figsize=(122 / 25.4, 92 / 25.4))
gs = fig.add_gridspec(2, 2, width_ratios=[0.78, 1.62], height_ratios=[1, 1], wspace=0.30, hspace=0.42,
                      left=0.11, right=0.99, top=0.94, bottom=0.12)

# ---------------- (a) slope on log scale ----------------
ax = fig.add_subplot(gs[:, 0])
X = [0, 1, 2]
for m in ("DT", "RF"):
    for s, (raw, pas, ret) in COUNTS[m].items():
        dx = {"mRMR-50": -0.11, "mRMR-75": 0.0, "Boruta": 0.11}[s]
        xs = [x + dx for x in X]
        ax.plot(xs, [raw, pas, ret], color=COL[m], lw=0.8, alpha=0.8, zorder=3)
        ax.scatter(xs, [raw, pas, ret], s=20, marker=MK[s], color=COL[m], ec="white", lw=0.5, zorder=4)
for m, dy in (("RF", 1.35), ("DT", 0.70)):
    for k in range(3):
        vals = [COUNTS[m][s][k] for s in COUNTS[m]]
        lo, hi = min(vals), max(vals)
        txt = (f"{int(q(lo, '1')):,}–{int(q(hi, '1')):,}" if m == "RF" else f"{q(lo, '0.1')}–{q(hi, '0.1')}")
        ax.text(X[k] + ((0.30 if m == "RF" else 0.12) if k == 0 else 0), hi * dy if m == "RF" else lo * dy, txt,
                fontsize=6.6, color=INK, ha="center", va="bottom" if m == "RF" else "top")
ax.hlines(BBAR, 1.62, 2.38, color=INK, lw=0.8, ls=(0, (3, 2)), zorder=2)
ax.annotate(r"mean budget $\bar B=85$", xy=(2.3, BBAR), xytext=(1.35, 26), fontsize=6.4, color=INK,
            ha="center", va="center", arrowprops=dict(arrowstyle="-", lw=0.5, color=MUTED, shrinkA=1, shrinkB=1))
ax.set_yscale("log"); ax.set_ylim(1.5, 6000)
ax.set_yticks([2, 10, 100, 1000])
ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, p: f"{v:,.0f}"))
ax.set_xticks(X); ax.set_xticklabels(["Raw", "Passed", "Retained"], fontsize=7)
ax.set_xlim(-0.35, 2.5)
ax.set_ylabel("Mean rules per dataset (log)", fontsize=7)
ax.set_title("(a) Rule-set reduction", fontsize=TFS, loc="left", fontweight="bold", pad=3)
style(ax)


# ---------------- (b), (c) grouped strips ----------------
def strip_panel(ax, key, title, ylim, yticks):
    for g, s in enumerate(SEL):
        d = D[D.selector == s].reset_index(drop=True)
        for j, m in enumerate(("DT", "RF")):
            x0 = g * 2.6 + j
            v = d[f"{m.lower()}_{key}"].to_numpy()
            xs = swarm(v, x0)
            ax.scatter(xs, v, s=10, marker=MK[s], color=COL[m], ec="white", lw=0.35, zorder=4)
            mu = v.mean()
            ax.plot([x0 - 0.38, x0 + 0.38], [mu, mu], color=INK, lw=0.9, zorder=5)
            ax.text(x0, ylim[0] + 0.012 * (ylim[1] - ylim[0]), f"{q(mu, '0.001')}", fontsize=5.9, ha="center",
                    va="bottom", color=INK, fontweight="bold")
        ax.text(g * 2.6 + 0.5, ylim[1] + 0.005, s, fontsize=6.6, ha="center", va="bottom", color=MUTED)
        if g < 2:
            ax.axvline(g * 2.6 + 1.8, color=GRID, lw=0.8, zorder=1)
    ax.set_xticks([g * 2.6 + j for g in range(3) for j in range(2)])
    ax.set_xticklabels(["DT", "RF"] * 3, fontsize=6.8)
    ax.set_xlim(-0.6, 2 * 2.6 + 1.6); ax.set_ylim(*ylim); ax.set_yticks(yticks)
    ax.set_title(title, fontsize=TFS, loc="left", fontweight="bold", pad=10)
    style(ax)


strip_panel(fig.add_subplot(gs[0, 1]), "cov", "(b) Test coverage", (0.25, 1.06), [0.4, 0.6, 0.8, 1.0])
strip_panel(fig.add_subplot(gs[1, 1]), "fidp", "(c) Test active-rule fidelity", (0.38, 1.06), [0.4, 0.6, 0.8, 1.0])

H = [Line2D([], [], color=COL["DT"], lw=1, marker="o", ms=3.5, label="DT"),
     Line2D([], [], color=COL["RF"], lw=1, marker="o", ms=3.5, label="RF"),
     Line2D([], [], color=MUTED, ls="", marker="o", ms=3.5, label="mRMR-50"),
     Line2D([], [], color=MUTED, ls="", marker="s", ms=3.5, label="mRMR-75"),
     Line2D([], [], color=MUTED, ls="", marker="^", ms=3.8, label="Boruta"),
     Line2D([], [], color=INK, lw=0.9, label="mean of 12 datasets (value at bottom)")]
fig.legend(handles=H, loc="lower center", ncol=6, fontsize=6.4, frameon=False, handlelength=1.3,
           handletextpad=0.3, columnspacing=0.8, bbox_to_anchor=(0.53, -0.005))
for ext, kw in [("pdf", {}), ("svg", {}), ("png", {"dpi": 600})]:
    fig.savefig(f"fig3_reduction_quality_B.{ext}", **kw)
print("ok")
