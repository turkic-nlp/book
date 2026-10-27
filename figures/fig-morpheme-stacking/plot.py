"""Morpheme stacking: Turkish konuşturamadıklarımızdan.

Treat konuş as one lexical stem and split inability into a + ma, following
Chapter 2's explicitly stated surface-segmentation convention.
"""
from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

mpl.rcParams.update({
    'font.family': 'serif', 'font.size': 10,
    'figure.dpi': 150, 'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.08,
})
OUT = Path(__file__).parent

# (surface, gloss, role in the suffix chain)
morphemes = [
    ('konuş', 'SPEAK', 'stem'),
    ('tur', 'CAUS', 'verbal'),
    ('a', 'ABIL', 'verbal'),
    ('ma', 'NEG', 'verbal'),
    ('dık', 'NMLZ', 'nominaliser'),
    ('lar', 'PL', 'nominal'),
    ('ımız', 'POSS.1PL', 'nominal'),
    ('dan', 'ABL', 'nominal'),
]
COLORS = {
    'stem': '#e08080',
    'verbal': '#4682b4',
    'nominaliser': '#c69232',
    'nominal': '#3cb371',
}

box_w, box_h, gap = 0.95, 0.55, 0.07
width = len(morphemes) * (box_w + gap) - gap
fig, ax = plt.subplots(figsize=(8.4, 2.45))
ax.set_xlim(-0.15, width + 0.15)
ax.set_ylim(-0.85, 1.35)
ax.axis('off')

for i, (surface, gloss, role) in enumerate(morphemes):
    x = i * (box_w + gap)
    ax.add_patch(mpatches.FancyBboxPatch(
        (x, 0), box_w, box_h, boxstyle='round,pad=0.035',
        facecolor=COLORS[role], edgecolor='white', linewidth=1.2,
    ))
    ax.text(x + box_w/2, box_h/2, surface, ha='center', va='center',
            fontsize=12, fontweight='bold', color='white')
    ax.text(x + box_w/2, -0.12, gloss, ha='center', va='top',
            fontsize=8.5, color='#333333')

word = '-'.join(surface for surface, _, _ in morphemes)
ax.text(width/2, 1.15, word, ha='center', va='center',
        fontsize=13, style='italic', color='#222222')
ax.text(width/2, 0.83, 'from/among those whom we could not get to speak',
        ha='center', va='center', fontsize=10, color='#444444')
handles = [mpatches.Patch(color=COLORS[key], label=label) for key, label in [
    ('stem', 'Lexical stem'), ('verbal', 'Verbal suffixes'),
    ('nominaliser', 'Nominaliser'), ('nominal', 'Nominal suffixes'),
]]
ax.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, 0),
          frameon=False, ncol=4, fontsize=8.5)
fig.tight_layout()
fig.savefig(OUT / 'output.pdf')
fig.savefig(OUT / 'output.png', dpi=180)
plt.close(fig)
print('Saved output.pdf and output.png')
