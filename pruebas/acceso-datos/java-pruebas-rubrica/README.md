# Batería de Java (`PruebasRubrica`) y los archivos que escribe

Resultado de `nova.PruebasRubrica` (lo mismo que lanza `acceso-datos/java/pruebas.bat`)
el 13 de noviembre de 2026, sobre la rama `integracion/candidata-2`.

- **Base de datos:** una base desechable montada desde cero con los scripts 01 a 23 de
  `acceso-datos/sql` (la batería 09–16 dio 123 PASS, 0 FAIL y el ERROR previsto). No
  es la base del equipo.
- **Resultado:** **47 PASS y 0 FAIL** (`resultado-pruebas-rubrica.txt`): inicio de
  sesión, pruebas A a J y permisos. Cada cifra se compara con una consulta SQL.
- **Contraseñas:** se escribieron por teclado. Ningún archivo de esta carpeta lleva
  contraseñas ni hashes (la prueba I2 lo comprueba en el JSON).

Los tres archivos que escribe la aplicación en su carpeta `salidas/` durante la
batería:

| Archivo | Qué demuestra | Prueba |
|---|---|---|
| `actividad_sneaker.txt` | El TXT de actividad: una línea por operación (inicio de sesión, consulta, alta, confirmación, cancelación, intentos rechazados…) con fecha, usuario, rol, operación, resultado y detalle. Solo se añaden líneas | G1 (tres consultas, tres líneas nuevas) |
| `usuarios_sneaker.json` | El JSON de usuarios después de crear, cambiar de rol y desactivar uno: `id_usuario`, `username`, `rol` y `activo`, sin contraseñas | I1 a I4 |
| `consulta_pedidos.csv` | El CSV de la consulta filtrada: la misma cabecera y las mismas celdas que la tabla | J6 |

Las fechas de los pedidos son la hora en que se montó la base. Las capturas de las
ventanas, con el CSV exportado desde la ventana y su TXT, están en `../java-swing/`.
