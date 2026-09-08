"""Figura 1.1 — cuatro pruebas declaran aleatorio al LFSR; una lo rompe."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras

import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
import bateria as B

BLUE,ORANGE,CTL="#2a78d6","#eb6834","#8a9498"
INK,SEC,MUT,SURF="#0f1518","#4b565b","#7c878c","#f7f8f7"
plt.rcParams.update({'figure.facecolor':SURF,'axes.facecolor':SURF,'font.size':9.5,
 'axes.edgecolor':'#d9e1e3','axes.labelcolor':SEC,'xtick.color':SEC,'ytick.color':SEC,
 'axes.spines.top':False,'axes.spines.right':False,'grid.color':'#eaf0f1','grid.linewidth':.8,
 'font.family':'DejaVu Sans'})
def clean(ax): ax.grid(True,alpha=.9,zorder=0); ax.set_axisbelow(True); ax.tick_params(length=3,width=.8)

N=70000
rng=np.random.default_rng(7)
seq={'LFSR de 32 bits':B.lfsr(N),'Aleatorio verdadero':rng.integers(0,2,N).astype(np.int8)}

fig=plt.figure(figsize=(12,8.6))
gs=fig.add_gridspec(2,2,hspace=.52,wspace=.26,left=.075,right=.975,top=.845,bottom=.075)

# --- 1. espectro ---
ax=fig.add_subplot(gs[0,0]); clean(ax)
for (nm,b),col,lw in zip(seq.items(),[BLUE,CTL],[1.6,4.5]):
    x=2*b.astype(float)-1
    I=np.abs(np.fft.rfft(x))[1:]**2; I/=np.median(I)
    f=np.arange(1,len(I)+1)/N
    ed=np.logspace(np.log10(f[0]),np.log10(f[-1]),90)
    idx=np.digitize(f,ed)-1
    pts=[(np.exp(np.log(f[idx==k]).mean()),I[idx==k].mean()) for k in range(90) if (idx==k).sum()>=3]
    ax.loglog(*zip(*pts),color=col,lw=lw,alpha=.55 if lw>3 else 1,
              label=nm,solid_capstyle='round',zorder=3 if lw<3 else 2)
ax.axhline(1,color=MUT,lw=1.2,ls=(0,(4,3)))
ax.set_xlabel('frecuencia (ciclos por bit)'); ax.set_ylabel('potencia / mediana')
ax.set_ylim(.1,10)
ax.set_title('1 · Espectro de potencia',color=INK,fontsize=11.5,loc='left',pad=22,fontweight='bold')
ax.text(0,1.055,'plano. Las dos curvas se superponen.',transform=ax.transAxes,fontsize=9,color=SEC)
ax.legend(frameon=False,fontsize=9,labelcolor=SEC,loc='lower left',handlelength=1.6)

# --- 2. autocorrelacion ---
ax=fig.add_subplot(gs[0,1]); clean(ax)
se=1/np.sqrt(N)
ax.axhspan(-2*se,2*se,color=BLUE,alpha=.12,lw=0,zorder=1)
ac=B.autocorr(seq['LFSR de 32 bits'],200)
ax.vlines(np.arange(1,201),0,ac[1:201],color=BLUE,lw=1.2,zorder=3)
ax.axhline(0,color=MUT,lw=1)
ax.set_xlabel('desfase (lag)'); ax.set_ylabel('autocorrelación r')
ax.set_ylim(-.018,.018); ax.set_xlim(0,201)
ax.set_title('2 · Autocorrelación',color=INK,fontsize=11.5,loc='left',pad=22,fontweight='bold')
ax.text(0,1.055,'todo dentro de la banda de ruido ±2σ',transform=ax.transAxes,fontsize=9,color=SEC)

# --- 3. Walsh ---
ax=fig.add_subplot(gs[1,0]); clean(ax)
z=B.walsh_lineal(seq['LFSR de 32 bits'],16)[1:]
h,ed=np.histogram(z,bins=70,range=(-5,5),density=True)
c=(ed[:-1]+ed[1:])/2
ax.fill_between(c,0,h,color=BLUE,alpha=.28,lw=0,zorder=3)
ax.plot(c,h,color=BLUE,lw=1.8,zorder=4,label='65.535 máscaras del LFSR')
xs=np.linspace(-5,5,300)
ax.plot(xs,np.exp(-xs**2/2)/np.sqrt(2*np.pi),color=ORANGE,lw=1.8,ls=(0,(4,2)),zorder=5,
        label='normal teórica si fuera aleatorio')
ax.set_xlabel('correlación de cada máscara con el bit siguiente (z)'); ax.set_ylabel('densidad')
ax.set_ylim(0,.52)
ax.set_title('3 · Criptoanálisis lineal (Walsh-Hadamard)',color=INK,fontsize=11.5,loc='left',pad=22,fontweight='bold')
ax.text(0,1.055,'ninguna combinación lineal de 16 bits predice el siguiente',transform=ax.transAxes,fontsize=9,color=SEC)
ax.legend(frameon=False,fontsize=8.8,labelcolor=SEC,loc='upper left',handlelength=1.7)
ax.text(.97,.55,f"máx |z| = {np.abs(z).max():.2f}\numbral = {B.umbral_multitest(2**16):.2f}",
        transform=ax.transAxes,ha='right',va='top',fontsize=9.2,color=SEC,
        family='DejaVu Sans Mono',linespacing=1.6)

# --- 4. Berlekamp-Massey ---
ax=fig.add_subplot(gs[1,1]); clean(ax)
cps=sorted(set(np.unique(np.logspace(1,np.log10(N),140).astype(int)).tolist()))
for (nm,b),col,lw,al in zip(seq.items(),[BLUE,CTL],[2.4,5.5],[1,.55]):
    p=np.array(B.perfil_complejidad(b,cps))
    ax.loglog(p[:,0],np.maximum(p[:,1],1),color=col,lw=lw,alpha=al,label=nm,
              solid_capstyle='round',zorder=4 if lw<3 else 2)
ax.set_xlabel('bits observados  n'); ax.set_ylabel('complejidad lineal  L(n)')
ax.set_ylim(3,2e5)
ax.set_title('4 · Complejidad lineal (Berlekamp-Massey)',color=INK,fontsize=11.5,loc='left',pad=22,fontweight='bold')
ax.text(0,1.055,'aquí se rompe: se estanca en 32 y no vuelve a crecer',transform=ax.transAxes,fontsize=9,color=SEC)
ax.legend(frameon=False,fontsize=9,labelcolor=SEC,loc='lower right',handlelength=1.6)
ax.annotate('L = 32 para siempre.\nCon 64 bits observados\nse predice todo lo demás.',
    xy=(3000,32),xytext=(.06,.30),textcoords='axes fraction',fontsize=9.6,color=BLUE,
    fontweight='bold',arrowprops=dict(arrowstyle='-',color=BLUE,lw=1.1))
ax.annotate('n/2',xy=(N,N/2),xytext=(.62,.86),textcoords='axes fraction',fontsize=9.6,
    color=SEC,fontweight='bold',arrowprops=dict(arrowstyle='-',color=SEC,lw=1))

fig.text(.075,.95,'Cuatro pruebas dicen «aleatorio». La quinta lo rompe con 64 bits.',
         fontsize=15.5,color=INK,fontweight='bold')
fig.text(.075,.908,'La misma secuencia de 70.000 bits, generada por un registro de 32 bits y totalmente determinista.',
         fontsize=9.5,color=SEC)
fig.savefig(figuras('fig1_1_lfsr.png'),dpi=170)
print("figura 1.1 ok")
