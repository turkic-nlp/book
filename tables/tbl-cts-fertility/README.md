# CTS fertility provenance

`source.json` freezes full-precision results from the paper checkout and records their SHA-256. `experiment-method.py` is a reference copy of the experiment, not a self-contained runnable pipeline. Regenerate the book table with `python generate.py` (standard library only).

Words are Python regex `[^\W_]+` matches (Unicode alphanumerics excluding underscore). Each word is encoded separately without special tokens. Each language’s 20 sentences are concatenated; corpus fertility is total tokens divided by extracted words. Native and converted word counts can differ. The group mean gives each language equal weight, using unrounded results.

The experiment loads Qwen/Qwen3.5-35B-A3B-FP8, meta-llama/Meta-Llama-3-8B and allenai/Olmo-3-1025-7B tokenizer.json files and tiktoken o200k_base. The historical result does not record tokenizer commit hashes, package versions or the exact mapping-source hash at execution time. A byte-exact rerun cannot be claimed from these files alone. Recover the original snapshot manifest before a publication-grade rerun; a current toolkit-source snapshot is not retroactive provenance for the experiment.

Overlap uses sets of character trigrams of the space-joined, ordinary-Python-lowercased regex words of each language’s concatenated sample. It includes cross-word trigrams. Word overlap uses Jaccard on the corresponding lowercased word sets. Pair summaries are macro-averages, not averages over aligned sentence pairs.
