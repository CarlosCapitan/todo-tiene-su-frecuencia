"""Compara lo observado con la nula IAAFT, hipotesis por hipotesis y
—lo que manda la preinscripcion— maximo contra maximo sobre la rejilla."""
import json, numpy as np
d = json.load(open("datos/resultados_continuos.json"))
UMBRAL = np.sqrt(2*np.log(82))

print("="*86)
print(f"{'combinacion':<16}{'hipotesis':<16}{'observado':>11}{'nula p50':>10}{'nula p99':>10}{'z':>8}  veredicto")
print("="*86)
resumen=[]
for clave, r in d.items():
    for h, obs in r["obs"].items():
        nul = np.array([v for v in r["nula"][h] if v==v], float)
        if len(nul) < 50 or not np.isfinite(obs): 
            print(f"{clave:<16}{h:<16}{obs:>11.3f}{'--':>10}{'--':>10}{'--':>8}  sin nula"); continue
        mu, sd = nul.mean(), nul.std()
        z = (obs-mu)/sd if sd>0 else np.nan
        p99 = np.quantile(nul, .99)
        v = "SUPERA" if abs(z) > UMBRAL else "-"
        resumen.append((clave,h,obs,float(z),v))
        print(f"{clave:<16}{h:<16}{obs:>11.3f}{np.median(nul):>10.3f}{p99:>10.3f}{z:>8.2f}  {v}")
    print("-"*86)

print("\n" + "="*86)
print("PRUEBA DEL MAXIMO: el observado mas extremo contra el maximo de cada surrogado")
print("="*86)
for clave, r in d.items():
    zs_obs=[]; zs_nul=None
    claves=[h for h in r["obs"] if np.isfinite(r["obs"][h])]
    M=[]
    for h in claves:
        nul=np.array([v for v in r["nula"][h] if v==v],float)
        if len(nul)<50: continue
        mu,sd=nul.mean(),nul.std()
        if sd<=0: continue
        zs_obs.append(abs((r["obs"][h]-mu)/sd))
        M.append((nul-mu)/sd)
    if not M: continue
    M=np.abs(np.array(M))            # hipotesis x surrogados
    maxnul=M.max(axis=0)             # maximo de la rejilla por surrogado
    mo=max(zs_obs)
    p=float((maxnul>=mo).mean())
    print(f"  {clave:<14} max|z| observado = {mo:5.2f}   "
          f"max|z| nula: p50={np.median(maxnul):.2f} p95={np.quantile(maxnul,.95):.2f}   "
          f"p = {p:.3f}   {'HALLAZGO' if p<0.05 else 'nada'}")
