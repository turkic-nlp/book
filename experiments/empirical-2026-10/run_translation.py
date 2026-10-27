"""Full FLORES-200 Turkish↔Kazakh pretrained NLLB-600M baseline; no fine-tuning.
Greedy decoding is fixed in advance for an affordable reproducible baseline.
"""
from common import *
import argparse,time
import torch
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
from sacrebleu.metrics import BLEU,CHRF
REV='f8d333a098d19b4fd9a8b18f94170487ad3f821d'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--archive',type=Path,required=True);ap.add_argument('--model-cache',type=Path,required=True);ap.add_argument('--device',default='mps');a=ap.parse_args();texts,inputs=flores(a.archive);out=Path(__file__).parent/'results';p=a.model_cache/'models--facebook--nllb-200-distilled-600M'/'snapshots'/REV;torch.set_num_threads(4);tok=AutoTokenizer.from_pretrained(p,local_files_only=True);model=AutoModelForSeq2SeqLM.from_pretrained(p,local_files_only=True,dtype=torch.float32).to(a.device).eval();summ=[];manifest={'model':'facebook/nllb-200-distilled-600M','revision':REV,'weights':{x.name:sha(x) for x in p.glob('*') if x.suffix in ['.bin','.safetensors']},'tokenizer_sha256':sha(p/'tokenizer.json'),'archive_sha256':ARCHIVE_SHA,'dataset':'original FLORES-200 devtest','inputs':{k:inputs[k] for k in ['tur_Latn','kaz_Cyrl']},'decoding':{'num_beams':1,'do_sample':False,'max_new_tokens':256,'forced_bos':'explicit target language token','batch_size':8},'device':a.device,'dtype':'float32','torch':torch.__version__,'transformers':__import__('transformers').__version__,'fine_tuning':False,'source_truncation':False,'scope':'Greedy pretrained baseline, not reproduction of the published beam-search NLLB scores. No independent contamination audit.','runs':{}}
 with torch.inference_mode():
  for src,tgt in [('tur_Latn','kaz_Cyrl'),('kaz_Cyrl','tur_Latn')]:
   tok.src_lang=src;forced=tok.convert_tokens_to_ids(tgt);assert forced!=tok.unk_token_id;hyp=[];audit=[];start=time.time()
   for begin in range(0,len(texts[src]),8):
    batch=texts[src][begin:begin+8];t=tok(batch,return_tensors='pt',padding=True,truncation=False);lengths=t.attention_mask.sum(1).tolist();assert max(lengths)<=512,'Source longer than documented training limit; no silent truncation'
    ids=model.generate(**t.to(a.device),forced_bos_token_id=forced,num_beams=1,do_sample=False,max_new_tokens=256);decoded=tok.batch_decode(ids,skip_special_tokens=True);hyp.extend(decoded)
    for offset,(tokens,n,translation) in enumerate(zip(ids.cpu().tolist(),lengths,decoded)):
     # The decoder starts with EOS; only a later EOS indicates completed generation.
     ended=tok.eos_token_id in tokens[2:];audit.append({'row_id':begin+offset+1,'source_tokens':n,'ended_with_eos':ended,'output':translation})
    if begin%80==0:print(src,tgt,begin+len(batch),'/',len(texts[src]),flush=True)
   assert len(hyp)==1012;pred=out/f'mt-{src}-{tgt}.jsonl';pred.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in audit));bleu=BLEU(tokenize='13a');chrf=CHRF(char_order=6,word_order=0,beta=2);chrfpp=CHRF(char_order=6,word_order=2,beta=2)
   scores={name:metric.corpus_score(hyp,[texts[tgt]]).score for name,metric in [('bleu',bleu),('chrf',chrf),('chrfpp',chrfpp)]};summ.append({'src':src,'tgt':tgt,'sentences':1012,**scores,'outputs_without_eos':sum(not x['ended_with_eos'] for x in audit),'empty_outputs':sum(not x.strip() for x in hyp),'source':'experiments/empirical-2026-10/run_translation.py; original FLORES-200 devtest'})
   manifest['runs'][f'{src}->{tgt}']={'metric_signatures':{name:str(m.get_signature()) for name,m in [('bleu',bleu),('chrf',chrf),('chrfpp',chrfpp)]},'predictions_sha256':sha(pred),'max_source_tokens':max(x['source_tokens'] for x in audit),'seconds':time.time()-start};csvout(out/'translation_summary.csv',summ);jsonout(out/'translation_manifest.json',manifest);print(summ[-1],flush=True)
if __name__=='__main__':main()
