"""
Indicadores (KPIs) de NOVA Sneakers, apartado 6.5 de la rubrica.

Cada KPI es una fila con: codigo, nombre, valor, unidad, detalle, formula,
poblacion (que pedidos cuenta), tabla_origen (de que tabla sale) y estado.

Poblaciones (config.py):
  todos     todos los pedidos validos, en cualquier estado
  demanda   pedidos no cancelados
  venta     pedidos confirmados en adelante
  pagado    estado_pago = "pagado" (lo que marca Acceso a Datos; no es caja)

Nunca se calcula un margen sin coste, ni se supone IVA ni cobros. Si un KPI
no se puede calcular, su estado es NO CALCULABLE y el detalle dice por que.
Todos usan las mismas funciones que las tablas: no hay dos formulas para lo mismo.
"""
import pandas as pd

import config
import conciliacion
from analiticas import NO_CALCULABLE, de_demanda, de_venta, dividir, porcentaje

COLUMNAS = ["codigo", "nombre", "valor", "unidad", "detalle", "formula", "poblacion", "tabla_origen", "estado"]


def kpi(codigo, nombre, valor, unidad, formula, poblacion, origen, detalle=""):
    """Un KPI calculado. Si el valor sale nulo (division por 0), su estado es 'sin datos'."""
    estado = "calculado" if valor is not None else "sin datos"
    return {"codigo": codigo, "nombre": nombre, "valor": valor, "unidad": unidad, "detalle": detalle,
            "formula": formula, "poblacion": poblacion, "tabla_origen": origen, "estado": estado}


def kpi_no_calculable(codigo, nombre, unidad, formula, poblacion, origen, motivo):
    """Un KPI sin valor: estado NO CALCULABLE y el motivo en el detalle."""
    fila = kpi(codigo, nombre, None, unidad, formula, poblacion, origen, motivo)
    fila["estado"] = NO_CALCULABLE
    return fila


def mas_solicitado(codigo, nombre, tabla, etiqueta, origen):
    """
    El elemento con mas pares de demanda (modelo o talla). Si hay empate se
    nombran todos: no se elige uno a dedo.
    """
    formula = f"máximo de pares de demanda por {etiqueta}"
    if len(tabla) == 0 or tabla["pares"].max() == 0:
        return kpi(codigo, nombre, None, "pares", formula, "demanda", origen, "no hay demanda")
    maximo = int(tabla["pares"].max())
    ganadores = tabla.loc[tabla["pares"] == maximo, etiqueta].astype(str)
    peso = porcentaje(maximo, tabla["pares"].sum())
    detalle = f"{', '.join(ganadores)}: {peso} % de los pares de demanda"
    return kpi(codigo, nombre, maximo, "pares", formula, "demanda", origen, detalle)


def calcular_kpis(pedidos, tabla_abc, tabla_tallas, tabla_stock, tabla_meses):
    """
    Los KPIs a partir de df_pedidos_unicos y de las tablas de analiticas.py.
    Devuelve un DataFrame con una fila por KPI.
    """
    demanda = de_demanda(pedidos)
    venta = de_venta(pedidos)
    pagados = pedidos[pedidos["estado_pago"] == config.ESTADO_PAGADO]
    pares_venta = int(venta["pares"].sum())
    importe_venta = round(float(venta["importe"].sum()), 2)
    origen = "df_pedidos_unicos"
    lista = [
        kpi("K01", "Pedidos registrados", len(pedidos), "pedidos",
            "nº de pedidos (una fila por pedido)", "todos", origen),
        kpi("K02", "Pedidos confirmados", len(venta), "pedidos",
            "nº de pedidos con estado " + ", ".join(config.ESTADOS_CONFIRMADOS), "venta", origen),
        kpi("K03", "Pedidos cancelados", int(pedidos["es_cancelado"].sum()), "pedidos",
            "nº de pedidos con estado cancelado", "todos", origen),
        kpi("K04", "Pares solicitados", int(demanda["pares"].sum()), "pares",
            "suma de pares de los pedidos no cancelados", "demanda", origen,
            "mismo criterio que la consulta P-A de Acceso a Datos"),
        kpi("K05", "Pares confirmados", pares_venta, "pares",
            "suma de pares de los pedidos confirmados en adelante", "venta", origen),
        kpi("K06", "Importe registrado", round(float(pedidos["importe"].sum()), 2), "€",
            "suma del importe de todos los pedidos", "todos", origen,
            "incluye pendientes y cancelados: no es venta. IVA " + config.IVA),
        kpi("K07", "Importe confirmado", importe_venta, "€",
            "suma del importe de los pedidos confirmados en adelante", "venta", origen,
            "no es dinero cobrado. IVA " + config.IVA),
        kpi("K08", "Importe con pago registrado", round(float(pagados["importe"].sum()), 2), "€",
            "suma del importe de los pedidos con estado_pago = pagado", "pagado", origen,
            "lo que Acceso a Datos marca como pagado; no es un cobro comprobado"),
        kpi("K09", "Ticket medio", dividir(importe_venta, len(venta)), "€/pedido",
            "K07 / K02 (se divide entre pedidos, nunca entre líneas)", "venta", origen,
            f"muestra: {len(venta)} pedido(s)"),
        kpi("K10", "Pares por pedido", dividir(pares_venta, len(venta), 1), "pares/pedido",
            "K05 / K02", "venta", origen, f"muestra: {len(venta)} pedido(s)"),
        kpi("K11", "Precio medio por par", dividir(importe_venta, pares_venta), "€/par",
            "K07 / K05 (media ponderada por pares)", "venta", origen),
        kpi("K12", "Pedidos Custom", porcentaje(demanda["es_custom"].sum(), len(demanda)), "%",
            "pedidos custom no cancelados / pedidos no cancelados x 100", "demanda", origen,
            f"{int(demanda['es_custom'].sum())} de {len(demanda)} pedidos"),
        mas_solicitado("K13", "Modelo más solicitado", tabla_abc, "nombre_modelo", "modelos_abc"),
        mas_solicitado("K14", "Talla más solicitada", tabla_tallas, "talla", "ventas_por_talla"),
    ]

    # Pareto: que parte de los pares se lleva el 20 % de los modelos con mas pares.
    # int(x + 0.5) redondea al entero mas cercano; como minimo se cuenta 1 modelo
    modelos = len(tabla_abc)
    if modelos > 0:
        cuantos = max(1, int(modelos * config.PARETO_PORCENTAJE / 100 + 0.5))
    else:
        cuantos = 0
    pares_de_los_primeros = tabla_abc["pares"].head(cuantos).sum()   # modelos_abc va de mas a menos pares
    pares_totales = tabla_abc["pares"].sum()
    lista.append(kpi(
        "K15", "Concentración de Pareto (modelos)",
        porcentaje(pares_de_los_primeros, pares_totales), "%",
        f"pares de los {config.PARETO_PORCENTAJE} % de modelos con más pares / pares totales x 100",
        "demanda", "modelos_abc", f"{cuantos} de {modelos} modelos del catálogo"))

    lista.append(kpi("K16", "Stock total", int(tabla_stock["stock_disponible"].sum()), "pares",
                     "suma de stock_disponible de todos los SKU", "stock", "stock_variantes",
                     "foto en la fecha de corte de stock.csv; no es un histórico"))
    lista.append(kpi("K17", "Referencias con stock bajo", int(tabla_stock["alerta_stock_bajo"].sum()), "SKU",
                     f"nº de SKU con stock_disponible < {config.UMBRAL_STOCK_BAJO}", "stock", "stock_variantes",
                     f"umbral {config.UMBRAL_STOCK_BAJO} pares, como el panel de Java y la consulta C8"))

    # Los que dependen de datos que no hay
    lista.append(kpi_no_calculable(
        "K18", "Margen", "€", "importe - coste", "venta", "precio_y_margen",
        "Acceso a Datos no exporta el coste unitario: no se calcula con el precio de venta"))
    lista.append(variacion_mensual(tabla_meses))
    lista.append(cobertura_total(tabla_stock))
    # dtype=object: cada valor conserva su tipo (12 pedidos, no 12.0)
    return pd.DataFrame(lista, columns=COLUMNAS, dtype=object)


def variacion_mensual(tabla_meses):
    """Variacion del importe de venta del ultimo mes frente al anterior. Hacen falta 2 meses."""
    formula = "(importe del último mes / importe del mes anterior - 1) x 100"
    if "estado" in tabla_meses.columns or len(tabla_meses) < 2:
        if "estado" in tabla_meses.columns:
            meses = 0   # la tabla es NO CALCULABLE: no hay ningun mes con ventas
        else:
            meses = len(tabla_meses)
        return kpi_no_calculable("K19", "Variación mensual del importe", "%", formula, "venta",
                                 "ventas_por_periodo", f"hacen falta 2 meses con ventas y hay {meses}")
    ultimo = tabla_meses.iloc[-1]
    if pd.isna(ultimo["variacion_importe_pct"]):
        valor = None
    else:
        valor = float(ultimo["variacion_importe_pct"])
    return kpi("K19", "Variación mensual del importe", valor, "%", formula, "venta",
               "ventas_por_periodo", f"{ultimo['anio_mes']} frente al mes anterior")


def cobertura_total(tabla_stock):
    """Semanas que duraria todo el stock con la demanda de los ultimos 28 dias."""
    formula = f"stock total / (pares de demanda de los últimos {config.DIAS_DEMANDA} días / 4)"
    if len(tabla_stock) == 0 or str(tabla_stock["estado_cobertura"].iloc[0]).startswith(NO_CALCULABLE):
        if len(tabla_stock) > 0:
            motivo = tabla_stock["estado_cobertura"].iloc[0]
        else:
            motivo = "no hay stock"
        return kpi_no_calculable("K20", "Cobertura de stock", "semanas", formula, "demanda",
                                 "stock_variantes", motivo)
    semanal = tabla_stock["demanda_28d"].sum() / (config.DIAS_DEMANDA / 7)
    if semanal == 0:
        return kpi("K20", "Cobertura de stock", None, "semanas", formula, "demanda", "stock_variantes",
                   f"N/D: sin demanda en los últimos {config.DIAS_DEMANDA} días")
    return kpi("K20", "Cobertura de stock", dividir(tabla_stock["stock_disponible"].sum(), semanal, 1),
               "semanas", formula, "demanda", "stock_variantes", "orientativa: el stock es una foto")


def coherencia_con_sql(tabla_kpis, carpeta_sql):
    """
    Contrasta los KPIs que tambien calcula Acceso a Datos con sus consultas
    P-A y P-B (las mismas de la conciliacion). None si faltan los resultados.
    """
    if conciliacion.faltan_resultados(carpeta_sql):
        return None
    p_a = conciliacion.leer_resultado(carpeta_sql, "P-A").iloc[0]
    p_b = conciliacion.leer_resultado(carpeta_sql, "P-B")
    valor = dict(zip(tabla_kpis["codigo"], tabla_kpis["valor"]))
    confirmados = p_b[p_b["estado"].isin(config.ESTADOS_CONFIRMADOS)]
    cancelados = p_b[p_b["estado"].isin(config.ESTADOS_CANCELADOS)]
    # Cada fila: consulta, KPI, que pedidos cuenta, cifra de SQL y cifra de Python
    filas = [
        conciliacion.comparar("P-B", "K01 pedidos registrados", "todos los estados",
                              p_b["pedidos"].sum(), valor["K01"]),
        conciliacion.comparar("P-B", "K02 pedidos confirmados", "confirmados en adelante",
                              confirmados["pedidos"].sum(), valor["K02"]),
        conciliacion.comparar("P-B", "K03 pedidos cancelados", "cancelado",
                              cancelados["pedidos"].sum(), valor["K03"]),
        conciliacion.comparar("P-A", "K04 pares solicitados", "no cancelados",
                              p_a["pares_solicitados"], valor["K04"]),
        conciliacion.comparar("P-B", "K05 pares confirmados", "confirmados en adelante",
                              confirmados["pares"].sum(), valor["K05"]),
        conciliacion.comparar("P-B", "K06 importe registrado", "todos los estados",
                              p_b["importe"].sum(), valor["K06"], euros=True),
        conciliacion.comparar("P-B", "K07 importe confirmado", "confirmados en adelante",
                              confirmados["importe"].sum(), valor["K07"], euros=True),
    ]
    return pd.DataFrame(filas)
