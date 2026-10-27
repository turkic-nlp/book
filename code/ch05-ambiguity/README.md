# Chapter 5/7 ambiguity snapshot

Run with HFST 3.16.0.1 and the recorded local TurkicNLP 0.5.0 checkout:

```sh
PYTHONPATH=/path/to/turkicnlp python code/ch05-ambiguity/measure_ambiguity.py /path/to/turkicnlp/tuecl_files
```

`manifest.json` identifies the exact corpus and transducer hashes. The local Turkish/Kazakh TueCL copies are not labelled as a published UD release. `readings.jsonl` stores every selected token and its analyses; `ambiguity.csv` stores integer numerators and full-precision rates by language/POS.

The denominator includes unknown tokens and excludes PUNCT/NUM/SYM and non-integer CoNLL-U IDs. The `no_plus` subset removes all `+` continuations; calling this “without copula” would be too narrow. Lookup tries NFC surface spelling first and lowercases only after failure, using Turkish dotted/dotless-I handling for Turkish.
