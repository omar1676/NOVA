from pathlib import Path

import pandas as pd

import config
from analiticas import de_demanda, de_venta, es_no_calculable

CONSULTAS = {
    "P-A": {
        "archivo": "P-A.csv",
        "sql": "count(*), sum(cantidad_total) y sum(importe_total) de pedidos con estado <> 'cancelado' "
               "(totales de la cabecera, todos los pedidos de la base)",
        "python": "filas de df_pedidos_unicos con es_cancelado = False; pares e importe sumados desde "
                  "sus líneas; solo pedidos válidos",
    },
    "P-B": {
        "archivo": "P-B.csv",
        "sql": "por estado: count(*), sum(cantidad_total) y sum(importe_total) de todos los pedidos, "
               "cancelados incluidos",
        "python": "df_pedidos_unicos agrupado por estado_pedido: pedidos, y pares e importe desde las líneas",
    },
    "P-C": {
        "archivo": "P-C.csv",
        "sql": "por COALESCE(modelo, 'X-NOVA'): sum(cantidad) y count(DISTINCT id_pedido) de las líneas "
               "de pedidos no cancelados",
        "python": "df_lineas_enriquecidas sin cancelados, agrupado por nombre_modelo: suma de cantidad "
                  "y pedidos distintos (nunique)",
    },
}

# Caso N: van aparte para que la conciliacion P-A a P-C no dependa de ellas
CONSULTAS_CASO_N = {
    "N-1": {
        "archivo": "N-1.csv",
        "sql": "count(*), sum(cantidad_total) y sum(importe_total) de los pedidos confirmados en adelante "
               "cuyo fecha_pedido es del mes pedido (to_char(fecha_pedido, 'YYYY-MM'))",
        "python": "la fila de ese mes en ventas_por_periodo (venta = confirmados en adelante); si el mes no "
                  "tiene ventas, 0",
    },
    "N-2": {
        "archivo": "N-2.csv",
        "sql": "por COALESCE(modelo, 'X-NOVA') y COALESCE(talla del SKU, talla de la configuración X-NOVA): "
               "sum(cantidad) de las líneas de pedidos no cancelados",
        "python": "cada celda distinta de 0 de matriz_modelo_talla (pares de demanda por modelo y talla)",
    },
    "N-3": {
        "archivo": "N-3.csv",
        "sql": "count(DISTINCT id_cliente) de pedidos: todos, no cancelados y confirmados en adelante",
        "python": "id_cliente distintos (nunique) de df_pedidos_unicos con los mismos tres criterios",
    },
}

# Columnas de texto de los resultados SQL; el resto son cifras
COLUMNAS_TEXTO = ["estado", "modelo", "anio_mes"]


def definicion(consulta):
    if consulta in CONSULTAS:
        return CONSULTAS[consulta]
    return CONSULTAS_CASO_N[consulta]


def faltan_resultados(carpeta_sql, consultas=CONSULTAS):
    carpeta_sql = Path(carpeta_sql)
    faltan = []
    for consulta in consultas.values():
        if not (carpeta_sql / consulta["archivo"]).exists():
            faltan.append(consulta["archivo"])
    return faltan


def leer_resultado(carpeta_sql, consulta):
    tabla = pd.read_csv(Path(carpeta_sql) / definicion(consulta)["archivo"], encoding="utf-8", dtype=str)
    for columna in tabla.columns:
        if columna not in COLUMNAS_TEXTO:
            tabla[columna] = pd.to_numeric(tabla[columna])
    return tabla


def comparar(consulta, indicador, clave, valor_sql, valor_python, euros=False):
    if pd.isna(valor_sql):
        resultado = "falta en SQL"
        diferencia = None
    elif pd.isna(valor_python):
        resultado = "falta en Python"
        diferencia = None
    else:
        diferencia = round(float(valor_python) - float(valor_sql), 2)
        if euros:
            tolerancia = config.TOLERANCIA_EUROS
        else:
            tolerancia = 0   # pedidos y pares tienen que coincidir exactamente
        if abs(diferencia) <= tolerancia:
            resultado = "coincide"
        else:
            resultado = "NO COINCIDE"
    return {"consulta": consulta, "indicador": indicador, "clave": clave,
            "valor_sql": valor_sql, "valor_python": valor_python,
            "diferencia": diferencia, "resultado": resultado,
            "definicion_sql": definicion(consulta)["sql"],
            "definicion_python": definicion(consulta)["python"]}


def comparar_por_grupos(consulta, sql, python, clave, indicadores):
    cruce = sql.merge(python, on=clave, how="outer", suffixes=("_sql", "_python"), validate="one_to_one")
    filas = []
    for _, fila in cruce.sort_values(clave).iterrows():
        for indicador, euros in indicadores:
            filas.append(comparar(consulta, indicador, fila[clave],
                                  fila[indicador + "_sql"], fila[indicador + "_python"], euros))
    return filas


def conciliar(carpeta_sql, pedidos_unicos, lineas_enriquecidas):
    if faltan_resultados(carpeta_sql):
        return None
    filas = []

    # P-A: pedidos no cancelados
    sql = leer_resultado(carpeta_sql, "P-A").iloc[0]
    no_cancelados = de_demanda(pedidos_unicos)
    filas.append(comparar("P-A", "pedidos", "no cancelados", sql["pedidos"], len(no_cancelados)))
    filas.append(comparar("P-A", "pares", "no cancelados", sql["pares_solicitados"], no_cancelados["pares"].sum()))
    filas.append(comparar("P-A", "importe", "no cancelados", sql["importe_ventas"],
                          round(no_cancelados["importe"].sum(), 2), euros=True))

    # P-B: por estado, todos los pedidos
    por_estado = pedidos_unicos.groupby("estado_pedido").agg(
        pedidos=("id_pedido", "count"), pares=("pares", "sum"), importe=("importe", "sum"))
    python = por_estado.reset_index().rename(columns={"estado_pedido": "estado"})   # el nombre de SQL
    filas += comparar_por_grupos("P-B", leer_resultado(carpeta_sql, "P-B"), python, "estado",
                                 [("pedidos", False), ("pares", False), ("importe", True)])

    # P-C: por modelo, lineas de pedidos no cancelados
    lineas = de_demanda(lineas_enriquecidas)
    por_modelo = lineas.groupby("nombre_modelo").agg(pares=("cantidad", "sum"), pedidos=("id_pedido", "nunique"))
    python = por_modelo.reset_index().rename(columns={"nombre_modelo": "modelo"})   # el nombre de SQL
    filas += comparar_por_grupos("P-C", leer_resultado(carpeta_sql, "P-C"), python, "modelo",
                                 [("pares", False), ("pedidos", False)])
    return pd.DataFrame(filas)


def contrastar_caso_n(carpeta_sql, tablas):
    if faltan_resultados(carpeta_sql, CONSULTAS_CASO_N):
        return None
    filas = []

    # N-1: el mes lo elige Acceso a Datos al lanzar la consulta (viene en el CSV)
    sql = leer_resultado(carpeta_sql, "N-1").iloc[0]
    mes = sql["anio_mes"]
    meses = tablas["ventas_por_periodo"]
    del_mes = pd.DataFrame()
    if not es_no_calculable(meses):
        del_mes = meses[meses["anio_mes"] == mes]
    for indicador, euros in [("pedidos", False), ("pares", False), ("importe", True)]:
        if len(del_mes) == 0:
            valor = 0   # un mes sin ventas: 0 pedidos, 0 pares y 0 euros
        else:
            valor = del_mes[indicador].iloc[0]
        filas.append(comparar("N-1", indicador, mes, sql[indicador], valor, euros))

    # N-2: cada celda de la matriz con pares, como "modelo · talla"
    matriz = tablas["matriz_modelo_talla"]
    if len(matriz) == 0:
        python = pd.DataFrame(columns=["celda", "pares"])
    else:
        celdas = matriz.reset_index().melt(id_vars="nombre_modelo", var_name="talla", value_name="pares")
        celdas = celdas[celdas["pares"] > 0]
        python = pd.DataFrame({"celda": celdas["nombre_modelo"] + " · " + celdas["talla"].astype(str),
                               "pares": celdas["pares"]})
    resultado_sql = leer_resultado(carpeta_sql, "N-2")
    sql = pd.DataFrame({"celda": resultado_sql["modelo"] + " · " + resultado_sql["talla"].astype(str),
                        "pares": resultado_sql["pares"]})
    filas += comparar_por_grupos("N-2", sql, python, "celda", [("pares", False)])

    # N-3: clientes distintos con cada criterio
    sql = leer_resultado(carpeta_sql, "N-3").iloc[0]
    pedidos = tablas["pedidos_unicos"]
    python = {
        "clientes_con_pedidos": pedidos["id_cliente"].nunique(),
        "clientes_con_demanda": de_demanda(pedidos)["id_cliente"].nunique(),
        "clientes_con_venta": de_venta(pedidos)["id_cliente"].nunique(),
    }
    for indicador, valor in python.items():
        filas.append(comparar("N-3", indicador, "clientes únicos", sql[indicador], valor))
    return pd.DataFrame(filas)
