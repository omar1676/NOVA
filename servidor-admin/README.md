# Servidor del panel de administración y de la tienda web

Conecta con PostgreSQL el panel de Álvaro (`interfaces/admin/`) y la tienda web (`interfaces/cliente/`).

```
Navegador ──► http://127.0.0.1:3000 ──► Node + Express (esta carpeta) ──► PostgreSQL
  panel: /admin.html                     · páginas del panel y /api/admin/...   usuario web_nova (solo lectura)
  tienda: /tienda/                       · web cliente y /api/tienda/...        usuario tienda_nova
```

- El navegador **nunca** habla con PostgreSQL. Pide datos a este servidor, y es el servidor el que hace las consultas.
- El mismo servidor entrega las páginas del panel y de la tienda. Así, páginas y API tienen el mismo origen y no hace falta CORS.
- Solo escucha en `127.0.0.1`: no se puede abrir desde otro ordenador.
- **Panel y tienda van separados:** cada uno tiene su usuario de PostgreSQL, su cookie de sesión y sus rutas. El panel sigue sin poder escribir nada.
- Los importes y el stock los calculan los triggers de PostgreSQL. El panel solo los lee; la tienda escribe únicamente a través de las funciones del script 20 (ver «La tienda web»).

## Puesta en marcha

Hace falta Node 20.6 o posterior (probado con Node 24.15) y una base con los scripts instalados.

1. Crear el rol de solo lectura y el usuario de conexión. Pide una contraseña:
   ```
   psql -U postgres -d nova_sneakers -f acceso-datos/sql/19_usuario_web.sql
   ```
2. Instalar las dos dependencias, `express` y `pg`, con las versiones exactas de `package-lock.json`:
   ```
   cd servidor-admin
   npm ci
   ```
3. Copiar `.env.example` como `.env` y escribir en `PGPASSWORD` la contraseña del paso 1. El `.env` no se sube a Git.
4. Arrancar:
   ```
   npm start
   ```
5. Abrir `http://127.0.0.1:3000` y entrar con `admin.demo`, con la contraseña que se puso en `13_activar_usuarios.sql`.

Si `.env` dice `PGUSER=postgres`, el servidor se niega a arrancar.

**Para la tienda**, además:

6. Después de la batería de pruebas (`09_pruebas.sql`), lanzar el 20, que pide la contraseña de `tienda_nova`, y el 21:
   ```
   psql -U postgres -d nova_sneakers -f acceso-datos/sql/20_tienda_web.sql
   psql -U postgres -d nova_sneakers -f acceso-datos/sql/21_catalogo_web.sql
   ```
7. Escribir en `.env` `TIENDA_PGUSER=tienda_nova` y `TIENDA_PGPASSWORD` con la contraseña del paso 6, y volver a arrancar.
8. Abrir `http://127.0.0.1:3000/tienda/`. Al arrancar, la consola dice si la tienda está configurada. Sin esas dos variables, el panel funciona igual y la tienda enseña el catálogo, pero no deja comprar.

## Archivos

| Archivo | Qué hace |
|---|---|
| `servidor.js` | Arranca Express y entrega las páginas del panel y de la tienda. Tiene el login, el logout y las 8 rutas del panel, y comprueba la sesión y el rol en cada petición |
| `bd.js` | Las dos conexiones con PostgreSQL. `consultarSoloLectura` (panel) abre `BEGIN ... READ ONLY` y `SET LOCAL ROLE panel_lectura`; `operarEnTienda` (tienda) abre una transacción con `SET LOCAL ROLE tienda_web` |
| `consultas.js` | Las 8 consultas SQL del panel. Salen de `12_consultas_panel.sql` y de `PedidoDAO.verAuditoria` (Java) |
| `tienda.js` | Las rutas de la tienda (`/api/tienda/...`): comprueban los datos y llaman a las funciones del script 20 con el cliente de la sesión |
| `consultas-tienda.js` | El SQL de la tienda: catálogo, cuenta, historial y las llamadas a las funciones de compra |
| `sesiones.js` | Las sesiones: un token aleatorio en una cookie HttpOnly, guardado en memoria. Dos almacenes separados: `sesion_nova` (panel) y `sesion_tienda` (clientes) |
| `intentos.js` | El límite de intentos de login (panel y tienda) |
| `pruebas/api.test.js` | Pruebas automáticas del panel (`npm test`). Solo leen |
| `pruebas/tienda.test.js` | Pruebas automáticas de la tienda (`npm run test:tienda`). Crean clientes y pedidos: **solo con una base desechable** |
| `../interfaces/admin/login.html` y `login.js` | La página de acceso del panel |

## Las rutas

Todas devuelven JSON. Las de `/api/admin/` necesitan una sesión de administrador: sin sesión responden **401**, y con otro rol, **403**.

| Ruta | Filtros (`?nombre=valor`) | De dónde sale la consulta |
|---|---|---|
| `GET /api/estado` | — | Comprueba la conexión. Es pública: no devuelve datos del negocio |
| `POST /api/login` | JSON `{usuario, contrasena}` | `iniciar_sesion` (02): la contraseña la comprueba PostgreSQL con bcrypt. Tras 5 fallos, **429** |
| `POST /api/logout` | — | Borra la sesión |
| `GET /api/sesion` | — | Quién ha entrado y con qué rol |
| `GET /api/admin/dashboard` | — | P-A (ventas), P-B (pedidos por estado), C8 (stock bajo), los últimos 5 pedidos y las ventas por día (últimos 30 días) |
| `GET /api/admin/pedidos` | `estado`, `texto` | C5 |
| `GET /api/admin/productos` | `estado`, `texto` | Los JOIN de `csv_stock` (16). Precio = `precio_base + suplemento_precio`, el mismo que cobra `anadir_linea_pedido` |
| `GET /api/admin/inventario` | `estado`, `texto` | C8 sin agrupar, por SKU y nave |
| `GET /api/admin/clientes` | `estado`, `texto` | `csv_clientes` (16), sin la dirección de entrega |
| `GET /api/admin/trabajadores` | `estado`, `texto` | P-H, más `personal` para el nombre y el puesto. Nunca el DNI |
| `GET /api/admin/auditoria` | `accion`, `texto` | `PedidoDAO.verAuditoria`: los últimos 100 eventos |
| `GET /api/admin/estadisticas` | — | P-A del mes en curso, P-B, P-C y los ingresos por mes |

- Los filtros siempre van como parámetros (`$1`, `$2`…), nunca pegados al SQL.
- Un valor que no está en la lista permitida da **400**, por ejemplo `?estado=borrado`. También lo da un byte nulo.
- En el buscador, `%` y `_` se buscan como letras, no como comodines.

## Seguridad

### Permisos en PostgreSQL (script 19)

El servidor se conecta como `web_nova`, que por sí solo no puede hacer nada. Para cada consulta pasa a **`panel_lectura`**, un rol que solo puede leer:

| Puede | No puede |
|---|---|
| Leer enteras las tablas sin datos personales: modelos, variantes, SKU, existencias, naves, roles y auditoría | Escribir nada: ni `INSERT`, ni `UPDATE`, ni `DELETE` en ninguna tabla. Tampoco crear tablas |
| Leer **algunas columnas** de pedidos, líneas, clientes, personal y usuarios | Leer `password_hash`, `dni`, `direccion_entrega` ni `personalizacion` |
| Ejecutar `iniciar_sesion` para el login | Ejecutar las funciones que escriben (`establecer_password`, `crear_usuario`, `realizar_compra`…) |
| — | Pasar a `nova_admin` ni a ningún otro rol |

`iniciar_sesion` es `SECURITY DEFINER`: compara la contraseña con los permisos de su dueño, así que `panel_lectura` puede comprobar un login sin ver nunca el hash.

Hay **dos barreras** contra escribir:
1. los permisos de `panel_lectura`, que pone PostgreSQL;
2. el `READ ONLY` de cada transacción, que pone `bd.js`.

Aunque el código olvidara una, la otra sigue funcionando. `REPEATABLE READ` hace, además, que todas las consultas de una petición vean los mismos datos.

### Login y sesiones

- **Login:**
  - la contraseña la comprueba PostgreSQL;
  - el mensaje de error es el mismo exista o no el usuario.
- **Límite de intentos** (`intentos.js`):
  - tras 5 fallos seguidos con un mismo nombre de usuario, el servidor responde 429 durante 5 minutos, aunque la contraseña sea la buena;
  - cuenta igual exista o no la cuenta, así que no delata qué usuarios hay;
  - al acertar, el contador vuelve a cero;
  - la duración se puede cambiar con la variable `BLOQUEO_LOGIN_MS` (las pruebas la ponen en 1,5 s).
- **Sesión:**
  - es un token aleatorio de 32 bytes en una cookie `HttpOnly` y `SameSite=Strict`;
  - caduca a las 2 horas y se pierde al reiniciar el servidor;
  - la contraseña no se guarda.
- **En cada petición a `/api/admin/`** se vuelve a mirar en la base si la cuenta sigue activa y sigue siendo administradora:
  - si se ha desactivado, la sesión se borra y la respuesta es 401;
  - si ha cambiado de rol, también se borra, y la respuesta es 403.

### Servidor y navegador

- **Tiempos máximos:**
  - una consulta que tarda más de 10 s se cancela y la API responde 503;
  - si en 5 s no hay ninguna conexión libre, también da error.
- **Cabecera Host:** solo se aceptan `127.0.0.1` y `localhost`. Así una web que haga *DNS rebinding* no puede usar el panel.
- **Cabeceras de las respuestas:**
  - sin `X-Powered-By`;
  - con `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` y `Referrer-Policy: same-origin`;
  - la API, además, con `Cache-Control: no-store`.
- **Páginas:** sin sesión de administrador solo se entregan `login.html`, `login.js`, `styles.css` y las imágenes. Cualquier otra página lleva a `login.html`.
- **Botón «Atrás»:** después de cerrar sesión, una página que el navegador tuviera guardada se vuelve a pedir al servidor, que manda al login.
- **Datos:** el panel pinta con `textContent`, no con `innerHTML`. Un dato que contenga HTML se ve como texto y no se ejecuta.
- **Librerías de la CDN:** Lucide (1.62.0) y Chart.js (4.4.1) tienen la versión fija y la huella de integridad (`integrity`). Si el archivo de la CDN cambiara, el navegador no lo ejecutaría.
- **Respuestas:** no llevan hashes, contraseñas, DNI ni direcciones. Los errores internos se apuntan en la consola del servidor y el navegador recibe un mensaje genérico.

## La tienda web

La web cliente (`interfaces/cliente/`) se sirve en `/tienda/`. Su JavaScript (`js/tienda.js`) pide los datos a estas rutas:

| Ruta | Sesión | Qué hace |
|---|---|---|
| `GET /api/tienda/catalogo` | No | Modelos a la venta con sus colores, tallas, precio y stock, leídos de PostgreSQL |
| `POST /api/tienda/registro` | No | `{nombre, email, contrasena, telefono?, direccion?}` → `registrar_cliente`. Abre la sesión |
| `POST /api/tienda/login` | No | `{email, contrasena}` → `iniciar_sesion_cliente`. Tras 5 fallos, **429** |
| `POST /api/tienda/logout` | No | Borra la sesión |
| `GET /api/tienda/sesion` | No | El cliente que ha entrado, o `{cliente: null}` |
| `POST /api/tienda/pedidos` | Sí | `{clave, lineas: [{sku, cantidad}], telefono, direccion}` → `crear_compra_web`. Devuelve el pedido **pendiente** con el precio de cada línea y el total que ha calculado PostgreSQL |
| `POST /api/tienda/pedidos/:id/pago` | Sí | `{resultado: "aceptado" \| "rechazado"}`. Aceptado → `confirmar_compra_web`; rechazado → `cancelar_compra_web` |
| `POST /api/tienda/pedidos/:id/cancelacion` | Sí | `cancelar_compra_web` |
| `GET /api/tienda/pedidos` y `/pedidos/:id` | Sí | Solo los pedidos de ese cliente. Si es de otro, **404** |

**Quién decide qué:**
- **Node** comprueba la forma de los datos: tipos, longitudes y cantidades enteras de 1 a 10. Saca el `id_cliente` **de la sesión**, nunca del cuerpo, y no lee ningún precio ni total que mande el navegador.
- **PostgreSQL** decide lo demás. Las cinco funciones del script 20 comprueban que el cliente está activo, que el pedido es suyo y de la web, y que está pendiente. El precio lo ponen `realizar_compra` y `anadir_linea_pedido` (02), y el stock lo descuenta `trg_descontar_stock_confirmacion` (03) al confirmar. No hay ningún cálculo de importes ni de stock en Node.

**Permisos (script 20):**
- La tienda se conecta como `tienda_nova`, que solo puede pasar a `tienda_web`.
- `tienda_web` lee el catálogo, sus columnas de clientes, pedidos y líneas, y **ejecuta las cinco funciones**.
- No tiene ningún `INSERT`, `UPDATE` ni `DELETE` sobre ninguna tabla, ni puede llamar directamente a `realizar_compra`.
- `web_nova` (el panel) no puede pasar a `tienda_web`, ni `tienda_nova` a `panel_lectura`.

**El pago es una simulación académica.** No se pide ningún dato bancario y no se cobra nada. El resultado lo elige quien prueba la web; en una tienda real lo mandaría la pasarela de pago al servidor.

**Dobles clics, reintentos y compras a la vez:**
- **Crear el pedido:** el navegador crea una `clave` aleatoria al abrir el checkout, y de ella sale la referencia `WEB-…`. Si la petición llega dos veces, `crear_compra_web` devuelve el mismo pedido, porque `pedidos_referencia_uq` no deja repetirla.
- **Pagar:** `confirmar_compra_web` bloquea el pedido (`FOR UPDATE`). El segundo pago ve que ya está pagado y no hace nada.
- **Los últimos pares:** `descontar_stock` no deja bajar de cero. Si dos clientes pagan a la vez, uno compra y al otro se le deshace todo y se le cancela el pedido.

## Diferencias con el prototipo, y por qué

| En el prototipo | Ahora | Motivo |
|---|---|---|
| Auditoría con las acciones crear, modificar, eliminar y acceso | `ALTA`, `CAMBIO_ESTADO`, `CAMBIO_STOCK` y `BAJA_LOGICA`, con los mismos colores | Son las que guardan los triggers de `08_auditoria.sql`. Los accesos no se registran en la base |
| Stock bajo con «10 unidades o menos» | **Menos de 10** | Es el criterio de C8, de P-E y del panel de Java |
| Sugerencias pendientes | «No disponible» | No hay tabla de sugerencias |
| Trabajadores: activo o inactivo | También «sin cuenta» | Personal sin usuario en la tabla `usuarios`. Las cuentas sin ficha de personal (las de `crear_usuario`) salen con el nombre en blanco |
| Productos: activo o inactivo | Inactivo si lo está el SKU **o su modelo** | Es la regla de `anadir_linea_pedido`: un SKU de un modelo dado de baja no se puede vender |
| Estadísticas | Las cuatro tarjetas son del mes en curso | Así lo dicen sus títulos. Las ventas siguen el criterio de P-A: todo menos los cancelados |

**Sugerencias, Mejoras y Configuración** siguen siendo prototipos con datos de ejemplo, y lo dicen en la página. Para conectarlas harían falta tablas nuevas, y se decidirá entre los tres.

## Cambios en los archivos de Álvaro (los tiene que revisar él)

- **En todas las páginas:**
  - el enlace «Cerrar sesión»;
  - **Lucide fijado en la versión 1.62.0**, con `integrity`, en lugar de `lucide@latest`. Es la última versión publicada hace más de dos semanas, y los 12 iconos del menú se han comprobado en las 11 páginas;
  - `integrity` también en Chart.js 4.4.1.
- **Páginas con datos** (Dashboard, Pedidos, Productos, Inventario, Clientes, Trabajadores, Auditoría y Estadísticas):
  - las filas de ejemplo dejan paso a los datos de la API;
  - la página se identifica con `data-pagina`.
- **`script.js`:** pide los datos a la API. Conserva su filtro (Sugerencias), `pintarDashboard` y los gráficos.
- **Auditoría:** las opciones del filtro son las acciones reales.
- **Configuración:** el texto del umbral dice «menos de 10».
- **Sugerencias, Mejoras y Configuración:** un aviso de «Prototipo».
- **Accesibilidad:** nombres accesibles en buscadores, desplegables, interruptores y gráficos, y el tablero de Mejoras se alcanza con el teclado.
- **`styles.css`:** al final, los estilos del login, del aviso de prototipo y de «No disponible», y el color de «sin cuenta».
- **`pedidosAdmin.html` y `productosAdmin.html`:** el icono de la pestaña apuntaba a una imagen que no existe. Se corrigió igual que lo hizo Berme en su rama.

## Pruebas

`npm test` arranca el servidor en un puerto libre y comprueba, en 16 pruebas:
- la conexión con `web_nova`;
- las cabeceras y el rechazo de un Host ajeno;
- el 401 sin sesión y el 403 con otro rol;
- el login, el logout y el **límite de intentos**;
- las 8 rutas, sin datos sensibles;
- los filtros, el 400, los datos no válidos (400, 413 y 415) y un intento de inyección;
- las rutas con `..`;
- que `web_nova` **no puede pasar a `nova_admin` ni escribir ni leer el hash, aunque falte `READ ONLY`**.

La desactivación de una cuenta con la sesión abierta se prueba aparte. Necesita cambiar un usuario en la base, y `web_nova` no tiene permiso para hacerlo. Los resultados de todas las pruebas, también las del navegador, están en `pruebas/panel-admin/`.

Las contraseñas de las cuentas de prueba se dan al ejecutar, nunca en el código. En PowerShell:

```
$env:PRUEBA_ADMIN_USUARIO = "admin.demo";  $env:PRUEBA_ADMIN_CLAVE = "..."
$env:PRUEBA_OTRO_USUARIO  = "taller.demo"; $env:PRUEBA_OTRO_CLAVE  = "..."
npm test
```

Sin esas variables, las pruebas que las necesitan se saltan y lo avisan.

`npm run test:tienda` hace 23 pruebas de la tienda:
- catálogo frente a PostgreSQL;
- registro, login, límite de intentos y logout;
- clientes y administradores separados;
- datos no válidos y precios manipulados;
- doble clic al crear y al pagar, y dos clientes comprando los últimos pares a la vez;
- falta de stock a mitad del pago;
- historial privado;
- que la compra sale en el panel.

**Registran clientes y crean pedidos de verdad**, así que solo se ejecutan si se confirma que la base es desechable:

```
$env:PRUEBA_TIENDA_BASE_DESECHABLE = "si"
npm run test:tienda
```

## Limitaciones conocidas

- **Tiempo de respuesta del login:** tarda algo más si el usuario existe, porque `iniciar_sesion` (script 02) solo calcula el bcrypt en ese caso. El límite de intentos reduce lo que se puede aprovechar.
- **Límite de intentos:** como cuenta por nombre de usuario, alguien que conozca un nombre puede bloquearlo 5 minutos fallando a propósito.
- **Al reiniciar el servidor** se olvidan las sesiones y el contador de intentos.
- **Sin internet:** el panel se queda sin iconos ni gráficos, porque las dos librerías vienen de una CDN.

**De la tienda:**
- **La identidad del cliente la pone el servidor.** Las funciones de compra reciben el `id_cliente` de la sesión; la base comprueba que el pedido es suyo, pero no sabe quién está al otro lado. Es el mismo límite que ya documenta la prueba G6 de `09_pruebas.sql`.
- **Pedidos pendientes olvidados:** si alguien cierra el navegador en mitad del pago, su pedido se queda pendiente (sin stock descontado) y cuenta en «Ventas» del dashboard, igual que un pendiente creado desde Java. Si cierra solo la ventana del pedido, la web lo cancela.
- **La dirección de entrega** se guarda en la ficha del cliente, porque `pedidos` no tiene columna de dirección. Un pedido antiguo enseña la dirección actual.
- **El registro dice si un correo ya existe**, y no hay verificación por correo.
- **En la auditoría** las compras web salen con el usuario «(sin sesión)», porque el cliente no es un usuario de la tabla `usuarios`. El detalle dice para qué cliente es.
