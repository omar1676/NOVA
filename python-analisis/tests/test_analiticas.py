"""
Pruebas de los dos DataFrames principales, las variables derivadas, los
importes por criterio y la conciliacion con SQL (analiticas.py y conciliacion.py).

Datos de partida (los CSV validos de test_pipeline.py):
  pedido 10  P-1  cliente 1  2026-10-01 10:00 (jueves)  normal  confirmado  lineas 100 y 101: 3 pares, 239.97 €
  pedido 11  P-2  cliente 2  2026-11-02 12:30 (lunes)   custom  cancelado   linea 102:         2 pares, 239.80 €
  fecha de corte del stock: 2026-11-09 19:00
"""
import pandas as pd

import analiticas
import calidad
import conciliacion
import pipeline
from test_calidad import PruebaCalidad


class PruebaAnalisis(PruebaCalidad):
    """Base: construir los dos DataFrames a partir de la carpeta temporal."""

    def construir(self):
        resultado = calidad.evaluar(self.carpeta)
        self.assertFalse(resultado["bloqueado"])
        stock = resultado["datos"]["stock"]
        lineas = analiticas.df_lineas_enriquecidas(resultado["validos"], stock)
        pedidos = analiticas.df_pedidos_unicos(resultado["validos"], lineas, stock["fecha_corte"].max())
        return lineas, pedidos


class PruebasLineasEnriquecidas(PruebaAnalisis):

    def test_una_fila_por_linea(self):
        lineas, _ = self.construir()
        self.assertEqual(lineas["id_linea"].tolist(), ["100", "101", "102"])
        self.assertTrue(lineas["id_linea"].is_unique)

    def test_datos_del_pedido_cliente_y_modelo(self):
        lineas, _ = self.construir()
        linea = lineas[lineas["id_linea"] == "102"].iloc[0]
        self.assertEqual(linea["referencia"], "P-2")
        self.assertEqual(linea["nombre_cliente"], "Club Atlético Prueba")
        self.assertEqual(linea["nombre_modelo"], "Modelo Dos")
        self.assertEqual(linea["color"], "Negro")
        self.assertEqual(linea["estado_pedido"], "cancelado")
        self.assertTrue(linea["es_cancelado"])
        self.assertTrue(linea["es_custom"])

    def test_participacion_de_la_linea_en_su_pedido(self):
        lineas, _ = self.construir()
        self.assertEqual(lineas["participacion_linea"].tolist(), [0.3333, 0.6667, 1.0])
        por_pedido = lineas.groupby("id_pedido")["participacion_linea"].sum()
        self.assertAlmostEqual(por_pedido["10"], 1.0, places=3)

    def test_linea_sin_sku_no_rompe_el_cruce_con_stock(self):
        # Una linea sin SKU (como las X-NOVA) no tiene color, pero no es un error
        self.anadir("lineas_pedido.csv", "103,10,,1,40,1,79.99,79.99\n")
        self.cambiar("pedidos.csv", "3,239.97", "4,319.96")
        lineas, _ = self.construir()
        self.assertEqual(len(lineas), 4)
        self.assertTrue(pd.isna(lineas.loc[lineas["id_linea"] == "103", "color"].iloc[0]))


class PruebasCruces(PruebaAnalisis):

    def test_join_que_duplicaria_filas_se_detiene(self):
        lineas = pd.DataFrame({"id_linea": ["1", "2", "3"], "id_cliente": ["1", "1", "2"]})
        clientes = pd.DataFrame({"id_cliente": ["1", "1", "2"], "nombre": ["Ana", "Ana bis", "Eva"]})
        # Sin validate, pandas multiplica las filas en silencio: 3 lineas pasan a ser 5
        self.assertEqual(len(lineas.merge(clientes, on="id_cliente")), 5)
        with self.assertRaises(pipeline.ErrorDatos) as contexto:
            analiticas.cruzar(lineas, clientes, "id_cliente", "many_to_one", "prueba")
        self.assertIn("many_to_one", str(contexto.exception))

    def test_clave_sin_pareja_se_detiene(self):
        lineas = pd.DataFrame({"id_linea": ["1"], "id_cliente": ["9"]})
        clientes = pd.DataFrame({"id_cliente": ["1"], "nombre": ["Ana"]})
        with self.assertRaises(pipeline.ErrorDatos) as contexto:
            analiticas.cruzar(lineas, clientes, "id_cliente", "many_to_one", "prueba")
        self.assertIn("sin pareja", str(contexto.exception))

    def test_sin_pareja_permitido_cuando_se_dice(self):
        pedidos = pd.DataFrame({"id_pedido": ["1", "2"]})
        metricas = pd.DataFrame({"id_pedido": ["1"], "pares": [3]})
        cruce = analiticas.cruzar(pedidos, metricas, "id_pedido", "one_to_one", "prueba", exigir_pareja=False)
        self.assertEqual(len(cruce), 2)


class PruebasPedidosUnicos(PruebaAnalisis):

    def test_una_fila_por_pedido(self):
        _, pedidos = self.construir()
        self.assertEqual(pedidos["referencia"].tolist(), ["P-1", "P-2"])
        self.assertTrue(pedidos["id_pedido"].is_unique)

    def test_metricas_de_sus_lineas(self):
        _, pedidos = self.construir()
        self.assertEqual(pedidos["num_lineas"].tolist(), [2, 1])
        self.assertEqual(pedidos["pares"].tolist(), [3, 2])
        self.assertEqual(pedidos["importe"].tolist(), [239.97, 239.80])
        self.assertEqual(pedidos["precio_medio_par"].tolist(), [79.99, 119.90])
        self.assertEqual(pedidos["num_tallas"].tolist(), [2, 1])
        # Lo calculado desde las lineas coincide con la cabecera de Acceso a Datos
        self.assertEqual(pedidos["pares"].tolist(), pedidos["cantidad_total"].tolist())

    def test_variables_de_calendario(self):
        _, pedidos = self.construir()
        self.assertEqual(pedidos["anio"].tolist(), [2026, 2026])
        self.assertEqual(pedidos["mes"].tolist(), [10, 11])
        self.assertEqual(pedidos["anio_mes"].tolist(), ["2026-10", "2026-11"])
        self.assertEqual(pedidos["trimestre"].tolist(), [4, 4])
        self.assertEqual(pedidos["dia_semana"].tolist(), ["jueves", "lunes"])
        self.assertEqual(pedidos["antiguedad_dias"].tolist(), [39, 7])   # hasta la fecha de corte

    def test_indicadores_de_tipo_y_estado(self):
        _, pedidos = self.construir()
        self.assertEqual(pedidos["es_custom"].tolist(), [False, True])
        self.assertEqual(pedidos["es_cancelado"].tolist(), [False, True])
        self.assertEqual(pedidos["es_confirmado"].tolist(), [True, False])

    def test_modelo_del_pedido_solo_si_es_unico(self):
        _, pedidos = self.construir()
        self.assertEqual(pedidos["modelo_pedido"].tolist(), ["Modelo Uno", "Modelo Dos"])
        # Ahora el pedido 10 lleva dos modelos: no se le atribuye ninguno
        self.cambiar("lineas_pedido.csv", "101,10,M1-41,1,41,2,79.99,159.98", "101,10,M2-42,2,42,2,119.90,239.80")
        self.cambiar("pedidos.csv", "3,239.97", "3,319.79")
        _, pedidos = self.construir()
        pedido = pedidos[pedidos["referencia"] == "P-1"].iloc[0]
        self.assertEqual(pedido["num_modelos"], 2)
        self.assertTrue(pedido["pedido_multimodelo"])
        self.assertTrue(pd.isna(pedido["modelo_pedido"]))

    def test_pedido_sin_lineas(self):
        self.cambiar("lineas_pedido.csv", "102,11,M2-42,2,42,2,119.90,239.80\n", "")
        self.cambiar("pedidos.csv", "2,239.80", "0,0.00")
        _, pedidos = self.construir()
        pedido = pedidos[pedidos["referencia"] == "P-2"].iloc[0]
        self.assertEqual((pedido["num_lineas"], pedido["pares"], pedido["importe"]), (0, 0, 0.0))
        self.assertTrue(pd.isna(pedido["precio_medio_par"]))   # sin pares no hay precio medio
        self.assertTrue(pd.isna(pedido["modelo_pedido"]))

    def test_filas_rechazadas_no_entran(self):
        self.cambiar("lineas_pedido.csv", "100,10,M1-40,1,40,1,", "100,10,M1-40,1,40,0,")
        lineas, pedidos = self.construir()
        self.assertEqual(pedidos["referencia"].tolist(), ["P-2"])
        self.assertEqual(lineas["id_linea"].tolist(), ["102"])


class PruebasImportesPorCriterio(PruebaAnalisis):

    def criterios(self):
        _, pedidos = self.construir()
        return analiticas.importes_por_criterio(pedidos).set_index("criterio")

    def test_tres_criterios(self):
        criterios = self.criterios()
        self.assertEqual(criterios.loc["registrados", ["pedidos", "pares", "importe_eur"]].tolist(), [2, 5, 479.77])
        self.assertEqual(criterios.loc["no_cancelados", ["pedidos", "pares", "importe_eur"]].tolist(), [1, 3, 239.97])
        self.assertEqual(criterios.loc["confirmados_en_adelante", ["pedidos", "pares", "importe_eur"]].tolist(), [1, 3, 239.97])
        self.assertEqual(set(criterios["iva"]), {"pendiente de confirmar"})

    def test_un_pedido_que_avanza_sigue_contando(self):
        self.cambiar("pedidos.csv", "normal,confirmado,pagado", "normal,en_preparacion,pagado")
        self.assertEqual(self.criterios().loc["confirmados_en_adelante", "pedidos"], 1)

    def test_pendiente_no_es_confirmado(self):
        self.cambiar("pedidos.csv", "normal,confirmado,pagado", "normal,pendiente,pendiente")
        criterios = self.criterios()
        self.assertEqual(criterios.loc["confirmados_en_adelante", "pedidos"], 0)
        self.assertEqual(criterios.loc["no_cancelados", "pedidos"], 1)


class PruebasCompararPedidos(PruebaAnalisis):

    def test_dos_pedidos_lado_a_lado(self):
        self.anadir("pedidos.csv", "12,P-3,1,2026-10-02 10:00:00,normal,pendiente,pendiente,,3,239.97\n")
        self.anadir("lineas_pedido.csv", "103,12,M1-40,1,40,1,79.99,79.99\n104,12,M1-41,1,41,2,79.99,159.98\n")
        lineas, pedidos = self.construir()
        tabla = analiticas.comparar_pedidos(pedidos, lineas, "P-1", "P-3").set_index("campo")
        self.assertTrue(tabla.loc["id_cliente", "igual"])
        self.assertTrue(tabla.loc["articulos", "igual"])
        self.assertFalse(tabla.loc["id_pedido", "igual"])
        self.assertFalse(tabla.loc["estado_pedido", "igual"])


# Resultados SQL que corresponden a los CSV validos (los usan tambien otras pruebas)
SQL_CORRECTOS = {
    "P-A.csv": "pedidos,pares_solicitados,importe_ventas\n1,3,239.97\n",
    "P-B.csv": "estado,pedidos,pares,importe\nconfirmado,1,3,239.97\ncancelado,1,2,239.80\n",
    "P-C.csv": "modelo,pares,pedidos\nModelo Uno,3,1\n",
}


class PruebasConciliacion(PruebaAnalisis):

    CORRECTOS = SQL_CORRECTOS

    def conciliar(self, cambios=None):
        carpeta_sql = self.carpeta / "conciliacion_sql"
        carpeta_sql.mkdir(exist_ok=True)
        for archivo, texto in {**self.CORRECTOS, **(cambios or {})}.items():
            (carpeta_sql / archivo).write_text(texto, encoding="utf-8")
        lineas, pedidos = self.construir()
        return conciliacion.conciliar(carpeta_sql, pedidos, lineas)

    def test_cifras_que_coinciden(self):
        tabla = self.conciliar()
        self.assertEqual(len(tabla), 11)   # P-A: 3 cifras, P-B: 2 estados x 3, P-C: 1 modelo x 2
        self.assertEqual(set(tabla["resultado"]), {"coincide"})

    def test_importe_que_no_coincide(self):
        tabla = self.conciliar({"P-A.csv": "pedidos,pares_solicitados,importe_ventas\n1,3,240.00\n"})
        fila = tabla[(tabla["consulta"] == "P-A") & (tabla["indicador"] == "importe")].iloc[0]
        self.assertEqual(fila["resultado"], "NO COINCIDE")
        self.assertEqual(fila["diferencia"], -0.03)

    def test_estado_que_solo_esta_en_sql(self):
        tabla = self.conciliar({"P-B.csv": self.CORRECTOS["P-B.csv"] + "pendiente,1,1,10.00\n"})
        self.assertEqual(set(tabla.loc[tabla["clave"] == "pendiente", "resultado"]), {"falta en Python"})

    def test_modelo_que_solo_esta_en_python(self):
        tabla = self.conciliar({"P-C.csv": "modelo,pares,pedidos\n"})
        self.assertEqual(set(tabla.loc[tabla["consulta"] == "P-C", "resultado"]), {"falta en SQL"})

    def test_sin_resultados_sql_queda_pendiente(self):
        lineas, pedidos = self.construir()
        carpeta_sql = self.carpeta / "no_existe"
        self.assertIsNone(conciliacion.conciliar(carpeta_sql, pedidos, lineas))
        self.assertEqual(conciliacion.faltan_resultados(carpeta_sql), ["P-A.csv", "P-B.csv", "P-C.csv"])

# Resultados SQL del caso N (N-1 a N-3 de 12_consultas_panel.sql) que corresponden a los CSV validos
SQL_CASO_N = {
    "N-1.csv": "anio_mes,pedidos,pares,importe\n2026-10,1,3,239.97\n",
    "N-2.csv": "modelo,talla,pares\nModelo Uno,40,1\nModelo Uno,41,2\n",
    "N-3.csv": "clientes_con_pedidos,clientes_con_demanda,clientes_con_venta\n2,1,1\n",
}


class PruebasCasoN(PruebaAnalisis):
    """Caso N: ingresos de un mes, matriz talla x modelo y clientes unicos, SQL frente a pandas."""

    def tablas(self):
        resultado = calidad.evaluar(self.carpeta)
        return analiticas.calcular_tablas(resultado["datos"], resultado["validos"])

    def contrastar(self, cambios=None):
        carpeta_sql = self.carpeta / "conciliacion_sql"
        carpeta_sql.mkdir(exist_ok=True)
        for archivo, texto in {**SQL_CASO_N, **(cambios or {})}.items():
            (carpeta_sql / archivo).write_text(texto, encoding="utf-8")
        return conciliacion.contrastar_caso_n(carpeta_sql, self.tablas())

    def test_las_tres_cifras_coinciden(self):
        tabla = self.contrastar()
        # N-1: pedidos, pares e importe; N-2: 2 celdas con pares; N-3: 3 criterios
        self.assertEqual(tabla["consulta"].value_counts().to_dict(), {"N-1": 3, "N-2": 2, "N-3": 3})
        self.assertEqual(set(tabla["resultado"]), {"coincide"})
        importe = tabla[(tabla["consulta"] == "N-1") & (tabla["indicador"] == "importe")].iloc[0]
        self.assertEqual((importe["clave"], importe["valor_python"]), ("2026-10", 239.97))

    def test_mes_sin_ventas_es_cero_en_los_dos_lados(self):
        # En noviembre solo hay un pedido cancelado, que no es venta
        tabla = self.contrastar({"N-1.csv": "anio_mes,pedidos,pares,importe\n2026-11,0,0,0.00\n"})
        mes = tabla[tabla["consulta"] == "N-1"]
        self.assertEqual(set(mes["clave"]), {"2026-11"})
        self.assertEqual(set(mes["resultado"]), {"coincide"})

    def test_discrepancias_detectadas(self):
        # Una consulta que olvida quitar los cancelados: sobra una celda y un cliente con demanda
        tabla = self.contrastar({
            "N-2.csv": SQL_CASO_N["N-2.csv"] + "Modelo Dos,42,2\n",
            "N-3.csv": "clientes_con_pedidos,clientes_con_demanda,clientes_con_venta\n2,2,1\n",
        })
        celda = tabla[tabla["clave"] == "Modelo Dos · 42"].iloc[0]
        self.assertEqual(celda["resultado"], "falta en Python")
        demanda = tabla[tabla["indicador"] == "clientes_con_demanda"].iloc[0]
        self.assertEqual((demanda["resultado"], demanda["diferencia"]), ("NO COINCIDE", -1.0))

    def test_sin_resultados_queda_pendiente(self):
        carpeta_sql = self.carpeta / "no_existe"
        self.assertIsNone(conciliacion.contrastar_caso_n(carpeta_sql, self.tablas()))
        self.assertEqual(conciliacion.faltan_resultados(carpeta_sql, conciliacion.CONSULTAS_CASO_N),
                         ["N-1.csv", "N-2.csv", "N-3.csv"])
