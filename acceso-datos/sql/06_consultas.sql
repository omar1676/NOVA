-- Consulta 1: ventas por modelo

SELECT
    m.nombre AS modelo,
    SUM(l.cantidad) AS unidades,
    SUM(l.subtotal) AS importe_total
FROM public.pedidos p
JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido
JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
JOIN public.variantes v ON v.id_variante = s.id_variante
JOIN public.modelos m ON m.id_modelo = v.id_modelo
GROUP BY m.id_modelo, m.nombre
ORDER BY importe_total DESC;


-- Consulta 2: ranking de clientes

SELECT
    c.nombre,
    c.email,
    COUNT(p.id_pedido) AS pedidos,
    COALESCE(SUM(p.importe_total), 0) AS importe_acumulado
FROM public.clientes c
LEFT JOIN public.pedidos p ON p.id_cliente = c.id_cliente
GROUP BY c.id_cliente, c.nombre, c.email
ORDER BY importe_acumulado DESC;


-- Consulta 3: productos con stock bajo

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
HAVING COALESCE(SUM(e.cantidad), 0) < 10
ORDER BY stock ASC, m.nombre;


-- Consulta 4: pedidos personalizados

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


-- Consulta 5: inventario por almacen

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


-- Consulta 6: tallas mas solicitadas

SELECT
    s.talla,
    SUM(l.cantidad) AS pares_pedidos,
    COUNT(DISTINCT l.id_pedido) AS pedidos_diferentes
FROM public.linea_pedido l
JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
GROUP BY s.talla
ORDER BY pares_pedidos DESC, s.talla;


-- Consulta 7: pedidos por mes

SELECT
    DATE_TRUNC('month', p.fecha_pedido)::date AS mes,
    COUNT(*) AS numero_pedidos,
    COALESCE(SUM(p.importe_total), 0) AS importe_pedidos,
    COUNT(*) FILTER (WHERE p.personalizado = true) AS personalizados
FROM public.pedidos p
GROUP BY DATE_TRUNC('month', p.fecha_pedido)
ORDER BY mes DESC;


-- Consulta 8: resumen de pagos y pedidos

SELECT
    p.estado_pago,
    COUNT(*) AS numero_pedidos,
    COALESCE(SUM(p.importe_total), 0) AS importe_total,
    COALESCE(SUM(p.cantidad_total), 0) AS unidades
FROM public.pedidos p
GROUP BY p.estado_pago
ORDER BY numero_pedidos DESC, p.estado_pago;
