-- =====================================================================
-- 15_exportar_fabricacion.sql
--
-- Exporta a un CSV la orden de fabricacion de un pedido Custom, para que
-- PSP pueda leerla. Por defecto, CUSTOM-40. Para otro pedido, por ejemplo
-- SO024, se indica con -v referencia=SO024 (ver COMO SE EJECUTA).
--
-- QUE EXPORTA, Y QUE NO
--   Solo el pedido indicado, y solo si esta confirmado y suma 40
--   pares. No mezcla ningun otro pedido: cada orden de fabricacion es de
--   un pedido.
--
--   Un pedido pendiente todavia no se fabrica, y uno cancelado ya no se
--   fabrica: en los dos casos el script se detiene con un error.
--
--   Lee el pedido GUARDADO en la base, no datos temporales. CUSTOM-40 lo
--   crea 14_caso_custom_persistente.sql; SO024 se crea desde la
--   aplicacion Java.
--
-- ESTE CSV NO ES NINGUNO DE LOS CINCO DEL DASHBOARD
--   Los cinco CSV del dashboard de Python (clientes.csv, modelos.csv,
--   pedidos.csv, lineas_pedido.csv y stock.csv) los exporta
--   16_exportar_csv_dashboard.sql, con las columnas que usa Python
--   (04_Python/config.py). Este archivo es distinto: es la orden
--   de fabricacion de un pedido concreto, para PSP. Su formato esta
--   descrito en 06_Intermodular/SO024/contrato-fabricacion.md.
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
--   Comprobar y exportar van en la misma transaccion (READ COMMITTED: cada
--   sentencia ve lo confirmado al empezar; el 16 usa REPEATABLE READ).
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
--
--   Para exportar otro pedido, se le pasa su referencia:
--     psql -U postgres -d nova_sneakers -v referencia=SO024 -f 15_exportar_fabricacion.sql
--
--   Cada ejecucion sobrescribe fabricacion_psp.csv. Para guardar la orden
--   de CUSTOM-40 y la de SO024, lanzalo desde dos carpetas distintas.
--
--   Ni \copy ni los bloques DO ven las variables de psql. Por eso la
--   referencia se guarda en una tabla temporal (pedido_a_exportar) y las
--   consultas la leen de alli. La tabla desaparece al terminar.
-- =====================================================================

\set ON_ERROR_STOP on

-- Si no se indica otra referencia con -v, se exporta CUSTOM-40.
\if :{?referencia}
\else
\set referencia CUSTOM-40
\endif

\echo '===== Orden de fabricacion para PSP: pedido' :referencia '====='
\echo ''
\echo 'El CSV se deja como fabricacion_psp.csv en el directorio actual.'

BEGIN;

-- La referencia del pedido, en una tabla temporal que leen las consultas.
CREATE TEMP TABLE pedido_a_exportar ON COMMIT DROP AS
SELECT :'referencia'::varchar(30) AS referencia;

-- ---------------------------------------------------------------------
-- 1. Comprobaciones previas. Si alguna falla, psql se detiene aqui y el
--    CSV anterior se queda exactamente como estaba.
-- ---------------------------------------------------------------------
\echo ''
\echo '--- Comprobaciones previas'

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
            'No existe el pedido %. CUSTOM-40 lo crea 14_caso_custom_persistente.sql y SO024 la aplicacion Java',
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

    IF v_pares <> 40 THEN
        RAISE EXCEPTION
            '% tiene % pares y la orden de fabricacion exige exactamente 40', v_ref, v_pares;
    END IF;

    IF v_lineas <> v_tallas THEN
        RAISE EXCEPTION
            '% tiene % lineas para % tallas: hay tallas repetidas', v_ref, v_lineas, v_tallas;
    END IF;

    RAISE NOTICE
        'PASS: % (id %) esta confirmado, con % lineas, % tallas y 40 pares.',
        v_ref, v_pedido, v_lineas, v_tallas;
END
$$;

-- ---------------------------------------------------------------------
-- 2. Lo que se va a escribir, en pantalla, antes de escribirlo.
--
--    Las ocho columnas son datos reales de PostgreSQL. Los precios no
--    van aqui: la fabricacion no los necesita, y ya salen en
--    lineas_pedido.csv (16_exportar_csv_dashboard.sql).
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
WHERE p.referencia = (SELECT referencia FROM pedido_a_exportar)
ORDER BY s.talla;

-- ---------------------------------------------------------------------
-- 3. La exportacion, dentro de la misma transaccion (READ COMMITTED).
--    Orden estable por talla, cabecera y UTF-8.
-- ---------------------------------------------------------------------
\echo ''
\echo '--- Exportacion'

\copy (SELECT p.referencia, s.sku, c.nombre AS cliente, m.nombre AS modelo, v.color, p.personalizacion, s.talla, l.cantidad FROM public.pedidos p JOIN public.clientes c ON c.id_cliente = p.id_cliente JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku JOIN public.variantes v ON v.id_variante = s.id_variante JOIN public.modelos m ON m.id_modelo = v.id_modelo WHERE p.referencia = (SELECT referencia FROM pedido_a_exportar) AND p.estado = 'confirmado' ORDER BY s.talla) TO 'fabricacion_psp.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

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
