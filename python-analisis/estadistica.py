"""
Estadistica descriptiva, tres hipotesis y bootstrap (apartados 6.6 y 6.7).

Las mismas funciones sirven para los datos de PRUEBA y para los SINTETICOS;
main.py escribe el origen en cada resultado.

OJO con los datos sinteticos: los inventa generador_datos.py con unas reglas
concretas. Si una hipotesis "se confirma" con ellos, lo unico que se comprueba
es que el metodo funciona y que el generador hace lo que se le pidio. No dice
nada de los clientes reales de NOVA.

Las tres hipotesis se escribieron ANTES de calcular ningun resultado:
  H1  Los pedidos Custom dejan mas importe por pedido que los estandar.
  H2  Las tallas centrales (41, 42 y 43) reunen mas de la mitad de los pares.
  H3  La demanda crece: los ultimos 6 meses tienen mas pares que los 6 anteriores.

Bootstrap: se sacan BOOTSTRAP_REMUESTREOS muestras nuevas del mismo tamano,
con reemplazo, y se calcula el estadistico en cada una. El intervalo al 95 %
va del percentil 2,5 al 97,5 de esos resultados. Semilla fija: config.SEMILLA.
"""
import numpy as np
import pandas as pd

import config
from analiticas import de_demanda, de_venta

TALLAS_CENTRALES = [41, 42, 43]

COLUMNAS_DESCRIPTIVOS = ["variable", "grupo", "unidad", "n", "media", "mediana", "moda", "desviacion_tipica",
                         "minimo", "p10", "p25", "p75", "p90", "maximo", "rango_intercuartilico",
                         "coef_variacion", "mejor_resumen", "motivo"]
COLUMNAS_HIPOTESIS = ["codigo", "hipotesis", "pregunta", "variable", "metodo", "n", "estimacion",
                      "ic_inferior", "ic_superior", "unidad", "resultado", "interpretacion",
                      "limitaciones", "no_se_puede_afirmar"]

AVISO_ORIGEN = {
    "SINTETICO": " Datos SINTÉTICOS: describe la simulación de generador_datos.py, no a los clientes de NOVA.",
    "PRUEBA": " Datos de PRUEBA de un solo día: no son ventas reales.",
    "REAL": "",
}


def aviso(tipo_origen):
    return AVISO_ORIGEN.get(tipo_origen, " Origen desconocido: no se sabe de qué base salen los datos.")


# ---------------------------------------------------------------------
# Estadistica descriptiva (apartado 6.6)
# ---------------------------------------------------------------------

def describir(valores, variable, grupo, unidad, con_moda):
    """
    Estadisticos de una variable, con pandas y NumPy.

    La moda solo se da en variables con pocos valores distintos (pares,
    precios de catalogo); en un importe casi nunca se repite el mismo valor.
    Si la media se separa mas de un 20 % de la mediana, unos pocos valores
    extremos la arrastran: entonces la mediana resume mejor el caso tipico.
    """
    valores = pd.Series(valores, dtype=float).dropna()
    fila = {"variable": variable, "grupo": grupo, "unidad": unidad, "n": len(valores)}
    if len(valores) == 0:
        fila["mejor_resumen"] = "sin datos"
        return fila
    media = valores.mean()
    mediana = valores.median()
    if len(valores) > 1:
        desviacion = valores.std()   # desviacion muestral (entre n - 1)
    else:
        desviacion = np.nan
    p10, p25, p75, p90 = np.percentile(valores, [10, 25, 75, 90])
    moda = None
    if con_moda:
        moda = valores.mode().iloc[0]
    coef_variacion = None
    if media != 0:
        coef_variacion = round(desviacion / media, 2)
    fila.update({
        "media": round(media, 2),
        "mediana": round(mediana, 2),
        "moda": moda,
        "desviacion_tipica": round(desviacion, 2),
        "minimo": round(valores.min(), 2),
        "p10": round(p10, 2),
        "p25": round(p25, 2),
        "p75": round(p75, 2),
        "p90": round(p90, 2),
        "maximo": round(valores.max(), 2),
        "rango_intercuartilico": round(p75 - p25, 2),
        "coef_variacion": coef_variacion,
    })
    # Cuanto se separa la media de la mediana, en tanto por uno (0,25 = un 25 %)
    if mediana != 0:
        separacion = (media - mediana) / mediana
    else:
        separacion = 0
    if abs(separacion) > 0.20:
        if separacion > 0:
            lado = "por encima"
        else:
            lado = "por debajo"
        fila["mejor_resumen"] = "mediana"
        fila["motivo"] = (f"la media está un {abs(separacion):.0%} {lado} de la mediana: unos pocos valores "
                          "extremos la arrastran y no representa al caso típico")
    else:
        fila["mejor_resumen"] = "media"
        fila["motivo"] = "media y mediana son parecidas: la media representa bien"
    return fila


def descriptivos(tablas):
    """
    Importe por pedido, pares por pedido y precio unitario de la demanda
    (pedidos no cancelados), para todos los pedidos y por tipo de pedido.
    """
    pedidos = de_demanda(tablas["pedidos_unicos"])
    lineas = de_demanda(tablas["lineas_enriquecidas"])
    filas = []
    for grupo in ["todos", "normal", "custom"]:
        if grupo == "todos":
            de_pedidos = pedidos
            de_lineas = lineas
        else:
            de_pedidos = pedidos[pedidos["tipo_pedido"] == grupo]
            de_lineas = lineas[lineas["tipo_pedido"] == grupo]
        filas.append(describir(de_pedidos["importe"], "importe por pedido", grupo, "€", con_moda=False))
        filas.append(describir(de_pedidos["pares"], "pares por pedido", grupo, "pares", con_moda=True))
        filas.append(describir(de_lineas["precio_unitario"], "precio unitario", grupo, "€/par", con_moda=True))
    tabla = pd.DataFrame(filas, columns=COLUMNAS_DESCRIPTIVOS)
    return tabla.sort_values("variable", kind="stable").reset_index(drop=True)


# ---------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------

def remuestrear(rng, valores):
    """Una muestra nueva del mismo tamano, sacada CON reemplazo: un valor puede salir varias veces."""
    return rng.choice(valores, size=len(valores), replace=True)


def intervalo(resultados):
    """Del percentil 2,5 al 97,5 de los resultados del bootstrap: intervalo al 95 %."""
    cola = (100 - config.NIVEL_CONFIANZA) / 2
    inferior, superior = np.percentile(resultados, [cola, 100 - cola])
    return round(float(inferior), 2), round(float(superior), 2)


def bootstrap_media(valores, semilla=config.SEMILLA, remuestreos=config.BOOTSTRAP_REMUESTREOS):
    """Intervalo al 95 % de la media."""
    valores = np.asarray(valores, dtype=float)
    rng = np.random.default_rng(semilla)
    medias = []
    for _ in range(remuestreos):
        medias.append(remuestrear(rng, valores).mean())
    return intervalo(medias)


def bootstrap_ticket_medio(pedidos_unicos, tipo_origen):
    """Ticket medio (importe medio de los pedidos de venta) con su intervalo bootstrap al 95 %."""
    importes = de_venta(pedidos_unicos)["importe"].astype(float).to_numpy()
    estimacion = None
    if len(importes) > 0:
        estimacion = round(float(importes.mean()), 2)
    fila = {"metrica": "ticket medio: importe medio por pedido de venta (confirmado en adelante)",
            "unidad": "€", "n": len(importes), "remuestreos": config.BOOTSTRAP_REMUESTREOS,
            "semilla": config.SEMILLA, "nivel_confianza_pct": config.NIVEL_CONFIANZA,
            "estimacion": estimacion,
            "ic_inferior": None, "ic_superior": None}
    if len(importes) < config.MINIMO_MUESTRA_HIPOTESIS:
        fila["resultado"] = "NO CALCULABLE"
        fila["interpretacion"] = (f"Con {len(importes)} pedido(s) de venta no se puede estimar un intervalo: "
                                  f"hacen falta al menos {config.MINIMO_MUESTRA_HIPOTESIS}." + aviso(tipo_origen))
        return pd.DataFrame([fila])
    inferior, superior = bootstrap_media(importes)
    fila.update({"ic_inferior": inferior, "ic_superior": superior, "resultado": "calculado"})
    fila["interpretacion"] = (f"Con estos {len(importes)} pedidos, el ticket medio está entre {inferior} y "
                              f"{superior} € con un 95 % de confianza. Es una media: los pedidos Custom, muy "
                              f"grandes, la suben." + aviso(tipo_origen))
    if len(importes) < config.MUESTRA_PEQUENA:
        fila["interpretacion"] += f" Muestra pequeña (menos de {config.MUESTRA_PEQUENA}): el intervalo es poco fiable."
    return pd.DataFrame([fila])


# ---------------------------------------------------------------------
# Las tres hipotesis (apartado 6.7)
# ---------------------------------------------------------------------

def veredicto(inferior, superior, referencia):
    """
    Si todo el intervalo queda por encima de la referencia, los datos apoyan
    la hipotesis; si queda todo por debajo, la contradicen. Si la referencia
    cae dentro del intervalo, no se puede decir: evidencia insuficiente.
    """
    if inferior > referencia:
        return "los datos la apoyan"
    if superior < referencia:
        return "los datos la contradicen"
    return f"evidencia insuficiente: el intervalo incluye {referencia}"


def aviso_muestra(*tamanos):
    """Texto de aviso si algun grupo tiene menos de MUESTRA_PEQUENA valores."""
    if min(tamanos) < config.MUESTRA_PEQUENA:
        return (f" Muestra pequeña (menos de {config.MUESTRA_PEQUENA} valores en algún grupo): "
                "el intervalo es poco fiable y el resultado, muy provisional.")
    return ""


def insuficiente(fila, motivo, tipo_origen):
    fila["resultado"] = f"evidencia insuficiente: {motivo}"
    fila["interpretacion"] = "No se puede contrastar con estos datos." + aviso(tipo_origen)
    return fila


def hipotesis_custom(pedidos_unicos, tipo_origen):
    demanda = de_demanda(pedidos_unicos)
    custom = demanda.loc[demanda["tipo_pedido"] == "custom", "importe"].astype(float).to_numpy()
    normal = demanda.loc[demanda["tipo_pedido"] == "normal", "importe"].astype(float).to_numpy()
    fila = {
        "codigo": "H1",
        "hipotesis": "Los pedidos Custom dejan más importe por pedido que los estándar",
        "pregunta": "¿Un pedido personalizado deja más dinero que uno estándar?",
        "variable": "importe por pedido (€), pedidos no cancelados",
        "metodo": "diferencia de medianas (Custom − estándar) con intervalo bootstrap al 95 %",
        "n": f"Custom {len(custom)}, estándar {len(normal)}",
        "unidad": "€",
        "limitaciones": "Los Custom son casi siempre de clubes y llevan muchos más pares: la diferencia puede "
                        "venir del tamaño del pedido y no de la personalización. Se usa la mediana porque los "
                        "importes están muy sesgados por unos pocos pedidos grandes.",
        "no_se_puede_afirmar": "Que personalizar un pedido haga gastar más a un mismo cliente: se comparan "
                               "grupos distintos de clientes, no es un experimento.",
    }
    if min(len(custom), len(normal)) < config.MINIMO_MUESTRA_HIPOTESIS:
        return insuficiente(fila, f"hacen falta al menos {config.MINIMO_MUESTRA_HIPOTESIS} pedidos de cada tipo",
                            tipo_origen)
    estimacion = np.median(custom) - np.median(normal)
    rng = np.random.default_rng(config.SEMILLA)
    diferencias = []
    for _ in range(config.BOOTSTRAP_REMUESTREOS):
        # Siempre primero la muestra Custom y despues la estandar: con la misma semilla salen las mismas
        muestra_custom = remuestrear(rng, custom)
        muestra_normal = remuestrear(rng, normal)
        diferencias.append(np.median(muestra_custom) - np.median(muestra_normal))
    inferior, superior = intervalo(diferencias)
    fila.update({"estimacion": round(float(estimacion), 2), "ic_inferior": inferior, "ic_superior": superior,
                 "resultado": veredicto(inferior, superior, 0)})
    fila["interpretacion"] = (f"La mediana de un pedido Custom supera a la de uno estándar en {estimacion:.2f} € "
                              f"(entre {inferior} y {superior} € con un 95 % de confianza)."
                              + aviso_muestra(len(custom), len(normal)) + aviso(tipo_origen))
    if tipo_origen == "SINTETICO":
        fila["interpretacion"] += (" El generador ya da a los Custom más pares y un recargo del 20 %: que se "
                                   "confirme solo prueba que el método lo detecta.")
    return fila


def hipotesis_tallas(lineas_enriquecidas, tipo_origen):
    demanda = de_demanda(lineas_enriquecidas)
    cantidades = demanda["cantidad"].astype(float).to_numpy()
    centrales = demanda["talla"].isin(TALLAS_CENTRALES).to_numpy()
    fila = {
        "codigo": "H2",
        "hipotesis": "Las tallas centrales (41, 42 y 43) reúnen más de la mitad de los pares pedidos",
        "pregunta": "¿Conviene concentrar la fabricación en las tallas 41 a 43?",
        "variable": "% de pares de demanda en las tallas 41, 42 y 43",
        "metodo": "proporción de pares con intervalo bootstrap al 95 % (remuestreando líneas), frente al 50 %",
        "n": f"{len(cantidades)} líneas",
        "unidad": "%",
        "limitaciones": "Remuestrear líneas supone que son independientes, pero las de un mismo pedido Custom "
                        "no lo son (un club pide varias tallas a la vez): el intervalo real sería algo más ancho.",
        "no_se_puede_afirmar": "Qué tallas habrá que fabricar el mes que viene: la proporción depende mucho "
                               "de los pedidos de club que entren.",
    }
    if len(cantidades) < config.MINIMO_MUESTRA_HIPOTESIS or cantidades.sum() == 0:
        return insuficiente(fila, f"hacen falta al menos {config.MINIMO_MUESTRA_HIPOTESIS} líneas", tipo_origen)
    estimacion = 100 * cantidades[centrales].sum() / cantidades.sum()
    rng = np.random.default_rng(config.SEMILLA)
    proporciones = []
    for _ in range(config.BOOTSTRAP_REMUESTREOS):
        indices = rng.integers(0, len(cantidades), size=len(cantidades))   # lineas al azar, con reemplazo
        de_la_muestra = cantidades[indices]
        es_central = centrales[indices]   # True si la linea elegida es de las tallas 41 a 43
        pares_centrales = de_la_muestra[es_central].sum()
        proporciones.append(100 * pares_centrales / de_la_muestra.sum())
    inferior, superior = intervalo(proporciones)
    fila.update({"estimacion": round(float(estimacion), 1), "ic_inferior": inferior, "ic_superior": superior,
                 "resultado": veredicto(inferior, superior, 50)})
    fila["interpretacion"] = (f"El {estimacion:.1f} % de los pares son de las tallas 41 a 43 (entre {inferior} y "
                              f"{superior} % con un 95 % de confianza)."
                              + aviso_muestra(len(cantidades)) + aviso(tipo_origen))
    return fila


def hipotesis_crecimiento(pedidos_unicos, tipo_origen):
    demanda = de_demanda(pedidos_unicos)
    fila = {
        "codigo": "H3",
        "hipotesis": "La demanda crece: los últimos 6 meses tienen más pares al mes que los 6 anteriores",
        "pregunta": "¿Hay que prever más producción para los próximos meses?",
        "variable": "pares de demanda por mes",
        "metodo": "diferencia de medias mensuales (últimos 6 meses − 6 anteriores) con intervalo bootstrap "
                  "al 95 % (remuestreando meses dentro de cada periodo)",
        "unidad": "pares/mes",
        "limitaciones": "Solo hay 6 meses en cada grupo y no son los mismos meses del año: la estacionalidad "
                        "se mezcla con el crecimiento. Los meses seguidos no son independientes.",
        "no_se_puede_afirmar": "Que la demanda vaya a seguir creciendo. Y si sale evidencia insuficiente, "
                               "tampoco que no crezca: no ver una diferencia no demuestra que no exista.",
    }
    if len(demanda) == 0:
        fila["n"] = "0 meses"
        return insuficiente(fila, "no hay pedidos", tipo_origen)
    meses = demanda["fecha_pedido"].dt.to_period("M")
    por_mes = demanda.groupby(meses)["pares"].sum()
    # Todos los meses entre el primero y el ultimo; un mes sin pedidos queda con 0 pares
    todos_los_meses = pd.period_range(por_mes.index.min(), por_mes.index.max(), freq="M")
    por_mes = por_mes.reindex(todos_los_meses, fill_value=0)
    fila["n"] = f"{len(por_mes)} meses"
    if len(por_mes) < 12:
        return insuficiente(fila, f"hacen falta 12 meses seguidos y hay {len(por_mes)}", tipo_origen)
    ultimos = por_mes.iloc[-6:].to_numpy(dtype=float)
    anteriores = por_mes.iloc[-12:-6].to_numpy(dtype=float)
    fila["n"] = (f"6 meses ({por_mes.index[-6]} a {por_mes.index[-1]}) frente a 6 meses "
                 f"({por_mes.index[-12]} a {por_mes.index[-7]})")
    estimacion = ultimos.mean() - anteriores.mean()
    rng = np.random.default_rng(config.SEMILLA)
    diferencias = []
    for _ in range(config.BOOTSTRAP_REMUESTREOS):
        # Siempre primero los ultimos 6 meses y despues los 6 anteriores (mismo orden de azar)
        muestra_ultimos = remuestrear(rng, ultimos)
        muestra_anteriores = remuestrear(rng, anteriores)
        diferencias.append(muestra_ultimos.mean() - muestra_anteriores.mean())
    inferior, superior = intervalo(diferencias)
    resultado = veredicto(inferior, superior, 0)
    fila.update({"estimacion": round(float(estimacion), 1), "ic_inferior": inferior, "ic_superior": superior,
                 "resultado": resultado})
    fila["interpretacion"] = (f"Los últimos 6 meses tienen de media {estimacion:+.1f} pares al mes respecto a los "
                              f"6 anteriores (entre {inferior} y {superior} con un 95 % de confianza)."
                              + aviso(tipo_origen))
    if tipo_origen == "SINTETICO" and resultado.startswith("evidencia insuficiente"):
        fila["interpretacion"] += (" La simulación sí tiene un crecimiento del 2 % al mes, pero con 6 meses por grupo "
                                   "y pedidos Custom tan grandes los datos no bastan para demostrarlo.")
    return fila


def contrastar_hipotesis(tablas, tipo_origen):
    """Las tres hipotesis, una fila cada una."""
    filas = [
        hipotesis_custom(tablas["pedidos_unicos"], tipo_origen),
        hipotesis_tallas(tablas["lineas_enriquecidas"], tipo_origen),
        hipotesis_crecimiento(tablas["pedidos_unicos"], tipo_origen),
    ]
    return pd.DataFrame(filas, columns=COLUMNAS_HIPOTESIS)
