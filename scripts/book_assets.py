"""Small shared drawing helpers for the sourced book figures."""
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, PathPatch
from matplotlib.path import Path as MplPath
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "pdf.fonttype": 42, "axes.spines.top": False,
                     "axes.spines.right": False})
INK = "#233746"
BLUE = "#2c6e91"
PALE = "#edf4f7"
def rows(path):
    with path.open(newline="", encoding="utf-8") as f:
        result = list(csv.DictReader(f))
    assert result and all(r.get("source", "").strip() for r in result)
    return result
def save(fig, folder):
    for ext in ("png", "pdf"):
        fig.savefig(folder / ("output." + ext), dpi=220, facecolor="white", bbox_inches="tight", pad_inches=.16)
    plt.close(fig)
def canvas(size=(8, 7), limits=(0, 10, 0, 10)):
    fig, ax = plt.subplots(figsize=size)
    ax.set(xlim=limits[:2], ylim=limits[2:]); ax.axis("off")
    return fig, ax
def box(ax, x, y, text, width=5.2, height=.8, decision=False, color=PALE, fontsize=10):
    if decision:
        p = Polygon([(x-width/2,y),(x,y+height/2),(x+width/2,y),(x,y-height/2)],
                    facecolor=color, edgecolor=BLUE, linewidth=1.1)
    else:
        p = FancyBboxPatch((x-width/2,y-height/2),width,height,boxstyle="round,pad=0.035,rounding_size=.08",
                          facecolor=color,edgecolor=BLUE,linewidth=1.1)
    ax.add_patch(p); ax.text(x,y,text,ha="center",va="center",color=INK,fontsize=fontsize,linespacing=1.4)
def arrow(ax, points, label=None, label_xy=None):
    if len(points)>2:
        ax.plot(*zip(*points[:-1]),color=BLUE,lw=1.1)
    ax.add_patch(FancyArrowPatch(points[-2], points[-1], arrowstyle="-|>", mutation_scale=11, color=BLUE,lw=1.1))
    if label:
        x,y=label_xy or points[0]
        ax.text(x,y,label,fontsize=9,ha="center",va="center",color=INK,bbox=dict(facecolor="white",edgecolor="none",pad=1))
