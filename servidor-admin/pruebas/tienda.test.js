// Pruebas automaticas de la tienda web (node --test, sin librerias extra).
//
// OJO: estas pruebas REGISTRAN CLIENTES Y CREAN PEDIDOS DE VERDAD, y gastan
// stock. Solo se pueden lanzar contra una base DESECHABLE, montada con todos
// los scripts (tambien el 20 y el 21). Por eso no van en "npm test" y piden
// una variable que lo confirme. En PowerShell, desde servidor-admin:
//   $env:PRUEBA_TIENDA_BASE_DESECHABLE = "si"
//   npm run test:tienda
// Si ademas se dan PRUEBA_ADMIN_USUARIO y PRUEBA_ADMIN_CLAVE (como en
// api.test.js), se comprueba que las compras salen en el panel.
//
// Cada prueba usa tallas que todavia tienen sus 5 pares, asi que se puede
// repetir varias veces sobre la misma base antes de tener que montarla otra vez.

const BLOQUEO_PRUEBA_MS = 1500; // el bloqueo por intentos dura 1,5 s en las pruebas
process.env.BLOQUEO_LOGIN_MS = String(BLOQUEO_PRUEBA_MS);

const test = require('node:test');
const assert = require('node:assert');
const crypto = require('node:crypto');
const http = require('node:http');
const { once } = require('node:events');
const app = require('../servidor');
const bd = require('../bd');

const saltar = process.env.PRUEBA_TIENDA_BASE_DESECHABLE !== 'si'
  && 'crean clientes y pedidos: solo con una base desechable (PRUEBA_TIENDA_BASE_DESECHABLE=si)';
const ADMIN = process.env.PRUEBA_ADMIN_USUARIO;
const CLAVE_ADMIN = process.env.PRUEBA_ADMIN_CLAVE;
const sinAdmin = saltar || (!(ADMIN && CLAVE_ADMIN) && 'faltan PRUEBA_ADMIN_USUARIO y PRUEBA_ADMIN_CLAVE');
const MODELO_WEB = /^NOVA (Street|Luxe|Casual|Hombre|Mujer|Unisex) 0[12]$/;
const CONTRASENA = 'clave-de-prueba-1';
const DIRECCION = 'Calle de Prueba 1, Madrid';

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

// Un "navegador" que guarda su cookie de la tienda entre peticiones
function navegador() {
  const nav = { cookie: '' };
  nav.pedir = async (metodo, ruta, cuerpo, cookieForzada) => {
    const cabeceras = {};
    const cookie = cookieForzada ?? nav.cookie;
    if (cookie) cabeceras.Cookie = cookie;
    if (cuerpo !== undefined) cabeceras['Content-Type'] = 'application/json';
    const respuesta = await fetch(base + ruta, {
      method: metodo,
      headers: cabeceras,
      body: cuerpo === undefined ? undefined : JSON.stringify(cuerpo),
      redirect: 'manual'
    });
    const setCookie = respuesta.headers.getSetCookie();
    for (const linea of setCookie) {
      const par = linea.split(';')[0];
      if (par.startsWith('sesion_tienda=')) nav.cookie = par === 'sesion_tienda=' ? '' : par;
    }
    const texto = await respuesta.text();
    let datos;
    try { datos = JSON.parse(texto); } catch { datos = texto; }
    return { codigo: respuesta.status, datos, setCookie, cabeceras: respuesta.headers };
  };
  return nav;
}

let contador = 0;
async function clienteNuevo() {
  const nav = navegador();
  contador += 1;
  nav.email = `prueba.${Date.now()}.${contador}@example.com`;
  const r = await nav.pedir('POST', '/api/tienda/registro', {
    nombre: `Cliente de prueba ${contador}`, email: nav.email, contrasena: CONTRASENA, direccion: DIRECCION
  });
  assert.equal(r.codigo, 201, JSON.stringify(r.datos));
  return nav;
}

function crearPedido(nav, lineas, extra = {}) {
  return nav.pedir('POST', '/api/tienda/pedidos', { clave: crypto.randomUUID(), lineas, direccion: DIRECCION, ...extra });
}

// Tallas que todavia tienen sus 5 pares (y no se han usado en esta ejecucion)
let catalogo;
const usadas = new Set();
async function tallaLibre() {
  if (!catalogo) catalogo = (await navegador().pedir('GET', '/api/tienda/catalogo')).datos.modelos;
  for (const modelo of catalogo.filter((m) => MODELO_WEB.test(m.nombre))) {
    for (const variante of modelo.variantes) {
      for (const talla of variante.tallas) {
        if (talla.stock === 5 && !usadas.has(talla.sku)) {
          usadas.add(talla.sku);
          return { sku: talla.sku, precio: variante.precio, modelo: modelo.nombre, talla: talla.talla };
        }
      }
    }
  }
  throw new Error('No quedan tallas con 5 pares: vuelve a montar la base desechable');
}

// Lecturas directas en PostgreSQL, con la conexion de solo lectura del panel
function leer(sql, parametros) {
  return bd.consultarSoloLectura(async (c) => (await c.query(sql, parametros)).rows);
}
async function stockDe(sku) {
  const filas = await leer('SELECT cantidad FROM public.existencias WHERE id_producto_sku = $1', [sku]);
  return filas[0].cantidad;
}

// ---------------------------------------------------------------------
// Catalogo y archivos de la tienda
// ---------------------------------------------------------------------
test('catalogo: los 12 modelos de la web, con precio, color, tallas y stock de PostgreSQL', { skip: saltar }, async () => {
  const r = await navegador().pedir('GET', '/api/tienda/catalogo');
  assert.equal(r.codigo, 200);
  const web = r.datos.modelos.filter((m) => MODELO_WEB.test(m.nombre));
  assert.equal(web.length, 12);
  const sku = web.flatMap((m) => m.variantes.flatMap((v) => v.tallas));
  assert.equal(sku.length, 106);
  // Comparado con la base, fila a fila
  const enLaBase = await leer(`
    SELECT s.id_producto_sku AS sku, m.precio_base + v.suplemento_precio AS precio, e.cantidad AS stock
    FROM public.producto_sku s JOIN public.variantes v USING (id_variante) JOIN public.modelos m USING (id_modelo)
    JOIN public.existencias e USING (id_producto_sku)
    WHERE m.nombre ~ '^NOVA (Street|Luxe|Casual|Hombre|Mujer|Unisex) 0[12]$'`);
  const porSku = new Map(enLaBase.map((f) => [f.sku, f]));
  for (const modelo of web) {
    for (const variante of modelo.variantes) {
      for (const talla of variante.tallas) {
        assert.equal(variante.precio, porSku.get(talla.sku).precio);
        assert.equal(talla.stock, porSku.get(talla.sku).stock);
      }
    }
  }
});

test('la web se sirve en /tienda/ y no deja salir de su carpeta', { skip: saltar }, async () => {
  const nav = navegador();
  const sinBarra = await nav.pedir('GET', '/tienda');
  assert.equal(sinBarra.codigo, 302);
  assert.equal(sinBarra.cabeceras.get('location'), '/tienda/');
  const portada = await nav.pedir('GET', '/tienda/');
  assert.equal(portada.codigo, 200);
  assert.match(portada.datos, /<title>NOVA Sneakers/);
  assert.equal(portada.cabeceras.get('x-frame-options'), 'DENY');
  assert.equal((await nav.pedir('GET', '/tienda/js/tienda.js')).codigo, 200);
  assert.equal((await nav.pedir('GET', '/tienda/no-existe.html')).codigo, 404);
  // fetch "arregla" las rutas con %2e%2e antes de enviarlas (como un
  // navegador), asi que estas se mandan tal cual con http.get.
  const rutaTalCual = (ruta) => new Promise((resolver, rechazar) => {
    http.get({ host: '127.0.0.1', port: servidor.address().port, path: ruta }, (respuesta) => {
      let cuerpo = '';
      respuesta.on('data', (trozo) => { cuerpo += trozo; });
      respuesta.on('end', () => resolver({ codigo: respuesta.statusCode, cuerpo }));
    }).on('error', rechazar);
  });
  for (const ruta of ['/tienda/../admin.html', '/tienda/%2e%2e/admin/admin.html', '/tienda/..%2fadmin%2fadmin.html',
    '/tienda/%2e%2e%2f%2e%2e%2fservidor-admin%2f.env.example', '/tienda/..\\..\\servidor-admin\\bd.js']) {
    const r = await rutaTalCual(ruta);
    assert.ok([400, 403, 404].includes(r.codigo), `${ruta} -> ${r.codigo}`);
    assert.doesNotMatch(r.cuerpo, /adm-menu|PGUSER|require\(/);
  }
});

// ---------------------------------------------------------------------
// Registro, login, logout
// ---------------------------------------------------------------------
test('registro: crea la cuenta, abre la sesion y la cookie es HttpOnly, SameSite=Strict y solo para /api/tienda', { skip: saltar }, async () => {
  const nav = navegador();
  const email = `registro.${Date.now()}@example.com`;
  const r = await nav.pedir('POST', '/api/tienda/registro', { nombre: '  Ana Registro ', email: email.toUpperCase(), contrasena: CONTRASENA });
  assert.equal(r.codigo, 201);
  assert.deepEqual(r.datos, { nombre: 'Ana Registro', email });
  const cookie = r.setCookie.find((c) => c.startsWith('sesion_tienda='));
  assert.match(cookie, /HttpOnly/);
  assert.match(cookie, /SameSite=Strict/);
  assert.match(cookie, /Path=\/api\/tienda/);
  const sesion = await nav.pedir('GET', '/api/tienda/sesion');
  assert.equal(sesion.datos.cliente.email, email);
  assert.ok(!JSON.stringify(sesion.datos).includes('hash'));
  assert.ok(!JSON.stringify(sesion.datos).includes(CONTRASENA));
});

test('registro: rechaza datos que no valen', { skip: saltar }, async () => {
  const nav = await clienteNuevo();
  const casos = [
    [{ nombre: 'X', email: nav.email, contrasena: CONTRASENA }, 409, /ya está registrado/],
    [{ nombre: 'X', email: 'daniel.jan@example.com', contrasena: CONTRASENA }, 409, /ya está registrado/],
    [{ nombre: 'X', email: `corta.${Date.now()}@example.com`, contrasena: '1234567' }, 400, /al menos 8/],
    [{ nombre: 'X', email: 'no-es-un-correo', contrasena: CONTRASENA }, 400, /correo no es válido/],
    [{ email: `sin.nombre.${Date.now()}@example.com`, contrasena: CONTRASENA }, 400, /Falta tu nombre/],
    [{ nombre: 'X', email: 12345, contrasena: CONTRASENA }, 400, /no es válido/],
    [{ nombre: 'X', email: `larga.${Date.now()}@example.com`, contrasena: 'x'.repeat(73) }, 400, /contraseña válida/],
    [{ nombre: 'X\u0000', email: `nulo.${Date.now()}@example.com`, contrasena: CONTRASENA }, 400, /no es válido/]
  ];
  for (const [cuerpo, codigo, mensaje] of casos) {
    const r = await navegador().pedir('POST', '/api/tienda/registro', cuerpo);
    assert.equal(r.codigo, codigo, JSON.stringify(cuerpo));
    assert.match(r.datos.error, mensaje);
  }
});

test('login: correcto, contrasena mala y correo que no existe (mismo mensaje)', { skip: saltar }, async () => {
  const cliente = await clienteNuevo();
  const bien = await navegador().pedir('POST', '/api/tienda/login', { email: cliente.email, contrasena: CONTRASENA });
  assert.equal(bien.codigo, 200);
  const mala = await navegador().pedir('POST', '/api/tienda/login', { email: cliente.email, contrasena: 'no-es-esta' });
  const nadie = await navegador().pedir('POST', '/api/tienda/login', { email: `nadie.${Date.now()}@example.com`, contrasena: 'no-es-esta' });
  assert.equal(mala.codigo, 401);
  assert.equal(nadie.codigo, 401);
  assert.deepEqual(mala.datos, nadie.datos);
});

test('login: 5 fallos bloquean ese correo (429), exista o no, y despues se puede entrar', { skip: saltar }, async () => {
  const cliente = await clienteNuevo();
  const inventado = `inventado.${Date.now()}@example.com`;
  for (const email of [cliente.email, inventado]) {
    for (let i = 0; i < 5; i++) {
      await navegador().pedir('POST', '/api/tienda/login', { email, contrasena: 'mala-mala' });
    }
  }
  const real = await navegador().pedir('POST', '/api/tienda/login', { email: cliente.email, contrasena: CONTRASENA });
  const falso = await navegador().pedir('POST', '/api/tienda/login', { email: inventado, contrasena: CONTRASENA });
  assert.equal(real.codigo, 429);
  assert.equal(falso.codigo, 429);
  assert.deepEqual(real.datos, falso.datos);
  await new Promise((resolver) => setTimeout(resolver, BLOQUEO_PRUEBA_MS + 200));
  const despues = await navegador().pedir('POST', '/api/tienda/login', { email: cliente.email, contrasena: CONTRASENA });
  assert.equal(despues.codigo, 200);
});

test('logout: la sesion deja de valer, tambien con la cookie antigua', { skip: saltar }, async () => {
  const cliente = await clienteNuevo();
  const antigua = cliente.cookie;
  assert.equal((await cliente.pedir('GET', '/api/tienda/pedidos')).codigo, 200);
  assert.equal((await cliente.pedir('POST', '/api/tienda/logout')).codigo, 200);
  assert.equal((await cliente.pedir('GET', '/api/tienda/pedidos')).codigo, 401);
  assert.equal((await cliente.pedir('GET', '/api/tienda/pedidos', undefined, antigua)).codigo, 401);
  assert.deepEqual((await cliente.pedir('GET', '/api/tienda/sesion', undefined, antigua)).datos, { cliente: null });
});

// ---------------------------------------------------------------------
// Clientes y administradores, separados
// ---------------------------------------------------------------------
test('la sesion de un cliente no sirve en el panel, ni sus credenciales en el login del panel', { skip: saltar }, async () => {
  const cliente = await clienteNuevo();
  const token = cliente.cookie.split('=')[1];
  for (const cookie of [cliente.cookie, `sesion_nova=${token}`]) {
    const r = await fetch(base + '/api/admin/dashboard', { headers: { Cookie: cookie } });
    assert.equal(r.status, 401);
  }
  const loginPanel = await fetch(base + '/api/login', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario: cliente.email, contrasena: CONTRASENA })
  });
  assert.equal(loginPanel.status, 401);
});

test('la sesion de un administrador no sirve en la tienda, ni sus credenciales en el login de la tienda', { skip: sinAdmin }, async () => {
  const login = await fetch(base + '/api/login', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario: ADMIN, contrasena: CLAVE_ADMIN })
  });
  assert.equal(login.status, 200);
  const cookieAdmin = login.headers.getSetCookie()[0].split(';')[0];
  const token = cookieAdmin.split('=')[1];
  const nav = navegador();
  assert.equal((await nav.pedir('GET', '/api/tienda/pedidos', undefined, cookieAdmin)).codigo, 401);
  assert.equal((await nav.pedir('GET', '/api/tienda/pedidos', undefined, `sesion_tienda=${token}`)).codigo, 401);
  assert.equal((await nav.pedir('POST', '/api/tienda/login', { email: ADMIN, contrasena: CLAVE_ADMIN })).codigo, 401);
});

// ---------------------------------------------------------------------
// Checkout: datos que no valen
// ---------------------------------------------------------------------
test('checkout sin sesion: 401', { skip: saltar }, async () => {
  const talla = await tallaLibre();
  const r = await crearPedido(navegador(), [{ sku: talla.sku, cantidad: 1 }]);
  assert.equal(r.codigo, 401);
  usadas.delete(talla.sku); // no se ha gastado
});

test('checkout: carrito vacio, cantidades y productos que no valen', { skip: saltar }, async () => {
  const cliente = await clienteNuevo();
  const talla = await tallaLibre();
  const casos = [
    [[], 400],
    ['no-es-una-lista', 400],
    [[{ sku: talla.sku, cantidad: 0 }], 400],
    [[{ sku: talla.sku, cantidad: -1 }], 400],
    [[{ sku: talla.sku, cantidad: 1.5 }], 400],
    [[{ sku: talla.sku, cantidad: '2' }], 400],
    [[{ sku: talla.sku, cantidad: 11 }], 400],
    [[{ sku: talla.sku, cantidad: 1e9 }], 400],
    [[{ sku: String(talla.sku), cantidad: 1 }], 400],
    [[{ sku: talla.sku, cantidad: 1 }, { sku: talla.sku, cantidad: 1 }], 400],
    [Array.from({ length: 21 }, (_, i) => ({ sku: i + 1, cantidad: 1 })), 400],
    [[{ sku: 999999, cantidad: 1 }], 409]
  ];
  for (const [lineas, codigo] of casos) {
    const r = await crearPedido(cliente, lineas);
    assert.equal(r.codigo, codigo, JSON.stringify(lineas).slice(0, 80) + ' -> ' + JSON.stringify(r.datos));
  }
  const sinClave = await cliente.pedir('POST', '/api/tienda/pedidos', { lineas: [{ sku: talla.sku, cantidad: 1 }], direccion: DIRECCION });
  assert.equal(sinClave.codigo, 400);
  const sinDireccion = await crearPedido(cliente, [{ sku: talla.sku, cantidad: 1 }], { direccion: '   ' });
  assert.equal(sinDireccion.codigo, 400);
  // Nada de esto ha creado pedidos
  assert.deepEqual((await cliente.pedir('GET', '/api/tienda/pedidos')).datos, { pedidos: [] });
  assert.equal(await stockDe(talla.sku), 5);
});

// ---------------------------------------------------------------------
// Compra completa: precios, total y stock
// ---------------------------------------------------------------------
test('compra: un precio o un cliente manipulados se ignoran; precio y total salen de PostgreSQL', { skip: saltar }, async () => {
  const ana = await clienteNuevo();
  const bea = await clienteNuevo();
  const idBea = (await bea.pedir('GET', '/api/tienda/sesion')).datos.cliente.id;
  const t1 = await tallaLibre();
  const t2 = await tallaLibre();
  const r = await crearPedido(ana, [
    { sku: t1.sku, cantidad: 2, precio: 0.01, subtotal: 0.02 },
    { sku: t2.sku, cantidad: 1, precio: 0.01 }
  ], { total: 0.03, importe_total: 0.03, id_cliente: idBea, idCliente: idBea });
  assert.equal(r.codigo, 201, JSON.stringify(r.datos));
  assert.equal(r.datos.estado, 'pendiente');
  assert.equal(r.datos.estadoPago, 'pendiente');
  assert.deepEqual(r.datos.lineas.map((l) => l.precio), [t1.precio, t2.precio]);
  assert.equal(r.datos.total, Math.round((2 * t1.precio + t2.precio) * 100) / 100);
  assert.equal(r.datos.pares, 3);
  // El pedido es de Ana (la sesion), no de Bea
  assert.equal((await ana.pedir('GET', `/api/tienda/pedidos/${r.datos.id}`)).codigo, 200);
  assert.equal((await bea.pedir('GET', `/api/tienda/pedidos/${r.datos.id}`)).codigo, 404);
  const enLaBase = await leer('SELECT importe_total, cantidad_total FROM public.pedidos WHERE id_pedido = $1', [r.datos.id]);
  assert.equal(enLaBase[0].importe_total, r.datos.total);
  // Crear el pedido no descuenta stock
  assert.equal(await stockDe(t1.sku), 5);
  assert.equal(await stockDe(t2.sku), 5);
});

test('pago aceptado: confirmado y pagado; el stock baja exactamente lo comprado', { skip: saltar }, async () => {
  const cliente = await clienteNuevo();
  const t1 = await tallaLibre();
  const t2 = await tallaLibre();
  const pedido = (await crearPedido(cliente, [{ sku: t1.sku, cantidad: 2 }, { sku: t2.sku, cantidad: 1 }])).datos;
  const r = await cliente.pedir('POST', `/api/tienda/pedidos/${pedido.id}/pago`, { resultado: 'aceptado' });
  assert.equal(r.codigo, 200, JSON.stringify(r.datos));
  assert.equal(r.datos.estado, 'confirmado');
  assert.equal(r.datos.estadoPago, 'pagado');
  assert.equal(await stockDe(t1.sku), 3);
  assert.equal(await stockDe(t2.sku), 4);
  // El catalogo ya ensena el stock nuevo
  const catalogoNuevo = (await navegador().pedir('GET', '/api/tienda/catalogo')).datos.modelos;
  const tallaEnCatalogo = catalogoNuevo.flatMap((m) => m.variantes.flatMap((v) => v.tallas)).find((t) => t.sku === t1.sku);
  assert.equal(tallaEnCatalogo.stock, 3);
  // Un pedido pagado no se cancela desde la web
  assert.equal((await cliente.pedir('POST', `/api/tienda/pedidos/${pedido.id}/cancelacion`)).codigo, 409);
});

test('pago rechazado: el pedido se cancela y el stock no cambia; ya no se puede pagar', { skip: saltar }, async () => {
  const cliente = await clienteNuevo();
  const talla = await tallaLibre();
  const pedido = (await crearPedido(cliente, [{ sku: talla.sku, cantidad: 3 }])).datos;
  const r = await cliente.pedir('POST', `/api/tienda/pedidos/${pedido.id}/pago`, { resultado: 'rechazado' });
  assert.equal(r.codigo, 200);
  assert.equal(r.datos.estado, 'cancelado');
  assert.equal(r.datos.estadoPago, 'pendiente');
  assert.equal(await stockDe(talla.sku), 5);
  assert.equal((await cliente.pedir('POST', `/api/tienda/pedidos/${pedido.id}/pago`, { resultado: 'aceptado' })).codigo, 409);
  assert.equal(await stockDe(talla.sku), 5);
  const raro = await cliente.pedir('POST', `/api/tienda/pedidos/${pedido.id}/pago`, { resultado: 'gratis' });
  assert.equal(raro.codigo, 400);
});

test('cancelar antes de pagar: cancelado y sin tocar el stock', { skip: saltar }, async () => {
  const cliente = await clienteNuevo();
  const talla = await tallaLibre();
  const pedido = (await crearPedido(cliente, [{ sku: talla.sku, cantidad: 1 }])).datos;
  const r = await cliente.pedir('POST', `/api/tienda/pedidos/${pedido.id}/cancelacion`);
  assert.equal(r.codigo, 200);
  assert.equal(r.datos.estado, 'cancelado');
  assert.equal(await stockDe(talla.sku), 5);
});

// ---------------------------------------------------------------------
// Dobles clics, reintentos y compras a la vez
// ---------------------------------------------------------------------
test('doble clic al crear: dos peticiones a la vez con la misma clave dan UN pedido', { skip: saltar }, async () => {
  const cliente = await clienteNuevo();
  const talla = await tallaLibre();
  const cuerpo = { clave: crypto.randomUUID(), lineas: [{ sku: talla.sku, cantidad: 1 }], direccion: DIRECCION };
  const [a, b] = await Promise.all([
    cliente.pedir('POST', '/api/tienda/pedidos', cuerpo),
    cliente.pedir('POST', '/api/tienda/pedidos', cuerpo)
  ]);
  assert.equal(a.codigo, 201, JSON.stringify(a.datos));
  assert.equal(b.codigo, 201, JSON.stringify(b.datos));
  assert.equal(a.datos.id, b.datos.id);
  // Un reintento mas tarde, tambien el mismo
  const c = await cliente.pedir('POST', '/api/tienda/pedidos', cuerpo);
  assert.equal(c.datos.id, a.datos.id);
  const enLaBase = await leer('SELECT count(*) AS n FROM public.pedidos WHERE referencia = $1', [a.datos.referencia]);
  assert.equal(enLaBase[0].n, 1);
  assert.equal((await cliente.pedir('GET', '/api/tienda/pedidos')).datos.pedidos.length, 1);
});

test('la clave de compra de otro cliente no le da su pedido', { skip: saltar }, async () => {
  const ana = await clienteNuevo();
  const bea = await clienteNuevo();
  const talla = await tallaLibre();
  const cuerpo = { clave: crypto.randomUUID(), lineas: [{ sku: talla.sku, cantidad: 1 }], direccion: DIRECCION };
  assert.equal((await ana.pedir('POST', '/api/tienda/pedidos', cuerpo)).codigo, 201);
  const r = await bea.pedir('POST', '/api/tienda/pedidos', cuerpo);
  assert.equal(r.codigo, 409);
  assert.ok(!('lineas' in r.datos));
});

test('doble clic al pagar: dos pagos a la vez descuentan el stock UNA sola vez', { skip: saltar }, async () => {
  const cliente = await clienteNuevo();
  const talla = await tallaLibre();
  const pedido = (await crearPedido(cliente, [{ sku: talla.sku, cantidad: 2 }])).datos;
  const pagos = await Promise.all([1, 2, 3].map(() =>
    cliente.pedir('POST', `/api/tienda/pedidos/${pedido.id}/pago`, { resultado: 'aceptado' })));
  assert.deepEqual(pagos.map((p) => p.codigo), [200, 200, 200]);
  assert.equal(await stockDe(talla.sku), 3);
  const cambios = await leer(
    "SELECT count(*) AS n FROM public.log_eventos WHERE accion = 'CAMBIO_STOCK' AND detalle = $1",
    [`SKU ${talla.sku}: 5 -> 3`]);
  assert.equal(cambios[0].n, 1);
});

test('compras a la vez de los ultimos pares: uno compra, al otro se le cancela y el stock queda en 0', { skip: saltar }, async () => {
  const ana = await clienteNuevo();
  const bea = await clienteNuevo();
  const talla = await tallaLibre();
  const pedidoAna = (await crearPedido(ana, [{ sku: talla.sku, cantidad: 5 }])).datos;
  const pedidoBea = (await crearPedido(bea, [{ sku: talla.sku, cantidad: 5 }])).datos;
  const [pagoAna, pagoBea] = await Promise.all([
    ana.pedir('POST', `/api/tienda/pedidos/${pedidoAna.id}/pago`, { resultado: 'aceptado' }),
    bea.pedir('POST', `/api/tienda/pedidos/${pedidoBea.id}/pago`, { resultado: 'aceptado' })
  ]);
  assert.deepEqual([pagoAna.codigo, pagoBea.codigo].sort(), [200, 409]);
  assert.equal(await stockDe(talla.sku), 0);
  const estados = await leer('SELECT estado FROM public.pedidos WHERE id_pedido = ANY($1) ORDER BY estado', [[pedidoAna.id, pedidoBea.id]]);
  assert.deepEqual(estados.map((e) => e.estado), ['cancelado', 'confirmado']);
  const perdedor = pagoAna.codigo === 409 ? pagoAna : pagoBea;
  assert.match(perdedor.datos.error, /se han agotado/);
});

test('sin stock: una talla agotada no se puede pedir', { skip: saltar }, async () => {
  const comprador = await clienteNuevo();
  const talla = await tallaLibre();
  const todo = (await crearPedido(comprador, [{ sku: talla.sku, cantidad: 5 }])).datos;
  assert.equal((await comprador.pedir('POST', `/api/tienda/pedidos/${todo.id}/pago`, { resultado: 'aceptado' })).codigo, 200);
  assert.equal(await stockDe(talla.sku), 0);
  const otro = await clienteNuevo();
  const r = await crearPedido(otro, [{ sku: talla.sku, cantidad: 1 }]);
  assert.equal(r.codigo, 409);
  assert.match(r.datos.error, new RegExp(`No queda stock suficiente de ${talla.modelo}`));
  assert.deepEqual((await otro.pedir('GET', '/api/tienda/pedidos')).datos, { pedidos: [] });
});

test('error a mitad del pago: si una linea se queda sin stock, no se descuenta ninguna', { skip: saltar }, async () => {
  const ana = await clienteNuevo();
  const t1 = await tallaLibre();
  const t2 = await tallaLibre();
  const pedidoAna = (await crearPedido(ana, [{ sku: t1.sku, cantidad: 2 }, { sku: t2.sku, cantidad: 3 }])).datos;
  // Mientras Ana paga, Bea se lleva los 5 pares de la segunda talla
  const bea = await clienteNuevo();
  const pedidoBea = (await crearPedido(bea, [{ sku: t2.sku, cantidad: 5 }])).datos;
  assert.equal((await bea.pedir('POST', `/api/tienda/pedidos/${pedidoBea.id}/pago`, { resultado: 'aceptado' })).codigo, 200);
  const r = await ana.pedir('POST', `/api/tienda/pedidos/${pedidoAna.id}/pago`, { resultado: 'aceptado' });
  assert.equal(r.codigo, 409);
  assert.equal(await stockDe(t1.sku), 5); // la primera linea NO se ha descontado
  assert.equal(await stockDe(t2.sku), 0);
  const cambios = await leer(
    "SELECT count(*) AS n FROM public.log_eventos WHERE accion = 'CAMBIO_STOCK' AND detalle LIKE $1",
    [`SKU ${t1.sku}: %`]);
  assert.equal(cambios[0].n, 0); // ni siquiera queda rastro de un descuento deshecho
  assert.equal((await ana.pedir('GET', `/api/tienda/pedidos/${pedidoAna.id}`)).datos.estado, 'cancelado');
});

// ---------------------------------------------------------------------
// Historial privado
// ---------------------------------------------------------------------
test('historial: cada cliente ve solo sus pedidos y no puede tocar los de otro', { skip: saltar }, async () => {
  const ana = await clienteNuevo();
  const bea = await clienteNuevo();
  const talla = await tallaLibre();
  const pedidoBea = (await crearPedido(bea, [{ sku: talla.sku, cantidad: 1 }])).datos;
  assert.deepEqual((await ana.pedir('GET', '/api/tienda/pedidos')).datos, { pedidos: [] });
  assert.equal((await bea.pedir('GET', '/api/tienda/pedidos')).datos.pedidos.length, 1);
  for (const [metodo, ruta, cuerpo] of [
    ['GET', `/api/tienda/pedidos/${pedidoBea.id}`],
    ['POST', `/api/tienda/pedidos/${pedidoBea.id}/pago`, { resultado: 'aceptado' }],
    ['POST', `/api/tienda/pedidos/${pedidoBea.id}/pago`, { resultado: 'rechazado' }],
    ['POST', `/api/tienda/pedidos/${pedidoBea.id}/cancelacion`]
  ]) {
    const r = await ana.pedir(metodo, ruta, cuerpo);
    assert.equal(r.codigo, 404, `${metodo} ${ruta}`);
  }
  // El pedido de Bea sigue igual
  const deBea = await bea.pedir('GET', `/api/tienda/pedidos/${pedidoBea.id}`);
  assert.equal(deBea.datos.estado, 'pendiente');
  assert.equal(await stockDe(talla.sku), 5);
  for (const id of ['abc', '0', '-1', '1.5', '99999999999']) {
    assert.equal((await ana.pedir('GET', `/api/tienda/pedidos/${id}`)).codigo, 404, id);
  }
});

// ---------------------------------------------------------------------
// Integracion con el panel de administracion
// ---------------------------------------------------------------------
test('panel: la compra sale en Pedidos, Dashboard, Inventario y Auditoria', { skip: sinAdmin }, async () => {
  const login = await fetch(base + '/api/login', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ usuario: ADMIN, contrasena: CLAVE_ADMIN })
  });
  const cookieAdmin = login.headers.getSetCookie()[0].split(';')[0];
  const panel = async (ruta) => (await fetch(base + ruta, { headers: { Cookie: cookieAdmin } })).json();

  const antes = await panel('/api/admin/dashboard');
  const cliente = await clienteNuevo();
  const talla = await tallaLibre();
  const pedido = (await crearPedido(cliente, [{ sku: talla.sku, cantidad: 2 }])).datos;
  await cliente.pedir('POST', `/api/tienda/pedidos/${pedido.id}/pago`, { resultado: 'aceptado' });

  const pedidos = await panel('/api/admin/pedidos?texto=' + pedido.referencia);
  assert.equal(pedidos.filas.length, 1);
  assert.equal(pedidos.filas[0].estado, 'confirmado');
  assert.equal(pedidos.filas[0].total, pedido.total);

  const despues = await panel('/api/admin/dashboard');
  assert.equal(despues.pedidosHoy, antes.pedidosHoy + 1);
  assert.equal(Math.round((despues.ventas - antes.ventas) * 100) / 100, pedido.total);

  const inventario = await panel('/api/admin/inventario?texto=' + encodeURIComponent(talla.modelo));
  const fila = inventario.filas.find((f) => f.talla === talla.talla);
  assert.equal(fila.stock, 3);

  const auditoria = await panel('/api/admin/auditoria?texto=' + pedido.referencia);
  const acciones = auditoria.filas.map((f) => f.accion).sort();
  assert.deepEqual(acciones, ['ALTA', 'CAMBIO_ESTADO']);
  const stock = await panel('/api/admin/auditoria?accion=CAMBIO_STOCK&texto=' + encodeURIComponent(`SKU ${talla.sku}: 5 -> 3`));
  assert.equal(stock.filas.length, 1);
});
