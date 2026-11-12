"""
Pruebas de los graficos (visualizaciones.py) y de la ejecucion completa (main.ejecutar).

Los graficos se guardan en una carpeta temporal. Se comprueba que salen los
10 PNG, que son imagenes validas, que no fallan sin datos y que, si los datos
estan bloqueados por calidad, no se publica ninguna cifra ni ningun grafico.
"""
import contextlib
import io

import pandas as pd

import config
import main
import visualizaciones
from test_analiticas import SQL_CORRECTOS
from test_tablas import PruebaTablas

FIRMA_PNG = b"\x89PNG\r\n\x1a\n"


class PruebasGraficos(PruebaTablas):

    def generar(self):
        salida = self.carpeta / "graficos"
        return visualizaciones.generar_todos(self.tablas(), salida, "pie de prueba"), salida

    def test_salen_los_diez_png(self):
        rutas, salida = self.generar()
        self.assertEqual(len(rutas), 10)
        self.assertEqual(sorted(ruta.name for ruta in rutas), sorted(g[0] for g in visualizaciones.GRAFICOS))
        for ruta in rutas:
            with self.subTest(grafico=ruta.name):
                self.assertTrue(ruta.read_bytes().startswith(FIRMA_PNG))
                self.assertGreater(ruta.stat().st_size, 10000)

    def test_cada_grafico_es_de_un_tipo_distinto_o_responde_otra_pregunta(self):
        preguntas = [g[2] for g in visualizaciones.GRAFICOS]
        self.assertEqual(len(set(preguntas)), len(preguntas))
        tipos = {g[1] for g in visualizaciones.GRAFICOS}
        for tipo in ["serie temporal", "Pareto", "histograma", "diagrama de caja", "mapa de calor",
                     "dispersión", "comparativa por segmento"]:
            self.assertIn(tipo, tipos)

    def test_sin_datos_no_falla(self):
        self.vaciar_lineas()
        rutas, _ = self.generar()
        self.assertEqual(len(rutas), 10)
        for ruta in rutas:
            self.assertTrue(ruta.read_bytes().startswith(FIRMA_PNG))


class PruebasEjecucionCompleta(PruebaTablas):

    def ejecutar(self):
        salida = self.carpeta / "salida"
        with contextlib.redirect_stdout(io.StringIO()):
            codigo = main.ejecutar(self.carpeta, salida)
        return codigo, salida

    def escribir_sql(self, cambios=None):
        carpeta_sql = self.carpeta / config.CARPETA_SQL
        carpeta_sql.mkdir(exist_ok=True)
        for archivo, texto in {**SQL_CORRECTOS, **(cambios or {})}.items():
            (carpeta_sql / archivo).write_text(texto, encoding="utf-8")

    def leer(self, salida, archivo):
        return pd.read_csv(salida / archivo, encoding="utf-8", dtype=str, keep_default_na=False)

    def test_ejecucion_correcta(self):
        self.escribir_sql()
        codigo, salida = self.ejecutar()
        self.assertEqual(codigo, 0)
        self.assertEqual(self.leer(salida, "estado_ejecucion.csv")["estado"].iloc[0], "CORRECTO")
        self.assertEqual(len(self.leer(salida, "kpis.csv")), 20)
        self.assertEqual(set(self.leer(salida, "coherencia_kpis_sql.csv")["resultado"]), {"coincide"})
        self.assertEqual(len(list((salida / "graficos").glob("*.png"))), 10)
        for archivo in ["pedidos_unicos.csv", "modelos_abc.csv", "matriz_modelo_talla.csv", "stock_variantes.csv",
                        "cohortes.csv", "ventas_por_periodo.csv", "precio_y_margen.csv", "nulos_por_columna.csv"]:
            self.assertTrue((salida / archivo).exists(), archivo)
        self.assertNotIn("nombre_cliente", self.leer(salida, "pedidos_unicos.csv").columns)
        self.assertEqual(self.leer(salida, "kpis.csv")["origen"].iloc[0], "DESCONOCIDO (no hay línea 'Tipo:' en ORIGEN.txt)")

    def test_datos_bloqueados_no_publican_nada(self):
        self.anadir("lineas_pedido.csv", "103,99,M1-40,1,40,1,79.99,79.99\n")   # linea huerfana
        codigo, salida = self.ejecutar()
        self.assertEqual(codigo, 1)
        self.assertEqual(self.leer(salida, "estado_ejecucion.csv")["estado"].iloc[0], "BLOQUEADO")
        self.assertTrue((salida / "incidencias.csv").exists())   # las incidencias si se guardan
        self.assertFalse((salida / "kpis.csv").exists())
        self.assertFalse((salida / "modelos_abc.csv").exists())
        self.assertFalse((salida / "graficos").exists())

    def test_metadatos_de_cada_dataframe(self):
        self.escribir_sql()
        _, salida = self.ejecutar()
        tabla = self.leer(salida, "metadatos_dataframes.csv").set_index("archivo")
        # Una fila por cada CSV de la carpeta (menos el propio archivo de metadatos)
        archivos = sorted(ruta.name for ruta in salida.glob("*.csv") if ruta.name != "metadatos_dataframes.csv")
        self.assertEqual(sorted(tabla.index), archivos)
        for columna in ["fecha_corte", "reglas_de_negocio", "filtros", "filas_origen", "funcion"]:
            self.assertTrue((tabla[columna].str.len() > 0).all(), columna)
        self.assertEqual(set(tabla["fecha_corte"]), {"2026-11-09 19:00:00"})   # la de stock.csv
        self.assertEqual(set(tabla["filtros"]), {"ninguno"})
        pedidos = tabla.loc["pedidos_unicos.csv"]
        self.assertEqual(pedidos["funcion"], "analiticas.df_pedidos_unicos")
        self.assertEqual(pedidos["filas_origen"], "clientes: 2 válidas; pedidos: 2 válidas; lineas_pedido: 3 válidas")
        self.assertEqual(pedidos["filas_resultado"], "2")
        self.assertIn("leídas", tabla.loc["incidencias.csv", "filas_origen"])
        # Se enlaza con cada CSV por su ejecucion
        self.assertEqual(set(tabla["ejecucion"]), set(self.leer(salida, "kpis.csv")["ejecucion"]))

    def test_metadatos_tambien_con_datos_bloqueados(self):
        self.anadir("lineas_pedido.csv", "103,99,M1-40,1,40,1,79.99,79.99\n")   # linea huerfana
        _, salida = self.ejecutar()
        tabla = self.leer(salida, "metadatos_dataframes.csv")
        self.assertEqual(sorted(tabla["archivo"]), ["estado_ejecucion.csv", "filas_rechazadas.csv", "incidencias.csv",
                                                    "resumen_calidad.csv"])
        self.assertTrue(tabla["filas_origen"].str.contains("lineas_pedido: 4 leídas").all())

    def test_si_no_cuadra_con_sql_lo_dice(self):
        self.escribir_sql({"P-A.csv": "pedidos,pares_solicitados,importe_ventas\n1,3,240.00\n"})
        codigo, salida = self.ejecutar()
        self.assertEqual(codigo, 1)
        self.assertEqual(self.leer(salida, "estado_ejecucion.csv")["estado"].iloc[0], "NO CUADRA CON SQL")
