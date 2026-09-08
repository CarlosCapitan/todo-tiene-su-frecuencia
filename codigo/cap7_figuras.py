#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura 7.1 — el hallazgo que sobrevive y el que muere."""
import os, csv
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt

AQUI=os.path.dirname(os.path.abspath(__file__)); RAIZ=os.path.dirname(AQUI)
# los dos CSV son la fuente; el .npz es solo una copia de conveniencia
_b=list(csv.DictReader(open(os.path.join(RAIZ,"datos","polymarket_walkforward_bloques.csv"))))
rows=np.array([[float(r["ini"]),float(r["fin"]),float(r["n_disparos"]),float(r["acierto"])] for r in _b])
nulls=np.array([float(r["acierto_nula"]) for r in
                csv.DictReader(open(os.path.join(RAIZ,"datos","polymarket_walkforward_nula.csv")))])
K=int(rows[:,2].sum()); A=float((rows[:,2]*rows[:,3]).sum()/K)

fig,ax=plt.subplots(1,3,figsize=(15,4.3))

# --- A: bloques walk-forward
acc=rows[:,3]; nn=rows[:,2]; x=np.arange(len(acc))
col=["#1f4e79" if a>.5 else "#c00000" for a in acc]
ax[0].bar(x,(acc-.5)*100,color=col,width=.72)
ax[0].axhline(0,color="#333",lw=1)
ax[0].axhline((A-.5)*100,color="#e08214",lw=2,ls="--",
              label=f"agregado {100*(A-.5):+.2f} pp  (n={K:,})")
ax[0].set_xlabel("bloque walk-forward (2.500 ventanas cada uno)")
ax[0].set_ylabel("ventaja sobre 50 %  (pp)")
ax[0].set_title("A · Cada bloque decide fuera de muestra")
ax[0].legend(fontsize=8); ax[0].grid(alpha=.3,axis="y")
ax[0].set_xticks(x[::3]); ax[0].set_xticklabels([str(i+1) for i in x[::3]])
ax[0].text(.3,-2.15,f"{int((acc>.5).sum())}/{len(acc)} bloques en positivo",fontsize=8.5,color="#444")

# --- B: nula del pipeline completo
ax[1].hist(nulls*100,bins=34,color="#b8c6d9",edgecolor="#7f96b3",lw=.5)
ax[1].axvline(nulls.mean()*100,color="#555",ls=":",lw=1.5)
ax[1].axvline(np.percentile(nulls,95)*100,color="#c00000",ls="--",lw=1.5,
              label=f"p95 de la nula = {100*np.percentile(nulls,95):.2f} %")
ax[1].axvline(A*100,color="#e08214",lw=2.6,label=f"observado = {100*A:.2f} %")
ax[1].set_xlabel("acierto fuera de muestra (%)"); ax[1].set_ylabel("réplicas")
ax[1].set_title("B · 300 réplicas del procedimiento COMPLETO")
ax[1].legend(fontsize=8); ax[1].grid(alpha=.3,axis="y")
ax[1].annotate("", xy=(A*100,9), xytext=(np.percentile(nulls,95)*100,9),
               arrowprops=dict(arrowstyle="<-",color="#e08214",lw=1.6))
ax[1].text(48.75,20.5,"5,9 desviaciones típicas\nninguna de las 300\nréplicas lo alcanza",
           fontsize=8.5,color="#a15c00")

# --- C: la hipotesis que muere
etq=["|ret| >\nmediana","|ret| >\ncuartil 75","|ret| >\ndecil 90","|ret| >\npercentil 95"]
entr=np.array([51.19,51.44,52.65,53.11]); test=np.array([49.77,50.85,52.16,51.08])
w=.36; xx=np.arange(len(etq))
ax[2].bar(xx-w/2,entr-50,w,color="#7f9fc0",label="en entrenamiento")
ax[2].bar(xx+w/2,test-50,w,color="#c00000",label="fuera de muestra")
ax[2].axhline(0,color="#333",lw=1)
ax[2].set_xticks(xx); ax[2].set_xticklabels(etq,fontsize=8)
ax[2].set_ylabel("ventaja sobre 50 %  (pp)")
ax[2].set_title("C · La hipótesis de volatilidad, condicionada")
ax[2].legend(fontsize=8,loc="upper left",bbox_to_anchor=(0.0,0.80)); ax[2].grid(alpha=.3,axis="y")
ax[2].text(-0.45,2.72,"sube al condicionar en entrenamiento;\nfuera de muestra no replica el patrón",
           fontsize=8,color="#444")
ax[2].set_ylim(-0.55,3.45)

fig.tight_layout()
sal=os.path.join(RAIZ,"figuras","fig7_1_sobrevive_o_muere.png")
fig.savefig(sal,dpi=150); print("figura ->",sal)
