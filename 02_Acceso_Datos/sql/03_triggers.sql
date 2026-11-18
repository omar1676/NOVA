-- 03_triggers.sql — triggers de pedidos y lineas (las funciones estan en 02_funciones.sql)

-- Trigger: recalcula los totales del pedido cuando cambia alguna de sus lineas
CREATE TRIGGER trg_actualizar_totales
AFTER INSERT OR DELETE OR UPDATE
ON public.linea_pedido
FOR EACH ROW
EXECUTE FUNCTION actualizar_totales_pedido();

-- Trigger: calcula el subtotal de la linea antes de guardarla
CREATE TRIGGER trg_calcular_subtotal
BEFORE INSERT OR UPDATE
ON public.linea_pedido
FOR EACH ROW
EXECUTE FUNCTION calcular_subtotal_linea();

-- Trigger: al cambiar el estado, devuelve el stock si el pedido se cancela
CREATE TRIGGER trg_devolver_stock_cancelacion
AFTER UPDATE OF estado
ON public.pedidos
FOR EACH ROW
WHEN (OLD.estado IS DISTINCT FROM NEW.estado)
EXECUTE FUNCTION devolver_stock_cancelacion();

-- Trigger: protege las lineas de una compra ya registrada antes de cambiarlas o borrarlas
CREATE TRIGGER trg_proteger_linea_pedido
BEFORE UPDATE OR DELETE
ON public.linea_pedido
FOR EACH ROW
EXECUTE FUNCTION proteger_linea_pedido();

-- Trigger: descuenta el stock solo cuando el pedido pasa a confirmado
CREATE TRIGGER trg_descontar_stock_confirmacion
AFTER UPDATE OF estado
ON public.pedidos
FOR EACH ROW
WHEN (NEW.estado = 'confirmado' AND OLD.estado <> 'confirmado')
EXECUTE FUNCTION descontar_stock_confirmacion();
