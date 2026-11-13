# Calidad de los datos (fase 2)

`calidad.py` aplica las doce reglas del apartado 6.2 de la rúbrica a los cinco CSV
y genera `incidencias.csv`, `resumen_calidad.csv` y `filas_rechazadas.csv` en
`outputs/real/`. Con la exportación de prueba del 9 de noviembre de 2026 hay **2
incidencias, las dos advertencias**, y ninguna fila rechazada: la calidad es del
100 % en las cinco tablas. Las 61 pruebas nuevas meten cada fallo a propósito
para comprobar que se detecta.

## Gravedad y tratamiento

| Gravedad | Tratamiento | Cuándo |
|---|---|---|
| bloqueante | se detiene: no se publica ninguna cifra | el conjunto no es fiable: falta un archivo o una columna, hay un id repetido, una clave huérfana o un stock de dos exportaciones (apartado 6.14) |
| recuperable | se rechaza la fila y se aparta en `filas_rechazadas.csv` | la fila no se puede usar, pero el resto sí |
| advertencia | la fila se queda y se avisa | hay algo raro que no cambia las cifras, o un dato que no se usa en los cálculos |

**Un pedido se analiza entero o no se analiza.** Si se rechaza una línea, se
rechaza su pedido con todas sus líneas, y si se rechaza un pedido, también sus
líneas. Así nunca se cuenta un pedido a medias. El stock rechazado no arrastra a
las líneas, porque es una foto aparte.

**Nunca se corrige ni se inventa un valor.** Un nulo no pasa a ser 0, un estado
mal escrito («Confirmado») no se arregla solo y no se borra ningún duplicado sin
saber qué identifica la fila. Cada incidencia guarda el valor tal como venía en
el CSV.

## Las doce reglas

| Regla | Qué comprueba | Gravedad |
|---|---|---|
| 01 · Fichero vacío o cabeceras insuficientes | El archivo existe, no está vacío, es UTF-8, es un CSV correcto y tiene las columnas obligatorias | bloqueante; con solo la cabecera, advertencia |
| 02 · IDs duplicados donde deban ser únicos | `id_cliente`, `id_modelo`, `id_pedido`, `referencia`, `id_linea` y `sku` (stock) no se repiten. Un id vacío no identifica la fila | repetido: bloqueante; vacío: recuperable |
| 03 · Claves huérfanas en líneas o pedidos | `pedidos.id_cliente`, `lineas.id_pedido`, `lineas.id_modelo`, `lineas.sku` y `stock.id_modelo` existen en su tabla | bloqueante |
| 04 · Fecha nula o imposible | `fecha_pedido` y `fecha_corte` existen y son fechas reales en `AAAA-MM-DD HH:MM:SS` | recuperable |
| 05 · Cantidad nula, cero o negativa | `lineas.cantidad` es un entero mayor que 0; `pedidos.cantidad_total` es un entero no negativo | recuperable |
| 06 · Precio no numérico o negativo | `precio_unitario`, `importe_linea` e `importe_total` son números con punto decimal y no negativos | recuperable; `precio_base` (no se usa en ventas): advertencia |
| 07 · Estado fuera del catálogo acordado | `estado_pedido` y `tipo_pedido` están en el catálogo de `config.py` (CHECK de la base) | recuperable; `estado_pago` y tipo de cliente: advertencia |
| 08 · Talla no válida según el contrato | La talla de cada línea es la de su SKU en `stock.csv` (el contrato pide que la talla sea válida para el modelo) y está entre 20 y 55 (CHECK de la base) | recuperable |
| 09 · Ausencia de cliente o modelo | `pedidos.id_cliente`, `lineas.id_modelo` y `stock.id_modelo` no están vacíos | recuperable; cliente o modelo sin nombre: advertencia |
| 10 · Duplicidad de líneas según clave documentada | Clave: pedido + SKU (en X-NOVA, sin SKU: pedido + modelo + talla). El contrato dice «cada talla aparecerá en una línea diferente» | advertencia: las dos líneas tienen su id y su importe, y el total del pedido las suma |
| 11 · Stock negativo o duplicado por modelo-talla | `stock_disponible` es un entero no negativo, y no hay dos SKU con el mismo modelo, **color** y talla | recuperable |
| 12 · Conflicto entre fechas o incoherencia comercial | Ver la lista de abajo | según el caso |

La regla 11 de la rúbrica habla de «modelo-talla», pero `stock.csv` tiene una fila
por color: un mismo modelo y talla aparece una vez por cada color, y eso es
correcto. La clave real es modelo + color + talla, que es lo que identifica el SKU.

La regla 12 comprueba:

- un pedido no puede ser posterior a la exportación (`fecha_corte`): recuperable;
- `stock.csv` tiene una sola `fecha_corte`; si mezcla dos, no es una sola foto: bloqueante;
- `importe_linea` = `cantidad` × `precio_unitario`: recuperable;
- `cantidad_total` e `importe_total` = suma de sus líneas: recuperable;
- un pedido sin líneas: advertencia (y si su cabecera dice que tiene pares, recuperable);
- un `custom` sin personalización o un `normal` con ella: advertencia;
- `reembolsado` en un pedido que no está cancelado: advertencia;
- dos pedidos del mismo cliente con exactamente las mismas líneas (SKU y cantidad):
  advertencia de posible pedido repetido. **No se borra**: que coincidan no demuestra
  que lo sean.

## Columnas de los CSV de calidad

Todos llevan delante `origen` (por ejemplo «ACC · PRUEBA (base de prueba: no son
ventas reales)») y `ejecucion` (fecha y hora del cálculo). Están en UTF-8 sin BOM,
con cabecera y separados por comas.

- **`incidencias.csv`**: `regla`, `nombre_regla`, `tabla`, `registro` (el id de la fila),
  `fila` (1 = la primera después de la cabecera; vacía si afecta al archivo
  entero), `columna`, `valor` (tal como venía), `gravedad`, `tratamiento` y
  `detalle`.
- **`resumen_calidad.csv`**: por tabla, `estado`, `filas_entrada`, `filas_validas`,
  `filas_rechazadas`, `porcentaje_calidad` (válidas / entrada) y el número de
  incidencias de cada gravedad.
- **`filas_rechazadas.csv`**: `tabla`, `fila`, `registro` y el `motivo`.

## Resultado con la exportación de prueba

| Tabla | Filas | Válidas | Rechazadas | Calidad | Incidencias |
|---|---|---|---|---|---|
| clientes | 6 | 6 | 0 | 100 % | 0 |
| modelos | 7 | 7 | 0 | 100 % | 0 |
| pedidos | 12 | 12 | 0 | 100 % | 2 advertencias (regla 12) |
| lineas_pedido | 18 | 18 | 0 | 100 % | 0 |
| stock | 60 | 60 | 0 | 100 % | 0 |

Es lo esperable: la base tiene restricciones (CHECK, claves ajenas) y el exportador
comprueba los totales antes de exportar. Los fallos aparecen cuando alguien edita un
CSV o cuando una exportación se corta.

## Casos investigados

### A. NOVA-0011 y CUSTOM-40

`analiticas.comparar_pedidos` los pone lado a lado:

| | NOVA-0011 | CUSTOM-40 | ¿Igual? |
|---|---|---|---|
| id_pedido | 11 | 46 | no |
| Cliente | 6, Club Atletico NOVA | 6, Club Atletico NOVA | sí |
| Fecha | 2026-11-09 19:12:52 | 2026-11-09 19:12:54 | no |
| Estado | pendiente | confirmado | no |
| Personalización | «Pedido de club: 40 pares repartidos en cuatro tallas» | «Club Atletico NOVA: logo bordado y numeracion en el talon» | no |
| Líneas | 11, 12, 13, 14 | 54, 55, 56, 57 | no |
| Artículos | NOVA-4-40 a 43, 10 de cada | NOVA-4-40 a 43, 10 de cada | sí |
| Precio por par | 119,90 € | 119,90 € | sí |
| Pares e importe | 40 y 4.796,00 € | 40 y 4.796,00 € | sí |
| Lo crea | `05_datos_prueba.sql` (datos de demostración) | `14_caso_custom_persistente.sql` (caso común) | |

**No comparten ningún identificador**: ni pedido, ni referencia, ni líneas. Son
dos registros distintos que crean dos scripts a propósito, y el 14 dice que deja
«los pedidos NOVA-0001 a NOVA-0011 como estaban». **Sí comparten** cliente,
artículos, cantidades y precio: es posible que representen el mismo encargo del
club cargado dos veces, uno como demostración y otro como caso común. Eso no se
puede saber con los datos: lo tiene que decidir Acceso a Datos. Python mantiene
los dos y la regla 12 los marca con una advertencia. Pesan mucho: son 80 de los
90 pares.

### B. Ventas y estados

`importes_por_criterio.csv` da las tres cifras sin llamar a ninguna «ingresos
cobrados» (eso sería `estado_pago`, y todos los pagos están pendientes):

| Criterio | Definición | Pedidos | Pares | Importe |
|---|---|---|---|---|
| registrados | todos los pedidos válidos | 12 | 90 | 10.686,45 € |
| no cancelados | estado distinto de `cancelado` (panel P-A de Acceso a Datos y contrato) | 12 | 90 | 10.686,45 € |
| confirmados en adelante | `confirmado`, `en_preparacion`, `enviado` o `entregado` (apartado 6.5) | 1 | 40 | 4.796,00 € |

Las dos primeras coinciden porque esta exportación no tiene ningún pedido
cancelado. «Confirmados o entregados» incluye los estados intermedios: si no, un
pedido dejaría de contar como venta al pasar de `confirmado` a `en_preparacion`.
El equipo tiene que elegir el criterio de la memoria y del dashboard.

### C. IVA

Ni el contrato, ni el esquema, ni el diccionario de Acceso a Datos dicen si los
importes llevan IVA. Queda **«pendiente de confirmar»** en `config.py` y en la
columna `iva` de `importes_por_criterio.csv`.

### D. Stock

El SKU identifica modelo + color + talla. La regla 11 busca duplicados por esa
clave, no por modelo + talla, y el stock no se suma entre colores. La rúbrica pide
además un archivo con un ID huérfano, una fecha inválida y un duplicado. Probado
con una copia de `entrada_acc/` (nunca con el original): da tres alertas
independientes (reglas 03, 04 y 02), bloquea la publicación y el original no cambia.
