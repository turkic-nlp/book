# Provenance: HPLT v3.0 Turkic statistics

- **Source:** `https://data.hplt-project.org/three/sorted/manifest.json` (HPLT Monolingual Datasets 3.0, sorted release; https://hplt-project.org/datasets/v3.0)
- **Manifest:** JSON Lines, 198 language–script subsets. SHA-256 `eb82cccdc093235f5ffd89fc775963ce9ca6b61857366b91b4b4096991afdb4c`; HTTP Last-Modified 2025-10-21T07:43:24Z; accessed 2026-10-12.
- **How the numbers were extracted.** On 2026-10-12, the manifest was read in a browser. data.hplt-project.org is not reachable from the sandboxed shells, so a browser was used instead of `fetch_hplt_v3.py`. The extraction applies the same logic as that script:
  1. The manifest fields `files`, `bytes`, `documents`, `segments`, `tokens`, `characters`, `t/d` and `c/t` are copied unchanged.
  2. The quality bin of each shard is the number before the underscore in the shard file name (`<code>/<bin>_<n>.jsonl.zst`; bins 5–10, Web Docs Scorer). Each shard's size comes from the HTTP `Content-Length` of a HEAD request. Per-bin sums equal the manifest's `bytes` exactly (checked).
  3. `sample_words_per_char` is computed on the official `samples` file for each language: 12 documents, 2 per bin. Words are `[\p{L}\p{M}]+` sequences and characters are Unicode code points.
- **Caveats.**
  - `gemma3_tokens` are Gemma 3 tokeniser tokens, **not words**.
  - `est_words` = `characters × sample_words_per_char`. It is a **rough estimate** from 12 sample documents. Replace it with counts on a real shard sample (N1-0, step 3) before using it in the book.
  - `bytes_compressed` is the zstd-compressed download size.
  - Sizes are **labelled** sizes: the documents were assigned to the language by OpenLID 2.0 and have not been audited (see N1-1).
  - `present = 0` means no subset with that code exists in the v3.0 manifest. The codes checked are in `hplt_code`.
- `fetch_hplt_v3.py` uses the Python pattern `[^\W\d_]+` for words. It can differ slightly from the browser's `[\p{L}\p{M}]+` on combining marks. Both counts are rough estimates.
