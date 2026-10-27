"""Regenerate this figure from its documented inputs; run with Python + matplotlib."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from book_assets import *
HERE = Path(__file__).resolve().parent

# Author-created evaluation workflow, not an empirical ranking of methods.
fig,ax=canvas((8.5,7.3))
box(ax,5,9.35,"Define task, target variety and held-out evaluation",height=.72,width=8.4)
box(ax,5,8.0,"Target task labels available?",decision=True,width=4.5,height=1.2)
arrow(ax,[(5,8.96),(5,8.63)])
box(ax,2.45,6.5,"Fine-tune a multilingual baseline\nCompare alternatives when data permits",width=4.65,height=1.05,fontsize=9.5)
box(ax,7.55,6.5,"Evaluate zero-shot / proxy transfer\nCollect a small target evaluation set",width=4.65,height=1.05,fontsize=9.5)
arrow(ax,[(2.75,8),(2.45,8),(2.45,7.05)],"Yes",(2.45,7.5))
arrow(ax,[(7.25,8),(7.55,8),(7.55,7.05)],"No",(7.55,7.5))
box(ax,5,4.7,"Check script compatibility\nPreserve originals; test conversion when needed",width=8.2,height=1.05)
arrow(ax,[(2.45,5.95),(2.45,5.5),(5,5.5),(5,5.25)])
arrow(ax,[(7.55,5.95),(7.55,5.5),(5,5.5)])
box(ax,5,2.9,"Compare a rule-based or hybrid option\nwhen a suitable finite-state transducer exists",width=8.2,height=1.05)
arrow(ax,[(5,4.15),(5,3.45)])
box(ax,5,1.1,"Select using held-out quality, coverage, cost\nand analysis of errors in the target variety",width=8.2,height=1.05)
arrow(ax,[(5,2.35),(5,1.65)])
ax.text(5,.02,"Evaluation is required on both branches; FST availability is an optional comparison.",ha="center",fontsize=9,color=INK)
save(fig,HERE)
