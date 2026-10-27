"""Regenerate this figure from its documented inputs; run with Python + matplotlib."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from book_assets import *
HERE = Path(__file__).resolve().parent

# Ratios of corpus totals, not averages over documents or words.
source = HERE / "hplt_v3_turkic.csv"  # HPLT v3.0 manifest, accessed 2026-10-12
data = [r for r in rows(source) if r["present"] == "1" and r["row_type"] in ("primary", "reference")]
assert len(data) == 13 and len({r["hplt_code"] for r in data}) == 13
out = []
for r in data:
    chars, tokens = int(r["characters"]), int(r["gemma3_tokens"])
    assert chars > 0 and tokens > 0
    ratio = chars / tokens
    assert abs(ratio - float(r["chars_per_token"])) < .00051
    out.append({k:r[k] for k in ("language", "hplt_code", "script", "row_type", "characters", "gemma3_tokens", "source")}
               | {"chars_per_token": f"{ratio:.6f}"})
with (HERE / "data.csv").open("w", newline="", encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
out.sort(key=lambda r: float(r["chars_per_token"]))
colors={"Latn":"#287994", "Cyrl":"#9b5b42", "Arab":"#77703d"}
fig, ax=plt.subplots(figsize=(8,5.5))
vals=[float(r["chars_per_token"]) for r in out]
ax.barh(range(len(out)),vals,color=["#92999e" if r["row_type"]=="reference" else colors[r["script"]] for r in out],height=.68)
ax.set_yticks(range(len(out)),[r["language"] for r in out]); ax.invert_yaxis()
ax.set_xlim(0,5); ax.set_xlabel("Characters / Gemma 3 token (ratio of corpus totals)")
ax.xaxis.grid(True,color="#e3e7e9"); ax.set_axisbelow(True)
for i,v in enumerate(vals): ax.text(v+.06,i,f"{v:.2f}",va="center",fontsize=9)
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=v,label=k) for k,v in colors.items()]+[Patch(color="#92999e",label="Reference")],loc="upper right",frameon=False,fontsize=9)
ax.set_title("HPLT v3: text length per token",loc="left",color=INK,pad=13)
fig.text(.01,.015,"Different language subsets; this comparison does not isolate a causal script effect.",fontsize=9,color=INK)
fig.tight_layout(rect=(0,.045,1,1));save(fig,HERE)
