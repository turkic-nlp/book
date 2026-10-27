# Provenance: HPLT v2.0 Turkic statistics

- **Source:** https://hplt-project.org/datasets/v2.0 (HPLT Monolingual Datasets 2.0, release of September 2024, 193 languages; download root `data.hplt-project.org/two/`). Accessed 2026-10-12.
- **Extraction:** the page embeds a JSON object per language with `cleaned`, `collectionsMerged` and `annotated` blocks. It was parsed in a browser (the sandboxed shells cannot reach hplt-project.org) with the same regexes as `../fetch_hplt_v2.py`; raw values are in `raw/hplt_v2_raw.tsv`, and `python fetch_hplt_v2.py --offline` rebuilds `hplt_v2_turkic.csv` from them.
- **Columns:** `dedup_*` = `collectionsMerged` (deduplicated release; identical to `annotated` for every Turkic row); `cleaned_*` = the filtered "cleaned" release. `*_words` is the page's `text_wcwords` (whitespace-delimited `wc -w` words), `*_chars` = characters, `*_bytes` = UTF-8 bytes of text.
- **Turkic coverage:** the same 11 subsets as v3.0 (tur_Latn, azj_Latn, azb_Arab, tuk_Latn, kaz_Cyrl, kir_Cyrl, tat_Cyrl, bak_Cyrl, crh_Latn, uzn_Latn, uig_Arab). Sizes are as labelled by the corpus's language identifier, not audited.
