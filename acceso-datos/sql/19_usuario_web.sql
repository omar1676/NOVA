-- =====================================================================
-- 19_usuario_web.sql — la cuenta con la que se conecta el servidor del
-- panel de administracion (servidor-admin/)
--
-- QUE HACE
--   1. Crea panel_lectura, un rol de SOLO LECTURA. Nadie se conecta con el
--      (NOLOGIN): solo reune los permisos que necesita el panel.
--        - Puede LEER lo que usan las ocho rutas, y nada mas.
--        - No tiene ningun permiso de escritura: ni INSERT, ni UPDATE, ni
--          DELETE en ninguna tabla.
--        - De las tablas con datos personales solo ve algunas columnas:
--          nada de password_hash, dni ni direccion_entrega.
--        - Puede ejecutar iniciar_sesion para el login. Es SECURITY DEFINER:
--          compara la contrasena con los permisos de su dueno, asi que
--          panel_lectura nunca llega a ver el hash.
--
--   2. Crea el usuario de PostgreSQL web_nova, que puede conectarse
--      (LOGIN). La contrasena se pide por teclado y no se guarda en el
--      repositorio: el servidor la lee de servidor-admin/.env.
--      Es NOINHERIT y solo puede pasar a panel_lectura. El servidor abre
--      cada consulta con
--         BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;
--         SET LOCAL ROLE panel_lectura;
--      Aunque el codigo olvidara el READ ONLY, PostgreSQL no le dejaria
--      escribir: panel_lectura no tiene permisos para hacerlo.
--
--   3. Si web_nova venia de la version anterior de este script, le quita
--      nova_admin.
--
--   No crea tablas, funciones ni triggers. Los roles no se llaman nova_*
--   porque las pruebas de 09 (P1, A11b y G4) cuentan los roles con ese
--   prefijo.
--
-- COMO SE EJECUTA
--   Con el usuario que instalo la base, despues de 07_seguridad.sql:
--     psql -U postgres -d nova_sneakers -f 19_usuario_web.sql
--   Se puede repetir: si los roles ya existen, solo cambia la contrasena
--   de web_nova y vuelve a dejar los permisos como dice este script.
-- =====================================================================

\set ON_ERROR_STOP on

\echo '===== Usuario de conexion para el servidor del panel de administracion ====='
\echo ''
\prompt 'Contrasena para web_nova (la que ira en servidor-admin/.env): ' clave_web

-- ---------------------------------------------------------------------
-- 1. El rol de solo lectura
-- ---------------------------------------------------------------------
SELECT NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'panel_lectura') AS hay_que_crear_rol
\gset

\if :hay_que_crear_rol
CREATE ROLE panel_lectura NOLOGIN;
\endif

GRANT USAGE ON SCHEMA public TO panel_lectura;

-- Tablas sin datos personales: se pueden leer enteras
GRANT SELECT
ON public.modelos, public.variantes, public.producto_sku,
   public.existencias, public.nave, public.roles, public.log_eventos
TO panel_lectura;

-- Tablas con datos personales o internos: solo las columnas que usa el panel
GRANT SELECT (id_pedido, referencia, id_cliente, fecha_pedido, estado, cantidad_total, importe_total)
ON public.pedidos TO panel_lectura;

GRANT SELECT (id_pedido, id_producto_sku, cantidad)
ON public.linea_pedido TO panel_lectura;

GRANT SELECT (id_cliente, nombre, tipo, email, telefono, activo)  -- sin direccion_entrega
ON public.clientes TO panel_lectura;

GRANT SELECT (id_personal, nombre, puesto)                         -- sin dni
ON public.personal TO panel_lectura;

GRANT SELECT (id_usuario, username, id_rol, id_personal, activo)   -- sin password_hash
ON public.usuarios TO panel_lectura;

-- El login
GRANT EXECUTE ON FUNCTION public.iniciar_sesion(character varying, text) TO panel_lectura;

-- ---------------------------------------------------------------------
-- 2. El usuario con el que se conecta el servidor
-- ---------------------------------------------------------------------
SELECT NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'web_nova') AS hay_que_crear
\gset

\if :hay_que_crear
CREATE ROLE web_nova LOGIN NOINHERIT;
\endif

ALTER ROLE web_nova WITH LOGIN NOINHERIT PASSWORD :'clave_web';
\unset clave_web

-- 3. La version anterior de este script le daba nova_admin: se le quita
SELECT EXISTS (
    SELECT 1 FROM pg_auth_members
    WHERE member = 'web_nova'::regrole AND roleid = 'nova_admin'::regrole
) AS era_nova_admin
\gset

\if :era_nova_admin
REVOKE nova_admin FROM web_nova;
\endif

-- Solo puede pasar a panel_lectura, y solo con SET ROLE (no hereda sus permisos).
-- Las opciones van escritas: si web_nova ya era miembro y heredaba, repetir el
-- script lo corrige (un GRANT sin opciones dejaria la herencia como estaba).
GRANT panel_lectura TO web_nova WITH INHERIT FALSE, SET TRUE;

-- ---------------------------------------------------------------------
-- Comprobaciones
-- ---------------------------------------------------------------------
\echo ''
\echo '--- Comprobacion: web_nova solo puede pasar a panel_lectura y no hereda'
SELECT
    r.rolname AS rol,
    m.inherit_option AS hereda_permisos,
    m.set_option AS puede_set_role
FROM pg_auth_members m
JOIN pg_roles r ON r.oid = m.roleid
WHERE m.member = 'web_nova'::regrole
ORDER BY r.rolname;

\echo ''
\echo '--- Comprobacion: sin SET ROLE, web_nova no lee nada ni puede hacer login'
\echo '    (se esperan tres f)'
SELECT
    has_any_column_privilege('web_nova', 'public.pedidos', 'SELECT') AS lee_pedidos,
    has_any_column_privilege('web_nova', 'public.clientes', 'SELECT') AS lee_clientes,
    has_function_privilege('web_nova', 'public.iniciar_sesion(character varying, text)', 'EXECUTE') AS hace_login;

\echo ''
\echo '--- Comprobacion: panel_lectura lee lo que necesita el panel (se esperan tres t)'
SELECT
    has_any_column_privilege('panel_lectura', 'public.pedidos', 'SELECT') AS lee_pedidos,
    has_table_privilege('panel_lectura', 'public.existencias', 'SELECT') AS lee_existencias,
    has_function_privilege('panel_lectura', 'public.iniciar_sesion(character varying, text)', 'EXECUTE') AS hace_login;

\echo ''
\echo '--- Comprobacion: panel_lectura no puede escribir en ninguna tabla de public'
\echo '    (se espera 0)'
SELECT count(*) AS tablas_en_las_que_puede_escribir
FROM pg_tables t
WHERE t.schemaname = 'public'
  AND (has_any_column_privilege('panel_lectura', format('%I.%I', t.schemaname, t.tablename), 'INSERT, UPDATE')
       OR has_table_privilege('panel_lectura', format('%I.%I', t.schemaname, t.tablename), 'DELETE, TRUNCATE'));

\echo ''
\echo '--- Comprobacion: panel_lectura no ve datos sensibles (se esperan cuatro f)'
SELECT
    has_column_privilege('panel_lectura', 'public.usuarios', 'password_hash', 'SELECT') AS lee_hash,
    has_column_privilege('panel_lectura', 'public.personal', 'dni', 'SELECT') AS lee_dni,
    has_column_privilege('panel_lectura', 'public.clientes', 'direccion_entrega', 'SELECT') AS lee_direccion,
    has_column_privilege('panel_lectura', 'public.pedidos', 'personalizacion', 'SELECT') AS lee_personalizacion;

\echo ''
\echo '===== FIN ====='
