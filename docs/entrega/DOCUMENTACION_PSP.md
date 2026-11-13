# NOVA Sneakers · Documentación del subsistema PSP

Programación de Servicios y Procesos (módulo 0490). Es el punto 5 de la memoria («Diseño del subsistema auxiliar PSP: procesos, entradas/salidas, comunicación, códigos de retorno, gestión de errores y relación con los datos exportados de Odoo», IM-COM-25), ampliado.

**Convenciones.** Rutas relativas a la raíz del repositorio, casi todas en `psp/`. Los IDs IM-PSP-xx son los de la matriz de requisitos de `docs/entrega/MATRIZ_RUBRICAS.md`, donde está el estado de cada uno (§2.3). Marcas: **[PENDIENTE (quién): …]** es trabajo que falta de verdad; **[POR DECIDIR (los tres): …]**, una decisión del equipo; **[DUDA PARA EL PROFESOR (Dn): …]**, una pregunta de la lista de dudas de la matriz; **[REVISIÓN (…) en la PR: …]**, algo que tiene que mirar un compañero al revisar la pull request.

**Versión:** rama `integracion/candidata-2`, código de `8cdc08c` (13/11/2026). PSP no ha cambiado desde la candidata publicada el 12/11 (`4203fe7`); lo nuevo son sus pruebas del 13/11 y la evidencia de SO024 provisional.

---

## 1. Qué es y qué no es

Una **aplicación Java de consola** que recibe la **exportación CSV de un pedido Custom** y la procesa con **tres procesos hijos** lanzados con `ProcessBuilder`: valida los datos, agrupa los pares por variante y talla, y prepara una **ficha auxiliar para el taller** (`psp/README.md`).

**Lo que no hace** (IM-PSP-05 y 15): no escribe en PostgreSQL ni en Odoo, no toca el stock y no crea la orden de fabricación. Solo lee una copia exportada del pedido y genera archivos en `salidas/`. La propia ficha lo dice al final: «Documento auxiliar generado por PSP a partir de una exportación del pedido. No sustituye a la orden de fabricación de Odoo».

---

## 2. Procesos y clases

| Clase | Papel | Tarea del reparto | Qué hace |
|---|---|---|---|
| `ProcesadorPedidosCustom` | **Proceso padre (coordinador)** | PSP-01 | Comprueba el archivo, lanza los tres hijos uno detrás de otro, les pasa los datos, mira sus códigos y sus respuestas, guarda la ficha y escribe el resumen |
| `GestorProcesos` | Apoyo del padre | PSP-05 | Lanza **un** hijo con `ProcessBuilder`, le escribe por stdin, recoge stdout y stderr por separado, espera con `waitFor` y lo cancela si tarda demasiado |
| `ValidadorPedidoCustom` | **Hijo 1** | PSP-02 | Comprueba el CSV y devuelve los datos normalizados |
| `LectorCsv` | Apoyo del hijo 1 | — | Parte el CSV en registros respetando las comillas (un campo puede tener comas, comillas y saltos de línea) |
| `Psp.AnalizadorTallas` (de Álvaro, `psp/src/Psp/`) | **Hijo 2** | PSP-03 | Agrupa los pares por modelo + color + talla y por talla |
| `GeneradorFichaTaller` | **Hijo 3** | PSP-04 | Comprueba que las cantidades cuadran y escribe la ficha |
| `pruebas/PruebasPsp` | Pruebas | — | Las 27 pruebas, lanzando los programas de verdad |
| `pruebas/HijoDePrueba` | Hijo solo para pruebas | — | Tarda, falla o devuelve un código raro a propósito |

Cada hijo se lanza en **otra máquina virtual de Java**, con el comando que se construye con `java.home` y el classpath del propio padre (`GestorProcesos.java`, líneas 84–87):

```java
String java = Path.of(System.getProperty("java.home"), "bin", "java").toString();
String classpath = System.getProperty("java.class.path");
ProcessBuilder pb = new ProcessBuilder(java, "-cp", classpath, clase);
```

---

## 3. Entradas y salidas

### 3.1 Entrada

Un archivo `.csv` en UTF-8, separado por comas, con **esta cabecera exacta** y una fila por línea de pedido (`integracion/contrato-fabricacion.md`):

```
referencia,sku,cliente,modelo,color,personalizacion,talla,cantidad
```

| Columna | Qué es |
|---|---|
| `referencia` | El pedido (`CUSTOM-40`, `SO024`): la clave que relaciona todo |
| `sku` | La referencia exacta de inventario (`NOVA-<variante>-<talla>`) |
| `cliente` | Para quién se fabrica |
| `modelo`, `color` | Qué zapatilla y en qué color |
| `personalizacion` | Qué hay que personalizar (puede tener varias líneas) |
| `talla`, `cantidad` | Cuántos pares de cada talla |

**Un pedido por archivo.** Hoy el CSV lo genera PostgreSQL con `acceso-datos/sql/15_exportar_fabricacion.sql` (§9). Los datos de ejemplo están en `psp/datos/`: `custom40_fabricacion_psp.csv` (copia sin cambios del que exportó el 15 sobre la base de PRUEBA el 9/11) y `prueba_cantidad_cero.csv` (con un error a propósito).

### 3.2 Salidas

| Salida | Qué contiene |
|---|---|
| Consola | Cada paso con su código de salida, su tiempo y la respuesta del hijo, y una línea final `Resultado: …` |
| `salidas/ficha_taller_<referencia>.txt` | La ficha auxiliar: pedido, cliente, archivo de origen, personalización, pares por modelo, color y talla, pares por talla y total |
| `salidas/registro_psp.txt` | Un bloque por cada ejecución, **también las que fallan**, con la fecha, el archivo y el resultado de cada paso |
| Código de salida del padre | 0, 1, 2 o 3 (§6) |

Ejemplos reales de ficha: `pruebas/psp/ficha_taller_CUSTOM-40.txt` y, con datos provisionales, `pruebas/psp/so024_provisional/ficha_taller_SO024_PROVISIONAL.txt`.

---

## 4. El protocolo `OK;` / `ERROR;`

Lo toma del ejemplo del profesor `EstadisticasHijo2.java` (`psp/README.md`, «Ejemplos del profesor utilizados»):

- **Si todo va bien**, el hijo escribe por **stdout** una primera línea que empieza por `OK;` y habla del mismo pedido, seguida de sus datos, y termina con código **0**.
- **Si rechaza los datos**, no escribe nada por stdout, escribe **`ERROR;motivo`** por **stderr** y termina con código **2**.

Cada hijo, con el pedido CUSTOM-40 (`psp/README.md`, «Qué recibe y qué devuelve cada hijo»):

**Hijo 1 · `ValidadorPedidoCustom`.** Recibe el CSV entero por stdin y devuelve:

```
OK;CUSTOM-40;4;40                                   <- referencia, líneas, pares
CLIENTE;Club Atletico NOVA
PERSONALIZACION;Club Atletico NOVA: logo bordado y numeracion en el talon
PEDIDO;CUSTOM-40
LINEA;NOVA-4-40;NOVA Velocity;Rojo;40;10            <- sku;modelo;color;talla;cantidad
LINEA;NOVA-4-41;NOVA Velocity;Rojo;41;10
LINEA;NOVA-4-42;NOVA Velocity;Rojo;42;10
LINEA;NOVA-4-43;NOVA Velocity;Rojo;43;10
FIN
```

**Hijo 2 · `Psp.AnalizadorTallas`.** Recibe el bloque `PEDIDO … FIN` (el formato que ya leía la clase de Álvaro) y devuelve:

```
OK;CUSTOM-40
VARIANTE_TALLA;NOVA Velocity;Rojo;40;10             <- modelo;color;talla;pares
...
TALLA;40;10                                         <- talla;pares
...
TOTAL;40
```

**Hijo 3 · `GeneradorFichaTaller`.** Recibe `PEDIDO`, `ORIGEN` (el nombre del archivo exportado), `CLIENTE`, `PERSONALIZACION`, las líneas del analizador y `FIN`. Comprueba que el total, la suma por variante y la suma por talla son iguales, y devuelve `OK;CUSTOM-40` seguido de la ficha.

**Lo que comprueba el padre después de cada paso:**

1. el **código de salida** (`waitFor` y `exitValue`);
2. que la respuesta empiece por **`OK;`** y hable **del mismo pedido**;
3. que **las cuentas cuadren**: el total del analizador tiene que ser el del validador.

**Si algo falla, no lanza el paso siguiente** y termina con el código que corresponde (§6).

---

## 5. Comunicación entre procesos

```
                         CSV del pedido
                               |
                               v
  ProcesadorPedidosCustom --stdin--> ValidadorPedidoCustom      (hijo 1)
                          <--stdout-- OK;... + datos normalizados
                          <--stderr-- ERROR;motivo
          |
          | el padre separa el bloque PEDIDO / LINEA / FIN
          v
  ProcesadorPedidosCustom --stdin--> Psp.AnalizadorTallas       (hijo 2)
                          <--stdout-- OK;... + VARIANTE_TALLA / TALLA / TOTAL
          |
          | el padre añade cliente y personalización
          v
  ProcesadorPedidosCustom --stdin--> GeneradorFichaTaller       (hijo 3)
                          <--stdout-- OK;... + la ficha
          |
          v
  salidas/ficha_taller_<referencia>.txt   y   salidas/registro_psp.txt
```

(`psp/README.md`, «Cómo se comunican los procesos».)

- **Los datos van por stdin y no como argumentos**, porque un CSV entero no cabe cómodamente en la línea de órdenes.
- **Los hijos no se hablan entre ellos:** todo pasa por el padre, que decide si el flujo continúa (IM-PSP-19).
- **Una personalización de varias líneas no se pierde:** el validador saca una línea `PERSONALIZACION` por cada una, y la prueba 06b comprueba que cruza los tres procesos con su coma y sus comillas.

### 5.1 Por qué `GestorProcesos` usa tres hilos

Las tres tuberías de un hijo (entrada, salida y error) tienen un tamaño limitado. Si una se llena, quien escribe se queda bloqueado: el padre, al enviar datos que el hijo no lee; o el hijo, al escribir algo que nadie recoge. Por eso hay un hilo por tubería, y el principal solo espera (`psp/README.md`):

```
hilo escritor       -> escribe los datos en la entrada del hijo y la cierra
hilo lector salida  -> guarda la salida del hijo en una lista
hilo lector error   -> guarda la salida de error en otra lista
hilo principal      -> waitFor(10 segundos) y, si no termina, lo cancela
```

- **Lectura diferenciada de stdout y stderr** (IM-PSP-25): cada una va a su lista. Prueba 07: `stdout [OK;salida] / stderr [AVISO;esto va por stderr]`.
- **Sin sincronizar nada:** cada hilo escribe en **su** lista, y el hilo principal no las lee hasta después de `join()`.
- **Origen:** el mismo diseño de `LanzadorValidacion.ejecutarHijo()` (8/11). Allí se midió que, sin estos hilos, el programa se colgaba con un CSV de 6 MB o con un hijo que escribía mucho.

La «sincronización» que pide el RA1 se hace aquí esperando con `waitFor` a cada hijo antes de lanzar el siguiente. Varios pedidos a la vez y un recurso compartido protegido son la ampliación posterior (IM-PSP-12 y 30), y no están hechos. **[DUDA PARA EL PROFESOR (D9): ¿la sincronización del RA1 obliga a usar hilos?]**

---

## 6. Códigos de salida (IM-PSP-09 y 26)

| Código | Padre (`ProcesadorPedidosCustom`) | Hijos |
|---|---|---|
| **0** | Correcto: ficha generada | Correcto |
| **1** | Problema con un archivo: el de entrada (no se lanza ningún hijo) o al guardar | Java no encuentra la clase o hay una excepción sin capturar |
| **2** | Un hijo ha rechazado los datos del pedido | Datos incorrectos (`ERROR;motivo`) |
| **3** | Un hijo ha fallado: no arranca, código inesperado, tiempo agotado, respuesta no válida o cuentas que no cuadran | Error inesperado (solo el de Álvaro) |

`GestorProcesos` usa dos valores propios cuando el hijo no llega a dar código: **−1** si no se ha podido arrancar y **−2** (`TIEMPO_AGOTADO`) si se ha cancelado por tiempo.

**Por qué así:** separar «el archivo está mal» (1), «los datos del pedido están mal» (2) y «un programa ha fallado» (3) permite saber, solo con el código, si hay que corregir la exportación o el código. Es el mismo convenio que usa Álvaro en su analizador (0 correcto, 2 datos incorrectos, 3 error inesperado).

---

## 7. Tiempos de espera (IM-PSP-27)

- El padre da a cada hijo **10 segundos** (`SEGUNDOS_MAXIMOS = 10` en `ProcesadorPedidosCustom.java`).
- `GestorProcesos` espera con `proceso.waitFor(segundosMaximos, TimeUnit.SECONDS)`. Si el hijo no ha terminado, le pide que acabe con `destroy()`; si en un segundo sigue vivo, lo mata con `destroyForcibly()` y espera a que muera (`GestorProcesos.java`, líneas 138–152).
- El resultado es `TIEMPO_AGOTADO` (−2) y el padre termina con código 3.
- **Prueba 10 (13/11):** un hijo que duerme 60 s se cancela a los 2 s (en la prueba el límite es 2): código −2 en 2,0 s en lugar de 60 (`pruebas/regresion-final/02_java_psp/04_psp_pruebas.txt`).
- **Lo que no está probado:** el tiempo agotado dentro del padre completo con un hijo real que se cuelgue, porque ninguno de los tres hijos se cuelga (`pruebas/psp/README.md`, «Lo que no está probado»).

---

## 8. Errores que se controlan

| Situación | Quién la detecta | Código del padre |
|---|---|---|
| Falta el argumento, el archivo no existe, no es `.csv`, está vacío o no es UTF-8 | El padre, antes de lanzar nada | 1 |
| CSV mal formado (comilla sin cerrar, texto pegado a una comilla…) | Hijo 1 (`LectorCsv`) | 2 |
| Cabecera distinta o un registro sin 8 campos | Hijo 1 | 2 |
| Falta la referencia, el SKU, el cliente, el modelo, el color, la talla o la cantidad | Hijo 1 | 2 |
| Talla o cantidad que no es un entero, o cantidad ≤ 0 | Hijo 1 | 2 |
| Dos pedidos o dos clientes en el mismo archivo | Hijo 1 | 2 |
| Talla fuera de 20–55 | Hijo 2 (regla de Álvaro) | 2 |
| Las cantidades no cuadran entre los procesos | El padre o el hijo 3 | 3 o 2 |
| Un hijo no arranca, no se encuentra su clase o termina con un código inesperado | El padre | 3 |
| Un hijo tarda más de 10 segundos | `GestorProcesos`, que lo cancela | 3 |

Pase lo que pase, el padre termina con una línea `Resultado: …` y añade el resumen al final de `registro_psp.txt`. Dos fallos controlados repetidos el 13/11 sobre el árbol final (`pruebas/regresion-final/02_java_psp/06_psp_error_no_existe.txt` y `06_psp_error_cantidad_cero.txt`):

```
Resultado: ERROR EN EL ARCHIVO (codigo 1). No existe el archivo: datos\no_existe.csv

Paso 1 ValidadorPedidoCustom: codigo 2 en 0,35 s
  ERROR;La cantidad del registro 2 tiene que ser mayor que cero, y es 0
Resultado: PEDIDO RECHAZADO (codigo 2). El paso 1 ha rechazado los datos del pedido
```

El tercer fallo controlado, el mismo pedido correcto **sin** el analizador de Álvaro en el classpath (el paso 2 falla y el padre termina con código 3 y el aviso de que hay que compilarlo), está en `pruebas/psp/02_errores_controlados.txt` (10/11).

---

## 9. Relación con la exportación del pedido (script 15) y con SO024

### 9.1 Cómo se genera la entrada

`acceso-datos/sql/15_exportar_fabricacion.sql` lee el pedido **guardado** en PostgreSQL. Antes de escribir comprueba que existe, que está **confirmado** y que suma exactamente 40 pares; si algo falla, psql se para con un código de error y el CSV anterior queda intacto (`acceso-datos/documentacion/README.md` §14, «Cómo se genera `fabricacion_psp.csv`»). Por defecto exporta `CUSTOM-40`; con `-v referencia=SO024`, otro pedido:

```
psql -U postgres -d nova_sneakers -v referencia=SO024 -f acceso-datos\sql\15_exportar_fabricacion.sql
```

El archivo siempre se llama `fabricacion_psp.csv` y queda en la carpeta desde la que se lanza psql. Se exporta con `\copy` porque `\o` cambiaba en Windows los saltos de línea de dentro de un campo; se comprobó que una personalización con salto de línea llega a PSP con los mismos bytes.

Siguiendo el manual de instalación sobre un clon nuevo (13/11), PSP procesó con código 0 tanto el CSV de ejemplo de `psp/datos/` como el que acababa de exportar el 15 (`pruebas/regresion-final/08_manual_instalacion/`).

### 9.2 SO024 con datos PROVISIONALES, de principio a fin (13/11)

Sobre el árbol final y una base desechable con los 23 scripts (`pruebas/regresion-final/06_so024_provisional/00_cadena.txt`; evidencia completa de PSP, rotulada PROVISIONAL, en `pruebas/psp/so024_provisional/`):

1. El script 18 cargó Runner X con el color «PROVISIONAL», 99,90 € y 10 pares por talla, y los métodos Java de la pestaña «Nuevo pedido» crearon y confirmaron SO024 con el reparto inventado 2/3/5/6/7/6/5/4/2 de la talla 38 a la 46: 9 líneas, 40 pares y 3.996,00 €.
2. El 15 exportó **9 filas y 40 pares**, con sus dos comprobaciones en PASS.
3. PSP: `Paso 1 … codigo 0` → `OK;SO024;9;40`; `Paso 2 … codigo 0` → `9 combinaciones de modelo, color y talla; 9 tallas; 40 pares`; `Paso 3 … codigo 0`; `Resultado: CORRECTO (codigo 0). Pedido SO024 procesado` (`03_psp.txt`).
4. Ficha: `ficha_taller_SO024_PROVISIONAL.txt`, con el cliente Club Halcones, la personalización «PROVISIONAL: escudo del Club Halcones en el lateral» y los pares por talla.
5. La cadena sigue después de PSP: el 16 exporta los cinco CSV y, en Python, SO024 es un solo pedido de 9 líneas y 40 pares.

**[PENDIENTE (los tres): acordar los 7 datos de SO024 y repetir la cadena con el pedido creado desde la ventana Java en la base del equipo (`SO024_DATOS_PENDIENTES.md`).]**

### 9.3 Relación con el pedido de Odoo (IM-PSP-10, 14 y 29)

- **Cómo se relaciona hoy:** por la **referencia**, que se conserva de principio a fin: en el CSV, en cada respuesta `OK;SO024`, en el nombre de la ficha y dentro de ella, y en `registro_psp.txt` junto con el nombre del archivo de origen.
- **Qué falta:** el pedido de verdad en Odoo. Hoy **no hay ninguna exportación de Odoo**. Cuando Berme tenga SO024 en Odoo hay dos caminos (`psp/README.md`, «Relación con PostgreSQL y Odoo»):
  1. exportar sus líneas desde Odoo a un CSV con estas mismas 8 columnas, y PSP lo procesa **sin cambiar nada**;
  2. o que la «Referencia del cliente» del pedido de Odoo sea `SO024` y la «Referencia interna» de cada variante sea el SKU de PostgreSQL, y apuntar en la ficha o en la memoria la correspondencia con el número que dé Odoo (`integracion/recorrido-manual-odoo.md`).
- El conector de Odoo de Berme que hay en el servidor (`servidor-admin/odoo.js`) está desactivado y no se ha probado contra ningún Odoo; PSP no lo usa.
- **[PENDIENTE (Berme): exportación CSV del pedido desde Odoo y la tabla de equivalencias de número de pedido y SKU. Sin ella, IM-PSP-10 e IM-PSP-29 quedan parciales.]**

---

## 10. Pruebas: 27 de 27

`java -cp clases PruebasPsp`. Trabajan en una carpeta temporal nueva y no tocan el repositorio. Resultado: **27 de 27** el 13/11 a las 01:02, sobre el árbol final exportado con `git archive` y con el analizador de Álvaro dentro del árbol (`pruebas/regresion-final/02_java_psp/04_psp_pruebas.txt`), y otra vez a las 01:20 siguiendo el manual sobre un clon nuevo (`pruebas/regresion-final/08_manual_instalacion/`). El mismo día, CUSTOM-40 de principio a fin dio código 0 y una ficha igual a la de `pruebas/psp/ficha_taller_CUSTOM-40.txt` (sin contar las fechas).

| Punto | Prueba | Resultado |
|---|---|---|
| 1. Pedido Custom válido | 01 · CUSTOM-40 de principio a fin (exportación real del 15) | Código 0, «Pedido CUSTOM-40 procesado» |
| 2. Varias tallas | 02 · Nueve tallas (38 a 46), dos colores y una talla repetida (pedido de prueba) | 9 tallas; la 42 suma 6 + 2 + 4 = 12; total 40 |
| 3. Validación | 03 · El validador, solo | `OK;CUSTOM-40;4;40` |
| 4. Agrupación | 04 · Validador → analizador de Álvaro | Rojo 42 = 8; talla 42 = 12; total 40 |
| 5. Ficha | 05 · Ficha y registro | Ficha de 29 líneas y `registro_psp.txt` |
| 6. Comunicación | 06a · Lo que el padre envía por stdin vuelve igual por stdout | `OK;eco, uno, dos;tres, cuatro, con coma` |
| | 06b · Personalización de 2 líneas por los tres procesos | Llegan las dos líneas, con la coma y las comillas |
| 7. stdout y stderr | 07 · Cada uno a su lista | Separados |
| 8. Códigos de salida | 08a · Se recoge el código exacto del hijo | Código 7 |
| | 08b · El validador rechaza con 2, `ERROR;` por stderr y nada por stdout | Código 2 |
| 9. Fallo controlado | 09a · Un hijo que lanza una excepción / 09b · Una clase que no existe | Código 1 en los dos |
| 10. Tiempo agotado | 10 · Un hijo que no termina | Cancelado a los 2,0 s, código −2 |
| 11. Archivo inexistente | 11 · El padre avisa y no lanza ningún hijo | Código 1 |
| 12. Datos mal formados | 12a–12m · Comilla sin cerrar, cabecera distinta, cantidad no numérica, 0 o negativa, falta la talla, falta el modelo, solo la cabecera, campos de menos, dos pedidos, talla 99, archivo vacío y formato `.json` | Código 2 (o 1 en el vacío y el `.json`) y **ninguna ficha** |

Detalle de qué cubre cada una: `pruebas/psp/README.md`. Las salidas del 10/11 sin editar (ejecución completa, errores controlados, cada hijo por separado con una tubería y el registro) siguen en `pruebas/psp/`.

**Avisos:**

- `PruebasPsp` falla si se lanza con `-Dfile.encoding=UTF-8` (visto el 12/11 en la Fase 0); hay que lanzarla sin esa opción, con el comando de arriba. Lo avisan `psp/README.md` (apartado «Pruebas») y la tabla de problemas de `MANUAL_INSTALACION.md` §10.
- `scripts/comprobar_psp.py` (de Berme) **falla, y se sabe por qué** (13/11, `pruebas/regresion-final/02_java_psp/07_comprobar_psp.txt`): espera que el validador conteste solo `OK;CUSTOM-40;4;40`, y desde el commit `81db6e5` el validador añade después los datos normalizados. En `feature/berme` hay un commit suyo que lo adapta (`862e37d`, «fix(psp): adapt quick check to the validator's normalized output»), que no está en esta rama. **[REVISIÓN (Berme) en la PR: traer su arreglo `862e37d` de `comprobar_psp.py` en un commit suyo.]**

---

## 11. El analizador de Álvaro

- **Qué se usa:** `Psp.AnalizadorTallas` (`psp/src/Psp/`, de su commit `6b7f4c1` del 9/11), **sin ningún cambio**, como hijo 2. El padre lo lanza por su nombre y el validador le prepara la entrada en el formato que ya leía (`PEDIDO;referencia`, `LINEA;sku;modelo;color;talla;cantidad`, `FIN`). Se respeta su convenio de códigos.
- **Su regla propia:** acepta tallas de 20 a 55 y cantidades positivas (`integracion/contrato-fabricacion.md`, «Protocolo del paquete Psp»). Por eso la prueba 12k (talla 99) la acepta el validador y la rechaza el analizador en el paso 2.
- **Qué no se usa:** su `LanzadorAnalizador` y su `ResultadoProceso`, porque el padre usa `GestorProcesos`. Su `PruebasAnalizador` sigue siendo su prueba y da 8 de 8.
- **Lo que debería revisar Álvaro en `LanzadorAnalizador`** (`psp/README.md`, «Integración con el trabajo de Álvaro»): lee la salida con `readAllBytes()` antes del `waitFor(10 s)`, y `readAllBytes()` espera a que el hijo termine, así que el tiempo de espera no llega a actuar. Medido el 10/11: con un hijo que tarda 20 s, esperó 20,1 s y devolvió código 0. También puede bloquearse si el hijo escribe mucho por stderr. **No se ha cambiado su archivo.** **[REVISIÓN (Álvaro) en la PR: el tiempo de espera de su `LanzadorAnalizador`.]**

---

## 12. Cómo ejecutarlo

Desde `psp`, con el JDK 17 (probado con el 17.0.12). Si `javac` no está en el PATH, se usa `& "$env:JAVA_HOME\bin\javac.exe"`.

```
javac -encoding UTF-8 -d clases *.java pruebas\*.java src\Psp\*.java
java -cp clases ProcesadorPedidosCustom datos\custom40_fabricacion_psp.csv
type salidas\ficha_taller_CUSTOM-40.txt
java -cp clases ProcesadorPedidosCustom datos\prueba_cantidad_cero.csv
java -cp clases PruebasPsp
```

Un hijo suelto, con una tubería:

```
Get-Content datos\custom40_fabricacion_psp.csv | java -cp clases ValidadorPedidoCustom
```

Para SO024: generar el CSV con el 15 (§9.1) y pasárselo al padre. Detalle en `MANUAL_INSTALACION.md` §5 y `MANUAL_DEMOSTRACION.md`.

---

## 13. Límites conocidos

- **Solo CSV:** un `.json` se rechaza con código 1.
- **Un pedido por archivo:** procesar varios a la vez es la «ampliación posterior» del enunciado (IM-PSP-30).
- **Lectura del CSV:** solo coma como separador, y un retorno de carro suelto fuera de comillas se rechaza.
- **Memoria:** el padre guarda en memoria todo lo que escribe cada hijo, sin tope.
- **Orden de la ficha:** las filas por modelo, color y talla salen en el orden del archivo; las de talla, ordenadas.
- **La versión anterior** (`LanzadorValidacion` y el `AnalizadorTallas` de la raíz de `psp/`, del 8/11) sigue funcionando, pero no forma parte del coordinador. **[POR DECIDIR (los tres): si se quedan como ejemplo o se quitan.]**
- **`psp/README.md`** ya dice, en «Relación con PostgreSQL y Odoo», que SO024 solo se ha probado con datos PROVISIONALES (script 18, Java, 15 y PSP con código 0), y avisa de que `PruebasPsp` no se lanza con `-Dfile.encoding=UTF-8`.

---

## 14. Autoría

Lo que dice `psp/README.md` («Autoría») y lo que se ve en Git (rama `integracion/candidata-2`):

- Commit `f4847d4` (Omar, 8/11): `ValidadorPedidoCustom`, `LectorCsv`, `LanzadorValidacion` y el `AnalizadorTallas` de la raíz.
- Commit `6b7f4c1` (Álvaro, 9/11): `psp/src/Psp/`.
- Commit `81db6e5` (Omar, 11/11; preparado el 10/11 en su rama): `ProcesadorPedidosCustom`, `GestorProcesos`, `GeneradorFichaTaller`, `pruebas/` y `datos/`, y los cambios del validador. «Se prepararon en la sesión de Omar con ayuda de Claude.»
- En el reparto, PSP-01 (`ProcesadorPedidosCustom`) y PSP-04 (`GeneradorFichaTaller`) eran de Berme; las subió Omar en el commit `81db6e5`. Berme subió `scripts/comprobar_psp.py` (`b3b0d45`) e `integracion/contrato-fabricacion.md` (`f3dda07`).

**[PENDIENTE (los tres): el reparto real de PSP y quién revisa y defiende cada clase en la defensa.]**

| Clase | Quién la escribió | Quién la revisó | Quién la defiende |
|---|---|---|---|
| `ProcesadorPedidosCustom` | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| `GestorProcesos` | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| `ValidadorPedidoCustom` y `LectorCsv` | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| `Psp.AnalizadorTallas` | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| `GeneradorFichaTaller` | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
| `PruebasPsp` | [PENDIENTE] | [PENDIENTE] | [PENDIENTE] |
