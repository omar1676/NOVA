// rutas-trabajador.js — la API del portal del trabajador (Berme).
//
// Las monta servidor.js detras de soloTrabajador: antes de llegar aqui ya se
// ha comprobado, contra la base, que la sesion es de un trabajador activo.
// Todo pasa por la conexion de siempre (web_nova) con el rol
// portal_trabajador (script 23):
//   - las lecturas, en una transaccion de solo lectura (leer);
//   - los dos cambios, con las funciones avanzar_pedido_trabajador y
//     ajustar_existencias_trabajador, que vuelven a comprobar el usuario y
//     dejan el cambio en log_eventos a su nombre.
// El usuario sale siempre de la sesion, nunca de lo que mande el navegador.
const express = require("express");

const siguienteEstado = {
  confirmado: "en_preparacion",
  en_preparacion: "enviado",
  enviado: "entregado"
};

// Hasta 9 cifras: un numero mayor no cabe en un integer de PostgreSQL
function esEnteroPositivo(valor) {
  return /^[1-9][0-9]{0,8}$/.test(String(valor));
}

// Errores de las funciones del script 23 que se pueden ensenar tal cual
function errorConocido(error) {
  if (error.code !== "P0001") return null;
  const mensaje = error.message;
  if (mensaje === "Usuario no autorizado") {
    return [403, "Tu usuario no tiene permiso para el portal del trabajador"];
  }
  if (mensaje === "El pedido no existe" || mensaje === "No existe esa existencia") {
    return [404, mensaje];
  }
  if (mensaje.startsWith("Un pedido en estado") || mensaje.startsWith("Solo se puede pasar de")
      || mensaje.startsWith("La cantidad debe ser")) {
    return [400, mensaje];
  }
  return null;
}

function crearRutasTrabajador(bd, sesiones) {
  const router = express.Router();

  // Lecturas: solo lectura y con el rol portal_trabajador
  function leer(sql, parametros) {
    return bd.consultarComoTrabajador((cliente) => cliente.query(sql, parametros));
  }

  // Los cambios solo aceptan JSON, como los manda el portal
  function soloJson(req, res) {
    if (req.is("application/json")) return true;
    res.status(415).json({ error: "Los datos tienen que ir en JSON" });
    return false;
  }

  router.get("/api/trabajador/pedidos", async function (req, res) {
    try {
      const resultado = await leer(
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

  // Avanzar un paso el estado de un pedido. Las reglas (existe, solo un paso
  // adelante) las comprueba avanzar_pedido_trabajador en PostgreSQL, que
  // bloquea el pedido: con dos clics a la vez, el segundo ya ve el cambio.
  router.patch("/api/trabajador/pedidos/:id/estado", async function (req, res) {
    if (!soloJson(req, res)) return;
    const idPedido = req.params.id;
    const estadoNuevo = req.body ? req.body.estado : undefined;

    if (!esEnteroPositivo(idPedido)) {
      return res.status(400).json({ error: "Identificador de pedido no válido" });
    }

    if (!Object.values(siguienteEstado).includes(estadoNuevo)) {
      return res.status(400).json({ error: "Estado no válido" });
    }

    try {
      const idUsuario = sesiones.leerSesion(req).idUsuario;
      const cambio = await bd.cambiarComoTrabajador(
        "SELECT * FROM public.avanzar_pedido_trabajador($1, $2, $3)",
        [idUsuario, Number(idPedido), estadoNuevo]
      );

      res.json(cambio.rows[0]);
    } catch (error) {
      const conocido = errorConocido(error);
      if (conocido) return res.status(conocido[0]).json({ error: conocido[1] });
      res.status(500).json({ error: "No se ha podido cambiar el estado" });
    }
  });

  router.get("/api/trabajador/inventario", async function (req, res) {
    try {
      const resultado = await leer(
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

  // Cambiar la cantidad de un SKU en una nave, con ajustar_existencias_trabajador
  router.patch("/api/trabajador/inventario/:idSku/:idNave", async function (req, res) {
    if (!soloJson(req, res)) return;
    const idSku = req.params.idSku;
    const idNave = req.params.idNave;
    const cantidad = req.body ? req.body.cantidad : undefined;

    if (!esEnteroPositivo(idSku) || !esEnteroPositivo(idNave)) {
      return res.status(400).json({ error: "Identificadores no válidos" });
    }

    if (!Number.isInteger(cantidad) || cantidad < 0 || cantidad > 99999) {
      return res.status(400).json({ error: "La cantidad debe ser un número entero entre 0 y 99999" });
    }

    try {
      const idUsuario = sesiones.leerSesion(req).idUsuario;
      const cambio = await bd.cambiarComoTrabajador(
        "SELECT * FROM public.ajustar_existencias_trabajador($1, $2, $3, $4)",
        [idUsuario, Number(idSku), Number(idNave), cantidad]
      );

      res.json(cambio.rows[0]);
    } catch (error) {
      const conocido = errorConocido(error);
      if (conocido) return res.status(conocido[0]).json({ error: conocido[1] });
      res.status(500).json({ error: "No se ha podido guardar la cantidad" });
    }
  });

  router.get("/api/trabajador/personalizados", async function (req, res) {
    try {
      const pedidos = await leer(
        `SELECT p.id_pedido, p.referencia, c.nombre AS cliente, p.fecha_objetivo,
                p.estado, p.cantidad_total, p.personalizacion
         FROM public.pedidos p
         JOIN public.clientes c ON c.id_cliente = p.id_cliente
         WHERE p.personalizado = $1
         ORDER BY p.fecha_pedido DESC`,
        [true]
      );

      const configuraciones = await leer(
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
      const resultado = await leer(
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
