-- =====================================================================
-- 16_exportar_csv_dashboard.sql
--
-- Exporta los cinco CSV del contrato de integracion (apartado 7) para
-- el dashboard:
--
--   clientes.csv  modelos.csv  pedidos.csv  lineas_pedido.csv  stock.csv
--
-- Las columnas, el formato y de donde sale cada dato estan explicados en
-- 02_Acceso_Datos/documentacion/README.md, "Exportacion de los cinco CSV del dashboard".
--
-- SOLO LEE
--   No modifica ninguna tabla. Lo pueden ejecutar postgres, nova_admin,
--   nova_trabajador y nova_comercial. nova_cliente no, porque no ve la
--   tabla pedidos.
--
-- LOS CINCO ARCHIVOS SON UNA MISMA FOTO DE LA BASE
--   Todo va en una transaccion REPEATABLE READ: las cinco consultas ven
--   los mismos datos aunque otra conexion cree pedidos mientras tanto.
--   Asi pedidos.csv y lineas_pedido.csv siempre cuadran entre si.
--
-- SI ALGO FALLA, NO SE TOCA NINGUN CSV
--   Las comprobaciones van ANTES del primer \copy. Si una falla, o el rol
--   no tiene permiso para leer alguna tabla, psql se detiene sin abrir
--   ningun archivo y los CSV anteriores se quedan como estaban.
--
-- POR QUE \copy
--   Por lo mismo que en 15_exportar_fabricacion.sql: \o altera los saltos
--   de linea en Windows y \copy no. El nombre de cada archivo es fijo y se
--   dejan en el directorio desde el que se lanza psql:
--     mkdir salidas
--     cd salidas
--     psql -U postgres -d nova_sneakers -f ..\02_Acceso_Datos\sql\16_exportar_csv_dashboard.sql
-- =====================================================================

\set ON_ERROR_STOP on
\set referencia_prueba 'CUSTOM-40'

\echo '===== Exportacion de los cinco CSV para el dashboard ====='

BEGIN ISOLATION LEVEL REPEATABLE READ;

-- ---------------------------------------------------------------------
-- 1. Una vista temporal por archivo. Cada vista es la consulta exacta de
--    su CSV. Desaparecen al cerrar psql.
-- ---------------------------------------------------------------------

CREATE TEMP VIEW csv_clientes AS
SELECT
    c.id_cliente,
    c.nombre,
    c.tipo,
    c.email AS correo,
    c.telefono,
    c.activo::text AS activo
FROM public.clientes c;

CREATE TEMP VIEW csv_modelos AS
SELECT
    m.id_modelo,
    m.nombre AS nombre_modelo,
    m.descripcion,
    m.precio_base,
    m.activo::text AS activo
FROM public.modelos m;

CREATE TEMP VIEW csv_pedidos AS
SELECT
    p.id_pedido,
    p.referencia,
    p.id_cliente,
    to_char(p.fecha_pedido, 'YYYY-MM-DD HH24:MI:SS') AS fecha_pedido,
    CASE WHEN p.personalizado THEN 'custom' ELSE 'normal' END AS tipo_pedido,
    p.estado AS estado_pedido,
    p.estado_pago,
    p.personalizacion,
    p.cantidad_total,
    p.importe_total
FROM public.pedidos p;

-- Una linea normal apunta a un SKU. Una linea X-NOVA no tiene SKU: su
-- modelo es X-NOVA y su talla es la de la configuracion. Es el mismo
-- criterio que usan P-C y P-D en 12_consultas_panel.sql.
CREATE TEMP VIEW csv_lineas_pedido AS
SELECT
    l.id_linea,
    l.id_pedido,
    s.sku,
    COALESCE(v.id_modelo, mx.id_modelo) AS id_modelo,
    COALESCE(s.talla, x.talla_referencia) AS talla,
    l.cantidad,
    l.precio_unitario,
    l.subtotal AS importe_linea
FROM public.linea_pedido l
LEFT JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
LEFT JOIN public.variantes v ON v.id_variante = s.id_variante
LEFT JOIN public.configuraciones_xnova x ON x.id_configuracion = l.id_configuracion_xnova
LEFT JOIN public.modelos mx ON mx.nombre = 'X-NOVA' AND x.id_configuracion IS NOT NULL;

-- Una fila por SKU, sumando todas las naves. Un SKU sin existencias sale
-- con 0. Es la misma cuenta que la consulta C8 de stock bajo.
CREATE TEMP VIEW csv_stock AS
SELECT
    s.sku,
    v.id_modelo,
    v.color,
    s.talla,
    s.activo::text AS activo,
    COALESCE(SUM(e.cantidad), 0) AS stock_disponible,
    to_char(now(), 'YYYY-MM-DD HH24:MI:SS') AS fecha_corte
FROM public.producto_sku s
JOIN public.variantes v ON v.id_variante = s.id_variante
LEFT JOIN public.existencias e ON e.id_producto_sku = s.id_producto_sku
GROUP BY s.sku, v.id_modelo, v.color, s.talla, s.activo;

-- ---------------------------------------------------------------------
-- 2. Comprobaciones previas. Todavia no se ha abierto ningun archivo.
-- ---------------------------------------------------------------------
\echo ''
\echo '--- Comprobaciones previas'

-- El total guardado en cada pedido tiene que ser la suma de sus lineas.
-- Si no lo fuera, el dashboard daria ventas distintas segun leyera
-- pedidos.csv o lineas_pedido.csv.
DO $$
DECLARE
    v_descuadres integer;
BEGIN
    SELECT count(*)
      INTO v_descuadres
      FROM csv_pedidos p
      LEFT JOIN (
          SELECT id_pedido,
                 sum(cantidad) AS pares,
                 sum(importe_linea) AS importe
            FROM csv_lineas_pedido
           GROUP BY id_pedido
      ) l ON l.id_pedido = p.id_pedido
     WHERE p.cantidad_total <> COALESCE(l.pares, 0)
        OR p.importe_total <> COALESCE(l.importe, 0);

    IF v_descuadres > 0 THEN
        RAISE EXCEPTION
            '% pedidos no cuadran con sus lineas. No se exporta ningun CSV', v_descuadres;
    END IF;

    RAISE NOTICE 'PASS: el total de cada pedido coincide con la suma de sus lineas.';
END
$$;

-- Cada linea tiene que tener modelo y talla, o el dashboard no podria
-- agruparla por modelo ni por talla.
DO $$
DECLARE
    v_incompletas integer;
BEGIN
    SELECT count(*)
      INTO v_incompletas
      FROM csv_lineas_pedido
     WHERE id_modelo IS NULL OR talla IS NULL;

    IF v_incompletas > 0 THEN
        RAISE EXCEPTION
            '% lineas no tienen modelo o talla. No se exporta ningun CSV', v_incompletas;
    END IF;

    RAISE NOTICE 'PASS: todas las lineas tienen modelo y talla.';
END
$$;

-- Leer las cinco vistas aqui sirve para dos cosas: ensenar cuantas filas
-- tendra cada archivo y comprobar que el rol puede leer todas las tablas
-- antes de abrir ningun CSV.
\echo ''
\echo '--- Filas que se van a exportar'
SELECT 'clientes.csv' AS archivo, count(*) AS filas FROM csv_clientes
UNION ALL SELECT 'modelos.csv', count(*) FROM csv_modelos
UNION ALL SELECT 'pedidos.csv', count(*) FROM csv_pedidos
UNION ALL SELECT 'lineas_pedido.csv', count(*) FROM csv_lineas_pedido
UNION ALL SELECT 'stock.csv', count(*) FROM csv_stock;

-- ---------------------------------------------------------------------
-- 3. Exportacion: cabecera, UTF-8, separador coma, punto decimal y
--    orden fijo, para que dos exportaciones iguales den archivos iguales.
-- ---------------------------------------------------------------------
\echo ''
\echo '--- Exportacion'
\copy (SELECT * FROM csv_clientes ORDER BY id_cliente) TO 'clientes.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy (SELECT * FROM csv_modelos ORDER BY id_modelo) TO 'modelos.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy (SELECT * FROM csv_pedidos ORDER BY id_pedido) TO 'pedidos.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy (SELECT * FROM csv_lineas_pedido ORDER BY id_linea) TO 'lineas_pedido.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')
\copy (SELECT * FROM csv_stock ORDER BY id_modelo, color, talla) TO 'stock.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')

-- ---------------------------------------------------------------------
-- 4. El pedido de prueba tal y como lo vera el dashboard: se une lo que
--    hay en los CSV con las mismas claves que tendra que usar el.
-- ---------------------------------------------------------------------
\echo ''
\echo '--- Pedido de prueba reconstruido a partir de los CSV'
SELECT
    p.referencia,
    c.nombre AS cliente,
    m.nombre_modelo AS modelo,
    st.color,
    l.talla,
    l.cantidad,
    l.precio_unitario,
    l.importe_linea,
    p.importe_total AS total_pedido,
    p.estado_pedido
FROM csv_pedidos p
JOIN csv_clientes c ON c.id_cliente = p.id_cliente
JOIN csv_lineas_pedido l ON l.id_pedido = p.id_pedido
JOIN csv_modelos m ON m.id_modelo = l.id_modelo
LEFT JOIN csv_stock st ON st.sku = l.sku
WHERE p.referencia = :'referencia_prueba'
ORDER BY l.talla;

COMMIT;

\echo ''
\echo 'Exportacion terminada.'
