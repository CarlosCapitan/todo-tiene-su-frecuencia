import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras

import numpy as np, datetime
d=np.load(datos('feat.npz'),allow_pickle=True)
X,y,ts,names=d['X'],d['y'],d['ts'],list(d['names'])
n=len(y)
HOR=['mom3','mom6','mom12','mom36','mom144','mom288']; QS=[.50,.60,.75,.85,.90]
TRAIN=20000; STEP=2500
print("="*78)
print("WALK-FORWARD DE LA REGLA — horizonte y umbral reelegidos en cada paso")
print("con SOLO las 20.000 ventanas anteriores; criterio de selección = máximo z")
print("="*78)
rows=[]; picks=[]
for s in range(TRAIN,n,STEP):
    tr=slice(s-TRAIN,s); best=None
    for h in HOR:
        j=names.index(h); mm=X[:,j]; p=(mm<0).astype(int)
        for q in QS:
            t=np.quantile(np.abs(mm[tr]),q); sel=np.abs(mm[tr])>t
            k=int(sel.sum())
            if k<600: continue
            a=float((p[tr][sel]==y[tr][sel]).mean()); z=(a-.5)/np.sqrt(.25/k)
            if best is None or z>best[0]: best=(z,h,q,t,a)
    z0,h,q,t,a0=best
    e=min(s+STEP,n); j=names.index(h); mm=X[:,j]; p=(mm<0).astype(int)
    sel=np.abs(mm[s:e])>t; k=int(sel.sum())
    if k<10: continue
    a=float((p[s:e][sel]==y[s:e][sel]).mean())
    rows.append((s,e,k,a)); picks.append((h,q))
    d0=datetime.datetime.utcfromtimestamp(int(ts[s])).strftime('%Y-%m-%d')
    print(f"  {d0}  elige {h:7s} p{int(q*100):<3d} (entren. {a0:.4f})  ->  fuera de muestra n={k:5d} acierto={a:.4f}")
K=sum(r[2] for r in rows); A=sum(r[2]*r[3] for r in rows)/K
z=(A-.5)/np.sqrt(.25/K)
lo,hi=A-1.96*np.sqrt(A*(1-A)/K), A+1.96*np.sqrt(A*(1-A)/K)
print("\n"+"="*78)
print(f"  AGREGADO FUERA DE MUESTRA:  n={K}  acierto={A:.4f}  ventaja={A-.5:+.4f}  z={z:+.2f}")
print(f"  IC 95 %: acierto [{lo:.4f}, {hi:.4f}]  ->  ventaja entre {(lo-.5)*100:+.2f} y {(hi-.5)*100:+.2f} pp")
from collections import Counter
print(f"  horizontes elegidos: {Counter(h for h,_ in picks).most_common()}")
print(f"  umbrales elegidos:   {Counter('p'+str(int(q*100)) for _,q in picks).most_common()}")

# nula: mismo procedimiento walk-forward sobre y desplazada
rng=np.random.default_rng(9); nulls=[]
for r in range(300):
    sh=int(rng.integers(2000,n-2000)); ysh=np.roll(y,sh)
    KK=0; AA=0.
    for s in range(TRAIN,n,STEP):
        tr=slice(s-TRAIN,s); b=None
        for h in HOR:
            j=names.index(h); mm=X[:,j]; p=(mm<0).astype(int)
            for q in QS:
                t=np.quantile(np.abs(mm[tr]),q); sel=np.abs(mm[tr])>t; k=int(sel.sum())
                if k<600: continue
                a=float((p[tr][sel]==ysh[tr][sel]).mean()); zz=(a-.5)/np.sqrt(.25/k)
                if b is None or zz>b[0]: b=(zz,h,t)
        _,h,t=b; e=min(s+STEP,n); j=names.index(h); mm=X[:,j]; p=(mm<0).astype(int)
        sel=np.abs(mm[s:e])>t; k=int(sel.sum())
        if k<10: continue
        KK+=k; AA+=k*float((p[s:e][sel]==ysh[s:e][sel]).mean())
    nulls.append(AA/KK)
nulls=np.array(nulls)
kk=int((nulls>=A).sum())
print(f"\n  Nula walk-forward (300 réplicas, todo el procedimiento incluido):")
print(f"    media={nulls.mean():.4f}  sd={nulls.std(ddof=1):.4f}  p95={np.quantile(nulls,.95):.4f}  max={nulls.max():.4f}")
print(f"    réplicas ≥ real: {kk}/300  ->  p empírico = {(kk+1)/301:.4f}")
np.savez(datos('wf_rule.npz'),rows=np.array(rows),A=A,K=K,nulls=nulls)
