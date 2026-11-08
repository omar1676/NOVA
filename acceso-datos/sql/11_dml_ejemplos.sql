\echo '===== EJEMPLOS DML: INSERT, UPDATE, DELETE y casos rechazados ====='
\echo ''
\echo 'Todo va dentro de transacciones que terminan en ROLLBACK, asi que los'
\echo 'datos de prueba no se alteran y el archivo se puede repetir.'
\echo ''

\echo '--- D1 INSERT: un cliente nuevo'
BEGIN;
INSERT INTO public.clientes (nombre, tipo, email, telefono, direccion_entrega)
VALUES ('Tienda Deportes Sur', 'empresa', 'deportes.sur@example.com',
        '600111222', 'Calle Mayor 1, Madrid');
SELECT
    CASE WHEN count(*) = 1 THEN 'PASS' ELSE 'FAIL' END AS d1,
    count(*) AS insertados
FROM public.clientes
WHERE email = 'deportes.sur@example.com';
ROLLBACK;

\echo ''
\echo '--- D2 INSERT: un modelo con su variante, su SKU y sus existencias'
BEGIN;
INSERT INTO public.modelos (nombre, descripcion, precio_base, activo)
VALUES ('NOVA Trail', 'Modelo de montana', 134.90, true);

INSERT INTO public.variantes (id_modelo, color, suplemento_precio)
SELECT id_modelo, 'Verde', 5.00
FROM public.modelos
WHERE nombre = 'NOVA Trail';

INSERT INTO public.producto_sku (id_variante, talla, sku)
SELECT v.id_variante, 42, 'NOVA-TRAIL-42'
FROM public.variantes v
JOIN public.modelos m ON m.id_modelo = v.id_modelo
WHERE m.nombre = 'NOVA Trail' AND v.color = 'Verde';

INSERT INTO public.existencias (id_producto_sku, id_nave, cantidad)
SELECT s.id_producto_sku, n.id_nave, 15
FROM public.producto_sku s
CROSS JOIN public.nave n
WHERE s.sku = 'NOVA-TRAIL-42'
  AND n.nombre = 'NOVA Central';

SELECT
    CASE WHEN modelos = 1 AND variantes = 1 AND sku = 1 AND stock = 15
         THEN 'PASS' ELSE 'FAIL' END AS d2,
    modelos, variantes, sku, stock
FROM (
    SELECT
        (SELECT count(*) FROM public.modelos WHERE nombre = 'NOVA Trail') AS modelos,
        (SELECT count(*) FROM public.variantes v
           JOIN public.modelos m ON m.id_modelo = v.id_modelo
          WHERE m.nombre = 'NOVA Trail') AS variantes,
        (SELECT count(*) FROM public.producto_sku WHERE sku = 'NOVA-TRAIL-42') AS sku,
        (SELECT e.cantidad FROM public.existencias e
           JOIN public.producto_sku s ON s.id_producto_sku = e.id_producto_sku
          WHERE s.sku = 'NOVA-TRAIL-42') AS stock
) AS t;
ROLLBACK;

\echo ''
\echo '--- D3 UPDATE: subir el precio base de un modelo'
BEGIN;
SELECT precio_base AS precio_antes FROM public.modelos WHERE nombre = 'NOVA Origin'
\gset
UPDATE public.modelos
SET precio_base = precio_base + 10
WHERE nombre = 'NOVA Origin';
SELECT
    CASE WHEN precio_base = :precio_antes + 10 THEN 'PASS' ELSE 'FAIL' END AS d3,
    :precio_antes AS antes, precio_base AS despues
FROM public.modelos
WHERE nombre = 'NOVA Origin';
ROLLBACK;

\echo ''
\echo '--- D4 UPDATE: avanzar el estado de un pedido'
BEGIN;
SELECT referencia AS ref FROM public.pedidos WHERE estado = 'pendiente' ORDER BY id_pedido LIMIT 1
\gset
UPDATE public.pedidos SET estado = 'confirmado' WHERE referencia = :'ref';
UPDATE public.pedidos SET estado = 'en_preparacion' WHERE referencia = :'ref';
SELECT
    CASE WHEN estado = 'en_preparacion' THEN 'PASS' ELSE 'FAIL' END AS d4,
    referencia, estado
FROM public.pedidos
WHERE referencia = :'ref';
ROLLBACK;

\echo ''
\echo '--- D5 DELETE: borrar una linea de un pedido pendiente sin stock descontado'
BEGIN;
SELECT l.id_linea AS linea
FROM public.linea_pedido l
JOIN public.pedidos p ON p.id_pedido = l.id_pedido
WHERE p.estado = 'pendiente'
  AND l.stock_descontado = false
  AND l.id_configuracion_xnova IS NULL
ORDER BY l.id_linea
LIMIT 1
\gset
DELETE FROM public.linea_pedido WHERE id_linea = :linea;
SELECT
    CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS d5,
    count(*) AS lineas_restantes
FROM public.linea_pedido
WHERE id_linea = :linea;
ROLLBACK;

\echo ''
\echo '--- D6 DELETE: borrar un cliente que no tiene pedidos'
BEGIN;
INSERT INTO public.clientes (nombre, email)
VALUES ('Cliente Temporal', 'temporal@example.com');
DELETE FROM public.clientes WHERE email = 'temporal@example.com';
SELECT
    CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS d6,
    count(*) AS clientes_restantes
FROM public.clientes
WHERE email = 'temporal@example.com';
ROLLBACK;

\echo ''
\echo '===== CASOS RECHAZADOS POR LAS RESTRICCIONES ====='

\echo ''
\echo '--- R1 CHECK: una linea con cantidad cero'
BEGIN;
DO $$
BEGIN
    INSERT INTO public.linea_pedido (id_pedido, id_producto_sku, cantidad, precio_unitario, subtotal)
    VALUES (
        (SELECT min(id_pedido) FROM public.pedidos),
        (SELECT min(id_producto_sku) FROM public.producto_sku),
        0, 50, 0);
    RAISE NOTICE 'FAIL R1: la base acepto cantidad cero';
EXCEPTION
    WHEN others THEN
        IF SQLSTATE = '23514' THEN
            RAISE NOTICE 'PASS R1: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL R1: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- R2 UNIQUE: dos clientes con el mismo correo'
BEGIN;
DO $$
BEGIN
    INSERT INTO public.clientes (nombre, email)
    VALUES ('Repetido', (SELECT email FROM public.clientes ORDER BY id_cliente LIMIT 1));
    RAISE NOTICE 'FAIL R2: la base acepto el correo repetido';
EXCEPTION
    WHEN others THEN
        IF SQLSTATE = '23505' THEN
            RAISE NOTICE 'PASS R2: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL R2: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- R3 FOREIGN KEY: un pedido de un cliente que no existe'
BEGIN;
DO $$
BEGIN
    INSERT INTO public.pedidos (referencia, id_cliente)
    VALUES ('R3', (SELECT max(id_cliente) + 1000 FROM public.clientes));
    RAISE NOTICE 'FAIL R3: la base acepto un cliente inexistente';
EXCEPTION
    WHEN others THEN
        IF SQLSTATE = '23503' THEN
            RAISE NOTICE 'PASS R3: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL R3: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- R4 NOT NULL: un modelo sin nombre'
BEGIN;
DO $$
BEGIN
    INSERT INTO public.modelos (nombre, precio_base) VALUES (NULL, 50);
    RAISE NOTICE 'FAIL R4: la base acepto un modelo sin nombre';
EXCEPTION
    WHEN others THEN
        IF SQLSTATE = '23502' THEN
            RAISE NOTICE 'PASS R4: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL R4: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- R5 CHECK: un estado de pedido que no esta permitido'
BEGIN;
DO $$
BEGIN
    UPDATE public.pedidos SET estado = 'inventado'
    WHERE id_pedido = (SELECT min(id_pedido) FROM public.pedidos);
    RAISE NOTICE 'FAIL R5: la base acepto un estado inventado';
EXCEPTION
    WHEN others THEN
        IF SQLSTATE = '23514' THEN
            RAISE NOTICE 'PASS R5: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL R5: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- R6 CHECK: una linea que es a la vez de catalogo y X-NOVA'
BEGIN;
DO $$
BEGIN
    INSERT INTO public.linea_pedido (
        id_pedido, id_producto_sku, id_configuracion_xnova, cantidad, precio_unitario, subtotal
    )
    VALUES (
        (SELECT min(id_pedido) FROM public.pedidos),
        (SELECT min(id_producto_sku) FROM public.producto_sku),
        1, 1, 50, 0);
    RAISE NOTICE 'FAIL R6: la base acepto la linea mixta';
EXCEPTION
    WHEN others THEN
        IF SQLSTATE IN ('23514', '23503') THEN
            RAISE NOTICE 'PASS R6: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL R6: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '===== FIN DE LOS EJEMPLOS DML ====='
