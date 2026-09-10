#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mismo_fenomeno.py — ¿la reversion del capitulo 7 y el rebote del capitulo 9
son el mismo fenomeno?

La prueba directa: el bit de Polymarket es, por definicion del mercado, el signo
del movimiento de BTC en una ventana de cinco minutos. Si el signo del retorno
de BTC a cinco minutos tiene la misma autocorrelacion que la secuencia de
Polymarket, entonces el "hallazgo" del capitulo 7 es microestructura de BTC
pasada por el mercado de apuestas, y el veredicto del capitulo 9 -vive dentro
del coste de operar, y se esta extinguiendo- se le aplica hacia atras.
"""
import os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, '..'))
from rutas import datos as datos_libro

import pickle, numpy as np, datetime as dt

d = pickle.load(open(datos_libro('data.pkl'), 'rb'))
ts, bits, cd = d['ts'], d['bits'].astype(int), d['cd']

# --- signo del retorno de BTC a 5 minutos, en los mismos instantes ------------
cierre = {int(k): float(v[4]) for k, v in cd.items()}
s_btc = np.full(len(ts), -1, np.int8)
for i, t in enumerate(ts):
    t = int(t)
    a, b = cierre.get(t - 300), cierre.get(t)
    if a is not None and b is not None and a != b:
        s_btc[i] = 1 if b > a else 0
ok = s_btc >= 0
print("="*74)
print("¿ES EL MISMO OBJETO?")
print("="*74)
print(f"  ventanas de Polymarket            : {len(ts):,}")
print(f"  con vela de BTC a los dos extremos: {ok.sum():,}  ({ok.mean():.1%})")
ac = (bits[ok] == s_btc[ok]).mean()
print(f"  el bit de Polymarket coincide con el signo del retorno de BTC: {ac:.2%}")

def r1(b):
    x = 2.0*b - 1.0; x = x - x.mean()
    return float(np.dot(x[:-1], x[1:]) / np.dot(x, x))

def z_de(r, n): return r*np.sqrt(n)

print("\n" + "="*74)
print("LA AUTOCORRELACION A UN PASO, EN LOS DOS")
print("="*74)
for nom, b in (("bits de Polymarket", bits[ok]), ("signo del retorno de BTC", s_btc[ok])):
    r = r1(b); n = len(b)
    print(f"  {nom:<28} r(1) = {r:+.5f}   z = {z_de(r,n):+.2f}   n = {n:,}")

# --- los ocho tramos, en los dos ---------------------------------------------
print("\n" + "="*74)
print("LOS OCHO TRAMOS: ¿se mueven juntos?")
print("="*74)
bp, bb = bits[ok], s_btc[ok]
m = len(bp)//8
print(f"  {'tramo':>6}{'Polymarket r(1)':>18}{'z':>8}{'BTC 5m r(1)':>15}{'z':>8}")
rp, rb = [], []
for i in range(8):
    a, c = i*m, (i+1)*m
    r1p, r1b = r1(bp[a:c]), r1(bb[a:c])
    rp.append(r1p); rb.append(r1b)
    print(f"  {i+1:>6}{r1p:>18.5f}{z_de(r1p,m):>8.2f}{r1b:>15.5f}{z_de(r1b,m):>8.2f}")
print(f"\n  correlacion entre las dos series de ocho valores: {np.corrcoef(rp,rb)[0,1]:+.4f}")

# --- ¿se extingue? ------------------------------------------------------------
print("\n" + "="*74)
print("¿SE ESTA EXTINGUIENDO, COMO EL DEL CAPITULO 9?")
print("="*74)
h = len(bp)//2
for nom, b in (("Polymarket", bp), ("BTC 5m", bb)):
    print(f"  {nom:<12} primera mitad r(1) = {r1(b[:h]):+.5f}   "
          f"segunda mitad r(1) = {r1(b[h:]):+.5f}")

# --- la misma medida a escala horaria, en la MISMA ventana temporal -----------
import json
print("\n" + "="*74)
print("LA MISMA MEDIDA A ESCALA HORARIA, EN LA MISMA VENTANA DE FECHAS")
print("="*74)
p = os.path.join(AQUI, "datos", "btc_1h.json")   # generado por codigo/btc/descargar.py
if os.path.exists(p):
    H = {int(v[0]): float(v[4]) for v in json.load(open(p))}
    th = np.array(sorted(H)); ph = np.array([H[t] for t in th])
    t0, t1 = int(ts[0]), int(ts[-1])
    m = (th >= t0) & (th <= t1)
    ph2 = ph[m]
    s = (np.diff(ph2) > 0).astype(int)
    print(f"  velas horarias en la ventana de Polymarket: {len(s):,}")
    print(f"  signo horario  r(1) = {r1(s):+.5f}   z = {z_de(r1(s), len(s)):+.2f}")
    # y el conjunto entero de 4 anos, para comparar
    s4 = (np.diff(ph) > 0).astype(int)
    print(f"  signo horario, los 4 anos enteros: r(1) = {r1(s4):+.5f}   "
          f"z = {z_de(r1(s4), len(s4)):+.2f}   n = {len(s4):,}")
else:
    print("  (no estan los datos horarios)")
