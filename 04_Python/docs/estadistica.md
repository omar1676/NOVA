# Estadística (fase 4)

`estadistica.py` calcula:
- estadísticos descriptivos de tres variables;
- tres hipótesis de negocio;
- un intervalo de confianza bootstrap del ticket medio.

Las mismas funciones se aplican a los datos de PRUEBA (`--modo real`) y a los
SINTÉTICOS (`--modo sintetico`). Los resultados quedan en
`estadisticos_descriptivos.csv`, `hipotesis.csv` y `bootstrap_ticket_medio.csv`
de cada carpeta de `outputs/`.

**Ninguno de estos resultados es una conclusión sobre los clientes reales de
NOVA.**
- **Datos sintéticos:** los ha inventado `generador_datos.py`. Si con ellos una
  hipótesis «se confirma», solo se comprueba que el método funciona y que el
  generador hace lo que se le pidió.
- **Datos de prueba:** son 12 pedidos de un solo día.

## Estadísticos descriptivos

Se calculan con pandas (`mean`, `median`, `std`, `mode`) y NumPy (`percentile`)
sobre los pedidos no cancelados:
- importe por pedido;
- pares por pedido;
- precio unitario por línea.

Cada uno se calcula para todos los pedidos y por tipo. La moda solo se da en
variables con pocos valores distintos: en un importe casi nunca se repite el
mismo valor.

**Qué estadístico representa mejor:** si la media se separa más de un 20 % de la
mediana, unos pocos valores extremos la arrastran y se recomienda la mediana.

### Datos sintéticos

| Variable | Grupo | n | Media | Mediana | Moda | Desv. típica | P25 | P75 | Mejor resumen |
|---|---|---|---|---|---|---|---|---|---|
| importe por pedido (€) | todos | 830 | 1.013,45 | 259,98 | — | 2.004,41 | 139,98 | 419,00 | **mediana** |
| importe por pedido (€) | normal | 700 | 247,43 | 228,56 | — | 139,29 | 129,99 | 329,97 | media |
| importe por pedido (€) | custom | 130 | 5.138,19 | 4.864,72 | — | 2.320,43 | 3.279,62 | 7.019,55 | media |
| pares por pedido | todos | 830 | 8,43 | 3 | 2 | 15,54 | 2 | 4 | **mediana** |
| pares por pedido | normal | 700 | 2,42 | 2 | 2 | 1,28 | 1 | 3 | **mediana** |
| pares por pedido | custom | 130 | 40,82 | 40 | 24 | 17,04 | 25,25 | 54 | media |
| precio unitario (€/par) | todos | 1.637 | 108,63 | 114,28 | 129,99 | 26,58 | 83,99 | 129,99 | media |
| precio unitario (€/par) | normal | 1.201 | 102,18 | 99,99 | 129,99 | 23,66 | 79,99 | 123,80 | media |
| precio unitario (€/par) | custom | 436 | 126,41 | 137,13 | 148,56 | 26,09 | 102,85 | 148,56 | media |

El archivo trae también el mínimo, el máximo, los percentiles 10 y 90, el rango
intercuartílico y el coeficiente de variación.

**Qué significa para NOVA (en la simulación):**
- **La media del importe engaña si se mezclan los dos tipos.** Un pedido «medio»
  sería de 1.013 €, pero la mitad de los pedidos no pasa de 260 €. Los 130
  pedidos Custom, de unos 5.000 € cada uno, arrastran la media un 290 % por
  encima de la mediana. Para hablar del pedido típico hay que usar la mediana o,
  mejor, separar normal y Custom: dentro de cada tipo, media y mediana se parecen.
- **Pares por pedido:** lo más frecuente es 2 pares (la moda). La media de los
  normales (2,42) ya se separa un 21 % de la mediana, porque los pedidos de 3
  pares la suben.
- **El precio unitario sí se resume bien con la media.** Los precios están
  acotados (de 66,66 a 155,99 € por par, contando la subida del 5 % y el recargo
  Custom) y no hay valores extremos.

### Datos de prueba

| Variable | Grupo | n | Media | Mediana | Mejor resumen |
|---|---|---|---|---|---|
| importe por pedido (€) | todos | 12 | 890,54 | 117,40 | mediana |
| pares por pedido | todos | 12 | 7,5 | 1 | mediana |
| precio unitario (€/par) | todos | 18 | 114,09 | 119,90 | media |

Pasa lo mismo, y más exagerado: dos pedidos de 40 pares (`NOVA-0011` y
`CUSTOM-40`) hacen que la media de pares por pedido sea 7,5, cuando 10 de los 12
pedidos son de 1 par. Con 12 pedidos de un día, estas cifras no describen ningún
comportamiento estable.

## Las tres hipótesis

Se escribieron **antes de calcular ningún resultado** (están así en la cabecera de
`estadistica.py`) y no se han cambiado después de verlos.

| | H1 | H2 | H3 |
|---|---|---|---|
| **Hipótesis** | Los pedidos Custom dejan más importe por pedido que los estándar | Las tallas 41, 42 y 43 reúnen más de la mitad de los pares | La demanda crece: los últimos 6 meses tienen más pares al mes que los 6 anteriores |
| **Pregunta de negocio** | ¿Un pedido personalizado deja más dinero? | ¿Conviene concentrar la fabricación en las tallas centrales? | ¿Hay que prever más producción? |
| **Variable** | importe por pedido (€), no cancelados | % de pares de demanda en las tallas 41 a 43 | pares de demanda por mes |
| **Método** | diferencia de medianas (Custom − estándar) | proporción de pares, frente al 50 % | diferencia de medias mensuales |
| **Intervalo** | bootstrap 95 %, remuestreando pedidos de cada tipo | bootstrap 95 %, remuestreando líneas | bootstrap 95 %, remuestreando meses de cada periodo |
| **Sintéticos: n** | 130 Custom y 700 estándar | 1.637 líneas | 6 meses (2026-05 a 2026-10) frente a 6 (2025-11 a 2026-04) |
| **Sintéticos: resultado** | +4.636,16 € (IC 95 %: 4.099,57 a 4.948,98) → **los datos la apoyan** | 53,2 % (IC 95 %: 49,46 a 57,11) → **evidencia insuficiente**: incluye el 50 % | −50,2 pares/mes (IC 95 %: −187,51 a +99,17) → **evidencia insuficiente**: incluye el 0 |
| **Prueba: resultado** | +20,09 € (IC 95 %: 5,00 a 4.716,01) → «la apoyan», pero con 5 y 7 pedidos el resultado es muy provisional | 74,4 % (IC 95 %: 45,68 a 97,53) → evidencia insuficiente | no se puede contrastar: hay 1 mes y hacen falta 12 |

**Cómo se decide:**
- si todo el intervalo queda por encima de la referencia (0 o 50 %), los datos apoyan la hipótesis;
- si queda todo por debajo, la contradicen;
- si la referencia cae dentro del intervalo, no se puede decir: **evidencia insuficiente**.

**Interpretación:**
- **H1.** Con los datos sintéticos se confirma, pero es lo esperable: el generador
  da a los Custom más pares y un 20 % más de precio. Solo demuestra que el
  método detecta una diferencia que existe. Se usa la mediana porque los importes
  están muy sesgados.
- **H2.** La proporción (53 %) queda tan cerca del 50 % que el intervalo lo
  incluye. Las tallas centrales son las más pedidas, pero no se puede afirmar que
  pasen de la mitad.
- **H3.** El generador **sí tiene** un crecimiento del 2 % al mes, y aun así los
  datos no lo demuestran. Hay solo 6 meses por grupo, los meses tienen distinta
  estacionalidad y unos pocos pedidos Custom de muchos pares hacen saltar la cifra
  de cada mes. Es un buen ejemplo de que **no ver una diferencia no demuestra que
  no exista**.

**Sobre lo que pide la rúbrica.** Pide que al menos dos hipótesis se contrasten y
admite que una termine en evidencia insuficiente. Las tres se han contrastado con
datos, pero dos han terminado sin concluir. No se han cambiado después de ver los
resultados para que salieran concluyentes, porque eso invalidaría el contraste.
Si el equipo quiere otra hipótesis, tiene que escribirla antes de calcularla.

## Bootstrap del ticket medio

- **Métrica:** el ticket medio, es decir, el importe medio de los pedidos de venta
  (confirmados en adelante).
- **Método:**
  1. Se sacan **2.000** muestras nuevas del mismo tamaño, **con reemplazo**, con
     la semilla **2026**.
  2. Se calcula la media de cada una.
  3. El intervalo al 95 % va del percentil 2,5 al 97,5 de esas 2.000 medias.

  Con la misma semilla sale siempre el mismo intervalo, y lo comprueba una prueba.

| Datos | n | Estimación | Límite inferior | Límite superior |
|---|---|---|---|---|
| sintéticos | 822 pedidos | 1.011,41 € | 878,59 € | 1.153,02 € |
| prueba | 1 pedido | 4.796,00 € | NO CALCULABLE | NO CALCULABLE |

**Interpretación (sintéticos):** con estos 822 pedidos, el ticket medio está entre
879 y 1.153 € con un 95 % de confianza. Es un intervalo ancho para tantos pedidos,
porque los Custom (unos 5.000 €) mezclados con los normales (unos 250 €) dan mucha
variación. Describe la simulación, **no a NOVA**. Con los datos de prueba solo hay
un pedido confirmado y no se puede estimar ningún intervalo.

## Supuestos, sesgos y limitaciones

- **Independencia.** El bootstrap supone que los valores son independientes. Las
  líneas de un mismo pedido Custom no lo son, y los meses seguidos tampoco: los
  intervalos de H2 y H3 serían algo más anchos de verdad.
- **Grupos distintos.** Custom y estándar no son el mismo tipo de cliente: casi
  todos los Custom son de clubes. Una diferencia entre grupos no demuestra que
  una cosa cause la otra.
- **Estacionalidad.** H3 compara meses del año distintos.
- **Datos sintéticos.** Cada resultado repite alguna regla del generador: no es
  evidencia sobre clientes reales.
- **Muestras pequeñas.** Con menos de 30 valores en algún grupo, el resultado
  lleva un aviso; con menos de 5, no se calcula.

## Lo que NO se puede afirmar

- **Que personalizar un pedido haga gastar más a un cliente.** H1 compara grupos
  distintos de clientes; no es un experimento.
- **Que la demanda de NOVA crezca o no crezca.** Con los datos de PRUEBA no hay
  historial (1 mes). Con los sintéticos, la diferencia no es concluyente, y eso
  tampoco demuestra que no haya crecimiento.
- **Qué tallas habrá que fabricar el mes que viene.** Depende de los pedidos de
  club que entren.
- **Nada de lo que sale de los datos sintéticos describe a los clientes de NOVA.**
