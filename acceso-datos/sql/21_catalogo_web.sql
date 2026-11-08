-- =====================================================================
-- 21_catalogo_web.sql — los 12 modelos de la web que se pueden comprar
--
-- QUE HACE
--   Da de alta en PostgreSQL el modelo 01 y el 02 de cada coleccion de la
--   web (interfaces/cliente/js/modelos.js), con:
--     - el MISMO nombre que en la web: es lo que une la web con la base;
--     - el precio y las tallas de su coleccion (datosColeccion en
--       modelos.js). Son PROVISIONALES hasta acordarlos con Odoo;
--     - una variante por modelo, con el color que se ve en su foto;
--     - un SKU por talla, con el formato del resto del catalogo
--       (NOVA-<variante>-<talla>, como 05_datos_prueba.sql);
--     - 5 pares de cada talla en la nave NOVA Central.
--   En total: 12 modelos, 12 variantes, 106 SKU y 530 pares. La nave pasa
--   de 1200 a 1730 pares (su capacidad es 2000).
--
--   Los otros 88 modelos de la web no estan en la base: la web los ensena,
--   pero como "No disponible".
--
-- COMO SE EJECUTA
--   Despues de la bateria 09_pruebas.sql (09 comprueba que hay 7 modelos,
--   12 variantes y 60 SKU) y del 20:
--     psql -U postgres -d nova_sneakers -f 21_catalogo_web.sql
--   Se puede repetir: lo que ya existe no se duplica, y las existencias no
--   se vuelven a poner a 5 (si ya hubo ventas, se respetan).
-- =====================================================================

\set ON_ERROR_STOP on

\echo '===== Catalogo de la tienda web: 12 modelos ====='

BEGIN;

-- Los 12 modelos en una tabla temporal, una fila por modelo, para verlos de
-- un vistazo. Desaparece sola al terminar la transaccion (ON COMMIT DROP).
CREATE TEMP TABLE catalogo_web (
    nombre varchar(40),
    color varchar(30),
    precio numeric(8,2),
    descripcion text,
    talla_min int4,
    talla_max int4
) ON COMMIT DROP;

INSERT INTO catalogo_web (nombre, color, precio, descripcion, talla_min, talla_max)
VALUES
('NOVA Street 01', 'Gris y coral',        109.90, 'Zapatilla urbana de estilo tecnico, con suela marcada y diseno atrevido', 38, 46),
('NOVA Street 02', 'Blanco y verde',      109.90, 'Zapatilla urbana de estilo tecnico, con suela marcada y diseno atrevido', 38, 46),
('NOVA Luxe 01',   'Negro',               139.90, 'Linea elegante, de acabados cuidados y colores sobrios, para vestir',   38, 46),
('NOVA Luxe 02',   'Crema',               139.90, 'Linea elegante, de acabados cuidados y colores sobrios, para vestir',   38, 46),
('NOVA Casual 01', 'Azul marino y cuero',  89.90, 'Zapatilla de inspiracion retro, comoda para el dia a dia',              38, 46),
('NOVA Casual 02', 'Crema y oliva',        89.90, 'Zapatilla de inspiracion retro, comoda para el dia a dia',              38, 46),
('NOVA Hombre 01', 'Azul marino',          99.90, 'Corte clasico y cana media, con horma de hombre',                       40, 46),
('NOVA Hombre 02', 'Crema y azul',         99.90, 'Corte clasico y cana media, con horma de hombre',                       40, 46),
('NOVA Mujer 01',  'Rosa y granate',       99.90, 'Detalles cuidados y horma pensada para mujer',                          35, 42),
('NOVA Mujer 02',  'Crema y rosa',         99.90, 'Detalles cuidados y horma pensada para mujer',                          35, 42),
('NOVA Unisex 01', 'Arena y oliva',        94.90, 'Diseno neutro y tallaje amplio, para cualquier persona',                36, 46),
('NOVA Unisex 02', 'Crema y verde',        94.90, 'Diseno neutro y tallaje amplio, para cualquier persona',                36, 46);

-- 1. Los modelos (modelos_nombre_uq evita duplicarlos al repetir el script)
INSERT INTO public.modelos (nombre, descripcion, precio_base, activo)
SELECT nombre, descripcion, precio, true
FROM catalogo_web
ON CONFLICT (nombre) DO NOTHING;

-- 2. Una variante (color) por modelo, sin suplemento de precio
INSERT INTO public.variantes (id_modelo, color)
SELECT m.id_modelo, c.color
FROM catalogo_web c
JOIN public.modelos m ON m.nombre = c.nombre
ON CONFLICT (id_modelo, color) DO NOTHING;

-- 3. Un SKU por talla, de talla_min a talla_max
INSERT INTO public.producto_sku (id_variante, talla, sku)
SELECT v.id_variante, t.talla, 'NOVA-' || v.id_variante || '-' || t.talla
FROM catalogo_web c
JOIN public.modelos m ON m.nombre = c.nombre
JOIN public.variantes v ON v.id_modelo = m.id_modelo AND v.color = c.color
CROSS JOIN LATERAL generate_series(c.talla_min, c.talla_max) AS t(talla)
ON CONFLICT DO NOTHING;

-- 4. 5 pares de cada talla en NOVA Central
INSERT INTO public.existencias (id_producto_sku, id_nave, cantidad)
SELECT s.id_producto_sku, n.id_nave, 5
FROM catalogo_web c
JOIN public.modelos m ON m.nombre = c.nombre
JOIN public.variantes v ON v.id_modelo = m.id_modelo AND v.color = c.color
JOIN public.producto_sku s ON s.id_variante = v.id_variante
JOIN public.nave n ON n.nombre = 'NOVA Central'
ON CONFLICT (id_producto_sku, id_nave) DO NOTHING;

-- ---------------------------------------------------------------------
-- Comprobacion (dentro de la transaccion, mientras existe catalogo_web)
-- ---------------------------------------------------------------------
\echo ''
\echo '--- Comprobacion: 12 modelos, 12 variantes, 106 SKU y 530 pares (con las ventas descontadas)'
SELECT
    CASE WHEN count(DISTINCT m.id_modelo) = 12 AND count(DISTINCT v.id_variante) = 12
              AND count(DISTINCT s.id_producto_sku) = 106
         THEN 'PASS' ELSE 'FAIL' END AS catalogo_web,
    count(DISTINCT m.id_modelo) AS modelos,
    count(DISTINCT v.id_variante) AS variantes,
    count(DISTINCT s.id_producto_sku) AS sku,
    sum(e.cantidad) AS pares
FROM catalogo_web c
JOIN public.modelos m ON m.nombre = c.nombre
JOIN public.variantes v ON v.id_modelo = m.id_modelo
JOIN public.producto_sku s ON s.id_variante = v.id_variante
LEFT JOIN public.existencias e ON e.id_producto_sku = s.id_producto_sku;

COMMIT;

\echo ''
\echo '--- El catalogo de la tienda'
SELECT m.nombre AS modelo, v.color, m.precio_base AS precio,
       min(s.talla) || '-' || max(s.talla) AS tallas,
       count(*) AS sku, sum(e.cantidad) AS pares
FROM public.modelos m
JOIN public.variantes v ON v.id_modelo = m.id_modelo
JOIN public.producto_sku s ON s.id_variante = v.id_variante
JOIN public.existencias e ON e.id_producto_sku = s.id_producto_sku
WHERE m.nombre ~ '^NOVA (Street|Luxe|Casual|Hombre|Mujer|Unisex) 0[12]$'
GROUP BY m.nombre, v.color, m.precio_base
ORDER BY m.nombre;

\echo ''
\echo '===== FIN ====='
