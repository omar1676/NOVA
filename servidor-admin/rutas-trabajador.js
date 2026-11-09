const express = require("express");

const siguienteEstado = {
  confirmado: "en_preparacion",
  en_preparacion: "enviado",
  enviado: "entregado"
};

function esEnteroPositivo(valor) {
  return /^[0-9]+$/.test(String(valor)) && Number(valor) > 0;
}

function crearRutasTrabajador(pool) {
  const router = express.Router();
  router.use(express.json());

  router.get("/api/trabajador/pedidos", async function (req, res) {
    try {
      const resultado = await pool.query(
        `SELECT p.id_pedido, p.referencia, c.nombre AS cliente, p.fecha_pedido,
                p.fecha_objetivo, p.estado, p.importe_total
         FROM public.pedidos p
         JOIN public.clientes c ON c.id_cliente = p.id_cliente
         WHERE p.estado IN ($1, $2, $3, $4)
         ORDER BY p.fecha_pedido DESC`,
        ["confirmado", "en_preparacion", "enviado", "entregado"]
      );
      res.json(resultado.rows);
    } catch (error) {
      res.status(500).json({ error: "No se han podido leer los pedidos" });
    }
  });

  router.patch("/api/trabajador/pedidos/:id/estado", async function (req, res) {
    const idPedido = req.params.id;
    const estadoNuevo = req.body ? req.body.estado : undefined;

    if (!esEnteroPositivo(idPedido)) {
      return res.status(400).json({ error: "Identificador de pedido no válido" });
    }

    try {
      const actual = await pool.query(
        "SELECT estado FROM public.pedidos WHERE id_pedido = $1",
        [idPedido]
      );

      if (actual.rows.length === 0) {
        return res.status(404).json({ error: "El pedido no existe" });
      }

      const estadoActual = actual.rows[0].estado;

      if (!siguienteEstado[estadoActual]) {
        return res.status(400).json({ error: "Un pedido en estado " + estadoActual + " no se puede avanzar" });
      }

      if (estadoNuevo !== siguienteEstado[estadoActual]) {
        return res.status(400).json({ error: "Solo se puede pasar de " + estadoActual + " a " + siguienteEstado[estadoActual] });
      }

      const cambio = await pool.query(
        `UPDATE public.pedidos
         SET estado = $1
         WHERE id_pedido = $2 AND estado = $3
         RETURNING id_pedido, referencia, estado`,
        [estadoNuevo, idPedido, estadoActual]
      );

      if (cambio.rows.length === 0) {
        return res.status(409).json({ error: "El pedido ha cambiado de estado, recarga la página" });
      }

      res.json(cambio.rows[0]);
    } catch (error) {
      res.status(500).json({ error: "No se ha podido cambiar el estado" });
    }
  });

  router.get("/api/trabajador/inventario", async function (req, res) {
    try {
      const resultado = await pool.query(
        `SELECT e.id_producto_sku, e.id_nave, n.nombre AS nave, m.nombre AS modelo,
                v.color, s.talla, s.sku, e.cantidad
         FROM public.existencias e
         JOIN public.nave n ON n.id_nave = e.id_nave
         JOIN public.producto_sku s ON s.id_producto_sku = e.id_producto_sku
         JOIN public.variantes v ON v.id_variante = s.id_variante
         JOIN public.modelos m ON m.id_modelo = v.id_modelo
         ORDER BY n.nombre, m.nombre, v.color, s.talla`
      );
      res.json(resultado.rows);
    } catch (error) {
      res.status(500).json({ error: "No se ha podido leer el inventario" });
    }
  });

  router.patch("/api/trabajador/inventario/:idSku/:idNave", async function (req, res) {
    const idSku = req.params.idSku;
    const idNave = req.params.idNave;
    const cantidad = req.body ? req.body.cantidad : undefined;

    if (!esEnteroPositivo(idSku) || !esEnteroPositivo(idNave)) {
      return res.status(400).json({ error: "Identificadores no válidos" });
    }

    if (!Number.isInteger(cantidad) || cantidad < 0) {
      return res.status(400).json({ error: "La cantidad debe ser un número entero igual o mayor que 0" });
    }

    try {
      const cambio = await pool.query(
        `UPDATE public.existencias
         SET cantidad = $1
         WHERE id_producto_sku = $2 AND id_nave = $3
         RETURNING id_producto_sku, id_nave, cantidad`,
        [cantidad, idSku, idNave]
      );

      if (cambio.rows.length === 0) {
        return res.status(404).json({ error: "No existe esa existencia" });
      }

      res.json(cambio.rows[0]);
    } catch (error) {
      res.status(500).json({ error: "No se ha podido guardar la cantidad" });
    }
  });

  router.get("/api/trabajador/personalizados", async function (req, res) {
    try {
      const pedidos = await pool.query(
        `SELECT p.id_pedido, p.referencia, c.nombre AS cliente, p.fecha_objetivo,
                p.estado, p.cantidad_total, p.personalizacion
         FROM public.pedidos p
         JOIN public.clientes c ON c.id_cliente = p.id_cliente
         WHERE p.personalizado = $1
         ORDER BY p.fecha_pedido DESC`,
        [true]
      );

      const configuraciones = await pool.query(
        `SELECT x.id_configuracion, c.nombre AS cliente, p.referencia, x.talla_referencia,
                x.color_principal, x.color_secundario, x.material, x.tipo_suela,
                x.texto_personalizado, x.fecha_creacion
         FROM public.configuraciones_xnova x
         JOIN public.clientes c ON c.id_cliente = x.id_cliente
         LEFT JOIN public.pedidos p ON p.id_pedido = x.id_pedido
         ORDER BY x.fecha_creacion DESC`
      );

      res.json({ pedidos: pedidos.rows, configuraciones: configuraciones.rows });
    } catch (error) {
      res.status(500).json({ error: "No se han podido leer los personalizados" });
    }
  });

  router.get("/api/trabajador/resumen", async function (req, res) {
    try {
      const resultado = await pool.query(
        `SELECT
           (SELECT COUNT(*) FROM public.pedidos WHERE estado = $1)::int AS "porPreparar",
           (SELECT COUNT(*) FROM public.pedidos WHERE estado = $2)::int AS "enPreparacion",
           (SELECT COUNT(*) FROM public.existencias WHERE cantidad < $3)::int AS "stockBajo",
           (SELECT COUNT(*) FROM public.pedidos WHERE fecha_pedido::date = CURRENT_DATE)::int AS "pedidosHoy"`,
        ["confirmado", "en_preparacion", 5]
      );
      res.json(resultado.rows[0]);
    } catch (error) {
      res.status(500).json({ error: "No se ha podido leer el resumen" });
    }
  });

  return router;
}

module.exports = crearRutasTrabajador;
