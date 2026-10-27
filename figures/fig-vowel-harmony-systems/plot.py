"""Regenerate this figure from its documented inputs; run with Python + matplotlib."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from book_assets import *
HERE = Path(__file__).resolve().parent

r=rows(HERE/"data.csv"); assert len(r)==4
fig,ax=canvas((9,5.4),(0,10,0,10))
ax.text(0,9.7,"Harmony patterns: speech, suffixes and spelling",fontsize=14,weight="bold",color=INK)
for i,d in enumerate(r):
    x=(i%2)*5.15; y=8.85-(i//2)*4.2
    ax.add_patch(FancyBboxPatch((x,y-3.65),4.85,3.65,boxstyle="round,pad=.03",facecolor=PALE,edgecolor="#bed2dd"))
    ax.text(x+.18,y-.48,d["language"],fontsize=13,weight="bold",color=BLUE)
    ax.text(x+.18,y-1.12,"Front/back",fontsize=9,weight="bold",color=INK)
    ax.text(x+.18,y-1.53,d["front_back"],fontsize=10,color=INK)
    ax.text(x+.18,y-2.06,"Rounding",fontsize=9,weight="bold",color=INK)
    ax.text(x+.18,y-2.47,d["rounding"],fontsize=10,color=INK)
    ax.text(x+.18,y-3.03,d["note"],fontsize=9,color=INK,va="center",linespacing=1.5)
ax.text(0,.12,"Qualitative comparison, not a vowel inventory. Source: Johanson (2021), pp. 305-315.",fontsize=9,color=INK)
save(fig,HERE)
