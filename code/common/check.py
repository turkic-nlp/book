"""Deterministic fixture/tiny-model checks, not pretrained quality experiments."""
import argparse, importlib.metadata as md, json, math, tempfile, types
from pathlib import Path
import sys
for _d in ('ch04-corpus','ch11-speech','ch13-retrieval','ch15-tumlu','ch16-transfer','ch17-resources'):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / _d))
import numpy as np
import torch
from common import check_splits,wilson
from speech import Collator,validate_wave,errors,normalize
from corpus import reservoir,script_shares,fst_coverage,weighted_clean,uzbek_letter_apostrophes
from transfer import conversion_map,restore_span,bio_spans
from retrieval import align,top1
from tumlu import prepare,sequence_logprobs,summary,audit_rows
from resources import hub_count
ROOT=Path(__file__).resolve().parents[2]
checks=[]
def ok(name):checks.append(name)
def rejects(fn):
    try:fn()
    except (ValueError,KeyError):return
    raise AssertionError('expected rejection')

# Leakage and categorical errors are not masked as empty/zero results.
a={'id':'1','group_id':'a','text':'one','label':'x'}
b={'id':'2','group_id':'b','text':'two','label':'y'}
check_splits({'train':[a],'dev':[b]})
rejects(lambda:check_splits({'train':[a],'dev':[{**b,'group_id':'a'}]}))
rejects(lambda:check_splits({'train':[a],'dev':[{**b,'text':' one '}]}))
ok('split IDs/source groups/text leakage guards')
assert math.isclose(math.exp(math.log(4)),2**2)
assert math.isclose(2*7/(2*7+6),.7)
assert math.isclose(1-(1-.25)*(1-.30),.475)
assert math.isclose(math.sqrt(9)/(math.sqrt(9)+math.sqrt(1)),.75)
assert wilson(0,10)[0]==0 and wilson(10,10)[1]<=1
z=torch.tensor([1000.,1001.]);assert torch.isfinite(z.softmax(-1)).all()
assert math.isclose(3/(1-.25),4)
ok('entropy/perplexity, stable softmax, F1, pivot and sampling arithmetic')

sample,report=reservoir(({'id':i} for i in range(100)),10,42)
assert report['population_documents']==100 and len({x['id'] for x in sample})==10
assert sample==reservoir(({'id':i} for i in range(100)),10,42)[0]
assert script_shares('ә a 12')['shares']['CYRILLIC']==.5
assert script_shares('123')['shares']['LATIN'] is None
assert fst_coverage([],lambda x:[])['coverage'] is None
assert fst_coverage(['a','b'],lambda x:[('*unknown',0)] if x=='a' else [('b<n>',0)])['coverage']==.5
assert fst_coverage(['Weezy'],lambda x:[('Weezy<np><unk>',0)])['coverage']==0  # analyser guesses are not recognition
assert math.isclose(weighted_clean([{'population':90,'sample':10,'clean':9},{'population':10,'sample':10,'clean':1}]),.82)
assert uzbek_letter_apostrophes("o'g’ 'quote' ma’no")=="oʻgʻ 'quote' ma’no"
ok('full-stream sampling, denominators, script shares, FST unknowns and stratum weights')

source=[{'id':2,'split':'devtest','text':'s2'},{'id':1,'split':'devtest','text':'s1'}]
target=[{'id':1,'split':'devtest','text':'same'},{'id':2,'split':'devtest','text':'same'}]
x,y=align(source,target)
assert x[0]['id']==1
assert top1(x,y,[[1,0],[1,0]],[[1,0],[1,0]])['top1']==1
z=[{**y[0],'text':'one'},{**y[1],'text':'two'}]
assert top1(x,z,[[1,0],[1,0]],[[1,0],[1,0]])['top1']==.5
rejects(lambda:align(source,target[:1]))
rejects(lambda:align(source,target+target[:1]))
rejects(lambda:top1(x,y,[[0,0],[1,0]],[[1,0],[1,0]]))
ok('retrieval shuffled IDs, coverage, duplicates, ties and zero vectors')

converted,mapping=conversion_map('a щ b',lambda s:s.replace('щ','shch'))
assert converted=='a shch b' and restore_span((2,6,'LOC'),mapping)==(2,3,'LOC')
rejects(lambda:restore_span((3,6,'LOC'),mapping))
text='New York.'
assert bio_spans([{'start':0,'end':3,'text':'New','tag':'B-GPE'},{'start':4,'end':8,'text':'York','tag':'I-GPE'}],text)==[(0,8,'LOC')]
rejects(lambda:bio_spans([{'start':0,'end':3,'text':'New','tag':'I-GPE'}],text))
ok('BIO schema/spans and ambiguous conversion boundaries')

class FakeAPI:
    def list_models(self,*,filter):return [types.SimpleNamespace(id='same')]
    def list_datasets(self,*,language):return []
assert hub_count(FakeAPI(),'models',['kk','kaz'])['value']==1
assert hub_count(FakeAPI(),'datasets',['kk'])['value']==0
assert hub_count(FakeAPI(),'models',[])['value'] is None
import httpx
class Broken(FakeAPI):
    def list_models(self,*,filter):raise httpx.ConnectError('fixture network error')
assert hub_count(Broken(),'models',['kk'])['status']=='error'
ok('Hub filter signature; observed zero, unknown, error and ID deduplication')

assert errors(['a b',''],['a','x'])['raw_wer']==1
assert normalize('ҚАЗАҚ! OʻZBEK')=='қазақ oʻzbek'
assert errors([''],['x'])['raw_wer'] is None
rejects(lambda:validate_wave(np.zeros(480001),16000))
rejects(lambda:validate_wave(np.zeros((10,2)),16000))
rejects(lambda:validate_wave(np.zeros(10),8000))
rejects(lambda:validate_wave(np.array([np.nan]),16000))
ok('ASR duration/rate/channel guards and raw/normalised error arithmetic')

item=prepare({'question':'Question','choices':['a','b'],'answer':'B','subject':'test','CoT':'SECRET GOLD EXPLANATION'})
assert item['gold']==1 and 'SECRET' not in item['prompt']
logits=torch.tensor([[[0.,1.,2.],[3.,2.,1.]],[[1.,0.,0.],[0.,2.,1.]]])
labels=torch.tensor([[2,-100],[0,1]])
scores=sequence_logprobs(logits,labels)
assert torch.allclose(scores,torch.stack([logits[0,0].log_softmax(-1)[2],logits[1,0].log_softmax(-1)[0]+logits[1,1].log_softmax(-1)[1]]))
assert summary([{'gold':0,'prediction':0,'n_choices':2},{'gold':0,'prediction':1,'n_choices':4}])['uniform_random_expectation']==.375
ok('TUMLU schema/gold isolation, padding/EOS-compatible sum scoring and analytic chance')

# Tiny real architectures: execute loss/backprop and save/reload, without weights downloads.
from transformers import (WhisperConfig,WhisperForConditionalGeneration,T5Config,T5ForConditionalGeneration,
                         XLMRobertaConfig,XLMRobertaForSequenceClassification,WhisperProcessor)
from peft import LoraConfig,TaskType,get_peft_model,PeftModel
from transformers import set_seed
set_seed(42);torch.set_num_threads(1)
cfg=XLMRobertaConfig(vocab_size=50,hidden_size=16,num_hidden_layers=1,num_attention_heads=2,intermediate_size=32,num_labels=3)
base=XLMRobertaForSequenceClassification(cfg)
with tempfile.TemporaryDirectory() as directory:
    directory=Path(directory);base.save_pretrained(directory/'base')
    model=get_peft_model(base,LoraConfig(task_type=TaskType.SEQ_CLS,r=2,lora_alpha=4,
        target_modules=['query','value'],modules_to_save=['classifier'],lora_dropout=0))
    batch={'input_ids':torch.tensor([[0,5,6,2],[0,7,8,2],[0,9,10,2]]),'attention_mask':torch.ones(3,4,dtype=torch.long),'labels':torch.tensor([0,1,2])}
    loss=model(**batch).loss;loss.backward()
    assert torch.isfinite(loss)
    assert any('lora_' in n and p.grad is not None and p.grad.abs().sum()>0 for n,p in model.named_parameters())
    assert any('classifier' in n and p.grad is not None and p.grad.abs().sum()>0 for n,p in model.named_parameters())
    torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=.01).step()
    model.eval();expected=model(**batch).logits.detach();model.save_pretrained(directory/'adapter')
    restored=PeftModel.from_pretrained(XLMRobertaForSequenceClassification.from_pretrained(directory/'base'),directory/'adapter').eval()
    torch.testing.assert_close(expected,restored(**batch).logits)
    # Vocabulary extension: old IDs/rows stable, resized rows receive gradients and reload.
    extension=T5ForConditionalGeneration(T5Config(vocab_size=20,d_model=16,d_ff=32,num_layers=1,num_decoder_layers=1,num_heads=2,decoder_start_token_id=0,pad_token_id=0,eos_token_id=1))
    old=extension.shared.weight.detach().clone();extension.resize_token_embeddings(22,mean_resizing=False)
    torch.testing.assert_close(old,extension.shared.weight[:20])
    assert extension.shared.weight.data_ptr()==extension.lm_head.weight.data_ptr()
    out=extension(input_ids=torch.tensor([[20,3,1]]),labels=torch.tensor([[21,1]]));out.loss.backward()
    assert extension.shared.weight.grad[20:].abs().sum()>0
    extension.eval();extension.save_pretrained(directory/'extended')
    reload=T5ForConditionalGeneration.from_pretrained(directory/'extended').eval()
    torch.testing.assert_close(extension(input_ids=torch.tensor([[20,3,1]]),labels=torch.tensor([[21,1]])).logits,
                               reload(input_ids=torch.tensor([[20,3,1]]),labels=torch.tensor([[21,1]])).logits)
ok('tiny XLM-R LoRA classifier gradients/step/adapter reload; tied embedding resize/gradient/reload')

p=argparse.ArgumentParser();p.add_argument('--sources',type=Path);a=p.parse_args()
if a.sources:
    proc=WhisperProcessor.from_pretrained(a.sources/'whisper',language='kazakh',task='transcribe')
    features=proc.feature_extractor(np.zeros(16000,dtype=np.float32),sampling_rate=16000,return_attention_mask=True)
    start=proc.tokenizer.convert_tokens_to_ids('<|startoftranscript|>')
    config=WhisperConfig(vocab_size=len(proc.tokenizer),num_mel_bins=80,d_model=16,
        encoder_layers=1,decoder_layers=1,encoder_attention_heads=2,decoder_attention_heads=2,
        encoder_ffn_dim=32,decoder_ffn_dim=32,max_source_positions=10,max_target_positions=32,
        decoder_start_token_id=start,pad_token_id=proc.tokenizer.pad_token_id,eos_token_id=proc.tokenizer.eos_token_id,
        suppress_tokens=[],begin_suppress_tokens=[])
    speech=WhisperForConditionalGeneration(config)
    data=[{'input_features':features.input_features[0][:,:20].tolist(),
        'attention_mask':features.attention_mask[0][:20].tolist(),'labels':proc.tokenizer(t).input_ids} for t in ['Сәлем.','Қазақ тілі.']]
    batch=Collator(proc,start)(data)
    assert not batch['labels'][:,0].eq(start).any() and batch['labels'].eq(-100).any()
    loss=speech(**batch).loss;loss.backward();assert torch.isfinite(loss)
    bad=[{**data[0],'labels':data[0]['labels'][1:]}]
    rejects(lambda:Collator(proc,start)(bad))
    ok('real pinned Whisper processor + tiny Whisper collator/forward/backward')
    import pyarrow.parquet as pq
    records={};invalid=[];released_counts={}
    for split in ('dev','test'):
        files=sorted((a.sources/'tumlu/kazakh').glob(f'{split}*.parquet'))
        if not files:raise ValueError('missing downloaded TUMLU Kazakh split')
        raw=[row for file in files for row in pq.read_table(file).to_pylist()]
        released_counts[split]=len(raw)
        records[split],bad=audit_rows(raw,split);invalid.extend(bad)
        assert len({r['id'] for r in records[split]})==len(records[split])
    assert not {r['id'] for r in records['dev']} & {r['id'] for r in records['test']}
    audit={'dataset':'jafarisbarov/TUMLU-mini','revision':'3523de73e1d1d784118d328f40b49d53afd6f334',
        'config':'kazakh','counts':{s:len(rs) for s,rs in records.items()},'duplicate_questions':0,'dev_test_overlap':0,
        'choice_counts':sorted({len(r['candidates']) for rs in records.values() for r in rs}),
        'released_counts':released_counts,'invalid_rows':invalid,
        'gold_explanations_used':False,'inference_run':False}
    (ROOT/'experiments/remaining_revision/tumlu-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    ok('all pinned TUMLU Kazakh rows schema/choices/duplicate/split audit')

env={'python':__import__('sys').version,'packages':{n:md.version(n) for n in ['torch','transformers','peft','datasets','accelerate','soundfile','numpy','huggingface-hub','scikit-learn','pyarrow']}}
(ROOT/'experiments/remaining_revision/environment.json').write_text(json.dumps(env,indent=2)+'\n')
result={'date':'2026-10-15','checks':checks,'n_check_groups':len(checks),'pretrained_training_run':False,'quality_claims':False}
(ROOT/'experiments/remaining_revision/mechanical-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
