# NOVA Sneakers · Web cliente

Abre `index.html` en un navegador moderno. No hace falta instalar librerías ni compilar el proyecto: el escaparate, el catálogo, la ficha, el probador, Custom y Contacto funcionan así.

Para **comprar**, la web tiene que abrirse desde el servidor: `http://127.0.0.1:3000/tienda/` (ver `servidor-admin/README.md`). Sin servidor, la ficha avisa de que la tienda online no está disponible.

## Dónde está cada cosa

- `index.html`: el contenido de la página: cabecera, estantería, catálogo, ficha, servicio Custom y contacto.
- `css/inicio.css`: colores, tamaños, distribución y diseño para móviles.
- `js/modelos.js`: lista de zapatillas, con su nombre, colección y rutas de imágenes, y `datosColeccion`, con el precio orientativo, las tallas y la descripción de cada colección.
- `js/inicio.js`: muestra las zapatillas y controla los filtros, las búsquedas y la ficha.
- `js/custom.js`: suma los pares por talla del formulario Custom y simula el envío.
- `js/tienda.js` y `css/tienda.css`: la tienda online (catálogo real, carrito, cuenta, pedido y «Mis pedidos»).
- `images/favicon.png`: favicon de 64×64. Es la estrella del logo, recortada de `logo-nova.png`.
- `images/nova/street/`: imágenes de la colección Street.
- `images/nova/luxe/`: imágenes de la colección Luxe.
- `images/nova/casual/`, `hombre/`, `mujer/` y `unisex/`: imágenes transparentes del ZIP de 80 modelos.

Cada modelo de `modelos.js` tiene dos rutas: `imagen` se muestra en la estantería, en la ficha y en la miniatura del probador; `imagenCatalogo` aparece en el catálogo inferior. En Street y Luxe, `imagen` apunta a los archivos `-sinfondo.webp`, recortados a partir de las fotos originales de 1254 px del ZIP de 20 modelos, e `imagenCatalogo` a la foto que conserva su fondo de estudio. Esos modelos llevan `catalogoConFondo: true` para que la tarjeta amplíe la foto hasta llenar su hueco (`object-fit: cover`) en vez de mostrarla como un recuadro dentro de otro; las imágenes sin fondo se muestran enteras (`object-fit: contain`). Si se quiere usar la misma foto en ambos sitios, se puede poner la misma ruta en los dos campos y quitar `catalogoConFondo`. Las rutas son relativas a `index.html`.

Los archivos acabados en `-recorte.webp` ya no se usan: al quitarles el fondo blanco se borraron también las partes blancas y crema de varias zapatillas (por ejemplo, Street 02, 04 y 07 y Luxe 02, 05 y 08), que se veían blanquecinas o casi invisibles sobre la estantería. Para recortar fotos nuevas con fondo claro no basta con un umbral de claridad: hay que rellenar el fondo desde los bordes de la imagen, para no agujerear las zonas claras de la zapatilla, y quitar aparte la sombra que queda bajo la suela.

Para añadir una zapatilla, copia un objeto de `modelos.js`, cambia su nombre y las rutas, y comprueba que los archivos existen. Usa `street`, `luxe`, `casual`, `hombre`, `mujer` o `unisex` en el campo `coleccion` para que aparezca en su filtro. El número mostrado en los filtros se calcula a partir de la lista.

El **nombre** es lo que une un modelo de la web con PostgreSQL. Doce modelos (el 01 y el 02 de cada colección) están en la base gracias a `21_catalogo_web.sql` y se pueden comprar. Los otros 88 se ven, pero salen como «No disponible».

El precio, las tallas y la descripción de `datosColeccion` son comunes a todos los modelos de una colección. Son el precio **orientativo** de los modelos que no están a la venta. En los doce de la tienda, el precio, el color, las tallas y el stock vienen de PostgreSQL; `21_catalogo_web.sql` usó esos mismos precios y tallas. Son **provisionales**: el equipo tiene que acordarlos para que coincidan con Odoo.

## Formulario Custom

Pide club o equipo, persona de contacto, email, modelo, personalización y pares de cada talla, de la 38 a la 46; el teléfono y los colores son opcionales. El navegador comprueba los campos obligatorios, el formato del email y que las cantidades sean números enteros no negativos; `custom.js` suma el total y exige al menos un par. No hay servidor: el envío es una **simulación**, no se envía ningún dato y no se registra ningún pedido. SO024 aparece solo como ejemplo de pedido.

## Tienda online

`js/tienda.js` pide al servidor el catálogo real y se encarga del resto:

- **Barra bajo la cabecera:** «Iniciar sesión» (o el saludo, «Mis pedidos» y «Cerrar sesión») y «Carrito (n)». No toca la cabecera, que sigue igual en todos los anchos.
- **Tarjetas del catálogo:** «Disponible», «Agotado» o «No disponible», también en su `aria-label`.
- **Ficha:** color, talla y cantidad. Las tallas agotadas salen tachadas y desactivadas, y no se puede pedir más de lo que hay en stock ni más de 10 pares por talla.
- **Carrito:** se guarda en `localStorage` con **solo el SKU y la cantidad**. Al cargar la página se vuelve a pedir el catálogo: lo que ya no existe o se ha agotado se quita, y lo cuenta. El total del carrito es una estimación; el que vale lo calcula PostgreSQL.
- **Cuenta:** el inicio de sesión es el **diálogo de Álvaro** (commit `52a8800`), con su HTML, su CSS y su JavaScript. Lo único que cambia son las dos últimas líneas de su `submit`, que ahora llaman al servidor, y un enlace a «Crear una cuenta». Las cuentas de cliente son distintas de las de los trabajadores.
- **Pedido en tres pasos:**
  1. Entrega: la dirección es obligatoria.
  2. Pago simulado: el pedido ya está creado como pendiente y se ven las líneas y el total calculados por PostgreSQL. Hay dos botones, «Simular pago aceptado» y «Simular pago rechazado». **No se pide ningún dato bancario y no se cobra nada.**
  3. Resultado: si se acepta, el pedido queda confirmado y se descuenta el stock; si se rechaza o se cancela, el pedido queda cancelado. Si se cierra la ventana sin pagar, el pedido se cancela.
- **Mis pedidos:** el historial del cliente, con el detalle de cada pedido.

## Pendiente de integración

Los precios, las tallas y el stock de los 12 modelos de la tienda son provisionales y hay que acordarlos con Odoo, igual que los impuestos y la correspondencia entre la referencia `WEB-…` de la tienda y la de Odoo. La web no genera referencias SO. El formulario Custom sigue simulando el envío de la solicitud.

El SQL identifica la talla con `producto_sku` y la personalización como texto a nivel del pedido. El caso CUSTOM-40 contiene varias líneas de tallas y una misma descripción de personalización. Debe acordarse cómo representar varias personalizaciones distintas en una compra sin perder información. PSP actualmente consume el CSV de fabricación de PostgreSQL, no una exportación de Odoo. La confirmación SQL descuenta stock y la cancelación lo devuelve; crear una línea no reserva stock.

Carrito, checkout, cuentas e historial ya funcionan con PostgreSQL (ver «Tienda online»). Falta el personalizador.

## Navegación entre secciones

En móvil se puede desplazar la página normalmente. En la franja inferior de la estantería, deslizar hacia arriba lleva al catálogo; también se puede pulsar «Desliza o ver catálogo». El enlace funciona con ratón y teclado. En el catálogo se puede buscar y filtrar por colección.

## Probador conceptual

Desde la ficha se puede abrir el probador, escoger cualquiera de los modelos del catálogo, ver las imágenes que existen con esa zapatilla puesta y cambiar de escenario. La altura (120–220 cm) cambia la escala visual; el peso (30–200 kg) se conserva en el campo y ambos valores se redondean en intervalos de 5. El peso no cambia ni determina automáticamente la complexión; la figura se escoge de forma independiente. Las imágenes son aproximaciones y no sirven para recomendar talla.

La zapatilla seleccionada se muestra por separado. Hay ejemplos generados con NOVA Street 01 puesta y dos poses con NOVA Casual 01 puesta; cada imagen solo se habilita para su producto y es una aproximación visual. Las poses, prendas y cuerpos forman parte de cada imagen y no se combinan libremente. Pelo, tono de piel y el resto de zapatillas puestas siguen pendientes. Las imágenes generadas están en `images/probador/`.

Si una zapatilla todavía no tiene foto puesta, el probador no muestra a nadie con otro calzado: enseña la zapatilla sola, en grande, sobre el escenario elegido, con el aviso «Aún no hay foto con este modelo puesto». La pose queda desactivada y la altura no se aplica. Las personas con calzado genérico (`persona-01` a `persona-04` y las figuras `modelo-base`, `modelo-delgado`, `modelo-ancho`, `modelo-urbano` y `modelo-deportivo`) siguen en `images/probador/`, pero no se ofrecen porque mostrarían unas zapatillas distintas de la elegida.

Las vistas de Casual 02 y 03 usan escenas completas generadas con una aproximación de cada zapatilla. Son imágenes fijas: altura y escenario quedan desactivados mientras se muestran.

## Logo y estantería

El logo `images/logo-nova.png` es una copia de `interfaces/admin/img/Nova Logo.png` de la rama `origin/feature/AlvaroBaz`. La animación de entrada usa CSS y se omite cuando el navegador tiene activada la opción de movimiento reducido. La estantería muestra como máximo ocho resultados del filtro; el catálogo inferior conserva todos los modelos.
