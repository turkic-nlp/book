"""N1: paired orthographic-length diagnostics on original FLORES-200 devtest.
No language-quality, naturalness or morphological-correctness labels are inferred.
"""
from common import *
import argparse,unicodedata,re,itertools

def stats(text):
 t=unicodedata.normalize('NFC',text);words=re.findall(r'\S+',t);letters=[sum(c.isalpha() for c in w) for w in words];letters=[n for n in letters if n];runs=[''.join(chars) for is_letter,chars in itertools.groupby(t,key=str.isalpha) if is_letter]
 assert letters and runs
 return {'whitespace_units':len(words),'letter_bearing_units':len(letters),'mean_letters_per_unit':float(np.mean(letters)),'mean_letter_run_length':float(np.mean([len(w) for w in runs])),'mean_codepoints_per_whitespace_unit':float(np.mean([len(w) for w in words])),'over10_letter_units':sum(n>10 for n in letters)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--archive',type=Path,required=True);a=ap.parse_args();texts,inputs=flores(a.archive);rows=[];summary=[];eng=np.array([stats(s)['mean_letters_per_unit'] for s in texts['eng_Latn']]);rng=np.random.default_rng(20261017);draw=rng.integers(0,len(eng),(2000,len(eng)))
 for lang,ss in texts.items():
  rr=[{'lang':lang,'row_id':i+1,**stats(s),'source':'experiments/empirical-2026-10/run_word_lengths.py; original FLORES-200 devtest'} for i,s in enumerate(ss)];rows.extend(rr);v=np.array([r['mean_letters_per_unit'] for r in rr]);delta=v-eng;boot=delta[draw].mean(1)
  summary.append({'lang':lang,'language':LANGS[lang],'sentences':len(ss),'mean_letters_per_unit':float(v.mean()),'median_sentence_mean':float(np.median(v)),'mean_letter_run_length':float(np.mean([r['mean_letter_run_length'] for r in rr])),'mean_whitespace_units':float(np.mean([r['whitespace_units'] for r in rr])),'paired_difference_vs_english':float(delta.mean()),'bootstrap_low':float(np.quantile(boot,.025)),'bootstrap_high':float(np.quantile(boot,.975)),'source':rr[0]['source']})
 out=Path(__file__).parent/'results';csvout(out/'word_length_items.csv',rows);csvout(out/'word_length_summary.csv',summary);jsonout(out/'word_length_manifest.json',{'archive_sha256':ARCHIVE_SHA,'inputs':inputs,'normalization':'NFC','primary_unit':'Whitespace-delimited token with at least one Unicode letter; count letters only within it','alternate_unit':'Contiguous Unicode letter runs, excluding digits and underscore','weighting':'Mean of sentence-level means, not pooled token mean','uncertainty':'2000 paired sentence bootstrap resamples, seed 20261017; descriptive conditional on the sample, not article-cluster or population uncertainty','scope':'Orthographic lengths on translations; not morphological complexity or filter quality.'})
if __name__=='__main__':main()
