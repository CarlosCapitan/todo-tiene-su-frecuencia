"""Descarga velas de BTC-USD de Coinbase Exchange (API publica, sin clave).

Escalas: 1 hora (granularity=3600) y 1 dia (86400).
Periodo: el fijado en PREINSCRIPCION.md — 2022-10-01 a 2026-09-30.
La API devuelve como maximo 300 velas por peticion, asi que se pagina.
"""
import os, time, json, datetime as dt
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "Chrome/125 Safari/537.36")

AQUI   = os.path.dirname(os.path.abspath(__file__))
DATOS  = os.path.join(AQUI, "datos")
BASE   = "https://api.exchange.coinbase.com/products/BTC-USD/candles"

# Periodo corregido el 2026-09-09; ver el registro de PREINSCRIPCION.md
INICIO = dt.datetime(2022, 9,  9, tzinfo=dt.timezone.utc)
FIN    = dt.datetime(2026, 9,  9, tzinfo=dt.timezone.utc)   # exclusivo: ultima vela cerrada, la del dia 8
MAXVEL = 290          # 300 es el limite duro; 290 deja margen

def descargar(gran, nombre):
    paso = dt.timedelta(seconds=gran * MAXVEL)
    velas, t0, n = {}, INICIO, 0
    while t0 < FIN:
        t1 = min(t0 + paso, FIN)
        # epoch en segundos: evita el '+' de la ISO-8601 en la query
        url = (f"{BASE}?granularity={gran}"
               f"&start={int(t0.timestamp())}&end={int(t1.timestamp())}")
        for intento in range(5):
            try:
                pet = urllib.request.Request(url, headers={"User-Agent": UA})
                with urllib.request.urlopen(pet, timeout=45) as r:
                    lote = json.loads(r.read().decode())
                break
            except Exception as e:
                if intento == 4:
                    raise
                time.sleep(1.5 * (intento + 1))
        # cada vela: [time, low, high, open, close, volume]
        for v in lote:
            velas[int(v[0])] = v
        n += 1
        if n % 20 == 0:
            print(f"  {nombre}: {len(velas):>6} velas  ({t1.date()})", flush=True)
        t0 = t1
        time.sleep(0.30)          # cortesia con el endpoint publico
    orden = [velas[k] for k in sorted(velas)]
    destino = os.path.join(DATOS, nombre)
    with open(destino, "w") as f:
        json.dump(orden, f)
    ini = dt.datetime.fromtimestamp(orden[0][0], dt.timezone.utc)
    fin = dt.datetime.fromtimestamp(orden[-1][0], dt.timezone.utc)
    print(f"{nombre}: {len(orden)} velas  {ini:%Y-%m-%d %H:%M} -> {fin:%Y-%m-%d %H:%M}")
    return orden

if __name__ == "__main__":
    os.makedirs(DATOS, exist_ok=True)
    descargar(3600,  "btc_1h.json")
    descargar(86400, "btc_1d.json")
