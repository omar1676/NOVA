// login.js — pagina de acceso al panel.
// Envia el usuario y la contrasena a /api/login. Si son correctos, el servidor
// responde con una cookie de sesion (HttpOnly) y se pasa al dashboard.

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

    if (!respuesta.ok) {
      aviso.textContent = cuerpo.error;
      campoContrasena.value = "";
      return;
    }

    // Usuario correcto, pero sin permiso para el panel: se cierra su sesion
    if (!cuerpo.accesoPanel) {
      await fetch("/api/logout", { method: "POST" });
      aviso.textContent = "El usuario " + cuerpo.usuario + " (" + cuerpo.rol + ") no tiene permiso para el panel.";
      campoContrasena.value = "";
      return;
    }

    window.location.href = "admin.html";
  } catch (error) {
    aviso.textContent = "No se puede conectar con el servidor del panel.";
  }
});
