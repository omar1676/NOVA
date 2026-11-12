\echo '===== NOVA Sneakers: bateria de pruebas ====='
\echo ''
\echo 'Los identificadores se obtienen de la base, no se escriben a mano.'

SELECT min(id_cliente) AS cliente_a, max(id_cliente) AS cliente_b FROM public.clientes
\gset
SELECT min(id_producto_sku) AS sku FROM public.producto_sku
\gset
SELECT min(id_nave) AS nave FROM public.nave
\gset
SELECT min(id_usuario) AS usuario FROM public.usuarios
\gset
SELECT referencia AS ref_demo FROM public.pedidos ORDER BY id_pedido LIMIT 1
\gset

SELECT :cliente_a AS cliente_a, :cliente_b AS cliente_b, :sku AS sku,
       :nave AS nave, :usuario AS usuario, :'ref_demo' AS pedido_demo;

\echo ''
\echo '===== COMPROBACIONES DE INSTALACION ====='
\echo ''
\echo '--- P1 objetos instalados (esperado 14 tablas, 16 claves, 19 funciones, 10 disparadores, 4 roles)'
SELECT
    CASE WHEN tablas = 14 AND claves = 16 AND funciones = 19
              AND disparadores = 10 AND roles = 4
         THEN 'PASS' ELSE 'FAIL' END AS p1,
    tablas, claves, funciones, disparadores, roles
FROM (
    SELECT
        (SELECT count(*) FROM information_schema.tables
          WHERE table_schema = 'public') AS tablas,
        (SELECT count(*) FROM pg_constraint
          WHERE contype = 'f' AND connamespace = 'public'::regnamespace) AS claves,
        (SELECT count(*) FROM pg_proc
          WHERE pronamespace = 'public'::regnamespace) AS funciones,
        (SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal) AS disparadores,
        (SELECT count(*) FROM pg_roles WHERE rolname LIKE 'nova\_%') AS roles
) AS conteo;

\echo ''
\echo '--- P1b las funciones SECURITY DEFINER pertenecen al dueno de las tablas'
SELECT
    CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS p1b,
    count(*) AS funciones_con_otro_dueno
FROM pg_proc f
WHERE f.pronamespace = 'public'::regnamespace
  AND f.prosecdef
  AND f.proowner <> (
      SELECT relowner FROM pg_class WHERE oid = 'public.linea_pedido'::regclass
  );

\echo ''
\echo '--- P1c las funciones SECURITY DEFINER fijan su search_path'
SELECT
    CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS p1c,
    count(*) AS funciones_sin_search_path
FROM pg_proc f
WHERE f.pronamespace = 'public'::regnamespace
  AND f.prosecdef
  AND f.proconfig IS NULL;

\echo ''
\echo '--- P1d lista de funciones SECURITY DEFINER'
SELECT f.proname AS funcion, pg_get_userbyid(f.proowner) AS dueno, f.proconfig AS configuracion
FROM pg_proc f
WHERE f.pronamespace = 'public'::regnamespace AND f.prosecdef
ORDER BY f.proname;

\echo ''
\echo '--- P2 datos de demostracion: el catalogo instalado'
\echo '    (el catalogo no cambia aunque despues se anadan pedidos)'
SELECT
    CASE WHEN modelos = 7 AND variantes = 12 AND sku = 60 AND naves = 1
              AND clientes = 6 AND roles_app = 3 AND personal = 3 AND usuarios = 3
              AND stock_total = 1200 - stock_descontado
         THEN 'PASS' ELSE 'FAIL' END AS p2,
    conteo.*
FROM (
    SELECT
        (SELECT count(*) FROM public.modelos) AS modelos,
        (SELECT count(*) FROM public.variantes) AS variantes,
        (SELECT count(*) FROM public.producto_sku) AS sku,
        (SELECT count(*) FROM public.nave) AS naves,
        (SELECT count(*) FROM public.clientes) AS clientes,
        (SELECT count(*) FROM public.roles) AS roles_app,
        (SELECT count(*) FROM public.personal) AS personal,
        (SELECT count(*) FROM public.usuarios) AS usuarios,
        (SELECT sum(cantidad) FROM public.existencias) AS stock_total,
        -- Las 1200 unidades instaladas menos lo que se haya descontado
        -- por pedidos confirmados. Asi la cuenta sigue cuadrando aunque
        -- se confirmen pedidos despues de instalar.
        (SELECT coalesce(sum(l.cantidad), 0) FROM public.linea_pedido l
          WHERE l.stock_descontado = true) AS stock_descontado
) AS conteo;

\echo ''
\echo '--- P2a los 11 pedidos de demostracion y sus 14 lineas'
\echo '    (acotado a las referencias NOVA-%, para no contar pedidos anadidos luego)'
SELECT
    CASE WHEN pedidos = 11 AND lineas = 14 AND importe = 5890.45
         THEN 'PASS' ELSE 'FAIL' END AS p2a,
    pedidos, lineas, importe
FROM (
    SELECT
        (SELECT count(*) FROM public.pedidos
          WHERE referencia LIKE 'NOVA-%') AS pedidos,
        (SELECT count(*) FROM public.linea_pedido l
           JOIN public.pedidos p ON p.id_pedido = l.id_pedido
          WHERE p.referencia LIKE 'NOVA-%') AS lineas,
        (SELECT sum(importe_total) FROM public.pedidos
          WHERE referencia LIKE 'NOVA-%') AS importe
) AS conteo;

\echo ''
\echo '--- P2b los pedidos de demostracion reparten el usuario asignado (9 con usuario, 2 sin usuario)'
SELECT
    CASE WHEN con_usuario = 9 AND sin_usuario = 2 THEN 'PASS' ELSE 'FAIL' END AS p2b,
    con_usuario, sin_usuario
FROM (
    SELECT count(id_usuario) AS con_usuario,
           count(*) - count(id_usuario) AS sin_usuario
    FROM public.pedidos
    WHERE referencia LIKE 'NOVA-%'
) AS t;

\echo ''
\echo '--- P3 los disparadores calcularon bien los totales de TODOS los pedidos'
\echo '    (se cuentan los incoherentes: tienen que ser cero, haya 11 pedidos o 50)'
SELECT
    CASE WHEN incoherentes = 0 THEN 'PASS' ELSE 'FAIL' END AS p3,
    incoherentes, total_pedidos
FROM (
    SELECT
        count(*) FILTER (
            WHERE p.cantidad_total <> COALESCE((
                    SELECT sum(l.cantidad) FROM public.linea_pedido l
                     WHERE l.id_pedido = p.id_pedido), 0)
               OR p.importe_total <> COALESCE((
                    SELECT sum(l.subtotal) FROM public.linea_pedido l
                     WHERE l.id_pedido = p.id_pedido), 0)
        ) AS incoherentes,
        count(*) AS total_pedidos
    FROM public.pedidos p
) AS t;

\echo ''
\echo '===== COMPRAS Y CANCELACIONES ====='
\echo ''
\echo '--- P4 crear un pedido NO mueve el stock; confirmarlo si'
BEGIN;
SELECT sum(cantidad) AS stock_antes FROM public.existencias
\gset
SELECT public.realizar_compra('P4', :cliente_a, :sku, :nave, 2) AS id_pedido
\gset
SELECT
    CASE WHEN stock = :stock_antes AND NOT marca AND estado = 'pendiente'
              AND unidades = 2 AND importe = 2 * precio
         THEN 'PASS' ELSE 'FAIL' END AS p4_al_crear,
    stock, marca, estado, unidades, importe
FROM (
    SELECT
        (SELECT sum(cantidad) FROM public.existencias) AS stock,
        p.estado AS estado,
        p.cantidad_total AS unidades,
        p.importe_total AS importe,
        l.stock_descontado AS marca,
        l.precio_unitario AS precio
    FROM public.pedidos p
    JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido
    WHERE p.id_pedido = :id_pedido
) AS t;
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
SELECT
    CASE WHEN stock = :stock_antes - 2 AND marca AND estado = 'confirmado'
         THEN 'PASS' ELSE 'FAIL' END AS p4_al_confirmar,
    stock, marca, estado
FROM (
    SELECT
        (SELECT sum(cantidad) FROM public.existencias) AS stock,
        p.estado AS estado,
        l.stock_descontado AS marca
    FROM public.pedidos p
    JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido
    WHERE p.id_pedido = :id_pedido
) AS t;
ROLLBACK;

\echo ''
\echo '--- P4b editar una linea pendiente no descuenta stock, y al confirmar se'
\echo '    descuenta una sola vez la cantidad final (requisito 3.6 del enunciado)'
BEGIN;
SELECT sum(cantidad) AS stock_antes FROM public.existencias
\gset
SELECT public.realizar_compra('P4b', :cliente_a, :sku, :nave, 5) AS id_pedido
\gset
UPDATE public.linea_pedido SET cantidad = 8 WHERE id_pedido = :id_pedido;
SELECT
    CASE WHEN stock = :stock_antes AND unidades = 8
         THEN 'PASS' ELSE 'FAIL' END AS p4b_tras_editar,
    stock, unidades
FROM (
    SELECT
        (SELECT sum(cantidad) FROM public.existencias) AS stock,
        (SELECT cantidad_total FROM public.pedidos WHERE id_pedido = :id_pedido) AS unidades
) AS t;
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
SELECT
    CASE WHEN stock = :stock_antes - 8 THEN 'PASS' ELSE 'FAIL' END AS p4b_tras_confirmar,
    stock, :stock_antes - stock AS descontado
FROM (
    SELECT (SELECT sum(cantidad) FROM public.existencias) AS stock
) AS t;
ROLLBACK;

\echo ''
\echo '--- P4c confirmar dos veces no descuenta el stock por duplicado'
BEGIN;
SELECT sum(cantidad) AS stock_antes FROM public.existencias
\gset
SELECT public.realizar_compra('P4c', :cliente_a, :sku, :nave, 3) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
UPDATE public.pedidos SET estado = 'en_preparacion' WHERE id_pedido = :id_pedido;
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
SELECT
    CASE WHEN sum(cantidad) = :stock_antes - 3 THEN 'PASS' ELSE 'FAIL' END AS p4c,
    sum(cantidad) AS stock,
    :stock_antes - sum(cantidad) AS descontado
FROM public.existencias;
ROLLBACK;

\echo ''
\echo '--- P5 pedido de tres lineas: el stock baja 6 al confirmar, no antes'
BEGIN;
SELECT sum(cantidad) AS stock_antes FROM public.existencias
\gset
SELECT public.realizar_compra('P5', :cliente_a, :sku, :nave, 1) AS id_pedido
\gset
SELECT public.anadir_linea_pedido(
    :id_pedido,
    (SELECT min(id_producto_sku) FROM public.producto_sku WHERE id_producto_sku > :sku),
    :nave,
    2
);
SELECT public.anadir_linea_pedido(
    :id_pedido,
    (SELECT max(id_producto_sku) FROM public.producto_sku),
    :nave,
    3
);
SELECT
    CASE WHEN lineas = 3 AND unidades = 6 AND stock = :stock_antes
         THEN 'PASS' ELSE 'FAIL' END AS p5_al_crear,
    lineas, unidades, stock, importe
FROM (
    SELECT
        (SELECT count(*) FROM public.linea_pedido WHERE id_pedido = :id_pedido) AS lineas,
        p.cantidad_total AS unidades,
        p.importe_total AS importe,
        (SELECT sum(cantidad) FROM public.existencias) AS stock
    FROM public.pedidos p
    WHERE p.id_pedido = :id_pedido
) AS t;
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
SELECT
    CASE WHEN stock = :stock_antes - 6 AND marcas = 3
         THEN 'PASS' ELSE 'FAIL' END AS p5_al_confirmar,
    stock, marcas
FROM (
    SELECT
        (SELECT sum(cantidad) FROM public.existencias) AS stock,
        (SELECT count(*) FROM public.linea_pedido
          WHERE id_pedido = :id_pedido AND stock_descontado = true) AS marcas
) AS t;
ROLLBACK;

\echo ''
\echo '--- P6 la cancelacion devuelve el stock, apaga la marca y conserva el importe'
BEGIN;
SELECT sum(cantidad) AS stock_antes FROM public.existencias
\gset
SELECT public.realizar_compra('P6', :cliente_a, :sku, :nave, 3) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
SELECT importe_total AS importe_antes FROM public.pedidos WHERE id_pedido = :id_pedido
\gset
UPDATE public.pedidos SET estado = 'cancelado' WHERE id_pedido = :id_pedido;
SELECT
    CASE WHEN stock = :stock_antes AND NOT marca
              AND importe = :importe_antes AND estado = 'cancelado'
         THEN 'PASS' ELSE 'FAIL' END AS p6,
    stock, marca, importe, estado
FROM (
    SELECT
        (SELECT sum(cantidad) FROM public.existencias) AS stock,
        p.estado AS estado,
        p.importe_total AS importe,
        l.stock_descontado AS marca
    FROM public.pedidos p
    JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido
    WHERE p.id_pedido = :id_pedido
) AS t;

\echo ''
\echo '--- P6b cancelar dos veces no devuelve el stock por duplicado'
UPDATE public.pedidos SET estado = 'cancelado' WHERE id_pedido = :id_pedido;
SELECT
    CASE WHEN sum(cantidad) = :stock_antes THEN 'PASS' ELSE 'FAIL' END AS p6b,
    sum(cantidad) AS stock
FROM public.existencias;
ROLLBACK;

\echo ''
\echo '--- P7 nova_admin confirma y cancela un pedido'
BEGIN;
SELECT sum(cantidad) AS stock_antes FROM public.existencias
\gset
SELECT public.realizar_compra('P7', :cliente_a, :sku, :nave, 2) AS id_pedido
\gset
SET ROLE nova_admin;
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
SELECT sum(cantidad) AS stock_confirmado FROM public.existencias
\gset
UPDATE public.pedidos SET estado = 'cancelado' WHERE id_pedido = :id_pedido;
RESET ROLE;
SELECT
    CASE WHEN :stock_confirmado = :stock_antes - 2
              AND stock = :stock_antes AND NOT marca AND estado = 'cancelado'
         THEN 'PASS' ELSE 'FAIL' END AS p7,
    :stock_confirmado AS stock_tras_confirmar, stock AS stock_tras_cancelar, marca, estado
FROM (
    SELECT
        (SELECT sum(cantidad) FROM public.existencias) AS stock,
        p.estado AS estado,
        l.stock_descontado AS marca
    FROM public.pedidos p
    JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido
    WHERE p.id_pedido = :id_pedido
) AS t;
ROLLBACK;

\echo ''
\echo '--- P8 nova_trabajador confirma y cancela un pedido'
BEGIN;
SELECT sum(cantidad) AS stock_antes FROM public.existencias
\gset
SELECT public.realizar_compra('P8', :cliente_a, :sku, :nave, 2) AS id_pedido
\gset
SET ROLE nova_trabajador;
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
SELECT sum(cantidad) AS stock_confirmado FROM public.existencias
\gset
UPDATE public.pedidos SET estado = 'cancelado' WHERE id_pedido = :id_pedido;
RESET ROLE;
SELECT
    CASE WHEN :stock_confirmado = :stock_antes - 2
              AND stock = :stock_antes AND NOT marca AND estado = 'cancelado'
         THEN 'PASS' ELSE 'FAIL' END AS p8,
    :stock_confirmado AS stock_tras_confirmar, stock AS stock_tras_cancelar, marca, estado
FROM (
    SELECT
        (SELECT sum(cantidad) FROM public.existencias) AS stock,
        p.estado AS estado,
        l.stock_descontado AS marca
    FROM public.pedidos p
    JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido
    WHERE p.id_pedido = :id_pedido
) AS t;
ROLLBACK;

\echo ''
\echo '--- P9 cancelar un pedido que nunca se confirmo no mueve el stock'
BEGIN;
SELECT sum(cantidad) AS stock_antes FROM public.existencias
\gset
SET ROLE nova_trabajador;
UPDATE public.pedidos SET estado = 'cancelado' WHERE referencia = :'ref_demo';
RESET ROLE;
SELECT
    CASE WHEN estado = 'cancelado' AND stock = :stock_antes
         THEN 'PASS' ELSE 'FAIL' END AS p9,
    estado, stock
FROM (
    SELECT
        (SELECT estado FROM public.pedidos WHERE referencia = :'ref_demo') AS estado,
        (SELECT sum(cantidad) FROM public.existencias) AS stock
) AS t;
ROLLBACK;

\echo ''
\echo '--- P9b confirmar un pedido sin existencias se rechaza entero, sin cambios'
\echo '    parciales ni stock negativo (prueba B del enunciado)'
BEGIN;
SELECT sum(cantidad) AS stock_antes FROM public.existencias
\gset
SELECT public.realizar_compra('P9b', :cliente_a, :sku, :nave, 5) AS id_pedido
\gset
SELECT public.anadir_linea_pedido(
    :id_pedido,
    (SELECT min(id_producto_sku) FROM public.producto_sku WHERE id_producto_sku > :sku),
    :nave,
    9999
);
DO $$
BEGIN
    UPDATE public.pedidos SET estado = 'confirmado' WHERE referencia = 'P9b';
    RAISE NOTICE 'FAIL P9b: la base confirmo un pedido sin existencias';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'Stock insuficiente o producto no encontrado' THEN
            RAISE NOTICE 'PASS P9b: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL P9b: error inesperado: %', SQLERRM;
        END IF;
END
$$;
SELECT
    CASE WHEN stock = :stock_antes AND marcas = 0
              AND estado = 'pendiente' AND minimo >= 0
         THEN 'PASS' ELSE 'FAIL' END AS p9b_sin_cambios_parciales,
    stock, marcas, estado, minimo AS stock_minimo
FROM (
    SELECT
        (SELECT sum(cantidad) FROM public.existencias) AS stock,
        (SELECT count(*) FROM public.linea_pedido
          WHERE id_pedido = :id_pedido AND stock_descontado = true) AS marcas,
        (SELECT estado FROM public.pedidos WHERE id_pedido = :id_pedido) AS estado,
        (SELECT min(cantidad) FROM public.existencias) AS minimo
) AS t;
ROLLBACK;

\echo ''
\echo '===== AUDITORIA ====='
\echo ''
\echo '--- P10 el alta, la confirmacion y la cancelacion dejan rastro en log_eventos'
\echo '    (se mide la DIFERENCIA de eventos, no el total, para que la prueba'
\echo '     siga valiendo si el registro ya tenia eventos de antes)'
SELECT
    (SELECT count(*) FROM public.log_eventos WHERE tabla_afectada = 'existencias') AS stock_antes,
    (SELECT count(*) FROM public.log_eventos WHERE tabla_afectada = 'pedidos') AS pedido_antes
\gset
BEGIN;
SELECT public.realizar_compra('P10', :cliente_a, :sku, :nave, 2, :usuario) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
UPDATE public.pedidos SET estado = 'cancelado' WHERE id_pedido = :id_pedido;
SELECT
    CASE WHEN eventos_stock - :stock_antes = 2
              AND eventos_pedido - :pedido_antes = 3
         THEN 'PASS' ELSE 'FAIL' END AS p10,
    eventos_stock - :stock_antes AS nuevos_de_stock,
    eventos_pedido - :pedido_antes AS nuevos_de_pedido
FROM (
    SELECT
        (SELECT count(*) FROM public.log_eventos WHERE tabla_afectada = 'existencias') AS eventos_stock,
        (SELECT count(*) FROM public.log_eventos WHERE tabla_afectada = 'pedidos') AS eventos_pedido
) AS t;
SELECT tabla_afectada, accion, id_usuario, detalle
FROM public.log_eventos
WHERE detalle LIKE '%P10%' OR tabla_afectada = 'existencias'
ORDER BY id_evento;
ROLLBACK;

\echo ''
\echo '--- P11 el registro guarda el OPERADOR autenticado, no el usuario del pedido'
\echo '    (el pedido se asigna a tienda.demo y la operacion la ejecuta taller.demo)'
BEGIN;
SELECT gen_random_uuid()::text AS clave_p11
\gset
SELECT public.establecer_password('taller.demo', :'clave_p11');
SELECT public.iniciar_sesion('taller.demo', :'clave_p11') AS operador
\gset
SELECT id_usuario AS duenyo_pedido FROM public.usuarios WHERE username = 'tienda.demo'
\gset
SELECT public.realizar_compra('P11', :cliente_a, :sku, :nave, 1, :duenyo_pedido) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
SELECT
    CASE WHEN id_usuario = :operador AND id_usuario <> :duenyo_pedido
         THEN 'PASS' ELSE 'FAIL' END AS p11,
    id_usuario AS operador_registrado,
    :duenyo_pedido AS usuario_del_pedido,
    detalle
FROM public.log_eventos
WHERE tabla_afectada = 'pedidos'
ORDER BY id_evento DESC
LIMIT 1;
ROLLBACK;

\echo ''
\echo '--- P11b sin sesion iniciada, el registro queda sin operador'
BEGIN;
SELECT id_usuario AS duenyo_pedido FROM public.usuarios WHERE username = 'tienda.demo'
\gset
SELECT public.realizar_compra('P11b', :cliente_a, :sku, :nave, 1, :duenyo_pedido) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
SELECT
    CASE WHEN id_usuario IS NULL THEN 'PASS' ELSE 'FAIL' END AS p11b,
    id_usuario AS operador_registrado,
    detalle
FROM public.log_eventos
WHERE tabla_afectada = 'pedidos'
ORDER BY id_evento DESC
LIMIT 1;
ROLLBACK;

\echo ''
\echo '--- P11c la auditoria registra el alta del pedido y la baja logica al cancelar'
\echo '    (tambien por diferencia antes/despues)'
SELECT
    (SELECT count(*) FROM public.log_eventos WHERE accion = 'ALTA') AS altas_antes,
    (SELECT count(*) FROM public.log_eventos WHERE accion = 'BAJA_LOGICA') AS bajas_antes,
    (SELECT count(*) FROM public.log_eventos WHERE accion = 'CAMBIO_STOCK') AS stock_antes_p11c
\gset
BEGIN;
SELECT public.realizar_compra('P11c', :cliente_a, :sku, :nave, 1) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
UPDATE public.pedidos SET estado = 'cancelado' WHERE id_pedido = :id_pedido;
SELECT
    CASE WHEN altas - :altas_antes = 1
              AND bajas - :bajas_antes = 1
              AND cambios_stock - :stock_antes_p11c = 2
         THEN 'PASS' ELSE 'FAIL' END AS p11c,
    altas - :altas_antes AS nuevas_altas,
    bajas - :bajas_antes AS nuevas_bajas,
    cambios_stock - :stock_antes_p11c AS nuevos_cambios_stock
FROM (
    SELECT
        (SELECT count(*) FROM public.log_eventos WHERE accion = 'ALTA') AS altas,
        (SELECT count(*) FROM public.log_eventos WHERE accion = 'BAJA_LOGICA') AS bajas,
        (SELECT count(*) FROM public.log_eventos WHERE accion = 'CAMBIO_STOCK') AS cambios_stock
) AS t;
ROLLBACK;

\echo ''
\echo '--- P11d dar de baja un modelo queda registrado como baja logica'
BEGIN;
UPDATE public.modelos SET activo = false WHERE nombre = 'NOVA Aura';
SELECT
    CASE WHEN count(*) = 1 THEN 'PASS' ELSE 'FAIL' END AS p11d,
    count(*) AS eventos,
    max(detalle) AS detalle
FROM public.log_eventos
WHERE tabla_afectada = 'modelos' AND accion = 'BAJA_LOGICA';
ROLLBACK;

\echo ''
\echo '===== COMPRAS PERSONALIZADAS X-NOVA ====='
\echo ''
\echo '--- P12 compra X-NOVA (esperado importe 12000, sin SKU, sin nave, sin tocar el stock)'
BEGIN;
SELECT sum(cantidad) AS stock_antes FROM public.existencias
\gset
INSERT INTO public.configuraciones_xnova (
    id_cliente, talla_referencia, color_principal, material, tipo_suela
)
VALUES (:cliente_a, 42, 'Negro', 'Malla tecnica', 'Goma reciclada')
RETURNING id_configuracion AS configuracion
\gset
SELECT public.realizar_compra_xnova('P12', :configuracion) AS id_pedido
\gset
SELECT
    CASE WHEN importe = 12000.00 AND sku IS NULL AND nave IS NULL
              AND NOT marca AND stock = :stock_antes
         THEN 'PASS' ELSE 'FAIL' END AS p12,
    importe, sku, nave, marca, stock
FROM (
    SELECT
        p.importe_total AS importe,
        l.id_producto_sku AS sku,
        l.id_nave AS nave,
        l.stock_descontado AS marca,
        (SELECT sum(cantidad) FROM public.existencias) AS stock
    FROM public.pedidos p
    JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido
    WHERE p.id_pedido = :id_pedido
) AS t;

\echo ''
\echo '--- P13 cancelar un X-NOVA no mueve el stock'
UPDATE public.pedidos SET estado = 'cancelado' WHERE id_pedido = :id_pedido;
SELECT
    CASE WHEN stock = :stock_antes AND estado = 'cancelado'
         THEN 'PASS' ELSE 'FAIL' END AS p13,
    stock, estado
FROM (
    SELECT
        (SELECT sum(cantidad) FROM public.existencias) AS stock,
        (SELECT estado FROM public.pedidos WHERE id_pedido = :id_pedido) AS estado
) AS t;
ROLLBACK;

\echo ''
\echo '--- P14 la consulta 1 incluye las ventas X-NOVA y cuadra con las lineas'
BEGIN;
INSERT INTO public.configuraciones_xnova (
    id_cliente, talla_referencia, color_principal, material, tipo_suela
)
VALUES (:cliente_b, 43, 'Blanco', 'Piel sintetica', 'Goma')
RETURNING id_configuracion AS configuracion
\gset
SELECT public.realizar_compra_xnova('P14', :configuracion);
WITH consulta_uno AS (
    SELECT
        COALESCE(m.nombre, 'X-NOVA') AS modelo,
        SUM(l.subtotal) AS importe
    FROM public.pedidos p
    JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido
    LEFT JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
    LEFT JOIN public.variantes v ON v.id_variante = s.id_variante
    LEFT JOIN public.modelos m ON m.id_modelo = v.id_modelo
    WHERE p.estado <> 'cancelado'
    GROUP BY COALESCE(m.nombre, 'X-NOVA')
)
SELECT
    CASE WHEN filas_xnova = 1 AND suma_consulta = suma_lineas
         THEN 'PASS' ELSE 'FAIL' END AS p14,
    filas_xnova, suma_consulta, suma_lineas
FROM (
    SELECT
        (SELECT count(*) FROM consulta_uno WHERE modelo = 'X-NOVA') AS filas_xnova,
        (SELECT sum(importe) FROM consulta_uno) AS suma_consulta,
        (SELECT sum(l.subtotal)
           FROM public.linea_pedido l
           JOIN public.pedidos p ON p.id_pedido = l.id_pedido
          WHERE p.estado <> 'cancelado') AS suma_lineas
) AS t;
ROLLBACK;

\echo ''
\echo '===== OPERACIONES QUE DEBEN SER RECHAZADAS ====='
\echo ''
\echo '--- E1 cambiar la cantidad de una linea de un pedido ya confirmado'
BEGIN;
SELECT public.realizar_compra('E1', :cliente_a, :sku, :nave, 2) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
DO $$
BEGIN
    UPDATE public.linea_pedido SET cantidad = 5
    WHERE id_pedido = (SELECT id_pedido FROM public.pedidos WHERE referencia = 'E1');
    RAISE NOTICE 'FAIL E1: la base acepto el cambio';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'No se puede modificar una compra registrada' THEN
            RAISE NOTICE 'PASS E1: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL E1: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- E2 cambiar el precio de una linea de un pedido ya confirmado'
BEGIN;
SELECT public.realizar_compra('E2', :cliente_a, :sku, :nave, 2) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
DO $$
BEGIN
    UPDATE public.linea_pedido SET precio_unitario = 1
    WHERE id_pedido = (SELECT id_pedido FROM public.pedidos WHERE referencia = 'E2');
    RAISE NOTICE 'FAIL E2: la base acepto el cambio';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'No se puede modificar una compra registrada' THEN
            RAISE NOTICE 'PASS E2: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL E2: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- E3 borrar una linea cuyo stock ya se ha descontado'
BEGIN;
SELECT public.realizar_compra('E3', :cliente_a, :sku, :nave, 2) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
DO $$
BEGIN
    DELETE FROM public.linea_pedido
    WHERE id_pedido = (SELECT id_pedido FROM public.pedidos WHERE referencia = 'E3');
    RAISE NOTICE 'FAIL E3: la base acepto el borrado';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'No se puede eliminar esta linea de pedido' THEN
            RAISE NOTICE 'PASS E3: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL E3: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- E4 apagar a mano la marca de stock de un pedido confirmado'
BEGIN;
SELECT public.realizar_compra('E4', :cliente_a, :sku, :nave, 2) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
DO $$
BEGIN
    UPDATE public.linea_pedido SET stock_descontado = false
    WHERE id_pedido = (SELECT id_pedido FROM public.pedidos WHERE referencia = 'E4');
    RAISE NOTICE 'FAIL E4: la base acepto el cambio';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'Cambio de stock no permitido' THEN
            RAISE NOTICE 'PASS E4: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL E4: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- E4b encender a mano la marca de stock sin confirmar el pedido'
BEGIN;
SELECT public.realizar_compra('E4b', :cliente_a, :sku, :nave, 2) AS id_pedido
\gset
DO $$
BEGIN
    UPDATE public.linea_pedido SET stock_descontado = true
    WHERE id_pedido = (SELECT id_pedido FROM public.pedidos WHERE referencia = 'E4b');
    RAISE NOTICE 'FAIL E4b: la base acepto encender la marca sin confirmar';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'Cambio de stock no permitido' THEN
            RAISE NOTICE 'PASS E4b: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL E4b: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- E5 anadir una linea a un pedido ya confirmado'
BEGIN;
SELECT public.realizar_compra('E5', :cliente_a, :sku, :nave, 1) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
DO $$
BEGIN
    PERFORM public.anadir_linea_pedido(
        (SELECT id_pedido FROM public.pedidos WHERE referencia = 'E5'),
        (SELECT min(id_producto_sku) FROM public.producto_sku),
        (SELECT min(id_nave) FROM public.nave),
        1);
    RAISE NOTICE 'FAIL E5: la base acepto la linea';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'Solo se pueden anadir lineas a un pedido pendiente' THEN
            RAISE NOTICE 'PASS E5: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL E5: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;
\echo ''
\echo '--- E6 repetir una referencia de pedido que ya existe'
BEGIN;
DO $$
BEGIN
    PERFORM public.realizar_compra(
        (SELECT referencia FROM public.pedidos ORDER BY id_pedido LIMIT 1),
        (SELECT min(id_cliente) FROM public.clientes),
        (SELECT min(id_producto_sku) FROM public.producto_sku),
        (SELECT min(id_nave) FROM public.nave),
        1);
    RAISE NOTICE 'FAIL E6: la base acepto la referencia repetida';
EXCEPTION
    WHEN others THEN
        IF SQLSTATE = '23505' THEN
            RAISE NOTICE 'PASS E6: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL E6: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- E7 reactivar un pedido cancelado'
BEGIN;
SELECT public.realizar_compra('E7', :cliente_a, :sku, :nave, 1) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'cancelado' WHERE id_pedido = :id_pedido;
DO $$
BEGIN
    UPDATE public.pedidos SET estado = 'pendiente' WHERE referencia = 'E7';
    RAISE NOTICE 'FAIL E7: la base acepto la reactivacion';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'No se puede reactivar un pedido cancelado' THEN
            RAISE NOTICE 'PASS E7: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL E7: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- E8 comprar cantidad cero'
BEGIN;
DO $$
BEGIN
    PERFORM public.realizar_compra('E8',
        (SELECT min(id_cliente) FROM public.clientes),
        (SELECT min(id_producto_sku) FROM public.producto_sku),
        (SELECT min(id_nave) FROM public.nave),
        0);
    RAISE NOTICE 'FAIL E8: la base acepto la cantidad cero';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'La cantidad debe ser mayor que cero' THEN
            RAISE NOTICE 'PASS E8: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL E8: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- E9 anadir una linea a un pedido ya cancelado'
BEGIN;
SELECT public.realizar_compra('E9', :cliente_a, :sku, :nave, 1) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'cancelado' WHERE id_pedido = :id_pedido;
DO $$
BEGIN
    PERFORM public.anadir_linea_pedido(
        (SELECT id_pedido FROM public.pedidos WHERE referencia = 'E9'),
        (SELECT min(id_producto_sku) FROM public.producto_sku),
        (SELECT min(id_nave) FROM public.nave),
        1);
    RAISE NOTICE 'FAIL E9: la base acepto la linea';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'Solo se pueden anadir lineas a un pedido pendiente' THEN
            RAISE NOTICE 'PASS E9: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL E9: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- E10 usar dos veces la misma configuracion X-NOVA'
BEGIN;
INSERT INTO public.configuraciones_xnova (
    id_cliente, talla_referencia, color_principal, material, tipo_suela
)
VALUES (:cliente_a, 41, 'Gris', 'Malla', 'Goma')
RETURNING id_configuracion AS configuracion
\gset
SELECT public.realizar_compra_xnova('E10-primera', :configuracion);
DO $$
BEGIN
    PERFORM public.realizar_compra_xnova('E10-segunda',
        (SELECT max(id_configuracion) FROM public.configuraciones_xnova));
    RAISE NOTICE 'FAIL E10: la base reutilizo la configuracion';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'Configuracion X-NOVA no disponible' THEN
            RAISE NOTICE 'PASS E10: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL E10: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- E11 tras un error, ROLLBACK deja el stock intacto y sin pedidos nuevos'
SELECT sum(cantidad) AS stock_antes FROM public.existencias
\gset
SELECT count(*) AS pedidos_antes FROM public.pedidos
\gset
SELECT count(*) AS eventos_antes FROM public.log_eventos
\gset
BEGIN;
SELECT public.realizar_compra('E11', :cliente_a, :sku, :nave, 2) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
DO $$
BEGIN
    PERFORM public.anadir_linea_pedido(
        (SELECT id_pedido FROM public.pedidos WHERE referencia = 'E11'),
        (SELECT min(id_producto_sku) FROM public.producto_sku),
        (SELECT min(id_nave) FROM public.nave),
        1);
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'error provocado a proposito: %', SQLERRM;
END
$$;
ROLLBACK;
SELECT
    CASE WHEN stock = :stock_antes AND pedidos = :pedidos_antes
              AND eventos = :eventos_antes
         THEN 'PASS' ELSE 'FAIL' END AS e11,
    stock, pedidos, eventos
FROM (
    SELECT
        (SELECT sum(cantidad) FROM public.existencias) AS stock,
        (SELECT count(*) FROM public.pedidos) AS pedidos,
        (SELECT count(*) FROM public.log_eventos) AS eventos
) AS t;

\echo ''
\echo '===== PERMISOS DE LOS TRES ROLES ====='
\echo ''
\echo 'Las pruebas que deben fallar no buscan identificadores: PostgreSQL comprueba'
\echo 'el permiso sobre la tabla antes de mirar las filas.'
\echo ''
\echo '--- S1 nova_cliente ve el catalogo (permitido)'
BEGIN;
SET ROLE nova_cliente;
DO $$
DECLARE
    v_modelos integer;
BEGIN
    SELECT count(*) INTO v_modelos FROM public.modelos;
    IF v_modelos = 7 THEN
        RAISE NOTICE 'PASS S1: el cliente ve % modelos', v_modelos;
    ELSE
        RAISE NOTICE 'FAIL S1: ve % modelos', v_modelos;
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'FAIL S1: %', SQLERRM;
END
$$;
RESET ROLE;
ROLLBACK;

\echo ''
\echo '--- S2 nova_cliente NO ve los pedidos'
BEGIN;
SET ROLE nova_cliente;
DO $$
DECLARE
    v_pedidos integer;
BEGIN
    SELECT count(*) INTO v_pedidos FROM public.pedidos;
    RAISE NOTICE 'FAIL S2: el cliente leyo % pedidos', v_pedidos;
EXCEPTION
    WHEN others THEN
        IF SQLSTATE = '42501' THEN
            RAISE NOTICE 'PASS S2: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL S2: error inesperado: %', SQLERRM;
        END IF;
END
$$;
RESET ROLE;
ROLLBACK;

\echo ''
\echo '--- S3 nova_cliente compra llamando a la funcion (permitido)'
BEGIN;
SET ROLE nova_cliente;
SELECT public.realizar_compra('S3', :cliente_a, :sku, :nave, 1) AS id_pedido
\gset
RESET ROLE;
SELECT
    CASE WHEN count(*) = 1 THEN 'PASS' ELSE 'FAIL' END AS s3,
    count(*) AS pedidos_creados
FROM public.pedidos
WHERE id_pedido = :id_pedido;
ROLLBACK;

\echo ''
\echo '--- S4 nova_cliente NO tiene permiso para llamar a descontar_stock'
SELECT
    CASE WHEN NOT has_function_privilege(
                   'nova_cliente',
                   'public.descontar_stock(integer, integer, integer)',
                   'EXECUTE')
         THEN 'PASS' ELSE 'FAIL' END AS s4,
    has_function_privilege(
        'nova_cliente',
        'public.descontar_stock(integer, integer, integer)',
        'EXECUTE') AS puede_ejecutar;

\echo ''
\echo '--- S4b al intentarlo de verdad, nova_cliente recibe un error'
BEGIN;
SET ROLE nova_cliente;
SELECT public.descontar_stock(:sku, :nave, 1);
ROLLBACK;
RESET ROLE;

\echo ''
\echo '--- S5 nova_admin NO puede insertar lineas de pedido a mano'
BEGIN;
SET ROLE nova_admin;
DO $$
BEGIN
    INSERT INTO public.linea_pedido (
        id_pedido, id_producto_sku, id_nave, cantidad, precio_unitario, subtotal
    )
    VALUES (
        (SELECT min(id_pedido) FROM public.pedidos),
        (SELECT min(id_producto_sku) FROM public.producto_sku),
        (SELECT min(id_nave) FROM public.nave),
        1, 10, 0
    );
    RAISE NOTICE 'FAIL S5: el administrador inserto una linea a mano';
EXCEPTION
    WHEN others THEN
        IF SQLSTATE = '42501' THEN
            RAISE NOTICE 'PASS S5: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL S5: error inesperado: %', SQLERRM;
        END IF;
END
$$;
RESET ROLE;
ROLLBACK;

\echo ''
\echo '--- S6 nova_admin ve las configuraciones X-NOVA y la auditoria (permitido)'
BEGIN;
SET ROLE nova_admin;
DO $$
DECLARE
    v_configuraciones integer;
    v_eventos integer;
BEGIN
    SELECT count(*) INTO v_configuraciones FROM public.configuraciones_xnova;
    SELECT count(*) INTO v_eventos FROM public.log_eventos;
    RAISE NOTICE 'PASS S6: lee % configuraciones y % eventos', v_configuraciones, v_eventos;
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'FAIL S6: %', SQLERRM;
END
$$;
RESET ROLE;
ROLLBACK;

\echo ''
\echo '--- S7 nova_trabajador cambia el estado de un pedido (permitido)'
BEGIN;
SET ROLE nova_trabajador;
DO $$
BEGIN
    UPDATE public.pedidos SET estado = 'en_preparacion'
    WHERE id_pedido = (SELECT min(id_pedido) FROM public.pedidos);
    RAISE NOTICE 'PASS S7: el trabajador cambio el estado';
EXCEPTION
    WHEN others THEN
        RAISE NOTICE 'FAIL S7: %', SQLERRM;
END
$$;
RESET ROLE;
ROLLBACK;

\echo ''
\echo '--- S8 nova_trabajador NO puede cambiar el importe de un pedido'
BEGIN;
SET ROLE nova_trabajador;
DO $$
BEGIN
    UPDATE public.pedidos SET importe_total = 0
    WHERE estado = 'pendiente';
    RAISE NOTICE 'FAIL S8: el trabajador cambio el importe';
EXCEPTION
    WHEN others THEN
        IF SQLSTATE = '42501' THEN
            RAISE NOTICE 'PASS S8: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL S8: error inesperado: %', SQLERRM;
        END IF;
END
$$;
RESET ROLE;
ROLLBACK;

\echo ''
\echo '--- S9 nova_trabajador NO puede comprar'
BEGIN;
SET ROLE nova_trabajador;
DO $$
BEGIN
    PERFORM public.realizar_compra('S9',
        (SELECT min(id_cliente) FROM public.clientes),
        (SELECT min(id_producto_sku) FROM public.producto_sku),
        (SELECT min(id_nave) FROM public.nave),
        1);
    RAISE NOTICE 'FAIL S9: el trabajador compro';
EXCEPTION
    WHEN others THEN
        IF SQLSTATE = '42501' THEN
            RAISE NOTICE 'PASS S9: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL S9: error inesperado: %', SQLERRM;
        END IF;
END
$$;
RESET ROLE;
ROLLBACK;

\echo ''
\echo '--- S10 nova_cliente NO puede cancelar un pedido'
BEGIN;
SET ROLE nova_cliente;
DO $$
BEGIN
    UPDATE public.pedidos SET estado = 'cancelado'
    WHERE estado = 'pendiente';
    RAISE NOTICE 'FAIL S10: el cliente cancelo un pedido';
EXCEPTION
    WHEN others THEN
        IF SQLSTATE = '42501' THEN
            RAISE NOTICE 'PASS S10: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL S10: error inesperado: %', SQLERRM;
        END IF;
END
$$;
RESET ROLE;
ROLLBACK;

\echo ''
\echo '===== AUTENTICACION DE LA APLICACION ====='
\echo ''
\echo 'Las contrasenas de prueba se generan al azar dentro de la transaccion y'
\echo 'desaparecen con el ROLLBACK, asi que no hay ninguna clave en el archivo.'
\echo ''
\echo '--- A1 las cuentas de demostracion llegan sin contrasena utilizable'
SELECT
    CASE WHEN count(*) = 3 THEN 'PASS' ELSE 'FAIL' END AS a1,
    count(*) AS cuentas_sin_contrasena
FROM public.usuarios
WHERE password_hash = '!';

\echo ''
\echo '--- A2 no se puede entrar en una cuenta sin contrasena establecida'
BEGIN;
DO $$
BEGIN
    PERFORM public.iniciar_sesion('admin.demo', 'loquesea');
    RAISE NOTICE 'FAIL A2: entro sin contrasena';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'La cuenta no tiene contrasena establecida' THEN
            RAISE NOTICE 'PASS A2: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL A2: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- A3 con la contrasena correcta el login devuelve el id del usuario'
BEGIN;
SELECT gen_random_uuid()::text AS clave_a3
\gset
SELECT public.establecer_password('admin.demo', :'clave_a3');
SELECT
    CASE WHEN public.iniciar_sesion('admin.demo', :'clave_a3') = id_usuario
         THEN 'PASS' ELSE 'FAIL' END AS a3,
    id_usuario, username
FROM public.usuarios
WHERE username = 'admin.demo';
ROLLBACK;

\echo ''
\echo '--- A4 con la contrasena incorrecta el login falla'
BEGIN;
SELECT gen_random_uuid()::text AS clave_a4
\gset
SELECT public.establecer_password('admin.demo', :'clave_a4');
DO $$
BEGIN
    PERFORM public.iniciar_sesion('admin.demo', 'contrasena-que-no-es');
    RAISE NOTICE 'FAIL A4: entro con la contrasena incorrecta';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'Usuario o contrasena incorrectos' THEN
            RAISE NOTICE 'PASS A4: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL A4: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- A5 un usuario que no existe da el mismo error, sin pistas'
BEGIN;
DO $$
BEGIN
    PERFORM public.iniciar_sesion('no.existe', 'loquesea');
    RAISE NOTICE 'FAIL A5: no dio error';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'Usuario o contrasena incorrectos' THEN
            RAISE NOTICE 'PASS A5: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL A5: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- A6 la contrasena guardada no es el texto que se ha escrito'
BEGIN;
SELECT gen_random_uuid()::text AS clave_a6
\gset
SELECT public.establecer_password('admin.demo', :'clave_a6');
SELECT
    CASE WHEN password_hash <> :'clave_a6' AND left(password_hash, 4) = '$2a$'
         THEN 'PASS' ELSE 'FAIL' END AS a6,
    left(password_hash, 7) AS comienzo_del_hash,
    length(password_hash) AS longitud
FROM public.usuarios
WHERE username = 'admin.demo';
ROLLBACK;

\echo ''
\echo '--- A7 dos usuarios con la misma contrasena tienen hashes distintos'
BEGIN;
SELECT gen_random_uuid()::text AS clave_a7
\gset
SELECT public.establecer_password('admin.demo', :'clave_a7');
SELECT public.establecer_password('taller.demo', :'clave_a7');
SELECT
    CASE WHEN count(DISTINCT password_hash) = 2 THEN 'PASS' ELSE 'FAIL' END AS a7,
    count(DISTINCT password_hash) AS hashes_distintos
FROM public.usuarios
WHERE username IN ('admin.demo', 'taller.demo');
ROLLBACK;

\echo ''
\echo '--- A8 una contrasena demasiado corta se rechaza'
BEGIN;
DO $$
BEGIN
    PERFORM public.establecer_password('admin.demo', 'corta');
    RAISE NOTICE 'FAIL A8: acepto una contrasena de 5 caracteres';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'La contrasena debe tener al menos 8 caracteres' THEN
            RAISE NOTICE 'PASS A8: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL A8: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- A9 solo nova_admin puede cambiar contrasenas'
SELECT
    CASE WHEN admin_puede AND NOT trabajador_puede AND NOT cliente_puede
         THEN 'PASS' ELSE 'FAIL' END AS a9,
    admin_puede, trabajador_puede, cliente_puede
FROM (
    SELECT
        has_function_privilege('nova_admin',
            'public.establecer_password(character varying, text)', 'EXECUTE') AS admin_puede,
        has_function_privilege('nova_trabajador',
            'public.establecer_password(character varying, text)', 'EXECUTE') AS trabajador_puede,
        has_function_privilege('nova_cliente',
            'public.establecer_password(character varying, text)', 'EXECUTE') AS cliente_puede
) AS t;

\echo ''
\echo '--- A10 los tres roles pueden iniciar sesion'
SELECT
    CASE WHEN admin_puede AND trabajador_puede AND cliente_puede
         THEN 'PASS' ELSE 'FAIL' END AS a10,
    admin_puede, trabajador_puede, cliente_puede
FROM (
    SELECT
        has_function_privilege('nova_admin',
            'public.iniciar_sesion(character varying, text)', 'EXECUTE') AS admin_puede,
        has_function_privilege('nova_trabajador',
            'public.iniciar_sesion(character varying, text)', 'EXECUTE') AS trabajador_puede,
        has_function_privilege('nova_cliente',
            'public.iniciar_sesion(character varying, text)', 'EXECUTE') AS cliente_puede
) AS t;

\echo ''
\echo '--- A11 solo nova_admin ve la tabla usuarios, y nadie ve password_hash'
SELECT
    CASE WHEN admin_ve_usuario AND admin_edita_activo
              AND NOT admin_ve_hash
              AND NOT trabajador_ve_usuario AND NOT cliente_ve_usuario
         THEN 'PASS' ELSE 'FAIL' END AS a11,
    admin_ve_usuario, admin_edita_activo, admin_ve_hash,
    trabajador_ve_usuario, cliente_ve_usuario
FROM (
    SELECT
        has_column_privilege('nova_admin', 'public.usuarios', 'username', 'SELECT') AS admin_ve_usuario,
        has_column_privilege('nova_admin', 'public.usuarios', 'activo', 'UPDATE') AS admin_edita_activo,
        has_column_privilege('nova_admin', 'public.usuarios', 'password_hash', 'SELECT') AS admin_ve_hash,
        has_column_privilege('nova_trabajador', 'public.usuarios', 'username', 'SELECT') AS trabajador_ve_usuario,
        has_column_privilege('nova_cliente', 'public.usuarios', 'username', 'SELECT') AS cliente_ve_usuario
) AS t;

\echo ''
\echo '--- A11b el hash de la contrasena es la clave de la firma de sesion,'
\echo '    asi que NINGUN rol de la aplicacion puede leerlo'
SELECT
    CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS a11b,
    count(*) AS roles_que_leen_el_hash
FROM pg_roles r
WHERE r.rolname LIKE 'nova\_%'
  AND has_column_privilege(r.rolname, 'public.usuarios', 'password_hash', 'SELECT');

\echo ''
\echo '--- A12 el usuario de sesion no sobrevive al final de la transaccion'
BEGIN;
SELECT gen_random_uuid()::text AS clave_a12
\gset
SELECT public.establecer_password('admin.demo', :'clave_a12');
SELECT public.iniciar_sesion('admin.demo', :'clave_a12');
SELECT
    CASE WHEN public.usuario_sesion() IS NOT NULL THEN 'PASS' ELSE 'FAIL' END AS a12_dentro,
    public.usuario_sesion() AS operador;
ROLLBACK;
SELECT
    CASE WHEN public.usuario_sesion() IS NULL THEN 'PASS' ELSE 'FAIL' END AS a12_despues,
    public.usuario_sesion() AS operador;

\echo ''
\echo '--- A13 el administrador puede gestionar usuarios, roles y personal'
SELECT
    CASE WHEN usuarios_crear AND usuarios_editar AND usuarios_password
              AND roles_crear AND personal_crear
         THEN 'PASS' ELSE 'FAIL' END AS a13,
    usuarios_crear, usuarios_editar, usuarios_password, roles_crear, personal_crear
FROM (
    SELECT
        has_function_privilege('nova_admin',
            'public.crear_usuario(character varying, character varying)', 'EXECUTE') AS usuarios_crear,
        has_column_privilege('nova_admin', 'public.usuarios', 'id_rol', 'UPDATE') AS usuarios_editar,
        has_function_privilege('nova_admin',
            'public.establecer_password(character varying, text)', 'EXECUTE') AS usuarios_password,
        has_table_privilege('nova_admin', 'public.roles', 'INSERT') AS roles_crear,
        has_table_privilege('nova_admin', 'public.personal', 'INSERT') AS personal_crear
) AS t;

\echo ''
\echo '--- A13b el administrador crea un usuario y llega sin contrasena utilizable'
BEGIN;
SET ROLE nova_admin;
SELECT public.crear_usuario('nuevo.demo', 'comercial') AS id_nuevo
\gset
RESET ROLE;
SELECT
    CASE WHEN total = 4 AND hash = '!' AND activo THEN 'PASS' ELSE 'FAIL' END AS a13b,
    total, hash AS contrasena, activo
FROM (
    SELECT
        (SELECT count(*) FROM public.usuarios) AS total,
        (SELECT password_hash FROM public.usuarios WHERE id_usuario = :id_nuevo) AS hash,
        (SELECT activo FROM public.usuarios WHERE id_usuario = :id_nuevo) AS activo
) AS t;
ROLLBACK;

\echo ''
\echo '--- A13c el administrador NO puede escribir password_hash a mano'
BEGIN;
SET ROLE nova_admin;
DO $$
BEGIN
    UPDATE public.usuarios SET password_hash = 'lo-que-sea'
    WHERE username = 'taller.demo';
    RAISE NOTICE 'FAIL A13c: el administrador escribio el hash a mano';
EXCEPTION
    WHEN others THEN
        IF SQLSTATE = '42501' THEN
            RAISE NOTICE 'PASS A13c: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL A13c: error inesperado: %', SQLERRM;
        END IF;
END
$$;
RESET ROLE;
ROLLBACK;

\echo ''
\echo '===== FALSIFICACION DE LA IDENTIDAD DE SESION ====='
\echo ''
\echo 'nova.id_usuario es un parametro que cualquier rol puede escribir con SET o'
\echo 'set_config: PostgreSQL no deja revocar ese permiso. Por eso el valor va'
\echo 'firmado y usuario_sesion() comprueba la firma antes de devolver nada.'
\echo ''
\echo '--- F1 poner el id a pelo no da sesion'
BEGIN;
SET ROLE nova_trabajador;
SELECT set_config('nova.id_usuario', '1', true);
SELECT
    CASE WHEN public.usuario_sesion() IS NULL THEN 'PASS' ELSE 'FAIL' END AS f1,
    public.usuario_sesion() AS operador;
RESET ROLE;
ROLLBACK;

\echo ''
\echo '--- F2 inventarse la firma tampoco'
BEGIN;
SET ROLE nova_trabajador;
SELECT set_config('nova.id_usuario', '1:firmainventada', true);
SELECT
    CASE WHEN public.usuario_sesion() IS NULL THEN 'PASS' ELSE 'FAIL' END AS f2,
    public.usuario_sesion() AS operador;
RESET ROLE;
ROLLBACK;

\echo ''
\echo '--- F3 una operacion con la identidad falsificada queda SIN operador,'
\echo '    no con el operador falso'
BEGIN;
SELECT id_usuario AS id_admin FROM public.usuarios WHERE username = 'admin.demo'
\gset
SET ROLE nova_trabajador;
SELECT set_config('nova.id_usuario', :'id_admin', true);
UPDATE public.pedidos SET estado = 'en_preparacion'
WHERE id_pedido = (SELECT min(id_pedido) FROM public.pedidos);
RESET ROLE;
SELECT
    CASE WHEN id_usuario IS NULL THEN 'PASS' ELSE 'FAIL' END AS f3,
    id_usuario AS operador_registrado,
    :id_admin AS operador_que_se_intento_falsificar
FROM public.log_eventos
ORDER BY id_evento DESC
LIMIT 1;
ROLLBACK;

\echo ''
\echo '--- F4 reusar la firma de otro usuario no sirve'
BEGIN;
SELECT gen_random_uuid()::text AS clave_f4
\gset
SELECT public.establecer_password('taller.demo', :'clave_f4');
SELECT public.iniciar_sesion('taller.demo', :'clave_f4');
SELECT current_setting('nova.id_usuario') AS testigo_de_taller
\gset
SELECT id_usuario AS id_admin_f4 FROM public.usuarios WHERE username = 'admin.demo'
\gset
SELECT set_config('nova.id_usuario',
    :'id_admin_f4' || ':' || split_part(:'testigo_de_taller', ':', 2), true);
SELECT
    CASE WHEN public.usuario_sesion() IS NULL THEN 'PASS' ELSE 'FAIL' END AS f4,
    public.usuario_sesion() AS operador;
ROLLBACK;

\echo ''
\echo '--- A14 el administrador puede desactivar un usuario y el resto se conserva'
BEGIN;
SET ROLE nova_admin;
UPDATE public.usuarios SET activo = false WHERE username = 'taller.demo';
RESET ROLE;
SELECT
    CASE WHEN inactivos = 1 AND total = 3 THEN 'PASS' ELSE 'FAIL' END AS a14,
    inactivos, total
FROM (
    SELECT
        (SELECT count(*) FROM public.usuarios WHERE activo = false) AS inactivos,
        (SELECT count(*) FROM public.usuarios) AS total
) AS t;
ROLLBACK;

\echo ''
\echo '--- A15 un usuario desactivado no puede iniciar sesion'
BEGIN;
SELECT gen_random_uuid()::text AS clave_a15
\gset
SELECT public.establecer_password('taller.demo', :'clave_a15');
UPDATE public.usuarios SET activo = false WHERE username = 'taller.demo';
DO $$
BEGIN
    PERFORM public.iniciar_sesion('taller.demo', 'da-igual-la-clave');
    RAISE NOTICE 'FAIL A15: entro un usuario desactivado';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'Usuario o contrasena incorrectos' THEN
            RAISE NOTICE 'PASS A15: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL A15: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '===== AUTORIZACION: IDENTIDAD NO ES PERMISO ====='
\echo ''
\echo 'Una identidad bien registrada no autoriza nada por si sola. Estas pruebas'
\echo 'separan lo que protege PostgreSQL de lo que tiene que comprobar Java.'
\echo ''
\echo '--- G1 un usuario desactivado NO conserva su sesion anterior'
BEGIN;
SELECT gen_random_uuid()::text AS clave_g1
\gset
SELECT public.establecer_password('taller.demo', :'clave_g1');
SELECT public.iniciar_sesion('taller.demo', :'clave_g1');
SELECT current_setting('nova.id_usuario') AS testigo_g1
\gset
UPDATE public.usuarios SET activo = false WHERE username = 'taller.demo';
SELECT set_config('nova.id_usuario', :'testigo_g1', true);
SELECT
    CASE WHEN public.usuario_sesion() IS NULL THEN 'PASS' ELSE 'FAIL' END AS g1,
    public.usuario_sesion() AS operador;
ROLLBACK;

\echo ''
\echo '--- G2 cambiar la contrasena invalida el testigo anterior'
BEGIN;
SELECT gen_random_uuid()::text AS clave_g2
\gset
SELECT public.establecer_password('taller.demo', :'clave_g2');
SELECT public.iniciar_sesion('taller.demo', :'clave_g2');
SELECT current_setting('nova.id_usuario') AS testigo_g2
\gset
SELECT gen_random_uuid()::text AS clave_g2b
\gset
SELECT public.establecer_password('taller.demo', :'clave_g2b');
SELECT set_config('nova.id_usuario', :'testigo_g2', true);
SELECT
    CASE WHEN public.usuario_sesion() IS NULL THEN 'PASS' ELSE 'FAIL' END AS g2,
    public.usuario_sesion() AS operador;
ROLLBACK;

\echo ''
\echo '--- G3 un usuario desactivado tampoco puede volver a entrar'
BEGIN;
SELECT gen_random_uuid()::text AS clave_g3
\gset
SELECT public.establecer_password('taller.demo', :'clave_g3');
UPDATE public.usuarios SET activo = false WHERE username = 'taller.demo';
DO $$
BEGIN
    PERFORM public.iniciar_sesion('taller.demo', 'da-igual');
    RAISE NOTICE 'FAIL G3: entro un usuario desactivado';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'Usuario o contrasena incorrectos' THEN
            RAISE NOTICE 'PASS G3: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL G3: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '--- G4 ningun rol puede crear objetos en public, asi que nadie puede'
\echo '    ensombrecer hmac ni crypt para enganar a las funciones de sesion'
SELECT
    CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS g4,
    count(*) AS roles_que_pueden_crear
FROM pg_roles r
WHERE r.rolname LIKE 'nova\_%'
  AND has_schema_privilege(r.rolname, 'public', 'CREATE');

\echo ''
\echo '--- G5 ninguna funcion SECURITY DEFINER devuelve texto que pueda'
\echo '    arrastrar un hash: todas devuelven integer, void o trigger'
SELECT
    CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS g5,
    count(*) AS funciones_que_devuelven_texto
FROM pg_proc p
WHERE p.pronamespace = 'public'::regnamespace
  AND p.prosecdef
  AND pg_get_function_result(p.oid) NOT IN ('integer', 'void', 'trigger');

\echo ''
\echo '--- G6 LIMITE CONOCIDO: las operaciones se autorizan por el rol de'
\echo '    CONEXION, no por el rol funcional autenticado. Sin iniciar_sesion'
\echo '    la operacion funciona y la auditoria queda sin operador.'
BEGIN;
SET ROLE nova_cliente;
SELECT public.realizar_compra('G6', :cliente_a, :sku, :nave, 1) AS id_pedido
\gset
RESET ROLE;
SELECT
    CASE WHEN pedido_creado = 1 AND operador IS NULL THEN 'PASS' ELSE 'FAIL' END AS g6,
    pedido_creado, operador AS operador_registrado
FROM (
    SELECT
        (SELECT count(*) FROM public.pedidos WHERE id_pedido = :id_pedido) AS pedido_creado,
        (SELECT id_usuario FROM public.log_eventos ORDER BY id_evento DESC LIMIT 1) AS operador
) AS t;
ROLLBACK;

\echo ''
\echo '--- G7 LIMITE CONOCIDO: no hay clave ajena entre usuarios y clientes,'
\echo '    asi que la base no puede saber de quien es un pedido'
SELECT
    CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END AS g7,
    count(*) AS vinculos_usuario_cliente
FROM pg_constraint
WHERE contype = 'f'
  AND connamespace = 'public'::regnamespace
  AND conrelid = 'public.usuarios'::regclass
  AND confrelid = 'public.clientes'::regclass;

\echo ''
\echo '--- G8 cada rol funcional tiene su rol de PostgreSQL equivalente'
SELECT
    CASE WHEN count(*) = 3 THEN 'PASS' ELSE 'FAIL' END AS g8,
    count(*) AS roles_funcionales_con_rol_de_base,
    string_agg(correspondencia, ', ' ORDER BY correspondencia) AS mapa
FROM (
    SELECT r.nombre || ' -> ' || pr.rolname AS correspondencia
    FROM public.roles r
    JOIN pg_roles pr
      ON pr.rolname = CASE r.nombre
                          WHEN 'administrador' THEN 'nova_admin'
                          WHEN 'trabajador' THEN 'nova_trabajador'
                          WHEN 'comercial' THEN 'nova_comercial'
                      END
) AS t;

\echo ''
\echo '--- G9 el perfil de nova_comercial: vende y sigue sus ventas, pero no'
\echo '    gestiona usuarios ni toca importes ni existencias'
SELECT
    CASE WHEN lee_clientes AND lee_pedidos AND puede_vender AND cambia_estado
              AND NOT gestiona_usuarios AND NOT cambia_importe AND NOT cambia_stock
              AND NOT lee_auditoria
         THEN 'PASS' ELSE 'FAIL' END AS g9,
    lee_clientes, lee_pedidos, puede_vender, cambia_estado,
    gestiona_usuarios, cambia_importe, cambia_stock, lee_auditoria
FROM (
    SELECT
        has_table_privilege('nova_comercial', 'public.clientes', 'SELECT') AS lee_clientes,
        has_table_privilege('nova_comercial', 'public.pedidos', 'SELECT') AS lee_pedidos,
        has_function_privilege('nova_comercial',
            'public.realizar_compra(character varying, integer, integer, integer, integer, integer)',
            'EXECUTE') AS puede_vender,
        has_column_privilege('nova_comercial', 'public.pedidos', 'estado', 'UPDATE') AS cambia_estado,
        has_function_privilege('nova_comercial',
            'public.crear_usuario(character varying, character varying)', 'EXECUTE') AS gestiona_usuarios,
        has_column_privilege('nova_comercial', 'public.pedidos', 'importe_total', 'UPDATE') AS cambia_importe,
        has_column_privilege('nova_comercial', 'public.existencias', 'cantidad', 'UPDATE') AS cambia_stock,
        has_table_privilege('nova_comercial', 'public.log_eventos', 'SELECT') AS lee_auditoria
) AS t;

\echo ''
\echo '--- G10 nova_comercial vende, confirma y cancela, pero no gestiona usuarios'
BEGIN;
SELECT sum(cantidad) AS stock_g10 FROM public.existencias
\gset
SET ROLE nova_comercial;
SELECT public.realizar_compra('G10', :cliente_a, :sku, :nave, 2) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
RESET ROLE;
SELECT
    CASE WHEN stock = :stock_g10 - 2 AND estado = 'confirmado'
         THEN 'PASS' ELSE 'FAIL' END AS g10,
    stock, estado
FROM (
    SELECT
        (SELECT sum(cantidad) FROM public.existencias) AS stock,
        (SELECT estado FROM public.pedidos WHERE id_pedido = :id_pedido) AS estado
) AS t;
SET ROLE nova_comercial;
DO $$
BEGIN
    PERFORM public.crear_usuario('colado.comercial', 'comercial');
    RAISE NOTICE 'FAIL G10b: el comercial creo un usuario';
EXCEPTION
    WHEN others THEN
        IF SQLSTATE = '42501' THEN
            RAISE NOTICE 'PASS G10b: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL G10b: error inesperado: %', SQLERRM;
        END IF;
END
$$;
RESET ROLE;
ROLLBACK;

\echo ''
\echo '===== CICLO DE ESTADOS DEL PEDIDO ====='
\echo ''
\echo '--- B1 el esquema admite pendiente, confirmado y cancelado'
SELECT
    CASE WHEN estados_admitidos = 6 THEN 'PASS' ELSE 'FAIL' END AS b1,
    estados_admitidos
FROM (
    SELECT count(*) AS estados_admitidos
    FROM (VALUES ('pendiente'), ('confirmado'), ('en_preparacion'),
                 ('enviado'), ('entregado'), ('cancelado')) AS e(estado)
    WHERE pg_get_constraintdef(
            (SELECT oid FROM pg_constraint WHERE conname = 'pedidos_check_3')
          ) LIKE '%' || e.estado || '%'
) AS t;

\echo ''
\echo '--- B2 recorrido pendiente, confirmado, cancelado con devolucion de stock'
BEGIN;
SELECT sum(cantidad) AS stock_antes FROM public.existencias
\gset
SELECT public.realizar_compra('B2', :cliente_a, :sku, :nave, 4) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
SELECT estado AS estado_confirmado FROM public.pedidos WHERE id_pedido = :id_pedido
\gset
SELECT sum(cantidad) AS stock_confirmado FROM public.existencias
\gset
UPDATE public.pedidos SET estado = 'cancelado' WHERE id_pedido = :id_pedido;
SELECT
    CASE WHEN :'estado_confirmado' = 'confirmado'
              AND :stock_confirmado = :stock_antes - 4
              AND estado = 'cancelado'
              AND stock = :stock_antes
              AND marcas = 0
         THEN 'PASS' ELSE 'FAIL' END AS b2,
    :'estado_confirmado' AS paso_intermedio,
    :stock_confirmado AS stock_tras_confirmar,
    estado, stock AS stock_tras_cancelar, marcas
FROM (
    SELECT
        (SELECT estado FROM public.pedidos WHERE id_pedido = :id_pedido) AS estado,
        (SELECT sum(cantidad) FROM public.existencias) AS stock,
        (SELECT count(*) FROM public.linea_pedido
          WHERE id_pedido = :id_pedido AND stock_descontado = true) AS marcas
) AS t;
ROLLBACK;

\echo ''
\echo '--- B3 un pedido confirmado no se puede modificar en sus lineas'
BEGIN;
SELECT public.realizar_compra('B3', :cliente_a, :sku, :nave, 1) AS id_pedido
\gset
UPDATE public.pedidos SET estado = 'confirmado' WHERE id_pedido = :id_pedido;
DO $$
BEGIN
    UPDATE public.linea_pedido SET cantidad = 9
    WHERE id_pedido = (SELECT id_pedido FROM public.pedidos WHERE referencia = 'B3');
    RAISE NOTICE 'FAIL B3: la base acepto el cambio';
EXCEPTION
    WHEN others THEN
        IF SQLERRM = 'No se puede modificar una compra registrada' THEN
            RAISE NOTICE 'PASS B3: %', SQLERRM;
        ELSE
            RAISE NOTICE 'FAIL B3: error inesperado: %', SQLERRM;
        END IF;
END
$$;
ROLLBACK;

\echo ''
\echo '===== DATOS MINIMOS QUE PIDE EL ENUNCIADO ====='
\echo ''
\echo '--- M1 al menos 5 clientes, 6 modelos, 10 pedidos y 3 personalizados'
SELECT
    CASE WHEN clientes >= 5 AND modelos >= 6 AND pedidos >= 10 AND personalizados >= 3
         THEN 'PASS' ELSE 'FAIL' END AS m1,
    clientes, modelos, pedidos, personalizados
FROM (
    SELECT
        (SELECT count(*) FROM public.clientes) AS clientes,
        (SELECT count(*) FROM public.modelos) AS modelos,
        (SELECT count(*) FROM public.pedidos) AS pedidos,
        (SELECT count(*) FROM public.pedidos WHERE personalizado = true) AS personalizados
) AS t;

\echo ''
\echo '--- M2 existe al menos un pedido con varias TALLAS distintas'
SELECT
    CASE WHEN count(*) >= 1 THEN 'PASS' ELSE 'FAIL' END AS m2,
    count(*) AS pedidos_con_varias_tallas
FROM (
    SELECT l.id_pedido
    FROM public.linea_pedido l
    JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
    GROUP BY l.id_pedido
    HAVING count(DISTINCT s.talla) > 1
) AS t;

\echo ''
\echo '--- M3 detalle del pedido de varias tallas'
SELECT
    p.referencia,
    c.nombre AS cliente,
    count(*) AS lineas,
    count(DISTINCT s.talla) AS tallas_distintas,
    sum(l.cantidad) AS pares,
    p.importe_total AS importe
FROM public.pedidos p
JOIN public.clientes c ON c.id_cliente = p.id_cliente
JOIN public.linea_pedido l ON l.id_pedido = p.id_pedido
JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
GROUP BY p.referencia, c.nombre, p.importe_total
HAVING count(DISTINCT s.talla) > 1
ORDER BY p.referencia;

\echo ''
\echo '--- M4 hay un usuario activo por cada rol funcional'
SELECT
    CASE WHEN count(*) = 3 THEN 'PASS' ELSE 'FAIL' END AS m4,
    count(*) AS roles_con_usuario_activo
FROM (
    SELECT r.nombre
    FROM public.roles r
    JOIN public.usuarios u ON u.id_rol = r.id_rol
    WHERE u.activo = true
    GROUP BY r.nombre
) AS t;

\echo ''
\echo '===== PRUEBA DE CONCURRENCIA ====='
\echo ''
\echo 'No se puede ejecutar desde una sola sesion.'
\echo 'El procedimiento con dos sesiones esta en el apartado 11 del README.'
\echo ''
\echo '===== FIN DE LA BATERIA ====='
