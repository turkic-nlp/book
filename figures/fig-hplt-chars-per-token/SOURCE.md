# HPLT characters per token

Input: `hplt_v3_turkic.csv`, the book's sourced HPLT v3 snapshot.
The generator selects present primary language subsets and the English/Russian references (13 rows), divides corpus character totals by Gemma 3 token totals, and checks against the rounded source ratio.

Manifest: https://data.hplt-project.org/three/sorted/manifest.json
Accessed 2026-10-12; SHA256 eb82cccdc093235f5ffd89fc775963ce9ca6b61857366b91b4b4096991afdb4c.

These are different language corpora, not parallel texts. Characters/token is not tokens/word, and this plot cannot isolate script, morphology, or tokenizer training as a cause. No estimated word counts are used.
