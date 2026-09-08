#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
escalado_grupo.py — cuanto cuesta de verdad buscar en un grupo

Mide el exponente empirico de dos algoritmos clasicos de logaritmo discreto
sobre curvas elipticas de ORDEN PRIMO construidas al vuelo, de 16 a 44 bits:

  - Pollard rho   (estocastico, memoria O(1),      teoria: 0,886*sqrt(n) pasos)
  - BSGS          (determinista, memoria O(sqrt n), teoria: 2*sqrt(n) pasos)

La pregunta del libro no es "¿funciona?" sino "¿como crece?". La pendiente de
log2(coste) frente a bits es la unica respuesta que decide si un metodo es un
ataque o una anecdota.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras

import math, random, time, sys

# ---------------- aritmetica de curva y^2 = x^3 + b ----------------
def add(P,Q,p):
    if P is None: return Q
    if Q is None: return P
    x1,y1=P; x2,y2=Q
    if x1==x2 and (y1+y2)%p==0: return None
    l=((3*x1*x1)*pow(2*y1,-1,p) if P==Q else (y2-y1)*pow(x2-x1,-1,p))%p
    x3=(l*l-x1-x2)%p; return (x3,(l*(x1-x3)-y1)%p)

def mul(k,P,p):
    R=None;Q=P
    while k>0:
        if k&1: R=add(R,Q,p)
        Q=add(Q,Q,p); k>>=1
    return R

def es_primo(n):
    if n<2: return False
    for q in (2,3,5,7,11,13,17,19,23,29,31,37):
        if n%q==0: return n==q
    d=n-1;s=0
    while d%2==0: d//=2;s+=1
    for a in (2,3,5,7,11,13,17,19,23,29,31,37):
        x=pow(a,d,n)
        if x in (1,n-1): continue
        for _ in range(s-1):
            x=x*x%n
            if x==n-1: break
        else: return False
    return True

def primo_desde(x):
    if x%2==0: x+=1
    while not es_primo(x): x+=2
    return x

def punto_en(p,b):
    for x in range(1,10000):
        r=(x*x*x+b)%p
        if r and pow(r,(p-1)//2,p)==1:
            y=pow(r,(p+1)//4,p)
            if (y*y-r)%p==0: return (x,y)
    return None

def orden_de(G,p):
    s=math.isqrt(p); lo=max(1,p+1-2*s); hi=p+1+2*s
    m=math.isqrt(hi-lo)+1
    tab={}; X=None
    for j in range(m+1):
        tab.setdefault("I" if X is None else X, j); X=add(X,G,p)
    mG=mul(m,G,p); cur=mul(lo,G,p)
    for i in range(m+3):
        k="I" if cur is None else (cur[0],(-cur[1])%p)
        if k in tab:
            c=lo+i*m+tab[k]
            if c>0 and mul(c,G,p) is None: return c
        cur=add(cur,mG,p)
    return None

def curva_orden_primo(bits, semilla=0):
    """Busca p ~ 2^bits con p=3 mod 4 y #<G> primo."""
    p = primo_desde((1<<bits) - (1<<max(1,bits-6)) + semilla)
    while True:
        if p%4==3 and p.bit_length()==bits:
            G=punto_en(p,7)
            if G:
                n=orden_de(G,p)
                if n and es_primo(n) and n.bit_length()>=bits-1:
                    return p,G,n
        p=primo_desde(p+2)
        if p.bit_length()>bits: raise RuntimeError(f"sin curva a {bits} bits")

# ---------------- Pollard rho ----------------
def pollard_rho(G,Q,p,n,rng):
    def paso(X,a,b):
        if X is None: return add(G,X,p),(a+1)%n,b
        s=X[0]%3
        if s==0: return add(X,G,p),(a+1)%n,b
        if s==1: return add(X,X,p),(2*a)%n,(2*b)%n
        return add(X,Q,p),a,(b+1)%n
    for _ in range(20):                      # reintentos si sale degenerado
        a=rng.randrange(1,n); b=rng.randrange(1,n)
        X=add(mul(a,G,p),mul(b,Q,p),p); a1,b1=a,b
        Y,a2,b2=X,a,b
        pasos=0
        while pasos < 60*int(math.isqrt(n))+1000:
            X,a1,b1=paso(X,a1,b1); pasos+=1
            Y,a2,b2=paso(*paso(Y,a2,b2)); pasos+=2
            if X==Y:
                db=(b1-b2)%n
                if db==0: break
                return (a2-a1)*pow(db,-1,n)%n, pasos
    return None,pasos

# ---------------- BSGS ----------------
def bsgs(G,Q,p,n):
    m=math.isqrt(n)+1; tab={}; X=None; ops=0
    for j in range(m):
        tab.setdefault("I" if X is None else X, j); X=add(X,G,p); ops+=1
    mG=mul(m,G,p); neg=None if mG is None else (mG[0],(-mG[1])%p)
    cur=Q
    for i in range(m+1):
        k="I" if cur is None else cur
        if k in tab: return (i*m+tab[k])%n, ops+i
        cur=add(cur,neg,p); ops+=1
    return None, ops

# ---------------- barrido ----------------
if __name__=="__main__":
    BITS=[int(x) for x in (sys.argv[1] if len(sys.argv)>1 else "16,20,24,28,32,36,40,44").split(",")]
    REPS_RHO={16:9,20:9,24:7,28:5,32:5,36:3,40:3,44:2,48:1}
    MAX_BSGS=40
    rng=random.Random(11)
    print(f"{'bits':>5} {'n (orden primo)':>18} {'rho pasos':>12} {'rho s':>8} {'BSGS ops':>12} {'BSGS s':>8}")
    filas=[]
    for b in BITS:
        p,G,n=curva_orden_primo(b)
        R=REPS_RHO.get(b,2); ps=[]; ts=[]
        for _ in range(R):
            d=rng.randrange(1,n); Q=mul(d,G,p)
            t0=time.perf_counter(); dr,pasos=pollard_rho(G,Q,p,n,rng); dt=time.perf_counter()-t0
            assert dr==d, f"rho fallo a {b} bits"
            ps.append(pasos); ts.append(dt)
        rho_pasos=sum(ps)/len(ps); rho_t=sum(ts)/len(ts)
        if b<=MAX_BSGS:
            d=rng.randrange(1,n); Q=mul(d,G,p)
            t0=time.perf_counter(); db,ops=bsgs(G,Q,p,n); bt=time.perf_counter()-t0
            assert db==d, f"bsgs fallo a {b} bits"
        else:
            ops=float('nan'); bt=float('nan')
        print(f"{b:5d} {n:18,} {rho_pasos:12,.0f} {rho_t:8.2f} {ops:12,.0f} {bt:8.2f}", flush=True)
        filas.append((b,n,rho_pasos,rho_t,ops,bt))

    import numpy as np
    A=np.array([[f[0],1] for f in filas])
    for col,nom,teor in ((2,"rho (pasos)",0.5),(4,"BSGS (ops)",0.5)):
        y=np.array([f[col] for f in filas],dtype=float)
        ok=~np.isnan(y)
        s,c=np.linalg.lstsq(A[ok],np.log2(y[ok]),rcond=None)[0]
        print(f"\najuste {nom:14}: log2(coste) = {s:.4f}*bits + {c:+.2f}   -> coste ~ N^{s:.4f}   (teoria {teor})")
    y=np.array([f[3] for f in filas],dtype=float)
    s,c=np.linalg.lstsq(A,np.log2(y),rcond=None)[0]
    print(f"ajuste {'rho (segundos)':14}: log2(t)      = {s:.4f}*bits + {c:+.2f}   -> t ~ N^{s:.4f}")
    np.save(datos('escalado_grupo.npy'), np.array(filas,dtype=float))
