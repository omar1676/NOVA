# NOVA Sneakers · Simulacro de defensa

13/11/2026 · Un guion de 15 minutos para cada uno: Omar, Álvaro y Berme · rama `main` (código de `4f09742`)

> El guion es **el mismo para los tres**. No asume quién hizo qué: el tribunal puede preguntar cualquier cosa a cualquiera (IM-COM-09) y en Acceso a Datos «todos los miembros deben comprender el modelo» (AD-135). Las respuestas de referencia están en `GUIA_DEFENSA.md`; la columna «Guía» dice en qué sección.

## 1. Reglas del simulacro

- **Tres rondas, una por persona.** En cada ronda, uno hace de tribunal (lee las preguntas y controla el reloj), otro anota (marca la hoja del examinado) y el tercero responde. Después se rota.
- **Mismo guion, mismo orden** en las tres rondas de la primera vuelta. En la segunda vuelta (otro día), cambiad el orden de los bloques y usad las preguntas de reserva del apartado 4.
- **Sin la guía delante.** Solo se puede abrir el código cuando la pregunta dice «señala la línea». Nadie responde por otro.
- **Tiempo:** cada respuesta, entre 30 y 60 segundos. Si se pasa, el tribunal corta: gestionar el tiempo también puntúa (presentación ante el tribunal, 20 %: «síntesis, estructura, comunicación profesional, gestión del tiempo y respuesta a preguntas»).
- **Preguntas trampa:** el tribunal las dice con seguridad, como si fueran ciertas. Hay que corregirlas con educación y con el dato («No exactamente: …, está en …»). Seguirle la corriente al tribunal cuenta como fallo.
- **Lo que no está hecho se dice.** Odoo tiene S00005 documentado, sin integración entre sistemas probada; SO024 es un ensayo provisional del ejemplo: inventar una respuesta es peor que decir «eso está pendiente y falta esto».
- **Al terminar:** cada uno rellena su hoja (apartado 5) y el anotador la contrasta con lo que ha oído.

## 2. Guion (15 minutos, igual para los tres)

| Minuto | Bloque | Pregunta del tribunal | Lo que tiene que salir en la respuesta (para el anotador) | Guía |
|---|---|---|---|---|
| 0:00–1:00 | Apertura | **1.** Explica NOVA en un minuto: qué problema resuelve, qué habéis construido y qué falta. | Fábrica con pedidos Custom de clubes; web, PostgreSQL con triggers, Java, PSP, Python con dashboard; S00005 del Club Atlético NOVA como caso documental de Odoo; módulos auxiliares con PRUEBA, sin trazabilidad del mismo pedido demostrada. | §0 |
| 1:00–2:15 | PostgreSQL y PL/pgSQL | **2.** ¿Cómo se calcula el importe total de un pedido y por qué no lo calcula Java? | BEFORE: subtotal = cantidad × precio; AFTER: `SUM` de las líneas (recalcular, no acumular); AD-43: la base hace la automatización. | §2, P2.2–P2.4 |
| 2:15–3:00 | PostgreSQL y PL/pgSQL | **3.** ¿Cuándo se descuenta el stock y qué impide descontarlo dos veces? Señala la línea del trigger. | Al confirmar; `WHEN` de `03_triggers.sql:31`; `stock_descontado = false`; protección de la marca. | §2, P2.5–P2.6 |
| 3:00–3:20 | **Trampa AD-SQL** | **T1.** «Si cancelo un pedido confirmado y luego lo vuelvo a confirmar, se descuenta el stock otra vez, ¿verdad?» | No se puede: un pedido cancelado no se reactiva (`02_funciones.sql:334-337`). Y Java solo confirma pedidos pendientes. | §2, P2.7 |
| 3:20–4:20 | Java/JDBC | **4.** ¿Por qué PreparedStatement y cómo hacéis que un filtro vacío no filtre? | Parámetros `?` separados del SQL (inyección); solo se añaden al `WHERE` los filtros con valor; `WHERE 1 = 1`. | §3, P3.1–P3.2 |
| 4:20–5:00 | Java/JDBC | **5.** ¿Cómo sabe PostgreSQL qué usuario de Java ha hecho un cambio? | `iniciar_sesion` al empezar cada transacción; `nova.id_usuario` firmado con HMAC; los triggers usan `usuario_sesion()`. | §3, P3.8; §2, P2.10 |
| 5:00–5:20 | **Trampa AD-Java** | **T2.** «Como usáis PreparedStatement en todo, el `SET ROLE` también va con un parámetro, ¿no?» | No: `SET ROLE` no admite `?`. Se concatena, pero solo acepta tres nombres fijos (`ConexionBD.java:63-78`). | §3, P3.7 |
| 5:20–6:20 | PSP | **6.** Cuenta el recorrido de los datos entre el padre y los tres hijos. ¿Por qué tres hilos? | CSV → validador → padre → analizador → padre → generador → ficha; stdin/stdout, errores por stderr; los hilos evitan que se llenen las tuberías. | §4, P4.2–P4.5 |
| 6:20–6:50 | PSP | **7.** ¿Qué pasa si un hijo se queda colgado? Di el código. | `waitFor(10 s)`; `destroy()` y `destroyForcibly()`; código -2 (TIEMPO_AGOTADO); el padre termina con 3 y no lanza el paso siguiente. | §4, P4.6–P4.7 |
| 6:50–7:10 | **Trampa PSP** | **T3.** «El validador ya comprueba que las tallas están entre 38 y 46, así que el analizador no necesita comprobar nada.» | No: el validador solo exige una talla positiva; el rango 20–55 lo comprueba el analizador (prueba 12k). | §4, E4.1 |
| 7:10–8:00 | Python y pandas | **8.** Un pedido de 3 líneas y una de ellas con cantidad -2: ¿qué pasa con ese pedido? ¿Y cuántos pedidos cuenta el ticket medio cuando todo está bien? | Regla 05, recuperable; se rechaza el pedido entero con sus 3 líneas; el ticket medio divide entre pedidos (`df_pedidos_unicos`), no entre líneas. | §5, P5.4–P5.7 |
| 8:00–8:50 | Ciencia de datos | **9.** ¿Por qué escaláis antes de KMeans, cómo elegisteis k y qué salió en la predicción frente al baseline? | KMeans mide distancias; `StandardScaler` y `log1p`; silhouette más alto, k = 4 (0,373); regresión: mejor en RMSE y peor en MAE, así que no mejora claramente. Todo con sintéticos. | §8 y §9 |
| 8:50–9:30 | Streamlit | **10.** ¿Qué hace el dashboard cada 60 s? ¿Y si llega un CSV roto? | `st.fragment(run_every="60s")`; relee, valida y recalcula todo; 4 estados; no publica cifras con errores; último resultado válido marcado DESACTUALIZADO. | §10 |
| 9:30–9:50 | **Trampa Python** | **T4.** «El ticket medio es el importe total entre el número de líneas, ¿no?» | No: entre pedidos («se divide entre pedidos, nunca entre líneas», `kpis.py:87-88`). | §5, P5.7 |
| 9:50–10:30 | Interfaces | **11.** ¿Cómo habéis hecho la web responsive y accesible? Dime una regla CSS concreta. | Grid de 4 a 2 columnas con `@media (max-width: 760px)`; `clamp()`; etiquetas, `fieldset`, `role="status"`, foco visible; WCAG 2.1 AA, axe y Lighthouse. | §12 |
| 10:30–10:45 | **Trampa Interfaces** | **T5.** «El formulario Custom guarda la solicitud en la base de datos, ¿verdad?» | No: es una simulación; `preventDefault()` en `js/custom.js:32` y el mensaje lo dice. El pedido real va por Odoo y Java. | §12, P12.6 |
| 10:45–11:20 | Seguridad | **12.** ¿Cómo guardáis las contraseñas y cómo funciona la sesión de la web? | bcrypt con sal (`crypt` y `gen_salt('bf')`); token aleatorio de 32 bytes en una cookie HttpOnly y SameSite=Strict de 2 h; 5 fallos → 429. | §13 |
| 11:20–11:35 | **Trampa Seguridad** | **T6.** «Si un usuario olvida la contraseña, el administrador puede descifrar el bcrypt y decírsela.» | No: bcrypt es un hash de un solo sentido. Se le pone una nueva con `establecer_password` (`02_funciones.sql:427-446`). | §13, P13.2 |
| 11:35–11:50 | **Trampa Git** | **T7.** «El commit `492c4e8` es de `omar1676`, así que el panel de administración lo programó él.» | No: el commit de fusión lo firma quien fusiona; los 25 commits de dentro conservan su autor. Y contar commits no mide el trabajo. | §14, P14.3–P14.4 |
| 11:50–12:20 | Odoo | **13.** ¿Qué pide el enunciado de Odoo y cómo se relaciona con PSP? | Núcleo del flujo: venta → fabricación → entrega → factura; instalación, roles, cliente, venta, MRP y backup. S00005 documentado en el PDF; no hay ficha PSP acreditada de ese pedido ni backup/restauración verificados aquí. | §11 |
| 12:20–12:35 | **Trampa Odoo** | **T8.** «¿Qué factura podéis mostrar y qué demuestra?» | Mostrar INV/2026/00001 en el PDF de Berme, p. 12, del flujo S00005. No es una factura SO024 ni prueba su procesamiento en PSP/PostgreSQL. | §11 |
| 12:35–13:25 | **Cruzada 1** | **14.** ¿Podéis seguir S00005 desde Odoo hasta el dashboard y distinguirlo del ensayo SO024? | No hay prueba de S00005 en esa cadena. Explicar por separado el PDF de Odoo y el flujo de PRUEBA PostgreSQL → 15 → PSP / 16 → Python. No cambiar identificadores para unirlos. | §15 |
| 13:25–14:05 | **Cruzada 2** | **15.** El panel Java y el dashboard pueden dar importes de venta distintos con los mismos datos. ¿Cuál está mal? | Ninguno: criterios distintos. Java suma los no cancelados (`IndicadoresDAO.java:20-26`); K07 suma los confirmados en adelante; Python calcula los tres (`analiticas.py:155-181`). **[EQUIPO: elegir el oficial, si se quiere unificar]** | §5, P5.8 |
| 14:05–14:30 | **Trampa Integración** | **T9.** «¿Elegir S00005 demuestra la integración completa?» | No. El PDF acredita el caso de Odoo; faltan exportación y correspondencia verificadas con PostgreSQL, PSP y Python. SO024 es solo un ejemplo y su ensayo no prueba S00005. | §15 |
| (reserva) | **Trampa Portal** | **T10.** «El portal del trabajador cambia el estado y el stock con un `UPDATE` directo, como lo dejó Berme.» | No: el servidor pasa a `portal_trabajador`, que no puede escribir en ninguna tabla; solo ejecuta `avanzar_pedido_trabajador` y `ajustar_existencias_trabajador` (script 23), que comprueban que es un trabajador activo y firman la auditoría a su nombre. | §16 |
| 14:30–15:00 | Cierre | **16.** ¿Qué mejorarías primero y cuál ha sido tu parte del trabajo? | Explicar los límites de trazabilidad, sin prometer nuevas funciones para esta entrega. La parte propia, contada tal como fue: la decide el equipo, no esta guía. | §0 |

## 3. Respuestas de las preguntas trampa (para el tribunal)

| Trampa | Por qué es trampa | Respuesta correcta y dónde está |
|---|---|---|
| T1 (AD-SQL) | Da por hecho que se puede volver a confirmar un cancelado | `devolver_stock_cancelacion` lanza «No se puede reactivar un pedido cancelado» (`02_funciones.sql:334-337`); `confirmarPedido` exige `estado = 'pendiente'` (`PedidoDAO.java:184-188`) |
| T2 (AD-Java) | Mezcla PreparedStatement con una orden que no admite parámetros | `SET ROLE` va concatenado con una lista blanca de tres roles (`ConexionBD.java:63-78`) |
| T3 (PSP) | Atribuye al validador una comprobación que no hace | Validador: talla positiva (`ValidadorPedidoCustom.java:144-150`); analizador: 20–55 (`03_PSP/src/Psp/AnalizadorTallas.java:85-87`) |
| T4 (Python) | Confunde líneas con pedidos | K09 = K07 / K02, «se divide entre pedidos, nunca entre líneas» (`kpis.py:87-88`) |
| T5 (Interfaces) | Supone que hay backend en el formulario | `evento.preventDefault()` y mensaje «SIMULACIÓN» (`js/custom.js:32` y `:48-51`) |
| T6 (Seguridad) | Confunde hash con cifrado | `crypt(p, hash) <> hash` para comprobar (`02_funciones.sql:25`); contraseña nueva con `establecer_password` (`:427-446`) |
| T7 (Git) | Confunde el autor de la fusión con el de los commits | `git log --format='%an' 492c4e8^1..492c4e8^2` → 25 commits de `Alvarobaz` |
| T8 (Odoo) | Pide la factura de SO024 | No existe: SO024 es el ejemplo del enunciado, no una venta de Odoo. Enseñar INV/2026/00001 en el PDF de Berme, p. 12, y aclarar que es del flujo S00005 (`05_Odoo/README.md`; `odoo/documentacion/Odoo-NOVA-Sneakers.pdf`) |
| T9 (Integración) | Confunde el caso documental con integración demostrada | `06_Intermodular/CASO_COMUN_S00005.md` (sin prueba de S00005 fuera de Odoo); `03_PSP/evidencias/so024_provisional/README.md` y `06_Intermodular/evidencias/regresion-final/06_so024_provisional/00_cadena.txt` (lanzador, datos PROVISIONALES) |
| T10 (Portal) | Supone que el portal escribe en las tablas | `23_portal_trabajador.sql:218-250` (rol sin escritura y solo dos `GRANT EXECUTE`); `servidor-admin/rutas-trabajador.js:77-103` llama a la función con el usuario de la sesión |

## 4. Preguntas de reserva (para la segunda vuelta)

**Trampas de reserva**

| Tema | Trampa | Respuesta correcta |
|---|---|---|
| SQL | «SECURITY DEFINER significa que la función solo la puede ejecutar el administrador.» | No: significa que se ejecuta con los permisos de su dueño. Quién la puede ejecutar lo deciden `REVOKE`/`GRANT EXECUTE` (`07_seguridad.sql:66-85`). |
| Java | «El JSON de usuarios se genera antes del COMMIT, para tenerlo listo.» | No: después del COMMIT, para no publicar un cambio deshecho (`UsuarioDAO.java:139-147`). |
| PSP | «`waitFor(10, SECONDS)` mata al hijo a los 10 segundos.» | No: `waitFor` solo espera y devuelve false. Lo cancelan `destroy()` y `destroyForcibly()` (`GestorProcesos.java:106-121`). |
| Estadística | «H3 sale con evidencia insuficiente: o sea, la demanda no crece.» | No: no se puede afirmar ni que crezca ni que no (`estadistica.py:189-199`). |
| RFM | «Un cliente que solo tiene pedidos cancelados no sale en el RFM.» | Sí sale, en «Sin compras válidas», con F = 0 y M = 0 (`segmentacion.py:54-59`). |
| KMeans | «Elegisteis k = 5 porque tiene la menor inercia.» | No: k = 4 por el silhouette más alto; la inercia siempre baja al subir k. |
| Predicción | «La regresión mejora al baseline, así que la usaríais.» | No claramente: RMSE 36,15 frente a 37,42, pero MAE 26,28 frente a 25,03. Se dice tal cual (PY-109). |
| Streamlit | «El dashboard está conectado a PostgreSQL: un pedido nuevo sale solo al minuto.» | No: lee CSV; sin una nueva exportación con el 16, los valores no cambian. |
| Seguridad | «Como la cookie es HttpOnly, la web ya es segura frente a todo.» | HttpOnly protege el token frente a XSS; contra CSRF está SameSite=Strict; falta `Secure` porque es HTTP local. |
| Git | «El `.gitignore` impide subir el `.env` aunque se use `git add -f`.» | No: `-f` se lo salta, y tampoco protege un archivo ya en seguimiento. |
| Portal | «Con la sesión del portal se puede entrar en el panel de administración.» | No: el login único lleva a cada rol a su panel y las rutas `/api/admin/` le responden 403 al trabajador (`servidor.js:221-225`; prueba 8 de `test:portal`). |
| Odoo | «El portal ya manda los pedidos a Odoo.» | No: `odoo.js` está desactivado sin `ODOO_URL`, `ODOO_DB` y `ODOO_API_KEY`, y las rutas de `pedidos.js` no se montan. En la versión entregada no se ha verificado contra ningún Odoo; el PDF documenta pruebas de Berme con una versión anterior en su entorno (pp. 13-15). |

**Cruzadas de reserva**

1. ¿Qué tienen en común el `CHECK (cantidad > 0)` de `linea_pedido`, la regla 05 de Python y el validador de PSP? ¿Por qué se repite la misma comprobación? *(Cada bloque recibe datos de otro y no se fía: defensa en profundidad.)*
2. `log_eventos`, `actividad_sneaker.txt` y `registro_psp.txt`: ¿qué guarda cada uno y por qué no tienen los mismos eventos? *(El primero es transaccional y se deshace con ROLLBACK; el TXT apunta también rechazos y errores; el de PSP, cada ejecución del procesador.)*
3. Una compra de la tienda web y un pedido creado en Java: ¿qué funciones y triggers comparten y en qué se diferencian? *(Los dos usan `realizar_compra`, `anadir_linea_pedido` y los triggers; cambian el rol, las comprobaciones del 20 y que la web queda «(sin sesión)» en la auditoría.)*
4. Se cancela en Java un pedido confirmado. ¿Qué cambia en `existencias`, `log_eventos`, el TXT y el dashboard, y cuándo? *(Stock devuelto y `CAMBIO_STOCK`; `BAJA_LOGICA`; línea `CANCELAR PEDIDO`; el dashboard, solo tras volver a exportar con el 16.)*
5. ¿Qué es un rol en Java, en PostgreSQL y en Odoo? ¿Son lo mismo?
6. Si mañana el pedido de SO024 pasa a 48 pares, ¿qué partes del proyecto fallarían o habría que cambiar? *(El 15 exige exactamente 40 pares, `15_exportar_fabricacion.sql:146-149`; el stock inicial del 18; los textos del caso común.)*
7. Un trabajador pulsa «Avanzar estado» en un pedido confirmado desde el portal. ¿Qué cambia en `pedidos`, `existencias` y `log_eventos`, y quién firma? *(Pasa a `en_preparacion`; el stock no cambia, porque ya se descontó al confirmar; `CAMBIO_ESTADO` a nombre del trabajador, con el mismo mecanismo de `nova.id_usuario` que el 22.)*

## 5. Hojas de autoevaluación

Marca una casilla por fila **justo después del simulacro**, sin mirar la guía. Criterio:

- **Sé explicarlo:** lo he contado bien, sin ayuda y en menos de un minuto, y sé decir dónde está en el código.
- **Lo explico con apoyo:** lo sé si miro el código o la guía, o me he dejado una parte importante.
- **No lo sé:** no he sabido responder, me he liado o he caído en la trampa.

### Hoja de Omar

| # | Tema | Sé explicarlo | Con apoyo | No lo sé | Guía |
|---|---|---|---|---|---|
| 1 | El proyecto en un minuto, con lo que falta | ☐ | ☐ | ☐ | §0 |
| 2 | Modelo: modelo → variante → SKU → existencias; pedidos y líneas | ☐ | ☐ | ☐ | §1 |
| 3 | Restricciones (PK, FK, UNIQUE, CHECK) con un ejemplo de cada una | ☐ | ☐ | ☐ | §1 |
| 4 | Transacciones, COMMIT/ROLLBACK y qué ve otra conexión | ☐ | ☐ | ☐ | §1 |
| 5 | Triggers de importes: BEFORE y AFTER | ☐ | ☐ | ☐ | §2 |
| 6 | Stock al confirmar y al cancelar; no descontar dos veces | ☐ | ☐ | ☐ | §2 |
| 7 | Auditoría: quién firma y qué pasa con un ROLLBACK | ☐ | ☐ | ☐ | §2 |
| 8 | SECURITY DEFINER, `search_path` y `REVOKE ... FROM PUBLIC` | ☐ | ☐ | ☐ | §2 |
| 9 | PreparedStatement y filtros combinables | ☐ | ☐ | ☐ | §3 |
| 10 | Transacciones JDBC y cierre de recursos | ☐ | ☐ | ☐ | §3 |
| 11 | Roles en Java: las dos barreras y el `SET ROLE` | ☐ | ☐ | ☐ | §3 |
| 12 | TXT, JSON y CSV: formato y escritura segura | ☐ | ☐ | ☐ | §3 |
| 13 | ProcessBuilder, el padre y los tres hijos | ☐ | ☐ | ☐ | §4 |
| 14 | stdin, stdout, stderr y los tres hilos | ☐ | ☐ | ☐ | §4 |
| 15 | Códigos de salida y tiempos de espera | ☐ | ☐ | ☐ | §4 |
| 16 | Las 12 reglas, las 3 gravedades y el pedido entero | ☐ | ☐ | ☐ | §5 |
| 17 | Líneas frente a pedidos; `merge` con `validate` | ☐ | ☐ | ☐ | §5 |
| 18 | KPIs y los tres criterios de venta | ☐ | ☐ | ☐ | §5 |
| 19 | Bootstrap, hipótesis y lo que no se puede afirmar | ☐ | ☐ | ☐ | §6 |
| 20 | RFM: R, F, M, quintiles y segmentos | ☐ | ☐ | ☐ | §7 |
| 21 | KMeans: escalado, silhouette y elección de k | ☐ | ☐ | ☐ | §8 |
| 22 | Predicción: baseline, separación por fecha, MAE, RMSE y fuga | ☐ | ☐ | ☐ | §9 |
| 23 | Streamlit: 60 s, 4 estados y último resultado válido | ☐ | ☐ | ☐ | §10 |
| 24 | Odoo: lo que pide la rúbrica y lo que está pendiente | ☐ | ☐ | ☐ | §11 |
| 25 | Responsive: Grid y media queries | ☐ | ☐ | ☐ | §12 |
| 26 | Accesibilidad: WCAG 2.1 AA, axe y Lighthouse | ☐ | ☐ | ☐ | §12 |
| 27 | Formulario Custom: validación y simulación | ☐ | ☐ | ☐ | §12 |
| 28 | Contraseñas con bcrypt | ☐ | ☐ | ☐ | §13 |
| 29 | Sesiones y cookies (HttpOnly, SameSite) | ☐ | ☐ | ☐ | §13 |
| 30 | Roles de PostgreSQL frente a roles de la aplicación | ☐ | ☐ | ☐ | §13 |
| 31 | Límite de intentos de login | ☐ | ☐ | ☐ | §13 |
| 32 | Git: ramas, merge, worktree y autoría | ☐ | ☐ | ☐ | §14 |
| 33 | S00005 documental y límites de integración | ☐ | ☐ | ☐ | §15 |
| 34 | Portal del trabajador: login único, `portal_trabajador` y las dos funciones del 23 | ☐ | ☐ | ☐ | §16 |
| 35 | Las limitaciones, dichas antes de que pregunten | ☐ | ☐ | ☐ | todas |
| 36 | Trampas: no he caído en ninguna (anota cuáles) | ☐ | ☐ | ☐ | §3 de este archivo |

Lo que tengo que estudiar antes del siguiente simulacro: ______________________________

### Hoja de Álvaro

| # | Tema | Sé explicarlo | Con apoyo | No lo sé | Guía |
|---|---|---|---|---|---|
| 1 | El proyecto en un minuto, con lo que falta | ☐ | ☐ | ☐ | §0 |
| 2 | Modelo: modelo → variante → SKU → existencias; pedidos y líneas | ☐ | ☐ | ☐ | §1 |
| 3 | Restricciones (PK, FK, UNIQUE, CHECK) con un ejemplo de cada una | ☐ | ☐ | ☐ | §1 |
| 4 | Transacciones, COMMIT/ROLLBACK y qué ve otra conexión | ☐ | ☐ | ☐ | §1 |
| 5 | Triggers de importes: BEFORE y AFTER | ☐ | ☐ | ☐ | §2 |
| 6 | Stock al confirmar y al cancelar; no descontar dos veces | ☐ | ☐ | ☐ | §2 |
| 7 | Auditoría: quién firma y qué pasa con un ROLLBACK | ☐ | ☐ | ☐ | §2 |
| 8 | SECURITY DEFINER, `search_path` y `REVOKE ... FROM PUBLIC` | ☐ | ☐ | ☐ | §2 |
| 9 | PreparedStatement y filtros combinables | ☐ | ☐ | ☐ | §3 |
| 10 | Transacciones JDBC y cierre de recursos | ☐ | ☐ | ☐ | §3 |
| 11 | Roles en Java: las dos barreras y el `SET ROLE` | ☐ | ☐ | ☐ | §3 |
| 12 | TXT, JSON y CSV: formato y escritura segura | ☐ | ☐ | ☐ | §3 |
| 13 | ProcessBuilder, el padre y los tres hijos | ☐ | ☐ | ☐ | §4 |
| 14 | stdin, stdout, stderr y los tres hilos | ☐ | ☐ | ☐ | §4 |
| 15 | Códigos de salida y tiempos de espera | ☐ | ☐ | ☐ | §4 |
| 16 | Las 12 reglas, las 3 gravedades y el pedido entero | ☐ | ☐ | ☐ | §5 |
| 17 | Líneas frente a pedidos; `merge` con `validate` | ☐ | ☐ | ☐ | §5 |
| 18 | KPIs y los tres criterios de venta | ☐ | ☐ | ☐ | §5 |
| 19 | Bootstrap, hipótesis y lo que no se puede afirmar | ☐ | ☐ | ☐ | §6 |
| 20 | RFM: R, F, M, quintiles y segmentos | ☐ | ☐ | ☐ | §7 |
| 21 | KMeans: escalado, silhouette y elección de k | ☐ | ☐ | ☐ | §8 |
| 22 | Predicción: baseline, separación por fecha, MAE, RMSE y fuga | ☐ | ☐ | ☐ | §9 |
| 23 | Streamlit: 60 s, 4 estados y último resultado válido | ☐ | ☐ | ☐ | §10 |
| 24 | Odoo: lo que pide la rúbrica y lo que está pendiente | ☐ | ☐ | ☐ | §11 |
| 25 | Responsive: Grid y media queries | ☐ | ☐ | ☐ | §12 |
| 26 | Accesibilidad: WCAG 2.1 AA, axe y Lighthouse | ☐ | ☐ | ☐ | §12 |
| 27 | Formulario Custom: validación y simulación | ☐ | ☐ | ☐ | §12 |
| 28 | Contraseñas con bcrypt | ☐ | ☐ | ☐ | §13 |
| 29 | Sesiones y cookies (HttpOnly, SameSite) | ☐ | ☐ | ☐ | §13 |
| 30 | Roles de PostgreSQL frente a roles de la aplicación | ☐ | ☐ | ☐ | §13 |
| 31 | Límite de intentos de login | ☐ | ☐ | ☐ | §13 |
| 32 | Git: ramas, merge, worktree y autoría | ☐ | ☐ | ☐ | §14 |
| 33 | S00005 documental y límites de integración | ☐ | ☐ | ☐ | §15 |
| 34 | Portal del trabajador: login único, `portal_trabajador` y las dos funciones del 23 | ☐ | ☐ | ☐ | §16 |
| 35 | Las limitaciones, dichas antes de que pregunten | ☐ | ☐ | ☐ | todas |
| 36 | Trampas: no he caído en ninguna (anota cuáles) | ☐ | ☐ | ☐ | §3 de este archivo |

Lo que tengo que estudiar antes del siguiente simulacro: ______________________________

### Hoja de Berme

| # | Tema | Sé explicarlo | Con apoyo | No lo sé | Guía |
|---|---|---|---|---|---|
| 1 | El proyecto en un minuto, con lo que falta | ☐ | ☐ | ☐ | §0 |
| 2 | Modelo: modelo → variante → SKU → existencias; pedidos y líneas | ☐ | ☐ | ☐ | §1 |
| 3 | Restricciones (PK, FK, UNIQUE, CHECK) con un ejemplo de cada una | ☐ | ☐ | ☐ | §1 |
| 4 | Transacciones, COMMIT/ROLLBACK y qué ve otra conexión | ☐ | ☐ | ☐ | §1 |
| 5 | Triggers de importes: BEFORE y AFTER | ☐ | ☐ | ☐ | §2 |
| 6 | Stock al confirmar y al cancelar; no descontar dos veces | ☐ | ☐ | ☐ | §2 |
| 7 | Auditoría: quién firma y qué pasa con un ROLLBACK | ☐ | ☐ | ☐ | §2 |
| 8 | SECURITY DEFINER, `search_path` y `REVOKE ... FROM PUBLIC` | ☐ | ☐ | ☐ | §2 |
| 9 | PreparedStatement y filtros combinables | ☐ | ☐ | ☐ | §3 |
| 10 | Transacciones JDBC y cierre de recursos | ☐ | ☐ | ☐ | §3 |
| 11 | Roles en Java: las dos barreras y el `SET ROLE` | ☐ | ☐ | ☐ | §3 |
| 12 | TXT, JSON y CSV: formato y escritura segura | ☐ | ☐ | ☐ | §3 |
| 13 | ProcessBuilder, el padre y los tres hijos | ☐ | ☐ | ☐ | §4 |
| 14 | stdin, stdout, stderr y los tres hilos | ☐ | ☐ | ☐ | §4 |
| 15 | Códigos de salida y tiempos de espera | ☐ | ☐ | ☐ | §4 |
| 16 | Las 12 reglas, las 3 gravedades y el pedido entero | ☐ | ☐ | ☐ | §5 |
| 17 | Líneas frente a pedidos; `merge` con `validate` | ☐ | ☐ | ☐ | §5 |
| 18 | KPIs y los tres criterios de venta | ☐ | ☐ | ☐ | §5 |
| 19 | Bootstrap, hipótesis y lo que no se puede afirmar | ☐ | ☐ | ☐ | §6 |
| 20 | RFM: R, F, M, quintiles y segmentos | ☐ | ☐ | ☐ | §7 |
| 21 | KMeans: escalado, silhouette y elección de k | ☐ | ☐ | ☐ | §8 |
| 22 | Predicción: baseline, separación por fecha, MAE, RMSE y fuga | ☐ | ☐ | ☐ | §9 |
| 23 | Streamlit: 60 s, 4 estados y último resultado válido | ☐ | ☐ | ☐ | §10 |
| 24 | Odoo: lo que pide la rúbrica y lo que está pendiente | ☐ | ☐ | ☐ | §11 |
| 25 | Responsive: Grid y media queries | ☐ | ☐ | ☐ | §12 |
| 26 | Accesibilidad: WCAG 2.1 AA, axe y Lighthouse | ☐ | ☐ | ☐ | §12 |
| 27 | Formulario Custom: validación y simulación | ☐ | ☐ | ☐ | §12 |
| 28 | Contraseñas con bcrypt | ☐ | ☐ | ☐ | §13 |
| 29 | Sesiones y cookies (HttpOnly, SameSite) | ☐ | ☐ | ☐ | §13 |
| 30 | Roles de PostgreSQL frente a roles de la aplicación | ☐ | ☐ | ☐ | §13 |
| 31 | Límite de intentos de login | ☐ | ☐ | ☐ | §13 |
| 32 | Git: ramas, merge, worktree y autoría | ☐ | ☐ | ☐ | §14 |
| 33 | S00005 documental y límites de integración | ☐ | ☐ | ☐ | §15 |
| 34 | Portal del trabajador: login único, `portal_trabajador` y las dos funciones del 23 | ☐ | ☐ | ☐ | §16 |
| 35 | Las limitaciones, dichas antes de que pregunten | ☐ | ☐ | ☐ | todas |
| 36 | Trampas: no he caído en ninguna (anota cuáles) | ☐ | ☐ | ☐ | §3 de este archivo |

Lo que tengo que estudiar antes del siguiente simulacro: ______________________________

## 6. De las marcas al plan de estudio

1. **«No lo sé»:** lee la sección de la guía, abre cada archivo en las líneas citadas, haz los dos ejercicios y explícaselo a uno de los otros dos sin mirar. Vuelve a hacer esa parte del simulacro al día siguiente.
2. **«Con apoyo»:** repite la respuesta en voz alta hasta que salga en menos de un minuto y con la línea del código.
3. **Prioridad:**
   - Primero, **Acceso a Datos** (filas 2 a 12): su enunciado dice que «es imprescindible aprobar todas las partes» (AD-138).
   - Después, **Python** (filas 16 a 23): su defensa pesa un 30 % e incluye «explicación individual de pandas y cardinalidades» (9 %) y «análisis estadístico/ML honesto» (7 %).
   - **Odoo** (fila 24): los tres deben distinguir la evidencia S00005 del PDF de la conexión no verificada y de los requisitos aún parciales.
   - **La fila 35** (limitaciones) y **la 36** (trampas) son las que más se notan delante de un tribunal.
4. **Resumen de cada ronda** (lo rellena quien hace de anotador):

| Ronda | Quién responde | Minutos usados | Preguntas sin responder | Trampas en las que ha caído | Lo mejor | Lo que hay que repetir |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
