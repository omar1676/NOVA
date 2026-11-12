// login.js — pagina de acceso del personal (la misma para todos los paneles).
// Envia el usuario y la contrasena a /api/login. Si son correctos, el servidor
// responde con una cookie de sesion (HttpOnly) y dice a que panel ir segun el
// rol: el administrador, al panel de administracion; el trabajador, a su
// portal. Lo decide el servidor: aqui solo se sigue su respuesta.

const formulario = document.getElementById("adm-login");
const aviso = document.getElementById("adm-login-aviso");
const campoContrasena = document.getElementById("adm-contrasena");

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

    window.location.href = cuerpo.destino;
  } catch (error) {
    aviso.textContent = "No se puede conectar con el servidor.";
  }
});
