"""Fetch only the pinned official release files into a separate directory.
Usage: python fetch.py /path/to/clean/ud217
"""
from pathlib import Path
import hashlib,json,sys,urllib.request
here=Path(__file__).resolve().parent;root=Path(sys.argv[1]);root.mkdir(parents=True,exist_ok=True)
for row in json.loads((here/'download-manifest.json').read_text()):
    if 'sha256' not in row:continue  # local additions absent from the release; retained for the audit
    dest=root/row['file']
    if dest.exists():
        if hashlib.sha256(dest.read_bytes()).hexdigest()!=row['sha256']:raise ValueError(f'existing file differs: {dest}')
        continue
    data=urllib.request.urlopen(row['url'],timeout=120).read()
    if hashlib.sha256(data).hexdigest()!=row['sha256']:raise ValueError(f'source changed: {row["url"]}')
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
