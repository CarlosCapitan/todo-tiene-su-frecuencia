#!/usr/bin/env python3
"""Tabla de la seccion 6.5: diagnostico ciego de los 18 registros."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras

import numpy as np, json
from scipy.io import loadmat
import rodamiento as R
meta=json.load(open(datos('indice.json')))
def carga(lab):
    m=meta[lab]; d=loadmat(f"datos/{m['f']}.mat")
    k=[kk for kk in d if kk.endswith('DE_time') and str(m['f']) in kk][0]
    return d[k].ravel().astype(float), m['rpm']
def verdad(l): return 'sano' if l.startswith('normal') else ('BPFI' if l.startswith('IR') else ('BSF2' if l.startswith('B0') else 'BPFO'))
print(f"{'registro':<14}{'verdad':>8}{'diagnostico':>12}{'z':>7}{'p':>9}")
print("-"*52)
res={}
for lab in meta:
    x,rpm=carga(lab); r=R.diagnose_v3(x,rpm); res[lab]=r
    print(f"{lab:<14}{verdad(lab):>8}{r['ganador']:>12}{r['zmax']:>7.1f}{r['pmin']:>9.4f}")
UMB=max(res[l]['zmax'] for l in meta if l.startswith('normal'))
fal=[l for l in meta if not l.startswith('normal')]
det=sum(res[l]['zmax']>UMB for l in fal)
cls=sum(res[l]['zmax']>UMB and res[l]['ganador']==verdad(l) for l in fal)
print(f"\numbral z={UMB:.1f} (maximo en sanos) | detecta {det}/{len(fal)} | clasifica {cls}/{len(fal)}")

# ERROR CORREGIDO. Aqui se imprimia "falsos positivos 0/4", contando cuantos de
# los cuatro sanos superaban un umbral definido como el MAXIMO de esos mismos
# cuatro. Es cero por teorema, no por medicion: un elemento no supera el maximo
# del conjunto al que pertenece. La linea se ha quitado.
#
# La tasa de falsos positivos honesta se mide en cwru_fuera_de_muestra.py y
# cwru_loo.py, partiendo por carga del motor: 28,6 %, cota al 95 % del 45,7 %,
# y toda ella concentrada en la carga 3. Ver apartado 4.6 y apendice A.8.
print("falsos positivos: ver cwru_loo.py — aqui no se pueden medir sin circularidad")
