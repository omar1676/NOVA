// intentos.js — limite de intentos de inicio de sesion.
//
// Si alguien falla 5 veces seguidas con el mismo nombre de usuario, ese
// nombre queda bloqueado unos minutos: el servidor responde 429 sin mirar la
// contrasena, aunque esta vez sea la buena.
//   - Se cuenta por nombre de usuario, exista o no la cuenta. Asi la
//     respuesta es la misma en los dos casos y no se descubre que usuarios hay.
//   - Al entrar bien, el contador vuelve a cero.
//   - Se guarda en memoria: al reiniciar el servidor se olvida.

const MAX_FALLOS = 5;
const BLOQUEO_MS = Number(process.env.BLOQUEO_LOGIN_MS) || 5 * 60 * 1000; // 5 minutos

const fallos = new Map(); // usuario -> { veces, ultimo, bloqueadoHasta }

// Cuantos milisegundos le quedan de bloqueo a ese usuario (0 = no esta bloqueado)
function tiempoDeBloqueo(usuario) {
  const registro = fallos.get(usuario);
  if (!registro) return 0;
  const quedan = registro.bloqueadoHasta - Date.now();
  return quedan > 0 ? quedan : 0;
}

function apuntarFallo(usuario) {
  const ahora = Date.now();

  // Se olvidan los registros viejos: sin fallos recientes y sin bloqueo en marcha
  for (const [nombre, registro] of fallos) {
    if (registro.bloqueadoHasta < ahora && registro.ultimo < ahora - BLOQUEO_MS) {
      fallos.delete(nombre);
    }
  }

  const registro = fallos.get(usuario) || { veces: 0, ultimo: 0, bloqueadoHasta: 0 };
  if (registro.bloqueadoHasta !== 0 && registro.bloqueadoHasta < ahora) {
    registro.veces = 0;            // ya cumplio un bloqueo: empieza de cero
    registro.bloqueadoHasta = 0;
  }
  registro.veces += 1;
  registro.ultimo = ahora;
  if (registro.veces >= MAX_FALLOS) {
    registro.bloqueadoHasta = ahora + BLOQUEO_MS;
  }
  fallos.set(usuario, registro);
}

function borrarFallos(usuario) {
  fallos.delete(usuario);
}

module.exports = { tiempoDeBloqueo, apuntarFallo, borrarFallos };
