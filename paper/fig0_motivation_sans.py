
import sys
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, RegularPolygon, FancyArrowPatch, Rectangle

FONT = "Arial" if sys.platform.startswith("win") else "Liberation Sans"   # sans-serif: crisper at small sizes
mpl.rcParams.update({"font.family": FONT, "mathtext.fontset": "stixsans", "pdf.fonttype": 42, "svg.fonttype": "none"})

W, H = 122.0, 44.0
fig = plt.figure(figsize=(W / 25.4, H / 25.4))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")

INK, NAVY, MUTED, LINE = "#1d1d1d", "#1f3a5f", "#6b6b6b", "#c9d3df"
PUR = "#8a6fd1"
BLU_L, BLU_D, BLU_G = "#dbe7f6", "#1f4e8c", "#eef2f7"
ORG, ORG_L, ORG_D = "#ec8a3a", "#fde6d2", "#b85410"
GRN_L, GRN_D = "#dcf0e5", "#1b6e48"
BAD = "#b23a3a"


def rbox(x, y, w, h, fc="white", ec=MUTED, lw=0.6, r=1.0, ls="-", z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw,
                                ls=ls, zorder=z))


def t(x, y, s, fs=6.8, c=INK, b=False, ha="center", va="center", z=6, **kw):
    ax.text(x, y, s, fontsize=fs, color=c, weight="bold" if b else "normal", ha=ha, va=va, zorder=z, **kw)


def arrow(p, q, c=INK, lw=0.6, ms=6, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms, color=c, lw=lw, linestyle=ls,
                                 shrinkA=0, shrinkB=0, zorder=7))


# group frames
FT = 40.4                                   # top border of the two frames
rbox(0.8, 0.8, 75.0, FT - 0.8, fc="none", ec="#8f9bab", lw=0.6, r=2.2, ls=(0, (4.0, 2.5)), z=1)
rbox(77.6, 0.8, 43.6, FT - 0.8, fc="none", ec=ORG, lw=0.8, r=2.2, z=1)


def tab(xc, label, ec, tc, w):
    rbox(xc - w / 2, FT - 2.0, w, 4.0, fc="white", ec=ec, lw=0.8, r=2.0, z=8)
    t(xc, FT, label, fs=7.0, c=tc, b=True, z=9)


tab(38.3, "Common explanation views", "#8f9bab", "#4a5566", 36.0)
tab(99.4, "X-Gene", ORG, ORG_D, 14.0)
# contrast marker between the two frames
ax.add_patch(Circle((76.7, 21.0), 2.3, fc="white", ec=MUTED, lw=0.6, zorder=9))
t(76.7, 21.0, "vs.", fs=6.2, c=MUTED, b=True, z=10)

PT, NY = 34.6, 3.6          # panel-title row, take-away row
# ---------------- (a) feature attribution ----------------
t(2.4, PT, "(a) Feature attribution", fs=7.4, b=True, ha="left")
for k, v in enumerate([1.0, 0.78, 0.6, 0.45]):
    y = 29.0 - k * 4.2
    t(9.6, y, rf"$g_{{{k + 1}}}$", fs=7.0, ha="right", c=INK)
    ax.add_patch(Rectangle((10.6, y - 1.3), 22.0 * v, 2.6, fc=PUR, ec="none", alpha=1 - 0.16 * k, zorder=3))
ax.plot([10.6, 10.6], [14.6, 31.2], color=MUTED, lw=0.6, zorder=4)
rbox(4.5, 7.6, 32.0, 4.4, fc="white", ec=BAD, lw=0.55, ls=(0, (2.2, 1.6)), r=0.8)
t(20.5, 9.8, "which conditions? thresholds?", fs=6.1, c=BAD, style="italic")
t(19.5, NY, "no explicit joint conditions", fs=6.6, c=NAVY, style="italic")

# ---------------- (b) gene-level summary ----------------
X0 = 39.5
t(X0, PT, "(b) Gene-level summary", fs=7.4, b=True, ha="left")
probes = [("210930_s_at", False), ("216836_s_at", False), ("234354_x_at", True)]
GX, GY = X0 + 28.0, 20.5
for k, (p, used) in enumerate(probes):
    y = 29.0 - k * 7.6
    ax.add_patch(RegularPolygon((X0 + 2.8, y), 6, radius=2.5, fc=BLU_L if used else BLU_G,
                                ec=BLU_D if used else "#9aa8ba", lw=0.8 if used else 0.5, zorder=3))
    t(X0 + 2.8, y - 0.1, r"$\pi$", fs=7.0, c=INK if used else MUTED)
    t(X0 + 6.2, y, p, fs=6.4, c=NAVY if used else MUTED, ha="left", b=used)
    arrow((X0 + 20.0, y), (GX - 4.3, GY + (1 - k) * 1.7), c=MUTED, lw=0.5, ms=5)
ax.add_patch(Circle((GX, GY), 4.0, fc=GRN_L, ec=GRN_D, lw=0.7, zorder=3))
t(GX, GY - 0.1, "ERBB2", fs=5.4, c=GRN_D, b=True)
t(GX, GY - 6.2, "one score", fs=6.2, c=MUTED)
t(X0 + 6.2, 10.4, "used in the rule of (c)", fs=6.3, c=BLU_D, ha="left", style="italic")
t(X0 + 17.0, NY, "probe identity not shown", fs=6.6, c=NAVY, style="italic")

# ---------------- (c) X-Gene: decision region ----------------
# axes in mm: x 84..112, y 9..31 ; data ranges are schematic
AX0, AX1, AY0, AY1 = 88.0, 111.0, 12.5, 31.5
XR, YR = (6.4, 8.2), (4.7, 6.3)
TX, TYv = 7.264, 5.520
mx = lambda v: AX0 + (v - XR[0]) / (XR[1] - XR[0]) * (AX1 - AX0)
my = lambda v: AY0 + (v - YR[0]) / (YR[1] - YR[0]) * (AY1 - AY0)
t(78.6, PT, "(c) Probe-level rule", fs=7.4, b=True, ha="left")
ax.add_patch(Rectangle((mx(TX), my(TYv)), AX1 - mx(TX), AY1 - my(TYv), fc=ORG_L, ec="none", zorder=2))
ax.plot([mx(TX)] * 2, [AY0, AY1], color=ORG_D, lw=0.8, ls=(0, (3, 2)), zorder=4)
ax.plot([AX0, AX1], [my(TYv)] * 2, color=ORG_D, lw=0.8, ls=(0, (3, 2)), zorder=4)
ax.plot([AX0, AX1], [AY0, AY0], color=INK, lw=0.6, zorder=5)
ax.plot([AX0, AX0], [AY0, AY1], color=INK, lw=0.6, zorder=5)
t((mx(TX) + AX1) / 2, (my(TYv) + AY1) / 2, "THEN\nHER2", fs=6.8, c=ORG_D, b=True, linespacing=1.1)
t(mx(TX) - 0.6, AY1 - 1.2, "7.264", fs=6.2, c=ORG_D, ha="right")
t(AX0 + 1.0, my(TYv) + 1.4, "5.520", fs=6.2, c=ORG_D, ha="left")
t((AX0 + AX1) / 2, AY0 - 2.4, "228273_at (PRR11)", fs=6.3, c=NAVY)
t(AX0 - 2.0, (AY0 + AY1) / 2, "234354_x_at (ERBB2)", fs=6.3, c=NAVY, rotation=90)
rbox(112.6, 14.0, 8.2, 17.0, fc="white", ec=ORG, lw=0.5, r=0.8)
t(116.7, 28.4, "rule set", fs=5.6, c=ORG_D, b=True)
t(116.7, 24.6, r"$\mathcal{D}_{te}$", fs=6.8, c=INK)
t(116.7, 20.6, "cov", fs=6.4, c=INK)
t(116.7, 17.2, r"fid$^{+}$", fs=6.4, c=INK)
t(99.3, NY, "explicit conditions on original probes", fs=6.6, c=NAVY, style="italic")

for ext, kw in [("pdf", {}), ("svg", {}), ("png", {"dpi": 600})]:
    fig.savefig(f"fig0_motivation_sans.{ext}", **kw)
print("ok")
