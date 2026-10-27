"""Dated inventory of Turkic NER datasets (checked 2026-10-13).

data.csv is curated by hand: every field comes from the resource's paper, data note,
release README or dataset card named in the `source` column. Fields not stated there are
written as such rather than filled in. This is a survey snapshot, not a complete list.
"""
from pathlib import Path
import csv, sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from book_tables import table
HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader(open(HERE / "data.csv", encoding="utf-8")))
assert all(r["source"] for r in rows)
table(HERE, ["Language(s)", "Resource", "Annotation", "Labels", "Domain", "Size", "Access / licence"],
      [[r["language"], r["resource"], r["annotation"], r["labels"], r["domain"], r["size"], r["access_licence"]] for r in rows],
      "Turkic NER resources identified in this survey (searched 2026-10-13; not exhaustive). Human annotation, "
      "weak supervision and automatic projection are kept apart; fields the source does not state are marked as such. "
      "WikiANN sizes are those of the commonly used Hugging Face splits. {#tbl-turkic-ner-resources}")
print(open(HERE / "output.md").read())
