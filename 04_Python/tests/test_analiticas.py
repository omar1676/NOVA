import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "modulos"))   # los modulos estan en ../modulos

import analiticas
import calidad
import conciliacion
import kpis
import pipeline
from test_calidad import PruebaCalidad


# Base: lineas enriquecidas y pedidos unicos de los CSV de prueba
class PruebaAnalisis(PruebaCalidad):

    # Evalua la calidad (sin bloqueantes) y devuelve las lineas enriquecidas y los pedidos unicos
    def construir(self):
        resultado = calidad.evaluar(self.carpeta)
        self.assertFalse(resultado["bloqueado"])
        stock = resultado["datos"]["stock"]
        lineas = analiticas.df_lineas_enriquecidas(resultado["validos"], stock)
        pedidos = analiticas.df_pedidos_unicos(resultado["validos"], lineas, stock["fecha_corte"].max())
        return lineas, pedidos


# DataFrame de lineas enriquecidas
class PruebasLineasEnriquecidas(PruebaAnalisis):

    # Una fila por cada linea del CSV, sin repetir
    def test_una_fila_por_linea(self):
        lineas, _ = self.construir()
        self.assertEqual(lineas["id_linea"].tolist(), ["100", "101", "102"])
        self.assertTrue(lineas["id_linea"].is_unique)

    # Cada linea trae los datos de su pedido, su cliente, su modelo y su color
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

    # Parte de cada linea en su pedido; las de un mismo pedido suman 1
    def test_participacion_de_la_linea_en_su_pedido(self):
        lineas, _ = self.construir()
        self.assertEqual(lineas["participacion_linea"].tolist(), [0.3333, 0.6667, 1.0])
        por_pedido = lineas.groupby("id_pedido")["participacion_linea"].sum()
        self.assertAlmostEqual(por_pedido["10"], 1.0, places=3)

    # Una linea sin SKU (como las X-NOVA) se queda sin color, pero el cruce con stock no falla
    def test_linea_sin_sku_no_rompe_el_cruce_con_stock(self):
        self.anadir("lineas_pedido.csv", "103,10,,1,40,1,79.99,79.99\n")
        self.cambiar("pedidos.csv", "3,239.97", "4,319.96")
        lineas, _ = self.construir()
        self.assertEqual(len(lineas), 4)
        self.assertTrue(pd.isna(lineas.loc[lineas["id_linea"] == "103", "color"].iloc[0]))


# Cruces (merge) con control de filas y de parejas
class PruebasCruces(PruebaAnalisis):

    # Un cruce que duplicaria filas se para con ErrorDatos
    def test_join_que_duplicaria_filas_se_detiene(self):
        lineas = pd.DataFrame({"id_linea": ["1", "2", "3"], "id_cliente": ["1", "1", "2"]})
        clientes = pd.DataFrame({"id_cliente": ["1", "1", "2"], "nombre": ["Ana", "Ana bis", "Eva"]})
        # Sin validate, pandas multiplica las filas en silencio: 3 lineas pasan a ser 5
        self.assertEqual(len(lineas.merge(clientes, on="id_cliente")), 5)
        with self.assertRaises(pipeline.ErrorDatos) as contexto:
            analiticas.cruzar(lineas, clientes, "id_cliente", "many_to_one", "prueba")
        self.assertIn("many_to_one", str(contexto.exception))

    # Una clave sin pareja se para con ErrorDatos
    def test_clave_sin_pareja_se_detiene(self):
        lineas = pd.DataFrame({"id_linea": ["1"], "id_cliente": ["9"]})
        clientes = pd.DataFrame({"id_cliente": ["1"], "nombre": ["Ana"]})
        with self.assertRaises(pipeline.ErrorDatos) as contexto:
            analiticas.cruzar(lineas, clientes, "id_cliente", "many_to_one", "prueba")
        self.assertIn("sin pareja", str(contexto.exception))

    # Con exigir_pareja=False, la fila sin pareja se queda
    def test_sin_pareja_permitido_cuando_se_dice(self):
        pedidos = pd.DataFrame({"id_pedido": ["1", "2"]})
        metricas = pd.DataFrame({"id_pedido": ["1"], "pares": [3]})
        cruce = analiticas.cruzar(pedidos, metricas, "id_pedido", "one_to_one", "prueba", exigir_pareja=False)
        self.assertEqual(len(cruce), 2)


# DataFrame de pedidos unicos
class PruebasPedidosUnicos(PruebaAnalisis):

    # P-1 y P-2 salen una sola vez, aunque P-1 tenga dos lineas
    def test_una_fila_por_pedido(self):
        _, pedidos = self.construir()
        self.assertEqual(pedidos["referencia"].tolist(), ["P-1", "P-2"])
        self.assertTrue(pedidos["id_pedido"].is_unique)

    # Lineas, pares, importe, precio medio y tallas salen de sus lineas
    def test_metricas_de_sus_lineas(self):
        _, pedidos = self.construir()
        self.assertEqual(pedidos["num_lineas"].tolist(), [2, 1])
        self.assertEqual(pedidos["pares"].tolist(), [3, 2])
        self.assertEqual(pedidos["importe"].tolist(), [239.97, 239.80])
        self.assertEqual(pedidos["precio_medio_par"].tolist(), [79.99, 119.90])
        self.assertEqual(pedidos["num_tallas"].tolist(), [2, 1])
        # Lo calculado desde las lineas coincide con la cabecera de Acceso a Datos
        self.assertEqual(pedidos["pares"].tolist(), pedidos["cantidad_total"].tolist())

    # Anio, mes, trimestre, dia de la semana y antiguedad del pedido
    def test_variables_de_calendario(self):
        _, pedidos = self.construir()
        self.assertEqual(pedidos["anio"].tolist(), [2026, 2026])
        self.assertEqual(pedidos["mes"].tolist(), [10, 11])
        self.assertEqual(pedidos["anio_mes"].tolist(), ["2026-10", "2026-11"])
        self.assertEqual(pedidos["trimestre"].tolist(), [4, 4])
        self.assertEqual(pedidos["dia_semana"].tolist(), ["jueves", "lunes"])
        self.assertEqual(pedidos["antiguedad_dias"].tolist(), [39, 7])   # hasta la fecha de corte

    # P-1 es normal y confirmado; P-2 es custom y cancelado
    def test_indicadores_de_tipo_y_estado(self):
        _, pedidos = self.construir()
        self.assertEqual(pedidos["es_custom"].tolist(), [False, True])
        self.assertEqual(pedidos["es_cancelado"].tolist(), [False, True])
        self.assertEqual(pedidos["es_confirmado"].tolist(), [True, False])

    # El modelo del pedido solo se pone si todas sus lineas son del mismo modelo
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

    # Un pedido sin lineas tiene 0 lineas, 0 pares y 0 euros
    def test_pedido_sin_lineas(self):
        self.cambiar("lineas_pedido.csv", "102,11,M2-42,2,42,2,119.90,239.80\n", "")
        self.cambiar("pedidos.csv", "2,239.80", "0,0.00")
        _, pedidos = self.construir()
        pedido = pedidos[pedidos["referencia"] == "P-2"].iloc[0]
        self.assertEqual((pedido["num_lineas"], pedido["pares"], pedido["importe"]), (0, 0, 0.0))
        self.assertTrue(pd.isna(pedido["precio_medio_par"]))   # sin pares no hay precio medio
        self.assertTrue(pd.isna(pedido["modelo_pedido"]))

    # Una linea rechazada (cantidad 0) deja fuera tambien su pedido
    def test_filas_rechazadas_no_entran(self):
        self.cambiar("lineas_pedido.csv", "100,10,M1-40,1,40,1,", "100,10,M1-40,1,40,0,")
        lineas, pedidos = self.construir()
        self.assertEqual(pedidos["referencia"].tolist(), ["P-2"])
        self.assertEqual(lineas["id_linea"].tolist(), ["102"])


# Pedidos, pares e importe con los tres criterios
class PruebasImportesPorCriterio(PruebaAnalisis):

    # Tabla de importes por criterio, con el nombre del criterio como indice
    def criterios(self):
        _, pedidos = self.construir()
        return analiticas.importes_por_criterio(pedidos).set_index("criterio")

    # Registrados: 2 pedidos, 5 pares y 479.77; no cancelados y confirmados: 1, 3 y 239.97
    def test_tres_criterios(self):
        criterios = self.criterios()
        self.assertEqual(criterios.loc["registrados", ["pedidos", "pares", "importe_eur"]].tolist(), [2, 5, 479.77])
        self.assertEqual(criterios.loc["no_cancelados", ["pedidos", "pares", "importe_eur"]].tolist(), [1, 3, 239.97])
        self.assertEqual(criterios.loc["confirmados_en_adelante", ["pedidos", "pares", "importe_eur"]].tolist(), [1, 3, 239.97])
        self.assertEqual(set(criterios["iva"]), {"pendiente de confirmar"})

    # Un pedido en preparacion sigue contando como confirmado
    def test_un_pedido_que_avanza_sigue_contando(self):
        self.cambiar("pedidos.csv", "normal,confirmado,pagado", "normal,en_preparacion,pagado")
        self.assertEqual(self.criterios().loc["confirmados_en_adelante", "pedidos"], 1)

    # Un pendiente es demanda, pero no venta
    def test_pendiente_no_es_confirmado(self):
        self.cambiar("pedidos.csv", "normal,confirmado,pagado", "normal,pendiente,pendiente")
        criterios = self.criterios()
        self.assertEqual(criterios.loc["confirmados_en_adelante", "pedidos"], 0)
        self.assertEqual(criterios.loc["no_cancelados", "pedidos"], 1)


# Comparar dos pedidos campo a campo
class PruebasCompararPedidos(PruebaAnalisis):

    # P-1 y P-3: mismo cliente y mismos articulos, pero distinto id y estado
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


# Conciliacion con P-A, P-B y P-C
class PruebasConciliacion(PruebaAnalisis):

    CORRECTOS = SQL_CORRECTOS

    # Escribe los resultados SQL (con los cambios que se pidan) y concilia
    def conciliar(self, cambios=None):
        carpeta_sql = self.carpeta / "conciliacion_sql"
        carpeta_sql.mkdir(exist_ok=True)
        for archivo, texto in {**self.CORRECTOS, **(cambios or {})}.items():
            (carpeta_sql / archivo).write_text(texto, encoding="utf-8")
        lineas, pedidos = self.construir()
        return conciliacion.conciliar(carpeta_sql, pedidos, lineas)

    # Con los resultados correctos coinciden las 11 cifras
    def test_cifras_que_coinciden(self):
        tabla = self.conciliar()
        self.assertEqual(len(tabla), 11)   # P-A: 3 cifras, P-B: 2 estados x 3, P-C: 1 modelo x 2
        self.assertEqual(set(tabla["resultado"]), {"coincide"})

    # 3 centimos de diferencia ya no coinciden (la tolerancia es medio centimo)
    def test_importe_que_no_coincide(self):
        tabla = self.conciliar({"P-A.csv": "pedidos,pares_solicitados,importe_ventas\n1,3,240.00\n"})
        fila = tabla[(tabla["consulta"] == "P-A") & (tabla["indicador"] == "importe")].iloc[0]
        self.assertEqual(fila["resultado"], "NO COINCIDE")
        self.assertEqual(fila["diferencia"], -0.03)

    # Un estado que solo esta en SQL sale como "falta en Python"
    def test_estado_que_solo_esta_en_sql(self):
        tabla = self.conciliar({"P-B.csv": self.CORRECTOS["P-B.csv"] + "pendiente,1,1,10.00\n"})
        self.assertEqual(set(tabla.loc[tabla["clave"] == "pendiente", "resultado"]), {"falta en Python"})

    # Un modelo que solo esta en Python sale como "falta en SQL"
    def test_modelo_que_solo_esta_en_python(self):
        tabla = self.conciliar({"P-C.csv": "modelo,pares,pedidos\n"})
        self.assertEqual(set(tabla.loc[tabla["consulta"] == "P-C", "resultado"]), {"falta en SQL"})

    # Sin los CSV de SQL no se concilia (devuelve None)
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


# Contraste del caso N (N-1, N-2 y N-3)
class PruebasCasoN(PruebaAnalisis):

    # Evalua la calidad y calcula todas las tablas analiticas de los CSV de prueba
    def tablas(self):
        resultado = calidad.evaluar(self.carpeta)
        return analiticas.calcular_tablas(resultado["datos"], resultado["validos"])

    # Escribe los resultados del caso N (con los cambios que se pidan) y los contrasta
    def contrastar(self, cambios=None):
        carpeta_sql = self.carpeta / "conciliacion_sql"
        carpeta_sql.mkdir(exist_ok=True)
        for archivo, texto in {**SQL_CASO_N, **(cambios or {})}.items():
            (carpeta_sql / archivo).write_text(texto, encoding="utf-8")
        return conciliacion.contrastar_caso_n(carpeta_sql, self.tablas())

    # Con los resultados correctos coinciden N-1, N-2 y N-3
    def test_las_tres_cifras_coinciden(self):
        tabla = self.contrastar()
        # N-1: pedidos, pares e importe; N-2: 2 celdas con pares; N-3: 3 criterios
        self.assertEqual(tabla["consulta"].value_counts().to_dict(), {"N-1": 3, "N-2": 2, "N-3": 3})
        self.assertEqual(set(tabla["resultado"]), {"coincide"})
        importe = tabla[(tabla["consulta"] == "N-1") & (tabla["indicador"] == "importe")].iloc[0]
        self.assertEqual((importe["clave"], importe["valor_python"]), ("2026-10", 239.97))

    # Un mes sin ventas da 0 en SQL y 0 en Python
    def test_mes_sin_ventas_es_cero_en_los_dos_lados(self):
        # En noviembre solo hay un pedido cancelado, que no es venta
        tabla = self.contrastar({"N-1.csv": "anio_mes,pedidos,pares,importe\n2026-11,0,0,0.00\n"})
        mes = tabla[tabla["consulta"] == "N-1"]
        self.assertEqual(set(mes["clave"]), {"2026-11"})
        self.assertEqual(set(mes["resultado"]), {"coincide"})

    # Se detecta una celda de mas en N-2 y un cliente de mas en N-3
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

    # Sin los CSV del caso N no se contrasta (devuelve None)
    def test_sin_resultados_queda_pendiente(self):
        carpeta_sql = self.carpeta / "no_existe"
        self.assertIsNone(conciliacion.contrastar_caso_n(carpeta_sql, self.tablas()))
        self.assertEqual(conciliacion.faltan_resultados(carpeta_sql, conciliacion.CONSULTAS_CASO_N),
                         ["N-1.csv", "N-2.csv", "N-3.csv"])


# Caso A: un pedido Custom de 40 pares en 4 tallas
class PruebasCasoA(PruebaAnalisis):

    # Lineas del pedido: id_linea -> (sku, talla, pares)
    LINEAS = {"103": ("M1-40", 40, 10), "104": ("M1-41", 41, 10), "105": ("M1-42", 42, 12), "106": ("M1-43", 43, 8)}

    # Se cuenta linea a linea y suma un solo pedido de 40 pares a los KPIs
    def test_pedido_custom_de_40_pares_linea_a_linea(self):
        sin_el = kpis.calcular_kpis(*self.tablas_para_kpis())
        self.anadir("stock.csv", "M1-42,1,Blanco,42,true,30,2026-11-09 19:00:00\n"
                                 "M1-43,1,Blanco,43,true,30,2026-11-09 19:00:00\n")
        self.anadir("pedidos.csv", "12,C-40,2,2026-11-03 09:00:00,custom,confirmado,pendiente,Logo del club,40,3199.60\n")
        self.anadir("lineas_pedido.csv", "".join(f"{linea},12,{sku},1,{talla},{pares},79.99,{pares * 79.99:.2f}\n"
                                                 for linea, (sku, talla, pares) in self.LINEAS.items()))
        resultado = calidad.evaluar(self.carpeta)
        self.assertEqual(len(resultado["incidencias"]), 0)
        tablas = analiticas.calcular_tablas(resultado["datos"], resultado["validos"])
        # Linea a linea: cada linea del CSV es una fila, con su talla, sus pares y su importe
        suyas = tablas["lineas_enriquecidas"].set_index("id_linea").loc[list(self.LINEAS)]
        for linea, (sku, talla, pares) in self.LINEAS.items():
            self.assertEqual((suyas.loc[linea, "sku"], suyas.loc[linea, "talla"], suyas.loc[linea, "cantidad"]),
                             (sku, talla, pares))
            self.assertAlmostEqual(suyas.loc[linea, "importe_linea"], round(pares * 79.99, 2))
        # Un solo pedido de 40 pares y 4 tallas
        pedido = tablas["pedidos_unicos"].set_index("referencia").loc["C-40"]
        self.assertEqual((pedido["num_lineas"], pedido["num_tallas"], pedido["pares"]), (4, 4, 40))
        self.assertEqual(pedido["importe"], 3199.60)
        # La matriz modelo x talla suma cada linea en su talla
        matriz = tablas["matriz_modelo_talla"].loc["Modelo Uno"]
        self.assertEqual([matriz[talla] for talla in [40, 41, 42, 43]], [11, 12, 12, 8])   # P-1 ya tenia 1 y 2
        # Los KPIs suben exactamente un pedido, 40 pares y su importe
        con_el = kpis.calcular_kpis(tablas["pedidos_unicos"], tablas["modelos_abc"], tablas["ventas_por_talla"],
                                    tablas["stock_variantes"], tablas["ventas_por_periodo"])
        antes = dict(zip(sin_el["codigo"], sin_el["valor"]))
        despues = dict(zip(con_el["codigo"], con_el["valor"]))
        self.assertEqual(despues["K01"] - antes["K01"], 1)
        self.assertEqual(despues["K04"] - antes["K04"], 40)
        self.assertEqual(despues["K05"] - antes["K05"], 40)
        self.assertAlmostEqual(despues["K07"] - antes["K07"], 3199.60, places=2)

    # Las tablas que necesita calcular_kpis, en su orden
    def tablas_para_kpis(self):
        resultado = calidad.evaluar(self.carpeta)
        tablas = analiticas.calcular_tablas(resultado["datos"], resultado["validos"])
        return (tablas["pedidos_unicos"], tablas["modelos_abc"], tablas["ventas_por_talla"], tablas["stock_variantes"],
                tablas["ventas_por_periodo"])
