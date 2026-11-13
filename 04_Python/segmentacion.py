"""
Segmentacion de clientes: RFM y KMeans (apartado 6.8 y DataFrame 06).

RFM, una fila por cliente:
  Recency    dias desde su ultima compra valida hasta la fecha de corte
  Frequency  numero de PEDIDOS de venta (no lineas: un pedido de 3 lineas es 1)
  Monetary   importe de esos pedidos (euros, IVA pendiente de confirmar)
Compra valida = pedido de venta (config.ESTADOS_CONFIRMADOS), el mismo
criterio que los KPIs, y nunca posterior a la fecha de corte.

Puntuaciones de 1 a 5 por quintiles: el 20 % de clientes mas recientes tiene
R = 5, el 20 % con mas pedidos F = 5 y el 20 % con mas importe M = 5. Son
puntuaciones relativas: comparan a los clientes entre si.

KMeans (scikit-learn) agrupa a los mismos clientes con las mismas tres
variables. Sus grupos son matematicos: se describen y se comparan con RFM,
pero no son categorias comerciales ni perfiles reales de NOVA.
"""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

import config
from analiticas import NO_CALCULABLE, cruzar, de_venta, no_calculable

SIN_COMPRAS = "Sin compras válidas"

# Que significa cada segmento y para que sirve (en el orden en que se aplican las reglas)
SEGMENTOS = {
    SIN_COMPRAS: "no tiene ningún pedido de venta: no se le inventa actividad. Captar o reactivar",
    "Mejores clientes": "R, F y M de 4 o más: compran a menudo, hace poco y mucho importe. Cuidarlos y priorizar sus pedidos",
    "En riesgo": "F de 3 o más pero R de 2 o menos: compraban a menudo y llevan tiempo sin comprar. Contactarlos antes de perderlos",
    "Habituales": "F de 3 o más: compran con regularidad. Mantener la relación y ofrecer reposición",
    "Inactivos": "R de 2 o menos y F menor que 3: compraron poco y hace tiempo. Campañas de baja prioridad",
    "Ocasionales": "el resto: pocas compras pero recientes. Intentar que repitan",
}


def rfm(pedidos_unicos, clientes, fecha_corte):
    """
    Recency, Frequency y Monetary de cada cliente, tambien de los que no han
    comprado (con frequency 0, monetary 0 y recency vacia: no hay ultima compra).
    """
    venta = de_venta(pedidos_unicos)
    venta = venta[venta["fecha_pedido"] <= fecha_corte]   # nunca pedidos posteriores al corte
    por_cliente = venta.groupby("id_cliente").agg(
        ultima_compra=("fecha_pedido", "max"),
        frequency=("id_pedido", "nunique"),
        monetary=("importe", "sum"),
    ).reset_index()

    tabla = clientes[["id_cliente", "tipo"]].rename(columns={"tipo": "tipo_cliente"})
    tabla = cruzar(tabla, por_cliente, "id_cliente", "one_to_one", "clientes-rfm", exigir_pareja=False)
    # Sin compras: 0 pedidos y 0 euros son recuentos; la recency queda vacia
    tabla["frequency"] = tabla["frequency"].fillna(0).astype(int)
    tabla["monetary"] = tabla["monetary"].fillna(0.0).round(2)
    tabla["recency_dias"] = (fecha_corte - tabla["ultima_compra"]).dt.days
    tabla = tabla.sort_values("id_cliente").reset_index(drop=True)
    return puntuar(tabla)


def quintil(valores, de_mayor_a_menor):
    """
    Puntuacion de 1 a 5 por quintiles. rank(method="first") deshace los
    empates por orden de id_cliente, asi siempre sale lo mismo.
    """
    if de_mayor_a_menor:
        etiquetas = [5, 4, 3, 2, 1]
    else:
        etiquetas = [1, 2, 3, 4, 5]
    posiciones = valores.rank(method="first")   # 1, 2, 3... sin empates
    # qcut reparte las posiciones en 5 grupos del mismo tamano y les pone la etiqueta
    return pd.qcut(posiciones, 5, labels=etiquetas).astype(int)


def puntuar(tabla):
    """Anade las puntuaciones R, F y M y el segmento (si hay clientes suficientes)."""
    con_compras = tabla["frequency"] > 0
    for columna in ["r_score", "f_score", "m_score"]:
        tabla[columna] = pd.Series(pd.NA, index=tabla.index, dtype="Int64")   # entero que admite vacio
    if con_compras.sum() < config.MINIMO_CLIENTES_RFM:
        tabla["segmento"] = np.where(con_compras, f"{NO_CALCULABLE}: menos de {config.MINIMO_CLIENTES_RFM} "
                                     "clientes con compras", SIN_COMPRAS)
        return tabla
    compradores = tabla[con_compras]
    # Recency: menos dias es mejor (el mas reciente tiene un 5)
    tabla.loc[con_compras, "r_score"] = quintil(compradores["recency_dias"], de_mayor_a_menor=True)
    tabla.loc[con_compras, "f_score"] = quintil(compradores["frequency"], de_mayor_a_menor=False)
    tabla.loc[con_compras, "m_score"] = quintil(compradores["monetary"], de_mayor_a_menor=False)
    tabla["segmento"] = [segmento(fila) for _, fila in tabla.iterrows()]
    return tabla


def segmento(fila):
    """Las reglas de los segmentos, en orden: la primera que se cumple decide."""
    if fila["frequency"] == 0:
        return SIN_COMPRAS
    r, f, m = fila["r_score"], fila["f_score"], fila["m_score"]
    if r >= 4 and f >= 4 and m >= 4:
        return "Mejores clientes"
    if f >= 3 and r <= 2:
        return "En riesgo"
    if f >= 3:
        return "Habituales"
    if r <= 2:
        return "Inactivos"
    return "Ocasionales"


def resumen_segmentos(tabla_rfm):
    """Una fila por segmento: cuantos clientes, sus medias y que parte del importe se llevan."""
    segmentos = dict(SEGMENTOS)
    # Si RFM no se ha podido calcular, sale tambien esa fila
    for nombre in tabla_rfm["segmento"].unique():
        if nombre.startswith(NO_CALCULABLE):
            segmentos[nombre] = "hay compras, pero muy pocos clientes para repartirlos en quintiles"
    total_importe = tabla_rfm["monetary"].sum()
    filas = []
    for nombre, significado in segmentos.items():
        del_segmento = tabla_rfm[tabla_rfm["segmento"] == nombre]
        clientes = len(del_segmento)
        importe_segmento = del_segmento["monetary"].sum()
        # Sin clientes (o sin importe) no hay medias ni porcentajes: vacio, no 0
        porcentaje_clientes = None
        if len(tabla_rfm) > 0:
            porcentaje_clientes = round(100 * clientes / len(tabla_rfm), 1)
        recency_media = None
        frequency_media = None
        if clientes > 0:
            recency_media = round(del_segmento["recency_dias"].mean(), 1)
            frequency_media = round(del_segmento["frequency"].mean(), 1)
        porcentaje_importe = None
        if total_importe != 0:
            porcentaje_importe = round(100 * importe_segmento / total_importe, 1)
        filas.append({
            "segmento": nombre,
            "clientes": clientes,
            "porcentaje_clientes": porcentaje_clientes,
            "recency_media_dias": recency_media,
            "frequency_media": frequency_media,
            "monetary_total": round(importe_segmento, 2),
            "porcentaje_importe": porcentaje_importe,
            "significado_y_uso": significado,
        })
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------
# KMeans
# ---------------------------------------------------------------------

def variables_kmeans(compradores):
    """
    Las tres variables RFM, preparadas para KMeans:
    - frequency y monetary con logaritmo (log(1 + x)): unos pocos clubes con
      importes enormes decidirian ellos solos los grupos;
    - todas estandarizadas (media 0, desviacion 1): los dias, los pedidos y
      los euros tienen escalas muy distintas y KMeans mide distancias.
    """
    variables = pd.DataFrame({
        "recency_dias": compradores["recency_dias"].astype(float),
        "log_frequency": np.log1p(compradores["frequency"].astype(float)),
        "log_monetary": np.log1p(compradores["monetary"].astype(float)),
    })
    nulos = int(variables.isna().sum().sum())
    if nulos > 0:
        raise ValueError(f"Hay {nulos} valores vacíos en las variables de KMeans")
    return StandardScaler().fit_transform(variables)


def kmeans_clientes(tabla_rfm):
    """
    Agrupa con KMeans a los clientes con compras, probando k = 2, 3, 4 y 5.
    Criterio para elegir k: el silhouette mas alto (si empatan, el k menor).
    El silhouette va de -1 a 1: cuanto mas alto, mas separados estan los grupos.

    Devuelve (seleccion de k, descripcion de los grupos, tabla_rfm con la columna cluster).
    """
    compradores = tabla_rfm[tabla_rfm["frequency"] > 0].copy()
    tabla = tabla_rfm.copy()
    tabla["cluster"] = pd.Series(pd.NA, index=tabla.index, dtype="Int64")
    if len(compradores) < config.MINIMO_CLIENTES_KMEANS:
        motivo = (f"hacen falta al menos {config.MINIMO_CLIENTES_KMEANS} clientes con compras y hay "
                  f"{len(compradores)}: los grupos no significarian nada")
        return no_calculable(motivo), no_calculable(motivo), tabla

    datos = variables_kmeans(compradores)
    filas = []
    for k in config.KMEANS_K:
        if k >= len(compradores):   # el silhouette necesita menos grupos que clientes
            continue
        modelo = KMeans(n_clusters=k, random_state=config.SEMILLA, n_init=10).fit(datos)
        silhouette = silhouette_score(datos, modelo.labels_)
        filas.append({"k": k, "silhouette": round(float(silhouette), 3),
                      "inercia": round(float(modelo.inertia_), 2)})
    seleccion = pd.DataFrame(filas)
    # El primero al ordenar: el silhouette mas alto y, si empatan, el k mas pequeno
    ordenada = seleccion.sort_values(["silhouette", "k"], ascending=[False, True])
    mejor_k = int(ordenada["k"].iloc[0])
    seleccion["elegido"] = seleccion["k"] == mejor_k

    modelo = KMeans(n_clusters=mejor_k, random_state=config.SEMILLA, n_init=10).fit(datos)
    compradores["cluster"] = modelo.labels_
    # Los numeros de KMeans no significan nada: se renumeran de mas a menos importe medio
    importe_medio = compradores.groupby("cluster")["monetary"].mean()
    orden = importe_medio.sort_values(ascending=False).index   # numeros de KMeans, del mayor importe al menor
    nuevo_numero = {}
    for numero, antiguo in enumerate(orden, start=1):
        nuevo_numero[antiguo] = numero
    compradores["cluster"] = compradores["cluster"].map(nuevo_numero)
    tabla.loc[compradores.index, "cluster"] = compradores["cluster"]
    return seleccion, describir_clusters(compradores), tabla


def describir_clusters(compradores):
    """
    Cada grupo con sus medias y un nombre que sale de comparar sus medias con
    la MEDIANA de todos los clientes con compras (la media la moverian los
    pocos clientes muy extremos): importe alto o bajo, muchos o pocos pedidos,
    compra reciente o no, y si son sobre todo empresas o particulares.
    """
    mediana_r = compradores["recency_dias"].median()
    mediana_f = compradores["frequency"].median()
    mediana_m = compradores["monetary"].median()
    filas = []
    for numero, grupo in compradores.groupby("cluster"):
        r = grupo["recency_dias"].mean()
        f = grupo["frequency"].mean()
        m = grupo["monetary"].mean()
        empresas = 100 * (grupo["tipo_cliente"] == "empresa").mean()
        if empresas >= 50:
            tipo = "empresas"
        else:
            tipo = "particulares"
        if m > mediana_m:
            importe = "alto"
        else:
            importe = "bajo"
        if f > mediana_f:
            pedidos = "muchos pedidos"
        else:
            pedidos = "pocos pedidos"
        if r <= mediana_r:
            compra = "compra reciente"
        else:
            compra = "sin comprar hace más tiempo"
        nombre = f"{tipo}: importe {importe}, {pedidos}, {compra}"
        filas.append({
            "cluster": numero,
            "nombre": nombre,
            "clientes": len(grupo),
            "porcentaje_clientes": round(100 * len(grupo) / len(compradores), 1),
            "recency_media_dias": round(r, 1),
            "frequency_media": round(f, 1),
            "monetary_medio": round(m, 2),
            "monetary_mediana": round(grupo["monetary"].median(), 2),
            "porcentaje_empresas": round(empresas, 1),
        })
    return pd.DataFrame(filas)


def comparar_rfm_kmeans(tabla_con_cluster):
    """Cuantos clientes de cada segmento RFM caen en cada grupo de KMeans (tabla cruzada)."""
    compradores = tabla_con_cluster[tabla_con_cluster["cluster"].notna()]
    if len(compradores) == 0:
        return no_calculable("KMeans no se ha podido calcular")
    tabla = pd.crosstab(compradores["segmento"], compradores["cluster"].astype(int))
    tabla.columns = [f"cluster_{numero}" for numero in tabla.columns]
    tabla["total"] = tabla.sum(axis=1)
    return tabla.reset_index()


def segmentar_clientes(pedidos_unicos, clientes, fecha_corte):
    """
    RFM, KMeans y la comparacion de los dos, en este orden. Devuelve las cinco
    tablas en un diccionario (su nombre es el del CSV). La usan main.py y el dashboard.
    """
    tabla_rfm = rfm(pedidos_unicos, clientes, fecha_corte)
    resumen = resumen_segmentos(tabla_rfm)
    # kmeans_clientes devuelve tres cosas: la eleccion de k, los grupos y la tabla RFM con la columna cluster
    seleccion_k, clusters, tabla_rfm = kmeans_clientes(tabla_rfm)
    return {
        "rfm_clientes": tabla_rfm,
        "rfm_segmentos": resumen,
        "kmeans_seleccion_k": seleccion_k,
        "kmeans_clusters": clusters,
        "rfm_frente_a_kmeans": comparar_rfm_kmeans(tabla_rfm),
    }
