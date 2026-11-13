# Regresión final · 13/11/2026

Todas las pruebas del proyecto, repetidas sobre el árbol final de la rama `integracion/candidata-2` (`8cdc08c`, el código que se propone a `main`), exportado con `git archive` a una carpeta desechable. No se ha cambiado ningún archivo de código para pasarlas.

- **Entorno:** Windows 11; PostgreSQL 17.11 en un clúster de pruebas (bases desechables nuevas, montadas desde cero con los scripts del repositorio); JDK 17.0.12; Python 3.13.5 (pandas 3.1.1, streamlit 1.67.0); Node 24.15.0 y npm 11.12.1 (express 5.3.0, pg 8.23.1, nodemailer 10.5.0); Microsoft Edge 157 con Playwright 1.65.0 y axe.
- **Servidor de pruebas:** `127.0.0.1:3301`, con un Resend simulado en el 3398. Nunca la base del equipo.
- **Sin contraseñas:** se pasaron por la entrada estándar. Ningún archivo de esta carpeta las lleva. Las rutas del ordenador se han cambiado por marcas como `<repo>` (el árbol exportado) o `<temporal>`.
- Los scripts de navegador (Playwright) no están en el repositorio; solo sus resultados y capturas. Los scripts SQL de prueba sí: `01_sql/pruebas_usadas/`.
- Las salidas de `psql` y de los servidores se guardan como `.log.txt`, porque el `.gitignore` excluye los `*.log`.

| Batería | Hora | Resultado | Archivos |
|---|---|---|---|
| SQL 01–23 desde cero; batería 09–16 | 00:58 | Los 23 scripts con salida 0 (el 23, dos veces). **123 PASS, 0 FAIL y 1 ERROR previsto** (S4b). Igual en una segunda base y en una sin el 23 | `01_sql/00_resumen.txt`, `01_montaje_01_23.txt`, `logs_nova_rf_base/` |
| Consulta 3 (HAVING) | 00:59 | 1 fila: `NOVA-4-43` (20 en stock y 11 pendientes → 9) | `01_sql/04_06_consultas.txt` |
| SQL de la tienda (20 y 21) | 00:59 | 55 PASS, 0 FAIL | `01_sql/05_sql_tienda.txt` |
| SQL del reparto (22), con el 23 instalado | 00:59 | 37 PASS, 0 FAIL | `01_sql/07_sql_reparto_con23.txt` |
| SQL del portal (23) | 00:59 | 50 PASS, 0 FAIL | `01_sql/08_sql_portal.txt` |
| Java `PruebasRubrica` | 01:01 | 47 PASS, 0 FAIL (y el TXT, el JSON de usuarios y el CSV que escribe) | `02_java_psp/02_pruebas_rubrica.txt`, `02_salidas_java/` |
| PSP `PruebasPsp` | 01:02 | 27 de 27; CUSTOM-40 con código 0; archivo inexistente, código 1; cantidad 0, código 2 | `02_java_psp/04_*.txt` a `06_*.txt` |
| `scripts/comprobar_psp.py` | 01:02 | Falla en la primera comprobación, como ya se sabía (espera la respuesta antigua del validador) | `02_java_psp/07_comprobar_psp.txt` |
| `scripts/comprobar_web.py` | 01:02 | Correcta | `02_java_psp/08_comprobar_web.txt` |
| `npm test` | 01:03 | 23 de 23 con base desechable (sin ella, 22 y 1 saltada) | `03_node/01_*.txt`, `02_*.txt` |
| `npm run test:tienda` | 01:03 | 39 de 39 (incluidas 7 con un Resend simulado y 7 con Ethereal simulado) | `03_node/03_test_tienda.txt` |
| `npm run test:portal` | 01:04 | 24 de 24 | `03_node/04_test_portal.txt` |
| Python `unittest` | 00:59–01:12 | **Ran 265 tests, OK** | `04_python/02_unittest.txt` |
| Python, las 93 salidas de `main.py` frente a la referencia | 01:12 | 91 idénticas; 2 con 4 columnas nuevas a propósito (`informe_ejecutivo.csv`: prioridad, urgencia, impacto esperado y sustento; las 10 de antes, iguales); 4 archivos nuevos a propósito (caso N y metadatos). «caso N: 17 de 17 cifras coinciden con SQL» | `04_python/03_salidas_93.txt` |
| Web: mejoras | 01:14 | 81 de 81 | `05_web/01_mejoras.txt` |
| Web: Interfaces | 01:16 | 136 de 136 | `05_web/02_interfaces.txt`; capturas (catálogo con precios, ficha, contacto y Custom simulado, en escritorio y móvil) en `05_web/capturas_interfaces/` |
| Web completa | 01:18 | 114 de 114 | `05_web/03_web.txt` |
| Compra en Edge (escritorio y móvil, con PostgreSQL y el panel) | 01:22 | 139 de 139; 4 recibos y 4 pedidos pagados | `05_web/04_compra_edge.txt`; capturas en `../../../01_Interfaces/evidencias/tienda/capturas-2026-11-13/` |
| Reparto en Edge | 01:24 | 29 de 29 | `05_web/05_recorrido_reparto.txt`; capturas en `../../../01_Interfaces/evidencias/reparto-y-correo/` |
| Login único, roles y portal en Edge | 01:25 | 82 de 82 | `05_web/06_edge_portal.txt`; capturas en `../../../01_Interfaces/evidencias/portal-trabajador/` |
| Ethereal real, con datos ficticios | 01:32 | 16 de 16 | `05_web/07_ethereal_real.txt`; capturas en `../../../01_Interfaces/evidencias/correo-ethereal/` |
| Ethereal sin red y sin respuesta (simulados) | 01:32 | 5 de 5 y 5 de 5 | `05_web/08_*.txt`, `09_*.txt` |
| SO024 **PROVISIONAL** de principio a fin | 01:06 | 18 → Java («Nuevo pedido») → 40 pares y 3.996,00 € → 15 → PSP código 0 → 16 → Python: un solo pedido | `06_so024_provisional/00_cadena.txt` |
| Ventanas Swing (`ProbarVentanas`) | 01:08 | 76 PASS, 0 FAIL; sin conexión, 1 de 1 (las capturas del 13/11 están en `../../../02_Acceso_Datos/evidencias/java-swing/`) | `07_ventanas_swing/` |
| Manual de instalación (`06_Intermodular/manuales/MANUAL_INSTALACION.md`), seguido sobre un clon nuevo y una base vacía | 01:19–08:44 | Reproducible. Base: los 23 scripts con salida 0 y 123/0/1; Java 47/47; PSP 27/27; Python con un entorno nuevo (`pip install -r requirements.txt`, versiones exactas), `main.py` en los tres modos (el de errores, código 1) y el dashboard; servidor estático; `npm ci` (0 vulnerabilidades); `npm start` con el login único de las tres cuentas (200, 200 y 403) y la tienda (la API lista 106 modelos: los 100 de la web y 6 de los datos de demostración del 05 que usa Java; la web solo enseña sus 100); `npm test` 23/23. Se corrigieron dos pasos del manual (ver abajo) | `08_manual_instalacion/00_parte1.txt`, `00_parte2.txt` |

## Lo que se corrigió en el manual al seguirlo

- El recuento de la batería con `Select-String` no distinguía mayúsculas: daba 142 PASS y 5 ERROR. Con `-CaseSensitive`, 123 / 0 / 1.
- La carpeta `02_Acceso_Datos/java/lib` no existe en un clon nuevo: sin crearla, el driver no se copiaba y `pruebas.bat` daba 0/1. Creándola, 47/47.
- La primera comprobación del dashboard dio «no responde» justo después de una pausa de unas siete horas del ordenador, probablemente suspendido (la hora salta de 01:40 a 08:40); el servidor sí había arrancado (`health: ok`). Repetida a las 08:44: responde en 3 s.

## Lo que no es un fallo

- **`prueba_reparto.sql` tal cual da 36/1 (P7) en una base sin el 23** si el clúster ya tiene el 23 en otra base: los miembros de un rol (`pg_auth_members`) son de todo el clúster, no de cada base. Explicado en `01_sql/06b_causa_P7.txt`. Con el 23, la versión que cuenta `portal_trabajador` da 37/37.
- `main.py --modo sintetico-errores` termina con código 1 a propósito (datos bloqueados).
- El 16 sobrescribe los CSV de `04_Python/entrada_acc/`.

## No se ha repetido el 13/11

- **Lighthouse:** el último es del 11/11 (`../../../01_Interfaces/evidencias/web/lighthouse/`).
- **Caso K** (el dashboard abierto tres ciclos de 60 s en Edge): se hizo a las 00:44 con este mismo código (`04_Python/evidencias/dashboard/caso_k_*`).
