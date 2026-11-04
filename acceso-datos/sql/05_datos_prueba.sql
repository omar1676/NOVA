INSERT INTO public.modelos (nombre, descripcion, precio_base, activo)
VALUES
('NOVA Origin', 'Estilo clasico y minimalista', 79.99, true),
('NOVA Velocity', 'Disenada para el movimiento', 119.90, true),
('NOVA Eclipse', 'Estilo urbano con contrastes', 129.99, true),
('NOVA Archive', 'Inspirada en la estetica retro Y2K', 109.90, true),
('NOVA Aura', 'Diseno ligero y contemporaneo', 99.99, true),
('NOVA Pulse', 'Estilo tecnico y futurista', 114.90, true),
('X-NOVA', 'Concepto de fabricacion personalizada mediante escaneo simulado del pie', 12000.00, true);
-- Variantes de los modelos normales

INSERT INTO public.variantes (id_modelo, color)
SELECT m.id_modelo, datos.color
FROM (
    VALUES
        ('NOVA Origin', 'Blanco'),
        ('NOVA Origin', 'Negro'),
        ('NOVA Velocity', 'Rojo'),
        ('NOVA Velocity', 'Azul'),
        ('NOVA Eclipse', 'Negro'),
        ('NOVA Eclipse', 'Gris'),
        ('NOVA Archive', 'Blanco'),
        ('NOVA Archive', 'Beige'),
        ('NOVA Aura', 'Rosa'),
        ('NOVA Aura', 'Crema'),
        ('NOVA Pulse', 'Verde'),
        ('NOVA Pulse', 'Negro')
) AS datos(nombre_modelo, color)
JOIN public.modelos m ON m.nombre = datos.nombre_modelo;
-- Generar cinco tallas por cada variante

INSERT INTO public.producto_sku (id_variante, talla, sku)
SELECT
    v.id_variante,
    t.talla,
    'NOVA-' || v.id_variante || '-' || t.talla
FROM public.variantes v
JOIN public.modelos m
    ON m.id_modelo = v.id_modelo
CROSS JOIN generate_series(40, 44) AS t(talla)
WHERE m.nombre IN (
    'NOVA Origin',
    'NOVA Velocity',
    'NOVA Eclipse',
    'NOVA Archive',
    'NOVA Aura',
    'NOVA Pulse'
);

-- Almacen principal de NOVA Sneakers

INSERT INTO public.nave (nombre, ubicacion, capacidad)
VALUES ('NOVA Central', 'Madrid', 2000);


-- Inventario inicial: 20 pares por cada SKU

INSERT INTO public.existencias (
    id_producto_sku,
    id_nave,
    cantidad
)
SELECT
    p.id_producto_sku,
    n.id_nave,
    20
FROM public.producto_sku p
CROSS JOIN public.nave n
WHERE n.nombre = 'NOVA Central';
-- Clientes ficticios de NOVA Sneakers

INSERT INTO public.clientes (nombre, email)
VALUES
    ('Daniel Jan', 'daniel.jan@example.com'),
    ('Jose Ferrer', 'jose.ferrer@example.com'),
    ('Santi Cruz', 'santi.cruz@example.com'),
    ('Nuria Soto', 'nuria.soto@example.com'),
    ('Aitor Parras', 'aitor.parras@example.com');
    -- Diez pedidos de demostracion

INSERT INTO public.pedidos (
    referencia,
    id_cliente,
    estado,
    estado_pago,
    personalizado,
    personalizacion
)
SELECT
    datos.referencia,
    c.id_cliente,
    'pendiente',
    'pendiente',
    datos.personalizado,
    datos.personalizacion
FROM (
    VALUES
    ('NOVA-0001', 'daniel.jan@example.com', false, NULL),
    ('NOVA-0002', 'jose.ferrer@example.com', false, NULL),
    ('NOVA-0003', 'santi.cruz@example.com', true, 'Cordones personalizados'),
    ('NOVA-0004', 'nuria.soto@example.com', false, NULL),
    ('NOVA-0005', 'aitor.parras@example.com', false, NULL),
    ('NOVA-0006', 'daniel.jan@example.com', true, 'Colores personalizados'),
    ('NOVA-0007', 'jose.ferrer@example.com', false, NULL),
    ('NOVA-0008', 'santi.cruz@example.com', false, NULL),
    ('NOVA-0009', 'nuria.soto@example.com', true, 'Iniciales personalizadas'),
    ('NOVA-0010', 'aitor.parras@example.com', false, NULL)
) AS datos(referencia, email, personalizado, personalizacion)
JOIN public.clientes c
    ON c.email = datos.email;
    
    -- Productos incluidos en los diez pedidos

INSERT INTO public.linea_pedido (
    id_pedido,
    id_producto_sku,
    cantidad,
    precio_unitario,
    subtotal
)
SELECT
    p.id_pedido,
    s.id_producto_sku,
    1,
    m.precio_base + v.suplemento_precio,
    0
FROM (
    VALUES
        ('NOVA-0001', 'NOVA Origin', 'Blanco', 42),
        ('NOVA-0002', 'NOVA Velocity', 'Rojo', 43),
        ('NOVA-0003', 'NOVA Eclipse', 'Negro', 41),
        ('NOVA-0004', 'NOVA Archive', 'Beige', 44),
        ('NOVA-0005', 'NOVA Aura', 'Rosa', 40),
        ('NOVA-0006', 'NOVA Pulse', 'Verde', 42),
        ('NOVA-0007', 'NOVA Origin', 'Negro', 43),
        ('NOVA-0008', 'NOVA Velocity', 'Azul', 41),
        ('NOVA-0009', 'NOVA Eclipse', 'Gris', 42),
        ('NOVA-0010', 'NOVA Archive', 'Blanco', 44)
) AS datos(referencia, modelo, color, talla)
JOIN public.pedidos p
    ON p.referencia = datos.referencia
JOIN public.modelos m
    ON m.nombre = datos.modelo
JOIN public.variantes v
    ON v.id_modelo = m.id_modelo
   AND v.color = datos.color
JOIN public.producto_sku s
    ON s.id_variante = v.id_variante
   AND s.talla = datos.talla;
