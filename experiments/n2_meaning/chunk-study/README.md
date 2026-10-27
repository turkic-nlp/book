# N2-4: measured token-budget capacity

Completed 16 October 2026. This replaces the chapter's isolated-word fertility estimate with an actual packing measurement. It is not a model benchmark or a retrieval-quality evaluation.

## Inputs

- Original **FLORES-200 devtest** from Meta's official public archive, linked by its [release README](https://github.com/facebookresearch/flores/blob/main/flores200/README.md). The archive README establishes that language files have aligned rows. The study uses 1,012 rows per variety: English; Turkish; North/South Azerbaijani; Turkmen; Kazakh; Kyrgyz; Tatar; Bashkir; Crimean Tatar; Northern Uzbek; Uyghur. Licence: CC BY-SA 4.0. Cite the NLLB paper (`costa2022nllb` in the book).
- The current account could not access the newer gated FLORES+ release. We used the separately published original FLORES-200 archive and label it accordingly; no FLORES+ revision is claimed.
- Qwen/Qwen3.5-35B-A3B-FP8, meta-llama/Meta-Llama-3-8B and allenai/Olmo-3-1025-7B **tokenizer.json only**, at the commits in `../exp_chunk_content.py`; plus tiktoken `o200k_base`. These are tokenizer comparisons, not performance claims about those models. No weights or inference are used.
- `../results/chunk_content_manifest.json` records archive/member hashes, tokenizer revisions/file hashes, the o200k merge-rank hash, library versions and output hashes. Raw benchmark text is kept in the input cache, not copied into the book repository.

## Protocol

Use published sentence order; strip leading/trailing whitespace per row (500 rows across the 12 files needed trimming), preserve internal text and join adjacent rows with a single ASCII space. Re-encode each proposed entire chunk; never approximate joined encoding by summing independently tokenized sentences. Disable automatic padding, truncation and special-token insertion. No chat template or prompt is included.

Greedily append the next whole sentence if the joined text uses at most 512 tokens; otherwise close the chunk and start the next. Fail if any individual sentence exceeds the budget, rather than silently dropping or truncating it. None did here (maximum: 388 tokens). Save every chunk, with inclusive one-based source-row ranges. The final tail is flagged and excluded from capacity means even if it happens to be full; it remains in the audit. “Words” means Python `\S+` whitespace-delimited units. “Sentences” means source rows, not an independently inferred sentence segmentation.

The 48 language/tokenizer combinations produce 6,458 chunks including 48 tails. Each combination accounts for exactly 1,012 rows. Closed-chunk mean fill ranges from 84.4% to 97.4%. The frozen summary has 48 rows. It reports tail counts, maximum sentence/chunk token counts and precise means, so differences in unused capacity are visible.

FLORES samples sentences from several articles. Packing here may cross those article boundaries: it is a capacity probe on a published sentence stream, not recommended document chunking. Corpus/order/translation choices affect the result; whitespace units are not linguistic morphemes or semantic information. Language and script are confounded. The final tail excluded from the means contains a different number of rows in different conditions. Retrieval accuracy, answer quality, prompts, embeddings and model context limits were not evaluated.

## Reproduce

Use Python 3.13 with a separate environment and install `requirements.txt`. Input fetching additionally uses the declared Hugging Face client; the Llama tokenizer may require existing authorisation. Never substitute a different tokenizer silently.

```sh
python experiments/n2_meaning/chunk-study/fetch_inputs.py --cache-dir /path/to/chunk-inputs
python experiments/n2_meaning/exp_chunk_content.py \
  --archive /path/to/chunk-inputs/flores200_dataset.tar.gz \
  --tokenizer-root /path/to/chunk-inputs/hub
python -m unittest discover -s experiments/n2_meaning -p test_chunk_content.py
python experiments/n2_meaning/chunk-study/validate_results.py \
  --archive /path/to/chunk-inputs/flores200_dataset.tar.gz \
  --tokenizer-root /path/to/chunk-inputs/hub
python tables/tbl-chunk-content/generate.py
python figures/fig-chunk-content/plot.py
```

On the first measurement run, tiktoken obtains its public o200k vocabulary unless already cached. Set `TIKTOKEN_CACHE_DIR` to a persistent input-cache directory for offline repeats. The original run used the user's existing HF tokenizer snapshots and a temporary o200k cache. Install Matplotlib separately to regenerate the figure; the CSV measurement has no plotting dependency.

## Outputs and validation

- `../results/chunk_content_measured.csv`: measured per-language/tokenizer summaries.
- `../results/chunk_content_chunks.csv`: every chunk, its row range, words, sentences, tokens and final-tail flag; no sentence text.
- `../results/chunk_content_manifest.json`: pinned inputs, exact protocol and runtime metadata.
- `../results/chunk_content_validation.json`: independent recount and aggregation checks.
- `tables/tbl-chunk-content/` and `figures/fig-chunk-content/`: generated table and figure, each with its copied source CSV.

Unit checks cover non-additive tokenization across joins, separator cost, an exact budget boundary, final-tail accounting, oversized sentences and invalid inputs. The independent validator reconstructs every saved row range, re-encodes it, checks that each closed chunk cannot accept its next sentence, and recomputes summaries. The old `chunk_content.csv` is historical estimate data; the current generator never falls back to it.

Document-level KazQAD chunking/retrieval evaluation and a newer FLORES+ replication remain open.
