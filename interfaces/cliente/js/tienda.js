// tienda.js — la tienda online de NOVA Sneakers.
//
// Qué hace este archivo:
//   1. Pide al servidor el catálogo real: precio, colores, tallas y stock de
//      PostgreSQL. Con eso marca qué modelos de la web se pueden comprar.
//   2. En la ficha: elegir color, talla y cantidad, y añadir al carrito.
//   3. El carrito se guarda en el navegador (localStorage) con SOLO el SKU y
//      la cantidad. El precio se vuelve a leer siempre del servidor.
//   4. La cuenta: registro, inicio de sesión (el diálogo de Álvaro) y salir.
//   5. El pedido en tres pasos: entrega -> pago simulado -> resultado.
//   6. Mis pedidos: el historial del cliente.
//
// Lo que manda lo deciden el servidor (servidor-admin/tienda.js) y
// PostgreSQL: el precio y el total del pedido, el stock y de quién es cada
// pedido. El total del carrito que se calcula aquí es solo una estimación
// para enseñarla.
//
// Usa funciones y variables de inicio.js (formatoPrecio, mostrarCatalogo,
// mostrarDatosCompra, dialogo, modeloSeleccionado y las del diálogo de
// acceso) y la lista "modelos" de modelos.js.

const API_TIENDA = "/api/tienda";
const CLAVE_CARRITO = "nova_carrito"; // nombre en localStorage
const MAXIMO_POR_TALLA = 10;
const MAXIMO_PRODUCTOS = 20;
const NOMBRES_ESTADO = {
  pendiente: "Pendiente de pago",
  confirmado: "Confirmado",
  en_preparacion: "En preparación",
  enviado: "Enviado",
  entregado: "Entregado",
  cancelado: "Cancelado",
};

let catalogoTienda = null; // nombre del modelo -> datos de la base (null = sin servidor)
let productosTienda = new Map(); // sku -> { modelo, color, precio, talla, stock }
let clienteActual = null; // { nombre, email, telefono, direccion } o null
let carrito = leerCarrito(); // [{ sku, cantidad }]
let avisosCarrito = []; // cambios que hay que contar al abrir el carrito
let compraActual = null; // { clave, pedido } mientras dura el checkout
let despuesDeEntrar = null; // qué hacer al iniciar sesión (seguir con el pedido...)
let modeloEnFicha = null; // el modelo de la base que enseña la ficha

// ---------------------------------------------------------------------
// Peticiones al servidor
// ---------------------------------------------------------------------

// Devuelve el JSON de la respuesta o lanza un Error con el mensaje del
// servidor (y su código en error.status).
async function pedirTienda(ruta, metodo = "GET", cuerpo) {
  let respuesta;
  try {
    respuesta = await fetch(API_TIENDA + ruta, {
      method: metodo,
      headers: cuerpo ? { "Content-Type": "application/json" } : {},
      body: cuerpo ? JSON.stringify(cuerpo) : undefined,
    });
  } catch {
    throw new Error("No hay conexión con la tienda. Inténtalo de nuevo.");
  }
  let datos = null;
  try {
    datos = await respuesta.json();
  } catch {
    // la respuesta no trae JSON
  }
  if (!respuesta.ok) {
    const error = new Error(
      datos?.error || "La tienda no ha podido atender la petición.",
    );
    error.status = respuesta.status;
    throw error;
  }
  return datos;
}

function mostrarErrorEn(elemento, mensaje) {
  elemento.textContent = mensaje;
  elemento.hidden = false;
}

// ---------------------------------------------------------------------
// 1. Catálogo real
// ---------------------------------------------------------------------
async function cargarCatalogoTienda() {
  try {
    const datos = await pedirTienda("/catalogo");
    catalogoTienda = new Map();
    productosTienda = new Map();
    for (const modelo of datos.modelos) {
      catalogoTienda.set(modelo.nombre, modelo);
      for (const variante of modelo.variantes) {
        for (const talla of variante.tallas) {
          productosTienda.set(talla.sku, {
            modelo: modelo.nombre,
            color: variante.color,
            precio: variante.precio,
            talla: talla.talla,
            stock: talla.stock,
          });
        }
      }
    }
  } catch {
    catalogoTienda = null; // sin servidor: se ve el escaparate, pero no se compra
  }
  mostrarCatalogo(); // inicio.js: vuelve a pintar las tarjetas con el estado real
  if (dialogo.open && modeloSeleccionado) mostrarDatosCompra(modeloSeleccionado);
  revisarCarrito();
}

// Para inicio.js: el precio real y el estado de un modelo de la web.
// null si no hay servidor (entonces la web enseña el precio orientativo).
function datosEnTienda(modelo) {
  if (!catalogoTienda) return null;
  const enBase = catalogoTienda.get(modelo.nombre);
  if (!enBase) {
    return { precio: null, estado: "No disponible", clase: "no-disponible" };
  }
  const precio = Math.min(...enBase.variantes.map((v) => v.precio));
  const hayStock = enBase.variantes.some((v) => v.tallas.some((t) => t.stock > 0));
  return hayStock
    ? { precio, estado: "Disponible", clase: "disponible" }
    : { precio, estado: "Agotado", clase: "agotado" };
}

// ---------------------------------------------------------------------
// 2. La ficha: color, talla, cantidad y "Añadir al carrito"
// ---------------------------------------------------------------------
const bloqueCompra = document.querySelector("#compra");
const avisoCompra = document.querySelector("#compra-aviso");
const opcionesColor = document.querySelector("#compra-colores");
const opcionesTalla = document.querySelector("#compra-tallas");
const textoStock = document.querySelector("#compra-stock");
const campoCantidad = document.querySelector("#compra-cantidad");
const botonAnadir = document.querySelector("#compra-anadir");
const mensajeAnadir = document.querySelector("#compra-mensaje");
const etiquetaPrecio = document.querySelector("#detalle-etiqueta-precio");
const notaPrecio = document.querySelector("#detalle-nota-precio");

// Llamada desde mostrarDatosCompra (inicio.js) cada vez que se abre la ficha.
function mostrarCompraEnFicha(modelo) {
  modeloEnFicha = catalogoTienda?.get(modelo.nombre) || null;
  avisarEnFicha("");
  if (!modeloEnFicha) {
    bloqueCompra.hidden = true;
    avisoCompra.hidden = false;
    avisoCompra.textContent = catalogoTienda
      ? "No disponible: este modelo todavía no está a la venta en la tienda online."
      : "La tienda online no está disponible en este momento. Puedes seguir viendo el catálogo.";
    // El precio que ha puesto inicio.js es el orientativo de la colección
    etiquetaPrecio.textContent = "PRECIO ORIENTATIVO";
    notaPrecio.textContent = "El precio final se confirma en el presupuesto.";
    return;
  }
  avisoCompra.hidden = true;
  bloqueCompra.hidden = false;
  etiquetaPrecio.textContent = "PRECIO";
  notaPrecio.textContent = "Precio de la tienda online de NOVA.";
  opcionesColor.replaceChildren();
  modeloEnFicha.variantes.forEach((variante, indice) => {
    opcionesColor.append(
      crearOpcion("color", String(indice), variante.color, false, indice === 0),
    );
  });
  pintarTallas();
}

// Una opción de radio con su texto, para los colores y las tallas
function crearOpcion(grupo, valor, texto, desactivada, marcada, descripcion) {
  const etiqueta = document.createElement("label");
  etiqueta.className = "compra-opcion";
  const radio = document.createElement("input");
  radio.type = "radio";
  radio.name = grupo;
  radio.value = valor;
  radio.disabled = desactivada;
  radio.checked = marcada;
  if (descripcion) radio.setAttribute("aria-label", descripcion);
  const nombre = document.createElement("b");
  nombre.textContent = texto;
  etiqueta.append(radio, nombre);
  return etiqueta;
}

function varianteElegida() {
  const marcada = opcionesColor.querySelector("input:checked");
  return modeloEnFicha.variantes[Number(marcada ? marcada.value : 0)];
}

function pintarTallas() {
  const variante = varianteElegida();
  document.querySelector("#detalle-precio").textContent = formatoPrecio(variante.precio);
  opcionesTalla.replaceChildren();
  for (const talla of variante.tallas) {
    const agotada = talla.stock === 0;
    opcionesTalla.append(
      crearOpcion(
        "talla",
        String(talla.sku),
        String(talla.talla),
        agotada,
        false,
        agotada ? `Talla ${talla.talla}, agotada` : null,
      ),
    );
  }
  const hayStock = variante.tallas.some((t) => t.stock > 0);
  textoStock.textContent = hayStock
    ? "Elige una talla. Las tachadas están agotadas."
    : "Agotado: no queda ninguna talla de este color.";
  botonAnadir.disabled = !hayStock;
  campoCantidad.value = 1;
  campoCantidad.max = MAXIMO_POR_TALLA;
}

function tallaElegida() {
  const marcada = opcionesTalla.querySelector("input:checked");
  return marcada ? Number(marcada.value) : null;
}

opcionesColor.addEventListener("change", () => {
  avisarEnFicha("");
  pintarTallas();
});

opcionesTalla.addEventListener("change", () => {
  avisarEnFicha("");
  const producto = productosTienda.get(tallaElegida());
  const enCarrito = cantidadEnCarrito(tallaElegida());
  textoStock.textContent =
    (producto.stock <= 3
      ? `Últimos ${producto.stock} pares de la talla ${producto.talla}.`
      : `Quedan ${producto.stock} pares de la talla ${producto.talla}.`) +
    (enCarrito ? ` Ya tienes ${enCarrito} en el carrito.` : "");
  campoCantidad.max = Math.max(1, Math.min(MAXIMO_POR_TALLA, producto.stock) - enCarrito);
});

function avisarEnFicha(texto, esError = false) {
  mensajeAnadir.textContent = texto;
  mensajeAnadir.classList.toggle("error", esError);
}

botonAnadir.addEventListener("click", () => {
  const sku = tallaElegida();
  if (!sku) {
    avisarEnFicha("Elige una talla.", true);
    opcionesTalla.querySelector("input:not(:disabled)")?.focus();
    return;
  }
  const cantidad = Number(campoCantidad.value);
  if (!Number.isInteger(cantidad) || cantidad < 1) {
    avisarEnFicha("La cantidad tiene que ser un número entero, de 1 en adelante.", true);
    campoCantidad.focus();
    return;
  }
  const producto = productosTienda.get(sku);
  const enCarrito = cantidadEnCarrito(sku);
  const maximo = Math.min(MAXIMO_POR_TALLA, producto.stock);
  if (enCarrito + cantidad > maximo) {
    avisarEnFicha(
      `Como mucho puedes llevar ${maximo} pares de esta talla` +
        (enCarrito ? ` y ya tienes ${enCarrito} en el carrito.` : "."),
      true,
    );
    return;
  }
  const linea = carrito.find((l) => l.sku === sku);
  if (linea) {
    linea.cantidad += cantidad;
  } else if (carrito.length >= MAXIMO_PRODUCTOS) {
    avisarEnFicha(`El carrito admite como mucho ${MAXIMO_PRODUCTOS} productos distintos.`, true);
    return;
  } else {
    carrito.push({ sku, cantidad });
  }
  guardarCarrito();
  pintarContador();
  avisarEnFicha(
    `Añadido al carrito: ${producto.modelo}, talla ${producto.talla} (${cantidad} ${cantidad === 1 ? "par" : "pares"}).`,
  );
});

// ---------------------------------------------------------------------
// 3. El carrito (localStorage)
// ---------------------------------------------------------------------
const dialogoCarrito = document.querySelector("#carrito");
const listaCarrito = document.querySelector("#carrito-lista");
const avisosDelCarrito = document.querySelector("#carrito-avisos");
const carritoVacio = document.querySelector("#carrito-vacio");
const pieCarrito = document.querySelector("#carrito-pie");
const totalCarrito = document.querySelector("#carrito-total");
const botonTramitar = document.querySelector("#carrito-tramitar");
const contadorCarrito = document.querySelector("#carrito-contador");

// Lo guardado puede estar roto o manipulado: solo se aceptan SKU y
// cantidades enteras. Si el navegador no deja usar localStorage (modo
// privado, por ejemplo), el carrito dura hasta recargar.
function leerCarrito() {
  try {
    const guardado = JSON.parse(localStorage.getItem(CLAVE_CARRITO) || "[]");
    if (!Array.isArray(guardado)) return [];
    return guardado
      .filter((l) => Number.isInteger(l?.sku) && Number.isInteger(l?.cantidad) && l.cantidad > 0)
      .map((l) => ({ sku: l.sku, cantidad: Math.min(l.cantidad, MAXIMO_POR_TALLA) }))
      .slice(0, MAXIMO_PRODUCTOS);
  } catch {
    return [];
  }
}

function guardarCarrito() {
  try {
    localStorage.setItem(CLAVE_CARRITO, JSON.stringify(carrito));
  } catch {
    // sin localStorage: no se guarda
  }
}

function cantidadEnCarrito(sku) {
  return carrito.find((l) => l.sku === sku)?.cantidad ?? 0;
}

function paresEnCarrito() {
  return carrito.reduce((suma, linea) => suma + linea.cantidad, 0);
}

// Estimación para enseñar: el total que vale lo calcula PostgreSQL
function totalEstimado() {
  return carrito.reduce(
    (suma, linea) => suma + (productosTienda.get(linea.sku)?.precio ?? 0) * linea.cantidad,
    0,
  );
}

function pintarContador() {
  contadorCarrito.textContent = `(${paresEnCarrito()})`;
}

// Con el catálogo recién leído: fuera lo que ya no existe o está agotado, y
// las cantidades no pueden pasar del stock.
function revisarCarrito() {
  if (catalogoTienda) {
    const revisado = [];
    for (const linea of carrito) {
      const producto = productosTienda.get(linea.sku);
      if (!producto) {
        avisosCarrito.push("Hemos quitado un producto que ya no está a la venta.");
        continue;
      }
      if (producto.stock === 0) {
        avisosCarrito.push(`${producto.modelo} (talla ${producto.talla}) se ha agotado y lo hemos quitado.`);
        continue;
      }
      const maximo = Math.min(MAXIMO_POR_TALLA, producto.stock);
      if (linea.cantidad > maximo) {
        avisosCarrito.push(
          `De ${producto.modelo} (talla ${producto.talla}) solo quedan ${producto.stock}: hemos ajustado la cantidad.`,
        );
        linea.cantidad = maximo;
      }
      revisado.push(linea);
    }
    carrito = revisado;
    guardarCarrito();
  }
  pintarContador();
  if (dialogoCarrito.open) pintarCarrito();
}

function pintarCarrito() {
  avisosDelCarrito.replaceChildren(
    ...avisosCarrito.map((texto) => {
      const item = document.createElement("li");
      item.textContent = texto;
      return item;
    }),
  );
  avisosCarrito = []; // se cuentan una sola vez
  listaCarrito.replaceChildren();
  const vacio = carrito.length === 0;
  carritoVacio.hidden = !vacio;
  pieCarrito.hidden = vacio;
  if (vacio) return;

  if (!catalogoTienda) {
    carritoVacio.hidden = false;
    carritoVacio.textContent =
      "La tienda online no está disponible en este momento. Tu carrito sigue guardado.";
    pieCarrito.hidden = true;
    return;
  }
  carritoVacio.textContent =
    "Tu carrito está vacío. Elige un modelo en el catálogo y añádelo desde su ficha.";

  for (const linea of carrito) {
    const producto = productosTienda.get(linea.sku);
    const descripcion = `${producto.modelo}, talla ${producto.talla}`;
    const item = document.createElement("li");
    item.className = "carrito-linea";

    const foto = document.createElement("img");
    foto.src = modelos.find((m) => m.nombre === producto.modelo)?.imagen || "";
    foto.alt = "";

    const datos = document.createElement("div");
    datos.className = "carrito-datos";
    const nombre = document.createElement("strong");
    nombre.textContent = producto.modelo;
    const detalle = document.createElement("small");
    detalle.textContent = `${producto.color} · Talla ${producto.talla} · ${formatoPrecio(producto.precio)} el par`;
    datos.append(nombre, detalle);

    const etiqueta = document.createElement("label");
    etiqueta.className = "carrito-cantidad";
    etiqueta.textContent = "Pares ";
    const campo = document.createElement("input");
    campo.type = "number";
    campo.min = 1;
    campo.max = Math.min(MAXIMO_POR_TALLA, producto.stock);
    campo.step = 1;
    campo.value = linea.cantidad;
    campo.dataset.sku = linea.sku;
    campo.setAttribute("aria-label", `Pares de ${descripcion}`);
    etiqueta.append(campo);

    const subtotal = document.createElement("strong");
    subtotal.className = "carrito-subtotal";
    subtotal.textContent = formatoPrecio(producto.precio * linea.cantidad);

    const quitar = document.createElement("button");
    quitar.type = "button";
    quitar.className = "enlace-boton";
    quitar.textContent = "Quitar";
    quitar.dataset.quitar = linea.sku;
    quitar.setAttribute("aria-label", `Quitar ${descripcion}`);

    item.append(foto, datos, etiqueta, subtotal, quitar);
    listaCarrito.append(item);
  }
  totalCarrito.textContent = formatoPrecio(totalEstimado());
}

function abrirCarrito() {
  pintarCarrito();
  if (!dialogoCarrito.open) dialogoCarrito.showModal();
}

// Cambiar la cantidad de una línea
listaCarrito.addEventListener("change", (evento) => {
  const sku = Number(evento.target.dataset.sku);
  const linea = carrito.find((l) => l.sku === sku);
  if (!linea) return;
  const producto = productosTienda.get(sku);
  const maximo = Math.min(MAXIMO_POR_TALLA, producto.stock);
  const cantidad = Number(evento.target.value);
  if (!Number.isInteger(cantidad) || cantidad < 1 || cantidad > maximo) {
    avisosCarrito.push(
      `La cantidad de ${producto.modelo} (talla ${producto.talla}) tiene que ser un número entero de 1 a ${maximo}.`,
    );
  } else {
    linea.cantidad = cantidad;
    guardarCarrito();
  }
  pintarContador();
  pintarCarrito();
  listaCarrito.querySelector(`input[data-sku="${sku}"]`)?.focus();
});

// Quitar una línea
listaCarrito.addEventListener("click", (evento) => {
  const boton = evento.target.closest("button[data-quitar]");
  if (!boton) return;
  carrito = carrito.filter((l) => l.sku !== Number(boton.dataset.quitar));
  guardarCarrito();
  pintarContador();
  pintarCarrito();
  (listaCarrito.querySelector("input") || dialogoCarrito.querySelector(".cerrar"))?.focus();
});

document.querySelector("#carrito-vaciar").addEventListener("click", () => {
  carrito = [];
  guardarCarrito();
  pintarContador();
  pintarCarrito();
  dialogoCarrito.querySelector(".cerrar").focus();
});

document.querySelector("#abrir-carrito").addEventListener("click", abrirCarrito);

botonTramitar.addEventListener("click", () => {
  if (!clienteActual) {
    despuesDeEntrar = abrirCheckout;
    dialogoCarrito.close();
    abrirAcceso("Inicia sesión o crea una cuenta para tramitar el pedido.");
    return;
  }
  abrirCheckout();
});

// ---------------------------------------------------------------------
// 4. La cuenta: sesión, registro, inicio de sesión y salir
// ---------------------------------------------------------------------
const saludoCuenta = document.querySelector("#barra-saludo");
const enlaceAcceso = document.querySelector("#abrir-acceso");
const botonMisPedidos = document.querySelector("#abrir-pedidos");
const botonSalir = document.querySelector("#cerrar-sesion");
const dialogoRegistro = document.querySelector("#registro");
const formularioRegistro = document.querySelector("#formulario-registro");
const errorRegistro = document.querySelector("#registro-error");

async function cargarSesion() {
  try {
    clienteActual = (await pedirTienda("/sesion")).cliente;
  } catch {
    clienteActual = null;
  }
  pintarCuenta();
}

function pintarCuenta() {
  const dentro = Boolean(clienteActual);
  saludoCuenta.hidden = !dentro;
  saludoCuenta.textContent = dentro ? `Hola, ${clienteActual.nombre.split(" ")[0]}` : "";
  enlaceAcceso.hidden = dentro;
  botonMisPedidos.hidden = !dentro;
  botonSalir.hidden = !dentro;
}

// Abre el diálogo de acceso de Álvaro con un aviso (por ejemplo, "inicia
// sesión para tramitar el pedido")
function abrirAcceso(aviso) {
  errorAcceso.textContent = aviso || "";
  errorAcceso.hidden = !aviso;
  dialogoAcceso.showModal();
}

// Al entrar: ocultar los diálogos de cuenta y seguir con lo pendiente
function alEntrar() {
  pintarCuenta();
  const siguiente = despuesDeEntrar;
  despuesDeEntrar = null;
  if (dialogoAcceso.open) dialogoAcceso.close();
  if (dialogoRegistro.open) dialogoRegistro.close();
  if (siguiente) siguiente();
}

// Llamada desde el formulario de Álvaro (inicio.js) cuando los dos campos
// están rellenos
async function iniciarSesionCliente(email, contrasena) {
  const boton = formularioAcceso.querySelector('button[type="submit"]');
  boton.disabled = true;
  try {
    await pedirTienda("/login", "POST", { email, contrasena });
    campoClaveAcceso.value = "";
    await cargarSesion();
    alEntrar();
  } catch (error) {
    mostrarErrorAcceso(error.message);
  } finally {
    boton.disabled = false;
  }
}

formularioRegistro.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  errorRegistro.hidden = true;
  const campo = (id) => document.querySelector(id);
  const nombre = campo("#registro-nombre").value.trim();
  const email = campo("#registro-email").value.trim();
  const contrasena = campo("#registro-clave").value;
  if (!nombre) {
    mostrarErrorEn(errorRegistro, "Escribe tu nombre.");
    return campo("#registro-nombre").focus();
  }
  if (!email || !campo("#registro-email").checkValidity()) {
    mostrarErrorEn(errorRegistro, "Escribe un correo válido.");
    return campo("#registro-email").focus();
  }
  if (contrasena.length < 8) {
    mostrarErrorEn(errorRegistro, "La contraseña debe tener al menos 8 caracteres.");
    return campo("#registro-clave").focus();
  }
  const boton = formularioRegistro.querySelector('button[type="submit"]');
  boton.disabled = true;
  try {
    await pedirTienda("/registro", "POST", {
      nombre,
      email,
      contrasena,
      telefono: campo("#registro-telefono").value.trim(),
      direccion: campo("#registro-direccion").value.trim(),
    });
    formularioRegistro.reset();
    await cargarSesion();
    alEntrar();
  } catch (error) {
    mostrarErrorEn(errorRegistro, error.message);
  } finally {
    boton.disabled = false;
  }
});

// Pasar de un diálogo de cuenta al otro (lo pendiente se conserva)
function cambiarDialogoDeCuenta(cerrar, abrir) {
  cerrar.close();
  errorRegistro.hidden = true;
  errorAcceso.hidden = true;
  abrir.showModal();
}
document.querySelector("#ir-a-registro").addEventListener("click", () =>
  cambiarDialogoDeCuenta(dialogoAcceso, dialogoRegistro),
);
document.querySelector("#ir-a-acceso").addEventListener("click", () =>
  cambiarDialogoDeCuenta(dialogoRegistro, dialogoAcceso),
);

// Si cierra el acceso o el registro sin entrar, se olvida lo pendiente.
// El evento "close" llega un instante después de cerrar: si para entonces
// está abierto el otro diálogo de cuenta, es que solo ha cambiado de uno a otro.
for (const dialogoCuenta of [dialogoAcceso, dialogoRegistro]) {
  dialogoCuenta.addEventListener("close", () => {
    if (!clienteActual && !dialogoAcceso.open && !dialogoRegistro.open) {
      despuesDeEntrar = null;
    }
  });
}

botonSalir.addEventListener("click", async () => {
  try {
    await pedirTienda("/logout", "POST");
  } catch {
    // aunque falle la petición, en esta página se sale igual
  }
  clienteActual = null;
  pintarCuenta();
  enlaceAcceso.focus();
});

// ---------------------------------------------------------------------
// 5. El pedido: entrega -> pago simulado -> resultado
// ---------------------------------------------------------------------
const dialogoCheckout = document.querySelector("#checkout");
const formularioEntrega = document.querySelector("#paso-entrega");
const errorEntrega = document.querySelector("#entrega-error");
const campoTelefono = document.querySelector("#entrega-telefono");
const campoDireccion = document.querySelector("#entrega-direccion");
const errorPago = document.querySelector("#pago-error");
const botonesPago = ["#pago-aceptar", "#pago-rechazar", "#pago-cancelar"].map((id) =>
  document.querySelector(id),
);

function mostrarPaso(paso) {
  for (const nombre of ["entrega", "pago", "resultado"]) {
    document.querySelector(`#paso-${nombre}`).hidden = nombre !== paso;
  }
  dialogoCheckout.querySelectorAll(".checkout-pasos li").forEach((item) => {
    if (item.dataset.paso === paso) item.setAttribute("aria-current", "step");
    else item.removeAttribute("aria-current");
  });
}

function abrirCheckout() {
  revisarCarrito();
  if (carrito.length === 0 || !catalogoTienda) {
    abrirCarrito();
    return;
  }
  // La clave identifica ESTA compra. Si la misma petición llega dos veces
  // (doble clic, reintento), el servidor devuelve el mismo pedido.
  compraActual = { clave: crypto.randomUUID(), pedido: null };
  document.querySelector("#entrega-nombre").textContent = clienteActual.nombre;
  document.querySelector("#entrega-email").textContent = clienteActual.email;
  campoTelefono.value = clienteActual.telefono || "";
  campoDireccion.value = clienteActual.direccion || "";
  const pares = paresEnCarrito();
  document.querySelector("#entrega-resumen").textContent =
    `${pares} ${pares === 1 ? "par" : "pares"} · total estimado ${formatoPrecio(totalEstimado())}.`;
  errorEntrega.hidden = true;
  mostrarPaso("entrega");
  if (dialogoCarrito.open) dialogoCarrito.close();
  dialogoCheckout.showModal();
}

// La sesión ha caducado en mitad de la compra: volver a entrar y seguir
function pedirQueVuelvaAEntrar() {
  clienteActual = null;
  pintarCuenta();
  if (dialogoCheckout.open) dialogoCheckout.close();
  despuesDeEntrar = abrirCheckout;
  abrirAcceso("Tu sesión ha caducado. Vuelve a entrar para terminar el pedido.");
}

// Paso 1 -> 2: crear el pedido PENDIENTE. El servidor lo crea con las
// funciones de PostgreSQL y devuelve las líneas con su precio y el total.
formularioEntrega.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  errorEntrega.hidden = true;
  const direccion = campoDireccion.value.trim();
  if (!direccion) {
    mostrarErrorEn(errorEntrega, "Escribe la dirección de entrega.");
    campoDireccion.focus();
    return;
  }
  const boton = document.querySelector("#entrega-continuar");
  boton.disabled = true; // contra el doble clic (y la clave hace el resto)
  try {
    const pedido = await pedirTienda("/pedidos", "POST", {
      clave: compraActual.clave,
      lineas: carrito.map((linea) => ({ sku: linea.sku, cantidad: linea.cantidad })),
      telefono: campoTelefono.value.trim(),
      direccion,
    });
    compraActual.pedido = pedido;
    clienteActual.telefono = campoTelefono.value.trim();
    clienteActual.direccion = direccion;
    pintarPedidoPendiente(pedido);
    mostrarPaso("pago");
    document.querySelector("#pago-aceptar").focus();
  } catch (error) {
    if (error.status === 401) return pedirQueVuelvaAEntrar();
    mostrarErrorEn(errorEntrega, error.message);
    if (error.status === 409) cargarCatalogoTienda(); // el stock ha cambiado
  } finally {
    boton.disabled = false;
  }
});

function pintarPedidoPendiente(pedido) {
  document.querySelector("#pago-referencia").textContent = pedido.referencia;
  const cuerpo = document.querySelector("#pago-lineas");
  cuerpo.replaceChildren();
  for (const linea of pedido.lineas) {
    const fila = document.createElement("tr");
    const celdas = [
      `${linea.modelo} · ${linea.color} · Talla ${linea.talla}`,
      String(linea.cantidad),
      formatoPrecio(linea.precio),
      formatoPrecio(linea.subtotal),
    ];
    for (const texto of celdas) {
      const celda = document.createElement("td");
      celda.textContent = texto;
      fila.append(celda);
    }
    cuerpo.append(fila);
  }
  document.querySelector("#pago-total").textContent = formatoPrecio(pedido.total);
  errorPago.hidden = true;
  botonesPago.forEach((boton) => (boton.disabled = false));
}

// Paso 2 -> 3: el resultado del pago SIMULADO
async function pagar(resultado) {
  botonesPago.forEach((boton) => (boton.disabled = true));
  errorPago.hidden = true;
  const pedidoAntes = compraActual.pedido;
  try {
    const pedido = await pedirTienda(`/pedidos/${pedidoAntes.id}/pago`, "POST", { resultado });
    compraActual.pedido = pedido;
    if (pedido.estado === "confirmado") {
      carrito = [];
      guardarCarrito();
      pintarContador();
      mostrarResultado(
        "Pedido confirmado.",
        `Pago simulado aceptado: no se ha cobrado nada. Tu pedido ${pedido.referencia} ` +
          `(${pedido.pares} ${pedido.pares === 1 ? "par" : "pares"}, ${formatoPrecio(pedido.total)}) ` +
          "está confirmado. Puedes seguirlo en «Mis pedidos».",
      );
    } else {
      mostrarResultado(
        "Pago rechazado.",
        `Era una simulación: no se ha cobrado nada. El pedido ${pedido.referencia} ` +
          "se ha cancelado y tu carrito sigue guardado.",
      );
    }
    cargarCatalogoTienda(); // el stock ha cambiado
  } catch (error) {
    if (error.status === 401) return pedirQueVuelvaAEntrar();
    if (error.status === 409) {
      // Se ha agotado algo mientras pagaba (el servidor ya ha cancelado el
      // pedido) o el pedido ya no está pendiente
      compraActual.pedido = { ...pedidoAntes, estado: "cancelado" };
      mostrarResultado("No se ha podido completar el pedido.", error.message);
      cargarCatalogoTienda();
      return;
    }
    mostrarErrorEn(errorPago, error.message);
    botonesPago.forEach((boton) => (boton.disabled = false));
  }
}

document.querySelector("#pago-aceptar").addEventListener("click", () => pagar("aceptado"));
document.querySelector("#pago-rechazar").addEventListener("click", () => pagar("rechazado"));

document.querySelector("#pago-cancelar").addEventListener("click", async () => {
  botonesPago.forEach((boton) => (boton.disabled = true));
  try {
    const pedido = await pedirTienda(`/pedidos/${compraActual.pedido.id}/cancelacion`, "POST");
    compraActual.pedido = pedido;
    mostrarResultado(
      "Pedido cancelado.",
      `El pedido ${pedido.referencia} se ha cancelado y no se ha cobrado nada. Tu carrito sigue guardado.`,
    );
  } catch (error) {
    if (error.status === 401) return pedirQueVuelvaAEntrar();
    mostrarErrorEn(errorPago, error.message);
    botonesPago.forEach((boton) => (boton.disabled = false));
  }
});

function mostrarResultado(titulo, texto) {
  const elementoTitulo = document.querySelector("#resultado-titulo");
  elementoTitulo.textContent = titulo;
  document.querySelector("#resultado-texto").textContent = texto;
  mostrarPaso("resultado");
  elementoTitulo.focus();
}

document.querySelector("#resultado-seguir").addEventListener("click", () => dialogoCheckout.close());
document.querySelector("#resultado-pedidos").addEventListener("click", () => {
  dialogoCheckout.close();
  abrirMisPedidos();
});

// Si se cierra la ventana con el pedido sin pagar, se cancela: así no se
// quedan pedidos pendientes olvidados.
dialogoCheckout.addEventListener("close", () => {
  if (dialogoCheckout.open) return; // ya se ha vuelto a abrir para otra compra
  const pedido = compraActual?.pedido;
  if (pedido && pedido.estado === "pendiente") {
    pedirTienda(`/pedidos/${pedido.id}/cancelacion`, "POST").catch(() => {});
  }
  compraActual = null;
});

// ---------------------------------------------------------------------
// 6. Mis pedidos
// ---------------------------------------------------------------------
const dialogoPedidos = document.querySelector("#pedidos");
const listaPedidos = document.querySelector("#pedidos-lista");
const estadoPedidos = document.querySelector("#pedidos-estado");

async function abrirMisPedidos() {
  if (!clienteActual) {
    despuesDeEntrar = abrirMisPedidos;
    abrirAcceso("Inicia sesión para ver tus pedidos.");
    return;
  }
  listaPedidos.replaceChildren();
  estadoPedidos.textContent = "Cargando tus pedidos…";
  if (!dialogoPedidos.open) dialogoPedidos.showModal();
  try {
    const { pedidos } = await pedirTienda("/pedidos");
    estadoPedidos.textContent = pedidos.length
      ? `${pedidos.length} ${pedidos.length === 1 ? "pedido" : "pedidos"}, del más reciente al más antiguo.`
      : "Todavía no has hecho ningún pedido.";
    for (const pedido of pedidos) listaPedidos.append(crearFilaPedido(pedido));
  } catch (error) {
    if (error.status === 401) {
      dialogoPedidos.close();
      clienteActual = null;
      pintarCuenta();
      despuesDeEntrar = abrirMisPedidos;
      abrirAcceso("Tu sesión ha caducado. Vuelve a entrar.");
      return;
    }
    estadoPedidos.textContent = error.message;
  }
}

function crearFilaPedido(pedido) {
  const item = document.createElement("li");
  item.className = "pedido";
  const cabecera = document.createElement("div");
  cabecera.className = "pedido-cabecera";
  const referencia = document.createElement("strong");
  referencia.textContent = pedido.referencia;
  const fecha = document.createElement("span");
  fecha.textContent = pedido.fecha;
  const estado = document.createElement("span");
  estado.className = `pedido-estado estado-${pedido.estado}`;
  estado.textContent = NOMBRES_ESTADO[pedido.estado] || pedido.estado;
  const importe = document.createElement("span");
  importe.textContent = `${pedido.pares} ${pedido.pares === 1 ? "par" : "pares"} · ${formatoPrecio(pedido.total)}`;
  const boton = document.createElement("button");
  boton.type = "button";
  boton.className = "enlace-boton";
  boton.textContent = "Ver detalle";
  boton.setAttribute("aria-expanded", "false");
  const detalle = document.createElement("ul");
  detalle.className = "pedido-lineas";
  detalle.id = `pedido-detalle-${pedido.id}`;
  detalle.hidden = true;
  boton.setAttribute("aria-controls", detalle.id);
  boton.addEventListener("click", () => verDetallePedido(pedido.id, boton, detalle));
  cabecera.append(referencia, fecha, estado, importe, boton);
  item.append(cabecera, detalle);
  return item;
}

async function verDetallePedido(id, boton, detalle) {
  const abrir = detalle.hidden;
  detalle.hidden = !abrir;
  boton.setAttribute("aria-expanded", String(abrir));
  boton.textContent = abrir ? "Ocultar detalle" : "Ver detalle";
  if (!abrir || detalle.childElementCount > 0) return;
  try {
    const pedido = await pedirTienda(`/pedidos/${id}`);
    for (const linea of pedido.lineas) {
      const item = document.createElement("li");
      item.textContent =
        `${linea.modelo} · ${linea.color} · Talla ${linea.talla} · ` +
        `${linea.cantidad} × ${formatoPrecio(linea.precio)} = ${formatoPrecio(linea.subtotal)}`;
      detalle.append(item);
    }
  } catch (error) {
    const item = document.createElement("li");
    item.textContent = error.message;
    detalle.append(item);
  }
}

botonMisPedidos.addEventListener("click", abrirMisPedidos);

// ---------------------------------------------------------------------
// Cerrar los diálogos de la tienda: la × y, salvo en el pedido, el fondo
// (en el pedido no, para no cancelarlo sin querer)
// ---------------------------------------------------------------------
for (const dialogoTienda of [dialogoRegistro, dialogoCarrito, dialogoCheckout, dialogoPedidos]) {
  dialogoTienda
    .querySelector(".cerrar-dialogo")
    .addEventListener("click", () => dialogoTienda.close());
  if (dialogoTienda !== dialogoCheckout) {
    dialogoTienda.addEventListener("click", (evento) => {
      if (evento.target === dialogoTienda) dialogoTienda.close();
    });
  }
}

// Si se vuelve a esta página con «Atrás» después de cerrar sesión, el
// navegador podría enseñarla tal como estaba: se recarga para pedir la
// sesión otra vez.
window.addEventListener("pageshow", (evento) => {
  if (evento.persisted) location.reload();
});

// Al cargar la página
pintarContador();
cargarCatalogoTienda();
cargarSesion();
