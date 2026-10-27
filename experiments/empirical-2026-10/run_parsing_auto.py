"""Automatic tokenization/MWT with gold sentence boundaries; official UD scoring.
Pairs with run_parsing.py to expose the effect of supplying word boundaries.
"""
from run_parsing import TASKS,sha,blocks,words,HERE
from pathlib import Path
import argparse,json,csv,time,gc
import stanza,torch
from stanza.utils.conll import CoNLL
from stanza.utils.conll18_ud_eval import load_conllu_file,evaluate

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--resume',action='store_true');ap.add_argument('--ud-root',type=Path,required=True);ap.add_argument('--model-root',type=Path,required=True);a=ap.parse_args();out=HERE/'results';summary=[];manifest={'release':'UD 2.17','stanza':stanza.__version__,'torch':torch.__version__,'device':'cpu','protocol':'Gold sentence boundaries only; automatic tokenization/MWT, POS, lemmas, features and heads. Official alignment-aware UD scorer. No training or tuning.','runs':{}};torch.set_num_threads(4)
 if a.resume and (out/'parsing_auto_summary.csv').exists():
  summary=list(csv.DictReader((out/'parsing_auto_summary.csv').open()));manifest=json.loads((out/'parsing_auto_manifest.json').read_text())
 for lang,tree,package,kind in TASKS:
  if lang in manifest['runs']:
   assert manifest['runs'][lang]['predicted_sha256']==sha(out/f'{lang}-ud217-auto-predicted.conllu');continue
  start=time.time();gold=next((a.ud_root/f'UD_{tree}').glob('*-ud-test.conllu'));bs=blocks(gold);texts=[]
  for b in bs:
   ss=[line.split('=',1)[1].lstrip() for line in b if line.startswith('# text =')];assert len(ss)==1;assert ss[0].strip();texts.append(ss[0])
  packages={'tokenize':package,'pos':f'{package}_{kind}','lemma':f'{package}_nocharlm','depparse':f'{package}_{kind}'};procs='tokenize,pos,lemma,depparse'
  if lang in ['kk','tr']:packages['mwt']=package;procs='tokenize,mwt,pos,lemma,depparse'
  pipe=stanza.Pipeline(lang=lang,dir=str(a.model_root),processors=procs,package=packages,tokenize_no_ssplit=True,download_method=None,use_gpu=False,verbose=False);pred=out/f'{lang}-ud217-auto-predicted.conllu'
  with pred.open('w') as f:
   for begin in range(0,len(texts),32):
    docs=pipe.bulk_process(texts[begin:begin+32]);assert len(docs)==len(texts[begin:begin+32])
    for doc in docs:
     assert len(doc.sentences)==1,'Sentence boundary not retained'
     CoNLL.write_doc2conll(doc, f)
    if begin%320==0:print(lang,begin+len(docs),'/',len(texts),flush=True)
  scores=evaluate(load_conllu_file(str(gold)),load_conllu_file(str(pred)))
  for metric in ['Tokens','Words','UPOS','UFeats','Lemmas','UAS','LAS','MLAS','BLEX']:
   m=scores[metric];summary.append({'language':lang,'treebank':tree,'sentences':len(bs),'metric':metric,'precision':m.precision,'recall':m.recall,'f1':m.f1,'gold_total':m.gold_total,'system_total':m.system_total,'correct':m.correct,'aligned_total':m.aligned_total,'source':'experiments/empirical-2026-10/run_parsing_auto.py; official UD r2.17 test'})
  manifest['runs'][lang]={'gold_sha256':sha(gold),'predicted_sha256':sha(pred),'packages':packages,'model_files':{str(p.relative_to(a.model_root)):sha(p) for p in (a.model_root/lang).rglob('*.pt') if 'ner' not in p.parts},'seconds':time.time()-start}
  with (out/'parsing_auto_summary.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
  (out/'parsing_auto_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(lang,'done',flush=True);del pipe;gc.collect()
if __name__=='__main__':main()
