// Pruebas del login unico y del portal del trabajador (npm run test:portal).
//
// Necesitan PostgreSQL con los scripts instalados, tambien el 22 y el 23.
// Las contrasenas NO se escriben aqui: se dan al ejecutar. En PowerShell,
// desde servidor-admin:
//   $env:PRUEBA_ADMIN_USUARIO = "admin.demo";  $env:PRUEBA_ADMIN_CLAVE = "..."
//   $env:PRUEBA_OTRO_USUARIO  = "taller.demo"; $env:PRUEBA_OTRO_CLAVE  = "..."   (un trabajador)
//   $env:PRUEBA_COMERCIAL_USUARIO = "tienda.demo"; $env:PRUEBA_COMERCIAL_CLAVE = "..."  (opcional)
//
// Las que CAMBIAN la base (avanzan pedidos, cambian stock, registran un
// cliente de la tienda) solo se lanzan con una base DESECHABLE:
//   $env:PRUEBA_TIENDA_BASE_DESECHABLE = "si"
// Las que desactivan una cuenta o le cambian el rol necesitan, ademas, un
// superusuario de esa base desechable (web_nova no puede tocar usuarios).
// Crean su propia cuenta de trabajador, prueba.portal.<hora>:
//   $env:PRUEBA_SUPERUSUARIO = "postgres"; $env:PRUEBA_SUPERUSUARIO_CLAVE = "..." (si la pide)
// Sin esas variables, las pruebas que las necesitan se saltan (y lo dicen).

// En las pruebas, el bloqueo por intentos dura 1,5 s en lugar de 5 minutos.
// Tiene que ponerse antes de cargar el servidor.
const BLOQUEO_PRUEBA_MS = 1500;
process.env.BLOQUEO_LOGIN_MS = String(BLOQUEO_PRUEBA_MS);
// El conector de Odoo se prueba sin configurar, aunque el .env diga otra cosa
delete process.env.ODOO_URL;
delete process.env.ODOO_DB;
delete process.env.ODOO_API_KEY;
// Y el recibo por correo, sin enviar nada
delete process.env.RESEND_API_KEY;
delete process.env.CORREO_PROVEEDOR;

const test = require('node:test');
const assert = require('node:assert');
const crypto = require('node:crypto');
const http = require('node:http');
const { once } = require('node:events');
const { Client } = require('pg');
const app = require('../servidor');
const bd = require('../bd');
const odoo = require('../odoo');

const ADMIN = process.env.PRUEBA_ADMIN_USUARIO;
const CLAVE_ADMIN = process.env.PRUEBA_ADMIN_CLAVE;
const TRABAJADOR = process.env.PRUEBA_OTRO_USUARIO;
const CLAVE_TRABAJADOR = process.env.PRUEBA_OTRO_CLAVE;
const COMERCIAL = process.env.PRUEBA_COMERCIAL_USUARIO;
const CLAVE_COMERCIAL = process.env.PRUEBA_COMERCIAL_CLAVE;
const SUPER = process.env.PRUEBA_SUPERUSUARIO;
const CLAVE_SUPER = process.env.PRUEBA_SUPERUSUARIO_CLAVE;

const sinAdmin = !(ADMIN && CLAVE_ADMIN) && 'faltan PRUEBA_ADMIN_USUARIO y PRUEBA_ADMIN_CLAVE';
const sinTrabajador = !(TRABAJADOR && CLAVE_TRABAJADOR) && 'faltan PRUEBA_OTRO_USUARIO y PRUEBA_OTRO_CLAVE (un trabajador)';
const sinComercial = !(COMERCIAL && CLAVE_COMERCIAL) && 'faltan PRUEBA_COMERCIAL_USUARIO y PRUEBA_COMERCIAL_CLAVE';
const sinDesechable = process.env.PRUEBA_TIENDA_BASE_DESECHABLE !== 'si'
  && 'cambian la base: solo con una base desechable (PRUEBA_TIENDA_BASE_DESECHABLE=si)';
const sinEscritura = sinTrabajador || sinAdmin || sinDesechable
  || (!bd.poolTienda && 'falta la tienda (TIENDA_PGUSER y TIENDA_PGPASSWORD): crea los pedidos de prueba');
const sinSuper = sinDesechable || (!SUPER && 'falta PRUEBA_SUPERUSUARIO (cambia cuentas en la base desechable)');

const RUTAS_ADMIN = ['dashboard', 'pedidos', 'productos', 'inventario', 'clientes', 'trabajadores', 'auditoria', 'estadisticas'];
const RUTAS_PORTAL = ['resumen', 'pedidos', 'inventario', 'personalizados'];
const PAGINAS_PORTAL = ['trabajador.html', 'pedidosTrabajador.html', 'inventarioTrabajador.html', 'personalizadosTrabajador.html'];
const DOS_HORAS = 2 * 60 * 60 * 1000;

let servidor;
let base;

test.before(async () => {
  servidor = app.listen(0, '127.0.0.1');
  await once(servidor, 'listening');
  base = `http://127.0.0.1:${servidor.address().port}`;
});

test.after(async () => {
  servidor.close();
  await bd.pool.end();
  if (bd.poolTienda) await bd.poolTienda.end();
});

// ---------------------------------------------------------------------
// Ayudas
// ---------------------------------------------------------------------
async function entrar(usuario, contrasena) {
  const respuesta = await fetch(base + '/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario, contrasena })
  });
  const cookie = (respuesta.headers.get('set-cookie') || '').split(';')[0];
  return { codigo: respuesta.status, cookie, datos: await respuesta.json() };
}

function pedir(ruta, cookie, cabeceras = {}) {
  if (cookie) cabeceras.Cookie = cookie;
  return fetch(base + ruta, { headers: cabeceras, redirect: 'manual' });
}

// Un PATCH como los del portal (JSON)
function cambiar(ruta, cookie, cuerpo, tipo = 'application/json') {
  const cabeceras = { Cookie: cookie };
  if (tipo) cabeceras['Content-Type'] = tipo;
  return fetch(base + ruta, { method: 'PATCH', headers: cabeceras, body: JSON.stringify(cuerpo), redirect: 'manual' });
}

function avanzar(idPedido, cookie, estado) {
  return cambiar(`/api/trabajador/pedidos/${idPedido}/estado`, cookie, { estado });
}

// Lecturas directas en PostgreSQL, con la conexion de solo lectura del panel
async function leer(sql, parametros) {
  return bd.consultarSoloLectura(async (cliente) => (await cliente.query(sql, parametros)).rows);
}

async function estadoDe(idPedido) {
  return (await leer('SELECT estado FROM public.pedidos WHERE id_pedido = $1', [idPedido]))[0].estado;
}

async function stockDe(idSku, idNave) {
  return (await leer('SELECT cantidad FROM public.existencias WHERE id_producto_sku = $1 AND id_nave = $2',
    [idSku, idNave]))[0].cantidad;
}

async function ultimoEvento() {
  return (await leer('SELECT COALESCE(max(id_evento), 0) AS id FROM public.log_eventos'))[0].id;
}

// Los eventos de auditoria apuntados despues de "desde", con el usuario
async function eventosDesde(desde) {
  return leer(`
    SELECT l.accion, u.username, l.detalle
    FROM public.log_eventos l LEFT JOIN public.usuarios u ON u.id_usuario = l.id_usuario
    WHERE l.id_evento > $1 ORDER BY l.id_evento`, [desde]);
}

// Una consulta con un rol de PostgreSQL concreto, con la conexion de web_nova
// y SIN READ ONLY: lo que se prueba son los permisos de ese rol
async function comoRol(rol, sql, parametros) {
  const cliente = await bd.pool.connect();
  try {
    await cliente.query('BEGIN');
    if (rol) await cliente.query(`SET LOCAL ROLE ${rol}`);
    await cliente.query(sql, parametros);
    return 'permitido';
  } catch (error) {
    return error.code === 'P0001' ? error.message : error.code;
  } finally {
    await cliente.query('ROLLBACK').catch(() => {});
    cliente.release();
  }
}

// Cambios en las cuentas, con el superusuario de la base desechable
async function comoSuperusuario(sql, parametros) {
  const cliente = new Client({ user: SUPER, password: () => CLAVE_SUPER || '' });
  await cliente.connect();
  try {
    return (await cliente.query(sql, parametros)).rows;
  } finally {
    await cliente.end();
  }
}

// Una cuenta de trabajador nueva (solo con superusuario), con su contrasena
async function trabajadorNuevo() {
  const usuario = `prueba.portal.${Date.now()}.${crypto.randomInt(1000)}`;
  const clave = crypto.randomBytes(12).toString('hex');
  await comoSuperusuario("SELECT public.crear_usuario($1, 'trabajador')", [usuario]);
  await comoSuperusuario('SELECT public.establecer_password($1, $2)', [usuario, clave]);
  return { usuario, clave };
}

// --- La tienda, para tener pedidos confirmados de verdad (como un cliente)
function navegadorTienda() {
  const nav = { cookie: '' };
  nav.pedir = async (metodo, ruta, cuerpo, cookieForzada) => {
    const cabeceras = {};
    const cookie = cookieForzada ?? nav.cookie;
    if (cookie) cabeceras.Cookie = cookie;
    if (cuerpo !== undefined) cabeceras['Content-Type'] = 'application/json';
    const respuesta = await fetch(base + ruta, {
      method: metodo, headers: cabeceras, redirect: 'manual',
      body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo)
    });
    for (const linea of respuesta.headers.getSetCookie()) {
      const par = linea.split(';')[0];
      if (par.startsWith('sesion_tienda=')) nav.cookie = par === 'sesion_tienda=' ? '' : par;
    }
    const texto = await respuesta.text();
    let datos;
    try { datos = JSON.parse(texto); } catch { datos = texto; }
    return { codigo: respuesta.status, datos };
  };
  return nav;
}

const CLAVE_CLIENTE = 'clave-de-prueba-portal-1';
let numeroCliente = 0;
async function clienteNuevo() {
  const nav = navegadorTienda();
  numeroCliente += 1;
  nav.email = `portal.${Date.now()}.${numeroCliente}@example.com`;
  const r = await nav.pedir('POST', '/api/tienda/registro', {
    nombre: `Cliente portal ${numeroCliente}`, email: nav.email, contrasena: CLAVE_CLIENTE, direccion: 'Calle Portal 1, Madrid'
  });
  assert.equal(r.codigo, 201, JSON.stringify(r.datos));
  return nav;
}

// Un SKU con stock que no se haya usado en esta ejecucion
const usados = new Set();
async function tallaConStock() {
  const catalogo = (await navegadorTienda().pedir('GET', '/api/tienda/catalogo')).datos.modelos;
  for (const modelo of catalogo) {
    for (const variante of modelo.variantes) {
      for (const talla of variante.tallas) {
        if (talla.stock >= 3 && !usados.has(talla.sku)) {
          usados.add(talla.sku);
          return talla;
        }
      }
    }
  }
  throw new Error('No quedan tallas con stock: vuelve a montar la base desechable');
}

// Un pedido CONFIRMADO, comprado y pagado en la tienda por un cliente nuevo
async function pedidoConfirmado() {
  const cliente = await clienteNuevo();
  const talla = await tallaConStock();
  const pedido = (await cliente.pedir('POST', '/api/tienda/pedidos', {
    clave: crypto.randomUUID(), lineas: [{ sku: talla.sku, cantidad: 1 }], direccion: 'Calle Portal 1, Madrid'
  })).datos;
  const pago = await cliente.pedir('POST', `/api/tienda/pedidos/${pedido.id}/pago`, { resultado: 'aceptado' });
  assert.equal(pago.datos.estado, 'confirmado');
  return { cliente, pedido };
}

// =====================================================================
// 1-3. El login unico
// =====================================================================
test('1. login del administrador -> panel de administracion', { skip: sinAdmin }, async () => {
  const login = await entrar(ADMIN, CLAVE_ADMIN);
  assert.equal(login.codigo, 200);
  assert.equal(login.datos.rol, 'administrador');
  assert.equal(login.datos.destino, '/admin.html');
  assert.match(login.cookie, /^sesion_nova=[0-9a-f]{64}$/);
  assert.equal((await pedir('/admin.html', login.cookie)).status, 200);
  assert.equal((await pedir('/api/admin/dashboard', login.cookie)).status, 200);
  // El portal no es suyo: ni las paginas ni la API
  assert.equal((await pedir('/trabajador/trabajador.html', login.cookie)).status, 302);
  assert.equal((await pedir('/api/trabajador/resumen', login.cookie)).status, 403);
});

test('2. login del trabajador -> portal del trabajador', { skip: sinTrabajador }, async () => {
  const login = await entrar(TRABAJADOR, CLAVE_TRABAJADOR);
  assert.equal(login.codigo, 200);
  assert.equal(login.datos.rol, 'trabajador', 'PRUEBA_OTRO_USUARIO tiene que ser un trabajador');
  assert.equal(login.datos.destino, '/trabajador/trabajador.html');
  assert.equal(login.datos.accesoPanel, false);
  for (const pagina of PAGINAS_PORTAL) {
    const respuesta = await pedir('/trabajador/' + pagina, login.cookie);
    assert.equal(respuesta.status, 200, pagina);
    assert.equal(respuesta.headers.get('x-frame-options'), 'DENY', pagina);
  }
  assert.equal((await pedir('/trabajador/styles.css', login.cookie)).status, 200);
  assert.equal((await pedir('/trabajador/script.js', login.cookie)).status, 200);
  // /trabajador y /trabajador/ llevan a la pagina de inicio del portal
  assert.equal((await pedir('/trabajador/', login.cookie)).headers.get('location'), '/trabajador/trabajador.html');
  // /api/sesion dice a donde ir
  const sesion = await (await pedir('/api/sesion', login.cookie)).json();
  assert.equal(sesion.destino, '/trabajador/trabajador.html');
});

test('3. contrasena incorrecta -> 401 con un mensaje claro y sin sesion', async () => {
  for (const usuario of [TRABAJADOR || 'taller.demo', 'usuario.que.no.existe']) {
    const login = await entrar(usuario, 'esta-no-es-la-contrasena');
    assert.equal(login.codigo, 401);
    assert.equal(login.cookie, '');
    assert.equal(login.datos.error, 'Usuario o contraseña incorrectos');
  }
  // Datos que no valen: 400, tambien sin sesion
  assert.equal((await entrar('', 'x')).codigo, 400);
  assert.equal((await entrar('a', '')).codigo, 400);
});

test('un usuario con un rol sin panel web (comercial) -> acceso denegado y sin sesion', { skip: sinComercial }, async () => {
  const login = await entrar(COMERCIAL, CLAVE_COMERCIAL);
  assert.equal(login.codigo, 403);
  assert.equal(login.cookie, '');
  assert.match(login.datos.error, /^Acceso denegado: .*\(comercial\) no tiene ningún panel web\.$/);
});

test('el limite de intentos tambien vale para el trabajador (429, y despues puede entrar)', { skip: sinTrabajador }, async () => {
  // Un acierto primero: el contador empieza de cero (la prueba 3 ya fallo una vez)
  assert.equal((await entrar(TRABAJADOR, CLAVE_TRABAJADOR)).codigo, 200);
  for (let i = 1; i <= 5; i++) {
    assert.equal((await entrar(TRABAJADOR, 'clave-mala-' + i)).codigo, 401);
  }
  const bloqueado = await entrar(TRABAJADOR, CLAVE_TRABAJADOR);
  assert.equal(bloqueado.codigo, 429);
  assert.equal(bloqueado.cookie, '');
  await new Promise((resolver) => setTimeout(resolver, BLOQUEO_PRUEBA_MS + 200));
  assert.equal((await entrar(TRABAJADOR, CLAVE_TRABAJADOR)).codigo, 200);
});

// =====================================================================
// 4. Cuenta desactivada (y rol cambiado) con la sesion abierta
// =====================================================================
test('4. usuario desactivado: no entra (mismo mensaje) y su sesion abierta deja de valer', { skip: sinSuper }, async () => {
  const cuenta = await trabajadorNuevo();
  const login = await entrar(cuenta.usuario, cuenta.clave);
  assert.equal(login.codigo, 200);
  assert.equal((await pedir('/api/trabajador/resumen', login.cookie)).status, 200);

  await comoSuperusuario('UPDATE public.usuarios SET activo = false WHERE username = $1', [cuenta.usuario]);
  // La misma cookie: la API y las paginas lo rechazan en ese momento
  const api = await pedir('/api/trabajador/resumen', login.cookie);
  assert.equal(api.status, 401);
  assert.equal((await api.json()).error, 'Tu sesión ya no es válida. Vuelve a entrar.');
  // Y la sesion se ha borrado: aunque se reactive, esa cookie ya no vale
  await comoSuperusuario('UPDATE public.usuarios SET activo = true WHERE username = $1', [cuenta.usuario]);
  assert.equal((await pedir('/api/trabajador/resumen', login.cookie)).status, 401);
  assert.equal((await pedir('/trabajador/trabajador.html', login.cookie)).status, 302);

  // Desactivada, no puede volver a entrar: 401 con el mismo mensaje que una
  // contrasena mala (no se dice que la cuenta existe)
  await comoSuperusuario('UPDATE public.usuarios SET activo = false WHERE username = $1', [cuenta.usuario]);
  const otraVez = await entrar(cuenta.usuario, cuenta.clave);
  assert.equal(otraVez.codigo, 401);
  assert.equal(otraVez.cookie, '');
  assert.equal(otraVez.datos.error, 'Usuario o contraseña incorrectos');

  // Desactivada en mitad de una pagina del portal: la pagina tambien la rechaza
  await comoSuperusuario('UPDATE public.usuarios SET activo = true WHERE username = $1', [cuenta.usuario]);
  const nueva = await entrar(cuenta.usuario, cuenta.clave);
  assert.equal((await pedir('/trabajador/pedidosTrabajador.html', nueva.cookie)).status, 200);
  await comoSuperusuario('UPDATE public.usuarios SET activo = false WHERE username = $1', [cuenta.usuario]);
  const pagina = await pedir('/trabajador/pedidosTrabajador.html', nueva.cookie);
  assert.equal(pagina.status, 302);
  assert.equal(pagina.headers.get('location'), '/login.html');
});

test('a un trabajador con la sesion abierta se le cambia el rol: 403, sesion borrada y sin panel', { skip: sinSuper }, async () => {
  const cuenta = await trabajadorNuevo();
  const login = await entrar(cuenta.usuario, cuenta.clave);
  assert.equal((await pedir('/api/trabajador/pedidos', login.cookie)).status, 200);

  // Pasa a comercial: el rol de la sesion ya no coincide con el de la base
  await comoSuperusuario(
    "UPDATE public.usuarios SET id_rol = (SELECT id_rol FROM public.roles WHERE nombre = 'comercial') WHERE username = $1",
    [cuenta.usuario]);
  assert.equal((await pedir('/api/trabajador/pedidos', login.cookie)).status, 403);
  assert.equal((await pedir('/api/trabajador/pedidos', login.cookie)).status, 401); // la sesion ya se borro
  // Ni con una sesion nueva: un comercial no tiene panel web
  const comercial = await entrar(cuenta.usuario, cuenta.clave);
  assert.equal(comercial.codigo, 403);
  assert.equal(comercial.cookie, '');

  // Pasa a administrador: entra en el panel, no en el portal
  await comoSuperusuario(
    "UPDATE public.usuarios SET id_rol = (SELECT id_rol FROM public.roles WHERE nombre = 'administrador') WHERE username = $1",
    [cuenta.usuario]);
  const admin = await entrar(cuenta.usuario, cuenta.clave);
  assert.equal(admin.datos.destino, '/admin.html');
  assert.equal((await pedir('/api/trabajador/resumen', admin.cookie)).status, 403);
  await comoSuperusuario('UPDATE public.usuarios SET activo = false WHERE username = $1', [cuenta.usuario]);
});

// =====================================================================
// 5-6. Cierre de sesion y caducidad
// =====================================================================
test('5. despues del logout la sesion del trabajador ya no sirve (API y paginas)', { skip: sinTrabajador }, async () => {
  const login = await entrar(TRABAJADOR, CLAVE_TRABAJADOR);
  assert.equal((await pedir('/api/trabajador/resumen', login.cookie)).status, 200);
  const salir = await fetch(base + '/api/logout', { method: 'POST', headers: { Cookie: login.cookie } });
  assert.equal(salir.status, 200);
  assert.match(salir.headers.get('set-cookie'), /^sesion_nova=;/); // el navegador borra la cookie
  assert.equal((await pedir('/api/trabajador/resumen', login.cookie)).status, 401);
  const pagina = await pedir('/trabajador/trabajador.html', login.cookie);
  assert.equal(pagina.status, 302);
  assert.equal(pagina.headers.get('location'), '/login.html');
});

test('6. la sesion caduca a las 2 horas (adelantando el reloj)', { skip: sinTrabajador }, async (t) => {
  const login = await entrar(TRABAJADOR, CLAVE_TRABAJADOR);
  assert.match(login.cookie, /^sesion_nova=/);
  const ahora = Date.now();
  const reloj = t.mock.method(Date, 'now', () => ahora + DOS_HORAS - 60 * 1000);
  assert.equal((await pedir('/api/trabajador/resumen', login.cookie)).status, 200, 'a la 1 h 59 min sigue valiendo');
  reloj.mock.mockImplementation(() => ahora + DOS_HORAS + 1000);
  assert.equal((await pedir('/api/trabajador/resumen', login.cookie)).status, 401, 'a las 2 h y 1 s ya no vale');
  reloj.mock.restore();
  // Y se ha borrado: con el reloj normal tampoco vale
  assert.equal((await pedir('/api/trabajador/resumen', login.cookie)).status, 401);
  assert.equal((await pedir('/trabajador/trabajador.html', login.cookie)).status, 302);
});

// =====================================================================
// 7-8. El trabajador no entra en el panel de administracion
// =====================================================================
test('7. trabajador -> paginas del panel de administracion: a la pagina de acceso', { skip: sinTrabajador }, async () => {
  const login = await entrar(TRABAJADOR, CLAVE_TRABAJADOR);
  for (const pagina of ['/admin.html', '/pedidosAdmin.html', '/auditoriaAdmin.html', '/script.js', '/']) {
    const respuesta = await pedir(pagina, login.cookie);
    assert.equal(respuesta.status, 302, pagina);
  }
  assert.equal((await pedir('/admin.html', login.cookie)).headers.get('location'), '/login.html');
  // Su sesion sigue valiendo para su portal
  assert.equal((await pedir('/api/trabajador/resumen', login.cookie)).status, 200);
});

test('8. trabajador -> /api/admin/*: 403 en todas, tambien en Marcar en reparto', { skip: sinTrabajador }, async () => {
  const login = await entrar(TRABAJADOR, CLAVE_TRABAJADOR);
  for (const ruta of RUTAS_ADMIN) {
    const respuesta = await pedir('/api/admin/' + ruta, login.cookie);
    assert.equal(respuesta.status, 403, ruta);
    assert.equal((await respuesta.json()).error, 'Tu usuario no tiene permiso para el panel de administración');
  }
  const reparto = await fetch(base + '/api/admin/pedidos/1/reparto', {
    method: 'POST', headers: { Cookie: login.cookie, 'Content-Type': 'application/json' }, body: '{}'
  });
  assert.equal(reparto.status, 403);
  // Con mayusculas o con la ruta escrita de otra forma, igual
  assert.equal((await pedir('/API/ADMIN/dashboard', login.cookie)).status, 403);
  assert.equal((await pedir('/api/admin/./pedidos', login.cookie)).status, 403);
});

test('sin sesion, el portal pide entrar: 401 en la API y la pagina de acceso en las paginas', async () => {
  for (const ruta of RUTAS_PORTAL) {
    assert.equal((await pedir('/api/trabajador/' + ruta)).status, 401, ruta);
  }
  assert.equal((await pedir('/API/TRABAJADOR/resumen')).status, 401);
  for (const pagina of PAGINAS_PORTAL.concat('script.js', 'styles.css', 'img/Nova%20Logo.png')) {
    const respuesta = await pedir('/trabajador/' + pagina);
    assert.equal(respuesta.status, 302, pagina);
    assert.equal(respuesta.headers.get('location'), '/login.html');
  }
  assert.equal((await pedir('/Trabajador/trabajador.html')).status, 302);
  assert.equal((await pedir('/trabajador')).headers.get('location'), '/trabajador/trabajador.html');
  // La pagina de acceso es publica y es la misma para todos
  assert.equal((await pedir('/login.html')).status, 200);
});

// =====================================================================
// 9. Lo que si puede hacer el trabajador
// =====================================================================
test('9a. el trabajador lee el resumen, los pedidos, el inventario y los personalizados, sin datos sensibles', { skip: sinTrabajador }, async () => {
  const login = await entrar(TRABAJADOR, CLAVE_TRABAJADOR);
  for (const ruta of RUTAS_PORTAL) {
    const respuesta = await pedir('/api/trabajador/' + ruta, login.cookie);
    assert.equal(respuesta.status, 200, ruta);
    assert.equal(respuesta.headers.get('cache-control'), 'no-store', ruta);
    const texto = await respuesta.text();
    assert.doesNotMatch(texto, /"(dni|password_hash|password|hash|email|telefono|direccion_entrega)"|\$2[aby]\$/i, ruta);
  }
  const resumen = await (await pedir('/api/trabajador/resumen', login.cookie)).json();
  assert.deepEqual(Object.keys(resumen).sort(), ['enPreparacion', 'pedidosHoy', 'porPreparar', 'stockBajo']);
  // Los pedidos son los mismos que dice la base (solo los que ya estan confirmados o despues)
  const pedidos = await (await pedir('/api/trabajador/pedidos', login.cookie)).json();
  const enLaBase = await leer(
    "SELECT count(*) AS n FROM public.pedidos WHERE estado IN ('confirmado', 'en_preparacion', 'enviado', 'entregado')");
  assert.equal(pedidos.length, enLaBase[0].n);
  assert.ok(pedidos.every((p) => ['confirmado', 'en_preparacion', 'enviado', 'entregado'].includes(p.estado)));
  const inventario = await (await pedir('/api/trabajador/inventario', login.cookie)).json();
  assert.equal(inventario.length, (await leer('SELECT count(*) AS n FROM public.existencias'))[0].n);
  const personalizados = await (await pedir('/api/trabajador/personalizados', login.cookie)).json();
  assert.ok(Array.isArray(personalizados.pedidos) && Array.isArray(personalizados.configuraciones));
});

test('9b. el trabajador avanza un pedido paso a paso hasta entregado y el stock no cambia', { skip: sinEscritura }, async () => {
  const { cliente, pedido } = await pedidoConfirmado();
  // El stock de ese SKU (en todas las naves) antes de avanzar
  const stockTotal = async () => (await leer(
    'SELECT sum(e.cantidad) AS total FROM public.existencias e JOIN public.linea_pedido l USING (id_producto_sku) WHERE l.id_pedido = $1',
    [pedido.id]))[0].total;
  const stockAntes = await stockTotal();
  const login = await entrar(TRABAJADOR, CLAVE_TRABAJADOR);

  for (const estado of ['en_preparacion', 'enviado', 'entregado']) {
    const respuesta = await avanzar(pedido.id, login.cookie, estado);
    assert.equal(respuesta.status, 200, estado);
    assert.deepEqual(await respuesta.json(), { id_pedido: pedido.id, referencia: pedido.referencia, estado });
    assert.equal(await estadoDe(pedido.id), estado);
  }
  // Entregado ya no avanza
  const fin = await avanzar(pedido.id, login.cookie, 'entregado');
  assert.equal(fin.status, 400);
  assert.equal((await fin.json()).error, 'Un pedido en estado entregado no se puede avanzar');
  assert.equal(await stockTotal(), stockAntes);
  // El cliente lo ve en "Mis pedidos"
  const detalle = (await cliente.pedir('GET', `/api/tienda/pedidos/${pedido.id}`)).datos;
  assert.equal(detalle.estado, 'entregado');
});

test('9c. el trabajador cambia la cantidad de unas existencias', { skip: sinEscritura }, async () => {
  const login = await entrar(TRABAJADOR, CLAVE_TRABAJADOR);
  const [fila] = await leer('SELECT id_producto_sku AS sku, id_nave AS nave, cantidad FROM public.existencias ORDER BY id_existencia DESC LIMIT 1');
  const nueva = fila.cantidad + 3;
  const respuesta = await cambiar(`/api/trabajador/inventario/${fila.sku}/${fila.nave}`, login.cookie, { cantidad: nueva });
  assert.equal(respuesta.status, 200);
  assert.deepEqual(await respuesta.json(), { id_producto_sku: fila.sku, id_nave: fila.nave, cantidad: nueva });
  assert.equal(await stockDe(fila.sku, fila.nave), nueva);
  // A 0 tambien se puede (agotado)
  assert.equal((await cambiar(`/api/trabajador/inventario/${fila.sku}/${fila.nave}`, login.cookie, { cantidad: 0 })).status, 200);
  assert.equal(await stockDe(fila.sku, fila.nave), 0);
  await cambiar(`/api/trabajador/inventario/${fila.sku}/${fila.nave}`, login.cookie, { cantidad: fila.cantidad });
  // Unas existencias que no existen: 404
  assert.equal((await cambiar('/api/trabajador/inventario/999999999/1', login.cookie, { cantidad: 1 })).status, 404);
});

test('9d. dos clics a la vez en "Avanzar estado": solo uno avanza', { skip: sinEscritura }, async () => {
  const { pedido } = await pedidoConfirmado();
  const login = await entrar(TRABAJADOR, CLAVE_TRABAJADOR);
  const desde = await ultimoEvento();
  const respuestas = await Promise.all([1, 2, 3].map(() => avanzar(pedido.id, login.cookie, 'en_preparacion')));
  const codigos = respuestas.map((r) => r.status).sort();
  assert.deepEqual(codigos, [200, 400, 400]);
  assert.equal(await estadoDe(pedido.id), 'en_preparacion');
  const cambios = (await eventosDesde(desde)).filter((e) => e.accion === 'CAMBIO_ESTADO');
  assert.equal(cambios.length, 1);
});

// =====================================================================
// 10. Manipular parametros, cookie o rol no cambia nada
// =====================================================================
test('10a. parametros manipulados: saltarse pasos, estados raros, ids y cantidades que no valen', { skip: sinEscritura }, async () => {
  const { pedido } = await pedidoConfirmado();
  const login = await entrar(TRABAJADOR, CLAVE_TRABAJADOR);
  const desde = await ultimoEvento();

  // Saltarse un paso o volver atras: 400 y el pedido no cambia
  for (const estado of ['enviado', 'entregado']) {
    const r = await avanzar(pedido.id, login.cookie, estado);
    assert.equal(r.status, 400, estado);
    assert.equal((await r.json()).error, 'Solo se puede pasar de confirmado a en_preparacion');
  }
  for (const estado of ['cancelado', 'pendiente', 'confirmado', '', null, 5, ['en_preparacion'], { estado: 'en_preparacion' }]) {
    assert.equal((await avanzar(pedido.id, login.cookie, estado)).status, 400, JSON.stringify(estado));
  }
  assert.equal(await estadoDe(pedido.id), 'confirmado');

  // Ids que no valen: 400; uno que no existe: 404
  for (const id of ['abc', '0', '-1', '1.5', '9999999999', '1e3', '%20']) {
    assert.equal((await avanzar(id, login.cookie, 'en_preparacion')).status, 400, id);
  }
  assert.equal((await avanzar('999999999', login.cookie, 'en_preparacion')).status, 404);
  // Un pedido pendiente o cancelado no se puede avanzar
  const [pendiente] = await leer("SELECT id_pedido AS id FROM public.pedidos WHERE estado = 'pendiente' LIMIT 1");
  assert.equal((await avanzar(pendiente.id, login.cookie, 'en_preparacion')).status, 400);
  assert.equal(await estadoDe(pendiente.id), 'pendiente');

  // Cantidades que no valen
  const [fila] = await leer('SELECT id_producto_sku AS sku, id_nave AS nave, cantidad FROM public.existencias ORDER BY id_existencia LIMIT 1');
  const ruta = `/api/trabajador/inventario/${fila.sku}/${fila.nave}`;
  for (const cantidad of [-1, 1.5, '5', null, 100000, 2 ** 31, [], {}]) {
    assert.equal((await cambiar(ruta, login.cookie, { cantidad })).status, 400, JSON.stringify(cantidad));
  }
  assert.equal(await stockDe(fila.sku, fila.nave), fila.cantidad);

  // Sin JSON (como un formulario de otra web): 415
  assert.equal((await cambiar(ruta, login.cookie, { cantidad: 1 }, 'text/plain')).status, 415);
  assert.equal((await cambiar(`/api/trabajador/pedidos/${pedido.id}/estado`, login.cookie, { estado: 'en_preparacion' }, null)).status, 415);
  // JSON roto: 400
  const roto = await fetch(base + ruta, {
    method: 'PATCH', headers: { Cookie: login.cookie, 'Content-Type': 'application/json' }, body: '{"cantidad":'
  });
  assert.equal(roto.status, 400);
  // Las rutas de lectura no aceptan cambios, ni las de cambio, GET
  assert.equal((await fetch(base + '/api/trabajador/inventario', { method: 'PATCH', headers: { Cookie: login.cookie } })).status, 404);
  assert.equal((await pedir(`/api/trabajador/pedidos/${pedido.id}/estado`, login.cookie)).status, 404);

  // Nada de esto ha dejado rastro en la auditoria
  assert.deepEqual(await eventosDesde(desde), []);
});

test('10b. el usuario y el rol salen de la sesion: los del cuerpo o las cabeceras se ignoran', { skip: sinEscritura }, async () => {
  const { pedido } = await pedidoConfirmado();
  const login = await entrar(TRABAJADOR, CLAVE_TRABAJADOR);
  const [admin] = await leer('SELECT id_usuario AS id FROM public.usuarios WHERE username = $1', [ADMIN]);
  const desde = await ultimoEvento();
  const r = await cambiar(`/api/trabajador/pedidos/${pedido.id}/estado`, login.cookie, {
    estado: 'en_preparacion', id_usuario: admin.id, idUsuario: admin.id, usuario: ADMIN, rol: 'administrador'
  });
  assert.equal(r.status, 200);
  const [evento] = await eventosDesde(desde);
  assert.equal(evento.username, TRABAJADOR); // a nombre del trabajador, no del administrador

  // Una cabecera o una cookie con el rol no dan permiso de administrador
  const conRol = await pedir('/api/admin/dashboard', `${login.cookie}; rol=administrador`, { 'X-Rol': 'administrador' });
  assert.equal(conRol.status, 403);
  // Un login con el rol en el cuerpo no cambia el rol de la sesion
  const truco = await fetch(base + '/api/login', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario: TRABAJADOR, contrasena: CLAVE_TRABAJADOR, rol: 'administrador', destino: '/admin.html' })
  });
  const datos = await truco.json();
  assert.equal(datos.rol, 'trabajador');
  assert.equal(datos.destino, '/trabajador/trabajador.html');
});

test('10c. cookies manipuladas: un token inventado o cambiado no vale', { skip: sinTrabajador }, async () => {
  const login = await entrar(TRABAJADOR, CLAVE_TRABAJADOR);
  const token = login.cookie.split('=')[1];
  const cambiado = (token[0] === 'a' ? 'b' : 'a') + token.slice(1);
  for (const cookie of [
    `sesion_nova=${crypto.randomBytes(32).toString('hex')}`,
    `sesion_nova=${cambiado}`,
    `sesion_nova=${token.slice(0, 32)}`,
    'sesion_nova=',
    `sesion_tienda=${token}` // la cookie de la tienda no vale para el portal
  ]) {
    assert.equal((await pedir('/api/trabajador/resumen', cookie)).status, 401, cookie);
  }
  // Con otro nombre de host, 400 (DNS rebinding), aunque lleve la cookie buena
  const codigo = await new Promise((resolver, fallar) => {
    const peticion = http.request(base + '/api/trabajador/resumen', {
      headers: { Host: 'atacante.example', Cookie: login.cookie }
    }, (respuesta) => {
      respuesta.resume();
      resolver(respuesta.statusCode);
    });
    peticion.on('error', fallar);
    peticion.end();
  });
  assert.equal(codigo, 400);
  // Salir de la carpeta del portal: 400
  assert.equal((await pedir('/trabajador/..%2Fadmin.html', login.cookie)).status, 400);
  assert.equal((await pedir('/trabajador/%E0', login.cookie)).status, 400);
  assert.equal((await pedir('/trabajador/no-existe.html', login.cookie)).status, 404);
});

test('10d. en PostgreSQL, portal_trabajador solo hace lo que dice el 23', { skip: sinAdmin || sinComercial || sinTrabajador }, async () => {
  const ids = Object.fromEntries((await leer(
    'SELECT username, id_usuario FROM public.usuarios WHERE username = ANY($1)', [[ADMIN, TRABAJADOR, COMERCIAL]]
  )).map((f) => [f.username, f.id_usuario]));
  const avanzarComo = (id) => comoRol('portal_trabajador',
    "SELECT * FROM public.avanzar_pedido_trabajador($1, 1, 'en_preparacion')", [id]);
  const stockComo = (id) => comoRol('portal_trabajador',
    'SELECT * FROM public.ajustar_existencias_trabajador($1, 1, 1, 5)', [id]);

  // Las funciones comprueban el usuario: con el id del administrador, del
  // comercial o de nadie, no hacen nada
  for (const id of [ids[ADMIN], ids[COMERCIAL], 999999, null]) {
    assert.equal(await avanzarComo(id), 'Usuario no autorizado', String(id));
    assert.equal(await stockComo(id), 'Usuario no autorizado', String(id));
  }
  // No puede escribir por su cuenta ni leer lo que no necesita
  for (const sql of [
    "UPDATE public.pedidos SET estado = 'enviado' WHERE false",
    'UPDATE public.existencias SET cantidad = 0 WHERE false',
    "INSERT INTO public.log_eventos (tabla_afectada, accion) VALUES ('x', 'x')",
    'DELETE FROM public.pedidos WHERE false',
    'SELECT password_hash FROM public.usuarios',
    'SELECT dni FROM public.personal',
    'SELECT email FROM public.clientes',
    'SELECT direccion_entrega FROM public.clientes',
    'SELECT count(*) FROM public.log_eventos',
    'SELECT count(*) FROM public.cuentas_cliente',
    'SELECT public.marcar_pedido_en_reparto(1, 1)',
    "SELECT public.realizar_compra('X', 1, 1, 1, 1)",
    "SELECT public.iniciar_sesion('admin.demo', 'x')"
  ]) {
    assert.equal(await comoRol('portal_trabajador', sql), '42501', sql);
  }
  // Lee lo que ensena el portal
  assert.equal(await comoRol('portal_trabajador', 'SELECT referencia, personalizacion, fecha_objetivo FROM public.pedidos LIMIT 1'), 'permitido');
  // Nadie mas puede usar las funciones del portal
  for (const rol of [null, 'panel_lectura', 'panel_reparto']) {
    assert.equal(await comoRol(rol, "SELECT * FROM public.avanzar_pedido_trabajador(1, 1, 'en_preparacion')"), '42501', String(rol));
    assert.equal(await comoRol(rol, 'SELECT * FROM public.ajustar_existencias_trabajador(1, 1, 1, 1)'), '42501', String(rol));
  }
  // web_nova sigue sin poder pasar a los roles de Java ni al superusuario
  for (const rol of ['nova_admin', 'nova_trabajador', 'nova_comercial', 'postgres']) {
    assert.equal(await comoRol(null, `SET LOCAL ROLE ${rol}`), '42501', rol);
  }
  // La tienda tampoco
  if (bd.poolTienda) {
    await assert.rejects(bd.operarEnTienda((c) => c.query("SELECT * FROM public.avanzar_pedido_trabajador(1, 1, 'en_preparacion')")), { code: '42501' });
    await assert.rejects(bd.operarEnTienda((c) => c.query('SET LOCAL ROLE portal_trabajador')), { code: '42501' });
  }
});

// =====================================================================
// 11. Auditoria con el usuario correcto
// =====================================================================
test('11. la auditoria apunta los cambios del portal a nombre del trabajador', { skip: sinEscritura }, async () => {
  const { pedido } = await pedidoConfirmado();
  const login = await entrar(TRABAJADOR, CLAVE_TRABAJADOR);
  const [fila] = await leer('SELECT id_producto_sku AS sku, id_nave AS nave, cantidad FROM public.existencias ORDER BY id_existencia LIMIT 1 OFFSET 3');
  const desde = await ultimoEvento();

  assert.equal((await avanzar(pedido.id, login.cookie, 'en_preparacion')).status, 200);
  assert.equal((await cambiar(`/api/trabajador/inventario/${fila.sku}/${fila.nave}`, login.cookie, { cantidad: fila.cantidad + 1 })).status, 200);

  const eventos = await eventosDesde(desde);
  assert.equal(eventos.length, 2, JSON.stringify(eventos));
  assert.equal(eventos[0].accion, 'CAMBIO_ESTADO');
  assert.equal(eventos[0].username, TRABAJADOR);
  assert.match(eventos[0].detalle, new RegExp(`^Pedido ${pedido.referencia}: confirmado -> en_preparacion`));
  assert.equal(eventos[1].accion, 'CAMBIO_STOCK');
  assert.equal(eventos[1].username, TRABAJADOR);
  assert.equal(eventos[1].detalle, `SKU ${fila.sku}: ${fila.cantidad} -> ${fila.cantidad + 1}`);

  // El administrador lo ve en su Auditoria con ese usuario
  const admin = await entrar(ADMIN, CLAVE_ADMIN);
  const auditoria = await (await pedir('/api/admin/auditoria?texto='
    + encodeURIComponent(`${pedido.referencia}: confirmado -> en_preparacion`), admin.cookie)).json();
  assert.equal(auditoria.filas.length, 1);
  assert.equal(auditoria.filas[0].usuario, TRABAJADOR);
  // Y la sesion de la base no se queda "abierta" con el trabajador
  const [sinSesion] = await leer("SELECT COALESCE(current_setting('nova.id_usuario', true), '') AS valor");
  assert.equal(sinSesion.valor, '');
});

// =====================================================================
// Clientes de la tienda y personal, separados en los dos sentidos
// =====================================================================
test('un cliente de la tienda no es un usuario interno: ni su sesion ni sus credenciales sirven en el portal', { skip: sinDesechable || (!bd.poolTienda && 'falta la tienda') }, async () => {
  const cliente = await clienteNuevo();
  const token = cliente.cookie.split('=')[1];
  for (const cookie of [cliente.cookie, `sesion_nova=${token}`]) {
    assert.equal((await pedir('/api/trabajador/resumen', cookie)).status, 401, cookie);
    assert.equal((await pedir('/trabajador/trabajador.html', cookie)).status, 302, cookie);
  }
  const login = await entrar(cliente.email, CLAVE_CLIENTE);
  assert.equal(login.codigo, 401);
  assert.equal(login.cookie, '');
});

test('un trabajador no es un cliente de la tienda: ni su sesion ni sus credenciales sirven en la tienda', { skip: sinTrabajador || (!bd.poolTienda && 'falta la tienda') }, async () => {
  const login = await entrar(TRABAJADOR, CLAVE_TRABAJADOR);
  const token = login.cookie.split('=')[1];
  const tienda = navegadorTienda();
  assert.equal((await tienda.pedir('GET', '/api/tienda/pedidos', undefined, login.cookie)).codigo, 401);
  assert.equal((await tienda.pedir('GET', '/api/tienda/pedidos', undefined, `sesion_tienda=${token}`)).codigo, 401);
  assert.equal((await tienda.pedir('POST', '/api/tienda/login', { email: TRABAJADOR, contrasena: CLAVE_TRABAJADOR })).codigo, 401);
  // La cookie del personal no lleva la ruta de la tienda: son almacenes distintos
  assert.match((await entrar(TRABAJADOR, CLAVE_TRABAJADOR)).cookie, /^sesion_nova=/);
});

// =====================================================================
// El conector de Odoo de Berme
// =====================================================================
test('el conector de Odoo esta desactivado sin configuracion, lo dice y no inventa respuestas', async () => {
  assert.equal(odoo.odooConfigurado, false);
  assert.match(odoo.resumen(), /^Conector de Odoo desactivado/);
  await assert.rejects(
    odoo.crearPedidoOdoo({ referencia: 'PRUEBA', cliente: { nombre: 'x', email: 'x@example.com' }, lineas: [] }),
    /Conector de Odoo desactivado/);
  // Las rutas de pedidos.js (crear pedidos y Odoo) no estan montadas
  const crear = await fetch(base + '/api/pedidos', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '{}' });
  assert.equal(crear.status, 404);
  assert.equal((await pedir('/api/pedidos/odoo-pendientes')).status, 404);
});
