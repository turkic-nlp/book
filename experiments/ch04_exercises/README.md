# Chapter 4 exercise outputs

`verified-output.json` records what the code cells of the four Chapter 4 notebooks (`exercises/04-exercise-*.ipynb`) printed. The worked solutions in the notebooks quote this file. The runner script that produced it is no longer distributed; to reproduce the outputs, run the notebooks.

- Run on 18 October 2026 (UTC) on the author's machine (Linux VM, aarch64, Python 3.10), TurkicNLP 0.5.0, GlotLID v3 (`model_v3.bin`, local copy via `GLOTLID_PATH`), Apertium analysers read with `pyhfst` 1.4.0.
- Data: X-WMT test sets from `github.com/turkic-interlingua/til-mt` (master branch).
- LaBSE (Exercise 3) was not installed; that cell records the failure instead of a number.
- The documents in Exercise 1 are built from test sentences of known language. They check the audit signals; they do not estimate contamination in any corpus.
