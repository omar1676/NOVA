
CREATE TRIGGER trg_actualizar_totales
AFTER INSERT OR DELETE OR UPDATE
ON public.linea_pedido
FOR EACH ROW
EXECUTE FUNCTION actualizar_totales_pedido();

CREATE TRIGGER trg_calcular_subtotal
BEFORE INSERT OR UPDATE
ON public.linea_pedido
FOR EACH ROW
EXECUTE FUNCTION calcular_subtotal_linea();

CREATE TRIGGER trg_devolver_stock_cancelacion
AFTER UPDATE OF estado
ON public.pedidos
FOR EACH ROW
WHEN (OLD.estado IS DISTINCT FROM NEW.estado)
EXECUTE FUNCTION devolver_stock_cancelacion();

CREATE TRIGGER trg_proteger_linea_pedido
BEFORE UPDATE OR DELETE
ON public.linea_pedido
FOR EACH ROW
EXECUTE FUNCTION proteger_linea_pedido();

CREATE TRIGGER trg_descontar_stock_confirmacion
AFTER UPDATE OF estado
ON public.pedidos
FOR EACH ROW
WHEN (NEW.estado = 'confirmado' AND OLD.estado <> 'confirmado')
EXECUTE FUNCTION descontar_stock_confirmacion();
