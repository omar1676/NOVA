-- 04_xnova.sql — zapatillas X-NOVA hechas a medida y su relacion con las lineas de pedido

BEGIN;

-- Tabla de configuraciones X-NOVA: el diseno que elige el cliente.
-- id_pedido queda vacio hasta que se compra
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

-- Una linea de pedido puede apuntar a una configuracion X-NOVA
ALTER TABLE public.linea_pedido
ADD COLUMN id_configuracion_xnova integer;

ALTER TABLE public.linea_pedido
ADD CONSTRAINT linea_xnova_fk
FOREIGN KEY (id_configuracion_xnova)
REFERENCES public.configuraciones_xnova(id_configuracion);

-- Las lineas X-NOVA no tienen SKU, asi que id_producto_sku pasa a admitir NULL
ALTER TABLE public.linea_pedido
ALTER COLUMN id_producto_sku DROP NOT NULL;

-- Cada linea es de catalogo (SKU) o X-NOVA (configuracion), nunca las dos ni ninguna
ALTER TABLE public.linea_pedido
ADD CONSTRAINT linea_tipo_producto_check
CHECK (
    (id_producto_sku IS NOT NULL AND id_configuracion_xnova IS NULL)
    OR
    (id_producto_sku IS NULL AND id_configuracion_xnova IS NOT NULL)
);

-- Una configuracion solo se puede comprar una vez
ALTER TABLE public.linea_pedido
ADD CONSTRAINT linea_configuracion_xnova_uq
UNIQUE (id_configuracion_xnova);

-- Solo las lineas de catalogo con nave pueden descontar stock (X-NOVA no tiene stock)
ALTER TABLE public.linea_pedido
ADD CONSTRAINT linea_stock_descontado_check
CHECK (
    stock_descontado = false
    OR (
        id_producto_sku IS NOT NULL
        AND id_nave IS NOT NULL
        AND id_configuracion_xnova IS NULL
    )
);

COMMIT;