# Resultados — la batería completa sobre Bitcoin

**Preinscrito** el 9 de septiembre de 2026 (commit `0490f5e`), **ejecutado** el
mismo día. Dos desviaciones anotadas en el registro de `PREINSCRIPCION.md`,
ambas antes de ejecutarse.

## Los datos

BTC-USD de Coinbase, 9 sep 2022 → 8 sep 2026. **35.052 velas horarias**
(cobertura 99,96 %) y **1.462 diarias** (100 %). Precio de 15.633 a 126.099, hoy
en 78.767: bajista, *halving* y alcista dentro de la misma ventana.

## Veredicto en una línea

**Ningún hallazgo direccional. Dos umbrales superados, y los dos son el mismo
fenómeno conocido: el agrupamiento de volatilidad.**

---

## 1. Los 11 tests binarios sobre el signo

**Escala horaria.** Tres instrumentos se encendieron —rachas (z = +7,30),
autocorrelación (z = −10,32 en el desfase 1) y Walsh-Hadamard (2 máscaras sobre
umbral)— y resultaron ser **uno solo**: la máscara ganadora de las 255 es
literalmente «el bit anterior», y el test de rachas mide esa misma alternancia
con otro nombre.

El efecto es r(1) = −0,055: la hora siguiente tiende a moverse contra la
anterior. Es **rebote entre las puntas de la horquilla**, el efecto de
microestructura más documentado que existe, y vive dentro del coste de operar.

Y no pasa las condiciones preinscritas:

| condición | resultado |
|---|---|
| supera 2,97 σ | sí (z = −10,32) |
| aparece en ambas escalas | **no** — a escala diaria z = −1,57 |
| sobrevive a partir el periodo | **no** — de r(1) = −0,075 a −0,035 |

Que se haya reducido a la mitad en cuatro años es lo que se espera de un mercado
con horquillas cada vez más estrechas.

**Escala diaria.** Nada. Ni un test por encima de su umbral.

**Dos instrumentos declarados inaplicables**, no «negativos»:

- **Maurer** necesita más de 8.960 bits y la serie diaria tiene 1.461. Se negó
  a correr, que es lo correcto.
- **Entropía aproximada (m = 10)** devolvió 0,343 frente a ln 2 = 0,693 a escala
  diaria. Leído a la ligera parecería un hallazgo enorme. No lo es: con 1.461
  bits no se pueden estimar 1.024 patrones. Es el error D₂ = 0,00 del apéndice A
  con otro traje.

## 2. Los 9 tests continuos, con 200 surrogados IAAFT

La prueba del máximo contra el máximo, como manda la preinscripción:

| combinación | max\|z\| observado | p | |
|---|---:|---:|---|
| 1h / retorno | 159,97 | 0,000 | supera |
| 1h / magnitud | 3,16 | 0,065 | — |
| 1d / retorno | 5,74 | 0,010 | supera |
| 1d / magnitud | 3,24 | 0,075 | — |

Sobre el retorno horario se encendieron **once de trece hipótesis**, con z de
46, de 30 y de 160.

**Y eso, precisamente, es lo que hizo sospechar.** Un hallazgo real no enciende
casi toda la batería. Cuando todo se enciende, lo que suele estar mal es la
nula, no el mundo.

## 3. El control que lo resuelve

Se construyeron dos variantes de la serie horaria con la verdad conocida por
construcción:

- **signos sorteados**: se conservan las magnitudes en su orden real y se sortea
  la dirección → queda el agrupamiento, desaparece toda la información
  direccional.
- **magnitudes barajadas**: se conserva la dirección y se barajan las magnitudes
  → desaparece el agrupamiento, queda la dirección.

| | ciclo 24 h | bicoh. | tiempo-frec. | envolvente | D₂ (m=7) |
|---|---:|---:|---:|---:|---:|
| **real** | 101,80 | 2,34 | 204,55 | 1445,67 | 1,77 |
| **signos sorteados** | 101,80 | 2,05 | 218,08 | 1498,70 | 1,76 |
| **magnitudes barajadas** | 7,83 | 1,09 | 109,02 | 52,48 | 1,24 |
| *(mediana de la nula)* | *8,42* | *1,12* | *84,58* | *54,29* | *1,23* |

Sortear los signos **no cambia nada**. Barajar las magnitudes **lo derrumba
todo hasta la mediana de la nula**, cifra por cifra.

La conclusión no admite matices: **el 100 % de lo que la batería detectó es
agrupamiento de volatilidad, y contiene cero información sobre la dirección.**
La autocorrelación de |r| a un paso es +0,272 en la serie real y en la de signos
sorteados, y +0,003 al barajar las magnitudes.

A escala diaria, lo mismo: 51,93 → 49,52 al sortear signos, → 31,25 al barajar
magnitudes.

## 4. Por qué la magnitud no se encendió y el retorno sí

Parece contradictorio y no lo es. IAAFT conserva el espectro de potencia y el
histograma. Sobre la serie de **magnitud**, el agrupamiento *está* en su propio
espectro, así que los surrogados lo conservan y el efecto es invisible. Sobre la
serie de **retorno**, el espectro es casi plano y el agrupamiento vive en la
dependencia no lineal, que IAAFT destruye — y por eso salta.

Es decir: la batería funcionó exactamente como debía. Lo que había que
interpretar con cuidado era la pregunta que la nula estaba respondiendo.

## 5. Lo que este experimento enseña sobre el método

**Superar el umbral preinscrito no basta.** Aquí se superó con p = 0,000, con
una preinscripción sellada, con la nula correcta y con la corrección de
múltiples pruebas bien hecha. Y aun así el resultado no significaba lo que
parecía significar. Hizo falta una pregunta más: *¿qué es, exactamente, lo que
ha sobrevivido?*

**La rejilla no era independiente.** De los 82 contrastes, tres de los binarios
medían el mismo desfase 1 y once de los continuos medían el mismo agrupamiento.
Contar hipótesis por instrumentos sobreestima la exploración en unas direcciones
y la subestima en otras.

**Y dos instrumentos había que declararlos inaplicables**, no negativos. Un
número perfectamente calculado sobre una muestra insuficiente no es un
resultado: es un artefacto con formato de resultado.

## 6. Fallo encontrado en la librería del libro

`spec.cyclo_stat` calculaba el índice de la frecuencia cíclica objetivo usando
una única longitud —la del primer retardo—, cuando cada retardo τ produce una
serie de longitud N−τ. Con series largas no se nota; con 1.461 puntos el índice
se sale del array y el programa revienta.

**Está en el código publicado del libro.** Corregido aquí; hay que llevarlo al
repositorio y a la próxima versión.

## 7. Qué queda medido, para el registro

| pregunta preinscrita | respuesta |
|---|---|
| ¿Hay estructura direccional predecible en BTC a 1 h o 1 d? | **No.** Cero de 20 instrumentos aplicables la encuentra. |
| ¿Hay estructura no direccional? | **Sí**, y ya se sabía: agrupamiento de volatilidad, r(1) de \|r\| = +0,272. |
| ¿Y el rebote de horquilla del signo horario? | Real, pero **no cumple** dos de las cuatro condiciones y se está extinguiendo. |
| ¿Instrumentos inaplicables a esta muestra? | 2 de 20 (Maurer y ApEn a escala diaria). |

Los cuatro requisitos preinscritos para declarar un hallazgo eran: superar
2,97 σ, aparecer en las dos escalas, sobrevivir a partir el periodo en dos
mitades, y no explicarse por un efecto conocido. **Nada los cumple los cuatro.**

Que es, exactamente, el resultado que el capítulo 8 ya anticipaba sobre otra
serie financiera y otro mercado — obtenido esta vez con el instrumental
completo, sobre el activo directo y sin Polymarket de por medio.
