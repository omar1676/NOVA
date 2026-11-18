import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

// Hijo 3: comprueba que las cantidades cuadran y escribe la ficha auxiliar para el taller
public class GeneradorFichaTaller {

    // Rayas que separan las partes de la ficha
    private static final String RAYA_DOBLE =
            "==================================================";
    private static final String RAYA_SIMPLE =
            "--------------------------------------------------";

    // Lee los datos por stdin linea a linea y, si todo cuadra, escribe OK;referencia y la ficha
    public static void main(String[] args) throws Exception {

        // stdout y stderr en UTF-8, que es como los lee el padre
        System.setOut(new PrintStream(System.out, true, StandardCharsets.UTF_8));
        System.setErr(new PrintStream(System.err, true, StandardCharsets.UTF_8));

        BufferedReader entrada = new BufferedReader(
                new InputStreamReader(System.in, StandardCharsets.UTF_8));

        // Datos del pedido que se van leyendo
        String referencia = "";
        String origen = "";
        String cliente = "";
        ArrayList<String> personalizacion = new ArrayList<>();

        ArrayList<String> filasVariantes = new ArrayList<>();
        ArrayList<String> filasTallas = new ArrayList<>();

        // Sumas por variante y por talla, para comprobar que las dos dan el total
        int sumaVariantes = 0;
        int sumaTallas = 0;
        int total = -1;
        boolean hayFin = false;
        int numeroLinea = 0;

        String linea;

        // Se lee hasta la linea FIN
        while ((linea = entrada.readLine()) != null) {

            numeroLinea++;

            // La primera linea tiene que ser PEDIDO;referencia
            if (numeroLinea == 1) {
                if (!linea.startsWith("PEDIDO;") || linea.equals("PEDIDO;")) {
                    error("La primera linea tiene que ser PEDIDO;referencia");
                }
                referencia = loQueSigue(linea);
                continue;
            }

            if (linea.equals("FIN")) {
                hayFin = true;
                break;
            }

            // Cada linea empieza por su tipo (ORIGEN, CLIENTE, VARIANTE_TALLA, TALLA, TOTAL...).
            // El -1 hace que split no quite los campos vacios del final
            String[] partes = linea.split(";", -1);
            String tipo = partes[0];

            if (tipo.equals("ORIGEN")) {
                origen = loQueSigue(linea);

            } else if (tipo.equals("CLIENTE")) {
                cliente = loQueSigue(linea);

            } else if (tipo.equals("PERSONALIZACION")) {
                personalizacion.add(loQueSigue(linea));

            } else if (tipo.equals("VARIANTE_TALLA")) {
                if (partes.length != 5) {
                    error("La linea " + numeroLinea + " tendria que ser"
                            + " VARIANTE_TALLA;modelo;color;talla;pares");
                }
                int pares = aNumero(partes[4], numeroLinea);
                filasVariantes.add(String.format("  %-20s %-12s %5s %6d",
                        partes[1], partes[2], partes[3], pares));
                sumaVariantes = sumaVariantes + pares;

            } else if (tipo.equals("TALLA")) {
                if (partes.length != 3) {
                    error("La linea " + numeroLinea + " tendria que ser TALLA;talla;pares");
                }
                int pares = aNumero(partes[2], numeroLinea);
                filasTallas.add("  Talla " + partes[1] + ": " + pares + " pares");
                sumaTallas = sumaTallas + pares;

            } else if (tipo.equals("TOTAL")) {
                if (partes.length != 2) {
                    error("La linea " + numeroLinea + " tendria que ser TOTAL;pares");
                }
                total = aNumero(partes[1], numeroLinea);

            } else {
                error("La linea " + numeroLinea + " es de un tipo desconocido: " + tipo);
            }
        }

        // Comprobaciones: que no falte nada
        if (numeroLinea == 0) {
            error("No ha llegado ningun dato");
        }
        if (!hayFin) {
            error("Faltan datos: no ha llegado la linea FIN");
        }
        if (cliente.isBlank()) {
            error("Falta el cliente del pedido");
        }
        if (filasVariantes.isEmpty() || filasTallas.isEmpty()) {
            error("Faltan las cantidades por variante y talla");
        }
        if (total < 0) {
            error("Falta la linea TOTAL");
        }

        // Las dos sumas tienen que dar el total que manda el analizador
        if (sumaVariantes != total || sumaTallas != total) {
            error("Las cantidades no cuadran: por variante suman " + sumaVariantes
                    + ", por talla " + sumaTallas + " y el total dice " + total);
        }

        // Primera linea para el padre; despues, la ficha
        System.out.println("OK;" + referencia);

        // Cabecera de la ficha
        System.out.println(RAYA_DOBLE);
        System.out.println("NOVA SNEAKERS - FICHA AUXILIAR PARA TALLER");
        System.out.println(RAYA_DOBLE);
        System.out.println("Pedido:           " + referencia);
        System.out.println("Cliente:          " + cliente);
        System.out.println("Datos exportados: " + origen);
        System.out.println();

        System.out.println("Personalizacion:");
        if (personalizacion.isEmpty()) {
            System.out.println("  (el pedido no trae personalizacion)");
        } else {
            for (String texto : personalizacion) {
                System.out.println("  " + texto);
            }
        }
        System.out.println();

        System.out.println("Pares por modelo, color y talla:");
        System.out.println(String.format("  %-20s %-12s %5s %6s",
                "Modelo", "Color", "Talla", "Pares"));
        for (String fila : filasVariantes) {
            System.out.println(fila);
        }
        System.out.println();

        System.out.println("Pares por talla:");
        for (String fila : filasTallas) {
            System.out.println(fila);
        }
        System.out.println();

        System.out.println("TOTAL: " + total + " pares");
        // Pie: la ficha no sustituye a la orden de fabricacion de Odoo
        System.out.println(RAYA_SIMPLE);
        System.out.println("Documento auxiliar generado por PSP a partir de");
        System.out.println("una exportacion del pedido. No sustituye a la");
        System.out.println("orden de fabricacion de Odoo.");
        System.out.println(RAYA_DOBLE);
    }

    // Devuelve lo que va despues del primer ; de la linea
    private static String loQueSigue(String linea) {
        return linea.substring(linea.indexOf(';') + 1);
    }

    // Pasa un texto a entero; rechaza los negativos y lo que no es un numero
    private static int aNumero(String texto, int numeroLinea) {

        try {
            int numero = Integer.parseInt(texto.trim());

            if (numero < 0) {
                error("La linea " + numeroLinea + " trae una cantidad negativa: " + texto);
            }
            return numero;

        } catch (NumberFormatException e) {
            error("La linea " + numeroLinea + " trae una cantidad que no es un numero: " + texto);
            return 0;
        }
    }

    // Rechaza los datos: ERROR;motivo por stderr y codigo 2
    private static void error(String motivo) {
        System.err.println("ERROR;" + motivo);
        System.exit(2);
    }
}
