-- 17_usuario_java.sql — la cuenta de conexion con los roles de la base

\set ON_ERROR_STOP on

\echo 'Usuario de conexion java_nova'
\echo ''
\prompt 'Contrasena para java_nova: ' clave_java

SELECT NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'java_nova') AS hay_que_crear
\gset

\if :hay_que_crear
CREATE ROLE java_nova LOGIN NOINHERIT;
\endif

ALTER ROLE java_nova WITH LOGIN NOINHERIT PASSWORD :'clave_java';
\unset clave_java

-- Puede cambiar a cualquiera de los tres roles con SET ROLE
GRANT nova_admin, nova_comercial, nova_trabajador TO java_nova;

-- Lo que necesita el login antes de elegir rol
GRANT USAGE ON SCHEMA public TO java_nova;
GRANT EXECUTE ON FUNCTION public.iniciar_sesion(character varying, text) TO java_nova;
GRANT SELECT (id_usuario, username, id_rol, activo) ON public.usuarios TO java_nova;
GRANT SELECT ON public.roles TO java_nova;

-- El comercial puede registrar pedidos Custom
GRANT UPDATE (personalizado, personalizacion) ON public.pedidos TO nova_comercial;

\echo ''
\echo 'Comprobacion: java_nova no hereda permisos y puede hacer SET ROLE'
SELECT
    r.rolname AS rol,
    m.inherit_option AS hereda_permisos,
    m.set_option AS puede_set_role
FROM pg_auth_members m
JOIN pg_roles r ON r.oid = m.roleid
WHERE m.member = 'java_nova'::regrole
ORDER BY r.rolname;

\echo ''
\echo 'Comprobacion: sin SET ROLE, java_nova no lee pedidos ni hashes'
\echo '    (se esperan dos f)'
SELECT
    has_table_privilege('java_nova', 'public.pedidos', 'SELECT') AS lee_pedidos_sin_set_role,
    has_column_privilege('java_nova', 'public.usuarios', 'password_hash', 'SELECT') AS lee_password_hash;

\echo ''
\echo 'FIN'
