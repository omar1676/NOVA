
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = 'nova_admin'
    ) THEN
        CREATE ROLE nova_admin NOLOGIN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = 'nova_trabajador'
    ) THEN
        CREATE ROLE nova_trabajador NOLOGIN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = 'nova_cliente'
    ) THEN
        CREATE ROLE nova_cliente NOLOGIN;
    END IF;
END
$$;

GRANT USAGE ON SCHEMA public
TO nova_admin, nova_trabajador, nova_cliente;

GRANT SELECT, INSERT, UPDATE
ON public.modelos, public.variantes, public.producto_sku,
   public.clientes, public.pedidos, public.linea_pedido,
   public.nave, public.existencias
TO nova_admin;

GRANT SELECT
ON public.modelos, public.variantes, public.producto_sku,
   public.nave, public.clientes
TO nova_trabajador;

GRANT SELECT
ON public.pedidos, public.linea_pedido, public.existencias
TO nova_trabajador;

GRANT UPDATE (estado, fecha_objetivo)
ON public.pedidos
TO nova_trabajador;

GRANT UPDATE (cantidad)
ON public.existencias
TO nova_trabajador;

GRANT SELECT
ON public.modelos, public.variantes, public.producto_sku
TO nova_cliente;

GRANT SELECT, INSERT ON public.configuraciones_xnova
TO nova_admin;

GRANT SELECT ON public.configuraciones_xnova
TO nova_trabajador;

GRANT SELECT ON public.log_eventos
TO nova_admin;

REVOKE INSERT, UPDATE ON public.linea_pedido
FROM nova_admin;

REVOKE EXECUTE ON FUNCTION public.descontar_stock(integer, integer, integer)
FROM PUBLIC;

REVOKE EXECUTE ON FUNCTION public.anadir_linea_pedido(integer, integer, integer, integer)
FROM PUBLIC;

REVOKE EXECUTE ON FUNCTION public.realizar_compra(character varying, integer, integer, integer, integer, integer)
FROM PUBLIC;

REVOKE EXECUTE ON FUNCTION public.realizar_compra_xnova(character varying, integer)
FROM PUBLIC;

GRANT EXECUTE ON FUNCTION public.anadir_linea_pedido(integer, integer, integer, integer)
TO nova_admin;

GRANT EXECUTE ON FUNCTION public.realizar_compra(character varying, integer, integer, integer, integer, integer)
TO nova_admin, nova_cliente;

GRANT EXECUTE ON FUNCTION public.realizar_compra_xnova(character varying, integer)
TO nova_admin;

REVOKE EXECUTE ON FUNCTION public.iniciar_sesion(character varying, text)
FROM PUBLIC;

GRANT EXECUTE ON FUNCTION public.iniciar_sesion(character varying, text)
TO nova_admin, nova_trabajador, nova_cliente;

GRANT EXECUTE ON FUNCTION public.usuario_sesion()
TO nova_admin, nova_trabajador, nova_cliente;

GRANT EXECUTE ON FUNCTION public.cerrar_sesion()
TO nova_admin, nova_trabajador, nova_cliente;

GRANT SELECT (id_usuario, username, id_rol, id_personal, activo)
ON public.usuarios
TO nova_admin;

GRANT UPDATE (username, id_rol, id_personal, activo)
ON public.usuarios
TO nova_admin;

GRANT SELECT ON public.roles, public.personal TO nova_admin;

REVOKE EXECUTE ON FUNCTION public.establecer_password(character varying, text)
FROM PUBLIC;

GRANT EXECUTE ON FUNCTION public.establecer_password(character varying, text)
TO nova_admin;

GRANT INSERT, UPDATE ON public.roles, public.personal TO nova_admin;

REVOKE EXECUTE ON FUNCTION public.crear_usuario(character varying, character varying)
FROM PUBLIC;

GRANT EXECUTE ON FUNCTION public.crear_usuario(character varying, character varying)
TO nova_admin;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_roles WHERE rolname = 'nova_comercial'
    ) THEN
        CREATE ROLE nova_comercial NOLOGIN;
    END IF;
END
$$;

GRANT USAGE ON SCHEMA public TO nova_comercial;

GRANT SELECT
ON public.modelos, public.variantes, public.producto_sku,
   public.nave, public.clientes, public.existencias
TO nova_comercial;

GRANT SELECT
ON public.pedidos, public.linea_pedido
TO nova_comercial;

GRANT UPDATE (estado)
ON public.pedidos
TO nova_comercial;

GRANT SELECT, INSERT ON public.configuraciones_xnova
TO nova_comercial;

GRANT EXECUTE ON FUNCTION public.realizar_compra(character varying, integer, integer, integer, integer, integer)
TO nova_comercial;

GRANT EXECUTE ON FUNCTION public.anadir_linea_pedido(integer, integer, integer, integer)
TO nova_comercial;

GRANT EXECUTE ON FUNCTION public.realizar_compra_xnova(character varying, integer)
TO nova_comercial;

GRANT EXECUTE ON FUNCTION public.iniciar_sesion(character varying, text)
TO nova_comercial;

GRANT EXECUTE ON FUNCTION public.usuario_sesion()
TO nova_comercial;

GRANT EXECUTE ON FUNCTION public.cerrar_sesion()
TO nova_comercial;
