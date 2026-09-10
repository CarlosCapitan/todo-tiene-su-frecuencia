#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura del control del apartado 6.4."""
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.stats import norm

d = np.load('../datos/cap06_control.npz')
hora, bv, b_mag = d['hora'], d['bv'], d['b_mag']
ps = np.array([bv[hora==h].mean() for h in range(24)])
pm = np.array([b_mag[hora==h].mean() for h in range(24)])
n  = np.array([(hora==h).sum() for h in range(24)])
umb = norm.ppf(1-(1-0.95**(1/24))/2)
banda = umb*0.5/np.sqrt(n)

fig, ax = plt.subplots(1, 2, figsize=(13.5, 5.0))
h = np.arange(24)
ax[0].fill_between(h, 0.5-banda, 0.5+banda, color="#c9d6e3", alpha=.7,
                   label=f"banda de ruido al 5 % (24 horas probadas)")
ax[0].axhline(0.5, color="#666", lw=1)
ax[0].plot(h, ps, "o-", color="#1f4e79", lw=2.2, ms=6, label="signo: ¿sube?")
ax[0].plot(h, pm, "s-", color="#e08214", lw=2.2, ms=6,
           label="magnitud binarizada: ¿supera su mediana?")
ax[0].set_xticks(range(0,24,3)); ax[0].set_xlabel("hora UTC")
ax[0].set_ylabel("probabilidad")
ax[0].set_title("A · Dos series binarias, misma longitud, p = 0,5\n"
                "Una no sale de la banda. La otra llega a 16,5 σ.", fontsize=11)
ax[0].legend(fontsize=8.5, loc="upper left"); ax[0].grid(alpha=.3)

nom = ["signo\n(binaria)", "magnitud\nBINARIZADA", "magnitud\n(continua)", "volumen\n(continua)"]
d24 = [4.0, 295.7, 479.6, 680.2]; d7 = [4.7, 1129.7, 1152.4, 658.5]
x = np.arange(4); w = 0.38
ax[1].bar(x-w/2, d24, w, color="#7f9fc0", label="pico diario (24 h)")
ax[1].bar(x+w/2, d7, w, color="#1f4e79", label="pico semanal (7 d)")
for i,(a,b) in enumerate(zip(d24,d7)):
    ax[1].text(i-w/2, a*1.12, f"{a:.0f}", ha="center", fontsize=9)
    ax[1].text(i+w/2, b*1.12, f"{b:.0f}", ha="center", fontsize=9)
ax[1].set_yscale("log"); ax[1].set_ylim(1, 4200)
ax[1].set_xticks(x); ax[1].set_xticklabels(nom, fontsize=9)
ax[1].set_ylabel("veces la mediana del espectro (escala log)")
ax[1].set_title("B · Binarizar la magnitud le cuesta el 2 % del pico semanal\n"
                "(1.152 → 1.130). No es la binarización lo que aplana.", fontsize=11)
ax[1].legend(fontsize=9); ax[1].grid(alpha=.3, axis="y", which="both")

fig.suptitle("El control que faltaba: binarizar la magnitud exactamente igual que el signo.",
             fontsize=10.5, y=0.995)
plt.tight_layout(); plt.savefig("../figuras/fig6_3_control.png", dpi=170); print("ok")
