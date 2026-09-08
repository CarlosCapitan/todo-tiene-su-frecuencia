import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras

import urllib.request, json, time, datetime, os, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
UA='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/125 Safari/537.36'
def get(url, tries=4):
    for a in range(tries):
        try:
            req=urllib.request.Request(url, headers={'User-Agent':UA,'Accept':'application/json'})
            with urllib.request.urlopen(req, timeout=60) as r: return json.load(r)
        except Exception as e:
            if a==tries-1: raise
            time.sleep(1.2*(a+1))
START=1766016000                      # 2025-12-18
END=(int(time.time())//300)*300
ALL=list(range(START,END,300))
print(f"slots={len(ALL)}  {datetime.datetime.utcfromtimestamp(START)} -> {datetime.datetime.utcfromtimestamp(END)}", flush=True)
CH=[ALL[i:i+100] for i in range(0,len(ALL),100)]
def fetch(chunk):
    q="&".join(f"slug=btc-updown-5m-{t}" for t in chunk)
    d=get(f"https://gamma-api.polymarket.com/events?{q}&limit=200")
    out=[]
    for e in d:
        try: ts=int(e['slug'].rsplit('-',1)[1])
        except: continue
        for m in e.get('markets',[]):
            try: op=json.loads(m.get('outcomePrices') or '[]')
            except: op=[]
            try: oc=json.loads(m.get('outcomes') or '[]')
            except: oc=[]
            out.append(dict(ts=ts, slug=e['slug'], outcomes=oc, prices=op,
                            closed=bool(m.get('closed')), uma=m.get('umaResolutionStatus'),
                            vol=m.get('volumeNum'), ev_vol=e.get('volume'),
                            oi=e.get('openInterest'), created=e.get('createdAt')))
            break
    return out
rows=[]; done=0; t0=time.time()
with ThreadPoolExecutor(max_workers=12) as ex:
    futs={ex.submit(fetch,c):c for c in CH}
    for f in as_completed(futs):
        try: rows.extend(f.result())
        except Exception as e: print("chunkfail", e, file=sys.stderr)
        done+=1
        if done%80==0: print(f"  {done}/{len(CH)} chunks  rows={len(rows)}  {time.time()-t0:.0f}s", flush=True)
rows.sort(key=lambda r:r['ts'])
with open(datos('raw.jsonl'),'w') as fh:
    for r in rows: fh.write(json.dumps(r)+"\n")
print(f"DONE rows={len(rows)} elapsed={time.time()-t0:.0f}s")
