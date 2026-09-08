#!/usr/bin/env python3
"""Descarga los 18 registros etiquetados del Bearing Data Center (Case Western).
Los datos son publicos y se descargan de origen; no se redistribuyen con el libro."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras, DATOS

import urllib.request, os, json
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/125 Safari/537.36'
BASE='https://engineering.case.edu/sites/default/files'
IDX={'normal_0':(97,1797,0),'normal_1':(98,1772,1),'normal_2':(99,1750,2),'normal_3':(100,1730,3),
     'IR007_0':(105,1797,0),'IR007_1':(106,1772,1),'IR014_0':(169,1797,0),'IR021_0':(209,1797,0),
     'B007_0':(118,1797,0),'B007_1':(119,1772,1),'B014_0':(185,1797,0),'B021_0':(222,1797,0),
     'OR007@6_0':(130,1797,0),'OR007@6_1':(131,1772,1),'OR007@3_0':(144,1797,0),
     'OR007@12_0':(156,1797,0),'OR014@6_0':(197,1797,0),'OR021@6_0':(234,1797,0)}
pass
meta={}
for lab,(f,rpm,hp) in IDX.items():
    p=datos(f'{f}.mat')
    if not os.path.exists(p):
        print(f'  descargando {lab} -> {f}.mat')
        r=urllib.request.Request(f'{BASE}/{f}.mat',headers={'User-Agent':UA})
        open(p,'wb').write(urllib.request.urlopen(r,timeout=120).read())
    meta[lab]=dict(f=f,rpm=rpm,hp=hp)
json.dump(meta,open(datos('indice.json'),'w'),indent=1)
print(f'listo: {len(meta)} registros en', DATOS)
