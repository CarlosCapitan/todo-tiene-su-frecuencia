"""Capitulo 3 — tres demostraciones sobre por que la nula decide la conclusion."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras

import numpy as np, bateria as B, json
from math import sqrt, log

rng=np.random.default_rng(11)
out={}

# ---------- 3.A: el maximo de N normales crece, y no es un descubrimiento ----------
print("="*88)
print("3.A — buscar entre N hipotesis sobre RUIDO PURO: cuanto sale el 'mejor' hallazgo")
print("="*88)
print(f"{'k (bits previos)':>17}{'N mascaras':>13}{'max |z| medido':>16}{'sqrt(2 lnN)':>14}{'¿supera 3σ?':>13}")
print("-"*88)
A=[]
for k in (6,8,10,12,14,16,18):
    zs=[]
    for r in range(6):
        b=rng.integers(0,2,60000).astype(np.int8)      # RUIDO PURO
        zs.append(float(np.abs(B.walsh_lineal(b,k)[1:]).max()))
    N=2**k-1; m=float(np.mean(zs)); teo=sqrt(2*log(N))
    A.append(dict(k=k,N=N,zmax=m,teo=teo))
    print(f"{k:>17}{N:>13}{m:>16.2f}{teo:>14.2f}{'SI' if m>3 else 'no':>13}")
out['A']=A
print("""
El 'hallazgo' de 4,5 sigmas de un buscador que probo 65.535 mascaras sobre ruido puro
no es un hallazgo: es el maximo de 65.535 normales, y vale exactamente lo que predice
sqrt(2 lnN). Un umbral fijo de 3 sigmas empieza a fabricar descubrimientos a partir de
N ~ 90 hipotesis.""")

# ---------- 3.B: la nula debe conservar todo menos lo que se prueba ----------
print("\n"+"="*88)
print("3.B — TASA DE FALSOS POSITIVOS de cada nula, sobre 400 experimentos")
print("     x e y son independientes por construccion: TODO positivo es falso")
print("="*88)
from math import erfc
n=4000; phi=0.7; REP=400
def ar1(n,phi,rng):
    e=rng.normal(size=n); y=np.zeros(n)
    for i in range(1,n): y[i]=phi*y[i-1]+e[i]
    return y
def estad(a,b):
    a=a-a.mean(); b=b-b.mean()
    return float((a*b).mean()/(a.std()*b.std()+1e-12))*sqrt(len(a))
fp_ing=fp_sh=fp_ci=0; sds=[]; sdc=[]
for r in range(REP):
    rg=np.random.default_rng(1000+r)
    x=ar1(n,phi,rg); y=ar1(n,phi,rg)          # INDEPENDIENTES
    obs=estad(x,y)
    sh=np.array([estad(rg.permutation(x),y) for _ in range(150)])
    ci=np.array([estad(np.roll(x,int(rg.integers(200,n-200))),y) for _ in range(150)])
    if erfc(abs(obs)/sqrt(2))<.05: fp_ing+=1
    if (np.sum(np.abs(sh)>=abs(obs))+1)/151<.05: fp_sh+=1
    if (np.sum(np.abs(ci)>=abs(obs))+1)/151<.05: fp_ci+=1
    sds.append(sh.std()); sdc.append(ci.std())
print(f"  {'nula':<48}{'sd media':>10}{'falsos positivos':>19}")
print("  "+"-"*78)
for nm,fp,sd in (("ingenua:  z ~ N(0,1)",fp_ing,1.0),
                 ("permutacion: rompe la estructura serial",fp_sh,np.mean(sds)),
                 ("desplazamiento circular: la conserva",fp_ci,np.mean(sdc))):
    print(f"  {nm:<48}{sd:>10.2f}{fp}/{REP} = {fp/REP*100:>5.1f} %")
print(f"""
  Nominal esperado: 5,0 %.
  Las dos primeras nulas destruyen la autocorrelacion que ambas series comparten, asi
  que su dispersion es {np.mean(sdc)/np.mean(sds):.1f} veces menor de lo que debe ser, y multiplican por
  {(fp_sh/REP)/(fp_ci/REP):.1f} la tasa de falsos positivos. La tercera conserva la estructura serial y
  rompe solo la ALINEACION, que es justo lo que se esta probando.""")
out['B']=dict(fp_ing=fp_ing/REP,fp_sh=fp_sh/REP,fp_ci=fp_ci/REP,
              sd_sh=float(np.mean(sds)),sd_ci=float(np.mean(sdc)),REP=REP)

# ---------- 3.C: por que funciona el conjunto de test ----------
print("\n"+"="*88)
print("3.C — seleccionar entre M candidatos: donde se infla y donde no")
print("     M=30 predictores, todos RUIDO PURO. Cualquier senal es ilusoria.")
print("="*88)
M=30; n=3000; REP=300
z_todo=[]; z_tr=[]; z_te=[]
for r in range(REP):
    rg=np.random.default_rng(5000+r)
    y=rg.normal(size=n); X=rg.normal(size=(n,M))
    mit=n//2
    zt=np.array([estad(X[:mit,j],y[:mit]) for j in range(M)])   # en entrenamiento
    za=np.array([estad(X[:,j],y) for j in range(M)])            # en TODO
    j=int(np.argmax(np.abs(zt)))                                # se elige con train
    z_todo.append(np.abs(za).max())                             # (i) elegir y medir en todo
    z_tr.append(abs(zt[j]))                                     # (ii) elegir y medir en train
    z_te.append(abs(estad(X[mit:,j],y[mit:])))                  # (iii) medir en test intacto
print(f"  {'protocolo':<52}{'|z| medio':>11}{'p95':>8}")
print("  "+"-"*72)
for nm,v in (("(i)  elegir y medir sobre TODOS los datos",z_todo),
             ("(ii) elegir y medir sobre entrenamiento",z_tr),
             ("(iii) elegir en entrenamiento, medir en TEST intacto",z_te)):
    print(f"  {nm:<52}{np.mean(v):>11.2f}{np.quantile(v,.95):>8.2f}")
print(f"""
  Referencia: si no hubiera seleccion, |z| medio seria 0,80 (media de una media normal).
  El maximo de {M} normales vale sqrt(2 ln {M}) = {sqrt(2*log(M)):.2f}: eso es lo que miden (i) y (ii).
  Solo (iii) vuelve al nivel honesto, y por eso el protocolo de este libro separa
  siempre un conjunto de test que no interviene en ninguna decision.
  Coste de saltarselo: {np.mean(z_tr)-np.mean(z_te):+.2f} sigmas regalados.""")
out['C']=dict(todo=float(np.mean(z_todo)),tr=float(np.mean(z_tr)),te=float(np.mean(z_te)),
              M=M,teo=float(sqrt(2*log(M))))
json.dump(out,open(figuras('cap3_datos.json'),'w'),indent=1)
