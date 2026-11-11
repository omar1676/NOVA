import java.io.File;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.concurrent.TimeUnit;

/**
 * NOVA Sneakers - PSP - Pruebas del procesador de pedidos Custom
 *
 * Lanza los programas DE VERDAD, como procesos, y comprueba lo que hacen.
 * No escribe en el repositorio: todo lo que genera va a una carpeta
 * temporal nueva.
 *
 * COMO SE EJECUTA (desde la carpeta psp, con todo compilado en "clases",
 * tambien el analizador de Alvaro; ver README)
 *   java -cp clases PruebasPsp
 *
 * Termina con codigo 0 si pasan todas y con 1 si falla alguna.
 */
public class PruebasPsp {

    // El CSV real que exporto el script 15 sobre la base de PRUEBA.
    private static final String CSV_CUSTOM40 = "datos/custom40_fabricacion_psp.csv";

    private static final String CABECERA =
            "referencia,sku,cliente,modelo,color,personalizacion,talla,cantidad";

    private static int superadas = 0;
    private static int fallidas = 0;

    // Carpeta temporal donde trabaja el coordinador en las pruebas.
    private static Path carpeta;

    // Lo que escribio el coordinador en la ultima prueba.
    private static String ultimaConsola = "";

    public static void main(String[] args) throws Exception {

        if (!Files.exists(Path.of(CSV_CUSTOM40))) {
            System.out.println("No encuentro " + CSV_CUSTOM40
                    + ". Ejecuta las pruebas desde la carpeta psp.");
            System.exit(1);
        }

        try {
            Class.forName("Psp.AnalizadorTallas");
        } catch (ClassNotFoundException e) {
            System.out.println("Falta el analizador de Alvaro (Psp.AnalizadorTallas)"
                    + " en el classpath. Compilalo antes (ver README).");
            System.exit(1);
        }

        carpeta = Files.createTempDirectory("nova_psp_pruebas_");
        System.out.println("Carpeta temporal de trabajo: " + carpeta.getFileName());
        System.out.println();

        String csvCustom40 = Files.readString(Path.of(CSV_CUSTOM40), StandardCharsets.UTF_8);
        Files.writeString(carpeta.resolve("custom40.csv"), csvCustom40, StandardCharsets.UTF_8);

        // =================================================================
        System.out.println("=== 1. Pedido Custom valido (exportacion real de CUSTOM-40) ===");
        int codigo = coordinador("custom40.csv");
        Path ficha40 = carpeta.resolve("salidas/ficha_taller_CUSTOM-40.txt");
        comprobar("01 CUSTOM-40 de principio a fin",
                codigo == 0 && ultimaConsola.contains("Resultado: CORRECTO")
                        && Files.exists(ficha40),
                "codigo " + codigo + ", " + ultimaLinea(ultimaConsola));

        // =================================================================
        System.out.println("=== 2. Varias tallas y cantidades (pedido de prueba, no real) ===");
        String csvVarias = CABECERA + "\n"
                + fila("PRUEBA-01", "SKU-R-44", "Rojo", 44, "3")
                + fila("PRUEBA-01", "SKU-R-38", "Rojo", 38, "2")
                + fila("PRUEBA-01", "SKU-R-39", "Rojo", 39, "3")
                + fila("PRUEBA-01", "SKU-R-40", "Rojo", 40, "5")
                + fila("PRUEBA-01", "SKU-R-41", "Rojo", 41, "5")
                + fila("PRUEBA-01", "SKU-R-42", "Rojo", 42, "6")
                + fila("PRUEBA-01", "SKU-R-43", "Rojo", 43, "4")
                + fila("PRUEBA-01", "SKU-R-45", "Rojo", 45, "2")
                + fila("PRUEBA-01", "SKU-R-46", "Rojo", 46, "2")
                + fila("PRUEBA-01", "SKU-N-42", "Negro", 42, "4")
                + fila("PRUEBA-01", "SKU-N-40", "Negro", 40, "2")
                + fila("PRUEBA-01", "SKU-R-42", "Rojo", 42, "2");   // talla repetida
        escribir("varias.csv", csvVarias);

        codigo = coordinador("varias.csv");
        String fichaVarias = leerSiExiste(carpeta.resolve("salidas/ficha_taller_PRUEBA-01.txt"));
        comprobar("02 Nueve tallas (38 a 46), dos colores y una talla repetida",
                codigo == 0
                        && fichaVarias.contains("Talla 38: 2 pares")
                        && fichaVarias.contains("Talla 40: 7 pares")
                        && fichaVarias.contains("Talla 42: 12 pares")
                        && fichaVarias.contains("Talla 46: 2 pares")
                        && fichaVarias.contains("TOTAL: 40 pares")
                        && contar(fichaVarias, "\n  Talla ") == 9,   // lineas "  Talla NN: ..."
                "codigo " + codigo + "; 9 tallas, la 42 suma 6 + 2 + 4 = 12, total 40");

        // =================================================================
        System.out.println("=== 3. Validacion correcta (el validador, solo) ===");
        GestorProcesos validador = new GestorProcesos("ValidadorPedidoCustom", 10);
        validador.ejecutar(csvCustom40);
        ArrayList<String> salidaValidador = validador.getSalida();
        comprobar("03 El validador acepta CUSTOM-40 y normaliza sus 4 lineas",
                validador.getCodigoSalida() == 0
                        && primera(salidaValidador).equals("OK;CUSTOM-40;4;40")
                        && salidaValidador.contains("CLIENTE;Club Atletico NOVA")
                        && salidaValidador.contains("PEDIDO;CUSTOM-40")
                        && salidaValidador.contains("LINEA;NOVA-4-40;NOVA Velocity;Rojo;40;10")
                        && salidaValidador.contains("LINEA;NOVA-4-43;NOVA Velocity;Rojo;43;10")
                        && salidaValidador.get(salidaValidador.size() - 1).equals("FIN"),
                "primera linea: " + primera(salidaValidador));

        // =================================================================
        System.out.println("=== 4. Agrupacion de tallas (validador -> analizador de Alvaro) ===");
        GestorProcesos validadorVarias = new GestorProcesos("ValidadorPedidoCustom", 10);
        validadorVarias.ejecutar(csvVarias);

        StringBuilder bloque = new StringBuilder();
        for (String linea : validadorVarias.getSalida()) {
            if (linea.startsWith("PEDIDO;") || linea.startsWith("LINEA;") || linea.equals("FIN")) {
                bloque.append(linea).append("\n");
            }
        }

        GestorProcesos analizador = new GestorProcesos("Psp.AnalizadorTallas", 10);
        analizador.ejecutar(bloque.toString());
        ArrayList<String> salidaAnalizador = analizador.getSalida();
        comprobar("04 Agrupa por variante y por talla",
                analizador.getCodigoSalida() == 0
                        && salidaAnalizador.contains("VARIANTE_TALLA;NOVA Velocity;Rojo;42;8")
                        && salidaAnalizador.contains("VARIANTE_TALLA;NOVA Velocity;Negro;42;4")
                        && salidaAnalizador.contains("TALLA;42;12")
                        && salidaAnalizador.contains("TALLA;38;2")
                        && salidaAnalizador.contains("TOTAL;40"),
                "Rojo 42 = 6 + 2 = 8; talla 42 = 12; total 40");

        // =================================================================
        System.out.println("=== 5. Generacion de la ficha auxiliar ===");
        String textoFicha40 = leerSiExiste(ficha40);
        String registro = leerSiExiste(carpeta.resolve("salidas/registro_psp.txt"));
        comprobar("05 Ficha de CUSTOM-40 con sus datos y registro del procesamiento",
                textoFicha40.contains("Pedido:           CUSTOM-40")
                        && textoFicha40.contains("Cliente:          Club Atletico NOVA")
                        && textoFicha40.contains("logo bordado y numeracion en el talon")
                        && textoFicha40.contains("NOVA Velocity")
                        && textoFicha40.contains("TOTAL: 40 pares")
                        && registro.contains("Resultado: CORRECTO"),
                "ficha de " + contar(textoFicha40, "\n") + " lineas y registro_psp.txt");

        // =================================================================
        System.out.println("=== 6. Comunicacion entre procesos ===");
        GestorProcesos eco = new GestorProcesos("HijoDePrueba", 10);
        eco.ejecutar("ECO\nuno\ndos;tres\ncuatro, con coma\n");
        comprobar("06a Lo que el padre envia por stdin vuelve igual por stdout",
                eco.getCodigoSalida() == 0
                        && eco.getSalida().size() == 4
                        && eco.getSalida().get(1).equals("uno")
                        && eco.getSalida().get(2).equals("dos;tres")
                        && eco.getSalida().get(3).equals("cuatro, con coma"),
                "recibido: " + eco.getSalida());

        comprobar("06b La personalizacion de 2 lineas cruza los tres procesos y llega a la ficha",
                fichaVarias.contains("  Dorsales del 1 al 40, escudo \"del club\"")
                        && fichaVarias.contains("  Segunda linea: nombre en el talon"),
                "las dos lineas, con la coma y las comillas");

        // =================================================================
        System.out.println("=== 7. Captura de stdout y stderr por separado ===");
        GestorProcesos dos = new GestorProcesos("HijoDePrueba", 10);
        dos.ejecutar("DOS_SALIDAS\n");
        comprobar("07 stdout y stderr llegan cada uno a su lista",
                dos.getCodigoSalida() == 0
                        && dos.getSalida().size() == 1
                        && dos.getSalida().get(0).equals("OK;salida")
                        && dos.getErrores().size() == 1
                        && dos.getErrores().get(0).equals("AVISO;esto va por stderr"),
                "stdout " + dos.getSalida() + " / stderr " + dos.getErrores());

        // =================================================================
        System.out.println("=== 8. Codigos de salida ===");
        GestorProcesos siete = new GestorProcesos("HijoDePrueba", 10);
        siete.ejecutar("CODIGO;7\n");
        comprobar("08a Se recoge el codigo exacto del hijo",
                siete.getCodigoSalida() == 7,
                "codigo " + siete.getCodigoSalida());

        GestorProcesos rechazo = new GestorProcesos("ValidadorPedidoCustom", 10);
        rechazo.ejecutar(CABECERA + "\n" + fila("MALO-00", "SKU-1", "Rojo", 40, "diez"));
        comprobar("08b El validador rechaza con 2, ERROR; por stderr y nada por stdout",
                rechazo.getCodigoSalida() == 2
                        && rechazo.getSalida().isEmpty()
                        && primera(rechazo.getErrores()).startsWith("ERROR;"),
                "codigo " + rechazo.getCodigoSalida() + ", " + rechazo.getErrores());

        // =================================================================
        System.out.println("=== 9. Fallo controlado de un proceso ===");
        GestorProcesos excepcion = new GestorProcesos("HijoDePrueba", 10);
        excepcion.ejecutar("EXCEPCION\n");
        comprobar("09a Un hijo que revienta con una excepcion",
                excepcion.getCodigoSalida() == 1
                        && String.join(" ", excepcion.getErrores()).contains("RuntimeException"),
                "codigo " + excepcion.getCodigoSalida() + ", " + primera(excepcion.getErrores()));

        GestorProcesos noExiste = new GestorProcesos("ClaseQueNoExiste", 10);
        noExiste.ejecutar("hola\n");
        comprobar("09b Un hijo que no se puede cargar",
                noExiste.getCodigoSalida() == 1
                        && String.join(" ", noExiste.getErrores()).contains("ClassNotFoundException"),
                "codigo " + noExiste.getCodigoSalida() + ", " + primera(noExiste.getErrores()));

        // =================================================================
        System.out.println("=== 10. Tiempo de espera agotado ===");
        GestorProcesos dormilon = new GestorProcesos("HijoDePrueba", 2);
        dormilon.ejecutar("DORMIR\n");
        comprobar("10 Un hijo que no termina se cancela a los 2 s",
                dormilon.getCodigoSalida() == GestorProcesos.TIEMPO_AGOTADO
                        && dormilon.getSegundos() < 6,
                "codigo " + dormilon.getCodigoSalida() + " (TIEMPO_AGOTADO) en "
                        + String.format("%.1f", dormilon.getSegundos()) + " s, en vez de 60");

        // =================================================================
        System.out.println("=== 11. Archivo inexistente ===");
        codigo = coordinador("no_existe.csv");
        comprobar("11 El padre avisa y no lanza ningun hijo",
                codigo == 1 && ultimaConsola.contains("No existe el archivo")
                        && !ultimaConsola.contains("Paso 1"),
                ultimaLinea(ultimaConsola));

        // =================================================================
        System.out.println("=== 12. Datos mal formados (el padre debe parar) ===");

        rechazado("12a Comilla sin cerrar", "MALO-01",
                CABECERA + "\nMALO-01,SKU-1,Club,NOVA Velocity,Rojo,\"logo sin cerrar,40,10\n",
                2, "mal formado");

        rechazado("12b Cabecera distinta", "MALO-02",
                "referencia,talla,cantidad\nMALO-02,40,10\n",
                2, "La cabecera no es la esperada");

        rechazado("12c Cantidad que no es un numero", "MALO-03",
                CABECERA + "\n" + fila("MALO-03", "SKU-1", "Rojo", 40, "diez"),
                2, "tiene que ser un numero entero");

        rechazado("12d Cantidad cero", "MALO-04",
                CABECERA + "\n" + fila("MALO-04", "SKU-1", "Rojo", 40, "0"),
                2, "mayor que cero");

        rechazado("12e Cantidad negativa", "MALO-05",
                CABECERA + "\n" + fila("MALO-05", "SKU-1", "Rojo", 40, "-5"),
                2, "mayor que cero");

        rechazado("12f Falta la talla", "MALO-06",
                CABECERA + "\nMALO-06,SKU-1,Club,NOVA Velocity,Rojo,logo,,10\n",
                2, "Falta la talla");

        rechazado("12g Falta el modelo", "MALO-07",
                CABECERA + "\nMALO-07,SKU-1,Club,,Rojo,logo,40,10\n",
                2, "Falta el modelo");

        rechazado("12h Solo la cabecera", "MALO-08",
                CABECERA + "\n",
                2, "solo trae la cabecera");

        rechazado("12i Registro con campos de menos", "MALO-09",
                CABECERA + "\nMALO-09,SKU-1,Club,NOVA Velocity,Rojo,40,10\n",
                2, "tiene 7 campos");

        rechazado("12j Dos pedidos en el mismo archivo", "MALO-10",
                CABECERA + "\n" + fila("MALO-10", "SKU-1", "Rojo", 40, "5")
                        + fila("OTRO-99", "SKU-2", "Rojo", 41, "5"),
                2, "un pedido por archivo");

        rechazado("12k Talla 99: la acepta el validador y la rechaza el analizador (paso 2)",
                "MALO-11",
                CABECERA + "\n" + fila("MALO-11", "SKU-1", "Rojo", 99, "5"),
                2, "Paso 2 Psp.AnalizadorTallas: codigo 2");

        rechazado("12l Archivo vacio", "MALO-12", "", 1, "El archivo esta vacio");

        // Un .json no se acepta: hoy solo hay exportacion en CSV.
        escribir("pedido.json", "{\"referencia\": \"MALO-13\"}");
        codigo = coordinador("pedido.json");
        comprobar("12m Formato que no es CSV",
                codigo == 1 && ultimaConsola.contains("Formato no admitido"),
                ultimaLinea(ultimaConsola));

        // =================================================================
        System.out.println();
        System.out.println("Pruebas superadas: " + superadas + " de " + (superadas + fallidas));

        if (fallidas > 0) {
            System.exit(1);
        }
    }

    // ---------------------------------------------------------------------
    // Ayudas de las pruebas
    // ---------------------------------------------------------------------

    /** Escribe [SUPERADA] o [FALLIDA] y lleva la cuenta. */
    private static void comprobar(String nombre, boolean bien, String detalle) {

        if (bien) {
            superadas++;
            System.out.println("[SUPERADA] " + nombre + " -> " + detalle);
        } else {
            fallidas++;
            System.out.println("[FALLIDA]  " + nombre + " -> " + detalle);
            System.out.println("           Ultima consola del coordinador:");
            System.out.println(ultimaConsola);
        }
    }

    /**
     * Prueba un CSV que el coordinador tiene que rechazar: comprueba el
     * codigo, el motivo y que NO se haya generado ninguna ficha.
     */
    private static void rechazado(String nombre, String referencia, String contenido,
                                  int codigoEsperado, String motivo) throws Exception {

        String archivo = referencia + ".csv";
        escribir(archivo, contenido);

        int codigo = coordinador(archivo);
        boolean sinFicha = !Files.exists(
                carpeta.resolve("salidas/ficha_taller_" + referencia + ".txt"));

        comprobar(nombre,
                codigo == codigoEsperado && ultimaConsola.contains(motivo) && sinFicha,
                "codigo " + codigo + ", sin ficha: " + motivoDelFallo(ultimaConsola));
    }

    /**
     * Lanza el coordinador como un proceso, en la carpeta temporal, y
     * devuelve su codigo de salida. Lo que escribe queda en ultimaConsola.
     *
     * Aqui no hace falta enviarle nada por stdin, asi que basta con mandar su
     * salida a un archivo (redirectOutput) y esperar: no puede bloquearse.
     */
    private static int coordinador(String archivo) throws Exception {

        String java = Path.of(System.getProperty("java.home"), "bin", "java").toString();

        ProcessBuilder pb = new ProcessBuilder(java, "-cp", classpathAbsoluto(),
                "ProcesadorPedidosCustom", archivo);

        pb.directory(carpeta.toFile());          // trabaja en la carpeta temporal
        pb.redirectErrorStream(true);            // stdout y stderr juntos

        File consola = carpeta.resolve("consola.txt").toFile();
        pb.redirectOutput(consola);

        Process proceso = pb.start();

        if (!proceso.waitFor(60, TimeUnit.SECONDS)) {
            proceso.destroyForcibly();
            ultimaConsola = "(el coordinador no termino en 60 s)";
            return -99;
        }

        // El coordinador escribe con el juego de caracteres por defecto.
        ultimaConsola = Files.readString(consola.toPath(), Charset.defaultCharset());
        return proceso.exitValue();
    }

    /**
     * El classpath con rutas absolutas. Hace falta porque el coordinador se
     * lanza en otra carpeta y una ruta relativa como "clases" ya no valdria.
     */
    private static String classpathAbsoluto() {

        String[] partes = System.getProperty("java.class.path").split(File.pathSeparator);
        StringBuilder classpath = new StringBuilder();

        for (String parte : partes) {
            if (classpath.length() > 0) {
                classpath.append(File.pathSeparator);
            }
            classpath.append(Path.of(parte).toAbsolutePath());
        }
        return classpath.toString();
    }

    /** Una fila del CSV de prueba, con cliente, modelo y personalizacion fijos. */
    private static String fila(String referencia, String sku, String color,
                               int talla, String cantidad) {

        return referencia + "," + sku + ",Club de Prueba,NOVA Velocity," + color
                + ",\"Dorsales del 1 al 40, escudo \"\"del club\"\"\n"
                + "Segunda linea: nombre en el talon\"," + talla + "," + cantidad + "\n";
    }

    private static void escribir(String nombre, String contenido) throws Exception {
        Files.writeString(carpeta.resolve(nombre), contenido, StandardCharsets.UTF_8);
    }

    private static String leerSiExiste(Path archivo) throws Exception {

        if (!Files.exists(archivo)) {
            return "";
        }
        return Files.readString(archivo, StandardCharsets.UTF_8);
    }

    /** Cuantas veces aparece un trozo de texto. */
    private static int contar(String texto, String trozo) {

        int veces = 0;
        int desde = texto.indexOf(trozo);

        while (desde != -1) {
            veces++;
            desde = texto.indexOf(trozo, desde + trozo.length());
        }
        return veces;
    }

    /** La linea "Resultado: ..." de la consola del coordinador. */
    private static String ultimaLinea(String consola) {

        for (String linea : consola.split("\r?\n")) {
            if (linea.startsWith("Resultado:")) {
                return linea;
            }
        }
        return "(sin linea de resultado)";
    }

    /** El motivo que dio el hijo (la linea ERROR;...) o, si no hay, el resultado. */
    private static String motivoDelFallo(String consola) {

        for (String linea : consola.split("\r?\n")) {
            if (linea.trim().startsWith("ERROR;")) {
                return linea.trim();
            }
        }
        return ultimaLinea(consola);
    }

    private static String primera(ArrayList<String> lineas) {

        if (lineas.isEmpty()) {
            return "(nada)";
        }
        return lineas.get(0);
    }
}
