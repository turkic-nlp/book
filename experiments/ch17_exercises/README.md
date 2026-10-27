# Chapter 17 exercises: recorded outputs

`verified-output.json` records what the code cells of the five Chapter 17 notebooks (`exercises/17-exercise-*.ipynb`) printed, with the date, package versions and the SHA-256 of every downloaded file. The worked solutions in the notebooks quote this file. To reproduce the outputs, run the notebooks.

```bash
pip install requests huggingface_hub fasttext-wheel transformers torch sentencepiece "turkicnlp[hfst]==0.5.0"
GLOTLID_PATH=… NLLB_PATH=… MODELS_DIR=… jupyter nbconvert --to notebook --execute --inplace exercises/17-exercise-*.ipynb
```

## Inputs

- **Audit (Exercise 1):** the book's UD 2.17 inventory (`tables/tbl-ud217-inventory/data.csv`),
  `git ls-remote` on the Apertium repositories, the language-pair table of the TIL corpus README
  (`turkic-interlingua/til-mt@7d988cc`, hash-checked), X-WMT and SIB-200 file availability, the
  NLLB-200 tokenizer's language codes, GlotLID v3 labels and Hugging Face Hub model tags through
  `code/ch17-resources/resources.py`. The live columns are dated observations (20 October 2026); the
  Hub queries failed from the book's network (HTTP 403 from the proxy) and are recorded as errors.
  `resource-audit-2026-10-20.json` keeps every observation with its query, status, error and time.
- **CARE (Exercise 2):** the README files of KazNERD (`bd4333d`) and KyrgyzNER (`b76b9c9`), hash-checked.
- **FST extension (Exercise 3):** TurkicNLP 0.5.0's Apertium Kazakh analyser (`kaz.automorf.hfst`,
  SHA-256 prefix printed in the output), the KazNERD train and test splits, `hfst` for compiling
  and union. The case-ending rules were written for the exercise and have not been reviewed by a
  speaker.
- **Projection (Exercise 4):** UD 2.17 Turkish, Azerbaijani, Uzbek and Kyrgyz TueCL test files
  (hash-checked), linked by `parallel_id`; paraphrase-xlm-r-multilingual-v1 (`c2e1945`) layer 8
  for the embedding aligner.
- **Plan checker (Exercise 5):** no data; the draft plan is invented.

## Runtime

Everything runs in a few minutes on a CPU.

## Interpretation notes (20 October 2026)

- A keyword search that returns no match cannot establish that governance is undocumented
  without reading the full source. The printed labels are search results.
- Analyser agreement and coverage are not independent linguistic validation. Machine
  timings exclude candidate review and maintenance.
- Projection scores measure UPOS agreement, not alignment precision, and include punctuation.
  Only shared parallel IDs are evaluated. Turkish remains in native spelling in the string
  method; target words are converted to CTS. The embedding method uses a 256-token limit
  and does not explicitly exclude zero vectors for truncated words.
- The plan checker detects empty fields; it cannot verify permissions or community approval.
