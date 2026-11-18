-- 20_tienda_web.sql — cuentas de cliente y compras desde la tienda web

\set ON_ERROR_STOP on

\echo 'Tienda web: cuentas de cliente, compras y usuario tienda_nova'
\echo ''
\prompt 'Contrasena para tienda_nova (la que ira en servidor-admin/.env): ' clave_tienda

-- Todo o nada: si algo falla, no queda nada a medias
BEGIN;

-- 1. Cuentas de cliente
CREATE TABLE IF NOT EXISTS public.cuentas_cliente (
    id_cliente int4 NOT NULL,
    password_hash text NOT NULL,
    fecha_alta timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT cuentas_cliente_pk PRIMARY KEY (id_cliente),
    CONSTRAINT cuentas_cliente_id_cliente_fk FOREIGN KEY (id_cliente)
        REFERENCES public.clientes (id_cliente)
);

-- Nadie la lee ni la escribe directamente: solo las funciones de abajo
REVOKE ALL ON public.cuentas_cliente FROM PUBLIC;

-- 2. Funciones

-- Funcion: da de alta un cliente de la web con su contrasena cifrada
CREATE OR REPLACE FUNCTION public.registrar_cliente(
    p_nombre character varying,
    p_email character varying,
    p_password text,
    p_telefono character varying DEFAULT NULL,
    p_direccion text DEFAULT NULL)
 RETURNS integer
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = pg_catalog, public, extensiones
AS $function$
DECLARE
    v_email varchar(150);
    v_id_cliente integer;
BEGIN
    v_email := lower(btrim(p_email));

    IF p_nombre IS NULL OR btrim(p_nombre) = '' OR length(p_nombre) > 120 THEN
        RAISE EXCEPTION 'Escribe tu nombre (maximo 120 caracteres)';
    END IF;

    IF v_email IS NULL OR length(v_email) > 150
       OR v_email !~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$' THEN
        RAISE EXCEPTION 'El correo no es valido';
    END IF;

    IF p_password IS NULL OR length(p_password) < 8 THEN
        RAISE EXCEPTION 'La contrasena debe tener al menos 8 caracteres';
    END IF;

    IF length(p_telefono) > 30 OR length(p_direccion) > 300 THEN
        RAISE EXCEPTION 'El telefono o la direccion son demasiado largos';
    END IF;

    IF EXISTS (SELECT 1 FROM public.clientes WHERE lower(email) = v_email) THEN
        RAISE EXCEPTION 'Ese correo ya esta registrado';
    END IF;

    INSERT INTO public.clientes (nombre, tipo, email, telefono, direccion_entrega)
    VALUES (btrim(p_nombre), 'particular', v_email,
            NULLIF(btrim(p_telefono), ''), NULLIF(btrim(p_direccion), ''))
    RETURNING id_cliente INTO v_id_cliente;

    -- La contrasena se guarda como hash bcrypt, igual que establecer_password
    INSERT INTO public.cuentas_cliente (id_cliente, password_hash)
    VALUES (v_id_cliente, crypt(p_password, gen_salt('bf')));

    RETURN v_id_cliente;
EXCEPTION
    -- Dos altas a la vez con el mismo correo: la segunda choca con clientes_email_uq
    WHEN unique_violation THEN
        RAISE EXCEPTION 'Ese correo ya esta registrado';
END;
$function$
;

-- Funcion: login de un cliente de la web; devuelve su id
CREATE OR REPLACE FUNCTION public.iniciar_sesion_cliente(p_email character varying, p_password text)
 RETURNS integer
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = pg_catalog, public, extensiones
AS $function$
DECLARE
    v_id_cliente integer;
    v_hash text;
BEGIN
    SELECT c.id_cliente, k.password_hash
    INTO v_id_cliente, v_hash
    FROM public.clientes c
    JOIN public.cuentas_cliente k ON k.id_cliente = c.id_cliente
    WHERE lower(c.email) = lower(btrim(p_email))
      AND c.activo = true;

    IF NOT FOUND THEN
        -- Se calcula un hash igualmente para tardar lo mismo que con un
        -- correo que si existe: asi el tiempo no delata que correos hay
        PERFORM crypt(COALESCE(p_password, ''), gen_salt('bf'));
        RAISE EXCEPTION 'Correo o contrasena incorrectos';
    END IF;

    IF crypt(COALESCE(p_password, ''), v_hash) <> v_hash THEN
        RAISE EXCEPTION 'Correo o contrasena incorrectos';
    END IF;

    RETURN v_id_cliente;
END;
$function$
;

-- Funcion: crea el pedido del carrito de la web, pendiente de pago
CREATE OR REPLACE FUNCTION public.crear_compra_web(
    p_id_cliente integer,
    p_referencia character varying,
    p_skus integer[],
    p_cantidades integer[],
    p_telefono character varying,
    p_direccion text)
 RETURNS integer
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = pg_catalog, public
AS $function$
DECLARE
    v_id_pedido integer;
    v_duenyo integer;
    v_id_nave integer;
    v_producto text;
    v_disponible integer;
    i integer;
BEGIN
    -- 1. El cliente tiene cuenta y esta activo
    IF NOT EXISTS (
        SELECT 1
        FROM public.clientes c
        JOIN public.cuentas_cliente k ON k.id_cliente = c.id_cliente
        WHERE c.id_cliente = p_id_cliente AND c.activo = true
    ) THEN
        RAISE EXCEPTION 'Cliente no valido';
    END IF;

    -- 2. La referencia tiene el formato de la web
    IF p_referencia IS NULL OR p_referencia !~ '^WEB-[0-9A-F]{20}$' THEN
        RAISE EXCEPTION 'Referencia no valida';
    END IF;

    -- 3. Repeticion: si el pedido ya existe y es suyo, es el mismo
    SELECT id_pedido, id_cliente
    INTO v_id_pedido, v_duenyo
    FROM public.pedidos
    WHERE referencia = p_referencia;

    IF FOUND THEN
        IF v_duenyo = p_id_cliente THEN
            RETURN v_id_pedido;
        END IF;
        RAISE EXCEPTION 'Referencia no valida';
    END IF;

    -- 4. El carrito: de 1 a 20 productos distintos, de 1 a 10 pares cada uno
    IF p_skus IS NULL OR p_cantidades IS NULL
       OR cardinality(p_skus) = 0 OR cardinality(p_skus) > 20
       OR cardinality(p_skus) <> cardinality(p_cantidades)
       OR array_position(p_skus, NULL) IS NOT NULL
       OR array_position(p_cantidades, NULL) IS NOT NULL THEN
        RAISE EXCEPTION 'El carrito no es valido';
    END IF;

    IF EXISTS (SELECT 1 FROM unnest(p_cantidades) AS c(cantidad)
               WHERE cantidad < 1 OR cantidad > 10) THEN
        RAISE EXCEPTION 'Cada producto admite de 1 a 10 pares';
    END IF;

    IF (SELECT count(DISTINCT s) FROM unnest(p_skus) AS s) <> cardinality(p_skus) THEN
        RAISE EXCEPTION 'Hay productos repetidos en el carrito';
    END IF;

    -- 5. Los datos de entrega
    IF p_direccion IS NULL OR btrim(p_direccion) = '' OR length(p_direccion) > 300 THEN
        RAISE EXCEPTION 'Escribe la direccion de entrega (maximo 300 caracteres)';
    END IF;

    IF length(p_telefono) > 30 THEN
        RAISE EXCEPTION 'El telefono es demasiado largo';
    END IF;

    -- 6. La nave: la primera (solo hay una, NOVA Central)
    SELECT id_nave INTO v_id_nave FROM public.nave ORDER BY id_nave LIMIT 1;

    -- 7. Cada producto existe, esta a la venta y hay stock AHORA.
    --    Es solo un aviso: la comprobacion que manda es la del trigger al confirmar
    FOR i IN 1 .. cardinality(p_skus) LOOP
        SELECT m.nombre || ' (' || v.color || ', talla ' || s.talla || ')',
               COALESCE(e.cantidad, 0)
        INTO v_producto, v_disponible
        FROM public.producto_sku s
        JOIN public.variantes v ON v.id_variante = s.id_variante
        JOIN public.modelos m ON m.id_modelo = v.id_modelo
        LEFT JOIN public.existencias e
            ON e.id_producto_sku = s.id_producto_sku AND e.id_nave = v_id_nave
        WHERE s.id_producto_sku = p_skus[i]
          AND s.activo = true
          AND m.activo = true;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Producto no disponible';
        END IF;

        IF v_disponible < p_cantidades[i] THEN
            RAISE EXCEPTION 'No queda stock suficiente de %', v_producto;
        END IF;
    END LOOP;

    -- 8. Los datos de entrega se guardan en la ficha del cliente
    UPDATE public.clientes
    SET telefono = NULLIF(btrim(p_telefono), ''),
        direccion_entrega = btrim(p_direccion)
    WHERE id_cliente = p_id_cliente;

    -- 9. El pedido, con las funciones originales: la primera linea crea la
    --    cabecera y las demas se anaden. El precio lo pone la base
    v_id_pedido := public.realizar_compra(
        p_referencia, p_id_cliente, p_skus[1], v_id_nave, p_cantidades[1]);

    FOR i IN 2 .. cardinality(p_skus) LOOP
        PERFORM public.anadir_linea_pedido(
            v_id_pedido, p_skus[i], v_id_nave, p_cantidades[i]);
    END LOOP;

    RETURN v_id_pedido;
EXCEPTION
    -- Dos peticiones con la misma referencia a la vez: se devuelve el pedido de la primera
    WHEN unique_violation THEN
        SELECT id_pedido, id_cliente
        INTO v_id_pedido, v_duenyo
        FROM public.pedidos
        WHERE referencia = p_referencia;

        IF FOUND AND v_duenyo = p_id_cliente THEN
            RETURN v_id_pedido;
        END IF;
        RAISE EXCEPTION 'Referencia no valida';
END;
$function$
;

-- Funcion: paga y confirma un pedido web del cliente (al confirmar se descuenta el stock)
CREATE OR REPLACE FUNCTION public.confirmar_compra_web(p_id_cliente integer, p_id_pedido integer)
 RETURNS void
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = pg_catalog, public
AS $function$
DECLARE
    v_estado varchar(25);
    v_pago varchar(25);
BEGIN
    SELECT p.estado, p.estado_pago
    INTO v_estado, v_pago
    FROM public.pedidos p
    JOIN public.clientes c ON c.id_cliente = p.id_cliente
    WHERE p.id_pedido = p_id_pedido
      AND p.id_cliente = p_id_cliente
      AND p.referencia LIKE 'WEB-%'
      AND c.activo = true
    FOR UPDATE OF p;

    -- El mismo mensaje si no existe o si es de otro cliente
    IF NOT FOUND THEN
        RAISE EXCEPTION 'El pedido no existe';
    END IF;

    -- Si ya estaba pagado no se hace nada: pulsar dos veces no paga dos veces
    IF v_estado = 'confirmado' AND v_pago = 'pagado' THEN
        RETURN;
    END IF;

    IF v_estado <> 'pendiente' THEN
        RAISE EXCEPTION 'Este pedido ya no se puede pagar';
    END IF;

    UPDATE public.pedidos
    SET estado = 'confirmado',
        estado_pago = 'pagado'
    WHERE id_pedido = p_id_pedido;
END;
$function$
;

-- Funcion: cancela un pedido web que todavia no se ha pagado
CREATE OR REPLACE FUNCTION public.cancelar_compra_web(p_id_cliente integer, p_id_pedido integer)
 RETURNS void
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = pg_catalog, public
AS $function$
DECLARE
    v_estado varchar(25);
BEGIN
    SELECT p.estado
    INTO v_estado
    FROM public.pedidos p
    JOIN public.clientes c ON c.id_cliente = p.id_cliente
    WHERE p.id_pedido = p_id_pedido
      AND p.id_cliente = p_id_cliente
      AND p.referencia LIKE 'WEB-%'
      AND c.activo = true
    FOR UPDATE OF p;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'El pedido no existe';
    END IF;

    -- Si ya estaba cancelado no se hace nada
    IF v_estado = 'cancelado' THEN
        RETURN;
    END IF;

    IF v_estado <> 'pendiente' THEN
        RAISE EXCEPTION 'Un pedido pagado no se puede cancelar desde la web';
    END IF;

    UPDATE public.pedidos
    SET estado = 'cancelado'
    WHERE id_pedido = p_id_pedido;
END;
$function$
;

-- Por defecto nadie puede ejecutar las cinco funciones; solo tienda_web (mas abajo)
REVOKE EXECUTE ON FUNCTION
    public.registrar_cliente(character varying, character varying, text, character varying, text),
    public.iniciar_sesion_cliente(character varying, text),
    public.crear_compra_web(integer, character varying, integer[], integer[], character varying, text),
    public.confirmar_compra_web(integer, integer),
    public.cancelar_compra_web(integer, integer)
FROM PUBLIC;

-- 3. El rol de la tienda
SELECT NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'tienda_web') AS hay_que_crear_rol
\gset

\if :hay_que_crear_rol
CREATE ROLE tienda_web NOLOGIN;
\endif

GRANT USAGE ON SCHEMA public TO tienda_web;

-- El catalogo: modelos, colores, tallas y existencias (no hay datos personales)
GRANT SELECT ON public.modelos, public.variantes, public.producto_sku, public.existencias
TO tienda_web;
GRANT SELECT (id_nave) ON public.nave TO tienda_web;

-- Clientes, pedidos y lineas: solo las columnas que usa la tienda
GRANT SELECT (id_cliente, nombre, email, telefono, direccion_entrega, activo)
ON public.clientes TO tienda_web;

GRANT SELECT (id_pedido, referencia, id_cliente, fecha_pedido, estado, estado_pago,
              cantidad_total, importe_total)
ON public.pedidos TO tienda_web;

GRANT SELECT (id_linea, id_pedido, id_producto_sku, cantidad, precio_unitario, subtotal)
ON public.linea_pedido TO tienda_web;

-- Escribir, solo a traves de las cinco funciones
GRANT EXECUTE ON FUNCTION
    public.registrar_cliente(character varying, character varying, text, character varying, text),
    public.iniciar_sesion_cliente(character varying, text),
    public.crear_compra_web(integer, character varying, integer[], integer[], character varying, text),
    public.confirmar_compra_web(integer, integer),
    public.cancelar_compra_web(integer, integer)
TO tienda_web;

-- 4. El usuario con el que se conecta la tienda
SELECT NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'tienda_nova') AS hay_que_crear
\gset

\if :hay_que_crear
CREATE ROLE tienda_nova LOGIN NOINHERIT;
\endif

ALTER ROLE tienda_nova WITH LOGIN NOINHERIT PASSWORD :'clave_tienda';
\unset clave_tienda

-- Solo puede pasar a tienda_web, y solo con SET ROLE (no hereda sus permisos)
GRANT tienda_web TO tienda_nova WITH INHERIT FALSE, SET TRUE;

COMMIT;

-- Comprobaciones
\echo ''
\echo 'Comprobacion: tienda_nova solo puede pasar a tienda_web y no hereda'
SELECT
    r.rolname AS rol,
    m.inherit_option AS hereda_permisos,
    m.set_option AS puede_set_role
FROM pg_auth_members m
JOIN pg_roles r ON r.oid = m.roleid
WHERE m.member = 'tienda_nova'::regrole
ORDER BY r.rolname;

\echo ''
\echo 'Comprobacion: sin SET ROLE, tienda_nova no lee nada ni compra (se esperan tres f)'
SELECT
    has_table_privilege('tienda_nova', 'public.modelos', 'SELECT') AS lee_modelos,
    has_any_column_privilege('tienda_nova', 'public.pedidos', 'SELECT') AS lee_pedidos,
    has_function_privilege('tienda_nova', 'public.confirmar_compra_web(integer, integer)', 'EXECUTE') AS compra;

\echo ''
\echo 'Comprobacion: tienda_web no puede escribir en ninguna tabla de public (se espera 0)'
SELECT count(*) AS tablas_en_las_que_puede_escribir
FROM pg_tables t
WHERE t.schemaname = 'public'
  AND (has_any_column_privilege('tienda_web', format('%I.%I', t.schemaname, t.tablename), 'INSERT, UPDATE')
       OR has_table_privilege('tienda_web', format('%I.%I', t.schemaname, t.tablename), 'DELETE, TRUNCATE'));

\echo ''
\echo 'Comprobacion: tienda_web no ve contrasenas ni datos internos (se esperan cinco f)'
SELECT
    has_any_column_privilege('tienda_web', 'public.cuentas_cliente', 'SELECT') AS lee_cuentas,
    has_column_privilege('tienda_web', 'public.usuarios', 'password_hash', 'SELECT') AS lee_hash_trabajadores,
    has_column_privilege('tienda_web', 'public.personal', 'dni', 'SELECT') AS lee_dni,
    has_table_privilege('tienda_web', 'public.log_eventos', 'SELECT') AS lee_auditoria,
    has_column_privilege('tienda_web', 'public.pedidos', 'personalizacion', 'SELECT') AS lee_personalizacion;

\echo ''
\echo 'Comprobacion: tienda_web no llama directamente a las funciones originales (se esperan cinco f)'
SELECT
    has_function_privilege('tienda_web', 'public.realizar_compra(character varying, integer, integer, integer, integer, integer)', 'EXECUTE') AS realizar_compra,
    has_function_privilege('tienda_web', 'public.anadir_linea_pedido(integer, integer, integer, integer)', 'EXECUTE') AS anadir_linea,
    has_function_privilege('tienda_web', 'public.descontar_stock(integer, integer, integer)', 'EXECUTE') AS descontar_stock,
    has_function_privilege('tienda_web', 'public.iniciar_sesion(character varying, text)', 'EXECUTE') AS login_trabajadores,
    has_function_privilege('tienda_web', 'public.crear_usuario(character varying, character varying)', 'EXECUTE') AS crear_usuario;

\echo ''
\echo 'Comprobacion: las cinco funciones de la tienda (tienda_web t, PUBLIC f)'
SELECT
    p.proname AS funcion,
    has_function_privilege('tienda_web', p.oid, 'EXECUTE') AS tienda_web,
    has_function_privilege('public', p.oid, 'EXECUTE') AS cualquiera,
    p.prosecdef AS security_definer,
    p.proconfig IS NOT NULL AS fija_search_path
FROM pg_proc p
WHERE p.pronamespace = 'public'::regnamespace
  AND p.proname IN ('registrar_cliente', 'iniciar_sesion_cliente', 'crear_compra_web',
                    'confirmar_compra_web', 'cancelar_compra_web')
ORDER BY p.proname;

\echo ''
\echo 'FIN'
