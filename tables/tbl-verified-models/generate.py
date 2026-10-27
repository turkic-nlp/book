"""Render exact base-model parameter counts from saved pinned configurations.
Fetch metadata via experiments/remaining_revision/fetch_sources.py first.
Does not fetch or instantiate pretrained weights.
"""
import csv,json,sys
from pathlib import Path
import torch
from transformers import AutoConfig,AutoModel
ROOT=Path(__file__).resolve().parent
source=Path(sys.argv[1])
specs=[('berturk','Turkish encoder','dbmdz/bert-base-turkish-cased'),
       ('xlmr','Multilingual encoder','FacebookAI/xlm-roberta-base'),
       ('mt5','Multilingual encoder-decoder','google/mt5-base'),
       ('whisper','Speech encoder-decoder','openai/whisper-small'),
       ('tts-chv','Chuvash TTS','facebook/mms-tts-chv'),
       ('tts-crh','Crimean Tatar TTS','facebook/mms-tts-crh')]
rows=[]
for folder,task,repo in specs:
    info=json.loads((source/folder/'info.json').read_text());cfg=json.loads((source/folder/'config.json').read_text())
    config=AutoConfig.for_model(cfg.pop('model_type'),**cfg)
    with torch.device('meta'):model=AutoModel.from_config(config)
    rows.append(dict(model=repo,task=task,parameters=sum(p.numel() for p in model.parameters()),
        class_name=type(model).__name__,revision=info['sha'],
        source=f"https://huggingface.co/{repo}/blob/{info['sha']}/config.json",
        licence=str(info.get('cardData',{}).get('license','not specified in fetched metadata')),
        checked='2026-10-15',weights_tested='no'))
with (ROOT/'data.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
text='| Checkpoint | Role | Base parameters | Loaded class |\n|---|---|---:|---|\n'
for r in rows:text+=f"| [{r['model']}](https://huggingface.co/{r['model']}/tree/{r['revision']}) | {r['task']} | {r['parameters']:,} | `{r['class_name']}` |\n"
text+='\n: Pinned configurations checked 15 October 2026. Counts are generated from `AutoModel` on the meta device, without pretrained weights; a task head changes the count. Availability is not a quality evaluation. Sources, revisions and licence metadata: `tables/tbl-verified-models/data.csv`. {#tbl-verified-models}\n'
(ROOT/'output.md').write_text(text)
print([(r['model'],r['parameters']) for r in rows])
