"""fig-tokenizer-fertility: measured fertility of four LLM tokenisers (Ch 6).
Data: ../../tables/tbl-fertility/data.csv (from @hakimov2025turkicnlp experiments)."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
rows = list(csv.DictReader(open(HERE / "../../tables/tbl-fertility/data.csv", encoding="utf-8")))
T = [("qwen", "Qwen3.5"), ("llama", "LLaMA 3"), ("olmo", "OLMo 3"), ("openai", "o200k_base")]
rows.sort(key=lambda r: max(float(r[f"fert_{t}"]) for t, _ in T))
names = [f"{r['language'].replace(' (reference)','')} ({r['script']})" for r in rows]
x = np.arange(len(rows)); w = 0.2
colors = ["#4C72B0", "#DD8452", "#55A868", "#8172B3"]
fig, ax = plt.subplots(figsize=(12, 4.8))
for i, (t, lab) in enumerate(T):
    ax.bar(x + (i - 1.5) * w, [float(r[f"fert_{t}"]) for r in rows], w, label=lab, color=colors[i])
ax.axhline(1.0, ls="--", lw=0.8, color="grey")
ax.set_xticks(x); ax.set_xticklabels(names, rotation=60, ha="right", fontsize=8)
for lbl, r in zip(ax.get_xticklabels(), rows):
    if r["script"] != "Latn":
        lbl.set_fontweight("bold")
ax.set_ylabel("Tokens per word")
ax.legend(ncol=4, frameon=False, loc="upper left")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(HERE / "output.png", dpi=200); fig.savefig(HERE / "output.pdf")
