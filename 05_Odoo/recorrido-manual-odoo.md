# Recorrido manual del pedido Custom: PostgreSQL → CSV → Odoo

> **Archivo histórico.** El caso de entrega es [S00005 del Club Atlético NOVA](../06_Intermodular/CASO_COMUN_S00005.md). El plan SO024 siguiente queda sustituido y no se ejecuta. Se conserva para documentar la preparación y los ensayos anteriores, sin atribuirlos a S00005.

> **Borrador histórico anterior al PDF de Berme.** No usar sus ejemplos de CUSTOM-40 como acuerdo de SO024. El estado actual, los códigos y el orden de conciliación están en [INTEGRACION_ODOO_SO024.md](../06_Intermodular/SO024/INTEGRACION_ODOO_SO024.md).

Borrador para revisar con Berme (OD-01 y OD-04), Álvaro (OD-02) y Omar (OD-03).

- **Qué es:** un recorrido **manual**, sin sincronización automática y sin escribir
  en Odoo desde ningún programa.
- **Por qué basta:** el enunciado (v0.3) dice que «la integración entre bloques
  puede realizarse mediante ficheros CSV/JSON y procedimientos documentados», y el
  plan de reparto añade que «no se pide crear una sincronización automática de
  stock o una API de Odoo».
- **Lo que se evalúa:** que los datos sean coherentes en los tres sistemas, y que
  se pueda seguir el mismo pedido de uno a otro.

> **No se ha podido comprobar Odoo desde este ordenador** (10/11/2026).
> `ubuntu.orb.local:8069` no se resuelve y la conexión no responde en 5 s.
> Las direcciones `.orb.local` son de OrbStack y normalmente solo funcionan en el
> equipo que lo ejecuta. Los nombres de menú y de campo de abajo son los estándar
> de Odoo en español: hay que confirmarlos en la instancia de clase, cuya versión
> no conocemos.

## 0. Decisión previa: qué pedido es «el caso común»

| | Enunciado y reparto | Base de datos (`entrada_acc`, exportación de PRUEBA) |
|---|---|---|
| Referencia | SO024 | **CUSTOM-40** (y NOVA-0011, igual pero pendiente) |
| Cliente | Club Halcones | Club Atletico NOVA (id 6, empresa) |
| Modelo | Runner X | NOVA Velocity (id 2), color Rojo |
| Tallas | 38 a 46 | 40, 41, 42 y 43, con 10 pares cada una |
| Pares | 40 | 40 |
| Importe | — | 4.796,00 € (4 líneas × 1.199,00 €), IVA pendiente |

Hay que decidir una de dos:
- **Usar en Odoo el pedido de la base,** CUSTOM-40 (lo más sencillo: los CSV ya
  existen).
- **Cambiar la base al caso SO024 del enunciado.**

Sea cual sea, el mismo pedido tiene que aparecer igual en PostgreSQL, en Odoo, en
PSP y en Python. Falta también decidir si NOVA-0011 y CUSTOM-40 son el mismo
encargo.

## 1. Tabla de identificadores (se rellena durante el recorrido)

| Dato | PostgreSQL / CSV | Campo en Odoo | Valor en Odoo |
|---|---|---|---|
| Cliente | `clientes.csv`: `id_cliente` 6, correo `club.atletico@example.com` | Contacto → **Referencia** (pestaña Ventas y compras) = `CLI-6`, y el mismo correo | … |
| Producto | `modelos.csv`: `id_modelo` 2, NOVA Velocity | Producto «NOVA Velocity», con los atributos Talla y Color | … |
| Variante (talla) | `lineas_pedido.csv` / `stock.csv`: `sku` NOVA-4-40 … NOVA-4-43 | Variante → **Referencia interna** = el mismo SKU | … |
| Pedido | `pedidos.csv`: `referencia` CUSTOM-40 (única en la base) | Pedido de venta → **Referencia del cliente** = CUSTOM-40 | SO… |
| Fabricación | `fabricacion_psp.csv` (script 15) | Orden de fabricación, cuyo origen es el pedido | MO… o WH/MO/… |
| Entrega | — | Albarán de salida | WH/OUT/… |
| Factura | — | Factura del pedido | INV/… |

Regla: **el SKU es la referencia interna de la variante en Odoo**, y **la
referencia del pedido de PostgreSQL va en «Referencia del cliente»**. No hace falta
ningún campo ni tabla nueva.

## 2. Pasos

### En PostgreSQL (base de PRUEBA, nunca la principal)
1. Exportar los cinco CSV con `02_Acceso_Datos/sql/16_exportar_csv_dashboard.sql` (el
   exportador oficial), desde `04_Python/entrada_acc`.
2. Exportar la orden de fabricación con `15_exportar_fabricacion.sql`, que crea
   `fabricacion_psp.csv` con las tallas y cantidades de CUSTOM-40 si está
   confirmado.
3. Apuntar en la tabla la referencia, el cliente, los cuatro SKU con sus pares y el
   importe total.

### En Odoo (a mano, en la instancia de Berme)
4. **Antes de crear nada, buscar.** En Ventas, filtrar los pedidos por «Referencia
   del cliente» = CUSTOM-40. Si ya existe, no se crea otro: así no hay duplicados.
5. **Contacto** (OD-03). Buscar por el correo. Si no existe, crearlo con la
   referencia `CLI-6`.
6. **Producto** (OD-02). NOVA Velocity, con las variantes de talla 40 a 43 y
   color Rojo, cada una con su SKU como referencia interna.
7. **Presupuesto** (OD-03). Una línea por talla, con la misma cantidad que
   `lineas_pedido.csv` (10 + 10 + 10 + 10). «Referencia del cliente» = CUSTOM-40 y,
   en la nota, la personalización del pedido. Confirmarlo: se convierte en pedido
   de venta SO….
8. **Fabricación, entrega y factura** (OD-04), según el alcance que se haya
   configurado.

### Cruce (la prueba de que es el mismo pedido)
9. Comparar el pedido de Odoo con los CSV:

   | Comprobación | CSV | Odoo | ¿Coincide? |
   |---|---|---|---|
   | Referencia | CUSTOM-40 | Referencia del cliente | |
   | Cliente | Club Atletico NOVA / club.atletico@example.com | contacto | |
   | Líneas (SKU y talla) | NOVA-4-40 … NOVA-4-43 | referencias internas de las líneas | |
   | Pares | 40 (10 por talla) | suma de cantidades | |
   | Importe | 4.796,00 € (sin aclarar el IVA) | base imponible | |
   | Estado | confirmado | pedido de venta confirmado | |

10. Guardar las evidencias: capturas de cada pantalla de Odoo, la tabla rellenada
    y los CSV usados.

## 3. Si algo falla

- **Odoo no está disponible.** Nada se pierde: PostgreSQL y los CSV siguen igual.
  En la tabla se anota «pendiente en Odoo» y el paso se repite más tarde.
- **El pedido ya existe en Odoo.** No se crea otro: se completa el que hay, gracias
  a la búsqueda del paso 4.
- **Las cifras no coinciden.** Se anota la diferencia y se corrige a mano en
  Odoo. PostgreSQL no se toca para que cuadre.
- **Duplicados en PostgreSQL.** No pueden darse: `referencia` es única (UNIQUE) y
  la base rechaza un segundo CUSTOM-40.

## 4. Lo que no se hace ahora

- **Ningún programa escribe en Odoo** (ni XML-RPC ni JSON-RPC), y no hay
  sincronización de stock.
- **No se guardan credenciales de Odoo** en el repositorio.
- **El stock de Odoo y el de PostgreSQL no se igualan solos.** Si hace falta
  enseñarlo, se explica como dos sistemas con responsabilidades distintas:
  - Odoo: el flujo comercial (venta, fabricación, entrega y factura).
  - PostgreSQL: los datos del módulo de Acceso a Datos, y la fuente de los CSV de
    Python y PSP.

Más adelante, y solo si Berme lo ve sencillo, podría añadirse un script de **solo
lectura** que compruebe que CUSTOM-40 existe en Odoo. Siempre con las
credenciales en un `.env` que no se sube.
