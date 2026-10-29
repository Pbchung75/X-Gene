"""Figure 2 (slope variant): (a) rule counts across stages on a log scale (k_min = 4, mean of 12 datasets);
(b) per-dataset test coverage and fid+ strip plots (mRMR-50, Table B).  Run:  py fig2_slope.py"""
import sys
from decimal import Decimal, ROUND_HALF_UP
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

FONT = "Arial" if sys.platform.startswith("win") else "Liberation Sans"
mpl.rcParams.update({"font.family": FONT, "mathtext.fontset": "stixsans", "pdf.fonttype": 42, "svg.fonttype": "none",
                     "font.size": 8.5, "axes.linewidth": 0.6, "xtick.major.width": 0, "ytick.major.width": 0.6,
                     "ytick.major.size": 2.5, "ytick.minor.size": 1.5, "ytick.minor.width": 0.4})
INK, MUTED, GRID = "#1d1d1d", "#6b6b6b", "#e6e6e6"
COL = {"DT": "#3a6fb8", "RF": "#d9792b"}
MK = {"mRMR-50": "o", "mRMR-75": "s", "Boruta": "^"}
TFS = 7.2                                   # panel-title size (all three panels)
q = lambda v, p: Decimal(str(v)).quantize(Decimal(p), ROUND_HALF_UP)

COUNTS = {"DT": {"mRMR-50": (9.17, 5.42, 5.42), "mRMR-75": (9.00, 5.25, 5.25), "Boruta": (8.50, 4.92, 4.92)},
          "RF": {"mRMR-50": (1714.75, 805.42, 85.00), "mRMR-75": (1707.83, 827.25, 85.00), "Boruta": (1674.75, 854.67, 84.25)}}
BBAR = 85.00
TB = pd.read_csv("table_B_metrics_audit.csv"); TB["gse"] = "GSE" + TB.dataset.astype(str)


def style(ax):
    ax.grid(axis="y", color=GRID, lw=0.5, zorder=0); ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("bottom", "left"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(labelsize=7.6, colors=INK)


def swarm(vals, x0, width=0.32, step=0.022, dx=0.06):
    order = np.argsort(vals); xs = np.zeros(len(vals)); placed = []
    for i in order:
        v = vals[i]; k = sum(1 for p in placed if abs(p - v) < step); placed.append(v)
        xs[i] = x0 + max(-width, min(width, ((k + 1) // 2) * dx * (1 if k % 2 else -1)))
    return xs


fig = plt.figure(figsize=(122 / 25.4, 60 / 25.4))
gs = fig.add_gridspec(1, 3, width_ratios=[1.18, 1, 1.2], wspace=0.32, left=0.105, right=0.99, top=0.89, bottom=0.2)

# ---------- (a) slope on log scale ----------
ax = fig.add_subplot(gs[0, 0])
X = [0, 1, 2]
for m in ("DT", "RF"):
    for s, (raw, pas, ret) in COUNTS[m].items():
        dx = {"mRMR-50": -0.11, "mRMR-75": 0.0, "Boruta": 0.11}[s]
        xs = [x + dx for x in X]
        ax.plot(xs, [raw, pas, ret], color=COL[m], lw=0.8, alpha=0.8, zorder=3)
        ax.scatter(xs, [raw, pas, ret], s=24, marker=MK[s], color=COL[m], ec="white", lw=0.5, zorder=4)
# value labels: range across the three selectors
for m, dy in (("RF", 1.35), ("DT", 0.70)):
    for k in range(3):
        vals = [COUNTS[m][s][k] for s in COUNTS[m]]
        lo, hi = min(vals), max(vals)
        if m == "RF":
            txt = f"{int(q(lo, '1')):,}–{int(q(hi, '1')):,}"
        else:
            txt = f"{q(lo, '0.1')}–{q(hi, '0.1')}"
        ax.text(X[k] + ((0.42 if m == "RF" else 0.2) if k == 0 else 0), hi * dy if m == "RF" else lo * dy, txt, fontsize=7.4, color=INK, ha="center",
                va="bottom" if m == "RF" else "top")
ax.hlines(BBAR, 1.62, 2.38, color=INK, lw=0.8, ls=(0, (3, 2)), zorder=2)
ax.annotate(r"mean budget $\bar B = 85$", xy=(2.3, BBAR), xytext=(1.45, 28), fontsize=7.0, color=INK,
            ha="center", va="center", arrowprops=dict(arrowstyle="-", lw=0.5, color=MUTED, shrinkA=1, shrinkB=1))
ax.set_yscale("log"); ax.set_ylim(1.5, 6000)
ax.set_yticks([1e0 * 2, 10, 100, 1000]); ax.set_yticks([2, 10, 100, 1000])
ax.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda v, p: f"{v:,.0f}"))
ax.set_xticks(X); ax.set_xticklabels(["Raw", "Passed", "Retained"], fontsize=7.6)
ax.set_xlim(-0.3, 2.55)
ax.set_ylabel("Mean rules per dataset (log)", fontsize=7.6)
ax.set_title(r"(a) Rule-set reduction", fontsize=TFS, loc="left", fontweight="bold", pad=3)
style(ax)

# ---------- (b) strip plots ----------
LABELS = {}
for j, (col, title) in enumerate([("cov", "(b) Test coverage"), ("fid_active", "(c) Test active-rule fidelity")]):
    ax = fig.add_subplot(gs[0, j + 1])
    for x0, m, mk in [(0, "dt", "o"), (1, "rf", "s")]:
        d = TB[TB.model == m].reset_index(drop=True)
        v = d[col].to_numpy(); xs = swarm(v, x0, dx=0.075)
        ax.scatter(xs, v, s=16, marker=mk, color=COL[m.upper()], ec="white", lw=0.4, zorder=4)
        mu = v.mean()
        ax.plot([x0 - 0.38, x0 + 0.38], [mu, mu], color=INK, lw=1.0, zorder=5)
        ax.text(x0 + 0.42, mu, f"{q(mu, '0.001')}", fontsize=7.4, va="center", ha="left", color=INK, fontweight="bold")
        for g in LABELS.get((col, m), []):
            i = d.index[d.gse == g][0]
            dy = {"GSE29354": 0.014, "GSE26304": -0.014}.get(g, 0) if col == "fid_active" else 0
            ax.text(xs[i] + (0.12 if x0 == 0 else -0.12), v[i] + dy, g.replace("GSE", ""), fontsize=5.8,
                    color=MUTED, va="center", ha="left" if x0 == 0 else "right")
    ax.set_xlim(-0.55, 2.0); ax.set_ylim(0.3, 1.05)
    ax.set_xticks([0, 1]); ax.set_xticklabels(["DT", "RF"], fontsize=7.6)
    ax.set_yticks([0.4, 0.6, 0.8, 1.0])
    ax.set_title(title, fontsize=TFS, loc="left", fontweight="bold", pad=3)
    style(ax)

H = [Line2D([], [], color=COL["DT"], lw=1, marker="o", ms=3.5, label="DT"),
     Line2D([], [], color=COL["RF"], lw=1, marker="o", ms=3.5, label="RF"),
     Line2D([], [], color=MUTED, ls="", marker="o", ms=3.5, label="mRMR-50"),
     Line2D([], [], color=MUTED, ls="", marker="s", ms=3.5, label="mRMR-75"),
     Line2D([], [], color=MUTED, ls="", marker="^", ms=3.8, label="Boruta"),
     Line2D([], [], color=INK, lw=1.0, label="mean of 12 datasets (b, c)")]
fig.legend(handles=H, loc="lower center", ncol=6, fontsize=7.0, frameon=False, handlelength=1.4,
           handletextpad=0.3, columnspacing=0.8, bbox_to_anchor=(0.54, -0.02))
for ext, kw in [("pdf", {}), ("svg", {}), ("png", {"dpi": 600})]:
    fig.savefig(f"fig2_sans.{ext}", **kw)
print("ok")
