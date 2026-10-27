"""TUMLU-mini schema audit and conditional label scoring (mT5 diagnostic)."""
import argparse, json, string
from collections import defaultdict
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'common'))  # code/common/common.py
from common import digest, wilson
DATASET='jafarisbarov/TUMLU-mini'
REVISION='3523de73e1d1d784118d328f40b49d53afd6f334'
MODEL='google/mt5-base'
MODEL_REVISION='2eb15465c5dd7f72a8f7984306ad05ebc3dd1e1f'

def prepare(row):
    choices=row['choices']
    if not isinstance(choices,list) or not 2<=len(choices)<=26 or any(not isinstance(c,str) or not c.strip() for c in choices):
        raise ValueError('invalid choices')
    letters=list(string.ascii_uppercase[:len(choices)])
    if row['answer'] not in letters: raise ValueError('invalid answer letter')
    if not row['question'].strip(): raise ValueError('empty question')
    # Deliberately never include the gold answer or released CoT in the input.
    prompt=row['question']+'\n'+'\n'.join(f'{l}. {c}' for l,c in zip(letters,choices))+'\nAnswer:'
    return {'id':digest([row['question'],choices]),'prompt':prompt,'candidates':letters,
            'gold':letters.index(row['answer']),'subject':row['subject']}

def audit_rows(rows, split):
    valid=[];invalid=[]
    for index,row in enumerate(rows):
        try:valid.append(prepare(row))
        except (ValueError,KeyError,TypeError) as exc:
            invalid.append({'split':split,'row_index':index,
                'id':digest([row.get('question'),row.get('choices')]),'reason':str(exc)})
    return valid,invalid

def sequence_logprobs(logits, labels):
    """Sum log P(candidate tokens incl. EOS); ignore only padding (-100)."""
    import torch
    mask=labels.ne(-100)
    safe=labels.masked_fill(~mask,0)
    return logits.log_softmax(-1).gather(-1,safe.unsqueeze(-1)).squeeze(-1).masked_fill(~mask,0).sum(-1)

def score(model, tokenizer, item, max_input=512, max_target=32):
    import torch
    model.eval()
    x=tokenizer([item['prompt']]*len(item['candidates']),return_tensors='pt',padding=True,truncation=False)
    y=tokenizer(text_target=item['candidates'],return_tensors='pt',padding=True,truncation=False)
    if x.input_ids.shape[1]>max_input or y.input_ids.shape[1]>max_target:
        raise ValueError(f"overlength benchmark item {item['id']}; do not silently truncate")
    labels=y.input_ids.masked_fill(y.attention_mask.eq(0),-100).to(model.device)
    with torch.inference_mode():
        logits=model(**x.to(model.device),labels=labels).logits
    return sequence_logprobs(logits,labels).cpu().tolist()

def summary(rows):
    if not rows: raise ValueError('empty evaluation')
    k=sum(r['prediction']==r['gold'] for r in rows); n=len(rows)
    return {'n':n,'correct':k,'accuracy':k/n,'wilson95':wilson(k,n),
            'uniform_random_expectation':sum(1/r['n_choices'] for r in rows)/n}

def main():
    from datasets import load_dataset
    p=argparse.ArgumentParser();p.add_argument('--config',default='kazakh')
    p.add_argument('--split',choices=['dev','test'],default='dev')
    p.add_argument('--output',type=Path,required=True);p.add_argument('--audit-only',action='store_true')
    p.add_argument('--device',default='cpu');p.add_argument('--exclude-invalid',action='store_true');a=p.parse_args()
    ds=load_dataset(DATASET,a.config,revision=REVISION)
    audited={s:audit_rows([dict(r) for r in ds[s]],s) for s in ('dev','test')}
    data={s:value[0] for s,value in audited.items()}
    invalid=[row for value in audited.values() for row in value[1]]
    for s,items in data.items():
        if len({r['id'] for r in items})!=len(items): raise ValueError(f'duplicate questions in {s}')
    if {r['id'] for r in data['dev']} & {r['id'] for r in data['test']}: raise ValueError('dev/test question overlap')
    report={'dataset':DATASET,'revision':REVISION,'config':a.config,'counts':{s:len(rs) for s,rs in data.items()},
            'model':MODEL,'model_revision':MODEL_REVISION,'split':a.split,'scoring':'sum logprob of letter plus EOS'}
    a.output.mkdir(parents=True,exist_ok=True)
    report['released_counts']={s:len(ds[s]) for s in data}
    report['invalid_rows']=invalid
    report['invalid_policy']='exclude and record' if a.exclude_invalid else 'reject scoring'
    (a.output/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
    if any(r['split']==a.split for r in invalid) and not a.audit_only and not a.exclude_invalid:
        raise ValueError('invalid released items: inspect audit.json; exclusion requires --exclude-invalid')
    if not a.audit_only:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        tok=AutoTokenizer.from_pretrained(MODEL,revision=MODEL_REVISION)
        model=AutoModelForSeq2SeqLM.from_pretrained(MODEL,revision=MODEL_REVISION).to(a.device)
        results=[]
        for item in data[a.split]:
            values=score(model,tok,item)
            results.append({'id':item['id'],'subject':item['subject'],'gold':item['gold'],
                'prediction':max(range(len(values)),key=values.__getitem__),
                'n_choices':len(values),'scores':values})
        report['overall']=summary(results)
        report['subjects']={s:summary([r for r in results if r['subject']==s]) for s in sorted({r['subject'] for r in results})}
        (a.output/'predictions.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in results))
    (a.output/'run.json').write_text(json.dumps(report,indent=2)+'\n')
if __name__=='__main__': main()
