# Head direction of `compound:lvc` in UD 2.17

Recompute from a clean official release:

```sh
python tables/tbl-ud217-inventory/fetch.py /tmp/clean-ud217
python tables/tbl-ud217-lvc-direction/generate.py /tmp/clean-ud217
```

Without the source argument, the generator redraws `output.md` from the frozen `data.csv`.
Inputs are the 48 hash-verified release files of `tables/tbl-ud217-inventory/download-manifest.json`
(all splits of the 25 Turkic treebanks). For every `compound:lvc` arc the generator records whether the
head is VERB/AUX ("verb head") or another UPOS ("nominal head"), and whether the dependent precedes the head.
The `source` column of `data.csv` lists the URL and SHA-256 hash of every counted file.
This is an annotation-convention diagnostic, not a parser result; generated on 19 October 2026.
