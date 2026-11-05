-- Seguridad de NOVA Sneakers
-- Ejecutar con un administrador de PostgreSQL.

-- Roles internos sin inicio de sesion
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

-- Acceso al esquema
GRANT USAGE ON SCHEMA public
TO nova_admin, nova_trabajador, nova_cliente;

-- Administrador: gestion de productos, clientes y pedidos
GRANT SELECT, INSERT, UPDATE
ON public.modelos, public.variantes, public.producto_sku,
   public.clientes, public.pedidos, public.linea_pedido,
   public.nave, public.existencias
TO nova_admin;

-- Trabajador: consultar catalogo y gestionar pedidos y stock
GRANT SELECT
ON public.modelos, public.variantes, public.producto_sku,
   public.nave, public.clientes
TO nova_trabajador;

-- Trabajador: lectura operativa
GRANT SELECT
ON public.pedidos, public.linea_pedido, public.existencias
TO nova_trabajador;

-- Actualizacion limitada a columnas autorizadas
GRANT UPDATE (estado, fecha_objetivo)
ON public.pedidos
TO nova_trabajador;

GRANT UPDATE (cantidad)
ON public.existencias
TO nova_trabajador;

-- Cliente: consultar catalogo y disponibilidad
GRANT SELECT
ON public.modelos, public.variantes, public.producto_sku
TO nova_cliente;

-- Las compras y los datos personales se gestionaran
-- desde el backend mediante operaciones autorizadas.
