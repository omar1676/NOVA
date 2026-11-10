# Portal del trabajador y login único · evidencias del 13/11/2026

El portal de Berme (`interfaces/trabajador/`, rutas en `servidor-admin/rutas-trabajador.js`) integrado con el login único del personal y el script `23_portal_trabajador.sql`. Es una **ampliación**: ninguna rúbrica lo pide.

**Prueba:** Edge sin ventana (Playwright) contra el servidor de pruebas, sobre una base desechable montada desde cero con los scripts 01–23, en escritorio (1440 px) y en móvil (390 px). **82 PASS, 0 FAIL** (`../regresion-final/05_web/06_edge_portal.txt`). Además, `npm run test:portal` 24/24 y el SQL del 23 50/50 (`../regresion-final/03_node/` y `01_sql/`).

Qué se comprueba:

- **Login único:** la página de acceso es la del personal; contraseña mal → mensaje claro, sin cookie y el campo se vacía; `admin.demo` (administrador) entra al panel; `taller.demo` (trabajador) entra al portal; `tienda.demo` (comercial) recibe «Acceso denegado» y no recibe cookie. La cookie es `HttpOnly` y `SameSite=Strict`.
- **Roles:** el administrador no entra al portal y el trabajador no entra al panel (las dos páginas llevan a `login.html`); `/api/admin/dashboard` desde el navegador del trabajador da 403. Cerrar sesión borra la cookie y «Atrás» no enseña datos.
- **Portal:** las cuatro páginas sin desplazamiento horizontal, con los iconos de Lucide 1.62.0 y **axe sin violaciones**; el resumen coincide con PostgreSQL; «Avanzar estado» cambia el pedido en la página y en la base, y la auditoría lo apunta a `taller.demo`; el inventario guarda la cantidad y la auditoría apunta el `CAMBIO_STOCK`; una cantidad negativa avisa y no se guarda; el buscador y el filtro de estado funcionan.
- **Lo que no se prueba:** el conector de Odoo (`odoo.js`, desactivado sin `ODOO_*`) y las rutas de `pedidos.js` (no se montan). Odoo sigue **PENDIENTE (Berme)**.

| Captura | Qué enseña |
|---|---|
| `login.png`, `login_movil.png` | La página de acceso única |
| `login_error.png`, `login_error_movil.png` | Contraseña incorrecta |
| `login_comercial_denegado.png`, `..._movil.png` | `tienda.demo` (comercial): acceso denegado |
| `admin_tras_login.png`, `..._movil.png` | `admin.demo` entra al panel |
| `portal_trabajador.png`, `..._movil.png` | Resumen del portal (`taller.demo`) |
| `portal_pedidosTrabajador.png`, `..._movil.png` | Pedidos |
| `portal_pedidos_antes_de_avanzar.png`, `portal_pedidos_tras_avanzar.png` | «Avanzar estado» antes y después |
| `portal_inventarioTrabajador.png`, `..._movil.png` | Inventario |
| `portal_personalizadosTrabajador.png`, `..._movil.png` | Personalizados |
| `portal_menu_movil.png` | Menú en el móvil |

Las capturas están reducidas (ancho máximo 1200 px en escritorio y 480 px en móvil, paleta de 256 colores) para que el repositorio no pese demasiado.
