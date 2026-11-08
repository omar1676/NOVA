# Comprobación de la rama integrada

Ejecutar desde la raíz y registrar el resultado real de cada paso. Esta lista
no afirma que las pruebas se hayan ejecutado sobre una base de datos.

## Interfaces

1. Ejecutar `python3 scripts/comprobar_web.py` para detectar rutas rotas.
2. Arrancar `python3 -m http.server 8000 --bind 127.0.0.1`.
3. Abrir `/interfaces/cliente/` y probar los seis filtros, búsquedas con y
   sin resultados, apertura/cierre de ficha y navegación con teclado.
4. Abrir el probador con Street 01, Casual 01, Casual 02 y un modelo sin
   foto puesta. Comprobar los avisos y controles deshabilitados.
5. Abrir inicio de sesión: validar campos vacíos y comprobar que informa
   de la falta de servidor; no debe simular un acceso correcto.
6. Abrir `/interfaces/admin/admin.html` y recorrer todos los enlaces del menú.
   El dashboard estático puede mostrar indicadores vacíos por falta de API.
7. Revisar catálogo, tablas y menú a 375 px y 1280 px de ancho.

## Procesos Java

Ejecutar `python3 scripts/comprobar_psp.py` con JDK 17 o posterior.
El comando compila ambas variantes por separado, comprueba el CSV multilínea,
su resumen de cuarenta pares y tres rechazos, y ejecuta las pruebas del
paquete `Psp`. Un fallo o bloqueo produce salida distinta de cero.

La muestra usa SKU sintéticos. El resultado valida el intercambio entre
procesos, no la correspondencia con un catálogo real ni el stock.

## Base de datos y fabricación

Seguir `acceso-datos/documentacion/README.md` sobre una base de demostración.
Orden documentado: esquema, 04, 02, 03, 05, 07, 08; después 06, 09, 10,
11 y 12; luego 13 para activar cuentas, 14 para persistir CUSTOM-40 y 15
para exportar. El script 09 contiene errores de permisos provocados a
propósito: revisar sus resultados PASS/FAIL según su documentación.

Ejecutar el proceso padre sobre el CSV exportado y comparar las tallas y
cantidades con SQL. Comprobar que crear el pedido no descuenta existencias,
confirmarlo las descuenta y cancelarlo las devuelve una sola vez.

## Pendiente

Odoo, backend HTTP, autenticación web, carrito, checkout y coordinador final
de fabricación requieren implementación o acuerdos adicionales. La unión
de archivos en una rama no completa estos flujos.
