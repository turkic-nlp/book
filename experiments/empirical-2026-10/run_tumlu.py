"""Zero-shot constrained next-letter scoring with cached Qwen2.5-1.5B-Instruct.
This is not free-form generation, mT5 scoring, full TUMLU or a contamination audit.
"""
from common import sha,jsonout,csvout
from collections import Counter
from pathlib import Path
import argparse,json,hashlib,string,math,time
import numpy as np
import pyarrow.parquet as pq
import torch
from transformers import AutoModelForCausalLM,AutoTokenizer
REV='989aa7980e4cf806f80c7fef2b1adb7bc71aa306'
INSTRUCTION='Select the correct option. Reply with only its letter.'
def prepare(row,index):
 choices=row['choices']
 if not isinstance(choices,list) or len(choices)!=4 or any(not isinstance(c,str) or not c.strip() for c in choices):raise ValueError('invalid choices')
 if row['answer'] not in 'ABCD' or len(row['answer'])!=1:raise ValueError('invalid answer')
 if not row['question'].strip():raise ValueError('empty question')
 text=INSTRUCTION+'\n\n'+row['question']+'\n'+'\n'.join(f'{l}. {c}' for l,c in zip('ABCD',choices))
 return {'row_index':index,'id':hashlib.sha256(json.dumps([row['question'],choices],ensure_ascii=False).encode()).hexdigest(),'prompt':text,'gold':row['answer'],'subject':row['subject']}
def wilson(k,n):
 z=1.959963984540054;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return [c-h,c+h]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True);ap.add_argument('--model-cache',type=Path,required=True);ap.add_argument('--device',default='mps');a=ap.parse_args();root=Path(__file__).resolve().parents[2];out=Path(__file__).parent/'results';baseline=json.loads((root/'experiments/remaining_revision/source-manifest.json').read_text());valid={};invalid=[];inputhash={}
 for split in ['dev','test']:
  p=a.data/f'{split}-00000-of-00001.parquet';expected=baseline[f'tumlu/kazakh/{p.name}']['sha256'];assert sha(p)==expected;inputhash[split]=expected;rows=pq.read_table(p).to_pylist();valid[split]=[]
  for i,r in enumerate(rows):
   try:valid[split].append(prepare(r,i))
   except ValueError as e:invalid.append({'split':split,'row_index':i,'reason':str(e)})
  assert len({x['id'] for x in valid[split]})==len(valid[split])
 assert len(valid['test'])==797 and len(valid['dev'])==40;assert not ({x['id'] for x in valid['dev']} & {x['id'] for x in valid['test']})
 assert [x['row_index'] for x in invalid]==[362,390]
 p=a.model_cache/'models--Qwen--Qwen2.5-1.5B-Instruct'/'snapshots'/REV;tok=AutoTokenizer.from_pretrained(p,local_files_only=True);tok.padding_side='left';ids=[tok.encode(l,add_special_tokens=False) for l in 'ABCD'];assert all(len(x)==1 for x in ids);ids=[x[0] for x in ids]
 torch.set_num_threads(4);model=AutoModelForCausalLM.from_pretrained(p,local_files_only=True,dtype=torch.float16).to(a.device).eval();start=time.time();results=[];lengths=[]
 with (out/'tumlu_predictions.jsonl').open('w') as f,torch.inference_mode():
  for begin in range(0,len(valid['test']),4):
   batch=valid['test'][begin:begin+4];prompts=[tok.apply_chat_template([{'role':'user','content':x['prompt']}],tokenize=False,add_generation_prompt=True) for x in batch];t=tok(prompts,return_tensors='pt',padding=True,truncation=False,add_special_tokens=False);ll=t.attention_mask.sum(1).tolist();lengths+=ll;assert max(ll)<=model.config.max_position_embeddings,'Input exceeds model context; no truncation permitted'
   logits=model(**t.to(a.device),logits_to_keep=1).logits[:,-1,:].float();lp=logits.log_softmax(-1);candidate=lp[:,ids].cpu().numpy();assert np.isfinite(candidate).all()
   for item,values,n in zip(batch,candidate,ll):
    prediction='ABCD'[int(np.argmax(values))];res={k:item[k] for k in ['row_index','id','gold','subject']};res.update(prediction=prediction,input_tokens=n,candidate_logprobs=[float(v) for v in values],letter_probability_mass=float(np.exp(values).sum()));results.append(res);f.write(json.dumps(res)+'\n')
   if begin%80==0:print(begin+len(batch),'/',797,flush=True)
 def summarize(rr):
  n=len(rr);k=sum(r['gold']==r['prediction'] for r in rr);return {'n':n,'correct':k,'accuracy':k/n,'wilson95':wilson(k,n),'uniform_random_expected_accuracy':.25}
 report={'dataset':'jafarisbarov/TUMLU-mini','dataset_revision':'3523de73e1d1d784118d328f40b49d53afd6f334','config':'kazakh','split':'test','released_count':799,'evaluated_count':797,'excluded':invalid,'input_sha256':inputhash,'model':'Qwen/Qwen2.5-1.5B-Instruct','model_revision':REV,'weights_sha256':sha(p/'model.safetensors'),'tokenizer_sha256':sha(p/'tokenizer.json'),'tokenizer_config_sha256':sha(p/'tokenizer_config.json'),'device':a.device,'dtype':'float16','torch':torch.__version__,'transformers':__import__('transformers').__version__,'instruction':INSTRUCTION,'prompt_sha256':hashlib.sha256('\n'.join(x['prompt'] for x in valid['test']).encode()).hexdigest(),'scoring':'Zero-shot chat template; next-token log probability of single-token A/B/C/D; forced choice; no EOS or answer-text scoring; no generation','candidate_token_ids':ids,'gold_and_cot_in_prompt':False,'dev_examples_in_prompt':False,'tuning':False,'truncation':False,'max_input_tokens':max(lengths),'overall':summarize(results),'subjects':{s:summarize([r for r in results if r['subject']==s]) for s in sorted({r['subject'] for r in results})},'median_letter_probability_mass':float(np.median([r['letter_probability_mass'] for r in results])),'seconds':time.time()-start,'contamination_audit_completed':False,'predictions_sha256':sha(out/'tumlu_predictions.jsonl')}
 dev_counts=Counter(x['gold'] for x in valid['dev']);mode=sorted(dev_counts,key=lambda k:(-dev_counts[k],k))[0]
 report['dev_majority_baseline']={'letter':mode,'dev_counts':dict(dev_counts),'test':summarize([dict(x,prediction=mode) for x in results])};report['gold_letter_counts']=dict(Counter(x['gold'] for x in results));report['predicted_letter_counts']=dict(Counter(x['prediction'] for x in results))
 jsonout(out/'tumlu_summary.json',report);print(report['overall'],flush=True)
if __name__=='__main__':main()
