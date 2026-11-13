# Página «Análisis de datos» del panel (13/11/2026)

Esta página enseña el dashboard de Python (`04_Python/app_dashboard.py`, Streamlit) dentro del panel de administración de Álvaro.

**Cómo se probó:**
- **Árbol:** la rama de la limpieza final, con la página nueva.
- **Entorno:** una base desechable montada desde cero con los scripts 01–23, el servidor Node en el puerto 3301 y Streamlit en el 8501.
- **Navegador:** Microsoft Edge con la ventana visible (Playwright) y axe.
- **Datos del dashboard:** la exportación de PRUEBA de `04_Python/entrada_acc/`.
- **Scripts:** el de Playwright no está en el repositorio; su resultado sí.

| Archivo | Qué es | Resultado |
|---|---|---|
| `00_escucha_streamlit.txt` | En qué direcciones escucha Streamlit (`netstat`) | Solo en `127.0.0.1:8501`: no se puede abrir desde otro equipo |
| `01_con_streamlit.txt` | Las pruebas con Streamlit arrancado | **43 de 43** |
| `02_sin_streamlit.txt` | Las pruebas con Streamlit parado | **2 de 2** |
| `capturas/` | Escritorio, filtro aplicado, pestaña Predicción, tablet, móvil y la página sin Streamlit | — |

## Qué se comprueba (`01_con_streamlit.txt`)

1. **«Análisis de datos» sale una sola vez en el menú** de las 12 páginas del panel, y todas cargan.
2. **Misma estructura que el resto del panel:** la barra lateral de Álvaro, el título y la opción activa. Dentro del panel, el dashboard usa la variante oscura con los colores del panel.
3. **Las Estadísticas y el Dashboard de Álvaro siguen funcionando:** tarjetas con datos y gráficos dibujados.
4. **El dashboard de Python sigue completo:** las 6 pestañas, dentro del panel. Abierto por su cuenta, sigue con su tema claro de siempre.
5. **Filtros, descargas y refresco funcionan dentro del panel:**
   - el filtro «confirmado» pasa de 12 a 1 pedido, y «Restablecer filtros» los devuelve;
   - una descarga CSV lleva su origen;
   - la hora de la comprobación cambia sola a los 60 s.
6. **Escritorio (1440 px), tablet (820 px) y móvil (390 px):** sin desplazamiento horizontal y con las cifras visibles.
7. **Solo entra el administrador:**
   - sin sesión, la página lleva al inicio de sesión;
   - el trabajador (`taller.demo`), el comercial (`tienda.demo`) y un cliente de la tienda con su sesión no pueden verla.
8. **axe** no encuentra en la página ninguna violación que no tenga ya la página Estadísticas, y no hay errores de JavaScript.

**Límite conocido.** Streamlit no tiene login propio. Solo escucha en este ordenador, así que desde otro equipo no se abre. Pero en este ordenador `http://localhost:8501` se puede abrir sin pasar por el panel; es el mismo dashboard que pide la rúbrica de Python. Los avisos de axe que ya tenía ese dashboard por su cuenta siguen igual: imágenes sin texto alternativo, un bloque de texto con desplazamiento y un gráfico SVG sin título. El tema oscuro no añade ninguno.
