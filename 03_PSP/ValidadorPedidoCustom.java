import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

// Hijo 1: valida el CSV del pedido y devuelve sus datos normalizados por stdout
public class ValidadorPedidoCustom {

    // Las 8 columnas que exporta 15_exportar_fabricacion.sql, en el mismo orden
    private static final String CABECERA_ESPERADA =
            "referencia,sku,cliente,modelo,color,personalizacion,talla,cantidad";

    // Lee el CSV por stdin, lo comprueba y escribe la respuesta para el padre
    public static void main(String[] args) throws Exception {

        // stdout y stderr en UTF-8, que es como los lee el padre
        System.setOut(new PrintStream(System.out, true, StandardCharsets.UTF_8));
        System.setErr(new PrintStream(System.err, true, StandardCharsets.UTF_8));

        // El CSV entero llega por la entrada estandar
        String contenido = new String(System.in.readAllBytes(), StandardCharsets.UTF_8);

        if (contenido.isBlank()) {
            error("El pedido esta vacio: no ha llegado nada");
        }

        ArrayList<ArrayList<String>> registros;

        try {
            registros = LectorCsv.partirTodo(contenido);

        } catch (IllegalArgumentException e) {
            error("El CSV esta mal formado: " + e.getMessage());
            // El return hace falta porque el compilador no sabe que error() acaba el programa
            return;
        }

        if (registros.isEmpty()) {
            error("El pedido esta vacio: no ha llegado ningun registro");
        }

        // La primera fila tiene que ser exactamente la cabecera esperada
        String cabecera = String.join(",", registros.get(0));

        if (!cabecera.equals(CABECERA_ESPERADA)) {
            error("La cabecera no es la esperada."
                    + " Esperaba: " + CABECERA_ESPERADA
                    + " / He recibido: " + cabecera);
        }

        if (registros.size() < 2) {
            error("El pedido solo trae la cabecera, sin ningun registro de pedido");
        }

        // Datos del pedido (se toman de la primera fila) y totales
        String referencia = "";
        String cliente = "";
        String personalizacion = "";
        int totalPares = 0;
        int totalRegistros = 0;

        ArrayList<String> lineasNormalizadas = new ArrayList<>();

        // Se revisa cada registro, desde el 1 para saltar la cabecera
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

            // Un archivo es un solo pedido de un solo cliente
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

            // Talla y cantidad: enteros mayores que cero (el rango 20-55 lo mira el analizador)
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

            // Linea normalizada en el formato que ya leia el analizador de Alvaro
            lineasNormalizadas.add("LINEA;" + sku + ";" + modelo + ";" + color
                    + ";" + talla + ";" + cantidad);

            totalPares = totalPares + cantidad;
            totalRegistros = totalRegistros + 1;
        }

        // Respuesta: primero OK;referencia;lineas;pares, que es la linea que lee el padre
        System.out.println("OK;" + referencia + ";" + totalRegistros + ";" + totalPares);
        System.out.println("CLIENTE;" + cliente);

        // Una linea PERSONALIZACION por cada linea del texto, para no perder nada
        if (!personalizacion.isBlank()) {
            String[] partes = personalizacion.split("\r\n|\n|\r");

            for (String parte : partes) {
                System.out.println("PERSONALIZACION;" + parte);
            }
        }

        // Bloque PEDIDO / LINEA / FIN, que el padre pasa al analizador
        System.out.println("PEDIDO;" + referencia);

        for (String linea : lineasNormalizadas) {
            System.out.println(linea);
        }

        System.out.println("FIN");
    }

    // Un campo de texto no puede faltar ni llevar ; o saltos de linea (romperian el formato de salida)
    private static void comprobarTexto(String texto, String queEs, int numeroRegistro) {

        if (texto.isBlank()) {
            error("Falta " + queEs + " en el registro " + numeroRegistro);
        }

        if (texto.contains(";") || texto.contains("\n") || texto.contains("\r")) {
            error("En el registro " + numeroRegistro + ", " + queEs
                    + " no puede llevar ';' ni saltos de linea: " + texto);
        }
    }

    // Pasa un texto a entero; si no es un numero, rechaza el pedido
    private static int aNumero(String texto, String queEs, int numeroRegistro) {

        try {
            return Integer.parseInt(texto.trim());

        } catch (NumberFormatException e) {
            error(queEs + " del registro " + numeroRegistro
                    + " tiene que ser un numero entero, y es: " + texto);
            return 0;
        }
    }

    // Rechaza el pedido: ERROR;motivo por stderr y codigo 2
    // (el mismo formato que el ejemplo EstadisticasHijo2 del profesor)
    private static void error(String motivo) {
        System.err.println("ERROR;" + motivo);
        System.exit(2);
    }
}
