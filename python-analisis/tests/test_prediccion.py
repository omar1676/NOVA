"""
Pruebas de la prediccion de demanda (prediccion.py) y de la fase 5 en main.py.

Las series se escriben a mano: 18 meses (2025-05 a 2026-10), como los datos
sinteticos, con la fecha de corte 2026-11-01. Los tres meses de evaluacion son
agosto, septiembre y octubre de 2026.
"""
import contextlib
import io
import unittest
from unittest import mock

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

import main
import prediccion
from analiticas import NO_CALCULABLE
from test_estadistica import tablas_sinteticas
from test_tablas import PruebaTablas

MESES = pd.period_range("2025-05", "2026-10", freq="M")
CORTE = pd.Timestamp("2026-11-01 00:00:00")
EVALUACION = ["2026-08", "2026-09", "2026-10"]


def lineas(series, primer_mes="2025-05"):
    """
    Lineas de demanda como las de lineas_enriquecidas: una por modelo y mes,
    el dia 15, con los pares de la serie (los meses con 0 pares no tienen linea).
    """
    meses = pd.period_range(primer_mes, periods=len(next(iter(series.values()))), freq="M")
    filas = []
    for modelo, valores in series.items():
        for mes, pares in zip(meses, valores):
            if pares > 0:
                filas.append({"nombre_modelo": modelo, "cantidad": int(pares), "es_cancelado": False,
                              "fecha_pedido": mes.to_timestamp() + pd.Timedelta(days=14)})
    return pd.DataFrame(filas)


def series_aleatorias():
    """Cuatro modelos con demandas distintas (siempre las mismas: semilla fija)."""
    rng = np.random.default_rng(7)
    return {"A": rng.integers(20, 80, 18), "B": rng.integers(0, 30, 18),
            "C": rng.integers(50, 150, 18), "D": rng.integers(0, 10, 18)}


def cambiar_meses(series, meses, factor):
    """Copia de las series con los meses indicados multiplicados por factor."""
    posiciones = [list(MESES.astype(str)).index(mes) for mes in meses]
    nuevas = {}
    for modelo, valores in series.items():
        valores = np.array(valores, dtype=int)
        valores[posiciones] = valores[posiciones] * factor + 1
        nuevas[modelo] = valores
    return nuevas


class PruebasDemandaMensual(unittest.TestCase):

    def test_ceros_y_cancelados(self):
        tabla = lineas({"A": [5, 0, 7], "B": [1, 2, 3]})
        cancelada = {"nombre_modelo": "A", "cantidad": 100, "es_cancelado": True,
                     "fecha_pedido": pd.Timestamp("2025-06-10")}
        tabla = pd.concat([tabla, pd.DataFrame([cancelada])], ignore_index=True)
        demanda = prediccion.demanda_mensual(tabla, CORTE)
        modelo_a = demanda[demanda["nombre_modelo"] == "A"]
        self.assertEqual(modelo_a["pares"].tolist(), [5, 0, 7])        # junio: 0 (el cancelado no cuenta)
        self.assertEqual(len(demanda), 6)                              # 2 modelos x 3 meses

    def test_sin_meses_futuros_ni_incompletos(self):
        tabla = lineas({"A": [5, 6, 7]}, primer_mes="2026-09")          # septiembre, octubre y noviembre
        # Corte el 9 de noviembre: noviembre no ha terminado y no entra
        demanda = prediccion.demanda_mensual(tabla, pd.Timestamp("2026-11-09 19:12:54"))
        self.assertEqual(demanda["mes"].astype(str).tolist(), ["2026-09", "2026-10"])
        # Corte el 1 de octubre: octubre y noviembre son posteriores
        demanda = prediccion.demanda_mensual(tabla, pd.Timestamp("2026-10-01 00:00:00"))
        self.assertEqual(demanda["mes"].astype(str).tolist(), ["2026-09"])


class PruebasVariables(unittest.TestCase):

    def setUp(self):
        demanda = prediccion.demanda_mensual(lineas({"A": [10, 20, 30, 40, 50], "B": [1, 2, 3, 4, 5]},
                                                    primer_mes="2026-01"), CORTE)
        self.tabla = prediccion.anadir_variables(demanda)

    def test_solo_meses_anteriores_del_mismo_modelo(self):
        modelo_b = self.tabla[self.tabla["nombre_modelo"] == "B"]
        # El primer mes de B no hereda el ultimo de A
        self.assertTrue(np.isnan(modelo_b["pares_mes_anterior"].iloc[0]))
        self.assertEqual(modelo_b["pares_mes_anterior"].tolist()[1:], [1, 2, 3, 4])
        # Abril (40 pares en A): la media de enero, febrero y marzo, sin abril
        abril = self.tabla[(self.tabla["nombre_modelo"] == "A") & (self.tabla["mes"].astype(str) == "2026-04")]
        self.assertEqual(abril["media_3_meses_previos"].iloc[0], 20.0)
        self.assertEqual(abril["pares_mes_anterior"].iloc[0], 30)

    def test_mes_del_ano_y_modelo_codificados(self):
        enero = self.tabla[self.tabla["mes"].astype(str) == "2026-01"].iloc[0]
        self.assertAlmostEqual(enero["mes_seno"], np.sin(2 * np.pi / 12))
        self.assertAlmostEqual(enero["mes_coseno"], np.cos(2 * np.pi / 12))
        # Dos modelos: una sola columna 0/1 (A es la referencia)
        self.assertEqual([c for c in self.tabla.columns if c.startswith("modelo_")], ["modelo_B"])
        self.assertEqual(sorted(self.tabla["modelo_B"].unique()), [0, 1])


class PruebasSeparacionTemporal(unittest.TestCase):

    def setUp(self):
        self.series = series_aleatorias()
        self.resultado = prediccion.predecir_demanda(lineas(self.series), CORTE)

    def test_periodos_exactos(self):
        demanda = self.resultado["demanda_mensual_modelo"]
        por_conjunto = demanda.groupby("conjunto")["anio_mes"].unique()
        self.assertEqual(sorted(por_conjunto["historial"]), ["2025-05", "2025-06", "2025-07"])
        self.assertEqual(sorted(por_conjunto["entrenamiento"]), [str(m) for m in MESES[3:15]])
        self.assertEqual(sorted(por_conjunto["evaluacion"]), EVALUACION)
        self.assertLess(max(por_conjunto["entrenamiento"]), min(por_conjunto["evaluacion"]))
        metricas = self.resultado["metricas_prediccion"]
        self.assertEqual(metricas["periodo_entrenamiento"].iloc[0], "2025-08 a 2026-07")
        self.assertEqual(metricas["periodo_evaluacion"].iloc[0], "2026-08 a 2026-10")
        self.assertEqual(metricas["filas_entrenamiento"].iloc[0], 12 * 4)   # 12 meses x 4 modelos

    def test_agosto_septiembre_octubre_no_entrenan(self):
        # 1. Se espia que filas recibe fit: ninguna es de los meses de evaluacion
        filas_de_entrenamiento = []
        fit_original = LinearRegression.fit

        def fit_que_anota(modelo, X, y):
            filas_de_entrenamiento.append(X.index)
            return fit_original(modelo, X, y)

        with mock.patch.object(LinearRegression, "fit", fit_que_anota):
            resultado = prediccion.predecir_demanda(lineas(self.series), CORTE)
        self.assertEqual(len(filas_de_entrenamiento), 1)                  # se entrena una sola vez
        meses = resultado["demanda_mensual_modelo"].loc[filas_de_entrenamiento[0], "anio_mes"]
        self.assertEqual(set(meses) & set(EVALUACION), set())
        self.assertEqual(len(meses), 12 * 4)

        # 2. Si agosto, septiembre y octubre fueran otros, el modelo entrenado seria el mismo
        cambiadas = cambiar_meses(self.series, EVALUACION, factor=100)
        otro = prediccion.predecir_demanda(lineas(cambiadas), CORTE)
        pd.testing.assert_frame_equal(otro["coeficientes_regresion"], self.resultado["coeficientes_regresion"])
        # y la prediccion de agosto (que solo usa julio y antes) tampoco cambia
        for resultado in [self.resultado, otro]:
            agosto = resultado["predicciones"][resultado["predicciones"]["anio_mes"] == "2026-08"]
            self.assertEqual(agosto["regresion"].tolist(),
                             self.resultado["predicciones"].query("anio_mes == '2026-08'")["regresion"].tolist())

    def test_el_mes_objetivo_no_es_una_entrada(self):
        # Octubre es el ultimo mes: si cambian sus pares, ninguna prediccion cambia
        cambiadas = cambiar_meses(self.series, ["2026-10"], factor=50)
        otro = prediccion.predecir_demanda(lineas(cambiadas), CORTE)
        columnas = ["nombre_modelo", "anio_mes", "baseline", "regresion"]
        pd.testing.assert_frame_equal(otro["predicciones"][columnas], self.resultado["predicciones"][columnas])
        self.assertFalse(otro["predicciones"]["pares_reales"].equals(self.resultado["predicciones"]["pares_reales"]))

    def test_entradas_de_octubre_solo_del_pasado(self):
        demanda = self.resultado["demanda_mensual_modelo"]
        for modelo, valores in self.series.items():
            octubre = demanda[(demanda["nombre_modelo"] == modelo) & (demanda["anio_mes"] == "2026-10")].iloc[0]
            self.assertEqual(octubre["pares_mes_anterior"], valores[16])                       # septiembre
            self.assertAlmostEqual(octubre["media_3_meses_previos"], round(np.mean(valores[14:17]), 2))


class PruebasMetodos(unittest.TestCase):

    def test_baseline_es_el_mes_anterior(self):
        series = series_aleatorias()
        predicciones = prediccion.predecir_demanda(lineas(series), CORTE)["predicciones"]
        for modelo, valores in series.items():
            del_modelo = predicciones[predicciones["nombre_modelo"] == modelo]
            self.assertEqual(del_modelo["baseline"].tolist(), list(valores[14:17]))   # julio, agosto, septiembre
            self.assertEqual(del_modelo["pares_reales"].tolist(), list(valores[15:18]))

    def test_mae_y_rmse_con_valores_conocidos(self):
        real, prediccion_ = [10, 20, 30], [12, 18, 34]                   # errores 2, 2 y 4
        self.assertAlmostEqual(prediccion.mae(real, prediccion_), 8 / 3)
        self.assertAlmostEqual(prediccion.rmse(real, prediccion_), np.sqrt(24 / 3))
        self.assertAlmostEqual(prediccion.mae(real, prediccion_), mean_absolute_error(real, prediccion_))
        self.assertAlmostEqual(prediccion.rmse(real, prediccion_), np.sqrt(mean_squared_error(real, prediccion_)))
        self.assertEqual(prediccion.mae([5, 5], [5, 5]), 0.0)

    def test_metricas_salen_de_las_predicciones(self):
        resultado = prediccion.predecir_demanda(lineas(series_aleatorias()), CORTE)
        predicciones = resultado["predicciones"]
        metricas = resultado["metricas_prediccion"].set_index("metodo")
        for metodo in ["baseline", "regresion"]:
            self.assertEqual(metricas.loc[metodo, "mae"],
                             round(prediccion.mae(predicciones["pares_reales"], predicciones[metodo]), 2))
            self.assertEqual(metricas.loc[metodo, "rmse"],
                             round(prediccion.rmse(predicciones["pares_reales"], predicciones[metodo]), 2))
        self.assertEqual(metricas.loc["baseline", "filas_evaluacion"], 3 * 4)
        self.assertTrue((predicciones["regresion"] >= 0).all())          # nunca pares negativos

    def test_comparacion_de_metodos(self):
        self.assertTrue(prediccion.mejora(1, 2, 3, 4).startswith("sí"))
        self.assertTrue(prediccion.mejora(5, 6, 3, 4).startswith("no"))
        self.assertTrue(prediccion.mejora(3, 4, 3, 4).startswith("no"))   # empatar no es mejorar
        self.assertEqual(prediccion.mejora(2, 5, 3, 4), "solo en una métrica: MAE sí, RMSE no")

    def test_mejora_cuando_hay_un_patron(self):
        # Demanda que sube 5 pares cada mes: el mes anterior siempre se queda corto
        series = {"A": [10 + 5 * mes for mes in range(18)], "B": [40 + 5 * mes for mes in range(18)]}
        metricas = prediccion.predecir_demanda(lineas(series), CORTE)["metricas_prediccion"].set_index("metodo")
        self.assertEqual(metricas.loc["baseline", "mae"], 5.0)
        self.assertLess(metricas.loc["regresion", "mae"], 0.5)
        self.assertTrue(metricas.loc["regresion", "mejora_al_baseline"].startswith("sí"))

    def test_si_no_mejora_lo_dice(self):
        # Demanda constante: el baseline acierta siempre y la regresion no puede mejorarlo
        series = {"A": [30] * 18, "B": [12] * 18}
        metricas = prediccion.predecir_demanda(lineas(series), CORTE)["metricas_prediccion"].set_index("metodo")
        self.assertEqual(metricas.loc["baseline", "mae"], 0.0)
        self.assertTrue(metricas.loc["regresion", "mejora_al_baseline"].startswith("no"))

    def test_errores_por_modelo(self):
        resultado = prediccion.predecir_demanda(lineas(series_aleatorias()), CORTE)
        tabla = resultado["errores_por_modelo"].set_index("nombre_modelo")
        self.assertEqual(sorted(tabla.index), ["A", "B", "C", "D"])
        predicciones = resultado["predicciones"]
        del_a = predicciones[predicciones["nombre_modelo"] == "A"]
        self.assertEqual(tabla.loc["A", "mae_baseline"], round(prediccion.mae(del_a["pares_reales"], del_a["baseline"]), 2))
        self.assertEqual(tabla.loc["A", "pares_reales_evaluacion"], del_a["pares_reales"].sum())


class PruebasDatosInsuficientes(unittest.TestCase):

    def test_once_meses_no_calculable(self):
        resultado = prediccion.predecir_demanda(lineas({"A": list(range(1, 12))}, primer_mes="2025-12"), CORTE)
        for nombre in ["predicciones", "metricas_prediccion", "errores_por_modelo", "coeficientes_regresion"]:
            self.assertEqual(resultado[nombre]["estado"].iloc[0], NO_CALCULABLE, nombre)
        self.assertIn("11 meses", resultado["predicciones"]["motivo"].iloc[0])
        self.assertEqual(len(resultado["demanda_mensual_modelo"]), 11)   # la demanda si se describe

    def test_sin_ningun_mes_completo(self):
        # Como la exportacion de PRUEBA de entrada_acc: pedidos solo del mes de la fecha de corte
        tabla = lineas({"A": [3]}, primer_mes="2026-11")
        resultado = prediccion.predecir_demanda(tabla, pd.Timestamp("2026-11-09 19:12:54"))
        self.assertEqual(resultado["demanda_mensual_modelo"]["estado"].iloc[0], NO_CALCULABLE)
        self.assertEqual(resultado["predicciones"]["estado"].iloc[0], NO_CALCULABLE)

    def test_con_los_sinteticos_si_se_calcula(self):
        tablas = tablas_sinteticas()
        resultado = prediccion.predecir_demanda(tablas["lineas_enriquecidas"], CORTE)
        self.assertEqual(len(resultado["demanda_mensual_modelo"]), 12 * 18)   # 12 modelos x 18 meses
        self.assertEqual(len(resultado["predicciones"]), 12 * 3)
        self.assertEqual(sorted(resultado["predicciones"]["anio_mes"].unique()), EVALUACION)
        demanda = resultado["demanda_mensual_modelo"]
        evaluacion = demanda[demanda["anio_mes"].isin(EVALUACION)]
        self.assertEqual(set(evaluacion["conjunto"]), {"evaluacion"})
        # Los pares de la demanda mensual son los de la matriz modelo x mes de la fase 3
        self.assertEqual(demanda["pares"].sum(), tablas["matriz_modelo_mes"].drop(columns="nombre_modelo").to_numpy().sum())


class PruebasFase5EnMain(PruebaTablas):

    def ejecutar(self):
        salida = self.carpeta / "salida"
        with contextlib.redirect_stdout(io.StringIO()):
            codigo = main.ejecutar(self.carpeta, salida)
        return codigo, salida

    def leer(self, salida, archivo):
        return pd.read_csv(salida / archivo, encoding="utf-8", dtype=str, keep_default_na=False)

    def test_pocos_datos_no_calculable(self):
        codigo, salida = self.ejecutar()
        self.assertEqual(codigo, 0)
        self.assertEqual(len(self.leer(salida, "rfm_clientes.csv")), 2)          # una fila por cliente
        for archivo in ["kmeans_seleccion_k.csv", "kmeans_clusters.csv", "predicciones.csv",
                        "metricas_prediccion.csv"]:
            with self.subTest(archivo=archivo):
                self.assertEqual(self.leer(salida, archivo)["estado"].iloc[0], NO_CALCULABLE)
        self.assertTrue((salida / "graficos_prediccion" / "11_real_frente_a_prediccion.png").exists())

    def test_datos_bloqueados_no_publican_la_fase_5(self):
        self.anadir("lineas_pedido.csv", "103,99,M1-40,1,40,1,79.99,79.99\n")   # linea huerfana: bloqueante
        codigo, salida = self.ejecutar()
        self.assertEqual(codigo, 1)
        self.assertEqual(self.leer(salida, "estado_ejecucion.csv")["estado"].iloc[0], "BLOQUEADO")
        for archivo in ["rfm_clientes.csv", "rfm_segmentos.csv", "kmeans_clusters.csv", "predicciones.csv",
                        "metricas_prediccion.csv", "demanda_mensual_modelo.csv"]:
            self.assertFalse((salida / archivo).exists(), archivo)
        self.assertFalse((salida / "graficos_prediccion").exists())


if __name__ == "__main__":
    unittest.main()
