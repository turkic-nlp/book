"""N1-0: merge all corpus size snapshots into one long table for the Turkic languages.

Inputs : data/hplt_v3_turkic.csv, data/hplt_v2_turkic.csv, data/raw/*
Outputs: data/corpus_availability_long.csv   one row per (language, corpus, subset)
         data/corpus_availability_docs.csv   wide: documents (or pages/articles) per corpus
         data/cc_turkic_share.csv            Common Crawl %pages per crawl, Turkic CLD2 codes

The measures differ by corpus and are kept in separate columns: documents,
words (whitespace words), tokens (with tokens_unit). Never compare tokens
across corpora: each corpus counts them with a different tokenizer.
"""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA, RAW = HERE / "data", HERE / "data" / "raw"
LANGS = list(csv.DictReader(open(HERE.parent / "common" / "turkic_languages.csv", encoding="utf-8")))
ISO = {L["iso639_3"]: L for L in LANGS}
ACC = "accessed 2026-10-12"

# corpus code -> iso639_3 of the book's language list
TWO = {"tr": "tur", "az": "aze", "azb": "azb", "tk": "tuk", "gag": "gag", "kk": "kaz", "ky": "kir", "tt": "tat",
       "ba": "bak", "crh": "crh", "kaa": "kaa", "nog": "nog", "kum": "kum", "krc": "krc", "uz": "uzb", "ug": "uig",
       "sah": "sah", "alt": "alt", "tyv": "tyv", "kjh": "kjh", "cv": "chv"}
THREE_CC = {"tur": "tur", "aze": "aze", "tuk": "tuk", "kaz": "kaz", "kir": "kir", "tat": "tat", "bak": "bak",
            "uzb": "uzb", "uig": "uig", "chv": "chv", "sah": "sah"}
FW2 = {"azj": "aze", "uzn": "uzb"}  # FineWeb2 macro/individual codes that differ from ours

CORPORA = ["HPLT v1.2", "HPLT v2.0", "HPLT v3.0", "FineWeb2", "CulturaX", "mC4", "CC-100", "Wikipedia"]
FIELDS = ["iso639_3", "language", "branch", "corpus", "subset", "documents", "words", "tokens", "tokens_unit",
          "bytes", "bytes_kind", "note", "source"]


def tsv(name):
    return list(csv.DictReader(open(RAW / name, encoding="utf-8"), delimiter="\t"))


def num(x):
    try:
        return float(x) if "." in str(x) else int(x)
    except (TypeError, ValueError):
        return ""


def row(iso, corpus, subset, source, **kw):
    L = ISO.get(iso, {"language": iso, "branch": ""})
    r = {k: "" for k in FIELDS}
    r.update(iso639_3=iso, language=L["language"], branch=L["branch"], corpus=corpus, subset=subset, source=source)
    r.update({k: v for k, v in kw.items() if v not in (None, "")})
    return r


def collect():
    out = []
    for r in tsv("hplt_v1_2_raw.tsv"):
        if r["lang"] in TWO:
            out.append(row(TWO[r["lang"]], "HPLT v1.2", r["lang"], f"hplt-project.org/datasets/v1.2, {ACC}",
                           documents=num(r["dedup_docs"]), words=num(r["dedup_words"]), note="deduplicated release"))
    for r in csv.DictReader(open(DATA / "hplt_v2_turkic.csv", encoding="utf-8")):
        if r["row_type"] == "primary" and r["present"] == "1":
            out.append(row(r["iso639_3"], "HPLT v2.0", r["hplt_code"], f"hplt-project.org/datasets/v2.0, {ACC}",
                           documents=num(r["dedup_docs"]), words=num(r["dedup_words"]), bytes=num(r["dedup_bytes"]),
                           bytes_kind="utf8_text", note="deduplicated release"))
    for r in csv.DictReader(open(DATA / "hplt_v3_turkic.csv", encoding="utf-8")):
        if r["row_type"] == "primary" and r["present"] == "1":
            out.append(row(r["iso639_3"], "HPLT v3.0", r["hplt_code"], f"data.hplt-project.org/three/sorted/manifest.json, {ACC}",
                           documents=num(r["documents"]), tokens=num(r["gemma3_tokens"]), tokens_unit="Gemma 3",
                           bytes=num(r["bytes_compressed"]), bytes_kind="zstd", note="words not reported"))
    for r in csv.DictReader(open(RAW / "fineweb2_language_distribution.csv", encoding="utf-8")):
        if r["split"] != "train" or r["family"] != "Turkic" or r["subset"].endswith("_removed"):
            continue
        iso = FW2.get(r["code"], r["code"])
        if iso not in ISO:
            continue  # cjs (Shor), kdr (Karaim), uzs (Southern Uzbek) are listed in the SOURCE note
        out.append(row(iso, "FineWeb2", r["subset"], f"github.com/huggingface/fineweb-2 language distribution CSV, {ACC}",
                       documents=num(r["documents"]), words=num(r["words"]), bytes=num(r["utf8_bytes"]),
                       bytes_kind="utf8_text", note="filtered train split"))
    for r in tsv("culturax_card.tsv"):
        if r["iso"] in TWO:
            out.append(row(TWO[r["iso"]], "CulturaX", r["iso"], f"huggingface.co/datasets/uonlp/CulturaX card, {ACC}",
                           documents=num(r["documents"]), tokens=num(r["tokens"]),
                           tokens_unit="CulturaX (Llama)" if r["tokens"] else ""))
    files = {r["iso"]: r for r in tsv("mc4_hf_allenai_c4_files.tsv")}
    for r in tsv("mc4_mt5_table6.tsv"):
        if r["iso"] in TWO:
            f = files.get(r["iso"], {})
            out.append(row(TWO[r["iso"]], "mC4", r["iso"], "Xue et al. 2021 (mT5), Table 6; HF allenai/c4 file sizes, " + ACC,
                           documents=round(float(r["pages_M"]) * 1e6), tokens=round(float(r["tokens_B"]) * 1e9),
                           tokens_unit="mT5 SentencePiece", bytes=num(f.get("bytes_gzip")), bytes_kind="gzip_json",
                           note="pages and tokens rounded in the paper (mC4 v3.0.1 as used for mT5)"))
    for r in tsv("cc100_xlmr_table6.tsv"):
        if r["iso"] in TWO:
            out.append(row(TWO[r["iso"]], "CC-100", r["iso"], "Conneau et al. 2020 (XLM-R), Table 6; data.statmt.org/cc-100, " + ACC,
                           tokens=round(float(r["tokens_M"]) * 1e6), tokens_unit="XLM-R SentencePiece",
                           bytes=round(float(r["size_GiB"]) * 2**30), bytes_kind="utf8_text",
                           note="documents not reported"))
    for r in tsv("wikipedia_siteinfo.tsv"):
        if r["wiki"] in TWO:
            out.append(row(TWO[r["wiki"]], "Wikipedia", r["wiki"] + "wiki", f"MediaWiki siteinfo statistics API, {ACC}",
                           documents=num(r["articles"]), note="content articles, incl. bot-generated stubs"))
    return out


def main():
    rows = collect()
    with open(DATA / "corpus_availability_long.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(rows)
    docs = defaultdict(lambda: defaultdict(int))
    tok_only = defaultdict(set)
    for r in rows:
        if r["documents"] != "":
            docs[r["iso639_3"]][r["corpus"]] += int(r["documents"])
        elif r["tokens"] != "":
            tok_only[r["iso639_3"]].add(r["corpus"])
    with open(DATA / "corpus_availability_docs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["iso639_3", "language", "branch", "primary_script"] + CORPORA + ["n_corpora", "source"])
        for L in LANGS:
            vals = []
            for c in CORPORA:
                if c in docs[L["iso639_3"]]:
                    vals.append(docs[L["iso639_3"]][c])
                elif c in tok_only[L["iso639_3"]]:
                    vals.append("present")  # CC-100 reports tokens only
                else:
                    vals.append(0)
            w.writerow([L["iso639_3"], L["language"], L["branch"], L["primary_script"]] + vals
                       + [sum(1 for v in vals if v), "see corpus_availability_long.csv (per-corpus sources)"])
    cc = [r for r in csv.DictReader(open(RAW / "cc_crawl_languages.csv", encoding="utf-8"))
          if r["primary_language"] in THREE_CC or r["primary_language"] in ("rus",)]
    with open(DATA / "cc_turkic_share.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["crawl", "cld2_code", "iso639_3", "pages", "pct_pages", "source"])
        for r in cc:
            if r["crawl"] < "CC-MAIN-2017":
                continue  # language annotation starts with CC-MAIN-2018-39; earlier rows are <unknown>
            w.writerow([r["crawl"], r["primary_language"], THREE_CC.get(r["primary_language"], r["primary_language"]),
                        r["pages"], r["%pages/crawl"],
                        f"commoncrawl/cc-crawl-statistics plots/languages.csv (CLD2), {ACC}"])
    print(f"{len(rows)} long rows; languages with any corpus: {sum(1 for L in LANGS if docs[L['iso639_3']] or tok_only[L['iso639_3']])}")


if __name__ == "__main__":
    main()
