"""Generate tbl-fertility (Ch 6) and tbl-context-window (Ch 11) from measured fertility.

Source: TurkicNLP paper results file tokenizer_metrics_corrected.csv, i.e. the 20 parallel
challenge sentences of the TurkicNLP paper (@hakimov2025turkicnlp), each word tokenised separately.
No values are extrapolated.
"""
from pathlib import Path
import csv

HERE = Path(__file__).parent
rows = list(csv.DictReader(open(HERE / 'data.csv', encoding='utf-8')))
T = ['qwen', 'llama', 'olmo', 'openai']

lines = ['| Language | Branch | Script | Qwen3.5 | LLaMA 3 | OLMo 3 | o200k_base |',
         '|----------|--------|:------:|:-------:|:-------:|:------:|:-------:|']
for r in rows:
    lines.append(f"| {r['language']} | {r['branch']} | {r['script']} | " +
                 ' | '.join(r[f'fert_{t}'] for t in T) + ' |')
lines += ['', ': Tokeniser fertility (mean tokens per word) of four LLM tokenisers on the 20 parallel '
          'challenge sentences of @hakimov2025turkicnlp, each word tokenised separately. Small samples '
          '(61–88 words per language): read the table as a diagnostic, not a benchmark. {#tbl-fertility}']
(HERE / 'output-fertility.md').write_text('\n'.join(lines), encoding='utf-8')

subset = ['eng', 'tur', 'kaz', 'kir', 'tat', 'uig']
lines = ['| Language | Fertility (best–worst) | Words in 4K window | Words in 32K window |',
         '|----------|:----------------------:|:------------------:|:-------------------:|']
for r in rows:
    if r['iso'] not in subset:
        continue
    vals = [float(r[f'fert_{t}']) for t in T]
    lo, hi = min(vals), max(vals)
    lines.append(f"| {r['language']} | {lo:.2f}–{hi:.2f} | {int(4096/hi):,}–{int(4096/lo):,} | "
                 f"{int(32768/hi):,}–{int(32768/lo):,} |")
lines += ['', ': Approximate number of words that fit into a context window, computed as window size divided '
          'by the fertility of the best and worst of the four tokenisers in @tbl-fertility. {#tbl-context-window}']
(HERE / 'output-context.md').write_text('\n'.join(lines), encoding='utf-8')
