# Experiments and recorded outputs

Paths are relative to the book root. Every number in the book comes from a file in one of these folders, from a table's `data.csv` under `tables/`, or from a figure's `data.csv` under `figures/`. `python scripts/make_all.py --list` lists the table and figure generators; `python scripts/make_all.py` reruns them.

| Folder | Contents |
|---|---|
| `common/` | `turkic_languages.csv` (the 24 languages with ISO 639-3 code, branch, primary script and corpus codes) and `bookgen.py` (helpers for the table and figure generators) |
| `n1_corpora/` | Corpus inventory and filter thresholds for Chapter 4: HPLT v2/v3, Common Crawl, CulturaX, mC4, FineWeb-2 and Wikipedia sizes (`fetch_*.py`, `build_availability.py`, `exp_word_length.py`). Collected data are in `data/` (each source has a `*_SOURCE.md` note) and `results/` |
| `n2_meaning/` | Token-budget (chunk content) measurement for Chapter 13 (`exp_chunk_content.py`, `chunk-study/`) and the curated `data/semantic_resources.csv` |
| `empirical-2026-10/` | Pretrained-model inference and descriptive measurements (parsing, NER, translation, retrieval, TUMLU, word lengths); frozen predictions in `results/`, tables and figures from `build_assets.py`. See its README |
| `chNN_exercises/` | `verified-output.json`: the recorded outputs quoted in the worked solutions of `exercises/NN-exercise-*.ipynb` |
| `ch789_revision/` | Source manifest, KazNERD tokeniser audit (output of `code/ch09-ner/audit_release.py`) and tiny-model mechanical checks for Chapters 8–10 |
| `remaining_revision/` | Outputs of `code/common/check.py`, the TUMLU audit, source manifests and the model metadata used by `tables/tbl-verified-models` |

Hugging Face, HPLT and Wikipedia were not reachable from the build environment on 12 October 2026. The HPLT, CulturaX, mC4-file and Wikipedia numbers were therefore read in a browser with the same logic as the fetch scripts; the `*_SOURCE.md` notes record this.
