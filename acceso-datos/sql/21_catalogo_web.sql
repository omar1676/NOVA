-- =====================================================================
-- 21_catalogo_web.sql — los 100 modelos de la web, a la venta
--
-- QUE HACE
--   Da de alta en PostgreSQL los 100 modelos de la web
--   (interfaces/cliente/js/modelos.js), con:
--     - el MISMO nombre comercial que en la web (NOVA Street Vortex...): es
--       lo que une la web con la base. Si se cambia aqui, hay que cambiarlo
--       tambien en modelos.js;
--     - el precio, la descripcion y las tallas de su coleccion (los de
--       datosColeccion en modelos.js). Son PROVISIONALES hasta acordarlos
--       con Odoo;
--     - una variante por modelo, con el color que se ve en su foto;
--     - un SKU por talla, con el formato del resto del catalogo
--       (NOVA-<variante>-<talla>, como 05_datos_prueba.sql);
--     - existencias en la nave NOVA Central: 5 pares por talla en los 12
--       modelos que ya se vendian (los dos primeros de cada coleccion; las
--       pruebas de la tienda cuentan con esos 5) y 20 en los otros 88 (asi
--       no salen en el panel como "stock bajo", que es menos de 10).
--   En total: 100 modelos, 100 variantes, 880 SKU y 16010 pares. En una
--   base recien instalada la nave pasa de 1200 a 17210 pares; si ya se ha
--   confirmado algun pedido, como CUSTOM-40, seran menos. La capacidad de
--   la nave (2000, de 05_datos_prueba.sql) solo se informa, no se
--   comprueba: queda pendiente de acordar.
--
--   No toca los 7 modelos de 05_datos_prueba.sql (NOVA Origin...) ni Runner X.
--
-- COMO SE EJECUTA
--   Despues de la bateria 09_pruebas.sql (09 comprueba que hay 7 modelos,
--   12 variantes y 60 SKU) y del 20:
--     psql -U postgres -d nova_sneakers -f 21_catalogo_web.sql
--   Se puede repetir: lo que ya existe no se duplica, y las existencias no
--   se vuelven a poner (si ya hubo ventas, se respetan).
--   En una base montada con una version anterior de este script (12
--   modelos llamados "NOVA Street 01", "NOVA Luxe 02"...), el paso 0 les
--   pone el nombre nuevo (conservan sus SKU, su stock y sus pedidos) y los
--   pasos 1 a 4 anaden los otros 88.
-- =====================================================================

\set ON_ERROR_STOP on

\echo '===== Catalogo de la tienda web: 100 modelos ====='

BEGIN;

-- Lo comun a cada coleccion: lo mismo que datosColeccion en modelos.js.
-- Las tablas temporales desaparecen solas al terminar (ON COMMIT DROP).
CREATE TEMP TABLE colecciones_web (
    coleccion varchar(10),
    precio numeric(8,2),
    descripcion text,
    talla_min int4,
    talla_max int4
) ON COMMIT DROP;

INSERT INTO colecciones_web (coleccion, precio, descripcion, talla_min, talla_max)
VALUES
('Street', 109.90, 'Zapatilla urbana de estilo tecnico, con suela marcada y diseno atrevido', 38, 46),
('Luxe',   139.90, 'Linea elegante, de acabados cuidados y colores sobrios, para vestir',   38, 46),
('Casual',  89.90, 'Zapatilla de inspiracion retro, comoda para el dia a dia',              38, 46),
('Hombre',  99.90, 'Corte clasico y cana media, con horma de hombre',                       40, 46),
('Mujer',   99.90, 'Detalles cuidados y horma pensada para mujer',                          35, 42),
('Unisex',  94.90, 'Diseno neutro y tallaje amplio, para cualquier persona',                36, 46);

-- Los 100 modelos, uno por fila y en el orden de las fotos (01, 02...).
-- La coleccion es la segunda palabra del nombre. pares = existencias de
-- cada talla. nombre_antiguo: solo en los 12 que ya se vendian.
CREATE TEMP TABLE catalogo_web (
    nombre varchar(40),
    color varchar(30),
    pares int4,
    nombre_antiguo varchar(40)
) ON COMMIT DROP;

INSERT INTO catalogo_web (nombre, color, pares, nombre_antiguo)
VALUES
-- Street
('NOVA Street Vortex',    'Gris y coral',            5, 'NOVA Street 01'),
('NOVA Street Drift',     'Blanco y verde',          5, 'NOVA Street 02'),
('NOVA Street Flux',      'Gris y lima',            20, NULL),
('NOVA Street Metro',     'Crema y azul marino',    20, NULL),
('NOVA Street Blaze',     'Morado y negro',         20, NULL),
('NOVA Street Echo',      'Verde salvia',           20, NULL),
('NOVA Street Rebel',     'Negro y crema',          20, NULL),
('NOVA Street Volt',      'Azul y plata',           20, NULL),
('NOVA Street Rogue',     'Gris y verde',           20, NULL),
('NOVA Street Raptor',    'Burdeos y negro',        20, NULL),
-- Luxe
('NOVA Luxe Onyx',        'Negro',                   5, 'NOVA Luxe 01'),
('NOVA Luxe Ivory',       'Crema',                   5, 'NOVA Luxe 02'),
('NOVA Luxe Velvet',      'Oliva',                  20, NULL),
('NOVA Luxe Cobalt',      'Azul marino',            20, NULL),
('NOVA Luxe Sable',       'Arena',                  20, NULL),
('NOVA Luxe Pearl',       'Gris perla',             20, NULL),
('NOVA Luxe Ruby',        'Burdeos',                20, NULL),
('NOVA Luxe Jade',        'Crema y verde',          20, NULL),
('NOVA Luxe Sterling',    'Gris oscuro',            20, NULL),
('NOVA Luxe Amber',       'Crema y cuero',          20, NULL),
-- Casual
('NOVA Casual Marea',     'Azul marino y cuero',     5, 'NOVA Casual 01'),
('NOVA Casual Olivo',     'Crema y oliva',           5, 'NOVA Casual 02'),
('NOVA Casual Paseo',     'Crema y naranja',        20, NULL),
('NOVA Casual Puerto',    'Azul marino y cuero',    20, NULL),
('NOVA Casual Sendero',   'Oliva y cuero',          20, NULL),
('NOVA Casual Brisa',     'Crema y gris',           20, NULL),
('NOVA Casual Rambla',    'Cuero y azul marino',    20, NULL),
('NOVA Casual Velero',    'Crema y cuero',          20, NULL),
('NOVA Casual Faro',      'Azul marino y cuero',    20, NULL),
('NOVA Casual Poniente',  'Oliva y crema',          20, NULL),
('NOVA Casual Verano',    'Naranja y oliva',        20, NULL),
('NOVA Casual Ribera',    'Azul marino y naranja',  20, NULL),
('NOVA Casual Duna',      'Oliva y naranja',        20, NULL),
('NOVA Casual Cala',      'Verde y mostaza',        20, NULL),
('NOVA Casual Malva',     'Morado y crema',         20, NULL),
('NOVA Casual Terraza',   'Oliva y naranja',        20, NULL),
('NOVA Casual Siesta',    'Cuero y oliva',          20, NULL),
('NOVA Casual Levante',   'Verde azulado y naranja', 20, NULL),
('NOVA Casual Mirador',   'Oliva y azul marino',    20, NULL),
('NOVA Casual Salina',    'Cuero y naranja',        20, NULL),
-- Hombre
('NOVA Hombre Aneto',     'Azul marino',             5, 'NOVA Hombre 01'),
('NOVA Hombre Teide',     'Crema y azul',            5, 'NOVA Hombre 02'),
('NOVA Hombre Gredos',    'Azul marino y cuero',    20, NULL),
('NOVA Hombre Moncayo',   'Cuero y azul marino',    20, NULL),
('NOVA Hombre Veleta',    'Cuero y gris',           20, NULL),
('NOVA Hombre Ordesa',    'Crema y azul marino',    20, NULL),
('NOVA Hombre Almanzor',  'Azul marino y cuero',    20, NULL),
('NOVA Hombre Montseny',  'Crema y gris',           20, NULL),
('NOVA Hombre Posets',    'Cuero y gris',           20, NULL),
('NOVA Hombre Bulnes',    'Gris y azul marino',     20, NULL),
('NOVA Hombre Everest',   'Azul marino y naranja',  20, NULL),
('NOVA Hombre Denali',    'Oliva y naranja',        20, NULL),
('NOVA Hombre Elbrus',    'Azul marino y oliva',    20, NULL),
('NOVA Hombre Fuji',      'Crema y verde',          20, NULL),
('NOVA Hombre Etna',      'Azul marino y naranja',  20, NULL),
('NOVA Hombre Olimpo',    'Azul y gris',            20, NULL),
('NOVA Hombre Ararat',    'Crema y azul marino',    20, NULL),
('NOVA Hombre Atlas',     'Verde azulado y naranja', 20, NULL),
('NOVA Hombre Andes',     'Oliva y cuero',          20, NULL),
('NOVA Hombre Cervino',   'Cuero y oliva',          20, NULL),
-- Mujer
('NOVA Mujer Aurora',     'Rosa y granate',          5, 'NOVA Mujer 01'),
('NOVA Mujer Luna',       'Crema y rosa',            5, 'NOVA Mujer 02'),
('NOVA Mujer Vega',       'Granate y rosa',         20, NULL),
('NOVA Mujer Lyra',       'Granate y crema',        20, NULL),
('NOVA Mujer Stella',     'Arena y rosa',           20, NULL),
('NOVA Mujer Celeste',    'Crema y rosa',           20, NULL),
('NOVA Mujer Selene',     'Granate y crema',        20, NULL),
('NOVA Mujer Estela',     'Crema y dorado',         20, NULL),
('NOVA Mujer Maia',       'Rosa y gris',            20, NULL),
('NOVA Mujer Alba',       'Arena y oliva',          20, NULL),
('NOVA Mujer Electra',    'Lila y rosa',            20, NULL),
('NOVA Mujer Capella',    'Rosa y dorado',          20, NULL),
('NOVA Mujer Casiopea',   'Lila y plata',           20, NULL),
('NOVA Mujer Altair',     'Crema y granate',        20, NULL),
('NOVA Mujer Antares',    'Rosa y granate',         20, NULL),
('NOVA Mujer Nebula',     'Malva y rosa',           20, NULL),
('NOVA Mujer Polaris',    'Granate y dorado',       20, NULL),
('NOVA Mujer Carina',     'Lila y morado',          20, NULL),
('NOVA Mujer Elara',      'Crema y lila',           20, NULL),
('NOVA Mujer Lucero',     'Granate y rosa',         20, NULL),
-- Unisex
('NOVA Unisex Lisboa',    'Arena y oliva',           5, 'NOVA Unisex 01'),
('NOVA Unisex Oslo',      'Crema y verde',           5, 'NOVA Unisex 02'),
('NOVA Unisex Praga',     'Azul marino y naranja',  20, NULL),
('NOVA Unisex Viena',     'Oliva y cuero',          20, NULL),
('NOVA Unisex Roma',      'Crema y oliva',          20, NULL),
('NOVA Unisex Lima',      'Gris y naranja',         20, NULL),
('NOVA Unisex Quito',     'Azul marino y oliva',    20, NULL),
('NOVA Unisex Atenas',    'Crema y azul marino',    20, NULL),
('NOVA Unisex Kioto',     'Oliva y gris',           20, NULL),
('NOVA Unisex Oporto',    'Oliva y crema',          20, NULL),
('NOVA Unisex Tokio',     'Oliva y naranja',        20, NULL),
('NOVA Unisex Bergen',    'Oliva y granate',        20, NULL),
('NOVA Unisex Cusco',     'Cuero y naranja',        20, NULL),
('NOVA Unisex Boston',    'Crema y azul marino',    20, NULL),
('NOVA Unisex Denver',    'Verde azulado y naranja', 20, NULL),
('NOVA Unisex Austin',    'Verde salvia',           20, NULL),
('NOVA Unisex Dakar',     'Crema y verde',          20, NULL),
('NOVA Unisex Sevilla',   'Naranja y verde azulado', 20, NULL),
('NOVA Unisex Bilbao',    'Azul marino y naranja',  20, NULL),
('NOVA Unisex Toledo',    'Naranja y verde',        20, NULL);

-- 0. Si la base tiene los nombres antiguos, se cambian por los nuevos. Solo
--    si el nombre nuevo no existe ya (modelos_nombre_uq no deja repetirlo).
UPDATE public.modelos m
SET nombre = c.nombre
FROM catalogo_web c
WHERE m.nombre = c.nombre_antiguo
  AND NOT EXISTS (SELECT 1 FROM public.modelos n WHERE n.nombre = c.nombre);

-- 1. Los modelos (modelos_nombre_uq evita duplicarlos al repetir el script)
INSERT INTO public.modelos (nombre, descripcion, precio_base, activo)
SELECT c.nombre, w.descripcion, w.precio, true
FROM catalogo_web c
JOIN colecciones_web w ON w.coleccion = split_part(c.nombre, ' ', 2)
ON CONFLICT (nombre) DO NOTHING;

-- 2. Una variante (color) por modelo, sin suplemento de precio
INSERT INTO public.variantes (id_modelo, color)
SELECT m.id_modelo, c.color
FROM catalogo_web c
JOIN public.modelos m ON m.nombre = c.nombre
ON CONFLICT (id_modelo, color) DO NOTHING;

-- 3. Un SKU por talla, de talla_min a talla_max de su coleccion
INSERT INTO public.producto_sku (id_variante, talla, sku)
SELECT v.id_variante, t.talla, 'NOVA-' || v.id_variante || '-' || t.talla
FROM catalogo_web c
JOIN colecciones_web w ON w.coleccion = split_part(c.nombre, ' ', 2)
JOIN public.modelos m ON m.nombre = c.nombre
JOIN public.variantes v ON v.id_modelo = m.id_modelo AND v.color = c.color
CROSS JOIN LATERAL generate_series(w.talla_min, w.talla_max) AS t(talla)
ON CONFLICT DO NOTHING;

-- 4. Las existencias de cada talla en NOVA Central (5 o 20 pares)
INSERT INTO public.existencias (id_producto_sku, id_nave, cantidad)
SELECT s.id_producto_sku, n.id_nave, c.pares
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
\echo '--- Comprobacion: 100 modelos, 100 variantes, 880 SKU y 16010 pares (con las ventas descontadas)'
SELECT
    CASE WHEN count(DISTINCT m.id_modelo) = 100 AND count(DISTINCT v.id_variante) = 100
              AND count(DISTINCT s.id_producto_sku) = 880
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
\echo '--- El catalogo de la tienda, por coleccion'
SELECT split_part(m.nombre, ' ', 2) AS coleccion,
       count(DISTINCT m.id_modelo) AS modelos,
       min(m.precio_base) AS precio,
       min(s.talla) || '-' || max(s.talla) AS tallas,
       count(*) AS sku,
       sum(e.cantidad) AS pares
FROM public.modelos m
JOIN public.variantes v ON v.id_modelo = m.id_modelo
JOIN public.producto_sku s ON s.id_variante = v.id_variante
JOIN public.existencias e ON e.id_producto_sku = s.id_producto_sku
WHERE m.nombre ~ '^NOVA (Street|Luxe|Casual|Hombre|Mujer|Unisex) '
GROUP BY 1
ORDER BY 1;

\echo ''
\echo '===== FIN ====='
