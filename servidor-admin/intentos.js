// intentos.js — limite de intentos de login: tras 5 fallos seguidos con el mismo nombre, ese nombre
// queda bloqueado unos minutos (429, sin mirar la contrasena). Se cuenta exista o no la cuenta, para no
// descubrir que usuarios hay. Al entrar bien vuelve a cero. Va en memoria: al reiniciar se olvida.

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

// Apunta un fallo de ese usuario; al quinto, lo bloquea
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

// Login correcto: el contador vuelve a cero
function borrarFallos(usuario) {
  fallos.delete(usuario);
}

module.exports = { tiempoDeBloqueo, apuntarFallo, borrarFallos };
