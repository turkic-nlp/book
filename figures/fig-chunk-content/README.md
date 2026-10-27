# Measured 512-token capacity

Run `python plot.py` after experiment N2-4. The plot reads `experiments/n2_meaning/results/chunk_content_measured.csv`, copies it to `data.csv`, and writes `output.png`, `output.pdf` and `output.svg`. Requires Matplotlib.

All 12 language varieties and four tokenizers are shown; the two panels report means for whitespace-delimited words and aligned sentence rows. No interpolation, synthetic scores or causal script comparison is used. See `experiments/n2_meaning/chunk-study/README.md` for exact inputs, packing rules and limits.
