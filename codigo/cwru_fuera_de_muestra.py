#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cwru_fuera_de_muestra.py — el umbral del capitulo 4, sin circularidad.

EL PROBLEMA. En la primera version, diagnostico.py hacia esto:

    UMB = max(zmax de los cuatro registros sanos)
    fp  = cuantos de esos MISMOS cuatro superan UMB

El segundo numero no puede ser otra cosa que cero. No es que la tasa de falsos
positivos saliera baja: es que no podia salir de ninguna otra manera. Un elemento
de un conjunto no supera el maximo de ese conjunto.

EL ARREGLO. Se parte por CARGA, que es la variable fisica que cambia entre
registros, y se trocea cada registro en ventanas para que haya n suficiente:

  · calibracion: ventanas sanas de las cargas 0 y 1  -> de ahi sale el umbral
  · validacion : ventanas sanas de las cargas 2 y 3  -> nunca vistas al calibrar

CWRU no permite mas: su linea base normal son cuatro ficheros, uno por carga.
No hay mas rodamientos sanos que conseguir. Lo que si se puede es medir sobre
ventanas independientes, que ademas es como se usaria el detector de verdad:
sobre un trozo de vibracion, no sobre "un rodamiento".
"""
import json, sys, numpy as np
from scipy.io import loadmat
import rodamiento as R

VENT = 60_000          # 5 segundos a 12 kHz
meta = json.load(open('../datos/indice.json'))

def señal(lab):
    m = meta[lab]; d = loadmat(f"../datos/{m['f']}.mat")
    k = [kk for kk in d if kk.endswith('DE_time') and str(m['f']) in kk][0]
    return d[k].ravel().astype(float), m['rpm'], m['carga'] if 'carga' in m else None

def verdad(l):
    return 'sano' if l.startswith('normal') else ('BPFI' if l.startswith('IR')
           else ('BSF2' if l.startswith('B0') else 'BPFO'))

CARGA = {l: int(l.rsplit('_', 1)[1]) for l in meta}

print("="*78)
print("VENTANAS DE 5 SEGUNDOS, DIAGNOSTICADAS UNA A UNA")
print("="*78)
filas = []
for lab in meta:
    x, rpm, _ = señal(lab)
    n = len(x)//VENT
    for i in range(n):
        r = R.diagnose_v3(x[i*VENT:(i+1)*VENT], rpm)
        filas.append(dict(reg=lab, vent=i, carga=CARGA[lab], sano=lab.startswith('normal'),
                          verdad=verdad(lab), zmax=r['zmax'], gan=r['ganador']))
    print(f"  {lab:<14} carga {CARGA[lab]}  {n:>2} ventanas")

san = [f for f in filas if f['sano']]
fal = [f for f in filas if not f['sano']]
print(f"\n  ventanas sanas: {len(san)}   con fallo: {len(fal)}")

# ---------------- lo que hacia la primera version -----------------------------
print("\n" + "="*78)
print("A. LO QUE HACIA LA PRIMERA VERSION (por registro entero, circular)")
print("="*78)
zs_reg = {}
for lab in meta:
    x, rpm, _ = señal(lab)
    zs_reg[lab] = R.diagnose_v3(x, rpm)
U0 = max(zs_reg[l]['zmax'] for l in meta if l.startswith('normal'))
fp0 = sum(zs_reg[l]['zmax'] > U0 for l in meta if l.startswith('normal'))
det0 = sum(zs_reg[l]['zmax'] > U0 for l in meta if not l.startswith('normal'))
print(f"  umbral = maximo de los 4 sanos = {U0:.2f}")
print(f"  falsos positivos sobre esos mismos 4: {fp0}/4   <- no podia dar otra cosa")
print(f"  detecta {det0}/14")

# ---------------- el arreglo ---------------------------------------------------
print("\n" + "="*78)
print("B. CALIBRAR CON LAS CARGAS 0 Y 1, VALIDAR CON LAS CARGAS 2 Y 3")
print("="*78)
cal = [f for f in san if f['carga'] in (0, 1)]
val = [f for f in san if f['carga'] in (2, 3)]
U = max(f['zmax'] for f in cal)
print(f"  ventanas de calibracion (sanas, cargas 0-1): {len(cal)}")
print(f"  umbral z = {U:.2f}")
print(f"  ventanas de validacion  (sanas, cargas 2-3): {len(val)}   <- nunca vistas")
fp = sum(f['zmax'] > U for f in val)
print(f"\n  FALSOS POSITIVOS FUERA DE MUESTRA: {fp}/{len(val)}")

def clopper_sup(k, n, alfa=0.05):
    from scipy.stats import beta
    return 1.0 if k == n else float(beta.ppf(1-alfa, k+1, n-k))
sup = clopper_sup(fp, len(val))
print(f"  tasa estimada: {fp/len(val):.1%}   cota superior al 95 %: {sup:.1%}")
print(f"  (con los 2 registros enteros que quedan fuera seria 0/2, cota {clopper_sup(0,2):.0%}:")
print(f"   por eso hace falta trocear, no por comodidad)")

det = sum(f['zmax'] > U for f in fal)
cls = sum(f['zmax'] > U and f['gan'] == f['verdad'] for f in fal)
print(f"\n  detecta {det}/{len(fal)} ventanas con fallo   ({det/len(fal):.0%})")
print(f"  y de las detectadas, clasifica bien {cls}/{det}   ({cls/max(det,1):.0%})")

print("\n" + "="*78)
print("C. POR REGISTRO, CON EL UMBRAL HONESTO")
print("="*78)
print(f"  {'registro':<14}{'carga':>6}{'verdad':>8}{'ventanas':>10}{'sobre umbral':>14}{'z medio':>9}")
for lab in meta:
    g = [f for f in filas if f['reg'] == lab]
    n_sup = sum(f['zmax'] > U for f in g)
    marca = ""
    if lab.startswith('normal') and CARGA[lab] in (2, 3): marca = "  <- validacion"
    print(f"  {lab:<14}{CARGA[lab]:>6}{verdad(lab):>8}{len(g):>10}{n_sup:>10}/{len(g):<3}"
          f"{np.mean([f['zmax'] for f in g]):>9.2f}{marca}")

json.dump(filas, open('../datos/cwru_ventanas.json', 'w'))
print("\n  guardado datos/cwru_ventanas.json")
