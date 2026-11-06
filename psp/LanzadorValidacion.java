import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.concurrent.TimeUnit;

/**
 * NOVA Sneakers - PSP - Proceso padre
 *
 * QUE HACE
 *   1. Lee el CSV del pedido Custom que exporta PostgreSQL.
 *   2. Lanza ValidadorPedidoCustom y le manda el CSV por su stdin.
 *   3. Lee su respuesta, comprueba el codigo de salida y que empiece por OK.
 *   4. SOLO si la validacion es correcta, lanza AnalizadorTallas y le manda
 *      el mismo CSV, y muestra su resumen.
 *
 *   Si cualquiera de los dos falla, se muestra el error y NO se continua.
 *
 * DE DONDE VIENE EL CSV
 *   De PostgreSQL, del script acceso-datos/sql/15_exportar_fabricacion.sql.
 *   Hoy NO viene de Odoo: el ERP todavia no exporta nada.
 *
 * QUE NO ES ESTA CLASE
 *   No es el ProcesadorPedidosCustom del enunciado. Ese es el coordinador
 *   del equipo, que encadenara tambien GeneradorFichaTaller. Esta clase solo
 *   lanza y comprueba mis dos procesos.
 *
 * COMO SE EJECUTA
 *   java -cp . LanzadorValidacion custom40.csv
 */
public class LanzadorValidacion {

    // Si un hijo tarda mas de esto, algo va mal y no esperamos para siempre.
    private static final int SEGUNDOS_DE_ESPERA = 10;

    public static void main(String[] args) throws Exception {

        // --- Comprobamos que nos han dicho que archivo leer ---------------
        if (args.length != 1) {
            System.err.println("Uso: java LanzadorValidacion <ruta del CSV>");
            System.exit(1);
        }

        Path rutaCsv = Path.of(args[0]);

        if (!Files.exists(rutaCsv)) {
            System.err.println("No existe el archivo: " + rutaCsv);
            System.exit(1);
        }

        /*
         * --- Leemos el CSV entero, TAL CUAL ------------------------------
         *
         * Lo leemos como un solo texto, no como una lista de lineas.
         *
         * POR QUE IMPORTA
         *   Antes se leia con readAllLines() y se reenviaba linea a linea con
         *   newLine(). Eso parte los registros que ocupan varias lineas y,
         *   ademas, cambia los finales de linea por los del sistema. Un campo
         *   entrecomillado con un salto de linea dentro llegaba al hijo
         *   alterado.
         *
         *   Leyendo y enviando el texto completo, el hijo recibe exactamente
         *   los mismos caracteres que tiene el archivo.
         */
        String contenidoCsv = Files.readString(rutaCsv, StandardCharsets.UTF_8);

        System.out.println("Archivo leido: " + rutaCsv);
        System.out.println("Bytes del archivo: " + contenidoCsv.length());
        System.out.println();

        // --- PASO 1: validar ----------------------------------------------
        System.out.println("--- Paso 1: validar el pedido");

        String respuesta = ejecutarHijo("ValidadorPedidoCustom", contenidoCsv, true);

        /*
         * Antes de interpretar nada comprobamos que la respuesta tenga la
         * forma acordada. Esta comprobacion es la del ejemplo del profesor
         * LanzadorEstadisticas.java.
         */
        if (respuesta == null || !respuesta.startsWith("OK;")) {
            System.err.println("Respuesta no valida del validador: " + respuesta);
            System.exit(1);
        }

        String[] partes = respuesta.split(";");

        if (partes.length != 4) {
            System.err.println("El validador tenia que devolver 4 campos y ha"
                    + " devuelto " + partes.length);
            System.exit(1);
        }

        // Interpretamos los datos que nos ha enviado el hijo.
        String referencia = partes[1];
        int lineasDePedido = Integer.parseInt(partes[2]);
        int pares = Integer.parseInt(partes[3]);

        System.out.println("Pedido validado: " + referencia);
        System.out.println("Lineas de pedido: " + lineasDePedido);
        System.out.println("Pares en total: " + pares);
        System.out.println();

        // --- PASO 2: resumir por tallas -----------------------------------
        System.out.println("--- Paso 2: resumen por tallas");

        ejecutarHijo("AnalizadorTallas", contenidoCsv, false);

        System.out.println();
        System.out.println("Procesamiento auxiliar terminado para " + referencia);
    }

    /**
     * Lanza un proceso hijo, le manda el CSV por su stdin y recoge lo que
     * conteste.
     *
     * @param clase          nombre de la clase Java que se va a lanzar
     * @param contenidoCsv   el CSV completo que le vamos a enviar por stdin
     * @param unaSolaLinea   true  -> devuelve la primera linea de su stdout
     *                       false -> muestra todo su stdout y devuelve null
     *
     * Si el hijo falla, se muestra su error y el programa termina: no se
     * continua con el proceso siguiente.
     */
    private static String ejecutarHijo(String clase,
                                       String contenidoCsv,
                                       boolean unaSolaLinea) throws Exception {

        /*
         * Construimos la ruta al "java" que esta usando este mismo programa,
         * y reutilizamos su classpath para que el hijo encuentre sus clases.
         * Las dos cosas estan copiadas de los ejemplos del profesor.
         */
        String java = Path.of(System.getProperty("java.home"), "bin", "java").toString();
        String classpath = System.getProperty("java.class.path");

        ProcessBuilder pb = new ProcessBuilder(java, "-cp", classpath, clase);

        // Arrancamos el hijo.
        Process proceso = pb.start();

        /*
         * Le escribimos el CSV por su entrada estandar, pero DESDE UN HILO.
         *
         * POR QUE UN HILO, Y NO AQUI DIRECTAMENTE
         *   La tuberia que conecta al padre con el hijo tiene un tamano
         *   limitado. Si el hijo no lee su entrada, la tuberia se llena y la
         *   escritura se queda bloqueada esperando sitio.
         *
         *   Si escribieramos aqui mismo, ese bloqueo seria del padre: se
         *   quedaria atascado en write() y no llegaria nunca a la espera con
         *   limite de tiempo de mas abajo. Se comprobo con un CSV de 6 MB y un
         *   hijo que no lee nada: el programa se quedaba colgado mas de 45
         *   segundos, hasta que lo mataba algo de fuera.
         *
         *   Escribiendo desde un hilo, si se bloquea solo se bloquea el hilo.
         *   El padre sigue libre, llega a su espera y puede cancelar al hijo.
         *   Al cancelarlo se cierra la tuberia, la escritura falla con
         *   IOException, el hilo la recoge y termina.
         *
         *   Es un hilo de tres lineas y es la unica concurrencia del programa.
         *
         * CERRAR AL ACABAR es igual de importante: mientras no se cierre, el
         * hijo sigue esperando mas datos. El try-with-resources lo cierra.
         */
        /*
         * Un array de una sola posicion para que el hilo pueda dejar aqui el
         * mensaje si la escritura falla. Hace falta el array porque desde
         * dentro de un hilo creado asi no se puede cambiar una variable
         * normal del metodo.
         */
        String[] errorDeEscritura = new String[1];

        Thread escritor = new Thread(() -> {
            try (BufferedWriter entradaDelHijo =
                         proceso.outputWriter(StandardCharsets.UTF_8)) {

                // De una vez y sin tocar nada: los saltos de linea del
                // archivo llegan al hijo tal como estaban.
                entradaDelHijo.write(contenidoCsv);

            } catch (IOException e) {
                // Guardamos el motivo. Mas abajo el padre decidira si es un
                // fallo de verdad o una consecuencia de haber cancelado.
                errorDeEscritura[0] = e.getMessage();
            }
        });

        /*
         * Los otros dos hilos VACIAN la salida y la salida de error del hijo
         * mientras trabaja.
         *
         * POR QUE HACE FALTA
         *   Las tuberias de salida tambien son limitadas. Si el hijo escribe
         *   mucho y nadie lo lee, se llenan y el hijo se queda bloqueado al
         *   escribir, sin poder terminar nunca. Pasa de verdad: un pedido con
         *   6.000 tallas distintas hace que el analizador escriba mas de lo
         *   que cabe en la tuberia.
         *
         *   Leyendo desde hilos, las tuberias nunca se llenan y el hijo puede
         *   acabar. Asi no perdemos el resultado de un hijo que funciona.
         *
         * Cada hilo guarda las lineas en SU lista. El padre no las toca hasta
         * despues de join(), y por eso no hace falta sincronizar nada.
         */
        ArrayList<String> salida = new ArrayList<>();
        ArrayList<String> errores = new ArrayList<>();

        Thread lectorSalida = new Thread(() -> leerTodo(
                proceso.inputReader(StandardCharsets.UTF_8), salida));

        Thread lectorError = new Thread(() -> leerTodo(
                proceso.errorReader(StandardCharsets.UTF_8), errores));

        /*
         * Demonios: si alguno se quedara bloqueado, no impide que el programa
         * termine. Sin esto, un hilo atascado mantendria vivo el proceso.
         */
        escritor.setDaemon(true);
        lectorSalida.setDaemon(true);
        lectorError.setDaemon(true);

        escritor.start();
        lectorSalida.start();
        lectorError.start();

        /*
         * PRIMERO esperamos a que termine, y DESPUES leemos lo que ha escrito.
         *
         * El orden importa, y mucho. Si leyeramos antes, el padre se quedaria
         * esperando en readLine() a que el hijo escribiera algo; y si el hijo
         * esta bloqueado y no escribe nada, el padre no llegaria nunca a esta
         * espera con limite de tiempo. Se comprobo: con las lecturas delante,
         * un hijo bloqueado deja el programa colgado para siempre.
         *
         * Esperando primero, pase lo que pase el padre recupera el control a
         * los SEGUNDOS_DE_ESPERA y puede cancelar al hijo.
         *
         * Mientras esperamos, los tres hilos mantienen las tres tuberias en
         * marcha, asi que el hijo no puede quedarse bloqueado por ninguna.
         * Si aun asi no termina, lo cancelamos.
         *
         * El control de tiempo es el del ejemplo del profesor
         * LanzadorProcesoFinal2.java.
         */
        boolean termino = proceso.waitFor(SEGUNDOS_DE_ESPERA, TimeUnit.SECONDS);

        if (!termino) {
            System.err.println("El proceso " + clase + " no ha terminado en "
                    + SEGUNDOS_DE_ESPERA + " segundos. Se cancela.");

            // destroy() pide que termine; destroyForcibly() lo mata.
            proceso.destroy();

            if (!proceso.waitFor(1, TimeUnit.SECONDS)) {
                proceso.destroyForcibly();
                proceso.waitFor();
            }

            /*
             * Al morir el hijo se cierran las tuberias y los tres hilos
             * terminan solos. Les damos un segundo y seguimos: son demonios,
             * asi que aunque siguieran bloqueados no impedirian salir.
             *
             * Aqui NO miramos errorDeEscritura: si hemos cancelado al hijo, es
             * normal que la escritura haya fallado. No es un fallo aparte.
             */
            escritor.join(1000);
            lectorSalida.join(1000);
            lectorError.join(1000);

            System.exit(1);
        }

        /*
         * El hijo ha terminado solo. Esperamos a que los hilos acaben de
         * recoger lo que haya escrito, para no quedarnos con media respuesta.
         */
        escritor.join(1000);
        lectorSalida.join(1000);
        lectorError.join(1000);

        int codigoSalida = proceso.exitValue();

        System.out.println("(" + clase + " termino con codigo " + codigoSalida + ")");

        // Si el hijo ha fallado, mostramos su error y no seguimos.
        if (codigoSalida != 0) {
            System.err.println("El proceso " + clase + " ha terminado con error.");

            for (String linea : errores) {
                System.err.println(linea);
            }

            System.exit(1);
        }

        /*
         * El hijo ha terminado bien, pero no pudimos enviarle todos los datos.
         * Eso significa que ha dado su respuesta leyendo solo una parte del
         * CSV, asi que su veredicto no vale. Es un fallo de verdad, distinto de
         * una cancelacion por tiempo.
         */
        if (errorDeEscritura[0] != null) {
            System.err.println("El proceso " + clase + " termino con codigo 0,"
                    + " pero no se le pudieron enviar todos los datos: "
                    + errorDeEscritura[0]);
            System.err.println("Su respuesta no es fiable porque solo ha leido"
                    + " parte del pedido.");

            System.exit(1);
        }

        String primeraLinea = null;

        if (unaSolaLinea) {
            if (!salida.isEmpty()) {
                primeraLinea = salida.get(0);
            }
        } else {
            // Mostramos todo lo que haya escrito, linea a linea.
            for (String linea : salida) {
                System.out.println(linea);
            }
        }

        return primeraLinea;
    }

    /**
     * Lee un flujo entero, linea a linea, y lo guarda en una lista.
     *
     * Lo usan los dos hilos lectores. Esta aparte para no escribir el mismo
     * bucle dos veces.
     */
    private static void leerTodo(BufferedReader lector, ArrayList<String> destino) {

        try (BufferedReader cerrarAlAcabar = lector) {

            String linea;

            while ((linea = cerrarAlAcabar.readLine()) != null) {
                destino.add(linea);
            }

        } catch (IOException e) {
            // La tuberia se ha cerrado porque el hijo ha terminado o lo hemos
            // cancelado. Nos quedamos con lo que hayamos leido.
        }
    }
}
