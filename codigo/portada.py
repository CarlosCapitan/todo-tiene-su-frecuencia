"""Portada del libro — generada por codigo, con los datos reales de los tres mundos.

Tres trazas, una por dominio, ninguna inventada:
  1. Vibracion de un rodamiento con defecto real (Case Western Reserve University).
  2. Bitcoin a cinco minutos, el precio que liquida el mercado de Polymarket.
  3. El espectro plano del LFSR de 32 bits del capitulo 1 — la tesis del libro.

Necesita datos ya descargados: ejecuta antes descargar_cwru.py (banda 1) y
download.py + candles.py + construir.py (banda 2).

Salida: figuras/portada.png  (2100 x 3000 px = 7 x 10 pulgadas a 300 ppp,
que es el tamano que pide Leanpub para este tamano de pagina).
"""
import os, sys, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import datos, figuras

import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from scipy.io import loadmat
import bateria as B

# --- paleta ---------------------------------------------------------------
FONDO  = "#070C11"
CIAN   = "#4FC3F7"
AMBAR  = "#F2A65A"
HUESO  = "#D5E3EC"
CLARO  = "#EAF6FF"
MUTE   = "#6E8494"
ETIQ   = "#8CA2B2"

_fam = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
TIPO = "Poppins" if "Poppins" in _fam else "DejaVu Sans"

def sin_marco(ax):
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_facecolor(FONDO)

# ==========================================================================
#  1. VIBRACION — rodamiento con defecto en pista exterior (registro 130)
# ==========================================================================
m = loadmat(datos("130.mat"))
clave = [k for k in m if k.endswith("_DE_time")][0]
vib = m[clave].ravel().astype(float)
vib = vib[20000:20000 + 8000]            # 0,67 s a 12 kHz
vib = vib / np.abs(vib).max()

# ==========================================================================
#  2. MERCADO — precio de Bitcoin en velas de 5 minutos
# ==========================================================================
d = pickle.load(open(datos("data.pkl"), "rb"))
velas = sorted(d["cd"].values(), key=lambda v: v[0])
cierre = np.array([v[4] for v in velas[-1700:]], dtype=float)   # ~6 dias
cierre = (cierre - cierre.min()) / (cierre.max() - cierre.min())

# ==========================================================================
#  3. ESPECTRO — el LFSR de 32 bits del capitulo 1
# ==========================================================================
N = 70000
x = 2 * B.lfsr(N).astype(float) - 1
I = np.abs(np.fft.rfft(x))[1:] ** 2
I = I / np.median(I)
COLS = 1500
esp = np.clip(I[np.linspace(0, len(I) - 1, COLS).astype(int)], 0, 6.0)

# ==========================================================================
#  lienzo
# ==========================================================================
fig = plt.figure(figsize=(7, 10), dpi=300)
fig.patch.set_facecolor(FONDO)

X0 = 0.085                              # margen del texto
XB, ANCHO = 0.0, 1.0                    # las trazas van a sangre
ALTO = 0.105
BANDAS = [0.535, 0.358, 0.181]          # base de cada banda

ETIQUETAS = [
    ("VIBRACIÓN",  "un rodamiento roto, 12 kHz"),
    ("MERCADO",    "Bitcoin a cinco minutos"),
    ("ESPECTRO",   "y lo que el método ve"),
]

# --- banda 1: la vibracion, linea densa e impulsiva
ax = fig.add_axes([XB, BANDAS[0], ANCHO, ALTO]); sin_marco(ax)
ax.plot(vib, color=CIAN, lw=0.35, alpha=0.9)
ax.set_xlim(0, len(vib)); ax.set_ylim(-1.05, 1.05)

# --- banda 2: el precio, linea gruesa con relleno
ax = fig.add_axes([XB, BANDAS[1], ANCHO, ALTO]); sin_marco(ax)
t = np.arange(len(cierre))
CAPAS = 26                              # degradado suave bajo la curva
for i in range(CAPAS):
    k = 0.90 * (i + 1) / CAPAS
    ax.fill_between(t, np.maximum(cierre - k, -0.20), cierre, color=AMBAR,
                    alpha=0.030 * (1 - i / CAPAS) + 0.006, lw=0)
ax.plot(t, cierre, color=AMBAR, lw=1.7, solid_capstyle='round')
ax.set_xlim(0, len(cierre) - 1); ax.set_ylim(-0.22, 1.12)

# --- banda 3: el espectro, barras verticales
ax = fig.add_axes([XB, BANDAS[2], ANCHO, ALTO]); sin_marco(ax)
segs = [[(i, 0), (i, v)] for i, v in enumerate(esp)]
t3 = (esp / 6.0) ** 0.6
cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
    "esp", ["#123246", HUESO, CLARO])
rgba = cmap(t3); rgba[:, 3] = 0.28 + 0.72 * t3
ax.add_collection(LineCollection(segs, colors=rgba, linewidths=0.62))
ax.axhline(1.0, color=AMBAR, lw=0.8, alpha=0.30)
ax.set_xlim(-0.5, COLS - 0.5); ax.set_ylim(0, 6.2)

# --- etiquetas de banda
for base, (fuerte, resto) in zip(BANDAS, ETIQUETAS):
    y = base + ALTO + 0.014
    fig.text(X0, y, fuerte, color=ETIQ, fontsize=8.5, fontfamily=TIPO,
             fontweight='bold', va='bottom', ha='left')
    fig.text(X0 + 0.135, y, resto, color=MUTE, fontsize=8.5, fontfamily=TIPO,
             va='bottom', ha='left')

# --- tipografia
fig.text(X0, 0.930, "Todo tiene", color=CLARO, fontsize=52,
         fontweight='bold', fontfamily=TIPO, va='top', ha='left')
fig.text(X0, 0.863, "su frecuencia", color=CIAN, fontsize=52,
         fontweight='bold', fontfamily=TIPO, va='top', ha='left')
fig.text(X0, 0.792, "Análisis espectral de Telecomunicaciones\n"
                    "aplicado a la industria, los mercados\n"
                    "y la criptografía",
         color=MUTE, fontsize=15.5, fontfamily=TIPO, va='top', ha='left',
         linespacing=1.5)

fig.text(X0, 0.128, "Tres mundos, una sola herramienta.\n"
                    "Y los dos casos en que la respuesta es que no hay nada.",
         color=MUTE, fontsize=12, fontfamily=TIPO, va='top', ha='left',
         linespacing=1.7)
fig.text(X0, 0.036, "CARLOS  NÚÑEZ  ZORRILLA", color=CLARO, fontsize=15,
         fontweight='bold', fontfamily=TIPO, va='bottom', ha='left')

destino = figuras("portada.png")
fig.savefig(destino, facecolor=FONDO, dpi=300)

# sin canal alfa: Leanpub y los generadores de PDF prefieren RGB plano
from PIL import Image
im = Image.open(destino)
if im.mode != "RGB":
    plano = Image.new("RGB", im.size, (7, 12, 17))
    plano.paste(im, mask=im.split()[-1])
    plano.save(destino, "PNG", optimize=True)
    im = plano
print(f"portada: {destino}  {im.size[0]}x{im.size[1]} {im.mode}")
