lucide.createIcons();

const buscador = document.getElementById("buscador");
const filtroEstado = document.getElementById("filtro-estado");

function filtrarPedidos() {
  const texto = buscador.value.toLowerCase();
  const estado = filtroEstado.value;
  const filas = document.querySelectorAll("tbody tr");

  filas.forEach(function (fila) {
    const contenido = fila.textContent.toLowerCase();
    const estadoFila = fila.querySelector(".estado").textContent;

    const coincideTexto = contenido.includes(texto);
    const coincideEstado = estado === "" || estadoFila === estado;

    fila.style.display = (coincideTexto && coincideEstado) ? "" : "none";
  });
}

if (buscador && filtroEstado) {
  buscador.addEventListener("input", filtrarPedidos);
  filtroEstado.addEventListener("change", filtrarPedidos);
}