"""Regenerate values and macro-means from frozen full-precision experiment data."""
from pathlib import Path
import csv,json,statistics,sys
HERE=Path(__file__).parent
sys.path.insert(0,str(HERE.parents[1]/'scripts'))
from book_tables import export,table
source=json.loads((HERE/'source.json').read_text())
raw=source['rows']; lookup={(r['lang'],r['tokenizer'],r['condition']):r for r in raw}
assert len(lookup)==len(raw)
names={r['iso']:r['language'] for r in csv.DictReader((HERE/'data.csv').open())}
T=[('qwen','Qwen3.5'),('llama','LLaMA 3'),('olmo','OLMo 3'),('openai','o200k_base')]
langs=list(names)
rows=[]
for lang in langs:
    r={'language':names[lang],'iso':lang,'native_script':lookup[lang,'qwen','native']['native_script']}
    for t,_ in T:
        for c in ['native','cts']:
            v=lookup[lang,t,c];assert int(v['word_count'])>0 and float(v['fertility'])>=1
            r[t+'_'+c]=f"{float(v['fertility']):.2f}"
    r['source']=source['source']+'; SHA256 '+source['source_sha256'];rows.append(r)
export(HERE,rows)
selected=[r for r in rows if r['native_script']!='Latn'];assert len(selected)==13
body=[[r['language'],r['native_script']]+[r[t+'_native']+' → '+r[t+'_cts'] for t,_ in T] for r in selected]
means=[]
for t,_ in T:
    a,b=[statistics.mean(float(lookup[r['iso'],t,c]['fertility']) for r in selected) for c in ['native','cts']]
    means.append(f'**{a:.2f} → {b:.2f}**')
body.append(['**Average (13 languages)**','']+means)
table(HERE,['Language','Script']+[n+' (native → CTS)' for _,n in T],body,'Fertility on the parallel challenge sample of @hakimov2025turkicnlp. Group means use full-precision values, not the rounded displayed cells. The OpenAI column is the measured `o200k_base` encoding, not an inference-time model measurement. {#tbl-cts-fertility}')
