// Muestra el dashboard de Streamlit en un iframe; necesita ambos servidores.
// El panel exige acceso de administrador y Streamlit escucha en este ordenador.
// Arranque de Python y Node: README.md, «Web, panel, portal del trabajador y tienda».

const PUERTO_DASHBOARD = 8501; // el puerto por defecto de Streamlit

// Dirección de Streamlit (este mismo ordenador) y elementos de la página
const direccionDashboard = `${location.protocol}//${location.hostname}:${PUERTO_DASHBOARD}/`;
const marco = document.getElementById("adm-analisis-marco");
const avisoAnalisis = document.getElementById("adm-analisis-aviso");
const enlaceAnalisis = document.getElementById("adm-analisis-enlace");

enlaceAnalisis.href = direccionDashboard;

// Comprueba si Streamlit está arrancado: si lo está, lo carga en el marco; si no, avisa.
// Con no-cors se detectan fallos de conexion, pero no se puede leer el estado HTTP.
async function mostrarDashboard() {
  try {
    await fetch(direccionDashboard + "_stcore/health", { mode: "no-cors", cache: "no-store" });
  } catch {
    avisoAnalisis.textContent =
      "El dashboard de Python no está arrancado. En la carpeta 04_Python: " +
      ".venv\\Scripts\\streamlit.exe run app_dashboard.py (y después recarga esta página).";
    avisoAnalisis.hidden = false;
    return;
  }
  // embed=true quita la barra de Streamlit y dark_theme usa el tema oscuro de
  // 04_Python/.streamlit/config.toml, con los colores del panel
  marco.src = direccionDashboard + "?embed=true&embed_options=dark_theme";
  marco.hidden = false;
}

mostrarDashboard();
