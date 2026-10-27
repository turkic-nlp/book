"""Train a text classifier on explicit JSONL splits; optional XLM-R LoRA.
Run from book root; see README.md for schema and inference commands.
"""
import argparse, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'common'))  # code/common/common.py
from common import check_splits, read_jsonl, digest
MODEL='FacebookAI/xlm-roberta-base'
REVISION='e73636d4f797dec63c3081bb6ed5c7b0bb3f2089'

def encode(rows, tokenizer, label2id):
    from datasets import Dataset
    values=[]
    for row in rows:
        inputs=tokenizer(row['text'], truncation=False)
        if len(inputs['input_ids']) > 512:
            raise ValueError(f"overlength item {row['id']}; define document chunking first")
        values.append({**inputs, 'labels':label2id[row['label']]})
    return Dataset.from_list(values)

def main():
    import numpy as np, torch
    from sklearn.metrics import accuracy_score, f1_score
    from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
        Trainer, TrainingArguments, DataCollatorWithPadding, set_seed)
    p=argparse.ArgumentParser()
    p.add_argument('data', type=Path); p.add_argument('output', type=Path)
    p.add_argument('--lora', action='store_true'); p.add_argument('--seed', type=int, default=42)
    p.add_argument('--epochs', type=float, default=3)
    a=p.parse_args(); set_seed(a.seed)
    rows={s:read_jsonl(a.data/f'{s}.jsonl') for s in ('train','dev','test')}
    counts=check_splits(rows)
    labels=sorted({r['label'] for r in rows['train']})
    if len(labels)<2: raise ValueError('need at least two training classes')
    label2id={label:i for i,label in enumerate(labels)}
    if any(r['label'] not in label2id for rs in rows.values() for r in rs):
        raise ValueError('evaluation label missing from training schema')
    tok=AutoTokenizer.from_pretrained(MODEL, revision=REVISION)
    model=AutoModelForSequenceClassification.from_pretrained(MODEL, revision=REVISION,
        num_labels=len(labels), label2id=label2id, id2label={i:l for l,i in label2id.items()})
    if a.lora:
        from peft import LoraConfig, TaskType, get_peft_model
        model=get_peft_model(model, LoraConfig(task_type=TaskType.SEQ_CLS,r=8,
            lora_alpha=16,lora_dropout=.1,target_modules=['query','value'],
            modules_to_save=['classifier']))
    trainable=sum(p.numel() for p in model.parameters() if p.requires_grad)
    total=sum(p.numel() for p in model.parameters())
    data={s:encode(rs,tok,label2id) for s,rs in rows.items()}
    def metrics(result):
        y=result.predictions.argmax(-1)
        return {'accuracy':accuracy_score(result.label_ids,y),
                'macro_f1':f1_score(result.label_ids,y,labels=list(range(len(labels))),average='macro',zero_division=0)}
    args=TrainingArguments(output_dir=str(a.output/'checkpoints'),num_train_epochs=a.epochs,
        per_device_train_batch_size=8,per_device_eval_batch_size=8,learning_rate=2e-4 if a.lora else 2e-5,
        eval_strategy='epoch',save_strategy='epoch',load_best_model_at_end=True,
        metric_for_best_model='macro_f1',greater_is_better=True,save_total_limit=1,
        seed=a.seed,data_seed=a.seed,report_to='none')
    trainer=Trainer(model=model,args=args,train_dataset=data['train'],eval_dataset=data['dev'],
        data_collator=DataCollatorWithPadding(tok),processing_class=tok,compute_metrics=metrics)
    trainer.train()
    saved=a.output/'model'; trainer.save_model(saved); tok.save_pretrained(saved)
    # Reload independently: the random task head must be saved with the adapter.
    if a.lora:
        from peft import PeftModel
        base=AutoModelForSequenceClassification.from_pretrained(MODEL,revision=REVISION,
            num_labels=len(labels),label2id=label2id,id2label={i:l for l,i in label2id.items()})
        restored=PeftModel.from_pretrained(base,saved)
    else: restored=AutoModelForSequenceClassification.from_pretrained(saved)
    probe=tok(rows['dev'][0]['text'],return_tensors='pt')
    trainer.model.to('cpu').eval(); restored.to('cpu').eval()
    with torch.inference_mode():
        torch.testing.assert_close(trainer.model(**probe).logits,restored(**probe).logits)
    # Test is used only after the recipe and selected checkpoint are frozen.
    trainer.model.to(args.device)
    result=trainer.predict(data['test'])
    manifest={'model':MODEL,'revision':REVISION,'seed':a.seed,'counts':counts,
        'input_hashes':{s:digest(rs) for s,rs in rows.items()},'label2id':label2id,
        'trainable':trainable,'total':total,'test_metrics':result.metrics,'lora':a.lora}
    (a.output/'run.json').write_text(json.dumps(manifest,indent=2)+'\n')
    with (a.output/'predictions.jsonl').open('w') as f:
        for row,pred in zip(rows['test'],result.predictions.argmax(-1)):
            f.write(json.dumps({'id':row['id'],'gold':row['label'],'prediction':labels[int(pred)]})+'\n')
if __name__=='__main__': main()
