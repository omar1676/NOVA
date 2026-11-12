"""
Graficos de NOVA (apartado 6.6): figuras PNG hechas con Matplotlib.

Cada grafico responde a una pregunta de negocio y se dibuja a partir de un
DataFrame de analiticas.py: nunca con cifras escritas a mano. Lleva titulo
(la pregunta), subtitulo (que datos usa), ejes con unidades, leyenda cuando
hace falta y un pie con el origen, la fecha de corte, el momento del calculo
y los filtros. Si no hay datos, el grafico lo dice en vez de fallar.

No usa Streamlit: el dashboard (app_dashboard.py) usa estas mismas funciones.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")   # dibuja directamente en archivos, sin abrir ventanas
import matplotlib.dates as mdates   # noqa: E402  (tiene que ir despues de elegir "Agg")
import matplotlib.pyplot as plt   # noqa: E402
import numpy as np   # noqa: E402
import pandas as pd   # noqa: E402
from matplotlib.patches import Patch   # noqa: E402

import config   # noqa: E402
from analiticas import de_demanda, es_no_calculable, rellenar_meses   # noqa: E402

AZUL = "#1f5fa8"
GRIS = "#9e9e9e"
NARANJA = "#e07b00"
COLOR_CLASE = {"A": "#2e7d32", "B": "#f9a825", "C": GRIS}
COLOR_TIPO = {"normal": AZUL, "custom": NARANJA}
MAXIMO_CLIENTES = 15   # en el ranking de clientes; con mas barras no se lee

# Lo que responde cada grafico (para la consola y la documentacion)
GRAFICOS = [
    ("01_pedidos_por_estado.png", "barras", "¿En qué estado están los pedidos?"),
    ("02_pareto_modelos.png", "Pareto", "¿Qué modelos concentran la demanda? (ABC)"),
    ("03_pares_por_talla.png", "barras", "¿Qué tallas se piden más?"),
    ("04_evolucion_demanda.png", "serie temporal", "¿Cómo evoluciona la demanda en el tiempo?"),
    ("05_matriz_modelo_talla.png", "mapa de calor", "¿Qué tallas se piden de cada modelo?"),
    ("06_custom_vs_estandar.png", "comparativa por segmento", "¿Cuánto pesan los pedidos Custom?"),
    ("07_clientes_por_importe.png", "ranking", "¿Qué clientes concentran el importe?"),
    ("08_stock_por_sku.png", "histograma", "¿Cuántas referencias tienen poco stock?"),
    ("09_importe_por_tipo.png", "diagrama de caja", "¿Cuánto vale un pedido según su tipo?"),
    ("10_pares_frente_a_importe.png", "dispersión", "¿El importe crece con los pares? ¿Hay pedidos raros?"),
]


def nueva_figura(pregunta, subtitulo):
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.suptitle(pregunta, fontsize=13, fontweight="bold", x=0.02, ha="left")
    ax.set_title(subtitulo, fontsize=9.5, loc="left", color="#444444")
    return fig, ax


def guardar(fig, carpeta, archivo, pie):
    fig.text(0.02, 0.012, pie, fontsize=7.5, color="#555555", ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    ruta = Path(carpeta) / archivo
    fig.savefig(ruta, dpi=110)
    plt.close(fig)
    return ruta


def sin_datos(ax, mensaje="Sin datos para este gráfico"):
    ax.text(0.5, 0.5, mensaje, ha="center", va="center", fontsize=12, transform=ax.transAxes)
    ax.set_xticks([])
    ax.set_yticks([])


def grafico_pedidos_por_estado(tabla, carpeta, pie):
    fig, ax = nueva_figura("¿En qué estado están los pedidos?",
                           "Pedidos registrados en cada estado del catálogo (también los que tienen 0)")
    if tabla["pedidos"].sum() == 0:
        sin_datos(ax)
    else:
        colores = [AZUL if venta else GRIS for venta in tabla["cuenta_como_venta"]]
        barras = ax.bar(tabla["estado_pedido"], tabla["pedidos"], color=colores)
        ax.bar_label(barras)
        ax.set_xlabel("Estado del pedido")
        ax.set_ylabel("Pedidos (nº)")
        ax.legend(handles=[Patch(color=AZUL, label="cuenta como venta (confirmado en adelante)"),
                           Patch(color=GRIS, label="no cuenta como venta")])
    return guardar(fig, carpeta, GRAFICOS[0][0], pie)


def grafico_pareto_modelos(tabla_abc, carpeta, pie):
    fig, ax = nueva_figura("¿Qué modelos concentran la demanda? (Pareto y clasificación ABC)",
                           "Pares de demanda por modelo (pedidos no cancelados) y % acumulado. "
                           f"A hasta el {config.ABC_LIMITE_A} %, B hasta el {config.ABC_LIMITE_B} %")
    if tabla_abc["pares"].sum() == 0:
        sin_datos(ax)
    else:
        colores = [COLOR_CLASE[clase] for clase in tabla_abc["clase_abc"]]
        barras = ax.bar(tabla_abc["nombre_modelo"], tabla_abc["pares"], color=colores)
        ax.bar_label(barras)
        ax.set_xlabel("Modelo")
        ax.set_ylabel("Pares (nº)")
        ax.tick_params(axis="x", rotation=20)
        acumulado = ax.twinx()
        acumulado.plot(tabla_abc["nombre_modelo"], tabla_abc["acumulado_pct"].astype(float),
                       color="black", marker="o", label="% acumulado")
        acumulado.axhline(config.ABC_LIMITE_A, color="black", linestyle="--", linewidth=0.8)
        acumulado.axhline(config.ABC_LIMITE_B, color="black", linestyle=":", linewidth=0.8)
        acumulado.set_ylim(0, 105)
        acumulado.set_ylabel("% acumulado de pares")
        # Leyenda: un cuadro por clase y una linea por cada marca del eje de la derecha
        leyenda = []
        for clase in "ABC":
            leyenda.append(Patch(color=COLOR_CLASE[clase], label=f"clase {clase}"))
        leyenda.append(plt.Line2D([], [], color="black", marker="o", label="% acumulado"))
        leyenda.append(plt.Line2D([], [], color="black", linestyle="--", label=f"límite A ({config.ABC_LIMITE_A} %)"))
        leyenda.append(plt.Line2D([], [], color="black", linestyle=":", label=f"límite B ({config.ABC_LIMITE_B} %)"))
        ax.legend(handles=leyenda, loc="center right")
    return guardar(fig, carpeta, GRAFICOS[1][0], pie)


def grafico_pares_por_talla(tabla_tallas, carpeta, pie):
    fig, ax = nueva_figura("¿Qué tallas se piden más?", "Pares de demanda por talla (pedidos no cancelados)")
    if len(tabla_tallas) == 0:
        sin_datos(ax)
    else:
        barras = ax.bar(tabla_tallas["talla"].astype(str), tabla_tallas["pares"], color=AZUL)
        etiquetas = []
        for pares, peso in zip(tabla_tallas["pares"], tabla_tallas["peso_pct"]):
            etiquetas.append(f"{pares} ({peso} %)")
        ax.bar_label(barras, labels=etiquetas)
        ax.set_xlabel("Talla (EU)")
        ax.set_ylabel("Pares (nº)")
    return guardar(fig, carpeta, GRAFICOS[2][0], pie)


def grafico_evolucion(pedidos, carpeta, pie):
    demanda = de_demanda(pedidos)
    meses = demanda["fecha_pedido"].dt.to_period("M")
    if meses.nunique() >= 2:
        # Con varios meses, por mes: por dia seria una nube de puntos ilegible
        fig, ax = nueva_figura("¿Cómo evoluciona la demanda en el tiempo?",
                               "Pares de demanda por mes (pedidos no cancelados). Un mes sin pedidos dentro del periodo sale con 0")
        por_mes = demanda.groupby(meses)["pares"].sum()
        por_mes = rellenar_meses(por_mes)
        etiquetas = [str(mes) for mes in por_mes.index]
        ax.plot(etiquetas, por_mes.values, color=AZUL, marker="o")
        for etiqueta, pares in zip(etiquetas, por_mes.values):
            ax.annotate(f"{pares}", (etiqueta, pares), xytext=(0, 6), textcoords="offset points", ha="center", fontsize=8)
        ax.set_xlabel("Mes del pedido")
        ax.set_ylabel("Pares (nº)")
        ax.set_ylim(0, por_mes.max() * 1.2)
        ax.tick_params(axis="x", rotation=45)
        return guardar(fig, carpeta, GRAFICOS[3][0], pie)

    fig, ax = nueva_figura("¿Cómo evoluciona la demanda en el tiempo?",
                           "Pares de demanda por día del pedido (pedidos no cancelados)")
    if len(demanda) == 0:
        sin_datos(ax)
    else:
        por_dia = demanda.groupby(demanda["fecha_pedido"].dt.normalize())["pares"].sum()
        ax.plot(por_dia.index, por_dia.values, color=AZUL, marker="o")
        for dia, pares in por_dia.items():
            ax.annotate(f"{pares} pares", (dia, pares), xytext=(0, 6), textcoords="offset points", ha="center")
        ax.set_xlabel("Día del pedido")
        ax.set_ylabel("Pares (nº)")
        ax.set_ylim(0, por_dia.max() * 1.25)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        if len(por_dia) == 1:
            # Con un solo dia, el eje enseña solo ese dia (y tres a cada lado):
            # si no, Matplotlib dibujaria varios anos que no tienen datos
            dia = por_dia.index[0]
            ax.set_xlim(dia - pd.Timedelta(days=3), dia + pd.Timedelta(days=3))
            ax.xaxis.set_major_locator(mdates.DayLocator())
            ax.text(0.5, 0.4, f"Solo hay pedidos de 1 día ({dia:%Y-%m-%d}): no hay evolución que mostrar",
                    transform=ax.transAxes, ha="center", fontsize=11,
                    bbox={"facecolor": "#fff3cd", "edgecolor": NARANJA})
        fig.autofmt_xdate()
    return guardar(fig, carpeta, GRAFICOS[3][0], pie)


def grafico_matriz_modelo_talla(matriz, carpeta, pie):
    fig, ax = nueva_figura("¿Qué tallas se piden de cada modelo?",
                           "Pares de demanda por modelo y talla (pedidos no cancelados)")
    if len(matriz) == 0:
        sin_datos(ax)
    else:
        valores = matriz.to_numpy(dtype=float)
        imagen = ax.imshow(valores, cmap="Blues", aspect="auto")
        ax.set_xticks(range(len(matriz.columns)), [str(talla) for talla in matriz.columns])
        ax.set_yticks(range(len(matriz.index)), matriz.index)
        for fila in range(valores.shape[0]):
            for columna in range(valores.shape[1]):
                valor = valores[fila, columna]
                color = "white" if valor > valores.max() / 2 else "black"
                ax.text(columna, fila, f"{valor:.0f}", ha="center", va="center", color=color)
        fig.colorbar(imagen, ax=ax, label="Pares (nº)")
        ax.set_xlabel("Talla (EU)")
        ax.set_ylabel("Modelo")
    return guardar(fig, carpeta, GRAFICOS[4][0], pie)


def grafico_custom_vs_estandar(tabla, carpeta, pie):
    fig, ax = nueva_figura("¿Cuánto pesan los pedidos Custom?",
                           "Parte de la demanda (pedidos no cancelados) de cada tipo: en pedidos, en pares y en euros")
    cuotas = tabla.set_index("tipo_pedido")[["cuota_pedidos_pct", "cuota_pares_pct", "cuota_importe_pct"]]
    cuotas = cuotas.astype(float)
    if cuotas.isna().all().all():
        sin_datos(ax)
    else:
        posiciones = np.arange(3)
        ancho = 0.38
        # Una barra por tipo en cada grupo, desplazada media barra a cada lado
        for numero, tipo in enumerate(cuotas.index):
            barras = ax.bar(posiciones + (numero - 0.5) * ancho, cuotas.loc[tipo].fillna(0), ancho,
                            label=tipo, color=COLOR_TIPO.get(tipo, GRIS))
            ax.bar_label(barras, fmt="%.1f %%")
        ax.set_xticks(posiciones, ["% de los pedidos", "% de los pares", "% del importe"])
        ax.set_ylabel("% de la demanda")
        ax.set_ylim(0, 110)
        ax.legend(title="Tipo de pedido")
    return guardar(fig, carpeta, GRAFICOS[5][0], pie)


def grafico_clientes_por_importe(tabla_clientes, carpeta, pie):
    cuantos = min(MAXIMO_CLIENTES, len(tabla_clientes))
    fig, ax = nueva_figura("¿Qué clientes concentran el importe?",
                           f"Los {cuantos} clientes con más importe de demanda, de {len(tabla_clientes)} "
                           "(no es dinero cobrado). Se muestra el id, no el nombre")
    if tabla_clientes["importe_demanda"].sum() == 0:
        sin_datos(ax)
    else:
        # Los que mas importe tienen, puestos de abajo arriba para que el primero quede arriba
        ordenada = tabla_clientes.sort_values(["importe_demanda", "id_cliente"], ascending=[False, True])
        ordenada = ordenada.head(MAXIMO_CLIENTES).iloc[::-1]
        etiquetas = "Cliente " + ordenada["id_cliente"] + " (" + ordenada["tipo_cliente"].fillna("?") + ")"
        colores = [NARANJA if tipo == "empresa" else AZUL for tipo in ordenada["tipo_cliente"]]
        barras = ax.barh(etiquetas, ordenada["importe_demanda"], color=colores)
        ax.bar_label(barras, fmt="%.2f €", padding=3)
        ax.set_xlabel(f"Importe de demanda (€, IVA {config.IVA})")
        ax.set_xlim(0, ordenada["importe_demanda"].max() * 1.2)
        ax.legend(handles=[Patch(color=NARANJA, label="empresa"), Patch(color=AZUL, label="particular")])
    return guardar(fig, carpeta, GRAFICOS[6][0], pie)


def grafico_stock(tabla_stock, carpeta, pie, umbral=config.UMBRAL_STOCK_BAJO):
    fig, ax = nueva_figura("¿Cuántas referencias tienen poco stock?",
                           "Stock de cada SKU (modelo + color + talla) en la fecha de corte: es una foto, no un histórico")
    if len(tabla_stock) == 0:
        sin_datos(ax)
    else:
        valores = tabla_stock["stock_disponible"].astype(float)
        # Bordes en los medios enteros (-0,5, 0,5...): una barra por cada numero de pares
        bordes = np.arange(0, valores.max() + 2) - 0.5
        ax.hist(valores, bins=bordes, color=AZUL)
        ax.axvline(umbral - 0.5, color="red", linestyle="--",
                   label=f"umbral de stock bajo: menos de {umbral} pares")
        bajos = int(tabla_stock["alerta_stock_bajo"].sum())
        ax.text(0.02, 0.9, f"{bajos} de {len(tabla_stock)} SKU por debajo del umbral", transform=ax.transAxes)
        ax.set_xlabel("Stock disponible por SKU (pares)")
        ax.set_ylabel("Referencias (nº de SKU)")
        ax.legend(loc="upper center")
    return guardar(fig, carpeta, GRAFICOS[7][0], pie)


def grafico_importe_por_tipo(pedidos, carpeta, pie):
    fig, ax = nueva_figura("¿Cuánto vale un pedido según su tipo?",
                           "Importe de cada pedido no cancelado según su tipo; cada punto es un pedido (escala logarítmica)")
    demanda = de_demanda(pedidos)
    # Los importes de cada tipo de pedido que tenga algun pedido
    grupos = []
    for tipo in config.TIPOS_PEDIDO:
        valores = demanda.loc[demanda["tipo_pedido"] == tipo, "importe"].astype(float)
        if len(valores) > 0:
            grupos.append((tipo, valores))
    if not grupos:
        sin_datos(ax)
    else:
        cajas = []
        etiquetas = []
        for tipo, valores in grupos:
            cajas.append(valores)
            etiquetas.append(f"{tipo} (n = {len(valores)})")
        ax.boxplot(cajas, tick_labels=etiquetas)
        for posicion, (tipo, valores) in enumerate(grupos, start=1):
            ax.scatter(np.full(len(valores), posicion), valores, color=COLOR_TIPO.get(tipo, GRIS), alpha=0.6, zorder=3)
        ax.set_yscale("log")
        ax.set_xlabel("Tipo de pedido")
        ax.set_ylabel("Importe del pedido (€, escala logarítmica)")
    return guardar(fig, carpeta, GRAFICOS[8][0], pie)


def grafico_pares_frente_a_importe(pedidos, carpeta, pie):
    fig, ax = nueva_figura("¿El importe crece con los pares? ¿Hay pedidos raros?",
                           "Cada punto es un pedido no cancelado; si es más grande, junta varios pedidos iguales. "
                           "Importe en escala logarítmica")
    demanda = de_demanda(pedidos)
    if len(demanda) == 0:
        sin_datos(ax)
    else:
        puntos = demanda.groupby(["tipo_pedido", "pares", "importe"]).size().reset_index(name="pedidos")
        for tipo, parte in puntos.groupby("tipo_pedido"):
            ax.scatter(parte["pares"], parte["importe"], s=60 * parte["pedidos"], alpha=0.7,
                       color=COLOR_TIPO.get(tipo, GRIS), label=tipo)
        ax.set_yscale("log")
        ax.set_xlabel("Pares del pedido")
        ax.set_ylabel("Importe del pedido (€, escala logarítmica)")
        ax.legend(title="Tipo de pedido")
    return guardar(fig, carpeta, GRAFICOS[9][0], pie)


# Fase 5: va aparte de los 10 anteriores (en graficos_prediccion/) porque es
# un resultado predictivo, no una descripcion de los datos
GRAFICO_PREDICCION = ("11_real_frente_a_prediccion.png", "dispersión", "¿Acierta la predicción de demanda?")


def grafico_real_frente_a_prediccion(predicciones, carpeta, pie):
    """Pares reales (eje x) frente a pares predichos (eje y) por los dos metodos, en los meses de evaluacion."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    if es_no_calculable(predicciones):
        fig, ax = nueva_figura(GRAFICO_PREDICCION[2], "Pares reales frente a pares predichos")
        # El motivo se recorta a 110 caracteres para que quepa en el grafico
        sin_datos(ax, f"No se puede predecir: {predicciones['motivo'].iloc[0]}"[:110])
        return guardar(fig, carpeta, GRAFICO_PREDICCION[0], pie)

    meses = sorted(predicciones["anio_mes"].unique())
    fig, ax = nueva_figura(GRAFICO_PREDICCION[2],
                           f"Cada punto es un modelo en un mes de evaluación ({meses[0]} a {meses[-1]}).\n"
                           "En la diagonal la predicción acierta; por encima se pasa y por debajo se queda corta")
    ax.scatter(predicciones["pares_reales"], predicciones["baseline"], color=GRIS, marker="o", s=45,
               alpha=0.8, label="A. baseline (pares del mes anterior)")
    ax.scatter(predicciones["pares_reales"], predicciones["regresion"], color=AZUL, marker="^", s=45,
               alpha=0.8, label="B. regresión lineal")
    maximo = max(predicciones["pares_reales"].max(), predicciones["baseline"].max(),
                 predicciones["regresion"].max()) * 1.05
    ax.plot([0, maximo], [0, maximo], color="#444444", linestyle="--", linewidth=1, label="predicción perfecta")
    ax.set_xlim(0, maximo)
    ax.set_ylim(0, maximo)
    ax.set_xlabel("Pares reales del modelo en el mes")
    ax.set_ylabel("Pares predichos")
    ax.legend(loc="upper left")
    return guardar(fig, carpeta, GRAFICO_PREDICCION[0], pie)


def generar_todos(tablas, carpeta, pie):
    """
    Dibuja los 10 graficos en la carpeta y devuelve la lista de rutas.
    `tablas` es un diccionario con los DataFrames de analiticas.py.
    """
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    return [
        grafico_pedidos_por_estado(tablas["pedidos_por_estado"], carpeta, pie),
        grafico_pareto_modelos(tablas["modelos_abc"], carpeta, pie),
        grafico_pares_por_talla(tablas["ventas_por_talla"], carpeta, pie),
        grafico_evolucion(tablas["pedidos_unicos"], carpeta, pie),
        grafico_matriz_modelo_talla(tablas["matriz_modelo_talla"], carpeta, pie),
        grafico_custom_vs_estandar(tablas["custom_vs_estandar"], carpeta, pie),
        grafico_clientes_por_importe(tablas["clientes_actividad"], carpeta, pie),
        grafico_stock(tablas["stock_variantes"], carpeta, pie),
        grafico_importe_por_tipo(tablas["pedidos_unicos"], carpeta, pie),
        grafico_pares_frente_a_importe(tablas["pedidos_unicos"], carpeta, pie),
    ]
