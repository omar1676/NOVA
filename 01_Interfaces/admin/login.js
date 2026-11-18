// login.js — pagina de acceso del personal (la misma para todos los paneles). Envia usuario y
// contrasena a /api/login; si son correctos, el servidor crea la sesion (cookie HttpOnly) y dice a que
// panel ir segun el rol (administrador o trabajador). Lo decide el servidor: aqui solo se sigue.

// Elementos de la pagina
const formulario = document.getElementById("adm-login");
const aviso = document.getElementById("adm-login-aviso");
const campoContrasena = document.getElementById("adm-contrasena");

// Login del personal: al enviar el formulario se llama a la API con fetch (sin recargar)
formulario.addEventListener("submit", async function (evento) {
  evento.preventDefault();
  aviso.textContent = "";

  const datos = {
    usuario: document.getElementById("adm-usuario").value.trim(),
    contrasena: campoContrasena.value
  };

  try {
    const respuesta = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(datos)
    });
    const cuerpo = await respuesta.json();

    // 401 credenciales mal, 403 sin panel web, 429 demasiados intentos...
    if (!respuesta.ok) {
      aviso.textContent = cuerpo.error;
      campoContrasena.value = "";
      return;
    }

    window.location.href = cuerpo.destino; // el panel de su rol
  } catch (error) {
    aviso.textContent = "No se puede conectar con el servidor.";
  }
});
