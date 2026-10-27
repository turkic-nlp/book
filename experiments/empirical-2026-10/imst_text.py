"""Redact and restore UD Turkish-IMST text in the frozen Stanza prediction files.

UD Turkish-IMST is licensed CC BY-NC-SA 4.0, which is incompatible with the
book's CC BY-SA 4.0 licence. The two Turkish prediction files in results/ are
therefore distributed without IMST text: word forms, predicted lemmas and the
`# text` comments are replaced by `_`/removed. Sentence IDs, character offsets,
predicted tags, features, heads and relations are kept.

    python imst_text.py redact                        # done once before release
    python imst_text.py restore --gold UD_ROOT/UD_Turkish-IMST/tr_imst-ud-test.conllu

`restore` refills forms and `# text` from the official UD 2.17 test file
(SHA-256 checked) and writes `*.restored.conllu` next to the redacted files,
which `validate_results.py` uses. Predicted lemmas are not recoverable, so the
Turkish Lemmas and BLEX rows are reported from the original run but are not
rescored after restoration.
"""
from pathlib import Path
import argparse, hashlib, json

HERE = Path(__file__).parent
RES = HERE / 'results'
FILES = {'gold_seg': RES / 'tr-ud217-predicted.conllu', 'auto': RES / 'tr-ud217-auto-predicted.conllu'}
GOLD_SHA = 'fc9269bd598489b942a025b678779557266ce0c054a843e47c7db386d76d6459'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sentences(path):
    return [b.split('\n') for b in Path(path).read_text(encoding='utf-8').strip('\n').split('\n\n') if b.strip()]


def write(path, blocks):
    Path(path).write_text('\n\n'.join('\n'.join(b) for b in blocks) + '\n\n', encoding='utf-8')


def is_token(line):
    return line and not line.startswith('#')


def misc_offsets(misc):
    d = dict(x.split('=', 1) for x in misc.split('|') if '=' in x)
    return (int(d['start_char']), int(d['end_char'])) if 'start_char' in d else None


def redact():
    for kind, path in FILES.items():
        out = []
        for b in sentences(path):
            nb = []
            for line in b:
                if line.startswith('# text = '):
                    continue
                if is_token(line):
                    f = line.split('\t')
                    inside_mwt_auto = kind == 'auto' and '-' not in f[0] and misc_offsets(f[9]) is None
                    if not inside_mwt_auto:   # model-produced MWT pieces have no offsets; kept (sub-word fragments only)
                        f[1] = '_'
                    f[2] = '_'
                    line = '\t'.join(f)
                nb.append(line)
            out.append(nb)
        write(path, out)
        print(f'redacted {path.name}: sha256 {sha(path)}')


def restore(gold):
    assert sha(gold) == GOLD_SHA, 'Use the official UD 2.17 Turkish-IMST test file'
    g = sentences(gold)
    gtext = [next(l[9:] for l in b if l.startswith('# text = ')) for b in g]
    gtok = [[l.split('\t') for l in b if is_token(l)] for b in g]
    # gold segmentation: same sentences and token/word lines as the gold file
    p = sentences(FILES['gold_seg']); assert len(p) == len(g)
    out = []
    for b, text, toks in zip(p, gtext, gtok):
        it = iter(toks); nb = []
        for line in b:
            if is_token(line):
                f = line.split('\t'); gf = next(it); assert f[0] == gf[0]; f[1] = gf[1]; line = '\t'.join(f)
            nb.append(line)
            if line.startswith('# sent_id'):
                nb.append('# text = ' + text)
        out.append(nb)
    write(FILES['gold_seg'].with_suffix('.restored.conllu'), out)
    # automatic tokenization: forms come from the gold sentence text via character offsets
    p = sentences(FILES['auto']); assert len(p) == len(g)
    out = []
    for b, text in zip(p, gtext):
        nb = []
        for line in b:
            if is_token(line):
                f = line.split('\t'); off = misc_offsets(f[9])
                if off:
                    f[1] = text[off[0]:off[1]]
                line = '\t'.join(f)
            nb.append(line)
        # the original runner wrote `# text` before `# sent_id`
        out.append(['# text = ' + text] + nb)
    write(FILES['auto'].with_suffix('.restored.conllu'), out)
    print('restored', *(FILES[k].with_suffix('.restored.conllu').name for k in FILES))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('action', choices=['redact', 'restore'])
    ap.add_argument('--gold', type=Path)
    a = ap.parse_args()
    redact() if a.action == 'redact' else restore(a.gold)
