#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Leave-one-load-out de la puerta de existencia (SK), estructura de cwru_loo.py
pero con el estadistico de la ETAPA 1 (spectral_kurtosis_band) en vez de la z de
frecuencia de la etapa 2. Mismas ventanas de 5 s, misma particion por carga,
umbral = maximo SK de las ventanas sanas de las cargas de calibracion."""
import json, numpy as np
from scipy.io import loadmat
from scipy.stats import beta
import rodamiento as R

VENT = 60_000          # 5 segundos a 12 kHz
meta = json.load(open('../datos/indice.json'))
CARGA = {l: int(l.rsplit('_', 1)[1]) for l in meta}

def señal(lab):
    m = meta[lab]; d = loadmat(f"../datos/{m['f']}.mat")
    k = [kk for kk in d if kk.endswith('DE_time') and str(m['f']) in kk][0]
    return d[k].ravel().astype(float)

def verdad(l):
    return 'sano' if l.startswith('normal') else ('BPFI' if l.startswith('IR')
           else ('BSF2' if l.startswith('B0') else 'BPFO'))

print("="*74)
print("PUERTA DE EXISTENCIA (SK, etapa 1): LEAVE-ONE-LOAD-OUT")
print("="*74)
filas = []
for lab in meta:
    x = señal(lab)
    n = len(x)//VENT
    for i in range(n):
        _, sk = R.spectral_kurtosis_band(x[i*VENT:(i+1)*VENT])
        filas.append(dict(reg=lab, vent=i, carga=CARGA[lab], sano=lab.startswith('normal'),
                          verdad=verdad(lab), sk=sk))

san = [f for f in filas if f['sano']]
fal = [f for f in filas if not f['sano']]
print(f"\n  ventanas sanas: {len(san)}   con fallo: {len(fal)}")

def cota(k, n, a=0.05): return 1.0 if k == n else float(beta.ppf(1-a, k+1, n-k))

print("\n" + "="*74)
print("DEJA UNA CARGA FUERA, LAS CUATRO VECES")
print("="*74)
print("  (calibrar con tres cargas sanas, validar con la cuarta; umbral = maximo SK sano)\n")
print(f"  {'carga fuera':>12}{'umbral SK':>11}{'falsos pos.':>14}{'tasa':>8}{'cota 95%':>10}"
      f"{'detecta':>10}")
tot_fp = tot_n = 0
for L in (0, 1, 2, 3):
    cal = [f for f in san if f['carga'] != L]
    val = [f for f in san if f['carga'] == L]
    U = max(f['sk'] for f in cal)
    fp = sum(f['sk'] > U for f in val)
    det = sum(f['sk'] > U for f in fal)
    tot_fp += fp; tot_n += len(val)
    print(f"  {L:>12}{U:>11.2f}{fp:>10}/{len(val):<3}{fp/len(val):>8.0%}"
          f"{cota(fp,len(val)):>10.0%}{det:>7}/{len(fal)}")
print(f"\n  AGREGADO: {tot_fp}/{tot_n} = {tot_fp/tot_n:.1%}   "
      f"cota superior al 95 %: {cota(tot_fp, tot_n):.1%}")
