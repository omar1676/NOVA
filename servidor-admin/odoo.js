// odoo.js — conector de Berme con la API JSON-2 de Odoo (/json/2/<modelo>/<metodo>).
//
// DESACTIVADO mientras no se configure: hacen falta ODOO_URL, ODOO_DB y
// ODOO_API_KEY en .env. Sin ellas no se llama a ningun servidor (antes iba
// a http://localhost:8069 por defecto) y cualquier llamada falla con un
// aviso claro. Nunca se inventa una respuesta de Odoo.
// Desde este ordenador no se llega a ningun Odoo: nada de este archivo se
// ha probado contra uno de verdad.
const URL_ODOO = process.env.ODOO_URL;
const BD_ODOO = process.env.ODOO_DB;
const CLAVE_ODOO = process.env.ODOO_API_KEY;
const odooConfigurado = Boolean(URL_ODOO && BD_ODOO && CLAVE_ODOO);

// La linea que escribe el servidor al arrancar
function resumen() {
  return odooConfigurado
    ? `Conector de Odoo configurado (${URL_ODOO}, base ${BD_ODOO}): sin probar contra un Odoo real`
    : 'Conector de Odoo desactivado (faltan ODOO_URL, ODOO_DB y ODOO_API_KEY en .env): no se envía nada a Odoo';
}

async function llamar(modelo, metodo, cuerpo) {
  if (!odooConfigurado) {
    throw new Error('Conector de Odoo desactivado: faltan ODOO_URL, ODOO_DB y ODOO_API_KEY');
  }
  const respuesta = await fetch(`${URL_ODOO}/json/2/${modelo}/${metodo}`, {
    method: 'POST',
    headers: {
      Authorization: `bearer ${CLAVE_ODOO}`,
      'X-Odoo-Database': BD_ODOO,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(cuerpo),
    signal: AbortSignal.timeout(15000),
  });
  const texto = await respuesta.text();
  if (!respuesta.ok) throw new Error(`Odoo ${modelo}.${metodo} ${respuesta.status}: ${texto}`);
  return texto ? JSON.parse(texto) : null;
}

async function buscarOCrearCliente(cliente) {
  const existentes = await llamar('res.partner', 'search_read', {
    domain: [['email', '=', cliente.email]],
    fields: ['id'],
    limit: 1,
  });
  if (existentes.length) return existentes[0].id;
  const creados = await llamar('res.partner', 'create', {
    vals_list: [{
      name: cliente.nombre,
      email: cliente.email,
      is_company: cliente.tipo === 'empresa',
    }],
  });
  return creados[0];
}

async function productosPorSku(skus) {
  const productos = await llamar('product.product', 'search_read', {
    domain: [['default_code', 'in', skus]],
    fields: ['id', 'default_code'],
  });
  const mapa = new Map(productos.map((p) => [p.default_code, p.id]));
  const faltan = skus.filter((sku) => !mapa.has(sku));
  if (faltan.length) throw new Error(`SKU sin producto en Odoo: ${faltan.join(', ')}`);
  return mapa;
}

async function crearPedidoOdoo({ referencia, cliente, lineas, personalizacion }) {
  const existente = await llamar('sale.order', 'search_read', {
    domain: [['client_order_ref', '=', referencia]],
    fields: ['id', 'name', 'state', 'amount_untaxed'],
    limit: 1,
  });
  if (existente.length) return { ...existente[0], yaExistia: true };

  const idCliente = await buscarOCrearCliente(cliente);
  const productos = await productosPorSku(lineas.map((l) => l.sku));

  const creados = await llamar('sale.order', 'create', {
    vals_list: [{
      partner_id: idCliente,
      client_order_ref: referencia,
      note: personalizacion || false,
      order_line: lineas.map((l) => [0, 0, {
        product_id: productos.get(l.sku),
        product_uom_qty: l.cantidad,
        price_unit: l.precio_unitario,
      }]),
    }],
  });
  const idPedido = creados[0];
  await llamar('sale.order', 'action_confirm', { ids: [idPedido] });

  const pedido = await llamar('sale.order', 'read', {
    ids: [idPedido],
    fields: ['id', 'name', 'state', 'amount_untaxed'],
  });
  return { ...pedido[0], yaExistia: false };
}

module.exports = { crearPedidoOdoo, odooConfigurado, resumen };
