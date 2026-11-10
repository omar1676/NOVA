"""
Los dos DataFrames principales y las variables derivadas (fase 2).

Solo usan filas VALIDAS: calidad.evaluar ya ha apartado las rechazadas.

Cada cruce (merge) declara su cardinalidad con validate= y comprueba con
indicator=True que todas las filas encuentran pareja. Si un cruce
multiplicara filas o perdiera claves, se para con un error: nunca se dan
cifras con un JOIN silencioso.

No usa Streamlit: el dashboard solo llamara a estas funciones (calcular_tablas).
"""
import numpy as np
import pandas as pd

import config
from pipeline import ErrorDatos

DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def cruzar(izquierda, derecha, clave, validate, nombre, exigir_pareja=True):
    """
    merge por la izquierda con validate= e indicator=True.

    Para con ErrorDatos si:
    - la cardinalidad no es la declarada (p. ej. un id repetido en la derecha
      en un "many_to_one", que multiplicaria filas),
    - el numero de filas cambia,
    - alguna fila con clave no encuentra pareja (si exigir_pareja).
    Una clave vacia no puede tener pareja (las lineas X-NOVA no tienen sku).
    """
    try:
        cruce = izquierda.merge(derecha, how="left", on=clave, validate=validate, indicator=True)
    except pd.errors.MergeError as error:
        raise ErrorDatos(f"El cruce {nombre} no es {validate}: {error}")
    if len(cruce) != len(izquierda):
        raise ErrorDatos(f"El cruce {nombre} ha pasado de {len(izquierda)} a {len(cruce)} filas")
    sin_pareja = (cruce["_merge"] == "left_only") & cruce[clave].notna()
    if exigir_pareja and sin_pareja.any():
        perdidas = ", ".join(cruce.loc[sin_pareja, clave].astype(str).unique())
        raise ErrorDatos(f"El cruce {nombre} tiene claves sin pareja: {perdidas}")
    return cruce.drop(columns="_merge")


def anadir_calendario(tabla):
    """Variables de calendario a partir de fecha_pedido (la misma funcion para lineas y pedidos)."""
    tabla = tabla.copy()
    fecha = tabla["fecha_pedido"]
    tabla["anio"] = fecha.dt.year
    tabla["mes"] = fecha.dt.month
    tabla["anio_mes"] = fecha.dt.strftime("%Y-%m")
    tabla["trimestre"] = fecha.dt.quarter
    tabla["dia_semana"] = fecha.dt.day_of_week.map(dict(enumerate(DIAS_SEMANA)))   # 0 = lunes
    return tabla


def df_lineas_enriquecidas(validos, stock):
    """
    Una fila por linea de pedido valida, con los datos de su pedido, su
    cliente, su modelo y el color de su SKU.

    stock es stock.csv completo: de el solo se toma el color de cada SKU.
    """
    lineas = validos["lineas_pedido"][["id_linea", "id_pedido", "sku", "id_modelo", "talla",
                                       "cantidad", "precio_unitario", "importe_linea"]]
    pedidos = validos["pedidos"][["id_pedido", "referencia", "id_cliente", "fecha_pedido",
                                  "tipo_pedido", "estado_pedido", "estado_pago"]]
    clientes = validos["clientes"][["id_cliente", "nombre", "tipo"]].rename(
        columns={"nombre": "nombre_cliente", "tipo": "tipo_cliente"})
    modelos = validos["modelos"][["id_modelo", "nombre_modelo"]]
    # Sin filas de SKU vacio: si no, una linea X-NOVA (sin SKU) se emparejaria con ellas
    colores = stock[["sku", "color"]].dropna(subset=["sku"])

    tabla = cruzar(lineas, pedidos, "id_pedido", "many_to_one", "líneas-pedidos")
    tabla = cruzar(tabla, clientes, "id_cliente", "many_to_one", "líneas-clientes")
    tabla = cruzar(tabla, modelos, "id_modelo", "many_to_one", "líneas-modelos")
    tabla = cruzar(tabla, colores, "sku", "many_to_one", "líneas-stock")

    tabla = anadir_calendario(tabla)
    tabla["es_custom"] = tabla["tipo_pedido"] == "custom"
    tabla["es_cancelado"] = tabla["estado_pedido"].isin(config.ESTADOS_CANCELADOS)
    # Que parte del importe de su pedido supone esta linea (entre 0 y 1)
    total_del_pedido = tabla.groupby("id_pedido")["importe_linea"].transform("sum")
    tabla["participacion_linea"] = (tabla["importe_linea"] / total_del_pedido).where(total_del_pedido > 0).round(4)

    columnas = ["id_linea", "id_pedido", "referencia", "fecha_pedido", "anio", "mes", "anio_mes",
                "trimestre", "dia_semana", "id_cliente", "nombre_cliente", "tipo_cliente",
                "tipo_pedido", "es_custom", "estado_pedido", "es_cancelado", "estado_pago",
                "id_modelo", "nombre_modelo", "sku", "color", "talla",
                "cantidad", "precio_unitario", "importe_linea", "participacion_linea"]
    return tabla[columnas]


def df_pedidos_unicos(validos, lineas_enriquecidas, fecha_corte):
    """
    Una fila por pedido valido, con su cliente y las metricas de sus lineas.

    pares e importe se suman desde las lineas, como pide la rubrica. La
    cabecera de Acceso a Datos trae cantidad_total e importe_total; la regla
    12 ya ha comprobado que coinciden con las lineas.

    fecha_corte es el momento de la exportacion: con ella se calcula la
    antiguedad de cada pedido sin depender del dia en que se ejecute Python.
    """
    # Metricas de las lineas: una fila por pedido
    por_pedido = lineas_enriquecidas.groupby("id_pedido").agg(
        num_lineas=("id_linea", "count"),
        pares=("cantidad", "sum"),
        importe=("importe_linea", "sum"),
        num_modelos=("id_modelo", "nunique"),
        num_tallas=("talla", "nunique"),
        primer_modelo=("nombre_modelo", "first"),
    ).reset_index()

    pedidos = validos["pedidos"][["id_pedido", "referencia", "id_cliente", "fecha_pedido", "tipo_pedido",
                                  "estado_pedido", "estado_pago", "personalizacion",
                                  "cantidad_total", "importe_total"]]
    clientes = validos["clientes"][["id_cliente", "nombre", "tipo"]].rename(
        columns={"nombre": "nombre_cliente", "tipo": "tipo_cliente"})

    tabla = cruzar(pedidos, clientes, "id_cliente", "many_to_one", "pedidos-clientes")
    # Un pedido sin lineas (advertencia de la regla 12) se queda: no exige pareja
    tabla = cruzar(tabla, por_pedido, "id_pedido", "one_to_one", "pedidos-métricas de líneas",
                   exigir_pareja=False)

    # Un pedido sin lineas tiene 0 lineas, 0 pares y 0 euros: es un recuento, no un dato inventado
    tabla["num_lineas"] = tabla["num_lineas"].fillna(0).astype(int)
    tabla["num_modelos"] = tabla["num_modelos"].fillna(0).astype(int)
    tabla["num_tallas"] = tabla["num_tallas"].fillna(0).astype(int)
    tabla["pares"] = tabla["pares"].fillna(0).astype(int)
    tabla["importe"] = tabla["importe"].fillna(0.0).round(2)

    # Precio medio por par: sin pares no hay precio medio (nulo, no 0)
    tabla["precio_medio_par"] = (tabla["importe"] / tabla["pares"]).where(tabla["pares"] > 0).round(2)
    # El modelo del pedido solo si todas sus lineas son del mismo modelo
    tabla["pedido_multimodelo"] = tabla["num_modelos"] > 1
    tabla["modelo_pedido"] = tabla["primer_modelo"].where(tabla["num_modelos"] == 1)
    tabla["es_custom"] = tabla["tipo_pedido"] == "custom"
    tabla["es_cancelado"] = tabla["estado_pedido"].isin(config.ESTADOS_CANCELADOS)
    tabla["es_confirmado"] = tabla["estado_pedido"].isin(config.ESTADOS_CONFIRMADOS)
    tabla = anadir_calendario(tabla)
    tabla["antiguedad_dias"] = (fecha_corte - tabla["fecha_pedido"]).dt.days

    columnas = ["id_pedido", "referencia", "fecha_pedido", "anio", "mes", "anio_mes", "trimestre",
                "dia_semana", "antiguedad_dias", "id_cliente", "nombre_cliente", "tipo_cliente",
                "tipo_pedido", "es_custom", "personalizacion", "estado_pedido", "es_cancelado",
                "es_confirmado", "estado_pago", "num_lineas", "num_modelos", "num_tallas",
                "pedido_multimodelo", "modelo_pedido", "pares", "importe", "precio_medio_par",
                "cantidad_total", "importe_total"]
    return tabla[columnas]


def importes_por_criterio(pedidos_unicos):
    """
    Pedidos, pares e importe con tres criterios distintos (caso B).

    Ninguno se llama "ingresos cobrados": si un pedido esta pagado lo dice
    estado_pago, y aqui no se usa. El IVA esta pendiente de confirmar.
    """
    criterios = [
        ("registrados", "todos los pedidos válidos, en cualquier estado",
         pd.Series(True, index=pedidos_unicos.index)),
        ("no_cancelados", "estado distinto de cancelado (criterio del panel P-A de Acceso a Datos)",
         ~pedidos_unicos["es_cancelado"]),
        ("confirmados_en_adelante", "estado " + ", ".join(config.ESTADOS_CONFIRMADOS) + " (apartado 6.5 de la rúbrica)",
         pedidos_unicos["es_confirmado"]),
    ]
    filas = []
    for nombre, definicion, mascara in criterios:
        parte = pedidos_unicos[mascara]
        filas.append({
            "criterio": nombre,
            "definicion": definicion,
            "pedidos": len(parte),
            "pares": int(parte["pares"].sum()),
            "importe_eur": round(float(parte["importe"].sum()), 2),
            "iva": config.IVA,
        })
    return pd.DataFrame(filas)


def comparar_pedidos(pedidos_unicos, lineas_enriquecidas, referencia_a, referencia_b):
    """
    Pone dos pedidos lado a lado para ver en que coinciden (caso A).
    No decide nada: solo ensena los datos.
    """
    pedido_a = pedidos_unicos[pedidos_unicos["referencia"] == referencia_a].iloc[0]
    pedido_b = pedidos_unicos[pedidos_unicos["referencia"] == referencia_b].iloc[0]

    def lineas_de(pedido):
        suyas = lineas_enriquecidas[lineas_enriquecidas["id_pedido"] == pedido["id_pedido"]].sort_values("sku")
        return {
            "id_linea": ", ".join(suyas["id_linea"]),
            "articulos": ", ".join(suyas["sku"].fillna("sin sku") + " x" + suyas["cantidad"].astype(str)),
            "precio_unitario": ", ".join(f"{precio:.2f}" for precio in suyas["precio_unitario"].unique()),
        }

    filas = []
    for campo in ["id_pedido", "referencia", "id_cliente", "nombre_cliente", "fecha_pedido", "tipo_pedido",
                  "estado_pedido", "estado_pago", "personalizacion", "pares", "importe"]:
        filas.append({"campo": campo, referencia_a: str(pedido_a[campo]), referencia_b: str(pedido_b[campo])})
    lineas_a = lineas_de(pedido_a)
    lineas_b = lineas_de(pedido_b)
    for campo in lineas_a:
        filas.append({"campo": campo, referencia_a: lineas_a[campo], referencia_b: lineas_b[campo]})
    tabla = pd.DataFrame(filas)
    tabla["igual"] = tabla[referencia_a] == tabla[referencia_b]
    return tabla


# ---------------------------------------------------------------------
# Fase 3: DataFrames analiticos (apartado 6.15)
#
# Cada tabla dice que pedidos usa (config.py):
#   demanda = no cancelados, venta = confirmados en adelante.
# Si una tabla no se puede calcular con los datos que hay, existe igual con
# estado NO CALCULABLE y el motivo: nunca con ceros inventados.
# ---------------------------------------------------------------------

NO_CALCULABLE = "NO CALCULABLE"


def no_calculable(motivo):
    """Tabla que no se puede calcular: una fila que dice por que."""
    return pd.DataFrame({"estado": [NO_CALCULABLE], "motivo": [motivo]})


def porcentaje(parte, total):
    """parte / total en %, con un decimal. Sin total no hay porcentaje: nulo, no 0."""
    if not total:
        return None
    return round(100 * float(parte) / float(total), 1)


def dividir(numerador, denominador, decimales=2):
    """Division que devuelve nulo (no 0 ni un error) si el denominador es 0."""
    if not denominador:
        return None
    return round(float(numerador) / float(denominador), decimales)


def de_demanda(tabla):
    """Pedidos o lineas que no estan cancelados."""
    return tabla[~tabla["es_cancelado"]]


def de_venta(pedidos_unicos):
    """Pedidos confirmados en adelante."""
    return pedidos_unicos[pedidos_unicos["es_confirmado"]]


def pedidos_por_estado(pedidos_unicos):
    """
    Pedidos, pares e importe de cada estado del catalogo. Un estado sin pedidos
    sale con 0 (es un recuento, no un dato inventado). Los cancelados se ven
    aqui aunque no cuenten como venta.
    """
    tabla = pedidos_unicos.groupby("estado_pedido").agg(
        pedidos=("id_pedido", "count"), pares=("pares", "sum"), importe=("importe", "sum"))
    tabla = tabla.reindex(config.ESTADOS_PEDIDO, fill_value=0)
    tabla.index.name = "estado_pedido"
    tabla = tabla.reset_index()
    total = tabla["pedidos"].sum()
    tabla["porcentaje_pedidos"] = [porcentaje(n, total) for n in tabla["pedidos"]]
    tabla["importe"] = tabla["importe"].round(2)
    tabla["cuenta_como_venta"] = tabla["estado_pedido"].isin(config.ESTADOS_CONFIRMADOS)
    return tabla


def pedidos_por_estado_pago(pedidos_unicos):
    """
    Pedidos e importe de cada estado de pago del catalogo (con 0 si no hay
    ninguno). Es lo que Acceso a Datos marca: no es un cobro comprobado.
    """
    tabla = pedidos_unicos.groupby("estado_pago").agg(pedidos=("id_pedido", "count"), importe=("importe", "sum"))
    tabla = tabla.reindex(config.ESTADOS_PAGO, fill_value=0)
    tabla.index.name = "estado_pago"
    tabla = tabla.reset_index()
    tabla["importe"] = tabla["importe"].round(2)
    tabla["porcentaje_pedidos"] = [porcentaje(n, tabla["pedidos"].sum()) for n in tabla["pedidos"]]
    return tabla


def ventas_por_periodo(pedidos_unicos):
    """
    Venta por mes (DataFrame 02): pedidos, pares, importe y ticket medio, la
    variacion respecto al mes anterior, la media de los 3 meses PREVIOS (sin el
    propio mes) y la variacion interanual (solo si existe el mismo mes del ano
    anterior). Un mes sin ventas DENTRO del periodo sale con 0; antes del
    primero y despues del ultimo no se inventa ninguno.
    """
    venta = de_venta(pedidos_unicos)
    if len(venta) == 0:
        return no_calculable("no hay pedidos de venta (confirmados en adelante)")
    mes = venta["fecha_pedido"].dt.to_period("M")
    tabla = venta.groupby(mes).agg(pedidos=("id_pedido", "count"), pares=("pares", "sum"),
                                   importe=("importe", "sum"))
    tabla = tabla.reindex(pd.period_range(tabla.index.min(), tabla.index.max(), freq="M"), fill_value=0)
    tabla["importe"] = tabla["importe"].round(2)
    tabla["ticket_medio"] = (tabla["importe"] / tabla["pedidos"]).where(tabla["pedidos"] > 0).round(2)
    # Si el mes anterior tuvo 0 euros, la variacion no existe (seria infinita)
    variacion = 100 * tabla["importe"].pct_change()
    tabla["variacion_importe_pct"] = variacion.replace([np.inf, -np.inf], np.nan).round(1)
    tabla["media_3_meses_previos"] = tabla["importe"].shift(1).rolling(3).mean().round(2)
    interanual = 100 * tabla["importe"].pct_change(12)
    tabla["variacion_interanual_pct"] = interanual.replace([np.inf, -np.inf], np.nan).round(1)
    tabla.index = tabla.index.astype(str)
    tabla.index.name = "anio_mes"
    return tabla.reset_index()


def matriz_modelo_mes(lineas_enriquecidas):
    """Pares de demanda por modelo (filas) y mes (columnas) (apartado 6.9)."""
    demanda = de_demanda(lineas_enriquecidas)
    if len(demanda) == 0:
        return no_calculable("no hay líneas de demanda")
    matriz = demanda.pivot_table(index="nombre_modelo", columns="anio_mes", values="cantidad",
                                 aggfunc="sum", fill_value=0)
    return matriz.reset_index()


def clasificar_abc(tabla, columna):
    """
    Anade a una tabla ORDENADA de mayor a menor por `columna` su peso, el
    acumulado y la clase ABC. La clase depende de lo que se acumula ANTES de
    cada fila: A si es menor que ABC_LIMITE_A (80 %), B si es menor que
    ABC_LIMITE_B (95 %), C el resto. Asi el modelo que cruza el 80 % es A.
    Las filas empatadas reciben la misma clase: la de la primera del empate.
    """
    tabla = tabla.copy()
    total = tabla[columna].sum()
    acumulado = tabla[columna].cumsum()
    tabla["peso_pct"] = [porcentaje(valor, total) for valor in tabla[columna]]
    tabla["acumulado_pct"] = [porcentaje(valor, total) for valor in acumulado]
    if not total:
        tabla["clase_abc"] = "C"
        return tabla
    anterior = 100 * (acumulado - tabla[columna]) / total
    anterior = anterior.groupby(tabla[columna]).transform("min")   # empates: misma clase
    tabla["clase_abc"] = np.where(anterior < config.ABC_LIMITE_A, "A",
                                  np.where(anterior < config.ABC_LIMITE_B, "B", "C"))
    return tabla


def modelos_abc(lineas_enriquecidas, modelos):
    """
    Ventas por modelo y clasificacion ABC (DataFrame 03).

    Variable de clasificacion: PARES DE DEMANDA (pedidos no cancelados), porque
    sirve para decidir que fabricar. Tambien sale el importe y su ranking. Salen
    todos los modelos del catalogo: uno sin demanda tiene 0 pares y clase C.
    No es el ABC del valor del stock: eso necesitaria el coste del inventario.
    """
    demanda = de_demanda(lineas_enriquecidas)
    por_modelo = demanda.groupby("id_modelo").agg(
        pares=("cantidad", "sum"), pedidos=("id_pedido", "nunique"), importe=("importe_linea", "sum")
    ).reset_index()
    tabla = cruzar(modelos[["id_modelo", "nombre_modelo"]], por_modelo, "id_modelo", "one_to_one",
                   "modelos-demanda", exigir_pareja=False)
    # Un modelo sin demanda tiene 0 pares, 0 pedidos y 0 euros: es un recuento
    tabla["pares"] = tabla["pares"].fillna(0).astype(int)
    tabla["pedidos"] = tabla["pedidos"].fillna(0).astype(int)
    tabla["importe"] = tabla["importe"].fillna(0.0).round(2)
    tabla = tabla.sort_values(["pares", "nombre_modelo"], ascending=[False, True]).reset_index(drop=True)
    tabla["ranking_pares"] = tabla["pares"].rank(method="min", ascending=False).astype(int)
    tabla["ranking_importe"] = tabla["importe"].rank(method="min", ascending=False).astype(int)
    tabla["peso_importe_pct"] = [porcentaje(valor, tabla["importe"].sum()) for valor in tabla["importe"]]
    return clasificar_abc(tabla, "pares")


def ventas_por_talla(lineas_enriquecidas):
    """Pares de demanda por talla, con su peso sobre el total."""
    demanda = de_demanda(lineas_enriquecidas)
    tabla = demanda.groupby("talla").agg(
        pares=("cantidad", "sum"), pedidos=("id_pedido", "nunique"), lineas=("id_linea", "count")
    ).reset_index()
    tabla["peso_pct"] = [porcentaje(valor, tabla["pares"].sum()) for valor in tabla["pares"]]
    return tabla.sort_values("talla").reset_index(drop=True)


def matriz_modelo_talla(lineas_enriquecidas):
    """
    Pares de demanda por modelo (filas) y talla (columnas) (DataFrame 04).
    Una combinacion sin pedidos tiene 0 pares.
    """
    demanda = de_demanda(lineas_enriquecidas)
    if len(demanda) == 0:
        return pd.DataFrame()
    return demanda.pivot_table(index="nombre_modelo", columns="talla", values="cantidad",
                               aggfunc="sum", fill_value=0)


def proporcion_tallas(matriz):
    """Que parte de los pares de cada modelo es de cada talla: cada fila suma 1."""
    if len(matriz) == 0:
        return matriz
    return matriz.div(matriz.sum(axis=1), axis=0).round(4)


def custom_vs_estandar(pedidos_unicos):
    """
    Pedido Custom frente a estandar (DataFrame 05). La tasa de cancelacion es de
    PEDIDOS registrados; las cuotas son de la demanda (pedidos, pares y euros);
    el importe y el ticket de venta, de los confirmados en adelante.
    """
    demanda_total = de_demanda(pedidos_unicos)
    filas = []
    for tipo in config.TIPOS_PEDIDO:
        del_tipo = pedidos_unicos[pedidos_unicos["tipo_pedido"] == tipo]
        demanda = de_demanda(del_tipo)
        venta = de_venta(del_tipo)
        filas.append({
            "tipo_pedido": tipo,
            "pedidos_registrados": len(del_tipo),
            "pedidos_cancelados": int(del_tipo["es_cancelado"].sum()),
            "tasa_cancelacion_pct": porcentaje(del_tipo["es_cancelado"].sum(), len(del_tipo)),
            "pedidos_demanda": len(demanda),
            "pares_demanda": int(demanda["pares"].sum()),
            "importe_demanda": round(float(demanda["importe"].sum()), 2),
            "cuota_pedidos_pct": porcentaje(len(demanda), len(demanda_total)),
            "cuota_pares_pct": porcentaje(demanda["pares"].sum(), demanda_total["pares"].sum()),
            "cuota_importe_pct": porcentaje(demanda["importe"].sum(), demanda_total["importe"].sum()),
            "pedidos_venta": len(venta),
            "importe_venta": round(float(venta["importe"].sum()), 2),
            "ticket_medio_venta": dividir(venta["importe"].sum(), len(venta)),
        })
    return pd.DataFrame(filas)


def clientes_actividad(pedidos_unicos, clientes, fecha_corte):
    """
    Una fila por cliente, tambien los que no tienen pedidos (con 0): cuantos
    pedidos, pares e importe, y cuando fue su ultimo pedido. Es la base del RFM
    de la fase siguiente. Solo lleva id y tipo de cliente: el nombre no hace
    falta para analizar.
    """
    registrados = pedidos_unicos.groupby("id_cliente").agg(
        pedidos_registrados=("id_pedido", "count"), pedidos_cancelados=("es_cancelado", "sum"))
    demanda = de_demanda(pedidos_unicos).groupby("id_cliente").agg(
        pedidos_demanda=("id_pedido", "count"), pares_demanda=("pares", "sum"),
        importe_demanda=("importe", "sum"), primer_pedido=("fecha_pedido", "min"),
        ultimo_pedido=("fecha_pedido", "max"))
    venta = de_venta(pedidos_unicos).groupby("id_cliente").agg(
        pedidos_venta=("id_pedido", "count"), importe_venta=("importe", "sum"))

    tabla = clientes[["id_cliente", "tipo"]].rename(columns={"tipo": "tipo_cliente"})
    for parte, nombre in [(registrados, "registrados"), (demanda, "demanda"), (venta, "venta")]:
        tabla = cruzar(tabla, parte.reset_index(), "id_cliente", "one_to_one", f"clientes-{nombre}",
                       exigir_pareja=False)
    # Un cliente sin pedidos tiene 0 pedidos y 0 euros: es un recuento
    for columna in ["pedidos_registrados", "pedidos_cancelados", "pedidos_demanda", "pares_demanda", "pedidos_venta"]:
        tabla[columna] = tabla[columna].fillna(0).astype(int)
    for columna in ["importe_demanda", "importe_venta"]:
        tabla[columna] = tabla[columna].fillna(0.0).round(2)
    tabla["dias_desde_ultimo_pedido"] = (fecha_corte - tabla["ultimo_pedido"]).dt.days
    tabla["sin_pedidos"] = tabla["pedidos_registrados"] == 0
    return tabla.sort_values(["importe_demanda", "id_cliente"], ascending=[False, True]).reset_index(drop=True)


def cohortes(pedidos_unicos):
    """
    Cohortes de compra (DataFrame 07). Cada cliente entra en la cohorte del mes
    de su primera compra (pedido de venta). Para cada cohorte y cada mes
    despues, que parte de sus clientes vuelve a comprar (retencion).
    Con ventas de menos de 2 meses no hay retencion que medir: NO CALCULABLE.
    """
    venta = de_venta(pedidos_unicos).copy()
    venta["mes"] = venta["fecha_pedido"].dt.to_period("M")
    meses_distintos = venta["mes"].nunique()
    if meses_distintos < 2:
        return no_calculable(f"hacen falta ventas de al menos 2 meses distintos y hay {meses_distintos}")
    venta["cohorte"] = venta.groupby("id_cliente")["mes"].transform("min")
    venta["meses_despues"] = (venta["mes"] - venta["cohorte"]).apply(lambda diferencia: diferencia.n)
    clientes = venta.pivot_table(index="cohorte", columns="meses_despues", values="id_cliente",
                                 aggfunc="nunique", fill_value=0)
    tabla = clientes.div(clientes[0], axis=0).round(3)
    # Un mes que todavia no ha pasado no es retencion 0: no se sabe (vacio)
    ultimo_mes = venta["mes"].max()
    for cohorte in tabla.index:
        for numero in tabla.columns:
            if cohorte + numero > ultimo_mes:
                tabla.loc[cohorte, numero] = np.nan
    tabla.columns = [f"retencion_mes_{numero}" for numero in tabla.columns]
    tabla.insert(0, "clientes_cohorte", clientes[0])
    tabla["aviso"] = np.where(tabla["clientes_cohorte"] < 5, "muestra pequeña: menos de 5 clientes", "")
    tabla.index = tabla.index.astype(str)
    tabla.index.name = "cohorte"
    return tabla.reset_index()


def stock_variantes(stock, modelos, lineas_enriquecidas, pedidos_unicos, fecha_corte,
                    umbral=config.UMBRAL_STOCK_BAJO):
    """
    Stock por SKU (modelo + color + talla) con la demanda de los ultimos
    DIAS_DEMANDA dias, la alerta de stock bajo y la cobertura (DataFrame 08).
    El umbral de stock bajo es el de config.py salvo que se pase otro (el
    dashboard deja cambiarlo).

    El stock es UNA FOTO en la fecha de corte, no un historico. Nunca se suma
    entre colores. Cobertura en semanas = stock / (pares demandados en 28 dias / 4).
    Solo se calcula si el historial de pedidos cubre los 28 dias enteros; un
    SKU sin demanda en ese periodo tiene cobertura N/D.
    """
    tabla = stock[["sku", "id_modelo", "color", "talla", "stock_disponible"]]
    tabla = cruzar(tabla, modelos[["id_modelo", "nombre_modelo"]], "id_modelo", "many_to_one", "stock-modelos")

    desde = fecha_corte - pd.Timedelta(days=config.DIAS_DEMANDA)
    demanda = de_demanda(lineas_enriquecidas)
    recientes = demanda[demanda["fecha_pedido"] > desde]
    por_sku = recientes.groupby("sku").agg(demanda_28d=("cantidad", "sum")).reset_index()
    tabla = cruzar(tabla, por_sku, "sku", "one_to_one", "stock-demanda", exigir_pareja=False)
    tabla["demanda_28d"] = tabla["demanda_28d"].fillna(0).astype(int)   # sin pedidos: 0 pares
    tabla["alerta_stock_bajo"] = tabla["stock_disponible"] < umbral

    primera = pedidos_unicos["fecha_pedido"].min()
    historial = (fecha_corte - primera).days if pd.notna(primera) else 0
    if historial < config.DIAS_DEMANDA:
        tabla["semanas_cobertura"] = np.nan
        tabla["estado_cobertura"] = (f"{NO_CALCULABLE}: el historial de pedidos cubre {historial} "
                                     f"días de {config.DIAS_DEMANDA}")
    else:
        demanda_semanal = tabla["demanda_28d"] / (config.DIAS_DEMANDA / 7)
        cobertura = tabla["stock_disponible"] / demanda_semanal
        tabla["semanas_cobertura"] = cobertura.where(tabla["demanda_28d"] > 0).round(1)
        tabla["estado_cobertura"] = np.where(tabla["demanda_28d"] > 0, "calculada",
                                             f"N/D: sin demanda en {config.DIAS_DEMANDA} días")
    return tabla.sort_values(["nombre_modelo", "color", "talla"]).reset_index(drop=True)


def stock_bajo(tabla_stock):
    """Referencias por debajo del umbral, de menos a mas stock (el mismo orden que la consulta C8)."""
    bajo = tabla_stock[tabla_stock["alerta_stock_bajo"]]
    return bajo.sort_values(["stock_disponible", "nombre_modelo", "color", "talla"]).reset_index(drop=True)


def anomalias_iqr(lineas_enriquecidas):
    """
    Atipicos con la regla del IQR dentro de grupos comparables (DataFrame 10):
    - precio_unitario por modelo Y tipo de pedido: un Custom lleva un recargo,
      asi que solo se compara con otros Custom del mismo modelo.
    - cantidad por tipo de pedido: un pedido Custom de club pide muchos pares y es normal.
    Limites: Q1 - 1,5 x IQR y Q3 + 1,5 x IQR. Un grupo con menos de
    MINIMO_MUESTRA_IQR valores no se evalua. Las lineas atipicas NO se borran:
    solo se senalan para revisarlas.
    """
    filas = []
    for variable, columnas in [("precio_unitario", ["nombre_modelo", "tipo_pedido"]), ("cantidad", ["tipo_pedido"])]:
        for valores_grupo, parte in lineas_enriquecidas.groupby(columnas):
            descripcion = ", ".join(f"{columna} = {valor}" for columna, valor in zip(columnas, valores_grupo))
            valores = parte[variable].astype(float)
            fila = {"variable": variable, "grupo": descripcion, "n": len(valores)}
            if len(valores) < config.MINIMO_MUESTRA_IQR:
                fila["estado"] = f"muestra insuficiente (menos de {config.MINIMO_MUESTRA_IQR} valores)"
            else:
                q1 = valores.quantile(0.25)
                q3 = valores.quantile(0.75)
                limite_inferior = q1 - 1.5 * (q3 - q1)
                limite_superior = q3 + 1.5 * (q3 - q1)
                fuera = parte[(valores < limite_inferior) | (valores > limite_superior)]
                fila.update({"q1": q1, "q3": q3, "limite_inferior": limite_inferior,
                             "limite_superior": limite_superior, "atipicos": len(fuera),
                             "lineas_atipicas": ", ".join(fuera["id_linea"]), "estado": "evaluado"})
            filas.append(fila)
    columnas = ["variable", "grupo", "n", "q1", "q3", "limite_inferior", "limite_superior",
                "atipicos", "lineas_atipicas", "estado"]
    return pd.DataFrame(filas, columns=columnas)


def precio_y_margen(tabla_abc, modelos):
    """
    Precio medio ponderado por par de cada modelo (importe / pares de demanda)
    frente a su precio de catalogo (DataFrame 11). El margen necesita el coste
    unitario y Acceso a Datos no lo exporta: NO CALCULABLE. Nunca se calcula
    un "margen" con el precio de venta.
    """
    tabla = cruzar(tabla_abc[["id_modelo", "nombre_modelo", "pares", "importe"]],
                   modelos[["id_modelo", "precio_base"]], "id_modelo", "one_to_one", "abc-precios")
    tabla["precio_medio_ponderado"] = (tabla["importe"] / tabla["pares"]).where(tabla["pares"] > 0).round(2)
    tabla["coste_unitario"] = "no disponible"
    tabla["margen"] = f"{NO_CALCULABLE}: Acceso a Datos no exporta el coste unitario"
    return tabla


def calcular_tablas(datos, validos):
    """
    Todas las tablas de analisis a partir de la misma version de los datos
    (calidad.evaluar ya ha apartado las filas rechazadas). La consola y el
    dashboard de la fase siguiente usan esta funcion: una sola formula por tabla.
    """
    corte = datos["stock"]["fecha_corte"].max()
    lineas = df_lineas_enriquecidas(validos, datos["stock"])
    pedidos = df_pedidos_unicos(validos, lineas, corte)
    abc = modelos_abc(lineas, validos["modelos"])
    matriz = matriz_modelo_talla(lineas)
    stock = stock_variantes(validos["stock"], validos["modelos"], lineas, pedidos, corte)
    return {
        "lineas_enriquecidas": lineas,
        "pedidos_unicos": pedidos,
        "pedidos_por_estado": pedidos_por_estado(pedidos),
        "pedidos_por_estado_pago": pedidos_por_estado_pago(pedidos),
        "ventas_por_periodo": ventas_por_periodo(pedidos),
        "modelos_abc": abc,
        "ventas_por_talla": ventas_por_talla(lineas),
        "matriz_modelo_talla": matriz,
        "matriz_modelo_talla_proporcion": proporcion_tallas(matriz),
        "matriz_modelo_mes": matriz_modelo_mes(lineas),
        "custom_vs_estandar": custom_vs_estandar(pedidos),
        "clientes_actividad": clientes_actividad(pedidos, validos["clientes"], corte),
        "cohortes": cohortes(pedidos),
        "stock_variantes": stock,
        "stock_bajo": stock_bajo(stock),
        "anomalias": anomalias_iqr(lineas),
        "precio_y_margen": precio_y_margen(abc, validos["modelos"]),
    }
