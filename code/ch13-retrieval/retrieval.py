"""ID-aligned translation retrieval; finite unit vectors; explicit tie policy."""
import numpy as np

def align(source,target):
    def index(rows):
        out={}
        for r in rows:
            key=(str(r['id']),r['split'])
            if key in out: raise ValueError('duplicate alignment ID in selected variety')
            if not r['text'].strip():raise ValueError('empty text')
            out[key]=r
        return out
    a,b=index(source),index(target)
    if not a or set(a)!=set(b): raise ValueError('incomplete translation alignment')
    keys=sorted(a)
    return [a[k] for k in keys],[b[k] for k in keys]

def top1(source,target,src_vectors,tgt_vectors):
    """Rows must already be aligned. Exact duplicate target texts are positives.
    Tied highest scores receive fractional credit: positive ties / all ties.
    Other semantic alternatives need human relevance judgments, not this rule.
    """
    a=np.array(src_vectors,dtype=float,copy=True);b=np.array(tgt_vectors,dtype=float,copy=True)
    if a.ndim!=2 or b.ndim!=2 or a.shape!=b.shape or len(a)!=len(source) or len(b)!=len(target) or not len(a):
        raise ValueError('unaligned shapes')
    if [(r['id'],r['split']) for r in source]!=[(r['id'],r['split']) for r in target]:raise ValueError('unaligned IDs')
    if not np.isfinite(a).all() or not np.isfinite(b).all():raise ValueError('nonfinite embeddings')
    for arr in (a,b):
        norms=np.linalg.norm(arr,axis=1,keepdims=True)
        if (norms==0).any():raise ValueError('zero embedding')
        arr/=norms
    scores=[]
    texts=[r['text'] for r in target]
    for i,v in enumerate(a):
        sim=v@b.T;ties=np.flatnonzero(np.isclose(sim,sim.max(),rtol=0,atol=1e-8))
        scores.append(sum(texts[j]==texts[i] for j in ties)/len(ties))
    return {'n_queries':len(a),'n_candidates':len(b),'top1':float(np.mean(scores)),'item_scores':scores}
