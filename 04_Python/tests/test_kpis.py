import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "modulos"))   # los modulos estan en ../modulos

import config
import kpis
from test_analiticas import SQL_CORRECTOS
from test_tablas import PruebaTablas


# Base: calcula los KPIs de los CSV de prueba
class PruebaKpis(PruebaTablas):

    # Tabla de KPIs con el codigo como indice
    def calcular(self):
        tablas = self.tablas()
        tabla = kpis.calcular_kpis(tablas["pedidos_unicos"], tablas["modelos_abc"], tablas["ventas_por_talla"],
                                   tablas["stock_variantes"], tablas["ventas_por_periodo"])
        return tabla.set_index("codigo")

    # Valor de un KPI concreto, por ejemplo el de K01
    def valor(self, tabla, codigo):
        return tabla.loc[codigo, "valor"]


# Valor de cada KPI con los datos de prueba
class PruebasKpis(PruebaKpis):

    # Columnas de la tabla, codigos sin repetir y todos con formula y unidad
    def test_columnas_y_codigos_unicos(self):
        tabla = self.calcular().reset_index()
        self.assertEqual(list(tabla.columns), kpis.COLUMNAS)
        self.assertTrue(tabla["codigo"].is_unique)
        self.assertTrue(tabla["formula"].str.len().gt(0).all())
        self.assertTrue(tabla["unidad"].str.len().gt(0).all())

    # Con los CSV de prueba al menos 12 de los 20 KPIs salen con estado "calculado"
    def test_doce_o_mas_kpis_calculados(self):
        tabla = self.calcular()
        self.assertGreaterEqual((tabla["estado"] == "calculado").sum(), 12)

    # K01 a K03: 2 pedidos registrados, 1 confirmado (P-1) y 1 cancelado (P-2)
    def test_estados_de_los_pedidos(self):
        tabla = self.calcular()
        self.assertEqual(self.valor(tabla, "K01"), 2)
        self.assertEqual(self.valor(tabla, "K02"), 1)
        self.assertEqual(self.valor(tabla, "K03"), 1)

    # K06 a K08: importe registrado, confirmado y con pago registrado
    def test_registrado_confirmado_y_pagado_son_distintos(self):
        tabla = self.calcular()
        self.assertEqual(self.valor(tabla, "K06"), 479.77)   # 239.97 + 239.80: incluye el cancelado
        self.assertEqual(self.valor(tabla, "K07"), 239.97)
        self.assertEqual(self.valor(tabla, "K08"), 239.97)   # P-1 esta pagado

    # Confirmado no quiere decir pagado
    def test_pagado_no_se_supone(self):
        self.cambiar("pedidos.csv", "normal,confirmado,pagado", "normal,confirmado,pendiente")
        tabla = self.calcular()
        self.assertEqual(self.valor(tabla, "K07"), 239.97)   # sigue confirmado...
        self.assertEqual(self.valor(tabla, "K08"), 0.0)      # ...pero nadie lo ha marcado pagado

    # K09 a K11: ticket medio, pares por pedido y precio medio por par
    def test_ticket_pares_y_precio_medio(self):
        tabla = self.calcular()
        self.assertEqual(self.valor(tabla, "K09"), 239.97)   # 239.97 € / 1 pedido, no / 2 lineas
        self.assertEqual(self.valor(tabla, "K10"), 3.0)
        self.assertEqual(self.valor(tabla, "K11"), 79.99)

    # K04 = 3: solo cuentan los pares de P-1, los 2 del pedido cancelado no
    def test_pares_solicitados_sin_cancelados(self):
        self.assertEqual(self.valor(self.calcular(), "K04"), 3)

    # K12 a K14: pedidos Custom, modelo y talla mas solicitados
    def test_custom_y_mas_solicitados(self):
        tabla = self.calcular()
        self.assertEqual(self.valor(tabla, "K12"), 0.0)      # el unico custom esta cancelado
        self.assertEqual(self.valor(tabla, "K13"), 3)
        self.assertIn("Modelo Uno", tabla.loc["K13", "detalle"])
        self.assertEqual(self.valor(tabla, "K14"), 2)
        self.assertIn("41", tabla.loc["K14", "detalle"])

    # Si las tallas 40 y 41 empatan a 1 par, el detalle de K14 nombra las dos
    def test_empate_en_lo_mas_solicitado_nombra_a_todos(self):
        self.cambiar("lineas_pedido.csv", "101,10,M1-41,1,41,2,79.99,159.98", "101,10,M1-41,1,41,1,79.99,79.99")
        self.cambiar("pedidos.csv", "3,239.97", "2,159.98")
        tabla = self.calcular()
        self.assertIn("40, 41", tabla.loc["K14", "detalle"])

    # K16 y K17: 17 pares de stock en total y 2 SKU con stock bajo
    def test_inventario(self):
        tabla = self.calcular()
        self.assertEqual(self.valor(tabla, "K16"), 17)
        self.assertEqual(self.valor(tabla, "K17"), 2)

    # K18 y K19 NO CALCULABLE; K20 sin demanda reciente
    def test_no_calculables(self):
        tabla = self.calcular()
        self.assertEqual(tabla.loc["K18", "estado"], "NO CALCULABLE")   # margen sin coste
        self.assertEqual(tabla.loc["K19", "estado"], "NO CALCULABLE")   # un solo mes de ventas
        self.assertTrue(pd.isna(self.valor(tabla, "K18")))
        self.assertIn("N/D", tabla.loc["K20", "detalle"])               # sin demanda en 28 dias

    # Con dos meses ya se calculan K19 y K20
    def test_con_dos_meses(self):
        self.anadir_otro_mes()
        tabla = self.calcular()
        self.assertEqual(self.valor(tabla, "K19"), 33.3)
        self.assertEqual(self.valor(tabla, "K20"), 22.7)   # 17 pares de stock / (3 pares pedidos en 28 dias / 4)

    # Sin pedidos no se divide entre cero: "sin datos" o NO CALCULABLE
    def test_sin_pedidos_no_divide_entre_cero(self):
        self.vaciar_lineas()
        tabla = self.calcular()
        self.assertEqual(self.valor(tabla, "K01"), 0)
        self.assertEqual(tabla.loc["K09", "estado"], "sin datos")
        self.assertEqual(tabla.loc["K13", "estado"], "sin datos")
        self.assertEqual(tabla.loc["K20", "estado"], "NO CALCULABLE")


# KPIs frente a las consultas P-A y P-B
class PruebasCoherenciaConSql(PruebaKpis):

    # Escribe los resultados SQL (con los cambios que se pidan)
    def escribir_sql(self, cambios=None):
        carpeta_sql = self.carpeta / config.CARPETA_SQL
        carpeta_sql.mkdir(exist_ok=True)
        for archivo, texto in {**SQL_CORRECTOS, **(cambios or {})}.items():
            (carpeta_sql / archivo).write_text(texto, encoding="utf-8")
        return carpeta_sql

    # Con los resultados correctos coinciden los 7 KPIs
    def test_kpis_coinciden_con_postgresql(self):
        carpeta_sql = self.escribir_sql()
        coherencia = kpis.coherencia_con_sql(self.calcular().reset_index(), carpeta_sql)
        self.assertEqual(len(coherencia), 7)
        self.assertEqual(set(coherencia["resultado"]), {"coincide"})

    # Un importe distinto en P-B sale como NO COINCIDE
    def test_kpi_que_no_coincide(self):
        carpeta_sql = self.escribir_sql({"P-B.csv": "estado,pedidos,pares,importe\n"
                                                    "confirmado,1,3,239.97\ncancelado,1,2,250.00\n"})
        coherencia = kpis.coherencia_con_sql(self.calcular().reset_index(), carpeta_sql)
        fila = coherencia[coherencia["indicador"] == "K06 importe registrado"].iloc[0]
        self.assertEqual(fila["resultado"], "NO COINCIDE")

    # Sin los CSV de SQL no hay comparacion (None)
    def test_sin_resultados_sql(self):
        self.assertIsNone(kpis.coherencia_con_sql(self.calcular().reset_index(), self.carpeta / "no_existe"))
