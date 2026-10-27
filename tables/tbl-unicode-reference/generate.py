from pathlib import Path
import csv,unicodedata
p=Path(__file__).resolve().parent
rows=list(csv.DictReader((p/'data.csv').open()))
text='| Lowercase | Uppercase | Code points (lower / upper) | Unicode name |\n|---|---|---|---|\n'
for r in rows:
 assert r['lower_code']==f"U+{ord(r['lower']):04X}" and r['upper']==r['lower'].upper()
 assert r['unicode_name']==unicodedata.name(r['lower'])
 text+=f"| {r['lower']} | {r['upper']} | {r['lower_code']} / {r['upper_code']} | {r['unicode_name']} |\n"
text+='\n: Selected Cyrillic characters, checked against Unicode names and code points by the generator. These are encoding identities, not cross-language pronunciation claims. {#tbl-cyrillic-letters}\n'
(p/'output.md').write_text(text)
