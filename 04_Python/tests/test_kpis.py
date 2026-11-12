"""
Pruebas de los KPIs (kpis.py) y de su coherencia con las consultas SQL.

Con los CSV validos de test_pipeline.py:
  P-1 confirmado y pagado, 3 pares, 239.97 €;  P-2 cancelado y reembolsado, 2 pares, 239.80 €.
"""
import pandas as pd

import config
import kpis
from test_analiticas import SQL_CORRECTOS
from test_tablas import PruebaTablas


class PruebaKpis(PruebaTablas):

    def calcular(self):
        tablas = self.tablas()
        tabla = kpis.calcular_kpis(tablas["pedidos_unicos"], tablas["modelos_abc"], tablas["ventas_por_talla"],
                                   tablas["stock_variantes"], tablas["ventas_por_periodo"])
        return tabla.set_index("codigo")

    def valor(self, tabla, codigo):
        return tabla.loc[codigo, "valor"]


class PruebasKpis(PruebaKpis):

    def test_columnas_y_codigos_unicos(self):
        tabla = self.calcular().reset_index()
        self.assertEqual(list(tabla.columns), kpis.COLUMNAS)
        self.assertTrue(tabla["codigo"].is_unique)
        self.assertTrue(tabla["formula"].str.len().gt(0).all())   # todos llevan formula
        self.assertTrue(tabla["unidad"].str.len().gt(0).all())    # y unidad

    def test_doce_o_mas_kpis_calculados(self):
        tabla = self.calcular()
        self.assertGreaterEqual((tabla["estado"] == "calculado").sum(), 12)

    def test_estados_de_los_pedidos(self):
        tabla = self.calcular()
        self.assertEqual(self.valor(tabla, "K01"), 2)    # registrados
        self.assertEqual(self.valor(tabla, "K02"), 1)    # confirmados
        self.assertEqual(self.valor(tabla, "K03"), 1)    # cancelados

    def test_registrado_confirmado_y_pagado_son_distintos(self):
        tabla = self.calcular()
        self.assertEqual(self.valor(tabla, "K06"), 479.77)   # registrado: incluye el cancelado
        self.assertEqual(self.valor(tabla, "K07"), 239.97)   # confirmado
        self.assertEqual(self.valor(tabla, "K08"), 239.97)   # con pago registrado (P-1 esta pagado)

    def test_pagado_no_se_supone(self):
        self.cambiar("pedidos.csv", "normal,confirmado,pagado", "normal,confirmado,pendiente")
        tabla = self.calcular()
        self.assertEqual(self.valor(tabla, "K07"), 239.97)   # sigue confirmado...
        self.assertEqual(self.valor(tabla, "K08"), 0.0)      # ...pero nadie lo ha marcado pagado

    def test_ticket_pares_y_precio_medio(self):
        tabla = self.calcular()
        self.assertEqual(self.valor(tabla, "K09"), 239.97)   # 239.97 € / 1 pedido, no / 2 lineas
        self.assertEqual(self.valor(tabla, "K10"), 3.0)
        self.assertEqual(self.valor(tabla, "K11"), 79.99)

    def test_pares_solicitados_sin_cancelados(self):
        self.assertEqual(self.valor(self.calcular(), "K04"), 3)

    def test_custom_y_mas_solicitados(self):
        tabla = self.calcular()
        self.assertEqual(self.valor(tabla, "K12"), 0.0)      # el unico custom esta cancelado
        self.assertEqual(self.valor(tabla, "K13"), 3)
        self.assertIn("Modelo Uno", tabla.loc["K13", "detalle"])
        self.assertEqual(self.valor(tabla, "K14"), 2)
        self.assertIn("41", tabla.loc["K14", "detalle"])

    def test_empate_en_lo_mas_solicitado_nombra_a_todos(self):
        self.cambiar("lineas_pedido.csv", "101,10,M1-41,1,41,2,79.99,159.98", "101,10,M1-41,1,41,1,79.99,79.99")
        self.cambiar("pedidos.csv", "3,239.97", "2,159.98")
        tabla = self.calcular()
        self.assertIn("40, 41", tabla.loc["K14", "detalle"])

    def test_inventario(self):
        tabla = self.calcular()
        self.assertEqual(self.valor(tabla, "K16"), 17)
        self.assertEqual(self.valor(tabla, "K17"), 2)

    def test_no_calculables(self):
        tabla = self.calcular()
        self.assertEqual(tabla.loc["K18", "estado"], "NO CALCULABLE")   # margen sin coste
        self.assertEqual(tabla.loc["K19", "estado"], "NO CALCULABLE")   # un solo mes de ventas
        self.assertTrue(pd.isna(self.valor(tabla, "K18")))
        self.assertIn("N/D", tabla.loc["K20", "detalle"])               # sin demanda en 28 dias

    def test_con_dos_meses(self):
        self.anadir_otro_mes()
        tabla = self.calcular()
        self.assertEqual(self.valor(tabla, "K19"), 33.3)
        self.assertEqual(self.valor(tabla, "K20"), 22.7)   # 17 pares / (3 pares en 28 dias / 4)

    def test_sin_pedidos_no_divide_entre_cero(self):
        self.vaciar_lineas()
        tabla = self.calcular()
        self.assertEqual(self.valor(tabla, "K01"), 0)
        self.assertEqual(tabla.loc["K09", "estado"], "sin datos")
        self.assertEqual(tabla.loc["K13", "estado"], "sin datos")
        self.assertEqual(tabla.loc["K20", "estado"], "NO CALCULABLE")


class PruebasCoherenciaConSql(PruebaKpis):

    def escribir_sql(self, cambios=None):
        carpeta_sql = self.carpeta / config.CARPETA_SQL
        carpeta_sql.mkdir(exist_ok=True)
        for archivo, texto in {**SQL_CORRECTOS, **(cambios or {})}.items():
            (carpeta_sql / archivo).write_text(texto, encoding="utf-8")
        return carpeta_sql

    def test_kpis_coinciden_con_postgresql(self):
        carpeta_sql = self.escribir_sql()
        coherencia = kpis.coherencia_con_sql(self.calcular().reset_index(), carpeta_sql)
        self.assertEqual(len(coherencia), 7)
        self.assertEqual(set(coherencia["resultado"]), {"coincide"})

    def test_kpi_que_no_coincide(self):
        carpeta_sql = self.escribir_sql({"P-B.csv": "estado,pedidos,pares,importe\n"
                                                    "confirmado,1,3,239.97\ncancelado,1,2,250.00\n"})
        coherencia = kpis.coherencia_con_sql(self.calcular().reset_index(), carpeta_sql)
        fila = coherencia[coherencia["indicador"] == "K06 importe registrado"].iloc[0]
        self.assertEqual(fila["resultado"], "NO COINCIDE")

    def test_sin_resultados_sql(self):
        self.assertIsNone(kpis.coherencia_con_sql(self.calcular().reset_index(), self.carpeta / "no_existe"))
