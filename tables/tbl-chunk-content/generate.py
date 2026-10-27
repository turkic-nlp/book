"""Generate the measured N2-4 table; never silently substitute fertility estimates."""
from pathlib import Path
import csv,shutil,sys
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'experiments/common'))
from bookgen import md_table
source=ROOT/'experiments/n2_meaning/results/chunk_content_measured.csv'
rows=list(csv.DictReader(source.open()));shutil.copy2(source,HERE/'data.csv')
langs=list(dict.fromkeys(r['lang'] for r in rows));body=[]
for lang in langs:
    rs=[r for r in rows if r['lang']==lang]
    assert len(rs)==4 and len({r['tokenizer'] for r in rs})==4
    def bounds(key,decimals=0):
        v=[float(r[key]) for r in rs];return f'{min(v):.{decimals}f}–{max(v):.{decimals}f}'
    body.append([rs[0]['language'],bounds('words_per_chunk'),bounds('sentences_per_chunk',1),bounds('fill_percent',1)])
caption=('Measured content of sentence-packed chunks with a 512-token ceiling on original FLORES-200 devtest '
         '(1,012 aligned sentence rows per variety). Ranges are the minimum and maximum means across four pinned '
         'tokenisers; extrema in different columns need not come from the same tokeniser. Words are whitespace-delimited '
         'units. The final tail is excluded from means, with all rows retained in the chunk audit. Fill is the mean '
         'percentage of the 512-token budget used. Source: experiment N2-4; @costa2022nllb.')
(HERE/'output.md').write_text(md_table(['Language','Words/chunk','Sentences/chunk','Fill (%)'],['l','r','r','r'],body,caption,'tbl-chunk-content'))
print('Generated measured table:',len(body),'language varieties')
