# NOVA Sneakers · Matriz de evidencias para la defensa

Para cada asignatura, una tabla corta: **bloque de requisitos → archivo que lo demuestra → cómo enseñarlo**. El detalle requisito por requisito, con su estado y su riesgo, está en `06_Intermodular/rubricas/MATRIZ_RUBRICAS.md` (los IDs son los mismos).

**Rutas.** Las rutas completas parten de la raíz del repositorio; los nombres abreviados se refieren al archivo de su asignatura o a la carpeta de evidencias indicada. El cierre publicado conserva las pruebas nuevas en `06_Intermodular/evidencias/cierre-entrega-20261113/`. Es la regresión del código entregado (`4f09742`). La regresión anterior del **13/11/2026** (`1bcbb10`, antes `8cdc08c`, sobre un árbol anterior con la estructura de carpetas antigua) está en `06_Intermodular/evidencias/regresion-final/` y es **histórica**: se cita para lo que no se repitió en el cierre (memoria, §7.2). Su `README.md` dice la hora, el entorno y el resultado de cada batería. Lo poco que sigue fuera del repositorio se dice expresamente («en el informe de integración»).

**Estado:** OK = hecho y probado el 13/11 (o, si se dice, antes) · PARCIAL = hecho, pero falta una parte o la prueba es anterior · PROVISIONAL = solo con los datos provisionales de SO024 · PENDIENTE = no está hecho.

**Marcas:** [PENDIENTE (quién)] = falta de verdad · [DUDA PARA EL PROFESOR (Dn)] · [POR DECIDIR (los tres)] · [EQUIPO], [OMAR], [ÁLVARO] o [BERME] = lo tiene que confirmar o completar esa persona · **Límite declarado** = no está hecho y se entrega así.

---

## 1. Desarrollo de Interfaces

| Bloque | Requisitos | Estado | Evidencia | Cómo enseñarlo |
|---|---|---|---|---|
| Estructura mínima | IM-INT-04 | OK | `06_Intermodular/evidencias/regresion-final/05_web/02_interfaces.txt` (136/136); capturas `01_Interfaces/evidencias/web/capturas/*_01_*.png` y `*_07_*.png` (11/11) | Recorrer el menú en directo: catálogo, «Nuestra visión», Custom y contacto |
| Responsive | IM-INT-05 | OK | `02_interfaces.txt` (4 anchos) y `05_web/01_mejoras.txt` (11 anchos de 320 a 1440 px); capturas de escritorio y móvil | F12 → modo dispositivo a 390 px; enseñar las media queries de `css/inicio.css`. **[DUDA PARA EL PROFESOR (D7): qué «técnicas CSS vistas en clase» espera]** |
| Catálogo | IM-INT-06 | OK | `02_interfaces.txt` (100 tarjetas con precio y 6 fichas) y `01_mejoras.txt` (las 100 fichas) | Filtrar una colección y abrir una ficha |
| Servicio Custom | IM-INT-07, 12 | OK | `02_interfaces.txt`; capturas `01_Interfaces/evidencias/web/capturas/*_04_*.png` a `*_06_*.png` | Enviar vacío, sin pares y bien (§1 de `06_Intermodular/manuales/MANUAL_DEMOSTRACION.md`) |
| Calidad, accesibilidad | IM-INT-08, RA4 a)-i) | OK (salvo usabilidad) | axe sin violaciones (`02_interfaces.txt`, `01_mejoras.txt`, 13/11); contraste 212/212 (12/11, informe de integración); `01_Interfaces/evidencias/web/lighthouse/` (100/100, 11/11); `01_Interfaces/evidencias/web/README.md` (checklists) | Abrir el informe de Lighthouse; navegar con el tabulador; explicar WCAG 2.1 AA |
| Usabilidad con personas | RA4 i) | PENDIENTE | `01_Interfaces/memoria/PROCEDIMIENTO_USABILIDAD.md` (procedimiento y plantillas vacías). **Límite declarado:** no se ha hecho la prueba con 3 a 5 personas. **[EQUIPO: si se hace, añadir el informe]** | Enseñar las hojas rellenadas y la SUS **cuando se haga** |
| Estrategia e integración | RA8 a), b), g) | OK | `01_Interfaces/memoria/ESTRATEGIA_PRUEBAS_INTERFACES.md`; `06_Intermodular/evidencias/regresion-final/05_web/04_compra_edge.txt` (web → API → PostgreSQL → panel, 139/139) y `03_web.txt` (114/114) | Explicar los niveles de prueba y la tabla de trazabilidad |
| Memoria, punto 3 | IM-COM-23 | OK (redactado) | `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf` §3 | — |

## 2. Acceso a Datos (PostgreSQL + Java)

| Bloque | Requisitos | Estado | Evidencia | Cómo enseñarlo |
|---|---|---|---|---|
| Diseño E-R y normalización | AD-05 a 09, AD-117 | PARCIAL | `02_Acceso_Datos/modelo/sneaker-factory.dbm`, `02_Acceso_Datos/modelo-er/Modelo-Er-Intermodular.drawio`; `02_Acceso_Datos/memoria/MEMORIA_ACCESO_DATOS.md` §2. **[PENDIENTE (Álvaro): elegir el diagrama oficial y exportarlo a PNG]** | Abrir el diagrama y explicar modelo → variante → SKU y pedido → líneas |
| Scripts y reconstrucción | AD-10 a 13, 118, 132, 133 | OK | `06_Intermodular/evidencias/regresion-final/01_sql/01_montaje_01_23.txt` (23 scripts, salida 0); `08_manual_instalacion/` (el manual seguido en un clon nuevo) | Enseñar la tabla de orden de `06_Intermodular/manuales/MANUAL_INSTALACION.md` §3 |
| Las 8 consultas | AD-15 a 19, 134 | OK | `02_Acceso_Datos/sql/06_consultas.sql`; `01_sql/04_06_consultas.txt`: la HAVING devuelve **1 fila** (`NOVA-4-43`) | Ejecutar una con JOIN y la HAVING en pgAdmin; explicar por qué HAVING y no WHERE |
| Restricciones y transacción | AD-20, 21 | OK | `09_pruebas.sql` (E6, E8, E11), `11_dml_ejemplos.sql` (R1–R6); prueba D de `02_java_psp/02_pruebas_rubrica.txt` | `BEGIN;` + compra + `ROLLBACK;` en psql |
| Triggers: importes y stock | AD-26 a 31, 36, 129 | OK | `02_funciones.sql`, `03_triggers.sql`; `02_Acceso_Datos/memoria/MEMORIA_ACCESO_DATOS.md` §6; pruebas A, B y C | Tabla de triggers; confirmar dos veces y ver que el stock baja una vez |
| Auditoría | AD-33 a 35, 63, 122 | OK (dos sesiones: 8/11, a mano) | `08_auditoria.sql`; prueba A5; `02_Acceso_Datos/documentacion/README.md` §11 | «Ver auditoría» como `admin.demo`; explicar el operador firmado |
| Java: alta, detalle, confirmar y cancelar | AD-14, 37 a 43, 123 | OK | `PanelNuevoPedido.java`, `PedidoDAO.java`; `06_Intermodular/evidencias/regresion-final/07_ventanas_swing/resultado.txt` (76/76); 19 capturas en `02_Acceso_Datos/evidencias/java-swing/` | §2 de `06_Intermodular/manuales/MANUAL_DEMOSTRACION.md` |
| Consulta visual y filtros | AD-44 a 50, 125 | OK | Prueba E; capturas 06, 08 y 19 (tras «Limpiar filtros») de `java-swing/` | Filtrar por cliente y estado; «Limpiar filtros» |
| Roles y permisos | AD-51, 53 a 74, 124 | OK (AD-57, ver duda) | `07_seguridad.sql`, `17_usuario_java.sql`, `Sesion.java`; pruebas L, P y F. **[DUDA PARA EL PROFESOR (D10): ¿basta con asignar roles, o hay que poder editar los permisos?]** | Entrar como `taller.demo` y que le denieguen; explicar las dos barreras |
| TXT de actividad | AD-82 a 91, 126 | OK | `Archivos.java`; prueba G; `java-swing/actividad_sneaker-prueba-ventanas.txt` y `02_java_psp/02_salidas_java/actividad_sneaker.txt` | Tres consultas → tres líneas nuevas en `actividad_sneaker.txt` |
| JSON de usuarios | AD-92 a 100, 127 | OK (ninguna prueba fuerza un ROLLBACK antes de exportar, AD-96) | `UsuarioDAO.java`; prueba I; `02_salidas_java/usuarios_sneaker.json` | Crear y desactivar un usuario y abrir el JSON |
| Indicadores y CSV | AD-101 a 108, 112, 128 | OK | `IndicadoresDAO.java`; prueba J; capturas 11 y 12 de `java-swing/` | Pestaña Indicadores con dos umbrales; exportar el CSV |
| Pruebas A–J | AD-75 a 81, 109 a 111 | OK (las capturas de A, B, C, D, G e I en la ventana, en la demo) | `02_java_psp/02_pruebas_rubrica.txt` (47/47) y `08_manual_instalacion/` (`pruebas.bat`, 47/47) | Lanzar `pruebas.bat` en una base de prueba |
| Integración con PSP y Odoo | AD-22 a 25, 107, 120 | PARCIAL (sin trazabilidad acreditada de S00005 hacia PSP) | `15_exportar_fabricacion.sql`; `06_Intermodular/evidencias/regresion-final/06_so024_provisional/`. No hay equivalencia acreditada de SKU ni de número de pedido con S00005. | §3 de la demo |
| Caso común | AD-113 a 116 | PROVISIONAL | `06_so024_provisional/00_cadena.txt`; `03_PSP/evidencias/so024_provisional/`. Ensayo histórico, no prueba de S00005; falta evidencia completa de la demo desde la ventana Java. | Demo con CUSTOM-40 de PRUEBA; no atribuirla a S00005 |
| Memoria del módulo | AD-121 | OK (redactada; con límites de evidencia manual y E-R; S00005 no acreditado en AD) | `02_Acceso_Datos/memoria/MEMORIA_ACCESO_DATOS.md` | — |

## 3. PSP

| Bloque | Requisitos | Estado | Evidencia | Cómo enseñarlo |
|---|---|---|---|---|
| Coordinador y procesos hijos | IM-PSP-04, 06, 07, 16, 23, 28 | OK | `03_PSP/ProcesadorPedidosCustom.java`, `GestorProcesos.java`; `06_Intermodular/evidencias/regresion-final/02_java_psp/04_psp_pruebas.txt` (27/27) y `05_psp_custom40.txt` | §3 de la demo |
| Comunicación stdin/stdout | IM-PSP-08, 24, 25 | OK | Pruebas 06a, 06b y 07 de `PruebasPsp`; `03_PSP/evidencias/03_hijos_por_separado.txt` | Lanzar un hijo suelto con una tubería (`03_PSP/memoria/DOCUMENTACION_PSP.md` §12) |
| Códigos, errores y tiempos | IM-PSP-09, 17, 26, 27 | OK | Pruebas 08 a 12m; `02_java_psp/06_psp_error_no_existe.txt` (código 1) y `06_psp_error_cantidad_cero.txt` (código 2) | Lanzar `prueba_cantidad_cero.csv`; explicar la tabla de códigos |
| Función auxiliar sin sustituir a Odoo | IM-PSP-05, 15 | OK | `03_PSP/README.md` («Lo que no hace»); pie de la ficha | Leer el pie de `03_PSP/evidencias/ficha_taller_CUSTOM-40.txt` |
| Salida relacionada con el pedido de Odoo | IM-PSP-10, 14, 29 | PARCIAL (sin trazabilidad acreditada de S00005 hacia PSP) | `ficha_taller_<ref>.txt`, `registro_psp.txt`; `03_PSP/evidencias/so024_provisional/ficha_taller_SO024_PROVISIONAL.txt`. S00005 existe en el PDF, pero no hay una exportación/ficha acreditada de ese pedido en PSP. | Señalar la referencia SO024 en el CSV, la respuesta `OK;`, la ficha y el registro |
| Documentación y depuración | IM-PSP-RA1-i, IM-COM-25 | OK (redactada; `03_PSP/README.md` al día) | `03_PSP/memoria/DOCUMENTACION_PSP.md`; `03_PSP/README.md` | — |
| Comprobación rápida de Berme | — | CORRECTA EN EL CIERRE | `06_Intermodular/evidencias/cierre-entrega-20261113/psp_comprobador.txt` | Corrección de Berme incorporada en 4f09742; el fallo anterior se conserva como histórico |

## 4. Python

| Bloque | Requisitos | Estado | Evidencia | Cómo enseñarlo |
|---|---|---|---|---|
| Pipeline, ETL y calidad | PY-10, 11, 42 a 64 | OK | `04_Python/pipeline.py`, `calidad.py`; `calidad_datos.md`; `06_Intermodular/evidencias/regresion-final/04_python/02_unittest.txt` (265 OK) | `main.py --modo sintetico-errores` → «DATOS BLOQUEADOS»; pestaña Calidad |
| Vistas base y cardinalidades | PY-65 a 69 | OK | `analiticas.py` (`validate=` e `indicator=True`); `diccionario_datos.md`; `test_pedido_custom_de_40_pares_linea_a_linea` (caso A) | Explicar por qué 9 líneas son 1 pedido con SO024 (`06_so024_provisional/06_pedidos_unicos_SO024.csv`) |
| DataFrames, metadatos y KPIs | PY-72 a 82, 142 a 160 | OK | `kpis_y_graficos.md`; `metadatos.py` y `metadatos_dataframes.csv` (fecha de corte, reglas, filtros, filas de origen y función de cada CSV); `outputs/real/kpis.csv` | Pestaña Dirección y Productos; enseñar un KPI NO CALCULABLE y por qué; abrir una descarga con sus metadatos |
| Conciliación con SQL | PY-68, 155, 201, 210 | OK | `conciliacion_sql.md`; P-A, P-B y P-C (21/21) y el caso N (N-1, N-2 y N-3: **17/17**) en `entrada_acc/conciliacion_sql/`; `04_python/03_salidas_93.txt` | Comparar P-A con la tarjeta de Dirección; enseñar `contraste_sql_caso_n.csv` |
| Estadística | PY-83 a 90 | OK | `estadistica.md`; `hipotesis.csv`, `bootstrap_ticket_medio.csv` | Explicar media frente a mediana y «evidencia insuficiente» |
| RFM y KMeans | PY-91 a 96 | OK (sintético) | `segmentacion_y_prediccion.md` | Pestaña Clientes con el origen sintético |
| Predicción y baseline | PY-102 a 109 | OK (sintético) | `segmentacion_y_prediccion.md` §3; `metricas_prediccion.csv` | Pestaña Predicción: MAE y RMSE y por qué no mejora |
| Dashboard, filtros y refresco de 60 s | PY-17, 129 a 141, 161 a 175 | OK | `app_dashboard.py`; `filtros.py` (6 filtros: periodo, modelo, talla, tipo, estado y cliente); `dashboard.md`; caso K en Edge (`04_Python/evidencias/dashboard/caso_k_*`, 13/11); pruebas del refresco que conserva filtros y pestaña y de R6 en `04_python/02_unittest.txt` | §4 de la demo |
| Datos reales frente a sintéticos | PY-29 a 41 | OK, salvo la exportación REAL | `entrada_acc/ORIGEN.txt` (`Tipo: PRUEBA`); `datos_sinteticos.md`. **Límite declarado:** se entrega la exportación de PRUEBA; no hay exportación REAL de la base del equipo | Cambiar el origen y ver el color y el aviso |
| Pruebas R1–R6 y casos A–O | PY-183 a 189, 197 a 211 | PARCIAL | `04_Python/memoria/INFORME_TECNICO_PYTHON.md` (tabla A–O). R6, A, K y N hechos; los que piden un alta o un cambio real en ACC siguen limitados por la exportación REAL y evidencias de alta/cambios en ACC; no exigen el identificador SO024 | — |
| Informes técnico y ejecutivo | PY-110, 111, 194, 215 | OK (redactados) | `04_Python/memoria/INFORME_TECNICO_PYTHON.md`; `04_Python/informe_ejecutivo.md` (cinco decisiones con prioridad, urgencia, impacto esperado y sustento) | Leer la decisión de prioridad 1 y su tabla de sustento |

## 5. Sistemas de Gestión Empresarial (Odoo)

**Actualización 13/11/2026:** existe el PDF de Berme en `odoo/documentacion/Odoo-NOVA-Sneakers.pdf`, con aportaciones OD-01 a OD-06. El mapa por páginas y sus límites están en `06_Intermodular/SO024/INTEGRACION_ODOO_SO024.md`. El caso elegido es S00005 del Club Atlético NOVA, documentado en el PDF. SO024 es el ejemplo del enunciado, no una venta realizada en Odoo. La tabla de abajo valora el material disponible; no debe interpretarse como ausencia de trabajo de Berme. La API de esta candidata sigue sin activarse ni probarse contra Odoo.

| Bloque | Requisitos | Estado | Evidencia | Cómo enseñarlo |
|---|---|---|---|---|
| Entorno e instalación | IM-SGE-06, 08; RA1, RA2 | EVIDENCIA DOCUMENTAL | PDF pp. 3–6: Ubuntu/OrbStack, Odoo y módulos | Mostrar como evidencia documental y explicar límites; ver estado final |
| Empresa, usuarios y roles | IM-SGE-09 | PARCIAL | PDF pp. 6 y 17: compañía y algunos perfiles; no todos acreditados | Mostrar como evidencia documental y explicar límites; ver estado final |
| Clientes, productos y venta | IM-SGE-10 a 12, 17 | DOCUMENTAL; perfiles/alcance pendientes según matriz | PDF pp. 10, 13 y 16: clientes, venta S00005 y variantes; sin correspondencia acreditada con los módulos auxiliares | Mostrar S00005 como caso de Odoo; SO024 es el ejemplo y su ensayo se conserva por separado |
| Fabricación, inventario y factura | IM-SGE-13 a 15 | EVIDENCIA DOCUMENTAL | PDF pp. 7–12 y 17: recorrido histórico; no ejecución en vivo aquí | Mostrar como evidencia documental y explicar límites; ver estado final |
| Trazabilidad y exportación | IM-SGE-16, 21; RA3, RA4 | PARCIAL | PDF pp. 10–12; sin CSV acreditado de S00005 hacia los módulos auxiliares | Mostrar como evidencia documental y explicar límites; ver estado final |
| ERP configurado y copia de seguridad | IM-COM-16 | PARCIAL | Configuración documentada en el PDF (pp. 3-8 y 16-17) y procedimiento de copia (p. 19). Falta la copia de seguridad de Berme: no consta ninguna copia hecha ni restaurada. **[BERME: datos de la copia y de la restauración, o confirmar que no hay]** | Enseñar la p. 19 y decir que la copia no está registrada |

Correspondencia de la lista histórica de tareas con el PDF: `05_Odoo/CHECKLIST_ODOO_BERME.md`, tabla inicial. La lista de casillas que sigue es del plan SO024, ya sustituido.

## 6. Proyecto Intermodular (común e integración)

| Bloque | Requisitos | Estado | Evidencia | Cómo enseñarlo |
|---|---|---|---|---|
| Memoria técnica | IM-COM-18, 21 a 29 | PARCIAL (versión de entrega; faltan los campos [EQUIPO], [OMAR], [ÁLVARO] y [BERME] del punto 9: reparto real y uso de la IA de cada persona) | `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf` | — |
| Manual de demostración | IM-COM-19, 32 | PARCIAL (ERP documental, sin ejecución en vivo ni trazabilidad entre sistemas) | `06_Intermodular/manuales/MANUAL_DEMOSTRACION.md` | Ensayarlo entero al menos una vez |
| Documentación reproducible | IM-COM-05 | OK | `06_Intermodular/manuales/MANUAL_INSTALACION.md`, seguido el 13/11 en un clon nuevo y una base nueva (`06_Intermodular/evidencias/regresion-final/08_manual_instalacion/`); `README.md` | — |
| Presentación | IM-COM-20 | PARCIAL | Guion vigente: `06_Intermodular/defensa/PRESENTACION.md`, actualizado con S00005. El `.pptx` tiene todavía el contenido anterior a S00005 y contradice el guion. **[EQUIPO: corregirlo diapositiva a diapositiva o retirarlo]** | Usar el guion Markdown, no las afirmaciones antiguas del PowerPoint |
| Repositorio publicado | IM-COM-02, 15 | OK (documentado) | `main`: cierre publicado mediante la PR #2 (`4a25d5a`) y revisión documental con la PR #3 (`372f811`). La historia publicada se reescribió el 13/11 (`06_Intermodular/EQUIVALENCIAS_COMMITS.md`) | Enseñar las PR y el historial con las aportaciones de los tres |
| Sin credenciales y datos ficticios | IM-COM-03, 04 | OK | `.gitignore`; búsqueda de las claves de las pruebas en las evidencias y la documentación (entonces `pruebas/` y `docs/`): 0 coincidencias (`06_Intermodular/evidencias/regresion-final/README.md`). **[DUDA PARA EL PROFESOR (D12): cómo se le dan las contraseñas de demostración]** | — |
| Modelo de datos común | IM-ITG-09 a 15 | PARCIAL (sin correspondencia de S00005 acreditada) | `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf` §6; `06_Intermodular/SO024/caso-comun-SO024.md`; `06_Intermodular/SO024/SO024_DATOS_PENDIENTES.md` | Distinguir el modelo del ensayo de la falta de correspondencia acreditada de S00005 |
| Ensayo histórico SO024 PROVISIONAL, no S00005 | IM-ITG-04, 16, 18 | PROVISIONAL | `06_Intermodular/evidencias/regresion-final/06_so024_provisional/00_cadena.txt` (de principio a fin, 13/11). No acredita S00005; los siete acuerdos del plan SO024 ya no son una obligación de entrega. | Mostrar el PDF de S00005 y reconocer que no hay prueba de ese pedido en todos los módulos |
| Frontera ERP/auxiliar y ampliaciones productivas | IM-ITG-06 | OK (redactada) | `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf` §2.3 y §2.4 | Explicarlo en el cierre |
| Reparto real | IM-COM-29, 33 | PARCIAL | `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf` §9: datos de Git (113/25/9 y 1 de «t»), declaración de la IA de Omar y huecos. **[EQUIPO: completar el reparto real y el uso de la IA de cada persona]** | Cada uno explica lo suyo y lo de otro |
| Datos de integración | IM-COM-17 | PARCIAL (no hay exportación acreditada de S00005 desde Odoo) | `03_PSP/pruebas/custom40.csv`, `03_PSP/datos/`, `04_Python/entrada_acc/`, `03_PSP/evidencias/so024_provisional/SO024_PROVISIONAL_fabricacion.csv` | — |

## 7. Ampliaciones (no obligatorias)

**[DUDA PARA EL PROFESOR (D6): ¿cuentan como ampliación o pueden restar (AD-136)?]**

| Ampliación | Evidencia (13/11, árbol final) | Cómo enseñarla |
|---|---|---|
| Tienda online | `06_Intermodular/evidencias/regresion-final/05_web/04_compra_edge.txt` (139/139), `01_sql/05_sql_tienda.txt` (55/55), `03_node/03_test_tienda.txt` (39/39); capturas en `01_Interfaces/evidencias/tienda/capturas-2026-11-13/` | `06_Intermodular/manuales/MANUAL_DEMOSTRACION.md`, parte opcional |
| Panel de administración (Álvaro) | `03_node/02_npm_test_desechable.txt` (23/23); `01_Interfaces/evidencias/tienda/capturas-2026-11-13/panel_*.png`; `01_Interfaces/evidencias/panel-admin/` (11/11) | Ídem |
| Reparto | `01_sql/07_sql_reparto_con23.txt` (37/37), `05_web/05_recorrido_reparto.txt` (29/29); capturas en `01_Interfaces/evidencias/reparto-y-correo/` | Ídem |
| Recibo con Resend y Ethereal | 7 + 7 pruebas simuladas dentro de `03_test_tienda.txt`; Ethereal sin red y sin respuesta 5/5 y 5/5 (`05_web/08_*`, `09_*`); compra real contra Ethereal con datos ficticios 16/16 (`05_web/07_ethereal_real.txt`); capturas y datos en `01_Interfaces/evidencias/correo-ethereal/` | Ídem |
| 100 modelos, colores, bloque de compra y probador | `05_web/01_mejoras.txt` (81/81); contraste 212/212 (12/11, informe de integración). **[ÁLVARO: confirmar si da por buena la adaptación de su paleta]** | Ídem |
| Portal del trabajador y login único (Berme) | `03_node/04_test_portal.txt` (24/24), `01_sql/08_sql_portal.txt` (50/50), `05_web/06_edge_portal.txt` (82/82, axe 0); capturas en `01_Interfaces/evidencias/portal-trabajador/capturas/`. **[BERME: revisar y confirmar los cambios en sus archivos]** | Entrar en `login.html` como `admin.demo`, `taller.demo` y `tienda.demo`; avanzar un pedido en el portal y verlo en la auditoría del panel |
