import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

public class ValidadorPedidoCustom {

    private static final String CABECERA_ESPERADA =
            "referencia,sku,cliente,modelo,color,personalizacion,talla,cantidad";

    public static void main(String[] args) throws Exception {

        System.setOut(new PrintStream(System.out, true, StandardCharsets.UTF_8));
        System.setErr(new PrintStream(System.err, true, StandardCharsets.UTF_8));

        String contenido = new String(System.in.readAllBytes(), StandardCharsets.UTF_8);

        if (contenido.isBlank()) {
            error("El pedido esta vacio: no ha llegado nada");
        }

        ArrayList<ArrayList<String>> registros;

        try {
            registros = LectorCsv.partirTodo(contenido);

        } catch (IllegalArgumentException e) {
            error("El CSV esta mal formado: " + e.getMessage());
            return;
        }

        if (registros.isEmpty()) {
            error("El pedido esta vacio: no ha llegado ningun registro");
        }

        String cabecera = String.join(",", registros.get(0));

        if (!cabecera.equals(CABECERA_ESPERADA)) {
            error("La cabecera no es la esperada."
                    + " Esperaba: " + CABECERA_ESPERADA
                    + " / He recibido: " + cabecera);
        }

        if (registros.size() < 2) {
            error("El pedido solo trae la cabecera, sin ningun registro de pedido");
        }

        String referencia = "";
        String cliente = "";
        String personalizacion = "";
        int totalPares = 0;
        int totalRegistros = 0;

        ArrayList<String> lineasNormalizadas = new ArrayList<>();

        for (int i = 1; i < registros.size(); i++) {

            ArrayList<String> campos = registros.get(i);

            if (campos.size() != 8) {
                error("El registro " + i + " tiene " + campos.size()
                        + " campos y tendria que tener 8");
            }

            String referenciaFila = campos.get(0);
            String sku = campos.get(1);
            String clienteFila = campos.get(2);
            String modelo = campos.get(3);
            String color = campos.get(4);
            String textoTalla = campos.get(6);
            String textoCantidad = campos.get(7);

            comprobarTexto(referenciaFila, "la referencia", i);
            comprobarTexto(sku, "el SKU", i);
            comprobarTexto(clienteFila, "el cliente", i);
            comprobarTexto(modelo, "el modelo", i);
            comprobarTexto(color, "el color", i);

            if (textoTalla.isBlank()) {
                error("Falta la talla en el registro " + i);
            }

            if (textoCantidad.isBlank()) {
                error("Falta la cantidad en el registro " + i);
            }

            if (referencia.isEmpty()) {
                referencia = referenciaFila;
                cliente = clienteFila;
                personalizacion = campos.get(5);

            } else if (!referencia.equals(referenciaFila)) {
                error("El registro " + i + " es del pedido " + referenciaFila
                        + " pero las anteriores son del pedido " + referencia
                        + ": un pedido por archivo");

            } else if (!cliente.equals(clienteFila)) {
                error("El registro " + i + " es del cliente " + clienteFila
                        + " pero las anteriores son de " + cliente
                        + ": un pedido es de un solo cliente");
            }

            int talla = aNumero(textoTalla, "La talla", i);

            if (talla <= 0) {
                error("La talla del registro " + i + " tiene que ser positiva,"
                        + " y es " + talla);
            }

            int cantidad = aNumero(textoCantidad, "La cantidad", i);

            if (cantidad <= 0) {
                error("La cantidad del registro " + i + " tiene que ser mayor"
                        + " que cero, y es " + cantidad);
            }

            lineasNormalizadas.add("LINEA;" + sku + ";" + modelo + ";" + color
                    + ";" + talla + ";" + cantidad);

            totalPares = totalPares + cantidad;
            totalRegistros = totalRegistros + 1;
        }

        System.out.println("OK;" + referencia + ";" + totalRegistros + ";" + totalPares);
        System.out.println("CLIENTE;" + cliente);

        if (!personalizacion.isBlank()) {
            String[] partes = personalizacion.split("\r\n|\n|\r");

            for (String parte : partes) {
                System.out.println("PERSONALIZACION;" + parte);
            }
        }

        System.out.println("PEDIDO;" + referencia);

        for (String linea : lineasNormalizadas) {
            System.out.println(linea);
        }

        System.out.println("FIN");
    }

    private static void comprobarTexto(String texto, String queEs, int numeroRegistro) {

        if (texto.isBlank()) {
            error("Falta " + queEs + " en el registro " + numeroRegistro);
        }

        if (texto.contains(";") || texto.contains("\n") || texto.contains("\r")) {
            error("En el registro " + numeroRegistro + ", " + queEs
                    + " no puede llevar ';' ni saltos de linea: " + texto);
        }
    }

    private static int aNumero(String texto, String queEs, int numeroRegistro) {

        try {
            return Integer.parseInt(texto.trim());

        } catch (NumberFormatException e) {
            error(queEs + " del registro " + numeroRegistro
                    + " tiene que ser un numero entero, y es: " + texto);
            return 0;
        }
    }

    private static void error(String motivo) {
        System.err.println("ERROR;" + motivo);
        System.exit(2);
    }
}
