-- =====================================================================
-- 14_caso_custom_persistente.sql
--
-- Deja el pedido CUSTOM-40 guardado de verdad en la base de
-- demostracion: 40 pares, 10 de cada talla 40, 41, 42 y 43.
--
-- POR QUE EXISTE ESTE ARCHIVO
--   10_caso_custom.sql prueba el caso dentro de BEGIN ... ROLLBACK, asi
--   que al terminar no queda nada en la base. Eso esta bien para probar,
--   pero la exportacion de fabricacion no puede leer datos que
--   desaparecen. Este archivo guarda el pedido una sola vez.
--
-- SE PUEDE EJECUTAR LAS VECES QUE SE QUIERA
--   Si CUSTOM-40 ya existe y esta bien, lo dice y no toca nada: no
--   duplica el pedido, no duplica lineas y no vuelve a descontar stock.
--   Si existe pero esta mal (cancelado, con otras cantidades o con otras
--   tallas), se detiene con un error que explica lo que ha encontrado.
--   No intenta arreglarlo por su cuenta.
--
-- NO BORRA NI MODIFICA NINGUN OTRO PEDIDO
--   Solo anade CUSTOM-40. Los pedidos NOVA-0001 a NOVA-0011 se quedan
--   como estaban.
--
-- QUE PERMISOS HACEN FALTA
--   Hay que lanzarlo como postgres o con el rol nova_admin: crea el
--   pedido, lo marca como Custom, lee log_eventos para comprobar la
--   auditoria y usuarios para el resumen. Comprobado rol por rol (13/11):
--   nova_comercial falla al leer log_eventos, nova_trabajador al llamar a
--   realizar_compra y nova_cliente al leer pedidos ("permission denied").
--
-- QUE HAY QUE HABER EJECUTADO ANTES
--   1. La instalacion completa, incluido 05_datos_prueba.sql.
--   2. 13_activar_usuarios.sql, porque este script inicia sesion como
--      tienda.demo y las cuentas se instalan sin contrasena utilizable.
--
-- LA CONTRASENA NO SE GUARDA EN NINGUN SITIO
--   Se pide por teclado con \prompt, igual que en 13_activar_usuarios.sql,
--   y se borra con \unset al terminar. No se escribe en el repositorio ni
--   se cambia ninguna contrasena de demostracion.
--
-- CUANDO SE EJECUTA: AL FINAL, DESPUES DE LAS PRUEBAS
--   Este archivo anade un pedido, asi que la base deja de tener 11
--   pedidos y 14 lineas. El orden correcto es:
--     1. instalacion:  esquema, 04, 02, 03, 05, 07, 08
--     2. pruebas:      06, 09, 10, 11, 12
--     3. contrasenas:  13
--     4. este archivo: 14   -> deja CUSTOM-40 confirmado
--     5. exportacion:  15   -> escribe el CSV
--
--   El 13 va DESPUES de las pruebas, no antes: las comprobaciones A1 y A2
--   verifican que las cuentas llegan sin contrasena utilizable, y si el 13
--   ya se ha ejecutado esas dos dan FAIL con razon.
--
-- COMO SE EJECUTA
--   psql -U postgres -d nova_sneakers -f 14_caso_custom_persistente.sql
-- =====================================================================

\set ON_ERROR_STOP on

\echo '===== Caso Custom: dejar CUSTOM-40 guardado en la base ====='
\echo ''
\echo 'Se necesita la contrasena de tienda.demo para que el pedido y su'
\echo 'auditoria queden a nombre de un operador identificado.'
\echo ''

\prompt 'Contrasena de tienda.demo: ' clave_tienda

-- ---------------------------------------------------------------------
-- Todo va en una sola transaccion, y la sesion se abre DENTRO de ella.
--
-- iniciar_sesion guarda el operador con set_config(..., true), y ese
-- "true" significa que el valor solo vale hasta el final de la
-- transaccion. Por eso hay que iniciar sesion aqui, despues del BEGIN:
-- si se hiciera antes, los triggers de auditoria no verian al operador.
-- ---------------------------------------------------------------------
BEGIN;

SELECT public.iniciar_sesion('tienda.demo', :'clave_tienda') AS operador;

DO $$
DECLARE
    v_pedido  integer;
    v_cliente integer;
    v_nave    integer;
    v_sku     integer;
    v_talla   integer;
    v_pares   integer;
    v_tallas  integer;
    v_estado  varchar(25);
    v_operador integer;
BEGIN
    -- La sesion tiene que estar viva aqui dentro, o la auditoria se
    -- quedaria sin operador.
    v_operador := public.usuario_sesion();

    IF v_operador IS NULL THEN
        RAISE EXCEPTION
            'No hay operador en la sesion. Hay que iniciar sesion dentro de esta misma transaccion';
    END IF;

    -- -----------------------------------------------------------------
    -- 1. Si el pedido ya esta, se comprueba y no se vuelve a crear.
    -- -----------------------------------------------------------------
    SELECT id_pedido, estado
      INTO v_pedido, v_estado
      FROM public.pedidos
     WHERE referencia = 'CUSTOM-40';

    IF v_pedido IS NOT NULL THEN
        SELECT coalesce(sum(l.cantidad), 0), count(DISTINCT s.talla)
          INTO v_pares, v_tallas
          FROM public.linea_pedido l
          JOIN public.producto_sku s
            ON s.id_producto_sku = l.id_producto_sku
         WHERE l.id_pedido = v_pedido;

        IF v_estado <> 'confirmado' THEN
            RAISE EXCEPTION
                'CUSTOM-40 ya existe (id %) pero esta en estado "%". Un pedido que no esta confirmado no sirve para fabricar: revisalo a mano antes de seguir',
                v_pedido, v_estado;
        END IF;

        IF v_pares <> 40 THEN
            RAISE EXCEPTION
                'CUSTOM-40 ya existe (id %) pero tiene % pares y deberia tener 40',
                v_pedido, v_pares;
        END IF;

        IF v_tallas <> 4 THEN
            RAISE EXCEPTION
                'CUSTOM-40 ya existe (id %) pero tiene % tallas distintas y deberian ser 4',
                v_pedido, v_tallas;
        END IF;

        RAISE NOTICE
            'CUSTOM-40 ya existe (id %), confirmado, con 40 pares en 4 tallas. No se cambia nada.',
            v_pedido;
        RETURN;
    END IF;

    -- -----------------------------------------------------------------
    -- 2. Localizar cliente y nave por sus claves naturales.
    --    Ningun identificador escrito a mano.
    -- -----------------------------------------------------------------
    SELECT id_cliente INTO v_cliente
      FROM public.clientes
     WHERE email = 'club.atletico@example.com';

    IF v_cliente IS NULL THEN
        RAISE EXCEPTION
            'No existe el cliente club.atletico@example.com. Ejecuta antes 05_datos_prueba.sql';
    END IF;

    SELECT min(id_nave) INTO v_nave FROM public.nave;

    IF v_nave IS NULL THEN
        RAISE EXCEPTION 'No hay ninguna nave registrada';
    END IF;

    -- -----------------------------------------------------------------
    -- 3. Crear el pedido con la talla 40 y anadir las otras tres.
    --    10 pares de cada talla: 40 pares en total.
    -- -----------------------------------------------------------------
    FOR v_talla IN 40..43 LOOP
        SELECT s.id_producto_sku INTO v_sku
          FROM public.producto_sku s
          JOIN public.variantes v ON v.id_variante = s.id_variante
          JOIN public.modelos m   ON m.id_modelo   = v.id_modelo
         WHERE m.nombre = 'NOVA Velocity'
           AND v.color  = 'Rojo'
           AND s.talla  = v_talla;

        IF v_sku IS NULL THEN
            RAISE EXCEPTION
                'No existe el SKU de NOVA Velocity Rojo talla %', v_talla;
        END IF;

        IF v_pedido IS NULL THEN
            v_pedido := public.realizar_compra(
                'CUSTOM-40', v_cliente, v_sku, v_nave, 10, v_operador);

            UPDATE public.pedidos
               SET personalizado   = true,
                   personalizacion = 'Club Atletico NOVA: logo bordado y numeracion en el talon'
             WHERE id_pedido = v_pedido;
        ELSE
            PERFORM public.anadir_linea_pedido(v_pedido, v_sku, v_nave, 10);
        END IF;
    END LOOP;

    -- -----------------------------------------------------------------
    -- 4. Confirmarlo. El trigger descuenta el stock una sola vez y
    --    marca stock_descontado en cada linea. Si no hubiera
    --    existencias, la excepcion deshace todo y no queda nada.
    -- -----------------------------------------------------------------
    UPDATE public.pedidos
       SET estado = 'confirmado'
     WHERE id_pedido = v_pedido;

    RAISE NOTICE
        'CUSTOM-40 creado y confirmado (id %) por el operador %: 40 pares en 4 tallas.',
        v_pedido, v_operador;
END
$$;

-- ---------------------------------------------------------------------
-- Comprobaciones, dentro de la misma transaccion.
--
-- Cada una lanza un error si no se cumple, en lugar de imprimir FAIL y
-- seguir: asi psql termina con un codigo de salida distinto de cero y
-- quien llame al script se entera de que algo ha ido mal.
-- ---------------------------------------------------------------------
DO $$
DECLARE
    v_pedido     integer;   -- el id del pedido CUSTOM-40
    v_cuantos    integer;   -- cuantos pedidos CUSTOM-40 hay
    v_pares      integer;   -- pares que suma el pedido
    v_tallas     integer;   -- tallas distintas que tiene
    v_tallas_mal integer;   -- tallas que no tienen 10 pares
    v_lineas     integer;
    v_skus       integer;
    v_marcadas   integer;
    v_negativas  integer;
    v_nova       integer;
    v_estado     varchar(25);
    v_personal   boolean;
    v_eventos    integer;
    v_sin_operador integer;
BEGIN
    SELECT count(*) INTO v_cuantos
      FROM public.pedidos WHERE referencia = 'CUSTOM-40';

    IF v_cuantos <> 1 THEN
        RAISE EXCEPTION 'C1 falla: hay % pedidos CUSTOM-40 y deberia haber 1', v_cuantos;
    END IF;
    RAISE NOTICE 'PASS C1: existe un unico pedido CUSTOM-40';

    SELECT id_pedido INTO v_pedido
      FROM public.pedidos WHERE referencia = 'CUSTOM-40';

    SELECT estado, personalizado INTO v_estado, v_personal
      FROM public.pedidos WHERE referencia = 'CUSTOM-40';

    IF v_estado <> 'confirmado' OR NOT v_personal THEN
        RAISE EXCEPTION 'C2 falla: estado "%" y personalizado %; se esperaba confirmado y true',
            v_estado, v_personal;
    END IF;
    RAISE NOTICE 'PASS C2: esta confirmado y marcado como personalizado';

    SELECT coalesce(sum(l.cantidad), 0), count(DISTINCT s.talla),
           count(*), count(DISTINCT l.id_producto_sku),
           count(*) FILTER (WHERE l.stock_descontado)
      INTO v_pares, v_tallas, v_lineas, v_skus, v_marcadas
      FROM public.linea_pedido l
      JOIN public.pedidos p ON p.id_pedido = l.id_pedido
      JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
     WHERE p.referencia = 'CUSTOM-40';

    IF v_pares <> 40 OR v_tallas <> 4 THEN
        RAISE EXCEPTION 'C3 falla: % pares en % tallas; se esperaban 40 en 4', v_pares, v_tallas;
    END IF;
    RAISE NOTICE 'PASS C3: 40 pares repartidos en 4 tallas';

    IF v_lineas <> 4 OR v_skus <> 4 THEN
        RAISE EXCEPTION 'C4 falla: % lineas con % SKU distintos; se esperaban 4 y 4', v_lineas, v_skus;
    END IF;
    RAISE NOTICE 'PASS C4: cuatro lineas, una por SKU, sin repetir';

    SELECT count(*) INTO v_tallas_mal
      FROM (
        SELECT s.talla
          FROM public.linea_pedido l
          JOIN public.producto_sku s ON s.id_producto_sku = l.id_producto_sku
         WHERE l.id_pedido = v_pedido
         GROUP BY s.talla
        HAVING sum(l.cantidad) <> 10
      ) AS tallas_mal_repartidas;

    IF v_tallas_mal <> 0 THEN
        RAISE EXCEPTION 'C5 falla: % tallas no tienen 10 pares', v_tallas_mal;
    END IF;
    RAISE NOTICE 'PASS C5: 10 pares en cada una de las cuatro tallas';

    IF v_marcadas <> 4 THEN
        RAISE EXCEPTION
            'C6 falla: % lineas con stock descontado y deberian ser 4', v_marcadas;
    END IF;
    RAISE NOTICE 'PASS C6: el stock se descontó una sola vez, las 4 lineas marcadas';

    SELECT count(*) INTO v_negativas
      FROM public.existencias WHERE cantidad < 0;

    IF v_negativas <> 0 THEN
        RAISE EXCEPTION 'C7 falla: hay % existencias negativas', v_negativas;
    END IF;
    RAISE NOTICE 'PASS C7: ninguna existencia negativa';

    SELECT count(*) INTO v_nova
      FROM public.pedidos WHERE referencia LIKE 'NOVA-%';

    IF v_nova <> 11 THEN
        RAISE EXCEPTION
            'C8 falla: hay % pedidos de demostracion y deberian seguir siendo 11', v_nova;
    END IF;
    RAISE NOTICE 'PASS C8: los 11 pedidos de demostracion siguen intactos';

    -- La auditoria de ESTE pedido: el alta y el cambio de estado.
    --
    -- Solo las filas de la tabla pedidos con id_registro = este pedido.
    -- Los cambios de stock (tabla existencias) no se cuentan: su
    -- id_registro es el de la existencia, no el del pedido.
    SELECT count(*), count(*) FILTER (WHERE id_usuario IS NULL)
      INTO v_eventos, v_sin_operador
      FROM public.log_eventos
     WHERE tabla_afectada = 'pedidos'
       AND id_registro = v_pedido;

    IF v_eventos < 2 THEN
        RAISE EXCEPTION
            'C9 falla: la auditoria tiene % eventos del pedido y deberia tener al menos 2 (el alta y la confirmacion)',
            v_eventos;
    END IF;

    IF v_sin_operador <> 0 THEN
        RAISE EXCEPTION
            'C9 falla: % eventos de auditoria del pedido sin operador identificado', v_sin_operador;
    END IF;
    RAISE NOTICE
        'PASS C9: % eventos de auditoria del pedido, todos con operador identificado', v_eventos;
END
$$;

COMMIT;

\unset clave_tienda

\echo ''
\echo '--- Resumen del pedido guardado'
SELECT
    p.referencia,
    p.estado,
    u.username AS operador,
    p.cantidad_total AS pares,
    p.importe_total
FROM public.pedidos p
LEFT JOIN public.usuarios u ON u.id_usuario = p.id_usuario
WHERE p.referencia = 'CUSTOM-40';

\echo ''
\echo 'Para exportar la orden de fabricacion: 15_exportar_fabricacion.sql'
\echo ''
