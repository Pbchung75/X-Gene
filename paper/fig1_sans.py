import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, FancyArrowPatch, Polygon, RegularPolygon

FONT = "Arial" if sys.platform.startswith("win") else "Liberation Sans"
mpl.rcParams.update({"font.family": FONT, "mathtext.fontset": "stixsans",
                     "pdf.fonttype": 42, "svg.fonttype": "none"})

W, TOP, BOT = 186.0, 73.0, -12.2
GAP, YCUT = 3.0, 27.8                  # bottom block shifted down by GAP (everything below YCUT)
fig = plt.figure(figsize=(W / 25.4, (TOP - BOT) / 25.4))
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(BOT, TOP); ax.axis("off")

BLU, BLU_L, BLU_D = "#5b8fd0", "#dbe7f6", "#1f4e8c"
ORG, ORG_L, ORG_D = "#ec8a3a", "#fde6d2", "#b85410"
GRN, GRN_L, GRN_D = "#3fa274", "#dcf0e5", "#1b6e48"
PUR, PUR_L, PUR_D = "#8a6fd1", "#ece6f8", "#5b45a8"
EXP, EXP_L, EXP_D = "#1f7a8c", "#e3f1f3", "#13505e"
INK, GRY, NAVY = "#1d1d1d", "#8a8a8a", "#1f3a5f"
TST, TST_L = "#5d6b80", "#e4e8ee"
DASH = "#4a78c2"
LT, LD = 9.2, 7.3
FS_K = 1.18 
FS_T = 1.0   # step titles (bold) scale
cm = mpl.colormaps["RdBu_r"]
rng = np.random.default_rng(5)


# ───────────────────────── helpers ─────────────────────────
LABELS = []                            # (artist, row) for overlap check


def txt(x, y, s, fs=LT, ha="center", va="center", c=INK, b=False, z=6, k=None, **kw):
    return ax.text(x, y, s, fontsize=fs * (FS_K if k is None else k), ha=ha, va=va, color=c, weight="bold" if b else "normal", zorder=z, **kw)


def label(x, y, title, detail=None, above=True):
    yt, yd = (y + 3.4, y) if above else (y, y - 3.4)
    LABELS.append((txt(x, yt, title, b=True, k=FS_T), "T" if above else "B"))
    if detail:
        # italic details inside region 1 (top row) and region 2 (bottom row, x within R2)
        ital = x < 141.0 and (y > 30.0 or x > 39.6)
        LABELS.append((txt(x, yd, detail, fs=LD, c=NAVY, style="italic" if ital else "normal"),
                       ("T" if above else "B") + "d"))


def rbox(x, y, w, h, fc="white", ec=GRY, lw=0.8, r=1.0, ls="-", z=2, alpha=1.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, ls=ls, zorder=z, alpha=alpha))


LW_K, MS_K = 0.32, 0.68                 # global thinning of all arrows / connectors


def arrow(p, q, c=INK, lw=1.3, ms=8, ls="-", z=7):
    lw, ms = lw * LW_K, ms * MS_K
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms, color=c, lw=lw, linestyle=ls,
                                 shrinkA=0, shrinkB=0, zorder=z))


def path(pts, c=INK, lw=1.3, ms=8, ls="-", z=7):
    """Orthogonal polyline ending in an arrow head."""
    xs, ys = zip(*pts[:-1])
    ax.plot(list(xs) + [pts[-2][0]], list(ys) + [pts[-2][1]], color=c, lw=lw * LW_K, ls=ls, zorder=z,
            solid_joinstyle="miter", solid_capstyle="butt")
    arrow(pts[-2], pts[-1], c=c, lw=lw, ms=ms, ls=ls, z=z)


def tree(cx, top, dx, dy, depth=2, path_=None, nc=BLU, rad=0.8, z=3):
    nodes = {(): (cx, top)}
    for d in range(1, depth + 1):
        for k in range(2 ** d):
            b = tuple((k >> (d - 1 - i)) & 1 for i in range(d))
            px, py = nodes[b[:-1]]
            nodes[b] = (px + dx / 2 ** d * (1 if b[-1] else -1), py - dy)
    on = {tuple(path_[:i]) for i in range(len(path_) + 1)} if path_ else set()
    for b, (x, y) in nodes.items():
        if b:
            px, py = nodes[b[:-1]]
            h = b in on
            ax.plot([px, x], [py, y], color=ORG if h else "#7f8fa3", lw=1.5 if h else 0.7, ls="--" if h else "-",
                    zorder=z)
    for b, (x, y) in nodes.items():
        ax.add_patch(Circle((x, y), rad, fc=ORG if b in on else nc, ec="#33475e", lw=0.5, zorder=z + 0.5))


def heat(x, y, nr, nc, cw, ch, cmap=cm, z=3, lo=0.08, hi=0.92):
    for i in range(nr):
        for j in range(nc):
            ax.add_patch(Rectangle((x + j * cw, y + i * ch), cw, ch, fc=cmap(lo + (hi - lo) * rng.random()),
                                   ec="white", lw=0.25, zorder=z))


def dte(x, y, w=6.8, h=3.4):
    rbox(x, y, w, h, fc=TST_L, ec=TST, lw=0.8, r=0.8, z=8)
    txt(x + w / 2, y + h / 2, r"$\mathcal{D}_{te}$", fs=7.6, c=TST, z=9)


def text_width(s, fs, bold=True):
    t = ax.text(0, 0, s, fontsize=fs * FS_K, weight="bold" if bold else "normal")
    fig.canvas.draw()
    w = t.get_window_extent(fig.canvas.get_renderer()).width * W / fig.bbox.width
    t.remove()
    return w


def region(x0, y0, x1, y1, col, light):
    """Component region: faint tint + thin border (drawn underneath everything)."""
    rbox(x0, y0, x1 - x0, y1 - y0, fc="none", ec=col, lw=0.6, r=2.4, z=0.3, ls=(0, (4.0, 2.5)))


def tab(x, y, num, text, col, light, anchor="left"):
    """Region name tab sitting on the region border."""
    tw = text_width(text, 7.5) + (6.2 if num else 3.2)
    x0 = x if anchor == "left" else x - tw / 2
    rbox(x0, y - 2.0, tw, 4.0, fc=light, ec=col, lw=0.9, r=2.0, z=10)
    if num:
        ax.add_patch(Circle((x0 + 2.4, y), 1.45, fc=col, ec="none", zorder=11))
        txt(x0 + 2.4, y - 0.05, num, fs=7.6, c="white", b=True, z=12)
        txt(x0 + 4.6, y, text, fs=7.5, ha="left", c=col, b=True, z=12)
    else:
        txt(x0 + 1.6, y, text, fs=7.5, ha="left", c=col, b=True, z=12)


# ───────────────────────── regions ─────────────────────────
R1 = (2.0, 29.6, 140.6, 70.6)       # (1) predictive learning
R2 = (39.6, -1.0, 140.6, 27.4)       # (2) rule-centric explanation
R3 = (143.0, -1.0, 185.6, 70.6)      # (3) traceable interpretation
RA = (2.0, -1.0, 37.4, 27.4)         # auxiliary (post-hoc)
region(*R1, BLU, BLU_L)
region(*R2, ORG, ORG_L)
region(*R3, EXP, EXP_L)
region(*RA, PUR, PUR_L)

TY, BY = 48.0, 17.0                # row centre lines
LAB_T, LAB_B = TY + 10.4, BY - 12.2

# ═════════════════ (1) predictive learning ═════════════════
# input
for k in range(3):
    rbox(4.6 + (2 - k) * 1.1, 41.0 + (2 - k) * 1.2, 15.5, 11.0, fc="white", ec="#9aa5b1", lw=0.7, r=1.2, z=2 + k)
heat(6.0, 42.1, 5, 7, 1.9, 1.75, z=6)
label(13.6, LAB_T, "Input Data", "GEO / CuMiDa")

# split: one block, 85 % D_tr above / 15 % D_te below
SX0, SX1, SY0, SH = 28.0, 40.0, TY - 7.55, 13.0
h_te = 0.15 * SH
ax.add_patch(Rectangle((SX0, SY0 + h_te), SX1 - SX0, SH - h_te, fc=BLU, ec="none", zorder=3))
ax.add_patch(Rectangle((SX0, SY0), SX1 - SX0, h_te, fc=TST, ec="none", zorder=3))
ax.plot([SX0, SX1], [SY0 + h_te] * 2, color="white", lw=0.9, zorder=4)
ax.add_patch(Rectangle((SX0, SY0), SX1 - SX0, SH, fc="none", ec="#33475e", lw=0.8, zorder=5))
txt((SX0 + SX1) / 2, TY, r"$\mathcal{D}_{tr}$", fs=9.0, c="white", b=True)
txt(SX1 + 0.8, SY0 + h_te / 2, r"$\mathcal{D}_{te}$", fs=7.4, c=TST, ha="left", b=True)
label(33.5, LAB_T, "Data Split", "stratified")

# feature selection
for i, v in enumerate([1.0, 0.85, 0.7, 0.5, 0.38, 0.3, 0.22, 0.16]):
    ax.add_patch(Rectangle((50.0 + i * 1.75, 42.0), 1.35, 12.0 * v, fc=BLU if i < 4 else "#c9d3df", ec="none",
                           zorder=3))
ax.plot([49.3, 64.3], [42.0, 42.0], color=GRY, lw=0.6, zorder=3)
ax.plot([57.15, 57.15], [41.4, 54.5], color=ORG, lw=0.9, ls=(0, (2, 1.5)), zorder=4)
label(56.4, LAB_T, "Feature Selection", "mRMR / Boruta")

# selected probes
heat(73.0, 41.8, 6, 5, 2.1, 2.0, cmap=mpl.colormaps["Blues"], lo=0.2, hi=0.85)
label(80.6, LAB_T, r"Selected $X_S$", r"chosen on $\mathcal{D}_{tr}$")
txt(78.25, 38.6, r"reused on $\mathcal{D}_{te}$", fs=6.8, c=TST, b=True)

# tree models
for k in range(2):
    rbox(92.6 + k * 1.6, 41.6 + k * 1.2, 13.5, 10.6, fc="white", ec="#9aa5b1", lw=0.6, r=1.0, z=2 + k)
rbox(95.8, 44.0, 13.5, 10.6, fc="white", ec="#33475e", lw=0.7, r=1.0, z=4)
tree(102.55, 52.4, 9.0, 3.5, depth=2, z=5, rad=0.85)
label(101.0, LAB_T, "Tree Models", "DT / RF")

# prediction
rbox(117.0, 43.0, 11.0, 10.0, fc=BLU_L, ec=BLU_D, lw=0.9, r=1.6)
txt(122.5, 48.0, r"$\hat{y}$", fs=14, c=BLU_D)
label(122.5, LAB_T, "Prediction", r"$\hat{y}=f(x)$")

# held-out model evaluation (inside region 1, under the prediction)
for i in range(3):
    for j in range(3):
        v = 0.85 if i == j else rng.uniform(0.05, 0.3)
        ax.add_patch(Rectangle((119.35 + j * 2.1, 33.2 + (2 - i) * 2.1), 2.1, 2.1, fc=mpl.colormaps["Blues"](v),
                               ec="white", lw=0.3, zorder=3))
arrow((122.5, 43.0), (122.5, 39.8), lw=1.0, ms=6)
dte(127.6, 34.4)
arrow((127.4, 36.1), (125.8, 36.1), c=TST, lw=0.9, ms=5)
txt(117.6, 38.6, "Held-out test", fs=LD, b=True, ha="right")
txt(117.6, 35.8, "Acc · BAcc", fs=LD, c=NAVY, ha="right", style="italic")
txt(117.6, 33.0, r"Macro-$F_1$", fs=LD, c=NAVY, ha="right", style="italic")

# row-1 arrows
for a, b in [(21.4, 27.8), (40.2, 48.8), (65.1, 72.4), (84.2, 92.0), (110.0, 116.8)]:
    arrow((a, TY), (b, TY), lw=1.4, ms=8)

# ═════════════════ (2) rule-centric explanation ═════════════════
PX, QX, FX, SX = 50.6, 72.0, 92.6, 110.0
EVX = 129.0                                   # held-out rule evaluation (leaf branch)
tree(PX, 24.5, 10.0, 4.0, depth=2, path_=[1, 0], nc="#9fbbe0", rad=0.85)
label(PX - 0.4, LAB_B, "Path-to-Rule", "IF … THEN")
for i, (v, c) in enumerate(zip([0.55, 0.95, 0.75, 0.65, 0.9], [ORG, ORG, ORG, ORG, BLU])):
    ax.add_patch(Rectangle((QX - 5.6 + i * 2.3, 11.0), 1.7, 12.0 * v, fc=c, ec="none", zorder=3, alpha=0.9))
ax.plot([QX - 6.2, QX + 6.2], [11.0, 11.0], color=GRY, lw=0.6, zorder=3)
label(QX + 0.1, LAB_B, "Rule Quality", r"on $\mathcal{D}_{tr}$")
for k, (wt, col) in enumerate([(13.0, "#f8d2ae"), (10.2, "#f3b079"), (7.4, ORG)]):
    yt = 24.0 - k * 4.3
    wb = wt - 2.8
    ax.add_patch(Polygon([(FX - wt / 2, yt), (FX + wt / 2, yt), (FX + wb / 2, yt - 3.9), (FX - wb / 2, yt - 3.9)],
                         closed=True, fc=col, ec="white", lw=0.6, zorder=3))
label(FX - 0.3, LAB_B, "Refinement", "filter·dedup·cap")
for k in range(3):
    rbox(SX - 6.3 + k * 1.2, 11.0 + (2 - k) * 4.2, 11.0, 3.6, fc="white", ec=ORG, lw=0.7, r=0.7, z=3 + k)
    txt(SX - 4.3 + k * 1.2, 12.8 + (2 - k) * 4.2, r"$r_{%d}$" % (k + 1), fs=7.0, z=7 + k)
    ax.plot([SX - 1.9 + k * 1.2, SX + 3.5 + k * 1.2], [12.8 + (2 - k) * 4.2] * 2, color=ORG, lw=1.0, zorder=7 + k)
label(SX + 2.4, LAB_B, "Rule Set", r"frozen $R_{\mathrm{final}}$")
# held-out rule evaluation: leaf branch from the frozen rule set (no arrow back, no arrow onward)
for i, (v, c) in enumerate(zip([0.6, 0.95, 0.85], [ORG, ORG, BLU])):
    ax.add_patch(Rectangle((EVX - 2.6 + i * 2.4, 10.6), 1.8, 7.0 * v, fc=c, ec="none", zorder=3))
ax.plot([EVX - 3.2, EVX + 4.6], [10.6, 10.6], color=GRY, lw=0.6, zorder=3)
dte(EVX - 8.6, 17.6, w=6.4, h=3.0)
arrow((EVX - 2.4, 18.4), (EVX - 1.2, 17.0), c=TST, lw=0.9, ms=5)         # D_te -> evaluation
arrow((SX - 3.9 + 11.0 - 0.1, 12.8), (EVX - 3.4, 12.8), lw=1.4, ms=8)      # R_final -> rule evaluation
label(EVX + 1.6, LAB_B, "Rule Eval.", "supp·conf·fid")
for a, b in [(PX + 8.8, QX - 6.8), (QX + 6.8, FX - 7.0), (FX + 7.0, SX - 6.9)]:
    arrow((a, BY), (b, BY), lw=1.4, ms=8)

# ═════════════════ (3) traceable interpretation ═════════════════
BX0, BX1, BY0, BY1 = 145.0, 183.6, 32.4, 66.4
rbox(BX0, BY0, BX1 - BX0, BY1 - BY0, fc="white", ec=EXP, lw=0.7, r=2.0, z=2)
txt((BX0 + BX1) / 2, 63.5, "Sample-level Explanation", b=True, fs=8.7, c=EXP_D, k=1.0)
rows = [(r"Test sample $x\in\mathcal{D}_{te}$", 55.6, 4.4), (r"Model: $\hat{y}=f(x)$", 49.2, 4.4),
        ("Matched rules", 40.2, 7.2), (r"GO context of $\mathcal{R}(x)$", 34.0, 4.4)]
RX0, RX1 = BX0 + 2.6, BX1 - 2.6
for s_, y, h in rows:
    rbox(RX0, y, RX1 - RX0, h, fc="white", ec=EXP, lw=0.6, r=1.0, z=3)
    if s_ == "Matched rules":
        txt((RX0 + RX1) / 2, y + 4.9, s_, fs=8.0, b=True, k=1.0)
        txt((RX0 + RX1) / 2, y + 2.0, r"$\mathcal{R}(x)=\{r\in R_{\mathrm{final}}: A_r(x)=1\}$", fs=7.0, k=1.0)
    else:
        txt((RX0 + RX1) / 2, y + h / 2, s_, fs=8.0, b=True, k=1.0)
# Gene & GO cluster centred in region 3: g, the GO chips, the label and the g -> box arrow share one
# vertical axis through the centre of the Sample-level Explanation box
GGX = (BX0 + BX1) / 2
PJX, PGY, PR = GGX - 9.0, 21.2, 2.8                          # probe (pi_j) and gene (g) icons
ax.add_patch(RegularPolygon((PJX, PGY), 6, radius=PR, fc=BLU_L, ec=BLU_D, lw=0.8, zorder=3))
txt(PJX, PGY - 0.1, r"$\pi_j$", fs=9.4)
ax.add_patch(Circle((GGX, PGY), PR, fc=GRN_L, ec=GRN_D, lw=0.8, zorder=3))
txt(GGX, PGY - 0.1, r"$g$", fs=10.0, c=GRN_D)
arrow((PJX + PR * 0.87 + 0.1, PGY), (GGX - PR - 0.1, PGY), c=GRN_D, lw=1.2, ms=7)
for k, (go, c) in enumerate([("BP", GRN), ("MF", "#58b88a"), ("CC", "#8fd0ad")]):
    rbox(GGX - 6.7 + k * 4.6, 11.2, 4.2, 4.0, fc=c, ec="none", r=0.7)
    txt(GGX - 4.6 + k * 4.6, 13.2, go, fs=6.4, b=True, c="white", k=1.0)
ax.plot([GGX, GGX], [PGY - PR, 15.2], color=GRN_D, lw=0.6, zorder=2)
label(GGX, LAB_B, "Gene & GO", r"$\pi_j \rightarrow g \rightarrow$ GO")

# connections into region 3
arrow((128.4, 50.4), (BX0 - 0.2, 50.4), lw=1.4, ms=8)                    # y_hat -> Model row
# R_final has two independent outputs:
#   (a) probes of the rules -> probe-to-gene mapping -> GO      (straight, no junction)
#   (b) the rules themselves -> rule matching for the test sample (routed through the inter-region gap
#       and entering the "Matched rules" row directly)
JY = 21.2
arrow((SX + 4.8, JY), (PJX - PR * 0.87 - 0.1, JY), lw=1.4, ms=8)                    # (a) -> pi_j
MROW = 40.2 + 7.2 / 2                                                                # Matched-rules row centre
CHX = 141.8                                                                          # channel between regions
arrow((GGX, PGY + PR + 0.1), (GGX, BY0 - 0.2), lw=1.4, ms=8)             # GO -> GO context

# ═════════════════ auxiliary: post-hoc SHAP ═════════════════
for k, v in enumerate([1.0, 0.8, 0.62, 0.5, 0.38]):
    ax.add_patch(Rectangle((5.0, 22.0 - k * 2.4), 12.0 * v, 1.7, fc=PUR, ec="none", alpha=1 - 0.12 * k, zorder=3))
ax.plot([5.0, 5.0], [11.4, 24.2], color=GRY, lw=0.6, zorder=3)
label(11.0, LAB_B, "TreeSHAP", r"on $\mathcal{D}_{tr}$")
ax.add_patch(Circle((25.4, 17.5), 4.6, fc=ORG, alpha=0.25, ec=ORG, lw=0.8, zorder=3))
ax.add_patch(Circle((31.0, 17.5), 4.6, fc=PUR, alpha=0.25, ec=PUR, lw=0.8, zorder=3))
txt(23.5, 17.5, r"$G_{r}$", fs=7.6)
txt(32.9, 17.5, r"$G_{s}$", fs=7.6)
label(28.2, LAB_B, r"Jaccard $J$")
arrow((17.6, 17.5), (20.5, 17.5), c=DASH, lw=1.1, ms=6, ls=(0, (3, 2)))
# G_r is defined in place (genes mapped from the probes of R_final), so no long connector is needed
txt(26.4, 24.6, r"$G_r$: genes of $R_{\mathrm{final}}$", fs=7.2, c=NAVY, b=True, k=1.0)

# ═════════════════ tabs & legend ═════════════════
tab(R1[0] + 3.0, R1[3], "1", "Probe-level Predictive Learning", BLU_D, "white")
tab(R2[0] + 3.0, R2[1], "2", "Rule-Centric Explanation Construction", ORG_D, "white")
tab((R3[0] + R3[2]) / 2, R3[3], "3", "Traceable Interpretation", EXP_D, "white", anchor="center")
tab(RA[0] + 2.4, RA[1], None, "Post-hoc", PUR_D, "white")

LY = -6.2
ax.plot([4.0, 10.0], [LY, LY], color=INK, lw=1.3 * LW_K); arrow((9.0, LY), (10.6, LY), lw=1.3, ms=6)
txt(12.0, LY, "main flow", fs=LD, ha="left")
ax.plot([32.0, 38.0], [LY, LY], color=DASH, lw=1.1 * LW_K, ls=(0, (3, 2))); arrow((37.0, LY), (38.6, LY), c=DASH, lw=1.1, ms=6)
txt(40.0, LY, "post-hoc (no feedback)", fs=LD, ha="left")
dte(73.0, LY - 1.7)
txt(81.2, LY, "held-out evaluation only", fs=LD, ha="left")

# ═════════════════ shift the bottom block down by GAP ═════════════════
from matplotlib.patches import Rectangle as _R
def _w(y):
    return y - GAP if y < YCUT else y
for a in list(ax.patches):
    if isinstance(a, FancyArrowPatch):
        (x0, y0), (x1, y1) = a._posA_posB
        a.set_positions((x0, _w(y0)), (x1, _w(y1)))
    elif isinstance(a, (FancyBboxPatch, _R)):
        y0, y1 = a.get_y(), a.get_y() + a.get_height()
        a.set_y(_w(y0)); a.set_height(_w(y1) - _w(y0))
    elif isinstance(a, Circle):
        x, y = a.center; a.center = (x, _w(y))
    elif isinstance(a, RegularPolygon):
        x, y = a.xy; a.xy = (x, _w(y))
    elif isinstance(a, Polygon):
        xy = a.get_xy(); xy[:, 1] = [_w(v) for v in xy[:, 1]]; a.set_xy(xy)
for l in ax.lines:
    l.set_ydata([_w(v) for v in l.get_ydata()])
for t in ax.texts:
    x, y = t.get_position(); t.set_position((x, _w(y)))

# connectors crossing the widened gap between region 1 and the bottom regions (R1 bottom 29.6, R2 top 24.4)
L_TREE, L_RULE, L_SHAP = 26.0, 27.0, 28.0   # SHAP lane above the tree lane: no crossings
path([(96.6, 41.4), (96.6, L_TREE), (PX, L_TREE), (PX, 25.6 - GAP)], lw=1.4, ms=8)                  # tree models -> paths
path([(SX - 1.0, 23.0 - GAP), (SX - 1.0, L_RULE), (CHX, L_RULE), (CHX, MROW), (BX0 - 0.2, MROW)], lw=1.4, ms=8)  # (b)
path([(94.4, 41.4), (94.4, L_SHAP), (11.0, L_SHAP), (11.0, 25.0 - GAP)], c=DASH, lw=1.1, ms=7, ls=(0, (3, 2)))  # model -> SHAP

fig.canvas.draw()
_r = fig.canvas.get_renderer()
from collections import defaultdict
_rows = defaultdict(list)
for t, rr in LABELS:
    _rows[(rr, round(t.get_position()[1], 1))].append(t)
for key, ts in _rows.items():
    items = sorted([(t.get_window_extent(_r), t.get_text()) for t in ts], key=lambda p: p[0].x0)
    for (a, na), (b, nb) in zip(items, items[1:]):
        gap = (b.x0 - a.x1) * W / fig.bbox.width
        if gap < 1.6:
            print(f"{key}: '{na}' | '{nb}' gap {gap:.2f} mm")
for ext, kw in [("pdf", {}), ("svg", {}), ("png", {"dpi": 600})]:
    fig.savefig(f"fig1_sans.{ext}", **kw)
print("ok")
