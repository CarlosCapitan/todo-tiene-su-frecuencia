#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figura 9.2 — dos algoritmos clasicos y tres exponentes medidos."""
import os, sys, csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt

f = lambda v: float(v) if v not in ("", None) else np.nan
r = list(csv.DictReader(open(datos("escalado_grupo.csv"))))
bits = np.array([f(x["bits"]) for x in r])
rho  = np.array([f(x["rho_pasos"]) for x in r])
bsgs = np.array([f(x["bsgs_ops"]) for x in r])

def exponente(y):
    ok = ~np.isnan(y)
    A = np.vstack([bits[ok], np.ones(ok.sum())]).T
    return np.linalg.lstsq(A, np.log2(y[ok]), rcond=None)[0][0]
e_rho, e_bsgs = exponente(rho), exponente(bsgs)
print(f"Pollard rho: N^{e_rho:.4f}    BSGS: N^{e_bsgs:.4f}    (cota de Shoup: 0,5)")

fig, ax = plt.subplots(1, 2, figsize=(11.5, 4.3))
ok = ~np.isnan(bsgs)
ax[0].semilogy(bits, rho, "o-", lw=2, color="#1f4e79", label=f"Pollard rho — medido  $N^{{{e_rho:.3f}}}$")
ax[0].semilogy(bits[ok], bsgs[ok], "s-", lw=2, color="#2e8b57", label=f"BSGS — medido  $N^{{{e_bsgs:.3f}}}$")
ax[0].semilogy(bits, rho[0]*2.0**((bits-bits[0])*0.5), "--", color="#c00000", label=r"$2^{n/2}$  (cota de Shoup)")
ax[0].semilogy(bits, rho[0]*2.0**((bits-bits[0])*1.0), ":", color="#999", label=r"$2^{n}$  (fuerza bruta)")
ax[0].set_xlabel("bits del orden del grupo (primo)"); ax[0].set_ylabel("operaciones de grupo")
ax[0].set_title("A · Dos algoritmos clasicos, curvas de orden primo")
ax[0].grid(alpha=.3, which="both"); ax[0].legend(fontsize=8, loc="upper left")

nom = ["Pollard rho\n(medido, 16-44 bits)", "BSGS\n(medido, 16-40 bits)",
       "gradient_hunt\n(TelecoSpectro, 20-48 bits)", "fuerza bruta", "Shor (cuantico)"]
expo = [e_rho, e_bsgs, 0.5055, 1.0, 0.0]
cols = ["#1f4e79", "#2e8b57", "#e08214", "#999999", "#7030a0"]
y = np.arange(len(expo))[::-1]
ax[1].barh(y, expo, color=cols, height=.55)
ax[1].axvline(0.5, color="#c00000", ls="--", lw=2)
ax[1].text(0.505, 4.35, "cota de Shoup para algoritmos genericos: 0,5", color="#c00000", fontsize=8.5, va="center")
for y_, e in zip(y, expo):
    et = "1 (exhaustiva)" if e == 1.0 else ("~0  (polinomico en log N)" if e == 0.0 else f"{e:.4f}")
    ax[1].text(e + 0.02, y_, et, va="center", fontsize=9)
ax[1].set_yticks(y); ax[1].set_yticklabels(nom, fontsize=8)
ax[1].set_xlim(0, 1.18); ax[1].set_xlabel("exponente medido:  coste ~ $N^{\\alpha}$")
ax[1].set_title("B · Tres implementaciones distintas, un solo exponente")
ax[1].grid(alpha=.3, axis="x")

fig.tight_layout()
sal = figuras("fig9_2_exponente.png"); fig.savefig(sal, dpi=150)
print("figura ->", sal)
