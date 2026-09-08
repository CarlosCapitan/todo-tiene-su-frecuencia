#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cap10_demos.py — la misma bateria apuntada a cinco campos

Cinco demos autocontenidos, uno por campo. Cada uno construye una senal
realista del dominio, aplica el metodo NATIVO de ese campo y, al lado, el
metodo que casi todo el mundo aplica la primera vez. La diferencia entre
los dos numeros es la leccion del apartado.

No hace falta descargar nada: las senales se generan aqui. Los datos
publicos reales de cada campo estan citados en el capitulo.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras

import numpy as np

rng = np.random.default_rng(7)
R = {}

def snr_pico(P, i, fondo=(0.05, 0.95)):
    """Cuantas veces sobresale el bin i sobre la mediana del fondo."""
    lo, hi = int(len(P)*fondo[0]), int(len(P)*fondo[1])
    med = np.median(P[lo:hi])
    return float(P[i]/med) if med > 0 else float("nan")

# ---------------------------------------------------------------- 1. RADIO
def radio():
    """QPSK enterrada en ruido. Nativo: cicloestacionariedad a la tasa de
    simbolo. Ingenuo: espectro de potencia (que no distingue modulaciones)."""
    N, sps = 200_000, 8                      # 8 muestras por simbolo
    sym = rng.choice([1+1j, 1-1j, -1+1j, -1-1j], N//sps)
    s = np.repeat(sym, sps)                                  # QPSK rectangular
    x = s + (rng.normal(0,1.4,N) + 1j*rng.normal(0,1.4,N))   # SNR ~ -3 dB
    # control: ruido filtrado con el MISMO espectro de potencia, sin ciclos
    X = np.fft.fft(x); ph = np.exp(2j*np.pi*rng.random(len(X)))
    ctrl = np.fft.ifft(np.abs(X)*ph)

    def ciclo(z, alpha, tau):
        """|<z(t) z*(t+tau) e^{-j2pi alpha t}>| : correlacion ciclica."""
        a = z[:len(z)-tau]; b = np.conj(z[tau:])
        t = np.arange(len(a))
        return float(abs(np.mean(a*b*np.exp(-2j*np.pi*alpha*t))))

    a, tau = 1.0/sps, sps//2                  # tasa de simbolo y retardo medio
    fondo = np.median([ciclo(x, aa, tau) for aa in rng.uniform(0.02, 0.45, 80)])
    R['radio'] = dict(
        ciclo_senal   = ciclo(x, a, tau)/fondo,
        ciclo_control = ciclo(ctrl, a, tau)/fondo,
        psd_dif_pct   = float(100*np.mean(np.abs(np.abs(np.fft.fft(x))**2
                                                 - np.abs(np.fft.fft(ctrl))**2))
                              / np.mean(np.abs(np.fft.fft(x))**2)),
    )

# ------------------------------------------------------------- 2. BIOMEDICA
def ecg():
    """ECG sintetico: tren de latidos NO sinusoidal a 72 lpm con variabilidad.
    Nativo: autocorrelacion / envolvente. Ingenuo: buscar el pico de la FFT."""
    fs, dur = 250, 300                       # 5 min
    n = fs*dur; t = np.arange(n)/fs
    fc = 72/60.0                             # 1,2 Hz
    x = np.zeros(n); tt = 0.0
    while tt < dur:
        i = int(tt*fs)
        if i+60 < n:                         # complejo QRS estrecho + onda T
            k = np.arange(60)
            x[i:i+60] += np.exp(-((k-10)/2.5)**2)*1.0 - np.exp(-((k-16)/3.5)**2)*0.35 \
                       + np.exp(-((k-40)/9.0)**2)*0.22
        tt += 1/fc * (1 + 0.06*rng.normal())  # variabilidad latido a latido
    x += 0.25*rng.normal(0,1,n) + 0.5*np.sin(2*np.pi*0.25*t)   # ruido + deriva

    P = np.abs(np.fft.rfft(x - x.mean()))**2
    f = np.fft.rfftfreq(n, 1/fs)
    i_fund = int(np.argmin(abs(f-fc)))
    banda = (f > 0.6) & (f < 3.0)            # 36-180 lpm: rango cardiaco plausible
    i_max = int(np.where(banda)[0][int(np.argmax(P[banda]))])
    i_libre = int(np.argmax(P[1:])) + 1
    # nativo: envolvente del QRS (banda 8-25 Hz) y autocorrelacion del tacograma
    F = np.fft.rfft(x); F[(f < 8) | (f > 25)] = 0
    env = np.abs(np.fft.irfft(F, n)); env -= env.mean()
    ac = np.correlate(env, env, 'full')[n-1:]; ac /= ac[0]
    lo, hi = int(fs/3.0), int(fs/0.6)        # mismos 36-180 lpm
    lag = int(np.argmax(ac[lo:hi])) + lo
    R['ecg'] = dict(
        fc_real = fc,
        fft_pico_hz = float(f[i_max]),
        fft_libre_hz = float(f[i_libre]),
        error_fft_libre_pct = 100*abs(f[i_libre]-fc)/fc,
        fft_snr_en_fundamental = snr_pico(P, i_fund),
        autocorr_hz = fs/lag,
        error_fft_pct = 100*abs(f[i_max]-fc)/fc,
        error_autocorr_pct = 100*abs(fs/lag-fc)/fc,
    )

# ------------------------------------------------------------- 3. DEMANDA
def demanda():
    """Demanda electrica: ciclo diario + semanal + tendencia. Se correlaciona
    con una serie INDEPENDIENTE que tiene los mismos ciclos."""
    n = 24*365*2                              # 2 anos horarios
    t = np.arange(n)
    est = (1.0*np.sin(2*np.pi*t/24 - 1.2) + 0.4*np.sin(2*np.pi*t/168)
           + 0.6*np.sin(2*np.pi*t/8766) + t*2e-5)
    d1 = est + rng.normal(0,0.35,n)
    d2 = est + rng.normal(0,0.35,n)           # independiente, mismos ciclos
    r_bruto = float(np.corrcoef(d1,d2)[0,1])
    # quitando la estacionalidad conocida (media por hora-del-dia y dia-semana)
    def desestacionalizar(y):
        h = t % 24; dw = (t//24) % 7
        z = y.copy()
        for k in range(24): z[h==k] -= z[h==k].mean()
        for k in range(7):  z[dw==k] -= z[dw==k].mean()
        # ciclo anual + tendencia por minimos cuadrados
        A = np.column_stack([np.ones(n), t,
                             np.sin(2*np.pi*t/8766), np.cos(2*np.pi*t/8766),
                             np.sin(4*np.pi*t/8766), np.cos(4*np.pi*t/8766)])
        z = z - A @ np.linalg.lstsq(A, z, rcond=None)[0]
        return z
    r_limpio = float(np.corrcoef(desestacionalizar(d1), desestacionalizar(d2))[0,1])
    R['demanda'] = dict(r_bruto=r_bruto, r_desestacionalizado=r_limpio)

# ------------------------------------------------------------- 4. SISMICA
def sismica():
    """Evento transitorio que ocupa el 2 % del registro (llegada P).
    Nativo: plano tiempo-frecuencia. Ingenuo: periodograma de todo el registro."""
    n, fs = 120_000, 100.0
    x = rng.normal(0, 1, n)
    i0, L = 60_000, 2_400                     # 24 s de 1200 s = 2 %
    k = np.arange(L)
    x[i0:i0+L] += 2.2*np.exp(-k/500)*np.sin(2*np.pi*6.0*k/fs)   # fase P a 6 Hz
    f = np.fft.rfftfreq(n, 1/fs); P = np.abs(np.fft.rfft(x))**2
    i6 = int(np.argmin(abs(f-6.0)))
    # tiempo-frecuencia: maxima energia en la banda 5-7 Hz por ventanas de 10 s
    W = int(10*fs); mejores = []
    for s in range(0, n-W, W//2):
        seg = x[s:s+W]*np.hanning(W)
        Ps = np.abs(np.fft.rfft(seg))**2; fs_ = np.fft.rfftfreq(W, 1/fs)
        b = (fs_>5)&(fs_<7)
        mejores.append(Ps[b].max()/np.median(Ps))
    R['sismica'] = dict(periodograma_global=snr_pico(P,i6),
                        tiempo_frecuencia=float(max(mejores)),
                        fraccion_del_registro=100*L/n)

# ------------------------------------------------------------ 5. ASTRONOMIA
def astronomia():
    """Curva de luz con muestreo IRREGULAR (huecos diurnos y meteorologicos).
    Nativo: Lomb-Scargle. Ingenuo: interpolar a rejilla y hacer FFT."""
    P0 = 0.83                                   # dias (sub-diario: zona de alias)
    t = np.sort(rng.uniform(0, 400, 900))
    t = t[(t % 1.0) < 0.42]                     # solo se observa de noche
    y = 1.0*np.sin(2*np.pi*t/P0) + rng.normal(0, 0.6, len(t))
    frec = np.linspace(1/50, 1/0.4, 40_000)
    # Lomb-Scargle (implementacion directa, sin dependencias)
    def lomb(t, y, w):
        y = y - y.mean(); P = np.empty(len(w))
        for i, wi in enumerate(w):
            wt = 2*np.pi*wi*t
            tau = 0.5*np.arctan2(np.sum(np.sin(2*wt)), np.sum(np.cos(2*wt)))
            c, s = np.cos(wt-tau), np.sin(wt-tau)
            P[i] = 0.5*((y@c)**2/np.sum(c*c) + (y@s)**2/np.sum(s*s))
        return P/np.var(y)
    idx = np.linspace(0, len(frec)-1, 4000).astype(int)
    PL = lomb(t, y, frec[idx])
    fl = frec[idx][int(np.argmax(PL))]
    # ingenuo: interpolar a rejilla uniforme y FFT
    tg = np.arange(0, 400, 0.02); yg = np.interp(tg, t, y)
    PF = np.abs(np.fft.rfft(yg - yg.mean()))**2
    ff = np.fft.rfftfreq(len(tg), 0.02)
    m = (ff > 1/50) & (ff < 1/0.4)
    ffft = ff[m][int(np.argmax(PF[m]))]
    R['astronomia'] = dict(periodo_real=P0,
                           lomb_periodo=float(1/fl),
                           fft_interp_periodo=float(1/ffft),
                           error_lomb_pct=100*abs(1/fl-P0)/P0,
                           error_fft_pct=100*abs(1/ffft-P0)/P0,
                           n_muestras=int(len(t)))

for fn in (radio, ecg, demanda, sismica, astronomia):
    fn()

print("="*74)
print("CINCO CAMPOS, LA MISMA BATERIA")
print("="*74)
print(f"""
1. ESPECTRO RADIO — QPSK a -3 dB de SNR
   cicloestacionariedad a la tasa de simbolo, senal .... {R['radio']['ciclo_senal']:8.1f} x fondo
   el mismo estadistico sobre un control con IDENTICO
   espectro de potencia y sin ciclos ................... {R['radio']['ciclo_control']:8.1f} x fondo
   -> el espectro de potencia no las distingue; la firma ciclica si.

2. BIOMEDICA — ECG sintetico a {R['ecg']['fc_real']*60:.0f} lpm ({R['ecg']['fc_real']:.2f} Hz)
   FFT sin acotar, pico maximo ................... {R['ecg']['fft_libre_hz']:.3f} Hz  (error {R['ecg']['error_fft_libre_pct']:5.1f} %)
   FFT acotada a 36-180 lpm ...................... {R['ecg']['fft_pico_hz']:.3f} Hz  (error {R['ecg']['error_fft_pct']:5.1f} %)
   envolvente QRS + autocorrelacion .............. {R['ecg']['autocorr_hz']:.3f} Hz  (error {R['ecg']['error_autocorr_pct']:5.1f} %)
   realce de la FFT en la fundamental ............ {R['ecg']['fft_snr_en_fundamental']:.1f} x el fondo

3. DEMANDA ELECTRICA — dos series INDEPENDIENTES con los mismos ciclos
   correlacion en bruto .......................... {R['demanda']['r_bruto']:+.3f}
   tras quitar hora-del-dia, dia-semana y tendencia  {R['demanda']['r_desestacionalizado']:+.3f}
   -> la correlacion verdadera es 0. La primera cifra es toda estacionalidad.

4. SISMICA — fase P a 6 Hz que ocupa el {R['sismica']['fraccion_del_registro']:.0f} % del registro
   periodograma promediado sobre todo el registro  {R['sismica']['periodograma_global']:8.1f} x fondo
   plano tiempo-frecuencia (ventanas de 10 s) .... {R['sismica']['tiempo_frecuencia']:8.1f} x fondo

5. ASTRONOMIA — curva de luz irregular, {R['astronomia']['n_muestras']} puntos, periodo real {R['astronomia']['periodo_real']} d
   Lomb-Scargle .................................. {R['astronomia']['lomb_periodo']:.4f} d  (error {R['astronomia']['error_lomb_pct']:5.2f} %)
   interpolar a rejilla + FFT .................... {R['astronomia']['fft_interp_periodo']:.4f} d  (error {R['astronomia']['error_fft_pct']:5.2f} %)
""")
np.save(datos('cap10_resultados.npy'), R, allow_pickle=True)
