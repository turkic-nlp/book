| System | Correct / 797 | Accuracy (%) |
|---|--:|--:|
| Qwen2.5-1.5B-Instruct | 226 | 28.36 |
| Development-majority letter D | 304 | 38.14 |
| Uniform choice (expectation) | Expected | 25.00 |

: Measured zero-shot constrained-letter Qwen score on 797 valid TUMLU-mini Kazakh test items; two malformed items of 799 are excluded and recorded. The letter-D baseline is selected from the 40 development items, not the test answers. Uniform accuracy is an expectation, not a model run. Source: `run_tumlu.py`; @isbarov2025tumlu. {#tbl-tumlu-pretrained-probe}
