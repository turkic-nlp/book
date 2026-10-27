"""Fetch the pinned small source files listed by the recorded audit manifest.
No pretrained weights or speech audio are requested. API metadata is historical:
use saved config summaries for parameter-count regeneration instead of expecting
current API responses to have historical byte hashes.
"""
from pathlib import Path
import argparse,hashlib,json,urllib.request
p=argparse.ArgumentParser();p.add_argument('destination',type=Path);a=p.parse_args()
manifest=json.loads((Path(__file__).parent/'source-manifest.json').read_text())
for name,item in manifest.items():
    if '/api/' in item['url']:continue
    target=a.destination/name;target.parent.mkdir(parents=True,exist_ok=True)
    data=urllib.request.urlopen(urllib.request.Request(item['url'],headers={'User-Agent':'TurkicNLP-book-source-audit/1.0'}),timeout=60).read()
    if hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError('source hash mismatch: '+name)
    target.write_bytes(data)
print('Pinned source files verified in',a.destination)
