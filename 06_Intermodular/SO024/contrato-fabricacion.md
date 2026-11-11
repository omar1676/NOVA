# Formatos actuales de fabricación

Este documento describe los formatos presentes en el código. No establece un
contrato nuevo de Odoo ni afirma que los dos analizadores sean intercambiables.

## CSV PostgreSQL → PSP

Productor: `02_Acceso_Datos/sql/15_exportar_fabricacion.sql`.
Consumidor: `03_PSP/LanzadorValidacion.java`, que encadena
`ValidadorPedidoCustom` y `AnalizadorTallas`.

Archivo: `fabricacion_psp.csv`, codificación UTF-8, separador coma, cabecera:

```csv
referencia,sku,cliente,modelo,color,personalizacion,talla,cantidad
```

Una fila corresponde a una línea de pedido. Los campos con comas, comillas o
saltos de línea se entrecomillan según CSV; una comilla interior se duplica.
No se debe leer separando cada línea por comas: un registro puede ocupar
varias líneas físicas. `LectorCsv` conserva estos campos.

El exportador actual exige `CUSTOM-40` confirmado, cuatro líneas, cuatro
tallas y cuarenta pares. El caso persistente está en el script SQL 14.
El validador Java admite otros pedidos: exige cabecera exacta, ocho campos,
una referencia común no vacía, tallas y cantidades enteras positivas.
Su aceptación por sí sola no prueba existencia del SKU ni disponibilidad.

El validador responde `OK;referencia;lineas;pares` por stdout con código 0.
Los datos rechazados producen `ERROR;motivo` por stderr y código 2.
El padre solo inicia el analizador después de validar.
El segundo proceso imprime cantidades por talla y un total.

La muestra `03_PSP/pruebas/custom40.csv` es sintética y no sustituye una
exportación de PostgreSQL. Incluye coma, comillas y salto de línea para
comprobar que el formato se transmite completo.

## Protocolo del paquete Psp

`03_PSP/src/Psp/AnalizadorTallas.java` utiliza un protocolo diferente:

```text
PEDIDO;referencia
LINEA;sku;modelo;color;talla;cantidad
FIN
```

No consume el CSV anterior. Acepta tallas de 20 a 55 y cantidades positivas.
Devuelve `OK`, agrupaciones `VARIANTE_TALLA` y `TALLA`, y `TOTAL`.
`PruebasAnalizador` ejecuta las comprobaciones incluidas en ese módulo.

## Decisiones pendientes

- Elegir el protocolo común y qué analizador se integrará con el coordinador.
- Acordar identificadores de SKU compartidos por catálogo, SQL y Odoo.
- Definir exportaciones de Odoo: no existe implementación en esta revisión.
- Acordar cómo representar personalizaciones distintas dentro de un pedido.
- Implementar el coordinador y la ficha de taller antes de afirmar que el
  flujo completo de fabricación está disponible.
