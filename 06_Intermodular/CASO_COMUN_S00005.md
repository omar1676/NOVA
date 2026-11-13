# Caso común de entrega: S00005 del Club Atlético NOVA

Decisión del equipo del 13/11/2026, documentada después de publicar main `4a25d5a`. Se elige **S00005 del Club Atlético NOVA** como caso real documentado de Odoo. No se crea ni modifica ningún pedido.

## Evidencia y alcance

La fuente es el [PDF original de Berme](../odoo/documentacion/Odoo-NOVA-Sneakers.pdf), que se conserva sin cambios, junto con sus capturas y autoría. Sus páginas 10–12 documentan la venta S00005, la fabricación WH/MO/00002, la entrega WH/OUT/00005 y la factura INV/2026/00001. La venta muestra 40 pares a 89 €/par: 3.560 € sin IVA y 4.307,60 € con IVA. Las variantes y precios posteriores del producto se muestran en otros momentos del PDF; no se trasladan a esa venta.

«Real documentado» significa que el pedido figura en la evidencia del entorno Odoo de Berme. No acredita una venta comercial externa ni una ejecución comprobada en nuestro entorno actual.

## Qué significa SO024

El equipo ha revisado el enunciado intermodular v0.3: SO024 aparece bajo **«EJEMPLO DE PEDIDO CUSTOM»**, sin una obligación expresa de usar literalmente ese identificador. Se conserva como ejemplo; no se presenta como venta realizada en Odoo. La evaluación de la integración corresponde al profesor.

Se conservan las pruebas históricas rotuladas SO024 PROVISIONAL: son ensayos con datos inventados en una base desechable. No prueban S00005 ni se renombran. Los documentos en `SO024/` conservan sus rutas para no romper enlaces ni alterar evidencias; sus planes antiguos de crear un «SO024 oficial» quedan descartados para esta entrega.

## Qué puede demostrarse

| Bloque | Caso o evidencia disponible | Límite |
|---|---|---|
| Odoo | S00005 del Club Atlético NOVA, en el PDF original | Evidencia documental; sin conexión en vivo accesible aquí |
| PostgreSQL y Java | CUSTOM-40 y demás datos de PRUEBA; ensayo SO024 PROVISIONAL fechado | No hay prueba de alta, confirmación ni conciliación de S00005 |
| PSP | CSV y fichas de CUSTOM-40; ensayo SO024 PROVISIONAL | No hay CSV ni ficha acreditados de S00005 |
| Python | CSV de PRUEBA y laboratorio sintético identificado | No hay exportación ni análisis acreditados de S00005 |
| Web | Custom simulado; tienda de demostración con PostgreSQL | La solicitud Custom no crea S00005 ni pedidos en Odoo |

Elegir S00005 resuelve qué caso de Odoo se presenta, pero **no demuestra la trazabilidad del mismo pedido entre todos los sistemas**. Los requisitos que la exigen continúan parciales. Coincidir en 40 pares o en el nombre del cliente no acredita equivalencia entre S00005 y CUSTOM-40.

No se cambian SKU, identificadores, bases, datos de prueba ni código. Las diferencias de Runner X y NOVA Velocity siguen documentadas en [la revisión técnica](SO024/INTEGRACION_ODOO_SO024.md). El conector NOVA → Odoo no se ha verificado contra una instalación real accesible desde este entorno y `pedidos.js` continúa sin montarse.

## Frase para la defensa

«Presentamos S00005 del Club Atlético NOVA, documentado por Berme en Odoo. SO024 es el ejemplo del enunciado, no una venta realizada por nosotros en Odoo. PostgreSQL, PSP y Python se demuestran con sus datos de PRUEBA existentes. No tenemos pruebas de que S00005 haya pasado por esos módulos y no afirmamos que la integración completa esté verificada».
