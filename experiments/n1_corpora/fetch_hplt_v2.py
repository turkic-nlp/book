"""N1-0: HPLT v2.0 size statistics for the Turkic languages.

The v2.0 download page (https://hplt-project.org/datasets/v2.0) embeds a JSON
blob with, per language, three blocks: `cleaned`, `collectionsMerged`
(= deduplicated) and `annotated`, each with docs / text_wcwords /
text_chars / text_bytes. This script parses that blob.

Usage:
  python fetch_hplt_v2.py            # fetch page (needs network) and write CSV
  python fetch_hplt_v2.py --offline  # rebuild CSV from data/raw/hplt_v2_raw.tsv
                                     # (values extracted in a browser on 2026-10-12)
Output: data/hplt_v2_turkic.csv
"""
from __future__ import annotations
import csv, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
LANGS = HERE.parent / "common" / "turkic_languages.csv"
PAGE = "https://hplt-project.org/datasets/v2.0"
SOURCE = "HPLT v2.0 download page (hplt-project.org/datasets/v2.0), accessed 2026-10-12"
REFERENCE = {"rus_Cyrl": ("rus", "Russian (reference)", ""), "eng_Latn": ("eng", "English (reference)", "")}
RAW_FIELDS = ["dedup_docs", "dedup_words", "dedup_chars", "dedup_bytes",
              "cleaned_docs", "cleaned_words", "cleaned_chars", "cleaned_bytes"]


def parse_page(html: str) -> dict[str, dict[str, int]]:
    h = html.replace('\\"', '"')
    out = {}
    for m in re.finditer(r'\{"lang":"([a-z]{3}_[A-Za-z]{4})"(.*?)"languageName":"([^"]*)"', h, re.S):
        code, body = m.group(1), m.group(2)
        blocks = {k: dict((f, int(v)) for f, v in re.findall(r'"(\w+)":"?(\d+)"?', b))
                  for k, b in re.findall(r'"(\w+)":\{([^{}]*)\}', body)}
        d, c = blocks.get("collectionsMerged", {}), blocks.get("cleaned", {})
        out[code] = {"dedup_docs": d.get("docs"), "dedup_words": d.get("text_wcwords"),
                     "dedup_chars": d.get("text_chars"), "dedup_bytes": d.get("text_bytes"),
                     "cleaned_docs": c.get("docs"), "cleaned_words": c.get("text_wcwords"),
                     "cleaned_chars": c.get("text_chars"), "cleaned_bytes": c.get("text_bytes")}
    return out


def load_raw() -> dict[str, dict[str, int]]:
    rows = csv.DictReader(open(DATA / "raw" / "hplt_v2_raw.tsv", encoding="utf-8"), delimiter="\t")
    return {r["hplt_code"]: {k: int(r[k]) for k in RAW_FIELDS} for r in rows}


def main() -> None:
    if "--offline" in sys.argv:
        stats = load_raw()
    else:
        import requests
        stats = parse_page(requests.get(PAGE, timeout=120).text)
    langs = list(csv.DictReader(open(LANGS, encoding="utf-8")))
    fields = ["iso639_3", "language", "branch", "hplt_code", "row_type", "present"] + RAW_FIELDS + ["source"]
    rows = []
    for L in langs:
        codes = [c for c in L["hplt_codes_to_check"].split(";") if c]
        hit = [c for c in codes if c in stats]
        for c in (hit or codes[:1] or [""]):
            s = stats.get(c, {})
            rows.append({"iso639_3": L["iso639_3"], "language": L["language"], "branch": L["branch"],
                         "hplt_code": c, "row_type": "primary", "present": int(bool(s)),
                         **{k: s.get(k, "") for k in RAW_FIELDS}, "source": SOURCE})
    for c, (iso, name, br) in REFERENCE.items():
        rows.append({"iso639_3": iso, "language": name, "branch": br, "hplt_code": c, "row_type": "reference",
                     "present": int(c in stats), **{k: stats.get(c, {}).get(k, "") for k in RAW_FIELDS},
                     "source": SOURCE})
    with open(DATA / "hplt_v2_turkic.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f"wrote {len(rows)} rows; present: {sum(r['present'] for r in rows)}")


if __name__ == "__main__":
    main()
