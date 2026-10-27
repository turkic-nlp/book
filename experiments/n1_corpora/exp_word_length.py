"""N1-3 step 4: distribution of mean word length (and stop-word ratio) per sentence, Turkic vs. English, on parallel text.

Sources (--source):
  tuecl  : TueCL UD test sets (parallel translations of the same English sentences; `# text` and `# text[en]`),
           local copy in ../../../turkicnlp/tuecl_files/ (default; available offline)
  flores : FLORES+ devtest via `datasets` (openlanguagedata/flores_plus; gated, needs HF login)
Output : results/word_length_<source>.csv  lang, sent_id, n_words, mean_word_len, max_word_len, n_long_words (>10 letters), source
"""
from __future__ import annotations
import argparse, csv, re, unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
RES = HERE / "results"
TUECL = HERE.parents[2] / "turkicnlp" / "tuecl_files"
TUECL_CODES = {"tr": "tur", "az": "aze", "tk": "tuk", "kk": "kaz", "ky": "kir", "tt": "tat", "ba": "bak", "kaa": "kaa",
               "kum": "kum", "uz": "uzb", "ug": "uig", "sah": "sah"}
FLORES = {"tur": "tur_Latn", "aze": "azj_Latn", "tuk": "tuk_Latn", "kaz": "kaz_Cyrl", "kir": "kir_Cyrl", "tat": "tat_Cyrl",
          "bak": "bak_Cyrl", "crh": "crh_Latn", "uzb": "uzn_Latn", "uig": "uig_Arab", "azb": "azb_Arab", "eng": "eng_Latn"}
WORD = re.compile(r"[^\W\d_]+")


def stats(text: str) -> dict:
    w = WORD.findall(unicodedata.normalize("NFC", text))
    return {"n_words": len(w), "mean_word_len": sum(map(len, w)) / len(w) if w else 0, "max_word_len": max(map(len, w), default=0),
            "n_long_words": sum(len(x) > 10 for x in w)}


def from_tuecl():
    rows, eng = [], {}
    for f in sorted(TUECL.glob("*_tuecl-ud-test.conllu")):
        lang = TUECL_CODES.get(f.name.split("_")[0])
        if not lang:
            continue
        sid = None
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith("# sent_id = "):
                sid = line.split("= ", 1)[1].strip()
            elif line.startswith("# text = "):
                rows.append({"lang": lang, "sent_id": sid, **stats(line[9:]), "source": f"TueCL {f.name}"})
            elif line.startswith("# text[en] = ") and sid not in eng:
                eng[sid] = line[13:]
    rows += [{"lang": "eng", "sent_id": k, **stats(v), "source": "TueCL # text[en] (deduplicated by sent_id)"} for k, v in eng.items()]
    return [r for r in rows if r["n_words"]]


def from_flores():
    from datasets import load_dataset
    rows = []
    for lang, code in FLORES.items():
        ds = load_dataset("openlanguagedata/flores_plus", code, split="devtest")  # VERIFY config naming
        rows += [{"lang": lang, "sent_id": ex.get("id", i), **stats(ex["text"]), "source": f"FLORES+ devtest {code}"} for i, ex in enumerate(ds)]
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--source", choices=["tuecl", "flores"], default="tuecl"); a = ap.parse_args()
    rows = from_tuecl() if a.source == "tuecl" else from_flores()
    RES.mkdir(exist_ok=True)
    with open(RES / f"word_length_{a.source}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["lang", "sent_id", "n_words", "mean_word_len", "max_word_len", "n_long_words", "source"]); w.writeheader(); w.writerows(rows)
    from collections import defaultdict
    by = defaultdict(list)
    for r in rows: by[r["lang"]].append(r["mean_word_len"])
    for l, v in sorted(by.items(), key=lambda x: sum(x[1]) / len(x[1])):
        print(f"{l}\t{len(v)}\t{sum(v)/len(v):.2f}")


if __name__ == "__main__":
    main()
