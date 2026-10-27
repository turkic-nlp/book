"""fig-cts-overlap: character-trigram Dice overlap with Turkish, native script vs. CTS (Ch 3).
Data: data.csv (from @hakimov2025turkicnlp experiments; 20 parallel challenge sentences)."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
HERE = Path(__file__).parent
rows = sorted(csv.DictReader(open(HERE / "data.csv", encoding="utf-8")), key=lambda r: float(r["dice_cts"]))
y = np.arange(len(rows))
fig, ax = plt.subplots(figsize=(7.5, 6.5))
ax.barh(y + 0.2, [float(r["dice_native"]) for r in rows], 0.4, color="#BBBBBB", label="native script")
ax.barh(y - 0.2, [float(r["dice_cts"]) for r in rows], 0.4, color="#4C72B0", label="Common Turkic Alphabet")
ax.set_yticks(y)
ax.set_yticklabels([f"{r['language']} ({r['native_script']}, {r['branch']})" for r in rows], fontsize=8)
ax.set_xlabel("Character-trigram overlap with Turkish (Dice)")
ax.legend(frameon=False, loc="lower right")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(HERE / "output.png", dpi=200); fig.savefig(HERE / "output.pdf")
