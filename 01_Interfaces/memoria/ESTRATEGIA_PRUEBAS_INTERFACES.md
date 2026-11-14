# NOVA Sneakers · Estrategia de pruebas de Interfaces

Desarrollo de Interfaces (módulo 0488). Cubre lo que piden los criterios de evaluación del IM (p. 8):

- **RA8 CE a), b) y g):** «Se establece una estrategia de pruebas, se realizan pruebas de integración y se documentan la estrategia y los resultados obtenidos.»
- **RA4 CE a)-b) y h)-i):** estándares de usabilidad y accesibilidad, claridad de los mensajes y pruebas de usabilidad y accesibilidad.

La prueba de usabilidad con personas tiene su propio documento: `PROCEDIMIENTO_USABILIDAD.md`.

**Convenciones.** Rutas relativas a la raíz del repositorio. Los resultados de la regresión final del **13/11/2026** (commit `1bcbb10`, exportado con `git archive`) están en la regresión del 13/11, y sus capturas, en `01_Interfaces/evidencias/tienda/capturas-2026-11-13/`, `01_Interfaces/evidencias/portal-trabajador/capturas/`, `01_Interfaces/evidencias/reparto-y-correo/capturas/` y `01_Interfaces/evidencias/correo-ethereal/capturas/`. Los scripts de navegador (Playwright y axe) **no están en el repositorio**: se guardan, con los demás scripts de la regresión, en el informe de integración. Marcas: **[PENDIENTE (quién): …]**, y .

---

## 1. Objetivo y alcance

**Objetivo:** comprobar que la web de NOVA cumple los requisitos de Interfaces del IM (IM-INT-04 a 08), que es usable y accesible, y que no se rompe al integrarla con el resto del proyecto.

| En el alcance | Fuera del alcance obligatorio (ampliaciones, que se prueban igual) |
|---|---|
| La web cliente: `01_Interfaces/cliente/index.html`, `css/inicio.css`, `js/modelos.js`, `js/inicio.js` y `js/custom.js` | La tienda online (`js/tienda.js`, `css/tienda.css`) y el panel de administración (`01_Interfaces/admin/`), que comparten página o servidor con la web (§4.4) |
| Escritorio y móvil | El login único del personal y el portal del trabajador de Berme (`01_Interfaces/trabajador/`), integrados en `servidor-admin` (§4.4) |

---

## 2. Qué se prueba y con qué criterio de aceptación

| Requisito | Qué se comprueba | Criterio de aceptación |
|---|---|---|
| IM-INT-04 Estructura mínima | El menú lleva a inicio, catálogo, «Nuestra visión», Custom y contacto; existen las fichas | Cada enlace deja su sección arriba del todo (o al final de la página, si es la última) |
| IM-INT-05 Responsive | Sin desplazamiento horizontal; la cabecera cabe y sus enlaces no se pisan ni se parten | En 1440, 820, 390 y 360 px, y en 11 anchos de 320 a 1440 px |
| IM-INT-06 Catálogo | Las 100 tarjetas enseñan su precio (también en el `aria-label`); cada ficha, precio, descripción y tallas | 100 de 100 |
| IM-INT-07 Custom | Explica el proceso; el formulario bloquea envío vacío, email mal escrito, cantidades negativas o con decimales y un pedido sin pares; suma el total; el envío válido da el mensaje de SIMULACIÓN y no sale ninguna petición de red | Todos los casos |
| IM-INT-08 Calidad | Contraste, foco visible, teclado, consistencia de componentes | 0 violaciones de axe; contraste WCAG AA en el 100 % de los textos medidos |
| RA4 a)-b) | Estándar: **WCAG 2.1 nivel AA** | axe-core con las reglas WCAG 2.1 A y AA; Lighthouse en accesibilidad. **Criterio del equipo:** 0 violaciones de axe y Lighthouse ≥ 90 |
| RA4 c)-g) | Menús, controles y legibilidad | Todos los campos con etiqueta; tallas en `fieldset` con `legend`; zonas táctiles de al menos 24 × 24 px (WCAG 2.2) |
| RA4 h)-i) | Claridad de los mensajes | Errores junto a su campo; `role="status"` o `role="alert"`; foco en el primer campo con error |
| RA4 i) | Usabilidad con personas | Procedimiento de `PROCEDIMIENTO_USABILIDAD.md`. **[PENDIENTE (los tres): hacer la prueba con 3 a 5 personas]** |
| RA8 b) | Integración | Web → servidor → PostgreSQL: lo que enseña la web coincide con la base (§4.4) |

**¿Por qué WCAG 2.1 AA?** Es el estándar internacional de accesibilidad web del W3C, el nivel que se exige habitualmente a las webs públicas en Europa y el que miden las herramientas que se usan (axe-core y Lighthouse). Una web de una marca la usan personas con distintas capacidades, dispositivos y conexiones, y eso incluye a quien navega con teclado, con lector de pantalla o con poco contraste.

---

## 3. Entorno de pruebas

| Elemento | Versión o valor (13/11) |
|---|---|
| Sistema | Windows 11 |
| Navegador | Microsoft Edge 157.0.4341.46, sin ventana, controlado con Playwright 1.65.0 |
| Accesibilidad | axe-core (reglas WCAG 2.1 A y AA) dentro de los scripts; Lighthouse 12.8.2 (11/11) |
| Servidor | `servidor-admin` del árbol exportado en `127.0.0.1:3301`, con un Resend **simulado** en el 3398 para los recibos |
| Base de datos | PostgreSQL 17.11, siempre una **copia desechable** de una base montada desde cero con los scripts 01–23 (clúster de pruebas), nunca la del equipo |
| Datos | Ficticios: correos `@example.com`; las contraseñas de demostración se pasan al ejecutar y no se guardan en ningún resultado |

Playwright, axe-core y Lighthouse **no son dependencias del proyecto**: se usan desde un entorno aparte.

---

## 4. Niveles de prueba

### 4.1 Pruebas unitarias

- **Web:** no hay pruebas unitarias de JavaScript. `custom.js` tiene 52 líneas y su lógica (sumar los pares, exigir al menos uno y componer el mensaje) se prueba en el navegador con los casos del §4.2. **Mejora opcional:** sacar `contarPares` a una función pura y probarla con `node --test`.
- **Servidor (ampliación):** `node --test` sobre la API: `servidor-admin/pruebas/api.test.js` (panel), `tienda.test.js` (tienda) y `portal.test.js` (login único y portal).
- La base, PSP y Python tienen sus propias pruebas automáticas (ver `Memoria_NOVA_Sneakers.pdf`).

### 4.2 Pruebas funcionales en el navegador

| Script (fuera del repositorio) | Qué recorre | Resultado (13/11) | Archivo |
|---|---|---|---|
| `comprobar_interfaces.py` | Los requisitos de Interfaces en 4 anchos: menú, 6 fichas por colección, precio de las 100 tarjetas, formulario Custom (vacío, email mal escrito, sin pares, negativos y decimales, total y simulación sin red), contacto, favicon, «Volver arriba» y axe. Compara con la web de Interfaces del 11/11 (`60a3fcd`) | **136 de 136** (01:16–01:18) | la regresión del 13/11 |
| `comprobar_web.py` | Toda la web: las 132 imágenes, escaparate, filtros, búsquedas con y sin resultados, ficha, probador, navegación y movimiento reducido | **114 de 114** (01:18–01:22) | la regresión del 13/11 |
| `comprobar_mejoras.py` | Las 100 fichas con su bloque de compra, teclado, 11 anchos de 320 a 1440 px, probador y axe | **81 de 81** (01:14–01:16) | la regresión del 13/11 |

Ejemplo de lo que comprueba (la regresión del 13/11):

```
OK    [escritorio] sin desplazamiento horizontal -> [1440, 1440]
OK    [escritorio] las 100 tarjetas del catálogo muestran su precio (también en aria-label) -> 100 tarjetas; ej.: Ver NOVA Street Vortex, 109,90 €, disponible; mal: []
OK    [escritorio] sin ningún par: avisa y lleva el foco a la primera talla -> Indica cuántos pares quieres de al menos una talla. | foco en talla 38
OK    [escritorio] cantidades negativas o con decimales: bloqueadas -> negativa=True decimal=True
OK    [escritorio] el total de pares se actualiza al escribir (8 tallas x 5 = 40) -> 40
```

### 4.3 Accesibilidad

| Prueba | Cómo | Resultado | Archivo |
|---|---|---|---|
| axe-core en la web: página en escritorio y móvil, ficha abierta, probador abierto y formulario enviado | Dentro de los scripts de §4.2 | **0 violaciones** (13/11) | la regresión del 13/11 |
| axe-core en la tienda: catálogo, ficha, carrito, diálogos de inicio de sesión y registro de Álvaro, entrega, pago, confirmación y «Mis pedidos», en escritorio y móvil | Dentro de la compra en Edge (§4.4) | **0 violaciones** en las 18 pantallas (13/11) | la regresión del 13/11 |
| axe-core en el panel y el recibo | Recorrido de reparto | **0 violaciones** en la página de pedidos (escritorio y móvil) y en el HTML del recibo | la regresión del 13/11 |
| axe-core en el login único y el portal del trabajador | Recorrido del portal | Login: **0 violaciones**. Las cuatro páginas del portal: **ninguna violación nueva** frente al original de Berme (en escritorio, 0; el original tenía `label` 940 y `select-name` 1 en inventario). En móvil, «Personalizados» mantiene las 2 `scrollable-region-focusable` que ya tenía | la regresión del 13/11 |
| Contraste de cada texto en Edge | Medida real de colores de primer plano y fondo | **212 de 212** cumplen AA (12/11; no se ha repetido el 13/11: la paleta no ha cambiado) | Informe de integración |
| Lighthouse | Escritorio y móvil | Accesibilidad **100** y buenas prácticas **100** en los dos (11/11) | `01_Interfaces/evidencias/web/lighthouse/lighthouse_escritorio.html` y `lighthouse_movil.html` |
| Teclado | Tabulador por toda la página; ficha que se cierra con Escape; radios de color y talla con flechas | Bien (13/11) | la regresión del 13/11; `01_Interfaces/evidencias/web/README.md` («Checklist de accesibilidad») |
| Movimiento reducido | `prefers-reduced-motion: reduce` | Sin animación de entrada (13/11) | la regresión del 13/11 |
| Lector de pantalla | NVDA o Narrador | No se ha probado (mejora recomendable) | — |

Checklist que se cumple (`01_Interfaces/evidencias/web/README.md`): `lang="es"` y enlace «Saltar al escaparate»; todas las imágenes con `alt` (vacío en las decorativas); tarjetas que son botones con un nombre que incluye el precio; todos los campos con etiqueta y los opcionales marcados; errores y resultado anunciados; foco visible; zonas táctiles del menú de 36 px o más.

### 4.4 Pruebas de integración (RA8 CE b)

La web no tiene servidor propio para lo obligatorio (el formulario Custom es una simulación, como permite el IM). La integración de la web con la base se prueba con las ampliaciones que hablan con PostgreSQL a través de `servidor-admin`. Todas el **13/11**, sobre copias desechables de la base 01–23:

| Prueba | Qué integra | Resultado | Archivo |
|---|---|---|---|
| Compra completa en Edge, en escritorio y móvil | Web → `servidor-admin` → PostgreSQL → panel: registro, login, carrito, pago aceptado y rechazado, stock, auditoría y el pedido en el panel, con axe en cada pantalla nueva | **139 de 139**; 4 pedidos web pagados y 4 recibos en el Resend simulado | la regresión del 13/11; capturas en `01_Interfaces/evidencias/tienda/capturas-2026-11-13/` |
| Recorrido de reparto | Compra → recibo → «Marcar en reparto» en el panel → «En reparto» en «Mis pedidos» | **29 de 29** | la regresión del 13/11; capturas en `01_Interfaces/evidencias/reparto-y-correo/capturas/` |
| Login único, roles y portal del trabajador | `admin.demo` → panel; `taller.demo` → portal; `tienda.demo` (comercial) → «Acceso denegado» sin cookie; las cuatro páginas del portal; «Avanzar estado» e inventario contrastados con la base; 403 del trabajador en `/api/admin/`; cerrar sesión y «Atrás» sin datos; escritorio y móvil | **82 de 82** | la regresión del 13/11; capturas en `01_Interfaces/evidencias/portal-trabajador/capturas/` |
| API de la tienda | Catálogo frente a la base, precios manipulados, doble clic, últimos pares a la vez, recibos (7 con Resend simulado y 7 con Ethereal simulado) | **39 de 39** (`npm run test:tienda`) | la regresión del 13/11 |
| API del panel | Las 8 rutas de lectura, «Marcar en reparto», permisos y seguridad | **23 de 23** (`npm test`) | la regresión del 13/11 |
| API del login único y del portal | Roles, sesiones, las dos funciones del script 23 y su auditoría | **24 de 24** (`npm run test:portal`) | la regresión del 13/11 |
| Recibo real contra Ethereal (datos ficticios) | Compra en Edge → correo de prueba → enlace en «Mis pedidos» | **16 de 16**; sin red y con Ethereal mudo, **5 de 5** y **5 de 5** (la compra sigue confirmada y el stock baja una vez) | la regresión del 13/11; capturas en `01_Interfaces/evidencias/correo-ethereal/capturas/` |
| Catálogo web frente a PostgreSQL | El script 21 carga en la base los mismos 100 modelos (880 SKU) que enseña la web | **55 de 55** en el SQL de la tienda | la regresión del 13/11 |

### 4.5 Extremo a extremo entre módulos

El caso SO024 recorre PostgreSQL → PSP → Python con datos **PROVISIONALES** (13/11: 40 pares, 3.996,00 €, PSP con código 0 y un solo pedido en Python; la regresión del 13/11). La web Custom solo simula el envío, sin registrar pedidos. En la entrega se presenta S00005 del Club Atlético NOVA mediante el PDF de Berme; no hay evidencia que conecte esa venta con la solicitud web ni con el ensayo SO024. Este último es una prueba histórica del ejemplo del enunciado, no una venta oficial por completar.md`.

### 4.6 Responsive

- **Anchos:** 1440, 820, 390 y 360 px (`comprobar_interfaces.py`) y 11 anchos de 320 a 1440 px (`comprobar_mejoras.py`), los dos en verde el 13/11.
- **Qué se mide:** que el ancho del documento no supere el de la ventana; que la cabecera quepa y sus enlaces no se pisen ni se partan en dos líneas; que las fichas quepan.
- **Capturas:** escritorio (1440 × 900) y móvil (390 × 844) de inicio, catálogo, ficha, formulario vacío, aviso sin pares, simulación y contacto en `01_Interfaces/evidencias/web/capturas/` (11/11); compra en escritorio y móvil en `01_Interfaces/evidencias/tienda/capturas-2026-11-13/`; portal en móvil en `01_Interfaces/evidencias/portal-trabajador/capturas/` (13/11).
- Es Edge simulando un móvil. El móvil de verdad entra en la tarea T6 de la prueba de usabilidad (`PROCEDIMIENTO_USABILIDAD.md`).

### 4.7 Regresión

Después de cada cambio en la web se vuelven a pasar los scripts de §4.2 a §4.4. **La última pasada es la del 13/11, sobre el árbol final:** mejoras 81/81, interfaces 136/136, web 114/114, compra 139/139, reparto 29/29, portal 82/82 y Ethereal 16/16, 5/5 y 5/5 (la regresión del 13/11). Lighthouse no se ha repetido desde el 11/11, y después cambiaron los nombres de los 100 modelos, los colores por colección y el bloque de compra de la ficha: conviene repetirlo antes de entregar (mejora recomendable).

---

## 5. Trazabilidad: requisito → prueba → evidencia

| Requisito | Prueba | Evidencia |
|---|---|---|
| IM-INT-04 | Menú → secciones; fichas | la regresión del 13/11; capturas `01_Interfaces/evidencias/web/capturas/*_01_*.png` y `*_07_*.png` |
| IM-INT-05 | Anchos | la regresión del 13/11; capturas de escritorio y móvil |
| IM-INT-06 | 100 tarjetas y 6 fichas | la regresión del 13/11; capturas `*_02` y `*_03` |
| IM-INT-07 | Casos del formulario | la regresión del 13/11; capturas `*_04` a `*_06_*.png` |
| IM-INT-08 | axe, contraste, teclado | la regresión del 13/11; contraste 212/212 (12/11); Lighthouse (11/11) |
| RA4 a)-b) | WCAG 2.1 AA | §2 y §4.3 de este documento |
| RA4 c)-i) | Checklist y mensajes | `01_Interfaces/evidencias/web/README.md`; mensajes junto a su campo en la regresión del 13/11 |
| RA4 i) usabilidad | Prueba con personas | **[PENDIENTE (los tres)]** `PROCEDIMIENTO_USABILIDAD.md` |
| RA8 a) y g) | Esta estrategia y los resultados | Este documento y la regresión del 13/11 |
| RA8 b) | Integración | §4.4 |

---

## 6. Problemas que encontraron las pruebas

Las pruebas no solo confirman: también encontraron fallos que se corrigieron.

| Qué se encontró | Cómo | Qué se hizo | Fuente |
|---|---|---|---|
| El probador no dejaba elegir las tres complexiones con ninguna zapatilla y el peso no hacía nada | Reproducción en Edge: Playwright se quedaba esperando una opción oculta | Se arregló `js/inicio.js`; 618 combinaciones de cuerpo y zapatilla bien | Informe de integración (mejoras de la web) |
| El restyle de Álvaro bajaba el contraste del precio a 1,0–1,8:1 y el del foco a 1,3:1 | Medida de contraste en Edge | Pastilla oscura, banda opaca y doble contorno de foco: 212/212 | `01_Interfaces/cliente/README.md` |
| En una pasada del 12/11, «menú → Custom» falló una vez (135/136) por el desplazamiento suave mientras otra prueba cargaba el ordenador | Repetición | Las pasadas siguientes y la del 13/11 dieron 136/136 | Informe de integración; la regresión del 13/11 |
| El portal de Berme tenía 940 campos de cantidad sin etiqueta y desplegables sin nombre accesible (axe) | axe sobre el original y sobre el integrado | Nombres accesibles en el buscador, los desplegables y los campos: 0 violaciones en escritorio | la regresión del 13/11; `servidor-admin/README.md` |
| La etiqueta del login decía «Usuario o correo», pero solo acepta correo | Corregido el 13/11: la etiqueta y el aviso piden el correo (pendiente del visto bueno de Álvaro) | |md` §3 |
| En el panel y en «Personalizados» del portal, en móvil, axe da `scrollable-region-focusable` en tablas sin botones | axe | | la regresión del 13/11 |

---

## 7. Cómo repetir las pruebas

1. Montar una base desechable con los scripts (`manuales/MANUAL_INSTALACION.md` §3).
2. Arrancar `servidor-admin` contra esa base en un puerto libre (`.env` con las contraseñas de prueba; nunca la base del equipo).
3. Lanzar los scripts de §4.2 y §4.4 con un Python que tenga Playwright y Edge. Los scripts no están en el repositorio: están, con los que lanzan toda la regresión, en el informe de integración.
4. Lanzar `npm test`, y solo con `PRUEBA_TIENDA_BASE_DESECHABLE=si`, `npm run test:tienda` y `npm run test:portal` (`servidor-admin/README.md`).
5. Lighthouse: desde Edge o Chrome, pestaña Lighthouse, categorías Accesibilidad y Buenas prácticas, en escritorio y en móvil.

Comprobaciones rápidas sin navegador: `py scripts\comprobar_web.py` comprueba que existen los recursos locales que enlaza la web (no evalúa el diseño ni la API; correcta el 13/11). La lista de comprobaciones manuales de Berme está en `manuales/PRUEBAS_MANUALES.md`.
