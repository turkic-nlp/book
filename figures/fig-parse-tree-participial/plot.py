"""Regenerate this figure from its documented inputs; run with Python + matplotlib."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from book_assets import *
HERE = Path(__file__).resolve().parent

r=rows(HERE/"data.csv")
fig,axs=plt.subplots(2,1,figsize=(8.5,5.7))
for ax,lang in zip(axs,["English","Turkish"]):
    tokens=[d for d in r if d["language"]==lang]
    heads={int(d["token_id"]):int(d["head"]) for d in tokens}
    assert sorted(heads)==list(range(1,len(tokens)+1)) and list(heads.values()).count(0)==1
    for node in heads:
        seen=set()
        while node:
            assert node not in seen and node in heads
            seen.add(node);node=heads[node]
    ax.set(xlim=(.45,len(tokens)+.6),ylim=(-.45,2.5));ax.axis("off")
    ax.text(.5,2.35,lang,fontsize=13,weight="bold",color=INK)
    for d in tokens:
        child,head=int(d["token_id"]),int(d["head"])
        ax.text(child,-.13,d["form"],ha="center",va="top",fontsize=12,color=INK)
        if head==0:
            ax.annotate("root",xy=(child,0),xytext=(child,1.4),ha="center",color=BLUE,fontsize=9,arrowprops=dict(arrowstyle="->",color=BLUE))
            continue
        height=.5+.38*abs(child-head)
        # Two cubic Beziers: exact apex at label, vertical tangents at each token.
        mid=(head+child)/2
        path=MplPath([(head,.02),(head,height),(mid-(child-head)*.2,height),(mid,height),(mid+(child-head)*.2,height),(child,height),(child,.02)],
                     [MplPath.MOVETO]+[MplPath.CURVE4]*6)
        ax.add_patch(FancyArrowPatch(path=path,arrowstyle="->",mutation_scale=10,color=BLUE,lw=1.1))
        ax.text(mid,height+.045,d["deprel"],ha="center",va="bottom",fontsize=9,color=INK,bbox=dict(facecolor="white",edgecolor="none",pad=.3))
fig.text(.5,.025,"Basic dependencies: one head per word; arrows run from head to dependent. No enhanced ref edges.",ha="center",fontsize=9,color=INK)
fig.tight_layout(rect=(0,.07,1,1),h_pad=1.8);save(fig,HERE)
