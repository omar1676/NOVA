import contextlib
import io
from pathlib import Path
from unittest import mock

import pandas as pd

import actualizacion
import analiticas
import calidad
import comprobaciones
import main
import pipeline
from test_actualizacion import PruebaCiclo

CARPETA_PYTHON = Path(__file__).resolve().parent.parent

CABECERAS = {
    "clientes.csv": "id_cliente,nombre,tipo,correo,telefono,activo\n",
    "modelos.csv": "id_modelo,nombre_modelo,descripcion,precio_base,activo\n",
    "pedidos.csv": "id_pedido,referencia,id_cliente,fecha_pedido,tipo_pedido,estado_pedido,estado_pago,"
                   "personalizacion,cantidad_total,importe_total\n",
    "lineas_pedido.csv": "id_linea,id_pedido,sku,id_modelo,talla,cantidad,precio_unitario,importe_linea\n",
    "stock.csv": "sku,id_modelo,color,talla,activo,stock_disponible,fecha_corte\n",
}


class PruebaRegresion(PruebaCiclo):
    # Los seis fallos de la auditoria del 18/11/2026: cada prueba falla con el codigo de main a4249ea

    def ejecutar_main(self):
        salida = self.carpeta / "salida"
        with contextlib.redirect_stdout(io.StringIO()):
            codigo = main.ejecutar(self.carpeta, salida, con_graficos=False)
        return codigo, salida

    def leer_salida(self, salida, archivo):
        return pd.read_csv(salida / archivo, encoding="utf-8", dtype=str, keep_default_na=False)


class PruebasFallo1RegistroSinPermiso(PruebaRegresion):
    # Docker: el usuario nova no podia crear /app/logs y el dashboard se caia al abrirlo

    def test_el_ciclo_sigue_si_no_se_puede_escribir_el_registro(self):
        # Un archivo donde deberia ir la carpeta: mkdir falla con OSError, como sin permisos
        archivo = Path(self.otra.name) / "no_es_carpeta"
        archivo.write_text("", encoding="utf-8")
        estado = actualizacion.ciclo(self.carpeta, None, "prueba", archivo / "logs" / "registro_eventos.csv")
        self.assertEqual(estado["estado"], actualizacion.CORRECTO)
        self.assertIsNotNone(estado["publicado"])
        self.assertTrue(any("registro de eventos" in aviso for aviso in estado["avisos"]))

    def test_el_dockerfile_crea_logs_para_el_usuario_nova(self):
        texto = (CARPETA_PYTHON / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("mkdir -p /app/logs", texto)
        self.assertIn("chown nova:nova /app/logs", texto)
        # Tiene que ser antes de USER nova: despues ya no hay permiso para hacerlo
        self.assertLess(texto.index("chown nova:nova /app/logs"), texto.index("USER nova"))


class PruebasFallo2LineaSinPedido(PruebaRegresion):
    # Una linea con id_pedido vacio pasaba como valida y contaba como demanda sin pedido

    def setUp(self):
        super().setUp()
        self.cambiar("lineas_pedido.csv", "101,10,M1-41", "101,,M1-41")

    def test_la_linea_se_rechaza_por_la_regla_09(self):
        resultado = self.evaluar()
        r09 = self.de_la_regla(resultado, "09")
        self.assertEqual(r09["registro"].tolist(), ["101"])
        self.assertEqual(r09["columna"].tolist(), ["id_pedido"])
        self.assertEqual(r09["gravedad"].tolist(), ["recuperable"])
        self.assertIn("101", self.rechazadas(resultado, "lineas_pedido"))
        self.assertNotIn("101", set(resultado["validos"]["lineas_pedido"]["id_linea"]))
        self.assertFalse(resultado["bloqueado"])

    def test_los_pares_cuadran_en_todas_las_tablas(self):
        resultado = self.evaluar()
        tablas = analiticas.calcular_tablas(resultado["datos"], resultado["validos"])
        pedidos = tablas["pedidos_unicos"]
        pares_demanda = int(pedidos.loc[~pedidos["es_cancelado"], "pares"].sum())
        self.assertEqual(int(tablas["modelos_abc"]["pares"].sum()), pares_demanda)
        self.assertEqual(int(tablas["ventas_por_talla"]["pares"].sum()), pares_demanda)
        self.assertEqual(int(tablas["lineas_enriquecidas"]["id_pedido"].isna().sum()), 0)


class PruebasFallo3SinPersonalizacion(PruebaRegresion):
    # Sin la columna personalizacion, calidad.py y analiticas.py daban KeyError

    def setUp(self):
        super().setUp()
        self.escribir("pedidos.csv",
                      "id_pedido,referencia,id_cliente,fecha_pedido,tipo_pedido,estado_pedido,estado_pago,"
                      "cantidad_total,importe_total\n"
                      "10,P-1,1,2026-10-01 10:00:00,normal,confirmado,pagado,3,239.97\n"
                      "11,P-2,2,2026-11-02 12:30:00,custom,cancelado,reembolsado,2,239.80\n")

    def test_es_un_bloqueo_de_la_regla_01_con_mensaje_claro(self):
        resultado = self.evaluar()
        r01 = self.de_la_regla(resultado, "01")
        self.assertEqual(r01["gravedad"].tolist(), ["bloqueante"])
        self.assertIn("personalizacion", r01["detalle"].iloc[0])
        self.assertTrue(resultado["bloqueado"])

    def test_main_y_el_dashboard_no_se_caen(self):
        codigo, salida = self.ejecutar_main()
        self.assertEqual(codigo, 1)
        self.assertEqual(self.leer_salida(salida, "estado_ejecucion.csv")["estado"].iloc[0], "BLOQUEADO")
        estado = self.ciclo()
        self.assertEqual(estado["estado"], actualizacion.ERROR_CARGA)
        self.assertIn("faltan columnas obligatorias: personalizacion", estado["mensaje"])


class PruebasFallo4SinFechaDeCorte(PruebaRegresion):
    # Sin ninguna fecha_corte valida no se bloqueaba y despues fallaba con NaT

    def test_stock_sin_fechas_de_corte_bloquea(self):
        self.cambiar("stock.csv", "2026-11-09 19:00:00", "")
        resultado = self.evaluar()
        bloqueantes = resultado["incidencias"][resultado["incidencias"]["gravedad"] == calidad.BLOQUEANTE]
        self.assertEqual(bloqueantes["regla"].tolist(), ["12"])
        self.assertIn("ninguna fecha_corte", bloqueantes["detalle"].iloc[0])
        codigo, salida = self.ejecutar_main()
        self.assertEqual(codigo, 1)
        self.assertEqual(self.leer_salida(salida, "estado_ejecucion.csv")["estado"].iloc[0], "BLOQUEADO")
        self.assertEqual(self.ciclo()["estado"], actualizacion.DATOS_INVALIDOS)

    def test_los_cinco_csv_solo_con_cabecera_bloquean(self):
        for archivo, cabecera in CABECERAS.items():
            self.escribir(archivo, cabecera)
        codigo, salida = self.ejecutar_main()
        self.assertEqual(codigo, 1)
        self.assertEqual(self.leer_salida(salida, "estado_ejecucion.csv")["estado"].iloc[0], "BLOQUEADO")
        self.assertEqual(self.ciclo()["estado"], actualizacion.DATOS_INVALIDOS)


class PruebasFallo5EstadoSiSeCorta(PruebaRegresion):
    # Si main se cortaba, estado_ejecucion.csv seguia diciendo CORRECTO (de la ejecucion anterior)

    def test_una_ejecucion_cortada_queda_en_curso(self):
        codigo, salida = self.ejecutar_main()
        self.assertEqual(codigo, 0)
        self.assertEqual(self.leer_salida(salida, "estado_ejecucion.csv")["estado"].iloc[0], "CORRECTO")
        with mock.patch.object(main, "paso_estadistica", side_effect=RuntimeError("corte simulado")):
            with self.assertRaises(RuntimeError):
                self.ejecutar_main()
        self.assertEqual(self.leer_salida(salida, "estado_ejecucion.csv")["estado"].iloc[0], "EN CURSO")

    def test_una_ejecucion_completa_no_duplica_los_metadatos(self):
        _, salida = self.ejecutar_main()
        metadatos = self.leer_salida(salida, "metadatos_dataframes.csv")
        self.assertEqual((metadatos["archivo"] == "estado_ejecucion.csv").sum(), 1)


class PruebasFallo6IdsVaciosEnLaFase1(PruebaRegresion):
    # comprobaciones.py unia ids con join y fallaba con un id vacio (TypeError)

    def test_linea_sin_id_e_importe_mal_calculado(self):
        self.cambiar("lineas_pedido.csv", "100,10,M1-40,1,40,1,79.99,79.99", ",10,M1-40,1,40,1,79.99,1.00")
        datos, _ = pipeline.cargar_todos(self.carpeta)
        comprobacion = comprobaciones.comprobar_importes_y_cantidades(datos)
        self.assertEqual(comprobacion["resultado"], "ERROR")
        self.assertIn("<NA>", comprobacion["detalle"])
        codigo, _ = self.ejecutar_main()
        self.assertEqual(codigo, 0)

    def test_pedido_sin_id_y_sin_lineas(self):
        self.anadir("pedidos.csv", ",P-9,1,2026-10-03 10:00:00,normal,pendiente,pendiente,,1,10.00\n")
        datos, _ = pipeline.cargar_todos(self.carpeta)
        comprobacion = comprobaciones.comprobar_importes_y_cantidades(datos)
        self.assertEqual(comprobacion["resultado"], "ERROR")
        codigo, _ = self.ejecutar_main()
        self.assertEqual(codigo, 0)
