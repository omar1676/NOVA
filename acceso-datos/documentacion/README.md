# NOVA Sneakers — Base de datos

## 1. Qué es esto

La base de datos de NOVA Sneakers, hecha en PostgreSQL 17. Guarda el catálogo
de zapatillas (modelos, colores y tallas), el inventario de los almacenes, los
clientes, los pedidos y las personalizaciones X-NOVA.

Los scripts están en `acceso-datos/sql`.

## 2. Requisitos

- PostgreSQL 17 (probado con la 17.11).
- Un usuario con permisos de administrador, porque hay que crear la base y tres roles.
- pgAdmin 4 o psql.

No hace falta ninguna extensión ni librería externa.

## 3. Cómo reconstruir la base desde cero

**Importante: hay que usar una base de datos nueva y vacía.** Los scripts no
comprueban si los objetos ya existen, así que lanzarlos dos veces sobre la
misma base da error. Si hay que repetir la instalación, se borra la base y se
crea otra.

```sql
CREATE DATABASE nova_sneakers;
```

Después hay que conectarse a esa base y lanzar los scripts **en este orden**.
El número del fichero no es el orden de ejecución: la numeración viene de
cuándo se escribió cada uno.

| # | Fichero | Qué hace | Necesita admin |
|---|---|---|---|
| 1 | `sneaker-factory-esquema.sql` | Crea el esquema `extensiones` con pgcrypto, 13 tablas, 13 claves foráneas y 12 índices | **sí** |
| 2 | `04_xnova.sql` | Crea `configuraciones_xnova` y añade a `linea_pedido` la columna que la referencia, más el CHECK del stock | no |
| 3 | `02_funciones.sql` | Las 14 funciones de negocio y de sesión | no |
| 4 | `03_triggers.sql` | Los 5 triggers de cálculo y control | no |
| 5 | `05_datos_prueba.sql` | **Inserta los datos de demostración** | no |
| 6 | `07_seguridad.sql` | **Crea los 4 roles** y reparte permisos | **sí** |
| 7 | `08_auditoria.sql` | Las 5 funciones y 5 triggers de auditoría | no |
| 8 | `06_consultas.sql` | Las 8 consultas del enunciado. Solo lee | no |
| 9 | `09_pruebas.sql` | La batería de pruebas. Opcional | no |
| 10 | `10_caso_custom.sql` | El caso del club deportivo: 40 pares en varias tallas, de principio a fin. Opcional | no |
| 11 | `11_dml_ejemplos.sql` | Ejemplos de INSERT, UPDATE y DELETE, y casos rechazados por las restricciones. Opcional | no |
| 12 | `12_consultas_panel.sql` | Consultas parametrizadas de búsqueda e indicadores para el panel Java. Opcional | no |
| 13 | `13_activar_usuarios.sql` | **Pone las contraseñas de las tres cuentas de demostración.** Pregunta por teclado; no guarda nada en el repositorio | **sí** |
| 14 | `14_caso_custom_persistente.sql` | **Deja el pedido `CUSTOM-40` guardado de verdad**, con 40 pares en cuatro tallas. Va al final, después de las pruebas. Opcional | no |
| 15 | `15_exportar_fabricacion.sql` | Exporta a un CSV para PSP la orden de fabricación de un pedido Custom confirmado de 40 pares: `CUSTOM-40` por defecto (necesita el 14) u otro con `-v referencia=SO024`. Opcional | no |
| 16 | `16_exportar_csv_dashboard.sql` | Exporta los cinco CSV del contrato (clientes, modelos, pedidos, líneas y stock) para el dashboard. Solo lee. Opcional | no |
| 17 | `17_usuario_java.sql` | **Crea `java_nova`, el usuario con el que se conecta la aplicación Java**, y deja al comercial marcar pedidos Custom. Pide la contraseña por teclado. Se puede lanzar después del 7 o al final | **sí** |
| 18 | `18_datos_so024.sql` | **Datos del caso común SO024**: el cliente Club Halcones, el modelo Runner X con sus tallas 38–46 (SKU y existencias). **No crea el pedido**: SO024 se crea y confirma desde la aplicación Java. El precio, el color y el stock se pasan con `-v` hasta que se acuerden; sin ellos no inserta nada. Va al final, después de las pruebas | no |
| 19 | `19_usuario_web.sql` | **Crea `panel_lectura`, un rol de solo lectura, y `web_nova`, el usuario con el que se conecta el servidor del panel de administración** (`servidor-admin/`). `web_nova` solo puede pasar a `panel_lectura` con `SET ROLE` y no hereda nada. `panel_lectura` no puede escribir en ninguna tabla ni leer `password_hash`, `dni` ni `direccion_entrega`. Pide la contraseña por teclado. Se puede lanzar después del 7 o al final | **sí** |

**Los tres últimos van al final, y el orden importa.** El orden correcto es:
instalación (1–7) → pruebas (8–12) → contraseñas (13) → `CUSTOM-40` (14) →
exportaciones (15 y 16) → datos de SO024 (18). El 17 y el 19 pueden ir en
cualquier momento después del 7: la batería `09_pruebas.sql` da 91 de 91 con
los dos instalados.
El 18 no puede ir antes de las pruebas: con Runner X ya cargado, dos
comprobaciones de `09_pruebas.sql` que cuentan los modelos de los datos de
demostración dan `FAIL`.

Dos razones, las dos comprobadas ejecutándolo:

- **El 13 va después de las pruebas, no antes.** Las comprobaciones `A1` y `A2`
  verifican que las tres cuentas llegan *sin* contraseña utilizable. Si el 13 ya
  se ha ejecutado, esas dos dan `FAIL` con toda la razón.
- **El 14 va después del 13**, porque inicia sesión como `tienda.demo` y
  necesita su contraseña. Y añade un pedido, así que después ya no hay 11
  pedidos ni 14 líneas. Las comprobaciones de `09_pruebas.sql` que dependían de
  esas cifras se reescribieron para medir integridad y diferencias antes/después,
  así que **ahora pasan igual con `CUSTOM-40` guardado o sin él**.

El primer script necesita permisos de administrador porque crea una
extensión. `CREATE EXTENSION pgcrypto` solo lo puede hacer un superusuario o
alguien con el rol `pg_create_extension`. Se usa para guardar las contraseñas
de los usuarios de la aplicación, y va en su propio esquema, `extensiones`,
para que sus 37 funciones no se mezclen con las nuestras en `public`.

Por qué este orden y no otro:

- `04_xnova.sql` va **antes** de `02_funciones.sql` porque la función
  `realizar_compra_xnova` usa la tabla `configuraciones_xnova`.
- El CHECK `linea_stock_descontado_check` está en `04_xnova.sql` y no en el
  esquema porque necesita la columna `id_configuracion_xnova`, que se añade
  en ese mismo script.
- `03_triggers.sql` va después de `02_funciones.sql` porque los triggers
  necesitan que las funciones existan.
- `05_datos_prueba.sql` va después de los triggers, y por eso los subtotales
  y los importes totales se calculan solos al insertar.
- `08_auditoria.sql` va después de los datos **a propósito**: así
  `log_eventos` arranca vacía y solo registra lo que pase a partir de ahí.
  Si se quisiera auditar también la carga inicial, habría que lanzarlo antes.

Scripts que **modifican el esquema**: 1, 2, 3, 4, 6 y 7.
Scripts que **insertan datos de forma permanente**: solo el 5.
Scripts que **solo consultan**: 8 y 12.
Scripts que **escriben y deshacen lo escrito** (todo dentro de `BEGIN ...
ROLLBACK`, así que se pueden repetir sin ensuciar la base): 9, 10 y 11.

## 4. Datos de demostración

`05_datos_prueba.sql` deja la base así:

| Qué | Cuántos |
|---|---|
| Modelos | 7 (6 normales y X-NOVA) |
| Variantes de color | 12 |
| SKU (variante + talla) | 60 (12 variantes x 5 tallas, de la 40 a la 44) |
| Almacenes | 1 (NOVA Central, Madrid) |
| Registros de existencias | 60, con 20 pares cada uno = **1.200 pares** |
| Clientes | 6 (5 particulares y el Club Atletico NOVA, de tipo empresa) |
| Roles de aplicación | 3 (administrador, trabajador, comercial) |
| Empleados (`personal`) | 3 |
| Usuarios (`usuarios`) | 3 |
| Pedidos | 11, de los cuales 4 marcados como personalizados |
| Líneas de pedido | 14 |
| Importe total de los 11 pedidos | **5.890,45 €** |
| Eventos de auditoría | 0 |

### El pedido de varias tallas

El enunciado pide al menos un pedido que incluya **varias tallas**, no solo
varias líneas. Ese es `NOVA-0011`: el Club Atletico NOVA pide **40 pares de
NOVA Velocity en rojo**, repartidos en cuatro tallas (10 pares de la 40, la
41, la 42 y la 43), por un importe de 4.796,00 €.

Es también la correspondencia con el caso Custom del enunciado: donde el
profesor habla del modelo **Runner X**, aquí se usa **NOVA Velocity**, que es
el modelo de running del catálogo. El recorrido completo de ese caso (crear,
confirmar, auditar, cancelar y devolver) está en `10_caso_custom.sql`.

### Usuarios ficticios

La tabla `usuarios` estaba vacía y eso impedía comprobar la auditoría: la
columna `log_eventos.id_usuario` tiene una clave foránea, así que sin usuarios
no había ningún valor válido que guardar. Ahora hay tres, inventados a
propósito y sin ningún dato real:

| username | Rol | Empleado | DNI |
|---|---|---|---|
| `admin.demo` | administrador | Demo Administracion | X0000001X |
| `taller.demo` | trabajador | Demo Taller | X0000002X |
| `tienda.demo` | comercial | Demo Tienda | X0000003X |

Los nombres, los DNI y los `username` son inventados.

**Las tres cuentas llegan sin contraseña utilizable.** La columna
`password_hash` lleva un solo carácter, `!`, que es la convención de toda la
vida en Unix para "cuenta sin contraseña". No es un hash, no se puede
confundir con uno, y no hay forma de que coincida con nada: `iniciar_sesion`
exige que el hash empiece por `$`, así que mientras valga `!` el login falla
siempre con "La cuenta no tiene contrasena establecida". En el repositorio no
hay ninguna contraseña, ni real ni de ejemplo.

Para poder entrar con una cuenta de demostración hay que ponerle contraseña,
y para eso está `13_activar_usuarios.sql`. Lo lanza **quien instaló la base**,
porque `establecer_password` solo lo puede ejecutar el propietario o
`nova_admin`:

```
psql -U postgres -d nova_sneakers -f 13_activar_usuarios.sql
```

El script **pregunta las tres contraseñas por teclado** con `\prompt`, las
guarda cifradas con bcrypt y después comprueba que el login funciona. No queda
ninguna contraseña en el repositorio, ni en el script, ni en el historial de
psql, porque las variables se borran con `\unset` al acabar.

Nunca hay que escribir un `UPDATE` a mano sobre `password_hash`: de hecho ya no
se puede, porque ningún rol tiene permiso sobre esa columna (ver apartado 9).

**El primer inicio de sesión de Java.** Hay un orden que no se puede saltar:
Java no puede entrar como administrador hasta que `admin.demo` tenga
contraseña, y ponerla requiere acceso a la base. Es decir, **activar las
cuentas es un paso de instalación, no algo que haga la aplicación**. El orden
es: instalar los scripts 1 a 7, lanzar el 13 y teclear las contraseñas, y a
partir de ahí Java ya puede hacer login. Si alguien arranca Java antes, todos
los logins fallarán con "La cuenta no tiene contrasena establecida", que es el
comportamiento correcto.

De los 11 pedidos de demostración, **9 tienen un usuario asignado y 2 no**
(`id_usuario` a nulo), para que se vea que la columna es opcional y que la
auditoría se comporta distinto en cada caso.

Quedan dos tablas sin datos: `tienda_fisica`, porque ningún pedido de
demostración se hace en tienda, y `log_eventos`, que se llena sola cuando se
usa la base.

**Un detalle importante:** los 11 pedidos se cargan en estado `pendiente` y
**ninguno descuenta stock**, porque el stock se mueve al confirmar (apartado
7b). Sus líneas llevan ya su almacén en `id_nave` y `stock_descontado` a
false. Por eso el stock sigue en 1.200 después de la carga, y por eso cancelar
uno de ellos no devuelve nada: nunca se confirmó.

Como las líneas sí tienen almacén, cualquiera de esos pedidos se puede
confirmar para ver el movimiento de existencias. Confirmar `NOVA-0011`, por
ejemplo, baja el stock en 40 pares de golpe.

El catálogo de 100 zapatillas de la web es una demostración aparte y no está
en la base de datos.

## 5. Las 14 tablas

modelos, variantes, producto_sku, nave, existencias, clientes, personal,
roles, usuarios, tienda_fisica, pedidos, linea_pedido, log_eventos y
configuraciones_xnova.

El detalle de las relaciones, las 16 claves foráneas y la normalización está
en `documentacion/modelo_relacional.md`.

El catálogo se organiza en tres niveles: un **modelo** (nombre y precio base)
tiene varias **variantes** (colores, con su suplemento de precio), y cada
variante tiene varios **SKU** (una talla concreta). El inventario se guarda en
`existencias`, que relaciona un SKU con un almacén y una cantidad.

## 6. Funciones

Son 19: 9 de negocio, 5 de sesión y usuarios, y 5 de auditoría.

| Función | Para qué sirve |
|---|---|
| `calcular_subtotal_linea()` | Multiplica cantidad por precio y guarda el resultado en `subtotal` |
| `actualizar_totales_pedido()` | Suma las líneas de un pedido y actualiza `cantidad_total` e `importe_total` |
| `descontar_stock(sku, nave, cantidad)` | Resta unidades de `existencias`. Falla si no hay suficientes |
| `anadir_linea_pedido(pedido, sku, nave, cantidad)` | Busca el precio y crea la línea. **No toca el stock.** Solo si el pedido está pendiente |
| `realizar_compra(referencia, cliente, sku, nave, cantidad, usuario)` | Crea el pedido **en estado pendiente** con su primera línea. Devuelve el `id_pedido` |
| `realizar_compra_xnova(referencia, configuracion)` | Crea un pedido personalizado a partir de una configuración X-NOVA |
| `descontar_stock_confirmacion()` | **Al confirmar un pedido**, descuenta el stock de todas sus líneas y las marca. Es `SECURITY DEFINER` |
| `devolver_stock_cancelacion()` | Al cancelar, devuelve las unidades de las líneas que las habían descontado. Es `SECURITY DEFINER`, ver apartado 9 |
| `iniciar_sesion(username, password)` | Comprueba la contraseña con bcrypt y, si es correcta, deja al usuario como operador de la transacción. Devuelve su `id_usuario` |
| `usuario_sesion()` | Devuelve el `id_usuario` del operador de la transacción actual, o nulo si no hay sesión |
| `cerrar_sesion()` | Borra el operador de la transacción actual |
| `establecer_password(username, password)` | Genera el hash bcrypt de una contraseña y lo guarda. Solo `nova_admin` |
| `crear_usuario(username, rol)` | Crea un usuario de la aplicación sin contraseña utilizable. Solo `nova_admin` |
| `auditar_alta_pedido()` | Escribe en `log_eventos` cuando se crea un pedido |
| `auditar_baja_modelo()` | Escribe en `log_eventos` cuando un modelo pasa a no activo |
| `auditar_baja_sku()` | Escribe en `log_eventos` cuando un SKU pasa a no activo |
| `proteger_linea_pedido()` | Impide modificar o borrar líneas de compras ya registradas |
| `auditar_estado_pedido()` | Escribe en `log_eventos` cuando cambia el estado de un pedido |
| `auditar_existencias()` | Escribe en `log_eventos` cuando cambia una cantidad de `existencias` |

Para un pedido de varios productos: primero `realizar_compra`, que crea el
pedido con su primera línea, y luego una llamada a `anadir_linea_pedido` por
cada producto adicional. **Ninguna de las dos toca el inventario**: el stock se
mueve al confirmar el pedido, y se devuelve al cancelarlo. Ver apartado 7b.

El último parámetro de `realizar_compra`, `p_id_usuario`, es opcional y vale
NULL si no se pasa. Sirve para guardar quién hizo la compra. Mientras la
aplicación no lo envíe, se queda a nulo (ver problemas conocidos).

## 7. Triggers

Son 10.

| Trigger | Tabla | Cuándo salta | Qué hace |
|---|---|---|---|
| `trg_calcular_subtotal` | `linea_pedido` | BEFORE INSERT OR UPDATE | Recalcula el subtotal |
| `trg_proteger_linea_pedido` | `linea_pedido` | BEFORE UPDATE OR DELETE | Bloquea cambios no permitidos |
| `trg_actualizar_totales` | `linea_pedido` | AFTER INSERT OR DELETE OR UPDATE | Actualiza los totales del pedido |
| `trg_descontar_stock_confirmacion` | `pedidos` | AFTER UPDATE OF estado | **Descuenta stock al confirmar** |
| `trg_devolver_stock_cancelacion` | `pedidos` | AFTER UPDATE OF estado | Devuelve stock al cancelar |
| `trg_auditar_alta_pedido` | `pedidos` | AFTER INSERT | Registra el alta del pedido |
| `trg_auditar_estado_pedido` | `pedidos` | AFTER UPDATE OF estado | Registra el cambio de estado o la baja lógica |
| `trg_auditar_existencias` | `existencias` | AFTER UPDATE OF cantidad | Registra el cambio de stock |
| `trg_auditar_baja_modelo` | `modelos` | AFTER UPDATE OF activo | Registra la baja lógica de un modelo |
| `trg_auditar_baja_sku` | `producto_sku` | AFTER UPDATE OF activo | Registra la baja lógica de un SKU |

Los tres triggers de recálculo de importes cubren las tres operaciones sobre
`linea_pedido`: `trg_actualizar_totales` es `AFTER INSERT OR DELETE OR UPDATE`,
así que añadir, cambiar o borrar una línea siempre deja el pedido cuadrado. La
prueba `P3` lo comprueba sobre los 11 pedidos y la `D5` al borrar una línea.

**No hay recursión.** Los triggers de auditoría solo escriben en
`log_eventos`, que no tiene ningún trigger. `trg_devolver_stock_cancelacion`
escribe en `existencias` y en `linea_pedido`, lo que dispara
`trg_auditar_existencias`, `trg_calcular_subtotal`, `trg_proteger_linea_pedido`
y `trg_actualizar_totales`; ninguno de ellos vuelve a tocar `pedidos.estado`,
que es lo que cerraría el círculo. Y `trg_auditar_estado_pedido` y
`trg_devolver_stock_cancelacion` llevan `WHEN (OLD.estado IS DISTINCT FROM
NEW.estado)`, así que repetir el mismo estado no dispara nada.

### 7b. Cuándo se mueve el stock, y por qué así

Esto es lo que pide el apartado 3.6 del enunciado, literalmente: *"mantener el
stock disponible cuando se confirme o cancele un pedido. No descontar stock en
cada edición de una línea y otra vez al confirmar."*

El ciclo es:

| Paso | Qué pasa con el stock | Marca `stock_descontado` |
|---|---|---|
| `realizar_compra` crea el pedido en `pendiente` | **no se toca** | false |
| `anadir_linea_pedido` añade más líneas | **no se toca** | false |
| se edita la cantidad de una línea pendiente | **no se toca** | false |
| `UPDATE pedidos SET estado = 'confirmado'` | **se descuenta una vez** | pasa a true |
| se vuelve a confirmar | no se toca otra vez | sigue true |
| `UPDATE pedidos SET estado = 'cancelado'` | **se devuelve** | vuelve a false |

Las tres piezas que lo sostienen:

1. **`trg_descontar_stock_confirmacion`** salta `AFTER UPDATE OF estado` con
   `WHEN (NEW.estado = 'confirmado' AND OLD.estado <> 'confirmado')`, y su
   bucle recorre solo las líneas con `stock_descontado = false`. Por eso
   confirmar dos veces no descuenta dos veces: la condición del `WHEN` ya no se
   cumple, y aunque se cumpliera, no quedarían líneas con la marca apagada.
2. **`descontar_stock`** lleva la comprobación dentro del `WHERE` del `UPDATE`,
   así que una confirmación nunca puede dejar existencias negativas.
3. **Si una línea no cabe, falla la confirmación entera.** La excepción aborta
   la transacción, así que no queda ninguna línea descontada a medias y el
   pedido se queda en `pendiente`. Está probado con un pedido de dos líneas
   donde la primera sí cabe y la segunda no (prueba `P9b`).

**Lo que se puede editar y lo que no.** Mientras el pedido está `pendiente` sus
líneas se pueden cambiar y borrar libremente, porque todavía no han movido
inventario. En cuanto se confirma, quedan bloqueadas por
`trg_proteger_linea_pedido`. Eso es justo lo que quiere decir el enunciado con
"no descontar stock en cada edición de una línea".

**Las líneas X-NOVA no entran en este circuito.** Son fabricación a medida, no
salen de almacén: el bucle las salta porque no tienen SKU ni almacén, y el
CHECK `linea_stock_descontado_check` impide que su marca se encienda nunca.

Cuatro cosas más que conviene entender de este montaje:

**El trigger de protección no cubre INSERT, y es a propósito.** Si lo cubriera,
bloquearía a `realizar_compra`, a `realizar_compra_xnova` y a la carga de
datos de prueba, porque las tres insertan líneas. Al cubrir solo UPDATE y
DELETE, lo que impide es que alguien toque una compra **después** de hacerla.

**El trigger de cancelación tiene que ser AFTER, no BEFORE.** Cuando devuelve
el stock hace un UPDATE sobre `linea_pedido` para apagar la marca, y eso
dispara el trigger de protección, que solo autoriza ese cambio si el pedido ya
está cancelado. Con AFTER, la fila de `pedidos` ya tiene el estado nuevo
cuando se consulta, así que da permiso. Con BEFORE leería el estado anterior y
cancelar sería imposible.

**Los dos triggers BEFORE de `linea_pedido` saltan por orden alfabético**, así
que `trg_calcular_subtotal` va antes que `trg_proteger_linea_pedido`. No pasa
nada porque la protección no vigila la columna `subtotal`: si la vigilara, el
recálculo del trigger anterior parecería una modificación y bloquearía
cualquier cambio legítimo.

## 8. Restricciones

Además de las 14 claves primarias y las 16 foráneas:

| Restricción | Qué asegura |
|---|---|
| `linea_tipo_producto_check` | Una línea es de SKU normal **o** de X-NOVA, nunca de las dos cosas ni de ninguna |
| `linea_stock_descontado_check` | Si una línea dice que descontó stock, tiene que tener SKU y almacén, y no puede ser X-NOVA |
| `linea_configuracion_xnova_uq` | Una configuración X-NOVA solo se puede usar en una línea |
| `pedidos_check_3` | El estado solo puede ser pendiente, en_preparacion, enviado, entregado o cancelado |
| `pedidos_check_4` | El estado de pago solo puede ser pendiente, pagado o reembolsado |
| `existencias_check_1` | La cantidad en almacén nunca puede ser negativa |
| `clientes_email_uq`, `pedidos_referencia_uq`, `producto_sku_sku_uq` | No se repiten correos, referencias ni códigos SKU |

El `linea_stock_descontado_check` es el que hace posible la devolución: sin
almacén no se sabría dónde reponer las unidades.

## 9. Roles y permisos

Cuatro roles, todos `NOLOGIN`: no se conecta nadie con ellos directamente, los
usa la aplicación. Para probarlos en pgAdmin se usa `SET ROLE nombre_del_rol`
y luego `RESET ROLE`.

| | nova_cliente | nova_comercial | nova_trabajador | nova_admin |
|---|---|---|---|---|
| Catálogo (modelos, variantes, SKU) | ver | ver | ver | ver, crear, modificar |
| Clientes | no | ver | ver | ver, crear, modificar |
| Pedidos | no | ver, cambiar `estado` y marcar Custom (`personalizado`, `personalizacion`, script 17) | ver, y cambiar `estado` y `fecha_objetivo` | ver, crear, modificar |
| Líneas de pedido | no | ver | ver | **solo ver** |
| Existencias | no | ver | ver y cambiar `cantidad` | ver, crear, modificar |
| Configuraciones X-NOVA | no | ver y crear | ver | ver y crear |
| Auditoría (`log_eventos`) | no | no | no | **solo ver** |
| Confirmar o cancelar un pedido | no | **sí** | **sí** | sí |
| Usuarios de la aplicación | no | no | no | ver (sin el hash), crear, modificar |
| Roles funcionales y personal | no | no | no | ver, crear, modificar |
| `iniciar_sesion` | sí | sí | sí | sí |
| `establecer_password` y `crear_usuario` | no | no | no | **sí, solo él** |
| `realizar_compra` | **sí** | **sí** | no | sí |
| `realizar_compra_xnova` | no | **sí** | no | sí |
| `anadir_linea_pedido` | no | **sí** | no | sí |
| `descontar_stock` | no | no | no | no |

**Por qué hay un cuarto rol.** Con tres no se podía cubrir el perfil
**comercial**, que vende en tienda: `nova_cliente` no puede leer `pedidos` ni
`clientes`, `nova_trabajador` no puede vender, y `nova_admin` sí puede todo
pero también gestiona usuarios. Así que un comercial solo podía trabajar
conectado como administrador, y entonces podría crear usuarios invocando la
función directamente. El enunciado exige justo lo contrario: *"probar que un
usuario sin autorización no puede ejecutar una operación restringida, ni
siquiera intentando invocar directamente la operación de persistencia"*.

Con `nova_comercial` la correspondencia es uno a uno, y eso es lo que comprueba
la prueba `G8`:

| Rol funcional (tabla `roles`) | Rol de PostgreSQL |
|---|---|
| `administrador` | `nova_admin` |
| `trabajador` | `nova_trabajador` |
| `comercial` | `nova_comercial` |

`nova_cliente` se queda para el escaparate web: solo ve catálogo y puede
comprar. No es un rol funcional de la aplicación de gestión.

Tres decisiones que hay que saber explicar:

**Ningún rol puede insertar líneas de pedido a mano.** Se le quitó el permiso
incluso a `nova_admin`. El motivo es que un INSERT directo crea la línea pero
no descuenta el stock, y eso descuadra el inventario. La única forma de crear
una línea es por `realizar_compra` o `anadir_linea_pedido`.

**Las funciones de compra son `SECURITY DEFINER`.** Eso significa que se
ejecutan con los permisos de quien las creó, no de quien las llama. Así
`nova_cliente` puede comprar aunque no tenga permiso para escribir en
`pedidos` ni en `linea_pedido`. Es lo que permite cerrar los permisos de las
tablas sin romper las compras. Las cuatro llevan `SET search_path =
pg_catalog, public` para que nadie pueda engañarlas cambiando el search_path,
y se les ha quitado el permiso `EXECUTE` que PostgreSQL da por defecto a
PUBLIC, para después concederlo solo a los roles que lo necesitan.

**El trigger de cancelación también es `SECURITY DEFINER`, y hace falta.**
Esto se descubrió probando, no leyendo el código. `devolver_stock_cancelacion`
empieza con un `SELECT ... FOR UPDATE` sobre `linea_pedido`, y en PostgreSQL
`FOR UPDATE` exige permiso de **UPDATE** sobre la tabla, no solo de SELECT.
Como a `nova_admin` se le había quitado ese permiso y `nova_trabajador` nunca
lo tuvo, **ningún rol podía cancelar un pedido**: el error era `permission
denied for table linea_pedido`. Y fallaba incluso al cancelar un pedido que no
tenía nada que devolver, porque el `FOR UPDATE` se evalúa antes de saber si
alguna fila cumple la condición.

La solución **no** fue conceder UPDATE sobre `linea_pedido`, porque eso
abriría justo el agujero que cierra el apartado anterior. Lo que se hizo fue
marcar la función como `SECURITY DEFINER` con su `search_path` fijado, igual
que las dos funciones de auditoría. Así la devolución de stock se ejecuta con
los permisos del propietario, mientras que un `UPDATE` directo sobre
`linea_pedido` sigue estando prohibido para todos los roles.

Las funciones pertenecen al usuario que instala la base. En las pruebas es
`postgres`; en un entorno real conviene que sea un usuario propietario que no
sea superusuario. La prueba `P1b` comprueba que todas las funciones
`SECURITY DEFINER` pertenecen al mismo dueño que las tablas, y la `P1c` que
todas fijan su `search_path`.

### Tres cosas distintas que se llaman "usuario"

Esto es lo que más se confunde al explicar el proyecto, así que conviene
tenerlo separado:

| Qué es | Dónde vive | Para qué sirve |
|---|---|---|
| **Rol de PostgreSQL** (`nova_admin`, `nova_trabajador`, `nova_cliente`) | En el servidor, fuera de la base | Decide qué tablas y funciones se pueden tocar |
| **Usuario de la aplicación** (fila de `usuarios`) | En la tabla `usuarios` | Es quien hace login en la aplicación: tiene `username`, contraseña y un rol funcional |
| **Rol funcional** (fila de `roles`) | En la tabla `roles` | Agrupa a los usuarios de la aplicación: administrador, trabajador, comercial |

Los tres roles de PostgreSQL son `NOLOGIN`: nadie se conecta con ellos. La
aplicación se conecta con **un solo usuario de PostgreSQL** al que se le
concede uno de los tres roles. **Tener tres roles de PostgreSQL no demuestra
que haya login**: el login es lo del apartado siguiente.

### Quién hace cada operación: el operador de la transacción

El enunciado pide que `log_eventos` guarde el usuario autenticado responsable
de cada cambio. Antes guardaba el usuario **asignado al pedido**, que no tiene
por qué ser quien ejecuta la operación. Ahora son dos datos distintos y los
dos se ven.

Cómo funciona, en tres pasos:

```sql
BEGIN;
SELECT iniciar_sesion('taller.demo', 'la-contrasena');
SELECT realizar_compra('REF-1', 3, 12, 1, 2, 5);
COMMIT;
```

1. `iniciar_sesion` busca el usuario, comprueba la contraseña con bcrypt y,
   **solo si coincide**, guarda su `id_usuario` en un ajuste de la transacción
   (`nova.id_usuario`).
2. Los triggers de auditoría leen ese ajuste con `usuario_sesion()` y lo
   escriben en `log_eventos.id_usuario`.
3. El ajuste se guarda con `set_config(..., true)`, que lo hace **local a la
   transacción**. En cuanto hay COMMIT o ROLLBACK desaparece.

### Un fallo que encontramos y cómo está arreglado

La primera versión de esto guardaba en `nova.id_usuario` solo el número del
usuario. **Y eso era falsificable.** Cualquier rol puede escribir un parámetro
personalizado con `SET` o `set_config`, así que esto funcionaba:

```sql
SET ROLE nova_trabajador;
SELECT set_config('nova.id_usuario', '1', true);
UPDATE pedidos SET estado = 'en_preparacion' WHERE id_pedido = 8;
```

Y en `log_eventos` quedaba el usuario 1, que es `admin.demo`. Un trabajador
firmando la auditoría como administrador, sin saber ninguna contraseña.

Lo primero que probamos fue quitarle el permiso:

```sql
REVOKE SET ON PARAMETER "nova.id_usuario" FROM PUBLIC;
```

**No sirve.** PostgreSQL acepta la orden sin error pero no crea ninguna
entrada en `pg_parameter_acl`, y el rol sigue pudiendo escribir el parámetro.
Los parámetros de categoría `USERSET` son escribibles por cualquiera y eso no
se puede revocar.

**La solución: el valor va firmado.** Ahora `iniciar_sesion` no guarda `3`,
guarda `3:<firma>`, donde la firma es un HMAC-SHA256 del id usando como clave
**el hash bcrypt de la contraseña de ese mismo usuario**. Y `usuario_sesion()`,
que es `SECURITY DEFINER`, recalcula la firma antes de devolver nada; si no
cuadra, devuelve nulo.

Por qué funciona: la clave de la firma es `usuarios.password_hash`, y **ningún
rol de la aplicación puede leer esa columna**. Se consiguió con permisos por
columna:

```sql
GRANT SELECT (id_usuario, username, id_rol, id_personal, activo)
ON public.usuarios TO nova_admin;
```

`nova_admin` ve los usuarios pero no sus hashes, y los otros dos roles no ven
la tabla en absoluto. Sin la clave no se puede fabricar una firma válida. La
prueba `A11b` recorre los tres roles y comprueba que ninguno lee la columna.

Las cuatro pruebas del apartado `FALSIFICACION` lo verifican atacando de
verdad: poner el id a pelo (`F1`), inventarse la firma (`F2`), hacer una
operación con la identidad falsificada (`F3`, y el registro queda **sin
operador**, no con el falso) y reutilizar la firma de otro usuario (`F4`).

Como efecto secundario, `nova_admin` tampoco puede escribir `password_hash`
(prueba `A13c`): las contraseñas solo se ponen por `establecer_password`, que
siempre pasa por bcrypt. Y crear usuarios se hace con `crear_usuario`, que los
deja con `!` hasta que alguien les ponga contraseña.

### Identidad no es permiso

Esto es lo más importante de todo el apartado y conviene decirlo sin rodeos:
**que la auditoría registre bien quién hizo algo no significa que esa persona
estuviera autorizada a hacerlo.** Son dos cosas distintas y se resuelven en
sitios distintos.

Lo que comprobamos atacando la base:

| Operación | ¿Funciona SIN `iniciar_sesion`? | Qué la autoriza entonces |
|---|---|---|
| Crear un pedido | **sí** | el rol de conexión tiene `EXECUTE` |
| Confirmar o cancelar | **sí** | el rol de conexión tiene `UPDATE (estado)` |
| Crear un usuario | **sí** | el rol de conexión es `nova_admin` |
| Cambiar una contraseña | **sí** | el rol de conexión es `nova_admin` |
| Comprar X-NOVA | **sí** | el rol de conexión tiene `EXECUTE` |

Es decir: **la autorización la da el rol de conexión, no el usuario
autenticado.** `iniciar_sesion` sirve para que la auditoría sepa quién fue, no
para abrir ni cerrar puertas. Si no hay sesión, la operación se hace igual y el
registro queda con el operador a nulo, que es lo honesto: la prueba `G6`
comprueba exactamente eso.

**La consecuencia práctica, y es una regla del contrato con Java:** la
aplicación tiene que **conectarse con el rol de PostgreSQL que corresponda al
rol funcional del usuario que ha hecho login**, usando la tabla de arriba. Si
Java se conecta siempre como `nova_admin`, los permisos de la base dejan de
servir para nada y cualquier usuario podría gestionar cuentas llamando a la
función directamente. Con la conexión por rol, un comercial recibe
`permission denied` aunque invoque el DAO a mano, que es lo que pide el
enunciado (prueba `G10`).

### Un usuario desactivado perdía la sesión... y no la perdía

Otro fallo que salió atacando, y que estaba mal. El testigo de sesión se puede
guardar y volver a poner en otra transacción, porque la firma no caduca. Eso en
sí no es escalada: el usuario sigue siendo él mismo. **Pero `usuario_sesion()`
no comprobaba `activo`**, así que un usuario al que acababan de desactivar
podía seguir operando con su testigo anterior y la auditoría lo aceptaba.

Arreglado con una línea: la consulta que busca el hash para verificar la firma
lleva ahora `AND activo = true`. Las pruebas `G1` y `G3` lo comprueban.

Lo que sí funcionaba bien y conviene saber por qué: **cambiar la contraseña
invalida el testigo al instante** (prueba `G2`), porque la clave de la firma es
el propio hash. Al cambiarlo, la firma antigua deja de cuadrar.

Qué garantiza y qué no, dicho claro:

- **No se puede pasar un id de usuario a mano.** Ni directamente ni falsificando
  el parámetro de sesión. Hay que probar la contraseña. Las pruebas `A4` y
  `F1`–`F4` lo comprueban.
- **Ningún rol puede leer `password_hash`**, que es la clave de las firmas. Se
  comprobaron ocho vías: SELECT directo, `SELECT *`, `UPDATE ... RETURNING`,
  filtrado ciego con `WHERE ... LIKE`, `COPY`, las estadísticas de `pg_stats`,
  un agregado `max()`, y lo que devuelven las funciones `SECURITY DEFINER`
  (ninguna devuelve texto). Las ocho denegadas.
- **Nadie puede engañar a las funciones de sesión cambiando el `search_path`.**
  Las funciones llevan el suyo fijado, y además ningún rol puede crear objetos
  en el esquema `public`, así que no se puede colocar un `hmac` o un `crypt`
  falso que las suplante. Prueba `G4`.
- **Ni fijarse el parámetro como valor por defecto**: `ALTER ROLE ... SET
  "nova.id_usuario"` da `permission denied to set parameter`.
- **No se confunde el dueño del pedido con el operador.** `realizar_compra`
  sigue teniendo su `p_id_usuario`, que es el usuario **al que se asigna el
  pedido**, y es un dato de negocio. El operador es otra cosa y va en
  `log_eventos`. La prueba `P11` crea un pedido asignado a `tienda.demo`
  ejecutándolo como `taller.demo`, y comprueba que en el registro consta
  `taller.demo`.
- **Si no se inicia sesión, el registro queda sin operador**, a nulo. No se
  rellena con el dueño del pedido para que no parezca lo que no es. Prueba
  `P11b`.
- **No sobrevive a la transacción**, así que en un pool de conexiones la
  identidad de una petición no se filtra a la siguiente. Prueba `A12`.
- **Lo que esto no resuelve:** cualquiera que tenga las credenciales de
  conexión a PostgreSQL de la aplicación puede abrir una sesión y hacer lo que
  su rol le permita, aunque ya no pueda hacerse pasar por otro usuario. La
  frontera real es que **las credenciales de conexión no pueden estar en manos
  del usuario final**. Eso es responsabilidad del despliegue, y el enunciado lo
  pide por otro lado: "las credenciales se mantendrán fuera del código
  compartido".

Reparto de responsabilidades:

- **PostgreSQL** guarda los usuarios y sus hashes, comprueba la contraseña,
  marca el operador de la transacción, aplica los permisos del rol y escribe
  la auditoría. Nada de esto se puede saltar desde Java.
- **Java** pide usuario y contraseña, llama a `iniciar_sesion` al principio de
  cada transacción, decide qué pantallas muestra según el rol funcional, y
  comprueba que el pedido sobre el que opera es del cliente que ha iniciado
  sesión. Esta última comprobación **no la puede hacer la base**, porque
  `realizar_compra` acepta cualquier `id_cliente`.

## 10. Las ocho consultas

Están en `06_consultas.sql`, en este orden:

1. **Ventas por modelo.** Unidades e importe de cada modelo. Incluye X-NOVA y excluye los pedidos cancelados.
2. **Ranking de clientes.** Número de pedidos e importe acumulado. Excluye cancelados pero sigue mostrando a los clientes que no han comprado nada.
3. **Productos con stock bajo.** SKU con menos de 10 unidades. Es la consulta
   con `HAVING` que pide el enunciado, y su utilidad es de reposición: el
   `HAVING` filtra **después** de agrupar, que es la única forma de preguntar
   "dame las referencias cuya suma de existencias en todos los almacenes es
   menor que X". Con `WHERE` se filtraría almacén por almacén y una referencia
   repartida entre dos naves parecería baja sin serlo. La versión con umbral
   configurable está en `12_consultas_panel.sql` (consulta `C8`).
4. **Pedidos personalizados.** Los que tienen la marca `personalizado`, incluidos los X-NOVA.
5. **Inventario por almacén.** Productos distintos y pares disponibles de cada nave.
6. **Tallas más solicitadas.** Incluye la talla de referencia de los X-NOVA.
7. **Pedidos por mes.** Número de pedidos, importe y cuántos eran personalizados.
8. **Resumen de pagos.** Pedidos, importe y unidades agrupados por estado de pago.

En pgAdmin hay que ejecutarlas **una a una**: si se lanza el fichero entero,
solo se ve el resultado de la última.

Las consultas 1 y 6 usan `LEFT JOIN` en lugar de `JOIN` a propósito. Una línea
X-NOVA no tiene SKU, así que con un JOIN normal desaparecía del informe. Con
`LEFT JOIN` y `COALESCE` aparece: en la consulta 1 como modelo X-NOVA y en la
6 con la talla que guarda su configuración.

Las consultas 1 y 2 excluyen los pedidos cancelados porque son informes de
ventas. La 6 no los excluye, porque mide lo que la gente pide, no lo que se
cobra. La 8 tampoco, porque es un resumen de estados de pago y los cancelados
forman parte de él.

## 11. Pruebas

Hay cuatro archivos de pruebas, y entre los cuatro dan **110 veredictos**:

| Archivo | Qué prueba | Veredictos |
|---|---|---|
| `09_pruebas.sql` | Instalación, compras, confirmaciones, cancelaciones, auditoría, X-NOVA, errores, permisos, autenticación, gestión de usuarios, falsificación de identidad, **autorización**, ciclo de estados y datos mínimos | 91 |
| `10_caso_custom.sql` | El caso del club: 40 pares en cuatro tallas, de principio a fin | 6 |
| `11_dml_ejemplos.sql` | INSERT, UPDATE, DELETE y seis casos rechazados por las restricciones | 12 |
| `12_consultas_panel.sql` | Coherencia de los indicadores del panel | 1 |

`09_pruebas.sql` tiene ahora **91** comprobaciones, no 90: la antigua P2 se
partió en dos, P2 para el catálogo instalado y P2a para los 11 pedidos de
demostración. Con eso son **110** sobre la base recién instalada.

Después, al final de todo, hay once más que comprueban la persistencia y la
exportación del pedido Custom:

| Archivo | Qué prueba | Veredictos |
|---|---|---|
| `14_caso_custom_persistente.sql` | Operador en la sesión, pedido único, confirmado y personalizado, 40 pares, cuatro líneas sin repetir, 10 por talla, stock descontado una vez, sin existencias negativas, los 11 pedidos de demostración intactos y la auditoría con operador | 9 |
| `15_exportar_fabricacion.sql` | El pedido está confirmado con 4 líneas, 4 tallas y 40 pares, y la orden exportada son esas 4 filas | 2 |

En total, **121 comprobaciones** si se ejecuta la secuencia completa en el orden
del apartado 3.

**Las de los scripts 14 y 15 no imprimen `FAIL`: lanzan un error.** Si algo no
cuadra, psql se detiene y devuelve un código de salida distinto de cero, para
que un fallo no pueda pasar por bueno.

**`A1` y `A2` solo pasan antes de ejecutar `13_activar_usuarios.sql`**, porque
comprueban que las cuentas llegan sin contraseña utilizable. Es correcto: son
comprobaciones del estado inicial. Si se vuelve a lanzar `09_pruebas.sql`
después del 13, esas dos darán `FAIL` y las otras 89 seguirán pasando.

Además hay **tres pruebas que necesitan dos sesiones a la vez** y no pueden
estar en un archivo de psql: la de concurrencia y las dos de visibilidad con
COMMIT y ROLLBACK. Están al final de este apartado, con el procedimiento
exacto.

Las 91 pruebas de `09_pruebas.sql` van cada una dentro de su
`BEGIN ... ROLLBACK`, así que al terminar la base queda igual que estaba y no
se pierden los datos de demostración. Lo mismo con los otros tres archivos.

**Cada prueba dice ella misma si ha ido bien.** No hay que interpretar los
resultados a ojo: cada una compara lo que ha pasado con lo que tenía que pasar
y devuelve `PASS` o `FAIL` en la primera columna. Para contar el resultado
basta con buscar cuántos PASS y cuántos FAIL hay en la salida.

Las pruebas que esperan un error usan un bloque `DO` con `EXCEPTION`, que
captura el error y comprueba que el mensaje es exactamente el esperado. Si la
operación prohibida llegara a funcionar, el bloque escribe `FAIL`. Para los
errores de PostgreSQL (clave duplicada, permiso denegado) se compara el código
`SQLSTATE` en vez del texto, porque el texto cambia según el idioma del
servidor.

**Ningún identificador está escrito a mano.** Al principio del archivo se
buscan los ids que existen de verdad y se guardan en variables de psql:

```
SELECT min(id_cliente) AS cliente_a, max(id_cliente) AS cliente_b FROM public.clientes
\gset
```

Después se usan como `:cliente_a`, `:sku`, `:nave`. Un detalle que da
problemas si no se sabe: **psql no sustituye estas variables dentro de un
bloque `$$ ... $$`**, así que los bloques `DO` buscan los ids con subconsultas
en lugar de usar variables.

Para lanzarla desde psql:

```
psql -U postgres -d nova_sneakers -f 09_pruebas.sql
```

### Resultados reales

Ejecutadas el 8 de noviembre de 2026 sobre PostgreSQL 17.11 en instalaciones
limpias desde cero. **110 de 110 dieron PASS**, más las tres pruebas de dos
sesiones, que también pasaron.

Esta tabla recoge las de `09_pruebas.sql`. Los otros tres archivos imprimen
sus veredictos con el mismo formato.

| Prueba | Esperado | Real |
|---|---|---|
| P1 objetos | 14 tablas, 16 FK, 19 funciones, 10 triggers, 4 roles | igual |
| P1b dueño de las funciones | todas las SECURITY DEFINER del dueño de las tablas | 0 excepciones |
| P1c search_path | todas las SECURITY DEFINER lo fijan | 0 excepciones |
| P2 catálogo instalado | 7 modelos, 12 variantes, 60 SKU, 1 nave, 6 clientes, 3 roles, 3 personal, 3 usuarios, 1200 pares de stock | igual |
| P2a pedidos de demostración | 11 pedidos, 14 líneas, 5.890,45 € | igual |
| P2b usuarios en los pedidos | 9 con usuario y 2 sin usuario | 9 y 2 |
| P3 totales calculados | ningún pedido con totales incoherentes | 0 de 11 |
| **P4 crear no mueve stock, confirmar sí** | al crear 1200 y marca false; al confirmar 1198 y marca true | igual |
| **P4b editar y luego confirmar** | tras editar a 8, el stock sigue en 1200; al confirmar baja 8, no 5 | igual |
| **P4c confirmar dos veces** | se descuenta una sola vez | 3 pares |
| P5 pedido de 3 líneas | al crear 1200; al confirmar 1194 y 3 marcas | igual |
| P6 cancelación | stock vuelve a 1200, marca a false, importe conservado | igual |
| P6b cancelar dos veces | el stock no se duplica | sigue en 1200 |
| **P7 nova_admin confirma y cancela** | 1198 al confirmar, 1200 al cancelar | igual |
| **P8 nova_trabajador confirma y cancela** | 1198 al confirmar, 1200 al cancelar | igual |
| **P9 cancelar un pedido sin confirmar** | se cancela y el stock no se mueve | cancelado y 1200 |
| **P9b confirmar sin existencias (prueba B)** | se rechaza entero, sin cambios parciales | stock 1200, 0 marcas, pedido pendiente, mínimo 20 |
| P10 auditoría | 2 eventos de stock y 3 de pedido (alta, confirmación y baja) | 2 y 3 |
| **P11 operador registrado** | consta quien ejecuta, no el dueño del pedido | operador taller.demo, pedido de tienda.demo |
| **P11b sin sesión iniciada** | el registro queda sin operador | nulo |
| **P11c acciones auditadas** | 1 alta, 1 baja lógica y 2 cambios de stock | 1, 1 y 2 |
| **P11d baja lógica de un modelo** | queda registrada | 1 evento BAJA_LOGICA |
| P12 X-NOVA | importe 12.000, sin SKU ni almacén, stock sin tocar | igual |
| P13 cancelar un X-NOVA | el stock no se mueve | 1200 |
| P14 consulta 1 con X-NOVA | X-NOVA aparece y la suma cuadra con las líneas | cuadra |
| E1 cambiar cantidad de un pedido confirmado | error | No se puede modificar una compra registrada |
| E2 cambiar precio de un pedido confirmado | error | No se puede modificar una compra registrada |
| E3 borrar línea ya descontada | error | No se puede eliminar esta linea de pedido |
| E4 apagar la marca de stock | error | Cambio de stock no permitido |
| **E4b encender la marca sin confirmar** | error | Cambio de stock no permitido |
| E5 añadir línea a un pedido confirmado | error | Solo se pueden anadir lineas a un pedido pendiente |
| E6 referencia repetida | error | duplicate key value violates unique constraint |
| E7 reactivar cancelado | error | No se puede reactivar un pedido cancelado |
| E8 cantidad cero | error | La cantidad debe ser mayor que cero |
| E9 añadir línea a cancelado | error | Solo se pueden anadir lineas a un pedido pendiente |
| E10 reusar configuración X-NOVA | error | Configuracion X-NOVA no disponible |
| E11 ROLLBACK tras error | stock intacto y 0 pedidos creados | 1200 y 0 |
| S1 cliente ve catálogo | permitido | 7 modelos |
| S2 cliente ve pedidos | denegado | permission denied for table pedidos |
| S3 cliente compra por función | permitido | pedido creado |
| S4 cliente puede ejecutar descontar_stock | no tiene el permiso | no lo tiene |
| S4b cliente lo intenta de verdad | error | permission denied for function descontar_stock |
| S5 admin inserta línea a mano | denegado | permission denied for table linea_pedido |
| S6 admin ve X-NOVA y auditoría | permitido | correcto |
| S7 trabajador cambia estado | permitido | correcto |
| S8 trabajador cambia importe | denegado | permission denied for table pedidos |
| S9 trabajador compra | denegado | permission denied for function realizar_compra |
| **S10 cliente cancela un pedido** | denegado | permission denied for table pedidos |

La prueba `S4` es la única que comprueba el permiso con
`has_function_privilege` en vez de intentar la operación. El motivo es que
`nova_cliente` no puede leer la tabla `nave`, así que para llamar a
`descontar_stock` habría que pasarle un identificador buscado fuera del
bloque, y psql no sustituye variables dentro de un bloque `$$`. La `S4b` hace
el intento de verdad y deja el error a la vista, pero sin veredicto
automático.

### Autenticación, ciclo de estados y datos mínimos

| Prueba | Esperado | Real |
|---|---|---|
| A1 cuentas sin contraseña | las 3 llegan con `!` | 3 |
| A2 login sin contraseña puesta | error | La cuenta no tiene contrasena establecida |
| A3 login correcto | devuelve el `id_usuario` | correcto |
| A4 contraseña incorrecta | error | Usuario o contrasena incorrectos |
| A5 usuario inexistente | el mismo error, sin dar pistas | Usuario o contrasena incorrectos |
| A6 la contraseña no se guarda en claro | el hash empieza por `$2a$` | `$2a$06$`, 60 caracteres |
| A7 dos usuarios con la misma contraseña | hashes distintos (sal distinta) | 2 hashes distintos |
| A8 contraseña de menos de 8 caracteres | error | La contrasena debe tener al menos 8 caracteres |
| A9 cambiar contraseñas | solo `nova_admin` | admin sí, trabajador y cliente no |
| A10 iniciar sesión | los tres roles | los tres |
| A11 tabla `usuarios` | `nova_admin` ve los usuarios pero no los hashes | correcto |
| **A11b nadie lee `password_hash`** | 0 roles de los 3 | 0 |
| A12 el operador no sobrevive a la transacción | dentro sí, después nulo | correcto |
| **A13 el administrador gestiona usuarios, roles y personal** | puede crear y editar los tres | correcto |
| **A13b crear un usuario** | nace con `!` y activo | correcto |
| **A13c el administrador escribe el hash a mano** | denegado | permission denied for table usuarios |
| **F1 poner el id de sesión a pelo** | no da sesión | nulo |
| **F2 inventarse la firma** | no da sesión | nulo |
| **F3 operar con identidad falsificada** | el registro queda sin operador | nulo, no el id falso |
| **F4 reusar la firma de otro usuario** | no da sesión | nulo |
| **G1 sesión de un usuario desactivado** | deja de valer | nulo |
| **G2 sesión tras cambiar la contraseña** | deja de valer | nulo |
| **G3 login de un usuario desactivado** | error | Usuario o contrasena incorrectos |
| **G4 crear objetos en `public`** | ningún rol puede | 0 de 4 |
| **G5 funciones que devuelven texto** | ninguna | 0 |
| **G6 operar sin login** | funciona, y el registro queda sin operador | pedido creado, operador nulo |
| **G7 vínculo usuarios–clientes** | no existe en el esquema | 0 |
| **G8 correspondencia rol funcional → rol de base** | los 3 | 3 de 3 |
| **G9 perfil de `nova_comercial`** | vende y sigue ventas, no gestiona usuarios | correcto |
| **G10 el comercial crea un usuario** | denegado | permission denied for function crear_usuario |
| **A14 desactivar un usuario** | queda 1 inactivo y los 3 siguen existiendo | correcto |
| **A15 un usuario desactivado no entra** | error | Usuario o contrasena incorrectos |
| B1 estados admitidos | pendiente, confirmado, cancelado y los otros tres | 6 de 6 |
| B2 pendiente → confirmado → cancelado | baja 4 al confirmar, vuelve al cancelar, marcas apagadas | correcto |
| B3 líneas de un pedido confirmado | no se pueden modificar | No se puede modificar una compra registrada |
| M1 datos mínimos | ≥5 clientes, ≥6 modelos, ≥10 pedidos, ≥3 personalizados | 6, 7, 11 y 4 |
| M2 pedido con varias tallas | al menos 1 | 1 (`NOVA-0011`) |
| M4 usuario activo por rol funcional | 3 de 3 | 3 |

### Visibilidad con COMMIT y ROLLBACK, con dos sesiones

También hay que hacerla a mano, con dos ventanas. Sesión A:

```sql
BEGIN;
SELECT realizar_compra('TX-COMMIT',
    (SELECT min(id_cliente) FROM clientes),
    (SELECT min(id_producto_sku) FROM producto_sku),
    (SELECT min(id_nave) FROM nave), 2);
SELECT pg_sleep(6);
COMMIT;
```

Sesión B, mientras A sigue abierta y otra vez después del COMMIT:

```sql
SELECT count(*) AS eventos FROM log_eventos;
SELECT sum(cantidad) AS stock FROM existencias;
SELECT count(*) AS pedidos FROM pedidos WHERE referencia = 'TX-COMMIT';
```

Resultado medido el 8 de noviembre de 2026, en una base recién instalada:

| Momento | Eventos que ve B | Stock que ve B | Pedido que ve B |
|---|---|---|---|
| Antes | 0 | 1200 | 0 |
| **Durante** la transacción de A | **0** | **1200** | **0** |
| Después del COMMIT de A | 1 | 1200 | 1 |

Es decir: el evento de auditoría se crea dentro de la misma transacción que el
cambio de datos, y **la otra sesión no ve ninguno de los dos hasta el COMMIT**.

El stock sigue en 1200 después del COMMIT porque `realizar_compra` deja el
pedido en `pendiente`, y **el stock solo se descuenta al confirmar** (ver el
apartado 7b). Por eso también se crea un solo evento, el del alta, y no dos.

Para el ROLLBACK, la misma sesión A pero cambiando `COMMIT` por `ROLLBACK` y
comprando 3 unidades. A, dentro de su propia transacción, veía **2 eventos y
stock 1200**. B veía 1 evento y 1200 antes, durante y después. Al terminar, el
pedido `TX-ROLLBACK` no existe: cero filas. Los cambios y sus eventos de
auditoría desaparecen juntos.

Una medición anterior de este apartado decía 2 eventos y stock 1198, y 4
eventos y stock 1195. Esas cifras eran de **antes** del rediseño que movió el
descuento de stock de la compra a la confirmación. Las conclusiones no
cambiaron; los números sí.

### Prueba de concurrencia

Esta no está en `09_pruebas.sql` y no puede estarlo: hacen falta **dos
sesiones a la vez**, y un archivo de psql solo abre una. Hay que hacerla a
mano, con dos ventanas.

Preparación, en una sesión cualquiera:

```
UPDATE existencias SET cantidad = 1
WHERE id_producto_sku = (SELECT min(id_producto_sku) FROM producto_sku)
  AND id_nave = (SELECT min(id_nave) FROM nave);
```

Sesión A, que compra la última unidad y se queda esperando:

```
BEGIN;
SELECT realizar_compra('CONC-A',
    (SELECT min(id_cliente) FROM clientes),
    (SELECT min(id_producto_sku) FROM producto_sku),
    (SELECT min(id_nave) FROM nave), 1);
SELECT pg_sleep(6);
COMMIT;
```

Sesión B, lanzada mientras A sigue abierta, intentando comprar la misma
unidad:

```
BEGIN;
SELECT realizar_compra('CONC-B',
    (SELECT min(id_cliente) FROM clientes),
    (SELECT min(id_producto_sku) FROM producto_sku),
    (SELECT min(id_nave) FROM nave), 1);
COMMIT;
```

Resultado medido el 7 de noviembre de 2026: la sesión B **se quedó esperando
5 segundos**, y cuando A confirmó, volvió a comprobar el stock y rechazó la
compra con "Stock insuficiente o producto no encontrado". El stock acabó en 0,
nunca en negativo, y solo se creó un pedido de los dos.

Esto funciona porque `descontar_stock` pone la comprobación dentro del `WHERE`
del `UPDATE` en vez de hacer un `SELECT` antes. PostgreSQL vuelve a evaluar
esa condición después de esperar al otro cliente, así que no se puede vender
la misma unidad dos veces.

## 12. Problemas conocidos

Cosas que funcionan pero no están terminadas, o que conviene saber antes de
tocar la base.

**1. La base no comprueba de quién es el pedido.** `realizar_compra` acepta
cualquier `p_id_cliente` y `anadir_linea_pedido` cualquier `p_id_pedido`, así
que un cliente podría crear un pedido a nombre de otro. **Esa comprobación
tiene que hacerla Java**, no se puede resolver con permisos de PostgreSQL,
porque la aplicación se conecta con un único usuario y dentro de la base no
existe "el cliente que está conectado ahora". Está en el contrato del
apartado 13.

**1b. El operador solo queda registrado si Java llama a `iniciar_sesion`.**
El mecanismo funciona y está probado (apartado 9), pero si la aplicación no lo
usa, `log_eventos.id_usuario` se queda a nulo. No es un fallo de la base: es
un requisito de integración que todavía no se puede dar por cerrado porque no
hay código Java en el repositorio.

**1c. La autorización depende del rol de conexión, no del usuario
autenticado.** Todas las operaciones funcionan sin haber hecho login: lo que
decide si se pueden hacer o no es el rol de PostgreSQL con el que está abierta
la conexión. Las funciones **no** consultan el rol funcional de la tabla
`roles`. Esto es admisible porque el enunciado deja la capa GRANT/REVOKE como
opcional y permite validar en el acceso a datos, pero **obliga a que Java se
conecte con el rol correcto** (ver apartado 13, control 1). Si alguien
simplifica y conecta todo como `nova_admin`, la seguridad de la base se queda
en nada.

Un límite más: el trigger de existencias sí guarda el operador, pero no sabe a
qué pedido corresponde el movimiento, porque trabaja sobre `existencias`. Para
atar un movimiento de stock con su pedido hay que mirar los eventos de la
misma transacción por su `fecha_hora`.

**2. Un pedido cancelado no se puede borrar nunca.** Sus líneas están
protegidas por el trigger, y la clave foránea no deja borrar el pedido
mientras tenga líneas. Es deliberado, porque conserva el histórico, pero
significa que no hay manera de limpiar pedidos de prueba: hay que recrear la
base.

**3. Cancelar no cambia el estado de pago.** Un pedido puede quedar
`cancelado` y `pagado` a la vez. No hay nada que obligue a pasarlo a
`reembolsado`, ni una máquina de estados que impida ir de `entregado` a
`pendiente`. Lo único bloqueado es salir de `cancelado`.

**3b. Un pedido pendiente no reserva stock.** El descuento ocurre al
confirmar, que es lo que pide el enunciado. La consecuencia es que dos clientes
pueden tener a la vez pedidos pendientes por las mismas unidades, y el segundo
que confirme se llevará el error. No es un fallo, es cómo funciona un pedido
que todavía no está confirmado, pero conviene saberlo para explicarlo: quien
quiera reservar, tiene que confirmar.

**4. Borrar una línea X-NOVA deja la configuración inservible.** Si el pedido
todavía está pendiente, la línea se puede borrar, pero
`configuraciones_xnova.id_pedido` se queda apuntando al pedido, y a partir de
ahí la configuración da "no disponible" para siempre.

**5. `modelos.nombre` no tiene UNIQUE** y `realizar_compra_xnova` lo usa para
buscar el precio con `WHERE nombre = 'X-NOVA'`. Si hubiera dos modelos con ese
nombre, cogería uno cualquiera sin avisar.

**6. Los scripts de instalación no se pueden relanzar.** Solo
`02_funciones.sql` y `08_auditoria.sql` son repetibles en sus funciones,
porque usan `CREATE OR REPLACE`, pero sus `CREATE TRIGGER` fallarían. El resto
falla si los objetos ya existen. Para repetir una instalación hay que borrar la
base y crearla otra vez. Los cuatro archivos de pruebas (9 a 12) sí se pueden
repetir todas las veces que se quiera.

**6b. El archivo de pgModeler se ha actualizado a mano y falta abrirlo.**
`acceso-datos/modelo/sneaker-factory.dbm` ya declara las **14 tablas** reales,
las 16 claves ajenas, `configuraciones_xnova` y las tres columnas nuevas de
`linea_pedido`. Se comprobó que el XML está bien formado y que la lista de
tablas y de claves ajenas coincide **exactamente** con la de una base recién
instalada.

Lo que **no** se ha podido comprobar: que pgModeler lo abra sin quejarse,
porque pgModeler no está instalado en el equipo donde se hizo el cambio. Antes
de entregar hay que abrirlo una vez y mirar el diagrama. Si diera problemas,
la alternativa segura es regenerarlo por ingeniería inversa desde una base
recién instalada, que son dos clics, y la versión anterior sigue en el
historial de git.

El `.dbm` describe el modelo de datos, no la instalación completa: no incluye
el esquema `extensiones` ni pgcrypto, que son de `sneaker-factory-esquema.sql`.

Hay además un diagrama entidad-relación en la rama de Álvaro
(`acceso-datos/modelo-er/Modelo-Er-Intermodular.drawio`) que tampoco se ha
comprobado contra el esquema final.

**7. `nave.capacidad` no se comprueba en ningún sitio.** Una devolución de
stock podría dejar el almacén por encima de su capacidad.

**8b. Las ocho consultas no usan el mismo criterio con los pedidos
cancelados.** Las consultas 1 y 2 los excluyen; las 4, 6, 7 y 8 los incluyen.
La 6 ni siquiera hace JOIN con `pedidos`, así que no podría filtrarlos sin
reescribirla. Ninguna da un resultado falso, pero si se compara el total de la
consulta 1 con el de la 7 no cuadran, y hay que saber por qué: la 1 mide
ventas reales y la 7 mide actividad.

**8. El orden de las columnas de `linea_pedido` es distinto** al de una base
donde `id_nave` y `stock_descontado` se añadieron con `ALTER TABLE`. No afecta
a nada porque todas las inserciones nombran sus columnas y ninguna consulta
usa `SELECT *`, pero sí importaría si el código Java leyera por posición.

## 13. Relación con Java/JDBC

Esto es el contrato que la parte Java puede dar por bueno. La aplicación ya
existe: está en `acceso-datos/java` y su README explica cómo se ejecuta. Así
cumple los cuatro controles de más abajo:

1. Se conecta con `java_nova` (script 17), que es `NOINHERIT`: sin rol no lee
   nada. Después del login hace `SET ROLE` al rol que toca.
2. No aplica: la usan empleados que registran pedidos de cualquier cliente.
   Este control es para una aplicación en la que entren los propios clientes.
3. `ConexionBD.empezarTransaccion()` llama a `iniciar_sesion` al principio de
   cada transacción que escribe.
4. No guarda el testigo: lo vuelve a pedir en cada transacción.

**Funciones que debe llamar la aplicación:**

```sql
-- login, devuelve el id_usuario. Primera llamada de cada transaccion
SELECT iniciar_sesion(?, ?);
-- parametros: username, password en claro (viaja por la conexion, no se guarda)

-- crea el pedido en estado pendiente, devuelve su id. NO mueve stock
SELECT realizar_compra(?, ?, ?, ?, ?, ?);
-- parametros: referencia, id_cliente, id_producto_sku, id_nave, cantidad, id_usuario

-- confirmar el pedido: ES AQUI donde PostgreSQL descuenta el stock
UPDATE pedidos SET estado = 'confirmado' WHERE id_pedido = ?;

-- cancelar el pedido: devuelve el stock de las lineas descontadas
UPDATE pedidos SET estado = 'cancelado' WHERE id_pedido = ?;

-- producto adicional en el mismo pedido
SELECT anadir_linea_pedido(?, ?, ?, ?);
-- parametros: id_pedido, id_producto_sku, id_nave, cantidad

-- compra personalizada
SELECT realizar_compra_xnova(?, ?);
-- parametros: referencia, id_configuracion

-- alta o cambio de contrasena, solo para el rol administrador
SELECT establecer_password(?, ?);
-- parametros: username, password nueva (minimo 8 caracteres)
```

**El patrón de cada operación que escribe**, y no es opcional si queremos que
la auditoría tenga sentido:

```java
conexion.setAutoCommit(false);
try (PreparedStatement sesion =
        conexion.prepareStatement("SELECT iniciar_sesion(?, ?)")) {
    sesion.setString(1, username);
    sesion.setString(2, password);
    sesion.executeQuery();
}
// ... aqui las operaciones de la transaccion ...
conexion.commit();
```

`iniciar_sesion` marca el operador **solo para la transacción en curso**. Con
`autoCommit` activado cada sentencia es su propia transacción, así que el
operador se perdería antes de la siguiente llamada y la auditoría quedaría a
nulo. Hay que desactivar `autoCommit` y agrupar.

**Cosas a tener en cuenta:**

- `realizar_compra` acepta un sexto parámetro opcional, `p_id_usuario`. La
  llamada de cinco parámetros sigue funcionando igual: se comprobó
  ejecutándola, y deja el usuario a nulo sin dar ningún error. Cuando se pase
  un usuario, los cambios de estado de ese pedido quedarán registrados con él.
  El valor tiene que ser un `id_usuario` que exista en la tabla `usuarios`, o
  la clave foránea rechazará el pedido.
### Los cuatro controles que Java tiene que implementar

Esto no es una lista de buenas intenciones: son cuatro cosas que la base de
datos **no puede** hacer, comprobadas atacándola. Si Java no las hace, no las
hace nadie.

**1. Conectarse con el rol de PostgreSQL que toque.** Según el rol funcional
del usuario que acaba de hacer login:

| Rol funcional | Rol de conexión |
|---|---|
| `administrador` | `nova_admin` |
| `trabajador` | `nova_trabajador` |
| `comercial` | `nova_comercial` |

Se puede hacer con una cuenta de PostgreSQL por rol, o con una sola cuenta a la
que se le concedan los tres y un `SET ROLE` nada más iniciar sesión. **Lo que no
vale es conectarse siempre como `nova_admin`**: eso anula toda la capa de
permisos de la base y cualquier usuario podría gestionar cuentas llamando al
DAO directamente.

**2. Comprobar de quién es el pedido.** La base no lo puede hacer, y no es
pereza: **no existe ninguna clave ajena entre `usuarios` y `clientes`** (prueba
`G7`). Los usuarios de la aplicación son empleados, y los clientes son otra
cosa. Así que dentro de la base no hay forma de preguntar "¿este pedido es del
cliente que ha iniciado sesión?". `realizar_compra` acepta cualquier
`id_cliente` y `anadir_linea_pedido` cualquier `id_pedido`; está comprobado que
se puede crear un pedido a nombre de otro cliente y añadir líneas a un pedido
ajeno. Esa validación va en Java, antes de llamar.

**3. Llamar a `iniciar_sesion` al principio de cada transacción que escriba.**
Si no, la operación se hace igual pero la auditoría queda sin operador (prueba
`G6`). No es un fallo de la base: es que la identidad la aporta la aplicación.

**4. No guardar el testigo de sesión entre peticiones.** El valor de
`nova.id_usuario` es local a la transacción y hay que regenerarlo con
`iniciar_sesion` en cada una. Guardarlo y reinyectarlo funciona mientras el
usuario siga activo y no cambie su contraseña, pero es una mala práctica: deja
de reflejar el estado real de la cuenta hasta la siguiente transacción.
- Si se vuelve a instalar la base sobre una que ya existía, hay que ejecutar
  `07_seguridad.sql` **después** de `02_funciones.sql`. El `DROP FUNCTION IF
  EXISTS` del principio de `02_funciones.sql` borra la versión antigua de
  `realizar_compra` y con ella sus permisos.
- **Leer siempre las columnas por nombre**, no por posición (ver problema 8).
- Todos los errores de negocio llegan como `PSQLException` con el SQLSTATE
  `P0001`, que es el genérico de `RAISE EXCEPTION`. Eso significa que Java no
  puede distinguir "stock insuficiente" de "producto no disponible" si no es
  leyendo el texto del mensaje. Se podría mejorar dando un código distinto a
  cada error, pero no se ha hecho todavía.
- La aplicación debe conectarse con un usuario al que se le haya concedido uno
  de los tres roles. Con el nivel de aislamiento por defecto (READ COMMITTED)
  el control de stock funciona bien. Si se subiera el nivel, las compras
  simultáneas empezarían a dar errores de serialización y Java tendría que
  reintentarlas.
- No hay que insertar en `linea_pedido` directamente: los roles no tienen
  permiso, y además se saltaría el descuento de stock.
- **Nada de tocar a mano `existencias.cantidad`, `pedidos.importe_total`,
  `pedidos.cantidad_total` ni `log_eventos`.** Los calculan los triggers. Los
  permisos ya lo impiden para `nova_cliente` y `nova_trabajador`; para
  `nova_admin` es una norma del contrato, porque sí tiene permiso sobre
  `pedidos` y `existencias` para los ajustes de inventario.
- **Todas las consultas con `PreparedStatement` y `?`**, nunca concatenando
  texto. Las consultas de `12_consultas_panel.sql` están escritas con
  variables de psql justamente para que se vea dónde va cada `?`.
- Los filtros combinables se escriben con el patrón
  `(? = '' OR columna = ?)`, de forma que un filtro vacío no excluya filas.
  Está probado en las consultas `C5` y `C6` de ese archivo.
- Las consultas que puede lanzar cada rol dependen de sus permisos de SELECT:
  `nova_cliente` no puede leer `pedidos`, así que el panel de indicadores solo
  funciona para `nova_trabajador` y `nova_admin`.

## 14. Estado

La instalación desde cero, las funciones, los triggers, el control de stock,
las cancelaciones con cada rol, X-NOVA, los permisos, la auditoría y las ocho
consultas están probados sobre PostgreSQL 17.11 con los resultados del
apartado 11.

### Exportación CSV para PSP: la orden de fabricación del pedido Custom

#### Qué es el pedido Custom

Es el caso del enunciado: el Club Atlético NOVA encarga **40 pares** del modelo
NOVA Velocity en color rojo, repartidos en cuatro tallas —10 pares de la 40, 10
de la 41, 10 de la 42 y 10 de la 43—, con una personalización: logo bordado y
numeración en el talón. Su referencia es `CUSTOM-40`.

#### Cómo se guarda en PostgreSQL

No hay ninguna tabla especial para los pedidos personalizados. Se usan las
mismas que para cualquier otro pedido:

- En `pedidos` va una fila con la referencia `CUSTOM-40`, el cliente, el
  operador que lo atiende, el estado, `personalizado = true` y el texto de
  `personalizacion`.
- En `linea_pedido` van **cuatro filas**, una por talla, cada una con su
  `id_producto_sku`, su cantidad de 10 y su precio.
- Los triggers calculan el subtotal de cada línea y los totales del pedido, y
  al confirmarlo descuentan el stock de cada una de las cuatro referencias.

Hay dos archivos y hacen cosas distintas, a propósito:

- `10_caso_custom.sql` **prueba** el caso completo —crear, confirmar, auditar,
  cancelar y devolver el stock— dentro de `BEGIN ... ROLLBACK`. Al terminar no
  queda nada en la base: eso es lo que se quiere de una prueba. Usa la
  referencia `CUSTOM-40-TEST` para no chocar con el pedido de verdad.
- `14_caso_custom_persistente.sql` **guarda** el pedido `CUSTOM-40` con un
  `COMMIT`, para que exista de verdad. Se puede lanzar las veces que se quiera:
  si ya está, lo comprueba y no toca nada, así que no duplica el pedido, ni las
  líneas, ni vuelve a descontar stock. No borra ni modifica ningún otro pedido.

#### Cómo se genera `fabricacion_psp.csv`

Lo hace `15_exportar_fabricacion.sql`, y **lee el pedido guardado en la base**,
no datos de una transacción que luego desaparece. Antes de escribir nada
comprueba tres cosas: que `CUSTOM-40` existe, que suma exactamente 40 pares y
que tiene cuatro tallas distintas. Si alguna falla, psql se detiene con un
código de error y **el CSV anterior se queda intacto**, porque no llega a
abrirlo.

El archivo se llama siempre `fabricacion_psp.csv` y se deja **en el directorio
desde el que se lanza psql**. Conviene lanzarlo desde una carpeta de salidas,
para no dejar archivos generados en la raíz del repositorio:

```
mkdir salidas
cd salidas
psql -U postgres -d nova_sneakers -f ..\acceso-datos\sql\15_exportar_fabricacion.sql
```

#### Por qué el nombre del archivo es fijo

Porque la alternativa estropea los datos en Windows, y se midió byte a byte.

La exportación usa `\copy`. Su argumento se toma literalmente, así que **no
admite variables** y el nombre no se puede configurar. Hubo una versión que
usaba `\o` con `COPY ... TO STDOUT` para poder pasar la ruta por `-v`, y esa
versión **alteraba el contenido**: psql escribe su salida en modo texto en
Windows y convierte cada `\n` en `\r\n`, también los que forman parte de un
campo.

Con una personalización de dos líneas, medido en hexadecimal:

| Vía | Lo que escribe | |
|---|---|---|
| en la base | `linea1` `0a` `linea2` | original |
| `\o` + `COPY TO STDOUT` | `linea1` `0d 0a` `linea2` | **alterado** |
| redirección del shell | `linea1` `0d 0a` `linea2` | **alterado** |
| `psql -o archivo` | `linea1` `0d 0a` `linea2` | **alterado** |
| `\copy` | `linea1` `0a` `linea2` | correcto |
| `COPY` del servidor | `linea1` `0a` `linea2` | correcto |

Y si el campo ya tenía `\r\n`, con `\o` salía `\r\r\n`. PostgreSQL y `COPY`
están bien; el que altera los bytes es **psql al escribir el archivo**.

De las dos vías correctas se eligió `\copy` porque el `COPY` del servidor
necesita **superusuario** y escribe en la máquina del servidor. `\copy` funciona
con los permisos normales y escribe donde está el cliente.

Comprobado que el carácter sobrevive al viaje completo: se guardó una
personalización con un salto de línea, se exportó y PSP la leyó. El hexadecimal
recuperado es idéntico al de la base, con LF y con CRLF.

#### Limitación conocida de la exportación

La exportación escribe directamente en `fabricacion_psp.csv`. Las validaciones
del pedido se ejecutan antes de abrirlo, así que un pedido inexistente,
cancelado o con cantidades incorrectas no modifica un CSV anterior. Sin
embargo, si `psql` se cierra o la conexión se interrumpe cuando `\copy` ya está
escribiendo, el archivo puede quedar incompleto. Para el alcance académico de
este proyecto se acepta esta limitación: se vuelve a ejecutar el script y solo
se procesa el CSV cuando `psql` termina correctamente.

#### Qué información recibe PSP

Ocho columnas, todas con datos reales de PostgreSQL, y **solo las cuatro filas
de `CUSTOM-40`**. No se mezcla con `NOVA-0011` ni con ningún otro pedido
personalizado: cada orden de fabricación es de un pedido.

| Columna | De dónde sale | Para qué |
|---|---|---|
| `referencia` | `pedidos.referencia` | identificar el pedido |
| `sku` | `producto_sku.sku` | la referencia exacta de inventario |
| `cliente` | `clientes.nombre` | para quién se fabrica |
| `modelo` | `modelos.nombre` | qué zapatilla |
| `color` | `variantes.color` | en qué color |
| `personalizacion` | `pedidos.personalizacion` | qué hay que personalizar |
| `talla` | `producto_sku.talla` | qué talla |
| `cantidad` | `linea_pedido.cantidad` | cuántos pares de esa talla |

Cabecera, codificación UTF-8, separador coma y orden estable por talla. Los
precios no van aquí: la fabricación no los necesita y su sitio es
`lineas_pedido.csv`, cuando se acuerde su formato.

Comprobado con tres ejecuciones seguidas: los tres archivos salen idénticos
byte a byte.

#### Qué identificadores deben compartir PostgreSQL, Odoo y PSP

El contrato (`integracion/contrato-pedido.md`) dice que los CSV tienen que
llevar **los mismos identificadores que la base**, para poder relacionarlos.
De los que PostgreSQL ya tiene y puede exportar hoy:

- `pedidos.id_pedido` y `pedidos.referencia`
- `clientes.id_cliente`
- `linea_pedido.id_linea`
- `modelos.id_modelo`, `variantes.id_variante` y `producto_sku.sku`
- `producto_sku.talla` y `linea_pedido.cantidad`

Este CSV lleva `referencia`, `sku` y `talla`, que son los tres que identifican
sin ambigüedad qué hay que fabricar. Los numéricos internos (`id_pedido`,
`id_linea`, `id_cliente`, `id_modelo`) existen y se pueden añadir en cuanto se
sepa si los otros módulos los van a usar.

#### Qué integración es real y cuál está pendiente

**Real y comprobado:** la base guarda el pedido Custom con sus cuatro tallas y
su personalización, y PostgreSQL lo exporta a CSV de forma repetible, validada
y con los identificadores que son nuestros.

**Pendiente, y no depende de Acceso a Datos:** el apartado 8 del contrato sigue
sin acordar los nombres definitivos de entidades y columnas, cómo se
representan las variantes personalizadas, los estados definitivos de pedido y
pago, las entregas parciales, **qué columnas llevan los cinco CSV**
(`clientes.csv`, `modelos.csv`, `pedidos.csv`, `lineas_pedido.csv` y
`stock.csv`) y el diccionario de datos. Mientras PSP no diga qué identificador
usa, esta exportación lleva los nuestros y **no se ha inventado ninguna
correspondencia**.

**De Odoo no se afirma nada.** El contrato no lo menciona: habla de Python. No
hay ningún identificador de Odoo acordado ni comprobado.

**Este CSV no es ninguno de los cinco del contrato.** Es la orden de
fabricación de un pedido concreto y se mantiene aparte, hasta que se acuerde el
formato definitivo de los cinco.

### Exportación de los cinco CSV del contrato (dashboard)

`16_exportar_csv_dashboard.sql` genera los cinco archivos del apartado 7 del
contrato, que son los que pide el enunciado de Ampliación de Python para su
dashboard: `clientes.csv`, `modelos.csv`, `pedidos.csv`, `lineas_pedido.csv` y
`stock.csv`. Solo lee; no cambia ninguna tabla.

```
mkdir salidas
cd salidas
psql -U postgres -d nova_sneakers -f ..\acceso-datos\sql\16_exportar_csv_dashboard.sql
```

**Es una propuesta de Acceso a Datos.** El contrato deja las columnas sin
cerrar (apartado 8). Aquí se usan sus nombres (`id_pedido`, `fecha_pedido`,
`tipo_pedido`, `estado_pedido`, `importe_linea`…) más los campos mínimos que
pide Python (`id_modelo` en las líneas, `stock_disponible` y `fecha_corte` en el
stock). El equipo tiene que aprobarla.

#### Cómo funciona

- Una **vista temporal por archivo** (`csv_clientes`, `csv_pedidos`…): cada
  vista es la consulta exacta de su CSV y desaparece al cerrar psql.
- Todo va en una transacción **`REPEATABLE READ`**: los cinco archivos son la
  misma foto de la base, aunque otra conexión esté creando pedidos a la vez.
- **Antes de abrir ningún archivo** comprueba que el total de cada pedido es
  la suma de sus líneas y que todas las líneas tienen modelo y talla. Si algo
  falla, o el rol no puede leer alguna tabla, psql se detiene y los CSV
  anteriores no se tocan.
- Al final enseña el pedido `CUSTOM-40` reconstruido uniendo las cinco vistas,
  igual que tendrá que hacerlo el dashboard.

Si `psql` termina con error, no se copian los archivos al dashboard: se
corrige y se vuelve a lanzar. Si se cortara a mitad de los `\copy`, algunos
archivos serían nuevos y otros viejos (la misma limitación que el 15).

#### Formato

UTF-8, separador coma, primera fila con los nombres de columna, punto decimal
(`119.90`) y sin símbolo de moneda (todo en euros). Fechas `AAAA-MM-DD HH:MM:SS`.
Los campos lógicos salen como `true` / `false`, y un campo vacío es un valor nulo.
Un texto con comas, comillas o saltos de línea va entre comillas dobles (CSV
estándar). Las filas salen siempre en el mismo orden, así que dos exportaciones
de los mismos datos dan archivos idénticos, salvo `fecha_corte`.

#### Diccionario de datos

| Archivo | Columna | Origen | Significado y valores |
|---|---|---|---|
| clientes | `id_cliente` | `clientes.id_cliente` | Clave. Es un identificador, no una cantidad |
| clientes | `nombre` | `clientes.nombre` | Nombre del cliente o del club |
| clientes | `tipo` | `clientes.tipo` | `particular` o `empresa` |
| clientes | `correo` | `clientes.email` | Correo ficticio (`@example.com`) |
| clientes | `telefono` | `clientes.telefono` | Puede estar vacío |
| clientes | `activo` | `clientes.activo` | `true` / `false` |
| modelos | `id_modelo` | `modelos.id_modelo` | Clave |
| modelos | `nombre_modelo` | `modelos.nombre` | Único |
| modelos | `descripcion` | `modelos.descripcion` | Puede estar vacía |
| modelos | `precio_base` | `modelos.precio_base` | Euros, precio de catálogo |
| modelos | `activo` | `modelos.activo` | `true` / `false` |
| pedidos | `id_pedido` | `pedidos.id_pedido` | Clave |
| pedidos | `referencia` | `pedidos.referencia` | Única. Es la que se ve en pantalla (`CUSTOM-40`) |
| pedidos | `id_cliente` | `pedidos.id_cliente` | Une con `clientes.csv` |
| pedidos | `fecha_pedido` | `pedidos.fecha_pedido` | Fecha y hora de alta |
| pedidos | `tipo_pedido` | `pedidos.personalizado` | `normal` o `custom` |
| pedidos | `estado_pedido` | `pedidos.estado` | `pendiente`, `confirmado`, `en_preparacion`, `enviado`, `entregado`, `cancelado` |
| pedidos | `estado_pago` | `pedidos.estado_pago` | `pendiente`, `pagado`, `reembolsado` |
| pedidos | `personalizacion` | `pedidos.personalizacion` | Texto libre. Vacío si el pedido es `normal` |
| pedidos | `cantidad_total` | `pedidos.cantidad_total` | Pares. Lo calcula el trigger: suma de sus líneas |
| pedidos | `importe_total` | `pedidos.importe_total` | Euros. Lo calcula el trigger: suma de sus líneas |
| lineas_pedido | `id_linea` | `linea_pedido.id_linea` | Clave |
| lineas_pedido | `id_pedido` | `linea_pedido.id_pedido` | Une con `pedidos.csv` |
| lineas_pedido | `sku` | `producto_sku.sku` | Une con `stock.csv`. Vacío en una línea X-NOVA |
| lineas_pedido | `id_modelo` | `variantes.id_modelo` | Une con `modelos.csv`. En X-NOVA, el modelo X-NOVA |
| lineas_pedido | `talla` | `producto_sku.talla` | Entre 20 y 55. En X-NOVA, la talla de la configuración |
| lineas_pedido | `cantidad` | `linea_pedido.cantidad` | Pares, mayor que 0 |
| lineas_pedido | `precio_unitario` | `linea_pedido.precio_unitario` | Euros por par en el momento del pedido |
| lineas_pedido | `importe_linea` | `linea_pedido.subtotal` | Euros, cantidad × precio_unitario |
| stock | `sku` | `producto_sku.sku` | Clave: una fila por SKU |
| stock | `id_modelo` | `variantes.id_modelo` | Une con `modelos.csv` |
| stock | `color` | `variantes.color` | Color de la variante |
| stock | `talla` | `producto_sku.talla` | Talla del SKU |
| stock | `activo` | `producto_sku.activo` | `true` / `false` |
| stock | `stock_disponible` | `SUM(existencias.cantidad)` | Pares, suma de todas las naves. 0 si no hay existencias |
| stock | `fecha_corte` | `now()` | Momento de la exportación. Es una foto, no un histórico |

**Ventas.** El panel de Acceso a Datos (`P-A`) cuenta como venta todo pedido
que no esté `cancelado`. El CSV trae todos los pedidos con su estado; quien lo
lea decide qué estados cuenta, y tiene que decirlo.

**Un pedido con varias líneas es un solo pedido.** Para contar pedidos se
cuenta en `pedidos.csv`, nunca en `lineas_pedido.csv`.

**Lo que no se exporta, y por qué:** `direccion_entrega` (dato personal que no
hace falta para analizar y además está vacío en todos los clientes), la nave
(solo hay una, `NOVA Central`), el suplemento de precio por color (es 0 en
todas las variantes) y la categoría del modelo (no existe en el esquema).

#### Comprobado

Sobre una base reconstruida desde cero con los scripts 1–16:

- Las tres cifras del panel cuadran con lo que sale de los CSV: `P-A` (12
  pedidos no cancelados, 90 pares, 10.686,45 €), `P-B` (11 pendientes y 1
  confirmado) y `P-C` (pares por modelo).
- `CUSTOM-40` se reconstruye solo con los CSV: Club Atletico NOVA, NOVA
  Velocity rojo, 10 pares de cada talla de la 40 a la 43, a 119,90 €, total
  4.796,00 €, `confirmado`, `custom`. Las líneas suman exactamente el total del
  pedido, y el stock de esas cuatro tallas baja de 20 a 10.
- Lanzado dos veces seguidas, los archivos salen idénticos (salvo `fecha_corte`).
- Funciona con `nova_admin`, `nova_trabajador` y `nova_comercial`. Con
  `nova_cliente` se detiene por permisos y no toca los CSV que ya había.
- Con un pedido descuadrado a propósito (en una base de pruebas) se detiene
  antes de escribir y los CSV anteriores no cambian.
- Una personalización con coma, comillas, salto de línea y tilde se lee de
  vuelta igual. Una línea X-NOVA sale con el modelo X-NOVA y la talla de su
  configuración.

### Última corrección (7 de noviembre de 2026)

Tres cambios, los tres salidos de una auditoría que encontró un fallo que
bloqueaba la entrega:

1. **`devolver_stock_cancelacion` pasa a `SECURITY DEFINER`** con su
   `search_path` fijado. Antes **ningún rol podía cancelar un pedido**: el
   `SELECT ... FOR UPDATE` de la función exige permiso de UPDATE sobre
   `linea_pedido`, que no tiene nadie a propósito. Explicado en el apartado 9.
2. **Tres usuarios ficticios** en `05_datos_prueba.sql`, con sus roles y su
   personal. Sin ellos la columna `log_eventos.id_usuario` no podía rellenarse
   nunca, porque tiene clave foránea y la tabla `usuarios` estaba vacía.
   Explicado en el apartado 4.
3. **`09_pruebas.sql` pasa de 29 a 40 pruebas**, cada una con su propio
   veredicto PASS o FAIL, sin ningún identificador escrito a mano, y con las
   tres cancelaciones por rol que antes no se probaban (`P7`, `P8`, `P9`) más
   `P11`, `P11b` y `S10`.

Por qué la batería anterior no detectó el fallo: la prueba de permisos del
trabajador cambiaba el estado a `en_preparacion`, nunca a `cancelado`, y la
prueba de cancelación se ejecutaba como propietario de la base. Las dos
pasaban sin tocar el camino que fallaba.

### Revisión contra el enunciado (7 de noviembre de 2026)

Se revisó el proyecto contra los requisitos del enunciado de Acceso a Datos y
se cerraron los que dependían solo de PostgreSQL:

1. **Identidad del operador en la auditoría.** `iniciar_sesion` con bcrypt,
   `usuario_sesion()` local a la transacción, y los triggers escribiendo el
   operador. Apartado 9.
2. **Cobertura de la auditoría.** Antes solo registraba cambios de estado y de
   stock. Ahora también el **alta** de pedidos y las **bajas lógicas** de
   pedidos, modelos y SKU. 9 triggers en total.
3. **Contraseñas.** La tabla `usuarios` ya no lleva ningún valor de relleno:
   las cuentas llegan con `!`, que no puede funcionar como hash, y
   `establecer_password` genera hashes bcrypt con sal. En el repositorio no hay
   ninguna contraseña.
4. **Estado `confirmado`.** Añadido al CHECK para poder representar el ciclo
   del enunciado. Ver el problema 3b para la diferencia con el momento del
   descuento de stock.
5. **Datos mínimos.** Sexto cliente (un club), undécimo pedido con **40 pares
   en cuatro tallas distintas**, que es lo que faltaba de verdad: antes todos
   los pedidos de demostración tenían una sola línea.
6. **Caso Custom del enunciado** (`10_caso_custom.sql`), con la exportación CSV
   para PSP.
7. **Ejemplos DML** (`11_dml_ejemplos.sql`) y **consultas del panel**
   (`12_consultas_panel.sql`), que cubren las búsquedas por cliente, modelo,
   estado y periodo, los filtros combinables y el umbral de stock
   configurable, que las ocho consultas originales no cubrían.
8. **Transacciones.** Las pruebas de visibilidad con COMMIT y ROLLBACK entre
   dos sesiones, en el apartado 11.

### Revisión contra el enunciado oficial (7 de noviembre de 2026, segunda vuelta)

Con el PDF del enunciado delante se encontró un incumplimiento que la revisión
anterior no podía ver, y se corrigió:

**El stock pasa a moverse al confirmar, no al crear la línea.** El apartado 3.6
del enunciado dice literalmente *"mantener el stock disponible cuando se
confirme o cancele un pedido. No descontar stock en cada edición de una línea y
otra vez al confirmar"*. El diseño anterior descontaba al crear la línea, que
es exactamente lo que el enunciado descarta. El cambio, explicado en el
apartado 7b:

- `anadir_linea_pedido` ya no llama a `descontar_stock`.
- Nuevo trigger `trg_descontar_stock_confirmacion` sobre `pedidos`.
- `proteger_linea_pedido` admite ahora la transición de la marca de false a
  true cuando el pedido está confirmado, y sigue prohibiendo todo lo demás.
- Las líneas de los pedidos de demostración llevan ya su almacén, para que se
  puedan confirmar.

Se volvieron a ejecutar las tres pruebas de dos sesiones con el diseño nuevo, y
las tres siguen pasando: la concurrencia ahora compite en la confirmación, y el
perdedor se queda en `pendiente` sin stock negativo.

**También se actualizó el `.dbm` de pgModeler** a las 14 tablas reales (ver el
problema 6b, que explica qué falta comprobar).

Lo que queda pendiente son los puntos del apartado 12 y, sobre todo, **toda la
parte de Java/JDBC**: a 7 de noviembre de 2026 no hay ni un archivo `.java` en
ninguna rama del repositorio, así que el login, el panel, los filtros, el TXT
de actividad, el JSON de usuarios y las pruebas de extremo a extremo siguen sin
empezar. La base de datos ya tiene preparado todo lo que esa parte necesita.

### Parte Java (9 de noviembre de 2026)

La aplicación Swing + JDBC ya está en `acceso-datos/java`: login, pedidos,
consultas con filtros, indicadores, usuarios, TXT, JSON y CSV. Las pruebas
A–J se lanzan con `pruebas.bat`, y sobre una base reconstruida desde cero con
los scripts 1–17 dieron 47 PASS y 0 FAIL. El detalle está en su README.
