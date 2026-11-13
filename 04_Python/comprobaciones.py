"""
Comprobaciones iniciales de la fase 1: que los cinco CSV se han leido bien
y que tienen sentido juntos.

OJO: NO son las doce reglas de calidad del apartado 6.2 de la rubrica.
Esas reglas (con gravedad, tratamiento, incidencias.csv...) son de la fase 2.
Aqui solo se mira si los datos estan bien preparados para empezar.

Cada comprobacion devuelve un diccionario:
    {"comprobacion": ..., "resultado": "OK" | "AVISO" | "ERROR", "detalle": ...}
"""
import config


def resultado(nombre, estado, detalle):
    return {"comprobacion": nombre, "resultado": estado, "detalle": detalle}


def comprobar_conversiones(avisos):
    """Todos los valores se han podido convertir a su tipo."""
    if not avisos:
        return resultado("Tipos de datos", "OK", "todos los valores se han convertido a su tipo")
    return resultado("Tipos de datos", "AVISO", f"{len(avisos)} valores no se han podido convertir (ver avisos)")


def comprobar_columnas(datos):
    """Las columnas son las que exporta 16_exportar_csv_dashboard.sql, en el mismo orden."""
    diferencias = []
    for nombre, definicion in config.ARCHIVOS.items():
        esperadas = list(definicion["tipos"])
        reales = list(datos[nombre].columns)
        faltan = [columna for columna in esperadas if columna not in reales]
        sobran = [columna for columna in reales if columna not in esperadas]
        if faltan:
            diferencias.append(f"{definicion['archivo']} no trae {', '.join(faltan)}")
        if sobran:
            diferencias.append(f"{definicion['archivo']} trae columnas nuevas: {', '.join(sobran)}")
        if not faltan and not sobran and reales != esperadas:
            diferencias.append(f"{definicion['archivo']} tiene las columnas en otro orden")
    if diferencias:
        return resultado("Columnas del exportador", "AVISO", "; ".join(diferencias))
    total = 0
    for definicion in config.ARCHIVOS.values():
        total += len(definicion["tipos"])
    return resultado("Columnas del exportador", "OK", f"las {total} columnas esperadas, en su orden")


def comprobar_codificacion(datos):
    """
    Si un archivo no fuera UTF-8, leer_csv ya habria parado. Aqui se buscan
    restos de una conversion mal hecha antes de exportar: el caracter de
    sustitucion (�) o "Ã" (lo que sale al leer "ñ" o "é" con otra codificacion).
    """
    sospechosos = []
    for nombre, tabla in datos.items():
        for columna in tabla.columns:
            if config.ARCHIVOS[nombre]["tipos"].get(columna) == "texto":
                texto = tabla[columna].dropna().astype(str)
                malos = texto[texto.str.contains("�|Ã", regex=True)]
                if len(malos) > 0:
                    sospechosos.append(f"{nombre}.{columna}: {len(malos)} valores")
    if sospechosos:
        return resultado("Codificación UTF-8", "ERROR", "texto mal codificado en " + "; ".join(sospechosos))
    return resultado("Codificación UTF-8", "OK", "leídos como UTF-8, sin caracteres mal convertidos")


def comprobar_claves_unicas(datos):
    """Cada identificador aparece una sola vez en su tabla."""
    repetidas = []
    for nombre, columna in config.CLAVES_UNICAS:
        valores = datos[nombre][columna]
        duplicados = valores[valores.duplicated()].unique()
        if len(duplicados) > 0:
            repetidas.append(f"{nombre}.{columna}: {', '.join(map(str, duplicados))}")
    if repetidas:
        return resultado("Claves únicas", "ERROR", "repetidas: " + "; ".join(repetidas))
    return resultado("Claves únicas", "OK", "ningún identificador repetido")


def sin_pareja(hijos, columna, padres, columna_padre):
    """Valores de hijos[columna] que no existen en padres[columna_padre] (los vacios no cuentan)."""
    valores = hijos[columna].dropna()
    return valores[~valores.isin(padres[columna_padre])].unique()


def comprobar_relaciones(datos):
    """Las claves que unen las tablas apuntan a algo que existe."""
    huerfanas = []
    for hijos, columna, padres, columna_padre in config.RELACIONES:
        perdidas = sin_pareja(datos[hijos], columna, datos[padres], columna_padre)
        if len(perdidas) > 0:
            huerfanas.append(f"{hijos}.{columna} sin pareja en {padres}: {', '.join(map(str, perdidas))}")
    if huerfanas:
        return resultado("Relaciones entre tablas", "ERROR", "; ".join(huerfanas))
    return resultado("Relaciones entre tablas", "OK", f"las {len(config.RELACIONES)} relaciones encuentran su pareja")


def comprobar_pedidos_con_lineas(datos):
    """Un pedido sin lineas no deberia existir: ACC crea el pedido con su primera linea."""
    sin_lineas = sin_pareja(datos["pedidos"], "id_pedido", datos["lineas_pedido"], "id_pedido")
    if len(sin_lineas) > 0:
        return resultado("Pedidos con líneas", "AVISO", f"pedidos sin líneas: {', '.join(map(str, sin_lineas))}")
    return resultado("Pedidos con líneas", "OK", "todos los pedidos tienen al menos una línea")


def comprobar_importes_y_cantidades(datos):
    """
    Las cantidades y los importes se han leido como numeros y cuadran:
    - cantidades mayores que 0 y stock no negativo
    - importe_linea = cantidad x precio_unitario
    - cantidad_total e importe_total del pedido = suma de sus lineas
    """
    lineas = datos["lineas_pedido"]
    pedidos = datos["pedidos"]
    problemas = []

    if (lineas["cantidad"] <= 0).any():
        problemas.append("hay líneas con cantidad 0 o negativa")
    if (lineas["precio_unitario"] < 0).any():
        problemas.append("hay precios negativos")
    if (datos["stock"]["stock_disponible"] < 0).any():
        problemas.append("hay stock negativo")

    # Los euros se comparan redondeados a centimos. Un valor que no se pudo
    # convertir da nulo; ya salio en los avisos, asi que aqui no cuenta (fillna).
    calculado = (lineas["cantidad"] * lineas["precio_unitario"]).round(2)
    diferencia = (calculado - lineas["importe_linea"]).abs()
    distinto = (diferencia > config.TOLERANCIA_EUROS).fillna(False)
    mal_calculadas = lineas.loc[distinto, "id_linea"]
    if len(mal_calculadas) > 0:
        problemas.append(f"importe_linea no es cantidad x precio en las líneas {', '.join(mal_calculadas)}")

    # Suma de las lineas de cada pedido, comparada con su cabecera
    suma = lineas.groupby("id_pedido").agg(pares=("cantidad", "sum"), importe=("importe_linea", "sum"))
    cruce = pedidos.merge(suma, how="left", left_on="id_pedido", right_index=True)
    cruce = cruce.fillna({"pares": 0, "importe": 0})
    pares_distintos = cruce["pares"] != cruce["cantidad_total"]
    importe_distinto = (cruce["importe"] - cruce["importe_total"]).abs() > config.TOLERANCIA_EUROS
    distinto = (pares_distintos | importe_distinto).fillna(False)
    no_cuadran = cruce.loc[distinto, "id_pedido"]
    if len(no_cuadran) > 0:
        problemas.append(f"el total no es la suma de sus líneas en los pedidos {', '.join(no_cuadran)}")

    if problemas:
        return resultado("Importes y cantidades", "ERROR", "; ".join(problemas))
    return resultado("Importes y cantidades", "OK",
                     f"{len(pedidos)} pedidos y {len(lineas)} líneas cuadran: "
                     f"{int(lineas['cantidad'].sum())} pares y {lineas['importe_linea'].sum():.2f} €")


def comprobar_periodo(datos):
    """Cuantos meses distintos cubren los pedidos. No es un error: avisa para el analisis temporal."""
    fechas = datos["pedidos"]["fecha_pedido"].dropna()
    if len(fechas) == 0:
        return resultado("Periodo de los pedidos", "AVISO", "no hay ninguna fecha de pedido válida")
    meses = fechas.dt.to_period("M").nunique()
    detalle = f"del {fechas.min():%Y-%m-%d} al {fechas.max():%Y-%m-%d}, {meses} mes(es) distinto(s)"
    if meses < 2:
        return resultado("Periodo de los pedidos", "AVISO",
                         detalle + ": no hay historial para series mensuales con estos datos")
    return resultado("Periodo de los pedidos", "OK", detalle)


def comprobar_todo(datos, avisos):
    """Lanza todas las comprobaciones iniciales, en orden."""
    return [
        comprobar_conversiones(avisos),
        comprobar_columnas(datos),
        comprobar_codificacion(datos),
        comprobar_claves_unicas(datos),
        comprobar_relaciones(datos),
        comprobar_pedidos_con_lineas(datos),
        comprobar_importes_y_cantidades(datos),
        comprobar_periodo(datos),
    ]
