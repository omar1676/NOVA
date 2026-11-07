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

// ===== Configuración =====
const botonGuardar = document.getElementById("adm-guardar");
const avisoGuardar = document.getElementById("adm-aviso-guardar");

if (botonGuardar && avisoGuardar) {
  botonGuardar.addEventListener("click", function () {
    avisoGuardar.textContent = "Todavía no hay servidor: los cambios no se guardan.";
  });
}

