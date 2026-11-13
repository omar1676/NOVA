import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

/**
 * Valida el CSV del script 15 y emite datos normalizados para el analizador de Alvaro.
 * Salida: OK;referencia;lineas;pares, CLIENTE, PERSONALIZACION y PEDIDO/LINEA/FIN.
 * La personalizacion multilinea conserva su orden en varias lineas PERSONALIZACION.
 * Termina con 0 si es valido; con 2 y ERROR por stderr si hay datos incorrectos.
 * Sigue el protocolo del ejemplo EstadisticasHijo2.java del profesor.
 */
public class ValidadorPedidoCustom {

    // Las 8 columnas que escribe el script 15, en este orden.
    private static final String CABECERA_ESPERADA =
            "referencia,sku,cliente,modelo,color,personalizacion,talla,cantidad";

    public static void main(String[] args) throws Exception {

        /*
         * Escribimos en UTF-8, que es como lee el proceso padre. Si no, una
         * letra con tilde de un cliente o de una personalizacion le llegaria
         * cambiada.
         */
        System.setOut(new PrintStream(System.out, true, StandardCharsets.UTF_8));
        System.setErr(new PrintStream(System.err, true, StandardCharsets.UTF_8));

        /*
         * Leemos TODA la entrada de golpe, no linea a linea: un registro del
         * CSV puede ocupar varias lineas si un campo entre comillas lleva un
         * salto de linea dentro (ver LectorCsv).
         */
        String contenido = new String(System.in.readAllBytes(), StandardCharsets.UTF_8);

        // --- Comprobacion 1: tiene que llegar algo -----------------------
        if (contenido.isBlank()) {
            error("El pedido esta vacio: no ha llegado nada");
        }

        /*
         * LectorCsv recorre el contenido y nos devuelve los REGISTROS, ya
         * separados en campos y respetando las comillas.
         */
        ArrayList<ArrayList<String>> registros;

        try {
            registros = LectorCsv.partirTodo(contenido);

        } catch (IllegalArgumentException e) {
            error("El CSV esta mal formado: " + e.getMessage());
            return;   // no se llega: error() termina el programa
        }

        if (registros.isEmpty()) {
            error("El pedido esta vacio: no ha llegado ningun registro");
        }

        // --- Comprobacion 2: la cabecera y sus 8 columnas ----------------
        String cabecera = String.join(",", registros.get(0));

        if (!cabecera.equals(CABECERA_ESPERADA)) {
            error("La cabecera no es la esperada."
                    + " Esperaba: " + CABECERA_ESPERADA
                    + " / He recibido: " + cabecera);
        }

        // --- Comprobacion 3: tiene que haber registros de pedido ---------
        if (registros.size() < 2) {
            error("El pedido solo trae la cabecera, sin ningun registro de pedido");
        }

        // Lo que se va acumulando al recorrer los registros.
        String referencia = "";
        String cliente = "";
        String personalizacion = "";
        int totalPares = 0;
        int totalRegistros = 0;

        // Las lineas LINEA;... ya normalizadas, para escribirlas al final.
        ArrayList<String> lineasNormalizadas = new ArrayList<>();

        // --- Recorremos los registros de pedido, saltando la cabecera ----
        for (int i = 1; i < registros.size(); i++) {

            ArrayList<String> campos = registros.get(i);

            // --- Comprobacion 4: cada registro tiene que traer 8 campos --
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

            /*
             * --- Comprobacion 5: no falta ningun dato de la linea ---------
             *
             * Ademas, estos textos van despues en lineas separadas por ";",
             * asi que no pueden llevar un ";" ni un salto de linea dentro.
             */
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

            /*
             * --- Comprobacion 6: todas las lineas, del mismo pedido ------
             *
             * La primera linea de datos fija la referencia y el cliente. Las
             * demas tienen que coincidir: una orden de fabricacion es de UN
             * pedido, y un pedido es de UN cliente.
             */
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

            // --- Comprobacion 7: la talla tiene que ser un numero --------
            int talla = aNumero(textoTalla, "La talla", i);

            if (talla <= 0) {
                error("La talla del registro " + i + " tiene que ser positiva,"
                        + " y es " + talla);
            }

            // --- Comprobacion 8: la cantidad, un entero positivo --------
            int cantidad = aNumero(textoCantidad, "La cantidad", i);

            if (cantidad <= 0) {
                error("La cantidad del registro " + i + " tiene que ser mayor"
                        + " que cero, y es " + cantidad);
            }

            // Si hemos llegado aqui, la linea es correcta: la guardamos.
            lineasNormalizadas.add("LINEA;" + sku + ";" + modelo + ";" + color
                    + ";" + talla + ";" + cantidad);

            totalPares = totalPares + cantidad;
            totalRegistros = totalRegistros + 1;
        }

        /*
         * Todo correcto. Contestamos por la salida estandar con el formato
         * acordado. La primera linea es la misma de siempre, para que el
         * padre la pueda partir por ";".
         */
        System.out.println("OK;" + referencia + ";" + totalRegistros + ";" + totalPares);
        System.out.println("CLIENTE;" + cliente);

        // Una linea PERSONALIZACION por cada linea del texto (puede no haber).
        // El split corta por cualquier final de linea: \r\n (Windows), \n o \r.
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

    /**
     * Comprueba un texto obligatorio de un registro: que no este vacio y que
     * no lleve ";" ni saltos de linea, porque romperian las lineas que se
     * envian a los otros procesos.
     */
    private static void comprobarTexto(String texto, String queEs, int numeroRegistro) {

        if (texto.isBlank()) {
            error("Falta " + queEs + " en el registro " + numeroRegistro);
        }

        if (texto.contains(";") || texto.contains("\n") || texto.contains("\r")) {
            error("En el registro " + numeroRegistro + ", " + queEs
                    + " no puede llevar ';' ni saltos de linea: " + texto);
        }
    }

    /**
     * Convierte un texto en numero entero. Si no es un numero, termina con
     * error, como el hijo del ejemplo del profesor.
     */
    private static int aNumero(String texto, String queEs, int numeroRegistro) {

        try {
            return Integer.parseInt(texto.trim());

        } catch (NumberFormatException e) {
            error(queEs + " del registro " + numeroRegistro
                    + " tiene que ser un numero entero, y es: " + texto);
            return 0;   // no se llega nunca: error() termina el programa
        }
    }

    /**
     * Escribe el motivo del fallo en la salida de error y termina el proceso
     * con codigo 2, para que el padre sepa que algo ha ido mal.
     */
    private static void error(String motivo) {
        System.err.println("ERROR;" + motivo);
        System.exit(2);
    }
}
