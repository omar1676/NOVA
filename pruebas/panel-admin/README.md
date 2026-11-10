# Evidencias del panel de administración

Pruebas del panel de Álvaro conectado a PostgreSQL a través de `servidor-admin/`. Se hicieron el 11 de noviembre de 2026.

**Entorno:**
- Windows 11, Node 24.15.0, Express 5.3.0 y pg 8.23.1.
- PostgreSQL 17.11, en una base **desechable** montada desde cero con los scripts del proyecto. No se usó la base real.
- Edge 157 manejado con Playwright 1.65, y axe-core 4.12.1.

Playwright y axe-core no son dependencias del proyecto. Las pruebas de navegador se ejecutaron desde una carpeta temporal, y aquí solo se guardan sus resultados. La parte que cualquiera puede repetir es `npm test` (ver `servidor-admin/README.md`).

## Resultados

| Archivo | Qué demuestra | Resultado |
|---|---|---|
| `resultados/01_scripts_sql.txt` | Los scripts originales, con el 19 instalado desde cero, siguen dando lo mismo; y el 19 se puede repetir | 123 PASS, 0 FAIL y 1 ERROR, que es el error de permisos que el 09 provoca a propósito |
| `resultados/02_npm_test.txt` | Las pruebas automáticas del servidor | 16 de 16 |
| `resultados/03_autenticacion.txt` | Login y logout; 401 sin sesión y 403 con otro rol; cookie HttpOnly y SameSite=Strict; intentos de saltarse la protección de las páginas | 44 de 44 |
| `resultados/04_seguridad.txt` | Cabeceras, cabecera Host, cuerpos grandes, byte nulo, comodines, tabla bloqueada (503 a los 10 s), «Atrás» tras cerrar sesión y login sin JavaScript | 28 de 28, más «Atrás» en dos modos del navegador |
| `resultados/05_permisos_web_nova.txt` | Conectado **de verdad como `web_nova`**: no puede pasar a otros roles. Como `panel_lectura`, y sin `READ ONLY`, no puede escribir ni leer datos sensibles, pero sí lo que usa el panel | 49 de 49 |
| `resultados/06_api_frente_a_postgresql.txt` | Las 8 rutas comparadas con consultas hechas directamente en PostgreSQL; filtros; 80 consultas sin cambiar ninguna tabla | 69 de 69 |
| `resultados/07_navegador_escritorio_y_movil.txt` | El panel en Edge a 1280 y 390 px, comparado con PostgreSQL; los iconos de Lucide 1.62.0 en las 11 páginas, y Chart.js | 124 de 124, más 12 de 12 |
| `resultados/08_accesibilidad.txt` | axe-core en las 12 páginas, antes y después de la limpieza | De 11 elementos con problemas a 0 |
| `resultados/09_intentos_y_sesiones.txt` | Límite de intentos (429, misma respuesta exista o no la cuenta, se puede volver a entrar); cuenta desactivada o con otro rol y la sesión abierta; logout; caducidad a las 2 horas | 25 de 25, más 4 de 4 |

En `07`, los únicos errores de consola son los 401 del login con contraseña incorrecta, que la prueba provoca a propósito.

## Capturas

Todas son del panel con los datos de la base de prueba:

| Captura | Página |
|---|---|
| `login_movil.png` | Login a 390 px, con el aviso de un trabajador sin permiso |
| `dashboard_escritorio.png` y `dashboard_movil.png` | Dashboard: ventas, pedidos del día y pendientes, «No disponible» en sugerencias, últimas operaciones, pedidos por estado y gráfico |
| `pedidos_escritorio.png` y `pedidos_movil.png` | Pedidos |
| `productos_escritorio.png` | Productos (un SKU por fila) |
| `inventario_escritorio.png` | Inventario, con el estado según el umbral (menos de 10) |
| `clientes_escritorio.png` | Clientes (correos ficticios `@example.com`) |
| `trabajadores_escritorio.png` | Trabajadores, sin DNI |
| `auditoria_escritorio.png` | Auditoría con las acciones reales de los triggers |
| `estadisticas_escritorio.png` | Estadísticas del mes, gráficos y modelos más vendidos |
| `configuracion_escritorio.png` | Una de las tres páginas que siguen siendo prototipo, con su aviso |

## Lo que sigue abierto

- **Tiempo de respuesta del login.** Tarda algo más si el usuario existe, por cómo está hecho `iniciar_sesion` (script 02, que no se ha tocado). El límite de intentos reduce lo que se puede aprovechar.
- **Bloqueo a propósito.** Como el límite cuenta por nombre de usuario, alguien que conozca un nombre puede bloquearlo 5 minutos fallando adrede.
- **Reinicios.** Al reiniciar el servidor se olvidan las sesiones y los intentos.
- **Lucide 1.62.0.** El cambio de versión lo tiene que revisar Álvaro.

## Regresión del 13/11/2026 (árbol final)

Con el código final (login único, portal del trabajador y «Marcar en reparto»), sobre bases desechables montadas desde cero con los scripts 01–23 (`../regresion-final/README.md`):

- `npm test`: **23 de 23** con base desechable (22 y 1 saltada sin ella) — `../regresion-final/03_node/`.
- Login único y roles en Edge: el administrador entra al panel, el trabajador no (403 en `/api/admin/`), el comercial no tiene panel web — **82 de 82** junto con el portal (`../regresion-final/05_web/06_edge_portal.txt`; capturas en `../portal-trabajador/capturas/`, por ejemplo `admin_tras_login.png`).
- El panel con las compras web (dashboard, pedidos y auditoría): `../tienda/capturas-2026-11-13/panel_13_*.png` a `panel_15_*.png`.
- «Marcar en reparto»: `../reparto-y-correo/`.

Las baterías largas de este README (autenticación, seguridad, API frente a PostgreSQL, navegador) son del 11/11 y **no se han repetido**. Desde entonces han cambiado `servidor.js`, `bd.js`, `consultas.js`, `login.js` y `script.js` (login único, portal, reparto y recibos). Lo que toca al panel —el login, los roles, el botón de reparto y las páginas con las compras web— se ha probado hoy con las pruebas de arriba.
