"""
Filtros combinables del dashboard (apartados 6.12 y 6.16). main.py no filtra:
sus CSV son siempre de todos los datos validos.

Seis filtros: periodo, modelo, talla, tipo de pedido, estado del pedido y
cliente (su id_cliente). Un filtro vacio (None o lista vacia) no restringe nada.

Como se aplican:
- El periodo, el tipo, el estado y el cliente son datos del PEDIDO: se quedan
  los pedidos que los cumplen, con todas sus lineas. El periodo incluye el dia
  final entero.
- El modelo y la talla son datos de la LINEA: se quedan solo las lineas que
  los cumplen. Un pedido con lineas de varios modelos aporta solo las del
  modelo elegido (sus pares y su importe) y cuenta UNA vez si tiene al menos
  una. Un pedido sin ninguna linea que cumpla desaparece.
- Las condiciones se combinan con Y (todas a la vez).

Despues se recalculan TODAS las tablas y los KPIs con las mismas funciones de
analiticas.py y kpis.py: no hay una segunda formula para ninguna cifra.

No se aplican a RFM, KMeans ni la prediccion (son siempre del conjunto
completo, ver dashboard.md) ni al stock salvo modelo y talla (ver tablas_inventario).
"""
import pandas as pd

import analiticas
import config
import kpis

SIN_FILTROS = {"desde": None, "hasta": None, "modelos": [], "tallas": [], "tipos": [], "estados": [], "clientes": []}


def hay_filtros(filtros):
    """True si algun filtro restringe algo."""
    for clave in SIN_FILTROS:
        if filtros.get(clave):
            return True
    return False


def describir(filtros):
    """Los filtros en una linea de texto, para el pie de graficos, las descargas y el registro."""
    partes = []
    if filtros.get("desde") or filtros.get("hasta"):
        desde = filtros.get("desde") or "inicio"
        hasta = filtros.get("hasta") or "fin"
        partes.append(f"periodo {desde} a {hasta}")
    nombres = {"modelos": "modelo", "tallas": "talla", "tipos": "tipo", "estados": "estado", "clientes": "cliente"}
    for clave, nombre in nombres.items():
        if filtros.get(clave):
            valores = [str(valor) for valor in filtros[clave]]
            partes.append(f"{nombre}: {', '.join(valores)}")
    if partes:
        return " · ".join(partes)
    return "ninguno"


def ids_de_modelos(modelos, nombres):
    """Los id_modelo de los modelos elegidos por su nombre."""
    return modelos.loc[modelos["nombre_modelo"].isin(nombres), "id_modelo"]


def filtrar_validos(validos, filtros):
    """
    Los datos validos (los de calidad.evaluar) reducidos a los pedidos y lineas
    que cumplen los filtros. Clientes, modelos y stock no cambian.
    """
    pedidos = validos["pedidos"]
    lineas = validos["lineas_pedido"]

    # 1. Condiciones del pedido
    if filtros.get("desde"):
        pedidos = pedidos[pedidos["fecha_pedido"] >= pd.Timestamp(filtros["desde"])]
    if filtros.get("hasta"):
        # hasta el final del dia: el 31 incluye un pedido del 31 a las 18:00
        dia_siguiente = pd.Timestamp(filtros["hasta"]) + pd.Timedelta(days=1)
        pedidos = pedidos[pedidos["fecha_pedido"] < dia_siguiente]
    if filtros.get("tipos"):
        pedidos = pedidos[pedidos["tipo_pedido"].isin(filtros["tipos"])]
    if filtros.get("estados"):
        pedidos = pedidos[pedidos["estado_pedido"].isin(filtros["estados"])]
    if filtros.get("clientes"):
        pedidos = pedidos[pedidos["id_cliente"].isin(filtros["clientes"])]
    lineas = lineas[lineas["id_pedido"].isin(pedidos["id_pedido"])]

    # 2. Condiciones de la linea
    if filtros.get("modelos"):
        ids_elegidos = ids_de_modelos(validos["modelos"], filtros["modelos"])
        lineas = lineas[lineas["id_modelo"].isin(ids_elegidos)]
    if filtros.get("tallas"):
        lineas = lineas[lineas["talla"].isin(filtros["tallas"])]
    if filtros.get("modelos") or filtros.get("tallas"):
        pedidos = pedidos[pedidos["id_pedido"].isin(lineas["id_pedido"])]

    # Una copia del diccionario con los pedidos y las lineas filtrados; el resto, igual
    filtrados = dict(validos)
    filtrados["pedidos"] = pedidos
    filtrados["lineas_pedido"] = lineas
    return filtrados


def filtrar_stock(validos, filtros):
    """El stock de los modelos y tallas elegidos (el periodo, el tipo, el estado y el cliente no lo cambian)."""
    stock = validos["stock"]
    if filtros.get("modelos"):
        stock = stock[stock["id_modelo"].isin(ids_de_modelos(validos["modelos"], filtros["modelos"]))]
    if filtros.get("tallas"):
        stock = stock[stock["talla"].isin(filtros["tallas"])]
    return stock


def calcular_filtrado(datos, validos, filtros):
    """
    Todas las tablas de analiticas.calcular_tablas y los 20 KPIs del
    subconjunto filtrado (sin filtros, son exactamente los de main.py).
    """
    tablas = analiticas.calcular_tablas(datos, filtrar_validos(validos, filtros))
    tablas["kpis"] = kpis.calcular_kpis(tablas["pedidos_unicos"], tablas["modelos_abc"], tablas["ventas_por_talla"],
                                        tablas["stock_variantes"], tablas["ventas_por_periodo"])
    return tablas


def tablas_inventario(validos, tablas_completas, corte, filtros, umbral=config.UMBRAL_STOCK_BAJO):
    """
    Stock por SKU y alertas con un umbral elegido, aplicando SOLO los filtros
    de modelo y talla. El stock es una foto en la fecha de corte (el periodo no
    lo cambia) y la demanda es siempre la de los 28 dias anteriores al corte,
    de todos los pedidos no cancelados de esos modelos y tallas.

    tablas_completas son las tablas sin filtrar (analiticas.calcular_tablas) y
    corte, la fecha de corte de la exportacion.
    """
    stock = filtrar_stock(validos, filtros)
    lineas = tablas_completas["lineas_enriquecidas"]
    if filtros.get("modelos"):
        lineas = lineas[lineas["nombre_modelo"].isin(filtros["modelos"])]
    if filtros.get("tallas"):
        lineas = lineas[lineas["talla"].isin(filtros["tallas"])]
    # El historial (para saber si hay 28 dias de pedidos) es el de toda la exportacion
    tabla = analiticas.stock_variantes(stock, validos["modelos"], lineas, tablas_completas["pedidos_unicos"],
                                       corte, umbral)
    return tabla, analiticas.stock_bajo(tabla)
