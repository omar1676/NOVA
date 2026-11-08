\echo '===== ACTIVAR LAS CUENTAS DE DEMOSTRACION ====='
\echo ''
\echo 'Las tres cuentas se instalan con password_hash = ! , que no es un hash y'
\echo 'no deja entrar a nadie. Este script pide las contrasenas por teclado y las'
\echo 'guarda cifradas con bcrypt. No se escribe ninguna contrasena en el'
\echo 'repositorio ni en este archivo.'
\echo ''
\echo 'Hay que lanzarlo con el usuario que instalo la base:'
\echo '  psql -U postgres -d nova_sneakers -f 13_activar_usuarios.sql'
\echo ''
\echo 'Minimo 8 caracteres. Al menos la cuenta admin.demo hace falta para que'
\echo 'Java pueda hacer el primer inicio de sesion.'
\echo ''

\prompt 'Contrasena para admin.demo   : ' clave_admin
SELECT public.establecer_password('admin.demo', :'clave_admin') AS admin_demo_lista;

\prompt 'Contrasena para taller.demo  : ' clave_taller
SELECT public.establecer_password('taller.demo', :'clave_taller') AS taller_demo_lista;

\prompt 'Contrasena para tienda.demo  : ' clave_tienda
SELECT public.establecer_password('tienda.demo', :'clave_tienda') AS tienda_demo_lista;

\unset clave_admin
\unset clave_taller
\unset clave_tienda

\echo ''
\echo '--- comprobacion: las tres cuentas tienen ya un hash bcrypt'
SELECT
    u.username,
    r.nombre AS rol,
    u.activo,
    CASE WHEN left(u.password_hash, 4) = '$2a$' THEN 'lista' ELSE 'SIN CONTRASENA' END AS estado
FROM public.usuarios u
JOIN public.roles r ON r.id_rol = u.id_rol
ORDER BY u.id_usuario;

\echo ''
\echo '--- comprobacion: el login funciona'
\echo '    (si esto falla, la contrasena escrita y la tecleada no coinciden)'
\prompt 'Repite la contrasena de admin.demo para probar el login: ' clave_prueba
SELECT
    CASE WHEN public.iniciar_sesion('admin.demo', :'clave_prueba') IS NOT NULL
         THEN 'LOGIN CORRECTO'
         ELSE 'LOGIN FALLIDO' END AS resultado;
\unset clave_prueba

\echo ''
\echo '===== FIN ====='
