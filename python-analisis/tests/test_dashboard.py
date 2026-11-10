"""
Pruebas del dashboard (app_dashboard.py) con AppTest de Streamlit: se ejecuta
la aplicacion de verdad (sin navegador) y se leen sus tarjetas, avisos y
pestanas.

Las tres carpetas de origen y el registro de eventos son temporales: durante
estas pruebas se cambian en config (AppTest ejecuta la app en este mismo
proceso) y al terminar se dejan como estaban. Nunca se tocan entrada_acc/,
datos_sinteticos/ ni logs/.
"""
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
