# Figure: Areas of knowledge gained through the adolescent SRH programme (Table 21)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from PIL import Image

plt.rcParams.update({"font.family": "Carlito", "font.size": 12, "savefig.dpi": 300})

INK, INK2, AXIS, TRACK = "#1f1f1f", "#52514e", "#c3c2b7", "#f1f3f6"
# one-hue blue ramp: lighter = lower share, deeper = higher share
RAMP = LinearSegmentedColormap.from_list("blue", ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"])

rows = [
    ("Body changes during adolescence", 47.89),
    ("Menstrual health/hygiene", 51.34),
    ("Sexual/reproductive health", 18.39),
    ("Healthy relationships/consent", 37.55),
    ("When/where to seek health services", 29.12),
    ("Pregnancy prevention", 23.75),
    ("Nutrition/anemia", 44.83),
    ("Violence/abuse/help-seeking", 14.18),
]
rows.sort(key=lambda r: r[1])  # largest ends up on top
vmin, vmax = min(r[1] for r in rows), max(r[1] for r in rows)


def bar(ax, y, length, thick, fc, r_pt=5, z=2):
    """Horizontal bar, square at the baseline, rounded at the data end."""
    fig = ax.figure
    bb = ax.get_position()
    rx = r_pt / 72 * (ax.get_xlim()[1] - ax.get_xlim()[0]) / (bb.width * fig.get_figwidth())
    ry = r_pt / 72 * (ax.get_ylim()[1] - ax.get_ylim()[0]) / (bb.height * fig.get_figheight())
    rx, ry = min(rx, length), min(ry, thick / 2)
    y0, L, T = y - thick / 2, length, thick
    verts = [(0, y0), (L - rx, y0), (L, y0), (L, y0 + ry), (L, y0 + T - ry),
             (L, y0 + T), (L - rx, y0 + T), (0, y0 + T), (0, y0)]
    codes = [Path.MOVETO, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.LINETO,
             Path.CURVE3, Path.CURVE3, Path.LINETO, Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=fc, edgecolor="none", zorder=z))


# same 6.0 in width and font sizes as Figures 1-7; taller to fit eight bars
fig = plt.figure(figsize=(6.0, 4.0))
ax = fig.add_axes([0.445, 0.132, 0.50, 0.84])
ax.set_xlim(0, 60)
ax.set_ylim(-0.6, len(rows) - 0.4)

h = 0.58
for y, (label, v) in enumerate(rows):
    bar(ax, y, 60, h, TRACK, z=1)                       # soft full-width track
    t = 0.12 + 0.88 * (v - vmin) / (vmax - vmin)
    bar(ax, y, v, h, RAMP(t))
    ax.text(v + 1.0, y, f"{v:.2f}%", va="center", ha="left", fontsize=11,
            fontweight="bold", color=INK, zorder=3)

ax.set_yticks(range(len(rows)))
ax.set_yticklabels([r[0] for r in rows], fontsize=12, color=INK)
ax.set_xticks([0, 10, 20, 30, 40, 50, 60])
ax.set_xticklabels([f"{t}%" for t in [0, 10, 20, 30, 40, 50, 60]], fontsize=10.5, color=INK2)
ax.tick_params(axis="both", length=0, pad=6)
for s in ["top", "right", "left"]:
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(AXIS)
ax.spines["bottom"].set_linewidth(0.8)
ax.set_xlabel("Percent (%)", fontsize=11, color=INK2, labelpad=6)

out = "figure_08_srh_knowledge_areas.png"
fig.savefig(out, facecolor="white")
Image.open(out).convert("RGB").save(out, dpi=(300, 300))
print("wrote", out)
