# Diccionario de datos

Columnas de los cinco CSV que exporta Acceso a Datos con
`02_Acceso_Datos/sql/16_exportar_csv_dashboard.sql`. Los nombres, el orden y los
tipos se han comprobado contra ese script, contra el esquema
(`sneaker-factory-esquema.sql` y `04_xnova.sql`) y contra una exportación real del
9 de noviembre de 2026. Acceso a Datos tiene su propio diccionario en
`02_Acceso_Datos/documentacion/README.md`, apartado «Exportación de los cinco CSV del
contrato».

Los tipos de pandas son los que deja `pipeline.py` después de convertir cada columna
(`config.py`). **Los identificadores se guardan como texto**: sirven para unir tablas,
nunca para sumar ni promediar.

## Formato de los cinco archivos

| Aspecto | Valor |
|---|---|
| Codificación | UTF-8 sin BOM (Python también acepta el BOM que añade Excel) |
| Delimitador | coma `,` |
| Decimal | punto: `119.90` |
| Moneda | euros, sin símbolo. **No se indica si los importes llevan IVA** |
| Fechas | `AAAA-MM-DD HH:MM:SS`, hora de la base, sin zona horaria |
| Lógicos | `true` / `false` |
| Nulo | celda vacía. Python lo deja como nulo: nunca lo convierte en 0 |
| Textos con comas | entre comillas dobles (CSV estándar) |
| Orden de las filas | fijo; dos exportaciones de los mismos datos dan archivos iguales, salvo `fecha_corte` |

## Relaciones

| Desde | Hacia | Cardinalidad | Nota |
|---|---|---|---|
| `pedidos.id_cliente` | `clientes.id_cliente` | muchos a uno | |
| `lineas_pedido.id_pedido` | `pedidos.id_pedido` | muchos a uno | un pedido con 3 líneas es **un** pedido |
| `lineas_pedido.id_modelo` | `modelos.id_modelo` | muchos a uno | |
| `lineas_pedido.sku` | `stock.sku` | muchos a uno | `sku` vacío en las líneas X-NOVA |
| `stock.id_modelo` | `modelos.id_modelo` | muchos a uno | |

`lineas_pedido.csv` no trae el color: se obtiene del stock a través del `sku`.

## clientes.csv

| Columna | Significado | Origen | Tipo pandas | Valores | Nulos | Obligatoria |
|---|---|---|---|---|---|---|
| `id_cliente` | Identificador del cliente | `clientes.id_cliente` | texto | único | no | sí |
| `nombre` | Nombre del cliente o del club | `clientes.nombre` | texto | | no | sí |
| `tipo` | Tipo de cliente | `clientes.tipo` | texto | `particular`, `empresa` | no | sí |
| `correo` | Correo de contacto | `clientes.email` | texto | ficticio, `@example.com` | no | no |
| `telefono` | Teléfono | `clientes.telefono` | texto | | sí (5 de 6 vacíos) | no |
| `activo` | Cliente activo | `clientes.activo` | lógico | `true`, `false` | no | sí |

`correo` y `telefono` son datos personales y no hacen falta para el análisis: no se
usarán en cálculos ni se mostrarán o descargarán en el dashboard.

## modelos.csv

| Columna | Significado | Origen | Tipo pandas | Valores | Nulos | Obligatoria |
|---|---|---|---|---|---|---|
| `id_modelo` | Identificador del modelo | `modelos.id_modelo` | texto | único | no | sí |
| `nombre_modelo` | Nombre comercial | `modelos.nombre` | texto | único | no | sí |
| `descripcion` | Descripción | `modelos.descripcion` | texto | | sí | no |
| `precio_base` | Precio de catálogo | `modelos.precio_base` | decimal | euros, ≥ 0 | no | sí |
| `activo` | Modelo a la venta | `modelos.activo` | lógico | `true`, `false` | no | sí |

## pedidos.csv

| Columna | Significado | Origen | Tipo pandas | Valores | Nulos | Obligatoria |
|---|---|---|---|---|---|---|
| `id_pedido` | Identificador del pedido | `pedidos.id_pedido` | texto | único | no | sí |
| `referencia` | Código visible del pedido | `pedidos.referencia` | texto | único, p. ej. `CUSTOM-40` | no | sí |
| `id_cliente` | Cliente que lo pide | `pedidos.id_cliente` | texto | existe en `clientes.csv` | no | sí |
| `fecha_pedido` | Fecha y hora de alta | `pedidos.fecha_pedido` | fecha | `AAAA-MM-DD HH:MM:SS` | no | sí |
| `tipo_pedido` | Estándar o personalizado | `pedidos.personalizado` | texto | `normal`, `custom` | no | sí |
| `estado_pedido` | Estado del pedido | `pedidos.estado` | texto | `pendiente`, `confirmado`, `en_preparacion`, `enviado`, `entregado`, `cancelado` | no | sí |
| `estado_pago` | Estado del pago | `pedidos.estado_pago` | texto | `pendiente`, `pagado`, `reembolsado` | no | sí |
| `personalizacion` | Qué se personaliza | `pedidos.personalizacion` | texto | texto libre | sí, en los `normal` | no |
| `cantidad_total` | Pares del pedido | `pedidos.cantidad_total` | entero | pares, ≥ 0; suma de sus líneas | no | sí |
| `importe_total` | Importe del pedido | `pedidos.importe_total` | decimal | euros, ≥ 0; suma de sus líneas | no | sí |

`cantidad_total` e `importe_total` los calcula un trigger de PostgreSQL. El
exportador comprueba antes de exportar que cuadran con las líneas, y Python lo
vuelve a comprobar.

## lineas_pedido.csv

| Columna | Significado | Origen | Tipo pandas | Valores | Nulos | Obligatoria |
|---|---|---|---|---|---|---|
| `id_linea` | Identificador de la línea | `linea_pedido.id_linea` | texto | único | no | sí |
| `id_pedido` | Pedido al que pertenece | `linea_pedido.id_pedido` | texto | existe en `pedidos.csv` | no | sí |
| `sku` | Referencia de inventario | `producto_sku.sku` | texto | existe en `stock.csv` | sí, en líneas X-NOVA | sí (la columna) |
| `id_modelo` | Modelo | `variantes.id_modelo` | texto | existe en `modelos.csv`; en X-NOVA, el modelo X-NOVA | no | sí |
| `talla` | Talla europea | `producto_sku.talla` | entero | la base admite 20–55; el catálogo tiene 40–44 | no | sí |
| `cantidad` | Pares de esa talla | `linea_pedido.cantidad` | entero | pares, > 0 | no | sí |
| `precio_unitario` | Precio por par al hacer el pedido | `linea_pedido.precio_unitario` | decimal | euros, ≥ 0 | no | sí |
| `importe_linea` | Importe de la línea | `linea_pedido.subtotal` | decimal | euros = `cantidad` × `precio_unitario` | no | sí |

## stock.csv

| Columna | Significado | Origen | Tipo pandas | Valores | Nulos | Obligatoria |
|---|---|---|---|---|---|---|
| `sku` | Referencia de inventario | `producto_sku.sku` | texto | único: una fila por SKU | no | sí |
| `id_modelo` | Modelo | `variantes.id_modelo` | texto | existe en `modelos.csv` | no | sí |
| `color` | Color de la variante | `variantes.color` | texto | | no | sí |
| `talla` | Talla europea | `producto_sku.talla` | entero | 40–44 en el catálogo actual | no | sí |
| `activo` | SKU a la venta | `producto_sku.activo` | lógico | `true`, `false` | no | no |
| `stock_disponible` | Pares en almacén | `SUM(existencias.cantidad)` | entero | pares, ≥ 0; suma de todas las naves | no | sí |
| `fecha_corte` | Momento de la exportación | `now()` | fecha | la misma en todas las filas | no | sí |

El stock es **una foto** en `fecha_corte`, no un histórico. Hay una fila por
modelo, color y talla: un mismo modelo y talla aparece una vez por color.

## Equivalencias con la rúbrica

La rúbrica (apartado 4) da nombres orientativos y pide un diccionario de
equivalencias:

| Archivo | Nombre en la rúbrica | Columna real |
|---|---|---|
| clientes | `id_cliente`, nombre o alias | `id_cliente`, `nombre` |
| modelos | `id_modelo`, `modelo`, categoría si existe | `id_modelo`, `nombre_modelo`; **no hay categoría** |
| pedidos | `id_pedido`, `fecha`, `id_cliente`, `estado`, `tipo` | `id_pedido`, `fecha_pedido`, `id_cliente`, `estado_pedido`, `tipo_pedido` |
| lineas_pedido | `id_linea`, `id_pedido`, `id_modelo`, `talla`, `cantidad`, `precio_unitario` | los mismos, más `sku` e `importe_linea` |
| stock | `id_modelo`, `talla`, `stock_disponible`, `fecha_corte` | los mismos, más `sku`, `color` y `activo` |

## Lo que falta o hay que decidir para cumplir la rúbrica

Visto en la exportación del 9 de noviembre de 2026 (base de prueba reconstruida
con los scripts del repositorio):

1. **No hay historial.** Los 12 pedidos son del mismo día (un solo mes). Con
   los datos reales no se pueden hacer series mensuales, estacionalidad, cohortes
   ni predicción: hará falta el histórico sintético de `generador_datos.py`
   (apartado 5), separado y etiquetado.
2. **Hay pocos clientes (6), y solo uno con compras.** RFM da una fila por cliente,
   pero ni los segmentos ni KMeans son defendibles con los datos reales (apartado
   6.8). Salen como NO CALCULABLE y se demuestran con el sintético (ver
   `segmentacion_y_prediccion.md`).
3. **No hay coste unitario.** El margen (DataFrame 11) será «NO CALCULABLE».
4. **No hay categoría de modelo.** No existe en el esquema.
5. **Solo hay dos estados.** Hay 11 pedidos `pendiente`, 1 `confirmado`, ningún
   `cancelado` ni `entregado`, y todos los pagos están `pendiente`. Para las
   pruebas de cancelación (caso B y R2), Acceso a Datos tiene que crear esos
   pedidos y volver a exportar.
6. **Hay que decidir qué es una venta.** El panel de Acceso a Datos cuenta todo
   pedido no `cancelado`. La rúbrica (6.5) habla de pedidos confirmados o
   entregados. Desde la fase 2, Python calcula los tres criterios
   (`importes_por_criterio.csv`), pero el equipo tiene que elegir uno para la
   memoria y el dashboard.
7. **No se sabe si los importes son netos o brutos.** El contrato no dice si
   llevan IVA, y la rúbrica pide distinguirlo. Queda «pendiente de confirmar» en
   `config.py` y en los resultados.
8. **Hay dos pedidos de 40 pares para el mismo club.** `NOVA-0011` (pendiente) y
   `CUSTOM-40` (confirmado). Son 80 de los 90 pares. Investigado en la fase 2
   (`calidad_datos.md`, caso A): no comparten ningún identificador, pero sí
   cliente, artículos, cantidades y precio. Python mantiene los dos con una
   advertencia; Acceso a Datos tiene que decir si son el mismo encargo.
9. **Las tallas válidas no están definidas.** La base admite 20–55, el catálogo
   tiene 40–44 y el caso común SO024 habla de 38–46. Hay que fijarlas para la
   regla 08.
10. **La clave del stock es el `sku`, no modelo + talla.** La regla 11
    («duplicado por modelo-talla») se tiene que adaptar a `sku` o a modelo + color
    + talla.
11. **X-NOVA tiene un `precio_base` de 12.000 €.** Ahora no tiene líneas. Si
    aparecen, saldrán como atípicas.
12. **Solo `stock.csv` lleva fecha de corte.** Los otros cuatro no llevan la
    hora de exportación; el manifiesto usa la fecha de modificación del archivo.
13. **No son datos de la base principal del equipo.** Antes de la defensa hay que
    exportar desde la base del equipo y actualizar `entrada_acc/ORIGEN.txt`.

## DataFrames de análisis (fase 2)

Los construye `analiticas.py` solo con las filas válidas (`calidad.py` ya ha apartado
las rechazadas). Cada cruce declara su cardinalidad con `validate=` y comprueba con
`indicator=True` que todas las filas encuentran pareja: si un cruce multiplicara
filas o perdiera claves, el programa se para con un error.

### df_lineas_enriquecidas: una fila por línea de pedido

| Cruce | Cardinalidad | Qué añade |
|---|---|---|
| líneas → pedidos (`id_pedido`) | muchos a uno | `referencia`, `fecha_pedido`, `tipo_pedido`, `estado_pedido`, `estado_pago`, `id_cliente` |
| → clientes (`id_cliente`) | muchos a uno | `nombre_cliente`, `tipo_cliente` |
| → modelos (`id_modelo`) | muchos a uno | `nombre_modelo` |
| → stock (`sku`) | muchos a uno | `color` (vacío en líneas sin SKU, como las X-NOVA) |

Columnas: `id_linea`, `id_pedido`, `referencia`, `fecha_pedido`, `anio`, `mes`,
`anio_mes`, `trimestre`, `dia_semana`, `id_cliente`, `nombre_cliente`, `tipo_cliente`,
`tipo_pedido`, `es_custom`, `estado_pedido`, `es_cancelado`, `estado_pago`,
`id_modelo`, `nombre_modelo`, `sku`, `color`, `talla`, `cantidad`, `precio_unitario`,
`importe_linea`, `participacion_linea` (26).

### df_pedidos_unicos: una fila por pedido

| Cruce | Cardinalidad | Qué añade |
|---|---|---|
| pedidos → clientes (`id_cliente`) | muchos a uno | `nombre_cliente`, `tipo_cliente` |
| → métricas de sus líneas (`id_pedido`) | uno a uno | `num_lineas`, `pares`, `importe`, `num_modelos`, `num_tallas`. Un pedido sin líneas se queda, con 0 |

Columnas: `id_pedido`, `referencia`, `fecha_pedido`, `anio`, `mes`, `anio_mes`,
`trimestre`, `dia_semana`, `antiguedad_dias`, `id_cliente`, `nombre_cliente`,
`tipo_cliente`, `tipo_pedido`, `es_custom`, `personalizacion`, `estado_pedido`,
`es_cancelado`, `es_confirmado`, `estado_pago`, `num_lineas`, `num_modelos`,
`num_tallas`, `pedido_multimodelo`, `modelo_pedido`, `pares`, `importe`,
`precio_medio_par`, `cantidad_total`, `importe_total` (29).

`pares` e `importe` salen de las líneas, como pide la rúbrica. `cantidad_total` e
`importe_total` son los de la cabecera de Acceso a Datos y se dejan para
contrastar; la regla 12 comprueba que coinciden. Los cancelados **no se eliminan**:
siguen en la actividad, marcados con `es_cancelado`, y cada cálculo decide si los
cuenta.

## Variables derivadas

Todas están en `analiticas.py`. Las de calendario las calcula una sola función,
`anadir_calendario`, para las dos tablas: así no hay dos fórmulas para lo mismo.

| Variable | Dónde | Cálculo | Unidad | Nivel | Disponible | Para qué sirve |
|---|---|---|---|---|---|---|
| `anio` | `anadir_calendario` | año de `fecha_pedido` | año | línea y pedido | al crear el pedido | agrupar por año |
| `mes` | `anadir_calendario` | mes de `fecha_pedido` | 1–12 | línea y pedido | al crear el pedido | estacionalidad |
| `anio_mes` | `anadir_calendario` | `AAAA-MM` | periodo | línea y pedido | al crear el pedido | series mensuales |
| `trimestre` | `anadir_calendario` | trimestre de `fecha_pedido` | 1–4 | línea y pedido | al crear el pedido | evolución trimestral |
| `dia_semana` | `anadir_calendario` | `lunes`…`domingo` | día | línea y pedido | al crear el pedido | patrones semanales |
| `antiguedad_dias` | `df_pedidos_unicos` | `fecha_corte` − `fecha_pedido` | días | pedido | en la fecha de corte | pedidos pendientes antiguos, recencia (RFM). No sirve como predictor del mes que se predice: depende del corte |
| `num_lineas` | `df_pedidos_unicos` | número de líneas | líneas | pedido | al cerrar el pedido | ver que un pedido de 3 líneas es **un** pedido |
| `num_modelos` | `df_pedidos_unicos` | modelos distintos | modelos | pedido | al cerrar el pedido | detectar pedidos mixtos |
| `num_tallas` | `df_pedidos_unicos` | tallas distintas | tallas | pedido | al cerrar el pedido | reparto de tallas de un encargo |
| `pares` | `df_pedidos_unicos` | suma de `cantidad` de sus líneas | pares | pedido | al cerrar el pedido | pares por pedido |
| `importe` | `df_pedidos_unicos` | suma de `importe_linea` | euros (IVA pendiente de confirmar) | pedido | al cerrar el pedido | ticket por pedido |
| `precio_medio_par` | `df_pedidos_unicos` | `importe` / `pares`; nulo si no hay pares | €/par | pedido | al cerrar el pedido | comparar Custom y estándar |
| `pedido_multimodelo` | `df_pedidos_unicos` | `num_modelos` > 1 | sí/no | pedido | al cerrar el pedido | saber cuándo no hay un único modelo |
| `modelo_pedido` | `df_pedidos_unicos` | el modelo si todas las líneas son del mismo; **nulo si hay varios** | texto | pedido | al cerrar el pedido | agrupar pedidos de un solo modelo sin inventar uno |
| `es_custom` | las dos tablas | `tipo_pedido == "custom"` | sí/no | línea y pedido | al crear el pedido | peso de Custom |
| `es_cancelado` | las dos tablas | estado en `ESTADOS_CANCELADOS` | sí/no | línea y pedido | cuando cambia el estado | excluir de ventas sin borrar de la actividad |
| `es_confirmado` | `df_pedidos_unicos` | estado en `ESTADOS_CONFIRMADOS` | sí/no | pedido | cuando cambia el estado | criterio de venta del apartado 6.5 |
| `participacion_linea` | `df_lineas_enriquecidas` | `importe_linea` / importe de su pedido | 0–1 | línea | al cerrar el pedido | qué parte del pedido supone cada línea |

**No se ha fabricado ningún valor.**
- **Margen:** no hay coste, así que no hay variable de margen.
- **Categoría:** no hay categoría de modelo, así que no hay variable de categoría.
- **Pedidos con varios modelos:** no se les asigna ninguno.

**Importante para la predicción (fase 5):** `es_cancelado` y `es_confirmado`
dependen del estado en el momento del corte. `antiguedad_dias` depende de la
fecha de corte. No se pueden usar para predecir un mes sin comprobar que no
filtran información futura. En la fase 5 no son variables de entrada:
`es_cancelado` solo decide qué pares cuentan como demanda (ver la limitación en
`segmentacion_y_prediccion.md`).
