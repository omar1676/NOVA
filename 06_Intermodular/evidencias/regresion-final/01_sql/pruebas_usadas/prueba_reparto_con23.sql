-- Pruebas SQL de 22_reparto_panel.sql (base desechable, copia de nova_reparto montada desde cero).
-- Se ejecuta como postgres; cada prueba se hace con SET ROLE <rol>, que deja exactamente los
-- permisos de ese rol (sin los de superusuario).
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
SELECT min(id_producto_sku) AS sku1 FROM existencias WHERE cantidad >= 5 \gset
SELECT min(id_producto_sku) AS sku2 FROM existencias WHERE cantidad >= 5 AND id_producto_sku > :sku1 \gset

-- Tres compras web de la misma clienta, hechas con las funciones de la tienda (rol tienda_web):
-- una pagada (confirmada), una cancelada y una pendiente
SET ROLE tienda_web;
SELECT registrar_cliente('Rita Reparto', 'rita.reparto@example.com', 'clave-rita-123', NULL, 'Calle Reparto 1, Madrid') AS rita \gset
SELECT crear_compra_web(:rita, 'WEB-BBBBBBBBBBBBBBBBBBB1', ARRAY[:sku1, :sku2], ARRAY[2, 1], NULL, 'Calle Reparto 1, Madrid') AS confirmado \gset
SELECT confirmar_compra_web(:rita, :confirmado) \gset
SELECT crear_compra_web(:rita, 'WEB-BBBBBBBBBBBBBBBBBBB2', ARRAY[:sku1], ARRAY[1], NULL, 'Calle Reparto 1, Madrid') AS cancelado \gset
SELECT cancelar_compra_web(:rita, :cancelado) \gset
SELECT crear_compra_web(:rita, 'WEB-BBBBBBBBBBBBBBBBBBB3', ARRAY[:sku2], ARRAY[1], NULL, 'Calle Reparto 1, Madrid') AS pendiente \gset
RESET ROLE;
SELECT string_agg(estado, ',' ORDER BY id_pedido) AS estados_partida FROM pedidos WHERE id_pedido IN (:confirmado, :cancelado, :pendiente) \gset
\echo 'Partida: pedidos' :confirmado :cancelado :pendiente '->' :estados_partida ' y CUSTOM-40 =' :custom

\echo '=== Quien puede llamar a la funcion'
SET ROLE tienda_web;
SELECT pg_temp.debe_fallar('P1 tienda_web no puede llamarla', format('SELECT marcar_pedido_en_reparto(%s, %s)', :admin, :confirmado), '42501');
RESET ROLE;
SET ROLE tienda_nova;
SELECT pg_temp.debe_fallar('P2 tienda_nova (el usuario de la tienda) tampoco', format('SELECT marcar_pedido_en_reparto(%s, %s)', :admin, :confirmado), '42501');
RESET ROLE;
SET ROLE panel_lectura;
SELECT pg_temp.debe_fallar('P3 panel_lectura (todas las demas rutas del panel) tampoco', format('SELECT marcar_pedido_en_reparto(%s, %s)', :admin, :confirmado), '42501');
RESET ROLE;
SET ROLE web_nova;
SELECT pg_temp.debe_fallar('P4 web_nova sin SET ROLE tampoco (NOINHERIT)', format('SELECT marcar_pedido_en_reparto(%s, %s)', :admin, :confirmado), '42501');
RESET ROLE;
SET ROLE nova_admin;
SELECT pg_temp.debe_fallar('P5 nova_admin (Java) tampoco', format('SELECT marcar_pedido_en_reparto(%s, %s)', :admin, :confirmado), '42501');
RESET ROLE;
SELECT CASE WHEN has_function_privilege('panel_reparto', f, 'EXECUTE')
             AND NOT has_function_privilege('public', f, 'EXECUTE')
             AND NOT has_function_privilege('tienda_web', f, 'EXECUTE')
             AND NOT has_function_privilege('tienda_nova', f, 'EXECUTE')
             AND NOT has_function_privilege('panel_lectura', f, 'EXECUTE')
             AND NOT has_function_privilege('web_nova', f, 'EXECUTE')
             AND NOT has_function_privilege('java_nova', f, 'EXECUTE')
             AND NOT has_function_privilege('nova_trabajador', f, 'EXECUTE')
             AND NOT has_function_privilege('nova_comercial', f, 'EXECUTE')
             AND NOT has_function_privilege('nova_cliente', f, 'EXECUTE')
            THEN 'PASS' ELSE 'FAIL' END || ' P6 EXECUTE solo para panel_reparto (ni PUBLIC, ni tienda, ni panel_lectura, ni Java)'
FROM (SELECT 'public.marcar_pedido_en_reparto(integer, integer)'::regprocedure AS f) x;
SELECT CASE WHEN string_agg(r.rolname || ':' || m.inherit_option || ':' || m.set_option, ' ' ORDER BY r.rolname)
                 = 'panel_lectura:false:true panel_reparto:false:true portal_trabajador:false:true'
            THEN 'PASS' ELSE 'FAIL' END || ' P7 web_nova solo pasa a panel_lectura, panel_reparto y portal_trabajador (23), sin heredar: '
       || string_agg(r.rolname || ' inherit=' || m.inherit_option || ' set=' || m.set_option, ', ' ORDER BY r.rolname)
FROM pg_auth_members m JOIN pg_roles r ON r.oid = m.roleid WHERE m.member = 'web_nova'::regrole;
SELECT CASE WHEN NOT rolcanlogin THEN 'PASS' ELSE 'FAIL' END || ' P8 panel_reparto no tiene login' FROM pg_roles WHERE rolname = 'panel_reparto';
SELECT CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END || ' P9 panel_reparto no puede leer ni escribir ninguna tabla de public: ' || count(*)
FROM pg_tables t WHERE t.schemaname = 'public'
  AND (has_any_column_privilege('panel_reparto', format('%I.%I', t.schemaname, t.tablename), 'SELECT, INSERT, UPDATE, REFERENCES')
       OR has_table_privilege('panel_reparto', format('%I.%I', t.schemaname, t.tablename), 'DELETE, TRUNCATE, TRIGGER'));
SELECT CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END || ' P10 panel_lectura sigue sin poder escribir en ninguna tabla: ' || count(*)
FROM pg_tables t WHERE t.schemaname = 'public'
  AND (has_any_column_privilege('panel_lectura', format('%I.%I', t.schemaname, t.tablename), 'INSERT, UPDATE')
       OR has_table_privilege('panel_lectura', format('%I.%I', t.schemaname, t.tablename), 'DELETE, TRUNCATE'));
SET ROLE panel_reparto;
SELECT pg_temp.debe_fallar('P11 panel_reparto no lee pedidos', 'SELECT count(*) FROM pedidos', '42501');
SELECT pg_temp.debe_fallar('P12 panel_reparto no cambia el estado a mano', format($q$UPDATE pedidos SET estado = 'enviado' WHERE id_pedido = %s$q$, :confirmado), '42501');
SELECT pg_temp.debe_fallar('P13 panel_reparto no toca existencias', 'UPDATE existencias SET cantidad = 0', '42501');
SELECT pg_temp.debe_fallar('P14 panel_reparto no escribe en la auditoria', $q$INSERT INTO log_eventos (tabla_afectada, accion) VALUES ('x', 'x')$q$, '42501');
SELECT pg_temp.debe_fallar('P15 panel_reparto no hace login (iniciar_sesion)', $q$SELECT iniciar_sesion('admin.demo', 'x')$q$, '42501');
SELECT pg_temp.debe_fallar('P16 panel_reparto no llama a las funciones de la tienda', format('SELECT confirmar_compra_web(%s, %s)', :rita, :pendiente), '42501');
RESET ROLE;
SET ROLE panel_lectura;
SELECT pg_temp.debe_fallar('P17 panel_lectura sigue sin poder cambiar pedidos', format($q$UPDATE pedidos SET estado = 'enviado' WHERE id_pedido = %s$q$, :confirmado), '42501');
RESET ROLE;
SELECT CASE WHEN p.prosecdef AND p.proconfig = ARRAY['search_path=pg_catalog, public, extensiones'] THEN 'PASS' ELSE 'FAIL' END
       || ' P18 SECURITY DEFINER con search_path fijo: ' || array_to_string(p.proconfig, ' ')
FROM pg_proc p WHERE p.oid = 'public.marcar_pedido_en_reparto(integer, integer)'::regprocedure;

\echo '=== Reglas de la funcion (como panel_reparto, que es lo que usa el servidor)'
SELECT sum(cantidad) AS stock_antes FROM existencias \gset
SELECT COALESCE(max(id_evento), 0) AS ultimo_evento FROM log_eventos \gset
SET ROLE panel_reparto;
SELECT pg_temp.debe_fallar('F1 un trabajador (taller.demo) no puede', format('SELECT marcar_pedido_en_reparto(%s, %s)', :taller, :confirmado), 'Usuario no autorizado');
SELECT pg_temp.debe_fallar('F2 un comercial (tienda.demo) no puede', format('SELECT marcar_pedido_en_reparto(%s, %s)', :comercial, :confirmado), 'Usuario no autorizado');
SELECT pg_temp.debe_fallar('F3 un usuario que no existe', format('SELECT marcar_pedido_en_reparto(999999, %s)', :confirmado), 'Usuario no autorizado');
SELECT pg_temp.debe_fallar('F4 sin usuario (NULL)', format('SELECT marcar_pedido_en_reparto(NULL, %s)', :confirmado), 'Usuario no autorizado');
SELECT pg_temp.debe_fallar('F5 un pedido pendiente (sin pagar)', format('SELECT marcar_pedido_en_reparto(%s, %s)', :admin, :pendiente), 'Solo se puede pasar a reparto un pedido confirmado');
SELECT pg_temp.debe_fallar('F6 un pedido cancelado', format('SELECT marcar_pedido_en_reparto(%s, %s)', :admin, :cancelado), 'Solo se puede pasar a reparto un pedido confirmado');
SELECT pg_temp.debe_fallar('F7 un pedido que no existe', format('SELECT marcar_pedido_en_reparto(%s, 999999)', :admin), 'El pedido no existe');
RESET ROLE;
UPDATE usuarios SET activo = false WHERE id_usuario = :admin;
SET ROLE panel_reparto;
SELECT pg_temp.debe_fallar('F8 un administrador desactivado', format('SELECT marcar_pedido_en_reparto(%s, %s)', :admin, :confirmado), 'Usuario no autorizado');
RESET ROLE;
UPDATE usuarios SET activo = true WHERE id_usuario = :admin;
SELECT CASE WHEN string_agg(estado, ',' ORDER BY id_pedido) = :'estados_partida' THEN 'PASS' ELSE 'FAIL' END
       || ' F9 los intentos rechazados no cambian nada: ' || string_agg(estado, ',' ORDER BY id_pedido)
FROM pedidos WHERE id_pedido IN (:confirmado, :cancelado, :pendiente);
SELECT CASE WHEN count(*) = 0 THEN 'PASS' ELSE 'FAIL' END || ' F10 ni dejan nada en la auditoria: ' || count(*) || ' eventos'
FROM log_eventos WHERE id_evento > :ultimo_evento;

\echo '=== Un pedido confirmado pasa a enviado'
SET ROLE panel_reparto;
SELECT marcar_pedido_en_reparto(:admin, :confirmado) \gset
SELECT CASE WHEN COALESCE(current_setting('nova.id_usuario', true), '') = '' THEN 'PASS' ELSE 'FAIL' END
       || ' F11 no deja una sesion abierta: nova.id_usuario vuelve a estar vacio';
RESET ROLE;
SELECT CASE WHEN estado = 'enviado' AND estado_pago = 'pagado' THEN 'PASS' ELSE 'FAIL' END
       || ' F12 el pedido confirmado pasa a enviado (sigue pagado): ' || estado || ' / ' || estado_pago
FROM pedidos WHERE id_pedido = :confirmado;
SELECT CASE WHEN sum(cantidad) = :stock_antes THEN 'PASS' ELSE 'FAIL' END || ' F13 el stock no cambia: ' || :stock_antes || ' -> ' || sum(cantidad)
FROM existencias;
SELECT CASE WHEN bool_and(stock_descontado) AND count(*) = 2 THEN 'PASS' ELSE 'FAIL' END || ' F14 las lineas siguen con el stock descontado una vez'
FROM linea_pedido WHERE id_pedido = :confirmado;
SELECT CASE WHEN count(*) = 1 AND min(l.accion) = 'CAMBIO_ESTADO' AND min(u.username) = 'admin.demo'
             AND min(l.detalle) LIKE 'Pedido WEB-BBBBBBBBBBBBBBBBBBB1: confirmado -> enviado%'
            THEN 'PASS' ELSE 'FAIL' END
       || ' F15 log_eventos apunta un CAMBIO_ESTADO con admin.demo (y nada mas): '
       || string_agg(l.accion || ' | ' || COALESCE(u.username, 'sin usuario') || ' | ' || l.detalle, ' ; ')
FROM log_eventos l LEFT JOIN usuarios u ON u.id_usuario = l.id_usuario
WHERE l.id_evento > :ultimo_evento;
SET ROLE panel_reparto;
SELECT pg_temp.debe_fallar('F16 otra vez el mismo pedido (ya enviado)', format('SELECT marcar_pedido_en_reparto(%s, %s)', :admin, :confirmado), 'Solo se puede pasar a reparto un pedido confirmado');
RESET ROLE;

\echo '=== La sesion de quien llama se respeta y READ ONLY sigue mandando'
BEGIN;
SELECT set_config('nova.id_usuario', 'valor-de-antes', true) \gset
SET LOCAL ROLE panel_reparto;
SELECT marcar_pedido_en_reparto(:admin, :custom) \gset
SELECT CASE WHEN current_setting('nova.id_usuario', true) = 'valor-de-antes' THEN 'PASS' ELSE 'FAIL' END
       || ' F17 si ya habia un valor en nova.id_usuario, la funcion lo deja como estaba';
ROLLBACK;
SELECT CASE WHEN estado = 'confirmado' THEN 'PASS' ELSE 'FAIL' END || ' F18 con ROLLBACK no queda nada (CUSTOM-40 sigue confirmado)'
FROM pedidos WHERE id_pedido = :custom;
BEGIN READ ONLY;
SET LOCAL ROLE panel_reparto;
SELECT pg_temp.debe_fallar('F19 dentro de una transaccion READ ONLY no se puede (como en el resto del panel)', format('SELECT marcar_pedido_en_reparto(%s, %s)', :admin, :custom), '25006');
ROLLBACK;
\echo '=== Fin'
