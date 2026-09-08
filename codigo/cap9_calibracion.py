#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nula para la distancia del mejor candidato espectral a la fase verdadera.

El prefiltro devuelve una lista ordenada de 32 fases candidatas. La metrica
publicada es la distancia circular minima entre la fase verdadera d mod 2^k y
la mejor de esas 32, normalizada por 2^k.

La nula correcta NO es "una fase al azar" (que daria 0,25): es el MINIMO de 32
fases al azar, porque el algoritmo tambien se queda con la mejor de 32.
"""
import random

N_CAND = 32
REPS = 200_000
OBS_MEDIANA, OBS_MEDIA = 0.0645, 0.0659   # medidos sobre 3.694 corridas

rng = random.Random(7)
nul = sorted(min(abs(rng.random() - 0.5) for _ in range(N_CAND)) for _ in range(REPS))
med = nul[len(nul) // 2]
mea = sum(nul) / len(nul)

print(f"nula: minimo de {N_CAND} fases uniformes ({REPS:,} repeticiones)")
print(f"   mediana = {med:.4f}   media = {mea:.4f}")
print(f"observado en las corridas reales")
print(f"   mediana = {OBS_MEDIANA:.4f}   media = {OBS_MEDIA:.4f}")
print(f"\nel mejor candidato espectral esta {OBS_MEDIANA/med:.1f} veces MAS LEJOS")
print("de la fase verdadera que 32 tiros al azar.")
