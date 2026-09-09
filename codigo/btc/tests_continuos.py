"""Los 9 tests continuos preinscritos, sobre retorno y magnitud, dos escalas.
Modelo nulo: IAAFT x200, y cada surrogado recorre la rejilla entera.
Se compara el maximo observado contra la distribucion del maximo de la nula.
"""
import pickle, json, time, numpy as np, spec as S

NSUR = 200
ESCALAS = {"1h": dict(alphas=(24,168,720), escalas_tf=np.logspace(0.3,2.2,24),
                      lags=(0,1,2,3,4,6,12,24,48,96,144,288)),
           "1d": dict(alphas=(7,30,365),   escalas_tf=np.logspace(0.2,1.8,20),
                      lags=(0,1,2,3,4,6,7,14,30,60,90))}

def estadisticos(x, cfg, rng):
    """Devuelve un dict {nombre_hipotesis: valor}. La rejilla preinscrita."""
    out = {}
    y = np.asarray(x, float); y = y - y.mean()
    n = len(y)

    # 1. autocorrelacion: max|z| sobre desfases (umbral interno)
    nl = min(500, n//10)
    yy = y/ y.std()
    ac = np.array([np.dot(yy[:-k], yy[k:])/n for k in range(1, nl+1)])
    out["autocorr"] = float(np.abs(ac*np.sqrt(n)).max())

    # 2-4. cicloestacionariedad: 3 frecuencias ciclicas candidatas
    cs = S.cyclo_stat(y, lags=cfg["lags"], targets=cfg["alphas"])
    for a in cfg["alphas"]:
        out[f"ciclo_{a}"] = float(cs["targets"][a]["snr"])

    # 5-6. bicoherencia: nfft 256 y 512
    for nf in (256, 512):
        out[f"bicoh_{nf}"] = float(S.bic_stat(y, nfft=nf)["ratio"])

    # 7. plano tiempo-frecuencia
    out["tiempo_frec"] = float(S.tf_stat(y, cfg["escalas_tf"])["max"])

    # 8. kurtosis espectral: maxima curtosis por banda
    from numpy.fft import rfft
    nseg = 256
    nsg  = n//nseg
    seg  = y[:nsg*nseg].reshape(nsg, nseg)
    Xf   = np.abs(rfft(seg, axis=1))
    ku   = ((Xf-Xf.mean(0))**4).mean(0)/(Xf.var(0)**2+1e-30) - 3
    out["kurt_espectral"] = float(np.nanmax(ku))

    # 9. espectro de la envolvente: pico maximo sobre la mediana
    from scipy.signal import hilbert
    env = np.abs(hilbert(y))
    E   = np.abs(rfft(env - env.mean()))**2
    out["envolvente"] = float(E[1:].max()/np.median(E[1:]))

    # 10-12. dimension de correlacion, m = 5,6,7
    for m in (5,6,7):
        d = S.corr_dim(y, m=m, tau=1, npts=4000, rng=rng)
        out[f"D2_m{m}"] = float(d) if d==d else np.nan

    # 13. Lyapunov
    lam,_ = S.lyapunov_rosenstein(y, m=6, tau=1, npts=3000, rng=rng)
    out["lyapunov"] = float(lam) if lam==lam else np.nan
    return out

if __name__ == "__main__":
    s = pickle.load(open("datos/series.pkl","rb"))
    resultados = json.load(open("datos/resultados_continuos.json"))
    for esc in ("1d",):        # las de 1h ya estan calculadas y guardadas
        cfg = ESCALAS[esc]
        for serie in ("retorno","magnitud"):
            clave = f"{esc}/{serie}"
            x = np.asarray(s[esc][serie], float)
            rng = np.random.default_rng(20260909)
            t0 = time.time()
            obs = estadisticos(x, cfg, rng)
            print(f"\n=== {clave}  n={len(x):,} ===", flush=True)
            for k,v in obs.items(): print(f"   {k:<16} {v:>12.4f}", flush=True)

            nulas = {k: [] for k in obs}
            for i in range(NSUR):
                sur = S.iaaft(x, iters=120, rng=rng)
                st  = estadisticos(sur, cfg, rng)
                for k,v in st.items(): nulas[k].append(v)
                if (i+1) % 25 == 0:
                    print(f"   surrogado {i+1}/{NSUR}  ({time.time()-t0:.0f}s)", flush=True)
            resultados[clave] = dict(obs=obs,
                                     nula={k: list(map(float,v)) for k,v in nulas.items()},
                                     n=len(x))
            json.dump(resultados, open("datos/resultados_continuos.json","w"))
    print("\nlisto")
