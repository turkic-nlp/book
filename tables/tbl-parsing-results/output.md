| Language | Matched words (n) | Stanza UPOS | Stanza UAS | Stanza LAS | Multilingual UPOS | Multilingual UAS | Multilingual LAS |
| --- | --- | --- | --- | --- | --- | --- | --- |
| *Gold UD-Turkic parallel test sets — supervised* |  |  |  |  |  |  |  |
| Turkish | 877 | 85.1 | 75.3 | 63.5 | **86.9** | **84.5** | **70.1** |
| Azerbaijani | 869 | 84.9 | 72.3 | 60.8 | **87.0** | **76.2** | **64.5** |
| Kazakh | 851 | 87.9 | 67.4 | 57.4 | **88.8** | **71.9** | **59.9** |
| Kyrgyz | 1,166 | 71.1 | 50.2 | 29.4 | **79.0** | **63.9** | **41.0** |
| Tatar | 29 | **86.2** | 69.2 | 57.7 | 79.3 | **77.8** | **70.4** |
| Uyghur | 758 | 76.9 | 77.1 | 62.3 | **79.7** | **81.5** | **66.7** |
| Uzbek | 905 | 71.8 | 67.2 | 46.3 | **87.6** | **81.5** | **68.3** |
| *Gold UD-Turkic parallel test sets — zero-shot*^†^ |  |  |  |  |  |  |  |
| Karakalpak^†^ | 235 | — | — | — | 77.5 | 61.7 | 45.8 |
| Kumyk^†^ | 144 | — | — | — | 78.5 | 60.4 | 45.5 |
| Sakha^†^ | 16 | — | — | — | 93.8 | 60.0 | 46.7 |
| *Silver test sets*^‡^ |  |  |  |  |  |  |  |
| Turkmen^‡^ | 825 | **86.1** | 76.8 | 67.8 | 85.8 | **77.9** | **68.4** |
| Bashkir^‡^ | 814 | 87.0 | 72.8 | 62.5 | **89.6** | **75.8** | **63.8** |

: POS tagging and dependency parsing from the frozen local manuscript table of 13 October 2026 (`tables/tbl-parsing-results/source.tex`), associated with @hakimov2025turkicnlp. This snapshot differs from the public arXiv table in some cells and sample sizes. Both backends receive the same automatic tokenisation. These are *conditional* scores, not the official tokenisation-aware CoNLL 2018 LAS F1: UPOS is computed over the n words whose boundaries match gold, and UAS/LAS additionally require matched gold and predicted heads, so tokenisation errors drop out of the denominator. ^†^Zero-shot with proxy embeddings: Karakalpak → Uzbek, Kumyk → Tatar, Sakha → Bashkir. ^‡^Silver test sets (translated and automatically annotated); these mainly measure agreement with the process that produced them. Tatar (29 words), Sakha (16), Kumyk (144) and Karakalpak (235) are qualitative examples, not grounds for ranking. Bold: higher score of the two backends. The source’s aggregate is omitted because it mixes gold and silver rows. {#tbl-parsing-results}
