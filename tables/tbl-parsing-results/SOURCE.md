# Frozen evaluation table

Source: the LaTeX source of the TurkicNLP paper (section 6, evaluation), `tab:parsing-eval`; book reference `hakimov2025turkicnlp` (https://arxiv.org/abs/2602.19174).
Copied on 2026-10-13 from the local manuscript; full source SHA256 `fc72d7382bce68c1fa462e90afaca1766f5ec8e97aa0ce61fb85de2045b1d741`.
`source.tex` is the exact table block. `generate.py` extracts every row to `data.csv` and generates `output.md`, included directly by the chapter. No evaluation was rerun. Published rounded averages are preserved rather than recomputed from rounded rows.

**Version check (19 October 2026).** The public arXiv version (v5, 22 May 2026) reports a different Karakalpak sample (1,126 matched words; Glot500 UPOS/UAS/LAS 82.1/67.5/51.0 instead of 235 words and 77.5/61.7/45.8) and differs by 0.1–0.4 points in several multilingual cells (e.g. Turkish UAS 84.9 vs 84.5, Bashkir LAS 64.1 vs 63.8, average LAS 63.6 vs 63.7). The author decided on 19 October 2026 to keep the manuscript numbers and cite the arXiv paper.
