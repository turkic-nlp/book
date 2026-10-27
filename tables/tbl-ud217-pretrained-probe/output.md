| Test treebank | Words | UPOS | UFeats | UAS | LAS |
|---|--:|--:|--:|--:|--:|
| Kyrgyz-KTMU | 11771 | 90.40 | 71.78 | 82.98 | 71.17 |
| Turkish-IMST | 10032 | 95.18 | 92.47 | 78.37 | 70.23 |
| Uyghur-UDT | 10330 | 89.69 | 88.38 | 76.72 | 65.29 |
| Kazakh-KTB† (replay, not held-out) | 10007 | 98.74 | 98.23 | 96.83 | 95.57 |

: Measured pretrained Stanza scores (%) on official UD 2.17 test files, using gold sentence and syntactic-word boundaries and predicted tags/features. The UD scorer includes punctuation in UAS/LAS; all denominators are retained. † Kazakh is a replay diagnostic with split-exposure risk, not held-out accuracy. These are not raw-text or newly trained results. Source: `run_parsing.py`. {#tbl-ud217-pretrained-probe}
