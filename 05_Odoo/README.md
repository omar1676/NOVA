# 05 · Sistemas de Gestión Empresarial (Odoo)

**Cierre de entrega (sin nuevas implementaciones):** se conserva el PDF y la evidencia real. El conector NOVA → Odoo no se ha verificado contra una instalación real accesible desde este entorno; `pedidos.js` no se monta. SO024 no es definitivo y sus códigos/datos no se alteran para aparentarlo. Los pendientes siguientes son limitaciones declaradas, no una espera de nuevos archivos.

**Estado documental a 13/11/2026: documentación de Berme recibida; conciliación del SO024 oficial pendiente.** El equipo confirma que los siete datos del caso común siguen por acordar. No debe presentarse la venta histórica del PDF como SO024.

## Evidencia disponible

[Odoo-NOVA-Sneakers.pdf](../odoo/documentacion/Odoo-NOVA-Sneakers.pdf) (19 páginas, ya en main) documenta Ubuntu 24.04 en OrbStack, Odoo 19 Community, la base `nova_sneaker`, productos, usuarios y un recorrido de venta, fabricación, entrega y factura. Las páginas 10–12 describen S00005 del Club Atletico NOVA; las 16–17 muestran variantes de Runner X.

El documento conserva su ubicación y autoría; no se duplica ni se modifica. La base Odoo `nova_sneaker` y la base académica `nova_sneakers` son distintas. Esta revisión documental no se conectó a ninguna de ellas.

## Integración preparada

La fuente actual de conciliación es [INTEGRACION_ODOO_SO024.md](../06_Intermodular/SO024/INTEGRACION_ODOO_SO024.md): evidencias por página, códigos observados frente a códigos pendientes de exportar, consultas de solo lectura y criterios de aceptación.

Hay un conflicto que resolver: el PDF usa `NOVA-4-38…46` para Runner X, mientras parte de esos códigos corresponde a NOVA Velocity en los datos del proyecto. No cambiar IDs ni referencias para forzar la coincidencia. Los SKU reales de la base del equipo y la decisión sobre Odoo siguen pendientes.

## Qué está pendiente

- Acordar los siete datos y crear el SO024 del Club Halcones, con equivalencia al número S… de Odoo.
- Aportar exportación de variantes y del pedido oficial; comprobar talla, color, cantidad, modelo, precio e IVA.
- Completar las evidencias del mismo pedido en PostgreSQL/Java, PSP y Python.
- Revisar los perfiles completos de la rúbrica, CRM si entra en el alcance, incidencias y backup/restauración.
- Actualizar la memoria y el guion de demo con la conciliación aprobada. La documentación OD-01…06 no cierra por sí sola todos los requisitos de SGE.

## API y arranque

El PDF incluye instalación y comandos del entorno de Berme (páginas 3–6 y 19); no se ha reproducido esa instalación aquí. El acceso mostrado es local a su entorno de OrbStack.

El conector `servidor-admin/odoo.js` exige `ODOO_URL`, `ODOO_DB` y `ODOO_API_KEY` en `.env`. Las rutas de `pedidos.js` siguen sin montarse por su incompatibilidad con permisos y auditoría de la candidata. Configurar las variables no autoriza ni activa esas rutas. No se ha probado la API de esta candidata contra Odoo.

## Archivos

| Archivo | Uso |
|---|---|
| PDF enlazado arriba | Aportación documental de Berme y capturas históricas |
| `CHECKLIST_ODOO_BERME.md` | Criterios para cerrar SO024 y la entrega, contrastados con el PDF |
| `recorrido-manual-odoo.md` | Borrador histórico; consultar primero el plan actual de conciliación |
| Plan de integración enlazado arriba | Único lugar para preparar códigos y el orden de aceptación |

El backup y la máquina virtual se conservan fuera de Git. Falta registrar ubicación, fecha, tamaño, hash y resultado de una restauración; no se ha creado ni modificado ninguna copia de seguridad en esta revisión.
