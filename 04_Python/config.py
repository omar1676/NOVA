from pathlib import Path

# Las rutas son relativas a esta carpeta, asi funciona en cualquier ordenador
CARPETA_PROYECTO = Path(__file__).resolve().parent
CARPETA_ENTRADA = CARPETA_PROYECTO / "entrada_acc"

# Carpeta donde se guardan los resultados
CARPETA_SALIDA = CARPETA_PROYECTO / "outputs"

# Archivo que dice de que base salen los CSV: PRUEBA, REAL o SINTETICO
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

# Los cinco CSV: nombre del archivo, tipo de cada columna y columnas obligatorias
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
                         "estado_pedido", "estado_pago", "personalizacion", "cantidad_total", "importe_total"],
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

# Columnas que no se pueden repetir en su tabla: (tabla, columna)
CLAVES_UNICAS = [("clientes", "id_cliente"), ("modelos", "id_modelo"), ("pedidos", "id_pedido"),
                 ("pedidos", "referencia"), ("lineas_pedido", "id_linea"), ("stock", "sku")]

# Claves ajenas: (tabla hija, columna, tabla padre, columna del padre)
RELACIONES = [
    ("pedidos", "id_cliente", "clientes", "id_cliente"),
    ("lineas_pedido", "id_pedido", "pedidos", "id_pedido"),
    ("lineas_pedido", "id_modelo", "modelos", "id_modelo"),
    ("lineas_pedido", "sku", "stock", "sku"),
    ("stock", "id_modelo", "modelos", "id_modelo"),
]

# Fase 2: catalogos y criterios de las reglas de calidad y del analisis

# Valores permitidos en los estados y los tipos
ESTADOS_PEDIDO = ["pendiente", "confirmado", "en_preparacion", "enviado", "entregado", "cancelado"]
ESTADOS_PAGO = ["pendiente", "pagado", "reembolsado"]
TIPOS_PEDIDO = ["normal", "custom"]
TIPOS_CLIENTE = ["particular", "empresa"]

# Rango de tallas aceptado
TALLA_MINIMA = 20
TALLA_MAXIMA = 55

# Demanda: todo menos cancelado. Venta: confirmado en adelante
ESTADOS_CANCELADOS = ["cancelado"]
ESTADOS_CONFIRMADOS = ["confirmado", "en_preparacion", "enviado", "entregado"]

# Ni el contrato ni el esquema dicen si los importes llevan IVA
IVA = "pendiente de confirmar"

# Diferencia maxima para dar por iguales dos importes en euros (medio centimo)
TOLERANCIA_EUROS = 0.005

# Fase 3: KPIs, DataFrames analiticos y graficos

ESTADO_PAGADO = "pagado"

# Stock bajo: un SKU con menos de 10 pares
UMBRAL_STOCK_BAJO = 10

# Dias de pedidos que se usan para la demanda reciente y la cobertura
DIAS_DEMANDA = 28

# Clasificacion ABC: A hasta el 80 % acumulado de pares, B hasta el 95 %, C el resto
ABC_LIMITE_A = 80
ABC_LIMITE_B = 95

# Concentracion de Pareto: que parte de los pares se lleva el 20 % de los modelos
PARETO_PORCENTAJE = 20

# Atipicos por IQR (DataFrame 10): solo con grupos de al menos 5 valores
MINIMO_MUESTRA_IQR = 5

# Fase 4: datos sinteticos y estadistica

# Semilla fija: lo aleatorio sale siempre igual en cada ejecucion
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

# Fase 5: segmentacion RFM, KMeans y prediccion de demanda

# Con menos clientes no se segmenta
MINIMO_CLIENTES_RFM = 10
MINIMO_CLIENTES_KMEANS = 10
KMEANS_K = [2, 3, 4, 5]          # numeros de grupos que se prueban

# Prediccion: los ultimos 3 meses se reservan para evaluar; hacen falta 12 meses completos
MESES_EVALUACION = 3
MINIMO_MESES_PREDICCION = 12

# Fase 6: dashboard Streamlit

# Cada cuantos segundos el dashboard vuelve a leer, validar y recalcular todo
SEGUNDOS_REFRESCO = 60

# Registro de eventos: una fila por cada comprobacion de los datos
CARPETA_LOGS = CARPETA_PROYECTO / "logs"
ARCHIVO_REGISTRO = CARPETA_LOGS / "registro_eventos.csv"

# Avisos: CSV de hace mas de 24 h o escritos con mas de 10 minutos de diferencia
HORAS_EXPORTACION_ANTIGUA = 24
MINUTOS_EXPORTACION_INCOMPLETA = 10
