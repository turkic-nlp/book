"""tbl-semantic-resources (Chapter 13): verified lexical-semantic resources per Turkic language.
Input: experiments/n2_meaning/data/semantic_resources.csv (hand-curated; every row has url + verified_on; `verify`=1 marks
cells still to check, rendered in red)."""
import sys
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "experiments" / "common"))
from bookgen import EXP, copy_input, read_csv, md_table

copy_input(EXP / "n2_meaning/data/semantic_resources.csv", HERE)
rows = read_csv(HERE / "data.csv")
def size(r):
    if r["verify"] == "1" and not r["size"]: return "[size to verify]{.placeholder}"
    return r["size"] + (" [verify]{.placeholder}" if r["verify"] == "1" else "") if r["size"] else "—"
body = [[r["language"], r["resource_type"], f"{r['resource']} [@{r['citation_key']}]", size(r)] for r in rows]
langs = sorted({r["language"] for r in rows})
cap = ("Selected lexical-semantic resources, checked October 2026. Sizes refer to the cited release or publication; "
       "this is not an exhaustive family inventory.")
md = md_table(["Language", "Type", "Resource", "Size"], ["l", "l", "l", "l"], body, cap, "tbl-semantic-resources")
(HERE / "output.md").write_text(md, encoding="utf-8"); print(md)
