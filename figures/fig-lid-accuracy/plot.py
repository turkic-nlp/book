"""fig-lid-accuracy: GlotLID accuracy (Turkic labels) per language with most frequent wrong label (Ch 3).
Data: data.csv (from @hakimov2025turkicnlp experiments; 20 challenge sentences per language)."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
HERE = Path(__file__).parent
rows = sorted(csv.DictReader(open(HERE / "data.csv", encoding="utf-8")), key=lambda r: float(r["accuracy"]))
y = np.arange(len(rows))
fig, ax = plt.subplots(figsize=(7.5, 6.5))
acc = [100 * float(r["accuracy"]) for r in rows]
ax.barh(y, acc, color=["#C44E52" if a < 60 else "#4C72B0" for a in acc])
for yi, r, a in zip(y, rows, acc):
    if r["top_confusion"] and int(r["confusion_count"]) >= 3:
        ax.text(a + 1.5, yi, f"→ {r['top_confusion']} ({r['confusion_count']}/20)", va="center", fontsize=7)
ax.set_yticks(y); ax.set_yticklabels([r["language"] for r in rows], fontsize=8)
ax.set_xlim(0, 130); ax.set_xticks([0, 20, 40, 60, 80, 100])
ax.set_xlabel("Sentences identified correctly (%)")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(HERE / "output.png", dpi=200); fig.savefig(HERE / "output.pdf")
