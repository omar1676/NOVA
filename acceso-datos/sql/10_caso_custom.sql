\echo '===== CASO CUSTOM: club deportivo, 40 pares en varias tallas ====='
\echo ''
\echo 'Correspondencia documentada: el modelo Runner X del enunciado se'
\echo 'representa con NOVA Velocity, que es el modelo de running del catalogo.'
\echo 'El stock se mueve al confirmar y al cancelar, nunca al crear la linea.'
\echo 'Todo el escenario va dentro de una transaccion y termina en ROLLBACK,'
\echo 'asi que se puede repetir tantas veces como se quiera.'
\echo ''

BEGIN;

\echo '--- Paso 1: identificar al cliente'
SELECT id_cliente AS cliente, nombre, tipo, email
FROM public.clientes
WHERE email = 'club.atletico@example.com'
\gset
SELECT :cliente AS id_cliente, nombre, tipo
FROM public.clientes
WHERE id_cliente = :cliente;

\echo ''
\echo '--- Paso 2: identificar al operador que atiende el pedido'
SELECT gen_random_uuid()::text AS clave
\gset
SELECT public.establecer_password('tienda.demo', :'clave');
SELECT public.iniciar_sesion('tienda.demo', :'clave') AS operador_autenticado;

\echo ''
\echo '--- Paso 3: registrar el modelo y las cuatro tallas'
SELECT id_producto_sku AS sku40 FROM public.producto_sku s
JOIN public.variantes v ON v.id_variante = s.id_variante
JOIN public.modelos m ON m.id_modelo = v.id_modelo
WHERE m.nombre = 'NOVA Velocity' AND v.color = 'Rojo' AND s.talla = 40
\gset
SELECT id_producto_sku AS sku41 FROM public.producto_sku s
JOIN public.variantes v ON v.id_variante = s.id_variante
JOIN public.modelos m ON m.id_modelo = v.id_modelo
WHERE m.nombre = 'NOVA Velocity' AND v.color = 'Rojo' AND s.talla = 41
\gset
SELECT id_producto_sku AS sku42 FROM public.producto_sku s
JOIN public.variantes v ON v.id_variante = s.id_variante
JOIN public.modelos m ON m.id_modelo = v.id_modelo
WHERE m.nombre = 'NOVA Velocity' AND v.color = 'Rojo' AND s.talla = 42
\gset
SELECT id_producto_sku AS sku43 FROM public.producto_sku s
JOIN public.variantes v ON v.id_variante = s.id_variante
JOIN public.modelos m ON m.id_modelo = v.id_modelo
WHERE m.nombre = 'NOVA Velocity' AND v.color = 'Rojo' AND s.talla = 43
\gset
SELECT min(id_nave) AS nave FROM public.nave
\gset
SELECT sum(cantidad) AS stock_antes FROM public.existencias
\gset
SELECT :stock_antes AS stock_total_antes;

\echo ''
\echo '--- Paso 4: crear el pedido Custom con 10 pares de la talla 40'
SELECT public.realizar_compra('CUSTOM-40', :cliente, :sku40, :nave, 10) AS pedido
\gset
UPDATE public.pedidos
SET personalizado = true,
    personalizacion = 'Club Atletico NOVA: logo bordado y numeracion en el talon'
WHERE id_pedido = :pedido;

\echo ''
\echo '--- Paso 5: anadir las tallas 41, 42 y 43, 10 pares de cada una'
SELECT public.anadir_linea_pedido(:pedido, :sku41, :nave, 10);
SELECT public.anadir_linea_pedido(:pedido, :sku42, :nave, 10);
SELECT public.anadir_linea_pedido(:pedido, :sku43, :nave, 10);

\echo ''
\echo '--- Paso 6: el pedido suma exactamente 40 pares y su importe esta calculado'
SELECT
    CASE WHEN p.cantidad_total = 40 AND tallas = 4 AND p.importe_total = 40 * precio
         THEN 'PASS' ELSE 'FAIL' END AS paso6,
    p.referencia, p.cantidad_total AS pares, tallas, p.importe_total AS importe, precio
FROM public.pedidos p
CROSS JOIN (
    SELECT count(DISTINCT s.talla) AS tallas, max(l.precio_unitario) AS precio
    FROM public.linea_pedido l
    JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
    WHERE l.id_pedido = (SELECT id_pedido FROM public.pedidos WHERE referencia = 'CUSTOM-40')
) AS resumen
WHERE p.referencia = 'CUSTOM-40';

\echo ''
\echo '--- Paso 7: el pedido sigue pendiente y el stock NO se ha movido'
SELECT
    CASE WHEN estado = 'pendiente' AND stock = :stock_antes AND marcas = 0
         THEN 'PASS' ELSE 'FAIL' END AS paso7,
    estado, stock, marcas
FROM (
    SELECT
        (SELECT estado FROM public.pedidos WHERE id_pedido = :pedido) AS estado,
        (SELECT sum(cantidad) FROM public.existencias) AS stock,
        (SELECT count(*) FROM public.linea_pedido
          WHERE id_pedido = :pedido AND stock_descontado = true) AS marcas
) AS t;

\echo ''
\echo '--- Paso 7b: detalle por talla'
SELECT s.talla, l.cantidad AS pares, l.precio_unitario, l.subtotal, l.stock_descontado
FROM public.linea_pedido l
JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
WHERE l.id_pedido = :pedido
ORDER BY s.talla;

\echo ''
\echo '--- Paso 8: confirmar el pedido'
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :pedido;
SELECT referencia, estado, estado_pago FROM public.pedidos WHERE id_pedido = :pedido;

\echo ''
\echo '--- Paso 9: al confirmar, las existencias bajan en 40 pares de una sola vez'
SELECT
    CASE WHEN stock = :stock_antes - 40 AND marcas = 4
         THEN 'PASS' ELSE 'FAIL' END AS paso9,
    stock AS stock_ahora,
    :stock_antes - stock AS pares_descontados,
    marcas AS lineas_descontadas
FROM (
    SELECT
        (SELECT sum(cantidad) FROM public.existencias) AS stock,
        (SELECT count(*) FROM public.linea_pedido
          WHERE id_pedido = :pedido AND stock_descontado = true) AS marcas
) AS t;

\echo ''
\echo '--- Paso 9b: detalle de existencias por talla tras confirmar'
SELECT s.talla, e.cantidad AS stock_restante, l.cantidad AS pares_del_pedido
FROM public.linea_pedido l
JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
JOIN public.existencias e ON e.id_producto_sku = l.id_producto_sku
                         AND e.id_nave = l.id_nave
WHERE l.id_pedido = :pedido
ORDER BY s.talla;

\echo ''
\echo '--- Paso 10: la auditoria ha registrado el alta, el stock y la confirmacion'
SELECT id_usuario AS operador, tabla_afectada, accion, detalle
FROM public.log_eventos
ORDER BY id_evento;

\echo ''
\echo '--- Paso 11: cancelar y comprobar la devolucion completa'
UPDATE public.pedidos SET estado = 'cancelado' WHERE id_pedido = :pedido;
SELECT
    CASE WHEN stock = :stock_antes AND marcas_activas = 0 AND importe > 0
         THEN 'PASS' ELSE 'FAIL' END AS paso11,
    stock, marcas_activas, importe AS importe_conservado
FROM (
    SELECT
        (SELECT sum(cantidad) FROM public.existencias) AS stock,
        (SELECT count(*) FROM public.linea_pedido
          WHERE id_pedido = (SELECT id_pedido FROM public.pedidos WHERE referencia = 'CUSTOM-40')
            AND stock_descontado = true) AS marcas_activas,
        (SELECT importe_total FROM public.pedidos WHERE referencia = 'CUSTOM-40') AS importe
) AS t;

\echo ''
\echo '--- Paso 12: rechazar la confirmacion de otro pedido sin stock suficiente'
SELECT public.realizar_compra('CUSTOM-SIN-STOCK',
    (SELECT id_cliente FROM public.clientes WHERE email = 'club.atletico@example.com'),
    (SELECT s.id_producto_sku
       FROM public.producto_sku s
       JOIN public.variantes v ON v.id_variante = s.id_variante
       JOIN public.modelos m ON m.id_modelo = v.id_modelo
      WHERE m.nombre = 'NOVA Velocity' AND v.color = 'Rojo' AND s.talla = 40),
    (SELECT min(id_nave) FROM public.nave),
    500) AS pedido_sin_stock;
DO $$
BEGIN
    UPDATE public.pedidos SET estado = 'confirmado'
    WHERE referencia = 'CUSTOM-SIN-STOCK';
    RAISE NOTICE 'FAIL paso12: la base confirmo 500 pares que no hay';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'Stock insuficiente o producto no encontrado' THEN
            RAISE NOTICE 'PASS paso12: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL paso12: error inesperado: %', SQLERRM;
        END IF;
END
$$;
SELECT
    CASE WHEN estado = 'pendiente' AND minimo >= 0
         THEN 'PASS' ELSE 'FAIL' END AS paso12b_sin_stock_negativo,
    estado, minimo AS stock_minimo
FROM (
    SELECT
        (SELECT estado FROM public.pedidos WHERE referencia = 'CUSTOM-SIN-STOCK') AS estado,
        (SELECT min(cantidad) FROM public.existencias) AS minimo
) AS t;

\echo ''
\echo '--- Consulta de fabricacion para PSP'
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
ORDER BY p.referencia, s.talla;

\echo ''
\echo '--- Exportacion CSV de fabricacion'
\copy (SELECT p.referencia, c.nombre AS cliente, m.nombre AS modelo, p.personalizacion, s.talla, l.cantidad FROM public.pedidos p JOIN public.clientes c ON c.id_cliente = p.id_cliente JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku JOIN public.variantes v ON v.id_variante = s.id_variante JOIN public.modelos m ON m.id_modelo = v.id_modelo WHERE p.personalizado = true ORDER BY p.referencia, s.talla) TO 'fabricacion_psp.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

ROLLBACK;

\echo ''
\echo '===== FIN DEL CASO CUSTOM ====='
