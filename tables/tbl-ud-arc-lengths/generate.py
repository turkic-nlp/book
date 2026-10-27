"""Recompute descriptive basic-arc distances from hash-verified UD 2.17 test files.
Usage: python generate.py /path/to/ud217-official
No parser is run. Root and PUNCT-dependent arcs excluded; punctuation positions
remain in distance. Range IDs and empty nodes are skipped. Quantiles use nearest
rank. Separate treebanks are not pooled as representative language samples.
"""
from pathlib import Path
import argparse,csv,hashlib,json,math,statistics
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
SELECT=['UD_Turkish-BOUN','UD_Turkish-IMST','UD_Azerbaijani-TueCL','UD_Kazakh-KTB','UD_Kyrgyz-KTMU','UD_Tatar-NMCTT','UD_Uyghur-UDT','UD_Uzbek-UT']
def quantile(values,p):
    return sorted(values)[math.ceil(len(values)*p)-1] if values else None

def summarise(path):
    sentences=[];sentence=[]
    for line in path.read_text().splitlines()+['']:
        if not line.strip():
            if sentence:sentences.append(sentence);sentence=[]
        elif not line.startswith('#'):
            cells=line.split('\t')
            if len(cells)!=10:raise ValueError('invalid row')
            if cells[0].isdigit(): sentence.append(cells)
    lengths=[];acl=[];left=0;words=0
    for sent in sentences:
        ids={int(c[0]) for c in sent};words+=len(sent)
        for c in sent:
            i=int(c[0]);h=int(c[6]);rel=c[7]
            if h and h not in ids: raise ValueError('missing basic head')
            if not h or c[3]=='PUNCT':continue
            lengths.append(abs(i-h));left+=i<h
            if rel.split(':')[0]=='acl':acl.append(abs(i-h))
    return dict(sentences=len(sentences),syntactic_words=words,eligible_arcs=len(lengths),
                distance_sum=sum(lengths),mean_distance=statistics.mean(lengths) if lengths else None,
                median_distance=quantile(lengths,.5),p90_distance=quantile(lengths,.9),
                dependent_before_head=left,acl_arcs=len(acl),acl_distance_sum=sum(acl),
                acl_median=quantile(acl,.5),acl_p90=quantile(acl,.9))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('source_root',type=Path,nargs='?');a=ap.parse_args()
    manifest=json.loads((ROOT/'tables/tbl-ud217-inventory/source-manifest.json').read_text())
    if a.source_root is None:
        rows=list(csv.DictReader((HERE/'data.csv').open()))
        for row in rows:
            for k in row:
                if k not in {'treebank','split','source'}: row[k]=float(row[k]) if k=='mean_distance' else int(row[k]) if row[k] else None
    else:
        rows=[];sources={}
        for rel,expected in sorted(manifest['sha256'].items()):
            if not rel.endswith('-test.conllu'):continue
            p=a.source_root/rel;actual=hashlib.sha256(p.read_bytes()).hexdigest();assert actual==expected,rel
            treebank=rel.split('/')[0];url=f'https://github.com/UniversalDependencies/{treebank}/blob/r2.17/{p.name}'
            rows.append({'treebank':treebank,'split':'test',**summarise(p),'source':url+' sha256:'+actual})
            sources[rel]={'sha256':actual,'url':url}
        with (HERE/'data.csv').open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
        (HERE/'source-manifest.json').write_text(json.dumps({'release':'2.17','files':sources,'method':__doc__},indent=2)+'\n')
    lines=['| Treebank | Sentences | Arcs | Mean | Median | P90 |','|:--|--:|--:|--:|--:|--:|']
    for row in rows:
        if row['treebank'] in SELECT:
            lines.append(f"| {row['treebank'][3:]} | {row['sentences']:,} | {row['eligible_arcs']:,} | {row['mean_distance']:.2f} | {row['median_distance']} | {row['p90_distance']} |")
    lines+=['',': Basic dependency distance in selected official UD 2.17 test sets, measured in integer-ID word positions. Root and punctuation-dependent arcs are excluded; intervening punctuation still occupies a position. P90 uses nearest rank. All 25 treebanks and source hashes are in the accompanying CSV. These are corpus diagnostics, not parser scores or matched language comparisons. {#tbl-ud-arc-lengths}']
    (HERE/'table.qmd').write_text('\n'.join(lines)+'\n')
    print(len(rows),'treebanks;',sum(r['eligible_arcs'] for r in rows),'arcs')
if __name__=='__main__':main()
