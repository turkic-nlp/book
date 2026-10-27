from pathlib import Path
import csv
p=Path(__file__).resolve().parent
rows=list(csv.DictReader((p/'data.csv').open()))
text='| Language | ISO 639-3 | Descriptive grouping | Script examples |\n|---|---|---|---|\n'
for r in rows:text+='| '+' | '.join(r[k] for k in ('language','iso639_3','branch','script_examples'))+' |\n'
text+='\n: Selected contemporary languages in this appendix; 23 rows, distinct from toolkit coverage. Groupings summarise the book’s linguistic discussion; script examples are not an exhaustive statement of legal status. Population estimates and unverified Glottocodes are omitted. {#tbl-language-reference}\n'
(p/'output.md').write_text(text)
