# Regresión del árbol limpio (13/11/2026, por la tarde)

Es la misma regresión que `../regresion-final/` (candidata 2, `9d589ae`), repetida sobre la rama de la limpieza final (`refactor/limpieza-final-nova`). Esa rama reorganiza las carpetas por asignaturas, quita 14 archivos sin uso y simplifica el código. **Todo da lo mismo que en la candidata 2.**

- **Entorno:** el mismo que el de `../regresion-final/`. Windows 11; PostgreSQL 17.11 en un clúster de pruebas, con bases desechables nuevas montadas desde cero con los scripts del repositorio; JDK 17.0.12; Python 3.13.5; Node 24.15.0 con express 5.3.0, pg 8.23.1 y nodemailer 10.5.0 (`npm ci`); Microsoft Edge con Playwright y axe.
- **Código probado:** el árbol de la rama exportado a una carpeta limpia.
  - SQL, Java, PSP, Python, SO024 y Swing (parte 1): `e5d024f`. Después de ese commit solo cambian la web, el servidor y la documentación.
  - Node, la web y el caso K (parte 2): `9e1130c`.
- **Ninguna base real:** solo el clúster de pruebas. Las rutas personales están sustituidas (`<repo>`, `<temporal>`…) y los enlaces de vista previa de Ethereal, tapados. Ningún archivo lleva contraseñas.
- **Scripts de prueba:** los de Playwright y los de montaje no están en el repositorio, igual que en `../regresion-final/`.

## Resultados, frente a la candidata 2

| Prueba | Candidata 2 (`../regresion-final/`) | Árbol limpio | Archivo |
|---|---|---|---|
| SQL 01–23 desde cero, batería 09–16 | 123 PASS, 0 FAIL, 1 ERROR previsto (S4b) | Igual, en tres bases (completa, repetida y sin el 23) | `01_sql/00_resumen.txt` |
| SQL de la tienda (20 y 21) | 55 / 0 | 55 / 0 | `01_sql/05_sql_tienda.txt` |
| SQL del reparto (22), con el 23 | 37 / 0 (sin el 23: 36 / 1, la P7, como ya se sabía) | Igual | `01_sql/07_sql_reparto_con23.txt` |
| SQL del portal (23) | 50 / 0 | 50 / 0 | `01_sql/08_sql_portal.txt` |
| Java `PruebasRubrica` | 47 / 0 | 47 / 0 | `02_java_psp/02_pruebas_rubrica.txt` |
| PSP: `PruebasPsp`, CUSTOM-40, archivo inexistente, cantidad 0 | 27 / 27; códigos 0, 1 y 2; la ficha, igual a la guardada | Igual | `02_java_psp/00_resumen.txt` |
| `scripts/comprobar_psp.py` y `comprobar_web.py` | La de PSP falla (ya se sabía); la de la web, correcta | Igual | `02_java_psp/07_*.txt` y `08_*.txt` |
| `npm test` / `test:tienda` / `test:portal` | 23 / 39 / 24 | 23 / 39 / 24 | `03_node/` |
| Python `unittest` | 265 OK | 265 OK | `04_python/02_unittest.txt` |
| Las salidas de `main.py` (real, sintético, con errores y generador) | — | Las 97, **idénticas** a las de la candidata 2. Los 22 PNG y los 4 `.log` cambian por la hora | `04_python/03_salidas_frente_candidata2.txt` |
| Web: mejoras, Interfaces, web completa | 81, 136, 114 | 81, 136, 114 | `05_web/01_*.txt` a `03_*.txt` |
| Compra en Edge (escritorio y móvil) | 139; 4 recibos y 4 pedidos pagados | Igual | `05_web/04_compra_edge.txt` |
| Reparto y login único con el portal | 29 y 82 | 29 y 82 | `05_web/05_*.txt` y `06_*.txt` |
| Ethereal real, sin red y sin respuesta | 16, 5 y 5 | 16, 5 y 5 | `05_web/07_*.txt` a `09_*.txt` |
| SO024 PROVISIONAL: 18 → Java → 15 → PSP → 16 → Python | PSP con código 0; un solo pedido en Python | Igual | `06_so024/` |
| Ventanas Swing (`ProbarVentanas`) | 76 / 0; sin conexión, 1 / 0 | Igual | `07_swing/` |
| Caso K: el dashboard en Edge, tres ciclos de 60 s sin tocarlo | 4 PASS | 4 PASS, con las mismas cifras (103 filas, 12 pedidos, 90 pares) | `08_caso_k/caso_k.txt` |

## Lo que no se ha repetido

- **El manual de instalación seguido desde un clon nuevo** (`../regresion-final/08_manual_instalacion/`). Sus rutas se actualizaron a las carpetas nuevas y se comprobaron una a una, pero el manual no se ha vuelto a seguir entero.
- **Lighthouse.** El último es del 11/11 (`01_Interfaces/evidencias/web/lighthouse/`).

## Cambios del código y pruebas de cada uno

Además de esta regresión final, cada parte se probó antes y después de su propio cambio:
- **Python:** las 265 pruebas y la comparación de las salidas después de cada grupo de cambios. También se comparó la consola, lo que publica el dashboard y los PNG con el pie fijo.
- **Web:** todas las pruebas de Edge, más las capturas y los estilos calculados de 126 estados de la página (42 por anchura).
- **Java, PSP y SQL:** todas las baterías y el bytecode compilado.

Los detalles están en el informe de la limpieza, que acompaña a la pull request.
