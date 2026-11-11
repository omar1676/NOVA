# Odoo · Lista de tareas y capturas para Berme

Sistemas de Gestión Empresarial (módulo 0491). **[PENDIENTE (Berme): todo lo de esta lista.]** A 13/11/2026 **no hay ninguna evidencia de Odoo** en el repositorio (`05_Odoo/` solo tiene `.gitkeep`). Esta lista cubre los 17 requisitos de SGE de `06_Intermodular/rubricas/MATRIZ_RUBRICAS.md` (IM-SGE-06 a 17 y 21, y RA1 a RA4), más la copia de seguridad (IM-COM-16) y el punto 4 de la memoria (IM-COM-24).

**Lo que ya hay de Berme en la rama** (anexo B de `06_Intermodular/memoria/MEMORIA.md`): el portal del trabajador, integrado y probado, y su conector con la API de Odoo, `servidor-admin/odoo.js`, integrado pero **desactivado** mientras falte alguna de `ODOO_URL`, `ODOO_DB` y `ODOO_API_KEY`. El conector **no se ha probado contra ningún Odoo** y no sustituye a nada de esta lista: el enunciado pide configurar Odoo y enseñar el flujo de SO024 en Odoo.

**Dónde se guarda cada cosa:**

- **Capturas:** `05_Odoo/capturas/NN_descripcion.png` (el número de la tabla del final). Sin contraseñas, sin claves de API y sin la barra del navegador con datos personales.
- **Exportación del pedido:** `05_Odoo/exportaciones/SO024_odoo.csv`.
- **Guía e incidencias:** `05_Odoo/README.md`.
- **Nada de contraseñas ni claves** en el repositorio. Si se usa la API, la clave va en `servidor-admin/.env`, que no se sube.

---

## 0. Antes de empezar (decisiones que no dependen solo de Berme)

- [ ] Los **7 datos de SO024** acordados entre los tres (`06_Intermodular/SO024/SO024_DATOS_PENDIENTES.md` §1). Sin ellos, el pedido de Odoo no coincidirá con el de PostgreSQL. **[PENDIENTE (los tres)]**
- [ ] **El SKU de cada talla de Runner X**, sacado de la base del equipo después de lanzar el 18 (`06_Intermodular/SO024/SO024_DATOS_PENDIENTES.md` §2). Es la «Referencia interna» de cada variante en Odoo. Con el orden de montaje del manual, en las bases de prueba sale la variante 114 (`NOVA-114-38` … `NOVA-114-46`), pero **vale el que salga en la base del equipo**.
- [ ] El **alcance** que pide el profesor: CRM sí o no, fabricación, inventario y facturación; máquina virtual o instancia; formato del backup. **[DUDA PARA EL PROFESOR (D5)]**
- [ ] El **nombre de la compañía**: «NOVA Sneakers» o «Sneaker Factory». **[DUDA PARA EL PROFESOR (D2)]**

**Reglas de identificadores** (`05_Odoo/recorrido-manual-odoo.md` §1, y las que usa tu conector `servidor-admin/odoo.js`):

- **SKU de PostgreSQL = «Referencia interna» (`default_code`) de la variante.**
- **`SO024` = «Referencia del cliente» (`client_order_ref`) del pedido de venta.** El número que ponga Odoo (S000…) se apunta como equivalencia.
- **Antes de crear nada, buscar** por «Referencia del cliente» = SO024, para no duplicar.

---

## 1. Entorno (IM-SGE-06, IM-SGE-08, RA1, RA2)

- [ ] Máquina virtual con Ubuntu (o la instancia que diga el profesor) y Odoo instalado y en marcha.
- [ ] Apuntar en `05_Odoo/README.md`: sistema operativo y versión, versión y edición de Odoo, gestor de datos (PostgreSQL y su versión), cómo se instaló (paso a paso, reproducible), aplicaciones instaladas (Ventas, Fabricación, Inventario, Facturación y, si entra, CRM) y la URL de acceso (sin contraseñas).
- [ ] Capturas 01 y 02.

## 2. Empresa, usuarios y roles (IM-SGE-09)

- [ ] Compañía configurada con el nombre acordado, dirección y logo (`01_Interfaces/cliente/images/logo-nova.png`).
- [ ] Un usuario por perfil, con datos ficticios y **sin contraseñas en el repositorio**:

| Perfil | Permisos mínimos | Nombre de usuario (lo elige Berme) |
|---|---|---|
| Comercial | Ventas (y CRM si entra) | ______ |
| Producción | Fabricación | ______ |
| Almacén | Inventario | ______ |
| Administración | Facturación y ajustes | ______ |

- [ ] Capturas 03 y 04.

## 3. Clientes y CRM (IM-SGE-10, IM-SGE-11)

- [ ] Contacto **Club Halcones** (empresa), con el mismo correo ficticio `@example.com` que le pone la base (`02_Acceso_Datos/sql/18_datos_so024.sql`).
- [ ] Al menos dos clientes ficticios más (IM-COM-04: varios clientes y pedidos).
- [ ] **Si CRM entra en el alcance:** oportunidad del Club Halcones que se convierte en presupuesto.
- [ ] Capturas 05 y 06.

## 4. Productos y variantes (IM-SGE-12)

- [ ] Producto **Runner X**, fabricado (ruta «Fabricar»), con el precio acordado.
- [ ] Atributo **Talla** con los valores **38 a 46** y el atributo **Color** con el color acordado → 9 variantes.
- [ ] En cada variante, **«Referencia interna» = el SKU de PostgreSQL** de esa talla.
- [ ] Opcional (ampliación, IM-SGE-05): ruta MTO para que la venta cree la orden de fabricación.
- [ ] Capturas 07 y 08.

## 5. Venta: presupuesto → pedido SO024 (IM-SGE-12, IM-SGE-17)

- [ ] Presupuesto para el Club Halcones: **una línea por talla** con los pares acordados (**40 en total**), el precio acordado y, en la nota, la personalización acordada.
- [ ] «Referencia del cliente» = **SO024**.
- [ ] Confirmar el presupuesto → pedido de venta. Apuntar el número que da Odoo: ______
- [ ] Capturas 09, 10 y 11.

## 6. Fabricación (IM-SGE-13)

- [ ] **Lista de materiales** de Runner X con componentes ficticios (los elige Berme: suela, piel, cordones, plantilla…).
- [ ] **Orden de fabricación** de SO024, con origen en el pedido de venta, y hacerla avanzar hasta «Hecho».
- [ ] Capturas 12, 13 y 14.

## 7. Inventario y entrega (IM-SGE-14)

- [ ] Stock inicial de componentes o de producto, según el flujo elegido.
- [ ] Movimientos de stock de la fabricación.
- [ ] Albarán de salida (entrega) de SO024 validado.
- [ ] Capturas 15 y 16.

## 8. Facturación (IM-SGE-15)

- [ ] Factura desde el pedido de venta (borrador o publicada), **o** una simulación documentada si la facturación no entra en el alcance. **[DUDA PARA EL PROFESOR (D5): qué cuenta como «simulación documentada»]**
- [ ] Usar el mismo criterio de IVA que el resto de bloques. **[POR DECIDIR (los tres): con o sin IVA, igual en Odoo, AD y Python; hoy en Python y en AD está «pendiente de confirmar»]**
- [ ] Captura 17.

## 9. Trazabilidad (IM-SGE-16, IM-SGE-21)

- [ ] Una captura del pedido de venta con sus documentos relacionados (fabricación, entrega y factura) visibles.
- [ ] Rellenar la columna «Odoo» de la tabla de `06_Intermodular/SO024/caso-comun-SO024.md` §3 (pares por talla).
- [ ] Captura 18.

## 10. Exportación CSV del pedido (RA3)

- [ ] Exportar desde Odoo las líneas de SO024 a `05_Odoo/exportaciones/SO024_odoo.csv`.
- [ ] **Mejor aún:** dejarlo con la cabecera exacta de PSP, para que PSP lo procese sin cambiar nada (`03_PSP/memoria/DOCUMENTACION_PSP.md` §9.3):

| Columna de PSP | Campo de Odoo |
|---|---|
| `referencia` | Referencia del cliente (SO024) |
| `sku` | Referencia interna de la variante |
| `cliente` | Cliente |
| `modelo` | Producto (Runner X) |
| `color` | Valor del atributo Color |
| `personalizacion` | Nota del pedido |
| `talla` | Valor del atributo Talla |
| `cantidad` | Cantidad |

- [ ] Probarlo desde `03_PSP\`, después de compilar (`javac -encoding UTF-8 -d clases *.java pruebas\*.java src\Psp\*.java`): `java -cp clases ProcesadorPedidosCustom ..\05_Odoo\exportaciones\SO024_odoo.csv` → código 0 y la misma ficha que con el CSV de PostgreSQL.
- [ ] Rellenar la **tabla de equivalencias** en `05_Odoo/README.md`: número de pedido de Odoo ↔ SO024, y SKU ↔ variante.
- [ ] Captura 19.

## 11. Adaptación a la empresa (RA4)

- [ ] Apuntar qué se ha adaptado y por qué: por ejemplo, el atributo Talla, la nota de personalización, vistas, filtros o campos de entrada. **[DUDA PARA EL PROFESOR (D5): qué adaptación espera]**

## 12. Copia de seguridad (IM-COM-16)

- [ ] Copia de la base de Odoo desde el gestor de bases de datos de Odoo (formato zip, con el *filestore*) o una instantánea de la máquina virtual.
- [ ] **No subirla al repositorio** (el plan del equipo prohíbe subir bases de datos y máquinas virtuales). Apuntar en `05_Odoo/README.md` su nombre, fecha, tamaño, huella SHA-256, dónde se guarda y cómo se restaura. **[DUDA PARA EL PROFESOR (D12): si el backup se entrega y dónde]**
- [ ] Probar a restaurarla una vez en otra base y apuntar el resultado.
- [ ] Captura 20.

## 13. Incidencias (RA1 a RA4: «documenta operaciones e incidencias»)

- [ ] En `05_Odoo/README.md`, una tabla: fecha, qué pasó, cómo se resolvió.

## 14. Memoria, punto 4 (IM-COM-24)

- [ ] Redactar `06_Intermodular/memoria/MEMORIA.md` §4 con los subapartados 4.1 a 4.13 que ya tiene preparados, usando estas capturas.

## 15. Si se usa el conector de la API (`servidor-admin/odoo.js`)

Hoy está integrado y **desactivado**; activarlo es opcional y no sustituye a nada de lo anterior.

- [ ] `ODOO_URL`, `ODOO_DB` y `ODOO_API_KEY` solo en `servidor-admin/.env`, que no se sube. Con las tres puestas, la consola del servidor dice al arrancar «Conector de Odoo configurado…». **Ojo:** el único que lo llama es `pedidos.js`, que no se monta (punto siguiente), así que configurarlo no basta para que se envíe nada.
- [ ] Usuario de Odoo con los permisos justos para lo que hace el conector.
- [ ] Las rutas de `servidor-admin/pedidos.js` (crear pedidos y enviarlos a Odoo) **no se montan**: escriben directamente en `pedidos` y en `log_eventos`, y en esta base ningún rol de la web puede hacerlo fuera de las funciones y los triggers. Para usarlas, habría que pasarlas a funciones `SECURITY DEFINER` con auditoría, como las de los scripts 22 y 23. **[REVISIÓN (Berme) en la PR: confirmar que está de acuerdo con dejarlas sin montar y con los cambios en sus archivos (`90c57e0`).]**
- [ ] Probar el conector contra el Odoo de la máquina virtual y guardar la prueba en `05_Odoo/`.
- [ ] Explicarlo en la memoria como un paso hacia la integración productiva (`06_Intermodular/memoria/MEMORIA.md` §2.4), no como requisito.

---

## Capturas que hay que aportar

| Nº | Archivo | Qué tiene que verse | Requisito |
|---|---|---|---|
| 01 | `01_entorno_vm.png` | La máquina virtual con Odoo en marcha (versión visible) | SGE-08, RA1 |
| 02 | `02_aplicaciones.png` | Las aplicaciones instaladas | SGE-06, RA2 |
| 03 | `03_compania.png` | La compañía configurada | SGE-09 |
| 04 | `04_usuarios.png` | Los cuatro usuarios y sus permisos | SGE-09 |
| 05 | `05_cliente.png` | El contacto Club Halcones | SGE-10 |
| 06 | `06_oportunidad.png` | La oportunidad (solo si hay CRM) | SGE-11 |
| 07 | `07_producto.png` | Runner X con sus atributos | SGE-12 |
| 08 | `08_variantes.png` | Las 9 variantes con su «Referencia interna» | SGE-12 |
| 09 | `09_presupuesto.png` | El presupuesto con sus líneas | SGE-12 |
| 10 | `10_pedido_confirmado.png` | El pedido de venta con «Referencia del cliente» = SO024 | SGE-12, 17 |
| 11 | `11_lineas_pedido.png` | Las líneas: tallas, cantidades y total | SGE-12 |
| 12 | `12_lista_materiales.png` | La lista de materiales | SGE-13 |
| 13 | `13_orden_fabricacion.png` | La orden de fabricación con su origen | SGE-13 |
| 14 | `14_fabricacion_hecha.png` | La orden terminada | SGE-13 |
| 15 | `15_movimientos_stock.png` | Los movimientos de inventario | SGE-14 |
| 16 | `16_entrega.png` | El albarán de salida validado | SGE-14 |
| 17 | `17_factura.png` | La factura o la simulación | SGE-15 |
| 18 | `18_trazabilidad.png` | El pedido con sus documentos relacionados | SGE-16, 21 |
| 19 | `19_exportacion.png` | La exportación del CSV | RA3 |
| 20 | `20_copia_seguridad.png` | La copia de seguridad hecha | COM-16 |
