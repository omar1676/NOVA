// Dibuja los iconos de Lucide (si la CDN no carga, el panel sigue funcionando sin iconos)
if (window.lucide) {
  lucide.createIcons();
}

// Elementos del buscador y del filtro (solo existen en las páginas con tabla)
const buscador = document.getElementById("adm-buscador");
const filtroEstado = document.getElementById("adm-filtro-estado");

// Qué página es: lo dice <body data-pagina="..."> (solo en las páginas con datos reales)
const pagina = document.body.dataset.pagina;

// Si el navegador enseña la página desde su memoria (botón Atrás), se vuelve a
// pedir al servidor. Así, después de cerrar sesión no quedan datos a la vista.
window.addEventListener("pageshow", function (evento) {
  if (evento.persisted) window.location.reload();
});

// ===== Conexión con el servidor del panel (servidor-admin) =====
// Todos los datos llegan de la API. Si no hay sesión (401) o el usuario no es
// administrador (403), se vuelve a la página de login.
async function pedirApi(ruta) {
  const respuesta = await fetch(ruta);
  if (respuesta.status === 401 || respuesta.status === 403) {
    window.location.href = "login.html";
    throw new Error("sin sesión de administrador");
  }
  if (!respuesta.ok) {
    throw new Error("el servidor respondió " + respuesta.status);
  }
  return respuesta.json();
}

function euros(valor) {
  return Number(valor).toLocaleString("es-ES", { style: "currency", currency: "EUR" });
}

// ===== Cerrar sesión =====
const botonSalir = document.getElementById("adm-salir");
if (botonSalir) {
  botonSalir.addEventListener("click", async function (evento) {
    evento.preventDefault();
    await fetch("/api/logout", { method: "POST" }).catch(function () {});
    window.location.href = "login.html";
  });
}

// ===== Tablas con datos reales =====
// Qué ruta pide cada página, qué filtro usa el desplegable y qué columnas
// pinta, en el mismo orden que el <thead> del HTML.
//   tipo "estado": la etiqueta de color (adm-estado)
//   tipo "euros":  importe con formato 1.234,50 €
const TABLAS = {
  pedidos: {
    ruta: "/api/admin/pedidos",
    filtro: "estado",
    columnas: [
      { campo: "referencia" }, { campo: "cliente" }, { campo: "fecha" },
      { campo: "estado", tipo: "estado" }, { campo: "total", tipo: "euros" }
    ]
  },
  productos: {
    ruta: "/api/admin/productos",
    filtro: "estado",
    columnas: [
      { campo: "modelo" }, { campo: "color" }, { campo: "talla" }, { campo: "sku" },
      { campo: "precio", tipo: "euros" }, { campo: "estado", tipo: "estado" }
    ]
  },
  inventario: {
    ruta: "/api/admin/inventario",
    filtro: "estado",
    columnas: [
      { campo: "nave" }, { campo: "modelo" }, { campo: "color" }, { campo: "talla" },
      { campo: "sku" }, { campo: "stock" }, { campo: "estado", tipo: "estado" }
    ]
  },
  clientes: {
    ruta: "/api/admin/clientes",
    filtro: "estado",
    columnas: [
      { campo: "nombre" }, { campo: "tipo" }, { campo: "correo" },
      { campo: "telefono" }, { campo: "estado", tipo: "estado" }
    ]
  },
  trabajadores: {
    ruta: "/api/admin/trabajadores",
    filtro: "estado",
    columnas: [
      { campo: "nombre" }, { campo: "usuario" }, { campo: "puesto" },
      { campo: "rol" }, { campo: "estado", tipo: "estado" }
    ]
  },
  auditoria: {
    ruta: "/api/admin/auditoria",
    filtro: "accion",
    columnas: [
      { campo: "fecha" }, { campo: "usuario" }, { campo: "accion", tipo: "estado" },
      { campo: "tabla" }, { campo: "registro" }, { campo: "detalle" }
    ]
  }
};

// Las acciones reales de la auditoría (08_auditoria.sql) con los colores del prototipo
const COLOR_ACCION = {
  ALTA: "crear",
  CAMBIO_ESTADO: "modificar",
  CAMBIO_STOCK: "modificar",
  BAJA_LOGICA: "eliminar"
};

// Una fila de aviso que ocupa toda la tabla ("Cargando...", "No hay resultados"...)
function mensajeEnTabla(cuerpo, texto, columnas) {
  const fila = document.createElement("tr");
  const celda = document.createElement("td");
  celda.colSpan = columnas;
  celda.className = "adm-vacio";
  celda.textContent = texto;
  fila.appendChild(celda);
  cuerpo.replaceChildren(fila);
}

// Pinta las filas en un <tbody>. Se usa textContent y no innerHTML: si un
// dato llevara "<script>", se vería como texto y no se ejecutaría.
function pintarFilas(cuerpo, filas, columnas) {
  if (filas.length === 0) {
    mensajeEnTabla(cuerpo, "No hay resultados", columnas.length);
    return;
  }

  cuerpo.replaceChildren();
  filas.forEach(function (datos) {
    const fila = document.createElement("tr");

    columnas.forEach(function (columna) {
      const celda = document.createElement("td");
      const valor = datos[columna.campo];

      if (columna.tipo === "estado") {
        const etiqueta = document.createElement("span");
        const color = COLOR_ACCION[valor] || String(valor).replace(/ /g, "-");
        etiqueta.className = "adm-estado adm-" + color;
        etiqueta.textContent = valor;
        celda.appendChild(etiqueta);
      } else if (columna.tipo === "euros") {
        celda.textContent = euros(valor);
      } else {
        celda.textContent = (valor === null || valor === "") ? "—" : valor;
      }

      fila.appendChild(celda);
    });

    cuerpo.appendChild(fila);
  });
}

// Pide al servidor solo las filas que cumplen el buscador y el desplegable.
// El filtro lo hace PostgreSQL con una consulta parametrizada.
let ultimaPeticion = 0;

async function cargarTabla(tabla) {
  const cuerpo = document.querySelector(".adm-tabla tbody");
  const parametros = new URLSearchParams();
  if (buscador.value.trim() !== "") parametros.set("texto", buscador.value.trim());
  if (filtroEstado.value !== "") parametros.set(tabla.filtro, filtroEstado.value);

  // Si se escribe deprisa salen varias peticiones: solo se pinta la última
  const numero = ++ultimaPeticion;
  try {
    const datos = await pedirApi(tabla.ruta + "?" + parametros.toString());
    if (numero === ultimaPeticion) pintarFilas(cuerpo, datos.filas, tabla.columnas);
  } catch (error) {
    if (numero === ultimaPeticion) {
      mensajeEnTabla(cuerpo, "No se han podido cargar los datos: " + error.message, tabla.columnas.length);
    }
  }
}

// Prototipos (Sugerencias): muestra u oculta las filas de ejemplo según el
// texto y el estado elegidos, sin pedir nada al servidor
function filtrarTabla() {
  const texto = buscador.value.toLowerCase();
  const estado = filtroEstado.value;
  const filas = document.querySelectorAll(".adm-tabla tbody tr");

  filas.forEach(function (fila) {
    const contenido = fila.textContent.toLowerCase();
    const estadoFila = fila.querySelector(".adm-estado").textContent;

    const coincideTexto = contenido.includes(texto);
    const coincideEstado = estado === "" || estadoFila === estado;

    fila.style.display = (coincideTexto && coincideEstado) ? "" : "none";
  });
}

// Solo activa el filtro si la página tiene buscador (el dashboard no)
if (buscador && filtroEstado) {
  const tabla = TABLAS[pagina];

  if (tabla) {
    // Página conectada: al escribir se espera un momento antes de preguntar
    let espera;
    buscador.addEventListener("input", function () {
      clearTimeout(espera);
      espera = setTimeout(function () { cargarTabla(tabla); }, 300);
    });
    filtroEstado.addEventListener("change", function () { cargarTabla(tabla); });
    cargarTabla(tabla);
  } else {
    buscador.addEventListener("input", filtrarTabla);
    filtroEstado.addEventListener("change", filtrarTabla);
  }
}

// ===== Listas del dashboard y de estadísticas =====
const ESTADOS_PEDIDO = ["pendiente", "confirmado", "en_preparacion", "enviado", "entregado", "cancelado"];

// Una fila de lista con dos textos: "pendiente ........ 11"
function filaDeLista(izquierda, derecha) {
  const fila = document.createElement("div");
  const nombre = document.createElement("span");
  const valor = document.createElement("span");
  nombre.textContent = izquierda;
  valor.textContent = derecha;
  fila.append(nombre, valor);
  return fila;
}

function textoVacio(texto) {
  const parrafo = document.createElement("p");
  parrafo.className = "adm-vacio";
  parrafo.textContent = texto;
  return parrafo;
}

// Los seis estados, aunque alguno tenga 0 pedidos
function pintarEstados(lista, filas) {
  lista.replaceChildren();
  ESTADOS_PEDIDO.forEach(function (estado) {
    const fila = filas.find(function (f) { return f.estado === estado; });
    lista.appendChild(filaDeLista(estado, fila ? fila.pedidos : 0));
  });
}

function pintarStockBajo(lista, filas, umbral) {
  lista.replaceChildren();
  if (filas.length === 0) {
    lista.appendChild(textoVacio("Ninguna referencia tiene menos de " + umbral + " unidades"));
    return;
  }
  filas.forEach(function (f) {
    lista.appendChild(filaDeLista(f.modelo + " · " + f.color + " · " + f.talla, f.stock + " uds."));
  });
}

function pintarMasVendidos(lista, filas) {
  lista.replaceChildren();
  if (filas.length === 0) {
    lista.appendChild(textoVacio("Todavía no hay ventas"));
    return;
  }

  const maximo = Math.max.apply(null, filas.map(function (f) { return f.pares; }));
  filas.forEach(function (f) {
    const fila = document.createElement("div");
    fila.className = "adm-barra-fila";

    const nombre = document.createElement("span");
    nombre.className = "adm-barra-nombre";
    nombre.textContent = f.modelo;

    const pista = document.createElement("span");
    pista.className = "adm-barra-pista";
    const relleno = document.createElement("span");
    relleno.className = "adm-barra-relleno";
    relleno.style.width = (f.pares / maximo * 100) + "%";
    pista.appendChild(relleno);

    const valor = document.createElement("span");
    valor.className = "adm-barra-valor";
    valor.textContent = f.pares;
    valor.title = f.pares + " pares en " + f.pedidos + " pedidos";

    fila.append(nombre, pista, valor);
    lista.appendChild(fila);
  });
}

//Dashboard
function pintarDashboard(datos) {
  document.getElementById("adm-ventas").textContent = euros(datos.ventas);
  document.getElementById("adm-pedidos-hoy").textContent = datos.pedidosHoy;
  document.getElementById("adm-pedidos-pendientes").textContent = datos.pedidosPendientes;

  // Todavía no existe la tabla de sugerencias en PostgreSQL
  const sugerencias = document.getElementById("adm-sugerencias-pendientes");
  if (datos.sugerenciasPendientes === null) {
    sugerencias.textContent = "No disponible";
    sugerencias.classList.add("adm-no-disponible");
    sugerencias.title = "Las sugerencias todavía no están en la base de datos";
  } else {
    sugerencias.textContent = datos.sugerenciasPendientes;
  }

  pintarFilas(document.getElementById("adm-ultimos"), datos.ultimosPedidos, TABLAS.pedidos.columnas);
  pintarEstados(document.getElementById("adm-estados"), datos.pedidosPorEstado);
  pintarStockBajo(document.getElementById("adm-stock-bajo"), datos.stockBajo, datos.umbralStockBajo);

  dibujarGrafico("ventas", "bar",
    datos.ventasDia.map(function (d) { return d.dia; }),
    datos.ventasDia.map(function (d) { return d.total; }));
}
if (pagina === "dashboard") {
  pedirApi("/api/admin/dashboard")
    .then(pintarDashboard)
    .catch(function (error) {
      mensajeEnTabla(document.getElementById("adm-ultimos"), "No se han podido cargar los datos: " + error.message, 5);
    });
}

// ===== Estadísticas =====
function pintarEstadisticas(datos) {
  document.getElementById("adm-est-ingresos").textContent = euros(datos.ingresosMes);
  document.getElementById("adm-est-pedidos").textContent = datos.pedidosMes;
  document.getElementById("adm-est-ticket").textContent = euros(datos.ticketMedio);
  document.getElementById("adm-est-pares").textContent = datos.paresMes;

  dibujarGrafico("ventas", "bar",
    datos.ventasDia.map(function (d) { return d.dia; }),
    datos.ventasDia.map(function (d) { return d.total; }));
  dibujarGrafico("ingresos", "line",
    datos.ingresosPorMes.map(function (m) { return m.mes; }),
    datos.ingresosPorMes.map(function (m) { return m.total; }));

  pintarEstados(document.getElementById("adm-estados"), datos.pedidosPorEstado);
  pintarMasVendidos(document.getElementById("adm-productos-lista"), datos.masVendidos);
}
if (pagina === "estadisticas") {
  pedirApi("/api/admin/estadisticas")
    .then(pintarEstadisticas)
    .catch(function (error) {
      const lista = document.getElementById("adm-productos-lista");
      lista.replaceChildren(textoVacio("No se han podido cargar los datos: " + error.message));
    });
}

// ===== Configuración =====
const botonGuardar = document.getElementById("adm-guardar");
const avisoGuardar = document.getElementById("adm-aviso-guardar");

if (botonGuardar && avisoGuardar) {
  botonGuardar.addEventListener("click", function () {
    avisoGuardar.textContent = "Prototipo: estos ajustes todavía no se guardan en la base de datos.";
  });
}

// ===== Gráficos =====
const colorTexto = "#8d8d95";
const colorLinea = "#2a2a2e";
const colorDorado = "#c9a24b";

function opcionesGrafico() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { labels: { color: colorTexto } } },
    scales: {
      x: { ticks: { color: colorTexto }, grid: { color: colorLinea } },
      y: { ticks: { color: colorTexto }, grid: { color: colorLinea }, beginAtZero: true }
    }
  };
}

function dibujarGrafico(nombre, tipo, etiquetas, valores) {
  const vacio = document.getElementById("adm-" + nombre + "-vacio");
  const caja = document.getElementById("adm-" + nombre + "-caja");
  const lienzo = document.getElementById("adm-" + nombre + "-canvas");
  if (!lienzo) return;

  if (!valores || valores.length === 0) {
    if (vacio) vacio.style.display = "block";
    if (caja) caja.style.display = "none";
    return;
  }

  // Si la CDN de Chart.js no ha cargado, se avisa en lugar de romper la página
  if (typeof Chart === "undefined") {
    if (vacio) vacio.textContent = "No se ha podido cargar la librería de gráficos";
    return;
  }

  if (vacio) vacio.style.display = "none";
  if (caja) caja.style.display = "block";

  const existente = Chart.getChart(lienzo);
  if (existente) existente.destroy();

  new Chart(lienzo, {
    type: tipo,
    data: {
      labels: etiquetas,
      datasets: [{
        label: "Importe (€)",
        data: valores,
        backgroundColor: colorDorado,
        borderColor: colorDorado,
        tension: 0.3
      }]
    },
    options: opcionesGrafico()
  });
}
