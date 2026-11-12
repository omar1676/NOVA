# NOVA Sneakers · Guía de defensa

13/11/2026 · Para Omar, Álvaro y Berme (2.º DAM) · rama `integracion/candidata-2`

> Los tres tenéis que poder contestar sobre **todo**. El enunciado lo dice así: «los roles sirven para organizar el trabajo; no justifican que un integrante desconozca el resto de la solución. La defensa podrá incluir preguntas individuales» (IM-COM-09). Y Acceso a Datos añade: «Todos los miembros deben comprender el modelo y poder explicar consultas representativas» (AD-135).
>
> Que algo esté implementado no significa que lo sepáis explicar. Esta guía sirve para comprobarlo.

## Cómo usar esta guía

1. Lee una sección entera.
2. Tapa las respuestas y contesta las preguntas en voz alta. Si tardas más de 30 segundos o necesitas mirar el código, márcala.
3. Abre cada archivo en la línea citada y explica qué hace sin leer el comentario.
4. Haz los dos ejercicios y compara tu respuesta con el **Anexo A**.
5. Apunta cómo te ha ido en la hoja de autoevaluación de `SIMULACION_DEFENSA.md`.

**Convenciones**

- Las rutas de código y de resultados son relativas a la raíz del repositorio, rama `integracion/candidata-2` (las líneas se han comprobado con el código de `8cdc08c`, el que pasó la regresión del 13/11). Si alguien toca un archivo, las líneas pueden moverse: repasad las citas la víspera.
- Los resultados de las pruebas están en `06_Intermodular/evidencias/regresion-final/` (regresión completa del 13/11, con la hora y el entorno de cada batería).
- `archivo:12-20` significa «líneas 12 a 20».
- **[PENDIENTE (quién)]**: no hay evidencias o falta hacerlo. **[PROVISIONAL]**: funciona con los datos de SO024 inventados. **[POR DECIDIR (los tres)]**: decisión del equipo. **[DUDA PARA EL PROFESOR (Dn)]**: pregunta abierta de la matriz de rúbricas.
- No hay ninguna contraseña en esta guía ni debe haberla en las diapositivas.

## Índice

0. [El proyecto en un minuto](#0-el-proyecto-en-un-minuto)
1. [PostgreSQL: modelo, restricciones y transacciones](#1-postgresql-modelo-restricciones-y-transacciones)
2. [SQL y PL/pgSQL: triggers, auditoría y SECURITY DEFINER](#2-sql-y-plpgsql-triggers-auditoría-y-security-definer)
3. [Java/JDBC](#3-javajdbc)
4. [PSP: procesos](#4-psp-procesos)
5. [Python y pandas: ETL, 12 reglas, DataFrames y KPIs](#5-python-y-pandas-etl-12-reglas-dataframes-y-kpis)
6. [Estadística: bootstrap e hipótesis](#6-estadística-bootstrap-e-hipótesis)
7. [RFM](#7-rfm)
8. [KMeans](#8-kmeans)
9. [Predicción de la demanda](#9-predicción-de-la-demanda)
10. [Streamlit: refresco de 60 s](#10-streamlit-refresco-de-60-s)
11. [Odoo [PENDIENTE (Berme)]](#11-odoo-pendiente-berme)
12. [Interfaces](#12-interfaces)
13. [Seguridad](#13-seguridad)
14. [Git](#14-git)
15. [Integración: el caso SO024](#15-integración-el-caso-so024)
16. [Portal del trabajador (ampliación, de Berme)](#16-portal-del-trabajador-ampliación-de-berme)
- [Anexo A. Soluciones de los ejercicios](#anexo-a-soluciones-de-los-ejercicios)
- [Anexo B. Dónde están las pruebas](#anexo-b-dónde-están-las-pruebas)

---

## 0. El proyecto en un minuto

Apréndelo casi de memoria; es la primera pregunta de cualquier tribunal.

> NOVA Sneakers es una fábrica de zapatillas que vende modelos de catálogo y pedidos personalizados para clubes (pedidos Custom). Hemos hecho una web responsive con el catálogo y una solicitud Custom; una base PostgreSQL en la que los importes, el stock y la auditoría los calculan triggers; una aplicación Java Swing que crea, confirma y consulta pedidos según el rol del usuario; un subsistema PSP que procesa la exportación de un pedido Custom con un proceso padre y tres hijos; y un análisis en Python con un dashboard Streamlit que se recalcula cada 60 segundos. Como ampliaciones, una tienda online, un panel de administración y un portal del trabajador con un login único. El hilo conductor es el pedido SO024 del Club Halcones: 40 pares de Runner X de las tallas 38 a 46. Odoo, que según el enunciado es el núcleo de ventas y fabricación, está pendiente.

**Cómo se conectan las piezas**

```
Navegador (web y tienda) --/api/tienda--> servidor-admin (Node + Express, 127.0.0.1:3000)
                                           usuario tienda_nova -> SET LOCAL ROLE tienda_web ----> PostgreSQL
Navegador (login único) --/api/login---> servidor-admin: administrador -> panel; trabajador -> portal; comercial -> 403
Navegador (panel admin)  --/api/admin---> servidor-admin
                                           usuario web_nova -> SET LOCAL ROLE panel_lectura -----> PostgreSQL
                                                               (o panel_reparto para "Marcar en reparto")
Navegador (portal)  --/api/trabajador---> servidor-admin
                                           usuario web_nova -> SET LOCAL ROLE portal_trabajador -> PostgreSQL
Aplicación Java Swing ----JDBC---------> usuario java_nova -> SET ROLE nova_admin /
                                           nova_comercial / nova_trabajador ------------------> PostgreSQL

PostgreSQL --15_exportar_fabricacion.sql (1 CSV)--> PSP: ProcesadorPedidosCustom + 3 hijos
                                                     --> salidas/ficha_taller_<ref>.txt y registro_psp.txt
PostgreSQL --16_exportar_csv_dashboard.sql (5 CSV)--> 04_Python/entrada_acc/
                                                     --> main.py (consola) y app_dashboard.py (Streamlit, cada 60 s)
Odoo (pedido de venta, fabricación, entrega, factura) ............................ [PENDIENTE (Berme)]
(servidor-admin/odoo.js, el conector de Berme, está desactivado: sin ODOO_* no llama a nada)
```

**Cifras que hay que saber** (regresión completa del 13/11 sobre el código final, salvo donde se indica; todo en `06_Intermodular/evidencias/regresion-final/`)

| Qué | Resultado | Dónde |
|---|---|---|
| Scripts SQL 01–23 en una base vacía; batería 09–16 | 123 PASS, 0 FAIL y 1 ERROR previsto (S4b) | `01_sql/00_resumen.txt` |
| SQL de la tienda (20 y 21), del reparto (22) y del portal (23) | 55/55, 37/37 y 50/50 | `01_sql/05_sql_tienda.txt`, `07_sql_reparto_con23.txt`, `08_sql_portal.txt` |
| Java: `nova.PruebasRubrica` (login, A–J y permisos) | 47 PASS, 0 FAIL | `02_java_psp/02_pruebas_rubrica.txt` |
| Java: ventanas Swing (`ProbarVentanas`) | 76 PASS, 0 FAIL; sin conexión 1/1 | `07_ventanas_swing/` |
| PSP: `PruebasPsp` | 27 de 27 | `02_java_psp/04_psp_pruebas.txt` |
| Python: `unittest` | 265 pruebas OK | `04_python/02_unittest.txt` |
| Python: las 93 salidas de `main.py` frente a la referencia | 91 idénticas, 2 con columnas nuevas a propósito y 4 archivos nuevos a propósito | `04_python/03_salidas_93.txt` |
| Web: interfaces / web completa / mejoras | 136/136, 114/114 y 81/81 | `05_web/02_interfaces.txt`, `03_web.txt`, `01_mejoras.txt` |
| Compra completa en Edge, contrastada con PostgreSQL | 139 PASS, 0 FAIL | `05_web/04_compra_edge.txt` |
| Reparto en Edge / login único, roles y portal en Edge | 29/29 y 82/82 | `05_web/05_recorrido_reparto.txt`, `06_edge_portal.txt` |
| Servidor: panel / tienda / portal (`npm test`, `test:tienda`, `test:portal`) | 23/23, 39/39 y 24/24 | `03_node/` |
| Recibo con Ethereal: real (datos ficticios) / sin red / sin respuesta | 16/16, 5/5 y 5/5 | `05_web/07_ethereal_real.txt`, `08_…`, `09_…` |
| SO024 de punta a punta **[PROVISIONAL]** | 40 pares, 9 líneas, 3.996,00 €; PSP código 0; un solo pedido en Python | `06_so024_provisional/00_cadena.txt` |
| Lighthouse (11/11) | Accesibilidad 100 y buenas prácticas 100, escritorio y móvil | `01_Interfaces/evidencias/web/README.md:20-21` |

---

## 1. PostgreSQL: modelo, restricciones y transacciones

### Preguntas probables

**P1.1 ¿Cómo habéis modelado el catálogo?**
En cuatro niveles: `modelos` (nombre y precio base) → `variantes` (un color de un modelo, con un suplemento de precio) → `producto_sku` (una variante en una talla) → `existencias` (pares de ese SKU en una nave). Un SKU es «modelo + color + talla», y `UNIQUE (id_variante, talla)` impide repetirlo (`02_Acceso_Datos/sql/sneaker-factory-esquema.sql:41`).

**P1.2 ¿Qué diferencia hay entre `pedidos` y `linea_pedido`?**
`pedidos` es la cabecera: cliente, estado, estado del pago, si es Custom y su personalización, y los totales. `linea_pedido` tiene una fila por SKU con la cantidad, el precio unitario y el subtotal. Los totales de la cabecera no los escribe nadie a mano: los calcula un trigger a partir de las líneas.

**P1.3 ¿Cuántas tablas hay?**
El esquema crea 13 (`sneaker-factory-esquema.sql`), `04_xnova.sql` añade `configuraciones_xnova` (14, las del módulo de Acceso a Datos) y la tienda web añade `cuentas_cliente` (`20_tienda_web.sql:69-76`). La auditoría se guarda en `log_eventos` (`esquema:151-160`).

**P1.4 ¿Qué restricciones podéis enseñar?**
Claves primarias con `GENERATED ALWAYS AS IDENTITY`, claves foráneas (`esquema:162-174`), NOT NULL, UNIQUE (referencia del pedido, email del cliente, SKU) y CHECK: talla entre 20 y 55 (`:42`), cantidad de la línea mayor que 0 (`:146`), stock nunca negativo (`:61`) y estados de una lista cerrada (`:132-133`). `11_dml_ejemplos.sql` enseña seis rechazos y da 12 PASS.

**P1.5 Si el stock ya lo controla una función, ¿para qué sirve el `CHECK (cantidad >= 0)`?**
Es la última barrera. Aunque alguien haga un UPDATE a mano o falle una función, PostgreSQL no deja guardar un stock negativo. La función da un mensaje claro; el CHECK garantiza que el dato nunca es imposible.

**P1.6 ¿Qué es una transacción y dónde la usáis?**
Un grupo de operaciones que se guarda entero (COMMIT) o no se guarda nada (ROLLBACK). El esquema entero va entre `BEGIN` y `COMMIT` (`esquema:1` y `:189`); cada prueba de `09_pruebas.sql` va entre BEGIN y ROLLBACK para no dejar rastro (por ejemplo, `:150-186`); y Java crea un pedido con todas sus líneas en una sola transacción (`02_Acceso_Datos/java/src/nova/PedidoDAO.java:70-106`).

**P1.7 ¿Qué ve otra conexión mientras una transacción no ha hecho COMMIT?**
Nada de lo nuevo: ni el pedido ni su evento de auditoría (es el aislamiento por defecto, READ COMMITTED). Se midió a mano con dos sesiones el 8/11: 0 eventos durante la transacción y 1 después del COMMIT; con ROLLBACK desaparecen los dos (`02_Acceso_Datos/documentacion/README.md:873-919`).

**P1.8 ¿Qué pasa si dos personas confirman a la vez pedidos que necesitan el último par?**
`descontar_stock` mete la comprobación en el propio UPDATE: `WHERE ... AND cantidad >= p_cantidad` (`02_funciones.sql:144-148`). La segunda transacción espera a que la primera libere la fila, vuelve a evaluar la condición con el dato nuevo, no encuentra ninguna fila y lanza «Stock insuficiente o producto no encontrado». El stock nunca queda en negativo.

**P1.9 ¿Por qué los scripts no se ejecutan en el orden de su número?**
Porque el número es el orden en que se escribieron. `04_xnova.sql` va antes que `02_funciones.sql` porque una función usa su tabla; los triggers, después de las funciones; y `08_auditoria.sql`, después de los datos, para que `log_eventos` empiece vacía (`documentacion/README.md:20-117`). El orden con el que se probó el 13/11, con los 23 scripts, está en `06_Intermodular/evidencias/regresion-final/01_sql/01_montaje_01_23.txt` y en `06_Intermodular/manuales/MANUAL_INSTALACION.md` §3.

**P1.10 ¿Para qué el esquema `extensiones`?**
`pgcrypto` (bcrypt y HMAC) se instala en su propio esquema para no mezclar sus funciones con las nuestras en `public` (`esquema:3-5`). Por eso el primer script necesita un superusuario: crear una extensión no lo puede hacer cualquiera.

**P1.11 ¿Qué pregunta responde la consulta con HAVING?**
«¿Qué referencias se quedarán con menos de 10 pares cuando se sirvan los pedidos pendientes?» (`06_consultas.sql:31-56`). Para cada SKU suma sus existencias de todas las naves, le resta los pares de los pedidos pendientes y el `HAVING` (`:55`) se queda con las que bajan de 10, el umbral de stock bajo. `HAVING` filtra después de agrupar; `WHERE` no podría, porque la suma todavía no existe. Con los datos de prueba devuelve 1 fila: `NOVA-4-43`, 20 en stock y 11 pendientes → 9 (`06_Intermodular/evidencias/regresion-final/01_sql/04_06_consultas.txt`). Hasta el 12/11 devolvía 0 filas.

### Código real

- `02_Acceso_Datos/sql/sneaker-factory-esquema.sql:33-43` — tabla `producto_sku`: el SKU es único, la pareja variante + talla también, y la talla tiene que estar entre 20 y 55.
- `02_Acceso_Datos/sql/sneaker-factory-esquema.sql:54-62` — tabla `existencias`: una fila por SKU y nave (`UNIQUE`) y `CHECK (cantidad >= 0)`.
- `02_Acceso_Datos/java/src/nova/PedidoDAO.java:70-106` — `crearPedido`: abre la transacción, crea la cabecera con la primera línea y añade las demás; si todo va bien, COMMIT; si algo falla, ROLLBACK y apunta el rechazo en el TXT.

### Ejercicios

- **E1.1** Alguien intenta guardar una línea con cantidad 0. Di las tres barreras que lo impiden según por dónde entre (la función, un INSERT directo o el rol) y señala la línea de cada una.
- **E1.2** Java está creando un pedido de 3 líneas y la tercera pide una talla que no existe para ese color. ¿Qué queda en `pedidos`, `linea_pedido`, `log_eventos` y `actividad_sneaker.txt`? Señala las líneas de `PedidoDAO.java` que lo deciden.

### Limitaciones que conviene decir antes de que pregunten

- Los scripts de instalación no se pueden relanzar sobre la misma base: hay que borrarla y crearla de nuevo (`documentacion/README.md`, §12, punto 6).
- Un pedido pendiente no reserva stock: lo consigue el primero que confirma (§12, punto 3b). Es lo que pide el enunciado: descontar al confirmar.
- Cancelar no cambia `estado_pago`: un pedido puede quedar cancelado y pagado (§12, punto 3). Tampoco hay una máquina de estados completa: solo se bloquea salir de `cancelado`.
- `nave.capacidad` no se comprueba en ningún sitio (§12, punto 7). Con el catálogo completo hay 17.170 pares para una nave de 2.000 (`06_Intermodular/rubricas/MATRIZ_RUBRICAS.md`).
- Hay dos diagramas E-R (`02_Acceso_Datos/modelo/sneaker-factory.dbm` y `02_Acceso_Datos/modelo-er/Modelo-Er-Intermodular.drawio`) y ninguna imagen exportada. **[PENDIENTE (Álvaro): elegir el E-R oficial y exportarlo a PNG (AD-05).]**
- El README dice en §12, punto 5, que `modelos.nombre` no tiene UNIQUE, pero el esquema ya lo tiene (`esquema:19`): es un texto desfasado que hay que corregir.
- La prueba de las dos sesiones (8/11) y la de concurrencia (7/11) se hicieron a mano y sin capturas. La de concurrencia, además, con la versión anterior, cuando el stock se descontaba al comprar. El mecanismo (`WHERE cantidad >= p_cantidad`) es el mismo que hoy.

---

## 2. SQL y PL/pgSQL: triggers, auditoría y SECURITY DEFINER

### Preguntas probables

**P2.1 ¿Qué triggers tenéis?**
Diez. Cinco de cálculo y control en `03_triggers.sql` (subtotal, totales, proteger líneas, descontar y devolver stock) y cinco de auditoría en `08_auditoria.sql` (alta de pedido, cambio de estado, cambio de stock y baja lógica de modelo y de SKU). La tabla con la tabla que dispara cada uno, si es BEFORE o AFTER y qué modifica está en `documentacion/README.md:269-298`.

**P2.2 ¿Cómo se calcula el importe del pedido?**
En dos pasos. BEFORE INSERT OR UPDATE en la línea: `subtotal = cantidad × precio_unitario` (`02_funciones.sql:124-133` y `03_triggers.sql:8-12`). AFTER INSERT, UPDATE o DELETE: se recalculan `cantidad_total` e `importe_total` con un `SUM` de todas las líneas del pedido (`02_funciones.sql:93-122` y `03_triggers.sql:2-6`).

**P2.3 ¿Por qué no sumáis el subtotal nuevo al total que ya había?**
Porque así, si un trigger salta dos veces o se modifica una línea, se sumaría de más. Recalcular desde cero con `SUM` da siempre el mismo resultado, se ejecute las veces que se ejecute (AD-28). La prueba P3 de `09_pruebas.sql` lo comprueba en todos los pedidos.

**P2.4 ¿Por qué el subtotal va en BEFORE y los totales en AFTER?**
En BEFORE se puede cambiar `NEW` antes de que la fila se guarde, así que el subtotal ya se guarda bien. Los totales necesitan que la línea esté guardada para que el `SUM` la cuente; por eso van en AFTER, y la función devuelve `NULL`, que en AFTER no importa.

**P2.5 ¿Cuándo se descuenta el stock?**
Al confirmar el pedido, no al crearlo. `trg_descontar_stock_confirmacion` salta cuando el estado pasa a `confirmado` (`03_triggers.sql:27-32`), y `descontar_stock_confirmacion` llama a `descontar_stock` para cada línea que todavía no tiene el stock descontado y la marca con `stock_descontado = true` (`02_funciones.sql:448-479`).

**P2.6 ¿Cómo evitáis descontar el stock dos veces?**
Con tres candados: el `WHEN` del trigger, que solo deja pasar si antes no estaba confirmado (`03_triggers.sql:31`); el filtro `stock_descontado = false` (`02_funciones.sql:461`); y `proteger_linea_pedido`, que solo deja cambiar esa marca de false a true con el pedido confirmado y de true a false con el pedido cancelado (`02_funciones.sql:405-421`).

**P2.7 ¿Y al cancelar?**
`trg_devolver_stock_cancelacion` (`03_triggers.sql:14-19`) devuelve a `existencias` los pares de cada línea con `stock_descontado = true` y les quita la marca (`02_funciones.sql:342-361`). Además, prohíbe reactivar un pedido cancelado (`02_funciones.sql:334-337`).

**P2.8 ¿Qué es SECURITY DEFINER y por qué lleva `SET search_path`?**
La función se ejecuta con los permisos de quien la creó, no con los de quien la llama. Así, `nova_admin` no puede hacer INSERT en `linea_pedido` (`07_seguridad.sql:63-64`), pero sí añadir líneas con `anadir_linea_pedido`, que pone el precio de la base (`02_funciones.sql:157-218`). El `search_path` fijo impide que alguien cree un objeto con el mismo nombre en otro esquema y la función lo use sin querer.

**P2.9 ¿Por qué tantos `REVOKE EXECUTE ... FROM PUBLIC`?**
Porque al crear una función PostgreSQL deja que la ejecute cualquiera. Se le quita a todos y se da solo al rol que la necesita (`07_seguridad.sql:66-85` y `20_tienda_web.sql:420-426`). El único ERROR de la batería es a propósito: `nova_cliente` intenta descontar stock y la base se lo niega (S4b, `09_pruebas.sql:998-1003`).

**P2.10 ¿Cómo sabe la auditoría quién hizo la operación, y qué pasa con un ROLLBACK?**
`iniciar_sesion` comprueba la contraseña y guarda `id:firma` en la variable `nova.id_usuario`, solo para esa transacción (`02_funciones.sql:29-34`). Los triggers llaman a `usuario_sesion()`, que vuelve a calcular la firma y, si no cuadra, devuelve NULL (`02_funciones.sql:40-83`). Como el evento se inserta dentro de la misma transacción, un ROLLBACK lo borra también (prueba D3: «1 eventos antes y 1 después»).

### Código real

- `02_Acceso_Datos/sql/02_funciones.sql:135-155` — `descontar_stock`: la comprobación del stock va dentro del `WHERE` del UPDATE; si no se actualiza ninguna fila, lanza «Stock insuficiente o producto no encontrado».
- `02_Acceso_Datos/sql/03_triggers.sql:27-32` y `02_funciones.sql:448-479` — el trigger que descuenta al confirmar y la función que recorre las líneas que faltan por descontar.
- `02_Acceso_Datos/sql/08_auditoria.sql:36-70` — `auditar_estado_pedido`: escribe `BAJA_LOGICA` si el pedido pasa a cancelado y `CAMBIO_ESTADO` en otro caso, con el usuario que devuelve `usuario_sesion()`.

### Ejercicios

- **E2.1** En la tienda web, el cliente pulsa «Simular pago aceptado» dos veces muy rápido. ¿Qué pasa en la base? Señala las líneas que impiden cobrar dos veces y descontar el stock dos veces.
- **E2.2** Se borra una línea de un pedido pendiente. ¿Qué triggers saltan, en qué orden y qué cambia? ¿Y si el pedido ya estuviera confirmado?

### Limitaciones que conviene decir antes de que pregunten

- No hay trigger de auditoría en `linea_pedido`. Se auditan el alta del pedido, sus cambios de estado y cada movimiento de stock (`08_auditoria.sql`), pero añadir o borrar una línea de un pedido pendiente no deja un evento propio.
- El evento de stock guarda quién lo hizo, pero no de qué pedido es: hay que relacionarlo por la hora de la transacción (`documentacion/README.md`, §12, punto 1c).
- Las compras de la tienda web quedan en `log_eventos` sin usuario, «(sin sesión)»: el cliente web no es un usuario de la tabla `usuarios`. El cliente sí aparece en el detalle (captura `01_Interfaces/evidencias/tienda/capturas-2026-11-13/panel_15_auditoria_con_compras_web.png`). Los cambios del portal del trabajador, en cambio, sí quedan a nombre del trabajador (§16).
- Las funciones no consultan el rol funcional de la tabla `roles`: deciden los permisos del rol de conexión. Si alguien conectara todo como `nova_admin`, la seguridad de la base no serviría de nada (§12, punto 1c).
- `realizar_compra` no comprueba de quién es el pedido (§12, punto 1). En la tienda sí: las funciones del script 20 comprueban que el pedido es de ese cliente (`20_tienda_web.sql:226-237` y `:346-359`).

---

## 3. Java/JDBC

### Preguntas probables

**P3.1 ¿Por qué PreparedStatement?**
Porque separa el SQL de los datos: el valor que escribe el usuario va como parámetro `?` y el driver lo envía aparte, así que no puede cambiar la consulta (inyección SQL). Además convierte bien los tipos. Ejemplo: los filtros de `02_Acceso_Datos/java/src/nova/PedidoDAO.java:250-279`.

**P3.2 ¿Cómo hacéis que un filtro vacío no filtre?**
Solo se añade al `WHERE` el trozo de los filtros que tienen valor; los que valen null no se añaden. El `WHERE 1 = 1` sirve para poder añadir siempre `AND ...` (`PedidoDAO.java:246-273`). Con todo vacío salen todos los pedidos (pruebas E1 y E4).

**P3.3 ¿Cómo cerráis los recursos?**
Con try-with-resources: el `PreparedStatement` y el `ResultSet` se declaran dentro del `try (...)` y se cierran solos aunque salte una excepción (`PedidoDAO.java:276-286`). La conexión es una para toda la aplicación y se cierra al salir (`ConexionBD.java:125-134`).

**P3.4 ¿Cómo se hace una transacción con JDBC?**
`setAutoCommit(false)` al empezar (`ConexionBD.java:96`), `commit()` si todo va bien (`:108-111`) y `rollback()` en el `catch` (`:114-123`, que se llama, por ejemplo, desde `PedidoDAO.java:98-99`). Al terminar se vuelve a poner `autoCommit` a true.

**P3.5 ¿Java calcula los importes o toca el stock?**
No. Java llama a `realizar_compra` y `anadir_linea_pedido` y cambia el estado del pedido; el precio, los totales, el stock y la auditoría los hace PostgreSQL (`PedidoDAO.java:11-18`, `:137-164` y `:184-196`). Es lo que exige AD-43, y las pruebas A3–A6 lo comprueban.

**P3.6 ¿Cómo funcionan los roles en Java?**
Hay dos barreras. La primera es `Sesion.comprobarPermiso`, con la matriz de permisos (`Sesion.java:8-16` y `:75-107`). La segunda es PostgreSQL: Java se conecta como `java_nova`, que no hereda permisos, y tras el login hace `SET ROLE` al rol de la base que corresponde (`ConexionBD.java:69-78`, `UsuarioDAO.java:60-64` y `17_usuario_java.sql:41-48`). Las pruebas P2 y P4 se saltan Java y la base lo niega igual.

**P3.7 Si usáis PreparedStatement, ¿por qué `SET ROLE` va concatenado?**
Porque `SET ROLE` no admite parámetros `?`. Para que sea seguro, solo acepta tres nombres fijos, y nunca le llega texto escrito por el usuario (`ConexionBD.java:63-78`).

**P3.8 ¿Cómo sabe PostgreSQL qué usuario de Java hace cada cambio?**
Cada transacción que escribe empieza con `SELECT iniciar_sesion(?, ?)` (`ConexionBD.java:94-106`). Eso deja el usuario firmado para esa transacción y los triggers lo guardan en `log_eventos`. Por eso la contraseña está en memoria mientras dura la sesión (`Sesion.java:35-38`); no se escribe en ningún archivo.

**P3.9 ¿Qué guarda `actividad_sneaker.txt` y cómo se escribe?**
Una línea por acción: `fecha | usuario | rol | acción | resultado | detalle`, sin contraseñas ni SQL (`Archivos.java:41-69`). Se abre con `FileWriter(..., UTF_8, true)`, y ese `true` es el modo append (`:63-64`). Se cierra en cada línea, así que se ve en disco sin cerrar Java. También apunta intentos rechazados y errores.

**P3.10 ¿Cómo escribís el JSON de usuarios y el CSV?**
El JSON se exporta solo después del COMMIT (`UsuarioDAO.java:139-147`) y sin la columna `password_hash` (`:93-94`); se escribe en un temporal, se cambia por el bueno con `ATOMIC_MOVE` y se vuelve a leer para comprobarlo (`Archivos.java:146-155`). El CSV copia la cabecera y las filas de la JTable, en UTF-8 y con comillas cuando un campo lleva comas (`Archivos.java:79-113`); la prueba J6 da 11 filas y 9 columnas, igual que la tabla.

### Código real

- `02_Acceso_Datos/java/src/nova/PedidoDAO.java:232-292` — `buscarPedidos`: filtros combinables con parámetros; con todo null salen todos los pedidos.
- `02_Acceso_Datos/java/src/nova/ConexionBD.java:94-106` — `empezarTransaccion`: desactiva el autocommit y llama a `iniciar_sesion` para que la auditoría sepa quién firma.
- `02_Acceso_Datos/java/src/nova/Archivos.java:126-157` — `guardarUsuariosJson`: escribe en un temporal, lo mueve de forma atómica y lo relee.

### Ejercicios

- **E3.1** En Java se pulsa «Confirmar pedido» dos veces sobre el mismo pedido. ¿Qué pasa la segunda vez? Señala la línea.
- **E3.2** Un comercial intenta ver la auditoría. ¿Qué lo para en Java? ¿Y si alguien se salta Java y lanza la consulta con la misma conexión? Señala las dos líneas.

### Limitaciones que conviene decir antes de que pregunten

- La contraseña del usuario está en memoria mientras dura la sesión, para firmar cada transacción (`Sesion.java:35-38`). No va a disco, pero es un compromiso de diseño.
- Java no tiene límite de intentos de login (el servidor web sí lo tiene).
- No existe la operación «modificar pedido» en Java (AD-86). **[DUDA PARA EL PROFESOR (D10): si hace falta.]**
- La matriz de permisos está fija en `Sesion.java` y en `07_seguridad.sql`: el administrador asigna roles, pero no puede editar permisos desde la aplicación (AD-57, PARCIAL). **[DUDA PARA EL PROFESOR (D10): si asignar roles basta.]**
- El JSON no lleva la fecha de creación (el enunciado dice «si procede»).
- La prueba visual de las ventanas Swing se repitió el 13/11 sobre el código final: 76/76 y 1/1 sin conexión (`06_Intermodular/evidencias/regresion-final/07_ventanas_swing/` y las capturas de `02_Acceso_Datos/evidencias/java-swing/`). `PruebasRubrica` (47/47) llama a los mismos métodos que los botones, no a la ventana. No hay capturas de las pruebas A, B, C, D, G e I hechas en la ventana: se enseñan en la demostración (`06_Intermodular/manuales/MANUAL_DEMOSTRACION.md`).
- Solo hay una nave: Java coge la primera (`PedidoDAO.java:108-118`).

---

## 4. PSP: procesos

### Preguntas probables

**P4.1 ¿Qué hace el subsistema PSP y qué no hace?**
Procesa una copia exportada en CSV de un pedido Custom con un proceso padre y tres hijos, y genera una ficha auxiliar para el taller y un registro. No escribe en PostgreSQL ni en Odoo, no toca el stock y no crea la orden de fabricación (`03_PSP/ProcesadorPedidosCustom.java:38-40`).

**P4.2 ¿Qué hace cada hijo?**
`ValidadorPedidoCustom` comprueba el CSV y lo normaliza; `Psp.AnalizadorTallas` agrupa los pares por modelo, color y talla; y `GeneradorFichaTaller` escribe la ficha (`ProcesadorPedidosCustom.java:55-58`). Cada uno es un programa Java con su propio `main` que se ejecuta en su propia máquina virtual.

**P4.3 ¿Cómo se lanza un hijo?**
Con `new ProcessBuilder(java, "-cp", classpath, clase)`, usando el mismo `java` y el mismo classpath que el padre (`03_PSP/GestorProcesos.java:84-92`). Si no arranca, se guarda el código especial `NO_ARRANCA` (-1) y el motivo (`:94-100`).

**P4.4 ¿Cómo se comunican?**
Siempre por stdin y stdout, pasando por el padre: el padre escribe el CSV en la entrada del validador, lee su salida y se la pasa al analizador, y así hasta el generador (`ProcesadorPedidosCustom.java:25-30` y `:119-207`). Los errores van por stderr y se leen por separado.

**P4.5 ¿Por qué `GestorProcesos` usa tres hilos?**
Las tuberías tienen un tamaño limitado: si el hijo llena stdout o stderr y nadie las lee, se bloquea, y el padre, que lo espera, también (interbloqueo). Un hilo escribe en stdin y lo cierra, otros dos vacían stdout y stderr, y el principal queda libre para esperar con límite de tiempo (`GestorProcesos.java:102-138`). Cada hilo escribe en su propia lista y el principal no las lee hasta después de `join()`, así que no hace falta sincronizar.

**P4.6 ¿Qué códigos de salida hay?**
Los hijos devuelven 0 si va bien y 2 si los datos no son válidos (`ValidadorPedidoCustom.java:269-272`); cualquier otro es un fallo. El padre devuelve 0 (correcto), 1 (problema con un archivo), 2 (pedido rechazado) o 3 (fallo de un proceso) (`ProcesadorPedidosCustom.java:42-48`). `GestorProcesos` añade -1 (no arranca) y -2 (tiempo agotado) (`GestorProcesos.java:49-53`).

**P4.7 ¿Qué pasa si un hijo se queda colgado?**
`waitFor(10, TimeUnit.SECONDS)` espera como mucho 10 segundos (`GestorProcesos.java:138` y `ProcesadorPedidosCustom.java:61`). Si no ha terminado, se llama a `destroy()`, se espera un segundo más y, si sigue vivo, `destroyForcibly()` (`GestorProcesos.java:143-153`). La prueba 10 cancela un hijo a los 2 s con el código -2.

**P4.8 ¿Cómo sabe el padre que la respuesta del hijo es buena?**
`comprobarPaso` mira el tiempo, si arrancó, el código de salida, si el hijo recibió todos los datos, que la primera línea empiece por `OK;` y que hable del mismo pedido (`ProcesadorPedidosCustom.java:286-350`). Además comprueba que el validador y el analizador cuentan los mismos pares (`:179-182`). Si algo falla, no lanza el paso siguiente.

**P4.9 ¿Qué evidencias deja?**
`salidas/ficha_taller_<referencia>.txt` y `salidas/registro_psp.txt`, al que cada ejecución añade su bloque en modo APPEND (`ProcesadorPedidosCustom.java:218-223` y `:375-381`). Hay un ejemplo real en `03_PSP/evidencias/ficha_taller_CUSTOM-40.txt`, que termina diciendo que no sustituye a la orden de fabricación de Odoo (`:25-28`).

**P4.10 ¿De dónde sale el CSV de entrada?**
De `02_Acceso_Datos/sql/15_exportar_fabricacion.sql`, que exporta con `\copy` las ocho columnas de la ficha de un pedido confirmado (`:197`). El validador espera exactamente esa cabecera (`ValidadorPedidoCustom.java:52-53`).

### Código real

- `03_PSP/GestorProcesos.java:87-153` — lanza el hijo, arranca los tres hilos, espera con límite y lo cancela si no termina.
- `03_PSP/ProcesadorPedidosCustom.java:286-350` — `comprobarPaso`: decide si el paso fue bien antes de seguir.
- `03_PSP/ValidadorPedidoCustom.java:269-272` — el error del hijo: el motivo por stderr y `System.exit(2)`.

### Ejercicios

- **E4.1** El CSV trae una línea con la talla 99. ¿Qué proceso la rechaza, con qué código termina el padre y se crea la ficha?
- **E4.2** `03_PSP/src/Psp/LanzadorAnalizador.java:29-32` lee primero toda la salida del hijo y después hace `waitFor(10, SECONDS)`. ¿Por qué ese tiempo de espera no protege de un hijo colgado? ¿Qué hace distinto `GestorProcesos`?

### Limitaciones que conviene decir antes de que pregunten

- Solo acepta CSV (un `.json` se rechaza con código 1) y un pedido por archivo. Procesar varios a la vez es la «ampliación posterior» del enunciado y no está hecha (`03_PSP/README.md`, «Límites conocidos»).
- El padre guarda en memoria todo lo que escribe cada hijo, sin tope.
- El validador solo comprueba que la talla sea positiva; el rango de 20 a 55 lo comprueba el analizador (prueba 12k).
- En la consola de Windows, los acentos de los mensajes del analizador salen mal si no se usa `-Dfile.encoding=UTF-8` (se ve en `06_Intermodular/evidencias/regresion-final/02_java_psp/04_psp_pruebas.txt`).
- La ficha todavía no se puede relacionar con un pedido de Odoo, porque no existe (PSP-10 y PSP-29). **[PENDIENTE (Berme): el pedido de Odoo y la equivalencia de su número y sus SKU.]**
- SO024 solo se ha probado con datos PROVISIONALES: el script 18 lo prepara en PostgreSQL y la cadena llega a PSP con código 0 (`03_PSP/evidencias/so024_provisional/`; lo explica también `03_PSP/README.md`).
- `scripts/comprobar_psp.py` falla en la primera comprobación, y se sabe por qué: espera la respuesta antigua del validador (`06_Intermodular/evidencias/regresion-final/02_java_psp/07_comprobar_psp.txt`). El arreglo de Berme (`862e37d`, en `feature/berme`) no está en esta rama.
- `LanzadorAnalizador.java` tiene el problema del ejercicio E4.2. El coordinador no lo usa: usa `GestorProcesos`.

---

## 5. Python y pandas: ETL, 12 reglas, DataFrames y KPIs

### Preguntas probables

**P5.1 ¿De dónde salen los datos?**
De cinco CSV que exporta Acceso a Datos con `16_exportar_csv_dashboard.sql`: clientes, modelos, pedidos, líneas y stock, más un `ORIGEN.txt` que dice si son REAL, PRUEBA o SINTÉTICO (`04_Python/config.py:18-26` y `:44`). Python nunca se conecta a PostgreSQL ni escribe en la carpeta de entrada.

**P5.2 ¿Qué pasos sigue el ETL?**
Leer y comprobar el esquema, aplicar las 12 reglas, quedarse con las filas válidas, construir las dos vistas base, calcular los DataFrames y los KPIs, conciliar con SQL y sacar gráficos, estadística, segmentación, predicción e informe (`main.py`, función `ejecutar`, que llama a un paso con nombre por cada fase: `paso_calidad`, `paso_tablas`, `paso_importes`, `paso_kpis`, `paso_conciliacion`…). Si hay una incidencia bloqueante, para y no publica ninguna cifra (`parar_por_bloqueo`, `main.py:158-166`).

**P5.3 ¿Cuáles son las 12 reglas y qué gravedades hay?**
Están en `calidad.py:27-40`: fichero vacío o sin cabeceras, IDs duplicados, claves huérfanas, fechas, cantidades, precios, estados, tallas, falta de cliente o modelo, líneas duplicadas, stock y coherencia. Hay tres gravedades (`:42-50`): bloqueante (no se publica nada), recuperable (se rechaza la fila) y advertencia (la fila se queda y se avisa).

**P5.4 ¿Por qué se rechaza el pedido entero si falla una sola línea?**
Para no contar nunca un pedido a medias: si se rechaza una línea, se rechaza su pedido con todas sus líneas, y si se rechaza un pedido, también sus líneas (`calidad.py:416-457`, sobre todo `:440-446`).

**P5.5 ¿Qué diferencia hay entre `df_lineas_enriquecidas` y `df_pedidos_unicos`?**
La primera tiene una fila por línea, con los datos de su pedido, cliente, modelo y color (`analiticas.py:59-93`). La segunda tiene una fila por pedido, con los pares y el importe sumados desde sus líneas (`:96-152`). Un pedido de 3 líneas es 1 pedido: los pedidos se cuentan en la segunda.

**P5.6 ¿Para qué sirven `validate` e `indicator` en el merge?**
`validate="many_to_one"` hace que el cruce falle si en la tabla de la derecha hay un id repetido, en lugar de multiplicar filas en silencio. `indicator=True` permite ver las claves que no encuentran pareja. Además se comprueba que el número de filas no cambia (`analiticas.py:23-44`).

**P5.7 ¿Qué KPIs calculáis?**
Veinte, de K01 a K20, cada uno con su fórmula, la población que usa y su origen (`kpis.py:67-166`). Ejemplo: K09, el ticket medio, es el importe confirmado entre los pedidos confirmados, y «se divide entre pedidos, nunca entre líneas» (`kpis.py:87-88`).

**P5.8 ¿Qué es una «venta»?**
Se calculan tres criterios: todos los pedidos registrados, los no cancelados (el criterio del panel Java) y los confirmados en adelante (el de la rúbrica de Python) (`analiticas.py:155-181`). **[POR DECIDIR (los tres): cuál es el oficial y si los importes llevan IVA]** (`config.py:156`: «pendiente de confirmar»).

**P5.9 ¿Cómo sabéis que Python cuadra con PostgreSQL?**
Con la conciliación: tres consultas SQL de Acceso a Datos (P-A, P-B y P-C, en `entrada_acc/conciliacion_sql/`) se comparan con los KPIs (`kpis.py:170` en adelante). Con la exportación del 16 salen calidad 100 %, 12 pedidos, 90 pares y 10.686,45 €, igual que en SQL. Además está el caso N: tres consultas más de `12_consultas_panel.sql` (`:244-289`; N-1, ingresos de un mes; N-2, la matriz talla × modelo; N-3, clientes únicos) se contrastan con pandas en `conciliacion.contrastar_caso_n` (`conciliacion.py:176`): 17 de 17 cifras coinciden (`04_Python/conciliacion_sql.md`).

**P5.10 ¿Por qué no rellenáis los vacíos con ceros?**
Porque cero es un dato y vacío es «no se sabe». Solo se pone 0 cuando es un recuento (un pedido sin líneas tiene 0 líneas), y el precio medio de un pedido sin pares se queda vacío (`analiticas.py:128-136`). La rúbrica lo prohíbe expresamente (PY-62).

**P5.11 ¿Qué metadatos lleva cada DataFrame?**
La fecha de corte, las reglas de negocio, los filtros, las filas de origen y la función que lo ha generado (PY-159). `main.py` escribe `metadatos_dataframes.csv`, una fila por CSV, enlazada por el nombre del archivo y la `ejecucion` (`metadatos.py:175`), y cada descarga del dashboard lleva esas columnas con los filtros que se le aplican (`metadatos.del_dashboard`, `:211`).

**P5.12 ¿Cómo se ordenan las recomendaciones del informe ejecutivo?**
Primero por la urgencia (alta: se puede dejar sin servir demanda que ya existe; media: sirve para planificar el próximo mes; baja: NO CALCULABLE o no cambiar nada) y, con la misma urgencia, por su número (`informe.py:11-19` y `:30`). Cada una dice su impacto esperado con una cifra, de dónde sale y la tabla y el gráfico que la sustentan (PY-110 y PY-111).

### Código real

- `04_Python/calidad.py:416-457` — `separar`: aparta las filas con incidencias y arrastra el pedido entero.
- `04_Python/analiticas.py:23-44` — `cruzar`: merge con `validate`, `indicator` y comprobación del número de filas.
- `04_Python/analiticas.py:108-115` — de líneas a pedidos: `groupby("id_pedido")` con número de líneas, pares, importe, modelos y tallas.

### Ejercicios

- **E5.1** Un pedido de 3 líneas tiene una línea con cantidad -2. ¿Qué regla salta, con qué gravedad, y cuántas filas de pedidos y de líneas se rechazan?
- **E5.2** `modelos.csv` llega con dos filas con `id_modelo = 7`. ¿Qué pasa? Y si esa regla no existiera, ¿qué haría el cruce entre líneas y modelos?

### Limitaciones que conviene decir antes de que pregunten

- Los CSV de `entrada_acc` son de PRUEBA (`entrada_acc/ORIGEN.txt`): una base reconstruida con los scripts el 9/11, no la base del equipo. **[PENDIENTE (los tres): exportar la base del equipo y poner «Tipo: REAL» antes de la defensa.]**
- Con esos datos (6 clientes y 12 pedidos de un solo día), RFM, KMeans, la predicción y el bootstrap salen NO CALCULABLE. Se demuestran con los sintéticos (900 pedidos, 40 clientes y 12 modelos).
- El informe técnico está en `04_Python/memoria/INFORME_TECNICO_PYTHON.md`; lo que depende de la exportación REAL o de SO024 sigue marcado como pendiente allí.

---

## 6. Estadística: bootstrap e hipótesis

### Preguntas probables

**P6.1 ¿Qué es el bootstrap?**
Se sacan muchas muestras nuevas del mismo tamaño que la original, con reemplazo (un valor puede salir varias veces), y se calcula el estadístico en cada una (`estadistica.py:137-156`). El intervalo al 95 % va del percentil 2,5 al 97,5 de esos resultados (`:142-146`). Se hacen 2.000 remuestreos (`config.py:208`).

**P6.2 ¿Para qué la semilla fija?**
Para que el resultado se pueda reproducir: con `SEMILLA = 2026` (`config.py:200`) el intervalo sale igual cada vez. Sin semilla, cada ejecución daría un intervalo un poco distinto.

**P6.3 ¿Qué hipótesis planteasteis?**
Tres, escritas antes de calcular nada (`estadistica.py:12-15`). H1: los pedidos Custom dejan más importe por pedido que los estándar. H2: las tallas 41, 42 y 43 reúnen más de la mitad de los pares. H3: los últimos 6 meses tienen más pares que los 6 anteriores.

**P6.4 ¿Qué salió?**
Con los sintéticos: H1, «los datos la apoyan» (diferencia de medianas de 4.636,16 €, IC 4.099,57–4.948,98); H2, evidencia insuficiente (53,2 %, IC 49,46–57,11, que incluye el 50); H3, evidencia insuficiente (−50,2 pares, IC −187,51–99,17, que incluye el 0). Fuente: `hipotesis.csv` de `main.py --modo sintetico` (en `04_Python/outputs/sinteticos/`; se genera al ejecutarlo y no va en Git). El 13/11 salió igual que la referencia (`06_Intermodular/evidencias/regresion-final/04_python/03_salidas_93.txt`).

**P6.5 ¿Por qué la mediana en H1 y no la media?**
Porque los importes están muy sesgados: unos pocos pedidos de club enormes mueven mucho la media. La mediana es el valor del centro y esos extremos no la mueven.

**P6.6 ¿Qué significa «evidencia insuficiente»?**
Que el valor de referencia (0 o 50 %) cae dentro del intervalo, así que los datos no permiten decir ni que sí ni que no (`estadistica.py:189-199`). No quiere decir que la hipótesis sea falsa.

**P6.7 ¿Qué no se puede afirmar?**
Que personalizar haga gastar más a un mismo cliente: se comparan grupos distintos de clientes, no es un experimento, así que no demuestra causa. Y nada sobre clientes reales: con los sintéticos solo se comprueba que el método funciona, porque el generador ya da a los Custom más pares y un recargo del 20 % (`estadistica.py:251-253`).

**P6.8 ¿Y con los datos de Acceso a Datos?**
El ticket medio sale NO CALCULABLE: hay 1 pedido de venta y hacen falta al menos 5 (`config.py:212`; `...\referencia\simplificado\real\bootstrap_ticket_medio.csv`). Con los sintéticos sale 1.011,41 € (IC 878,59–1.153,02) con 822 pedidos.

### Código real

- `04_Python/estadistica.py:137-156` — `remuestrear`, `intervalo` y `bootstrap_media`.
- `04_Python/estadistica.py:189-199` — `veredicto`: apoya, contradice o evidencia insuficiente según dónde cae la referencia.
- `04_Python/estadistica.py:238-245` — el bucle del bootstrap de H1: dos muestras por vuelta y la diferencia de medianas.

### Ejercicios

- **E6.1** En H1, ¿qué resultado escribe `veredicto()` si el intervalo es [−20, 300]? ¿Y si es [120, 300]?
- **E6.2** ¿Por qué en cada vuelta se remuestrea siempre primero la muestra Custom y después la estándar (`estadistica.py:240-243`)? ¿Qué pasaría si se cambiara el orden?

### Limitaciones que conviene decir antes de que pregunten

- Todas las conclusiones con números son de datos SINTÉTICOS: describen la simulación, no a los clientes de NOVA.
- Con los datos de PRUEBA, el bootstrap y las hipótesis no se pueden calcular (muestras de 1 a 5).
- Una diferencia observada no demuestra causalidad (PY-89).

---

## 7. RFM

### Preguntas probables

**P7.1 ¿Qué es RFM?**
Tres números por cliente: Recency, los días desde su última compra válida hasta la fecha de corte; Frequency, cuántos pedidos de venta tiene (pedidos, no líneas); y Monetary, cuánto importe suman (`segmentacion.py:4-9` y `:41-61`).

**P7.2 ¿Qué es una compra válida?**
Un pedido confirmado en adelante (`de_venta`, `analiticas.py:254-256`) y nunca posterior a la fecha de corte (`segmentacion.py:47`). Es el mismo criterio que los KPIs de venta.

**P7.3 ¿Cómo se puntúa cada cliente?**
De 1 a 5 por quintiles: el 20 % con más pedidos tiene F = 5, y así con M. En Recency es al revés: menos días es mejor, así que el más reciente tiene un 5 (`segmentacion.py:64-75` y `:88-91`).

**P7.4 ¿Para qué el `rank(method="first")` antes del `qcut`?**
Para deshacer los empates: si muchos clientes tienen el mismo número de pedidos, `qcut` no podría hacer cinco grupos iguales. Con el rango, cada cliente tiene una posición distinta y el resultado sale siempre igual (`segmentacion.py:64-75`).

**P7.5 ¿Qué segmentos hay?**
Seis, con reglas que se aplican en orden y la primera que se cumple decide: Sin compras válidas, Mejores clientes, En riesgo, Habituales, Inactivos y Ocasionales (`segmentacion.py:31-38` y `:96-109`). Cada uno tiene su significado y su uso comercial al lado.

**P7.6 ¿Qué pasa con los clientes que no han comprado?**
Van a una categoría propia, «Sin compras válidas», con frequency 0, monetary 0 y la recency vacía, porque no hay última compra; no se les inventa actividad (`segmentacion.py:56-59` y `:98-99`).

**P7.7 ¿Qué salió?**
Con los sintéticos (40 clientes): Mejores clientes 7, En riesgo 6, Habituales 11, Inactivos 10, Ocasionales 6 y Sin compras 0 (`...\referencia\simplificado\sintetico\rfm_segmentos.csv`). Con los datos de PRUEBA no se puede: hacen falta 10 clientes con compras (`config.py:222`).

### Código real

- `04_Python/segmentacion.py:41-61` — `rfm`: agrupa las ventas por cliente y une todos los clientes, también los que no han comprado.
- `04_Python/segmentacion.py:64-75` — `quintil`: `rank(method="first")` y `qcut` en 5 grupos.
- `04_Python/segmentacion.py:96-109` — `segmento`: las reglas en orden.

### Ejercicios

- **E7.1** Un cliente tiene R = 5, F = 2 y M = 5. ¿En qué segmento cae? Recorre las reglas en orden.
- **E7.2** Un cliente se dio de alta y solo tiene un pedido, cancelado. ¿Qué R, F y M tiene y en qué segmento cae?

### Limitaciones que conviene decir antes de que pregunten

- Los quintiles son relativos: comparan a los clientes entre sí. Con pocos clientes, un 5 no significa «muy bueno», sino «de los mejores de este grupo».
- Los umbrales de los segmentos (4 o más, 2 o menos…) son una decisión nuestra, explicada pero no validada con el negocio.
- Con los datos de PRUEBA no se puede calcular; se demuestra con los sintéticos (PY-96 lo permite si se dice expresamente).

---

## 8. KMeans

### Preguntas probables

**P8.1 ¿Qué variables usa KMeans?**
Las tres de RFM: los días de recency, `log1p(frequency)` y `log1p(monetary)`, y solo de los clientes con compras (`segmentacion.py:154-170` y `:181`).

**P8.2 ¿Por qué hay que escalar las variables?**
Porque KMeans agrupa por distancias, y días, pedidos y euros tienen escalas muy distintas: la variable con los números más grandes mandaría ella sola. `StandardScaler` deja cada variable con media 0 y desviación 1 (`segmentacion.py:170`).

**P8.3 ¿Y por qué el logaritmo?**
Porque unos pocos clubes con importes enormes decidirían los grupos. `log1p(x) = log(1 + x)` aplasta los valores grandes y acepta el 0 (`segmentacion.py:157-160`).

**P8.4 ¿Qué valores de k probáis y cómo elegís?**
k = 2, 3, 4 y 5 (`config.py:224`). Se queda el que tiene el silhouette más alto; si empatan, el k más pequeño (`segmentacion.py:191-202`).

**P8.5 ¿Qué es el silhouette?**
Una medida de −1 a 1 de lo bien separados que están los grupos: compara lo cerca que está cada cliente de los de su grupo con lo cerca que está del grupo más próximo. Cuanto más alto, mejor separados (`segmentacion.py:176-177` y `:195`).

**P8.6 ¿Qué salió?**
Con los sintéticos: k = 2 → 0,348; k = 3 → 0,361; k = 4 → 0,373 (elegido); k = 5 → 0,319 (`...\referencia\simplificado\sintetico\kmeans_seleccion_k.csv`). Con los datos de PRUEBA no se puede: hay 1 cliente con compras y hacen falta 10.

**P8.7 ¿Para qué `random_state` y `n_init=10`?**
KMeans empieza con centros al azar. `random_state` hace que el resultado se pueda repetir, y `n_init=10` lo prueba con 10 comienzos distintos y se queda con el mejor (`segmentacion.py:194`).

**P8.8 ¿Un grupo de KMeans es un segmento comercial?**
No. Es un grupo matemático: se describe comparando sus medias con la mediana de todos y se le pone un nombre interpretable (`segmentacion.py:217-261`), y se compara con RFM en una tabla cruzada (`:264-272`). El nombre ayuda a entenderlo, pero no lo convierte en una categoría del negocio.

### Código real

- `04_Python/segmentacion.py:154-170` — `variables_kmeans`: logaritmo y `StandardScaler`.
- `04_Python/segmentacion.py:173-214` — `kmeans_clientes`: prueba k = 2 a 5, calcula el silhouette, elige k y renumera los grupos por importe medio.
- `04_Python/segmentacion.py:264-272` — `comparar_rfm_kmeans`: tabla cruzada segmento RFM × grupo.

### Ejercicios

- **E8.1** Si se quitara `StandardScaler`, ¿qué variable mandaría en las distancias y por qué?
- **E8.2** Con la tabla de P8.6, ¿qué k se elige? ¿Por qué no se elige el k con la menor inercia (71,78 / 48,10 / 37,31 / 30,12)?

### Limitaciones que conviene decir antes de que pregunten

- Solo se ha podido calcular con datos sintéticos; con los de PRUEBA sale NO CALCULABLE.
- Un silhouette de 0,37 indica una separación moderada, no grupos muy claros.
- Los números de grupo de KMeans no significan nada: se renumeran de más a menos importe medio para que siempre salgan igual (`segmentacion.py:206-213`).

---

## 9. Predicción de la demanda

### Preguntas probables

**P9.1 ¿Qué se predice?**
Los pares de demanda (pedidos no cancelados) de cada modelo en cada mes (`prediccion.py:4-5` y `:39-60`). Solo se usan meses completos anteriores a la fecha de corte, y un mes sin pedidos dentro del periodo cuenta como 0.

**P9.2 ¿Qué variables de entrada usa?**
Los pares del mes anterior, la media de los tres meses anteriores, el mes del año como seno y coseno y el modelo en columnas de 0 y 1 (one-hot con `drop_first`) (`prediccion.py:36` y `:63-82`). Todas se conocen antes de que empiece el mes que se predice.

**P9.3 ¿Qué es el baseline y para qué sirve?**
Un método base muy simple: el mes que viene se piden los mismos pares que este (`prediccion.py:195-196`). Es obligatorio porque, sin él, no se sabe si el modelo de machine learning aporta algo.

**P9.4 ¿Cómo separáis entrenamiento y prueba?**
Por fecha, nunca al azar: los 3 primeros meses son historial (no tienen 3 meses previos), los últimos 3 son evaluación y los del medio, entrenamiento (`prediccion.py:85-95`; `config.py:229`). Con los sintéticos: entrenamiento de 2025-08 a 2026-07 y evaluación de 2026-08 a 2026-10.

**P9.5 ¿Qué es la fuga de información y cómo la evitáis?**
Usar al entrenar algo que no se sabría en el momento de predecir: el propio mes, meses futuros o la variable objetivo. Aquí las entradas salen de `shift(1)`, `shift(2)` y `shift(3)` del mismo modelo (`prediccion.py:69-74`), la regresión se entrena solo con el conjunto de entrenamiento (`:182` y `:186`) y el mes sin terminar se quita (`:48-51`). Lo comprueban `test_el_mes_objetivo_no_es_una_entrada` y `test_agosto_septiembre_octubre_no_entrenan`.

**P9.6 ¿Qué son MAE y RMSE?**
MAE es la media de los errores en valor absoluto: «de media me equivoco en tantos pares» (`prediccion.py:98-102`). RMSE es la raíz de la media de los errores al cuadrado: un error grande pesa mucho más que varios pequeños (`:105-109`).

**P9.7 ¿Qué salió?**
Con los sintéticos: baseline MAE 25,03 y RMSE 37,42; regresión MAE 26,28 y RMSE 36,15. La regresión mejora solo en RMSE y es peor en MAE: «solo en una métrica: RMSE sí, MAE no» (`...\referencia\simplificado\sintetico\metricas_prediccion.csv`). Hay que decirlo así: no mejora claramente al baseline.

**P9.8 ¿Por qué una regresión lineal?**
Porque no tiene hiperparámetros que ajustar mirando la evaluación (`prediccion.py:185`), es fácil de explicar y se pueden enseñar sus coeficientes. Como una recta puede dar pares negativos, la predicción se corta en 0 (`:188-189`).

**P9.9 ¿Por qué el mes en seno y coseno?**
Para que diciembre (12) y enero (1) queden cerca, como en el calendario. Si el mes fuera un número de 1 a 12, para la regresión estarían en los dos extremos (`prediccion.py:10-11` y `:76-77`).

**P9.10 ¿Y con los datos reales?**
NO CALCULABLE: hay 0 meses completos de demanda y hacen falta al menos 12 (3 de historial, 6 o más de entrenamiento y 3 de evaluación) (`prediccion.py:167-178`; `config.py:230`).

### Código real

- `04_Python/prediccion.py:63-82` — `anadir_variables`: retardos con `shift`, media de 3 meses previos, seno y coseno y one-hot.
- `04_Python/prediccion.py:85-95` — `separar_por_fecha`: historial, entrenamiento y evaluación por mes.
- `04_Python/prediccion.py:180-214` — entrena solo con el entrenamiento, predice la evaluación y compara con el baseline.

### Ejercicios

- **E9.1** Si `separar_por_fecha` se cambiara por un `train_test_split` aleatorio, ¿qué problema habría y cómo se notaría en el MAE?
- **E9.2** Para predecir octubre de 2026 de un modelo, ¿qué dato usa el baseline y qué datos usa la regresión?

### Limitaciones que conviene decir antes de que pregunten

- La regresión no mejora claramente al baseline, y eso se dice tal cual (PY-109: «Si el modelo no mejora la referencia, comunicarlo y explicar por qué»).
- Solo hay predicción con datos sintéticos; con los reales no hay suficientes meses.
- Evaluación de solo 3 meses (36 filas): el resultado puede cambiar mucho con otros meses.

---

## 10. Streamlit: refresco de 60 s

### Preguntas probables

**P10.1 ¿Cómo se refresca cada 60 segundos?**
La función `panel` lleva `@st.fragment(run_every="60s")` (`app_dashboard.py:695-696`): Streamlit la vuelve a ejecutar sola cada 60 s mientras la página está abierta. `actualizar()` lanza un ciclo si han pasado 60 s, con 5 de margen, desde la última comprobación (`:50` y `:57-73`). No hay `time.sleep` ni bucles, que la rúbrica prohíbe (PY-135).

**P10.2 ¿Qué hace cada ciclo?**
Los cinco pasos de la rúbrica: comprueba los archivos y su huella SHA-256, lee y valida con las 12 reglas, recalcula todo con esa misma versión de los datos, publica todo o nada y lo anota en el registro (`actualizacion.py:1-21` y `:159-219`).

**P10.3 ¿Qué estados hay?**
Cuatro: CORRECTO (datos nuevos y válidos), SIN CAMBIOS (los mismos datos, recalculados), DATOS INVÁLIDOS (se leen, pero hay incidencias bloqueantes) y ERROR DE CARGA (falta un archivo o no se puede leer) (`actualizacion.py:41-45`).

**P10.4 ¿Qué es la huella y para qué sirve?**
Un SHA-256 del contenido de cada CSV y otro de todas las huellas juntas (`actualizacion.py:47-74`). Si se vuelve a exportar lo mismo, la huella no cambia y el estado es SIN CAMBIOS: la hora de la última actualización válida se mantiene (`:199-202`).

**P10.5 ¿Qué pasa si llega un CSV roto?**
No se publica ninguna cifra nueva. Se conserva el último resultado válido, pero solo se enseña si el usuario lo pide, y con el rótulo DESACTUALIZADO y su hora (`actualizacion.py:190-197` y `:216`; `app_dashboard.py:678-692`).

**P10.6 Si se crea un pedido en PostgreSQL, ¿aparece solo en el dashboard?**
No. Python solo lee los CSV: hasta que Acceso a Datos vuelva a exportarlos con el 16, los valores no cambian. Recalcular cada 60 s no es lo mismo que tener datos nuevos, y el propio dashboard lo dice (`app_dashboard.py:762-763`; `actualizacion.py:19-21`).

**P10.7 ¿Todos los KPIs salen de la misma versión de los datos?**
Sí. Se publica un único resultado con su versión, y las tablas filtradas se calculan sobre esos mismos datos publicados (`app_dashboard.py:723`). No puede haber un gráfico con un CSV nuevo y otro con uno viejo (PY-137).

**P10.8 ¿Se mantienen los filtros y la pestaña al refrescar?**
Los filtros (periodo, modelo, talla, tipo, estado y cliente) se guardan en `st.session_state` (`app_dashboard.py:92-118`) y la pestaña va en la URL con `bind="query-params"` (`:714`). Cuando llega una exportación nueva, se redibuja toda la página para actualizar las opciones de los filtros (`:699-700`). Lo prueba `test_filtros_y_pestana_se_mantienen_al_refrescar` (`tests/test_dashboard.py:242`): sigue en Productos, con el cliente 1 y la talla 40, y la tabla ABC pasa de 1 a 2 pares (PY-168).

### Código real

- `04_Python/app_dashboard.py:695-741` — `panel`, el fragmento que se repite cada 60 s.
- `04_Python/actualizacion.py:159-219` — `ciclo`: comprobar, validar, recalcular, publicar o no y anotar.
- `04_Python/app_dashboard.py:678-692` — `publicacion_visible`: el último resultado válido, rotulado como DESACTUALIZADO.

### Ejercicios

- **E10.1** Durante la demo, alguien quita la columna `id_pedido` de `lineas_pedido.csv`. ¿Qué estado sale, qué cifras ve el usuario y qué pasa cuando se repone el archivo bueno?
- **E10.2** El dashboard se queda abierto 3 minutos sin que nadie exporte nada. ¿Qué cambia en la pantalla y qué no?

### Limitaciones que conviene decir antes de que pregunten

- La exportación de `entrada_acc` es de PRUEBA, así que la procedencia sale «PRUEBA» y no «ACC · REAL» (PY-130 y PY-138). **[PENDIENTE (los tres): la exportación REAL.]**
- R1–R3 se han probado con pruebas automáticas o con CSV editados a mano (capturas `04_Python/evidencias/dashboard/refresco_1_sin_cambios.png` y `refresco_2_pedido_nuevo.png`, del 10/11), no con un alta real en Acceso a Datos durante la sesión. R6 (filtrado cruzado) tiene su prueba automática: `test_filtrado_cruzado_R6` (`tests/test_dashboard.py:275`).
- El caso K está hecho: el 13/11 el dashboard estuvo abierto en Edge tres ciclos de 60 s sin tocarlo, con las cifras iguales y el registro de cada comprobación (`04_Python/evidencias/dashboard/caso_k_*`). Con datos de PRUEBA.

---

## 11. Odoo [PENDIENTE (Berme)]

> **Estado:** no hay ninguna evidencia de Odoo. La carpeta `05_Odoo/` solo tiene la lista de tareas, el borrador del recorrido y la plantilla de su `README.md`; no hay instalación documentada, capturas, exportaciones ni backup, y el conector de Berme está desactivado. Todo lo de esta sección es **[PENDIENTE (Berme)]** (lista de tareas en `05_Odoo/CHECKLIST_ODOO_BERME.md`). No inventéis pantallas, números de pedido ni resultados: si preguntan, se dice que está pendiente y qué falta.

### Lo que pide la rúbrica

| Requisito | Qué pide |
|---|---|
| IM-SGE-06 y 08 | Instalar, configurar y adaptar Odoo en una máquina virtual con Ubuntu, documentado y operativo |
| IM-SGE-09 | Compañía y perfiles: comercial, producción, almacén y administración |
| IM-SGE-10 y 11 | Clientes y contactos; oportunidades de CRM si entra en el alcance |
| IM-SGE-12 | Presupuesto y pedido de venta con líneas, cantidades, variantes y condiciones: la referencia comercial del pedido Custom |
| IM-SGE-13 | Fabricación (MRP): productos fabricados, listas de materiales y órdenes de fabricación, sin un módulo propio |
| IM-SGE-14 y 15 | Inventario y entrega si se han trabajado; facturación o su simulación documentada |
| IM-SGE-16 y 17 | Trazabilidad del mismo pedido con capturas o exportaciones; Odoo como núcleo de una venta realista |
| IM-COM-16 y 24 | ERP configurado con su copia o backup; el punto 4 de la memoria |
| RA1–RA4 | Verificar el entorno, implantar, exportar datos e informes, adaptar y documentar operaciones e incidencias |
| IM-SGE-05 | Ruta MTO: opcional, como ampliación |

### Preguntas probables (respuestas de concepto; lo nuestro se completa cuando haya evidencias)

**P11.1 ¿Qué papel tiene Odoo en el proyecto?**
Es el núcleo del negocio: la venta empieza ahí y de ella salen la fabricación, la entrega y la factura (IM-SGE-07 y 17). PostgreSQL con Java y PSP son módulos académicos y auxiliares: no sustituyen a Ventas ni a Fabricación de Odoo (IM-PSP-05).

**P11.2 ¿Qué diferencia hay entre un presupuesto y un pedido de venta?**
El presupuesto es la oferta que se envía al cliente; cuando el cliente la acepta y se confirma, pasa a ser pedido de venta. En NOVA: **[PENDIENTE (Berme): el presupuesto y el pedido SO024, con sus capturas]**.

**P11.3 ¿Qué son las variantes de un producto?**
Un producto base (Runner X) con atributos, por ejemplo la talla de la 38 a la 46 y el color, que generan una variante por combinación. Cada variante puede tener su referencia interna, que es donde encajaría nuestro SKU. En NOVA: **[PENDIENTE (Berme): Runner X con sus variantes]**.

**P11.4 ¿Qué es una lista de materiales y una orden de fabricación?**
La lista de materiales dice qué componentes hacen falta para fabricar un producto; la orden de fabricación es la orden de producir una cantidad consumiendo esos componentes. En NOVA: **[PENDIENTE (Berme): lista de materiales y orden de fabricación de SO024]**.

**P11.5 ¿Qué es la ruta MTO?**
Fabricar bajo pedido (make to order): confirmar la venta genera la necesidad de fabricar. El enunciado la deja como ampliación, «no como requisito cerrado» (IM-SGE-05).

**P11.6 ¿Cómo se relaciona Odoo con PSP?**
PSP procesa una copia exportada del pedido y su ficha tiene que poder relacionarse con la referencia de Odoo (IM-PSP-10 y 29). Hoy el CSV sale de PostgreSQL con el 15, no de Odoo; falta la exportación desde Odoo y la tabla de equivalencias.

**P11.7 ¿Qué usuarios y roles hay que configurar?**
Comercial, producción, almacén y administración, «cuando proceda» (IM-SGE-09). No son los mismos que los roles de Java (administrador, comercial y trabajador): cada sistema tiene los suyos.

**P11.8 ¿Qué hay que entregar de Odoo?**
La instancia o máquina virtual, una copia o backup o evidencias suficientes para reproducir la configuración (IM-COM-16), y el capítulo 4 de la memoria (IM-COM-24).

### Material real que existe (no son evidencias de funcionamiento)

- `05_Odoo/recorrido-manual-odoo.md:1-20` — borrador de un recorrido manual PostgreSQL → CSV → Odoo. Dice expresamente que el 10/11 no se pudo comprobar Odoo desde este ordenador.
- `06_Intermodular/SO024/caso-comun-SO024.md`, apartado 1 — los siete datos de SO024 que hay que acordar, entre ellos el SKU y el número de pedido en Odoo.
- `servidor-admin/odoo.js` (de Berme, integrado con su autoría en `654ad8b`): un conector con la API JSON-2 de Odoo que lee la clave de `ODOO_API_KEY` y espera como mucho 15 s (`odoo.js:33`). Está **desactivado** mientras falte `ODOO_URL`, `ODOO_DB` u `ODOO_API_KEY` (`odoo.js:3-23`), y la consola lo dice al arrancar (`servidor.js:473`). Es código; no se ha probado contra ningún Odoo. La única prueba es que se queda desactivado sin configuración (`test:portal`).
- `servidor-admin/pedidos.js` (de Berme): rutas para crear pedidos y enviarlos a Odoo. **No se montan** (`pedidos.js:1-11` explica por qué). **[POR DECIDIR (los tres): cómo integrarlas cuando haya Odoo.]**

### Ejercicios

- **E11.1** Según `06_Intermodular/SO024/caso-comun-SO024.md`, ¿qué datos tenéis que acordar los tres antes de crear SO024 en Odoo, y en qué script de PostgreSQL se usa cada uno?
- **E11.2** El SKU de PostgreSQL tiene la forma `NOVA-<variante>-<talla>` (`18_datos_so024.sql`). ¿Qué dos opciones hay para que la ficha de PSP se pueda relacionar con el pedido de Odoo?

### Limitaciones que conviene decir antes de que pregunten

- Todo el bloque de Odoo está pendiente: es la mitad del recorrido de SO024.
- La frontera entre el ERP y el subsistema auxiliar sí está explicada (`03_PSP/README.md`, «Relación con PostgreSQL y Odoo»).
- **[DUDA PARA EL PROFESOR (D4 y D5): alcance de CRM, fabricación, inventario y facturación, formato del backup y si «SO024» tiene que verse tal cual en Odoo.]**

---

## 12. Interfaces

### Preguntas probables

**P12.1 ¿Qué partes tiene la web?**
Las cinco que pide el enunciado (IM-INT-04): inicio, catálogo con 100 modelos (`01_Interfaces/cliente/js/modelos.js`), ficha de cada modelo con precio, descripción y tallas, el servicio Custom (`index.html:267`) y una parte corporativa («Nuestra visión») con contacto. El menú está en `index.html:31-36`.

**P12.2 ¿Cómo la habéis hecho responsive?**
Con CSS Grid y media queries: el catálogo tiene 4 columnas en escritorio (`css/inicio.css:617-622`) y pasa a 2 por debajo de 760 px (`:649` y `:660-663`); los títulos usan `clamp()` para ajustar el tamaño (`:144`) y las barras usan `flex-wrap`. Se probó en 11 anchos de 320 a 1440 px sin desplazamiento horizontal (H12).

**P12.3 ¿Qué habéis hecho para la accesibilidad?**
Un enlace «Saltar al escaparate» (`index.html:23`), navegación con `aria-label`, una etiqueta en cada campo, las tallas agrupadas con `fieldset` y `legend` (`:348-349`), mensajes con `role="status"` y `aria-live` (`:366` y `:139`), foco visible (`css/inicio.css:30-32`) y menos animaciones si el usuario lo pide (`:545-555`). axe no da violaciones, hay 212/212 contrastes AA y Lighthouse da 100 en accesibilidad (11/11).

**P12.4 ¿Qué estándar seguís y por qué?**
WCAG 2.1 nivel AA, que es el que comprueban axe y Lighthouse (`01_Interfaces/evidencias/web/README.md:8-9`). Sirve para que la web la pueda usar más gente: con teclado, con lector de pantalla o con poca vista (contraste mínimo de 4,5:1 en texto normal).

**P12.5 ¿Cómo funciona el formulario Custom?**
El HTML valida lo básico: campos obligatorios, formato del email y cantidades enteras de 0 en adelante (`index.html:302-358`). El JavaScript suma los pares de todas las tallas al escribir (`js/custom.js:17-27`); al enviar, si no hay ningún par avisa y pone el foco en la primera talla (`:34-38`), y si todo está bien enseña el resumen marcado como SIMULACIÓN (`:48-51`).

**P12.6 ¿Por qué el formulario Custom no envía nada?**
Porque el enunciado pide «un formulario o prototipo de solicitud» (IM-INT-07) y no obliga a tener un backend. El pedido Custom de verdad se registra en Odoo y en Java. `preventDefault()` evita el envío (`js/custom.js:32`) y el texto lo dice claramente: «No se ha enviado ningún dato».

**P12.7 Entonces, ¿qué es la tienda online?**
Una ampliación que ningún enunciado pide: cuentas de cliente, carrito, pago simulado y «Mis pedidos», conectada a PostgreSQL a través del servidor y de las funciones del script 20. Conviene presentarla como ampliación: AD-136 dice que se valora más la coherencia que añadir cosas no pedidas.

**P12.8 ¿Cómo evitáis el doble clic al pagar?**
El navegador desactiva los botones mientras espera la respuesta (`01_Interfaces/cliente/js/tienda.js:851` y `:900`) y cada compra lleva una clave aleatoria creada al abrir el checkout (`:817`); si la misma compra llega dos veces, la base devuelve el mismo pedido (`20_tienda_web.sql:226-237`).

**P12.9 ¿De dónde saca los datos el panel de administración?**
De la API `/api/admin/...` del servidor (`01_Interfaces/admin/script.js:62-100`), que lee PostgreSQL en transacciones de solo lectura (`servidor-admin/bd.js:61-72`, con el ayudante `enTransaccion` de `:40-56`). La única escritura es «Marcar en reparto», con su propio rol (`bd.js:80-83`).

### Código real

- `01_Interfaces/cliente/js/custom.js:17-51` — suma de pares, aviso si no hay ninguno y mensaje de simulación.
- `01_Interfaces/cliente/css/inicio.css:649-666` — la media query que pasa el catálogo de 4 a 2 columnas.
- `01_Interfaces/cliente/index.html:348-366` — `fieldset` de tallas con su `legend` y resultado con `role="status"`.

### Ejercicios

- **E12.1** Un usuario escribe −3 en la talla 40, deja vacías las demás y pulsa «Simular envío». ¿Quién lo para y dónde? ¿Y si escribe 0 en todas?
- **E12.2** En un móvil de 360 px, ¿cuántas columnas tiene el catálogo y qué regla CSS lo decide? ¿Qué más cambia por debajo de 370 px?

### Limitaciones que conviene decir antes de que pregunten

- **[PENDIENTE (los tres): la prueba de usabilidad con personas (RA4, CE i)].** El procedimiento está preparado en `01_Interfaces/memoria/PROCEDIMIENTO_USABILIDAD.md`. La estrategia de pruebas (RA8) está en `01_Interfaces/memoria/ESTRATEGIA_PRUEBAS_INTERFACES.md`.
- El formulario Custom no pide la fecha objetivo ni enseña un número de pedido (el enunciado dice «Puede mostrarse o simularse»).
- Runner X, el modelo de SO024, no está en el catálogo de la web.
- Por debajo de 370 px se oculta el enlace «Nuestra visión» del menú (`css/inicio.css:534-536`); la sección sigue ahí bajando por la página.
- En móvil, axe avisa de `scrollable-region-focusable` en las tablas del panel; el panel y el portal cargan Lucide (y el panel, Chart.js) de internet.
- Las baterías de la web se repitieron el 13/11 sobre el código final: 136/136, 114/114, 81/81 y la compra 139/139 (`06_Intermodular/evidencias/regresion-final/05_web/`). Lighthouse es del 11/11.

---

## 13. Seguridad

### Preguntas probables

**P13.1 ¿Cómo guardáis las contraseñas?**
Como hash bcrypt con sal: `crypt(p_password, gen_salt('bf'))` de pgcrypto (`02_funciones.sql:439`; los clientes de la web en `20_tienda_web.sql:134-135`). Nunca en texto plano, y ningún rol de la aplicación puede leer la columna `password_hash` (`07_seguridad.sql:99-101`).

**P13.2 ¿Se puede descifrar una contraseña guardada con bcrypt?**
No. Es un hash de un solo sentido, no un cifrado. Para comprobarla se vuelve a calcular `crypt(lo_que_escribe_el_usuario, hash_guardado)` y se compara con el hash (`02_funciones.sql:25`); la sal va dentro del propio hash.

**P13.3 ¿Por qué el login de clientes calcula un hash aunque el correo no exista?**
Para tardar lo mismo en los dos casos, y que el tiempo de respuesta no delate qué correos están registrados (`20_tienda_web.sql:166-170`). El mensaje también es siempre el mismo: «Correo o contraseña incorrectos».

**P13.4 ¿Cómo funcionan las sesiones web?**
Al entrar, el servidor crea un token aleatorio de 32 bytes (`servidor-admin/sesiones.js:53`), lo guarda en memoria con los datos del usuario y se lo da al navegador en una cookie que caduca a las 2 horas (`:20` y `:55`). La contraseña no se guarda en la sesión.

**P13.5 ¿Qué significan HttpOnly y SameSite=Strict?**
HttpOnly: el JavaScript de la página no puede leer la cookie, y eso protege el token si alguien consigue inyectar código (XSS). SameSite=Strict: el navegador no envía la cookie en peticiones que vienen de otras webs, y eso protege de CSRF (`sesiones.js:26-30`).

**P13.6 ¿Por qué hay dos cookies de sesión?**
Una para el panel (`sesion_nova`, ruta `/`) y otra para la tienda (`sesion_tienda`, ruta `/api/tienda`), cada una con su propio almacén: una sesión de cliente no sirve en el panel, ni la de un trabajador para comprar (`sesiones.js:79-80`).

**P13.7 ¿Cómo limitáis los intentos de login?**
Tras 5 fallos seguidos con el mismo usuario, el servidor responde 429 durante 5 minutos sin mirar la contraseña, aunque sea la buena (`servidor-admin/intentos.js:11-12` y `:41-43`; `servidor.js:120-124`). Se cuenta por nombre, exista o no la cuenta, y un acierto pone el contador a cero (`servidor.js:134`). Vale igual para el administrador y para el trabajador, porque entran por el mismo login. La tienda hace lo mismo con el correo (`servidor-admin/tienda.js:207-211`).

**P13.8 ¿Qué roles de PostgreSQL hay y para qué sirve cada uno?**
Los usuarios con LOGIN no tienen permisos propios (NOINHERIT): `java_nova`, `web_nova` y `tienda_nova`. Al conectarse pasan con `SET ROLE` a un rol sin login con los permisos justos: `nova_admin`, `nova_comercial` o `nova_trabajador` (Java), `panel_lectura` o `panel_reparto` (panel), `portal_trabajador` (portal) y `tienda_web` (tienda) (`17_usuario_java.sql:41-48`, `19_usuario_web.sql:111`, `23_portal_trabajador.sql:242`, `servidor-admin/bd.js:71`, `:81`, `:96`, `:100` y `:153`).

**P13.9 ¿Qué diferencia hay entre un rol de la aplicación y un rol de PostgreSQL?**
El rol de la aplicación (administrador, comercial o trabajador) es del negocio y está en la tabla `roles`; el de PostgreSQL es un conjunto de permisos de la base. Java los une con `Sesion.rolPostgres` (`Sesion.java:110-121`). Y `admin.demo` no es un rol de PostgreSQL, sino una fila de la tabla `usuarios` (`20_tienda_web.sql:35-42`). Es lo que pide explicar AD-67.

**P13.10 ¿Cómo se protegen el panel y el portal en cada petición?**
`comprobarRol` comprueba la sesión y el rol, y vuelve a mirar en la base que la cuenta sigue activa y sigue teniendo ese rol; si no, borra la sesión (`servidor.js:187-203`). `soloRol` la convierte en un filtro de Express con 401 o 403 (`:205-219`), y de ahí salen `soloAdministrador` para `/api/admin` y `soloTrabajador` para `/api/trabajador` (`:221-225`). Además, las lecturas del panel van en una transacción READ ONLY con `panel_lectura` (`bd.js:40-56`), y el servidor solo escucha en 127.0.0.1 (`servidor.js:27`).

### Código real

- `02_Acceso_Datos/sql/02_funciones.sql:1-39` — `iniciar_sesion`: comprueba la contraseña con bcrypt y deja el usuario firmado con HMAC para esa transacción.
- `servidor-admin/sesiones.js:23-56` — opciones de la cookie y creación de la sesión con un token aleatorio.
- `servidor-admin/bd.js:61-72` — transacción de solo lectura con `SET LOCAL ROLE panel_lectura` (la abre `enTransaccion`, `:40-56`).

### Ejercicios

- **E13.1** Alguien prueba 5 contraseñas malas de `admin.demo` y en el sexto intento escribe la buena. ¿Qué responde el servidor? ¿Llega a comprobar la contraseña?
- **E13.2** Un trabajador conectado con `nova_trabajador` ejecuta `SELECT set_config('nova.id_usuario', '1', true);` para firmar la auditoría como el administrador. ¿Qué queda en `log_eventos`?

### Limitaciones que conviene decir antes de que pregunten

- Las sesiones y los intentos están en memoria: si se reinicia el servidor se pierden (`sesiones.js:16`).
- La cookie no lleva `Secure` porque el servidor usa HTTP en 127.0.0.1. En producción haría falta HTTPS y `Secure`.
- El límite de intentos es por nombre de usuario, no por IP: alguien podría probar una misma contraseña con muchos usuarios.
- Java no tiene límite de intentos y guarda la contraseña en memoria durante la sesión.
- El pago es simulado y el resultado lo elige el navegador (`servidor-admin/tienda.js:284-285`); en una tienda real lo daría la pasarela de pago al servidor.
- Los permisos de la tienda son por columnas, no por filas: que cada cliente vea solo lo suyo lo asegura el servidor, que filtra por el id de su sesión (`20_tienda_web.sql:27-29`).
- `marcar_pedido_en_reparto` confía en el id de usuario que le pasa el servidor, que lo saca de la sesión, no del navegador (`22_reparto_panel.sql:46-67`).
- El recibo por correo con Resend nunca se ha enviado con una clave real; Ethereal es solo para desarrollo.

---

## 14. Git

### Preguntas probables

**P14.1 ¿Cómo os organizasteis con Git?**
Con ramas por persona y tarea (`feature/omar-*`, `feature/AlvaroBaz` y `feature/berme`), una rama de integración donde se fusionan (`6439bbc`, `7715f83` y `150d02f`), la candidata final `integracion/candidata-2` y worktrees para tener varias ramas abiertas a la vez en carpetas distintas.

**P14.2 ¿Qué es un worktree?**
Otra carpeta de trabajo del mismo repositorio con otra rama. Comparten el historial: en un worktree, `.git` es un archivo que apunta a la carpeta `.git/worktrees/...` del repositorio principal. Sirve para no tener que cambiar de rama con trabajo a medias (RT-GIT-01). `git worktree list` los enseña todos.

**P14.3 ¿Qué hace un merge?**
Une dos historias. Si las dos ramas han avanzado, crea un commit de fusión con dos padres. Los commits de la rama fusionada no cambian: conservan su autor y su fecha.

**P14.4 ¿Cómo se ve quién hizo qué?**
Con `git log`, `git shortlog -sn` y `git blame`. Por ejemplo, `git log 7715f83^1..7715f83^2` lista los 25 commits que entraron con esa fusión, todos con su autor original (`Alvarobaz`), aunque el commit de fusión lo firme otra persona (`omar1676`). Lo mismo pasa con los dos commits del portal de Berme: entraron con `git cherry-pick -x` (`7341001` y `654ad8b`), así que conservan su autor y su fecha del 11/11 y llevan la línea «cherry picked from commit …». En la rama final, `git shortlog -sn` da 74 commits de `omar1676`, 25 de `Alvarobaz` y 8 de `Ivan Bermejo`. El número de commits no mide la contribución: **[PENDIENTE (los tres): el reparto real, punto 9 de la memoria]**.

**P14.5 ¿Qué no se sube y por qué?**
`.env`, `conexion.properties`, los `.class`, las salidas, los logs y el driver JDBC (`.gitignore:5-8`, `:11-14`, `:24`, `:37` y `:40`). Las contraseñas de las cuentas de la base se piden por teclado al ejecutar los scripts (`17_usuario_java.sql:35`) y en el repositorio solo hay plantillas vacías (`servidor-admin/.env.example` y `02_Acceso_Datos/java/conexion.properties.ejemplo`).

**P14.6 ¿Qué convención de commits seguís?**
Al principio, la del plan del equipo (`feat(web): …`, `test(psp): …`; se ve en los commits que entraron con `150d02f`). Ahora, mensajes en inglés, en imperativo y sin prefijo, por ejemplo `4203fe7 Note the known failure of the PSP quick check`.

**P14.7 ¿Qué es un conflicto y cómo se resuelve?**
Pasa cuando dos ramas cambian las mismas líneas y Git no sabe con cuál quedarse: marca el archivo con `<<<<<<<`, `=======` y `>>>>>>>`. Se edita a mano, se prueba, se hace `git add` y se termina la fusión con un commit.

**P14.8 ¿Qué falta por publicar?**
La candidata final (`integracion/candidata-2`) tiene sus commits en local, sin cambios pendientes, encima de la candidata publicada el 12/11 (`4203fe7`). Falta llevarla a `main` con una Pull Request revisada por Álvaro y Berme y fusionada con «Create a merge commit», sin force-push. Comprobad el estado del remoto antes de la defensa.

### Código real (historial)

- `7715f83` — fusión de la rama `feature/AlvaroBaz` (25 commits con su autor original).
- `150d02f` — fusión de la rama de Berme (6 commits con su autor original).
- `.gitignore:4-8` y `:35-37` — los archivos con credenciales que no se suben.

### Ejercicios

- **E14.1** ¿Qué comando usarías para ver solo los commits que entraron con la fusión `7715f83`, y quién es su autor?
- **E14.2** Alguien hace commit de `servidor-admin/.env` por error. ¿Lo impide el `.gitignore`? Si ya se ha subido, ¿qué hay que hacer?

### Limitaciones que conviene decir antes de que pregunten

- En el historial solo hay una fusión hecha con Pull Request (`558cab3`); las demás se hicieron en local.
- El reparto del plan del equipo (RT) no coincide del todo con quién hizo cada cosa. El punto 9 de la memoria tiene que contarlo como fue, sin inventar.
- Contar commits no mide el trabajo: hay revisión, pruebas y trabajo fuera del repositorio (Odoo).

---

## 15. Integración: el caso SO024

### Preguntas probables

**P15.1 ¿Qué es SO024?**
El pedido del enunciado que hace de hilo conductor: «SO024 · Club Halcones · Modelo Runner X · 40 pares · tallas 38-46 · diseño personalizado» (IM, p. 5). Es el mismo pedido en todos los bloques, con la misma referencia.

**P15.2 ¿Qué recorrido sigue?**
Web (solicitud Custom simulada) → Odoo (pendiente) → PostgreSQL (el 18 carga el cliente y Runner X) → Java (se crea y se confirma SO024) → el 15 exporta el CSV → PSP genera la ficha → el 16 exporta los cinco CSV → Python y el dashboard (`06_Intermodular/SO024/caso-comun-SO024.md`, apartado 2).

**P15.3 ¿Qué resultados hay?**
**[PROVISIONAL]** El 13/11, sobre el código final: 40 pares, 9 líneas y 3.996,00 €; cada talla baja una sola vez (8, 7, 5, 4, 3, 4, 5, 6 y 8); la auditoría tiene el ALTA y el CAMBIO_ESTADO de `admin.demo`; el 15 exporta 9 filas y 40 pares; PSP termina con código 0 y 9 tallas, y Python lo cuenta como un solo pedido (`06_Intermodular/evidencias/regresion-final/06_so024_provisional/00_cadena.txt` y `03_PSP/evidencias/so024_provisional/`).

**P15.4 ¿Por qué es provisional?**
Porque faltan siete datos por acordar entre los tres: el reparto por talla, el color, el precio, el stock inicial, el texto de la personalización, el SKU en Odoo y el número de pedido en Odoo (`06_Intermodular/SO024/caso-comun-SO024.md`, apartado 1). El 18 los recibe con `-v` y, si falta alguno, no inserta nada.

**P15.5 ¿Cómo se integran los bloques?**
Con ficheros CSV y procedimientos documentados, sin sincronización automática. El enunciado lo permite (IM-ITG-07) y dice que la integración se evalúa «por la coherencia de los datos y del flujo, no por el uso de una arquitectura compleja» (IM-ITG-08).

**P15.6 ¿Qué datos comparten todos los bloques?**
La referencia del pedido, el cliente, el producto y la variante, la cantidad y el estado de cada bloque (IM-ITG-10 a 14). PostgreSQL y PSP usan `SO024`; la web no enseña ningún número porque es una simulación.

**P15.7 ¿Qué comprueba el 15 antes de exportar?**
Que el pedido existe, que está confirmado, que suma exactamente 40 pares y que no repite tallas. Si algo falla, se para y el CSV anterior se queda como estaba (`15_exportar_fabricacion.sql:102-160`).

**P15.8 ¿Qué haría falta para una integración de verdad?**
(IM-ITG-06) Que Odoo fuera el origen del pedido y lo exportara él, o con su API; una tabla de equivalencias de SKU y número de pedido; que la exportación para Python fuera automática; y que PSP leyera pedidos de una cola en vez de un archivo. El conector de Berme (`servidor-admin/odoo.js`) va en esa dirección, pero está desactivado y sin probar contra ningún Odoo.

### Código real

- `02_Acceso_Datos/sql/18_datos_so024.sql:1-40` — explica que el 18 prepara el cliente, Runner X y sus nueve SKU, pero no crea el pedido: SO024 se crea en Java.
- `02_Acceso_Datos/sql/15_exportar_fabricacion.sql:197` — el `\copy` que escribe `fabricacion_psp.csv` con las ocho columnas, solo de un pedido confirmado.
- `03_PSP/ProcesadorPedidosCustom.java:218-219` — la ficha lleva la referencia del pedido en su nombre: `ficha_taller_SO024.txt`.

### Ejercicios

- **E15.1** En Java se crea SO024 pero se olvida confirmarlo, y se ejecuta el 15. ¿Qué pasa? ¿Qué recibe PSP?
- **E15.2** ¿Por qué Python enseña SO024 como un solo pedido aunque tenga 9 líneas? Señala dónde se hace.

### Limitaciones que conviene decir antes de que pregunten

- Los datos de SO024 son provisionales. **[PENDIENTE (los tres): acordar los 7 datos y hacer el SO024 oficial desde la ventana Java, en la base del equipo.]**
- En la prueba del 13/11, Java creó SO024 con los métodos de «Nuevo pedido» desde un lanzador (`SO024Provisional.java`), no desde la ventana.
- Runner X no está en el catálogo de la web y Odoo está pendiente: falta la mitad del recorrido.
- El 15 exige exactamente 40 pares (`15_exportar_fabricacion.sql:146-149`): sirve para este caso, no para cualquier pedido.
- `entrada_acc` sigue siendo una exportación de PRUEBA. **[PENDIENTE (los tres): la exportación REAL.]**

---

## 16. Portal del trabajador (ampliación, de Berme)

El portal es de Berme: sus dos commits (`7341001`, las páginas y las rutas; `654ad8b`, el conector de Odoo y las rutas de pedidos) entraron con `cherry-pick -x` y conservan su autor y su fecha del 11/11. Se integró en `servidor-admin`, detrás del login único y con el rol `portal_trabajador` del script 23. **Es una ampliación:** ningún enunciado lo pide, y el inventario y la fabricación «de verdad» siguen siendo de Odoo.

### Preguntas probables

**P16.1 ¿Para qué sirve el portal y qué hace que no haga el panel?**
Es para el taller y el almacén. Tiene cuatro páginas (`01_Interfaces/trabajador/`): Resumen (por preparar, en preparación, SKU con menos de 5 pares y pedidos de hoy), Pedidos con «Avanzar estado» (`confirmado` → `en_preparacion` → `enviado` → `entregado`), Inventario con «Guardar» la cantidad, y Personalizados. El panel de administración solo lee (salvo «Marcar en reparto»); el portal cambia estados y stock, pero solo con dos funciones del script 23.

**P16.2 ¿Cómo se entra?**
Por el login único, `/login.html` (`servidor.js:110-155`): `iniciar_sesion` comprueba la contraseña con bcrypt y el rol de la tabla `roles` decide adónde va cada uno (`PANELES`, `:39-42`): el administrador, a `/admin.html`; el trabajador, a `/trabajador/trabajador.html`. Un rol sin panel web (el comercial) recibe 403 y no se le crea sesión (`:136-143`). La cookie es la misma del panel (`sesion_nova`) y el límite de 5 intentos vale igual.

**P16.3 ¿Qué impide que un trabajador use el panel, o un administrador el portal?**
`soloRol` (`servidor.js:205-219`) crea `soloAdministrador` y `soloTrabajador` (`:221-225`): sin sesión, 401; con otro rol, 403. Por debajo, `comprobarRol` (`:187-203`) vuelve a mirar en la base en cada petición: si la cuenta se desactiva o le cambian el rol, la sesión se borra en ese momento. Las páginas del portal también están protegidas (`protegerPortal`, `:408-416`).

**P16.4 ¿Con qué usuario de PostgreSQL se conecta y a qué rol pasa?**
Con `web_nova`, el mismo del panel. En cada transacción del portal hace `SET LOCAL ROLE portal_trabajador` (`bd.js:95-102`): las lecturas, en una transacción de solo lectura (`consultarComoTrabajador`), y los dos cambios en otra (`cambiarComoTrabajador`). `web_nova` no hereda los permisos del rol: solo puede pasar a él (`23_portal_trabajador.sql:242`, `WITH INHERIT FALSE, SET TRUE`).

**P16.5 ¿Qué puede hacer `portal_trabajador`?**
Leer solo las columnas que enseña el portal (`23_portal_trabajador.sql:219-234`): nada de `password_hash`, `dni`, `email`, `telefono`, `direccion_entrega` ni `log_eventos`. Y ejecutar dos funciones (`:237-238`). No puede escribir en ninguna tabla (`:214`).

**P16.6 ¿Cómo avanza un pedido?**
`avanzar_pedido_trabajador` (`23_portal_trabajador.sql:52-131`) comprueba que el usuario existe, está activo y es trabajador (`:69-79`), bloquea el pedido con `FOR UPDATE` (`:83-87`), solo deja dar un paso (`:93-106`), firma `nova.id_usuario` igual que `iniciar_sesion` (`:110-116`), hace el UPDATE (`:118-120`) y deja la variable como estaba (`:123`). Así el trigger de auditoría apunta el `CAMBIO_ESTADO` a nombre del trabajador.

**P16.7 ¿Avanzar un pedido toca el stock?**
No. El stock se descuenta al confirmar, y el trigger solo salta al pasar a `confirmado` (`03_triggers.sql:31`). La prueba 9b de `test:portal` lleva un pedido hasta `entregado` y comprueba que el stock no cambia.

**P16.8 ¿Y el inventario?**
`ajustar_existencias_trabajador` (`23_portal_trabajador.sql:136-196`) hace la misma comprobación del usuario, solo acepta una cantidad de 0 a 99999 (`:165-166`), firma y hace el UPDATE. El `CHECK (cantidad >= 0)` de `existencias` sigue ahí (`esquema:61`), y `trg_auditar_existencias` apunta el `CAMBIO_STOCK` a nombre del trabajador (`08_auditoria.sql:101-105`; prueba 11 de `test:portal`).

**P16.9 ¿Qué ha pasado con Odoo y con `pedidos.js`?**
El conector (`odoo.js`) está desactivado mientras falten `ODOO_URL`, `ODOO_DB` y `ODOO_API_KEY` (`odoo.js:3-23`), y la consola lo dice al arrancar (`servidor.js:473`). Las rutas de `pedidos.js` no se montan (`pedidos.js:1-11`): crearían pedidos sin login ni rol, escriben en `pedidos` y `log_eventos` directamente y necesitan un Odoo que no está. No se ha probado contra ningún Odoo.

**P16.10 ¿Qué pruebas tiene?**
`npm run test:portal`, 24/24: el login de cada rol, el comercial denegado, el límite de intentos, desactivar o cambiar el rol con la sesión abierta, el logout, la caducidad, 403 en todo `/api/admin/` para el trabajador, avanzar paso a paso, dos clics a la vez, parámetros y cookies manipulados, los permisos en PostgreSQL, la auditoría y el conector desactivado. Además, el SQL del 23 (50/50) y el recorrido en Edge, en escritorio y en móvil y con axe (82/82). Todo del 13/11, en `06_Intermodular/evidencias/regresion-final/` (capturas en `01_Interfaces/evidencias/portal-trabajador/capturas/`).

### Código real

- `02_Acceso_Datos/sql/23_portal_trabajador.sql:52-131` — `avanzar_pedido_trabajador`: comprueba el rol, bloquea el pedido, un solo paso y la firma para la auditoría.
- `servidor-admin/servidor.js:187-225` — `comprobarRol`, `soloRol`, `soloAdministrador` y `soloTrabajador`.
- `servidor-admin/rutas-trabajador.js:77-103` — `PATCH /api/trabajador/pedidos/:id/estado`: valida la petición y llama a la función con el usuario de la sesión.

### Ejercicios

- **E16.1** Dos trabajadores pulsan «Avanzar estado» a la vez sobre el mismo pedido confirmado. ¿Qué recibe cada uno y qué queda en la base? Señala la línea.
- **E16.2** Un trabajador manda `PATCH /api/trabajador/pedidos/5/estado` con `{"estado": "entregado", "idUsuario": 1}` sobre un pedido confirmado. ¿Qué pasa con el estado y con el usuario?

### Limitaciones que conviene decir antes de que pregunten

- Es una ampliación y no sustituye a Odoo. El conector y las rutas de pedidos de Berme no están activos. **[POR DECIDIR (los tres): qué se hace con `pedidos.js` cuando haya Odoo.]**
- La hoja de estilos y el logo del portal son copias idénticas de los del panel de Álvaro.
- Las sesiones están en memoria y los iconos (Lucide 1.62.0, con `integrity`) vienen de internet; sin conexión, el portal funciona sin iconos.
- La cantidad del inventario no se compara con la capacidad de la nave.
- La columna «Fecha objetivo» sale vacía («—»): ningún pedido de prueba la tiene.

---

## Anexo A. Soluciones de los ejercicios

**E1.1** Tres barreras:
- Por la función: `anadir_linea_pedido` lanza «La cantidad debe ser mayor que cero» antes del INSERT (`02_funciones.sql:167-169`).
- Por un INSERT directo: el CHECK `linea_pedido_check_1 (cantidad > 0)` (`esquema:146`) lo rechaza con un código de error 23…; Java lo traduce como «Algún dato no es válido para la base de datos» (`ConexionBD.java:178-180`).
- Por permisos: `nova_admin` no tiene INSERT en `linea_pedido` (`07_seguridad.sql:63-64`) y los otros roles tampoco; solo se puede entrar por la función.
(Fuera de la base hay más: la regla 05 de Python y el validador de PSP también rechazan cantidades de 0 o menos.)

**E1.2** El bucle de `PedidoDAO.java:83-92` llama a `buscarSku`, que lanza «No existe la talla … para ese modelo y color» con código P0001 (`:128-130`). El `catch` de `:98-103` hace `hacerRollback()` y escribe en el TXT una línea `CREAR PEDIDO | rechazado`. Resultado: ninguna fila nueva en `pedidos` ni en `linea_pedido`, y tampoco el evento ALTA de `log_eventos`: se insertó dentro de la misma transacción y se deshace con ella. En el TXT sí queda el rechazo. Por eso el TXT y `log_eventos` no tienen los mismos eventos (AD-90).

**E2.1** Cuatro barreras, de fuera a dentro:
1. Navegador: al pulsar, desactiva los botones de pago (`01_Interfaces/cliente/js/tienda.js:900`).
2. Servidor: `pg_advisory_xact_lock(idPedido)` hace que dos pagos del mismo pedido vayan uno detrás de otro (`servidor-admin/tienda.js:303`).
3. Base: `confirmar_compra_web` bloquea la fila con `FOR UPDATE` (`20_tienda_web.sql:346-354`); el segundo pago ve el pedido `confirmado` y `pagado` y sale sin hacer nada (`:361-363`).
4. Aunque se repitiera el UPDATE, el trigger solo salta si antes no estaba confirmado (`03_triggers.sql:31`) y solo descuenta líneas con `stock_descontado = false` (`02_funciones.sql:461`).
Resultado: un pago, un único descuento de stock y un solo recibo, porque solo el que lo pasa de pendiente a confirmado tiene `recienPagado` (`servidor-admin/tienda.js:307` y `:326-328`).

**E2.2** Primero salta BEFORE DELETE `trg_proteger_linea_pedido` (`03_triggers.sql:21-25`): con el pedido pendiente y sin stock descontado, la línea no está bloqueada y la deja borrar (`02_funciones.sql:381-391`). Después salta AFTER DELETE `trg_actualizar_totales` (`03_triggers.sql:2-6`), que recalcula los totales usando `OLD.id_pedido` (`02_funciones.sql:100-101`): bajan `cantidad_total` e `importe_total` (prueba D5). No se registra ningún evento de auditoría para la línea. Si el pedido estuviera confirmado, `estado_pedido <> 'pendiente'` hace que la línea esté bloqueada y salta «No se puede eliminar esta linea de pedido» (`02_funciones.sql:381-388`).

**E3.1** `confirmarPedido` hace `UPDATE … WHERE id_pedido = ? AND estado = 'pendiente'` (`PedidoDAO.java:184-188`). La segunda vez no cambia ninguna fila, así que `filas == 0` y se lanza «Solo se puede confirmar un pedido pendiente» (`:208-210`); se hace ROLLBACK y se apunta como `rechazado` en el TXT (`:212-216`). El stock no se toca. Además, el trigger solo salta al pasar a confirmado (`03_triggers.sql:31`).

**E3.2** En Java, el rol comercial no tiene `VER_AUDITORIA` en la matriz (`Sesion.java:82-87`), y `verAuditoria` llama a `comprobarPermiso` (`PedidoDAO.java:326`), que lanza «Acceso denegado» con el código 42501 (`Sesion.java:100-107`). Si alguien se salta Java, la conexión está en `nova_comercial` (por el SET ROLE) y solo `nova_admin` puede leer `log_eventos` (`07_seguridad.sql:60-61`): PostgreSQL responde «permission denied for table log_eventos». Son las pruebas F2 y F3.

**E4.1** El validador solo comprueba que la talla sea un entero positivo (`ValidadorPedidoCustom.java:181-187`), así que la deja pasar y termina con 0. El analizador comprueba el rango de 20 a 55 y lanza `DatosIncorrectosException` (`03_PSP/src/Psp/AnalizadorTallas.java:85-87`), que termina con el código 2 (`:15` y `:27-29`). El padre ve el 2 en `comprobarPaso` y termina con «PEDIDO RECHAZADO (código 2)» sin lanzar el generador (`ProcesadorPedidosCustom.java:306-309`): no hay ficha, pero sí se escribe el registro. Es la prueba 12k de `06_Intermodular/evidencias/regresion-final/02_java_psp/04_psp_pruebas.txt`.

**E4.2** `readAllBytes()` no termina hasta que el hijo cierra su salida. Si el hijo se cuelga sin terminar, el lanzador se queda parado en la línea 29 y nunca llega al `waitFor` de la 32, así que el límite de 10 s no sirve. Además, si el hijo llena stderr mientras el padre espera stdout, se bloquean los dos. `GestorProcesos` hace lo contrario: lee stdout y stderr en dos hilos (`GestorProcesos.java:116-131`), el hilo principal espera primero con límite (`:138`) y cancela con `destroy()` y `destroyForcibly()` (`:143-153`). El coordinador usa `GestorProcesos`.

**E5.1** Salta la regla 05, «Cantidad nula, cero o negativa», con gravedad recuperable (`calidad.py:188-189`). `separar` rechaza esa línea, después su pedido y, por el pedido, las otras dos líneas (`calidad.py:440-446`): se rechazan 1 pedido y 3 líneas, y el resto se publica. Lo prueba `test_un_pedido_se_analiza_entero_o_no_se_analiza` (`tests/test_calidad.py:153`).

**E5.2** La regla 02 marca como BLOQUEANTE un ID repetido donde tiene que ser único (`calidad.py:143-147`), así que no se publica ninguna cifra. Si esa regla no existiera, `cruzar(..., "many_to_one")` lanzaría un `MergeError` que se convierte en `ErrorDatos` (`analiticas.py:34-37`). Sin `validate`, el merge duplicaría las líneas de ese modelo y los pares y el importe saldrían inflados sin avisar.

**E6.1** Con [−20, 300]: ni el extremo inferior es mayor que 0 ni el superior menor que 0, así que escribe «evidencia insuficiente: el intervalo incluye 0» (`estadistica.py:195-199`). Con [120, 300]: el extremo inferior es mayor que 0, así que escribe «los datos la apoyan» (`:195-196`).

**E6.2** Con la misma semilla, el generador da siempre la misma secuencia de números aleatorios. Si en cada vuelta se sacan primero los de la muestra Custom y después los de la estándar, el resultado sale igual en cada ejecución. Si se cambiara el orden, cada muestra usaría otros números y el intervalo saldría algo distinto del guardado: igual de válido, pero no reproducible respecto a lo que ya está en los informes (lo explica el comentario de `estadistica.py:241`).

**E7.1** Reglas en orden (`segmentacion.py:96-109`): no tiene F = 0; no cumple R, F y M de 4 o más (F = 2); no cumple F ≥ 3 con R ≤ 2; no cumple F ≥ 3; no cumple R ≤ 2. Cae en el último caso: **Ocasionales** (pocas compras, pero recientes).

**E7.2** `de_venta` solo cuenta pedidos confirmados en adelante (`analiticas.py:254-256`), así que el cancelado no entra. El cliente se une igual porque se parte de todos los clientes (`segmentacion.py:54-55`): F = 0, M = 0 y la recency vacía (`:56-59`). Segmento: **Sin compras válidas** (`:98-99`).

**E8.1** Mandaría `recency_dias`: son días (decenas o cientos), mientras que `log_frequency` y `log_monetary` son números pequeños después del logaritmo. Las distancias dependerían casi solo de la recencia, y los grupos serían «compró hace poco» frente a «hace mucho». Por eso se usa `StandardScaler` (`segmentacion.py:170`).

**E8.2** Se elige k = 4, que tiene el silhouette más alto, 0,373 (`segmentacion.py:199-201`). La inercia baja siempre al añadir grupos (71,78 → 48,10 → 37,31 → 30,12): con más grupos, cada cliente queda más cerca de su centro. Si se eligiera la menor inercia, siempre ganaría el k más grande. El silhouette, en cambio, tiene un máximo.

**E9.1** Con un reparto al azar se entrenaría con meses posteriores a algunos de los de prueba: el modelo «vería el futuro» (fuga de información), el MAE de la evaluación saldría más bajo de lo que de verdad sería y la comparación con el baseline no valdría. La rúbrica lo prohíbe (PY-106). El código lo evita asignando el conjunto por mes (`prediccion.py:85-95`) y entrenando solo con el entrenamiento (`:182` y `:186`).

**E9.2** El baseline usa los pares de septiembre de ese modelo (`pares_mes_anterior`, que es `shift(1)`: `prediccion.py:70`, `:73` y `:196`). La regresión usa los pares de septiembre, la media de julio, agosto y septiembre (`:74`), el seno y el coseno del mes 10 (`:76-77`) y las columnas del modelo (`:81`). Los pares de octubre nunca son una entrada (`test_el_mes_objetivo_no_es_una_entrada`), y la regresión se entrenó solo hasta julio de 2026: no se vuelve a entrenar con agosto ni con septiembre (`prediccion.py:25-27`).

**E10.1** `cargar` no puede preparar la tabla y apunta una incidencia 01 BLOQUEANTE (`calidad.py:118-125`). Como no están las cinco tablas, el estado es ERROR DE CARGA (`actualizacion.py:190-193`) y no se publica ninguna cifra nueva. El último resultado válido se conserva y solo se ve si se activa el interruptor, con el rótulo DESACTUALIZADO y su hora (`actualizacion.py:216`; `app_dashboard.py:678-692`). Al reponer el archivo bueno, el siguiente ciclo vuelve a CORRECTO, o a SIN CAMBIOS si el contenido es el mismo de antes.

**E10.2** Cambian la «Última comprobación», el registro de ciclos (uno por minuto) y la duración del cálculo. El estado es SIN CAMBIOS y los KPIs no se mueven. La «Última actualización válida» tampoco cambia, porque se conserva la de la publicación anterior (`actualizacion.py:199-202`): la huella de los CSV es la misma (`:47-74`). Así salió en el caso K del 13/11 (`04_Python/evidencias/dashboard/caso_k_registro.txt`).

**E12.1** Con −3, el navegador lo para antes de enviar, por el `min="0"` del campo (`index.html:352`): el evento `submit` ni siquiera llega al JavaScript (lo explica `js/custom.js:29-31`). Con 0 en todas, el formulario sí se envía, pero el total es 0: sale «Indica cuántos pares quieres de al menos una talla» y el foco va a la primera talla (`js/custom.js:34-38`).

**E12.2** Dos columnas: la media query `@media (max-width: 760px)` cambia `.catalogo-grid` a `repeat(2, minmax(0, 1fr))` (`css/inicio.css:649` y `:660-663`); en escritorio son 4 (`:617-622`). Por debajo de 370 px, además, se oculta el segundo enlace del menú, «Nuestra visión» (`:534-536`).

**E13.1** Responde 429 «Demasiados intentos» con la cabecera `Retry-After`, sin comprobar la contraseña: `tiempoDeBloqueo` es mayor que 0 y el login sale antes de llamar a `iniciar_sesion` (`servidor.js:120-124`). El bloqueo lo puso el quinto fallo (`intentos.js:41-43`). Está probado en `01_Interfaces/evidencias/panel-admin/resultados/09_intentos_y_sesiones.txt` («6.o intento CON la contrasena buena -> 429»). Pasados 5 minutos puede volver a entrar.

**E13.2** `usuario_sesion()` separa el id y la firma por `:`. Con `'1'` no hay firma, así que devuelve NULL (`02_funciones.sql:59-64`): el evento queda **sin operador**, no a nombre del administrador. Si se inventa una firma, el HMAC no coincide y también devuelve NULL (`:76-78`). La clave de la firma es el hash bcrypt del usuario, que ningún rol de la aplicación puede leer (`07_seguridad.sql:99-101`). Son las pruebas F1–F4 (`documentacion/README.md:504-557`).

**E14.1** `git log --oneline 7715f83^1..7715f83^2`: muestra lo que está en el segundo padre (la rama fusionada) y no en el primero (la rama de integración). Salen 25 commits; con `--format='%an'` se ve que el autor de todos es `Alvarobaz`, aunque el commit de fusión lo firme `omar1676`.

**E14.2** No siempre: `.gitignore` (`:5-8`) solo ignora archivos que no estaban ya en seguimiento, y `git add -f` se lo salta. Si ya se ha subido, hay que dar la contraseña por comprometida: cambiarla en PostgreSQL (los scripts 19 y 20 se pueden volver a ejecutar para ponerle otra a `web_nova` y `tienda_nova`), sacar el archivo del repositorio con `git rm --cached` y, si hace falta, limpiar el historial. Nunca se pone la contraseña en el mensaje del commit.

**E15.1** El 15 se para en la comprobación del estado: «SO024 está en estado "pendiente" y solo se fabrica un pedido confirmado» (`15_exportar_fabricacion.sql:131-135`). Con `ON_ERROR_STOP`, psql termina ahí y el CSV anterior se queda tal cual (`:102-104`). PSP no recibe nada nuevo: si se lanza, procesa el CSV que ya hubiera.

**E15.2** `df_pedidos_unicos` agrupa las líneas por `id_pedido` (`analiticas.py:108-115`): las 9 líneas se convierten en 1 fila con 40 pares y 3.996 €. Los KPIs dividen entre pedidos, no entre líneas (`kpis.py:87-88`). La prueba lo confirma: SO024 sale en 1 fila de `pedidos_unicos.csv`, con 9 líneas, 40 pares y 3.996 € (`06_Intermodular/evidencias/regresion-final/06_so024_provisional/06_pedidos_unicos_SO024.csv`).

**E11.1** Los siete datos (`06_Intermodular/SO024/caso-comun-SO024.md`, apartado 1): los pares de cada talla de la 38 a la 46 (se usan en Java y en Odoo), el color de Runner X (`18_datos_so024.sql`, `-v color`), el precio base (`-v precio`), el stock inicial por talla (`-v stock`), el texto de la personalización (Java y Odoo), el SKU en Odoo y el número de pedido en Odoo.

**E11.2** O se usa el SKU de PostgreSQL como referencia interna de cada variante en Odoo, o se apunta una tabla de equivalencias entre el SKU y la variante de Odoo. Además hay que acordar el número del pedido de venta (que sea SO024 o apuntar la equivalencia) para que la ficha de PSP y su registro lleven la referencia de Odoo (IM-PSP-10 y 29; `06_Intermodular/SO024/SO024_DATOS_PENDIENTES.md`).

**E16.1** `avanzar_pedido_trabajador` bloquea el pedido con `FOR UPDATE` (`23_portal_trabajador.sql:83-87`): el segundo espera a que el primero termine. Cuando entra, ya ve `en_preparacion`, pero pide otra vez `en_preparacion`, y la función lanza «Solo se puede pasar de en_preparacion a enviado» (`:104-106`). La ruta lo convierte en un 400 con ese mensaje (`rutas-trabajador.js:26-40`). En la base queda un solo cambio y un solo `CAMBIO_ESTADO` en `log_eventos`. Es la prueba 9d de `test:portal`.

**E16.2** La ruta deja pasar `entregado` porque es un estado válido, pero la función solo permite un paso: «Solo se puede pasar de confirmado a en_preparacion» (`23_portal_trabajador.sql:104-106`) → 400. El `idUsuario` del cuerpo no se usa: la ruta toma el usuario de la sesión (`rutas-trabajador.js:91`) y la función vuelve a comprobar que es un trabajador activo (`23_portal_trabajador.sql:69-79`). Son las pruebas 10a y 10b de `test:portal`.

---

## Anexo B. Dónde están las pruebas

Todo en el repositorio. La regresión completa del 13/11 (`06_Intermodular/evidencias/regresion-final/README.md`) dice la hora, el entorno y el resultado de cada batería.

| Bloque | Archivo de resultados | Qué demuestra |
|---|---|---|
| SQL | `06_Intermodular/evidencias/regresion-final/01_sql/` | Los scripts 01–23 en una base vacía; 09–16 con 123 PASS, 0 FAIL y el ERROR previsto; tienda 55/55, reparto 37/37 y portal 50/50 |
| Java | `06_Intermodular/evidencias/regresion-final/02_java_psp/02_pruebas_rubrica.txt` y `02_Acceso_Datos/evidencias/java-pruebas-rubrica/` | 47 pruebas: login, A–J y permisos (P), con el TXT, el JSON y el CSV que escribe |
| Java (ventanas) | `06_Intermodular/evidencias/regresion-final/07_ventanas_swing/` y `02_Acceso_Datos/evidencias/java-swing/` | 76/76 y 1/1 sin conexión; 19 capturas |
| PSP | `06_Intermodular/evidencias/regresion-final/02_java_psp/` y `03_PSP/evidencias/` | 27/27, CUSTOM-40 con código 0, los errores controlados, la ficha y el registro |
| Python | `06_Intermodular/evidencias/regresion-final/04_python/` | 265 pruebas y la comparación de las 93 salidas con la referencia |
| Dashboard | `04_Python/evidencias/dashboard/` | Capturas del 9 y 10/11 (pestañas, filtros, R1, R4 y R5) y el caso K del 13/11 (tres ciclos en Edge) |
| Web | `06_Intermodular/evidencias/regresion-final/05_web/` y `01_Interfaces/evidencias/web/` | 81/81, 136/136 y 114/114; Lighthouse (11/11) |
| Tienda | `06_Intermodular/evidencias/regresion-final/05_web/04_compra_edge.txt` y `01_Interfaces/evidencias/tienda/capturas-2026-11-13/` | Compra en Edge 139/139, contrastada con PostgreSQL y con el panel |
| Servidor | `06_Intermodular/evidencias/regresion-final/03_node/` | Panel 23/23, tienda 39/39 y portal 24/24 |
| Reparto y recibos | `01_Interfaces/evidencias/reparto-y-correo/` y `01_Interfaces/evidencias/correo-ethereal/` | Reparto en Edge 29/29; Ethereal real 16/16 (datos ficticios), sin red 5/5 y sin respuesta 5/5 |
| Login único y portal | `06_Intermodular/evidencias/regresion-final/05_web/06_edge_portal.txt` y `01_Interfaces/evidencias/portal-trabajador/` | 82/82 en Edge (escritorio y móvil, axe) |
| Seguridad del panel (11/11) | `01_Interfaces/evidencias/panel-admin/resultados/` | Intentos, sesiones, cabeceras y permisos |
| SO024 [PROVISIONAL] | `06_Intermodular/evidencias/regresion-final/06_so024_provisional/` y `03_PSP/evidencias/so024_provisional/` | La cadena 18 → Java → 15 → PSP → 16 → Python |
| Instalación | `06_Intermodular/evidencias/regresion-final/08_manual_instalacion/` | El manual de instalación seguido en un clon nuevo y una base nueva |
| Estado de cada requisito | `06_Intermodular/rubricas/MATRIZ_RUBRICAS.md` | Qué está hecho, probado y documentado, qué falta y qué riesgo tiene |
