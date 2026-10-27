from pathlib import Path
import json,hashlib,sys,subprocess,argparse
ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True);ap.add_argument('--toolkit',type=Path,required=True);args=ap.parse_args()
sys.path.insert(0,str(args.toolkit))
from turkicnlp.scripts import Script
from turkicnlp.scripts.transliterator import Transliterator
import turkicnlp.scripts.transliterator as module
r=args.data;rows=[json.loads(x) for x in (r/'uzn_Latn.jsonl').read_text().splitlines()];to_c=Transliterator('uzb',Script.LATIN,Script.CYRILLIC);to_l=Transliterator('uzb',Script.CYRILLIC,Script.LATIN);out=[]
for i,x in enumerate(rows):
 q=x['question'];c=to_c.transliterate(q);back=to_l.transliterate(c);assert not any(0xe000<=ord(ch)<=0xf8ff for ch in c+back);out.append({'row':i,'original':q,'cyrillic':c,'roundtrip':back})
(r/'uzbek-script-probe.json').write_text(json.dumps(out,ensure_ascii=False))
files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(module.__file__).parent.rglob('*.py')}
(r/'uzbek-script-manifest.json').write_text(json.dumps({'toolkit_source_files':files,'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=args.toolkit,text=True).strip(),'mapping':'uzb LATIN→CYRILLIC→LATIN','queries':len(out),'changed_queries':sum(x['original']!=x['cyrillic'] for x in out),'exact_roundtrip_queries':sum(x['original']==x['roundtrip'] for x in out),'human_validated':False},indent=2))
print(len(out),'queries transformed')
