"""
Comprobacion periodica de la exportacion y recalculo (apartados 6.14 y 6.17).

No usa Streamlit: el dashboard llama a ciclo() cada 60 segundos, y las
pruebas lo llaman igual. Cada ciclo hace los cinco pasos de la rubrica:

1. Comprueba que archivos hay, su tamano, su fecha y su huella (un hash del
   CONTENIDO: si se vuelve a exportar lo mismo, no cuenta como cambio).
2. Lee los CSV del disco y los valida con las 12 reglas de calidad.
3. Si son validos, recalcula TODO a partir de esa misma version de los datos:
   tablas, KPIs, segmentacion, prediccion, conciliacion e informe.
4. Publica un resultado completo, o ninguno: con errores no hay cifras nuevas
   y el ultimo resultado valido se conserva marcado como desactualizado.
5. Anota el ciclo en el registro de eventos.

Se recalcula siempre, aunque los CSV no hayan cambiado: asi se comprueba
cada minuto que siguen siendo validos. Si no han cambiado, las cifras salen
iguales y el estado es SIN CAMBIOS. Python nunca escribe en la carpeta de
entrada: los datos nuevos de PostgreSQL solo llegan cuando Acceso a Datos
vuelve a exportar los CSV.
"""
import hashlib
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

import analiticas
import calidad
import conciliacion
import config
import informe
import kpis
import pipeline
import prediccion
import registro
import segmentacion

# Los cuatro estados que pide la rubrica
CORRECTO = "CORRECTO"                 # datos nuevos, validos y publicados
SIN_CAMBIOS = "SIN CAMBIOS"           # los mismos datos: recalculado y sin cambios
DATOS_INVALIDOS = "DATOS INVÁLIDOS"   # se leen, pero hay incidencias bloqueantes
ERROR_CARGA = "ERROR DE CARGA"        # falta un archivo o no se puede leer


def inspeccionar_archivos(carpeta):
    """Una fila por archivo de la exportacion: si existe, su tamano, su fecha y su huella."""
    carpeta = Path(carpeta)
    # Los cinco CSV y, al final, ORIGEN.txt
    nombres = []
    for definicion in config.ARCHIVOS.values():
        nombres.append(definicion["archivo"])
    nombres.append(config.ARCHIVO_ORIGEN)
    filas = []
    for nombre in nombres:
        ruta = carpeta / nombre
        if ruta.exists():
            contenido = ruta.read_bytes()
            filas.append({"archivo": nombre, "existe": True, "bytes": len(contenido),
                          "modificado": datetime.fromtimestamp(ruta.stat().st_mtime).replace(microsecond=0),
                          "huella": hashlib.sha256(contenido).hexdigest()[:12]})
        else:
            filas.append({"archivo": nombre, "existe": False, "bytes": 0, "modificado": pd.NaT, "huella": ""})
    return pd.DataFrame(filas)


def version_datos(archivos):
    """
    La version de la exportacion: una huella de las huellas de todos los
    archivos. Cambia si cambia el contenido de cualquiera, no solo su fecha.
    """
    texto = "|".join(archivos["archivo"] + ":" + archivos["huella"])
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:8]


def avisos_archivos(archivos, ahora):
    """Avisos sobre la exportacion: archivos que faltan, vacios, antiguos o de distintos momentos."""
    avisos = []
    csv = archivos[archivos["archivo"] != config.ARCHIVO_ORIGEN]
    for nombre in csv.loc[~csv["existe"], "archivo"]:
        avisos.append(f"Falta {nombre}: la exportación está incompleta.")
    for nombre in csv.loc[csv["existe"] & (csv["bytes"] == 0), "archivo"]:
        avisos.append(f"{nombre} está vacío (0 bytes).")
    presentes = csv[csv["existe"]]
    if len(presentes) > 0:
        mas_antiguo = presentes["modificado"].min()
        horas = (ahora - mas_antiguo).total_seconds() / 3600
        if horas > config.HORAS_EXPORTACION_ANTIGUA:
            avisos.append(f"Exportación antigua: el CSV más antiguo es del {mas_antiguo:%Y-%m-%d %H:%M} "
                          f"(hace {horas:.0f} h). Acceso a Datos tiene que volver a exportar para ver datos nuevos.")
        minutos = (presentes["modificado"].max() - mas_antiguo).total_seconds() / 60
        if minutos > config.MINUTOS_EXPORTACION_INCOMPLETA:
            avisos.append(f"Los CSV se escribieron con {minutos:.0f} minutos de diferencia: puede que no sean "
                          "todos de la misma exportación.")
    if not archivos.loc[archivos["archivo"] == config.ARCHIVO_ORIGEN, "existe"].iloc[0]:
        avisos.append("Falta ORIGEN.txt: no se sabe de qué base salen estos CSV.")
    return avisos


def estado_conciliacion(carpeta, tablas, tabla_kpis):
    """Texto con el resultado de la conciliacion con SQL y la tabla de cifras comparadas (o None)."""
    carpeta_sql = Path(carpeta) / config.CARPETA_SQL
    if pipeline.tipo_origen(carpeta) == "SINTETICO":
        return "NO APLICA: los datos sintéticos no salen de PostgreSQL", None
    tabla = conciliacion.conciliar(carpeta_sql, tablas["pedidos_unicos"], tablas["lineas_enriquecidas"])
    if tabla is None:
        faltan = ", ".join(conciliacion.faltan_resultados(carpeta_sql))
        return f"PENDIENTE: faltan los resultados SQL ({faltan})", None
    coherencia = kpis.coherencia_con_sql(tabla_kpis, carpeta_sql)
    juntas = pd.concat([tabla, coherencia], ignore_index=True)   # cifras de las tablas y de los KPIs
    iguales = int((juntas["resultado"] == "coincide").sum())
    texto = f"{iguales} de {len(juntas)} cifras coinciden con SQL"
    if iguales == len(juntas):
        return texto, juntas
    return f"NO CUADRA: {texto}", juntas


def calcular_publicacion(carpeta, resultado, version, momento):
    """
    Todo lo que publica el dashboard, calculado de una vez con la misma
    version de los datos (resultado es el de calidad.evaluar, sin bloqueo).
    Son las mismas funciones que usa main.py.
    """
    datos = resultado["datos"]
    validos = resultado["validos"]
    corte = datos["stock"]["fecha_corte"].max()
    tipo = pipeline.tipo_origen(carpeta)

    tablas = analiticas.calcular_tablas(datos, validos)
    tabla_kpis = kpis.calcular_kpis(tablas["pedidos_unicos"], tablas["modelos_abc"], tablas["ventas_por_talla"],
                                    tablas["stock_variantes"], tablas["ventas_por_periodo"])
    tabla_rfm = segmentacion.rfm(tablas["pedidos_unicos"], validos["clientes"], corte)
    resumen_rfm = segmentacion.resumen_segmentos(tabla_rfm)
    seleccion_k, clusters, tabla_rfm = segmentacion.kmeans_clientes(tabla_rfm)
    resultados_prediccion = prediccion.predecir_demanda(tablas["lineas_enriquecidas"], corte)
    texto_conciliacion, tabla_conciliacion = estado_conciliacion(carpeta, tablas, tabla_kpis)
    return {
        "version": version,
        "actualizado": momento,
        "corte": corte,
        "tipo": tipo,
        "datos": datos,
        "validos": validos,
        "tablas": tablas,
        "kpis": tabla_kpis,
        "segmentacion": {
            "rfm_clientes": tabla_rfm,
            "rfm_segmentos": resumen_rfm,
            "kmeans_seleccion_k": seleccion_k,
            "kmeans_clusters": clusters,
            "rfm_frente_a_kmeans": segmentacion.comparar_rfm_kmeans(tabla_rfm),
        },
        "prediccion": resultados_prediccion,
        "conciliacion": texto_conciliacion,
        "tabla_conciliacion": tabla_conciliacion,
        "informe": informe.conclusiones(tablas, resumen_rfm, resultados_prediccion["metricas_prediccion"], tipo),
        "filas_validas": sum(len(tabla) for tabla in validos.values()),
    }


def ciclo(carpeta, anterior=None, operacion="comprobación automática", archivo_registro=None):
    """
    Un ciclo completo de comprobacion y recalculo de una carpeta de entrada.

    anterior es lo que devolvio el ciclo anterior de ESTA carpeta (o None): de
    el solo se toma el ultimo resultado valido. Devuelve un diccionario con
    el estado, los mensajes, la calidad y el resultado publicado.
    """
    inicio = time.perf_counter()
    ahora = datetime.now().replace(microsecond=0)
    carpeta = Path(carpeta)
    publicado = None
    if anterior is not None and Path(anterior["carpeta"]) == carpeta:   # nunca se mezclan origenes
        publicado = anterior["publicado"]

    archivos = inspeccionar_archivos(carpeta)
    version = version_datos(archivos)
    estado = {
        "carpeta": carpeta,
        "origen": pipeline.etiqueta_origen(carpeta),
        "tipo": pipeline.tipo_origen(carpeta),
        "comprobado": ahora,
        "archivos": archivos,
        "version": version,
        "avisos": avisos_archivos(archivos, ahora),
        "calidad": None,
        "publicado": publicado,
    }
    try:
        resultado = calidad.evaluar(carpeta)
        estado["calidad"] = resultado
        if resultado["bloqueado"]:
            # Sin los cinco archivos legibles es un error de carga; con ellos, datos invalidos
            cargados = len(resultado["datos"]) == len(config.ARCHIVOS)
            estado["estado"] = DATOS_INVALIDOS if cargados else ERROR_CARGA
            bloqueantes = resultado["incidencias"][resultado["incidencias"]["gravedad"] == calidad.BLOQUEANTE]
            estado["mensaje"] = (f"Incidencias bloqueantes: {len(bloqueantes)}. No se publica ninguna cifra nueva. "
                                 f"Primera: {bloqueantes['detalle'].iloc[0]}")
        else:
            nuevo = calcular_publicacion(carpeta, resultado, version, ahora)
            if publicado is not None and publicado["version"] == version:
                estado["estado"] = SIN_CAMBIOS
                nuevo["actualizado"] = publicado["actualizado"]   # los datos son los mismos desde entonces
                estado["mensaje"] = "Los CSV no han cambiado: se han vuelto a leer, validar y calcular, con el mismo resultado."
            else:
                estado["estado"] = CORRECTO
                estado["mensaje"] = "Datos leídos, validados y publicados."
            estado["publicado"] = nuevo
    except Exception as error:
        # Cualquier fallo inesperado: se avisa y se anota, pero no se publica
        # nada a medias (se conserva el ultimo resultado valido)
        estado["estado"] = ERROR_CARGA
        estado["mensaje"] = f"Error al procesar la exportación: {error}"

    # Los mensajes de error de lectura llevan la ruta completa de la carpeta: se deja la relativa
    for ruta in {str(carpeta), str(carpeta.resolve())}:
        estado["mensaje"] = estado["mensaje"].replace(ruta, carpeta_relativa(carpeta))
    estado["desactualizado"] = estado["publicado"] is not None and estado["estado"] in (DATOS_INVALIDOS, ERROR_CARGA)
    estado["duracion"] = round(time.perf_counter() - inicio, 2)
    anotar_ciclo(estado, operacion, archivo_registro)
    return estado


def carpeta_relativa(carpeta):
    """La carpeta vista desde python-analisis (no la ruta completa del ordenador)."""
    try:
        return Path(carpeta).resolve().relative_to(config.CARPETA_PROYECTO).as_posix()
    except ValueError:
        return Path(carpeta).name


def anotar_ciclo(estado, operacion, archivo_registro=None):
    """Una fila en el registro de eventos con el resultado del ciclo."""
    resultado = estado["calidad"]
    if resultado is None:
        # El ciclo ha fallado antes de evaluar la calidad: no hay filas ni incidencias
        incidencias = pd.DataFrame(columns=["gravedad"])
        leidas = 0
        validas = 0
    else:
        incidencias = resultado["incidencias"]
        leidas = 0
        for tabla in resultado["datos"].values():
            leidas += len(tabla)
        validas = 0
        for tabla in resultado["validos"].values():
            validas += len(tabla)
    registro.anotar(
        archivo_registro or config.ARCHIVO_REGISTRO,
        fecha_hora=estado["comprobado"].strftime(config.FORMATO_FECHA),
        origen=estado["origen"],
        carpeta=carpeta_relativa(estado["carpeta"]),
        operacion=operacion,
        resultado=estado["estado"],
        filas_procesadas=leidas,
        filas_validas=validas,
        incidencias=len(incidencias),
        bloqueantes=int((incidencias["gravedad"] == calidad.BLOQUEANTE).sum()),
        version_datos=estado["version"],
        duracion_s=estado["duracion"],
        detalle=" ".join([estado["mensaje"]] + estado["avisos"]),
    )
