# SO024 · Evidencia PROVISIONAL de PSP

> **PROVISIONAL. No es el SO024 oficial.** El reparto por talla, el precio, el
> color, el stock y la personalización son datos inventados para probar la cadena.
> Faltan los 7 datos que tienen que acordar los tres. Cuando estén, hay que repetir esta prueba y
> sustituir estos archivos.

Prueba hecha el 13 de noviembre de 2026 sobre la,
en una base desechable (clúster de pruebas, no la base del equipo).

## Datos provisionales

| Dato | Valor provisional |
|---|---|
| Cliente | Club Halcones (lo da de alta `18_datos_so024.sql`) |
| Modelo | Runner X, tallas 38 a 46 |
| Precio | 99,90 € el par (`-v precio=99.90`) |
| Color | `PROVISIONAL` (`-v color=PROVISIONAL`) |
| Stock inicial | 10 pares por talla (`-v stock=10`) |
| Reparto | 38: 2 · 39: 3 · 40: 5 · 41: 6 · 42: 7 · 43: 6 · 44: 5 · 45: 4 · 46: 2 (40 pares) |
| Personalización | «PROVISIONAL: escudo del Club Halcones en el lateral» |

## Cómo se hizo

1. Base nueva con los scripts 01 a 23 de `02_Acceso_Datos/sql` (la batería 09–16 dio
   123 PASS, 0 FAIL y el ERROR previsto).
2. `18_datos_so024.sql -v precio=99.90 -v color=PROVISIONAL -v stock=10`.
3. SO024 se creó y se confirmó con los **mismos métodos que usa la pestaña «Nuevo
   pedido»** de la aplicación Java (`PedidoDAO.crearPedido` y
   `PedidoDAO.confirmarPedido`, con la sesión de `admin.demo`), desde un lanzador de
   prueba. No se usó la ventana.
4. `15_exportar_fabricacion.sql -v referencia=SO024` dejó el CSV de fabricación.
5. PSP lo procesó: `java -cp clases ProcesadorPedidosCustom datos\SO024_PROVISIONAL_fabricacion.csv`.

## Resultado

- SO024 confirmado: 9 líneas, 40 pares y 3.996,00 €.
- El stock de Runner X baja una vez por talla: queda en 8, 7, 5, 4, 3, 4, 5, 6 y 8.
- La auditoría del pedido la firma `admin.demo` (alta y cambio de estado).
- El 15 exporta 9 filas y 40 pares, con sus dos comprobaciones en PASS.
- PSP: los tres procesos hijo terminan con código 0 (9 combinaciones, 9 tallas y
  40 pares) y el padre, también con **código 0**. La ficha del taller cuadra con el CSV.

## Archivos

| Archivo | Qué es |
|---|---|
| `SO024_PROVISIONAL_fabricacion.csv` | El CSV que dejó el 15 (el que lee PSP) |
| `01_cadena_SO024_PROVISIONAL.txt` | Resumen de la cadena: 18, Java, comprobaciones en PostgreSQL, 15 y PSP |
| `02_exportacion_15_SO024_PROVISIONAL.txt` | Salida completa del 15 |
| `03_ejecucion_psp_SO024_PROVISIONAL.txt` | Salida completa de PSP, con la ficha |
| `ficha_taller_SO024_PROVISIONAL.txt` | La ficha que escribió PSP en `salidas/` |
| `registro_psp_SO024_PROVISIONAL.txt` | La entrada que añadió PSP a `registro_psp.txt` |

Ningún archivo lleva contraseñas ni rutas del ordenador.
