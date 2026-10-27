"""Regenerate this figure from its documented inputs; run with Python + matplotlib."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from book_assets import *
HERE = Path(__file__).resolve().parent

# Longest-match lookup kernel. Contextual/case rules belong to a versioned mapping layer.
fig,ax=canvas((8.5,8))
box(ax,4.6,9.45,"Input text and a versioned mapping\nRequire non-empty mapping keys",width=6.5,height=.9)
box(ax,4.6,8.15,"i = 0; output = empty\nM = maximum key length (0 for an empty mapping)",width=6.5,height=.9,fontsize=9.5)
arrow(ax,[(4.6,8.97),(4.6,8.63)])
box(ax,4.6,6.85,"i < len(text)?",decision=True,width=3.8,height=1)
arrow(ax,[(4.6,7.67),(4.6,7.38)])
box(ax,8.8,6.85,"Return\noutput",width=1.8,height=.85)
arrow(ax,[(6.52,6.85),(7.86,6.85)],"No",(7.18,7.05))
box(ax,4.6,5.45,"Try key lengths M, ..., 1 at position i\nChoose the longest matching key",width=6.5,height=.9)
arrow(ax,[(4.6,6.33),(4.6,5.93)],"Yes",(4.95,6.13))
box(ax,4.6,4.13,"Match found?",decision=True,width=3.8,height=1)
arrow(ax,[(4.6,4.97),(4.6,4.66)])
box(ax,2.7,2.55,"Append mapped value\ni += matched key length",width=3.5,height=1,fontsize=9.5)
box(ax,7.1,2.55,"Copy text[i] unchanged\ni += 1",width=3.5,height=1,fontsize=9.5)
arrow(ax,[(2.68,4.13),(2.7,4.13),(2.7,3.08)],"Yes",(2.35,3.62))
arrow(ax,[(6.52,4.13),(7.1,4.13),(7.1,3.08)],"No",(7.45,3.62))
arrow(ax,[(2.7,2.02),(2.7,1.3),(4.6,1.3)])
arrow(ax,[(7.1,2.02),(7.1,1.3),(4.6,1.3)])
arrow(ax,[(4.6,1.3),(.35,1.3),(.35,6.85),(2.68,6.85)])
ax.text(5,.35,"Lookup kernel only: contextual spelling, normalisation and case handling\nrequire explicit policies outside this loop.",ha="center",fontsize=9,linespacing=1.5,color=INK)
save(fig,HERE)
