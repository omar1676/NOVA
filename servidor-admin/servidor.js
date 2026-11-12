// servidor.js — servidor de NOVA Sneakers: el panel de administracion y la
// tienda web.
//
//   navegador (panel HTML)  -->  este servidor (Express)  -->  PostgreSQL (web_nova)
//   navegador (tienda web)  -->  este servidor (Express)  -->  PostgreSQL (tienda_nova)
//
// El navegador nunca habla con PostgreSQL: pide /api/... a este servidor, que
// hace las consultas. El mismo servidor entrega los archivos del panel y de la
// tienda, asi que paginas y API tienen el mismo origen (sin CORS).
//   http://127.0.0.1:3000/admin.html   panel (solo administradores)
//   http://127.0.0.1:3000/tienda/      tienda web (rutas en tienda.js)

const path = require('node:path');
const express = require('express');
const bd = require('./bd');
const sesiones = require('./sesiones');
const intentos = require('./intentos');
const consultas = require('./consultas');
const tienda = require('./tienda');
const correo = require('./correo');

const PUERTO = Number(process.env.PUERTO) || 3000;
const HOST = '127.0.0.1'; // solo este ordenador: el servidor no se abre a la red
const CARPETA_PANEL = path.join(__dirname, '..', 'interfaces', 'admin');
const CARPETA_TIENDA = path.join(__dirname, '..', 'interfaces', 'cliente');

// El panel es solo para el rol "administrador" de la tabla roles.
const ROL_PANEL = 'administrador';

const app = express();
app.disable('x-powered-by'); // no anunciar en cada respuesta que el servidor es Express

// Solo se atienden peticiones dirigidas a este ordenador por su nombre. Asi una
// web maliciosa que haga apuntar su dominio a 127.0.0.1 ("DNS rebinding") no
// puede usar el panel desde el navegador del administrador.
const HOSTS_PERMITIDOS = ['127.0.0.1', 'localhost'];
app.use((req, res, next) => {
  if (!HOSTS_PERMITIDOS.includes(req.hostname)) {
    return res.status(400).json({ error: 'Host no permitido' });
  }
  next();
});

// Cabeceras de proteccion en todas las respuestas
app.use((req, res, next) => {
  res.set('X-Content-Type-Options', 'nosniff'); // el navegador no adivina el tipo de los archivos
  res.set('X-Frame-Options', 'DENY');           // ninguna otra web puede meter el panel en un iframe
  res.set('Referrer-Policy', 'same-origin');
  if (req.path.toLowerCase().startsWith('/api/')) { // las rutas no distinguen mayusculas
    res.set('Cache-Control', 'no-store');       // los datos de la API no se guardan en la cache
  }
  next();
});

app.use(express.json());

// ---------------------------------------------------------------------
// Estado del servidor y de la conexion con PostgreSQL
// ---------------------------------------------------------------------
app.get('/api/estado', async (req, res) => {
  try {
    const conexion = await bd.comprobarConexion();
    res.json({
      servidor: 'ok',
      baseDeDatos: 'conectada',
      usuarioBaseDeDatos: conexion.usuario,
      base: conexion.base
    });
  } catch (error) {
    console.error('Sin conexion con PostgreSQL:', error.message);
    res.status(503).json({ servidor: 'ok', baseDeDatos: 'sin conexion' });
  }
});

// ---------------------------------------------------------------------
// Login y logout
//
// La contrasena la comprueba PostgreSQL con iniciar_sesion (bcrypt), igual
// que en la aplicacion Java. Si no coincide, o la cuenta no tiene contrasena
// o esta desactivada, iniciar_sesion lanza una excepcion (RAISE EXCEPTION,
// codigo P0001).
//
// Despues de 5 fallos seguidos con el mismo usuario, se responde 429 durante
// unos minutos sin comprobar la contrasena (intentos.js).
// ---------------------------------------------------------------------

// El rol de un usuario ACTIVO, o null si la cuenta no existe o esta desactivada.
// La usan el login y la comprobacion de cada peticion del panel.
async function rolDeUsuarioActivo(cliente, idUsuario) {
  const resultado = await cliente.query(
    'SELECT r.nombre AS rol FROM public.usuarios u JOIN public.roles r ON r.id_rol = u.id_rol '
    + 'WHERE u.id_usuario = $1 AND u.activo', [idUsuario]);
  return resultado.rows.length > 0 ? resultado.rows[0].rol : null;
}

app.post('/api/login', async (req, res) => {
  const usuario = req.body?.usuario;
  const contrasena = req.body?.contrasena;
  if (typeof usuario !== 'string' || typeof contrasena !== 'string'
      || usuario === '' || contrasena === ''
      || usuario.length > 60 || contrasena.length > 200
      || usuario.includes('\0') || contrasena.includes('\0')) { // PostgreSQL no admite el caracter nulo
    return res.status(400).json({ error: 'Escribe el usuario y la contraseña' });
  }

  const bloqueo = intentos.tiempoDeBloqueo(usuario);
  if (bloqueo > 0) {
    res.set('Retry-After', String(Math.ceil(bloqueo / 1000))); // segundos que faltan
    return res.status(429).json({ error: 'Demasiados intentos. Espera unos minutos y vuelve a probar.' });
  }

  try {
    const datos = await bd.consultarSoloLectura(async (cliente) => {
      const login = await cliente.query(
        'SELECT iniciar_sesion($1, $2) AS id_usuario', [usuario, contrasena]);
      const idUsuario = login.rows[0].id_usuario;
      return { idUsuario, usuario, rol: await rolDeUsuarioActivo(cliente, idUsuario) };
    });

    intentos.borrarFallos(usuario);
    sesiones.crearSesion(req, res, datos);
    res.json({ usuario: datos.usuario, rol: datos.rol, accesoPanel: datos.rol === ROL_PANEL });
  } catch (error) {
    if (error.code === 'P0001') {
      // El mismo mensaje para todo: no se dice si el usuario existe o no
      intentos.apuntarFallo(usuario);
      return res.status(401).json({ error: 'Usuario o contraseña incorrectos' });
    }
    throw error; // Express 5 lo pasa al manejador de errores del final
  }
});

app.post('/api/logout', (req, res) => {
  sesiones.cerrarSesion(req, res);
  res.json({ ok: true });
});

// Para que el panel sepa si hay alguien dentro y con que rol
app.get('/api/sesion', (req, res) => {
  const sesion = sesiones.leerSesion(req);
  if (!sesion) {
    return res.status(401).json({ error: 'No has iniciado sesión' });
  }
  res.json({ usuario: sesion.usuario, rol: sesion.rol, accesoPanel: sesion.rol === ROL_PANEL });
});

// ---------------------------------------------------------------------
// Rutas del panel: solo para administradores
//   401 = no sabemos quien eres (no hay sesion): hay que entrar
//   403 = sabemos quien eres, pero tu rol no tiene permiso
//
// En cada peticion se vuelve a mirar en la base si la cuenta sigue activa y
// sigue siendo de administrador. Si se desactiva o se le cambia el rol, su
// sesion deja de valer en ese mismo momento (y se borra).
// ---------------------------------------------------------------------
async function soloAdministrador(req, res, next) {
  const sesion = sesiones.leerSesion(req);
  if (!sesion) {
    return res.status(401).json({ error: 'No has iniciado sesión' });
  }
  if (sesion.rol !== ROL_PANEL) {
    return res.status(403).json({ error: 'Tu usuario no tiene permiso para el panel de administración' });
  }

  const rolActual = await bd.consultarSoloLectura((cliente) => rolDeUsuarioActivo(cliente, sesion.idUsuario));
  if (rolActual === null) {
    sesiones.cerrarSesion(req, res);
    return res.status(401).json({ error: 'Tu sesión ya no es válida. Vuelve a entrar.' });
  }
  if (rolActual !== ROL_PANEL) {
    sesiones.cerrarSesion(req, res);
    return res.status(403).json({ error: 'Tu usuario no tiene permiso para el panel de administración' });
  }
  next();
}

app.use('/api/admin', soloAdministrador);

// Lee un filtro de la URL, por ejemplo /api/admin/pedidos?estado=pendiente.
// Si no viene, devuelve '' (sin filtro). Si viene un valor que no esta en la
// lista de permitidos, la peticion se rechaza con 400.
function leerFiltro(req, nombre, permitidos) {
  const valor = req.query[nombre];
  if (valor === undefined) return '';
  if (typeof valor !== 'string' || valor.length > 60 || valor.includes('\0')) {
    throw errorDePeticion(`El filtro "${nombre}" no es válido`);
  }
  const limpio = valor.trim();
  if (limpio !== '' && permitidos && !permitidos.includes(limpio)) {
    throw errorDePeticion(`"${limpio}" no es un valor válido para "${nombre}"`);
  }
  return limpio;
}

// El texto del buscador va dentro de un ILIKE, donde % y _ son comodines.
// Se escapan con \ para que se busquen como letras normales (si no,
// ?texto=_ devolveria todas las filas).
function leerTexto(req) {
  return leerFiltro(req, 'texto').replace(/[\\%_]/g, '\\$&');
}

function errorDePeticion(mensaje) {
  const error = new Error(mensaje);
  error.status = 400;
  return error;
}

// Las ocho rutas de lectura del panel. Cada una lee sus filtros y llama a su
// consulta de consultas.js dentro de una transaccion de solo lectura.
app.get('/api/admin/dashboard', async (req, res) => {
  res.json(await bd.consultarSoloLectura((cliente) => consultas.dashboard(cliente)));
});

app.get('/api/admin/pedidos', async (req, res) => {
  const estado = leerFiltro(req, 'estado', consultas.ESTADOS_PEDIDO);
  const texto = leerTexto(req);
  res.json(await bd.consultarSoloLectura((cliente) => consultas.pedidos(cliente, estado, texto)));
});

app.get('/api/admin/productos', async (req, res) => {
  const estado = leerFiltro(req, 'estado', consultas.ESTADOS_ACTIVO);
  const texto = leerTexto(req);
  res.json(await bd.consultarSoloLectura((cliente) => consultas.productos(cliente, estado, texto)));
});

app.get('/api/admin/inventario', async (req, res) => {
  const estado = leerFiltro(req, 'estado', consultas.ESTADOS_STOCK);
  const texto = leerTexto(req);
  res.json(await bd.consultarSoloLectura((cliente) => consultas.inventario(cliente, estado, texto)));
});

app.get('/api/admin/clientes', async (req, res) => {
  const estado = leerFiltro(req, 'estado', consultas.ESTADOS_ACTIVO);
  const texto = leerTexto(req);
  res.json(await bd.consultarSoloLectura((cliente) => consultas.clientes(cliente, estado, texto)));
});

app.get('/api/admin/trabajadores', async (req, res) => {
  const estado = leerFiltro(req, 'estado', consultas.ESTADOS_ACTIVO);
  const texto = leerTexto(req);
  res.json(await bd.consultarSoloLectura((cliente) => consultas.trabajadores(cliente, estado, texto)));
});

app.get('/api/admin/auditoria', async (req, res) => {
  const accion = leerFiltro(req, 'accion', consultas.ACCIONES_AUDITORIA);
  const texto = leerTexto(req);
  res.json(await bd.consultarSoloLectura((cliente) => consultas.auditoria(cliente, accion, texto)));
});

app.get('/api/admin/estadisticas', async (req, res) => {
  res.json(await bd.consultarSoloLectura((cliente) => consultas.estadisticas(cliente)));
});

// ---------------------------------------------------------------------
// La unica ruta del panel que cambia algo: el boton "Marcar en reparto".
// Pasa un pedido confirmado a "enviado" con marcar_pedido_en_reparto
// (script 22), en una transaccion de escritura aparte (bd.marcarEnReparto).
// La funcion vuelve a comprobar que el usuario es administrador y la
// auditoria apunta el cambio a su nombre. Respuestas:
//   401 / 403  como las demas rutas del panel (soloAdministrador)
//   415        si no llega JSON
//   404        el pedido no existe
//   409        el pedido no esta confirmado (pendiente, cancelado, ya enviado...)
//   200        el pedido, ya en "enviado"
// ---------------------------------------------------------------------
const ERRORES_REPARTO = {
  'Usuario no autorizado': [403, 'Tu usuario no tiene permiso para el panel de administración'],
  'El pedido no existe': [404, 'Ese pedido no existe'],
  'Solo se puede pasar a reparto un pedido confirmado':
    [409, 'Solo se puede marcar en reparto un pedido confirmado (puede que este ya haya cambiado de estado).']
};

app.post('/api/admin/pedidos/:id/reparto', async (req, res) => {
  // Solo JSON, como manda el panel: un formulario de otra web no puede
  // enviar este tipo de datos sin que el servidor lo permita (CORS)
  if (!req.is('application/json')) {
    return res.status(415).json({ error: 'Los datos tienen que ir en JSON' });
  }
  if (!/^[1-9][0-9]{0,8}$/.test(req.params.id)) {
    return res.status(404).json({ error: 'Ese pedido no existe' });
  }
  const idPedido = Number(req.params.id);
  const sesion = sesiones.leerSesion(req); // soloAdministrador ya ha comprobado que existe

  try {
    await bd.marcarEnReparto(sesion.idUsuario, idPedido);
  } catch (error) {
    const conocido = error.code === 'P0001' && ERRORES_REPARTO[error.message];
    if (!conocido) throw error; // cualquier otro: 500 sin detalles
    return res.status(conocido[0]).json({ error: conocido[1] });
  }

  // El pedido ya cambiado, leido con la conexion de solo lectura de siempre
  res.json(await bd.consultarSoloLectura((cliente) => consultas.pedido(cliente, idPedido)));
});

// La tienda web: sus rutas estan en tienda.js. Usa su propia sesion (cookie
// sesion_tienda) y su propio usuario de PostgreSQL (tienda_nova).
app.use('/api/tienda', tienda.rutas);

// Cualquier otra ruta /api/... que no exista
app.use('/api', (req, res) => {
  res.status(404).json({ error: 'Esa ruta de la API no existe' });
});

// ---------------------------------------------------------------------
// Archivos de la tienda web: publicos, en /tienda/
//
// Van antes que los del panel para que protegerPanel no los pida. Sin la
// barra final, el navegador buscaria css/ y js/ fuera de /tienda/, asi que
// /tienda se redirige a /tienda/. express.static no sirve nada que este
// fuera de interfaces/cliente (rechaza las rutas con ..).
// ---------------------------------------------------------------------
app.use((req, res, next) => {
  if (req.path === '/tienda') return res.redirect('/tienda/');
  next();
});
app.use('/tienda', express.static(CARPETA_TIENDA));
app.use('/tienda', (req, res) => res.status(404).send('No encontrado')); // y no al login del panel

// ---------------------------------------------------------------------
// Archivos del panel
//
// Sin sesion de administrador solo se entrega lo que necesita la pagina de
// login. Cualquier otra pagina redirige a login.html.
// ---------------------------------------------------------------------
const ARCHIVOS_PUBLICOS = ['/login.html', '/login.js', '/styles.css'];

function protegerPanel(req, res, next) {
  let ruta;
  try {
    ruta = decodeURIComponent(req.path).toLowerCase();
  } catch {
    return res.status(400).end(); // una ruta mal codificada, como /%E0
  }
  if (ruta.includes('..') || ruta.includes('\\')) {
    return res.status(400).end(); // nada de salir de la carpeta del panel
  }

  const esPublico = ARCHIVOS_PUBLICOS.includes(ruta) || ruta.startsWith('/img/');
  const sesion = sesiones.leerSesion(req);
  if (esPublico || (sesion && sesion.rol === ROL_PANEL)) {
    return next();
  }
  res.redirect('/login.html');
}

app.get('/', (req, res) => res.redirect('/admin.html'));
app.use(protegerPanel);
app.use(express.static(CARPETA_PANEL, { index: false }));

// ---------------------------------------------------------------------
// Errores: se apuntan en la consola y el navegador recibe un mensaje
// generico, sin detalles de la base de datos.
// ---------------------------------------------------------------------
app.use((error, req, res, next) => {
  if (error.type === 'entity.parse.failed') {
    return res.status(400).json({ error: 'Los datos enviados no son JSON válido' });
  }
  if (error.type === 'entity.too.large') {
    return res.status(413).json({ error: 'Los datos enviados son demasiado grandes' });
  }
  // Cualquier otro problema con los datos enviados que detecte express.json
  // (por ejemplo, un juego de caracteres que no admite: 415)
  if (error.type && error.status >= 400 && error.status < 500) {
    return res.status(error.status).json({ error: 'Los datos enviados no son válidos' });
  }
  // Un filtro de la URL que no es valido (leerFiltro)
  if (error.status === 400) {
    return res.status(400).json({ error: error.message });
  }
  // PostgreSQL ha cancelado una consulta que tardaba demasiado (statement_timeout en bd.js)
  if (error.code === '57014') {
    return res.status(503).json({ error: 'La base de datos tarda demasiado en responder' });
  }
  console.error('Error en', req.method, req.path, '-', error.message);
  res.status(500).json({ error: 'Error interno del servidor' });
});

// Solo arranca si se ejecuta este archivo; las pruebas lo importan sin arrancarlo.
if (require.main === module) {
  app.listen(PUERTO, HOST, (error) => {
    if (error) {
      console.error('No se pudo arrancar el servidor:', error.message);
      process.exit(1);
    }
    console.log(`Panel de NOVA en http://${HOST}:${PUERTO}`);
    console.log(bd.poolTienda
      ? `Tienda web en http://${HOST}:${PUERTO}/tienda/`
      : 'Tienda web sin configurar (faltan TIENDA_PGUSER y TIENDA_PGPASSWORD en .env)');
    console.log(correo.resumen()); // Resend, Ethereal (solo desarrollo) o sin correo
  });
}

module.exports = app;
