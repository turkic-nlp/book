# Provenance: corpus sizes for N1-0 (other than HPLT v2.0/v3.0)

All accessed 2026-10-12. Raw snapshots are in `raw/`; `../fetch_corpus_sizes.py` refreshes the machine-readable ones and `../build_availability.py` merges everything into `corpus_availability_long.csv`, `corpus_availability_docs.csv` and `cc_turkic_share.csv`.

| File | Source | How obtained | Measure |
|---|---|---|---|
| `raw/hplt_v1_2_raw.tsv` | https://hplt-project.org/datasets/v1.2 (embedded JSON, 75 languages) | browser, regex in `fetch_corpus_sizes.py:hplt_v1_2` | raw / dedup / cleaned words, documents, size (compressed) |
| `raw/fineweb2_language_distribution.csv` | https://github.com/huggingface/fineweb-2/blob/main/fineweb2-language-distribution.csv | curl (full file, unchanged) | words, documents, UTF-8 bytes per subset and split; `*_removed` rows are the filtered-out data |
| `raw/culturax_card.tsv` | https://huggingface.co/datasets/uonlp/CulturaX (dataset card table; the card is gated for raw download but rendered on the page) | browser, hand-checked | documents; tokens (only for the larger languages; `-` on the card) |
| `raw/mc4_mt5_table6.tsv` | Xue et al. 2021, mT5, Table 6 (https://arxiv.org/abs/2010.11934, via ar5iv) | browser | tokens (B) and pages (M) as rounded in the paper; mC4 version used for mT5 |
| `raw/mc4_hf_allenai_c4_files.tsv` | Hugging Face API, `allenai/c4` tree `multilingual/` | browser, paginated API (`fetch_corpus_sizes.py:mc4_files`) | number and gzip bytes of train shards (mC4 v3.1.0 files) |
| `raw/cc100_xlmr_table6.tsv` | Conneau et al. 2020, XLM-R, Table 6 (https://arxiv.org/abs/1911.02116, via ar5iv); download sizes from https://data.statmt.org/cc-100/ | browser | tokens (M), size (GiB, uncompressed); `.xz` download size |
| `raw/cc_crawl_languages.csv` | https://github.com/commoncrawl/cc-crawl-statistics `plots/languages.csv` | curl (full file, unchanged) | pages per CLD2 primary language per crawl |
| `raw/wikipedia_siteinfo.tsv` | MediaWiki API `meta=siteinfo&siprop=statistics` on each `<code>.wikipedia.org` | browser (`fetch_corpus_sizes.py:wikipedia`) | content articles, pages, edits, active users |

## Code mapping and caveats

- Codes are mapped to the book's 24-language list (`../../common/turkic_languages.csv`) in `build_availability.py`. ISO 639-1 `az` is counted as North Azerbaijani; `uz` and FineWeb2 `uzn_*` as Uzbek. FineWeb2 subsets for Shor (`cjs_Cyrl`, 32 documents), Karaim (`kdr_Latn`, 3 documents) and Southern Uzbek (`uzs_Arab`, 13,061 documents) are outside the list and not counted.
- FineWeb2 counts sum all script subsets of a language (e.g. Uzbek = `uzn_Latn` + `uzn_Cyrl`), train split only, and exclude the `_removed` rows.
- **The measures are not interchangeable.** Documents (HPLT, FineWeb2, CulturaX), pages (mC4, Common Crawl) and articles (Wikipedia) are counted differently, and each corpus counts tokens with its own tokenizer. Compare corpora by documents only with that caveat, and never compare token counts across corpora.
- Wikipedia article counts include bot-generated stubs (Tatar: 709k articles against 196k FineWeb2 documents; South Azerbaijani similar). They measure Wikipedia size, not text volume.
- No Wikipedia exists (2026-10-12) for Khakas, Nogai, Kumyk, Ottoman Turkish, Khalaj or Old Turkic; their API requests failed.
- Common Crawl's language is CLD2's primary language. CLD2 labels only 9 Turkic languages: aze, bak, kaz, kir, tat, tuk, tur, uig, uzb. Language annotation starts with CC-MAIN-2018-34.
- All sizes are as labelled by each corpus's own language identifier and have not been audited (N1-1).
