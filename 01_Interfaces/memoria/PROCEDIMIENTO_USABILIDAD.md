# NOVA Sneakers · Procedimiento de la prueba de usabilidad

Desarrollo de Interfaces, RA4 CE h)-i): «Se comprueba la claridad de los mensajes y se realizan pruebas de usabilidad y accesibilidad» (IM p. 8). La parte automática (accesibilidad, responsive y funcionamiento) está en `ESTRATEGIA_PRUEBAS_INTERFACES.md`, y su última pasada, la del 13/11 sobre la rama final, está en verde (`06_Intermodular/evidencias/regresion-final/05_web/`). Esta es la parte **con personas**, y ninguna prueba automática la sustituye.

> **Estado: [PENDIENTE (los tres): hacer la prueba con 3 a 5 personas].** La prueba no se ha hecho todavía (13/11/2026). Este documento es el procedimiento y las plantillas **vacías**. No hay ningún resultado: los rellena el equipo el día de la prueba, con lo que pase de verdad.

---

## 1. Objetivo

Comprobar si personas que no conocen la web consiguen hacer las tareas principales (ver el catálogo, entender el servicio Custom, pedir una solicitud y encontrar el contacto), cuánto tardan, dónde se equivocan y qué les parece. Con eso se decide qué mejorar antes de la entrega.

**Preguntas que tiene que responder:**

1. ¿Se encuentra el precio y las tallas de un modelo sin ayuda?
2. ¿Se entiende qué es el servicio Custom y qué pasa después de enviar la solicitud?
3. ¿Se rellena el formulario Custom sin errores? ¿Se entienden sus mensajes?
4. ¿Se navega bien en el móvil?
5. ¿Qué puntuación SUS da la web?

---

## 2. Participantes

- **Cuántos:** de **3 a 5** personas. Con 5 suelen salir la mayoría de los problemas graves; con menos de 3 no hay con qué comparar.
- **Quiénes:** personas **ajenas al equipo** que no hayan visto la web (compañeros de otro grupo, familiares o amigos), mayores de edad.
- **Variedad:** si se puede, al menos una persona que no sea de informática y al menos una que haga las tareas en un **móvil de verdad**.
- **Identificación:** cada persona se apunta solo con un código, **P1 a P5**. No se escriben nombres en ninguna hoja que vaya al repositorio.

| Código | Perfil (sin datos personales) | Dispositivo | ¿Ha visto la web antes? |
|---|---|---|---|
| P1 | | | |
| P2 | | | |
| P3 | | | |
| P4 | | | |
| P5 | | | |

---

## 3. Papeles del equipo en cada sesión

| Papel | Qué hace | Quién (rotar entre sesiones) |
|---|---|---|
| Moderador | Lee el guion y las tareas. **No ayuda** salvo que la persona se bloquee del todo | ______ (se decide el día de la prueba) |
| Cronometrador | Mide el tiempo de cada tarea | ______ (se decide el día de la prueba) |
| Observador | Apunta errores, dudas, frases en voz alta y si hubo ayuda | ______ (se decide el día de la prueba) |

Si solo hay dos miembros del equipo, el moderador también cronometra.

---

## 4. Material y preparación

**Material:**

- Un ordenador con Microsoft Edge (zoom al 100 %) y, para la tarea 6, un móvil.
- La web servida en local desde la raíz del repositorio:
  ```
  py -m http.server 8000 --bind 127.0.0.1
  ```
  y abierta en `http://127.0.0.1:8000/01_Interfaces/cliente/`. Para el móvil hace falta que esté en la misma red y servirla con `--bind 0.0.0.0` **solo durante la prueba**, o usar el modo móvil de Edge (F12 → dispositivo) y apuntarlo en la hoja.
- Un cronómetro (el del móvil sirve).
- Por cada participante: una hoja de consentimiento (§10), una hoja de observación (§8), un cuestionario SUS (§9) y la tarjeta de datos de la tarea 4 (§6).

**Antes de cada sesión (lista de comprobación):**

- [ ] Versión de la web apuntada (commit o fecha de los archivos): ______
- [ ] Navegador recién abierto, sin historial de la sesión anterior y en la página de inicio.
- [ ] Ninguna pestaña con el código ni con documentación abierta.
- [ ] La hoja de consentimiento firmada **antes** de empezar.
- [ ] Sin grabaciones, salvo que la persona lo haya aceptado por escrito.

---

## 5. Guion del moderador (leer tal cual)

> «Gracias por ayudarnos. Vamos a probar la web de una marca de zapatillas que hemos hecho en clase. **Probamos la web, no a ti**: si algo cuesta, es un fallo de la web y eso es justo lo que queremos encontrar.
>
> Te voy a pedir unas tareas cortas, de una en una. Intenta hacerlas como lo harías en casa. Si puedes, **piensa en voz alta**: di qué buscas y qué esperas encontrar. No te voy a ayudar durante las tareas, porque queremos ver qué pasa sin ayuda; si te quedas bloqueado o bloqueada, dímelo y pasamos a la siguiente.
>
> No se guarda ningún dato tuyo: el formulario es de prueba y no envía nada. Al final te pediré que rellenes un cuestionario de diez preguntas. Puedes parar cuando quieras. ¿Alguna duda?»

Después de cada tarea, preguntar: **«Del 1 al 7, ¿cómo de fácil o difícil te ha parecido esta tarea?»** (1 = muy difícil, 7 = muy fácil).

---

## 6. Las tareas

Se leen en este orden. Cada una empieza en la página de inicio, salvo que se diga otra cosa. Las respuestas esperadas son las de la web de la rama final (`integracion/candidata-2`, 13/11/2026; `js/modelos.js`, `datosColeccion`); **hay que comprobarlas el día de la prueba**, porque los precios son provisionales.

| Tarea | Enunciado que se lee | Dispositivo | Éxito si… | Tiempo máximo |
|---|---|---|---|---|
| T1 | «Busca una zapatilla de la colección **Luxe** y dime cuánto cuesta y qué tallas tiene.» | Ordenador | Dice el precio y las tallas que salen en la ficha (el 13/11: 139,90 € y de la 38 a la 46) | 2 min |
| T2 | «Busca el modelo que se llama **Aurora** y abre su ficha.» | Ordenador | Abre la ficha de NOVA Mujer Aurora | 2 min |
| T3 | «Tu club quiere zapatillas personalizadas para todo el equipo. Averigua cómo funciona el servicio y **qué pasa después de enviar la solicitud**.» | Ordenador | Llega a la sección Custom y explica con sus palabras que después viene un presupuesto, la fabricación y la entrega | 2 min |
| T4 | «Ahora pide esas zapatillas con los datos de esta tarjeta.» (Se le da la tarjeta de abajo.) | Ordenador | Sale el mensaje «SIMULACIÓN · Solicitud preparada…» con **20 pares** | 4 min |
| T5 | «Busca el correo para escribir a la empresa.» | Ordenador | Dice o señala el correo de la sección de contacto | 1 min |
| T6 | «En el móvil, ve a la sección donde se piden zapatillas personalizadas y después vuelve arriba del todo.» | Móvil | Llega a Custom y vuelve al inicio (con el menú, «Volver arriba» o desplazándose) | 1,5 min |

**Tarjeta de datos de la tarea 4** (datos ficticios; **no** son los de SO024, que no están acordados):

| Campo | Valor |
|---|---|
| Club o equipo | CD Prueba Usabilidad |
| Persona de contacto | Ana Prueba |
| Email | ana.prueba@example.com |
| Teléfono | (dejar vacío) |
| Modelo | NOVA Street Vortex |
| Colores | azul y blanco |
| Personalización | Escudo del club en el lateral |
| Pares por talla | 39: **4** · 40: **6** · 41: **6** · 42: **4** (total 20) |

**Tarea opcional** (solo si se prueba también la tienda, que es una ampliación y necesita el servidor): «Añade al carrito dos pares de una zapatilla en tu talla.» Si se hace, se apunta aparte y no cuenta para las métricas de la web obligatoria.

---

## 7. Métricas y cómo se miden

| Métrica | Definición exacta | Cómo se apunta |
|---|---|---|
| **Éxito** | **E** = lo consigue sola; **EA** = lo consigue después de una ayuda del moderador; **F** = no lo consigue o se pasa del tiempo máximo | Una letra por tarea |
| **Tiempo** | Segundos desde que el moderador termina de leer la tarea hasta que la persona dice que ha terminado (o se llega al máximo) | Número entero de segundos |
| **Errores** | Cada acción que no acerca al objetivo: ir a una sección equivocada, abrir una ficha que no era, un envío que el navegador bloquea, escribir en un campo que no toca… | Número y una descripción corta |
| **Ayudas** | Cada vez que el moderador tiene que dar una pista | Número y qué se dijo |
| **Facilidad (SEQ)** | La respuesta de 1 a 7 a la pregunta de después de cada tarea | Número |
| **SUS** | El cuestionario del §9, al final | Puntuación de 0 a 100 |
| **Comentarios** | Frases en voz alta, dudas y sugerencias, **literales** | Texto |

**Criterios para decidir que hay un problema** (los fija el equipo antes de la prueba):

- una tarea con menos del 80 % de éxitos sin ayuda;
- una tarea en la que la mediana del tiempo pasa del máximo;
- un error que repiten dos o más personas;
- una SUS media por debajo de 68 (la media de referencia que se usa habitualmente para este cuestionario).

Cada problema se clasifica por gravedad: **0** no es un problema; **1** cosmético; **2** menor; **3** importante (hay que arreglarlo antes de entregar); **4** grave (impide hacer la tarea).

---

## 8. Hoja de observación (una por participante)

**Participante:** P__ · **Fecha:** __/__/2026 · **Hora:** __:__ · **Dispositivo y navegador:** ____________ · **Versión de la web:** ____________
**Moderador:** ______ · **Cronometrador:** ______ · **Observador:** ______

| Tarea | Éxito (E / EA / F) | Tiempo (s) | Errores (nº) | Qué errores | Ayudas (nº y cuál) | Facilidad (1–7) |
|---|---|---|---|---|---|---|
| T1 | | | | | | |
| T2 | | | | | | |
| T3 | | | | | | |
| T4 | | | | | | |
| T5 | | | | | | |
| T6 | | | | | | |

**Mensajes de la web que la persona no entendió (literal):**

-

**Comentarios en voz alta (literal):**

-

**Otras observaciones:**

-

---

## 9. Cuestionario SUS (System Usability Scale)

Se da al final, en papel. La persona marca de **1** (totalmente en desacuerdo) a **5** (totalmente de acuerdo). Hay que contestar todas; si duda, que marque el 3.

| Nº | Afirmación | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| 1 | Creo que me gustaría usar esta web con frecuencia | ☐ | ☐ | ☐ | ☐ | ☐ |
| 2 | La web me ha parecido innecesariamente complicada | ☐ | ☐ | ☐ | ☐ | ☐ |
| 3 | La web me ha parecido fácil de usar | ☐ | ☐ | ☐ | ☐ | ☐ |
| 4 | Creo que necesitaría la ayuda de una persona con conocimientos técnicos para usar esta web | ☐ | ☐ | ☐ | ☐ | ☐ |
| 5 | Las distintas partes de la web me han parecido bien integradas | ☐ | ☐ | ☐ | ☐ | ☐ |
| 6 | La web me ha parecido demasiado incoherente | ☐ | ☐ | ☐ | ☐ | ☐ |
| 7 | Imagino que la mayoría de la gente aprendería a usar esta web muy rápido | ☐ | ☐ | ☐ | ☐ | ☐ |
| 8 | La web me ha parecido muy difícil de manejar | ☐ | ☐ | ☐ | ☐ | ☐ |
| 9 | Me he sentido segura o seguro usando la web | ☐ | ☐ | ☐ | ☐ | ☐ |
| 10 | He tenido que aprender muchas cosas antes de manejarme con la web | ☐ | ☐ | ☐ | ☐ | ☐ |

**Cómo se calcula:**

1. En las afirmaciones **impares** (1, 3, 5, 7 y 9): puntuación marcada − 1.
2. En las **pares** (2, 4, 6, 8 y 10): 5 − puntuación marcada.
3. Se suman los diez resultados (de 0 a 40) y se multiplica por **2,5**. Sale un número de 0 a 100.

No es un porcentaje: es una puntuación. Se da la media y el mínimo y el máximo de las personas.

---

## 10. Consentimiento (una copia por participante)

> **Prueba de usabilidad de la web NOVA Sneakers (proyecto de clase de 2.º DAM)**
>
> Me han explicado que:
>
> - se prueba la web, no a mí;
> - la prueba dura unos 20 minutos y puedo dejarla cuando quiera, sin dar explicaciones;
> - el formulario de la web es de prueba: no envía ni guarda ningún dato;
> - el equipo apuntará en una hoja lo que hago, cuánto tardo y lo que digo, **sin mi nombre**, solo con un código (P1, P2…);
> - esas hojas solo se usan para mejorar la web y para la memoria del proyecto, y no se publican con datos que me identifiquen;
> - ☐ **acepto** / ☐ **no acepto** que se grabe la pantalla (sin mi cara ni mi voz). Si no lo acepto, no se graba nada.
>
> Código de participante: P__ Fecha: __/__/2026
>
> Firma: ____________________

Las hojas firmadas **no se suben al repositorio** (tienen la firma). Se guardan en papel hasta la evaluación y después se destruyen.

---

## 11. Tabla resumen (se rellena al terminar todas las sesiones)

**Por tarea:**

| Tarea | Éxitos sin ayuda | Éxitos con ayuda | Fracasos | % de éxito sin ayuda | Tiempo mediano (s) | Errores totales | Facilidad media (1–7) |
|---|---|---|---|---|---|---|---|
| T1 | | | | | | | |
| T2 | | | | | | | |
| T3 | | | | | | | |
| T4 | | | | | | | |
| T5 | | | | | | | |
| T6 | | | | | | | |

**SUS:**

| Participante | P1 | P2 | P3 | P4 | P5 | Media |
|---|---|---|---|---|---|---|
| Puntuación SUS | | | | | | |

**Problemas encontrados:**

| Nº | Problema | Tarea | Cuántas personas | Gravedad (0–4) | Propuesta de cambio | ¿Corregido? (archivo y commit) |
|---|---|---|---|---|---|---|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |

---

## 12. Informe breve para la memoria (plantilla)

Cuando esté hecha, se resume en el apartado 3.4 de `06_Intermodular/memoria/Memoria_NOVA_Sneakers.pdf` con esta estructura (una página como mucho):

1. **Cuándo y con quién:** fecha, número de participantes y perfiles (sin nombres), dispositivos y versión de la web.
2. **Resultados por tarea:** la tabla resumen.
3. **SUS:** media, mínimo y máximo.
4. **Problemas encontrados**, ordenados por gravedad, con lo que dijeron las personas (literal).
5. **Qué se ha cambiado** por la prueba (archivo y commit) y **qué no**, y por qué.
6. **Limitaciones:** pocas personas, perfiles que no son clientes reales de un club, entorno controlado.

**[PENDIENTE (los tres): fecha de la prueba ______, participantes ______, resultados ______.]**
