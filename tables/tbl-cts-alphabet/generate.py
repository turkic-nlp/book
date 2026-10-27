"""Export the exact alphabet of the frozen toolkit-source snapshot."""
from pathlib import Path
import json,sys
HERE=Path(__file__).parent
sys.path.insert(0,str(HERE.parents[1]/'scripts'))
from book_tables import export,table
s=json.loads((HERE/'source.json').read_text())
rows=[]
for scope,pairs in [('base',s['ordered_pairs']),('Uyghur extension',s['extension_pairs'])]:
    for pair in pairs:
        assert len(pair)==2
        rows.append({'letters':pair,'codepoints':' / '.join(f'U+{ord(c):04X}' for c in pair),'scope':scope,'source':s['source']+'; SHA256 '+s['source_sha256']})
assert len(s['ordered_pairs'])==34 and len({k.split('_')[0] for k in s['cts_mappings']})==23
allowed=set(''.join(s['ordered_pairs']+s['extension_pairs']))
assert all(c in allowed for mapping in s['cts_mappings'].values() for value in mapping.values() for c in value if c.isalpha())
export(HERE,rows)
# Two parallel blocks keep the full code-point inventory compact in print.
body=[]
for i in range(18):
    left=rows[i];right=rows[i+18] if i+18<len(rows) else None
    body.append([left['letters'],left['codepoints'],right['letters'] if right else '',right['codepoints'] if right else ''])
table(HERE,['Letters','Code points (upper / lower)','Letters','Code points (upper / lower)'],body,'CTS base alphabet and the additional Éé pair for Uyghur, from the frozen local TurkicNLP source identifying itself as 0.5.0 (13 October 2026). Source hash and all CTS mappings are recorded in `tables/tbl-cts-alphabet/source.json`; the package version alone does not identify this local source revision. {#tbl-cts-alphabet}')
