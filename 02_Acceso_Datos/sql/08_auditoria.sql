-- 08_auditoria.sql — triggers que apuntan en log_eventos los cambios importantes
-- El operador es el de la sesion (usuario_sesion), no el usuario asignado al pedido

-- Funcion de auditoria: registra el alta de un pedido.
-- Todas son SECURITY DEFINER: los roles no escriben en log_eventos, pero el trigger si
CREATE OR REPLACE FUNCTION public.auditar_alta_pedido()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
BEGIN
    INSERT INTO public.log_eventos (
        id_usuario,
        tabla_afectada,
        id_registro,
        accion,
        detalle
    )
    VALUES (
        public.usuario_sesion(),
        'pedidos',
        NEW.id_pedido,
        'ALTA',
        'Pedido ' || NEW.referencia ||
        ' creado para el cliente ' || NEW.id_cliente ||
        ' en estado ' || NEW.estado
    );

    RETURN NEW;
END;
$$;

-- Trigger: despues de crear un pedido
CREATE TRIGGER trg_auditar_alta_pedido
AFTER INSERT ON public.pedidos
FOR EACH ROW
EXECUTE FUNCTION public.auditar_alta_pedido();



-- Funcion de auditoria: registra cada cambio de estado; cancelar cuenta como baja logica
CREATE OR REPLACE FUNCTION public.auditar_estado_pedido()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
BEGIN
    INSERT INTO public.log_eventos (
        id_usuario,
        tabla_afectada,
        id_registro,
        accion,
        detalle
    )
    VALUES (
        public.usuario_sesion(),
        'pedidos',
        NEW.id_pedido,
        CASE WHEN NEW.estado = 'cancelado'
             THEN 'BAJA_LOGICA'
             ELSE 'CAMBIO_ESTADO' END,
        'Pedido ' || NEW.referencia ||
        ': ' || OLD.estado || ' -> ' || NEW.estado ||
        '. Usuario del pedido: ' || COALESCE(NEW.id_usuario::text, 'sin asignar')
    );

    RETURN NEW;
END;
$$;

-- Trigger: solo cuando el estado cambia de verdad
CREATE TRIGGER trg_auditar_estado_pedido
AFTER UPDATE OF estado ON public.pedidos
FOR EACH ROW
WHEN (OLD.estado IS DISTINCT FROM NEW.estado)
EXECUTE FUNCTION public.auditar_estado_pedido();



-- Funcion de auditoria: registra los cambios de stock (cantidad antes y despues)
CREATE OR REPLACE FUNCTION public.auditar_existencias()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
BEGIN
    INSERT INTO public.log_eventos (
        id_usuario,
        tabla_afectada,
        id_registro,
        accion,
        detalle
    )
    VALUES (
        public.usuario_sesion(),
        'existencias',
        NEW.id_existencia,
        'CAMBIO_STOCK',
        'SKU ' || NEW.id_producto_sku ||
        ': ' || OLD.cantidad || ' -> ' || NEW.cantidad
    );

    RETURN NEW;
END;
$$;

-- Trigger: solo cuando la cantidad cambia de verdad
CREATE TRIGGER trg_auditar_existencias
AFTER UPDATE OF cantidad ON public.existencias
FOR EACH ROW
WHEN (OLD.cantidad IS DISTINCT FROM NEW.cantidad)
EXECUTE FUNCTION public.auditar_existencias();



-- Funcion de auditoria: registra la baja logica de un modelo (activo pasa a false)
CREATE OR REPLACE FUNCTION public.auditar_baja_modelo()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
BEGIN
    INSERT INTO public.log_eventos (
        id_usuario,
        tabla_afectada,
        id_registro,
        accion,
        detalle
    )
    VALUES (
        public.usuario_sesion(),
        'modelos',
        NEW.id_modelo,
        'BAJA_LOGICA',
        'Modelo ' || NEW.nombre || ' marcado como no activo'
    );

    RETURN NEW;
END;
$$;

-- Trigger: cuando un modelo activo se desactiva
CREATE TRIGGER trg_auditar_baja_modelo
AFTER UPDATE OF activo ON public.modelos
FOR EACH ROW
WHEN (OLD.activo = true AND NEW.activo = false)
EXECUTE FUNCTION public.auditar_baja_modelo();



-- Funcion de auditoria: registra la baja logica de un SKU
CREATE OR REPLACE FUNCTION public.auditar_baja_sku()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
BEGIN
    INSERT INTO public.log_eventos (
        id_usuario,
        tabla_afectada,
        id_registro,
        accion,
        detalle
    )
    VALUES (
        public.usuario_sesion(),
        'producto_sku',
        NEW.id_producto_sku,
        'BAJA_LOGICA',
        'SKU ' || NEW.sku || ' marcado como no activo'
    );

    RETURN NEW;
END;
$$;

-- Trigger: cuando un SKU activo se desactiva
CREATE TRIGGER trg_auditar_baja_sku
AFTER UPDATE OF activo ON public.producto_sku
FOR EACH ROW
WHEN (OLD.activo = true AND NEW.activo = false)
EXECUTE FUNCTION public.auditar_baja_sku();


-- Las funciones de auditoria solo las llaman los triggers: nadie puede ejecutarlas a mano
REVOKE ALL ON FUNCTION public.auditar_alta_pedido()
FROM PUBLIC;

REVOKE ALL ON FUNCTION public.auditar_estado_pedido()
FROM PUBLIC;

REVOKE ALL ON FUNCTION public.auditar_existencias()
FROM PUBLIC;

REVOKE ALL ON FUNCTION public.auditar_baja_modelo()
FROM PUBLIC;

REVOKE ALL ON FUNCTION public.auditar_baja_sku()
FROM PUBLIC;
