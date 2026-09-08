import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras

import numpy as np, time
from sklearn.ensemble import HistGradientBoostingClassifier
d=np.load(datos('feat.npz'),allow_pickle=True)
X,y,ts,names=d['X'],d['y'],d['ts'],list(d['names'])
import datetime
n=len(y)
KW=dict(max_depth=5,max_iter=400,learning_rate=.03,min_samples_leaf=100,l2_regularization=1.0)
TRAIN=20000; STEP=2500          # reentrenar cada ~8.7 días con las últimas 20.000 ventanas
print("="*76); print("WALK-FORWARD: reentrenar cada 2.500 ventanas con las 20.000 anteriores"); print("="*76)
preds=np.full(n,np.nan); t0=time.time()
starts=list(range(TRAIN,n,STEP))
for s in starts:
    m=HistGradientBoostingClassifier(random_state=0,early_stopping=False,**KW).fit(X[s-TRAIN:s],y[s-TRAIN:s])
    e=min(s+STEP,n)
    preds[s:e]=m.predict_proba(X[s:e])[:,1]
print(f"  {len(starts)} reentrenamientos en {time.time()-t0:.0f}s")
m=np.isfinite(preds)
acc=float(((preds[m]>.5).astype(int)==y[m]).mean()); N=int(m.sum())
print(f"\n  TODAS las predicciones fuera de muestra: n={N}  acierto={acc:.4f}  ventaja={acc-.5:+.4f}  z={(acc-.5)/np.sqrt(.25/N):+.2f}")
print(f"  periodo: {datetime.datetime.utcfromtimestamp(int(ts[m][0]))} -> {datetime.datetime.utcfromtimestamp(int(ts[m][-1]))}")

print("\n  Por bloque temporal (¿se está agotando la ventaja?):")
idx=np.where(m)[0]
B=6; edges=np.array_split(idx,B)
for i,e in enumerate(edges):
    a=float(((preds[e]>.5).astype(int)==y[e]).mean()); k=len(e)
    d0=datetime.datetime.utcfromtimestamp(int(ts[e][0])).strftime('%Y-%m-%d')
    d1=datetime.datetime.utcfromtimestamp(int(ts[e][-1])).strftime('%Y-%m-%d')
    print(f"    {d0} → {d1}  n={k:5d}  acierto={a:.4f}  ventaja={a-.5:+.4f}  z={(a-.5)/np.sqrt(.25/k):+5.2f}")

print("\n  Selectividad (apostar solo lo más confiado):")
conf=np.abs(preds[m]-.5); order=np.argsort(-conf); ys=y[m]; ps=(preds[m]>.5).astype(int)
for frac in [.05,.10,.20,.35,.50,.75,1.0]:
    k=int(N*frac); ii=order[:k]
    a=float((ps[ii]==ys[ii]).mean())
    print(f"    top {int(frac*100):3d}%  n={k:5d}  acierto={a:.4f}  ventaja={a-.5:+.4f}  z={(a-.5)/np.sqrt(.25/k):+5.2f}")

print("\n"+"="*76); print("REGLA SIMPLE Y TRANSPARENTE: reversión contra el movimiento de las últimas 12 h"); print("="*76)
j=names.index('mom144')
mm=X[:,j]
i1,i2=int(n*.50),int(n*.70)
thr=np.quantile(np.abs(mm[:i1]),[.5,.75,.9])
for lab,t in [("|mom144| > mediana",thr[0]),("|mom144| > p75",thr[1]),("|mom144| > p90",thr[2])]:
    sel=np.abs(mm)>t
    pred=(mm<0).astype(int)      # si subió mucho -> apostar Down
    for nmb,sl in [("entrenamiento",slice(0,i2)),("TEST",slice(i2,n))]:
        s=sel[sl]; k=int(s.sum())
        if k<200: continue
        a=float((pred[sl][s]==y[sl][s]).mean())
        if nmb=="TEST":
            print(f"   {lab:22s} {nmb:13s} n={k:5d}  acierto={a:.4f}  ventaja={a-.5:+.4f}  z={(a-.5)/np.sqrt(.25/k):+5.2f}")
        else:
            print(f"   {lab:22s} {nmb:13s} n={k:5d}  acierto={a:.4f}", end="   ")
np.savez(datos('wf.npz'),preds=preds,y=y,ts=ts,mask=m)
