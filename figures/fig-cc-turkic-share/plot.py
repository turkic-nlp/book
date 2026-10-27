"""fig-cc-turkic-share (Ch 4, N1-0): share of pages per Turkic language in Common Crawl snapshots, by CLD2.
Input: experiments/n1_corpora/data/cc_turkic_share.csv (from cc-crawl-statistics plots/languages.csv)."""
import sys
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "experiments" / "common"))
from bookgen import EXP, copy_input, read_csv, save
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

copy_input(EXP / "n1_corpora/data/cc_turkic_share.csv", HERE)
rows = [r for r in read_csv(HERE / "data.csv") if r["iso639_3"] != "rus"]
NAMES = {"tur": "Turkish", "aze": "Azerbaijani", "kaz": "Kazakh", "uzb": "Uzbek", "kir": "Kyrgyz", "tat": "Tatar",
         "tuk": "Turkmen", "bak": "Bashkir", "uig": "Uyghur", "chv": "Chuvash", "sah": "Sakha"}
crawls = sorted({r["crawl"] for r in rows})
series = defaultdict(dict)
for r in rows:
    series[r["iso639_3"]][r["crawl"]] = float(r["pct_pages"])
order = sorted(series, key=lambda k: -series[k].get(crawls[-1], 0))
fig, ax = plt.subplots(figsize=(7.5, 4.6))
x = list(range(len(crawls)))
for k in order:
    ys = [series[k].get(c) for c in crawls]
    ax.plot(x, ys, lw=1.4, label=f"{NAMES.get(k, k)} ({series[k].get(crawls[-1], 0):.3f}%)")
ax.set_yscale("log")
ax.set_ylabel("Share of pages in the crawl (%, log scale)")
step = max(1, len(crawls) // 8)
ax.set_xticks(x[::step]); ax.set_xticklabels([c.replace("CC-MAIN-", "") for c in crawls[::step]], rotation=35, ha="right", fontsize=7)
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", color="#E5E5E5", lw=0.6)
ax.legend(fontsize=7, frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.0), title=f"latest: {crawls[-1]}", title_fontsize=7)
fig.text(0.01, 0.01, "Language = CLD2 primary language. CLD2 has no label for Chuvash, Sakha or the smaller Turkic languages.", fontsize=7, color="#555555")
fig.tight_layout(rect=(0, 0.03, 1, 1))
save(fig, HERE)
