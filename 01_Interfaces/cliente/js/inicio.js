// Funciones de la portada. Los datos de las zapatillas están en modelos.js.
const estanterias = document.querySelector("#estanterias");
const busqueda = document.querySelector("#busqueda");
const resultados = document.querySelector("#resultados");
const vacio = document.querySelector("#vacio");
const dialogo = document.querySelector("#detalle");
let filtro = "casual";
let ultimoBoton = null;
let modeloSeleccionado = null;

// Precio con formato español: 109.9 -> "109,90 €".
function formatoPrecio(precio) {
  return precio.toLocaleString("es-ES", { style: "currency", currency: "EUR" });
}
// Escribe en la ficha el precio, la descripción y las tallas de la colección.
function mostrarDatosCompra(modelo) {
  const datos = datosColeccion[modelo.coleccion];
  document.querySelector("#detalle-precio").textContent = formatoPrecio(
    datos.precio,
  );
  document.querySelector("#detalle-descripcion").textContent =
    datos.descripcion;
  document.querySelector("#detalle-tallas").textContent =
    `Tallas: ${datos.tallas.join(", ")}`;
  // Tienda (js/tienda.js): precio real, colores, tallas con stock y carrito.
  if (typeof mostrarCompraEnFicha === "function") mostrarCompraEnFicha(modelo);
}

function mostrarModelos() {
  const consulta = busqueda.value.trim().toLocaleLowerCase("es");
  const visibles = modelos.filter(
    (modelo) =>
      (filtro === "todos" || modelo.coleccion === filtro) &&
      modelo.nombre.toLocaleLowerCase("es").includes(consulta),
  );
  // El escaparate muestra como máximo ocho; el catálogo contiene la colección completa.
  const seleccion = visibles.slice(0, 8);
  estanterias.replaceChildren();
  seleccion.forEach((modelo) => {
    const tarjeta = document.createElement("article");
    tarjeta.className = "zapatilla";
    const boton = document.createElement("button");
    boton.className = "tarjeta";
    boton.type = "button";
    boton.setAttribute("aria-label", `Ver ${modelo.nombre}`);
    const imagen = document.createElement("img");
    imagen.src = modelo.imagen;
    imagen.alt = "";
    imagen.loading = "lazy";
    boton.append(imagen);
    const datos = document.createElement("span");
    datos.className = "datos";
    const nombre = document.createElement("strong");
    nombre.textContent = modelo.nombre;
    const accion = document.createElement("span");
    accion.textContent = "Ver modelo ↗";
    datos.append(nombre, accion);
    boton.append(datos);
    boton.addEventListener("click", () => abrirDetalle(modelo, boton));
    tarjeta.append(boton);
    estanterias.append(tarjeta);
  });
  resultados.textContent =
    visibles.length > seleccion.length
      ? `${seleccion.length} de ${visibles.length} modelos · colección completa en el catálogo`
      : `${visibles.length} ${visibles.length === 1 ? "modelo" : "modelos"}`;
  vacio.hidden = visibles.length > 0;
}
function abrirDetalle(modelo, boton) {
  modeloSeleccionado = modelo;
  ultimoBoton = boton;
  document.querySelector("#detalle-titulo").textContent = modelo.nombre;
  document.querySelector("#detalle-coleccion").textContent =
    `COLECCIÓN ${modelo.coleccion.toUpperCase()}`;
  const imagen = document.querySelector("#detalle-imagen");
  imagen.src = modelo.imagen;
  imagen.alt = `Vista de ${modelo.nombre}`;
  mostrarDatosCompra(modelo);
  dialogo.showModal();
}
document.querySelectorAll(".filtro").forEach((boton) =>
  boton.addEventListener("click", () => {
    filtro = boton.dataset.filtro;
    document.querySelectorAll(".filtro").forEach((item) => {
      const activo = item === boton;
      item.classList.toggle("activo", activo);
      item.setAttribute("aria-pressed", String(activo));
    });
    mostrarModelos();
  }),
);
busqueda.addEventListener("input", mostrarModelos);
dialogo
  .querySelectorAll(".cerrar, .cerrar-secundario")
  .forEach((boton) => boton.addEventListener("click", () => dialogo.close()));
dialogo.addEventListener("click", (evento) => {
  if (evento.target === dialogo) dialogo.close();
});
dialogo.addEventListener("close", () => ultimoBoton?.focus());
document.querySelector("#cantidad-street").textContent = modelos.filter(
  (modelo) => modelo.coleccion === "street",
).length;
document.querySelector("#cantidad-luxe").textContent = modelos.filter(
  (modelo) => modelo.coleccion === "luxe",
).length;
["casual", "hombre", "mujer", "unisex"].forEach((coleccion) => {
  document.querySelector(`#cantidad-${coleccion}`).textContent = modelos.filter(
    (modelo) => modelo.coleccion === coleccion,
  ).length;
});
document.querySelector("#cantidad-todos").textContent = modelos.length;
mostrarModelos();

// El catálogo complementa al escaparate y muestra las dos colecciones.
const catalogoGrid = document.querySelector("#catalogo-grid");
const buscarCatalogo = document.querySelector("#buscar-catalogo");
let coleccionCatalogo = "todos";
function mostrarCatalogo() {
  const consulta = buscarCatalogo.value.trim().toLocaleLowerCase("es");
  const visibles = modelos.filter(
    (modelo) =>
      (coleccionCatalogo === "todos" ||
        modelo.coleccion === coleccionCatalogo) &&
      modelo.nombre.toLocaleLowerCase("es").includes(consulta),
  );
  catalogoGrid.replaceChildren();
  visibles.forEach((modelo) => {
    const tarjeta = document.createElement("button");
    tarjeta.type = "button";
    // c-<colección>: los colores de Álvaro para cada colección (inicio.css)
    tarjeta.className = "catalogo-tarjeta c-" + modelo.coleccion;
    // Tienda (js/tienda.js): si el modelo está en PostgreSQL, su precio real
    // y si se puede comprar. Sin servidor, el precio orientativo y nada más.
    const enTienda =
      typeof datosEnTienda === "function" ? datosEnTienda(modelo) : null;
    const textoPrecio = formatoPrecio(
      enTienda?.precio ?? datosColeccion[modelo.coleccion].precio,
    );
    const textoEstado = enTienda?.estado ?? "";
    tarjeta.setAttribute(
      "aria-label",
      `Ver ${modelo.nombre}, ${textoPrecio}${textoEstado ? `, ${textoEstado.toLowerCase()}` : ""}`,
    );
    // Zona de la foto: el color de la colección y su etiqueta
    const foto = document.createElement("span");
    foto.className = "catalogo-foto";
    const etiqueta = document.createElement("span");
    etiqueta.className = "catalogo-etiqueta";
    etiqueta.textContent = modelo.coleccion;
    const imagen = document.createElement("img");
    imagen.src = modelo.imagen;
    imagen.alt = "";
    imagen.loading = "lazy";
    foto.append(etiqueta, imagen);
    // Banda de datos: nombre, precio, disponibilidad y «Ver modelo»
    const contenido = document.createElement("span");
    contenido.className = "catalogo-datos";
    const nombre = document.createElement("strong");
    nombre.textContent = modelo.nombre;
    const precio = document.createElement("span");
    precio.className = "catalogo-precio";
    precio.textContent = textoPrecio;
    const accion = document.createElement("span");
    accion.className = "catalogo-accion";
    accion.textContent = "Ver modelo ↗";
    contenido.append(nombre, accion, precio);
    if (textoEstado) {
      const estado = document.createElement("span");
      estado.className = `catalogo-estado ${enTienda.clase}`;
      estado.textContent = textoEstado;
      contenido.append(estado);
    }
    tarjeta.append(foto, contenido);
    tarjeta.addEventListener("click", () => abrirDetalle(modelo, tarjeta));
    catalogoGrid.append(tarjeta);
  });
  document.querySelector("#catalogo-resultados").textContent =
    `${visibles.length} ${visibles.length === 1 ? "modelo" : "modelos"}`;
  document.querySelector("#catalogo-vacio").hidden = visibles.length > 0;
}
document.querySelectorAll(".catalogo-filtro").forEach((boton) => {
  boton.addEventListener("click", () => {
    coleccionCatalogo = boton.dataset.coleccion;
    document.querySelectorAll(".catalogo-filtro").forEach((opcion) => {
      const activo = opcion === boton;
      opcion.classList.toggle("activo", activo);
      opcion.setAttribute("aria-pressed", String(activo));
    });
    mostrarCatalogo();
  });
});
buscarCatalogo.addEventListener("input", mostrarCatalogo);
mostrarCatalogo();

// En pantallas táctiles, al llegar al final de la estantería, un deslizamiento
// hacia arriba lleva al catálogo. Antes de llegar, el desplazamiento es normal.
const escaparate = document.querySelector("#catalogo");
const zonaDeslizamiento = document.querySelector(".escaparate-pie");
let inicioToque = null;
zonaDeslizamiento.addEventListener(
  "touchstart",
  (evento) => {
    if (
      evento.touches.length !== 1 ||
      evento.target.closest("button, input, a")
    )
      return;
    inicioToque = {
      x: evento.touches[0].clientX,
      y: evento.touches[0].clientY,
      cercaDelFinal:
        escaparate.getBoundingClientRect().bottom <= window.innerHeight + 80,
    };
  },
  { passive: true },
);
// Al reconocer el gesto, evitamos que la inercia salte por encima del catálogo.
zonaDeslizamiento.addEventListener(
  "touchmove",
  (evento) => {
    if (
      !inicioToque ||
      !inicioToque.cercaDelFinal ||
      evento.touches.length !== 1
    )
      return;
    const diferenciaY = inicioToque.y - evento.touches[0].clientY;
    const diferenciaX = Math.abs(inicioToque.x - evento.touches[0].clientX);
    if (diferenciaY > 10 && diferenciaY > diferenciaX * 1.5)
      evento.preventDefault();
  },
  { passive: false },
);
zonaDeslizamiento.addEventListener(
  "touchend",
  (evento) => {
    if (!inicioToque || evento.changedTouches.length !== 1) return;
    const diferenciaY = inicioToque.y - evento.changedTouches[0].clientY;
    const diferenciaX = Math.abs(
      inicioToque.x - evento.changedTouches[0].clientX,
    );
    if (
      inicioToque.cercaDelFinal &&
      diferenciaY > 65 &&
      diferenciaY > diferenciaX * 1.5
    ) {
      document.querySelector("#catalogo-completo").scrollIntoView();
    }
    inicioToque = null;
  },
  { passive: true },
);
zonaDeslizamiento.addEventListener("touchcancel", () => {
  inicioToque = null;
});

// Probador conceptual: la zapatilla elegida con una figura, puesta o sola.
const probador = document.querySelector("#probador");
const vistaProbador = document.querySelector(".probador-vista");
const elegirZapatilla = document.querySelector("#elegir-zapatilla");
const alturaModelo = document.querySelector("#altura-modelo");
const pesoModelo = document.querySelector("#peso-modelo");
const tipoModelo = document.querySelector("#tipo-modelo");
const imagenModelo = document.querySelector(".modelo-base");
const imagenEscena = document.querySelector("#escena-completa");
const zapatillaEscena = document.querySelector("#zapatilla-escena");
const avisoVista = document.querySelector("#aviso-sin-foto");

// Las tres figuras (con calzado genérico) valen para todas las zapatillas.
const figuras = {
  delgado: { imagen: "images/probador/modelo-delgado.png", texto: "delgada" },
  base: { imagen: "images/probador/modelo-base.png", texto: "media" },
  ancho: { imagen: "images/probador/modelo-ancho.png", texto: "amplia" },
};
// Fotos con una zapatilla concreta puesta. Qué modelo tiene cada una lo dice
// el campo «probador» de modelos.js (así no dependen del nombre).
const personasPuestas = {
  street01: "images/probador/modelo-street-01.png",
  "casual01-urbano": "images/probador/modelo-casual01-urbano.png",
  "casual01-deportivo": "images/probador/modelo-casual01-deportivo.png",
};
const escenasPuestas = {
  "casual02-escena": "images/probador/escena-casual-02.png",
  "casual03-escena": "images/probador/escena-casual-03.png",
};

// Las opciones salen de la misma lista que alimenta el catálogo.
modelos.forEach((modelo, indice) => {
  const opcion = document.createElement("option");
  opcion.value = indice;
  opcion.textContent = modelo.nombre;
  elegirZapatilla.append(opcion);
});
function mostrarZapatillaProbador(modelo) {
  document.querySelector("#probador-nombre").textContent = modelo.nombre;
  const imagen = document.querySelector("#probador-zapatilla");
  // Miniatura sobre fondo blanco: el recorte sin fondo encaja mejor que la foto cuadrada.
  imagen.src = modelo.imagen;
  imagen.alt = `Vista de ${modelo.nombre}`;
}
// Al abrir el probador o cambiar de zapatilla. Las vistas «puesta» solo se
// ofrecen con su zapatilla. Si se estaba viendo una figura, se mantiene (la
// misma complexión con otra zapatilla); si no, la primera foto puesta o, si no
// la hay, la zapatilla sola.
function prepararVistas() {
  const puestas = modeloSeleccionado.probador || [];
  tipoModelo.querySelectorAll("option[data-puesta]").forEach((opcion) => {
    const permitida = puestas.includes(opcion.value);
    opcion.disabled = !permitida;
    opcion.hidden = !permitida;
  });
  if (!figuras[tipoModelo.value]) tipoModelo.value = puestas[0] || "producto";
  tipoModelo.dispatchEvent(new Event("change"));
}
document.querySelector(".abrir-probador").addEventListener("click", () => {
  if (!modeloSeleccionado) return;
  elegirZapatilla.value = modelos.indexOf(modeloSeleccionado);
  mostrarZapatillaProbador(modeloSeleccionado);
  prepararVistas();
  dialogo.close();
  probador.showModal();
});
elegirZapatilla.addEventListener("change", () => {
  modeloSeleccionado = modelos[Number(elegirZapatilla.value)];
  mostrarZapatillaProbador(modeloSeleccionado);
  prepararVistas();
  document.querySelector("#detalle-titulo").textContent =
    modeloSeleccionado.nombre;
  document.querySelector("#detalle-coleccion").textContent =
    `COLECCIÓN ${modeloSeleccionado.coleccion.toUpperCase()}`;
  const imagen = document.querySelector("#detalle-imagen");
  imagen.src = modeloSeleccionado.imagen;
  imagen.alt = `Vista de ${modeloSeleccionado.nombre}`;
  mostrarDatosCompra(modeloSeleccionado);
});
// Se redondea a intervalos de 5 y se limita al rango visual disponible.
function redondearMedida(campo, minimo, maximo, valorInicial) {
  const valor = Number(campo.value);
  if (campo.value === "" || !Number.isFinite(valor)) {
    campo.value = valorInicial;
  } else {
    campo.value = Math.max(minimo, Math.min(maximo, Math.round(valor / 5) * 5));
  }
}
// La complexión aproximada sale del IMC (peso / estatura²): solo sirve para
// elegir una de las tres figuras, no para recomendar nada.
function figuraSegunMedidas() {
  const metros = Number(alturaModelo.value) / 100;
  const imc = Number(pesoModelo.value) / (metros * metros);
  if (imc < 20) return "delgado";
  if (imc < 27) return "base";
  return "ancho";
}
// Al cambiar la estatura o el peso se ve la figura que corresponde.
function mostrarFiguraSegunMedidas() {
  tipoModelo.value = figuraSegunMedidas();
  tipoModelo.dispatchEvent(new Event("change"));
}
alturaModelo.addEventListener("change", () => {
  redondearMedida(alturaModelo, 120, 220, 175);
  // Escala visual orientativa; no pretende reproducir proporciones reales.
  const alturaVisual = `${58 + (Number(alturaModelo.value) - 120) * 0.15}%`;
  imagenModelo.style.height = alturaVisual;
  vistaProbador.style.setProperty("--escala-modelo", alturaVisual);
  mostrarFiguraSegunMedidas();
});
pesoModelo.addEventListener("change", () => {
  redondearMedida(pesoModelo, 30, 200, 75);
  mostrarFiguraSegunMedidas();
});
tipoModelo.addEventListener("change", () => {
  const vista = tipoModelo.value;
  const figura = figuras[vista];
  const rutaPersona = figura ? figura.imagen : personasPuestas[vista];
  const rutaEscena = escenasPuestas[vista];
  // «producto»: la zapatilla elegida sola, en grande, sin ninguna persona.
  const soloZapatilla = vista === "producto";
  // La zapatilla elegida se ve sola o, con una figura, en una tarjeta a su lado.
  const verZapatilla = soloZapatilla || Boolean(figura);
  const nombre = modeloSeleccionado.nombre;
  imagenEscena.hidden = !rutaEscena;
  zapatillaEscena.hidden = !verZapatilla;
  vistaProbador.classList.toggle("escena-fija", Boolean(rutaEscena));
  vistaProbador.classList.toggle("solo-zapatilla", soloZapatilla);
  vistaProbador.classList.toggle("con-figura", Boolean(figura));
  document.querySelector("#aviso-escena").hidden = !rutaEscena;
  avisoVista.textContent = figura
    ? "Figura con calzado genérico · tu zapatilla, al lado"
    : "Aún no hay foto con este modelo puesto";
  avisoVista.hidden = !(
    figura ||
    (soloZapatilla && !modeloSeleccionado.probador)
  );
  probador.querySelectorAll(".escenarios button").forEach((boton) => {
    boton.disabled = Boolean(rutaEscena);
  });
  if (verZapatilla) {
    zapatillaEscena.src = modeloSeleccionado.imagen;
    zapatillaEscena.alt = figura
      ? `${nombre}, junto a la figura`
      : `${nombre} sobre el escenario`;
  }
  if (rutaEscena) {
    imagenEscena.src = rutaEscena;
    imagenEscena.alt = `Imagen generada con ${nombre} puesta`;
  }
  if (rutaPersona) {
    imagenModelo.src = rutaPersona;
    imagenModelo.alt = figura
      ? `Figura de complexión ${figura.texto}`
      : `Persona con ${nombre} puesta`;
  }
});
probador.querySelectorAll(".escenarios button").forEach((boton) => {
  boton.addEventListener("click", () => {
    vistaProbador.dataset.escenario = boton.dataset.escenario;
    probador.querySelectorAll(".escenarios button").forEach((opcion) => {
      opcion.setAttribute("aria-pressed", String(opcion === boton));
    });
  });
});
function cerrarProbador() {
  probador.close();
}
probador
  .querySelectorAll(".cerrar-probador, .cerrar-probador-secundario")
  .forEach((boton) => boton.addEventListener("click", cerrarProbador));
probador.addEventListener("click", (evento) => {
  if (evento.target === probador) cerrarProbador();
});
probador.addEventListener("close", () => {
  if (modeloSeleccionado && !dialogo.open) dialogo.showModal();
});

// ---------------------------------------------------------------------
// Bloque de Álvaro (commit 52a8800), copiado sin cambios salvo las dos
// últimas líneas: antes avisaban de que no había servidor; ahora llaman a
// iniciarSesionCliente (js/tienda.js).
// ---------------------------------------------------------------------
// Inicio de sesión (solo interfaz)
const dialogoAcceso = document.querySelector("#acceso");
const formularioAcceso = document.querySelector("#formulario-acceso");
const campoUsuarioAcceso = document.querySelector("#acceso-usuario");
const campoClaveAcceso = document.querySelector("#acceso-clave");
const botonVerClave = document.querySelector("#acceso-ver");
const errorAcceso = document.querySelector("#acceso-error");

function mostrarErrorAcceso(mensaje) {
  errorAcceso.textContent = mensaje;
  errorAcceso.hidden = false;
}

document.querySelector("#abrir-acceso").addEventListener("click", (evento) => {
  evento.preventDefault();
  errorAcceso.hidden = true;
  dialogoAcceso.showModal();
});

dialogoAcceso
  .querySelector(".cerrar-acceso")
  .addEventListener("click", () => dialogoAcceso.close());

dialogoAcceso.addEventListener("click", (evento) => {
  if (evento.target === dialogoAcceso) dialogoAcceso.close();
});

botonVerClave.addEventListener("click", () => {
  const oculta = campoClaveAcceso.type === "password";
  campoClaveAcceso.type = oculta ? "text" : "password";
  botonVerClave.textContent = oculta ? "Ocultar" : "Mostrar";
  botonVerClave.setAttribute("aria-pressed", oculta ? "true" : "false");
});

formularioAcceso.addEventListener("submit", (evento) => {
  evento.preventDefault();
  errorAcceso.hidden = true;

  if (campoUsuarioAcceso.value.trim() === "") {
    mostrarErrorAcceso("Escribe tu usuario o correo.");
    campoUsuarioAcceso.focus();
    return;
  }
  if (campoClaveAcceso.value === "") {
    mostrarErrorAcceso("Escribe tu contraseña.");
    campoClaveAcceso.focus();
    return;
  }

  // Tienda (js/tienda.js): el correo y la contraseña se comprueban en el servidor.
  iniciarSesionCliente(campoUsuarioAcceso.value.trim(), campoClaveAcceso.value);
});
