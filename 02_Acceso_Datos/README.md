# 02 · Acceso a Datos

La base de datos PostgreSQL de NOVA Sneakers.

| | |
|---|---|
| **Qué hace** | La base guarda el catálogo (modelos, colores y tallas), el inventario, los clientes, los pedidos y las personalizaciones X-NOVA, con funciones, triggers, roles, auditoría y exportaciones a CSV. |
| **Tecnologías** | PostgreSQL 17 (SQL y PL/pgSQL), pgModeler y draw.io para el modelo |
| **Qué necesita** | PostgreSQL 17 con `psql` o pgAdmin |
| **Cómo se inicia** | Base: los 23 scripts de `sql/` sobre una base vacía, **en el orden del `README.md` principal** (el número del archivo no es el orden) |
| **Pruebas** | Batería de `sql/09_pruebas.sql` a `16_exportar_csv_dashboard.sql`: 123 PASS, 0 FAIL y 1 ERROR previsto (S4b); el 09 aporta 91 de esos PASS. |
| **Rúbrica** | 130 requisitos, 114 cumplidos. Faltan las aportaciones de cada uno en la memoria, el E-R en PNG y ciertas evidencias manuales. S00005 no está probado en PostgreSQL. **«Es imprescindible aprobar todas las partes»** (AD-138) |
| **Conexión con otras asignaturas** | `sql/15_exportar_fabricacion.sql` genera el CSV que procesa PSP (`03_PSP/`); `sql/16_exportar_csv_dashboard.sql`, los cinco CSV de Python (`04_Python/entrada_acc/`); los scripts 19, 20, 22 y 23 crean los usuarios y funciones que usa `servidor-admin` (panel, tienda, reparto y portal); `sql/21_catalogo_web.sql` carga los 100 modelos de la web; `sql/18_datos_so024.sql` prepara el ensayo opcional del ejemplo SO024, no S00005 |
| **Evidencias** | La batería SQL completa (scripts 09 a 16) se lanza con los scripts de `sql/` |

## Carpetas

| Carpeta | Contenido |
|---|---|
| `sql/` | Los 23 scripts: esquema, funciones, triggers, datos de demostración, seguridad, auditoría, pruebas, exportaciones y ampliaciones |
| `documentacion/` | Instalación de la base, qué hace cada script, decisiones de diseño, seguridad y pruebas (`README.md`), y el modelo relacional |
| `modelo/`, `modelo-er/` | Modelo de pgModeler (`.dbm`) y diagrama entidad-relación (`.drawio`) |
| `memoria/` | `MEMORIA_ACCESO_DATOS.md`, el apartado de Acceso a Datos que pide la rúbrica |

Quién ha hecho cada parte se ve con `git log --follow <archivo>`: en la base de datos y en la aplicación han trabajado los tres.
