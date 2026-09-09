"""Control con verdad conocida.

Si lo que se ha encendido es agrupamiento de volatilidad —los movimientos
grandes van juntos— entonces destruir TODA la direccion y conservar solo las
magnitudes debe dejar los mismos numeros. Y al reves: conservar la direccion
y barajar las magnitudes debe apagarlos.

  r          = serie real
  r_signos   = |r| en su orden real, con el signo sorteado  -> sin direccion
  r_magbaraj = signo real, magnitudes barajadas             -> sin agrupamiento
"""
import pickle, numpy as np, spec as S
from tests_continuos import estadisticos, ESCALAS

s = pickle.load(open("datos/series.pkl","rb"))
import sys
esc = sys.argv[1] if len(sys.argv)>1 else "1h"; cfg = ESCALAS[esc]
r = np.asarray(s[esc]["retorno"], float)
rng = np.random.default_rng(20260909)

variantes = {
    "real                    ": r,
    "signos sorteados        ": np.abs(r) * rng.choice([-1.0,1.0], len(r)),
    "magnitudes barajadas    ": np.sign(r) * rng.permutation(np.abs(r)),
}
cols = (["ciclo_24"] if esc=="1h" else ["ciclo_7"]) + ["bicoh_512","tiempo_frec","envolvente","D2_m7","kurt_espectral"]
print(f"\n### escala {esc} ###")
print(f"{'variante':<26}" + "".join(f"{c:>16}" for c in cols))
print("-"*(26+16*len(cols)))
for nom, x in variantes.items():
    st = estadisticos(x, cfg, np.random.default_rng(7))
    print(f"{nom:<26}" + "".join(f"{st[c]:>16.2f}" for c in cols))

print("\nAutocorrelacion a 1 paso de |r| (definicion de agrupamiento):")
for nom, x in variantes.items():
    a = np.abs(x); a = a - a.mean()
    print(f"  {nom} r(1)|r| = {np.dot(a[:-1],a[1:])/np.dot(a,a):+.4f}")
