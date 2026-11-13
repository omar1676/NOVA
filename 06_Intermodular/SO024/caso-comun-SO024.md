# Caso común SO024

Del enunciado del proyecto intermodular: **SO024 · Club Halcones · Runner X · 40 pares · tallas 38–46 · diseño personalizado.**

El mismo pedido se enseña en todas las asignaturas, con la misma referencia, `SO024`. No hay sincronización automática: la integración consiste en que los datos coincidan, y se comprueba con la tabla de abajo.

> **Revisión 13/11/2026:** los siete datos siguen pendientes de acuerdo, confirmado por el equipo. El PDF de Odoo documenta otro pedido histórico; no rellena estos acuerdos. Ver [la preparación de integración y los códigos de Runner X](INTEGRACION_ODOO_SO024.md).

## 1. Datos por acordar (Omar, Berme y Álvaro)

| Dato | Valor acordado | Dónde se usa |
|---|---|---|
| Pares de la talla 38 / 39 / 40 / 41 / 42 / 43 / 44 / 45 / 46 (en total, 40) | ___ | Java (al crear SO024) y Odoo |
| Color de Runner X | ___ | `18_datos_so024.sql` (`-v color=`) y Odoo |
| Precio base de Runner X | ___ | `18_datos_so024.sql` (`-v precio=`) y Odoo |
| Stock inicial por talla (como mínimo, los pares de la talla más pedida) | ___ | `18_datos_so024.sql` (`-v stock=`) |
| Texto de la personalización | ___ | Java y Odoo |
| SKU: el de PostgreSQL es `NOVA-<variante>-<talla>`. ¿Se usa como referencia interna en Odoo o se apunta la equivalencia? | ___ | Odoo |
| Número del pedido en Odoo: `SO024` u otro con la equivalencia apuntada | ___ | Odoo |

## 2. Pasos de la demostración

1. **Web (Interfaces).** El Club Halcones rellena la solicitud Custom. El envío es una simulación.
2. **Odoo (SGE).** Cliente, presupuesto y pedido SO024, orden de fabricación, entrega y factura (o su simulación).
3. **PostgreSQL.** Se cargan los datos de SO024:
   `psql -U postgres -d nova_sneakers -v precio=… -v color=… -v stock=… -f 18_datos_so024.sql`
4. **Java (Acceso a Datos).**
   - Pestaña «Nuevo pedido»: referencia `SO024`, cliente Club Halcones, «Pedido Custom» marcado con su personalización y una línea por talla.
   - Se confirma, y el trigger descuenta el stock una sola vez.
   - Se consulta filtrando por el cliente.
5. **Exportación para PSP.**
   `psql -U postgres -d nova_sneakers -v referencia=SO024 -f 15_exportar_fabricacion.sql`
6. **PSP.** `ProcesadorPedidosCustom` con ese CSV lanza los tres procesos hijos y escribe `ficha_taller_SO024.txt`.
7. **Python.**
   - Se exportan los cinco CSV con `16_exportar_csv_dashboard.sql` y se copian a `04_Python/entrada_acc/`.
   - Se regeneran P-A, P-B y P-C.
   - El dashboard muestra SO024 en 60 segundos como máximo.
8. **Cierre.** Se rellena la tabla del apartado 3.

## 3. Comprobación final: las mismas cantidades en todas partes

| Talla | Odoo | PostgreSQL | Java | Ficha de PSP | `lineas_pedido.csv` |
|---|---|---|---|---|---|
| 38 | | | | | |
| 39 | | | | | |
| 40 | | | | | |
| 41 | | | | | |
| 42 | | | | | |
| 43 | | | | | |
| 44 | | | | | |
| 45 | | | | | |
| 46 | | | | | |
| **Total** | **40** | **40** | **40** | **40** | **40** |
