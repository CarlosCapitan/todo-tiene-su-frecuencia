#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cap6_bateria.py — bateria criptoanalitica sobre el keystream de Polymarket.
Reproduce las tablas de las secciones 6.2, 6.3 y 6.4.

Requiere haber ejecutado antes:  download.py  ->  candles.py  ->  features.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos
import pickle, numpy as np, lib as L

d = pickle.load(open(datos('data.pkl'), 'rb'))
b = d['bits'].astype(np.int8)
n = len(b)
print("="*74)
print(f"KEYSTREAM POLYMARKET  btc-up-or-down-5m   ·   {n} bits")
print("="*74)

mb = L.monobit(b);            print(f"[1] MONOBIT       Up={int(b.sum())} Down={n-int(b.sum())}  p(Up)={b.mean():.5f}  z={mb['z']:.3f}  p={mb['p']:.4f}")
rt = L.runs_test(b);          print(f"[2] RACHAS        z={rt.get('z',float('nan')):.3f}  p={rt['p']:.4f}")
lr = L.longest_run_ones(b);   print(f"[3] RACHA MAX     {lr}")
dt = L.nist_dft(b);           print(f"[4] NIST DFT      p={dt['p']:.4f}")
mu = L.maurer_universal(b);   print(f"[6] MAURER        fn={mu['fn']:.5f}  z={mu['z']:.3f}  p={mu['p']:.4f}")
ae = L.approx_entropy(b);     print(f"[7] ApEn(m=10)    {ae:.6f}   (ln2 = 0.693147)")
Lc, _ = L.berlekamp_massey(b)
print(f"[8] BERLEKAMP-MASSEY  L = {Lc}  sobre {n} bits   (esperado n/2 = {n//2})   ratio = {Lc/(n/2):.4f}")
nl = L.nist_linear_complexity(b);  print(f"[9] NIST LinComp  chi2={nl['chi2']:.2f}  p={nl['p']:.4f}")

print("\n--- WALSH-HADAMARD: criptoanalisis lineal ---")
for k in (12, 16, 20):
    z = L.walsh_linear(b, k=k)
    N = 2**k - 1
    umb = np.sqrt(2*np.log(N))
    print(f"  k={k:2d}  {N:>9,} mascaras   max|z|={np.abs(z).max():.2f}   umbral sqrt(2 ln N)={umb:.2f}   por encima: {int((np.abs(z)>umb).sum())}")

print("\n--- AUTOCORRELACION ---")
r = np.asarray(L.autocorr(b, 4000), float)[1:]   # r[0] es el desfase 0
z = r*np.sqrt(n)
i = int(np.argmax(np.abs(z)))
print(f"  max |z| sobre 4000 desfases = {abs(z[i]):.2f} en el desfase {i+1}")
print(f"  umbral por comparacion multiple = {np.sqrt(2*np.log(4000)):.2f}")
print(f"  r(1) = {r[0]:+.5f}   z = {z[0]:+.2f}")
