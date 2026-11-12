"""
Ejecucion por consola (fases 1 a 6).

1. Aplica las doce reglas de calidad y guarda incidencias.csv,
   resumen_calidad.csv y filas_rechazadas.csv (siempre, aunque haya bloqueo).
2. Si hay alguna incidencia bloqueante, se para: no publica ninguna cifra.
3. Si no, calcula todas las tablas de analisis, los importes por criterio, los
   KPIs, la conciliacion con SQL, los graficos, la estadistica, la segmentacion
   de clientes (RFM y KMeans), la prediccion de demanda y las cinco
   conclusiones del informe ejecutivo, y lo guarda todo.

El dashboard (app_dashboard.py) usa estas mismas funciones.

Cada ejecucion deja estado_ejecucion.csv con su resultado y
metadatos_dataframes.csv con la fecha de corte, las reglas, los filtros, las
filas de origen y la funcion de cada CSV. Solo LEE la carpeta de entrada; los
resultados van a la carpeta de salida (los graficos, en graficos/ y
graficos_prediccion/).

Tres modos, cada uno con su entrada y su salida, para no mezclar nunca datos:
    real               entrada_acc/                     -> outputs/real/
    sintetico          datos_sinteticos/limpios/        -> outputs/sinteticos/
    sintetico-errores  datos_sinteticos/con_errores/    -> outputs/sinteticos_con_errores/

En Windows, desde la carpeta 04_Python:
    .venv\\Scripts\\python.exe main.py
    .venv\\Scripts\\python.exe main.py --modo sintetico
    .venv\\Scripts\\python.exe main.py --entrada CARPETA --salida CARPETA

Termina con codigo 1 si los datos estan bloqueados o si alguna cifra no
coincide con SQL.
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

import analiticas
import calidad
import comprobaciones
import conciliacion
import config
import estadistica
import informe
import kpis
import metadatos
import pipeline
import prediccion
import segmentacion
import visualizaciones

# Cada modo lee de una carpeta y escribe en otra: los resultados reales y los
# sinteticos nunca acaban en la misma carpeta
MODOS = {
    "real": (config.CARPETA_ENTRADA, config.CARPETA_SALIDA / "real"),
    "sintetico": (config.CARPETA_SINTETICOS_LIMPIOS, config.CARPETA_SALIDA / "sinteticos"),
    "sintetico-errores": (config.CARPETA_SINTETICOS_ERRORES, config.CARPETA_SALIDA / "sinteticos_con_errores"),
}

NOMBRES = {
    "clientes": "Clientes",
    "modelos": "Modelos",
    "pedidos": "Pedidos",
    "lineas_pedido": "Líneas de pedido",
    "stock": "Registros de stock",
}

# Tablas que no se guardan en CSV: lineas_enriquecidas es la vista de detalle
# (lleva el nombre de cada cliente en cada linea y no es una salida de la rubrica)
NO_SE_GUARDAN = ["lineas_enriquecidas"]


def titulo(texto):
    print()
    print(texto)
    print("-" * len(texto))


# ---------------------------------------------------------------------
# Lo que comparten todos los pasos: la ejecucion y el guardado de los CSV
# ---------------------------------------------------------------------

def empezar(carpeta, salida):
    """
    Los datos de esta ejecucion, en un diccionario que reciben todos los pasos.
    Escribe la cabecera de la consola.
    """
    carpeta = Path(carpeta)
    ejecucion = {
        "carpeta": carpeta,
        "salida": Path(salida),
        "momento": datetime.now().strftime(config.FORMATO_FECHA),   # va en la columna ejecucion de cada CSV
        "origen": pipeline.etiqueta_origen(carpeta),   # el texto largo: "ACC · PRUEBA (...)"
        "tipo": pipeline.tipo_origen(carpeta),         # PRUEBA, REAL, SINTETICO o DESCONOCIDO
        "guardados": [],   # (archivo, filas) de cada CSV guardado: para metadatos_dataframes.csv
    }
    print("NOVA Sneakers - Análisis de datos (calidad, análisis, KPIs, gráficos, estadística, "
          "segmentación y predicción)")
    print(f"Carpeta de entrada: {carpeta}")
    print(f"Origen:             {ejecucion['origen']}")
    print(f"Ejecución:          {ejecucion['momento']}")
    return ejecucion


def guardar(ejecucion, tabla, archivo):
    """Guarda un CSV en la carpeta de salida y lo apunta para metadatos_dataframes.csv."""
    # Una tabla con indice con nombre (una matriz) lo pasa a columna
    if tabla.index.name is not None:
        tabla = tabla.reset_index()
    ejecucion["guardados"].append((archivo, len(tabla)))
    return pipeline.guardar_salida(tabla, archivo, ejecucion["salida"], ejecucion["carpeta"], ejecucion["origen"],
                                   ejecucion["momento"])


def anotar_estado(ejecucion, resultado, estado, detalle):
    """
    Guarda estado_ejecucion.csv y despues metadatos_dataframes.csv, con todos los
    CSV de esta ejecucion. Por eso es lo ultimo que se guarda.
    """
    guardar(ejecucion, pd.DataFrame([{"estado": estado, "detalle": detalle}]), "estado_ejecucion.csv")
    tabla_metadatos = metadatos.tabla(ejecucion["guardados"], resultado["datos"], resultado["validos"])
    pipeline.guardar_salida(tabla_metadatos, "metadatos_dataframes.csv", ejecucion["salida"], ejecucion["carpeta"],
                            ejecucion["origen"], ejecucion["momento"])


def imprimir_filas(nombre, tabla):
    """Una linea del listado de tablas: cuantas filas tiene, o por que no se ha podido calcular."""
    if analiticas.es_no_calculable(tabla):
        print(f"  {nombre:32} NO CALCULABLE: {tabla['motivo'].iloc[0]}")
    else:
        print(f"  {nombre:32} {len(tabla):>4} filas")


# ---------------------------------------------------------------------
# Los pasos, en el orden en que los llama ejecutar()
# ---------------------------------------------------------------------

def paso_calidad(ejecucion):
    """1. Las doce reglas de calidad. Sus tres CSV se guardan siempre, aunque haya bloqueo."""
    resultado = calidad.evaluar(ejecucion["carpeta"])
    incidencias = resultado["incidencias"]
    guardar(ejecucion, incidencias, "incidencias.csv")
    guardar(ejecucion, resultado["resumen"], "resumen_calidad.csv")
    guardar(ejecucion, resultado["rechazadas"], "filas_rechazadas.csv")

    titulo("Calidad de los datos (12 reglas, apartado 6.2)")
    print(resultado["resumen"].to_string(index=False))
    if len(incidencias) == 0:
        print("\nNinguna incidencia.")
    else:
        print(f"\n{len(incidencias)} incidencias:")
        print(incidencias[["regla", "tabla", "registro", "fila", "columna", "valor", "gravedad", "detalle"]]
              .to_string(index=False))
    return resultado


def parar_por_bloqueo(ejecucion, resultado):
    """Con una incidencia bloqueante no se calcula ni se publica ninguna cifra. Devuelve el codigo 1."""
    anotar_estado(ejecucion, resultado, "BLOQUEADO",
                  "hay incidencias bloqueantes y no se ha calculado ninguna cifra. Cualquier otro resultado de "
                  "esta carpeta es de una ejecución anterior (mira su columna ejecucion) y está DESACTUALIZADO")
    print("\nDATOS BLOQUEADOS: hay incidencias bloqueantes. No se publica ninguna cifra.")
    print("Acceso a Datos tiene que corregir la exportación y volver a generarla.")
    print(f"Detalle en {ejecucion['salida'] / 'incidencias.csv'}")
    return 1


def paso_resumen_carga(ejecucion, resultado, corte):
    """2. Resumen de la carga (fase 1): filas, manifiesto, avisos de lectura y comprobaciones rapidas."""
    datos = resultado["datos"]
    titulo("Resumen de la carga")
    for nombre, etiqueta in NOMBRES.items():
        print(f"  {etiqueta + ':':22}{len(datos[nombre]):>5}")
    print(f"  {'Fecha de corte stock:':22}{corte}")
    print()
    print(pipeline.manifiesto(ejecucion["carpeta"], datos).to_string(index=False))
    if resultado["avisos"]:
        print("\nAvisos de lectura:")
        for aviso in resultado["avisos"]:
            print(f"  - {aviso}")
    titulo("Comprobaciones rápidas de la fase 1")
    for comprobacion in comprobaciones.comprobar_todo(datos, resultado["avisos"]):
        print(f"  [{comprobacion['resultado']:5}] {comprobacion['comprobacion']}: {comprobacion['detalle']}")


def paso_tablas(ejecucion, datos, validos):
    """3. Tablas de analisis (solo filas validas, la misma version de los datos). Devuelve el diccionario."""
    tablas = analiticas.calcular_tablas(datos, validos)
    tablas["nulos_por_columna"] = calidad.nulos_por_columna(datos)
    titulo("DataFrames de análisis (outputs/*.csv)")
    for nombre, tabla in tablas.items():
        imprimir_filas(nombre, tabla)
        if nombre in NO_SE_GUARDAN:
            continue
        if nombre == "pedidos_unicos":
            tabla = tabla.drop(columns=["nombre_cliente"])   # el nombre no hace falta en el CSV
        guardar(ejecucion, tabla, f"{nombre}.csv")
    return tablas


def paso_importes(ejecucion, tablas):
    """4. Pedidos, pares e importe con tres criterios (fase 2)."""
    criterios = analiticas.importes_por_criterio(tablas["pedidos_unicos"])
    guardar(ejecucion, criterios, "importes_por_criterio.csv")
    titulo("Pedidos, pares e importe según el criterio (no son ingresos cobrados)")
    print(criterios[["criterio", "pedidos", "pares", "importe_eur", "iva"]].to_string(index=False))


def paso_kpis(ejecucion, tablas):
    """5. Los KPIs. Devuelve su tabla (la conciliacion la necesita)."""
    tabla_kpis = kpis.calcular_kpis(tablas["pedidos_unicos"], tablas["modelos_abc"], tablas["ventas_por_talla"],
                                    tablas["stock_variantes"], tablas["ventas_por_periodo"])
    guardar(ejecucion, tabla_kpis, "kpis.csv")
    titulo("KPIs (datos de " + ejecucion["tipo"] + ")")
    print(tabla_kpis[["codigo", "nombre", "valor", "unidad", "poblacion", "estado", "detalle"]].to_string(index=False))
    return tabla_kpis


def paso_conciliacion(ejecucion, tablas, tabla_kpis):
    """
    6. Conciliacion con SQL y coherencia de los KPIs con las mismas consultas.
    Devuelve False si alguna cifra no coincide con SQL (y True si coinciden todas,
    o si no hay con que comparar: sinteticos o resultados SQL pendientes).
    """
    carpeta_sql = ejecucion["carpeta"] / config.CARPETA_SQL
    tabla_conciliacion = conciliacion.conciliar(carpeta_sql, tablas["pedidos_unicos"], tablas["lineas_enriquecidas"])
    titulo("Conciliación con las consultas SQL P-A, P-B y P-C de Acceso a Datos (y caso N: N-1, N-2 y N-3)")
    if ejecucion["tipo"] == "SINTETICO":
        print("  NO APLICA: los datos sintéticos no salen de PostgreSQL; no hay consultas con las que compararlos.")
        return True
    if tabla_conciliacion is None:
        faltan = ", ".join(conciliacion.faltan_resultados(carpeta_sql))
        print(f"  PENDIENTE: faltan los resultados SQL en {carpeta_sql} ({faltan}).")
        print("  No se da por buena ninguna cifra sin compararla.")
        return True

    coherencia = kpis.coherencia_con_sql(tabla_kpis, carpeta_sql)
    guardar(ejecucion, tabla_conciliacion, "conciliacion_sql.csv")
    guardar(ejecucion, coherencia, "coherencia_kpis_sql.csv")
    comparadas = [("tablas", tabla_conciliacion), ("KPIs", coherencia)]
    # Caso N: ingresos de un mes, matriz talla x modelo y clientes unicos
    caso_n = conciliacion.contrastar_caso_n(carpeta_sql, tablas)
    if caso_n is None:
        faltan = ", ".join(conciliacion.faltan_resultados(carpeta_sql, conciliacion.CONSULTAS_CASO_N))
        print(f"  caso N: PENDIENTE: faltan {faltan}.")
    else:
        guardar(ejecucion, caso_n, "contraste_sql_caso_n.csv")
        comparadas.append(("caso N", caso_n))

    cuadra = True
    for nombre, cifras in comparadas:
        iguales = (cifras["resultado"] == "coincide").sum()
        print(f"  {nombre}: {iguales} de {len(cifras)} cifras coinciden con SQL")
        distintas = cifras[cifras["resultado"] != "coincide"]
        if len(distintas) > 0:
            cuadra = False
            print(distintas[["consulta", "indicador", "clave", "valor_sql", "valor_python", "resultado"]]
                  .to_string(index=False))
    return cuadra


def pie_de_graficos(ejecucion, corte):
    """El pie de los PNG de main.py: origen, fecha de corte, momento del calculo, filtros e IVA."""
    return (f"Origen: {ejecucion['origen']} · Corte: {corte:%Y-%m-%d %H:%M} · Calculado: {ejecucion['momento']} · "
            f"Filtros: ninguno · IVA {config.IVA}")


def paso_graficos(ejecucion, tablas, pie):
    """7. Los diez graficos PNG y, en la consola, la pregunta que responde cada uno."""
    rutas = visualizaciones.generar_todos(tablas, ejecucion["salida"] / "graficos", pie)
    titulo(f"Gráficos ({len(rutas)} PNG en {ejecucion['salida'] / 'graficos'})")
    for archivo, tipo_grafico, pregunta in visualizaciones.GRAFICOS:
        print(f"  {archivo:32} {tipo_grafico:26} {pregunta}")


def paso_estadistica(ejecucion, tablas):
    """8. Estadistica: descriptivos, tres hipotesis y bootstrap del ticket medio."""
    tipo = ejecucion["tipo"]
    descriptivos = estadistica.descriptivos(tablas)
    hipotesis = estadistica.contrastar_hipotesis(tablas, tipo)
    ticket = estadistica.bootstrap_ticket_medio(tablas["pedidos_unicos"], tipo)
    guardar(ejecucion, descriptivos, "estadisticos_descriptivos.csv")
    guardar(ejecucion, hipotesis, "hipotesis.csv")
    guardar(ejecucion, ticket, "bootstrap_ticket_medio.csv")
    titulo(f"Estadística (datos de {tipo}; {config.BOOTSTRAP_REMUESTREOS} remuestreos, semilla {config.SEMILLA})")
    print(descriptivos[["variable", "grupo", "n", "media", "mediana", "desviacion_tipica", "p25", "p75",
                        "mejor_resumen"]].to_string(index=False))
    print()
    print(hipotesis[["codigo", "n", "estimacion", "ic_inferior", "ic_superior", "unidad", "resultado"]]
          .to_string(index=False))
    fila_ticket = ticket.iloc[0]
    print(f"\n  Ticket medio: {fila_ticket['estimacion']} € (IC 95 %: {fila_ticket['ic_inferior']} a "
          f"{fila_ticket['ic_superior']} €, n = {fila_ticket['n']}) -> {fila_ticket['resultado']}")


def paso_segmentacion_y_prediccion(ejecucion, tablas, validos, corte):
    """
    9. Segmentacion de clientes (RFM y KMeans), prediccion de la demanda (fase 5)
    y las cinco conclusiones del informe ejecutivo. Devuelve las tablas calculadas.
    """
    tipo = ejecucion["tipo"]
    resultados = segmentacion.segmentar_clientes(tablas["pedidos_unicos"], validos["clientes"], corte)
    resumen_rfm = resultados["rfm_segmentos"]
    seleccion_k = resultados["kmeans_seleccion_k"]
    clusters = resultados["kmeans_clusters"]
    resultados.update(prediccion.predecir_demanda(tablas["lineas_enriquecidas"], corte))
    # Las cinco conclusiones del informe ejecutivo (las mismas que ensena el dashboard)
    resultados["informe_ejecutivo"] = informe.conclusiones(tablas, resumen_rfm, resultados["metricas_prediccion"], tipo)

    titulo(f"Segmentación y predicción (datos de {tipo}; fecha de referencia {corte})")
    texto_aviso = estadistica.aviso(tipo).strip()
    if texto_aviso:
        print(texto_aviso)
    else:
        print("Datos de la base del equipo.")
    for nombre, tabla in resultados.items():
        imprimir_filas(nombre, tabla)
        guardar(ejecucion, tabla, f"{nombre}.csv")
    print()
    print(resumen_rfm[["segmento", "clientes", "recency_media_dias", "frequency_media", "monetary_total",
                       "porcentaje_importe"]].to_string(index=False))
    if not analiticas.es_no_calculable(seleccion_k):
        print()
        print(seleccion_k.to_string(index=False))
        print(clusters[["cluster", "nombre", "clientes", "recency_media_dias", "frequency_media",
                        "monetary_medio"]].to_string(index=False))
    if not analiticas.es_no_calculable(resultados["metricas_prediccion"]):
        print()
        print(resultados["metricas_prediccion"][["metodo", "mae", "rmse", "periodo_entrenamiento",
                                                 "periodo_evaluacion", "mejora_al_baseline"]].to_string(index=False))
    return resultados


def paso_grafico_prediccion(ejecucion, predicciones, pie):
    """El grafico de la prediccion, aparte de los otros diez (en graficos_prediccion/)."""
    ruta = visualizaciones.grafico_real_frente_a_prediccion(predicciones, ejecucion["salida"] / "graficos_prediccion",
                                                           pie)
    print()
    print(f"  Gráfico: {ruta}")


def ejecutar(carpeta, salida, con_graficos=True):
    """Hace todo el proceso, paso a paso. Devuelve 0 si ha ido bien y 1 si no."""
    pd.set_option("display.width", 200)
    pd.set_option("display.max_colwidth", 90)
    ejecucion = empezar(carpeta, salida)

    resultado = paso_calidad(ejecucion)                                   # 1
    if resultado["bloqueado"]:
        return parar_por_bloqueo(ejecucion, resultado)
    datos = resultado["datos"]
    validos = resultado["validos"]
    corte = datos["stock"]["fecha_corte"].max()   # momento de la exportacion

    paso_resumen_carga(ejecucion, resultado, corte)                       # 2
    tablas = paso_tablas(ejecucion, datos, validos)                       # 3
    paso_importes(ejecucion, tablas)                                      # 4
    tabla_kpis = paso_kpis(ejecucion, tablas)                             # 5
    cuadra = paso_conciliacion(ejecucion, tablas, tabla_kpis)             # 6
    if con_graficos:
        pie = pie_de_graficos(ejecucion, corte)
        paso_graficos(ejecucion, tablas, pie)                             # 7
    paso_estadistica(ejecucion, tablas)                                   # 8
    resultados = paso_segmentacion_y_prediccion(ejecucion, tablas, validos, corte)   # 9
    if con_graficos:
        paso_grafico_prediccion(ejecucion, resultados["predicciones"], pie)

    if cuadra:
        anotar_estado(ejecucion, resultado, "CORRECTO", "todas las cifras de esta carpeta son de esta ejecución")
    else:
        anotar_estado(ejecucion, resultado, "NO CUADRA CON SQL",
                      "hay cifras que no coinciden con Acceso a Datos: revisar conciliacion_sql.csv")
    print(f"\nResultados guardados en {ejecucion['salida']}")
    if cuadra:
        return 0
    return 1


def main():
    parser = argparse.ArgumentParser(description="NOVA Sneakers: calidad, análisis, KPIs, gráficos, estadística, "
                                                 "segmentación y predicción")
    parser.add_argument("--modo", choices=list(MODOS), default="real",
                        help="real (entrada_acc), sintetico o sintetico-errores (datos_sinteticos)")
    parser.add_argument("--entrada", help="otra carpeta de entrada (si no, la del modo)")
    parser.add_argument("--salida", help="otra carpeta de salida (si no, la del modo)")
    argumentos = parser.parse_args()
    entrada, salida = MODOS[argumentos.modo]
    return ejecutar(argumentos.entrada or entrada, argumentos.salida or salida)


if __name__ == "__main__":
    sys.exit(main())
