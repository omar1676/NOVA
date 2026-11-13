# Reparto y recibo por correo · evidencias del 13/11/2026

El botón «Marcar en reparto» del panel (`22_reparto_panel.sql`, función `marcar_pedido_en_reparto` y rol `panel_reparto`), el estado «En reparto» en «Mis pedidos» de la tienda y el recibo que se manda al pagar. Es una **ampliación**: ninguna rúbrica lo pide.

**Prueba:** Edge sin ventana contra el servidor de pruebas, con un **Resend simulado** (un servidor local que guarda los correos; la clave es inventada), sobre una base desechable 01–23. **29 PASS, 0 FAIL** (`../../../06_Intermodular/evidencias/regresion-final/05_web/05_recorrido_reparto.txt`). Además, el SQL del 22: 37/37 (`../../../06_Intermodular/evidencias/regresion-final/01_sql/07_sql_reparto_con23.txt`) y las pruebas de `npm test` y `test:tienda` (`../../../06_Intermodular/evidencias/regresion-final/03_node/`).

| Archivo | Qué enseña |
|---|---|
| `capturas/panel_boton_marcar_en_reparto.png` (y `_movil`) | El botón en la tabla de pedidos del panel |
| `capturas/panel_tras_marcar_en_reparto.png` | El pedido ya en `enviado` |
| `capturas/panel_error_al_marcar.png` | El mensaje cuando el pedido ya no se puede marcar |
| `capturas/mis_pedidos_en_reparto.png` (y `_movil`) | «En reparto» en «Mis pedidos» del cliente |
| `capturas/recibo_ejemplo.png`, `recibo_ejemplo.html`, `recibo_ejemplo.txt` | El recibo que recibió el Resend simulado (cliente y dirección **ficticios**) |

Nunca se ha mandado un correo por el Resend real: no hay clave. Las capturas están reducidas para el repositorio.
