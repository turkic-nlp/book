"""Short-utterance Whisper training on pinned Kazakh FLEURS.
No audio is truncated to fit its full transcript. Long examples require a separate
aligned segmentation protocol; this runner fails rather than changing the task.
"""
import argparse, io, json, unicodedata
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'common'))  # code/common/common.py
from common import canonical, digest
MODEL='openai/whisper-small'
REVISION='973afd24965f72e36ca33b3055d56a652f456b4d'
DATA_REVISION='70bb2e84b976b7e960aa89f1c648e09c59f894dd'

def validate_wave(wave, sr):
    import numpy as np
    wave=np.asarray(wave)
    if sr!=16000 or wave.ndim!=1 or not len(wave) or not np.isfinite(wave).all():
        raise ValueError('require finite, nonempty, mono 16 kHz audio')
    if len(wave)>30*sr: raise ValueError('audio exceeds 30 s: align and segment before training')
    return wave

def normalize(text):
    # Conservative scoring: preserve letters, diacritics and apostrophes.
    text=unicodedata.normalize('NFC',text).lower()
    return ' '.join(''.join(c if not unicodedata.category(c).startswith('P') or c in "'ʻʼ’" else ' ' for c in text).split())

def distance(a,b):
    row=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        nxt=[i]
        for j,y in enumerate(b,1): nxt.append(min(nxt[-1]+1,row[j]+1,row[j-1]+(x!=y)))
        row=nxt
    return row[-1]

def errors(refs,hyps):
    if len(refs)!=len(hyps) or not refs: raise ValueError('unaligned/empty references')
    result={}
    for name,fn in [('raw',lambda x:x),('normalized',normalize)]:
        pairs=[(fn(r),fn(h)) for r,h in zip(refs,hyps)]
        for unit,split in [('wer',str.split),('cer',list)]:
            denom=sum(len(split(r)) for r,h in pairs)
            edits=sum(distance(split(r),split(h)) for r,h in pairs)
            result[f'{name}_{unit}']=edits/denom if denom else None
        result[f'{name}_empty_references']=sum(not r for r,h in pairs)
    return result

class Collator:
    def __init__(self,processor,start): self.processor=processor; self.start=start
    def __call__(self,features):
        import torch
        batch={'input_features':torch.tensor([f['input_features'] for f in features]),
               'attention_mask':torch.tensor([f['attention_mask'] for f in features])}
        labels=self.processor.tokenizer.pad([{'input_ids':f['labels']} for f in features],return_tensors='pt')
        ids=labels.input_ids.masked_fill(labels.attention_mask.eq(0),-100)
        if not ids[:,0].eq(self.start).all(): raise ValueError('inconsistent Whisper decoder-start prefix')
        # The model shifts labels right and inserts decoder_start_token_id itself.
        batch['labels']=ids[:,1:]
        return batch

def main():
    import numpy as np, soundfile as sf
    from datasets import load_dataset, Audio, Dataset
    from transformers import WhisperProcessor, WhisperForConditionalGeneration, Seq2SeqTrainer, Seq2SeqTrainingArguments, set_seed
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--epochs',type=float,default=3)
    p.add_argument('--seed',type=int,default=42);a=p.parse_args();set_seed(a.seed)
    ds=load_dataset('google/fleurs','kk_kz',revision=DATA_REVISION).cast_column('audio',Audio(decode=False))
    proc=WhisperProcessor.from_pretrained(MODEL,revision=REVISION,language='kazakh',task='transcribe')
    model=WhisperForConditionalGeneration.from_pretrained(MODEL,revision=REVISION)
    model.generation_config.language='kazakh';model.generation_config.task='transcribe'
    model.generation_config.forced_decoder_ids=None
    data={};refs={};ids={};hours={};seen_ids={};seen_prompts={};seen_prompt_ids={}
    for split in ('train','validation','test'):
        features=[];refs[split]=[];ids[split]=[];samples=0
        for row in ds[split]:
            item_id=str(row['path']);prompt=canonical(row['raw_transcription'])
            if not prompt: raise ValueError('empty training/evaluation transcript')
            if item_id in seen_ids: raise ValueError('duplicate recording path')
            seen_ids[item_id]=split
            prompt_id=str(row['id'])
            if seen_prompt_ids.setdefault(prompt_id,split)!=split:
                raise ValueError('prompt ID overlap across official splits; investigate before evaluation')
            other=seen_prompts.setdefault(prompt,split)
            if other!=split: raise ValueError('transcript overlap across official splits; investigate before evaluation')
            audio=row['audio'];source=io.BytesIO(audio['bytes']) if audio.get('bytes') is not None else audio['path']
            wave,sr=sf.read(source,dtype='float32');wave=validate_wave(wave,sr)
            inputs=proc.feature_extractor(wave,sampling_rate=sr,return_attention_mask=True)
            labels=proc.tokenizer(prompt).input_ids
            if len(labels)-1>model.config.max_target_positions: raise ValueError('overlength transcript')
            features.append({'input_features':inputs.input_features[0].tolist(),
                'attention_mask':inputs.attention_mask[0].tolist(),'labels':labels})
            refs[split].append(row['raw_transcription']);ids[split].append(item_id);samples+=len(wave)
        data[split]=Dataset.from_list(features);hours[split]=samples/16000/3600
    current_refs=refs['validation']
    def metrics(pred):
        hyp=proc.tokenizer.batch_decode(np.where(pred.predictions==-100,proc.tokenizer.pad_token_id,pred.predictions),skip_special_tokens=True)
        return errors(current_refs,hyp)
    args=Seq2SeqTrainingArguments(output_dir=str(a.output/'checkpoints'),num_train_epochs=a.epochs,
        per_device_train_batch_size=2,per_device_eval_batch_size=2,learning_rate=1e-5,
        predict_with_generate=True,generation_max_length=model.config.max_target_positions,
        eval_strategy='epoch',save_strategy='epoch',load_best_model_at_end=True,
        metric_for_best_model='normalized_wer',greater_is_better=False,
        remove_unused_columns=False,save_total_limit=1,report_to='none',seed=a.seed)
    trainer=Seq2SeqTrainer(model=model,args=args,train_dataset=data['train'],eval_dataset=data['validation'],
        data_collator=Collator(proc,model.config.decoder_start_token_id),processing_class=proc,compute_metrics=metrics)
    baseline_dev=trainer.evaluate()
    trainer.train();trainer.save_model(a.output/'model');proc.save_pretrained(a.output/'model')
    # Fixed test protocol: checkpoint selection used validation only.
    current_refs=refs['test'];fine=trainer.predict(data['test'])
    base_model=WhisperForConditionalGeneration.from_pretrained(MODEL,revision=REVISION)
    base_model.generation_config.language='kazakh';base_model.generation_config.task='transcribe'
    base_model.generation_config.forced_decoder_ids=None
    baseline_trainer=Seq2SeqTrainer(model=base_model,args=args,
        data_collator=Collator(proc,base_model.config.decoder_start_token_id),
        processing_class=proc,compute_metrics=metrics)
    baseline=baseline_trainer.predict(data['test'])
    a.output.mkdir(parents=True,exist_ok=True)
    report={'model':MODEL,'revision':REVISION,'data_revision':DATA_REVISION,'seed':a.seed,
        'hours':hours,'counts':{s:len(v) for s,v in refs.items()},'id_hashes':{s:digest(v) for s,v in ids.items()},
        'baseline_dev':baseline_dev,'baseline_test':baseline.metrics,'adapted_test':fine.metrics,
        'speaker_check':'FLEURS card split guarantee; no speaker IDs exposed in loaded schema'}
    (a.output/'run.json').write_text(json.dumps(report,indent=2)+'\n')
    for name,result in [('baseline',baseline),('adapted',fine)]:
        # Trainer pads predictions across batches with -100, which is not a token ID.
        hypotheses=proc.tokenizer.batch_decode(np.where(result.predictions==-100,proc.tokenizer.pad_token_id,result.predictions),skip_special_tokens=True)
        (a.output/f'{name}.jsonl').write_text(''.join(json.dumps({'id':i,'reference':r,'hypothesis':h},ensure_ascii=False)+'\n' for i,r,h in zip(ids['test'],refs['test'],hypotheses)))
if __name__=='__main__':main()
