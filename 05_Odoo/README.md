# 05 · Sistemas de Gestión Empresarial (Odoo)

**Cierre de entrega (sin nuevas implementaciones):** se conserva el PDF y la evidencia real. El conector NOVA → Odoo no se ha verificado contra una instalación real accesible desde este entorno; `pedidos.js` no se monta. El caso elegido es S00005 del Club Atlético NOVA. SO024 es el ejemplo del enunciado; no se crea ni se renombra ninguna venta. Los pendientes siguientes son limitaciones declaradas, no una espera de nuevos archivos.

**Decisión de entrega del 13/11/2026:** se utiliza S00005, ya documentado por Berme. No hay pruebas de su procesamiento en PostgreSQL, PSP o Python. Ver [el caso y sus límites](..md).

## Evidencia disponible

[Odoo-NOVA-Sneakers.pdf](../odoo/documentacion/Odoo-NOVA-Sneakers.pdf) (19 páginas, ya en main) documenta Ubuntu 24.04 en OrbStack, Odoo 19 Community, la base `nova_sneaker`, productos, usuarios y un recorrido de venta, fabricación, entrega y factura. Las páginas 10–12 describen S00005 del Club Atletico NOVA; las 16–17 muestran variantes de Runner X, movimientos de stock y usuarios. Las páginas 13-15 describen el conector de una versión anterior del servidor (rutas `servidor/…`) y los pedidos S00001-S00004 creados desde el proyecto en el entorno de Berme; en el código entregado ese conector está desactivado (ver «API y arranque»). El resumen por páginas, las incidencias y la adaptación a la empresa están en la memoria del proyecto (`Memoria_NOVA_Sneakers.pdf`) §4.

El documento conserva su ubicación y autoría; no se duplica ni se modifica. La base Odoo `nova_sneaker` y la base académica `nova_sneakers` son distintas. Esta revisión documental no se conectó a ninguna de ellas.

## Límites de integración

md](..md): evidencias por página, códigos observados frente a códigos pendientes de exportar, consultas de solo lectura y criterios de aceptación.

Hay un conflicto que resolver: el PDF usa `NOVA-4-38…46` para Runner X, mientras parte de esos códigos corresponde a NOVA Velocity en los datos del proyecto. No cambiar IDs ni referencias para forzar la coincidencia. No hay equivalencia de SKU validada entre sistemas y no se modifican códigos para esta entrega.

## Qué está pendiente

- No se aporta una exportación de S00005 ni una correspondencia acreditada con PostgreSQL/Java, PSP y Python. La trazabilidad entre esos sistemas no está demostrada. SO024 no se exige como una venta nueva.
- Perfiles documentados (PDF, p. 17): Vendedor NOVA (Ventas: usuario) para el comercial y Almacén NOVA (Inventario y Fabricación: usuario) para almacén y producción; la administración la lleva el administrador de la base (p. 5). No hay un usuario aparte para producción ni para administración. CRM no se instaló (p. 6), así que queda fuera del alcance (IM-SGE-11 es condicional). **[EQUIPO: confirmar que se acepta así]**
- Las cinco incidencias que recoge el PDF (pp. 4, 8, 14, 15 y 16) están resumidas en la memoria del proyecto (`Memoria_NOVA_Sneakers.pdf`) §4.7.
- Falta la copia de seguridad (ver «Archivos», al final).
- La documentación OD-01…06 acredita el flujo de Odoo documentado, pero no cierra por sí sola todos los requisitos de SGE ni la integración entre sistemas.

## API y arranque

El PDF incluye instalación y comandos del entorno de Berme (páginas 3–6 y 19); no se ha reproducido esa instalación aquí. El acceso mostrado es local a su entorno de OrbStack.

El conector `servidor-admin/odoo.js` exige `ODOO_URL`, `ODOO_DB` y `ODOO_API_KEY` en `.env`. Las rutas de `pedidos.js` siguen sin montarse por su incompatibilidad con permisos y auditoría . Configurar las variables no autoriza ni activa esas rutas. No se ha verificado la API de la versión entregada contra un Odoo desde este entorno; el PDF documenta pruebas de Berme en su entorno con una versión anterior (pp. 13-15).

## Archivos

| Archivo | Uso |
|---|---|
| PDF enlazado arriba | Aportación documental de Berme y capturas históricas |

**Copia de seguridad (IM-COM-16).** El procedimiento está en el PDF (p. 19): desde `/web/database/manager`, «Backup» de `nova_sneaker` en formato zip con el almacén de archivos, guardado fuera del repositorio. No consta ninguna copia hecha ni restaurada: ubicación **[BERME]**, fecha **[BERME]**, tamaño **[BERME]**, SHA-256 **[BERME]** y restauración probada **[BERME: sí o no, fecha y base de destino]**. Si no hay copia, **límite declarado:** no se aporta copia, y la configuración se reconstruye siguiendo el PDF, pp. 3-19. La copia no se sube a Git. En esta revisión no se ha creado ni modificado ninguna copia.
