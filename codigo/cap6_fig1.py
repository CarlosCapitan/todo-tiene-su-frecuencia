import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras

import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
D=json.load(open(datos('chart_data.json')))
BLUE,ORANGE="#2a78d6","#eb6834"; INK,SEC,MUT,SURF="#0b0b0b","#52514e","#8a8984","#fcfcfb"
plt.rcParams.update({'figure.facecolor':SURF,'axes.facecolor':SURF,'font.size':9.5,
 'axes.edgecolor':'#d8d7d2','axes.labelcolor':SEC,'xtick.color':SEC,'ytick.color':SEC,
 'axes.spines.top':False,'axes.spines.right':False,'grid.color':'#eceae5','grid.linewidth':.8,
 'font.family':'DejaVu Sans'})
def clean(ax): ax.grid(True,alpha=.9,zorder=0); ax.set_axisbelow(True); ax.tick_params(length=3,width=.8)

fig=plt.figure(figsize=(11.5,8.4))
gs=fig.add_gridspec(2,2,height_ratios=[1.35,1],hspace=.40,wspace=.24,left=.075,right=.975,top=.855,bottom=.075)

ax=fig.add_subplot(gs[0,:]); clean(ax)
s=np.array(D['pg_sign']); m=np.array(D['pg_mag'])
ax.loglog(m[:,0],m[:,1],color=ORANGE,lw=1.7,solid_capstyle='round',label='Magnitud  log |retorno BTC 5 min|',zorder=3)
ax.loglog(s[:,0],s[:,1],color=BLUE,lw=1.9,solid_capstyle='round',label='Signo de la resolución (el "keystream")',zorder=4)
ax.axhline(1,color=MUT,lw=1,ls=(0,(4,3)),zorder=2)
ax.text(4e-5,.62,'nivel de ruido blanco',fontsize=8.4,color=MUT,va='center')
for lab,fm in [('24 h',D['pg_marks']['24h']),('7 d',D['pg_marks']['7d']),('1 h',D['pg_marks']['1h'])]:
    ax.axvline(fm,color=INK,lw=.9,alpha=.28,zorder=1)
    ax.text(fm,.055,' '+lab,fontsize=8.4,color=SEC,va='bottom')
ax.set_xlim(3e-5,.6); ax.set_ylim(.05,2200)
ax.set_xlabel('frecuencia   (ciclos por vela de 5 min)'); ax.set_ylabel('potencia espectral / mediana')
ax.legend(frameon=False,loc='upper right',fontsize=9.6,labelcolor=SEC,handlelength=1.6)
ax.annotate('pico semanal',xy=(D['pg_marks']['7d'],250),xytext=(.30,.90),textcoords='axes fraction',
    fontsize=9.4,color=ORANGE,fontweight='bold',arrowprops=dict(arrowstyle='-',color=ORANGE,lw=1,alpha=.8))
ax.annotate('pico diario',xy=(D['pg_marks']['24h'],42),xytext=(.475,.66),textcoords='axes fraction',
    fontsize=9.4,color=ORANGE,fontweight='bold',arrowprops=dict(arrowstyle='-',color=ORANGE,lw=1,alpha=.8))
ax.annotate('el signo es plano de extremo a extremo:\nninguna frecuencia destaca sobre el fondo',
    xy=(.02,.5),xytext=(.02,.13),textcoords='axes fraction',fontsize=9.6,color=BLUE,fontweight='bold')
ax.set_title('Un solo eje, dos series del MISMO mercado y los MISMOS instantes',
    color=INK,fontsize=10.5,loc='left',pad=10,fontweight='bold')

ax=fig.add_subplot(gs[1,0]); clean(ax)
h=np.array(D['hour_sign']); se=(1/np.sqrt(h[:,2])).mean()*100
ax.axhspan(50-2*se,50+2*se,color=BLUE,alpha=.11,lw=0,zorder=1)
ax.axhline(50,color=MUT,lw=1,zorder=2)
ax.plot(h[:,0],h[:,1]*100,color=BLUE,lw=2,marker='o',ms=4.5,mfc=SURF,mew=1.4,zorder=3)
ax.text(.03,.055,'banda de ruido ±2σ',transform=ax.transAxes,fontsize=8.4,color=BLUE)
ax.set_xlabel('hora del día (UTC)'); ax.set_ylabel('% de resoluciones "Up"')
ax.set_title('Signo por hora del día',color=INK,fontsize=10.5,loc='left',pad=15,fontweight='bold')
ax.text(0,1.04,'ninguna hora se sale del ruido',transform=ax.transAxes,fontsize=8.8,color=SEC)
ax.set_ylim(46.8,53.4); ax.set_xticks(range(0,24,4))

ax=fig.add_subplot(gs[1,1]); clean(ax)
mm=np.array(D['hour_mag'])
ax.plot(mm[:,0],mm[:,1],color=ORANGE,lw=2,marker='o',ms=4.5,mfc=SURF,mew=1.4,zorder=3)
ax.set_xlabel('hora del día (UTC)'); ax.set_ylabel('|retorno| mediano  (%)')
ax.set_title('Magnitud por hora del día',color=INK,fontsize=10.5,loc='left',pad=15,fontweight='bold')
ax.text(0,1.04,'el doble de volatilidad en la apertura de EE. UU.',transform=ax.transAxes,fontsize=8.8,color=SEC)
ax.set_xticks(range(0,24,4)); ax.set_ylim(.034,.094)
i0,i1=int(np.argmin(mm[:,1])),int(np.argmax(mm[:,1]))
ax.annotate(f'{mm[i1,1]:.3f} %',xy=(mm[i1,0],mm[i1,1]),xytext=(0,9),textcoords='offset points',ha='center',fontsize=8.8,color=ORANGE,fontweight='bold')
ax.annotate(f'{mm[i0,1]:.3f} %',xy=(mm[i0,0],mm[i0,1]),xytext=(0,-17),textcoords='offset points',ha='center',fontsize=8.8,color=ORANGE,fontweight='bold')

fig.text(.075,.955,'La asimetría central: el signo está "cifrado", la magnitud no',fontsize=15,color=INK,fontweight='bold')
fig.text(.075,.917,'Polymarket «BTC Up or Down 5m» · 70.729 resoluciones reales · 18-dic-2025 → 5-sep-2026',fontsize=9.3,color=SEC)
fig.savefig(figuras('fig6_1_signo_magnitud.png'),dpi=170); print("ok")
