// bd.js — la conexion con PostgreSQL.
//
// El servidor se conecta SIEMPRE con web_nova (script 19_usuario_web.sql),
// nunca con postgres. Los datos de conexion salen de las variables de entorno
// PGHOST, PGPORT, PGDATABASE, PGUSER y PGPASSWORD, que la libreria pg lee sola.
// Se escriben en el archivo .env, que no se sube a Git.

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

// Ejecuta "trabajo" dentro de una transaccion de SOLO LECTURA y con los
// permisos de panel_lectura (script 19). Hay dos barreras contra escribir:
//   - SET LOCAL ROLE panel_lectura: web_nova no tiene permisos propios
//     (NOINHERIT) y solo puede pasar a panel_lectura, que no tiene ningun
//     permiso de escritura. Esta barrera la pone PostgreSQL.
//   - READ ONLY: ademas, la transaccion rechaza cualquier INSERT, UPDATE o
//     DELETE aunque hubiera permiso.
// REPEATABLE READ hace que todas las consultas de una peticion vean la misma
// "foto" de los datos: las cifras del dashboard cuadran entre si aunque
// alguien este escribiendo a la vez.
async function consultarSoloLectura(trabajo) {
  const cliente = await pool.connect();
  let conexionRota = false;
  try {
    await cliente.query('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY');
    await cliente.query('SET LOCAL ROLE panel_lectura');
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

// Para /api/estado: comprueba que la base responde y con que usuario.
async function comprobarConexion() {
  const resultado = await pool.query('SELECT current_user AS usuario, current_database() AS base');
  return resultado.rows[0];
}

module.exports = { consultarSoloLectura, comprobarConexion, pool };
