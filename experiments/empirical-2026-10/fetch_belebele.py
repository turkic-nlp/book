"""Download only pinned public Belebele files and verify their SHA-256 hashes."""
from pathlib import Path
import argparse,hashlib,json,shutil,urllib.request
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);here=Path(__file__).parent;manifest=here/'inputs/belebele-source-manifest.json';m=json.loads(manifest.read_text());checks=json.loads((here/'inputs/checksums.json').read_text());assert all(hashlib.sha256((here/'inputs'/name).read_bytes()).hexdigest()==h for name,h in checks.items())
for x in m['files']+[{'code':'LICENSE_CC-BY-SA4.0','url':m['license_url'],'sha256':m['license_sha256']}]:
 name=x['code'] if x['code'].startswith('LICENSE') else x['code']+'.jsonl';dest=a.out/name
 data=dest.read_bytes() if dest.exists() else urllib.request.urlopen(x['url'],timeout=120).read()
 assert hashlib.sha256(data).hexdigest()==x['sha256'],f'Checksum mismatch: {name}'
 if not dest.exists():dest.write_bytes(data)
 print('Verified',name)
for name in ['belebele-source-manifest.json','uzbek-script-probe.json','uzbek-script-manifest.json']:
 shutil.copy2(here/'inputs'/name,a.out/name)
