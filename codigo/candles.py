import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras

import urllib.request, json, time, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/125 Safari/537.36'
def get(url, tries=5):
    for a in range(tries):
        try:
            req=urllib.request.Request(url, headers={'User-Agent':UA})
            with urllib.request.urlopen(req, timeout=45) as r: return json.load(r)
        except Exception as e:
            if a==tries-1: raise
            time.sleep(1.0+1.5*a)
rows=[json.loads(l) for l in open(datos('raw.jsonl'))]
lo=min(r['ts'] for r in rows)-600; hi=max(r['ts'] for r in rows)+900
wins=[]; t=lo
while t<hi:
    e=min(t+300*300, hi); wins.append((t,e)); t=e
print("windows:", len(wins), flush=True)
def f(w):
    s,e=w
    u=("https://api.exchange.coinbase.com/products/BTC-USD/candles"
       f"?granularity=300&start={s}&end={e}")
    return get(u)
out={}
t0=time.time(); done=0
with ThreadPoolExecutor(max_workers=4) as ex:
    futs={ex.submit(f,w):w for w in wins}
    for fu in as_completed(futs):
        try:
            for c in fu.result(): out[int(c[0])]=c   # [time,low,high,open,close,volume]
        except Exception as ex2: print("fail",futs[fu],ex2, file=sys.stderr)
        done+=1
        if done%40==0: print(f"  {done}/{len(wins)} candles={len(out)} {time.time()-t0:.0f}s", flush=True)
json.dump(out, open(datos('candles.json'),'w'))
print("DONE candles:", len(out), f"{time.time()-t0:.0f}s")
