// correo.js — el recibo por correo de las compras de la tienda.
//
// Cuando el pago simulado se acepta y el pedido ya esta confirmado en
// PostgreSQL, tienda.js llama a enviarRecibo. Hay dos proveedores:
//   - Resend (el de siempre): un POST a su API con la clave en la cabecera
//     Authorization y el correo en JSON, con el fetch que ya trae Node.
//   - Ethereal, SOLO PARA DESARROLLO: un buzon falso de Nodemailer. El correo
//     no llega a nadie; se ve en una pagina de ethereal.email (vista previa).
//
// Configuracion, en .env (no se sube a Git):
//   CORREO_PROVEEDOR  opcional: resend (si no se indica) o ethereal.
//                     ethereal no se admite con NODE_ENV=production.
//   RESEND_API_KEY    la clave de Resend. Sin ella no se envia nada por Resend.
//   RESEND_FROM       el remitente, por ejemplo: NOVA Sneakers <onboarding@resend.dev>
//   RESEND_URL        opcional. Por defecto https://api.resend.com/emails; las
//                     pruebas la cambian por un Resend simulado en este ordenador.
// Ethereal no necesita nada: la cuenta temporal se crea sola en el primer envio.
//
// El correo nunca hace fallar la compra: si falta la clave, si el proveedor
// falla o si tarda demasiado (5 s Resend, 10 s Ethereal), el pedido sigue
// confirmado y solo se escribe una linea en la consola. Las claves no se
// escriben nunca en la consola ni en ningun archivo.

const nodemailer = require('nodemailer');

const URL_RESEND = 'https://api.resend.com/emails';
const TIEMPO_MAXIMO_MS = 5000;
const TIEMPO_MAXIMO_ETHEREAL_MS = 10000; // crear la cuenta y mandar el correo
const REMITENTE_ETHEREAL = 'NOVA Sneakers <recibos@example.com>'; // inventado: Ethereal no entrega nada
const AVISO = 'Pago simulado: NOVA Sneakers es un proyecto académico y no se ha cobrado nada.';

function euros(valor) {
  return Number(valor).toLocaleString('es-ES', { style: 'currency', currency: 'EUR' });
}

// El nombre y la direccion los escribe el cliente: si llevan < o &, en el
// HTML tienen que verse como texto y no como etiquetas
function escaparHtml(texto) {
  return String(texto)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// El asunto, el HTML y el texto plano del recibo.
//   cliente: { nombre, email, direccion } leidos de la base
//   pedido:  { referencia, fecha, total, lineas: [{ modelo, color, talla, cantidad, precio, subtotal }] }
function crearRecibo(cliente, pedido) {
  const asunto = `Recibo de tu pedido ${pedido.referencia} · NOVA Sneakers`;

  const texto = [
    `Hola, ${cliente.nombre}:`,
    '',
    `Gracias por tu compra. Este es el recibo del pedido ${pedido.referencia} (${pedido.fecha}).`,
    '',
    ...pedido.lineas.map((l) =>
      `- ${l.modelo} · ${l.color} · talla ${l.talla} · ${l.cantidad} × ${euros(l.precio)} = ${euros(l.subtotal)}`),
    '',
    `Total: ${euros(pedido.total)}`,
    ...(cliente.direccion ? [`Dirección de entrega: ${cliente.direccion}`] : []),
    '',
    AVISO
  ].join('\n');

  const celda = 'padding:8px;border-bottom:1px solid #e4e4e7;';
  const filas = pedido.lineas.map((l) => `
        <tr>
          <td style="${celda}">${escaparHtml(l.modelo)}</td>
          <td style="${celda}">${escaparHtml(l.color)}</td>
          <td style="${celda}">${escaparHtml(l.talla)}</td>
          <td style="${celda}text-align:right">${escaparHtml(l.cantidad)}</td>
          <td style="${celda}text-align:right">${escaparHtml(euros(l.precio))}</td>
          <td style="${celda}text-align:right">${escaparHtml(euros(l.subtotal))}</td>
        </tr>`).join('');
  const direccion = cliente.direccion
    ? `<p><strong>Dirección de entrega:</strong> ${escaparHtml(cliente.direccion)}</p>`
    : '';

  const html = `<!DOCTYPE html>
<html lang="es">
<head><meta charset="utf-8"><title>${escaparHtml(asunto)}</title></head>
<body style="margin:0;padding:24px;background:#f4f4f5;font-family:Arial,sans-serif;color:#18181b">
  <div style="max-width:640px;margin:0 auto;background:#ffffff;border-radius:8px;padding:24px">
    <h1 style="margin:0 0 4px;font-size:22px">NOVA Sneakers</h1>
    <p style="margin:0 0 20px;color:#52525b">Recibo del pedido <strong>${escaparHtml(pedido.referencia)}</strong> · ${escaparHtml(pedido.fecha)}</p>
    <p>Hola, ${escaparHtml(cliente.nombre)}:</p>
    <p>Gracias por tu compra. Estas son las zapatillas de tu pedido:</p>
    <table style="width:100%;border-collapse:collapse;font-size:14px">
      <thead>
        <tr style="text-align:left;color:#52525b">
          <th scope="col" style="${celda}">Zapatilla</th>
          <th scope="col" style="${celda}">Color</th>
          <th scope="col" style="${celda}">Talla</th>
          <th scope="col" style="${celda}text-align:right">Cantidad</th>
          <th scope="col" style="${celda}text-align:right">Precio</th>
          <th scope="col" style="${celda}text-align:right">Subtotal</th>
        </tr>
      </thead>
      <tbody>${filas}
      </tbody>
      <tfoot>
        <tr>
          <th scope="row" colspan="5" style="padding:12px 8px;text-align:right">Total</th>
          <td style="padding:12px 8px;text-align:right;font-weight:bold">${escaparHtml(euros(pedido.total))}</td>
        </tr>
      </tfoot>
    </table>
    ${direccion}
    <p style="margin:20px 0 0;padding:12px;border:1px solid #c9a24b;border-radius:6px;background:#fdf8ec">
      <strong>${AVISO}</strong>
    </p>
  </div>
</body>
</html>`;

  return { asunto, html, texto };
}

// ---------------------------------------------------------------------
// Que proveedor toca
// ---------------------------------------------------------------------

// 'resend', 'ethereal', 'ethereal-prohibido' (ethereal en produccion) o
// 'desconocido'. Si no se indica CORREO_PROVEEDOR, Resend, como siempre.
function proveedor() {
  const elegido = (process.env.CORREO_PROVEEDOR || '').trim().toLowerCase() || 'resend';
  if (elegido === 'ethereal' && process.env.NODE_ENV === 'production') return 'ethereal-prohibido';
  if (elegido === 'resend' || elegido === 'ethereal') return elegido;
  return 'desconocido';
}

const MOTIVOS = {
  'ethereal-prohibido': 'CORREO_PROVEEDOR=ethereal no se admite con NODE_ENV=production',
  desconocido: 'CORREO_PROVEEDOR no es valido (tiene que ser resend o ethereal)'
};

// La linea que escribe servidor.js al arrancar
function resumen() {
  const elegido = proveedor();
  if (elegido === 'ethereal') {
    return 'Recibos por correo de PRUEBA con Ethereal (solo desarrollo): no llega ningun correo real';
  }
  if (elegido !== 'resend') return `${MOTIVOS[elegido]}: no se envian recibos`;
  return process.env.RESEND_API_KEY && process.env.RESEND_FROM
    ? 'Recibos por correo activados (Resend)'
    : 'Recibos por correo sin configurar (faltan RESEND_API_KEY y RESEND_FROM en .env): no se envian';
}

// Envia el recibo al correo con el que se registro el cliente.
// No lanza nunca errores: devuelve true si el proveedor lo ha aceptado y
// false si no se ha enviado (y lo apunta en la consola).
async function enviarRecibo(cliente, pedido) {
  const elegido = proveedor();
  if (elegido === 'resend') return enviarConResend(cliente, pedido);
  if (elegido === 'ethereal') return enviarConEthereal(cliente, pedido);
  console.error(`Recibo de ${pedido.referencia} sin enviar: ${MOTIVOS[elegido]}`);
  return false;
}

// ---------------------------------------------------------------------
// Resend
// ---------------------------------------------------------------------
async function enviarConResend(cliente, pedido) {
  const clave = process.env.RESEND_API_KEY;
  const remitente = process.env.RESEND_FROM;
  if (!clave || !remitente) {
    console.log(`Recibo de ${pedido.referencia} sin enviar: falta RESEND_API_KEY o RESEND_FROM en .env`);
    return false;
  }

  const recibo = crearRecibo(cliente, pedido);
  try {
    const respuesta = await fetch(process.env.RESEND_URL || URL_RESEND, {
      method: 'POST',
      headers: { Authorization: `Bearer ${clave}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: remitente,
        to: cliente.email,
        subject: recibo.asunto,
        html: recibo.html,
        text: recibo.texto
      }),
      signal: AbortSignal.timeout(TIEMPO_MAXIMO_MS) // si tarda mas, se corta
    });
    if (!respuesta.ok) {
      // Resend explica el motivo en su respuesta. Por si acaso, se tapa la clave.
      const detalle = (await respuesta.text()).slice(0, 300).replaceAll(clave, '***');
      console.error(`Recibo de ${pedido.referencia} sin enviar: Resend ha respondido ${respuesta.status} ${detalle}`);
      return false;
    }
    console.log(`Recibo de ${pedido.referencia} enviado`);
    return true;
  } catch (error) {
    const motivo = error.name === 'TimeoutError'
      ? `Resend no ha respondido en ${TIEMPO_MAXIMO_MS / 1000} s`
      : `${error.message}${error.cause?.code ? ' (' + error.cause.code + ')' : ''}`;
    console.error(`Recibo de ${pedido.referencia} sin enviar: ${motivo}`);
    return false;
  }
}

// ---------------------------------------------------------------------
// Ethereal (solo desarrollo). Todo se guarda en memoria: al reiniciar el
// servidor se crea otra cuenta y se olvidan las vistas previas.
// ---------------------------------------------------------------------
let transporteEthereal = null;   // la promesa del transporte SMTP
let secretosEthereal = [];       // usuario y contrasena, solo para taparlos en los errores
const vistasPrevias = new Map(); // id del pedido -> URL de la vista previa del recibo

// Pide una cuenta temporal a Ethereal y prepara el transporte SMTP con ella
async function crearTransporteEthereal() {
  const cuenta = await nodemailer.createTestAccount();
  secretosEthereal = [cuenta.user, cuenta.pass];
  return nodemailer.createTransport({
    host: cuenta.smtp.host,
    port: cuenta.smtp.port,
    secure: cuenta.smtp.secure,
    auth: { user: cuenta.user, pass: cuenta.pass },
    connectionTimeout: TIEMPO_MAXIMO_ETHEREAL_MS,
    greetingTimeout: TIEMPO_MAXIMO_ETHEREAL_MS,
    socketTimeout: TIEMPO_MAXIMO_ETHEREAL_MS,
    disableFileAccess: true, // el recibo no lleva adjuntos ni descarga nada
    disableUrlAccess: true
  });
}

// La cuenta se crea en el primer envio y se reutiliza. Si falla (sin red,
// Ethereal caido...), se olvida para volver a probar en el siguiente.
async function mandarAEthereal(mensaje) {
  if (!transporteEthereal) {
    transporteEthereal = crearTransporteEthereal();
    transporteEthereal.catch(() => { transporteEthereal = null; });
  }
  const transporte = await transporteEthereal;
  return transporte.sendMail(mensaje);
}

// Si la promesa tarda mas de ms, falla con un TimeoutError
function conLimite(promesa, ms) {
  let reloj;
  const limite = new Promise((resolver, rechazar) => {
    reloj = setTimeout(() => {
      const error = new Error(`Ethereal no ha respondido en ${ms / 1000} s`);
      error.name = 'TimeoutError';
      rechazar(error);
    }, ms);
  });
  return Promise.race([promesa, limite]).finally(() => clearTimeout(reloj));
}

function taparSecretos(texto) {
  let limpio = String(texto);
  for (const secreto of secretosEthereal) {
    if (secreto) limpio = limpio.replaceAll(secreto, '***');
  }
  return limpio;
}

// El mismo recibo que con Resend. Guarda la URL de la vista previa para el
// detalle del pedido y la escribe en la consola.
async function enviarConEthereal(cliente, pedido) {
  const recibo = crearRecibo(cliente, pedido);
  try {
    const info = await conLimite(mandarAEthereal({
      from: REMITENTE_ETHEREAL,
      to: cliente.email,
      subject: recibo.asunto,
      html: recibo.html,
      text: recibo.texto
    }), TIEMPO_MAXIMO_ETHEREAL_MS);
    const url = nodemailer.getTestMessageUrl(info);
    if (!url) {
      console.error(`Recibo de ${pedido.referencia} enviado, pero Ethereal no ha dado vista previa`);
      return true;
    }
    vistasPrevias.set(pedido.id, url);
    console.log(`Vista previa del recibo ${pedido.referencia}: ${url}`);
    return true;
  } catch (error) {
    const motivo = error.name === 'TimeoutError' ? error.message : `Ethereal ha fallado: ${error.message}`;
    console.error(`Recibo de ${pedido.referencia} sin enviar: ${taparSecretos(motivo)}`);
    return false;
  }
}

// La URL de la vista previa del recibo de ese pedido: solo con Ethereal y
// solo si se ha enviado. Si no, null.
function vistaPrevia(idPedido) {
  if (proveedor() !== 'ethereal') return null;
  return vistasPrevias.get(idPedido) || null;
}

// Solo para las pruebas automaticas: un transporte de Nodemailer que no sale
// a la red, en lugar de la cuenta de Ethereal
function usarTransporteDePrueba(transporte) {
  transporteEthereal = Promise.resolve(transporte);
}

module.exports = { enviarRecibo, crearRecibo, resumen, vistaPrevia, usarTransporteDePrueba };
