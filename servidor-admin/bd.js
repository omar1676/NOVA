// bd.js — las conexiones con PostgreSQL.
//
// El panel y el portal del trabajador se conectan SIEMPRE con web_nova
// (script 19_usuario_web.sql), nunca con postgres. Los datos de conexion
// salen de las variables de entorno PGHOST, PGPORT, PGDATABASE, PGUSER y
// PGPASSWORD, que la libreria pg lee sola. Se escriben en el archivo .env,
// que no se sube a Git.
// La tienda usa su propio usuario, tienda_nova (ver mas abajo).

const { Pool, types } = require('pg');

// PostgreSQL devuelve los numeric y los bigint como texto para no perder
// precision. En el panel son importes con dos decimales y contadores, asi que
// los convertimos a numero para que el JSON lleve numeros.
types.setTypeParser(1700, (valor) => parseFloat(valor)); // numeric: importes
types.setTypeParser(20, (valor) => parseInt(valor, 10)); // bigint: count(*), sum de enteros

if (!process.env.PGUSER || !process.env.PGDATABASE) {
  throw new Error('Faltan PGUSER o PGDATABASE: copia .env.example como .env y rellenalo');
}
if (process.env.PGUSER === 'postgres') {
  throw new Error('El servidor no puede conectarse como postgres: usa web_nova (script 19)');
}

const pool = new Pool({
  max: 5,                          // como mucho 5 conexiones a la vez
  connectionTimeoutMillis: 5000,   // si no hay conexion libre en 5 s, error en vez de esperar siempre
  statement_timeout: 10000         // PostgreSQL cancela una consulta que tarde mas de 10 s
});

// Si se cae una conexion que estaba esperando, se avisa sin tumbar el servidor.
pool.on('error', (error) => {
  console.error('Error en una conexion inactiva con PostgreSQL:', error.message);
});

// Abre una transaccion en una conexion de "conexiones" (el pool del panel o el
// de la tienda), cambia al rol de PostgreSQL que toca y ejecuta "trabajo".
// Si todo va bien, COMMIT; si algo falla, ROLLBACK y el error sigue hacia
// arriba: no queda nada a medias. "inicio" y "cambioDeRol" son siempre textos
// fijos de este archivo, nunca datos que lleguen del navegador.
async function enTransaccion(conexiones, inicio, cambioDeRol, trabajo) {
  const cliente = await conexiones.connect();
  let conexionRota = false;
  try {
    await cliente.query(inicio);
    await cliente.query(cambioDeRol);
    const resultado = await trabajo(cliente);
    await cliente.query('COMMIT');
    return resultado;
  } catch (error) {
    // Si ni siquiera se puede hacer ROLLBACK, la conexion esta rota
    await cliente.query('ROLLBACK').catch(() => { conexionRota = true; });
    throw error;
  } finally {
    cliente.release(conexionRota); // true = se cierra en lugar de volver al pool
  }
}

// REPEATABLE READ hace que todas las consultas de una peticion vean la misma
// "foto" de los datos: las cifras del dashboard cuadran entre si aunque
// alguien este escribiendo a la vez.
const SOLO_LECTURA = 'BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY';

// Ejecuta "trabajo" dentro de una transaccion de SOLO LECTURA y con los
// permisos de panel_lectura (script 19). Hay dos barreras contra escribir:
//   - SET LOCAL ROLE panel_lectura: web_nova no tiene permisos propios
//     (NOINHERIT) y aqui pasa a panel_lectura, que no tiene ningun
//     permiso de escritura. Esta barrera la pone PostgreSQL.
//   - READ ONLY: ademas, la transaccion rechaza cualquier INSERT, UPDATE o
//     DELETE aunque hubiera permiso.
async function consultarSoloLectura(trabajo) {
  return enTransaccion(pool, SOLO_LECTURA, 'SET LOCAL ROLE panel_lectura', trabajo);
}

// La UNICA escritura del panel: el boton "Marcar en reparto" (script 22).
// Va en una transaccion aparte, solo para esta llamada, con el rol
// panel_reparto: no puede leer ni escribir ninguna tabla, solo ejecutar
// marcar_pedido_en_reparto, que vuelve a comprobar que el usuario es
// administrador y que el pedido esta confirmado. Todas las demas consultas
// del panel siguen yendo por consultarSoloLectura.
async function marcarEnReparto(idUsuario, idPedido) {
  await enTransaccion(pool, 'BEGIN', 'SET LOCAL ROLE panel_reparto', (cliente) =>
    cliente.query('SELECT public.marcar_pedido_en_reparto($1, $2)', [idUsuario, idPedido]));
}

// ---------------------------------------------------------------------
// El portal del trabajador (script 23) usa la misma conexion (web_nova),
// pero con su propio rol, portal_trabajador:
//   - consultarComoTrabajador: lecturas, en una transaccion de SOLO
//     LECTURA, como las del panel. Solo ve las columnas que ensena el portal.
//   - cambiarComoTrabajador: las dos escrituras del portal. El rol no puede
//     escribir en ninguna tabla: solo ejecutar avanzar_pedido_trabajador y
//     ajustar_existencias_trabajador, que vuelven a comprobar que el usuario
//     es un trabajador activo.
// ---------------------------------------------------------------------
async function consultarComoTrabajador(trabajo) {
  return enTransaccion(pool, SOLO_LECTURA, 'SET LOCAL ROLE portal_trabajador', trabajo);
}

async function cambiarComoTrabajador(sql, parametros) {
  return enTransaccion(pool, 'BEGIN', 'SET LOCAL ROLE portal_trabajador', (cliente) =>
    cliente.query(sql, parametros));
}

// Para /api/estado: comprueba que la base responde y con que usuario.
async function comprobarConexion() {
  const resultado = await pool.query('SELECT current_user AS usuario, current_database() AS base');
  return resultado.rows[0];
}

// ---------------------------------------------------------------------
// La tienda web usa OTRA conexion, con el usuario tienda_nova (script 20).
// Asi web_nova sigue sin poder escribir nada, y la tienda solo puede lo que
// permite tienda_web: leer el catalogo, los datos del cliente y sus pedidos,
// y llamar a las cinco funciones del script 20 (registro, login y compra).
// Servidor, base y puerto son los mismos (PGHOST, PGPORT, PGDATABASE); el
// usuario y la contrasena van en TIENDA_PGUSER y TIENDA_PGPASSWORD. Si no
// estan, el panel funciona igual y la tienda responde 503.
// ---------------------------------------------------------------------
const tiendaConfigurada = Boolean(process.env.TIENDA_PGUSER && process.env.TIENDA_PGPASSWORD);

if (process.env.TIENDA_PGUSER === 'postgres') {
  throw new Error('La tienda no puede conectarse como postgres: usa tienda_nova (script 20)');
}

const poolTienda = tiendaConfigurada
  ? new Pool({
    user: process.env.TIENDA_PGUSER,
    password: process.env.TIENDA_PGPASSWORD,
    max: 5,
    connectionTimeoutMillis: 5000,
    statement_timeout: 10000
  })
  : null;

if (poolTienda) {
  poolTienda.on('error', (error) => {
    console.error('Error en una conexion inactiva de la tienda:', error.message);
  });
}

// Ejecuta "trabajo" en UNA transaccion con los permisos de tienda_web.
// Si algo falla (por ejemplo, falta stock al confirmar), ROLLBACK: no queda
// nada a medias. No es READ ONLY porque las funciones de compra escriben,
// pero tienda_web no tiene permiso para escribir en ninguna tabla por su
// cuenta: solo a traves de esas funciones.
async function operarEnTienda(trabajo) {
  if (!poolTienda) {
    const error = new Error('La tienda no está disponible en este momento');
    error.status = 503;
    error.publico = true;
    throw error;
  }
  return enTransaccion(poolTienda, 'BEGIN', 'SET LOCAL ROLE tienda_web', trabajo);
}

module.exports = {
  consultarSoloLectura, marcarEnReparto, consultarComoTrabajador, cambiarComoTrabajador,
  comprobarConexion, pool, operarEnTienda, poolTienda
};
