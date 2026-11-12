// sesiones.js — las sesiones del personal (panel y portal) y las de la tienda.
//
// Cuando alguien entra con su usuario y su contrasena, el servidor crea un
// identificador aleatorio (token) y se lo da al navegador en una cookie
// HttpOnly: el JavaScript de la pagina no puede leerla, el navegador solo la
// envia en cada peticion. El servidor guarda en memoria a quien corresponde
// cada token. La contrasena no se guarda en ningun sitio.
//
// Hay DOS almacenes separados, cada uno con su cookie y su propio Map:
//   - sesion_nova:   el personal que entra por login.html (el administrador
//                    va al panel y el trabajador, al portal).
//   - sesion_tienda: clientes de la tienda web. Esta cookie solo se envia a
//                    /api/tienda, asi que nunca llega a las rutas del panel.
// Un token de un almacen no existe en el otro: una sesion de cliente no
// sirve para el panel ni para el portal, ni una del personal para comprar.
//
// Al reiniciar el servidor las sesiones se pierden y hay que volver a entrar.

const crypto = require('node:crypto');

const DURACION_MS = 2 * 60 * 60 * 1000; // 2 horas

// Crea un almacen de sesiones con su propia cookie.
function crearAlmacen(nombreCookie, rutaCookie) {
  const sesiones = new Map(); // token -> { ...datos, caduca }

  const opcionesCookie = {
    httpOnly: true,     // el JavaScript de la pagina no la puede leer
    sameSite: 'strict', // el navegador no la envia desde otras webs
    path: rutaCookie    // solo se envia a las rutas que empiezan asi
  };

  // Express no trae lector de cookies. Para una sola cookie basta con buscarla
  // en la cabecera, que llega asi:  Cookie: otra=1; sesion_nova=ab12...
  function leerToken(req) {
    const cabecera = req.headers.cookie || '';
    for (const trozo of cabecera.split(';')) {
      const [nombre, valor] = trozo.trim().split('=');
      if (nombre === nombreCookie) return valor;
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
    res.cookie(nombreCookie, token, { ...opcionesCookie, maxAge: DURACION_MS });
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
    res.clearCookie(nombreCookie, opcionesCookie);
  }

  return { crearSesion, leerSesion, cerrarSesion };
}

const panel = crearAlmacen('sesion_nova', '/');
const tienda = crearAlmacen('sesion_tienda', '/api/tienda');

// Las del personal se usan tal cual (sesiones.leerSesion...) en servidor.js y
// rutas-trabajador.js; las de la tienda van en sesiones.tienda.
module.exports = { ...panel, tienda };
