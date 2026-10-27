"""Pretrained Stanza evaluation on official UD 2.17, with gold sentence/word segmentation.
Only word forms are passed to the model. Gold POS, morphology, lemmas and heads are never inputs.
"""
from pathlib import Path
import argparse,json,csv,hashlib,io,time,gc
import stanza,torch
from stanza.utils.conll18_ud_eval import load_conllu_file,evaluate
HERE=Path(__file__).parent
TASKS=[('kk','Kazakh-KTB','ktb','charlm'),('ky','Kyrgyz-KTMU','ktmu','nocharlm'),('tr','Turkish-IMST','imst','charlm'),('ug','Uyghur-UDT','udt','nocharlm')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def blocks(p):return [b.splitlines() for b in p.read_text().strip().split('\n\n') if b.strip()]
def words(b):return [x.split('\t') for x in b if x and not x.startswith('#') and x.split('\t')[0].isdigit()]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ud-root',type=Path,required=True);ap.add_argument('--model-root',type=Path,required=True);a=ap.parse_args();out=HERE/'results';summary=[];manifest={'release':'UD 2.17','stanza':stanza.__version__,'torch':torch.__version__,'device':'cpu','protocol':'Gold sentences and syntactic-word segmentation; predicted POS/lemmas/features/heads. Not end-to-end raw-text parsing. No training or tuning. Model exposure to older benchmark versions is not independently audited.','scorer':{'path':'stanza.utils.conll18_ud_eval','sha256':sha(__import__('stanza.utils.conll18_ud_eval',fromlist=['x']).__file__)},'runs':{}}
 torch.set_num_threads(4)
 for lang,tree,package,kind in TASKS:
  start=time.time();gold=next((a.ud_root/f'UD_{tree}').glob('*-ud-test.conllu'));bs=blocks(gold);prediction=out/f'{lang}-ud217-predicted.conllu';print('Loading',lang,flush=True)
  model_files={str(p.relative_to(a.model_root)):sha(p) for p in (a.model_root/lang).rglob('*.pt') if any(part in ['pos','lemma','depparse','pretrain','forward_charlm','backward_charlm'] for part in p.parts)}
  pipeline=stanza.Pipeline(lang=lang,dir=str(a.model_root),processors='tokenize,pos,lemma,depparse',package={'pos':f'{package}_{kind}','lemma':f'{package}_nocharlm','depparse':f'{package}_{kind}'},tokenize_pretokenized=True,download_method=None,use_gpu=False,verbose=False)
  with prediction.open('w') as f:
   for start_batch in range(0,len(bs),32):
    batch=bs[start_batch:start_batch+32];inputs=[[w[1] for w in words(b)] for b in batch];doc=pipeline(inputs);assert len(doc.sentences)==len(batch)
    for b,sent in zip(batch,doc.sentences):
     g=words(b);assert len(g)==len(sent.words);pred=iter(sent.words)
     for line in b:
      fields=line.split('\t')
      if not line.startswith('#') and fields[0].isdigit():
       w=next(pred);assert w.text==fields[1];fields[2:8]=[w.lemma or '_',w.upos or '_',w.xpos or '_',w.feats or '_',str(w.head),w.deprel or '_'];fields[8]='_';f.write('\t'.join(fields)+'\n')
      else:f.write(line+'\n')
     f.write('\n')
    if start_batch%320==0:print(lang,start_batch+len(batch),'/',len(bs),flush=True)
  scores=evaluate(load_conllu_file(str(gold)),load_conllu_file(str(prediction)))
  nwords=sum(len(words(b)) for b in bs)
  for metric in ['UPOS','UFeats','Lemmas','UAS','LAS','MLAS','BLEX']:
   m=scores[metric];summary.append({'language':lang,'treebank':tree,'sentences':len(bs),'syntactic_words':nwords,'metric':metric,'precision':m.precision,'recall':m.recall,'f1':m.f1,'gold_total':m.gold_total,'system_total':m.system_total,'correct':m.correct,'aligned_total':m.aligned_total,'source':'experiments/empirical-2026-10/run_parsing.py; official UD r2.17 test'})
  manifest['runs'][lang]={'gold_path':str(gold),'gold_sha256':sha(gold),'predicted_sha256':sha(prediction),'model_files':model_files,'resources_sha256':sha(a.model_root/'resources.json'),'seconds':time.time()-start}
  with (out/'parsing_summary.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
  (out/'parsing_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(lang,'done',summary[-4],flush=True);del pipeline;gc.collect()
if __name__=='__main__':main()
