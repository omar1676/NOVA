# KPIs, DataFrames y gráficos (fase 3)

`main.py` calcula 20 KPIs (17 calculables y 3 «NO CALCULABLE» con su motivo), 17
DataFrames analíticos y 10 gráficos PNG. Todo sale de los mismos DataFrames de
`analiticas.py` y queda en `outputs/real/`.

**Los datos son de una base de PRUEBA**, no de la base del equipo. Son 12 pedidos
de un solo día, de 6 clientes. Las cifras de abajo sirven para comprobar que los
cálculos funcionan, **no son ventas reales** y no se deben presentar como tales.
Cada CSV y cada gráfico lleva escrito su origen.

## Qué pedidos cuenta cada cifra

| Población | Qué pedidos | Para qué |
|---|---|---|
| todos | todos los pedidos válidos, en cualquier estado | actividad registrada |
| demanda | los no cancelados (criterio del panel P-A de Acceso a Datos) | modelos, tallas, matrices y ABC: lo que hay que fabricar |
| venta | `confirmado`, `en_preparacion`, `enviado` y `entregado` (apartado 6.5) | importe vendido, ticket y precio medio |
| pagado | `estado_pago = pagado` | lo que Acceso a Datos marca como pagado. No es un cobro comprobado |

Ninguna cifra es «ingresos cobrados» y el IVA está **pendiente de confirmar**. El
equipo tiene que confirmar qué estados son venta; está en `config.py`.

## KPIs

| Código | KPI | Fórmula | Unidad | Población | Datos de prueba |
|---|---|---|---|---|---|
| K01 | Pedidos registrados | nº de pedidos | pedidos | todos | 12 |
| K02 | Pedidos confirmados | nº de pedidos confirmados en adelante | pedidos | venta | 1 |
| K03 | Pedidos cancelados | nº de pedidos cancelados | pedidos | todos | 0 |
| K04 | Pares solicitados | suma de pares de los no cancelados | pares | demanda | 90 |
| K05 | Pares confirmados | suma de pares de los confirmados en adelante | pares | venta | 40 |
| K06 | Importe registrado | suma del importe de todos los pedidos | € | todos | 10.686,45 |
| K07 | Importe confirmado | suma del importe de los confirmados en adelante | € | venta | 4.796,00 |
| K08 | Importe con pago registrado | suma del importe con `estado_pago = pagado` | € | pagado | 0,00 |
| K09 | Ticket medio | K07 / K02 (entre pedidos, nunca entre líneas) | €/pedido | venta | 4.796,00 (1 pedido) |
| K10 | Pares por pedido | K05 / K02 | pares/pedido | venta | 40 (1 pedido) |
| K11 | Precio medio por par | K07 / K05 (media ponderada) | €/par | venta | 119,90 |
| K12 | Pedidos Custom | custom no cancelados / no cancelados × 100 | % | demanda | 41,7 (5 de 12) |
| K13 | Modelo más solicitado | máximo de pares por modelo; si hay empate se nombran todos | pares | demanda | 82, NOVA Velocity (91,1 %) |
| K14 | Talla más solicitada | máximo de pares por talla; si hay empate se nombran todas | pares | demanda | 23, talla 42 (25,6 %) |
| K15 | Concentración de Pareto | pares del 20 % de modelos con más pares / pares totales × 100 | % | demanda | 91,1 (1 de 7 modelos) |
| K16 | Stock total | suma de `stock_disponible` de todos los SKU | pares | stock | 1.160 |
| K17 | Referencias con stock bajo | nº de SKU con menos de 10 pares | SKU | stock | 0 |
| K18 | Margen | importe − coste | € | venta | **NO CALCULABLE**: no hay coste unitario |
| K19 | Variación mensual del importe | (último mes / mes anterior − 1) × 100 | % | venta | **NO CALCULABLE**: un solo mes |
| K20 | Cobertura de stock | stock / (demanda de 28 días / 4) | semanas | demanda | **NO CALCULABLE**: 0 días de historial |

Cada KPI está en `kpis.csv` con su detalle y la tabla de la que sale. Los siete que
también calcula Acceso a Datos (K01 a K07) se contrastan con sus consultas P-A y
P-B en `coherencia_kpis_sql.csv`: **coinciden los 7**.

No hay dos KPIs que den la misma cifra con distinto nombre. Por ejemplo, K04 (90
pares) y K05 (40) cuentan pedidos distintos.

## DataFrames

| Nº de la rúbrica (6.15) | Archivo | Qué contiene | Filas |
|---|---|---|---|
| base | `df_lineas_enriquecidas` (no se guarda) | una fila por línea, con pedido, cliente y modelo | 18 |
| 01 | `pedidos_unicos.csv` | una fila por pedido (sin el nombre del cliente) | 12 |
| — | `pedidos_por_estado.csv` | pedidos, pares e importe de los 6 estados del catálogo | 6 |
| 02 | `ventas_por_periodo.csv` | venta por mes: ticket, variación, media de 3 meses previos e interanual | 1 |
| 03 | `modelos_abc.csv` | ventas por modelo: pares, pedidos, importe, rankings y clase ABC | 7 |
| — | `ventas_por_talla.csv` | pares de demanda por talla y su peso | 5 |
| 04 | `matriz_modelo_talla.csv` y `matriz_modelo_talla_proporcion.csv` | pares por modelo × talla, y qué parte de cada modelo es de cada talla | 6 × 5 |
| 6.9 | `matriz_modelo_mes.csv` | pares por modelo × mes | 6 × 1 |
| 05 | `custom_vs_estandar.csv` | tasa de cancelación (pedidos), cuotas de demanda y ticket de venta por tipo | 2 |
| 06 | `clientes_actividad.csv` | pedidos, pares, importe y días desde el último pedido por cliente (base del RFM) | 6 |
| 07 | `cohortes.csv` | retención por mes de primera compra | **NO CALCULABLE** |
| 08 | `stock_variantes.csv` y `stock_bajo.csv` | stock por SKU, demanda de 28 días, alerta y cobertura | 60 y 0 |
| 09 | `resumen_calidad.csv`, `incidencias.csv` y `nulos_por_columna.csv` | calidad por tabla, incidencias y celdas vacías por columna | 5, 2 y 36 |
| 10 | `anomalias.csv` | atípicos de precio (por modelo y tipo de pedido) y de cantidad (por tipo) con la regla IQR | 9 grupos, 0 atípicos |
| 11 | `precio_y_margen.csv` | precio medio ponderado por par; margen **NO CALCULABLE** | 7 |
| 12 | `conciliacion_sql.csv` | conciliación con P-A, P-B y P-C | 21 cifras, todas coinciden |

Hay 14 tablas analíticas además de las dos vistas base, y ninguna está hecha para
llegar a un número:
- `pedidos_por_estado` y `ventas_por_talla` las pide el enunciado.
- `matriz_modelo_mes` la pide el apartado 6.9.
- `stock_bajo` es solo una vista filtrada de `stock_variantes` y no se cuenta aparte.

Cada cruce lleva `validate=` e `indicator=True`, y las pruebas comprueban que las
matrices, el ABC y las tallas suman exactamente los pares de demanda: nada se
cuenta dos veces.

El RFM (segmentos) se hace en la fase 5, en `segmentacion.py`; ver
`segmentacion_y_prediccion.md`. `clientes_actividad` sigue siendo la tabla de
actividad de cada cliente.

## Gráficos

Están en `outputs/real/graficos/`. Cada uno lleva la pregunta como título, ejes con
unidades, leyenda cuando hace falta y un pie con el origen, el corte, el momento
del cálculo, los filtros y el IVA.

| Archivo | Tipo | Pregunta | Lectura con los datos de prueba |
|---|---|---|---|
| `01_pedidos_por_estado` | barras | ¿En qué estado están los pedidos? | 11 pendientes y 1 confirmado; ningún cancelado, enviado ni entregado |
| `02_pareto_modelos` | Pareto | ¿Qué modelos concentran la demanda? | NOVA Velocity se lleva el 91 % de los pares (clase A). Pero 80 de sus 82 pares son los dos pedidos de 40 que podrían ser el mismo |
| `03_pares_por_talla` | barras | ¿Qué tallas se piden más? | de la 40 a la 43, casi igual (21–23 pares); la 44, 2 |
| `04_evolucion_demanda` | serie temporal | ¿Cómo evoluciona la demanda? | **solo hay un día**: el gráfico lo dice y el eje no inventa meses |
| `05_matriz_modelo_talla` | mapa de calor | ¿Qué tallas se piden de cada modelo? | Velocity, de la 40 a la 43, unos 20 de cada; el resto, pares sueltos |
| `06_custom_vs_estandar` | comparativa por segmento | ¿Cuánto pesan los Custom? | 42 % de los pedidos, pero 92 % de los pares y 93 % del importe |
| `07_clientes_por_importe` | ranking | ¿Qué clientes concentran el importe? | el cliente 6 (empresa) tiene el 89,8 % del importe de demanda (9.592 de 10.686,45 €) |
| `08_stock_por_sku` | histograma | ¿Cuántas referencias tienen poco stock? | 56 SKU con 20 pares y 4 con 10; ninguno por debajo de 10 |
| `09_importe_por_tipo` | diagrama de caja | ¿Cuánto vale un pedido según su tipo? | normal, entre 80 y 120 €; custom, de 115 a 4.796 € |
| `10_pares_frente_a_importe` | dispersión | ¿El importe crece con los pares? | dos grupos: pedidos de 1 par y dos pedidos de 40 pares; ningún punto fuera de esos grupos |

Los clientes salen por su id, no por su nombre: el nombre no hace falta para
analizar.

## Clasificación ABC

- **Qué se clasifica:** los modelos del catálogo, por **pares de demanda** (pedidos
  no cancelados). Se usan pares porque sirve para decidir qué fabricar. El importe
  y su ranking también están en la tabla.
- **Cómo:** se ordena de más a menos pares y se mira lo que se acumula **antes** de
  cada modelo:
  - **A** si es menos del 80 %;
  - **B** si es menos del 95 %;
  - **C** el resto.

  Así, el modelo que cruza el 80 % es A. Los modelos empatados reciben la misma
  clase, porque si no el orden alfabético decidiría la clase. Un modelo sin demanda
  sigue en la tabla, con 0 pares y clase C.
- **Resultado con los datos de prueba:**

| Modelo | Pares | Peso | Acumulado | Clase |
|---|---|---|---|---|
| NOVA Velocity | 82 | 91,1 % | 91,1 % | A |
| NOVA Archive, NOVA Eclipse, NOVA Origin | 2 cada uno | 2,2 % cada uno | 93,3 a 97,8 % | B (empatados) |
| NOVA Aura, NOVA Pulse | 1 cada uno | 1,1 % cada uno | 98,9 y 100 % | C |
| X-NOVA | 0 | 0 % | 100 % | C |

- **Para qué sirve:**
  - **Clase A:** se planifica primero, con materiales y hormas de sus tallas preparados.
  - **Clase B:** se fabrica por pedido.
  - **Clase C:** no se fabrica sin pedido, porque inmovilizaría almacén.
- **No es el ABC del valor del stock.** Ese clasificaría el inventario por lo que
  vale y necesitaría el coste de cada par, que no se exporta. Aquí se clasifica la
  demanda.

## Limitaciones y valores no calculables

- **Datos de prueba.** No son la base del equipo ni ventas reales.
- **Un solo día de pedidos.** No hay evolución mensual (K19), cohortes, cobertura
  (K20) ni estacionalidad. No se ha inventado ningún mes.
- **Pocos datos.** Hay 6 clientes, 12 pedidos y 18 líneas. El ticket, los pares por
  pedido y el precio medio de venta salen de **un solo pedido confirmado**. Los
  atípicos no se pueden evaluar en la mayoría de grupos (menos de 5 valores).
- **NOVA-0011 y CUSTOM-40.** Siguen los dos, con la advertencia de calidad de la
  regla 12. Si fueran el mismo encargo, la demanda sería de 50 pares y no de 90, y
  NOVA Velocity seguiría siendo A, pero con 42 pares.
- **Sin coste unitario.** El margen es NO CALCULABLE y no se calcula con el precio
  de venta.
- **Sin IVA confirmado ni cobros comprobados.** Ninguna cifra es «cobrado».
- **El stock es una foto.** Corresponde a la fecha de corte y no es un histórico.
  Nunca se suma entre colores.
- **No hay datos sintéticos** en ningún resultado de esta fase.
