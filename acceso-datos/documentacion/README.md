# NOVA Sneakers — Base de datos

## 1. Descripción

La base de datos de NOVA Sneakers está desarrollada en PostgreSQL 17.

Permite gestionar modelos de zapatillas, variantes, tallas, inventario, clientes, usuarios, pedidos y productos personalizados X-NOVA.

## 2. Estructura

El diseño contiene 14 tablas:

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

Las relaciones están implementadas mediante claves primarias y foráneas.

## 3. Instalación

Crear una base de datos vacía en PostgreSQL 17.

Ejecutar estos archivos en el orden indicado:

1. sneaker-factory-esquema.sql
2. 04_xnova.sql
3. 02_funciones.sql
4. 03_triggers.sql
5. 05_datos_prueba.sql
6. 07_seguridad.sql
7. 08_auditoria.sql

El archivo 06_consultas.sql contiene las consultas de análisis y se puede ejecutar después de cargar los datos.

Los scripts están disponibles en acceso-datos/sql.

## 4. Datos de demostración

Se incluyen:

- 7 modelos de zapatillas.
- 12 variantes.
- 60 SKU.
- 1 almacén.
- 60 registros de existencias.
- 5 clientes ficticios.
- 10 pedidos, incluidos 3 personalizados.

El inventario inicial contiene 1.200 pares.

## 5. Funciones y triggers

Se implementan cinco funciones de negocio:

- calcular_subtotal_linea
- actualizar_totales_pedido
- descontar_stock
- realizar_compra
- realizar_compra_xnova

También existen dos triggers de cálculo y dos triggers de auditoría.

## 6. Seguridad

Se definen tres roles internos:

- nova_admin
- nova_trabajador
- nova_cliente

Estos roles controlan los permisos sobre las tablas.

Los roles PostgreSQL no sustituyen la autenticación de los usuarios de la aplicación web.

## 7. Auditoría

La tabla log_eventos registra cambios de estado de pedidos y cambios en las existencias mediante triggers.

## 8. Consultas SQL

El archivo 06_consultas.sql contiene ocho consultas:

1. Ventas por modelo.
2. Ranking de clientes.
3. Productos con stock bajo.
4. Pedidos personalizados.
5. Inventario por almacén.
6. Tallas más solicitadas.
7. Pedidos por mes.
8. Resumen por estado de pago.

## 9. Pruebas

La base de datos se reconstruyó desde cero en nova_validacion_final.

Se comprobaron la instalación de las tablas, las funciones, los triggers, los datos de demostración y las ocho consultas SQL.

Los diez pedidos de prueba sumaron 1.094,45 euros y los cálculos de los importes no presentaron diferencias.

## 10. Estado

La implementación SQL ha sido validada en PostgreSQL 17.

La integración con la aplicación web y Java/JDBC requiere pruebas independientes.
