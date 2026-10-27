"""Generate a sourced script overview; do not conflate reform dates and prevalence."""
from pathlib import Path
import csv,sys
HERE=Path(__file__).parent
sys.path.insert(0,str(HERE.parents[1]/'scripts'))
from book_tables import table
rows=list(csv.DictReader((HERE/'data.csv').open(encoding='utf-8')))
assert all(r['source'] and 'VERIFY' not in r['source'] for r in rows)
table(HERE,['Language','Scripts and regional scope','Historical or implementation note','Source'],[[r[k] for k in ['language','scripts','dated_scope','source']] for r in rows],'Selected language–script relationships. Historical dates follow the cited accounts; script prevalence and current legal status are not inferred from them. {#tbl-script-dates}')
