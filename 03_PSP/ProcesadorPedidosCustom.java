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

public class ProcesadorPedidosCustom {

    private static final String VALIDADOR = "ValidadorPedidoCustom";
    private static final String ANALIZADOR = "Psp.AnalizadorTallas";
    private static final String GENERADOR = "GeneradorFichaTaller";

    private static final int SEGUNDOS_MAXIMOS = 10;

    private static final Path CARPETA_SALIDAS = Path.of("salidas");
    private static final Path REGISTRO = CARPETA_SALIDAS.resolve("registro_psp.txt");

    public static final int CORRECTO = 0;
    public static final int ERROR_ARCHIVO = 1;
    public static final int DATOS_RECHAZADOS = 2;
    public static final int FALLO_PROCESO = 3;

    private static final int HIJO_RECHAZA_DATOS = 2;

    private static final ArrayList<String> resumen = new ArrayList<>();

    public static void main(String[] args) throws Exception {

        String ahora = LocalDateTime.now().format(
                DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
        anotar("===== NOVA Sneakers - PSP - " + ahora + " =====");

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
            csv = Files.readString(archivo, StandardCharsets.UTF_8);

        } catch (MalformedInputException e) {
            terminar(ERROR_ARCHIVO, "El archivo no esta en UTF-8");
            return;

        } catch (IOException e) {
            terminar(ERROR_ARCHIVO, "No se ha podido leer el archivo: " + e.getMessage());
            return;
        }

        GestorProcesos validador = new GestorProcesos(VALIDADOR, SEGUNDOS_MAXIMOS);
        validador.ejecutar(csv);
        comprobarPaso(1, validador, null);

        String[] partes = validador.getSalida().get(0).split(";");

        if (partes.length != 4) {
            terminar(FALLO_PROCESO, "El validador tenia que contestar OK;referencia;lineas;pares");
        }

        String referencia = partes[1];
        int pares = aNumero(partes[3]);

        if (pares <= 0) {
            terminar(FALLO_PROCESO, "El validador no ha dado un total de pares valido");
        }

        StringBuilder paraAnalizador = new StringBuilder();
        ArrayList<String> datosPedido = new ArrayList<>();

        for (String linea : validador.getSalida()) {

            if (linea.startsWith("PEDIDO;") || linea.startsWith("LINEA;") || linea.equals("FIN")) {
                paraAnalizador.append(linea).append("\n");

            } else if (linea.startsWith("CLIENTE;") || linea.startsWith("PERSONALIZACION;")) {
                datosPedido.add(linea);
            }
        }

        GestorProcesos analizador = new GestorProcesos(ANALIZADOR, SEGUNDOS_MAXIMOS);
        analizador.ejecutar(paraAnalizador.toString());
        comprobarPaso(2, analizador, referencia);

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

        System.out.println();
        for (String linea : ficha) {
            System.out.println(linea);
        }
        System.out.println();

        anotar("Ficha para el taller: " + archivoFicha);
        terminar(CORRECTO, "Pedido " + referencia + " procesado");
    }

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

        if (codigo == HIJO_RECHAZA_DATOS) {
            anotar("  " + primeraLinea(paso.getErrores()));
            terminar(DATOS_RECHAZADOS, "El paso " + numero + " ha rechazado los datos del pedido");
        }

        if (codigo != 0) {
            anotar("  " + primeraLinea(paso.getErrores()));

            String mensaje = "El paso " + numero + " ha fallado con codigo " + codigo;

            if (String.join(" ", paso.getErrores()).contains("ClassNotFoundException")) {
                mensaje = mensaje + ". No se encuentra la clase " + paso.getClase()
                        + ": hay que compilarla (ver README)";
            }
            terminar(FALLO_PROCESO, mensaje);
        }

        if (paso.getErrorDeEscritura() != null) {
            terminar(FALLO_PROCESO, "El paso " + numero + " ha contestado sin recibir"
                    + " todos los datos (" + paso.getErrorDeEscritura() + ")");
        }

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

    private static void anotar(String linea) {
        System.out.println(linea);
        resumen.add(linea);
    }

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

    private static String primeraLinea(ArrayList<String> lineas) {

        if (lineas.isEmpty()) {
            return "(sin mensaje)";
        }
        return lineas.get(0);
    }

    private static int aNumero(String texto) {

        try {
            return Integer.parseInt(texto.trim());
        } catch (NumberFormatException e) {
            return -1;
        }
    }

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
