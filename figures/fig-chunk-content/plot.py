"""Plot measured FLORES-200 chunk capacity from the frozen N2-4 results."""
from pathlib import Path
import csv,shutil,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'experiments/common'))
from bookgen import EXP
source=EXP/'n2_meaning/results/chunk_content_measured.csv'
rows=list(csv.DictReader(source.open()));shutil.copy2(source,HERE/'data.csv')
langs=list(dict.fromkeys(r['lang'] for r in rows));names={r['lang']:r['language'] for r in rows}
models=[('qwen','Qwen3.5','#2b6f92','o'),('llama','Llama 3','#d67c28','s'),('olmo','OLMo 3','#7962a6','^'),('o200k','o200k_base','#299278','D')]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
fig,axes=plt.subplots(1,2,figsize=(9.1,6.3),sharey=True)
for ax,key,label in zip(axes,['words_per_chunk','sentences_per_chunk'],['Mean whitespace-delimited words/chunk','Mean aligned sentence rows/chunk']):
    for j,(model,title,color,marker) in enumerate(models):
        points={r['lang']:float(r[key]) for r in rows if r['tokenizer']==model}
        ax.scatter([points[l] for l in langs],[i+(j-1.5)*.16 for i in range(len(langs))],s=25,color=color,marker=marker,label=title,zorder=3)
    ax.set_xlabel(label);ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True);ax.spines[['top','right','left']].set_visible(False);ax.tick_params(axis='y',length=0)
    ax.set_xlim(left=0)
axes[0].set_yticks(range(len(langs)),[names[l]+(' (reference)' if l=='eng_Latn' else '') for l in langs]);axes[0].invert_yaxis()
handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=4,frameon=False,bbox_to_anchor=(.57,.005))
fig.suptitle('Measured text capacity under a 512-token ceiling',fontsize=12,y=.98)
fig.tight_layout(rect=(0,.065,1,.96))
for ext in ['png','pdf','svg']:fig.savefig(HERE/f'output.{ext}',dpi=200)
plt.close(fig)
print('Generated fig-chunk-content')
