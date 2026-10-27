"""Compile the toy grammar of Chapter 6 (finite-state morphology) with HFST and test it.

    pip install hfst            # tested with hfst 3.16.0.1, Python 3.12
    python build_and_test.py
"""
import hfst
import tempfile, json, hashlib, platform, importlib.metadata
from pathlib import Path
HERE=Path(__file__).resolve().parent
work=tempfile.TemporaryDirectory()

lexicon = hfst.compile_lexc_file(str(HERE / "tr-toy.lexc"))              # analysis:morphophonemic
hfst.compile_twolc_file(str(HERE / "tr-toy.twolc"), str(Path(work.name) / "tr-toy.twol.hfst"))
stream = hfst.HfstInputStream(str(Path(work.name) / "tr-toy.twol.hfst"))
rules = []
while not stream.is_eof():
    rules.append(stream.read())
stream.close()

generator = hfst.HfstTransducer(lexicon)
generator.compose_intersect(tuple(rules))                    # analysis:surface
generator.minimize()
analyser = hfst.HfstTransducer(generator)
analyser.invert()                                            # surface:analysis
analyser.minimize()
# Optimized-lookup format, the format of Apertium's .automorf/.autogen files
analyser.convert(hfst.ImplementationType.HFST_OLW_TYPE)
generator.convert(hfst.ImplementationType.HFST_OLW_TYPE)

def analyse(word):
    return sorted(a for a, _ in analyser.lookup(word))

def generate(analysis):
    return sorted(s for s, _ in generator.lookup(analysis))

accept = {"evler": "ev<n><pl>", "arabalar": "araba<n><pl>", "evlerde": "ev<n><pl><loc>",
          "arabalarda": "araba<n><pl><loc>", "gözden": "göz<n><abl>", "kitapta": "kitap<n><loc>",
          "kitaplardan": "kitap<n><pl><abl>"}
reject = ["evlar", "arabaler", "evlarda", "kitapda", "arabade"]
for word, gold in accept.items():
    assert analyse(word) == [gold], (word, analyse(word))      # the analysis, not just acceptance
for word in reject:
    assert analyse(word) == [], (word, analyse(word))
assert generate("göz<n><pl><loc>") == ["gözlerde"]
print("all tests passed")
for w in ["evlerde", "kitapta", "evlar"]:
    print(w, analyse(w))
print("göz<n><pl><loc> ->", generate("göz<n><pl><loc>"))

# Explicit reference forms cover every paradigm cell in the four-stem toy grammar.
paradigms={
    'ev':['ev','evde','evden','evler','evlerde','evlerden'],
    'araba':['araba','arabada','arabadan','arabalar','arabalarda','arabalardan'],
    'göz':['göz','gözde','gözden','gözler','gözlerde','gözlerden'],
    'kitap':['kitap','kitapta','kitaptan','kitaplar','kitaplarda','kitaplardan'],
}
tags=['<n>','<n><loc>','<n><abl>','<n><pl>','<n><pl><loc>','<n><pl><abl>']
for stem, forms in paradigms.items():
    for form, tag in zip(forms,tags):
        assert analyse(form)==[stem+tag],(form,analyse(form))
        assert generate(stem+tag)==[form],(stem+tag,generate(stem+tag))
result={'date':'2026-10-14','python':platform.python_version(),'hfst':importlib.metadata.version('hfst'),
        'paradigm_cells_checked_both_directions':24,'rejected_forms':reject,
        'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),HERE/'tr-toy.lexc',HERE/'tr-toy.twolc']}}
(HERE/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
work.cleanup()
print('24 paradigm cells verified in both directions; 5 invalid forms rejected')
