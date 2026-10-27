# Chapter 13 exercises: recorded outputs

`verified-output.json` records what the code cells of the four Chapter 13 notebooks (`exercises/13-exercise-*.ipynb`) printed, with the date, package versions and the SHA-256 of every downloaded file. The worked solutions in the notebooks quote this file. To reproduce the outputs, run the notebooks.

```bash
pip install torch transformers sentencepiece scipy bm25s requests "turkicnlp[hfst]==0.5.0"
jupyter nbconvert --to notebook --execute --inplace exercises/13-exercise-*.ipynb
```

## Models and data

- **Encoders**, at the revisions pinned in `MODELS`: `paraphrase-multilingual-MiniLM-L12-v2` and
  `paraphrase-xlm-r-multilingual-v1` (mean pooling, 128-token ceiling, as configured), and the
  NLLB-200 distilled 600M encoder read from TurkicNLP's model folder, as its `embeddings`
  processor does. Tokenizers only: Glot500-base, Llama 3, OLMo 3 and Qwen3.6. The book's run read
  local copies of the pinned snapshots because the Hugging Face Hub was not reachable from the
  machine that ran it; the NLLB weights used have SHA-256 `c26fea1b…dec41`.
- **Data**, commit-pinned on GitHub: SIB-200 (`dadelani/sib-200@efad32e`: the 1,004 FLORES-200
  sentences of its annotated splits, CC BY-SA 4.0), Kardeş-NLU STS test sets
  (`lksenel/Kardes-NLU@48eea77`) and KazQAD's information-retrieval collection, topics and qrels
  (`IS2AI/KazQAD@ab8684a`, CC BY-SA 4.0).

## Runtime and caching

On two CPU threads the encoders took about 50 minutes for all sentence sets (Exercises 1 and 3);
Exercise 2 builds a context-free Apertium lemma map for the 1.24 million word types of KazQAD and
seven BM25 indexes in about 15 minutes; Exercise 4 takes a few minutes. Vectors (`ch13-vectors/`),
the lemma map (`ch13-kazqad-lemmas.json`) and the BM25 runs (`ch13-kazqad-run-*.json`, top 100
passages per question) are cached in `BOOK_DATA_DIR` (default `~/.cache/turkic-nlp-book`).

## Interpretation and protocol notes (20 October 2026)

The saved sentence-retrieval run sorts SIB-200 rows by ID separately per language without the hands-on loader’s explicit uniqueness/coverage assertions. Its `argmax` uses the first candidate for ties rather than fractional tie credit. The paraphrase encoders truncate at 128 tokens and NLLB at 512; CTS retains the original NLLB language token. No new alignment, truncation or contamination audit was run in the editorial pass. Setting `src_lang` to `eng_Latn` selects an English token; it does not remove the language token. Recorded outputs are unchanged.
