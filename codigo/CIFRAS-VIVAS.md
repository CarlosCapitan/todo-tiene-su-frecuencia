# Inventario de cifras vivas

> No exhaustivo al 100 % (no lo pide U2a). Cubre n, r(1), aciertos,
> coincidencia y tramos de los capítulos 6-9, que son los que dependen de
> descargas de Polymarket (`gamma-api.polymarket.com`) y Coinbase
> (`api.exchange.coinbase.com`) — las dos series siguen creciendo mientras
> el libro se lee. Construido a partir de los bloques «Código del capítulo»
> de los caps. 6, 7 y 8, y de `codigo/btc/` para el 9 (el 9 no tiene bloque
> de reproducción propio en el capítulo; su pipeline está en el apéndice B).

| cap/apartado | cifra | script | fichero de datos |
|---|---|---|---|
| 6.1 (intro) | n = 70.729 resoluciones reales | `download.py` → `candles.py` → `construir.py` → `cap6_bateria.py` | `datos/data.pkl` |
| 6.3 | Berlekamp-Massey, complejidad lineal L = 35.365 | `cap6_bateria.py` | (stdout) |
| 6.3 | r(1) del signo = −0,0153, z = −4,06; ocho tramos de −0,0410 a +0,0103 | `cap6_bateria.py` | (stdout) |
| 6.4 | tabla Fisher g (p-valor), SNR 24 h / 7 d, r(1) — signo/magnitud/volumen | `cap6_bateria.py` | (stdout) |
| 6.5 | tabla de control: pico diario/semanal y estadístico g de Fisher (signo, magnitud binarizada, magnitud log, volumen); amplitud por hora (máx \|z\| 2,33 y 16,55) | `cap06_control_binario.py` | `datos/cap06_control.npz` |
| 7.1–7.2 | 71 variables sin fuga temporal | `features.py` | `datos/feat.npz` |
| 7.3 | disparos = 11.203, acierto = 52,58 %, nula walk-forward (300 réplicas), p = 1/301 | `wf_rule.py` | `datos/wf_rule.npz` (≈ `datos/polymarket_walkforward.npz`) + `datos/polymarket_walkforward_bloques.csv`, `datos/polymarket_walkforward_nula.csv` |
| 7.4 | modelo walk-forward completo, acierto y z | `walkfwd.py` | `datos/wf.npz` |
| 8.2–8.3 | «las mismas N ventanas» (51.626 en la pasada de corte); ciclo@288, ciclo@2016, bicoherencia, tiempo-frecuencia (signo, residuo, magnitud) + 80 surrogados IAAFT | `resid.py`, `cap8_fase3.py` | `datos/series.npz`, `datos/polymarket_fase3.csv`, `datos/polymarket_surrogados_iaaft.csv` |
| 8.5 | tabla de R² por fuente (bit anterior, walk-forward completo, regla del cap. 7, CLV) | `cap08_techo_libro.py` (secciones E y F) + `datos/polymarket_varianza.csv` (fila del CLV no está en ese CSV — ver nota) | `datos/polymarket_varianza.csv` (parcial), `datos/polymarket_walkforward.npz` |
| 8.6 | CLV: n ventanas, acierto 51,99 %, R² 0,159 %, coincidencia bit/vela 95,6 %, R² atenuado al bit ≈0,13 % | `cap08_techo_libro.py` (secciones A-D, G) | `datos/data.pkl` |
| 9.3 | once tests binarios sobre el signo | `codigo/btc/tests_binarios.py` | `codigo/btc/datos/resultados_binarios.json` |
| 9.4 | nueve tests continuos × 4 combinaciones × 200 surrogados IAAFT | `codigo/btc/tests_continuos.py` | `codigo/btc/datos/resultados_continuos.json` |
| 9.5 | control de signos sorteados | `codigo/btc/control_signos.py` | (stdout) |
| 9.6–9.7 | diagnóstico de qué miden los tres tests que se encienden, máscara de Walsh ganadora | `codigo/btc/diagnostico_hallazgo.py` | (stdout) |
| 9.8 | n, r(1) bits Polymarket y signo BTC 5 min, coincidencia bit/signo, correlación entre 8 tramos | `codigo/btc/mismo_fenomeno.py` | `datos/data.pkl`, `codigo/btc/datos/btc_1h.json` |
| 9.9 | tabla del veredicto final | `codigo/btc/veredicto.py` | (stdout) |

**Nota sobre `datos/polymarket_varianza.csv`.** No se ha encontrado en ningún
repo el script que lo genera (ver NOTAS-LECTURA.md, Ronda 2, T2/CLV). Las
tres filas originales (bit anterior, walk-forward completo, regla del
capítulo 7) están ahí escritas a mano o por un script perdido; la fila del
CLV que añadió la Ronda 3 (U1b) no está en ese CSV, solo en el capítulo y en
la salida de `cap08_techo_libro.py`. Si `codigo/CIFRAS-VIVAS.md` se usa para
una regeneración futura, esa fila necesita su propio paso.
