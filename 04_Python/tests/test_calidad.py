import hashlib

import pandas as pd

import calidad
import pipeline
from test_pipeline import VALIDOS, PruebaConCarpeta


# Base de las pruebas de calidad: ayudas para cambiar los CSV y leer el resultado
class PruebaCalidad(PruebaConCarpeta):

    # Cambia un trozo de un CSV valido
    def cambiar(self, archivo, antes, despues):
        texto = VALIDOS[archivo]
        self.assertIn(antes, texto)   # la prueba tiene que cambiar algo que existe
        self.escribir(archivo, texto.replace(antes, despues))

    # Anade filas al final de un CSV valido
    def anadir(self, archivo, filas):
        self.escribir(archivo, VALIDOS[archivo] + filas)

    def evaluar(self):
        return calidad.evaluar(self.carpeta)

    # Incidencias de una regla
    def de_la_regla(self, resultado, regla):
        incidencias = resultado["incidencias"]
        return incidencias[incidencias["regla"] == regla]

    # Registros rechazados de una tabla
    def rechazadas(self, resultado, tabla):
        rechazadas = resultado["rechazadas"]
        return set(rechazadas.loc[rechazadas["tabla"] == tabla, "registro"])


# Datos validos
class PruebasSinIncidencias(PruebaCalidad):

    # Los CSV validos no dan ninguna incidencia (100 % de calidad)
    def test_datos_validos_sin_incidencias(self):
        resultado = self.evaluar()
        self.assertEqual(len(resultado["incidencias"]), 0)
        self.assertFalse(resultado["bloqueado"])
        self.assertEqual(resultado["resumen"]["porcentaje_calidad"].tolist(), [100.0] * 5)


# Regla 01: archivo que falta, vacio o con columnas de menos
class PruebasRegla01(PruebaCalidad):

    # Falta stock.csv: bloqueante, y el resto queda sin evaluar
    def test_archivo_que_falta(self):
        (self.carpeta / "stock.csv").unlink()
        resultado = self.evaluar()
        r01 = self.de_la_regla(resultado, "01")
        self.assertEqual(r01["tabla"].tolist(), ["stock"])
        self.assertEqual(r01["gravedad"].tolist(), ["bloqueante"])
        self.assertTrue(resultado["bloqueado"])
        estados = dict(zip(resultado["resumen"]["tabla"], resultado["resumen"]["estado"]))
        self.assertEqual(estados["stock"], "no cargado")
        self.assertEqual(estados["pedidos"], "sin evaluar")

    # Archivo de 0 bytes
    def test_archivo_vacio(self):
        self.escribir("clientes.csv", "")
        r01 = self.de_la_regla(self.evaluar(), "01")
        self.assertIn("vacío", r01["detalle"].iloc[0])

    # Falta una columna obligatoria (precio_base)
    def test_falta_columna(self):
        self.escribir("modelos.csv", "id_modelo,nombre_modelo\n1,Uno\n2,Dos\n")
        r01 = self.de_la_regla(self.evaluar(), "01")
        self.assertIn("precio_base", r01["detalle"].iloc[0])

    # Solo la cabecera: es una advertencia, no bloquea
    def test_solo_cabecera_es_advertencia(self):
        self.escribir("lineas_pedido.csv", "id_linea,id_pedido,sku,id_modelo,talla,cantidad,precio_unitario,importe_linea\n")
        resultado = self.evaluar()
        r01 = self.de_la_regla(resultado, "01")
        self.assertEqual(r01["gravedad"].tolist(), ["advertencia"])
        self.assertFalse(resultado["bloqueado"])
        # Sus pedidos dicen tener pares que no estan en ninguna linea: se rechazan (regla 12)
        self.assertEqual(self.rechazadas(resultado, "pedidos"), {"10", "11"})


# Regla 02: identificadores repetidos o vacios
class PruebasRegla02(PruebaCalidad):

    # Un id_pedido repetido bloquea, y se marca en las dos filas
    def test_pedido_duplicado_por_id(self):
        self.anadir("pedidos.csv", "10,P-3,1,2026-10-05 10:00:00,normal,pendiente,pendiente,,0,0.00\n")
        resultado = self.evaluar()
        r02 = self.de_la_regla(resultado, "02")
        repetidos = r02[r02["columna"] == "id_pedido"]
        self.assertEqual(repetidos["fila"].tolist(), [1, 3])        # las dos filas con el 10
        self.assertEqual(set(repetidos["gravedad"]), {"bloqueante"})
        self.assertTrue(resultado["bloqueado"])

    # Un id vacio solo rechaza su fila
    def test_id_vacio_se_rechaza(self):
        self.cambiar("lineas_pedido.csv", "101,10,M1-41", ",10,M1-41")
        resultado = self.evaluar()
        r02 = self.de_la_regla(resultado, "02")
        self.assertEqual(r02["gravedad"].tolist(), ["recuperable"])
        self.assertFalse(resultado["bloqueado"])


# Regla 03: claves huerfanas
class PruebasRegla03(PruebaCalidad):

    # Con los CSV validos no hay ninguna
    def test_relaciones_validas(self):
        self.assertEqual(len(self.de_la_regla(self.evaluar(), "03")), 0)

    # Linea de un pedido que no existe: bloqueante
    def test_linea_huerfana(self):
        self.anadir("lineas_pedido.csv", "103,99,M1-40,1,40,1,79.99,79.99\n")
        resultado = self.evaluar()
        r03 = self.de_la_regla(resultado, "03")
        self.assertEqual(r03["registro"].tolist(), ["103"])
        self.assertEqual(r03["valor"].tolist(), ["99"])
        self.assertEqual(r03["gravedad"].tolist(), ["bloqueante"])
        self.assertTrue(resultado["bloqueado"])

    # Pedido de un cliente que no existe
    def test_pedido_con_cliente_que_no_existe(self):
        self.cambiar("pedidos.csv", "11,P-2,2,", "11,P-2,9,")
        r03 = self.de_la_regla(self.evaluar(), "03")
        self.assertEqual(r03["columna"].tolist(), ["id_cliente"])

    # Linea con un SKU que no esta en stock.csv
    def test_sku_que_no_esta_en_stock(self):
        self.cambiar("lineas_pedido.csv", "102,11,M2-42", "102,11,M9-42")
        r03 = self.de_la_regla(self.evaluar(), "03")
        self.assertIn("stock.csv", r03["detalle"].iloc[0])


# Regla 04: fechas
class PruebasRegla04(PruebaCalidad):

    # 30 de febrero: se rechaza el pedido y se guarda el valor original
    def test_fecha_imposible(self):
        self.cambiar("pedidos.csv", "2026-11-02 12:30:00", "2026-02-30 12:30:00")
        resultado = self.evaluar()
        r04 = self.de_la_regla(resultado, "04")
        self.assertEqual(r04["valor"].tolist(), ["2026-02-30 12:30:00"])   # el valor original
        self.assertEqual(r04["gravedad"].tolist(), ["recuperable"])
        self.assertIn("11", self.rechazadas(resultado, "pedidos"))

    # Fecha de corte vacia en stock.csv
    def test_fecha_vacia(self):
        self.cambiar("stock.csv", "M2-42,2,Negro,42,true,12,2026-11-09 19:00:00", "M2-42,2,Negro,42,true,12,")
        r04 = self.de_la_regla(self.evaluar(), "04")
        self.assertIn("vacía", r04["detalle"].iloc[0])


# Regla 05: cantidades
class PruebasRegla05(PruebaCalidad):

    # Cantidad 0, negativa o escrita con letras
    def test_cantidad_cero_negativa_o_texto(self):
        for valor, texto in [("0", "cero o negativa"), ("-1", "cero o negativa"), ("dos", "no es un número entero")]:
            with self.subTest(valor=valor):
                self.cambiar("lineas_pedido.csv", "100,10,M1-40,1,40,1,", f"100,10,M1-40,1,40,{valor},")
                r05 = self.de_la_regla(self.evaluar(), "05")
                self.assertEqual(r05["registro"].tolist(), ["100"])
                self.assertIn(texto, r05["detalle"].iloc[0])

    # Una linea mala deja fuera su pedido entero
    def test_un_pedido_se_analiza_entero_o_no_se_analiza(self):
        self.cambiar("lineas_pedido.csv", "100,10,M1-40,1,40,1,", "100,10,M1-40,1,40,0,")
        resultado = self.evaluar()
        # Se rechaza la linea 100, su pedido 10 y la otra linea del pedido (101)
        self.assertEqual(self.rechazadas(resultado, "lineas_pedido"), {"100", "101"})
        self.assertEqual(self.rechazadas(resultado, "pedidos"), {"10"})
        resumen = resultado["resumen"].set_index("tabla")
        self.assertEqual(resumen.loc["lineas_pedido", "filas_validas"], 1)
        self.assertEqual(resumen.loc["lineas_pedido", "porcentaje_calidad"], 33.3)


# Regla 06: precios
class PruebasRegla06(PruebaCalidad):

    # Precio negativo o con coma decimal
    def test_precio_negativo_y_no_numerico(self):
        for valor, texto in [("-79.99", "negativo"), ('"79,99"', "no es un número")]:
            with self.subTest(valor=valor):
                self.cambiar("lineas_pedido.csv", "100,10,M1-40,1,40,1,79.99,", f"100,10,M1-40,1,40,1,{valor},")
                r06 = self.de_la_regla(self.evaluar(), "06")
                self.assertEqual(r06["columna"].tolist(), ["precio_unitario"])
                self.assertIn(texto, r06["detalle"].iloc[0])

    # Un precio_base malo en modelos solo es advertencia
    def test_precio_de_catalogo_solo_avisa(self):
        self.cambiar("modelos.csv", "79.99,true", "abc,true")
        resultado = self.evaluar()
        r06 = self.de_la_regla(resultado, "06")
        self.assertEqual(r06["gravedad"].tolist(), ["advertencia"])
        self.assertEqual(len(resultado["rechazadas"]), 0)


# Regla 07: valores fuera del catalogo
class PruebasRegla07(PruebaCalidad):

    # "Confirmado" con mayuscula no se corrige: se rechaza
    def test_estado_fuera_del_catalogo_no_se_corrige(self):
        self.cambiar("pedidos.csv", "normal,confirmado,pagado", "normal,Confirmado,pagado")
        resultado = self.evaluar()
        r07 = self.de_la_regla(resultado, "07")
        self.assertEqual(r07["valor"].tolist(), ["Confirmado"])
        self.assertEqual(r07["gravedad"].tolist(), ["recuperable"])
        self.assertIn("10", self.rechazadas(resultado, "pedidos"))

    # Un tipo de pedido malo se rechaza; un estado de pago malo solo avisa
    def test_estado_de_pago_y_tipo(self):
        self.cambiar("pedidos.csv", "custom,cancelado,reembolsado", "especial,cancelado,devuelto")
        r07 = self.de_la_regla(self.evaluar(), "07")
        gravedades = dict(zip(r07["columna"], r07["gravedad"]))
        self.assertEqual(gravedades, {"tipo_pedido": "recuperable", "estado_pago": "advertencia"})


# Regla 08: tallas
class PruebasRegla08(PruebaCalidad):

    # La talla de la linea no es la de su SKU
    def test_talla_distinta_de_la_de_su_sku(self):
        self.cambiar("lineas_pedido.csv", "100,10,M1-40,1,40,", "100,10,M1-40,1,41,")
        r08 = self.de_la_regla(self.evaluar(), "08")
        self.assertEqual(r08["registro"].tolist(), ["100"])
        self.assertIn("su SKU", r08["detalle"].iloc[0])

    # Talla 70: fuera del rango
    def test_talla_fuera_de_rango(self):
        self.anadir("stock.csv", "M9-70,1,Rojo,70,true,1,2026-11-09 19:00:00\n")
        r08 = self.de_la_regla(self.evaluar(), "08")
        self.assertEqual(r08["registro"].tolist(), ["M9-70"])
        self.assertIn("rango", r08["detalle"].iloc[0])


# Regla 09: falta el cliente, el pedido o el modelo
class PruebasRegla09(PruebaCalidad):

    # Pedido sin cliente y linea sin modelo: se rechazan
    def test_pedido_sin_cliente_y_linea_sin_modelo(self):
        self.cambiar("pedidos.csv", "11,P-2,2,", "11,P-2,,")
        self.cambiar("lineas_pedido.csv", "100,10,M1-40,1,", "100,10,M1-40,,")
        r09 = self.de_la_regla(self.evaluar(), "09")
        self.assertEqual(sorted(r09["columna"]), ["id_cliente", "id_modelo"])
        self.assertEqual(set(r09["gravedad"]), {"recuperable"})


# Regla 10: lineas duplicadas
class PruebasRegla10(PruebaCalidad):

    # El mismo SKU dos veces en un pedido: solo se avisa, no se borra nada
    def test_mismo_sku_dos_veces_en_un_pedido_no_se_borra(self):
        self.anadir("lineas_pedido.csv", "103,10,M1-40,1,40,1,79.99,79.99\n")
        self.cambiar("pedidos.csv", "3,239.97", "4,319.96")   # el total incluye la linea nueva
        resultado = self.evaluar()
        r10 = self.de_la_regla(resultado, "10")
        self.assertEqual(r10["registro"].tolist(), ["100", "103"])
        self.assertEqual(set(r10["gravedad"]), {"advertencia"})
        self.assertEqual(len(resultado["rechazadas"]), 0)   # las dos lineas se quedan


# Regla 11: stock
class PruebasRegla11(PruebaCalidad):

    # Stock negativo
    def test_stock_negativo(self):
        self.cambiar("stock.csv", "true,12,", "true,-3,")
        r11 = self.de_la_regla(self.evaluar(), "11")
        self.assertEqual(r11["valor"].tolist(), ["-3"])

    # Dos SKU para el mismo modelo, color y talla
    def test_dos_skus_para_la_misma_variante(self):
        self.anadir("stock.csv", "M1-40B,1,Blanco,40,true,3,2026-11-09 19:00:00\n")
        resultado = self.evaluar()
        r11 = self.de_la_regla(resultado, "11")
        self.assertEqual(r11["registro"].tolist(), ["M1-40", "M1-40B"])
        # El stock rechazado no arrastra las lineas: el pedido sigue siendo valido
        self.assertEqual(self.rechazadas(resultado, "lineas_pedido"), set())

    # El mismo modelo y talla en otro color no es duplicado
    def test_otro_color_no_es_duplicado(self):
        self.anadir("stock.csv", "M1-40R,1,Rojo,40,true,3,2026-11-09 19:00:00\n")
        self.assertEqual(len(self.de_la_regla(self.evaluar(), "11")), 0)


# Regla 12: coherencia de fechas, importes y pedidos
class PruebasRegla12(PruebaCalidad):

    # El importe_total no es la suma de sus lineas: se rechaza el pedido con sus lineas
    def test_total_que_no_cuadra(self):
        self.cambiar("pedidos.csv", "3,239.97", "3,250.00")
        resultado = self.evaluar()
        r12 = self.de_la_regla(resultado, "12")
        self.assertEqual(r12["columna"].tolist(), ["importe_total"])
        self.assertIn("239.97", r12["detalle"].iloc[0])
        self.assertEqual(self.rechazadas(resultado, "lineas_pedido"), {"100", "101"})

    # importe_linea distinto de cantidad x precio
    def test_importe_de_linea_mal_calculado(self):
        self.cambiar("lineas_pedido.csv", "2,79.99,159.98", "2,79.99,150.00")
        r12 = self.de_la_regla(self.evaluar(), "12")
        self.assertIn("lineas_pedido", r12["tabla"].tolist())

    # Pedido con fecha posterior al corte de la exportacion
    def test_pedido_posterior_a_la_exportacion(self):
        self.cambiar("pedidos.csv", "2026-11-02 12:30:00", "2026-12-01 10:00:00")
        r12 = self.de_la_regla(self.evaluar(), "12")
        self.assertIn("posterior", r12["detalle"].iloc[0])

    # stock.csv con dos fechas de corte: bloqueante
    def test_stock_de_dos_exportaciones_es_bloqueante(self):
        self.cambiar("stock.csv", "M2-42,2,Negro,42,true,12,2026-11-09 19:00:00",
                     "M2-42,2,Negro,42,true,12,2026-11-10 08:00:00")
        resultado = self.evaluar()
        self.assertEqual(self.de_la_regla(resultado, "12")["gravedad"].tolist(), ["bloqueante"])
        self.assertTrue(resultado["bloqueado"])

    # Pedido custom sin personalizacion: advertencia
    def test_custom_sin_personalizacion(self):
        self.cambiar("pedidos.csv", '"Logo, dorsal"', "")
        r12 = self.de_la_regla(self.evaluar(), "12")
        self.assertEqual(r12["gravedad"].tolist(), ["advertencia"])

    # Posible pedido repetido: se avisa, pero no se borra
    def test_posible_pedido_repetido_no_se_borra(self):
        # Pedido 12: mismo cliente que el 10 y exactamente las mismas lineas
        self.anadir("pedidos.csv", "12,P-3,1,2026-10-02 10:00:00,normal,pendiente,pendiente,,3,239.97\n")
        self.anadir("lineas_pedido.csv", "103,12,M1-40,1,40,1,79.99,79.99\n104,12,M1-41,1,41,2,79.99,159.98\n")
        resultado = self.evaluar()
        r12 = self.de_la_regla(resultado, "12")
        self.assertEqual(r12["valor"].tolist(), ["P-1", "P-3"])
        self.assertEqual(set(r12["gravedad"]), {"advertencia"})
        self.assertEqual(len(resultado["rechazadas"]), 0)
        self.assertEqual(len(resultado["validos"]["pedidos"]), 3)

    # Misma cantidad pero otros articulos: no es un pedido repetido
    def test_misma_cantidad_no_basta_para_ser_repetido(self):
        # Mismo cliente y 3 pares, pero otros articulos: no es sospechoso
        self.anadir("pedidos.csv", "12,P-3,1,2026-10-02 10:00:00,normal,pendiente,pendiente,,3,359.70\n")
        self.anadir("lineas_pedido.csv", "103,12,M2-42,2,42,3,119.90,359.70\n")
        self.assertEqual(len(self.de_la_regla(self.evaluar(), "12")), 0)


# CSV de salida de la calidad
class PruebasCsvDeCalidad(PruebaCalidad):

    # Guarda la tabla en CSV y la vuelve a leer como texto
    def guardar_y_leer(self, tabla, archivo):
        salida = self.carpeta / "salida"
        ruta = pipeline.guardar_salida(tabla, archivo, salida, self.carpeta, "ACC · PRUEBA", "2026-11-09 20:00:00")
        return ruta, pd.read_csv(ruta, encoding="utf-8", dtype=str, keep_default_na=False)

    # CSV de incidencias: columnas, origen y UTF-8 sin BOM
    def test_csv_de_incidencias(self):
        self.cambiar("pedidos.csv", "2026-11-02 12:30:00", "2026-02-30 12:30:00")
        resultado = self.evaluar()
        ruta, leido = self.guardar_y_leer(resultado["incidencias"], "incidencias.csv")
        self.assertEqual(list(leido.columns), ["origen", "ejecucion"] + calidad.COLUMNAS_INCIDENCIA)
        self.assertEqual(len(leido), len(resultado["incidencias"]))
        self.assertEqual(leido.loc[0, "nombre_regla"], "Fecha nula o imposible")   # UTF-8 con tildes
        self.assertEqual(leido.loc[0, "origen"], "ACC · PRUEBA")
        self.assertFalse(ruta.read_bytes().startswith(b"\xef\xbb\xbf"))           # sin BOM

    # Sin incidencias, el CSV lleva al menos la cabecera
    def test_csv_de_incidencias_vacio_lleva_cabecera(self):
        _, leido = self.guardar_y_leer(self.evaluar()["incidencias"], "incidencias.csv")
        self.assertEqual(len(leido), 0)
        self.assertIn("gravedad", leido.columns)

    # Resumen: filas de entrada, validas, rechazadas y porcentaje
    def test_csv_resumen(self):
        self.cambiar("lineas_pedido.csv", "100,10,M1-40,1,40,1,", "100,10,M1-40,1,40,0,")
        _, leido = self.guardar_y_leer(self.evaluar()["resumen"], "resumen_calidad.csv")
        lineas = leido[leido["tabla"] == "lineas_pedido"].iloc[0]
        self.assertEqual((lineas["filas_entrada"], lineas["filas_validas"], lineas["filas_rechazadas"]), ("3", "1", "2"))
        self.assertEqual(lineas["porcentaje_calidad"], "33.3")

    # Guardar en la carpeta de entrada da error
    def test_nunca_escribe_en_la_carpeta_de_entrada(self):
        with self.assertRaises(pipeline.ErrorDatos):
            pipeline.guardar_salida(self.evaluar()["resumen"], "resumen.csv", self.carpeta, self.carpeta, "x", "y")

    # Evaluar no cambia ningun CSV original
    def test_evaluar_no_modifica_los_originales(self):
        antes = {ruta.name: hashlib.sha256(ruta.read_bytes()).hexdigest() for ruta in self.carpeta.glob("*.csv")}
        self.evaluar()
        despues = {ruta.name: hashlib.sha256(ruta.read_bytes()).hexdigest() for ruta in self.carpeta.glob("*.csv")}
        self.assertEqual(antes, despues)
