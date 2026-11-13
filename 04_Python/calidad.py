"""
Las doce reglas de calidad del apartado 6.2 de la rubrica.

Cada regla mira una cosa y apunta una INCIDENCIA por cada registro que la
incumple: regla, tabla, registro, fila, columna, valor original, gravedad,
tratamiento y explicacion.

Gravedad y tratamiento:
  bloqueante   el conjunto no se puede usar: no se publica ninguna cifra hasta
               que Acceso a Datos lo corrija y vuelva a exportar (apartado 6.14:
               CSV que falta, esquema incorrecto o clave huerfana).
  recuperable  la fila se RECHAZA: se aparta en filas_rechazadas.csv y no entra
               en los calculos. El resto de los datos sigue adelante.
  advertencia  la fila se queda en los calculos y la incidencia queda anotada.

Nunca se corrige ni se inventa un valor: un nulo no se convierte en 0, un
estado mal escrito no se arregla solo y no se borran duplicados sin saber que
identifica una fila.
"""
from pathlib import Path

import pandas as pd

import config
import pipeline

REGLAS = {
    "01": "Fichero vacío o cabeceras insuficientes",
    "02": "IDs duplicados donde deban ser únicos",
    "03": "Claves huérfanas en líneas o pedidos",
    "04": "Fecha nula o imposible",
    "05": "Cantidad nula, cero o negativa",
    "06": "Precio no numérico o negativo",
    "07": "Estado fuera del catálogo acordado",
    "08": "Talla no válida según el contrato",
    "09": "Ausencia de cliente o modelo",
    "10": "Duplicidad de líneas según clave documentada",
    "11": "Stock negativo o duplicado por modelo-talla",
    "12": "Conflicto entre fechas o incoherencia comercial",
}

BLOQUEANTE = "bloqueante"
RECUPERABLE = "recuperable"
ADVERTENCIA = "advertencia"

TRATAMIENTO = {
    BLOQUEANTE: "detener: no se publica ninguna cifra",
    RECUPERABLE: "rechazar la fila",
    ADVERTENCIA: "mantener la fila y avisar",
}

# Columna que identifica cada fila de cada tabla
CLAVE = {"clientes": "id_cliente", "modelos": "id_modelo", "pedidos": "id_pedido",
         "lineas_pedido": "id_linea", "stock": "sku"}

COLUMNAS_INCIDENCIA = ["regla", "nombre_regla", "tabla", "registro", "fila", "columna",
                       "valor", "gravedad", "tratamiento", "detalle"]


# ---------------------------------------------------------------------
# Ayudas
# ---------------------------------------------------------------------

def incidencia(regla, tabla, gravedad, detalle, registro="", fila="", columna="", valor=""):
    """Una incidencia: un diccionario con las columnas de incidencias.csv."""
    return {"regla": regla, "nombre_regla": REGLAS[regla], "tabla": tabla,
            "registro": registro, "fila": fila, "columna": columna, "valor": valor,
            "gravedad": gravedad, "tratamiento": TRATAMIENTO[gravedad], "detalle": detalle}


def original(textos, nombre, indice, columna):
    """El valor tal como venia en el CSV ("" si la celda estaba vacia)."""
    valor = textos[nombre].at[indice, columna]
    return "" if pd.isna(valor) else str(valor)


def por_filas(regla, nombre, datos, textos, mascara, columna, gravedad, detalle):
    """Una incidencia por cada fila de la tabla en la que la mascara es True."""
    lista = []
    # Un valor que no se pudo convertir da nulo en la comparacion: no cuenta aqui
    mascara = mascara.fillna(False).astype(bool)
    for indice in datos[nombre].index[mascara]:
        lista.append(incidencia(regla, nombre, gravedad, detalle,
                                registro=original(textos, nombre, indice, CLAVE[nombre]),
                                fila=indice + 1,   # fila 1 = la primera despues de la cabecera
                                columna=columna,
                                valor=original(textos, nombre, indice, columna)))
    return lista


def vacio_y_no_convertible(datos, textos, nombre, columna):
    """Dos mascaras: celda vacia, y valor que habia pero no se pudo convertir a su tipo."""
    texto = textos[nombre][columna]
    vacio = texto.isna()
    no_convertible = texto.notna() & datos[nombre][columna].isna()
    return vacio, no_convertible


# ---------------------------------------------------------------------
# Regla 01: se aplica al cargar los archivos
# ---------------------------------------------------------------------

def cargar(carpeta):
    """
    Lee los cinco CSV. Regla 01: un archivo que no existe, esta vacio, no es
    UTF-8, esta mal formado o no tiene las columnas obligatorias es bloqueante.
    Un archivo con solo la cabecera se puede leer: es una advertencia.

    Devuelve (datos convertidos, textos originales, incidencias, avisos de lectura).
    """
    carpeta = Path(carpeta)
    datos = {}
    textos = {}
    incidencias = []
    avisos = []
    for nombre, definicion in config.ARCHIVOS.items():
        ruta = carpeta / definicion["archivo"]
        try:
            texto = pipeline.leer_texto(ruta)
            datos[nombre], avisos_archivo = pipeline.preparar(texto, nombre, ruta.name)
            textos[nombre] = texto
            avisos.extend(avisos_archivo)
        except pipeline.ErrorDatos as error:
            incidencias.append(incidencia("01", nombre, BLOQUEANTE, str(error), registro=definicion["archivo"]))
            continue
        if len(texto) == 0:
            incidencias.append(incidencia("01", nombre, ADVERTENCIA, "solo tiene la cabecera, ninguna fila",
                                          registro=definicion["archivo"]))
    return datos, textos, incidencias, avisos


# ---------------------------------------------------------------------
# Reglas 02 a 12: necesitan los cinco archivos cargados
# ---------------------------------------------------------------------

def regla_02_ids_duplicados(datos, textos):
    """
    Cada identificador tiene que ser unico. Si se repite, un cruce multiplica
    filas y no se puede saber cual es la buena: bloqueante. Un identificador
    vacio no identifica la fila: se rechaza.
    """
    lista = []
    for nombre, columna in config.CLAVES_UNICAS:
        valores = datos[nombre][columna]
        repetido = valores.duplicated(keep=False) & valores.notna()
        lista += por_filas("02", nombre, datos, textos, repetido, columna, BLOQUEANTE,
                           f"{columna} repetido: aparece en más de una fila")
    for nombre, columna in CLAVE.items():
        lista += por_filas("02", nombre, datos, textos, datos[nombre][columna].isna(), columna, RECUPERABLE,
                           f"{columna} vacío: la fila no se puede identificar")
    return lista


def regla_03_claves_huerfanas(datos, textos):
    """
    Cada clave que une dos tablas tiene que existir en la otra. Una clave
    huerfana es una exportacion incompleta: bloqueante (apartado 6.14).
    """
    lista = []
    for hijos, columna, padres, columna_padre in config.RELACIONES:
        valores = datos[hijos][columna]
        huerfana = valores.notna() & ~valores.isin(datos[padres][columna_padre])
        lista += por_filas("03", hijos, datos, textos, huerfana, columna, BLOQUEANTE,
                           f"{columna} no existe en {padres}.csv")
    return lista


def regla_04_fechas(datos, textos):
    """Una fecha vacia o imposible (30 de febrero, otro formato) no se puede situar en el tiempo."""
    lista = []
    for nombre, columna in [("pedidos", "fecha_pedido"), ("stock", "fecha_corte")]:
        vacio, imposible = vacio_y_no_convertible(datos, textos, nombre, columna)
        lista += por_filas("04", nombre, datos, textos, vacio, columna, RECUPERABLE, f"{columna} vacía")
        lista += por_filas("04", nombre, datos, textos, imposible, columna, RECUPERABLE,
                           f"{columna} imposible o con otro formato (se espera AAAA-MM-DD HH:MM:SS)")
    return lista


def regla_05_cantidades(datos, textos):
    """Las cantidades son pares: enteros, y en una linea mayores que 0."""
    lista = []
    for nombre, columna in [("lineas_pedido", "cantidad"), ("pedidos", "cantidad_total")]:
        vacio, malo = vacio_y_no_convertible(datos, textos, nombre, columna)
        lista += por_filas("05", nombre, datos, textos, vacio, columna, RECUPERABLE, f"{columna} vacía")
        lista += por_filas("05", nombre, datos, textos, malo, columna, RECUPERABLE,
                           f"{columna} no es un número entero")
    lineas = datos["lineas_pedido"]
    lista += por_filas("05", "lineas_pedido", datos, textos, lineas["cantidad"] <= 0, "cantidad", RECUPERABLE,
                       "cantidad cero o negativa: una línea tiene al menos un par")
    pedidos = datos["pedidos"]
    lista += por_filas("05", "pedidos", datos, textos, pedidos["cantidad_total"] < 0, "cantidad_total", RECUPERABLE,
                       "cantidad_total negativa")
    return lista


def regla_06_precios(datos, textos):
    """
    Precios e importes: numeros con punto decimal y no negativos. El precio de
    catalogo (precio_base) no se usa para calcular ventas: solo se avisa.
    """
    lista = []
    columnas = [("lineas_pedido", "precio_unitario", RECUPERABLE),
                ("lineas_pedido", "importe_linea", RECUPERABLE),
                ("pedidos", "importe_total", RECUPERABLE),
                ("modelos", "precio_base", ADVERTENCIA)]
    for nombre, columna, gravedad in columnas:
        vacio, malo = vacio_y_no_convertible(datos, textos, nombre, columna)
        lista += por_filas("06", nombre, datos, textos, vacio, columna, gravedad, f"{columna} vacío")
        lista += por_filas("06", nombre, datos, textos, malo, columna, gravedad,
                           f"{columna} no es un número (se espera punto decimal y sin símbolo de moneda)")
        lista += por_filas("06", nombre, datos, textos, datos[nombre][columna] < 0, columna, gravedad,
                           f"{columna} negativo")
    return lista


def regla_07_estados(datos, textos):
    """
    Estados y tipos fuera del catalogo acordado (config.py). No se corrigen
    solos aunque solo cambie una mayuscula. Sin estado_pedido o tipo_pedido no
    se puede saber si un pedido es venta o si es Custom: se rechaza. El
    estado_pago y el tipo de cliente no se usan en los calculos: solo se avisa.
    """
    lista = []
    catalogos = [("pedidos", "estado_pedido", config.ESTADOS_PEDIDO, RECUPERABLE),
                 ("pedidos", "tipo_pedido", config.TIPOS_PEDIDO, RECUPERABLE),
                 ("pedidos", "estado_pago", config.ESTADOS_PAGO, ADVERTENCIA),
                 ("clientes", "tipo", config.TIPOS_CLIENTE, ADVERTENCIA)]
    for nombre, columna, permitidos, gravedad in catalogos:
        fuera = ~datos[nombre][columna].isin(permitidos)
        lista += por_filas("07", nombre, datos, textos, fuera, columna, gravedad,
                           f"{columna} fuera del catálogo: {', '.join(permitidos)}")
    return lista


def regla_08_tallas(datos, textos):
    """
    El contrato pide que la talla sea valida para el modelo: la talla de una
    linea tiene que ser la de su SKU en stock.csv. Ademas la base solo admite
    tallas entre TALLA_MINIMA y TALLA_MAXIMA. Las lineas X-NOVA no tienen SKU:
    solo se comprueba el rango.
    """
    lista = []
    for nombre in ["lineas_pedido", "stock"]:
        vacio, malo = vacio_y_no_convertible(datos, textos, nombre, "talla")
        talla = datos[nombre]["talla"]
        fuera_de_rango = (talla < config.TALLA_MINIMA) | (talla > config.TALLA_MAXIMA)
        lista += por_filas("08", nombre, datos, textos, vacio, "talla", RECUPERABLE, "talla vacía")
        lista += por_filas("08", nombre, datos, textos, malo, "talla", RECUPERABLE, "talla que no es un número entero")
        lista += por_filas("08", nombre, datos, textos, fuera_de_rango, "talla", RECUPERABLE,
                           f"talla fuera del rango de la base ({config.TALLA_MINIMA}-{config.TALLA_MAXIMA})")

    # Talla de cada SKU en stock.csv. Un SKU repetido ya lo apunta la regla 02;
    # aqui se usa su primera fila, porque map necesita una sola talla por SKU
    lineas = datos["lineas_pedido"]
    stock = datos["stock"].drop_duplicates("sku")
    talla_del_sku = lineas["sku"].map(stock.set_index("sku")["talla"])
    distinta = lineas["sku"].notna() & talla_del_sku.notna() & (lineas["talla"] != talla_del_sku)
    lista += por_filas("08", "lineas_pedido", datos, textos, distinta, "talla", RECUPERABLE,
                       "la talla de la línea no es la de su SKU en stock.csv")
    return lista


def regla_09_ausencia_cliente_modelo(datos, textos):
    """Un pedido sin cliente o una linea sin modelo no se pueden analizar. Un cliente o modelo sin nombre, se avisa."""
    lista = []
    # columna[3:] quita el prefijo "id_" para el mensaje: id_cliente -> cliente
    for nombre, columna in [("pedidos", "id_cliente"), ("lineas_pedido", "id_modelo"), ("stock", "id_modelo")]:
        lista += por_filas("09", nombre, datos, textos, datos[nombre][columna].isna(), columna, RECUPERABLE,
                           f"{columna} vacío: no se sabe de qué {columna[3:]} es")
    for nombre, columna in [("clientes", "nombre"), ("modelos", "nombre_modelo")]:
        lista += por_filas("09", nombre, datos, textos, datos[nombre][columna].isna(), columna, ADVERTENCIA,
                           f"{columna} vacío: existe el registro pero no se puede mostrar")
    return lista


def regla_10_lineas_duplicadas(datos, textos):
    """
    Clave documentada: el contrato dice que cada talla va en una linea, asi que
    en un pedido cada SKU aparece una sola vez (en X-NOVA, sin SKU: modelo y
    talla). La base no lo impide. Las dos lineas tienen su propio id e importe y
    el total del pedido las suma las dos, asi que no se borra ninguna: se avisa.
    """
    lineas = datos["lineas_pedido"]
    repetida = lineas.duplicated(subset=["id_pedido", "sku", "id_modelo", "talla"], keep=False)
    return por_filas("10", "lineas_pedido", datos, textos, repetida, "sku", ADVERTENCIA,
                     "el mismo SKU aparece en más de una línea del mismo pedido")


def regla_11_stock(datos, textos):
    """
    Stock vacio, que no es entero o negativo: se rechaza. La rubrica habla de
    duplicado por modelo-talla, pero aqui hay una fila por COLOR: la clave real
    es modelo + color + talla (el SKU). Si dos SKU distintos tienen el mismo
    modelo, color y talla, el stock se contaria dos veces: se rechazan los dos.
    """
    lista = []
    vacio, malo = vacio_y_no_convertible(datos, textos, "stock", "stock_disponible")
    stock = datos["stock"]
    lista += por_filas("11", "stock", datos, textos, vacio, "stock_disponible", RECUPERABLE, "stock vacío")
    lista += por_filas("11", "stock", datos, textos, malo, "stock_disponible", RECUPERABLE,
                       "stock que no es un número entero")
    lista += por_filas("11", "stock", datos, textos, stock["stock_disponible"] < 0, "stock_disponible", RECUPERABLE,
                       "stock negativo")
    repetida = stock.duplicated(subset=["id_modelo", "color", "talla"], keep=False)
    lista += por_filas("11", "stock", datos, textos, repetida, "sku", RECUPERABLE,
                       "otro SKU tiene el mismo modelo, color y talla: el stock se contaría dos veces")
    return lista


def huella_de_pedidos(lineas):
    """Para cada pedido, sus articulos y cantidades ordenados: 'NOVA-4-40 x10 | NOVA-4-41 x10 ...'."""
    # Una linea sin SKU (X-NOVA) se identifica por su modelo y su talla
    sin_sku = "modelo " + lineas["id_modelo"].fillna("?") + " talla " + lineas["talla"].astype(str)
    articulo = lineas["sku"].fillna(sin_sku)
    partes = articulo + " x" + lineas["cantidad"].astype(str)
    # Una linea con algun dato vacio (ya rechazada por otra regla) no rompe la huella
    partes = partes.fillna("línea incompleta")
    return partes.groupby(lineas["id_pedido"]).agg(lambda valores: " | ".join(sorted(valores)))


def comprobar_totales_pedido(datos, textos):
    """Compara los totales de cada cabecera con la suma de sus lineas."""
    lista = []
    pedidos = datos["pedidos"]
    lineas = datos["lineas_pedido"]
    suma = lineas.groupby("id_pedido").agg(pares=("cantidad", "sum"), importe=("importe_linea", "sum"))
    for indice, pedido in pedidos.iterrows():
        if pd.isna(pedido["id_pedido"]):
            continue   # ya lo apunta la regla 02
        if pedido["id_pedido"] in suma.index:
            pares = suma.at[pedido["id_pedido"], "pares"]
            importe = suma.at[pedido["id_pedido"], "importe"]
        else:
            # Sin lineas: 0 pares y 0 euros. Si su cabecera dice otra cosa, tampoco cuadra
            lista.append(incidencia("12", "pedidos", ADVERTENCIA, "pedido sin ninguna línea",
                                    registro=pedido["id_pedido"], fila=indice + 1))
            pares = 0
            importe = 0.0
        if pd.notna(pedido["cantidad_total"]) and pedido["cantidad_total"] != pares:
            lista.append(incidencia("12", "pedidos", RECUPERABLE,
                                    f"cantidad_total {pedido['cantidad_total']} y sus líneas suman {pares} pares",
                                    registro=pedido["id_pedido"], fila=indice + 1, columna="cantidad_total",
                                    valor=original(textos, "pedidos", indice, "cantidad_total")))
        if pd.notna(pedido["importe_total"]) and abs(pedido["importe_total"] - importe) > config.TOLERANCIA_EUROS:
            lista.append(incidencia("12", "pedidos", RECUPERABLE,
                                    f"importe_total {pedido['importe_total']:.2f} y sus líneas suman {importe:.2f} €",
                                    registro=pedido["id_pedido"], fila=indice + 1, columna="importe_total",
                                    valor=original(textos, "pedidos", indice, "importe_total")))
    return lista


def avisar_pedidos_repetidos(pedidos, lineas):
    """Coincidir en cliente y articulos solo genera un aviso; no elimina pedidos."""
    lista = []
    huellas = huella_de_pedidos(lineas)
    con_huella = pedidos.copy()
    con_huella["huella"] = pedidos["id_pedido"].map(huellas)
    con_huella = con_huella.dropna(subset=["huella"])
    for (cliente, huella), grupo in con_huella.groupby(["id_cliente", "huella"]):
        if len(grupo) > 1:
            for indice, pedido in grupo.iterrows():
                otras_referencias = grupo.loc[grupo.index != indice, "referencia"].fillna("?")
                otros = ", ".join(otras_referencias)
                lista.append(incidencia("12", "pedidos", ADVERTENCIA,
                                        f"mismo cliente y mismas líneas que {otros}: posible pedido repetido "
                                        f"(no se elimina; confirmar con Acceso a Datos)",
                                        registro=pedido["id_pedido"], fila=indice + 1, columna="referencia",
                                        valor=pedido["referencia"]))
    return lista


def regla_12_coherencia(datos, textos):
    """Comprueba fechas, importes, personalizacion y posibles pedidos repetidos."""
    lista = []
    pedidos = datos["pedidos"]
    lineas = datos["lineas_pedido"]
    stock = datos["stock"]

    fechas_corte = stock["fecha_corte"].dropna().unique()
    if len(fechas_corte) > 1:
        lista.append(incidencia("12", "stock", BLOQUEANTE,
                                f"stock.csv mezcla {len(fechas_corte)} fechas de corte distintas: no es una sola exportación",
                                registro="stock.csv", columna="fecha_corte"))
    if len(fechas_corte) > 0:
        corte = stock["fecha_corte"].max()
        lista += por_filas("12", "pedidos", datos, textos, pedidos["fecha_pedido"] > corte, "fecha_pedido", RECUPERABLE,
                           f"pedido posterior a la exportación ({corte:%Y-%m-%d %H:%M:%S})")

    calculado = (lineas["cantidad"] * lineas["precio_unitario"]).round(2)
    distinto = (calculado - lineas["importe_linea"]).abs() > config.TOLERANCIA_EUROS
    lista += por_filas("12", "lineas_pedido", datos, textos, distinto, "importe_linea", RECUPERABLE,
                       "importe_linea no es cantidad x precio_unitario")

    lista += comprobar_totales_pedido(datos, textos)

    custom_sin_texto = (pedidos["tipo_pedido"] == "custom") & pedidos["personalizacion"].isna()
    normal_con_texto = (pedidos["tipo_pedido"] == "normal") & pedidos["personalizacion"].notna()
    lista += por_filas("12", "pedidos", datos, textos, custom_sin_texto, "personalizacion", ADVERTENCIA,
                       "pedido custom sin descripción de la personalización")
    lista += por_filas("12", "pedidos", datos, textos, normal_con_texto, "personalizacion", ADVERTENCIA,
                       "pedido normal con personalización")
    reembolso_raro = (pedidos["estado_pago"] == "reembolsado") & (pedidos["estado_pedido"] != "cancelado")
    lista += por_filas("12", "pedidos", datos, textos, reembolso_raro, "estado_pago", ADVERTENCIA,
                       "pago reembolsado en un pedido que no está cancelado")

    lista += avisar_pedidos_repetidos(pedidos, lineas)
    return lista


REGLAS_CON_DATOS = [regla_02_ids_duplicados, regla_03_claves_huerfanas, regla_04_fechas,
                    regla_05_cantidades, regla_06_precios, regla_07_estados, regla_08_tallas,
                    regla_09_ausencia_cliente_modelo, regla_10_lineas_duplicadas, regla_11_stock,
                    regla_12_coherencia]


# ---------------------------------------------------------------------
# Separar filas validas y rechazadas, y resumen por tabla
# ---------------------------------------------------------------------

def separar(datos, incidencias):
    """
    Aparta las filas que tienen alguna incidencia que no es una advertencia.

    Un pedido se analiza entero o no se analiza: si se rechaza una linea, se
    rechaza su pedido con todas sus lineas, y si se rechaza un pedido, tambien
    sus lineas. Asi nunca se cuenta un pedido a medias.

    (Si hay una incidencia bloqueante no se publica nada, pero sus filas
    tambien se apartan aqui para que el resumen diga cuantas son.)

    Devuelve (validos: nombre -> DataFrame, rechazadas: DataFrame con el motivo).
    """
    motivos = {nombre: {} for nombre in datos}   # nombre -> {indice de fila: motivo}
    de_fila = incidencias[(incidencias["gravedad"] != ADVERTENCIA) & (incidencias["fila"] != "")]
    # setdefault: si una fila tiene varias incidencias, se queda el motivo de la primera
    for _, fila in de_fila.iterrows():
        motivos[fila["tabla"]].setdefault(fila["fila"] - 1, f"regla {fila['regla']}: {fila['detalle']}")

    pedidos = datos["pedidos"]
    lineas = datos["lineas_pedido"]
    # Pedidos que salen enteros: los rechazados y los que tienen alguna linea rechazada
    filas_pedidos = list(motivos["pedidos"])
    filas_lineas = list(motivos["lineas_pedido"])
    pedidos_fuera = set(pedidos.loc[filas_pedidos, "id_pedido"].dropna())
    pedidos_fuera.update(lineas.loc[filas_lineas, "id_pedido"].dropna())
    lista_fuera = list(pedidos_fuera)
    for indice in pedidos.index[pedidos["id_pedido"].isin(lista_fuera)]:
        motivos["pedidos"].setdefault(indice, "tiene una línea rechazada")
    for indice in lineas.index[lineas["id_pedido"].isin(lista_fuera)]:
        motivos["lineas_pedido"].setdefault(indice, "su pedido se ha rechazado")

    validos = {}
    filas_rechazadas = []
    for nombre, tabla in datos.items():
        validos[nombre] = tabla.drop(index=list(motivos[nombre]))
        for indice, motivo in sorted(motivos[nombre].items()):
            filas_rechazadas.append({"tabla": nombre, "fila": indice + 1,
                                     "registro": tabla.at[indice, CLAVE[nombre]], "motivo": motivo})
    rechazadas = pd.DataFrame(filas_rechazadas, columns=["tabla", "fila", "registro", "motivo"])
    return validos, rechazadas


def resumen_calidad(datos, validos, incidencias):
    """Una fila por tabla: filas de entrada, validas, rechazadas, % de calidad e incidencias por gravedad."""
    filas = []
    for nombre, definicion in config.ARCHIVOS.items():
        de_la_tabla = incidencias[incidencias["tabla"] == nombre]
        bloqueantes = int((de_la_tabla["gravedad"] == BLOQUEANTE).sum())
        if nombre not in validos:
            # El archivo no se ha podido cargar, o falta otro y no se ha evaluado
            if nombre in datos:
                estado = "sin evaluar"
                entrada = len(datos[nombre])
            else:
                estado = "no cargado"
                entrada = 0
            buenas = None
        else:
            entrada = len(datos[nombre])
            buenas = len(validos[nombre])
            if bloqueantes > 0:
                estado = "bloqueado"
            else:
                estado = "correcto"
        # Sin evaluar no hay filas rechazadas ni porcentaje (vacio, no 0)
        rechazadas = None
        porcentaje_calidad = None
        if buenas is not None:
            rechazadas = entrada - buenas
            if entrada > 0:
                porcentaje_calidad = round(100 * buenas / entrada, 1)
        filas.append({
            "tabla": nombre,
            "archivo": definicion["archivo"],
            "estado": estado,
            "filas_entrada": entrada,
            "filas_validas": buenas,
            "filas_rechazadas": rechazadas,
            "porcentaje_calidad": porcentaje_calidad,
            "bloqueantes": bloqueantes,
            "recuperables": int((de_la_tabla["gravedad"] == RECUPERABLE).sum()),
            "advertencias": int((de_la_tabla["gravedad"] == ADVERTENCIA).sum()),
        })
    return pd.DataFrame(filas)


def evaluar(carpeta):
    """
    Aplica las doce reglas a los CSV de la carpeta.

    Devuelve un diccionario con: datos, avisos, incidencias, validos,
    rechazadas, resumen y bloqueado (True si no se puede publicar nada).
    """
    datos, textos, lista, avisos = cargar(carpeta)
    cargados = len(datos) == len(config.ARCHIVOS)
    if cargados:
        for regla in REGLAS_CON_DATOS:
            lista += regla(datos, textos)

    # Las incidencias quedan en el orden en que se aplican las reglas, de la 01 a la 12
    incidencias = pd.DataFrame(lista, columns=COLUMNAS_INCIDENCIA)
    bloqueado = (not cargados) or bool((incidencias["gravedad"] == BLOQUEANTE).any())

    validos = {}
    rechazadas = pd.DataFrame(columns=["tabla", "fila", "registro", "motivo"])
    if cargados:
        validos, rechazadas = separar(datos, incidencias)
    return {
        "datos": datos,
        "avisos": avisos,
        "incidencias": incidencias,
        "validos": validos,
        "rechazadas": rechazadas,
        "resumen": resumen_calidad(datos, validos, incidencias),
        "bloqueado": bloqueado,
    }


def nulos_por_columna(datos):
    """
    Celdas vacias de cada columna (DataFrame 09, junto con resumen_calidad e
    incidencias). Cuenta tambien los valores que no se pudieron convertir.
    Que una columna opcional tenga vacios (telefono, personalizacion) es normal.
    """
    filas = []
    for nombre, tabla in datos.items():
        for columna in tabla.columns:
            nulos = int(tabla[columna].isna().sum())
            porcentaje_nulos = None
            if len(tabla) > 0:
                porcentaje_nulos = round(100 * nulos / len(tabla), 1)
            filas.append({
                "tabla": nombre,
                "columna": columna,
                "obligatoria": columna in config.ARCHIVOS[nombre]["obligatorias"],
                "nulos": nulos,
                "porcentaje_nulos": porcentaje_nulos,
            })
    return pd.DataFrame(filas)
