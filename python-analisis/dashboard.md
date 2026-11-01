# Dashboard Streamlit (fase 6)

Apartados 6.12 y 6.14 a 6.17 de la rúbrica. El dashboard es la segunda entrada
del proyecto, después de `main.py`.

## Arrancar

Desde la carpeta `python-analisis`, para que Streamlit lea `.streamlit/config.toml`:

```
.venv\Scripts\streamlit.exe run app_dashboard.py
```

Se abre en `http://localhost:8501`. Por defecto solo responde en este ordenador
(`server.address = "localhost"`). Para verlo desde un móvil de la misma red:

```
.venv\Scripts\streamlit.exe run app_dashboard.py --server.address 0.0.0.0
```

Probado con Python 3.13.5 y Streamlit 1.67.0 (la versión de `requirements.txt`).
`st.fragment(run_every=...)` existe en Streamlit desde la versión 1.37. No hay
dependencias nuevas.

## Arquitectura: la interfaz no calcula

```
app_dashboard.py   solo orquesta y muestra (Streamlit)
   │
   ├─ actualizacion.ciclo()   cada 60 s: comprobar archivos → validar → recalcular → publicar → anotar
   │     ├─ calidad.evaluar          las 12 reglas
   │     ├─ analiticas.calcular_tablas, kpis.calcular_kpis
   │     ├─ segmentacion (RFM y KMeans), prediccion
   │     ├─ conciliacion (SQL), informe (5 conclusiones)
   │     └─ registro.anotar          una fila en logs/registro_eventos.csv
   ├─ filtros.calcular_filtrado()   tablas y KPIs del subconjunto filtrado
   ├─ filtros.tablas_inventario()   stock con el umbral elegido
   └─ visualizaciones               los mismos gráficos Matplotlib que main.py
```

Todas las cifras salen de las mismas funciones que usa `main.py`: no hay una
segunda fórmula para ningún KPI. `actualizacion.py`, `filtros.py`, `informe.py`
y `registro.py` no importan Streamlit, así que se prueban desde consola y con
`unittest`.

## Origen de los datos

En la barra lateral se elige uno de tres orígenes. Cada uno tiene su carpeta y
su propio estado en la sesión, así que nunca se mezclan:

| Origen en pantalla | Carpeta | Qué es |
|---|---|---|
| Exportación ACC (por defecto) | `entrada_acc/` | CSV exportados de PostgreSQL. Su tipo lo dice `ORIGEN.txt`; ahora es **PRUEBA** |
| Sintéticos limpios | `datos_sinteticos/limpios/` | Histórico de `generador_datos.py` |
| Sintéticos con errores | `datos_sinteticos/con_errores/` | La copia con errores: muestra el bloqueo de calidad |

El origen está siempre visible:
- **Etiqueta de color** con el texto de `ORIGEN.txt`: naranja para PRUEBA, violeta
  para SINTÉTICO y verde para REAL.
- **Aviso fijo:** «Exportación de PRUEBA… no son ventas reales» o «Datos SINTÉTICOS…».
- **Cada gráfico y cada descarga** llevan el origen escrito.

Los datos de prueba nunca se llaman reales. El origen y la pestaña se guardan en
la dirección, para poder compartir un enlace:
`http://localhost:8501/?origen=Sintéticos+limpios&pestana=Clientes`.

## Las pestañas

En todas, el título dice qué se ve y una etiqueta indica si es **Filtrado** o
**Global: no usa los filtros**. Solo se calcula la pestaña abierta.

| Pestaña | Contenido |
|---|---|
| **Dirección** | Tarjetas de pedidos registrados, confirmados y cancelados, pares solicitados, importe confirmado, ticket medio e importe con pago registrado; el importe del último mes frente al anterior; evolución mensual (gráfico 04 de pares y serie de importe confirmado); pedidos por estado (gráfico 01) y por estado de pago; las cinco conclusiones del informe ejecutivo |
| **Productos** | Ranking y clasificación ABC (tabla y gráfico de Pareto 02); tallas (gráfico 03); matriz modelo × talla (mapa de calor 05); Custom frente a estándar (gráfico 06, caja 09 y tabla) |
| **Clientes** | Actividad y ranking de clientes (tabla y gráfico 07, solo con id y tipo); segmentos RFM con su significado y una dispersión recencia × importe; KMeans (silhouette por k, grupos y cruce con RFM); cohortes de compra |
| **Inventario** | Umbral de stock bajo configurable; tarjetas de stock total, SKU, SKU bajo el umbral, SKU bajo el umbral con pedidos recientes y cobertura; stock por modelo y color; tabla de alertas; demanda de 28 días frente a existencias (histograma 08 y tabla por SKU) |
| **Calidad** | Semáforo; última comprobación; filas recibidas, válidas y rechazadas; incidencias por gravedad; calidad por tabla; tablas y columnas afectadas; incidencias; filas rechazadas; origen de los archivos (tamaño, fecha y huella); `ORIGEN.txt`; conciliación con SQL; registro de eventos |
| **Predicción** | Laboratorio, rotulado como tal con datos sintéticos: MAE y RMSE del baseline y de la regresión, si mejora, periodos, gráfico real frente a predicción (11), error por modelo, predicciones y coeficientes |

- **Las 5 obligatorias y la sexta.** Las cinco pestañas que pide el encargo son
  las cinco primeras. La sexta es la vista «06 · Modelos predictivos» del
  apartado 6.16.
- **Los datos de cada gráfico.** Cada gráfico tiene debajo «Ver los datos del
  gráfico» con su tabla.
- **Diseño.** Solo hay componentes nativos de Streamlit y un tema con los
  colores de la web de NOVA (`.streamlit/config.toml`), sin CSS propio.
- **En el móvil.** Las columnas se apilan y las pestañas se desplazan en
  horizontal.

### Con datos insuficientes o bloqueados

- **Bloqueo de calidad o error de carga.** Las pestañas de negocio no enseñan
  ninguna cifra: dicen «No se publican cifras» y mandan a Calidad.
- **Último resultado válido.** Si existe uno de ese mismo origen, se puede ver con
  un interruptor (apagado por defecto). Sale rotulado como **DESACTUALIZADO** y
  con su fecha.
- **RFM, KMeans, cohortes y predicción** salen como **NO CALCULABLE** con su
  motivo cuando faltan clientes o meses. Con la exportación de prueba pasa: hay 1
  cliente con compras y ningún mes completo.

## Filtros combinados

Hay cinco: **periodo** (fecha del pedido), **modelo**, **talla**, **tipo de
pedido** y **estado del pedido**. Se combinan con Y, y un filtro vacío no
restringe nada. «Restablecer filtros» los deja todos vacíos. Cada origen
recuerda sus filtros, y el refresco de 60 s no los borra.

Cómo se aplican (`filtros.filtrar_validos`):

1. **Periodo, tipo y estado son del pedido.** Se quedan los pedidos que los
   cumplen, con todas sus líneas. El periodo incluye el último día entero.
2. **Modelo y talla son de la línea.** Se quedan solo las líneas que los cumplen.
   Un pedido con líneas de varios modelos:
   - aporta solo las del modelo elegido (sus pares y su importe);
   - cuenta **una vez** si tiene al menos una;
   - desaparece si no tiene ninguna.
3. **Se recalcula todo.** `analiticas.calcular_tablas` y `kpis.calcular_kpis`
   vuelven a calcular TODAS las tablas y KPIs con ese subconjunto. Las tarjetas,
   las tablas, los gráficos y las descargas son, por tanto, del mismo subconjunto
   y de la misma versión de los datos.

En Dirección se dice el denominador: «N de M pedidos registrados cumplen los
filtros…». Hay cosas que no usan los filtros, y van rotuladas como globales:

- **RFM y KMeans** usan siempre todos los pedidos de venta hasta la fecha de
  corte. Con un periodo o un modelo filtrado, la recencia y los quintiles
  cambiarían de significado.
- **La predicción** usa la serie completa de cada modelo. Con meses filtrados, la
  separación por fecha entre entrenamiento y evaluación dejaría de tener sentido.
- **Las conclusiones del informe** se calculan con toda la exportación.
- **El inventario** solo aplica modelo y talla. El stock es una foto en la fecha
  de corte, y la demanda es siempre la de los 28 días anteriores al corte.

Comprobado con pruebas:

- **Las cifras son las de un filtro hecho a mano.** El resultado filtrado coincide
  con filtrar a mano las líneas válidas.
- **No se duplica nada.** Filtrando modelo a modelo, los pares y el importe suman
  lo mismo que sin filtrar.
- **El navegador da las mismas cifras que la consola.** Prueba: en Edge se
  eligieron, con clics en la barra lateral, tipo Custom, modelo SINT Runner,
  estado entregado y talla 42. Salieron 31 de 900 pedidos, 370 pares, 56.133,71 €
  confirmados y un ticket de 1.810,76 €. Son las cifras de
  `filtros.calcular_filtrado` en la consola, y la tabla `pedidos_unicos`
  descargada suma lo mismo.

## Refresco cada 60 segundos

- **El temporizador.** `panel()` es un `st.fragment(run_every="60s")`, y Streamlit
  lo vuelve a ejecutar cada 60 s mientras la página está abierta. No hay
  `time.sleep`, bucles ni recargas del navegador.
- **El ciclo.** Si han pasado 60 s desde la última comprobación del origen (con 5 s
  de margen, porque el temporizador no es exacto), se llama a
  `actualizacion.ciclo`, que:
  1. comprueba qué archivos hay, su tamaño, su fecha y su **huella SHA-256 del
     contenido**;
  2. **relee los CSV del disco** y los valida con las 12 reglas;
  3. si son válidos, recalcula todo de una vez con esa misma versión;
  4. publica un resultado completo o ninguno;
  5. anota el ciclo en el registro.
- **Siempre se recalcula.** Se hace aunque los CSV no hayan cambiado: así se
  comprueba cada minuto que siguen siendo válidos.
- **Una exportación nueva.** Si cambia la huella, se redibuja la página entera,
  también las opciones de los filtros. Si el periodo era el completo, se amplía
  con las fechas nuevas, para que los pedidos nuevos no queden fuera.
- **«Actualizar ahora».** El botón de la barra lateral lanza el ciclo en el acto.

### Estados

| Estado | Cuándo |
|---|---|
| Correcto | datos nuevos (otra huella), válidos y publicados |
| Sin cambios | la misma huella: se ha vuelto a leer, validar y calcular, y sale lo mismo |
| Datos inválidos | se leen los cinco CSV, pero hay incidencias bloqueantes |
| Error de carga | falta un CSV, está vacío, no es UTF-8, le falta una columna obligatoria o falla la lectura |

Arriba se ven siempre:
- **el estado** y **la hora de la última comprobación**, que cambia cada minuto;
- **la última actualización válida**: el momento en que se cargó por primera vez
  la versión que se está mostrando;
- **las filas válidas**, **la fecha de corte**, **la versión** (la huella),
  **el tiempo de procesamiento** y **los avisos de archivos**: que faltan, vacíos,
  antiguos (más de 24 h) o de momentos distintos (más de 10 min entre el primero y
  el último).

Python solo lee CSV. **Un pedido nuevo en PostgreSQL no aparece hasta que Acceso
a Datos vuelve a exportar los CSV** (`16_exportar_csv_dashboard.sql`). Sin una
exportación nueva, cada minuto se vuelve a calcular, pero las cifras no tienen
por qué cambiar.

### Demostración en un navegador real (Edge)

Se hizo con una copia de `entrada_acc/` en una carpeta temporal: la original no
se tocó. El navegador no recargó ni pulsó nada; solo esperó.

| Paso | Cambio en los CSV | A los 60 s, en pantalla |
|---|---|---|
| R5 | ninguno | Estado «Sin cambios». La última comprobación pasa de 12:28:39 a 12:29:41 y la actualización válida sigue en 12:28:39. Las cifras no cambian: 12 pedidos y 4.796,00 € confirmados |
| R1 | un pedido confirmado nuevo con 2 líneas (3 pares, 239,97 €) | «Correcto»: pedidos de 12 a 13, confirmados de 1 a 2, pares de 90 a 93 e importe de 4.796,00 € a 5.035,97 €, sin contar nada dos veces |
| R4 | se quita `pedidos.csv` | «Error de carga» y «Falta pedidos.csv». No hay cifras; el interruptor enseña las de las 12:30:41 rotuladas DESACTUALIZADO |
| Recuperación | vuelve `pedidos.csv` | Vuelven las cifras: 13 pedidos y 5.035,97 €. El estado es «Sin cambios» porque es la misma versión que la última válida |

R2 (cancelación) y R3 (cambio de stock) se comprueban en `test_actualizacion.py`
y `test_dashboard.py`.

## Descargas CSV

Hay 10 botones con 10 tablas distintas:

| Pestaña | Tablas |
|---|---|
| Dirección | `ventas_por_periodo` y `pedidos_unicos` |
| Productos | `modelos_abc` y `matriz_modelo_talla` |
| Clientes | `clientes_actividad` y `rfm_clientes` (global) |
| Inventario | `stock_bajo` y `stock_variantes` |
| Calidad | `incidencias` (cuando hay alguna) |
| Predicción | `predicciones` (global) |

Cada archivo:
- está en **UTF-8, con cabecera**;
- es la **misma tabla que se ve** en pantalla, con los mismos filtros;
- empieza por tres columnas de linaje: `origen`, `ejecucion` (momento y versión de
  los datos) y `filtros` (o «ninguno (resultado global)»);
- lleva el origen en el nombre, como `modelos_abc_sintetico.csv`;
- **nunca lleva nombres, correos ni teléfonos de clientes**
  (`pipeline.sin_datos_personales`).

## Registro de eventos

Es un solo archivo, `logs/registro_eventos.csv`. Git lo ignora y se le añade una
fila por operación; no se crea un archivo por refresco.

- **Columnas:** fecha y hora, origen, carpeta (relativa), operación, resultado,
  filas procesadas, filas válidas, incidencias, bloqueantes, versión de los datos,
  duración y detalle.
- **Operaciones:**
  - carga inicial del origen;
  - comprobación automática (60 s);
  - actualización manual;
  - descarga de un CSV.
- **Lo que nunca lleva:**
  - contraseñas (Python no maneja credenciales);
  - la ruta completa del ordenador (los mensajes de error se dejan con la ruta
    relativa);
  - datos de clientes.

Las últimas 50 filas se ven en la pestaña Calidad. Cada sesión del navegador
hace sus propios ciclos, así que con dos pestañas abiertas hay dos filas por
minuto.

## Pruebas

| Archivo | Pruebas | Qué cubren |
|---|---|---|
| `test_filtros.py` | 14 | cada filtro y los cuatro combinados contra un filtro a mano; sin filtros no cambia nada; sin duplicar pedidos ni importes; KPIs filtrados coherentes con sus tablas; filtro sin resultados; inventario con umbral; CSV descargado (UTF-8, cabecera, linaje, sin datos personales); estado de pagos |
| `test_actualizacion.py` | 20 | primer ciclo; R1 a R5; volver a exportar lo mismo no es un cambio; CSV ausente y recuperación; CSV corrupto; clave huérfana; sin ninguna venta; avisos de exportación antigua o incompleta; no escribe en la entrada; cambio de origen sin mezclar; sintéticos con errores bloqueados; registro (un archivo, una fila por ciclo, sin rutas ni datos personales); las cinco conclusiones y su procedencia |
| `test_dashboard.py` | 11 | `AppTest` de Streamlit ejecuta la aplicación de verdad: arranca con la exportación ACC rotulada PRUEBA; seis pestañas, todas sin errores con los tres orígenes; al menos cinco descargas; NO CALCULABLE con pocos datos; bloqueo sin cifras; cambio de origen; relectura a los 60 s (y antes no); botón «Actualizar ahora»; CSV que falta; cuatro filtros combinados que cambian las tarjetas, y restablecer |

Para estas pruebas, `test_dashboard.py` cambia en `config` las tres carpetas y el
registro por carpetas temporales. Al terminar las deja como estaban, así que
nunca toca `entrada_acc/`, `datos_sinteticos/` ni `logs/`.
