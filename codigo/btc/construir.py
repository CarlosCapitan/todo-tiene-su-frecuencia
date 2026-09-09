"""Construye las tres series preinscritas a partir de las velas de Coinbase.

  signo(t)    = 1 si log(p_t/p_{t-1}) > 0, si no 0      (binaria)
  retorno(t)  = log(p_t/p_{t-1})                        (continua)
  magnitud(t) = log(|retorno(t)| + eps)                 (continua)

El precio en bruto NO se analiza: la preinscripcion lo excluye por no
estacionario. Aqui se mide su autocorrelacion solo para dejar constancia
numerica de por que se excluye.
"""
import json, pickle, numpy as np

EPS = 1e-12

def series(nombre):
    v = json.load(open(f"datos/{nombre}"))
    ts = np.array([x[0] for x in v], dtype=np.int64)
    p  = np.array([x[4] for x in v], dtype=float)      # cierre
    r  = np.diff(np.log(p))                            # log-retorno
    s  = (r > 0).astype(np.int8)                       # signo
    m  = np.log(np.abs(r) + EPS)                       # magnitud
    return dict(ts=ts[1:], precio=p[1:], retorno=r, signo=s, magnitud=m)

def ac1(x):
    x = np.asarray(x, float); x = x - x.mean()
    return float(np.dot(x[:-1], x[1:]) / np.dot(x, x))

if __name__ == "__main__":
    todo = {}
    for etiqueta, fichero in (("1h", "btc_1h.json"), ("1d", "btc_1d.json")):
        d = series(fichero)
        todo[etiqueta] = d
        r, s, m, p = d["retorno"], d["signo"], d["magnitud"], d["precio"]
        n = len(r)
        print(f"\n=== escala {etiqueta} — {n} observaciones ===")
        print(f"  signo     p(sube) = {s.mean():.5f}   "
              f"(z frente a 0,5 = {(s.mean()-0.5)*np.sqrt(n)/0.5:+.2f})")
        print(f"  retorno   media {r.mean():+.3e}  sigma {r.std():.5f}  "
              f"asimetria {float(((r-r.mean())**3).mean()/r.std()**3):+.3f}  "
              f"curtosis {float(((r-r.mean())**4).mean()/r.std()**4):.2f}")
        print(f"  magnitud  media {m.mean():+.3f}  sigma {m.std():.3f}")
        print(f"  autocorrelacion a 1 paso:")
        print(f"     precio   {ac1(p):+.5f}   <- por esto se excluye")
        print(f"     retorno  {ac1(r):+.5f}")
        print(f"     signo    {ac1(2*s-1.0):+.5f}")
        print(f"     magnitud {ac1(m):+.5f}")
    pickle.dump(todo, open("datos/series.pkl", "wb"))
    print("\ndatos/series.pkl escrito")
