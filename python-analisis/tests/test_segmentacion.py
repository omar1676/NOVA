"""
Pruebas de la segmentacion de clientes: RFM y KMeans (segmentacion.py).

Las pruebas de RFM usan pedidos escritos a mano, con resultados que se pueden
calcular de cabeza. Las de KMeans usan los datos sinteticos (40 clientes):
con los 6 clientes de la exportacion de PRUEBA (entrada_acc) no se puede agrupar.
"""
import unittest

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import config
import generador_datos
import segmentacion
from analiticas import NO_CALCULABLE
from test_estadistica import tablas_sinteticas

CORTE = pd.Timestamp("2026-11-01 00:00:00")


def pedidos(filas):
    """Pedidos como los de pedidos_unicos: (id_pedido, id_cliente, fecha, estado, importe)."""
    tabla = pd.DataFrame(filas, columns=["id_pedido", "id_cliente", "fecha_pedido", "estado_pedido", "importe"])
    tabla["fecha_pedido"] = pd.to_datetime(tabla["fecha_pedido"])
    tabla["es_confirmado"] = tabla["estado_pedido"].isin(config.ESTADOS_CONFIRMADOS)
    return tabla


def clientes(cuantos):
    return pd.DataFrame({"id_cliente": [str(numero) for numero in range(1, cuantos + 1)],
                         "tipo": ["particular"] * cuantos})


def compradores(cuantos):
    """
    El cliente i hace i pedidos entregados de 100*i euros; el ultimo, 5*i dias
    antes del corte. Asi: frequency = i, monetary = 100*i*i y recency = 5*i.
    """
    filas = []
    for cliente in range(1, cuantos + 1):
        for vez in range(cliente):
            fecha = CORTE - pd.Timedelta(days=5 * cliente + 30 * vez)
            filas.append((f"{cliente}-{vez}", str(cliente), fecha, "entregado", 100.0 * cliente))
    return pedidos(filas)


def rfm_sintetico():
    """RFM de los 40 clientes sinteticos (las tablas se calculan una sola vez)."""
    tablas = tablas_sinteticas()
    lista = tablas["clientes_actividad"][["id_cliente", "tipo_cliente"]].rename(columns={"tipo_cliente": "tipo"})
    return segmentacion.rfm(tablas["pedidos_unicos"], lista, pd.Timestamp(generador_datos.FECHA_CORTE))


class PruebasRecencyFrequencyMonetary(unittest.TestCase):

    def test_recency_desde_la_fecha_de_corte(self):
        tabla = pedidos([
            ("1", "1", "2026-09-01 10:00:00", "entregado", 100.0),
            ("2", "1", "2026-10-22 00:00:00", "confirmado", 50.0),     # ultima compra valida: 10 dias antes
            ("3", "1", "2026-10-30 00:00:00", "cancelado", 999.0),     # cancelado: no es una compra
            ("4", "1", "2026-10-31 00:00:00", "pendiente", 999.0),     # pendiente: todavia no es venta
        ])
        fila = segmentacion.rfm(tabla, clientes(1), CORTE).iloc[0]
        self.assertEqual(fila["recency_dias"], 10)
        self.assertEqual(fila["ultima_compra"], pd.Timestamp("2026-10-22"))

    def test_pedidos_posteriores_al_corte_no_cuentan(self):
        tabla = pedidos([
            ("1", "1", "2026-10-01 00:00:00", "entregado", 100.0),
            ("2", "1", "2026-11-05 00:00:00", "entregado", 500.0),     # despues del corte
        ])
        fila = segmentacion.rfm(tabla, clientes(1), CORTE).iloc[0]
        self.assertEqual((fila["frequency"], fila["monetary"], fila["recency_dias"]), (1, 100.0, 31))

    def test_frequency_cuenta_pedidos_y_monetary_suma_importes(self):
        tabla = pedidos([
            ("1", "1", "2026-08-01 00:00:00", "entregado", 100.0),
            ("2", "1", "2026-09-01 00:00:00", "enviado", 200.0),
            ("3", "1", "2026-10-01 00:00:00", "en_preparacion", 50.5),
            ("4", "1", "2026-10-02 00:00:00", "cancelado", 1000.0),
            ("5", "2", "2026-10-03 00:00:00", "confirmado", 80.0),
        ])
        tabla_rfm = segmentacion.rfm(tabla, clientes(2), CORTE).set_index("id_cliente")
        self.assertEqual(tabla_rfm.loc["1", "frequency"], 3)          # el cancelado no cuenta
        self.assertEqual(tabla_rfm.loc["1", "monetary"], 350.5)
        self.assertEqual(tabla_rfm.loc["2", "frequency"], 1)

    def test_clientes_sin_compras_validas(self):
        tabla = pedidos([("1", "2", "2026-10-01 00:00:00", "cancelado", 100.0)])   # el 2 solo cancelo
        tabla_rfm = segmentacion.rfm(tabla, clientes(3), CORTE)
        self.assertEqual(len(tabla_rfm), 3)                           # una fila por cliente, tambien sin compras
        self.assertEqual(tabla_rfm["frequency"].tolist(), [0, 0, 0])
        self.assertEqual(tabla_rfm["monetary"].tolist(), [0.0, 0.0, 0.0])
        self.assertTrue(tabla_rfm["recency_dias"].isna().all())       # no se inventa una ultima compra
        self.assertEqual(set(tabla_rfm["segmento"]), {segmentacion.SIN_COMPRAS})


class PruebasSegmentos(unittest.TestCase):

    def test_puntuaciones_por_quintiles(self):
        tabla_rfm = segmentacion.rfm(compradores(15), clientes(15), CORTE).set_index("id_cliente")
        # 15 clientes: 3 en cada puntuacion de 1 a 5
        for columna in ["r_score", "f_score", "m_score"]:
            self.assertEqual(tabla_rfm[columna].value_counts().sort_index().tolist(), [3, 3, 3, 3, 3])
        # El cliente 1 compro hace menos (R = 5) pero poco (F = 1); el 15, al reves
        self.assertEqual(tabla_rfm.loc["1", ["r_score", "f_score", "m_score"]].tolist(), [5, 1, 1])
        self.assertEqual(tabla_rfm.loc["15", ["r_score", "f_score", "m_score"]].tolist(), [1, 5, 5])

    def test_reglas_de_los_segmentos(self):
        casos = [
            ((5, 5, 5, 10), "Mejores clientes"),
            ((4, 4, 4, 10), "Mejores clientes"),
            ((2, 4, 5, 10), "En riesgo"),           # compraba mucho y lleva tiempo sin comprar
            ((3, 3, 1, 10), "Habituales"),
            ((5, 5, 3, 10), "Habituales"),           # M de 3: no llega a mejor cliente
            ((1, 2, 5, 10), "Inactivos"),
            ((5, 1, 1, 10), "Ocasionales"),
            ((None, None, None, 0), segmentacion.SIN_COMPRAS),
        ]
        for (r, f, m, frequency), esperado in casos:
            with self.subTest(r=r, f=f, m=m):
                fila = {"r_score": r, "f_score": f, "m_score": m, "frequency": frequency}
                self.assertEqual(segmentacion.segmento(fila), esperado)

    def test_al_menos_cuatro_segmentos_con_significado(self):
        con_compras = [nombre for nombre in segmentacion.SEGMENTOS if nombre != segmentacion.SIN_COMPRAS]
        self.assertGreaterEqual(len(con_compras), 4)
        self.assertIn(segmentacion.SIN_COMPRAS, segmentacion.SEGMENTOS)
        for nombre, significado in segmentacion.SEGMENTOS.items():
            self.assertGreater(len(significado), 20, nombre)

    def test_resumen_cuenta_a_todos_los_clientes(self):
        tabla_rfm = segmentacion.rfm(compradores(15), clientes(18), CORTE)   # 3 sin compras
        resumen = segmentacion.resumen_segmentos(tabla_rfm).set_index("segmento")
        self.assertEqual(resumen["clientes"].sum(), 18)
        self.assertEqual(resumen.loc[segmentacion.SIN_COMPRAS, "clientes"], 3)
        self.assertEqual(resumen["monetary_total"].sum(), round(tabla_rfm["monetary"].sum(), 2))
        self.assertAlmostEqual(resumen["porcentaje_importe"].sum(), 100.0, delta=0.2)

    def test_reproducible_aunque_cambie_el_orden(self):
        tablas = tablas_sinteticas()
        lista = tablas["clientes_actividad"][["id_cliente", "tipo_cliente"]].rename(columns={"tipo_cliente": "tipo"})
        corte = pd.Timestamp(generador_datos.FECHA_CORTE)
        primera = segmentacion.rfm(tablas["pedidos_unicos"], lista, corte)
        desordenados = tablas["pedidos_unicos"].sample(frac=1, random_state=1)
        segunda = segmentacion.rfm(desordenados, lista.sample(frac=1, random_state=2), corte)
        pd.testing.assert_frame_equal(primera, segunda)

    def test_pocos_clientes_no_calculable(self):
        # Como la exportacion de PRUEBA de entrada_acc: 6 clientes y solo el 6 con una compra
        tabla = pedidos([("1", "6", "2026-10-30 00:00:00", "confirmado", 4796.0)])
        tabla_rfm = segmentacion.rfm(tabla, clientes(6), CORTE).set_index("id_cliente")
        self.assertTrue(tabla_rfm.loc["6", "segmento"].startswith(NO_CALCULABLE))
        self.assertTrue(tabla_rfm["r_score"].isna().all())            # no se reparten quintiles
        self.assertEqual((tabla_rfm["segmento"] == segmentacion.SIN_COMPRAS).sum(), 5)


class PruebasKMeans(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.rfm = rfm_sintetico()
        cls.seleccion, cls.clusters, cls.con_cluster = segmentacion.kmeans_clientes(cls.rfm)

    def test_variables_estandarizadas_y_sin_nulos(self):
        datos = segmentacion.variables_kmeans(self.rfm[self.rfm["frequency"] > 0])
        self.assertEqual(datos.shape[1], 3)
        np.testing.assert_allclose(datos.mean(axis=0), 0, atol=1e-9)    # media 0
        np.testing.assert_allclose(datos.std(axis=0), 1, atol=1e-9)     # desviacion 1
        con_nulo = self.rfm[self.rfm["frequency"] > 0].copy()
        con_nulo.loc[con_nulo.index[0], "recency_dias"] = np.nan
        with self.assertRaises(ValueError):
            segmentacion.variables_kmeans(con_nulo)

    def test_prueba_k_de_2_a_5_con_silhouette(self):
        self.assertEqual(self.seleccion["k"].tolist(), [2, 3, 4, 5])
        self.assertTrue(self.seleccion["silhouette"].between(-1, 1).all())

    def test_silhouette_calculado_con_sklearn(self):
        datos = segmentacion.variables_kmeans(self.rfm[self.rfm["frequency"] > 0])
        for _, fila in self.seleccion.iterrows():
            modelo = KMeans(n_clusters=int(fila["k"]), random_state=config.SEMILLA, n_init=10).fit(datos)
            self.assertEqual(fila["silhouette"], round(float(silhouette_score(datos, modelo.labels_)), 3))

    def test_se_elige_el_k_con_mayor_silhouette(self):
        self.assertEqual(self.seleccion["elegido"].sum(), 1)
        elegido = self.seleccion[self.seleccion["elegido"]].iloc[0]
        self.assertEqual(elegido["silhouette"], self.seleccion["silhouette"].max())
        self.assertEqual(len(self.clusters), elegido["k"])

    def test_reproducible(self):
        seleccion, clusters, con_cluster = segmentacion.kmeans_clientes(self.rfm)
        pd.testing.assert_frame_equal(seleccion, self.seleccion)
        pd.testing.assert_frame_equal(clusters, self.clusters)
        pd.testing.assert_series_equal(con_cluster["cluster"], self.con_cluster["cluster"])

    def test_clusters_describen_a_todos_los_compradores(self):
        compradores_sinteticos = (self.rfm["frequency"] > 0).sum()
        self.assertEqual(self.clusters["clientes"].sum(), compradores_sinteticos)
        self.assertEqual(self.con_cluster["cluster"].notna().sum(), compradores_sinteticos)
        # Numerados de mas a menos importe medio, cada uno con nombre
        self.assertEqual(self.clusters["cluster"].tolist(), list(range(1, len(self.clusters) + 1)))
        self.assertTrue(self.clusters["monetary_medio"].is_monotonic_decreasing)
        self.assertTrue((self.clusters["nombre"].str.len() > 10).all())
        self.assertAlmostEqual(self.clusters["porcentaje_clientes"].sum(), 100.0, delta=0.2)

    def test_comparacion_con_rfm(self):
        comparacion = segmentacion.comparar_rfm_kmeans(self.con_cluster)
        columnas = [f"cluster_{numero}" for numero in self.clusters["cluster"]]
        self.assertEqual(list(comparacion.columns), ["segmento"] + columnas + ["total"])
        self.assertEqual(comparacion["total"].sum(), self.clusters["clientes"].sum())
        segmentos = self.rfm[self.rfm["frequency"] > 0]["segmento"].value_counts()
        self.assertEqual(comparacion.set_index("segmento")["total"].to_dict(), segmentos.to_dict())

    def test_no_se_fuerza_con_pocos_clientes(self):
        # Los 6 clientes de la exportacion de PRUEBA, con una sola compra: no hay grupos
        tabla = pedidos([("1", "6", "2026-10-30 00:00:00", "confirmado", 4796.0)])
        tabla_rfm = segmentacion.rfm(tabla, clientes(6), CORTE)
        seleccion, clusters, con_cluster = segmentacion.kmeans_clientes(tabla_rfm)
        self.assertEqual(seleccion["estado"].iloc[0], NO_CALCULABLE)
        self.assertEqual(clusters["estado"].iloc[0], NO_CALCULABLE)
        self.assertTrue(con_cluster["cluster"].isna().all())
        self.assertEqual(segmentacion.comparar_rfm_kmeans(con_cluster)["estado"].iloc[0], NO_CALCULABLE)


if __name__ == "__main__":
    unittest.main()
