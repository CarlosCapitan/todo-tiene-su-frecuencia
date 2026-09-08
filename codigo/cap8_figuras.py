#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura 8.1 — cuatro metodos mas alla de Fourier, sus surrogados, y el techo."""
import os, csv
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt

AQUI=os.path.dirname(os.path.abspath(__file__)); RAIZ=os.path.dirname(AQUI)
D=lambda f: os.path.join(RAIZ,"datos",f)
f3={r['serie']:r for r in csv.DictReader(open(D("polymarket_fase3.csv")))}
sur=list(csv.DictReader(open(D("polymarket_surrogados_iaaft.csv"))))

fig,ax=plt.subplots(1,3,figsize=(15,4.4))

# --- A: los cuatro metodos, normalizados a la linea base de ruido blanco
met=["ciclo288","ciclo2016","bicoh","tf_max"]
etq=["cicloest.\n@288 (24 h)","cicloest.\n@2016 (7 d)","bicoherencia\n(no lineal)","tiempo-frec.\n(transitorios)"]
base=np.array([float(f3['ruido_blanco_calibracion'][m]) for m in met])
series=[("signo de la resolución","#1f4e79","signo_crudo"),
        ("residuo blanqueado","#7f9fc0","residuo_blanqueado"),
        ("magnitud (control +)","#e08214","magnitud_log_ret")]
w=.26; x=np.arange(len(met))
for i,(lab,c,key) in enumerate(series):
    v=np.array([float(f3[key][m]) for m in met])/base
    ax[0].bar(x+(i-1)*w, v, w, color=c, label=lab)
ax[0].axhline(1,color="#c00000",ls="--",lw=1.6)
ax[0].text(3.35,1.08,"línea base\n= ruido blanco",fontsize=8,color="#c00000",ha="right")
ax[0].set_yscale("log"); ax[0].set_ylim(.5,40)
ax[0].set_xticks(x); ax[0].set_xticklabels(etq,fontsize=8)
ax[0].set_ylabel("veces la línea base (escala log)")
ax[0].set_title("A · Cuatro métodos más allá de Fourier")
ax[0].legend(fontsize=8,loc="upper left"); ax[0].grid(alpha=.3,axis="y",which="both")

# --- B: p empiricos de los surrogados IAAFT
grupos={"signo_crudo":("signo","#1f4e79","o"),
        "residuo_blanqueado":("residuo","#7f9fc0","s"),
        "magnitud_log_ret":("magnitud","#e08214","^")}
nom={"ciclo288":"ciclo@288","ciclo2016":"ciclo@2016","bicoh":"bicoherencia","tf":"tiempo-frec."}
ypos={k:i for i,k in enumerate(["ciclo288","ciclo2016","bicoh","tf"][::-1])}
orden=list(grupos)
for r in sur:
    lab,c,m=grupos[r['serie']]
    dy=0.20*(orden.index(r['serie'])-1)
    ax[1].scatter(float(r['p_empirico']), ypos[r['estadistico']]+dy,
                  s=85,c=c,marker=m,edgecolor="k",lw=.4,zorder=3)
ax[1].axvline(0.05,color="#c00000",ls="--",lw=1.6)
ax[1].text(0.065,-0.42,"α = 0,05",fontsize=8.5,color="#c00000")
ax[1].set_ylim(-0.55,3.55)
ax[1].set_yticks(list(ypos.values())); ax[1].set_yticklabels([nom[k] for k in ypos],fontsize=9)
ax[1].set_xlim(0,1); ax[1].set_xlabel("p empírico frente a 80 surrogados IAAFT")
ax[1].set_title("B · Nula que conserva espectro y distribución")
ax[1].grid(alpha=.3,axis="x")
from matplotlib.lines import Line2D
ax[1].legend(handles=[Line2D([],[],marker=m,ls="",color=c,label=l,markeredgecolor="k")
                      for l,c,m in grupos.values()],fontsize=8,loc="lower right")

# --- C: el techo de varianza
var={r['fuente']:float(r['r2_pct']) for r in csv.DictReader(open(D("polymarket_varianza.csv")))}
etq3=["solo el signo anterior\n(capítulo 6)","modelo, todas\nlas ventanas","regla del capítulo 7,\nsobre sus disparos"]
val3=[var['solo_signo_anterior_fase1'],var['walkforward_modelo_todas_ventanas'],var['walkforward_regla_con_disparo']]
cols=["#b8c6d9","#7f9fc0","#e08214"]
yy=np.arange(3)
ax[2].barh(yy,val3,color=cols,edgecolor="#666",height=.6)
for y_,v in zip(yy,val3):
    ax[2].text(v+0.006,y_,f"{v:.4f} %".replace(".",","),va="center",fontsize=9.5)
ax[2].set_yticks(yy); ax[2].set_yticklabels(etq3,fontsize=8.5)
ax[2].set_xlim(0,0.36); ax[2].set_xlabel("R² : % de la varianza del signo explicada")
ax[2].set_title("C · El techo: cuánto es predeterminable")
ax[2].grid(alpha=.3,axis="x")
ax[2].text(0.355,-0.62,"el total es 100 %  ·  lo mejor extraído ≈ 1 parte de cada 376",
           fontsize=8.5,color="#555",ha="right")
ax[2].set_ylim(-0.85,2.6)

fig.tight_layout()
sal=os.path.join(RAIZ,"figuras","fig8_1_techo.png")
fig.savefig(sal,dpi=150); print("figura ->",sal)
