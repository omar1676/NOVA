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
ERROR_CARGA = "ERROR DE CARGA"        # falta un archivo, no se puede leer o falla el proceso


# Mira el tamano, la fecha y la huella (hash) de cada archivo de la exportacion
# Recibe la carpeta del origen; devuelve un DataFrame con una fila por archivo (los cinco CSV y ORIGEN.txt)
def inspeccionar_archivos(carpeta):
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


# Calcula la version de los datos (8 caracteres) con las huellas de los archivos
# Cambia si cambia el contenido de cualquier archivo, no su fecha
def version_datos(archivos):
    texto = "|".join(archivos["archivo"] + ":" + archivos["huella"])
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()[:8]


# Avisos: archivos que faltan (tambien ORIGEN.txt), vacios, antiguos o de exportaciones distintas
# Recibe la tabla de inspeccionar_archivos y la hora actual; devuelve una lista de textos
def avisos_archivos(archivos, ahora):
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


# Compara las cifras de Python con los resultados SQL de Acceso a Datos
# Devuelve el texto del resultado y la tabla de cifras comparadas (None si no aplica o faltan resultados)
def estado_conciliacion(carpeta, tablas, tabla_kpis):
    carpeta_sql = Path(carpeta) / config.CARPETA_SQL
    if pipeline.tipo_origen(carpeta) == "SINTETICO":
        return "NO APLICA: los datos sintéticos no salen de PostgreSQL", None
    tabla = conciliacion.conciliar(carpeta_sql, tablas["pedidos_unicos"], tablas["lineas_enriquecidas"])
    if tabla is None:
        faltan = ", ".join(conciliacion.faltan_resultados(carpeta_sql))
        return f"PENDIENTE: faltan los resultados SQL ({faltan})", None
    coherencia = kpis.coherencia_con_sql(tabla_kpis, carpeta_sql)
    partes = [tabla, coherencia]
    caso_n = conciliacion.contrastar_caso_n(carpeta_sql, tablas)   # None si faltan N-1, N-2 o N-3
    if caso_n is not None:
        partes.append(caso_n)
    juntas = pd.concat(partes, ignore_index=True)   # cifras de las tablas, de los KPIs y del caso N
    iguales = int((juntas["resultado"] == "coincide").sum())
    texto = f"{iguales} de {len(juntas)} cifras coinciden con SQL"
    if iguales == len(juntas):
        return texto, juntas
    return f"NO CUADRA: {texto}", juntas


# Calcula todo lo que se publica: tablas, KPIs, segmentos, prediccion, conciliacion e informe
# Devuelve un diccionario con todo lo que ensena el dashboard de esa version de los datos
def calcular_publicacion(carpeta, resultado, version, momento):
    datos = resultado["datos"]
    validos = resultado["validos"]
    corte = datos["stock"]["fecha_corte"].max()
    tipo = pipeline.tipo_origen(carpeta)

    tablas = analiticas.calcular_tablas(datos, validos)
    tabla_kpis = kpis.calcular_kpis(tablas["pedidos_unicos"], tablas["modelos_abc"], tablas["ventas_por_talla"],
                                    tablas["stock_variantes"], tablas["ventas_por_periodo"])
    segmentos = segmentacion.segmentar_clientes(tablas["pedidos_unicos"], validos["clientes"], corte)
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
        "segmentacion": segmentos,
        "prediccion": resultados_prediccion,
        "conciliacion": texto_conciliacion,
        "tabla_conciliacion": tabla_conciliacion,
        "informe": informe.conclusiones(tablas, segmentos["rfm_segmentos"], resultados_prediccion["metricas_prediccion"],
                                        tipo),
        "filas_validas": sum(len(tabla) for tabla in validos.values()),
    }


# Hace un ciclo completo: lee, valida, calcula, publica y lo anota en el registro
# Recibe la carpeta del origen y el estado anterior; devuelve el estado del ciclo (diccionario)
def ciclo(carpeta, anterior=None, operacion="comprobación automática", archivo_registro=None):
    inicio = time.perf_counter()
    ahora = datetime.now().replace(microsecond=0)
    carpeta = Path(carpeta)
    publicado = None
    if anterior is not None and Path(anterior["carpeta"]) == carpeta:   # nunca se mezclan origenes
        publicado = anterior["publicado"]

    # Estado del ciclo: "estado" y "mensaje" se completan en el try
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
    # Valida la calidad y, si no hay bloqueantes, publica los datos nuevos
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
            # Misma version que la publicada: SIN CAMBIOS
            if publicado is not None and publicado["version"] == version:
                estado["estado"] = SIN_CAMBIOS
                nuevo["actualizado"] = publicado["actualizado"]   # los datos son los mismos desde entonces
                estado["mensaje"] = "Los CSV no han cambiado: se han vuelto a leer, validar y calcular, con el mismo resultado."
            else:
                estado["estado"] = CORRECTO
                estado["mensaje"] = "Datos leídos, validados y publicados."
            estado["publicado"] = nuevo
    except Exception as error:
        estado["estado"] = ERROR_CARGA
        estado["mensaje"] = f"Error al procesar la exportación: {error}"

    # Los mensajes de error de lectura llevan la ruta completa de la carpeta: se deja la relativa
    for ruta in {str(carpeta), str(carpeta.resolve())}:
        estado["mensaje"] = estado["mensaje"].replace(ruta, carpeta_relativa(carpeta))
    # Si los datos nuevos fallan, se guarda lo publicado antes marcado como desactualizado
    # (el dashboard solo lo ensena si el usuario lo pide)
    estado["desactualizado"] = estado["publicado"] is not None and estado["estado"] in (DATOS_INVALIDOS, ERROR_CARGA)
    estado["duracion"] = round(time.perf_counter() - inicio, 2)
    try:
        anotar_ciclo(estado, operacion, archivo_registro)
    except OSError as error:
        estado["avisos"].append(f"No se ha podido escribir el registro de eventos: {error}")
    return estado


# Devuelve la ruta de una carpeta o archivo relativa a 04_Python (config.CARPETA_PROYECTO)
# Si esta fuera de 04_Python, devuelve solo su nombre
def carpeta_relativa(carpeta):
    try:
        return Path(carpeta).resolve().relative_to(config.CARPETA_PROYECTO).as_posix()
    except ValueError:
        return Path(carpeta).name


# Escribe el resultado del ciclo en el registro de eventos (una fila)
# Sin archivo_registro, usa el de config.py: logs/registro_eventos.csv
def anotar_ciclo(estado, operacion, archivo_registro=None):
    resultado = estado["calidad"]
    if resultado is None:
        # El ciclo ha fallado antes de evaluar la calidad: no hay filas ni incidencias
        incidencias = pd.DataFrame(columns=["gravedad"])
        leidas = 0
        validas = 0
    else:
        incidencias = resultado["incidencias"]
        leidas = sum(len(tabla) for tabla in resultado["datos"].values())
        validas = sum(len(tabla) for tabla in resultado["validos"].values())
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
