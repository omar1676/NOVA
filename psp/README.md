# PSP — Validación y resumen del pedido Custom

Parte de **Programación de Servicios y Procesos** correspondiente a mi trabajo:
validar el pedido `CUSTOM-40` que sale de PostgreSQL y resumir sus cantidades
por talla, usando procesos y comunicación entre ellos.

**De dónde vienen los datos.** Del CSV que exporta
`acceso-datos/sql/15_exportar_fabricacion.sql`. **Hoy no vienen de Odoo**: el
ERP todavía no exporta nada. Cuando lo haga, solo habrá que cambiar el origen
del archivo.

**Lo que esto no es.** No es el `ProcesadorPedidosCustom` del enunciado, que es
el coordinador del equipo y encadenará también `GeneradorFichaTaller`. Aquí solo
están mis dos procesos y un lanzador que los prueba.

## Las tres clases

### `ValidadorPedidoCustom.java` — proceso hijo

Lee **toda** su entrada estándar y la pasa por `LectorCsv`, que le devuelve los
registros. Despues comprueba ocho cosas: que llega contenido, que la cabecera
trae las 8 columnas esperadas, que hay registros de pedido además de la
cabecera, que cada registro tiene 8 campos, que la referencia no está vacía, que
todos los registros son del mismo pedido, que la talla es un número positivo y
que la cantidad es un entero mayor que cero.

Lee la entrada de golpe con `readAllBytes()`, no línea a línea, porque un
registro puede ocupar varias líneas del archivo.

Si todo está bien escribe una línea en su **salida estándar** y termina con
código **0**:

```
OK;CUSTOM-40;4;40
   referencia  líneas  pares
```

Si algo falla escribe el motivo en su **salida de error** y termina con código
**2**:

```
ERROR;La cantidad de la linea 2 tiene que ser mayor que cero, y es -5
```

### `AnalizadorTallas.java` — proceso hijo

Lee el mismo CSV por su entrada estándar, también de golpe y con `LectorCsv`,
agrupa las cantidades por talla y escribe el resumen:

```
Talla 40: 10 pares
Talla 41: 10 pares
Talla 42: 10 pares
Talla 43: 10 pares
Total: 40 pares
```

Guarda los datos en **dos listas que van en paralelo**: en `tallas` la talla y
en `cantidades` sus pares, en la misma posición. Si una talla ya estaba, le suma;
si no, la añade al final. Al terminar ordena las dos listas de menor a mayor
talla, para que el resumen salga igual aunque el archivo venga desordenado.

**Ninguna cifra está escrita en el código**: todas se calculan sumando lo que
trae el archivo.

### `LectorCsv.java` — clase auxiliar compartida

Recorre el contenido de un CSV y lo separa en **registros**, cada uno ya
partido en campos. Está aparte porque la necesitan **los dos hijos**: tenerla en
un sitio evita escribir dos veces el mismo código y que uno se arregle y el otro
no.

**Una línea del archivo no es lo mismo que un registro.** Esto es lo importante
de esta clase, y es lo que más cuesta ver.

Un campo entrecomillado puede llevar un **salto de línea dentro**, y entonces un
solo registro ocupa varias líneas del archivo. PostgreSQL los genera de verdad:
si una personalización se guarda en dos líneas, `COPY` exporta esto, que son dos
líneas del archivo para **un** registro:

```
CUSTOM-40,NOVA-4-40,...,Rojo,"Logo bordado, con el texto ""NOVA""
Segunda linea: numeracion en el talon",40,10
```

Por eso la clase **no lee línea a línea**: recorre todo el contenido letra a
letra y decide ella misma dónde acaba cada registro. Un salto de línea dentro de
comillas es texto del campo y se conserva tal cual; fuera de comillas, termina
el registro.

Las cuatro reglas que aplica: las comas separan campos; un campo entre comillas
puede contener comas; dentro de las comillas, dos comillas seguidas (`""`) son
una comilla de verdad; y dentro de las comillas, un salto de línea es texto.

Si el CSV está mal formado —comilla sin cerrar al acabar el archivo, texto
pegado detrás de la comilla de cierre, comilla en medio de un campo sin
entrecomillar— lanza una excepción con el motivo, y el hijo la convierte en su
`ERROR;…`.

**Qué se ha probado, y qué no.** Están probados: comas dentro de comillas,
comillas escapadas, saltos de línea CRLF y LF dentro del campo, los tres
combinados, comilla sin cerrar, registro incompleto y un CSV real exportado por
`COPY`. No se afirma compatibilidad total con el estándar CSV: por ejemplo, un
retorno de carro suelto fuera de comillas se rechaza en vez de tratarse como
final de línea, y no se admiten separadores distintos de la coma.

### `LanzadorValidacion.java` — proceso padre

Recibe la ruta del CSV como argumento, lo lee y lanza los dos hijos con
`ProcessBuilder`:

1. Lanza el validador y le manda el CSV por su stdin.
2. Lee su respuesta, comprueba el código de salida y que empiece por `OK;`.
3. **Solo si la validación es correcta**, lanza el analizador y muestra su
   resumen.

Si cualquiera de los dos falla, muestra el error y **no continúa**.

## Cómo se comunican los procesos

El padre y los hijos hablan por las tuberías que crea `ProcessBuilder`:

```
LanzadorValidacion  --- CSV por stdin --->  ValidadorPedidoCustom
                    <-- OK;... por stdout --
                    <-- ERROR;... por stderr
```

Tres detalles que importan:

Las tuberías tienen un tamaño limitado: cuando se llenan, quien escribe se
queda bloqueado esperando sitio. Hay **tres tuberías** —entrada, salida y salida
de error— y cualquiera de las tres puede colgar el programa.

La solución es **un hilo por tubería**, y el hilo principal solo espera:

```
hilo escritor       -> escribe el CSV en la entrada del hijo
hilo lector salida  -> vacía la salida del hijo
hilo lector error   -> vacía la salida de error del hijo
hilo principal      -> waitFor(10 segundos) y decide
```

**Por qué hace falta cada uno.** Si el padre escribiera él mismo y el hijo no
leyera, el padre se quedaría atascado en `write()` sin llegar nunca a su espera:
comprobado con un CSV de 6 MB, se colgaba **46 segundos**. Y si nadie vaciara la
salida del hijo, el hijo se bloquearía al escribir y no podría terminar:
comprobado con un pedido de **6.000 tallas distintas**, que hace que el
analizador escriba más de lo que cabe en la tubería.

Con un hilo en cada una, ninguna se llena y el hilo principal queda libre para
controlar el tiempo.

**Los tres hilos son demonios**, así que si alguno quedara bloqueado no
impediría que el programa termine. Cada lector guarda las líneas en **su propia
lista**, y el hilo principal no las mira hasta después de `join()`: por eso no
hace falta sincronizar nada.

**Si el hijo no termina en 10 segundos** se cancela: primero `destroy()`, que le
pide que termine, y si en un segundo no lo ha hecho, `destroyForcibly()`, que lo
mata. Al morir el hijo se cierran las tuberías y los tres hilos acaban solos.

### Si la escritura falla, el padre lo dice

El hilo escritor guarda el error en vez de tragárselo, y el padre distingue dos
situaciones:

- **Cancelación por tiempo.** Si hemos cancelado al hijo, es normal que la
  escritura falle. No se avisa de nada aparte: el mensaje es que se ha cancelado.
- **Fallo real.** Si el hijo termina con código 0 pero no se le pudieron enviar
  todos los datos, significa que ha contestado leyendo solo una parte del
  pedido. El padre avisa de que **su respuesta no es fiable** y termina con 1.

### Lo que esto garantiza, y lo que no

**El programa siempre termina.** Los cuatro bloqueos posibles, probados con
hijos preparados a propósito:

| Escenario | Exit | Tiempo | Huérfanos |
|---|---|---|---|
| No termina nunca | 1 | 10 s | 0 |
| No lee su entrada, CSV de 6 MB | 1 | 11 s | 0 |
| Inunda stderr (200.000 líneas) | **0** | 2 s | 0 |
| Pedido de 6.000 tallas | **0** | 1 s | 0 |

Los dos últimos salen con **0 porque ahora terminan bien**: los hilos vacían sus
tuberías y el resultado se conserva. Antes se cancelaban a los 10 segundos y se
perdía.

**No hay límite de tamaño.** El CSV de 6 MB con 60.000 líneas se procesa en
1 segundo, y el pedido de 6.000 tallas devuelve sus 6.000 líneas de resumen.

**Lo que no hace:** el padre guarda en memoria todo lo que escriba el hijo. Con
6.000 líneas no es problema, pero no hay un tope. Y el protocolo sigue siendo
que el validador contesta **una sola línea** empezando por `OK;`: si escribiera
algo antes, el padre lo tomaría por respuesta y la rechazaría.

## Cómo compilar y ejecutar

Hace falta un JDK; está probado con el **17.0.12**. No hay Maven ni librerías.

**En este ordenador `javac` y `java` no están en el PATH**, así que los comandos
cortos no funcionan: dan «javac no se reconoce como un comando interno o
externo». Hay que usar la ruta completa del JDK, que está en la variable
`JAVA_HOME`.

Desde **PowerShell**, dentro de la carpeta `psp`:

```powershell
cd C:\Users\omar2\NOVA\psp
& "$env:JAVA_HOME\bin\javac.exe" -encoding UTF-8 -d clases *.java
& "$env:JAVA_HOME\bin\java.exe" -cp clases LanzadorValidacion ..\fabricacion_psp.csv
```

Desde **cmd**:

```
cd C:\Users\omar2\NOVA\psp
"%JAVA_HOME%\bin\javac" -encoding UTF-8 -d clases *.java
"%JAVA_HOME%\bin\java" -cp clases LanzadorValidacion ..\fabricacion_psp.csv
```

Si se añade `%JAVA_HOME%\bin` al PATH, entonces sí valen los comandos cortos
`javac` y `java`.

La carpeta `clases` que se crea al compilar **no se sube al repositorio**: son
archivos generados.

Para generar primero el CSV desde PostgreSQL. El script deja siempre
`fabricacion_psp.csv` en el directorio desde el que se lanza psql, así que hay
que situarse donde se quiera el archivo:

```
cd C:\Users\omar2\NOVA\psp
psql -U postgres -d nova_sneakers -f ..\acceso-datos\sql\15_exportar_fabricacion.sql
```

El nombre es fijo a propósito: la exportación usa `\copy`, que es la única vía
de psql que **no altera los saltos de línea** de los campos en Windows. Está
explicado en `acceso-datos/documentacion/README.md`.

Cada hijo se puede probar suelto con una tubería. En PowerShell:

```powershell
Get-Content ..\fabricacion_psp.csv | & "$env:JAVA_HOME\bin\java.exe" -cp clases ValidadorPedidoCustom
Get-Content ..\fabricacion_psp.csv | & "$env:JAVA_HOME\bin\java.exe" -cp clases AnalizadorTallas
```

En cmd se usa `type` en lugar de `Get-Content`.

## Qué pasa si hay un error

| Situación | Qué hace | Código |
|---|---|---|
| Todo correcto | valida y muestra el resumen | 0 |
| Falta el argumento o no existe el archivo | avisa y no lanza nada | 1 |
| El validador rechaza los datos | muestra su `ERROR;…` y no lanza el analizador | 1 |
| Un hijo no se puede lanzar | muestra su error y para | 1 |
| Un hijo no termina, no lee su entrada o llena su salida | lo cancela a los 10 segundos y recoge el hilo escritor | 1 |

El validador por su cuenta devuelve 0 si acepta los datos y 2 si los rechaza.

## Ejemplos del profesor utilizados

De **`mini_reto_1_lanzador_estadisticas`**:

- El protocolo `OK;campo1;campo2` por stdout y `ERROR;motivo` por stderr con
  `System.exit(2)`, que viene de `EstadisticasHijo2.java`.
- La estructura del padre de `LanzadorEstadisticas.java`: construir el comando
  con `java.home` y el classpath del propio proceso, leer los dos flujos con
  `inputReader()` y `errorReader()`, `waitFor()`, comprobar el código de salida
  y **validar que la respuesta empiece por `OK;` antes de interpretarla**.

De **`UD2 IPC y sincronizacion/EG1_PipelineTexto`**:

- Cómo un hijo lee su entrada estándar con un `BufferedReader` sobre
  `System.in`, de `ContadorPalabrasLargas.java`.

De **`UD1_ejemplo_guiado_clase/LanzadorProcesoFinal2.java`**:

- La espera con límite de tiempo: `waitFor(n, TimeUnit.SECONDS)` y, si no
  termina, `destroyForcibly()`.

### Qué se ha adaptado

- En el ejemplo del profesor los datos van al hijo **como argumentos**. Aquí van
  por **stdin**, porque un CSV completo no cabe cómodamente en la línea de
  órdenes.
- `LanzadorEstadisticas.java` **no compila** tal cual: declara `String salida;`
  y `String error;` y luego los vuelve a declarar. Se comprobó con
  `javac 17.0.12`. Al adaptarlo se ha corregido.
- El padre usa `outputWriter()` para escribir al hijo, que es el método
  simétrico de `inputReader()`.

### Qué es propio

Las ocho comprobaciones del validador, el agrupamiento por talla con dos listas
en paralelo, su ordenación, el encadenado de los dos pasos con parada si el
primero falla, y el formato del resumen.

**El hilo que escribe el CSV también es propio.** Los ejemplos `.java` del
profesor no usan hilos: trabajan con procesos, no con concurrencia dentro del
programa. En el material teórico los hilos solo se mencionan de pasada, sin
código. Hizo falta uno porque sin él el padre se bloqueaba al escribir un CSV
grande en un hijo que no lo leía, y está explicado en el código para poder
defenderlo.
