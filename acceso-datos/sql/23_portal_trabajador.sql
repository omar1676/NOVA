-- =====================================================================
-- 23_portal_trabajador.sql — lo que puede hacer en la base el portal del
-- trabajador (interfaces/trabajador, rutas en servidor-admin/rutas-trabajador.js)
--
-- QUE HACE
--   1. Crea dos funciones SECURITY DEFINER, con search_path fijo. Son lo
--      UNICO que el portal puede cambiar en la base:
--        - avanzar_pedido_trabajador(usuario, pedido, estado): el boton
--          "Avanzar estado". Un pedido solo avanza un paso:
--          confirmado -> en_preparacion -> enviado -> entregado.
--        - ajustar_existencias_trabajador(usuario, sku, nave, cantidad): el
--          boton "Guardar" del inventario (cantidad entre 0 y 99999).
--      Las dos comprueban que el usuario existe, esta activo y tiene el rol
--      "trabajador". Usan el mismo mecanismo que iniciar_sesion (02) y que
--      marcar_pedido_en_reparto (22): la variable nova.id_usuario con el id
--      y su firma, solo durante el cambio. Asi los triggers de 08 apuntan en
--      log_eventos el CAMBIO_ESTADO o el CAMBIO_STOCK con ese trabajador.
--      Los cambios pasan por los triggers de siempre: avanzar un pedido ya
--      confirmado no toca el stock.
--
--   2. Crea portal_trabajador, un rol sin login. Puede:
--        - LEER solo las columnas que ensena el portal (pedidos, clientes,
--          inventario y configuraciones X-Nova). Nada de password_hash,
--          dni, email, telefono ni direccion_entrega, ni log_eventos;
--        - ejecutar las dos funciones de arriba.
--      No puede escribir en ninguna tabla por su cuenta. web_nova pasa a el
--      con SET LOCAL ROLE (sin heredar sus permisos), como a panel_lectura
--      (19) y a panel_reparto (22). Nadie mas puede llamar a las funciones.
--
-- QUE NO HACE
--   No cambia ninguna tabla, trigger, funcion ni rol de los scripts 01-22:
--   panel_lectura y panel_reparto siguen igual.
--   El rol no se llama nova_* porque 09 cuenta los roles con ese prefijo.
--
-- COMO SE EJECUTA
--   Con el usuario que instalo la base, DESPUES de 19 y 22:
--     psql -U postgres -d nova_sneakers -f 23_portal_trabajador.sql
--   Se puede repetir: vuelve a dejar las funciones y los permisos como dice
--   este script.
-- =====================================================================

\set ON_ERROR_STOP on

\echo '===== Portal del trabajador ====='

-- Todo o nada: si algo falla, no queda nada a medias
BEGIN;

-- ---------------------------------------------------------------------
-- 1. Avanzar el estado de un pedido (un paso)
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.avanzar_pedido_trabajador(
    p_id_usuario integer,
    p_id_pedido integer,
    p_estado_nuevo varchar
)
 RETURNS TABLE (id_pedido integer, referencia varchar, estado varchar)
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = pg_catalog, public, extensiones
AS $function$
DECLARE
    v_hash text;
    v_estado varchar(25);
    v_siguiente varchar(25);
    v_sesion_anterior text;
BEGIN
    -- 1. El usuario existe, esta activo y es trabajador
    SELECT u.password_hash
    INTO v_hash
    FROM public.usuarios u
    JOIN public.roles r ON r.id_rol = u.id_rol
    WHERE u.id_usuario = p_id_usuario
      AND u.activo = true
      AND r.nombre = 'trabajador';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Usuario no autorizado';
    END IF;

    -- 2. El pedido existe. FOR UPDATE: si llegan dos clics a la vez, el
    --    segundo espera al primero y ya ve el estado nuevo.
    SELECT p.estado
    INTO v_estado
    FROM public.pedidos p
    WHERE p.id_pedido = p_id_pedido
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'El pedido no existe';
    END IF;

    -- 3. Solo un paso adelante, como el portal de Berme (siguienteEstado)
    v_siguiente := CASE v_estado
        WHEN 'confirmado' THEN 'en_preparacion'
        WHEN 'en_preparacion' THEN 'enviado'
        WHEN 'enviado' THEN 'entregado'
    END;

    IF v_siguiente IS NULL THEN
        RAISE EXCEPTION 'Un pedido en estado % no se puede avanzar', v_estado;
    END IF;

    IF p_estado_nuevo IS DISTINCT FROM v_siguiente THEN
        RAISE EXCEPTION 'Solo se puede pasar de % a %', v_estado, v_siguiente;
    END IF;

    -- 4. Quien hace el cambio: el id y su firma, como iniciar_sesion (02).
    --    Asi auditar_estado_pedido (08) apunta al trabajador.
    v_sesion_anterior := current_setting('nova.id_usuario', true);
    PERFORM set_config(
        'nova.id_usuario',
        p_id_usuario::text || ':' ||
        encode(hmac(p_id_usuario::text, v_hash, 'sha256'), 'hex'),
        true
    );

    UPDATE public.pedidos p
    SET estado = v_siguiente
    WHERE p.id_pedido = p_id_pedido;

    -- 5. La variable vuelve a como estaba: no queda una sesion abierta
    PERFORM set_config('nova.id_usuario', COALESCE(v_sesion_anterior, ''), true);

    RETURN QUERY
    SELECT p.id_pedido, p.referencia, p.estado
    FROM public.pedidos p
    WHERE p.id_pedido = p_id_pedido;
END;
$function$
;

-- ---------------------------------------------------------------------
-- 2. Cambiar la cantidad de unas existencias (SKU en una nave)
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.ajustar_existencias_trabajador(
    p_id_usuario integer,
    p_id_producto_sku integer,
    p_id_nave integer,
    p_cantidad integer
)
 RETURNS TABLE (id_producto_sku integer, id_nave integer, cantidad integer)
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = pg_catalog, public, extensiones
AS $function$
DECLARE
    v_hash text;
    v_sesion_anterior text;
BEGIN
    -- 1. El usuario existe, esta activo y es trabajador
    SELECT u.password_hash
    INTO v_hash
    FROM public.usuarios u
    JOIN public.roles r ON r.id_rol = u.id_rol
    WHERE u.id_usuario = p_id_usuario
      AND u.activo = true
      AND r.nombre = 'trabajador';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Usuario no autorizado';
    END IF;

    -- 2. Una cantidad razonable (la tabla solo exige >= 0)
    IF p_cantidad IS NULL OR p_cantidad < 0 OR p_cantidad > 99999 THEN
        RAISE EXCEPTION 'La cantidad debe ser un numero entero entre 0 y 99999';
    END IF;

    -- 3. Quien hace el cambio, para auditar_existencias (08)
    v_sesion_anterior := current_setting('nova.id_usuario', true);
    PERFORM set_config(
        'nova.id_usuario',
        p_id_usuario::text || ':' ||
        encode(hmac(p_id_usuario::text, v_hash, 'sha256'), 'hex'),
        true
    );

    UPDATE public.existencias e
    SET cantidad = p_cantidad
    WHERE e.id_producto_sku = p_id_producto_sku
      AND e.id_nave = p_id_nave;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'No existe esa existencia';
    END IF;

    PERFORM set_config('nova.id_usuario', COALESCE(v_sesion_anterior, ''), true);

    RETURN QUERY
    SELECT e.id_producto_sku, e.id_nave, e.cantidad
    FROM public.existencias e
    WHERE e.id_producto_sku = p_id_producto_sku
      AND e.id_nave = p_id_nave;
END;
$function$
;

-- Al crear una funcion, PostgreSQL deja que cualquiera la ejecute (PUBLIC).
-- Se quita: solo portal_trabajador podra usarlas.
REVOKE EXECUTE ON FUNCTION public.avanzar_pedido_trabajador(integer, integer, varchar) FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION public.ajustar_existencias_trabajador(integer, integer, integer, integer) FROM PUBLIC;

-- ---------------------------------------------------------------------
-- 3. El rol del portal
-- ---------------------------------------------------------------------
SELECT NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'portal_trabajador') AS hay_que_crear_rol
\gset

\if :hay_que_crear_rol
CREATE ROLE portal_trabajador NOLOGIN;
\endif

-- Si se repite el script, se empieza de cero con sus permisos de tabla
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM portal_trabajador;

GRANT USAGE ON SCHEMA public TO portal_trabajador;

-- Solo las columnas que lee el portal (rutas-trabajador.js)
GRANT SELECT (id_pedido, referencia, id_cliente, fecha_pedido, fecha_objetivo, estado,
              importe_total, cantidad_total, personalizado, personalizacion)
ON public.pedidos TO portal_trabajador;

GRANT SELECT (id_cliente, nombre)            -- sin email, telefono ni direccion_entrega
ON public.clientes TO portal_trabajador;

GRANT SELECT (id_producto_sku, id_nave, cantidad) ON public.existencias TO portal_trabajador;
GRANT SELECT (id_nave, nombre) ON public.nave TO portal_trabajador;
GRANT SELECT (id_producto_sku, id_variante, talla, sku) ON public.producto_sku TO portal_trabajador;
GRANT SELECT (id_variante, id_modelo, color) ON public.variantes TO portal_trabajador;
GRANT SELECT (id_modelo, nombre) ON public.modelos TO portal_trabajador;

GRANT SELECT (id_configuracion, id_cliente, id_pedido, talla_referencia, color_principal,
              color_secundario, material, tipo_suela, texto_personalizado, fecha_creacion)
ON public.configuraciones_xnova TO portal_trabajador;

-- Las dos escrituras, solo a traves de las funciones
GRANT EXECUTE ON FUNCTION public.avanzar_pedido_trabajador(integer, integer, varchar) TO portal_trabajador;
GRANT EXECUTE ON FUNCTION public.ajustar_existencias_trabajador(integer, integer, integer, integer) TO portal_trabajador;

-- web_nova puede pasar a portal_trabajador solo con SET ROLE (no hereda nada),
-- como con panel_lectura (19) y panel_reparto (22)
GRANT portal_trabajador TO web_nova WITH INHERIT FALSE, SET TRUE;

COMMIT;

-- ---------------------------------------------------------------------
-- Comprobaciones
-- ---------------------------------------------------------------------
\echo ''
\echo '--- Comprobacion: web_nova pasa a panel_lectura, panel_reparto y portal_trabajador, sin heredar'
SELECT
    r.rolname AS rol,
    m.inherit_option AS hereda_permisos,
    m.set_option AS puede_set_role
FROM pg_auth_members m
JOIN pg_roles r ON r.oid = m.roleid
WHERE m.member = 'web_nova'::regrole
ORDER BY r.rolname;

\echo ''
\echo '--- Comprobacion: quien puede usar las funciones del portal (solo portal_trabajador: t)'
SELECT
    f.funcion,
    has_function_privilege('portal_trabajador', f.funcion, 'EXECUTE') AS portal_trabajador,
    has_function_privilege('web_nova', f.funcion, 'EXECUTE') AS web_nova_sin_set_role,
    has_function_privilege('panel_lectura', f.funcion, 'EXECUTE') AS panel_lectura,
    has_function_privilege('panel_reparto', f.funcion, 'EXECUTE') AS panel_reparto,
    has_function_privilege('tienda_web', f.funcion, 'EXECUTE') AS tienda_web,
    has_function_privilege('public', f.funcion, 'EXECUTE') AS cualquiera
FROM (VALUES
    ('public.avanzar_pedido_trabajador(integer, integer, character varying)'),
    ('public.ajustar_existencias_trabajador(integer, integer, integer, integer)')
) AS f(funcion);

\echo ''
\echo '--- Comprobacion: portal_trabajador no escribe en ninguna tabla (se espera 0)'
SELECT count(*) AS tablas_en_las_que_escribe
FROM pg_tables t
WHERE t.schemaname = 'public'
  AND (has_any_column_privilege('portal_trabajador', format('%I.%I', t.schemaname, t.tablename), 'INSERT, UPDATE')
       OR has_table_privilege('portal_trabajador', format('%I.%I', t.schemaname, t.tablename), 'DELETE, TRUNCATE'));

\echo ''
\echo '--- Comprobacion: portal_trabajador no ve datos sensibles ni la auditoria (se esperan seis f)'
SELECT
    has_column_privilege('portal_trabajador', 'public.usuarios', 'password_hash', 'SELECT') AS lee_hash,
    has_column_privilege('portal_trabajador', 'public.personal', 'dni', 'SELECT') AS lee_dni,
    has_column_privilege('portal_trabajador', 'public.clientes', 'email', 'SELECT') AS lee_email,
    has_column_privilege('portal_trabajador', 'public.clientes', 'direccion_entrega', 'SELECT') AS lee_direccion,
    has_any_column_privilege('portal_trabajador', 'public.log_eventos', 'SELECT') AS lee_auditoria,
    has_any_column_privilege('portal_trabajador', 'public.cuentas_cliente', 'SELECT') AS lee_cuentas_tienda;

\echo ''
\echo '--- Comprobacion: las funciones son SECURITY DEFINER y fijan el search_path (se esperan dos filas t, t)'
SELECT
    p.proname AS funcion,
    p.prosecdef AS security_definer,
    p.proconfig IS NOT NULL AS fija_search_path
FROM pg_proc p
WHERE p.oid IN ('public.avanzar_pedido_trabajador(integer, integer, character varying)'::regprocedure,
                'public.ajustar_existencias_trabajador(integer, integer, integer, integer)'::regprocedure)
ORDER BY p.proname;

\echo ''
\echo '===== FIN ====='
