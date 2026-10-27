# Chapter 16 exercises: recorded outputs

`verified-output.json` records what the code cells of the five Chapter 16 notebooks (`exercises/16-exercise-*.ipynb`) printed, with the date, package versions and the SHA-256 of every downloaded file. The worked solutions in the notebooks quote this file. To reproduce the outputs, run the notebooks.

```bash
pip install sklearn-crfsuite scikit-learn scipy torch transformers sentencepiece sacrebleu \
    "stanza==1.11.0" requests "turkicnlp[hfst]==0.5.0"
STANZA_RESOURCES_DIR=… MODELS_DIR=… NLLB_PATH=… jupyter nbconvert --to notebook --execute --inplace exercises/16-exercise-*.ipynb
```

## Inputs

- **NER (Exercise 1):** KazNERD training split (`IS2AI/KazNERD@bd4333d`, 20,000 sentences sampled
  with seed 0) and the KyrgyzNER test split (`Akyl-AI/KyrgyzNER@b76b9c9`), both hash-checked;
  `sklearn-crfsuite` with the Chapter 9 features. Conversion: TurkicNLP 0.5.0 transliterators to
  the Common Turkic Script (CTS); span mapping with `code/ch16-transfer/transfer.py`.
- **Classification (Exercises 2 and 3):** SIB-200 (`dadelani/sib-200@efad32e`) for ten language
  varieties; sentence vectors from paraphrase-multilingual-MiniLM-L12-v2 (`e8f8c21`),
  paraphrase-xlm-r-multilingual-v1 (`c2e1945`) and the NLLB-200 distilled 600M encoder, mean-pooled
  as in Chapter 13 (the same vector cache).
- **Synthetic data (Exercise 4):** X-WMT Kazakh–Kyrgyz test set (`turkic-interlingua/til-mt@7d988cc`,
  500 pairs) and NLLB-200 distilled 600M, greedy decoding; chrF from sacrebleu.
- **Code-switching (Exercise 5):** UD 2.17 Turkish–German SAGT and Turkish IMST test files
  (hash-checked) and Stanza 1.11.0's Turkish checkpoint.

## Caching and runtime

Embeddings (`ch13-vectors/`), NLLB translations (`ch16-nllb.json`, saved after every batch) and
Stanza tags (`ch16-stanza-*.json`) are cached in `BOOK_DATA_DIR`. On two CPU threads Exercise 4 took
about 40 minutes (1,000 translations) and Exercise 1 several minutes (two CRFs); the others take
minutes once the vectors are cached.

## Interpretation notes (20 October 2026)

The revised worked solutions preserve recorded outputs while clarifying that:

- NER scores use token spans and a permissive local BIO parser. The separate strict
  character-mapping test uses space-joined text, not original document offsets.
- Encoder comparisons include different truncation limits (128 for paraphrase encoders,
  512 for NLLB). Matched sample counts do not establish matched compute or pretraining.
- Sampling changes content exposure and repetition as well as language proportions.
- The round-trip filtering probe selects benchmark outputs; it does not test adaptation.
  Any follow-up training must use separate synthetic training data.
- Synthetic noun replacement has an intended tag but needs contextual validation.
