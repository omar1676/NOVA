# Datos sintéticos (fase 4)

`generador_datos.py` crea un histórico **inventado** de 18 meses con las mismas
columnas que los cinco CSV de Acceso a Datos. Sirve para practicar estadística,
segmentación y predicción con suficientes datos, porque la exportación de prueba
solo tiene 12 pedidos de un día. **No son datos de NOVA ni salen de PostgreSQL**:
todo lo que sale de ellos va etiquetado como SINTÉTICO.

## Cómo se generan

```
cd python-analisis
.venv\Scripts\python.exe generador_datos.py
```

Escribe dos carpetas:

| Carpeta | Contenido |
|---|---|
| `datos_sinteticos/limpios/` | los cinco CSV, sin ningún error, y `ORIGEN.txt` con `Tipo: SINTETICO` |
| `datos_sinteticos/con_errores/` | la misma copia con 12 errores introducidos a propósito, `ORIGEN.txt` y `errores_introducidos.csv` |

**Semilla: 2026** (`config.SEMILLA`). Con la misma semilla salen exactamente los
mismos datos: lo comprueba una prueba automática.

## Lo que se ha generado

| Conjunto | Filas | Mínimo de la rúbrica |
|---|---|---|
| clientes | 40 (10 empresas y 30 particulares) | 40 |
| modelos | 12 | 12 |
| pedidos | 900 | 800 |
| líneas de pedido | 1.777 (1,97 por pedido) | 1.600 |
| stock | 216 SKU (12 modelos × 2 colores × 9 tallas), 6.500 pares | — |

- **Periodo:** 18 meses seguidos, del **1 de mayo de 2025 al 31 de octubre de 2026**. Cada mes tiene entre 26 y 77 pedidos.
- **Fecha de corte:** 1 de noviembre de 2026 a las 00:00.
- **Estados:** 784 entregados, 70 cancelados, 25 enviados, 12 confirmados, 8 pendientes y 1 en preparación.
- **Pagos:** 809 pagados, 54 pendientes y 37 reembolsados.
- **Tipos:** 760 pedidos normales y 140 Custom.
- **Volumen:** 7.637 pares y 917.025,52 € registrados.

## Hipótesis de la simulación

Son reglas **inventadas** para que los datos tengan variedad, pero **no describen
la demanda real**. Están al principio de `generador_datos.py`.

| Qué | Regla |
|---|---|
| Clientes | 10 empresas (clubes) y 30 particulares; unos compran más que otros (peso 1 / posición^0,7) |
| Modelos | 12, con popularidad 1 / posición: el modelo 1 es el más pedido. Precio de catálogo entre 69,99 y 139,99 € |
| Tallas | de la 38 a la 46, más pedidas las centrales (20 % la 42, 3 % la 38) |
| Meses | más pedidos en primavera y en septiembre-octubre, menos en agosto y enero, y un crecimiento del 2 % al mes |
| Custom | 15 % de los pedidos, casi siempre de clubes: un modelo y un color en 2 a 5 tallas, 5 a 20 pares por talla, un 20 % más caros |
| Normales | 1 a 3 líneas de 1 a 3 pares |
| Precios | suben un 5 % en enero de 2026 |
| Estados | el 8 % se cancela; el resto avanza según los días que han pasado hasta el corte |
| Pagos | entregado = pagado; un cancelado puede estar reembolsado; un pendiente no está pagado |

## Por qué los datos limpios no tienen errores

Las reglas de calidad se cumplen por construcción:
- **Líneas:** nunca hay dos con el mismo SKU en un pedido.
- **Importes:** el de la línea es cantidad × precio, y el del pedido es la suma de sus líneas.
- **Pagos:** solo un cancelado puede estar reembolsado.
- **Personalización:** solo la llevan los Custom.
- **Fechas:** ningún pedido es posterior al corte.
- **Duplicados:** ningún cliente repite exactamente el mismo pedido.

Resultado de las 12 reglas: **0 incidencias y 100 % de calidad en las cinco
tablas**.

## La copia con errores

Tiene al menos un fallo de cada regla de la 02 a la 12 (`errores_introducidos.csv`):

| Regla | Error introducido |
|---|---|
| 02 | un pedido repetido con el mismo `id_pedido` |
| 03 | una línea del pedido 99999, que no existe |
| 04 | una fecha imposible, `2026-02-30` |
| 05 | una línea con 0 pares |
| 06 | un precio negativo |
| 07 | el estado `Entregado`, con mayúscula |
| 08 | una línea con una talla que no es la de su SKU |
| 09 | un pedido sin cliente |
| 10 | una línea repetida: mismo pedido y mismo SKU |
| 11 | un stock negativo |
| 12 | un total que no es la suma de sus líneas y un pedido posterior a la exportación |

**Resultado: se detectan las 11 reglas**, con 21 incidencias:
- 3 bloqueantes;
- 14 recuperables;
- 4 advertencias.

Hay más incidencias que errores introducidos porque un mismo error tiene
consecuencias. Por ejemplo, una línea con 0 pares tampoco cuadra con su importe ni
con el total de su pedido, y el pedido repetido sale también como posible pedido
repetido.

Al haber incidencias bloqueantes, `main.py` **no publica ninguna cifra** y lo dice
en `estado_ejecucion.csv`.

La regla 01 (archivo vacío o sin columnas) no puede estar en esta copia: si un
archivo no se puede leer, las demás reglas no se aplican. Se prueba aparte, en
`test_calidad.py`.

## Cómo se separan de los datos de Acceso a Datos

- **Entrada:** `guardar` se niega a escribir en `entrada_acc/` o dentro de ella. Lo comprueba una prueba.
- **Identificadores:** las referencias empiezan por `SINT-` y los modelos por `SINT `, así que una mezcla se vería enseguida.
- **Carpetas:** cada modo de `main.py` tiene las suyas:

| Modo | Lee | Escribe |
|---|---|---|
| `real` (por defecto) | `entrada_acc/` | `outputs/real/` |
| `sintetico` | `datos_sinteticos/limpios/` | `outputs/sinteticos/` |
| `sintetico-errores` | `datos_sinteticos/con_errores/` | `outputs/sinteticos_con_errores/` |

- **Etiquetas:** cada CSV y cada gráfico lleva en su origen «SINTÉTICO (generado por
  Python: no son datos reales)».
- **Conciliación:** con datos sintéticos sale «NO APLICA», porque no hay consultas
  SQL con las que compararlos.

## El mismo programa para los dos tipos de datos

`main.py --modo sintetico` usa exactamente las mismas funciones que con los datos
de prueba: no hay código duplicado. Con ellos funcionan:
- las 12 reglas de calidad;
- los 2 DataFrames principales y todas las tablas analíticas;
- los 20 KPIs, 19 de ellos calculables (la variación mensual y la cobertura ya tienen valor);
- las cohortes;
- los 10 gráficos;
- la estadística.

Al probarlo con 18 meses salieron tres cosas que con un solo día no se veían. Las
he corregido, cada una con su prueba:

1. **Atípicos de precio.** Se comparaban por modelo, y un Custom (+20 %) salía
   como atípico de su propio modelo: había 96 falsas alarmas. Ahora se comparan
   por **modelo y tipo de pedido**.
2. **Gráfico de evolución.** Por día, 540 puntos con su etiqueta no se leían.
   Ahora, si hay dos meses o más, va **por mes**. Con un solo día sigue avisando
   de que no hay evolución.
3. **Gráfico de clientes.** 40 barras no se leían. Ahora enseña los **15 con más
   importe** y lo dice en el subtítulo.
