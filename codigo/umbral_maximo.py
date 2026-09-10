#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
umbral_maximo.py — que es exactamente sqrt(2 ln N), y que no es.

sqrt(2 ln N) es el valor TIPICO del maximo de N normales independientes. No es
su cuantil 95. Usarlo como umbral de significacion es usar un criterio mas
permisivo de lo que se anuncia, y el libro lo hacia.

Aqui se calculan las dos cosas al lado, y se comprueba por simulacion:

  · sqrt(2 ln N)          el maximo tipico
  · P(max|z| > eso)       cuantas veces lo supera el ruido puro
  · umbral al 5 %         el cuantil 95 del maximo, que es lo que hay que usar
"""
import numpy as np
from scipy.stats import norm

def umbral_5(N, alfa=0.05):
    """Cuantil 1-alfa del maximo de |z| sobre N pruebas independientes.
    Exacto bajo independencia: P(todas por debajo de u) = (1-2(1-Phi(u)))^N."""
    return float(norm.ppf(1 - (1 - (1-alfa)**(1.0/N))/2))

def p_supera(N, u):
    """P(el maximo de |z| sobre N pruebas supere u), bajo la nula."""
    return float(1 - (1 - 2*(1-norm.cdf(u)))**N)

def simula(N, reps, rng):
    out = np.empty(reps); lote = max(1, int(4e7//N)); i = 0
    while i < reps:
        m = min(lote, reps-i)
        out[i:i+m] = np.abs(rng.standard_normal((m, N))).max(1); i += m
    return out

rng = np.random.default_rng(7)
NS = [30, 63, 82, 255, 1023, 4000, 4095, 16383, 65535, 262143, 1048575]

print("="*84)
print("EL MAXIMO TIPICO NO ES EL UMBRAL AL 5 %")
print("="*84)
print(f"{'N':>9}{'sqrt(2 lnN)':>13}{'P(lo supera)':>14}{'umbral 5 %':>12}"
      f"{'Bonferroni':>12}{'diferencia':>12}")
for N in NS:
    t = np.sqrt(2*np.log(N)); u5 = umbral_5(N); bf = norm.ppf(1-0.025/N)
    print(f"{N:>9}{t:>13.3f}{p_supera(N,t):>13.1%}{u5:>12.3f}{bf:>12.3f}{u5-t:>12.3f}")

print("\n" + "="*84)
print("COMPROBACION POR SIMULACION")
print("="*84)
print(f"{'N':>9}{'reps':>10}{'P(supera) teorica':>20}{'medida':>10}"
      f"{'umbral 5 % teorico':>21}{'medido':>10}")
for N, reps in ((82, 200_000), (4095, 60_000), (65535, 8_000)):
    M = simula(N, reps, rng); t = np.sqrt(2*np.log(N))
    print(f"{N:>9}{reps:>10,}{p_supera(N,t):>19.1%}{(M>t).mean():>10.1%}"
          f"{umbral_5(N):>21.3f}{np.percentile(M,95):>10.3f}")

print("\n  Entre el 15 % y el 22 % de las veces el ruido puro supera sqrt(2 ln N).")
print("  No es el 5 %, y tampoco es la mitad: es eso.")
print("\n  OJO: todo lo anterior supone N pruebas INDEPENDIENTES. Cuando se")
print("  solapan -desfases contiguos, mascaras parecidas, rejillas de")
print("  parametros- el N efectivo es menor y estos umbrales se pasan de")
print("  duros. Ver el apartado 9.7.")
