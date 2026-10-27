"""Cached Stanza KazNERD checkpoint on the full pinned KazNERD test split.
Exact span+type scoring with supplied word boundaries; no training or tuning.
"""
from pathlib import Path
import argparse,json,csv,hashlib,time
from collections import Counter
import stanza,torch
HERE=Path(__file__).parent
GOLD_SHA='359a1f61f6a21280c6c47b4fde9a5adcd07411d62015aa6e32d940c51f163b7a'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def spans(tags):
 out=set();start=None;typ=None
 for i,t in enumerate(list(tags)+['O']):
  if t=='O':prefix,label='O',None
  else:prefix,label=t.split('-',1)
  if prefix=='S':prefix='B'
  if prefix=='E':prefix='I'
  if prefix not in ('O','B','I'):raise ValueError(t)
  if prefix=='I' and (start is None or label!=typ):raise ValueError(f'Orphan I tag at {i}: {t}')
  if prefix in ('O','B'):
   if start is not None:out.add((start,i,typ))
   start,typ=(i,label) if prefix=='B' else (None,None)
 return out

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--test',type=Path,required=True);ap.add_argument('--model-root',type=Path,required=True);a=ap.parse_args();assert sha(a.test)==GOLD_SHA
 rows=[[line.rsplit(None,1) for line in block.splitlines()] for block in a.test.read_text().strip().split('\n\n') if block.strip()];assert len(rows)==11307 and sum(map(len,rows))==129824
 torch.set_num_threads(4);start=time.time();pipe=stanza.Pipeline(lang='kk',dir=str(a.model_root),processors='tokenize,ner',package={'ner':'kazNERD'},tokenize_pretokenized=True,download_method=None,use_gpu=False,verbose=False)
 true=Counter();pred=Counter();correct=Counter();out=HERE/'results';labels=set()
 with (out/'ner_predictions.jsonl').open('w') as f:
  for begin in range(0,len(rows),64):
   batch=rows[begin:begin+64];doc=pipe([[x[0] for x in sent] for sent in batch]);assert len(doc.sentences)==len(batch)
   for offset,(gold,sent) in enumerate(zip(batch,doc.sentences)):
    assert [x[0] for x in gold]==[t.text for t in sent.tokens];gt=[x[1] for x in gold];pt=[t.ner for t in sent.tokens];g=spans(gt);p=spans(pt)
    for _,_,k in g:true[k]+=1;labels.add(k)
    for _,_,k in p:pred[k]+=1
    for _,_,k in g&p:correct[k]+=1
    f.write(json.dumps({'sentence_id':begin+offset+1,'predicted_tags':pt,'gold_entities':len(g),'predicted_entities':len(p),'correct_entities':len(g&p)})+'\n')
   if begin%640==0:print(begin+len(batch),'/',len(rows),flush=True)
 assert set(pred)<=labels,(set(pred)-labels)
 result=[]
 for k in ['ALL',*sorted(labels)]:
  g=sum(true.values()) if k=='ALL' else true[k];p=sum(pred.values()) if k=='ALL' else pred[k];c=sum(correct.values()) if k=='ALL' else correct[k]
  result.append({'entity_type':k,'gold_entities':g,'predicted_entities':p,'correct_entities':c,'precision':c/p if p else 0,'recall':c/g if g else 0,'f1':2*c/(p+g) if p+g else 0,'source':'experiments/empirical-2026-10/run_ner.py; KazNERD bd4333d test; cached Stanza kazNERD'})
 with (out/'ner_summary.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
 files={str(p.relative_to(a.model_root)):sha(p) for p in (a.model_root/'kk').rglob('*.pt') if any(x in p.parts for x in ['ner','pretrain','forward_charlm','backward_charlm'])}
 manifest={'dataset':'KazNERD','revision':'bd4333d0f5952b9fafb2ef2ac2fefa0ad3c0333f','test_sha256':GOLD_SHA,'sentences':len(rows),'words':sum(map(len,rows)),'gold_entity_types':sorted(labels),'model_files':files,'stanza':stanza.__version__,'torch':torch.__version__,'resources_sha256':sha(a.model_root/'resources.json'),'training':False,'protocol':'Gold word and sentence boundaries; exact typed-span micro F1; BIOES S→B/E→I, reject orphan I. No test-set tuning. Pretrained benchmark re-evaluation, not new training.','seconds':time.time()-start,'predictions_sha256':sha(out/'ner_predictions.jsonl')};(out/'ner_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(result[0],flush=True)
if __name__=='__main__':main()
