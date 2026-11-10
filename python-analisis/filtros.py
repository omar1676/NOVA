"""
Filtros combinables (apartados 6.12 y 6.16), para el dashboard y la consola.

Cinco filtros: periodo, modelo, talla, tipo de pedido y estado del pedido.
Un filtro vacio (None o lista vacia) no restringe nada.

Como se aplican:
- El periodo, el tipo y el estado son datos del PEDIDO: se quedan los pedidos
  que los cumplen, con todas sus lineas. El periodo incluye el dia final entero.
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

SIN_FILTROS = {"desde": None, "hasta": None, "modelos": [], "tallas": [], "tipos": [], "estados": []}


def hay_filtros(filtros):
    """True si algun filtro restringe algo."""
    return any(filtros.get(clave) for clave in SIN_FILTROS)


def describir(filtros):
    """Los filtros en una linea de texto, para el pie de graficos, las descargas y el registro."""
    partes = []
    if filtros.get("desde") or filtros.get("hasta"):
        partes.append(f"periodo {filtros.get('desde') or 'inicio'} a {filtros.get('hasta') or 'fin'}")
    nombres = {"modelos": "modelo", "tallas": "talla", "tipos": "tipo", "estados": "estado"}
    for clave, nombre in nombres.items():
        if filtros.get(clave):
            partes.append(f"{nombre}: {', '.join(str(valor) for valor in filtros[clave])}")
    return " · ".join(partes) if partes else "ninguno"


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
        pedidos = pedidos[pedidos["fecha_pedido"] < pd.Timestamp(filtros["hasta"]) + pd.Timedelta(days=1)]
    if filtros.get("tipos"):
        pedidos = pedidos[pedidos["tipo_pedido"].isin(filtros["tipos"])]
    if filtros.get("estados"):
        pedidos = pedidos[pedidos["estado_pedido"].isin(filtros["estados"])]
    lineas = lineas[lineas["id_pedido"].isin(pedidos["id_pedido"])]

    # 2. Condiciones de la linea
    if filtros.get("modelos"):
        lineas = lineas[lineas["id_modelo"].isin(ids_de_modelos(validos["modelos"], filtros["modelos"]))]
    if filtros.get("tallas"):
        lineas = lineas[lineas["talla"].isin(filtros["tallas"])]
    if filtros.get("modelos") or filtros.get("tallas"):
        pedidos = pedidos[pedidos["id_pedido"].isin(lineas["id_pedido"])]

    return {**validos, "pedidos": pedidos, "lineas_pedido": lineas}


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
    stock = validos["stock"]
    lineas = tablas_completas["lineas_enriquecidas"]
    if filtros.get("modelos"):
        stock = stock[stock["id_modelo"].isin(ids_de_modelos(validos["modelos"], filtros["modelos"]))]
        lineas = lineas[lineas["nombre_modelo"].isin(filtros["modelos"])]
    if filtros.get("tallas"):
        stock = stock[stock["talla"].isin(filtros["tallas"])]
        lineas = lineas[lineas["talla"].isin(filtros["tallas"])]
    # El historial (para saber si hay 28 dias de pedidos) es el de toda la exportacion
    tabla = analiticas.stock_variantes(stock, validos["modelos"], lineas, tablas_completas["pedidos_unicos"],
                                       corte, umbral)
    return tabla, analiticas.stock_bajo(tabla)
