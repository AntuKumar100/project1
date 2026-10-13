import textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, Wedge

OUT = "/home/user/project1/figures"

# Carlito is metric-compatible with Calibri (Word's default body font)
plt.rcParams.update({
    "font.family": "Carlito",
    "font.size": 12,
    "savefig.dpi": 300,
    "figure.dpi": 300,
})

# One fixed canvas for every figure, so text size stays identical once placed in Word
W, H = 6.0, 3.3

ACHIEVED = "#2a78d6"   # blue: indicator met
NOT_MET  = "#eb6834"   # orange: indicator not met
TRACK    = "#eef0f3"
INK      = "#1f1f1f"
INK2     = "#52514e"
GRID     = "#e1e0d9"
AXIS     = "#c3c2b7"

data = [
    # (file, chart, [(label, pct, achieved?), ...])
    ("figure_01_satisfaction", "donut",
     [("Not satisfied", 3.56, False), ("Satisfied (at least 3 of 5)", 96.44, True)], "Satisfied"),
    ("figure_02_preventive_measures", "hbar",
     [("Fewer than 4 preventive measures", 37.78, False), ("4 or more preventive measures", 62.22, True)]),
    ("figure_03_sensitivity", "column",
     [("Fewer than 3 dimensions", 2.57, False), ("At least 3 of 4 dimensions", 97.43, True)]),
    ("figure_04_anc_visits", "donut",
     [("Fewer than 4 ANC visits", 6.19, False), ("At least 4 ANC visits", 93.81, True)], "At least 4 visits"),
    ("figure_05_pnc_visits", "hbar",
     [("Fewer than 3 PNC visits", 26.42, False), ("At least 3 PNC visits", 73.58, True)]),
    ("figure_06_exclusive_breastfeeding", "column",
     [("Not exclusively breastfed", 3.97, False), ("Exclusively breastfed", 96.03, True)]),
    ("figure_07_understanding_confidence", "donut",
     [("No", 9.23, False), ("Yes", 90.77, True)], "Yes"),
]


from matplotlib.path import Path
from matplotlib.patches import PathPatch

def rounded_bar(ax, x0, y0, length, thick, r_pt, horizontal, fc, z=2):
    """Bar anchored at the baseline with rounded corners on the data end only."""
    fig = ax.figure
    bb = ax.get_position()
    w_in = bb.width * fig.get_figwidth()
    h_in = bb.height * fig.get_figheight()
    xr = ax.get_xlim()[1] - ax.get_xlim()[0]
    yr = ax.get_ylim()[1] - ax.get_ylim()[0]
    rx = r_pt / 72 * xr / w_in
    ry = r_pt / 72 * yr / h_in
    if horizontal:
        # grows along x from x0, spans y0..y0+thick
        L, T = length, thick
        r_len, r_th = rx, ry
    else:
        L, T = length, thick
        r_len, r_th = ry, rx
    r_len = min(r_len, L)          # tiny bars: shrink radius, never exceed the bar
    r_th = min(r_th, T / 2)
    # local coords: u along length (0 = baseline), v across thickness
    pts = [(0, 0), (L - r_len, 0), (L, 0), (L, r_th), (L, T - r_th), (L, T), (L - r_len, T), (0, T), (0, 0)]
    codes = [Path.MOVETO, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.LINETO,
             Path.CURVE3, Path.CURVE3, Path.LINETO, Path.CLOSEPOLY]
    if horizontal:
        verts = [(x0 + u, y0 + v) for u, v in pts]
    else:
        verts = [(x0 + v, y0 + u) for u, v in pts]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=fc, edgecolor="none", zorder=z))


def pct(v):
    return f"{v:.2f}%"

def color(ok):
    return ACHIEVED if ok else NOT_MET


def donut(ax, fig, rows, center_label):
    ax.set_aspect("equal")
    ax.axis("off")
    # positive category starts at 12 o'clock and runs clockwise
    rows_draw = [r for r in rows if r[2]] + [r for r in rows if not r[2]]
    start = 90.0
    gap = 1.2  # degrees of white between segments
    R, w = 1.0, 0.30
    for label, v, ok in rows_draw:
        sweep = 360.0 * v / 100.0
        theta2 = start
        theta1 = start - sweep
        ax.add_patch(Wedge((0, 0), R, theta1 + gap / 2, theta2 - gap / 2,
                           width=w, facecolor=color(ok), edgecolor="white", linewidth=1.5))
        start = theta1
    ax.set_xlim(-1.08, 1.08)
    ax.set_ylim(-1.08, 1.08)
    main = next(r for r in rows if r[2])
    ax.text(0, 0.08, pct(main[1]), ha="center", va="center",
            fontsize=22, fontweight="bold", color=INK)
    ax.text(0, -0.22, center_label, ha="center", va="center", fontsize=11, color=INK2)

    # legend on the right, in table order
    lx = 0.54
    ly0 = 0.60
    for i, (label, v, ok) in enumerate(rows):
        y = ly0 - i * 0.22
        fig.patches.append(FancyBboxPatch((lx, y - 0.028), 0.028, 0.056,
                           boxstyle="round,pad=0,rounding_size=0.008",
                           transform=fig.transFigure, facecolor=color(ok), edgecolor="none"))
        fig.text(lx + 0.05, y + 0.012, label, fontsize=12, color=INK, va="center")
        fig.text(lx + 0.05, y - 0.065, pct(v), fontsize=12, color=INK2, va="center", fontweight="bold")


def hbar(ax, rows):
    labels = [r[0] for r in rows]
    n = len(rows)
    ys = list(range(n))[::-1]  # table order top-to-bottom
    h = 0.42
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.55, n - 0.25)
    for y, (label, v, ok) in zip(ys, rows):
        rounded_bar(ax, 0, y - h / 2, 100, h, 5, True, TRACK, z=1)
        rounded_bar(ax, 0, y - h / 2, v, h, 5, True, color(ok), z=2)
        # value label inside bar end when it fits, otherwise just outside
        if v > 18:
            ax.text(v - 1.6, y, pct(v), ha="right", va="center", fontsize=12,
                    color="white", fontweight="bold", zorder=3)
        else:
            ax.text(v + 1.6, y, pct(v), ha="left", va="center", fontsize=12,
                    color=INK, fontweight="bold", zorder=3)
        ax.text(0, y + h / 2 + 0.09, label, ha="left", va="bottom", fontsize=12, color=INK)
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.55, n - 0.25)
    ax.set_yticks([])
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_xticklabels([f"{t}%" for t in [0, 20, 40, 60, 80, 100]], fontsize=10.5, color=INK2)
    ax.tick_params(axis="x", length=0, pad=6)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.set_xlabel("Percent (%)", fontsize=11, color=INK2, labelpad=6)


def column(ax, rows):
    n = len(rows)
    xs = list(range(n))
    w = 0.42
    ax.set_xlim(-0.6, n - 0.4)
    ax.set_ylim(0, 116)
    for x, (label, v, ok) in zip(xs, rows):
        rounded_bar(ax, x - w / 2, 0, v, w, 5, False, color(ok))
        ax.text(x, v + 2.2, pct(v), ha="center", va="bottom", fontsize=12,
                fontweight="bold", color=INK, zorder=3)
    ax.set_xticks(xs)
    ax.set_xticklabels(["\n".join(textwrap.wrap(r[0], 30)) for r in rows],
                       fontsize=12, color=INK, linespacing=1.15)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_yticklabels([f"{t}%" for t in [0, 20, 40, 60, 80, 100]], fontsize=10.5, color=INK2)
    ax.tick_params(axis="both", length=0, pad=6)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(AXIS)
    ax.spines["bottom"].set_linewidth(0.8)
    ax.set_ylabel("Percent (%)", fontsize=11, color=INK2, labelpad=6)


for fname, kind, rows, *extra in data:
    fig = plt.figure(figsize=(W, H))
    if kind == "donut":
        ax = fig.add_axes([0.04, 0.04, 0.46, 0.92])
        donut(ax, fig, rows, extra[0])
    elif kind == "hbar":
        ax = fig.add_axes([0.05, 0.17, 0.88, 0.78])
        hbar(ax, rows)
    else:
        ax = fig.add_axes([0.14, 0.20, 0.82, 0.76])
        column(ax, rows)
    fig.savefig(f"{OUT}/{fname}.png", facecolor="white")
    plt.close(fig)
    print("wrote", fname)

# flatten to RGB (no alpha) so Word/PDF viewers never tint the white background
from PIL import Image
import glob
for f in glob.glob(f"{OUT}/figure_*.png"):
    Image.open(f).convert("RGB").save(f, dpi=(300, 300))
