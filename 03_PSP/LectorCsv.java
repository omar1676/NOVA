import java.util.ArrayList;

// Clase de apoyo: parte un CSV en registros y campos, respetando las comillas.
// La usan ValidadorPedidoCustom (hijo 1) y el AnalizadorTallas de esta carpeta
public class LectorCsv {

    // Devuelve la lista de registros; cada registro es la lista de sus campos.
    // Si el CSV esta mal formado, lanza IllegalArgumentException con el motivo
    public static ArrayList<ArrayList<String>> partirTodo(String contenido) {

        ArrayList<ArrayList<String>> registros = new ArrayList<>();

        ArrayList<String> registro = new ArrayList<>();

        StringBuilder campo = new StringBuilder();

        // true mientras se lee un campo entre comillas
        boolean dentroDeComillas = false;

        // true justo despues de cerrar la comilla: solo puede venir una coma o un salto de linea
        boolean comillaCerrada = false;

        // Se recorre el texto letra a letra
        for (int i = 0; i < contenido.length(); i++) {

            char letra = contenido.charAt(i);

            if (dentroDeComillas) {

                // Dentro de comillas, dos comillas seguidas son una comilla escrita
                // y una sola cierra el campo
                if (letra == '"') {

                    if (i + 1 < contenido.length() && contenido.charAt(i + 1) == '"') {
                        campo.append('"');
                        i++;
                    } else {
                        dentroDeComillas = false;
                        comillaCerrada = true;
                    }

                } else {
                    // Lo demas, incluidas las comas y los saltos de linea, es parte del campo
                    campo.append(letra);
                }

            } else {

                // Fuera de comillas: la coma separa campos y el salto de linea separa registros
                if (letra == ',') {
                    registro.add(campo.toString());
                    campo.setLength(0);
                    comillaCerrada = false;

                } else if (letra == '\n') {
                    registro.add(campo.toString());
                    campo.setLength(0);
                    comillaCerrada = false;

                    registros.add(registro);
                    registro = new ArrayList<>();

                } else if (letra == '\r') {
                    // Windows acaba las lineas en \r\n: se salta el \r y el \n cierra el registro
                    if (i + 1 < contenido.length() && contenido.charAt(i + 1) == '\n') {
                        continue;
                    }

                    throw new IllegalArgumentException(
                            "hay un retorno de carro suelto fuera de un campo entrecomillado");

                } else if (letra == '"') {

                    // Una comilla solo puede abrir un campo que todavia esta vacio
                    if (comillaCerrada) {
                        throw new IllegalArgumentException(
                                "hay una comilla de mas despues de cerrar un campo");
                    }

                    if (campo.length() > 0) {
                        throw new IllegalArgumentException(
                                "hay una comilla en medio de un campo sin entrecomillar");
                    }

                    dentroDeComillas = true;

                } else {

                    if (comillaCerrada) {
                        throw new IllegalArgumentException(
                                "hay texto pegado detras de la comilla de cierre");
                    }

                    campo.append(letra);
                }
            }
        }

        // Si se acaba el texto con una comilla abierta, el CSV esta mal formado
        if (dentroDeComillas) {
            throw new IllegalArgumentException(
                    "falta la comilla de cierre al final del archivo");
        }

        // Ultimo registro, por si el archivo no termina en salto de linea
        if (campo.length() > 0 || !registro.isEmpty()) {
            registro.add(campo.toString());
            registros.add(registro);
        }

        return registros;
    }
}
