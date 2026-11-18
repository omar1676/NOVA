import pandas as pd

import analiticas
import config
import kpis

# Filtros vacios (ninguno puesto): asi empieza el dashboard. Sus claves son todos los filtros que hay
SIN_FILTROS = {"desde": None, "hasta": None, "modelos": [], "tallas": [], "tipos": [], "estados": [], "clientes": []}


# Devuelve True si hay al menos un filtro puesto en el diccionario de filtros
def hay_filtros(filtros):
    for clave in SIN_FILTROS:
        if filtros.get(clave):
            return True
    return False


# Devuelve un texto con los filtros activos ("ninguno" si no hay), para la pantalla y los CSV descargados
def describir(filtros):
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


# Pasa los nombres de modelo elegidos a sus id_modelo
# Recibe la tabla de modelos y la lista de nombres; devuelve una serie con los id_modelo
def ids_de_modelos(modelos, nombres):
    return modelos.loc[modelos["nombre_modelo"].isin(nombres), "id_modelo"]


# Aplica los filtros a los pedidos y a sus lineas
# Recibe las tablas validas (diccionario) y los filtros; devuelve una copia del diccionario ya filtrada
def filtrar_validos(validos, filtros):
    pedidos = validos["pedidos"]
    lineas = validos["lineas_pedido"]

    # 1. Condiciones del pedido (periodo, tipo, estado y cliente); despues, solo las lineas de esos pedidos
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

    # 2. Condiciones de la linea (modelo y talla)
    if filtros.get("modelos"):
        ids_elegidos = ids_de_modelos(validos["modelos"], filtros["modelos"])
        lineas = lineas[lineas["id_modelo"].isin(ids_elegidos)]
    if filtros.get("tallas"):
        lineas = lineas[lineas["talla"].isin(filtros["tallas"])]
    # Solo quedan los pedidos con alguna linea que cumpla el filtro
    if filtros.get("modelos") or filtros.get("tallas"):
        pedidos = pedidos[pedidos["id_pedido"].isin(lineas["id_pedido"])]

    # Una copia del diccionario con los pedidos y las lineas filtrados; el resto, igual
    filtrados = dict(validos)
    filtrados["pedidos"] = pedidos
    filtrados["lineas_pedido"] = lineas
    return filtrados


# Filtra el stock, solo por modelo y talla (es una foto en la fecha de corte, sin periodo)
# Devuelve la tabla de stock filtrada
def filtrar_stock(validos, filtros):
    stock = validos["stock"]
    if filtros.get("modelos"):
        stock = stock[stock["id_modelo"].isin(ids_de_modelos(validos["modelos"], filtros["modelos"]))]
    if filtros.get("tallas"):
        stock = stock[stock["talla"].isin(filtros["tallas"])]
    return stock


# Vuelve a calcular las tablas y los KPIs solo con los datos filtrados
# Recibe los datos leidos, los validos y los filtros; devuelve el diccionario de tablas (con "kpis")
def calcular_filtrado(datos, validos, filtros):
    tablas = analiticas.calcular_tablas(datos, filtrar_validos(validos, filtros))
    tablas["kpis"] = kpis.calcular_kpis(tablas["pedidos_unicos"], tablas["modelos_abc"], tablas["ventas_por_talla"],
                                        tablas["stock_variantes"], tablas["ventas_por_periodo"])
    return tablas


# Calcula la tabla de stock y la de stock bajo con los filtros de modelo y talla y el umbral elegido
# Devuelve las dos tablas: (stock, stock bajo)
def tablas_inventario(validos, tablas_completas, corte, filtros, umbral=config.UMBRAL_STOCK_BAJO):
    stock = filtrar_stock(validos, filtros)
    lineas = tablas_completas["lineas_enriquecidas"]
    if filtros.get("modelos"):
        lineas = lineas[lineas["nombre_modelo"].isin(filtros["modelos"])]
    if filtros.get("tallas"):
        lineas = lineas[lineas["talla"].isin(filtros["tallas"])]
    # El historial (para saber si hay 28 dias de pedidos) es el de toda la exportacion, sin filtrar
    tabla = analiticas.stock_variantes(stock, validos["modelos"], lineas, tablas_completas["pedidos_unicos"],
                                       corte, umbral)
    return tabla, analiticas.stock_bajo(tabla)
