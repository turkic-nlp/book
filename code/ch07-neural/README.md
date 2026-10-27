# Chapter 7 reproducibility checks

Run from the book root. The tokenizer and tagging demonstrations are independent; the tagging baseline does not require TurkicNLP.

```sh
pip install "sentencepiece==0.2.1" "transformers==5.3.0" "torch==2.10.0" "accelerate==1.12.0"
python code/ch07-neural/check_examples.py
python code/ch07-neural/check_ud_alignment.py /path/to/ud-treebanks-v2.17/UD_Turkish-IMST /path/to/pinned-berturk-tokenizer
```

The second check requires the tokenizer files from `dbmdz/bert-base-turkish-cased`, revision `b6e1de16c983e0f2c70664591ea3f22810072608`, and a `revision.txt` containing that hash. `ud-alignment.json` records the tested input hashes and counts. Downloading only tokenizer/config files is enough for this check; no encoder weights are used.

`checks.json` records mechanical tests using a tiny random BERT, an actual one-step Trainer run, checkpoint save/reload, and a tiny SentencePiece model trained on synthetic boundary fixtures. These are not morphology accuracy results. The real UD alignment check and synthetic overflow check complement each other: no sentence in this IMST snapshot exceeds the 512-token limit.

To run the full fixed-budget experiment M3 (not executed in this review):

```sh
UD_IMST_DIR=/path/to/ud-treebanks-v2.17/UD_Turkish-IMST python code/ch07-neural/fine_tune.py
```

This downloads the pinned BERTurk encoder if needed, fine-tunes for five epochs, and writes its final checkpoint, all-word dev/test scores, CoNLL-U predictions and provenance to `berturk-morph-tagger/`. The other CoNLL-U columns remain gold/source annotations: do not score them as predictions. Preserve the source files and run manifest with the checkpoint. The model can use an available accelerator; the local smoke check is CPU-only.

`boundary_tokenizer.py` requires segments that concatenate to the original surface. It rejects reserved markers, checks token-ID decoding, and keeps whitespace in a sidecar. This representation demonstrates the boundary contract; it is not a drop-in input stream for an existing language model. Segmenter correctness and downstream benefit require M2 and a separate experiment.
