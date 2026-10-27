| Test treebank | Gold-word LAS | Auto word F1 | Auto UAS | Auto LAS |
|---|--:|--:|--:|--:|
| Kyrgyz-KTMU | 71.17 | 99.12 | 82.30 | 70.62 |
| Turkish-IMST | 70.23 | 97.26 | 73.57 | 65.95 |
| Uyghur-UDT | 65.29 | 99.48 | 76.17 | 64.80 |
| Kazakh-KTB† (replay, not held-out) | 95.57 | 99.80 | 96.57 | 95.34 |

: Measured Stanza scores (%) on the same official UD 2.17 tests. Both conditions retain gold sentence boundaries; the automatic condition predicts tokenization/MWT and uses the official alignment-aware scorer. † Kazakh has split-exposure risk and is not a held-out score. Gold-word LAS is repeated from the preceding table. Source: run_parsing.py and run_parsing_auto.py. {#tbl-ud217-tokenization-probe}
