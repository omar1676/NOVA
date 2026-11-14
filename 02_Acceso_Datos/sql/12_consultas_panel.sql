\echo '===== CONSULTAS PARAMETRIZADAS Y PANEL DE INDICADORES ====='
\echo ''
\echo 'Consultas parametrizadas C1 a C8 y panel de indicadores. Aqui los'
\echo 'parametros se ponen con variables de psql para poder probarlas; desde'
\echo 'un programa, cada valor va como parametro, nunca pegado al texto.'
\echo ''

\set cliente_buscado 'ferrer'
\set modelo_buscado 'Velocity'
\set estado_buscado 'pendiente'
\set fecha_desde '2026-01-01'
\set fecha_hasta '2026-12-31'
\set umbral_stock 10

\echo '--- C1 buscar pedidos por nombre o correo de cliente'
SELECT
    p.referencia,
    c.nombre AS cliente,
    p.fecha_pedido::date AS fecha,
    p.estado,
    p.cantidad_total AS pares,
    p.importe_total AS importe
FROM public.pedidos p
JOIN public.clientes c ON c.id_cliente = p.id_cliente
WHERE (c.nombre ILIKE '%' || :'cliente_buscado' || '%'
       OR c.email ILIKE '%' || :'cliente_buscado' || '%')
ORDER BY p.fecha_pedido DESC;

\echo ''
\echo '--- C2 buscar pedidos por modelo'
SELECT
    p.referencia,
    c.nombre AS cliente,
    m.nombre AS modelo,
    s.talla,
    l.cantidad AS pares,
    l.subtotal
FROM public.pedidos p
JOIN public.clientes c ON c.id_cliente = p.id_cliente
JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido
JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
JOIN public.variantes v ON v.id_variante = s.id_variante
JOIN public.modelos m ON m.id_modelo = v.id_modelo
WHERE m.nombre ILIKE '%' || :'modelo_buscado' || '%'
ORDER BY p.referencia, s.talla;

\echo ''
\echo '--- C3 buscar pedidos por estado'
SELECT
    p.referencia,
    c.nombre AS cliente,
    p.estado,
    p.estado_pago,
    p.importe_total AS importe
FROM public.pedidos p
JOIN public.clientes c ON c.id_cliente = p.id_cliente
WHERE p.estado = :'estado_buscado'
ORDER BY p.referencia;

\echo ''
\echo '--- C4 buscar pedidos por periodo'
SELECT
    p.referencia,
    p.fecha_pedido::date AS fecha,
    c.nombre AS cliente,
    p.importe_total AS importe
FROM public.pedidos p
JOIN public.clientes c ON c.id_cliente = p.id_cliente
WHERE p.fecha_pedido::date BETWEEN :'fecha_desde'::date AND :'fecha_hasta'::date
ORDER BY p.fecha_pedido;

\echo ''
\echo '--- C5 los tres filtros combinados: cliente, estado y periodo'
\echo '    (un filtro vacio no debe excluir filas, de ahi los OR con NULL)'
\set cliente_filtro 'club'
\set estado_filtro 'pendiente'
SELECT
    p.referencia,
    c.nombre AS cliente,
    p.estado,
    p.fecha_pedido::date AS fecha,
    p.cantidad_total AS pares,
    p.importe_total AS importe
FROM public.pedidos p
JOIN public.clientes c ON c.id_cliente = p.id_cliente
WHERE (:'cliente_filtro' = '' OR c.nombre ILIKE '%' || :'cliente_filtro' || '%')
  AND (:'estado_filtro' = '' OR p.estado = :'estado_filtro')
  AND p.fecha_pedido::date BETWEEN :'fecha_desde'::date AND :'fecha_hasta'::date
ORDER BY p.fecha_pedido DESC;

\echo ''
\echo '--- C6 el mismo filtro combinado sin ningun valor: debe devolver todo'
\set cliente_filtro ''
\set estado_filtro ''
SELECT count(*) AS pedidos_sin_filtrar
FROM public.pedidos p
JOIN public.clientes c ON c.id_cliente = p.id_cliente
WHERE (:'cliente_filtro' = '' OR c.nombre ILIKE '%' || :'cliente_filtro' || '%')
  AND (:'estado_filtro' = '' OR p.estado = :'estado_filtro')
  AND p.fecha_pedido::date BETWEEN :'fecha_desde'::date AND :'fecha_hasta'::date;

\echo ''
\echo '--- C7 un filtro que no encuentra nada: la consulta devuelve cero filas'
SELECT count(*) AS resultados
FROM public.pedidos p
JOIN public.clientes c ON c.id_cliente = p.id_cliente
WHERE c.nombre ILIKE '%no-existe-este-cliente%';

\echo ''
\echo '--- C8 stock bajo con umbral configurable'
SELECT
    m.nombre AS modelo,
    v.color,
    s.talla,
    s.sku,
    COALESCE(SUM(e.cantidad), 0) AS stock
FROM public.producto_sku s
JOIN public.variantes v ON v.id_variante = s.id_variante
JOIN public.modelos m ON m.id_modelo = v.id_modelo
LEFT JOIN public.existencias e ON e.id_producto_sku = s.id_producto_sku
GROUP BY m.nombre, v.color, s.talla, s.sku
HAVING COALESCE(SUM(e.cantidad), 0) < :umbral_stock
ORDER BY stock, m.nombre, v.color, s.talla;

\echo ''
\echo '===== PANEL DE INDICADORES ====='

\echo ''
\echo '--- P-A numero de pedidos, pares solicitados e importe de ventas'
SELECT
    count(*) AS pedidos,
    COALESCE(sum(cantidad_total), 0) AS pares_solicitados,
    COALESCE(sum(importe_total), 0) AS importe_ventas
FROM public.pedidos
WHERE estado <> 'cancelado';

\echo ''
\echo '--- P-B pedidos por estado'
SELECT
    estado,
    count(*) AS pedidos,
    COALESCE(sum(cantidad_total), 0) AS pares,
    COALESCE(sum(importe_total), 0) AS importe
FROM public.pedidos
GROUP BY estado
ORDER BY pedidos DESC, estado;

\echo ''
\echo '--- P-C modelos mas solicitados'
SELECT
    COALESCE(m.nombre, 'X-NOVA') AS modelo,
    SUM(l.cantidad) AS pares,
    COUNT(DISTINCT l.id_pedido) AS pedidos
FROM public.linea_pedido l
JOIN public.pedidos p ON p.id_pedido = l.id_pedido
LEFT JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
LEFT JOIN public.variantes v ON v.id_variante = s.id_variante
LEFT JOIN public.modelos m ON m.id_modelo = v.id_modelo
WHERE p.estado <> 'cancelado'
GROUP BY COALESCE(m.nombre, 'X-NOVA')
ORDER BY pares DESC, modelo;

\echo ''
\echo '--- P-D distribucion por tallas, sin contar los cancelados'
SELECT
    COALESCE(s.talla, x.talla_referencia) AS talla,
    SUM(l.cantidad) AS pares,
    COUNT(DISTINCT l.id_pedido) AS pedidos
FROM public.linea_pedido l
JOIN public.pedidos p ON p.id_pedido = l.id_pedido
LEFT JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
LEFT JOIN public.configuraciones_xnova x ON x.id_configuracion = l.id_configuracion_xnova
WHERE p.estado <> 'cancelado'
GROUP BY COALESCE(s.talla, x.talla_referencia)
ORDER BY pares DESC, talla;

\echo ''
\echo '--- P-E numero de referencias por debajo del umbral'
SELECT
    count(*) AS referencias_bajo_umbral,
    :umbral_stock AS umbral
FROM (
    SELECT s.id_producto_sku, COALESCE(SUM(e.cantidad), 0) AS stock
    FROM public.producto_sku s
    LEFT JOIN public.existencias e ON e.id_producto_sku = s.id_producto_sku
    GROUP BY s.id_producto_sku
    HAVING COALESCE(SUM(e.cantidad), 0) < :umbral_stock
) AS bajo;

\echo ''
\echo '--- P-F fabricacion personalizada para PSP, filtrada por referencia'
\set referencia_psp 'NOVA-0011'
SELECT
    p.referencia,
    c.nombre AS cliente,
    m.nombre AS modelo,
    p.personalizacion,
    s.talla,
    l.cantidad
FROM public.pedidos p
JOIN public.clientes c ON c.id_cliente = p.id_cliente
JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido
JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
JOIN public.variantes v ON v.id_variante = s.id_variante
JOIN public.modelos m ON m.id_modelo = v.id_modelo
WHERE p.personalizado = true
  AND p.referencia = :'referencia_psp'
ORDER BY s.talla;

\echo ''
\echo '--- P-G comprobacion de coherencia: los totales del panel cuadran con las lineas'
SELECT
    CASE WHEN panel_pares = lineas_pares AND panel_importe = lineas_importe
         THEN 'PASS' ELSE 'FAIL' END AS coherencia,
    panel_pares, lineas_pares, panel_importe, lineas_importe
FROM (
    SELECT
        (SELECT COALESCE(sum(cantidad_total), 0) FROM public.pedidos
          WHERE estado <> 'cancelado') AS panel_pares,
        (SELECT COALESCE(sum(importe_total), 0) FROM public.pedidos
          WHERE estado <> 'cancelado') AS panel_importe,
        (SELECT COALESCE(sum(l.cantidad), 0) FROM public.linea_pedido l
           JOIN public.pedidos p ON p.id_pedido = l.id_pedido
          WHERE p.estado <> 'cancelado') AS lineas_pares,
        (SELECT COALESCE(sum(l.subtotal), 0) FROM public.linea_pedido l
           JOIN public.pedidos p ON p.id_pedido = l.id_pedido
          WHERE p.estado <> 'cancelado') AS lineas_importe
) AS t;

\echo ''
\echo '--- P-H datos para el fichero usuarios_sneaker.json'
\echo '    Son exactamente los campos que pide el enunciado. No sale ningun'
\echo '    hash ni nada parecido a una credencial.'
SELECT
    u.id_usuario,
    u.username,
    r.nombre AS rol,
    u.activo
FROM public.usuarios u
JOIN public.roles r ON r.id_rol = u.id_rol
ORDER BY u.id_usuario;

\echo ''
\echo '===== CASO N: CONTRASTE CON PYTHON ====='
\echo 'Tres cifras que Python vuelve a calcular con pandas. Se usan los mismos'
\echo 'criterios que el dashboard: venta = confirmado en adelante; demanda ='
\echo 'pedidos no cancelados. Su resultado, con psql --csv, va a'
\echo '04_Python/entrada_acc/conciliacion_sql/ (N-1.csv, N-2.csv y N-3.csv).'

\set mes_contraste '2026-11'

\echo ''
\echo '--- N-1 ingresos de un mes: pedidos, pares e importe de venta del mes'
SELECT
    :'mes_contraste' AS anio_mes,
    count(*) AS pedidos,
    COALESCE(sum(cantidad_total), 0) AS pares,
    COALESCE(sum(importe_total), 0) AS importe
FROM public.pedidos
WHERE estado IN ('confirmado', 'en_preparacion', 'enviado', 'entregado')
  AND to_char(fecha_pedido, 'YYYY-MM') = :'mes_contraste';

\echo ''
\echo '--- N-2 matriz talla x modelo: pares de los pedidos no cancelados'
SELECT
    COALESCE(m.nombre, 'X-NOVA') AS modelo,
    COALESCE(s.talla, x.talla_referencia) AS talla,
    SUM(l.cantidad) AS pares
FROM public.linea_pedido l
JOIN public.pedidos p ON p.id_pedido = l.id_pedido
LEFT JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
LEFT JOIN public.variantes v ON v.id_variante = s.id_variante
LEFT JOIN public.modelos m ON m.id_modelo = v.id_modelo
LEFT JOIN public.configuraciones_xnova x ON x.id_configuracion = l.id_configuracion_xnova
WHERE p.estado <> 'cancelado'
GROUP BY COALESCE(m.nombre, 'X-NOVA'), COALESCE(s.talla, x.talla_referencia)
ORDER BY modelo, talla;

\echo ''
\echo '--- N-3 clientes unicos: con algun pedido, con demanda y con venta'
SELECT
    count(DISTINCT id_cliente) AS clientes_con_pedidos,
    count(DISTINCT id_cliente) FILTER (WHERE estado <> 'cancelado') AS clientes_con_demanda,
    count(DISTINCT id_cliente) FILTER (
        WHERE estado IN ('confirmado', 'en_preparacion', 'enviado', 'entregado')) AS clientes_con_venta
FROM public.pedidos;

\echo ''
\echo '===== FIN DE LAS CONSULTAS DEL PANEL ====='
