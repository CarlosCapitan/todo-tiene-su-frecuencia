#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprobaciones antes de dar por bueno el resultado anterior."""
import json, numpy as np
from scipy.io import loadmat
from scipy.stats import beta
import rodamiento as R

meta = json.load(open('../datos/indice.json'))
CARGA = {l: int(l.rsplit('_',1)[1]) for l in meta}
def señal(lab):
    m = meta[lab]; d = loadmat(f"../datos/{m['f']}.mat")
    k = [kk for kk in d if kk.endswith('DE_time') and str(m['f']) in kk][0]
    return d[k].ravel().astype(float), m['rpm']

print("="*74)
print("1. ¿ES ARTEFACTO DEL TROCEADO? z sobre el REGISTRO ENTERO")
print("="*74)
zr = {}
for lab in meta:
    if not lab.startswith('normal'): continue
    x, rpm = señal(lab); zr[lab] = R.diagnose_v3(x, rpm)['zmax']
    print(f"  {lab:<12} carga {CARGA[lab]}   z = {zr[lab]:.2f}")
print("\n  Si el registro sano de carga 3 ya destaca sobre el registro entero,")
print("  el efecto es de la CARGA, no de la ventana.")

filas = json.load(open('../datos/cwru_ventanas.json'))
san = [f for f in filas if f['sano']]; fal = [f for f in filas if not f['sano']]

def cota(k, n, a=0.05): return 1.0 if k == n else float(beta.ppf(1-a, k+1, n-k))

print("\n" + "="*74)
print("2. DEJA UNA CARGA FUERA, LAS CUATRO VECES")
print("="*74)
print("  (calibrar con tres cargas sanas, validar con la cuarta)\n")
print(f"  {'carga fuera':>12}{'umbral':>9}{'falsos pos.':>14}{'tasa':>8}{'cota 95%':>10}"
      f"{'detecta':>10}")
tot_fp = tot_n = 0
for L in (0, 1, 2, 3):
    cal = [f for f in san if f['carga'] != L]
    val = [f for f in san if f['carga'] == L]
    U = max(f['zmax'] for f in cal)
    fp = sum(f['zmax'] > U for f in val)
    det = sum(f['zmax'] > U for f in fal)
    tot_fp += fp; tot_n += len(val)
    print(f"  {L:>12}{U:>9.2f}{fp:>10}/{len(val):<3}{fp/len(val):>8.0%}"
          f"{cota(fp,len(val)):>10.0%}{det:>7}/{len(fal)}")
print(f"\n  AGREGADO: {tot_fp}/{tot_n} = {tot_fp/tot_n:.1%}   "
      f"cota superior al 95 %: {cota(tot_fp, tot_n):.1%}")

print("\n" + "="*74)
print("3. ¿Y SI EL UMBRAL SE FIJA CON MARGEN, NO CON EL MAXIMO?")
print("="*74)
print("  Umbral = percentil de las ventanas sanas de calibracion.\n")
print(f"  {'percentil':>11}{'falsos pos. agregados':>24}{'detecta':>12}")
for q in (100, 99, 95, 90):
    fpq = nq = detq = 0
    for L in (0,1,2,3):
        cal = [f['zmax'] for f in san if f['carga'] != L]
        val = [f for f in san if f['carga'] == L]
        U = np.percentile(cal, q)
        fpq += sum(f['zmax'] > U for f in val); nq += len(val)
        detq += sum(f['zmax'] > U for f in fal)
    print(f"  {q:>10}%{fpq:>16}/{nq:<3}{detq:>9}/{4*len(fal)}")
print("\n  Bajar el umbral sube la deteccion y sube los falsos positivos.")
print("  No hay ningun punto donde las dos cosas salgan bien: el problema")
print("  no es donde se pone la raya, es que las cargas no son comparables.")

print("\n" + "="*74)
print("4. LA CAUSA: el nivel de fondo depende de la carga")
print("="*74)
for L in (0,1,2,3):
    v = [f['zmax'] for f in san if f['carga'] == L]
    print(f"  carga {L}: z de las ventanas sanas  mediana {np.median(v):.2f}   "
          f"maximo {max(v):.2f}   (n={len(v)})")
