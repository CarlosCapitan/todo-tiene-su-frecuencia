import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras

import pickle, numpy as np, datetime, json
d=pickle.load(open(datos('data.pkl'),'rb'))
ts=d['ts'].astype(np.int64); bits=d['bits'].astype(np.int8); vol=d['vol']; cd=d['cd']

# --- serie de precio alineada a la rejilla de mercados ---
# ventana del mercado i = [ts[i], ts[i]+300).  Vela Coinbase en ts[i]: [t,low,high,open,close,volume]
op=np.full(len(ts),np.nan); cl=np.full(len(ts),np.nan)
hi=np.full(len(ts),np.nan); lo=np.full(len(ts),np.nan); cvol=np.full(len(ts),np.nan)
for i,t in enumerate(ts):
    c=cd.get(int(t))
    if c: lo[i],hi[i],op[i],cl[i],cvol[i]=c[1],c[2],c[3],c[4],c[5]
ret=(cl-op)/op                      # retorno DENTRO de la ventana i  -> es la etiqueta, no un input
absret=np.abs(ret)

LAGB=24        # bits previos
def build():
    n=len(ts)
    # contigüidad: exigimos que las LOOK ranuras anteriores existan en rejilla
    LOOK=300
    contig=np.zeros(n,bool)
    for i in range(n):
        if i>=LOOK and ts[i]-ts[i-LOOK]==300*LOOK: contig[i]=True
    F={}; 
    x=2*bits.astype(np.float64)-1
    # 1. bits previos
    for k in range(1,LAGB+1):
        v=np.full(n,np.nan); v[k:]=x[:-k]; F[f'bit_lag{k}']=v
    # 2. retornos previos normalizados por vol reciente
    vol12=np.full(n,np.nan); vol288=np.full(n,np.nan); vol2016=np.full(n,np.nan)
    a=np.nan_to_num(absret,nan=np.nanmedian(absret))
    cs=np.concatenate([[0],np.cumsum(a**2)])
    for W,out in [(12,vol12),(288,vol288),(2016,vol2016)]:
        rms=np.sqrt((cs[W:]-cs[:-W])/W)
        out[W:]=rms[:-1] if len(rms)==n-W+1 else np.nan   # hasta i-1 inclusive
        out[W:]=np.sqrt((cs[W:n]-cs[0:n-W])/W)
    for k in range(1,9):
        v=np.full(n,np.nan); v[k:]=ret[:-k]; F[f'ret_lag{k}']=v/ (vol288+1e-9)
        w=np.full(n,np.nan); w[k:]=absret[:-k]; F[f'absret_lag{k}']=w/(vol288+1e-9)
    # 3. volatilidad realizada (todas hasta i-1)
    F['vol12']=vol12; F['vol288']=vol288; F['vol2016']=vol2016
    F['vol_ratio']=vol12/(vol288+1e-9)
    F['vol_ratio2']=vol288/(vol2016+1e-9)
    # 4. rango/posición del precio
    p=np.full(n,np.nan); p[1:]=cl[:-1]
    for W in [12,288]:
        mx=np.full(n,np.nan); mn=np.full(n,np.nan)
        s=np.nan_to_num(cl,nan=np.nanmedian(cl))
        from numpy.lib.stride_tricks import sliding_window_view
        sw=sliding_window_view(s,W)
        mx[W:]=sw.max(1)[:n-W]; mn[W:]=sw.min(1)[:n-W]
        F[f'pos{W}']=(p-mn)/(mx-mn+1e-9)
        F[f'range{W}']=(mx-mn)/(p+1e-9)
    # 5. momento acumulado
    for W in [3,6,12,36,144,288]:
        c=np.concatenate([[0],np.cumsum(np.nan_to_num(ret))])
        v=np.full(n,np.nan); v[W+1:]=(c[W+1:n]-c[1:n-W])
        F[f'mom{W}']=v/(vol288*np.sqrt(W)+1e-9)
    # 6. racha actual
    run=np.zeros(n)
    for i in range(1,n):
        run[i]=run[i-1]+x[i-1] if (i>1 and x[i-1]==x[i-2]) else x[i-1]
    F['runlen']=run
    # 7. suma de bits recientes (desequilibrio)
    for W in [6,12,48,288]:
        c=np.concatenate([[0],np.cumsum(x)])
        v=np.full(n,np.nan); v[W:]=(c[W:n]-c[0:n-W])/W
        F[f'imb{W}']=v
    # 8. calendario
    hr=np.array([datetime.datetime.utcfromtimestamp(int(t)).hour+
                 datetime.datetime.utcfromtimestamp(int(t)).minute/60 for t in ts])
    dw=np.array([datetime.datetime.utcfromtimestamp(int(t)).weekday() for t in ts],float)
    F['hour_sin']=np.sin(2*np.pi*hr/24); F['hour_cos']=np.cos(2*np.pi*hr/24)
    F['dow_sin']=np.sin(2*np.pi*dw/7);   F['dow_cos']=np.cos(2*np.pi*dw/7)
    # 9. volumen REZAGADO del mercado (el de i-1 se conoce en i)
    lv=np.log1p(np.nan_to_num(vol))
    for k in [1,2,3]:
        v=np.full(n,np.nan); v[k:]=lv[:-k]; F[f'lvol_lag{k}']=v
    c=np.concatenate([[0],np.cumsum(lv)])
    v=np.full(n,np.nan); v[288:]=(c[288:n]-c[0:n-288])/288
    F['lvol288']=v
    F['lvol_ratio']=F['lvol_lag1']-F['lvol288']
    # 10. volumen de BTC en la vela previa
    cvn=np.log1p(np.nan_to_num(cvol,nan=np.nanmedian(cvol)))
    v=np.full(n,np.nan); v[1:]=cvn[:-1]; F['btcvol_lag1']=v
    c=np.concatenate([[0],np.cumsum(cvn)])
    w=np.full(n,np.nan); w[288:]=(c[288:n]-c[0:n-288])/288
    F['btcvol_ratio']=F['btcvol_lag1']-w

    names=sorted(F.keys())
    X=np.column_stack([F[k] for k in names])
    y=bits.astype(np.int8)
    ok=contig & np.isfinite(X).all(1) & np.isfinite(y)
    return X,y,names,ok

X,y,names,ok=build()
print(f"muestras totales={len(y)}  válidas={ok.sum()}  características={X.shape[1]}")
print("bloques de fecha:", datetime.datetime.utcfromtimestamp(int(ts[ok][0])),
      "->", datetime.datetime.utcfromtimestamp(int(ts[ok][-1])))
np.savez_compressed(datos('feat.npz'),X=X[ok],y=y[ok],ts=ts[ok],ret=ret[ok],absret=absret[ok],
                    names=np.array(names))
print("p(Up) en muestras válidas:", round(float(y[ok].mean()),5))
