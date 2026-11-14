# Evidencias de la tienda web

Pruebas de la tienda online (`01_Interfaces/cliente` + `servidor-admin` + scripts 20 y 21), hechas el 11 de noviembre de 2026.

**Entorno:**
- Windows 11, Node 24.15.0, Express 5.3.0 y pg 8.23.1.
- PostgreSQL 17.11, en una base **desechable** (`nova_tienda`) montada desde cero con los scripts 01–21. No se usó la base real, y todos los datos son ficticios (correos `@example.com`).
- Edge 157 manejado con Playwright 1.65, axe-core 4.12.1 y Lighthouse 12.8.2.

Playwright, axe-core y Lighthouse no son dependencias del proyecto. Las pruebas de navegador se ejecutaron desde una carpeta temporal y aquí solo se guardan sus resultados. Lo que cualquiera puede repetir es `npm test` y `npm run test:tienda` (ver `servidor-admin/README.md`).

## Resultados

La pasada final (archivos 01 a 06) se hizo seguida, sobre una base recién montada. Las regresiones (07 a 09) se hicieron con el mismo código.

| Archivo | Qué demuestra | Resultado |
|---|---|---|
| `resultados/01_scripts_sql.txt` | Los scripts originales siguen dando lo mismo. El 20 y el 21 se instalan después de la batería y se pueden repetir sin duplicar nada | 123 PASS, 0 FAIL y el ERROR que 09 provoca a propósito; 20 y 21 sin errores, también repetidos |
| `resultados/02_sql_tienda.txt` | Directamente en PostgreSQL, con los permisos de `tienda_web`: no puede escribir en ninguna tabla ni leer contraseñas; registro y login; carritos no válidos; doble clic; un cliente no puede pagar ni cancelar el pedido de otro; el stock se descuenta una vez; un fallo a mitad no deja nada a medias; la auditoría | 55 de 55 |
| `resultados/03_usuario_tienda_nova.txt` | `tienda_nova` entra con su contraseña, solo puede pasar a `tienda_web` y sin ella no lee nada. `web_nova` (el panel) no puede pasar a `tienda_web` | 9 de 9 |
| `resultados/04_npm_test_panel.txt` | Las pruebas del panel con el servidor nuevo | 16 de 16 |
| `resultados/05_npm_test_tienda.txt` | API de la tienda: catálogo frente a la base, registro, login y límite de intentos, logout, clientes y administradores separados, datos no válidos, precio y cliente manipulados, doble clic al crear y al pagar, últimos pares comprados a la vez, falta de stock a mitad del pago, historial privado y el pedido en el panel | 23 de 23 |
| `resultados/06_compra_edge.txt` | La compra completa en Edge, en escritorio y en móvil, comprobando cada paso en PostgreSQL y pasando axe-core a cada pantalla nueva | 111 de 111 |
| `resultados/07_regresion_panel.txt` | Todas las pruebas del panel (`01_Interfaces/evidencias/panel-admin`) con el servidor nuevo y una base con compras web | Autenticación 44/44, seguridad 27/27, API 69/69, intentos 25/25, caducidad 4/4, navegador 124/124 e iconos 12/12; axe sin violaciones |
| `resultados/08_regresion_interfaces.txt` | Los requisitos de Interfaces con la tienda, la web completa y Lighthouse | 136 de 136, 114 de 114; axe sin violaciones; Lighthouse 100 y 100 en escritorio y en móvil |
| `resultados/09_python.txt` | Python (`main.py` con los CSV del 16) sobre la base con la tienda | Python termina bien y con los datos al 100 % de calidad |

**Pruebas que se han tenido que tocar** (lo explica cada archivo):
- **Panel (07):** dos comprobaciones comparaban la lista de pedidos confirmados con una consulta sin `ORDER BY`. Solo funcionaban mientras había un pedido confirmado. Se les añadió el orden del panel; **el panel no se ha cambiado**.
- **Interfaces (08):** una comprobación pedía que el `aria-label` de las tarjetas terminara en el precio. Ahora el precio va seguido de la disponibilidad («…, 109,90 €, disponible»), para que la oiga un lector de pantalla, y la comprobación acepta ese final.

## Capturas

Escritorio a 1440×900 y móvil a 390×844, con los datos de la base de prueba:

| Captura | Qué enseña |
|---|---|
| `escritorio_00_portada_con_barra` y `movil_00_portada_con_barra` | La barra de la tienda bajo la cabecera, que no cambia |
| `escritorio_01_catalogo_disponibilidad` | Tarjetas del catálogo con «Disponible» o «No disponible» |
| `escritorio_02_ficha_no_disponible` | Un modelo que no está a la venta: precio orientativo y aviso |
| `escritorio_03_ficha_anadido` y `movil_03_ficha_anadido` | Color, talla, stock, cantidad y «Añadido al carrito» |
| `escritorio_04_carrito` y `movil_04_carrito` | El carrito con el precio de PostgreSQL y el total estimado |
| `escritorio_05_login_alvaro` | El diálogo de Álvaro rechazando las credenciales de `admin.demo` |
| `escritorio_06_registro` | Crear una cuenta |
| `escritorio_07_checkout_entrega` | Paso 1: datos de entrega |
| `escritorio_08_checkout_pago_simulado` y `movil_08_checkout_pago_simulado` | Paso 2: el pedido pendiente con el total calculado por PostgreSQL y el pago simulado |
| `escritorio_09_resultado_confirmado` | Pago aceptado: pedido confirmado |
| `escritorio_10_mis_pedidos` | Historial con el detalle del pedido |
| `escritorio_11_resultado_rechazado` | Pago rechazado: pedido cancelado |
| `escritorio_12_ficha_talla_agotada` | Una talla agotada, tachada y desactivada |
| `panel_14_pedidos_con_compras_web` | Las compras web en Pedidos del panel |
| `panel_15_auditoria_con_compras_web` | Alta, cambio de estado, stock y cancelación en Auditoría |

## No probado

- Con un móvil real, con un lector de pantalla y con usuarios reales: las pruebas usan Edge simulando un móvil.
- Firefox y Safari.
- Una base real con historial de meses. Python avisa de que con los datos de prueba no hay meses suficientes para las series mensuales, igual que antes de la tienda.

## Regresión del 13/11/2026 (árbol final)

Con el código final (100 modelos a la venta, recibo por correo, reparto y login único), sobre una base desechable montada desde cero con los scripts 01–23 (la regresión del 13/11):

| Prueba | Resultado | Archivo |
|---|---|---|
| SQL de la tienda (`tienda_web`, 100 modelos y 880 SKU) | 55 de 55 | la regresión del 13/11 |
| `npm run test:tienda` (ahora con recibos por Resend simulado y Ethereal) | 39 de 39 | la regresión del 13/11 |
| Compra completa en Edge, escritorio y móvil, contrastada con PostgreSQL y con el panel | 139 de 139; 4 recibos en el Resend simulado y 4 pedidos pagados | la regresión del 13/11 |
| Mejoras de la web (100 fichas, teclado, 11 anchos, probador, axe) | 81 de 81 | la regresión del 13/11 |

Las capturas de esa compra están en `capturas-2026-11-13/` (reducidas para el repositorio): catálogo con disponibilidad, ficha, carrito, el diálogo de login de Álvaro, registro, entrega, pago simulado aceptado y rechazado, «Mis pedidos», talla agotada, compra de modelos nuevos, y el panel con las compras web (`panel_13` a `panel_15`). Las capturas de `capturas/` son del 11/11, anteriores a la integración.
