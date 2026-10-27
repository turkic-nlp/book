"""Regenerate this figure from its documented inputs; run with Python + matplotlib."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from book_assets import *
HERE = Path(__file__).resolve().parent

import unicodedata
r=rows(HERE/"data.csv")
fig,ax=canvas((8,5.5),(0,10,0,10))
ax.text(0,9.8,"Selected Unicode blocks used in Turkic text",fontsize=14,color=INK,weight="bold")
for i,d in enumerate(r):
    for c in d["codepoints"].split():
        assert int(d["start"],16) <= int(c,16) <= int(d["end"],16)
        assert unicodedata.name(chr(int(c,16)))
    y=8.8-i*1.04
    ax.add_patch(FancyBboxPatch((0,y-.43),10,.88,boxstyle="round,pad=.02",facecolor=PALE if i%2==0 else "#f7f8f8",edgecolor="none"))
    ax.text(.16,y+.1,d["block"],fontsize=10,color=INK,va="center",weight="bold")
    ax.text(.16,y-.2,f'U+{d["start"]}-U+{d["end"]}',fontsize=9,color="#54636e",va="center")
    ax.text(5.05,y,d["examples"],fontsize=12,color=INK,va="center")
ax.text(0,.05,"Unicode 17.0. Selected examples only; band widths do not represent block sizes.",fontsize=9,color=INK)
save(fig,HERE)
