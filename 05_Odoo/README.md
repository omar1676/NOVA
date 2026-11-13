# 05 · Sistemas de Gestión Empresarial (Odoo)

**Cierre de entrega (sin nuevas implementaciones):** se conserva el PDF y la evidencia real. El conector NOVA → Odoo no se ha verificado contra una instalación real accesible desde este entorno; `pedidos.js` no se monta. El caso elegido es S00005 del Club Atlético NOVA. SO024 es el ejemplo del enunciado; no se crea ni se renombra ninguna venta. Los pendientes siguientes son limitaciones declaradas, no una espera de nuevos archivos.

**Decisión de entrega del 13/11/2026:** se utiliza S00005, ya documentado por Berme. No hay pruebas de su procesamiento en PostgreSQL, PSP o Python. Ver [el caso y sus límites](../06_Intermodular/CASO_COMUN_S00005.md).

## Evidencia disponible

[Odoo-NOVA-Sneakers.pdf](../odoo/documentacion/Odoo-NOVA-Sneakers.pdf) (19 páginas, ya en main) documenta Ubuntu 24.04 en OrbStack, Odoo 19 Community, la base `nova_sneaker`, productos, usuarios y un recorrido de venta, fabricación, entrega y factura. Las páginas 10–12 describen S00005 del Club Atletico NOVA; las 16–17 muestran variantes de Runner X.

El documento conserva su ubicación y autoría; no se duplica ni se modifica. La base Odoo `nova_sneaker` y la base académica `nova_sneakers` son distintas. Esta revisión documental no se conectó a ninguna de ellas.

## Límites de integración

La revisión técnica conservada es [INTEGRACION_ODOO_SO024.md](../06_Intermodular/SO024/INTEGRACION_ODOO_SO024.md): evidencias por página, códigos observados frente a códigos pendientes de exportar, consultas de solo lectura y criterios de aceptación.

Hay un conflicto que resolver: el PDF usa `NOVA-4-38…46` para Runner X, mientras parte de esos códigos corresponde a NOVA Velocity en los datos del proyecto. No cambiar IDs ni referencias para forzar la coincidencia. No hay equivalencia de SKU validada entre sistemas y no se modifican códigos para esta entrega.

## Qué está pendiente

- No se aporta una exportación de S00005 ni una correspondencia acreditada con PostgreSQL/Java, PSP y Python. La trazabilidad entre esos sistemas no está demostrada. SO024 no se exige como una venta nueva.
- Revisar los perfiles completos de la rúbrica, CRM si entra en el alcance, incidencias y backup/restauración.
- La documentación OD-01…06 acredita el flujo de Odoo documentado, pero no cierra por sí sola todos los requisitos de SGE ni la integración entre sistemas.

## API y arranque

El PDF incluye instalación y comandos del entorno de Berme (páginas 3–6 y 19); no se ha reproducido esa instalación aquí. El acceso mostrado es local a su entorno de OrbStack.

El conector `servidor-admin/odoo.js` exige `ODOO_URL`, `ODOO_DB` y `ODOO_API_KEY` en `.env`. Las rutas de `pedidos.js` siguen sin montarse por su incompatibilidad con permisos y auditoría de la candidata. Configurar las variables no autoriza ni activa esas rutas. No se ha probado la API de esta candidata contra Odoo.

## Archivos

| Archivo | Uso |
|---|---|
| PDF enlazado arriba | Aportación documental de Berme y capturas históricas |
| `CHECKLIST_ODOO_BERME.md` | Plan histórico de SO024, no aplicable como obligación de entrega |
| `recorrido-manual-odoo.md` | Borrador histórico; no ejecutarlo para recrear S00005 |
| Plan de integración enlazado arriba | Revisión histórica de códigos; el caso vigente se define en CASO_COMUN_S00005.md |

El backup y la máquina virtual se conservan fuera de Git. Falta registrar ubicación, fecha, tamaño, hash y resultado de una restauración; no se ha creado ni modificado ninguna copia de seguridad en esta revisión.
