// Pruebas automaticas de la API del panel (node --test, sin librerias extra).
//
// Necesitan PostgreSQL con los scripts instalados (tambien el 19) y el .env del
// servidor. Las contrasenas de las cuentas de prueba NO se escriben aqui: se
// dan al ejecutar. En PowerShell, desde servidor-admin:
//   $env:PRUEBA_ADMIN_USUARIO = "admin.demo";  $env:PRUEBA_ADMIN_CLAVE = "..."
//   $env:PRUEBA_OTRO_USUARIO  = "taller.demo"; $env:PRUEBA_OTRO_CLAVE  = "..."
//   npm test
// Sin esas variables, las pruebas que las necesitan se saltan (y lo dicen).

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
