"""
Configuracion del analisis: carpetas, formato de los CSV y columnas.

Todo lo que puede cambiar esta aqui, y no repartido por el codigo.
Las columnas son las que exporta Acceso a Datos con
02_Acceso_Datos/sql/16_exportar_csv_dashboard.sql (ver diccionario_datos.md).
"""
from pathlib import Path

# Las rutas son relativas a esta carpeta, asi funciona en cualquier ordenador
CARPETA_PROYECTO = Path(__file__).resolve().parent
CARPETA_ENTRADA = CARPETA_PROYECTO / "entrada_acc"

CARPETA_SALIDA = CARPETA_PROYECTO / "outputs"

# Archivo opcional en la carpeta de entrada que dice de donde salen los CSV.
# Su linea "Tipo:" dice que clase de datos son. Nunca se mezclan sin avisar.
ARCHIVO_ORIGEN = "ORIGEN.txt"
TIPOS_ORIGEN = {
    "PRUEBA": "ACC · PRUEBA (base de prueba: no son ventas reales)",
    "REAL": "ACC · REAL (base del equipo)",
    "SINTETICO": "SINTÉTICO (generado por Python: no son datos reales)",
}

# Resultados de las consultas SQL de Acceso a Datos para la conciliacion
CARPETA_SQL = "conciliacion_sql"   # dentro de la carpeta de entrada

# Formato de los CSV de Acceso a Datos
SEPARADOR = ","
CODIFICACION = "utf-8-sig"          # UTF-8; tambien acepta el BOM que anade Excel
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"  # 2026-11-09 19:12:52

# Tipos de columna:
#   "id"       identificador: se queda como texto, nunca se suma ni se promedia
#   "texto"    texto libre
#   "entero"   numero entero (pares, tallas)
#   "decimal"  numero con punto decimal (euros)
#   "fecha"    fecha y hora con FORMATO_FECHA
#   "logico"   true / false
#
# "tipos" lleva todas las columnas que exporta Acceso a Datos, en su orden.
# "obligatorias" son las que hacen falta para unir las tablas y analizar:
# si falta una, el archivo no se puede usar.
ARCHIVOS = {
    "clientes": {
        "archivo": "clientes.csv",
        "tipos": {
            "id_cliente": "id",
            "nombre": "texto",
            "tipo": "texto",
            "correo": "texto",
            "telefono": "texto",
            "activo": "logico",
        },
        "obligatorias": ["id_cliente", "nombre", "tipo", "activo"],
    },
    "modelos": {
        "archivo": "modelos.csv",
        "tipos": {
            "id_modelo": "id",
            "nombre_modelo": "texto",
            "descripcion": "texto",
            "precio_base": "decimal",
            "activo": "logico",
        },
        "obligatorias": ["id_modelo", "nombre_modelo", "precio_base", "activo"],
    },
    "pedidos": {
        "archivo": "pedidos.csv",
        "tipos": {
            "id_pedido": "id",
            "referencia": "texto",
            "id_cliente": "id",
            "fecha_pedido": "fecha",
            "tipo_pedido": "texto",
            "estado_pedido": "texto",
            "estado_pago": "texto",
            "personalizacion": "texto",
            "cantidad_total": "entero",
            "importe_total": "decimal",
        },
        "obligatorias": ["id_pedido", "referencia", "id_cliente", "fecha_pedido", "tipo_pedido",
                         "estado_pedido", "estado_pago", "cantidad_total", "importe_total"],
    },
    "lineas_pedido": {
        "archivo": "lineas_pedido.csv",
        "tipos": {
            "id_linea": "id",
            "id_pedido": "id",
            "sku": "id",
            "id_modelo": "id",
            "talla": "entero",
            "cantidad": "entero",
            "precio_unitario": "decimal",
            "importe_linea": "decimal",
        },
        "obligatorias": ["id_linea", "id_pedido", "sku", "id_modelo", "talla", "cantidad",
                         "precio_unitario", "importe_linea"],
    },
    "stock": {
        "archivo": "stock.csv",
        "tipos": {
            "sku": "id",
            "id_modelo": "id",
            "color": "texto",
            "talla": "entero",
            "activo": "logico",
            "stock_disponible": "entero",
            "fecha_corte": "fecha",
        },
        "obligatorias": ["sku", "id_modelo", "color", "talla", "stock_disponible", "fecha_corte"],
    },
}

# ---------------------------------------------------------------------
# Fase 2: catalogos y criterios de las reglas de calidad y del analisis
# ---------------------------------------------------------------------

# Catalogos acordados: los CHECK de PostgreSQL y el diccionario de Acceso a
# Datos. Se comparan tal cual: "Pendiente" con mayuscula esta fuera.
# (El contrato de integracion lista 5 estados; la base tiene tambien
# en_preparacion, y es la base la que exporta.)
ESTADOS_PEDIDO = ["pendiente", "confirmado", "en_preparacion", "enviado", "entregado", "cancelado"]
ESTADOS_PAGO = ["pendiente", "pagado", "reembolsado"]
TIPOS_PEDIDO = ["normal", "custom"]
TIPOS_CLIENTE = ["particular", "empresa"]

# Tallas. El contrato pide que "el modelo y la talla solicitados sean
# validos": la talla de cada linea tiene que ser la de su SKU en stock.csv.
# Ademas, la base solo admite tallas entre 20 y 55 (CHECK de producto_sku).
TALLA_MINIMA = 20
TALLA_MAXIMA = 55

# Criterios para contar ventas (apartado 6.5). El equipo tiene que elegir uno
# y decirlo en la memoria. Ninguno significa "cobrado": eso es estado_pago.
ESTADOS_CANCELADOS = ["cancelado"]
# "Confirmados o entregados" incluye los estados intermedios: si no, un pedido
# dejaria de contar como venta al pasar de confirmado a en_preparacion.
ESTADOS_CONFIRMADOS = ["confirmado", "en_preparacion", "enviado", "entregado"]

# Ni el contrato ni el esquema dicen si los importes llevan IVA
IVA = "pendiente de confirmar"

# Diferencia maxima para dar por iguales dos importes en euros (medio centimo)
TOLERANCIA_EUROS = 0.005

# ---------------------------------------------------------------------
# Fase 3: KPIs, DataFrames analiticos y graficos
# ---------------------------------------------------------------------

# Tres poblaciones distintas. Cada KPI y cada tabla dice cual usa.
#   demanda  pedidos no cancelados: lo que los clientes piden y siguen
#            queriendo (criterio del panel P-A de Acceso a Datos). Se usa para
#            modelos, tallas, matrices y ABC: es lo que hay que fabricar.
#   venta    pedidos confirmados en adelante (ESTADOS_CONFIRMADOS, apartado
#            6.5): importe vendido, ticket medio y precio medio por par.
#   pagado   estado_pago = "pagado": lo que Acceso a Datos marca como pagado.
#            No es un cobro comprobado ni lleva IVA (pendiente de confirmar).
ESTADO_PAGADO = "pagado"

# Stock bajo: menos de este numero de pares, igual que el panel de Java y la
# consulta C8 de Acceso a Datos
UMBRAL_STOCK_BAJO = 10

# Cobertura de stock (apartado 6.15, DataFrame 08): demanda de los ultimos 28
# dias. Solo se calcula si el historial de pedidos cubre esos 28 dias enteros.
DIAS_DEMANDA = 28

# Clasificacion ABC de modelos por pares demandados: A hasta el 80 % acumulado,
# B hasta el 95 %, C el resto
ABC_LIMITE_A = 80
ABC_LIMITE_B = 95

# Concentracion de Pareto: que parte de los pares se lleva el 20 % de los modelos
PARETO_PORCENTAJE = 20

# Atipicos por IQR (DataFrame 10): solo con grupos de al menos 5 valores
MINIMO_MUESTRA_IQR = 5

# ---------------------------------------------------------------------
# Fase 4: datos sinteticos y estadistica
# ---------------------------------------------------------------------

# Una sola semilla para todo lo aleatorio: el generador y el bootstrap.
# Misma semilla -> mismos datos y mismos resultados.
SEMILLA = 2026

# Datos sinteticos: carpeta propia, nunca dentro de entrada_acc/
CARPETA_SINTETICOS = CARPETA_PROYECTO / "datos_sinteticos"
CARPETA_SINTETICOS_LIMPIOS = CARPETA_SINTETICOS / "limpios"
CARPETA_SINTETICOS_ERRORES = CARPETA_SINTETICOS / "con_errores"

# Bootstrap (apartado 6.7): cuantas muestras nuevas se sacan y nivel de confianza
BOOTSTRAP_REMUESTREOS = 2000
NIVEL_CONFIANZA = 95

# Con menos valores que estos, una comparacion no se hace: evidencia insuficiente
MINIMO_MUESTRA_HIPOTESIS = 5
# Con menos de estos, se hace pero se avisa de que el intervalo es poco fiable
MUESTRA_PEQUENA = 30

# ---------------------------------------------------------------------
# Fase 5: segmentacion RFM, KMeans y prediccion de demanda
# ---------------------------------------------------------------------

# RFM y KMeans necesitan al menos estos clientes CON compras validas. Con
# menos, los quintiles y los grupos no significan nada: NO CALCULABLE.
MINIMO_CLIENTES_RFM = 10
MINIMO_CLIENTES_KMEANS = 10
KMEANS_K = [2, 3, 4, 5]          # numeros de grupos que se prueban

# Prediccion: los ultimos 3 meses se reservan para evaluar. Hacen falta al
# menos 12 meses: 3 para tener el historial de los primeros, 6 para entrenar
# y 3 para evaluar.
MESES_EVALUACION = 3
MINIMO_MESES_PREDICCION = 12

# ---------------------------------------------------------------------
# Fase 6: dashboard Streamlit
# ---------------------------------------------------------------------

# Cada cuantos segundos el dashboard vuelve a leer, validar y recalcular todo
SEGUNDOS_REFRESCO = 60

# Registro de eventos: un solo CSV al que se anade una fila por operacion
# (no un archivo por refresco). Git ignora la carpeta logs/.
CARPETA_LOGS = CARPETA_PROYECTO / "logs"
ARCHIVO_REGISTRO = CARPETA_LOGS / "registro_eventos.csv"

# Avisos sobre la exportacion: una exportacion de hace mas de estas horas se
# avisa como antigua, y si los cinco CSV se escribieron con mas de estos
# minutos de diferencia, puede que no sean de la misma exportacion
HORAS_EXPORTACION_ANTIGUA = 24
MINUTOS_EXPORTACION_INCOMPLETA = 10
