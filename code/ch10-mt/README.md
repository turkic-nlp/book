# Kazakh→Kyrgyz tutorial

From the book root: `python code/ch10-mt/train.py path/to/prepared-splits --output nllb-kaz-kir`.
Mechanics checked with Python 3.13, transformers 5.3.0, torch 2.10.0, accelerate 1.12.0,
sacrebleu 2.5.1, sentencepiece 0.2.1. Install compatible dependencies in an isolated environment.
The script downloads the pinned NLLB weights for a full run; mechanical checks use a tiny random model.

Provide UTF-8 `train.tsv`, `validation.tsv`, and `test.tsv`, each with the exact header
`document_id<TAB>src<TAB>tgt`. IDs must identify original source documents consistently across
collections. Preserve corpus provenance and split documents before producing translations or synthetic data.
Do not fabricate document IDs from row numbers to conceal unknown grouping. If document provenance
cannot be recovered, record that limitation and prepare independent evaluation data before using this protocol.

The loader rejects empty/malformed records, duplicate pairs and cross-split document or normalised single-side
text overlap. This conservative text-overlap policy can reject common short sentences; make any alternative
policy explicit and version the prepared data. Hashes identify prepared files, not their upstream provenance.
Store upstream URLs/revisions, licences and the split procedure alongside them.

No sentence is truncated. Over-budget examples stop the run: align and segment source/target together,
preserve document groups and specify reconstruction before evaluating longer inputs. Decoding has a fixed
budget; inspect outputs that reach it. No claims about translation accuracy follow from smoke tests.
