"""fig-hplt-v3-quality: share of each Turkic subset's bytes per Web Docs Scorer quality bin (5 = lowest
kept, 10 = highest) in HPLT v3.0, corpora chapter.
Data: data.csv = experiments/n1_corpora/data/hplt_v3_turkic_quality_bins.csv; languages.csv for names."""
from pathlib import Path
import csv
from collections import defaultdict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
HERE = Path(__file__).parent
names = {r["hplt_code"]: r["language"] for r in csv.DictReader(open(HERE / "languages.csv", encoding="utf-8"))}
share = defaultdict(dict)
for r in csv.DictReader(open(HERE / "data.csv", encoding="utf-8")):
    share[r["hplt_code"]][int(r["wds_bin"])] = float(r["share_of_language_bytes"])
codes = sorted(share, key=lambda c: share[c].get(8, 0) + share[c].get(9, 0) + share[c].get(10, 0))
bins = [5, 6, 7, 8, 9, 10]
colors = ["#DCE6F2", "#B7CCE6", "#8AAED6", "#5B8CC2", "#336BA8", "#173F75"]  # one hue, light -> dark
y = np.arange(len(codes))
fig, ax = plt.subplots(figsize=(7.5, 4.6))
left = np.zeros(len(codes))
for b, c in zip(bins, colors):
    vals = np.array([share[k].get(b, 0) for k in codes])
    ax.barh(y, vals, 0.65, left=left, color=c, edgecolor="white", linewidth=1, label=f"bin {b}")
    left += vals
ax.set_yticks(y)
ax.set_yticklabels([f"{names[k]} ({k.split('_')[1]})" for k in codes], fontsize=8)
ax.set_xlim(0, 1)
ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
ax.set_xlabel("Share of compressed bytes per quality bin")
ax.legend(ncol=6, frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, 1.1))
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(HERE / "output.png", dpi=200); fig.savefig(HERE / "output.pdf")
