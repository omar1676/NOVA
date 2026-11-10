"""
Metadatos de cada DataFrame de resultados (apartado 6.15): la fecha de corte,
las reglas de negocio, los filtros, las filas de origen y la funcion que lo
ha generado.

Cada CSV de outputs/ ya lleva en sus columnas el origen (REAL, PRUEBA o
SINTETICO) y el momento de la ejecucion. Lo demas no cabe en cada fila sin
repetirlo cientos de veces, asi que main.py lo guarda aparte, en
metadatos_dataframes.csv: una fila por CSV, que se enlaza por el nombre del
archivo y la columna ejecucion.

El dashboard, en cambio, lo mete dentro de cada descarga (columnas
fecha_corte, funcion, reglas_de_negocio y filas_origen), con los filtros que
se estan usando.
"""
import pandas as pd

import config
import filtros

# Que filtros del dashboard se aplican a cada DataFrame
TODOS = "todos"                       # periodo, modelo, talla, tipo, estado y cliente
MODELO_Y_TALLA = "modelo y talla"     # el stock: es una foto en la fecha de corte
NINGUNO = "ninguno"                   # resultados globales (calidad, RFM, prediccion...)

# Las cinco tablas de la exportacion
TODAS = ["clientes", "modelos", "pedidos", "lineas_pedido", "stock"]
PEDIDOS = ["pedidos", "lineas_pedido"]

DEMANDA = "demanda = pedidos no cancelados"
VENTA = "venta = pedidos " + ", ".join(config.ESTADOS_CONFIRMADOS)
SOLO_VALIDAS = "solo filas válidas (sin las rechazadas por las 12 reglas)"

# nombre del DataFrame (y de su CSV) -> (funcion que lo genera, tablas de entrada, reglas de negocio, filtros)
DATAFRAMES = {
    # Calidad: se calculan con las filas tal como llegan (leidas)
    "incidencias": ("calidad.evaluar", TODAS,
                    "las 12 reglas de calidad_datos.md; cada incidencia es bloqueante, recuperable o advertencia",
                    NINGUNO),
    "resumen_calidad": ("calidad.resumen_calidad", TODAS,
                        "filas recibidas, válidas y rechazadas de cada tabla con las 12 reglas", NINGUNO),
    "filas_rechazadas": ("calidad.separar", TODAS,
                         "una incidencia recuperable aparta la fila (y su pedido entero); las advertencias no "
                         "apartan nada", NINGUNO),
    "nulos_por_columna": ("calidad.nulos_por_columna", TODAS, "celdas vacías de cada columna, sin convertir nada",
                          NINGUNO),
    "estado_ejecucion": ("main.ejecutar", TODAS,
                         "CORRECTO, BLOQUEADO o NO CUADRA CON SQL: dice si las demás cifras de la carpeta son de "
                         "esta ejecución", NINGUNO),
    # Analisis (fases 2 y 3)
    "pedidos_unicos": ("analiticas.df_pedidos_unicos", ["clientes"] + PEDIDOS,
                       f"una fila por pedido; pares e importe sumados desde sus líneas; {SOLO_VALIDAS}", TODOS),
    "pedidos_por_estado": ("analiticas.pedidos_por_estado", PEDIDOS,
                           "todos los estados del catálogo, también los cancelados (un estado sin pedidos, 0)",
                           TODOS),
    "pedidos_por_estado_pago": ("analiticas.pedidos_por_estado_pago", PEDIDOS,
                                "estado_pago tal como lo marca Acceso a Datos: no es un cobro comprobado", TODOS),
    "ventas_por_periodo": ("analiticas.ventas_por_periodo", PEDIDOS,
                           f"{VENTA}; por mes de fecha_pedido; un mes sin ventas dentro del periodo, 0", TODOS),
    "modelos_abc": ("analiticas.modelos_abc", ["modelos"] + PEDIDOS,
                    f"{DEMANDA}; ABC por pares: A hasta el {config.ABC_LIMITE_A} %, B hasta el {config.ABC_LIMITE_B} %",
                    TODOS),
    "ventas_por_talla": ("analiticas.ventas_por_talla", PEDIDOS, f"{DEMANDA}; pares por talla", TODOS),
    "matriz_modelo_talla": ("analiticas.matriz_modelo_talla", ["modelos"] + PEDIDOS,
                            f"{DEMANDA}; pares por modelo y talla (0 si no hay)", TODOS),
    "matriz_modelo_talla_proporcion": ("analiticas.proporcion_tallas", ["modelos"] + PEDIDOS,
                                       f"{DEMANDA}; cada fila (modelo) suma 1", TODOS),
    "matriz_modelo_mes": ("analiticas.matriz_modelo_mes", ["modelos"] + PEDIDOS,
                          f"{DEMANDA}; pares por modelo y mes del pedido", TODOS),
    "custom_vs_estandar": ("analiticas.custom_vs_estandar", PEDIDOS,
                           f"cancelación sobre pedidos registrados; cuotas de la {DEMANDA}; importe y ticket de la "
                           f"{VENTA}", TODOS),
    "clientes_actividad": ("analiticas.clientes_actividad", ["clientes"] + PEDIDOS,
                           "todos los clientes, también sin pedidos (con 0); registrados, demanda y venta por separado; "
                           "sin nombres", TODOS),
    "cohortes": ("analiticas.cohortes", PEDIDOS,
                 f"{VENTA}; cohorte = mes de la primera compra; hacen falta ventas de 2 meses", TODOS),
    "stock_variantes": ("analiticas.stock_variantes", ["modelos", "stock"] + PEDIDOS,
                        f"stock = foto en la fecha de corte; demanda de los {config.DIAS_DEMANDA} días anteriores "
                        f"(no cancelados); alerta con menos de {config.UMBRAL_STOCK_BAJO} pares en main.py (el "
                        "dashboard deja cambiar el umbral); cobertura = stock / (demanda de 28 días / 4)",
                        MODELO_Y_TALLA),
    "stock_bajo": ("analiticas.stock_bajo", ["modelos", "stock"] + PEDIDOS,
                   "las referencias de stock_variantes bajo el umbral, de menos a más stock", MODELO_Y_TALLA),
    "anomalias": ("analiticas.anomalias_iqr", ["modelos"] + PEDIDOS,
                  f"regla del IQR (1,5) en grupos comparables de al menos {config.MINIMO_MUESTRA_IQR} valores; no se "
                  "borra ninguna línea", NINGUNO),
    "precio_y_margen": ("analiticas.precio_y_margen", ["modelos"] + PEDIDOS,
                        f"{DEMANDA}; precio medio = importe / pares; margen NO CALCULABLE sin coste unitario", TODOS),
    "importes_por_criterio": ("analiticas.importes_por_criterio", PEDIDOS,
                              f"registrados, no cancelados y confirmados en adelante; ninguno es un cobro; IVA "
                              f"{config.IVA}", NINGUNO),
    "kpis": ("kpis.calcular_kpis", ["modelos", "stock"] + PEDIDOS,
             "cada KPI dice su fórmula y su población (todos, demanda, venta, pagado o stock)", TODOS),
    # Conciliacion con SQL
    "conciliacion_sql": ("conciliacion.conciliar", ["modelos"] + PEDIDOS,
                         "frente a P-A, P-B y P-C de 12_consultas_panel.sql; euros iguales con medio céntimo, el resto "
                         "exacto", NINGUNO),
    "coherencia_kpis_sql": ("kpis.coherencia_con_sql", PEDIDOS, "K01 a K07 frente a P-A y P-B", NINGUNO),
    "contraste_sql_caso_n": ("conciliacion.contrastar_caso_n", ["clientes", "modelos"] + PEDIDOS,
                             f"caso N frente a N-1, N-2 y N-3: {VENTA} de un mes, celdas de la matriz de demanda y "
                             "clientes distintos", NINGUNO),
    # Estadistica (fase 4)
    "estadisticos_descriptivos": ("estadistica.descriptivos", PEDIDOS,
                                  "importe y pares por pedido y precio unitario, en total y por tipo de pedido",
                                  NINGUNO),
    "hipotesis": ("estadistica.contrastar_hipotesis", PEDIDOS,
                  f"bootstrap de {config.BOOTSTRAP_REMUESTREOS} remuestreos con semilla {config.SEMILLA}; con menos "
                  f"de {config.MINIMO_MUESTRA_HIPOTESIS} valores, evidencia insuficiente", NINGUNO),
    "bootstrap_ticket_medio": ("estadistica.bootstrap_ticket_medio", PEDIDOS,
                               f"{VENTA}; intervalo del {config.NIVEL_CONFIANZA} % con semilla {config.SEMILLA}",
                               NINGUNO),
    # Segmentacion y prediccion (fase 5): siempre con todos los datos
    "rfm_clientes": ("segmentacion.rfm", ["clientes"] + PEDIDOS,
                     f"{VENTA} hasta la fecha de corte; F = pedidos (no líneas); quintiles de 1 a 5; la columna "
                     "cluster es la de segmentacion.kmeans_clientes", NINGUNO),
    "rfm_segmentos": ("segmentacion.resumen_segmentos", ["clientes"] + PEDIDOS,
                      f"segmentos por reglas de R, F y M; hacen falta {config.MINIMO_CLIENTES_RFM} clientes con compras",
                      NINGUNO),
    "kmeans_seleccion_k": ("segmentacion.kmeans_clientes", ["clientes"] + PEDIDOS,
                           f"k de {config.KMEANS_K[0]} a {config.KMEANS_K[-1]}; se elige el de mayor silhouette; hacen "
                           f"falta {config.MINIMO_CLIENTES_KMEANS} clientes con compras", NINGUNO),
    "kmeans_clusters": ("segmentacion.describir_clusters", ["clientes"] + PEDIDOS,
                        "grupos matemáticos de R, F y M estandarizados: no son categorías comerciales", NINGUNO),
    "rfm_frente_a_kmeans": ("segmentacion.comparar_rfm_kmeans", ["clientes"] + PEDIDOS,
                            "clientes de cada segmento RFM en cada grupo de KMeans", NINGUNO),
    "demanda_mensual_modelo": ("prediccion.demanda_mensual", ["modelos"] + PEDIDOS,
                               f"{DEMANDA}; pares por modelo y mes completo hasta la fecha de corte", NINGUNO),
    "predicciones": ("prediccion.predecir_demanda", ["modelos"] + PEDIDOS,
                     f"los {config.MESES_EVALUACION} últimos meses para evaluar; solo variables conocidas antes del "
                     "mes; baseline = pares del mes anterior", NINGUNO),
    "metricas_prediccion": ("prediccion.predecir_demanda", ["modelos"] + PEDIDOS,
                            "MAE y RMSE del baseline y de la regresión; solo mejora si bajan los dos", NINGUNO),
    "errores_por_modelo": ("prediccion.errores_por_modelo", ["modelos"] + PEDIDOS,
                           "MAE de cada método por modelo en los meses de evaluación", NINGUNO),
    "coeficientes_regresion": ("prediccion.predecir_demanda", ["modelos"] + PEDIDOS,
                               "LinearRegression entrenada solo con los meses de entrenamiento", NINGUNO),
    "informe_ejecutivo": ("informe.conclusiones", TODAS,
                          "cinco conclusiones; prioridad por urgencia y, con la misma, por número; sin filtros",
                          NINGUNO),
}

# Los DataFrames de calidad cuentan las filas leidas; el resto, las validas
DE_FILAS_LEIDAS = ["incidencias", "resumen_calidad", "filas_rechazadas", "nulos_por_columna", "estado_ejecucion"]


def contar(tablas):
    """Filas de cada tabla de un diccionario de DataFrames."""
    return {nombre: len(tabla) for nombre, tabla in tablas.items()}


def fecha_corte(datos):
    """La fecha de corte de la exportacion (la de stock.csv) en texto."""
    if "stock" not in datos or datos["stock"]["fecha_corte"].isna().all():
        return "desconocida: no se ha podido leer stock.csv"
    return datos["stock"]["fecha_corte"].max().strftime(config.FORMATO_FECHA)


def fila(nombre, filas_resultado, corte, entradas, clase, texto_filtros):
    """
    Los metadatos de un DataFrame. entradas: filas de cada tabla de la
    exportacion (de contar); clase: "leídas" o "válidas".
    """
    funcion, tablas, reglas, _ = DATAFRAMES[nombre]
    partes = []
    for tabla in tablas:
        if tabla in entradas:
            partes.append(f"{tabla}: {entradas[tabla]} {clase}")
        else:
            partes.append(f"{tabla}: no se ha podido leer")
    return {"dataframe": nombre, "funcion": funcion, "fecha_corte": corte, "reglas_de_negocio": reglas,
            "filtros": texto_filtros, "filas_origen": "; ".join(partes), "filas_resultado": filas_resultado}


def tabla(guardados, datos, validos):
    """
    metadatos_dataframes.csv de main.py: una fila por cada CSV guardado, sin
    filtros. guardados: lista de (archivo, filas); datos y validos: los de
    calidad.evaluar.
    """
    corte = fecha_corte(datos)
    filas = []
    for archivo, filas_resultado in guardados:
        nombre = archivo.removesuffix(".csv")
        if nombre in DE_FILAS_LEIDAS:
            filas.append(fila(nombre, filas_resultado, corte, contar(datos), "leídas", "ninguno"))
        else:
            filas.append(fila(nombre, filas_resultado, corte, contar(validos), "válidas", "ninguno"))
    resultado = pd.DataFrame(filas)
    resultado.insert(1, "archivo", [archivo for archivo, _ in guardados])
    return resultado


def filtros_que_usa(nombre, elegidos):
    """Los filtros del dashboard que se aplican de verdad a un DataFrame."""
    alcance = DATAFRAMES[nombre][3]
    if alcance == TODOS:
        return elegidos
    if alcance == MODELO_Y_TALLA:
        return {**filtros.SIN_FILTROS, "modelos": elegidos.get("modelos") or [], "tallas": elegidos.get("tallas") or []}
    return dict(filtros.SIN_FILTROS)


def texto_filtros(nombre, elegidos):
    """Los filtros de un DataFrame del dashboard en una linea (para la columna filtros de su descarga)."""
    if DATAFRAMES[nombre][3] == NINGUNO:
        return "ninguno (resultado global)"
    return filtros.describir(filtros_que_usa(nombre, elegidos))


def del_dashboard(nombre, filas_resultado, datos, validos, elegidos):
    """Los metadatos de un DataFrame del dashboard, con las filas de origen que dejan sus filtros."""
    usados = filtros_que_usa(nombre, elegidos)
    filtrados = filtros.filtrar_validos(validos, usados)
    if DATAFRAMES[nombre][3] == MODELO_Y_TALLA:
        filtrados["stock"] = filtros.filtrar_stock(validos, usados)
    return fila(nombre, filas_resultado, fecha_corte(datos), contar(filtrados), "válidas",
                texto_filtros(nombre, elegidos))
