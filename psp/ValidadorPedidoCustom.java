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
 *   Si todo esta bien, escribe UNA linea en su salida estandar:
 *
 *       OK;CUSTOM-40;4;40
 *          referencia  lineas  pares
 *
 *   y termina con codigo de salida 0.
 *
 *   Si algo esta mal, escribe el motivo en la salida de error:
 *
 *       ERROR;La cantidad tiene que ser un numero entero: diez
 *
 *   y termina con codigo de salida 2.
 *
 *   Este formato "OK;..." y "ERROR;..." es el mismo del ejemplo del profesor
 *   EstadisticasHijo2.java (mini_reto_1_lanzador_estadisticas).
 *
 * COMO SE PRUEBA SUELTO
 *   type custom40.csv | java -cp . ValidadorPedidoCustom
 */
public class ValidadorPedidoCustom {

    // Las 8 columnas que tiene que traer el CSV, en este orden.
    // Son las que escribe de verdad el script 15, no inventadas.
    private static final String CABECERA_ESPERADA =
            "referencia,sku,cliente,modelo,color,personalizacion,talla,cantidad";

    public static void main(String[] args) throws Exception {

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
        int totalPares = 0;
        int totalRegistros = 0;

        // --- Recorremos los registros de pedido, saltando la cabecera ----
        for (int i = 1; i < registros.size(); i++) {

            ArrayList<String> campos = registros.get(i);

            // --- Comprobacion 4: cada registro tiene que traer 8 campos --
            if (campos.size() != 8) {
                error("El registro " + i + " tiene " + campos.size()
                        + " campos y tendria que tener 8");
            }

            String referenciaFila = campos.get(0);
            String textoTalla = campos.get(6);
            String textoCantidad = campos.get(7);

            // --- Comprobacion 5: la referencia no puede estar vacia ------
            if (referenciaFila.isEmpty()) {
                error("El registro " + i + " no tiene referencia de pedido");
            }

            /*
             * --- Comprobacion 6: todas las lineas, del mismo pedido ------
             *
             * La primera linea de datos fija la referencia. Las demas tienen
             * que coincidir: una orden de fabricacion es de UN pedido.
             */
            if (referencia.isEmpty()) {
                referencia = referenciaFila;
            } else if (!referencia.equals(referenciaFila)) {
                error("El registro " + i + " es del pedido " + referenciaFila
                        + " pero las anteriores son del pedido " + referencia
                        + ": un pedido por archivo");
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

            // Si hemos llegado aqui, la linea es correcta: la sumamos.
            totalPares = totalPares + cantidad;
            totalRegistros = totalRegistros + 1;
        }

        /*
         * Todo correcto. Contestamos por la salida estandar con el formato
         * acordado, para que el proceso padre lo pueda leer y partir por ";".
         */
        System.out.println("OK;" + referencia + ";" + totalRegistros + ";" + totalPares);
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
