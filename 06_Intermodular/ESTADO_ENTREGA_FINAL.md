# Estado final de entrega — NOVA Sneakers

Cierre del 13/11/2026. No se añaden funcionalidades ni se rehace Odoo. Candidata: `revision/incorporar-limpieza-main-20261113`, descendiente de main `a6151db`. La candidata se publicó mediante la PR #2 y merge `4a25d5a`. La revisión documental posterior adopta S00005; no cambia código ni datos.

| Asignatura / bloque | Estado entregado | Límite que hay que explicar |
|---|---|---|
| Interfaces | Web BEM, catálogo, ficha, probador conceptual, Custom simulado y tienda; evidencias históricas y humo nuevo en Edge | Custom no crea pedidos; falta usabilidad con personas; no se repitió Lighthouse |
| Acceso a Datos | SQL, permisos, triggers, auditoría, exportaciones y Java JDBC; instalación desde cero y 47 pruebas Java | S00005 no probado aquí; E-R exportado y ciertos requisitos de defensa/evidencia manual siguen parciales |
| PSP | Coordinador y tres hijos, errores, tiempo límite, ficha; 27 + 8 pruebas y comprobador correcto | No sustituye Odoo; S00005 no tiene CSV/ficha acreditados en PSP |
| Python | Calidad, KPIs, estadística, segmentación, predicción y dashboard; 265 pruebas desde venv nuevo | Entrada ACC entregada de PRUEBA; laboratorio sintético identificado; no hay nueva exportación REAL |
| Odoo | Se entrega sin modificar el PDF de Berme, con instalación, ventas y fabricación documentadas | Conector NOVA → Odoo sin verificar aquí; rutas de pedidos.js no montadas; no se activa ni se inventa una integración |
| Común y ampliaciones | Manuales actualizados, matrices y evidencias; panel, portal, pedidos, recibos y dashboard conservados | Trazabilidad de S00005 entre sistemas no demostrada; SMTP externo no verificado en este cierre |

## Ruta de entrega

1. Instalar con `manuales/MANUAL_INSTALACION.md`, usando una base nueva de PRUEBA.
2. Demostrar con `manuales/MANUAL_DEMOSTRACION.md`: CUSTOM-40 y pedidos de demostración, sin atribuir esos resultados a S00005.
3. Consultar `rubricas/MATRIZ_RUBRICAS.md`: distingue cumplimiento, evidencia documental, parcialidad y pendientes. La nota la determina el profesor.
4. Mostrar S00005 del Club Atlético NOVA en el PDF de Berme; explicar su alcance en `CASO_COMUN_S00005.md` y los límites técnicos en `SO024/INTEGRACION_ODOO_SO024.md`.
5. Enseñar resultados reales en `evidencias/cierre-entrega-20261113/` y conservar los ensayos anteriores con sus fechas.

## Limitaciones declaradas

- Los códigos de Runner X no se han modificado; algunos NOVA-4-* corresponden a NOVA Velocity en los datos del proyecto. No se fuerza una equivalencia con Odoo.
- S00005 del Club Atlético NOVA es el caso elegido de Odoo; SO024 es el ejemplo del enunciado, no una venta realizada. No se renombran pedidos ni se traslada la evidencia de los ensayos a S00005.
- No se cambian cantidades, precios, stock ni referencias para aparentar cierre del caso común.
- No se crean CSV de Odoo, facturas, backups, capturas ni resultados que no existan.
- No se habilitan permisos ni rutas del conector antiguo. El flujo manual documentado de Odoo no implica sincronización automática.
- El checkout de instalación necesita configuración local y dependencias descargadas; .env y conexion.properties no se entregan en Git. Las credenciales las elige quien instala.
- La CDN de iconos/gráficos y los proveedores de correo requieren red. Los tests de correo de este cierre usan un transporte de prueba.

La autoría original permanece en Git. La revisión y documentación final se prepararon con Codex a petición de Omar; no se atribuyen decisiones o pruebas personales a compañeros ausentes. Los campos del reparto personal no confirmados quedan como no verificables.
