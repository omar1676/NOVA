package Psp;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.TimeUnit;

public class LanzadorAnalizador {

    private static final int SEGUNDOS_MAXIMOS = 10;

    public static ResultadoProceso analizar(String pedido) throws IOException, InterruptedException {
        return lanzar("Psp.AnalizadorTallas", pedido);
    }

    public static ResultadoProceso lanzar(String clase, String entrada)
            throws IOException, InterruptedException {

        String java = System.getProperty("java.home") + "/bin/java";
        String classpath = System.getProperty("java.class.path");

        ProcessBuilder pb = new ProcessBuilder(java, "-cp", classpath, clase);
        Process proceso = pb.start();

        try (OutputStream os = proceso.getOutputStream()) {
            os.write(entrada.getBytes(StandardCharsets.UTF_8));
        }

        String salida = new String(proceso.getInputStream().readAllBytes(), StandardCharsets.UTF_8);
        String errores = new String(proceso.getErrorStream().readAllBytes(), StandardCharsets.UTF_8);

        boolean terminado = proceso.waitFor(SEGUNDOS_MAXIMOS, TimeUnit.SECONDS);
        if (!terminado) {
            proceso.destroyForcibly();
            return new ResultadoProceso(ResultadoProceso.SIN_RESPUESTA, salida, errores);
        }
        return new ResultadoProceso(proceso.exitValue(), salida, errores);
    }
}