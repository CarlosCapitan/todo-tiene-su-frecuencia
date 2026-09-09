#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cap8_fase3.py — cuatro metodos mas alla de Fourier + surrogados IAAFT.
Produce las dos tablas de las secciones 8.2 y 8.3, y los dos CSV de los
que se dibuja la figura 8.1.

Requiere haber ejecutado antes:  features.py  ->  resid.py

Todo se mide con la MISMA implementacion (spec.py). En la primera version del
libro la tabla 8.2 salia de bateria.py y la 8.3 de spec.py: dos implementaciones
del mismo estadistico dando numeros distintos. Unificado.
"""
import os, sys, csv, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos
import numpy as np, spec as S

ESCALAS = np.arange(4, 128, 4)
NR = int(os.environ.get("N_SURROGADOS", "80"))
rng = np.random.default_rng(11)

def normaliza(x):
    x = np.asarray(x, float); m = np.isfinite(x)
    if not m.all(): x = np.where(m, x, np.median(x[m]))
    return (x - x.mean())/(x.std() or 1)

def cuatro(x):
    c = S.cyclo_stat(x)['targets']
    return (c[288]['snr'], c[2016]['snr'],
            S.bic_stat(x)['ratio'], S.tf_stat(x, ESCALAS)['max'])

d = np.load(datos('series.npz'), allow_pickle=True)
X = {k: normaliza(d[k]) for k in ('x', 'r', 'mag')}
N = len(X['x'])

# controles de referencia, de la misma longitud que las series reales
blanco = normaliza(rng.standard_normal(N))
t = np.arange(N)
am = normaliza((1 + 0.30*np.sin(2*np.pi*t/288))*rng.standard_normal(N))

FILAS = [("ruido_blanco_calibracion", blanco),
         ("signo_crudo",              X['x']),
         ("residuo_blanqueado",       X['r']),
         ("magnitud_log_ret",         X['mag']),
         ("control_AM_ciclo288",      am)]

print("="*104)
print(f"FASE 3 — cuatro metodos, {N} muestras")
print("="*104)
print(f"{'serie':<30}{'CICLO@288':>11}{'CICLO@2016':>12}{'BICOH':>9}{'TF max':>9}{'Lyapunov':>10}{'D2(m=6)':>9}")
obs = {}
with open(datos('polymarket_fase3.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['serie','ciclo288','ciclo2016','bicoh','tf_max','lyapunov','d2_m6'])
    for nom, x in FILAS:
        c288, c2016, bi, tf = cuatro(x); obs[nom] = (c288, c2016, bi, tf)
        ly, _ = S.lyapunov_rosenstein(x, rng=np.random.default_rng(7))
        d2 = S.corr_dim(x, rng=np.random.default_rng(7))
        w.writerow([nom, f"{c288:.2f}", f"{c2016:.2f}", f"{bi:.2f}", f"{tf:.2f}",
                    f"{ly:.3f}", f"{d2:.2f}"])
        print(f"{nom:<30}{c288:11.2f}{c2016:12.2f}{bi:9.2f}{tf:9.2f}{ly:10.3f}{d2:9.2f}")

print(f"\n--- SURROGADOS IAAFT ({NR} replicas por serie) ---")
print("conservan el espectro de potencia Y la distribucion de amplitudes\n")
with open(datos('polymarket_surrogados_iaaft.csv'), 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['serie','estadistico','real','nula_media','nula_p95','nula_max','p_empirico'])
    for nom in ("signo_crudo", "residuo_blanqueado", "magnitud_log_ret"):
        x = dict(FILAS)[nom]
        nul = [[], [], [], []]; t0 = time.time()
        for _ in range(NR):
            for k, v in enumerate(cuatro(S.iaaft(x, rng=rng))): nul[k].append(v)
        print(f"{nom}   [{time.time()-t0:.0f}s]")
        print(f"   {'estadistico':<14}{'real':>9}{'nula media':>12}{'nula p95':>10}{'p empirico':>12}")
        for et, o, v in zip(("ciclo288","ciclo2016","bicoh","tf"), obs[nom], nul):
            v = np.array(v); p = (1 + (v >= o).sum())/(1 + len(v))
            w.writerow([nom, et, f"{o:.2f}", f"{v.mean():.2f}",
                        f"{np.percentile(v,95):.2f}", f"{v.max():.2f}", f"{p:.4f}"])
            print(f"   {et:<14}{o:9.2f}{v.mean():12.2f}{np.percentile(v,95):10.2f}{p:12.4f}")

print(f"\nCSV escritos: polymarket_fase3.csv y polymarket_surrogados_iaaft.csv")
