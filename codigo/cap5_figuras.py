#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura 5.1 — el detector de dos etapas y el rechazo de interferencia."""
import csv, os
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt

AQUI=os.path.dirname(os.path.abspath(__file__)); RAIZ=os.path.dirname(AQUI)
D=lambda f: os.path.join(RAIZ,"datos",f)

filas=list(csv.DictReader(open(D("rodamientos_dos_etapas.csv"))))
sanos=[float(r['sk_banda']) for r in filas if r['verdad']=='sano']
fallo=[(float(r['sk_banda']), r['etapa1']=='FALLO', r['verdad']) for r in filas if r['verdad']!='sano']

fig,ax=plt.subplots(1,2,figsize=(11.5,4.3))

# --- A: separacion por kurtosis de banda
rng=np.random.default_rng(0)
ax[0].scatter(sanos, rng.normal(1,.09,len(sanos)), s=70, c="#2e8b57",
              edgecolor="k", lw=.5, zorder=3, label="sanos (4)")
det=[k for k,d,_ in fallo if d]; nod=[k for k,d,_ in fallo if not d]
ax[0].scatter(det, rng.normal(2,.05,len(det)), s=70, c="#c00000",
              edgecolor="k", lw=.5, zorder=3, label="con fallo, firma detectada (11)")
ax[0].scatter(nod, rng.normal(2,.05,len(nod)), s=70, facecolor="white",
              edgecolor="#c00000", lw=1.6, zorder=3, label="con fallo, sin firma (3)")
ax[0].axvspan(0.9,2.5,color="#ffe08a",alpha=.5,zorder=1)
ax[0].axvline(1.0,color="#333",ls="--",lw=1.2,zorder=2)
ax[0].text(1.06,1.52,"umbral\nSK = 1,0",fontsize=8.5,color="#333")
ax[0].text(1.55,2.62,"hueco 0,9 – 2,5",fontsize=8.5,ha="center",color="#8a6d00")
ax[0].set_xscale("log"); ax[0].set_xlim(0.15,40); ax[0].set_ylim(0.4,2.9)
ax[0].set_yticks([1,2]); ax[0].set_yticklabels(["sano","con fallo"])
ax[0].set_xlabel("kurtosis espectral de la banda demodulada (escala log)")
ax[0].set_title("A · Etapa 1: ¿hay contenido impulsivo?")
ax[0].grid(alpha=.3,axis="x",which="both"); ax[0].legend(fontsize=8,loc="lower right",framealpha=.95)

# --- B: interferencia blanca vs estructurada
rr=[r for r in csv.DictReader(open(D("rodamientos_interferencia.csv"))) if r['registro']=='OR007@6_0']
snr=[float(r['snr_db']) for r in rr]
zb=[float(r['z_ruido_blanco']) for r in rr]
zr=[float(r['z_rodamiento_sano']) for r in rr]
ax[1].plot(snr,zr,"o-",lw=2.2,color="#1f4e79",label="interferencia = rodamiento sano real")
ax[1].plot(snr,zb,"s--",lw=2.2,color="#c00000",label="interferencia = ruido blanco")
ax[1].axhline(2.5,color="#666",ls=":",lw=1.3)
ax[1].text(-9.5,2.65,"umbral de deteccion",fontsize=8,color="#444")
ax[1].invert_xaxis()
ax[1].set_xlabel("SNR global (dB)"); ax[1].set_ylabel("z de BPFO")
ax[1].set_title("B · Etapa 2: el ruido real estorba menos (OR007@6)")
ax[1].grid(alpha=.3); ax[1].legend(fontsize=8,loc="center left")
ax[1].annotate("", xy=(0,6.845), xytext=(0,1.921),
               arrowprops=dict(arrowstyle="<->",color="#444",lw=1.4))
ax[1].text(-1.2,4.3,"misma SNR global,\n21,7 dB menos de ruido\nDENTRO de la banda",
           fontsize=8.5,color="#333")

fig.tight_layout()
sal=os.path.join(RAIZ,"figuras","fig5_1_dos_etapas.png")
fig.savefig(sal,dpi=150); print("figura ->",sal)
