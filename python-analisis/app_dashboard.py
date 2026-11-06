"""
Dashboard de NOVA Sneakers (apartados 6.14 a 6.17). Desde python-analisis:

    .venv\\Scripts\\streamlit.exe run app_dashboard.py

Este archivo solo ORQUESTA y MUESTRA. Ningun calculo esta aqui:
- actualizacion.ciclo: comprobar los CSV, validarlos, recalcular todo y anotarlo;
- filtros: las tablas y los KPIs del subconjunto filtrado (las mismas funciones de main.py);
- visualizaciones: los graficos Matplotlib de main.py;
- informe: las cinco conclusiones.

Refresco cada 60 s: panel() es un st.fragment(run_every="60s"). Streamlit la
vuelve a ejecutar cada 60 segundos mientras la pagina esta abierta, y si han
pasado 60 s desde la ultima comprobacion llama a actualizacion.ciclo, que
RELEE los CSV del disco. No hay time.sleep ni bucles: lo programa Streamlit.
"""
import tempfile
from datetime import datetime

import pandas as pd
import streamlit as st

import actualizacion
import config
import filtros
import kpis
import pipeline
import registro
import visualizaciones
from analiticas import NO_CALCULABLE
from informe import no_calculable, numero

# Cada origen tiene su carpeta: nunca se mezclan. El primero es el de por defecto
# (la exportacion de Acceso a Datos). Su tipo (PRUEBA o REAL) lo dice ORIGEN.txt.
# El nombre visible sale en la direccion: ?origen=Sintéticos+limpios&pestana=Clientes
ORIGENES = {
    "acc": ("Exportación ACC", config.CARPETA_ENTRADA),
    "sinteticos": ("Sintéticos limpios", config.CARPETA_SINTETICOS_LIMPIOS),
    "sinteticos-errores": ("Sintéticos con errores", config.CARPETA_SINTETICOS_ERRORES),
}
PESTANAS = ["Dirección", "Productos", "Clientes", "Inventario", "Calidad", "Predicción"]
COLOR_ORIGEN = {"REAL": "green", "PRUEBA": "orange", "SINTETICO": "violet"}
# Cada color de zapatilla se pinta con su color (el blanco, gris claro para que se vea)
COLOR_PRODUCTO = {"Negro": "#222222", "Blanco": "#d9d9d9", "Gris": "#8c8c8c", "Rojo": "#c62828", "Azul": "#1f5fa8",
                  "Verde": "#2e7d32", "Beige": "#d8c3a5", "Crema": "#efe3c8", "Rosa": "#e991b0"}
FORMATO_HORA = "%d/%m/%Y %H:%M:%S"
# El temporizador de Streamlit no es exacto: se da por cumplido el minuto 5 s antes
MARGEN_SEGUNDOS = 5


# ---------------------------------------------------------------------
# Refresco
# ---------------------------------------------------------------------

def actualizar(nombre, operacion=None):
    """
    Lanza un ciclo de comprobacion y recalculo del origen si toca: la primera
    vez, si se pide a mano o si han pasado 60 s desde la ultima comprobacion.
    Cada origen guarda su propio estado. Devuelve True si ha hecho el ciclo.
    """
    estados = st.session_state.setdefault("estados", {})
    anterior = estados.get(nombre)
    if operacion is None:
        if anterior is None:
            operacion = "carga inicial del origen"
        elif (datetime.now() - anterior["comprobado"]).total_seconds() >= config.SEGUNDOS_REFRESCO - MARGEN_SEGUNDOS:
            operacion = "comprobación automática (60 s)"
        else:
            return False
    estados[nombre] = actualizacion.ciclo(ORIGENES[nombre][1], anterior, operacion)
    return True


# ---------------------------------------------------------------------
# Filtros (barra lateral)
# ---------------------------------------------------------------------

def restablecer_filtros(sufijo, primero, ultimo):
    st.session_state[f"periodo_{sufijo}"] = (primero, ultimo)
    for nombre in ["modelos", "tallas", "tipos", "estados"]:
        st.session_state[f"{nombre}_{sufijo}"] = []


def lista_filtro(etiqueta, opciones, clave):
    """Un filtro de varias opciones. Quita de lo elegido lo que ya no existe (tras una exportacion nueva)."""
    st.session_state[clave] = [valor for valor in st.session_state.get(clave, []) if valor in opciones]
    return st.multiselect(etiqueta, opciones, key=clave, placeholder="Todos")


def elegir_filtros(nombre, estado):
    """Los cinco filtros. Cada origen recuerda los suyos (clave con su numero)."""
    st.subheader("Filtros")
    publicado = estado["publicado"]
    if publicado is None or len(publicado["validos"]["pedidos"]) == 0:
        st.caption("No hay pedidos válidos que filtrar.")
        return dict(filtros.SIN_FILTROS)
    sufijo = list(ORIGENES).index(nombre)
    pedidos = publicado["validos"]["pedidos"]
    lineas = publicado["tablas"]["lineas_enriquecidas"]
    primero = pedidos["fecha_pedido"].min().date()
    ultimo = pedidos["fecha_pedido"].max().date()

    # Si el periodo era el completo (nadie lo ha restringido), sigue siendo el completo cuando una
    # exportacion nueva trae fechas nuevas: si no, los pedidos nuevos quedarian fuera sin avisar
    clave = f"periodo_{sufijo}"
    guardado = st.session_state.get(clave)
    sin_restringir = guardado is None or tuple(guardado) == st.session_state.get(f"rango_{sufijo}")
    fuera = guardado is not None and any(dia < primero or dia > ultimo for dia in guardado)
    if sin_restringir or fuera:
        st.session_state[clave] = (primero, ultimo)
    st.session_state[f"rango_{sufijo}"] = (primero, ultimo)
    periodo = st.date_input("Periodo (fecha del pedido)", min_value=primero, max_value=ultimo, key=clave,
                            format="DD/MM/YYYY")
    elegidos = {
        "desde": None,
        "hasta": None,
        "modelos": lista_filtro("Modelo", sorted(publicado["validos"]["modelos"]["nombre_modelo"]), f"modelos_{sufijo}"),
        "tallas": lista_filtro("Talla", sorted(int(talla) for talla in lineas["talla"].dropna().unique()),
                               f"tallas_{sufijo}"),
        "tipos": lista_filtro("Tipo de pedido", config.TIPOS_PEDIDO, f"tipos_{sufijo}"),
        "estados": lista_filtro("Estado del pedido", config.ESTADOS_PEDIDO, f"estados_{sufijo}"),
    }
    # El periodo solo filtra si no es el completo (y cuando ya se han elegido las dos fechas)
    if len(periodo) == 2 and (periodo[0] > primero or periodo[1] < ultimo):
        elegidos["desde"], elegidos["hasta"] = periodo[0].isoformat(), periodo[1].isoformat()
    elif len(periodo) == 1:
        st.caption("Elige también la fecha final: mientras tanto se usa el periodo completo.")
    st.button("Restablecer filtros", on_click=restablecer_filtros, args=(sufijo, primero, ultimo),
              icon=":material/filter_alt_off:", width="stretch")
    st.caption("Los filtros se combinan (todos a la vez). Un filtro vacío no restringe nada.")
    return elegidos


# ---------------------------------------------------------------------
# Piezas que se repiten: tarjetas, tablas, graficos y descargas
# ---------------------------------------------------------------------

def texto_kpi(fila):
    """El valor de un KPI para una tarjeta, o N/D si no se puede calcular."""
    valor = fila["valor"]
    if fila["estado"] != "calculado" or valor is None or (not isinstance(valor, str) and pd.isna(valor)):
        return "N/D"
    if isinstance(valor, str):
        return valor
    # Euros, porcentajes y semanas llevan su unidad; los recuentos ya la dicen en el titulo
    if fila["unidad"].startswith("€"):
        return f"{numero(valor, 2)} €"
    texto = numero(valor, 0 if float(valor).is_integer() else 1)
    return f"{texto} {fila['unidad']}" if fila["unidad"] in ["%", "semanas"] else texto


def tarjeta(columna, fila, etiqueta=None):
    """Una tarjeta con un KPI de kpis.py; la ayuda dice su formula y su poblacion."""
    ayuda = f"{fila['formula']} ({fila['unidad']}). Población: {fila['poblacion']}."
    if fila["detalle"]:
        ayuda += f" {fila['detalle']}."
    columna.metric(etiqueta or fila["nombre"], texto_kpi(fila), help=ayuda, border=True)


def alcance(c, filtrado=True):
    """Etiqueta que dice si lo que sigue usa los filtros o es global."""
    if not filtrado:
        st.badge("Global: no usa los filtros", icon=":material/public:", color="gray")
    elif filtros.hay_filtros(c["filtros"]):
        st.badge(f"Filtrado: {c['texto_filtros']}", icon=":material/filter_alt:", color="blue")
    else:
        st.badge("Todos los datos (sin filtros)", icon=":material/filter_alt_off:", color="gray")


def preparar(tabla):
    """La tabla tal como se ensena y se descarga: indice como columna, nombres de columna como texto
    (en la matriz de tallas son numeros) y sin datos personales."""
    if tabla.index.name is not None:
        tabla = tabla.reset_index()
    tabla = pipeline.sin_datos_personales(tabla)
    tabla.columns = [str(columna) for columna in tabla.columns]
    return tabla


def tabla(datos, alto="auto"):
    """Una tabla consultable (ordenable y con busqueda), con los euros formateados."""
    datos = preparar(datos)
    formatos = {columna: st.column_config.NumberColumn(format="%.2f €") for columna in datos.columns
                if any(palabra in str(columna) for palabra in ["importe", "ticket", "monetary"])}
    st.dataframe(datos, hide_index=True, column_config=formatos, height=alto)


def anotar_descarga(archivo, filas, origen, carpeta, version, texto_filtros):
    registro.anotar(config.ARCHIVO_REGISTRO, origen=origen, carpeta=carpeta, operacion=f"descarga de {archivo}",
                    resultado="correcto", filas_procesadas=filas, version_datos=version,
                    detalle=f"filtros: {texto_filtros}")


def descarga(datos, nombre, c, filtrado=True):
    """Boton para descargar la MISMA tabla que se ve, en CSV UTF-8, con su origen y sus filtros."""
    datos = preparar(datos)
    texto_filtros = c["texto_filtros"] if filtrado else "ninguno (resultado global)"
    archivo = f"{nombre}_{c['publicado']['tipo'].lower()}.csv"
    st.download_button(
        f"Descargar {nombre}.csv", pipeline.csv_descarga(datos, c["estado"]["origen"], c["ejecucion"], texto_filtros),
        file_name=archivo, mime="text/csv", key=f"descarga_{nombre}", icon=":material/download:",
        on_click=anotar_descarga,
        args=(archivo, len(datos), c["estado"]["origen"], actualizacion.carpeta_relativa(c["estado"]["carpeta"]),
              c["publicado"]["version"], texto_filtros))


def carpeta_graficos():
    """Una carpeta temporal por sesion para los PNG (se sobrescriben: no se acumulan)."""
    if "carpeta_graficos" not in st.session_state:
        st.session_state["carpeta_graficos"] = tempfile.mkdtemp(prefix="nova_graficos_")
    return st.session_state["carpeta_graficos"]


def grafico(funcion, entrada, datos, c, **opciones):
    """Un grafico de visualizaciones.py y, debajo, la tabla de datos que lo dibuja."""
    ruta = funcion(entrada, carpeta_graficos(), c["pie"], **opciones)
    st.image(str(ruta), width="stretch")
    with st.expander("Ver los datos del gráfico"):
        tabla(datos)


def aviso_no_calculable(datos):
    st.info(f"{NO_CALCULABLE}: {datos['motivo'].iloc[0]}", icon=":material/info:")


def kpis_por_codigo(tabla_kpis):
    return {fila["codigo"]: fila for fila in tabla_kpis.to_dict("records")}


# ---------------------------------------------------------------------
# Pestanas
# ---------------------------------------------------------------------

def sin_cifras():
    st.error("No se publican cifras: los datos actuales no son válidos (o no se pueden leer). "
             "El detalle está en la pestaña Calidad.", icon=":material/block:")


def pestana_direccion(c):
    tablas = c["tablas"]
    k = kpis_por_codigo(tablas["kpis"])
    st.subheader("Indicadores principales")
    alcance(c)
    st.caption(c["denominador"])
    fila = st.columns(4)
    tarjeta(fila[0], k["K01"])
    tarjeta(fila[1], k["K02"])
    tarjeta(fila[2], k["K04"])
    tarjeta(fila[3], k["K07"])
    fila = st.columns(4)
    tarjeta(fila[0], k["K09"])
    tarjeta(fila[1], k["K08"])
    tarjeta(fila[2], k["K03"])
    meses = tablas["ventas_por_periodo"]
    if no_calculable(meses):
        fila[3].metric("Importe del último mes", "N/D", border=True, help=meses["motivo"].iloc[0])
    else:
        ultimo = meses.iloc[-1]
        delta = None
        if len(meses) >= 2 and pd.notna(ultimo["variacion_importe_pct"]):
            delta = f"{numero(ultimo['variacion_importe_pct'], 1)} % frente a {meses.iloc[-2]['anio_mes']}"
        fila[3].metric(f"Importe confirmado {ultimo['anio_mes']}", f"{numero(ultimo['importe'], 2)} €", delta=delta,
                       border=True, help="Comparación con el mes anterior (ventas_por_periodo). Si el periodo "
                                         "filtrado corta un mes, ese mes está incompleto.")

    st.subheader("Evolución mensual")
    izquierda, derecha = st.columns(2)
    with izquierda:
        grafico(visualizaciones.grafico_evolucion, tablas["pedidos_unicos"], tablas["matriz_modelo_mes"], c)
    with derecha:
        st.markdown("**Importe confirmado por mes (€)**")
        if no_calculable(meses):
            aviso_no_calculable(meses)
        else:
            st.line_chart(meses, x="anio_mes", y="importe", x_label="Mes del pedido", y_label="Importe confirmado (€)")
            st.caption("Pedidos confirmados en adelante (criterio de venta). Importes con IVA "
                       f"{config.IVA}. Un mes sin ventas dentro del periodo sale con 0.")
        with st.expander("Ver los datos del gráfico"):
            tabla(meses)
        descarga(meses, "ventas_por_periodo", c)

    st.subheader("Estado de los pedidos y de los pagos")
    izquierda, derecha = st.columns(2)
    with izquierda:
        grafico(visualizaciones.grafico_pedidos_por_estado, tablas["pedidos_por_estado"], tablas["pedidos_por_estado"], c)
    with derecha:
        st.markdown("**Pedidos por estado de pago**")
        tabla(tablas["pedidos_por_estado_pago"])
        st.caption("Es lo que Acceso a Datos marca como pagado: no es un cobro comprobado.")
        st.markdown("**Pedidos por estado**")
        tabla(tablas["pedidos_por_estado"])
        descarga(tablas["pedidos_unicos"], "pedidos_unicos", c)

    st.subheader("Conclusiones para dirección")
    alcance(c, filtrado=False)
    st.caption("Cada conclusión dice de dónde sale. Ninguna simulación es un resultado comercial real.")
    for fila in c["publicado"]["informe"].to_dict("records"):
        with st.container(border=True):
            st.markdown(f"**{fila['numero']}. {fila['titulo']}**")
            color = "blue" if fila["procede_de"].startswith("Predicción") else COLOR_ORIGEN.get(c["publicado"]["tipo"], "gray")
            st.badge(fila["procede_de"], color=color)
            st.markdown(f"**Evidencia.** {fila['evidencia']}  \n**Interpretación.** {fila['interpretacion']}  \n"
                        f"**Decisión.** {fila['decision']}  \n**Limitación.** {fila['limitacion']}")


def pestana_productos(c):
    tablas = c["tablas"]
    abc = tablas["modelos_abc"]
    st.subheader("Ranking de modelos y clasificación ABC")
    alcance(c)
    izquierda, derecha = st.columns(2)
    with izquierda:
        tabla(abc[["ranking_pares", "nombre_modelo", "pares", "pedidos", "importe", "peso_pct", "acumulado_pct",
                   "clase_abc"]])
        st.caption(f"Clase A hasta el {config.ABC_LIMITE_A} % de los pares acumulados, B hasta el "
                   f"{config.ABC_LIMITE_B} %, C el resto. Pares de pedidos no cancelados.")
        descarga(abc, "modelos_abc", c)
    with derecha:
        grafico(visualizaciones.grafico_pareto_modelos, abc, abc, c)

    st.subheader("Tallas")
    izquierda, derecha = st.columns(2)
    with izquierda:
        grafico(visualizaciones.grafico_pares_por_talla, tablas["ventas_por_talla"], tablas["ventas_por_talla"], c)
    with derecha:
        grafico(visualizaciones.grafico_matriz_modelo_talla, tablas["matriz_modelo_talla"],
                tablas["matriz_modelo_talla"], c)
        descarga(tablas["matriz_modelo_talla"], "matriz_modelo_talla", c)

    st.subheader("Custom frente a estándar")
    izquierda, derecha = st.columns(2)
    with izquierda:
        grafico(visualizaciones.grafico_custom_vs_estandar, tablas["custom_vs_estandar"],
                tablas["custom_vs_estandar"], c)
    with derecha:
        datos = tablas["pedidos_unicos"][["referencia", "tipo_pedido", "estado_pedido", "pares", "importe"]]
        grafico(visualizaciones.grafico_importe_por_tipo, tablas["pedidos_unicos"], datos, c)
    tabla(tablas["custom_vs_estandar"])


def pestana_clientes(c):
    tablas = c["tablas"]
    segmentos = c["publicado"]["segmentacion"]
    st.subheader("Actividad y ranking de clientes")
    alcance(c)
    st.caption("Solo el id y el tipo de cliente: el nombre no hace falta para analizar.")
    izquierda, derecha = st.columns(2)
    with izquierda:
        tabla(tablas["clientes_actividad"], alto=420)
        descarga(tablas["clientes_actividad"], "clientes_actividad", c)
    with derecha:
        grafico(visualizaciones.grafico_clientes_por_importe, tablas["clientes_actividad"],
                tablas["clientes_actividad"], c)

    st.subheader("Segmentación RFM")
    alcance(c, filtrado=False)
    st.caption("RFM se calcula siempre con todos los pedidos de venta hasta la fecha de corte: con un periodo o un "
               "modelo filtrado, la recencia y los quintiles cambiarían de significado.")
    resumen = segmentos["rfm_segmentos"]
    rfm = segmentos["rfm_clientes"]
    compradores = rfm[rfm["frequency"] > 0]
    segmentable = len(compradores) >= config.MINIMO_CLIENTES_RFM   # el mismo minimo que segmentacion.py
    if not segmentable:
        st.info(f"{NO_CALCULABLE}: hay {len(compradores)} cliente(s) con compras válidas y hacen falta al menos "
                f"{config.MINIMO_CLIENTES_RFM}. No se reparten segmentos ni se inventa actividad.",
                icon=":material/info:")
    izquierda, derecha = st.columns(2)
    with izquierda:
        tabla(resumen[["segmento", "clientes", "porcentaje_clientes", "recency_media_dias", "frequency_media",
                       "monetary_total", "porcentaje_importe", "significado_y_uso"]])
        descarga(rfm, "rfm_clientes", c, filtrado=False)
    with derecha:
        if segmentable:
            st.markdown("**Clientes por recencia e importe**")
            st.scatter_chart(compradores, x="recency_dias", y="monetary", color="segmento",
                             x_label="Días desde la última compra", y_label="Importe vendido (€)")
            st.caption("Cada punto es un cliente con compras. A la izquierda, los que compraron hace poco; "
                       "arriba, los de más importe. El color es su segmento RFM.")
            with st.expander("Ver los datos del gráfico"):
                tabla(compradores)

    st.subheader("Grupos de KMeans")
    alcance(c, filtrado=False)
    clusters = segmentos["kmeans_clusters"]
    if no_calculable(clusters):
        aviso_no_calculable(clusters)
    else:
        seleccion = segmentos["kmeans_seleccion_k"]
        elegido = seleccion[seleccion["elegido"]].iloc[0]
        st.caption(f"Se probó k = 2 a 5 y se eligió k = {int(elegido['k'])}, el de mayor silhouette "
                   f"({numero(elegido['silhouette'], 3)}). Son grupos matemáticos: se comparan con RFM, pero no son "
                   "categorías comerciales ni perfiles reales de clientes.")
        izquierda, derecha = st.columns([1, 2])
        with izquierda:
            tabla(seleccion)
        with derecha:
            tabla(clusters)
        st.markdown("**Segmentos RFM frente a grupos de KMeans** (clientes en cada cruce)")
        tabla(segmentos["rfm_frente_a_kmeans"])

    st.subheader("Cohortes de compra")
    alcance(c)
    cohortes = tablas["cohortes"]
    if no_calculable(cohortes):
        aviso_no_calculable(cohortes)
    else:
        st.caption("Cada fila es el mes de la primera compra; cada columna, la parte de esos clientes que vuelve a "
                   "comprar N meses después (1,0 = todos).")
        tabla(cohortes)


def pestana_inventario(c):
    publicado = c["publicado"]
    st.info(f"El stock es una foto en la fecha de corte ({publicado['corte']:%d/%m/%Y %H:%M}), no un histórico. "
            "Aquí solo se aplican los filtros de modelo y talla; la demanda es siempre la de los "
            f"{config.DIAS_DEMANDA} días anteriores al corte (pedidos no cancelados).", icon=":material/inventory_2:")
    if "umbral" not in st.session_state:
        st.session_state["umbral"] = config.UMBRAL_STOCK_BAJO
    umbral = st.number_input("Umbral de stock bajo: alerta con menos de estos pares", min_value=1, max_value=1000,
                             step=1, key="umbral")
    stock, bajo = filtros.tablas_inventario(publicado["validos"], publicado["tablas"], publicado["corte"],
                                            c["filtros"], umbral)
    cobertura = kpis.cobertura_total(stock)
    con_demanda = bajo[bajo["demanda_28d"] > 0]
    # La unidad va en el titulo: asi el numero cabe en la tarjeta
    fila = st.columns(5)
    fila[0].metric("Stock total (pares)", numero(stock["stock_disponible"].sum()), border=True)
    fila[1].metric("Referencias (SKU)", numero(len(stock)), border=True)
    fila[2].metric("SKU bajo el umbral", numero(len(bajo)), border=True,
                   help=f"Referencias con menos de {umbral} pares")
    fila[3].metric("Bajo umbral y pedidos", numero(len(con_demanda)), border=True,
                   help=f"SKU bajo el umbral que se han pedido en los últimos {config.DIAS_DEMANDA} días: "
                        "los primeros que se pueden agotar")
    fila[4].metric("Cobertura (semanas)", texto_kpi(cobertura).replace(" semanas", ""), border=True,
                   help=f"{cobertura['formula']}. {cobertura['detalle']}")

    st.subheader("Stock por modelo y color")
    if len(stock) > 0:
        # Una columna por color de zapatilla: asi cada tramo se pinta con su color
        por_modelo = stock.pivot_table(index="nombre_modelo", columns="color", values="stock_disponible",
                                       aggfunc="sum", fill_value=0)
        colores = list(por_modelo.columns)
        st.bar_chart(por_modelo, y=colores, color=[COLOR_PRODUCTO.get(color, "#9e9e9e") for color in colores],
                     stack=True, x_label="Modelo", y_label="Pares en stock")
        st.caption("Pares en stock de cada modelo, sumando sus tallas; cada tramo es un color de zapatilla. El "
                   "detalle por talla está en la tabla de abajo.")
        with st.expander("Ver los datos del gráfico"):
            tabla(por_modelo)

    st.subheader(f"Alertas: referencias con menos de {umbral} pares")
    if len(bajo) == 0:
        st.success("Ninguna referencia por debajo del umbral.", icon=":material/check_circle:")
    else:
        tabla(bajo[["sku", "nombre_modelo", "color", "talla", "stock_disponible", "demanda_28d", "semanas_cobertura",
                    "estado_cobertura"]])
        descarga(bajo, "stock_bajo", c)

    st.subheader("Demanda y existencias por referencia")
    izquierda, derecha = st.columns(2)
    with izquierda:
        grafico(visualizaciones.grafico_stock, stock, stock, c, umbral=umbral)
    with derecha:
        tabla(stock[["sku", "nombre_modelo", "color", "talla", "stock_disponible", "demanda_28d", "semanas_cobertura",
                     "estado_cobertura"]], alto=420)
        st.caption("Cobertura = stock / (pares de 28 días / 4), en semanas. Sin demanda en 28 días: N/D. Si la "
                   "exportación no cubre 28 días de pedidos, no se calcula.")
        descarga(stock, "stock_variantes", c)


def pestana_calidad(c):
    estado = c["estado"]
    resultado = estado["calidad"]
    if resultado is None:
        st.error(f"{estado['estado']}: {estado['mensaje']}", icon=":material/error:")
        return
    incidencias = resultado["incidencias"]
    gravedades = incidencias["gravedad"].value_counts()
    if resultado["bloqueado"]:
        st.error(f"BLOQUEADO: {estado['mensaje']}", icon=":material/block:")
    elif len(incidencias) > 0:
        st.warning(f"Datos publicados con {len(incidencias)} incidencias no bloqueantes: las filas afectadas se han "
                   "apartado o solo se avisan.", icon=":material/warning:")
    else:
        st.success("Calidad correcta: los cinco CSV pasan las 12 reglas sin ninguna incidencia.",
                   icon=":material/check_circle:")

    leidas = sum(len(datos) for datos in resultado["datos"].values())
    validas = sum(len(datos) for datos in resultado["validos"].values())
    fila = st.columns(4)
    fila[0].metric("Última comprobación", f"{estado['comprobado']:%H:%M:%S}", border=True,
                   help=f"{estado['comprobado']:{FORMATO_HORA}}")
    fila[1].metric("Filas recibidas", numero(leidas), border=True)
    fila[2].metric("Filas válidas", numero(validas), border=True)
    fila[3].metric("Filas rechazadas", numero(len(resultado["rechazadas"])), border=True)
    fila = st.columns(4)
    fila[0].metric("Bloqueantes", int(gravedades.get("bloqueante", 0)), border=True,
                   help="Paran todo: no se publica ninguna cifra")
    fila[1].metric("Recuperables", int(gravedades.get("recuperable", 0)), border=True,
                   help="Se aparta la fila (y su pedido entero)")
    fila[2].metric("Advertencias", int(gravedades.get("advertencia", 0)), border=True,
                   help="Se mantiene la fila y se avisa")
    fila[3].metric("Tiempo de procesamiento", f"{numero(estado['duracion'], 2)} s", border=True)

    st.subheader("Calidad por tabla")
    tabla(resultado["resumen"])
    if len(incidencias) > 0:
        st.subheader("Tablas y columnas afectadas")
        afectadas = incidencias.groupby(["tabla", "columna", "gravedad"]).size().reset_index(name="incidencias")
        tabla(afectadas)
        st.subheader("Incidencias")
        tabla(incidencias)
        st.download_button("Descargar incidencias.csv",
                           pipeline.csv_descarga(incidencias, estado["origen"],
                                                 f"{estado['comprobado']:%Y-%m-%d %H:%M:%S}", "ninguno"),
                           file_name=f"incidencias_{estado['tipo'].lower()}.csv", mime="text/csv",
                           key="descarga_incidencias", icon=":material/download:")
    if len(resultado["rechazadas"]) > 0:
        st.subheader("Filas rechazadas")
        tabla(resultado["rechazadas"])

    st.subheader("Origen de los archivos")
    st.caption(f"Carpeta: {actualizacion.carpeta_relativa(estado['carpeta'])} · versión de los datos "
               f"{estado['version']} (huella del contenido: solo cambia si cambian los datos, no la fecha).")
    tabla(estado["archivos"])
    st.code(pipeline.leer_origen(estado["carpeta"]), language=None)
    for aviso in estado["avisos"] + resultado["avisos"]:
        st.warning(aviso, icon=":material/warning:")

    st.subheader("Conciliación con SQL (Acceso a Datos)")
    publicado = estado["publicado"]
    if publicado is None or estado["desactualizado"]:
        st.info("Sin datos válidos no se concilia.", icon=":material/info:")
    else:
        st.markdown(f"**{publicado['conciliacion']}**")
        if publicado["tabla_conciliacion"] is not None:
            tabla(publicado["tabla_conciliacion"][["consulta", "indicador", "clave", "valor_sql", "valor_python",
                                                   "diferencia", "resultado"]])

    st.subheader("Registro de eventos")
    st.caption(f"Un solo archivo ({actualizacion.carpeta_relativa(config.ARCHIVO_REGISTRO)}) con una fila por "
               "comprobación, actualización, cambio de origen o descarga. Las más recientes, primero.")
    tabla(registro.leer(config.ARCHIVO_REGISTRO, ultimas=50), alto=320)


def pestana_prediccion(c):
    publicado = c["publicado"]
    resultados = publicado["prediccion"]
    metricas = resultados["metricas_prediccion"]
    if publicado["tipo"] == "SINTETICO":
        st.warning("LABORATORIO · DATOS SINTÉTICOS. Demuestra el método de predicción y su evaluación; no es una "
                   "previsión de la demanda real de NOVA.", icon=":material/science:")
    alcance(c, filtrado=False)
    st.caption("La predicción usa siempre la serie completa de cada modelo: con meses filtrados, el entrenamiento y "
               "la evaluación por fecha dejarían de tener sentido.")
    if no_calculable(metricas):
        aviso_no_calculable(metricas)
        return
    por_metodo = metricas.set_index("metodo")
    baseline = por_metodo.loc["baseline"]
    regresion = por_metodo.loc["regresion"]
    fila = st.columns(4)
    fila[0].metric("MAE baseline", f"{numero(baseline['mae'], 2)} pares", border=True,
                   help="Error absoluto medio de repetir el mes anterior")
    fila[1].metric("RMSE baseline", f"{numero(baseline['rmse'], 2)} pares", border=True,
                   help="Como el MAE, pero los errores grandes pesan más")
    fila[2].metric("MAE regresión", f"{numero(regresion['mae'], 2)} pares", border=True, delta_color="inverse",
                   delta=f"{numero(regresion['mae'] - baseline['mae'], 2)} frente al baseline")
    fila[3].metric("RMSE regresión", f"{numero(regresion['rmse'], 2)} pares", border=True, delta_color="inverse",
                   delta=f"{numero(regresion['rmse'] - baseline['rmse'], 2)} frente al baseline")
    st.markdown(f"**¿Mejora la regresión al baseline?** {regresion['mejora_al_baseline']}.")
    st.caption(f"Entrenamiento {baseline['periodo_entrenamiento']} · evaluación {baseline['periodo_evaluacion']} "
               "(los 3 últimos meses, separados por fecha). Solo cuenta como mejora si baja el MAE y el RMSE.")

    izquierda, derecha = st.columns(2)
    with izquierda:
        grafico(visualizaciones.grafico_real_frente_a_prediccion, resultados["predicciones"],
                resultados["predicciones"], c)
    with derecha:
        st.markdown("**Error de cada método por modelo**")
        tabla(resultados["errores_por_modelo"])
    st.markdown("**Predicciones de los meses de evaluación**")
    tabla(resultados["predicciones"])
    descarga(resultados["predicciones"], "predicciones", c, filtrado=False)
    with st.expander("Coeficientes de la regresión"):
        tabla(resultados["coeficientes_regresion"])


# ---------------------------------------------------------------------
# Cabecera y panel (se refresca cada 60 s)
# ---------------------------------------------------------------------

def cabecera(estado):
    st.title("NOVA Sneakers · Panel de datos")
    st.badge(estado["origen"], icon=":material/database:", color=COLOR_ORIGEN.get(estado["tipo"], "red"))
    if estado["tipo"] == "SINTETICO":
        st.warning("Datos SINTÉTICOS generados por Python: no son ventas ni clientes reales de NOVA.",
                   icon=":material/science:")
    elif estado["tipo"] == "PRUEBA":
        st.info("Exportación de PRUEBA de PostgreSQL: sirve para comprobar el sistema; no son ventas reales.",
                icon=":material/info:")
    publicado = estado["publicado"]
    fila = st.columns([1.3, 1, 1.3, 0.8])
    fila[0].metric("Estado", estado["estado"].capitalize(), border=True, help=estado["mensaje"])
    # En la tarjeta, la hora; la fecha completa, en la linea de debajo
    fila[1].metric("Última comprobación", f"{estado['comprobado']:%H:%M:%S}", border=True,
                   help=f"Se vuelve a comprobar cada {config.SEGUNDOS_REFRESCO} s mientras la página está abierta")
    fila[2].metric("Última actualización válida", f"{publicado['actualizado']:%H:%M:%S}" if publicado else "Ninguna",
                   border=True, help="Momento en que se cargaron por primera vez los datos que se están mostrando")
    filas_validas = numero(publicado["filas_validas"]) if publicado else "0"
    fila[3].metric("Filas válidas", filas_validas, border=True, help="Suma de las filas válidas de los cinco CSV")
    corte = f"{publicado['corte']:%d/%m/%Y %H:%M}" if publicado else "-"
    actualizado = f"{publicado['actualizado']:{FORMATO_HORA}}" if publicado else "ninguna"
    st.caption(f"Última comprobación: {estado['comprobado']:{FORMATO_HORA}} · última actualización válida: "
               f"{actualizado} · fecha de corte: {corte} · versión de los datos: {estado['version']} · procesado en "
               f"{numero(estado['duracion'], 2)} s · próxima comprobación automática en {config.SEGUNDOS_REFRESCO} s")
    if estado["estado"] in (actualizacion.DATOS_INVALIDOS, actualizacion.ERROR_CARGA):
        st.error(f"{estado['estado']}: {estado['mensaje']}", icon=":material/error:")
    for aviso in estado["avisos"]:
        st.warning(aviso, icon=":material/warning:")


def publicacion_visible(estado):
    """
    Lo publicado que se puede ensenar. Si los datos actuales no son validos,
    no se ensena ninguna cifra, salvo que se pida ver el ultimo resultado
    valido, que entonces sale rotulado como DESACTUALIZADO.
    """
    publicado = estado["publicado"]
    if publicado is None or not estado["desactualizado"]:
        return publicado
    hora = f"{publicado['actualizado']:{FORMATO_HORA}}"
    if st.toggle(f"Ver el último resultado válido ({hora}), marcado como DESACTUALIZADO", key="ver_desactualizado"):
        st.error(f"DESACTUALIZADO: estas cifras son de la exportación válida del {hora}, no de los CSV actuales.",
                 icon=":material/history:")
        return publicado
    return None


@st.fragment(run_every=f"{config.SEGUNDOS_REFRESCO}s")
def panel(nombre, elegidos):
    """Todo lo que se refresca solo: cabecera de estado y pestanas."""
    version = st.session_state["estados"][nombre]["version"]
    if actualizar(nombre) and st.session_state["estados"][nombre]["version"] != version:
        st.rerun()   # exportacion nueva: se redibuja toda la pagina, tambien las opciones de los filtros
    estado = st.session_state["estados"][nombre]
    cabecera(estado)
    publicado = publicacion_visible(estado)

    c = {"estado": estado, "publicado": publicado, "filtros": elegidos, "texto_filtros": filtros.describir(elegidos),
         "tablas": None}
    if publicado is not None:
        c["ejecucion"] = f"{publicado['actualizado']:%Y-%m-%d %H:%M:%S} (versión {publicado['version']})"
        c["pie"] = (f"Origen: {estado['origen']} · Corte: {publicado['corte']:%Y-%m-%d %H:%M} · Datos: {c['ejecucion']}"
                    f" · Filtros: {c['texto_filtros']} · IVA {config.IVA}")

    pestanas = st.tabs(PESTANAS, key="pestana", bind="query-params")
    abierta = next((nombre_pestana for nombre_pestana, pestana in zip(PESTANAS, pestanas) if pestana.open), PESTANAS[0])
    if publicado is not None and abierta in ["Dirección", "Productos", "Clientes"]:
        # Las tablas filtradas salen de la MISMA version de los datos que todo lo demas
        c["tablas"] = filtros.calcular_filtrado(publicado["datos"], publicado["validos"], elegidos)
        total = len(publicado["tablas"]["pedidos_unicos"])
        if filtros.hay_filtros(elegidos):
            c["denominador"] = (f"{len(c['tablas']['pedidos_unicos'])} de {total} pedidos registrados cumplen los "
                                "filtros. Cada KPI se calcula solo con ellos (los de venta, con los confirmados de "
                                "ese subconjunto); con filtro de modelo o talla, cada pedido aporta solo esas líneas.")
        else:
            c["denominador"] = f"Sin filtros: los {total} pedidos registrados de la exportación."

    funciones = [pestana_direccion, pestana_productos, pestana_clientes, pestana_inventario, pestana_calidad,
                 pestana_prediccion]
    for nombre_pestana, pestana, funcion in zip(PESTANAS, pestanas, funciones):
        if nombre_pestana != abierta:
            continue   # solo se calcula y se dibuja la pestana abierta
        with pestana:
            if publicado is None and funcion is not pestana_calidad:
                sin_cifras()
            else:
                funcion(c)


def main():
    st.set_page_config(page_title="NOVA Sneakers · Dashboard", page_icon="👟", layout="wide")
    with st.sidebar:
        st.header("NOVA Sneakers")
        nombre = st.selectbox("Origen de los datos", list(ORIGENES), format_func=lambda clave: ORIGENES[clave][0],
                              key="origen", bind="query-params",
                              help="Exportación ACC: entrada_acc/ (CSV de PostgreSQL). Sintéticos: "
                                   "datos_sinteticos/limpios/ y datos_sinteticos/con_errores/. Cada origen se lee de "
                                   "su carpeta y nunca se mezcla con los demás.")
        manual = st.button("Actualizar ahora", icon=":material/refresh:", width="stretch", type="primary")
    actualizar(nombre, "actualización manual" if manual else None)
    with st.sidebar:
        elegidos = elegir_filtros(nombre, st.session_state["estados"][nombre])
        st.divider()
        st.caption(f"Se vuelven a leer y validar los CSV cada {config.SEGUNDOS_REFRESCO} s. Los datos nuevos de "
                   "PostgreSQL solo aparecen cuando Acceso a Datos vuelve a exportar los CSV.")
    panel(nombre, elegidos)


if __name__ == "__main__":
    main()
