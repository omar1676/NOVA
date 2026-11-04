"""
Pruebas de los filtros combinables (filtros.py), de las tablas de inventario
con umbral y de la descarga CSV del dashboard (pipeline.csv_descarga).

Usan los datos sinteticos (900 pedidos), generados en una carpeta temporal.
Cada resultado filtrado se compara con lo que sale de filtrar a mano las
lineas validas: asi se comprueba que los filtros cambian de verdad los
calculos y que no duplican pedidos ni importes.
"""
import io
import tempfile
import unittest
from pathlib import Path

import pandas as pd

import analiticas
import calidad
import config
import filtros
import generador_datos
import kpis
import pipeline


def sinteticos():
    """calidad.evaluar de los datos sinteticos (se calcula una sola vez)."""
    if not hasattr(sinteticos, "cache"):
        with tempfile.TemporaryDirectory() as temporal:
            carpeta = generador_datos.guardar(generador_datos.generar(config.SEMILLA), Path(temporal), "test")
            sinteticos.cache = calidad.evaluar(carpeta)
            sinteticos.cache["tablas"] = analiticas.calcular_tablas(sinteticos.cache["datos"],
                                                                    sinteticos.cache["validos"])
    return sinteticos.cache


def con_filtros(**cambios):
    return {**filtros.SIN_FILTROS, **cambios}


def calcular(**cambios):
    resultado = sinteticos()
    return filtros.calcular_filtrado(resultado["datos"], resultado["validos"], con_filtros(**cambios))


def valor(tablas, codigo):
    tabla = tablas["kpis"]
    return tabla.loc[tabla["codigo"] == codigo, "valor"].iloc[0]


class PruebasFiltros(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.resultado = sinteticos()
        cls.lineas = cls.resultado["tablas"]["lineas_enriquecidas"]   # todas las lineas validas, sin filtrar

    def test_sin_filtros_no_restringe_nada(self):
        tablas = calcular()
        completas = self.resultado["tablas"]
        pd.testing.assert_frame_equal(tablas["pedidos_unicos"], completas["pedidos_unicos"])
        esperados = kpis.calcular_kpis(completas["pedidos_unicos"], completas["modelos_abc"],
                                       completas["ventas_por_talla"], completas["stock_variantes"],
                                       completas["ventas_por_periodo"])
        pd.testing.assert_frame_equal(tablas["kpis"], esperados)
        self.assertFalse(filtros.hay_filtros(filtros.SIN_FILTROS))
        self.assertEqual(filtros.describir(filtros.SIN_FILTROS), "ninguno")

    def test_periodo_incluye_el_dia_final(self):
        dia = "2026-10-20"
        tablas = calcular(desde=dia, hasta=dia)
        pedidos = self.resultado["validos"]["pedidos"]
        del_dia = pedidos[pedidos["fecha_pedido"].dt.date == pd.Timestamp(dia).date()]
        self.assertGreater(len(del_dia), 0)
        self.assertEqual(sorted(tablas["pedidos_unicos"]["id_pedido"]), sorted(del_dia["id_pedido"]))

    def test_tipo_y_estado_son_del_pedido(self):
        tablas = calcular(tipos=["custom"], estados=["entregado"])
        pedidos = tablas["pedidos_unicos"]
        self.assertTrue((pedidos["tipo_pedido"] == "custom").all())
        self.assertTrue((pedidos["estado_pedido"] == "entregado").all())
        validos = self.resultado["validos"]["pedidos"]
        esperados = validos[(validos["tipo_pedido"] == "custom") & (validos["estado_pedido"] == "entregado")]
        self.assertEqual(len(pedidos), len(esperados))

    def test_modelo_solo_aporta_sus_lineas(self):
        tablas = calcular(modelos=["SINT Runner"])
        lineas = tablas["lineas_enriquecidas"]
        self.assertEqual(set(lineas["nombre_modelo"]), {"SINT Runner"})
        del_modelo = self.lineas[self.lineas["nombre_modelo"] == "SINT Runner"]
        pedidos = tablas["pedidos_unicos"].set_index("id_pedido")
        # Cada pedido cuenta una vez y sus pares e importe son solo los de ese modelo
        self.assertTrue(pedidos.index.is_unique)
        self.assertEqual(len(pedidos), del_modelo["id_pedido"].nunique())
        por_pedido = del_modelo.groupby("id_pedido")["cantidad"].sum()
        self.assertEqual(pedidos["pares"].to_dict(), por_pedido.to_dict())
        # Hay pedidos con varios modelos (si no, la prueba no comprobaria nada)
        multimodelo = self.resultado["tablas"]["pedidos_unicos"]
        self.assertTrue(multimodelo.loc[multimodelo["id_pedido"].isin(pedidos.index), "pedido_multimodelo"].any())

    def test_talla_es_de_la_linea(self):
        tablas = calcular(tallas=[42])
        self.assertEqual(set(tablas["lineas_enriquecidas"]["talla"]), {42})
        self.assertEqual(int(valor(tablas, "K04")),
                         int(analiticas.de_demanda(self.lineas[self.lineas["talla"] == 42])["cantidad"].sum()))

    def test_cuatro_filtros_combinados(self):
        tablas = calcular(desde="2026-01-01", hasta="2026-06-30", modelos=["SINT Runner", "SINT Court"],
                          tipos=["normal"], estados=["entregado", "enviado"])
        lineas = self.lineas
        esperadas = lineas[(lineas["fecha_pedido"] >= "2026-01-01") & (lineas["fecha_pedido"] < "2026-07-01")
                           & lineas["nombre_modelo"].isin(["SINT Runner", "SINT Court"])
                           & (lineas["tipo_pedido"] == "normal") & lineas["estado_pedido"].isin(["entregado", "enviado"])]
        self.assertGreater(len(esperadas), 0)
        self.assertEqual(sorted(tablas["lineas_enriquecidas"]["id_linea"]), sorted(esperadas["id_linea"]))
        self.assertEqual(sorted(tablas["pedidos_unicos"]["id_pedido"]), sorted(esperadas["id_pedido"].unique()))
        self.assertEqual(valor(tablas, "K01"), esperadas["id_pedido"].nunique())
        self.assertEqual(valor(tablas, "K06"), round(float(esperadas["importe_linea"].sum()), 2))
        texto = filtros.describir(con_filtros(desde="2026-01-01", hasta="2026-06-30", modelos=["SINT Runner"],
                                              tipos=["normal"], estados=["entregado"]))
        self.assertEqual(texto, "periodo 2026-01-01 a 2026-06-30 · modelo: SINT Runner · tipo: normal · "
                                "estado: entregado")

    def test_sin_duplicar_pedidos_ni_importes(self):
        # Filtrando modelo a modelo, los pares y los euros suman lo mismo que sin filtrar
        completas = calcular()
        pares = importe = 0
        for modelo in self.resultado["validos"]["modelos"]["nombre_modelo"]:
            tablas = calcular(modelos=[modelo])
            self.assertTrue(tablas["pedidos_unicos"]["id_pedido"].is_unique)
            pares += valor(tablas, "K04")
            importe += valor(tablas, "K06")
        self.assertEqual(pares, valor(completas, "K04"))
        self.assertAlmostEqual(importe, valor(completas, "K06"), delta=0.01 * len(self.resultado["validos"]["modelos"]))

    def test_kpis_filtrados_coherentes(self):
        tablas = calcular(tipos=["custom"], desde="2025-09-01", hasta="2026-03-31")
        pedidos = tablas["pedidos_unicos"]
        venta = pedidos[pedidos["es_confirmado"]]
        self.assertEqual(valor(tablas, "K01"), len(pedidos))
        self.assertEqual(valor(tablas, "K02"), len(venta))
        self.assertEqual(valor(tablas, "K07"), round(float(venta["importe"].sum()), 2))
        self.assertEqual(valor(tablas, "K09"), round(valor(tablas, "K07") / valor(tablas, "K02"), 2))
        # Las tablas dicen lo mismo que los KPIs
        self.assertEqual(tablas["ventas_por_periodo"]["importe"].sum().round(2), valor(tablas, "K07"))
        normal = tablas["custom_vs_estandar"].set_index("tipo_pedido").loc["normal"]
        self.assertEqual(normal["pedidos_registrados"], 0)

    def test_filtro_sin_resultados(self):
        tablas = calcular(desde="2030-01-01", hasta="2030-12-31")
        self.assertEqual(len(tablas["pedidos_unicos"]), 0)
        self.assertEqual(valor(tablas, "K01"), 0)
        self.assertIsNone(valor(tablas, "K09"))                       # sin pedidos no hay ticket (no 0)
        self.assertEqual(tablas["ventas_por_periodo"]["estado"].iloc[0], analiticas.NO_CALCULABLE)


class PruebasInventario(unittest.TestCase):

    def setUp(self):
        self.resultado = sinteticos()
        self.corte = self.resultado["datos"]["stock"]["fecha_corte"].max()

    def inventario(self, umbral=config.UMBRAL_STOCK_BAJO, **cambios):
        return filtros.tablas_inventario(self.resultado["validos"], self.resultado["tablas"], self.corte,
                                         con_filtros(**cambios), umbral)

    def test_solo_modelo_y_talla(self):
        stock, _ = self.inventario(modelos=["SINT Runner"], tallas=[42])
        self.assertEqual(set(stock["nombre_modelo"]), {"SINT Runner"})
        self.assertEqual(set(stock["talla"]), {42})
        # El periodo, el tipo y el estado no cambian el stock ni la demanda de 28 dias
        otro, _ = self.inventario(modelos=["SINT Runner"], tallas=[42], tipos=["custom"], desde="2025-05-01",
                                  hasta="2025-06-01", estados=["cancelado"])
        pd.testing.assert_frame_equal(stock, otro)
        completo = self.resultado["tablas"]["stock_variantes"].set_index("sku")
        self.assertEqual(stock.set_index("sku")["demanda_28d"].to_dict(),
                         completo.loc[stock["sku"], "demanda_28d"].to_dict())

    def test_umbral_configurable(self):
        stock, bajo = self.inventario(umbral=10)
        self.assertEqual(len(bajo), int((stock["stock_disponible"] < 10).sum()))
        _, todos = self.inventario(umbral=1000)
        self.assertEqual(len(todos), len(stock))
        _, ninguno = self.inventario(umbral=0)
        self.assertEqual(len(ninguno), 0)


class PruebasDescargaCsv(unittest.TestCase):

    def test_csv_utf8_con_cabecera_origen_y_filtros(self):
        tabla = sinteticos()["tablas"]["pedidos_unicos"].head(20)
        datos = pipeline.csv_descarga(tabla, "SINTÉTICO (prueba)", "2026-11-09 12:00:00", "tipo: custom")
        texto = datos.decode("utf-8")                                  # es UTF-8 (con tildes)
        cabecera = texto.splitlines()[0].split(",")
        self.assertEqual(cabecera[:3], ["origen", "ejecucion", "filtros"])
        self.assertNotIn("nombre_cliente", cabecera)                   # sin datos personales
        leida = pd.read_csv(io.BytesIO(datos), encoding="utf-8", dtype=str)
        self.assertEqual(len(leida), 20)
        self.assertEqual(set(leida["origen"]), {"SINTÉTICO (prueba)"})
        self.assertEqual(set(leida["filtros"]), {"tipo: custom"})
        self.assertEqual(leida["id_pedido"].tolist(), tabla["id_pedido"].tolist())
        self.assertEqual(leida["importe"].astype(float).tolist(), tabla["importe"].tolist())

    def test_sin_datos_personales(self):
        tabla = pd.DataFrame({"id_cliente": ["1"], "nombre": ["Ana"], "correo": ["a@b.es"], "telefono": ["600"],
                              "importe": [10.0]})
        self.assertEqual(list(pipeline.sin_datos_personales(tabla).columns), ["id_cliente", "importe"])

    def test_estado_de_pagos(self):
        tablas = sinteticos()["tablas"]
        pagos = tablas["pedidos_por_estado_pago"].set_index("estado_pago")
        self.assertEqual(list(pagos.index), config.ESTADOS_PAGO)
        self.assertEqual(pagos["pedidos"].sum(), len(tablas["pedidos_unicos"]))
        pagados = tablas["pedidos_unicos"][tablas["pedidos_unicos"]["estado_pago"] == "pagado"]
        self.assertEqual(pagos.loc["pagado", "importe"], round(float(pagados["importe"].sum()), 2))


if __name__ == "__main__":
    unittest.main()
