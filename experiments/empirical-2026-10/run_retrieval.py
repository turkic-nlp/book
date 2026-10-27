"""Source-passage retrieval derived from Belebele, NOT multiple-choice QA accuracy.
Fixed BM25 settings, an exploratory prefix grid, two cached encoders and an
explicit synthetic Uzbek-script probe. No test labels are used for fitting.
"""
from common import *
from collections import Counter
import argparse,re,unicodedata,gc,time

def tokenise(s,lang,k=None):
 s=unicodedata.normalize('NFC',s)
 if lang in ['tur_Latn','azj_Latn']:s=s.replace('I','ı').replace('İ','i')
 ts=re.findall(r'[^\W_]+',s.lower());return [t[:k] if k else t for t in ts]
def bm25(docs,queries,lang,k=None):
 dt=[Counter(tokenise(s,lang,k)) for s in docs];vocab=sorted(set().union(*(x.keys() for x in dt)));v={x:i for i,x in enumerate(vocab)};tf=np.zeros((len(docs),len(vocab)),dtype=np.float64)
 for i,c in enumerate(dt):
  for t,n in c.items():tf[i,v[t]]=n
 dl=tf.sum(1);assert dl.mean()>0;df=(tf>0).sum(0);idf=np.log1p((len(docs)-df+.5)/(df+.5));w=idf*tf*2.2/(tf+1.2*(.25+.75*dl[:,None]/dl.mean()));scores=[]
 for q in queries:
  terms=[v[t] for t in set(tokenise(q,lang,k)) if t in v];scores.append(w[:,terms].sum(1))
 return np.array(scores)
def metrics(scores,gold):
 assert scores.ndim==2 and len(scores)==len(gold) and np.isfinite(scores).all();out=[]
 for s,g in zip(scores,gold):
  equal=np.isclose(s,s[g],atol=1e-6,rtol=0);b=int(((s>s[g])&~equal).sum());e=int(equal.sum());assert e>0
  ranks=np.arange(b+1,min(b+e,10)+1);row={'rank_min':b+1,'rank_max':b+e,'top1':1/e if b==0 else 0,'mrr10':float((1/ranks).sum()/e),'ndcg10':float((1/np.log2(ranks+1)).sum()/e),'recall10':min(max(10-b,0),e)/e,'recall100':min(max(100-b,0),e)/e};out.append(row)
 return out

def collection(path):
 rows=[json.loads(x) for x in path.read_text().splitlines()];assert len(rows)==900;by={};qs={}
 for i,x in enumerate(rows):
  pid=x['link'];qid=(pid,int(x['question_number']));assert qid not in qs;qs[qid]=(x['question'],i)
  if pid in by:assert by[pid]==x['flores_passage'],'One link maps to conflicting passages'
  by[pid]=x['flores_passage']
 assert len(by)==488 and len(set(by.values()))==488
 ids=sorted(by);qids=sorted(qs);return {'ids':ids,'qids':qids,'docs':[by[x] for x in ids],'queries':[qs[x][0] for x in qids],'source_rows':[qs[x][1] for x in qids],'gold':[ids.index(x[0]) for x in qids]}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True);ap.add_argument('--model-cache',type=Path,required=True);ap.add_argument('--vector-cache',type=Path,required=True);ap.add_argument('--device',default='mps');a=ap.parse_args();out=Path(__file__).parent/'results';source=json.loads((a.data/'belebele-source-manifest.json').read_text());collections={x['code']:collection(a.data/(x['code']+'.jsonl')) for x in source['files']}
 for x in source['files']:assert sha(a.data/(x['code']+'.jsonl'))==x['sha256']
 base=next(iter(collections.values()))
 for c in collections.values():assert c['ids']==base['ids'] and c['qids']==base['qids']
 summary=[];details=[];manifest={'source':source,'protocol':'Derived source-passage retrieval. One known source passage per question, 488 candidates and 900 questions per language. No multiple-choice answers used. No tuning. No claim of complete semantic relevance judgments.','bm25':{'k1':1.2,'b':.75,'idf':'ln(1+(N-df+0.5)/(df+0.5))','query_tf':'each distinct query token once','tokens':'NFC, language-aware lowercase for Turkish/Azerbaijani, Unicode alphanumeric runs excluding underscore','prefix_grid':[3,4,5,6,7,8],'grid_scope':'exploratory test-set sensitivity; no best k selected'},'tie_policy':'Expected metric under uniformly random ordering of all gold-score ties, atol=1e-6; no row-order tie breaking','models':{},'truncation':{}}
 def record(name,src,tgt,s,g,condition='native'):
  rr=metrics(s,g);summary.append({'run':name,'src':src,'tgt':tgt,'condition':condition,'queries':len(g),'candidates':s.shape[1],**{m:float(np.mean([r[m] for r in rr])) for m in ['top1','mrr10','ndcg10','recall10','recall100']},'queries_with_gold_ties':sum(r['rank_max']>r['rank_min'] for r in rr),'source':'experiments/empirical-2026-10/run_retrieval.py; pinned Belebele-derived passage retrieval'})
  details.extend({'run':name,'src':src,'tgt':tgt,'condition':condition,'query_index':i,**r} for i,r in enumerate(rr));print(name,src,tgt,condition,summary[-1]['ndcg10'],flush=True)
 probe=json.loads((a.data/'uzbek-script-probe.json').read_text());assert len(probe)==900 and [x['row'] for x in probe]==list(range(900));original_rows=[json.loads(x) for x in (a.data/'uzn_Latn.jsonl').read_text().splitlines()];assert all(p['original']==x['question'] for p,x in zip(probe,original_rows));uz=collections['uzn_Latn'];cyrl=[probe[i]['cyrillic'] for i in uz['source_rows']];back=[probe[i]['roundtrip'] for i in uz['source_rows']]
 for code,c in collections.items():
  for k in [None,3,4,5,6,7,8]:record('bm25-surface' if k is None else f'bm25-prefix{k}',code,code,bm25(c['docs'],c['queries'],code,k),c['gold'])
 record('bm25-surface','uzn_Latn','uzn_Latn',bm25(uz['docs'],cyrl,'uzn_Latn'),uz['gold'],'synthetic-Cyrillic-query')
 record('bm25-surface','uzn_Latn','uzn_Latn',bm25(uz['docs'],back,'uzn_Latn'),uz['gold'],'roundtrip-Latin-query')
 for key in MODELS:
  enc=Encoder(key,a.model_cache,a.device);manifest['models'][key]=enc.manifest;vectors={}
  for code,c in collections.items():
   vectors[code]={}
   for kind,texts in [('docs',c['docs']),('queries',c['queries'])]:
    v,info=enc.encode(texts);vectors[code][kind]=v;manifest['truncation'][f'{key}/{code}/{kind}']=info
   record(key,code,code,vectors[code]['queries']@vectors[code]['docs'].T,c['gold'])
  for src,tgt in [('kaz_Cyrl','rus_Cyrl'),('rus_Cyrl','kaz_Cyrl'),('tur_Latn','eng_Latn'),('uzn_Latn','rus_Cyrl')]:
   record(key,src,tgt,vectors[src]['queries']@vectors[tgt]['docs'].T,collections[src]['gold'],'cross-language')
  for condition,qs in [('synthetic-Cyrillic-query',cyrl),('roundtrip-Latin-query',back)]:
   v,info=enc.encode(qs);record(key,'uzn_Latn','uzn_Latn',v@vectors['uzn_Latn']['docs'].T,uz['gold'],condition);manifest['truncation'][f'{key}/{condition}']=info
  del enc;gc.collect()
 manifest['script_probe_sha256']=sha(a.data/'uzbek-script-probe.json');manifest['script_probe']=json.loads((a.data/'uzbek-script-manifest.json').read_text());manifest['query_ids']={code:[{'index':i,'link':q[0],'question_number':q[1],'source_row':c['source_rows'][i]} for i,q in enumerate(c['qids'])] for code,c in collections.items()}
 csvout(out/'retrieval_summary.csv',summary);csvout(out/'retrieval_items.csv',details);jsonout(out/'retrieval_manifest.json',manifest)
if __name__=='__main__':main()
