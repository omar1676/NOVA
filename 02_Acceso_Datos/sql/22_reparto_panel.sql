-- =====================================================================
-- 22_reparto_panel.sql — el boton "Marcar en reparto" del panel
--
-- QUE HACE
--   1. Crea la funcion marcar_pedido_en_reparto(p_id_usuario, p_id_pedido),
--      SECURITY DEFINER y con search_path fijo. Es lo UNICO que el panel
--      puede cambiar en la base:
--        - comprueba que el usuario existe, esta activo y es administrador;
--        - comprueba que el pedido existe y esta en "confirmado";
--        - lo pasa a "enviado" (en la web sale como "En reparto").
--      El cambio pasa por los triggers de siempre (03 y 08): no se toca el
--      stock (ya se desconto al confirmar) y la auditoria apunta un
--      CAMBIO_ESTADO con ese administrador. Para que usuario_sesion() (02)
--      lo reconozca se usa el mismo mecanismo que iniciar_sesion: la
--      variable nova.id_usuario con el id y su firma, solo durante el cambio.
--
--   2. Crea panel_reparto, un rol sin login que SOLO puede ejecutar esa
--      funcion: no lee ni escribe ninguna tabla. web_nova puede pasar a el
--      con SET LOCAL ROLE (sin heredar sus permisos), igual que a
--      panel_lectura. panel_lectura no cambia: sigue sin poder escribir.
--      Nadie mas puede llamar a la funcion (ni tienda_web ni tienda_nova).
--
-- QUE NO HACE
--   No cambia ninguna tabla, trigger ni funcion de los scripts 01-21.
--   Las reglas de 02 y 03 no exigen pasar por "en_preparacion" antes de
--   "enviado", asi que se pasa directamente de "confirmado" a "enviado".
--   El rol no se llama nova_* porque 09 cuenta los roles con ese prefijo.
--
-- COMO SE EJECUTA
--   Con el usuario que instalo la base, DESPUES de 09, 19 y 20:
--     psql -U postgres -d nova_sneakers -f 22_reparto_panel.sql
--   Se puede repetir: vuelve a dejar la funcion y los permisos como dice
--   este script.
-- =====================================================================

\set ON_ERROR_STOP on

\echo '===== Panel: marcar pedidos en reparto ====='

-- Todo o nada: si algo falla, no queda nada a medias
BEGIN;

-- ---------------------------------------------------------------------
-- 1. La funcion
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.marcar_pedido_en_reparto(p_id_usuario integer, p_id_pedido integer)
 RETURNS void
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = pg_catalog, public, extensiones
AS $function$
DECLARE
    v_hash text;
    v_estado varchar(25);
    v_sesion_anterior text;
BEGIN
    -- 1. El usuario existe, esta activo y es administrador
    SELECT u.password_hash
    INTO v_hash
    FROM public.usuarios u
    JOIN public.roles r ON r.id_rol = u.id_rol
    WHERE u.id_usuario = p_id_usuario
      AND u.activo = true
      AND r.nombre = 'administrador';

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Usuario no autorizado';
    END IF;

    -- 2. El pedido existe y esta confirmado. FOR UPDATE: si llegan dos clics
    --    a la vez, el segundo espera al primero y ya lo ve "enviado".
    SELECT estado
    INTO v_estado
    FROM public.pedidos
    WHERE id_pedido = p_id_pedido
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'El pedido no existe';
    END IF;

    IF v_estado <> 'confirmado' THEN
        RAISE EXCEPTION 'Solo se puede pasar a reparto un pedido confirmado';
    END IF;

    -- 3. Quien hace el cambio: lo mismo que deja iniciar_sesion (02), el id
    --    y su firma. Asi auditar_estado_pedido (08) apunta al administrador.
    v_sesion_anterior := current_setting('nova.id_usuario', true);
    PERFORM set_config(
        'nova.id_usuario',
        p_id_usuario::text || ':' ||
        encode(hmac(p_id_usuario::text, v_hash, 'sha256'), 'hex'),
        true
    );

    -- 4. El cambio de estado. Los triggers de 03 no tocan el stock: solo
    --    actuan al confirmar o al cancelar.
    UPDATE public.pedidos
    SET estado = 'enviado'
    WHERE id_pedido = p_id_pedido;

    -- 5. La variable vuelve a como estaba: no queda una sesion abierta
    PERFORM set_config('nova.id_usuario', COALESCE(v_sesion_anterior, ''), true);
END;
$function$
;

-- Al crear una funcion, PostgreSQL deja que cualquiera la ejecute (PUBLIC).
-- Se quita: solo panel_reparto podra usarla.
REVOKE EXECUTE ON FUNCTION public.marcar_pedido_en_reparto(integer, integer) FROM PUBLIC;

-- ---------------------------------------------------------------------
-- 2. El rol que solo puede marcar pedidos en reparto
-- ---------------------------------------------------------------------
SELECT NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'panel_reparto') AS hay_que_crear_rol
\gset

\if :hay_que_crear_rol
CREATE ROLE panel_reparto NOLOGIN;
\endif

-- USAGE solo deja encontrar la funcion dentro de public: no da acceso a
-- ninguna tabla
GRANT USAGE ON SCHEMA public TO panel_reparto;
GRANT EXECUTE ON FUNCTION public.marcar_pedido_en_reparto(integer, integer) TO panel_reparto;

-- web_nova puede pasar a panel_reparto solo con SET ROLE (no hereda nada),
-- como con panel_lectura en el script 19
GRANT panel_reparto TO web_nova WITH INHERIT FALSE, SET TRUE;

COMMIT;

-- ---------------------------------------------------------------------
-- Comprobaciones
-- ---------------------------------------------------------------------
\echo ''
\echo '--- Comprobacion: web_nova pasa a panel_lectura y a panel_reparto, sin heredar'
SELECT
    r.rolname AS rol,
    m.inherit_option AS hereda_permisos,
    m.set_option AS puede_set_role
FROM pg_auth_members m
JOIN pg_roles r ON r.oid = m.roleid
WHERE m.member = 'web_nova'::regrole
ORDER BY r.rolname;

\echo ''
\echo '--- Comprobacion: quien puede marcar en reparto (solo panel_reparto: t)'
SELECT
    has_function_privilege('panel_reparto', 'public.marcar_pedido_en_reparto(integer, integer)', 'EXECUTE') AS panel_reparto,
    has_function_privilege('panel_lectura', 'public.marcar_pedido_en_reparto(integer, integer)', 'EXECUTE') AS panel_lectura,
    has_function_privilege('web_nova', 'public.marcar_pedido_en_reparto(integer, integer)', 'EXECUTE') AS web_nova_sin_set_role,
    has_function_privilege('tienda_web', 'public.marcar_pedido_en_reparto(integer, integer)', 'EXECUTE') AS tienda_web,
    has_function_privilege('tienda_nova', 'public.marcar_pedido_en_reparto(integer, integer)', 'EXECUTE') AS tienda_nova,
    has_function_privilege('public', 'public.marcar_pedido_en_reparto(integer, integer)', 'EXECUTE') AS cualquiera;

\echo ''
\echo '--- Comprobacion: panel_reparto no lee ni escribe ninguna tabla y panel_lectura no escribe (se esperan dos 0)'
SELECT
    count(*) FILTER (WHERE has_any_column_privilege('panel_reparto', format('%I.%I', t.schemaname, t.tablename), 'SELECT, INSERT, UPDATE')
                        OR has_table_privilege('panel_reparto', format('%I.%I', t.schemaname, t.tablename), 'DELETE, TRUNCATE')) AS tablas_panel_reparto,
    count(*) FILTER (WHERE has_any_column_privilege('panel_lectura', format('%I.%I', t.schemaname, t.tablename), 'INSERT, UPDATE')
                        OR has_table_privilege('panel_lectura', format('%I.%I', t.schemaname, t.tablename), 'DELETE, TRUNCATE')) AS escribe_panel_lectura
FROM pg_tables t
WHERE t.schemaname = 'public';

\echo ''
\echo '--- Comprobacion: la funcion es SECURITY DEFINER y fija el search_path (se esperan dos t)'
SELECT
    p.prosecdef AS security_definer,
    p.proconfig IS NOT NULL AS fija_search_path
FROM pg_proc p
WHERE p.oid = 'public.marcar_pedido_en_reparto(integer, integer)'::regprocedure;

\echo ''
\echo '===== FIN ====='
