// Pruebas automaticas de la API del panel (node --test, sin librerias extra).
//
// Necesitan PostgreSQL con los scripts instalados (tambien el 19) y el .env del
// servidor. Las contrasenas de las cuentas de prueba NO se escriben aqui: se
// dan al ejecutar. En PowerShell, desde servidor-admin:
//   $env:PRUEBA_ADMIN_USUARIO = "admin.demo";  $env:PRUEBA_ADMIN_CLAVE = "..."
//   $env:PRUEBA_OTRO_USUARIO  = "taller.demo"; $env:PRUEBA_OTRO_CLAVE  = "..."
//   npm test
// Sin esas variables, las pruebas que las necesitan se saltan (y lo dicen).
//
// Todas solo leen, salvo UNA: la que pulsa "Marcar en reparto" en un pedido
// confirmado y lo deja en "enviado". Esa solo se lanza con una base
// DESECHABLE y la misma variable que las pruebas de la tienda:
//   $env:PRUEBA_TIENDA_BASE_DESECHABLE = "si"

// En las pruebas, el bloqueo por intentos dura 1,5 s en lugar de 5 minutos.
// Tiene que ponerse antes de cargar el servidor.
const BLOQUEO_PRUEBA_MS = 1500;
process.env.BLOQUEO_LOGIN_MS = String(BLOQUEO_PRUEBA_MS);

const test = require('node:test');
const assert = require('node:assert');
const { once } = require('node:events');
const app = require('../servidor');
const bd = require('../bd');

const RUTAS = ['dashboard', 'pedidos', 'productos', 'inventario', 'clientes', 'trabajadores', 'auditoria', 'estadisticas'];
const ADMIN = process.env.PRUEBA_ADMIN_USUARIO;
const CLAVE_ADMIN = process.env.PRUEBA_ADMIN_CLAVE;
const OTRO = process.env.PRUEBA_OTRO_USUARIO;
const CLAVE_OTRO = process.env.PRUEBA_OTRO_CLAVE;
const sinAdmin = !(ADMIN && CLAVE_ADMIN) && 'faltan PRUEBA_ADMIN_USUARIO y PRUEBA_ADMIN_CLAVE';
const sinOtro = !(OTRO && CLAVE_OTRO) && 'faltan PRUEBA_OTRO_USUARIO y PRUEBA_OTRO_CLAVE';
const sinBaseDesechable = sinAdmin || (process.env.PRUEBA_TIENDA_BASE_DESECHABLE !== 'si'
  && 'cambia un pedido: solo con una base desechable (PRUEBA_TIENDA_BASE_DESECHABLE=si)');

let servidor;
let base;

test.before(async () => {
  servidor = app.listen(0, '127.0.0.1'); // puerto libre cualquiera
  await once(servidor, 'listening');
  base = `http://127.0.0.1:${servidor.address().port}`;
});

test.after(async () => {
  servidor.close();
  await bd.pool.end();
});

async function entrar(usuario, contrasena) {
  const respuesta = await fetch(base + '/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario, contrasena })
  });
  const cookie = (respuesta.headers.get('set-cookie') || '').split(';')[0];
  return { codigo: respuesta.status, cookie, datos: await respuesta.json() };
}

function pedir(ruta, cookie) {
  return fetch(base + ruta, { headers: cookie ? { Cookie: cookie } : {}, redirect: 'manual' });
}

// El boton "Marcar en reparto": POST con JSON, como lo manda el panel
function marcarReparto(id, cookie, tipo = 'application/json') {
  const cabeceras = {};
  if (cookie) cabeceras.Cookie = cookie;
  if (tipo) cabeceras['Content-Type'] = tipo;
  return fetch(`${base}/api/admin/pedidos/${id}/reparto`, {
    method: 'POST', headers: cabeceras, body: '{}', redirect: 'manual'
  });
}

// Lecturas directas en PostgreSQL, con la conexion de solo lectura del panel
function leer(sql, parametros) {
  return bd.consultarSoloLectura(async (cliente) => (await cliente.query(sql, parametros)).rows);
}

test('el servidor responde y se conecta con web_nova, no con postgres', async () => {
  const respuesta = await pedir('/api/estado');
  assert.equal(respuesta.status, 200);
  const datos = await respuesta.json();
  assert.equal(datos.baseDeDatos, 'conectada');
  assert.equal(datos.usuarioBaseDeDatos, 'web_nova');
});

test('las respuestas llevan cabeceras de proteccion y la API no se guarda en cache', async () => {
  const pagina = await pedir('/login.html');
  const api = await pedir('/api/estado');
  assert.equal(pagina.headers.get('x-powered-by'), null);
  assert.equal(pagina.headers.get('x-content-type-options'), 'nosniff');
  assert.equal(pagina.headers.get('x-frame-options'), 'DENY');
  assert.equal(api.headers.get('cache-control'), 'no-store');
});

test('una peticion con otro nombre de host se rechaza (DNS rebinding)', async () => {
  // fetch no deja cambiar la cabecera Host, asi que se usa el modulo http
  const http = require('node:http');
  const codigo = await new Promise((resolver, fallar) => {
    http.get(base + '/api/estado', { headers: { Host: 'atacante.example' } }, (respuesta) => {
      respuesta.resume();
      resolver(respuesta.statusCode);
    }).on('error', fallar);
  });
  assert.equal(codigo, 400);
});

test('los datos no validos dan 4xx y no 500', async () => {
  const enviar = (cuerpo, tipo = 'application/json') => fetch(base + '/api/login', {
    method: 'POST', headers: { 'Content-Type': tipo }, body: cuerpo
  });
  assert.equal((await enviar(JSON.stringify({ usuario: 'a\u0000', contrasena: 'x' }))).status, 400);
  assert.equal((await enviar(JSON.stringify({ usuario: 'a', contrasena: 'x'.repeat(200000) }))).status, 413);
  assert.equal((await enviar('{"usuario":"a","contrasena":"b"}', 'application/json; charset=latin1')).status, 415);
});

test('las rutas con .. o mal codificadas dan 400 y lo publico se ve sin sesion', async () => {
  assert.equal((await pedir('/img/..%2Fadmin.html')).status, 400);
  assert.equal((await pedir('/%E0')).status, 400);
  assert.equal((await pedir('/styles.css')).status, 200);
  assert.equal((await pedir('/img/Nova%20Logo.png')).status, 200);
});

test('sin sesion, las 8 rutas responden 401', async () => {
  for (const ruta of RUTAS) {
    assert.equal((await pedir('/api/admin/' + ruta)).status, 401, ruta);
  }
});

test('sin sesion, las paginas del panel llevan al login', async () => {
  const respuesta = await pedir('/admin.html');
  assert.equal(respuesta.status, 302);
  assert.equal(respuesta.headers.get('location'), '/login.html');
  assert.equal((await pedir('/login.html')).status, 200);
});

test('una contrasena incorrecta da 401 y no crea sesion', async () => {
  const login = await entrar(ADMIN || 'admin.demo', 'esta-no-es-la-contrasena');
  assert.equal(login.codigo, 401);
  assert.equal(login.cookie, '');
});

test('un usuario que no es administrador recibe 403', { skip: sinOtro }, async () => {
  const login = await entrar(OTRO, CLAVE_OTRO);
  assert.equal(login.codigo, 200);
  assert.equal(login.datos.accesoPanel, false);
  for (const ruta of RUTAS) {
    assert.equal((await pedir('/api/admin/' + ruta, login.cookie)).status, 403, ruta);
  }
  assert.equal((await pedir('/admin.html', login.cookie)).status, 302); // tampoco ve las paginas
});

test('el administrador recibe JSON de las 8 rutas, sin datos sensibles', { skip: sinAdmin }, async () => {
  const login = await entrar(ADMIN, CLAVE_ADMIN);
  assert.equal(login.codigo, 200);
  for (const ruta of RUTAS) {
    const respuesta = await pedir('/api/admin/' + ruta, login.cookie);
    assert.equal(respuesta.status, 200, ruta);
    const texto = await respuesta.text();
    JSON.parse(texto); // falla si no es JSON valido
    assert.doesNotMatch(texto, /"(dni|password_hash|password|hash|direccion_entrega)"|\$2[aby]\$/i, ruta);
  }
});

test('el dashboard marca las sugerencias como no disponibles y usa el umbral 10', { skip: sinAdmin }, async () => {
  const login = await entrar(ADMIN, CLAVE_ADMIN);
  const datos = await (await pedir('/api/admin/dashboard', login.cookie)).json();
  assert.equal(datos.sugerenciasPendientes, null);
  assert.equal(datos.umbralStockBajo, 10);
  assert.ok(datos.stockBajo.every((fila) => fila.stock < 10));
});

test('los filtros se aplican y un valor no permitido da 400', { skip: sinAdmin }, async () => {
  const login = await entrar(ADMIN, CLAVE_ADMIN);
  const pendientes = await (await pedir('/api/admin/pedidos?estado=pendiente', login.cookie)).json();
  assert.ok(pendientes.filas.every((fila) => fila.estado === 'pendiente'));
  const bajo = await (await pedir('/api/admin/inventario?estado=bajo', login.cookie)).json();
  assert.ok(bajo.filas.every((fila) => fila.stock > 0 && fila.stock < 10));
  const inyeccion = await (await pedir('/api/admin/pedidos?texto=' + encodeURIComponent("' OR '1'='1"), login.cookie)).json();
  assert.equal(inyeccion.filas.length, 0);
  assert.equal((await pedir('/api/admin/pedidos?estado=borrado', login.cookie)).status, 400);
  assert.equal((await pedir('/api/admin/auditoria?accion=crear', login.cookie)).status, 400);
  assert.equal((await pedir('/api/admin/pedidos?texto=%00', login.cookie)).status, 400);
  // _ y % se buscan como letras, no como comodines
  const guion = await (await pedir('/api/admin/pedidos?texto=_', login.cookie)).json();
  assert.ok(guion.filas.every((fila) => (fila.referencia + fila.cliente).includes('_')));
});

test('consultar no puede escribir: la transaccion es de solo lectura', async () => {
  await assert.rejects(
    bd.consultarSoloLectura((cliente) => cliente.query('UPDATE public.pedidos SET estado = estado')),
    { code: '25006' } // cannot execute UPDATE in a read-only transaction
  );
});

test('despues del logout la sesion ya no sirve', { skip: sinAdmin }, async () => {
  const login = await entrar(ADMIN, CLAVE_ADMIN);
  assert.equal((await pedir('/api/admin/pedidos', login.cookie)).status, 200);
  await fetch(base + '/api/logout', { method: 'POST', headers: { Cookie: login.cookie } });
  assert.equal((await pedir('/api/admin/pedidos', login.cookie)).status, 401);
});

test('web_nova no puede pasar a nova_admin ni escribir, aunque falte READ ONLY', async () => {
  // Una transaccion normal (sin READ ONLY): lo que se prueba son los permisos
  const cliente = await bd.pool.connect();
  const intentar = async (sql) => {
    await cliente.query('BEGIN');
    try {
      await cliente.query('SET LOCAL ROLE panel_lectura');
      await cliente.query(sql);
      return 'permitido';
    } catch (error) {
      return error.code; // 42501 = permiso denegado
    } finally {
      await cliente.query('ROLLBACK');
    }
  };
  try {
    await cliente.query('BEGIN');
    await assert.rejects(cliente.query('SET LOCAL ROLE nova_admin'), { code: '42501' });
    await cliente.query('ROLLBACK');

    assert.equal(await intentar('UPDATE public.pedidos SET estado = estado WHERE false'), '42501');
    assert.equal(await intentar('UPDATE public.existencias SET cantidad = cantidad WHERE false'), '42501');
    assert.equal(await intentar("INSERT INTO public.log_eventos (tabla_afectada, accion) VALUES ('x', 'x')"), '42501');
    assert.equal(await intentar('SELECT password_hash FROM public.usuarios'), '42501');
    assert.equal(await intentar('SELECT dni FROM public.personal'), '42501');
    assert.equal(await intentar('SELECT count(*) FROM public.pedidos'), 'permitido');
  } finally {
    cliente.release();
  }
});

// ---------------------------------------------------------------------
// Boton "Marcar en reparto" (POST /api/admin/pedidos/:id/reparto, script 22)
// ---------------------------------------------------------------------
test('reparto: sin sesion responde 401', async () => {
  assert.equal((await marcarReparto(1)).status, 401);
});

test('reparto: un usuario que no es administrador recibe 403', { skip: sinOtro }, async () => {
  const login = await entrar(OTRO, CLAVE_OTRO);
  assert.equal((await marcarReparto(1, login.cookie)).status, 403);
});

test('reparto: 404 si el pedido no existe, 415 sin JSON y las protecciones de siempre', { skip: sinAdmin }, async () => {
  const login = await entrar(ADMIN, CLAVE_ADMIN);
  for (const id of ['999999999', 'abc', '0', '-1', '1.5']) {
    const respuesta = await marcarReparto(id, login.cookie);
    assert.equal(respuesta.status, 404, id);
    assert.equal(respuesta.headers.get('cache-control'), 'no-store');
  }
  // Sin Content-Type JSON (como un formulario de otra web), no se hace nada
  assert.equal((await marcarReparto(1, login.cookie, null)).status, 415);
  assert.equal((await marcarReparto(1, login.cookie, 'text/plain')).status, 415);
  assert.equal((await marcarReparto(1, login.cookie, 'application/x-www-form-urlencoded')).status, 415);
  // Con otro nombre de host, 400 (DNS rebinding), aunque lleve la cookie
  const http = require('node:http');
  const codigo = await new Promise((resolver, fallar) => {
    const peticion = http.request(base + '/api/admin/pedidos/1/reparto', {
      method: 'POST',
      headers: { Host: 'atacante.example', Cookie: login.cookie, 'Content-Type': 'application/json' }
    }, (respuesta) => {
      respuesta.resume();
      resolver(respuesta.statusCode);
    });
    peticion.on('error', fallar);
    peticion.end('{}');
  });
  assert.equal(codigo, 400);
});

test('reparto: un pedido pendiente da 409 y no cambia', { skip: sinAdmin }, async () => {
  const login = await entrar(ADMIN, CLAVE_ADMIN);
  const [pendiente] = await leer("SELECT id_pedido AS id FROM public.pedidos WHERE estado = 'pendiente' ORDER BY id_pedido LIMIT 1");
  const respuesta = await marcarReparto(pendiente.id, login.cookie);
  assert.equal(respuesta.status, 409);
  assert.match((await respuesta.json()).error, /Solo se puede marcar en reparto un pedido confirmado/);
  const [despues] = await leer('SELECT estado FROM public.pedidos WHERE id_pedido = $1', [pendiente.id]);
  assert.equal(despues.estado, 'pendiente');
});

test('reparto: un pedido confirmado pasa a enviado, sin tocar el stock, y la auditoria apunta al administrador', { skip: sinBaseDesechable }, async (t) => {
  const [confirmado] = await leer(
    "SELECT id_pedido AS id, referencia FROM public.pedidos WHERE estado = 'confirmado' ORDER BY id_pedido LIMIT 1");
  if (!confirmado) return t.skip('no queda ningun pedido confirmado: vuelve a montar la base desechable');
  const [stockAntes] = await leer('SELECT sum(cantidad) AS total FROM public.existencias');
  const [ultimo] = await leer('SELECT COALESCE(max(id_evento), 0) AS id FROM public.log_eventos');

  const login = await entrar(ADMIN, CLAVE_ADMIN);
  const respuesta = await marcarReparto(confirmado.id, login.cookie);
  assert.equal(respuesta.status, 200);
  assert.equal(respuesta.headers.get('cache-control'), 'no-store');
  const pedido = await respuesta.json();
  assert.equal(pedido.id, confirmado.id);
  assert.equal(pedido.referencia, confirmado.referencia);
  assert.equal(pedido.estado, 'enviado');

  const [enLaBase] = await leer('SELECT estado FROM public.pedidos WHERE id_pedido = $1', [confirmado.id]);
  assert.equal(enLaBase.estado, 'enviado');
  const [stockDespues] = await leer('SELECT sum(cantidad) AS total FROM public.existencias');
  assert.equal(stockDespues.total, stockAntes.total);
  const eventos = await leer(`
    SELECT l.accion, u.username, l.detalle
    FROM public.log_eventos l LEFT JOIN public.usuarios u ON u.id_usuario = l.id_usuario
    WHERE l.id_evento > $1 ORDER BY l.id_evento`, [ultimo.id]);
  assert.equal(eventos.length, 1, JSON.stringify(eventos));
  assert.equal(eventos[0].accion, 'CAMBIO_ESTADO');
  assert.equal(eventos[0].username, ADMIN);
  assert.match(eventos[0].detalle, new RegExp(`^Pedido ${confirmado.referencia}: confirmado -> enviado`));

  // Otra vez el mismo (doble clic o lista sin recargar): ya no esta confirmado
  assert.equal((await marcarReparto(confirmado.id, login.cookie)).status, 409);
  // Y la lista del panel lo ensena como enviado, sin boton (el id viene en la fila)
  const lista = await (await pedir('/api/admin/pedidos?texto=' + confirmado.referencia, login.cookie)).json();
  assert.equal(lista.filas[0].id, confirmado.id);
  assert.equal(lista.filas[0].estado, 'enviado');
});

test('reparto: el resto del panel sigue siendo de solo lectura', async () => {
  // Las consultas del panel (panel_lectura) no pueden llamar a la funcion
  await assert.rejects(
    bd.consultarSoloLectura((cliente) => cliente.query('SELECT public.marcar_pedido_en_reparto(1, 1)')),
    { code: '42501' });
  // Ni aunque falte el READ ONLY
  const cliente = await bd.pool.connect();
  const intentar = async (rol, sql) => {
    await cliente.query('BEGIN');
    try {
      await cliente.query(`SET LOCAL ROLE ${rol}`);
      await cliente.query(sql);
      return 'permitido';
    } catch (error) {
      return error.code;
    } finally {
      await cliente.query('ROLLBACK');
    }
  };
  try {
    assert.equal(await intentar('panel_lectura', 'SELECT public.marcar_pedido_en_reparto(1, 1)'), '42501');
    // panel_reparto, el rol de la ruta nueva, solo puede ejecutar esa funcion: ni leer ni escribir tablas
    assert.equal(await intentar('panel_reparto', 'SELECT count(*) FROM public.pedidos'), '42501');
    assert.equal(await intentar('panel_reparto', "UPDATE public.pedidos SET estado = 'enviado' WHERE false"), '42501');
    assert.equal(await intentar('panel_reparto', 'UPDATE public.existencias SET cantidad = cantidad WHERE false'), '42501');
    assert.equal(await intentar('panel_reparto', 'SELECT password_hash FROM public.usuarios'), '42501');
    // Sin SET ROLE, web_nova no puede llamarla (NOINHERIT)
    assert.equal(await intentar('web_nova', 'SELECT public.marcar_pedido_en_reparto(1, 1)'), '42501');
  } finally {
    cliente.release();
  }
});

test('reparto: las rutas de lectura no aceptan POST y las de reparto no aceptan GET', { skip: sinAdmin }, async () => {
  const login = await entrar(ADMIN, CLAVE_ADMIN);
  const post = await fetch(base + '/api/admin/pedidos', {
    method: 'POST', headers: { Cookie: login.cookie, 'Content-Type': 'application/json' }, body: '{}'
  });
  assert.equal(post.status, 404);
  assert.equal((await pedir('/api/admin/pedidos/1/reparto', login.cookie)).status, 404);
});

test('tras 5 fallos el usuario queda bloqueado (429), exista o no, y despues puede entrar', { skip: sinAdmin }, async () => {
  const respuestas = [];
  for (const usuario of [ADMIN, 'usuario.que.no.existe']) {
    for (let i = 1; i <= 5; i++) {
      assert.equal((await entrar(usuario, 'clave-mala-' + i)).codigo, 401);
    }
    // Bloqueado: ni con la contrasena buena se entra
    const bloqueado = await entrar(usuario, usuario === ADMIN ? CLAVE_ADMIN : 'da-igual');
    assert.equal(bloqueado.codigo, 429);
    respuestas.push(bloqueado.datos);
  }
  // La respuesta no dice si la cuenta existe
  assert.deepEqual(respuestas[0], respuestas[1]);

  // Pasado el bloqueo, el usuario legitimo vuelve a entrar
  await new Promise((resolver) => setTimeout(resolver, BLOQUEO_PRUEBA_MS + 200));
  assert.equal((await entrar(ADMIN, CLAVE_ADMIN)).codigo, 200);
});
