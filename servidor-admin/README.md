# Servidor del panel de administración, del portal del trabajador y de la tienda web

Conecta con PostgreSQL el panel de Álvaro (`01_Interfaces/admin/`), el portal del trabajador de Berme (`01_Interfaces/trabajador/`) y la tienda web (`01_Interfaces/cliente/`). Es el único servidor del proyecto.

```
Navegador ──► http://127.0.0.1:3000 ──► Node + Express (esta carpeta) ──► PostgreSQL
  acceso: /login.html                    · login único del personal (administrador y trabajador)
  panel: /admin.html                     · páginas del panel y /api/admin/...       usuario web_nova (solo lectura)
         /analisisAdmin.html             · el dashboard de Python (Streamlit, puerto 8501) dentro del panel
  portal: /trabajador/                   · portal de Berme y /api/trabajador/...    usuario web_nova (rol portal_trabajador)
  tienda: /tienda/                       · web cliente y /api/tienda/...            usuario tienda_nova
```

- El navegador **nunca** habla con PostgreSQL. Pide datos a este servidor, y es el servidor el que hace las consultas.
- El mismo servidor entrega las páginas del panel y de la tienda. Así, páginas y API tienen el mismo origen y no hace falta CORS.
- Solo escucha en `127.0.0.1`: no se puede abrir desde otro ordenador.
- **Personal y clientes van separados:** el panel y el portal comparten el login único y la cookie del personal (`sesion_nova`); la tienda tiene su usuario de PostgreSQL, su cookie (`sesion_tienda`) y sus rutas. El panel solo lee, con una excepción: el botón «Marcar en reparto», que pasa un pedido confirmado a `enviado` a través de una única función (script 22, ver «La única escritura del panel»). El portal lee con su propio rol y solo cambia algo con las dos funciones del script 23 (ver «El portal del trabajador»).
- Los importes y el stock los calculan los triggers de PostgreSQL. El panel solo los lee; la tienda escribe únicamente a través de las funciones del script 20 (ver «La tienda web»).

## Puesta en marcha

Hace falta Node 20.6 o posterior (probado con Node 24.15) y una base con los scripts instalados.

1. Crear el rol de solo lectura y el usuario de conexión. Pide una contraseña:
   ```
   psql -U postgres -d nova_sneakers -f 02_Acceso_Datos/sql/19_usuario_web.sql
   ```
2. Instalar las tres dependencias, `express`, `pg` y `nodemailer` (solo para Ethereal), con las versiones exactas de `package-lock.json`:
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
   psql -U postgres -d nova_sneakers -f 02_Acceso_Datos/sql/20_tienda_web.sql
   psql -U postgres -d nova_sneakers -f 02_Acceso_Datos/sql/21_catalogo_web.sql
   ```
7. Escribir en `.env` `TIENDA_PGUSER=tienda_nova` y `TIENDA_PGPASSWORD` con la contraseña del paso 6, y volver a arrancar.
8. Abrir `http://127.0.0.1:3000/tienda/`. Al arrancar, la consola dice si la tienda está configurada. Sin esas dos variables, el panel funciona igual y la tienda enseña el catálogo, pero no deja comprar.

**Para el botón «Marcar en reparto»** del panel, después del 09, el 19 y el 20 (se puede repetir):

9. ```
   psql -U postgres -d nova_sneakers -f 02_Acceso_Datos/sql/22_reparto_panel.sql
   ```

**Para el portal del trabajador**, después del 22 (se puede repetir):

10. ```
    psql -U postgres -d nova_sneakers -f 02_Acceso_Datos/sql/23_portal_trabajador.sql
    ```
    No pide contraseñas: usa el mismo `web_nova`. Se entra por la misma página, `http://127.0.0.1:3000/login.html`, con `taller.demo`.

**Para el recibo por correo** (opcional):

11. Escribir en `.env` la clave de [Resend](https://resend.com) y el remitente, y volver a arrancar:
    ```
    RESEND_API_KEY=re_...
    RESEND_FROM=NOVA Sneakers <onboarding@resend.dev>
    ```
    Mientras no haya un dominio verificado en Resend, solo llegan los correos dirigidos al correo de la propia cuenta de Resend: hay que registrarse en la tienda con ese correo para recibir el recibo. Sin estas variables, la compra funciona igual y la consola dice que el recibo no se ha enviado.
12. **Solo para desarrollo**, para probar el recibo sin enviar correos reales: `CORREO_PROVEEDOR=ethereal` en `.env` (no necesita claves). En el primer envío, Nodemailer crea una cuenta temporal de [Ethereal](https://ethereal.email): el correo no llega a nadie, la consola escribe `Vista previa del recibo WEB-…: <url>` y en «Mis pedidos», al ver el detalle del pedido, sale el enlace «Ver recibo de prueba (Ethereal)». Con `NODE_ENV=production` se niega y no se envía nada. Sin `CORREO_PROVEEDOR` (o con `resend`) todo sigue como en el paso 11.

**El conector de Odoo de Berme** (`odoo.js`) se queda **desactivado** mientras falte alguna de `ODOO_URL`, `ODOO_DB` y `ODOO_API_KEY` en `.env`: no se llama a ningún servidor y la consola lo dice al arrancar. Desde este ordenador no se llega a ningún Odoo, así que no se ha probado contra uno de verdad.

## Archivos

| Archivo | Qué hace |
|---|---|
| `servidor.js` | Arranca Express y entrega las páginas del panel, del portal y de la tienda. Tiene el login único, el logout, las 8 rutas de lectura del panel y la de «Marcar en reparto», monta las rutas del portal y comprueba la sesión y el rol, contra la base, en cada petición |
| `bd.js` | Las dos conexiones con PostgreSQL. `consultarSoloLectura` (panel) abre `BEGIN ... READ ONLY` y `SET LOCAL ROLE panel_lectura`; `marcarEnReparto` (solo el botón del panel) abre una transacción aparte con `SET LOCAL ROLE panel_reparto`; `consultarComoTrabajador` y `cambiarComoTrabajador` (portal) hacen lo mismo con `portal_trabajador`; `operarEnTienda` (tienda) abre una transacción con `SET LOCAL ROLE tienda_web`. Las cinco usan `enTransaccion`, que abre la transacción, cambia de rol y hace `COMMIT` o `ROLLBACK` |
| `consultas.js` | Las 8 consultas SQL del panel. Salen de `12_consultas_panel.sql` y de la auditoría de `08_auditoria.sql` |
| `tienda.js` | Las rutas de la tienda (`/api/tienda/...`): comprueban los datos y llaman a las funciones del script 20 con el cliente de la sesión |
| `consultas-tienda.js` | El SQL de la tienda: catálogo, cuenta, historial y las llamadas a las funciones de compra |
| `correo.js` | El recibo por correo de cada compra pagada: con la API de Resend (`fetch` de Node) o, solo en desarrollo, con Ethereal (Nodemailer) |
| `rutas-trabajador.js` | **De Berme.** Las rutas del portal (`/api/trabajador/...`). Leen con `portal_trabajador` y sus dos cambios llaman a las funciones del script 23 con el usuario de la sesión |
| `odoo.js` | **De Berme.** El conector con la API JSON-2 de Odoo. Desactivado sin `ODOO_URL`, `ODOO_DB` y `ODOO_API_KEY` |
| `pedidos.js` | **De Berme.** Rutas para crear pedidos y enviarlos a Odoo. **No se montan** (ver «Lo que falta del portal») |
| `sesiones.js` | Las sesiones: un token aleatorio en una cookie HttpOnly, guardado en memoria. Dos almacenes separados: `sesion_nova` (personal: panel y portal) y `sesion_tienda` (clientes) |
| `intentos.js` | El límite de intentos de login (panel y tienda) |
| `pruebas/api.test.js` | Pruebas automáticas del panel (`npm test`). Solo leen |
| `pruebas/tienda.test.js` | Pruebas automáticas de la tienda (`npm run test:tienda`). Crean clientes y pedidos: **solo con una base desechable** |
| `pruebas/portal.test.js` | Pruebas del login único y del portal (`npm run test:portal`). Las que cambian algo, **solo con una base desechable** |
| `../01_Interfaces/admin/login.html` y `login.js` | La página de acceso única del personal |
| `../01_Interfaces/trabajador/` | **De Berme.** Las cuatro páginas del portal, su `script.js` y su `styles.css` (sacada de la hoja del panel de Álvaro; solo quedan las reglas que usa el portal) |

## Las rutas

Todas devuelven JSON. Las de `/api/admin/` necesitan una sesión de administrador, y las de `/api/trabajador/`, una de trabajador: sin sesión responden **401**, y con otro rol, **403**.

| Ruta | Filtros (`?nombre=valor`) | De dónde sale la consulta |
|---|---|---|
| `GET /api/estado` | — | Comprueba la conexión. Es pública: no devuelve datos del negocio |
| `POST /api/login` | JSON `{usuario, contrasena}` | `iniciar_sesion` (02): la contraseña la comprueba PostgreSQL con bcrypt. Responde con el rol y `destino`, el panel al que ir. **401** si no es correcta (o la cuenta está desactivada), **403** si su rol no tiene panel web (sin sesión). Tras 5 fallos, **429** |
| `POST /api/logout` | — | Borra la sesión |
| `GET /api/sesion` | — | Quién ha entrado, con qué rol y su `destino` |
| `GET /api/admin/dashboard` | — | P-A (ventas), P-B (pedidos por estado), C8 (stock bajo), los últimos 5 pedidos y las ventas por día (últimos 30 días) |
| `GET /api/admin/pedidos` | `estado`, `texto` | C5 |
| `GET /api/admin/productos` | `estado`, `texto` | Los JOIN de `csv_stock` (16). Precio = `precio_base + suplemento_precio`, el mismo que cobra `anadir_linea_pedido` |
| `GET /api/admin/inventario` | `estado`, `texto` | C8 sin agrupar, por SKU y nave |
| `GET /api/admin/clientes` | `estado`, `texto` | `csv_clientes` (16), sin la dirección de entrega |
| `GET /api/admin/trabajadores` | `estado`, `texto` | P-H, más `personal` para el nombre y el puesto. Nunca el DNI |
| `GET /api/admin/auditoria` | `accion`, `texto` | Los últimos 100 eventos de `log_eventos` |
| `GET /api/admin/estadisticas` | — | P-A del mes en curso, P-B, P-C y los ingresos por mes |
| `POST /api/admin/pedidos/:id/reparto` | JSON `{}` | `marcar_pedido_en_reparto` (22): un pedido **confirmado** pasa a `enviado`. **200** con el pedido, **404** si no existe, **409** si no está confirmado, **415** si no llega JSON |

Las del portal del trabajador (`rutas-trabajador.js`, de Berme):

| Ruta | Datos | Qué hace |
|---|---|---|
| `GET /api/trabajador/resumen` | — | Pedidos por preparar y en preparación, SKU con menos de 5 pares y pedidos de hoy |
| `GET /api/trabajador/pedidos` | — | Los pedidos confirmados, en preparación, enviados y entregados, con su cliente (solo el nombre) |
| `PATCH /api/trabajador/pedidos/:id/estado` | JSON `{estado}` | `avanzar_pedido_trabajador` (23): un paso adelante, `confirmado` → `en_preparacion` → `enviado` → `entregado`. **400** si el paso no vale, **404** si no existe, **415** sin JSON |
| `GET /api/trabajador/inventario` | — | Las existencias por nave, modelo, color, talla y SKU |
| `PATCH /api/trabajador/inventario/:idSku/:idNave` | JSON `{cantidad}` | `ajustar_existencias_trabajador` (23): la cantidad nueva, de 0 a 99999. **400**, **404** o **415** igual que arriba |
| `GET /api/trabajador/personalizados` | — | Los pedidos personalizados y las configuraciones X-Nova |

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

### La única escritura del panel: «Marcar en reparto» (script 22)

Es una prueba: el administrador pulsa el botón en un pedido confirmado y el cliente lo ve «En reparto» en la tienda.

- **La función** `marcar_pedido_en_reparto(p_id_usuario, p_id_pedido)` es `SECURITY DEFINER` con `search_path` fijo. Comprueba que el usuario existe, está activo y es administrador, y que el pedido existe y está `confirmado`; entonces lo pasa a `enviado`. Los triggers de 03 no tocan el stock (ya se descontó al confirmar).
- **La auditoría** (08) apunta un `CAMBIO_ESTADO` a nombre del administrador. Para que `usuario_sesion()` lo reconozca, la función usa lo mismo que `iniciar_sesion`: la variable `nova.id_usuario` con el id y su firma, y al terminar la deja como estaba.
- **El rol** `panel_reparto` no tiene login ni puede leer o escribir ninguna tabla: **solo ejecuta esa función**. `web_nova` pasa a él con `SET LOCAL ROLE` (sin heredar), igual que a `panel_lectura`. Nadie más puede llamarla: ni `PUBLIC`, ni `panel_lectura`, ni `tienda_web` o `tienda_nova`, ni los roles de Java.
- **El servidor** la llama en una transacción de escritura aparte, solo para esta ruta, detrás de `soloAdministrador` (que vuelve a mirar el rol en la base). El usuario sale de la sesión, nunca del navegador, y solo acepta `Content-Type: application/json`, así que un formulario de otra web no puede lanzarla. Las demás rutas siguen con `READ ONLY` y `panel_lectura`.

### El portal del trabajador (script 23)

- **El rol** `portal_trabajador` no tiene login. `web_nova` pasa a él con `SET LOCAL ROLE` (sin heredar), igual que a `panel_lectura` y a `panel_reparto`.
- **Lee solo lo que enseña el portal:** algunas columnas de pedidos, el nombre de los clientes, las existencias, las naves, los SKU, los colores, los modelos y las configuraciones X-Nova. No ve `password_hash`, `dni`, `email`, `telefono`, `direccion_entrega` ni la auditoría.
- **No escribe en ninguna tabla por su cuenta.** Sus dos cambios van por funciones `SECURITY DEFINER` con `search_path` fijo:
  - `avanzar_pedido_trabajador(usuario, pedido, estado)`: bloquea el pedido (`FOR UPDATE`) y solo deja avanzar un paso. Con dos clics a la vez, uno avanza y el otro recibe 400. No toca el stock;
  - `ajustar_existencias_trabajador(usuario, sku, nave, cantidad)`: pone la cantidad nueva, de 0 a 99999.
- **Las dos comprueban** que el usuario existe, está activo y es **trabajador**, y dejan el cambio en `log_eventos` a su nombre (`CAMBIO_ESTADO` o `CAMBIO_STOCK`), con el mismo mecanismo de `nova.id_usuario` que el 22.
- **El servidor** lee en transacciones `READ ONLY` y hace cada cambio en una transacción aparte. El usuario sale de la sesión, nunca del cuerpo de la petición, y los cambios solo aceptan `Content-Type: application/json`.
- Nadie más puede llamar a esas funciones: ni `PUBLIC`, ni `web_nova` sin `SET ROLE`, ni `panel_lectura`, `panel_reparto` o `tienda_web`.

### Login único y roles

Hay **una sola página de acceso** para el personal, `login.html`. El servidor decide adónde va cada uno según el rol de la tabla `roles`, siguiendo la matriz de permisos de `02_Acceso_Datos/documentacion/README.md`:

| Rol | Cuenta de demostración | Al entrar | Por qué |
|---|---|---|---|
| `administrador` | `admin.demo` | Panel de administración (`/admin.html`) | Ve todo, también la auditoría, y es el único que marca pedidos en reparto desde el panel |
| `trabajador` | `taller.demo` | Portal del trabajador (`/trabajador/`) | Prepara pedidos y controla el almacén: avanza el estado de los pedidos y corrige el stock. No vende ni ve la auditoría |
| `comercial` | `tienda.demo` | **Acceso denegado** (403, sin sesión) | Ninguna página web es suya |

- **Cada uno solo entra en su panel.** El administrador no entra en el portal (ya tiene su panel) y el trabajador no entra en el panel: sus páginas le llevan a `login.html` y todas las rutas `/api/admin/` le responden 403.
- **Contraseña mal, usuario que no existe o cuenta desactivada:** 401 con el mismo mensaje, «Usuario o contraseña incorrectos». Así no se sabe qué cuentas existen ni cuáles están desactivadas.
- **Rol sin panel** (comercial): la contraseña es buena, pero no se crea ninguna sesión y la página dice «Acceso denegado: el usuario … (comercial) no tiene ningún panel web.».
- **El rol nunca sale del navegador.** Lo guarda la sesión, en la memoria del servidor, y en cada petición se vuelve a mirar en la base. No hay nada que cambiar en el JavaScript, la cookie o la petición para tener otro rol.
- **Clientes y personal no se mezclan:** las cuentas de la tienda (`cuentas_cliente`) no sirven en `login.html`, ni las del personal en la tienda, y cada cookie solo vale en su almacén de sesiones.

### Login y sesiones

- **Login:**
  - la contraseña la comprueba PostgreSQL;
  - el mensaje de error es el mismo exista o no el usuario, y esté o no desactivado.
- **Límite de intentos** (`intentos.js`):
  - tras 5 fallos seguidos con un mismo nombre de usuario, el servidor responde 429 durante 5 minutos, aunque la contraseña sea la buena;
  - cuenta igual exista o no la cuenta, así que no delata qué usuarios hay;
  - al acertar, el contador vuelve a cero;
  - la duración se puede cambiar con la variable `BLOQUEO_LOGIN_MS` (las pruebas la ponen en 1,5 s).
- **Sesión:**
  - es un token aleatorio de 32 bytes en una cookie `HttpOnly` y `SameSite=Strict`;
  - caduca a las 2 horas y se pierde al reiniciar el servidor;
  - la contraseña no se guarda.
- **En cada petición a `/api/admin/` y a `/api/trabajador/`, y en cada página del panel y del portal,** se vuelve a mirar en la base si la cuenta sigue activa y sigue teniendo ese rol:
  - si se ha desactivado, la sesión se borra y la respuesta es 401 (las páginas llevan a `login.html`);
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
- **Páginas:** sin sesión de administrador solo se entregan `login.html`, `login.js`, `styles.css` y las imágenes del panel. Las páginas del portal (`/trabajador/...`), incluidos su CSS, su JavaScript y sus imágenes, solo se entregan con una sesión de trabajador. Cualquier otra página lleva a `login.html`.
- **Botón «Atrás»:** después de cerrar sesión, una página que el navegador tuviera guardada se vuelve a pedir al servidor, que manda al login.
- **Datos:** el panel pinta con `textContent`, no con `innerHTML`. Un dato que contenga HTML se ve como texto y no se ejecuta.
- **Librerías de la CDN:** Lucide (1.62.0) y Chart.js (4.4.1) tienen la versión fija y la huella de integridad (`integrity`). Si el archivo de la CDN cambiara, el navegador no lo ejecutaría.
- **Respuestas:** no llevan hashes, contraseñas, DNI ni direcciones. Los errores internos se apuntan en la consola del servidor y el navegador recibe un mensaje genérico.

## La tienda web

La web cliente (`01_Interfaces/cliente/`) se sirve en `/tienda/`. Su JavaScript (`js/tienda.js`) pide los datos a estas rutas:

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

**Recibo por correo (`correo.js`):**
- Cuando el pago aceptado ya está guardado en PostgreSQL, el servidor responde al cliente y **después** manda el recibo con la API de Resend: un `POST` con `Authorization: Bearer <clave>` y el JSON `{from, to, subject, html, text}`.
- Va al correo **con el que se registró el cliente**, leído de la base, nunca uno que mande el navegador.
- Lleva la referencia `WEB-…`, cada zapatilla con su color, talla, cantidad, precio y subtotal, el total, la dirección de entrega y el aviso de que es un pago simulado de un proyecto académico y no se ha cobrado nada. En el HTML, los datos que escribe el cliente van escapados.
- **Nunca hace fallar la compra.** Sin `RESEND_API_KEY` no se envía nada y la consola lo dice en una línea. Si Resend falla o tarda más de 5 s, el pedido sigue confirmado, la respuesta al cliente es la misma y solo se apunta el error. La clave no se escribe nunca en la consola.
- El pago rechazado o cancelado no manda correo. Si llegan varios pagos del mismo pedido a la vez (doble clic), un bloqueo de PostgreSQL (`pg_advisory_xact_lock`) los pone en fila y solo el que lo confirma manda el recibo.
- `RESEND_URL` (opcional, por defecto `https://api.resend.com/emails`) sirve para que las pruebas usen un Resend simulado.
- **Ethereal (solo desarrollo, `CORREO_PROVEEDOR=ethereal`):** el mismo recibo (la misma función `crearRecibo`) se manda por SMTP a una cuenta temporal que crea `nodemailer.createTestAccount()`. Sus credenciales solo están en memoria: no se escriben en la consola ni en ningún archivo. La URL de `nodemailer.getTestMessageUrl(info)` se guarda en memoria con el pedido, sale en la consola y `GET /api/tienda/pedidos/:id` la devuelve como `reciboPrueba` (solo al dueño del pedido y solo en modo Ethereal). Si Ethereal no está (sin red, error o más de 10 s), la compra sigue confirmada y solo se apunta el error. Al reiniciar el servidor se olvidan la cuenta y los enlaces.

**Dobles clics, reintentos y compras a la vez:**
- **Crear el pedido:** el navegador crea una `clave` aleatoria al abrir el checkout, y de ella sale la referencia `WEB-…`. Si la petición llega dos veces, `crear_compra_web` devuelve el mismo pedido, porque `pedidos_referencia_uq` no deja repetirla.
- **Pagar:** `confirmar_compra_web` bloquea el pedido (`FOR UPDATE`). El segundo pago ve que ya está pagado y no hace nada.
- **Los últimos pares:** `descontar_stock` no deja bajar de cero. Si dos clientes pagan a la vez, uno compra y al otro se le deshace todo y se le cancela el pedido.

## Diferencias con el prototipo, y por qué

| En el prototipo | Ahora | Motivo |
|---|---|---|
| Auditoría con las acciones crear, modificar, eliminar y acceso | `ALTA`, `CAMBIO_ESTADO`, `CAMBIO_STOCK` y `BAJA_LOGICA`, con los mismos colores | Son las que guardan los triggers de `08_auditoria.sql`. Los accesos no se registran en la base |
| Stock bajo con «10 unidades o menos» | **Menos de 10** | Es el criterio de C8 y de P-E |
| Stock bajo en el portal del trabajador | **Menos de 5** (`01_Interfaces/trabajador/script.js:185` y `/api/trabajador/resumen`) | El portal de Berme usa su propio umbral: una talla con 5 a 9 pares sale «bajo» en el panel y «suficiente» en el portal. Es una diferencia conocida; no se ha cambiado el código |
| Sugerencias pendientes | «No disponible» | No hay tabla de sugerencias |
| Trabajadores: activo o inactivo | También «sin cuenta» | Personal sin usuario en la tabla `usuarios`. Las cuentas sin ficha de personal (las de `crear_usuario`) salen con el nombre en blanco |
| Productos: activo o inactivo | Inactivo si lo está el SKU **o su modelo** | Es la regla de `anadir_linea_pedido`: un SKU de un modelo dado de baja no se puede vender |
| Estadísticas | Las cuatro tarjetas son del mes en curso | Así lo dicen sus títulos. Las ventas siguen el criterio de P-A: todo menos los cancelados |

**Sugerencias, Mejoras y Configuración** siguen siendo prototipos con datos de ejemplo, y lo dicen en la página. Para conectarlas harían falta tablas nuevas, y se decidirá entre los tres.

## Cambios en los archivos de Álvaro (los tiene que revisar él)

- **En todas las páginas:**
  - el enlace «Cerrar sesión»;
  - **Lucide fijado en la versión 1.62.0**, con `integrity`, en lugar de `lucide@latest`. Es la última versión publicada hace más de dos semanas, y los 12 iconos del menú se comprobaron en las 11 páginas que había antes de «Análisis de datos»;
  - `integrity` también en Chart.js 4.4.1;
  - una línea más en el menú, «Análisis de datos», que lleva a la página nueva `analisisAdmin.html` (el dashboard de Python dentro del panel).
- **Páginas con datos** (Dashboard, Pedidos, Productos, Inventario, Clientes, Trabajadores, Auditoría y Estadísticas):
  - las filas de ejemplo dejan paso a los datos de la API;
  - la página se identifica con `data-pagina`.
- **`script.js`:** pide los datos a la API. Conserva su filtro (Sugerencias), `pintarDashboard` y los gráficos.
- **Auditoría:** las opciones del filtro son las acciones reales.
- **Configuración:** el texto del umbral dice «menos de 10».
- **Sugerencias, Mejoras y Configuración:** un aviso de «Prototipo».
- **Accesibilidad:** nombres accesibles en buscadores, desplegables, interruptores y gráficos, y el tablero de Mejoras se alcanza con el teclado.
- **`styles.css`:** al final, los estilos del login, del aviso de prototipo y de «No disponible», y el color de «sin cuenta».
- **Botón «Marcar en reparto»** (solo se añade; el diseño no cambia):
  - `pedidosAdmin.html`: una columna más, «Reparto», y un aviso vacío encima de la tabla (`role="status"`);
  - `script.js`: el botón en los pedidos confirmados, con la confirmación, el aviso y la recarga de la lista;
  - `styles.css`: al final, el tamaño del botón, su foco y los colores del aviso.
- **`pedidosAdmin.html` y `productosAdmin.html`:** el icono de la pestaña apuntaba a una imagen que no existe. Se corrigió igual que lo hizo Berme en su rama.

## Cambios en los archivos de Berme (los tiene que revisar él)

Sus commits (`b8e5fe1` y `a52341e`, del 11/11) siguen a su nombre. Después:

- **`servidor/` pasa a `servidor-admin/`**, sin cambios en ese commit: sus rutas necesitan Express y un pool de PostgreSQL, y el único servidor es este.
- **`rutas-trabajador.js`:** las mismas rutas, consultas, mensajes y reglas. Cambia cómo llegan a la base: en lugar de `pool.query` con permisos de quien se conectara, lee con `portal_trabajador` y sus dos `UPDATE` pasan a las funciones del script 23 (que comprueban el usuario y dejan la auditoría). Además, los cambios solo aceptan JSON (415) y los ids, como mucho 9 cifras (un número que no cabía en un `integer` daba un error 500 en PostgreSQL).
- **`odoo.js`:** sin configuración ya no llama a `http://localhost:8069` por defecto: se queda desactivado y lo dice.
- **`pedidos.js`:** igual que lo dejó, con un comentario al principio que explica por qué no se monta.
- **Páginas del portal:** el enlace «Cerrar sesión»; Lucide fijado en la 1.62.0 con `integrity` (como el panel) en lugar de `lucide@latest`; nombres accesibles en el buscador, los desplegables y los campos de cantidad. El diseño no cambia.
- **`script.js`:** si la CDN de Lucide no carga, el portal sigue funcionando; con un 401 o un 403 vuelve a `login.html`; y el botón «Atrás» no enseña datos después de cerrar sesión.

## Pruebas

`npm test` arranca el servidor en un puerto libre y comprueba, en 23 pruebas:
- la conexión con `web_nova`;
- las cabeceras y el rechazo de un Host ajeno;
- el 401 sin sesión y el 403 con otro rol;
- el login, el logout y el **límite de intentos**;
- las 8 rutas, sin datos sensibles;
- los filtros, el 400, los datos no válidos (400, 413 y 415) y un intento de inyección;
- las rutas con `..`;
- que `web_nova` **no puede pasar a `nova_admin` ni escribir ni leer el hash, aunque falte `READ ONLY`**;
- «Marcar en reparto»: 401, 403, 404, 409, 415, Host ajeno y `no-store`; que el resto del panel no puede llamar a la función y que `panel_reparto` no lee ni escribe ninguna tabla;
- y, **solo con `PRUEBA_TIENDA_BASE_DESECHABLE=si`**, el 200: un pedido confirmado pasa a `enviado`, el stock no cambia y la auditoría apunta un `CAMBIO_ESTADO` con `admin.demo`. Es la única prueba de `npm test` que cambia algo; sin esa variable se salta.

La desactivación de una cuenta con la sesión abierta se prueba aparte. Necesita cambiar un usuario en la base, y `web_nova` no tiene permiso para hacerlo. Los resultados de todas las pruebas, también las del navegador, están en `01_Interfaces/evidencias/panel-admin/`.

Las contraseñas de las cuentas de prueba se dan al ejecutar, nunca en el código. En PowerShell:

```
$env:PRUEBA_ADMIN_USUARIO = "admin.demo";  $env:PRUEBA_ADMIN_CLAVE = "..."
$env:PRUEBA_OTRO_USUARIO  = "taller.demo"; $env:PRUEBA_OTRO_CLAVE  = "..."
npm test
```

Sin esas variables, las pruebas que las necesitan se saltan y lo avisan.

`npm run test:tienda` hace 39 pruebas de la tienda:
- catálogo frente a PostgreSQL;
- registro, login, límite de intentos y logout;
- clientes y administradores separados;
- datos no válidos y precios manipulados;
- doble clic al crear y al pagar, y dos clientes comprando los últimos pares a la vez;
- falta de stock a mitad del pago;
- historial privado;
- que la compra sale en el panel, y que al marcarla en reparto el cliente la ve como `enviado`;
- el recibo por correo, con un **Resend simulado** en este ordenador (`RESEND_URL` apunta a él y la clave es inventada, aunque el `.env` tenga la de verdad): pago aceptado → un correo al email registrado con la referencia, las líneas y el total; rechazado o cancelado → ninguno; sin clave → ninguno y la compra va bien; Resend responde 500 o no responde → la compra sigue confirmada; doble clic → un solo correo; la clave no sale en la consola;
- el recibo de prueba con `CORREO_PROVEEDOR=ethereal`, **sin red**: en lugar de la cuenta de Ethereal se usa un transporte de Nodemailer que guarda los mensajes en memoria. Pago aceptado → un recibo al email registrado, igual que el de Resend, y `reciboPrueba` en el detalle; rechazado o cancelado → ninguno; doble clic → uno solo; el transporte falla, lanza un error o no responde → la compra sigue confirmada y el stock baja una vez; con `NODE_ENV=production` → se niega.

**Registran clientes y crean pedidos de verdad**, así que solo se ejecutan si se confirma que la base es desechable:

```
$env:PRUEBA_TIENDA_BASE_DESECHABLE = "si"
npm run test:tienda
```

`npm run test:portal` hace 24 pruebas del login único y del portal: el login del administrador y del trabajador, contraseña mal, cuenta desactivada y rol cambiado con la sesión abierta, logout, caducidad a las 2 horas (adelantando el reloj), el trabajador fuera del panel y de las 8 rutas `/api/admin/`, las lecturas y los dos cambios del portal (también con doble clic), parámetros, cookies y roles manipulados, los permisos de `portal_trabajador` en PostgreSQL, la auditoría a nombre del trabajador, clientes y personal separados en los dos sentidos, y el conector de Odoo desactivado.

```
$env:PRUEBA_ADMIN_USUARIO = "admin.demo";  $env:PRUEBA_ADMIN_CLAVE = "..."
$env:PRUEBA_OTRO_USUARIO  = "taller.demo"; $env:PRUEBA_OTRO_CLAVE  = "..."
$env:PRUEBA_COMERCIAL_USUARIO = "tienda.demo"; $env:PRUEBA_COMERCIAL_CLAVE = "..."
$env:PRUEBA_TIENDA_BASE_DESECHABLE = "si"
$env:PRUEBA_SUPERUSUARIO = "postgres"   # y PRUEBA_SUPERUSUARIO_CLAVE si la pide
npm run test:portal
```

Las que avanzan pedidos, cambian el stock o registran un cliente solo se lanzan con `PRUEBA_TIENDA_BASE_DESECHABLE=si`. Las que desactivan una cuenta o le cambian el rol necesitan además `PRUEBA_SUPERUSUARIO`, porque `web_nova` no puede tocar la tabla `usuarios`; crean su propia cuenta de trabajador (`prueba.portal.<hora>`) y la dejan desactivada.

## Limitaciones conocidas

- **Tiempo de respuesta del login:** tarda algo más si el usuario existe, porque `iniciar_sesion` (script 02) solo calcula el bcrypt en ese caso. El límite de intentos reduce lo que se puede aprovechar.
- **Límite de intentos:** como cuenta por nombre de usuario, alguien que conozca un nombre puede bloquearlo 5 minutos fallando a propósito.
- **Al reiniciar el servidor** se olvidan las sesiones y el contador de intentos.
- **Sin internet:** el panel se queda sin iconos ni gráficos, porque las dos librerías vienen de una CDN. El portal, sin iconos.
- **Una sesión del personal por navegador:** el panel y el portal usan la misma cookie, así que entrar con otro usuario en el mismo navegador cierra la sesión anterior.

**Del portal del trabajador (ver también «Lo que falta del portal»):**
- **El stock se puede poner a mano** a cualquier cantidad de 0 a 99999, como lo diseñó Berme. Queda en la auditoría, pero no se comprueba la capacidad de la nave.
- **Avanzar no vuelve atrás:** si un trabajador se equivoca, el estado no se puede deshacer desde la web.

**Lo que falta del portal:**
- **`pedidos.js` no se monta.** Crearía pedidos sin login ni rol, escribe directamente en `pedidos` y `log_eventos` (y `web_nova` no tiene esos permisos) y necesita un Odoo. Según la matriz, el trabajador no crea pedidos. Para usarlo habría que decidir quién lo usa, darle una función como las del 23 y un Odoo de verdad.
- **Odoo:** `odoo.js` no se ha podido probar contra ningún Odoo. Faltan la URL, la base y la clave de la API, y saber qué productos de Odoo corresponden a cada SKU.

**De la tienda:**
- **La identidad del cliente la pone el servidor.** Las funciones de compra reciben el `id_cliente` de la sesión; la base comprueba que el pedido es suyo, pero no sabe quién está al otro lado. Es el mismo límite que ya documenta la prueba G6 de `09_pruebas.sql`.
- **Pedidos pendientes olvidados:** si alguien cierra el navegador en mitad del pago, su pedido se queda pendiente (sin stock descontado) y cuenta en «Ventas» del dashboard, igual que un pendiente creado desde Java. Si cierra solo la ventana del pedido, la web lo cancela.
- **La dirección de entrega** se guarda en la ficha del cliente, porque `pedidos` no tiene columna de dirección. Un pedido antiguo enseña la dirección actual.
- **El registro dice si un correo ya existe**, y no hay verificación por correo.
- **Nodemailer** (10.5.0, la versión exacta de `package.json`) solo se usa con `CORREO_PROVEEDOR=ethereal`, en desarrollo, para mandar un correo sin adjuntos a un buzón falso que no entrega nada.
- **En la auditoría** las compras web salen con el usuario «(sin sesión)», porque el cliente no es un usuario de la tabla `usuarios`. El detalle dice para qué cliente es.
