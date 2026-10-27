"""Extract and run the Python code blocks of the book's chapters.

Blocks of one chapter run in order in a shared namespace, so later blocks can
use names defined earlier (as a reader would run them). Each chapter runs in a
fresh temporary working directory.

Usage:
    python scripts/run_code_blocks.py                       # all chapters
    python scripts/run_code_blocks.py chapters/05-*.qmd     # selected chapters
    python scripts/run_code_blocks.py --include-training    # also run blocks that train models
    python scripts/run_code_blocks.py --list                # only list the blocks

Blocks are skipped (not failed) when they
  * train a model (contain ``.train(`` or ``trainer.``) unless --include-training,
  * contain a placeholder such as ``load_dataset("...")`` or ``TUMLU_ID = "..."``,
  * call an LLM server (``llm_base_url=`` / ``llm_provider=``) unless --include-llm,
  * need the speech environment (``SpeechRecognizer`` / ``from_audio``) unless --include-asr.
A block that fails makes later blocks of the same chapter that depend on it fail too;
the report shows the first error of each block.

Exit code: number of failed blocks (0 = all run or skipped).
"""
from __future__ import annotations

import argparse
import contextlib
import glob
import io
import os
import re
import sys
import tempfile
import time
import traceback
import types
from pathlib import Path

BOOK = Path(__file__).resolve().parents[1]
BLOCK_RE = re.compile(r"^```(?:python|\{python\})\s*\n(.*?)^```", re.S | re.M)


def blocks(path: Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    out = []
    for m in BLOCK_RE.finditer(text):
        line = text.count("\n", 0, m.start()) + 1
        out.append((line, m.group(1)))
    return out


def skip_reason(code: str, args) -> str | None:
    if not args.include_training and (".train(" in code or "trainer." in code):
        return "trains a model"
    if '"..."' in code or "'...'" in code:
        return "contains a placeholder"
    if not args.include_llm and ("llm_base_url=" in code or "llm_provider=" in code or "**llm" in code):
        return "needs an LLM server"
    if not args.include_asr and ("SpeechRecognizer" in code or "from_audio" in code):
        return "needs the speech environment"
    return None


def run_chapter(path: Path, args) -> list[tuple[int, str, str]]:
    results = []
    module = types.ModuleType("__book__")        # dataclasses need a real module
    sys.modules["__book__"] = module
    ns = module.__dict__
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        try:
            for line, code in blocks(path):
                reason = skip_reason(code, args)
                if reason:
                    results.append((line, "SKIP", reason))
                    continue
                buf = io.StringIO()
                t0 = time.time()
                try:
                    with contextlib.redirect_stdout(buf):
                        exec(compile(code, f"{path.name}:{line}", "exec"), ns)
                    results.append((line, "OK", f"{time.time() - t0:.1f}s"))
                except Exception as exc:  # noqa: BLE001
                    tb = traceback.extract_tb(exc.__traceback__)
                    where = next((f"{fr.filename}:{fr.lineno}" for fr in reversed(tb)
                                  if fr.filename.startswith(path.name)), "")
                    results.append((line, "FAIL", f"{type(exc).__name__}: {str(exc)[:160]} {where}"))
                if args.verbose and buf.getvalue():
                    print(buf.getvalue())
        finally:
            os.chdir(cwd)
    return results


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--include-training", action="store_true")
    ap.add_argument("--include-llm", action="store_true")
    ap.add_argument("--include-asr", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true", help="print the blocks' output")
    args = ap.parse_args()

    files = [Path(f) for pat in (args.files or [str(BOOK / "chapters" / "*.qmd")])
             for f in sorted(glob.glob(pat))]
    failed = 0
    for path in files:
        bl = blocks(path)
        if not bl:
            continue
        print(f"\n== {path.name} ({len(bl)} blocks)")
        if args.list:
            for line, code in bl:
                print(f"  line {line}: {code.strip().splitlines()[0][:80]}")
            continue
        for line, status, info in run_chapter(path, args):
            print(f"  {status:<4} line {line:<5} {info}")
            failed += status == "FAIL"
    print(f"\n{failed} block(s) failed")
    return failed


if __name__ == "__main__":
    sys.exit(main())
