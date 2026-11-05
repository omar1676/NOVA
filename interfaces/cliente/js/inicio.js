// Datos visuales provisionales: cada objeto representa una zapatilla.
const modelos = [
  { nombre: "NOVA 01", tono: "Arena", color: "#ddd0bb", detalle: "#a79881" },
  { nombre: "NOVA 02", tono: "Carbón", color: "#343a3c", detalle: "#77817d" },
  { nombre: "NOVA 03", tono: "Oliva", color: "#66705c", detalle: "#afb3a0" },
  { nombre: "NOVA 04", tono: "Hueso", color: "#e2ded1", detalle: "#b6ac99" },
  { nombre: "NOVA 05", tono: "Arcilla", color: "#a97964", detalle: "#dfbda4" },
  { nombre: "NOVA 06", tono: "Marino", color: "#4e5e69", detalle: "#aab3b2" },
  { nombre: "NOVA 07", tono: "Piedra", color: "#a7a7a0", detalle: "#d4d0c5" },
  { nombre: "NOVA 08", tono: "Negro", color: "#333333", detalle: "#a08962" }
];

// Dibujo original y simplificado: los colores cambian para cada modelo.
function dibujarZapatilla(modelo) {
  return `
    <svg viewBox="0 0 280 125" role="img" aria-label="Ilustración de ${modelo.nombre}, color ${modelo.tono}">
      <path d="M24 85 C39 80 51 72 62 58 L83 30 Q90 23 97 28 L113 48 Q120 57 139 62 L179 70 Q193 73 218 77 L249 82 Q262 84 263 95 L263 101 L23 101 Q17 99 18 93 Q19 88 24 85 Z" fill="${modelo.color}" stroke="#363b38" stroke-width="2" stroke-linejoin="round"/>
      <path d="M63 58 Q78 66 91 71 L113 49 M126 61 L112 79 M163 68 L151 85" fill="none" stroke="${modelo.detalle}" stroke-width="5" stroke-linecap="round"/>
      <path d="M99 40 L120 46 M103 48 L126 54 M108 56 L132 62" fill="none" stroke="#f2eee4" stroke-width="3" stroke-linecap="round"/>
      <path d="M20 94 Q75 99 135 97 L262 95 L263 103 Q263 111 253 112 L34 112 Q20 111 19 103 Z" fill="#e5e0d5" stroke="#444844" stroke-width="2"/>
      <path d="M31 106 L247 106" stroke="#aaa69d" stroke-width="2"/>
      <path d="M194 79 Q211 81 224 84" stroke="${modelo.detalle}" stroke-width="4" stroke-linecap="round"/>
    </svg>`;
}

// Creamos una tarjeta por modelo y la colocamos sobre su repisa.
const estanterias = document.getElementById("estanterias");
modelos.forEach(function (modelo) {
  const pieza = document.createElement("article");
  pieza.className = "zapatilla";
  pieza.innerHTML = `<div class="zapatilla-figura">${dibujarZapatilla(modelo)}</div>
    <div class="repisa" aria-hidden="true"></div>
    <div class="datos"><strong>${modelo.nombre}</strong><span>${modelo.tono}</span></div>`;
  estanterias.appendChild(pieza);
});
