# Todo tiene su frecuencia
### Análisis espectral de Telecomunicaciones aplicado a la industria, los mercados y la criptografía

Repositorio de código del libro. **Todas las cifras del texto salen de ejecutar
esto sobre datos públicos.** El libro entero se reproduce en menos de una hora,
descargas incluidas.

```
capitulos/   el texto en Markdown
codigo/      bateria.py     nucleo comun: generadores, controles, metodos, nulas
             rodamiento.py  detector de vibracion: banda, envolvente, nula interna
             capN_*.py      un script por capitulo
datos/       resultados medidos (los datos crudos se descargan de origen)
figuras/     generadas por el codigo, nunca a mano
```

## Empezar

```bash
git clone https://github.com/CarlosCapitan/todo-tiene-su-frecuencia
cd todo-tiene-su-frecuencia
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python codigo/cap2_matriz.py       # test de instalacion
```

Si la matriz control × método sale **diagonal** —cada control enciende su método
y ningún otro— la batería funciona y todo lo demás está en pie.

## Contenido

| parte | capítulo | datos |
|---|---|---|
| **I · El instrumento** | 1 · Nada es ruido blanco | sintéticos |
| | 2 · La batería: qué ve cada transformada | sintéticos |
| | 3 · Calibrar y dudar | sintéticos |
| **II · Rodamientos**<br>*cuando hay verdad conocida* | 4 · Rodamientos: el fallo que la FFT no ve | CWRU |
| | 5 · Rodamientos: detectar y clasificar son dos problemas | CWRU |
| **III · Bitcoin en Polymarket**<br>*cuando no hay verdad conocida* | 6 · Bitcoin en Polymarket: un mercado como cifrado de flujo | Polymarket + Coinbase |
| | 7 · Bitcoin en Polymarket: cuando encuentras algo (y cuando lo matas) | Polymarket + Coinbase |
| | 8 · Bitcoin en Polymarket: más allá de Fourier, y el techo | Polymarket + Coinbase |
| **IV · La clave privada de Bitcoin**<br>*cuando el límite es un teorema* | 9 · La clave privada de Bitcoin: el oráculo en la firma | secp256k1 |
| **V · Tu turno** | 10 · La batería, ordenada | — |
| | Apéndice A · Los errores que cometí | — |
| | Apéndice B · Reproducir todo | — |
| | Apéndice C · Los instrumentos, en concepto | — |

## Algunos resultados

- Un LFSR de 32 bits pasa el test DFT del NIST, Walsh y la autocorrelación — y se
  rompe con 64 bits observados. **La planitud es relativa a la base.**
- En vibración, la elección de transformada **compró 35 dB** de sensibilidad: la
  FFT directa no detecta el fallo a ningún nivel de ruido; la envolvente sí.
- Un detector de dos etapas: **11/14 detectados, 0/4 falsos positivos, 11/11 bien
  clasificados**, y tres registros declarados *sin firma detectable* en vez de
  adivinados.
- 70.729 resoluciones de mercado tratadas como *keystream*: complejidad lineal
  **35.365 frente a n/2 = 35.364**. Un millón de máscaras de Walsh: ninguna pasa
  el umbral.
- La misma serie: el **signo** es espectralmente plano; la **magnitud** tiene
  picos de 853×. Lo que las separa no es la física, es quién cobra por cuál.
- Un hallazgo que sobrevive a **300 réplicas del procedimiento completo**
  (52,58 %, 5,9 σ) junto a otro igual de atractivo que muere fuera de muestra.
- El techo: entre el **0,04 % y el 0,27 %** de la varianza del signo es
  predeterminable. El resto no es ignorancia, es causalidad.
- Tres implementaciones independientes de búsqueda en un grupo, un solo
  exponente: **N^0,5107**, **N^0,4953**, **N^0,5055** — la cota de Shoup.

## Sobre los datos

No se redistribuyen. Cada capítulo trae su script de descarga:

| capítulos | fuente |
|---|---|
| 4, 5 | Bearing Data Center, Case Western Reserve University |
| 6, 7, 8 | Polymarket «BTC Up or Down 5m» (gamma-api + CLOB) |
| 9 | ninguno: las curvas se construyen al vuelo |

## El libro

El texto se publica de forma incremental en Leanpub. Este repositorio es su
código: todas las cifras del libro salen de ejecutarlo.

## Licencia

El **código** (`codigo/`) y los resultados derivados (`datos/`) van bajo licencia
MIT. El **texto del libro** (`capitulos/`) es propiedad del autor. Los **datos
originales** no se redistribuyen: cada capítulo trae su script de descarga y cada
fuente tiene sus propias condiciones.
