"""Shared helpers for the table/figure generators of the new chapters.

Every generator copies its input from experiments/**/{data,results}/ into its
own data.csv (with a `source` column) and writes either the real output or,
if the experiment has not been run yet, a red placeholder. A placeholder
never defines a #tbl-/#fig- label.
"""
from __future__ import annotations
import csv
import shutil
from pathlib import Path

BOOK = Path(__file__).resolve().parents[2]
EXP = BOOK / "experiments"


def read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str] | None = None) -> None:
    fields = fields or (list(rows[0].keys()) if rows else ["source"])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)


def copy_input(src: Path, here: Path, name: str = "data.csv") -> bool:
    """Copy an experiment output next to the generator. Returns False if it does not exist yet."""
    if not src.exists():
        return False
    shutil.copyfile(src, here / name)
    return True


def md_table(header: list[str], align: list[str], rows: list[list[str]], caption: str, label: str) -> str:
    sep = {"l": "---", "r": "--:", "c": ":-:"}
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(sep[a] for a in align) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    out += ["", f": {caption} {{#{label}}}"]
    return "\n".join(out) + "\n"


def placeholder_md(here: Path, label: str, experiment: str, needs: str, run: str) -> str:
    txt = (f"::: {{.placeholder}}\n**`{label}` not generated yet ({experiment}).** Needs `{needs}`. "
           f"Run `{run}`, then re-run `{(here / ('generate.py' if label.startswith('tbl') else 'plot.py')).relative_to(BOOK)}`.\n:::\n")
    (here / "output.md").write_text(txt, encoding="utf-8")
    print(txt)
    return txt


def placeholder_figure(here: Path, label: str, experiment: str, needs: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.5, 2.2))
    ax.axis("off")
    ax.text(0.5, 0.5, f"PLACEHOLDER: {label}\n{experiment} not run yet\nneeds {needs}",
            ha="center", va="center", color="#C00000", fontsize=11)
    fig.savefig(here / "output.png", dpi=150); fig.savefig(here / "output.pdf"); plt.close(fig)
    (here / "STATUS.txt").write_text(f"placeholder: {experiment} has not produced {needs}\n", encoding="utf-8")
    print(f"[placeholder] {label}: waiting for {needs}")


def fmt_count(v) -> str:
    if v in ("", None, "0", 0):
        return "—"
    if v == "present":
        return "✓"
    v = float(v)
    if v >= 1e9:
        return f"{v/1e9:.1f}B"
    if v >= 1e6:
        return f"{v/1e6:.1f}M"
    if v >= 1e3:
        return f"{v/1e3:.0f}k"
    return f"{int(v)}"


def save(fig, here: Path) -> None:
    (here / "STATUS.txt").unlink(missing_ok=True)
    fig.savefig(here / "output.png", dpi=200); fig.savefig(here / "output.pdf")
