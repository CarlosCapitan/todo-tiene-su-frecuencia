# Todo tiene su frecuencia — código

Código del libro **«Todo tiene su frecuencia. Análisis espectral de
Telecomunicaciones aplicado a la industria, los mercados y la criptografía»**,
de Carlos Núñez Zorrilla.

**Todas las cifras del libro salen de ejecutar esto sobre datos públicos.**
Ninguna está estimada. El conjunto se reproduce en menos de una hora, descargas
incluidas — y esa afirmación está comprobada desde un clon limpio.

```
codigo/    bateria.py     nucleo comun: generadores, controles, metodos, nulas
           rodamiento.py  deteccion de fallo por envolvente y nula interna
           rutas.py       rutas del repositorio
           capN_*.py      un script por capitulo
datos/     resultados medidos (los datos crudos se descargan de origen)
figuras/   generadas por el codigo, nunca a mano
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

## Qué hay aquí

Una biblioteca de análisis espectral escrita desde cero en menos de mil líneas,
sin marcos de aprendizaje automático ni dependencias de procesado de señal:
batería NIST, Berlekamp-Massey, Walsh-Hadamard, correlación espectral cíclica,
bicoherencia, escalograma de Morlet, kit de caos, surrogados IAAFT y
desplazamiento circular, kurtograma con selección de banda, y evaluación
walk-forward.

Más los guiones que reproducen cada resultado del libro.

## Algunos de esos resultados

- Un LFSR de 32 bits pasa el test DFT del NIST, Walsh y la autocorrelación — y se
  rompe con 64 bits observados. La planitud es relativa a la base.
- En vibración, la elección de transformada **compró 35 dB**: la FFT directa no
  detecta el fallo a ningún nivel de ruido; la envolvente sí.
- Detector de dos etapas: **11/14 detectados, 0/4 falsos positivos, 11/11 bien
  clasificados**, y tres registros declarados *sin firma detectable*.
- 70.729 resoluciones de mercado como *keystream*: complejidad lineal **35.365
  frente a n/2 = 35.364**. Un millón de máscaras de Walsh, ninguna sobre el umbral.
- Un hallazgo que sobrevive a **300 réplicas del procedimiento completo**
  (52,58 %, 5,9 σ) junto a otro igual de atractivo que muere fuera de muestra.
- Tres implementaciones independientes de búsqueda en un grupo, un solo
  exponente: **N^0,5107**, **N^0,4953**, **N^0,5055** — la cota de Shoup.

## Sobre los datos

No se redistribuyen. Cada capítulo trae su script de descarga:

| capítulos | fuente |
|---|---|
| 4, 5 | Bearing Data Center, Case Western Reserve University |
| 6, 7, 8 | Polymarket «BTC Up or Down 5m» + velas de Coinbase |
| 9, 10 | ninguno: las señales se construyen al vuelo |

## El libro

Se publica de forma incremental en Leanpub. Este repositorio es su código.

## Licencia

MIT para el código y los resultados derivados. El texto del libro no está en este
repositorio y sus derechos se reserva el autor. Los datos originales tienen las
condiciones de cada fuente.
