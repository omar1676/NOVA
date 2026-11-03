# Evidencias de la aplicación Java Swing (Acceso a Datos)

Capturas de la aplicación de `acceso-datos/java` tomadas el 9 de noviembre de 2026.

- **Base de datos:** una base de prueba reconstruida desde cero con los scripts de
  `acceso-datos/sql`, no la base real. Los usuarios son los de demostración
  (`admin.demo`, `tienda.demo` y `taller.demo`) y los clientes son los ficticios de
  `05_datos_prueba.sql`.
- **Cómo se hicieron:** un programa de prueba abrió la aplicación real
  (`VentanaLogin`), escribió en los campos y pulsó los botones con los tres roles.
  Comparó lo que salía en pantalla con consultas SQL: 77 comprobaciones, todas PASS
  (`resultado-prueba-ventanas.txt`).
- **Qué se ve:** cada captura es la ventana de la aplicación, sin la barra de Windows.
- **La ruta `N:\NOVA`** es una unidad virtual que solo se usó para la prueba, para que
  la captura del CSV no enseñe carpetas personales.
- **Datos sensibles:** ninguna captura muestra contraseñas, hashes ni datos de conexión.

## Qué captura demuestra cada requisito

| Requisito de la rúbrica | Capturas |
|---|---|
| 3.7 Interfaz Java con JDBC: elegir cliente, modelo y color, talla y cantidad | 04, 05 (lista de modelos cargada de PostgreSQL) |
| 3.7 Mensaje comprensible cuando la base rechaza una operación | 14 (talla que no existe), 16 (permiso denegado) |
| 3.7 Consulta visual con «Buscar / Consultar» y tabla legible | 06 |
| 3.7 Tres filtros combinables | 06 (cliente + estado), 08 (modelo + desde + hasta) |
| 3.7 Resultado vacío | 08 («No hay pedidos con esos filtros.») |
| 3.7 Error de conexión | 18 |
| 3.7 Consulta incorrecta | 09 (fecha mal escrita) |
| 3.7 y 3.8 Permisos según el usuario, no solo ocultando botones | 16 (el botón está, pero se deniega), 04, 15 y 17 (pestañas de cada rol) |
| 3.8 Inicio de sesión | 01; errores en 02 (campos vacíos) y 03 (contraseña incorrecta). Las dos dan el mismo mensaje a propósito, para no revelar qué usuarios existen |
| 3.8 Un usuario de prueba por rol | 04 (administrador), 15 (comercial), 17 (trabajador) |
| 3.8 Operación denegada | 16 |
| 3.8 Usuario y hora en `log_eventos` | 10 (auditoría vista por el administrador) |
| 3.9 Prueba E (sin filtros, filtros combinados) | 06, 08 |
| 3.9 Prueba F (búsqueda sin resultados y perfil sin permiso) | 08, 16 |
| 3.12 Panel de indicadores calculado en PostgreSQL | 11 |
| 3.12 Análisis por modelo y talla | 11 («Modelos más solicitados» y «Pares por talla») |
| 3.12 Stock bajo con umbral configurable, ordenado | 11 (umbral 10, sin resultados y con aviso), 12 (umbral 25), 13 (umbral negativo rechazado) |
| 3.12 CSV de la consulta filtrada | 06 (2 pedidos en la tabla) y 07 (2 filas exportadas) |
| 3.13 Prueba J (indicadores y CSV comparados con SQL) | 11, 12 y 07; la comparación está en `resultado-prueba-ventanas.txt` |

## Lista de capturas

| Captura | Qué se ve |
|---|---|
| 01-login | Ventana de inicio de sesión |
| 02-error-login-vacio | Entrar con usuario y contraseña vacíos |
| 03-error-login-clave | Entrar con una contraseña incorrecta |
| 04-admin.demo-inicio | Administrador: cuatro pestañas |
| 05-admin.demo-nuevo-pedido | Nuevo pedido con la lista «Modelo y color» abierta |
| 06-admin.demo-consulta-filtrada | Consulta filtrada por cliente y estado: 2 pedidos |
| 07-csv-exportado | Exportación a CSV de esa consulta: 2 filas |
| 08-admin.demo-consulta-sin-resultados | Modelo y fechas sin coincidencias |
| 09-error-fecha | Fecha escrita con un formato incorrecto |
| 10-auditoria-admin | `log_eventos`: usuario, fecha y hora, acción y detalle |
| 11-admin.demo-indicadores-umbral-10 | Indicadores; stock bajo vacío con su aviso |
| 12-admin.demo-indicadores-umbral-25 | Stock bajo con umbral 25: 60 referencias, de menos a más |
| 13-error-umbral-negativo | Umbral -5 rechazado |
| 14-error-talla-inexistente | Pedido con talla 38: lo rechaza PostgreSQL y no se guarda nada |
| 15-tienda.demo-inicio | Comercial: sin la pestaña Usuarios |
| 16-auditoria-denegada-comercial | El comercial pulsa «Ver auditoría» y recibe «Acceso denegado» |
| 17-taller.demo-inicio | Trabajador: solo Consultas e Indicadores |
| 18-error-conexion | Sin PostgreSQL: mensaje de error de conexión |

## Lo que todavía no tiene captura

Estas pruebas pasan en `pruebas.bat` (batería A–J, 47 PASS), pero sus capturas hay que
hacerlas a mano en la demostración:

- **Pruebas A y H:** crear un pedido Custom desde Java (por ejemplo, el caso común de 40
  pares), ver su detalle y confirmarlo.
- **Pruebas B y C:** confirmar sin stock y cancelar un pedido confirmado.
- **Prueba D:** el ROLLBACK, que se enseña con SQL.
- **«Limpiar filtros»:** la tabla después de pulsarlo.
- **3.10 y prueba G:** `actividad_sneaker.txt` con las líneas nuevas después de tres consultas.
- **3.11 y prueba I:** la pestaña Usuarios (crear y desactivar), `usuarios_sneaker.json` y la
  exportación denegada al comercial.
- **El CSV abierto,** para ver su contenido.
