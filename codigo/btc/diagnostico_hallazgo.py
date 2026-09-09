"""Las condiciones 3 y 4 de la preinscripcion sobre lo que se encendio a 1h,
mas la comprobacion de si los tres tests miden lo mismo."""
import pickle, numpy as np, lib as L

s = pickle.load(open("datos/series.pkl","rb"))

def z1(b):
    b = np.asarray(b, float); x = 2*b-1; x = x - x.mean()
    r = float(np.dot(x[:-1],x[1:])/np.dot(x,x))
    return r, r*np.sqrt(len(b))

print("="*72)
print("A) ¿Son tres hallazgos o uno? — la mascara de Walsh que gana")
print("="*72)
b = s["1h"]["signo"].astype(np.int8)
z = L.walsh_linear(b, k=8)
orden = np.argsort(-np.abs(z))[:4]
for m in orden:
    bits = [i+1 for i in range(8) if (m+1) >> i & 1]   # mascaras 1..255
    print(f"   mascara {m+1:>3} (bits previos {bits})  z={z[m]:+.2f}")

print()
print("="*72)
print("B) Condicion 3: ¿aparece en las dos escalas?")
print("="*72)
for esc in ("1h","1d"):
    b = s[esc]["signo"]
    r, zz = z1(b)
    print(f"   {esc}: r(1) del signo = {r:+.5f}   z = {zz:+.2f}   n = {len(b):,}")

print()
print("="*72)
print("C) Condicion 4: ¿sobrevive al partir los cuatro anos en dos mitades?")
print("="*72)
for esc in ("1h","1d"):
    b = s[esc]["signo"]; n=len(b); h=n//2
    for etiq, tramo in (("1a mitad", b[:h]), ("2a mitad", b[h:])):
        r, zz = z1(tramo)
        print(f"   {esc} {etiq}: r(1) = {r:+.5f}   z = {zz:+.2f}   n = {len(tramo):,}")
    print()

print("="*72)
print("D) Lo mismo sobre el RETORNO continuo (no solo el signo)")
print("="*72)
for esc in ("1h","1d"):
    x = np.asarray(s[esc]["retorno"], float); x = x - x.mean()
    r = float(np.dot(x[:-1],x[1:])/np.dot(x,x))
    print(f"   {esc}: r(1) del retorno = {r:+.5f}   z = {r*np.sqrt(len(x)):+.2f}")

print()
print("="*72)
print("E) Aviso: ¿tienen sentido ApEn y Maurer a cada escala?")
print("="*72)
for esc in ("1h","1d"):
    n = len(s[esc]["signo"])
    print(f"   {esc}: n={n:,}   ApEn(m=10) necesita n >> 2^10=1.024 patrones -> "
          f"{'aceptable' if n>20000 else 'NO FIABLE'}")
