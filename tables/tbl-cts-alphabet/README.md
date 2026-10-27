# CTS alphabet and mapping snapshot

`source.json` records the complete CTS-target mappings, explicit case pairs and SHA-256 of the local `turkicnlp/scripts/transliterator.py` source captured on 2026-10-13. The local toolkit reports version 0.5.0; it may contain changes absent from a published 0.5.0 wheel. Do not interpret the version as an exact revision pin. `python generate.py` needs only the standard library, verifies mapping-output letters against the exported inventory, and writes `data.csv` and the chapter table. Unsupported input characters can still pass through the converter; the output alphabet is not a validator of arbitrary input.

The frozen snapshot is contemporary documentation of the implementation, not proof of which mapping revision produced an older experiment. A comparison with the 2024 commission’s complete annex remains a separate source-verification task.
