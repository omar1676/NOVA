-- =====================================================================
-- 18_datos_so024.sql — datos del caso comun SO024
--
-- QUE HACE
--   Deja en la base lo que necesita el pedido SO024 del enunciado
--   (Club Halcones, Runner X, 40 pares, tallas 38 a 46), pero NO crea el
--   pedido: SO024 se da de alta y se confirma desde la aplicacion Java
--   (pestana "Nuevo pedido").
--   No es CUSTOM-40: ese pedido (10 y 14) es el caso Custom de Acceso a
--   Datos y usa NOVA Velocity en lugar de Runner X. SO024 es el caso
--   comun del proyecto intermodular y usa un Runner X de verdad.
--     1. El cliente Club Halcones.
--     2. El modelo Runner X, con un color.
--     3. Sus nueve SKU, de la talla 38 a la 46, con el mismo formato que
--        el resto del catalogo (05_datos_prueba.sql): NOVA-<variante>-<talla>.
--     4. Sus existencias en la nave NOVA Central.
--
--   No cambia ninguna tabla ni ningun trigger: solo hace INSERT, y en
--   estas cinco tablas no hay ningun trigger de INSERT.
--
-- DATOS QUE FALTAN POR ACORDAR
--   El precio, el color y el stock inicial no estan escritos aqui porque
--   todavia no se han acordado con Berme y Alvaro (Odoo debe tener los
--   mismos). Se pasan al ejecutar; si falta alguno, el script se para
--   sin insertar nada. Cuando se acuerden, se apuntan en
--   06_Intermodular/SO024/caso-comun-SO024.md.
--     precio = precio_base de Runner X, en euros y con punto (119.90).
--     color  = el color de su unica variante.
--     stock  = pares de cada talla. Tiene que llegar, como minimo, a los
--              pares que pida SO024 en su talla mas pedida; si no, la
--              confirmacion fallara con "Stock insuficiente".
--
-- SE PUEDE EJECUTAR LAS VECES QUE SE QUIERA
--   Cada INSERT lleva ON CONFLICT DO NOTHING: si la fila ya existe, no
--   hace nada. Asi no se duplica nada y, si SO024 ya ha gastado stock,
--   no se vuelve a rellenar.
--
-- CUANDO SE EJECUTA
--   Con el usuario que instalo la base, al final: despues de 14 y de
--   exportar CUSTOM-40 con 15 y 16. Luego se crea SO024 en Java y se
--   exporta con 15 -v referencia=SO024. Antes de las pruebas (09) no,
--   porque 09 cuenta los datos de 05 (P2 y S1).
--
-- COMO SE EJECUTA
--   psql -U postgres -d nova_sneakers -v precio=___ -v color=___ -v stock=___ -f 18_datos_so024.sql
-- =====================================================================

\set ON_ERROR_STOP on

\echo '===== Datos del caso comun SO024 (sin crear el pedido) ====='

-- Si falta un dato por acordar, se para aqui sin tocar la base.
\if :{?precio}
\else
\echo 'Falta el precio de Runner X (-v precio=...). No se ha insertado nada.'
\quit
\endif
\if :{?color}
\else
\echo 'Falta el color de Runner X (-v color=...). No se ha insertado nada.'
\quit
\endif
\if :{?stock}
\else
\echo 'Falta el stock inicial por talla (-v stock=...). No se ha insertado nada.'
\quit
\endif

BEGIN;

-- 1. Cliente. El email es ficticio, como los de 05_datos_prueba.sql.
INSERT INTO public.clientes (nombre, tipo, email)
VALUES ('Club Halcones', 'empresa', 'club.halcones@example.com')
ON CONFLICT (email) DO NOTHING;

-- 2. Modelo.
INSERT INTO public.modelos (nombre, descripcion, precio_base)
VALUES ('Runner X', 'Modelo del pedido Custom de clubes (caso SO024)',
        :'precio'::numeric(8,2))
ON CONFLICT (nombre) DO NOTHING;

-- 3. Color (una variante del modelo).
INSERT INTO public.variantes (id_modelo, color)
SELECT id_modelo, :'color'
FROM public.modelos
WHERE nombre = 'Runner X'
ON CONFLICT (id_modelo, color) DO NOTHING;

-- 4. Un SKU por talla, de la 38 a la 46.
INSERT INTO public.producto_sku (id_variante, talla, sku)
SELECT
    v.id_variante,
    tallas.talla,
    'NOVA-' || v.id_variante || '-' || tallas.talla
FROM public.variantes v
JOIN public.modelos m ON m.id_modelo = v.id_modelo
CROSS JOIN generate_series(38, 46) AS tallas(talla)
WHERE m.nombre = 'Runner X'
  AND v.color = :'color'
ON CONFLICT DO NOTHING;

-- 5. Stock inicial de cada SKU en la nave NOVA Central.
INSERT INTO public.existencias (id_producto_sku, id_nave, cantidad)
SELECT s.id_producto_sku, n.id_nave, :'stock'::integer
FROM public.producto_sku s
JOIN public.variantes v ON v.id_variante = s.id_variante
JOIN public.modelos m   ON m.id_modelo   = v.id_modelo
CROSS JOIN public.nave n
WHERE m.nombre = 'Runner X'
  AND v.color = :'color'
  AND n.nombre = 'NOVA Central'
ON CONFLICT DO NOTHING;

-- 6. Comprobacion: Runner X tiene las nueve tallas y todas con stock.
--    Si no, se deshace todo.
DO $$
DECLARE
    v_tallas    integer;
    v_sin_stock integer;
BEGIN
    SELECT count(DISTINCT s.talla)
      INTO v_tallas
      FROM public.producto_sku s
      JOIN public.variantes v ON v.id_variante = s.id_variante
      JOIN public.modelos m   ON m.id_modelo   = v.id_modelo
     WHERE m.nombre = 'Runner X'
       AND s.talla BETWEEN 38 AND 46;

    SELECT count(*)
      INTO v_sin_stock
      FROM public.producto_sku s
      JOIN public.variantes v ON v.id_variante = s.id_variante
      JOIN public.modelos m   ON m.id_modelo   = v.id_modelo
     WHERE m.nombre = 'Runner X'
       AND NOT EXISTS (SELECT 1 FROM public.existencias e
                        WHERE e.id_producto_sku = s.id_producto_sku);

    IF v_tallas <> 9 OR v_sin_stock <> 0 THEN
        RAISE EXCEPTION
            'Runner X tiene % tallas de la 38 a la 46 (se esperaban 9) y % SKU sin existencias',
            v_tallas, v_sin_stock;
    END IF;

    RAISE NOTICE 'PASS: Runner X tiene las 9 tallas (38 a 46) y todas tienen existencias.';
END
$$;

COMMIT;

\echo ''
\echo '--- Lo que hay ahora en la base para el caso SO024'
SELECT nombre, tipo, email
FROM public.clientes
WHERE email = 'club.halcones@example.com';

SELECT m.nombre AS modelo, m.precio_base, v.color, s.talla, s.sku, e.cantidad AS stock
FROM public.modelos m
JOIN public.variantes v     ON v.id_modelo        = m.id_modelo
JOIN public.producto_sku s  ON s.id_variante      = v.id_variante
JOIN public.existencias e   ON e.id_producto_sku  = s.id_producto_sku
WHERE m.nombre = 'Runner X'
ORDER BY v.color, s.talla;

\echo 'SO024 se crea ahora desde la aplicacion Java (pestana "Nuevo pedido").'
