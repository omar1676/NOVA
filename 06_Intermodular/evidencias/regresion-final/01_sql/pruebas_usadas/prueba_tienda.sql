-- Pruebas SQL de 20_tienda_web.sql y 21_catalogo_web.sql (base desechable nova_mejoras_sql).
-- web_mejoras: nombres comerciales nuevos y catalogo de 100 modelos (T12: 880 SKU en vez de 106).
-- Se ejecuta como postgres; cada prueba de la tienda se hace con SET ROLE tienda_web,
-- que tiene exactamente los permisos de tienda_web (sin los de superusuario).
\set QUIET on
\pset footer off
\set VERBOSITY terse

CREATE OR REPLACE FUNCTION pg_temp.debe_fallar(p_nombre text, p_sql text, p_esperado text)
RETURNS text LANGUAGE plpgsql AS $$
BEGIN
    EXECUTE p_sql;
    RETURN 'FAIL ' || p_nombre || ': se ejecuto sin error';
EXCEPTION WHEN others THEN
    IF SQLSTATE = p_esperado OR SQLERRM LIKE p_esperado THEN
        RETURN 'PASS ' || p_nombre || ': ' || SQLSTATE || ' ' || SQLERRM;
    END IF;
    RETURN 'FAIL ' || p_nombre || ': error inesperado ' || SQLSTATE || ' ' || SQLERRM;
END $$;

-- Datos de partida
SELECT id_producto_sku AS sku1 FROM producto_sku WHERE sku = (SELECT 'NOVA-' || v.id_variante || '-40' FROM variantes v JOIN modelos m USING (id_modelo) WHERE m.nombre = 'NOVA Street Vortex') \gset
SELECT id_producto_sku AS sku2 FROM producto_sku WHERE sku = (SELECT 'NOVA-' || v.id_variante || '-37' FROM variantes v JOIN modelos m USING (id_modelo) WHERE m.nombre = 'NOVA Mujer Aurora') \gset
SELECT id_producto_sku AS sku3 FROM producto_sku WHERE sku = (SELECT 'NOVA-' || v.id_variante || '-44' FROM variantes v JOIN modelos m USING (id_modelo) WHERE m.nombre = 'NOVA Luxe Ivory') \gset
SELECT count(*) AS eventos_inicio FROM log_eventos \gset

\echo '=== Permisos de tienda_web'
SET ROLE tienda_web;
SELECT pg_temp.debe_fallar('T1 no inserta pedidos', $q$INSERT INTO pedidos (referencia, id_cliente) VALUES ('X', 1)$q$, '42501');
SELECT pg_temp.debe_fallar('T2 no cambia el estado de un pedido', $q$UPDATE pedidos SET estado = 'confirmado' WHERE id_pedido = 1$q$, '42501');
SELECT pg_temp.debe_fallar('T3 no cambia importes', $q$UPDATE pedidos SET importe_total = 0$q$, '42501');
SELECT pg_temp.debe_fallar('T4 no toca existencias', $q$UPDATE existencias SET cantidad = 999$q$, '42501');
SELECT pg_temp.debe_fallar('T5 no toca lineas', $q$UPDATE linea_pedido SET precio_unitario = 0$q$, '42501');
SELECT pg_temp.debe_fallar('T6 no lee cuentas_cliente', $q$SELECT * FROM cuentas_cliente$q$, '42501');
SELECT pg_temp.debe_fallar('T7 no lee hashes de trabajadores', $q$SELECT password_hash FROM usuarios$q$, '42501');
SELECT pg_temp.debe_fallar('T8 no lee la auditoria', $q$SELECT * FROM log_eventos$q$, '42501');
SELECT pg_temp.debe_fallar('T9 no llama a realizar_compra', $q$SELECT realizar_compra('X', 1, 1, 1, 1)$q$, '42501');
SELECT pg_temp.debe_fallar('T10 no cambia datos de clientes', $q$UPDATE clientes SET email = 'x@x.es'$q$, '42501');
SELECT pg_temp.debe_fallar('T11 no borra pedidos', $q$DELETE FROM pedidos$q$, '42501');
SELECT CASE WHEN count(*) = 880 THEN 'PASS' ELSE 'FAIL' END || ' T12 lee el catalogo web con su stock: ' || count(*) || ' SKU con existencias'
FROM producto_sku s JOIN variantes v USING (id_variante) JOIN modelos m USING (id_modelo) JOIN existencias e USING (id_producto_sku)
WHERE m.nombre ~ '^NOVA (Street|Luxe|Casual|Hombre|Mujer|Unisex) [A-Z][a-z]+$';
RESET ROLE;

\echo '=== Registro e inicio de sesion'
SET ROLE tienda_web;
SELECT registrar_cliente('Ana Prueba', '  Ana.Prueba@Example.com ', 'clave-ana-123', '600111222', 'Calle Falsa 1, Madrid') AS ana \gset
SELECT registrar_cliente('Bea Prueba', 'bea.prueba@example.com', 'clave-bea-123') AS bea \gset
SELECT pg_temp.debe_fallar('R1 correo repetido (en otras mayusculas)', $q$SELECT registrar_cliente('Otra', 'ANA.PRUEBA@example.com', 'otraclave1')$q$, 'Ese correo ya esta registrado');
SELECT pg_temp.debe_fallar('R2 correo de un cliente dado de alta por un trabajador', $q$SELECT registrar_cliente('Suplantador', 'daniel.jan@example.com', 'clave-mala-1')$q$, 'Ese correo ya esta registrado');
SELECT pg_temp.debe_fallar('R3 contrasena corta', $q$SELECT registrar_cliente('Corta', 'corta@example.com', '1234567')$q$, 'La contrasena debe tener al menos 8 caracteres');
SELECT pg_temp.debe_fallar('R4 correo mal escrito', $q$SELECT registrar_cliente('Mal', 'no-es-un-correo', 'clave-larga-1')$q$, 'El correo no es valido');
SELECT pg_temp.debe_fallar('R5 nombre vacio', $q$SELECT registrar_cliente('   ', 'vacio@example.com', 'clave-larga-1')$q$, 'Escribe tu nombre%');
SELECT CASE WHEN iniciar_sesion_cliente('ana.prueba@example.com', 'clave-ana-123') = :ana THEN 'PASS' ELSE 'FAIL' END || ' L1 login correcto (correo en minusculas)';
SELECT CASE WHEN iniciar_sesion_cliente(' ANA.PRUEBA@EXAMPLE.COM', 'clave-ana-123') = :ana THEN 'PASS' ELSE 'FAIL' END || ' L2 login con el correo en mayusculas';
SELECT pg_temp.debe_fallar('L3 contrasena incorrecta', $q$SELECT iniciar_sesion_cliente('ana.prueba@example.com', 'clave-mala')$q$, 'Correo o contrasena incorrectos');
SELECT pg_temp.debe_fallar('L4 correo que no existe (mismo mensaje)', $q$SELECT iniciar_sesion_cliente('nadie@example.com', 'clave-ana-123')$q$, 'Correo o contrasena incorrectos');
SELECT pg_temp.debe_fallar('L5 un cliente sin cuenta web no entra', $q$SELECT iniciar_sesion_cliente('daniel.jan@example.com', 'cualquiera')$q$, 'Correo o contrasena incorrectos');
SELECT pg_temp.debe_fallar('L6 la cuenta de admin.demo no sirve en la tienda', $q$SELECT iniciar_sesion_cliente('admin.demo', 'cualquiera')$q$, 'Correo o contrasena incorrectos');
RESET ROLE;
SELECT CASE WHEN password_hash LIKE '$2a$%' AND length(password_hash) = 60 THEN 'PASS' ELSE 'FAIL' END || ' R6 la contrasena se guarda como hash bcrypt, no en claro'
FROM cuentas_cliente WHERE id_cliente = :ana;
SELECT CASE WHEN email = 'ana.prueba@example.com' AND tipo = 'particular' AND direccion_entrega = 'Calle Falsa 1, Madrid' THEN 'PASS' ELSE 'FAIL' END || ' R7 el cliente queda en clientes (correo en minusculas)'
FROM clientes WHERE id_cliente = :ana;

\echo '=== Crear la compra (pedido pendiente)'
SELECT cantidad AS stock1_antes FROM existencias WHERE id_producto_sku = :sku1 \gset
SELECT cantidad AS stock2_antes FROM existencias WHERE id_producto_sku = :sku2 \gset
SET ROLE tienda_web;
SELECT crear_compra_web(:ana, 'WEB-AAAAAAAAAAAAAAAAAAA1', ARRAY[:sku1, :sku2], ARRAY[2, 1], '600111222', 'Calle Falsa 1, Madrid') AS pedido_ana \gset
SELECT CASE WHEN crear_compra_web(:ana, 'WEB-AAAAAAAAAAAAAAAAAAA1', ARRAY[:sku1, :sku2], ARRAY[2, 1], '600111222', 'Calle Falsa 1, Madrid') = :pedido_ana
       THEN 'PASS' ELSE 'FAIL' END || ' C2 la misma referencia otra vez (doble clic) devuelve el mismo pedido';
SELECT pg_temp.debe_fallar('C3 otro cliente con la referencia de Ana', format($q$SELECT crear_compra_web(%s, 'WEB-AAAAAAAAAAAAAAAAAAA1', ARRAY[%s], ARRAY[1], '', 'Otra calle')$q$, :bea, :sku1), 'Referencia no valida');
SELECT pg_temp.debe_fallar('C4 carrito vacio', format($q$SELECT crear_compra_web(%s, 'WEB-AAAAAAAAAAAAAAAAAAA2', ARRAY[]::int[], ARRAY[]::int[], '', 'Calle')$q$, :bea), 'El carrito no es valido');
SELECT pg_temp.debe_fallar('C5 cantidad 0', format($q$SELECT crear_compra_web(%s, 'WEB-AAAAAAAAAAAAAAAAAAA2', ARRAY[%s], ARRAY[0], '', 'Calle')$q$, :bea, :sku1), 'Cada producto admite de 1 a 10 pares');
SELECT pg_temp.debe_fallar('C6 cantidad 11', format($q$SELECT crear_compra_web(%s, 'WEB-AAAAAAAAAAAAAAAAAAA2', ARRAY[%s], ARRAY[11], '', 'Calle')$q$, :bea, :sku1), 'Cada producto admite de 1 a 10 pares');
SELECT pg_temp.debe_fallar('C7 cantidad negativa', format($q$SELECT crear_compra_web(%s, 'WEB-AAAAAAAAAAAAAAAAAAA2', ARRAY[%s], ARRAY[-3], '', 'Calle')$q$, :bea, :sku1), 'Cada producto admite de 1 a 10 pares');
SELECT pg_temp.debe_fallar('C8 el mismo SKU dos veces', format($q$SELECT crear_compra_web(%s, 'WEB-AAAAAAAAAAAAAAAAAAA2', ARRAY[%s, %s], ARRAY[1, 1], '', 'Calle')$q$, :bea, :sku1, :sku1), 'Hay productos repetidos en el carrito');
SELECT pg_temp.debe_fallar('C9 listas de distinto tamano', format($q$SELECT crear_compra_web(%s, 'WEB-AAAAAAAAAAAAAAAAAAA2', ARRAY[%s, %s], ARRAY[1], '', 'Calle')$q$, :bea, :sku1, :sku2), 'El carrito no es valido');
SELECT pg_temp.debe_fallar('C10 SKU que no existe', format($q$SELECT crear_compra_web(%s, 'WEB-AAAAAAAAAAAAAAAAAAA2', ARRAY[999999], ARRAY[1], '', 'Calle')$q$, :bea), 'Producto no disponible');
SELECT pg_temp.debe_fallar('C11 mas pares de los que hay', format($q$SELECT crear_compra_web(%s, 'WEB-AAAAAAAAAAAAAAAAAAA2', ARRAY[%s], ARRAY[6], '', 'Calle')$q$, :bea, :sku3), 'No queda stock suficiente de NOVA Luxe Ivory (Crema, talla 44)');
SELECT pg_temp.debe_fallar('C12 sin direccion de entrega', format($q$SELECT crear_compra_web(%s, 'WEB-AAAAAAAAAAAAAAAAAAA2', ARRAY[%s], ARRAY[1], '', '  ')$q$, :bea, :sku1), 'Escribe la direccion de entrega%');
SELECT pg_temp.debe_fallar('C13 referencia con otro formato', format($q$SELECT crear_compra_web(%s, 'SO024', ARRAY[%s], ARRAY[1], '', 'Calle')$q$, :bea, :sku1), 'Referencia no valida');
SELECT pg_temp.debe_fallar('C14 cliente sin cuenta web', format($q$SELECT crear_compra_web(1, 'WEB-AAAAAAAAAAAAAAAAAAA2', ARRAY[%s], ARRAY[1], '', 'Calle')$q$, :sku1), 'Cliente no valido');
SELECT pg_temp.debe_fallar('C15 mas de 20 productos', format($q$SELECT crear_compra_web(%s, 'WEB-AAAAAAAAAAAAAAAAAAA2', array_fill(%s, ARRAY[21]), array_fill(1, ARRAY[21]), '', 'Calle')$q$, :bea, :sku1), 'El carrito no es valido');
RESET ROLE;
SELECT CASE WHEN count(*) = 1 THEN 'PASS' ELSE 'FAIL' END || ' C16 solo hay un pedido con esa referencia' FROM pedidos WHERE referencia = 'WEB-AAAAAAAAAAAAAAAAAAA1';
SELECT CASE WHEN p.estado = 'pendiente' AND p.estado_pago = 'pendiente' AND p.id_usuario IS NULL
            AND p.cantidad_total = 3 AND p.importe_total = 2 * 109.90 + 99.90 THEN 'PASS' ELSE 'FAIL' END
       || ' C1 pedido pendiente, con precio y total de la base: ' || p.cantidad_total || ' pares, ' || p.importe_total || ' EUR'
FROM pedidos p WHERE p.id_pedido = :pedido_ana;
SELECT CASE WHEN bool_and(l.precio_unitario = m.precio_base + v.suplemento_precio AND l.subtotal = l.cantidad * l.precio_unitario AND NOT l.stock_descontado)
       THEN 'PASS' ELSE 'FAIL' END || ' C17 cada linea lleva el precio del modelo y su subtotal; nada descontado aun'
FROM linea_pedido l JOIN producto_sku s USING (id_producto_sku) JOIN variantes v USING (id_variante) JOIN modelos m USING (id_modelo)
WHERE l.id_pedido = :pedido_ana;
SELECT CASE WHEN (SELECT cantidad FROM existencias WHERE id_producto_sku = :sku1) = :stock1_antes
             AND (SELECT cantidad FROM existencias WHERE id_producto_sku = :sku2) = :stock2_antes
       THEN 'PASS' ELSE 'FAIL' END || ' C18 crear el pedido no descuenta stock';

\echo '=== Confirmar (pago aceptado) y cancelar'
SET ROLE tienda_web;
SELECT pg_temp.debe_fallar('P1 Bea no puede pagar el pedido de Ana', format('SELECT confirmar_compra_web(%s, %s)', :bea, :pedido_ana), 'El pedido no existe');
SELECT pg_temp.debe_fallar('P2 Bea no puede cancelar el pedido de Ana', format('SELECT cancelar_compra_web(%s, %s)', :bea, :pedido_ana), 'El pedido no existe');
SELECT confirmar_compra_web(:ana, :pedido_ana);
SELECT confirmar_compra_web(:ana, :pedido_ana);
RESET ROLE;
SELECT CASE WHEN estado = 'confirmado' AND estado_pago = 'pagado' THEN 'PASS' ELSE 'FAIL' END || ' P3 Ana paga: confirmado y pagado' FROM pedidos WHERE id_pedido = :pedido_ana;
SELECT CASE WHEN (SELECT cantidad FROM existencias WHERE id_producto_sku = :sku1) = :stock1_antes - 2
             AND (SELECT cantidad FROM existencias WHERE id_producto_sku = :sku2) = :stock2_antes - 1
       THEN 'PASS' ELSE 'FAIL' END || ' P4 el stock baja exactamente lo comprado, una sola vez (pagado dos veces)';
SET ROLE tienda_web;
SELECT pg_temp.debe_fallar('P5 un pedido pagado no se cancela desde la web', format('SELECT cancelar_compra_web(%s, %s)', :ana, :pedido_ana), 'Un pedido pagado no se puede cancelar desde la web');
SELECT crear_compra_web(:bea, 'WEB-BBBBBBBBBBBBBBBBBBB1', ARRAY[:sku1], ARRAY[1], '', 'Calle de Bea 2') AS pedido_bea \gset
SELECT cancelar_compra_web(:bea, :pedido_bea);
SELECT cancelar_compra_web(:bea, :pedido_bea);
SELECT pg_temp.debe_fallar('P6 un pedido cancelado no se puede pagar', format('SELECT confirmar_compra_web(%s, %s)', :bea, :pedido_bea), 'Este pedido ya no se puede pagar');
RESET ROLE;
SELECT CASE WHEN estado = 'cancelado' AND estado_pago = 'pendiente' THEN 'PASS' ELSE 'FAIL' END || ' P7 pago rechazado o cancelado: el pedido queda cancelado' FROM pedidos WHERE id_pedido = :pedido_bea;
SELECT CASE WHEN (SELECT cantidad FROM existencias WHERE id_producto_sku = :sku1) = :stock1_antes - 2
       THEN 'PASS' ELSE 'FAIL' END || ' P8 cancelar un pendiente no cambia el stock';
SET ROLE tienda_web;
SELECT pg_temp.debe_fallar('P9 un pedido de Java (no WEB-) no se paga desde la web', $q$SELECT confirmar_compra_web(1, 1)$q$, 'El pedido no existe');
RESET ROLE;

\echo '=== Error a mitad de la confirmacion: no queda nada a medias'
SET ROLE tienda_web;
SELECT crear_compra_web(:bea, 'WEB-BBBBBBBBBBBBBBBBBBB2', ARRAY[:sku2, :sku3], ARRAY[1, 2], '', 'Calle de Bea 2') AS pedido_parcial \gset
RESET ROLE;
-- Otro cliente se lleva la talla 44 de Luxe 02 entre crear y pagar (se simula dejandola a 1)
SELECT cantidad AS stock2_parcial FROM existencias WHERE id_producto_sku = :sku2 \gset
UPDATE existencias SET cantidad = 1 WHERE id_producto_sku = :sku3;
SET ROLE tienda_web;
SELECT pg_temp.debe_fallar('E1 falta stock de la segunda linea al pagar', format('SELECT confirmar_compra_web(%s, %s)', :bea, :pedido_parcial), 'Stock insuficiente o producto no encontrado');
RESET ROLE;
SELECT CASE WHEN (SELECT cantidad FROM existencias WHERE id_producto_sku = :sku2) = :stock2_parcial
             AND (SELECT cantidad FROM existencias WHERE id_producto_sku = :sku3) = 1
             AND (SELECT estado FROM pedidos WHERE id_pedido = :pedido_parcial) = 'pendiente'
             AND (SELECT bool_and(NOT stock_descontado) FROM linea_pedido WHERE id_pedido = :pedido_parcial)
       THEN 'PASS' ELSE 'FAIL' END || ' E2 no se descuenta la primera linea y el pedido sigue pendiente';
UPDATE existencias SET cantidad = 5 WHERE id_producto_sku = :sku3;

\echo '=== Auditoria automatica (triggers de 08)'
SELECT CASE WHEN count(*) FILTER (WHERE accion = 'ALTA' AND detalle LIKE 'Pedido WEB-AAAAAAAAAAAAAAAAAAA1 creado para el cliente ' || :ana || '%') = 1
             AND count(*) FILTER (WHERE accion = 'CAMBIO_ESTADO' AND detalle LIKE 'Pedido WEB-AAAAAAAAAAAAAAAAAAA1: pendiente -> confirmado%') = 1
             AND count(*) FILTER (WHERE accion = 'CAMBIO_STOCK' AND detalle IN ('SKU ' || :sku1 || ': ' || :stock1_antes || ' -> ' || (:stock1_antes - 2),
                                                                             'SKU ' || :sku2 || ': ' || :stock2_antes || ' -> ' || (:stock2_antes - 1))) = 2
             AND count(*) FILTER (WHERE accion = 'BAJA_LOGICA' AND detalle LIKE 'Pedido WEB-BBBBBBBBBBBBBBBBBBB1: pendiente -> cancelado%') = 1
       THEN 'PASS' ELSE 'FAIL' END || ' A1 la auditoria registra alta, pago (cambio de estado), stock y cancelacion'
FROM log_eventos WHERE id_evento > :eventos_inicio;

-- Se deshace lo que han dejado estas pruebas para no ensuciar la base de las pruebas del servidor
\echo '=== Fin'
