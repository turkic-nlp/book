"""Corpus audit primitives: explicit sampling population and no fake denominators."""
import random, unicodedata, math
from collections import Counter

def reservoir(rows,k,seed=0):
    if k<=0:raise ValueError('sample size must be positive')
    rng=random.Random(seed);out=[];n=0
    for n,row in enumerate(rows,1):
        if n<=k:out.append(row)
        else:
            j=rng.randrange(n)
            if j<k:out[j]=row
    if n<k:raise ValueError('population smaller than requested sample')
    return out,{'population_documents':n,'sample_documents':k,'seed':seed,'method':'full-stream reservoir'}

def script_shares(text):
    c=Counter()
    for x in text:
        if not x.isalpha():continue
        name=unicodedata.name(x,'')
        c[next((s for s in ('LATIN','CYRILLIC','ARABIC') if s in name),'OTHER')]+=1
    n=sum(c.values())
    return {'letters':n,'shares':{s:c[s]/n if n else None for s in ('LATIN','CYRILLIC','ARABIC','OTHER')}}

def fst_coverage(words,lookup):
    eligible=[w for w in words if any(c.isalpha() for c in w)]
    def accepted(w):
        return any(reading and not reading.startswith('*') and '<unk>' not in reading and math.isfinite(weight)
                   for reading,weight in lookup(w))
    count=sum(accepted(w) for w in eligible)
    return {'accepted_words':count,'eligible_words':len(eligible),
            'coverage':count/len(eligible) if eligible else None}

def audit(text,sentences,target_label,predict_all,lookup,words):
    """Callbacks are built once for the chosen language/model revision.
    predict_all must search the full label space, including Russian and other.
    """
    parts=[s for s in sentences if s.strip()]
    labels=[predict_all(s.replace('\n',' ')) for s in parts]
    n=len(labels)
    return {'script':script_shares(text),'sentences':n,
        'target_share':sum(l==target_label for l in labels)/n if n else None,
        'russian_share':sum(l=='__label__rus_Cyrl' for l in labels)/n if n else None,
        'other_share':sum(l not in (target_label,'__label__rus_Cyrl') for l in labels)/n if n else None,
        'fst':fst_coverage(words,lookup)}

def weighted_clean(strata):
    # Each row: population documents, independently labelled sample, clean labels.
    if not strata or any(not 0<=r['clean']<=r['sample']<=r['population'] or r['sample']==0 for r in strata):
        raise ValueError('invalid strata')
    total=sum(r['population'] for r in strata)
    return sum(r['population']*r['clean']/r['sample'] for r in strata)/total

def uzbek_letter_apostrophes(text):
    """Derived Latin search key only: unify o/g letter marks, not tutuq/quotes."""
    import re
    return re.sub(r"([oOgG])[ʻʼ‘’'`]",lambda m:m[1]+'ʻ',unicodedata.normalize('NFC',text))
