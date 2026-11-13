-- Consulta 1. Ventas por modelo: unidades e importe, con X-NOVA y sin los pedidos cancelados.
SELECT
    COALESCE(m.nombre, 'X-NOVA') AS modelo,
    SUM(l.cantidad) AS unidades,
    SUM(l.subtotal) AS importe_total
FROM public.pedidos p
JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido
LEFT JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
LEFT JOIN public.variantes v ON v.id_variante = s.id_variante
LEFT JOIN public.modelos m ON m.id_modelo = v.id_modelo
WHERE p.estado <> 'cancelado'
GROUP BY COALESCE(m.nombre, 'X-NOVA')
ORDER BY importe_total DESC;


-- Consulta 2. Ranking de clientes: pedidos e importe sin cancelados, incluidos los que no han comprado.
SELECT
    c.nombre,
    c.email,
    COUNT(p.id_pedido) AS pedidos,
    COALESCE(SUM(p.importe_total), 0) AS importe_acumulado
FROM public.clientes c
LEFT JOIN public.pedidos p
    ON p.id_cliente = c.id_cliente
   AND p.estado <> 'cancelado'
GROUP BY c.id_cliente, c.nombre, c.email
ORDER BY importe_acumulado DESC;



-- Consulta 3 (HAVING). Pregunta: que referencias se quedaran con menos de
-- 10 pares cuando se sirvan los pedidos pendientes? Son las que hay que
-- reponer antes de confirmarlos, porque el stock baja al confirmar. HAVING
-- filtra despues de sumar las existencias de todas las naves.
SELECT
    m.nombre AS modelo,
    v.color,
    s.talla,
    s.sku,
    COALESCE(SUM(e.cantidad), 0) AS stock,
    COALESCE(pendiente.pares, 0) AS pares_pendientes,
    COALESCE(SUM(e.cantidad), 0) - COALESCE(pendiente.pares, 0) AS stock_previsto
FROM public.producto_sku s
JOIN public.variantes v ON v.id_variante = s.id_variante
JOIN public.modelos m ON m.id_modelo = v.id_modelo
LEFT JOIN public.existencias e ON e.id_producto_sku = s.id_producto_sku
LEFT JOIN (
    SELECT l.id_producto_sku, SUM(l.cantidad) AS pares
    FROM public.linea_pedido l
    JOIN public.pedidos p ON p.id_pedido = l.id_pedido
    WHERE p.estado = 'pendiente'
    GROUP BY l.id_producto_sku
) AS pendiente ON pendiente.id_producto_sku = s.id_producto_sku
GROUP BY m.nombre, v.color, s.talla, s.sku, pendiente.pares
HAVING COALESCE(SUM(e.cantidad), 0) - COALESCE(pendiente.pares, 0) < 10
ORDER BY stock_previsto ASC, m.nombre;


-- Consulta 4. Pedidos personalizados, incluidos los X-NOVA.
SELECT
    p.referencia,
    c.nombre AS cliente,
    p.fecha_pedido,
    p.personalizacion,
    p.estado,
    p.importe_total
FROM public.pedidos p
JOIN public.clientes c ON c.id_cliente = p.id_cliente
WHERE p.personalizado = true
ORDER BY p.fecha_pedido DESC;


-- Consulta 5. Inventario por almacen: productos distintos y pares disponibles de cada nave.
SELECT
    n.nombre AS almacen,
    n.ubicacion,
    COUNT(DISTINCT e.id_producto_sku) AS productos_diferentes,
    COALESCE(SUM(e.cantidad), 0) AS pares_disponibles,
    n.capacidad
FROM public.nave n
LEFT JOIN public.existencias e ON e.id_nave = n.id_nave
GROUP BY n.id_nave, n.nombre, n.ubicacion, n.capacidad
ORDER BY pares_disponibles DESC;


-- Consulta 6. Tallas mas pedidas, con la talla de referencia de los X-NOVA.
SELECT
    COALESCE(s.talla, x.talla_referencia) AS talla,
    SUM(l.cantidad) AS pares_pedidos,
    COUNT(DISTINCT l.id_pedido) AS pedidos_diferentes
FROM public.linea_pedido l
LEFT JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
LEFT JOIN public.configuraciones_xnova x ON x.id_configuracion = l.id_configuracion_xnova
GROUP BY COALESCE(s.talla, x.talla_referencia)
ORDER BY pares_pedidos DESC, talla;


-- Consulta 7. Pedidos por mes: numero, importe y cuantos son personalizados.
SELECT
    DATE_TRUNC('month', p.fecha_pedido)::date AS mes,
    COUNT(*) AS numero_pedidos,
    COALESCE(SUM(p.importe_total), 0) AS importe_pedidos,
    COUNT(*) FILTER (WHERE p.personalizado = true) AS personalizados
FROM public.pedidos p
GROUP BY DATE_TRUNC('month', p.fecha_pedido)
ORDER BY mes DESC;


-- Consulta 8. Resumen de pagos: pedidos, importe y pares por estado de pago.
SELECT
    p.estado_pago,
    COUNT(*) AS numero_pedidos,
    COALESCE(SUM(p.importe_total), 0) AS importe_total,
    COALESCE(SUM(p.cantidad_total), 0) AS unidades
FROM public.pedidos p
GROUP BY p.estado_pago
ORDER BY numero_pedidos DESC, p.estado_pago;
