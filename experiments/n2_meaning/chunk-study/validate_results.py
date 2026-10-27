"""Independently reconstruct saved chunks and verify the reported aggregates."""
from pathlib import Path
import argparse,csv,hashlib,json,statistics,sys,tarfile,re
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from exp_chunk_content import TOKENIZERS,LANGUAGES

def main():
    from tokenizers import Tokenizer
    import tiktoken
    ap=argparse.ArgumentParser();ap.add_argument('--archive',type=Path,required=True);ap.add_argument('--tokenizer-root',type=Path,default=Path.home()/'.cache/huggingface/hub');a=ap.parse_args()
    result=Path(__file__).resolve().parents[1]/'results';manifest=json.loads((result/'chunk_content_manifest.json').read_text())
    assert hashlib.sha256(a.archive.read_bytes()).hexdigest()==manifest['archive_sha256']
    for name,digest in manifest['outputs'].items():assert hashlib.sha256((result/name).read_bytes()).hexdigest()==digest
    fn={}
    for key,(repo,rev) in TOKENIZERS.items():
        path=a.tokenizer_root/('models--'+repo.replace('/','--'))/'snapshots'/rev/'tokenizer.json'
        assert hashlib.sha256(path.read_bytes()).hexdigest()==manifest['tokenizers'][key]['sha256']
        t=Tokenizer.from_file(str(path));t.no_padding();t.no_truncation();fn[key]=lambda text,t=t:len(t.encode(text,add_special_tokens=False).ids)
    e=tiktoken.get_encoding('o200k_base');fn['o200k']=lambda text:len(e.encode(text,disallowed_special=()))
    bpe=b'\n'.join(k.hex().encode()+b' '+str(v).encode() for k,v in sorted(e._mergeable_ranks.items(),key=lambda kv:kv[1]))
    assert hashlib.sha256(bpe).hexdigest()==manifest['tokenizers']['o200k']['mergeable_ranks_sha256']
    rows=list(csv.DictReader((result/'chunk_content_measured.csv').open()));chunks=list(csv.DictReader((result/'chunk_content_chunks.csv').open()))
    expected={(l,t) for l in LANGUAGES for t in fn};assert {(r['lang'],r['tokenizer']) for r in rows}==expected and len(rows)==len(expected)
    assert {(r['lang'],r['tokenizer']) for r in chunks}==expected
    checks=0
    with tarfile.open(a.archive) as tar:
        for row in rows:
            lang,key=row['lang'],row['tokenizer'];raw=tar.extractfile(manifest['inputs'][lang]['archive_member']).read();assert hashlib.sha256(raw).hexdigest()==manifest['inputs'][lang]['sha256']
            ss=[s.strip() for s in raw.decode().splitlines()];cc=[c for c in chunks if c['lang']==lang and c['tokenizer']==key];position=0
            for j,c in enumerate(cc):
                first,last=int(c['first_row'])-1,int(c['last_row']);assert first==position and first<last<=len(ss);position=last
                assert int(c['chunk'])==j+1 and int(c['sentences'])==last-first
                text=' '.join(ss[first:last]);n=fn[key](text);assert n==int(c['tokens']) and 0<n<=512
                assert len(re.findall(r'\S+',text))==int(c['words'])
                assert int(c['final_tail'])==int(j==len(cc)-1)
                if last<len(ss):assert fn[key](' '.join(ss[first:last+1]))>512
                checks+=1
            assert position==1012 and len(cc)-1==int(row['closed_chunks'])
            for key2 in ['words','sentences','tokens']:
                mean=statistics.mean(int(c[key2]) for c in cc[:-1]);assert abs(mean-float(row[key2+'_per_chunk']))<=.000001
            assert abs(statistics.mean(int(c['tokens']) for c in cc[:-1])/512*100-float(row['fill_percent']))<=.000001
            assert int(row['summarized_sentences'])+int(row['tail_sentences'])==1012
            assert int(row['tail_tokens'])==int(cc[-1]['tokens'])
            assert int(row['max_sentence_tokens'])==max(map(fn[key],ss))
            assert int(row['max_chunk_tokens'])==max(int(c['tokens']) for c in cc)
    report={'status':'passed','conditions':len(rows),'reencoded_chunks':checks,'input_rows_per_condition':1012,'all_chunks_within_budget':True,'all_closed_chunks_maximal_for_next_sentence':True,'summary_means_recomputed':True,'all_input_and_output_hashes_checked':True,'validator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (result/'chunk_content_validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
