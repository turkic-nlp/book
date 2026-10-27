"""Render the explicitly attributed grammar comparison; transcription is not IPA."""
from pathlib import Path
import csv,sys
HERE=Path(__file__).parent
sys.path.insert(0,str(HERE.parents[1]/'scripts'))
from book_tables import table
rows=list(csv.DictReader((HERE/'data.csv').open(encoding='utf-8')))
assert len(rows)==6 and all(r['source'] for r in rows)
table(HERE,['Language','Vowels (source transcription)','Spelling, in corresponding order','Scope','Source'],[[r[k] for k in ['language','inventory','orthography','scope','source']] for r in rows],'Vowel inventories under the cited analyses. Symbols follow Johanson’s Turkological notation, not a uniform IPA transcription. Orthographic correspondences do not imply identical pronunciation across languages. {#tbl-vowel-inventories}')
