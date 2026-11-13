# 06 · Proyecto Intermodular

Lo que une las asignaturas: el caso común SO024, la memoria técnica común, los manuales, las matrices de rúbricas, la defensa y la regresión completa.

| | |
|---|---|
| **Qué hace** | Reúne la documentación y las pruebas que no son de una sola asignatura: el pedido SO024 del Club Halcones (Runner X, 40 pares, tallas 38–46) recorre la web, Odoo, PostgreSQL, PSP y Python con los mismos identificadores |
| **Tecnologías** | Las de cada asignatura. Aquí solo hay documentos (Markdown y la presentación `.pptx`) y resultados de pruebas |
| **Qué necesita** | Para repetir el recorrido: la base montada con los scripts 01–23, Java 17, Python con su entorno y, cuando exista, Odoo |
| **Cómo se inicia** | Instalación completa: `manuales/MANUAL_INSTALACION.md` (probado sobre un clon nuevo y una base vacía). Guion de la demostración: `manuales/MANUAL_DEMOSTRACION.md` |
| **Pruebas** | `evidencias/regresion-final/README.md`: la regresión completa del 13/11 (SQL, Java, PSP, Node, Python, web en Edge, SO024 provisional, ventanas Swing y el manual seguido desde cero) |
| **Rúbrica** | Entregables comunes e integración SO024: 37 requisitos, 10 cumplidos; faltan el punto 4 (Odoo) y el 9 (reparto real del trabajo y uso de la IA) de la memoria, el paso de Odoo en el manual de demostración y el SO024 oficial. Detalle en `rubricas/MATRIZ_RUBRICAS.md` (§2.6 y §2.7) |
| **Conexión con otras asignaturas** | Es la conexión: `SO024/contrato-fabricacion.md` fija el CSV entre Acceso a Datos y PSP, y `SO024/caso-comun-SO024.md` los datos que tienen que coincidir en todas las partes |
| **Evidencias** | `evidencias/regresion-final/` y la cadena SO024 PROVISIONAL (`evidencias/regresion-final/06_so024_provisional/` y `03_PSP/evidencias/so024_provisional/`) |

## Carpetas

| Carpeta | Contenido |
|---|---|
| `SO024/` | El caso común: los datos acordados y los **7 que faltan** (`caso-comun-SO024.md`), el contrato del CSV de fabricación y la prueba completa preparada para cuando se acuerden (`SO024_DATOS_PENDIENTES.md`). **SO024 es PROVISIONAL** |
| `memoria/` | `MEMORIA.md`: la memoria técnica común (9 puntos). Las memorias de cada asignatura están en la carpeta `memoria/` de cada una |
| `manuales/` | Instalación, demostración y la lista de comprobaciones manuales |
| `rubricas/` | `MATRIZ_RUBRICAS.md` (estado de cada requisito de cada rúbrica, con su evidencia) y `MATRIZ_EVIDENCIAS.md` (qué archivo enseñar para cada bloque) |
| `defensa/` | Guía y simulación de la defensa, y la presentación (`.md` y `.pptx`) |
| `evidencias/` | La regresión completa del 13/11 (`regresion-final/`) y la misma sobre el árbol limpio (`regresion-limpieza/`) |

Cada documento sigue siendo la única fuente de su tema: los README de las asignaturas enlazan aquí en lugar de copiarlo.
