"""Candidate rule checks, not context-disambiguated judgments.

Supply words from one declared tokenizer and a pinned raw HFST lookup callback.
All analyser readings are considered; no UPOS guess or prefix fallback is used.
No clembench transcript format is assumed: adapt a pinned release explicitly.
"""
import math
import re
import unicodedata


def key(text, lang):
    text = unicodedata.normalize('NFC', text)
    if lang in {'tur', 'aze'}:
        text = text.replace('I', 'ı').replace('İ', 'i')
    return text.casefold()


def check_tokens(tokens, forbidden, lookup, lang):
    if not forbidden or any(not f.strip() or any(c.isspace() for c in f) for f in forbidden):
        raise ValueError('provide nonempty single-token forbidden lemmas')
    blocked = {key(f, lang) for f in forbidden}
    result = {'surface_hits': [], 'lemma_candidates': [], 'unresolved': []}
    for token in tokens:
        if not any(c.isalpha() for c in token):
            continue
        norm = key(token, lang)
        if norm in blocked:
            result['surface_hits'].append(token)
        readings = []
        for form, weight in lookup(token):
            if isinstance(form, bytes):
                form = form.decode('utf-8')
            if not form or form.startswith('*') or not math.isfinite(weight):
                continue
            # Raw Apertium lemma<tag> format. Do not silently parse another schema.
            clean = re.sub(r'@[^@]+@', '', form)
            if '<' not in clean:
                raise ValueError('expected raw Apertium lemma<tag> readings')
            readings.append(clean.split('<', 1)[0])
        matches = sorted({x for x in readings if key(x, lang) in blocked})
        if matches:
            result['lemma_candidates'].append({'token': token, 'lemmas': matches})
        if not readings and norm not in blocked:
            result['unresolved'].append(token)
    return result
