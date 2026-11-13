"""
Pruebas de la estadistica descriptiva, las tres hipotesis y el bootstrap (estadistica.py).
"""
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

import analiticas
import calidad
import config
import estadistica
import generador_datos
from test_tablas import PruebaTablas


def tablas_sinteticas():
    """Las tablas de analisis de los datos sinteticos (se calculan una sola vez)."""
    if not hasattr(tablas_sinteticas, "cache"):
        with tempfile.TemporaryDirectory() as temporal:
            carpeta = generador_datos.guardar(generador_datos.generar(config.SEMILLA), Path(temporal), "test")
            resultado = calidad.evaluar(carpeta)
            tablas_sinteticas.cache = analiticas.calcular_tablas(resultado["datos"], resultado["validos"])
    return tablas_sinteticas.cache


class PruebasDescriptivos(unittest.TestCase):

    def test_valores_conocidos(self):
        fila = estadistica.describir([1, 2, 3, 4, 100], "x", "todos", "€", con_moda=False)
        self.assertEqual((fila["n"], fila["media"], fila["mediana"]), (5, 22.0, 3.0))
        self.assertEqual((fila["minimo"], fila["p25"], fila["p75"], fila["maximo"]), (1.0, 2.0, 4.0, 100.0))
        self.assertEqual(fila["rango_intercuartilico"], 2.0)
        self.assertEqual(fila["desviacion_tipica"], round(np.std([1, 2, 3, 4, 100], ddof=1), 2))
        self.assertEqual(fila["mejor_resumen"], "mediana")          # el 100 arrastra la media
        self.assertIsNone(fila["moda"])

    def test_simetrica_y_moda(self):
        fila = estadistica.describir([10, 11, 11, 12], "x", "todos", "pares", con_moda=True)
        self.assertEqual(fila["mejor_resumen"], "media")
        self.assertEqual(fila["moda"], 11)

    def test_sin_datos(self):
        fila = estadistica.describir([], "x", "todos", "€", con_moda=False)
        self.assertEqual((fila["n"], fila["mejor_resumen"]), (0, "sin datos"))

    def test_descriptivos_de_los_sinteticos(self):
        tablas = tablas_sinteticas()
        tabla = estadistica.descriptivos(tablas)
        self.assertEqual(len(tabla), 9)                               # 3 variables x 3 grupos
        demanda = analiticas.de_demanda(tablas["pedidos_unicos"])
        fila = tabla[(tabla["variable"] == "importe por pedido") & (tabla["grupo"] == "todos")].iloc[0]
        self.assertEqual(fila["n"], len(demanda))
        self.assertEqual(fila["media"], round(demanda["importe"].mean(), 2))
        self.assertEqual(fila["mejor_resumen"], "mediana")            # los Custom arrastran la media


class PruebasBootstrap(unittest.TestCase):

    VALORES = np.array([12.0, 15, 9, 22, 30, 11, 14, 18, 25, 16, 13, 20])

    def test_reproducible_con_la_misma_semilla(self):
        self.assertEqual(estadistica.bootstrap_media(self.VALORES), estadistica.bootstrap_media(self.VALORES))
        self.assertNotEqual(estadistica.bootstrap_media(self.VALORES, semilla=1),
                            estadistica.bootstrap_media(self.VALORES, semilla=2))

    def test_el_intervalo_contiene_la_media(self):
        inferior, superior = estadistica.bootstrap_media(self.VALORES)
        self.assertLessEqual(inferior, self.VALORES.mean())
        self.assertGreaterEqual(superior, self.VALORES.mean())

    def test_con_mas_datos_el_intervalo_es_mas_estrecho(self):
        pocos = estadistica.bootstrap_media(self.VALORES)
        muchos = estadistica.bootstrap_media(np.tile(self.VALORES, 50))
        self.assertLess(muchos[1] - muchos[0], pocos[1] - pocos[0])

    def test_ticket_medio_de_los_sinteticos(self):
        pedidos = tablas_sinteticas()["pedidos_unicos"]
        fila = estadistica.bootstrap_ticket_medio(pedidos, "SINTETICO").iloc[0]
        venta = analiticas.de_venta(pedidos)
        self.assertEqual(fila["n"], len(venta))
        self.assertEqual(fila["estimacion"], round(venta["importe"].mean(), 2))
        self.assertEqual(fila["resultado"], "calculado")
        self.assertLess(fila["ic_inferior"], fila["estimacion"])
        self.assertGreater(fila["ic_superior"], fila["estimacion"])
        self.assertEqual((fila["remuestreos"], fila["semilla"]), (config.BOOTSTRAP_REMUESTREOS, config.SEMILLA))
        self.assertIn("SINTÉTICOS", fila["interpretacion"])

    def test_ticket_con_pocos_pedidos(self):
        pedidos = pd.DataFrame({"es_confirmado": [True, True], "importe": [100.0, 120.0]})
        fila = estadistica.bootstrap_ticket_medio(pedidos, "PRUEBA").iloc[0]
        self.assertEqual(fila["resultado"], "NO CALCULABLE")


class PruebasHipotesis(PruebaTablas):

    def test_veredicto(self):
        self.assertEqual(estadistica.veredicto(5, 10, 0), "los datos la apoyan")
        self.assertEqual(estadistica.veredicto(-10, -5, 0), "los datos la contradicen")
        self.assertTrue(estadistica.veredicto(-1, 1, 0).startswith("evidencia insuficiente"))

    def test_tres_hipotesis_completas(self):
        tabla = estadistica.contrastar_hipotesis(tablas_sinteticas(), "SINTETICO")
        self.assertEqual(tabla["codigo"].tolist(), ["H1", "H2", "H3"])
        self.assertEqual(list(tabla.columns), estadistica.COLUMNAS_HIPOTESIS)
        for columna in ["pregunta", "variable", "metodo", "resultado", "interpretacion", "limitaciones",
                        "no_se_puede_afirmar"]:
            self.assertTrue(tabla[columna].str.len().gt(0).all(), columna)
        self.assertTrue(tabla["interpretacion"].str.contains("SINTÉTICOS").all())

    def test_resultados_reproducibles(self):
        primera = estadistica.contrastar_hipotesis(tablas_sinteticas(), "SINTETICO")
        segunda = estadistica.contrastar_hipotesis(tablas_sinteticas(), "SINTETICO")
        pd.testing.assert_frame_equal(primera, segunda)

    def test_h1_con_sinteticos(self):
        fila = estadistica.contrastar_hipotesis(tablas_sinteticas(), "SINTETICO").iloc[0]
        self.assertEqual(fila["resultado"], "los datos la apoyan")
        self.assertLess(fila["ic_inferior"], fila["estimacion"])
        self.assertGreater(fila["ic_superior"], fila["estimacion"])

    def test_pocos_datos_evidencia_insuficiente(self):
        # Los CSV pequenos de las pruebas: un solo mes y ningun Custom sin cancelar
        tabla = estadistica.contrastar_hipotesis(self.tablas(), "PRUEBA").set_index("codigo")
        self.assertTrue(tabla.loc["H1", "resultado"].startswith("evidencia insuficiente"))
        self.assertTrue(tabla.loc["H3", "resultado"].startswith("evidencia insuficiente"))
        self.assertIn("12 meses", tabla.loc["H3", "resultado"])

    def test_h3_detecta_un_crecimiento_claro(self):
        meses = pd.period_range("2025-01", periods=12, freq="M")
        pedidos = pd.DataFrame({"fecha_pedido": [mes.to_timestamp() for mes in meses],
                                "pares": [10] * 6 + [100] * 6, "es_cancelado": [False] * 12})
        fila = estadistica.hipotesis_crecimiento(pedidos, "PRUEBA")
        self.assertEqual(fila["estimacion"], 90.0)
        self.assertEqual(fila["resultado"], "los datos la apoyan")
