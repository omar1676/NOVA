import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.concurrent.TimeUnit;

/**
 * NOVA Sneakers - PSP - Lanzar un proceso hijo y recoger su resultado
 * (tarea PSP-05 del reparto: ProcessBuilder, stdin/stdout, codigos y tiempos)
 *
 * QUE HACE
 *   Cada objeto se encarga de UN proceso hijo:
 *     1. Lo lanza con ProcessBuilder, en otra maquina virtual de Java.
 *     2. Le envia los datos por su entrada estandar (stdin) y la cierra.
 *     3. Recoge POR SEPARADO su salida estandar (stdout) y su salida de
 *        error (stderr), cada una en su lista.
 *     4. Espera a que termine (waitFor), como mucho segundosMaximos. Si no
 *        termina a tiempo, lo cancela.
 *     5. Guarda el codigo de salida y lo que ha tardado.
 *
 *   No decide si el resultado es bueno o malo. Eso lo hace el proceso padre,
 *   ProcesadorPedidosCustom, que es quien sabe que esperaba de cada hijo.
 *
 * DE DONDE SALE
 *   Es el metodo ejecutarHijo() de LanzadorValidacion, pasado a una clase
 *   para que lo pueda usar el coordinador. Los tres hilos y el orden
 *   "primero esperar, despues leer" son los mismos, y alli estan explicados
 *   con lo que se midio. La diferencia es que aquel terminaba el programa
 *   con System.exit() al primer fallo, y este GUARDA el resultado, para que
 *   el padre pueda decidir y escribir siempre el resumen final.
 *
 * POR QUE TRES HILOS (resumen)
 *   Las tres tuberias (entrada, salida y error) tienen un tamano limitado.
 *   Si se llena una, quien escribe se queda bloqueado. Con un hilo en cada
 *   una, ninguna se llena, y el hilo principal queda libre para hacer
 *   waitFor() con limite de tiempo y cancelar al hijo si hace falta.
 *   Cada hilo trabaja con SU lista y el principal no las mira hasta despues
 *   de join(): por eso no hace falta sincronizar nada.
 *
 * USO
 *   GestorProcesos validador = new GestorProcesos("ValidadorPedidoCustom", 10);
 *   validador.ejecutar(contenidoCsv);
 *   int codigo = validador.getCodigoSalida();
 */
public class GestorProcesos {

    /** El hijo no se ha podido arrancar, asi que no tiene codigo de salida. */
    public static final int NO_ARRANCA = -1;

    /** El hijo no ha terminado a tiempo y se ha cancelado. */
    public static final int TIEMPO_AGOTADO = -2;

    // Que se lanza y cuanto se espera.
    private final String clase;
    private final int segundosMaximos;

    // El resultado de la ejecucion.
    private int codigoSalida;
    private final ArrayList<String> salida = new ArrayList<>();
    private final ArrayList<String> errores = new ArrayList<>();
    private String errorDeEscritura;     // null si se le envio todo
    private long milisegundos;

    public GestorProcesos(String clase, int segundosMaximos) {
        this.clase = clase;
        this.segundosMaximos = segundosMaximos;
    }

    /**
     * Lanza el hijo, le envia "entrada" por su stdin y espera su resultado.
     * Al volver, el resultado queda en los getters.
     */
    public void ejecutar(String entrada) throws InterruptedException {

        long inicio = System.currentTimeMillis();

        /*
         * El hijo es "java -cp <classpath> <clase>", con el mismo java y el
         * mismo classpath que este programa, como en los ejemplos del
         * profesor. Asi encuentra sus clases sin configurar nada.
         */
        String java = Path.of(System.getProperty("java.home"), "bin", "java").toString();
        String classpath = System.getProperty("java.class.path");

        ProcessBuilder pb = new ProcessBuilder(java, "-cp", classpath, clase);

        Process proceso;

        try {
            proceso = pb.start();

        } catch (IOException e) {
            // Ni siquiera ha arrancado: no hay salida ni codigo que recoger.
            errores.add("No se ha podido arrancar el proceso: " + e.getMessage());
            codigoSalida = NO_ARRANCA;
            milisegundos = System.currentTimeMillis() - inicio;
            return;
        }

        /*
         * Hilo 1: escribe los datos en la entrada del hijo y la CIERRA.
         * Cerrarla es lo que le dice al hijo que ya no llegan mas datos.
         * Si la escritura falla, guardamos el motivo: el padre lo mirara.
         */
        Thread escritor = new Thread(() -> {
            try (BufferedWriter entradaDelHijo = proceso.outputWriter(StandardCharsets.UTF_8)) {
                entradaDelHijo.write(entrada);

            } catch (IOException e) {
                errorDeEscritura = e.getMessage();
            }
        });

        // Hilos 2 y 3: vacian la salida y la salida de error del hijo.
        Thread lectorSalida = new Thread(() -> leerTodo(
                proceso.inputReader(StandardCharsets.UTF_8), salida));

        Thread lectorError = new Thread(() -> leerTodo(
                proceso.errorReader(StandardCharsets.UTF_8), errores));

        // Demonios: si alguno se quedara bloqueado, no impide que el
        // programa termine.
        escritor.setDaemon(true);
        lectorSalida.setDaemon(true);
        lectorError.setDaemon(true);

        escritor.start();
        lectorSalida.start();
        lectorError.start();

        /*
         * PRIMERO esperamos, con limite de tiempo, y DESPUES leemos. Asi, pase
         * lo que pase dentro del hijo, recuperamos el control a los
         * segundosMaximos. (Ejemplo del profesor LanzadorProcesoFinal2.java.)
         */
        boolean termino = proceso.waitFor(segundosMaximos, TimeUnit.SECONDS);

        if (termino) {
            codigoSalida = proceso.exitValue();

        } else {
            // destroy() le pide que termine; destroyForcibly() lo mata.
            proceso.destroy();

            if (!proceso.waitFor(1, TimeUnit.SECONDS)) {
                proceso.destroyForcibly();
                proceso.waitFor();
            }

            codigoSalida = TIEMPO_AGOTADO;
        }

        /*
         * El hijo ya no existe y sus tuberias estan cerradas, asi que los
         * hilos acaban enseguida. Esperamos a que terminen de guardar lo que
         * quedara por leer, para no quedarnos con media respuesta.
         */
        escritor.join(1000);
        lectorSalida.join(1000);
        lectorError.join(1000);

        milisegundos = System.currentTimeMillis() - inicio;
    }

    /**
     * Lee un flujo entero, linea a linea, y lo guarda en una lista.
     * Lo usan los dos hilos lectores.
     */
    private static void leerTodo(BufferedReader lector, ArrayList<String> destino) {

        try (BufferedReader cerrarAlAcabar = lector) {

            String linea;

            while ((linea = cerrarAlAcabar.readLine()) != null) {
                destino.add(linea);
            }

        } catch (IOException e) {
            // La tuberia se ha cerrado porque el hijo ha terminado o lo hemos
            // cancelado. Nos quedamos con lo que hayamos leido.
        }
    }

    // --- Lo que el padre consulta despues de ejecutar() -------------------

    public String getClase() {
        return clase;
    }

    public int getSegundosMaximos() {
        return segundosMaximos;
    }

    /** 0 si fue bien, el codigo del hijo, NO_ARRANCA o TIEMPO_AGOTADO. */
    public int getCodigoSalida() {
        return codigoSalida;
    }

    /** Lo que el hijo escribio en su stdout, linea a linea. */
    public ArrayList<String> getSalida() {
        return salida;
    }

    /** Lo que el hijo escribio en su stderr, linea a linea. */
    public ArrayList<String> getErrores() {
        return errores;
    }

    /** null si se le enviaron todos los datos; si no, el motivo. */
    public String getErrorDeEscritura() {
        return errorDeEscritura;
    }

    public double getSegundos() {
        return milisegundos / 1000.0;
    }
}
