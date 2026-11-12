// tienda.js — las rutas de la tienda web: /api/tienda/...
//
//   web cliente (01_Interfaces/cliente)  -->  estas rutas  -->  PostgreSQL (tienda_nova)
//
// Este archivo hace tres cosas:
//   1. Comprueba que los datos que llegan tienen la forma correcta (tipos,
//      longitudes, cantidades enteras...). Si no, responde 400.
//   2. Saca el id del cliente de SU SESION. Nunca usa un id que mande el
//      navegador, ni un precio, ni un total: no se leen del cuerpo.
//   3. Llama a las funciones del script 20, que son las que comprueban el
//      dueno del pedido, su estado y el stock. Precios, totales y existencias
//      los calcula PostgreSQL.
//
// Rutas sin sesion:  GET catalogo · POST registro · POST login · POST logout · GET sesion
// Rutas con sesion:  POST pedidos · POST pedidos/:id/pago · POST pedidos/:id/cancelacion
//                    GET pedidos · GET pedidos/:id

const express = require('express');
const bd = require('./bd');
const sesiones = require('./sesiones');
const intentos = require('./intentos');
const consultas = require('./consultas-tienda');
const correo = require('./correo');

const rutas = express.Router();
const sesionesTienda = sesiones.tienda; // NO son las del personal (panel y portal)

// ---------------------------------------------------------------------
// Errores
// ---------------------------------------------------------------------

// Un error con un mensaje que SI se puede ensenar al cliente
function errorParaElCliente(mensaje, status = 400) {
  const error = new Error(mensaje);
  error.status = status;
  error.publico = true;
  return error;
}

// Las funciones SQL avisan con RAISE EXCEPTION (codigo P0001). Sus mensajes
// van sin tildes, como todos los scripts SQL. Aqui se decide que codigo HTTP
// le corresponde a cada uno y como se escribe para la web.
const ERRORES_BD = {
  'Ese correo ya esta registrado': [409, 'Ese correo ya está registrado. Inicia sesión.'],
  'El correo no es valido': [400, 'El correo no es válido'],
  'La contrasena debe tener al menos 8 caracteres': [400, 'La contraseña debe tener al menos 8 caracteres'],
  'Producto no disponible': [409, 'Alguno de los productos ya no está a la venta. Revisa el carrito.'],
  'Hay productos repetidos en el carrito': [400, 'Hay productos repetidos en el carrito'],
  'El pedido no existe': [404, 'Ese pedido no existe'],
  'Este pedido ya no se puede pagar': [409, 'Este pedido ya no se puede pagar'],
  'Un pedido pagado no se puede cancelar desde la web': [409, 'Un pedido pagado no se puede cancelar desde la web'],
  'Referencia no valida': [409, 'No se ha podido crear el pedido. Vuelve a intentarlo.'],
  'Cliente no valido': [401, 'Tu sesión ya no es válida. Vuelve a entrar.']
};

function traducirErrorBD(error) {
  if (error.code !== 'P0001') return error; // no es de nuestras funciones: error 500
  const conocido = ERRORES_BD[error.message];
  if (conocido) return errorParaElCliente(conocido[1], conocido[0]);
  if (error.message.startsWith('No queda stock suficiente de ')) {
    return errorParaElCliente(`${error.message}. Revisa el carrito.`, 409);
  }
  return errorParaElCliente(error.message, 400);
}

// Igual que bd.operarEnTienda, pero con los errores de la base ya traducidos
async function enTienda(trabajo) {
  try {
    return await bd.operarEnTienda(trabajo);
  } catch (error) {
    throw traducirErrorBD(error);
  }
}

// ---------------------------------------------------------------------
// Comprobacion de los datos que llegan
// ---------------------------------------------------------------------

// Un texto del cuerpo de la peticion: string, sin el caracter nulo (PostgreSQL
// no lo admite) y sin pasarse de largo. Devuelve el texto sin espacios a los lados.
function leerTexto(cuerpo, campo, maximo, obligatorio, descripcion) {
  const valor = cuerpo?.[campo];
  if (valor === undefined || valor === null || valor === '') {
    if (obligatorio) throw errorParaElCliente(`Falta ${descripcion}`);
    return '';
  }
  if (typeof valor !== 'string' || valor.includes('\0') || valor.length > maximo) {
    throw errorParaElCliente(`${descripcion} no es válido (máximo ${maximo} caracteres)`);
  }
  const limpio = valor.trim();
  if (obligatorio && limpio === '') throw errorParaElCliente(`Falta ${descripcion}`);
  return limpio;
}

// La contrasena no se recorta: los espacios tambien cuentan.
// bcrypt solo usa los 72 primeros bytes, asi que no se admite mas.
function leerContrasena(cuerpo) {
  const valor = cuerpo?.contrasena;
  if (typeof valor !== 'string' || valor === '' || valor.includes('\0')
      || Buffer.byteLength(valor) > 72) {
    throw errorParaElCliente('Escribe una contraseña válida (de 8 a 72 caracteres)');
  }
  return valor;
}

// El navegador crea una clave aleatoria (crypto.randomUUID) al abrir el
// checkout y la manda con el pedido. Con ella se forma la referencia
// WEB-XXXXXXXXXXXXXXXXXXXX. Si la misma compra llega dos veces (doble clic,
// reintento), trae la misma clave y crear_compra_web devuelve el mismo pedido.
const FORMATO_CLAVE = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

function referenciaDeLaCompra(clave) {
  if (typeof clave !== 'string' || !FORMATO_CLAVE.test(clave)) {
    throw errorParaElCliente('Falta la clave de la compra. Recarga la página.');
  }
  return 'WEB-' + clave.replace(/-/g, '').slice(0, 20).toUpperCase();
}

// Las lineas del carrito: [{ sku, cantidad }, ...]. Solo se leen esos dos
// campos: si el navegador manda tambien un precio, se ignora.
function leerLineas(lineas) {
  if (!Array.isArray(lineas) || lineas.length === 0) {
    throw errorParaElCliente('El carrito está vacío');
  }
  if (lineas.length > 20) {
    throw errorParaElCliente('El carrito admite como mucho 20 productos distintos');
  }
  const skus = [];
  const cantidades = [];
  for (const linea of lineas) {
    const sku = linea?.sku;
    const cantidad = linea?.cantidad;
    // Number.isInteger rechaza "2" (texto), 1.5, NaN e Infinity
    if (!Number.isInteger(sku) || sku < 1 || sku > 2147483647) {
      throw errorParaElCliente('Hay un producto que no es válido. Revisa el carrito.');
    }
    if (!Number.isInteger(cantidad) || cantidad < 1 || cantidad > 10) {
      throw errorParaElCliente('Cada producto admite de 1 a 10 pares');
    }
    if (skus.includes(sku)) {
      throw errorParaElCliente('Hay productos repetidos en el carrito');
    }
    skus.push(sku);
    cantidades.push(cantidad);
  }
  return { skus, cantidades };
}

// El id de la URL (/pedidos/15). Si no es un numero, el pedido no existe.
function leerIdPedido(req) {
  if (!/^[1-9][0-9]{0,8}$/.test(req.params.id)) {
    throw errorParaElCliente('Ese pedido no existe', 404);
  }
  return Number(req.params.id);
}

// ---------------------------------------------------------------------
// Solo para clientes con sesion. En cada peticion se vuelve a mirar en la
// base que el cliente sigue activo; si no, la sesion se borra.
// Deja sus datos en req.cliente: { id, nombre, email, telefono, direccion }.
// ---------------------------------------------------------------------
async function soloCliente(req, res, next) {
  const sesion = sesionesTienda.leerSesion(req);
  if (!sesion) {
    return res.status(401).json({ error: 'Inicia sesión para continuar' });
  }
  const cliente = await enTienda((c) => consultas.datosCliente(c, sesion.idCliente));
  if (!cliente) {
    sesionesTienda.cerrarSesion(req, res);
    return res.status(401).json({ error: 'Tu sesión ya no es válida. Vuelve a entrar.' });
  }
  req.cliente = cliente;
  next();
}

// ---------------------------------------------------------------------
// Catalogo
// ---------------------------------------------------------------------
rutas.get('/catalogo', async (req, res) => {
  res.json({ modelos: await enTienda((c) => consultas.catalogo(c)) });
});

// ---------------------------------------------------------------------
// Registro, login, logout y sesion
// ---------------------------------------------------------------------
rutas.post('/registro', async (req, res) => {
  const nombre = leerTexto(req.body, 'nombre', 120, true, 'tu nombre');
  const email = leerTexto(req.body, 'email', 150, true, 'el correo').toLowerCase();
  const contrasena = leerContrasena(req.body);
  const telefono = leerTexto(req.body, 'telefono', 30, false, 'El teléfono');
  const direccion = leerTexto(req.body, 'direccion', 300, false, 'La dirección');

  const idCliente = await enTienda((c) =>
    consultas.registrar(c, nombre, email, contrasena, telefono, direccion));

  // Recien registrado, ya tiene la sesion abierta
  sesionesTienda.crearSesion(req, res, { idCliente });
  res.status(201).json({ nombre, email });
});

// Igual que el login del personal: la contrasena la comprueba PostgreSQL y,
// tras 5 fallos con el mismo correo, se responde 429 unos minutos.
rutas.post('/login', async (req, res) => {
  const email = leerTexto(req.body, 'email', 150, true, 'el correo').toLowerCase();
  const contrasena = leerContrasena(req.body);

  const claveIntentos = 'cliente:' + email; // separado de los usuarios del panel
  const bloqueo = intentos.tiempoDeBloqueo(claveIntentos);
  if (bloqueo > 0) {
    res.set('Retry-After', String(Math.ceil(bloqueo / 1000)));
    return res.status(429).json({ error: 'Demasiados intentos. Espera unos minutos y vuelve a probar.' });
  }

  let cliente;
  try {
    cliente = await bd.operarEnTienda(async (c) => {
      const idCliente = await consultas.iniciarSesion(c, email, contrasena);
      return consultas.datosCliente(c, idCliente);
    });
  } catch (error) {
    if (error.code === 'P0001') {
      // El mismo mensaje exista o no el correo
      intentos.apuntarFallo(claveIntentos);
      return res.status(401).json({ error: 'Correo o contraseña incorrectos' });
    }
    throw error;
  }

  intentos.borrarFallos(claveIntentos);
  sesionesTienda.crearSesion(req, res, { idCliente: cliente.id });
  res.json({ nombre: cliente.nombre, email: cliente.email });
});

rutas.post('/logout', (req, res) => {
  sesionesTienda.cerrarSesion(req, res);
  res.json({ ok: true });
});

// La web pregunta al cargar si hay alguien dentro. Sin sesion responde 200
// con cliente: null (no es un error: la tienda se puede ver sin entrar).
rutas.get('/sesion', async (req, res) => {
  const sesion = sesionesTienda.leerSesion(req);
  if (!sesion) return res.json({ cliente: null });
  const cliente = await enTienda((c) => consultas.datosCliente(c, sesion.idCliente));
  if (!cliente) sesionesTienda.cerrarSesion(req, res);
  res.json({ cliente });
});

// ---------------------------------------------------------------------
// Compras (con sesion)
// ---------------------------------------------------------------------

// cancelar_compra_web: cancela un pedido sin pagar del cliente (sin tocar el
// stock) y lo devuelve ya cancelado. La usan el pago rechazado y la cancelacion.
function cancelarPedido(idCliente, idPedido) {
  return enTienda(async (c) => {
    await consultas.cancelarCompra(c, idCliente, idPedido);
    return consultas.pedido(c, idCliente, idPedido);
  });
}

// Paso 1 del checkout: crea el pedido PENDIENTE y devuelve sus lineas con el
// precio y el total que ha calculado PostgreSQL. No descuenta stock.
rutas.post('/pedidos', soloCliente, async (req, res) => {
  const referencia = referenciaDeLaCompra(req.body?.clave);
  const { skus, cantidades } = leerLineas(req.body?.lineas);
  const telefono = leerTexto(req.body, 'telefono', 30, false, 'El teléfono');
  const direccion = leerTexto(req.body, 'direccion', 300, true, 'la dirección de entrega');

  const pedido = await enTienda(async (c) => {
    const idPedido = await consultas.crearCompra(
      c, req.cliente.id, referencia, skus, cantidades, telefono, direccion);
    return consultas.pedido(c, req.cliente.id, idPedido);
  });
  res.status(201).json(pedido);
});

// Paso 2: el resultado del pago SIMULADO.
//   aceptado  -> confirmar_compra_web: confirmado y pagado; el trigger
//                descuenta el stock. Si ya no queda, se deshace y el pedido
//                se cancela. Si queda confirmado, se envia el recibo por
//                correo (correo.js).
//   rechazado -> cancelar_compra_web: cancelado, sin tocar el stock y sin correo.
// En una tienda real el resultado lo daria la pasarela de pago al servidor,
// nunca el navegador. Aqui es una simulacion academica: no se cobra nada.
rutas.post('/pedidos/:id/pago', soloCliente, async (req, res) => {
  const idPedido = leerIdPedido(req);
  const resultado = req.body?.resultado;
  if (resultado !== 'aceptado' && resultado !== 'rechazado') {
    throw errorParaElCliente('El resultado del pago simulado tiene que ser "aceptado" o "rechazado"');
  }

  if (resultado === 'rechazado') {
    return res.json(await cancelarPedido(req.cliente.id, idPedido));
  }

  let pago;
  try {
    pago = await bd.operarEnTienda(async (c) => {
      // Si llegan dos pagos del mismo pedido a la vez (doble clic), este
      // bloqueo de PostgreSQL hace que vayan uno detras de otro. Asi solo el
      // que lo pasa de pendiente a confirmado manda el recibo.
      await c.query('SELECT pg_advisory_xact_lock($1)', [idPedido]);
      const antes = await consultas.pedido(c, req.cliente.id, idPedido);
      await consultas.confirmarCompra(c, req.cliente.id, idPedido);
      const pedido = await consultas.pedido(c, req.cliente.id, idPedido);
      return { pedido, recienPagado: antes?.estado === 'pendiente' };
    });
  } catch (error) {
    // Entre crear el pedido y pagarlo, otro cliente se ha llevado los ultimos
    // pares (el trigger de 03 lanza este error y no se descuenta nada).
    if (error.code === 'P0001' && error.message === 'Stock insuficiente o producto no encontrado') {
      await enTienda((c) => consultas.cancelarCompra(c, req.cliente.id, idPedido));
      throw errorParaElCliente(
        'Mientras pagabas se han agotado algunas tallas. El pedido se ha cancelado y no se ha cobrado nada.', 409);
    }
    throw traducirErrorBD(error);
  }

  // El pago ya esta guardado (COMMIT): primero se responde al cliente y
  // despues se manda el recibo, asi que si el correo falla o tarda la compra
  // no cambia. Va al correo con el que se registro: req.cliente lo ha leido
  // soloCliente de la base, no viene del navegador. enviarRecibo no lanza
  // errores: como mucho los apunta en la consola.
  res.json(pago.pedido);
  if (pago.recienPagado) {
    await correo.enviarRecibo(req.cliente, pago.pedido);
  }
});

// El cliente cancela un pedido que todavia no ha pagado
rutas.post('/pedidos/:id/cancelacion', soloCliente, async (req, res) => {
  const idPedido = leerIdPedido(req);
  res.json(await cancelarPedido(req.cliente.id, idPedido));
});

// Historial: solo sus pedidos
rutas.get('/pedidos', soloCliente, async (req, res) => {
  res.json({ pedidos: await enTienda((c) => consultas.pedidos(c, req.cliente.id)) });
});

// Un pedido con sus lineas. Si es de otro cliente, 404 (no se dice que existe).
rutas.get('/pedidos/:id', soloCliente, async (req, res) => {
  const idPedido = leerIdPedido(req);
  const pedido = await enTienda((c) => consultas.pedido(c, req.cliente.id, idPedido));
  if (!pedido) throw errorParaElCliente('Ese pedido no existe', 404);
  // Solo en desarrollo con CORREO_PROVEEDOR=ethereal: el enlace al recibo de prueba
  const reciboPrueba = correo.vistaPrevia(pedido.id);
  if (reciboPrueba) pedido.reciboPrueba = reciboPrueba;
  res.json(pedido);
});

// Errores de la tienda con mensaje para el cliente. Los demas siguen al
// manejador general de servidor.js (500 sin detalles de la base).
rutas.use((error, req, res, next) => {
  if (error.publico) {
    return res.status(error.status).json({ error: error.message });
  }
  next(error);
});

module.exports = { rutas };
