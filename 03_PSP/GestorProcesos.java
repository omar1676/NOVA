import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.concurrent.TimeUnit;

// Clase de apoyo del padre: lanza un proceso hijo, le pasa los datos por stdin
// y recoge su salida, sus errores y su codigo de salida
public class GestorProcesos {

    // Codigos propios para cuando el hijo no da codigo: no arranca o se cancela por tiempo
    public static final int NO_ARRANCA = -1;

    public static final int TIEMPO_AGOTADO = -2;

    // Clase Java del hijo y segundos que se le dejan
    private final String clase;
    private final int segundosMaximos;

    // Resultado del hijo: codigo, lineas de stdout y de stderr, y cuanto ha tardado
    private int codigoSalida;
    private final ArrayList<String> salida = new ArrayList<>();
    private final ArrayList<String> errores = new ArrayList<>();
    private String errorDeEscritura;
    private long milisegundos;

    // Constructor: el hijo que se va a lanzar y su tiempo maximo
    public GestorProcesos(String clase, int segundosMaximos) {
        this.clase = clase;
        this.segundosMaximos = segundosMaximos;
    }

    // Lanza el hijo, le envia la entrada y espera a que termine (o lo cancela)
    public void ejecutar(String entrada) throws InterruptedException {

        long inicio = System.currentTimeMillis();

        // El hijo se lanza con el mismo java y el mismo classpath que el padre
        String java = Path.of(System.getProperty("java.home"), "bin", "java").toString();
        String classpath = System.getProperty("java.class.path");

        ProcessBuilder pb = new ProcessBuilder(java, "-cp", classpath, clase);

        Process proceso;

        // Si el proceso no arranca, se guarda el motivo y no se sigue
        try {
            proceso = pb.start();

        } catch (IOException e) {
            errores.add("No se ha podido arrancar el proceso: " + e.getMessage());
            codigoSalida = NO_ARRANCA;
            milisegundos = System.currentTimeMillis() - inicio;
            return;
        }

        // Un hilo por tuberia (entrada, salida y error): si una se llena, el padre o el hijo
        // se quedan bloqueados. Es el mismo diseno que LanzadorValidacion
        Thread escritor = new Thread(() -> {
            try (BufferedWriter entradaDelHijo = proceso.outputWriter(StandardCharsets.UTF_8)) {
                entradaDelHijo.write(entrada);

            } catch (IOException e) {
                errorDeEscritura = e.getMessage();
            }
        });

        Thread lectorSalida = new Thread(() -> leerTodo(
                proceso.inputReader(StandardCharsets.UTF_8), salida));

        Thread lectorError = new Thread(() -> leerTodo(
                proceso.errorReader(StandardCharsets.UTF_8), errores));

        // Daemon: estos hilos no impiden que el programa termine
        escritor.setDaemon(true);
        lectorSalida.setDaemon(true);
        lectorError.setDaemon(true);

        escritor.start();
        lectorSalida.start();
        lectorError.start();

        // Espera con limite; si no termina, destroy() y, si sigue vivo, destroyForcibly()
        boolean termino = proceso.waitFor(segundosMaximos, TimeUnit.SECONDS);

        if (termino) {
            codigoSalida = proceso.exitValue();

        } else {
            proceso.destroy();

            if (!proceso.waitFor(1, TimeUnit.SECONDS)) {
                proceso.destroyForcibly();
                proceso.waitFor();
            }

            codigoSalida = TIEMPO_AGOTADO;
        }

        // Se espera a que los hilos acaben antes de leer las listas
        escritor.join(1000);
        lectorSalida.join(1000);
        lectorError.join(1000);

        milisegundos = System.currentTimeMillis() - inicio;
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

    // Getters: el padre los usa para ver como ha ido el hijo
    public String getClase() {
        return clase;
    }

    public int getSegundosMaximos() {
        return segundosMaximos;
    }

    public int getCodigoSalida() {
        return codigoSalida;
    }

    public ArrayList<String> getSalida() {
        return salida;
    }

    public ArrayList<String> getErrores() {
        return errores;
    }

    public String getErrorDeEscritura() {
        return errorDeEscritura;
    }

    public double getSegundos() {
        return milisegundos / 1000.0;
    }
}
