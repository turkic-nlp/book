"""N1-3: per-language filter thresholds of FineWeb2 vs. the English defaults of datatrove's filters.

Downloads configs/<subset>.yml from github.com/huggingface/fineweb-2 for every Turkic subset (plus rus_Cyrl)
and writes data/fineweb2_filter_thresholds.csv. English defaults are the datatrove constructor defaults
(GopherQualityFilter, GopherRepetitionFilter, FineWebQualityFilter; datatrove main @ 1977fbb, 2026-09-30;
copies in data/raw/datatrove_filters/). FineWeb2 overrides only some parameters (see
data/raw/fineweb-2-pipeline.py, lines 245-285): min_stop_words stays 2, char_duplicates_ratio is 0.1.
Usage: python fetch_fineweb2_configs.py [--offline]   (offline: use data/raw/fineweb2_configs/)
"""
from __future__ import annotations
import csv, sys
from pathlib import Path
import yaml

HERE = Path(__file__).resolve().parent
RAW = HERE / "data" / "raw" / "fineweb2_configs"
BASE = "https://raw.githubusercontent.com/huggingface/fineweb-2/main/configs/"
SUBSETS = ["tur_Latn", "azj_Latn", "azj_Cyrl", "azb_Arab", "tuk_Latn", "tuk_Cyrl", "gag_Latn", "gag_Cyrl", "kaz_Cyrl", "kir_Cyrl",
           "tat_Cyrl", "tat_Latn", "bak_Cyrl", "crh_Latn", "crh_Cyrl", "kaa_Cyrl", "kaa_Latn", "nog_Cyrl", "kum_Cyrl", "krc_Cyrl",
           "uzn_Latn", "uzn_Cyrl", "uig_Arab", "uig_Latn", "uig_Cyrl", "sah_Cyrl", "alt_Cyrl", "tyv_Cyrl", "kjh_Cyrl", "chv_Cyrl",
           "ota_Arab", "rus_Cyrl"]
ENGLISH = {"subset": "English defaults (datatrove)", "min_avg_word_length": 3, "max_avg_word_length": 10,
           "max_non_alpha_words_ratio": 0.8, "line_punct_thr": 0.12, "new_line_ratio": 0.3, "dup_line_frac": 0.3,
           "top_2gram": 0.2, "dup_5gram": 0.15, "language_score": "", "n_stopwords": 8,
           "stopwords_head": "the be to of and that have with",
           "source": "datatrove main@1977fbb (2026-09-30) constructor defaults; STOP_WORDS in gopher_quality_filter.py"}


def main():
    if "--offline" not in sys.argv:
        import requests
        RAW.mkdir(parents=True, exist_ok=True)
        for s in SUBSETS:
            r = requests.get(BASE + s + ".yml", timeout=60)
            if r.ok:
                (RAW / f"{s}.yml").write_text(r.text, encoding="utf-8")
    rows = [ENGLISH]
    for s in SUBSETS:
        p = RAW / f"{s}.yml"
        if not p.exists():
            continue
        c = yaml.safe_load(p.read_text(encoding="utf-8"))
        rows.append({"subset": s, "min_avg_word_length": c["min_avg_word_length"], "max_avg_word_length": c["max_avg_word_length"],
                     "max_non_alpha_words_ratio": c["max_non_alpha_words_ratio"], "line_punct_thr": c["line_punct_thr"],
                     "new_line_ratio": c["new_line_ratio"], "dup_line_frac": c["dup_line_frac"],
                     "top_2gram": dict(map(tuple, c["top_n_grams"]))[2], "dup_5gram": dict(map(tuple, c["dup_n_grams"]))[5],
                     "language_score": c["language_score"], "n_stopwords": len(c["stopwords"]),
                     "stopwords_head": " ".join(c["stopwords"][:8]),
                     "source": f"github.com/huggingface/fineweb-2 configs/{s}.yml, accessed 2026-10-12"})
    out = HERE / "data" / "fineweb2_filter_thresholds.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(ENGLISH)); w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} rows -> {out}")


if __name__ == "__main__":
    main()
