lucide.createIcons();

const buscador = document.getElementById("adm-buscador");
const filtroEstado = document.getElementById("adm-filtro-estado");

const siguienteEstado = {
  confirmado: "en_preparacion",
  en_preparacion: "enviado",
  enviado: "entregado"
};

function filtrarTabla() {
  const texto = buscador.value.toLowerCase();
  const estado = filtroEstado ? filtroEstado.value : "";
  const filas = document.querySelectorAll(".adm-tabla tbody tr");

  filas.forEach(function (fila) {
    if (fila.querySelector(".adm-vacio")) {
      return;
    }

    const contenido = fila.textContent.toLowerCase();
    const etiqueta = fila.querySelector(".adm-estado");
    const estadoFila = etiqueta ? etiqueta.textContent : "";

    const coincideTexto = contenido.includes(texto);
    const coincideEstado = estado === "" || estadoFila === estado;

    fila.style.display = (coincideTexto && coincideEstado) ? "" : "none";
  });
}

if (buscador) {
  buscador.addEventListener("input", filtrarTabla);
}

if (filtroEstado) {
  filtroEstado.addEventListener("change", filtrarTabla);
}

function crearCelda(texto) {
  const celda = document.createElement("td");
  celda.textContent = texto === null || texto === undefined || texto === "" ? "—" : texto;
  return celda;
}

function crearCeldaEstado(estado) {
  const celda = document.createElement("td");
  const etiqueta = document.createElement("span");
  etiqueta.className = "adm-estado adm-" + estado;
  etiqueta.textContent = estado;
  celda.appendChild(etiqueta);
  return celda;
}

function formatearFecha(fecha) {
  if (!fecha) {
    return "—";
  }
  return new Date(fecha).toLocaleDateString("es-ES");
}

function formatearDinero(importe) {
  return Number(importe).toLocaleString("es-ES", { style: "currency", currency: "EUR" });
}

function pintarFilaVacia(cuerpo, columnas, mensaje) {
  cuerpo.innerHTML = "";
  const fila = document.createElement("tr");
  const celda = document.createElement("td");
  celda.colSpan = columnas;
  celda.className = "adm-vacio";
  celda.textContent = mensaje;
  fila.appendChild(celda);
  cuerpo.appendChild(fila);
}

async function pedirDatos(url, opciones) {
  const respuesta = await fetch(url, opciones);
  const datos = await respuesta.json();
  if (!respuesta.ok) {
    throw new Error(datos.error || "Error del servidor");
  }
  return datos;
}

function enviarCambio(url, metodo, cuerpo) {
  return pedirDatos(url, {
    method: metodo,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(cuerpo)
  });
}

const cuerpoPedidos = document.getElementById("adm-pedidos");

async function cargarPedidos() {
  try {
    const pedidos = await pedirDatos("/api/trabajador/pedidos");

    if (pedidos.length === 0) {
      pintarFilaVacia(cuerpoPedidos, 7, "Todavía no hay datos");
      return;
    }

    cuerpoPedidos.innerHTML = "";

    pedidos.forEach(function (pedido) {
      const fila = document.createElement("tr");
      fila.appendChild(crearCelda(pedido.referencia));
      fila.appendChild(crearCelda(pedido.cliente));
      fila.appendChild(crearCelda(formatearFecha(pedido.fecha_pedido)));
      fila.appendChild(crearCelda(formatearFecha(pedido.fecha_objetivo)));
      fila.appendChild(crearCeldaEstado(pedido.estado));
      fila.appendChild(crearCelda(formatearDinero(pedido.importe_total)));

      const celdaAccion = document.createElement("td");
      if (siguienteEstado[pedido.estado]) {
        const boton = document.createElement("button");
        boton.className = "adm-boton";
        boton.textContent = "Avanzar estado";
        boton.addEventListener("click", function () {
          avanzarEstado(pedido.id_pedido, siguienteEstado[pedido.estado]);
        });
        celdaAccion.appendChild(boton);
      } else {
        celdaAccion.textContent = "—";
      }
      fila.appendChild(celdaAccion);

      cuerpoPedidos.appendChild(fila);
    });

    filtrarTabla();
  } catch (error) {
    pintarFilaVacia(cuerpoPedidos, 7, "No se han podido cargar los pedidos");
  }
}

async function avanzarEstado(idPedido, estadoNuevo) {
  try {
    await enviarCambio("/api/trabajador/pedidos/" + idPedido + "/estado", "PATCH", { estado: estadoNuevo });
    await cargarPedidos();
  } catch (error) {
    alert(error.message);
  }
}

if (cuerpoPedidos) {
  cargarPedidos();
}

const cuerpoInventario = document.getElementById("adm-inventario");

function calcularEstadoStock(cantidad) {
  if (cantidad === 0) {
    return "agotado";
  }
  if (cantidad < 5) {
    return "bajo";
  }
  return "suficiente";
}

async function cargarInventario() {
  try {
    const existencias = await pedirDatos("/api/trabajador/inventario");

    if (existencias.length === 0) {
      pintarFilaVacia(cuerpoInventario, 7, "Todavía no hay datos");
      return;
    }

    cuerpoInventario.innerHTML = "";

    existencias.forEach(function (existencia) {
      const fila = document.createElement("tr");
      fila.appendChild(crearCelda(existencia.nave));
      fila.appendChild(crearCelda(existencia.modelo));
      fila.appendChild(crearCelda(existencia.color));
      fila.appendChild(crearCelda(existencia.talla));
      fila.appendChild(crearCelda(existencia.sku));
      fila.appendChild(crearCeldaEstado(calcularEstadoStock(existencia.cantidad)));

      const celdaCantidad = document.createElement("td");
      const campo = document.createElement("input");
      campo.type = "number";
      campo.min = "0";
      campo.value = existencia.cantidad;
      campo.style.width = "70px";

      const boton = document.createElement("button");
      boton.className = "adm-boton";
      boton.textContent = "Guardar";
      boton.addEventListener("click", function () {
        guardarCantidad(existencia.id_producto_sku, existencia.id_nave, campo.value);
      });

      celdaCantidad.appendChild(campo);
      celdaCantidad.appendChild(boton);
      fila.appendChild(celdaCantidad);

      cuerpoInventario.appendChild(fila);
    });

    filtrarTabla();
  } catch (error) {
    pintarFilaVacia(cuerpoInventario, 7, "No se ha podido cargar el inventario");
  }
}

async function guardarCantidad(idSku, idNave, valor) {
  const cantidad = Number(valor);

  if (valor === "" || !Number.isInteger(cantidad) || cantidad < 0) {
    alert("La cantidad debe ser un número entero igual o mayor que 0");
    return;
  }

  try {
    await enviarCambio("/api/trabajador/inventario/" + idSku + "/" + idNave, "PATCH", { cantidad: cantidad });
    await cargarInventario();
  } catch (error) {
    alert(error.message);
  }
}

if (cuerpoInventario) {
  cargarInventario();
}

const cuerpoPersonalizados = document.getElementById("adm-personalizados");
const cuerpoXnova = document.getElementById("adm-xnova");

async function cargarPersonalizados() {
  try {
    const datos = await pedirDatos("/api/trabajador/personalizados");

    if (datos.pedidos.length === 0) {
      pintarFilaVacia(cuerpoPersonalizados, 6, "Todavía no hay datos");
    } else {
      cuerpoPersonalizados.innerHTML = "";
      datos.pedidos.forEach(function (pedido) {
        const fila = document.createElement("tr");
        fila.appendChild(crearCelda(pedido.referencia));
        fila.appendChild(crearCelda(pedido.cliente));
        fila.appendChild(crearCelda(formatearFecha(pedido.fecha_objetivo)));
        fila.appendChild(crearCeldaEstado(pedido.estado));
        fila.appendChild(crearCelda(pedido.cantidad_total));
        fila.appendChild(crearCelda(pedido.personalizacion));
        cuerpoPersonalizados.appendChild(fila);
      });
    }

    if (datos.configuraciones.length === 0) {
      pintarFilaVacia(cuerpoXnova, 9, "Todavía no hay datos");
    } else {
      cuerpoXnova.innerHTML = "";
      datos.configuraciones.forEach(function (configuracion) {
        const fila = document.createElement("tr");
        fila.appendChild(crearCelda(configuracion.cliente));
        fila.appendChild(crearCelda(configuracion.referencia));
        fila.appendChild(crearCelda(configuracion.talla_referencia));
        fila.appendChild(crearCelda(configuracion.color_principal));
        fila.appendChild(crearCelda(configuracion.color_secundario));
        fila.appendChild(crearCelda(configuracion.material));
        fila.appendChild(crearCelda(configuracion.tipo_suela));
        fila.appendChild(crearCelda(configuracion.texto_personalizado));
        fila.appendChild(crearCelda(formatearFecha(configuracion.fecha_creacion)));
        cuerpoXnova.appendChild(fila);
      });
    }

    filtrarTabla();
  } catch (error) {
    pintarFilaVacia(cuerpoPersonalizados, 6, "No se han podido cargar los datos");
    pintarFilaVacia(cuerpoXnova, 9, "No se han podido cargar los datos");
  }
}

if (cuerpoPersonalizados && cuerpoXnova) {
  cargarPersonalizados();
}

const tarjetaPorPreparar = document.getElementById("adm-por-preparar");

async function cargarResumen() {
  try {
    const resumen = await pedirDatos("/api/trabajador/resumen");
    document.getElementById("adm-por-preparar").textContent = resumen.porPreparar;
    document.getElementById("adm-en-preparacion").textContent = resumen.enPreparacion;
    document.getElementById("adm-stock-bajo").textContent = resumen.stockBajo;
    document.getElementById("adm-pedidos-hoy").textContent = resumen.pedidosHoy;
  } catch (error) {
    document.getElementById("adm-aviso").textContent = "No se ha podido cargar el resumen";
  }
}

if (tarjetaPorPreparar) {
  cargarResumen();
}
