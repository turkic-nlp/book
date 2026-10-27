"""Word-preserving helpers for the Chapter 7 closed-bundle tagger."""
from pathlib import Path
import torch

def canonical_label(upos, feats):
    if not upos or upos == '_':
        raise ValueError('UPOS gold label is missing')
    if not feats or feats == '_': return upos
    pairs = {}
    for field in feats.split('|'):
        key, value = field.split('=', 1)
        if key in pairs: raise ValueError('Duplicate feature: '+key)
        pairs[key] = ','.join(sorted(value.split(',')))
    return upos+'|'+'|'.join(k+'='+pairs[k] for k in sorted(pairs))

def load_conllu(path):
    sentences, labels, words, tags = [], [], [], []
    for line in Path(path).read_text().splitlines()+['']:
        if not line.strip():
            if words: sentences.append(words); labels.append(tags)
            words, tags = [], []
        elif not line.startswith('#'):
            c = line.split('\t')
            if len(c) != 10: raise ValueError('Expected 10 CoNLL-U columns')
            if c[0].isdigit():  # skip multiword-token headers and empty nodes
                words.append(c[1]); tags.append(canonical_label(c[3], c[5]))
    return sentences, labels

def word_chunks(words, tokenizer, max_len):
    """Greedy, non-overlapping chunks at whole-word boundaries; no truncation.

    A word that cannot fit alone raises, rather than silently losing its label.
    Tokenization is repeated on each candidate chunk so context-sensitive lengths
    are measured directly, not estimated by adding isolated-word lengths.
    """
    if any(not w or any(c.isspace() for c in w) for w in words):
        raise ValueError('Expected non-empty pretokenized words without whitespace')
    start = 0
    while start < len(words):
        end, best = start, None
        while end < len(words):
            enc = tokenizer(words[start:end+1], is_split_into_words=True, truncation=False)
            if len(enc['input_ids']) > max_len: break
            ids = enc.word_ids()
            if {x for x in ids if x is not None} != set(range(end+1-start)):
                raise ValueError('Tokenizer dropped a word')
            best = enc; end += 1
        if best is None: raise ValueError(f'Word at index {start} exceeds token budget')
        yield start, end, best
        start = end

def training_rows(sentences, labels, tokenizer, label2id, max_len):
    if len(sentences) != len(labels): raise ValueError('Sentence count mismatch')
    rows=[]
    for words, gold in zip(sentences,labels):
        if len(words)!=len(gold): raise ValueError('Word count mismatch')
        for start,end,enc in word_chunks(words,tokenizer,max_len):
            aligned=[]; seen=set()
            for wid in enc.word_ids():
                if wid is None or wid in seen: aligned.append(-100)
                else:
                    # Training labels must all exist; dev/test never enter this function.
                    aligned.append(label2id[gold[start+wid]]); seen.add(wid)
            rows.append({**dict(enc),'labels':aligned})
    return rows

def predict_words(words, model, tokenizer, id2label, max_len):
    model.eval(); device=next(model.parameters()).device; result=[]
    for start,end,enc in word_chunks(words,tokenizer,max_len):
        inputs={k:torch.tensor([v],device=device) for k,v in enc.items()}
        with torch.inference_mode(): pred=model(**inputs).logits[0].argmax(-1).tolist()
        seen={}
        for wid,lid in zip(enc.word_ids(),pred):
            if wid is not None and wid not in seen: seen[wid]=id2label[lid]
        if len(seen)!=end-start: raise ValueError('Prediction coverage mismatch')
        result.extend(seen[i] for i in range(end-start))
    if len(result)!=len(words): raise ValueError('Prediction count mismatch')
    return result

def score_predictions(predictions, gold, label2id):
    if len(predictions)!=len(gold): raise ValueError('Sentence count mismatch')
    total=correct=unseen=0
    for pred, labels in zip(predictions,gold):
        if len(pred)!=len(labels): raise ValueError('Word count mismatch')
        for p,g in zip(pred,labels):
            total+=1; correct+=p==g; unseen+=g not in label2id
    if not total: raise ValueError('Empty evaluation set')
    return {'words':total,'correct':correct,'accuracy':correct/total,
            'unseen_bundles':unseen,'unseen_rate':unseen/total}

def export_conllu(source, predictions, target):
    """Keep sentence/MWT/empty-node structure; replace only integer-ID UPOS/FEATS.

    Other columns remain source annotations, not model predictions. Evaluate
    only UPOS/UFeats, not lemma, XPOS, dependencies or AllTags from this export.
    """
    lines=Path(source).read_text().splitlines(); out=[]; sid=wid=0
    for line in lines+['']:
        if not line.strip():
            if wid:
                if sid>=len(predictions) or wid!=len(predictions[sid]): raise ValueError('Word count mismatch')
                sid+=1;wid=0
        elif not line.startswith('#'):
            c=line.split('\t')
            if len(c)!=10: raise ValueError('Expected CoNLL-U')
            if c[0].isdigit():
                if sid>=len(predictions) or wid>=len(predictions[sid]): raise ValueError('Missing prediction')
                tag=predictions[sid][wid]; upos,sep,feats=tag.partition('|')
                c[3]=upos;c[5]=feats if sep else '_';line='\t'.join(c);wid+=1
        out.append(line)
    if sid!=len(predictions): raise ValueError('Extra predictions')
    Path(target).write_text('\n'.join(out).rstrip()+'\n\n')
