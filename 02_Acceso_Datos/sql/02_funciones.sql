CREATE OR REPLACE FUNCTION public.iniciar_sesion(p_username character varying, p_password text)
 RETURNS integer
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = pg_catalog, public, extensiones
AS $function$
DECLARE
    v_id_usuario integer;
    v_hash text;
BEGIN
    SELECT u.id_usuario, u.password_hash
    INTO v_id_usuario, v_hash
    FROM public.usuarios u
    WHERE u.username = p_username
      AND u.activo = true;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Usuario o contrasena incorrectos';
    END IF;

    IF v_hash IS NULL OR left(v_hash, 1) <> '$' THEN
        RAISE EXCEPTION 'La cuenta no tiene contrasena establecida';
    END IF;

    IF crypt(p_password, v_hash) <> v_hash THEN
        RAISE EXCEPTION 'Usuario o contrasena incorrectos';
    END IF;

    PERFORM set_config(
        'nova.id_usuario',
        v_id_usuario::text || ':' ||
        encode(hmac(v_id_usuario::text, v_hash, 'sha256'), 'hex'),
        true
    );

    RETURN v_id_usuario;
END;
$function$
;
CREATE OR REPLACE FUNCTION public.usuario_sesion()
 RETURNS integer
 LANGUAGE plpgsql
 STABLE
 SECURITY DEFINER
 SET search_path = pg_catalog, public, extensiones
AS $function$
DECLARE
    v_valor text;
    v_id text;
    v_firma text;
    v_hash text;
BEGIN
    v_valor := current_setting('nova.id_usuario', true);

    IF v_valor IS NULL OR v_valor = '' THEN
        RETURN NULL;
    END IF;

    v_id := split_part(v_valor, ':', 1);
    v_firma := split_part(v_valor, ':', 2);

    IF v_id !~ '^[0-9]+$' OR v_firma = '' THEN
        RETURN NULL;
    END IF;

    SELECT password_hash
    INTO v_hash
    FROM public.usuarios
    WHERE id_usuario = v_id::integer
      AND activo = true;

    IF NOT FOUND THEN
        RETURN NULL;
    END IF;

    IF v_firma <> encode(hmac(v_id, v_hash, 'sha256'), 'hex') THEN
        RETURN NULL;
    END IF;

    RETURN v_id::integer;
END;
$function$
;
CREATE OR REPLACE FUNCTION public.cerrar_sesion()
 RETURNS void
 LANGUAGE plpgsql
AS $function$
BEGIN
    PERFORM set_config('nova.id_usuario', '', true);
END;
$function$
;
CREATE OR REPLACE FUNCTION public.actualizar_totales_pedido()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_id_pedido int4;
BEGIN
    IF TG_OP = 'DELETE' THEN
        v_id_pedido := OLD.id_pedido;
    ELSE
        v_id_pedido := NEW.id_pedido;
    END IF;

    UPDATE public.pedidos
    SET
        cantidad_total = COALESCE((
            SELECT SUM(cantidad)
            FROM public.linea_pedido
            WHERE id_pedido = v_id_pedido
        ), 0),
        importe_total = COALESCE((
            SELECT SUM(subtotal)
            FROM public.linea_pedido
            WHERE id_pedido = v_id_pedido
        ), 0)
    WHERE id_pedido = v_id_pedido;

    RETURN NULL;
END;
$function$
;
CREATE OR REPLACE FUNCTION public.calcular_subtotal_linea()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    NEW.subtotal := NEW.cantidad * NEW.precio_unitario;

    RETURN NEW;
END;
$function$
;
CREATE OR REPLACE FUNCTION public.descontar_stock(p_id_producto_sku integer, p_id_nave integer, p_cantidad integer)
 RETURNS void
 LANGUAGE plpgsql
AS $function$
BEGIN
    IF p_cantidad <= 0 THEN
        RAISE EXCEPTION 'La cantidad debe ser mayor que cero';
    END IF;

    UPDATE public.existencias
    SET cantidad = cantidad - p_cantidad
    WHERE id_producto_sku = p_id_producto_sku
      AND id_nave = p_id_nave
      AND cantidad >= p_cantidad;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Stock insuficiente o producto no encontrado';
    END IF;
END;
$function$
;
DROP FUNCTION IF EXISTS public.realizar_compra(character varying, integer, integer, integer, integer);
CREATE OR REPLACE FUNCTION public.anadir_linea_pedido(p_id_pedido integer, p_id_producto_sku integer, p_id_nave integer, p_cantidad integer)
 RETURNS void
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = pg_catalog, public
AS $function$
DECLARE
    v_precio numeric(8,2);
    v_estado varchar(25);
BEGIN
    IF p_cantidad <= 0 THEN
        RAISE EXCEPTION 'La cantidad debe ser mayor que cero';
    END IF;

    SELECT estado
    INTO v_estado
    FROM public.pedidos
    WHERE id_pedido = p_id_pedido;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'El pedido no existe';
    END IF;

    IF v_estado <> 'pendiente' THEN
        RAISE EXCEPTION 'Solo se pueden anadir lineas a un pedido pendiente';
    END IF;

    SELECT m.precio_base + v.suplemento_precio
    INTO v_precio
    FROM public.producto_sku s
    JOIN public.variantes v
        ON v.id_variante = s.id_variante
    JOIN public.modelos m
        ON m.id_modelo = v.id_modelo
    WHERE s.id_producto_sku = p_id_producto_sku
      AND s.activo = true
      AND m.activo = true;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Producto no disponible';
    END IF;

    INSERT INTO public.linea_pedido (
        id_pedido,
        id_producto_sku,
        id_nave,
        cantidad,
        precio_unitario,
        subtotal,
        stock_descontado
    )
    VALUES (
        p_id_pedido,
        p_id_producto_sku,
        p_id_nave,
        p_cantidad,
        v_precio,
        0,
        false
    );
END;
$function$
;
CREATE OR REPLACE FUNCTION public.realizar_compra(p_referencia character varying, p_id_cliente integer, p_id_producto_sku integer, p_id_nave integer, p_cantidad integer, p_id_usuario integer DEFAULT NULL)
 RETURNS integer
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = pg_catalog, public
AS $function$
DECLARE
    v_id_pedido integer;
BEGIN
    INSERT INTO public.pedidos (
        referencia,
        id_cliente,
        id_usuario,
        estado_pago
    )
    VALUES (
        p_referencia,
        p_id_cliente,
        p_id_usuario,
        'pendiente'
    )
    RETURNING id_pedido INTO v_id_pedido;

    PERFORM public.anadir_linea_pedido(
        v_id_pedido,
        p_id_producto_sku,
        p_id_nave,
        p_cantidad
    );

    RETURN v_id_pedido;
END;
$function$
;
CREATE OR REPLACE FUNCTION public.realizar_compra_xnova(p_referencia character varying, p_id_configuracion integer)
 RETURNS integer
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = pg_catalog, public
AS $function$
DECLARE
    v_id_cliente integer;
    v_id_pedido integer;
    v_precio numeric(8,2);
BEGIN
    SELECT id_cliente
    INTO v_id_cliente
    FROM public.configuraciones_xnova
    WHERE id_configuracion = p_id_configuracion
      AND id_pedido IS NULL
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Configuracion X-NOVA no disponible';
    END IF;

    SELECT precio_base
    INTO v_precio
    FROM public.modelos
    WHERE nombre = 'X-NOVA'
      AND activo = true;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Modelo X-NOVA no disponible';
    END IF;

    INSERT INTO public.pedidos (
        referencia,
        id_cliente,
        personalizado,
        personalizacion,
        estado_pago
    )
    VALUES (
        p_referencia,
        v_id_cliente,
        true,
        'Fabricacion personalizada X-NOVA',
        'pendiente'
    )
    RETURNING id_pedido INTO v_id_pedido;

    INSERT INTO public.linea_pedido (
        id_pedido,
        id_configuracion_xnova,
        cantidad,
        precio_unitario,
        subtotal
    )
    VALUES (
        v_id_pedido,
        p_id_configuracion,
        1,
        v_precio,
        0
    );

    UPDATE public.configuraciones_xnova
    SET id_pedido = v_id_pedido
    WHERE id_configuracion = p_id_configuracion;

    RETURN v_id_pedido;
END;
$function$
;
CREATE OR REPLACE FUNCTION public.devolver_stock_cancelacion()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = pg_catalog, public
AS $function$
DECLARE
    linea RECORD;
BEGIN
    IF OLD.estado = 'cancelado'
       AND NEW.estado <> 'cancelado' THEN
        RAISE EXCEPTION 'No se puede reactivar un pedido cancelado';
    END IF;

    IF NEW.estado = 'cancelado'
       AND OLD.estado <> 'cancelado' THEN

        FOR linea IN
            SELECT *
            FROM public.linea_pedido
            WHERE id_pedido = NEW.id_pedido
              AND stock_descontado = true
            FOR UPDATE
        LOOP
            UPDATE public.existencias
            SET cantidad = cantidad + linea.cantidad
            WHERE id_producto_sku = linea.id_producto_sku
              AND id_nave = linea.id_nave;

            IF NOT FOUND THEN
                RAISE EXCEPTION 'No se encontraron las existencias';
            END IF;

            UPDATE public.linea_pedido
            SET stock_descontado = false
            WHERE id_linea = linea.id_linea;
        END LOOP;
    END IF;

    RETURN NEW;
END;
$function$
;
CREATE OR REPLACE FUNCTION public.proteger_linea_pedido()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    estado_pedido varchar(25);
    linea_bloqueada boolean;
BEGIN
    SELECT estado
    INTO estado_pedido
    FROM public.pedidos
    WHERE id_pedido = OLD.id_pedido;

    linea_bloqueada := OLD.stock_descontado
        OR OLD.id_configuracion_xnova IS NOT NULL
        OR estado_pedido <> 'pendiente';

    IF TG_OP = 'DELETE' THEN
        IF linea_bloqueada THEN
            RAISE EXCEPTION 'No se puede eliminar esta linea de pedido';
        END IF;

        RETURN OLD;
    END IF;

    IF OLD.id_pedido IS DISTINCT FROM NEW.id_pedido
       OR OLD.id_producto_sku IS DISTINCT FROM NEW.id_producto_sku
       OR OLD.id_nave IS DISTINCT FROM NEW.id_nave
       OR OLD.id_configuracion_xnova IS DISTINCT FROM NEW.id_configuracion_xnova
       OR OLD.cantidad IS DISTINCT FROM NEW.cantidad
       OR OLD.precio_unitario IS DISTINCT FROM NEW.precio_unitario THEN

        IF linea_bloqueada THEN
            RAISE EXCEPTION 'No se puede modificar una compra registrada';
        END IF;
    END IF;

    IF OLD.stock_descontado IS DISTINCT FROM NEW.stock_descontado THEN
        IF NOT (
            (
                OLD.stock_descontado = false
                AND NEW.stock_descontado = true
                AND estado_pedido = 'confirmado'
            )
            OR
            (
                OLD.stock_descontado = true
                AND NEW.stock_descontado = false
                AND estado_pedido = 'cancelado'
            )
        ) THEN
            RAISE EXCEPTION 'Cambio de stock no permitido';
        END IF;
    END IF;

    RETURN NEW;
END;
$function$
;
CREATE OR REPLACE FUNCTION public.establecer_password(p_username character varying, p_password text)
 RETURNS void
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = pg_catalog, public, extensiones
AS $function$
BEGIN
    IF length(p_password) < 8 THEN
        RAISE EXCEPTION 'La contrasena debe tener al menos 8 caracteres';
    END IF;

    UPDATE public.usuarios
    SET password_hash = crypt(p_password, gen_salt('bf'))
    WHERE username = p_username;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'El usuario no existe';
    END IF;
END;
$function$
;
CREATE OR REPLACE FUNCTION public.descontar_stock_confirmacion()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = pg_catalog, public
AS $function$
DECLARE
    linea RECORD;
BEGIN
    FOR linea IN
        SELECT *
        FROM public.linea_pedido
        WHERE id_pedido = NEW.id_pedido
          AND stock_descontado = false
          AND id_producto_sku IS NOT NULL
          AND id_nave IS NOT NULL
        FOR UPDATE
    LOOP
        PERFORM public.descontar_stock(
            linea.id_producto_sku,
            linea.id_nave,
            linea.cantidad
        );

        UPDATE public.linea_pedido
        SET stock_descontado = true
        WHERE id_linea = linea.id_linea;
    END LOOP;

    RETURN NEW;
END;
$function$
;
CREATE OR REPLACE FUNCTION public.crear_usuario(p_username character varying, p_nombre_rol character varying)
 RETURNS integer
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path = pg_catalog, public
AS $function$
DECLARE
    v_id_rol integer;
    v_id_usuario integer;
BEGIN
    SELECT id_rol
    INTO v_id_rol
    FROM public.roles
    WHERE nombre = p_nombre_rol;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'El rol indicado no existe';
    END IF;

    INSERT INTO public.usuarios (username, password_hash, id_rol, activo)
    VALUES (p_username, '!', v_id_rol, true)
    RETURNING id_usuario INTO v_id_usuario;

    RETURN v_id_usuario;
END;
$function$
;
