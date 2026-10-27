"""Analytic metric checks and independent rescoring of saved predictions.
Run after the empirical suite; source data are read-only.
"""
from common import *
from collections import defaultdict
import argparse,math
from run_bitext import score_pair
from run_retrieval import metrics,bm25,tokenise
from run_tumlu import prepare
from stanza.models.ner.utils import bio2_to_bioes,decode_from_bioes

def imst_restored(path,manifest):
  """Distributed Turkish predictions omit IMST text (CC BY-NC-SA); run `imst_text.py restore` first."""
  info=json.loads((path.parent/manifest).read_text())['runs']['tr']['imst_text_redaction'];assert sha(path)==info['redacted_sha256']
  r=path.with_suffix('.restored.conllu');assert r.exists(),'Run: python imst_text.py restore --gold UD_ROOT/UD_Turkish-IMST/tr_imst-ud-test.conllu';assert sha(r)==info['restored_sha256'];return r
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--ud-scorer',type=Path);ap.add_argument('--archive',type=Path,required=True);ap.add_argument('--ner-gold',type=Path,required=True);ap.add_argument('--ud-root',type=Path,required=True);ap.add_argument('--model-root',type=Path,required=True);a=ap.parse_args();out=Path(__file__).parent/'results';checks=[];jsonout(out/'validation.json',{'passed':False,'status':'validation in progress; a failure must not leave stale success'})
 r=metrics(np.array([[1.,1.,0.]]),[0])[0];assert r['top1']==.5 and r['mrr10']==.75 and np.isclose(r['ndcg10'],(1+1/math.log2(3))/2);z=metrics(np.zeros((1,488)),[487])[0];assert np.isclose(z['top1'],1/488) and np.isclose(z['recall100'],100/488)
 credit,_,_=score_pair(np.eye(2),np.eye(2)[::-1],['a','b']);assert np.array_equal(credit,[0,0]);credit,_,_=score_pair(np.eye(2),np.eye(2)[::-1],['a','a']);assert np.array_equal(credit,[1,1]);checks.append('Analytic ties, no-overlap chance, shuffled alignment and duplicate-target credit')
 assert tokenise('I İ','tur_Latn')==['ı','i'];s=bm25(['red blue','green'],['red'],'eng_Latn');assert s[0,0]>s[0,1];checks.append('BM25 term matching and Turkish case handling')
 x={'choices':['a','b','c','d'],'question':'Question','answer':'A','subject':'test'};y=dict(x,answer='D',cot='the gold answer is D');assert prepare(x,0)['prompt']==prepare(y,0)['prompt'];checks.append('Changing gold answer/explanation cannot change TUMLU input')
 for file,nconditions,nqueries,keys in [('bitext_items.csv',312,1012,['model','src','tgt']),('retrieval_items.csv',77,900,['run','src','tgt','condition'])]:
  groups=defaultdict(list)
  with (out/file).open() as f:
   for r in csv.DictReader(f):groups[tuple(r[k] for k in keys)].append(r)
  assert len(groups)==nconditions and all(len(v)==nqueries for v in groups.values())
  summaries=list(csv.DictReader((out/file.replace('items','summary')).open()))
  for r in summaries:
   group=groups[tuple(r[k] for k in keys)]
   fields={'top1_accuracy':'top1_credit'} if file.startswith('bitext') else {k:k for k in ['top1','mrr10','ndcg10','recall10','recall100']}
   for field,item in fields.items():assert np.isclose(float(r[field]),np.mean([float(x[item]) for x in group]),atol=1e-12)
  checks.append(f'{file}: every condition has its full denominator and rescored means match')
 # Independent entity decoding provided by Stanza, not the experiment span parser.
 gold=[[line.rsplit(None,1)[1] for line in b.splitlines()] for b in a.ner_gold.read_text().strip().split('\n\n') if b.strip()];pred=[json.loads(s) for s in (out/'ner_predictions.jsonl').read_text().splitlines()];assert len(gold)==len(pred)==11307;counts=np.zeros(3,dtype=int)
 for g,p in zip(gold,pred):
  def decode(tags):return {(x['start'],x['end'],x['type']) for x in decode_from_bioes(tags)}
  gs=decode(bio2_to_bioes(g));ps=decode(p['predicted_tags']);counts+=[len(gs),len(ps),len(gs&ps)]
 overall=list(csv.DictReader((out/'ner_summary.csv').open()))[0];assert list(counts)==[int(overall[k]) for k in ['gold_entities','predicted_entities','correct_entities']];checks.append('KazNERD exact entity counts independently match Stanza decoder')
 resources=json.loads((a.model_root/'resources.json').read_text());verified=[]
 for lang,package,kind in [('kk','ktb','charlm'),('ky','ktmu','nocharlm'),('tr','imst','charlm'),('ug','udt','nocharlm')]:
  for proc,name in [('tokenize',package),('pos',package+'_'+kind),('depparse',package+'_'+kind),('lemma',package+'_nocharlm')]+([('mwt',package)] if lang in ['kk','tr'] else [])+([('ner','kazNERD')] if lang=='kk' else []):
   p=a.model_root/lang/proc/(name+'.pt');assert hashlib.md5(p.read_bytes()).hexdigest()==resources[lang][proc][name]['md5'];verified.append(str(p.relative_to(a.model_root)))
 checks.append('Cached task checkpoints match declared Stanza resource MD5s')
 # Gold-segmented LAS recomputed directly, with UD scorer's coarse-relation convention.
 for lang,tree in [('kk','Kazakh-KTB'),('ky','Kyrgyz-KTMU'),('tr','Turkish-IMST'),('ug','Uyghur-UDT')]:
  def rows(path):return [s.split('\t') for s in path.read_text().splitlines() if s and not s.startswith('#') and s.split('\t')[0].isdigit()]
  g=rows(next((a.ud_root/f'UD_{tree}').glob('*-ud-test.conllu')));p=rows(imst_restored(out/f'{lang}-ud217-predicted.conllu','parsing_manifest.json') if lang=='tr' else out/f'{lang}-ud217-predicted.conllu');assert len(g)==len(p)
  matched=sum(x[6]==y[6] and x[7].split(':')[0]==y[7].split(':')[0] for x,y in zip(g,p));r=next(x for x in csv.DictReader((out/'parsing_summary.csv').open()) if x['language']==lang and x['metric']=='LAS');assert matched==int(r['correct']) and len(g)==int(r['gold_total'])
 checks.append('Direct coarse LAS counts match official scorer on all four gold-segmented tests')
 t=json.loads((out/'tumlu_summary.json').read_text());p=[json.loads(s) for s in (out/'tumlu_predictions.jsonl').read_text().splitlines()];assert len(p)==797 and len({x['id'] for x in p})==797
 assert sum(x['prediction']==x['gold'] for x in p)==t['overall']['correct']==226
 assert all(x['prediction']=='ABCD'[int(np.argmax(x['candidate_logprobs']))] for x in p);assert sum(x['gold']=='D' for x in p)==t['dev_majority_baseline']['test']['correct']==304;checks.append('TUMLU labels rescore to 226/797; dev-majority baseline to 304/797; two exclusions retained')
 if a.ud_scorer:
  import importlib.util
  expected=json.loads((out/'parsing_manifest.json').read_text())['scorer']['sha256'];assert sha(a.ud_scorer)==expected,'Use the exact scorer recorded by the inference run'
  spec=importlib.util.spec_from_file_location('empirical_ud_scorer',a.ud_scorer);scorer=importlib.util.module_from_spec(spec);spec.loader.exec_module(scorer);load_conllu_file=scorer.load_conllu_file;evaluate=scorer.evaluate
 else:
  from stanza.utils.conll18_ud_eval import load_conllu_file,evaluate
 auto=list(csv.DictReader((out/'parsing_auto_summary.csv').open()));am=json.loads((out/'parsing_auto_manifest.json').read_text());assert len(auto)==36 and len(am['runs'])==4
 for lang,tree in [('kk','Kazakh-KTB'),('ky','Kyrgyz-KTMU'),('tr','Turkish-IMST'),('ug','Uyghur-UDT')]:
  gold=next((a.ud_root/f'UD_{tree}').glob('*-ud-test.conllu'));pred=out/f'{lang}-ud217-auto-predicted.conllu';assert sha(gold)==am['runs'][lang]['gold_sha256']
  if lang=='tr':pred=imst_restored(pred,'parsing_auto_manifest.json')  # IMST text redacted for licensing; see imst_text.py
  else:assert sha(pred)==am['runs'][lang]['predicted_sha256']
  scores=evaluate(load_conllu_file(str(gold)),load_conllu_file(str(pred)))
  for row in [x for x in auto if x['language']==lang and not (lang=='tr' and x['metric'] in ('Lemmas','BLEX'))]:
   m=scores[row['metric']];assert np.isclose(m.f1,float(row['f1']),atol=1e-12);assert m.correct==int(row['correct']) and m.gold_total==int(row['gold_total']) and m.system_total==int(row['system_total'])
 checks.append('All four automatic-tokenization tests rescore with identical official UD alignment and denominators')
 audit=json.loads((out/'stanza_split_audit.json').read_text());assert [x['language'] for x in audit['runs'] if x['standard_preparation_swaps_train_test']]==['kk'];assert all('not held-out' in x['evaluation_scope'] for x in auto if x['language']=='kk');checks.append('Kazakh split-swap exposure is explicit; no held-out interpretation attached')
 from sacrebleu.metrics import BLEU,CHRF
 texts,_=flores(a.archive);mt=list(csv.DictReader((out/'translation_summary.csv').open()));mm=json.loads((out/'translation_manifest.json').read_text());assert len(mt)==2
 for row in mt:
  src,tgt=row['src'],row['tgt'];p=out/f'mt-{src}-{tgt}.jsonl';items=[json.loads(x) for x in p.read_text().splitlines()];assert len(items)==1012 and [x['row_id'] for x in items]==list(range(1,1013));assert sha(p)==mm['runs'][f'{src}->{tgt}']['predictions_sha256'];hyp=[x['output'] for x in items]
  for key,metric in [('bleu',BLEU(tokenize='13a')),('chrf',CHRF(char_order=6,word_order=0,beta=2)),('chrfpp',CHRF(char_order=6,word_order=2,beta=2))]:
   assert np.isclose(metric.corpus_score(hyp,[texts[tgt]]).score,float(row[key]),atol=1e-10);assert str(metric.get_signature())==mm['runs'][f'{src}->{tgt}']['metric_signatures'][key]
  assert sum(not x['ended_with_eos'] for x in items)==int(row['outputs_without_eos']);assert sum(not x.strip() for x in hyp)==int(row['empty_outputs']);assert max(x['source_tokens'] for x in items)<=512
 checks.append('Both complete MT directions rescore exactly with saved signatures and EOS/empty-output audits')
 from run_word_lengths import stats
 length_rows=list(csv.DictReader((out/'word_length_items.csv').open()));assert len(length_rows)==13*1012
 for row in length_rows:
  observed=stats(texts[row['lang']][int(row['row_id'])-1])
  for key,value in observed.items():assert np.isclose(value,float(row[key]),atol=1e-12)
 probe=json.loads((out.parent/'inputs/uzbek-script-probe.json').read_text());rm=json.loads((out/'retrieval_manifest.json').read_text());assert len(probe)==900 and sha(out.parent/'inputs/uzbek-script-probe.json')==rm['script_probe_sha256']
 checks.append('All 13,156 orthographic-length rows independently recompute; frozen script-query hash matches')

 jsonout(out/'validation.json',{'checks':checks,'verified_stanza_checkpoints':verified,'passed':True,'scope':'Empirical mechanics, saved predictions, complete denominators and checkpoint integrity; not human validation or a contamination audit'});print('\n'.join(checks))
if __name__=='__main__':main()
