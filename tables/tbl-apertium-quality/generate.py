"""Rebuild data.csv and the chapter include from the frozen primary-source snapshot."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
from book_tables import *
HERE=Path(__file__).resolve().parent

r=latex_rows(HERE/"source.tex"); assert len(r)==21 and all(len(x)==9 for x in r)
source="hakimov2025turkicnlp; source.tex, tab:morph-eval (snapshot 2026-10-13)"
keys=["language","iso","script","apertium_det","apertium_ana","apertium_feat","neural_det","neural_ana","neural_feat"]
export(HERE,[dict(zip(keys,x))|{"source":source} for x in r])
body=[]
for x in r:
    name=x[0]
    if name=="Average": name="**Average**"
    body.append([name]+paired([x[3],x[5],x[6],x[8]],2))
table(HERE,["Language","Apertium Det%","Apertium Feat%","Neural Det%","Neural Feat%"],body,
      "Small diagnostic probe results (Det% and non-empty-feature rate) for Apertium and multilingual neural morphological analysis on the 20-sentence parallel challenge set [@hakimov2025turkicnlp]. Not a measure of analysis accuracy. Det%: sentences in which the target UD feature is detected; Feat%: content words receiving at least one feature (coverage, not feature accuracy). ^†^Zero-shot for the neural model. Bold: higher value per metric. Published rounded averages are preserved. {#tbl-apertium-quality}")
