# Resultados SQL para la conciliación

`P-A.csv`, `P-B.csv` y `P-C.csv` son el resultado de las consultas P-A, P-B y P-C
de `02_Acceso_Datos/sql/12_consultas_panel.sql`, copiadas tal cual del archivo y
ejecutadas con `psql --csv`.

**Origen: base de PRUEBA**, no la base principal del equipo. Es la misma base
de prueba de la que salen los cinco CSV de `entrada_acc/`. Se reconstruyó desde
cero con los scripts 1–17 el 9 de noviembre de 2026, y su nueva exportación era
idéntica a la de `entrada_acc/` salvo `fecha_pedido` y `fecha_corte`, que son la
hora de la reconstrucción. Estas tres consultas no usan fechas.

`N-1.csv`, `N-2.csv` y `N-3.csv` son las tres consultas del caso N (ingresos de
2026-11, matriz talla × modelo y clientes únicos), del bloque «CASO N» del mismo
archivo. Se ejecutaron el 13 de noviembre de 2026 en otra base de PRUEBA
montada igual, con los scripts 1–17. Su exportación era idéntica a la de
`entrada_acc/` salvo `fecha_pedido` y `fecha_corte`, que caen en el mismo mes,
y en ella P-A, P-B y P-C daban exactamente estos mismos archivos.

Cómo se repite con otra base: ver `../../conciliacion_sql.md`.
