"""Experiment B: does the Common Turkic Alphabet (CTS) narrow the tokenization gap?

For the 20 parallel challenge sentences of 20 Turkic languages we compare LLM
tokenizer fertility (tokens per word, words = ``[^\\W_]+`` and every word is
tokenized separately, exactly as in ``arxiv_paper/tokenizer_analysis``) for
  * the native script,
  * the national Latin orthography (where one exists), and
  * the Common Turkic Alphabet (CTS) produced by TurkicNLP.
We also measure cross-lingual surface overlap between the parallel sentence
sets (character-trigram Dice and word-type Jaccard, averaged over all language
pairs) in native script and in CTS.

Tokenizers are read from local Hugging Face caches (no network access needed):
  --qwen  .../Qwen3.5-35B-A3B-FP8 snapshot dir
  --llama .../Meta-Llama-3-8B snapshot dir
  --olmo  .../Olmo-3-1025-7B snapshot dir
  --openai (optional) uses tiktoken o200k_base if its BPE file is cached.

Usage:  python exp_cts_tokenizers.py   (paths are auto-detected)
"""

from __future__ import annotations

import argparse
import csv
import glob
import itertools
import os
import statistics

from common import LANG_ORDER, RESULTS, load_challenge, save_json, words
from turkicnlp.scripts import Script
from turkicnlp.scripts.detector import _char_to_script
from turkicnlp.scripts.transliterator import Transliterator

NATIVE = {"uig": Script.PERSO_ARABIC,
          **{l: Script.LATIN for l in ["tur", "aze", "tuk", "gag", "crh", "kaa", "uzb"]}}
NATIONAL_LATIN = {"kaz": Script.CYRILLIC, "tat": Script.CYRILLIC, "uig": Script.PERSO_ARABIC}


def snapshot(pattern: str) -> str | None:
    home = os.path.expanduser("~")
    for root in (f"{home}/mnt", f"{home}/.cache/huggingface/hub"):
        c = glob.glob(f"{root}/{pattern}/snapshots/*/tokenizer.json")
        if c:
            return os.path.dirname(sorted(c)[-1])
    return None


class HFTok:
    def __init__(self, path: str):
        from tokenizers import Tokenizer
        self.tok = Tokenizer.from_file(os.path.join(path, "tokenizer.json"))

    def n(self, word: str) -> int:
        return len(self.tok.encode(word, add_special_tokens=False).ids)


class TikTok:
    def __init__(self, enc: str = "o200k_base"):
        import tiktoken
        self.tok = tiktoken.get_encoding(enc)

    def n(self, word: str) -> int:
        return len(self.tok.encode(word))


def fertility(tok, text: str) -> float:
    ws = words(text)
    return sum(tok.n(w) for w in ws) / len(ws)


def trigram_dice(a: str, b: str) -> float:
    def grams(t):
        t = " ".join(w.lower() for w in words(t))
        return {t[i:i + 3] for i in range(len(t) - 2)}
    ga, gb = grams(a), grams(b)
    return 2 * len(ga & gb) / (len(ga) + len(gb))


def word_jaccard(a: str, b: str) -> float:
    wa, wb = {w.lower() for w in words(a)}, {w.lower() for w in words(b)}
    return len(wa & wb) / len(wa | wb)


def latin_share(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    return sum(_char_to_script(c) == Script.LATIN for c in letters) / len(letters)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qwen", default=snapshot("models--Qwen--Qwen3.5-35B-A3B-FP8"))
    ap.add_argument("--llama", default=snapshot("models--meta-llama--Meta-Llama-3-8B"))
    ap.add_argument("--olmo", default=snapshot("models--allenai--Olmo-3-1025-7B"))
    ap.add_argument("--openai", action="store_true", help="also run tiktoken o200k_base (GPT-5.2)")
    args = ap.parse_args()

    toks = {}
    for name in ("qwen", "llama", "olmo"):
        p = getattr(args, name)
        if p:
            toks[name] = HFTok(p)
        else:
            print(f"[warn] tokenizer {name} not found; skipping")
    if args.openai:
        try:
            toks["openai"] = TikTok()
        except Exception as exc:  # network / cache missing
            print(f"[warn] tiktoken o200k_base unavailable: {exc}")

    challenge = load_challenge()
    texts = {}  # lang -> {condition: text}
    purity = {}
    for lang in LANG_ORDER:
        sents = [s for _, s in challenge[lang]]
        native = " ".join(sents)
        src = NATIVE.get(lang, Script.CYRILLIC)
        cts = " ".join(Transliterator(lang, src, Script.COMMON_TURKIC).transliterate(s) for s in sents)
        texts[lang] = {"native": native, "cts": cts}
        if lang in NATIONAL_LATIN:
            texts[lang]["latin"] = " ".join(
                Transliterator(lang, src, Script.LATIN).transliterate(s) for s in sents)
        elif src == Script.LATIN:
            texts[lang]["latin"] = native
        purity[lang] = latin_share(cts)

    rows = []
    for lang in LANG_ORDER:
        for cond, text in texts[lang].items():
            for tname, tok in toks.items():
                rows.append({"tokenizer": tname, "lang": lang, "condition": cond,
                             "native_script": str(NATIVE.get(lang, Script.CYRILLIC)),
                             "word_count": len(words(text)),
                             "fertility": fertility(tok, text)})
    with open(RESULTS / "cts_fertility.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)

    def mean(tname, cond, langs):
        v = [r["fertility"] for r in rows if r["tokenizer"] == tname and r["condition"] == cond
             and r["lang"] in langs]
        return statistics.mean(v) if v else None

    non_latin = [l for l in LANG_ORDER if NATIVE.get(l, Script.CYRILLIC) != Script.LATIN]
    latin = [l for l in LANG_ORDER if NATIVE.get(l, Script.CYRILLIC) == Script.LATIN]
    summary = {}
    for tname in toks:
        summary[tname] = {
            "non_latin_native": mean(tname, "native", non_latin),
            "non_latin_cts": mean(tname, "cts", non_latin),
            "latin_native": mean(tname, "native", latin),
            "latin_cts": mean(tname, "cts", latin),
            "all_native": mean(tname, "native", LANG_ORDER),
            "all_cts": mean(tname, "cts", LANG_ORDER),
            "tur_native": mean(tname, "native", ["tur"]),
        }

    # cross-lingual surface overlap between parallel sentence sets
    def overlap(cond, fn, pairs):
        return statistics.mean(fn(texts[a][cond], texts[b][cond]) for a, b in pairs)
    all_pairs = list(itertools.combinations(LANG_ORDER, 2))
    cross_script = [(a, b) for a, b in all_pairs
                    if NATIVE.get(a, Script.CYRILLIC) != NATIVE.get(b, Script.CYRILLIC)]
    ov = {}
    for label, pairs in (("all_pairs", all_pairs), ("cross_script_pairs", cross_script)):
        ov[label] = {"n_pairs": len(pairs)}
        for cond in ("native", "cts"):
            ov[label][f"char3_dice_{cond}"] = overlap(cond, trigram_dice, pairs)
            ov[label][f"word_jaccard_{cond}"] = overlap(cond, word_jaccard, pairs)
    tur_pairs = {b: {"native": trigram_dice(texts["tur"]["native"], texts[b]["native"]),
                     "cts": trigram_dice(texts["tur"]["cts"], texts[b]["cts"])}
                 for b in LANG_ORDER if b != "tur"}

    res = {"summary": summary, "overlap": ov, "dice_with_turkish": tur_pairs,
           "cts_latin_share": purity, "tokenizers": list(toks),
           "per_language": rows}
    save_json("cts_tokenizers.json", res)

    print("CTS Latin-letter share (min):", min(purity.values()), min(purity, key=purity.get))
    print(f"\n{'lang':5}" + "".join(f"{t+':'+c:>15}" for t in toks for c in ("native", "latin", "cts")))
    for lang in LANG_ORDER:
        line = f"{lang:5}"
        for t in toks:
            for c in ("native", "latin", "cts"):
                v = [r["fertility"] for r in rows if r["tokenizer"] == t and r["lang"] == lang and r["condition"] == c]
                line += f"{v[0]:15.2f}" if v else f"{'-':>15}"
        print(line)
    print("\nsummary:")
    for t, s in summary.items():
        print(t, {k: round(v, 3) for k, v in s.items()})
    print("\noverlap:", ov)


if __name__ == "__main__":
    main()
