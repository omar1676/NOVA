# NOVA Sneakers — Análisis de datos (Ampliación de Python)

Proyecto de Ampliación de Python: lee los CSV que exporta Acceso a Datos, los
valida con las doce reglas de calidad de la rúbrica, construye los DataFrames de
análisis, calcula los KPIs, los gráficos y la estadística, y concilia las cifras
con SQL. También genera un histórico sintético, siempre separado y etiquetado, y
con él segmenta clientes (RFM y KMeans) y predice la demanda. Todo se ve en un
dashboard Streamlit que vuelve a leer, validar y calcular los CSV cada 60 segundos.

Esta carpeta es la equivalente a `sneaker-data-lab/` del apartado 9 de la rúbrica.
Se llama `python-analisis` para seguir el estilo de las demás carpetas del
repositorio (`acceso-datos`, `interfaces`, `psp`).

## Estado

| Fase | Qué incluye | Estado |
|---|---|---|
| 1 | Lectura y validación de los cinco CSV, diccionario de datos, comprobaciones rápidas | hecha |
| 2 | Las 12 reglas de calidad, `incidencias.csv` y `resumen_calidad.csv`, `df_lineas_enriquecidas` y `df_pedidos_unicos`, 18 variables derivadas, importes con tres criterios, conciliación con 3 consultas SQL y las 3 del caso N | hecha |
| 3 | 20 KPIs (3 NO CALCULABLES), 14 DataFrames analíticos, clasificación ABC, 10 gráficos PNG, coherencia de los KPIs con SQL | hecha |
| 4 | Generador sintético (900 pedidos, 18 meses, semilla 2026) y copia con errores, estadística descriptiva, 3 hipótesis y bootstrap del ticket medio | hecha |
| 5 | RFM con 6 segmentos, KMeans (k de 2 a 5, silhouette), predicción de la demanda mensual por modelo con baseline y regresión lineal (MAE y RMSE) | hecha |
| 6 | Dashboard Streamlit: 6 pestañas, refresco real cada 60 s, 6 filtros combinables, 10 descargas CSV con sus metadatos, registro de eventos e informe ejecutivo con 5 conclusiones priorizadas | hecha |

**Los datos actuales son de una base de PRUEBA**, no de la base principal del
equipo (lo dice `entrada_acc/ORIGEN.txt` y todos los resultados lo llevan
escrito). No son ventas reales.

## Estructura

```
python-analisis/
├── README.md             este archivo
├── diccionario_datos.md  columnas, tipos, relaciones, DataFrames y variables derivadas
├── calidad_datos.md      las 12 reglas, gravedades y casos investigados
├── conciliacion_sql.md   las consultas SQL (P-A a P-C y caso N), en qué se diferencian y resultados
├── kpis_y_graficos.md    los KPIs con su fórmula, los DataFrames, los gráficos y el ABC
├── datos_sinteticos.md   cómo se generan los datos sintéticos, sus hipótesis y la copia con errores
├── estadistica.md        descriptivos, las tres hipótesis, el bootstrap y lo que no se puede afirmar
├── segmentacion_y_prediccion.md  RFM, KMeans, predicción, resultados y análisis de errores
├── dashboard.md          el dashboard: pestañas, filtros, refresco, descargas y registro
├── informe_ejecutivo.md  las cinco conclusiones para producción y comercial
├── requirements.txt      dependencias con versión fija
├── config.py             carpetas, formato, columnas, catálogos, criterios y umbrales
├── pipeline.py           lectura y validación de los CSV, origen y guardado
├── comprobaciones.py     comprobaciones rápidas de la fase 1
├── calidad.py            las 12 reglas de calidad y los nulos por columna
├── analiticas.py         todos los DataFrames, variables derivadas, ABC e importes
├── kpis.py               los KPIs y su coherencia con SQL
├── visualizaciones.py    los 10 gráficos (Matplotlib) y el de real frente a predicción
├── estadistica.py        descriptivos, hipótesis y bootstrap
├── segmentacion.py       RFM y KMeans
├── prediccion.py         demanda mensual, baseline, regresión, MAE y RMSE
├── filtros.py            los seis filtros combinables (sin Streamlit)
├── actualizacion.py      ciclo de 60 s: comprobar, validar, recalcular, publicar y anotar
├── registro.py           registro de eventos (logs/registro_eventos.csv)
├── informe.py            las cinco conclusiones del informe ejecutivo
├── metadatos.py          fecha de corte, reglas, filtros, filas de origen y función de cada DataFrame
├── app_dashboard.py      el dashboard Streamlit (solo orquesta y muestra)
├── .streamlit/           tema del dashboard y opciones del servidor
├── conciliacion.py       comparación con las consultas SQL de Acceso a Datos
├── generador_datos.py    el generador de datos SINTÉTICOS
├── main.py               ejecución por consola (modos real, sintetico y sintetico-errores)
├── entrada_acc/          los cinco CSV de Acceso a Datos + ORIGEN.txt + conciliacion_sql/
├── datos_sinteticos/     limpios/ y con_errores/ (los escribe generador_datos.py)
├── outputs/              real/, sinteticos/ y sinteticos_con_errores/ (se generan; Git los ignora)
├── logs/                 registro de eventos del dashboard (se genera; Git lo ignora)
├── evidencias/dashboard/ capturas del dashboard en Edge (escritorio y móvil)
└── tests/                pruebas con CSV inventados (nunca los reales)
```

Ningún cálculo está en Streamlit: el dashboard solo llama a `actualizacion`,
`filtros`, `analiticas`, `kpis`, `visualizaciones` e `informe`, las mismas funciones
que `main.py`, para que no haya dos fórmulas para la misma cifra.

## Instalación

Hace falta **Python 3.12 o superior** (probado con 3.13.5). En Windows, el comando
`python` puede abrir la Microsoft Store en lugar de Python: usad el lanzador `py`.

En Windows, desde la raíz del repositorio:

```
cd python-analisis
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

El entorno `.venv/` es de cada uno y Git lo ignora (`.gitignore` de esta carpeta).
Los comandos de abajo usan `.venv\Scripts\python.exe` directamente, así no hace
falta activar el entorno.

## Datos de entrada

Python no se conecta a PostgreSQL: lee los CSV que exporta Acceso a Datos. Para
generarlos, desde la raíz del repositorio:

```
cd python-analisis\entrada_acc
psql -U postgres -d nova_sneakers -f ..\..\acceso-datos\sql\16_exportar_csv_dashboard.sql
```

Después hay que poner en `entrada_acc/ORIGEN.txt` de qué base salen y su tipo en la
primera línea:
- `Tipo: PRUEBA`: base de prueba.
- `Tipo: REAL`: base del equipo.
- `Tipo: SINTETICO`: generado por Python.

Ese tipo se escribe en todos los resultados. Para la conciliación hacen falta
también los resultados de las tres consultas SQL en `entrada_acc/conciliacion_sql/`
(ver `conciliacion_sql.md`).

Python nunca modifica la carpeta de entrada: solo la lee, y `guardar_salida` se
niega a escribir en ella.

## Ejecución

Desde la carpeta `python-analisis`:

```
.venv\Scripts\python.exe main.py
.venv\Scripts\python.exe generador_datos.py
.venv\Scripts\python.exe main.py --modo sintetico
.venv\Scripts\python.exe main.py --modo sintetico-errores
.venv\Scripts\python.exe main.py --entrada CARPETA --salida CARPETA
.venv\Scripts\streamlit.exe run app_dashboard.py
```

La última línea abre el dashboard en `http://localhost:8501` (detalle en
`dashboard.md`).

Cada modo tiene sus carpetas, para que los datos nunca se mezclen:

| Modo | Lee | Escribe |
|---|---|---|
| `real` (por defecto) | `entrada_acc/` (exportación de Acceso a Datos) | `outputs/real/` |
| `sintetico` | `datos_sinteticos/limpios/` | `outputs/sinteticos/` |
| `sintetico-errores` | `datos_sinteticos/con_errores/` | `outputs/sinteticos_con_errores/` |

`generador_datos.py` vuelve a crear las dos carpetas de `datos_sinteticos/`
(detalle en `datos_sinteticos.md`).

Pasos de `main.py`:

1. Aplica las 12 reglas y guarda `incidencias.csv`, `resumen_calidad.csv` y
   `filas_rechazadas.csv`, siempre, aunque haya bloqueo.
2. Si hay alguna incidencia **bloqueante**, se para y no publica ninguna cifra.
3. Si no:
   - enseña el resumen de la carga y las comprobaciones rápidas;
   - calcula todos los DataFrames y guarda uno en CSV cada uno;
   - guarda `importes_por_criterio.csv` y `kpis.csv`;
   - concilia con SQL (`conciliacion_sql.csv`, `coherencia_kpis_sql.csv` y, para el
     caso N, `contraste_sql_caso_n.csv`); con datos sintéticos, la conciliación
     «NO APLICA»;
   - dibuja los 10 gráficos en la carpeta `graficos/` de su salida;
   - calcula la estadística (`estadisticos_descriptivos.csv`, `hipotesis.csv` y
     `bootstrap_ticket_medio.csv`);
   - segmenta a los clientes y predice la demanda (`rfm_*.csv`, `kmeans_*.csv`,
     `demanda_mensual_modelo.csv`, `predicciones.csv`, `metricas_prediccion.csv`…)
     y dibuja `graficos_prediccion/11_real_frente_a_prediccion.png`. Con pocos
     clientes o pocos meses, cada tabla sale como NO CALCULABLE con su motivo.

Cada ejecución deja `metadatos_dataframes.csv`, con una fila por CSV: la fecha de
corte, las reglas de negocio, los filtros, las filas de origen y la función que lo
genera (`metadatos.py`). Se enlaza con cada CSV por su nombre y su columna
`ejecucion`.

Y deja `estado_ejecucion.csv`:
- `CORRECTO`;
- `BLOQUEADO`: avisa de que cualquier otro resultado de la carpeta es de una
  ejecución anterior y está **desactualizado**;
- `NO CUADRA CON SQL`.

Termina con código 1 si los datos están bloqueados o si alguna cifra no coincide
con SQL. Todos los CSV de salida están en UTF-8, con cabecera, y empiezan por las
columnas `origen` y `ejecucion`. Los mismos datos dan las mismas cifras y los
mismos gráficos; solo cambia la hora de la ejecución.

## Calidad (`calidad.py`)

Doce reglas, una función por regla, con gravedad **bloqueante** (se detiene),
**recuperable** (se rechaza la fila) o **advertencia** (se mantiene y se avisa). Un
pedido se analiza entero o no se analiza. Nunca se corrige ni se inventa un valor.
Detalle en `calidad_datos.md`.

## Análisis (`analiticas.py`)

- **`df_lineas_enriquecidas`:** una fila por línea, con pedido, cliente, modelo y color.
- **`df_pedidos_unicos`:** una fila por pedido, con su cliente y las métricas de sus líneas.

Cada `merge` lleva `validate=` e `indicator=True`, y para si multiplica filas o
pierde claves. Las 18 variables derivadas están en `diccionario_datos.md`.
`importes_por_criterio` da pedidos, pares e importe de tres formas:
- registrados;
- no cancelados;
- confirmados en adelante.

Ninguna se llama «ingresos cobrados».

## KPIs y gráficos (`kpis.py` y `visualizaciones.py`)

- **KPIs:** 20, cada uno con fórmula, unidad, población y tabla de origen. 17 son
  calculables con los datos actuales y 3 salen como **NO CALCULABLE** con su motivo:
  margen (no hay coste), variación mensual (un solo mes) y cobertura (no hay 28
  días de historial).
- **Gráficos:** 10, de los 8 tipos que pide el apartado 6.6, y cada uno responde a
  una pregunta.

El detalle, con los valores de los datos de prueba y la clasificación ABC, está en
`kpis_y_graficos.md`.

## Datos sintéticos y estadística (`generador_datos.py` y `estadistica.py`)

- **Datos sintéticos:** 40 clientes, 12 modelos, 900 pedidos, 1.777 líneas y 216
  SKU de stock, en 18 meses (de mayo de 2025 a octubre de 2026), con la semilla 2026.
  Pasan las 12 reglas sin ninguna incidencia. La copia con errores hace saltar las
  reglas de la 02 a la 12.
- **Estadística:** media, mediana, moda, desviación típica, percentiles y rango
  intercuartílico de tres variables, con qué estadístico representa mejor cada caso.
  Incluye tres hipótesis con su intervalo bootstrap y el ticket medio con su
  intervalo al 95 % (2.000 remuestreos, semilla 2026).

Nada de lo que sale de los datos sintéticos describe a los clientes reales de
NOVA. Detalle en `datos_sinteticos.md` y `estadistica.md`.

## Segmentación y predicción (`segmentacion.py` y `prediccion.py`)

- **RFM:** recency, frequency y monetary de cada cliente con las ventas válidas y la
  fecha de corte como referencia. Puntuaciones de 1 a 5 por quintiles y 6 segmentos
  (Mejores clientes, En riesgo, Habituales, Inactivos, Ocasionales y Sin compras
  válidas).
- **KMeans:** sobre las tres variables RFM escaladas, prueba k = 2 a 5 y elige el
  silhouette más alto (con los sintéticos: k = 4, silhouette 0,373). Los grupos se
  comparan con RFM.
- **Predicción:** pares de demanda por modelo y mes, entrenamiento 2025-08 a 2026-07
  y evaluación 2026-08 a 2026-10. Con los sintéticos, la regresión **no** mejora
  claramente al baseline del mes anterior: MAE 26,28 frente a 25,03 y RMSE 36,15
  frente a 37,42.

Con los datos de prueba de Acceso a Datos (6 clientes, 1 con compras, ningún mes
completo) todo sale como NO CALCULABLE. Detalle en `segmentacion_y_prediccion.md`.

## Dashboard (`app_dashboard.py`)

Seis pestañas: Dirección, Productos, Clientes, Inventario, Calidad y Predicción.

- **Origen siempre visible.** Puede ser la exportación de ACC (ahora PRUEBA), los
  sintéticos limpios o los sintéticos con errores, y nunca se mezclan.
- **Refresco real cada 60 s.** Con `st.fragment(run_every="60s")`, cada minuto
  vuelve a leer los CSV del disco, los valida y lo recalcula todo con la misma
  versión de los datos. También hay un botón «Actualizar ahora».
- **Estado del ciclo.** Correcto, sin cambios, datos inválidos o error de carga.
  Con datos bloqueados no se publica ninguna cifra.
- **Filtros.** Seis filtros combinables (periodo, modelo, talla, tipo, estado y
  cliente), hechos en `filtros.py`, fuera de Streamlit. Se mantienen con el
  refresco y «Restablecer filtros» los vacía todos.
- **Descargas.** Diez CSV en UTF-8, con su origen, sus filtros y sus metadatos
  (fecha de corte, función, reglas y filas de origen), y sin datos personales.
- **Registro.** `logs/registro_eventos.csv`, una fila por operación.

Los datos nuevos de PostgreSQL solo llegan cuando Acceso a Datos vuelve a
exportar los CSV. Detalle en `dashboard.md`; las conclusiones, en
`informe_ejecutivo.md`.

## Pruebas

Desde la carpeta `python-analisis`:

```
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

**265 pruebas.** Cada una crea sus propios CSV en una carpeta temporal.

| Archivo | Pruebas | Qué cubren |
|---|---|---|
| `test_pipeline.py` | 20 | fase 1: lectura, CSV ausente, vacío, mal formado, otra codificación, comprobaciones rápidas |
| `test_calidad.py` | 38 | ver abajo |
| `test_analiticas.py` | 28 | ver abajo |
| `test_tablas.py` | 27 | ver abajo |
| `test_kpis.py` | 16 | ver abajo |
| `test_visualizaciones.py` | 8 | ver abajo |
| `test_sinteticos.py` | 21 | ver abajo |
| `test_estadistica.py` | 15 | ver abajo |
| `test_segmentacion.py` | 18 | ver abajo |
| `test_prediccion.py` | 20 | ver abajo |
| `test_filtros.py` | 18 | filtros combinados (también el de cliente), sin duplicados, KPIs filtrados, inventario con umbral, CSV descargado con sus metadatos (ver `dashboard.md`) |
| `test_actualizacion.py` | 22 | ciclo de 60 s, pruebas R1 a R5, CSV ausente o corrupto, bloqueo, cambio de origen, registro e informe ejecutivo (prioridad, impacto y sustento) |
| `test_dashboard.py` | 14 | la aplicación Streamlit con `AppTest`: pestañas, orígenes, bloqueo, filtros (también el de cliente), filtros y pestaña que se mantienen al refrescar, R6 (filtrado cruzado), refresco y botón «Actualizar ahora» |

`test_sinteticos.py`:
- misma semilla, mismos datos;
- los mínimos de filas y los 18 meses seguidos;
- pedidos y líneas que cuadran;
- sin claves huérfanas;
- las reglas de negocio y la variedad;
- datos limpios sin incidencias y la copia con errores, que hace saltar las 11 reglas;
- la separación de `entrada_acc/`;
- la ejecución completa con datos sintéticos, también la fase 5 etiquetada como
  SINTÉTICO.

`test_segmentacion.py`:
- recency desde la fecha de corte;
- pedidos posteriores al corte;
- frequency y monetary;
- clientes sin compras;
- quintiles y reglas de los segmentos;
- RFM reproducible;
- variables de KMeans escaladas y sin nulos;
- k de 2 a 5 con silhouette, y la elección de k;
- KMeans reproducible;
- descripción de los clústeres y comparación con RFM;
- con pocos clientes, NO CALCULABLE.

`test_prediccion.py`:
- demanda mensual sin cancelados ni meses futuros o incompletos;
- variables solo del pasado;
- periodos exactos;
- agosto, septiembre y octubre de 2026 no entran en el entrenamiento;
- el mes objetivo no es una entrada;
- baseline;
- MAE y RMSE;
- comparación de métodos, con un caso en que la regresión mejora y otro en que no;
- datos insuficientes;
- con calidad bloqueada no se publica la fase 5.

`test_estadistica.py`:
- los descriptivos con valores conocidos;
- el bootstrap reproducible;
- el ticket medio;
- las tres hipótesis completas y reproducibles;
- la evidencia insuficiente con pocos datos;
- un crecimiento claro que sí se detecta.

`test_tablas.py`:
- los estados;
- la matriz modelo × talla y que no se cuenta nada dos veces;
- ABC con acumulados, empates y sin demanda;
- dos meses y un mes vacío;
- las cohortes;
- los totales de inventario y la cobertura;
- el margen;
- los atípicos;
- las tablas vacías.

`test_kpis.py`:
- cada KPI;
- registrado, confirmado y pagado son cifras distintas;
- ticket entre pedidos;
- empates;
- los NO CALCULABLES;
- sin pedidos;
- coherencia con PostgreSQL.

`test_visualizaciones.py`:
- salen los 10 PNG válidos;
- funcionan sin datos;
- la ejecución completa: correcta, bloqueada por calidad (sin cifras ni gráficos) y
  con SQL que no cuadra;
- `metadatos_dataframes.csv`: una fila por CSV, también con los datos bloqueados.

`test_calidad.py`:
- al menos un caso preparado por cada una de las 12 reglas;
- un pedido duplicado por id, líneas huérfanas y totales que no cuadran;
- rechazo del pedido entero;
- los CSV de incidencias y de resumen;
- que nunca se escribe en la entrada.

`test_analiticas.py`:
- un JOIN que duplicaría filas;
- una fila por línea y por pedido;
- las variables derivadas y el modelo del pedido;
- los tres criterios de importe;
- la conciliación: coincide, no coincide, falta en SQL, falta en Python y pendiente;
- el caso N (ingresos de un mes, matriz talla × modelo y clientes únicos): coincide,
  mes sin ventas, discrepancias detectadas y pendiente;
- el caso A: un pedido Custom de 40 pares en 4 tallas, línea a línea, en la matriz y
  en los KPIs.

Se usa `unittest`, que viene con Python. La rúbrica recomienda pytest, y pytest
puede ejecutar estas mismas pruebas si el equipo decide añadirlo.
