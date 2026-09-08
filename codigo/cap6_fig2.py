import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras

import json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
D=json.load(open(datos('chart_data.json')))
BLUE,ORANGE,AQUA="#2a78d6","#eb6834","#1baf7a"; INK,SEC,MUT,SURF="#0b0b0b","#52514e","#8a8984","#fcfcfb"
plt.rcParams.update({'figure.facecolor':SURF,'axes.facecolor':SURF,'font.size':9.5,
 'axes.edgecolor':'#d8d7d2','axes.labelcolor':SEC,'xtick.color':SEC,'ytick.color':SEC,
 'axes.spines.top':False,'axes.spines.right':False,'grid.color':'#eceae5','grid.linewidth':.8,
 'font.family':'DejaVu Sans'})
def clean(ax): ax.grid(True,alpha=.9,zorder=0); ax.set_axisbelow(True); ax.tick_params(length=3,width=.8)
fig=plt.figure(figsize=(11.5,8.6))
gs=fig.add_gridspec(2,2,hspace=.52,wspace=.30,left=.075,right=.975,top=.86,bottom=.075)

# --- complejidad lineal ---
ax=fig.add_subplot(gs[0,0]); clean(ax)
r=np.array(D['lc_real']); q=np.array(D['lc_rand']); l=np.array(D['lc_lfsr'])
ax.loglog(r[:,0],np.maximum(r[:,1],1),color=BLUE,lw=2.2,label='Polymarket BTC 5m (real)',zorder=4)
ax.loglog(q[:,0],np.maximum(q[:,1],1),color=MUT,lw=5,alpha=.45,label='ruido pseudoaleatorio',zorder=2,solid_capstyle='round')
ax.loglog(l[:,0],np.maximum(l[:,1],1),color=ORANGE,lw=2,label='LFSR de 32 bits (predecible)',zorder=4)
ax.set_xlabel('bits observados  n'); ax.set_ylabel('complejidad lineal  L(n)')
ax.set_title('Perfil de complejidad lineal (Berlekamp-Massey)',color=INK,fontsize=10.5,loc='left',pad=19,fontweight='bold')
ax.text(0,1.04,'¿existe un LFSR corto que genere la secuencia?',transform=ax.transAxes,fontsize=8.8,color=SEC)
ax.set_ylim(3,2.2e5)
ax.legend(frameon=False,loc='center right',fontsize=8.6,labelcolor=SEC,handlelength=1.8,bbox_to_anchor=(1.03,.30))
ax.annotate('se estanca en 32:\nrota para siempre',xy=(4e2,32),xytext=(.33,.09),textcoords='axes fraction',
    fontsize=8.8,color=ORANGE,fontweight='bold',ha='center',arrowprops=dict(arrowstyle='-',color=ORANGE,lw=1))
ax.annotate('L = 35.365 = n/2 exacto\n(indistinguible del ruido)',xy=(70729,35365),xytext=(.06,.90),
    textcoords='axes fraction',fontsize=8.8,color=BLUE,fontweight='bold',va='top',
    arrowprops=dict(arrowstyle='-',color=BLUE,lw=1))

# --- autocorrelacion ---
ax=fig.add_subplot(gs[0,1]); clean(ax)
a=np.array(D['acf']); se=D['acf_se']
ax.axhspan(-2*se,2*se,color=BLUE,alpha=.11,lw=0,zorder=1)
ax.axhline(0,color=MUT,lw=1,zorder=2)
ax.vlines(a[:,0],0,a[:,1],color=BLUE,lw=1.1,alpha=.85,zorder=3)
ax.plot([1],[a[0,1]],marker='o',ms=7,color=ORANGE,mec=SURF,mew=1.6,zorder=5)
ax.annotate(f'lag 1:  r = {a[0,1]:+.4f}   (z = −4,1)\nel ÚNICO hallazgo real',xy=(1,a[0,1]),
    xytext=(.22,.10),textcoords='axes fraction',fontsize=9.2,color=ORANGE,fontweight='bold',
    arrowprops=dict(arrowstyle='-',color=ORANGE,lw=1))
ax.text(.97,.09,'banda ±2σ',transform=ax.transAxes,fontsize=8.4,color=BLUE,ha='right')
ax.set_xlabel('desfase (lag), en velas de 5 min'); ax.set_ylabel('autocorrelación  r')
ax.set_title('Autocorrelación del signo',color=INK,fontsize=10.5,loc='left',pad=19,fontweight='bold')
ax.text(0,1.04,'300 desfases; nada sobresale salvo el primero',transform=ax.transAxes,fontsize=8.8,color=SEC)
ax.set_xlim(0,301); ax.set_ylim(-.021,.021)

# --- walsh ---
ax=fig.add_subplot(gs[1,0]); clean(ax)
w=np.array(D['walsh_hist'])
ax.fill_between(w[:,0],0,w[:,1],color=BLUE,alpha=.28,lw=0,zorder=3)
ax.plot(w[:,0],w[:,1],color=BLUE,lw=1.7,zorder=4,label='65.535 máscaras lineales (real)')
xs=np.linspace(-5,5,300); ax.plot(xs,np.exp(-xs**2/2)/np.sqrt(2*np.pi),color=ORANGE,lw=1.7,ls=(0,(4,2)),zorder=5,label='normal teórica si es aleatorio')
ax.set_xlabel('correlación de cada máscara con el bit siguiente  (z)'); ax.set_ylabel('densidad')
ax.set_title('Espectro de Walsh-Hadamard',color=INK,fontsize=10.5,loc='left',pad=19,fontweight='bold')
ax.text(0,1.04,'criptoanálisis lineal: ¿alguna combinación de 16 bits predice el siguiente?',transform=ax.transAxes,fontsize=8.8,color=SEC)
ax.set_ylim(0,.52)
ax.legend(frameon=False,loc='upper left',fontsize=8.6,labelcolor=SEC,handlelength=1.8)
ax.text(.985,.60,("máx |z| real       = %.2f\nmáx |z| control  = %.2f\numbral de ruido = %.2f"
    % (D['walsh_max'],D['walsh_max_rand'],D['walsh_thr'])).replace('.',','),
    transform=ax.transAxes,fontsize=8.8,color=SEC,ha='right',va='top',linespacing=1.6,family='DejaVu Sans Mono')
ax.text(.985,.30,'las dos curvas se superponen:\nninguna máscara predice nada',transform=ax.transAxes,
    fontsize=9,color=BLUE,ha='right',va='top',fontweight='bold',linespacing=1.4)

# --- comisiones ---
ax=fig.add_subplot(gs[1,1]); clean(ax)
f=D['fees']; lab=[x[0] for x in f]; val=[x[1] for x in f]; y=np.arange(len(f))[::-1]
ax.barh(y,val,height=.5,color=ORANGE,zorder=3)
edge=D['edge']['out']*100
ax.axvline(edge,color=BLUE,lw=2.2,zorder=5)
ax.annotate(('ventaja real fuera de\nmuestra:  %.2f %%'%edge).replace('.',','),xy=(edge,-.42),
    xytext=(1.35,-.45),fontsize=9.2,color=BLUE,fontweight='bold',va='center',
    arrowprops=dict(arrowstyle='-',color=BLUE,lw=1))
for yy,v,l in zip(y,val,lab):
    ax.text(v+.08,yy,f'{v:.2f} %'.replace('.',','),va='center',fontsize=9,color=SEC,fontweight='bold')
    ax.text(.06,yy+.42,l.replace('Comisión ','').replace('Horquilla','Horquilla'),va='bottom',fontsize=8.6,color=SEC)
ax.set_yticks([]); ax.set_ylim(-.7,len(f)-.05)
ax.set_xlabel('coste por operación  (% del nocional)'); ax.set_xlim(0,4.6)
ax.set_title('La barrera que lo anula todo',color=INK,fontsize=10.5,loc='left',pad=19,fontweight='bold')
ax.text(0,1.04,'la ventaja hallada frente al coste de operar',transform=ax.transAxes,fontsize=8.8,color=SEC)
ax.grid(axis='y',alpha=0)

fig.text(.075,.955,'La secuencia supera todos los tests que rompen una clave débil',fontsize=15,color=INK,fontweight='bold')
fig.text(.075,.918,'Batería criptoanalítica NIST SP 800-22 + Walsh-Hadamard sobre 70.729 bits reales',fontsize=9.3,color=SEC)
fig.savefig(figuras('fig6_2_cripto.png'),dpi=170); print("ok")
