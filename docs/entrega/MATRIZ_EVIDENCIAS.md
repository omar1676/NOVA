# NOVA Sneakers · Matriz de evidencias para la defensa

Para cada asignatura, una tabla corta: **bloque de requisitos → archivo que lo demuestra → cómo enseñarlo**. El detalle requisito por requisito, con su estado y su riesgo, está en `docs/entrega/MATRIZ_RUBRICAS.md` (los IDs son los mismos).

**Rutas.** Todas son relativas a la raíz del repositorio. La regresión completa del **13/11/2026** sobre el árbol final (`8cdc08c`) está en `pruebas/regresion-final/`; su `README.md` dice la hora, el entorno y el resultado de cada batería. Lo poco que sigue fuera del repositorio se dice expresamente («en el informe de integración»).

**Estado:** OK = hecho y probado el 13/11 (o, si se dice, antes) · PARCIAL = hecho, pero falta una parte o la prueba es anterior · PROVISIONAL = solo con los datos provisionales de SO024 · PENDIENTE = no está hecho.

**Marcas:** [PENDIENTE (quién)] = falta de verdad · [DUDA PARA EL PROFESOR (Dn)] · [POR DECIDIR (los tres)] · [REVISIÓN (Álvaro o Berme) en la PR].

---

## 1. Desarrollo de Interfaces

| Bloque | Requisitos | Estado | Evidencia | Cómo enseñarlo |
|---|---|---|---|---|
| Estructura mínima | IM-INT-04 | OK | `pruebas/regresion-final/05_web/02_interfaces.txt` (136/136); capturas `pruebas/interfaces/capturas/*_01` y `*_07` (11/11) | Recorrer el menú en directo: catálogo, «Nuestra visión», Custom y contacto |
| Responsive | IM-INT-05 | OK | `02_interfaces.txt` (4 anchos) y `05_web/01_mejoras.txt` (11 anchos de 320 a 1440 px); capturas de escritorio y móvil | F12 → modo dispositivo a 390 px; enseñar las media queries de `css/inicio.css`. **[DUDA PARA EL PROFESOR (D7): qué «técnicas CSS vistas en clase» espera]** |
| Catálogo | IM-INT-06 | OK | `02_interfaces.txt` (100 tarjetas con precio y 6 fichas) y `01_mejoras.txt` (las 100 fichas) | Filtrar una colección y abrir una ficha |
| Servicio Custom | IM-INT-07, 12 | OK | `02_interfaces.txt`; capturas `pruebas/interfaces/capturas/*_04` a `*_06` | Enviar vacío, sin pares y bien (paso 2 de `MANUAL_DEMOSTRACION.md`) |
| Calidad, accesibilidad | IM-INT-08, RA4 a)-i) | OK (salvo usabilidad) | axe sin violaciones (`02_interfaces.txt`, `01_mejoras.txt`, 13/11); contraste 212/212 (12/11, informe de integración); `pruebas/interfaces/lighthouse/` (100/100, 11/11); `pruebas/interfaces/README.md` (checklists) | Abrir el informe de Lighthouse; navegar con el tabulador; explicar WCAG 2.1 AA |
| Usabilidad con personas | RA4 i) | PENDIENTE | `PROCEDIMIENTO_USABILIDAD.md` (procedimiento y plantillas vacías). **[PENDIENTE (los tres): la prueba con 3 a 5 personas y su informe]** | Enseñar las hojas rellenadas y la SUS **cuando se haga** |
| Estrategia e integración | RA8 a), b), g) | OK | `ESTRATEGIA_PRUEBAS_INTERFACES.md`; `pruebas/regresion-final/05_web/04_compra_edge.txt` (web → API → PostgreSQL → panel, 139/139) y `03_web.txt` (114/114) | Explicar los niveles de prueba y la tabla de trazabilidad |
| Memoria, punto 3 | IM-COM-23 | OK (redactado) | `MEMORIA.md` §3 | — |

## 2. Acceso a Datos (PostgreSQL + Java)

| Bloque | Requisitos | Estado | Evidencia | Cómo enseñarlo |
|---|---|---|---|---|
| Diseño E-R y normalización | AD-05 a 09, AD-117 | PARCIAL | `acceso-datos/modelo/sneaker-factory.dbm`, `acceso-datos/modelo-er/Modelo-Er-Intermodular.drawio`; `MEMORIA_ACCESO_DATOS.md` §2. **[PENDIENTE (Álvaro): elegir el diagrama oficial y exportarlo a PNG]** | Abrir el diagrama y explicar modelo → variante → SKU y pedido → líneas |
| Scripts y reconstrucción | AD-10 a 13, 118, 132, 133 | OK | `pruebas/regresion-final/01_sql/01_montaje_01_23.txt` (23 scripts, salida 0); `08_manual_instalacion/` (el manual seguido en un clon nuevo) | Enseñar la tabla de orden de `MANUAL_INSTALACION.md` §3 |
| Las 8 consultas | AD-15 a 19, 134 | OK | `acceso-datos/sql/06_consultas.sql`; `01_sql/04_06_consultas.txt`: la HAVING devuelve **1 fila** (`NOVA-4-43`) | Ejecutar una con JOIN y la HAVING en pgAdmin; explicar por qué HAVING y no WHERE |
| Restricciones y transacción | AD-20, 21 | OK | `09_pruebas.sql` (E6, E8, E11), `11_dml_ejemplos.sql` (R1–R6); prueba D de `02_java_psp/02_pruebas_rubrica.txt` | `BEGIN;` + compra + `ROLLBACK;` en psql |
| Triggers: importes y stock | AD-26 a 31, 36, 129 | OK | `02_funciones.sql`, `03_triggers.sql`; `MEMORIA_ACCESO_DATOS.md` §6; pruebas A, B y C | Tabla de triggers; confirmar dos veces y ver que el stock baja una vez |
| Auditoría | AD-33 a 35, 63, 122 | OK (dos sesiones: 8/11, a mano) | `08_auditoria.sql`; prueba A5; `acceso-datos/documentacion/README.md` §11 | «Ver auditoría» como `admin.demo`; explicar el operador firmado |
| Java: alta, detalle, confirmar y cancelar | AD-14, 37 a 43, 123 | OK | `PanelNuevoPedido.java`, `PedidoDAO.java`; `pruebas/regresion-final/07_ventanas_swing/resultado.txt` (76/76); 19 capturas en `pruebas/acceso-datos/java-swing/` | Paso 4 de `MANUAL_DEMOSTRACION.md` |
| Consulta visual y filtros | AD-44 a 50, 125 | OK | Prueba E; capturas 06, 08 y 19 (tras «Limpiar filtros») de `java-swing/` | Filtrar por cliente y estado; «Limpiar filtros» |
| Roles y permisos | AD-51, 53 a 74, 124 | OK (AD-57, ver duda) | `07_seguridad.sql`, `17_usuario_java.sql`, `Sesion.java`; pruebas L, P y F. **[DUDA PARA EL PROFESOR (D10): ¿basta con asignar roles, o hay que poder editar los permisos?]** | Entrar como `taller.demo` y que le denieguen; explicar las dos barreras |
| TXT de actividad | AD-82 a 91, 126 | OK | `Archivos.java`; prueba G; `java-swing/actividad_sneaker-prueba-ventanas.txt` y `02_java_psp/02_salidas_java/actividad_sneaker.txt` | Tres consultas → tres líneas nuevas en `actividad_sneaker.txt` |
| JSON de usuarios | AD-92 a 100, 127 | OK (ninguna prueba fuerza un ROLLBACK antes de exportar, AD-96) | `UsuarioDAO.java`; prueba I; `02_salidas_java/usuarios_sneaker.json` | Crear y desactivar un usuario y abrir el JSON |
| Indicadores y CSV | AD-101 a 108, 112, 128 | OK | `IndicadoresDAO.java`; prueba J; capturas 11 y 12 de `java-swing/` | Pestaña Indicadores con dos umbrales; exportar el CSV |
| Pruebas A–J | AD-75 a 81, 109 a 111 | OK (las capturas de A, B, C, D, G e I en la ventana, en la demo) | `02_java_psp/02_pruebas_rubrica.txt` (47/47) y `08_manual_instalacion/` (`pruebas.bat`, 47/47) | Lanzar `pruebas.bat` en una base de prueba |
| Integración con PSP y Odoo | AD-22 a 25, 107, 120 | PARCIAL (falta Odoo) | `15_exportar_fabricacion.sql`; `pruebas/regresion-final/06_so024_provisional/`. **[PENDIENTE (Berme): la tabla de equivalencias de SKU y de número de pedido con Odoo]** | Paso 5 de la demo |
| Caso común | AD-113 a 116 | PROVISIONAL | `06_so024_provisional/00_cadena.txt`; `pruebas/psp/so024_provisional/`. **[PENDIENTE (los tres): los 7 datos y el SO024 oficial desde la ventana Java]** | Pasos 4 y 5 de la demo, con los datos acordados |
| Memoria del módulo | AD-121 | OK (redactada; con los PENDIENTE de SO024 y del E-R) | `MEMORIA_ACCESO_DATOS.md` | — |

## 3. PSP

| Bloque | Requisitos | Estado | Evidencia | Cómo enseñarlo |
|---|---|---|---|---|
| Coordinador y procesos hijos | IM-PSP-04, 06, 07, 16, 23, 28 | OK | `psp/ProcesadorPedidosCustom.java`, `GestorProcesos.java`; `pruebas/regresion-final/02_java_psp/04_psp_pruebas.txt` (27/27) y `05_psp_custom40.txt` | Paso 6 de la demo |
| Comunicación stdin/stdout | IM-PSP-08, 24, 25 | OK | Pruebas 06a, 06b y 07 de `PruebasPsp`; `pruebas/psp/03_hijos_por_separado.txt` | Lanzar un hijo suelto con una tubería (`DOCUMENTACION_PSP.md` §12) |
| Códigos, errores y tiempos | IM-PSP-09, 17, 26, 27 | OK | Pruebas 08 a 12m; `02_java_psp/06_psp_error_no_existe.txt` (código 1) y `06_psp_error_cantidad_cero.txt` (código 2) | Lanzar `prueba_cantidad_cero.csv`; explicar la tabla de códigos |
| Función auxiliar sin sustituir a Odoo | IM-PSP-05, 15 | OK | `psp/README.md` («Lo que no hace»); pie de la ficha | Leer el pie de la ficha de SO024 |
| Salida relacionada con el pedido de Odoo | IM-PSP-10, 14, 29 | PARCIAL (falta Odoo) | `ficha_taller_<ref>.txt`, `registro_psp.txt`; `pruebas/psp/so024_provisional/ficha_taller_SO024_PROVISIONAL.txt`. **[PENDIENTE (Berme): el pedido y su exportación en Odoo]** | Señalar la referencia SO024 en el CSV, la respuesta `OK;`, la ficha y el registro |
| Documentación y depuración | IM-PSP-RA1-i, IM-COM-25 | OK (redactada; `psp/README.md` al día) | `DOCUMENTACION_PSP.md`; `psp/README.md` | — |
| Comprobación rápida de Berme | — | Falla, ya se sabe | `02_java_psp/07_comprobar_psp.txt`. **[REVISIÓN (Berme) en la PR: traer su arreglo `862e37d`]** | — |

## 4. Python

| Bloque | Requisitos | Estado | Evidencia | Cómo enseñarlo |
|---|---|---|---|---|
| Pipeline, ETL y calidad | PY-10, 11, 42 a 64 | OK | `python-analisis/pipeline.py`, `calidad.py`; `calidad_datos.md`; `pruebas/regresion-final/04_python/02_unittest.txt` (265 OK) | `main.py --modo sintetico-errores` → «DATOS BLOQUEADOS»; pestaña Calidad |
| Vistas base y cardinalidades | PY-65 a 69 | OK | `analiticas.py` (`validate=` e `indicator=True`); `diccionario_datos.md`; `test_pedido_custom_de_40_pares_linea_a_linea` (caso A) | Explicar por qué 9 líneas son 1 pedido con SO024 (`06_so024_provisional/06_pedidos_unicos_SO024.csv`) |
| DataFrames, metadatos y KPIs | PY-72 a 82, 142 a 160 | OK | `kpis_y_graficos.md`; `metadatos.py` y `metadatos_dataframes.csv` (fecha de corte, reglas, filtros, filas de origen y función de cada CSV); `outputs/real/kpis.csv` | Pestaña Dirección y Productos; enseñar un KPI NO CALCULABLE y por qué; abrir una descarga con sus metadatos |
| Conciliación con SQL | PY-68, 155, 201, 210 | OK | `conciliacion_sql.md`; P-A, P-B y P-C (21/21) y el caso N (N-1, N-2 y N-3: **17/17**) en `entrada_acc/conciliacion_sql/`; `04_python/03_salidas_93.txt` | Comparar P-A con la tarjeta de Dirección; enseñar `contraste_sql_caso_n.csv` |
| Estadística | PY-83 a 90 | OK | `estadistica.md`; `hipotesis.csv`, `bootstrap_ticket_medio.csv` | Explicar media frente a mediana y «evidencia insuficiente» |
| RFM y KMeans | PY-91 a 96 | OK (sintético) | `segmentacion_y_prediccion.md` | Pestaña Clientes con el origen sintético |
| Predicción y baseline | PY-102 a 109 | OK (sintético) | `segmentacion_y_prediccion.md` §3; `metricas_prediccion.csv` | Pestaña Predicción: MAE y RMSE y por qué no mejora |
| Dashboard, filtros y refresco de 60 s | PY-17, 129 a 141, 161 a 175 | OK | `app_dashboard.py`; `filtros.py` (6 filtros: periodo, modelo, talla, tipo, estado y cliente); `dashboard.md`; caso K en Edge (`python-analisis/evidencias/dashboard/caso_k_*`, 13/11); pruebas del refresco que conserva filtros y pestaña y de R6 en `04_python/02_unittest.txt` | Paso 7 de la demo |
| Datos reales frente a sintéticos | PY-29 a 41 | OK, salvo la exportación REAL | `entrada_acc/ORIGEN.txt` (`Tipo: PRUEBA`); `datos_sinteticos.md`. **[PENDIENTE (los tres): la exportación REAL de la base del equipo]** | Cambiar el origen y ver el color y el aviso |
| Pruebas R1–R6 y casos A–O | PY-183 a 189, 197 a 211 | PARCIAL | `INFORME_TECNICO_PYTHON.md` (tabla A–O). R6, A, K y N hechos; los que piden un alta o un cambio real en ACC dependen de la exportación REAL y del SO024 oficial | — |
| Informes técnico y ejecutivo | PY-110, 111, 194, 215 | OK (redactados) | `INFORME_TECNICO_PYTHON.md`; `python-analisis/informe_ejecutivo.md` (cinco decisiones con prioridad, urgencia, impacto esperado y sustento) | Leer la decisión de prioridad 1 y su tabla de sustento |

## 5. Sistemas de Gestión Empresarial (Odoo)

**[PENDIENTE (Berme): todo el bloque.]** No hay ninguna evidencia de Odoo en el repositorio. El conector `servidor-admin/odoo.js` está integrado pero desactivado y sin probar: no cuenta como evidencia de ninguno de estos requisitos.

| Bloque | Requisitos | Estado | Evidencia | Cómo enseñarlo |
|---|---|---|---|---|
| Entorno e instalación | IM-SGE-06, 08; RA1, RA2 | PENDIENTE | — | Capturas de la máquina virtual y de las aplicaciones instaladas |
| Empresa, usuarios y roles | IM-SGE-09 | PENDIENTE | — | Ajustes → Usuarios, con los cuatro perfiles |
| Clientes, productos y venta | IM-SGE-10 a 12, 17 | PENDIENTE | — | Paso 3 de la demo |
| Fabricación, inventario y factura | IM-SGE-13 a 15 | PENDIENTE | — | Ídem |
| Trazabilidad y exportación | IM-SGE-16, 21; RA3, RA4 | PENDIENTE | — | Secuencia de capturas y CSV exportado |
| Copia de seguridad | IM-COM-16 | PENDIENTE | — | Enseñar el archivo de la copia y cómo se restaura |

Todo lo que falta, con casillas: `CHECKLIST_ODOO_BERME.md`.

## 6. Proyecto Intermodular (común e integración)

| Bloque | Requisitos | Estado | Evidencia | Cómo enseñarlo |
|---|---|---|---|---|
| Memoria técnica | IM-COM-18, 21 a 29 | PARCIAL (faltan el punto 4, Odoo, y el 9, reparto real e IA) | `docs/entrega/MEMORIA.md` | — |
| Manual de demostración | IM-COM-19, 32 | PARCIAL (falta Odoo) | `docs/entrega/MANUAL_DEMOSTRACION.md` | Ensayarlo entero al menos una vez |
| Documentación reproducible | IM-COM-05 | OK | `docs/entrega/MANUAL_INSTALACION.md`, seguido el 13/11 en un clon nuevo y una base nueva (`pruebas/regresion-final/08_manual_instalacion/`); `README.md` | — |
| Presentación | IM-COM-20 | PARCIAL (falta Odoo) | `docs/defensa/PRESENTACION.md` y `PRESENTACION.pptx` | Ensayarla con la guía de `docs/defensa/` |
| Repositorio publicado | IM-COM-02, 15 | PARCIAL | La candidata anterior está publicada (`integracion/nova-candidata-2026-11-12`); esta rama se propone a `main` con una pull request y un commit de fusión, sin force-push. **[REVISIÓN (Álvaro y Berme) en la PR: revisarla antes de fusionar]** | Enseñar la PR y el historial con los tres autores |
| Sin credenciales y datos ficticios | IM-COM-03, 04 | OK | `.gitignore`; búsqueda de las claves de las pruebas en `pruebas/` y `docs/`: 0 coincidencias (`pruebas/regresion-final/README.md`). **[DUDA PARA EL PROFESOR (D12): cómo se le dan las contraseñas de demostración]** | — |
| Modelo de datos común | IM-ITG-09 a 15 | PROVISIONAL | `MEMORIA.md` §6; `integracion/caso-comun-SO024.md`; `SO024_DATOS_PENDIENTES.md` | Tabla de datos comunes |
| Caso completo SO024 | IM-ITG-04, 16, 18 | PROVISIONAL | `pruebas/regresion-final/06_so024_provisional/00_cadena.txt` (de principio a fin, 13/11). **[PENDIENTE (los tres): los 7 datos y el SO024 oficial]** | Paso 8 de la demo: la tabla de 40 pares en todas las columnas |
| Frontera ERP/auxiliar y ampliaciones productivas | IM-ITG-06 | OK (redactada) | `MEMORIA.md` §2.3 y §2.4 | Explicarlo en el cierre |
| Reparto real | IM-COM-29, 33 | PENDIENTE | `MEMORIA.md` §9 (datos de Git y huecos). **[PENDIENTE (los tres): el reparto real y el uso de la IA]** | Cada uno explica lo suyo y lo de otro |
| Datos de integración | IM-COM-17 | PARCIAL (faltan el CSV oficial de SO024 y la exportación de Odoo) | `pruebas/fixtures/custom40.csv`, `psp/datos/`, `python-analisis/entrada_acc/`, `pruebas/psp/so024_provisional/SO024_PROVISIONAL_fabricacion.csv` | — |

## 7. Ampliaciones (no obligatorias)

**[DUDA PARA EL PROFESOR (D6): ¿cuentan como ampliación o pueden restar (AD-136)?]**

| Ampliación | Evidencia (13/11, árbol final) | Cómo enseñarla |
|---|---|---|
| Tienda online | `pruebas/regresion-final/05_web/04_compra_edge.txt` (139/139), `01_sql/05_sql_tienda.txt` (55/55), `03_node/03_test_tienda.txt` (39/39); capturas en `pruebas/tienda/capturas-2026-11-13/` | `MANUAL_DEMOSTRACION.md`, parte opcional |
| Panel de administración (Álvaro) | `03_node/02_npm_test_desechable.txt` (23/23); `pruebas/tienda/capturas-2026-11-13/panel_*.png`; `pruebas/panel-admin/` (11/11) | Ídem |
| Reparto | `01_sql/07_sql_reparto_con23.txt` (37/37), `05_web/05_recorrido_reparto.txt` (29/29); capturas en `pruebas/reparto-y-correo/` | Ídem |
| Recibo con Resend y Ethereal | 7 + 7 pruebas simuladas dentro de `03_test_tienda.txt`; Ethereal sin red y sin respuesta 5/5 y 5/5 (`05_web/08_*`, `09_*`); compra real contra Ethereal con datos ficticios 16/16 (`05_web/07_ethereal_real.txt`); capturas y datos en `pruebas/correo-ethereal/` | Ídem |
| 100 modelos, colores, bloque de compra y probador | `05_web/01_mejoras.txt` (81/81); contraste 212/212 (12/11, informe de integración). **[REVISIÓN (Álvaro) en la PR: la adaptación de su paleta]** | Ídem |
| Portal del trabajador y login único (Berme) | `03_node/04_test_portal.txt` (24/24), `01_sql/08_sql_portal.txt` (50/50), `05_web/06_edge_portal.txt` (82/82, axe 0); capturas en `pruebas/portal-trabajador/capturas/`. **[REVISIÓN (Berme) en la PR: los cambios en sus archivos]** | Entrar en `login.html` como `admin.demo`, `taller.demo` y `tienda.demo`; avanzar un pedido en el portal y verlo en la auditoría del panel |
