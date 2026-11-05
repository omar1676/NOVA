INSERT INTO public.modelos (nombre, descripcion, precio_base, activo)
VALUES
('NOVA Origin', 'Estilo clasico y minimalista', 79.99, true),
('NOVA Velocity', 'Disenada para el movimiento', 119.90, true),
('NOVA Eclipse', 'Estilo urbano con contrastes', 129.99, true),
('NOVA Archive', 'Inspirada en la estetica retro Y2K', 109.90, true),
('NOVA Aura', 'Diseno ligero y contemporaneo', 99.99, true),
('NOVA Pulse', 'Estilo tecnico y futurista', 114.90, true),
('X-NOVA', 'Concepto de fabricacion personalizada mediante escaneo simulado del pie', 12000.00, true);

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

INSERT INTO public.producto_sku (id_variante, talla, sku)
SELECT
    v.id_variante,
    tallas.talla,
    'NOVA-' || v.id_variante || '-' || tallas.talla
FROM public.variantes v
JOIN public.modelos m
    ON m.id_modelo = v.id_modelo
CROSS JOIN generate_series(40, 44) AS tallas(talla)
WHERE m.nombre IN (
    'NOVA Origin',
    'NOVA Velocity',
    'NOVA Eclipse',
    'NOVA Archive',
    'NOVA Aura',
    'NOVA Pulse'
);


INSERT INTO public.nave (nombre, ubicacion, capacidad)
VALUES ('NOVA Central', 'Madrid', 2000);



INSERT INTO public.existencias (
    id_producto_sku,
    id_nave,
    cantidad
)
SELECT
    s.id_producto_sku,
    n.id_nave,
    20
FROM public.producto_sku s
CROSS JOIN public.nave n
WHERE n.nombre = 'NOVA Central';

INSERT INTO public.clientes (nombre, email)
VALUES
    ('Daniel Jan', 'daniel.jan@example.com'),
    ('Jose Ferrer', 'jose.ferrer@example.com'),
    ('Santi Cruz', 'santi.cruz@example.com'),
    ('Nuria Soto', 'nuria.soto@example.com'),
    ('Aitor Parras', 'aitor.parras@example.com');

INSERT INTO public.clientes (nombre, tipo, email, telefono)
VALUES
    ('Club Atletico NOVA', 'empresa', 'club.atletico@example.com', '600000000');

INSERT INTO public.roles (nombre, descripcion)
VALUES
    ('administrador', 'Gestiona el catalogo, los pedidos y el inventario'),
    ('trabajador', 'Prepara los pedidos y actualiza su estado'),
    ('comercial', 'Registra pedidos de clientes en la tienda');

INSERT INTO public.personal (nombre, dni, puesto)
VALUES
    ('Demo Administracion', 'X0000001X', 'Administrador de sistema'),
    ('Demo Taller', 'X0000002X', 'Operario de taller'),
    ('Demo Tienda', 'X0000003X', 'Comercial de tienda');

INSERT INTO public.usuarios (
    username,
    password_hash,
    id_rol,
    id_personal,
    activo
)
SELECT
    datos.username,
    '!',
    r.id_rol,
    pe.id_personal,
    true
FROM (
    VALUES
        ('admin.demo', 'administrador', 'X0000001X'),
        ('taller.demo', 'trabajador', 'X0000002X'),
        ('tienda.demo', 'comercial', 'X0000003X')
) AS datos(username, nombre_rol, dni)
JOIN public.roles r
    ON r.nombre = datos.nombre_rol
JOIN public.personal pe
    ON pe.dni = datos.dni;

INSERT INTO public.pedidos (
    referencia,
    id_cliente,
    id_usuario,
    estado,
    estado_pago,
    personalizado,
    personalizacion
)
SELECT
    datos.referencia,
    c.id_cliente,
    u.id_usuario,
    'pendiente',
    'pendiente',
    datos.personalizado,
    datos.personalizacion
FROM (
    VALUES
    ('NOVA-0001', 'daniel.jan@example.com', 'tienda.demo', false, NULL),
    ('NOVA-0002', 'jose.ferrer@example.com', 'tienda.demo', false, NULL),
    ('NOVA-0003', 'santi.cruz@example.com', 'tienda.demo', true, 'Cordones personalizados'),
    ('NOVA-0004', 'nuria.soto@example.com', 'taller.demo', false, NULL),
    ('NOVA-0005', 'aitor.parras@example.com', 'taller.demo', false, NULL),
    ('NOVA-0006', 'daniel.jan@example.com', 'taller.demo', true, 'Colores personalizados'),
    ('NOVA-0007', 'jose.ferrer@example.com', 'admin.demo', false, NULL),
    ('NOVA-0008', 'santi.cruz@example.com', 'admin.demo', false, NULL),
    ('NOVA-0009', 'nuria.soto@example.com', NULL, true, 'Iniciales personalizadas'),
    ('NOVA-0010', 'aitor.parras@example.com', NULL, false, NULL)
) AS datos(referencia, email, username, personalizado, personalizacion)
JOIN public.clientes c
    ON c.email = datos.email
LEFT JOIN public.usuarios u
    ON u.username = datos.username;
    

INSERT INTO public.linea_pedido (
    id_pedido,
    id_producto_sku,
    id_nave,
    cantidad,
    precio_unitario,
    subtotal
)
SELECT
    p.id_pedido,
    s.id_producto_sku,
    (SELECT id_nave FROM public.nave WHERE nombre = 'NOVA Central'),
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

INSERT INTO public.pedidos (
    referencia,
    id_cliente,
    id_usuario,
    estado,
    estado_pago,
    personalizado,
    personalizacion
)
SELECT
    'NOVA-0011',
    c.id_cliente,
    u.id_usuario,
    'pendiente',
    'pendiente',
    true,
    'Pedido de club: 40 pares repartidos en cuatro tallas'
FROM public.clientes c
JOIN public.usuarios u
    ON u.username = 'tienda.demo'
WHERE c.email = 'club.atletico@example.com';

INSERT INTO public.linea_pedido (
    id_pedido,
    id_producto_sku,
    id_nave,
    cantidad,
    precio_unitario,
    subtotal
)
SELECT
    p.id_pedido,
    s.id_producto_sku,
    (SELECT id_nave FROM public.nave WHERE nombre = 'NOVA Central'),
    datos.cantidad,
    m.precio_base + v.suplemento_precio,
    0
FROM (
    VALUES
        (40, 10),
        (41, 10),
        (42, 10),
        (43, 10)
) AS datos(talla, cantidad)
JOIN public.pedidos p
    ON p.referencia = 'NOVA-0011'
JOIN public.modelos m
    ON m.nombre = 'NOVA Velocity'
JOIN public.variantes v
    ON v.id_modelo = m.id_modelo
   AND v.color = 'Rojo'
JOIN public.producto_sku s
    ON s.id_variante = v.id_variante
   AND s.talla = datos.talla;
