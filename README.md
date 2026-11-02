# NOVA Sneakers

Proyecto intermodular de 2.º DAM: una marca de zapatillas con web de
catálogo, base de datos PostgreSQL, aplicación Java de pedidos, procesos Java
para preparar la fabricación y análisis de datos en Python.

## Estructura

| Carpeta | Contenido |
| --- | --- |
| `acceso-datos/sql/` | Los 21 scripts de PostgreSQL: esquema, funciones, triggers, datos de demostración, seguridad, auditoría, pruebas y exportaciones a CSV |
| `acceso-datos/documentacion/` | Instalación de la base, decisiones de diseño, seguridad y pruebas (`README.md`) y modelo relacional |
| `acceso-datos/modelo/`, `acceso-datos/modelo-er/` | Modelo de pgModeler (`.dbm`) y diagrama entidad-relación (`.drawio`) |
| `acceso-datos/java/` | Aplicación Swing + JDBC: login, pedidos, consultas con filtros, indicadores, usuarios y archivos TXT, JSON y CSV |
| `psp/` | `ProcesadorPedidosCustom`, que lee el CSV de fabricación y lanza tres procesos hijos para generar la ficha del taller. Pruebas en `psp/pruebas/` |
| `psp/src/Psp/` | Analizador de tallas con protocolo de líneas; el coordinador lo usa como segundo hijo |
| `python-analisis/` | Calidad de datos, KPIs, gráficos, estadística, segmentación, predicción y dashboard Streamlit |
| `interfaces/cliente/` | Web de la marca: escaparate, catálogo con precios, ficha, probador, formulario Custom, contacto, inicio de sesión y tienda |
| `interfaces/admin/` | Panel de administración |
| `servidor-admin/` | Servidor Node + Express que conecta el panel y la tienda con PostgreSQL |
| `integracion/` | Caso común SO024, formatos de fabricación y borrador del recorrido con Odoo |
| `pruebas/` | Resultados y capturas de las pruebas de cada parte, y la muestra `fixtures/custom40.csv` |
| `scripts/` | Comprobaciones rápidas de la web y de PSP |
| `docs/` | Lista de comprobaciones manuales |
| `odoo/` | Vacía: solo tiene `.gitkeep` |

## Requisitos

- **PostgreSQL 17** (probado con la 17.11) y `psql` o pgAdmin.
- **JDK 17** (probado con el 17.0.12). La aplicación Java necesita el driver
  `postgresql-42.7.14.jar` en `acceso-datos/java/lib/`. Hay que descargarlo:
  no se sube al repositorio.
- **Python 3.12 o superior** (probado con 3.13), con las dependencias de
  `python-analisis/requirements.txt`.
- **Node 20.6 o superior** (probado con 24.15), solo para el panel y la
  tienda. Las dependencias son `express` y `pg`, con las versiones de
  `servidor-admin/package-lock.json`.

## Reconstruir la base de datos

Sobre una base **nueva y vacía** (`CREATE DATABASE nova_sneakers;`), se lanzan
los scripts de `acceso-datos/sql/` con `psql -U postgres -d nova_sneakers -f
<script>`. El número del archivo no es el orden de ejecución. El orden es este:

1. Instalación: `sneaker-factory-esquema.sql`, `04_xnova.sql`,
   `02_funciones.sql`, `03_triggers.sql`, `05_datos_prueba.sql`,
   `07_seguridad.sql` y `08_auditoria.sql`.
2. Consultas y pruebas: `06_consultas.sql`, `09_pruebas.sql`,
   `10_caso_custom.sql`, `11_dml_ejemplos.sql` y `12_consultas_panel.sql`.
3. `13_activar_usuarios.sql` (contraseñas de `admin.demo`, `tienda.demo` y
   `taller.demo`) y `14_caso_custom_persistente.sql` (guarda el pedido
   `CUSTOM-40`).
4. Exportaciones: `15_exportar_fabricacion.sql` (CSV para PSP) y
   `16_exportar_csv_dashboard.sql` (los cinco CSV de Python). Dejan los
   archivos en la carpeta desde la que se lanza `psql`.
5. Usuarios de conexión y ampliaciones: `17_usuario_java.sql`,
   `18_datos_so024.sql`, `19_usuario_web.sql`, `20_tienda_web.sql` y
   `21_catalogo_web.sql`.

**El 09 va antes del 18, el 20 y el 21.** Esos tres añaden modelos, tablas y
funciones, y algunas comprobaciones del 09 cuentan los de la instalación
original: después darían `FAIL`. El 13 también va después del 09, porque las
pruebas A1 y A2 comprueban que las cuentas llegan sin contraseña. El 17 y el 19
se pueden lanzar en cualquier momento después del 7.

**Piden contraseña por teclado:** el 13 (las tres cuentas de demostración), el
14 (la de `tienda.demo`), el 17 (`java_nova`), el 19 (`web_nova`) y el 20
(`tienda_nova`). Ninguna se guarda en el repositorio. El 18 no pide nada, pero
necesita `-v precio=… -v color=… -v stock=…`; sin esos valores no inserta nada.

Necesitan un usuario administrador `sneaker-factory-esquema.sql`,
`07_seguridad.sql`, el 13, el 17, el 19 y el 20. El detalle de cada script está
en `acceso-datos/documentacion/README.md`.

## Cómo se ejecuta cada parte

### Aplicación Java (Acceso a Datos)

1. Lanzar `17_usuario_java.sql` y copiar
   `acceso-datos/java/conexion.properties.ejemplo` como
   `conexion.properties`, con la contraseña de `java_nova`. Ese archivo está en
   el `.gitignore`.
2. `acceso-datos\java\ejecutar.bat` compila y abre la ventana de login.

Más detalle en `acceso-datos/java/README.md`.

### PSP

Desde `psp`:

```
javac -encoding UTF-8 -d clases *.java pruebas\*.java src\Psp\*.java
java -cp clases ProcesadorPedidosCustom datos\custom40_fabricacion_psp.csv
```

La ficha queda en `psp\salidas\ficha_taller_CUSTOM-40.txt`. Para otro pedido
se usa el CSV que genera `15_exportar_fabricacion.sql`, por ejemplo con
`-v referencia=SO024`. Más detalle en `psp/README.md`.

### Python

Desde `python-analisis`:

```
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
.venv\Scripts\streamlit.exe run app_dashboard.py
```

`main.py` trabaja por consola con los CSV de `entrada_acc/` (los genera el 16)
y deja los resultados en `outputs/`. El dashboard se abre en
`http://localhost:8501`. Los modos sintéticos y el resto de opciones están en
`python-analisis/README.md`.

### Web, panel y tienda

Sin servidor, `interfaces/cliente/index.html` se puede abrir directamente o
con un servidor estático desde la raíz del repositorio:

```
py -m http.server 8000 --bind 127.0.0.1
```

Así funcionan el escaparate, el catálogo, la ficha, el probador, Custom y
Contacto en `http://127.0.0.1:8000/interfaces/cliente/`. El inicio de sesión,
la tienda y los datos del panel necesitan `servidor-admin`:

1. Lanzar `19_usuario_web.sql`; para la tienda, también el 20 y el 21.
2. En `servidor-admin`, `npm ci`.
3. Copiar `.env.example` como `.env` y escribir las contraseñas de `web_nova`
   y, para la tienda, de `tienda_nova`. El `.env` no se sube a Git.
4. `npm start` y abrir `http://127.0.0.1:3000` (panel, con `admin.demo`) o
   `http://127.0.0.1:3000/tienda/` (tienda).

Más detalle en `servidor-admin/README.md`.

## Pruebas

| Parte | Cómo se lanza | Resultado esperado |
| --- | --- | --- |
| SQL | Scripts 09 a 16, en el orden de arriba | 123 PASS, 0 FAIL y 1 ERROR previsto (la S4b: PostgreSQL deniega `descontar_stock` al cliente a propósito) |
| Java | `acceso-datos\java\pruebas.bat` (pide las contraseñas de demostración) | 47 PASS, 0 FAIL |
| PSP | En `psp`, tras compilar: `java -cp clases PruebasPsp` | 27 de 27 |
| Python | En `python-analisis`: `.venv\Scripts\python.exe -m unittest discover -s tests -v` | 249 pruebas OK |
| Panel | En `servidor-admin`: `npm test` (con las variables `PRUEBA_*` de su README) | 16 de 16 |
| Tienda | En `servidor-admin`: `npm run test:tienda`, solo con `PRUEBA_TIENDA_BASE_DESECHABLE=si` | 23 de 23 |

`pruebas.bat` deja pedidos `PRUEBA-*` en la base y las pruebas de la tienda
crean clientes y pedidos de verdad: conviene lanzarlas sobre una base de
prueba. Los resultados guardados y las capturas están en `pruebas/` y en
`python-analisis/evidencias/`.

Hay además dos comprobaciones rápidas, desde la raíz:

```
python3 scripts/comprobar_web.py
python3 scripts/comprobar_psp.py
```

La primera comprueba que existen los recursos locales que enlaza la web; no
evalúa el diseño ni la API. La segunda necesita `java` y `javac` en el PATH,
compila en una carpeta temporal y comprueba `ValidadorPedidoCustom`,
`LanzadorValidacion` y las pruebas del paquete `Psp`. Ahora mismo se para en la
primera comprobación: espera que el validador conteste solo
`OK;CUSTOM-40;4;40`, y desde el commit `81db6e5` el validador añade después
los datos normalizados. Si se compara solo esa primera línea, el resto pasa.
En Windows, `python3`
puede no existir: se usa `py`. La lista de comprobaciones manuales está en
`docs/PRUEBAS_MANUALES.md` y se escribió antes de conectar el panel y la
tienda.

## Estado del caso común SO024

`integracion/caso-comun-SO024.md` recoge el pedido del enunciado (SO024, Club
Halcones, Runner X, 40 pares, tallas 38–46) y los **7 datos que faltan por
acordar**: el reparto por talla, el color, el precio, el stock, el texto de la
personalización, el SKU en Odoo y el número del pedido en Odoo.

Mientras tanto, el recorrido se ha probado con datos provisionales en una base
desechable: el 18, el alta y la confirmación de SO024 con los métodos de la
aplicación Java, la exportación con el 15 (`-v referencia=SO024`), la ficha de
PSP, la exportación con el 16 y Python. Funciona, pero con cantidades
inventadas, y esa prueba no está guardada en el repositorio.

## Odoo

**No hay ninguna evidencia de Odoo en el repositorio: está pendiente
(Berme).** `odoo/` está vacía e `integracion/recorrido-manual-odoo.md` es un
borrador de cómo se haría el recorrido a mano, no una prueba.

## Ampliaciones

La tienda online (cuentas de cliente, carrito y pago simulado) y la conexión
del panel de administración con PostgreSQL a través de `servidor-admin` son
**ampliaciones que no pide ninguna rúbrica**. El panel es solo de lectura y en
la tienda no se cobra nada.

## Limitaciones conocidas

- Odoo y los datos de SO024, como se explica arriba.
- Los CSV de `python-analisis/entrada_acc/` salen de una base de prueba, no de
  la del equipo.
- Los precios y las tallas por colección de la web (`datosColeccion` en
  `interfaces/cliente/js/modelos.js`) son provisionales. El probador es una
  aproximación visual y no recomienda tallas.
- Las pruebas de navegador (Playwright, axe y Lighthouse) se hicieron con
  scripts que no están en el repositorio: solo se guardan sus resultados.
- Las capturas de `pruebas/interfaces/` y `pruebas/tienda/` son anteriores a
  la integración y no muestran la parte del rediseño de tarjetas de Álvaro que
  se ha incorporado.
- PSP procesa un pedido por archivo y solo en CSV. Queda por decidir qué se
  hace con la versión anterior (`LanzadorValidacion` y el `AnalizadorTallas` de
  la raíz de `psp/`).
- El servidor guarda las sesiones en memoria, y el panel necesita internet
  para los iconos y los gráficos. El resto de límites del panel y de la tienda
  están en `servidor-admin/README.md`.

El formato del CSV de fabricación está descrito en
`integracion/contrato-fabricacion.md`.
