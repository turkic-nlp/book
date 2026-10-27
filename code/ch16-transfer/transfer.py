"""Strict span reconstruction and conservative transliteration boundary mapping."""
SCHEMA={'PERSON':'PER','PER':'PER','ORG':'ORG','ORGANIZATION':'ORG','ORGANISATION':'ORG',
        'LOC':'LOC','LOCATION':'LOC','GPE':'LOC'}

def bio_spans(words,text):
    spans=[];active=None;previous_end=0
    for w in words:
        start,end,tag=w['start'],w['end'],w['tag']
        if not 0<=start<end<=len(text) or start<previous_end or text[start:end]!=w['text']:raise ValueError('invalid original offsets')
        previous_end=end
        if tag=='O': prefix,kind='O',None
        else:
            prefix,kind=tag.split('-',1)
            if prefix not in ('B','I'):raise ValueError('invalid BIO prefix')
            kind=SCHEMA.get(kind)
            if kind is None:prefix='O'
        if prefix=='I' and (active is None or active[2]!=kind):raise ValueError('orphan/mismatched I tag')
        if prefix!='I':
            if active:spans.append(tuple(active));active=None
            if prefix=='B':active=[start,end,kind]
        else:active[1]=end
    if active:spans.append(tuple(active))
    return spans

def conversion_map(text,convert):
    """Map only unique stable boundaries. Reject context-sensitive/deleted ambiguity.
    Prefix probing is quadratic: appropriate for a short diagnostic, not a corpus.
    """
    converted=convert(text);reverse={}
    for i in range(len(text)+1):
        prefix=convert(text[:i])
        if converted.startswith(prefix):reverse.setdefault(len(prefix),[]).append(i)
    return converted,{j:ii[0] for j,ii in reverse.items() if len(ii)==1}

def restore_span(span,reverse):
    s,e,label=span
    if s not in reverse or e not in reverse:raise ValueError('span cuts an ambiguous transliteration unit')
    return reverse[s],reverse[e],label
