"""Full original FLORES-200 devtest bitext retrieval with cached pretrained encoders.
No fitting, threshold tuning or language-training-coverage regression is performed.
"""
from common import *
import argparse,itertools,time

def score_pair(a,b,texts):
 s=a.astype(np.float64)@b.astype(np.float64).T;best=s.max(1);tie=np.isclose(s,best[:,None],atol=1e-6,rtol=0)
 equal=np.equal(np.array(texts,dtype=object)[:,None],np.array(texts,dtype=object)[None,:]);credit=(tie&equal).sum(1)/tie.sum(1)
 pred=s.argmax(1);return credit,pred,tie.sum(1)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--archive',type=Path,required=True);ap.add_argument('--model-cache',type=Path,required=True);ap.add_argument('--vector-cache',type=Path,required=True);ap.add_argument('--device',default='mps');a=ap.parse_args()
 out=Path(__file__).parent/'results';a.vector_cache.mkdir(exist_ok=True,parents=True);texts,inputs=flores(a.archive);summ=[];itemfile=out/'bitext_items.csv';manifest={'dataset':'original FLORES-200','split':'devtest','archive_sha256':ARCHIVE_SHA,'input_files':inputs,'model_training':False,'candidate_scope':'all 1012 target rows per direction','tie_tolerance':1e-6,'tie_credit':'fraction of maximum-score ties whose target text exactly equals the aligned target text','conditions':'native text only','models':{},'truncation':{},'source':'https://github.com/facebookresearch/flores/blob/main/flores200/README.md'}
 with itemfile.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['model','src','tgt','row_id','predicted_row_id','top1_credit','max_score_ties']);w.writeheader()
  for key in MODELS:
   start=time.time();enc=Encoder(key,a.model_cache,a.device);manifest['models'][key]=enc.manifest;vectors={}
   for code,rows in texts.items():
    p=a.vector_cache/f'{key}-{code}-devtest.npy';m=p.with_suffix('.json')
    fingerprint={'input':inputs[code]['sha256'],'model':enc.manifest}
    if p.exists() and m.exists() and json.loads(m.read_text())['fingerprint']==fingerprint:
     v=np.load(p);info=json.loads(m.read_text())['stats']
    else:
     v,info=enc.encode(rows);np.save(p,v);jsonout(m,{'fingerprint':fingerprint,'stats':info})
    vectors[code]=v;manifest['truncation'][f'{key}/{code}']=info;print(key,code,info,flush=True)
   del enc
   for src,tgt in itertools.permutations(texts,2):
    credit,pred,ties=score_pair(vectors[src],vectors[tgt],texts[tgt]);summ.append({'model':key,'src':src,'tgt':tgt,'n_queries':len(credit),'n_candidates':len(texts[tgt]),'top1_accuracy':float(credit.mean()),'queries_with_ties':int((ties>1).sum()),'source':'experiments/empirical-2026-10/run_bitext.py; original FLORES-200 devtest'})
    w.writerows({'model':key,'src':src,'tgt':tgt,'row_id':i+1,'predicted_row_id':int(pred[i])+1,'top1_credit':float(credit[i]),'max_score_ties':int(ties[i])} for i in range(len(credit)))
   csvout(out/'bitext_summary.csv',summ);jsonout(out/'bitext_manifest.json',manifest);print(key,'seconds',time.time()-start,flush=True)
if __name__=='__main__':main()
