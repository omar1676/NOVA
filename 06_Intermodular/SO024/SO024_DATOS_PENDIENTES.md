# SO024 · Datos que hay que acordar y prueba completa preparada

El caso común del enunciado es **«SO024 · Club Halcones · Modelo Runner X · 40 pares · tallas 38-46 · diseño personalizado»** (IM p. 5). El enunciado no da el color, el precio, el reparto por talla, la personalización, la fecha objetivo ni el contacto. Por eso hay **7 datos por acordar** en `06_Intermodular/SO024/caso-comun-SO024.md` §1, que deciden **los tres**. **[PENDIENTE (los tres): acordar los 7 datos y hacer el SO024 oficial.]**

> **Estado el 13/11/2026:** la cadena 18 → Java → 15 → PSP → 16 → Python está probada **de principio a fin sobre el árbol final**, pero **con datos PROVISIONALES** (`06_Intermodular/evidencias/regresion-final/06_so024_provisional/` y, la parte de PSP, `03_PSP/evidencias/so024_provisional/`): reparto **2/3/5/6/7/6/5/4/2**, precio **99,90 €**, color **«PROVISIONAL»**, stock **10** por talla y personalización «PROVISIONAL: escudo del Club Halcones en el lateral». El pedido se creó y se confirmó con los **métodos** de la pestaña «Nuevo pedido» (no con la ventana). Falta Odoo. **Nada de eso es un dato acordado** y no se puede presentar como el SO024 oficial.

Resultado de esa prueba: SO024 confirmado con 9 líneas, **40 pares y 3.996,00 €**; el stock de Runner X baja una sola vez por talla (queda en 8, 7, 5, 4, 3, 4, 5, 6 y 8); la auditoría la firma `admin.demo`; el 15 exporta 9 filas y 40 pares; PSP termina con **código 0** en los tres hijos y en el padre; y Python cuenta SO024 como **un solo pedido** de 9 líneas, 40 pares y 3.996 €. El 18 lanzado sin sus `-v` no inserta nada.

---

## 1. Los 7 datos

| # | Dato | Qué módulos lo usan y dónde | Valor provisional (13/11) | Valor acordado | Qué hay que tener en cuenta |
|---|---|---|---|---|---|
| 1 | **Pares de cada talla**, de la 38 a la 46 (en total, 40) | Web (formulario Custom), Odoo (líneas del pedido), Java («Nuevo pedido»), PSP (ficha) y Python (`lineas_pedido.csv`) | 2 / 3 / 5 / 6 / 7 / 6 / 5 / 4 / 2 | 38: __ · 39: __ · 40: __ · 41: __ · 42: __ · 43: __ · 44: __ · 45: __ · 46: __ | Enteros, que sumen **40**. Si alguna talla queda a 0, decir si «tallas 38-46» se cumple igual |
| 2 | **Color** de Runner X | `18_datos_so024.sql` (`-v color=`), Odoo (atributo Color), PSP (`color`) y Python (`stock.csv`) | `PROVISIONAL` | ______ | Un solo color: el 18 crea una sola variante. Máximo 30 caracteres (`variantes.color`) |
| 3 | **Precio base** de Runner X | `18_datos_so024.sql` (`-v precio=`, con punto: `119.90`), Odoo (precio del producto), Java y Python (importe) | 99,90 € (total 3.996,00 €) | ______ € | El importe del pedido será 40 × precio (el suplemento del color es 0). **[POR DECIDIR (los tres): con IVA o sin IVA, lo mismo en Odoo, AD y Python]** |
| 4 | **Stock inicial por talla** | `18_datos_so024.sql` (`-v stock=`) y, por separado, Odoo | 10 | ______ | El 18 pone **el mismo número en las 9 tallas**. Tiene que ser **como mínimo** los pares de la talla más pedida, o la confirmación fallará con «Stock insuficiente». Si se quiere enseñar la falta de stock con otro pedido (AD-114), que quede poco margen |
| 5 | **Texto de la personalización** | Web (campo Personalización), Odoo (nota del pedido), Java («Pedido Custom») y PSP (`personalizacion` y la ficha) | «PROVISIONAL: escudo del Club Halcones en el lateral» | ______ | Puede tener comas, comillas y saltos de línea: PostgreSQL y PSP los conservan |
| 6 | **SKU en Odoo** | Odoo («Referencia interna» de cada variante), PostgreSQL y PSP (`sku`) | `NOVA-114-38` … `NOVA-114-46` en las bases de prueba montadas con el orden del manual | ______ | **Ver §2: el SKU de PostgreSQL cambia según el orden de montaje** |
| 7 | **Número del pedido en Odoo** | Odoo, y la equivalencia en la memoria | — | ______ | Odoo numera los pedidos con su propia secuencia (S000…). Opciones: `SO024` en «Referencia del cliente» y apuntar la equivalencia, o ajustar la secuencia de Odoo. **[DUDA PARA EL PROFESOR (D4): ¿tiene que verse «SO024» literalmente en Odoo?]** |

**Otras decisiones que afectan a SO024** (no están entre los 7, pero conviene cerrarlas en la misma reunión). **[POR DECIDIR (los tres)]**:

| Decisión | Por qué importa | Fuente |
|---|---|---|
| Fecha objetivo de SO024 | El ejemplo del IM (p. 2) habla de «fecha objetivo». `pedidos.fecha_objetivo` existe en la base, pero el formulario Custom no la pide. **[DUDA PARA EL PROFESOR (D8)]** | `02_Acceso_Datos/sql/sneaker-factory-esquema.sql` |
| Contacto del Club Halcones | El 18 le pone un correo ficticio `@example.com`; Odoo y la web deberían usar el mismo | `18_datos_so024.sql` |
| Criterio de venta | AD cuenta todo lo no cancelado; Python también calcula «confirmados en adelante» | `04_Python/calidad_datos.md`, caso B |
| Hasta qué estado llega SO024 en la demo | `confirmado` en PostgreSQL (el portal del trabajador podría avanzarlo después hasta `entregado`); en Odoo, hasta la factura | `06_Intermodular/manuales/MANUAL_DEMOSTRACION.md` |
| Rango de tallas válidas | La base admite 20–55, los datos de demostración usan 40–44, la web 35–46 y SO024 38–46 | `04_Python/diccionario_datos.md`, punto 9 |

Cuando se acuerden, se apuntan en `06_Intermodular/SO024/caso-comun-SO024.md` §1 (el documento del equipo) y se dan por cerrados.

---

## 2. El SKU: por qué hay que fijarlo antes de pasárselo a Odoo

El 18 forma el SKU así: `'NOVA-' || v.id_variante || '-' || talla` (`02_Acceso_Datos/sql/18_datos_so024.sql`, paso 4). `id_variante` es un número automático (`GENERATED ALWAYS AS IDENTITY`) y **depende de todo lo que se cargó antes**. La variante de Runner X ha salido la 14 (Fase 0, solo con los scripts 1–17), la 26 (candidata del 12/11) y la **114** con el orden final del manual, que carga antes los 100 modelos del 21 (`06_Intermodular/evidencias/regresion-final/06_so024_provisional/SO024_PROVISIONAL_fabricacion.csv`). Además, las pruebas que acaban en ROLLBACK también gastan números. Si Odoo apunta un SKU y después se vuelve a montar la base de otra forma, dejarán de coincidir.

Propuesta, **sin cambiar ningún identificador**:

1. Montar la base del equipo **siempre en el mismo orden** (`06_Intermodular/manuales/MANUAL_INSTALACION.md` §3) y lanzar el 18 al final.
2. Leer los SKU reales de esa base y apuntarlos:
   ```powershell
   psql -U postgres -d nova_sneakers -c "SELECT s.talla, s.sku FROM producto_sku s JOIN variantes v USING (id_variante) JOIN modelos m USING (id_modelo) WHERE m.nombre = 'Runner X' ORDER BY s.talla;"
   ```
3. Pasárselos a Berme para la «Referencia interna» de cada variante en Odoo.
4. **No volver a montar la base del equipo** después de eso. Si hiciera falta, repetir los pasos 2 y 3.

Para una integración productiva, lo correcto sería un SKU fijo que no dependa de un número interno (`06_Intermodular/memoria/MEMORIA.md` §2.4, punto 2). Eso cambiaría el 18 y no se hace ahora.

---

## 3. Runner X no está en el catálogo de la web

**Cómo está hoy** (`01_Interfaces/cliente/`, sin cambios en esta rama):

- El catálogo tiene 100 modelos (`js/modelos.js`) y ninguno es Runner X. No hay ninguna foto de Runner X en `images/`.
- La sección Custom ya nombra el caso: «Ejemplo de pedido: SO024 · Club Halcones · Runner X · 40 pares de la talla 38 a la 46 con diseño personalizado» (`index.html`, línea 293), y el campo Modelo tiene el texto de ayuda «Ej.: Runner X» (línea 330).
- El campo Modelo es **texto libre** con sugerencias (`<datalist>`) que `custom.js` rellena con los 100 nombres de `modelos.js`. Se puede escribir «Runner X», pero no sale en las sugerencias.
- Runner X **sí existe en PostgreSQL** (lo crea el 18), y el 21 no lo toca. La web y la base se unen **por el nombre** (`01_Interfaces/cliente/README.md`).

**Propuesta (recomendada): Runner X solo como modelo del servicio Custom, sin añadirlo al catálogo.**

1. En `js/custom.js`, añadir a las sugerencias del campo Modelo una lista aparte con los modelos que solo se hacen bajo pedido, con un único nombre: **`Runner X`**, escrito exactamente igual que `modelos.nombre` en el 18. No se toca `modelos.js`.
2. En `index.html`, dentro de `#custom`, una tarjeta breve: «Runner X · modelo de running para clubes, solo bajo pedido · tallas 38 a 46». Sin precio hasta que se acuerde el dato 3, y con el precio acordado después.
3. No se añade ninguna referencia ni SKU a la web: el identificador del pedido sigue sin mostrarse (el IM lo deja como opcional, IM-ITG-10).

**Por qué así:**

- **No cambia ningún identificador ni ningún dato definitivo:** el nombre ya es el de la base, y los 100 modelos, sus nombres y sus pruebas siguen igual.
- **Evita un problema real:** si Runner X entrara en `modelos.js`, la tienda (ampliación) lo pondría a la venta, porque está en PostgreSQL, y un cliente de la web podría gastar el stock que necesita SO024.
- **Coherencia** (IM-ITG-12 y 15): el modelo del caso común aparece en la web con el mismo nombre que en Odoo y en PostgreSQL.

**Lo que habría que tocar después:**

- La comprobación «el campo Modelo sugiere los 100 modelos del catálogo» de la prueba de Interfaces en Edge (`06_Intermodular/evidencias/regresion-final/05_web/02_interfaces.txt`) contaría 101: hay que cambiarla para que compruebe «los 100 del catálogo y Runner X».
- Volver a pasar las pruebas de la web (`01_Interfaces/memoria/ESTRATEGIA_PRUEBAS_INTERFACES.md` §4).
- **[POR DECIDIR (los tres): si se hace. Este documento solo lo propone; no se ha cambiado ningún archivo de la web.]**

**Alternativas descartadas:**

| Alternativa | Por qué no |
|---|---|
| Añadir Runner X a `modelos.js` como un modelo más | Saldría en el catálogo y en la tienda; necesita foto; cambia el número de modelos de las pruebas |
| Dejarlo como está (se escribe a mano) | Funciona, pero el modelo del caso común no aparece en la web: es una incoherencia que señala `06_Intermodular/rubricas/MATRIZ_RUBRICAS.md` (IM-ITG-12) |

---

## 4. La prueba completa, paso a paso

Se hace **dos veces**: primero en una **base de ensayo** (para no gastar el stock de la buena) y después, el día de la demo o antes de grabar las evidencias, en la **base del equipo**. Comandos de PowerShell desde la raíz del repositorio; las contraseñas las piden los scripts y Java. La versión provisional de esta misma prueba, hecha por script el 13/11, está en `06_Intermodular/evidencias/regresion-final/06_so024_provisional/`: sirve para comparar lo que tiene que salir.

### 4.0 Antes

- [ ] Los 7 datos del §1 acordados y apuntados en `06_Intermodular/SO024/caso-comun-SO024.md`.
- [ ] Base montada en el orden de `06_Intermodular/manuales/MANUAL_INSTALACION.md` §3, **sin** el 18 todavía.

```powershell
$BD = "nova_so024_ensayo"     # el día de la demo: nova_sneakers
$PRECIO = "___"; $COLOR = "___"; $STOCK = "___"   # los valores acordados (precio con punto)
```

### 4.1 Datos de SO024 en PostgreSQL (script 18)

```powershell
psql -U postgres -d $BD -v ON_ERROR_STOP=1 -v precio=$PRECIO -v color=$COLOR -v stock=$STOCK -f 02_Acceso_Datos\sql\18_datos_so024.sql
psql -U postgres -d $BD -c "SELECT s.talla, s.sku, e.cantidad FROM producto_sku s JOIN variantes v USING (id_variante) JOIN modelos m USING (id_modelo) JOIN existencias e USING (id_producto_sku) WHERE m.nombre = 'Runner X' ORDER BY s.talla;"
```

**Esperado:** salida 0; 9 filas (tallas 38 a 46), cada una con su SKU y `$STOCK` pares. En la base del equipo: apuntar los SKU y dárselos a Berme (§2).

### 4.2 Alta y confirmación desde la ventana de Java

1. `02_Acceso_Datos\java\conexion.properties` apuntando a `$BD`.
2. `02_Acceso_Datos\java\ejecutar.bat` → entrar como `tienda.demo`.
3. «Nuevo pedido»: referencia `SO024`, cliente Club Halcones, «Pedido Custom» con la personalización acordada, y una línea de Runner X por talla con los pares acordados. Crear.
4. «Consultas»: filtrar por Club Halcones, ver el detalle y **confirmar**.
5. Entrar como `admin.demo` → «Ver auditoría».

**Comprobación en SQL:**

```powershell
psql -U postgres -d $BD -c "SELECT p.referencia, p.estado, p.cantidad_total, p.importe_total, count(*) AS lineas, sum(l.subtotal) AS suma_lineas FROM pedidos p JOIN linea_pedido l USING (id_pedido) WHERE p.referencia = 'SO024' GROUP BY 1, 2, 3, 4;"
psql -U postgres -d $BD -c "SELECT s.talla, e.cantidad FROM existencias e JOIN producto_sku s USING (id_producto_sku) JOIN variantes v USING (id_variante) JOIN modelos m USING (id_modelo) WHERE m.nombre = 'Runner X' ORDER BY s.talla;"
psql -U postgres -d $BD -c "SELECT le.accion, u.username, le.fecha_hora FROM log_eventos le LEFT JOIN usuarios u USING (id_usuario) WHERE le.tabla_afectada = 'pedidos' AND le.id_registro = (SELECT id_pedido FROM pedidos WHERE referencia = 'SO024') ORDER BY le.id_evento;"
```

**Esperado:** `SO024 | confirmado | 40 | 40 × precio | 9 | 40 × precio`; el stock de cada talla = `$STOCK` − los pares de esa talla (baja **una sola vez**); en la auditoría, `ALTA` y `CAMBIO_ESTADO` de `tienda.demo`. Capturas de cada pantalla de Java para la memoria (AD-81).

### 4.3 Exportación para PSP (script 15)

```powershell
New-Item -ItemType Directory -Force salidas | Out-Null; cd salidas
psql -U postgres -d $BD -v referencia=SO024 -f ..\02_Acceso_Datos\sql\15_exportar_fabricacion.sql
Import-Csv fabricacion_psp.csv | Measure-Object -Property cantidad -Sum | Select-Object Count, Sum
cd ..
```

**Esperado:** dos `PASS`; `Count` = 9 y `Sum` = 40.

### 4.4 PSP

```powershell
cd psp
javac -encoding UTF-8 -d clases *.java pruebas\*.java src\Psp\*.java
java -cp clases ProcesadorPedidosCustom ..\salidas\fabricacion_psp.csv
type salidas\ficha_taller_SO024.txt
cd ..
```

**Esperado:** los tres pasos con `codigo 0`, «9 combinaciones de modelo, color y talla; 9 tallas; 40 pares» y `Resultado: CORRECTO (codigo 0). Pedido SO024 procesado`. La ficha con el color, la personalización y los pares acordados.

### 4.5 Exportación para Python (script 16) y conciliación

En la base de ensayo, a una carpeta aparte (para no tocar `entrada_acc`):

```powershell
New-Item -ItemType Directory -Force salidas\csv16 | Out-Null; cd salidas\csv16
psql -U postgres -d $BD -f ..\..\02_Acceso_Datos\sql\16_exportar_csv_dashboard.sql
cd ..\..\04_Python
.venv\Scripts\python.exe main.py --modo real --entrada ..\salidas\csv16 --salida ..\salidas\python_so024
Select-String -Path ..\salidas\python_so024\pedidos_unicos.csv -Pattern ",SO024,"
cd ..
```

**Para que haya conciliación**, en el mismo momento que el 16 hay que sacar también P-A, P-B y P-C (y N-1, N-2 y N-3) con `psql --csv` a `conciliacion_sql\` dentro de la carpeta de entrada, como explica `04_Python/conciliacion_sql.md` («De dónde salen los resultados SQL»). En la prueba provisional del 13/11 no se sacaron, y Python lo dijo: «PENDIENTE: faltan los resultados SQL… No se da por buena ninguna cifra sin compararla» (`06_Intermodular/evidencias/regresion-final/06_so024_provisional/05_python_main.txt`).

En la base del equipo, a `04_Python\entrada_acc\`: cambiar la primera línea de `ORIGEN.txt` a `Tipo: REAL` (con la fecha y la base de la que sale) y regenerar las consultas de `conciliacion_sql\` **en el mismo momento**. **[PENDIENTE (los tres): esta es la exportación REAL que falta para Python.]**

**Esperado:** dos `PASS` en el 16; **una sola fila** de SO024 en `pedidos_unicos.csv`, con 9 líneas y 40 pares; y, con las consultas sacadas a la vez, la conciliación con SQL coincide.

### 4.6 Dashboard: antes y después

1. Con el dashboard abierto **antes** del paso 4.5, apuntar (o capturar) pedidos, pares e importe de la pestaña Dirección.
2. Exportar (4.5) y esperar al siguiente ciclo de 60 s.
3. Capturar otra vez: un pedido más y 40 pares más, estado «Correcto» y origen «REAL».

Estas capturas son las de «antes y después» que pide Python (PY-216).

### 4.7 Odoo (Berme)

**[PENDIENTE (Berme)]**

1. Crear SO024 según `05_Odoo/CHECKLIST_ODOO_BERME.md` §5, con los mismos datos.
2. Exportarlo con la cabecera de PSP (`05_Odoo/CHECKLIST_ODOO_BERME.md` §10) y pasárselo a PSP:
   ```powershell
   cd psp
   java -cp clases ProcesadorPedidosCustom ..\05_Odoo\exportaciones\SO024_odoo.csv
   cd ..
   ```
   **Esperado:** la misma ficha que en 4.4.

### 4.8 Comprobación final

Rellenar la tabla de `06_Intermodular/SO024/caso-comun-SO024.md` §3 con lo que ha salido en cada sitio:

| Talla | Odoo | PostgreSQL | Java | Ficha de PSP | `lineas_pedido.csv` |
|---|---|---|---|---|---|
| 38 … 46 | | | | | |
| **Total** | **40** | **40** | **40** | **40** | **40** |

### 4.9 Evidencias que hay que guardar

Propuesta: en `06_Intermodular/evidencias/so024/` (al lado de la provisional, `06_Intermodular/evidencias/regresion-final/06_so024_provisional/`, que se quedará como ensayo). **[POR DECIDIR (los tres): la carpeta y quién hace cada paso.]**

- [ ] Salida del 18 y los SKU de Runner X.
- [ ] Capturas de Java: alta, detalle, confirmación y auditoría.
- [ ] Salida de las tres consultas SQL del 4.2.
- [ ] `fabricacion_psp.csv`, la salida de PSP, `ficha_taller_SO024.txt` y `registro_psp.txt`.
- [ ] Los cinco CSV del 16, las consultas de `conciliacion_sql\`, `ORIGEN.txt` y la salida de `main.py`.
- [ ] Capturas del dashboard antes y después.
- [ ] Capturas de Odoo y `SO024_odoo.csv`.
- [ ] La tabla del §4.8 rellenada.

Al sustituir la evidencia provisional, actualizar también `03_PSP/evidencias/so024_provisional/README.md`, que dice que hay que repetirla con los datos acordados.
