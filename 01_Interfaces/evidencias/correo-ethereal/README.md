# Recibo de prueba con Ethereal · evidencias del 13/11/2026

`CORREO_PROVEEDOR=ethereal` (**solo desarrollo**): Nodemailer 10.5.0 crea una cuenta temporal de Ethereal, el recibo no llega a nadie y la vista previa se enlaza en «Mis pedidos». Con `NODE_ENV=production` se niega. Es una **ampliación**.

- **Prueba real contra ethereal.email, con datos ficticios:** compra en Edge de un cliente inventado (`@example.com`), vista previa del recibo en Ethereal y enlace en «Mis pedidos»: **16 de 16** (`../../../06_Intermodular/evidencias/regresion-final/05_web/07_ethereal_real.txt`). Las vistas previas de Ethereal son **públicas**: por eso solo se prueba con datos ficticios.
- **Simulados:** sin red (la API de Ethereal en un puerto cerrado) y con un servidor que no responde: **5/5 y 5/5**. La compra sigue confirmada, la respuesta no espera al correo, el error queda en la consola y el stock baja una sola vez (`08_ethereal_sin_red.txt` y `09_ethereal_mudo.txt`). Además, 7 pruebas de Ethereal sin red en `npm run test:tienda` (39/39).

| Archivo | Qué es |
|---|---|
| `capturas/mis_pedidos_enlace.png` | «Mis pedidos» con el enlace «Ver recibo de prueba» |
| `capturas/recibo_ethereal.png` | El recibo en la vista previa de ethereal.email |
| `datos_prueba_real.json` | Los datos ficticios de la compra y el enlace de la vista previa |

Ninguna credencial de Ethereal se guarda: solo existen en la memoria del servidor mientras está arrancado.
