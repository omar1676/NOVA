# 05 · Sistemas de Gestión Empresarial (Odoo)

La parte de Odoo la documenta Iván Bermejo en [Odoo-NOVA-Sneakers.pdf](../odoo/documentacion/Odoo-NOVA-Sneakers.pdf): 19 páginas con 28 capturas. El caso documentado es la venta **S00005** del Club Atlético NOVA. SO024 es el ejemplo del enunciado, no un identificador obligatorio.

## Qué documenta el PDF

| Páginas | Contenido |
|---|---|
| 3–6 | Ubuntu 24.04 en OrbStack, Odoo 19 Community como servicio, la base `nova_sneaker` y las aplicaciones instaladas (Ventas, Inventario, Fabricación, Facturación y Contactos) |
| 7–9 | El producto Runner X, su lista de materiales y una orden de fabricación de prueba |
| 10–12 | La venta S00005: 40 pares, la orden de fabricación WH/MO/00002, la entrega WH/OUT/00005 y la factura INV/2026/00001, pagada |
| 13–15 | La conexión de un servidor Node con la API JSON-2 de Odoo, probada en el entorno de Berme |
| 16–17 | Las variantes por talla de Runner X (`NOVA-4-38` a `NOVA-4-46`), los movimientos de stock y los usuarios Vendedor NOVA y Almacén NOVA |
| 18–19 | El resumen de las tareas OD-01 a OD-06 y los comandos útiles: servicio, actualización, clave de API y copia de seguridad |

La explicación de cada parte, con sus capturas, está en la memoria del proyecto (`Memoria_NOVA_Sneakers.pdf`).

## Límites

- S00005 está documentado en Odoo. No hay una exportación de S00005 procesada en PostgreSQL, PSP ni Python.
- En Odoo, `NOVA-4-38` a `NOVA-4-46` son las variantes de Runner X. En PostgreSQL, `NOVA-4-40` a `NOVA-4-44` corresponden a NOVA Velocity. No hay una tabla de equivalencias entre los dos sistemas.
- El conector del servidor (`servidor-admin/odoo.js` y `pedidos.js`) necesita `ODOO_URL`, `ODOO_DB` y `ODOO_API_KEY`, y sus rutas no están montadas en el servidor. La conexión de las páginas 13–15 corresponde al entorno de Berme.
- CRM no está instalado (p. 6). Los perfiles son Vendedor NOVA (Ventas) y Almacén NOVA (Inventario y Fabricación), en la p. 17.

## Cómo se arranca

En la máquina Ubuntu de OrbStack (PDF, pp. 3–6 y 19):

```
sudo systemctl status odoo --no-pager
sudo systemctl restart odoo
```

Odoo se abre en `http://ubuntu.orb.local:8069`, con la base `nova_sneaker`.

## Copia de seguridad

Desde `http://ubuntu.orb.local:8069/web/database/manager`, «Backup» de `nova_sneaker` en formato zip, con el almacén de archivos (PDF, p. 19). La copia se guarda fuera del repositorio.
