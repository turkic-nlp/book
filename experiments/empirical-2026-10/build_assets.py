"""Generate publication tables and figures only from frozen measured outputs."""
from pathlib import Path
import csv,json,shutil,sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];RES=Path(__file__).parent/'results'
sys.path.insert(0,str(ROOT/'experiments/common'))
from bookgen import md_table
ONLY=sys.argv[1] if len(sys.argv)>1 else None
NAMES={'eng_Latn':'English','rus_Cyrl':'Russian','tur_Latn':'Turkish','azj_Latn':'N. Azerbaijani','azb_Arab':'S. Azerbaijani','tuk_Latn':'Turkmen','kaz_Cyrl':'Kazakh','kir_Cyrl':'Kyrgyz','tat_Cyrl':'Tatar','bak_Cyrl':'Bashkir','crh_Latn':'Crimean Tatar','uzn_Latn':'N. Uzbek','uig_Arab':'Uyghur'}
def read(name):return list(csv.DictReader((RES/name).open()))
def table(ident,source,heads,body,caption):
 if ONLY and ONLY!=ident:return
 d=ROOT/'tables'/ident;d.mkdir(exist_ok=True);shutil.copy2(RES/source,d/'data.csv')
 (d/'output.md').write_text(md_table(heads,['l']+['r']*(len(heads)-1),body,caption,ident))
 (d/'generate.py').write_text('from pathlib import Path\nimport runpy,sys\nsys.argv=[sys.argv[0],Path(__file__).resolve().parent.name]\nrunpy.run_path(str(Path(__file__).resolve().parents[2]/"experiments/empirical-2026-10/build_assets.py"),run_name="__main__")\n')
 (d/'README.md').write_text(f'# {ident}\n\nGenerated from `experiments/empirical-2026-10/results/{source}`. Run `python experiments/empirical-2026-10/build_assets.py` from the book root. See that experiment folder’s README for protocol, input hashes and limitations. Values in `data.csv` are the frozen source measurements, before display rounding.\n')
def figure(ident,source,fig):
 if ONLY and ONLY!=ident:plt.close(fig);return
 d=ROOT/'figures'/ident;d.mkdir(exist_ok=True);shutil.copy2(RES/source,d/'data.csv')
 for ext in ['png','pdf','svg']:fig.savefig(d/f'output.{ext}',dpi=210,bbox_inches='tight')
 plt.close(fig)
 (d/'plot.py').write_text('from pathlib import Path\nimport runpy,sys\nsys.argv=[sys.argv[0],Path(__file__).resolve().parent.name]\nrunpy.run_path(str(Path(__file__).resolve().parents[2]/"experiments/empirical-2026-10/build_assets.py"),run_name="__main__")\n')
 (d/'README.md').write_text(f'# {ident}\n\nMeasured data: `experiments/empirical-2026-10/results/{source}`. Regenerate with `python experiments/empirical-2026-10/build_assets.py`. No illustrative values are substituted. Protocol and scope are in the experiment README.\n')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42,'svg.fonttype':'none'})
# Parallel orthographic length, separate from the earlier TueCL plot.
w=read('word_length_summary.csv')  # tbl-flores-word-length is no longer in the book; only the figure is built
w=sorted(w,key=lambda x:float(x['paired_difference_vs_english']));v=np.array([float(x['paired_difference_vs_english']) for x in w]);lo=np.array([float(x['bootstrap_low']) for x in w]);hi=np.array([float(x['bootstrap_high']) for x in w]);fig,ax=plt.subplots(figsize=(6.8,4.6));ax.barh(range(len(w)),v,color=['#64748b' if x['lang'] in ['eng_Latn','rus_Cyrl'] else '#137d92' for x in w]);ax.errorbar(v,range(len(w)),xerr=[v-lo,hi-v],fmt='none',ecolor='#172a3a',capsize=2,lw=.8);ax.set_yticks(range(len(w)),[NAMES[x['lang']] for x in w]);ax.axvline(0,color='#444',lw=.8);ax.set_xlabel('Difference in mean letters per unit versus English');ax.grid(axis='x',alpha=.18);ax.set_axisbelow(True);fig.tight_layout();figure('fig-flores-word-length','word_length_summary.csv',fig)
# Native sentence retrieval.
b=read('bitext_summary.csv');langs=list(NAMES);body=[]
for lang in langs:
 values=[]
 for model in ['minilm','xlmr']:
  rr=[float(x['top1_accuracy']) for x in b if x['model']==model and x['src']==lang];assert len(rr)==12;values.append(f'{np.mean(rr)*100:.1f}')
 body.append([NAMES[lang],*values])
table('tbl-flores-native-probe','bitext_summary.csv',['Query variety','MiniLM (%)','XLM-R (%)'],body,'Native-script bitext top-1 accuracy, averaged equally over the other 12 target varieties. Each direction uses all 1,012 original FLORES-200 devtest rows as queries and candidates. Models are the pinned multilingual paraphrase MiniLM and XLM-R encoders, with their 128-token limit and recorded truncation. Source: `run_bitext.py`; @costa2022nllb.')
m=np.full((len(langs),len(langs)),np.nan)
for x in b:
 if x['model']=='xlmr':m[langs.index(x['src']),langs.index(x['tgt'])]=100*float(x['top1_accuracy'])
fig,ax=plt.subplots(figsize=(7.3,6.4));im=ax.imshow(np.ma.masked_invalid(m),vmin=0,vmax=100,cmap='YlGnBu');labels=[s.split('_')[0] for s in langs];ax.set_xticks(range(len(langs)),labels,rotation=45,ha='right');ax.set_yticks(range(len(langs)),labels);ax.set_xlabel('Target candidate language');ax.set_ylabel('Query language')
for i in range(len(langs)):
 for j in range(len(langs)):
  if i!=j:ax.text(j,i,f'{m[i,j]:.0f}',ha='center',va='center',fontsize=7.2,color='white' if m[i,j]>55 else '#102a43')
fig.colorbar(im,ax=ax,shrink=.8,label='Top-1 accuracy (%)');fig.tight_layout();figure('fig-flores-native-probe','bitext_summary.csv',fig)
# Passage retrieval and script probe.
r=read('retrieval_summary.csv');codes=sorted(set(x['src'] for x in r));body=[]
for code in codes:
 vals=[]
 for run in ['bm25-surface','bm25-prefix5','minilm','xlmr']:
  x=next(x for x in r if x['src']==x['tgt']==code and x['condition']=='native' and x['run']==run);vals.append(f"{float(x['ndcg10']):.3f}")
 body.append([NAMES[code],*vals])
table('tbl-belebele-passage-probe','retrieval_summary.csv',['Language','Surface','Prefix 5','MiniLM','XLM-R'],body,'Measured nDCG@10 for source-passage retrieval derived from Belebele: 900 questions and 488 candidate passages per language. This is not Belebele multiple-choice accuracy. BM25 uses fixed k1=1.2 and b=0.75; dense encoders use their 128-token limit. Gold-score ties receive expected rank credit. Source: `run_retrieval.py`; @bandarkar2024belebele.')
body=[]
for condition,label in [('native','Original Latin'),('synthetic-Cyrillic-query','Synthetic Cyrillic'),('roundtrip-Latin-query','Round-trip Latin')]:
 vals=[]
 for run in ['bm25-surface','minilm','xlmr']:
  x=next(x for x in r if x['src']==x['tgt']=='uzn_Latn' and x['condition']==condition and x['run']==run);vals.append(f"{float(x['ndcg10']):.3f}")
 body.append([label,*vals])
table('tbl-uzbek-script-probe','retrieval_summary.csv',['Query condition','BM25','MiniLM','XLM-R'],body,'Measured nDCG@10 on the same 900 Uzbek questions and 488 Latin passages. Cyrillic queries are generated by the pinned toolkit mapping, then optionally converted back to Latin. No native-speaker validation is claimed. Source: `run_retrieval.py` and `prepare_script_probe.py`; @bandarkar2024belebele.')
body=[]
for src,tgt in [('kaz_Cyrl','rus_Cyrl'),('rus_Cyrl','kaz_Cyrl'),('tur_Latn','eng_Latn'),('uzn_Latn','rus_Cyrl')]:
 vals=[]
 for run in ['minilm','xlmr']:
  x=next(x for x in r if x['src']==src and x['tgt']==tgt and x['condition']=='cross-language' and x['run']==run);vals.append(f"{float(x['ndcg10']):.3f}")
 body.append([NAMES[src]+' → '+NAMES[tgt],*vals])
table('tbl-belebele-crosslanguage-probe','retrieval_summary.csv',['Question → passages','MiniLM','XLM-R'],body,'Cross-language passage-recovery nDCG@10: 900 questions and 488 aligned target-language passages per direction. Source: `run_retrieval.py`; @bandarkar2024belebele.')
fig,ax=plt.subplots(figsize=(6.8,4.2))
for code in codes:
 xs=list(range(3,9));ys=[float(next(x for x in r if x['src']==x['tgt']==code and x['run']==f'bm25-prefix{k}' and x['condition']=='native')['ndcg10']) for k in xs];ax.plot(xs,ys,marker='o',ms=3,label=NAMES[code],linestyle='--' if code in ['eng_Latn','rus_Cyrl'] else '-')
ax.set_xlabel('Prefix length (Unicode code points after tokenization)');ax.set_ylabel('nDCG@10');ax.set_xticks(range(3,9));ax.grid(alpha=.2);ax.legend(fontsize=8,ncol=2);fig.tight_layout();figure('fig-belebele-prefix-probe','retrieval_summary.csv',fig)
# Official UD scorer results.
p=read('parsing_summary.csv');body=[]
for lang,name in [('ky','Kyrgyz-KTMU'),('tr','Turkish-IMST'),('ug','Uyghur-UDT'),('kk','Kazakh-KTB† (replay, not held-out)')]:
 rr=[x for x in p if x['language']==lang];vals=[f"{float(next(x for x in rr if x['metric']==metric)['f1'])*100:.2f}" for metric in ['UPOS','UFeats','UAS','LAS']];body.append([name,rr[0]['syntactic_words'],*vals])
table('tbl-ud217-pretrained-probe','parsing_summary.csv',['Test treebank','Words','UPOS','UFeats','UAS','LAS'],body,'Measured pretrained Stanza scores (%) on official UD 2.17 test files, using gold sentence and syntactic-word boundaries and predicted tags/features. The UD scorer includes punctuation in UAS/LAS; all denominators are retained. † Kazakh is a replay diagnostic with split-exposure risk, not held-out accuracy. These are not raw-text or newly trained results. Source: `run_parsing.py`.')
if (RES/'parsing_auto_summary.csv').exists():
 auto=read('parsing_auto_summary.csv');body=[]
 for lang,name in [('ky','Kyrgyz-KTMU'),('tr','Turkish-IMST'),('ug','Uyghur-UDT'),('kk','Kazakh-KTB† (replay, not held-out)')]:
  rr=[x for x in auto if x['language']==lang];g=next(x for x in p if x['language']==lang and x['metric']=='LAS');vals=[f"{100*float(next(x for x in rr if x['metric']==metric)['f1']):.2f}" for metric in ['Words','UAS','LAS']];body.append([name,f"{100*float(g['f1']):.2f}",*vals])
 table('tbl-ud217-tokenization-probe','parsing_auto_summary.csv',['Test treebank','Gold-word LAS','Auto word F1','Auto UAS','Auto LAS'],body,'Measured Stanza scores (%) on the same official UD 2.17 tests. Both conditions retain gold sentence boundaries; the automatic condition predicts tokenization/MWT and uses the official alignment-aware scorer. † Kazakh has split-exposure risk and is not a held-out score. Gold-word LAS is repeated from the preceding table. Source: run_parsing.py and run_parsing_auto.py.')
n=read('ner_summary.csv');overall=n[0];table('tbl-kaznerd-pretrained-probe','ner_summary.csv',['Test sentences','Gold entities','Predicted','Correct','P (%)','R (%)','F1 (%)'],[['11,307',overall['gold_entities'],overall['predicted_entities'],overall['correct_entities'],*[f"{float(overall[k])*100:.2f}" for k in ['precision','recall','f1']]]],'Measured cached Stanza KazNERD checkpoint on the complete pinned test split, with gold word/sentence boundaries and exact entity spans and types. No fine-tuning was performed. Source: `run_ner.py`; @yeshpanov2022kaznerd.')
n=sorted(n[1:],key=lambda x:float(x['f1']));fig,ax=plt.subplots(figsize=(6.8,7.4));ax.barh(range(len(n)),[100*float(x['f1']) for x in n],color='#137d92');ax.set_yticks(range(len(n)),[x['entity_type']+' (n='+x['gold_entities']+')' for x in n],fontsize=8);ax.set_xlim(0,100);ax.set_xlabel('Exact span-and-type F1 (%)');ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True);fig.tight_layout();figure('fig-kaznerd-type-probe','ner_summary.csv',fig)
t=json.loads((RES/'tumlu_summary.json').read_text());base=t['dev_majority_baseline']['test'];rows=[{'system':'Qwen2.5-1.5B-Instruct','correct':t['overall']['correct'],'n':797,'accuracy':t['overall']['accuracy'],'source':'experiments/empirical-2026-10/run_tumlu.py; pinned TUMLU-mini Kazakh valid subset'}, {'system':'Development-majority letter D','correct':base['correct'],'n':797,'accuracy':base['accuracy'],'source':'experiments/empirical-2026-10/run_tumlu.py; letter selected from 40 dev questions'}, {'system':'Uniform choice (expectation)','correct':'','n':797,'accuracy':.25,'source':'Analytic expectation: four choices per valid question'}]
with (RES/'tumlu_table.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
table('tbl-tumlu-pretrained-probe','tumlu_table.csv',['System','Correct / 797','Accuracy (%)'],[[x['system'],str(x['correct']) if x['correct']!='' else 'Expected',f"{x['accuracy']*100:.2f}"] for x in rows],'Measured zero-shot constrained-letter Qwen score on 797 valid TUMLU-mini Kazakh test items; two malformed items of 799 are excluded and recorded. The letter-D baseline is selected from the 40 development items, not the test answers. Uniform accuracy is an expectation, not a model run. Source: `run_tumlu.py`; @isbarov2025tumlu.')
if (RES/'translation_summary.csv').exists():
 t=read('translation_summary.csv');table('tbl-nllb-pretrained-probe','translation_summary.csv',['Direction','Sentences','BLEU-13a','chrF','chrF++'],[[NAMES[x['src']]+' → '+NAMES[x['tgt']],x['sentences'],*[f"{float(x[k]):.2f}" for k in ['bleu','chrf','chrfpp']]] for x in t],'Measured NLLB-200 distilled 600M greedy translation on original FLORES-200 devtest. No fine-tuning or input truncation; explicit target language token, one beam and a 256-token generation ceiling. Exact SacreBLEU signatures and output audits are retained. Source: `run_translation.py`; @costa2022nllb.')
print('Empirical assets regenerated from frozen results')
