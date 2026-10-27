# Chapter 15 exercises: recorded outputs

`verified-output.json` records what the code cells of the five Chapter 15 notebooks (`exercises/15-exercise-*.ipynb`) printed, with the date, package versions and the SHA-256 of every downloaded file. The worked solutions in the notebooks quote this file. To reproduce the outputs, run the notebooks.

```bash
pip install "stanza==1.11.0" sacrebleu torch transformers sentencepiece llama-cpp-python \
    fasttext-wheel pyarrow requests "turkicnlp[hfst]==0.5.0"
STANZA_RESOURCES_DIR=… QWEN_GGUF=… QWEN_TOKENIZER=… GLOTLID_PATH=… TUMLU_DIR=data/tumlu-mini jupyter nbconvert --to notebook --execute --inplace exercises/15-exercise-*.ipynb
```

## Inputs

- **UD 2.17** Kazakh-KTB and Turkish-IMST train/test files (hash-checked) and Stanza 1.11.0's
  `kk` and `tr` checkpoints. Stanza trains its Kazakh model on the KTB test file (Chapter 8), so
  the Kazakh numbers are a replay diagnostic.
- **X-WMT** English–Turkish test set (`turkic-interlingua/til-mt@7d988cc`), TurkicNLP's Apertium
  Turkish analyser and generator, and NLLB-200 distilled 600M (`NLLB_PATH`).
- **TUMLU-mini** Kazakh dev/test parquet files, revision `3523de73e1d1d784118d328f40b49d53afd6f334`.
  They are not redistributed: download them into `data/tumlu-mini/` (ignored by Git), e.g.
  `huggingface-cli download jafarisbarov/TUMLU-mini --repo-type dataset --revision 3523de7… --include "kazakh/*" --local-dir data/tumlu-mini`.
  The code checks their SHA-256 against `experiments/remaining_revision/` (dev `cd73f20c…`,
  test `01533125…`).
- **Qwen2.5-1.5B-Instruct** (revision `989aa79`) as a q8_0 GGUF file run with llama-cpp-python
  0.3.16 (as in Chapter 14), and **GlotLID v3**. KazNERD test sentences
  (`IS2AI/KazNERD@bd4333d`) calibrate the language identifier.

## Caching and runtime

Stanza predictions, NLLB translations, Qwen replies and letter log-probabilities are cached in
`BOOK_DATA_DIR` (`ch15-stanza-*.json`, `ch15-replies.jsonl`). On two CPU threads the run took about
an hour, most of it Exercise 4 (957 TUMLU prompts: 160 rotated development prompts and 797 test prompts).

## Interpretation notes (editorial review, 20 October 2026)

The recorded outputs are unchanged. Read them with the revised notebook solutions:

- Exercise 1 averages the independence product over actual sentence lengths for the overall
  estimate, but uses fixed representative lengths (3, 8, 15, 26) for the printed length bins.
  Sentence-exact here checks feature bundles only and includes punctuation.
- Exercise 2 partitions against the official UD training vocabulary, which is not the Kazakh
  Stanza model's actual training exposure. Error rates alone do not identify causal effects of novelty.
- Exercise 3 uses separately selected perturbation sets. Generated forms still need contextual
  validation. The printed metric signatures describe the corpus comparison, not all sentence-level
  perturbation settings. Despite the output caption, the A/B key remains in the same in-memory
  records; exporting a blinded sheet with a separate key is still required.
- Exercise 4 changes inference implementation as well as precision relative to the chapter's
  separate baseline. The score difference does not isolate a quantisation effect. Rotation
  aggregation does not guarantee removal of position bias.
- Exercise 5 uses a provisional threshold estimated from target-labelled Kazakh news. It is not
  probability calibration or validation against other languages and mixed spans. The printed
  one-per-category excerpts are previews, not complete annotation records or a representative
  sample for estimating error rates.
