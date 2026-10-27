"""Regenerate every table and figure of the book from its data.

Runs tables/*/generate.py and figures/*/plot.py (each in its own folder, as the book's convention expects) and reports which
ones produced real output and which are still red placeholders because their experiment has not been run.

Usage: python scripts/make_all.py [--only tbl-hplt-releases fig-cc-turkic-share ...] [--new-chapters]
  --new-chapters  only the generators of the new chapters (3b, 8b, 11b, 11c), i.e. those that use experiments/common/bookgen.py
Optional first step (network): python experiments/n1_corpora/fetch_corpus_sizes.py && python experiments/n1_corpora/build_availability.py
"""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--only", nargs="*"); ap.add_argument("--new-chapters", action="store_true"); ap.add_argument("--list", action="store_true", help="List selected active generators without running them"); a = ap.parse_args()
    gens = sorted(BOOK.glob("tables/*/generate.py")) + sorted(BOOK.glob("figures/*/plot.py"))
    if a.only:
        gens = [g for g in gens if g.parent.name in a.only]
    if a.new_chapters:
        gens = [g for g in gens if "bookgen" in g.read_text(encoding="utf-8")]
    deprecated = [g for g in gens if (g.parent / "DEPRECATED.md").exists()]
    gens = [g for g in gens if g not in deprecated]
    if deprecated:
        print("skipped deprecated: " + ", ".join(g.parent.name for g in deprecated))
    if a.only:
        unknown = set(a.only) - {g.parent.name for g in gens + deprecated}
        if unknown:
            ap.error("unknown or filtered asset IDs: " + ", ".join(sorted(unknown)))
    if a.list:
        for g in gens:
            print(g.parent.name)
        return
    real, placeholder, failed = [], [], []
    for g in gens:
        r = subprocess.run([sys.executable, g.name], cwd=g.parent, capture_output=True, text=True)
        name = g.parent.name
        if r.returncode != 0:
            failed.append((name, r.stderr.strip().splitlines()[-1] if r.stderr.strip() else "?"))
        elif (g.parent / "STATUS.txt").exists() or ((g.parent / "output.md").exists() and
                                                     (g.parent / "output.md").read_text(encoding="utf-8").startswith("::: {.placeholder}")):
            placeholder.append(name)
        else:
            real.append(name)
    print(f"real output ({len(real)}): " + ", ".join(real))
    print(f"placeholder, experiment not run ({len(placeholder)}): " + ", ".join(placeholder))
    if failed:
        print(f"FAILED ({len(failed)}):"); [print(f"  {n}: {e}") for n, e in failed]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
