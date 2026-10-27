"""N1-0: refresh the raw per-language size snapshots for the other corpora.

Each function writes one file in data/raw/. The 2026-10-12 snapshots in
data/raw/ were produced with this logic (some via a browser because the
sandboxed shell could not reach the host; see data/corpus_sizes_SOURCE.md).

  fineweb2   GitHub CSV  huggingface/fineweb-2/fineweb2-language-distribution.csv
  cc         GitHub CSV  commoncrawl/cc-crawl-statistics/plots/languages.csv (CLD2 primary language)
  mc4_files  HF API      allenai/c4 tree multilingual/ (gzip bytes per language)
  wikipedia  MediaWiki   action=query&meta=siteinfo&siprop=statistics per wiki
  hplt_v1_2  page JSON   hplt-project.org/datasets/v1.2

Hand-copied (paper / dataset-card tables; no machine-readable source):
  raw/mc4_mt5_table6.tsv    mT5 paper (Xue et al. 2021), Table 6
  raw/cc100_xlmr_table6.tsv XLM-R paper (Conneau et al. 2020), Table 6 + data.statmt.org/cc-100 sizes
  raw/culturax_card.tsv     huggingface.co/datasets/uonlp/CulturaX dataset card table

Usage: python fetch_corpus_sizes.py [fineweb2 cc mc4_files wikipedia hplt_v1_2]
"""
from __future__ import annotations
import csv, re, sys
from collections import defaultdict
from pathlib import Path
import requests

RAW = Path(__file__).resolve().parent / "data" / "raw"
WIKIS = ["tr", "az", "azb", "ba", "crh", "cv", "gag", "kaa", "kk", "krc", "ky", "sah", "tt", "tk",
         "tyv", "ug", "uz", "alt", "kjh", "nog", "kum", "ru", "en"]


def fineweb2():
    u = "https://raw.githubusercontent.com/huggingface/fineweb-2/main/fineweb2-language-distribution.csv"
    (RAW / "fineweb2_language_distribution.csv").write_bytes(requests.get(u, timeout=120).content)


def cc():
    u = "https://raw.githubusercontent.com/commoncrawl/cc-crawl-statistics/master/plots/languages.csv"
    (RAW / "cc_crawl_languages.csv").write_bytes(requests.get(u, timeout=120).content)


def mc4_files():
    url = "https://huggingface.co/api/datasets/allenai/c4/tree/main/multilingual?limit=1000"
    agg = defaultdict(lambda: [0, 0])
    while url:
        r = requests.get(url, timeout=120); r.raise_for_status()
        for f in r.json():
            m = re.search(r"c4-([a-zA-Z-]+?)(-validation)?\.tfrecord-\d+-of-\d+\.json\.gz$", f["path"])
            if m:
                k = (m.group(1), "validation" if m.group(2) else "train")
                agg[k][0] += 1; agg[k][1] += f.get("size", 0)
        url = r.links.get("next", {}).get("url")
    with open(RAW / "mc4_hf_allenai_c4_files.tsv", "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t"); w.writerow(["iso", "split", "files", "bytes_gzip"])
        for (iso, split), (n, b) in sorted(agg.items()):
            if split == "train" and iso in {"az", "kk", "ky", "tr", "uz", "ru", "en"}:
                w.writerow([iso, split, n, b])


def wikipedia():
    with open(RAW / "wikipedia_siteinfo.tsv", "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t"); w.writerow(["wiki", "articles", "pages", "edits", "activeusers"])
        for c in WIKIS:
            try:
                s = requests.get(f"https://{c}.wikipedia.org/w/api.php", timeout=30, params={
                    "action": "query", "meta": "siteinfo", "siprop": "statistics", "format": "json"}).json()["query"]["statistics"]
                w.writerow([c, s["articles"], s["pages"], s["edits"], s["activeusers"]])
            except Exception:
                pass  # wiki does not exist (e.g. kjh, nog, kum on 2026-10-12)


def hplt_v1_2():
    h = requests.get("https://hplt-project.org/datasets/v1.2", timeout=120).text.replace('\\"', '"')
    pat = re.compile(r'\{"lang":\{"value":"([^"]+)","label":"([^"]+)"\},"raw":\{"words":(\d+),"documents":(\d+),"size":"([^"]+)"\},'
                     r'"dedup":\{"words":(\d+),"documents":(\d+),"size":"([^"]+)"\},"cleaned":\{"words":(\d+),"documents":(\d+),"size":"([^"]+)"\}')
    keep = {"az", "kk", "ky", "tr", "tt", "uz", "ru", "en"}
    with open(RAW / "hplt_v1_2_raw.tsv", "w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(["lang", "label", "raw_words", "raw_docs", "raw_size", "dedup_words", "dedup_docs", "dedup_size",
                    "cleaned_words", "cleaned_docs", "cleaned_size"])
        for m in pat.finditer(h):
            if m.group(1) in keep:
                w.writerow(m.groups())


if __name__ == "__main__":
    for name in (sys.argv[1:] or ["fineweb2", "cc", "mc4_files", "wikipedia", "hplt_v1_2"]):
        globals()[name](); print("refreshed", name)
