"""Count a local UD 2.17 release; no model predictions. Usage: python generate.py UD_ROOT.
Without an argument, render the frozen CSV. Integer IDs count syntactic words;
range IDs count orthographic tokens once, replacing their component words.
"""
from pathlib import Path
import csv,hashlib,json,sys
HERE=Path(__file__).resolve().parent
LANGS={'Turkish','Turkish_German','Turkish_English','Ottoman_Turkish','Old_Turkish','Azerbaijani','Kazakh','Kyrgyz','Uzbek','Uyghur','Tatar','Yakut'}
def sentences(path):
    rows=[];sid=None
    for line in path.read_text().splitlines()+['']:
        if line.startswith('# sent_id = '):sid=line[12:]
        elif line and not line.startswith('#'):
            parts=line.split('\t')
            if len(parts)!=10:raise ValueError((path,line))
            rows.append(parts)
        elif not line and rows:
            yield sid,rows;rows=[];sid=None
if len(sys.argv)>1:
    root=Path(sys.argv[1]);rows=[];manifest={};examples=[]
    verified=json.loads((HERE/'download-manifest.json').read_text())
    expected={r['file']:r['sha256'] for r in verified if 'sha256' in r}
    for rel,digest in expected.items():
        if hashlib.sha256((root/rel).read_bytes()).hexdigest()!=digest:raise ValueError(f'Not the pinned official file: {rel}')
    for d in sorted(root.glob('UD_*')):
        if d.name[3:].split('-')[0] not in LANGS:continue
        row={'treebank':d.name[3:],'train':0,'dev':0,'test':0,'words':0,'tokens':0,'source':f'UD 2.17, {d.name}/*.conllu; generate.py; source-manifest.json'}
        files=sorted(root/rel for rel in expected if Path(rel).parent.name==d.name)
        if not files:continue
        for p in files:
            split=p.stem.rsplit('-',1)[1]
            manifest[str(p.relative_to(root))]=hashlib.sha256(p.read_bytes()).hexdigest()
            for sid,words in sentences(p):
                row[split]+=1
                ints={int(w[0]):w for w in words if w[0].isdigit()}
                row['words']+=len(ints);tokens=len(ints)
                for w in words:
                    if '-' in w[0]:
                        a,b=map(int,w[0].split('-'));tokens-=b-a
                row['tokens']+=tokens
                if d.name in {'UD_Turkish-BOUN','UD_Turkish-IMST','UD_Turkish-PUD'}:
                    for w in ints.values():
                        if w[2]=='yardım' and w[6].isdigit() and int(w[6]) in ints:
                            h=ints[int(w[6])]
                            if h[2]=='et':examples.append({'treebank':d.name[3:],'file':p.name,'sent_id':sid,'dependent':w[1],'dependent_upos':w[3],'head':h[1],'head_upos':h[3],'relation':w[7],'source':f'UD 2.17 {p.name}, sent_id={sid}'})
                        if w[2]=='et' and w[6].isdigit() and int(w[6]) in ints and ints[int(w[6])][2]=='yardım':
                            h=ints[int(w[6])];examples.append({'treebank':d.name[3:],'file':p.name,'sent_id':sid,'dependent':w[1],'dependent_upos':w[3],'head':h[1],'head_upos':h[3],'relation':w[7],'source':f'UD 2.17 {p.name}, sent_id={sid}'})
        rows.append(row)
    for filename,data in [('data.csv',rows),('light-verbs.csv',examples)]:
        with (HERE/filename).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    (HERE/'source-manifest.json').write_text(json.dumps({'release':'2.17','sha256':manifest},indent=2)+'\n')
rows=list(csv.DictReader((HERE/'data.csv').open()))
for name,condition,label in [('turkish',lambda r:r['treebank'].startswith('Turkish-'),'tbl-turkish-treebanks'),('other',lambda r:not r['treebank'].startswith('Turkish-'),'tbl-other-treebanks')]:
    text='| Treebank | Train sentences | Dev sentences | Test sentences | Syntactic words | Orthographic tokens |\n|---|---:|---:|---:|---:|---:|\n'
    for r in rows:
        if condition(r):text+='| '+r['treebank'].replace('_',' ')+' | '+' | '.join(f'{int(r[k]):,}' for k in ('train','dev','test','words','tokens'))+' |\n'
    text+='\n: UD 2.17 inventory, generated from the release CoNLL-U files by `tables/tbl-ud217-inventory/generate.py`; file hashes are recorded alongside the CSV. A zero means no sentences in that split. Word and token totals sum all splits; multiword-token ranges count once in the token total, and empty nodes count in neither. Historical and code-switched treebanks retain their UD language names. {#'+label+'}\n'
    (HERE/f'output-{name}.md').write_text(text)
print(f'{len(rows)} treebanks; frozen counts rendered')
