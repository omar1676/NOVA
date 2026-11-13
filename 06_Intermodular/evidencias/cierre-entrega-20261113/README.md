# Regresión de cierre de entrega — 13/11/2026

Código probado: `4f097425355f29ae1aca8882aea46075ceb2afd4`, en un clon local nuevo de la candidata. Los cambios posteriores del cierre son documentación y evidencias. PostgreSQL 17.11 en un clúster nuevo y puerto libre, JDK 17.0.12, driver JDBC 42.7.14 descargado de la web oficial, Python 3.13.5 en un venv nuevo, Node 24.15.0 y Edge. No se tocaron bases ni configuraciones existentes.

| Prueba | Resultado nuevo de este cierre |
|---|---|
| Instalación Python | venv nuevo + pip install -r requirements.txt: correcta |
| Instalación Node | npm ci: 80 paquetes instalados |
| SQL | Montaje de esquema y scripts 02–23 en orden del manual, salvo SO024 sin datos; batería: 123 PASS, 0 FAIL, 1 ERROR previsto S4b |
| Java PruebasRubrica | 47 PASS, 0 FAIL |
| PSP PruebasPsp | 27/27 |
| Analizador de Álvaro | 8/8 |
| Comprobador rápido PSP | Correcto; corrección de Berme 0baf61f incorporada como 4f09742 sin cambiar su autoría |
| Python unittest | 265 OK |
| Node panel | 23/23, 0 saltos |
| Node tienda | 39/39, 0 saltos: compras, pagos simulados y recibos con transporte de correo de prueba |
| Node portal | 24/24, 0 saltos |
| Web recursos | 21 HTML y 155 recursos locales |
| Edge | 9 controles: catálogo 100, BEM/ancho, login admin e iframe a 1440/390 px; login y datos del trabajador |

La prueba de recibos usa un transporte Nodemailer simulado: construye el correo y prueba fallos/tiempos, pero no demuestra entrega real a un buzón externo. El pago es simulado. No se llamó a Odoo.

El puerto 8501 estaba ocupado por un servicio existente: Streamlit se inició en otro puerto y el navegador de ensayo redirigió 8501 a ese puerto para el iframe. No se modificó el código de la página ni el servicio existente. Es una adaptación del entorno de ensayo, no una nueva función.

Dos incidencias del arnés, corregidas y repetidas sin cambiar producción: Node heredó PGUSER=postgres de la instalación (el servidor lo rechazó); y la primera ejecución PSP impuso UTF-8 solo al padre mientras sus hijos usaban la codificación de Windows. Las salidas iniciales se conservan. Los resultados finales son los de la tabla. El JSON contiene ambos intentos: para cada nombre se usa el último resultado.

No se repitieron en este cierre las pruebas manuales de ventanas Swing, la usabilidad con personas, Lighthouse ni el contraste completo. Sus evidencias históricas se conservan con sus fechas. No se presenta SO024 como oficial ni los CSV de PRUEBA como REAL.
