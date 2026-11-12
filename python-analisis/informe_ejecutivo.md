# Informe ejecutivo: cinco conclusiones (apartado 6.11)

Dirigido a producción y comercial. Las conclusiones las calcula `informe.py` a
partir de las tablas de análisis. Las cifras no están escritas a mano: si cambian
los datos, cambian las cifras. Aparecen:
- en la pestaña Dirección del dashboard;
- en `outputs/<modo>/informe_ejecutivo.csv`, que escribe `main.py`.

Se calculan con toda la exportación, sin filtros.

> **De dónde salen.** Las cifras de abajo son de los **datos SINTÉTICOS** de
> `generador_datos.py` (semilla 2026, 900 pedidos y 18 meses). No son ventas ni
> clientes reales de NOVA. La conclusión 5 es un **resultado predictivo** sobre
> esos datos sintéticos. Con la exportación de **PRUEBA** de Acceso a Datos salen
> otras cifras, que se resumen al final.

Cada conclusión separa:
- la **evidencia** (qué pasa);
- la **interpretación** (por qué podría pasar);
- la **decisión** (qué podría hacer NOVA);
- la **limitación** o riesgo (qué no se puede afirmar).

Y lleva además:
- el **impacto esperado**: qué parte de la demanda, del importe o del stock toca
  la decisión, con su cifra;
- el **sustento**: la tabla y el gráfico de los que sale;
- su **prioridad** (1 = la primera).

**Criterio de prioridad** (`informe.py`):
1. Primero, la urgencia:
   - **alta**: si no se actúa, se puede dejar sin servir demanda que ya existe
     (los modelos que concentran los pares, las referencias que se agotan);
   - **media**: sirve para planificar el próximo mes (capacidad, clientes);
   - **baja**: todavía no se puede decidir con datos (NO CALCULABLE) o la
     decisión es no cambiar nada.
2. Con la misma urgencia, el orden del informe (el número).

Con los datos sintéticos el orden es **1, 4, 2, 3 y 5**.

## 1. La demanda se concentra en pocos modelos

*Procede de datos sintéticos.*

- **Evidencia.** 6 de 12 modelos (clase A) suman el 81,7 % de los pares
  solicitados. El más pedido, SINT Runner, aporta el 35,1 % (2.458 pares).
- **Interpretación.** La producción depende de pocos modelos: quedarse sin stock
  de uno de clase A afecta a una gran parte de la demanda.
- **Decisión.** Priorizar materiales, capacidad y stock de los modelos A, y
  revisar los de clase C antes de fabricar más.
- **Limitación.** Son pares de pedidos no cancelados (demanda), no ventas
  cobradas, y salen de una simulación.
- **Impacto esperado.** Mantener servida la demanda de los modelos A: el 81,7 %
  de los pares solicitados (5.718 pares).
- **Prioridad 1** (urgencia alta). Sustento: `modelos_abc.csv` y el gráfico
  `02_pareto_modelos.png`.

## 2. Los pedidos Custom mueven la mayor parte del volumen

*Procede de datos sintéticos.*

- **Evidencia.** Los Custom son el 15,7 % de los pedidos de demanda, pero el
  75,8 % de los pares y el 79,4 % del importe. Ticket medio de venta: 5.116,63 €
  los Custom frente a 247,23 € los estándar.
- **Interpretación.** Pocos encargos de clubes y equipos concentran el volumen:
  un solo pedido Custom cambia la carga de producción de un mes.
- **Decisión.** Planificar la capacidad alrededor de los pedidos Custom (plazos y
  tallas por equipo) y seguirlos uno a uno.
- **Limitación.** Las cuotas son de pedidos no cancelados; el ticket, de los
  confirmados en adelante. El IVA está pendiente de confirmar.
- **Impacto esperado.** Plazos fiables para el 75,8 % de los pares y el 79,4 %
  del importe de la demanda, que son de pedidos Custom.
- **Prioridad 3** (urgencia media). Sustento: `custom_vs_estandar.csv` y los
  gráficos `06_custom_vs_estandar.png` y `09_importe_por_tipo.png`.

## 3. Unos pocos clientes concentran el importe

*Procede de datos sintéticos.*

- **Evidencia.** 7 «Mejores clientes» (17,5 % de los clientes) suman el 45,4 %
  del importe vendido. Hay 6 clientes «En riesgo» con el 10,5 %.
- **Interpretación.** Perder a uno de los mejores clientes se notaría mucho en la
  venta. Los que están en riesgo compraban a menudo y han dejado de hacerlo.
- **Decisión.** Cuidar a los mejores clientes (prioridad en plazos) y contactar
  primero a los que están en riesgo.
- **Limitación.** Los segmentos son quintiles relativos con la fecha de corte
  como referencia, sobre 40 clientes simulados.
- **Impacto esperado.** Conservar el 45,4 % del importe vendido (mejores
  clientes) y recuperar parte del 10,5 % que suman los clientes en riesgo.
- **Prioridad 4** (urgencia media). Sustento: `rfm_segmentos.csv`,
  `rfm_clientes.csv` y la dispersión RFM de la pestaña Clientes.

## 4. Riesgo de quedarse sin stock

*Procede de datos sintéticos.*

- **Evidencia.** 33 de 216 SKU tienen menos de 10 pares. 9 de ellos se pidieron
  en los últimos 28 días (47 pares). El modelo con más demanda entre ellos es
  SINT Flex.
- **Interpretación.** Una referencia con poco stock y pedidos recientes es la que
  antes se puede quedar sin existencias.
- **Decisión.** Reponer primero esos 9 SKU, empezando por las tallas que más se
  piden.
- **Limitación.** El stock es una foto en la fecha de corte, y la demanda de 28
  días no es una previsión.
- **Impacto esperado.** Evitar roturas de stock en 9 SKU que suman 47 pares
  pedidos en los últimos 28 días.
- **Prioridad 2** (urgencia alta). Sustento: `stock_variantes.csv`,
  `stock_bajo.csv` y el gráfico `08_stock_por_sku.png`.

## 5. La predicción no mejora al método sencillo

*Procede de una predicción sobre datos sintéticos.*

- **Evidencia.** Evaluación de 2026-08 a 2026-10, con 36 predicciones:

  | Método | MAE (pares) | RMSE (pares) |
  |---|---|---|
  | Baseline (mes anterior) | 25,03 | 37,42 |
  | Regresión lineal | 26,28 | 36,15 |

  Solo mejora en una métrica: el RMSE sí, el MAE no.
- **Interpretación.** La demanda depende de pedidos Custom que llegan a saltos:
  ni el mes anterior ni la regresión los anticipan bien.
- **Decisión.** No usar la regresión para planificar: seguir con el dato del mes
  anterior y revisar a mano los pedidos Custom confirmados.
- **Limitación.** Solo hay 36 predicciones de 3 meses; con otros meses el
  resultado podría cambiar.
- **Impacto esperado.** No añadir un método que no reduce el error: MAE de 25,03
  pares con el baseline y de 26,28 con la regresión, por modelo y mes.
- **Prioridad 5** (urgencia baja: la decisión es no cambiar el método). Sustento:
  `metricas_prediccion.csv`, `predicciones.csv` y el gráfico
  `11_real_frente_a_prediccion.png`.

## Con la exportación de PRUEBA de Acceso a Datos

Son 12 pedidos de un solo día, y no son ventas reales.

| Conclusión | Resultado | Prioridad |
|---|---|---|
| 1 | 1 de 7 modelos (NOVA Velocity) suma el 91,1 % de los pares, por dos pedidos Custom de 40 pares: NOVA-0011 (pendiente) y CUSTOM-40 (confirmado), que quizá sean el mismo encargo (pendiente de decidir) | 1 (alta) |
| 2 | Los Custom son el 41,7 % de los pedidos, pero el 92,2 % de los pares y el 93,3 % del importe | 2 (media) |
| 3 | NO CALCULABLE: 1 cliente con compras válidas, y hacen falta 10 | 3 (baja) |
| 4 | Ningún SKU por debajo del umbral: no hay riesgo inmediato | 4 (baja) |
| 5 | NO CALCULABLE: ningún mes completo | 5 (baja) |

Ninguna de estas conclusiones se puede presentar como resultado comercial de
NOVA. Para eso hace falta la exportación de la base del equipo (`Tipo: REAL` en
`ORIGEN.txt`) y un historial de varios meses.
