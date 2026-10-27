"""Check published split sizes against Stanza's small-training-set swap rule.
This flags exposure risk; historical checkpoint training membership is not reconstructed.
"""
from pathlib import Path
import argparse,json,hashlib,inspect
import stanza,torch
from stanza.utils.datasets import prepare_tokenizer_treebank as prep
from stanza.utils.datasets import common
p=argparse.ArgumentParser();p.add_argument('--ud-root',type=Path,required=True);p.add_argument('--model-root',type=Path,required=True);a=p.parse_args();rows=[]
for lang,tree,package in [('kk','Kazakh-KTB','ktb_charlm'),('ky','Kyrgyz-KTMU','ktmu_nocharlm'),('tr','Turkish-IMST','imst_charlm'),('ug','Uyghur-UDT','udt_nocharlm')]:
 root=a.ud_root/f'UD_{tree}';train=next(root.glob('*-ud-train.conllu'));test=next(root.glob('*-ud-test.conllu'));nt=common.num_words_in_file(str(train));ne=common.num_words_in_file(str(test));dev=bool(list(root.glob('*-ud-dev.conllu')));risk=not dev and nt<=1000 and ne>5000
 checkpoint=torch.load(a.model_root/lang/'depparse'/(package+'.pt'),map_location='cpu',weights_only=False);config=checkpoint['config'];rows.append({'language':lang,'treebank':tree,'training_words_as_counted_by_stanza':nt,'test_words_as_counted_by_stanza':ne,'has_official_dev':dev,'standard_preparation_swaps_train_test':risk,'checkpoint_train_basename':Path(config['train_file']).name,'checkpoint_dev_basename':Path(config['eval_file']).name,'interpretation':'Replay/exposure-risk diagnostic, not held-out accuracy' if risk else 'Official test evaluation; historical training membership not independently audited'})
source=Path(prep.__file__);result={'stanza_version':stanza.__version__,'preparation_module':'stanza.utils.datasets.prepare_tokenizer_treebank','function':'process_partial_ud_treebank','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_url':'https://github.com/stanfordnlp/stanza/blob/v1.11.0/stanza/utils/datasets/prepare_tokenizer_treebank.py','rule':'For a treebank lacking dev, swap train/test when train <=1000 words and test >5000; split the new training file for dev.','historical_checkpoint_training_membership_reconstructed':False,'runs':rows}
(Path(__file__).parent/'results/stanza_split_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(rows,indent=2))

# Attach exposure labels to already generated score files without changing scores.
import csv
res=Path(__file__).parent/'results';scope={x['language']:x['interpretation'] for x in rows}
for name in ['parsing_summary.csv','parsing_auto_summary.csv']:
 path=res/name
 if not path.exists():continue
 scored=list(csv.DictReader(path.open()))
 for row in scored:row['evaluation_scope']=scope[row['language']]
 with path.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(scored[0]));w.writeheader();w.writerows(scored)
for name in ['parsing_manifest.json','parsing_auto_manifest.json']:
 path=res/name
 if not path.exists():continue
 m=json.loads(path.read_text());m['split_exposure_audit']='stanza_split_audit.json';m['kazakh_interpretation']=scope['kk'];path.write_text(json.dumps(m,indent=2)+'\n')
