-- 15_exportar_fabricacion.sql — exporta a CSV la orden de fabricacion de un pedido, para PSP

\set ON_ERROR_STOP on

-- Si no se indica otra referencia con -v, se exporta CUSTOM-40.
\if :{?referencia}
\else
\set referencia CUSTOM-40
\endif

\echo 'Orden de fabricacion para PSP: pedido' :referencia
\echo ''
\echo 'El CSV se deja como fabricacion_psp.csv en el directorio actual.'

BEGIN;

-- La referencia del pedido, en una tabla temporal que leen las consultas.
CREATE TEMP TABLE pedido_a_exportar ON COMMIT DROP AS
SELECT :'referencia'::varchar(30) AS referencia;

-- 1. Comprobaciones previas. Si alguna falla, psql se detiene aqui y el
--    CSV anterior se queda como estaba
\echo ''
\echo 'Comprobaciones previas'

DO $$
DECLARE
    v_ref    varchar(30);
    v_pedido integer;
    v_estado varchar(25);
    v_pares  integer;
    v_tallas integer;
    v_lineas integer;
BEGIN
    SELECT referencia INTO v_ref FROM pedido_a_exportar;

    SELECT id_pedido, estado
      INTO v_pedido, v_estado
      FROM public.pedidos
     WHERE referencia = v_ref;

    IF v_pedido IS NULL THEN
        RAISE EXCEPTION
            'No existe el pedido %. CUSTOM-40 lo crea 14_caso_custom_persistente.sql y SO024 se crea antes en la base',
            v_ref;
    END IF;

    IF v_estado <> 'confirmado' THEN
        RAISE EXCEPTION
            '% esta en estado "%" y solo se fabrica un pedido confirmado. Un pedido pendiente aun no se fabrica y uno cancelado ya no',
            v_ref, v_estado;
    END IF;

    SELECT count(*),
           coalesce(sum(l.cantidad), 0),
           count(DISTINCT s.talla)
      INTO v_lineas, v_pares, v_tallas
      FROM public.linea_pedido l
      JOIN public.producto_sku s
        ON s.id_producto_sku = l.id_producto_sku
     WHERE l.id_pedido = v_pedido;

    -- Regla de la orden de fabricacion: exactamente 40 pares
    IF v_pares <> 40 THEN
        RAISE EXCEPTION
            '% tiene % pares y la orden de fabricacion exige exactamente 40', v_ref, v_pares;
    END IF;

    -- Una linea por talla: si hay mas lineas que tallas, alguna esta repetida
    IF v_lineas <> v_tallas THEN
        RAISE EXCEPTION
            '% tiene % lineas para % tallas: hay tallas repetidas', v_ref, v_lineas, v_tallas;
    END IF;

    RAISE NOTICE
        'PASS: % (id %) esta confirmado, con % lineas, % tallas y 40 pares.',
        v_ref, v_pedido, v_lineas, v_tallas;
END
$$;

-- 2. Lo que se va a escribir, en pantalla, antes de escribirlo.
\echo ''
\echo 'Filas que se van a exportar'

SELECT
    p.referencia,
    s.sku,
    c.nombre AS cliente,
    m.nombre AS modelo,
    v.color,
    p.personalizacion,
    s.talla,
    l.cantidad
FROM public.pedidos p
JOIN public.clientes c      ON c.id_cliente      = p.id_cliente
JOIN public.linea_pedido l  ON l.id_pedido       = p.id_pedido
JOIN public.producto_sku s  ON s.id_producto_sku = l.id_producto_sku
JOIN public.variantes v     ON v.id_variante     = s.id_variante
JOIN public.modelos m       ON m.id_modelo       = v.id_modelo
WHERE p.referencia = (SELECT referencia FROM pedido_a_exportar)
ORDER BY s.talla;

-- 3. La exportacion, dentro de la misma transaccion (READ COMMITTED).
--    La orden copy de psql tiene que ir entera en una sola linea
\echo ''
\echo 'Exportacion'

\copy (SELECT p.referencia, s.sku, c.nombre AS cliente, m.nombre AS modelo, v.color, p.personalizacion, s.talla, l.cantidad FROM public.pedidos p JOIN public.clientes c ON c.id_cliente = p.id_cliente JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku JOIN public.variantes v ON v.id_variante = s.id_variante JOIN public.modelos m ON m.id_modelo = v.id_modelo WHERE p.referencia = (SELECT referencia FROM pedido_a_exportar) AND p.estado = 'confirmado' ORDER BY s.talla) TO 'fabricacion_psp.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

-- 4. Comprobacion final, todavia en la misma transaccion.
DO $$
DECLARE
    v_filas  integer;
    v_tallas integer;
    v_pares  integer;
BEGIN
    SELECT count(*), count(DISTINCT s.talla), coalesce(sum(l.cantidad), 0)
      INTO v_filas, v_tallas, v_pares
      FROM public.pedidos p
      JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido
      JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
     WHERE p.referencia = (SELECT referencia FROM pedido_a_exportar)
       AND p.estado = 'confirmado';

    IF v_filas <> v_tallas OR v_pares <> 40 THEN
        RAISE EXCEPTION
            'La orden exportada tiene % filas, % tallas y % pares; se esperaba una fila por talla y 40 pares',
            v_filas, v_tallas, v_pares;
    END IF;

    RAISE NOTICE 'PASS: la orden exportada son % filas, % tallas y 40 pares.', v_filas, v_tallas;
END
$$;

COMMIT;

\echo ''
\echo 'Exportacion terminada.'
\echo ''
