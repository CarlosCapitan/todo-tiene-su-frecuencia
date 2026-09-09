"""Bateria de deteccion de estructura — nucleo comun del libro.

Todas las funciones responden, de una forma u otra, a la misma pregunta:
¿es esto notable DENTRO de esta señal, o es lo que cabria esperar por azar?
"""
import numpy as np
from math import erfc, sqrt, log, log2
from numpy.fft import rfft, irfft

# ============================================================
#  Generadores de referencia
# ============================================================
def lfsr(n, taps=(32, 22, 2, 1), estado=0xACE1ACE1, ancho=32):
    """Registro de desplazamiento con realimentacion lineal.
    Determinista por completo: el estado son `ancho` bits y la secuencia
    queda fijada por ellos. Se rompe observando 2*ancho bits."""
    out = np.zeros(n, dtype=np.int8)
    s = estado
    mask = (1 << ancho) - 1
    for i in range(n):
        b = 0
        for t in taps:
            b ^= (s >> (t-1)) & 1
        s = ((s << 1) | b) & mask
        out[i] = b
    return out

# ============================================================
#  Los tests que NO lo detectan
# ============================================================
def monobit(b):
    n = len(b); s = int((2*b.astype(int)-1).sum())
    z = abs(s)/sqrt(n)
    return dict(n=n, S=s, z=z, p=erfc(z/sqrt(2)))

def rachas(b):
    n = len(b); pi = b.mean()
    if abs(pi-0.5) >= 2/sqrt(n):
        return dict(p=0.0, nota="falla el prerrequisito de monobit")
    v = 1 + int((b[1:] != b[:-1]).sum())
    z = abs(v - 2*n*pi*(1-pi)) / (2*sqrt(2*n)*pi*(1-pi))
    return dict(V=v, esperado=2*n*pi*(1-pi), z=z, p=erfc(z/sqrt(2)))

def dft_nist(b):
    """Test espectral del NIST SP 800-22: cuenta picos por encima del umbral."""
    n = len(b); x = 2*b.astype(float)-1
    S = np.abs(rfft(x))[1:n//2+1]
    T = sqrt(log(1/0.05)*n)
    N0 = 0.95*n/2; N1 = float((S < T).sum())
    d = (N1-N0)/sqrt(n*0.95*0.05/4)
    return dict(T=T, N0=N0, N1=N1, d=d, p=erfc(abs(d)/sqrt(2)), S=S)

def autocorr(b, maxlag):
    x = 2*b.astype(float)-1; x -= x.mean(); n = len(x)
    f = rfft(x, 2*n)
    ac = irfft(f*np.conj(f))[:maxlag+1]
    return ac/ac[0]

def fwht(a):
    """Transformada rapida de Walsh-Hadamard, in-place por niveles."""
    a = a.astype(np.float64).copy(); h = 1; n = len(a)
    while h < n:
        for i in range(0, n, h*2):
            x = a[i:i+h].copy(); y = a[i+h:i+2*h].copy()
            a[i:i+h] = x+y; a[i+h:i+2*h] = x-y
        h *= 2
    return a

def walsh_lineal(b, k=16):
    """Criptoanalisis lineal: correlacion del bit siguiente con TODA combinacion
    lineal de los k bits previos, calculada de golpe por Walsh-Hadamard."""
    n = len(b)-k
    w = np.zeros(n, dtype=np.int64)
    for i in range(k):
        w = (w << 1) | b[i:n+i].astype(np.int64)
    y = 1 - 2*b[k:].astype(np.float64)
    T = np.bincount(w, weights=y, minlength=2**k)
    return fwht(T)/n * sqrt(n)          # z-scores

# ============================================================
#  El test que SI lo detecta
# ============================================================
def berlekamp_massey(bits):
    """Registro de desplazamiento lineal mas corto que genera la secuencia.
    Implementado con enteros de Python como vectores de bits: el producto
    escalar sobre GF(2) es un AND seguido de la paridad del popcount."""
    N = len(bits); C = 1; B = 1; L = 0; m = -1; R = 0
    for n in range(N):
        R = (R << 1) | int(bits[n])
        if (C & R).bit_count() & 1:      # discrepancia
            T = C
            C ^= (B << (n-m))
            if 2*L <= n:
                L = n+1-L; B = T; m = n
    return L, C

def perfil_complejidad(bits, puntos):
    """Complejidad lineal L(n) evaluada en una lista creciente de n."""
    N = len(bits); C = 1; B = 1; L = 0; m = -1; R = 0
    prof = []; cps = set(puntos)
    for i in range(N):
        R = (R << 1) | int(bits[i])
        if (C & R).bit_count() & 1:
            T = C; C ^= (B << (i-m))
            if 2*L <= i:
                L = i+1-L; B = T; m = i
        if (i+1) in cps:
            prof.append((i+1, L))
    return prof

# ============================================================
#  Nulas
# ============================================================
def umbral_multitest(N):
    """Umbral de |z| esperado como maximo de N estadisticos normales."""
    return sqrt(2*log(N))

def surrogado_fase(x, rng=None):
    """Aleatoriza las fases: conserva EXACTAMENTE el espectro de potencia."""
    rng = rng or np.random.default_rng()
    n = len(x); X = rfft(x)
    ph = rng.uniform(0, 2*np.pi, len(X)); ph[0] = 0
    if n % 2 == 0: ph[-1] = 0
    return irfft(np.abs(X)*np.exp(1j*ph), n)

def iaaft(x, iters=100, rng=None):
    """Surrogado IAAFT: conserva el espectro de potencia Y la distribucion
    de amplitudes. Destruye solo la estructura no lineal / de fase."""
    rng = rng or np.random.default_rng()
    n = len(x); amp = np.abs(rfft(x)); srt = np.sort(x)
    y = rng.permutation(x)
    for _ in range(iters):
        Y = rfft(y); y = irfft(amp*np.exp(1j*np.angle(Y)), n)
        y = srt[np.argsort(np.argsort(y))]
    return y

# ============================================================
#  Controles sinteticos con estructura conocida  (capitulo 2)
# ============================================================
def control_blanco(n, rng=None):
    """A · ruido gaussiano. Linea base: si un metodo salta aqui, tiene falsos positivos."""
    rng = rng or np.random.default_rng(0)
    return rng.normal(size=n)

def control_am(n, periodo=288, prof=0.30, rng=None):
    """B · cicloestacionario: ruido modulado en amplitud. Su PSD es casi plana;
    la estructura vive en la correlacion espectral ciclica."""
    rng = rng or np.random.default_rng(1)
    t = np.arange(n)
    return rng.normal(size=n)*(1 + prof*np.cos(2*np.pi*t/periodo))

def control_fases(n, f1=0.11, f2=0.17, amp=1.2, rng=None):
    """C · acoplamiento cuadratico de fases: tres tonos en f1, f2 y f1+f2 con fases
    ligadas. El espectro de potencia no lo distingue de tres tonos independientes."""
    rng = rng or np.random.default_rng(2)
    t = np.arange(n); p1, p2 = rng.uniform(0, 2*np.pi, 2)
    s = (np.cos(2*np.pi*f1*t+p1) + np.cos(2*np.pi*f2*t+p2)
         + np.cos(2*np.pi*(f1+f2)*t+p1+p2))
    return amp*s + rng.normal(size=n)

def control_rafaga(n, inicio=None, dur=2000, periodo=60, amp=1.8, rng=None):
    """D · periodicidad transitoria: vive `dur` muestras y se apaga. Invisible en un
    periodograma promediado sobre toda la serie."""
    rng = rng or np.random.default_rng(3)
    x = rng.normal(size=n); s = inicio if inicio is not None else n//3
    x[s:s+dur] += amp*np.sin(2*np.pi*np.arange(dur)/periodo)
    return x

def control_henon(n, a=1.4, b=0.3, x0=0.1, y0=0.3):
    """E · caos determinista. Espectro de banda ancha, atractor de dimension baja."""
    x, y = x0, y0; out = np.empty(n)
    for i in range(n):
        x, y = 1 - a*x*x + y, b*x
        out[i] = x
    return out

def controles(n=50000):
    return {'A · ruido blanco': control_blanco(n),
            'B · AM ciclo 288': control_am(n),
            'C · acoplamiento de fases': control_fases(n),
            'D · ráfaga transitoria': control_rafaga(n),
            'E · Hénon (caos)': control_henon(n)}

# ============================================================
#  Los seis metodos  (capitulo 2)
# ============================================================
def autocorr_ciclica(x, retardos=(0,1,2,3,4,6,12,24,48,96,144,288)):
    """R(alpha,tau) = (1/N) sum_t x(t)x(t+tau) e^{-i2*pi*alpha*t}.
    Se calcula por FFT del producto de retardo: todos los alpha de una vez.
    OJO con tau=0: es donde vive la modulacion de amplitud pura. Omitirlo hace
    que el metodo no detecte su propio control (ver seccion 2.4)."""
    x = np.asarray(x, float); x = x - x.mean(); N = len(x); out = {}
    for tau in retardos:
        z = (x*x) if tau == 0 else x[:N-tau]*x[tau:]
        z = z - z.mean()
        Z = np.abs(rfft(z))**2
        out[tau] = Z/np.median(Z[1:])
    return out

def ciclo_snr(x, periodos=(288, 2016)):
    """SNR de la potencia ciclica en los periodos objetivo, contra el fondo local."""
    N = len(x); C = autocorr_ciclica(x)
    res = {}
    for T in periodos:
        best = 0.0
        for h in (1, 2, 3, 4):
            for tau, Z in C.items():
                # OJO con la longitud: el producto de retardo tiene N-tau muestras,
                # asi que cada tau tiene su propio numero de bins y su propia
                # frecuencia ciclica por bin. Usar N para todos desplaza el bin
                # objetivo (inadvertido en series largas) y con series cortas
                # saca el indice del array. Es el error de la seccion 8.x.
                nbt = len(Z)
                b = int(round((N-tau)*h/T))
                if b < 3 or b >= nbt-3: continue
                pico = Z[b-2:b+3].max()
                lo, hi = max(1, b-400), min(nbt, b+400)
                fondo = np.median(np.concatenate([Z[lo:b-4], Z[b+5:hi]]))
                best = max(best, float(pico/(fondo+1e-12)))
        res[T] = best
    return res

def bicoherencia(x, nfft=256, solape=0.5):
    """Bicoherencia normalizada. Un proceso gaussiano lineal la tiene ~1/K;
    el acoplamiento cuadratico de fases la dispara."""
    x = np.asarray(x, float); x = x - x.mean()
    paso = int(nfft*(1-solape)); w = np.hanning(nfft)
    X = np.array([rfft(x[s:s+nfft]*w) for s in range(0, len(x)-nfft, paso)])
    K = len(X); nf = nfft//2
    f1, f2 = np.meshgrid(np.arange(nf//2+1), np.arange(nf//2+1), indexing='ij')
    m = (f1+f2) <= nf
    A = X[:, f1]; Bb = X[:, f2]; Cc = np.conj(X[:, np.clip(f1+f2, 0, nf)])
    B = (A*Bb*Cc).mean(0)
    bic = np.where(m, np.abs(B)**2/((np.abs(A*Bb)**2).mean(0)*(np.abs(Cc)**2).mean(0)+1e-30), np.nan)
    v = bic[np.isfinite(bic)]
    return float(v.mean()*K)          # ratio sobre el valor esperado 1/K

def cwt_morlet(x, escalas, w0=6.0):
    x = np.asarray(x, float); x = x - x.mean(); n = len(x)
    nf = int(2**np.ceil(np.log2(n)))
    X = np.fft.fft(x, nf); om = 2*np.pi*np.fft.fftfreq(nf)
    out = np.empty((len(escalas), n))
    for i, s in enumerate(escalas):
        psi = (np.pi**-.25)*np.sqrt(s)*np.exp(-.5*(s*om-w0)**2)*(om > 0)
        out[i] = np.abs(np.fft.ifft(X*psi)[:n])**2
    return out

def tf_max(x, escalas=None):
    """Maximo del escalograma normalizado por la mediana de cada escala.
    Detecta periodicidades que viven poco y se apagan."""
    escalas = escalas if escalas is not None else np.logspace(np.log10(4), np.log10(3000), 44)
    W = cwt_morlet(x, escalas)
    return float((W/np.median(W, axis=1, keepdims=True)).max())

def embed(x, m, tau=1):
    n = len(x)-(m-1)*tau
    return np.column_stack([x[i*tau:i*tau+n] for i in range(m)])

def falsos_vecinos(x, ms=range(1, 9), tau=1, rtol=10.0):
    """Fraccion de vecinos que dejan de serlo al anadir una dimension.
    Un atractor de dimension baja la lleva a cero pronto; el ruido decae suave."""
    from scipy.spatial import cKDTree
    out = []
    for m in ms:
        Y = embed(x, m, tau); Y2 = embed(x, m+1, tau); n = len(Y2); Y = Y[:n]
        d, idx = cKDTree(Y).query(Y, k=2)
        d1 = d[:, 1]; j = idx[:, 1]
        d2 = np.abs(Y2[:, -1]-Y2[j, -1])
        ok = d1 > 1e-12
        out.append(float((d2[ok]/d1[ok] > rtol).mean()) if ok.sum() else np.nan)
    return list(ms), out

def lyapunov(x, m=5, tau=1, npts=1200, horizonte=20, theiler=300, rng=None):
    """Exponente de Lyapunov por el metodo de Rosenstein: pendiente inicial de la
    divergencia media entre trayectorias inicialmente proximas."""
    from scipy.spatial import cKDTree
    rng = rng or np.random.default_rng(0)
    Y = embed(x, m, tau); N = len(Y)-horizonte
    idx = rng.choice(N, min(npts, N), replace=False)
    t = cKDTree(Y[:N]); div = np.zeros(horizonte); cnt = np.zeros(horizonte)
    for i in idx:
        d, j = t.query(Y[i], k=60)
        good = [jj for dd, jj in zip(d, j) if abs(jj-i) > theiler]
        if not good: continue
        jj = good[0]
        for h in range(horizonte):
            dd = np.linalg.norm(Y[i+h]-Y[jj+h])
            if dd > 0: div[h] += np.log(dd); cnt[h] += 1
    ok = cnt > 20
    if ok.sum() < 6: return np.nan
    hh = np.arange(horizonte)[ok]; curva = div[ok]/cnt[ok]
    k = min(10, len(hh))
    return float(np.polyfit(hh[:k], curva[:k], 1)[0])
