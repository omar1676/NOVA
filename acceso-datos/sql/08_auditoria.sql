-- Auditoria de NOVA Sneakers

-- Registrar cambios de estado de pedidos

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
        NEW.id_usuario,
        'pedidos',
        NEW.id_pedido,
        'CAMBIO_ESTADO',
        'Pedido ' || NEW.referencia ||
        ': ' || OLD.estado || ' -> ' || NEW.estado
    );

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_auditar_estado_pedido
AFTER UPDATE OF estado ON public.pedidos
FOR EACH ROW
WHEN (OLD.estado IS DISTINCT FROM NEW.estado)
EXECUTE FUNCTION public.auditar_estado_pedido();


-- Registrar cambios de existencias

CREATE OR REPLACE FUNCTION public.auditar_existencias()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = pg_catalog, public
AS $$
BEGIN
    INSERT INTO public.log_eventos (
        tabla_afectada,
        id_registro,
        accion,
        detalle
    )
    VALUES (
        'existencias',
        NEW.id_existencia,
        'CAMBIO_STOCK',
        'SKU ' || NEW.id_producto_sku ||
        ': ' || OLD.cantidad || ' -> ' || NEW.cantidad
    );

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_auditar_existencias
AFTER UPDATE OF cantidad ON public.existencias
FOR EACH ROW
WHEN (OLD.cantidad IS DISTINCT FROM NEW.cantidad)
EXECUTE FUNCTION public.auditar_existencias();

-- Proteger las funciones de auditoria

REVOKE ALL ON FUNCTION public.auditar_estado_pedido()
FROM PUBLIC;

REVOKE ALL ON FUNCTION public.auditar_existencias()
FROM PUBLIC;
