"""KazNERD entity classes with mention counts per split.

Counts are computed from the authors' release (github.com/IS2AI/KazNERD, commit bd4333d,
KazNERD/IOB2_{train,valid,test}.txt; one mention = one B- tag). Run with the path of a
clone to recompute data.csv:  python generate.py /path/to/KazNERD
Without an argument the script rebuilds output.md from data.csv.
"""
from pathlib import Path
from collections import Counter
import csv, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from book_tables import export, table
HERE = Path(__file__).resolve().parent
SOURCE = "IS2AI/KazNERD@bd4333d KazNERD/IOB2_*.txt; counted by tables/tbl-kaznerd-types/generate.py"
GROUPS = {
    "People and groups": ["PERSON", "NORP", "POSITION"],
    "Organisations and places": ["ORGANISATION", "GPE", "LOCATION", "FACILITY"],
    "Time": ["DATE", "TIME"],
    "Numbers and measures": ["CARDINAL", "ORDINAL", "QUANTITY", "MONEY", "PERCENTAGE"],
    "Other": ["ADAGE", "ART", "CONTACT", "DISEASE", "EVENT", "LANGUAGE", "LAW", "NON_HUMAN",
              "PRODUCT", "PROJECT", "MISCELLANEOUS"],
}

def count(path):
    sents, mentions, cur = 0, Counter(), False
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            sents += cur; cur = False; continue
        cur = True
        tag = line.split()[-1]
        if tag.startswith("B-"): mentions[tag[2:]] += 1
    return sents + cur, mentions

if len(sys.argv) > 1:
    root = Path(sys.argv[1]) / "KazNERD"
    stats = {sp: count(root / f"IOB2_{sp}.txt") for sp in ("train", "valid", "test")}
    labels = set().union(*(m for _, m in stats.values()))
    assert labels == {l for g in GROUPS.values() for l in g}, labels
    rows = [{"group": g, "label": l, **{sp: stats[sp][1][l] for sp in stats}, "source": SOURCE}
            for g, ls in GROUPS.items() for l in ls]
    rows.append({"group": "_sentences", "label": "_sentences", **{sp: stats[sp][0] for sp in stats}, "source": SOURCE})
    export(HERE, rows)

rows = list(csv.DictReader(open(HERE / "data.csv", encoding="utf-8")))
sent = next(r for r in rows if r["label"] == "_sentences")
body = []
for g in GROUPS:
    body.append([g, ", ".join(f"{r['label']} ({int(r['train']):,} / {int(r['test']):,})"
                               for r in rows if r["group"] == g)])
tot = {sp: sum(int(r[sp]) for r in rows if r["label"] != "_sentences") for sp in ("train", "valid", "test")}
table(HERE, ["Category", "Classes (training / test mentions)"], body,
      "The 25 KazNERD entity classes [@yeshpanov2022kaznerd], grouped for readability, with mention counts "
      f"computed from the authors' release (IOB2; {int(sent['train']):,} / {int(sent['valid']):,} / {int(sent['test']):,} "
      f"training / validation / test sentences; {tot['train']:,} / {tot['valid']:,} / {tot['test']:,} mentions). "
      "Rare classes such as NON_HUMAN have too few test mentions for a meaningful per-class F1. {#tbl-kaznerd-types}")
print(open(HERE / "output.md").read())
