# Segmentación de clientes y predicción de demanda (fase 5)

Apartados 6.8 (RFM y clustering) y 6.10 (predicción con aprendizaje automático)
de la rúbrica. El código está en `segmentacion.py` y `prediccion.py`, y `main.py`
lo ejecuta en el paso 9.

> **Todo lo que sale aquí con cifras es de los datos SINTÉTICOS** de
> `generador_datos.py` (semilla 2026). No son clientes ni ventas de NOVA. Los
> grupos de KMeans no son perfiles reales de clientes, y las predicciones no son
> una previsión de negocio: solo demuestran que el método funciona y cómo se evalúa.
> Cada CSV lleva la columna `origen` con «SINTÉTICO».

## Con los datos de prueba de Acceso a Datos: NO CALCULABLE

La exportación de prueba (`entrada_acc/`) tiene 6 clientes. Solo el cliente 6 tiene
una compra válida (CUSTOM-40), y todos los pedidos son del 9 de noviembre de 2026,
el mismo día de la fecha de corte. Con eso:

| Resultado | Qué sale | Por qué |
|---|---|---|
| RFM | una fila por cliente: 5 «Sin compras válidas» y el cliente 6 «NO CALCULABLE» | hacen falta al menos 10 clientes con compras para repartir quintiles |
| KMeans | NO CALCULABLE | con 1 cliente con compras, los grupos no significarían nada |
| Demanda mensual | NO CALCULABLE | noviembre no ha terminado: no hay ningún mes completo |
| Predicción | NO CALCULABLE | hacen falta al menos 12 meses completos |

No se fuerza KMeans sobre esos 6 clientes ni se rellena actividad que no existe.
Como pide la rúbrica, el método se demuestra con el histórico sintético y la
limitación se dice aquí.

## 1. RFM

### Las tres variables

Una fila por cliente, también para los que no han comprado.

| Variable | Cálculo | Unidad |
|---|---|---|
| Recency | días desde su última compra válida hasta la fecha de corte | días |
| Frequency | número de **pedidos** de venta distintos (no líneas: un pedido de 3 líneas cuenta 1) | pedidos |
| Monetary | suma del importe de esos pedidos (suma de sus líneas) | € (IVA pendiente de confirmar) |

- **Compra válida.** Es un pedido de venta (`config.ESTADOS_CONFIRMADOS`:
  confirmado, en preparación, enviado o entregado), el mismo criterio que los KPIs
  de venta. Los cancelados y los pendientes no cuentan.
- **Fecha de referencia.** Es la fecha de corte de la exportación
  (`stock.fecha_corte`), no el día en que se ejecuta Python. Así la misma
  exportación da siempre el mismo RFM. En los datos sintéticos es el 2026-11-01
  00:00.
- **Pedidos posteriores a la fecha de corte.** No entran nunca.
- **Clientes sin compras válidas.** Se quedan con frequency 0 y monetary 0, que son
  recuentos. Su recency queda vacía, porque no hay última compra que contar: no se
  inventa. Van al segmento «Sin compras válidas».

### Puntuaciones de 1 a 5

Cada variable se reparte en quintiles entre los clientes con compras: el 20 % de
clientes más recientes tiene R = 5, el 20 % con más pedidos tiene F = 5 y el 20 %
con más importe tiene M = 5. En recency se invierte la escala, porque menos días es
mejor.

Se usa `rank(method="first")` y después `qcut`. Los empates se deshacen por el
orden de `id_cliente`, así que el resultado es siempre el mismo aunque los pedidos
lleguen en otro orden (lo comprueba una prueba). Las puntuaciones son relativas:
comparan a los clientes entre sí y no dicen nada en euros absolutos.

### Los segmentos y su umbral

Las reglas se aplican en este orden, y gana la primera que se cumple:

| Segmento | Regla | Significado | Uso comercial |
|---|---|---|---|
| Sin compras válidas | frequency = 0 | no tiene ningún pedido de venta | captar o reactivar; no se le atribuye actividad |
| Mejores clientes | R ≥ 4, F ≥ 4 y M ≥ 4 | compran a menudo, hace poco y con mucho importe | cuidarlos y priorizar sus pedidos en producción |
| En riesgo | F ≥ 3 y R ≤ 2 | compraban con frecuencia, pero llevan tiempo sin comprar | contactarlos antes de perderlos |
| Habituales | F ≥ 3 | compran con regularidad | mantener la relación y ofrecer reposición |
| Inactivos | R ≤ 2 y F < 3 | compraron poco y hace tiempo | campañas de baja prioridad |
| Ocasionales | el resto | pocas compras, pero recientes | intentar que repitan |

Resultado con los datos sintéticos (40 clientes; todos han comprado alguna vez):

| Segmento | Clientes | Recency media (días) | Frequency media | Monetary total (€) | % del importe | Recency min–max | Frequency min–max |
|---|---|---|---|---|---|---|---|
| Sin compras válidas | 0 | – | – | 0,00 | 0,0 | – | – |
| Mejores clientes | 7 | 10,9 | 42,9 | 377.706,21 | 45,4 | 5–17 | 21–84 |
| En riesgo | 6 | 48,2 | 19,7 | 87.003,32 | 10,5 | 33–72 | 13–34 |
| Habituales | 11 | 17,1 | 22,4 | 240.007,03 | 28,9 | 2–28 | 14–47 |
| Inactivos | 10 | 65,4 | 9,6 | 90.137,12 | 10,8 | 30–154 | 5–13 |
| Ocasionales | 6 | 15,5 | 10,3 | 36.523,83 | 4,4 | 3–26 | 9–12 |

Los 7 «Mejores clientes» (17,5 % de los clientes) se llevan el 45,4 % del importe.

## 2. KMeans

### Variables y preparación

Se agrupa a los clientes **con compras** con las mismas tres variables del RFM:

1. **Recency en días.**
2. **log(1 + frequency) y log(1 + monetary).** Unos pocos clubes tienen importes
   muy grandes (hasta 173.187 €), y sin el logaritmo decidirían ellos solos los
   grupos.
3. **Estandarización** con `StandardScaler` (media 0 y desviación 1). Los días, los
   pedidos y los euros tienen escalas muy distintas, y KMeans mide distancias: sin
   escalar, mandarían los euros.
4. **Comprobación de nulos.** Si alguna variable tuviera un valor vacío, se para con
   un error en vez de rellenarlo. Los clientes sin compras no entran, porque su
   recency no existe.

No se usan variables que no sean de compra (tipo de cliente, nombre…). El tipo de
cliente solo se mira después, para describir los grupos.

### Elección de k

Se prueba k = 2, 3, 4 y 5 con `random_state = 2026` y `n_init = 10`, así que
siempre sale lo mismo. El criterio es el **silhouette score** más alto: va de −1 a
1, y cuanto más alto, más separado está cada grupo de los demás. Si hubiera empate,
se elegiría el k menor. La inercia se guarda solo como información.

| k | Silhouette | Inercia | Elegido |
|---|---|---|---|
| 2 | 0,348 | 71,78 | |
| 3 | 0,361 | 48,10 | |
| 4 | **0,373** | 37,31 | **sí** |
| 5 | 0,319 | 30,12 | |

**Mejor k = 4, con silhouette 0,373.** Es una separación moderada: los grupos
existen, pero no están muy separados. Las diferencias entre k = 2, 3 y 4 son
pequeñas.

### Los grupos

Los números de KMeans no significan nada, así que se renumeran de más a menos
importe medio. El nombre se forma automáticamente comparando las medias del grupo
con la **mediana** de todos los clientes con compras: recency 25,5 días, frequency
15,5 pedidos y monetary 7.992,81 €. Se usa la mediana porque la media la moverían los
pocos clientes extremos.

| Clúster | Nombre automático | Clientes | % | Recency media | Frequency media | Monetary medio (€) | Monetary mediana (€) | % empresas |
|---|---|---|---|---|---|---|---|---|
| 1 | empresas: importe alto, muchos pedidos, sin comprar hace más tiempo | 10 | 25,0 | 26,5 | 20,9 | 60.747,62 | 46.071,45 | 100 |
| 2 | particulares: importe alto, muchos pedidos, compra reciente | 9 | 22,5 | 16,6 | 40,1 | 14.526,82 | 10.708,27 | 0 |
| 3 | particulares: importe bajo, pocos pedidos, sin comprar hace más tiempo | 19 | 47,5 | 31,5 | 12,3 | 4.458,38 | 3.531,11 | 0 |
| 4 | particulares: importe bajo, pocos pedidos, sin comprar hace más tiempo | 2 | 5,0 | 144,0 | 9,0 | 4.225,33 | 4.225,33 | 0 |

- **Clúster 1:** son los 10 clubes del conjunto sintético. Hacen pedidos Custom
  grandes.
- **Clúster 2:** particulares muy frecuentes y recientes.
- **Clúster 3:** el grueso de particulares con poca actividad.
- **Clúster 4:** dos clientes que llevan unos 144 días sin comprar. Los clústeres 3
  y 4 tienen el mismo nombre automático porque las reglas solo distinguen «más» o
  «menos» que la mediana. Lo que los separa es cuánto: el 4 tiene una recency
  media de 144 días frente a 31,5.

### Comparación con RFM

Clientes de cada segmento RFM en cada clúster (`rfm_frente_a_kmeans.csv`):

| Segmento RFM | Clúster 1 | Clúster 2 | Clúster 3 | Clúster 4 | Total |
|---|---|---|---|---|---|
| En riesgo | 1 | 1 | 4 | 0 | 6 |
| Habituales | 4 | 4 | 3 | 0 | 11 |
| Inactivos | 2 | 0 | 6 | 2 | 10 |
| Mejores clientes | 3 | 4 | 0 | 0 | 7 |
| Ocasionales | 0 | 0 | 6 | 0 | 6 |

- **Coincidencias.** Ningún «Mejor cliente» cae en los clústeres de poca actividad
  (3 y 4). Los dos clientes del clúster 4 son «Inactivos». Los «Ocasionales» están
  todos en el clúster 3.
- **Diferencias.**
  - KMeans separa sobre todo a **empresas** y **particulares**: el importe de un
    club es de otro orden.
  - RFM mezcla los dos tipos en cada segmento, porque puntúa por quintiles
    relativos.
  - Los «Mejores clientes» de RFM se reparten entre los clústeres 1 y 2.

**Por qué un grupo matemático no es una categoría comercial.** KMeans solo busca
puntos cercanos en un espacio de tres variables escaladas. No sabe qué es «un
cliente en riesgo» ni qué acción comercial conviene, y sus grupos cambian si
cambian las variables, la escala o el k. Las reglas RFM, en cambio, las define el
equipo con un umbral explicado y una acción asociada. Para decidir campañas sirven
las reglas RFM. KMeans sirve para comprobar si esas reglas reflejan la forma de los
datos: aquí indica que el tipo de cliente pesa mucho y que quizá convendría
segmentar empresas y particulares por separado.

## 3. Predicción de la demanda mensual por modelo

### Qué se predice

Los **pares de demanda de un modelo en un mes**. Se cuentan los pedidos no
cancelados, el mismo criterio que la matriz modelo × mes de la fase 3: la suma de
los 216 valores coincide con esa matriz, y lo comprueba una prueba.

- Solo entran **meses completos** anteriores a la fecha de corte. Un mes a medias
  parecería una caída de la demanda.
- Un modelo sin pedidos en un mes del periodo tiene 0 pares, que es un recuento.

Datos sintéticos: 12 modelos × 18 meses (2025-05 a 2026-10) = 216 filas.

### Variables de entrada (todas anteriores al mes que se predice)

| Variable | Cálculo | Por qué |
|---|---|---|
| `pares_mes_anterior` | pares del mismo modelo en el mes t−1 | la rúbrica la pide; es también el baseline |
| `media_3_meses_previos` | media de t−1, t−2 y t−3 (sin el mes t) | suaviza los picos de un solo mes |
| `mes_seno`, `mes_coseno` | sen(2π·mes/12) y cos(2π·mes/12) | el mes del año como un punto en un círculo: diciembre y enero quedan cerca, y no se trata el mes como una cantidad que crece de 1 a 12 |
| `modelo_…` | una columna de 0 y 1 por modelo (one-hot), menos el primero | el número de un modelo es una etiqueta, no una cantidad; se quita una columna porque con las 12 una se deduce de las otras y la regresión lineal no tendría una solución única |

- Todas se calculan con `shift`, que significa «el mes anterior del mismo modelo».
- El primer mes de un modelo no hereda el último mes del modelo anterior.
- Los pares del propio mes, y los de los meses siguientes, nunca son una entrada.
- Tampoco lo es ningún total del mes que se predice.

### Separación por fecha

Los meses nunca se mezclan al azar:

| Conjunto | Meses | Filas | Para qué |
|---|---|---|---|
| historial | 2025-05 a 2025-07 | 36 | no tienen 3 meses previos: solo dan datos a las variables de los meses siguientes |
| entrenamiento | **2025-08 a 2026-07** (12 meses) | 144 | lo único con lo que se ajusta la regresión |
| evaluación | **2026-08 a 2026-10** (los 3 últimos) | 36 | solo para medir el error |

La evaluación es **a un mes vista**: para predecir septiembre ya se conocen los pares
de agosto, igual que los sabría NOVA el 1 de septiembre. Los dos métodos usan esa
misma información. La regresión **no** se vuelve a entrenar con agosto ni con
septiembre. Hacen falta al menos 12 meses completos (3 de historial, 6 o más de
entrenamiento y 3 de evaluación); con menos, NO CALCULABLE.

### Los dos métodos

- **A. Baseline:** el mes que viene se piden los mismos pares que este mes. Es la
  referencia obligatoria. Si el aprendizaje automático no la mejora, no aporta nada.
- **B. `LinearRegression` de scikit-learn** con las variables de la tabla anterior.
  Se eligió por tres motivos:
  - **Es interpretable.** Sus coeficientes se leen en `coeficientes_regresion.csv`.
  - **Encaja con pocos datos.** Con 144 filas, un modelo más flexible, como un
    bosque aleatorio, aprendería el ruido.
  - **No tiene hiperparámetros que ajustar.** Así no hay nada que se pueda elegir
    mirando la evaluación.

  Si la recta da un número negativo, se deja en 0, porque no se pueden pedir menos
  de 0 pares. Esta regla se fijó antes de ver los resultados. En la evaluación solo
  afecta a 1 predicción (−2,38 pasa a 0), y sin ella la conclusión es la misma:
  MAE 26,34 y RMSE 36,16.

### Métricas

- **MAE (error absoluto medio).** Cuántos pares se equivoca de media, sin mirar si
  se pasa o se queda corto: media de |real − predicción|.
- **RMSE (raíz del error cuadrático medio).** √media((real − predicción)²). Se
  parece al MAE, pero un error grande pesa mucho más que varios pequeños.

**Criterio, fijado en el código antes de ver los resultados**
(`prediccion.mejora`): la regresión solo «mejora al baseline» si baja el MAE **y**
el RMSE. Si mejora una sola métrica, se dice así. Un empate no es una mejora.

### Resultado (evaluación 2026-08 a 2026-10, 36 predicciones)

| Método | MAE (pares) | RMSE (pares) | ¿Mejora al baseline? |
|---|---|---|---|
| A. Baseline (mes anterior) | **25,03** | 37,42 | es la referencia |
| B. Regresión lineal | 26,28 | **36,15** | solo en una métrica: RMSE sí, MAE no |

**La regresión NO mejora al baseline de forma clara.** Se equivoca más de media
(MAE 26,28 frente a 25,03) y algo menos en los errores grandes (RMSE 36,15 frente a
37,42). Con el criterio fijado, no justifica sustituir al método ingenuo, que además
es más sencillo. No se han cambiado los datos ni las variables después de ver el
resultado.

Pares totales por mes (suma de los 12 modelos):

| Mes | Real | Baseline | Regresión |
|---|---|---|---|
| 2026-08 | 296 | 270 | 327,3 |
| 2026-09 | 584 | 296 | 389,5 |
| 2026-10 | 397 | 584 | 460,6 |

Por modelo (`errores_por_modelo.csv`):

| Modelo | Pares reales | MAE baseline | MAE regresión | RMSE baseline | RMSE regresión | Menos error (MAE) |
|---|---|---|---|---|---|---|
| SINT Runner | 325 | 46,00 | 58,30 | 58,14 | 70,02 | baseline |
| SINT Court | 221 | 12,67 | 37,90 | 13,74 | 38,39 | baseline |
| SINT Classic | 197 | 30,00 | 42,90 | 33,18 | 46,68 | baseline |
| SINT Trail | 179 | 56,33 | 34,63 | 61,16 | 46,25 | regresión |
| SINT Flex | 104 | 25,33 | 18,73 | 32,79 | 24,50 | regresión |
| SINT Urban | 84 | 47,33 | 27,93 | 57,64 | 38,16 | regresión |
| SINT Sprint | 84 | 44,00 | 24,70 | 50,52 | 33,76 | regresión |
| SINT Street | 22 | 22,00 | 36,07 | 35,87 | 36,18 | baseline |
| SINT Retro | 19 | 5,33 | 4,47 | 8,68 | 4,94 | regresión |
| SINT Volt | 18 | 6,67 | 6,10 | 7,48 | 7,10 | regresión |
| SINT Wave | 14 | 4,33 | 19,43 | 4,65 | 19,51 | baseline |
| SINT Peak | 10 | 0,33 | 4,17 | 0,58 | 5,48 | baseline |

### Análisis de errores

- **Los pedidos Custom.** El 75 % de los pares de los meses de evaluación son
  pedidos Custom de clubes, de 5 a 20 pares por talla. Llegan de forma irregular:
  SINT Trail pasa de 9 pares en julio a 99 en agosto, y 95 de ellos son Custom. Por
  eso lo que pasó el mes anterior predice mal el siguiente, y los dos métodos tienen
  errores grandes.
- **El baseline va un mes tarde.** Copia el pico del mes anterior:
  - SINT Urban: pide 75 en septiembre; el baseline predice 75 en octubre y llegan 8.
  - SINT Sprint: el mismo caso, con 69 predichos en octubre y 5 reales.
  - Sus errores más grandes son de 93, 90 y 74 pares.
- **La regresión predice cerca de la media de cada modelo.** Sus coeficientes lo
  explican: el mes anterior pesa poco (+0,256) y la media de 3 meses incluso resta
  (−0,412), porque tras un pico suele venir un mes flojo. Lo que más pesa es la
  columna del modelo (SINT Runner +155 pares). Por eso:
  - acierta más en los modelos con picos sueltos (Trail, Urban, Sprint, Flex);
  - falla más en los modelos estables o pequeños, donde el mes anterior ya era una
    buena pista (Court, Wave, Peak);
  - su peor error: predice 158 pares de SINT Runner en agosto y fueron 59.
- **Pocos datos.** La regresión aprende de 12 meses × 12 modelos = 144 filas. Cada
  mes del año aparece una sola vez en el entrenamiento, así que la estacionalidad
  (seno y coseno) apenas se puede estimar.

Gráfico: `graficos_prediccion/11_real_frente_a_prediccion.png`. Cada punto es un
modelo en un mes de evaluación, y en la diagonal la predicción acierta. Está aparte
de los 10 gráficos descriptivos porque es un resultado predictivo.

## Archivos que se generan (en la carpeta de salida de cada modo)

| Archivo | Contenido |
|---|---|
| `rfm_clientes.csv` | una fila por cliente: tipo, última compra, recency, frequency, monetary, R, F, M, segmento y clúster |
| `rfm_segmentos.csv` | clientes, medias, importe y significado de cada segmento |
| `kmeans_seleccion_k.csv` | silhouette e inercia de k = 2 a 5 y el k elegido |
| `kmeans_clusters.csv` | estadísticas, proporciones y nombre de cada clúster |
| `rfm_frente_a_kmeans.csv` | tabla cruzada segmento RFM × clúster |
| `demanda_mensual_modelo.csv` | pares por modelo y mes, sus variables de entrada y su conjunto |
| `predicciones.csv` | real, baseline, regresión y sus errores en los meses de evaluación |
| `metricas_prediccion.csv` | MAE y RMSE de los dos métodos, periodos exactos y si la regresión mejora |
| `errores_por_modelo.csv` | MAE y RMSE de cada método por modelo de zapatilla |
| `coeficientes_regresion.csv` | constante y coeficiente de cada variable de la regresión |
| `graficos_prediccion/11_real_frente_a_prediccion.png` | real frente a predicción |

Todos llevan las columnas `origen` y `ejecucion`. Si la calidad bloquea los datos,
no se escribe ninguno.

## Lo que NO se puede afirmar

- Nada de esto describe a los clientes reales de NOVA. Los segmentos y los clústeres
  son de 40 clientes simulados.
- Con los datos de prueba de Acceso a Datos no hay segmentación ni predicción
  defendibles: 1 cliente con compras y ningún mes completo.
- Un silhouette de 0,373 indica grupos moderadamente separados, no tipos de cliente
  «naturales».
- La regresión no ha demostrado mejorar al método ingenuo. Con un historial real más
  largo habría que repetir la evaluación antes de usarla para planificar
  producción.
- 3 meses de evaluación (36 predicciones) son pocos: con otros 3 meses, el orden de
  los dos métodos podría cambiar.
- Los estados de los pedidos son los de la fecha de corte, porque no hay un
  historial de cambios de estado. Por ejemplo, un pedido de agosto cancelado en
  octubre ya no cuenta en la demanda de agosto, aunque el 1 de septiembre todavía
  se contaba. Ninguna variable de entrada usa el mes que se predice, pero los meses
  anteriores se ven con los estados de hoy.

## Pruebas

En `tests/test_segmentacion.py` hay 18 pruebas y en `tests/test_prediccion.py`
hay 20. `test_sinteticos.py` añade 1, que comprueba la ejecución completa con datos
sintéticos.

Segmentación:
- recency desde la fecha de corte;
- pedidos posteriores al corte;
- frequency y monetary;
- clientes sin compras;
- quintiles y reglas de cada segmento;
- RFM reproducible aunque cambie el orden;
- variables estandarizadas y sin nulos;
- k de 2 a 5 con silhouette, y la elección de k;
- KMeans reproducible;
- descripción de los clústeres y comparación con RFM;
- con pocos clientes, NO CALCULABLE.

Predicción:
- demanda con ceros y sin cancelados;
- sin meses futuros ni incompletos;
- variables solo del pasado;
- periodos exactos;
- **las filas de agosto, septiembre y octubre de 2026 no entran en el
  entrenamiento.** Se espía qué filas recibe `fit`. Además, si se multiplican esos
  meses por 100, los coeficientes no cambian;
- el mes objetivo no es una entrada: si se cambia octubre, ninguna predicción
  cambia;
- baseline;
- MAE y RMSE con valores conocidos;
- comparación de los dos métodos, en un caso en que mejora y en otro en que no;
- datos insuficientes;
- con calidad bloqueada no se publica nada.
