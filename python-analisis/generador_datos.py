"""
Generador de datos SINTETICOS (apartado 5 de la rubrica).

Crea un historico INVENTADO de 18 meses con las MISMAS columnas que los cinco
CSV de Acceso a Datos, para poder practicar estadistica, segmentacion y
prediccion con suficientes datos. No son datos reales: todo lo que sale de
aqui lleva "Tipo: SINTETICO" en su ORIGEN.txt y nunca se guarda en entrada_acc/.

Hipotesis de la simulacion (inventadas: NO describen la demanda real de NOVA):
  - 40 clientes: 10 empresas (clubes) y 30 particulares. Unos compran mas que
    otros (peso 1 / posicion^0,7).
  - 12 modelos con distinta popularidad: el modelo 1 es el mas pedido
    (peso 1 / posicion). Precios de catalogo entre 69,99 y 139,99 euros.
  - 2 colores por modelo y tallas de la 38 a la 46; las centrales (41-43) se
    piden mas (PESO_TALLAS).
  - Mas pedidos en primavera y en septiembre-octubre (temporada deportiva) y
    menos en agosto y enero (PESO_MES_DEL_ANIO), con un crecimiento del 2 % al mes.
  - 15 % de pedidos Custom: casi siempre de clubes, un solo modelo y color en
    2 a 5 tallas, de 5 a 20 pares por talla y un recargo del 20 % en el precio.
  - Los pedidos normales tienen 1 a 3 lineas de 1 a 3 pares.
  - Los precios suben un 5 % en enero de 2026 (el catalogo tiene el precio nuevo).
  - El estado depende de la antiguedad del pedido; el 8 % se cancela. El pago
    depende del estado (un pedido entregado esta pagado).

Los datos limpios cumplen todas las reglas de calidad. Aparte se guarda una
copia con errores introducidos a proposito (errores_introducidos.csv dice cuales).

Con la misma semilla salen siempre exactamente los mismos datos.

En Windows, desde la carpeta python-analisis:
    .venv\\Scripts\\python.exe generador_datos.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import config

PRIMER_MES = "2025-05"            # 18 meses seguidos: de mayo de 2025 a octubre de 2026
NUMERO_MESES = 18
FECHA_CORTE = "2026-11-01 00:00:00"
NUMERO_CLIENTES = 40
NUMERO_EMPRESAS = 10
NUMERO_PEDIDOS = 900
NOMBRES_MODELOS = ["Runner", "Court", "Trail", "Street", "Classic", "Flex",
                   "Sprint", "Urban", "Peak", "Wave", "Volt", "Retro"]
COLORES = ["Negro", "Blanco", "Rojo", "Azul", "Gris", "Verde"]
TALLAS = [38, 39, 40, 41, 42, 43, 44, 45, 46]
PESO_TALLAS = [0.03, 0.06, 0.11, 0.17, 0.20, 0.18, 0.13, 0.08, 0.04]
PESO_MES_DEL_ANIO = {1: 0.7, 2: 0.8, 3: 1.1, 4: 1.3, 5: 1.3, 6: 1.0,
                     7: 0.8, 8: 0.6, 9: 1.2, 10: 1.3, 11: 1.0, 12: 1.1}
CRECIMIENTO_MENSUAL = 0.02
PROPORCION_CUSTOM = 0.15
RECARGO_CUSTOM = 0.20
MES_SUBIDA_PRECIOS = "2026-01"
SUBIDA_PRECIOS = 0.05
PROPORCION_CANCELADOS = 0.08
PERSONALIZACIONES = ["Logo del club y dorsal", "Iniciales en el talón", "Colores del club"]


def normalizar(pesos):
    """Convierte unos pesos en probabilidades que suman 1."""
    pesos = np.array(pesos, dtype=float)
    return pesos / pesos.sum()


def colores_del_modelo(id_modelo):
    """Dos colores por modelo, siempre los mismos."""
    return [COLORES[(id_modelo - 1) % len(COLORES)], COLORES[(id_modelo + 2) % len(COLORES)]]


def codigo_sku(id_modelo, color, talla):
    """Por ejemplo S01-NEG-42: modelo 1, color negro, talla 42."""
    return f"S{id_modelo:02d}-{color[:3].upper()}-{talla}"


def generar_clientes():
    filas = []
    for numero in range(1, NUMERO_CLIENTES + 1):
        empresa = numero <= NUMERO_EMPRESAS
        filas.append({
            "id_cliente": numero,
            "nombre": f"Club sintético {numero:02d}" if empresa else f"Cliente sintético {numero:02d}",
            "tipo": "empresa" if empresa else "particular",
            "correo": f"cliente{numero:02d}@sintetico.example.com",
            "telefono": f"600{numero:06d}" if empresa else "",
            "activo": "true",
        })
    return pd.DataFrame(filas)


def generar_modelos(rng):
    precios = rng.integers(7, 15, size=len(NOMBRES_MODELOS)) * 10 - 0.01   # de 69,99 a 139,99 euros
    filas = []
    for numero, (nombre, precio) in enumerate(zip(NOMBRES_MODELOS, precios), start=1):
        filas.append({
            "id_modelo": numero,
            "nombre_modelo": f"SINT {nombre}",
            "descripcion": "Modelo inventado para el histórico sintético",
            "precio_base": round(float(precio), 2),
            "activo": "true",
        })
    return pd.DataFrame(filas)


def generar_stock(rng, modelos):
    """Una fila por SKU (modelo + color + talla), con un stock entre 0 y 60 pares."""
    filas = []
    for id_modelo in modelos["id_modelo"]:
        for color in colores_del_modelo(id_modelo):
            for talla in TALLAS:
                filas.append({
                    "sku": codigo_sku(id_modelo, color, talla),
                    "id_modelo": id_modelo,
                    "color": color,
                    "talla": talla,
                    "activo": "true",
                    "stock_disponible": int(rng.integers(0, 61)),
                    "fecha_corte": FECHA_CORTE,
                })
    return pd.DataFrame(filas)


def generar_fechas(rng):
    """
    Fecha y hora de cada pedido. Primero se reparte el numero de pedidos entre
    los 18 meses segun la estacionalidad y el crecimiento; despues, dentro de
    cada mes, el dia y la hora son al azar.
    """
    meses = pd.period_range(PRIMER_MES, periods=NUMERO_MESES, freq="M")
    pesos = [PESO_MES_DEL_ANIO[mes.month] * (1 + CRECIMIENTO_MENSUAL) ** numero for numero, mes in enumerate(meses)]
    pedidos_por_mes = rng.multinomial(NUMERO_PEDIDOS, normalizar(pesos))
    fechas = []
    for mes, cuantos in zip(meses, pedidos_por_mes):
        for _ in range(cuantos):
            dia = int(rng.integers(1, mes.days_in_month + 1))
            fechas.append(pd.Timestamp(mes.year, mes.month, dia, int(rng.integers(9, 21)), int(rng.integers(0, 60))))
    return sorted(fechas)


def elegir_articulos(rng, custom, ids_modelos, peso_modelos):
    """
    Las lineas de un pedido, como (id_modelo, color, talla, cantidad).
    Nunca hay dos lineas con el mismo SKU: el contrato dice una linea por talla.
    """
    if custom:
        # Un club pide un modelo y un color en varias tallas distintas
        id_modelo = int(rng.choice(ids_modelos, p=peso_modelos))
        color = str(rng.choice(colores_del_modelo(id_modelo)))
        tallas = rng.choice(TALLAS, size=int(rng.integers(2, 6)), replace=False, p=PESO_TALLAS)
        return [(id_modelo, color, int(talla), int(rng.integers(5, 21))) for talla in sorted(tallas)]

    cuantas = int(rng.choice([1, 2, 3], p=[0.45, 0.40, 0.15]))
    articulos = []
    usados = set()
    while len(articulos) < cuantas:
        id_modelo = int(rng.choice(ids_modelos, p=peso_modelos))
        color = str(rng.choice(colores_del_modelo(id_modelo)))
        talla = int(rng.choice(TALLAS, p=PESO_TALLAS))
        if codigo_sku(id_modelo, color, talla) not in usados:
            usados.add(codigo_sku(id_modelo, color, talla))
            articulos.append((id_modelo, color, talla, int(rng.choice([1, 2, 3], p=[0.65, 0.28, 0.07]))))
    return articulos


def elegir_estado(rng, fecha, corte):
    """El 8 % se cancela; el resto avanza segun los dias que han pasado hasta el corte."""
    if rng.random() < PROPORCION_CANCELADOS:
        return "cancelado"
    dias = (corte - fecha).days
    if dias > 30:
        return "entregado"
    if dias > 14:
        return str(rng.choice(["enviado", "entregado"]))
    if dias > 7:
        return str(rng.choice(["confirmado", "en_preparacion", "enviado"]))
    return str(rng.choice(["pendiente", "confirmado"]))


def elegir_estado_pago(rng, estado):
    """Entregado: pagado. Cancelado: reembolsado o pendiente. Pendiente: pendiente."""
    if estado == "entregado":
        return "pagado"
    if estado in ("confirmado", "en_preparacion", "enviado"):
        return "pagado" if rng.random() < 0.7 else "pendiente"
    if estado == "cancelado":
        return "reembolsado" if rng.random() < 0.5 else "pendiente"
    return "pendiente"


def precio_en_fecha(precio_actual, fecha, custom):
    """El catalogo tiene el precio de ahora; antes de la subida era un 5 % mas bajo. Custom: +20 %."""
    precio = precio_actual
    if fecha < pd.Timestamp(MES_SUBIDA_PRECIOS + "-01"):
        precio = precio_actual / (1 + SUBIDA_PRECIOS)
    if custom:
        precio = precio * (1 + RECARGO_CUSTOM)
    return round(precio, 2)


def generar_pedidos(rng, clientes, modelos):
    corte = pd.Timestamp(FECHA_CORTE)
    precios = dict(zip(modelos["id_modelo"], modelos["precio_base"]))
    ids_modelos = modelos["id_modelo"].tolist()
    peso_modelos = normalizar([1 / posicion for posicion in range(1, len(ids_modelos) + 1)])
    empresas = clientes.loc[clientes["tipo"] == "empresa", "id_cliente"].tolist()
    particulares = clientes.loc[clientes["tipo"] == "particular", "id_cliente"].tolist()
    peso_empresas = normalizar([1 / posicion ** 0.7 for posicion in range(1, len(empresas) + 1)])
    peso_particulares = normalizar([1 / posicion ** 0.7 for posicion in range(1, len(particulares) + 1)])

    huellas = set()   # (cliente, articulos): ningun cliente repite exactamente el mismo pedido
    pedidos = []
    lineas = []
    id_linea = 0
    for id_pedido, fecha in enumerate(generar_fechas(rng), start=1):
        custom = rng.random() < PROPORCION_CUSTOM
        de_empresa = rng.random() < (0.8 if custom else 0.15)
        if de_empresa:
            cliente = int(rng.choice(empresas, p=peso_empresas))
        else:
            cliente = int(rng.choice(particulares, p=peso_particulares))
        while True:
            articulos = elegir_articulos(rng, custom, ids_modelos, peso_modelos)
            huella = (cliente, tuple(sorted((codigo_sku(m, c, t), q) for m, c, t, q in articulos)))
            if huella not in huellas:
                huellas.add(huella)
                break

        estado = elegir_estado(rng, fecha, corte)
        cantidad_total = 0
        importe_total = 0.0
        for id_modelo, color, talla, cantidad in articulos:
            id_linea += 1
            precio = precio_en_fecha(precios[id_modelo], fecha, custom)
            importe = round(cantidad * precio, 2)
            lineas.append({
                "id_linea": id_linea,
                "id_pedido": id_pedido,
                "sku": codigo_sku(id_modelo, color, talla),
                "id_modelo": id_modelo,
                "talla": talla,
                "cantidad": cantidad,
                "precio_unitario": precio,
                "importe_linea": importe,
            })
            cantidad_total += cantidad
            importe_total += importe

        pedidos.append({
            "id_pedido": id_pedido,
            "referencia": f"SINT-{id_pedido:04d}",
            "id_cliente": cliente,
            "fecha_pedido": fecha.strftime(config.FORMATO_FECHA),
            "tipo_pedido": "custom" if custom else "normal",
            "estado_pedido": estado,
            "estado_pago": elegir_estado_pago(rng, estado),
            "personalizacion": str(rng.choice(PERSONALIZACIONES)) if custom else "",
            "cantidad_total": cantidad_total,
            "importe_total": round(importe_total, 2),
        })
    return pd.DataFrame(pedidos), pd.DataFrame(lineas)


def generar(semilla=config.SEMILLA):
    """Los cinco conjuntos sinteticos, con las columnas en el orden del contrato."""
    rng = np.random.default_rng(semilla)
    clientes = generar_clientes()
    modelos = generar_modelos(rng)
    stock = generar_stock(rng, modelos)
    pedidos, lineas = generar_pedidos(rng, clientes, modelos)
    datos = {"clientes": clientes, "modelos": modelos, "pedidos": pedidos, "lineas_pedido": lineas, "stock": stock}
    return {nombre: tabla[list(config.ARCHIVOS[nombre]["tipos"])] for nombre, tabla in datos.items()}


# ---------------------------------------------------------------------
# Copia con errores introducidos a proposito
# ---------------------------------------------------------------------

def como_texto(tabla):
    """Todo a texto, como en el CSV (euros con 2 decimales), para poder meter valores erroneos."""
    texto = tabla.copy()
    for columna in texto.columns:
        if pd.api.types.is_float_dtype(texto[columna]):
            texto[columna] = texto[columna].map(lambda valor: f"{valor:.2f}")
        else:
            texto[columna] = texto[columna].astype(str)
    return texto


def introducir_errores(datos):
    """
    Una copia de los datos con al menos un fallo de cada regla de la 02 a la 12.
    La regla 01 (archivo vacio o sin columnas) no se puede mezclar aqui: si un
    archivo no se puede leer, las demas reglas no se aplican. Se prueba aparte.

    Devuelve (copia, DataFrame con cada error y lo que deberia detectar).
    """
    copia = {nombre: como_texto(tabla) for nombre, tabla in datos.items()}
    pedidos = copia["pedidos"]
    lineas = copia["lineas_pedido"]
    stock = copia["stock"]
    errores = []

    def anotar(regla, tabla, registro, cambio, se_espera):
        errores.append({"regla": regla, "tabla": tabla, "registro": registro, "cambio": cambio,
                        "se_espera": se_espera})

    # 02: un pedido repetido con el mismo id_pedido (y otra referencia)
    repetido = pedidos.iloc[[5]].copy()
    repetido["referencia"] = "SINT-REPETIDO"
    anotar("02", "pedidos", repetido["id_pedido"].iloc[0], "fila añadida con un id_pedido que ya existe",
           "02 bloqueante en las dos filas; 12 advertencia de posible pedido repetido")
    # 03: una linea de un pedido que no existe
    huerfana = lineas.iloc[[0]].copy()
    huerfana["id_linea"] = "999999"
    huerfana["id_pedido"] = "99999"
    anotar("03", "lineas_pedido", "999999", "línea añadida del pedido 99999, que no existe", "03 bloqueante")
    # 10: una linea repetida (mismo pedido y mismo SKU) sin cambiar el total del pedido
    repetida = lineas.iloc[[80]].copy()
    repetida["id_linea"] = "999998"
    anotar("10", "lineas_pedido", "999998", f"copia de la línea {lineas.at[80, 'id_linea']} (mismo pedido y SKU)",
           "10 advertencia en las dos líneas; 12 porque el total del pedido ya no es la suma")

    def cambiar(regla, tabla, nombre_tabla, fila, columna, valor, se_espera):
        anterior = tabla.at[fila, columna]
        tabla.at[fila, columna] = valor
        clave = config.ARCHIVOS[nombre_tabla]["tipos"]
        registro = tabla.at[fila, next(iter(clave))]
        anotar(regla, nombre_tabla, registro, f"{columna}: '{anterior}' pasa a '{valor}'", se_espera)

    entregado = pedidos.index[(pedidos["estado_pedido"] == "entregado") & (pedidos.index > 70)][0]
    talla = int(lineas.at[60, "talla"])
    cambiar("04", pedidos, "pedidos", 10, "fecha_pedido", "2026-02-30 10:00:00", "04 recuperable (fecha imposible)")
    cambiar("05", lineas, "lineas_pedido", 20, "cantidad", "0", "05 recuperable; 12 (importe de línea y total)")
    cambiar("06", lineas, "lineas_pedido", 40, "precio_unitario", "-" + lineas.at[40, "precio_unitario"],
            "06 recuperable; 12 (importe de línea)")
    cambiar("07", pedidos, "pedidos", entregado, "estado_pedido", "Entregado", "07 recuperable (mayúscula)")
    cambiar("08", lineas, "lineas_pedido", 60, "talla", str(talla + 1 if talla < 46 else talla - 1),
            "08 recuperable (no es la talla de su SKU)")
    cambiar("09", pedidos, "pedidos", 40, "id_cliente", "", "09 recuperable (pedido sin cliente)")
    cambiar("11", stock, "stock", 10, "stock_disponible", "-5", "11 recuperable (stock negativo)")
    cambiar("12", pedidos, "pedidos", 50, "importe_total", f"{float(pedidos.at[50, 'importe_total']) + 10:.2f}",
            "12 recuperable (el total no es la suma de sus líneas)")
    cambiar("12", pedidos, "pedidos", 60, "fecha_pedido", "2027-01-15 10:00:00",
            "12 recuperable (pedido posterior a la exportación)")

    copia["pedidos"] = pd.concat([pedidos, repetido], ignore_index=True)
    copia["lineas_pedido"] = pd.concat([lineas, huerfana, repetida], ignore_index=True)
    return copia, pd.DataFrame(errores)


# ---------------------------------------------------------------------
# Guardar
# ---------------------------------------------------------------------

def guardar(datos, carpeta, descripcion):
    """
    Escribe los cinco CSV como los exporta Acceso a Datos (UTF-8, coma, punto
    decimal, cabecera) y un ORIGEN.txt con "Tipo: SINTETICO".
    Se niega a escribir en entrada_acc/: alli solo van exportaciones de PostgreSQL.
    """
    carpeta = Path(carpeta).resolve()
    entrada = config.CARPETA_ENTRADA.resolve()
    if carpeta == entrada or entrada in carpeta.parents:
        raise ValueError("Los datos sintéticos nunca se guardan en entrada_acc/: "
                         "allí solo van exportaciones de Acceso a Datos")
    carpeta.mkdir(parents=True, exist_ok=True)
    for nombre, tabla in datos.items():
        tabla.to_csv(carpeta / config.ARCHIVOS[nombre]["archivo"], index=False, encoding="utf-8",
                     float_format="%.2f", lineterminator="\n")
    (carpeta / config.ARCHIVO_ORIGEN).write_text(f"Tipo: SINTETICO\n{descripcion}\n", encoding="utf-8")
    return carpeta


def main():
    datos = generar(config.SEMILLA)
    descripcion = (f"Datos INVENTADOS por generador_datos.py con la semilla {config.SEMILLA}: "
                   f"{NUMERO_MESES} meses desde {PRIMER_MES}, corte {FECHA_CORTE}. "
                   "No son datos de NOVA ni salen de PostgreSQL.")
    guardar(datos, config.CARPETA_SINTETICOS_LIMPIOS, descripcion)
    con_errores, errores = introducir_errores(datos)
    carpeta = guardar(con_errores, config.CARPETA_SINTETICOS_ERRORES,
                      descripcion + " COPIA CON ERRORES introducidos a propósito (ver errores_introducidos.csv).")
    errores.to_csv(carpeta / "errores_introducidos.csv", index=False, encoding="utf-8")

    print(f"Datos sintéticos (semilla {config.SEMILLA}) en {config.CARPETA_SINTETICOS}")
    for nombre, tabla in datos.items():
        print(f"  {nombre:15} {len(tabla):>5} filas")
    meses = pd.to_datetime(datos["pedidos"]["fecha_pedido"]).dt.to_period("M")
    print(f"  meses con pedidos: {meses.nunique()} ({meses.min()} a {meses.max()})")
    print(f"  copia con errores: {len(errores)} errores introducidos ({carpeta / 'errores_introducidos.csv'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
