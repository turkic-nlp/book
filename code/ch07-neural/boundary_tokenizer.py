"""Strict surface-morph encoding; whitespace is retained in a separate sidecar.

This demonstrates the boundary contract, not a drop-in pretrained LM tokenizer.
The same segment_word callable must be used for training and inference.
"""
import re
BOUNDARY='│'

def segmented_word(word, segment_word):
    if not word or any(c.isspace() for c in word) or BOUNDARY in word or '▁' in word:
        raise ValueError('Word contains whitespace or a reserved marker')
    parts=list(segment_word(word))
    if not parts or any(not p for p in parts) or ''.join(parts)!=word:
        raise ValueError('Segmenter changed the surface or returned empty segments')
    return BOUNDARY.join(parts)

def training_lines(text, segment_word):
    return [segmented_word(m.group(),segment_word) for m in re.finditer(r'\S+',text)]

def encode_text(text, sp, segment_word):
    encoded=[]
    for m in re.finditer(r'\s+|\S+',text):
        value=m.group()
        if value.isspace(): encoded.append({'whitespace':value});continue
        segmented=segmented_word(value,segment_word)
        ids=sp.encode(segmented,out_type=int)
        pieces=[sp.id_to_piece(i) for i in ids]
        if any(BOUNDARY in p and p!=BOUNDARY for p in pieces):
            raise ValueError('A token crosses a boundary')
        if sp.unk_id() in ids or sp.decode(ids)!=segmented:
            raise ValueError('Token IDs do not reconstruct segmented input')
        encoded.append({'ids':ids})
    if decode_text(encoded,sp)!=text: raise ValueError('Text round trip failed')
    return encoded

def decode_text(encoded,sp):
    return ''.join(x['whitespace'] if 'whitespace' in x else sp.decode(x['ids']).replace(BOUNDARY,'') for x in encoded)
