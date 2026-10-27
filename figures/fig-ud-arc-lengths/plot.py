"""Plot frozen descriptive official-UD test statistics; regenerate table first."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
rows=list(csv.DictReader((ROOT/'tables/tbl-ud-arc-lengths/data.csv').open()))
rows.sort(key=lambda r:float(r['mean_distance']))
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
fig,ax=plt.subplots(figsize=(8,8))
y=list(range(len(rows)))
ax.hlines(y,[float(r['median_distance']) for r in rows],[float(r['p90_distance']) for r in rows],color='#b4c7d9',lw=2,label='Median to P90')
ax.scatter([float(r['mean_distance']) for r in rows],y,s=20,color='#174a75',label='Mean',zorder=3)
ax.set_yticks(y,[r['treebank'][3:] for r in rows]);ax.set_xlabel('Basic dependency distance (word positions)')
ax.set_title('Official UD 2.17 test sets: dependency distance')
ax.grid(axis='x',alpha=.2);ax.legend(loc='lower right',fontsize=8)
ax.spines[['top','right']].set_visible(False)
fig.tight_layout()
for ext in ('png','pdf','svg'):fig.savefig(HERE/f'figure.{ext}',dpi=180)
plt.close(fig)
