# Chapter 14 exercises: recorded outputs

`verified-output.json` records what the code cells of the four Chapter 14 notebooks (`exercises/14-exercise-*.ipynb`) printed, with the date, package versions and the SHA-256 of every downloaded file. The worked solutions in the notebooks quote this file. To reproduce the outputs, run the notebooks.

```bash
pip install llama-cpp-python fasttext-wheel requests "turkicnlp[hfst]==0.5.0"
QWEN_GGUF=/path/qwen2.5-1.5b-instruct-q8_0.gguf GLOTLID_PATH=/path/model_v3.bin jupyter nbconvert --to notebook --execute --inplace exercises/14-exercise-*.ipynb
```

## Models and data

- **Generator and judge:** Qwen2.5-1.5B-Instruct, Hugging Face revision
  `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`, converted with llama.cpp
  (`convert_hf_to_gguf.py --outtype q8_0`, llama.cpp commit `d8d9297`) and run with
  llama-cpp-python 0.3.16 on two CPU threads, greedy decoding. The GGUF file's SHA-256 is printed
  by the core cell. A 16-bit run in PyTorch was too slow on this CPU (about 0.5 tokens per second).
- **Language identification:** GlotLID v3 (`model_v3.bin`, SHA-256 `a818b6bd…afc9e`), full label set.
- **Morphology:** TurkicNLP's Apertium analysers for Kazakh (Cyrillic) and Uzbek (Latin), raw
  lookup with `hfst`.
- **Data:** KazNERD test split (`IS2AI/KazNERD@bd4333d`, CC BY 4.0) and SIB-200 Kazakh
  (`dadelani/sib-200@efad32e`, CC BY-SA 4.0). The Taboo targets and the cultural questions were
  written for these exercises and have not been checked by a native speaker.

## Caching

Every model reply is stored with its messages in `BOOK_DATA_DIR/ch14-replies.jsonl` (default
`~/.cache/turkic-nlp-book`); a rerun with the same file reproduces the outputs exactly and generates
only what is missing. The book's run made 507 calls in about 90 minutes. One small model is used
throughout: its errors illustrate the measurements and are not a comparison of models.
