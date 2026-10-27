# KazNERD tutorial

Run from the book root: `python code/ch09-ner/train.py`.
The script mirrors Chapter 9's sequential training blocks. It requires the authors' repository
at `KazNERD/`, checked out at `bd4333d0f5952b9fafb2ef2ac2fefa0ad3c0333f`; input files
are `KazNERD/KazNERD/IOB2_{train,valid,test}.txt`. Full training downloads the pinned
XLM-R-large weights and needs suitable hardware. No full training scores are claimed here.

Mechanics were checked with transformers 5.3.0, datasets 4.6.1, torch 2.10.0,
accelerate 1.12.0, seqeval 1.2.2 and sentencepiece 0.2.1.
Install compatible dependencies in an isolated environment.

To repeat the data audit without model weights, download the tokenizer files from
`FacebookAI/xlm-roberta-large` at revision `c23d21b0620b635a76227c604d44e43a9f0ee389`, then run:

```sh
python code/ch09-ner/audit_release.py path/to/KazNERD/KazNERD path/to/tokenizer audit.json
```

`ner_utils.py` rejects invalid tag syntax, missing words, overlong encodings and prediction/gold
shape mismatches. The training-only orphan-I repair is recorded, while evaluation gold is unchanged.
Span scoring is strict IOB2. Do not silently repair predicted labels or alter the scorer when comparing runs.

The stored audit counts all sentences and words. Tiny random-model checks, recorded in
`experiments/ch789_revision/mechanical-checks.json`, exercised the APIs, loss, generation, scoring and checkpoint reloads; they were not quality evaluations.
