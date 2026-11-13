import java.util.ArrayList;

/**
 * Lee registros CSV completos, incluidos campos con comas y saltos de linea.
 * Dentro de un campo entrecomillado, dos comillas representan una comilla literal.
 * Lo comparten el validador y el analizador CSV; un formato invalido lanza
 * IllegalArgumentException para que el hijo avise por stderr.
 */
public class LectorCsv {

    /**
     * Recorre todo el contenido de un CSV y devuelve sus registros.
     *
     * Cada registro es una lista de campos, asi que lo que se devuelve es una
     * lista de listas: registros.get(0) es el primer registro y
     * registros.get(0).get(6) es su septimo campo.
     */
    public static ArrayList<ArrayList<String>> partirTodo(String contenido) {

        ArrayList<ArrayList<String>> registros = new ArrayList<>();

        // El registro que estamos montando ahora mismo.
        ArrayList<String> registro = new ArrayList<>();

        // El campo que estamos montando, letra a letra.
        StringBuilder campo = new StringBuilder();

        // true mientras estamos dentro de un campo entre comillas.
        boolean dentroDeComillas = false;

        // true justo despues de cerrar un campo entrecomillado. Sirve para
        // detectar basura pegada detras, como "hola"adios
        boolean comillaCerrada = false;

        for (int i = 0; i < contenido.length(); i++) {

            char letra = contenido.charAt(i);

            if (dentroDeComillas) {

                if (letra == '"') {

                    // ¿Es una comilla escapada ("") o la que cierra el campo?
                    if (i + 1 < contenido.length() && contenido.charAt(i + 1) == '"') {
                        campo.append('"');
                        i++;                    // nos saltamos la segunda
                    } else {
                        dentroDeComillas = false;
                        comillaCerrada = true;
                    }

                } else {
                    /*
                     * Dentro de comillas TODO es texto: comas, saltos de linea
                     * y retornos de carro incluidos. Se guardan tal cual para
                     * no cambiar el contenido original.
                     */
                    campo.append(letra);
                }

            } else {

                if (letra == ',') {
                    // Acaba el campo, empieza el siguiente.
                    registro.add(campo.toString());
                    campo.setLength(0);
                    comillaCerrada = false;

                } else if (letra == '\n') {
                    // Fuera de comillas, un salto de linea ACABA EL REGISTRO.
                    registro.add(campo.toString());
                    campo.setLength(0);
                    comillaCerrada = false;

                    registros.add(registro);
                    registro = new ArrayList<>();

                } else if (letra == '\r') {
                    /*
                     * Fuera de comillas, el retorno de carro de un final de
                     * linea de Windows (\r\n) no es texto: se ignora, y el \n
                     * que viene detras cierra el registro.
                     */
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

        // Si el contenido se acaba y seguimos dentro, falta la comilla final.
        if (dentroDeComillas) {
            throw new IllegalArgumentException(
                    "falta la comilla de cierre al final del archivo");
        }

        /*
         * El ultimo registro puede no llevar salto de linea detras. Si queda
         * algo a medias, lo cerramos.
         *
         * Si el archivo acaba en salto de linea, aqui no queda nada y no se
         * anade ningun registro vacio de propina.
         */
        if (campo.length() > 0 || !registro.isEmpty()) {
            registro.add(campo.toString());
            registros.add(registro);
        }

        return registros;
    }
}
