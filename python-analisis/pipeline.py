"""
Lectura y validacion de los cinco CSV que exporta Acceso a Datos.

Este modulo solo LEE los archivos: nunca los modifica ni los sobrescribe.

Cada CSV se lee primero entero como texto y despues cada columna se
convierte a su tipo de forma explicita (config.py). Si un valor no se puede
convertir, por ejemplo "dos" en una cantidad, no se pierde en silencio:
queda vacio y se apunta un aviso con su fila y su columna.
"""
from datetime import datetime
from pathlib import Path

import pandas as pd

import config


class ErrorDatos(Exception):
    """Un CSV que no se puede usar: no existe, esta vacio, esta roto o le falta una columna."""


def leer_csv(ruta, nombre):
    """
    Lee uno de los cinco CSV del contrato.

    nombre es la clave de config.ARCHIVOS ("clientes", "pedidos"...).
    Devuelve (DataFrame, lista de avisos). Lanza ErrorDatos si no se puede usar.
    """
    ruta = Path(ruta)
    return preparar(leer_texto(ruta), nombre, ruta.name)


def leer_texto(ruta):
    """
    Lee el CSV tal cual, todo como texto, sin convertir nada. Solo comprueba
    que el archivo existe, no esta vacio, es UTF-8 y es un CSV correcto.
    Las reglas de calidad lo usan para ensenar el valor ORIGINAL de cada celda.
    """
    ruta = Path(ruta)
    if not ruta.exists():
        raise ErrorDatos(f"No existe el archivo {ruta.name} en {ruta.parent}")
    if ruta.stat().st_size == 0:
        raise ErrorDatos(f"El archivo {ruta.name} está vacío (0 bytes)")

    # Todo como texto (dtype=str) y solo la celda vacia como nulo: asi pandas
    # no adivina tipos ni convierte "NA" o "null" en nulos por su cuenta.
    try:
        datos = pd.read_csv(ruta, sep=config.SEPARADOR, encoding=config.CODIFICACION,
                            dtype=str, keep_default_na=False, na_values=[""])
    except UnicodeDecodeError:
        raise ErrorDatos(f"El archivo {ruta.name} no está en UTF-8")
    except pd.errors.EmptyDataError:
        raise ErrorDatos(f"El archivo {ruta.name} no tiene cabecera ni datos")
    except pd.errors.ParserError as error:
        raise ErrorDatos(f"El archivo {ruta.name} no es un CSV correcto: {error}")

    # Si la primera fila trae un valor mas que la cabecera, pandas no da error:
    # usa la primera columna como indice y desplaza todos los datos. Se detecta
    # porque el indice deja de ser el normal (0, 1, 2...).
    if not isinstance(datos.index, pd.RangeIndex):
        raise ErrorDatos(f"El archivo {ruta.name} no es un CSV correcto: "
                         f"tiene filas con más valores que columnas en la cabecera")
    return datos


def preparar(texto, nombre, archivo):
    """
    Comprueba las columnas obligatorias y convierte cada columna a su tipo.

    No cambia el DataFrame de texto que recibe: trabaja sobre una copia.
    Devuelve (DataFrame convertido, lista de avisos).
    """
    definicion = config.ARCHIVOS[nombre]
    datos = texto.copy()

    faltan = [columna for columna in definicion["obligatorias"] if columna not in datos.columns]
    if faltan:
        mensaje = f"A {archivo} le faltan columnas obligatorias: {', '.join(faltan)}"
        # Una sola columna con ";" dentro: casi seguro que el separador no es la coma
        if len(datos.columns) == 1 and ";" in datos.columns[0]:
            mensaje += ". Parece que usa ';' como separador en lugar de ','"
        raise ErrorDatos(mensaje)

    avisos = []
    if len(datos) == 0:
        avisos.append(f"{archivo}: solo tiene la cabecera, ninguna fila")

    for columna, tipo in definicion["tipos"].items():
        if columna in datos.columns:
            convertidos, fallidos = convertir(datos[columna], tipo)
            datos[columna] = convertidos
            for fila, valor in fallidos.items():
                # fila 1 = la primera despues de la cabecera
                avisos.append(f"{archivo}, fila {fila + 1}, columna {columna}: "
                              f"'{valor}' no es un valor {tipo} válido")
    return datos, avisos


def convertir(valores, tipo):
    """
    Convierte una columna de texto a su tipo.

    Devuelve la columna convertida y los valores que no se han podido
    convertir (una Serie con el indice de su fila).
    """
    if tipo == "entero":
        numeros = pd.to_numeric(valores, errors="coerce")
        # 42.5 se lee como numero, pero no es un entero valido
        convertidos = numeros.where(numeros % 1 == 0).astype("Int64")
    elif tipo == "decimal":
        convertidos = pd.to_numeric(valores, errors="coerce")
    elif tipo == "fecha":
        convertidos = pd.to_datetime(valores, format=config.FORMATO_FECHA, errors="coerce")
    elif tipo == "logico":
        convertidos = valores.map({"true": True, "false": False}).astype("boolean")
    else:
        # "id" y "texto" se quedan como texto
        convertidos = valores.astype("string")

    # Fallo = habia un valor y despues de convertir ya no lo hay
    fallidos = valores[valores.notna() & convertidos.isna()]
    return convertidos, fallidos


def cargar_todos(carpeta=config.CARPETA_ENTRADA):
    """
    Lee los cinco CSV de la carpeta.

    Devuelve (diccionario nombre -> DataFrame, lista de avisos). Si algun
    archivo no se puede usar, lanza ErrorDatos con TODOS los problemas: no
    se analiza nunca con los datos a medias.
    """
    carpeta = Path(carpeta)
    datos = {}
    avisos = []
    errores = []
    for nombre, definicion in config.ARCHIVOS.items():
        try:
            datos[nombre], avisos_archivo = leer_csv(carpeta / definicion["archivo"], nombre)
            avisos.extend(avisos_archivo)
        except ErrorDatos as error:
            errores.append(str(error))
    if errores:
        raise ErrorDatos("No se pueden cargar los datos:\n  - " + "\n  - ".join(errores))
    return datos, avisos


def manifiesto(carpeta, datos):
    """
    Manifiesto de origen: una fila por archivo con sus filas, columnas,
    tamaño y fecha de modificacion, y el momento del analisis.
    """
    carpeta = Path(carpeta)
    ahora = datetime.now().strftime(config.FORMATO_FECHA)
    filas = []
    for nombre, definicion in config.ARCHIVOS.items():
        ruta = carpeta / definicion["archivo"]
        modificado = datetime.fromtimestamp(ruta.stat().st_mtime).strftime(config.FORMATO_FECHA)
        filas.append({
            "archivo": definicion["archivo"],
            "filas": len(datos[nombre]),
            "columnas": len(datos[nombre].columns),
            "bytes": ruta.stat().st_size,
            "modificado": modificado,
            "analizado": ahora,
        })
    return pd.DataFrame(filas)


def leer_origen(carpeta):
    """Texto de ORIGEN.txt, si existe: quien exporto los CSV y desde que base."""
    ruta = Path(carpeta) / config.ARCHIVO_ORIGEN
    if not ruta.exists():
        return "(no hay ORIGEN.txt: no se sabe de qué base salen estos CSV)"
    return ruta.read_text(encoding="utf-8").strip()


def tipo_origen(carpeta):
    """
    Clase de datos segun la linea "Tipo:" de ORIGEN.txt: PRUEBA, REAL o
    SINTETICO (config.TIPOS_ORIGEN). DESCONOCIDO si no se dice.
    """
    ruta = Path(carpeta) / config.ARCHIVO_ORIGEN
    if ruta.exists():
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if linea.lower().startswith("tipo:"):
                tipo = linea.split(":", 1)[1].strip().upper()
                if tipo in config.TIPOS_ORIGEN:
                    return tipo
    return "DESCONOCIDO"


def etiqueta_origen(carpeta):
    """Texto que acompana a cada resultado, p. ej. 'ACC · PRUEBA (base de prueba: ...)'."""
    tipo = tipo_origen(carpeta)
    return config.TIPOS_ORIGEN.get(tipo, "DESCONOCIDO (no hay línea 'Tipo:' en ORIGEN.txt)")


def guardar_salida(tabla, archivo, carpeta_salida, carpeta_entrada, origen, ejecucion):
    """
    Guarda un resultado en CSV UTF-8 con cabecera. Las dos primeras columnas
    dicen de donde salen los datos y cuando se calculo (linaje).

    Nunca escribe en la carpeta de entrada: los CSV de Acceso a Datos no se tocan.
    """
    carpeta_salida = Path(carpeta_salida)
    if carpeta_salida.resolve() == Path(carpeta_entrada).resolve():
        raise ErrorDatos("No se escribe nunca en la carpeta de entrada: los CSV de Acceso a Datos no se tocan")
    carpeta_salida.mkdir(parents=True, exist_ok=True)
    salida = tabla.copy()
    salida.insert(0, "origen", origen)
    salida.insert(1, "ejecucion", ejecucion)
    ruta = carpeta_salida / archivo
    salida.to_csv(ruta, index=False, encoding="utf-8")
    return ruta


# Columnas con datos personales que no hacen falta para analizar: nunca se descargan
COLUMNAS_PERSONALES = ["nombre_cliente", "nombre", "correo", "telefono"]


def sin_datos_personales(tabla):
    """La tabla sin nombres, correos ni telefonos de clientes."""
    return tabla.drop(columns=[columna for columna in COLUMNAS_PERSONALES if columna in tabla.columns])


def csv_descarga(tabla, origen, ejecucion, filtros):
    """
    El CSV (UTF-8, con cabecera) de una tabla del dashboard. Lleva el mismo
    linaje que guardar_salida (origen y momento del calculo) y ademas los
    filtros con los que se ha calculado. Devuelve los bytes del archivo.
    """
    salida = sin_datos_personales(tabla).copy()
    salida.insert(0, "origen", origen)
    salida.insert(1, "ejecucion", ejecucion)
    salida.insert(2, "filtros", filtros)
    return salida.to_csv(index=False).encode("utf-8")
