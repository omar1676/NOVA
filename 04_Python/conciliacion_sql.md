# Conciliación con SQL (fase 2)

Python calcula pedidos, pares e importes con pandas y los compara con tres
consultas que ya existían en Acceso a Datos (`02_Acceso_Datos/sql/12_consultas_panel.sql`,
sin cambiar nada). Con la exportación de prueba del 9 de noviembre de 2026
**coinciden las 21 cifras comparadas**. Resultado completo en
`outputs/real/conciliacion_sql.csv`.

## Las tres consultas y en qué se diferencian de Python

| Consulta (línea en el `.sql`) | Qué calcula SQL | Qué calcula Python | Diferencias de definición |
|---|---|---|---|
| P-A (129) | `count(*)`, `sum(cantidad_total)` y `sum(importe_total)` de los pedidos con `estado <> 'cancelado'` | filas de `df_pedidos_unicos` con `es_cancelado = False`; pares e importe sumados desde sus líneas | SQL usa los **totales de la cabecera**; Python suma **las líneas**. SQL cuenta **todos** los pedidos de la base; Python, solo los **válidos** |
| P-B (138) | por estado: `count(*)`, `sum(cantidad_total)` y `sum(importe_total)` de todos los pedidos, también los cancelados | `df_pedidos_unicos` agrupado por `estado_pedido`; pares e importe desde las líneas | las mismas que P-A |
| P-C (149) | por `COALESCE(modelo, 'X-NOVA')`: `SUM(cantidad)` y `COUNT(DISTINCT id_pedido)` de las líneas de pedidos no cancelados | `df_lineas_enriquecidas` sin cancelados, agrupado por `nombre_modelo`: suma de `cantidad` y `nunique` de `id_pedido` | SQL llega al modelo por SKU → variante → modelo; Python, por el `id_modelo` que trae `lineas_pedido.csv` (en X-NOVA, el exportador pone el modelo X-NOVA). Python solo usa líneas válidas |

**Por qué se pueden comparar igualmente:**
- **Cabecera y líneas:** la regla 12 comprueba que la cabecera es la suma de sus líneas, así que dan lo mismo.
- **Todos y válidos:** solo difieren si se rechaza alguna fila. Con esta exportación no se rechaza ninguna. Si se rechazara, la diferencia sería exactamente la de las filas de `filas_rechazadas.csv`.

## Resultado

| Consulta | Cifras | Coinciden |
|---|---|---|
| P-A: 12 pedidos no cancelados, 90 pares, 10.686,45 € | 3 | 3 |
| P-B: pendiente (11 pedidos, 50 pares, 5.890,45 €) y confirmado (1, 40, 4.796,00 €) | 6 | 6 |
| P-C: 6 modelos × pares y pedidos (NOVA Velocity: 82 pares en 4 pedidos) | 12 | 12 |

Los euros se dan por iguales con medio céntimo de diferencia; el resto tiene que
ser exacto. Si una cifra no coincide, sale `NO COINCIDE` y `main.py` termina con
código 1. Si un estado o un modelo solo está en un lado, sale `falta en SQL` o
`falta en Python`. Las pruebas comprueban los cuatro casos con datos inventados.

## Caso N: ingresos de un mes, matriz talla × modelo y clientes únicos

La rúbrica pide «contrastar por SQL los ingresos de un mes, la matriz talla ×
modelo y el número de clientes únicos; explicar discrepancias y correcciones».
Son tres consultas nuevas, N-1, N-2 y N-3, al final de
`02_Acceso_Datos/sql/12_consultas_panel.sql` (bloque «CASO N»). Python las compara en
`conciliacion.contrastar_caso_n` y guarda `outputs/real/contraste_sql_caso_n.csv`.
En el dashboard salen en la misma tabla de conciliación de la pestaña Calidad.

| Consulta | Qué calcula SQL | Qué calcula Python | Diferencias de definición |
|---|---|---|---|
| N-1 · ingresos de un mes | `count(*)`, `sum(cantidad_total)` y `sum(importe_total)` de los pedidos confirmados en adelante cuyo `to_char(fecha_pedido, 'YYYY-MM')` es el mes pedido (`mes_contraste`) | la fila de ese mes en `ventas_por_periodo`; si el mes no tiene ventas, 0 | cabecera frente a líneas (la regla 12 dice que coinciden); todos los pedidos frente a los válidos |
| N-2 · matriz talla × modelo | por `COALESCE(modelo, 'X-NOVA')` y `COALESCE(talla del SKU, talla de la configuración)`: `SUM(cantidad)` de las líneas de pedidos no cancelados | cada celda distinta de 0 de `matriz_modelo_talla`, como «modelo · talla» | SQL llega al modelo y a la talla por el SKU; Python, por las columnas de `lineas_pedido.csv` (que el 16 saca con la misma regla) |
| N-3 · clientes únicos | `count(DISTINCT id_cliente)` de los pedidos: todos, no cancelados y confirmados en adelante | `nunique` de `id_cliente` en `df_pedidos_unicos` con los mismos tres criterios | todos los pedidos frente a los válidos |

**Resultado con la exportación de prueba: coinciden las 17 cifras.**
- N-1 (2026-11): 1 pedido, 40 pares y 4.796,00 €. Es CUSTOM-40; NOVA-0011 está
  pendiente y no cuenta como venta.
- N-2: 11 celdas. NOVA Velocity tiene 20, 21, 20 y 21 pares en las tallas 40 a 43.
- N-3: 6 clientes con pedidos, 6 con demanda y 1 con venta.

**Discrepancias que pueden salir y cómo se corrigen:**
- **Criterio distinto en cada lado.** Si una consulta cuenta como «ingresos» los
  pedidos no cancelados (el criterio de P-A), entran los pendientes y el importe no
  cuadra. Si la matriz no quita los cancelados, sobra una celda («falta en Python»).
  Corrección: los dos lados usan los mismos estados de `config.py`. La prueba
  `test_discrepancias_detectadas` lo provoca a propósito.
- **Otro mes.** Las fechas de una base reconstruida son la hora de la carga. Si la
  base se monta otro mes, N-1 hay que lanzarla con el mes de la exportación
  (`\set mes_contraste 'AAAA-MM'`).
- **Filas rechazadas.** SQL cuenta todos los pedidos y Python solo los válidos. Si
  la calidad rechaza alguno, la diferencia son exactamente las filas de
  `filas_rechazadas.csv`.
- **La base cambia entre la exportación y las consultas.** Hay que repetir las dos
  cosas seguidas.

Si alguna cifra no coincide, `main.py` termina con código 1 y el estado es
`NO CUADRA CON SQL`, igual que con P-A a P-C.

## De dónde salen los resultados SQL

Python no se conecta a PostgreSQL. Los resultados están en
`entrada_acc/conciliacion_sql/` (`P-A.csv`, `P-B.csv` y `P-C.csv`) y salen de la
**misma base de prueba** que los cinco CSV, no de la base principal del equipo.

La base de prueba es un clúster temporal, distinto del PostgreSQL del equipo:
1. Se reconstruyó desde cero con los scripts 1–17.
2. Se comprobó que su nueva exportación era idéntica a la de `entrada_acc/` salvo
   `fecha_pedido` y `fecha_corte`, que son la hora de la reconstrucción.
3. Se ejecutaron las tres consultas, copiadas tal cual del archivo.

Ninguna de las tres usa fechas. N-1, N-2 y N-3 se sacaron el 13 de noviembre de
2026 de otra base de prueba montada igual, con los scripts 1–17 de la candidata.
Su exportación también era idéntica a la de `entrada_acc/` salvo esas dos fechas,
que caen en el mismo mes (2026-11), y P-A, P-B y P-C salían iguales byte a byte.

Para repetirlo con la base del equipo, en el mismo momento en que se exporten los
cinco CSV:

```
cd 04_Python\entrada_acc\conciliacion_sql
```

Copiar en tres archivos `P-A.sql`, `P-B.sql` y `P-C.sql` el `SELECT` de cada
consulta de `12_consultas_panel.sql`, tal cual, y lanzar (lo mismo con `N-1`,
`N-2` y `N-3`; delante del `SELECT` de N-1 va `\set mes_contraste 'AAAA-MM'`):

```
psql -U postgres -d nova_sneakers --csv -f P-A.sql > P-A.csv
psql -U postgres -d nova_sneakers --csv -f P-B.sql > P-B.csv
psql -U postgres -d nova_sneakers --csv -f P-C.sql > P-C.csv
```

Si la base cambia entre la exportación y las consultas, las cifras no cuadrarán.
No es un error de Python: hay que volver a hacer las dos cosas seguidas.

**Nota:** el `ORDER BY` de P-C tiene un criterio de desempate que está en los
cambios locales de Java/SQL pendientes de revisar por Berme (M2). Solo cambia el
orden de las filas, no los valores.
