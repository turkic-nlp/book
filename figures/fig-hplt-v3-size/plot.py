"""fig-hplt-v3-size: size of each Turkic subset in HPLT v3.0 (characters, log scale), corpora chapter.
Data: data.csv = experiments/n1_corpora/data/hplt_v3_turkic.csv (HPLT v3.0 manifest, accessed 2026-10-12)."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
HERE = Path(__file__).parent
rows = list(csv.DictReader(open(HERE / "data.csv", encoding="utf-8")))
prim = [r for r in rows if r["row_type"] == "primary"]
pres = sorted([r for r in prim if r["present"] == "1"], key=lambda r: int(r["characters"]))
absent = [r["language"] for r in prim if r["present"] == "0"]
y = np.arange(len(pres))
fig, ax = plt.subplots(figsize=(7.5, 4.8))
ax.barh(y, [int(r["characters"]) for r in pres], 0.6, color="#4C72B0")
for yi, r in zip(y, pres):
    v = int(r["characters"])
    ax.text(v * 1.15, yi, f"{v/1e9:.1f} B" if v >= 1e9 else f"{v/1e6:.0f} M", va="center", fontsize=8, color="#333333")
ax.set_xscale("log")
ax.set_xlim(1e8, 3e12)
ax.set_yticks(y)
ax.set_yticklabels([f"{r['language']} ({r['script']})" for r in pres], fontsize=8)
ax.set_xlabel("Characters in HPLT v3.0 (log scale)")
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="x", color="#E5E5E5", linewidth=0.6); ax.set_axisbelow(True)
fig.text(0.01, 0.01, "Not present: " + ", ".join(absent), fontsize=7, color="#555555", wrap=True)
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(HERE / "output.png", dpi=200); fig.savefig(HERE / "output.pdf")
