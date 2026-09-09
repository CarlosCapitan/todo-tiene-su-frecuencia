#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analiza el escalado medido de run_gradient_hunt sobre secp256k1 real.
Entrada: datos/escalado_gradient_hunt.csv   Salida: figuras/figX_escalado.png
"""
import csv, math, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
CSV = os.path.join(RAIZ, "datos", "escalado_gradient_hunt.csv")

bits_l, tt, tl, rss = [], [], [], []
for r in csv.DictReader(open(CSV)):
    if r["build"] == "sin_prefiltro":
        continue
    bits_l.append(int(r["bits"])); tt.append(float(r["t_total_s"]))
    tl.append(float(r["t_lente_s"])); rss.append(float(r["rss_mb"]))
bits_l = np.array(bits_l); tt = np.array(tt); tl = np.array(tl); rss = np.array(rss)

ub = np.unique(bits_l)
t_tot = np.array([tt[bits_l == b].mean() for b in ub])
t_len = np.array([tl[bits_l == b].mean() for b in ub])
t_bus = t_tot - t_len                      # el trabajo real de busqueda
m_rss = np.array([rss[bits_l == b].max() for b in ub])

print(f"{'bits':>5} {'total s':>9} {'lente s':>8} {'busqueda s':>11} "
      f"{'x/4bits':>8} {'RSS MB':>9}")
prev = None
for b, a, l, s, r in zip(ub, t_tot, t_len, t_bus, m_rss):
    rat = f"{s/prev:.2f}" if prev else "  -"
    print(f"{b:5d} {a:9.3f} {l:8.3f} {s:11.3f} {rat:>8} {r:9.1f}")
    prev = s

# Ajuste log2(t) = a*bits + c sobre el tramo asintotico (>=32 bits)
sel = ub >= 32
A = np.vstack([ub[sel], np.ones(sel.sum())]).T
a, c = np.linalg.lstsq(A, np.log2(t_bus[sel]), rcond=None)[0]
print(f"\najuste log2(t) = {a:.4f}*bits + {c:.3f}")
print(f"exponente medido: t ~ 2^({a:.4f}*n)  ->  N^{a:.4f}")
print(f"  Pollard/BSGS teorico: 0.5000   fuerza bruta: 1.0000")

# Extrapolacion a secp256k1 completo
t48 = t_bus[ub == 48][0]
t256 = t48 * 2 ** ((256 - 48) * a)
anios = t256 / (365.25 * 24 * 3600)
mem_bytes = (2 ** 128) * 12
print(f"\nextrapolacion a 256 bits: {t256:.3e} s = {anios:.3e} anios")
print(f"memoria requerida (m=2^128 x 12 B): {mem_bytes:.3e} B = {mem_bytes/1e12:.3e} TB")

# Techo por RAM: 32 GB / 12 B por baby step
m_max = 32 * 1024**3 / 12
n_max = 2 * math.log2(m_max)
print(f"techo por RAM (32 GB): m={m_max:.3e} -> n_max = {n_max:.1f} bits")

fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))

ax[0].semilogy(ub, t_bus, "o-", lw=2, color="#1f4e79", label="medido (busqueda)")
ref_sqrt = t_bus[ub == 32][0] * 2.0 ** ((ub - 32) * 0.5)
ref_full = t_bus[ub == 32][0] * 2.0 ** ((ub - 32) * 1.0)
ax[0].semilogy(ub, ref_sqrt, "--", color="#c00000", label=r"$2^{n/2}$  (Pollard/BSGS)")
ax[0].semilogy(ub, ref_full, ":", color="#7f7f7f", label=r"$2^{n}$  (fuerza bruta)")
ax[0].semilogy(ub, t_len, "s-", color="#2e8b57", ms=4, label="prefiltro espectral")
ax[0].set_xlabel("bits del universo de busqueda")
ax[0].set_ylabel("segundos")
ax[0].set_title("A · Tiempo de recuperacion de d")
ax[0].grid(alpha=.3, which="both"); ax[0].legend(fontsize=8)

BASE_MB = 29.0                      # interprete + numpy, medido a 20 bits
ax[1].semilogy(ub, m_rss - BASE_MB, "o-", lw=2, color="#1f4e79",
               label="RSS medido - linea base")
ref_mem = (m_rss[ub == 48][0] - BASE_MB) * 2.0 ** ((ub - 48) * 0.5)
ax[1].semilogy(ub, ref_mem, "--", color="#c00000", label=r"$2^{n/2}$")
teo = (2.0 ** (ub / 2.0)) * 12 / 1024**2
ax[1].semilogy(ub, teo, ":", color="#2e8b57", label=r"holograma teorico $12\cdot 2^{n/2}$ B")
ax[1].axhline(32 * 1024, color="#c00000", lw=1, alpha=.6)
ax[1].text(20.5, 32 * 1024 * 1.4, "32 GB (RAM de la maquina)", fontsize=8, color="#c00000")
ax[1].set_xlabel("bits del universo de busqueda")
ax[1].set_ylabel("MB")
ax[1].set_title("B · Memoria del holograma (baby steps)")
ax[1].grid(alpha=.3, which="both"); ax[1].legend(fontsize=8)

fig.tight_layout()
sal = os.path.join(RAIZ, "figuras", "fig10_1_escalado.png")
fig.savefig(sal, dpi=150)
print("\nfigura ->", sal)
