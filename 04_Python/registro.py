"""
Registro de eventos del procesamiento (apartados 6.12 y 6.17, paso 5).

Un solo archivo CSV (config.ARCHIVO_REGISTRO) al que se anade una fila por
operacion: la carga inicial de cada origen, cada comprobacion de 60 s, cada
actualizacion manual y cada descarga. No se crea un archivo nuevo en cada refresco.

Solo se anotan datos del proceso: momento, origen, operacion, resultado,
filas, incidencias, duracion y una explicacion. Nunca contrasenas, rutas
completas del ordenador ni datos de clientes (Python no maneja credenciales:
lee CSV ya exportados).
"""
import csv
from datetime import datetime
from pathlib import Path

import pandas as pd

import config

COLUMNAS = ["fecha_hora", "origen", "carpeta", "operacion", "resultado", "filas_procesadas", "filas_validas",
            "incidencias", "bloqueantes", "version_datos", "duracion_s", "detalle"]


def anotar(archivo, **campos):
    """Anade una fila al registro (y lo crea con su cabecera si no existe)."""
    archivo = Path(archivo)
    archivo.parent.mkdir(parents=True, exist_ok=True)
    nuevo = not archivo.exists()
    fila = {columna: campos.get(columna, "") for columna in COLUMNAS}
    if not fila["fecha_hora"]:
        fila["fecha_hora"] = datetime.now().strftime(config.FORMATO_FECHA)
    # El detalle en una sola linea: un salto de linea romperia la lectura
    fila["detalle"] = " ".join(str(fila["detalle"]).split())
    with open(archivo, "a", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS)
        if nuevo:
            escritor.writeheader()
        escritor.writerow(fila)


def leer(archivo, ultimas=100):
    """Las ultimas filas del registro, de la mas reciente a la mas antigua."""
    archivo = Path(archivo)
    if not archivo.exists():
        return pd.DataFrame(columns=COLUMNAS)
    tabla = pd.read_csv(archivo, encoding="utf-8", dtype=str, keep_default_na=False)
    ultimas_filas = tabla.tail(ultimas)
    de_la_mas_reciente = ultimas_filas.iloc[::-1]   # [::-1] da la vuelta al orden de las filas
    return de_la_mas_reciente.reset_index(drop=True)
