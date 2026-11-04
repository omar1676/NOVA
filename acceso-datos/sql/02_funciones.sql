CREATE OR REPLACE FUNCTION public.actualizar_totales_pedido()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
DECLARE
    pedido_afectado int4;
BEGIN
    IF TG_OP = 'DELETE' THEN
        pedido_afectado := OLD.id_pedido;
    ELSE
        pedido_afectado := NEW.id_pedido;
    END IF;

    UPDATE public.pedidos
    SET
        cantidad_total = COALESCE((
            SELECT SUM(cantidad)
            FROM public.linea_pedido
            WHERE id_pedido = pedido_afectado
        ), 0),
        importe_total = COALESCE((
            SELECT SUM(subtotal)
            FROM public.linea_pedido
            WHERE id_pedido = pedido_afectado
        ), 0)
    WHERE id_pedido = pedido_afectado;

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
CREATE OR REPLACE FUNCTION public.realizar_compra(p_referencia character varying, p_id_cliente integer, p_id_producto_sku integer, p_id_nave integer, p_cantidad integer)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_precio numeric(8,2);
    v_id_pedido integer;
BEGIN
    IF p_cantidad <= 0 THEN
        RAISE EXCEPTION 'La cantidad debe ser mayor que cero';
    END IF;

    SELECT m.precio_base + v.suplemento_precio
    INTO v_precio
    FROM public.producto_sku p
    JOIN public.variantes v
        ON v.id_variante = p.id_variante
    JOIN public.modelos m
        ON m.id_modelo = v.id_modelo
    WHERE p.id_producto_sku = p_id_producto_sku
      AND p.activo = true
      AND m.activo = true;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Producto no disponible';
    END IF;

    -- Descontar existencias
    PERFORM public.descontar_stock(
        p_id_producto_sku,
        p_id_nave,
        p_cantidad
    );

    -- Crear el pedido
    INSERT INTO public.pedidos (
        referencia,
        id_cliente,
        estado_pago
    )
    VALUES (
        p_referencia,
        p_id_cliente,
        'pendiente'
    )
    RETURNING id_pedido INTO v_id_pedido;

    -- Registrar las zapatillas compradas
    INSERT INTO public.linea_pedido (
        id_pedido,
        id_producto_sku,
        cantidad,
        precio_unitario,
        subtotal
    )
    VALUES (
        v_id_pedido,
        p_id_producto_sku,
        p_cantidad,
        v_precio,
        0
    );

    RETURN v_id_pedido;
END;
$function$
;
CREATE OR REPLACE FUNCTION public.realizar_compra_xnova(p_referencia character varying, p_id_configuracion integer)
 RETURNS integer
 LANGUAGE plpgsql
AS $function$
DECLARE
    v_id_cliente integer;
    v_id_pedido integer;
    v_precio numeric(8,2);
BEGIN
    -- Comprobar que la configuraci├│n existe y est├í disponible
    SELECT id_cliente
    INTO v_id_cliente
    FROM public.configuraciones_xnova
    WHERE id_configuracion = p_id_configuracion
      AND id_pedido IS NULL
    FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Configuracion X-NOVA no disponible';
    END IF;

    -- Obtener el precio del modelo
    SELECT precio_base
    INTO v_precio
    FROM public.modelos
    WHERE nombre = 'X-NOVA'
      AND activo = true;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Modelo X-NOVA no disponible';
    END IF;

    -- Crear pedido
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

    -- Crear l├¡nea personalizada
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

    -- Asociar la configuraci├│n al pedido
    UPDATE public.configuraciones_xnova
    SET id_pedido = v_id_pedido
    WHERE id_configuracion = p_id_configuracion;

    RETURN v_id_pedido;
END;
$function$
;
