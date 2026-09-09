# Preinscripción — la batería completa sobre Bitcoin

**Escrito antes de descargar ningún dato.** Este documento fija qué se va a
medir, con qué parámetros y contra qué umbral. Se sella con un commit fechado.
Cualquier desviación posterior se anota aquí abajo, en el registro de cambios,
con su motivo. Sin eso, esto sería una pesca.

> La pregunta no es «¿hay señal en Bitcoin?». Es: **¿el negativo del capítulo 8
> aguanta a otras escalas y sobre el activo entero, en vez de sobre un mercado
> de apuestas a cinco minutos?**

---

## 1. Los datos

| | |
|---|---|
| Activo | BTC-USD |
| Fuente | Coinbase Exchange, API pública de velas (el mismo `candles.py` del libro) |
| Periodo | **4 años**: del 1 de octubre de 2022 al 30 de septiembre de 2026 |
| Escalas | **1 hora** (~35.000 velas) y **1 día** (~1.460 velas) |

Cuatro años porque cubren un mercado bajista, un *halving* y un mercado alcista.
Si el resultado dependiera de acortar la ventana, eso sería el hallazgo.

## 2. Las tres series

Bitcoin no es una serie. Del precio de cierre *p(t)* se derivan tres, y el
libro ya demostró en el capítulo 6 que **no se comportan igual**:

| serie | definición | tipo |
|---|---|---|
| **signo** | `s(t) = 1 si log(p_t/p_{t-1}) > 0, si no 0` | binaria |
| **retorno** | `r(t) = log(p_t/p_{t-1})` | continua |
| **magnitud** | `m(t) = log(|r(t)| + ε)` | continua |

El precio en bruto **no se analiza**. No es estacionario: la autocorrelación
saldría ≈1, el espectro una rampa 1/f y la dimensión de correlación un número
perfectamente calculado y sin significado. Eso no serían hallazgos, serían
artefactos de la tendencia.

## 3. Qué instrumentos aplican, y cuáles no

De los 35 del apéndice C, **no aplican 8**, y decir por qué es parte del
resultado:

| instrumento | por qué no |
|---|---|
| BPFO, BPFI, BSF, FTF | frecuencias de la geometría de un rodamiento |
| bandas laterales | íd. |
| ECDLP, secp256k1, Pollard rho, BSGS, cota de Shoup | criptografía de curva elíptica |
| LFSR | es un objeto de estudio, no un test |

Otros **7 no son tests sino protocolo**: los cinco generadores de nula, el
umbral √(2·ln N) y el walk-forward. Se usan, no se puntúan.

Quedan **20 tests**, repartidos así:

**Sobre la serie binaria del signo** (11): monobit · rachas · racha máxima ·
DFT del NIST · autocorrelación binaria · Maurer · entropía aproximada ·
complejidad lineal del NIST · Berlekamp-Massey · perfil de complejidad lineal ·
Walsh-Hadamard.

**Sobre retorno y magnitud** (9): autocorrelación · cicloestacionariedad ·
bicoherencia · plano tiempo-frecuencia (Morlet) · kurtosis espectral ·
espectro de la envolvente · falsos vecinos · dimensión de correlación ·
exponente de Lyapunov.

## 4. La rejilla de parámetros, contada

Aquí es donde se decide si esto es ciencia o pesca. **N no son 20.**

| bloque | combinaciones | subtotal |
|---|---|---|
| 11 tests binarios × 2 escalas | 11 × 2 | 22 |
| Walsh: k ∈ {8, 12, 16} (ya incluido arriba como 1) → añade | 2 × 2 escalas | 4 |
| 9 tests continuos × 2 series × 2 escalas | 9 × 4 | 36 |
| cicloestacionariedad: 3 frecuencias cíclicas candidatas por escala | +2 × 4 | 8 |
| bicoherencia: nfft ∈ {256, 512} | +1 × 4 | 4 |
| dimensión de correlación: m ∈ {5, 6, 7} | +2 × 4 | 8 |
| **N total** | | **82** |

**Umbral honesto: √(2·ln 82) = 2,97 σ.**

Conviene subrayarlo: para esta rejilla el umbral cae justo por debajo de los
tres sigmas de costumbre. No porque tres tenga nada de mágico, sino porque
alrededor de un centenar de hipótesis es lo que hace falta para que tres sigmas
sea aproximadamente el número correcto. Con 500 haría falta 3,53; con 5.000,
4,13. Ese es todo el contenido de la regla.

Las frecuencias cíclicas candidatas se fijan **ahora**, por calendario y no por
lo que se vea: escala horaria → 24 h, 168 h (semana), 720 h (mes); escala
diaria → 7, 30, 365 días.

## 5. La nula

Para cada test continuo, el modelo nulo es **IAAFT** (conserva espectro de
potencia e histograma) con 200 surrogados. Para las preguntas de alineación
entre series, desplazamiento circular. Para la serie binaria, la nula es la
propia distribución del estadístico bajo independencia, salvo en Walsh, donde
se usa el umbral multi-test.

**Y la nula pasa por la rejilla entera.** Si el barrido real prueba 82
combinaciones, cada surrogado prueba las 82 y se compara el máximo contra el
máximo. No una configuración contra una configuración.

## 6. Qué se declara hallazgo

Un test cuenta como positivo si, y solo si:

1. supera 2,97 σ contra su nula, **y**
2. sobrevive al máximo de la nula sobre la rejilla completa, **y**
3. aparece en las dos escalas o se explica por qué no, **y**
4. sigue ahí al partir los cuatro años en dos mitades.

Cualquier cosa que cumpla 1 y falle 2 es, por definición, el máximo de 82
normales.

## 7. El resultado esperado

**Nada.** Bitcoin es probablemente la serie temporal más analizada de la
historia; miles de personas con más datos, más cómputo y más incentivo han
pasado estas herramientas por ella. La probabilidad a priori de encontrar algo
explotable en velas horarias o diarias es muy baja.

Eso no invalida el experimento: lo que se entrega es **el techo medido y la
tabla de qué vio cada instrumento**, que es un resultado publicable y es la
réplica a otra escala del capítulo 8. Si además sale algo, tendrá que pasar
las cuatro condiciones de arriba antes de llamarse hallazgo.

---

## Registro de cambios

*(Cualquier desviación de lo anterior se anota aquí, con fecha y motivo, antes
de ejecutarla.)*

### 2026-09-09 · Corrección del periodo

**Qué.** El periodo preinscrito era «1 de octubre de 2022 → 30 de septiembre de
2026». Pasa a ser **9 de septiembre de 2022 → 8 de septiembre de 2026**.

**Por qué.** Error de redacción: la fecha final era futura. Hoy es 9 de
septiembre de 2026, así que la última vela diaria cerrada es la del día 8.
La API de Coinbase devolvía 400 al pedir el tramo futuro.

**Qué se conserva.** La duración exacta: cuatro años. Se desplaza la ventana
hacia atrás en vez de acortarla, para no perder poder estadístico ni cambiar
el número de observaciones respecto a lo previsto. Sigue cubriendo mercado
bajista, *halving* y alcista.

**Qué no cambia.** Ni las series, ni las escalas, ni la rejilla, ni N = 82, ni
el umbral de 2,97 σ, ni las cuatro condiciones para declarar hallazgo. Esta
corrección se anota antes de ejecutar la descarga definitiva.

### 2026-09-09 · Desfases de la autocorrelación cíclica a escala diaria

**Qué.** Los desfases (τ) de la autocorrelación cíclica pasan a ser
`(0,1,2,3,4,6,7,14,30,60,90)` en la escala diaria, en lugar de los de la
librería `(0,1,2,3,4,6,12,24,48,96,144,288)`.

**Por qué.** Los de la librería están pensados para velas de cinco minutos,
donde 288 es exactamente un día. Sobre 1.461 velas diarias, un desfase de 288
son diez meses: no tiene sentido y además deja tramos demasiado cortos. Los
nuevos son el calendario equivalente a escala diaria: días sueltos, semana,
quincena, mes, bimestre y trimestre. La escala horaria **no se toca**.

**Fallo de librería encontrado de paso.** `spec.cyclo_stat` calculaba el índice
de la frecuencia objetivo con una única longitud, la del primer τ, cuando cada
τ produce una serie de longitud distinta (N−τ). Con series largas nunca se
notaba; con 1.461 puntos el índice se salía del array y reventaba. Corregido
para usar la longitud y el N efectivo de cada τ. **Este fallo está en el
código publicado del libro** y debe arreglarse también allí.

**Qué no cambia.** Ni las series, ni las escalas, ni N = 82, ni el umbral, ni
las cuatro condiciones. Los resultados de la escala horaria ya calculados
(200 surrogados) no se recalculan: no les afecta.
