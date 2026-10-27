"""TIL training-set sizes for selected pairs, read from a frozen copy of the release README.

Source: github.com/turkic-interlingua/til-mt, til_corpus/README.md at commit 7d988cc
(2022-01-20), column "Training size (# of sentences)". Copied 2026-10-13 to source/.
The paper's appendix Table 7 [@mirzakhalov2021large] reports different totals for some
pairs (e.g. en-tr 39.9M); this table uses the release's training sizes.
"""
from pathlib import Path
import re, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from book_tables import export, table
HERE = Path(__file__).resolve().parent
README = HERE / "source" / "til_corpus_README_7d988cc.md"
SOURCE = "til-mt@7d988cc til_corpus/README.md (Training size); release of mirzakhalov2021large"

sizes, names = {}, {}
for line in README.read_text(encoding="utf-8").splitlines():
    m = re.match(r"\|\s*\d+\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(\w+)\s*\|\s*(\w+)\s*\|\s*(\d+)\s*\|", line)
    if m:
        s_name, t_name, s, t, n = m.groups()
        sizes[frozenset((s, t))] = int(n); names[s] = s_name; names[t] = t_name
assert len(sizes) > 150, len(sizes)

PAIRS = [("en", "tr"), ("ru", "tr"), ("kk", "ru"), ("en", "kk"), ("en", "az"), ("en", "uz"),
         ("en", "ky"), ("en", "ug"), ("tr", "az"), ("kk", "ky"), ("ru", "kjh"), ("en", "tyv"), ("en", "krc")]
NAME = {"Kirghiz": "Kyrgyz", "Tuvinian": "Tuvan"}
rows = []
for s, t in PAIRS:
    n = sizes[frozenset((s, t))]
    rows.append({"pair": f"{s}-{t}", "language_pair": f"{NAME.get(names[s], names[s])}–{NAME.get(names[t], names[t])}",
                 "training_sentence_pairs": n, "source": SOURCE})
export(HERE, rows)

def fmt(n):
    return f"{n/1e6:.1f} M" if n >= 1e6 else f"{n/1e3:.1f} K"
ratio = sizes[frozenset(("en", "tr"))] / sizes[frozenset(("en", "ug"))]
table(HERE, ["Language pair", "Training sentence pairs"],
      [[r["language_pair"], fmt(r["training_sentence_pairs"])] for r in rows],
      "Training-set sizes for selected language pairs in the TIL corpus release [@mirzakhalov2021large]; "
      "counts from the release README (til-mt, commit 7d988cc), not the paper's appendix table, which gives different totals for some pairs. "
      f"English–Turkish has about {ratio:.0f} times more training data than English–Uyghur. "
      "Karachay-Balkar, Khakas and Tuvan are covered, but with small pair sizes; Nogai is not covered. {#tbl-til-data}")
print(open(HERE / "output.md").read())
