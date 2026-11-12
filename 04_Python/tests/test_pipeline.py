"""
Pruebas de la lectura de CSV y de las comprobaciones iniciales (fase 1).

Cada prueba escribe sus propios CSV pequenos en una carpeta temporal que se
borra al terminar. NUNCA usan entrada_acc/ ni la base de datos: son datos
de prueba inventados, no datos reales.

Se ejecutan desde la carpeta 04_Python:
    python -m unittest discover -s tests -v
"""
import hashlib
import tempfile
import unittest
from pathlib import Path

import pandas as pd

import comprobaciones
import pipeline

# Cinco CSV pequenos y coherentes entre si. Llevan tildes y enes para
# comprobar que el UTF-8 se lee bien, y comas dentro de comillas.
VALIDOS = {
    "clientes.csv": (
        "id_cliente,nombre,tipo,correo,telefono,activo\n"
        "1,Nuria Muñoz,particular,nuria@example.com,,true\n"
        "2,Club Atlético Prueba,empresa,club@example.com,600000000,true\n"
    ),
    "modelos.csv": (
        "id_modelo,nombre_modelo,descripcion,precio_base,activo\n"
        '1,Modelo Uno,"Diseñada para correr, ligera",79.99,true\n'
        "2,Modelo Dos,,119.90,false\n"
    ),
    "pedidos.csv": (
        "id_pedido,referencia,id_cliente,fecha_pedido,tipo_pedido,estado_pedido,estado_pago,"
        "personalizacion,cantidad_total,importe_total\n"
        "10,P-1,1,2026-10-01 10:00:00,normal,confirmado,pagado,,3,239.97\n"
        '11,P-2,2,2026-11-02 12:30:00,custom,cancelado,reembolsado,"Logo, dorsal",2,239.80\n'
    ),
    "lineas_pedido.csv": (
        "id_linea,id_pedido,sku,id_modelo,talla,cantidad,precio_unitario,importe_linea\n"
        "100,10,M1-40,1,40,1,79.99,79.99\n"
        "101,10,M1-41,1,41,2,79.99,159.98\n"
        "102,11,M2-42,2,42,2,119.90,239.80\n"
    ),
    "stock.csv": (
        "sku,id_modelo,color,talla,activo,stock_disponible,fecha_corte\n"
        "M1-40,1,Blanco,40,true,5,2026-11-09 19:00:00\n"
        "M1-41,1,Blanco,41,true,0,2026-11-09 19:00:00\n"
        "M2-42,2,Negro,42,true,12,2026-11-09 19:00:00\n"
    ),
}


class PruebaConCarpeta(unittest.TestCase):
    """Base: una carpeta temporal con los cinco CSV validos."""

    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.carpeta = Path(self.temporal.name)
        for archivo, texto in VALIDOS.items():
            self.escribir(archivo, texto)

    def tearDown(self):
        self.temporal.cleanup()

    def escribir(self, archivo, texto, codificacion="utf-8"):
        # newline="" para que Windows no cambie los saltos de linea
        with open(self.carpeta / archivo, "w", encoding=codificacion, newline="") as f:
            f.write(texto)
        return self.carpeta / archivo


class PruebasLeerCsv(PruebaConCarpeta):

    def test_csv_valido(self):
        clientes, avisos = pipeline.leer_csv(self.carpeta / "clientes.csv", "clientes")
        self.assertEqual(len(clientes), 2)
        self.assertEqual(avisos, [])
        self.assertEqual(clientes.loc[0, "nombre"], "Nuria Muñoz")          # UTF-8 bien leido
        self.assertEqual(clientes.loc[0, "id_cliente"], "1")                # el id sigue siendo texto
        self.assertTrue(pd.api.types.is_string_dtype(clientes["id_cliente"]))
        self.assertTrue(pd.isna(clientes.loc[0, "telefono"]))               # celda vacia = nulo
        self.assertEqual(clientes["activo"].tolist(), [True, True])

    def test_tipos_convertidos(self):
        lineas, avisos = pipeline.leer_csv(self.carpeta / "lineas_pedido.csv", "lineas_pedido")
        pedidos, _ = pipeline.leer_csv(self.carpeta / "pedidos.csv", "pedidos")
        self.assertEqual(avisos, [])
        self.assertEqual(lineas["cantidad"].sum(), 5)
        self.assertAlmostEqual(lineas["importe_linea"].sum(), 479.77)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(pedidos["fecha_pedido"]))
        self.assertEqual(pedidos.loc[1, "personalizacion"], "Logo, dorsal")  # coma dentro de comillas

    def test_csv_ausente(self):
        with self.assertRaises(pipeline.ErrorDatos) as contexto:
            pipeline.leer_csv(self.carpeta / "no_existe.csv", "clientes")
        self.assertIn("No existe", str(contexto.exception))

    def test_csv_vacio(self):
        ruta = self.escribir("clientes.csv", "")
        with self.assertRaises(pipeline.ErrorDatos) as contexto:
            pipeline.leer_csv(ruta, "clientes")
        self.assertIn("vacío", str(contexto.exception))

    def test_csv_solo_cabecera(self):
        ruta = self.escribir("clientes.csv", "id_cliente,nombre,tipo,correo,telefono,activo\n")
        clientes, avisos = pipeline.leer_csv(ruta, "clientes")
        self.assertEqual(len(clientes), 0)
        self.assertIn("solo tiene la cabecera", avisos[0])

    def test_columna_obligatoria_ausente(self):
        ruta = self.escribir("pedidos.csv", "id_pedido,referencia,id_cliente\n10,P-1,1\n")
        with self.assertRaises(pipeline.ErrorDatos) as contexto:
            pipeline.leer_csv(ruta, "pedidos")
        self.assertIn("fecha_pedido", str(contexto.exception))
        self.assertIn("importe_total", str(contexto.exception))

    def test_separador_punto_y_coma(self):
        ruta = self.escribir("clientes.csv", "id_cliente;nombre;tipo;correo;telefono;activo\n1;Ana;particular;a@example.com;;true\n")
        with self.assertRaises(pipeline.ErrorDatos) as contexto:
            pipeline.leer_csv(ruta, "clientes")
        self.assertIn("separador", str(contexto.exception))

    def test_datos_mal_formados(self):
        ruta = self.escribir("lineas_pedido.csv", (
            "id_linea,id_pedido,sku,id_modelo,talla,cantidad,precio_unitario,importe_linea\n"
            "100,10,M1-40,1,40,dos,79.99,79.99\n"        # cantidad que no es un numero
            "101,10,M1-41,1,41.5,2,79.99,159.98\n"       # talla que no es entera
            "102,11,M2-42,2,42,2,\"119,90\",239.80\n"    # decimal con coma
        ))
        lineas, avisos = pipeline.leer_csv(ruta, "lineas_pedido")
        self.assertEqual(len(lineas), 3)                 # no se pierde ninguna fila
        self.assertEqual(len(avisos), 3)
        self.assertTrue(any("fila 1, columna cantidad: 'dos'" in aviso for aviso in avisos))
        self.assertTrue(any("fila 2, columna talla: '41.5'" in aviso for aviso in avisos))
        self.assertTrue(any("fila 3, columna precio_unitario: '119,90'" in aviso for aviso in avisos))
        self.assertTrue(pd.isna(lineas.loc[0, "cantidad"]))
        self.assertTrue(pd.isna(lineas.loc[1, "talla"]))
        self.assertTrue(pd.isna(lineas.loc[2, "precio_unitario"]))
        self.assertEqual(lineas.loc[1, "cantidad"], 2)   # el resto de la fila se conserva

    def test_fecha_y_logico_mal_formados(self):
        ruta = self.escribir("stock.csv", (
            "sku,id_modelo,color,talla,activo,stock_disponible,fecha_corte\n"
            "M1-40,1,Blanco,40,si,5,2026-02-30 19:00:00\n"   # "si" y 30 de febrero
        ))
        stock, avisos = pipeline.leer_csv(ruta, "stock")
        self.assertEqual(len(avisos), 2)
        self.assertTrue(pd.isna(stock.loc[0, "activo"]))
        self.assertTrue(pd.isna(stock.loc[0, "fecha_corte"]))

    def test_csv_corrupto(self):
        cabecera = "id_cliente,nombre,tipo,correo,telefono,activo\n"
        corruptos = {
            "valor de más en la primera fila": cabecera + "1,Ana,particular,a@example.com,,true,de_mas\n",
            "valor de más en otra fila": cabecera + "1,Ana,particular,a@example.com,,true\n"
                                                    "2,Eva,particular,e@example.com,,true,de_mas\n",
            "comillas sin cerrar": cabecera + '1,"Ana,particular,a@example.com,,true\n',
        }
        for caso, texto in corruptos.items():
            with self.subTest(caso=caso):
                ruta = self.escribir("clientes.csv", texto)
                with self.assertRaises(pipeline.ErrorDatos) as contexto:
                    pipeline.leer_csv(ruta, "clientes")
                self.assertIn("no es un CSV correcto", str(contexto.exception))

    def test_no_es_utf8(self):
        ruta = self.escribir("clientes.csv", VALIDOS["clientes.csv"], codificacion="latin-1")
        with self.assertRaises(pipeline.ErrorDatos) as contexto:
            pipeline.leer_csv(ruta, "clientes")
        self.assertIn("UTF-8", str(contexto.exception))

    def test_no_modifica_el_original(self):
        ruta = self.carpeta / "pedidos.csv"
        antes = hashlib.sha256(ruta.read_bytes()).hexdigest()
        fecha_antes = ruta.stat().st_mtime
        pipeline.leer_csv(ruta, "pedidos")
        self.assertEqual(hashlib.sha256(ruta.read_bytes()).hexdigest(), antes)
        self.assertEqual(ruta.stat().st_mtime, fecha_antes)


class PruebasCargarTodos(PruebaConCarpeta):

    def test_cinco_validos(self):
        datos, avisos = pipeline.cargar_todos(self.carpeta)
        self.assertEqual(sorted(datos), ["clientes", "lineas_pedido", "modelos", "pedidos", "stock"])
        self.assertEqual(avisos, [])
        manifiesto = pipeline.manifiesto(self.carpeta, datos)
        self.assertEqual(manifiesto["filas"].tolist(), [2, 2, 2, 3, 3])

    def test_falta_un_archivo(self):
        (self.carpeta / "stock.csv").unlink()
        with self.assertRaises(pipeline.ErrorDatos) as contexto:
            pipeline.cargar_todos(self.carpeta)
        self.assertIn("stock.csv", str(contexto.exception))

    def test_informa_de_todos_los_errores(self):
        (self.carpeta / "stock.csv").unlink()
        self.escribir("clientes.csv", "")
        with self.assertRaises(pipeline.ErrorDatos) as contexto:
            pipeline.cargar_todos(self.carpeta)
        self.assertIn("stock.csv", str(contexto.exception))
        self.assertIn("clientes.csv", str(contexto.exception))


class PruebasComprobaciones(PruebaConCarpeta):

    def resultados(self):
        datos, avisos = pipeline.cargar_todos(self.carpeta)
        return {r["comprobacion"]: r for r in comprobaciones.comprobar_todo(datos, avisos)}

    def test_datos_coherentes(self):
        resultados = self.resultados()
        errores = [r for r in resultados.values() if r["resultado"] == "ERROR"]
        self.assertEqual(errores, [])
        self.assertEqual(resultados["Periodo de los pedidos"]["resultado"], "OK")   # octubre y noviembre

    def test_linea_huerfana(self):
        self.escribir("lineas_pedido.csv", VALIDOS["lineas_pedido.csv"] + "103,99,M1-40,1,40,1,79.99,79.99\n")
        resultado = self.resultados()["Relaciones entre tablas"]
        self.assertEqual(resultado["resultado"], "ERROR")
        self.assertIn("99", resultado["detalle"])

    def test_id_duplicado(self):
        self.escribir("clientes.csv", VALIDOS["clientes.csv"] + "2,Otro,particular,otro@example.com,,true\n")
        resultado = self.resultados()["Claves únicas"]
        self.assertEqual(resultado["resultado"], "ERROR")
        self.assertIn("clientes.id_cliente: 2", resultado["detalle"])

    def test_total_que_no_cuadra(self):
        self.escribir("pedidos.csv", VALIDOS["pedidos.csv"].replace("3,239.97", "3,250.00"))
        resultado = self.resultados()["Importes y cantidades"]
        self.assertEqual(resultado["resultado"], "ERROR")
        self.assertIn("10", resultado["detalle"])

    def test_texto_mal_codificado(self):
        # "Muñoz" guardado en UTF-8 despues de haberlo leido mal: "MuÃ±oz"
        self.escribir("clientes.csv", VALIDOS["clientes.csv"].replace("Muñoz", "MuÃ±oz"))
        resultado = self.resultados()["Codificación UTF-8"]
        self.assertEqual(resultado["resultado"], "ERROR")


if __name__ == "__main__":
    unittest.main()
