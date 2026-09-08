"""Tabla y figura 2.1 — la matriz control x metodo debe salir diagonal."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras

import numpy as np, bateria as B, json
N=50000
C=B.controles(N)
esc=np.logspace(np.log10(4),np.log10(3000),44)
filas={}
print("="*104)
print("MATRIZ DE CALIBRACION — cada control debe caer ante SU metodo y ante ningun otro")
print("="*104)
print(f"{'control':<28}{'CICLO@288':>11}{'CICLO@2016':>12}{'BICOH':>8}{'TF':>8}{'Lyapunov':>10}  FNN(m=1..6)")
print("-"*104)
for nm,x in C.items():
    cs=B.ciclo_snr(x); bi=B.bicoherencia(x); tf=B.tf_max(x,esc)
    ly=B.lyapunov(x[:20000]); ms,fnn=B.falsos_vecinos(x[:20000],ms=range(1,7))
    filas[nm]=dict(c288=cs[288],c2016=cs[2016],bic=bi,tf=tf,lyap=ly,fnn=fnn)
    print(f"{nm:<28}{cs[288]:>11.1f}{cs[2016]:>12.1f}{bi:>8.2f}{tf:>8.1f}{ly:>10.3f}  "
          +" ".join(f"{v:.2f}" for v in fnn))
json.dump(filas,open(figuras('cap2_matriz.json'),'w'),indent=1)
base=filas['A · ruido blanco']
print(f"""
LECTURA
  A es la linea base. B debe disparar solo CICLO@288 (x{filas['B · AM ciclo 288']['c288']/base['c288']:.0f} sobre la base).
  C debe disparar solo BICOH (x{filas['C · acoplamiento de fases']['bic']/base['bic']:.1f}).
  D debe disparar solo TF (x{filas['D · ráfaga transitoria']['tf']/base['tf']:.0f}).
  E debe dar Lyapunov alto ({filas['E · Hénon (caos)']['lyap']:.3f} frente a {base['lyap']:.3f}) y FNN que colapsa.
  El valor teorico del Lyapunov de Henon es ~0,42: el instrumento no solo detecta, mide.""")
