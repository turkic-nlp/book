"""Schematic ordering constraints; examples are alternatives, not one word."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
HERE=Path(__file__).parent
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42})
nom=[('Root / stem','ev “house”'),('Derivation','-lik'),('Number','-ler'),('Possession','-im'),('Case','-de'),('Predication','-dir; construction-dependent')]
verb=[('Root / stem','yaz- “write”'),('Voice','-ıl- (passive)'),('Ability / negation','-(y)Abil-; negative -A-mA-'),('Tense / aspect / mood','-dı (past), among other forms'),('Person / number','-lar (3PL); 3SG may be zero')]
fig,ax=plt.subplots(figsize=(8,6.5));ax.set(xlim=(0,8),ylim=(-.9,6.9));ax.axis('off')
for x,slots,title,color in [(0.1,nom,'Nominal ordering','#28618c'),(4.15,verb,'Verbal ordering','#287458')]:
    ax.text(x+1.8,6.6,title,ha='center',weight='bold',color=color,fontsize=12)
    for i,(label,example) in enumerate(slots):
        y=5.5-i
        ax.add_patch(FancyBboxPatch((x,y),3.55,.7,boxstyle='round,pad=.04',facecolor='#f4f7f9',edgecolor=color))
        ax.text(x+1.775,y+.47,label,ha='center',weight='bold',fontsize=10)
        ax.text(x+1.775,y+.17,example,ha='center',fontsize=9)
        if i<len(slots)-1: ax.annotate('',xy=(x+1.775,y-.24),xytext=(x+1.775,y-.04),arrowprops={'arrowstyle':'->','color':color})
ax.text(4,-.52,'Slots constrain order; not every slot is overt or freely combinable.\nNominalised verbs continue with nominal inflection.',ha='center',va='center',fontsize=9,color='#444444')
fig.savefig(HERE/'output.pdf',bbox_inches='tight');fig.savefig(HERE/'output.png',dpi=180,bbox_inches='tight');plt.close(fig)
