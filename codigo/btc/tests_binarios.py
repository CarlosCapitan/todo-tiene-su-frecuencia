"""Los 11 tests binarios preinscritos, sobre el signo, en las dos escalas.

Umbral honesto de la rejilla completa (N=82): 2,97 sigma.
Walsh usa ademas su propio umbral interno por numero de mascaras.
"""
import pickle, numpy as np, lib as L, json

UMBRAL = np.sqrt(2*np.log(82))          # 2,97
series = pickle.load(open("datos/series.pkl","rb"))
filas = []

def anota(escala, test, stat, z, nota=""):
    filas.append(dict(escala=escala, test=test, stat=stat, z=z, nota=nota))
    marca = "  <-- SUPERA" if (z is not None and abs(z) > UMBRAL) else ""
    zt = f"{z:+.3f}" if z is not None else "   --"
    print(f"  {test:<26} {stat:<34} z={zt}{marca}")

for escala in ("1h","1d"):
    b = series[escala]["signo"].astype(np.int8)
    n = len(b)
    print(f"\n{'='*78}\nSIGNO DE BTC-USD  ·  escala {escala}  ·  {n:,} bits"
          f"\numbral honesto (N=82): {UMBRAL:.2f} sigma\n{'='*78}")

    mb = L.monobit(b)
    anota(escala,"1 monobit", f"p(sube)={b.mean():.5f}", mb['z'])

    rt = L.runs_test(b)
    anota(escala,"2 rachas", f"p={rt['p']:.4f}", rt.get('z'))

    lr = L.longest_run_ones(b)
    anota(escala,"3 racha maxima", str(lr), None)

    dt = L.nist_dft(b)
    anota(escala,"4 DFT del NIST", f"p={dt['p']:.4f}", dt.get('z'))

    r = np.asarray(L.autocorr(b, min(2000, n//10)), float)[1:]
    za = r*np.sqrt(n)
    k = int(np.argmax(np.abs(za)))
    ua = np.sqrt(2*np.log(len(za)))          # max de L desfases: umbral propio
    supera = abs(za[k]) > ua
    filas.append(dict(escala=escala, test="5 autocorrelacion",
                      stat=f"max|z| en desfase {k+1} de {len(za)}",
                      z=float(za[k]), nota=f"umbral interno {ua:.2f}"))
    print(f"  {'5 autocorrelacion':<26} {f'max|z| en desfase {k+1} de {len(za)}, umbral {ua:.2f}':<34} "
          f"z={za[k]:+.3f}{'  <-- SUPERA' if supera else '  (no supera su umbral)'}")

    mu = L.maurer_universal(b)
    if mu is None:
        anota(escala,"6 Maurer", "NO APLICA: serie demasiado corta (necesita >8.960 bits)", None)
    else:
        anota(escala,"6 Maurer", f"fn={mu['fn']:.5f}", mu['z'])

    ae = L.approx_entropy(b)
    anota(escala,"7 ApEn(m=10)", f"{ae:.6f}  (ln2={np.log(2):.6f})", None)

    Lc,_ = L.berlekamp_massey(b)
    anota(escala,"8 Berlekamp-Massey", f"L={Lc} de n/2={n//2}  ratio={Lc/(n/2):.4f}", None)

    nl = L.nist_linear_complexity(b)
    anota(escala,"9 complejidad lineal NIST", f"chi2={nl['chi2']:.2f}  p={nl['p']:.4f}", None)

    print("  10-11 Walsh-Hadamard (criptoanalisis lineal):")
    for kk in (8,12,16):
        z = L.walsh_linear(b, k=kk)
        N = 2**kk - 1
        uw = np.sqrt(2*np.log(N))
        sobre = int((np.abs(z) > uw).sum())
        print(f"       k={kk:2d}  {N:>7,} mascaras  max|z|={np.abs(z).max():.2f}"
              f"  umbral {uw:.2f}  por encima: {sobre}")
        filas.append(dict(escala=escala, test=f"walsh k={kk}",
                          stat=f"{N} mascaras, {sobre} sobre umbral",
                          z=float(np.abs(z).max()), nota=f"umbral interno {uw:.2f}"))

json.dump(filas, open("datos/resultados_binarios.json","w"), indent=1)
print(f"\n{'='*78}")
sup = [f for f in filas if f['z'] is not None and abs(f['z'])>UMBRAL and 'walsh' not in f['test']]
print(f"Tests que superan {UMBRAL:.2f} sigma: {len(sup)}")
for f in sup: print(f"   {f['escala']}  {f['test']}  z={f['z']:+.3f}  ({f['stat']})")
