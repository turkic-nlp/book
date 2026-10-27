# Chapter 9 exercise runs

`verified-output.json` records what the code cells of the six Chapter 9 notebooks (`exercises/09-exercise-*.ipynb`) printed. The worked solutions in the notebooks quote this file. The runner script that produced it is no longer distributed; to reproduce the outputs, run the notebooks.

```sh
pip install "turkicnlp[hfst]==0.5.0" "stanza==1.11.0" sklearn-crfsuite transformers sentencepiece requests
jupyter nbconvert --to notebook --execute --inplace exercises/09-exercise-*.ipynb
```

Inputs (commit-pinned, SHA-256 checked in the notebooks): KazNERD `bd4333d`, KyrgyzNER `b76b9c9`
(github.com/Akyl-AI/KyrgyzNER, MIT), Starlang Turkish NER `nerdata.txt` `9d0e105`, TRopBank frames `4578d14`,
Turkish WordNet `89fee78`, UD 2.17 Turkish IMST train. Models: the Stanza 1.11.0 KazNERD checkpoint
(`kk/ner/kazNERD.pt`, SHA-256 `cb5ba19c…`, as in `experiments/empirical-2026-10/results/ner_manifest.json`),
the Apertium Kazakh transducer shipped with TurkicNLP 0.5.0, and the Glot500 and NLLB-200 tokenisers from
TurkicNLP's local model folder. All taggers receive gold words.

Not run in the recorded environment (no Hugging Face Hub, no GPU, no LLM server): the BERTurk and XLM-R
tokenisers and fine-tuning runs of Exercise 2, and the LLM rows of Exercise 6. The cells print that instead
of numbers. Cross-check: Exercise 1 reproduces the chapter's KazNERD baseline (strict micro F1 94.94).
