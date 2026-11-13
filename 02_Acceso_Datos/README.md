# 02 · Acceso a Datos

La base de datos PostgreSQL de NOVA Sneakers y la aplicación Java que trabaja con ella por JDBC.

| | |
|---|---|
| **Qué hace** | La base guarda el catálogo (modelos, colores y tallas), el inventario, los clientes, los pedidos y las personalizaciones X-NOVA, con funciones, triggers, roles, auditoría y exportaciones a CSV. La aplicación Java (Swing) permite iniciar sesión, crear y confirmar pedidos en una transacción, consultar con filtros, ver indicadores, gestionar usuarios y generar los archivos TXT, JSON y CSV |
| **Tecnologías** | PostgreSQL 17 (SQL y PL/pgSQL), Java 17 con Swing y JDBC (driver `postgresql-42.7.14.jar`), pgModeler y draw.io para el modelo |
| **Qué necesita** | PostgreSQL 17 con `psql` o pgAdmin, JDK 17 y el driver JDBC en `java/lib/` (se descarga; no se sube a Git) |
| **Cómo se inicia** | Base: los 23 scripts de `sql/` sobre una base vacía, **en el orden del `README.md` principal** (el número del archivo no es el orden). Aplicación: lanzar `17_usuario_java.sql`, copiar `java/conexion.properties.ejemplo` como `java/conexion.properties` con la contraseña de `java_nova` y ejecutar `java\ejecutar.bat` |
| **Pruebas** | Batería de `sql/09_pruebas.sql` a `16_exportar_csv_dashboard.sql`: 123 PASS, 0 FAIL y 1 ERROR previsto (S4b); el 09 aporta 91 de esos PASS. `java\pruebas.bat` (`PruebasRubrica`, pruebas A a J y roles): 47 de 47. Las ventanas Swing se comprobaron con los tres roles frente a SQL (76 PASS; el script no está en el repositorio, sus resultados sí) |
| **Rúbrica** | 130 requisitos, 114 cumplidos. Faltan las aportaciones de cada uno en la memoria, el E-R en PNG y ciertas evidencias manuales. S00005 no está probado en PostgreSQL/Java. **«Es imprescindible aprobar todas las partes»** (AD-138).md` (§2.2) |
| **Conexión con otras asignaturas** | `sql/15_exportar_fabricacion.sql` genera el CSV que procesa PSP (`03_PSP/`); `sql/16_exportar_csv_dashboard.sql`, los cinco CSV de Python (`04_Python/entrada_acc/`); los scripts 19, 20, 22 y 23 crean los usuarios y funciones que usa `servidor-admin` (panel, tienda, reparto y portal); `sql/21_catalogo_web.sql` carga los 100 modelos de la web; `sql/18_datos_so024.sql` prepara el ensayo opcional del ejemplo SO024, no S00005 |
| **Evidencias** | `evidencias/java-pruebas-rubrica/` (salida de las 47 pruebas y archivos generados) y `evidencias/java-swing/` (capturas de las ventanas). La batería SQL completa está en la regresión del 13/11 |

## Carpetas

| Carpeta | Contenido |
|---|---|
| `sql/` | Los 23 scripts: esquema, funciones, triggers, datos de demostración, seguridad, auditoría, pruebas, exportaciones y ampliaciones |
| `documentacion/` | Instalación de la base, qué hace cada script, decisiones de diseño, seguridad y pruebas (`README.md`), y el modelo relacional |
| `modelo/`, `modelo-er/` | Modelo de pgModeler (`.dbm`) y diagrama entidad-relación (`.drawio`) |
| `java/` | Aplicación Swing + JDBC. Su `README.md` explica cada clase, la configuración y las pruebas |
| `evidencias/` | Resultados y capturas de las pruebas |
| `memoria/` | `MEMORIA_ACCESO_DATOS.md`, el apartado de Acceso a Datos que pide la rúbrica |

Quién ha hecho cada parte se ve con `git log --follow <archivo>`: en la base de datos y en la aplicación han trabajado los tres.
