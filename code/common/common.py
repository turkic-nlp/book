"""Small, dependency-free validation shared by the remaining tutorials."""
import hashlib, json, math, unicodedata
from pathlib import Path

def canonical(text):
    return ' '.join(unicodedata.normalize('NFC', text).split())

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()

def read_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]

def check_splits(splits, text_key='text'):
    """IDs, source groups and exact normalised texts must be disjoint across splits.
    Within-split repeated text is allowed; IDs are always unique. Group IDs must be
    stable across derived variants, translations and excerpts of the same source.
    """
    seen = {k: {} for k in ('id', 'group_id', text_key)}
    for split, rows in splits.items():
        if not rows: raise ValueError(f'empty split: {split}')
        local_ids = set()
        for row in rows:
            if row['id'] in local_ids: raise ValueError('duplicate item ID')
            local_ids.add(row['id'])
            for key in seen:
                value = canonical(row[key]) if key == text_key else str(row[key])
                if not value: raise ValueError(f'empty {key}')
                previous = seen[key].setdefault(value, split)
                if previous != split: raise ValueError(f'{key} overlaps {previous}/{split}')
    return {k: len(v) for k, v in splits.items()}

def wilson(k, n, z=1.959963984540054):
    if not 0 <= k <= n or not n: raise ValueError('require 0 <= k <= n and n > 0')
    p=k/n; den=1+z*z/n
    centre=(p+z*z/(2*n))/den
    radius=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0., centre-radius), min(1., centre+radius)]
