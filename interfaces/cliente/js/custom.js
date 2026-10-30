// Formulario Custom: suma los pares por talla y simula el envío.
// No hay servidor: no se envía ni se guarda ningún dato.
const formularioCustom = document.querySelector("#form-custom");
const camposTalla = document.querySelectorAll(".custom-tallas input");
const totalPares = document.querySelector("#custom-total");
const resultadoCustom = document.querySelector("#custom-resultado");

// Sugerencias para el campo Modelo: los nombres del catálogo (modelos.js).
const listaModelos = document.querySelector("#custom-modelos");
modelos.forEach((modelo) => {
  const opcion = document.createElement("option");
  opcion.value = modelo.nombre;
  listaModelos.append(opcion);
});

// Suma los pares de todas las tallas. Un campo vacío no cuenta.
function contarPares() {
  let total = 0;
  camposTalla.forEach((campo) => {
    const pares = Number(campo.value);
    if (pares > 0) total += pares;
  });
  totalPares.textContent = total;
  return total;
}

formularioCustom.addEventListener("input", contarPares);

// Antes de este evento, el navegador ya ha comprobado los campos obligatorios,
// el formato del email y que las cantidades sean números enteros positivos.
formularioCustom.addEventListener("submit", (evento) => {
  evento.preventDefault(); // no hay servidor: el formulario no se envía
  const total = contarPares();
  if (total === 0) {
    resultadoCustom.textContent =
      "Indica cuántos pares quieres de al menos una talla.";
    camposTalla[0].focus();
    return;
  }
  const tallas = [];
  camposTalla.forEach((campo) => {
    if (Number(campo.value) > 0) {
      tallas.push(`${campo.dataset.talla}: ${campo.value}`);
    }
  });
  const club = formularioCustom.elements.club.value;
  const modelo = formularioCustom.elements.modelo.value;
  resultadoCustom.textContent =
    `SIMULACIÓN · Solicitud preparada para ${club}: ${modelo}, ${total} pares ` +
    `(tallas ${tallas.join(", ")}). No se ha enviado ningún dato ni se ha ` +
    "registrado ningún pedido.";
});
