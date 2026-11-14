package nova;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import javax.swing.table.TableModel;

public class Archivos {

    private static final DateTimeFormatter FORMATO_FECHA =
            DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public static File archivo(String nombre) {
        File carpeta = new File(ConexionBD.getPropiedad("carpeta_salida", "salidas"));
        if (!carpeta.exists()) {
            carpeta.mkdirs();
        }
        return new File(carpeta, nombre);
    }

    public static void registrar(String accion, String resultado, String detalle) {
        String usuario = "-";
        String rol = "-";
        if (Sesion.haySesion()) {
            usuario = Sesion.getUsuario();
            rol = Sesion.getRol();
        }
        String linea = LocalDateTime.now().format(FORMATO_FECHA)
                + " | " + usuario
                + " | " + rol
                + " | " + accion
                + " | " + resultado
                + " | " + detalle.replace('\n', ' ').replace('\r', ' ');

        try (FileWriter escritor = new FileWriter(archivo("actividad_sneaker.txt"),
                StandardCharsets.UTF_8, true)) {
            escritor.write(linea + System.lineSeparator());
        } catch (IOException e) {
            System.err.println("No se pudo escribir en actividad_sneaker.txt: " + e.getMessage());
        }
    }

    public static File exportarCsv(TableModel modelo, String nombreArchivo) throws IOException {
        File destino = archivo(nombreArchivo);
        try (BufferedWriter escritor = Files.newBufferedWriter(destino.toPath(), StandardCharsets.UTF_8)) {
            for (int columna = 0; columna < modelo.getColumnCount(); columna++) {
                if (columna > 0) {
                    escritor.write(",");
                }
                escritor.write(campoCsv(modelo.getColumnName(columna)));
            }
            escritor.newLine();

            for (int fila = 0; fila < modelo.getRowCount(); fila++) {
                for (int columna = 0; columna < modelo.getColumnCount(); columna++) {
                    if (columna > 0) {
                        escritor.write(",");
                    }
                    escritor.write(campoCsv(modelo.getValueAt(fila, columna)));
                }
                escritor.newLine();
            }
        }
        return destino;
    }

    private static String campoCsv(Object valor) {
        if (valor == null) {
            return "";
        }
        String texto = valor.toString();
        if (texto.contains(",") || texto.contains("\"") || texto.contains("\n") || texto.contains("\r")) {
            return "\"" + texto.replace("\"", "\"\"") + "\"";
        }
        return texto;
    }

    public static File guardarUsuariosJson(TableModel usuarios) throws IOException {
        StringBuilder json = new StringBuilder("[\n");
        for (int fila = 0; fila < usuarios.getRowCount(); fila++) {
            json.append("  {");
            for (int columna = 0; columna < usuarios.getColumnCount(); columna++) {
                if (columna > 0) {
                    json.append(", ");
                }
                json.append(textoJson(usuarios.getColumnName(columna)));
                json.append(": ");
                json.append(valorJson(usuarios.getValueAt(fila, columna)));
            }
            json.append("}");
            if (fila < usuarios.getRowCount() - 1) {
                json.append(",");
            }
            json.append("\n");
        }
        json.append("]\n");

        Path temporal = archivo("usuarios_sneaker.json.tmp").toPath();
        Path definitivo = archivo("usuarios_sneaker.json").toPath();
        Files.writeString(temporal, json.toString(), StandardCharsets.UTF_8);
        Files.move(temporal, definitivo, StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);

        String leido = Files.readString(definitivo, StandardCharsets.UTF_8);
        if (!leido.equals(json.toString())) {
            throw new IOException("usuarios_sneaker.json no se ha guardado completo");
        }
        return definitivo.toFile();
    }

    private static String valorJson(Object valor) {
        if (valor == null) {
            return "null";
        }
        if (valor instanceof Number || valor instanceof Boolean) {
            return valor.toString();
        }
        return textoJson(valor.toString());
    }

    private static String textoJson(String texto) {
        StringBuilder resultado = new StringBuilder("\"");
        for (int i = 0; i < texto.length(); i++) {
            char letra = texto.charAt(i);
            if (letra == '"') {
                resultado.append("\\\"");
            } else if (letra == '\\') {
                resultado.append("\\\\");
            } else if (letra == '\n') {
                resultado.append("\\n");
            } else if (letra == '\r') {
                resultado.append("\\r");
            } else if (letra == '\t') {
                resultado.append("\\t");
            } else if (letra < 32) {
                resultado.append(String.format("\\u%04x", (int) letra));
            } else {
                resultado.append(letra);
            }
        }
        resultado.append("\"");
        return resultado.toString();
    }
}
