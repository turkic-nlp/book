# Shared helpers and mechanical checks

`common.py` holds the split checks, hashes and Wilson intervals used by the chapter
scripts in `code/ch11-speech/`, `code/ch12-classify/` and `code/ch15-tumlu/`; those
scripts add this folder to `sys.path` themselves. `check.py` imports the helpers of
chapters 4, 11, 13, 15, 16 and 17 from their chapter folders.

Run commands from the book root. To import a helper from your own script, put its
chapter folder (for example `code/ch04-corpus`) on `PYTHONPATH`. No training or data
download happens on import.

## Checked scope

`check.py` exercises leakage guards, arithmetic, corpus sampling/weights, retrieval
alignment/ties, BIO/conversion boundaries, resource query states, and tiny XLM-R,
T5 and Whisper model mechanics. It uses no pretrained model weights and establishes
no task accuracy. `experiments/remaining_revision/mechanical-checks.json` and
`environment.json` record the completed run. `requirements-tested.txt` records
direct package versions, not a universal platform lock.

```bash
python code/common/check.py
# Optional pinned processor + real TUMLU file checks:
python experiments/remaining_revision/fetch_sources.py /tmp/book-sources
python code/common/check.py --sources /tmp/book-sources
```

The optional fetch gets small public model configuration/tokenizer files and the
Kazakh TUMLU-mini Parquet files, with byte-hash verification. It does not get
pretrained weights, speech audio, or gated FLORES data. Historical metadata needed
for parameter counts is saved in `experiments/remaining_revision/data/`:

```bash
python tables/tbl-verified-models/generate.py experiments/remaining_revision/data
python tables/tbl-language-reference/generate.py
python tables/tbl-unicode-reference/generate.py
```

## Full experiment entry points (not run in this revision)

- `code/ch12-classify/classify.py DATA OUTPUT [--lora]`: DATA contains train/dev/test JSONL files.
  Each row has nonempty `id`, `group_id`, `text`, and string `label`. Group IDs
  identify source documents and all their derived excerpts/variants. IDs are
  unique within each split; IDs, groups and normalised exact texts cannot cross
  splits. All evaluation labels must occur in the training schema. The script
  rejects inputs over 512 tokenizer tokens; document chunking is a separate task.
  It saves model/adapter plus tokenizer, verifies fresh-base reload logits, selects
  by development macro-F1 and writes test predictions and a run manifest. Full
  training downloads pinned XLM-R weights. Three epochs is an illustrative setting,
  not a tuned recommendation.
- `code/ch11-speech/speech.py OUTPUT`: downloads the pinned Kazakh FLEURS release and Whisper-small
  weights. It preserves official train/validation/test, reads undecoded audio with
  SoundFile, rejects cross-split transcript duplication and duplicate recording
  paths, and checks mono 16 kHz audio up to 30 seconds. It refuses overlength audio
  or transcripts instead of silently truncating. Investigate any failed release
  check before changing the protocol. Development WER selects the checkpoint;
  baseline/adapted test metrics use identical items and original references. It
  saves all transcripts and raw/normalised WER/CER. The full audio and Trainer run
  remains R10-1; the tiny processor/model check is narrower.
- `code/ch15-tumlu/tumlu.py --config kazakh --audit-only --output OUTPUT`: downloads the pinned
  TUMLU-mini data and writes an audit. The release contains 40 dev and 799 test rows;
  two test rows have empty options. Without `--audit-only`, scoring refuses invalid
  rows unless `--exclude-invalid` explicitly chooses the audited subset (797 test
  items). Their original indices and hashes remain in `audit.json`. Full inference
  downloads mT5-base. It scores candidate letters plus EOS by summed log probability,
  never uses CoT explanations, and saves predictions, support, Wilson intervals and
  analytical chance. Use dev for protocol selection and test only after freezing it.
- `code/ch17-resources/resources.py --iso3 kaz --hub-alias kk --hub-alias kaz --output FILE`: queries
  public Hub tags with current supported API arguments, deduplicates IDs, and
  distinguishes observed zero, unknown and query failure. It is not a comprehensive
  quality census. UD, FST quality and Wikipedia remain explicitly unchecked until
  independent source observations are supplied.

## Helper contracts

- `code/ch04-corpus/corpus.py`: full-stream reservoir sampling, script-letter shares, raw FST
  recognition, unrestricted-LID signal aggregation and weighted document strata.
  Supply actual language-specific callbacks and pin their revisions. Human labels
  and confidence intervals are still required for corpus-quality estimates.
- `code/ch13-retrieval/retrieval.py`: align by `(id, split)` within selected varieties before encoding;
  score cosine retrieval with exact-duplicate positives and fractional tie credit.
  Export authorisation, encoder/pooling settings, role prefixes, checked CTS
  mappings and independent relevance judgments remain the caller's responsibility.
- `code/ch16-transfer/transfer.py`: reduced PER/ORG/LOC schema, strict BIO-to-span reconstruction,
  conservative unique-boundary mapping. Mapping ambiguity raises an error and must
  be counted. Prefix probing is quadratic and intended for short examples.
- `code/common/common.py`: split validation, stable hashes and Wilson intervals. Exact text
  checks do not detect every near-duplicate or semantic leakage; audit provenance.

## Limits

These checks do not include full ASR or classification training, retrieval matrices,
community or speaker judgments, or a comprehensive resource census. Measured
pretrained-model results are in `experiments/empirical-2026-10/`.
