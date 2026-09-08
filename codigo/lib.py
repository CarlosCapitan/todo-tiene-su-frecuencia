import numpy as np
from math import erfc, sqrt, log, log2

def monobit(b):
    n=len(b); s=int((2*b.astype(int)-1).sum())
    z=abs(s)/sqrt(n); return dict(n=n, S=s, z=z, p=erfc(z/sqrt(2)))

def runs_test(b):
    n=len(b); pi=b.mean()
    if abs(pi-0.5)>=2/sqrt(n): return dict(p=0.0, note="falla prerrequisito monobit")
    v=1+int((b[1:]!=b[:-1]).sum())
    num=abs(v-2*n*pi*(1-pi)); den=2*sqrt(2*n)*pi*(1-pi)
    z=num/den
    return dict(V=v, expected=2*n*pi*(1-pi), z=z, p=erfc(z/sqrt(2)))

def longest_run_ones(b):
    best=cur=0
    for x in b:
        cur = cur+1 if x else 0
        best=max(best,cur)
    bestd=curd=0
    for x in b:
        curd = curd+1 if not x else 0
        bestd=max(bestd,curd)
    return best, bestd

def berlekamp_massey(bits):
    """BM sobre GF(2) usando enteros de Python como vectores de bits."""
    N=len(bits); C=1; B=1; L=0; m=-1; R=0
    for n in range(N):
        R=(R<<1)|int(bits[n])
        d=(C & R).bit_count() & 1
        if d:
            T=C
            C ^= (B << (n-m))
            if 2*L<=n:
                L=n+1-L; B=T; m=n
    return L, C

def nist_linear_complexity(b, M=500):
    N=len(b)//M
    K=6
    pi=[0.010417,0.03125,0.125,0.5,0.25,0.0625,0.020833]
    mu=M/2 + (9+(-1)**(M+1))/36 - (M/3 + 2/9)/(2**M)
    T=[]
    for i in range(N):
        L,_=berlekamp_massey(b[i*M:(i+1)*M])
        T.append((-1)**M * (L-mu) + 2/9)
    T=np.array(T)
    v=np.zeros(7)
    v[0]=(T<=-2.5).sum(); v[1]=((T>-2.5)&(T<=-1.5)).sum(); v[2]=((T>-1.5)&(T<=-0.5)).sum()
    v[3]=((T>-0.5)&(T<=0.5)).sum(); v[4]=((T>0.5)&(T<=1.5)).sum(); v[5]=((T>1.5)&(T<=2.5)).sum()
    v[6]=(T>2.5).sum()
    exp=N*np.array(pi)
    chi=float(((v-exp)**2/exp).sum())
    from scipy.stats import chi2
    return dict(N=N, M=M, chi2=chi, p=float(chi2.sf(chi,K)), mean_L=float(np.mean([x for x in T])), v=v.tolist(), exp=exp.tolist())

def nist_dft(b):
    n=len(b); x=2*b.astype(float)-1
    S=np.abs(np.fft.rfft(x))[1:n//2+1]
    T=sqrt(log(1/0.05)*n)
    N0=0.95*n/2; N1=float((S<T).sum())
    d=(N1-N0)/sqrt(n*0.95*0.05/4)
    return dict(T=T, N0=N0, N1=N1, d=d, p=erfc(abs(d)/sqrt(2)), S=S)

def block_entropy(b, mmax=16):
    n=len(b); out=[]
    packed=b.astype(np.int64)
    for m in range(1,mmax+1):
        w=np.zeros(n-m+1,dtype=np.int64)
        for i in range(m): w=(w<<1)|packed[i:n-m+1+i]
        cnt=np.bincount(w, minlength=1)
        cnt=cnt[cnt>0]; N=cnt.sum(); p=cnt/N
        H=float(-(p*np.log2(p)).sum())
        K=len(cnt)
        Hmm=H+(K-1)/(2*N*log(2))          # Miller-Madow
        out.append((m,H,Hmm))
    return out

def approx_entropy(b, m=10):
    def phi(mm):
        n=len(b); w=np.zeros(n,dtype=np.int64)
        bb=np.concatenate([b,b[:mm]]).astype(np.int64)
        for i in range(mm): w=(w<<1)|bb[i:n+i]
        c=np.bincount(w,minlength=2**mm)/n
        c=c[c>0]; return float((c*np.log(c)).sum())
    return phi(m)-phi(m+1)

def maurer_universal(b, L=7, Q=1280):
    n=len(b); K=n//L - Q
    if K<=0: return None
    blocks=b[:(Q+K)*L].reshape(-1,L)
    vals=np.zeros(len(blocks),dtype=np.int64)
    for i in range(L): vals=(vals<<1)|blocks[:,i].astype(np.int64)
    tab=np.zeros(2**L,dtype=np.int64)
    for i in range(Q): tab[vals[i]]=i+1
    s=0.0
    for i in range(Q,Q+K):
        v=vals[i]; s+=log2(i+1-tab[v]); tab[v]=i+1
    fn=s/K
    expected={6:5.2177052,7:6.1962507,8:7.1836656}[L]
    var={6:2.954,7:3.125,8:3.238}[L]
    c=0.7-0.8/L+(4+32/L)*(K**(-3/L))/15
    sigma=c*sqrt(var/K)
    z=(fn-expected)/sigma
    return dict(fn=fn, expected=expected, z=z, p=erfc(abs(z)/sqrt(2)), K=K, L=L)

def fwht(a):
    a=a.astype(np.float64).copy(); h=1; n=len(a)
    while h<n:
        for i in range(0,n,h*2):
            x=a[i:i+h].copy(); y=a[i+h:i+2*h].copy()
            a[i:i+h]=x+y; a[i+h:i+2*h]=x-y
        h*=2
    return a

def walsh_linear(b, k=16):
    """Correlación entre el bit siguiente y toda combinación lineal de los k bits previos."""
    n=len(b)-k
    w=np.zeros(n,dtype=np.int64)
    for i in range(k): w=(w<<1)|b[i:n+i].astype(np.int64)
    y=1-2*b[k:].astype(np.float64)   # +-1
    T=np.bincount(w, weights=y, minlength=2**k)
    W=fwht(T)/n                       # correlaciones
    z=W*sqrt(n)                       # z-scores
    return z

def autocorr(b, maxlag):
    x=2*b.astype(np.float64)-1; x-=x.mean(); n=len(x)
    f=np.fft.rfft(x, 2*n)
    ac=np.fft.irfft(f*np.conj(f))[:maxlag+1]
    return ac/ac[0]

def fisher_g(x):
    """Test exacto de Fisher para periodicidad oculta: pico del periodograma vs suma."""
    x=np.asarray(x,dtype=float); x=x-x.mean(); n=len(x)
    I=np.abs(np.fft.rfft(x))[1:]**2
    if n%2==0: I=I[:-1]
    m=len(I); g=I.max()/I.sum()
    from math import comb
    p=0.0; kmax=int(1/g)
    for k in range(1,min(kmax,60)+1):
        term=comb(m,k)*(1-k*g)**(m-1)
        p += (-1)**(k-1)*term
        if abs(term)<1e-300: break
    return dict(g=float(g), p=float(min(max(p,0.0),1.0)), m=m,
                peak_bin=int(np.argmax(I))+1, I=I)

def period_power(x, period_samples, n=None):
    """SNR del periodograma en la frecuencia de un periodo dado (con fugas +-2 bins)."""
    x=np.asarray(x,dtype=float); x=x-x.mean(); N=len(x)
    I=np.abs(np.fft.rfft(x))[1:]**2
    bin_f=N/period_samples
    lo=max(0,int(np.floor(bin_f))-3); hi=min(len(I),int(np.ceil(bin_f))+3)
    band=I[lo:hi].max()
    med=np.median(I)
    return dict(bin=bin_f, band_peak=float(band), median=float(med), snr=float(band/med))
