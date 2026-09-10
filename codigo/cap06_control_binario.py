#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cap06_control_binario.py — el control que le faltaba al apartado 6.4.

LA OBJECION. El apartado 6.4 compara el espectro del SIGNO (serie binaria, ±1)
con el de la MAGNITUD (serie continua) y lee la diferencia como incentivos
economicos. Pero una serie binaria con p ~ 0,5 tiene espectro casi plano casi por
construccion: binarizar es una cuantizacion brutal que tira la amplitud, y los
picos de la magnitud son justamente estructura de amplitud. Puede que lo que
aplana el signo no sea el mercado, sino el hecho de ser binario.

EL CONTROL. Binarizar la magnitud EXACTAMENTE IGUAL —1 si |r| supera su mediana,
0 si no— y volver a medir. Sale una serie binaria con p = 0,5 por construccion,
la misma longitud, el mismo codigo.

  · Si el pico semanal SOBREVIVE a la binarizacion, entonces binarizar no aplana,
    y la planitud del signo es un hecho sobre el signo.
  · Si el pico DESAPARECE, la comparacion del 6.4 era entre peras y manzanas y la
    tesis de los incentivos hay que rebajarla a hipotesis.
"""
import pickle, numpy as np, datetime as dt

d = pickle.load(open('../datos/data.pkl','rb'))
ts, bits, cd, vol = d['ts'], d['bits'].astype(int), d['cd'], d['vol']

cierre = {int(k): float(v[4]) for k, v in cd.items()}
r = np.full(len(ts), np.nan)
for i, t in enumerate(ts):
    t = int(t); a, b = cierre.get(t-300), cierre.get(t)
    if a and b: r[i] = np.log(b/a)
ok = np.isfinite(r) & (r != 0)
r, tsv, bv = r[ok], ts[ok].astype(np.int64), bits[ok]
mag = np.log(np.abs(r))
print(f"ventanas utilizables: {len(r):,}")

PASO = 300.0                       # 5 minutos
def periodograma(x):
    x = np.asarray(x, float); x = x - x.mean()
    P = np.abs(np.fft.rfft(x))**2
    f = np.fft.rfftfreq(len(x), d=PASO)
    return f[1:], P[1:]

def snr(x, periodo_s):
    f, P = periodograma(x)
    med = np.median(P)
    j = int(np.argmin(np.abs(f - 1.0/periodo_s)))
    return float(P[max(j-1,0):j+2].max()/med)

def fisher_g(x):
    _, P = periodograma(x)
    return float(P.max()/P.sum())

DIA, SEM = 86400.0, 7*86400.0
series = {
    "signo (binaria)":                 (2.0*bv - 1.0),
    "MAGNITUD BINARIZADA (binaria)":   (mag > np.median(mag)).astype(float)*2 - 1,
    "magnitud log|r| (continua)":      mag,
    "volumen (continua)":              vol[ok].astype(float),
}
print("\n" + "="*80)
print("EL MISMO CODIGO SOBRE LAS CUATRO SERIES")
print("="*80)
print(f"{'serie':<34}{'SNR 24 h':>11}{'SNR 7 d':>11}{'g de Fisher':>14}{'p(1)':>8}")
for nom, x in series.items():
    p1 = float(np.mean(x > np.percentile(x, 50.0001))) if len(set(np.round(x,9)))>2 else float(np.mean(x>0))
    print(f"{nom:<34}{snr(x,DIA):>11.1f}{snr(x,SEM):>11.1f}{fisher_g(x):>14.2e}{p1:>8.3f}")

# ---------- la prueba sin espectro: por hora del dia --------------------------
print("\n" + "="*80)
print("SIN ESPECTRO: LA MISMA PREGUNTA, POR HORA DEL DIA")
print("="*80)
hora = np.array([dt.datetime.fromtimestamp(int(t), dt.timezone.utc).hour for t in tsv])
b_mag = (mag > np.median(mag)).astype(int)
print(f"{'hora UTC':>9}{'p(sube)':>12}{'z':>8}   {'p(|r| > mediana)':>18}{'z':>8}")
zs_signo, zs_mag = [], []
for h in range(24):
    m = hora == h; n = m.sum()
    ps, pm = bv[m].mean(), b_mag[m].mean()
    zs = (ps-0.5)*np.sqrt(n)/0.5; zm = (pm-0.5)*np.sqrt(n)/0.5
    zs_signo.append(zs); zs_mag.append(zm)
    print(f"{h:>9}{ps:>12.4f}{zs:>8.2f}   {pm:>18.4f}{zm:>8.2f}")
zs_signo, zs_mag = np.array(zs_signo), np.array(zs_mag)
print(f"\n  amplitud del signo   : de {bv[hora==np.argmin([bv[hora==h].mean() for h in range(24)])].mean():.4f} "
      f"a {bv[hora==np.argmax([bv[hora==h].mean() for h in range(24)])].mean():.4f}")
print(f"  amplitud de la magnitud binarizada: de {min(b_mag[hora==h].mean() for h in range(24)):.4f} "
      f"a {max(b_mag[hora==h].mean() for h in range(24)):.4f}")
print(f"\n  max |z| del signo                  : {np.abs(zs_signo).max():.2f}")
print(f"  max |z| de la magnitud binarizada  : {np.abs(zs_mag).max():.2f}")
print(f"  umbral al 5 % para 24 horas probadas: {__import__('scipy.stats',fromlist=['norm']).norm.ppf(1-(1-0.95**(1/24))/2):.2f}")
np.savez('../datos/cap06_control.npz', hora=hora, bv=bv, b_mag=b_mag, mag=mag,
         zs_signo=zs_signo, zs_mag=zs_mag)
print("\n  guardado datos/cap06_control.npz")
