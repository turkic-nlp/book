"""Audit raw Apertium ambiguity on public UD 2.17 test files.

Usage: python measure_ambiguity.py --tur UD_Turkish-TueCL/tr_tuecl-ud-test.conllu --kaz UD_Kazakh-KTB/kk_ktb-ud-test.conllu
(the Turkish file is parallel grammar examples; the Kazakh file is a different, larger sample)
All integer-ID syntactic words except PUNCT/NUM/SYM are the denominator,
including unknowns. Try NFC surface first, then language-aware lowercase.
The no-plus subset excludes ALL '+' continuations, not just copular readings.
"""
import argparse, collections, csv, hashlib, importlib.metadata, json, platform, unicodedata
from pathlib import Path
import hfst
from turkicnlp.resources.registry import ModelRegistry

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load(path):
    stream = hfst.HfstInputStream(str(path)); fst = stream.read(); stream.close(); return fst

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tur',type=Path,required=True,help='UD 2.17 tr_tuecl-ud-test.conllu')
    parser.add_argument('--kaz',type=Path,required=True,help='UD 2.17 kk_ktb-ud-test.conllu')
    args=parser.parse_args(); out=Path(__file__).resolve().parent
    rows=[]; records=[]; sources=[]
    for lang,script,corpus in [('tur','Latn',args.tur),('kaz','Cyrl',args.kaz)]:
        model=ModelRegistry.get_model_path(lang,'morph','apertium',script=script)/f'{lang}.automorf.hfst'
        ana=load(model); stats=collections.defaultdict(collections.Counter)
        source=f'{corpus.name} sha256:{sha(corpus)}; {model.name} sha256:{sha(model)}'
        sources.append({'language':lang,'corpus':corpus.name,'corpus_sha256':sha(corpus),'model':model.name,'model_sha256':sha(model)})
        sid=''; sentence=1
        for line in corpus.read_text().splitlines():
            if line.startswith('# sent_id = '): sid=line.split(' = ',1)[1]
            if not line.strip(): sentence+=1; continue
            c=line.split('\t')
            if len(c)!=10 or not c[0].isdigit() or c[3] in {'PUNCT','NUM','SYM'}: continue
            surface=unicodedata.normalize('NFC',c[1]); lookup=surface
            readings={a for a,_ in ana.lookup(surface)}
            if not readings:
                lookup=(surface.replace('I','ı').replace('İ','i') if lang=='tur' else surface).lower()
                readings={a for a,_ in ana.lookup(lookup)}
            simple={a for a in readings if '+' not in a}
            for pos in ('ALL',c[3]):
                v=stats[pos];v['tokens']+=1;v['unknown_count']+=not readings
                v['ambiguous_all_count']+=len(readings)>1;v['ambiguous_no_plus_count']+=len(simple)>1
            records.append({'lang':lang,'sentence_index':sentence,'sent_id':sid,'id':c[0],'form':c[1],'upos':c[3],'lookup':lookup,'readings':sorted(readings),'no_plus_readings':sorted(simple)})
        for pos,v in sorted(stats.items(),key=lambda x:(x[0]!='ALL',x[0])):
            row={'lang':lang,'upos':pos,**v}
            for key in ('unknown','ambiguous_all','ambiguous_no_plus'): row[key+'_rate']=v[key+'_count']/v['tokens']
            row['source']=source;rows.append(row)
    with (out/'ambiguity.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (out/'readings.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records))
    (out/'manifest.json').write_text(json.dumps({'date':'2026-10-26','python':platform.python_version(),'hfst':importlib.metadata.version('hfst'),'script_sha256':sha(__file__),'source_status':'Official UD 2.17 test files (UD_Turkish-TueCL, UD_Kazakh-KTB; CC BY-SA 4.0); paths are recorded only by file name','denominator':'integer-ID words excluding PUNCT, NUM, SYM; includes unknowns','normalization':'NFC; original first; Turkish-aware or ordinary lowercase only when original has no reading','simple_subset':'excludes every reading containing +','sources':sources},indent=2)+'\n')
    print(json.dumps([r for r in rows if r['upos']=='ALL'],indent=2))
if __name__=='__main__': main()
