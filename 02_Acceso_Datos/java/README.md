# NOVA Sneakers — Aplicación Java (Acceso a Datos)

Aplicación Swing que se conecta a PostgreSQL por JDBC: inicio de sesión,
pedidos, consultas con filtros, indicadores, usuarios y los tres archivos
externos (TXT, JSON y CSV).

Java **no calcula importes, ni toca el stock, ni escribe la auditoría**. Lo
hacen los triggers de PostgreSQL (ver `../documentacion/README.md`). Java llama
a las funciones de la base, cambia el estado de los pedidos y enseña los
resultados.

## Requisitos

- JDK 17 (`javac` y `java` en el PATH).
- La base `nova_sneakers` instalada con los scripts de `../sql` y las
  contraseñas de demostración puestas con `13_activar_usuarios.sql`.
- Descargar el driver JDBC de PostgreSQL 42.7.14 y guardarlo como
  `lib/postgresql-42.7.14.jar`. El binario es una dependencia local y no se
  guarda en Git. No hace falta ninguna otra librería.

## Puesta en marcha

1. Crear el usuario de conexión, una sola vez:

   ```
   psql -U postgres -d nova_sneakers -f ..\sql\17_usuario_java.sql
   ```

   Pide una contraseña para `java_nova`.

2. Copiar `conexion.properties.ejemplo` como `conexion.properties` y escribir
   esa contraseña. Este archivo está en el `.gitignore`: la contraseña no se
   sube al repositorio.

3. Arrancar la aplicación con `ejecutar.bat`, que compila y abre la ventana de
   login. Para lanzar las pruebas, `pruebas.bat`.

Si `javac` no está en el PATH:
`set PATH=C:\Program Files\Java\jdk-17.0.12\bin;%PATH%`

## Usuarios y roles

| Usuario | Rol de la aplicación | Rol de PostgreSQL |
|---|---|---|
| `admin.demo` | administrador | `nova_admin` |
| `tienda.demo` | comercial | `nova_comercial` |
| `taller.demo` | trabajador (almacén y taller) | `nova_trabajador` |

Matriz de permisos (está también en `Sesion.java`):

| Operación | administrador | comercial | trabajador |
|---|---|---|---|
| Crear pedidos | sí | sí | no |
| Consultar pedidos y su detalle | sí | sí | sí |
| Confirmar o cancelar pedidos | sí | sí | sí |
| Indicadores y stock bajo | sí | sí | sí |
| Ver la auditoría (`log_eventos`) | sí | no | no |
| Gestionar usuarios y exportar el JSON | sí | no | no |

Por qué así: el comercial vende y sigue sus pedidos, pero no gestiona
cuentas. El trabajador prepara pedidos y controla el almacén, así que
confirma y cancela, pero no vende. Solo el administrador ve quién hizo cada
cambio y gestiona usuarios.

### Dos barreras

1. **Java**: cada método de los DAO empieza con
   `Sesion.comprobarPermiso(...)`, y la ventana solo enseña las pestañas que
   el rol puede usar.
2. **PostgreSQL**: Java se conecta con `java_nova`, que es `NOINHERIT` y por
   sí solo no puede leer ni una tabla. Al iniciar sesión hace `SET ROLE` al
   rol de la base que corresponde. Si alguien se saltara la comprobación de
   Java, la base rechazaría la operación igual (pruebas F3, P2 y P4).

### Contraseñas

Las guarda PostgreSQL con bcrypt (`crypt` y `gen_salt('bf')`). Java envía
usuario y contraseña a `iniciar_sesion` y la base contesta si es correcta.
Java nunca ve un hash.

### Quién firma la auditoría

Cada operación que escribe empieza con `SELECT iniciar_sesion(?, ?)` dentro
de la transacción (`ConexionBD.empezarTransaccion`). Así los triggers saben
qué usuario la hace y lo guardan en `log_eventos.id_usuario`. Por eso la
contraseña se queda en memoria mientras dura la sesión: no se escribe en
ningún sitio.

## Qué hace cada clase

| Clase | Para qué |
|---|---|
| `ConexionBD` | Abre la conexión con `conexion.properties`, `SET ROLE`, transacciones (`empezarTransaccion`, `hacerCommit`, `hacerRollback`) y mensajes de error legibles |
| `Sesion` | Quién ha entrado, su rol y la matriz de permisos |
| `UsuarioDAO` | Login, logout, usuarios (crear, cambiar rol, activar/desactivar) y exportación a JSON |
| `PedidoDAO` | Crear, confirmar y cancelar pedidos, buscar con filtros, detalle y auditoría |
| `IndicadoresDAO` | Las consultas del panel, con COUNT, SUM y GROUP BY |
| `Archivos` | `actividad_sneaker.txt`, el CSV de la tabla y `usuarios_sneaker.json` |
| `Opcion` | Un elemento de un JComboBox: id y texto |
| `VentanaLogin` | La ventana de entrada, con el `main` |
| `VentanaPrincipal` | Las pestañas según el rol |
| `PanelNuevoPedido` | Cliente, modelo, talla y cantidad, con varias líneas |
| `PanelConsultas` | Filtros, JTable, detalle, confirmar, cancelar, CSV y auditoría |
| `PanelIndicadores` | Las tablas de indicadores y el umbral de stock |
| `PanelUsuarios` | Gestión de usuarios (solo administrador) |
| `PruebasRubrica` | Las pruebas L, A–J y P, sin ventanas |

## Cómo funciona un pedido

1. **Crear** (`PedidoDAO.crearPedido`), todo en una transacción:
   `iniciar_sesion` → `realizar_compra` para la primera línea →
   `anadir_linea_pedido` para las demás → si es Custom, un `UPDATE` de
   `personalizado` y `personalizacion` → `COMMIT`. Los triggers calculan
   subtotales y total. El stock no se toca todavía.
2. **Confirmar**: `UPDATE pedidos SET estado = 'confirmado'`. El trigger
   descuenta el stock de cada línea. Si no hay bastante, PostgreSQL lanza
   "Stock insuficiente" y se deshace todo.
3. **Cancelar**: `UPDATE pedidos SET estado = 'cancelado'`. El trigger devuelve
   el stock que se había descontado.

Si algo falla, `hacerRollback()` deshace la transacción entera: no quedan
pedidos a medias ni entradas de auditoría de cambios que no existen.

## Consultas con filtros

Cliente, modelo, estado y fechas desde/hasta, combinables. El SQL se monta
añadiendo un trozo de `WHERE` por cada filtro que se usa, y su valor va en un
`ArrayList` de parámetros que se pasa con `?`. Nunca se pega texto del
usuario en el SQL. Sin filtros salen todos los pedidos; «Limpiar filtros» los
vacía y vuelve a buscar. La tabla se vacía antes de cada búsqueda, para que un
error no deje a la vista datos viejos.

El botón «Ver auditoría» se deja visible para todos a propósito: así se puede
enseñar en la defensa que el comercial y el trabajador reciben «Acceso
denegado» (prueba F).

## Archivos externos

Se guardan en la carpeta `carpeta_salida` (por defecto `salidas/`, que está en
el `.gitignore`).

- **`actividad_sneaker.txt`**: una línea por acción, con `FileWriter` en modo
  append (`true`). Formato:
  `fecha | usuario | rol | acción | resultado | detalle`. El resultado es
  `correcto`, `rechazado` (permiso, regla de negocio o restricción) o `error`.
  Solo se escribe `correcto` después del `COMMIT`. Nunca lleva contraseñas ni
  SQL. Los filtros se apuntan por id, no por nombre.
- **`usuarios_sneaker.json`**: lista de objetos `id_usuario`, `username`, `rol`
  y `activo`, sin contraseñas ni hashes. Se regenera sola después de cada
  cambio confirmado de un usuario, y también con el botón. Primero se escribe
  un archivo temporal, después se cambia por el definitivo y se vuelve a leer
  para comprobar que está entero.
- **`consulta_pedidos.csv`**: lo que hay en la JTable en ese momento, con la
  misma cabecera, las mismas filas y en UTF-8.

**`log_eventos` y el TXT no tienen los mismos eventos.** `log_eventos` es de
PostgreSQL y depende de la transacción: si hay ROLLBACK, desaparece. El TXT es
de la aplicación y apunta también los intentos rechazados y los errores, que
en `log_eventos` no aparecen porque no llegaron a guardarse.

## Pruebas

`pruebas.bat` pide las contraseñas de los tres usuarios de demostración y
lanza `PruebasRubrica`. Usa los mismos métodos que los botones y comprueba
cada resultado con una consulta SQL. Deja en la base, como evidencia, pedidos
`PRUEBA-*` y un usuario `prueba.*` desactivado. Cada vez llevan un número
distinto, así que se puede lanzar varias veces.

Resultado el 9 de noviembre de 2026, sobre una base reconstruida desde cero
con los scripts 1–17: **47 PASS, 0 FAIL**. El 13 de noviembre, con los scripts
01–23, dio lo mismo (`../evidencias/java-pruebas-rubrica/`).

| Prueba | Qué comprueba |
|---|---|
| L | Login de cada rol y conexión con su rol de PostgreSQL; contraseña incorrecta rechazada |
| A | Pedido Custom de dos tallas por el comercial: cabecera, líneas, total calculado por la base, stock tras confirmar y `log_eventos` con usuario y hora |
| B | Confirmar sin stock: rechazado, sin stock negativo ni cambios a medias |
| C | Cancelar un pedido confirmado: estado, stock devuelto y auditoría de quién lo hizo |
| D | ROLLBACK deliberado: ni el cambio ni la auditoría quedan |
| E | Consulta sin filtros, con dos y con tres filtros combinados, y limpiar, comparado con SQL |
| F | Búsqueda sin resultados; el comercial no ve la auditoría, ni siquiera saltándose Java |
| G | Tres consultas seguidas: tres líneas nuevas en el TXT |
| H | Pedido desde Java en tablas, consulta visual y TXT; error forzado (referencia repetida) |
| I | Crear, cambiar de rol y desactivar un usuario: el JSON se actualiza; el comercial no puede exportarlo |
| J | Indicadores igual que el SQL; el CSV filtrado coincide fila a fila con la tabla |
| P | Operaciones denegadas por Java y por PostgreSQL sin que cambie ningún dato |

**Lo que estas pruebas no cubren:** que los botones de las ventanas llamen
a esos métodos. Eso lo comprobó aparte un programa de prueba que abrió las
ventanas con los tres roles y comparó la pantalla con SQL: 76 PASS, más 1 sin
conexión (`../evidencias/java-swing/`, con las capturas). Ese programa no está
en el repositorio; en la demostración se enseña a mano.

## Correspondencia con el enunciado

| Apartado | Dónde |
|---|---|
| 3.7 Interfaz Java + JDBC, alta, detalle, confirmar y cancelar | `PanelNuevoPedido`, `PanelConsultas`, `PedidoDAO` |
| 3.7 Consulta visual, tres filtros o más, «Limpiar filtros» | `PanelConsultas`, `PedidoDAO.buscarPedidos` |
| 3.7 PreparedStatement, cierre de recursos, transacciones | todos los DAO (`try` con recursos, `ConexionBD`) |
| 3.8 Login, tres roles, permisos en Java y en PostgreSQL | `UsuarioDAO.login`, `Sesion`, `17_usuario_java.sql` |
| 3.8 Usuario responsable en `log_eventos` | `ConexionBD.empezarTransaccion` |
| 3.10 `actividad_sneaker.txt` | `Archivos.registrar` |
| 3.11 `usuarios_sneaker.json` | `UsuarioDAO.exportarUsuariosJson`, `Archivos.guardarUsuariosJson` |
| 3.12 Indicadores, modelos y tallas, stock bajo con umbral | `PanelIndicadores`, `IndicadoresDAO` |
| 3.12 CSV de la consulta filtrada | `Archivos.exportarCsv` |
| 3.9 y 3.13 Pruebas A–J | `PruebasRubrica` |
