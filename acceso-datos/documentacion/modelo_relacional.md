# NOVA Sneakers - Modelo relacional y normalizacion

## 1. Introduccion

La base de datos NOVA Sneakers utiliza PostgreSQL 17 y contiene 14 tablas.

Su objetivo es gestionar el catalogo de zapatillas, las variantes, el inventario, los clientes, los pedidos y la personalizacion X-NOVA.

## 2. Tablas del modelo

- modelos
- variantes
- producto_sku
- nave
- existencias
- clientes
- personal
- roles
- usuarios
- tienda_fisica
- pedidos
- linea_pedido
- log_eventos
- configuraciones_xnova

## 3. Relaciones

Las siguientes 15 claves foraneas se han comprobado directamente en PostgreSQL.

| Tabla origen | Columna | Tabla destino | Columna |
|---|---|---|---|
| variantes | id_modelo | modelos | id_modelo |
| producto_sku | id_variante | variantes | id_variante |
| existencias | id_producto_sku | producto_sku | id_producto_sku |
| existencias | id_nave | nave | id_nave |
| pedidos | id_cliente | clientes | id_cliente |
| pedidos | id_usuario | usuarios | id_usuario |
| pedidos | id_tienda | tienda_fisica | id_tienda |
| linea_pedido | id_pedido | pedidos | id_pedido |
| linea_pedido | id_producto_sku | producto_sku | id_producto_sku |
| linea_pedido | id_configuracion_xnova | configuraciones_xnova | id_configuracion |
| configuraciones_xnova | id_cliente | clientes | id_cliente |
| configuraciones_xnova | id_pedido | pedidos | id_pedido |
| usuarios | id_personal | personal | id_personal |
| usuarios | id_rol | roles | id_rol |
| log_eventos | id_usuario | usuarios | id_usuario |

## 4. Organizacion de los productos

El catalogo se divide en tres niveles:

1. modelos: nombre, descripcion y precio base.
2. variantes: colores y suplemento de precio.
3. producto_sku: combinacion concreta de variante y talla.

Esto permite almacenar un modelo una vez y relacionarlo con distintos colores y tallas.

## 5. Inventario

La tabla existencias relaciona cada SKU con una nave y su cantidad disponible.

Esto permite almacenar existencias de un producto en diferentes almacenes sin duplicar la informacion del producto.

## 6. Pedidos

La tabla pedidos guarda los datos generales de una compra.

La tabla linea_pedido almacena los productos y cantidades de cada pedido.

La relacion evita repetir los datos generales del pedido por cada producto.

Los importes y las cantidades totales se mantienen mediante triggers.

## 7. Personalizacion X-NOVA

La tabla configuraciones_xnova almacena las opciones de personalizacion.

Una linea de pedido puede estar asociada a un SKU normal o a una configuracion X-NOVA, pero no a ambos.

Esta condicion se controla mediante una restriccion CHECK.

## 8. Primera forma normal (1FN)

La primera forma normal exige que cada columna contenga valores individuales y que las filas puedan identificarse.

El diseño utiliza columnas separadas para las propiedades de los productos, clientes, pedidos y existencias.

## 9. Segunda forma normal (2FN)

La segunda forma normal exige cumplir 1FN y evitar dependencias parciales de una clave candidata compuesta.

Las entidades principales utilizan identificadores propios. Aun asi, las claves candidatas y sus dependencias deben revisarse para justificar formalmente la 2FN.

## 10. Tercera forma normal (3FN)

La tercera forma normal busca evitar dependencias transitivas inapropiadas entre atributos no clave.

El diseño separa modelos, variantes, SKU, clientes, pedidos y existencias para reducir la duplicacion de datos.

Hay campos calculados, como importe_total y cantidad_total en pedidos, que se conservan por motivos operativos y se actualizan mediante triggers.

Por tanto, no se afirma que todo el esquema cumpla estrictamente 3FN sin una revision completa de dependencias funcionales.

## 11. Integridad referencial

Las 15 claves foraneas impiden referencias a registros inexistentes.

Ademas, el esquema utiliza restricciones CHECK y UNIQUE para validar estados, importes y configuraciones X-NOVA.

## 12. Conclusion

NOVA Sneakers tiene un modelo relacional de 14 tablas y 15 claves foraneas comprobadas.

La estructura separa las entidades principales y permite gestionar productos, clientes, pedidos, inventario y personalizaciones.

La verificacion formal de la normalizacion requiere revisar las claves candidatas y dependencias de todas las tablas.

## 13. Claves y restricciones de unicidad

Se han comprobado 14 claves primarias y 11 restricciones UNIQUE mediante PostgreSQL.

Cada tabla tiene una clave primaria que identifica sus registros.

### Restricciones UNIQUE

| Tabla | Columnas unicas |
|---|---|
| clientes | email |
| existencias | id_producto_sku, id_nave |
| linea_pedido | id_configuracion_xnova |
| pedidos | referencia |
| personal | dni |
| producto_sku | id_variante, talla |
| producto_sku | sku |
| roles | nombre |
| usuarios | id_personal |
| usuarios | username |
| variantes | id_modelo, color |

### Justificacion del diseño

- Un correo electronico no puede repetirse entre clientes.
- Una combinacion de modelo y color no puede duplicarse.
- Una variante y una talla identifican un SKU concreto.
- Un SKU solo tiene un registro de existencias por almacen.
- Cada pedido tiene una referencia unica.
- Una configuracion X-NOVA solo puede utilizarse en una linea de pedido.

La restriccion UNIQUE de id_configuracion_xnova permite valores NULL para las lineas que contienen productos normales.

### Relacion con la normalizacion

La separacion de modelos, variantes y SKU reduce la repeticion de informacion.

La separacion de pedidos y lineas permite almacenar varios productos sin duplicar los datos generales del pedido.

La separacion de productos, almacenes y existencias permite controlar el inventario de cada ubicacion.

Estas decisiones apoyan la normalizacion del modelo, aunque la comprobacion formal de 3FN requiere analizar las dependencias funcionales de todos los atributos.

## 14. Dependencias funcionales y atributos derivados

### Dependencias principales

En la tabla modelos, id_modelo determina el nombre, la descripcion, el precio base y el estado del modelo.

En variantes, id_variante determina el modelo relacionado, el color y el suplemento de precio.

En producto_sku, id_producto_sku determina la variante, la talla, el codigo SKU y su estado.

En pedidos, id_pedido determina los datos generales de cada compra.

En linea_pedido, id_linea identifica cada linea y sus valores.

### Datos calculados

El diseño almacena tres valores derivados:

- linea_pedido.subtotal: cantidad multiplicada por precio_unitario.
- pedidos.cantidad_total: suma de cantidades de sus lineas.
- pedidos.importe_total: suma de subtotales de sus lineas.

Estos campos facilitan consultar los importes sin repetir los calculos en cada solicitud.

Para mantener su coherencia se utilizan triggers de PostgreSQL.

### Normalizacion

La separacion de modelos, variantes y SKU reduce duplicidades.

Las tablas pedidos y linea_pedido separan la cabecera de la compra de sus productos.

Las existencias se relacionan con cada SKU y almacen, evitando duplicar los datos de los productos.

Los atributos derivados son decisiones de implementacion que deben justificarse al analizar la normalizacion.

La comprobacion formal de 3FN para el esquema completo requiere revisar todas sus dependencias funcionales y claves candidatas.

### Validacion

Se comprobaron diez pedidos de demostracion.

Los importes y cantidades calculados coincidieron con los valores almacenados en los pedidos, sin diferencias.
