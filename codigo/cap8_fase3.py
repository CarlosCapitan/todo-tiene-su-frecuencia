#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cap8_fase3.py — cuatro metodos mas alla de Fourier + surrogados IAAFT.
Reproduce las tablas de las secciones 8.2, 8.3 y 8.4.

Requiere haber ejecutado antes:  features.py  ->  resid.py
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos
import numpy as np, spec as S

d = np.load(datos('series.npz'), allow_pickle=True)
SERIES = [("SIGNO crudo (+-1)", d['x']),
          ("RESIDUO blanqueado", d['r']),
          ("MAGNITUD log|ret| (control +)", d['mag'])]
NR = int(os.environ.get("N_SURROGADOS", "80"))

print("="*96)
print(f"FASE 3 — cuatro metodos, {len(d['x'])} muestras")
print("="*96)
print(f"{'serie':<34}{'CICLO@288':>11}{'CICLO@2016':>12}{'BICOH':>9}{'TF max':>9}")
res = {}
for nom, x in SERIES:
    x = np.asarray(x, float)
    m = np.isfinite(x)
    if not m.all(): x = np.where(m, x, np.median(x[m]))
    x = (x - x.mean())/(x.std() or 1)
    c = S.cyclo_stat(x)['targets']
    c288, c2016 = c[288]['snr'], c[2016]['snr']
    bi = S.bic_stat(x)['ratio']; tf = S.tf_stat(x, np.arange(4, 128, 4))['max']
    res[nom] = (c288, c2016, bi, tf)
    print(f"{nom:<34}{c288:11.1f}{c2016:12.1f}{bi:9.2f}{tf:9.1f}")

print(f"\n--- SURROGADOS IAAFT ({NR} replicas por serie) ---")
print("conservan el espectro de potencia Y la distribucion de amplitudes\n")
rng = np.random.default_rng(11)
for nom, x in SERIES:
    x = np.asarray(x, float)
    m = np.isfinite(x)
    if not m.all(): x = np.where(m, x, np.median(x[m]))
    x = (x - x.mean())/(x.std() or 1)
    obs = res[nom]; nul = [[], [], [], []]
    t0 = time.time()
    for _ in range(NR):
        s = S.iaaft(x, rng=rng)
        c = S.cyclo_stat(s)['targets']
        nul[0].append(c[288]['snr']); nul[1].append(c[2016]['snr'])
        nul[2].append(S.bic_stat(s)['ratio'])
        nul[3].append(S.tf_stat(s, np.arange(4, 128, 4))['max'])
    print(f"{nom}   [{time.time()-t0:.0f}s]")
    print(f"   {'estadistico':<14}{'real':>8}{'nula media':>12}{'nula p95':>10}{'p empirico':>12}")
    for et, o, v in zip(("ciclo288","ciclo2016","bicoh","tf"), obs, nul):
        v = np.array(v); p = (1 + (v >= o).sum())/(1 + len(v))
        print(f"   {et:<14}{o:8.2f}{v.mean():12.2f}{np.percentile(v,95):10.2f}{p:12.4f}")
