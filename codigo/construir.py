#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
construir.py — une la descarga de Polymarket con las velas de Coinbase.

Entrada:  datos/raw.jsonl    (download.py)
          datos/candles.json (candles.py)
Salida:   datos/data.pkl     con ts, bits, vol y el diccionario de velas

El bit es 1 ("Up") cuando el precio de liquidacion del resultado "Up" es 1.
Solo se conservan los mercados CERRADOS y con resolucion limpia (0/1): los
que siguen abiertos o quedaron sin resolver se descartan y se informa cuantos.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos
import json, pickle, numpy as np

filas, descartados = {}, 0
for linea in open(datos('raw.jsonl')):
    r = json.loads(linea)
    if not r.get('closed'):
        descartados += 1; continue
    oc, pr = r.get('outcomes') or [], r.get('prices') or []
    if len(oc) != 2 or len(pr) != 2:
        descartados += 1; continue
    try:
        p = [float(x) for x in pr]
    except ValueError:
        descartados += 1; continue
    if sorted(p) != [0.0, 1.0]:          # resolucion no limpia
        descartados += 1; continue
    i_up = oc.index('Up') if 'Up' in oc else 0
    filas[int(r['ts'])] = (int(p[i_up] == 1.0), float(r.get('vol') or 0.0))

ts = np.array(sorted(filas), dtype=np.int64)
bits = np.array([filas[t][0] for t in ts], dtype=np.int8)
vol  = np.array([filas[t][1] for t in ts], dtype=float)

cd = {int(k): v for k, v in json.load(open(datos('candles.json'))).items()}

pickle.dump(dict(ts=ts, bits=bits, vol=vol, cd=cd), open(datos('data.pkl'), 'wb'))
print(f"data.pkl:  {len(ts)} resoluciones  ({descartados} descartadas)  ·  {len(cd)} velas")
print(f"  rango: {ts[0]} -> {ts[-1]}   p(Up) = {bits.mean():.5f}")
