"""Kazakh→Kyrgyz NLLB tutorial. Run from the book root; see README.md.
Full training needs real, independently partitioned data and suitable hardware.
"""
from pathlib import Path
import argparse,csv,hashlib,json,unicodedata
from importlib.metadata import version
import numpy as np
import torch
from sacrebleu.metrics import BLEU,CHRF
from transformers import (NllbTokenizer,AutoModelForSeq2SeqLM,Seq2SeqTrainer,
    Seq2SeqTrainingArguments,DataCollatorForSeq2Seq,set_seed)
MODEL='facebook/nllb-200-distilled-600M'
REVISION='f8d333a098d19b4fd9a8b18f94170487ad3f821d'
SOURCE='kaz_Cyrl';TARGET='kir_Cyrl';SEED=42
MAX_INPUT=256;MAX_TARGET=255;GENERATION_LENGTH=256;BEAMS=4

def normalise(text):
    return ' '.join(unicodedata.normalize('NFC',text).split())

def load_splits(directory):
    """Require TSV header document_id/src/tgt; reject cross-split overlap.
    Document IDs must identify original source documents across ALL collections.
    """
    result={};hashes={};seen={kind:{} for kind in ('document','source','target')}
    for split in ('train','validation','test'):
        path=Path(directory)/f'{split}.tsv';rows=[];pairs=set()
        with path.open(encoding='utf-8',newline='') as f:
            reader=csv.DictReader(f,delimiter='\t')
            if reader.fieldnames!=['document_id','src','tgt']:raise ValueError(f'{path}: expected document_id, src, tgt header')
            for line,row in enumerate(reader,2):
                if None in row or any(v is None or not v.strip() for v in row.values()):raise ValueError(f'{path}:{line}: malformed/empty field')
                src,tgt=normalise(row['src']),normalise(row['tgt'])
                if (src,tgt) in pairs:raise ValueError(f'{path}:{line}: duplicate pair')
                pairs.add((src,tgt))
                for kind,key in [('document',row['document_id']),('source',src),('target',tgt)]:
                    previous=seen[kind].get(key)
                    if previous is not None and previous!=split:raise ValueError(f'{kind} overlap: {previous}/{split}, {path}:{line}')
                    seen[kind][key]=split
                rows.append(row)
        if not rows:raise ValueError(f'{path}: empty split')
        result[split]=rows;hashes[split]=hashlib.sha256(path.read_bytes()).hexdigest()
    return result,hashes

def check_languages(tokenizer):
    src_id=tokenizer.convert_tokens_to_ids(SOURCE);tgt_id=tokenizer.convert_tokens_to_ids(TARGET)
    if src_id==tgt_id or tokenizer.unk_token_id in (src_id,tgt_id):raise ValueError('missing or identical language tokens')
    source=tokenizer('Алматы')['input_ids'];target=tokenizer(text_target='Бишкек')['input_ids']
    if source[0]!=src_id or target[0]!=tgt_id or source[-1]!=tokenizer.eos_token_id or target[-1]!=tokenizer.eos_token_id:
        raise ValueError('source/target language prefix or EOS mismatch; check tokenizer class/revision')
    return src_id,tgt_id

def encode_rows(rows,tokenizer,max_input=MAX_INPUT,max_target=MAX_TARGET):
    out=[]
    for i,row in enumerate(rows):
        source=tokenizer(row['src'],truncation=False)
        target=tokenizer(text_target=row['tgt'],truncation=False)['input_ids']
        if len(source['input_ids'])>max_input or len(target)>max_target:
            raise ValueError(f'pair {i} exceeds token budget; align shorter segments before training, without changing held-out coverage')
        out.append({**source,'labels':target})
    return out

def decoded_ids(ids,tokenizer):
    ids=np.asarray(ids)
    if ids.ndim!=2:raise ValueError('expected generated token IDs')
    return tokenizer.batch_decode(np.where(ids==-100,tokenizer.pad_token_id,ids),skip_special_tokens=True)

def score_text(hypotheses,references):
    if not hypotheses or len(hypotheses)!=len(references):raise ValueError('empty or mismatched hypotheses/references')
    bleu=BLEU(tokenize='13a');chrf=CHRF(word_order=2)
    scores={'bleu':bleu.corpus_score(hypotheses,[references]).score,'chrfpp':chrf.corpus_score(hypotheses,[references]).score}
    signatures={'bleu':str(bleu.get_signature()),'chrfpp':str(chrf.get_signature())}
    return scores,signatures

def metrics_for(tokenizer,references):
    # Score ORIGINAL references, not their tokenizer-decoded reconstructions.
    def metrics(prediction):
        return score_text(decoded_ids(prediction.predictions,tokenizer),references)[0]
    return metrics

def generate_rows(model,tokenizer,rows,batch_size=4):
    model.eval();hypotheses=[];budget_hits=0
    for start in range(0,len(rows),batch_size):
        batch=tokenizer([r['src'] for r in rows[start:start+batch_size]],padding=True,truncation=False,return_tensors='pt').to(model.device)
        with torch.inference_mode():ids=model.generate(**batch)
        budget_hits+=sum(int((seq!=tokenizer.pad_token_id).sum())>=GENERATION_LENGTH for seq in ids)
        hypotheses.extend(tokenizer.batch_decode(ids,skip_special_tokens=True))
    return hypotheses,int(budget_hits)

def configure_generation(model,target_id):
    model.generation_config.forced_bos_token_id=target_id
    model.generation_config.max_length=GENERATION_LENGTH
    model.generation_config.max_new_tokens=None
    model.generation_config.num_beams=BEAMS
    model.generation_config.do_sample=False

def run(data_dir,output_dir):
    set_seed(SEED);out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    data,hashes=load_splits(data_dir)
    tokenizer=NllbTokenizer.from_pretrained(MODEL,revision=REVISION,src_lang=SOURCE,tgt_lang=TARGET,legacy_behaviour=False)
    source_id,target_id=check_languages(tokenizer)
    encoded={split:encode_rows(rows,tokenizer) for split,rows in data.items()}
    model=AutoModelForSeq2SeqLM.from_pretrained(MODEL,revision=REVISION)
    configure_generation(model,target_id)  # BEFORE baseline, development scoring and training
    args=Seq2SeqTrainingArguments(output_dir=str(out/'checkpoints'),num_train_epochs=3,
        per_device_train_batch_size=2,per_device_eval_batch_size=4,learning_rate=5e-5,
        eval_strategy='epoch',save_strategy='epoch',predict_with_generate=True,
        generation_max_length=GENERATION_LENGTH,generation_num_beams=BEAMS,
        load_best_model_at_end=True,metric_for_best_model='chrfpp',greater_is_better=True,
        seed=SEED,report_to='none')
    trainer=Seq2SeqTrainer(model=model,args=args,train_dataset=encoded['train'],eval_dataset=encoded['validation'],
        processing_class=tokenizer,data_collator=DataCollatorForSeq2Seq(tokenizer,model=model),
        compute_metrics=metrics_for(tokenizer,[r['tgt'] for r in data['validation']]))
    baseline_dev=trainer.evaluate(metric_key_prefix='baseline_dev')
    trainer.train();trainer.save_model(out/'best');tokenizer.save_pretrained(out/'best')
    fine_dev=trainer.evaluate(metric_key_prefix='selected_dev')
    # All choices are now fixed. Evaluate the two systems on the untouched test once.
    hypotheses,budget_hits=generate_rows(trainer.model,tokenizer,data['test'])
    references=[r['tgt'] for r in data['test']]
    fine_scores,signatures=score_text(hypotheses,references)
    (out/'finetuned-test.json').write_text(json.dumps(hypotheses,ensure_ascii=False,indent=2))
    # Release the trainer/optimiser before loading the baseline checkpoint again.
    device=trainer.model.device
    del trainer,model
    import gc
    gc.collect()
    if torch.cuda.is_available():torch.cuda.empty_cache()
    baseline=AutoModelForSeq2SeqLM.from_pretrained(MODEL,revision=REVISION).to(device)
    configure_generation(baseline,target_id)
    baseline_hypotheses,baseline_hits=generate_rows(baseline,tokenizer,data['test'])
    baseline_scores,_=score_text(baseline_hypotheses,references)
    (out/'baseline-test.json').write_text(json.dumps(baseline_hypotheses,ensure_ascii=False,indent=2))
    result={'model':MODEL,'revision':REVISION,'source':SOURCE,'target':TARGET,'seed':SEED,
        'data_sha256':hashes,'split_sizes':{k:len(v) for k,v in data.items()},
        'source_token_id':source_id,'target_token_id':target_id,'signatures':signatures,
        'baseline_dev':baseline_dev,'selected_dev':fine_dev,'baseline_test':baseline_scores,'finetuned_test':fine_scores,
        'generation':{'max_length':GENERATION_LENGTH,'beams':BEAMS,'do_sample':False},
        'test_outputs_reaching_length_budget':{'baseline':baseline_hits,'finetuned':budget_hits},
        'versions':{name:version(name) for name in ('transformers','torch','accelerate','sacrebleu','sentencepiece','numpy')},
        'device':str(device),'training_args':args.to_dict()}
    (out/'run-info.json').write_text(json.dumps(result,indent=2,default=str)+'\n')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('data_dir');parser.add_argument('--output',default='nllb-kaz-kir')
    args=parser.parse_args();print(json.dumps(run(args.data_dir,args.output),indent=2,default=str))
