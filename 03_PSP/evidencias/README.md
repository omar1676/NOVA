# Evidencias de PSP: procesador auxiliar de pedidos Custom

Salidas reales del 10 de noviembre de 2026, con el **JDK 17.0.12** en Windows
11. No son capturas de pantalla: es el texto que escribieron los programas, sin
editar. Solo se han cambiado los finales de línea a LF y se han pasado a UTF-8.

**De dónde vienen los datos.** El CSV de entrada es
`03_PSP/datos/custom40_fabricacion_psp.csv`, que exportó
`02_Acceso_Datos/sql/15_exportar_fabricacion.sql` sobre la **base de PRUEBA** (no
la del equipo).

**Los programas.**

- **Los nuestros:** las clases de `03_PSP/` tal como están en esta rama.
- **El analizador de Álvaro:** `Psp.AnalizadorTallas`, compilado **sin cambios**
 desde su rama, la parte de Álvaro (sus archivos de PSP son los de su
  commit `6b7f4c1`). Se sacó con `git archive` a una carpeta temporal, porque
  ese día su rama todavía no estaba en la nuestra (se fusionó el 12/11, en
  `7715f83`, con esos mismos archivos).

**Las rutas.** Las ejecuciones se hicieron en una carpeta temporal, con rutas
relativas, para que no aparezcan rutas personales. En los comandos que se
muestran:

- `clases` son nuestras clases compiladas;
- `clases_alvaro` son las de Álvaro, compiladas aparte desde su rama.

En `03_PSP/README.md` se compila todo en una sola carpeta `clases`, que funciona
igual.

| Archivo | Qué muestra |
|---|---|
| `01_ejecucion_custom40.txt` | Ejecución completa del padre con CUSTOM-40: los tres pasos con su código de salida y su tiempo, la respuesta `OK;` de cada hijo, el control de que el validador y el analizador cuentan 40 pares, la ficha y el resultado final (código 0) |
| `ficha_taller_CUSTOM-40.txt` | La ficha auxiliar que guardó el padre en `salidas/` |
| `02_errores_controlados.txt` | Tres fallos controlados: archivo inexistente (código 1, no se lanza ningún hijo); cantidad 0 (el hijo 1 la rechaza, código 2, no se lanzan los pasos 2 y 3); el mismo pedido correcto sin el analizador de Álvaro en el classpath (el paso 2 falla, código 3, con el aviso de que hay que compilarlo) |
| `registro_psp.txt` | El registro que va acumulando el padre: un bloque por cada una de esas cuatro ejecuciones |
| `03_hijos_por_separado.txt` | Cada hijo lanzado solo con una tubería: lo que recibe por stdin, lo que devuelve por stdout y su código. Incluye un rechazo, con stdout vacío y el motivo en stderr |
| `04_resultado_pruebas.txt` | `PruebasPsp`: **27 de 27 superadas** (los 12 puntos pedidos, algunos con varios casos) |

## Qué cubre cada prueba de `04_resultado_pruebas.txt`

| Punto pedido | Pruebas |
|---|---|
| 1. Pedido Custom válido | 01 |
| 2. Varias tallas y cantidades | 02: nueve tallas (38 a 46), dos colores y una talla repetida |
| 3. Validación correcta | 03 |
| 4. Agrupación de tallas | 04 |
| 5. Generación de la ficha auxiliar | 05 |
| 6. Comunicación entre procesos | 06a (eco por stdin/stdout), 06b (personalización de dos líneas que cruza los tres procesos) |
| 7. Captura de stdout y stderr | 07 |
| 8. Códigos de salida | 08a, 08b |
| 9. Fallo controlado de un proceso | 09a (excepción), 09b (clase que no existe) y, en `02_errores_controlados.txt`, el analizador ausente |
| 10. Tiempo de espera agotado | 10: un hijo que duerme 60 s se cancela a los 2 s |
| 11. Archivo inexistente | 11 |
| 12. Datos mal formados | 12a a 12m: comilla sin cerrar, cabecera distinta, cantidad no numérica, 0 o negativa, falta la talla, falta el modelo, solo la cabecera, campos de menos, dos pedidos, talla 99 (la rechaza el paso 2), archivo vacío y formato `.json` |

## Lo que no está probado

- **El tiempo de espera dentro del padre completo.** Se ha probado en
  `GestorProcesos`, que es lo que usa el padre (prueba 10), pero no lanzando
  `ProcesadorPedidosCustom` con un hijo real que se cuelgue: ninguno de los tres
  hijos de verdad se cuelga.
- **Un pedido exportado de Odoo.** No hay ninguno: ver «Relación con PostgreSQL
  y Odoo» en `03_PSP/README.md`.

## Cómo repetirlas

Desde `03_PSP`, con los comandos de `03_PSP/README.md`:

- **Compilar:** incluido el analizador de Álvaro.
- **Ejecución correcta:**
  `java -cp clases ProcesadorPedidosCustom datos\custom40_fabricacion_psp.csv`
- **Rechazo:**
  `java -cp clases ProcesadorPedidosCustom datos\prueba_cantidad_cero.csv`
- **Pruebas:** `java -cp clases PruebasPsp`

Los tiempos de cada paso cambian de una ejecución a otra; el resto de la salida
es igual.
