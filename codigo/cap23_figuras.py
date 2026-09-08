"""Figuras 2.1 y 3.1."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras

import numpy as np, json, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from math import sqrt, log
BLUE,ORANGE,AQUA,RED,CTL="#2a78d6","#eb6834","#1baf7a","#e34948","#8a9498"
INK,SEC,MUT,SURF="#0f1518","#4b565b","#7c878c","#f7f8f7"
plt.rcParams.update({'figure.facecolor':SURF,'axes.facecolor':SURF,'font.size':9.5,
 'axes.edgecolor':'#d9e1e3','axes.labelcolor':SEC,'xtick.color':SEC,'ytick.color':SEC,
 'axes.spines.top':False,'axes.spines.right':False,'grid.color':'#eaf0f1','grid.linewidth':.8,
 'font.family':'DejaVu Sans'})
def clean(ax): ax.grid(True,alpha=.9,zorder=0); ax.set_axisbelow(True); ax.tick_params(length=3,width=.8)

# ================= FIGURA 2.1 =================
M=json.load(open(figuras('cap2_matriz.json')))
ctrl=list(M.keys()); met=['CICLO@288','CICLO@2016','BICOH','TF','Lyapunov','FNN colapsa']
key=['c288','c2016','bic','tf','lyap','fnn']
V=np.zeros((len(ctrl),6))
for i,c in enumerate(ctrl):
    for j,k in enumerate(key):
        V[i,j]= (1.0 if M[c]['fnn'][1]<.05 else 0.0) if k=='fnn' else M[c][k]
base=V[0].copy()
R=np.zeros_like(V)
for j in range(6):
    R[:,j]= V[:,j]*2.2 if j==5 else np.log10(np.maximum(V[:,j],1e-3)/max(base[j],1e-3))
fig,ax=plt.subplots(figsize=(11.6,4.6))
fig.subplots_adjust(left=.20,right=.98,top=.72,bottom=.13)
ax.imshow(R,cmap='Oranges',aspect='auto',vmin=0,vmax=2.2)
ax.set_xticks(range(6)); ax.set_xticklabels(met,fontsize=10.5)
ax.set_yticks(range(len(ctrl))); ax.set_yticklabels(ctrl,fontsize=10.5)
for i in range(len(ctrl)):
    for j in range(6):
        v=V[i,j]
        t='sí' if (j==5 and v>0) else ('no' if j==5 else (f"{v:.0f}" if v>=10 else f"{v:.2f}"))
        ax.text(j,i,t,ha='center',va='center',fontsize=11,
                color='white' if R[i,j]>1.2 else INK, fontweight='bold' if R[i,j]>0.35 else 'normal')
ax.grid(False)
for s in ax.spines.values(): s.set_visible(False)
fig.text(.20,.90,'Figura 2.1 · La matriz tiene que salir diagonal',fontsize=14.5,color=INK,fontweight='bold')
fig.text(.20,.845,'Cada control con estructura conocida debe caer ante su método y ante ningún otro.',fontsize=9.5,color=SEC)
fig.text(.20,.795,'Una casilla encendida fuera de la diagonal es un falso positivo; una apagada en ella, un método ciego.',fontsize=9.5,color=SEC)
fig.savefig(figuras('fig2_1_matriz.png'),dpi=170); print("figura 2.1 ok")

# ================= FIGURA 3.1 =================
D=json.load(open(figuras('cap3_datos.json')))
fig=plt.figure(figsize=(12.4,4.7))
gs=fig.add_gridspec(1,3,wspace=.30,left=.065,right=.98,top=.70,bottom=.155)

ax=fig.add_subplot(gs[0]); clean(ax)
A=D['A']; Ns=[a['N'] for a in A]
ax.semilogx(Ns,[a['zmax'] for a in A],color=BLUE,lw=2.4,marker='o',ms=6,mfc=SURF,mew=1.6,label='medido sobre ruido puro',zorder=4)
ax.semilogx(Ns,[a['teo'] for a in A],color=CTL,lw=4.5,alpha=.55,label='√(2·ln N)',zorder=2)
ax.axhline(3,color=RED,lw=1.6,ls=(0,(4,3)),zorder=3)
ax.text(3e5,3.08,'umbral fijo de 3σ',fontsize=9,color=RED,fontweight='bold',ha='right')
ax.set_xlabel('número de hipótesis probadas  N'); ax.set_ylabel('máx |z| obtenido')
ax.set_ylim(2.2,5.4)
ax.set_title('A · El máximo de N normales',color=INK,fontsize=11,loc='left',pad=20,fontweight='bold')
ax.text(0,1.05,'sobre ruido puro: no hay nada que encontrar',transform=ax.transAxes,fontsize=9,color=SEC)
ax.legend(frameon=False,fontsize=8.8,labelcolor=SEC,loc='lower right',handlelength=1.7)

ax=fig.add_subplot(gs[1]); clean(ax)
B=D['B']; lab=['ingenua\nz ~ N(0,1)','permutación','desplazamiento\ncircular']
val=[B['fp_ing']*100,B['fp_sh']*100,B['fp_ci']*100]
cols=[RED,RED,AQUA]
ax.bar(range(3),val,width=.6,color=cols,zorder=3)
ax.axhline(5,color=INK,lw=1.6,ls=(0,(4,3)),zorder=4)
ax.text(2.45,5.6,'nominal 5 %',fontsize=9,color=INK,ha='right',fontweight='bold')
for i,v in enumerate(val): ax.text(i,v+.7,f"{v:.1f} %",ha='center',fontsize=10.5,fontweight='bold',color=INK)
ax.set_xticks(range(3)); ax.set_xticklabels(lab,fontsize=9.2)
ax.set_ylabel('falsos positivos (%)'); ax.set_ylim(0,26)
ax.set_title('B · Tasa de falsos positivos',color=INK,fontsize=11,loc='left',pad=20,fontweight='bold')
ax.text(0,1.05,'series independientes: todo positivo es falso',transform=ax.transAxes,fontsize=9,color=SEC)

ax=fig.add_subplot(gs[2]); clean(ax)
C=D['C']; lab2=['elegir y medir\nen TODO','elegir y medir\nen entrenamiento','elegir en train,\nmedir en TEST']
val2=[C['todo'],C['tr'],C['te']]
ax.bar(range(3),val2,width=.6,color=[RED,RED,AQUA],zorder=3)
ax.axhline(0.80,color=INK,lw=1.6,ls=(0,(4,3)),zorder=4)
ax.text(-.42,.88,'nivel honesto 0,80',fontsize=9,color=INK,ha='left',fontweight='bold')
ax.axhline(C['teo'],color=CTL,lw=1.4,ls=(0,(2,2)),zorder=4)
ax.text(.02,C['teo']+.08,f"√(2·ln 30) = {C['teo']:.2f}",fontsize=8.8,color=SEC)
for i,v in enumerate(val2): ax.text(i,v+.12,f"{v:.2f}",ha='center',fontsize=10.5,fontweight='bold',color=INK)
ax.set_xticks(range(3)); ax.set_xticklabels(lab2,fontsize=9.2)
ax.set_ylabel('|z| medio obtenido'); ax.set_ylim(0,3.1)
ax.set_title('C · Dónde se infla la selección',color=INK,fontsize=11,loc='left',pad=20,fontweight='bold')
ax.text(0,1.05,'30 predictores, todos ruido puro',transform=ax.transAxes,fontsize=9,color=SEC)

fig.text(.065,.90,'Figura 3.1 · Tres formas de engañarse, y su corrección',fontsize=14.5,color=INK,fontweight='bold')
fig.text(.065,.845,'En los tres paneles no hay ninguna señal real: todo lo que aparece por encima del nivel honesto es artefacto del método.',fontsize=9.5,color=SEC)
fig.savefig(figuras('fig3_1_nulas.png'),dpi=170); print("figura 3.1 ok")
