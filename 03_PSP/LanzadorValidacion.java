import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.concurrent.TimeUnit;

// Version anterior del padre (8 de noviembre): lanza el validador y el AnalizadorTallas
// de esta carpeta. El coordinador actual es ProcesadorPedidosCustom
public class LanzadorValidacion {

    // Tiempo maximo que se espera a cada hijo
    private static final int SEGUNDOS_DE_ESPERA = 10;

    // Lee el CSV indicado y lanza los dos hijos, uno detras de otro
    public static void main(String[] args) throws Exception {

        // Se comprueba el argumento y que el archivo existe
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

        // Paso 1: el validador; de su respuesta solo se usa la primera linea
        System.out.println("--- Paso 1: validar el pedido");

        String respuesta = ejecutarHijo("ValidadorPedidoCustom", contenidoCsv, true);

        if (respuesta == null || !respuesta.startsWith("OK;")) {
            System.err.println("Respuesta no valida del validador: " + respuesta);
            System.exit(1);
        }

        // La respuesta es OK;referencia;lineas;pares
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

        // Paso 2: el analizador escribe directamente el resumen por tallas
        System.out.println("--- Paso 2: resumen por tallas");

        ejecutarHijo("AnalizadorTallas", contenidoCsv, false);

        System.out.println();
        System.out.println("Procesamiento auxiliar terminado para " + referencia);
    }

    // Lanza un hijo, le pasa el CSV por stdin y devuelve la primera linea de su salida.
    // Si unaSolaLinea es false, escribe toda su salida en pantalla y devuelve null
    private static String ejecutarHijo(String clase,
                                       String contenidoCsv,
                                       boolean unaSolaLinea) throws Exception {

        // Mismo java y mismo classpath que el padre
        String java = Path.of(System.getProperty("java.home"), "bin", "java").toString();
        String classpath = System.getProperty("java.class.path");

        ProcessBuilder pb = new ProcessBuilder(java, "-cp", classpath, clase);

        Process proceso = pb.start();

        // Array de una posicion: dentro de la lambda no se puede cambiar una variable local
        String[] errorDeEscritura = new String[1];

        // Un hilo por tuberia (entrada, salida y error) para que ninguna se llene y bloquee
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

        // Espera con limite; si el hijo no termina, se cancela y el programa acaba con error
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

        // Si el codigo no es 0, se muestran los errores del hijo y se para
        int codigoSalida = proceso.exitValue();

        System.out.println("(" + clase + " termino con codigo " + codigoSalida + ")");

        if (codigoSalida != 0) {
            System.err.println("El proceso " + clase + " ha terminado con error.");

            for (String linea : errores) {
                System.err.println(linea);
            }

            System.exit(1);
        }

        // Si no se pudo enviar todo el CSV, la respuesta del hijo no vale
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

    // Lee todas las lineas de una tuberia y las guarda en la lista
    private static void leerTodo(BufferedReader lector, ArrayList<String> destino) {

        try (BufferedReader cerrarAlAcabar = lector) {

            String linea;

            while ((linea = cerrarAlAcabar.readLine()) != null) {
                destino.add(linea);
            }

        } catch (IOException e) {
            // Si la tuberia se cierra de golpe, simplemente se deja de leer
        }
    }
}
