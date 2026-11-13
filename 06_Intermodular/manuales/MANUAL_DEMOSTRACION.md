# NOVA Sneakers · Manual de demostración (caso SO024)

Guion breve con los pasos exactos para enseñar el caso de uso completo (IM-COM-19), sobre la rama final `integracion/candidata-2` (13/11/2026). Sigue el orden del guion sugerido del IM (§11): empresa → web → Odoo → exportación → PSP → evidencias → cierre, con Acceso a Datos y Python en medio, que es por donde pasa hoy el pedido.

**Recorrido:** Web Custom → Odoo → Java/PostgreSQL → script 15 → PSP → script 16 → Python/Streamlit → cierre.

**Reglas para la demo:**

- **Contraseñas:** no se escriben en ningún sitio visible ni se dicen en voz alta. Se usa la contraseña de demostración acordada (**[DUDA PARA EL PROFESOR (D12): por qué medio se le comunica]**). Antes de proyectar, cerrar `conexion.properties` y `.env`.
- **Base:** la base del equipo, montada en el orden de `MANUAL_INSTALACION.md` §3 (scripts 01 a 23) y con SO024 **todavía sin crear**. Nada de bases de prueba con pedidos `PRUEBA-*` a la vista.
- **Datos de SO024:** los 7 acordados (`06_Intermodular/SO024/SO024_DATOS_PENDIENTES.md`). **[PENDIENTE (los tres): acordar los 7 datos. Hoy solo hay datos PROVISIONALES; si se hace la demo con ellos, hay que decirlo en voz alta.]**
- **Tiempos:** orientativos, para unos 15 minutos en total. **[DUDA PARA EL PROFESOR (D1 y D12): cuánto tiempo da el tribunal; ajustarlos a eso.]**

**Usuarios de demostración** (solo por nombre):

| Sistema | Usuario | Rol | Para qué |
|---|---|---|---|
| Java / PostgreSQL | `tienda.demo` | comercial | Crear y confirmar SO024 |
| Java / PostgreSQL | `admin.demo` | administrador | Ver la auditoría y gestionar usuarios |
| Java / PostgreSQL | `taller.demo` | trabajador | Enseñar una operación denegada |
| Odoo | **[PENDIENTE (Berme): los usuarios de Odoo]** | comercial, producción, almacén y administración | Venta, fabricación, entrega y factura |
| Login único web (ampliación) | `admin.demo` | administrador | Entra al panel de administración. Solo en la parte opcional |
| Login único web (ampliación) | `taller.demo` | trabajador | Entra al portal del trabajador. Solo en la parte opcional |
| Login único web (ampliación) | `tienda.demo` | comercial | Recibe «Acceso denegado»: un comercial trabaja con la aplicación Java y no tiene panel web |

---

## Paso 0. Preparación (el día antes y 30 minutos antes)

- [ ] Base del equipo montada desde cero en el orden del manual (01 a 23); 13 lanzado (contraseñas) y 18 lanzado con los datos acordados (`psql … -v precio=… -v color=… -v stock=… -f 02_Acceso_Datos\sql\18_datos_so024.sql`).
- [ ] Apuntado el SKU de cada talla de Runner X en esa base y pasado a Berme para Odoo (`06_Intermodular/SO024/SO024_DATOS_PENDIENTES.md` §2).
- [ ] Odoo arrancado, con el cliente y el producto creados y SO024 preparado según `05_Odoo/CHECKLIST_ODOO_BERME.md`. **[PENDIENTE (Berme): Odoo entero]**
- [ ] `03_PSP` compilado (`MANUAL_INSTALACION.md` §5) y la carpeta `salidas\` creada en la raíz.
- [ ] `04_Python\entrada_acc\` con la última exportación **de la base del equipo**, `ORIGEN.txt` con `Tipo: REAL` y P-A, P-B, P-C y N-1 a N-3 regenerados a la vez (`04_Python/conciliacion_sql.md`). **[PENDIENTE (los tres): la exportación REAL; hoy `entrada_acc` es de PRUEBA.]**
- [ ] Ventanas abiertas: la web (`py -m http.server 8000 --bind 127.0.0.1` → `http://127.0.0.1:8000/01_Interfaces/cliente/`), Odoo, la ventana de login de Java (`02_Acceso_Datos\java\ejecutar.bat`), una consola PowerShell en la raíz y el dashboard (`04_Python\.venv\Scripts\streamlit.exe run app_dashboard.py`, desde `04_Python`). El dashboard también se puede enseñar dentro del panel de administración, en «Análisis de datos».
- [ ] **El dashboard abierto desde antes** de exportar SO024, para enseñar el antes y el después.
- [ ] Para la parte opcional: `servidor-admin` arrancado con `npm start` (`MANUAL_INSTALACION.md` §7) y el navegador en `http://127.0.0.1:3000/login.html`.
- [ ] Plan B a mano: capturas de cada paso (las de las carpetas `evidencias/` de cada asignatura, `04_Python/evidencias/dashboard/` y las de Odoo cuando existan) y los resultados de la regresión del 13/11 (`06_Intermodular/evidencias/regresion-final/README.md`).

---

## Paso 1. La empresa y el problema (1 min)

- **Qué abrir:** la portada de la web o la primera diapositiva de `06_Intermodular/defensa/PRESENTACION.pptx`.
- **Qué decir:** NOVA Sneakers fabrica zapatillas y hace pedidos personalizados para clubes. El caso que vamos a seguir es el del enunciado: **SO024, Club Halcones, 40 pares de Runner X, tallas 38 a 46, diseño personalizado**. Odoo es el núcleo; PSP es un ayudante; PostgreSQL y Python son los módulos de Acceso a Datos y de Python sobre el mismo pedido.
- **Evidencia:** `06_Intermodular/memoria/MEMORIA.md` §1 y el diagrama del §2.1.

## Paso 2. Web: el club pide sus zapatillas (2 min)

- **Qué abrir:** `http://127.0.0.1:8000/01_Interfaces/cliente/` en escritorio y, después, en modo móvil (F12 → icono de dispositivo → un móvil de 390 px).
- **Usuario:** ninguno (es la web pública).
- **Qué hacer:**
  1. Menú → **Catálogo**: filtrar por una colección y abrir una ficha (precio, descripción y tallas).
  2. Menú → **Custom**: leer los cuatro pasos del servicio.
  3. Rellenar el formulario con los datos de SO024: club «Club Halcones», contacto y email ficticios, modelo «Runner X», la personalización acordada y los pares acordados de cada talla de la 38 a la 46.
  4. Pulsar «SIMULAR ENVÍO».
- **Qué tiene que salir:** el total se va sumando al escribir (**40 pares**) y aparece «SIMULACIÓN · Solicitud preparada para Club Halcones: Runner X, 40 pares (tallas …). No se ha enviado ningún dato ni se ha registrado ningún pedido.».
- **Qué contar:** el envío es una simulación, como permite el IM («formulario o prototipo»). La solicitud la recoge el comercial, que la registra en Odoo.
- **Evidencia:** `06_Intermodular/evidencias/regresion-final/05_web/02_interfaces.txt` (136/136, 13/11) y las capturas `01_Interfaces/evidencias/web/capturas/*_04` a `*_06`.
- **Si falla:** si la página no carga, abrir `01_Interfaces/cliente/index.html` directamente; si no hay navegador, enseñar las capturas de escritorio y móvil. Ojo: «Runner X» no está en las sugerencias del campo Modelo (no está en el catálogo de la web): se escribe a mano (`06_Intermodular/SO024/SO024_DATOS_PENDIENTES.md` §3).

## Paso 3. Odoo: la venta y la fabricación (3 min) · [PENDIENTE (Berme)]

- **Qué abrir:** Odoo **[PENDIENTE (Berme): URL de la instancia o de la máquina virtual]**.
- **Usuario:** **[PENDIENTE (Berme): el comercial de Odoo]**; después, el de producción, el de almacén y el de administración.
- **Qué hacer:**
  1. Localizar al cliente Club Halcones (y la oportunidad, si CRM entra en el alcance).
  2. Enseñar el presupuesto y confirmarlo como pedido de venta: líneas de Runner X por talla, con la «Referencia del cliente» = SO024.
  3. Enseñar la orden de fabricación con su lista de materiales, el albarán de salida y la factura (o su simulación), según el alcance.
  4. Exportar a CSV las líneas del pedido.
- **Qué tiene que salir:** el mismo cliente, el mismo producto y variantes, las mismas cantidades por talla (40 en total) y la trazabilidad pedido → fabricación → entrega → factura.
- **Evidencia:** las capturas y la exportación de `05_Odoo/CHECKLIST_ODOO_BERME.md`. **[PENDIENTE (Berme): presupuesto, SO024, fabricación, entrega y factura, con sus capturas y la exportación CSV]**
- **Ojo:** el conector de Odoo de Berme (`servidor-admin/odoo.js`) está en el servidor, pero **desactivado** sin `ODOO_*` y sin probar contra ningún Odoo. No se enseña como si funcionara.
- **Si falla:** si Odoo no arranca, enseñar las capturas del recorrido y la exportación guardadas, y decirlo: «Odoo no está disponible ahora; esta es la evidencia del día …». PostgreSQL y PSP siguen funcionando sin Odoo, porque no dependen de él.

## Paso 4. Java y PostgreSQL: el mismo pedido en el módulo de Acceso a Datos (3 min)

- **Qué abrir:** la ventana de login de Java.
- **Usuario:** `tienda.demo` (comercial).
- **Qué hacer:**
  1. Pestaña **«Nuevo pedido»**: referencia `SO024`, cliente Club Halcones, marcar «Pedido Custom» con la personalización acordada, y una línea por talla de Runner X con los pares acordados. Crear.
  2. En **«Consultas»**, filtrar por cliente Club Halcones y estado `pendiente`, pulsar «Buscar / Consultar» y ver el detalle: 9 líneas y el importe que ha calculado la base.
  3. **Confirmar** el pedido.
  4. Volver a consultar con el estado `confirmado` y pulsar «Limpiar filtros».
  5. Cerrar sesión y entrar como `admin.demo`: «Ver auditoría».
- **Qué tiene que salir:**
  - Pedido con **40 pares** e importe = 40 × precio acordado (calculado por PostgreSQL, no por Java).
  - Al confirmar, cada talla baja **una sola vez** los pares de esa talla.
  - En la auditoría: `ALTA` y `CAMBIO_ESTADO` de SO024, con `tienda.demo` y la hora.
  - En `salidas\actividad_sneaker.txt` (carpeta de `conexion.properties`), una línea por cada acción.
- **Comprobación en SQL** (opcional, solo lectura, en la consola):
  ```powershell
  psql -U postgres -d nova_sneakers -c "SELECT p.referencia, p.estado, p.cantidad_total, p.importe_total, count(*) AS lineas, sum(l.subtotal) AS suma_lineas FROM pedidos p JOIN linea_pedido l USING (id_pedido) WHERE p.referencia = 'SO024' GROUP BY 1, 2, 3, 4;"
  psql -U postgres -d nova_sneakers -c "SELECT s.talla, e.cantidad FROM existencias e JOIN producto_sku s USING (id_producto_sku) JOIN variantes v USING (id_variante) JOIN modelos m USING (id_modelo) WHERE m.nombre = 'Runner X' ORDER BY s.talla;"
  ```
- **Qué contar:** Java no calcula importes, ni toca el stock, ni escribe la auditoría: lo hacen los triggers. El stock se descuenta al confirmar, no al crear.
- **Evidencia:** `06_Intermodular/evidencias/regresion-final/02_java_psp/02_pruebas_rubrica.txt` (47/47, 13/11), `06_Intermodular/evidencias/regresion-final/06_so024_provisional/00_cadena.txt` (cadena PROVISIONAL, con los métodos de «Nuevo pedido» desde un lanzador) y las capturas de `02_Acceso_Datos/evidencias/java-swing/` (ventanas Swing, 76/76 el 13/11).
- **Si falla:**
  - «La cuenta no tiene contrasena establecida»: falta el 13.
  - «Stock insuficiente»: el stock del 18 es menor que los pares de alguna talla. No se cambia nada a mano: se explica que la base protege el stock (es la prueba B) y se sigue con el pedido de respaldo **[POR DECIDIR (los tres): si se prepara un SO024 ya confirmado en una segunda base]**.
  - Sin conexión: enseñar las capturas y la batería de `02_pruebas_rubrica.txt`.

## Paso 5. Exportación del pedido para PSP (script 15) (1 min)

- **Qué abrir:** la consola PowerShell, en la carpeta `salidas\` de la raíz.
- **Usuario:** el administrador de PostgreSQL que instaló la base.
- **Qué hacer:**
  ```powershell
  cd salidas
  psql -U postgres -d nova_sneakers -v referencia=SO024 -f ..\02_Acceso_Datos\sql\15_exportar_fabricacion.sql
  type fabricacion_psp.csv
  cd ..
  ```
- **Qué tiene que salir:** dos `PASS` (el pedido está confirmado, con 9 líneas, 9 tallas y 40 pares) y un `fabricacion_psp.csv` con la cabecera `referencia,sku,cliente,modelo,color,personalizacion,talla,cantidad` y **9 filas** de SO024.
- **Qué contar:** es la «copia o exportación de los datos del pedido» del IM. Hoy sale de PostgreSQL; cuando exista, saldría igual de Odoo con las mismas 8 columnas.
- **Evidencia:** `03_PSP/evidencias/so024_provisional/SO024_PROVISIONAL_fabricacion.csv` y `02_exportacion_15_SO024_PROVISIONAL.txt` (PROVISIONAL).
- **Si falla:** si el pedido no está confirmado o no suma 40, el script se para y **no toca el CSV anterior**. Volver al paso 4 y confirmarlo.

## Paso 6. PSP: el proceso coordinador y sus tres hijos (2 min)

- **Qué abrir:** la consola, en `03_PSP\`.
- **Usuario:** ninguno (PSP no se conecta a nada).
- **Qué hacer:**
  ```powershell
  cd 03_PSP
  java -cp clases ProcesadorPedidosCustom ..\salidas\fabricacion_psp.csv
  type salidas\ficha_taller_SO024.txt
  java -cp clases ProcesadorPedidosCustom datos\prueba_cantidad_cero.csv
  type salidas\registro_psp.txt
  cd ..
  ```
- **Qué tiene que salir:**
  - `Paso 1 ValidadorPedidoCustom: codigo 0` → `OK;SO024;9;40`.
  - `Paso 2 Psp.AnalizadorTallas: codigo 0` → `9 combinaciones de modelo, color y talla; 9 tallas; 40 pares`.
  - `Paso 3 GeneradorFichaTaller: codigo 0` → `Resultado: CORRECTO (codigo 0). Pedido SO024 procesado`.
  - La ficha con Club Halcones, la personalización y los pares por talla, y al final «No sustituye a la orden de fabricación de Odoo».
  - Con el archivo erróneo: `codigo 2`, `ERROR;La cantidad del registro … tiene que ser mayor que cero`, `PEDIDO RECHAZADO (codigo 2)` y ninguna ficha nueva.
- **Qué contar:** el padre lanza cada hijo con `ProcessBuilder`, le pasa los datos por stdin y lee stdout y stderr por separado; mira el código de salida y que la respuesta empiece por `OK;` del mismo pedido; si un hijo tarda más de 10 s, lo cancela. **La ficha se relaciona con el pedido de Odoo por la referencia SO024.**
- **Evidencia:** `06_Intermodular/evidencias/regresion-final/02_java_psp/04_psp_pruebas.txt` (27/27, 13/11), `03_PSP/evidencias/so024_provisional/03_ejecucion_psp_SO024_PROVISIONAL.txt` y `03_PSP/memoria/DOCUMENTACION_PSP.md`.
- **Si falla:** «No se encuentra la clase Psp.AnalizadorTallas» (código 3) quiere decir que no se compiló `src\Psp`: volver a compilar con `javac -encoding UTF-8 -d clases *.java pruebas\*.java src\Psp\*.java`.

## Paso 7. Exportación para Python (script 16) y dashboard (2 min)

- **Qué abrir:** la consola, en `04_Python\entrada_acc\`, y el dashboard (`http://localhost:8501`), que ya estaba abierto desde antes.
- **Usuario:** el administrador de PostgreSQL para la exportación; el dashboard no tiene login.
- **Qué hacer:**
  1. En el dashboard, apuntar las cifras de **Dirección** (pedidos, pares e importe) antes de exportar.
  2. Exportar:
     ```powershell
     cd 04_Python\entrada_acc
     psql -U postgres -d nova_sneakers -f ..\..\02_Acceso_Datos\sql\16_exportar_csv_dashboard.sql
     cd ..\..
     ```
     (y regenerar P-A, P-B, P-C y N-1 a N-3 como dice `04_Python/conciliacion_sql.md`).
  3. Esperar al siguiente ciclo (60 s como máximo) o pulsar «Actualizar ahora».
- **Qué tiene que salir:** estado «Correcto», nueva hora de «última actualización válida», **un pedido más y 40 pares más**, sin contar las 9 líneas como 9 pedidos. En la pestaña **Calidad**, la calidad por tabla y la conciliación con SQL. La etiqueta de origen en verde, «REAL».
- **Qué contar:** Python no se conecta a PostgreSQL: solo lee CSV. Cada minuto vuelve a leer, validar y recalcular aunque no cambie nada; si no se exporta, las cifras no cambian. La pestaña Predicción es un laboratorio con datos **sintéticos** y lo dice.
- **Evidencia:** `04_Python/evidencias/dashboard/` (capturas del 9 y 10/11, y las del caso K del 13/11: tres ciclos de 60 s en Edge) y `04_Python/memoria/INFORME_TECNICO_PYTHON.md`.
- **Si falla:**
  - «Error de carga»: falta un CSV o está a medias; volver a lanzar el 16. El último resultado válido se ve con el interruptor, rotulado DESACTUALIZADO.
  - Si en vez de «REAL» sale «PRUEBA», `ORIGEN.txt` no se ha actualizado: decirlo.
  - Sin dashboard: `.venv\Scripts\python.exe main.py` en la consola y enseñar `outputs\real\pedidos_unicos.csv`.

## Paso 8. Cierre: el mismo pedido en todas partes (1 min)

- **Qué abrir:** la tabla del §3 de `06_Intermodular/SO024/caso-comun-SO024.md`, rellenada con lo que se ha visto (Odoo, PostgreSQL, Java, ficha de PSP y `lineas_pedido.csv`): las mismas cantidades por talla y **40** en todas las columnas.
- **Qué contar:**
  - **Qué es del ERP y qué es auxiliar:** Odoo lleva la venta, la fabricación, la entrega y la factura; PSP solo valida, agrupa y prepara una ficha; PostgreSQL y Python trabajan sobre el mismo pedido para sus módulos (`06_Intermodular/memoria/MEMORIA.md` §2.3).
  - **Qué haría falta para una integración productiva:** exportación automática desde Odoo, SKU estables y compartidos, una sola fuente de stock y PSP como servicio (`06_Intermodular/memoria/MEMORIA.md` §2.4).
  - **Pruebas, problemas y mejoras:** `06_Intermodular/memoria/MEMORIA.md` §7 y §8, y `06_Intermodular/evidencias/regresion-final/README.md`.

---

## Demostraciones de cada módulo (para la defensa de cada asignatura)

### Acceso a Datos (lo que pide AD-114 a AD-116, además del paso 4)

Con la ventana Java:

1. **Tres consultas seguidas** con filtros distintos (sin filtros, cliente y estado, y una sin coincidencias) y abrir `actividad_sneaker.txt`: tres líneas nuevas con fecha, usuario, filtros y número de filas.
2. **Otro perfil:** entrar como `taller.demo` y pulsar «Ver auditoría» → «Acceso denegado». Intentar crear un pedido → denegado.
3. **Cancelar** un pedido confirmado (uno de prueba, no SO024) y ver que el stock vuelve y la auditoría apunta `BAJA_LOGICA`.
4. **Falta de stock:** crear otro pedido de Runner X que pida más pares de una talla de los que quedan y confirmarlo → «Stock insuficiente…», el pedido sigue pendiente y el stock no cambia.
5. **Indicadores:** pestaña Indicadores (pedidos, pares, importe y pedidos por estado; modelos y tallas; stock bajo con un umbral).
6. **CSV filtrado:** exportar la tabla filtrada y abrir `consulta_pedidos.csv`.
7. **JSON:** como `admin.demo`, crear un usuario en la pestaña Usuarios y abrir `usuarios_sneaker.json`: aparece, sin contraseña. Desactivarlo: cambia su estado y no se pierde nadie.
8. **ROLLBACK:** en psql, `BEGIN;` + una compra + `ROLLBACK;` y comprobar que ni el pedido ni su evento de auditoría quedan (o enseñar la prueba D de `06_Intermodular/evidencias/regresion-final/02_java_psp/02_pruebas_rubrica.txt`).

### Python (lo que se examina en la defensa: PY-189)

1. Dashboard abierto durante **tres ciclos de 60 s** sin cambios: cambia «Última comprobación», no cambian las cifras y el registro de la pestaña Calidad tiene una fila por ciclo. Ya se hizo así en Edge el 13/11 (caso K: `04_Python/evidencias/dashboard/caso_k_*`).
2. **CSV defectuoso** (en una **copia** de `entrada_acc`, nunca en la original): quitar `pedidos.csv` → «Error de carga» y el último resultado DESACTUALIZADO; devolverlo → se recupera.
3. **Filtros:** periodo, modelo, talla, tipo, estado y cliente combinados; esperar un ciclo y ver que siguen puestos y que la pestaña no cambia; «Restablecer filtros»; descargar un CSV filtrado que cuadra con la tarjeta y lleva sus metadatos (fecha de corte, función, reglas y filas de origen).
4. **Laboratorio:** cambiar el origen a «Sintéticos limpios» → todo en violeta y rotulado SINTÉTICO; pestaña Predicción con el MAE y el RMSE del baseline y de la regresión.

---

## Demostración opcional: ampliaciones

Solo si sobra tiempo y el tribunal lo pide. **No sustituyen a nada obligatorio.** Necesitan `servidor-admin` arrancado (`MANUAL_INSTALACION.md` §7) y los scripts 19 a 23 en la base. Las pruebas de estas ampliaciones están en `06_Intermodular/evidencias/regresion-final/05_web/` (compra 139/139, reparto 29/29, login y portal 82/82 y Ethereal 16/16, todas del 13/11).

| Ampliación | Qué abrir | Usuario | Qué enseñar | Si falla |
|---|---|---|---|---|
| Tienda online | `http://127.0.0.1:3000/tienda/` | Un cliente de prueba registrado en la tienda (correo `@example.com`) | Ficha con su bloque de compra → carrito → entrega → «Simular pago aceptado» → «Mis pedidos». El stock lo descuenta PostgreSQL | Si dice «no disponible», faltan las variables `TIENDA_*` del `.env` |
| Login único del personal | `http://127.0.0.1:3000/login.html` | `admin.demo`, `taller.demo` y `tienda.demo` | El administrador entra al panel; el trabajador, al portal; el comercial recibe «Acceso denegado: … no tiene ningún panel web» | «Usuario o contraseña incorrectos» con la contraseña buena: falta el 13. Tras 5 fallos, 429 durante 5 minutos |
| Panel de administración | `http://127.0.0.1:3000/admin.html` (tras el login) | `admin.demo` | Dashboard, pedidos, inventario y auditoría leídos de PostgreSQL | Sin internet no hay iconos ni gráficos |
| Reparto | Panel → Pedidos | `admin.demo` | «Marcar en reparto» en el pedido web confirmado → en «Mis pedidos» del cliente sale «En reparto» | Lanzar el 22 en esa base |
| Recibo por correo | La consola del servidor y «Mis pedidos» | El cliente de prueba | Con `CORREO_PROVEEDOR=ethereal`, el enlace «Ver recibo de prueba (Ethereal)» | Sin red, la compra sigue bien y solo se apunta el error |
| Probador | Ficha → probador | — | Elegir zapatilla, escenario y complexión; cambiar peso y estatura | Es una aproximación visual: no recomienda tallas |
| Portal del trabajador (Berme) | `http://127.0.0.1:3000/trabajador/` (tras el login) | `taller.demo` | Resumen; Pedidos: «Avanzar estado» en un pedido confirmado que **no sea SO024** (por ejemplo, una compra web), que pasa a `en_preparacion`, y el stock no cambia; Inventario: cambiar una cantidad y «Guardar»; Personalizados. Después, como `admin.demo`, la Auditoría del panel enseña el `CAMBIO_ESTADO` y el `CAMBIO_STOCK` a nombre de `taller.demo` | Si da error al entrar, falta el 23. No se avanza SO024: el 15 solo exporta pedidos `confirmado` (`15_exportar_fabricacion.sql:131-135`). Sin internet el portal funciona sin iconos |
