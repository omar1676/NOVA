# Estado final de entrega — NOVA Sneakers

Cierre del 13/11/2026. No se añaden funcionalidades ni se rehace Odoo. Candidata: `revision/incorporar-limpieza-main-20261113`, descendiente de main `a6151db`. La publicación e integración en main siguen sin ejecutarse.

| Asignatura / bloque | Estado entregado | Límite que hay que explicar |
|---|---|---|
| Interfaces | Web BEM, catálogo, ficha, probador conceptual, Custom simulado y tienda; evidencias históricas y humo nuevo en Edge | Custom no crea pedidos; falta usabilidad con personas; no se repitió Lighthouse |
| Acceso a Datos | SQL, permisos, triggers, auditoría, exportaciones y Java JDBC; instalación desde cero y 47 pruebas Java | SO024 oficial, E-R exportado y ciertos requisitos de defensa/evidencia manual siguen parciales |
| PSP | Coordinador y tres hijos, errores, tiempo límite, ficha; 27 + 8 pruebas y comprobador correcto | No sustituye Odoo; el caso oficial no está conciliado |
| Python | Calidad, KPIs, estadística, segmentación, predicción y dashboard; 265 pruebas desde venv nuevo | Entrada ACC entregada de PRUEBA; laboratorio sintético identificado; no hay nueva exportación REAL |
| Odoo | Se entrega sin modificar el PDF de Berme, con instalación, ventas y fabricación documentadas | Conector NOVA → Odoo sin verificar aquí; rutas de pedidos.js no montadas; no se activa ni se inventa una integración |
| Común y ampliaciones | Manuales actualizados, matrices y evidencias; panel, portal, pedidos, recibos y dashboard conservados | Los siete datos y la conciliación oficial de SO024 permanecen pendientes; SMTP externo no verificado en este cierre |

## Ruta de entrega

1. Instalar con `manuales/MANUAL_INSTALACION.md`, usando una base nueva de PRUEBA.
2. Demostrar con `manuales/MANUAL_DEMOSTRACION.md`: CUSTOM-40 y pedidos de demostración, sin hacerse pasar por el SO024 definitivo.
3. Consultar `rubricas/MATRIZ_RUBRICAS.md`: distingue cumplimiento, evidencia documental, parcialidad y pendientes. La nota la determina el profesor.
4. Mostrar el PDF de Odoo como evidencia histórica; explicar las diferencias de SKU y cliente en `SO024/INTEGRACION_ODOO_SO024.md`.
5. Enseñar resultados reales en `evidencias/cierre-entrega-20261113/` y conservar los ensayos anteriores con sus fechas.

## Limitaciones declaradas

- Los códigos de Runner X no se han modificado; algunos NOVA-4-* corresponden a NOVA Velocity en los datos del proyecto. No se fuerza una equivalencia con Odoo.
- S00005 del PDF, del Club Atletico NOVA y a 89 €/par, no se renombra como SO024 del Club Halcones.
- No se cambian cantidades, precios, stock ni referencias para aparentar cierre del caso común.
- No se crean CSV de Odoo, facturas, backups, capturas ni resultados que no existan.
- No se habilitan permisos ni rutas del conector antiguo. El flujo manual documentado de Odoo no implica sincronización automática.
- El checkout de instalación necesita configuración local y dependencias descargadas; .env y conexion.properties no se entregan en Git. Las credenciales las elige quien instala.
- La CDN de iconos/gráficos y los proveedores de correo requieren red. Los tests de correo de este cierre usan un transporte de prueba.

La autoría original permanece en Git. La revisión y documentación final se prepararon con Codex a petición de Omar; no se atribuyen decisiones o pruebas personales a compañeros ausentes. Los campos del reparto personal no confirmados quedan como no verificables.
