# NOVA Sneakers · Web cliente

Abre `index.html` en un navegador moderno. No hace falta instalar librerías ni compilar el proyecto: el escaparate, el catálogo, la ficha, el probador, Custom y Contacto funcionan así.

Para **comprar**, la web tiene que abrirse desde el servidor: `http://127.0.0.1:3000/tienda/` (ver `servidor-admin/README.md`). Sin servidor, la ficha avisa de que la tienda online no está disponible.

## Dónde está cada cosa

- `index.html`: el contenido de la página: cabecera, estantería, catálogo, ficha, servicio Custom y un único pie de página (`<footer id="contacto">`) con el contacto, la marca y «Volver arriba».
- `css/inicio.css`: colores, tamaños, distribución y diseño para móviles.
- `js/modelos.js`: lista de zapatillas, con su nombre comercial, colección y rutas de imágenes, y `datosColeccion`, con el precio orientativo, las tallas y la descripción de cada colección. Es el único sitio de la web donde se escriben los nombres.
- `js/inicio.js`: muestra las zapatillas y controla los filtros, las búsquedas y la ficha.
- `js/custom.js`: suma los pares por talla del formulario Custom y simula el envío.
- `js/tienda.js` y `css/tienda.css`: la tienda online (catálogo real, carrito, cuenta, pedido y «Mis pedidos»).
- `images/favicon.png`: favicon de 64×64. Es la estrella del logo, recortada de `logo-nova.png`.
- `images/nova/street/`: imágenes de la colección Street.
- `images/nova/luxe/`: imágenes de la colección Luxe.
- `images/nova/casual/`, `hombre/`, `mujer/` y `unisex/`: imágenes transparentes del ZIP de 80 modelos.

Cada modelo de `modelos.js` tiene dos rutas: `imagen` se muestra en la estantería, en la ficha y en la miniatura del probador; `imagenCatalogo` aparece en el catálogo inferior. En Street y Luxe, `imagen` apunta a los archivos `-sinfondo.webp`, recortados a partir de las fotos originales de 1254 px del ZIP de 20 modelos, e `imagenCatalogo` a la foto que conserva su fondo de estudio. Esos modelos llevan `catalogoConFondo: true` para que la tarjeta amplíe la foto hasta llenar su hueco (`object-fit: cover`) en vez de mostrarla como un recuadro dentro de otro; las imágenes sin fondo se muestran enteras (`object-fit: contain`). Si se quiere usar la misma foto en ambos sitios, se puede poner la misma ruta en los dos campos y quitar `catalogoConFondo`. Las rutas son relativas a `index.html`.

Con el rediseño de tarjetas de Álvaro (commit `5f0ce57`), el catálogo usa `imagen` en todas las tarjetas, sin fondo y con sombra. `imagenCatalogo` y `catalogoConFondo` siguen en los datos, pero el catálogo no los usa. Queda por decidir con qué foto se queda.

**Colores por colección.** Cada tarjeta lleva la clase `c-<colección>` y los colores de Álvaro (las variables `--col-claro` y `--col-oscuro` del final de `inicio.css`): su degradado en la zona de la foto, una etiqueta con el nombre de la colección y una banda inferior del tono oscuro con el nombre, el precio y la disponibilidad en claro. Los filtros del catálogo llevan un punto del mismo color. Respecto a su versión se han cambiado tres cosas para cumplir WCAG AA: la etiqueta va en una pastilla oscura (su texto blanco sobre el tono claro se quedaba en 2,9:1), la banda es opaca (sobre el degradado el precio bajaba de 4,5:1) y el foco suma a su contorno claro `#f6c696` otro oscuro por fuera (el claro solo, sobre el fondo del catálogo, daba 1,3:1).

Los archivos acabados en `-recorte.webp` ya no se usan: al quitarles el fondo blanco se borraron también las partes blancas y crema de varias zapatillas (por ejemplo, las fotos 02, 04 y 07 de Street y 02, 05 y 08 de Luxe), que se veían blanquecinas o casi invisibles sobre la estantería. Para recortar fotos nuevas con fondo claro no basta con un umbral de claridad: hay que rellenar el fondo desde los bordes de la imagen, para no agujerear las zonas claras de la zapatilla, y quitar aparte la sombra que queda bajo la suela.

Para añadir una zapatilla, copia un objeto de `modelos.js`, cambia su nombre y las rutas, y comprueba que los archivos existen. Para venderla, añádela también a `21_catalogo_web.sql` con el mismo nombre. Usa `street`, `luxe`, `casual`, `hombre`, `mujer` o `unisex` en el campo `coleccion` para que aparezca en su filtro. El número mostrado en los filtros se calcula a partir de la lista.

El **nombre** es lo que une un modelo de la web con PostgreSQL. Cada modelo tiene un nombre comercial, «NOVA <colección> <nombre>», con un estilo por colección: Street, palabras cortas de energía urbana (Vortex, Drift…); Luxe, materiales nobles (Onyx, Ivory…); Casual, paseo mediterráneo (Marea, Olivo…); Hombre, cumbres (Aneto, Teide…); Mujer, estrellas y cielo (Aurora, Luna…); y Unisex, ciudades (Lisboa, Oslo…). Las fotos conservan su número (`nova-street-01…`). Los 100 modelos están en la base gracias a `21_catalogo_web.sql` y se pueden comprar; los nombres de `modelos.js` y del 21 tienen que coincidir.

El precio, las tallas y la descripción de `datosColeccion` son comunes a todos los modelos de una colección. Son el precio **orientativo** que se ve si la tienda no responde. Con la tienda, el precio, el color, las tallas y el stock vienen de PostgreSQL; `21_catalogo_web.sql` usó esos mismos precios y tallas. Son **provisionales**: el equipo tiene que acordarlos para que coincidan con Odoo.

## Formulario Custom

Pide club o equipo, persona de contacto, email, modelo, personalización y pares de cada talla, de la 38 a la 46; el teléfono y los colores son opcionales. El navegador comprueba los campos obligatorios, el formato del email y que las cantidades sean números enteros no negativos; `custom.js` suma el total y exige al menos un par. No hay servidor: el envío es una **simulación**, no se envía ningún dato y no se registra ningún pedido. SO024 aparece solo como ejemplo de pedido.

## Tienda online

`js/tienda.js` pide al servidor el catálogo real y se encarga del resto:

- **Barra bajo la cabecera:** «Iniciar sesión» (o el saludo, «Mis pedidos» y «Cerrar sesión») y «Carrito (n)». No toca la cabecera, que sigue igual en todos los anchos.
- **Tarjetas del catálogo:** «Disponible» o «Agotado» (ninguna talla con stock), también en su `aria-label`. «No disponible» solo sale si un modelo de la web no está en la base (por ejemplo, en una base sin el 21 nuevo).
- **Ficha:** el bloque de compra va en un panel oscuro liso, como en una tienda: el precio grande; el color con su muestra y su nombre («Color: Gris y coral»; el tono de cada palabra está en `TONOS`, en `tienda.js`); la talla en una cuadrícula de botones (la elegida rellena, las agotadas tachadas, con una raya y desactivadas); el aviso de stock con un punto de color; la cantidad con «−» y «+»; y «Añadir al carrito» como botón principal. Cada error sale debajo de su campo («Elige una talla.» bajo las tallas y los de cantidad bajo la cantidad, con `role="alert"`); el mensaje de «Añadido al carrito», debajo del botón, con «Ver el carrito». No se puede pedir más de lo que hay en stock ni más de 10 pares por talla (el mismo límite que el servidor y el SQL). Los radios de color y talla son radios de verdad, transparentes encima de su dibujo: van con el teclado (flechas) y el lector de pantalla los anuncia.
- **Carrito:** se guarda en `localStorage` con **solo el SKU y la cantidad**. Al cargar la página se vuelve a pedir el catálogo: lo que ya no existe o se ha agotado se quita, y lo cuenta. El total del carrito es una estimación; el que vale lo calcula PostgreSQL.
- **Cuenta:** el inicio de sesión es el **diálogo de Álvaro** (commit `52a8800`), con su HTML, su CSS y su JavaScript. Lo único que cambia son las dos últimas líneas de su `submit`, que ahora llaman al servidor, y un enlace a «Crear una cuenta». Las cuentas de cliente son distintas de las de los trabajadores.
- **Pedido en tres pasos:**
  1. Entrega: la dirección es obligatoria.
  2. Pago simulado: el pedido ya está creado como pendiente y se ven las líneas y el total calculados por PostgreSQL. Hay dos botones, «Simular pago aceptado» y «Simular pago rechazado». **No se pide ningún dato bancario y no se cobra nada.**
  3. Resultado: si se acepta, el pedido queda confirmado y se descuenta el stock; si se rechaza o se cancela, el pedido queda cancelado. Si se cierra la ventana sin pagar, el pedido se cancela.
- **Mis pedidos:** el historial del cliente, con el detalle de cada pedido.

## Pendiente de integración

Los precios, las tallas y el stock de los 100 modelos de la tienda son provisionales y hay que acordarlos con Odoo, igual que los impuestos y la correspondencia entre la referencia `WEB-…` de la tienda y la de Odoo. La web no genera referencias SO. El formulario Custom sigue simulando el envío de la solicitud.

El SQL identifica la talla con `producto_sku` y la personalización como texto a nivel del pedido. El caso CUSTOM-40 contiene varias líneas de tallas y una misma descripción de personalización. Debe acordarse cómo representar varias personalizaciones distintas en una compra sin perder información. PSP actualmente consume el CSV de fabricación de PostgreSQL, no una exportación de Odoo. La confirmación SQL descuenta stock y la cancelación lo devuelve; crear una línea no reserva stock.

Carrito, checkout, cuentas e historial ya funcionan con PostgreSQL (ver «Tienda online»). Falta el personalizador.

## Navegación entre secciones

En móvil se puede desplazar la página normalmente. En la franja inferior de la estantería, deslizar hacia arriba lleva al catálogo; también se puede pulsar «Desliza o ver catálogo». El enlace funciona con ratón y teclado. En el catálogo se puede buscar y filtrar por colección.

## Probador conceptual

Desde la ficha se puede abrir el probador, escoger cualquiera de los modelos del catálogo y cambiar de escenario. El desplegable «Vista y complexión» ofrece, con **todas** las zapatillas, tres figuras: complexión delgada (`modelo-delgado.png`), media (`modelo-base.png`) y amplia (`modelo-ancho.png`). Las figuras llevan un calzado genérico, así que la zapatilla elegida se ve en una tarjeta blanca a su lado, con el aviso «Figura con calzado genérico · tu zapatilla, al lado». Al cambiar de zapatilla se mantiene la figura elegida.

La estatura (120–220 cm) cambia la escala visual y el peso (30–200 kg) se redondea en intervalos de 5. **Al cambiar la estatura o el peso se elige la figura más parecida** según el IMC (peso / estatura²): por debajo de 20, delgada; de 20 a 27, media; desde 27, amplia. Es solo una forma de escoger una de las tres imágenes, no una recomendación. Las imágenes son aproximaciones y no sirven para recomendar talla.

Algunas zapatillas tienen además fotos con esa zapatilla puesta: el campo `probador` de su objeto en `modelos.js` dice cuáles (NOVA Street Vortex, una pose; NOVA Casual Marea, dos poses; NOVA Casual Olivo y NOVA Casual Paseo, una escena fija cada una). Esas opciones solo aparecen con su zapatilla y son la vista inicial; las demás zapatillas empiezan con «Zapatilla sola», que la enseña en grande sobre el escenario con el aviso «Aún no hay foto con este modelo puesto». Las escenas fijas tienen escenario y pose propios: mientras se ven, el escenario no se puede cambiar. Pelo, tono de piel y el resto de zapatillas puestas siguen pendientes. Las personas con calzado genérico que no son figuras (`persona-01` a `persona-04`, `modelo-urbano` y `modelo-deportivo`) siguen en `images/probador/`, pero no se ofrecen.

Antes, las tres figuras estaban en el desplegable pero ocultas y desactivadas con todas las zapatillas, y el peso no hacía nada: por eso «ponerlo más gordo» no funcionaba.

## Logo y estantería

El logo `images/logo-nova.png` es una copia de `interfaces/admin/img/Nova Logo.png` de la rama `origin/feature/AlvaroBaz`. La animación de entrada usa CSS y se omite cuando el navegador tiene activada la opción de movimiento reducido. La estantería muestra como máximo ocho resultados del filtro; el catálogo inferior conserva todos los modelos.
