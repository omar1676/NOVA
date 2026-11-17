-- 19_usuario_web.sql — la cuenta con la que se conecta el servidor del

\set ON_ERROR_STOP on

\echo 'Usuario de conexion para el servidor del panel de administracion'
\echo ''
\prompt 'Contrasena para web_nova (la que ira en servidor-admin/.env): ' clave_web

-- 1. El rol de solo lectura
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

-- 2. El usuario con el que se conecta el servidor
SELECT NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'web_nova') AS hay_que_crear
\gset

\if :hay_que_crear
CREATE ROLE web_nova LOGIN NOINHERIT;
\endif

ALTER ROLE web_nova WITH LOGIN NOINHERIT PASSWORD :'clave_web';
\unset clave_web

-- 3. Un borrador anterior de este script le daba nova_admin: si lo tiene, se le quita
SELECT EXISTS (
    SELECT 1 FROM pg_auth_members
    WHERE member = 'web_nova'::regrole AND roleid = 'nova_admin'::regrole
) AS era_nova_admin
\gset

\if :era_nova_admin
REVOKE nova_admin FROM web_nova;
\endif

GRANT panel_lectura TO web_nova WITH INHERIT FALSE, SET TRUE;

-- Comprobaciones
\echo ''
\echo 'Comprobacion: web_nova solo puede pasar a panel_lectura y no hereda'
SELECT
    r.rolname AS rol,
    m.inherit_option AS hereda_permisos,
    m.set_option AS puede_set_role
FROM pg_auth_members m
JOIN pg_roles r ON r.oid = m.roleid
WHERE m.member = 'web_nova'::regrole
ORDER BY r.rolname;

\echo ''
\echo 'Comprobacion: sin SET ROLE, web_nova no lee nada ni puede hacer login'
\echo '    (se esperan tres f)'
SELECT
    has_any_column_privilege('web_nova', 'public.pedidos', 'SELECT') AS lee_pedidos,
    has_any_column_privilege('web_nova', 'public.clientes', 'SELECT') AS lee_clientes,
    has_function_privilege('web_nova', 'public.iniciar_sesion(character varying, text)', 'EXECUTE') AS hace_login;

\echo ''
\echo 'Comprobacion: panel_lectura lee lo que necesita el panel (se esperan tres t)'
SELECT
    has_any_column_privilege('panel_lectura', 'public.pedidos', 'SELECT') AS lee_pedidos,
    has_table_privilege('panel_lectura', 'public.existencias', 'SELECT') AS lee_existencias,
    has_function_privilege('panel_lectura', 'public.iniciar_sesion(character varying, text)', 'EXECUTE') AS hace_login;

\echo ''
\echo 'Comprobacion: panel_lectura no puede escribir en ninguna tabla de public'
\echo '    (se espera 0)'
SELECT count(*) AS tablas_en_las_que_puede_escribir
FROM pg_tables t
WHERE t.schemaname = 'public'
  AND (has_any_column_privilege('panel_lectura', format('%I.%I', t.schemaname, t.tablename), 'INSERT, UPDATE')
       OR has_table_privilege('panel_lectura', format('%I.%I', t.schemaname, t.tablename), 'DELETE, TRUNCATE'));

\echo ''
\echo 'Comprobacion: panel_lectura no ve datos sensibles (se esperan cuatro f)'
SELECT
    has_column_privilege('panel_lectura', 'public.usuarios', 'password_hash', 'SELECT') AS lee_hash,
    has_column_privilege('panel_lectura', 'public.personal', 'dni', 'SELECT') AS lee_dni,
    has_column_privilege('panel_lectura', 'public.clientes', 'direccion_entrega', 'SELECT') AS lee_direccion,
    has_column_privilege('panel_lectura', 'public.pedidos', 'personalizacion', 'SELECT') AS lee_personalizacion;

\echo ''
\echo 'FIN'
