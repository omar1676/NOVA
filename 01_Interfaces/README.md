# 01 · Desarrollo de Interfaces

La web de NOVA Sneakers y las pantallas del personal.

| | |
|---|---|
| **Qué hace** | La web de la marca (`cliente/`): escaparate, catálogo de 100 modelos con precio, ficha, probador, formulario Custom (el envío es una simulación), contacto y tienda con cuenta, carrito y pago simulado. Además, el panel de administración (`admin/`) y el portal del trabajador (`trabajador/`), a los que se entra desde un único inicio de sesión |
| **Tecnologías** | HTML5, CSS3 y JavaScript, sin librerías ni compilación. El panel y el portal cargan los iconos y los gráficos desde internet. Los datos los da el servidor Node compartido (`servidor-admin/`) |
| **Qué necesita** | Un navegador moderno. La tienda, el inicio de sesión, el panel y el portal necesitan además `servidor-admin` y la base de datos con los scripts 19 a 23 |
| **Cómo se inicia** | Sin servidor: abrir `cliente/index.html`, o lanzar `py -m http.server 8000 --bind 127.0.0.1` desde la raíz del repositorio y entrar en `http://127.0.0.1:8000/01_Interfaces/cliente/`. Con servidor: `npm start` en `servidor-admin` y abrir `http://127.0.0.1:3000/tienda/` o `http://127.0.0.1:3000/login.html` (pasos en el `README.md` principal) |
| **Pruebas** | `py scripts/comprobar_web.py` (que existan los recursos que enlaza la web). Pruebas en Edge con Playwright y axe: Interfaces, web completa, mejoras, compra, reparto, inicio de sesión y portal (los scripts no están en el repositorio; sus resultados sí). Las pruebas de Node del servidor están en `servidor-admin/README.md`. La prueba de usabilidad **con personas** está **PENDIENTE**: el procedimiento está en `memoria/PROCEDIMIENTO_USABILIDAD.md` |
| **Rúbrica** | IM §4.1, RA4 y RA8: 14 requisitos, 13 cumplidos; falta la usabilidad con personas. Detalle en `06_Intermodular/rubricas/MATRIZ_RUBRICAS.md` (§2.1). La tienda, el panel, el reparto, los correos y el portal son ampliaciones que no pide la rúbrica (§3) |
| **Conexión con otras asignaturas** | Los 100 modelos se llaman igual que en `02_Acceso_Datos/sql/21_catalogo_web.sql`. La tienda, el panel y el portal leen y escriben en PostgreSQL a través de `servidor-admin` (usuarios `web_nova` y `tienda_nova`). El formulario Custom es la solicitud del caso común SO024 (`06_Intermodular/SO024/`) |
| **Evidencias** | `evidencias/web/` (capturas en 4 anchos y Lighthouse), `evidencias/tienda/`, `evidencias/panel-admin/`, `evidencias/portal-trabajador/`, `evidencias/reparto-y-correo/` y `evidencias/correo-ethereal/`. La regresión completa está en `06_Intermodular/evidencias/` |

## Carpetas

| Carpeta | Contenido |
|---|---|
| `cliente/` | Web pública y tienda: `index.html`, `css/`, `js/` e `images/`. Su `README.md` explica cada archivo y cada decisión |
| `admin/` | Panel de administración y página de acceso única del personal (`login.html`) |
| `trabajador/` | Portal del trabajador: resumen, pedidos, inventario y personalizados |
| `evidencias/` | Resultados y capturas de las pruebas, cada una con su `README.md` |
| `memoria/` | Estrategia de pruebas (RA8) y procedimiento de la prueba de usabilidad (RA4) |

Quién ha hecho cada parte se ve con `git log --follow <archivo>`: en la web han trabajado los tres.
