# NOVA Sneakers

Proyecto intermodular de 2.º DAM (Omar, Álvaro y Berme): una marca de zapatillas con web de catálogo, base de datos PostgreSQL, aplicación Java de pedidos, procesos Java para preparar la fabricación y análisis de datos en Python. El caso común es el pedido personalizado **SO024** del Club Halcones (Runner X, 40 pares, tallas 38–46).

**Estado a 13/11/2026** (detalle en `06_Intermodular/rubricas/MATRIZ_RUBRICAS.md`):

| Parte | Estado |
|---|---|
| Interfaces (web) | Hecha y probada en Edge. Falta la prueba de usabilidad **con personas** |
| Acceso a Datos (PostgreSQL + Java) | Hecha y probada. Faltan el E-R en PNG, la memoria y el SO024 oficial |
| PSP | Hecha y probada (27/27). SO024 solo con datos **PROVISIONALES** |
| Python | Hecho y probado (265 pruebas). Los CSV son de una base de **PRUEBA**: falta la exportación **REAL** |
| Odoo | PDF de Berme recibido; pendiente conciliar códigos y ejecutar el SO024 oficial. Ver `05_Odoo/README.md` |
| SO024 | **PROVISIONAL.** Faltan los 7 datos que tienen que acordar los tres (`06_Intermodular/SO024/caso-comun-SO024.md`) |

## Estructura: una carpeta por asignatura

Cada asignatura tiene su carpeta con su código, sus pruebas, sus evidencias y su memoria, y un `README.md` que explica qué hace, con qué se hace, qué necesita, cómo se arranca, qué pruebas tiene, qué requisitos de la rúbrica cubre, cómo se conecta con las demás y dónde están sus evidencias. Lo que comparten varias asignaturas está una sola vez, sin copias.

```
NOVA/
├── 01_Interfaces/        Web de la marca y tienda (cliente/), panel de administración (admin/), portal del trabajador (trabajador/)
├── 02_Acceso_Datos/      PostgreSQL (sql/, documentacion/, modelo/, modelo-er/) y aplicación Java Swing + JDBC (java/)
├── 03_PSP/               Procesador de pedidos Custom con tres procesos hijos (y el analizador de tallas en src/Psp/)
├── 04_Python/            Calidad de datos, KPIs, estadística, segmentación, predicción y dashboard Streamlit
├── 05_Odoo/              Estado de Odoo y preparación de SO024 (PDF en odoo/documentacion/)
├── 06_Intermodular/      SO024, memoria común, manuales, matrices de rúbricas, defensa y regresión completa
├── servidor-admin/       Servidor Node + Express, COMPARTIDO: da servicio a la tienda, al panel y al portal
├── scripts/              Comprobaciones rápidas de la web y de PSP
├── README.md
└── .gitignore
```

Dentro de cada asignatura: `evidencias/` guarda los resultados y las capturas de sus pruebas, y `memoria/` su documento de entrega.

### Mapa de rutas y componentes

| Qué buscas | Dónde está |
| --- | --- |
| Memoria técnica común (9 puntos) | `06_Intermodular/memoria/MEMORIA.md` |
| Memoria de Acceso a Datos | `02_Acceso_Datos/memoria/MEMORIA_ACCESO_DATOS.md` |
| Documentación de PSP | `03_PSP/memoria/DOCUMENTACION_PSP.md` |
| Informe técnico de Python | `04_Python/memoria/INFORME_TECNICO_PYTHON.md` |
| Estrategia de pruebas y usabilidad de Interfaces | `01_Interfaces/memoria/` |
| Estado de cada requisito de cada rúbrica | `06_Intermodular/rubricas/MATRIZ_RUBRICAS.md` |
| Qué enseñar para cada bloque | `06_Intermodular/rubricas/MATRIZ_EVIDENCIAS.md` |
| Instalación paso a paso y guion de la demostración | `06_Intermodular/manuales/` |
| Caso común SO024 y los 7 datos pendientes | `06_Intermodular/SO024/` |
| Defensa y presentación | `06_Intermodular/defensa/` |
| Regresión completa del 13/11 | `06_Intermodular/evidencias/regresion-final/README.md` y, sobre el árbol limpio, `06_Intermodular/evidencias/regresion-limpieza/README.md` |
| Odoo (lo que falta) | `05_Odoo/CHECKLIST_ODOO_BERME.md` |

```
                     Web (01_Interfaces/cliente)  ─┐
 Panel (01_Interfaces/admin) y portal (…/trabajador) ─┼─► servidor-admin (Node) ─► PostgreSQL (02_Acceso_Datos/sql)
                                                    ┘                                   │
 Aplicación Java (02_Acceso_Datos/java) ──── JDBC ──────────────────────────────────────┤
                                                                                        ├─ script 15 ─► CSV ─► PSP (03_PSP) ─► ficha del taller
                                                                                        └─ script 16 ─► 5 CSV ─► Python (04_Python) ─► dashboard
 Odoo (05_Odoo, PENDIENTE) ◄── mismos identificadores de SO024 (06_Intermodular/SO024) ──► PostgreSQL
```

En todas las asignaturas hemos trabajado los tres: quién hizo cada cambio se ve con `git log --follow <archivo>`.

### Si vienes de la estructura anterior

Hasta el 13/11 las carpetas eran `interfaces/`, `acceso-datos/`, `psp/`, `python-analisis/`, `odoo/`, `integracion/`, `docs/` y `pruebas/`. Se movieron con `git mv`, así que la historia y los autores siguen con `git log --follow`. En un clon que ya existía:

- Git mueve los archivos versionados, pero **no** lo que está ignorado. Hay que pasar a mano: `acceso-datos/java/conexion.properties` y `acceso-datos/java/lib/*.jar` a `02_Acceso_Datos/java/`, y el entorno de Python (`python-analisis/.venv`) a `04_Python/.venv` (o crearlo de nuevo). `servidor-admin/.env` no cambia de sitio.
- Las carpetas viejas que se queden con esos restos están en el `.gitignore`, para que no se suban por error. Cuando estén vacías, se pueden borrar.
- Una rama empezada antes de la reorganización se puede fusionar (se probó el 13/11 con una rama de ejemplo):
  - Los cambios en archivos que ya existían se aplican en su ruta nueva.
  - Los archivos **nuevos** dentro de una carpeta que se movió entera (`interfaces/`, `acceso-datos/`, `psp/`, `python-analisis/` o una subcarpeta de `pruebas/`) Git los pone en la carpeta nueva y lo marca como conflicto de ubicación (*file location*): se revisa y se confirma con `git add`.
  - Los archivos **nuevos** en `odoo/` o en `docs/` se quedan en la carpeta vieja (la de Odoo estaba vacía y la de documentación se repartió entre varias): hay que moverlos a mano antes del commit de la fusión, por ejemplo `git mv odoo/README.md 05_Odoo/README.md`.

## Requisitos

- **PostgreSQL 17** (probado con la 17.11) y `psql` o pgAdmin.
- **JDK 17** (probado con el 17.0.12). La aplicación Java necesita el driver `postgresql-42.7.14.jar` en `02_Acceso_Datos/java/lib/`. Hay que descargarlo (no se sube al repositorio) y crear antes la carpeta `lib`.
- **Python 3.12 o superior** (probado con 3.13.5), con las versiones exactas de `04_Python/requirements.txt`: pandas 3.1.1, numpy 2.5.4, matplotlib 3.11.2, scikit-learn 1.9.1 y streamlit 1.67.0.
- **Node 20.6 o superior** (probado con 24.15), solo para el panel, el portal y la tienda. Dependencias exactas en `servidor-admin/package-lock.json`: express 5.3.0, pg 8.23.1 y nodemailer 10.5.0 (`npm ci`).

El paso a paso completo, probado el 13/11 sobre un clon nuevo y una base vacía, está en **`06_Intermodular/manuales/MANUAL_INSTALACION.md`**.

## Reconstruir la base de datos

Sobre una base **nueva y vacía** (`CREATE DATABASE nova_sneakers;`), se lanzan los scripts de `02_Acceso_Datos/sql/` con `psql -U postgres -d nova_sneakers -f <script>`. **El número del archivo no es el orden de ejecución.** El orden es este:

1. Instalación: `sneaker-factory-esquema.sql`, `04_xnova.sql`, `02_funciones.sql`, `03_triggers.sql`, `05_datos_prueba.sql`, `07_seguridad.sql` y `08_auditoria.sql`.
2. Usuarios de conexión: `17_usuario_java.sql` (Java) y `19_usuario_web.sql` (servidor).
3. Consultas y pruebas: `06_consultas.sql`, `09_pruebas.sql`, `10_caso_custom.sql`, `11_dml_ejemplos.sql` y `12_consultas_panel.sql`.
4. `13_activar_usuarios.sql` (contraseñas de `admin.demo`, `tienda.demo` y `taller.demo`) y `14_caso_custom_persistente.sql` (guarda el pedido `CUSTOM-40`).
5. Exportaciones: `15_exportar_fabricacion.sql` (CSV para PSP) y `16_exportar_csv_dashboard.sql` (los cinco CSV de Python). Dejan los archivos en la carpeta desde la que se lanza `psql`.
6. Ampliaciones: `20_tienda_web.sql`, `21_catalogo_web.sql`, `22_reparto_panel.sql` (el botón «Marcar en reparto»; después del 09, el 19 y el 20) y `23_portal_trabajador.sql` (el portal del trabajador; después del 19 y el 22).
7. Al final, y solo con los datos acordados: `18_datos_so024.sql` (necesita `-v precio=… -v color=… -v stock=…`; sin ellos no inserta nada).

**El 09 va antes del 13, el 18, el 20 y el 21.** Algunas comprobaciones del 09 cuentan los objetos de la instalación original o esperan cuentas sin contraseña: después darían `FAIL`. El 17 y el 19 se pueden lanzar en cualquier momento después del 07.

**Piden contraseña por teclado:** el 13 (las tres cuentas de demostración y otra vez la de `admin.demo`), el 14 (la de `tienda.demo`), el 17 (`java_nova`), el 19 (`web_nova`) y el 20 (`tienda_nova`). Ninguna se guarda en el repositorio.

Necesitan un usuario administrador `sneaker-factory-esquema.sql`, `07_seguridad.sql`, el 13, el 17, el 19, el 20, el 22 y el 23. El detalle de cada script está en `02_Acceso_Datos/documentacion/README.md`.

## Cómo se arranca cada parte

### Aplicación Java (Acceso a Datos)

1. Lanzar `17_usuario_java.sql` y copiar `02_Acceso_Datos/java/conexion.properties.ejemplo` como `conexion.properties`, con la contraseña de `java_nova`. Ese archivo está en el `.gitignore`.
2. `02_Acceso_Datos\java\ejecutar.bat` compila y abre la ventana de login.

Más detalle en `02_Acceso_Datos/java/README.md`.

### PSP

Desde `03_PSP`:

```
javac -encoding UTF-8 -d clases *.java pruebas\*.java src\Psp\*.java
java -cp clases ProcesadorPedidosCustom datos\custom40_fabricacion_psp.csv
```

La ficha queda en `03_PSP\salidas\ficha_taller_CUSTOM-40.txt`. Para otro pedido se usa el CSV que genera `15_exportar_fabricacion.sql`, por ejemplo con `-v referencia=SO024`. Más detalle en `03_PSP/README.md`.

### Python

Desde `04_Python`:

```
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
.venv\Scripts\streamlit.exe run app_dashboard.py
```

`main.py` trabaja por consola con los CSV de `entrada_acc/` (los genera el 16) y deja los resultados en `outputs/`. El dashboard se abre en `http://localhost:8501` y se refresca solo cada 60 s. Los modos sintéticos y el resto de opciones están en `04_Python/README.md`.

### Web, panel, portal del trabajador y tienda

Sin servidor, `01_Interfaces/cliente/index.html` se puede abrir directamente o con un servidor estático desde la raíz del repositorio:

```
py -m http.server 8000 --bind 127.0.0.1
```

Así funcionan el escaparate, el catálogo, la ficha, el probador, Custom y Contacto en `http://127.0.0.1:8000/01_Interfaces/cliente/`. El inicio de sesión, la tienda, los datos del panel y el portal del trabajador necesitan `servidor-admin`:

1. Lanzar `19_usuario_web.sql`; para la tienda, también el 20 y el 21; para el reparto, el 22; para el portal del trabajador, el 23.
2. En `servidor-admin`, `npm ci`.
3. Copiar `.env.example` como `.env` y escribir las contraseñas de `web_nova` y, para la tienda, de `tienda_nova`. El `.env` no se sube a Git.
4. `npm start` y abrir `http://127.0.0.1:3000/login.html`, la página de acceso única del personal: `admin.demo` (administrador) pasa al panel, `taller.demo` (trabajador) al portal del trabajador, y `tienda.demo` (comercial) recibe «sin permiso», porque trabaja con la aplicación Java. La tienda está en `http://127.0.0.1:3000/tienda/`.

5. Para la página **«Análisis de datos»** del panel (el dashboard de Python dentro del panel de administración), arrancar también Streamlit, en otra consola:

   ```
   cd 04_Python
   .venv\Scripts\streamlit.exe run app_dashboard.py
   ```

   El panel lo muestra dentro de su propia página, con los colores del panel, en `http://127.0.0.1:3000/analisisAdmin.html` (solo para el administrador). Si Streamlit no está arrancado, la página explica cómo arrancarlo. Streamlit solo escucha en este ordenador (`04_Python/.streamlit/config.toml`, `address = "localhost"`). No tiene login propio: desde otro equipo no se puede abrir, pero en este ordenador `http://localhost:8501` se abre sin pasar por el panel.

El conector de Odoo de Berme (`servidor-admin/odoo.js`) está **desactivado** mientras falten `ODOO_URL`, `ODOO_DB` y `ODOO_API_KEY`, y las rutas de `servidor-admin/pedidos.js` (crear pedidos y enviarlos a Odoo) **no se montan**. Más detalle en `servidor-admin/README.md`.

## Pruebas

Todas sobre una base de **prueba**, nunca la del equipo: la batería Java deja pedidos `PRUEBA-*` y las de la tienda y el portal crean clientes, pedidos y cambios de verdad.

| Parte | Cómo se lanza | Resultado esperado | Regresión del 13/11 |
| --- | --- | --- | --- |
| SQL | Scripts 09 a 16, en el orden de arriba | 123 PASS, 0 FAIL y 1 ERROR previsto (la S4b: PostgreSQL deniega `descontar_stock` al cliente a propósito) | 123 / 0 / 1 |
| SQL de la tienda, del reparto y del portal | `psql -U postgres -d <copia de la base 01–23> -At -f <script>` con los tres scripts de `06_Intermodular/evidencias/regresion-final/01_sql/pruebas_usadas/` | 55, 37 y 50 PASS | 55 / 0, 37 / 0 y 50 / 0 |
| Java | `02_Acceso_Datos\java\pruebas.bat` (pide las contraseñas de demostración) | 47 PASS, 0 FAIL | 47 / 0; ventanas Swing 76 / 0 |
| PSP | En `03_PSP`, tras compilar: `java -cp clases PruebasPsp` | 27 de 27 | 27 / 27 |
| Python | En `04_Python`: `.venv\Scripts\python.exe -m unittest discover -s tests -v` | 265 pruebas OK | 265 OK; las 93 salidas de `main.py`, iguales a la referencia salvo los cambios hechos a propósito |
| Panel | En `servidor-admin`: `npm test` (con las variables `PRUEBA_*` de su README) | 23 de 23 con `PRUEBA_TIENDA_BASE_DESECHABLE=si` (sin ella, 22 y 1 saltada) | 23 / 23 |
| Tienda | En `servidor-admin`: `npm run test:tienda`, solo con `PRUEBA_TIENDA_BASE_DESECHABLE=si` | 39 de 39 | 39 / 39 |
| Login único y portal | En `servidor-admin`: `npm run test:portal`, con `PRUEBA_TIENDA_BASE_DESECHABLE=si` y `PRUEBA_SUPERUSUARIO` | 24 de 24 | 24 / 24 |
| Web en Edge | Scripts de Playwright y axe (fuera del repositorio: solo sus resultados) | Interfaces, web completa, mejoras, compra, reparto, login y portal, Ethereal | Ver `06_Intermodular/evidencias/regresion-final/README.md` |

Los scripts de `package.json` leen `servidor-admin/.env` (`--env-file`): tiene que existir. Los resultados guardados y las capturas están en la carpeta `evidencias/` de cada asignatura. **La regresión completa del 13/11, con la fecha, el entorno y el resultado de cada batería, está en `06_Intermodular/evidencias/regresion-final/`.** La misma regresión, repetida sobre el árbol ya reorganizado y simplificado, da lo mismo: `06_Intermodular/evidencias/regresion-limpieza/`.

Hay además dos comprobaciones rápidas, desde la raíz:

```
py scripts/comprobar_web.py
py scripts/comprobar_psp.py
```

La primera comprueba que existen los recursos locales que enlaza la web; no evalúa el diseño ni la API. La segunda necesita `java` y `javac` en el PATH. **Falla en la primera comprobación, y se sabe por qué:** espera que el validador conteste solo `OK;CUSTOM-40;4;40`, y desde el commit `81db6e5` el validador añade después los datos normalizados. El arreglo de Berme (`862e37d`, en `feature/berme`) no está en esta rama. La lista de comprobaciones manuales está en `06_Intermodular/manuales/PRUEBAS_MANUALES.md` y se escribió antes de conectar el panel y la tienda.

## Caso común SO024: PROVISIONAL

`06_Intermodular/SO024/caso-comun-SO024.md` recoge el pedido del enunciado y los **7 datos que faltan por acordar**: el reparto por talla, el color, el precio, el stock, el texto de la personalización, el SKU en Odoo y el número del pedido en Odoo.

Mientras tanto, el recorrido se ha probado de principio a fin con **datos PROVISIONALES** en una base desechable: el 18, el alta y la confirmación de SO024 con los métodos de la aplicación Java (no con la ventana), la exportación con el 15 (`-v referencia=SO024`), la ficha de PSP, la exportación con el 16 y Python, donde SO024 cuenta como un solo pedido de 9 líneas, 40 pares y 3.996,00 €. Las evidencias están en `03_PSP/evidencias/so024_provisional/` y `06_Intermodular/evidencias/regresion-final/06_so024_provisional/`, rotuladas PROVISIONAL. Cuando se acuerden los datos hay que repetirlo desde la ventana Java y en la base del equipo (`06_Intermodular/SO024/SO024_DATOS_PENDIENTES.md`).

## Odoo: documentación recibida, SO024 pendiente

La documentación de Berme ya está en `odoo/documentacion/Odoo-NOVA-Sneakers.pdf`. Incluye evidencias de Odoo y una venta histórica del Club Atletico NOVA; no equivale todavía al SO024 del Club Halcones. Hay que conciliar los códigos de Runner X con los de la base del equipo y acordar los siete datos oficiales.

La preparación actual y los criterios de aceptación están en `06_Intermodular/SO024/INTEGRACION_ODOO_SO024.md`. El conector conserva sus límites: `pedidos.js` no se monta y no se ha activado ni probado la API de esta candidata contra Odoo. Detalle del módulo: `05_Odoo/README.md`.

## Ampliaciones

La tienda online (cuentas de cliente, carrito, pago simulado y recibo por correo), la conexión del panel de administración con PostgreSQL, el botón «Marcar en reparto» y el portal del trabajador con su login único son **ampliaciones que no pide ninguna rúbrica**. El panel solo lee (salvo «Marcar en reparto»), el portal solo cambia algo con las dos funciones del script 23 y en la tienda no se cobra nada.

## Limitaciones conocidas

- Odoo y los datos de SO024, como se explica arriba.
- Los CSV de `04_Python/entrada_acc/` salen de una base de prueba, no de la del equipo (`ORIGEN.txt` dice `Tipo: PRUEBA`).
- Los precios y las tallas por colección de la web (`datosColeccion` en `01_Interfaces/cliente/js/modelos.js`) son provisionales. El probador es una aproximación visual y no recomienda tallas.
- Las pruebas de navegador (Playwright, axe y Lighthouse) se hicieron con scripts que no están en el repositorio: solo se guardan sus resultados y capturas.
- PSP procesa un pedido por archivo y solo en CSV. Queda por decidir qué se hace con la versión anterior (`LanzadorValidacion` y el `AnalizadorTallas` de la raíz de `03_PSP/`).
- El servidor guarda las sesiones en memoria, y el panel y el portal necesitan internet para los iconos y los gráficos. El resto de límites del panel, del portal y de la tienda están en `servidor-admin/README.md`.

El formato del CSV de fabricación está descrito en `06_Intermodular/SO024/contrato-fabricacion.md`.
