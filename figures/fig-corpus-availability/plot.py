"""fig-corpus-availability (Ch 4, N1-0): heat map of documents per language x corpus (log scale).
Input: experiments/n1_corpora/data/corpus_availability_docs.csv."""
import sys, math
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "experiments" / "common"))
from bookgen import EXP, copy_input, read_csv, fmt_count, save
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

copy_input(EXP / "n1_corpora/data/corpus_availability_docs.csv", HERE)
rows = read_csv(HERE / "data.csv")
CORP = ["HPLT v1.2", "HPLT v2.0", "HPLT v3.0", "FineWeb2", "CulturaX", "mC4", "CC-100", "Wikipedia"]
M = np.full((len(rows), len(CORP)), np.nan)
for i, r in enumerate(rows):
    for j, c in enumerate(CORP):
        v = r[c]
        if v not in ("0", "", "present"):
            M[i, j] = math.log10(float(v))
fig, ax = plt.subplots(figsize=(7.5, 8.2))
cmap = matplotlib.colormaps["Blues"].copy(); cmap.set_bad("#F2F2F2")
im = ax.imshow(np.ma.masked_invalid(M), aspect="auto", cmap=cmap, vmin=1, vmax=9)
for i, r in enumerate(rows):
    for j, c in enumerate(CORP):
        v = r[c]
        if v == "present":
            ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False, hatch="///", edgecolor="#9AA5B1", lw=0))
            ax.text(j, i, "✓", ha="center", va="center", fontsize=8, color="#333333")
        elif v not in ("0", ""):
            ax.text(j, i, fmt_count(v), ha="center", va="center", fontsize=6.5,
                    color="white" if M[i, j] > 6 else "#222222")
ax.set_xticks(range(len(CORP))); ax.set_xticklabels(CORP, rotation=35, ha="right", fontsize=8)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels([f"{r['language']} ({r['primary_script']})" for r in rows], fontsize=8)
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
cb.set_label("Documents (log10)", fontsize=8); cb.ax.tick_params(labelsize=7)
fig.text(0.01, 0.005, "Grey: absent. Hatched ✓: present, documents not reported (CC-100). mC4 = pages, Wikipedia = articles.",
         fontsize=7, color="#555555")
fig.tight_layout(rect=(0, 0.02, 1, 1))
save(fig, HERE)
