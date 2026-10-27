| Query variety | MiniLM (%) | XLM-R (%) |
|---|--:|--:|
| English | 54.7 | 77.3 |
| Russian | 54.0 | 76.7 |
| Turkish | 54.1 | 77.1 |
| N. Azerbaijani | 39.4 | 73.5 |
| S. Azerbaijani | 31.4 | 40.3 |
| Turkmen | 23.8 | 33.6 |
| Kazakh | 31.1 | 75.1 |
| Kyrgyz | 35.3 | 71.0 |
| Tatar | 30.2 | 40.2 |
| Bashkir | 27.5 | 31.7 |
| Crimean Tatar | 44.8 | 65.2 |
| N. Uzbek | 32.8 | 50.7 |
| Uyghur | 18.1 | 60.9 |

: Native-script bitext top-1 accuracy, averaged equally over the other 12 target varieties. Each direction uses all 1,012 original FLORES-200 devtest rows as queries and candidates. Models are the pinned multilingual paraphrase MiniLM and XLM-R encoders, with their 128-token limit and recorded truncation. Source: `run_bitext.py`; @costa2022nllb. {#tbl-flores-native-probe}
