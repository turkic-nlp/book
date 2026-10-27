"""N1-0: HPLT v3.0 size statistics for all Turkic languages.

Reads the HPLT v3.0 manifest (one JSON object per line), keeps the Turkic
subsets listed in ../common/turkic_languages.csv (plus rus_Cyrl and eng_Latn
as reference rows), sums shard sizes per Web Docs Scorer quality bin
(HEAD requests), and estimates words per character from the official
per-language samples file.

Outputs (in data/):
  hplt_v3_turkic.csv               one row per language / script variant
  hplt_v3_turkic_quality_bins.csv  compressed bytes per quality bin
  hplt_v3_manifest.jsonl           raw copy of the manifest (for pinning)

Usage:  python fetch_hplt_v3.py
Needs network access to data.hplt-project.org (not available in the
sandboxed shells used while drafting; the 2026-10-12 numbers were extracted
with the same logic in a browser, see data/hplt_v3_SOURCE.md).
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

import requests

MANIFEST = "https://data.hplt-project.org/three/sorted/manifest.json"
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
LANGS = HERE.parent / "common" / "turkic_languages.csv"
REFERENCE = {"rus_Cyrl": ("rus", "Russian (reference)"), "eng_Latn": ("eng", "English (reference)")}
LETTER_WORD = re.compile(r"[^\W\d_]+", re.UNICODE)  # letter-only words, as in the browser extraction

FIELDS = ["iso639_3", "language", "branch", "hplt_code", "script", "row_type", "present", "files",
          "bytes_compressed", "documents", "segments", "gemma3_tokens", "characters",
          "tokens_per_doc", "chars_per_token", "sample_docs", "sample_words_per_char",
          "est_words", "est_words_M", "top_bins_8_10_share_bytes"]


def load_manifest(session: requests.Session) -> tuple[dict[str, dict], str, str]:
    r = session.get(MANIFEST, timeout=120)
    r.raise_for_status()
    text = r.text
    (DATA / "hplt_v3_manifest.jsonl").write_text(text, encoding="utf-8")
    recs = [json.loads(line) for line in text.splitlines() if line.strip()]
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return {rec["name"]: rec for rec in recs}, sha, r.headers.get("Last-Modified", "")


def bin_sizes(session: requests.Session, urls: list[str]) -> dict[int, int]:
    out: dict[int, int] = defaultdict(int)
    for u in urls:
        b = int(u.rsplit("/", 1)[1].split("_", 1)[0])
        h = session.head(u, timeout=60, allow_redirects=True)
        h.raise_for_status()
        out[b] += int(h.headers.get("Content-Length", 0))
    return dict(out)


def words_per_char(session: requests.Session, samples_url: str) -> tuple[int, float]:
    s = session.get(samples_url, timeout=120).json()
    n = chars = words = 0
    for docs in s.get("samples", {}).values():
        for txt in docs:
            n += 1
            chars += len(txt)
            words += len(LETTER_WORD.findall(txt))
    return n, (words / chars if chars else float("nan"))


def main() -> None:
    DATA.mkdir(exist_ok=True)
    session = requests.Session()
    man, sha, last_mod = load_manifest(session)

    targets = []  # (iso, name, branch, code, row_type)
    with LANGS.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            codes = row["hplt_codes_to_check"].split(";")
            for i, code in enumerate(codes):
                targets.append((row["iso639_3"], row["language"], row["branch"], code,
                                "primary" if i == 0 else "script_variant"))
    for code, (iso, name) in REFERENCE.items():
        targets.append((iso, name, "—", code, "reference"))

    rows, bin_rows = [], []
    for iso, name, branch, code, typ in targets:
        r = dict(iso639_3=iso, language=name, branch=branch, hplt_code=code,
                 script=code.split("_")[1], row_type=typ, present=0)
        rec = man.get(code)
        if rec is not None:
            n, wpc = words_per_char(session, rec["samples"])
            est = rec["characters"] * wpc
            r.update(present=1, files=rec["files"], bytes_compressed=rec["bytes"],
                     documents=rec["documents"], segments=rec["segments"],
                     gemma3_tokens=rec["tokens"], characters=rec["characters"],
                     tokens_per_doc=f"{rec['t/d']:.1f}", chars_per_token=f"{rec['c/t']:.3f}",
                     sample_docs=n, sample_words_per_char=f"{wpc:.4f}",
                     est_words=f"{est:.0f}", est_words_M=f"{est / 1e6:.1f}")
            if typ != "reference":
                bins = bin_sizes(session, rec["urls"])
                total = sum(bins.values())
                assert total == rec["bytes"], (code, total, rec["bytes"])
                top = sum(v for b, v in bins.items() if b >= 8)
                r["top_bins_8_10_share_bytes"] = f"{top / total:.3f}"
                for b in sorted(bins):
                    bin_rows.append([code, b, bins[b], f"{bins[b] / total:.4f}"])
        rows.append(r)

    with (DATA / "hplt_v3_turkic.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    with (DATA / "hplt_v3_turkic_quality_bins.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["hplt_code", "wds_bin", "bytes_compressed", "share_of_language_bytes"])
        w.writerows(bin_rows)
    print(f"manifest sha256={sha} last-modified={last_mod} accessed={dt.date.today()}")


if __name__ == "__main__":
    main()
