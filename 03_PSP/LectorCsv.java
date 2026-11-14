import java.util.ArrayList;

public class LectorCsv {

    public static ArrayList<ArrayList<String>> partirTodo(String contenido) {

        ArrayList<ArrayList<String>> registros = new ArrayList<>();

        ArrayList<String> registro = new ArrayList<>();

        StringBuilder campo = new StringBuilder();

        boolean dentroDeComillas = false;

        boolean comillaCerrada = false;

        for (int i = 0; i < contenido.length(); i++) {

            char letra = contenido.charAt(i);

            if (dentroDeComillas) {

                if (letra == '"') {

                    if (i + 1 < contenido.length() && contenido.charAt(i + 1) == '"') {
                        campo.append('"');
                        i++;
                    } else {
                        dentroDeComillas = false;
                        comillaCerrada = true;
                    }

                } else {
                    
                    campo.append(letra);
                }

            } else {

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
                    
                    if (i + 1 < contenido.length() && contenido.charAt(i + 1) == '\n') {
                        continue;
                    }

                    throw new IllegalArgumentException(
                            "hay un retorno de carro suelto fuera de un campo entrecomillado");

                } else if (letra == '"') {

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

        if (dentroDeComillas) {
            throw new IllegalArgumentException(
                    "falta la comilla de cierre al final del archivo");
        }

        if (campo.length() > 0 || !registro.isEmpty()) {
            registro.add(campo.toString());
            registros.add(registro);
        }

        return registros;
    }
}
