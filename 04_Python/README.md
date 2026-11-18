# NOVA Sneakers — Análisis de datos (Ampliación de Python)

Proyecto de Ampliación de Python: lee los CSV que exporta Acceso a Datos, los
valida con las doce reglas de calidad de la rúbrica, construye los DataFrames de
análisis, calcula los KPIs, los gráficos y la estadística, y concilia las cifras
con SQL. También genera un histórico sintético, siempre separado y etiquetado, y
con él segmenta clientes (RFM y KMeans) y predice la demanda. Todo se ve en un
dashboard Streamlit que vuelve a leer, validar y calcular los CSV cada 60 segundos.

Esta carpeta es la equivalente a `sneaker-data-lab/` del apartado 9 de la rúbrica.
Se llama `04_Python` para seguir el estilo de las demás carpetas del
repositorio (`01_Interfaces`, `02_Acceso_Datos`, `03_PSP`…).

## En resumen

| | |
|---|---|
| **Tecnologías** | Python 3.12 o superior con pandas, numpy, matplotlib, scikit-learn y Streamlit (versiones exactas en `requirements.txt`) |
| **Qué necesita** | Un entorno virtual con `requirements.txt` y los CSV de `entrada_acc/` (los genera `02_Acceso_Datos/sql/16_exportar_csv_dashboard.sql`) |
| **Cómo se inicia** | `main.py` por consola y `streamlit run app_dashboard.py` para el dashboard (apartado «Instalación» de este README) |
| **Pruebas** | `python -m unittest discover -s tests -v`: 278 pruebas en 14 archivos (apartado «Pruebas»). El 13/11 también se compararon las salidas de datos de `main.py` (tres modos) y del generador con una referencia guardada (97 archivos según aquella comprobación); sus registros no están en el repositorio |
| **Rúbrica** | Según la matriz de requisitos del 13/11, que ya no está en el repositorio: 214 requisitos y 200 cumplidos. Falta sobre todo la exportación REAL |
| **Conexión con otras asignaturas** | Lee lo que exporta Acceso a Datos y concilia sus cifras con las consultas de `02_Acceso_Datos/sql/12_consultas_panel.sql`. El ensayo SO024 PROVISIONAL se comprobó el 13/11, pero sus registros no están en el repositorio; no hay una exportación acreditada de S00005 en Python |
| **Evidencias y memoria** | `evidencias/dashboard/` (casos del dashboard y refresco de 60 s), `evidencias/verificacion/` (pruebas y `main.py` de la versión entregada), `memoria/Memoria_Python_NOVA_Sneakers.pdf` (la memoria técnica), `memoria/INFORME_TECNICO_PYTHON.md` (el informe técnico que pide la rúbrica) y `memoria/informe_ejecutivo.md` (el informe ejecutivo) |

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
04_Python/
├── README.md             este archivo
├── diccionario_datos.md  columnas, tipos, relaciones, DataFrames y variables derivadas
├── requirements.txt      dependencias con versión fija
├── main.py               ejecución por consola (modos real, sintetico y sintetico-errores)
├── app_dashboard.py      el dashboard Streamlit (solo orquesta y muestra)
├── generador_datos.py    el generador de datos SINTÉTICOS
├── modulos/              las funciones que usan main.py, el dashboard y las pruebas
│   │  Datos
│   ├── config.py             carpetas, formato, columnas, catálogos, criterios y umbrales
│   ├── pipeline.py           lectura y validación de los CSV, origen y guardado
│   ├── comprobaciones.py     comprobaciones rápidas de la fase 1
│   ├── calidad.py            las 12 reglas de calidad y los nulos por columna
│   │  Análisis
│   ├── analiticas.py         todos los DataFrames, variables derivadas, ABC e importes
│   ├── filtros.py            los seis filtros combinables (sin Streamlit)
│   ├── metadatos.py          fecha de corte, reglas, filtros, filas de origen y función de cada DataFrame
│   ├── kpis.py               los KPIs y su coherencia con SQL
│   ├── conciliacion.py       comparación con las consultas SQL de Acceso a Datos
│   ├── visualizaciones.py    los 10 gráficos (Matplotlib) y el de real frente a predicción
│   ├── informe.py            las cinco conclusiones del informe ejecutivo
│   │  Ciencia de datos
│   ├── estadistica.py        descriptivos, hipótesis y bootstrap
│   ├── segmentacion.py       RFM y KMeans
│   ├── prediccion.py         demanda mensual, baseline, regresión, MAE y RMSE
│   │  Dashboard
│   ├── actualizacion.py      ciclo de 60 s: comprobar, validar, recalcular, publicar y anotar
│   └── registro.py           registro de eventos (logs/registro_eventos.csv)
├── docs/                 documentación técnica por tema
│   ├── calidad_datos.md      las 12 reglas, gravedades y casos investigados
│   ├── conciliacion_sql.md   las consultas SQL (P-A a P-C y caso N), en qué se diferencian y resultados
│   ├── kpis_y_graficos.md    los KPIs con su fórmula, los DataFrames, los gráficos y el ABC
│   ├── datos_sinteticos.md   cómo se generan los datos sintéticos, sus hipótesis y la copia con errores
│   ├── estadistica.md        descriptivos, las tres hipótesis, el bootstrap y lo que no se puede afirmar
│   ├── segmentacion_y_prediccion.md  RFM, KMeans, predicción, resultados y análisis de errores
│   └── dashboard.md          el dashboard: pestañas, filtros, refresco, descargas y registro
├── memoria/
│   ├── Memoria_Python_NOVA_Sneakers.pdf  la memoria técnica completa (PDF)
│   ├── INFORME_TECNICO_PYTHON.md  el informe técnico que pide la rúbrica
│   └── informe_ejecutivo.md       las cinco conclusiones para producción y comercial
├── .streamlit/           tema del dashboard y opciones del servidor
├── Dockerfile            imagen del dashboard (la usa compose.yaml de la raíz)
├── .dockerignore         lo que no entra en la imagen (.venv, outputs, logs, evidencias, memoria…)
├── entrada_acc/          los cinco CSV de Acceso a Datos + ORIGEN.txt + conciliacion_sql/
├── datos_sinteticos/     limpios/ y con_errores/ (los escribe generador_datos.py)
├── outputs/              real/, sinteticos/ y sinteticos_con_errores/ (se generan; Git los ignora)
├── logs/                 registro de eventos del dashboard (se genera; Git lo ignora)
├── evidencias/
│   ├── dashboard/            capturas del dashboard en Edge (escritorio y móvil) y registro del caso K
│   └── verificacion/         salidas de las pruebas y de main.py de la versión entregada
└── tests/                14 archivos de pruebas con CSV inventados (nunca los reales)
```

**Por qué hay una línea `sys.path` al principio de `main.py`, `app_dashboard.py`,
`generador_datos.py` y de cada prueba.** Los módulos están en `modulos/`, pero se
siguen importando por su nombre (`import calidad`). Para eso, cada programa añade
esa carpeta a la lista de sitios donde Python busca módulos antes de importarlos:
`sys.path.insert(0, str(Path(__file__).resolve().parent / "modulos"))` (en las
pruebas, `parent.parent`, porque están en `tests/`). Así los comandos no cambian.
No se ha hecho un paquete (`modulos.calidad`) porque `metadatos.py` escribe en cada
CSV el nombre de la función que lo genera (por ejemplo `analiticas.modelos_abc`) y
`test_filtros.py` importa ese nombre con `importlib`; con un paquete cambiarían
esos textos. `modulos/config.py` calcula la carpeta del proyecto con
`.parent.parent`, así que las rutas (`entrada_acc/`, `outputs/`, `logs/`…) siguen
siendo las de `04_Python/`.

Dos archivos se conservan tal como se entregaron y citan rutas de antes de esta
organización: `entrada_acc/conciliacion_sql/LEEME.md` remite a `conciliacion_sql.md`
(ahora `docs/conciliacion_sql.md`) y `evidencias/dashboard/README.md` remite a
`dashboard.md` (ahora `docs/dashboard.md`).

En los documentos de `docs/` y `memoria/`, los módulos se nombran solo por su
archivo (por ejemplo `calidad.py`): todos están en `modulos/`, salvo `main.py`,
`app_dashboard.py` y `generador_datos.py`, que están en esta carpeta.

Ningún cálculo está en Streamlit: el dashboard solo llama a `actualizacion`,
`filtros`, `analiticas`, `kpis`, `metadatos`, `pipeline`, `registro`,
`visualizaciones` e `informe`, las mismas funciones que `main.py`, para que no haya
dos fórmulas para la misma cifra.

## Instalación

Hace falta **Python 3.12 o superior** (probado con 3.13.5). En Windows, el comando
`python` puede abrir la Microsoft Store en lugar de Python: usad el lanzador `py`.

En Windows, desde la carpeta `04_Python` (la del repositorio o la del ZIP de la
entrega):

```
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
cd 04_Python\entrada_acc
psql -U postgres -d nova_sneakers -f ..\..\02_Acceso_Datos\sql\16_exportar_csv_dashboard.sql
```

Después hay que poner en `entrada_acc/ORIGEN.txt` de qué base salen y su tipo en la
primera línea:
- `Tipo: PRUEBA`: base de prueba.
- `Tipo: REAL`: base del equipo.
- `Tipo: SINTETICO`: generado por Python.

Ese tipo se escribe en todos los resultados. Para la conciliación hacen falta
también los resultados de las consultas SQL en `entrada_acc/conciliacion_sql/`:
seis CSV, `P-A`, `P-B` y `P-C`, y `N-1`, `N-2` y `N-3` del caso N (ver
`docs/conciliacion_sql.md`).

El 16 sobrescribe los cinco CSV de `entrada_acc/` que trae el repositorio. Para
volver a los del repositorio: `git restore 04_Python/entrada_acc` (más detalle en
`manuales/MANUAL_INSTALACION.md`, en la raíz del repositorio).

Python nunca modifica la carpeta de entrada: solo la lee, y `guardar_salida` se
niega a escribir en ella.

## Contrato de datos (resumen)

Son cinco CSV con nombre fijo. El detalle de cada columna (significado, origen en
la base, tipo, valores, nulos y si es obligatoria) está en `diccionario_datos.md`.

| Archivo | Columnas (en este orden) |
|---|---|
| `clientes.csv` | `id_cliente`, `nombre`, `tipo`, `correo`, `telefono`, `activo` |
| `modelos.csv` | `id_modelo`, `nombre_modelo`, `descripcion`, `precio_base`, `activo` |
| `pedidos.csv` | `id_pedido`, `referencia`, `id_cliente`, `fecha_pedido`, `tipo_pedido`, `estado_pedido`, `estado_pago`, `personalizacion`, `cantidad_total`, `importe_total` |
| `lineas_pedido.csv` | `id_linea`, `id_pedido`, `sku`, `id_modelo`, `talla`, `cantidad`, `precio_unitario`, `importe_linea` |
| `stock.csv` | `sku`, `id_modelo`, `color`, `talla`, `activo`, `stock_disponible`, `fecha_corte` |

- **Formato:** UTF-8 (se acepta el BOM de Excel), coma como separador, cabecera en
  la primera fila, punto decimal, euros sin símbolo, fechas `AAAA-MM-DD HH:MM:SS`,
  lógicos `true`/`false` y una celda vacía es un nulo (nunca se convierte en 0).
- **Relaciones:** un pedido tiene un cliente; una línea, un pedido, un modelo y un
  SKU (vacío en las líneas X-NOVA); cada SKU del stock es un modelo, un color y una
  talla. Un pedido con tres líneas es **un** pedido.
- **Identificadores:** se leen como texto; sirven para unir tablas, nunca para
  sumar.
- **Fecha de corte:** solo la lleva `stock.csv`, y es la misma en todas sus filas.
- **Columnas obligatorias y tipos:** están en `modulos/config.py` (`ARCHIVOS`). Si
  falta una columna obligatoria, la regla 01 bloquea la carga.

## Ejecución

Desde la carpeta `04_Python`:

```
.venv\Scripts\python.exe main.py
.venv\Scripts\python.exe generador_datos.py
.venv\Scripts\python.exe main.py --modo sintetico
.venv\Scripts\python.exe main.py --modo sintetico-errores
.venv\Scripts\python.exe main.py --entrada CARPETA --salida CARPETA
.venv\Scripts\streamlit.exe run app_dashboard.py
```

La última línea abre el dashboard en `http://localhost:8501` (detalle en
`docs/dashboard.md`).

Cada modo tiene sus carpetas, para que los datos nunca se mezclen:

| Modo | Lee | Escribe |
|---|---|---|
| `real` (por defecto) | `entrada_acc/` (exportación de Acceso a Datos) | `outputs/real/` |
| `sintetico` | `datos_sinteticos/limpios/` | `outputs/sinteticos/` |
| `sintetico-errores` | `datos_sinteticos/con_errores/` | `outputs/sinteticos_con_errores/` |

`generador_datos.py` vuelve a crear las dos carpetas de `datos_sinteticos/`
(detalle en `docs/datos_sinteticos.md`).

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
genera (`modulos/metadatos.py`). Se enlaza con cada CSV por su nombre y su columna
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

## Con Docker

Desde la raíz del repositorio, `docker compose up -d --build` arranca también el
dashboard (servicio `dashboard` de `compose.yaml`, imagen hecha con el `Dockerfile`
de esta carpeta) en `http://localhost:8501`. Los pasos completos están en el
`README.md` de la raíz.

- **Los CSV no van dentro de la imagen.** `compose.yaml` monta
  `04_Python/entrada_acc` en `/app/entrada_acc` en **solo lectura** (`:ro`): una
  exportación nueva se ve en el siguiente refresco de 60 s sin reconstruir la
  imagen, y el contenedor no puede escribir en la carpeta de entrada.
- **El registro de eventos va al volumen `logs_dashboard`** (`/app/logs`): se
  conserva aunque se vuelva a crear el contenedor.
- La zona horaria es `Europe/Madrid` (si no, las horas saldrían en UTC) y el puerto
  solo se abre en este ordenador (`127.0.0.1:8501`).
- Dentro del contenedor, la aplicación no se ejecuta como administrador (usuario
  `nova`). El `Dockerfile` crea `/app/logs` para ese usuario antes de cambiar a él;
  lo comprueba `tests/test_regresiones.py`.
- El contenedor solo arranca el dashboard (`CMD` del `Dockerfile`); `main.py` y las
  pruebas se lanzan como en «Ejecución» y «Pruebas».

**Sin el resto del repositorio** (por ejemplo, desde el ZIP de la entrega, que no
trae `compose.yaml`), en PowerShell y desde la carpeta `04_Python`:

```
docker build -t nova-dashboard .
docker run -d --name nova-dashboard -p 127.0.0.1:8501:8501 -e TZ=Europe/Madrid `
  -v "${PWD}\entrada_acc:/app/entrada_acc:ro" -v nova_logs:/app/logs nova-dashboard
```

Es lo mismo que hace `compose.yaml`: los CSV en solo lectura y el registro en un
volumen (`nova_logs`). El dashboard queda en `http://localhost:8501`. Las pruebas
también se pueden pasar dentro del contenedor:
`docker exec nova-dashboard python -m unittest discover -s tests`. Para pararlo:
`docker rm -f nova-dashboard`.

## Calidad (`modulos/calidad.py`)

Doce reglas, una función por regla, con gravedad **bloqueante** (se detiene),
**recuperable** (se rechaza la fila) o **advertencia** (se mantiene y se avisa). Un
pedido se analiza entero o no se analiza. Nunca se corrige ni se inventa un valor.
Detalle en `docs/calidad_datos.md`.

## Análisis (`modulos/analiticas.py`)

- **`df_lineas_enriquecidas`:** una fila por línea, con pedido, cliente, modelo y color.
- **`df_pedidos_unicos`:** una fila por pedido, con su cliente y las métricas de sus líneas.

Cada `merge` lleva `validate=` e `indicator=True`, y para si multiplica filas o
pierde claves. Las 18 variables derivadas están en `diccionario_datos.md`.
Además de las dos vistas base, `calcular_tablas` construye las tablas de análisis
(entre ellas `pedidos_por_estado_pago`, pedidos e importe por estado de pago).
`importes_por_criterio` da pedidos, pares e importe de tres formas:
- registrados;
- no cancelados;
- confirmados en adelante.

Ninguna se llama «ingresos cobrados».

## KPIs y gráficos (`modulos/kpis.py` y `modulos/visualizaciones.py`)

- **KPIs:** 20, cada uno con fórmula, unidad, población y tabla de origen. 17 son
  calculables con los datos actuales y 3 salen como **NO CALCULABLE** con su motivo:
  margen (no hay coste), variación mensual (un solo mes) y cobertura (no hay 28
  días de historial).
- **Gráficos:** 10, de los 8 tipos que pide el apartado 6.6, y cada uno responde a
  una pregunta.

El detalle, con los valores de los datos de prueba y la clasificación ABC, está en
`docs/kpis_y_graficos.md`.

## Datos sintéticos y estadística (`generador_datos.py` y `modulos/estadistica.py`)

- **Datos sintéticos:** 40 clientes, 12 modelos, 900 pedidos, 1.777 líneas y 216
  SKU de stock, en 18 meses (de mayo de 2025 a octubre de 2026), con la semilla 2026.
  Pasan las 12 reglas sin ninguna incidencia. La copia con errores hace saltar las
  reglas de la 02 a la 12.
- **Estadística:** media, mediana, moda, desviación típica, percentiles y rango
  intercuartílico de tres variables, con qué estadístico representa mejor cada caso.
  Incluye tres hipótesis con su intervalo bootstrap y el ticket medio con su
  intervalo al 95 % (2.000 remuestreos, semilla 2026).

Nada de lo que sale de los datos sintéticos describe a los clientes reales de
NOVA. Detalle en `docs/datos_sinteticos.md` y `docs/estadistica.md`.

## Segmentación y predicción (`modulos/segmentacion.py` y `modulos/prediccion.py`)

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
completo) todo sale como NO CALCULABLE. Detalle en `docs/segmentacion_y_prediccion.md`.

## Dashboard (`app_dashboard.py`)

Seis pestañas: Dirección, Productos, Clientes, Inventario, Calidad y Predicción.

**También dentro del panel de administración.** La página «Análisis de datos» del panel de Álvaro (`01_Interfaces/admin/analisisAdmin.html`) carga este mismo dashboard en un marco, sin su barra de Streamlit y con la variante oscura del tema (`[theme.dark]` en `.streamlit/config.toml`, con los colores del panel). Dentro del panel funcionan igual los filtros, las descargas y el refresco de 60 s. A la página «Análisis de datos» solo entra el administrador del panel, pero el dashboard (puerto 8501) no tiene login propio: solo escucha en este ordenador, y aquí `http://localhost:8501` se abre sin pasar por el panel. Abierto por su cuenta, el dashboard sigue con el tema claro de siempre. Para verlo en el panel hacen falta los dos servidores: `npm start` (en `servidor-admin`) y `streamlit run app_dashboard.py` (aquí).

- **Origen siempre visible.** Puede ser la exportación de ACC (ahora PRUEBA), los
  sintéticos limpios o los sintéticos con errores, y nunca se mezclan.
- **Refresco real cada 60 s.** Con `st.fragment(run_every="60s")`, cada minuto
  vuelve a leer los CSV del disco, los valida y lo recalcula todo con la misma
  versión de los datos. También hay un botón «Actualizar ahora».
- **Estado del ciclo.** Correcto, sin cambios, datos inválidos o error de carga.
  Con datos bloqueados no se publica ninguna cifra.
- **Filtros.** Seis filtros combinables (periodo, modelo, talla, tipo, estado y
  cliente), hechos en `modulos/filtros.py`, fuera de Streamlit. Se mantienen con el
  refresco y «Restablecer filtros» los vacía todos.
- **Descargas.** Diez CSV en UTF-8, con su origen, sus filtros y sus metadatos
  (fecha de corte, función, reglas y filas de origen), y sin datos personales.
- **Registro.** `logs/registro_eventos.csv`, una fila por cada ciclo de
  comprobación (carga inicial, refresco de 60 s o «Actualizar ahora») y por cada
  una de las diez descargas, también la de `incidencias.csv` de la pestaña Calidad.

Los datos nuevos de PostgreSQL solo llegan cuando Acceso a Datos vuelve a
exportar los CSV. Detalle en `docs/dashboard.md`; las conclusiones, en
`memoria/informe_ejecutivo.md`.

## Prueba de datos nuevos y recuperación tras un CSV erróneo

Python solo lee CSV: un pedido nuevo en PostgreSQL **no aparece hasta que Acceso a
Datos vuelve a exportar** con el 16. Para repetirlo en la defensa:

1. Abrir el dashboard (`.venv\Scripts\streamlit.exe run app_dashboard.py`, o con
   Docker) con la exportación en `entrada_acc/` y apuntar las cifras de Dirección.
2. **Datos nuevos.** Dar de alta un pedido en la base (o cancelarlo, o cambiar el
   stock) y volver a exportar con el 16 en `entrada_acc/`. Con Docker sirve la
   misma carpeta del ordenador, porque está montada en el contenedor.
3. Esperar al siguiente ciclo de 60 s (o pulsar «Actualizar ahora»): el estado pasa
   a «Correcto» y cambian las cifras, sin contar nada dos veces. Si no ha cambiado
   ningún CSV, el estado es «Sin cambios» y la hora de «Última comprobación» sí
   cambia.
4. **CSV erróneo.** Sacar `pedidos.csv` de `entrada_acc/` (o dejar un CSV sin una
   columna obligatoria). Al minuto, «Error de carga» con el motivo, ninguna cifra
   nueva y, si se pide con el interruptor, el último resultado válido rotulado
   **DESACTUALIZADO** con su hora. Con incidencias bloqueantes (por ejemplo, una
   clave huérfana) sale «Datos inválidos» y tampoco se publica nada.
5. **Recuperación.** Devolver el archivo (o volver a exportar con el 16, o
   `git restore 04_Python/entrada_acc` para volver a los CSV del repositorio). En
   el siguiente ciclo vuelven las cifras. Si los CSV son idénticos a los de la
   última versión válida, el estado es «Sin cambios».

Por consola pasa lo mismo: con bloqueantes, `main.py` guarda `incidencias.csv`,
deja `estado_ejecucion.csv` en `BLOQUEADO` y termina con código 1. Cada ciclo queda
en `logs/registro_eventos.csv`.

Se hizo así en Edge el 9 y el 10/11 con una copia de `entrada_acc/` (capturas
`refresco_*` de `evidencias/dashboard/`; tabla en `docs/dashboard.md`). R2
(cancelación) y R3 (stock) se comprueban con CSV inventados en
`tests/test_actualizacion.py` y `tests/test_dashboard.py`. Falta repetirlo con la
exportación REAL de la base del equipo, que todavía no existe.

## Pruebas

Desde la carpeta `04_Python`:

```
.venv\Scripts\python.exe -m unittest discover -s tests -v
```

**278 pruebas en 14 archivos.** Cada una crea sus propios CSV en una carpeta
temporal. Pasan todas en Windows y dentro de Docker. La última,
`test_descarga_de_incidencias`, comprueba que `incidencias.csv` trae las incidencias
con su origen y que su descarga queda anotada en el registro.

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
| `test_filtros.py` | 18 | filtros combinados (también el de cliente), sin duplicados, KPIs filtrados, inventario con umbral, CSV descargado con sus metadatos (ver `docs/dashboard.md`) |
| `test_actualizacion.py` | 22 | ciclo de 60 s, pruebas R1 a R5, CSV ausente o corrupto, bloqueo, cambio de origen, registro e informe ejecutivo (prioridad, impacto y sustento) |
| `test_dashboard.py` | 15 | la aplicación Streamlit con `AppTest`: pestañas, orígenes, bloqueo, filtros (también el de cliente), filtros y pestaña que se mantienen al refrescar, R6 (filtrado cruzado), refresco, botón «Actualizar ahora» y descarga de `incidencias.csv` |
| `test_regresiones.py` | 12 | ver abajo: los seis fallos que encontró la auditoría del 18/11 (PR #16), dos pruebas por fallo |

`test_regresiones.py` (cada fallo tiene dos pruebas):
- si no se puede escribir el registro de eventos, el ciclo sigue y lo avisa, y el
  `Dockerfile` crea `/app/logs` para el usuario `nova` antes de `USER nova`;
- una línea con `id_pedido` vacío se rechaza (regla 09) y los pares cuadran en
  todas las tablas;
- un `pedidos.csv` sin la columna `personalizacion` es un bloqueo de la regla 01 con
  un mensaje claro, y ni `main.py` ni el dashboard se caen;
- un `stock.csv` sin ninguna `fecha_corte` válida, o los cinco CSV solo con
  cabecera, bloquean;
- una ejecución de `main.py` que se corta deja `estado_ejecucion.csv` en
  `EN CURSO`, y una completa no duplica los metadatos;
- con identificadores vacíos, las comprobaciones rápidas dan `ERROR` en vez de
  romperse.

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
