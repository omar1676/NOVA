import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.concurrent.TimeUnit;

public class GestorProcesos {

    public static final int NO_ARRANCA = -1;

    public static final int TIEMPO_AGOTADO = -2;

    private final String clase;
    private final int segundosMaximos;

    private int codigoSalida;
    private final ArrayList<String> salida = new ArrayList<>();
    private final ArrayList<String> errores = new ArrayList<>();
    private String errorDeEscritura;
    private long milisegundos;

    public GestorProcesos(String clase, int segundosMaximos) {
        this.clase = clase;
        this.segundosMaximos = segundosMaximos;
    }

    public void ejecutar(String entrada) throws InterruptedException {

        long inicio = System.currentTimeMillis();

        String java = Path.of(System.getProperty("java.home"), "bin", "java").toString();
        String classpath = System.getProperty("java.class.path");

        ProcessBuilder pb = new ProcessBuilder(java, "-cp", classpath, clase);

        Process proceso;

        try {
            proceso = pb.start();

        } catch (IOException e) {
            errores.add("No se ha podido arrancar el proceso: " + e.getMessage());
            codigoSalida = NO_ARRANCA;
            milisegundos = System.currentTimeMillis() - inicio;
            return;
        }

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

        escritor.setDaemon(true);
        lectorSalida.setDaemon(true);
        lectorError.setDaemon(true);

        escritor.start();
        lectorSalida.start();
        lectorError.start();

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

        escritor.join(1000);
        lectorSalida.join(1000);
        lectorError.join(1000);

        milisegundos = System.currentTimeMillis() - inicio;
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
