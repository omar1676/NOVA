# NOVA Sneakers · Matriz de rúbricas (final)

**Cierre de entrega del 13/11/2026.** Versión: `main`, commit `372f811` (PR #3); código probado desde un clon nuevo en `4f09742`, con documentos y evidencias posteriores. La historia publicada se reescribió el 13/11 (cambiaron fechas e identificadores, no archivos ni autores): las evidencias históricas citan identificadores antiguos, y su equivalencia está en `06_Intermodular/EQUIVALENCIAS_COMMITS.md`. Esta versión incorpora la evidencia documental de Odoo y conserva los requisitos/ID originales. Caso de Odoo elegido después de publicar main `4a25d5a`: S00005 del Club Atlético NOVA. SO024 es el ejemplo del enunciado, no una venta realizada ni un identificador expresamente obligatorio. Ver `06_Intermodular/CASO_COMUN_S00005.md`.

## 0. Qué se ha auditado y cómo leer la matriz

**Qué se ha auditado.**
- **El código del cierre**, clonado en `4f09742`, instalado con venv nuevo y npm ci, y probado con un clúster PostgreSQL nuevo. Logs actuales en `06_Intermodular/evidencias/cierre-entrega-20261113/`.
- **Las pruebas históricas de la Fase A del 13/11**, conservadas con su contexto original. Resultados, sin rutas personales, en `06_Intermodular/evidencias/regresion-final/` (resumen en su `README.md`).
- **La documentación de entrega** que ya está en el repositorio: las carpetas `memoria/` de cada asignatura, `05_Odoo/`, `06_Intermodular/` y `06_Intermodular/defensa/`.
- **Los textos literales de las rúbricas**, extraídos el 12/11: IM y reparto de tareas, AD y Python. Los ID son los mismos que en la matriz del 12/11.

**Reglas que se han aplicado:**
- **«Probado» solo si hay un resultado identificable** que lo demuestra: el cierre nuevo o, con su contexto, la regresión de la Fase A o el cierre de requisitos de esa madrugada. Son los códigos R01 a R26.
- Si la última prueba es anterior, el estado es **CUMPLIDO SIN PRUEBA DEL 13/11**. Se cita su código A1 a A8, con la fecha.
- **No se usa el número de pruebas como sustituto de la rúbrica.** Cada fila dice qué comprobación concreta cubre ese requisito: el nombre de la prueba, la verificación o la captura, o que no hay ninguna.
- **Los requisitos que solo piden un texto** quedan como **CUMPLIDO (DOCUMENTADO)** si el texto está en el repositorio, y se cita dónde.
- **PENDIENTE** de verdad solo es esto:
  - los requisitos de Odoo sin evidencia suficiente y la trazabilidad de S00005 entre sistemas;
  - la exportación REAL;
  - la usabilidad con personas;
  - el reparto real del trabajo y el uso de la IA (punto 9);
  - el E-R en PNG (Álvaro);
  - y lo que de verdad no existe, como las capturas manuales de la ventana Java, la prueba de dos sesiones con capturas o el JSON tras un ROLLBACK.
- Las preguntas al profesor van como **[DUDA PARA EL PROFESOR (Dn)]** (apartado 5). Las decisiones del equipo, como **[POR DECIDIR (los tres)]**. Lo que tiene que confirmar o revisar una persona (las PR #2 y #3 ya están fusionadas), como **[ÁLVARO: …]**, **[BERME: …]**, **[OMAR: …]** o **[EQUIPO: …]**. Lo que no está hecho y se entrega así, como **Límite declarado**.
- **«PUEDE IMPEDIR APROBAR»** marca lo que, según el texto literal de la rúbrica, puede dejar una asignatura sin aprobar (apartado 1.2).
- **Las ampliaciones** (tienda, panel, reparto, correos, portal del trabajador, 100 modelos y probador) **no cuentan para aprobar** y van aparte, en el apartado 3.
- No se dan porcentajes ni notas.

**Estados:**

| Estado | Significado |
|---|---|
| CUMPLIDO Y PROBADO | Hecho, y un resultado del 13/11 (R01–R26) lo demuestra |
| CUMPLIDO SIN PRUEBA DEL 13/11 | Hecho, pero su última prueba es anterior (A1–A8) o ninguna prueba ejecutable lo cubre entero |
| CUMPLIDO (DOCUMENTADO) | Requisito de documentación: el texto está en el repositorio |
| PARCIAL | Falta una parte del requisito |
| PROVISIONAL | Ensayo con datos inventados de SO024; no es evidencia de S00005 ni una obligación de crear un SO024 oficial |
| PENDIENTE | No está hecho |
| PENDIENTE DE DUDA | Depende de una respuesta del profesor |
| NO VERIFICABLE | Se ve en la defensa o en el tribunal |

**Documentación del repositorio (columna DOCUMENTADO EN):**

| Abreviatura | Archivo |
|---|---|
| MEM | `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf` (memoria técnica común, 9 puntos) |
| MAD | `02_Acceso_Datos/memoria/MEMORIA_ACCESO_DATOS.md` (apartado de Acceso a Datos) |
| ITP | `04_Python/memoria/INFORME_TECNICO_PYTHON.md` |
| DPSP | `03_PSP/memoria/DOCUMENTACION_PSP.md` |
| EPI | `01_Interfaces/memoria/ESTRATEGIA_PRUEBAS_INTERFACES.md` |
| PUS | `01_Interfaces/memoria/PROCEDIMIENTO_USABILIDAD.md` |
| MI | `06_Intermodular/manuales/MANUAL_INSTALACION.md` |
| MD | `06_Intermodular/manuales/MANUAL_DEMOSTRACION.md` |
| CASO | `06_Intermodular/CASO_COMUN_S00005.md` |
| SDP | `06_Intermodular/SO024/SO024_DATOS_PENDIENTES.md` |
| COB | `05_Odoo/CHECKLIST_ODOO_BERME.md` (lista de tareas de Odoo: no es evidencia) |
| GD, SD, PRES | `06_Intermodular/defensa/GUIA_DEFENSA.md`, `06_Intermodular/defensa/SIMULACION_DEFENSA.md` y `06_Intermodular/defensa/PRESENTACION.md`/`.pptx` |
| README AD, README Python | `02_Acceso_Datos/documentacion/README.md`, `04_Python/README.md` |

### 0.1 Evidencias citadas

**Del 13/11, en el repositorio.** Las rutas son relativas a la raíz; `RF/` es `06_Intermodular/evidencias/regresion-final/`, la regresión **histórica** sobre un árbol anterior al cierre (`1bcbb10`, antes `8cdc08c`, con la estructura de carpetas antigua). La regresión del código entregado es `06_Intermodular/evidencias/cierre-entrega-20261113/` (`4f09742`): repitió SQL (123/0/1), Java 47/47, PSP 27/27 y 8/8, el comprobador de PSP, Python 265, Node 23/39/24 y 9 controles en Edge; lo demás de esta tabla no se repitió.

| Código | Hora (13/11) | Qué se ejecutó | Resultado | Archivo |
|---|---|---|---|---|
| R01 | 00:58 | Scripts 01–23 desde cero en una base nueva, en el orden del README, y el 23 dos veces. Igual en una segunda base y en una sin el 23 | Los 23 con salida 0. **Batería 09–16: 123 PASS, 0 FAIL y 1 ERROR previsto** (S4b) | `RF/01_sql/00_resumen.txt`, `01_montaje_01_23.txt` |
| R02 | 00:58 | Salida completa de cada script: 06 (las 8 consultas; la 3, con HAVING, devuelve 1 fila), 09 (91 veredictos), 10, 11, 12, 14, 15 y 16 | — | `RF/01_sql/logs_nova_rf_base/*.log.txt`, `04_06_consultas.txt` |
| R03 | 00:59 | SQL de la tienda (20 y 21) | 55 PASS, 0 FAIL | `RF/01_sql/05_sql_tienda.txt` |
| R04 | 00:59 | SQL del reparto (22), con el 23 instalado | 37 PASS, 0 FAIL. La P7 antigua da 36/1 por un catálogo compartido del clúster, no por el código (`06b_causa_P7.txt`) | `RF/01_sql/07_sql_reparto_con23.txt` |
| R05 | 00:59 | SQL del portal (23) | 50 PASS, 0 FAIL | `RF/01_sql/08_sql_portal.txt` |
| R06 | 01:01 | Java `PruebasRubrica`: login L, pruebas A–J y permisos P; cada cifra comparada con SQL | 47 PASS, 0 FAIL | `RF/02_java_psp/02_pruebas_rubrica.txt` |
| R07 | 01:01 | El TXT, el JSON de usuarios y el CSV filtrado que escribe la aplicación en esa batería | Sin contraseñas ni hashes | `RF/02_java_psp/02_salidas_java/`; `02_Acceso_Datos/evidencias/java-pruebas-rubrica/` |
| R08 | 01:08 (y 00:4x) | `ProbarVentanas`: la aplicación Swing de verdad, con los tres roles, comparando la pantalla con SQL | 76 PASS, 0 FAIL; sin conexión, 1/1. Las 19 capturas del 13/11 están en `02_Acceso_Datos/evidencias/java-swing/` | `RF/07_ventanas_swing/resultado.txt` |
| R09 | 01:02 | PSP: `PruebasPsp`; CUSTOM-40; archivo inexistente; cantidad 0 | 27 de 27; códigos 0, 1 y 2; la ficha, igual a la guardada | `RF/02_java_psp/04_*.txt` a `06_*.txt` |
| R10 | 01:02 | `scripts/comprobar_psp.py` y `scripts/comprobar_web.py` | La de PSP **falla**, como ya se sabía (espera la respuesta antigua del validador); la de la web, correcta | `RF/02_java_psp/07_*.txt`, `08_*.txt` |
| R11 | 01:03 | `npm test` (panel) | 23 de 23 con base desechable; 22 y 1 saltada sin ella | `RF/03_node/01_*.txt`, `02_*.txt` |
| R12 | 01:03 | `npm run test:tienda` | 39 de 39 (7 con un Resend simulado y 7 con Ethereal simulado) | `RF/03_node/03_test_tienda.txt` |
| R13 | 01:04 | `npm run test:portal` (login único y portal) | 24 de 24 | `RF/03_node/04_test_portal.txt` |
| R14 | 00:59–01:12 | Python `unittest`, con salida detallada (`-v`): el nombre de cada prueba está en el archivo | Ran 265 tests, OK | `RF/04_python/02_unittest.txt` |
| R15 | 01:12–01:13 | Las 93 salidas de `main.py` (real, sintético, sintético con errores y generador) frente a la referencia original | 91 idénticas; 2 con 4 columnas nuevas a propósito; 4 archivos nuevos a propósito (caso N y metadatos); «caso N: 17 de 17 cifras coinciden con SQL» | `RF/04_python/03_salidas_93.txt` |
| R16 | 01:14 | Web, mejoras: 100 fichas, teclado, 11 anchos de 320 a 1440 px, probador y axe | 81 de 81 | `RF/05_web/01_mejoras.txt` |
| R17 | 01:16 | Interfaces: 4 anchos, menú, fichas, Custom, contacto y axe frente a la web anterior | 136 de 136 | `RF/05_web/02_interfaces.txt` |
| R18 | 01:18 | Web completa | 114 de 114 | `RF/05_web/03_web.txt` |
| R19 | 01:22 | Compra en Edge (escritorio y móvil), contrastada con PostgreSQL y con el panel | 139 de 139; 4 recibos y 4 pedidos pagados | `RF/05_web/04_compra_edge.txt`; `01_Interfaces/evidencias/tienda/capturas-2026-11-13/` |
| R20 | 01:24 | Reparto en Edge: «Marcar en reparto», «En reparto» en «Mis pedidos» y recibo | 29 de 29 | `RF/05_web/05_recorrido_reparto.txt`; `01_Interfaces/evidencias/reparto-y-correo/capturas/` |
| R21 | 01:25 | Login único, roles y portal en Edge: administrador → panel, trabajador → portal, comercial → 403, las 4 páginas, avanzar estado, inventario, axe y móvil | 82 de 82 | `RF/05_web/06_edge_portal.txt`; `01_Interfaces/evidencias/portal-trabajador/capturas/` |
| R22 | 01:32 | Ethereal real con datos ficticios; Ethereal sin red y sin respuesta (simulados) | 16 de 16; 5 de 5 y 5 de 5 | `RF/05_web/07_*.txt` a `09_*.txt`; `01_Interfaces/evidencias/correo-ethereal/` |
| R23 | 01:06 | **SO024 PROVISIONAL** de principio a fin: 18 → métodos Java de «Nuevo pedido» → 15 → PSP → 16 → Python | 40 pares, 9 líneas y 3.996,00 €; cada talla baja una vez; auditoría de `admin.demo`; PSP con código 0; en Python, un solo pedido | `RF/06_so024_provisional/`; `03_PSP/evidencias/so024_provisional/` |
| R24 | 01:19–08:44 | **El manual de instalación seguido al pie de la letra** en un clon nuevo y una base vacía: base, Java, PSP, entorno Python nuevo con `requirements.txt`, Streamlit, `npm ci`, `.env`, login único y `npm test` | 23 scripts con salida 0, 123/0/1, `pruebas.bat` 47/47, 27/27, `npm test` 23/23. Salieron dos errores del manual, ya corregidos | `RF/08_manual_instalacion/` |
| R25 | 00:44–00:47 | Caso K: el dashboard abierto en Edge tres ciclos de 60 s sin tocarlo (mismo código, `1bcbb10`) | 4 PASS: cuatro horas de comprobación distintas, «Sin cambios» y las mismas cifras | `04_Python/evidencias/dashboard/caso_k_*` |
| R26 | 13/11 | Búsqueda de las cinco contraseñas de demostración en las evidencias y la documentación (entonces `pruebas/` y `docs/`), `README.md` y los resultados | 0 coincidencias. El escaneo de todos los blobs nuevos de la rama se hace al preparar la PR | `RF/README.md` («Sin contraseñas») |

**Anteriores al 13/11 (no repetidas):**

| Código | Archivo | Qué demuestra | Fecha |
|---|---|---|---|
| A1 | `01_Interfaces/evidencias/web/` (resultados, 14 capturas y Lighthouse) | Interfaces y Lighthouse 100/100 en accesibilidad y buenas prácticas, escritorio y móvil | 11/11 |
| A2 | `04_Python/evidencias/dashboard/` (capturas y README) | Dashboard en Edge: 6 pestañas, filtros, R1, R4, R5 y recuperación | 9 y 10/11 |
| A3 | `01_Interfaces/evidencias/panel-admin/` | Panel: autenticación, seguridad, API frente a PostgreSQL y accesibilidad | 11/11 |
| A4 | `01_Interfaces/evidencias/tienda/resultados/` y `capturas/` | Tienda: 111/111 en Edge | 11/11 |
| A5 | `02_Acceso_Datos/documentacion/README.md` §11 | Las tres pruebas de dos sesiones (visibilidad con COMMIT y ROLLBACK, concurrencia), a mano | 8/11 |
| A6 | `04_Python/entrada_acc/conciliacion_sql/` | P-A, P-B y P-C (9/11) y N-1 a N-3 (13/11), de una base de PRUEBA | 9 y 13/11 |
| A7 | Informe de integración (fuera del repositorio) | Contraste WCAG AA: 212 de 212 medidas en Edge | 12/11 |
| A8 | Informe de integración (fuera del repositorio) | 1.771 archivos comparados al integrar: ninguno perdido | 12/11 |

**No se ha repetido el 13/11:** Lighthouse (A1) y el contraste (A7).

---

### 0.2 Limpieza final (13/11, por la tarde)

La rama local `refactor/limpieza-final-nova` (no se publicó con ese nombre) sale de la candidata 2 (`ab357ed`) y hace tres cosas:
- **Reorganiza el repositorio por asignaturas.** Las carpetas pasan a `01_Interfaces` … `06_Intermodular`, con `git mv`, y `servidor-admin` sigue siendo una sola carpeta compartida. Las rutas de esta matriz ya son las nuevas.
- **Quita 14 archivos sin uso.** Son 6 imágenes del probador, 1 captura repetida y 7 `.gitkeep`. Ninguno es una evidencia que cite esta matriz.
- **Simplifica código sin cambiar resultados.** Afecta a Python, la web, el servidor, PSP y los comentarios SQL.

**No cambia el estado de ningún requisito.** Los códigos R01–R26 siguen valiendo porque la regresión se repitió entera sobre el árbol limpio y dio lo mismo. Los resultados están en `06_Intermodular/evidencias/regresion-limpieza/` (`RL/`).

| Bloque | Regresión del 13/11 (R) | Árbol limpio (RL) |
|---|---|---|
| SQL 01–23 desde cero, batería 09–16 | 123 / 0 / 1 (R01) | 123 / 0 / 1 en tres bases |
| SQL de tienda, reparto (con el 23) y portal | 55, 37 y 50 (R03–R05) | 55, 37 y 50 |
| Java `PruebasRubrica` | 47 / 0 (R06) | 47 / 0 |
| Ventanas Swing (`ProbarVentanas`) | 76 / 0 (R08) | 76 / 0 |
| PSP | 27 / 27; códigos 0, 1 y 2 (R09) | 27 / 27; códigos 0, 1 y 2; ficha CUSTOM-40 igual |
| `npm test`, `test:tienda`, `test:portal` | 23, 39 y 24 (R11–R13) | 23, 39 y 24 |
| Python `unittest` | 265 OK (R14) | 265 OK |
| Salidas de `main.py` | R15 | Las 97, idénticas a las de la candidata 2 |
| Web en Edge: mejoras, Interfaces, web, compra, reparto, portal | 81, 136, 114, 139, 29 y 82 (R16–R21) | 81, 136, 114, 139, 29 y 82 |
| Ethereal real, sin red y sin respuesta | 16, 5 y 5 (R22) | 16, 5 y 5 |
| SO024 PROVISIONAL de principio a fin | R23 | Igual: PSP con código 0 y un solo pedido en Python |
| Caso K: el dashboard tres ciclos de 60 s | 4 PASS (R25) | 4 PASS, con las mismas cifras |

Lo que **no** se ha repetido sobre el árbol limpio:
- **R24, el manual de instalación seguido desde un clon nuevo.** Las rutas del manual se actualizaron y se comprobaron una a una, pero el manual no se ha vuelto a seguir entero. En el cierre se hizo una instalación limpia de `4f09742` en el orden del manual (`06_Intermodular/evidencias/cierre-entrega-20261113/README.md`), sin registrar cada paso. **[EQUIPO: seguirlo entero otra vez antes de entregar, si da tiempo]**
- **R26, la búsqueda de contraseñas.** Se rehízo con el escáner de la rama: las 5 contraseñas de demostración no aparecen en ninguno de sus 970 blobs.

Al cierre se declaran las limitaciones del apartado 4: trazabilidad de S00005 entre sistemas no demostrada, exportación REAL no aportada, usabilidad con personas no realizada aquí, aportaciones personales no confirmadas y E-R en PNG pendiente. Odoo sí tiene evidencia documental; su API no se verificó en este entorno.

## 1. Resumen definitivo de estados al cierre

Recuento reproducido de las filas con estado del apartado 2; los identificadores agrupados y las filas opcionales no equivalen a un número de pruebas ni a una nota. Los resultados nuevos están en `06_Intermodular/evidencias/cierre-entrega-20261113/`. Las referencias R01…R26 se conservan como evidencia histórica, no como ejecuciones nuevas.

| Asignatura | Filas con estado | Cumplido probado/documentado | Solo evidencia documental | Parcial/provisional | Pendiente/no verificable/opcional |
|---|---:|---:|---:|---:|---:|
| Interfaces | 14 | 13 | 0 | 0 | 1 |
| Acceso a Datos | 130 | 114 | 0 | 14 | 2 |
| PSP | 19 | 17 | 0 | 2 | 0 |
| Python | 214 | 200 | 0 | 13 | 1 |
| Odoo | 17 | 0 | 12 | 3 | 2 |
| Intermodular | 37 | 12 | 2 | 16 | 7 |

«Cumplido sin prueba del 13/11» conserva la distinción original: no se transforma en prueba nueva. Las rúbricas de defensa, participación individual y usabilidad requieren personas; no se inventan. Una documentación de Odoo no demuestra la conexión de esta candidata con su instancia.

### Límites que pueden afectar la evaluación

La trazabilidad de S00005 entre sistemas, exportación REAL, usabilidad con personas, E-R final en PNG y ciertas evidencias manuales siguen pendientes/parciales. Odoo tiene S00005 documentado, pero no exportación conciliada hacia los otros módulos, backup/restauración verificados aquí ni API en vivo. La defensa y el reparto individual no confirmados son no verificables. El cierre de código está publicado en main `4a25d5a` (PR #2); esta revisión actualiza únicamente la documentación del caso elegido. No se promete superar todos los requisitos por el hecho de que pasen las pruebas automáticas.

## 2. Matrices por asignatura

Columnas:
- ID de la rúbrica;
- REQUISITO (corto);
- OBLIGATORIO u OPCIONAL;
- ARCHIVO;
- COMPROBACIÓN CONCRETA (la prueba, verificación o captura que lo cubre, o que no hay ninguna);
- EVIDENCIA (códigos del apartado 0.1);
- DOCUMENTADO EN;
- ESTADO;
- PENDIENTE.

Cuando una celda no aplica, lleva una raya (—). «Ídem» repite la fila de arriba.

### 2.1 Desarrollo de Interfaces (módulo 0488, IM §4.1, RA4 y RA8)

| ID | REQUISITO | OBL/OPC | ARCHIVO | COMPROBACIÓN CONCRETA | EVIDENCIA | DOCUMENTADO EN | ESTADO | PENDIENTE |
|---|---|---|---|---|---|---|---|---|
| IM-INT-04 | Estructura mínima: inicio, catálogo, ficha de producto, Custom y sección corporativa/contacto | OBLIGATORIO | `01_Interfaces/cliente/index.html`, `js/inicio.js`, `js/modelos.js` | Script de Playwright no incluido en el repositorio (solo sus resultados), en 4 anchos: «el menú lleva a inicio, catálogo, Custom y contacto», «menú → Custom» y «menú → Contacto», las fichas de las 6 colecciones y «sección de contacto con email» | R17 (136/136); R18 (114/114) | MEM §3.1 | CUMPLIDO Y PROBADO | — |
| IM-INT-05 | Responsive en móvil y escritorio con las técnicas CSS vistas en clase | OBLIGATORIO | `01_Interfaces/cliente/css/inicio.css`, `css/tienda.css` | «sin desplazamiento horizontal» y «la cabecera cabe y sus enlaces no se pisan» en 4 anchos (R17); 11 anchos de 320 a 1440 px (R16) | R17, R16; Lighthouse 100/100 en A1 (11/11) | MEM §3.3; EPI §4.6 | CUMPLIDO Y PROBADO | [DUDA PARA EL PROFESOR (D7)]: qué «técnicas CSS vistas en clase» espera |
| IM-INT-06 | Catálogo: varios modelos con nombre, imagen, precio orientativo, descripción y tallas | OBLIGATORIO | `js/modelos.js` (`datosColeccion`, 100 modelos), `index.html` | «las 100 tarjetas del catálogo muestran su precio» y «ficha …: precio, descripción y tallas» de las 6 colecciones (R17); las 100 fichas con su bloque de compra (R16) | R17, R16; el 21 carga en PostgreSQL los mismos 100 modelos (R01: 1 PASS; R03: T12) | MEM §3.1 | CUMPLIDO Y PROBADO | Precios y tallas provisionales: acordarlos con Odoo (IM-ITG-15) |
| IM-INT-07 | Custom: explicar el proceso para clubes y un formulario o prototipo de solicitud | OBLIGATORIO | `index.html` (`#custom`), `js/custom.js` | Envío vacío, email mal escrito, sin pares y cantidades negativas o con decimales bloqueados; «el total de pares se actualiza al escribir (8 tallas × 5 = 40)»; «envío válido: mensaje de SIMULACIÓN, sin peticiones de red y sin recargar» (4 anchos) | R17; captura `escritorio_06_custom_simulacion.png` en A1 (11/11) | MEM §3.1 | CUMPLIDO Y PROBADO | No pide fecha objetivo ni enseña un identificador; el IM lo deja como opcional. [DUDA PARA EL PROFESOR (D8)] |
| IM-INT-08 | Calidad: jerarquía visual, legibilidad, consistencia, navegación, organización del CSS y uso razonado de componentes | VALORADO (criterio) | `css/inicio.css`, `css/tienda.css`, `index.html` | axe: 0 violaciones WCAG 2.1 A/AA en la web, la ficha, el formulario enviado, el probador y el carrito (R16, R17); foco visible con Tab (R17); contraste AA 212/212 (A7, 12/11, no repetido) | R16, R17; A7 (12/11) | MEM §3.2; EPI §2 | CUMPLIDO Y PROBADO | La organización del CSS y el uso de los componentes los valora el profesor: están explicados en MEM §3.2 |
| IM-INT-11 | Autocomprobación: ¿la web es navegable y responsive y representa la fábrica? | AUTOCOMPROBACIÓN | Las mismas que INT-04 e INT-05 | Las de INT-04 e INT-05 | R17, R18 | MEM §3 | CUMPLIDO Y PROBADO | — |
| IM-INT-12 | Autocomprobación: ¿hay una propuesta clara para pedidos Custom? | AUTOCOMPROBACIÓN | `#custom`, `js/custom.js` | La de INT-07 | R17 | MEM §3.1 | CUMPLIDO Y PROBADO | — |
| IM-INT-RA4-ab | RA4 CE a)-b): identificar los estándares de usabilidad y accesibilidad y valorar por qué se usan | CRITERIO (RA/CE) | `01_Interfaces/evidencias/web/README.md` | axe con WCAG 2.1 A/AA en la web (R16, R17) y en el login y el portal (R21) | R16, R17, R21; contraste A7 (12/11) | MEM §3.4; EPI §4.3 | CUMPLIDO Y PROBADO | — |
| IM-INT-RA4-cg | RA4 CE c)-g): menús, acciones y controles coherentes, y legibilidad | CRITERIO (RA/CE) | `index.html`, `css/inicio.css` | «todos los campos tienen etiqueta, las tallas van en un fieldset y el resultado es role=status», foco visible y menú (R17); talla enfocada con el teclado y zonas táctiles (R16) | R17, R16; contraste A7 (12/11) | MEM §3.4; EPI §4.3 | CUMPLIDO Y PROBADO | — |
| IM-INT-RA4-hi-acc | RA4 CE h)-i): claridad de los mensajes y pruebas de accesibilidad | CRITERIO (RA/CE) | `js/custom.js`, `js/tienda.js` | Errores junto a su campo y `role=status/alert` (R16, R17); axe en todos los estados, también tras enviar el formulario (R17) y en la compra (R19) | R16, R17, R19 | EPI §4.3 | CUMPLIDO Y PROBADO | — |
| IM-INT-RA4-hi-usab | RA4 CE i): pruebas de usabilidad (con personas) | CRITERIO (RA/CE) | — | Ninguna con personas | — | PUS (procedimiento, sin resultados) | PENDIENTE | **Límite declarado:** no se ha hecho la prueba con 3 a 5 personas; el procedimiento está listo en PUS, sin fecha, participantes ni resultados. **[EQUIPO: si se hace, añadir el resultado]** |
| IM-INT-RA8-a | RA8 CE a): establecer una estrategia de pruebas | CRITERIO (RA/CE) | — | — | — | EPI §1–§5 | CUMPLIDO (DOCUMENTADO) | — |
| IM-INT-RA8-b | RA8 CE b): pruebas de integración | CRITERIO (RA/CE) | `01_Interfaces/cliente/js/tienda.js`, `servidor-admin/` | Web → API → PostgreSQL en Edge: compra contrastada con PostgreSQL y con el panel (R19), reparto (R20), login único y portal (R21); `npm test`, `test:tienda` y `test:portal` (R11–R13) | R19, R20, R21, R11–R13 | EPI §4.4 | CUMPLIDO Y PROBADO | Los scripts de navegador no están en el repositorio: solo sus resultados y capturas |
| IM-INT-RA8-g | RA8 CE g): documentar la estrategia y los resultados | CRITERIO (RA/CE) | `01_Interfaces/evidencias/web/README.md`, `01_Interfaces/evidencias/tienda/README.md` | La estrategia y la trazabilidad requisito → prueba → evidencia, con los resultados del 13/11 | R16–R22 (`06_Intermodular/evidencias/regresion-final/05_web/` y sus capturas) | EPI §5 y §7 | CUMPLIDO Y PROBADO | — |

**No obligatorios de Interfaces:**

| ID | Qué es | Carácter | Estado |
|---|---|---|---|
| IM-INT-01 a 03 | Objetivos (presencia digital, caso de uso, web responsive) | OBJETIVO | Cubiertos por INT-04 a INT-07 |
| IM-INT-09 | JavaScript: validación, filtrado, cálculo orientativo | OPCIONAL («Evolución posible») | OPCIONAL: hecho y probado (R17: filtros, ficha y total de pares de `custom.js`) |
| IM-INT-10 | Guion de demo, paso 2: escritorio, móvil y una solicitud Custom | ORIENTATIVO | En MD, §1 |

### 2.2 Acceso a Datos (PostgreSQL + Java)

Las 130 filas obligatorias de la rúbrica de AD.
- **«Es imprescindible aprobar todas las partes» (AD-138).**
- La memoria (30 %) y la defensa (30 %) pesan más que el entregable (20 %).
- En la columna COMPROBACIÓN, L, A–J y P son las pruebas de `PruebasRubrica` (R06). Los números de captura son los de `02_Acceso_Datos/evidencias/java-swing/` (R08).

| ID | REQUISITO | OBL/OPC | ARCHIVO | COMPROBACIÓN CONCRETA | EVIDENCIA | DOCUMENTADO EN | ESTADO | PENDIENTE |
|---|---|---|---|---|---|---|---|---|
| AD-01 | Datos coherentes con el catálogo, los clientes y los pedidos del proyecto común | OBLIGATORIO | `02_Acceso_Datos/sql/05_datos_prueba.sql`, `18_datos_so024.sql`, `21_catalogo_web.sql` | El 21 da de alta los 100 modelos de la web; el 18, Club Halcones y Runner X | R01 (05 y 21 con salida 0; el 21, 1 PASS); R23 (18) | MAD §1 | PARCIAL | Catálogo web/PostgreSQL disponible; no hay correspondencia acreditada con los productos de S00005 en Odoo. SO024 es un ensayo, no una venta obligatoria. |
| AD-02 | No crear otra empresa ni un segundo proyecto | OBLIGATORIO (límite) | Todo `02_Acceso_Datos/` | Revisión: una sola base y la misma marca NOVA en todos los bloques | Revisión del repositorio (13/11) | MAD §1 | CUMPLIDO SIN PRUEBA DEL 13/11 | [DUDA PARA EL PROFESOR (D2)]: «NOVA» en lugar de «Sneaker Factory» |
| AD-03 | Base PostgreSQL de clientes, zapatillas, variantes y pedidos personalizados, con claves, restricciones, consultas e integridad | OBLIGATORIO | `sneaker-factory-esquema.sql`, 02–08 | Montaje desde cero y batería 09–16 | R01 (13/11) | MAD §1 | CUMPLIDO Y PROBADO | — |
| AD-04 | Acceso por perfiles y cada operación auditada asociada a un usuario autenticado | OBLIGATORIO | `07_seguridad.sql`, `08_auditoria.sql`, `java/src/nova/Sesion.java` | L1, F2–F3, P1–P5 y A5 | R06 (13/11) | MAD §1 | CUMPLIDO Y PROBADO | — |
| AD-05 | Diagrama entidad-relación | OBLIGATORIO | `02_Acceso_Datos/modelo/sneaker-factory.dbm`, `modelo-er/Modelo-Er-Intermodular.drawio` | — | Diagrama en MAD §2.1 (mermaid, sacado de las 16 FK); `.dbm` y `.drawio` | MAD §2 | PARCIAL | [PENDIENTE (Álvaro): elegir el E-R oficial (`.dbm` o `.drawio`) y exportarlo a PNG para la memoria] |
| AD-06 | Entidades clientes, modelos, pedidos y líneas, o equivalentes justificados | OBLIGATORIO | `sneaker-factory-esquema.sql` (14 tablas) | Creación en una base vacía | R01 (13/11) | MAD §2 | CUMPLIDO Y PROBADO | — |
| AD-07 | Cada línea con talla y cantidad; color o personalización identificables | OBLIGATORIO | Esquema: `linea_pedido` → `producto_sku` (talla) → variante (color); `pedidos.personalizacion` | A2 (tallas 41 y 42); el 15 exporta color y personalización | R06, R23 (13/11) | MAD §2 | CUMPLIDO Y PROBADO | — |
| AD-08 | PK, FK, tipos y reglas básicas de integridad | OBLIGATORIO | Esquema | 09 (E1–E10) y 11 (6 rechazos) | R01, R02 (13/11) | MAD §2 | CUMPLIDO Y PROBADO | — |
| AD-09 | Evitar duplicación y justificar el diseño | OBLIGATORIO | `documentacion/modelo_relacional.md`, `documentacion/README.md` §5–8 | Montaje desde cero sin duplicados (R01) | R01; MAD §2.2–2.3; `documentacion/modelo_relacional.md` | MAD §2 | CUMPLIDO Y PROBADO | — |
| AD-10 | Script reproducible con PRIMARY KEY, FOREIGN KEY, NOT NULL, UNIQUE y CHECK | OBLIGATORIO | `sneaker-factory-esquema.sql` | Base vacía: salida 0 | R01 (13/11) | MAD §3 | CUMPLIDO Y PROBADO | — |
| AD-11 | Al menos 5 clientes, 6 modelos o variantes y 10 pedidos | OBLIGATORIO | `05_datos_prueba.sql` | 09 («datos mínimos»). Base 01–23 del 13/11: 6 clientes, 7 modelos (107 con el 21) y 12 pedidos | R01, R02 (13/11) | MAD §3 | CUMPLIDO Y PROBADO | — |
| AD-12 | Al menos 3 pedidos Custom y 1 con varias tallas | OBLIGATORIO | `05`, `10_caso_custom.sql`, `14_caso_custom_persistente.sql` | Consulta 4 del 06 (4 personalizados); 10 y 14 (CUSTOM-40 con 4 tallas) | R02 (13/11) | MAD §3 | CUMPLIDO Y PROBADO | — |
| AD-13 | INSERT, UPDATE y DELETE respetando las restricciones | OBLIGATORIO | `11_dml_ejemplos.sql` | 12 PASS | R01, R02 (13/11) | MAD §3 | CUMPLIDO Y PROBADO | — |
| AD-14 | Alta de pedidos y líneas desde Java con JDBC | OBLIGATORIO | `PedidoDAO.java`, `PanelNuevoPedido.java` | A1–A2 y H1 (los métodos de los botones) | R06 (13/11) | MAD §3 | CUMPLIDO Y PROBADO | [PENDIENTE (Omar): captura del alta desde la ventana para la memoria] (lista en `02_Acceso_Datos/evidencias/java-swing/README.md`) |
| AD-15 | Entregar y ejecutar al menos 8 consultas | OBLIGATORIO | `06_consultas.sql` | Las 8 se ejecutan con salida 0 y dan resultado | R01; R02 (`logs_nova_rf_base/06_consultas.log.txt`, `04_06_consultas.txt`) | MAD §4 | CUMPLIDO Y PROBADO | — |
| AD-16 | Búsquedas por cliente, modelo, estado o periodo | OBLIGATORIO | `06_consultas.sql` (consultas 4 y 7), `PedidoDAO.buscarPedidos` | E2 (cliente y estado), E3 (cliente, modelo y fechas) | R06, R02 | MAD §4 | CUMPLIDO Y PROBADO | — |
| AD-17 | Consultas con JOIN | OBLIGATORIO | `06_consultas.sql` (1, 2, 4 y 6) | Ejecutadas | R02 (13/11) | MAD §4 | CUMPLIDO Y PROBADO | — |
| AD-18 | GROUP BY: unidades por talla, ventas por modelo y pedidos por cliente | OBLIGATORIO | `06_consultas.sql` (6, 1 y 2) | Ejecutadas | R02 (13/11) | MAD §4 | CUMPLIDO Y PROBADO | — |
| AD-19 | Al menos una consulta con HAVING o subconsulta, con su utilidad explicada | OBLIGATORIO | `06_consultas.sql` (consulta 3); `documentacion/README.md` §10 | Consulta 3 (HAVING): «¿qué referencias se quedan con menos de 10 pares cuando se sirvan los pedidos pendientes?». Devuelve **1 fila** (`NOVA-4-43`: 20 en stock y 11 pendientes → 9) en la base de instalación | R02 (`logs_nova_rf_base/06_consultas.log.txt`); README AD §10 | MAD §4 | CUMPLIDO Y PROBADO | — |
| AD-20 | Demostrar al menos dos restricciones | OBLIGATORIO | Esquema; `09_pruebas.sql`, `11_dml_ejemplos.sql` | E8 (cantidad mayor que cero), E6 (referencia única) y los 6 rechazos del 11 | R01, R02 (13/11) | MAD §5 | CUMPLIDO Y PROBADO | — |
| AD-21 | Transacción con BEGIN, COMMIT y ROLLBACK, explicando qué pasa al deshacer | OBLIGATORIO | `09_pruebas.sql` (cada prueba entre BEGIN y ROLLBACK), `ConexionBD.java` | D1–D3 (ROLLBACK deliberado) y A (COMMIT) | R06, R01 (13/11) | MAD §5 | CUMPLIDO Y PROBADO | — |
| AD-22 | Mismos identificadores, o una correspondencia documentada, con Odoo y PSP | OBLIGATORIO | `15_exportar_fabricacion.sql`; `documentacion/README.md` §14 | La referencia (CUSTOM-40 y SO024) llega a la ficha de PSP | R09, R23 (13/11) | MAD §1; README AD §14 | PARCIAL | No hay tabla de equivalencias ni exportación de S00005 que lo vincule con PostgreSQL y PSP. |
| AD-23 | Consulta para la ficha de fabricación: referencia, cliente, modelo, personalización, talla y cantidad | OBLIGATORIO | `15_exportar_fabricacion.sql` | CUSTOM-40 (2 PASS) y SO024 (9 filas, 40 pares) | R01 (15: 2 PASS); R23 (SO024: 9 filas, 40 pares) | MAD §1; README AD §14 | CUMPLIDO Y PROBADO | — |
| AD-24 | Exportar esa consulta a CSV para PSP | OBLIGATORIO | `15` → `fabricacion_psp.csv` | PSP procesa el CSV (prueba 01) | R09 (CUSTOM-40, código 0); R23 (SO024, código 0) | MAD §1; README AD §14 | CUMPLIDO Y PROBADO | — |
| AD-26 | Al menos dos funciones de trigger reales, sin lógica duplicada en Java | OBLIGATORIO | `02_funciones.sql`, `03_triggers.sql`, `08_auditoria.sql` (10 triggers) | Batería 09; A3–A6 | R01, R06 (13/11) | MAD §6 | CUMPLIDO Y PROBADO | — |
| AD-27 | Recalcular el importe al insertar, modificar o borrar una línea | OBLIGATORIO | `trg_actualizar_totales` | P3 y D5 (09); A3 | R01, R06 (13/11) | MAD §6 | CUMPLIDO Y PROBADO | — |
| AD-28 | No sumar importes repetidos ni guardar totales incoherentes | OBLIGATORIO | Ídem | P3; en el 16, el total de cada pedido es la suma de sus líneas | R01 (13/11) | MAD §6 | CUMPLIDO Y PROBADO | — |
| AD-29 | Mantener el stock al confirmar o cancelar | OBLIGATORIO | `trg_descontar_stock_confirmacion`, `trg_devolver_stock_cancelacion` | A4 y C2 | R06 (13/11) | MAD §6 | CUMPLIDO Y PROBADO | — |
| AD-30 | No descontar el stock dos veces | OBLIGATORIO | Ídem; `documentacion/README.md` §7b | 14 (descontado una vez); SO024 (cada talla baja una vez) | R01 (14); R23 (cada talla de Runner X baja una vez: 8,7,5,4,3,4,5,6,8) | MAD §6 | CUMPLIDO Y PROBADO | — |
| AD-31 | Ninguna confirmación deja stock negativo; la cancelación revierte | OBLIGATORIO | Ídem | B1–B2 y C2 | R06 (13/11) | MAD §6 | CUMPLIDO Y PROBADO | — |
| AD-33 | `log_eventos` con fecha y hora, tabla, operación, identificador y resumen | OBLIGATORIO | `08_auditoria.sql` | A5 y C3 | R06 (13/11) | MAD §7 | CUMPLIDO Y PROBADO | — |
| AD-34 | Auditoría con triggers, no con mensajes por consola | OBLIGATORIO | `08_auditoria.sql` | Batería 09 | R01 (13/11) | MAD §7 | CUMPLIDO Y PROBADO | — |
| AD-35 | Auditoría dentro de la transacción: visible en otras conexiones tras el COMMIT y deshecha con ROLLBACK. Explicarlo y demostrarlo | OBLIGATORIO | `08_auditoria.sql`; README §11 | D1–D3: el ROLLBACK deshace también la auditoría (R06). La visibilidad desde **otra conexión** tras el COMMIT solo se probó a mano el 8/11 (A5) | R06; A5 (8/11) | MAD §7 | PARCIAL | [PENDIENTE (Omar): repetir la prueba de dos sesiones (COMMIT y ROLLBACK) con capturas para la memoria]; no existen |
| AD-36 | Documentar qué tabla dispara cada trigger, si es BEFORE o AFTER y qué tablas modifica (sin recursión) | OBLIGATORIO | `documentacion/README.md` §7 (tabla de los 10 triggers y párrafo de recursión) | — | README AD §7; MAD §6.1 | MAD §6.1 | CUMPLIDO (DOCUMENTADO) | — |
| AD-37 | Interfaz Java (Swing) con JDBC | OBLIGATORIO | `02_Acceso_Datos/java/src/nova/` | Compila sin errores (R06, `01_javac.txt` vacío) y la ventana se abre y se usa (R08) | R06; R08 | MAD §8 | CUMPLIDO Y PROBADO | — |
| AD-39 | Elegir cliente y modelo, indicar talla y cantidad, crear el pedido, ver el detalle, confirmar y cancelar | OBLIGATORIO | `PanelNuevoPedido.java`, `PanelConsultas.java` | Los métodos de los botones de «Nuevo pedido» y «Consultas» con A, C y H (R06); en la ventana, «Nuevo pedido: clientes y modelo-color» cargados de PostgreSQL y el rechazo de una talla inexistente sin guardar nada (R08) | R06; R08 (capturas 05 y 14) | MAD §8 | CUMPLIDO Y PROBADO | [PENDIENTE (Omar): capturas de crear, confirmar y cancelar desde la ventana para la memoria] |
| AD-40 | Mensajes de error comprensibles cuando la base rechaza algo | OBLIGATORIO | `ConexionBD.java` (mensajes legibles) | B1, H4 y F3 enseñan el mensaje traducido | R06; R08 (capturas 14 y 16) | MAD §8 | CUMPLIDO Y PROBADO | — |
| AD-41 | PreparedStatement, cierre de recursos y transacciones JDBC | OBLIGATORIO | DAO (`try` con recursos), `ConexionBD.empezarTransaccion` | A, D y H; código revisado el 12/11 | R06 (13/11) | MAD §8 | CUMPLIDO Y PROBADO | — |
| AD-42 | Credenciales fuera del código compartido | OBLIGATORIO | `java/conexion.properties.ejemplo`, `.gitignore` | Las pruebas leen un `conexion.properties` creado fuera del repositorio y lo borran al terminar; `git status` no lo ve (R24) | R06; R24 | MAD §8 | CUMPLIDO Y PROBADO | — |
| AD-43 | Java no actualiza totales, stock ni log: lo hace PostgreSQL | OBLIGATORIO | `PedidoDAO.java` (solo llama a funciones y cambia el estado) | A3–A6 | R06 (13/11) | MAD §8 | CUMPLIDO Y PROBADO | — |
| AD-44 | Consulta visual: botón «Buscar / Consultar» y JTable | OBLIGATORIO | `PanelConsultas.java` | En la ventana: «sin filtros salen todos» (12 filas = SQL) y «filtros cliente + estado» (2 = SQL), con los tres roles (R08); E1 (R06) | R08 (captura 06); R06 | MAD §8 | CUMPLIDO Y PROBADO | — |
| AD-45 | Al menos 3 filtros combinables | OBLIGATORIO | `PedidoDAO.buscarPedidos` | E2 y E3 | R06 (13/11) | MAD §8 | CUMPLIDO Y PROBADO | — |
| AD-46 | Un filtro vacío no restringe | OBLIGATORIO | Ídem | E1 y E4 | R06 (13/11) | MAD §8 | CUMPLIDO Y PROBADO | — |
| AD-47 | Botón «Limpiar filtros» | OBLIGATORIO | `PanelConsultas.java` | «Limpiar filtros vacía los filtros y vuelve a buscar» → 12 filas = SQL, con los tres roles (R08); E4 (R06) | R08 (captura 19, «tras limpiar filtros»); R06 | MAD §8 | CUMPLIDO Y PROBADO | — |
| AD-48 | La tabla se actualiza en cada pulsación, sin datos viejos | OBLIGATORIO | `PanelConsultas.java` (vacía la tabla antes de buscar) | Cada «Buscar» rehace la tabla: sin filtros 12, con dos filtros 2, con tres 4, sin coincidencias 0 y tras limpiar 12 (R08) | R08 | MAD §8 | CUMPLIDO Y PROBADO | — |
| AD-49 | Mensajes para resultado vacío, error de conexión y consulta incorrecta | OBLIGATORIO | `PanelConsultas.java`, `ConexionBD.java` | «consulta sin resultados» con su etiqueta, «fecha mal escrita» y «sin conexión» (1/1) (R08); F1 (R06) | R08 (capturas 08, 09 y 18); R06 | MAD §8 | CUMPLIDO Y PROBADO | — |
| AD-50 | Parámetros con PreparedStatement, sin concatenar valores | OBLIGATORIO | `PedidoDAO.buscarPedidos` (fragmentos fijos con `?`) | E1–E3; código revisado el 12/11 | R06 (13/11) | MAD §8 | CUMPLIDO Y PROBADO | — |
| AD-51 | Consultas sujetas a los permisos del usuario; justificar dónde se limita | OBLIGATORIO | `Sesion.java`, `17_usuario_java.sql` (`java_nova` NOINHERIT y SET ROLE) | F2 y F3 | R06 (13/11) | MAD §8 | CUMPLIDO Y PROBADO | — |
| AD-53 | Autenticación y autorización por roles | OBLIGATORIO | `UsuarioDAO.login`, `Sesion.java` | L1, L2 y P1–P5 | R06 (13/11) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-54 | Al menos 3 roles: Administrador y dos operativos | OBLIGATORIO | `07_seguridad.sql` | L1 (administrador, comercial y trabajador) | R06 (13/11) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-56 | Un usuario de prueba activo por rol, documentado | OBLIGATORIO | `07`, `13_activar_usuarios.sql`; `documentacion/README.md` §4 | L1 | R06 (13/11) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-57 | Administrador desde la carga inicial, con acceso completo, incluida la administración de usuarios, roles y permisos | OBLIGATORIO | `07`, `PanelUsuarios.java` | L1; I1–I4 (crear, cambiar el rol, desactivar) | R06 (13/11) | MAD §9 | PARCIAL | [DUDA PARA EL PROFESOR (D10)]: si basta con asignar roles. Usuarios y roles se administran (I1–I4); la matriz de permisos es fija (`Sesion.java` y SQL) |
| AD-58 | Permisos de cada rol justificados en la memoria | OBLIGATORIO | `java/README.md` (matriz y «Por qué así») | — | MAD §9.2; `java/README.md` | MAD §9 | CUMPLIDO (DOCUMENTADO) | — |
| AD-59 | Matriz de permisos por rol y operación | OBLIGATORIO | `java/README.md`, `Sesion.java` | P1–P5, I5 y F2 la aplican | R06 (13/11) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-60 | Permisos aplicados en la lógica de datos, no solo ocultando botones | OBLIGATORIO | `Sesion.comprobarPermiso` y roles de PostgreSQL | F3, P2 y P4 (saltándose Java) | R06 (13/11) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-61 | Inicio de sesión en Java y operaciones visibles y ejecutables según el rol | OBLIGATORIO | `VentanaLogin.java`, `VentanaPrincipal.java` | Login y permisos de ejecución (L1, P1, I5, R06); en la ventana, «pestañas del rol» y «cabecera con usuario y rol» de los tres usuarios (R08) | R06; R08 (capturas 04, 15 y 17) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-62 | Un usuario sin permiso no puede ejecutar la operación ni llamando directamente a la persistencia | OBLIGATORIO | Roles de PostgreSQL | F3, P2 y P4 | R06 (13/11) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-63 | `log_eventos` con el usuario responsable y la acción | OBLIGATORIO | `08_auditoria.sql`, `ConexionBD.empezarTransaccion` | A5, A6 y C3; SO024 (`admin.demo`) | R06; R23 (auditoría de SO024 firmada por `admin.demo`) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-64 | Explicar cómo se propaga la identidad de la sesión Java a PostgreSQL | OBLIGATORIO | `java/README.md` («Quién firma la auditoría»); README §9 | — | MAD §9.4; `java/README.md` («Quién firma la auditoría») | MAD §9 | CUMPLIDO (DOCUMENTADO) | Prepararlo para la defensa (GD §2) |
| AD-65 | Contraseñas con sal y bcrypt; nunca en texto plano | OBLIGATORIO | `02_funciones.sql` (`crypt` y `gen_salt('bf')`) | I2 (sin `$2a$` en el JSON); pruebas A del 09 | R06, R01 (13/11) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-66 | Credenciales iniciales ficticias que se puedan cambiar | OBLIGATORIO | `13_activar_usuarios.sql`, función `establecer_password` | A8 del 09 (contraseña mínima) | R01 (13/11) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-67 | Distinguir en la memoria los roles de la aplicación de los de PostgreSQL | OBLIGATORIO | `java/README.md` (tabla); README §9 («Tres cosas distintas…») | — | MAD §9.1; `java/README.md` | MAD §9 | CUMPLIDO (DOCUMENTADO) | — |
| AD-70 | Prueba mínima 1: acceso correcto con un usuario de cada rol | OBLIGATORIO | `PruebasRubrica.java` | L1 | R06 (13/11) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-71 | Prueba mínima 2: operación permitida desde Java | OBLIGATORIO | Ídem | A1 (el comercial crea) y C1 (el trabajador cancela) | R06 (13/11) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-72 | Prueba mínima 3: operación denegada sin cambiar datos | OBLIGATORIO | Ídem | P1–P5 y F2–F3 | R06 (13/11) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-73 | Prueba mínima 4: gestión administrativa de usuarios | OBLIGATORIO | Ídem | I1–I4 | R06 (13/11) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-74 | Prueba mínima 5: identidad y hora en el log de una operación confirmada | OBLIGATORIO | Ídem | A5 | R06 (13/11) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-75 | Prueba A: pedido Custom válido desde Java | OBLIGATORIO | Ídem | A1–A6 | R06 (13/11) | MAD §12 | CUMPLIDO Y PROBADO | [PENDIENTE (Omar): captura desde la ventana para la memoria] |
| AD-76 | Prueba B: confirmar sin stock suficiente | OBLIGATORIO | Ídem | B1–B2 | R06 (13/11) | MAD §12 | CUMPLIDO Y PROBADO | [PENDIENTE (Omar): captura para la memoria] |
| AD-77 | Prueba C: cancelar un pedido confirmado | OBLIGATORIO | Ídem | C1–C3 | R06 (13/11) | MAD §12 | CUMPLIDO Y PROBADO | [PENDIENTE (Omar): captura para la memoria] |
| AD-78 | Prueba D: ROLLBACK deliberado | OBLIGATORIO | Ídem | D1–D3 | R06 (13/11) | MAD §12 | CUMPLIDO Y PROBADO | [PENDIENTE (Omar): captura o salida SQL para la memoria] |
| AD-79 | Prueba E: consulta sin filtros, con dos filtros y «Limpiar filtros», comparada con SQL | OBLIGATORIO | Ídem | E1–E4 | R06 (13/11) | MAD §12 | CUMPLIDO Y PROBADO | — |
| AD-80 | Prueba F: búsqueda sin coincidencias y perfil sin permiso | OBLIGATORIO | Ídem | F1–F3 | R06 (13/11) | MAD §12 | CUMPLIDO Y PROBADO | — |
| AD-81 | Demostrar las pruebas con SQL y capturas; justificar las decisiones | OBLIGATORIO | `PruebasRubrica.java` (compara con SQL); `02_Acceso_Datos/evidencias/java-swing/` | Las pruebas comparan con SQL (R06, R08). Hay capturas de E, F, J, login, roles, errores y «Limpiar filtros» (R08) | R06; R08 (19 capturas en `02_Acceso_Datos/evidencias/java-swing/`) | MAD §12 | PARCIAL | [PENDIENTE (Omar): capturas de A, B, C, D, G e I y la del CSV abierto] (lista en el README de `java-swing`) |
| AD-82 | `actividad_sneaker.txt` en modo anexado, una línea por operación | OBLIGATORIO | `Archivos.registrar` (`FileWriter` con `true`) | G1 y H3 | R06, R07 (13/11) | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-83 | El TXT complementa la auditoría de la base, no la sustituye | OBLIGATORIO | `Archivos.java` y `08_auditoria.sql` | Existen los dos registros: G1 y A5 | R06 (13/11) | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-84 | Campos del TXT: fecha, usuario, rol, acción, resultado y pedido o filas | OBLIGATORIO | `Archivos.registrar` | Líneas de G1 | R06, R07 (13/11) | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-85 | El TXT no lleva contraseñas, hashes ni SQL | OBLIGATORIO | Ídem | Contenido de los TXT del 13/11 revisado: ningún dato sensible | R07; R08 («TXT sin contraseñas») | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-86 | Registrar Buscar, Limpiar filtros, crear, modificar, confirmar y cancelar pedidos, inicio de sesión e intento sin permiso | OBLIGATORIO | `Archivos.registrar`, llamado desde los paneles | El TXT de la prueba de ventanas trae 51 líneas nuevas, también LIMPIAR FILTROS (R08); el de `PruebasRubrica`, LOGIN, CONSULTA, CREAR, CONFIRMAR, CANCELAR y rechazados (R07) | R08; R07; `02_Acceso_Datos/evidencias/java-swing/actividad_sneaker-prueba-ventanas.txt` | MAD §10 | CUMPLIDO Y PROBADO | En Java no existe la operación «modificar pedido». [DUDA PARA EL PROFESOR (D10)] |
| AD-87 | Registrar también búsquedas sin resultados y errores controlados | OBLIGATORIO | Ídem | G1 (0 filas) y H4 (rechazado) | R06 (13/11) | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-88 | TXT fuera de la base, en una carpeta configurable, en UTF-8 y anexado | OBLIGATORIO | `carpeta_salida` en `conexion.properties` | G1 con `carpeta_salida=salidas` | R06 (13/11) | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-89 | Visible en disco sin esperar a cerrar Java | OBLIGATORIO | Ídem | G1 lee el archivo con la aplicación en marcha | R06 (13/11) | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-90 | Diferenciar `log_eventos` del TXT y explicarlo | OBLIGATORIO | `java/README.md` («`log_eventos` y el TXT no tienen los mismos eventos») | H4–H5: el TXT apunta el rechazo y `log_eventos` solo el alta buena (R06) | R06; MAD §10.2 | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-91 | Demostración en directo: tres consultas, tres líneas nuevas | OBLIGATORIO (demo) | `PanelConsultas.java`, `Archivos.java` | G1 | R06 (13/11) | MAD §10 | CUMPLIDO Y PROBADO | Ensayarlo en directo (MD, «Demostraciones de cada módulo») |
| AD-92 | `usuarios_sneaker.json` con identificador, usuario, rol y estado | OBLIGATORIO | `UsuarioDAO.exportarUsuariosJson` | I1 | R06, R07 (13/11) | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-93 | El JSON sin contraseñas, hashes ni secretos | OBLIGATORIO | Ídem | I2 | R06 (13/11) | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-94 | Botón «Exportar usuarios a JSON» solo para los roles autorizados | OBLIGATORIO | `PanelUsuarios.java` (pestaña solo del administrador) | Denegación al comercial, I5 (R06); la pestaña Usuarios solo en el rol administrador (R08) | R06; R08 (capturas 04 y 15) | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-95 | JSON actualizado al crear, modificar, desactivar o cambiar el rol | OBLIGATORIO | `UsuarioDAO.java` | I1 e I4 | R06 (13/11) | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-96 | El JSON refleja el estado confirmado; tras un error o ROLLBACK no publica cambios inexistentes | OBLIGATORIO | `UsuarioDAO.java` (exporta después del COMMIT) | I1–I4 cubren el caso bueno (R06). Ninguna prueba exporta tras un error o un ROLLBACK | R06 | MAD §10 | CUMPLIDO SIN PRUEBA DEL 13/11 | [PENDIENTE (Omar): probar y enseñar que tras un ROLLBACK el JSON no cambia]; no existe |
| AD-97 | JSON válido y estable que se puede volver a leer | OBLIGATORIO | `Archivos.guardarUsuariosJson` (lo relee) | I1 e I4 leen el JSON | R06 (13/11) | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-98 | Escritura segura: temporal y sustitución | OBLIGATORIO | `Archivos.guardarUsuariosJson` (código revisado) | Se ejecuta en I1–I4 | R06 (13/11) | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-99 | Justificar quién exporta los usuarios e impedirlo a quien no tenga permiso | OBLIGATORIO | `Sesion.java`, `java/README.md` | I5 | R06 (13/11) | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-100 | Un usuario nuevo sale en el JSON; al desactivarlo cambia su estado sin perder a nadie | OBLIGATORIO | `UsuarioDAO.java` | I1 e I4 | R06 (13/11) | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-101 | La analítica de §3.12 entra en el mínimo | OBLIGATORIO | `IndicadoresDAO.java`, `PanelIndicadores.java` | J1–J6 | R06 (13/11) | MAD §11 | CUMPLIDO Y PROBADO | — |
| AD-102 | Panel Java: pedidos, pares, importe y pedidos por estado | OBLIGATORIO | `PanelIndicadores.java` | J1 y J2 | R06; R08 (captura 11) | MAD §11 | CUMPLIDO Y PROBADO | — |
| AD-103 | Indicadores calculados en PostgreSQL sobre los registros autorizados | OBLIGATORIO | `IndicadoresDAO.java`, `12_consultas_panel.sql` | J1 igual que el SQL de P-A | R06 (13/11) | MAD §11 | CUMPLIDO Y PROBADO | [DUDA PARA EL PROFESOR (D10)]: qué significa «sobre los registros autorizados» |
| AD-104 | Modelos más pedidos y pares por talla con GROUP BY, y su utilidad | OBLIGATORIO | `IndicadoresDAO.java` | J3 y J4 | R06 (13/11) | MAD §11 | CUMPLIDO Y PROBADO | — |
| AD-105 | Stock bajo con un umbral configurable, ordenado | OBLIGATORIO | Consulta C8 del 12; `PanelIndicadores.java` | J5 (umbral 19: 111 referencias) | R06 (J5: 111 = SQL); R08 (umbral 10, 25 y 0; capturas 11 a 13) | MAD §11 | CUMPLIDO Y PROBADO | — |
| AD-106 | CSV de una consulta filtrada desde Java, igual que la tabla | OBLIGATORIO | `Archivos.exportarCsv` | J6 (11 filas y 9 columnas) | R06, R07 (13/11) | MAD §11 | CUMPLIDO Y PROBADO | — |
| AD-107 | Conservar la exportación del pedido Custom para PSP | OBLIGATORIO | `15_exportar_fabricacion.sql` | 15 (2 PASS) | R01 (13/11) | MAD §11 | CUMPLIDO Y PROBADO | — |
| AD-108 | Interpretar los datos con un criterio: cancelados, cabecera frente a líneas, nulos y orden | OBLIGATORIO | `12_consultas_panel.sql` (P-A excluye cancelados); README §10 | J1–J4 | R06 (13/11) | MAD §11 | CUMPLIDO Y PROBADO | [POR DECIDIR (los tres)]: el criterio de «venta» que se usa igual en AD y en Python |
| AD-109 | Prueba G | OBLIGATORIO | `PruebasRubrica.java` | G1 | R06 (13/11) | MAD §12 | CUMPLIDO Y PROBADO | — |
| AD-110 | Prueba H | OBLIGATORIO | Ídem | H1–H5 | R06 (13/11) | MAD §12 | CUMPLIDO Y PROBADO | — |
| AD-111 | Prueba I | OBLIGATORIO | Ídem | I1–I5 | R06 (13/11) | MAD §12 | CUMPLIDO Y PROBADO | — |
| AD-112 | Prueba J | OBLIGATORIO | Ídem | J1–J6 | R06 (13/11) | MAD §12 | CUMPLIDO Y PROBADO | — |
| AD-113 | Caso común: 40 pares de Runner X en varias tallas, registrado y confirmado desde Java | OBLIGATORIO (demo) | `18_datos_so024.sql`; lanzador de prueba no incluido en el repositorio (`03_PSP/evidencias/so024_provisional/01_cadena_SO024_PROVISIONAL.txt:3`) | 18 → métodos de «Nuevo pedido» (`PedidoDAO.crearPedido` y `confirmarPedido` con la sesión de `admin.demo`) → 9 líneas, 40 pares y 3.996,00 €; stock 8,7,5,4,3,4,5,6,8; auditoría de `admin.demo` | R23 | MAD §13; MD §2–§3 | PROVISIONAL | **PUEDE IMPEDIR APROBAR.** Falta la evidencia de alta y confirmación desde la ventana con el caso de la demo. El ensayo no acredita S00005; no exige crear un SO024 oficial. |
| AD-114 | Consultar el resultado, exportar el CSV para PSP y enseñar la cancelación o la falta de stock | OBLIGATORIO (demo) | 15; pruebas B y C | SO024 → 15 (9 filas). B y C, con pedidos de prueba | R23 (15: 9 filas); R06 (B y C con pedidos de prueba) | MAD §13; MD §2–§3 | PROVISIONAL | **PUEDE IMPEDIR APROBAR.** Falta evidencia completa de la demostración con pedidos de PRUEBA; S00005 no se ha acreditado en AD. |
| AD-115 | Filtrar por cliente y estado, ver el pedido, limpiar los filtros y comprobar que otro perfil solo ve lo suyo | OBLIGATORIO (demo) | `PanelConsultas.java` | E2, E4 y F2, con pedidos de prueba | R06; R08 | MAD §13; MD §2–§3 | PROVISIONAL | **PUEDE IMPEDIR APROBAR.** Falta el recorrido completo de la demo en ventana; no hay prueba de S00005 ni se exige el identificador SO024. |
| AD-116 | TXT tras cada búsqueda, panel, CSV filtrado y usuario nuevo en el JSON | OBLIGATORIO (demo) | — | G, J e I | R06 (G, I y J); R08 | MAD §13; MD §2–§3 | PROVISIONAL | **PUEDE IMPEDIR APROBAR.** Faltan evidencias del ensayo completo de la demo (MD); no hay prueba de S00005 ni se exige el identificador SO024. |
| AD-117 | Entregable 01 · Diseño: diagrama E-R y explicación | OBLIGATORIO (entregable) | `modelo/`, `modelo-er/`, `documentacion/modelo_relacional.md` | — | MAD §2 (diagrama mermaid y explicación); `documentacion/modelo_relacional.md` | MAD §2 | PARCIAL | **PUEDE IMPEDIR APROBAR.** [PENDIENTE (Álvaro): el E-R oficial en PNG] |
| AD-118 | Entregable 02 · Scripts de creación, carga y consultas | OBLIGATORIO (entregable) | `02_Acceso_Datos/sql/` | Desde cero | R01 (13/11) | MAD §3 y §12 | CUMPLIDO Y PROBADO | — |
| AD-119 | Entregable 03 · Pruebas de restricciones, transacciones, triggers, stock, totales y rollback | OBLIGATORIO (entregable) | `09`–`16` | 123 PASS | R01 (13/11) | MAD §3 y §12 | CUMPLIDO Y PROBADO | — |
| AD-120 | Entregable 04 · CSV Custom, pruebas con Java y correspondencia con PSP y Odoo | OBLIGATORIO (entregable) | `15`, `PruebasRubrica.java` | 15, A–J, PSP | R01, R06, R09 (13/11) | MAD §1 y §13 | PARCIAL | Correspondencia documental parcial con Odoo (MEM §6.1: S00005 y CUSTOM-40; S00001 y NOVA-0011, solo en el texto del PDF, p. 13). **Límite declarado:** no hay exportación de Odoo ni conciliación probada. **[BERME: comprobar S00001 en su Odoo]** |
| AD-121 | Entregable 05 · Apartado de AD en la memoria común | OBLIGATORIO (entregable) | — | — | `02_Acceso_Datos/memoria/MEMORIA_ACCESO_DATOS.md` (decisiones, pruebas y dificultades, §1–§14) | MAD | PARCIAL | **PUEDE IMPEDIR APROBAR.** Aportaciones personales no confirmadas y E-R en PNG pendiente. No se exige crear un SO024 oficial. |
| AD-122 | Entregable 06 · PL/pgSQL, `log_eventos` y capturas de auditoría con marca temporal | OBLIGATORIO (entregable) | `02`, `03`, `08` | Batería 09; A5 | R01, R06; R08 (captura 10) | MAD §6 y §7 | CUMPLIDO Y PROBADO | — |
| AD-123 | Entregable 07 · Proyecto Java ejecutable, instrucciones de conexión y pruebas del flujo | OBLIGATORIO (entregable) | `java/`, `java/README.md`, `ejecutar.bat`, `pruebas.bat` | A y C | R06; R24 (`pruebas.bat` 47/47 siguiendo el manual en un clon nuevo) | MAD §8; MI §4 | CUMPLIDO Y PROBADO | — |
| AD-124 | Entregable 08 · Scripts de roles y usuarios, matriz justificada, login, permitido y denegado, log con actor | OBLIGATORIO (entregable) | `07`, `13`, `17`; `java/README.md`; capturas 01–03 | L, P, F y A5 | R06; R08 (capturas 01–03, 15–17) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-125 | Entregable 09 · Código del botón y de los filtros, capturas (sin filtros, combinados y sin coincidencias), SQL parametrizado y prueba por rol | OBLIGATORIO (entregable) | `PanelConsultas.java`, `PedidoDAO.java`; capturas 06 y 08 | E y F (R06); en la ventana: sin filtros, combinados, sin coincidencias y tras «Limpiar filtros» (R08) | R06; R08 (capturas 06, 08 y 19) | MAD §8 | CUMPLIDO Y PROBADO | — |
| AD-126 | Entregable 10 · TXT, código de anexado y capturas de las entradas nuevas | OBLIGATORIO (entregable) | `Archivos.java` | G1 (R06); las 51 líneas nuevas del TXT de la prueba de ventanas (R08) | R07; R08; `java-swing/actividad_sneaker-prueba-ventanas.txt` | MAD §10.1 | PARCIAL | [PENDIENTE (Omar): captura del TXT abierto con las líneas nuevas] |
| AD-127 | Entregable 11 · JSON sin credenciales, lógica de actualización y pruebas | OBLIGATORIO (entregable) | `UsuarioDAO.java`, `Archivos.java` | I | R06, R07 (13/11) | MAD §10.3 | CUMPLIDO Y PROBADO | — |
| AD-128 | Entregable 12 · Indicadores, análisis por modelo, talla y stock, panel Java y CSV filtrado | OBLIGATORIO (entregable) | `IndicadoresDAO.java`, `PanelIndicadores.java` | J | R06; R08 (capturas 07 y 11–13) | MAD §11 | CUMPLIDO Y PROBADO | — |
| AD-129 | Triggers y funciones en PL/pgSQL, no simulados en Java | OBLIGATORIO | `02`, `03`, `08` | A3–A6 | R06 (13/11) | MAD §6 | CUMPLIDO Y PROBADO | — |
| AD-130 | Autenticación y permisos obligatorios | OBLIGATORIO | `Sesion.java`, `07` | L y P | R06 (13/11) | MAD §9 | CUMPLIDO Y PROBADO | — |
| AD-131 | Interfaz funcional mínima | OBLIGATORIO | `java/src/nova/` | PruebasRubrica | R06; R08 | MAD §8 | CUMPLIDO Y PROBADO | — |
| AD-132 | Base reconstruible desde los archivos entregados | OBLIGATORIO | `02_Acceso_Datos/sql/`; README §3 | Base vacía con los scripts 01–23 (R01) y siguiendo el manual en un clon nuevo (R24) | R01; R24 | MI §3; README AD §3 | CUMPLIDO Y PROBADO | — |
| AD-133 | Se recrean también roles, usuarios ficticios y permisos | OBLIGATORIO | `07`, `13`, `17` | Scripts con salida 0; L1 | R01; R06; R24 | MI §3; README AD §3 | CUMPLIDO Y PROBADO | — |
| AD-134 | Consultas con resultados verificables con los datos de prueba | OBLIGATORIO | `06`, `12` | Las 8 consultas del 06 y las del 12 dan filas verificables; la 3 (HAVING), 1 fila | R02 | MAD §4 | CUMPLIDO Y PROBADO | — |
| AD-135 | Todos comprenden el modelo y explican consultas representativas | OBLIGATORIO (defensa) | — | — | — | GD §1–§3; SD | NO VERIFICABLE | Ensayo individual con el banco de preguntas de GD §1–§3 (y SD) |
| AD-137 | TXT, JSON y CSV coherentes con PostgreSQL en datos y permisos | OBLIGATORIO | `Archivos.java` | G, I y J6 comparan con SQL | R06 (13/11) | MAD §10 | CUMPLIDO Y PROBADO | — |
| AD-138 | Aprobar todas las partes (tribunal, memoria, entregable y defensa) | OBLIGATORIO (condición) | — | — | — | — | NO VERIFICABLE | **PUEDE IMPEDIR APROBAR.** Cada parte tiene que estar aprobada. Aportaciones y E-R en PNG siguen limitados; no hay prueba de S00005 en AD. |

**No obligatorios de AD** (15 filas):

| ID | Qué es | Carácter | Estado |
|---|---|---|---|
| AD-25 | Exportación manual documentada, sin integración automática con Odoo | ADMITIDO | Se usa: el 15 con `psql`, en README AD §14 y MI §3 |
| AD-32 | Tabla de existencias por variante y talla | OPCIONAL (permitido) | Se usa (`existencias` por SKU y nave) |
| AD-38 | No se evalúa el aspecto visual | NO EXIGIDO | — |
| AD-52 | No hace falta refrescar la tabla sola | NO EXIGIDO | — |
| AD-55 | Más de tres roles si se justifica | OPCIONAL | No se usa (3 roles en Java; `nova_cliente` es de la tienda) |
| AD-68 | Autorización con tablas y validaciones en el acceso a datos | ADMITIDO | Se usa, junto con roles de PostgreSQL |
| AD-69 | GRANT/REVOKE o roles nativos, justificados | OPCIONAL | Se usa (`07`, `17`, `java_nova`) y se justifica en MAD §9 |
| AD-136 | Se valora la coherencia más que las funciones no pedidas | CRITERIO | Ver el apartado 3: las ampliaciones no deben quitar tiempo a lo obligatorio |
| AD-139 | Vistas SQL | OPCIONAL | No hecho |
| AD-140 | Índices justificados con EXPLAIN | OPCIONAL | Hay 5 índices en el esquema, sin EXPLAIN |
| AD-141 | Paginación | OPCIONAL | No hecho |
| AD-142 | Importación CSV con validación | OPCIONAL | No hecho |
| AD-143 | Gráficos de tendencias | OPCIONAL | No hecho en Java (sí en Python y en el panel web) |
| AD-144 | Auditoría con valores anteriores y posteriores en JSONB | OPCIONAL | No hecho |
| AD-145 | LISTEN/NOTIFY | OPCIONAL | No hecho |

### 2.3 PSP (módulo 0490, IM §4.3, anexo y RA1)

| ID | REQUISITO | OBL/OPC | ARCHIVO | COMPROBACIÓN CONCRETA | EVIDENCIA | DOCUMENTADO EN | ESTADO | PENDIENTE |
|---|---|---|---|---|---|---|---|---|
| IM-PSP-04 | Recibe una exportación del pedido Custom y coordina varios procesos | OBLIGATORIO (enunciativo) | `03_PSP/ProcesadorPedidosCustom.java` | `ProcesadorPedidosCustom` con CUSTOM-40: los tres hijos y el padre con código 0 (R09); con SO024 PROVISIONAL, código 0 (R23) | R09; R23 | DPSP §1–§2; MEM §5 | CUMPLIDO Y PROBADO | — |
| IM-PSP-05 | No sustituye a Ventas ni a Fabricación de Odoo | OBLIGATORIO (enunciativo) | `03_PSP/README.md` («Lo que no hace»); la ficha lo dice | 05: ficha y registro | R09 (`05_psp_custom40.txt`) | DPSP §1; MEM §5 | CUMPLIDO Y PROBADO | — |
| IM-PSP-06 | Proceso coordinador que lanza los hijos con ProcessBuilder | OBLIGATORIO (enunciativo) | `03_PSP/GestorProcesos.java` | 01 y 06a | R09 (PruebasPsp 01 y 06a) | DPSP §2 y §5; MEM §5 | CUMPLIDO Y PROBADO | — |
| IM-PSP-07 | Procesos especializados: validar, resumir por talla o variante, ficha de taller o informe | AMBIGUO («Como mínimo, pueden») | `ValidadorPedidoCustom.java`, `src/Psp/AnalizadorTallas.java` (Álvaro), `GeneradorFichaTaller.java` | 03, 04 y 05 (cada hijo por separado) | R09 (13/11) | DPSP §2; MEM §5 | CUMPLIDO Y PROBADO | [DUDA PARA EL PROFESOR (D9)]: el número mínimo de hijos |
| IM-PSP-08 | Comunicación por stdin/stdout, tuberías o IPC | OBLIGATORIO | `GestorProcesos.java` | 06a (eco) y 06b (la personalización cruza los tres procesos) | R09 (13/11) | DPSP §5; MEM §5 | CUMPLIDO Y PROBADO | — |
| IM-PSP-09 | Códigos de salida, errores, tiempos de espera y finalización, justificados | OBLIGATORIO | `GestorProcesos.java`; `03_PSP/README.md` («Códigos de salida») | PruebasPsp 08a–b, 09a–b, 10 (tiempo agotado a los 2 s), 11 y 12a–m; archivo inexistente → código 1 y cantidad 0 → código 2 (R09) | R09 (`04_psp_pruebas.txt`, `06_psp_error_*.txt`) | DPSP §6–§8; MEM §5 | CUMPLIDO Y PROBADO | — |
| IM-PSP-10 | Salida comprensible relacionada con el pedido original de Odoo | OBLIGATORIO (enunciativo) | `GeneradorFichaTaller.java` → `ficha_taller_<ref>.txt` y `registro_psp.txt` | 05; `ficha_taller_SO024_PROVISIONAL.txt` (ensayo) | R09; R23 (`ficha_taller_SO024_PROVISIONAL.txt`) | DPSP §9.3; MEM §5 | PARCIAL | No hay CSV ni ficha acreditados de S00005; el ensayo SO024 no demuestra su relación con el pedido de Odoo. |
| IM-PSP-15 | Autocomprobación: función auxiliar clara sin sustituir a Odoo | AUTOCOMPROBACIÓN | Igual que PSP-05 | Ídem | R09 (13/11) | DPSP §1; MEM §5 | CUMPLIDO Y PROBADO | — |
| IM-PSP-16 | Autocomprobación: lanza y controla procesos | AUTOCOMPROBACIÓN | `GestorProcesos.java` | 01 y 10 | R09 (13/11) | DPSP §5; MEM §5 | CUMPLIDO Y PROBADO | — |
| IM-PSP-17 | Autocomprobación: intercambian información y gestionan errores y códigos | AUTOCOMPROBACIÓN | Ídem | 06–12 | R09 (13/11) | DPSP §4–§8; MEM §5 | CUMPLIDO Y PROBADO | — |
| IM-PSP-23 | Uso correcto de ProcessBuilder | CRITERIO | `GestorProcesos.java` | 01–12 | R09 (13/11) | DPSP §5; MEM §5 | CUMPLIDO Y PROBADO | — |
| IM-PSP-24 | Paso de parámetros o comunicación por stdin/stdout | CRITERIO | Ídem | 06a | R09 (13/11) | DPSP §5; MEM §5 | CUMPLIDO Y PROBADO | — |
| IM-PSP-25 | Lectura separada de stdout y stderr (cuando proceda) | CRITERIO (condicional) | `GestorProcesos.java` (3 hilos) | 07 | R09 (13/11) | DPSP §5.1; MEM §5 | CUMPLIDO Y PROBADO | — |
| IM-PSP-26 | `waitFor` y tratamiento de los códigos de salida | CRITERIO | Ídem | 08a (código 7 recogido exacto) | R09 (13/11) | DPSP §6; MEM §5 | CUMPLIDO Y PROBADO | — |
| IM-PSP-27 | Procesos bloqueados o que tardan demasiado (si se ha trabajado en clase) | CRITERIO (condicional) | `GestorProcesos.java` (`waitFor` con límite y `destroyForcibly`) | 10: se cancela a los 2,0 s en vez de 60 | R09 (13/11) | DPSP §7; MEM §5 | CUMPLIDO Y PROBADO | El `LanzadorAnalizador` de Álvaro, que el coordinador no usa, no aplica el tiempo máximo. [ÁLVARO: revisar y confirmar] |
| IM-PSP-28 | Separación de responsabilidades y código legible | CRITERIO | Tres hijos y un gestor; limpieza de comentarios (`eae5fc5`) | 03–05 prueban cada hijo por separado | R09 (27/27 tras la limpieza de comentarios) | DPSP §2; MEM §5 | CUMPLIDO Y PROBADO | [POR DECIDIR (los tres)]: qué se hace con la versión anterior (`LanzadorValidacion` y el `AnalizadorTallas` de la raíz) |
| IM-PSP-29 | Registro que permita seguir el pedido y relacionarlo con su referencia de Odoo | CRITERIO | `registro_psp.txt` | 05 | R09 (13/11) | DPSP §9.3; MEM §5 | PARCIAL | **Límite declarado:** no hay exportación de S00005 desde Odoo; `registro_psp.txt` lleva la referencia del pedido de PostgreSQL (por ejemplo, CUSTOM-40) |
| IM-PSP-RA1-cefg | RA1 CE c), e)-g): subprocesos, compartir información, sincronizar y valores de retorno | CRITERIO (RA/CE) | `03_PSP/` | 01–10 | R09 (13/11) | DPSP §5 y §10; MEM §5 | CUMPLIDO Y PROBADO | Aquí sincronizar es esperar con `waitFor`, un hijo tras otro. [DUDA PARA EL PROFESOR (D9)]: si la sincronización obliga a usar hilos |
| IM-PSP-RA1-i | RA1 CE i): depurar y documentar | CRITERIO (RA/CE) | `03_PSP/README.md`; `scripts/comprobar_psp.py` | Regresión final: 27/27 y comprobador rápido correcto con el cambio de Berme | cierre-entrega-20261113/psp_pruebas.txt y psp_comprobador.txt | DPSP §10 y §13; MEM §5 | CUMPLIDO Y PROBADO | — |

**No obligatorios de PSP:**

| ID | Qué es | Carácter | Estado |
|---|---|---|---|
| IM-PSP-01 a 03 | Objetivos y propuesta de una aplicación Java de consola | OBJETIVO u ORIENTATIVO | Cubiertos: aplicación Java de consola |
| IM-PSP-11 | Ejemplo SO024: validar, agrupar tallas, ficha y registro de cada subproceso | ORIENTATIVO | PROVISIONAL: R23 («9 tallas; 40 pares», código 0 y `ficha_taller_SO024_PROVISIONAL.txt`) |
| IM-PSP-13 y 14 | Guion de demo, pasos 6 y 7 | ORIENTATIVO | MD §3 (PSP) y §7 (Odoo documental); no hay relación de S00005 con la ficha PSP acreditada |
| IM-PSP-18 a 22 | Clases propuestas en el anexo | ORIENTATIVO | Hechas con esos nombres y probadas (R09) |
| IM-PSP-12 y 30 | Varias órdenes a la vez, recursos compartidos, procesos frente a hilos | OPCIONAL («Ampliación posterior») | No hecho («Un pedido por archivo», DPSP §13) |

### 2.4 Python (Ampliación de Python: ciencia de datos y dashboard)

Las 209 filas obligatorias y las 5 condicionales de la rúbrica de Python. Todas las rutas son de `04_Python/`.
- En la columna COMPROBACIÓN va el nombre de la prueba de `tests/` que lo cubre. Las 265 pasaron el 13/11 con salida detallada, así que cada nombre se puede buscar en `RF/04_python/02_unittest.txt` (R14).
- **Los datos de `entrada_acc/` son de PRUEBA** («Tipo: PRUEBA» en `ORIGEN.txt`; exportados el 9/11 de una base reconstruida con los scripts). Por eso lo que exige datos «REALES» en la defensa queda en PARCIAL.

| ID | REQUISITO | OBL/OPC | ARCHIVO | COMPROBACIÓN CONCRETA | EVIDENCIA | DOCUMENTADO EN | ESTADO | PENDIENTE |
|---|---|---|---|---|---|---|---|---|
| PY-01 | Proceso reproducible que distingue datos reales, simulados y predicciones | OBLIGATORIO | `main.py`, `config.py` (`TIPOS_ORIGEN`) | `test_todo_etiquetado_como_sintetico`, `test_datos_de_prueba_se_dicen_de_prueba` | R14, R15 | ITP §1 | CUMPLIDO Y PROBADO | — |
| PY-02 | No crear otra empresa ni duplicar datos | OBLIGATORIO (límite) | `entrada_acc/` (sale del 16 de AD) | `test_nunca_se_guarda_en_entrada_acc` | R14, R15 (13/11) | ITP §1 | CUMPLIDO Y PROBADO | — |
| PY-03 | Pipeline reproducible, auditoría, tablas en pandas, KPIs y aplicación web | OBLIGATORIO | Todo `04_Python/` | 265 pruebas y las 93 salidas de `main.py` | R14, R15 | ITP §1 | CUMPLIDO Y PROBADO | — |
| PY-04 | Volumen vendido y parte cancelada, pendiente y personalizada | OBLIGATORIO | `kpis.py` | `test_estados_de_los_pedidos`, `test_custom_y_mas_solicitados` | R14 (13/11) | ITP §1 | CUMPLIDO Y PROBADO | — |
| PY-05 | Modelos, tallas y periodos con más demanda; estacionalidad | OBLIGATORIO | `analiticas.py` (matrices y `ventas_por_periodo`) | `test_matriz_modelo_talla`, `test_dos_meses` | R14 (13/11) | ITP §1 | CUMPLIDO Y PROBADO | Con la exportación de PRUEBA hay un solo mes: la estacionalidad solo se ve con los sintéticos |
| PY-06 | Clientes con más valor, recurrencia o tiempo sin comprar | OBLIGATORIO | `segmentacion.py` (RFM) | `test_recency_desde_la_fecha_de_corte`, `test_frequency_cuenta_pedidos_y_monetary_suma_importes` | R14 (13/11) | ITP §1 | CUMPLIDO Y PROBADO | Con la exportación de PRUEBA, NO CALCULABLE (un solo cliente con compras) |
| PY-07 | Qué problemas de los CSV impiden confiar | OBLIGATORIO | `calidad.py` | 38 pruebas de `test_calidad.py` | R14 (13/11) | ITP §1 | CUMPLIDO Y PROBADO | — |
| PY-08 | Dónde hay riesgo de rotura de stock | OBLIGATORIO | `analiticas.py` (stock bajo y cobertura) | `test_stock_bajo_ordenado`, `test_cobertura_con_demanda` | R14 (13/11) | ITP §1 | CUMPLIDO Y PROBADO | — |
| PY-09 | Estimar la demanda y comprobar si se supera a la predicción ingenua | OBLIGATORIO | `prediccion.py` | `test_comparacion_de_metodos`, `test_si_no_mejora_lo_dice` | R14 (13/11) | ITP §1 | CUMPLIDO Y PROBADO | La regresión no mejora al baseline, y se dice. Con la exportación de PRUEBA es NO CALCULABLE |
| PY-10 | Flujo obligatorio: PostgreSQL/Java → CSV → validación → cruces → DataFrames → análisis → dashboard de 60 s → informes | OBLIGATORIO | `16_exportar_csv_dashboard.sql` → `entrada_acc/` → `pipeline.py` → `analiticas.py` → `app_dashboard.py` | Cadena 16 → Python con SO024 PROVISIONAL (R23); 265 pruebas (R14) | R14, R23 | ITP §2 | CUMPLIDO Y PROBADO | **Límite declarado:** la exportación se entrega como PRUEBA (`04_Python/entrada_acc/ORIGEN.txt`); no hay exportación REAL |
| PY-11 | Mantener la ejecución por consola | OBLIGATORIO | `main.py` | Modos real, sintético y sintético con errores | R15 (13/11) | ITP §2 | CUMPLIDO Y PROBADO | — |
| PY-12 | Python, pandas, NumPy, Matplotlib, scikit-learn y Streamlit | OBLIGATORIO | `requirements.txt` | Las pruebas las importan todas | R14 (13/11) | ITP §2 | CUMPLIDO Y PROBADO | — |
| PY-15 | Los cálculos, fuera de `app_dashboard.py` | OBLIGATORIO | `analiticas.py`, `kpis.py`, `filtros.py` | `test_cuatro_filtros_combinados_cambian_los_kpis`; `test_filtrado_cruzado_R6` (el panel da lo mismo que pandas) | R14 (13/11) | ITP §2 | CUMPLIDO Y PROBADO | — |
| PY-16 | Dependencias en `requirements.txt` | OBLIGATORIO | `requirements.txt` | 265 pruebas | R14 (13/11) | ITP §2 | CUMPLIDO Y PROBADO | La instalación desde cero está en PY-219 |
| PY-17 | Dashboard web funcional en Streamlit | OBLIGATORIO | `app_dashboard.py` | 11 pruebas con `AppTest` en `test_dashboard.py` | R14; R25 (Edge, 13/11) | ITP §2 | CUMPLIDO Y PROBADO | — |
| PY-18 | Integración con ACC por CSV: cada minuto se revisan, se reprocesan y se reflejan los cambios | OBLIGATORIO | `actualizacion.py` | `test_relee_los_csv_cada_60_segundos` | R14 (13/11) | ITP §2 | CUMPLIDO Y PROBADO | Los CSV son de PRUEBA. **Límite declarado:** la exportación se entrega como PRUEBA (`04_Python/entrada_acc/ORIGEN.txt`); no hay exportación REAL |
| PY-19 | Acordar la exportación con AD y tener un diccionario de equivalencias | OBLIGATORIO | `02_Acceso_Datos/sql/16_exportar_csv_dashboard.sql`; `diccionario_datos.md` («Equivalencias con la rúbrica») | 16: 2 PASS | R01 (16: 2 PASS) | ITP §3 | CUMPLIDO Y PROBADO | — |
| PY-20 | `clientes.csv` | OBLIGATORIO | `entrada_acc/clientes.csv` | `test_cinco_validos` | R14, R15 (13/11) | ITP §3 | CUMPLIDO Y PROBADO | — |
| PY-21 | `modelos.csv` (categoría solo si existe) | OBLIGATORIO | `entrada_acc/modelos.csv` | Ídem | R14, R15 (13/11) | ITP §3 | CUMPLIDO Y PROBADO | No hay categoría en el esquema; el diccionario lo dice |
| PY-22 | `pedidos.csv` | OBLIGATORIO | `entrada_acc/pedidos.csv` | Ídem | R14, R15 (13/11) | ITP §3 | CUMPLIDO Y PROBADO | — |
| PY-23 | `lineas_pedido.csv` | OBLIGATORIO | `entrada_acc/lineas_pedido.csv` | Ídem | R14, R15 (13/11) | ITP §3 | CUMPLIDO Y PROBADO | — |
| PY-24 | `stock.csv` con fecha de corte | OBLIGATORIO | `entrada_acc/stock.csv` | Ídem | R14, R15 (13/11) | ITP §3 | CUMPLIDO Y PROBADO | — |
| PY-25 | Diccionario: nombre, significado, origen, tipo, unidad, valores permitidos y nulos | OBLIGATORIO | `diccionario_datos.md` | — | `diccionario_datos.md`; ITP §3 | ITP §3 | CUMPLIDO (DOCUMENTADO) | La unidad va dentro de la columna «Valores» (pares, euros); no tiene columna propia |
| PY-26 | Los ID no se tratan como magnitudes | OBLIGATORIO | `pipeline.py` (los ID como texto) | `test_identificadores_que_no_se_confunden` | R14 (13/11) | ITP §3 | CUMPLIDO Y PROBADO | — |
| PY-27 | Explicar el formato de fechas, moneda, decimal, codificación y delimitador | OBLIGATORIO | `diccionario_datos.md` («Formato de los cinco archivos»), `pipeline.py` | `test_separador_punto_y_coma`, `test_no_es_utf8` | R14 (13/11) | ITP §3 | CUMPLIDO Y PROBADO | — |
| PY-28 | Si se usan `usuarios_sneaker.json` o `actividad_sneaker.txt`, como fuentes complementarias y sin datos sensibles | CONDICIONAL | — | — | — | ITP §3 | OPCIONAL | No aplica: Python no usa esos archivos |
| PY-29 | Norma: análisis reales con CSV de AD; aprendizaje automático con sintéticos identificados; nunca mezclados | OBLIGATORIO | `config.py`, `main.py` (modos) | `test_cambio_de_origen_no_mezcla`, `test_nunca_se_guarda_en_entrada_acc`, `test_todo_etiquetado_como_sintetico` | R14 (13/11) | ITP §10 | CUMPLIDO Y PROBADO | — |
| PY-30 | Los CSV de AD son la fuente del dashboard operativo | OBLIGATORIO | `app_dashboard.py` (origen ACC por defecto) | `test_arranca_con_la_exportacion_de_acceso_a_datos` | R14 (13/11) | ITP §10 | CUMPLIDO Y PROBADO | **Límite declarado:** la exportación se entrega como PRUEBA (`04_Python/entrada_acc/ORIGEN.txt`); no hay exportación REAL |
| PY-31 | Histórico sintético aparte (`generador_datos.py`), nunca como ventas reales | OBLIGATORIO | `generador_datos.py`, `datos_sinteticos/` | `test_nunca_se_guarda_en_entrada_acc`, `test_origen_sintetico` | R14 (13/11) | ITP §10 | CUMPLIDO Y PROBADO | — |
| PY-32 | Al menos 800 pedidos, 1.600 líneas, 40 clientes, 12 modelos y 18 meses | OBLIGATORIO | `generador_datos.py` | `test_minimos_de_la_rubrica`, `test_dieciocho_meses_seguidos` | R14 (13/11) | ITP §10 | CUMPLIDO Y PROBADO | Salen 900 pedidos, 1.777 líneas, 40 clientes y 12 modelos, de 2025-05 a 2026-10 |
| PY-33 | Distribución explicable y no uniforme | OBLIGATORIO | Ídem | `test_variedad_que_no_es_uniforme` | R14 (13/11) | ITP §10 | CUMPLIDO Y PROBADO | — |
| PY-34 | Respetar claves, fechas, estados, cantidades, precios y pedidos frente a líneas | OBLIGATORIO | Ídem | `test_sin_claves_huerfanas`, `test_reglas_de_negocio`, `test_pedidos_y_lineas_cuadran` | R14 (13/11) | ITP §10 | CUMPLIDO Y PROBADO | — |
| PY-35 | Variaciones por mes, modelo, talla y tipo | OBLIGATORIO | Ídem | `test_variedad_que_no_es_uniforme` | R14 (13/11) | ITP §10 | CUMPLIDO Y PROBADO | — |
| PY-36 | Documentar las hipótesis de la simulación | OBLIGATORIO | `datos_sinteticos.md` («Hipótesis de la simulación») | — | `datos_sinteticos.md`; ITP §10 | ITP §10 | CUMPLIDO (DOCUMENTADO) | — |
| PY-37 | Semilla fija y ejecución reproducible | OBLIGATORIO | `generador_datos.py` (semilla 2026) | `test_misma_semilla_mismos_datos` | R14 (13/11) | ITP §10 | CUMPLIDO Y PROBADO | — |
| PY-38 | Copia con incidencias provocadas | OBLIGATORIO | `datos_sinteticos/con_errores/` | `test_con_errores_se_detecta_cada_regla`, `test_cada_error_esta_documentado` | R14, R15 (13/11) | ITP §10 | CUMPLIDO Y PROBADO | — |
| PY-39 | Informes en modo real y sintético, separados y etiquetados | OBLIGATORIO | `main.py --modo` | `test_cada_modo_tiene_sus_carpetas` | R14, R15 (13/11) | ITP §10 | CUMPLIDO Y PROBADO | — |
| PY-40 | El dashboard funciona por defecto y en la defensa solo con exportaciones REALES de AD | OBLIGATORIO | `app_dashboard.py`, `entrada_acc/ORIGEN.txt` | `test_arranca_con_la_exportacion_de_acceso_a_datos` | R14 (13/11) | ITP §10 | PARCIAL | `entrada_acc` es «Tipo: PRUEBA». **Límite declarado:** la exportación se entrega como PRUEBA (`04_Python/entrada_acc/ORIGEN.txt`); no hay exportación REAL y poner «Tipo: REAL» |
| PY-42 | Cargar los 5 CSV y comprobar que existen, con cabeceras y columnas obligatorias | OBLIGATORIO | `pipeline.py` | `test_cinco_validos`, `test_falta_un_archivo`, `test_columna_obligatoria_ausente` | R14 (13/11) | ITP §4 | CUMPLIDO Y PROBADO | — |
| PY-43 | Copia lógica de los originales: no se sobrescriben | OBLIGATORIO | `pipeline.guardar_salida` | `test_no_modifica_el_original`, `test_nunca_escribe_en_la_carpeta_de_entrada` | R14 (13/11) | ITP §4 | CUMPLIDO Y PROBADO | — |
| PY-44 | Manifiesto de origen: fichero, fecha, filas, columnas y tamaño | OBLIGATORIO | `pipeline.manifiesto` | `test_cinco_validos` (comprueba las filas del manifiesto) | R14 (13/11) | ITP §4 | CUMPLIDO Y PROBADO | — |
| PY-45 | Normalizar tipos y fechas; controlar delimitadores, nulos y decimales | OBLIGATORIO | `pipeline.py` | `test_tipos_convertidos`, `test_datos_mal_formados`, `test_separador_punto_y_coma` | R14 (13/11) | ITP §4 | CUMPLIDO Y PROBADO | — |
| PY-46 | Documentar las conversiones fallidas | OBLIGATORIO | `pipeline.py` | `test_fecha_y_logico_mal_formados`, `test_informa_de_todos_los_errores` | R14 (13/11) | ITP §4 | CUMPLIDO Y PROBADO | — |
| PY-47 | Decisiones en el archivo de incidencias y resumen de calidad por tabla | OBLIGATORIO | `calidad.py` | `test_csv_de_incidencias`, `test_csv_resumen` | R14 (13/11) | ITP §4 | CUMPLIDO Y PROBADO | — |
| PY-48 | 12 comprobaciones con tabla, registro, regla, gravedad y tratamiento | OBLIGATORIO | `calidad.py`, `calidad_datos.md` | `test_calidad.py`; `test_con_errores_se_detecta_cada_regla` | R14 (13/11) | ITP §5 | CUMPLIDO Y PROBADO | — |
| PY-49 | Regla 01: fichero vacío o cabeceras insuficientes | OBLIGATORIO | `calidad.py` | `test_archivo_vacio`, `test_falta_columna`, `test_solo_cabecera_es_advertencia` | R14 (13/11) | ITP §5 | CUMPLIDO Y PROBADO | — |
| PY-50 | Regla 02: ID duplicados | OBLIGATORIO | Ídem | `test_pedido_duplicado_por_id`, `test_id_vacio_se_rechaza` | R14 (13/11) | ITP §5 | CUMPLIDO Y PROBADO | — |
| PY-51 | Regla 03: claves huérfanas | OBLIGATORIO | Ídem | `test_linea_huerfana`, `test_pedido_con_cliente_que_no_existe` | R14 (13/11) | ITP §5 | CUMPLIDO Y PROBADO | — |
| PY-52 | Regla 04: fecha nula o imposible | OBLIGATORIO | Ídem | `test_fecha_imposible`, `test_fecha_vacia` | R14 (13/11) | ITP §5 | CUMPLIDO Y PROBADO | — |
| PY-53 | Regla 05: cantidad nula, cero o negativa | OBLIGATORIO | Ídem | `test_cantidad_cero_negativa_o_texto` | R14 (13/11) | ITP §5 | CUMPLIDO Y PROBADO | — |
| PY-54 | Regla 06: precio no numérico o negativo | OBLIGATORIO | Ídem | `test_precio_negativo_y_no_numerico` | R14 (13/11) | ITP §5 | CUMPLIDO Y PROBADO | — |
| PY-55 | Regla 07: estado fuera del catálogo | OBLIGATORIO | Ídem; catálogo en `config.py` | `test_estado_fuera_del_catalogo_no_se_corrige` | R14 (13/11) | ITP §5 | CUMPLIDO Y PROBADO | — |
| PY-56 | Regla 08: talla no válida según el contrato | OBLIGATORIO | Ídem | `test_talla_fuera_de_rango`, `test_talla_distinta_de_la_de_su_sku` | R14 (13/11) | ITP §5 | CUMPLIDO Y PROBADO | [POR DECIDIR (los tres)]: el rango de tallas (`diccionario_datos.md`, punto 9); con los 100 modelos va de la 35 a la 46 |
| PY-57 | Regla 09: falta el cliente o el modelo | OBLIGATORIO | Ídem | `test_pedido_sin_cliente_y_linea_sin_modelo` | R14 (13/11) | ITP §5 | CUMPLIDO Y PROBADO | — |
| PY-58 | Regla 10: líneas duplicadas según una clave documentada | OBLIGATORIO | Ídem | `test_mismo_sku_dos_veces_en_un_pedido_no_se_borra`, `test_posible_pedido_repetido_no_se_borra` | R14 (13/11) | ITP §5 | CUMPLIDO Y PROBADO | — |
| PY-59 | Regla 11: stock negativo o duplicado | OBLIGATORIO | Ídem (clave: `sku`) | `test_stock_negativo`, `test_dos_skus_para_la_misma_variante` | R14 (13/11) | ITP §5 | CUMPLIDO Y PROBADO | — |
| PY-60 | Regla 12: fechas en conflicto o incoherencia comercial | OBLIGATORIO | Ídem | `test_total_que_no_cuadra`, `test_pedido_posterior_a_la_exportacion`, `test_importe_de_linea_mal_calculado` | R14 (13/11) | ITP §5 | CUMPLIDO Y PROBADO | — |
| PY-61 | Bloqueante, recuperable o advertencia, con justificación | OBLIGATORIO | `calidad.py`; `calidad_datos.md` («Gravedad y tratamiento») | `test_un_pedido_se_analiza_entero_o_no_se_analiza`, `test_solo_cabecera_es_advertencia` | R14 (13/11) | ITP §5 | CUMPLIDO Y PROBADO | — |
| PY-62 | No pasar nulos a cero ni borrar duplicados sin comprobarlo | OBLIGATORIO (prohibición) | `calidad.py` | `test_mismo_sku_dos_veces_en_un_pedido_no_se_borra`, `test_posible_pedido_repetido_no_se_borra` | R14 (13/11) | ITP §5 | CUMPLIDO Y PROBADO | — |
| PY-63 | Guardar `incidencias.csv` y `resumen_calidad.csv` | OBLIGATORIO | `calidad.py` | `test_csv_de_incidencias`, `test_csv_resumen` | R14, R15 (13/11) | ITP §5 | CUMPLIDO Y PROBADO | — |
| PY-64 | Filas de entrada, válidas y rechazadas, y porcentaje de calidad por tabla | OBLIGATORIO | Ídem | `test_csv_resumen` | R14, R15 (calidad 100 %) (13/11) | ITP §5 | CUMPLIDO Y PROBADO | — |
| PY-65 | Merge con cardinalidad, `validate=` e `indicator=` | OBLIGATORIO | `analiticas.cruzar` | `test_join_que_duplicaria_filas_se_detiene`, `test_clave_sin_pareja_se_detiene` | R14 (13/11) | ITP §6 | CUMPLIDO Y PROBADO | — |
| PY-66 | Vista por línea y vista por pedido | OBLIGATORIO | `df_lineas_enriquecidas`, `df_pedidos_unicos` | `test_una_fila_por_linea`, `test_una_fila_por_pedido` | R14 (13/11) | ITP §6 | CUMPLIDO Y PROBADO | — |
| PY-67 | Explicar por qué un pedido de 3 líneas no son 3 pedidos | OBLIGATORIO | `diccionario_datos.md` (vistas); `dashboard.md` | `test_tablas_kpis_y_graficos` (900 pedidos, no 1.777); `test_pedido_custom_de_40_pares_linea_a_linea` (9 líneas, 1 pedido) | R14; ITP §6 | ITP §6 | CUMPLIDO Y PROBADO | Prepararlo para la defensa individual (GD §5) |
| PY-68 | Contrastar pedidos, líneas e ingresos con al menos 3 consultas SQL | OBLIGATORIO | `conciliacion.py`; `entrada_acc/conciliacion_sql/` (P-A, P-B y P-C) | `test_cifras_que_coinciden`; `main.py --modo real`: P-A, P-B y P-C (21 cifras) y caso N (17 de 17) | R14, R15; A6 | ITP §9 | CUMPLIDO Y PROBADO | **Límite declarado:** la exportación se entrega como PRUEBA (`04_Python/entrada_acc/ORIGEN.txt`); no hay exportación REAL: repetir P-A, P-B, P-C y N con ella |
| PY-69 | Detectar cruces que multiplican filas, claves sin pareja y diferencias de importe | OBLIGATORIO | `analiticas.cruzar`, `conciliacion.py` | `test_join_que_duplicaria_filas_se_detiene`, `test_importe_que_no_coincide` | R14 (13/11) | ITP §6 | CUMPLIDO Y PROBADO | — |
| PY-70 | Al menos 10 variables derivadas documentadas, con unidad, nivel y disponibilidad | OBLIGATORIO | `analiticas.py`; `diccionario_datos.md` («Variables derivadas»: 18) | `test_variables_de_calendario`, `test_metricas_de_sus_lineas` | R14 (13/11) | ITP §6 | CUMPLIDO Y PROBADO | — |
| PY-71 | Sin fugas de información en las variables de predicción | OBLIGATORIO | `prediccion.py` | `test_solo_meses_anteriores_del_mismo_modelo`, `test_entradas_de_octubre_solo_del_pasado` | R14 (13/11) | ITP §6 | CUMPLIDO Y PROBADO | — |
| PY-72 | Al menos 12 KPIs con definición y fórmula | OBLIGATORIO | `kpis.py`, `kpis_y_graficos.md` | `test_doce_o_mas_kpis_calculados` (20, 3 de ellos NO CALCULABLES) | R14 (13/11) | ITP §8 | CUMPLIDO Y PROBADO | — |
| PY-73 | Distinguir pedidos creados, pendientes, confirmados, entregados y cancelados | OBLIGATORIO | `kpis.py`, `config.py` | `test_estados_de_los_pedidos`, `test_todos_los_estados_del_catalogo` | R14 (13/11) | ITP §8 | CUMPLIDO Y PROBADO | La exportación de prueba solo trae «pendiente» y «confirmado» |
| PY-74 | Pares e ingresos de pedidos confirmados o entregados | OBLIGATORIO | `analiticas.py` (tres criterios) | `test_tres_criterios`, `test_pendiente_no_es_confirmado` | R14 (13/11) | ITP §8 | CUMPLIDO Y PROBADO | [POR DECIDIR (los tres)]: el criterio de venta (`diccionario_datos.md`, punto 6) |
| PY-75 | Ticket medio y pares por pedido entre pedidos válidos, nunca entre líneas | OBLIGATORIO | `kpis.py` | `test_ticket_pares_y_precio_medio`, `test_sin_duplicar_pedidos_ni_importes` | R14 (13/11) | ITP §8 | CUMPLIDO Y PROBADO | — |
| PY-76 | Peso de Custom en pedidos, pares e importe | OBLIGATORIO | `kpis.py`, `analiticas.py` | `test_custom_y_mas_solicitados`, `test_custom_frente_a_estandar` | R14 (13/11) | ITP §8 | CUMPLIDO Y PROBADO | — |
| PY-77 | Top de modelos, tallas y clientes con acumulados | OBLIGATORIO | `analiticas.py` | `test_clases_por_acumulado`, `test_ventas_por_talla`, `test_clientes_actividad` | R14 (13/11) | ITP §8 | CUMPLIDO Y PROBADO | — |
| PY-78 | Evolución mensual o trimestral, con variación si hay periodo anterior | OBLIGATORIO | `analiticas.ventas_por_periodo` | `test_un_solo_mes_no_inventa_evolucion`, `test_dos_meses`, `test_con_dos_meses` | R14 (13/11) | ITP §8 | CUMPLIDO Y PROBADO | — |
| PY-79 | Concentración de Pareto: lo que acumula el 20 % principal | OBLIGATORIO | `kpis.py` (K15) | `test_el_que_cruza_el_80_es_a` | R14 (13/11) | ITP §8 | CUMPLIDO Y PROBADO | — |
| PY-80 | Rotación y cobertura orientativas sin inventar movimientos | OBLIGATORIO | `analiticas.py` | `test_cobertura_sin_demanda_reciente`, `test_cobertura_con_poco_historial` | R14 (13/11) | ITP §8 | CUMPLIDO Y PROBADO | Con la exportación de PRUEBA, la cobertura es NO CALCULABLE |
| PY-81 | Estados incluidos, momento del ingreso y redondeo en la configuración y en la memoria | OBLIGATORIO | `config.py` | — | `config.py`; ITP §8 | ITP §8 | PARCIAL | [POR DECIDIR (los tres)]: criterio de venta e IVA («pendiente de confirmar» en `config.py`) |
| PY-82 | Sin costes no se calcula margen ni beneficio | OBLIGATORIO (prohibición) | `analiticas.py` | `test_margen_no_calculable` | R14 (13/11) | ITP §8 | CUMPLIDO Y PROBADO | — |
| PY-83 | Análisis univariante y bivariante | OBLIGATORIO | `estadistica.py`, `visualizaciones.py` | `test_descriptivos_de_los_sinteticos` | R14 (13/11) | ITP §11 | CUMPLIDO Y PROBADO | — |
| PY-84 | Al menos 8 PNG de 8 tipos, con título, unidades, leyenda e interpretación | OBLIGATORIO | `visualizaciones.py` | `test_salen_los_diez_png`, `test_cada_grafico_es_de_un_tipo_distinto_o_responde_otra_pregunta` | R14, R15 (13/11) | ITP §11 | CUMPLIDO Y PROBADO | — |
| PY-85 | Media, mediana, moda, desviación, percentiles e IQR, y cuál representa mejor | OBLIGATORIO | `estadistica.py`, `estadistica.md` | `test_valores_conocidos`, `test_simetrica_y_moda` | R14 (13/11) | ITP §11 | CUMPLIDO Y PROBADO | — |
| PY-86 | Atípicos con una regla reproducible (IQR), sin borrarlos | OBLIGATORIO | `analiticas.anomalias_iqr` | `test_anomalia_detectada_y_no_borrada`, `test_el_recargo_custom_no_es_un_atipico` | R14 (13/11) | ITP §11 | CUMPLIDO Y PROBADO | — |
| PY-87 | Tres hipótesis, al menos dos contrastadas | OBLIGATORIO | `estadistica.py`, `estadistica.md` | `test_tres_hipotesis_completas`, `test_h1_con_sinteticos`, `test_h3_detecta_un_crecimiento_claro` | R14 (13/11) | ITP §11 | CUMPLIDO Y PROBADO | — |
| PY-88 | Bootstrap con intervalo del 95 % y semilla fija | OBLIGATORIO | `estadistica.py` | `test_reproducible_con_la_misma_semilla`, `test_el_intervalo_contiene_la_media` | R14 (13/11) | ITP §11 | CUMPLIDO Y PROBADO | — |
| PY-89 | Explicar supuestos, sesgos y limitaciones | OBLIGATORIO | `estadistica.md` («Supuestos, sesgos y limitaciones») | — | `estadistica.md`; ITP §16 | ITP §16 | CUMPLIDO (DOCUMENTADO) | — |
| PY-90 | Al menos una conclusión sobre lo que NO se puede afirmar | OBLIGATORIO | `estadistica.md` y `segmentacion_y_prediccion.md` («Lo que NO se puede afirmar») | `test_pocos_datos_evidencia_insuficiente` | R14 (13/11) | ITP §16 | CUMPLIDO Y PROBADO | — |
| PY-91 | RFM con ventas válidas, fecha de referencia y una fila por cliente | OBLIGATORIO | `segmentacion.py` | `test_recency_desde_la_fecha_de_corte`, `test_frequency_cuenta_pedidos_y_monetary_suma_importes` | R14 (13/11) | ITP §12 | CUMPLIDO Y PROBADO | — |
| PY-92 | Clientes sin compras en una categoría propia | OBLIGATORIO | Ídem | `test_clientes_sin_compras_validas` | R14 (13/11) | ITP §12 | CUMPLIDO Y PROBADO | — |
| PY-93 | Al menos 4 segmentos RFM con su umbral y utilidad | OBLIGATORIO | Ídem; `segmentacion_y_prediccion.md` | `test_al_menos_cuatro_segmentos_con_significado` (6) | R14 (13/11) | ITP §12 | CUMPLIDO Y PROBADO | — |
| PY-94 | KMeans con variables escaladas, k de 2 a 5 y silhouette | OBLIGATORIO | Ídem | `test_prueba_k_de_2_a_5_con_silhouette`, `test_variables_estandarizadas_y_sin_nulos` | R14 (13/11) | ITP §12 | CUMPLIDO Y PROBADO | — |
| PY-95 | Describir cada grupo y compararlo con RFM | OBLIGATORIO | Ídem | `test_clusters_describen_a_todos_los_compradores`, `test_comparacion_con_rfm` | R14 (13/11) | ITP §12 | CUMPLIDO Y PROBADO | — |
| PY-96 | Si los datos reales no bastan, usar los sintéticos y avisar | CONDICIONAL (se cumple) | Ídem | `test_pocos_clientes_no_calculable`, `test_no_se_fuerza_con_pocos_clientes` | R14 (13/11) | ITP §12 | CUMPLIDO Y PROBADO | — |
| PY-97 | Matrices modelo × mes y talla × modelo | OBLIGATORIO | `analiticas.matriz_modelo_mes`, `matriz_modelo_talla` | `test_matriz_modelo_talla`, `test_matriz_no_duplica_pares` | R14, R15 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-98 | Alertas de stock bajo con un umbral configurable | OBLIGATORIO | `config.py`, `analiticas.py`, `filtros.py` | `test_stock_bajo_ordenado`, `test_umbral_configurable` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-99 | Semanas de cobertura solo con demanda histórica | CONDICIONAL | `analiticas.py` | `test_cobertura_sin_demanda_reciente` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-100 | Clasificación ABC y decisiones de fabricación | OBLIGATORIO | `analiticas.clasificar_abc`; `kpis_y_graficos.md` («Clasificación ABC») | `test_clases_por_acumulado`, `test_empates_reciben_la_misma_clase` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-101 | No tratar el stock de una fecha de corte como una serie histórica | OBLIGATORIO (prohibición) | `app_dashboard.py` (aviso de stock «foto»), `dashboard.md` | — | A2 (9/11) | ITP §7 | CUMPLIDO SIN PRUEBA DEL 13/11 | Ninguna prueba automática lo comprueba; el aviso sale en las capturas del 9/11 |
| PY-102 | Predictor de pares por modelo y mes (con sintéticos si no hay histórico) | OBLIGATORIO | `prediccion.py` | `test_con_los_sinteticos_si_se_calcula`, `test_once_meses_no_calculable` | R14 (13/11) | ITP §13 | CUMPLIDO Y PROBADO | — |
| PY-103 | Objetivo y 4 predictores anteriores al mes | OBLIGATORIO | Ídem | `test_mes_del_ano_y_modelo_codificados`, `test_solo_meses_anteriores_del_mismo_modelo` | R14 (13/11) | ITP §13 | CUMPLIDO Y PROBADO | — |
| PY-104 | Baseline: el mes anterior | OBLIGATORIO | Ídem | `test_baseline_es_el_mes_anterior` | R14 (13/11) | ITP §13 | CUMPLIDO Y PROBADO | — |
| PY-105 | Al menos una regresión de scikit-learn, justificada | OBLIGATORIO | Ídem; `segmentacion_y_prediccion.md` («Los dos métodos») | `test_comparacion_de_metodos` | R14 (13/11) | ITP §13 | CUMPLIDO Y PROBADO | — |
| PY-106 | Separación por fecha, reservando al menos los últimos 3 meses | OBLIGATORIO | Ídem | `test_periodos_exactos`, `test_agosto_septiembre_octubre_no_entrenan` | R14 (13/11) | ITP §13 | CUMPLIDO Y PROBADO | — |
| PY-107 | Comparar con MAE y RMSE | OBLIGATORIO | Ídem | `test_mae_y_rmse_con_valores_conocidos` | R14 (13/11) | ITP §13 | CUMPLIDO Y PROBADO | — |
| PY-108 | Tabla por modelo, gráfico real frente a predicción y análisis de errores | OBLIGATORIO | Ídem; gráfico 11; `segmentacion_y_prediccion.md` («Análisis de errores») | `test_errores_por_modelo` | R14 (13/11) | ITP §13 | CUMPLIDO Y PROBADO | — |
| PY-109 | Si no mejora al baseline, decirlo y explicar por qué | OBLIGATORIO | Ídem | `test_si_no_mejora_lo_dice` | R14 (13/11) | ITP §13 | CUMPLIDO Y PROBADO | — |
| PY-110 | Informe ejecutivo con 5 decisiones concretas y priorizadas, cada una con su indicador | OBLIGATORIO | `informe.py`, `informe_ejecutivo.md` | `test_prioridad_impacto_y_sustento`, `test_sin_datos_la_urgencia_es_baja`: las 5 decisiones con un criterio de prioridad escrito (urgencia y número) y la tabla y el gráfico que las sustentan; `informe_ejecutivo.csv` con 4 columnas nuevas | R14, R15 | ITP §14.4; `informe_ejecutivo.md` | CUMPLIDO Y PROBADO | — |
| PY-111 | En cada recomendación: impacto esperado, limitación y procedencia | OBLIGATORIO | Ídem | `test_prioridad_impacto_y_sustento`: cada recomendación con su impacto esperado (cifra), limitación y procedencia | R14, R15 | ITP §14.4; `informe_ejecutivo.md` | CUMPLIDO Y PROBADO | — |
| PY-112 | Separar observación, interpretación y propuesta | OBLIGATORIO | Ídem (evidencia, interpretación, decisión y limitación) | `test_cinco_conclusiones_con_procedencia` | R14 (13/11) | ITP §14; `informe_ejecutivo.md` | CUMPLIDO Y PROBADO | — |
| PY-113 | `main.py` con modo, carpetas y todas las fases | OBLIGATORIO | `main.py` | Real, sintético y sintético con errores | R15 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-114 | Segunda entrada: `streamlit run app_dashboard.py` | OBLIGATORIO | `app_dashboard.py` | `AppTest` (`test_dashboard.py`) | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-115 | Las mismas funciones; nunca dos fórmulas para un KPI | OBLIGATORIO (prohibición) | `filtros.py`, `kpis.py` | `test_cuatro_filtros_combinados_cambian_los_kpis` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-116 | Al menos 4 filtros combinables en el dashboard y en el motor | OBLIGATORIO | `filtros.py` (6 filtros) | `test_cuatro_filtros_combinados` (motor) y `test_cuatro_filtros_combinados_cambian_los_kpis` (AppTest) | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-117 | Un filtro vacío no restringe; cada cifra corresponde al subconjunto y dice su denominador | OBLIGATORIO | `filtros.py` | `test_sin_filtros_no_restringe_nada`, `test_kpis_filtrados_coherentes` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-118 | Carpetas de salida, registro de eventos y errores comprensibles | OBLIGATORIO | `registro.py`, `main.py` | `test_una_fila_por_ciclo_en_un_solo_archivo`, `test_ejecucion_correcta` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-119 | Mostrar la última comprobación, la última actualización válida, las filas y el estado de calidad | OBLIGATORIO | `app_dashboard.py` (cabecera con `st.metric`) | La cabecera en Edge: «Estado», «Última comprobación», «Última actualización válida» y «Filas válidas» en 4 momentos (R25); `test_relee_los_csv_cada_60_segundos` (R14) | R25 (`caso_k_*.png`, `caso_k_registro.txt`); R14 | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-120 | Un fallo nunca enseña cifras viejas como si fueran nuevas | OBLIGATORIO (prohibición) | `actualizacion.py` | `test_csv_defectuoso_no_publica_cifras`, `test_csv_ausente_R4_y_recuperacion` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-121 | Dependencias declaradas, configuración fuera del código, rutas relativas y semilla | OBLIGATORIO | `requirements.txt`, `config.py` | Las 265 pruebas pasan en una copia en otra carpeta | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-122 | No editar a mano los resultados publicados | OBLIGATORIO (prohibición) | Salidas generadas por el código | Las 93 salidas se regeneran idénticas | R15 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-123 | Al menos 12 pruebas automatizadas | OBLIGATORIO | `tests/` | 265 | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-124 | Pruebas de carga: ruta inexistente, CSV vacío, columna ausente y fecha corrupta | OBLIGATORIO | `tests/test_pipeline.py` | `test_csv_ausente`, `test_csv_vacio`, `test_columna_obligatoria_ausente`, `test_fecha_y_logico_mal_formados` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-125 | Pruebas de integridad: huérfano, duplicado, cardinalidad y cantidad negativa | OBLIGATORIO | `tests/` | `test_linea_huerfana`, `test_id_duplicado`, `test_join_que_duplicaria_filas_se_detiene`, `test_cantidad_cero_negativa_o_texto` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-126 | Pruebas de cálculo: cancelados, pedido de varias líneas, importe y ticket | OBLIGATORIO | `tests/` | `test_pares_solicitados_sin_cancelados`, `test_metricas_de_sus_lineas`, `test_sin_duplicar_pedidos_ni_importes` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-127 | Prueba de reproducibilidad: la misma semilla da lo mismo | OBLIGATORIO | `tests/` | `test_misma_semilla_mismos_datos`, `test_resultados_reproducibles` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-128 | Pruebas de aprendizaje automático y tiempo: sin meses de prueba ni datos futuros | OBLIGATORIO | `tests/test_prediccion.py` | `test_agosto_septiembre_octubre_no_entrenan`, `test_el_mes_objetivo_no_es_una_entrada` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-129 | Dashboard para dirección, producción, almacén y comercial; todo sale de funciones pandas | OBLIGATORIO | `app_dashboard.py` | `test_todas_las_pestanas_sin_errores` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-130 | Arranca en modo REAL, con el origen y la fecha de corte visibles | OBLIGATORIO | `app_dashboard.py` | `test_arranca_con_la_exportacion_de_acceso_a_datos` | R14 (13/11) | ITP §14 | PARCIAL | Arranca con la exportación de ACC, rotulada PRUEBA. **Límite declarado:** la exportación se entrega como PRUEBA (`04_Python/entrada_acc/ORIGEN.txt`); no hay exportación REAL |
| PY-131 | Recalcular automáticamente cada 60 s con la sesión abierta | OBLIGATORIO | `actualizacion.ciclo`, `app_dashboard.panel` | `test_relee_los_csv_cada_60_segundos` (R14); en Edge, tres ciclos de 60 s sin tocar el navegador (R25) | R14; R25 | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-132 | Botón «Actualizar ahora» | OBLIGATORIO | `app_dashboard.py` | `test_boton_actualizar_ahora` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-133 | Documentar que un dato nuevo en PostgreSQL no llega sin reexportar | OBLIGATORIO (documentar) | `dashboard.md` («Python solo lee CSV…»), `README.md` | — | `dashboard.md`, `README.md` («Los datos nuevos de PostgreSQL solo llegan…»); ITP §14 | ITP §14 | CUMPLIDO (DOCUMENTADO) | — |
| PY-134 | `st.fragment(run_every="60s")` | OBLIGATORIO | `app_dashboard.panel` | `test_relee_los_csv_cada_60_segundos` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-135 | Sin `time.sleep(60)`, bucles ni recargas del navegador | OBLIGATORIO (prohibición) | `app_dashboard.py` (código revisado el 12/11: sin `time.sleep` ni `while True`) | `AppTest` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-136 | El refresco mantiene los filtros y la pestaña, no duplica nada y no escribe en el origen | OBLIGATORIO | `app_dashboard.py`, `actualizacion.py` | `test_filtros_y_pestana_se_mantienen_al_refrescar` (sigue en Productos, con cliente 1 y talla 40, y la tabla ABC pasa de 1 a 2 pares); `test_no_escribe_en_la_entrada` | R14 | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-137 | Todos los KPIs de la misma ejecución y versión de los datos | OBLIGATORIO | `actualizacion.ciclo` (publica uno o ninguno) | `test_primer_ciclo_publica`, `test_clave_huerfana_no_publica` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-138 | Comprobación, actualización válida, filas, «ACC · REAL», tiempo y 4 estados | OBLIGATORIO | `app_dashboard.py` | Correcto y Sin cambios (`test_relee…`), Error de carga (`test_csv_defectuoso…`), Datos inválidos (`test_bloqueo_por_calidad_sin_cifras`) | R14 (13/11) | ITP §14 | PARCIAL | La procedencia sale «PRUEBA». **Límite declarado:** la exportación se entrega como PRUEBA (`04_Python/entrada_acc/ORIGEN.txt`); no hay exportación REAL |
| PY-139 | Ante un CSV que falta, incompleto, con huérfanos o mal formado: avisar, registrar y no publicar cálculos parciales | OBLIGATORIO | `actualizacion.py` | `test_csv_ausente_R4_y_recuperacion`, `test_clave_huerfana_no_publica`, `test_avisos_de_exportacion_antigua_o_incompleta` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-141 | Cada minuto se vuelve a ejecutar aunque no cambie nada, sin inventar cambios | OBLIGATORIO | Ídem | `test_sin_cambios_R5`, `test_reexportar_lo_mismo_no_es_un_cambio` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-142 | Al menos 10 DataFrames más las 2 vistas base | OBLIGATORIO | `analiticas.calcular_tablas` (14) | `test_tablas.py` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-143 | Cada función devuelve un DataFrame verificable y documenta sus columnas | OBLIGATORIO | `analiticas.py`; `kpis_y_graficos.md` («DataFrames») | `test_tablas.py` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-144 | DF 01 · Pedidos únicos | OBLIGATORIO | `analiticas.py` | `test_una_fila_por_pedido`, `test_metricas_de_sus_lineas` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-145 | DF 02 · Ventas por periodo | OBLIGATORIO | Ídem | `test_un_solo_mes_no_inventa_evolucion`, `test_dos_meses`, `test_mes_sin_ventas_en_medio_es_cero` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-146 | DF 03 · Modelos ABC y Pareto | OBLIGATORIO | Ídem | `test_clases_por_acumulado`, `test_modelo_sin_demanda_es_c_y_no_desaparece` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-147 | DF 04 · Matriz modelo × talla | OBLIGATORIO | Ídem | `test_matriz_modelo_talla`, `test_matriz_no_duplica_pares` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-148 | DF 05 · Custom frente a estándar | OBLIGATORIO | Ídem | `test_custom_frente_a_estandar` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-149 | DF 06 · Clientes RFM | OBLIGATORIO | `segmentacion.py` | `test_segmentacion.py` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-150 | DF 07 · Cohortes, avisando si la muestra no basta | OBLIGATORIO | `analiticas.py` | `test_cohortes` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | Con la exportación de PRUEBA, NO CALCULABLE |
| PY-151 | DF 08 · Stock y cobertura (sin demanda, «N/D») | OBLIGATORIO | Ídem | `test_cobertura_sin_demanda_reciente`, `test_cobertura_con_demanda` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-152 | DF 09 · Calidad e incidencias | OBLIGATORIO | `calidad.py` | `test_nulos_por_columna` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-153 | DF 10 · Anomalías | OBLIGATORIO | `analiticas.anomalias_iqr` | `test_anomalias_con_muestra_pequena`, `test_anomalia_detectada_y_no_borrada` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-154 | DF 11 · Margen solo con un coste fiable; si no, «Coste no disponible» | CONDICIONAL | `analiticas.py` | `test_margen_no_calculable` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-155 | DF 12 · Reconciliación con SQL | OBLIGATORIO | `conciliacion.py` | `test_cifras_que_coinciden`, `test_kpis_coinciden_con_postgresql` | R14, R15 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-156 | Los diez operativos más la reconciliación | OBLIGATORIO | `analiticas.py`, `conciliacion.py` | `test_tablas.py`, `test_kpis.py` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-157 | Si faltan datos, el DataFrame existe como «NO CALCULABLE», nunca con ceros | OBLIGATORIO | `analiticas.py`, `kpis.py` | `test_no_calculables`, `test_once_meses_no_calculable` | R14 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-159 | Metadatos de cada DataFrame: fecha de corte, reglas, filtros, filas de origen y función que lo generó | OBLIGATORIO | `pipeline.guardar_salida` (origen y ejecución), `pipeline.csv_descarga` (más filtros) | `test_metadatos_de_cada_dataframe`, `test_metadatos_tambien_con_datos_bloqueados`, `test_descarga_con_sus_metadatos`, `test_el_stock_solo_lleva_los_filtros_de_modelo_y_talla`, `test_cada_dataframe_dice_una_funcion_que_existe`; `metadatos_dataframes.csv` en los tres modos | R14, R15 | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-160 | No sacar indicadores de un Excel ni copiarlos del panel de AD | OBLIGATORIO (prohibición) | Todo se calcula en código | Las 93 salidas se regeneran | R15 (13/11) | ITP §7 | CUMPLIDO Y PROBADO | — |
| PY-161 | Al menos 5 pestañas navegables | OBLIGATORIO | `app_dashboard.py` | `test_seis_pestanas` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | [DUDA PARA EL PROFESOR (D11)]: si la sexta es obligatoria |
| PY-162 | Pestaña Dirección: 4 o más KPI, comparación con el periodo anterior y estado del refresco | OBLIGATORIO | `app_dashboard.py` | En Edge, la pestaña Dirección con 8 tarjetas y el estado del refresco (R25); `test_filtrado_cruzado_R6` lee sus tarjetas (R14) | R25; R14; A2 (9/11: la comparación con el periodo anterior) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-163 | Pestaña Producto y ventas: ABC, matriz talla-modelo, Custom y ticket por tipo | OBLIGATORIO | Ídem | `test_filtrado_cruzado_R6` abre Productos y cuadra la tabla de su gráfico de tallas, la ABC y la matriz con pandas (R14); el resto, en las capturas del 9/11 | R14; A2 (9/11) | ITP §14 | CUMPLIDO SIN PRUEBA DEL 13/11 | El contenido completo solo en las capturas del 9/11 |
| PY-164 | Pestaña Clientes: ranking, RFM y cohortes si hay histórico | OBLIGATORIO | Ídem | `test_filtrado_cruzado_R6` abre Clientes (R14); `test_todas_las_pestanas_sin_errores` | R14; A2 (9/11) | ITP §14 | CUMPLIDO SIN PRUEBA DEL 13/11 | El contenido completo solo en las capturas del 9/11 |
| PY-165 | Pestaña Almacén: demanda de 28 días, stock, alertas, cobertura y aviso de «foto» | OBLIGATORIO | Ídem | Ídem | R14 (abre sin errores); A2 (9/11) | ITP §14 | CUMPLIDO SIN PRUEBA DEL 13/11 | El contenido solo en las capturas del 9/11 |
| PY-166 | Pestaña Calidad y auditoría: filas, reglas, huérfanos, conciliación y última ejecución | OBLIGATORIO | Ídem | Ídem | R14 (abre sin errores); A2 (9/11) | ITP §14 | CUMPLIDO SIN PRUEBA DEL 13/11 | El contenido solo en las capturas del 9/11. Desde el 13/11 enseña también el contraste del caso N |
| PY-167 | Pestaña Modelos predictivos, solo con una evaluación honesta | CONDICIONAL | Ídem (laboratorio con datos sintéticos) | `test_seis_pestanas` | R14 (13/11); A2 (9/11) | ITP §14 | CUMPLIDO SIN PRUEBA DEL 13/11 | [DUDA PARA EL PROFESOR (D11)]: si se pueden enseñar predicciones sintéticas en esta pestaña |
| PY-168 | Filtros combinables y persistentes: periodo, modelo, talla y tipo; estado y cliente si el esquema lo permite | OBLIGATORIO | `filtros.py`, `app_dashboard.py` (6 filtros) | Seis filtros (periodo, modelo, talla, tipo, estado y **cliente**): `test_cliente_es_del_pedido`, `test_filtro_de_cliente_combinado_y_restablecer`; persistentes: `test_filtros_y_pestana_se_mantienen_al_refrescar` | R14 | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-169 | Acción «Restablecer filtros» | OBLIGATORIO | `app_dashboard.restablecer_filtros` | `test_filtro_de_cliente_combinado_y_restablecer` y `test_cuatro_filtros_combinados_cambian_los_kpis` (pulsan «Restablecer») | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-170 | Explicar si un filtro reduce el denominador de cada KPI | OBLIGATORIO | `app_dashboard.py` (`denominador`) | En Edge, el texto del denominador («Sin filtros: los 12 pedidos registrados de la exportación») junto a las tarjetas (R25) | R25; A2 (9/11, con filtros) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-171 | Al menos 8 visualizaciones: serie temporal, barras, mapa de calor, distribución y ranking acumulado | OBLIGATORIO | `app_dashboard.py`, `visualizaciones.py` | — | A2 (9/11) | ITP §14 | CUMPLIDO SIN PRUEBA DEL 13/11 | Ninguna prueba automática las cuenta |
| PY-172 | Ver la tabla de datos de cada gráfico | OBLIGATORIO | `app_dashboard.py` («Ver los datos del gráfico») | `test_filtrado_cruzado_R6` lee las tablas de los gráficos de evolución, tallas y meses y las cuadra con pandas | R14; A2 (9/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-173 | Al menos 5 descargas CSV en UTF-8, filtradas y sin datos personales | OBLIGATORIO | `pipeline.csv_descarga` | `test_al_menos_cinco_descargas`, `test_csv_utf8_con_cabecera_origen_y_filtros`, `test_sin_datos_personales`, `test_descarga_con_sus_metadatos` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-174 | Cada gráfica con título, unidad, periodo, leyenda y explicación | OBLIGATORIO | `visualizaciones.py` (código revisado el 12/11) | `test_salen_los_diez_png` (solo que se generan) | R14 (13/11) | ITP §14 | CUMPLIDO SIN PRUEBA DEL 13/11 | Ninguna prueba comprueba títulos, unidades ni la explicación |
| PY-175 | Importes con moneda y distinguiendo neto y bruto; pares y pedidos sin mezclar | OBLIGATORIO | `config.py` (`IVA = "pendiente de confirmar"`) | — | Lectura del texto (13/11) | ITP §14 | PARCIAL | [POR DECIDIR (los tres)]: si los importes son netos o brutos. [DUDA PARA EL PROFESOR (D11)] |
| PY-177 | El pipeline no depende de Streamlit y se puede probar | OBLIGATORIO | `pipeline.py`, `analiticas.py` (no importan Streamlit) | 265 pruebas | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-178 | Paso 1: cada 60 s, comprobar los CSV y anotar la hora | OBLIGATORIO | `actualizacion.py` | `test_primer_ciclo_publica`, `test_avisos_de_exportacion_antigua_o_incompleta` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-179 | Paso 2: leer y validar sin editar los CSV | OBLIGATORIO | Ídem | `test_no_escribe_en_la_entrada` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-180 | Paso 3: recalcular todo con una sola versión y sin caché | OBLIGATORIO | Ídem | `test_sin_cambios_R5` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-181 | Paso 4: publicar un resultado único o no publicar nada | OBLIGATORIO | Ídem | `test_clave_huerfana_no_publica` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-182 | Paso 5: log de cada refresco (fecha, origen, filas, duración, estado y anomalías) | OBLIGATORIO | `registro.py` (`logs/registro_eventos.csv`) | `test_una_fila_por_ciclo_en_un_solo_archivo`, `test_detalle_en_una_linea` | R14 (13/11) | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-183 | R1 · ACC inserta un pedido de 2 líneas y exporta con el dashboard abierto | OBLIGATORIO | `actualizacion.py` | `test_pedido_nuevo_R1` (CSV de prueba); SO024 PROVISIONAL exportado con el 16 y leído por `main.py` como un solo pedido (R23) | R14; R23; A2 (10/11) | ITP §14 | PARCIAL | **Límite declarado:** la exportación se entrega como PRUEBA (`04_Python/entrada_acc/ORIGEN.txt`); no hay exportación REAL y un alta en ACC con el dashboard abierto, con capturas antes y después |
| PY-184 | R2 · ACC cancela un pedido y vuelve a exportar | OBLIGATORIO | Ídem | `test_cancelacion_R2` (CSV inventados) | R14 (13/11) | ITP §14 | PARCIAL | **Límite declarado:** la exportación se entrega como PRUEBA (`04_Python/entrada_acc/ORIGEN.txt`); no hay exportación REAL: una cancelación real en ACC y su exportación |
| PY-185 | R3 · ACC exporta un stock nuevo | OBLIGATORIO | Ídem | `test_cambio_de_stock_R3` (CSV inventados) | R14 (13/11) | ITP §14 | PARCIAL | **Límite declarado:** la exportación se entrega como PRUEBA (`04_Python/entrada_acc/ORIGEN.txt`); no hay exportación REAL: un cambio real de stock y su exportación |
| PY-186 | R4 · CSV sin columna clave o con huérfanos | OBLIGATORIO | Ídem | `test_csv_ausente_R4_y_recuperacion`, `test_csv_corrupto`; en Edge, `refresco_3*` (10/11) | R14 (13/11); A2 | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-187 | R5 · Dos o más ciclos sin cambios | OBLIGATORIO | Ídem | `test_sin_cambios_R5`; en Edge, `refresco_1` (10/11) | R14 (13/11); A2 | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-188 | R6 · Filtrado cruzado: tarjetas, gráficos, tablas exportadas y su suma coinciden en varias vistas | OBLIGATORIO | `filtros.py` | `test_filtrado_cruzado_R6`: mismo periodo, modelo y talla en Dirección, Productos y Clientes; tarjetas, tablas de los gráficos y CSV descargados (los del propio botón) cuadran con pandas y tienen la misma `ejecucion` y `fecha_corte` | R14 | ITP §14 | CUMPLIDO Y PROBADO | — |
| PY-189 | Aceptación: distinguir el recálculo de 60 s de la llegada de datos; antes y después; log | OBLIGATORIO | `dashboard.md` | — | `dashboard.md`; ITP §14; R25 | ITP §14 | PARCIAL | **Límite declarado:** la exportación se entrega como PRUEBA (`04_Python/entrada_acc/ORIGEN.txt`); no hay exportación REAL: el antes y después de una exportación real (PY-216) |
| PY-190 | Cada CSV, imagen o informe dice su origen, su momento y sus filtros | OBLIGATORIO | `pipeline.guardar_salida`; pie de los PNG | `test_csv_utf8_con_cabecera_origen_y_filtros`, `test_todo_etiquetado_como_sintetico` | R14 (13/11) | ITP §15 | CUMPLIDO Y PROBADO | — |
| PY-191 | DataFrames generados en código | OBLIGATORIO | `analiticas.py` | 93 salidas | R15 (13/11) | ITP §15 | CUMPLIDO Y PROBADO | — |
| PY-192 | Al menos 10 CSV de resultados, separados por origen | OBLIGATORIO | `outputs/<modo>/` | Más de 30 CSV por modo | R15 (13/11) | ITP §15 | CUMPLIDO Y PROBADO | [DUDA PARA EL PROFESOR (D11)]: si son 10 o 12 y qué es el de «auditoría» |
| PY-193 | Al menos 8 PNG | OBLIGATORIO | `visualizaciones.py` | `test_salen_los_diez_png`; 22 PNG | R14, R15 (13/11) | ITP §15 | CUMPLIDO Y PROBADO | — |
| PY-194 | Dos informes: técnico y ejecutivo | OBLIGATORIO | `04_Python/memoria/INFORME_TECNICO_PYTHON.md`, `informe_ejecutivo.md` | — | `04_Python/memoria/INFORME_TECNICO_PYTHON.md` (método, pruebas, métricas y sesgos) e `informe_ejecutivo.md` | ITP §15 | CUMPLIDO (DOCUMENTADO) | [DUDA PARA EL PROFESOR (D11)]: si el informe técnico es la memoria técnica |
| PY-195 | Proyecto modular | OBLIGATORIO | Estructura de `04_Python/` | 265 pruebas | R14 (13/11) | ITP §15 | CUMPLIDO Y PROBADO | — |
| PY-196 | Un dashboard: refresco de 60 s, vistas, filtros, logs y 5 descargas | OBLIGATORIO | `app_dashboard.py` | `test_dashboard.py` | R14 (13/11) | ITP §15 | CUMPLIDO Y PROBADO | — |
| PY-197 | Caso A · Pedido Custom de 40 pares en varias tallas: correspondencia línea a línea y total en los KPIs | OBLIGATORIO | `analiticas.py`, `kpis.py` | `test_pedido_custom_de_40_pares_linea_a_linea`: cada línea, un solo pedido de 40 pares, la matriz y los KPIs (+1 pedido, +40 pares y su importe); CUSTOM-40 en la exportación (R15); SO024 PROVISIONAL como un pedido de 9 líneas (R23) | R14, R15, R23; tabla A–O en ITP §15.3 | ITP §15.3 | CUMPLIDO Y PROBADO | Captura en la demostración (MD) |
| PY-198 | Caso B · Cancelado y pendiente: qué entra en ventas y qué solo en actividad | OBLIGATORIO | `analiticas.py`; `calidad_datos.md` (caso B) | `test_tres_criterios`, `test_pendiente_no_es_confirmado`, `test_cancelacion_R2` | R14 (13/11) | ITP §15.3 | CUMPLIDO Y PROBADO | — |
| PY-199 | Caso C · Alta desde Java → exportación → Python → los indicadores cambian | OBLIGATORIO | Cadena SO024 | Métodos Java de «Nuevo pedido» → 16 → `main.py`: SO024 sale como un solo pedido de 9 líneas, 40 pares y 3.996 € | R23 | ITP §15.3 | PROVISIONAL | Falta evidencia desde la ventana Java y con indicadores antes/después. No exige SO024; no hay prueba de S00005 en Python. |
| PY-200 | Caso D · Huérfano, fecha mala y duplicado: tres alertas sin tocar el original | OBLIGATORIO | `calidad.py` | `test_con_errores_se_detecta_cada_regla`, `test_no_modifica_el_original` | R14 (13/11) | ITP §15.3 | CUMPLIDO Y PROBADO | — |
| PY-201 | Caso E · Al menos 3 cifras de SQL conciliadas con pandas | OBLIGATORIO | `conciliacion.py` | 21 cifras de P-A, P-B y P-C; 17 de 17 del caso N (R15) | R14, R15; A6 | ITP §15.3 | CUMPLIDO Y PROBADO | — |
| PY-202 | Caso F · RFM de un cliente con varios pedidos, sin contar líneas | OBLIGATORIO | `segmentacion.py` | `test_frequency_cuenta_pedidos_y_monetary_suma_importes` | R14 (13/11) | ITP §15.3 | CUMPLIDO Y PROBADO | — |
| PY-203 | Caso G · Misma semilla, mismos resultados | OBLIGATORIO | `generador_datos.py` | `test_misma_semilla_mismos_datos`, `test_reproducible` | R14 (13/11) | ITP §15.3 | CUMPLIDO Y PROBADO | — |
| PY-204 | Caso H · Otro intervalo de fechas: tabla, gráfico y totales coinciden | OBLIGATORIO | `filtros.py` | `test_periodo_incluye_el_dia_final`, `test_kpis_filtrados_coherentes` | R14 (13/11) | ITP §15.3 | CUMPLIDO Y PROBADO | — |
| PY-205 | Caso I · Entrenamiento frente a meses reservados, comparado con el baseline | OBLIGATORIO | `prediccion.py` | `test_agosto_septiembre_octubre_no_entrenan`, `test_comparacion_de_metodos` | R14 (13/11) | ITP §15.3 | CUMPLIDO Y PROBADO | — |
| PY-206 | Caso J · Datos insuficientes: comportamiento controlado y aviso | OBLIGATORIO | `segmentacion.py`, `prediccion.py` | `test_pocos_clientes_no_calculable`, `test_once_meses_no_calculable`, `test_sin_datos_suficientes_lo_dice` | R14 (13/11) | ITP §15.3 | CUMPLIDO Y PROBADO | — |
| PY-207 | Caso K · Dashboard abierto durante 3 ciclos de 60 s | OBLIGATORIO | `actualizacion.py`, `registro.py` | El dashboard abierto en Edge tres ciclos de 60 s sin tocarlo: cuatro horas de comprobación distintas, «Sin cambios» en los tres, las mismas cifras y el registro con la carga inicial y 3 comprobaciones automáticas (4 PASS) | R25 | ITP §14.3 y §15.3 | CUMPLIDO Y PROBADO | Con la exportación de PRUEBA |
| PY-208 | Caso L · Exportar un pedido nuevo desde ACC durante la sesión | OBLIGATORIO | Ídem | En Edge, R1 con los CSV editados a mano (10/11) | A2 | ITP §15.3 | PARCIAL | **Límite declarado:** la exportación se entrega como PRUEBA (`04_Python/entrada_acc/ORIGEN.txt`); no hay exportación REAL (de un pedido acreditado, sin exigir el identificador SO024) durante la sesión, con el 16 |
| PY-209 | Caso M · Exportación defectuosa: alerta, último resultado válido marcado como obsoleto y recuperación | OBLIGATORIO | `actualizacion.py` | `test_csv_ausente_R4_y_recuperacion`; en Edge, `refresco_3`, `3b` y `4` (10/11) | R14 (13/11); A2 | ITP §15.3 | CUMPLIDO Y PROBADO | — |
| PY-210 | Caso N · Por SQL: ingresos de un mes, matriz talla × modelo y clientes únicos | OBLIGATORIO | — | N-1 (ingresos de un mes), N-2 (matriz talla × modelo) y N-3 (clientes únicos) en `12_consultas_panel.sql`; `PruebasCasoN` (4 pruebas); `main.py --modo real`: «caso N: 17 de 17 cifras coinciden con SQL» | R14, R15; `entrada_acc/conciliacion_sql/N-*.csv`; `conciliacion_sql.md` | ITP §9 y §15.3; `conciliacion_sql.md` | CUMPLIDO Y PROBADO | Repetirlo con la exportación REAL |
| PY-211 | Caso O · Descargar un DataFrame filtrado, cuadrarlo con el gráfico y que lo sintético no salga como «real» | OBLIGATORIO | `pipeline.csv_descarga` | `test_csv_utf8_con_cabecera_origen_y_filtros`, `test_todo_etiquetado_como_sintetico`; en Edge, descarga filtrada (9/11) | R14 (13/11); A2 | ITP §15.3 | CUMPLIDO Y PROBADO | — |
| PY-212 | Carpeta ejecutable y autocontenida, sin credenciales | OBLIGATORIO | `04_Python/` | Las pruebas pasan en una copia en otra carpeta | R14 (13/11) | ITP §2; README Python | CUMPLIDO Y PROBADO | — |
| PY-214 | README con instalación, ejecución, importación, contrato, filtros, diccionario, modos, dependencias, 60 s, datos nuevos y recuperación | OBLIGATORIO | `README.md` | — | Lectura del texto (13/11) | README Python | PARCIAL | [PENDIENTE (Omar): llevar al README la prueba de datos nuevos y la recuperación paso a paso] (ahora están en `dashboard.md` y en ITP §14) |
| PY-215 | Memoria técnica (diccionario, ETL, reglas, pandas, fórmulas, conciliación, hipótesis, clustering, predicción, dashboard, refresco, pruebas y limitaciones) | OBLIGATORIO | `04_Python/memoria/INFORME_TECNICO_PYTHON.md` y los .md de `04_Python/` | — | `04_Python/memoria/INFORME_TECNICO_PYTHON.md` (diccionario, ETL, reglas, DataFrames, fórmulas, conciliación, hipótesis, clustering, predicción, dashboard, refresco, pruebas y limitaciones) y MEM | ITP; MEM | CUMPLIDO (DOCUMENTADO) | [DUDA PARA EL PROFESOR (D11)]: informe técnico frente a memoria técnica |
| PY-216 | Capturas antes y después de incorporar datos reales nuevos | OBLIGATORIO | `evidencias/dashboard/refresco_1_sin_cambios.png` y `refresco_2_pedido_nuevo.png` | Edge (10/11), datos de PRUEBA | A2 (`refresco_1_sin_cambios.png` y `refresco_2_pedido_nuevo.png`, 10/11, datos de PRUEBA) | ITP §14 | PARCIAL | **Límite declarado:** la exportación se entrega como PRUEBA (`04_Python/entrada_acc/ORIGEN.txt`); no hay exportación REAL: capturas antes y después con ella |
| PY-217 | Sin indicadores fijos, sintéticos como reales ni gráficos desconectados | OBLIGATORIO (aceptación) | Todo | `test_todo_etiquetado_como_sintetico`, `test_datos_de_prueba_se_dicen_de_prueba` | R14 (13/11) | ITP §15 y §16 | CUMPLIDO Y PROBADO | **PUEDE IMPEDIR APROBAR.** **Condición de aceptación** («No se admiten…»): se cumple |
| PY-218 | Sin fechas futuras, ID como magnitudes ni líneas contadas como pedidos | OBLIGATORIO (aceptación) | Todo | `test_el_mes_objetivo_no_es_una_entrada`, `test_identificadores_que_no_se_confunden`, `test_una_fila_por_pedido` | R14 (13/11) | ITP §15 y §16 | CUMPLIDO Y PROBADO | **PUEDE IMPEDIR APROBAR.** **Condición de aceptación** («No se evaluarán como válidas…»): se cumple |
| PY-219 | Instalar las dependencias y ejecutarlo todo desde cero | OBLIGATORIO | `requirements.txt`; `README.md` («Instalación») | Siguiendo el manual en un clon nuevo: entorno virtual nuevo, `pip install -r requirements.txt`, `main.py` en los tres modos, el generador y `streamlit run` (R24); las 265 pruebas en una copia (R14) | R24; R14 | MI §6; README Python («Instalación») | CUMPLIDO Y PROBADO | — |
| PY-220 | Con la aplicación abierta, un CSV válido se ve en el siguiente ciclo y uno inválido da una alerta | OBLIGATORIO | `actualizacion.py` | `test_relee_los_csv_cada_60_segundos`, `test_csv_defectuoso_no_publica_cifras` | R14 (13/11) | ITP §15 y §16 | CUMPLIDO Y PROBADO | — |
| PY-221 | Sin credenciales ni datos personales reales | OBLIGATORIO | `pipeline.sin_datos_personales`; clientes ficticios | `test_sin_datos_personales` | R14 (13/11) | ITP §15 y §16 | CUMPLIDO Y PROBADO | — |

**No obligatorios de Python** (14 filas):

| ID | Qué es | Carácter | Estado |
|---|---|---|---|
| PY-13 | pytest | RECOMENDADO | Se usa `unittest` (265 pruebas); pytest las puede lanzar |
| PY-14 | Plotly | ADMISIBLE | No se usa (Matplotlib) |
| PY-41 | Laboratorio sintético en el dashboard | OPCIONAL | Hecho: pestaña Predicción, rotulada como laboratorio |
| PY-140 | Último resultado rotulado DESACTUALIZADO | ADMITIDO | Hecho: `test_csv_defectuoso_no_publica_cifras` (R14) |
| PY-158 | Se valora el denominador y el tamaño de muestra | CRITERIO | — |
| PY-176 | Arquitectura sugerida | RECOMENDADO | Se sigue: `app_dashboard`, `pipeline`, `analiticas`, `visualizaciones`, `config` y `tests` |
| PY-213 | Estructura `sneaker-data-lab/` o una equivalente documentada | RECOMENDADO | La equivalente es `04_Python/`, documentada en el README |
| PY-222 a 228 | Isolation Forest, validación progresiva, intervalos de predicción, otro clustering, instantáneas históricas, alertas de reposición y PDF | OPCIONAL | No hechos (las alertas de stock bajo son obligatorias y están) |

### 2.5 Sistemas de Gestión Empresarial: Odoo (módulo 0491, IM §4.2 y RA1–RA4)

**Estado final de la evidencia:** el PDF de Berme se conserva y se valora documentalmente. EVIDENCIA DOCUMENTAL no equivale a CUMPLIDO Y PROBADO en este entorno. S00005 se reconoce como caso documental de Odoo; su trazabilidad entre sistemas permanece parcial y los códigos no se alteran; no se esperan más archivos para esta entrega. Las 17 filas conservan sus ID. IM-SGE-07, 10, 12 y 16 pasan de PARCIAL a EVIDENCIA DOCUMENTAL porque S00005 sí documenta el flujo de Odoo; no pasan a CUMPLIDO Y PROBADO en este entorno. IM-ITG-04 reconoce documentalmente el pedido colectivo de 40 pares. Los requisitos de trazabilidad entre sistemas siguen PARCIALES.

| ID | REQUISITO | OBL/OPC | ARCHIVO | COMPROBACIÓN CONCRETA | EVIDENCIA | DOCUMENTADO EN | ESTADO | PENDIENTE |
|---|---|---|---|---|---|---|---|---|
| IM-SGE-06 | Instalar, configurar y adaptar Odoo a la empresa | OBLIGATORIO | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | PDF p. 3–6 | MEM §4; estado final de entrega | EVIDENCIA DOCUMENTAL | Instalación y configuración aportadas; no reproducidas en esta instancia |
| IM-SGE-07 | Odoo como sistema central: la venta encadena el resto del flujo | OBLIGATORIO (enunciativo) | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | PDF p. 10–12 | MEM §4; estado final de entrega | EVIDENCIA DOCUMENTAL | Flujo S00005 documentado dentro de Odoo; no prueba conexión con los módulos auxiliares. |
| IM-SGE-08 | Máquina virtual con Ubuntu y Odoo instalado, documentado y operativo | OBLIGATORIO (enunciativo) | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | PDF p. 3–6 | MEM §4; estado final de entrega | EVIDENCIA DOCUMENTAL | Ubuntu/OrbStack y servicio documentados; sin acceso vivo aquí |
| IM-SGE-09 | Compañía y perfiles: comercial, producción, almacén y administración | OBLIGATORIO (enunciativo; perfiles «cuando proceda») | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | PDF p. 6, 17 | MEM §4; estado final de entrega | PARCIAL | Usuarios documentados; no acreditados todos los perfiles de la rúbrica |
| IM-SGE-10 | Clientes y contactos | OBLIGATORIO (enunciativo) | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | PDF p. 10, 13 | MEM §4; estado final de entrega | EVIDENCIA DOCUMENTAL | Club Atlético NOVA documentado como cliente de S00005; no se exige crear Club Halcones para reproducir el ejemplo |
| IM-SGE-11 | Oportunidades de CRM antes de la venta | CONDICIONAL (si CRM entra en el alcance) | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | Sin evidencia específica | MEM §4; estado final de entrega | PENDIENTE | CRM no acreditado; condicionado al alcance del profesor |
| IM-SGE-12 | Presupuesto y pedido de venta con líneas, cantidades, variantes y condiciones | OBLIGATORIO (enunciativo) | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | PDF p. 10, 16 | MEM §4; estado final de entrega | EVIDENCIA DOCUMENTAL | S00005 documentado con una línea de 40 pares; variantes en páginas posteriores. No se inventa un reparto por talla ni una exportación. |
| IM-SGE-13 | Fabricación: productos fabricados, listas de materiales y órdenes | OBLIGATORIO (enunciativo; lo trabajado en clase) | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | PDF p. 7–11 | MEM §4; estado final de entrega | EVIDENCIA DOCUMENTAL | Lista de materiales y fabricación documentadas; sin ejecución actual aquí |
| IM-SGE-14 | Inventario, movimientos y entrega | CONDICIONAL (si se ha trabajado) | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | PDF p. 11, 17 | MEM §4; estado final de entrega | EVIDENCIA DOCUMENTAL | Entrega y stock históricos documentados |
| IM-SGE-15 | Facturación o simulación documentada | CONDICIONAL (si entra en el alcance) | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | PDF p. 12 | MEM §4; estado final de entrega | EVIDENCIA DOCUMENTAL | Factura/pago documentados del flujo S00005; no una factura SO024 ni ejecución actual. |
| IM-SGE-16 | Trazabilidad: capturas, exportaciones o informes del mismo pedido de principio a fin | OBLIGATORIO (enunciativo) | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | PDF p. 10–12 | MEM §4; estado final de entrega | EVIDENCIA DOCUMENTAL | Trazabilidad documental de S00005 dentro de Odoo, no una cadena acreditada entre todos los módulos. |
| IM-SGE-17 | Requisito estable: Odoo es el núcleo y se demuestra una venta realista | OBLIGATORIO | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | PDF p. 10–12 | MEM §4; estado final de entrega | EVIDENCIA DOCUMENTAL | Venta realista en el PDF; no demostración ERP en vivo desde aquí |
| IM-SGE-21 | Autocomprobación: Odoo adaptado y con un flujo realista | AUTOCOMPROBACIÓN | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | PDF p. 7–18 | MEM §4; estado final de entrega | EVIDENCIA DOCUMENTAL | Flujo y variantes documentados, con límites declarados |
| IM-SGE-RA1 | RA1 CE d)-h): verificar el entorno (sistema operativo, gestor de datos, configuración) y documentar operaciones e incidencias | CRITERIO (RA/CE) | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | PDF p. 3–6 | MEM §4; estado final de entrega | PARCIAL | Entorno documentado; registro completo de incidencias/recuperación no aportado |
| IM-SGE-RA2 | RA2 CE a)-f): implantar: módulos, instalación, configuración, verificación y documentación | CRITERIO (RA/CE) | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | PDF p. 3–6 | MEM §4; estado final de entrega | EVIDENCIA DOCUMENTAL | Implantación y módulos documentados |
| IM-SGE-RA3 | RA3 CE d), g) y h): exportar datos e informes y sacar información | CRITERIO (RA/CE) | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | Sin evidencia específica | MEM §4; estado final de entrega | PENDIENTE | No se aporta exportación CSV acreditada de S00005 desde Odoo. |
| IM-SGE-RA4 | RA4 CE a), d), h) e i): adaptar interfaces de entrada y procesos, probar y documentar | CRITERIO (RA/CE) | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Revisión documental; no ejecución en vivo en el cierre | PDF p. 16–18 | MEM §4; estado final de entrega | PARCIAL | Adaptaciones documentadas; verificación completa de procesos e incidencias no acreditada en este entorno |

En el apartado 2.6 hay dos filas más que también son de Berme: el entregable «ERP configurado» con su backup (IM-COM-16) y el punto 4 de la memoria (IM-COM-24).

**No obligatorios de Odoo:** IM-SGE-01 a 03 (objetivos), 04 (flujo de referencia), 05 (ruta MTO) y 18 a 20 (ejemplo/guion). No se usan para compensar pendientes obligatorios; el guion final explica el alcance documental.

### 2.6 Proyecto Intermodular: entregables comunes e integración

| ID | REQUISITO | OBL/OPC | ARCHIVO | COMPROBACIÓN CONCRETA | EVIDENCIA | DOCUMENTADO EN | ESTADO | PENDIENTE |
|---|---|---|---|---|---|---|---|---|
| IM-COM-01 | Código propio y comprensible: el equipo explica sus decisiones | OBLIGATORIO | Todo el repositorio | — | — | GD; SD | NO VERIFICABLE | Se ve en la defensa. Banco de preguntas y ejercicios en GD; ensayo en SD |
| IM-COM-02 | El código de la web, PSP y la documentación en un repositorio Git del equipo | OBLIGATORIO (enunciativo) | Repositorio NOVA, rama main | Cierre publicado mediante la PR #2 (merge `4a25d5a`) y documentación final con la PR #3 (merge `372f811`) | Git, historial publicado y evidencias del cierre | README raíz | CUMPLIDO (DOCUMENTADO) | El acceso del profesor al repositorio privado se gestiona fuera de Git |
| IM-COM-03a | No hay credenciales reales en el repositorio | OBLIGATORIO (prohibición) | `.gitignore` (`.env` y `conexion.properties`); `servidor-admin/.env.example` vacío | Búsqueda de las contraseñas de demostración en las evidencias y la documentación (entonces `pruebas/` y `docs/`) y los resultados del 13/11: 0 coincidencias (R26). El escaneo de los blobs de la rama, en la preparación de la PR | R26 | MI (convenciones); README raíz | CUMPLIDO Y PROBADO | — |
| IM-COM-03b | Las contraseñas de demostración se comunican por el medio acordado | OBLIGATORIO (enunciativo) | — | — | — | MI (convenciones) | PENDIENTE DE DUDA | [DUDA PARA EL PROFESOR (D12)]: el medio para dar las contraseñas de demostración |
| IM-COM-04 | Datos ficticios suficientes de varios productos, clientes y pedidos | OBLIGATORIO (enunciativo) | `05_datos_prueba.sql`, `21_catalogo_web.sql`, `generador_datos.py` | Base: 6 clientes, 107 modelos y 12 pedidos; sintéticos: 900 pedidos | R01, R14 | MAD §3.2; ITP §10 | CUMPLIDO Y PROBADO | — |
| IM-COM-05 | Documentación que otro equipo pueda seguir para instalar, ejecutar y repetir el caso | OBLIGATORIO (enunciativo) | `README.md` y los README de cada módulo | El manual seguido al pie de la letra en un clon nuevo y una base vacía: 23 scripts con salida 0, 123/0/1, Java 47/47, PSP 27/27, Python y servidor (R24). Se corrigieron dos errores del manual que salieron al seguirlo | R24; MI; README raíz | MI; README raíz | PARCIAL | La instalación de Odoo está documentada en el PDF de Berme (pp. 3-6 y 19), en su entorno; no se reproduce desde este repositorio. La copia y su restauración no constan. **[BERME: datos de la copia de seguridad y de la restauración]** |
| IM-COM-07 | Todos conocen el funcionamiento global | OBLIGATORIO | — | — | — | GD; SD | NO VERIFICABLE | Simulación de defensa por persona |
| IM-COM-09 | Preparación para preguntas individuales en la defensa | OBLIGATORIO (enunciativo) | — | — | — | GD; SD | NO VERIFICABLE | Ensayo individual (SD). El reparto real se cuenta en MEM §9 |
| IM-COM-15 | Entregable: repositorio con la web, PSP, README e instrucciones | OBLIGATORIO (entregable) | Repositorio NOVA, rama main | Cierre publicado mediante la PR #2 (merge `4a25d5a`) y documentación final con la PR #3 (merge `372f811`) | Git, historial publicado y evidencias del cierre | README raíz; MI | CUMPLIDO (DOCUMENTADO) | El acceso del profesor al repositorio privado se gestiona fuera de Git |
| IM-COM-16 | Entregable: ERP configurado y su copia o backup | OBLIGATORIO (entregable) | `odoo/documentacion/Odoo-NOVA-Sneakers.pdf` | Configuración documentada: entorno e instalación (pp. 3-5), base, empresa y aplicaciones (p. 6), producto, variantes y usuarios (pp. 7-8, 16-17); procedimiento de copia (p. 19) | PDF de Berme (evidencia documental) | MEM §4 | PARCIAL | **PUEDE IMPEDIR APROBAR.** Falta la copia de seguridad de Berme: no consta ninguna copia hecha ni restaurada, solo el procedimiento. **[BERME: ubicación, fecha, tamaño, SHA-256 y prueba de restauración, o confirmar que no hay copia]** |
| IM-COM-17 | Entregable: ejemplos de órdenes en CSV/JSON y los ficheros de la demo | OBLIGATORIO (entregable) | `03_PSP/pruebas/custom40.csv`, `03_PSP/datos/custom40_fabricacion_psp.csv`, `04_Python/entrada_acc/` | PSP y Python procesan los CSV de CUSTOM-40 y SO024 PROVISIONAL | R09, R14, R23 (`SO024_PROVISIONAL_fabricacion.csv`, `06_pedidos_unicos_SO024.csv`) | MEM §6.2; SDP | PARCIAL | Muestras de PRUEBA disponibles; no hay exportación acreditada de S00005 desde Odoo. |
| IM-COM-18 | Entregable: memoria técnica común | OBLIGATORIO (entregable) | `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf` | — | `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf` (los 9 puntos y conclusiones) | MEM | PARCIAL | Versión de entrega con límites declarados. Faltan los campos [EQUIPO], [OMAR], [ÁLVARO] y [BERME] del §9 (reparto real y uso de la IA de cada persona) y otros datos personales; la trazabilidad de S00005 entre sistemas no está demostrada. |
| IM-COM-19 | Entregable: manual de demostración con los pasos exactos | OBLIGATORIO (entregable) | `06_Intermodular/manuales/MANUAL_DEMOSTRACION.md` | Guion final de módulos disponibles con CUSTOM-40 y PRUEBA | `06_Intermodular/manuales/MANUAL_DEMOSTRACION.md` | MD | PARCIAL | Guion actualizado con S00005 documental y pruebas independientes; no demuestra ERP en vivo ni S00005 en los módulos auxiliares. |
| IM-COM-20 | Entregable: presentación para la defensa y el tribunal | OBLIGATORIO (entregable) | `06_Intermodular/defensa/PRESENTACION.md`, `06_Intermodular/defensa/PRESENTACION.pptx` | — | Guion vigente: `06_Intermodular/defensa/PRESENTACION.md` (15 diapositivas, actualizado con S00005) | PRES | PARCIAL | El `.pptx` tiene todavía el contenido anterior a S00005 y contradice el guion y la memoria. **[EQUIPO: corregir el `.pptx` diapositiva a diapositiva o retirarlo]**; la diapositiva 14 (reparto) depende del §9 de la memoria. Ensayarla (SD) |
| IM-COM-21 | Memoria 1: empresa, problema y alcance | OBLIGATORIO | `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf` | — | MEM §1 | MEM §1 | CUMPLIDO (DOCUMENTADO) | [DUDA PARA EL PROFESOR (D2)]: el nombre de la marca |
| IM-COM-22 | Memoria 2: arquitectura y relación entre módulos | OBLIGATORIO | `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf` | — | MEM §2 | MEM §2 | CUMPLIDO (DOCUMENTADO) | — |
| IM-COM-23 | Memoria 3: diseño de la interfaz y criterios responsive | OBLIGATORIO | `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf`; `01_Interfaces/evidencias/web/README.md`; `01_Interfaces/cliente/README.md` | — | MEM §3; EPI; PUS | MEM §3; EPI; PUS | CUMPLIDO (DOCUMENTADO) | **Límite declarado:** no se ha hecho la prueba con personas (IM-INT-RA4-hi-usab) |
| IM-COM-24 | Memoria 4: configuración de Odoo y flujo demostrado | OBLIGATORIO | MEM §4 y PDF de Berme | Síntesis documental y límites reales del cierre | PDF pp. 3–18 | MEM §4 | EVIDENCIA DOCUMENTAL | S00005 documentado; sin ERP en vivo ni integración entre sistemas probada. |
| IM-COM-25 | Memoria 5: diseño del subsistema PSP | OBLIGATORIO | `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf`; `03_PSP/memoria/DOCUMENTACION_PSP.md` | — | MEM §5; DPSP | MEM §5; DPSP | CUMPLIDO (DOCUMENTADO) | — |
| IM-COM-26 | Memoria 6: modelo de datos común e integración CSV/JSON | OBLIGATORIO | `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf`; `06_Intermodular/` | — | MEM §6; `06_Intermodular/SO024/caso-comun-SO024.md`; `06_Intermodular/SO024/contrato-fabricacion.md` | MEM §6; SDP | PARCIAL | Modelo/CSV documentados para los ensayos; no hay correspondencia acreditada de S00005 entre sistemas. |
| IM-COM-27 | Memoria 7: pruebas y resultados | OBLIGATORIO | `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf`; `06_Intermodular/evidencias/cierre-entrega-20261113/`; `06_Intermodular/evidencias/regresion-final/` (histórica) | — | MEM §7.1 y `06_Intermodular/evidencias/cierre-entrega-20261113/README.md` (código entregado, `4f09742`); MEM §7.2 y `06_Intermodular/evidencias/regresion-final/README.md` (históricas, no repetidas) | MEM §7 | CUMPLIDO (DOCUMENTADO) | — |
| IM-COM-28 | Memoria 8: dificultades, decisiones y mejoras | OBLIGATORIO | `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf` | — | MEM §8 | MEM §8 | CUMPLIDO (DOCUMENTADO) | — |
| IM-COM-29 | Memoria 9: reparto real del trabajo y contribuciones | OBLIGATORIO | `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf` | Historial conservado; no se infieren responsabilidades personales por número de commits | MEM §9 (lo que dice Git en `main`: omar1676 113, 7 de ellos fusiones; Alvarobaz 25; Ivan Bermejo 9; y 1 del autor «t») | MEM §9 | NO VERIFICABLE | Faltan los campos [OMAR], [ÁLVARO] y [BERME] del §9.2 y del §9.4 (uso de la IA). Las aportaciones no confirmadas se declaran «no verificables», sin inventarlas |
| IM-COM-32 | Autocomprobación: ¿se puede repetir la demo siguiendo la documentación? | AUTOCOMPROBACIÓN | — | — | MD; MI; R24 | MD; MI | PARCIAL | Guion de módulos disponibles y PDF de S00005; sin ejecución en vivo del ERP ni trazabilidad entre sistemas probada |
| IM-COM-33 | Autocomprobación: ¿todos explican el proyecto y su contribución? | AUTOCOMPROBACIÓN | — | — | — | GD; SD | NO VERIFICABLE | Simulación de defensa |
| IM-ITG-04 | Un pedido colectivo como hilo conductor (40 pares) | OBLIGATORIO (enunciativo) | PDF de Berme; CASO | Caso de Odoo documental | PDF pp. 10–12; R23 solo para el ensayo SO024 | CASO; MEM §6; MD | EVIDENCIA DOCUMENTAL | S00005 del Club Atlético NOVA: 40 pares documentados en Odoo. No se atribuye su procesamiento a PostgreSQL/PSP/Python. |
| IM-ITG-06 | Explicar qué es del ERP, qué es auxiliar y qué ampliaciones harían falta para producción | OBJETIVO (se pide en la demo) | `03_PSP/README.md` («Relación con PostgreSQL y Odoo») | — | MEM §2.3 y §2.4; `03_PSP/README.md` | MEM §2.3–§2.4 | CUMPLIDO (DOCUMENTADO) | Enseñarlo en la demo (MD) |
| IM-ITG-08 | Se evalúa la coherencia de los datos y del flujo | CRITERIO | PDF de Berme; CASO | Caso de Odoo documental | PDF pp. 10–12; R23 solo para el ensayo SO024 | CASO; MEM §6; MD | PARCIAL | No hay trazabilidad de S00005 entre sistemas. Los ensayos SO024 PROVISIONAL y CUSTOM-40 no se renombran ni prueban esa venta. |
| IM-ITG-09 | Modelo de información común del pedido | OBLIGATORIO | PDF de Berme; CASO | Caso de Odoo documental | PDF pp. 10–12; R23 solo para el ensayo SO024 | CASO; MEM §6; MD | PARCIAL | Contrato CSV disponible; falta una correspondencia acreditada del caso S00005 con los módulos auxiliares. |
| IM-ITG-10 | El mismo identificador en web, Odoo y PSP | OBLIGATORIO | PDF de Berme; CASO | Caso de Odoo documental | PDF pp. 10–12; R23 solo para el ensayo SO024 | CASO; MEM §6; MD | PARCIAL | No hay identificador o equivalencia acreditados de S00005 en PostgreSQL y PSP; web Custom simulado. |
| IM-ITG-11 | El mismo cliente en todos los bloques | OBLIGATORIO | PDF de Berme; CASO | Caso de Odoo documental | PDF pp. 10–12; R23 solo para el ensayo SO024 | CASO; MEM §6; MD | PARCIAL | Club Atlético NOVA figura en Odoo; coincidir con un nombre de los fixtures no prueba el mismo pedido. |
| IM-ITG-12 | El mismo producto y variante | OBLIGATORIO | PDF de Berme; CASO | Caso de Odoo documental | PDF pp. 10–12; R23 solo para el ensayo SO024 | CASO; MEM §6; MD | PARCIAL | No se han conciliado productos, variantes y SKU de S00005 entre Odoo y los módulos auxiliares. |
| IM-ITG-13 | La misma cantidad | OBLIGATORIO | PDF de Berme; CASO | Caso de Odoo documental | PDF pp. 10–12; R23 solo para el ensayo SO024 | CASO; MEM §6; MD | PARCIAL | S00005 tiene 40 pares en el PDF; que otro ensayo tenga 40 no acredita igualdad de líneas o variantes. |
| IM-ITG-14 | El estado de cada bloque | OBLIGATORIO | PDF de Berme; CASO | Caso de Odoo documental | PDF pp. 10–12; R23 solo para el ensayo SO024 | CASO; MEM §6; MD | PARCIAL | Estados de S00005 documentados en Odoo; estados de ensayos en los otros módulos sin equivalencia probada. |
| IM-ITG-15 | Misma empresa y productos, clientes y pedidos compatibles | OBLIGATORIO | PDF de Berme; CASO | Caso de Odoo documental | PDF pp. 10–12; R23 solo para el ensayo SO024 | CASO; MEM §6; MD | PARCIAL | Catálogo web/PostgreSQL coherente en sus pruebas; sin correspondencia acreditada de S00005 y sus productos en Odoo. |
| IM-ITG-16 | Al menos un caso que se pueda seguir de la solicitud a las evidencias | OBLIGATORIO | PDF de Berme; CASO | Caso de Odoo documental | PDF pp. 10–12; R23 solo para el ensayo SO024 | CASO; MEM §6; MD | PARCIAL | **PUEDE IMPEDIR APROBAR.** Falta el seguimiento del mismo pedido entre Odoo y módulos auxiliares; elegir S00005 no lo demuestra. |
| IM-ITG-18 | Autocomprobación: ¿mismo caso y datos compatibles en los tres bloques? | AUTOCOMPROBACIÓN | PDF de Berme; CASO | Caso de Odoo documental | PDF pp. 10–12; R23 solo para el ensayo SO024 | CASO; MEM §6; MD | PARCIAL | No está demostrada la compatibilidad del mismo pedido S00005 en todos los sistemas. |

**No obligatorios comunes:**

| ID | Qué es | Carácter | Estado |
|---|---|---|---|
| IM-COM-06 y 08 | Equipos de 3 o 4 y roles de referencia | ORIENTATIVO | Equipo de 3 |
| IM-COM-10 a 14 | Fases e hitos propuestos (análisis, construcción, integración, calidad y entrega) | ORIENTATIVO | Hay una versión candidata y una regresión completa (R01–R25). Faltan el documento de análisis con bocetos y el backlog inicial |
| IM-COM-30 y 31 | Guion de demo, pasos 1 y 8 | ORIENTATIVO | En MD, pasos 1 y 8 |
| IM-ITG-01 a 03, 05 | Encargo y objetivos | OBJETIVO | — |
| IM-ITG-07 | Integración con CSV/JSON y procedimientos documentados | OPCIONAL (permiso) | Se usa (MEM §6.2) |
| IM-ITG-17 | Guion de demo, paso 5: exportar el pedido a CSV/JSON | ORIENTATIVO | Con el 15 (R23, ensayo histórico; MD §3, CUSTOM-40). Falta la exportación desde Odoo |
| IM-ITG-19 | Encaje de otros módulos («Por acordar») | OPCIONAL (para el profesorado) | Acceso a Datos y Python aportan al mismo caso (D3) |

### 2.7 El reparto de tareas (RT)

`Sneaker_Factory_Reparto_Tareas_Git_Worktrees.pdf` lo escribió el equipo, no el profesor («propuesta organizativa», RT p. 1). Sus 88 filas no son requisitos evaluables y no se cuentan aquí. Tres avisos:
- RT-AD-13 y RT-J-13 copian los mínimos de AD, que ya están en el apartado 2.2.
- El reparto que dice el RT no coincide con lo que se ve en Git. Por ejemplo, PSP-01 y PSP-04 eran de Berme y las subió Omar (`9dc66ac`; `03_PSP/README.md`, «Autoría»).
  - En Git, `main` tiene 113 commits de omar1676 (7 son fusiones), 25 de Alvarobaz, 9 de Ivan Bermejo y 1 del autor «t». Los 2 del portal de Berme se trajeron con su autoría. El autor de un commit no prueba quién hizo el trabajo.
  - El punto 9 de la memoria (IM-COM-29) tiene que contarlo como fue: **[EQUIPO: completar el §9.2 y el §9.4]**.
- El formato de commits del RT (`feat(web): …`) no es el que usa el equipo ahora (en inglés y sin prefijo).

---

## 3. Ampliaciones (no las pide ningún enunciado; no cuentan para aprobar)

| Ampliación | ARCHIVO | COMPROBACIÓN | EVIDENCIA | ESTADO | Pendiente o aviso |
|---|---|---|---|---|---|
| Tienda online: cuentas, carrito, pago simulado y «Mis pedidos» | `02_Acceso_Datos/sql/20_tienda_web.sql`, `21_catalogo_web.sql`; `servidor-admin/tienda.js`; `01_Interfaces/cliente/js/tienda.js` | Compra completa en Edge (escritorio y móvil) contrastada con PostgreSQL y el panel; pruebas Node y SQL de la tienda | R19 139/139; R12 39/39; R03 55/55 | AMPLIACIÓN, probada el 13/11 | Fallo conocido del 20: un correo de más de 150 caracteres da un error técnico; desde la web no se puede provocar |
| Los 100 modelos a la venta, con sus nombres comerciales | `21_catalogo_web.sql`, `js/modelos.js` | El 21, que se puede repetir (R01, 1 PASS); la T12 del SQL de la tienda (100 modelos y 880 SKU); compra de un modelo nuevo de cada colección | R01, R03, R16, R19 | AMPLIACIÓN, probada el 13/11 | Precios, colores y stock provisionales. La nave tiene capacidad 2.000 y guarda 17.170 pares: **[POR DECIDIR (los tres)]** |
| Bloque de compra de la ficha y colores de Álvaro por colección (WCAG AA) | `css/inicio.css`, `css/tienda.css`, `js/tienda.js` | 100 fichas, teclado, 11 anchos y axe (R16); contraste 212/212 (A7, 12/11) | R16; A7 | AMPLIACIÓN, probada el 13/11 | **[ÁLVARO: revisar y confirmar]**: la adaptación de su paleta |
| Probador virtual: 3 figuras y la complexión según el peso y la estatura | `js/inicio.js`, `images/probador/` | Probador con la figura amplia y axe (R16); cambiar de zapatilla actualiza precio y tallas (R17) | R16, R17 | AMPLIACIÓN, probada el 13/11 | Es una aproximación visual y no recomienda tallas |
| Login y registro de Álvaro dentro de la tienda | `01_Interfaces/cliente/index.html` (su diálogo) | El registro en su diálogo durante la compra en Edge | R19 (`escritorio_05_login_alvaro.png`, `escritorio_06_registro.png`) | AMPLIACIÓN, probada el 13/11 | **[ÁLVARO: revisar y confirmar]**: la etiqueta dice «Usuario o correo», pero solo acepta correo |
| Panel de administración de Álvaro conectado a PostgreSQL (solo lectura) | `01_Interfaces/admin/`, `servidor-admin/`, `19_usuario_web.sql` | `npm test`; el panel tras la compra (dashboard, pedidos y auditoría) | R11 23/23; R19 (`panel_13` a `panel_15`); A3 (11/11) | AMPLIACIÓN, probada el 13/11 | En móvil, axe da `scrollable-region-focusable` en las tablas sin botones (**[ÁLVARO: revisar y confirmar]**). Lucide y Chart.js se cargan de internet |
| Reparto: botón «Marcar en reparto» y «En reparto» en «Mis pedidos» | `22_reparto_panel.sql`, `servidor-admin/bd.js`, `servidor.js`, `consultas.js`, `01_Interfaces/admin/script.js` | SQL del 22, Node y recorrido en Edge | R04 37/37; R20 29/29; R11 | AMPLIACIÓN, probada el 13/11 | — |
| Recibo por correo con Resend | `servidor-admin/correo.js`, `tienda.js`, `.env.example` | 7 pruebas con un Resend simulado: aceptado, rechazado, sin clave, error 500, sin respuesta, doble clic y clave oculta; 4 recibos durante la compra en Edge | R12; R19 | AMPLIACIÓN, probada con simulación | Nunca se ha enviado por el Resend real (no hay clave). Sin un dominio verificado, solo llega al correo de la cuenta |
| Recibo de prueba con Ethereal y Nodemailer 10.5.0 (solo en desarrollo) | `servidor-admin/correo.js`, `package.json`, `package-lock.json`, `js/tienda.js` (enlace) | 7 pruebas sin red; compra real contra Ethereal con datos ficticios; sin red y sin respuesta | R12; R22 16/16, 5/5 y 5/5; `npm ci` sin vulnerabilidades (R24) | AMPLIACIÓN, probada el 13/11 | Las vistas previas de Ethereal son públicas: solo con datos ficticios |
| **Portal del trabajador (Berme) y login único del personal** | `01_Interfaces/trabajador/`, `servidor-admin/rutas-trabajador.js`, `servidor.js`, `23_portal_trabajador.sql` | SQL del 23; `test:portal`; en Edge, administrador → panel, trabajador → portal, comercial → 403, las 4 páginas, avanzar estado, inventario, axe y móvil; el arranque y el login siguiendo el manual | R05 50/50; R13 24/24; R21 82/82; R24 | AMPLIACIÓN, integrada y probada el 13/11 (ya no está EN INTEGRACIÓN) | Los 2 commits de Berme se trajeron con su autoría. **[BERME: revisar y confirmar]**: la adaptación de sus rutas a las funciones del 23 |
| Dashboard de Python dentro del panel de Álvaro («Análisis de datos») | `01_Interfaces/admin/analisisAdmin.html`, `analisis.js`; `04_Python/.streamlit/config.toml` (`[theme.dark]`) | En Edge, en 1440, 820 y 390 px: solo entra el administrador (el trabajador, el comercial y un cliente de la tienda, no); la opción sale una vez en las 12 páginas del panel; las cifras, las 6 pestañas, los filtros, una descarga y el refresco de 60 s funcionan dentro del panel; las Estadísticas y el Dashboard de Álvaro siguen igual; axe sin violaciones nuevas; Streamlit solo escucha en 127.0.0.1; sin Streamlit, la página explica cómo arrancarlo | `01_Interfaces/evidencias/panel-admin/analisis-datos/` (45/45 y la escucha de Streamlit, 13/11) | CUMPLIDO Y PROBADO | Streamlit no tiene login propio: solo se abre desde este ordenador. El dashboard sigue existiendo por su cuenta, como pide la rúbrica de Python. **[ÁLVARO: revisar y confirmar]:** una línea más en el menú de sus 12 páginas |
| Conector de Odoo y rutas de pedidos de Berme | `servidor-admin/odoo.js`, `pedidos.js` | El arranque dice «Conector de Odoo desactivado» (R24); `pedidos.js` no se monta | R24 | **No activo y sin probar** | Desde este equipo no se llega a ningún Odoo. Escribe en `log_eventos` directamente: habría que adaptarlo antes de montarlo |

No son ampliaciones, pero mejoran la calidad: la simplificación del Python y la limpieza de comentarios de Java y PSP (`d0490cf` y `eae5fc5`). Las salidas siguen iguales a la referencia (R15) y las pruebas pasan (R06, R09 y R14).

**Aviso de alcance:** AD-136 dice que «se valorará la coherencia con el proyecto de fábrica más que incorporar funcionalidades no solicitadas». Las ampliaciones no suman por sí solas y no deben quitar tiempo a lo obligatorio que falta. **[DUDA PARA EL PROFESOR (D6)]**

---

## 4. Límites finales de esta entrega

No es una lista de nuevas ampliaciones ni una espera de trabajo de compañeros. Se entrega lo existente con estos límites: S00005 sin trazabilidad entre sistemas; códigos Runner X sin conciliar; exportación ACC de PRUEBA; usabilidad con personas y parte de evidencias manuales no repetidas; ERP documental sin API verificada aquí; backup/restauración Odoo no acreditados en este entorno; atribuciones personales no confirmadas. Véase `06_Intermodular/ESTADO_ENTREGA_FINAL.md` y el guion disponible.

La corrección del comprobador PSP ya está incorporada con autoría de Berme (`4f09742`) y verificada. No se borran sus pruebas ni las evidencias del fallo anterior. Los cambios adicionales al catálogo, seguridad, algoritmo de predicción o integración ERP quedan fuera del cierre.

## 5. Dudas para el profesor

| # | Duda | Por qué importa |
|---|---|---|
| D1 | ¿La versión 0.3 del IM y su rúbrica (20/30/30/20) son las definitivas? ¿Cuál es la fecha de entrega, de la defensa y del tribunal? AD solo dice «noviembre de 2026 (fecha exacta comunicada por el docente)»; el IM y Python no tienen fecha | Plan de trabajo |
| D2 | ¿Se acepta la marca «NOVA Sneakers» en lugar de «Sneaker Factory», en todos los bloques? | IM-ITG-15, AD-02, IM-COM-21 |
| D3 | ¿Acceso a Datos y Python entran en el proyecto intermodular? ¿Con qué peso? El IM deja los demás módulos «Por acordar» | El tribunal común (20 %) |
| D4 | Decisión del equipo: SO024 figura bajo «EJEMPLO DE PEDIDO CUSTOM» en el v0.3, según la revisión del equipo; se elige S00005 documentado en Odoo. No se acredita por ello la integración entre sistemas. La evaluación de esa coherencia corresponde al profesor. | B2, IM-ITG-10 a 12 |
| D5 | Odoo: ¿qué alcance de CRM, fabricación, inventario y facturación? ¿VM o instancia? ¿En qué formato va el backup? ¿Qué versión? ¿Qué cuenta como «simulación documentada» de la factura? ¿Qué adaptación de interfaces pide RA4? | B1 |
| D6 | ¿La tienda, el panel, el reparto, los correos y el portal cuentan como ampliación, o pueden restar por AD-136? | Apartado 3 |
| D7 | Interfaces: ¿qué «técnicas CSS vistas en clase»? ¿Qué evidencia se espera de la prueba de usabilidad (número de usuarios, formato) y qué estándar de accesibilidad? ¿Suma el JavaScript? | IM-INT-05, RA4 y RA8 |
| D8 | Interfaces: ¿el formulario Custom tiene que pedir la fecha objetivo y enseñar un identificador del pedido? | IM-INT-07, ITG-10 |
| D9 | PSP: ¿los tiempos de espera son obligatorios (p. 4 frente a p. 11)? ¿Cuántos hijos como mínimo? ¿La sincronización del RA1 obliga a usar hilos? ¿La entrada tiene que ser una exportación real de Odoo o vale una copia preparada? | PSP-07, PSP-09, PSP-27, RA1 |
| D10 | AD: ¿«administración de usuarios, roles y permisos» (AD-57) se cumple asignando roles, o hay que poder editar los permisos? ¿Hace falta la operación «modificar pedido» en Java (AD-86)? ¿Qué significa «sobre los registros autorizados» en el panel (AD-103)? ¿«Aprobar todas las partes» es un 5 en cada bloque? ¿Cuentan para AD los 5 CSV que pide Python? | AD-57, 86, 103 y 138 |
| D11 | Python: ¿5 o 6 pestañas, y se pueden enseñar predicciones sintéticas en la sexta? ¿10 o 12 CSV, y qué es el de «auditoría»? ¿El informe técnico es la memoria técnica? ¿Una exportación de una base de prueba montada con los scripts cuenta como «REAL»? ¿R1–R3 se pueden simular editando los CSV o tienen que salir de un alta real en ACC? ¿Neto o bruto, si el contrato no lo dice? ¿Basta con NO CALCULABLE en RFM, KMeans y predicción con los datos reales (caso J)? | PY-40, 161, 167, 175, 183 a 185, 192, 194 y 215 |
| D12 | Común: ¿por qué medio se comunican las contraseñas de demostración? ¿Formato, extensión e idioma de la memoria y del manual? ¿Qué acceso necesita el profesor al repositorio? ¿El backup de Odoo va en el repositorio? ¿La nota es individual o de grupo? ¿Cuánto dura la exposición ante el tribunal? | IM-COM-03b, IM-COM-15 a 20 |
