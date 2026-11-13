// Página «Análisis de datos» del panel: enseña dentro del panel el dashboard de
// Python (04_Python/app_dashboard.py). Es una aplicación de Streamlit con su
// propio servidor, así que aquí solo se carga en un iframe.
//
// Para verlo hay que tener arrancados los dos servidores:
//   - el del panel:   npm start                          (en servidor-admin)
//   - el de Python:   .venv\Scripts\streamlit.exe run app_dashboard.py   (en 04_Python)
// El panel ya exige haber entrado como administrador. Streamlit solo escucha en
// este ordenador (04_Python/.streamlit/config.toml).

const PUERTO_DASHBOARD = 8501; // el puerto por defecto de Streamlit

const direccionDashboard = `${location.protocol}//${location.hostname}:${PUERTO_DASHBOARD}/`;
const marco = document.getElementById("adm-analisis-marco");
const avisoAnalisis = document.getElementById("adm-analisis-aviso");
const enlaceAnalisis = document.getElementById("adm-analisis-enlace");

enlaceAnalisis.href = direccionDashboard;

// Antes de cargarlo se comprueba que Streamlit está arrancado. Con "no-cors" la
// respuesta no se puede leer, pero la petición solo falla si nadie contesta.
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
  // embed=true quita la barra de Streamlit (el marco ya está dentro del panel) y
  // dark_theme usa la variante oscura de 04_Python/.streamlit/config.toml, con los
  // colores del panel
  marco.src = direccionDashboard + "?embed=true&embed_options=dark_theme";
  marco.hidden = false;
}

mostrarDashboard();
