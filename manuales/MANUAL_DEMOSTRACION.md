# NOVA Sneakers · Demostración final de lo disponible

Guion de entrega del 13/11/2026, 15–20 minutos. Presenta S00005 del Club Atlético NOVA mediante el PDF de Berme; no requiere Odoo en ejecución ni crear SO024. Se usa una base nueva de PRUEBA montada con el manual; las contraseñas se preparan fuera de Git. No trabajar sobre una base con datos personales o pedidos reales.

## 0. Preparación

- SQL 01–23 en el orden del manual; el 18 solo se muestra sin parámetros (no inserta nada).
- Servidor con web_nova y tienda_nova; Node, PostgreSQL y Streamlit en marcha.
- Web en `http://127.0.0.1:3000/tienda/`, login del personal en `/login.html`; Streamlit en `http://localhost:8501`.
- `04_Python/entrada_acc/ORIGEN.txt` conserva `Tipo: PRUEBA`. No cambiar a REAL para la defensa.
- PDF de Berme y logs de la regresión del 13/11 disponibles como respaldo.
- Si 8501 está ocupado, usar el servicio acordado para la demo o cerrar solo el propio; la página integrada espera 8501. No cambiar puertos del profesor sin comprobarlo.

## 1. Presentación y web (3 min)

Explicar la marca y la organización por asignaturas. Abrir catálogo, filtrar y buscar, ver ficha y probador conceptual. Mostrar el diseño BEM en escritorio y móvil. El probador no es una medición clínica ni una prueba física de talla.

En Custom, preparar una solicitud ilustrativa de 40 pares. Pulsar SIMULAR ENVÍO y leer el aviso: no se registra un pedido. El SO024 que muestra la web es el ejemplo del enunciado; no registra una venta en Odoo ni crea S00005. No hay SKU conciliado entre sistemas.

## 2. Exportación y PSP (2 min)

Desde la raíz, con la base de PRUEBA en PGHOST/PGPORT y el usuario de instalación:

```powershell
New-Item -ItemType Directory -Force salidas | Out-Null
cd salidas
psql -U postgres -d nova_sneakers -f ..\02_Acceso_Datos\sql\15_exportar_fabricacion.sql
cd ..\03_PSP
javac -encoding UTF-8 -d clases *.java pruebas\*.java src\Psp\*.java
java -cp clases ProcesadorPedidosCustom ..\salidas\fabricacion_psp.csv
type salidas\ficha_taller_CUSTOM-40.txt
java -cp clases ProcesadorPedidosCustom datos\prueba_cantidad_cero.csv
cd ..
```

El 15 exporta el CUSTOM-40 existente (40 pares); no exporta automáticamente el pedido opcional de un par del paso anterior. Explicar padre, tres hijos, stdin/stdout/stderr, código 0 y rechazo 2. La ficha no sustituye una orden de Odoo.

## 3. Python y dashboard integrado (3 min)

Desde 04_Python, ejecutar `.venv\Scripts\python.exe main.py` y `.venv\Scripts\streamlit.exe run app_dashboard.py`. Mostrar Calidad, Dirección, Productos y Predicción. Enseñar la etiqueta PRUEBA y distinguir el laboratorio sintético. Python lee CSV; no sincroniza por sí solo con PostgreSQL.

En el panel, entrar como admin.demo y abrir «Análisis de datos»: el iframe muestra Streamlit. Se necesita el servicio en 8501. El refresco vuelve a leer/validar cada 60 s, pero una venta nueva no aparece si no se exportan y concilian los CSV. No prometer «un pedido más» sin haber hecho esa exportación.

## 4. Tienda, pedidos y recibos (3 min)

Registrar un cliente ficticio nuevo (`demo.<hora>@example.com`), añadir una talla disponible al carrito y completar el checkout con pago SIMULADO. Mostrar el pedido confirmado y «Mis pedidos». Se puede ensayar un pago rechazado con la opción de simulación y comprobar el mensaje.

El recibo por correo depende del proveedor y de su configuración. Si no está configurado, no prometer entrega al buzón. Las 39 pruebas de tienda incluyen construcción MIME, recibos y fallos mediante transporte Nodemailer de prueba; no son un envío SMTP real de este cierre.

## 5. Panel y portal del trabajador (2 min)

admin.demo: ver pedidos, inventario, clientes y auditoría, con datos de la base. taller.demo: entrar al portal y mostrar solo sus operaciones permitidas, localizar un pedido de prueba en «Pedidos» y cambiar su estado (lo que permite su rol; el portal no tiene vista de detalle). tienda.demo (comercial) no tiene panel web: el acceso se deniega por diseño.

## 6. Odoo y límites (2 min)

Abrir `odoo/documentacion/Odoo-NOVA-Sneakers.pdf`: instalación y servicio, venta S00005 del Club Atlético NOVA, fabricación, entrega, factura y variantes. Son evidencias aportadas por Berme, no una conexión en vivo desde este entorno.

Decir literalmente: «El conector NOVA → Odoo no se ha verificado contra una instalación real accesible desde este entorno. Sus rutas no se activan en el servidor principal. Nuestro caso de Odoo es S00005 del Club Atlético NOVA. SO024 es el ejemplo del enunciado, no una venta realizada por nosotros en Odoo. No tenemos pruebas de S00005 en PostgreSQL, PSP o Python y no hemos cambiado SKU ni pedidos para fingir esa integración».

## 7. Cierre y respaldo

Mostrar el estado por asignatura. Reconocer lo no demostrado: trazabilidad de S00005 entre sistemas, exportación REAL, usabilidad con personas, recuperación de Odoo y requisitos que solo puede juzgar la defensa. Si un servicio falla en la presentación, usar sus logs/capturas indicando fecha y origen; no presentarlos como una ejecución actual.
