"""Pinned inputs and model-card-equivalent mean pooling for the October studies."""
from pathlib import Path
import hashlib,json,csv,tarfile,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
LANGS={'eng_Latn':'English','rus_Cyrl':'Russian','tur_Latn':'Turkish','azj_Latn':'North Azerbaijani','azb_Arab':'South Azerbaijani','tuk_Latn':'Turkmen','kaz_Cyrl':'Kazakh','kir_Cyrl':'Kyrgyz','tat_Cyrl':'Tatar','bak_Cyrl':'Bashkir','crh_Latn':'Crimean Tatar','uzn_Latn':'Northern Uzbek','uig_Arab':'Uyghur'}
MODELS={'minilm':('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2','e8f8c211226b894fcb81acc59f3b34ba3efd5f42'),'xlmr':('sentence-transformers/paraphrase-xlm-r-multilingual-v1','c2e19453aae46f98a865abfdf173f35f2e119f5a')}
ARCHIVE_SHA='b8b0b76783024b85797e5cc75064eb83fc5288b41e9654dabc7be6ae944011f6'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def csvout(p,rows):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('w',newline='',encoding='utf8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def jsonout(p,obj):Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def flores(path,split='devtest'):
 assert sha(path)==ARCHIVE_SHA,'Incorrect FLORES-200 archive'
 out={};manifest={}
 with tarfile.open(path) as tf:
  for code in LANGS:
   member=f'./flores200_dataset/{split}/{code}.{split}';raw=tf.extractfile(member).read();lines=raw.decode().splitlines();assert len(lines)==(1012 if split=='devtest' else 997)
   assert all(x.strip() for x in lines);out[code]=[x.strip() for x in lines];manifest[code]={'sha256':hashlib.sha256(raw).hexdigest(),'member':member,'rows':len(lines),'exact_duplicate_rows':len(lines)-len(set(lines))}
 return out,manifest
class Encoder:
 def __init__(self,key,cache,device='mps'):
  import torch
  from transformers import AutoTokenizer,AutoModel
  repo,rev=MODELS[key];p=Path(cache)/('models--'+repo.replace('/','--'))/'snapshots'/rev
  self.torch=torch;torch.set_num_threads(4);self.device=device;self.tok=AutoTokenizer.from_pretrained(p,local_files_only=True);self.model=AutoModel.from_pretrained(p,local_files_only=True).to(device).eval()
  conf=json.loads((p/'sentence_bert_config.json').read_text());pool=json.loads((p/'1_Pooling/config.json').read_text());assert pool['pooling_mode_mean_tokens'] and not pool['pooling_mode_cls_token'];self.maxlen=conf['max_seq_length']
  self.manifest={'repo_id':repo,'revision':rev,'device':device,'max_length':self.maxlen,'pooling':'attention-mask mean over all retained tokens including specials, then L2 normalization','weights_sha256':sha(p/'model.safetensors'),'tokenizer_sha256':sha(p/'tokenizer.json'),'torch':torch.__version__,'transformers':__import__('transformers').__version__}
 def encode(self,texts,batch=24):
  lengths=[len(x) for x in self.tok(texts,truncation=False)['input_ids']];out=[]
  with self.torch.inference_mode():
   for start in range(0,len(texts),batch):
    t=self.tok(texts[start:start+batch],padding=True,truncation=True,max_length=self.maxlen,return_tensors='pt').to(self.device)
    h=self.model(**t).last_hidden_state;m=t['attention_mask'].unsqueeze(-1);v=(h*m).sum(1)/m.sum(1).clamp(min=1);v=self.torch.nn.functional.normalize(v,p=2,dim=1);out.append(v.cpu().numpy())
  a=np.concatenate(out);assert np.isfinite(a).all();assert np.allclose(np.linalg.norm(a,axis=1),1,atol=1e-4)
  return a,{'rows':len(texts),'truncated_rows':sum(n>self.maxlen for n in lengths),'max_untruncated_tokens':max(lengths)}
