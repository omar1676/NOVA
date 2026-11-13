-- Pruebas SQL de 23_portal_trabajador.sql (base desechable de la candidata 2, montada desde cero).
-- Se ejecuta como postgres; cada prueba se hace con SET ROLE <rol>, que deja exactamente los
-- permisos de ese rol (sin los de superusuario). Mismo formato que prueba_reparto.sql (22).
\set QUIET on
\pset footer off
\set VERBOSITY terse

CREATE OR REPLACE FUNCTION pg_temp.debe_fallar(p_nombre text, p_sql text, p_esperado text)
RETURNS text LANGUAGE plpgsql AS $$
BEGIN
    EXECUTE p_sql;
    RETURN 'FAIL ' || p_nombre || ': se ejecuto sin error';
EXCEPTION WHEN others THEN
    IF SQLSTATE = p_esperado OR SQLERRM LIKE p_esperado THEN
        RETURN 'PASS ' || p_nombre || ': ' || SQLSTATE || ' ' || SQLERRM;
    END IF;
    RETURN 'FAIL ' || p_nombre || ': error inesperado ' || SQLSTATE || ' ' || SQLERRM;
END $$;

-- Datos de partida
SELECT id_usuario AS admin FROM usuarios WHERE username = 'admin.demo' \gset
SELECT id_usuario AS taller FROM usuarios WHERE username = 'taller.demo' \gset
SELECT id_usuario AS comercial FROM usuarios WHERE username = 'tienda.demo' \gset
SELECT id_pedido AS custom FROM pedidos WHERE referencia = 'CUSTOM-40' AND estado = 'confirmado' \gset
SELECT id_pedido AS pendiente FROM pedidos WHERE estado = 'pendiente' ORDER BY id_pedido LIMIT 1 \gset
SELECT id_producto_sku AS sku, id_nave AS nave, cantidad AS stock_sku FROM existencias ORDER BY id_existencia LIMIT 1 \gset
\echo 'Partida: CUSTOM-40 =' :custom ', pendiente =' :pendiente ', SKU' :sku 'nave' :nave 'con' :stock_sku

\echo '=== Quien puede llamar a las funciones'
SET ROLE tienda_web;
SELECT pg_temp.debe_fallar('Q1 tienda_web no puede avanzar pedidos', format($q$SELECT * FROM avanzar_pedido_trabajador(%s, %s, 'en_preparacion')$q$, :taller, :custom), '42501');
SELECT pg_temp.debe_fallar('Q2 tienda_web no puede cambiar el stock', format('SELECT * FROM ajustar_existencias_trabajador(%s, %s, %s, 1)', :taller, :sku, :nave), '42501');
RESET ROLE;
SET ROLE panel_lectura;
SELECT pg_temp.debe_fallar('Q3 panel_lectura (el panel) tampoco', format($q$SELECT * FROM avanzar_pedido_trabajador(%s, %s, 'en_preparacion')$q$, :taller, :custom), '42501');
RESET ROLE;
SET ROLE panel_reparto;
SELECT pg_temp.debe_fallar('Q4 panel_reparto tampoco', format('SELECT * FROM ajustar_existencias_trabajador(%s, %s, %s, 1)', :taller, :sku, :nave), '42501');
RESET ROLE;
SET ROLE web_nova;
SELECT pg_temp.debe_fallar('Q5 web_nova sin SET ROLE tampoco (NOINHERIT)', format($q$SELECT * FROM avanzar_pedido_trabajador(%s, %s, 'en_preparacion')$q$, :taller, :custom), '42501');
RESET ROLE;
SET ROLE nova_trabajador;
SELECT pg_temp.debe_fallar('Q6 nova_trabajador (Java) tampoco', format('SELECT * FROM ajustar_existencias_trabajador(%s, %s, %s, 1)', :taller, :sku, :nave), '42501');
RESET ROLE;
SELECT CASE WHEN bool_and(has_function_privilege('portal_trabajador', f, 'EXECUTE'))
             AND NOT bool_or(has_function_privilege('public', f, 'EXECUTE'))
             AND NOT bool_or(has_function_privilege('tienda_nova', f, 'EXECUTE'))
             AND NOT bool_or(has_function_privilege('java_nova', f, 'EXECUTE'))
             AND NOT bool_or(has_function_privilege('nova_admin', f, 'EXECUTE'))
             AND NOT bool_or(has_function_privilege('nova_comercial', f, 'EXECUTE'))
             AND NOT bool_or(has_function_privilege('nova_cliente', f, 'EXECUTE'))
            THEN 'PASS' ELSE 'FAIL' END || ' Q7 EXECUTE solo para portal_trabajador (ni PUBLIC, ni tienda, ni Java)'
FROM (VALUES ('public.avanzar_pedido_trabajador(integer, integer, character varying)'::regprocedure),
             ('public.ajustar_existencias_trabajador(integer, integer, integer, integer)'::regprocedure)) x(f);
SELECT CASE WHEN m.inherit_option = false AND m.set_option = true THEN 'PASS' ELSE 'FAIL' END
       || ' Q8 web_nova pasa a portal_trabajador solo con SET ROLE (sin heredar)'
FROM pg_auth_members m WHERE m.member = 'web_nova'::regrole AND m.roleid = 'portal_trabajador'::regrole;
SELECT CASE WHEN NOT rolcanlogin THEN 'PASS' ELSE 'FAIL' END || ' Q9 portal_trabajador no tiene login' FROM pg_roles WHERE rolname = 'portal_trabajador';
SELECT CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END || ' Q10 portal_trabajador no escribe en ninguna tabla de public: ' || count(*)
FROM pg_tables t WHERE t.schemaname = 'public'
  AND (has_any_column_privilege('portal_trabajador', format('%I.%I', t.schemaname, t.tablename), 'INSERT, UPDATE, REFERENCES')
       OR has_table_privilege('portal_trabajador', format('%I.%I', t.schemaname, t.tablename), 'DELETE, TRUNCATE, TRIGGER'));
SELECT CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END || ' Q11 panel_lectura sigue sin poder escribir en ninguna tabla: ' || count(*)
FROM pg_tables t WHERE t.schemaname = 'public'
  AND (has_any_column_privilege('panel_lectura', format('%I.%I', t.schemaname, t.tablename), 'INSERT, UPDATE')
       OR has_table_privilege('panel_lectura', format('%I.%I', t.schemaname, t.tablename), 'DELETE, TRUNCATE'));
SELECT CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END || ' Q12 panel_reparto sigue sin leer ni escribir ninguna tabla: ' || count(*)
FROM pg_tables t WHERE t.schemaname = 'public'
  AND (has_any_column_privilege('panel_reparto', format('%I.%I', t.schemaname, t.tablename), 'SELECT, INSERT, UPDATE')
       OR has_table_privilege('panel_reparto', format('%I.%I', t.schemaname, t.tablename), 'DELETE, TRUNCATE'));
SET ROLE portal_trabajador;
SELECT pg_temp.debe_fallar('Q13 portal_trabajador no cambia el estado a mano', format($q$UPDATE pedidos SET estado = 'enviado' WHERE id_pedido = %s$q$, :custom), '42501');
SELECT pg_temp.debe_fallar('Q14 portal_trabajador no toca existencias a mano', 'UPDATE existencias SET cantidad = 0', '42501');
SELECT pg_temp.debe_fallar('Q15 portal_trabajador no escribe en la auditoria', $q$INSERT INTO log_eventos (tabla_afectada, accion) VALUES ('x', 'x')$q$, '42501');
SELECT pg_temp.debe_fallar('Q16 portal_trabajador no lee la auditoria', 'SELECT count(*) FROM log_eventos', '42501');
SELECT pg_temp.debe_fallar('Q17 portal_trabajador no lee el hash', 'SELECT password_hash FROM usuarios', '42501');
SELECT pg_temp.debe_fallar('Q18 portal_trabajador no lee el DNI', 'SELECT dni FROM personal', '42501');
SELECT pg_temp.debe_fallar('Q19 portal_trabajador no lee el correo ni la direccion de los clientes', 'SELECT email, direccion_entrega FROM clientes', '42501');
SELECT pg_temp.debe_fallar('Q20 portal_trabajador no lee las cuentas de la tienda', 'SELECT count(*) FROM cuentas_cliente', '42501');
SELECT pg_temp.debe_fallar('Q21 portal_trabajador no marca en reparto (22)', format('SELECT marcar_pedido_en_reparto(%s, %s)', :admin, :custom), '42501');
SELECT pg_temp.debe_fallar('Q22 portal_trabajador no hace login (iniciar_sesion)', $q$SELECT iniciar_sesion('taller.demo', 'x')$q$, '42501');
SELECT pg_temp.debe_fallar('Q23 portal_trabajador no compra (realizar_compra)', $q$SELECT realizar_compra('X-1', 1, 1, 1, 1)$q$, '42501');
SELECT CASE WHEN count(*) > 0 THEN 'PASS' ELSE 'FAIL' END || ' Q24 portal_trabajador lee lo que ensena el portal (pedidos con su personalizacion)'
FROM (SELECT referencia, personalizacion, fecha_objetivo FROM pedidos) x;
RESET ROLE;
SELECT CASE WHEN bool_and(p.prosecdef AND p.proconfig = ARRAY['search_path=pg_catalog, public, extensiones']) AND count(*) = 2
            THEN 'PASS' ELSE 'FAIL' END || ' Q25 las dos son SECURITY DEFINER con search_path fijo'
FROM pg_proc p WHERE p.oid IN ('public.avanzar_pedido_trabajador(integer, integer, character varying)'::regprocedure,
                               'public.ajustar_existencias_trabajador(integer, integer, integer, integer)'::regprocedure);

\echo '=== Reglas de las funciones (como portal_trabajador, que es lo que usa el servidor)'
SELECT sum(cantidad) AS stock_antes FROM existencias \gset
SELECT COALESCE(max(id_evento), 0) AS ultimo_evento FROM log_eventos \gset
SET ROLE portal_trabajador;
SELECT pg_temp.debe_fallar('R1 el administrador no usa el portal', format($q$SELECT * FROM avanzar_pedido_trabajador(%s, %s, 'en_preparacion')$q$, :admin, :custom), 'Usuario no autorizado');
SELECT pg_temp.debe_fallar('R2 un comercial tampoco', format($q$SELECT * FROM avanzar_pedido_trabajador(%s, %s, 'en_preparacion')$q$, :comercial, :custom), 'Usuario no autorizado');
SELECT pg_temp.debe_fallar('R3 un usuario que no existe', format($q$SELECT * FROM avanzar_pedido_trabajador(999999, %s, 'en_preparacion')$q$, :custom), 'Usuario no autorizado');
SELECT pg_temp.debe_fallar('R4 sin usuario (NULL)', format('SELECT * FROM ajustar_existencias_trabajador(NULL, %s, %s, 1)', :sku, :nave), 'Usuario no autorizado');
SELECT pg_temp.debe_fallar('R5 el administrador no cambia stock por el portal', format('SELECT * FROM ajustar_existencias_trabajador(%s, %s, %s, 1)', :admin, :sku, :nave), 'Usuario no autorizado');
SELECT pg_temp.debe_fallar('R6 saltarse un paso (confirmado -> enviado)', format($q$SELECT * FROM avanzar_pedido_trabajador(%s, %s, 'enviado')$q$, :taller, :custom), 'Solo se puede pasar de confirmado a en_preparacion');
SELECT pg_temp.debe_fallar('R7 volver atras o cancelar', format($q$SELECT * FROM avanzar_pedido_trabajador(%s, %s, 'cancelado')$q$, :taller, :custom), 'Solo se puede pasar de confirmado a en_preparacion');
SELECT pg_temp.debe_fallar('R8 un pedido pendiente no avanza', format($q$SELECT * FROM avanzar_pedido_trabajador(%s, %s, 'en_preparacion')$q$, :taller, :pendiente), 'Un pedido en estado pendiente no se puede avanzar');
SELECT pg_temp.debe_fallar('R9 un pedido que no existe', format($q$SELECT * FROM avanzar_pedido_trabajador(%s, 999999, 'en_preparacion')$q$, :taller), 'El pedido no existe');
SELECT pg_temp.debe_fallar('R10 una cantidad negativa', format('SELECT * FROM ajustar_existencias_trabajador(%s, %s, %s, -1)', :taller, :sku, :nave), 'La cantidad debe ser%');
SELECT pg_temp.debe_fallar('R11 una cantidad enorme', format('SELECT * FROM ajustar_existencias_trabajador(%s, %s, %s, 100000)', :taller, :sku, :nave), 'La cantidad debe ser%');
SELECT pg_temp.debe_fallar('R12 unas existencias que no existen', format('SELECT * FROM ajustar_existencias_trabajador(%s, 999999, %s, 1)', :taller, :nave), 'No existe esa existencia');
RESET ROLE;
UPDATE usuarios SET activo = false WHERE id_usuario = :taller;
SET ROLE portal_trabajador;
SELECT pg_temp.debe_fallar('R13 un trabajador desactivado', format($q$SELECT * FROM avanzar_pedido_trabajador(%s, %s, 'en_preparacion')$q$, :taller, :custom), 'Usuario no autorizado');
SELECT pg_temp.debe_fallar('R14 un trabajador desactivado no cambia stock', format('SELECT * FROM ajustar_existencias_trabajador(%s, %s, %s, 1)', :taller, :sku, :nave), 'Usuario no autorizado');
RESET ROLE;
UPDATE usuarios SET activo = true WHERE id_usuario = :taller;
SELECT CASE WHEN estado = 'confirmado' THEN 'PASS' ELSE 'FAIL' END || ' R15 los intentos rechazados no cambian el pedido' FROM pedidos WHERE id_pedido = :custom;
SELECT CASE WHEN sum(cantidad) = :stock_antes THEN 'PASS' ELSE 'FAIL' END || ' R16 ni el stock' FROM existencias;
SELECT CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END || ' R17 ni dejan nada en la auditoria: ' || count(*) || ' eventos'
FROM log_eventos WHERE id_evento > :ultimo_evento;

\echo '=== Un pedido avanza paso a paso y el stock cambia, a nombre del trabajador'
SET ROLE portal_trabajador;
SELECT estado AS paso1 FROM avanzar_pedido_trabajador(:taller, :custom, 'en_preparacion') \gset
SELECT CASE WHEN COALESCE(current_setting('nova.id_usuario', true), '') = '' THEN 'PASS' ELSE 'FAIL' END
       || ' R18 no deja una sesion abierta: nova.id_usuario vuelve a estar vacio';
SELECT estado AS paso2 FROM avanzar_pedido_trabajador(:taller, :custom, 'enviado') \gset
SELECT estado AS paso3 FROM avanzar_pedido_trabajador(:taller, :custom, 'entregado') \gset
SELECT pg_temp.debe_fallar('R19 entregado ya no avanza', format($q$SELECT * FROM avanzar_pedido_trabajador(%s, %s, 'entregado')$q$, :taller, :custom), 'Un pedido en estado entregado no se puede avanzar');
SELECT cantidad AS nueva FROM ajustar_existencias_trabajador(:taller, :sku, :nave, :stock_sku + 4) \gset
RESET ROLE;
SELECT CASE WHEN :'paso1' = 'en_preparacion' AND :'paso2' = 'enviado' AND :'paso3' = 'entregado' AND estado = 'entregado'
            THEN 'PASS' ELSE 'FAIL' END || ' R20 confirmado -> en_preparacion -> enviado -> entregado: ' || estado
FROM pedidos WHERE id_pedido = :custom;
SELECT CASE WHEN sum(cantidad) = :stock_antes + 4 THEN 'PASS' ELSE 'FAIL' END
       || ' R21 avanzar no toca el stock; solo cambia el SKU ajustado (+4): ' || :stock_antes || ' -> ' || sum(cantidad)
FROM existencias;
SELECT CASE WHEN count(*) = 4
             AND bool_and(u.username = 'taller.demo')
             AND count(*) FILTER (WHERE l.accion = 'CAMBIO_ESTADO') = 3
             AND count(*) FILTER (WHERE l.accion = 'CAMBIO_STOCK' AND l.detalle = format('SKU %s: %s -> %s', :sku, :stock_sku, :stock_sku + 4)) = 1
            THEN 'PASS' ELSE 'FAIL' END
       || ' R22 log_eventos: 3 CAMBIO_ESTADO y 1 CAMBIO_STOCK, todos con taller.demo: '
       || string_agg(l.accion || ' | ' || COALESCE(u.username, 'sin usuario') || ' | ' || l.detalle, ' ; ' ORDER BY l.id_evento)
FROM log_eventos l LEFT JOIN usuarios u ON u.id_usuario = l.id_usuario
WHERE l.id_evento > :ultimo_evento;

\echo '=== La sesion de quien llama se respeta y READ ONLY sigue mandando'
BEGIN;
SELECT set_config('nova.id_usuario', 'valor-de-antes', true) \gset
SET LOCAL ROLE portal_trabajador;
SELECT cantidad FROM ajustar_existencias_trabajador(:taller, :sku, :nave, 1) \gset
SELECT CASE WHEN current_setting('nova.id_usuario', true) = 'valor-de-antes' THEN 'PASS' ELSE 'FAIL' END
       || ' R23 si ya habia un valor en nova.id_usuario, la funcion lo deja como estaba';
ROLLBACK;
SELECT CASE WHEN cantidad = :stock_sku + 4 THEN 'PASS' ELSE 'FAIL' END || ' R24 con ROLLBACK no queda nada'
FROM existencias WHERE id_producto_sku = :sku AND id_nave = :nave;
BEGIN READ ONLY;
SET LOCAL ROLE portal_trabajador;
SELECT pg_temp.debe_fallar('R25 dentro de una transaccion READ ONLY no se puede (como las lecturas del portal)', format('SELECT * FROM ajustar_existencias_trabajador(%s, %s, %s, 1)', :taller, :sku, :nave), '25006');
ROLLBACK;
\echo '=== Fin'
