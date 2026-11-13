# Odoo y SO024: preparación conservada y límites de la entrega

> **Archivo histórico.** El caso de entrega es [S00005 del Club Atlético NOVA](../CASO_COMUN_S00005.md). El plan SO024 siguiente queda sustituido y no se ejecuta. Se conserva para documentar la preparación y los ensayos anteriores, sin atribuirlos a S00005.

**Cierre del 13/11/2026:** este plan se conserva como explicación técnica. No se ejecutará una nueva integración en esta entrega, no se esperan más archivos y no se fijan datos oficiales. Las consultas no se ejecutaron sobre la base del equipo. El guion disponible usa CUSTOM-40 y evidencia documental de Odoo.

Revisión del 13/11/2026 sobre `revision/incorporar-limpieza-main-20261113`, base de código `d24fa27`, descendiente de `a6151db`.

**Estado: documentación recibida; conciliación del SO024 oficial pendiente.** El equipo confirma que los datos definitivos siguen sin acordarse. Este documento no fija esos datos, no activa la API y no modifica ninguna base.

## 1. Fuente y alcance

La fuente es [el PDF de Berme](../../odoo/documentacion/Odoo-NOVA-Sneakers.pdf), 19 páginas. Su blob `466a4e32fb0709445186f339de44abf571fc56fe` coincide con el PDF de `origin/feature/berme` (ruta original con «documentación») y con el que ya está en main. No hay que copiarlo otra vez ni integrar toda la rama antigua del compañero.

El documento acredita aportaciones de Odoo con capturas; no constituye una prueba ejecutada sobre esta candidata. Aquí se revisaron el texto y las páginas 10, 16 y 17 renderizadas. No se accedió a la instancia de OrbStack.

| Evidencia aportada | Páginas | Qué queda por comprobar para SO024 |
|---|---|---|
| Ubuntu 24.04 en OrbStack, Odoo 19 Community y servicio | 3–6 | Reproducibilidad/acceso desde el equipo de la demo; backup y restauración |
| Runner X y fabricación de prueba | 7–9 | Variante y cantidades oficiales por talla |
| Venta S00005, fabricación WH/MO/00002 y entrega WH/OUT/00005 | 10–11 | Es del Club Atletico NOVA; no demuestra el pedido del Club Halcones |
| Factura INV/2026/00001 y pago | 12 | No reutilizar como factura de SO024 ni alterar el documento histórico |
| Pedidos por API y referencias del cliente | 13–15 | Compatibilidad con las rutas/roles de esta candidata y con los códigos reales |
| Nueve variantes 38–46, referencias internas y usuarios | 16–17 | Resolver la colisión de códigos y los permisos completos de la rúbrica |
| Resumen de tareas OD-01 a OD-06 | 18 | No equivale a cerrar todos los requisitos de SGE ni SO024 |

## 2. Diferencias que impiden declarar la integración terminada

| Campo | PDF de Berme | Candidata / caso común | Conclusión |
|---|---|---|---|
| Cliente del pedido demostrado | Club Atletico NOVA | Club Halcones para SO024 | Son casos diferentes |
| Pedido demostrado | S00005, una línea de 40 pares | SO024, reparto acordado en tallas 38–46 | No hay equivalencia acreditada S00005 ↔ SO024 |
| Precio de esa venta | 89,00 €/par; 3.560,00 € sin IVA; 4.307,60 € con IVA | Precio oficial e IVA pendientes | No rehacer ni renombrar la venta histórica para forzar una coincidencia |
| Precio posterior del producto | 99,90 €/par (p. 17; la captura de variantes p. 16 aún muestra 89 €) | 99,90 € fue un valor provisional en los ensayos | Verificar precio actual y acordar criterio; el documento refleja momentos distintos |
| Stock mostrado después de variantes | 51 pares en talla 40, cero en las demás | El script 18 prepara stock por talla según el dato acordado | No basta para demostrar la entrega del reparto oficial |
| Referencias Runner X | NOVA-4-38 … NOVA-4-46 | Runner X usa NOVA-<id_variante>-<talla>; el ID depende del montaje | Falta la exportación de la base del equipo |
| Modelo asociado a parte de esos códigos | Runner X en Odoo | NOVA-4-40 … 43 son NOVA Velocity en los fixtures y resultados existentes | Conflicto semántico: el mismo texto puede seleccionar otro producto |

La colisión se comprueba en `03_PSP/datos/custom40_fabricacion_psp.csv` y en `06_Intermodular/evidencias/regresion-limpieza/01_sql/04_06_consultas.txt`. Es evidencia del repositorio, no una consulta a la base viva. Los ID 14, 26 o 114 de ensayos anteriores tampoco son identificadores oficiales para copiar.

## 3. Tabla de conciliación de Runner X

Los códigos de la segunda columna son los **observados en el PDF**, no una propuesta de reemplazo de PostgreSQL. No rellenar la tercera por similitud de números.

| Talla | Odoo observado (p. 16) | SKU real en PostgreSQL del equipo | Decisión acordada |
|---|---|---|---|
| 38 | NOVA-4-38 | PENDIENTE DE EXPORTACIÓN | PENDIENTE |
| 39 | NOVA-4-39 | PENDIENTE DE EXPORTACIÓN | PENDIENTE |
| 40 | NOVA-4-40 | PENDIENTE DE EXPORTACIÓN | PENDIENTE |
| 41 | NOVA-4-41 | PENDIENTE DE EXPORTACIÓN | PENDIENTE |
| 42 | NOVA-4-42 | PENDIENTE DE EXPORTACIÓN | PENDIENTE |
| 43 | NOVA-4-43 | PENDIENTE DE EXPORTACIÓN | PENDIENTE |
| 44 | NOVA-4-44 | PENDIENTE DE EXPORTACIÓN | PENDIENTE |
| 45 | NOVA-4-45 | PENDIENTE DE EXPORTACIÓN | PENDIENTE |
| 46 | NOVA-4-46 | PENDIENTE DE EXPORTACIÓN | PENDIENTE |

### Consultas preparadas de solo lectura (no ejecutadas en esta revisión)

Ejecutar sobre la base del equipo elegida, sin reinstalarla, cuando se autorice obtener su inventario. Guardar fecha y nombre de la base junto con el resultado; sin contraseñas.

```sql
BEGIN READ ONLY;

-- Referencias reales de Runner X: no se presupone un id_variante.
SELECT m.nombre AS modelo, m.precio_base, v.id_variante, v.color,
       s.talla, s.sku
FROM public.modelos m
JOIN public.variantes v USING (id_modelo)
JOIN public.producto_sku s USING (id_variante)
WHERE m.nombre = 'Runner X'
ORDER BY v.color, s.talla;

-- Qué modelo ocupa los códigos usados en el PDF.
SELECT s.sku, m.nombre AS modelo, v.color, s.talla
FROM public.producto_sku s
JOIN public.variantes v USING (id_variante)
JOIN public.modelos m USING (id_modelo)
WHERE s.sku LIKE 'NOVA-4-%'
ORDER BY s.talla;

-- Stock por almacén: no sumar ni confundir una foto con stock inicial.
SELECT s.sku, s.talla, n.nombre AS almacen, e.cantidad
FROM public.producto_sku s
JOIN public.variantes v USING (id_variante)
JOIN public.modelos m USING (id_modelo)
JOIN public.existencias e USING (id_producto_sku)
JOIN public.nave n USING (id_nave)
WHERE m.nombre = 'Runner X'
ORDER BY s.talla, n.nombre;

ROLLBACK;
```

En Odoo, Berme debe exportar `product.product`: referencia interna (`default_code`), producto, talla, color si existe, activo/archivado, precio y stock, usando un identificador estable de variante. Debe incluir también los productos archivados con códigos repetidos para distinguirlos de los activos.

### Decisión de códigos

El conector actual busca igualdad exacta por `default_code`; no aplica una tabla de equivalencias. Para usarlo, cada código enviado tiene que corresponder al mismo modelo, talla y color en ambos sistemas, sin ambigüedad entre productos activos.

- Opción simple, tras acuerdo: mantener los SKU reales de PostgreSQL y hacer coincidir las referencias de las variantes correctas de Odoo, con un plan que preserve las ventas y referencias históricas. No tocar NOVA Velocity ni reutilizar sus códigos para otro modelo.
- Si se conservan códigos diferentes: documentar la equivalencia y, antes de activar la API, implementar y probar una traducción explícita. La tabla de este documento por sí sola no cambia el conector.

No se ha elegido ninguna opción ni cambiado un SKU. No se debe reconstruir la base para intentar que aparezca el número 4.

## 4. Los siete acuerdos de SO024

La confirmación del equipo en esta revisión es que **siguen pendientes**. La fuente de acuerdos sigue siendo [caso-comun-SO024.md](caso-comun-SO024.md), no las cifras del PDF ni las de un ensayo.

1. Reparto entero entre tallas 38–46, con total 40.
2. Color de Runner X.
3. Precio y criterio de IVA común a Odoo, PostgreSQL y Python.
4. Stock inicial por talla y almacén; no confundirlo con el stock final de 51 pares del PDF.
5. Texto de personalización.
6. Códigos de variante tras completar la tabla anterior.
7. Número de venta de Odoo y cómo se vincula mediante `client_order_ref = SO024`.

También faltan fecha objetivo y contacto ficticio del Club Halcones, según el documento de pendientes. Esta restricción del plan anterior queda descartada: el equipo elige S00005 como caso de Odoo. CUSTOM-40 sigue siendo una prueba independiente, sin equivalencia acreditada con S00005.

## 5. Ruta de aceptación del caso común

| Paso | Responsable de aportar/confirmar | Criterio para cerrarlo |
|---|---|---|
| Acordar los siete datos | Los tres | Valores escritos en caso-comun-SO024.md |
| Exportar catálogo real y resolver códigos | Base del equipo + Berme | Nueve tallas del color elegido; cada código identifica el mismo producto en ambos sistemas |
| Preparar Odoo | Berme | Club Halcones, variantes, permisos, componentes y stock acordados; sin alterar la venta histórica |
| Crear el pedido oficial | Berme y quien haga la demo Java | Referencia SO024; mismo reparto y personalización; número S… apuntado como equivalencia |
| Fabricar, entregar y facturar | Berme | Documentos enlazados al nuevo pedido y estados demostrados; IVA documentado |
| Exportar el pedido de Odoo | Berme | CSV del SO024 real, con referencia, SKU, cliente, modelo, color, personalizacion, talla y cantidad |
| Conciliar Java/PostgreSQL, PSP y Python | Los tres | Totales, nueve tallas según el acuerdo, importes bajo el mismo criterio; stock descontado una vez; PSP código 0; Python cuenta un pedido |
| Evidencias y recuperación | Los tres | Tabla final de caso-comun completada, memoria actualizada, backup externo identificado y restauración probada |

Las pruebas sobre el ensayo provisional siguen siendo evidencia del ensayo, no del pedido oficial. No crear documentos históricos retroactivos ni cambiar sus importes.

## 6. API de Odoo: preparación separada del flujo manual

El PDF muestra pruebas por API en el entorno de Berme, pero esta candidata mantiene `servidor-admin/pedidos.js` sin montar. Sus rutas escriben directamente en pedidos y log_eventos y no encajan con los roles actuales. `servidor-admin/odoo.js` requiere configuración explícita; no se ha activado ni llamado aquí.

No basta con poner una clave en .env: antes hay que resolver los códigos, revisar autorización/auditoría y probar errores, reintentos e importes contra la instancia real. No restaurar los valores por defecto ni las rutas antiguas copiando la rama completa del compañero. El recorrido manual y el CSV permiten preparar SO024 sin abrir esa vía de escritura.

## 7. Trabajo remoto ya localizado

- El PDF de `origin/feature/berme` es idéntico al de main; no hace falta volver a incorporarlo.
- Berme ya tiene un arreglo del comprobador PSP, `0baf61f`. La corrección se incorporó en el cierre como `4f09742`, conservando autor y fecha originales, sin traer la rama completa. Se revisó y aplicó de forma aislada, conservando su autoría y las rutas actuales, sin incorporar su rama entera. El comprobador y las pruebas principales de PSP pasan en el cierre.
- `777868a` y `d24fa27` permanecen intactos. Toda esta preparación se hace en la misma candidata, sin ramas nuevas, sin merge y sin push.
