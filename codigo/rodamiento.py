"""Detector de fallo en rodamientos por analisis de envolvente y correlacion espectral ciclica.
Nunca mira la etiqueta: calcula una puntuacion para cada frecuencia caracteristica y elige."""
import numpy as np
from scipy.signal import hilbert, butter, sosfiltfilt, get_window

FS = 12000.0
# SKF 6205-2RS JEM (extremo motriz): 9 bolas, d=0,3126", D=1,537", angulo 0
MULT = {'BPFO': 3.5848, 'BPFI': 5.4152, 'BSF': 2.3568, 'FTF': 0.3983}

def freqs(rpm):
    fr = rpm/60.0
    f = {k: v*fr for k, v in MULT.items()}
    f['BSF2'] = 2*f['BSF']; f['fr'] = fr
    return f

# ---------- 1. kurtograma rapido: donde estan los impactos ----------
def spectral_kurtosis_band(x, fs=FS, nlev=4, fmin=300.0, fmax=5500.0, bwmin=350.0):
    """Kurtograma. Correcciones frente a la version ingenua:
       - la kurtosis se mide sobre la senal FILTRADA (impulsividad), no sobre su envolvente
       - ancho de banda minimo: las bandas ultraestrechas dan kurtosis espuria por borde de filtro
       - se excluye la vecindad de Nyquist, donde el filtro se degrada"""
    best = (-1e9, None)
    for lev in range(1, nlev+1):
        nb = 2**lev; bw = fs/2/nb
        if bw < bwmin: continue
        for b in range(nb):
            lo, hi = b*bw, (b+1)*bw
            if lo < fmin or hi > fmax: continue
            sos = butter(4, [lo/(fs/2), hi/(fs/2)], btype='band', output='sos')
            try: y = sosfiltfilt(sos, x)
            except Exception: continue
            y = y[int(.05*len(y)):int(.95*len(y))]          # descarta transitorio de borde
            k = float(((y-y.mean())**4).mean()/(y.var()**2+1e-30)) - 3.0
            if k > best[0]: best = (k, (lo, hi))
    return (best[1] if best[1] else (2000.0, 4000.0)), best[0]

# ---------- 2. envolvente ----------
def envelope_spectrum(x, band, fs=FS):
    lo, hi = band
    sos = butter(4, [max(lo,1)/(fs/2), min(hi,fs/2-1)/(fs/2)], btype='band', output='sos')
    y = sosfiltfilt(sos, x)
    env = np.abs(hilbert(y)); env = env - env.mean()
    w = get_window('hann', len(env))
    E = np.abs(np.fft.rfft(env*w))
    f = np.fft.rfftfreq(len(env), 1/fs)
    return f, E

# ---------- 3. puntuacion en una frecuencia caracteristica ----------
def score_at(f, E, f0, fr=None, nharm=4, tol=0.025, bg=(15.0, 900.0), sidebands=True):
    """SNR = media de los picos en f0 y armonicos sobre el fondo mediano local.
    Un fallo en pista INTERNA gira dentro de la zona de carga: su respuesta va modulada
    por la rotacion del eje y aparece en f0 +- fr. Sin contar bandas laterales se le
    subestima sistematicamente."""
    m = (f > bg[0]) & (f < bg[1])
    base = np.median(E[m]) + 1e-30
    peaks = []
    for h in range(1, nharm+1):
        t = f0*h
        if t > bg[1]: break
        cand = [t]
        if sidebands and fr: cand += [t-fr, t+fr]
        v = 0.0
        for c in cand:
            w = (f > c*(1-tol)) & (f < c*(1+tol))
            if w.sum(): v = max(v, float(E[w].max()))
        peaks.append(v/base)
    return float(np.mean(peaks)) if peaks else 0.0

def diagnose(x, rpm, fs=FS, band=None):
    """Diagnostico ciego: puntua cada frecuencia caracteristica y devuelve la ganadora."""
    F = freqs(rpm)
    if band is None: band, sk = spectral_kurtosis_band(x, fs)
    else: sk = np.nan
    f, E = envelope_spectrum(x, band, fs)
    sc = {k: score_at(f, E, F[k], fr=F['fr'], sidebands=(k!='BPFO')) for k in ('BPFO', 'BPFI', 'BSF2')}
    win = max(sc, key=sc.get)
    srt = sorted(sc.values(), reverse=True)
    margen = srt[0]/(srt[1]+1e-12)
    return dict(scores=sc, ganador=win, snr=srt[0], margen=margen, banda=band, sk=sk)

# ---------- 4. comparacion: FFT ordinaria (sin envolvente) ----------
def diagnose_fft(x, rpm, fs=FS):
    """El metodo ingenuo: buscar la frecuencia de fallo en el espectro directo."""
    F = freqs(rpm)
    w = get_window('hann', len(x))
    X = np.abs(np.fft.rfft((x-x.mean())*w)); f = np.fft.rfftfreq(len(x), 1/fs)
    sc = {k: score_at(f, X, F[k], fr=F['fr'], sidebands=(k!='BPFO')) for k in ('BPFO', 'BPFI', 'BSF2')}
    srt = sorted(sc.values(), reverse=True)
    return dict(scores=sc, ganador=max(sc, key=sc.get), snr=srt[0], margen=srt[0]/(srt[1]+1e-12))

# ---------- 5. nula construida DENTRO de la propia senal ----------
def score_null(f, E, fr, n=400, rng=None, lo=40.0, hi=500.0):
    """Puntuacion en n frecuencias arbitrarias del mismo espectro.
    Responde a: '¿es este pico notable DENTRO de esta senal?', que es la pregunta correcta.
    Un rodamiento sano tiene picos, pero ninguno destaca sobre los demas."""
    rng = rng or np.random.default_rng(0)
    fs_ = rng.uniform(lo, hi, n)
    return np.array([score_at(f, E, f0, fr=fr) for f0 in fs_])

def diagnose_v3(x, rpm, fs=FS, band=None, nnull=400, seed=0):
    F = freqs(rpm)
    if band is None: band, sk = spectral_kurtosis_band(x, fs)
    else: sk = np.nan
    f, E = envelope_spectrum(x, band, fs)
    sc = {k: score_at(f, E, F[k], fr=F['fr'], sidebands=(k != 'BPFO')) for k in ('BPFO','BPFI','BSF2')}
    null = score_null(f, E, F['fr'], n=nnull, rng=np.random.default_rng(seed))
    mu, sd = float(null.mean()), float(null.std(ddof=1)+1e-12)
    z = {k: (v-mu)/sd for k, v in sc.items()}
    p = {k: float((null >= sc[k]).mean()) for k in sc}
    win = max(z, key=z.get)
    return dict(scores=sc, z=z, p=p, ganador=win, zmax=z[win], pmin=p[win],
                banda=band, sk=sk, null_mu=mu, null_sd=sd)

# ---------- 6. puntuacion con familia de bandas laterales arbitraria ----------
def score_family(f, E, f0, fmod, nharm=4, nside=3, tol=0.02, bg=(15.0, 900.0), agg='sum'):
    """Suma (o maximo) de la energia de la familia f0*h +- k*fmod.
    Para un defecto en elemento rodante, el modulador correcto NO es la velocidad
    de eje sino la de jaula (FTF): el defecto entra y sale de la zona de carga a
    esa cadencia, asi que la energia se reparte en bandas laterales de FTF."""
    m = (f > bg[0]) & (f < bg[1])
    base = np.median(E[m]) + 1e-30
    tot = []
    for h in range(1, nharm+1):
        c0 = f0*h
        if c0 > bg[1]: break
        acc = []
        for k in range(-nside, nside+1):
            c = c0 + k*fmod
            if c <= bg[0] or c >= bg[1]: continue
            w = (f > c-max(tol*c, 1.0)) & (f < c+max(tol*c, 1.0))
            if w.sum(): acc.append(float(E[w].max()))
        if acc: tot.append((np.sum(acc) if agg == 'sum' else np.max(acc))/base)
    return float(np.mean(tot)) if tot else 0.0

def score_null_family(f, E, fmod, n=400, rng=None, lo=40.0, hi=500.0, **kw):
    rng = rng or np.random.default_rng(0)
    return np.array([score_family(f, E, f0, fmod, **kw) for f0 in rng.uniform(lo, hi, n)])

def diagnose_v4(x, rpm, fs=FS, band=None, nnull=350, seed=0):
    """Como v3, pero cada frecuencia caracteristica usa SU modulador fisico:
       BPFO -> ninguno (la pista externa esta fija en la zona de carga)
       BPFI -> velocidad de eje (el defecto gira con el eje)
       BSF  -> jaula (el elemento rodante orbita con la jaula)"""
    F = freqs(rpm)
    if band is None: band, sk = spectral_kurtosis_band(x, fs)
    else: sk = np.nan
    f, E = envelope_spectrum(x, band, fs)
    MOD = {'BPFO': 0.0, 'BPFI': F['fr'], 'BSF2': F['FTF']}
    z = {}; sc = {}; p = {}
    for k, fmod in MOD.items():
        s = score_family(f, E, F[k], fmod, nside=(0 if fmod == 0 else 3))
        nl = score_null_family(f, E, fmod, n=nnull, rng=np.random.default_rng(seed),
                               nside=(0 if fmod == 0 else 3))
        mu, sd = nl.mean(), nl.std(ddof=1)+1e-12
        sc[k] = s; z[k] = (s-mu)/sd; p[k] = float((nl >= s).mean())
    win = max(z, key=z.get)
    return dict(scores=sc, z=z, p=p, ganador=win, zmax=z[win], pmin=p[win], banda=band, sk=sk)

# ---------- 7. v5: firma de bola completa + puerta de calidad ----------
SK_MIN = 1.0   # por debajo de esta kurtosis de banda no hay nada impulsivo que demodular

def diagnose_v5(x, rpm, fs=FS, band=None, nnull=350, seed=0, sk_min=SK_MIN):
    """Tres cambios sobre v4:
    1. La firma de bola incluye los armonicos de JAULA (FTF), no solo 2xBSF. Un defecto
       en elemento rodante hace visible el paso de jaula aunque el propio BSF sea debil.
    2. Puerta de calidad: si la mejor banda no es impulsiva, el registro se declara
       NO DIAGNOSTICABLE en lugar de forzar una respuesta. Un detector que siempre
       responde miente en los casos en que no hay senal.
    3. Se reporta la kurtosis de banda como medida de confianza."""
    F = freqs(rpm)
    if band is None: band, sk = spectral_kurtosis_band(x, fs)
    else: _, sk = spectral_kurtosis_band(x, fs)
    f, E = envelope_spectrum(x, band, fs)
    rng = np.random.default_rng(seed)
    sc, z, p = {}, {}, {}
    # BPFO: pico limpio, sin modulacion
    for k, fmod, ns in (('BPFO', 0.0, 0), ('BPFI', F['fr'], 3)):
        s = score_family(f, E, F[k], fmod, nside=ns)
        nl = score_null_family(f, E, fmod, n=nnull, rng=np.random.default_rng(seed), nside=ns)
        sc[k] = s; z[k] = (s-nl.mean())/(nl.std(ddof=1)+1e-12); p[k] = float((nl >= s).mean())
    # BSF: max entre la familia 2xBSF+-FTF y los armonicos de jaula
    s1 = score_family(f, E, F['BSF2'], F['FTF'], nside=3)
    s2 = score_family(f, E, F['FTF'], 0.0, nside=0, nharm=5)
    nl1 = score_null_family(f, E, F['FTF'], n=nnull, rng=np.random.default_rng(seed), nside=3)
    nl2 = score_null_family(f, E, 0.0, n=nnull, rng=np.random.default_rng(seed), nside=0, nharm=5)
    z1 = (s1-nl1.mean())/(nl1.std(ddof=1)+1e-12); z2 = (s2-nl2.mean())/(nl2.std(ddof=1)+1e-12)
    sc['BSF2'] = max(s1, s2); z['BSF2'] = max(z1, z2)
    p['BSF2'] = float((nl1 >= s1).mean()) if z1 >= z2 else float((nl2 >= s2).mean())
    win = max(z, key=z.get)
    diag = 'NO DIAGNOSTICABLE' if sk < sk_min else win
    return dict(scores=sc, z=z, p=p, ganador=diag, bruto=win, zmax=z[win], pmin=p[win],
                banda=band, sk=sk, via=('FTF' if z2 > z1 else '2BSF'))
