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

Cada ejecucion deja estado_ejecucion.csv con su resultado. Solo LEE la carpeta
de entrada; los resultados van a la carpeta de salida (graficos en graficos/).

Tres modos, cada uno con su entrada y su salida, para no mezclar nunca datos:
    real               entrada_acc/                     -> outputs/real/
    sintetico          datos_sinteticos/limpios/        -> outputs/sinteticos/
    sintetico-errores  datos_sinteticos/con_errores/    -> outputs/sinteticos_con_errores/

En Windows, desde la carpeta python-analisis:
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


def ejecutar(carpeta, salida, con_graficos=True):
    """Hace todo el proceso. Devuelve 0 si ha ido bien y 1 si no."""
    carpeta = Path(carpeta)
    salida = Path(salida)
    pd.set_option("display.width", 200)
    pd.set_option("display.max_colwidth", 90)

    ejecucion = datetime.now().strftime(config.FORMATO_FECHA)
    origen = pipeline.etiqueta_origen(carpeta)
    print("NOVA Sneakers - Análisis de datos (calidad, análisis, KPIs, gráficos, estadística, "
          "segmentación y predicción)")
    print(f"Carpeta de entrada: {carpeta}")
    print(f"Origen:             {origen}")
    print(f"Ejecución:          {ejecucion}")

    def guardar(tabla, archivo):
        # Una tabla con indice con nombre (una matriz) lo pasa a columna
        if tabla.index.name is not None:
            tabla = tabla.reset_index()
        return pipeline.guardar_salida(tabla, archivo, salida, carpeta, origen, ejecucion)

    def anotar_estado(estado, detalle):
        guardar(pd.DataFrame([{"estado": estado, "detalle": detalle}]), "estado_ejecucion.csv")

    # 1. Doce reglas de calidad
    resultado = calidad.evaluar(carpeta)
    incidencias = resultado["incidencias"]
    guardar(incidencias, "incidencias.csv")
    guardar(resultado["resumen"], "resumen_calidad.csv")
    guardar(resultado["rechazadas"], "filas_rechazadas.csv")

    titulo("Calidad de los datos (12 reglas, apartado 6.2)")
    print(resultado["resumen"].to_string(index=False))
    if len(incidencias) == 0:
        print("\nNinguna incidencia.")
    else:
        print(f"\n{len(incidencias)} incidencias:")
        print(incidencias[["regla", "tabla", "registro", "fila", "columna", "valor", "gravedad", "detalle"]]
              .to_string(index=False))

    if resultado["bloqueado"]:
        anotar_estado("BLOQUEADO", "hay incidencias bloqueantes y no se ha calculado ninguna cifra. Cualquier "
                      "otro resultado de esta carpeta es de una ejecución anterior (mira su columna ejecucion) "
                      "y está DESACTUALIZADO")
        print("\nDATOS BLOQUEADOS: hay incidencias bloqueantes. No se publica ninguna cifra.")
        print("Acceso a Datos tiene que corregir la exportación y volver a generarla.")
        print(f"Detalle en {salida / 'incidencias.csv'}")
        return 1

    datos = resultado["datos"]
    validos = resultado["validos"]
    corte = datos["stock"]["fecha_corte"].max()   # momento de la exportacion

    # 2. Resumen de la carga (fase 1)
    titulo("Resumen de la carga")
    for nombre, etiqueta in NOMBRES.items():
        print(f"  {etiqueta + ':':22}{len(datos[nombre]):>5}")
    print(f"  {'Fecha de corte stock:':22}{corte}")
    print()
    print(pipeline.manifiesto(carpeta, datos).to_string(index=False))
    if resultado["avisos"]:
        print("\nAvisos de lectura:")
        for aviso in resultado["avisos"]:
            print(f"  - {aviso}")
    titulo("Comprobaciones rápidas de la fase 1")
    for comprobacion in comprobaciones.comprobar_todo(datos, resultado["avisos"]):
        print(f"  [{comprobacion['resultado']:5}] {comprobacion['comprobacion']}: {comprobacion['detalle']}")

    # 3. Tablas de analisis (solo filas validas, la misma version de los datos)
    tablas = analiticas.calcular_tablas(datos, validos)
    tablas["nulos_por_columna"] = calidad.nulos_por_columna(datos)
    titulo("DataFrames de análisis (outputs/*.csv)")
    for nombre, tabla in tablas.items():
        if "estado" in tabla.columns and len(tabla) == 1 and tabla["estado"].iloc[0] == analiticas.NO_CALCULABLE:
            print(f"  {nombre:32} NO CALCULABLE: {tabla['motivo'].iloc[0]}")
        else:
            print(f"  {nombre:32} {len(tabla):>4} filas")
        if nombre in NO_SE_GUARDAN:
            continue
        if nombre == "pedidos_unicos":
            tabla = tabla.drop(columns=["nombre_cliente"])   # el nombre no hace falta en el CSV
        guardar(tabla, f"{nombre}.csv")

    # 4. Importes con tres criterios (fase 2)
    criterios = analiticas.importes_por_criterio(tablas["pedidos_unicos"])
    guardar(criterios, "importes_por_criterio.csv")
    titulo("Pedidos, pares e importe según el criterio (no son ingresos cobrados)")
    print(criterios[["criterio", "pedidos", "pares", "importe_eur", "iva"]].to_string(index=False))

    # 5. KPIs
    tabla_kpis = kpis.calcular_kpis(tablas["pedidos_unicos"], tablas["modelos_abc"], tablas["ventas_por_talla"],
                                    tablas["stock_variantes"], tablas["ventas_por_periodo"])
    guardar(tabla_kpis, "kpis.csv")
    titulo("KPIs (datos de " + pipeline.tipo_origen(carpeta) + ")")
    print(tabla_kpis[["codigo", "nombre", "valor", "unidad", "poblacion", "estado", "detalle"]].to_string(index=False))

    # 6. Conciliacion con SQL y coherencia de los KPIs con las mismas consultas
    carpeta_sql = carpeta / config.CARPETA_SQL
    tabla_conciliacion = conciliacion.conciliar(carpeta_sql, tablas["pedidos_unicos"], tablas["lineas_enriquecidas"])
    titulo("Conciliación con las consultas SQL P-A, P-B y P-C de Acceso a Datos (y caso N: N-1, N-2 y N-3)")
    cuadra = True
    if pipeline.tipo_origen(carpeta) == "SINTETICO":
        print("  NO APLICA: los datos sintéticos no salen de PostgreSQL; no hay consultas con las que compararlos.")
    elif tabla_conciliacion is None:
        faltan = ", ".join(conciliacion.faltan_resultados(carpeta_sql))
        print(f"  PENDIENTE: faltan los resultados SQL en {carpeta_sql} ({faltan}).")
        print("  No se da por buena ninguna cifra sin compararla.")
    else:
        coherencia = kpis.coherencia_con_sql(tabla_kpis, carpeta_sql)
        guardar(tabla_conciliacion, "conciliacion_sql.csv")
        guardar(coherencia, "coherencia_kpis_sql.csv")
        comparadas = [("tablas", tabla_conciliacion), ("KPIs", coherencia)]
        # Caso N: ingresos de un mes, matriz talla x modelo y clientes unicos
        caso_n = conciliacion.contrastar_caso_n(carpeta_sql, tablas)
        if caso_n is None:
            faltan = ", ".join(conciliacion.faltan_resultados(carpeta_sql, conciliacion.CONSULTAS_CASO_N))
            print(f"  caso N: PENDIENTE: faltan {faltan}.")
        else:
            guardar(caso_n, "contraste_sql_caso_n.csv")
            comparadas.append(("caso N", caso_n))
        for nombre, cifras in comparadas:
            iguales = (cifras["resultado"] == "coincide").sum()
            print(f"  {nombre}: {iguales} de {len(cifras)} cifras coinciden con SQL")
            distintas = cifras[cifras["resultado"] != "coincide"]
            if len(distintas) > 0:
                cuadra = False
                print(distintas[["consulta", "indicador", "clave", "valor_sql", "valor_python", "resultado"]]
                      .to_string(index=False))

    # 7. Graficos
    if con_graficos:
        pie = (f"Origen: {origen} · Corte: {corte:%Y-%m-%d %H:%M} · Calculado: {ejecucion} · "
               f"Filtros: ninguno · IVA {config.IVA}")
        rutas = visualizaciones.generar_todos(tablas, salida / "graficos", pie)
        titulo(f"Gráficos ({len(rutas)} PNG en {salida / 'graficos'})")
        for archivo, tipo, pregunta in visualizaciones.GRAFICOS:
            print(f"  {archivo:32} {tipo:26} {pregunta}")

    # 8. Estadistica: descriptivos, tres hipotesis y bootstrap del ticket medio
    tipo = pipeline.tipo_origen(carpeta)
    descriptivos = estadistica.descriptivos(tablas)
    hipotesis = estadistica.contrastar_hipotesis(tablas, tipo)
    ticket = estadistica.bootstrap_ticket_medio(tablas["pedidos_unicos"], tipo)
    guardar(descriptivos, "estadisticos_descriptivos.csv")
    guardar(hipotesis, "hipotesis.csv")
    guardar(ticket, "bootstrap_ticket_medio.csv")
    titulo(f"Estadística (datos de {tipo}; {config.BOOTSTRAP_REMUESTREOS} remuestreos, semilla {config.SEMILLA})")
    print(descriptivos[["variable", "grupo", "n", "media", "mediana", "desviacion_tipica", "p25", "p75",
                        "mejor_resumen"]].to_string(index=False))
    print()
    print(hipotesis[["codigo", "n", "estimacion", "ic_inferior", "ic_superior", "unidad", "resultado"]]
          .to_string(index=False))
    fila_ticket = ticket.iloc[0]
    print(f"\n  Ticket medio: {fila_ticket['estimacion']} € (IC 95 %: {fila_ticket['ic_inferior']} a "
          f"{fila_ticket['ic_superior']} €, n = {fila_ticket['n']}) -> {fila_ticket['resultado']}")

    # 9. Segmentacion de clientes (RFM y KMeans) y prediccion de la demanda (fase 5)
    tabla_rfm = segmentacion.rfm(tablas["pedidos_unicos"], validos["clientes"], corte)
    resumen_rfm = segmentacion.resumen_segmentos(tabla_rfm)
    # kmeans_clientes devuelve tres cosas: la eleccion de k, los grupos y la tabla RFM con la columna cluster
    seleccion_k, clusters, tabla_rfm = segmentacion.kmeans_clientes(tabla_rfm)
    rfm_frente_a_kmeans = segmentacion.comparar_rfm_kmeans(tabla_rfm)
    resultados = {"rfm_clientes": tabla_rfm, "rfm_segmentos": resumen_rfm, "kmeans_seleccion_k": seleccion_k,
                  "kmeans_clusters": clusters, "rfm_frente_a_kmeans": rfm_frente_a_kmeans}
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
        if "estado" in tabla.columns and len(tabla) == 1 and tabla["estado"].iloc[0] == analiticas.NO_CALCULABLE:
            print(f"  {nombre:32} NO CALCULABLE: {tabla['motivo'].iloc[0]}")
        else:
            print(f"  {nombre:32} {len(tabla):>4} filas")
        guardar(tabla, f"{nombre}.csv")
    print()
    print(resumen_rfm[["segmento", "clientes", "recency_media_dias", "frequency_media", "monetary_total",
                       "porcentaje_importe"]].to_string(index=False))
    if "elegido" in seleccion_k.columns:
        print()
        print(seleccion_k.to_string(index=False))
        print(clusters[["cluster", "nombre", "clientes", "recency_media_dias", "frequency_media",
                        "monetary_medio"]].to_string(index=False))
    if "mae" in resultados["metricas_prediccion"].columns:
        print()
        print(resultados["metricas_prediccion"][["metodo", "mae", "rmse", "periodo_entrenamiento",
                                                 "periodo_evaluacion", "mejora_al_baseline"]].to_string(index=False))
    if con_graficos:
        ruta = visualizaciones.grafico_real_frente_a_prediccion(resultados["predicciones"],
                                                               salida / "graficos_prediccion", pie)
        print()
        print(f"  Gráfico: {ruta}")

    if cuadra:
        anotar_estado("CORRECTO", "todas las cifras de esta carpeta son de esta ejecución")
    else:
        anotar_estado("NO CUADRA CON SQL", "hay cifras que no coinciden con Acceso a Datos: revisar conciliacion_sql.csv")
    print(f"\nResultados guardados en {salida}")
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
