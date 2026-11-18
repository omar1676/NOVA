import csv
from datetime import datetime
from pathlib import Path

import pandas as pd

import config

# Columnas del registro de eventos
COLUMNAS = ["fecha_hora", "origen", "carpeta", "operacion", "resultado", "filas_procesadas", "filas_validas",
            "incidencias", "bloqueantes", "version_datos", "duracion_s", "detalle"]


# Anade una fila al registro (si el CSV no existe, lo crea con la cabecera)
def anotar(archivo, **campos):
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


# Lee las ultimas filas del registro, de la mas reciente a la mas antigua
def leer(archivo, ultimas=100):
    archivo = Path(archivo)
    if not archivo.exists():
        return pd.DataFrame(columns=COLUMNAS)
    tabla = pd.read_csv(archivo, encoding="utf-8", dtype=str, keep_default_na=False)
    ultimas_filas = tabla.tail(ultimas)
    de_la_mas_reciente = ultimas_filas.iloc[::-1]   # [::-1] da la vuelta al orden de las filas
    return de_la_mas_reciente.reset_index(drop=True)
