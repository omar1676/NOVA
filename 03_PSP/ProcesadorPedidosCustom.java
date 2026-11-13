import java.io.IOException;
import java.nio.charset.MalformedInputException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.InvalidPathException;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;

/**
 * Procesa la copia CSV de un pedido: validador, analizador de Alvaro y generador.
 * El padre pasa los datos entre hijos por stdin/stdout y se detiene si un paso falla.
 * Genera una ficha auxiliar y anade el resumen a salidas/registro_psp.txt.
 * No modifica PostgreSQL, Odoo ni el stock; no crea una orden de fabricacion.
 * Codigos: 0 correcto, 1 error de archivo, 2 pedido rechazado, 3 fallo de proceso.
 */
public class ProcesadorPedidosCustom {

    // Los tres hijos. Cada nombre es una clase con su propio main.
    private static final String VALIDADOR = "ValidadorPedidoCustom";
    private static final String ANALIZADOR = "Psp.AnalizadorTallas";   // de Alvaro
    private static final String GENERADOR = "GeneradorFichaTaller";

    // Ningun hijo deberia tardar mas de esto con un pedido normal.
    private static final int SEGUNDOS_MAXIMOS = 10;

    private static final Path CARPETA_SALIDAS = Path.of("salidas");
    private static final Path REGISTRO = CARPETA_SALIDAS.resolve("registro_psp.txt");

    // Codigos de salida del padre.
    public static final int CORRECTO = 0;
    public static final int ERROR_ARCHIVO = 1;
    public static final int DATOS_RECHAZADOS = 2;
    public static final int FALLO_PROCESO = 3;

    // Codigo con el que los tres hijos dicen "los datos no son validos".
    private static final int HIJO_RECHAZA_DATOS = 2;

    // Las lineas del resumen. Se muestran segun se anaden y al final se
    // guardan en el registro.
    private static final ArrayList<String> resumen = new ArrayList<>();

    public static void main(String[] args) throws Exception {

        String ahora = LocalDateTime.now().format(
                DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        anotar("===== NOVA Sneakers - PSP - " + ahora + " =====");

        // =================================================================
        // Leer el archivo de entrada
        // =================================================================
        if (args.length != 1) {
            terminar(ERROR_ARCHIVO, "Uso: java ProcesadorPedidosCustom <archivo.csv>");
        }

        anotar("Archivo: " + args[0]);

        String problema = comprobarArchivo(args[0]);

        if (problema != null) {
            terminar(ERROR_ARCHIVO, problema);
        }

        Path archivo = Path.of(args[0]);
        String csv;

        try {
            // Entero y tal cual: un registro puede ocupar varias lineas.
            csv = Files.readString(archivo, StandardCharsets.UTF_8);

        } catch (MalformedInputException e) {
            terminar(ERROR_ARCHIVO, "El archivo no esta en UTF-8");
            return;   // no se llega: terminar() acaba el programa

        } catch (IOException e) {
            terminar(ERROR_ARCHIVO, "No se ha podido leer el archivo: " + e.getMessage());
            return;
        }

        // =================================================================
        // Paso 1: validar. Le enviamos el CSV entero por su stdin.
        // =================================================================
        GestorProcesos validador = new GestorProcesos(VALIDADOR, SEGUNDOS_MAXIMOS);
        validador.ejecutar(csv);
        comprobarPaso(1, validador, null);

        // Su primera linea es OK;referencia;lineas;pares
        String[] partes = validador.getSalida().get(0).split(";");

        if (partes.length != 4) {
            terminar(FALLO_PROCESO, "El validador tenia que contestar OK;referencia;lineas;pares");
        }

        String referencia = partes[1];
        int pares = aNumero(partes[3]);

        if (pares <= 0) {
            terminar(FALLO_PROCESO, "El validador no ha dado un total de pares valido");
        }

        /*
         * Separamos lo que nos ha devuelto el validador:
         *   - PEDIDO, LINEA y FIN son la entrada del analizador de Alvaro,
         *     que espera justo ese formato.
         *   - CLIENTE y PERSONALIZACION los guardamos para la ficha.
         */
        StringBuilder paraAnalizador = new StringBuilder();
        ArrayList<String> datosPedido = new ArrayList<>();

        for (String linea : validador.getSalida()) {

            if (linea.startsWith("PEDIDO;") || linea.startsWith("LINEA;") || linea.equals("FIN")) {
                paraAnalizador.append(linea).append("\n");

            } else if (linea.startsWith("CLIENTE;") || linea.startsWith("PERSONALIZACION;")) {
                datosPedido.add(linea);
            }
        }

        // =================================================================
        // Paso 2: agrupar por variante y talla.
        // =================================================================
        GestorProcesos analizador = new GestorProcesos(ANALIZADOR, SEGUNDOS_MAXIMOS);
        analizador.ejecutar(paraAnalizador.toString());
        comprobarPaso(2, analizador, referencia);

        // Contamos lo que ha devuelto y comprobamos que cuadra con el paso 1.
        int combinaciones = 0;
        int tallas = 0;
        int totalAnalizador = -1;

        for (String linea : analizador.getSalida()) {

            if (linea.startsWith("VARIANTE_TALLA;")) {
                combinaciones++;
            } else if (linea.startsWith("TALLA;")) {
                tallas++;
            } else if (linea.startsWith("TOTAL;")) {
                totalAnalizador = aNumero(linea.substring("TOTAL;".length()));
            }
        }

        if (totalAnalizador != pares) {
            terminar(FALLO_PROCESO, "Los procesos no coinciden: el validador cuenta "
                    + pares + " pares y el analizador " + totalAnalizador);
        }

        anotar("  " + combinaciones + " combinaciones de modelo, color y talla; "
                + tallas + " tallas; " + totalAnalizador + " pares");

        // =================================================================
        // Paso 3: la ficha. Le enviamos los datos del pedido y el
        // resumen del analizador (sin su primera linea, que es el OK).
        // =================================================================
        StringBuilder paraGenerador = new StringBuilder();
        paraGenerador.append("PEDIDO;").append(referencia).append("\n");
        paraGenerador.append("ORIGEN;").append(archivo.getFileName()).append("\n");

        for (String linea : datosPedido) {
            paraGenerador.append(linea).append("\n");
        }

        for (int i = 1; i < analizador.getSalida().size(); i++) {
            paraGenerador.append(analizador.getSalida().get(i)).append("\n");
        }

        paraGenerador.append("FIN\n");

        GestorProcesos generador = new GestorProcesos(GENERADOR, SEGUNDOS_MAXIMOS);
        generador.ejecutar(paraGenerador.toString());
        comprobarPaso(3, generador, referencia);

        // =================================================================
        // Guardar la ficha (todo menos la primera linea, que es el OK).
        // =================================================================
        ArrayList<String> ficha = new ArrayList<>();

        for (int i = 1; i < generador.getSalida().size(); i++) {
            ficha.add(generador.getSalida().get(i));
        }

        Path archivoFicha = CARPETA_SALIDAS.resolve(
                "ficha_taller_" + nombreParaArchivo(referencia) + ".txt");

        try {
            Files.createDirectories(CARPETA_SALIDAS);
            Files.write(archivoFicha, ficha, StandardCharsets.UTF_8);

        } catch (IOException e) {
            terminar(ERROR_ARCHIVO, "No se ha podido guardar la ficha: " + e.getMessage());
        }

        // La ficha se ensena en pantalla, pero no se copia en el registro.
        System.out.println();
        for (String linea : ficha) {
            System.out.println(linea);
        }
        System.out.println();

        anotar("Ficha para el taller: " + archivoFicha);
        terminar(CORRECTO, "Pedido " + referencia + " procesado");
    }

    /**
     * Comprueba el archivo antes de leerlo. Devuelve el problema, o null si
     * esta bien.
     */
    private static String comprobarArchivo(String ruta) {

        Path archivo;

        try {
            archivo = Path.of(ruta);
        } catch (InvalidPathException e) {
            return "La ruta no es valida: " + ruta;
        }

        if (!Files.exists(archivo)) {
            return "No existe el archivo: " + ruta;
        }

        if (!Files.isRegularFile(archivo)) {
            return "No es un archivo: " + ruta;
        }

        if (!ruta.toLowerCase().endsWith(".csv")) {
            return "Formato no admitido: el pedido tiene que venir en un archivo .csv";
        }

        try {
            if (Files.size(archivo) == 0) {
                return "El archivo esta vacio";
            }
        } catch (IOException e) {
            return "No se ha podido leer el archivo: " + e.getMessage();
        }

        return null;
    }

    /**
     * Mira como ha ido un paso. Si ha ido bien, vuelve y el padre sigue. Si
     * no, escribe por que y termina el programa: el paso siguiente NO se
     * lanza.
     *
     * @param referencia la del pedido, para comprobar que el hijo contesta
     *                   sobre el mismo pedido; null en el paso 1, que es
     *                   quien la descubre
     */
    private static void comprobarPaso(int numero, GestorProcesos paso, String referencia) {

        String nombre = "Paso " + numero + " " + paso.getClase() + ": ";
        int codigo = paso.getCodigoSalida();

        if (codigo == GestorProcesos.TIEMPO_AGOTADO) {
            anotar(nombre + "no ha terminado en " + paso.getSegundosMaximos()
                    + " s y se ha cancelado");
            terminar(FALLO_PROCESO, "El paso " + numero + " ha superado el tiempo de espera");
        }

        if (codigo == GestorProcesos.NO_ARRANCA) {
            anotar(nombre + primeraLinea(paso.getErrores()));
            terminar(FALLO_PROCESO, "No se ha podido lanzar el paso " + numero);
        }

        anotar(nombre + "codigo " + codigo + " en "
                + String.format("%.2f", paso.getSegundos()) + " s");

        // El hijo ha rechazado los datos: su motivo viene por stderr.
        if (codigo == HIJO_RECHAZA_DATOS) {
            anotar("  " + primeraLinea(paso.getErrores()));
            terminar(DATOS_RECHAZADOS, "El paso " + numero + " ha rechazado los datos del pedido");
        }

        // Cualquier otro codigo distinto de 0 es un fallo del hijo.
        if (codigo != 0) {
            anotar("  " + primeraLinea(paso.getErrores()));

            String mensaje = "El paso " + numero + " ha fallado con codigo " + codigo;

            if (String.join(" ", paso.getErrores()).contains("ClassNotFoundException")) {
                mensaje = mensaje + ". No se encuentra la clase " + paso.getClase()
                        + ": hay que compilarla (ver README)";
            }
            terminar(FALLO_PROCESO, mensaje);
        }

        // Ha terminado con 0, pero sin leer todo lo que le enviamos.
        if (paso.getErrorDeEscritura() != null) {
            terminar(FALLO_PROCESO, "El paso " + numero + " ha contestado sin recibir"
                    + " todos los datos (" + paso.getErrorDeEscritura() + ")");
        }

        /*
         * Antes de usar la respuesta, comprobamos que tiene la forma
         * acordada: empieza por OK; y habla del mismo pedido. (Como en el
         * ejemplo del profesor LanzadorEstadisticas.java.)
         */
        String respuesta = primeraLinea(paso.getSalida());
        String[] partes = respuesta.split(";");

        boolean valida = respuesta.startsWith("OK;") && partes.length >= 2;

        if (valida && referencia != null && !partes[1].equals(referencia)) {
            valida = false;
        }

        if (!valida) {
            anotar("  Respuesta recibida: " + respuesta);
            terminar(FALLO_PROCESO, "La respuesta del paso " + numero + " no es la esperada");
        }

        anotar("  " + respuesta);
    }

    /** Muestra una linea del resumen y la guarda para el registro. */
    private static void anotar(String linea) {
        System.out.println(linea);
        resumen.add(linea);
    }

    /** Escribe la ultima linea del resumen, guarda el registro y sale con el codigo. */
    private static void terminar(int codigo, String mensaje) {

        String estado;

        if (codigo == CORRECTO) {
            estado = "CORRECTO";
        } else if (codigo == ERROR_ARCHIVO) {
            estado = "ERROR EN EL ARCHIVO";
        } else if (codigo == DATOS_RECHAZADOS) {
            estado = "PEDIDO RECHAZADO";
        } else {
            estado = "FALLO DE UN PROCESO";
        }

        anotar("Resultado: " + estado + " (codigo " + codigo + "). " + mensaje);

        // Cada ejecucion anade su bloque al final (APPEND), separado por una linea en blanco.
        resumen.add("");

        try {
            Files.createDirectories(CARPETA_SALIDAS);
            Files.write(REGISTRO, resumen, StandardCharsets.UTF_8,
                    StandardOpenOption.CREATE, StandardOpenOption.APPEND);

        } catch (IOException e) {
            System.err.println("Aviso: no se ha podido guardar el registro: " + e.getMessage());
        }

        System.exit(codigo);
    }

    /** La primera linea de una lista, o un aviso si esta vacia. */
    private static String primeraLinea(ArrayList<String> lineas) {

        if (lineas.isEmpty()) {
            return "(sin mensaje)";
        }
        return lineas.get(0);
    }

    /** Convierte un texto en entero; -1 si no es un numero. */
    private static int aNumero(String texto) {

        try {
            return Integer.parseInt(texto.trim());
        } catch (NumberFormatException e) {
            return -1;
        }
    }

    /**
     * La referencia va en el nombre del archivo de la ficha. Cambiamos por
     * "_" todo lo que no sea letra, numero, guion o guion bajo, para que el
     * nombre sea valido en cualquier sistema.
     */
    private static String nombreParaArchivo(String referencia) {

        StringBuilder nombre = new StringBuilder();

        for (int i = 0; i < referencia.length(); i++) {
            char letra = referencia.charAt(i);

            if (Character.isLetterOrDigit(letra) || letra == '-' || letra == '_') {
                nombre.append(letra);
            } else {
                nombre.append('_');
            }
        }
        return nombre.toString();
    }
}
