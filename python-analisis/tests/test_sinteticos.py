"""
Pruebas del generador de datos sinteticos (generador_datos.py) y de su
separacion de los datos de Acceso a Datos.

Todo se genera en memoria o en carpetas temporales: nunca se toca entrada_acc/
ni datos_sinteticos/.
"""
import contextlib
import hashlib
import io
import tempfile
import unittest
from pathlib import Path

import pandas as pd

import calidad
import config
import generador_datos
import main
import pipeline

REGLAS_02_A_12 = [f"{numero:02d}" for numero in range(2, 13)]


class PruebasGenerador(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.datos = generador_datos.generar(config.SEMILLA)

    def test_misma_semilla_mismos_datos(self):
        otra_vez = generador_datos.generar(config.SEMILLA)
        for nombre, tabla in self.datos.items():
            pd.testing.assert_frame_equal(tabla, otra_vez[nombre])

    def test_otra_semilla_otros_datos(self):
        otra = generador_datos.generar(config.SEMILLA + 1)
        self.assertFalse(self.datos["pedidos"].equals(otra["pedidos"]))

    def test_minimos_de_la_rubrica(self):
        self.assertEqual(len(self.datos["clientes"]), 40)
        self.assertEqual(len(self.datos["modelos"]), 12)
        self.assertGreaterEqual(len(self.datos["pedidos"]), 800)
        self.assertGreaterEqual(len(self.datos["lineas_pedido"]), 1600)

    def test_dieciocho_meses_seguidos(self):
        fechas = pd.to_datetime(self.datos["pedidos"]["fecha_pedido"])
        meses = sorted(fechas.dt.to_period("M").unique())
        self.assertEqual(meses, list(pd.period_range("2025-05", "2026-10", freq="M")))
        self.assertTrue((fechas < pd.Timestamp(generador_datos.FECHA_CORTE)).all())

    def test_columnas_del_contrato(self):
        for nombre, tabla in self.datos.items():
            self.assertEqual(list(tabla.columns), list(config.ARCHIVOS[nombre]["tipos"]))

    def test_pedidos_y_lineas_cuadran(self):
        lineas = self.datos["lineas_pedido"]
        pedidos = self.datos["pedidos"].set_index("id_pedido")
        calculado = (lineas["cantidad"] * lineas["precio_unitario"]).round(2)
        self.assertTrue(((calculado - lineas["importe_linea"]).abs() < 0.005).all())
        suma = lineas.groupby("id_pedido").agg(pares=("cantidad", "sum"), importe=("importe_linea", "sum"))
        self.assertEqual(len(suma), len(pedidos))                 # todos los pedidos tienen lineas
        self.assertTrue((suma["pares"] == pedidos["cantidad_total"]).all())
        self.assertTrue(((suma["importe"] - pedidos["importe_total"]).abs() < 0.005).all())

    def test_sin_claves_huerfanas(self):
        datos = self.datos
        self.assertTrue(datos["pedidos"]["id_cliente"].isin(datos["clientes"]["id_cliente"]).all())
        self.assertTrue(datos["lineas_pedido"]["id_pedido"].isin(datos["pedidos"]["id_pedido"]).all())
        self.assertTrue(datos["lineas_pedido"]["id_modelo"].isin(datos["modelos"]["id_modelo"]).all())
        self.assertTrue(datos["lineas_pedido"]["sku"].isin(datos["stock"]["sku"]).all())
        self.assertTrue(datos["stock"]["id_modelo"].isin(datos["modelos"]["id_modelo"]).all())

    def test_reglas_de_negocio(self):
        pedidos = self.datos["pedidos"]
        reembolsados = pedidos[pedidos["estado_pago"] == "reembolsado"]
        self.assertTrue((reembolsados["estado_pedido"] == "cancelado").all())
        custom = pedidos["tipo_pedido"] == "custom"
        self.assertTrue((pedidos.loc[custom, "personalizacion"] != "").all())
        self.assertTrue((pedidos.loc[~custom, "personalizacion"] == "").all())
        self.assertTrue((self.datos["lineas_pedido"]["cantidad"] > 0).all())

    def test_variedad_que_no_es_uniforme(self):
        pedidos = self.datos["pedidos"]
        lineas = self.datos["lineas_pedido"]
        self.assertGreaterEqual(pedidos["estado_pedido"].nunique(), 5)
        self.assertTrue(0.10 < (pedidos["tipo_pedido"] == "custom").mean() < 0.20)
        por_modelo = lineas.groupby("id_modelo")["cantidad"].sum()
        self.assertGreater(por_modelo[1], por_modelo[12])          # el modelo 1 es el mas popular
        por_talla = lineas.groupby("talla")["cantidad"].sum()
        self.assertGreater(por_talla[42], por_talla[38])           # las tallas centrales se piden mas
        por_mes = pd.to_datetime(pedidos["fecha_pedido"]).dt.to_period("M").value_counts()
        self.assertGreater(por_mes.max(), 1.5 * por_mes.min())     # hay estacionalidad


class PruebasDatosGuardados(unittest.TestCase):
    """Los datos limpios y la copia con errores, guardados y pasados por las 12 reglas."""

    @classmethod
    def setUpClass(cls):
        cls.temporal = tempfile.TemporaryDirectory()
        base = Path(cls.temporal.name)
        datos = generador_datos.generar(config.SEMILLA)
        cls.limpios = generador_datos.guardar(datos, base / "limpios", "datos de prueba del test")
        con_errores, cls.errores = generador_datos.introducir_errores(datos)
        cls.con_errores = generador_datos.guardar(con_errores, base / "con_errores", "copia con errores del test")
        cls.resultado_limpios = calidad.evaluar(cls.limpios)
        cls.resultado_errores = calidad.evaluar(cls.con_errores)

    @classmethod
    def tearDownClass(cls):
        cls.temporal.cleanup()

    def test_limpios_sin_ninguna_incidencia(self):
        self.assertEqual(len(self.resultado_limpios["incidencias"]), 0)
        self.assertFalse(self.resultado_limpios["bloqueado"])
        self.assertEqual(self.resultado_limpios["resumen"]["porcentaje_calidad"].tolist(), [100.0] * 5)

    def test_con_errores_se_detecta_cada_regla(self):
        detectadas = set(self.resultado_errores["incidencias"]["regla"])
        for regla in REGLAS_02_A_12:
            with self.subTest(regla=regla):
                self.assertIn(regla, detectadas)
        self.assertTrue(self.resultado_errores["bloqueado"])

    def test_cada_error_esta_documentado(self):
        self.assertEqual(sorted(set(self.errores["regla"])), REGLAS_02_A_12)
        self.assertTrue(self.errores["se_espera"].str.len().gt(0).all())

    def test_origen_sintetico(self):
        self.assertEqual(pipeline.tipo_origen(self.limpios), "SINTETICO")
        self.assertIn("SINTÉTICO", pipeline.etiqueta_origen(self.con_errores))

    def test_mismo_formato_que_acceso_a_datos(self):
        texto = (self.limpios / "pedidos.csv").read_bytes()
        self.assertFalse(texto.startswith(b"\xef\xbb\xbf"))          # UTF-8 sin BOM
        self.assertNotIn(b"\r\n", texto)                             # saltos de linea como el exportador
        primera = pd.read_csv(self.limpios / "pedidos.csv", dtype=str).iloc[0]
        self.assertRegex(primera["importe_total"], r"^\d+\.\d{2}$")   # punto decimal y 2 decimales
        self.assertRegex(primera["fecha_pedido"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")


class PruebasSeparacion(unittest.TestCase):

    def test_nunca_se_guarda_en_entrada_acc(self):
        huella = {ruta.name: hashlib.sha256(ruta.read_bytes()).hexdigest()
                  for ruta in config.CARPETA_ENTRADA.glob("*.*")}
        datos = generador_datos.generar(config.SEMILLA)
        for carpeta in [config.CARPETA_ENTRADA, config.CARPETA_ENTRADA / "sinteticos"]:
            with self.subTest(carpeta=carpeta):
                with self.assertRaises(ValueError):
                    generador_datos.guardar(datos, carpeta, "no debe guardarse")
        self.assertFalse((config.CARPETA_ENTRADA / "sinteticos").exists())
        despues = {ruta.name: hashlib.sha256(ruta.read_bytes()).hexdigest()
                   for ruta in config.CARPETA_ENTRADA.glob("*.*")}
        self.assertEqual(huella, despues)

    def test_cada_modo_tiene_sus_carpetas(self):
        entradas = [Path(entrada).resolve() for entrada, _ in main.MODOS.values()]
        salidas = [Path(salida).resolve() for _, salida in main.MODOS.values()]
        self.assertEqual(len(set(entradas)), 3)
        self.assertEqual(len(set(salidas)), 3)
        real = config.CARPETA_ENTRADA.resolve()
        for entrada in entradas[1:]:
            self.assertNotIn(real, entrada.parents)                 # lo sintetico no esta dentro de entrada_acc

    def test_identificadores_que_no_se_confunden(self):
        sinteticos = generador_datos.generar(config.SEMILLA)
        self.assertTrue(sinteticos["pedidos"]["referencia"].str.startswith("SINT-").all())
        self.assertTrue(sinteticos["modelos"]["nombre_modelo"].str.startswith("SINT ").all())
        de_prueba = pd.read_csv(config.CARPETA_ENTRADA / "pedidos.csv", dtype=str)
        self.assertFalse(de_prueba["referencia"].str.startswith("SINT").any())


class PruebasCompatibilidad(unittest.TestCase):
    """La misma ejecucion que con los datos de PRUEBA, sobre los sinteticos."""

    @classmethod
    def setUpClass(cls):
        cls.temporal = tempfile.TemporaryDirectory()
        base = Path(cls.temporal.name)
        entrada = generador_datos.guardar(generador_datos.generar(config.SEMILLA), base / "limpios", "test")
        cls.salida = base / "salida"
        with contextlib.redirect_stdout(io.StringIO()) as consola:
            cls.codigo = main.ejecutar(entrada, cls.salida)
        cls.consola = consola.getvalue()

    @classmethod
    def tearDownClass(cls):
        cls.temporal.cleanup()

    def leer(self, archivo):
        return pd.read_csv(self.salida / archivo, encoding="utf-8", dtype=str, keep_default_na=False)

    def test_ejecucion_correcta(self):
        self.assertEqual(self.codigo, 0)
        self.assertEqual(self.leer("estado_ejecucion.csv")["estado"].iloc[0], "CORRECTO")
        self.assertIn("NO APLICA", self.consola)                    # no hay SQL con que conciliar

    def test_todo_etiquetado_como_sintetico(self):
        for archivo in ["kpis.csv", "pedidos_unicos.csv", "hipotesis.csv", "incidencias.csv"]:
            with self.subTest(archivo=archivo):
                self.assertTrue(self.leer(archivo)["origen"].str.startswith("SINTÉTICO").all())

    def test_tablas_kpis_y_graficos(self):
        self.assertEqual(len(self.leer("pedidos_unicos.csv")), 900)   # el cruce no multiplica pedidos
        kpis = self.leer("kpis.csv").set_index("codigo")
        self.assertEqual(kpis.loc["K19", "estado"], "calculado")     # ya hay varios meses
        self.assertEqual(kpis.loc["K20", "estado"], "calculado")
        self.assertNotIn("estado", self.leer("cohortes.csv").columns)  # cohortes calculables
        self.assertEqual(len(self.leer("ventas_por_periodo.csv")), 18)
        self.assertEqual(len(list((self.salida / "graficos").glob("*.png"))), 10)
        self.assertEqual(len(self.leer("hipotesis.csv")), 3)

    def test_fase_5_publicada_y_etiquetada(self):
        # Con 40 clientes y 18 meses, la segmentacion y la prediccion se calculan
        for archivo in ["rfm_clientes.csv", "rfm_segmentos.csv", "kmeans_seleccion_k.csv", "kmeans_clusters.csv",
                        "rfm_frente_a_kmeans.csv", "demanda_mensual_modelo.csv", "predicciones.csv",
                        "metricas_prediccion.csv", "errores_por_modelo.csv", "coeficientes_regresion.csv"]:
            with self.subTest(archivo=archivo):
                tabla = self.leer(archivo)
                self.assertNotIn("estado", tabla.columns)              # no es NO CALCULABLE
                self.assertTrue(tabla["origen"].str.startswith("SINTÉTICO").all())
        self.assertEqual(len(self.leer("rfm_clientes.csv")), 40)
        self.assertEqual(self.leer("metricas_prediccion.csv")["periodo_evaluacion"].iloc[0], "2026-08 a 2026-10")
        self.assertEqual(len(list((self.salida / "graficos_prediccion").glob("*.png"))), 1)
