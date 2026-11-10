// Dibuja los iconos de Lucide
lucide.createIcons();

// Elementos del buscador y del filtro (solo existen en las páginas con tabla)
const buscador = document.getElementById("adm-buscador");
const filtroEstado = document.getElementById("adm-filtro-estado");

// Muestra u oculta cada fila según el texto y el estado elegidos
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
  buscador.addEventListener("input", filtrarTabla);
  filtroEstado.addEventListener("change", filtrarTabla);
}
//Dashboard 
function pintarDashboard(datos) {
  document.getElementById("adm-ventas").textContent = datos.ventas + " €";
  document.getElementById("adm-pedidos-hoy").textContent = datos.pedidosHoy;
  document.getElementById("adm-pedidos-pendientes").textContent = datos.pedidosPendientes;
  document.getElementById("adm-sugerencias-pendientes").textContent = datos.sugerenciasPendientes;

  dibujarGrafico("ventas", "bar",
    datos.ventasDia.map(function (d) { return d.dia; }),
    datos.ventasDia.map(function (d) { return d.total; }));
}
if (document.getElementById("adm-pedidos-hoy")) {
  fetch("/api/admin/dashboard")
    .then(function (r) { return r.json(); })
    .then(pintarDashboard)
    .catch(function () {});
}

// ===== Configuración =====
const botonGuardar = document.getElementById("adm-guardar");
const avisoGuardar = document.getElementById("adm-aviso-guardar");

if (botonGuardar && avisoGuardar) {
  botonGuardar.addEventListener("click", function () {
    avisoGuardar.textContent = "Todavía no hay servidor: los cambios no se guardan.";
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

  if (vacio) vacio.style.display = "none";
  if (caja) caja.style.display = "block";

  const existente = Chart.getChart(lienzo);
  if (existente) existente.destroy();

  new Chart(lienzo, {
    type: tipo,
    data: {
      labels: etiquetas,
      datasets: [{
        data: valores,
        backgroundColor: colorDorado,
        borderColor: colorDorado,
        tension: 0.3
      }]
    },
    options: opcionesGrafico()
  });
}

