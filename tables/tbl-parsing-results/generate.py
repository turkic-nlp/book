"""Rebuild data.csv and the chapter include from the frozen primary-source snapshot.

Rows are grouped by test-set type (gold supervised / gold zero-shot / silver) so that
gold and silver results are never read as one series. Only matched-word counts are
published in the source; gold-word and predicted-word totals are not, so they are not
invented here (the chapter marks them as a placeholder).
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
from book_tables import *
HERE=Path(__file__).resolve().parent

r=latex_rows(HERE/"source.tex"); assert len(r)==13 and all(len(x)==10 for x in r)
source="hakimov2025turkicnlp; source.tex, tab:parsing-eval (snapshot 2026-10-13)"
keys=["language","iso","matched_words","stanza_upos","stanza_uas","stanza_las","neural_upos","neural_uas","neural_las"]

def test_set(name):
    if name.startswith("Avg"): return "published average (mixes gold and silver rows)"
    if "‡" in name: return "silver (translated, automatically annotated)"
    if "†" in name: return "gold UD-Turkic parallel, zero-shot"
    return "gold UD-Turkic parallel"

rows=[dict(zip(keys,x[:6]+x[7:]))|{"test_set":test_set(x[0]),"source":source} for x in r]
export(HERE,rows)

groups=[("*Gold UD-Turkic parallel test sets — supervised*","gold UD-Turkic parallel"),
        ("*Gold UD-Turkic parallel test sets — zero-shot*^†^","gold UD-Turkic parallel, zero-shot"),
        ("*Silver test sets*^‡^","silver (translated, automatically annotated)")]
body=[]
for label,kind in groups:
    body.append([label]+[""]*7)
    for x in r:
        if test_set(x[0])!=kind: continue
        name=x[0]; n=f"{int(x[2]):,}" if x[2] else ""
        if name.startswith("Avg"): name="Average (9 shared; includes Turkmen and Bashkir silver rows)"
        body.append([name,n]+paired(x[3:6]+x[7:],3))
table(HERE,["Language","Matched words (n)","Stanza UPOS","Stanza UAS","Stanza LAS","Multilingual UPOS","Multilingual UAS","Multilingual LAS"],body,
      "POS tagging and dependency parsing from the frozen local manuscript table of 13 October 2026 (`tables/tbl-parsing-results/source.tex`), associated with @hakimov2025turkicnlp. This snapshot differs from the public arXiv table in some cells and sample sizes. Both backends receive the same automatic tokenisation. These are *conditional* scores, not the official tokenisation-aware CoNLL 2018 LAS F1: UPOS is computed over the n words whose boundaries match gold, and UAS/LAS additionally require matched gold and predicted heads, so tokenisation errors drop out of the denominator. ^†^Zero-shot with proxy embeddings: Karakalpak → Uzbek, Kumyk → Tatar, Sakha → Bashkir. ^‡^Silver test sets (translated and automatically annotated); these mainly measure agreement with the process that produced them. Tatar (29 words), Sakha (16), Kumyk (144) and Karakalpak (235) are qualitative examples, not grounds for ranking. Bold: higher score of the two backends. The source’s aggregate is omitted because it mixes gold and silver rows. {#tbl-parsing-results}")
