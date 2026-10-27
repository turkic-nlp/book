# Pinned UD 2.17 Turkic inventory

Run `python fetch.py /tmp/clean-ud217`, then `python generate.py /tmp/clean-ud217`.
Run `python generate.py` to render the frozen CSV without downloading data.

The 25 treebanks include modern Turkic, historical Turkic and Turkish code-switching resources.
Counts use only official `r2.17` CoNLL-U files whose URLs and SHA-256 hashes appear in
`download-manifest.json`; derived `.ct.conllu` files and local train/test additions are excluded.
The generator verifies hashes before counting. `source-manifest.json` records counted inputs.
`light-verbs.csv` records all directly connected yardım/et lemma pairs found in BOUN, IMST and PUD,
with sentence IDs; it is not a frequency estimate for every light-verb construction.

The local folder named `ud-treebanks-v2.17` was not a clean release. It included Turkmen-TueCL and
Bashkir-TUD silver data, added Azerbaijani training data and an altered Azerbaijani test file,
and extra Tatar files. The public release inventory must not count these as released gold data.
404 records in the download audit document rejected local additions, not missing table inputs.
The original files were not changed.

Only derived counts, short attested forms and provenance metadata are redistributed here. Consult
individual treebank READMEs/licences at the recorded release tags before redistributing corpus text.
The `r2.17` inventory is a reproducible historical snapshot, not a claim to cover later releases.
