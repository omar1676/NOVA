// pedidos.js — rutas de Berme para crear pedidos y enviarlos a Odoo.
//
// NO SE MONTAN en servidor.js, a proposito:
//   - crearian pedidos sin login ni rol (segun la matriz de permisos, el
//     trabajador no crea pedidos; los crean el administrador y el
//     comercial);
//   - escriben en pedidos y log_eventos directamente, y web_nova no tiene
//     (ni debe tener) esos permisos;
//   - necesitan un Odoo, que no esta: odoo.js queda desactivado.
// Se guardan tal como los escribio Berme para cuando el equipo decida
// como integrarlos.

const express = require('express');
const { crearPedidoOdoo } = require('./odoo');

module.exports = function crearRouterPedidos(pool) {
  const router = express.Router();
  router.use(express.json());

  async function registrar(idPedido, accion, detalle) {
    await pool.query(
      'INSERT INTO log_eventos (tabla_afectada, id_registro, accion, detalle) VALUES ($1, $2, $3, $4)',
      ['pedidos', idPedido, accion, detalle]
    );
  }

  async function crearPedidoDB({ id_cliente, id_nave, lineas, personalizacion }) {
    const conexion = await pool.connect();
    try {
      await conexion.query('BEGIN');
      await conexion.query('SELECT pg_advisory_xact_lock(7001)');
      const siguiente = await conexion.query(
        `SELECT 'NOVA-' || lpad((COALESCE(MAX(substring(referencia from 6)::int), 0) + 1)::text, 4, '0') AS referencia
         FROM pedidos WHERE referencia ~ '^NOVA-[0-9]+$'`
      );
      const referencia = siguiente.rows[0].referencia;
      const [primera, ...resto] = lineas;
      const compra = await conexion.query(
        'SELECT realizar_compra($1, $2, $3, $4, $5) AS id_pedido',
        [referencia, id_cliente, primera.id_producto_sku, id_nave, primera.cantidad]
      );
      const idPedido = compra.rows[0].id_pedido;
      for (const linea of resto) {
        await conexion.query('SELECT anadir_linea_pedido($1, $2, $3, $4)', [
          idPedido,
          linea.id_producto_sku,
          id_nave,
          linea.cantidad,
        ]);
      }
      if (personalizacion) {
        await conexion.query(
          'UPDATE pedidos SET personalizado = true, personalizacion = $2 WHERE id_pedido = $1',
          [idPedido, personalizacion]
        );
      }
      await conexion.query("UPDATE pedidos SET estado = 'confirmado' WHERE id_pedido = $1", [idPedido]);
      await conexion.query('COMMIT');
      return { idPedido, referencia };
    } catch (error) {
      await conexion.query('ROLLBACK');
      throw error;
    } finally {
      conexion.release();
    }
  }

  async function sincronizarOdoo(idPedido) {
    const cabecera = await pool.query(
      `SELECT p.referencia, p.personalizacion, p.importe_total, c.nombre, c.email, c.tipo
       FROM pedidos p JOIN clientes c ON c.id_cliente = p.id_cliente
       WHERE p.id_pedido = $1`,
      [idPedido]
    );
    if (!cabecera.rows.length) return null;
    const pedido = cabecera.rows[0];
    const lineas = await pool.query(
      `SELECT s.sku, l.cantidad, l.precio_unitario
       FROM linea_pedido l JOIN producto_sku s ON s.id_producto_sku = l.id_producto_sku
       WHERE l.id_pedido = $1 ORDER BY l.id_linea`,
      [idPedido]
    );
    try {
      const odoo = await crearPedidoOdoo({
        referencia: pedido.referencia,
        cliente: { nombre: pedido.nombre, email: pedido.email, tipo: pedido.tipo },
        lineas: lineas.rows.map((l) => ({
          sku: l.sku,
          cantidad: l.cantidad,
          precio_unitario: Number(l.precio_unitario),
        })),
        personalizacion: pedido.personalizacion,
      });
      await registrar(idPedido, 'odoo_ok', JSON.stringify(odoo));
      if (Math.abs(Number(odoo.amount_untaxed) - Number(pedido.importe_total)) > 0.01) {
        await registrar(
          idPedido,
          'odoo_importe_dif',
          `PostgreSQL ${pedido.importe_total} / Odoo ${odoo.amount_untaxed}`
        );
      }
      return { ok: true, odoo };
    } catch (error) {
      await registrar(idPedido, 'odoo_pendiente', error.message);
      return { ok: false, error: error.message };
    }
  }

  router.post('/api/pedidos', async (req, res) => {
    const { id_cliente, id_nave = 1, lineas, personalizacion } = req.body;
    const valido =
      Number.isInteger(id_cliente) &&
      Array.isArray(lineas) &&
      lineas.length > 0 &&
      lineas.every((l) => Number.isInteger(l.id_producto_sku) && Number.isInteger(l.cantidad) && l.cantidad > 0);
    if (!valido) {
      return res.status(400).json({ error: 'Se necesita id_cliente y lineas [{id_producto_sku, cantidad}]' });
    }
    let creado;
    try {
      creado = await crearPedidoDB({ id_cliente, id_nave, lineas, personalizacion });
    } catch (error) {
      return res.status(409).json({ error: error.message });
    }
    const odoo = await sincronizarOdoo(creado.idPedido);
    res.status(201).json({ id_pedido: creado.idPedido, referencia: creado.referencia, odoo });
  });

  router.get('/api/pedidos/odoo-pendientes', async (req, res) => {
    const resultado = await pool.query(
      `SELECT p.id_pedido, p.referencia FROM pedidos p
       WHERE EXISTS (SELECT 1 FROM log_eventos l WHERE l.tabla_afectada = 'pedidos' AND l.id_registro = p.id_pedido AND l.accion = 'odoo_pendiente')
         AND NOT EXISTS (SELECT 1 FROM log_eventos l WHERE l.tabla_afectada = 'pedidos' AND l.id_registro = p.id_pedido AND l.accion = 'odoo_ok')
       ORDER BY p.id_pedido`
    );
    res.json(resultado.rows);
  });

  router.post('/api/pedidos/:id/reintentar-odoo', async (req, res) => {
    const odoo = await sincronizarOdoo(Number(req.params.id));
    if (!odoo) return res.status(404).json({ error: 'Pedido no encontrado' });
    res.json({ id_pedido: Number(req.params.id), odoo });
  });

  return router;
};
