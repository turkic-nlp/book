# Chapter 8 exercise runs

`verified-output.json` records what the code cells of the five Chapter 8 notebooks (`exercises/08-exercise-*.ipynb`) printed. The worked solutions in the notebooks quote this file. The runner script that produced it is no longer distributed; to reproduce the outputs, run the notebooks.

```sh
pip install "turkicnlp==0.5.0" "stanza==1.11.0" scipy matplotlib requests
jupyter nbconvert --to notebook --execute --inplace exercises/08-exercise-*.ipynb
```

Inputs: UD 2.17 release files (tag `r2.17`), downloaded to `UD217_DIR` and checked against the SHA-256 hashes
in the notebooks (the same hashes as `tables/tbl-ud217-inventory/download-manifest.json`; EN-EWT hashes were
recorded on 19 October 2026). Parsers: Stanza 1.11.0 with the Turkish IMST, Kazakh KTB and Kyrgyz KTMU
checkpoints whose SHA-256 hashes are listed in `experiments/empirical-2026-10/results/parsing_manifest.json`;
the resources file was `resources_1.11.0.json` (SHA-256 `e334b4e2…`, as in that manifest). All parsers
receive gold words. The Kazakh KTB model has seen KTB test data (split-swap rule), so its row is a replay
diagnostic. Not run: TurkicNLP's multilingual Glot500 parser and the custom Azerbaijani Stanza model.

Cross-checks: the Stanza IMST scores on the IMST test set (UPOS 95.18, UAS 78.37, LAS 70.23) and the
Kazakh KTB replay scores (98.74, 96.83, 95.57) equal `tables/tbl-ud217-pretrained-probe`, and the 9,205
BOUN test arcs in Exercise 2 equal the count in `tables/tbl-ud-arc-lengths`.
