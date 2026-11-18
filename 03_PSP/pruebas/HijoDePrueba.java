import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

// Hijo falso, solo para las pruebas: hace lo que le pide la primera linea de su entrada
public class HijoDePrueba {

    // ECO devuelve lo recibido, DOS_SALIDAS escribe en stdout y en stderr, CODIGO;n sale con n,
    // EXCEPCION lanza una excepcion y DORMIR tarda 60 s para probar el tiempo de espera
    public static void main(String[] args) throws Exception {

        System.setOut(new PrintStream(System.out, true, StandardCharsets.UTF_8));
        System.setErr(new PrintStream(System.err, true, StandardCharsets.UTF_8));

        BufferedReader entrada = new BufferedReader(
                new InputStreamReader(System.in, StandardCharsets.UTF_8));

        // Se lee toda la entrada; la primera linea es la orden
        ArrayList<String> lineas = new ArrayList<>();
        String linea;

        while ((linea = entrada.readLine()) != null) {
            lineas.add(linea);
        }

        String orden = "";
        if (!lineas.isEmpty()) {
            orden = lineas.get(0);
        }

        if (orden.equals("ECO")) {
            System.out.println("OK;eco");
            for (int i = 1; i < lineas.size(); i++) {
                System.out.println(lineas.get(i));
            }

        } else if (orden.equals("DOS_SALIDAS")) {
            System.out.println("OK;salida");
            System.err.println("AVISO;esto va por stderr");

        } else if (orden.startsWith("CODIGO;")) {
            System.err.println("ERROR;codigo pedido por la prueba");
            System.exit(Integer.parseInt(orden.substring("CODIGO;".length())));

        } else if (orden.equals("EXCEPCION")) {
            throw new RuntimeException("fallo provocado por la prueba");

        } else if (orden.equals("DORMIR")) {
            Thread.sleep(60000);

        } else {
            System.err.println("ERROR;orden desconocida: " + orden);
            System.exit(2);
        }
    }
}
