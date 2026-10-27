"""Audit pinned KazNERD files using a pinned tokenizer, without model weights.
Usage: python audit_release.py DATA_DIR TOKENIZER_DIR OUTPUT_JSON
"""
from pathlib import Path
import hashlib,json,sys
from transformers import AutoTokenizer
from ner_utils import *
root=Path(sys.argv[1]);tok=AutoTokenizer.from_pretrained(sys.argv[2],local_files_only=True)
result={'kaznerd_revision':'bd4333d0f5952b9fafb2ef2ac2fefa0ad3c0333f','tokenizer_revision':'c23d21b0620b635a76227c604d44e43a9f0ee389','splits':{}}
for split in ('train','valid','test'):
    path=root/f'IOB2_{split}.txt';raw=read_iob2(path);invalid=sum(not valid_iob2(t) for _,t in raw)
    fixed,edits=repair_training_iob2(raw)
    if split!='train' and edits:raise ValueError('invalid evaluation gold')
    maxlen=0;words=0
    for start in range(0,len(fixed),256):
        batch=fixed[start:start+256]
        enc=align_batch({'tokens':[w for w,_ in batch],'ner_tags':[[0]*len(w) for w,_ in batch]},tok,512)
        maxlen=max(maxlen,max(map(len,enc['input_ids'])));words+=sum(len(w) for w,_ in batch)
    result['splits'][split]={'sentences':len(raw),'words':words,'max_words':max(len(w) for w,_ in raw),'max_subwords_including_special':maxlen,'invalid_sentences':invalid,'orphan_tags':len(edits),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    if split=='train':result['training_repairs']=edits
Path(sys.argv[3]).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['splits'],indent=2))
