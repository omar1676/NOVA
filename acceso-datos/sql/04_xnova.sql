BEGIN;

CREATE TABLE public.configuraciones_xnova (
    id_configuracion integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_cliente integer NOT NULL,
    id_pedido integer,
    talla_referencia smallint,
    color_principal varchar(40) NOT NULL,
    color_secundario varchar(40),
    material varchar(60) NOT NULL,
    tipo_suela varchar(60) NOT NULL,
    texto_personalizado varchar(50),
    escaneo_simulado boolean NOT NULL DEFAULT true,
    fecha_creacion timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT xnova_cliente_fk
        FOREIGN KEY (id_cliente)
        REFERENCES public.clientes(id_cliente),

    CONSTRAINT xnova_pedido_fk
        FOREIGN KEY (id_pedido)
        REFERENCES public.pedidos(id_pedido),

    CONSTRAINT xnova_talla_check
        CHECK (talla_referencia BETWEEN 20 AND 55)
);

ALTER TABLE public.linea_pedido
ADD COLUMN id_configuracion_xnova integer;

ALTER TABLE public.linea_pedido
ADD CONSTRAINT linea_xnova_fk
FOREIGN KEY (id_configuracion_xnova)
REFERENCES public.configuraciones_xnova(id_configuracion);

ALTER TABLE public.linea_pedido
ALTER COLUMN id_producto_sku DROP NOT NULL;

ALTER TABLE public.linea_pedido
ADD CONSTRAINT linea_tipo_producto_check
CHECK (
    (id_producto_sku IS NOT NULL AND id_configuracion_xnova IS NULL)
    OR
    (id_producto_sku IS NULL AND id_configuracion_xnova IS NOT NULL)
);

ALTER TABLE public.linea_pedido
ADD CONSTRAINT linea_configuracion_xnova_uq
UNIQUE (id_configuracion_xnova);

COMMIT;