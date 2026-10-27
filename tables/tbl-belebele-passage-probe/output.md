| Language | Surface | Prefix 5 | MiniLM | XLM-R |
|---|--:|--:|--:|--:|
| N. Azerbaijani | 0.638 | 0.827 | 0.347 | 0.639 |
| English | 0.881 | 0.904 | 0.858 | 0.882 |
| Kazakh | 0.653 | 0.818 | 0.310 | 0.697 |
| Kyrgyz | 0.668 | 0.846 | 0.257 | 0.620 |
| Russian | 0.731 | 0.888 | 0.797 | 0.844 |
| Turkish | 0.744 | 0.855 | 0.789 | 0.850 |
| N. Uzbek | 0.703 | 0.839 | 0.270 | 0.355 |

: Measured nDCG@10 for source-passage retrieval derived from Belebele: 900 questions and 488 candidate passages per language. This is not Belebele multiple-choice accuracy. BM25 uses fixed k1=1.2 and b=0.75; dense encoders use their 128-token limit. Gold-score ties receive expected rank credit. Source: `run_retrieval.py`; @bandarkar2024belebele. {#tbl-belebele-passage-probe}
