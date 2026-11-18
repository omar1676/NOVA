// servidor.js — servidor Express de NOVA: entrega las paginas y la API /api/... (mismo origen).
// Paginas: /login.html (personal), /admin.html (panel), /trabajador/ (portal) y /tienda/ (tienda.js).
// El navegador nunca habla con PostgreSQL: lo hace este servidor (web_nova, y tienda_nova para la tienda).

const path = require('node:path');
const express = require('express');
const bd = require('./bd');
const sesiones = require('./sesiones');
const intentos = require('./intentos');
const consultas = require('./consultas');
const tienda = require('./tienda');
const correo = require('./correo');
const crearRutasTrabajador = require('./rutas-trabajador'); // portal del trabajador (Berme)
const odoo = require('./odoo'); // conector de Berme: desactivado sin configuracion

// Configuracion: puerto, host y carpetas de las paginas
const PUERTO = Number(process.env.PUERTO) || 3000;
const HOST = process.env.HOST || '127.0.0.1'; // solo este ordenador (en Docker, compose.yaml lo publica en 127.0.0.1)
const CARPETA_PANEL = path.join(__dirname, '..', '01_Interfaces', 'admin');
const CARPETA_TIENDA = path.join(__dirname, '..', '01_Interfaces', 'cliente');
const CARPETA_PORTAL = path.join(__dirname, '..', '01_Interfaces', 'trabajador');

// Login unico del personal: cada rol entra en su panel (administrador -> 01_Interfaces/admin,
// trabajador -> 01_Interfaces/trabajador, de Berme). Un rol sin panel web (comercial) no puede entrar.
const ROL_PANEL = 'administrador';
const ROL_PORTAL = 'trabajador';
const PANELES = {
  administrador: '/admin.html',
  trabajador: '/trabajador/trabajador.html'
};

const app = express();
app.disable('x-powered-by'); // no anunciar en cada respuesta que el servidor es Express

// Proteccion contra "DNS rebinding": solo se aceptan peticiones a 127.0.0.1 o localhost. Asi una
// web maliciosa que apunte su dominio a este ordenador no puede usar el panel desde el navegador.
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

// Lee el cuerpo JSON de las peticiones y lo deja en req.body
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
// La contrasena la comprueba PostgreSQL con iniciar_sesion (bcrypt): si no coincide, o la cuenta
// no tiene contrasena o esta desactivada, lanza RAISE EXCEPTION (codigo P0001).
// Tras 5 fallos seguidos con el mismo usuario: 429 unos minutos, sin mirar la contrasena (intentos.js).
// ---------------------------------------------------------------------

// El rol de un usuario ACTIVO, o null si la cuenta no existe o esta desactivada.
// La usan el login y la comprobacion de cada peticion del panel y del portal.
async function rolDeUsuarioActivo(cliente, idUsuario) {
  const resultado = await cliente.query(
    'SELECT r.nombre AS rol FROM public.usuarios u JOIN public.roles r ON r.id_rol = u.id_rol '
    + 'WHERE u.id_usuario = $1 AND u.activo', [idUsuario]);
  return resultado.rows.length > 0 ? resultado.rows[0].rol : null;
}

// Ruta: login del personal
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

    // Contrasena correcta, pero su rol no tiene panel web: 403 y sin sesion
    const destino = PANELES[datos.rol];
    if (!destino) {
      return res.status(403).json({
        error: `Acceso denegado: el usuario ${datos.usuario} (${datos.rol}) no tiene ningún panel web.`
      });
    }

    sesiones.crearSesion(req, res, datos);
    res.json({ usuario: datos.usuario, rol: datos.rol, accesoPanel: datos.rol === ROL_PANEL, destino });
  } catch (error) {
    if (error.code === 'P0001') {
      // El mismo mensaje para todo: no se dice si el usuario existe o no
      intentos.apuntarFallo(usuario);
      return res.status(401).json({ error: 'Usuario o contraseña incorrectos' });
    }
    throw error; // Express 5 lo pasa al manejador de errores del final
  }
});

// Ruta: logout (borra la sesion y la cookie)
app.post('/api/logout', (req, res) => {
  sesiones.cerrarSesion(req, res);
  res.json({ ok: true });
});

// Ruta: quien ha entrado, con que rol y cual es su panel (destino)
app.get('/api/sesion', (req, res) => {
  const sesion = sesiones.leerSesion(req);
  if (!sesion) {
    return res.status(401).json({ error: 'No has iniciado sesión' });
  }
  res.json({
    usuario: sesion.usuario, rol: sesion.rol,
    accesoPanel: sesion.rol === ROL_PANEL, destino: PANELES[sesion.rol]
  });
});

// ---------------------------------------------------------------------
// Permisos del panel (solo administradores) y del portal (solo trabajadores)
//   401 = no hay sesion, hay que entrar · 403 = hay sesion, pero su rol no tiene permiso
// En cada peticion se mira en la base si la cuenta sigue activa y con ese rol; si no, la
// sesion se borra en ese momento. El rol sale de la sesion y de la base, nunca del navegador.
// ---------------------------------------------------------------------

// Devuelve 0 si la sesion es de un usuario activo con ese rol, o el codigo
// de error: 401 (sin sesion, o la cuenta ya no esta activa) o 403 (otro rol).
async function comprobarRol(req, res, rol) {
  const sesion = sesiones.leerSesion(req);
  if (!sesion) return 401;
  if (sesion.rol !== rol) return 403;

  const rolActual = await bd.consultarSoloLectura((cliente) => rolDeUsuarioActivo(cliente, sesion.idUsuario));
  if (rolActual === null) {
    sesiones.cerrarSesion(req, res);
    return 401;
  }
  if (rolActual !== rol) {
    sesiones.cerrarSesion(req, res);
    return 403;
  }
  return 0;
}

// Crea un middleware que solo deja pasar a ese rol (si no, responde 401 o 403)
function soloRol(rol, mensajeSinPermiso) {
  return async (req, res, next) => {
    const teniaSesion = Boolean(sesiones.leerSesion(req));
    const codigo = await comprobarRol(req, res, rol);
    if (codigo === 401) {
      return res.status(401).json({
        error: teniaSesion ? 'Tu sesión ya no es válida. Vuelve a entrar.' : 'No has iniciado sesión'
      });
    }
    if (codigo === 403) {
      return res.status(403).json({ error: mensajeSinPermiso });
    }
    next();
  };
}

const soloAdministrador = soloRol(ROL_PANEL, 'Tu usuario no tiene permiso para el panel de administración');
const soloTrabajador = soloRol(ROL_PORTAL, 'Tu usuario no tiene permiso para el portal del trabajador');

// Toda la API del panel pide administrador, y la del portal, trabajador
app.use('/api/admin', soloAdministrador);
app.use('/api/trabajador', soloTrabajador);

// Las rutas del portal del trabajador (rutas-trabajador.js, de Berme). Van
// detras de soloTrabajador y usan el rol portal_trabajador (script 23).
app.use(crearRutasTrabajador(bd, sesiones));

// Lee un filtro de la URL (por ejemplo ?estado=pendiente). Si no viene, devuelve '' (sin filtro);
// si trae un valor que no esta en la lista de permitidos, la peticion se rechaza con 400.
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

// El texto del buscador va dentro de un ILIKE, donde % y _ son comodines: se escapan con \
// para buscarlos como letras normales (si no, ?texto=_ devolveria todas las filas).
function leerTexto(req) {
  return leerFiltro(req, 'texto').replace(/[\\%_]/g, '\\$&');
}

// Un error 400 con un mensaje que se puede ensenar al navegador
function errorDePeticion(mensaje) {
  const error = new Error(mensaje);
  error.status = 400;
  return error;
}

// Las ocho rutas de lectura del panel. Cada una lee sus filtros y llama a su
// consulta de consultas.js dentro de una transaccion de solo lectura.

// Ruta: dashboard (cifras, ultimos pedidos y stock bajo)
app.get('/api/admin/dashboard', async (req, res) => {
  res.json(await bd.consultarSoloLectura((cliente) => consultas.dashboard(cliente)));
});

// Ruta: pedidos (filtro por estado y buscador)
app.get('/api/admin/pedidos', async (req, res) => {
  const estado = leerFiltro(req, 'estado', consultas.ESTADOS_PEDIDO);
  const texto = leerTexto(req);
  res.json(await bd.consultarSoloLectura((cliente) => consultas.pedidos(cliente, estado, texto)));
});

// Ruta: productos (activos o inactivos y buscador)
app.get('/api/admin/productos', async (req, res) => {
  const estado = leerFiltro(req, 'estado', consultas.ESTADOS_ACTIVO);
  const texto = leerTexto(req);
  res.json(await bd.consultarSoloLectura((cliente) => consultas.productos(cliente, estado, texto)));
});

// Ruta: inventario (stock suficiente, bajo o agotado y buscador)
app.get('/api/admin/inventario', async (req, res) => {
  const estado = leerFiltro(req, 'estado', consultas.ESTADOS_STOCK);
  const texto = leerTexto(req);
  res.json(await bd.consultarSoloLectura((cliente) => consultas.inventario(cliente, estado, texto)));
});

// Ruta: clientes (activos o inactivos y buscador)
app.get('/api/admin/clientes', async (req, res) => {
  const estado = leerFiltro(req, 'estado', consultas.ESTADOS_ACTIVO);
  const texto = leerTexto(req);
  res.json(await bd.consultarSoloLectura((cliente) => consultas.clientes(cliente, estado, texto)));
});

// Ruta: trabajadores y sus cuentas de usuario
app.get('/api/admin/trabajadores', async (req, res) => {
  const estado = leerFiltro(req, 'estado', consultas.ESTADOS_ACTIVO);
  const texto = leerTexto(req);
  res.json(await bd.consultarSoloLectura((cliente) => consultas.trabajadores(cliente, estado, texto)));
});

// Ruta: auditoria (filtro por accion y buscador)
app.get('/api/admin/auditoria', async (req, res) => {
  const accion = leerFiltro(req, 'accion', consultas.ACCIONES_AUDITORIA);
  const texto = leerTexto(req);
  res.json(await bd.consultarSoloLectura((cliente) => consultas.auditoria(cliente, accion, texto)));
});

// Ruta: estadisticas (mes actual, ingresos y mas vendidos)
app.get('/api/admin/estadisticas', async (req, res) => {
  res.json(await bd.consultarSoloLectura((cliente) => consultas.estadisticas(cliente)));
});

// ---------------------------------------------------------------------
// Ruta: boton "Marcar en reparto", la unica del panel que cambia algo.
// Pasa un pedido confirmado a "enviado" con marcar_pedido_en_reparto (script 22), en una transaccion
// aparte (bd.marcarEnReparto). La funcion vuelve a comprobar que es administrador y la auditoria
// apunta el cambio a su nombre.
//   401/403 sin permiso · 415 sin JSON · 404 no existe · 409 no esta confirmado · 200 ya "enviado"
// ---------------------------------------------------------------------

// Mensaje de la funcion SQL -> [codigo HTTP, texto para el panel]
const ERRORES_REPARTO = {
  'Usuario no autorizado': [403, 'Tu usuario no tiene permiso para el panel de administración'],
  'El pedido no existe': [404, 'Ese pedido no existe'],
  'Solo se puede pasar a reparto un pedido confirmado':
    [409, 'Solo se puede marcar en reparto un pedido confirmado (puede que este ya haya cambiado de estado).']
};

app.post('/api/admin/pedidos/:id/reparto', async (req, res) => {
  // Solo JSON, como manda el panel: un formulario de otra web no puede enviar JSON
  // sin que el servidor lo permita (CORS)
  if (!req.is('application/json')) {
    return res.status(415).json({ error: 'Los datos tienen que ir en JSON' });
  }
  // El id tiene que ser un numero entero positivo (de 1 a 9 cifras)
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
// Van antes que los del panel para que protegerPanel no pida sesion. /tienda se redirige a /tienda/
// para que css/ y js/ se busquen dentro. express.static no sale de 01_Interfaces/cliente (rechaza ..).
// ---------------------------------------------------------------------
app.use((req, res, next) => {
  if (req.path === '/tienda') return res.redirect('/tienda/');
  next();
});
app.use('/tienda', express.static(CARPETA_TIENDA));
app.use('/tienda', (req, res) => res.status(404).send('No encontrado')); // y no al login del panel

// ---------------------------------------------------------------------
// Archivos del panel y del portal del trabajador
// login.html es la misma para los dos. Sin sesion (o con la de otro rol) solo se entrega lo que
// necesita esa pagina; lo demas lleva a login.html. Como en la API, el rol se mira en la base cada vez.
// ---------------------------------------------------------------------

// Lo que necesita la pagina de acceso: se ve sin sesion
const ARCHIVOS_PUBLICOS = ['/login.html', '/login.js', '/styles.css'];

// La ruta pedida, en minusculas, o null si no vale (mal codificada o con ..)
function leerRuta(req) {
  let ruta;
  try {
    ruta = decodeURIComponent(req.path).toLowerCase();
  } catch {
    return null; // una ruta mal codificada, como /%E0
  }
  if (ruta.includes('..') || ruta.includes('\\')) {
    return null; // nada de salir de la carpeta
  }
  return ruta;
}

// Paginas del panel: solo administradores (lo publico, para todos); si no, a login.html
async function protegerPanel(req, res, next) {
  const ruta = leerRuta(req);
  if (ruta === null) return res.status(400).end();

  const esPublico = ARCHIVOS_PUBLICOS.includes(ruta) || ruta.startsWith('/img/');
  if (esPublico || await comprobarRol(req, res, ROL_PANEL) === 0) {
    return next();
  }
  res.redirect('/login.html');
}

// Paginas del portal: solo trabajadores; si no, a login.html
async function protegerPortal(req, res, next) {
  const ruta = leerRuta(req);
  if (ruta === null) return res.status(400).end();

  if (await comprobarRol(req, res, ROL_PORTAL) === 0) {
    return next();
  }
  res.redirect('/login.html');
}

// El portal: /trabajador lleva a su pagina de inicio
app.use((req, res, next) => {
  const ruta = req.path.toLowerCase();
  if (ruta === '/trabajador' || ruta === '/trabajador/') return res.redirect(PANELES[ROL_PORTAL]);
  next();
});
app.use('/trabajador', protegerPortal);
app.use('/trabajador', express.static(CARPETA_PORTAL, { index: false }));
app.use('/trabajador', (req, res) => res.status(404).send('No encontrado'));

// El panel: la raiz lleva a admin.html y sus archivos van protegidos
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
  // Otro problema que detecte express.json (por ejemplo, un juego de caracteres que no admite: 415)
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
    console.log(`Panel de NOVA en http://localhost:${PUERTO}`);
    console.log(bd.poolTienda
      ? `Tienda web en http://localhost:${PUERTO}/tienda/`
      : 'Tienda web sin configurar (faltan TIENDA_PGUSER y TIENDA_PGPASSWORD en .env)');
    console.log(correo.resumen()); // Resend, Ethereal (solo desarrollo) o sin correo
    console.log(`Portal del trabajador en http://localhost:${PUERTO}/trabajador/ (script 23)`);
    console.log(odoo.resumen()); // las rutas de pedidos.js (crear pedidos y Odoo) no se montan
  });
}

module.exports = app;
