-- =====================================================================
-- 15_exportar_fabricacion.sql
--
-- Exporta la orden de fabricacion del pedido CUSTOM-40 a un CSV, para
-- que PSP pueda leerla.
--
-- QUE EXPORTA, Y QUE NO
--   Solo CUSTOM-40, y solo si esta **confirmado**. No mezcla NOVA-0011
--   ni ningun otro pedido personalizado: cada orden de fabricacion es de
--   un pedido.
--
--   Un pedido pendiente todavia no se fabrica, y uno cancelado ya no se
--   fabrica: en los dos casos el script se detiene con un error.
--
--   Lee el pedido GUARDADO en la base, no datos temporales. Si CUSTOM-40
--   no esta, hay que ejecutar antes 14_caso_custom_persistente.sql.
--
-- ESTE CSV NO ES NINGUNO DE LOS CINCO DEL CONTRATO
--   El contrato de integracion (integracion/contrato-pedido.md, apartado
--   7) pide clientes.csv, modelos.csv, pedidos.csv, lineas_pedido.csv y
--   stock.csv, y sus columnas estan todavia sin acordar (apartado 8).
--   Este archivo es distinto: es la orden de fabricacion de un pedido
--   concreto. Se mantiene aparte hasta que PSP y Odoo acuerden el
--   formato definitivo de los cinco.
--
-- SI ALGO FALLA, FALLA DE VERDAD
--   Con ON_ERROR_STOP, cualquier error detiene psql y devuelve un codigo
--   de salida distinto de cero. Las comprobaciones lanzan excepciones en
--   lugar de imprimir FAIL, para que un fallo no pase por bueno.
--
--   Las comprobaciones van ANTES de abrir el archivo, asi que si los
--   datos no son correctos el CSV anterior se queda intacto: psql se
--   detiene sin llegar a tocarlo.
--
--   Comprobar y exportar van en la MISMA transaccion, para que las dos
--   cosas vean exactamente el mismo estado del pedido.
--
-- QUE PERMISOS HACEN FALTA
--   Solo lee. Lo pueden ejecutar postgres, nova_admin, nova_comercial y
--   nova_trabajador. nova_cliente no, porque no ve la tabla pedidos.
--
-- POR QUE SE USA \copy Y NO \o CON COPY ... TO STDOUT
--   Porque \o estropea los datos en Windows.
--
--   Si un campo lleva un salto de linea dentro, psql escribe su salida en
--   modo texto y convierte cada \n en \r\n, tambien los que son parte del
--   campo. Medido byte a byte sobre una personalizacion de dos lineas:
--
--     en la base       linea1 \n linea2          (0a)
--     con \o           linea1 \r\n linea2        (0d 0a)  <- alterado
--     con \copy        linea1 \n linea2          (0a)     <- correcto
--
--   Y si el campo ya tenia \r\n, con \o sale \r\r\n. Pasa igual con la
--   redireccion del shell y con psql -o: las tres vias de psql alteran los
--   bytes. Solo \copy y el COPY del servidor los conservan, y el del
--   servidor necesita superusuario.
--
--   El precio de usar \copy es que su argumento se toma literal y NO
--   admite variables, asi que el nombre del archivo es fijo. El destino se
--   elige con el directorio desde el que se lanza psql.
--
-- COMO SE EJECUTA
--   Deja fabricacion_psp.csv en el directorio actual:
--     psql -U postgres -d nova_sneakers -f 15_exportar_fabricacion.sql
--
--   Para dejarlo en otra carpeta, se lanza desde ella:
--     mkdir salidas
--     cd salidas
--     psql -U postgres -d nova_sneakers -f ..\15_exportar_fabricacion.sql
-- =====================================================================

\set ON_ERROR_STOP on

\echo '===== Orden de fabricacion para PSP: pedido CUSTOM-40 ====='
\echo ''
\echo 'El CSV se deja como fabricacion_psp.csv en el directorio actual.'

BEGIN;

-- ---------------------------------------------------------------------
-- 1. Comprobaciones previas. Si alguna falla, psql se detiene aqui y el
--    CSV anterior se queda exactamente como estaba.
-- ---------------------------------------------------------------------
\echo ''
\echo '--- Comprobaciones previas'

DO $$
DECLARE
    v_pedido integer;
    v_estado varchar(25);
    v_pares  integer;
    v_tallas integer;
    v_lineas integer;
BEGIN
    SELECT id_pedido, estado
      INTO v_pedido, v_estado
      FROM public.pedidos
     WHERE referencia = 'CUSTOM-40';

    IF v_pedido IS NULL THEN
        RAISE EXCEPTION
            'No existe el pedido CUSTOM-40. Ejecuta antes 14_caso_custom_persistente.sql';
    END IF;

    IF v_estado <> 'confirmado' THEN
        RAISE EXCEPTION
            'CUSTOM-40 esta en estado "%" y solo se fabrica un pedido confirmado. Un pedido pendiente aun no se fabrica y uno cancelado ya no',
            v_estado;
    END IF;

    SELECT count(*),
           coalesce(sum(l.cantidad), 0),
           count(DISTINCT s.talla)
      INTO v_lineas, v_pares, v_tallas
      FROM public.linea_pedido l
      JOIN public.producto_sku s
        ON s.id_producto_sku = l.id_producto_sku
     WHERE l.id_pedido = v_pedido;

    IF v_pares <> 40 THEN
        RAISE EXCEPTION
            'CUSTOM-40 tiene % pares y la orden de fabricacion exige exactamente 40', v_pares;
    END IF;

    IF v_tallas <> 4 THEN
        RAISE EXCEPTION
            'CUSTOM-40 tiene % tallas distintas y se esperaban 4', v_tallas;
    END IF;

    IF v_lineas <> v_tallas THEN
        RAISE EXCEPTION
            'CUSTOM-40 tiene % lineas para % tallas: hay tallas repetidas', v_lineas, v_tallas;
    END IF;

    RAISE NOTICE
        'PASS: CUSTOM-40 (id %) esta confirmado, con 4 lineas, 4 tallas y 40 pares.',
        v_pedido;
END
$$;

-- ---------------------------------------------------------------------
-- 2. Lo que se va a escribir, en pantalla, antes de escribirlo.
--
--    Las ocho columnas son datos reales de PostgreSQL. Los precios no
--    van aqui: la fabricacion no los necesita y su sitio es
--    lineas_pedido.csv, cuando se acuerde.
-- ---------------------------------------------------------------------
\echo ''
\echo '--- Filas que se van a exportar'

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
WHERE p.referencia = 'CUSTOM-40'
ORDER BY s.talla;

-- ---------------------------------------------------------------------
-- 3. La exportacion. Misma transaccion, mismo estado del pedido.
--    Orden estable por talla, cabecera y UTF-8.
-- ---------------------------------------------------------------------
\echo ''
\echo '--- Exportacion'

\copy (SELECT p.referencia, s.sku, c.nombre AS cliente, m.nombre AS modelo, v.color, p.personalizacion, s.talla, l.cantidad FROM public.pedidos p JOIN public.clientes c ON c.id_cliente = p.id_cliente JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku JOIN public.variantes v ON v.id_variante = s.id_variante JOIN public.modelos m ON m.id_modelo = v.id_modelo WHERE p.referencia = 'CUSTOM-40' AND p.estado = 'confirmado' ORDER BY s.talla) TO 'fabricacion_psp.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

-- ---------------------------------------------------------------------
-- 4. Comprobacion final, todavia en la misma transaccion.
-- ---------------------------------------------------------------------
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
     WHERE p.referencia = 'CUSTOM-40'
       AND p.estado = 'confirmado';

    IF v_filas <> 4 OR v_tallas <> 4 OR v_pares <> 40 THEN
        RAISE EXCEPTION
            'La orden exportada tiene % filas, % tallas y % pares; se esperaban 4, 4 y 40',
            v_filas, v_tallas, v_pares;
    END IF;

    RAISE NOTICE 'PASS: la orden exportada son 4 filas, 4 tallas y 40 pares.';
END
$$;

COMMIT;

\echo ''
\echo 'Exportacion terminada.'
\echo ''
