-- Sneaker Factory — esquema inicial, PostgreSQL 14+
-- Ejecutar en una base de datos nueva y vacía.
-- No ejecuta INSERT, DROP, ni modifica datos existentes.
BEGIN;

CREATE TABLE public.modelos (
    id_modelo int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
    nombre varchar(40) NOT NULL,
    descripcion text,
    precio_base numeric(8,2) NOT NULL,
    activo boolean NOT NULL DEFAULT true,
    CONSTRAINT modelos_pk PRIMARY KEY (id_modelo),
    CONSTRAINT modelos_precio_check CHECK (precio_base >= 0)
);

CREATE TABLE public.variantes (
    id_variante int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
    id_modelo int4 NOT NULL,
    color varchar(30) NOT NULL,
    suplemento_precio numeric(8,2) NOT NULL DEFAULT 0,
    CONSTRAINT variantes_pk PRIMARY KEY (id_variante),
    CONSTRAINT variantes_id_modelo_color_uq UNIQUE (id_modelo, color),
    CONSTRAINT variantes_check_1 CHECK (suplemento_precio >= 0)
);

CREATE TABLE public.producto_sku (
    id_producto_sku int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
    id_variante int4 NOT NULL,
    talla int2 NOT NULL,
    sku varchar(30) NOT NULL,
    activo boolean NOT NULL DEFAULT true,
    CONSTRAINT producto_sku_pk PRIMARY KEY (id_producto_sku),
    CONSTRAINT producto_sku_sku_uq UNIQUE (sku),
    CONSTRAINT producto_sku_id_variante_talla_uq UNIQUE (id_variante, talla),
    CONSTRAINT producto_sku_check_1 CHECK (talla BETWEEN 20 AND 55)
);

CREATE TABLE public.nave (
    id_nave int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
    nombre varchar(80) NOT NULL,
    ubicacion varchar(180) NOT NULL,
    capacidad int4 NOT NULL,
    CONSTRAINT nave_pk PRIMARY KEY (id_nave),
    CONSTRAINT nave_check_1 CHECK (capacidad >= 0)
);

CREATE TABLE public.existencias (
    id_existencia int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
    id_producto_sku int4 NOT NULL,
    id_nave int4 NOT NULL,
    cantidad int4 NOT NULL DEFAULT 0,
    CONSTRAINT existencias_pk PRIMARY KEY (id_existencia),
    CONSTRAINT existencias_id_producto_sku_id_nave_uq UNIQUE (id_producto_sku, id_nave),
    CONSTRAINT existencias_check_1 CHECK (cantidad >= 0)
);

CREATE TABLE public.clientes (
    id_cliente int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
    nombre varchar(120) NOT NULL,
    tipo varchar(20) NOT NULL DEFAULT 'particular',
    email varchar(150) NOT NULL,
    telefono varchar(30),
    direccion_entrega text,
    activo boolean NOT NULL DEFAULT true,
    CONSTRAINT clientes_pk PRIMARY KEY (id_cliente),
    CONSTRAINT clientes_email_uq UNIQUE (email),
    CONSTRAINT clientes_check_1 CHECK (tipo IN ('particular', 'empresa'))
);

CREATE TABLE public.personal (
    id_personal int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
    nombre varchar(120) NOT NULL,
    dni varchar(20) NOT NULL,
    puesto varchar(80) NOT NULL,
    CONSTRAINT personal_pk PRIMARY KEY (id_personal),
    CONSTRAINT personal_dni_uq UNIQUE (dni)
);

CREATE TABLE public.roles (
    id_rol int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
    nombre varchar(50) NOT NULL,
    descripcion text,
    CONSTRAINT roles_pk PRIMARY KEY (id_rol),
    CONSTRAINT roles_nombre_uq UNIQUE (nombre)
);

CREATE TABLE public.usuarios (
    id_usuario int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
    username varchar(60) NOT NULL,
    password_hash text NOT NULL,
    id_rol int4 NOT NULL,
    id_personal int4,
    activo boolean NOT NULL DEFAULT true,
    CONSTRAINT usuarios_pk PRIMARY KEY (id_usuario),
    CONSTRAINT usuarios_username_uq UNIQUE (username),
    CONSTRAINT usuarios_id_personal_uq UNIQUE (id_personal)
);

CREATE TABLE public.tienda_fisica (
    id_tienda int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
    nombre varchar(100) NOT NULL,
    direccion varchar(200) NOT NULL,
    telefono varchar(30),
    CONSTRAINT tienda_fisica_pk PRIMARY KEY (id_tienda)
);

CREATE TABLE public.pedidos (
    id_pedido int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
    referencia varchar(30) NOT NULL,
    id_cliente int4 NOT NULL,
    id_usuario int4,
    id_tienda int4,
    fecha_pedido timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_objetivo date,
    estado varchar(25) NOT NULL DEFAULT 'pendiente',
    estado_pago varchar(25) NOT NULL DEFAULT 'pendiente',
    personalizado boolean NOT NULL DEFAULT false,
    personalizacion text,
    cantidad_total int4 NOT NULL DEFAULT 0,
    importe_total numeric(12,2) NOT NULL DEFAULT 0,
    CONSTRAINT pedidos_pk PRIMARY KEY (id_pedido),
    CONSTRAINT pedidos_referencia_uq UNIQUE (referencia),
    CONSTRAINT pedidos_check_1 CHECK (cantidad_total >= 0),
    CONSTRAINT pedidos_check_2 CHECK (importe_total >= 0),
    CONSTRAINT pedidos_check_3 CHECK (estado IN ('pendiente', 'en_preparacion', 'enviado', 'entregado', 'cancelado')),
    CONSTRAINT pedidos_check_4 CHECK (estado_pago IN ('pendiente', 'pagado', 'reembolsado'))
);

CREATE TABLE public.linea_pedido (
    id_linea int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
    id_pedido int4 NOT NULL,
    id_producto_sku int4 NOT NULL,
    cantidad int4 NOT NULL,
    precio_unitario numeric(8,2) NOT NULL,
    subtotal numeric(12,2) NOT NULL,
    CONSTRAINT linea_pedido_pk PRIMARY KEY (id_linea),
    CONSTRAINT linea_pedido_check_1 CHECK (cantidad > 0),
    CONSTRAINT linea_pedido_check_2 CHECK (precio_unitario >= 0),
    CONSTRAINT linea_pedido_check_3 CHECK (subtotal >= 0)
);

CREATE TABLE public.log_eventos (
    id_evento int4 GENERATED ALWAYS AS IDENTITY NOT NULL,
    id_usuario int4,
    tabla_afectada varchar(80) NOT NULL,
    id_registro int4,
    accion varchar(30) NOT NULL,
    fecha_hora timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    detalle text,
    CONSTRAINT log_eventos_pk PRIMARY KEY (id_evento)
);

ALTER TABLE public.variantes ADD CONSTRAINT variantes_id_modelo_fk FOREIGN KEY (id_modelo) REFERENCES public.modelos (id_modelo);
ALTER TABLE public.producto_sku ADD CONSTRAINT producto_sku_id_variante_fk FOREIGN KEY (id_variante) REFERENCES public.variantes (id_variante);
ALTER TABLE public.existencias ADD CONSTRAINT existencias_id_producto_sku_fk FOREIGN KEY (id_producto_sku) REFERENCES public.producto_sku (id_producto_sku);
ALTER TABLE public.existencias ADD CONSTRAINT existencias_id_nave_fk FOREIGN KEY (id_nave) REFERENCES public.nave (id_nave);
ALTER TABLE public.usuarios ADD CONSTRAINT usuarios_id_rol_fk FOREIGN KEY (id_rol) REFERENCES public.roles (id_rol);
ALTER TABLE public.usuarios ADD CONSTRAINT usuarios_id_personal_fk FOREIGN KEY (id_personal) REFERENCES public.personal (id_personal);
ALTER TABLE public.pedidos ADD CONSTRAINT pedidos_id_cliente_fk FOREIGN KEY (id_cliente) REFERENCES public.clientes (id_cliente);
ALTER TABLE public.pedidos ADD CONSTRAINT pedidos_id_usuario_fk FOREIGN KEY (id_usuario) REFERENCES public.usuarios (id_usuario);
ALTER TABLE public.pedidos ADD CONSTRAINT pedidos_id_tienda_fk FOREIGN KEY (id_tienda) REFERENCES public.tienda_fisica (id_tienda);
ALTER TABLE public.linea_pedido ADD CONSTRAINT linea_pedido_id_pedido_fk FOREIGN KEY (id_pedido) REFERENCES public.pedidos (id_pedido);
ALTER TABLE public.linea_pedido ADD CONSTRAINT linea_pedido_id_producto_sku_fk FOREIGN KEY (id_producto_sku) REFERENCES public.producto_sku (id_producto_sku);
ALTER TABLE public.log_eventos ADD CONSTRAINT log_eventos_id_usuario_fk FOREIGN KEY (id_usuario) REFERENCES public.usuarios (id_usuario);

-- Índices para mejorar JOIN sobre claves foráneas
CREATE INDEX variantes_id_modelo_idx ON public.variantes (id_modelo);
CREATE INDEX producto_sku_id_variante_idx ON public.producto_sku (id_variante);
CREATE INDEX existencias_id_producto_sku_idx ON public.existencias (id_producto_sku);
CREATE INDEX existencias_id_nave_idx ON public.existencias (id_nave);
CREATE INDEX usuarios_id_rol_idx ON public.usuarios (id_rol);
CREATE INDEX usuarios_id_personal_idx ON public.usuarios (id_personal);
CREATE INDEX pedidos_id_cliente_idx ON public.pedidos (id_cliente);
CREATE INDEX pedidos_id_usuario_idx ON public.pedidos (id_usuario);
CREATE INDEX pedidos_id_tienda_idx ON public.pedidos (id_tienda);
CREATE INDEX linea_pedido_id_pedido_idx ON public.linea_pedido (id_pedido);
CREATE INDEX linea_pedido_id_producto_sku_idx ON public.linea_pedido (id_producto_sku);
CREATE INDEX log_eventos_id_usuario_idx ON public.log_eventos (id_usuario);

COMMIT;
