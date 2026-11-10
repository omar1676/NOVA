"""
Pruebas del ciclo de comprobacion y recalculo (actualizacion.py), del
registro de eventos (registro.py) y del informe ejecutivo (informe.py).

Siguen las pruebas de actualizacion de la rubrica (apartado 6.17): pedido
nuevo (R1), cancelacion (R2), cambio de stock (R3), CSV defectuoso (R4) y sin
cambios (R5). Cada prueba cambia los CSV de una carpeta temporal entre dos
ciclos: el segundo ciclo tiene que RELEER el disco para verlo. El registro va
a otra carpeta temporal (nunca a logs/ ni a la carpeta de entrada).
"""
import hashlib
import os
import tempfile
import time
from pathlib import Path

import pandas as pd

import actualizacion
import config
import generador_datos
import informe
import registro
from analiticas import NO_CALCULABLE
from test_calidad import PruebaCalidad
from test_pipeline import VALIDOS

PEDIDO_NUEVO = "12,P-3,1,2026-11-05 10:00:00,normal,confirmado,pagado,,3,239.97\n"
LINEAS_NUEVAS = "103,12,M1-40,1,40,1,79.99,79.99\n104,12,M1-41,1,41,2,79.99,159.98\n"


def valor(estado, codigo):
    tabla = estado["publicado"]["kpis"]
    return tabla.loc[tabla["codigo"] == codigo, "valor"].iloc[0]


class PruebaCiclo(PruebaCalidad):
    """Base: la carpeta con los cinco CSV validos y un registro aparte."""

    def setUp(self):
        super().setUp()
        self.otra = tempfile.TemporaryDirectory()
        self.archivo_registro = Path(self.otra.name) / "registro_eventos.csv"

    def tearDown(self):
        self.otra.cleanup()
        super().tearDown()

    def ciclo(self, anterior=None, operacion="prueba"):
        return actualizacion.ciclo(self.carpeta, anterior, operacion, self.archivo_registro)


class PruebasCiclo(PruebaCiclo):

    def test_primer_ciclo_publica(self):
        estado = self.ciclo()
        self.assertEqual(estado["estado"], actualizacion.CORRECTO)
        self.assertFalse(estado["desactualizado"])
        self.assertEqual(valor(estado, "K01"), 2)
        self.assertEqual(estado["publicado"]["filas_validas"], 12)
        self.assertEqual(len(estado["version"]), 8)
        self.assertEqual(estado["publicado"]["actualizado"], estado["comprobado"])

    def test_sin_cambios_R5(self):
        primero = self.ciclo()
        time.sleep(1.1)
        segundo = self.ciclo(primero)
        self.assertEqual(segundo["estado"], actualizacion.SIN_CAMBIOS)
        self.assertGreater(segundo["comprobado"], primero["comprobado"])          # cambia la comprobacion
        self.assertEqual(segundo["publicado"]["actualizado"], primero["publicado"]["actualizado"])
        self.assertIsNot(segundo["publicado"], primero["publicado"])               # se ha vuelto a calcular
        pd.testing.assert_frame_equal(segundo["publicado"]["kpis"], primero["publicado"]["kpis"])

    def test_reexportar_lo_mismo_no_es_un_cambio(self):
        primero = self.ciclo()
        self.escribir("pedidos.csv", VALIDOS["pedidos.csv"])               # mismo contenido, fecha nueva
        os.utime(self.carpeta / "pedidos.csv", (time.time() + 5, time.time() + 5))
        self.assertEqual(self.ciclo(primero)["estado"], actualizacion.SIN_CAMBIOS)

    def test_pedido_nuevo_R1(self):
        primero = self.ciclo()
        self.anadir("pedidos.csv", PEDIDO_NUEVO)
        self.anadir("lineas_pedido.csv", LINEAS_NUEVAS)
        segundo = self.ciclo(primero)
        self.assertEqual(segundo["estado"], actualizacion.CORRECTO)
        self.assertNotEqual(segundo["version"], primero["version"])
        self.assertEqual(valor(segundo, "K01"), valor(primero, "K01") + 1)     # un pedido mas, no dos
        self.assertEqual(valor(segundo, "K05"), valor(primero, "K05") + 3)     # sus 3 pares, una vez
        self.assertAlmostEqual(valor(segundo, "K07"), valor(primero, "K07") + 239.97, places=2)
        self.assertEqual(len(segundo["publicado"]["tablas"]["pedidos_unicos"]), 3)

    def test_cancelacion_R2(self):
        primero = self.ciclo()
        self.cambiar("pedidos.csv", "normal,confirmado,pagado", "normal,cancelado,reembolsado")
        segundo = self.ciclo(primero)
        self.assertEqual(valor(segundo, "K02"), 0)                      # baja la venta valida
        self.assertEqual(valor(segundo, "K07"), 0)
        self.assertEqual(valor(segundo, "K01"), valor(primero, "K01"))  # el pedido sigue en la actividad
        self.assertEqual(valor(segundo, "K03"), 2)

    def test_sin_ninguna_venta(self):
        # Cancelado el unico pedido confirmado, no queda ningun cliente con compras
        self.cambiar("pedidos.csv", "normal,confirmado,pagado", "normal,cancelado,reembolsado")
        estado = self.ciclo()
        self.assertEqual(estado["estado"], actualizacion.CORRECTO)
        conclusiones = estado["publicado"]["informe"].set_index("numero")
        self.assertTrue(conclusiones.loc[3, "evidencia"].startswith(f"{NO_CALCULABLE}: 0 cliente(s)"))

    def test_cambio_de_stock_R3(self):
        primero = self.ciclo()
        self.assertEqual(valor(primero, "K17"), 2)                      # M1-40 (5) y M1-41 (0)
        self.cambiar("stock.csv", "M1-40,1,Blanco,40,true,5,", "M1-40,1,Blanco,40,true,50,")
        segundo = self.ciclo(primero)
        self.assertEqual(valor(segundo, "K17"), 1)
        self.assertEqual(valor(segundo, "K16"), valor(primero, "K16") + 45)

    def test_csv_ausente_R4_y_recuperacion(self):
        primero = self.ciclo()
        (self.carpeta / "pedidos.csv").unlink()
        segundo = self.ciclo(primero)
        self.assertEqual(segundo["estado"], actualizacion.ERROR_CARGA)
        self.assertTrue(segundo["desactualizado"])                      # se conserva lo ultimo valido...
        self.assertIs(segundo["publicado"], primero["publicado"])       # ...sin recalcular nada a medias
        self.assertIn("Falta pedidos.csv: la exportación está incompleta.", segundo["avisos"])
        # Ni el mensaje ni el registro llevan la ruta completa del ordenador
        self.assertNotIn(str(self.carpeta), segundo["mensaje"])
        self.assertNotIn(str(self.carpeta), self.archivo_registro.read_text(encoding="utf-8"))
        self.escribir("pedidos.csv", VALIDOS["pedidos.csv"])
        tercero = self.ciclo(segundo)
        self.assertFalse(tercero["desactualizado"])
        self.assertIn(tercero["estado"], [actualizacion.CORRECTO, actualizacion.SIN_CAMBIOS])

    def test_csv_corrupto(self):
        primero = self.ciclo()
        self.escribir("pedidos.csv", VALIDOS["pedidos.csv"].replace("id_pedido,", "", 1))   # sin columna clave
        segundo = self.ciclo(primero)
        self.assertEqual(segundo["estado"], actualizacion.ERROR_CARGA)
        self.assertTrue(segundo["desactualizado"])
        self.assertIn("bloqueantes", segundo["mensaje"])

    def test_clave_huerfana_no_publica(self):
        self.anadir("lineas_pedido.csv", "103,99,M1-40,1,40,1,79.99,79.99\n")
        estado = self.ciclo()
        self.assertEqual(estado["estado"], actualizacion.DATOS_INVALIDOS)
        self.assertIsNone(estado["publicado"])                          # ninguna cifra

    def test_avisos_de_exportacion_antigua_o_incompleta(self):
        hace_dos_dias = time.time() - 2 * 24 * 3600
        os.utime(self.carpeta / "pedidos.csv", (hace_dos_dias, hace_dos_dias))
        avisos = " ".join(self.ciclo()["avisos"])
        self.assertIn("Exportación antigua", avisos)
        self.assertIn("minutos de diferencia", avisos)

    def test_no_escribe_en_la_entrada(self):
        def huellas():
            return {ruta.name: hashlib.sha256(ruta.read_bytes()).hexdigest() for ruta in self.carpeta.iterdir()}
        antes = huellas()
        estado = self.ciclo()
        self.ciclo(estado)
        self.assertEqual(huellas(), antes)

    def test_datos_insuficientes(self):
        publicado = self.ciclo()["publicado"]
        self.assertEqual(publicado["segmentacion"]["kmeans_clusters"]["estado"].iloc[0], NO_CALCULABLE)
        self.assertEqual(publicado["prediccion"]["metricas_prediccion"]["estado"].iloc[0], NO_CALCULABLE)
        calculables = publicado["informe"].set_index("numero")["calculable"]
        self.assertFalse(calculables[3])                                # RFM: pocos clientes
        self.assertFalse(calculables[5])                                # prediccion: pocos meses
        self.assertTrue(publicado["informe"].loc[publicado["informe"]["numero"] == 3, "evidencia"].iloc[0]
                        .startswith(NO_CALCULABLE))


class PruebasOrigenes(PruebaCiclo):

    def test_cambio_de_origen_no_mezcla(self):
        prueba = self.ciclo()
        with tempfile.TemporaryDirectory() as temporal:
            sinteticos = generador_datos.guardar(generador_datos.generar(config.SEMILLA), Path(temporal), "test")
            otro = actualizacion.ciclo(sinteticos, prueba, "cambio de origen", self.archivo_registro)
        self.assertEqual(otro["estado"], actualizacion.CORRECTO)        # no hereda nada de la otra carpeta
        self.assertEqual(otro["tipo"], "SINTETICO")
        self.assertEqual(valor(otro, "K01"), 900)
        self.assertEqual(valor(prueba, "K01"), 2)
        self.assertNotEqual(otro["version"], prueba["version"])

    def test_sinteticos_con_errores_bloquean(self):
        with tempfile.TemporaryDirectory() as temporal:
            con_errores, _ = generador_datos.introducir_errores(generador_datos.generar(config.SEMILLA))
            carpeta = generador_datos.guardar(con_errores, Path(temporal), "test con errores")
            estado = actualizacion.ciclo(carpeta, None, "prueba", self.archivo_registro)
        self.assertEqual(estado["estado"], actualizacion.DATOS_INVALIDOS)
        self.assertIsNone(estado["publicado"])
        self.assertGreater((estado["calidad"]["incidencias"]["gravedad"] == "bloqueante").sum(), 0)


class PruebasRegistro(PruebaCiclo):

    def test_una_fila_por_ciclo_en_un_solo_archivo(self):
        estado = self.ciclo(operacion="carga inicial del origen")
        estado = self.ciclo(estado, operacion="comprobación automática (60 s)")
        self.anadir("lineas_pedido.csv", "103,99,M1-40,1,40,1,79.99,79.99\n")
        self.ciclo(estado, operacion="actualización manual")
        self.assertEqual([ruta.name for ruta in Path(self.otra.name).iterdir()], ["registro_eventos.csv"])
        filas = registro.leer(self.archivo_registro)                    # la mas reciente, primero
        self.assertEqual(len(filas), 3)
        self.assertEqual(list(filas.columns), registro.COLUMNAS)
        self.assertEqual(filas["resultado"].tolist(), ["DATOS INVÁLIDOS", "SIN CAMBIOS", "CORRECTO"])
        self.assertEqual(filas["operacion"].tolist(),
                         ["actualización manual", "comprobación automática (60 s)", "carga inicial del origen"])
        self.assertEqual(filas["filas_procesadas"].iloc[-1], "12")
        self.assertEqual(filas["bloqueantes"].iloc[0], "1")
        # Sin rutas completas del ordenador ni datos de clientes
        self.assertEqual(filas["carpeta"].iloc[0], self.carpeta.name)
        texto = self.archivo_registro.read_text(encoding="utf-8")
        self.assertNotIn(str(Path.home()), texto)
        self.assertNotIn("Nuria", texto)

    def test_detalle_en_una_linea(self):
        registro.anotar(self.archivo_registro, operacion="prueba", detalle="linea uno\nlinea dos")
        self.assertEqual(registro.leer(self.archivo_registro)["detalle"].iloc[0], "linea uno linea dos")


class PruebasInforme(PruebaCiclo):

    def test_cinco_conclusiones_con_procedencia(self):
        with tempfile.TemporaryDirectory() as temporal:
            sinteticos = generador_datos.guardar(generador_datos.generar(config.SEMILLA), Path(temporal), "test")
            publicado = actualizacion.ciclo(sinteticos, None, "prueba", self.archivo_registro)["publicado"]
        conclusiones = publicado["informe"]
        self.assertEqual(conclusiones["numero"].tolist(), [1, 2, 3, 4, 5])
        self.assertTrue(conclusiones["calculable"].all())
        self.assertEqual(conclusiones["procede_de"].tolist(), ["Datos sintéticos"] * 4 + ["Predicción · Datos sintéticos"])
        for columna in ["evidencia", "interpretacion", "decision", "limitacion"]:
            self.assertTrue((conclusiones[columna].str.len() > 20).all(), columna)
        self.assertTrue(conclusiones["limitacion"].str.contains("no son ventas ni clientes reales").all())
        # Las cifras salen de las tablas, no estan escritas a mano
        custom = publicado["tablas"]["custom_vs_estandar"].set_index("tipo_pedido").loc["custom"]
        self.assertIn(f"{informe.numero(custom['cuota_importe_pct'], 1)} % del importe", conclusiones["evidencia"][1])
        metricas = publicado["prediccion"]["metricas_prediccion"].set_index("metodo")
        self.assertIn(f"MAE {informe.numero(metricas.loc['baseline', 'mae'], 2)}", conclusiones["evidencia"][4])

    def test_prioridad_impacto_y_sustento(self):
        with tempfile.TemporaryDirectory() as temporal:
            sinteticos = generador_datos.guardar(generador_datos.generar(config.SEMILLA), Path(temporal), "test")
            publicado = actualizacion.ciclo(sinteticos, None, "prueba", self.archivo_registro)["publicado"]
        conclusiones = publicado["informe"]
        # Las columnas de antes no cambian de sitio; las nuevas van al final
        self.assertEqual(list(conclusiones.columns)[-4:], ["prioridad", "urgencia", "impacto_esperado", "sustento"])
        self.assertEqual(sorted(conclusiones["prioridad"]), [1, 2, 3, 4, 5])
        # Criterio: primero la urgencia (alta, media, baja) y, con la misma, el numero
        orden = conclusiones.sort_values("prioridad")
        claves = [(informe.URGENCIAS[urgencia], numero_) for urgencia, numero_ in zip(orden["urgencia"], orden["numero"])]
        self.assertEqual(claves, sorted(claves))
        por_numero = conclusiones.set_index("numero")
        stock = publicado["tablas"]["stock_variantes"]
        en_riesgo = stock[stock["alerta_stock_bajo"] & (stock["demanda_28d"] > 0)]
        self.assertGreater(len(en_riesgo), 0)
        self.assertEqual(por_numero.loc[4, "urgencia"], "alta")       # hay SKU que se pueden agotar
        self.assertIn(f"{len(en_riesgo)} SKU", por_numero.loc[4, "impacto_esperado"])
        custom = publicado["tablas"]["custom_vs_estandar"].set_index("tipo_pedido").loc["custom"]
        self.assertIn(f"{informe.numero(custom['cuota_pares_pct'], 1)} % de los pares", por_numero.loc[2, "impacto_esperado"])
        for _, fila in por_numero.iterrows():
            self.assertGreater(len(fila["impacto_esperado"]), 20)
            self.assertIn(".csv", fila["sustento"])                     # la tabla que la sustenta

    def test_sin_datos_la_urgencia_es_baja(self):
        self.escribir(config.ARCHIVO_ORIGEN, "Tipo: PRUEBA\nbase de prueba\n")
        conclusiones = self.ciclo()["publicado"]["informe"].set_index("numero")
        sin_datos = conclusiones[~conclusiones["calculable"]]
        self.assertGreater(len(sin_datos), 0)
        self.assertEqual(set(sin_datos["urgencia"]), {"baja"})
        self.assertTrue(sin_datos["impacto_esperado"].str.startswith("Ninguno todavía").all())

    def test_datos_de_prueba_se_dicen_de_prueba(self):
        self.escribir(config.ARCHIVO_ORIGEN, "Tipo: PRUEBA\nbase de prueba\n")
        conclusiones = self.ciclo()["publicado"]["informe"]
        self.assertEqual(conclusiones["procede_de"].iloc[0], "Datos de prueba (exportación de ACC)")
        self.assertTrue(conclusiones["limitacion"].str.contains("no son ventas reales").all())
        self.assertFalse(conclusiones["procede_de"].str.contains("reales").any())

    def test_formato_espanol(self):
        self.assertEqual(informe.numero(1234.5, 1), "1.234,5")
        self.assertEqual(informe.numero(831377.51, 2), "831.377,51")
