# Chapter 10 exercise runs

`verified-output.json` records what the code cells of the seven Chapter 10 notebooks (`exercises/10-exercise-*.ipynb`) printed, with the date, package versions and the SHA-256 of every downloaded file. The worked solutions in the notebooks quote this file. To reproduce the outputs, run the notebooks.

```sh
pip install "turkicnlp[hfst]==0.5.0" torch transformers sentencepiece sacrebleu requests
jupyter nbconvert --to notebook --execute --inplace exercises/10-exercise-*.ipynb
```

Recorded runs (19 October 2026):

- EX2, EX4, EX5, EX6 (NLLB-200 distilled 600M, float32, CPU): Linux VM on the author's computer (aarch64,
  4 cores; torch 2.5.1, transformers 4.46.3, sacrebleu 2.6.0). The model was a local copy
  (`model.safetensors` SHA-256 `c26fea1b0788456e3e0d6dfd0165cacec798a0b6d957c9045a234826994dec41`); the
  Hub revision pinned in the chapter (`f8d333a`) could not be checked against it from that environment.
  Greedy decoding unless stated, 256-token ceiling. Every translation is in `nllb-translations.jsonl`
  (the cache the notebooks write: source/target code, beams, ceiling, source, output, ceiling flag,
  per-sentence generation time).
- EX1, EX3, EX7: the book's cloud container (Python 3.11; TurkicNLP 0.5.0 Apertium Kazakh analyser and
  Tatar generator). EX7 needs an LLM server and Nogai references and printed that it was not configured.

Inputs: TIL release `til-mt@7d988cc` (X-WMT test sets and `til_corpus/README.md`, MIT), KyrgyzNER
`b76b9c9` (MIT; monolingual Kyrgyz for EX5), `apertium-kaz-tat@028c57b` bilingual dictionary (GPL).
SHA-256 hashes of every file read are recorded under `runs.*.fetched_sha256`. X-WMT text is tokenised;
`detok` in the notebooks removes spaces around punctuation and apostrophes, a heuristic that also joins
some quotation marks to the neighbouring word.

FLORES-200 was not used: its archive host was not reachable from either environment.
