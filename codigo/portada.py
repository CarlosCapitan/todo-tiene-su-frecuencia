"""Portada del libro — generada por codigo, con datos reales.

La imagen es el periodograma crudo del LFSR de 32 bits del capitulo 1:
un espectro perfectamente plano producido por una secuencia perfectamente
determinista. La portada es la tesis del libro.

Salida: figuras/portada.png  (2100 x 3000 px = 7 x 10 pulgadas a 300 ppp,
que es el tamano que pide Leanpub para este tamano de pagina).
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rutas import figuras

import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import bateria as B

# --- paleta ---------------------------------------------------------------
FONDO = "#070C11"
CIAN  = "#4FC3F7"
CLARO = "#EAF6FF"
MUTE  = "#7E93A3"
ACENTO= "#F2A65A"

TITULO = "Poppins" if "Poppins" in {f.name for f in
          matplotlib.font_manager.fontManager.ttflist} else "DejaVu Sans"
TEXTO  = TITULO

# --- los datos ------------------------------------------------------------
N = 70000
bits = B.lfsr(N)
x = 2 * bits.astype(float) - 1
I = np.abs(np.fft.rfft(x))[1:] ** 2
I = I / np.median(I)

COLS = 1500
idx = np.linspace(0, len(I) - 1, COLS).astype(int)
v = I[idx]
TOPE = 6.5
v = np.clip(v, 0, TOPE)

# --- lienzo ---------------------------------------------------------------
fig = plt.figure(figsize=(7, 10), dpi=300)
fig.patch.set_facecolor(FONDO)

ax = fig.add_axes([0.0, 0.150, 1.0, 0.475])
ax.set_facecolor(FONDO)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_xticks([]); ax.set_yticks([])
ax.set_xlim(-0.5, COLS - 0.5); ax.set_ylim(0, TOPE * 1.02)

# barras verticales coloreadas por altura: cian abajo, casi blanco arriba
segs = [[(i, 0), (i, vi)] for i, vi in enumerate(v)]
t = (v / TOPE) ** 0.6
cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
    "esp", ["#0E2E42", CIAN, CLARO])
rgba = cmap(t)
rgba[:, 3] = 0.42 + 0.58 * t          # las columnas bajas pesan menos
lc = LineCollection(segs, colors=rgba, linewidths=0.75)
ax.add_collection(lc)

# la mediana: la linea que dice "aqui no sobresale nada"
ax.axhline(1.0, color=ACENTO, lw=1.1, alpha=0.85, zorder=5)

# --- tipografia -----------------------------------------------------------
fig.text(0.085, 0.905, "Todo tiene", color=CLARO, fontsize=52,
         fontweight='bold', fontfamily=TITULO, va='top', ha='left')
fig.text(0.085, 0.838, "su frecuencia", color=CIAN, fontsize=52,
         fontweight='bold', fontfamily=TITULO, va='top', ha='left')

fig.text(0.085, 0.767, "Análisis espectral de Telecomunicaciones\n"
                       "aplicado a la industria, los mercados\n"
                       "y la criptografía",
         color=MUTE, fontsize=15.5, fontfamily=TEXTO, va='top', ha='left',
         linespacing=1.5)

fig.text(0.085, 0.132, "Espectro de un registro de 32 bits.\n"
                       "Perfectamente plano. Perfectamente predecible.",
         color=MUTE, fontsize=12.5, fontfamily=TEXTO, va='top', ha='left',
         linespacing=1.7)

fig.text(0.085, 0.036, "CARLOS  NÚÑEZ  ZORRILLA", color=CLARO, fontsize=15,
         fontweight='bold', fontfamily=TITULO, va='bottom', ha='left')

destino = figuras("portada.png")
fig.savefig(destino, facecolor=FONDO, dpi=300)
print("portada:", destino)
im = plt.imread(destino)
print("pixeles:", im.shape[1], "x", im.shape[0])
