import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "modulos"))   # los modulos estan en ../modulos

import analiticas
import calidad
from test_analiticas import PruebaAnalisis


# Base: todas las tablas analiticas de los CSV de prueba
class PruebaTablas(PruebaAnalisis):

    # Evalua la calidad y calcula las tablas (sin bloqueantes)
    def tablas(self):
        resultado = calidad.evaluar(self.carpeta)
        self.assertFalse(resultado["bloqueado"])
        return analiticas.calcular_tablas(resultado["datos"], resultado["validos"])

    # Anade dos pedidos de noviembre: asi hay dos meses con ventas
    def anadir_otro_mes(self):
        self.anadir("pedidos.csv", "12,P-3,1,2026-11-05 10:00:00,normal,confirmado,pagado,,1,79.99\n"
                                   "13,P-4,2,2026-11-06 10:00:00,normal,entregado,pagado,,2,239.80\n")
        self.anadir("lineas_pedido.csv", "103,12,M1-40,1,40,1,79.99,79.99\n104,13,M2-42,2,42,2,119.90,239.80\n")

    # Deja lineas_pedido.csv solo con la cabecera
    def vaciar_lineas(self):
        self.escribir("lineas_pedido.csv", "id_linea,id_pedido,sku,id_modelo,talla,cantidad,precio_unitario,importe_linea\n")


# Pedidos por estado
class PruebasEstados(PruebaTablas):

    # Salen los 6 estados, tambien los que no tienen pedidos
    def test_todos_los_estados_del_catalogo(self):
        tabla = self.tablas()["pedidos_por_estado"].set_index("estado_pedido")
        self.assertEqual(len(tabla), 6)
        self.assertEqual(tabla.loc["confirmado", "pedidos"], 1)
        self.assertEqual(tabla.loc["cancelado", "pedidos"], 1)
        self.assertEqual(tabla.loc["enviado", "pedidos"], 0)          # un estado sin pedidos sale con 0
        self.assertEqual(tabla.loc["cancelado", "importe"], 239.80)  # el cancelado se ve, no se borra
        self.assertTrue(tabla.loc["confirmado", "cuenta_como_venta"])
        self.assertFalse(tabla.loc["cancelado", "cuenta_como_venta"])
        self.assertEqual(tabla["pedidos"].sum(), 2)


# Modelos y tallas
class PruebasModelosYTallas(PruebaTablas):

    # Matriz modelo x talla y su proporcion por fila
    def test_matriz_modelo_talla(self):
        tablas = self.tablas()
        matriz = tablas["matriz_modelo_talla"]
        # Solo demanda: el pedido cancelado (Modelo Dos, talla 42) no cuenta
        self.assertEqual(matriz.loc["Modelo Uno"].tolist(), [1, 2])
        self.assertEqual(list(matriz.columns), [40, 41])
        self.assertEqual(tablas["matriz_modelo_talla_proporcion"].loc["Modelo Uno"].tolist(), [0.3333, 0.6667])

    # Matriz, tallas y ABC suman los mismos pares que las lineas de demanda
    def test_matriz_no_duplica_pares(self):
        self.anadir_otro_mes()
        tablas = self.tablas()
        demanda = tablas["lineas_enriquecidas"]
        demanda = demanda[~demanda["es_cancelado"]]
        self.assertEqual(tablas["matriz_modelo_talla"].to_numpy().sum(), demanda["cantidad"].sum())
        self.assertEqual(tablas["ventas_por_talla"]["pares"].sum(), demanda["cantidad"].sum())
        self.assertEqual(tablas["modelos_abc"]["pares"].sum(), demanda["cantidad"].sum())

    # Talla 40: 1 par (33.3 %) y talla 41: 2 pares (66.7 %); el cancelado no cuenta
    def test_ventas_por_talla(self):
        tabla = self.tablas()["ventas_por_talla"]
        self.assertEqual(tabla["talla"].tolist(), [40, 41])
        self.assertEqual(tabla["pares"].tolist(), [1, 2])
        self.assertEqual(tabla["peso_pct"].tolist(), [33.3, 66.7])


# Clasificacion ABC
class PruebasAbc(PruebaTablas):

    # La clase sale del acumulado de los anteriores
    def test_clases_por_acumulado(self):
        tabla = pd.DataFrame({"modelo": ["X", "Y", "Z"], "pares": [80, 15, 5]})
        abc = analiticas.clasificar_abc(tabla, "pares")
        self.assertEqual(abc["acumulado_pct"].tolist(), [80.0, 95.0, 100.0])
        # Clase segun lo acumulado ANTES: X (0 %) A, Y (80 %) B, Z (95 %) C
        self.assertEqual(abc["clase_abc"].tolist(), ["A", "B", "C"])

    # El modelo que pasa del 80 % sigue siendo A
    def test_el_que_cruza_el_80_es_a(self):
        tabla = pd.DataFrame({"modelo": ["X", "Y"], "pares": [60, 40]})
        self.assertEqual(analiticas.clasificar_abc(tabla, "pares")["clase_abc"].tolist(), ["A", "A"])

    # Modelos empatados en pares tienen la misma clase
    def test_empates_reciben_la_misma_clase(self):
        tabla = pd.DataFrame({"modelo": ["V", "W", "X", "Y"], "pares": [91, 3, 3, 3]})
        abc = analiticas.clasificar_abc(tabla, "pares")
        self.assertEqual(abc["clase_abc"].tolist(), ["A", "B", "B", "B"])   # 97 % acumulado y sigue en B

    # Un modelo sin demanda sale con 0 pares y clase C
    def test_modelo_sin_demanda_es_c_y_no_desaparece(self):
        abc = self.tablas()["modelos_abc"].set_index("nombre_modelo")
        self.assertEqual(abc.loc["Modelo Uno", "clase_abc"], "A")
        self.assertEqual(abc.loc["Modelo Dos", "pares"], 0)        # su unico pedido esta cancelado
        self.assertEqual(abc.loc["Modelo Dos", "clase_abc"], "C")

    # Sin ninguna demanda todos son C y no hay porcentajes
    def test_sin_ninguna_demanda(self):
        tabla = pd.DataFrame({"modelo": ["X", "Y"], "pares": [0, 0]})
        abc = analiticas.clasificar_abc(tabla, "pares")
        self.assertEqual(abc["clase_abc"].tolist(), ["C", "C"])
        self.assertEqual(abc["peso_pct"].tolist(), [None, None])   # sin total no hay porcentaje


# Custom frente a estandar y actividad de clientes
class PruebasCustomYClientes(PruebaTablas):

    # Cancelacion, cuota y ticket medio de cada tipo de pedido
    def test_custom_frente_a_estandar(self):
        tabla = self.tablas()["custom_vs_estandar"].set_index("tipo_pedido")
        self.assertEqual(tabla.loc["custom", "tasa_cancelacion_pct"], 100.0)   # de pedidos
        self.assertEqual(tabla.loc["normal", "cuota_importe_pct"], 100.0)      # de euros de demanda
        self.assertEqual(tabla.loc["normal", "ticket_medio_venta"], 239.97)
        self.assertTrue(pd.isna(tabla.loc["custom", "ticket_medio_venta"]))    # sin ventas no hay ticket (nulo)

    # Una fila por cliente, sin nombre, con sus pedidos e importes
    def test_clientes_actividad(self):
        tabla = self.tablas()["clientes_actividad"].set_index("id_cliente")
        self.assertEqual(len(tabla), 2)
        self.assertNotIn("nombre", tabla.columns)                            # no hace falta el nombre
        self.assertEqual(tabla.loc["1", "importe_demanda"], 239.97)
        self.assertEqual(tabla.loc["1", "dias_desde_ultimo_pedido"], 39)
        self.assertEqual(tabla.loc["2", "pedidos_cancelados"], 1)
        self.assertEqual(tabla.loc["2", "importe_demanda"], 0.0)


# Tablas por mes y cohortes
class PruebasTiempo(PruebaTablas):

    # Con un solo mes no hay variacion ni cohortes
    def test_un_solo_mes_no_inventa_evolucion(self):
        tablas = self.tablas()
        ventas = tablas["ventas_por_periodo"]
        self.assertEqual(ventas["anio_mes"].tolist(), ["2026-10"])
        self.assertTrue(pd.isna(ventas.loc[0, "variacion_importe_pct"]))
        self.assertEqual(tablas["cohortes"]["estado"].iloc[0], "NO CALCULABLE")

    # Con los pedidos de noviembre hay dos meses y el importe sube un 33.3 %
    def test_dos_meses(self):
        self.anadir_otro_mes()
        ventas = self.tablas()["ventas_por_periodo"]
        self.assertEqual(ventas["anio_mes"].tolist(), ["2026-10", "2026-11"])
        self.assertEqual(ventas["pedidos"].tolist(), [1, 2])
        self.assertEqual(ventas["importe"].tolist(), [239.97, 319.79])
        self.assertEqual(ventas.loc[1, "variacion_importe_pct"], 33.3)
        self.assertTrue(pd.isna(ventas.loc[1, "media_3_meses_previos"]))   # harian falta 3 meses previos

    # Un mes sin ventas entre dos con ventas sale con 0
    def test_mes_sin_ventas_en_medio_es_cero(self):
        self.anadir("pedidos.csv", "12,P-3,1,2026-12-05 10:00:00,normal,confirmado,pagado,,1,79.99\n")
        self.anadir("lineas_pedido.csv", "103,12,M1-40,1,40,1,79.99,79.99\n")
        self.cambiar("stock.csv", "2026-11-09 19:00:00", "2026-12-09 19:00:00")
        ventas = self.tablas()["ventas_por_periodo"]
        self.assertEqual(ventas["anio_mes"].tolist(), ["2026-10", "2026-11", "2026-12"])
        self.assertEqual(ventas["pedidos"].tolist(), [1, 0, 1])

    # Retencion de cada cohorte; lo que aun no ha pasado queda vacio
    def test_cohortes(self):
        self.anadir_otro_mes()
        cohortes = self.tablas()["cohortes"].set_index("cohorte")
        # Cliente 1: primera compra en octubre y vuelve en noviembre
        self.assertEqual(cohortes.loc["2026-10", "retencion_mes_1"], 1.0)
        # Cliente 2: su primera COMPRA es de noviembre (el de octubre esta cancelado)
        self.assertEqual(cohortes.loc["2026-11", "clientes_cohorte"], 1)
        # Diciembre aun no ha pasado: no se sabe, no es 0
        self.assertTrue(pd.isna(cohortes.loc["2026-11", "retencion_mes_1"]))


# Stock por SKU y cobertura
class PruebasStock(PruebaTablas):

    # 3 SKU, 17 pares de stock en total y 2 SKU con alerta de stock bajo
    def test_totales_de_inventario(self):
        stock = self.tablas()["stock_variantes"]
        self.assertEqual(len(stock), 3)                      # una fila por SKU: el cruce no multiplica
        self.assertEqual(stock["stock_disponible"].sum(), 17)
        self.assertEqual(stock["alerta_stock_bajo"].sum(), 2)

    # La tabla de stock bajo va de menos a mas stock: M1-41 (0 pares) antes que M1-40 (5)
    def test_stock_bajo_ordenado(self):
        bajo = self.tablas()["stock_bajo"]
        self.assertEqual(bajo["sku"].tolist(), ["M1-41", "M1-40"])

    # Cada color es un SKU aparte: su stock no se suma
    def test_no_se_suma_entre_colores(self):
        self.anadir("stock.csv", "M1-40R,1,Rojo,40,true,7,2026-11-09 19:00:00\n")
        stock = self.tablas()["stock_variantes"]
        self.assertEqual(len(stock), 4)
        self.assertEqual(stock.loc[stock["sku"] == "M1-40", "stock_disponible"].iloc[0], 5)

    # Sin pedidos en los ultimos 28 dias la cobertura es N/D
    def test_cobertura_sin_demanda_reciente(self):
        stock = self.tablas()["stock_variantes"]
        self.assertTrue(stock["semanas_cobertura"].isna().all())
        self.assertTrue(stock["estado_cobertura"].str.startswith("N/D").all())

    # Cobertura = stock / (pares de 28 dias / 4)
    def test_cobertura_con_demanda(self):
        self.anadir_otro_mes()
        stock = self.tablas()["stock_variantes"].set_index("sku")
        self.assertEqual(stock.loc["M1-40", "demanda_28d"], 1)
        self.assertEqual(stock.loc["M1-40", "semanas_cobertura"], 20.0)   # 5 / (1 / 4)
        self.assertEqual(stock.loc["M2-42", "semanas_cobertura"], 24.0)   # 12 / (2 / 4)

    # Con menos de 28 dias de historial la cobertura es NO CALCULABLE
    def test_cobertura_con_poco_historial(self):
        self.cambiar("pedidos.csv", "2026-10-01 10:00:00", "2026-11-01 10:00:00")
        stock = self.tablas()["stock_variantes"]
        self.assertTrue(stock["estado_cobertura"].iloc[0].startswith("NO CALCULABLE"))


# Margen, atipicos y nulos
class PruebasOtrasTablas(PruebaTablas):

    # Hay precio medio, pero el margen es NO CALCULABLE (falta el coste)
    def test_margen_no_calculable(self):
        precios = self.tablas()["precio_y_margen"].set_index("nombre_modelo")
        self.assertEqual(precios.loc["Modelo Uno", "precio_medio_ponderado"], 79.99)
        self.assertTrue(precios["margen"].str.startswith("NO CALCULABLE").all())

    # Con grupos pequenos no se buscan atipicos
    def test_anomalias_con_muestra_pequena(self):
        anomalias = self.tablas()["anomalias"]
        self.assertTrue(anomalias["estado"].str.startswith("muestra insuficiente").all())

    # Un precio de 800 entre precios de 80 es atipico, pero la linea no se borra
    def test_anomalia_detectada_y_no_borrada(self):
        lineas = pd.DataFrame({"id_linea": [str(i) for i in range(6)], "nombre_modelo": ["M"] * 6,
                               "tipo_pedido": ["normal"] * 6, "cantidad": [1] * 6,
                               "precio_unitario": [80.0, 80.0, 80.0, 80.0, 80.0, 800.0]})
        anomalias = analiticas.anomalias_iqr(lineas)
        precio = anomalias[anomalias["variable"] == "precio_unitario"].iloc[0]
        self.assertEqual(precio["atipicos"], 1)
        self.assertEqual(precio["lineas_atipicas"], "5")
        self.assertEqual(len(lineas), 6)

    # El recargo de los Custom no es atipico: custom y normal van en grupos distintos
    def test_el_recargo_custom_no_es_un_atipico(self):
        lineas = pd.DataFrame({"id_linea": [str(i) for i in range(11)], "nombre_modelo": ["M"] * 11,
                               "tipo_pedido": ["normal"] * 6 + ["custom"] * 5, "cantidad": [1] * 6 + [10] * 5,
                               "precio_unitario": [100.0] * 6 + [120.0] * 5})
        anomalias = analiticas.anomalias_iqr(lineas)
        precios = anomalias[anomalias["variable"] == "precio_unitario"]
        self.assertEqual(len(precios), 2)                     # un grupo custom (5 valores) y uno normal (6)...
        self.assertEqual(precios["atipicos"].sum(), 0)        # ...y ninguno marca el recargo como raro
        self.assertEqual(sorted(precios["grupo"]), ["nombre_modelo = M, tipo_pedido = custom",
                                                    "nombre_modelo = M, tipo_pedido = normal"])

    # El telefono de clientes tiene 1 nulo en 2 filas: un 50 % de nulos
    def test_nulos_por_columna(self):
        resultado = calidad.evaluar(self.carpeta)
        nulos = calidad.nulos_por_columna(resultado["datos"]).set_index(["tabla", "columna"])
        self.assertEqual(nulos.loc[("clientes", "telefono"), "nulos"], 1)
        self.assertEqual(nulos.loc[("clientes", "telefono"), "porcentaje_nulos"], 50.0)


# Sin lineas
class PruebasTablasVacias(PruebaTablas):

    # Sin ninguna linea, ninguna tabla falla y el stock sigue ahi
    def test_sin_lineas_ninguna_tabla_falla(self):
        self.vaciar_lineas()
        tablas = self.tablas()
        self.assertEqual(len(tablas["pedidos_unicos"]), 0)
        self.assertEqual(tablas["pedidos_por_estado"]["pedidos"].sum(), 0)
        self.assertEqual(len(tablas["ventas_por_talla"]), 0)
        self.assertEqual(len(tablas["matriz_modelo_talla"]), 0)
        self.assertEqual(tablas["ventas_por_periodo"]["estado"].iloc[0], "NO CALCULABLE")
        self.assertEqual(tablas["matriz_modelo_mes"]["estado"].iloc[0], "NO CALCULABLE")
        self.assertEqual(set(tablas["modelos_abc"]["clase_abc"]), {"C"})
        self.assertEqual(tablas["clientes_actividad"]["sin_pedidos"].tolist(), [True, True])
        self.assertEqual(tablas["stock_variantes"]["stock_disponible"].sum(), 17)
