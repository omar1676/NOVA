"""
Conciliacion con tres consultas SQL de Acceso a Datos (caso E de la rubrica).

Las tres consultas son las del panel de indicadores de
acceso-datos/sql/12_consultas_panel.sql, sin cambiar nada:
  P-A  pedidos, pares e importe de los pedidos no cancelados
  P-B  pedidos, pares e importe por estado
  P-C  pares y pedidos por modelo, sin cancelados

Acceso a Datos las ejecuta con psql y deja el resultado en CSV en
entrada_acc/conciliacion_sql/ (como lo hace aqui conciliacion_sql.md).
Python no se conecta a PostgreSQL: lee esos CSV y los compara con lo que
calcula el con pandas. Si faltan, la conciliacion queda PENDIENTE: nunca
se da por buena sin haberla hecho.
"""
from pathlib import Path

import pandas as pd

import config

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


def faltan_resultados(carpeta_sql):
    """Lista de los CSV de resultados SQL que no estan."""
    carpeta_sql = Path(carpeta_sql)
    return [c["archivo"] for c in CONSULTAS.values() if not (carpeta_sql / c["archivo"]).exists()]


def leer_resultado(carpeta_sql, consulta):
    """Lee el CSV que ha dejado psql para una consulta. Las cifras se convierten a numero."""
    tabla = pd.read_csv(Path(carpeta_sql) / CONSULTAS[consulta]["archivo"], encoding="utf-8", dtype=str)
    for columna in tabla.columns:
        if columna not in ("estado", "modelo"):
            tabla[columna] = pd.to_numeric(tabla[columna])
    return tabla


def comparar(consulta, indicador, clave, valor_sql, valor_python, euros=False):
    """Una fila de la conciliacion. Los euros se dan por iguales con medio centimo de diferencia."""
    if pd.isna(valor_sql):
        resultado, diferencia = "falta en SQL", None
    elif pd.isna(valor_python):
        resultado, diferencia = "falta en Python", None
    else:
        diferencia = round(float(valor_python) - float(valor_sql), 2)
        tolerancia = config.TOLERANCIA_EUROS if euros else 0
        resultado = "coincide" if abs(diferencia) <= tolerancia else "NO COINCIDE"
    return {"consulta": consulta, "indicador": indicador, "clave": clave,
            "valor_sql": valor_sql, "valor_python": valor_python,
            "diferencia": diferencia, "resultado": resultado,
            "definicion_sql": CONSULTAS[consulta]["sql"],
            "definicion_python": CONSULTAS[consulta]["python"]}


def comparar_por_grupos(consulta, sql, python, clave, indicadores):
    """
    Cruza el resultado SQL y el de Python por su clave (estado o modelo) con
    un merge "outer": asi sale tambien un grupo que solo esta en uno de los dos.
    """
    cruce = sql.merge(python, on=clave, how="outer", suffixes=("_sql", "_python"), validate="one_to_one")
    filas = []
    for _, fila in cruce.sort_values(clave).iterrows():
        for indicador, euros in indicadores:
            filas.append(comparar(consulta, indicador, fila[clave],
                                  fila[indicador + "_sql"], fila[indicador + "_python"], euros))
    return filas


def conciliar(carpeta_sql, pedidos_unicos, lineas_enriquecidas):
    """
    Compara las tres consultas con pandas. Devuelve un DataFrame con una fila
    por cifra comparada, o None si faltan los resultados SQL (pendiente).
    """
    if faltan_resultados(carpeta_sql):
        return None
    filas = []

    # P-A: pedidos no cancelados
    sql = leer_resultado(carpeta_sql, "P-A").iloc[0]
    no_cancelados = pedidos_unicos[~pedidos_unicos["es_cancelado"]]
    filas.append(comparar("P-A", "pedidos", "no cancelados", sql["pedidos"], len(no_cancelados)))
    filas.append(comparar("P-A", "pares", "no cancelados", sql["pares_solicitados"], no_cancelados["pares"].sum()))
    filas.append(comparar("P-A", "importe", "no cancelados", sql["importe_ventas"],
                          round(no_cancelados["importe"].sum(), 2), euros=True))

    # P-B: por estado, todos los pedidos
    python = pedidos_unicos.groupby("estado_pedido").agg(
        pedidos=("id_pedido", "count"), pares=("pares", "sum"), importe=("importe", "sum")
    ).reset_index().rename(columns={"estado_pedido": "estado"})
    filas += comparar_por_grupos("P-B", leer_resultado(carpeta_sql, "P-B"), python, "estado",
                                 [("pedidos", False), ("pares", False), ("importe", True)])

    # P-C: por modelo, lineas de pedidos no cancelados
    lineas = lineas_enriquecidas[~lineas_enriquecidas["es_cancelado"]]
    python = lineas.groupby("nombre_modelo").agg(
        pares=("cantidad", "sum"), pedidos=("id_pedido", "nunique")
    ).reset_index().rename(columns={"nombre_modelo": "modelo"})
    filas += comparar_por_grupos("P-C", leer_resultado(carpeta_sql, "P-C"), python, "modelo",
                                 [("pares", False), ("pedidos", False)])
    return pd.DataFrame(filas)
