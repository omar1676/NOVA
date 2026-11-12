import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

/**
 * NOVA Sneakers - PSP - Proceso hijo 3: ficha auxiliar para el taller
 * (tarea PSP-04 del reparto)
 *
 * QUE RECIBE por su entrada estandar (stdin)
 *   Lo prepara el proceso padre con lo que le han devuelto los otros dos
 *   hijos: los datos del pedido que da el validador y el resumen que da el
 *   analizador de tallas.
 *
 *       PEDIDO;CUSTOM-40
 *       ORIGEN;custom40_fabricacion_psp.csv
 *       CLIENTE;Club Atletico NOVA
 *       PERSONALIZACION;Club Atletico NOVA: logo bordado y ...
 *       VARIANTE_TALLA;NOVA Velocity;Rojo;40;10
 *       ...
 *       TALLA;40;10
 *       ...
 *       TOTAL;40
 *       FIN
 *
 * QUE DEVUELVE por su salida estandar (stdout)
 *   Una primera linea OK;CUSTOM-40 y, debajo, la ficha ya escrita. El padre
 *   la guarda en salidas/ficha_taller_CUSTOM-40.txt. Codigo de salida 0.
 *
 *   Si los datos no tienen esa forma, o las cantidades no cuadran, escribe
 *   ERROR;motivo en su salida de error y termina con codigo 2.
 *
 * LO QUE NO ES
 *   La ficha es un documento AUXILIAR para leer en el taller. No es la orden
 *   de fabricacion: esa la lleva Odoo. Este programa no escribe en ningun
 *   sitio, solo transforma los datos que recibe.
 *
 * COMO SE PRUEBA SUELTO
 *   Se le puede escribir la entrada a mano y terminar con FIN:
 *   java -cp clases GeneradorFichaTaller
 */
public class GeneradorFichaTaller {

    private static final String RAYA_DOBLE =
            "==================================================";
    private static final String RAYA_SIMPLE =
            "--------------------------------------------------";

    public static void main(String[] args) throws Exception {

        // En UTF-8, que es como lee el proceso padre.
        System.setOut(new PrintStream(System.out, true, StandardCharsets.UTF_8));
        System.setErr(new PrintStream(System.err, true, StandardCharsets.UTF_8));

        BufferedReader entrada = new BufferedReader(
                new InputStreamReader(System.in, StandardCharsets.UTF_8));

        // Los datos que vamos recogiendo.
        String referencia = "";
        String origen = "";
        String cliente = "";
        ArrayList<String> personalizacion = new ArrayList<>();

        // Las filas de la ficha se van preparando segun llegan.
        ArrayList<String> filasVariantes = new ArrayList<>();
        ArrayList<String> filasTallas = new ArrayList<>();

        int sumaVariantes = 0;
        int sumaTallas = 0;
        int total = -1;              // -1 = todavia no ha llegado el TOTAL
        boolean hayFin = false;
        int numeroLinea = 0;

        String linea;

        while ((linea = entrada.readLine()) != null) {

            numeroLinea++;

            // La primera linea dice de que pedido es todo: PEDIDO;referencia.
            // Sin referencia (solo "PEDIDO;") no vale.
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

            // Con -1, split no descarta los campos vacios del final: la cuenta de partes es exacta
            String[] partes = linea.split(";", -1);
            String tipo = partes[0];

            if (tipo.equals("ORIGEN")) {
                origen = loQueSigue(linea);

            } else if (tipo.equals("CLIENTE")) {
                cliente = loQueSigue(linea);

            } else if (tipo.equals("PERSONALIZACION")) {
                personalizacion.add(loQueSigue(linea));

            } else if (tipo.equals("VARIANTE_TALLA")) {
                // VARIANTE_TALLA;modelo;color;talla;pares
                if (partes.length != 5) {
                    error("La linea " + numeroLinea + " tendria que ser"
                            + " VARIANTE_TALLA;modelo;color;talla;pares");
                }
                int pares = aNumero(partes[4], numeroLinea);
                // %-20s: texto a la izquierda en 20 columnas; %6d: numero en 6 columnas
                filasVariantes.add(String.format("  %-20s %-12s %5s %6d",
                        partes[1], partes[2], partes[3], pares));
                sumaVariantes = sumaVariantes + pares;

            } else if (tipo.equals("TALLA")) {
                // TALLA;talla;pares
                if (partes.length != 3) {
                    error("La linea " + numeroLinea + " tendria que ser TALLA;talla;pares");
                }
                int pares = aNumero(partes[2], numeroLinea);
                filasTallas.add("  Talla " + partes[1] + ": " + pares + " pares");
                sumaTallas = sumaTallas + pares;

            } else if (tipo.equals("TOTAL")) {
                // TOTAL;pares
                if (partes.length != 2) {
                    error("La linea " + numeroLinea + " tendria que ser TOTAL;pares");
                }
                total = aNumero(partes[1], numeroLinea);

            } else {
                error("La linea " + numeroLinea + " es de un tipo desconocido: " + tipo);
            }
        }

        // --- Comprobaciones antes de escribir nada ----------------------
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

        /*
         * Las tres cuentas tienen que dar lo mismo. Si no, alguien ha perdido
         * pares por el camino y la ficha no seria fiable.
         */
        if (sumaVariantes != total || sumaTallas != total) {
            error("Las cantidades no cuadran: por variante suman " + sumaVariantes
                    + ", por talla " + sumaTallas + " y el total dice " + total);
        }

        // --- Todo bien: primero el OK y despues la ficha ----------------
        System.out.println("OK;" + referencia);

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
        System.out.println(RAYA_SIMPLE);
        System.out.println("Documento auxiliar generado por PSP a partir de");
        System.out.println("una exportacion del pedido. No sustituye a la");
        System.out.println("orden de fabricacion de Odoo.");
        System.out.println(RAYA_DOBLE);
    }

    /** Todo lo que va detras del primer ";" de la linea. */
    private static String loQueSigue(String linea) {
        return linea.substring(linea.indexOf(';') + 1);
    }

    /** Convierte un texto en un entero no negativo, o termina con error. */
    private static int aNumero(String texto, int numeroLinea) {

        try {
            int numero = Integer.parseInt(texto.trim());

            if (numero < 0) {
                error("La linea " + numeroLinea + " trae una cantidad negativa: " + texto);
            }
            return numero;

        } catch (NumberFormatException e) {
            error("La linea " + numeroLinea + " trae una cantidad que no es un numero: " + texto);
            return 0;   // no se llega: error() termina el programa
        }
    }

    /** Escribe el motivo por stderr y termina con codigo 2 (datos incorrectos). */
    private static void error(String motivo) {
        System.err.println("ERROR;" + motivo);
        System.exit(2);
    }
}
