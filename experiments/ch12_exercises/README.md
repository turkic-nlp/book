# Chapter 12 exercises: recorded outputs

`verified-output.json` records what the code cells of the five Chapter 12 notebooks (`exercises/12-exercise-*.ipynb`) printed, with the date, package versions and the SHA-256 of every downloaded file. The worked solutions in the notebooks quote this file. To reproduce the outputs, run the notebooks.

```bash
pip install torch transformers peft scikit-learn psutil requests "turkicnlp==0.5.0"
jupyter nbconvert --to notebook --execute --inplace exercises/12-exercise-*.ipynb
```

## Models and data

- **Models**, at the Hugging Face revisions pinned in `MODELS`: Glot500-base (fine-tuned in
  Exercises 2, 3 and 5), the XLM-R vocabulary of `sentence-transformers/paraphrase-xlm-r-multilingual-v1`,
  the Llama 3, OLMo 3 and Qwen3.6 tokenizers, and Qwen2.5-1.5B-Instruct (Exercise 4). They are
  read from a local Hugging Face cache (`HF_HUB_DIR`), a folder of copies named
  `models--org--name--revision` (`MODELS_DIR`) or the Hub. The book's run read local copies of the
  pinned snapshots because the Hub was not reachable from the machine that ran it.
- **Data**, commit-pinned on GitHub: SIB-200 (`dadelani/sib-200@efad32e`, annotated splits),
  Kardeş-NLU's Kazakh XCOPA (`lksenel/Kardes-NLU@48eea77`) and the BERTurk evaluation tables
  (`stefan-it/turkish-bert@0ab49e2`, `OLD_EVALUATIONS.md`).

## Runtime and caching

Everything runs on the CPU. Each fine-tuning run (ten epochs on 701 sentences) took 15 minutes
with LoRA, 20 minutes with partial fine-tuning (word embeddings frozen) and about 24 minutes with the vocabulary extension on
two CPU threads; the whole set took about five hours. Every run is cached as JSON in
`BOOK_DATA_DIR/ch12-runs/` (default `~/.cache/turkic-nlp-book`), keyed by its configuration, so a
rerun only trains what is missing. Peak memory is measured separately in a fresh process per setting
(`peak_memory`), because the resident memory of a long-running process includes earlier runs.
Exercise 4's alternative scores are cached in `ch12-xcopa-scores.json`. Exercise 5 writes a 1.2 GB
adapter to `ch12-ext-adapter/` (PEFT saves the whole resized embedding matrix).

## Interpretation correction (20 October 2026)

The historical `full` mode freezes word embeddings and trains 86,047,495 parameters. It is partial fine-tuning, not a full-model baseline. The saved output labels remain unchanged for traceability. The exercise runner also uses truncation at 256 tokens, unlike the hands-on classifier’s overlength rejection; affected native/converted inputs were not counted in the saved report. The reported times cover complete runs, not individual epochs. No training was rerun for this editorial correction.
