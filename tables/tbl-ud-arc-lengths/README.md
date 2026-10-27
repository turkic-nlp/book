# Official UD 2.17 test-arc diagnostics

Recompute from a clean official release:

```sh
python tables/tbl-ud-arc-lengths/generate.py /path/to/ud217-official
python figures/fig-ud-arc-lengths/plot.py
```

Without the source argument, the table generator redraws the frozen CSV only. The plot requires matplotlib. Distances use original integer-ID word positions, excluding root and PUNCT-dependent arcs, but retaining intervening punctuation positions. Quantiles use nearest rank. Each treebank is a separate corpus; no causal language comparison is implied. The CSV includes source URLs and hashes, exact arc counts and distance sums. `acl` subtype counts are not a validated participial-clause extraction.
