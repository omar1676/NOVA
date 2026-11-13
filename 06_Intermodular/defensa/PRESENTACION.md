# NOVA Sneakers · Presentación ante el tribunal

13/11/2026 · 15 diapositivas · 15 minutos · rama `integracion/candidata-2`

> La presentación ante el tribunal vale un **20 %** del proyecto intermodular y se valoran la «síntesis, estructura, comunicación profesional, gestión del tiempo y respuesta a preguntas» (IM, p. 8). Por eso cada diapositiva tiene un tiempo y unas notas del orador: se ensaya con reloj.

## Antes de empezar

- **Duración prevista: 15:00.** **[DUDA PARA EL PROFESOR (D12): cuánto dura la exposición ante el tribunal.]** Si os dan menos tiempo, ved «Si hay que recortar» al final.
- **Quién presenta cada diapositiva: [POR DECIDIR (los tres)].** Lo recomendable es repartirlas de forma que cada uno hable de módulos que no son «los suyos»: así se demuestra que los tres conocen todo el proyecto (IM-COM-07).
- **Las rutas de las figuras** son relativas a la raíz del repositorio y todas existen en la rama final. La captura del catálogo de la diapositiva 1 es de la regresión del 13/11 (`06_Intermodular/evidencias/regresion-final/05_web/capturas_interfaces/escritorio_01_catalogo_con_precios.png`, reducida en el repositorio).
- **Odoo:** mostrar S00005 en el PDF original de Berme, pp. 10–12. Es evidencia documental; no una conexión en vivo. El `.pptx` conservado es un borrador histórico anterior a esta decisión: usar este guion actualizado, no sus afirmaciones antiguas.
- **SO024:** ejemplo del enunciado y ensayo histórico PROVISIONAL, no venta realizada en Odoo. No se renombran sus resultados como S00005.
- **Sin contraseñas** en ninguna diapositiva ni captura.
- Hay una versión en PowerPoint con el mismo contenido, las mismas notas y algunas capturas: `PRESENTACION.pptx` (generada el 13/11 con las capturas del repositorio).

## Resumen de tiempos

| # | Diapositiva | Tiempo | Acumulado |
|---|---|---|---|
| 1 | El problema | 1:00 | 1:00 |
| 2 | La solución | 0:45 | 1:45 |
| 3 | Arquitectura | 1:15 | 3:00 |
| 4 | Caso de Odoo y pruebas auxiliares | 1:30 | 4:30 |
| 5 | Interfaces | 1:00 | 5:30 |
| 6 | Odoo | 0:45 | 6:15 |
| 7 | PostgreSQL y PL/pgSQL | 1:15 | 7:30 |
| 8 | Java/JDBC | 1:00 | 8:30 |
| 9 | PSP | 1:15 | 9:45 |
| 10 | Python y dashboard | 1:15 | 11:00 |
| 11 | Pruebas | 1:00 | 12:00 |
| 12 | Dificultades y decisiones | 0:45 | 12:45 |
| 13 | Limitaciones | 0:45 | 13:30 |
| 14 | Reparto del trabajo | 0:45 | 14:15 |
| 15 | Conclusiones | 0:45 | 15:00 |

---

## Diapositiva 1 · NOVA Sneakers: el problema · 1:00

**Puntos**
- Una fábrica de zapatillas que vende modelos de catálogo y pedidos personalizados para clubes y equipos.
- Necesita tres cosas: presencia digital, gestionar la venta hasta la fabricación y tratar los pedidos Custom.
- El encargo: actuar como una pequeña consultora y montar una primera solución integrada.
- Caso de Odoo: **S00005 · Club Atlético NOVA · PDF original de Berme**. PostgreSQL, PSP y Python conservan sus pruebas independientes.

**Figura recomendada:** el catálogo en escritorio (en el `.pptx`, la captura de la regresión del 13/11; en el repositorio, `01_Interfaces/evidencias/tienda/capturas-2026-11-13/escritorio_01_catalogo_disponibilidad.png`) y el logo `01_Interfaces/cliente/images/logo-nova.png` (blanco, va bien sobre fondo oscuro).

**Notas del orador**
Buenos días. Somos Omar, Álvaro y Berme, y os presentamos NOVA Sneakers. NOVA es una fábrica de zapatillas que vende modelos de catálogo y, sobre todo, pedidos personalizados para clubes. El enunciado nos pide actuar como una consultora: dar a la fábrica presencia digital, gestionar sus ventas y fabricación, y procesar los pedidos Custom. Presentamos S00005 del Club Atlético NOVA con las evidencias de Odoo de Berme. Los módulos auxiliares se demuestran con sus datos de prueba; no tenemos pruebas de que S00005 haya pasado por ellos. Os contaremos qué hemos hecho, cómo lo hemos probado y también qué falta.

---

## Diapositiva 2 · La solución: cinco piezas y sus evidencias · 0:45

**Puntos**
- **Web** responsive con catálogo de 100 modelos y solicitud Custom. Ampliaciones: tienda, panel y portal del trabajador.
- **Odoo** como núcleo de ventas y fabricación, documentado con S00005.
- **PostgreSQL + Java:** la base calcula importes, stock y auditoría; Java solo pide.
- **PSP:** un proceso padre y tres hijos procesan la exportación del pedido.
- **Python + Streamlit:** calidad de datos, 20 KPIs y análisis que se recalculan cada 60 s (265 pruebas).

**Figura recomendada:** un esquema de cinco tarjetas, una por pieza (en el `.pptx` está dibujado).

**Notas del orador**
La solución tiene cinco piezas. La web es la cara pública. Odoo, según el enunciado, es el núcleo del negocio; su flujo está documentado en el PDF de Berme, sin conexión en vivo en esta demo. Acceso a Datos tiene dos partes: una base PostgreSQL donde los cálculos importantes los hace la propia base, y una aplicación Java que la usa. PSP procesa el pedido Custom con varios procesos. Y Python analiza los datos y los enseña en un dashboard. La trazabilidad de S00005 entre los cinco bloques no está demostrada y se declara como limitación.

---

## Diapositiva 3 · Arquitectura · 1:15

**Puntos**
- Cuatro clientes (web y tienda, panel de administración, portal del trabajador y aplicación Java) y una sola base PostgreSQL.
- Cada cliente entra con su usuario y pasa con `SET ROLE` a un rol con los permisos justos: `panel_lectura`, `panel_reparto`, `portal_trabajador`, `tienda_web` o los `nova_*` de Java.
- Login único del personal: el administrador va al panel, el trabajador al portal y un comercial no tiene panel web.
- Integración por archivos: un CSV para PSP (script 15) y cinco CSV para Python (script 16).
- Odoo queda fuera por ahora; la frontera entre el ERP y lo auxiliar está explicada.

**Figura recomendada:** el diagrama de la sección 0 de `GUIA_DEFENSA.md` (en el `.pptx` está dibujado con cajas y flechas).

**Notas del orador**
Aquí se ve cómo se conectan las piezas. El navegador nunca habla con la base: pide a un servidor Node que solo escucha en este ordenador, y ese servidor entra con un usuario sin permisos que pasa a un rol con lo justo: solo lectura para el panel, el del portal del trabajador o el de la tienda. El personal entra por un login único: el administrador va al panel, el trabajador al portal, y un comercial no tiene panel web. La aplicación Java entra con otro usuario y pasa al rol del empleado que ha iniciado sesión. Desde la base salen dos exportaciones: un CSV con la ficha de fabricación para PSP y cinco CSV para Python. El enunciado permite integrar con ficheros y dice que se evalúa la coherencia de los datos, no la complejidad de la arquitectura.

---

## Diapositiva 4 · Caso de Odoo y pruebas auxiliares · 1:30

**Puntos**
- Odoo: S00005 del Club Atlético NOVA, PDF de Berme pp. 10–12.
- PostgreSQL → PSP → Python: CUSTOM-40 de PRUEBA; ensayo SO024 PROVISIONAL conservado.
- No hay prueba de que S00005 haya pasado por esos módulos.
- SO024 es el ejemplo del enunciado; no una venta que haya que recrear.

**Notas del orador**
Elegimos el pedido ya documentado, S00005. Conservamos sus capturas y el PDF sin alterar. Para ejecutar los módulos usamos los datos de prueba que ya funcionan. No presentamos CUSTOM-40 ni el ensayo SO024 como equivalentes de S00005 y no damos por cerrada la trazabilidad entre sistemas.

---

## Diapositiva 5 · Interfaces: una web responsive y accesible · 1:00

**Puntos**
- Las cinco partes que pide el enunciado; 100 modelos con precio, descripción y tallas.
- Responsive con CSS Grid y media queries: probada en 11 anchos, de 320 a 1440 px.
- Accesibilidad WCAG 2.1 AA: axe sin violaciones, 212/212 contrastes y Lighthouse 100 (11/11).
- Formulario Custom con validación y suma de pares; el envío es una simulación.
- Ampliaciones no pedidas: tienda con pago simulado, panel de administración y portal del trabajador, con un login único.

**Figura recomendada:** `01_Interfaces/evidencias/tienda/capturas-2026-11-13/escritorio_03_ficha_anadido.png` junto a `movil_01_catalogo_disponibilidad.png` (la misma web en escritorio y en móvil), y `01_Interfaces/evidencias/portal-trabajador/capturas/portal_pedidos_tras_avanzar.png` (el portal, como ampliación).

**Notas del orador**
La web tiene inicio, catálogo, ficha de producto, servicio Custom y una parte corporativa con contacto. Es responsive: el catálogo pasa de cuatro columnas a dos en el móvil con una media query, y la hemos probado en once anchos. Para la accesibilidad seguimos WCAG 2.1 nivel AA: etiquetas en todos los campos, foco visible, mensajes que lee el lector de pantalla y contraste suficiente. El formulario Custom valida los datos y suma los pares, pero no envía nada: lo dice en pantalla. La tienda online, el panel y el portal del trabajador son ampliaciones; las presentamos como tales.

---

## Diapositiva 6 · Odoo: evidencia de S00005 · 0:45

**Puntos**
- PDF original: venta S00005, fabricación WH/MO/00002, entrega WH/OUT/00005 y factura INV/2026/00001.
- Cliente: Club Atlético NOVA; 40 pares a 89 €/par en esa venta.
- Evidencia documental de Berme; sin ejecución en vivo desde este entorno.
- Conector no verificado aquí y rutas de pedidos sin activar; sin prueba de S00005 en PSP o PostgreSQL.

**Material:** abrir el PDF original pp. 10–12; no sustituir sus capturas ni atribuirles una fecha nueva.

**Notas del orador**
Odoo sí tiene trabajo documentado. Mostramos S00005 tal como figura en el PDF de Berme. SO024 es el ejemplo del enunciado, no una venta realizada por nosotros en Odoo. La ausencia de una exportación y conciliación con los módulos auxiliares sigue siendo una limitación.

---

## Diapositiva 7 · PostgreSQL y PL/pgSQL: la base manda · 1:15

**Puntos**
- 14 tablas: modelo → variante → SKU → existencias, y pedidos con sus líneas.
- 10 triggers: importes, stock al confirmar y al cancelar, y auditoría.
- El stock se descuenta una sola vez y nunca queda negativo, ni con dos confirmaciones a la vez.
- La auditoría sabe quién firma cada cambio y se deshace con un ROLLBACK.
- Batería SQL: 123 PASS, 0 FAIL y 1 error previsto (13/11).

**Figura recomendada:** `01_Interfaces/evidencias/tienda/capturas-2026-11-13/panel_15_auditoria_con_compras_web.png` (`log_eventos` visto desde el panel: altas, cambios de estado y cambios de stock).

**Notas del orador**
En la base de datos tomamos una decisión clara: lo importante lo calcula PostgreSQL, no las aplicaciones. Cuando se añade una línea, un trigger calcula el subtotal y otro recalcula el total del pedido desde cero. El stock se descuenta al confirmar, y una marca en cada línea impide descontarlo dos veces. Si dos personas confirman a la vez el último par, la comprobación va dentro del propio UPDATE y la segunda recibe «stock insuficiente». Cada cambio queda en la tabla de auditoría con el usuario que lo hizo, y si la transacción se deshace, el evento también desaparece.

---

## Diapositiva 8 · Java/JDBC: la aplicación pide, la base decide · 1:00

**Puntos**
- Swing con inicio de sesión y pestañas según el rol: administrador, comercial y trabajador.
- PreparedStatement, filtros combinables y transacciones con ROLLBACK.
- Dos barreras de permisos: la matriz en Java y el `SET ROLE` en PostgreSQL.
- Archivos externos: TXT de actividad, JSON de usuarios y CSV de la consulta.
- 47 de 47 pruebas; ventanas Swing, 76 de 76 (13/11).

**Figura recomendada:** `02_Acceso_Datos/evidencias/java-swing/06-admin.demo-consulta-filtrada.png` (13/11: consulta con dos filtros, «Buscar / Consultar» y «Limpiar filtros»).

**Notas del orador**
La aplicación Java crea pedidos con varias líneas en una sola transacción, los confirma o cancela y hace consultas con filtros que se pueden combinar; si un filtro está vacío, no filtra. Todos los valores van como parámetros. Los permisos se comprueban dos veces: en Java, y en la base, porque la conexión cambia al rol del usuario. Las pruebas se saltan Java a propósito y la base sigue negándolo. Además, Java escribe un TXT de actividad, un JSON de usuarios sin contraseñas y un CSV igual que la tabla.

---

## Diapositiva 9 · PSP: un padre y tres hijos · 1:15

**Puntos**
- Validador → analizador de tallas → generador de la ficha, cada uno en su propio proceso.
- Comunicación por stdin y stdout a través del padre; los errores, por stderr.
- Un hilo por tubería para que no se llenen; espera máxima de 10 s por hijo.
- Códigos de salida 0, 1, 2 y 3; si un paso falla, no se lanza el siguiente.
- Ficha para el taller y registro de cada ejecución: 27 de 27 pruebas; con el CSV de SO024 (provisional), código 0.

**Figura recomendada:** el texto de la ficha real `03_PSP/evidencias/ficha_taller_CUSTOM-40.txt` (en el `.pptx` está copiado tal cual, en letra de máquina).

**Notas del orador**
PSP es un subsistema auxiliar: no sustituye a Odoo ni escribe en la base. El proceso padre lanza tres programas Java con ProcessBuilder. Les pasa los datos por la entrada estándar y lee lo que devuelven; los errores llegan por la salida de error. Usamos un hilo por cada tubería porque, si se llenan, el padre y el hijo se quedan bloqueados. Cada hijo tiene diez segundos; si no termina, se cancela. Después de cada paso, el padre mira el código de salida y que la respuesta hable del mismo pedido, y solo entonces sigue. El resultado es esta ficha para el taller.

---

## Diapositiva 10 · Python y dashboard: datos fiables, conclusiones honestas · 1:15

**Puntos**
- 12 reglas de calidad; un pedido se analiza entero o no se analiza.
- 20 KPIs, conciliados con las consultas SQL de Acceso a Datos (y el caso N: 17 de 17 cifras).
- Bootstrap con semilla fija, RFM, KMeans (k = 4) y predicción frente a un baseline.
- Streamlit: recalcula cada 60 s, 4 estados, 6 filtros (también el de cliente) que se mantienen al refrescar, y último resultado válido marcado como DESACTUALIZADO.
- 265 pruebas; con la exportación de prueba, lo avanzado sale «NO CALCULABLE».

**Figura recomendada:** `04_Python/evidencias/dashboard/caso_k_3_ciclo_3.png` (13/11: el tercer ciclo de 60 s con el dashboard abierto en Edge sin tocarlo; estado, última comprobación, última actualización válida y KPIs). Los datos son de PRUEBA: decirlo.

**Notas del orador**
Python lee los cinco CSV que exporta la base y los pasa por doce reglas de calidad; si una línea es mala, se aparta su pedido entero, para no contar pedidos a medias. Con los datos válidos calcula veinte KPIs, que comprobamos contra SQL. Hicimos estadística con bootstrap, segmentación RFM y KMeans y una predicción de la demanda. Somos honestos con los resultados: la regresión no mejora claramente al método base, y lo decimos. El dashboard vuelve a leer y validar los datos cada minuto y, si llega un archivo roto, no enseña cifras a medias. Los filtros, también el de cliente, se mantienen al refrescar. La captura es del 13/11: el tercer ciclo de 60 s con el dashboard abierto en Edge sin tocarlo, con la exportación de PRUEBA.

---

## Diapositiva 11 · Pruebas · 1:00

**Puntos** (tabla)

| Bloque | Resultado | Fecha |
|---|---|---|
| SQL: scripts 01–23 y batería 09–16 | 123 PASS · 0 FAIL · 1 error previsto | 13/11 |
| Java: `PruebasRubrica` · ventanas Swing | 47/47 · 76/76 | 13/11 |
| PSP (`PruebasPsp`) | 27/27 | 13/11 |
| Python: `unittest` · salidas de `main.py` | 265 OK · 93 salidas comparadas (91 iguales, 2 con columnas nuevas a propósito y 4 archivos nuevos a propósito) | 13/11 |
| Web: interfaces · web completa · mejoras | 136/136 · 114/114 · 81/81 | 13/11 |
| Edge: compra · reparto · login único y portal | 139/139 · 29/29 · 82/82 | 13/11 |
| Node: panel · tienda · portal; SQL de la tienda | 23/23 · 39/39 · 24/24; 55/55 | 13/11 |
| SO024 de punta a punta (provisional) | 40 pares · 9 líneas · 3.996 € · PSP 0 | 13/11 |
| Lighthouse | Accesibilidad 100 | 11/11 |

**Figura recomendada:** la propia tabla. Fuentes: `06_Intermodular/evidencias/regresion-final/` (la regresión completa del 13/11 sobre el código final, con la hora y el entorno de cada batería) y `01_Interfaces/evidencias/web/lighthouse/` (11/11).

**Notas del orador**
Todo lo que os hemos contado está probado con la regresión completa del 13 de noviembre, sobre el código final, salvo Lighthouse, que es del 11. El único error de la batería SQL es a propósito: comprueba que un rol sin permiso no puede descontar stock. Las pruebas no solo miran que funcione lo bueno: también fuerzan errores, como pagar dos veces, un hijo que no termina, un CSV roto o un trabajador que intenta entrar en el panel. Lo que falta por probar lo tenemos apuntado y os lo contamos ahora.

---

## Diapositiva 12 · Dificultades y decisiones · 0:45

**Puntos**
- La firma de la auditoría se podía falsificar: ahora va firmada con HMAC y se comprueba en la base.
- Con un CSV grande, PSP se colgaba: un hilo por tubería y espera con límite de tiempo.
- Doble clic y dos personas a la vez: bloqueos en la base, no solo en el botón.
- El portal del trabajador llegó sin login ni roles: login único, un rol que no escribe en ninguna tabla y dos funciones que firman la auditoría (script 23).
- Decisión: integrar con CSV y procedimientos documentados, como permite el enunciado.

**Figura recomendada:** ninguna. Fuentes: `02_Acceso_Datos/documentacion/README.md` §9 («Un fallo que encontramos»), `03_PSP/README.md` («Por qué GestorProcesos usa tres hilos») y `servidor-admin/README.md` («El portal del trabajador»).

**Notas del orador**
Las dificultades nos han enseñado más que lo que salió a la primera. Descubrimos que cualquiera podía hacerse pasar por el administrador en la auditoría, y lo arreglamos firmando la identidad. En PSP, el programa se colgaba con archivos grandes hasta que entendimos cómo se llenan las tuberías. Y el portal del trabajador llegó sin login ni roles: lo pusimos detrás del mismo login que el panel, con un rol propio que no puede escribir en ninguna tabla y dos funciones que dejan la auditoría a nombre del trabajador.

---

## Diapositiva 13 · Limitaciones · 0:45

**Puntos**
- S00005 está documentado en Odoo, sin trazabilidad probada hacia PostgreSQL, PSP y Python.
- SO024 se conserva como ensayo PROVISIONAL del ejemplo; no hay que crear una venta oficial ni cambiar Runner X.
- Python usa una exportación de PRUEBA (**[PENDIENTE (los tres): la exportación REAL]**); el aprendizaje automático solo se ha podido calcular con datos sintéticos.
- Faltan la prueba de usabilidad con personas, el reparto real y el uso de la IA en la memoria, y el diagrama E-R en imagen.
- Es una demo: HTTP local, sesiones en memoria y pago simulado.

**Figura recomendada:** ninguna. Fuente: `06_Intermodular/rubricas/MATRIZ_RUBRICAS.md`.

**Notas del orador**
Queremos ser claros con lo que no está terminado. El PDF documenta S00005, pero no prueba su recorrido en los módulos auxiliares. SO024 es un ejemplo y su ensayo sigue siendo provisional, sin una venta realizada en Odoo. Python trabaja con una exportación de prueba y el análisis avanzado solo se puede calcular con datos sintéticos. Faltan la prueba de usabilidad con personas, el reparto real y el uso de la IA en la memoria, y el diagrama E-R en imagen. Y la seguridad está pensada para una demostración en local: en producción haría falta HTTPS, sesiones persistentes y una pasarela de pago real.

---

## Diapositiva 14 · Reparto del trabajo · 0:45

**Puntos** **[PENDIENTE (los tres): el reparto real]**

| Persona | Qué hizo | Qué revisó | Qué cambió del trabajo de otro |
|---|---|---|---|
| Omar | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| Álvaro | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| Berme | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |

- Los tres podemos explicar todos los módulos: lo hemos ensayado con el mismo simulacro.

**Figura recomendada:** ninguna. Tiene que coincidir con el punto 9 de la memoria («Reparto real del trabajo y contribuciones», IM-COM-29). No usar el número de commits como medida.

**Notas del orador**
**[PENDIENTE (los tres): lo escribe el equipo.]** Contadlo tal como fue, aunque no coincida con el plan inicial, y terminad diciendo que los tres podemos responder sobre cualquier parte.

---

## Diapositiva 15 · Conclusiones · 0:45

**Puntos**
- S00005 se documenta en Odoo; los módulos auxiliares conservan sus pruebas, sin trazabilidad de esa venta entre sistemas.
- Lo crítico está en la base: importes, stock y auditoría no dependen de la aplicación.
- Todo está medido con pruebas, y decimos lo que no funciona.
- Límite de entrega: S00005 sin trazabilidad entre sistemas y CSV de PRUEBA; no se prometen nuevas integraciones.
- Gracias. ¿Preguntas?

**Figura recomendada:** el logo `01_Interfaces/cliente/images/logo-nova.png`.

**Notas del orador**
Para terminar: hemos construido y probado los módulos disponibles, y conservamos el flujo S00005 documentado por Berme en Odoo. Las decisiones importantes están en la base de datos, de forma que ninguna aplicación puede dejar un importe o un stock incoherente. Hemos mostrado los resultados disponibles y sus límites: S00005 no está acreditado en PostgreSQL, PSP o Python, y la exportación Python sigue siendo de PRUEBA. Muchas gracias; estamos listos para vuestras preguntas.

---

## Si hay que recortar

- **10 minutos:** juntad la 2 con la 3, la 7 con la 8, y la 12 con la 13; la 11 en 30 segundos.
- **5 minutos:** 1, 3, 4, 13 y 15, y el resto de módulos en una frase cada uno.

## Preguntas del tribunal

- Cada respuesta, en 30 a 60 segundos: primero la idea y después el dato o la línea del código.
- Si preguntan por Odoo, distinguir S00005 documental de la conexión no verificada y de los ensayos SO024 PROVISIONAL.
- Las respuestas preparadas están en `GUIA_DEFENSA.md` y el ensayo, en `SIMULACION_DEFENSA.md`.
