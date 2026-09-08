import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
d=np.load(datos('feat.npz'),allow_pickle=True)
X,y,ts,names=d['X'],d['y'],d['ts'],list(d['names'])
n=len(y)
# variables de la reversion multiescala conocida
MOM=[i for i,nm in enumerate(names) if nm.startswith('mom') or nm.startswith('ret_lag')
     or nm.startswith('pos') or nm.startswith('bit_lag') or nm.startswith('imb')]
Xm=X[:,MOM]
print(f"blanqueando con {len(MOM)} variables de reversion/momento sobre {n} muestras")
# walk-forward: p_hat de cada bloque se estima SOLO con datos anteriores
TR=15000; STEP=2500
p=np.full(n,np.nan)
for s in range(TR,n,STEP):
    sc=StandardScaler().fit(Xm[s-TR:s])
    m=LogisticRegression(max_iter=3000,C=.08).fit(sc.transform(Xm[s-TR:s]),y[s-TR:s])
    e=min(s+STEP,n); p[s:e]=m.predict_proba(sc.transform(Xm[s:e]))[:,1]
ok=np.isfinite(p)
p=np.clip(p,.02,.98)
r=np.where(ok,(y-p)/np.sqrt(p*(1-p)),np.nan)     # residuo de Pearson
x=2*y.astype(float)-1
print(f"residuo definido en {ok.sum()} muestras  media={np.nanmean(r[ok]):+.4f}  sd={np.nanstd(r[ok]):.4f}")
# comprobacion: el residuo NO debe conservar la reversion
from numpy import corrcoef
j=names.index('mom6')
c_raw=np.corrcoef(X[ok,j],x[ok])[0,1]
c_res=np.corrcoef(X[ok,j],r[ok])[0,1]
print(f"corr(mom6, signo crudo) = {c_raw:+.4f}   corr(mom6, residuo) = {c_res:+.4f}   <- debe caer a ~0")
# 'mag' es el control positivo del capitulo 8: log|retorno| en la misma ventana
mag=np.log(np.abs(d['ret'])+1e-12)
np.savez(datos('series.npz'), x=x[ok], r=r[ok], ts=ts[ok], p=p[ok], y=y[ok], mag=mag[ok])
print("series guardadas:", int(ok.sum()))
