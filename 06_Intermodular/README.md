# 06 · Proyecto Intermodular

Lo que une las asignaturas: el caso documentado S00005 de Odoo y las pruebas independientes de los módulos, la memoria técnica común, los manuales, las matrices de rúbricas, la defensa y la regresión completa.

| | |
|---|---|
| **Qué hace** | Reúne la documentación y las pruebas que no son de una sola asignatura: S00005 del Club Atlético NOVA se presenta con el PDF de Berme; no hay prueba de que ese pedido recorra PostgreSQL, PSP o Python |
| **Tecnologías** | Las de cada asignatura. Aquí solo hay documentos (Markdown y la presentación `.pptx`) y resultados de pruebas |
| **Qué necesita** | Para repetir el recorrido: la base montada con los scripts 01–23, Java 17, Python con su entorno y el PDF original de Odoo para la parte documental |
| **Cómo se inicia** | Instalación completa: `manuales/MANUAL_INSTALACION.md` (probado sobre un clon nuevo y una base vacía). Guion de la demostración: `manuales/MANUAL_DEMOSTRACION.md` |
| **Pruebas** | `evidencias/cierre-entrega-20261113/README.md`: la regresión del código entregado (`4f09742`, clon nuevo): SQL, Java, PSP, Python, Node y 9 controles en Edge. Las anteriores, históricas y sobre árboles anteriores: `evidencias/regresion-final/README.md` (web en Edge, SO024 provisional, ventanas Swing y el manual seguido desde cero) y `evidencias/regresion-limpieza/README.md` |
| **Rúbrica** | Entregables comunes e integración: se conserva evidencia documental de Odoo; la trazabilidad de S00005 entre sistemas y las aportaciones personales no confirmadas siguen limitadas. Detalle en `rubricas/MATRIZ_RUBRICAS.md` (§2.6 y §2.7) |
| **Conexión con otras asignaturas** | Es la conexión: `SO024/contrato-fabricacion.md` fija el CSV entre Acceso a Datos y PSP, y `CASO_COMUN_S00005.md` explica el caso elegido y lo que no se ha demostrado |
| **Evidencias** | `evidencias/cierre-entrega-20261113/` (código entregado); históricas: `evidencias/regresion-final/`, `evidencias/regresion-limpieza/` y la cadena SO024 PROVISIONAL (`evidencias/regresion-final/06_so024_provisional/` y `03_PSP/evidencias/so024_provisional/`). Las históricas citan identificadores de commit anteriores a la reescritura del 13/11: ver `EQUIVALENCIAS_COMMITS.md` |

## Carpetas

| Carpeta | Contenido |
|---|---|
| `SO024/` | Archivo del ejemplo SO024 y sus ensayos PROVISIONALES; incluye el contrato CSV aún vigente. El caso de Odoo actual es `CASO_COMUN_S00005.md`; no se ejecutará el plan antiguo de crear un SO024 oficial |
| `memoria/` | `MEMORIA.md`: la memoria técnica común (9 puntos y conclusiones). Las memorias de cada asignatura están en la carpeta `memoria/` de cada una |
| `manuales/` | Instalación, demostración y la lista de comprobaciones manuales |
| `rubricas/` | `MATRIZ_RUBRICAS.md` (estado de cada requisito de cada rúbrica, con su evidencia) y `MATRIZ_EVIDENCIAS.md` (qué archivo enseñar para cada bloque) |
| `defensa/` | Guía, simulación y guion de presentación `.md` vigentes, con S00005. El `.pptx` tiene todavía el contenido anterior a S00005: no usarlo hasta corregirlo **[EQUIPO: corregirlo o retirarlo antes de entregar]** |
| `evidencias/` | La regresión del código entregado (`cierre-entrega-20261113/`) y las dos anteriores del 13/11, históricas: `regresion-final/` y la misma sobre la rama local de la limpieza (`regresion-limpieza/`) |

Cada documento sigue siendo la única fuente de su tema: los README de las asignaturas enlazan aquí en lugar de copiarlo.
