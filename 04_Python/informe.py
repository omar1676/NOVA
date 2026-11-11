"""
Informe ejecutivo: cinco conclusiones para produccion y comercial (apartado 6.11).

Cada conclusion sale de una tabla ya calculada (no hay cifras escritas a mano)
y separa la evidencia (que pasa), la interpretacion (por que podria pasar), la
decision (que hacer) y la limitacion. Dice siempre de donde procede: datos de
prueba de ACC, datos sinteticos o una prediccion. Si una tabla no se puede
calcular, la conclusion lo dice en vez de inventar una cifra.

Ademas, cada una lleva el impacto esperado (que parte de la demanda, del
importe o del stock toca la decision, con su cifra), la tabla y el grafico que
la sustentan y su prioridad. Criterio de prioridad (1 = la primera):
  1. la urgencia:
       alta   si no se actua, se puede dejar sin servir demanda que ya existe
              (modelos que concentran los pares, referencias que se agotan);
       media  sirve para planificar el proximo mes (capacidad, clientes);
       baja   todavia no se puede decidir con datos (NO CALCULABLE) o la
              decision es no cambiar nada;
  2. con la misma urgencia, el orden del informe (el numero).

Se calculan con el conjunto completo, sin filtros.
"""
import pandas as pd

import config
from analiticas import NO_CALCULABLE, es_no_calculable
from segmentacion import SIN_COMPRAS

# Orden de las urgencias para la prioridad
URGENCIAS = {"alta": 1, "media": 2, "baja": 3}
# Tabla y grafico de los que sale cada conclusion (outputs/ y la pestana del dashboard)
SUSTENTO = {
    1: "modelos_abc.csv · gráfico 02_pareto_modelos.png (pestaña Productos)",
    2: "custom_vs_estandar.csv · gráficos 06_custom_vs_estandar.png y 09_importe_por_tipo.png (pestaña Productos)",
    3: "rfm_segmentos.csv y rfm_clientes.csv · dispersión RFM de la pestaña Clientes",
    4: "stock_variantes.csv y stock_bajo.csv · gráfico 08_stock_por_sku.png (pestaña Inventario)",
    5: "metricas_prediccion.csv y predicciones.csv · gráfico 11_real_frente_a_prediccion.png (pestaña Predicción)",
}

PROCEDENCIA = {
    "PRUEBA": "Datos de prueba (exportación de ACC)",
    "SINTETICO": "Datos sintéticos",
    "REAL": "Datos reales (exportación de ACC)",
}
LIMITE_ORIGEN = {
    "PRUEBA": "Exportación de PRUEBA: no son ventas reales de NOVA.",
    "SINTETICO": "Simulación de generador_datos.py: no son ventas ni clientes reales de NOVA.",
    "REAL": "",
}


def numero(valor, decimales=0):
    """Numero al estilo espanol: 1.234,5"""
    texto = f"{float(valor):,.{decimales}f}"   # formato ingles: 1,234.5
    texto = texto.replace(",", "_")             # 1_234.5 (los miles, aparte un momento)
    texto = texto.replace(".", ",")             # 1_234,5 (coma decimal)
    return texto.replace("_", ".")              # 1.234,5 (punto de miles)


def conclusion(numero_, titulo, procede_de, evidencia, interpretacion, decision, limitacion, calculable=True,
               urgencia="baja", impacto="Ninguno todavía: no hay datos para decidir."):
    """
    Una conclusion del informe. numero_ lleva "_" para no tapar la funcion numero().
    Sin datos (calculable=False), la urgencia es baja y no hay impacto que esperar.
    """
    return {"numero": numero_, "titulo": titulo, "procede_de": procede_de, "calculable": calculable,
            "evidencia": evidencia, "interpretacion": interpretacion, "decision": decision,
            "limitacion": limitacion.strip(), "urgencia": urgencia, "impacto_esperado": impacto,
            "sustento": SUSTENTO[numero_]}


def concentracion_modelos(abc, procede_de, limite):
    if es_no_calculable(abc) or abc["pares"].sum() == 0:
        return conclusion(1, "La demanda se concentra en pocos modelos", procede_de,
                          f"{NO_CALCULABLE}: no hay pares de demanda.", "-", "Esperar a tener pedidos.", limite, False)
    clase_a = abc[abc["clase_abc"] == "A"]
    primero = abc.iloc[0]
    if len(clase_a) == 1:
        verbo = "suma"
    else:
        verbo = "suman"
    return conclusion(
        1, "La demanda se concentra en pocos modelos", procede_de,
        f"{len(clase_a)} de {len(abc)} modelos (clase A) {verbo} el "
        f"{numero(clase_a['peso_pct'].sum(), 1)} % de los "
        f"pares solicitados. El más pedido, {primero['nombre_modelo']}, aporta el {numero(primero['peso_pct'], 1)} % "
        f"({numero(primero['pares'])} pares).",
        "La producción depende de pocos modelos: quedarse sin stock de uno de clase A afecta a una gran parte "
        "de la demanda.",
        "Priorizar materiales, capacidad y stock de los modelos A; revisar los de clase C antes de fabricar más.",
        f"Pares de pedidos no cancelados (demanda), no ventas cobradas. {limite}",
        urgencia="alta",
        impacto=f"Mantener servida la demanda de los modelos A: el {numero(clase_a['peso_pct'].sum(), 1)} % de los "
                f"pares solicitados ({numero(clase_a['pares'].sum())} pares).")


def peso_custom(tabla, procede_de, limite):
    custom = tabla[tabla["tipo_pedido"] == "custom"].iloc[0]
    normal = tabla[tabla["tipo_pedido"] == "normal"].iloc[0]
    if custom["pedidos_demanda"] == 0:
        return conclusion(2, "Los pedidos Custom mueven la mayor parte del volumen", procede_de,
                          "No hay pedidos Custom de demanda.", "-", "-", limite, False)
    tickets = []
    for nombre, fila in [("Custom", custom), ("estándar", normal)]:
        ticket = fila["ticket_medio_venta"]
        if pd.notna(ticket):
            tickets.append(f"{nombre} {numero(ticket, 2)} €")
        else:
            tickets.append(f"{nombre} sin ventas confirmadas")
    return conclusion(
        2, "Los pedidos Custom mueven la mayor parte del volumen", procede_de,
        f"Los Custom son el {numero(custom['cuota_pedidos_pct'], 1)} % de los pedidos de demanda, pero el "
        f"{numero(custom['cuota_pares_pct'], 1)} % de los pares y el {numero(custom['cuota_importe_pct'], 1)} % del "
        f"importe. Ticket medio de venta: {' frente a '.join(tickets)}.",
        "Pocos encargos de clubes y equipos concentran el volumen: un solo pedido Custom cambia la carga de "
        "producción de un mes.",
        "Planificar la capacidad alrededor de los pedidos Custom (plazos y tallas por equipo) y seguirlos uno a uno.",
        f"Cuotas de pedidos no cancelados; el ticket, de pedidos confirmados en adelante. IVA {config.IVA}. {limite}",
        urgencia="media",
        impacto=f"Plazos fiables para el {numero(custom['cuota_pares_pct'], 1)} % de los pares y el "
                f"{numero(custom['cuota_importe_pct'], 1)} % del importe de la demanda, que son de pedidos Custom.")


def clientes_rfm(resumen, procede_de, limite):
    # El mismo minimo que segmentacion.puntuar: con menos clientes con compras no hay segmentos
    con_compras = int(resumen.loc[resumen["segmento"] != SIN_COMPRAS, "clientes"].sum())
    if con_compras < config.MINIMO_CLIENTES_RFM:
        return conclusion(
            3, "Segmentos de clientes", procede_de,
            f"{NO_CALCULABLE}: {con_compras} cliente(s) con compras válidas; hacen falta "
            f"al menos {config.MINIMO_CLIENTES_RFM} para repartir los segmentos RFM.",
            "Con tan pocos clientes, cualquier segmento sería arbitrario.",
            "No segmentar todavía: repetir el análisis cuando haya más clientes con pedidos confirmados.",
            limite, False)
    por_segmento = resumen.set_index("segmento")
    mejores = por_segmento.loc["Mejores clientes"]
    riesgo = por_segmento.loc["En riesgo"]
    return conclusion(
        3, "Unos pocos clientes concentran el importe", procede_de,
        f"{int(mejores['clientes'])} «Mejores clientes» ({numero(mejores['porcentaje_clientes'], 1)} % de los "
        f"clientes) suman el {numero(mejores['porcentaje_importe'], 1)} % del importe vendido. Hay "
        f"{int(riesgo['clientes'])} clientes «En riesgo» con el {numero(riesgo['porcentaje_importe'], 1)} %.",
        "Perder a uno de los mejores clientes se notaría mucho en la venta; los que están en riesgo compraban "
        "a menudo y han dejado de hacerlo.",
        "Cuidar a los mejores clientes (prioridad en plazos) y contactar primero a los que están en riesgo.",
        f"Segmentos por quintiles relativos, con la fecha de corte como referencia. {limite}",
        urgencia="media",
        impacto=f"Conservar el {numero(mejores['porcentaje_importe'], 1)} % del importe vendido (mejores clientes) "
                f"y recuperar parte del {numero(riesgo['porcentaje_importe'], 1)} % que suman los clientes en riesgo.")


def riesgo_stock(stock, procede_de, limite):
    titulo = "Riesgo de quedarse sin stock"
    if len(stock) == 0:
        return conclusion(4, titulo, procede_de, "No hay stock exportado.", "-", "-", limite, False)
    bajos = stock[stock["alerta_stock_bajo"]]
    en_riesgo = bajos[bajos["demanda_28d"] > 0]
    evidencia = (f"{len(bajos)} de {len(stock)} SKU tienen menos de {config.UMBRAL_STOCK_BAJO} pares. "
                 f"{len(en_riesgo)} de ellos se pidieron en los últimos {config.DIAS_DEMANDA} días "
                 f"({numero(en_riesgo['demanda_28d'].sum())} pares).")
    if len(en_riesgo) == 0:
        interpretacion = "Ninguna referencia combina poco stock y pedidos recientes: no hay riesgo inmediato."
        decision = "No hace falta reponer con urgencia; vigilar el stock de los modelos de clase A."
        impacto = "Ninguno inmediato: ninguna referencia combina poco stock y pedidos recientes."
        if len(bajos) == 0:
            urgencia = "baja"
        else:
            urgencia = "media"   # hay stock bajo, pero sin pedidos recientes
    else:
        modelo = en_riesgo.groupby("nombre_modelo")["demanda_28d"].sum().sort_values(ascending=False)
        evidencia += f" El modelo con más demanda entre ellos es {modelo.index[0]}."
        interpretacion = "Una referencia con poco stock y pedidos recientes es la que antes se puede quedar sin existencias."
        decision = (f"Reponer primero los {len(en_riesgo)} SKU con stock bajo y demanda reciente, empezando por las "
                    "tallas que más se piden.")
        urgencia = "alta"
        impacto = (f"Evitar roturas de stock en {len(en_riesgo)} SKU que suman "
                   f"{numero(en_riesgo['demanda_28d'].sum())} pares pedidos en los últimos {config.DIAS_DEMANDA} días.")
    return conclusion(
        4, titulo, procede_de, evidencia, interpretacion, decision,
        f"El stock es una foto en la fecha de corte; la demanda de {config.DIAS_DEMANDA} días no es una previsión. "
        f"{limite}", urgencia=urgencia, impacto=impacto)


def prediccion_frente_a_baseline(metricas, tipo, limite):
    procede_de = f"Predicción · {PROCEDENCIA.get(tipo, 'Origen desconocido')}"
    if es_no_calculable(metricas):
        return conclusion(
            5, "La predicción de demanda todavía no se puede evaluar", procede_de,
            f"{NO_CALCULABLE}: {metricas['motivo'].iloc[0]}.",
            "Sin varios meses completos no se puede entrenar ni evaluar un modelo.",
            "Planificar con la demanda conocida y repetir la evaluación con un historial más largo.",
            limite, False)
    por_metodo = metricas.set_index("metodo")
    baseline = por_metodo.loc["baseline"]
    regresion = por_metodo.loc["regresion"]
    mejora = regresion["mejora_al_baseline"].startswith("sí")
    errores = (f"MAE {numero(baseline['mae'], 2)} pares con el baseline y {numero(regresion['mae'], 2)} con la "
               "regresión, por modelo y mes")
    if mejora:
        titulo = "La predicción mejora al método sencillo"
        interpretacion = "La regresión aprende algo que el mes anterior no recoge."
        decision = "Usar la regresión como apoyo y compararla cada mes con el baseline."
        urgencia = "media"
        impacto = f"Planificar con menos error: {errores}."
    else:
        titulo = "La predicción no mejora al método sencillo"
        interpretacion = ("La demanda depende de pedidos Custom que llegan a saltos: ni el mes anterior ni la "
                          "regresión los anticipan bien.")
        decision = ("No usar la regresión para planificar: seguir con el dato del mes anterior y revisar a mano "
                    "los pedidos Custom confirmados.")
        urgencia = "baja"   # la decision es no cambiar el metodo actual
        impacto = f"No añadir un método que no reduce el error: {errores}."
    return conclusion(
        5, titulo, procede_de,
        f"Evaluación {baseline['periodo_evaluacion']} ({int(baseline['filas_evaluacion'])} predicciones): baseline "
        f"(mes anterior) MAE {numero(baseline['mae'], 2)} y RMSE {numero(baseline['rmse'], 2)} pares; regresión "
        f"lineal MAE {numero(regresion['mae'], 2)} y RMSE {numero(regresion['rmse'], 2)}. ¿Mejora? "
        f"{regresion['mejora_al_baseline']}.",
        interpretacion,
        decision,
        f"Solo {int(baseline['filas_evaluacion'])} predicciones de 3 meses; el resultado podría cambiar con otros "
        f"meses. {limite}", urgencia=urgencia, impacto=impacto)


def conclusiones(tablas, resumen_rfm, metricas_prediccion, tipo):
    """
    Las cinco conclusiones en un DataFrame. tablas son las de
    analiticas.calcular_tablas (sin filtros), resumen_rfm el de
    segmentacion.resumen_segmentos y metricas_prediccion la tabla de
    prediccion.predecir_demanda. tipo es PRUEBA, SINTETICO o REAL.
    """
    procede_de = PROCEDENCIA.get(tipo, "Origen desconocido")
    limite = LIMITE_ORIGEN.get(tipo, "No se sabe de qué base salen los datos.")
    tabla = pd.DataFrame([
        concentracion_modelos(tablas["modelos_abc"], procede_de, limite),
        peso_custom(tablas["custom_vs_estandar"], procede_de, limite),
        clientes_rfm(resumen_rfm, procede_de, limite),
        riesgo_stock(tablas["stock_variantes"], procede_de, limite),
        prediccion_frente_a_baseline(metricas_prediccion, tipo, limite),
    ])
    # Prioridad 1 a 5: primero la urgencia y, con la misma, el numero (alta 1 -> 11, media 2 -> 22...)
    clave = tabla["urgencia"].map(URGENCIAS) * 10 + tabla["numero"]
    tabla["prioridad"] = clave.rank(method="first").astype(int)
    # Las columnas nuevas, al final: las de antes no cambian de sitio
    return tabla[["numero", "titulo", "procede_de", "calculable", "evidencia", "interpretacion", "decision",
                  "limitacion", "prioridad", "urgencia", "impacto_esperado", "sustento"]]
