"""Check actual UD data with a pinned local BERTurk tokenizer, without weights.
Usage: python check_ud_alignment.py UD_IMST_DIR TOKENIZER_DIR
"""
from pathlib import Path
import hashlib,json,sys
import transformers
from transformers import AutoTokenizer
from morph_tagging import load_conllu,training_rows,word_chunks
root,tokdir=map(Path,sys.argv[1:])
tok=AutoTokenizer.from_pretrained(tokdir,local_files_only=True,use_fast=True)
train_sents,train_labels=load_conllu(root/'tr_imst-ud-train.conllu')
l2i={v:i for i,v in enumerate(sorted({v for seq in train_labels for v in seq}))}
results={}
for split in ['train','dev','test']:
    path=root/f'tr_imst-ud-{split}.conllu';sents,labels=load_conllu(path)
    chunks=words=long_sentences=max_ids=0
    for sent in sents:
        count=0
        for start,end,enc in word_chunks(sent,tok,512):
            chunks+=1;words+=end-start;count+=1;max_ids=max(max_ids,len(enc['input_ids']))
        long_sentences+=count>1
    assert words==sum(map(len,sents))
    if split=='train':
        rows=training_rows(sents,labels,tok,l2i,512)
        assert sum(sum(x!=-100 for x in r['labels']) for r in rows)==words
    results[split]={'sentences':len(sents),'words':words,'chunks':chunks,'sentences_chunked':long_sentences,
       'max_chunk_tokens':max_ids,'unseen_gold_bundles':sum(v not in l2i for seq in labels for v in seq),
       'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
obj={'date':'2026-10-14','ud_release':'2.17','tokenizer':'dbmdz/bert-base-turkish-cased',
    'revision':(tokdir/'revision.txt').read_text().strip(),'transformers':transformers.__version__,
    'tokenizer_files_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in tokdir.iterdir() if p.is_file()},
    'label_classes':len(l2i),'splits':results,'scope':'Tokenization/alignment only; no pretrained model loaded or accuracy measured.'}
Path(__file__).with_name('ud-alignment.json').write_text(json.dumps(obj,indent=2)+'\n');print(json.dumps(obj,indent=2))
