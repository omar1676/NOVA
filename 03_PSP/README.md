# PSP — Procesador auxiliar de pedidos Custom

Parte de **Programación de Servicios y Procesos**, según el apartado 4.3 y el
anexo 13 del enunciado (Proyecto Intermodular v0.3).

Es una aplicación Java de consola que recibe la **exportación CSV de un pedido
Custom** y la procesa con **tres procesos hijos** lanzados con `ProcessBuilder`:
valida los datos, agrupa los pares por variante y talla, y prepara una **ficha
auxiliar para el taller**.

**Lo que no hace.** No escribe en PostgreSQL ni en Odoo, no toca el stock y no
crea la orden de fabricación. Solo lee una copia exportada del pedido y genera
archivos en `salidas/`.

## En resumen

| | |
|---|---|
| **Tecnologías** | Java 17 (`ProcessBuilder`, hilos para leer la salida de cada hijo, esperas con límite). Sin librerías |
| **Qué necesita** | JDK 17 |
| **Cómo se inicia** | Desde esta carpeta: `javac -encoding UTF-8 -d clases *.java pruebas\*.java src\Psp\*.java` y `java -cp clases ProcesadorPedidosCustom datos\custom40_fabricacion_psp.csv` |
| **Pruebas** | `java -cp clases PruebasPsp`: 27 de 27. `scripts/comprobar_psp.py` (raíz del repositorio) correcto en la regresión de cierre; corrección de Berme incorporada en `4f09742`, con su autoría |
| **Rúbrica** | IM §4.3 y anexo: 19 requisitos, 17 cumplidos; falta relacionar la ficha con el pedido de Odoo |
| **Conexión con otras asignaturas** | Lee el CSV que genera `02_Acceso_Datos/sql/15_exportar_fabricacion.sql`, con el formato de `03_PSP/memoria/DOCUMENTACION_PSP.md`. La ficha se demuestra con CUSTOM-40; SO024 es un ensayo provisional y no hay ficha acreditada de S00005 |
| **Evidencias y memoria** | `evidencias/` (ejecución de CUSTOM-40, errores controlados, hijos por separado, pruebas y SO024 provisional) y `memoria/DOCUMENTACION_PSP.md` |

## Las clases

| Clase | Qué es | Tarea del reparto | Qué hace |
|---|---|---|---|
| `ProcesadorPedidosCustom` | **proceso padre** | PSP-01 | Comprueba el archivo, lanza los tres hijos uno detrás de otro, les pasa los datos, mira sus códigos y respuestas, guarda la ficha y escribe el resumen |
| `GestorProcesos` | clase de apoyo del padre | PSP-05 | Lanza **un** hijo con `ProcessBuilder`, le escribe por stdin, recoge stdout y stderr por separado, espera con `waitFor` y lo cancela si tarda demasiado |
| `ValidadorPedidoCustom` | **hijo 1** | PSP-02 | Comprueba el CSV y devuelve los datos normalizados |
| `LectorCsv` | clase de apoyo del hijo 1 | — | Parte el CSV en registros respetando las comillas |
| `Psp.AnalizadorTallas` | **hijo 2**, de Álvaro | PSP-03 | Agrupa los pares por modelo + color + talla y por talla |
| `GeneradorFichaTaller` | **hijo 3** | PSP-04 | Comprueba que las cantidades cuadran y escribe la ficha |
| `pruebas/PruebasPsp` | pruebas | — | Las 27 pruebas, lanzando los programas de verdad |
| `pruebas/HijoDePrueba` | hijo solo para pruebas | — | Tarda, falla o devuelve un código raro a propósito |

`Psp.AnalizadorTallas` es la clase de Álvaro (`03_PSP/src/Psp/`).
**Se usa sin cambiarla**: el padre la lanza por su nombre
y el validador le prepara la entrada en el formato que ella ya leía.

## Cómo se comunican los procesos

Los datos pasan de un hijo al siguiente **a través del padre**, siempre por la
entrada y la salida estándar:

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
  salidas/ficha_taller_CUSTOM-40.txt   y   salidas/registro_psp.txt
```

Después de cada paso, el padre comprueba:

1. el **código de salida** (`waitFor` y `exitValue`);
2. que la respuesta empiece por **`OK;`** y hable **del mismo pedido**;
3. que **las cuentas cuadren**: el total de pares del analizador tiene que ser
   el mismo que el del validador.

Si algo falla, **no lanza el paso siguiente**.

### Qué recibe y qué devuelve cada hijo

**Hijo 1 — `ValidadorPedidoCustom`.** Recibe el CSV entero por stdin. Si está
bien, devuelve por stdout:

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

Si una personalización ocupa varias líneas, sale una línea `PERSONALIZACION`
por cada una, para que no se pierda texto.

**Hijo 2 — `Psp.AnalizadorTallas` (Álvaro).** Recibe el bloque `PEDIDO …
FIN` y devuelve:

```
OK;CUSTOM-40
VARIANTE_TALLA;NOVA Velocity;Rojo;40;10             <- modelo;color;talla;pares
...
TALLA;40;10                                         <- talla;pares
...
TOTAL;40
```

**Hijo 3 — `GeneradorFichaTaller`.** Recibe `PEDIDO`, `ORIGEN` (el nombre del
archivo exportado), `CLIENTE`, `PERSONALIZACION`, las líneas del analizador y
`FIN`. Comprueba que el total, la suma por variante y la suma por talla sean
iguales, y devuelve `OK;CUSTOM-40` seguido de la ficha. El padre la guarda en
`salidas/ficha_taller_<referencia>.txt`. Hay un ejemplo en
`evidencias/ficha_taller_CUSTOM-40.txt`.

**Si un hijo rechaza los datos,** no escribe nada por stdout, escribe
`ERROR;motivo` por stderr y termina con **código 2**. Es el formato del ejemplo
del profesor `EstadisticasHijo2.java`, y Álvaro usa el mismo código 2.

### Por qué `GestorProcesos` usa tres hilos

Las tres tuberías de un hijo (entrada, salida y error) tienen un tamaño
limitado. Si una se llena, quien escribe se queda bloqueado: el padre al
enviarle datos que no lee, o el hijo al escribir algo que nadie recoge.

Por eso hay **un hilo por tubería**, y el hilo principal solo hace
`waitFor(10 s)`:

```
hilo escritor       -> escribe los datos en la entrada del hijo y la cierra
hilo lector salida  -> guarda la salida del hijo en una lista
hilo lector error   -> guarda la salida de error en otra lista
hilo principal      -> waitFor(10 segundos) y, si no termina, lo cancela
```

- **Sin sincronizar nada:** cada hilo escribe en **su** lista, y el principal
  no las lee hasta después de `join()`.
- **Cancelación:** si el hijo no termina, primero `destroy()` y, si en un
  segundo sigue vivo, `destroyForcibly()`.
- **Origen:** es el mismo diseño que ya tenía `LanzadorValidacion.ejecutarHijo()`
  (8 de noviembre). Allí se midió que sin estos hilos el programa se colgaba
  con un CSV de 6 MB o con un hijo que escribía mucho.

## Códigos de salida

| Código | Padre (`ProcesadorPedidosCustom`) | Hijos |
|---|---|---|
| 0 | Correcto: ficha generada | Correcto |
| 1 | Problema con un archivo: el de entrada (no se lanza ningún hijo) o al guardar | Java no encuentra la clase o hay una excepción sin capturar |
| 2 | Un hijo ha rechazado los datos del pedido | Datos incorrectos (`ERROR;motivo`) |
| 3 | Un hijo ha fallado: no arranca, código inesperado, tiempo agotado, respuesta no válida o cuentas que no cuadran | Error inesperado (solo el de Álvaro) |

`GestorProcesos` usa dos valores propios, porque en esos casos el hijo no da
código: **-1** si no se ha podido arrancar y **-2** si se ha cancelado por
tiempo.

## Errores que se controlan

| Situación | Quién lo detecta | Código del padre |
|---|---|---|
| Falta el argumento, el archivo no existe, no es `.csv`, está vacío o no es UTF-8 | padre, antes de lanzar nada | 1 |
| CSV mal formado (comilla sin cerrar, texto pegado a una comilla…) | hijo 1 (`LectorCsv`) | 2 |
| Cabecera distinta o registro con un número de campos distinto de 8 | hijo 1 | 2 |
| Falta la referencia, el SKU, el cliente, el modelo, el color, la talla o la cantidad | hijo 1 | 2 |
| Talla o cantidad que no es un entero, o cantidad ≤ 0 | hijo 1 | 2 |
| Dos pedidos o dos clientes en el mismo archivo | hijo 1 | 2 |
| Talla fuera de 20–55 | hijo 2 (regla de Álvaro) | 2 |
| Las cantidades no cuadran entre los procesos | padre o hijo 3 | 3 o 2 |
| Un hijo no arranca, no se encuentra su clase o termina con un código inesperado | padre | 3 |
| Un hijo tarda más de 10 segundos | `GestorProcesos`, que lo cancela | 3 |

Pase lo que pase, el padre termina con una línea `Resultado: …` y añade el
resumen al final de `salidas/registro_psp.txt`.

## Cómo ejecutarlo en Windows con JDK 17

Probado con el **JDK 17.0.12**, sin Maven ni librerías. En este ordenador `javac`
y `java` no están en el PATH, así que se usa la ruta de `JAVA_HOME`. Las
carpetas `clases/` y `salidas/` no se suben al repositorio (`.gitignore`).

### 1. El analizador de Álvaro

Ya está integrado, con su autoría, en `src/Psp`: no hace falta sacarlo de su rama.

### 2. Compilar

Desde esta carpeta (`03_PSP`), todo en la carpeta `clases`:

```powershell
& "$env:JAVA_HOME\bin\javac.exe" -encoding UTF-8 -d clases *.java pruebas\*.java src\Psp\*.java
```

### 3. Procesar el pedido

```powershell
& "$env:JAVA_HOME\bin\java.exe" -cp clases ProcesadorPedidosCustom datos\custom40_fabricacion_psp.csv
type salidas\ficha_taller_CUSTOM-40.txt
```

Para ver un fallo controlado:

```powershell
& "$env:JAVA_HOME\bin\java.exe" -cp clases ProcesadorPedidosCustom datos\prueba_cantidad_cero.csv
```

### 4. Pruebas

```powershell
& "$env:JAVA_HOME\bin\java.exe" -cp clases PruebasPsp
```

Trabajan en una carpeta temporal nueva y no tocan el repositorio. La última
ejecución está en `evidencias/04_resultado_pruebas.txt` y la de la
regresión final del 13/11.

**Sin `-Dfile.encoding=UTF-8`:** con esa opción, las pruebas comparan textos
con tildes en otro juego de caracteres y fallan. Se lanzan tal cual, como arriba.

### Cada hijo, suelto

Se puede probar cada hijo con una tubería:

```powershell
Get-Content datos\custom40_fabricacion_psp.csv | & "$env:JAVA_HOME\bin\java.exe" -cp clases ValidadorPedidoCustom
```

Hay ejemplos de los tres en `evidencias/03_hijos_por_separado.txt`.

## Los datos de entrada

**`datos/custom40_fabricacion_psp.csv`** es una copia sin cambios del CSV que
genera `02_Acceso_Datos/sql/15_exportar_fabricacion.sql`. Se generó el 9 de
noviembre sobre la **base de PRUEBA**, no sobre la del equipo.

- **Columnas:** `referencia, sku, cliente, modelo, color, personalizacion,
  talla, cantidad`.
- **Contenido:** el pedido CUSTOM-40, que está *confirmado*: Club Atletico NOVA,
  NOVA Velocity en rojo, tallas 40 a 43 con 10 pares cada una, 40 pares en
  total.

**`datos/prueba_cantidad_cero.csv`** es un pedido de prueba con un error a
propósito, para enseñar un rechazo.

Para exportarlo de nuevo, siempre sobre una base de prueba:

```
psql -U postgres -d nova_sneakers -f ..\02_Acceso_Datos\sql\15_exportar_fabricacion.sql
```

El script deja `fabricacion_psp.csv` en la carpeta desde la que se lanza.

## Relación con PostgreSQL y Odoo

- **PostgreSQL** es de donde sale hoy el CSV, con el script 15. PSP solo lo
  **lee**: no se conecta a la base.
- **Odoo** lleva la venta y la fabricación de verdad. PSP no se conecta a Odoo.
  La ficha dice expresamente que **no sustituye a la orden de fabricación de
  Odoo**.
- **Cómo se relaciona el resultado con el pedido original.** Por la
  **referencia**, que se conserva de principio a fin:
  - en el CSV y en cada respuesta `OK;CUSTOM-40`;
  - en el nombre de la ficha y dentro de ella;
  - en el registro, junto con el nombre del archivo de origen.
- **Límite de Odoo.** S00005 del Club Atlético NOVA es el caso documentado en el PDF de Berme. No hay CSV ni ficha acreditados de S00005 en PSP. CUSTOM-40 y el ensayo SO024 PROVISIONAL conservan sus resultados, pero no prueban esa venta. SO024 es el ejemplo del enunciado; no hay que crear un pedido oficial con ese nombre. La relación con una exportación real de Odoo sigue sin demostrarse. Ver `..md`.

## La versión anterior: `LanzadorValidacion` y `AnalizadorTallas`

Del 8 de noviembre (commit `f5426cb`). `LanzadorValidacion` lanza el validador
y el `AnalizadorTallas` de la raíz, que solo agrupa por talla y lee el CSV
directamente.

- **Siguen funcionando:** el validador mantiene su primera línea
  `OK;referencia;líneas;pares`, que es la que ellos leen.
- **No forman parte del coordinador:** se usa el analizador de Álvaro, que ya
  agrupa por variante y por talla, para no tener dos versiones de la misma
  tarea.
- **Qué hacer con ellos:** queda por decidir entre los tres si se quedan como
  ejemplo o se quitan. No se ha borrado nada.

## Integración con el trabajo de Álvaro

- **Qué se usa:** `Psp.AnalizadorTallas`, sin ningún cambio, como hijo 2. Se
  sigue su formato de entrada (`PEDIDO / LINEA / FIN`) y su convenio de
  códigos (0 correcto, 2 datos incorrectos, 3 error inesperado).
- **Qué no se usa:**
  - `LanzadorAnalizador` y `ResultadoProceso`: el padre usa `GestorProcesos`
    (PSP-05);
  - `PruebasAnalizador`: sigue siendo su prueba del analizador y da 8 de 8.
- **Qué debería revisar Álvaro en `LanzadorAnalizador`:**
  - **El tiempo de espera no llega a actuar.** Lee la salida con
    `readAllBytes()` antes del `waitFor(10 s)`, y `readAllBytes()` espera a que
    el hijo termine.
  - **Medido el 10 de noviembre:** con un hijo que tarda 20 segundos, el
    lanzador esperó 20,1 s y devolvió código 0 en vez de `SIN_RESPUESTA`.
  - **Riesgo de bloqueo:** también puede bloquearse si el hijo escribe mucho
    por stderr, porque lee primero toda la salida y después los errores.
  - **No se ha cambiado su archivo:** es una propuesta para que la revise él.
- **Cómo está integrado:** su rama se fusionó en el commit `492c4e8` (12/11),
  así que su autoría sigue en su commit `e71947e`. Sus archivos no se han
  copiado a mano: son idénticos a los de ese commit.

## Autoría

- **Commit `f5426cb`** (Omar, 8 de noviembre): `ValidadorPedidoCustom`,
  `LectorCsv`, `LanzadorValidacion` y el `AnalizadorTallas` de la raíz.
- **Commit `e71947e`** (Álvaro, 9 de noviembre), en su rama, fusionada en
  `492c4e8`: `03_PSP/src/Psp/`.
- **Commit `9dc66ac`** (Omar, 11 de noviembre; preparado el 10 en su rama):
  - nuevos: `ProcesadorPedidosCustom`, `GestorProcesos`,
    `GeneradorFichaTaller`, `pruebas/` y `datos/`;
  - cambios en `ValidadorPedidoCustom`: datos normalizados, comprobación de
    datos que faltan y salida en UTF-8.

- **Pendiente de acordar:** en el reparto, PSP-01 (`ProcesadorPedidosCustom`) y
  PSP-04 (`GeneradorFichaTaller`) eran de Berme. Estas dos clases las subió
  Omar en el commit `9dc66ac`. En su rama, Berme subió
  `scripts/comprobar_psp.py` (commit `f1983d2`), que compila y comprueba
  `ValidadorPedidoCustom`, `LanzadorValidacion` y las pruebas del paquete
 `Psp`, e `03_PSP/memoria/DOCUMENTACION_PSP.md` (commit `0f7d27d`), que
  describe los dos formatos de entrada. Hay que decidir entre los tres quién
  revisa y defiende cada clase.

## Ejemplos del profesor utilizados

- **`mini_reto_1_lanzador_estadisticas`:**
  - el protocolo `OK;…` por stdout y `ERROR;…` por stderr con
    `System.exit(2)` (`EstadisticasHijo2.java`);
  - construir el comando con `java.home` y el classpath del propio programa;
  - comprobar que la respuesta empieza por `OK;` antes de usarla
    (`LanzadorEstadisticas.java`).
- **`UD2 IPC y sincronizacion/EG1_PipelineTexto`:** el hijo que lee su entrada
  estándar con un `BufferedReader` sobre `System.in`.
- **`UD1_ejemplo_guiado_clase/LanzadorProcesoFinal2.java`:** la espera con
  límite `waitFor(n, TimeUnit.SECONDS)` y `destroyForcibly()`.

**Qué es distinto de los ejemplos:**

- **Los datos van por stdin y no como argumentos,** porque un CSV entero no cabe
  cómodamente en la línea de órdenes.
- **Los hilos de `GestorProcesos`.** Los ejemplos del profesor no usan hilos;
  aquí hicieron falta para que el tiempo de espera funcione aunque el hijo no
  lea o escriba mucho (ver arriba).

## Límites conocidos

- **Solo CSV:** un `.json` se rechaza con código 1.
- **Un pedido por archivo.** Procesar varios a la vez sería la «ampliación
  posterior» del enunciado y no se ha hecho.
- **Lectura del CSV:** no se admiten separadores distintos de la coma, y un
  retorno de carro suelto fuera de comillas se rechaza.
- **Memoria:** el padre guarda en memoria todo lo que escribe cada hijo, sin
  tope.
- **Orden de la ficha:** las filas por modelo, color y talla salen en el orden
  del archivo (así las devuelve el analizador); las de talla, ordenadas.
