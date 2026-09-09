#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura 9.1 — A: las 13 hipotesis del retorno horario contra el umbral
preinscrito.  B: el control que lo resuelve, normalizado a la mediana de la nula."""
import json, os, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt

AQUI = os.path.dirname(os.path.abspath(__file__))
FIGURAS = os.path.join(os.path.dirname(os.path.dirname(AQUI)), "figuras")
d = json.load(open(os.path.join(AQUI, "datos", "resultados_continuos.json")))
r = d["1h/retorno"]
UMBRAL = np.sqrt(2*np.log(82))

ETQ = {"autocorr":"autocorrelación","ciclo_24":"ciclo @24 h","ciclo_168":"ciclo @168 h",
       "ciclo_720":"ciclo @720 h","bicoh_256":"bicoherencia 256","bicoh_512":"bicoherencia 512",
       "tiempo_frec":"tiempo-frecuencia","kurt_espectral":"kurtosis espectral",
       "envolvente":"envolvente","D2_m5":"D₂ (m=5)","D2_m6":"D₂ (m=6)","D2_m7":"D₂ (m=7)",
       "lyapunov":"Lyapunov"}
zs = []
for h, obs in r["obs"].items():
    nul = np.array([v for v in r["nula"][h] if v == v], float)
    if len(nul) < 50: continue
    mu, sd = nul.mean(), nul.std()
    zs.append((ETQ.get(h, h), abs((obs-mu)/sd)))
zs.sort(key=lambda t: t[1])

fig, ax = plt.subplots(1, 2, figsize=(14, 5.2))

nom = [t[0] for t in zs]; val = [t[1] for t in zs]
col = ["#1f4e79" if v > UMBRAL else "#b8c4d0" for v in val]
ax[0].barh(range(len(val)), val, color=col)
ax[0].axvline(UMBRAL, color="#c00000", ls="--", lw=1.8)
ax[0].text(UMBRAL*1.12, 0.2, f"umbral preinscrito\n√(2·ln 82) = {UMBRAL:.2f}",
           fontsize=8.5, color="#c00000")
ax[0].set_xscale("log"); ax[0].set_yticks(range(len(nom))); ax[0].set_yticklabels(nom, fontsize=9)
ax[0].set_xlabel("|z| contra 200 surrogados IAAFT (escala log)")
ax[0].set_title("A · Once de trece hipótesis se encienden\n(retorno horario)", fontsize=11)
ax[0].grid(alpha=.3, axis="x", which="both")

# B: control, normalizado a la mediana de la nula
est = ["ciclo_24", "bicoh_512", "tiempo_frec", "envolvente", "kurt_espectral"]
lab = ["ciclo @24 h", "bicoherencia", "tiempo-frec.", "envolvente", "kurt. espectral"]
real   = [101.80, 2.34, 204.55, 1445.67, 11.84]
sortea = [101.80, 2.05, 218.08, 1498.70, 20.72]
baraja = [  7.83, 1.09, 109.02,   52.48,  3.04]
nula   = [np.median([v for v in r["nula"][e] if v == v]) for e in est]

x = np.arange(len(est)); w = .27
for i, (v, c, lb) in enumerate([(real, "#1f4e79", "real"),
                                (sortea, "#e08214", "signos sorteados"),
                                (baraja, "#b8c4d0", "magnitudes barajadas")]):
    ax[1].bar(x + (i-1)*w, np.array(v)/np.array(nula), w, color=c, label=lb)
ax[1].axhline(1, color="#c00000", ls="--", lw=1.8)
ax[1].text(-0.42, 0.90, "mediana de la nula", fontsize=8.5, color="#c00000", ha="left", va="top")
ax[1].set_yscale("log"); ax[1].set_xticks(x); ax[1].set_xticklabels(lab, fontsize=9)
ax[1].set_ylabel("veces la mediana de la nula (escala log)")
ax[1].set_title("B · Sortear la dirección no cambia nada.\nBarajar las magnitudes lo apaga todo.", fontsize=11)
ax[1].legend(fontsize=9, loc="upper left"); ax[1].grid(alpha=.3, axis="y", which="both")

plt.tight_layout()
sal = os.path.join(FIGURAS if os.path.isdir(FIGURAS) else AQUI, "fig9_1_control.png")
plt.savefig(sal, dpi=170); print("escrita", sal)
