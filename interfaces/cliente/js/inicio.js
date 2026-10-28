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
    tarjeta.className = "catalogo-tarjeta";
    tarjeta.classList.add("c-" + modelo.coleccion);
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
    const imagen = document.createElement("img");
    imagen.src = modelo.imagen;
    imagen.alt = "";
    imagen.loading = "lazy";
    const contenido = document.createElement("span");
    contenido.className = "catalogo-datos";
    const nombre = document.createElement("strong");
    nombre.textContent = modelo.nombre;
    const precio = document.createElement("span");
    precio.className = "catalogo-precio";
    precio.textContent = textoPrecio;
    const accion = document.createElement("span");
    accion.textContent = "Ver modelo ↗";
    contenido.append(nombre, accion, precio);
    if (textoEstado) {
      const estado = document.createElement("span");
      estado.className = `catalogo-estado ${enTienda.clase}`;
      estado.textContent = textoEstado;
      contenido.append(estado);
    }
    tarjeta.append(imagen, contenido);
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

// Primera versión visual del probador: muestra el modelo y el producto por separado.
const probador = document.querySelector("#probador");
const vistaProbador = document.querySelector(".probador-vista");
const elegirZapatilla = document.querySelector("#elegir-zapatilla");
const alturaModelo = document.querySelector("#altura-modelo");
const pesoModelo = document.querySelector("#peso-modelo");
const tipoModelo = document.querySelector("#tipo-modelo");
const imagenModelo = document.querySelector(".modelo-base");
const opcionesUnisex = document.querySelector("#modelo-unisex");
let modeloUnisexPreferido = "hombre";

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
document.querySelector(".abrir-probador").addEventListener("click", () => {
  if (!modeloSeleccionado) return;
  elegirZapatilla.value = modelos.indexOf(modeloSeleccionado);
  mostrarZapatillaProbador(modeloSeleccionado);
  actualizarOpcionStreet();
  elegirVistaConZapatilla();
  dialogo.close();
  probador.showModal();
});
elegirZapatilla.addEventListener("change", () => {
  modeloSeleccionado = modelos[Number(elegirZapatilla.value)];
  mostrarZapatillaProbador(modeloSeleccionado);
  actualizarOpcionStreet();
  elegirVistaConZapatilla();
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
alturaModelo.addEventListener("change", () => {
  redondearMedida(alturaModelo, 120, 220, 175);
  // Escala visual orientativa; no pretende reproducir proporciones reales.
  const alturaVisual = `${58 + (Number(alturaModelo.value) - 120) * 0.15}%`;
  imagenModelo.style.height = alturaVisual;
  vistaProbador.style.setProperty("--escala-modelo", alturaVisual);
});
pesoModelo.addEventListener("change", () =>
  redondearMedida(pesoModelo, 30, 200, 75),
);
// Vistas en las que la persona lleva puesta una zapatilla concreta.
const fotosPuestas = {
  street01: "NOVA Street 01",
  "casual01-urbano": "NOVA Casual 01",
  "casual01-deportivo": "NOVA Casual 01",
  "casual02-escena": "NOVA Casual 02",
  "casual03-escena": "NOVA Casual 03",
};
// Cada imagen con zapatillas puestas solo se activa para el producto correcto. Las
// personas con calzado genérico no se ofrecen: mostrarían otras zapatillas.
function actualizarOpcionStreet() {
  const eleccionAnterior = tipoModelo.value;
  tipoModelo.querySelectorAll("option").forEach((opcion) => {
    const permitida =
      opcion.value === "producto" ||
      fotosPuestas[opcion.value] === modeloSeleccionado.nombre;
    opcion.disabled = !permitida;
    opcion.hidden = !permitida;
  });
  if (
    fotosPuestas[eleccionAnterior] &&
    fotosPuestas[eleccionAnterior] !== modeloSeleccionado.nombre
  ) {
    tipoModelo.value = "producto";
    tipoModelo.dispatchEvent(new Event("change"));
  }
}
function elegirVistaConZapatilla() {
  const vistas = {
    "NOVA Street 01": "street01",
    "NOVA Casual 01": "casual01-urbano",
    "NOVA Casual 02": "casual02-escena",
    "NOVA Casual 03": "casual03-escena",
  };
  // Solo aparece una persona si lleva puesta la zapatilla elegida. Si aún no hay foto
  // así, se muestra la zapatilla sola sobre el escenario y la pose queda desactivada.
  const vista = vistas[modeloSeleccionado.nombre];
  opcionesUnisex.hidden = true;
  tipoModelo.disabled = !vista;
  tipoModelo.value = vista || "producto";
  tipoModelo.dispatchEvent(new Event("change"));
}
// Elección de persona en los modelos unisex: queda sin uso mientras no haya fotos de
// personas con cada zapatilla unisex puesta.
// Los botones solo cambian la persona de la vista; no cambian la zapatilla.
function seleccionarModeloUnisex(tipo) {
  modeloUnisexPreferido = tipo;
  tipoModelo.value = tipo === "mujer" ? "persona02" : "persona01";
  tipoModelo.dispatchEvent(new Event("change"));
}
opcionesUnisex.querySelectorAll("button").forEach((boton) => {
  boton.addEventListener("click", () =>
    seleccionarModeloUnisex(boton.dataset.modeloUnisex),
  );
});
tipoModelo.addEventListener("change", () => {
  if (modeloSeleccionado && modeloSeleccionado.coleccion === "unisex") {
    const mujeres = ["persona02", "persona03"];
    const hombres = [
      "persona01",
      "persona04",
      "base",
      "delgado",
      "ancho",
      "urbano",
      "deportivo",
    ];
    let tipo = null;
    if (mujeres.includes(tipoModelo.value)) tipo = "mujer";
    if (hombres.includes(tipoModelo.value)) tipo = "hombre";
    if (tipo) modeloUnisexPreferido = tipo;
    opcionesUnisex.querySelectorAll("button").forEach((boton) => {
      boton.setAttribute(
        "aria-pressed",
        String(boton.dataset.modeloUnisex === tipo),
      );
    });
  }
  const imagenes = {
    persona01: "images/probador/persona-01.png",
    persona02: "images/probador/persona-02.png",
    persona03: "images/probador/persona-03.png",
    persona04: "images/probador/persona-04.png",
    base: "images/probador/modelo-base.png",
    delgado: "images/probador/modelo-delgado.png",
    ancho: "images/probador/modelo-ancho.png",
    urbano: "images/probador/modelo-urbano.png",
    deportivo: "images/probador/modelo-deportivo.png",
    street01: "images/probador/modelo-street-01.png",
    "casual01-urbano": "images/probador/modelo-casual01-urbano.png",
    "casual01-deportivo": "images/probador/modelo-casual01-deportivo.png",
  };
  const escenas = {
    "casual02-escena": "images/probador/escena-casual-02.png",
    "casual03-escena": "images/probador/escena-casual-03.png",
  };
  const rutaEscena = escenas[tipoModelo.value];
  // «producto»: la zapatilla elegida sola, en grande, sin ninguna persona.
  const soloZapatilla = tipoModelo.value === "producto";
  const imagenEscena = document.querySelector("#escena-completa");
  const zapatillaEscena = document.querySelector("#zapatilla-escena");
  imagenEscena.hidden = !rutaEscena;
  zapatillaEscena.hidden = !soloZapatilla;
  vistaProbador.classList.toggle("escena-fija", Boolean(rutaEscena));
  vistaProbador.classList.toggle("solo-zapatilla", soloZapatilla);
  document.querySelector("#aviso-escena").hidden = !rutaEscena;
  document.querySelector("#aviso-sin-foto").hidden =
    !soloZapatilla ||
    Object.values(fotosPuestas).includes(modeloSeleccionado.nombre);
  alturaModelo.disabled = Boolean(rutaEscena) || soloZapatilla;
  probador.querySelectorAll(".escenarios button").forEach((boton) => {
    boton.disabled = Boolean(rutaEscena);
  });
  if (soloZapatilla) {
    zapatillaEscena.src = modeloSeleccionado.imagen;
    zapatillaEscena.alt = `${modeloSeleccionado.nombre} sobre el escenario`;
  } else if (rutaEscena) {
    imagenEscena.src = rutaEscena;
    imagenEscena.alt = `Imagen generada con ${modeloSeleccionado.nombre} puesta`;
  } else {
    imagenModelo.src = imagenes[tipoModelo.value];
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
