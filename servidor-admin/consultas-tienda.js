// consultas-tienda.js — el SQL de la tienda web.
//
// Dos tipos de sentencias:
//   - Lecturas: el catalogo (el mismo para todos) y los datos y pedidos del
//     cliente, siempre filtrados por el id del cliente que tiene la sesion.
//   - Llamadas a las funciones del script 20 (registrar_cliente,
//     crear_compra_web, ...). Son lo unico que escribe en la base.
// Aqui no se calcula ningun precio ni se toca el stock: lo hace PostgreSQL.
// Todas reciben "cliente", la conexion que abre bd.operarEnTienda.

// ---------------------------------------------------------------------
// Catalogo: los modelos a la venta, con sus colores, tallas y stock.
// El precio es precio_base + suplemento del color: lo que mostrara la ficha.
// El que se guarda en el pedido lo pone anadir_linea_pedido al crearlo.
// El stock es el de la nave que usan los pedidos (la primera, como en Java).
// ---------------------------------------------------------------------
async function catalogo(cliente) {
  const resultado = await cliente.query(`
    SELECT m.nombre AS modelo,
           v.color,
           m.precio_base + v.suplemento_precio AS precio,
           s.id_producto_sku AS sku,
           s.talla,
           COALESCE(e.cantidad, 0) AS stock
    FROM public.modelos m
    JOIN public.variantes v ON v.id_modelo = m.id_modelo
    JOIN public.producto_sku s ON s.id_variante = v.id_variante AND s.activo
    LEFT JOIN public.existencias e
           ON e.id_producto_sku = s.id_producto_sku
          AND e.id_nave = (SELECT min(id_nave) FROM public.nave)
    WHERE m.activo
    ORDER BY m.nombre, v.color, s.talla`);

  // Las filas llegan una por talla. Se agrupan: modelo -> colores -> tallas.
  const modelos = [];
  for (const fila of resultado.rows) {
    let modelo = modelos.at(-1);
    if (!modelo || modelo.nombre !== fila.modelo) {
      modelo = { nombre: fila.modelo, variantes: [] };
      modelos.push(modelo);
    }
    let variante = modelo.variantes.at(-1);
    if (!variante || variante.color !== fila.color) {
      variante = { color: fila.color, precio: fila.precio, tallas: [] };
      modelo.variantes.push(variante);
    }
    variante.tallas.push({ sku: fila.sku, talla: fila.talla, stock: fila.stock });
  }
  return modelos;
}

// ---------------------------------------------------------------------
// Cuentas
// ---------------------------------------------------------------------
async function registrar(cliente, nombre, email, contrasena, telefono, direccion) {
  const resultado = await cliente.query(
    'SELECT public.registrar_cliente($1, $2, $3, $4, $5) AS id',
    [nombre, email, contrasena, telefono || null, direccion || null]);
  return resultado.rows[0].id;
}

async function iniciarSesion(cliente, email, contrasena) {
  const resultado = await cliente.query(
    'SELECT public.iniciar_sesion_cliente($1, $2) AS id', [email, contrasena]);
  return resultado.rows[0].id;
}

// Los datos del cliente, o null si ya no existe o esta desactivado
async function datosCliente(cliente, idCliente) {
  const resultado = await cliente.query(`
    SELECT id_cliente AS id, nombre, email, telefono, direccion_entrega AS direccion
    FROM public.clientes
    WHERE id_cliente = $1 AND activo`, [idCliente]);
  return resultado.rows[0] || null;
}

// ---------------------------------------------------------------------
// Compras: siempre a traves de las funciones del script 20
// ---------------------------------------------------------------------
async function crearCompra(cliente, idCliente, referencia, skus, cantidades, telefono, direccion) {
  const resultado = await cliente.query(
    'SELECT public.crear_compra_web($1, $2, $3::int[], $4::int[], $5, $6) AS id',
    [idCliente, referencia, skus, cantidades, telefono || null, direccion]);
  return resultado.rows[0].id;
}

async function confirmarCompra(cliente, idCliente, idPedido) {
  await cliente.query('SELECT public.confirmar_compra_web($1, $2)', [idCliente, idPedido]);
}

async function cancelarCompra(cliente, idCliente, idPedido) {
  await cliente.query('SELECT public.cancelar_compra_web($1, $2)', [idCliente, idPedido]);
}

// ---------------------------------------------------------------------
// Historial: solo los pedidos de ESE cliente
// ---------------------------------------------------------------------
const COLUMNAS_PEDIDO = `
    id_pedido AS id,
    referencia,
    to_char(fecha_pedido, 'DD/MM/YYYY HH24:MI') AS fecha,
    estado,
    estado_pago AS "estadoPago",
    cantidad_total AS pares,
    importe_total AS total`;

async function pedidos(cliente, idCliente) {
  const resultado = await cliente.query(`
    SELECT ${COLUMNAS_PEDIDO}
    FROM public.pedidos
    WHERE id_cliente = $1
    ORDER BY fecha_pedido DESC, id_pedido DESC`, [idCliente]);
  return resultado.rows;
}

// Un pedido con sus lineas, o null si no existe o es de otro cliente
async function pedido(cliente, idCliente, idPedido) {
  const cabecera = await cliente.query(`
    SELECT ${COLUMNAS_PEDIDO}
    FROM public.pedidos
    WHERE id_pedido = $1 AND id_cliente = $2`, [idPedido, idCliente]);
  if (cabecera.rows.length === 0) return null;

  const lineas = await cliente.query(`
    SELECT m.nombre AS modelo, v.color, s.talla, l.cantidad,
           l.precio_unitario AS precio, l.subtotal
    FROM public.linea_pedido l
    JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
    JOIN public.variantes v ON v.id_variante = s.id_variante
    JOIN public.modelos m ON m.id_modelo = v.id_modelo
    WHERE l.id_pedido = $1
    ORDER BY l.id_linea`, [idPedido]);

  return { ...cabecera.rows[0], lineas: lineas.rows };
}

module.exports = {
  catalogo,
  registrar,
  iniciarSesion,
  datosCliente,
  crearCompra,
  confirmarCompra,
  cancelarCompra,
  pedidos,
  pedido
};
