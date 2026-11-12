# NOVA Sneakers · Manual de instalación y ejecución

Cómo instalar, montar la base de datos, arrancar cada parte y pasar las pruebas, para que otro equipo pueda repetirlo (IM-COM-05).

- **Probado** en Windows 11 el **13/11/2026**, siguiendo este mismo manual sobre una copia nueva del repositorio y una base de datos nueva y vacía. El resultado está en `06_Intermodular/evidencias/regresion-final/08_manual_instalacion/`.
- **Rama:** `integracion/candidata-2` (la candidata final; se propone a `main` con una pull request). Cuando se fusione, todo esto vale igual desde `main`.
- **Convenciones.** Los comandos son de **PowerShell** y se lanzan desde la **raíz del repositorio**, salvo que se diga otra cosa.
- **Contraseñas.** **Nunca se escribe ninguna en un archivo del repositorio.** Los scripts las piden por teclado, y los archivos de configuración que las llevan (`02_Acceso_Datos/java/conexion.properties` y `servidor-admin/.env`) están en el `.gitignore`. Cada equipo elige las suyas al instalar. **[DUDA PARA EL PROFESOR (D12): por qué medio se le dan las contraseñas de demostración el día de la defensa.]**

---

## 1. Requisitos

| Software | Versión | Para qué | Comprobar |
|---|---|---|---|
| PostgreSQL | **17** (probado con la 17.11), con `psql` o pgAdmin 4 | Base de datos | `psql --version` |
| JDK | **17** (probado con el 17.0.12) | Aplicación Java y PSP | `javac -version` |
| Driver JDBC de PostgreSQL | **42.7.14**, como `02_Acceso_Datos/java/lib/postgresql-42.7.14.jar` | Aplicación Java | El archivo existe. **No se sube al repositorio:** hay que descargarlo (por ejemplo, de la web oficial del driver de PostgreSQL o de Maven Central) |
| Python | **3.12 o superior** (probado con 3.13.5), con un entorno virtual `.venv` | Análisis y dashboard | `py -3.13 --version` |
| Dependencias de Python | pandas 3.1.1, numpy 2.5.4, matplotlib 3.11.2, scikit-learn 1.9.1 y streamlit 1.67.0 | Ídem | `04_Python/requirements.txt` |
| Node | **20.6 o superior** (probado con 24.15) | Solo para las ampliaciones: panel, portal del trabajador y tienda | `node --version` |
| Dependencias de Node | express 5.3.0, pg 8.23.1 y nodemailer 10.5.0 (versiones exactas del `package-lock.json`) | Ídem | `servidor-admin/package.json` |
| Navegador | Microsoft Edge o Chrome actual | Web, panel, portal, tienda y dashboard | — |
| Odoo | **[PENDIENTE (Berme): versión, edición y máquina virtual]** | ERP | — |

Si `javac` o `psql` no están en el PATH, para la sesión actual:

```powershell
$env:PATH = "C:\Program Files\Java\jdk-17.0.12\bin;C:\Program Files\PostgreSQL\17\bin;" + $env:PATH
$env:PGCLIENTENCODING = "UTF8"
```

`PGCLIENTENCODING=UTF8` evita que las tildes salgan mal en la consola de Windows. Es lo que usaron las pruebas.

Si PostgreSQL no está en `localhost:5432` (por ejemplo, un servidor de pruebas en otro puerto), se indica una vez para toda la sesión, y `psql` lo usa en todos los comandos de este manual:

```powershell
$env:PGHOST = "localhost"
$env:PGPORT = "5432"
```

---

## 2. Obtener el código

```powershell
git clone https://github.com/omar1676/NOVA.git
cd NOVA
git switch main
```

El repositorio es privado: el profesor necesita que le den acceso. Hasta que se fusione la pull request, la candidata final está en su propia rama (la que indica la pull request); se cambia `main` por el nombre de esa rama.

---

## 3. Montar la base de datos

**Importante:** sobre una base **nueva y vacía**. Los scripts de instalación no comprueban si los objetos ya existen. Para repetir la instalación, se borra la base y se crea otra (`02_Acceso_Datos/documentacion/README.md` §3).

```powershell
psql -U postgres -c "CREATE DATABASE nova_sneakers;"
```

**El número del archivo no es el orden de ejecución.** Este es el orden probado el 13/11 desde cero, con salida 0 en todos (`06_Intermodular/evidencias/regresion-final/01_sql/01_montaje_01_23.txt`):

| Paso | Script | Qué hace | ¿Admin? | ¿Pide contraseña? | Resultado esperado |
|---|---|---|---|---|---|
| 1 | `sneaker-factory-esquema.sql` (el «01») | Esquema `extensiones` con pgcrypto, 13 tablas, claves e índices | **Sí** | No | Salida 0 |
| 2 | `04_xnova.sql` | `configuraciones_xnova` y sus columnas en `linea_pedido` | No | No | Salida 0 |
| 3 | `02_funciones.sql` | Las 14 funciones de negocio y de sesión | No | No | Salida 0 |
| 4 | `03_triggers.sql` | Los 5 triggers de cálculo y control | No | No | Salida 0 |
| 5 | `05_datos_prueba.sql` | Datos de demostración | No | No | Salida 0 |
| 6 | `07_seguridad.sql` | Los 4 roles `nova_*` y sus permisos | **Sí** | No | Salida 0 |
| 7 | `08_auditoria.sql` | Las 5 funciones y 5 triggers de auditoría | No | No | Salida 0 |
| 8 | `17_usuario_java.sql` | El usuario `java_nova` de la aplicación Java | **Sí** | **Sí** (`java_nova`) | Salida 0 |
| 9 | `19_usuario_web.sql` | `panel_lectura` y el usuario `web_nova` del servidor | **Sí** | **Sí** (`web_nova`) | Salida 0 |
| 10 | `06_consultas.sql` | Las 8 consultas (solo leen). La 3 (`HAVING`) devuelve **1 fila** con los datos de prueba: `NOVA-4-43` | No | No | Salida 0 |
| 11 | `09_pruebas.sql` | **Batería de pruebas** | No | No | **91 PASS y 1 ERROR previsto** (S4b) |
| 12 | `10_caso_custom.sql` | Caso del club, dentro de un ROLLBACK | No | No | 6 PASS |
| 13 | `11_dml_ejemplos.sql` | INSERT, UPDATE, DELETE y 6 rechazos | No | No | 12 PASS |
| 14 | `12_consultas_panel.sql` | Consultas del panel Java y del caso N de Python | No | No | 1 PASS |
| 15 | `13_activar_usuarios.sql` | Contraseñas de `admin.demo`, `taller.demo` y `tienda.demo` | **Sí** | **Sí** (las tres, y otra vez la de `admin.demo` para probar el login) | Salida 0 |
| 16 | `14_caso_custom_persistente.sql` | Guarda el pedido `CUSTOM-40` | No | **Sí** (la de `tienda.demo`) | 9 PASS |
| 17 | `15_exportar_fabricacion.sql` | CSV para PSP | No | No | 2 PASS y `fabricacion_psp.csv` |
| 18 | `16_exportar_csv_dashboard.sql` | Los 5 CSV de Python | No | No | 2 PASS y 5 CSV |
| 19 | `20_tienda_web.sql` | Tienda (ampliación): `cuentas_cliente`, 5 funciones, `tienda_web` y `tienda_nova` | **Sí** | **Sí** (`tienda_nova`) | Salida 0 |
| 20 | `21_catalogo_web.sql` | Los 100 modelos de la web (ampliación) | No | No | 1 PASS |
| 21 | `22_reparto_panel.sql` | Botón «Marcar en reparto» del panel (ampliación) | **Sí** | No | Salida 0 (se puede repetir) |
| 22 | `23_portal_trabajador.sql` | Portal del trabajador (ampliación): rol `portal_trabajador` y sus 2 funciones | **Sí** | No | Salida 0 (se puede repetir) |
| 23 | `18_datos_so024.sql` | Club Halcones y Runner X para SO024 | No | No, pero necesita `-v precio=… -v color=… -v stock=…` | Ver `06_Intermodular/SO024/SO024_DATOS_PENDIENTES.md`. **Sin los `-v` no inserta nada** |

Resumen: **la instalación (01–08, con el 17 y el 19), la batería (06 y 09–12), las contraseñas y el caso Custom (13 y 14), las exportaciones (15 y 16), las ampliaciones (20, 21, 22 y 23) y, al final, SO024 (18)**. Las pruebas 09–16 suman **123 PASS, 0 FAIL y 1 ERROR previsto**.

**Por qué este orden** (`02_Acceso_Datos/documentacion/README.md` §3):

- El 04 va antes del 02 porque `realizar_compra_xnova` usa `configuraciones_xnova`.
- El 08 va después de los datos para que `log_eventos` empiece vacía.
- **El 09 va antes del 13, el 18, el 20 y el 21:** A1 y A2 comprueban que las cuentas llegan sin contraseña, y P1, P2 y S1 cuentan los objetos de la instalación original. Si no, dan `FAIL` con razón.
- El 14 va después del 13 porque inicia sesión como `tienda.demo`.
- El 22 va después del 09, el 19 y el 20. El 23, después del 19 y del 22.
- El 18 va al final. **Ojo:** el SKU de Runner X se forma con el número de su variante (`NOVA-<id_variante>-<talla>`), y ese número depende de todo lo que se ha cargado antes. Para que el SKU sea siempre el mismo, la base del equipo se monta siempre en este orden.

**Comandos.** Los de instalación, con `ON_ERROR_STOP`, para que se paren al primer error. La batería, **sin** él, porque el 09 provoca un error a propósito.

```powershell
$SQL = "02_Acceso_Datos\sql"
foreach ($f in "sneaker-factory-esquema","04_xnova","02_funciones","03_triggers","05_datos_prueba","07_seguridad","08_auditoria") {
  psql -U postgres -d nova_sneakers -v ON_ERROR_STOP=1 -f "$SQL\$f.sql"
}
psql -U postgres -d nova_sneakers -f "$SQL\17_usuario_java.sql"      # pide la contraseña de java_nova
psql -U postgres -d nova_sneakers -f "$SQL\19_usuario_web.sql"       # pide la de web_nova
foreach ($f in "06_consultas","09_pruebas","10_caso_custom","11_dml_ejemplos","12_consultas_panel") {
  psql -U postgres -d nova_sneakers -f "$SQL\$f.sql" | Tee-Object -FilePath "$f.log"
}
psql -U postgres -d nova_sneakers -f "$SQL\13_activar_usuarios.sql" | Tee-Object -FilePath "13_activar_usuarios.log"   # pide las tres contraseñas y otra vez la de admin.demo
psql -U postgres -d nova_sneakers -f "$SQL\14_caso_custom_persistente.sql" | Tee-Object -FilePath "14_caso_custom_persistente.log"   # pide la de tienda.demo
```

Los `.log` quedan en la carpeta actual y están en el `.gitignore`. Para contar el resultado de la batería (después de las exportaciones de abajo, que también dejan su `.log`):

```powershell
foreach ($p in "PASS","FAIL","ERROR") { "$p $((Select-String -Path *.log -Pattern $p -CaseSensitive).Count)" }
```

Tiene que salir `PASS 123`, `FAIL 0` y `ERROR 1`. **Hace falta `-CaseSensitive`:** sin él, `Select-String` no distingue mayúsculas y cuenta también «password» o «error provocado a propósito» (en la prueba del 13/11 salieron 142 y 5). Las pruebas de los scripts 14, 15 y 16 no imprimen `FAIL`: si algo no cuadra, lanzan un error y psql termina con un código distinto de 0.

**Exportaciones.** Dejan los archivos **en la carpeta desde la que se lanza psql**:

```powershell
New-Item -ItemType Directory -Force salidas | Out-Null
cd salidas
psql -U postgres -d nova_sneakers -f ..\02_Acceso_Datos\sql\15_exportar_fabricacion.sql     # fabricacion_psp.csv (CUSTOM-40)
cd ..\04_Python\entrada_acc
psql -U postgres -d nova_sneakers -f ..\..\02_Acceso_Datos\sql\16_exportar_csv_dashboard.sql | Tee-Object -FilePath ..\..\16_exportar_csv_dashboard.log   # los 5 CSV
cd ..\..
```

(El 15 se lanza igual, con `| Tee-Object -FilePath ..\15_exportar_fabricacion.log`, si se quiere contar también en la batería.)

**El 16 sobrescribe los cinco CSV de `entrada_acc` que trae el repositorio:** `git status` los marca como modificados. Para volver a los del repositorio: `git restore 04_Python/entrada_acc`. Después de exportar a `entrada_acc`, hay que poner en la primera línea de `04_Python/entrada_acc/ORIGEN.txt` el tipo: `Tipo: PRUEBA` (base de prueba) o `Tipo: REAL` (base del equipo). Los CSV que trae el repositorio son de una base de PRUEBA. **[PENDIENTE (los tres): la exportación REAL de la base del equipo.]**

**Ampliaciones:**

```powershell
psql -U postgres -d nova_sneakers -v ON_ERROR_STOP=1 -f "$SQL\20_tienda_web.sql"     # pide la de tienda_nova
psql -U postgres -d nova_sneakers -v ON_ERROR_STOP=1 -f "$SQL\21_catalogo_web.sql"
psql -U postgres -d nova_sneakers -v ON_ERROR_STOP=1 -f "$SQL\22_reparto_panel.sql"
psql -U postgres -d nova_sneakers -v ON_ERROR_STOP=1 -f "$SQL\23_portal_trabajador.sql"
```

**SO024**, solo cuando los tres hayan acordado los datos (ver `06_Intermodular/SO024/SO024_DATOS_PENDIENTES.md`):

```powershell
psql -U postgres -d nova_sneakers -v ON_ERROR_STOP=1 -v precio=<precio> -v color=<color> -v stock=<stock> -f "$SQL\18_datos_so024.sql"
```

---

## 4. Aplicación Java (Acceso a Datos)

1. Descargar el driver y dejarlo como `02_Acceso_Datos\java\lib\postgresql-42.7.14.jar`. **La carpeta `lib` no viene en el repositorio** (el `.jar` está en el `.gitignore`): hay que crearla antes, con `New-Item -ItemType Directory -Force 02_Acceso_Datos\java\lib`.
2. Copiar `02_Acceso_Datos\java\conexion.properties.ejemplo` como `02_Acceso_Datos\java\conexion.properties` y escribir la contraseña de `java_nova` (la del paso 8):
   ```
   url=jdbc:postgresql://localhost:5432/nova_sneakers
   usuario=java_nova
   contrasena=
   carpeta_salida=salidas
   ```
3. Arrancar: `02_Acceso_Datos\java\ejecutar.bat` (compila y abre la ventana de login).
4. Entrar con `admin.demo`, `tienda.demo` o `taller.demo` y la contraseña que se puso en el paso 15.

Los archivos `actividad_sneaker.txt`, `usuarios_sneaker.json` y `consulta_pedidos.csv` se guardan en `carpeta_salida`.

---

## 5. PSP

```powershell
cd 03_PSP
javac -encoding UTF-8 -d clases *.java pruebas\*.java src\Psp\*.java
java -cp clases ProcesadorPedidosCustom datos\custom40_fabricacion_psp.csv
type salidas\ficha_taller_CUSTOM-40.txt
cd ..
```

Para otro pedido, se le pasa el `fabricacion_psp.csv` que genera el 15 (por ejemplo, con `-v referencia=SO024`). La ficha queda en `03_PSP\salidas\ficha_taller_<referencia>.txt` y el registro, en `03_PSP\salidas\registro_psp.txt`.

---

## 6. Python (consola y dashboard)

```powershell
cd 04_Python
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py                          # modo real: entrada_acc\ → outputs\real\
.venv\Scripts\python.exe generador_datos.py               # vuelve a crear datos_sinteticos\
.venv\Scripts\python.exe main.py --modo sintetico
.venv\Scripts\python.exe main.py --modo sintetico-errores # tiene que terminar con «DATOS BLOQUEADOS» (código 1)
.venv\Scripts\streamlit.exe run app_dashboard.py          # http://localhost:8501
cd ..
```

- Con Python 3.12 se cambia `-3.13` por `-3.12`.
- No hace falta activar el entorno: se usa `.venv\Scripts\python.exe` directamente. El `.venv` no se sube a Git.
- `generador_datos.py` vuelve a escribir los CSV de `datos_sinteticos\` (semilla 2026): salen iguales a los del repositorio. En Windows, `git status` puede marcarlos como modificados solo por los finales de línea; `git diff` no enseña ningún cambio.
- `main.py --entrada CARPETA --salida CARPETA` sirve para analizar otra exportación sin tocar `entrada_acc\`.
- En modo real, `main.py` también contrasta con SQL las consultas del caso N (`12_consultas_panel.sql`): tiene que decir «caso N: 17 de 17 cifras coinciden con SQL».
- El dashboard se abre en `http://localhost:8501` y solo responde en ese ordenador. Para verlo desde un móvil de la misma red: `--server.address 0.0.0.0`.
- **Para que el dashboard vea un pedido nuevo de PostgreSQL hay que volver a exportar con el 16:** Python solo lee CSV.

---

## 7. Web, panel, portal del trabajador y tienda

**Solo la web** (escaparate, catálogo, ficha, probador, Custom y contacto), sin servidor:

```powershell
py -m http.server 8000 --bind 127.0.0.1
```

y abrir `http://127.0.0.1:8000/01_Interfaces/cliente/`. También funciona abriendo `01_Interfaces/cliente/index.html` directamente.

**Panel, portal y tienda** (ampliaciones), con `servidor-admin`:

1. Haber lanzado el 19 (panel) y, para la tienda, el 20 y el 21; para el reparto, el 22; para el portal del trabajador, el 23.
2. Instalar las dependencias exactas:
   ```powershell
   cd servidor-admin
   npm ci
   ```
3. Copiar `.env.example` como `.env` y rellenarlo. **El `.env` no se sube a Git.**

   | Variable | Qué poner |
   |---|---|
   | `PGHOST`, `PGPORT`, `PGDATABASE` | `localhost`, `5432` y `nova_sneakers` |
   | `PGUSER`, `PGPASSWORD` | `web_nova` y su contraseña (paso 9). Con `PGUSER=postgres` el servidor **se niega a arrancar** |
   | `PUERTO` | `3000` |
   | `TIENDA_PGUSER`, `TIENDA_PGPASSWORD` | `tienda_nova` y su contraseña (paso 19). Vacías: el panel funciona y la tienda enseña el catálogo, pero no deja comprar |
   | `RESEND_API_KEY`, `RESEND_FROM` | Opcional: la clave de Resend y el remitente (por ejemplo, `NOVA Sneakers <onboarding@resend.dev>`). Sin dominio verificado en Resend, solo llegan los correos al correo de la propia cuenta. Vacías: no se manda ningún recibo y la compra funciona igual |
   | `CORREO_PROVEEDOR` | Vacía o `resend`: Resend. `ethereal`: **solo desarrollo**: el recibo va a una cuenta temporal de Ethereal que no entrega nada, y el enlace sale en la consola y en «Mis pedidos». Con `NODE_ENV=production` se niega. Las vistas previas de Ethereal son públicas: solo con datos ficticios |
   | `RESEND_URL` | Opcional, solo para pruebas (un Resend simulado) |
   | `BLOQUEO_LOGIN_MS` | Opcional: duración del bloqueo tras 5 fallos de login (por defecto, 5 minutos) |
   | `ODOO_URL`, `ODOO_DB`, `ODOO_API_KEY` | **Vacías.** Es el conector de Odoo de Berme (`odoo.js`): sin las tres se queda desactivado y no llama a ningún servidor. No se ha probado contra ningún Odoo |

4. Arrancar y abrir:
   ```powershell
   npm start
   ```
   - **Login único del personal:** `http://127.0.0.1:3000/login.html`. `admin.demo` (administrador) entra al panel; `taller.demo` (trabajador), al portal del trabajador; `tienda.demo` (comercial) recibe «sin permiso», porque trabaja con la aplicación Java.
   - Panel: `http://127.0.0.1:3000/admin.html`. Portal: `http://127.0.0.1:3000/trabajador/`.
   - Tienda: `http://127.0.0.1:3000/tienda/`.
   - Al arrancar, la consola dice si la tienda, el correo y Odoo están configurados.

---

## 8. Portal del trabajador y Odoo

- **Portal del trabajador (Berme), integrado.** Cuatro páginas (`01_Interfaces/trabajador/`): resumen, pedidos («Avanzar estado»: `confirmado` → `en_preparacion` → `enviado` → `entregado`), inventario («Guardar» la cantidad) y personalizados. Se entra por el login único con una cuenta de rol **trabajador** (`taller.demo`). El servidor se conecta como `web_nova` y, para el portal, pasa al rol `portal_trabajador` (script 23), que solo lee las columnas que enseña el portal y solo cambia algo con dos funciones que dejan la auditoría a nombre del trabajador.
- **Lo que de Berme no está activo:** el conector de Odoo (`odoo.js`) está **desactivado** sin `ODOO_*`, y las rutas de `pedidos.js` (crear pedidos y enviarlos a Odoo) **no se montan** (`servidor-admin/README.md`, «Lo que falta del portal»).
- **Odoo:** **[PENDIENTE (Berme)]**: máquina virtual, versión, instalación, módulos, usuarios de demostración (sin contraseñas en el repositorio) y cómo restaurar la copia de seguridad. Ver `05_Odoo/CHECKLIST_ODOO_BERME.md`.

---

## 9. Pruebas: cómo se lanza cada batería y qué tiene que salir

**Todas sobre una base de PRUEBA, nunca la del equipo:** la batería Java deja pedidos `PRUEBA-*` y un usuario `prueba.*`, y las de la tienda y el portal crean clientes, pedidos y cambios de verdad.

| Batería | Cómo se lanza | Resultado esperado | Último resultado (13/11) |
|---|---|---|---|
| SQL | Scripts 09 a 16 en el orden del §3 | **123 PASS, 0 FAIL y 1 ERROR previsto** (S4b) | 123 / 0 / 1 (`06_Intermodular/evidencias/regresion-final/01_sql/`) |
| Java | `02_Acceso_Datos\java\pruebas.bat` (pide las tres contraseñas de demostración) | `RESULTADO: 47 PASS, 0 FAIL` | 47 / 0 (`06_Intermodular/evidencias/regresion-final/02_java_psp/`) |
| PSP | En `03_PSP`, tras compilar: `java -cp clases PruebasPsp` | `Pruebas superadas: 27 de 27` | 27 / 27 (ídem) |
| Python | En `04_Python`: `.venv\Scripts\python.exe -m unittest discover -s tests -v` (tarda unos 12 minutos) | `Ran 265 tests` y `OK` | 265 OK (`06_Intermodular/evidencias/regresion-final/04_python/`) |
| Panel | En `servidor-admin`, con `$env:PRUEBA_ADMIN_USUARIO`, `PRUEBA_ADMIN_CLAVE`, `PRUEBA_OTRO_USUARIO` y `PRUEBA_OTRO_CLAVE` (y las `PRUEBA_COMERCIAL_*`): `npm test` | `tests 23`, `pass 23` con `PRUEBA_TIENDA_BASE_DESECHABLE=si` (sin ella, una se salta) | 23 / 23 y 22 + 1 saltada (`06_Intermodular/evidencias/regresion-final/03_node/`) |
| Tienda | `$env:PRUEBA_TIENDA_BASE_DESECHABLE = "si"; npm run test:tienda` | `tests 39`, `pass 39` | 39 / 39 (ídem) |
| Login único y portal | `$env:PRUEBA_TIENDA_BASE_DESECHABLE = "si"; $env:PRUEBA_SUPERUSUARIO = "postgres"; npm run test:portal` | `tests 24`, `pass 24` | 24 / 24 (ídem) |
| Web (rápida) | `py scripts\comprobar_web.py` | Que existen los recursos que enlaza la web | Correcta (`06_Intermodular/evidencias/regresion-final/02_java_psp/08_comprobar_web.txt`) |
| PSP (rápida) | `py scripts\comprobar_psp.py` (con `java` y `javac` en el PATH) | **Falla en la primera comprobación, ya se sabe:** espera la respuesta antigua del validador (`OK;CUSTOM-40;4;40`). El arreglo de Berme está en `feature/berme` (`862e37d`) y no se ha traído | Falla como se espera (ídem, `07_comprobar_psp.txt`) |
| Web en navegador | Scripts de Playwright, fuera del repositorio (`01_Interfaces/memoria/ESTRATEGIA_PRUEBAS_INTERFACES.md` §7) | 81/81, 136/136, 114/114, compra 139/139, reparto 29/29, portal 82/82 y Ethereal 16/16 | Ver `06_Intermodular/evidencias/regresion-final/README.md` |

`npm test`, `test:tienda` y `test:portal` leen el `.env` (`node --env-file=.env`): tiene que existir, aunque las variables `PRUEBA_*` se pongan en la consola.

---

## 10. Qué hacer si algo falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `relation "…" already exists` al instalar | La base no estaba vacía | Borrar la base, crearla otra vez y repetir desde el paso 1 |
| En el 09, `FAIL` en A1 y A2 | Se lanzó el 13 antes del 09 | Es lo esperado en ese orden. Para ver 91 PASS, montar de nuevo en el orden del §3 |
| En el 09, `FAIL` en P1, P2 o S1 | Se lanzaron el 18, el 20 o el 21 antes del 09 | Ídem |
| En el 09, un `ERROR` en S4b | Es la prueba de permisos: el cliente no puede ejecutar `descontar_stock` | Nada: es el error previsto |
| Java: «La cuenta no tiene contrasena establecida» | No se ha lanzado el 13 | Lanzar `13_activar_usuarios.sql` |
| Java: `ClassNotFoundException: org.postgresql.Driver` | Falta el driver | Copiar `postgresql-42.7.14.jar` en `02_Acceso_Datos\java\lib\` |
| Java: `javac` no se reconoce | El JDK no está en el PATH | Ver §1 |
| Java: «password authentication failed for user java_nova» | `conexion.properties` mal o no se ha lanzado el 17 | Revisar la contraseña o volver a lanzar el 17 |
| Java: «Acceso denegado» en una operación | El rol no tiene ese permiso | Es correcto (matriz de permisos de `02_Acceso_Datos/memoria/MEMORIA_ACCESO_DATOS.md` §9.2) |
| El 15 se para y no genera el CSV | El pedido no existe, no está confirmado o no suma 40 pares | Lanzar el 14 (para `CUSTOM-40`) o confirmar el pedido en Java; el CSV anterior queda intacto |
| El 18 dice «Falta el precio…» y no inserta nada | Faltan los `-v` | Pasar `-v precio=… -v color=… -v stock=…` (`06_Intermodular/SO024/SO024_DATOS_PENDIENTES.md`) |
| PSP: «No se encuentra la clase Psp.AnalizadorTallas» (código 3) | No se compiló `src\Psp` | Compilar con `src\Psp\*.java`, como en el §5 |
| `PruebasPsp` falla con caracteres raros | Se lanzó con `-Dfile.encoding=UTF-8` | Lanzarla sin esa opción |
| `python` abre la Microsoft Store | Es el alias de Windows | Usar `py` o `.venv\Scripts\python.exe` |
| `main.py` termina con «DATOS BLOQUEADOS» | Hay incidencias bloqueantes | Ver `outputs\<modo>\incidencias.csv`; los CSV de entrada no se tocan |
| `main.py` termina con «NO CUADRA CON SQL» | P-A, P-B, P-C o N-1 a N-3 son de otra exportación | Exportar los 5 CSV y las consultas a la vez (`04_Python/conciliacion_sql.md`) |
| El dashboard dice «Error de carga» | Falta un CSV, está vacío o le falta una columna | Volver a exportar con el 16; el último resultado válido se ve rotulado DESACTUALIZADO |
| El dashboard pone «PRUEBA» en naranja | Es lo que dice `ORIGEN.txt` | Poner `Tipo: REAL` solo si la exportación es de la base del equipo |
| Un pedido nuevo no sale en el dashboard | No se ha vuelto a exportar | Lanzar el 16 y esperar al siguiente ciclo de 60 s (o «Actualizar ahora») |
| El servidor no arranca: se niega con `PGUSER=postgres` | Es una protección | Usar `web_nova` |
| `npm test` dice que no encuentra `.env` | Los scripts de `package.json` usan `--env-file=.env` | Crear el `.env` (§7) |
| La tienda dice «no disponible» | Faltan `TIENDA_PGUSER` y `TIENDA_PGPASSWORD`, o no se lanzó el 20 | Rellenar el `.env`, lanzar el 20 y reiniciar |
| Todos los modelos salen «No disponible» | La base no tiene el 21 nuevo (100 modelos) | Lanzar el 21 (se puede repetir y renombra los 12 antiguos) |
| `taller.demo` entra pero el portal da error | No se ha lanzado el 23 | Lanzar `23_portal_trabajador.sql` (después del 22) |
| `tienda.demo` no entra en el panel ni en el portal | Es un comercial: trabaja con la aplicación Java | Nada: es lo previsto (403) |
| El panel o el portal salen sin iconos ni gráficos | No hay internet: Lucide y Chart.js vienen de una CDN | Conectarse a internet. El portal sigue funcionando sin iconos |
| No llega el recibo de Ethereal | `NODE_ENV=production`, sin red o Ethereal no responde en 10 s | La compra sigue confirmada; revisar la consola |
| El puerto 3000 está ocupado | Otro servidor | Cambiar `PUERTO` en el `.env` |
| Tildes rotas en la consola de psql | Codificación de la consola | `$env:PGCLIENTENCODING = "UTF8"` (y, si hace falta, `chcp 65001`) |
