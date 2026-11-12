import java.util.ArrayList;

/**
 * NOVA Sneakers - PSP - Leer un CSV y separarlo en registros y campos
 *
 * POR QUE EXISTE ESTA CLASE
 *   Leer bien un CSV no es tan simple como partir por comas. La usan
 *   ValidadorPedidoCustom (hijo 1) y el AnalizadorTallas antiguo de esta
 *   carpeta; asi el codigo esta en un solo sitio.
 *
 * LINEA FISICA NO ES LO MISMO QUE REGISTRO
 *   Esto es lo importante de esta clase. Un registro del CSV puede ocupar
 *   VARIAS lineas del archivo, porque un campo entrecomillado puede llevar un
 *   salto de linea dentro.
 *
 *   PostgreSQL los genera de verdad. Si una personalizacion se guarda asi:
 *
 *       Logo bordado, con el texto "NOVA"
 *       Segunda linea: numeracion en el talon
 *
 *   el CSV que exporta COPY ocupa DOS lineas del archivo para UN solo
 *   registro:
 *
 *       CUSTOM-40,NOVA-4-40,...,Rojo,"Logo bordado, con el texto ""NOVA""
 *       Segunda linea: numeracion en el talon",40,10
 *
 *   Por eso esta clase no lee linea a linea: recorre TODO el contenido letra
 *   a letra y decide ella misma donde acaba cada registro. Un salto de linea
 *   dentro de comillas es texto del campo; fuera de comillas, termina el
 *   registro.
 *
 * LAS REGLAS DEL CSV, QUE SON CUATRO
 *   1. Los campos se separan por comas.
 *   2. Un campo puede ir entre comillas dobles. Dentro, una coma es texto.
 *   3. Dentro de comillas, dos comillas seguidas ("") son una comilla de verdad.
 *   4. Dentro de comillas, un salto de linea es texto y se conserva tal cual.
 *
 * SI EL CSV ESTA MAL
 *   Lanza IllegalArgumentException con el motivo. El hijo que la llama la
 *   recoge con un try/catch y avisa por su salida de error.
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
