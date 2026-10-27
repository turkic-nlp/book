# Measured empirical baselines, 17–18 October 2026

This suite contains full-dataset **pretrained inference and descriptive measurements**, not newly trained systems. Frozen predictions and summaries are in `results/`; `build_assets.py` creates the corresponding tables and figures. No values are illustrative. Earlier R7/R8/R9/R12/N1/N2 plans remain open where they require controlled training, other datasets, independent contamination checks or human judgments.

## Completed scope

| Script | Evaluation | Scope |
|---|---|---|
| `run_bitext.py` | Original FLORES-200 devtest | 13 varieties, 1,012 rows each; 156 directed pairs × 2 encoders = 312 conditions |
| `run_retrieval.py` | Belebele-derived source-passage recovery | 7 languages, 900 queries and 488 passages each; 77 lexical/dense/script/language conditions |
| `run_parsing.py` | Official UD 2.17 test files | Kazakh-KTB, Kyrgyz-KTMU, Turkish-IMST, Uyghur-UDT; gold sentence/word boundaries; Kazakh exposure-risk replay |
| `run_parsing_auto.py` | Same official UD test files | Gold sentences, automatic tokenization/MWT, official alignment-aware scoring |
| `run_ner.py` | KazNERD test | All 11,307 sentences, 129,824 words, 25 entity types; gold boundaries |
| `run_word_lengths.py`, `audit_spacing.py` | Original FLORES-200 devtest | 13 aligned varieties; sentence-weighted orthographic lengths and spacing diagnostics |
| `run_tumlu.py` | TUMLU-mini Kazakh | 797 valid test items of 799; 40 development items for answer-frequency baseline |
| `run_translation.py` | Original FLORES-200 devtest | Turkish→Kazakh and Kazakh→Turkish, 1,012 translations each |

The Belebele task recovers the supplied source passage; it is **not** multiple-choice accuracy or an exhaustively judged open-domain relevance collection. The release has unique `(link, question_number)` joins and one passage per link; no `split` column is available in these JSONL inputs. The Uzbek Cyrillic questions are synthetic mappings, not human-validated data. The fixed prefix-five table is accompanied by an exploratory prefix-three-through-eight test grid; no best test setting is selected as a tuned system.

## Inputs and provenance

- Original FLORES-200 archive: `https://dl.fbaipublicfiles.com/nllb/flores200_dataset.tar.gz`, SHA-256 `b8b0b76783024b85797e5cc75064eb83fc5288b41e9654dabc7be6ae944011f6`. This is not FLORES+. `common.py` verifies the archive and each manifest records extracted files. All rows are retained. The spacing audit finds 83 one-whitespace-unit South Azerbaijani rows and 128 with mean length above 30 letters; these distort orthographic-length averages and must not be interpreted as morphology.
- Belebele: `inputs/belebele-source-manifest.json` pins revision, seven file URLs/hashes and the CC BY-SA 4.0 license. `fetch_belebele.py` downloads and verifies these files. Requested Uyghur is unavailable in this snapshot and is excluded rather than fabricated. The original license is retained. Cite Bandarkar et al. (2024); see the book bibliography.
- Uzbek transformations: frozen derived queries and source hashes are under `inputs/`. `prepare_script_probe.py` can regenerate them with a matching TurkicNLP checkout; the recorded Git HEAD alone is not sufficient if source files differ, so compare the file hashes as well. Only queries are transformed; documents remain Latin. These derived Belebele texts retain CC BY-SA 4.0 attribution/terms.
- UD: use `python tables/tbl-ud217-inventory/fetch.py /path/to/ud217-official` from the book root. Its pinned download manifest supplies the official release files; never substitute locally augmented/silver files. The run manifests record exact test hashes. Original dataset licenses remain applicable to the tokens retained in predicted CoNLL-U files. UD Turkish-IMST is CC BY-NC-SA 4.0, which the book's CC BY-SA 4.0 licence cannot carry, so the two Turkish prediction files are distributed without IMST text: forms, predicted lemmas and `# text` comments are removed by `imst_text.py redact`, while sentence IDs, character offsets and all predicted tags, features, heads and relations are kept. Before validation, run `python experiments/empirical-2026-10/imst_text.py restore --gold UD_ROOT/UD_Turkish-IMST/tr_imst-ud-test.conllu`; it checks the official test file's SHA-256 and writes `*.restored.conllu` (git-ignored). The restored files reproduce every Turkish score in `parsing_summary.csv` and `parsing_auto_summary.csv` except the lemma-based Lemmas and BLEX rows, which come from the original run.
- KazNERD: `https://github.com/IS2AI/KazNERD`, revision `bd4333d0f5952b9fafb2ef2ac2fefa0ad3c0333f`; use `IOB2_test.txt`, SHA-256 `359a1f61f6a21280c6c47b4fde9a5adcd07411d62015aa6e32d940c51f163b7a`. Only predicted tags, not source sentence text, are saved in the NER JSONL.
- TUMLU-mini: use the exact Kazakh dev/test parquet URLs and hashes already recorded in `experiments/remaining_revision/source-manifest.json`. The runner verifies them. Test indices 362 and 390 have empty choices and are recorded as exclusions, not silently scored.

Model snapshots are required locally and are **not redistributed**. The recorded revisions are:

| Hugging Face repository | Revision |
|---|---|
| sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 | `e8f8c211226b894fcb81acc59f3b34ba3efd5f42` |
| sentence-transformers/paraphrase-xlm-r-multilingual-v1 | `c2e19453aae46f98a865abfdf173f35f2e119f5a` |
| Qwen/Qwen2.5-1.5B-Instruct | `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` |
| facebook/nllb-200-distilled-600M | `f8d333a098d19b4fd9a8b18f94170487ad3f821d` |

Acquire these snapshots through the normal Hugging Face download mechanism subject to their individual terms; pass the hub cache root to `--model-cache`. For Stanza use the checkpoint packages and SHA-256 hashes in `parsing_manifest.json`, `parsing_auto_manifest.json` and `ner_manifest.json`, together with matching `resources.json`. `validate_results.py` checks their declared resource MD5s. These are cached benchmark models, not an independently audited training recipe.

## Reproduce

Commands run from the book root. Replace uppercase paths below with local locations. The suite used Python 3.13, PyTorch 2.10.0 and Transformers 5.3.0 for encoder/LLM/MT inference; Stanza 1.11.0 with Python 3.10/PyTorch 2.10.0 for parsing and NER. Encoder and MT inference used Apple MPS; parsing/NER used CPU. The manifests record actual precision and dependencies. Python needs numpy, pyarrow, transformers, torch, stanza, sentencepiece, sacrebleu 2.5.1 and matplotlib for the respective scripts. Separate environments are acceptable; preserve versions for comparable inference. GPU kernels/precision may cause small numerical differences on another platform.

```sh
python experiments/empirical-2026-10/fetch_belebele.py --out DATA
python experiments/empirical-2026-10/run_word_lengths.py --archive FLORES_ARCHIVE
python experiments/empirical-2026-10/audit_spacing.py --archive FLORES_ARCHIVE
python experiments/empirical-2026-10/run_bitext.py --archive FLORES_ARCHIVE --model-cache HF_HUB_CACHE --vector-cache VECTORS --device mps
python experiments/empirical-2026-10/run_retrieval.py --data DATA --model-cache HF_HUB_CACHE --vector-cache VECTORS --device mps
python experiments/empirical-2026-10/run_parsing.py --ud-root UD_ROOT --model-root STANZA_ROOT
python experiments/empirical-2026-10/run_parsing_auto.py --ud-root UD_ROOT --model-root STANZA_ROOT
python experiments/empirical-2026-10/audit_stanza_splits.py --ud-root UD_ROOT --model-root STANZA_ROOT
python experiments/empirical-2026-10/run_ner.py --test KAZNERD_TEST --model-root STANZA_ROOT
python experiments/empirical-2026-10/run_tumlu.py --data KAZAKH_PARQUET_DIRECTORY --model-cache HF_HUB_CACHE --device mps
python experiments/empirical-2026-10/run_translation.py --archive FLORES_ARCHIVE --model-cache HF_HUB_CACHE --device mps
python experiments/empirical-2026-10/imst_text.py restore --gold UD_ROOT/UD_Turkish-IMST/tr_imst-ud-test.conllu
python experiments/empirical-2026-10/validate_results.py --ud-scorer STANZA_1_11_SCORER_PY --archive FLORES_ARCHIVE --ner-gold KAZNERD_TEST --ud-root UD_ROOT --model-root STANZA_ROOT
python experiments/empirical-2026-10/build_assets.py
python experiments/empirical-2026-10/write_manifest.py
```

For validation across separate environments, `STANZA_1_11_SCORER_PY` is the path to `stanza/utils/conll18_ud_eval.py` in the Stanza 1.11.0 environment. The validator checks its SHA-256 against the recorded inference scorer before loading it. Omit this argument only when that module is available in the validation environment.

Use `--device cpu` for the Transformers runners where MPS is unavailable; inference will be slower. `run_parsing_auto.py --resume` reuses completed language predictions after hash verification. To regenerate synthetic questions instead of using the frozen derived file:

```sh
python experiments/empirical-2026-10/prepare_script_probe.py --data DATA --toolkit TURKICNLP_CHECKOUT
```

## Interpretation and validation

Both paraphrase models use their configured 128-token limit, attention-mask mean pooling and L2 normalization. Truncation counts are retained. Bitext exact-duplicate targets are additional positives; top ties within 1e-6 receive fractional credit. Passage retrieval uses expected rank metrics over tied gold scores, avoiding arbitrary first-row wins on all-zero BM25 queries. It has one supplied relevant passage per query.

Parsing supplies predicted POS/features even with gold word boundaries. Automatic tokenization retains gold sentence boundaries and is therefore not a raw-document segmentation test. `# text =` metadata is parsed with optional whitespace after `=` (ten KTMU rows omit it). Official UD alignment scoring includes punctuation and coarse dependency relations. No gold labels enter the model. NER is strict span-and-type scoring, independently checked with Stanza's decoder.

TUMLU uses the checkpoint chat template and next-token A/B/C/D scoring, no gold answer/CoT in the prompt, no input truncation. Qwen obtains 226/797 (28.36%), below the development-selected D baseline's 304/797 (38.14%). Uniform 25% is an analytic expectation. This one protocol is not equivalent to full-answer likelihood or free generation, and there is no contamination audit.

MT uses float32, explicit source/target language IDs, batch eight, greedy generation and a 256-token output ceiling. BLEU uses 13a; chrF uses character order six/beta two, chrF++ word order two. Exact signatures and EOS/empty-output audits accompany the results. These are corpus metrics on a fixed benchmark, not a claim of human-rated adequacy or a reproduction of published beam-search scores.

`validation.json` records metric invariants, full denominators, saved-prediction rescoring and checkpoint-integrity checks. Human language/morphology/meaning checks, independent contamination assessment, matched training, learning curves, CTS retrieval, full translation matrices, speech and downstream adaptation remain open. Test-set prefix exploration must not be reused as development tuning without a new held-out evaluation.

## Kazakh parsing exposure correction (18 October 2026)

Stanza 1.11.0's standard preparation swaps a no-dev treebank's train/test inputs when the training file has at most 1,000 words and the test file has more than 5,000. Official Kazakh-KTB triggers this rule; checkpoint configuration names the prepared train/dev files. Its 95.57% gold-word and 95.34% automatic-tokenization LAS values are retained only as **replay/exposure-risk diagnostics, not held-out accuracy**. Historical checkpoint sentence membership was not reconstructed. The three other evaluated treebanks do not trigger this rule. `audit_stanza_splits.py` and `results/stanza_split_audit.json` record the source hash, thresholds and treebank counts; score CSVs carry the scope warning. This does not complete controlled or independently held-out Kazakh parsing evaluation.
