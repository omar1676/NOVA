// bd.js — conexiones con PostgreSQL. El panel y el portal usan SIEMPRE web_nova
// (script 19_usuario_web.sql), nunca postgres; la tienda usa tienda_nova (mas abajo).
// Los datos de conexion (PGHOST, PGUSER...) van en .env, que no se sube a Git; pg los lee solo.

const { Pool, types } = require('pg');

// PostgreSQL devuelve numeric y bigint como texto para no perder precision. Aqui son importes
// y contadores, asi que se pasan a numero para que el JSON lleve numeros.
types.setTypeParser(1700, (valor) => parseFloat(valor)); // numeric: importes
types.setTypeParser(20, (valor) => parseInt(valor, 10)); // bigint: count(*), sum de enteros

// Sin .env no arranca, y nunca con el superusuario postgres
if (!process.env.PGUSER || !process.env.PGDATABASE) {
  throw new Error('Faltan PGUSER o PGDATABASE: copia .env.example como .env y rellenalo');
}
if (process.env.PGUSER === 'postgres') {
  throw new Error('El servidor no puede conectarse como postgres: usa web_nova (script 19)');
}

// Conexiones del panel y del portal (usuario web_nova)
const pool = new Pool({
  max: 5,                          // como mucho 5 conexiones a la vez
  connectionTimeoutMillis: 5000,   // si no hay conexion libre en 5 s, error en vez de esperar siempre
  statement_timeout: 10000         // PostgreSQL cancela una consulta que tarde mas de 10 s
});

// Si se cae una conexion que estaba esperando, se avisa sin tumbar el servidor.
pool.on('error', (error) => {
  console.error('Error en una conexion inactiva con PostgreSQL:', error.message);
});

// Ejecuta "trabajo" en una transaccion del pool que toca (panel o tienda) y con su rol de PostgreSQL.
// Si todo va bien, COMMIT; si algo falla, ROLLBACK (no queda nada a medias) y el error sigue.
// "inicio" y "cambioDeRol" son siempre textos fijos de este archivo, nunca datos del navegador.
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

// REPEATABLE READ: todas las consultas de una peticion ven la misma "foto" de los datos,
// asi las cifras del dashboard cuadran aunque alguien este escribiendo a la vez.
const SOLO_LECTURA = 'BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY';

// Lecturas del panel: transaccion de SOLO LECTURA con el rol panel_lectura (script 19). Dos barreras:
//   - web_nova no tiene permisos propios (NOINHERIT) y panel_lectura no puede escribir nada.
//   - READ ONLY rechaza cualquier INSERT, UPDATE o DELETE aunque hubiera permiso.
async function consultarSoloLectura(trabajo) {
  return enTransaccion(pool, SOLO_LECTURA, 'SET LOCAL ROLE panel_lectura', trabajo);
}

// La UNICA escritura del panel: el boton "Marcar en reparto" (script 22), en su propia transaccion.
// El rol panel_reparto no puede leer ni escribir tablas: solo ejecutar marcar_pedido_en_reparto,
// que vuelve a comprobar que el usuario es administrador y que el pedido esta confirmado.
async function marcarEnReparto(idUsuario, idPedido) {
  await enTransaccion(pool, 'BEGIN', 'SET LOCAL ROLE panel_reparto', (cliente) =>
    cliente.query('SELECT public.marcar_pedido_en_reparto($1, $2)', [idUsuario, idPedido]));
}

// ---------------------------------------------------------------------
// El portal del trabajador (script 23): la misma conexion (web_nova), con el rol portal_trabajador.
// ---------------------------------------------------------------------

// Lecturas del portal: SOLO LECTURA, como las del panel, y solo las columnas que ensena el portal
async function consultarComoTrabajador(trabajo) {
  return enTransaccion(pool, SOLO_LECTURA, 'SET LOCAL ROLE portal_trabajador', trabajo);
}

// Las dos escrituras del portal: el rol no escribe en tablas, solo ejecuta avanzar_pedido_trabajador
// y ajustar_existencias_trabajador, que vuelven a comprobar que el usuario es un trabajador activo.
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
// La tienda web usa OTRA conexion, el usuario tienda_nova (script 20): asi web_nova sigue sin escribir.
// tienda_web solo lee catalogo, cliente y pedidos, y llama a las cinco funciones del script 20
// (registro, login y compra). Sin TIENDA_PGUSER y TIENDA_PGPASSWORD, el panel va igual y la tienda, 503.
// ---------------------------------------------------------------------
const tiendaConfigurada = Boolean(process.env.TIENDA_PGUSER && process.env.TIENDA_PGPASSWORD);

if (process.env.TIENDA_PGUSER === 'postgres') {
  throw new Error('La tienda no puede conectarse como postgres: usa tienda_nova (script 20)');
}

// Conexiones de la tienda (null si no esta configurada). Mismo servidor y base que el panel.
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

// Operaciones de la tienda: UNA transaccion con el rol tienda_web; si algo falla (sin stock...), ROLLBACK.
// No es READ ONLY porque las compras escriben, pero solo a traves de las funciones del script 20.
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
