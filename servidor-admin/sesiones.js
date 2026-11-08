// sesiones.js — las sesiones del panel.
//
// Cuando alguien entra con su usuario y su contrasena, el servidor crea un
// identificador aleatorio (token) y se lo da al navegador en una cookie
// HttpOnly: el JavaScript de la pagina no puede leerla, el navegador solo la
// envia en cada peticion. El servidor guarda en memoria a quien corresponde
// cada token. La contrasena no se guarda en ningun sitio.
//
// Al reiniciar el servidor las sesiones se pierden y hay que volver a entrar.

const crypto = require('node:crypto');

const NOMBRE_COOKIE = 'sesion_nova';
const DURACION_MS = 2 * 60 * 60 * 1000; // 2 horas
const sesiones = new Map(); // token -> { idUsuario, usuario, rol, caduca }

const OPCIONES_COOKIE = {
  httpOnly: true,     // el JavaScript de la pagina no la puede leer
  sameSite: 'strict', // el navegador no la envia desde otras webs
  path: '/'
};

// Express no trae lector de cookies. Para una sola cookie basta con buscarla
// en la cabecera, que llega asi:  Cookie: otra=1; sesion_nova=ab12...
function leerToken(req) {
  const cabecera = req.headers.cookie || '';
  for (const trozo of cabecera.split(';')) {
    const [nombre, valor] = trozo.trim().split('=');
    if (nombre === NOMBRE_COOKIE) return valor;
  }
  return null;
}

// Crea una sesion nueva (y borra la anterior, si la habia) y envia la cookie.
function crearSesion(req, res, datos) {
  const anterior = leerToken(req);
  if (anterior) sesiones.delete(anterior);

  // De paso se borran las sesiones caducadas que nadie ha vuelto a usar
  for (const [token, sesion] of sesiones) {
    if (sesion.caduca < Date.now()) sesiones.delete(token);
  }

  const token = crypto.randomBytes(32).toString('hex');
  sesiones.set(token, { ...datos, caduca: Date.now() + DURACION_MS });
  res.cookie(NOMBRE_COOKIE, token, { ...OPCIONES_COOKIE, maxAge: DURACION_MS });
}

// Devuelve los datos de la sesion, o null si no hay sesion o ha caducado.
function leerSesion(req) {
  const token = leerToken(req);
  const sesion = token ? sesiones.get(token) : undefined;
  if (!sesion) return null;
  if (sesion.caduca < Date.now()) {
    sesiones.delete(token);
    return null;
  }
  return sesion;
}

function cerrarSesion(req, res) {
  const token = leerToken(req);
  if (token) sesiones.delete(token);
  res.clearCookie(NOMBRE_COOKIE, OPCIONES_COOKIE);
}

module.exports = { crearSesion, leerSesion, cerrarSesion };
