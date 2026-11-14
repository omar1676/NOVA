import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.concurrent.TimeUnit;

public class LanzadorValidacion {

    private static final int SEGUNDOS_DE_ESPERA = 10;

    public static void main(String[] args) throws Exception {

        if (args.length != 1) {
            System.err.println("Uso: java LanzadorValidacion <ruta del CSV>");
            System.exit(1);
        }

        Path rutaCsv = Path.of(args[0]);

        if (!Files.exists(rutaCsv)) {
            System.err.println("No existe el archivo: " + rutaCsv);
            System.exit(1);
        }

        String contenidoCsv = Files.readString(rutaCsv, StandardCharsets.UTF_8);

        System.out.println("Archivo leido: " + rutaCsv);
        System.out.println("Bytes del archivo: " + contenidoCsv.length());
        System.out.println();

        System.out.println("--- Paso 1: validar el pedido");

        String respuesta = ejecutarHijo("ValidadorPedidoCustom", contenidoCsv, true);

        if (respuesta == null || !respuesta.startsWith("OK;")) {
            System.err.println("Respuesta no valida del validador: " + respuesta);
            System.exit(1);
        }

        String[] partes = respuesta.split(";");

        if (partes.length != 4) {
            System.err.println("El validador tenia que devolver 4 campos y ha"
                    + " devuelto " + partes.length);
            System.exit(1);
        }

        String referencia = partes[1];
        int lineasDePedido = Integer.parseInt(partes[2]);
        int pares = Integer.parseInt(partes[3]);

        System.out.println("Pedido validado: " + referencia);
        System.out.println("Lineas de pedido: " + lineasDePedido);
        System.out.println("Pares en total: " + pares);
        System.out.println();

        System.out.println("--- Paso 2: resumen por tallas");

        ejecutarHijo("AnalizadorTallas", contenidoCsv, false);

        System.out.println();
        System.out.println("Procesamiento auxiliar terminado para " + referencia);
    }

    private static String ejecutarHijo(String clase,
                                       String contenidoCsv,
                                       boolean unaSolaLinea) throws Exception {

        String java = Path.of(System.getProperty("java.home"), "bin", "java").toString();
        String classpath = System.getProperty("java.class.path");

        ProcessBuilder pb = new ProcessBuilder(java, "-cp", classpath, clase);

        Process proceso = pb.start();

        String[] errorDeEscritura = new String[1];

        Thread escritor = new Thread(() -> {
            try (BufferedWriter entradaDelHijo =
                         proceso.outputWriter(StandardCharsets.UTF_8)) {

                entradaDelHijo.write(contenidoCsv);

            } catch (IOException e) {
                errorDeEscritura[0] = e.getMessage();
            }
        });

        ArrayList<String> salida = new ArrayList<>();
        ArrayList<String> errores = new ArrayList<>();

        Thread lectorSalida = new Thread(() -> leerTodo(
                proceso.inputReader(StandardCharsets.UTF_8), salida));

        Thread lectorError = new Thread(() -> leerTodo(
                proceso.errorReader(StandardCharsets.UTF_8), errores));

        escritor.setDaemon(true);
        lectorSalida.setDaemon(true);
        lectorError.setDaemon(true);

        escritor.start();
        lectorSalida.start();
        lectorError.start();

        boolean termino = proceso.waitFor(SEGUNDOS_DE_ESPERA, TimeUnit.SECONDS);

        if (!termino) {
            System.err.println("El proceso " + clase + " no ha terminado en "
                    + SEGUNDOS_DE_ESPERA + " segundos. Se cancela.");

            proceso.destroy();

            if (!proceso.waitFor(1, TimeUnit.SECONDS)) {
                proceso.destroyForcibly();
                proceso.waitFor();
            }

            escritor.join(1000);
            lectorSalida.join(1000);
            lectorError.join(1000);

            System.exit(1);
        }

        escritor.join(1000);
        lectorSalida.join(1000);
        lectorError.join(1000);

        int codigoSalida = proceso.exitValue();

        System.out.println("(" + clase + " termino con codigo " + codigoSalida + ")");

        if (codigoSalida != 0) {
            System.err.println("El proceso " + clase + " ha terminado con error.");

            for (String linea : errores) {
                System.err.println(linea);
            }

            System.exit(1);
        }

        if (errorDeEscritura[0] != null) {
            System.err.println("El proceso " + clase + " termino con codigo 0,"
                    + " pero no se le pudieron enviar todos los datos: "
                    + errorDeEscritura[0]);
            System.err.println("Su respuesta no es fiable porque solo ha leido"
                    + " parte del pedido.");

            System.exit(1);
        }

        String primeraLinea = null;

        if (unaSolaLinea) {
            if (!salida.isEmpty()) {
                primeraLinea = salida.get(0);
            }
        } else {
            for (String linea : salida) {
                System.out.println(linea);
            }
        }

        return primeraLinea;
    }

    private static void leerTodo(BufferedReader lector, ArrayList<String> destino) {

        try (BufferedReader cerrarAlAcabar = lector) {

            String linea;

            while ((linea = cerrarAlAcabar.readLine()) != null) {
                destino.add(linea);
            }

        } catch (IOException e) {
        }
    }
}
