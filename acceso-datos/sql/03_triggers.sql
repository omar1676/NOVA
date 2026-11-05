CREATE TRIGGER trg_actualizar_totales AFTER INSERT OR DELETE OR UPDATE ON public.linea_pedido FOR EACH ROW EXECUTE FUNCTION actualizar_totales_pedido();
CREATE TRIGGER trg_calcular_subtotal BEFORE INSERT OR UPDATE OF cantidad, precio_unitario ON public.linea_pedido FOR EACH ROW EXECUTE FUNCTION calcular_subtotal_linea();
