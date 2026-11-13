# Pruebas de Interfaces · web cliente de NOVA Sneakers

Pruebas hechas el 11 de noviembre de 2026 sobre `01_Interfaces/cliente`, con la web servida en local (`127.0.0.1`).

| Herramienta | Versión | Para qué |
|---|---|---|
| Microsoft Edge (sin ventana, controlado con Playwright 1.65) | 157 | Recorrer la web y hacer las capturas |
| axe-core | 4.12.1 | Accesibilidad, reglas WCAG 2.1 A y AA |
| Lighthouse | 12.8.2 | Accesibilidad y buenas prácticas, en escritorio y en móvil |

Los scripts de prueba no forman parte de la web y no están en el repositorio. Aquí se guardan sus resultados.

## Resultados

| Prueba | Resultado | Archivo |
|---|---|---|
| Requisitos de Interfaces a 1440, 820, 390 y 360 px, más la cabecera en 11 anchos de 320 a 1440 px | **136 de 136** | `resultados/pruebas_interfaces.txt` |
| Toda la web: escaparate, filtros, búsquedas, ficha, probador, navegación y movimiento reducido | **114 de 114** | `resultados/pruebas_toda_la_web.txt` |
| axe-core en 5 estados: página en escritorio y en móvil, ficha abierta, probador abierto y formulario enviado | **0 violaciones** | `resultados/pruebas_interfaces.txt` |
| Lighthouse en escritorio | Accesibilidad **100** · Buenas prácticas **100** | `lighthouse/lighthouse_escritorio.html` |
| Lighthouse en móvil | Accesibilidad **100** · Buenas prácticas **100** | `lighthouse/lighthouse_movil.html` |

Los informes de Lighthouse se abren con el navegador.

## Checklist de accesibilidad

- [x] La página declara el idioma (`lang="es"`) y tiene un enlace «Saltar al escaparate» para el teclado.
- [x] Todas las imágenes tienen `alt`. Las decorativas lo llevan vacío y la ficha describe el modelo.
- [x] Las tarjetas del catálogo son botones con un nombre que incluye el precio, por ejemplo «Ver NOVA Street 01, 109,90 €».
- [x] Formulario Custom:
  - todos los campos tienen etiqueta;
  - las tallas van en un `fieldset` con `legend`;
  - los opcionales están marcados como «(opcional)».
- [x] Los errores y el resultado del formulario se anuncian (`role="status"`). Si faltan pares, el foco va a la primera talla.
- [x] El foco se ve al usar el teclado (contorno oscuro en las secciones claras) y la ficha se cierra con Escape.
- [x] Contraste WCAG AA en todos los textos: lo comprueban axe y Lighthouse.
- [x] Con «reducir movimiento» activado, la animación de entrada no aparece.
- [x] En el móvil, los enlaces del menú tienen una zona táctil de 36 px de alto o más (el mínimo de WCAG 2.2 es 24×24).

## Checklist de usabilidad

- [x] **El menú lleva a todas las secciones obligatorias.**
  - En escritorio: inicio (logo), Catálogo, Nuestra visión, Custom y Contacto.
  - En el móvil: inicio, Catálogo, Custom y Contacto. «Nuestra visión» se alcanza bajando por la página.
- [x] Sin desplazamiento horizontal en ningún ancho entre 320 y 1440 px.
- [x] Los enlaces de la cabecera no se parten en dos líneas ni se pisan.
- [x] **Catálogo:**
  - filtros por colección y buscador;
  - aviso cuando no hay resultados;
  - precio orientativo en cada tarjeta.
- [x] **Ficha:** precio orientativo, descripción y tallas. Se actualiza si se cambia de zapatilla en el probador.
- [x] **Formulario Custom:**
  - avisa de que es un prototipo antes de rellenarlo;
  - calcula el total de pares mientras se escribe;
  - rechaza un email mal escrito, las cantidades negativas o con decimales, y un pedido sin pares;
  - al enviar no sale ninguna petición de red y la página no se recarga.
- [x] «Volver arriba» deja la página arriba del todo, con la cabecera visible.
- [x] La pestaña del navegador muestra un favicon: la estrella del logo.

## No probado todavía

- Con un móvil real. Las pruebas usan Edge simulando un móvil.
- Con un lector de pantalla (NVDA o Narrador).
- Con usuarios reales: una prueba corta con compañeros, apuntando qué tareas completan y dónde dudan.

## Capturas (`capturas/`)

Escritorio a 1440×900 y móvil a 390×844:

| Captura | Qué enseña |
|---|---|
| `*_01_inicio_y_menu` | Portada y menú |
| `*_02_catalogo_con_precios` | Catálogo con precios |
| `*_03_ficha_precio_tallas` | Ficha con precio y tallas |
| `*_04_custom_formulario_vacio` | Formulario vacío, con el aviso de prototipo |
| `*_05_custom_aviso_sin_pares` | Aviso cuando no se indica ningún par |
| `*_06_custom_simulacion` | Mensaje de simulación |
| `*_07_contacto` | Sección de contacto |

En las capturas del formulario, el reparto de 5 pares en las tallas 38 a 45 es **de prueba**. No es el reparto de SO024, que todavía no está acordado.

## Datos provisionales

Los precios y las tallas de cada colección (`js/modelos.js`, objeto `datosColeccion`) son **PROVISIONALES**. Faltan por acordar con Berme y Álvaro, para que coincidan con Odoo y PostgreSQL.
