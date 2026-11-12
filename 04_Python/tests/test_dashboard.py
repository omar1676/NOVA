"""
Pruebas del dashboard (app_dashboard.py) con AppTest de Streamlit: se ejecuta
la aplicacion de verdad (sin navegador) y se leen sus tarjetas, avisos y
pestanas.

Las tres carpetas de origen y el registro de eventos son temporales: durante
estas pruebas se cambian en config (AppTest ejecuta la app en este mismo
proceso) y al terminar se dejan como estaban. Nunca se tocan entrada_acc/,
datos_sinteticos/ ni logs/.
"""
import io
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

import pandas as pd
import streamlit as st
from streamlit.testing.v1 import AppTest

import calidad
import config
import filtros
import generador_datos
import registro
from informe import numero
from test_actualizacion import LINEAS_NUEVAS, PEDIDO_NUEVO
from test_pipeline import VALIDOS

APP = str(Path(__file__).resolve().parent.parent / "app_dashboard.py")
PESTANAS = ["Dirección", "Productos", "Clientes", "Inventario", "Calidad", "Predicción"]
CAMBIADOS = ["CARPETA_ENTRADA", "CARPETA_SINTETICOS_LIMPIOS", "CARPETA_SINTETICOS_ERRORES", "ARCHIVO_REGISTRO"]


class PruebaApp(unittest.TestCase):
    """Base: tres origenes temporales (prueba, sinteticos y sinteticos con errores)."""

    @classmethod
    def setUpClass(cls):
        cls.temporal = tempfile.TemporaryDirectory()
        base = Path(cls.temporal.name)
        datos = generador_datos.generar(config.SEMILLA)
        con_errores, _ = generador_datos.introducir_errores(datos)
        cls.limpios = generador_datos.guardar(datos, base / "limpios", "test")
        errores = generador_datos.guardar(con_errores, base / "con_errores", "test")
        cls.acc = base / "entrada_acc"
        cls.graficos = base / "graficos"
        cls.graficos.mkdir()
        cls.originales = {nombre: getattr(config, nombre) for nombre in CAMBIADOS}
        config.CARPETA_ENTRADA = cls.acc
        config.CARPETA_SINTETICOS_LIMPIOS = cls.limpios
        config.CARPETA_SINTETICOS_ERRORES = errores
        config.ARCHIVO_REGISTRO = base / "logs" / "registro_eventos.csv"

    @classmethod
    def tearDownClass(cls):
        for nombre, valor in cls.originales.items():
            setattr(config, nombre, valor)
        cls.temporal.cleanup()

    def setUp(self):
        # La exportacion "de prueba": los cinco CSV validos de test_pipeline.py
        self.acc.mkdir(exist_ok=True)
        for archivo, texto in VALIDOS.items():
            (self.acc / archivo).write_text(texto, encoding="utf-8", newline="")
        (self.acc / config.ARCHIVO_ORIGEN).write_text("Tipo: PRUEBA\nbase de prueba\n", encoding="utf-8")

    def abrir(self, origen="acc", pestana=None):
        app = AppTest.from_file(APP, default_timeout=120)
        app.session_state["carpeta_graficos"] = str(self.graficos)
        app.session_state["origen"] = origen
        if pestana:
            app.session_state["pestana"] = pestana
        app.run()
        self.assertEqual(len(app.exception), 0, [e.value for e in app.exception])
        return app

    def tarjetas(self, app):
        return {tarjeta.label: tarjeta.value for tarjeta in app.metric}

    def textos(self, elementos):
        return " ".join(str(elemento.value) for elemento in elementos)

    def pasar_un_minuto(self, app, origen="acc"):
        """Como si hubieran pasado los 60 s desde la ultima comprobacion."""
        estados = app.session_state["estados"]
        estados[origen]["comprobado"] -= timedelta(seconds=config.SEGUNDOS_REFRESCO + 1)
        app.session_state["estados"] = estados


class PruebasArranque(PruebaApp):

    def test_arranca_con_la_exportacion_de_acceso_a_datos(self):
        app = self.abrir()
        self.assertEqual(app.sidebar.selectbox(key="origen").value, "acc")
        self.assertIn("NOVA Sneakers", app.title[0].value)
        self.assertIn("PRUEBA", self.textos(app.info))               # se dice que son datos de prueba
        self.assertNotIn("SINTÉTICOS", self.textos(app.warning))
        tarjetas = self.tarjetas(app)
        self.assertEqual(tarjetas["Estado"], "Correcto")
        self.assertEqual(tarjetas["Pedidos registrados"], "2")
        self.assertEqual(tarjetas["Filas válidas"], "12")

    def test_seis_pestanas(self):
        app = self.abrir()
        self.assertEqual([pestana.label for pestana in app.tabs], PESTANAS)   # las 5 obligatorias + prediccion

    def test_todas_las_pestanas_sin_errores(self):
        for origen in ["acc", "sinteticos", "sinteticos-errores"]:
            for pestana in PESTANAS:
                with self.subTest(origen=origen, pestana=pestana):
                    self.abrir(origen, pestana)

    def test_al_menos_cinco_descargas(self):
        nombres = set()
        for pestana in PESTANAS:
            app = self.abrir("sinteticos", pestana)
            nombres.update(boton.label for boton in app.get("download_button"))
        self.assertGreaterEqual(len(nombres), 5, nombres)

    def test_sin_datos_suficientes_lo_dice(self):
        clientes = self.abrir("acc", "Clientes")
        self.assertIn("NO CALCULABLE", self.textos(clientes.info))   # RFM y KMeans con 2 clientes
        prediccion = self.abrir("acc", "Predicción")
        self.assertIn("NO CALCULABLE", self.textos(prediccion.info))


class PruebasCalidadYOrigen(PruebaApp):

    def test_bloqueo_por_calidad_sin_cifras(self):
        for pestana in ["Dirección", "Productos", "Clientes", "Inventario", "Predicción"]:
            with self.subTest(pestana=pestana):
                app = self.abrir("sinteticos-errores", pestana)
                self.assertIn("No se publican cifras", self.textos(app.error))
                self.assertNotIn("Pedidos registrados", self.tarjetas(app))
        calidad_app = self.abrir("sinteticos-errores", "Calidad")
        self.assertIn("BLOQUEADO", self.textos(calidad_app.error))
        self.assertEqual(self.tarjetas(calidad_app)["Bloqueantes"], "3")

    def test_cambio_de_origen(self):
        app = self.abrir("acc")
        self.assertEqual(self.tarjetas(app)["Pedidos registrados"], "2")
        app.sidebar.selectbox(key="origen").set_value("sinteticos").run()
        self.assertEqual(self.tarjetas(app)["Pedidos registrados"], "900")
        self.assertIn("SINTÉTICOS", self.textos(app.warning))        # siempre se ve el origen
        app.sidebar.selectbox(key="origen").set_value("acc").run()
        self.assertEqual(self.tarjetas(app)["Pedidos registrados"], "2")
        self.assertEqual(set(app.session_state["estados"]), {"acc", "sinteticos"})   # cada uno, el suyo


class PruebasRefresco(PruebaApp):

    def test_relee_los_csv_cada_60_segundos(self):
        app = self.abrir("acc")
        self.assertEqual(self.tarjetas(app)["Pedidos registrados"], "2")
        (self.acc / "pedidos.csv").write_text(VALIDOS["pedidos.csv"] + PEDIDO_NUEVO, encoding="utf-8", newline="")
        (self.acc / "lineas_pedido.csv").write_text(VALIDOS["lineas_pedido.csv"] + LINEAS_NUEVAS, encoding="utf-8",
                                                     newline="")
        app.run()                                                    # antes del minuto: el mismo resultado
        self.assertEqual(self.tarjetas(app)["Pedidos registrados"], "2")
        self.pasar_un_minuto(app)
        app.run()                                                    # al minuto: relee el disco
        tarjetas = self.tarjetas(app)
        self.assertEqual(tarjetas["Pedidos registrados"], "3")
        self.assertEqual(tarjetas["Estado"], "Correcto")
        self.pasar_un_minuto(app)
        app.run()                                                    # sin cambios en los CSV
        self.assertEqual(self.tarjetas(app)["Estado"], "Sin cambios")
        self.assertEqual(self.tarjetas(app)["Pedidos registrados"], "3")
        operaciones = registro.leer(config.ARCHIVO_REGISTRO)["operacion"].tolist()
        self.assertEqual(operaciones[:2], ["comprobación automática (60 s)"] * 2)

    def test_boton_actualizar_ahora(self):
        app = self.abrir("acc")
        (self.acc / "pedidos.csv").write_text(VALIDOS["pedidos.csv"] + PEDIDO_NUEVO, encoding="utf-8", newline="")
        (self.acc / "lineas_pedido.csv").write_text(VALIDOS["lineas_pedido.csv"] + LINEAS_NUEVAS, encoding="utf-8",
                                                     newline="")
        app.sidebar.button[0].click().run()
        self.assertEqual(self.tarjetas(app)["Pedidos registrados"], "3")
        ultimo = registro.leer(config.ARCHIVO_REGISTRO).iloc[0]
        self.assertEqual((ultimo["operacion"], ultimo["resultado"]), ("actualización manual", "CORRECTO"))

    def test_csv_defectuoso_no_publica_cifras(self):
        app = self.abrir("acc")
        (self.acc / "pedidos.csv").unlink()
        self.pasar_un_minuto(app)
        app.run()
        self.assertEqual(self.tarjetas(app)["Estado"], "Error de carga")
        self.assertIn("Falta pedidos.csv", self.textos(app.warning))
        self.assertNotIn("Pedidos registrados", self.tarjetas(app))   # nada nuevo ni viejo sin avisar
        self.assertIn("DESACTUALIZADO", app.toggle(key="ver_desactualizado").label)


class PruebasFiltros(PruebaApp):

    def test_cuatro_filtros_combinados_cambian_los_kpis(self):
        app = self.abrir("sinteticos")
        app.sidebar.date_input(key="periodo_1").set_value((date(2026, 1, 1), date(2026, 6, 30)))
        app.sidebar.multiselect(key="modelos_1").set_value(["SINT Runner", "SINT Court"])
        app.sidebar.multiselect(key="tipos_1").set_value(["normal"])
        app.sidebar.multiselect(key="estados_1").set_value(["entregado", "enviado"])
        app.run()
        self.assertEqual(len(app.exception), 0)
        elegidos = {"desde": "2026-01-01", "hasta": "2026-06-30", "modelos": ["SINT Runner", "SINT Court"],
                    "tallas": [], "tipos": ["normal"], "estados": ["entregado", "enviado"]}
        resultado = calidad.evaluar(self.limpios)
        esperados = filtros.calcular_filtrado(resultado["datos"], resultado["validos"], elegidos)["kpis"]
        valor = dict(zip(esperados["codigo"], esperados["valor"]))
        tarjetas = self.tarjetas(app)
        self.assertEqual(tarjetas["Pedidos registrados"], numero(valor["K01"]))
        self.assertEqual(tarjetas["Pares solicitados"], numero(valor["K04"]))
        self.assertEqual(tarjetas["Importe confirmado"], f"{numero(valor['K07'], 2)} €")
        self.assertNotEqual(tarjetas["Pedidos registrados"], "900")
        self.assertIn(f"{valor['K01']} de 900 pedidos registrados", self.textos(app.caption))

        app.sidebar.button[1].click().run()                          # Restablecer filtros
        self.assertEqual(self.tarjetas(app)["Pedidos registrados"], "900")

    def test_filtro_de_cliente_combinado_y_restablecer(self):
        resultado = calidad.evaluar(self.limpios)
        pedidos = resultado["validos"]["pedidos"]
        cliente = pedidos.loc[pedidos["tipo_pedido"] == "custom", "id_cliente"].value_counts().index[0]
        app = self.abrir("sinteticos")
        app.sidebar.multiselect(key="clientes_1").set_value([cliente])
        app.sidebar.multiselect(key="tipos_1").set_value(["custom"])
        app.run()
        elegidos = {**filtros.SIN_FILTROS, "clientes": [cliente], "tipos": ["custom"]}
        esperados = filtros.calcular_filtrado(resultado["datos"], resultado["validos"], elegidos)["kpis"]
        valor = dict(zip(esperados["codigo"], esperados["valor"]))
        suyos = pedidos[(pedidos["id_cliente"] == cliente) & (pedidos["tipo_pedido"] == "custom")]
        self.assertEqual(valor["K01"], len(suyos))
        self.assertEqual(self.tarjetas(app)["Pedidos registrados"], numero(len(suyos)))
        self.assertEqual(self.tarjetas(app)["Importe confirmado"], f"{numero(valor['K07'], 2)} €")
        self.assertIn(f"{len(suyos)} de 900 pedidos registrados", self.textos(app.caption))

        app.sidebar.button[1].click().run()                          # Restablecer filtros: tambien el cliente
        self.assertEqual(app.sidebar.multiselect(key="clientes_1").value, [])
        self.assertEqual(app.sidebar.multiselect(key="tipos_1").value, [])
        self.assertEqual(self.tarjetas(app)["Pedidos registrados"], "900")

    def test_filtros_y_pestana_se_mantienen_al_refrescar(self):
        app = self.abrir("acc", "Productos")
        app.sidebar.multiselect(key="clientes_0").set_value(["1"])
        app.sidebar.multiselect(key="tallas_0").set_value([40])
        app.run()
        self.assertEqual(self.pares_abc(app), {"Modelo Uno": 1, "Modelo Dos": 0})    # P-1, talla 40
        # Acceso a Datos exporta un pedido nuevo del cliente 1 con el dashboard abierto
        (self.acc / "pedidos.csv").write_text(VALIDOS["pedidos.csv"] + PEDIDO_NUEVO, encoding="utf-8", newline="")
        (self.acc / "lineas_pedido.csv").write_text(VALIDOS["lineas_pedido.csv"] + LINEAS_NUEVAS, encoding="utf-8",
                                                     newline="")
        self.pasar_un_minuto(app)
        app.run()                                                    # refresco de 60 s con datos nuevos
        self.assertEqual(self.tarjetas(app)["Estado"], "Correcto")
        # La misma pestana y los mismos filtros, y las cifras ya son las de la exportacion nueva
        self.assertEqual(app.session_state["pestana"], "Productos")
        titulos = [titulo.value for titulo in app.subheader]
        self.assertIn("Ranking de modelos y clasificación ABC", titulos)
        self.assertNotIn("Indicadores principales", titulos)
        self.assertEqual(app.sidebar.multiselect(key="clientes_0").value, ["1"])
        self.assertEqual(app.sidebar.multiselect(key="tallas_0").value, [40])
        self.assertEqual(self.pares_abc(app), {"Modelo Uno": 2, "Modelo Dos": 0})    # P-1 y P-3
        # Sin duplicar nada: un solo ranking y un solo boton de restablecer
        self.assertEqual(titulos.count("Ranking de modelos y clasificación ABC"), 1)
        self.assertEqual([boton.label for boton in app.sidebar.button].count("Restablecer filtros"), 1)

    def pares_abc(self, app):
        """Pares por modelo de la tabla ABC de la pestana Productos."""
        for tabla in app.dataframe:
            datos = tabla.value
            if "clase_abc" in datos.columns:
                return dict(zip(datos["nombre_modelo"], datos["pares"]))
        self.fail("no está la tabla ABC")

    def test_filtrado_cruzado_R6(self):
        """
        R6: mismo periodo, modelo y talla en varias vistas (Direccion, Productos y Clientes). Las tarjetas, las
        tablas de los graficos, los CSV descargados y su suma dicen lo mismo, y todo es del mismo snapshot.
        """
        app = self.abrir("sinteticos")
        app.sidebar.date_input(key="periodo_1").set_value((date(2026, 1, 1), date(2026, 6, 30)))
        app.sidebar.multiselect(key="modelos_1").set_value(["SINT Runner"])
        app.sidebar.multiselect(key="tallas_1").set_value([42])
        # Se guarda lo que el dashboard entrega en cada boton de descarga
        descargas = {}
        boton_real = st.download_button

        def boton_que_guarda(etiqueta, datos, *args, **opciones):
            descargas[opciones["file_name"]] = pd.read_csv(io.BytesIO(datos), encoding="utf-8")
            return boton_real(etiqueta, datos, *args, **opciones)

        tablas_graficos = {}
        with mock.patch.object(st, "download_button", boton_que_guarda):
            app.run()                                                # Direccion
            tarjetas = self.tarjetas(app)
            for pestana in ["Productos", "Clientes"]:
                tablas_graficos.update(self.tablas_de_graficos(app))
                app.session_state["pestana"] = pestana
                app.run()
                self.assertEqual(len(app.exception), 0)
                self.assertEqual(app.session_state["pestana"], pestana)
            tablas_graficos.update(self.tablas_de_graficos(app))

        # Lo que tiene que salir, calculado aparte con pandas sobre las lineas validas
        resultado = calidad.evaluar(self.limpios)
        lineas = filtros.calcular_filtrado(resultado["datos"], resultado["validos"], filtros.SIN_FILTROS)[
            "lineas_enriquecidas"]
        elegidas = lineas[(lineas["fecha_pedido"] >= "2026-01-01") & (lineas["fecha_pedido"] < "2026-07-01")
                          & (lineas["nombre_modelo"] == "SINT Runner") & (lineas["talla"] == 42)]
        pares = int(elegidas.loc[~elegidas["es_cancelado"], "cantidad"].sum())
        venta = elegidas[elegidas["estado_pedido"].isin(config.ESTADOS_CONFIRMADOS)]
        importe = round(float(venta["importe_linea"].sum()), 2)
        pedidos = elegidas["id_pedido"].nunique()
        self.assertGreater(pares, 0)

        # 1. Tarjetas de Direccion
        self.assertEqual(tarjetas["Pedidos registrados"], numero(pedidos))
        self.assertEqual(tarjetas["Pares solicitados"], numero(pares))
        self.assertEqual(tarjetas["Importe confirmado"], f"{numero(importe, 2)} €")
        # 2. Tablas de los graficos (lo que dibuja cada uno)
        self.assertEqual(int(tablas_graficos["evolucion"].drop(columns="nombre_modelo").to_numpy().sum()), pares)
        self.assertEqual(int(tablas_graficos["tallas"]["pares"].sum()), pares)
        self.assertEqual(set(tablas_graficos["tallas"]["talla"]), {42})
        self.assertAlmostEqual(float(tablas_graficos["meses"]["importe"].sum()), importe, places=2)
        # 3. CSV descargados en las tres pestanas y su suma
        ventas = descargas["ventas_por_periodo_sintetico.csv"]
        self.assertAlmostEqual(float(ventas["importe"].sum()), importe, places=2)
        unicos = descargas["pedidos_unicos_sintetico.csv"]
        self.assertEqual(len(unicos), pedidos)
        self.assertEqual(int(unicos.loc[unicos["estado_pedido"] != "cancelado", "pares"].sum()), pares)
        abc = descargas["modelos_abc_sintetico.csv"].set_index("nombre_modelo")
        self.assertEqual(int(abc["pares"].sum()), pares)
        self.assertEqual(int(abc.loc["SINT Runner", "pares"]), pares)
        matriz = descargas["matriz_modelo_talla_sintetico.csv"]
        self.assertEqual(int(matriz["42"].sum()), pares)
        clientes = descargas["clientes_actividad_sintetico.csv"]
        self.assertEqual(int(clientes["pares_demanda"].sum()), pares)
        self.assertAlmostEqual(float(clientes["importe_venta"].sum()), importe, places=2)
        self.assertEqual(int(clientes["pedidos_registrados"].sum()), pedidos)
        # 4. Todas las descargas son del mismo snapshot; las filtradas llevan los mismos filtros y RFM dice que es global
        juntas = pd.concat(descargas.values())
        self.assertEqual(juntas["ejecucion"].nunique(), 1)
        self.assertEqual(juntas["fecha_corte"].nunique(), 1)
        for tabla in [ventas, unicos, descargas["modelos_abc_sintetico.csv"], matriz, clientes]:
            self.assertEqual(set(tabla["filtros"]), {"periodo 2026-01-01 a 2026-06-30 · modelo: SINT Runner · talla: 42"})
        self.assertEqual(set(descargas["rfm_clientes_sintetico.csv"]["filtros"]), {"ninguno (resultado global)"})

    def tablas_de_graficos(self, app):
        """Las tablas que hay debajo de los graficos de la pestana abierta, reconocidas por sus columnas."""
        encontradas = {}
        for tabla in app.dataframe:
            datos = tabla.value
            if "nombre_modelo" in datos.columns and any(str(columna).startswith("20") for columna in datos.columns):
                encontradas["evolucion"] = datos                     # matriz modelo x mes del grafico de evolucion
            elif list(datos.columns[:2]) == ["talla", "pares"]:
                encontradas["tallas"] = datos                        # grafico de pares por talla
            elif list(datos.columns[:2]) == ["anio_mes", "pedidos"]:
                encontradas["meses"] = datos                         # importe confirmado por mes
        return encontradas


if __name__ == "__main__":
    unittest.main()
