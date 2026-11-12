# NOVA Sneakers · Web cliente

Abre `index.html` en un navegador moderno. No hace falta instalar librerías ni compilar el proyecto.

## Dónde está cada cosa

- `index.html`: el contenido de la página: cabecera, estantería, catálogo, ficha, servicio Custom y contacto.
- `css/inicio.css`: colores, tamaños, distribución y diseño para móviles.
- `js/modelos.js`: lista de zapatillas, con su nombre, colección y rutas de imágenes, y `datosColeccion`, con el precio orientativo, las tallas y la descripción de cada colección.
- `js/inicio.js`: muestra las zapatillas y controla los filtros, las búsquedas y la ficha.
- `js/custom.js`: suma los pares por talla del formulario Custom y simula el envío.
- `images/favicon.png`: favicon de 64×64. Es la estrella del logo, recortada de `logo-nova.png`.
- `images/nova/street/`: imágenes de la colección Street.
- `images/nova/luxe/`: imágenes de la colección Luxe.
- `images/nova/casual/`, `hombre/`, `mujer/` y `unisex/`: imágenes transparentes del ZIP de 80 modelos.

Cada modelo de `modelos.js` tiene dos rutas: `imagen` se muestra en la estantería, en la ficha y en la miniatura del probador; `imagenCatalogo` aparece en el catálogo inferior. En Street y Luxe, `imagen` apunta a los archivos `-sinfondo.webp`, recortados a partir de las fotos originales de 1254 px del ZIP de 20 modelos, e `imagenCatalogo` a la foto que conserva su fondo de estudio. Esos modelos llevan `catalogoConFondo: true` para que la tarjeta amplíe la foto hasta llenar su hueco (`object-fit: cover`) en vez de mostrarla como un recuadro dentro de otro; las imágenes sin fondo se muestran enteras (`object-fit: contain`). Si se quiere usar la misma foto en ambos sitios, se puede poner la misma ruta en los dos campos y quitar `catalogoConFondo`. Las rutas son relativas a `index.html`.

Los archivos acabados en `-recorte.webp` ya no se usan: al quitarles el fondo blanco se borraron también las partes blancas y crema de varias zapatillas (por ejemplo, Street 02, 04 y 07 y Luxe 02, 05 y 08), que se veían blanquecinas o casi invisibles sobre la estantería. Para recortar fotos nuevas con fondo claro no basta con un umbral de claridad: hay que rellenar el fondo desde los bordes de la imagen, para no agujerear las zonas claras de la zapatilla, y quitar aparte la sombra que queda bajo la suela.

Para añadir una zapatilla, copia un objeto de `modelos.js`, cambia su nombre y las rutas, y comprueba que los archivos existen. Usa `street`, `luxe`, `casual`, `hombre`, `mujer` o `unisex` en el campo `coleccion` para que aparezca en su filtro. El número mostrado en los filtros se calcula a partir de la lista.

Los nombres y las imágenes son una presentación visual; todavía no están vinculados a los productos de la base de datos.

El precio, las tallas y la descripción son comunes a todos los modelos de una colección y se cambian solo en `datosColeccion`. Son **provisionales**: el equipo tiene que acordarlos para que coincidan con Odoo y PostgreSQL.

## Formulario Custom

Pide club o equipo, persona de contacto, email, modelo, personalización y pares de cada talla, de la 38 a la 46; el teléfono y los colores son opcionales. El navegador comprueba los campos obligatorios, el formato del email y que las cantidades sean números enteros no negativos; `custom.js` suma el total y exige al menos un par. No hay servidor: el envío es una **simulación**, no se envía ningún dato y no se registra ningún pedido. SO024 aparece solo como ejemplo de pedido.

## Pendiente de integración

No hay `contrato-pedido.md` en esta rama ni una API o exportación de Odoo disponible. Antes de habilitar la compra hay que acordar identificadores de producto, variante y SKU, tallas, stock disponible, precios y moneda, datos de cliente y dirección, impuestos, referencia asignada por Odoo y estados. El servidor deberá volver a validar precio y stock al confirmar. La web no genera referencias SO ni registra pedidos: el formulario Custom solo simula el envío de la solicitud.

El SQL identifica la talla con `producto_sku` y la personalización como texto a nivel del pedido. El caso CUSTOM-40 contiene varias líneas de tallas y una misma descripción de personalización. Debe acordarse cómo representar varias personalizaciones distintas en una compra sin perder información. PSP actualmente consume el CSV de fabricación de PostgreSQL, no una exportación de Odoo. La confirmación SQL descuenta stock y la cancelación lo devuelve; crear una línea no reserva stock.

Faltan carrito, checkout, autenticación, historial y personalizador. No se presentan como funcionalidades operativas mientras faltan los datos y contratos necesarios.

## Navegación entre secciones

En móvil se puede desplazar la página normalmente. En la franja inferior de la estantería, deslizar hacia arriba lleva al catálogo; también se puede pulsar «Desliza o ver catálogo». El enlace funciona con ratón y teclado. En el catálogo se puede buscar y filtrar por colección.

## Probador conceptual

Desde la ficha se puede abrir el probador, escoger cualquiera de los modelos del catálogo, ver las imágenes que existen con esa zapatilla puesta y cambiar de escenario. La altura (120–220 cm) cambia la escala visual; el peso (30–200 kg) se conserva en el campo y ambos valores se redondean en intervalos de 5. El peso no cambia ni determina automáticamente la complexión; la figura se escoge de forma independiente. Las imágenes son aproximaciones y no sirven para recomendar talla.

La zapatilla seleccionada se muestra por separado. Hay ejemplos generados con NOVA Street 01 puesta y dos poses con NOVA Casual 01 puesta; cada imagen solo se habilita para su producto y es una aproximación visual. Las poses, prendas y cuerpos forman parte de cada imagen y no se combinan libremente. Pelo, tono de piel y el resto de zapatillas puestas siguen pendientes. Las imágenes generadas están en `images/probador/`.

Si una zapatilla todavía no tiene foto puesta, el probador no muestra a nadie con otro calzado: enseña la zapatilla sola, en grande, sobre el escenario elegido, con el aviso «Aún no hay foto con este modelo puesto». La pose queda desactivada y la altura no se aplica. Las personas con calzado genérico (`persona-01` a `persona-04` y las figuras `modelo-base`, `modelo-delgado`, `modelo-ancho`, `modelo-urbano` y `modelo-deportivo`) siguen en `images/probador/`, pero no se ofrecen porque mostrarían unas zapatillas distintas de la elegida.

Las vistas de Casual 02 y 03 usan escenas completas generadas con una aproximación de cada zapatilla. Son imágenes fijas: altura y escenario quedan desactivados mientras se muestran.

## Logo y estantería

El logo `images/logo-nova.png` es una copia de `interfaces/admin/img/Nova Logo.png` de la rama `origin/feature/AlvaroBaz`. La animación de entrada usa CSS y se omite cuando el navegador tiene activada la opción de movimiento reducido. La estantería muestra como máximo ocho resultados del filtro; el catálogo inferior conserva todos los modelos.
