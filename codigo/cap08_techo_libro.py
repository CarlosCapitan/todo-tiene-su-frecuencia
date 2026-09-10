#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cap08_techo_libro.py — acotar la afirmacion del apartado 8.6.

EL 8.6 DICE que el 99,73 % restante "no es ignorancia nuestra, es causalidad":
lo determina flujo de ordenes que aun no ha ocurrido en el instante de decidir.

LA OBJECION es que el propio apartado 7.7 dice que falta el precio del libro de
ordenes en el instante del disparo. Si falta informacion que SI existe al
decidir, parte de ese 99,73 % es ignorancia, no causalidad.

QUE SE PUEDE MEDIR AQUI. No tengo el libro de ordenes: las velas de Coinbase no
lo traen. Lo que si existe en el instante de decidir y NO estaba entre las 71
variables del capitulo 7 son tres aproximaciones clasicas a la presion
compradora dentro de la ultima vela cerrada:

  · CLV, close location value = (cierre - minimo)/(maximo - minimo)
  · volumen firmado = volumen x (2*CLV - 1)
  · cuerpo sobre rango = (cierre - apertura)/(maximo - minimo)

Sin fuga temporal: la apuesta se coloca cuando la ventana se ABRE, en t-300, asi
que solo puede usarse la vela que termina en t-300.
"""
import pickle, numpy as np

d = pickle.load(open('../datos/data.pkl','rb'))
ts, bits, cd = d['ts'], d['bits'].astype(int), d['cd']
V = {int(k): [float(z) for z in v] for k, v in cd.items()}   # [t, low, high, open, close, vol]

X, y, bits_ok = [], [], []
for i, t in enumerate(ts):
    t = int(t)
    # Convencion: las claves de cd son el INICIO de vela (API de Coinbase,
    # granularity=300). La vela con clave t-300 cubre [t-300, t) y cierra
    # exactamente en t, el instante en que se abre la ventana que se apuesta.
    assert (t - 300) + 300 <= t   # la vela usada cierra <= instante de decision
    v = V.get(t-300)                      # ultima vela CERRADA al abrirse la ventana
    a, b = V.get(t-300), V.get(t)
    if v is None or a is None or b is None: continue
    _, lo, hi, op, cl, vo = v
    if hi <= lo or b[4] == a[4]: continue
    clv  = (cl-lo)/(hi-lo)
    X.append([2*clv-1, vo*(2*clv-1), (cl-op)/(hi-lo)])
    y.append(1 if b[4] > a[4] else 0)
    bits_ok.append(int(bits[i]))
X, y, bits_ok = np.array(X), np.array(y), np.array(bits_ok)
n = len(y)
print(f"ventanas utilizables sin fuga temporal: {n:,}")
print(f"p(sube) global: {y.mean():.5f}\n")

NOM = ["CLV (presion compradora)", "volumen firmado", "cuerpo sobre rango"]
def z_prop(p, m): return (p-0.5)*np.sqrt(m)/0.5

print("="*78)
print("A. ¿PREDICE ALGO, UNIVARIANTE, DENTRO DE MUESTRA?")
print("="*78)
print(f"{'variable':<28}{'corr con el signo':>19}{'z':>8}{'acierto':>10}{'z':>8}")
h = n//2
for j, nom in enumerate(NOM):
    x = X[:, j]
    xs = (x - x.mean())/(x.std()+1e-12); ys = (y-0.5)*2
    c = float(np.mean(xs*ys))
    pred = (x > np.median(x)).astype(int)
    ac = float((pred == y).mean())
    print(f"{nom:<28}{c:>19.5f}{c*np.sqrt(n):>8.2f}{ac:>10.4f}{z_prop(ac,n):>8.2f}")

print("\n" + "="*78)
print("B. LA PRUEBA QUE IMPORTA: ajustar en la primera mitad, medir en la segunda")
print("="*78)
print(f"{'variable':<28}{'acierto 1a mitad':>18}{'acierto 2a mitad':>18}{'z fuera':>9}")
pout_por_var = {}
for j, nom in enumerate(NOM):
    x = X[:, j]
    umb = np.median(x[:h])
    sentido = 1 if ((x[:h] > umb).astype(int) == y[:h]).mean() >= 0.5 else -1
    pin  = (((x[:h] > umb).astype(int) if sentido==1 else (x[:h] <= umb).astype(int)) == y[:h]).mean()
    pout = (((x[h:] > umb).astype(int) if sentido==1 else (x[h:] <= umb).astype(int)) == y[h:]).mean()
    pout_por_var[nom] = pout
    print(f"{nom:<28}{pin:>18.4f}{pout:>18.4f}{z_prop(pout, n-h):>9.2f}")

print("\n" + "="*78)
print("C. LAS TRES JUNTAS: regresion logistica, ajuste en la 1a mitad")
print("="*78)
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
sc = StandardScaler().fit(X[:h])
m = LogisticRegression(max_iter=2000).fit(sc.transform(X[:h]), y[:h])
pin  = m.score(sc.transform(X[:h]), y[:h])
pout = m.score(sc.transform(X[h:]), y[h:])
print(f"  acierto en muestra   : {pin:.4f}")
print(f"  acierto FUERA        : {pout:.4f}   z = {z_prop(pout, n-h):+.2f}")
print(f"  coeficientes: " + ", ".join(f"{a}={b:+.4f}" for a,b in zip(NOM, m.coef_[0])))

r2 = (2*(pout-0.5))**2
print(f"\n  R2 implicito fuera de muestra: {100*r2:.4f} %")
print(f"  (el techo que declara el 8.6 va del 0,0139 % al 0,2663 %)")

# ---------------------------------------------------------------------------
print("\n" + "="*78)
print("D. LA PREGUNTA QUE DECIDE: ¿aporta algo MAS ALLA del bit anterior?")
print("="*78)
print("  El capitulo 7 ya usaba bit_lag1 entre sus 71 variables. Si el CLV solo")
print("  es una version mas fina de lo mismo, no hay informacion nueva: hay la")
print("  misma informacion mejor medida.\n")

# reconstruir con el bit anterior alineado
Xb, yb = [], []
prev = None
for i, t in enumerate(ts):
    t = int(t); a, b, v = V.get(t-300), V.get(t), V.get(t-300)
    if v is None or a is None or b is None or b[4] == a[4]:
        prev = None; continue
    _, lo, hi, op, cl, vo = v
    if hi <= lo: prev = None; continue
    yi = 1 if b[4] > a[4] else 0
    if prev is not None:
        Xb.append([2*(cl-lo)/(hi-lo)-1, vo*(2*(cl-lo)/(hi-lo)-1), (cl-op)/(hi-lo), 2*prev-1])
        yb.append(yi)
    prev = yi
Xb, yb = np.array(Xb), np.array(yb)
nb = len(yb); hb = nb//2
print(f"  ventanas con bit anterior disponible: {nb:,}")

def fuera(cols):
    sc = StandardScaler().fit(Xb[:hb, cols])
    m = LogisticRegression(max_iter=2000).fit(sc.transform(Xb[:hb, cols]), yb[:hb])
    return m.score(sc.transform(Xb[hb:, cols]), yb[hb:])

modelos = [("solo el bit anterior",              [3]),
           ("solo el CLV",                       [0]),
           ("bit anterior + CLV",                [3, 0]),
           ("bit anterior + las tres nuevas",    [3, 0, 1, 2])]
print(f"\n  {'modelo':<34}{'acierto fuera de muestra':>26}{'z':>8}")
base = None
for nom, cols in modelos:
    a = fuera(cols)
    if nom == "solo el bit anterior": base = a
    print(f"  {nom:<34}{a:>26.4f}{z_prop(a, nb-hb):>8.2f}")
print(f"\n  mejora del CLV sobre el bit anterior: "
      f"{100*(fuera([3,0])-base):+.3f} puntos porcentuales")

print("\n" + "="*78)
print("E. R2 DE CADA MODELO POR SEPARADO (no cruzar cifras de C con las de D)")
print("="*78)
for nom, cols in modelos:
    a = fuera(cols)
    r2m = (2*(a-0.5))**2
    print(f"  {nom:<34}acierto {a:.4f}   R2 = {100*r2m:.4f} %")

print("\n" + "="*78)
print("F. TECHO INCONDICIONAL DE LA REGLA DEL CAPITULO 7 (el 0,27% del 8.5 es")
print("   condicional a sus disparos, no a la varianza total del mercado)")
print("="*78)
wf = np.load('../datos/polymarket_walkforward.npz')
K_regla, A_regla = int(wf['K']), float(wf['A'])
N_TOTAL = 51626   # las mismas ventanas de la serie walk-forward, apartado 8.2 (resid.py)
frac = K_regla / N_TOTAL
acierto_incond = 0.5 + frac*(A_regla-0.5)
rho_incond = 2*(acierto_incond-0.5)
r2_incond = rho_incond**2
print(f"  disparos: {K_regla:,} de {N_TOTAL:,} ventanas ({frac:.1%})")
print(f"  acierto condicional (sobre los disparos): {A_regla:.4f}")
print(f"  acierto global equivalente (resto de ventanas a 0,5): {acierto_incond:.4f}")
print(f"  rho incondicional: {rho_incond:.4f}   R2 incondicional: {100*r2_incond:.4f} %")

print("\n" + "="*78)
print("G. ATENUACION DEL R2 DEL CLV, DEL SIGNO DE LA VELA AL BIT DEL MERCADO")
print("="*78)
coincidencia = float((bits_ok == y).mean())
r2_clv = (2*(pout_por_var["CLV (presion compradora)"]-0.5))**2
print(f"  coincidencia bit de Polymarket == signo de la vela: {coincidencia:.4f}")
print(f"  R2 del CLV sobre el signo de la vela: {100*r2_clv:.4f} %")
# Atenuacion del R2 medido sobre el signo de la vela al bit del mercado.
# Con desacuerdo eps independiente, rho se atenua por (1-2*eps).
eps = 1 - coincidencia          # coincidencia = fraccion vela == bit
print("R2 CLV sobre el bit (atenuado):", r2_clv * (1 - 2*eps)**2)
