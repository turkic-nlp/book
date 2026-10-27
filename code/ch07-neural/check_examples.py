"""Offline mechanical checks, with a tiny random BERT and hand-built fixtures.
No tagging accuracy or expert linguistic validation is claimed.
"""
import hashlib, json, platform, tempfile
from pathlib import Path
import sentencepiece as spm
import torch, transformers
from transformers import (BertConfig, BertForTokenClassification, BertTokenizerFast,
                          Trainer, TrainingArguments, DataCollatorForTokenClassification)
import accelerate
from morph_tagging import *
from boundary_tokenizer import *

def raises(fn):
    try: fn()
    except (ValueError,KeyError): return
    raise AssertionError('Expected failure')

with tempfile.TemporaryDirectory() as td:
    root=Path(td)
    vocab=['[PAD]','[UNK]','[CLS]','[SEP]','[MASK]','ev','##ler','geldi','.']
    (root/'vocab.txt').write_text('\n'.join(vocab)+'\n')
    tok=BertTokenizerFast(vocab_file=str(root/'vocab.txt'),do_lower_case=False)
    # Transformers 5 supports the explicit vocab argument; 4 uses vocab_file.
    if len(tok)!=len(vocab): tok=BertTokenizerFast(vocab=str(root/'vocab.txt'),do_lower_case=False)
    assert len(tok)==len(vocab),len(tok)
    words=['evler','geldi','.']*5; labels=['NOUN|Number=Plur','VERB|Tense=Past','PUNCT']*5
    l2i={x:i for i,x in enumerate(sorted(set(labels)))};i2l={i:x for x,i in l2i.items()}
    rows=training_rows([words],[labels],tok,l2i,8)
    assert sum(sum(x!=-100 for x in r['labels']) for r in rows)==len(words)
    assert len(rows)>1 and all(len(r['input_ids'])<=8 for r in rows)
    assert all(r['labels'][0]==r['labels'][-1]==-100 for r in rows)
    assert canonical_label('NOUN','Person=3|Number=Plur')=='NOUN|Number=Plur|Person=3'
    assert canonical_label('PUNCT','_')=='PUNCT'
    torch.manual_seed(13)
    model=BertForTokenClassification(BertConfig(vocab_size=len(tok),hidden_size=16,num_hidden_layers=1,
        num_attention_heads=2,intermediate_size=32,max_position_embeddings=16,num_labels=len(l2i)))
    batch={k:torch.tensor([v]) for k,v in rows[0].items()}
    model.train(); loss=model(**batch).loss;assert torch.isfinite(loss);loss.backward()
    opt=torch.optim.AdamW(model.parameters(),lr=1e-4);opt.step();opt.zero_grad()
    # Exercise the actual Trainer interface used by the chapter as well.
    trainer=Trainer(model=model,train_dataset=rows,processing_class=tok,
        data_collator=DataCollatorForTokenClassification(tok),
        args=TrainingArguments(output_dir=str(root/'trainer'),max_steps=1,
            per_device_train_batch_size=2,use_cpu=True,eval_strategy='no',
            save_strategy='no',report_to='none',disable_tqdm=True))
    trained=trainer.train()
    assert trained.global_step==1
    trainer.save_model(str(root/'saved'));tok.save_pretrained(root/'saved')
    restored=BertForTokenClassification.from_pretrained(root/'saved')
    assert len(predict_words(words,restored,tok,i2l,8))==len(words)
    pred=predict_words(words,model,tok,i2l,8);assert len(pred)==len(words)
    metrics=score_predictions([[labels[0],labels[0]]],[[labels[0],'NOUN|Case=Alien']],l2i)
    assert metrics['accuracy']==0.5 and metrics['unseen_rate']==0.5
    raises(lambda:score_predictions([[]],[labels],l2i))
    raises(lambda:score_predictions([],[],l2i))
    raises(lambda:list(word_chunks([''],tok,8)))
    raises(lambda:list(word_chunks(['evler'],tok,3)))
    sample='# sent_id = fixture\n1-2\tevler\t_\t_\t_\t_\t_\t_\t_\t_\n1\tev\tev\tNOUN\t_\tNumber=Plur\t0\troot\t_\t_\n2\tgeldi\tgel\tVERB\t_\tTense=Past\t1\tdep\t_\t_\n2.1\tx\t_\tX\t_\t_\t_\t_\t_\t_\n\n'
    (root/'source.conllu').write_text(sample)
    ws,gs=load_conllu(root/'source.conllu');assert len(ws[0])==2
    export_conllu(root/'source.conllu',[['PROPN','AUX|Tense=Past']],root/'pred.conllu')
    out=(root/'pred.conllu').read_text();assert '1-2\tevler' in out and '2.1\tx' in out and '# sent_id' in out
    assert load_conllu(root/'pred.conllu')[1]==[['PROPN','AUX|Tense=Past']]
    raises(lambda:export_conllu(root/'source.conllu',[['PROPN']],root/'bad.conllu'))
    fixtures={'evlerimizden':['ev','ler','imiz','den'],'мектептер':['мектеп','тер']}
    segment=lambda word:fixtures.get(word,[word])
    corpus='evlerimizden мектептер evlerimizden мектептер'
    (root/'seg.txt').write_text('\n'.join(training_lines(corpus,segment))+'\n')
    spm.SentencePieceTrainer.train(input=str(root/'seg.txt'),model_prefix=str(root/'m'),vocab_size=320,
        hard_vocab_limit=False,model_type='unigram',user_defined_symbols=[BOUNDARY],byte_fallback=True,
        normalization_rule_name='identity',remove_extra_whitespaces=False,add_dummy_prefix=False,
        character_coverage=1.0,minloglevel=2)
    sp=spm.SentencePieceProcessor(model_file=str(root/'m.model'))
    for text in ['',corpus,'  evlerimizden\tмектептер\n🙂 Ω e\u0301  ']:
        encoded=encode_text(text,sp,segment);assert decode_text(encoded,sp)==text
    raises(lambda:encode_text('a│b',sp,segment));raises(lambda:encode_text('a▁b',sp,segment))
    raises(lambda:encode_text('ev',sp,lambda _:['EV']))
result={'date':'2026-10-14','python':platform.python_version(),'torch':torch.__version__,
    'transformers':transformers.__version__,'sentencepiece':spm.__version__,'accelerate':accelerate.__version__,
    'checks':['whole-word overflow chunks preserve every label','first-piece loss masks',
    'tiny random BERT forward/backward/optimizer and chunked inference','Trainer one-step run and checkpoint reload','unseen bundles count in accuracy',
    'length and empty-set rejection','canonical feature ordering','CoNLL-U structure preserved',
    'SentencePiece ID round-trip with bytes and whitespace sidecar','reserved-marker and surface-change rejection'],
    'scope':'Mechanical tests with synthetic fixtures; no pretrained-model fine-tuning or measured linguistic accuracy.',
    'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}}
Path(__file__).with_name('checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
