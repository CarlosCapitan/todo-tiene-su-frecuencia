import numpy as np
from numpy.fft import rfft, irfft, fft

# ---------- surrogados ----------
def iaaft(x, iters=120, rng=None):
    """Surrogado IAAFT: conserva el espectro de potencia Y la distribucion de amplitudes,
    destruye la estructura no lineal / de fase."""
    rng=rng or np.random.default_rng()
    n=len(x); amp=np.abs(rfft(x)); srt=np.sort(x)
    y=rng.permutation(x)
    for _ in range(iters):
        Y=rfft(y); Y=amp*np.exp(1j*np.angle(Y)); y=irfft(Y,n)
        y=srt[np.argsort(np.argsort(y))]
    return y

def phase_surrogate(x, rng=None):
    """Aleatoriza fases: conserva exactamente la PSD."""
    rng=rng or np.random.default_rng()
    n=len(x); X=rfft(x); ph=rng.uniform(0,2*np.pi,len(X)); ph[0]=0
    if n%2==0: ph[-1]=0
    return irfft(np.abs(X)*np.exp(1j*ph), n)

# ---------- 1. cicloestacionariedad ----------
def cyclic_autocorr(x, lags, alphas=None):
    """R(alpha,tau) = (1/N) sum_t x(t)x(t+tau) e^{-i 2 pi alpha t}.
    Se calcula por FFT del producto de retardo: da TODOS los alpha de golpe."""
    x=np.asarray(x,float); x=x-x.mean(); N=len(x)
    out={}
    for tau in lags:
        z=(x*x) if tau==0 else x[:N-tau]*x[tau:]
        z=z-z.mean()                      # quita alpha=0 (autocorrelacion ordinaria)
        Z=np.abs(rfft(z))**2
        out[tau]=Z/np.median(Z[1:])       # potencia ciclica normalizada
    return out

def cyclo_stat(x, lags=(0,1,2,3,4,6,12,24,48,96,144,288), targets=(288,2016)):
    """Estadistico: maxima potencia ciclica normalizada, y potencia en las
    frecuencias ciclicas objetivo (diaria=1/288, semanal=1/2016) y sus armonicos."""
    N=len(x); C=cyclic_autocorr(x,lags)
    res={'max':0.0,'max_tau':None,'max_alpha':None,'targets':{}}
    for tau,Z in C.items():
        k=int(np.argmax(Z[1:]))+1
        if Z[k]>res['max']: res.update(max=float(Z[k]),max_tau=int(tau),max_alpha=k/(N-tau))
    for T in targets:
        best=0.0; bh=None; bt=None
        for h in (1,2,3,4):
            for tau,Z in C.items():
                # ERROR CORREGIDO: el indice de bin depende del retardo. La serie
                # de producto de retardo tiene N-tau muestras, no N, asi que cada
                # tau tiene su propio numero de bins y su propia frecuencia ciclica
                # por bin. Con series largas el desfase es de un bin y pasa
                # inadvertido; con series cortas el indice se sale del array.
                nbt=len(Z)
                b=int(round((N-tau)*h/T))
                if b<3 or b>=nbt-3: continue
                w=Z[b-2:b+3].max()
                lo=max(1,b-400); hi=min(nbt,b+400)
                bg=np.median(np.concatenate([Z[lo:b-4],Z[b+5:hi]]))
                snr=w/(bg+1e-12)
                if snr>best: best=float(snr); bh=h; bt=int(tau)
        res['targets'][T]={'snr':best,'armonico':bh,'tau':bt}
    return res

# ---------- 2. biespectro ----------
def bicoherence(x, nfft=256, overlap=0.5):
    x=np.asarray(x,float); x=x-x.mean()
    step=int(nfft*(1-overlap)); segs=[]
    w=np.hanning(nfft)
    for s in range(0,len(x)-nfft,step): segs.append(rfft(x[s:s+nfft]*w))
    X=np.array(segs); K=len(X); nf=nfft//2
    f1,f2=np.meshgrid(np.arange(nf//2+1),np.arange(nf//2+1),indexing='ij')
    m=(f1+f2)<=nf
    B=np.zeros(f1.shape,complex); P12=np.zeros(f1.shape); P3=np.zeros(f1.shape)
    A=X[:,f1]; Bb=X[:,f2]; Cc=np.conj(X[:,np.clip(f1+f2,0,nf)])
    B=(A*Bb*Cc).mean(0)
    P12=(np.abs(A*Bb)**2).mean(0); P3=(np.abs(Cc)**2).mean(0)
    bic=np.where(m,(np.abs(B)**2)/(P12*P3+1e-30),np.nan)
    return bic, K

def bic_stat(x, nfft=256):
    bic,K=bicoherence(x,nfft)
    v=bic[np.isfinite(bic)]
    return {'mean':float(v.mean()),'max':float(v.max()),'K':int(K),
            'expected_mean':1.0/K,'ratio':float(v.mean()*K)}

def third_cumulant(x, L=20):
    """C(t1,t2)=E[x(t)x(t+t1)x(t+t2)] normalizado."""
    x=np.asarray(x,float); x=(x-x.mean())/x.std(); N=len(x)
    C=np.zeros((L+1,L+1))
    for a in range(L+1):
        for b in range(a,L+1):
            m=N-b
            v=float((x[:m]*x[a:a+m]*x[b:b+m]).mean())
            C[a,b]=C[b,a]=v
    return C

# ---------- 3. tiempo-frecuencia ----------
def morlet_cwt(x, scales, w0=6.0):
    x=np.asarray(x,float); x=x-x.mean(); n=len(x)
    nf=int(2**np.ceil(np.log2(n)))
    X=fft(x,nf); om=2*np.pi*np.fft.fftfreq(nf)
    out=np.empty((len(scales),n))
    for i,s in enumerate(scales):
        psi=(np.pi**-.25)*np.sqrt(s)*np.exp(-.5*(s*om-w0)**2)*(om>0)
        out[i]=np.abs(np.fft.ifft(X*psi)[:n])**2
    return out

def tf_stat(x, scales):
    W=morlet_cwt(x,scales)
    Wn=W/np.median(W,axis=1,keepdims=True)
    return {'max':float(Wn.max()),'max_scale':float(scales[int(np.unravel_index(Wn.argmax(),Wn.shape)[0])]),
            'p999':float(np.quantile(Wn,.999))}

# ---------- 4. caos ----------
def embed(x,m,tau):
    n=len(x)-(m-1)*tau
    return np.column_stack([x[i*tau:i*tau+n] for i in range(m)])

def false_nn(x, ms=range(1,11), tau=1, rtol=10.0):
    from scipy.spatial import cKDTree
    out=[]
    for m in ms:
        Y=embed(x,m,tau); Y2=embed(x,m+1,tau); n=len(Y2)
        Y=Y[:n]
        t=cKDTree(Y); d,idx=t.query(Y,k=2)
        d1=d[:,1]; j=idx[:,1]
        d2=np.abs(Y2[:,-1]-Y2[j,-1])
        ok=d1>1e-12
        out.append(float((d2[ok]/d1[ok]>rtol).mean()))
    return list(ms),out

def corr_dim(x, m=6, tau=1, npts=4000, rng=None):
    from scipy.spatial import cKDTree
    rng=rng or np.random.default_rng(0)
    Y=embed(x,m,tau)
    if len(Y)>npts: Y=Y[rng.choice(len(Y),npts,replace=False)]
    t=cKDTree(Y)
    sd=Y.std()
    rs=np.logspace(np.log10(sd*.05),np.log10(sd*1.5),18)
    c=[t.count_neighbors(t,r)/len(Y)**2 for r in rs]
    c=np.array(c); m_=(c>1e-5)&(c<.5)
    if m_.sum()<4: return np.nan
    return float(np.polyfit(np.log(rs[m_]),np.log(c[m_]),1)[0])

def lyapunov_rosenstein(x, m=6, tau=1, npts=3000, horizon=25, theiler=300, rng=None):
    from scipy.spatial import cKDTree
    rng=rng or np.random.default_rng(0)
    Y=embed(x,m,tau); N=len(Y)-horizon
    idx=rng.choice(N,min(npts,N),replace=False)
    t=cKDTree(Y[:N])
    div=np.zeros(horizon); cnt=np.zeros(horizon)
    for i in idx:
        d,j=t.query(Y[i],k=60)
        good=[jj for dd,jj in zip(d,j) if abs(jj-i)>theiler]
        if not good: continue
        jj=good[0]
        for h in range(horizon):
            dd=np.linalg.norm(Y[i+h]-Y[jj+h])
            if dd>0: div[h]+=np.log(dd); cnt[h]+=1
    ok=cnt>20
    if ok.sum()<6: return np.nan,None
    curve=div[ok]/cnt[ok]
    hh=np.arange(horizon)[ok]
    k=min(10,len(hh)); 
    return float(np.polyfit(hh[:k],curve[:k],1)[0]), (hh,curve)
