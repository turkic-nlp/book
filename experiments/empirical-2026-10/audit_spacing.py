"""Record spacing outliers without editing or excluding benchmark rows."""
from common import *
from run_word_lengths import stats
import argparse
p=argparse.ArgumentParser();p.add_argument('--archive',type=Path,required=True);a=p.parse_args();texts,inputs=flores(a.archive);rows=[]
for lang,ss in texts.items():
 for i,s in enumerate(ss):
  x=stats(s)
  if x['whitespace_units']==1 or x['mean_letters_per_unit']>30:
   rows.append({'lang':lang,'row_id':i+1,'whitespace_units':x['whitespace_units'],'mean_letters_per_unit':x['mean_letters_per_unit'],'source':'experiments/empirical-2026-10/audit_spacing.py; original FLORES-200 devtest'})
csvout(Path(__file__).parent/'results'/'spacing_outliers.csv',rows)
jsonout(Path(__file__).parent/'results'/'spacing_audit.json',{'archive_sha256':ARCHIVE_SHA,'threshold':'one whitespace unit OR sentence mean >30 letters per letter-bearing whitespace unit; diagnostic only, no exclusions','counts':{lang:{'one_whitespace_unit':sum(stats(s)['whitespace_units']==1 for s in ss),'mean_over30':sum(stats(s)['mean_letters_per_unit']>30 for s in ss)} for lang,ss in texts.items()}})
