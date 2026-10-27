"""Strict word-level NER inputs, first-subword alignment, and scoring conversion."""
import re
import numpy as np
TAG=re.compile(r'(?:O|[BI]-[^\s]+)\Z')
def valid_iob2(tags):
    prev='O'
    for tag in tags:
        if not TAG.fullmatch(tag) or (tag.startswith('I-') and prev not in ('B-'+tag[2:],'I-'+tag[2:])):return False
        prev=tag
    return True

def read_iob2(path):
    sents=[];words=[];tags=[]
    with open(path,encoding='utf-8') as stream:
        for n,line in enumerate(stream,1):
            if not line.strip():
                if words:sents.append((words,tags));words=[];tags=[]
                continue
            parts=line.split()
            if len(parts)!=2 or not TAG.fullmatch(parts[1]):raise ValueError(f'{path}:{n}: expected token and valid BIO tag')
            words.append(parts[0]);tags.append(parts[1])
    if words:sents.append((words,tags))
    if not sents:raise ValueError(f'{path}: empty data')
    return sents

def repair_training_iob2(sents):
    """Change orphan I-X to B-X; return copied data and a zero-based edit audit."""
    out=[];edits=[]
    for sid,(words,tags) in enumerate(sents):
        fixed=[];prev='O'
        for wid,tag in enumerate(tags):
            if not TAG.fullmatch(tag):raise ValueError(tag)
            if tag.startswith('I-') and prev not in ('B-'+tag[2:],'I-'+tag[2:]):
                edits.append({'sentence':sid,'word':wid,'old':tag,'new':'B-'+tag[2:]});tag='B-'+tag[2:]
            fixed.append(tag);prev=tag
        out.append((list(words),fixed))
    return out,edits

def align_batch(examples,tokenizer,max_length):
    words=examples['tokens'];gold=examples['ner_tags']
    if len(words)!=len(gold) or any(not w or len(w)!=len(g) for w,g in zip(words,gold)):raise ValueError('word/label count mismatch or empty sentence')
    encoded=tokenizer(words,is_split_into_words=True,truncation=False)
    all_labels=[]
    for i,labels in enumerate(gold):
        ids=encoded.word_ids(batch_index=i)
        if len(ids)>max_length:raise ValueError(f'sentence {i}: {len(ids)} subwords exceed {max_length}; split with word/span reconstruction first')
        ordered=[wid for j,wid in enumerate(ids) if wid is not None and (j==0 or wid!=ids[j-1])]
        if ordered!=list(range(len(labels))):raise ValueError('tokenizer lost, reordered or repeated a word')
        seen=set();row=[]
        for wid in ids:
            row.append(-100 if wid is None or wid in seen else labels[wid]);seen.add(wid)
        all_labels.append(row)
    encoded['labels']=all_labels
    return encoded

def tag_sequences(predictions,labels,id2label):
    predictions=np.asarray(predictions);labels=np.asarray(labels)
    if predictions.ndim!=2 or predictions.shape!=labels.shape:raise ValueError('prediction/gold shape mismatch')
    truth=[];pred=[]
    for p,g in zip(predictions,labels):
        keep=g!=-100
        if not keep.any():raise ValueError('sentence has no scored words')
        truth.append([id2label[int(x)] for x in g[keep]])
        pred.append([id2label[int(x)] for x in p[keep]])
    if not truth:raise ValueError('empty evaluation')
    return truth,pred
