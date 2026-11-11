// consultas.js — las consultas SQL del panel de administracion.
//
// Todas son de SOLO LECTURA: bd.consultarSoloLectura las ejecuta dentro de
// BEGIN ... READ ONLY y con el rol panel_lectura (script 19), que solo puede
// leer las tablas y columnas que aparecen aqui.
//
// Salen de las que ya tenia el proyecto, para que el panel, Java y los
// informes den las mismas cifras:
//   - 02_Acceso_Datos/sql/12_consultas_panel.sql: C5 (filtros), C8 (stock bajo),
//     P-A (ventas), P-B (pedidos por estado) y P-C (modelos mas solicitados).
//   - PedidoDAO.verAuditoria (Java): la auditoria.
//
// Ninguna recalcula los totales de los pedidos ni el stock: importe_total,
// cantidad_total y existencias los mantienen los triggers de PostgreSQL.
// Solo se suman o se promedian para mostrarlos (ventas, ticket medio).
//
// Los filtros van siempre como parametros ($1, $2...), nunca pegados al SQL.
// Un filtro vacio ('') no excluye nada, igual que en C5.

// Stock bajo: MENOS de 10 unidades, como C8 y el panel de indicadores de Java.
const UMBRAL_STOCK_BAJO = 10;

// Valores que se aceptan en los filtros (los de los CHECK y los triggers)
const ESTADOS_PEDIDO = ['pendiente', 'confirmado', 'en_preparacion', 'enviado', 'entregado', 'cancelado'];
const ESTADOS_ACTIVO = ['activo', 'inactivo'];
const ESTADOS_STOCK = ['suficiente', 'bajo', 'agotado'];
const ACCIONES_AUDITORIA = ['ALTA', 'CAMBIO_ESTADO', 'CAMBIO_STOCK', 'BAJA_LOGICA']; // 08_auditoria.sql

// ---------------------------------------------------------------------
// Consultas que usan varias rutas
// ---------------------------------------------------------------------

// P-B: pedidos por estado
const SQL_PEDIDOS_POR_ESTADO = `
  SELECT estado,
         count(*) AS pedidos,
         COALESCE(sum(cantidad_total), 0) AS pares,
         COALESCE(sum(importe_total), 0) AS importe
  FROM public.pedidos
  GROUP BY estado
  ORDER BY pedidos DESC, estado`;

// Ventas de los ultimos 30 dias. Igual que P-A, los cancelados no cuentan.
const SQL_VENTAS_POR_DIA = `
  SELECT to_char(fecha_pedido::date, 'DD/MM') AS dia,
         sum(importe_total) AS total
  FROM public.pedidos
  WHERE estado <> 'cancelado'
    AND fecha_pedido >= current_date - 29
  GROUP BY fecha_pedido::date
  ORDER BY fecha_pedido::date`;

// C8: referencias con menos stock que el umbral, sumando todas las naves
const SQL_STOCK_BAJO = `
  SELECT m.nombre AS modelo,
         v.color,
         s.talla,
         s.sku,
         COALESCE(SUM(e.cantidad), 0) AS stock
  FROM public.producto_sku s
  JOIN public.variantes v ON v.id_variante = s.id_variante
  JOIN public.modelos m ON m.id_modelo = v.id_modelo
  LEFT JOIN public.existencias e ON e.id_producto_sku = s.id_producto_sku
  GROUP BY m.nombre, v.color, s.talla, s.sku
  HAVING COALESCE(SUM(e.cantidad), 0) < $1
  ORDER BY stock, m.nombre`;

// ---------------------------------------------------------------------
// 1. Dashboard
// ---------------------------------------------------------------------
async function dashboard(cliente) {
  // P-A: importe de las ventas (todo menos los cancelados)
  const ventas = await cliente.query(`
    SELECT COALESCE(sum(importe_total), 0) AS importe
    FROM public.pedidos
    WHERE estado <> 'cancelado'`);

  // Pedidos que han entrado hoy, en cualquier estado
  const hoy = await cliente.query(`
    SELECT count(*) AS pedidos
    FROM public.pedidos
    WHERE fecha_pedido::date = current_date`);

  const ultimos = await cliente.query(`
    SELECT p.referencia,
           c.nombre AS cliente,
           to_char(p.fecha_pedido, 'DD/MM/YYYY') AS fecha,
           p.estado,
           p.importe_total AS total
    FROM public.pedidos p
    JOIN public.clientes c ON c.id_cliente = p.id_cliente
    ORDER BY p.fecha_pedido DESC, p.id_pedido DESC
    LIMIT 5`);

  const porEstado = await cliente.query(SQL_PEDIDOS_POR_ESTADO);
  const ventasDia = await cliente.query(SQL_VENTAS_POR_DIA);
  const stockBajo = await cliente.query(SQL_STOCK_BAJO, [UMBRAL_STOCK_BAJO]);

  const pendientes = porEstado.rows.find((fila) => fila.estado === 'pendiente');

  return {
    ventas: ventas.rows[0].importe,
    pedidosHoy: hoy.rows[0].pedidos,
    pedidosPendientes: pendientes ? pendientes.pedidos : 0,
    sugerenciasPendientes: null, // no hay tabla de sugerencias: "no disponible"
    ultimosPedidos: ultimos.rows,
    pedidosPorEstado: porEstado.rows,
    ventasDia: ventasDia.rows,
    stockBajo: stockBajo.rows,
    umbralStockBajo: UMBRAL_STOCK_BAJO
  };
}

// ---------------------------------------------------------------------
// 2. Pedidos (C5: estado y texto; un filtro vacio no excluye nada)
//    El id lo usa el boton "Marcar en reparto" (POST /api/admin/pedidos/:id/reparto).
// ---------------------------------------------------------------------
const COLUMNAS_PEDIDO = `
    p.id_pedido AS id,
    p.referencia,
    c.nombre AS cliente,
    to_char(p.fecha_pedido, 'DD/MM/YYYY') AS fecha,
    p.estado,
    p.importe_total AS total`;

async function pedidos(cliente, estado, texto) {
  const resultado = await cliente.query(`
    SELECT ${COLUMNAS_PEDIDO}
    FROM public.pedidos p
    JOIN public.clientes c ON c.id_cliente = p.id_cliente
    WHERE ($1::text = '' OR p.estado = $1)
      AND ($2::text = '' OR p.referencia ILIKE '%' || $2 || '%'
                         OR c.nombre ILIKE '%' || $2 || '%')
    ORDER BY p.fecha_pedido DESC, p.id_pedido DESC`, [estado, texto]);
  return { filas: resultado.rows };
}

// Un pedido con las mismas columnas que la lista (o null si no existe):
// lo que devuelve la ruta de reparto despues del cambio
async function pedido(cliente, idPedido) {
  const resultado = await cliente.query(`
    SELECT ${COLUMNAS_PEDIDO}
    FROM public.pedidos p
    JOIN public.clientes c ON c.id_cliente = p.id_cliente
    WHERE p.id_pedido = $1`, [idPedido]);
  return resultado.rows[0] || null;
}

// ---------------------------------------------------------------------
// 3. Productos: un SKU por fila. Se sigue a anadir_linea_pedido (02_funciones.sql):
//    - precio = precio_base del modelo + suplemento_precio del color (aqui solo se ve);
//    - un SKU solo se puede vender si el SKU y su modelo estan activos.
// ---------------------------------------------------------------------
async function productos(cliente, estado, texto) {
  const resultado = await cliente.query(`
    SELECT *
    FROM (
        SELECT m.nombre AS modelo,
               v.color,
               s.talla,
               s.sku,
               m.precio_base + v.suplemento_precio AS precio,
               CASE WHEN s.activo AND m.activo THEN 'activo' ELSE 'inactivo' END AS estado
        FROM public.producto_sku s
        JOIN public.variantes v ON v.id_variante = s.id_variante
        JOIN public.modelos m ON m.id_modelo = v.id_modelo
    ) AS productos
    WHERE ($1::text = '' OR estado = $1)
      AND ($2::text = '' OR modelo ILIKE '%' || $2 || '%'
                         OR color ILIKE '%' || $2 || '%'
                         OR sku ILIKE '%' || $2 || '%')
    ORDER BY modelo, color, talla`, [estado, texto]);
  return { filas: resultado.rows };
}

// ---------------------------------------------------------------------
// 4. Inventario: una fila por SKU y nave.
//    Un SKU sin fila en existencias cuenta como 0, igual que en C8.
//    agotado = 0 · bajo = menos de 10 · suficiente = 10 o mas
// ---------------------------------------------------------------------
async function inventario(cliente, estado, texto) {
  const resultado = await cliente.query(`
    SELECT *
    FROM (
        SELECT n.nombre AS nave,
               m.nombre AS modelo,
               v.color,
               s.talla,
               s.sku,
               COALESCE(e.cantidad, 0) AS stock,
               CASE WHEN COALESCE(e.cantidad, 0) = 0 THEN 'agotado'
                    WHEN COALESCE(e.cantidad, 0) < $1 THEN 'bajo'
                    ELSE 'suficiente' END AS estado
        FROM public.producto_sku s
        JOIN public.variantes v ON v.id_variante = s.id_variante
        JOIN public.modelos m ON m.id_modelo = v.id_modelo
        LEFT JOIN public.existencias e ON e.id_producto_sku = s.id_producto_sku
        LEFT JOIN public.nave n ON n.id_nave = e.id_nave
    ) AS inventario
    WHERE ($2::text = '' OR estado = $2)
      AND ($3::text = '' OR nave ILIKE '%' || $3 || '%'
                         OR modelo ILIKE '%' || $3 || '%'
                         OR color ILIKE '%' || $3 || '%'
                         OR sku ILIKE '%' || $3 || '%'
                         OR talla::text = $3)
    ORDER BY modelo, color, talla, nave`, [UMBRAL_STOCK_BAJO, estado, texto]);
  return { umbralStockBajo: UMBRAL_STOCK_BAJO, filas: resultado.rows };
}

// ---------------------------------------------------------------------
// 5. Clientes. Sin la direccion de entrega: el panel no la usa.
// ---------------------------------------------------------------------
async function clientes(cliente, estado, texto) {
  const resultado = await cliente.query(`
    SELECT *
    FROM (
        SELECT nombre,
               tipo,
               email AS correo,
               telefono,
               CASE WHEN activo THEN 'activo' ELSE 'inactivo' END AS estado
        FROM public.clientes
    ) AS clientes
    WHERE ($1::text = '' OR estado = $1)
      AND ($2::text = '' OR nombre ILIKE '%' || $2 || '%'
                         OR correo ILIKE '%' || $2 || '%'
                         OR telefono ILIKE '%' || $2 || '%')
    ORDER BY nombre`, [estado, texto]);
  return { filas: resultado.rows };
}

// ---------------------------------------------------------------------
// 6. Trabajadores: el personal y las cuentas de usuario.
//    FULL JOIN para que salgan tambien las cuentas sin ficha de personal
//    (las que crea crear_usuario) y el personal sin cuenta.
//    Nunca el DNI. panel_lectura no puede leer ni personal.dni ni
//    usuarios.password_hash (script 19).
// ---------------------------------------------------------------------
async function trabajadores(cliente, estado, texto) {
  const resultado = await cliente.query(`
    SELECT *
    FROM (
        SELECT p.nombre,
               u.username AS usuario,
               p.puesto,
               r.nombre AS rol,
               CASE WHEN u.id_usuario IS NULL THEN 'sin cuenta'
                    WHEN u.activo THEN 'activo'
                    ELSE 'inactivo' END AS estado
        FROM public.personal p
        FULL JOIN public.usuarios u ON u.id_personal = p.id_personal
        LEFT JOIN public.roles r ON r.id_rol = u.id_rol
    ) AS trabajadores
    WHERE ($1::text = '' OR estado = $1)
      AND ($2::text = '' OR nombre ILIKE '%' || $2 || '%'
                         OR usuario ILIKE '%' || $2 || '%'
                         OR puesto ILIKE '%' || $2 || '%')
    ORDER BY nombre, usuario`, [estado, texto]);
  return { filas: resultado.rows };
}

// ---------------------------------------------------------------------
// 7. Auditoria: la misma consulta que PedidoDAO.verAuditoria (Java),
//    con las acciones tal como las guardan los triggers de 08_auditoria.sql.
// ---------------------------------------------------------------------
const LIMITE_AUDITORIA = 100;

async function auditoria(cliente, accion, texto) {
  const resultado = await cliente.query(`
    SELECT to_char(e.fecha_hora, 'DD/MM/YYYY HH24:MI') AS fecha,
           COALESCE(u.username, '(sin sesión)') AS usuario,
           e.accion,
           e.tabla_afectada AS tabla,
           e.id_registro AS registro,
           e.detalle
    FROM public.log_eventos e
    LEFT JOIN public.usuarios u ON u.id_usuario = e.id_usuario
    WHERE ($1::text = '' OR e.accion = $1)
      AND ($2::text = '' OR u.username ILIKE '%' || $2 || '%'
                         OR e.tabla_afectada ILIKE '%' || $2 || '%'
                         OR e.detalle ILIKE '%' || $2 || '%')
    ORDER BY e.id_evento DESC
    LIMIT $3`, [accion, texto, LIMITE_AUDITORIA]);
  return { limite: LIMITE_AUDITORIA, filas: resultado.rows };
}

// ---------------------------------------------------------------------
// 8. Estadisticas. Mismo criterio que P-A: los cancelados no son ventas.
// ---------------------------------------------------------------------
async function estadisticas(cliente) {
  const mes = await cliente.query(`
    SELECT to_char(current_date, 'MM/YYYY') AS mes,
           COALESCE(sum(importe_total), 0) AS ingresos,
           count(*) AS pedidos,
           COALESCE(round(sum(importe_total) / NULLIF(count(*), 0), 2), 0) AS ticket_medio,
           COALESCE(sum(cantidad_total), 0) AS pares
    FROM public.pedidos
    WHERE estado <> 'cancelado'
      AND date_trunc('month', fecha_pedido) = date_trunc('month', current_date)`);

  const ingresosPorMes = await cliente.query(`
    SELECT to_char(date_trunc('month', fecha_pedido), 'MM/YYYY') AS mes,
           sum(importe_total) AS total
    FROM public.pedidos
    WHERE estado <> 'cancelado'
    GROUP BY date_trunc('month', fecha_pedido)
    ORDER BY date_trunc('month', fecha_pedido)`);

  // P-C: modelos mas solicitados (las lineas X-NOVA no tienen SKU).
  // Se ordena tambien por modelo para que los empates salgan siempre igual.
  const masVendidos = await cliente.query(`
    SELECT COALESCE(m.nombre, 'X-NOVA') AS modelo,
           SUM(l.cantidad) AS pares,
           COUNT(DISTINCT l.id_pedido) AS pedidos
    FROM public.linea_pedido l
    JOIN public.pedidos p ON p.id_pedido = l.id_pedido
    LEFT JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
    LEFT JOIN public.variantes v ON v.id_variante = s.id_variante
    LEFT JOIN public.modelos m ON m.id_modelo = v.id_modelo
    WHERE p.estado <> 'cancelado'
    GROUP BY COALESCE(m.nombre, 'X-NOVA')
    ORDER BY pares DESC, modelo`);

  const porEstado = await cliente.query(SQL_PEDIDOS_POR_ESTADO);
  const ventasDia = await cliente.query(SQL_VENTAS_POR_DIA);

  return {
    mes: mes.rows[0].mes,
    ingresosMes: mes.rows[0].ingresos,
    pedidosMes: mes.rows[0].pedidos,
    ticketMedio: mes.rows[0].ticket_medio,
    paresMes: mes.rows[0].pares,
    ventasDia: ventasDia.rows,
    ingresosPorMes: ingresosPorMes.rows,
    pedidosPorEstado: porEstado.rows,
    masVendidos: masVendidos.rows
  };
}

module.exports = {
  UMBRAL_STOCK_BAJO,
  ESTADOS_PEDIDO,
  ESTADOS_ACTIVO,
  ESTADOS_STOCK,
  ACCIONES_AUDITORIA,
  dashboard,
  pedidos,
  pedido,
  productos,
  inventario,
  clientes,
  trabajadores,
  auditoria,
  estadisticas
};
