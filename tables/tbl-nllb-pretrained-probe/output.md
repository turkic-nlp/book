| Direction | Sentences | BLEU-13a | chrF | chrF++ |
|---|--:|--:|--:|--:|
| Turkish → Kazakh | 1012 | 9.48 | 41.97 | 37.55 |
| Kazakh → Turkish | 1012 | 12.02 | 45.25 | 41.04 |

: Measured NLLB-200 distilled 600M greedy translation on original FLORES-200 devtest. No fine-tuning or input truncation; explicit target language token, one beam and a 256-token generation ceiling. Exact SacreBLEU signatures and output audits are retained. Source: `run_translation.py`; @costa2022nllb. {#tbl-nllb-pretrained-probe}
