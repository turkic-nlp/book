"""tbl-hplt-releases (Ch 4, N1-0): the Turkic subsets across HPLT v1.2, v2.0 and v3.0.
Inputs: experiments/n1_corpora/data/{raw/hplt_v1_2_raw.tsv, hplt_v2_turkic.csv, hplt_v3_turkic.csv}."""
import csv, sys
from pathlib import Path
HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "experiments" / "common"))
from bookgen import EXP, read_csv, write_csv, md_table, fmt_count

D = EXP / "n1_corpora/data"
V1 = {"az": "aze", "kk": "kaz", "ky": "kir", "tr": "tur", "tt": "tat", "uz": "uzb"}
v1 = {V1[r["lang"]]: r for r in csv.DictReader(open(D / "raw/hplt_v1_2_raw.tsv", encoding="utf-8"), delimiter="\t") if r["lang"] in V1}
v2 = {r["iso639_3"]: r for r in read_csv(D / "hplt_v2_turkic.csv") if r["row_type"] == "primary" and r["present"] == "1"}
v3 = {r["iso639_3"]: r for r in read_csv(D / "hplt_v3_turkic.csv") if r["row_type"] == "primary" and r["present"] == "1"}
out = []
for iso in sorted(set(v1) | set(v2) | set(v3), key=lambda k: -int(v3.get(k, v2.get(k, {})).get("documents", v2.get(k, {}).get("dedup_docs", 0)) or 0)):
    a, b, c = v1.get(iso, {}), v2.get(iso, {}), v3.get(iso, {})
    out.append({"iso639_3": iso, "language": (b or c)["language"], "subset_v2_v3": c.get("hplt_code", b.get("hplt_code", "")),
                "v1_2_docs": a.get("dedup_docs", ""), "v1_2_words": a.get("dedup_words", ""),
                "v2_docs": b.get("dedup_docs", ""), "v2_words": b.get("dedup_words", ""), "v2_chars": b.get("dedup_chars", ""),
                "v2_cleaned_docs": b.get("cleaned_docs", ""), "v2_cleaned_chars": b.get("cleaned_chars", ""),
                "v3_docs": c.get("documents", ""), "v3_chars": c.get("characters", ""),
                "source": "HPLT v1.2 and v2.0 download pages; HPLT v3.0 sorted manifest; accessed 2026-10-12"})
write_csv(HERE / "data.csv", out)

body = [[r["language"], f"`{r['subset_v2_v3']}`", fmt_count(r["v1_2_docs"]), fmt_count(r["v2_docs"]), fmt_count(r["v2_cleaned_docs"]),
         fmt_count(r["v3_docs"]), fmt_count(r["v2_chars"]), fmt_count(r["v2_cleaned_chars"]), fmt_count(r["v3_chars"])] for r in out]
cap = ("The Turkic subsets across three HPLT releases: v1.2 deduplicated; v2.0 deduplicated (dedup.) and cleaned; v3.0 sorted "
       "(Web Docs Scorer bins 5–10 only). v2.0's cleaned release drops, among others, documents with a language-identification "
       "probability below 0.5 or a Web Docs Scorer value below 5 [@burchell2025hplt, sec. 4.2]. Because v3.0 also contains only bins 5–10, v2.0's cleaned release is the closer comparison on that criterion; the other v3.0 filters were not checked here. "
       "v1.2 does not report characters. Sources: hplt-project.org/datasets/v1.2 and /v2.0, HPLT v3.0 manifest; accessed 12 October 2026.")
md = md_table(["Language", "Subset", "Docs v1.2", "Docs v2.0 dedup.", "Docs v2.0 cleaned", "Docs v3.0", "Chars v2.0 dedup.", "Chars v2.0 cleaned", "Chars v3.0"],
              ["l", "l", "r", "r", "r", "r", "r", "r", "r"], body, cap, "tbl-hplt-releases")
(HERE / "output.md").write_text(md, encoding="utf-8"); print(md)
