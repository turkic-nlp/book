"""Rebuild data.csv and the chapter include from the frozen primary-source snapshot."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"scripts"))
from book_tables import *
HERE=Path(__file__).resolve().parent

d=json.loads((HERE/"source.json").read_text());r=d["challenge_turkic"];n=d["sentences_per_language"]
assert r["n"]==n*len(r["per_lang"])
names={"gag":"Gagauz","crh":"Crimean Tatar","kaa":"Karakalpak (2016 Latin)","nog":"Nogai","alt":"Altai","tyv":"Tuvan","kjh":"Khakas","kum":"Kumyk","tur":"Turkish","kir":"Kyrgyz","kaz":"Kazakh","krc":"Karachay-Balkar"}
records=[];body=[]
for iso in ["gag","crh","kaa","nog","alt","tyv","kjh","kum"]:
    cs=sorted([c for c in r["top_confusions"] if c["gold"].split("_")[0]==iso],key=lambda c:-c["count"])
    c=cs[0];accuracy=r["per_lang"][iso];correct=round(accuracy*n)
    assert abs(correct/n-accuracy)<1e-10 and c["count"]<=n-correct
    pred=c["pred"].split("_")[0]
    records.append(dict(language=names[iso],iso=iso,sentences=n,correct=correct,accuracy=accuracy,top_wrong_label=c["pred"],wrong_count=c["count"],source="hakimov2025turkicnlp; langid.json challenge.turkic; source.json"))
    body.append([names[iso],f"{names[pred]} ({c['count']}/{n})",f"{accuracy*100:.0f}%"])
export(HERE,records)
table(HERE,["Language","Most frequent wrong label (sentences)","Challenge-set accuracy"],body,
      "Language identification for eight smaller Turkic languages: GlotLID restricted to Turkic labels, 20 parallel challenge sentences per language [@hakimov2025turkicnlp]. Counts refer to the most frequent recorded wrong label, not all errors. {#tbl-lid-confusions}")
