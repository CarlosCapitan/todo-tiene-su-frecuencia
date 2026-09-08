"""Tabla 1.1 — la bateria completa aplicada al LFSR y al control aleatorio."""
import numpy as np, bateria as B
N=70000; rng=np.random.default_rng(7)
S={'LFSR de 32 bits':B.lfsr(N),'Aleatorio verdadero':rng.integers(0,2,N).astype(np.int8)}
print("="*84); print("TABLA 1.1 — la misma bateria sobre las dos secuencias"); print("="*84)
print(f"{'prueba':<34}{'LFSR':>22}{'aleatorio':>22}"); print("-"*84)
r={}
for nm,b in S.items():
    mb=B.monobit(b); ra=B.rachas(b); df=B.dft_nist(b)
    ac=B.autocorr(b,4000); se=1/np.sqrt(N)
    z=B.walsh_lineal(b,16)[1:]
    L,_=B.berlekamp_massey(b)
    r[nm]=dict(mb=mb,ra=ra,df=df,acmax=float(np.abs(ac[1:]).max()/se),
               wmax=float(np.abs(z).max()),L=L)
f=lambda k,fmt: [fmt.format(r[nm][k]) for nm in S]
rows=[("Monobit  (p-valor)",[f"{r[n]['mb']['p']:.4f}" for n in S]),
      ("Rachas  (p-valor)",[f"{r[n]['ra']['p']:.4f}" for n in S]),
      ("DFT espectral NIST  (p-valor)",[f"{r[n]['df']['p']:.4f}" for n in S]),
      ("Autocorrelación  máx |z| en 4.000 lags",[f"{r[n]['acmax']:.2f}" for n in S]),
      ("Walsh-Hadamard  máx |z| en 65.535",[f"{r[n]['wmax']:.2f}" for n in S]),
      ("── Berlekamp-Massey  L(70.000)",[f"{r[n]['L']}" for n in S])]
for lab,vals in rows: print(f"{lab:<34}{vals[0]:>22}{vals[1]:>22}")
print(f"\numbral de ruido multi-test:  autocorrelación {B.umbral_multitest(4000):.2f}   Walsh {B.umbral_multitest(2**16):.2f}")
print(f"valor esperado de L si fuera aleatorio: n/2 = {N//2}")
print(f"\nBits necesarios para romper el LFSR: 2 x 32 = 64")
Lp=B.perfil_complejidad(S['LFSR de 32 bits'],[32,64,65,100,1000])
print("perfil de complejidad del LFSR:", {n:l for n,l in Lp})
