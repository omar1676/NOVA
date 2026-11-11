import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;

/**
 * NOVA Sneakers - PSP - Proceso hijo 1: validar el pedido Custom
 *
 * QUE HACE
 *   Lee por su entrada estandar (stdin) el CSV del pedido Custom que exporta
 *   PostgreSQL con el script acceso-datos/sql/15_exportar_fabricacion.sql, y
 *   comprueba que los datos son correctos antes de que nadie los use.
 *
 * COMO CONTESTA
 *   Si todo esta bien, escribe en su salida estandar una primera linea con
 *   el resumen y, debajo, los datos del pedido ya NORMALIZADOS:
 *
 *       OK;CUSTOM-40;4;40                     <- referencia, lineas, pares
 *       CLIENTE;Club Atletico NOVA
 *       PERSONALIZACION;Club Atletico NOVA: logo bordado y ...
 *       PEDIDO;CUSTOM-40
 *       LINEA;NOVA-4-40;NOVA Velocity;Rojo;40;10
 *       LINEA;NOVA-4-41;NOVA Velocity;Rojo;41;10
 *       ...
 *       FIN
 *
 *   y termina con codigo de salida 0.
 *
 *   El bloque PEDIDO / LINEA / FIN es justo lo que lee por su stdin el
 *   AnalizadorTallas de Alvaro (paquete Psp), con su formato
 *   LINEA;sku;modelo;color;talla;cantidad. Asi el padre se lo puede pasar
 *   tal cual, sin volver a leer el CSV.
 *
 *   Si la personalizacion ocupa varias lineas, sale una linea
 *   PERSONALIZACION por cada una, en el mismo orden: no se pierde texto.
 *
 *   Si algo esta mal, NO escribe nada en la salida estandar. Escribe el
 *   motivo en la salida de error:
 *
 *       ERROR;La cantidad del registro 2 tiene que ser un numero entero, y es: diez
 *
 *   y termina con codigo de salida 2.
 *
 *   Este formato "OK;..." y "ERROR;..." es el mismo del ejemplo del profesor
 *   EstadisticasHijo2.java (mini_reto_1_lanzador_estadisticas).
 *
 * COMO SE PRUEBA SUELTO
 *   type datos\custom40_fabricacion_psp.csv | java -cp clases ValidadorPedidoCustom
 */
public class ValidadorPedidoCustom {

    // Las 8 columnas que tiene que traer el CSV, en este orden.
    // Son las que escribe de verdad el script 15, no inventadas.
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
         * Leemos TODA la entrada estandar de golpe, no linea a linea.
         *
         * Hace falta leerla entera porque un registro del CSV puede ocupar
         * varias lineas del archivo: si un campo entrecomillado lleva un
         * salto de linea dentro, PostgreSQL lo escribe asi y partir por
         * lineas rompería ese registro en dos.
         *
         * readAllBytes() nos da los bytes tal cual y los pasamos a texto con
         * UTF-8, para no cambiar ningun caracter del contenido original.
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

        /*
         * Variables donde iremos acumulando el resultado.
         * Las declaramos antes del bucle para que sigan existiendo despues.
         */
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
     * Convierte un texto en numero entero.
     *
     * Si el texto no es un numero, no seguimos: avisamos y terminamos, igual
     * que hace el hijo del ejemplo del profesor cuando recibe algo que no es
     * un entero.
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
