-- =====================================================================
-- 17_usuario_java.sql — la cuenta con la que se conecta la aplicacion Java
--
-- QUE HACE
--   1. Crea el usuario de PostgreSQL java_nova, que es el unico que puede
--      conectarse (LOGIN). La contrasena se pide por teclado y no se
--      guarda en el repositorio: Java la lee de conexion.properties.
--
--   2. Le concede los tres roles de la aplicacion, pero es NOINHERIT: por
--      si solo no tiene ninguno de sus permisos. Despues del login, Java
--      hace SET ROLE al rol que corresponde al usuario:
--         administrador -> nova_admin
--         comercial     -> nova_comercial
--         trabajador    -> nova_trabajador
--      A partir de ahi la conexion solo puede hacer lo que permite ese rol.
--
--   3. Le da lo justo para el login, que pasa ANTES del SET ROLE:
--      comprobar la contrasena con iniciar_sesion y leer el rol del usuario
--      (sin la columna password_hash).
--
--   4. Deja que el comercial marque un pedido como Custom (columnas
--      personalizado y personalizacion). Antes solo podia el administrador,
--      y el enunciado pide que el pedido Custom se registre desde Java.
--
-- COMO SE EJECUTA
--   Con el usuario que instalo la base, despues de 07_seguridad.sql:
--     psql -U postgres -d nova_sneakers -f 17_usuario_java.sql
--   Se puede repetir: si java_nova ya existe, solo le cambia la contrasena.
-- =====================================================================

\set ON_ERROR_STOP on

\echo '===== Usuario de conexion para la aplicacion Java ====='
\echo ''
\prompt 'Contrasena para java_nova (la que ira en conexion.properties): ' clave_java

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
\echo '--- Comprobacion: java_nova no hereda permisos y puede hacer SET ROLE'
SELECT
    r.rolname AS rol,
    m.inherit_option AS hereda_permisos,
    m.set_option AS puede_set_role
FROM pg_auth_members m
JOIN pg_roles r ON r.oid = m.roleid
WHERE m.member = 'java_nova'::regrole
ORDER BY r.rolname;

\echo ''
\echo '--- Comprobacion: sin SET ROLE, java_nova no lee pedidos ni hashes'
\echo '    (se esperan dos f)'
SELECT
    has_table_privilege('java_nova', 'public.pedidos', 'SELECT') AS lee_pedidos_sin_set_role,
    has_column_privilege('java_nova', 'public.usuarios', 'password_hash', 'SELECT') AS lee_password_hash;

\echo ''
\echo '===== FIN ====='
